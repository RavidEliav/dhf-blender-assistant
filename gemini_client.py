import hashlib
import math
import re
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

import httpx
import numpy as np
from google import genai
from google.genai import errors, types
from pypdf import PdfReader

BASE_DIR = Path(__file__).parent
MANUAL_PATH = BASE_DIR / "DHF Blender Manual.pdf"
# Committed to the repo so deployments don't re-embed the manual on every cold start.
INDEX_DIR = BASE_DIR / "index"
EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 768
EMBED_BATCH = 20
MAX_PAGE_CHARS = 8000
TOP_K = 12

_WORD = re.compile(r"[a-z0-9]+")
_STOP = set(
    "a an and are as at be by can do does for from how i in is it its my of on or the this to what when where which who why with you your".split()
)

SYSTEM_PROMPT = """You are a helpful support assistant for the DHF Inline Blender, an industrial chemical blending system. \
Each question comes with excerpts from the official DHF Blender manual, each marked [Page N]. These excerpts are your ONLY source of truth.

Rules:
- Answer strictly based on the provided excerpts. Do not use outside knowledge or guess.
- If the excerpts do not contain the answer, say clearly that the manual does not seem to cover it, and mention the closest related page if one exists.
- Cite the page(s) you used at the end of each relevant statement, like "(p. 12)", using the N from the [Page N] markers.
- Always reply in the same language as the user's question (e.g. Hebrew question -> Hebrew answer, English question -> English answer).
- Be concise and practical. Use numbered steps for procedures and bullet lists where helpful.
- Reproduce any safety warnings or cautions related to the question faithfully.
- Use the conversation history to understand follow-up questions."""


def get_client(api_key: str) -> genai.Client:
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=120_000,  # ms
            retry_options=types.HttpRetryOptions(attempts=3),
        ),
    )


def _tokens(text: str) -> list[str]:
    # Crude plural stemming so "daytanks" matches "daytank".
    return [w[:-1] if len(w) > 4 and w.endswith("s") else w for w in _WORD.findall(text.lower()) if w not in _STOP]


@dataclass
class ManualIndex:
    pages: list[str]
    vectors: np.ndarray  # one L2-normalized row per page
    term_counts: list[Counter] = field(init=False)
    doc_lens: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        self.term_counts = [Counter(_tokens(p)) for p in self.pages]
        self.doc_lens = np.array([sum(c.values()) for c in self.term_counts], dtype=np.float32)

    def bm25(self, query: str, k1: float = 1.5, b: float = 0.75) -> np.ndarray:
        n = len(self.pages)
        norm = k1 * (1 - b + b * self.doc_lens / max(self.doc_lens.mean(), 1.0))
        scores = np.zeros(n, dtype=np.float32)
        for term in set(_tokens(query)):
            tf = np.array([c.get(term, 0) for c in self.term_counts], dtype=np.float32)
            df = int((tf > 0).sum())
            if df:
                idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
                scores += idf * tf * (k1 + 1) / (tf + norm)
        return scores


def _embed(client: genai.Client, texts: list[str], task_type: str) -> np.ndarray:
    vectors = []
    for i in range(0, len(texts), EMBED_BATCH):
        for attempt in range(10):
            try:
                result = client.models.embed_content(
                    model=EMBED_MODEL,
                    contents=texts[i : i + EMBED_BATCH],
                    config=types.EmbedContentConfig(task_type=task_type, output_dimensionality=EMBED_DIM),
                )
                break
            except errors.ClientError as e:
                # Free tier has a low tokens-per-minute limit; wait for the window to reset.
                if e.code != 429 or attempt == 9:
                    raise
                time.sleep(30)
        vectors.extend(e.values for e in result.embeddings)
    arr = np.array(vectors, dtype=np.float32)
    return arr / np.clip(np.linalg.norm(arr, axis=1, keepdims=True), 1e-12, None)


def build_index(client: genai.Client) -> ManualIndex:
    """Extract page text and embed it, reusing embeddings cached on disk for the same PDF."""
    pages = [(p.extract_text() or "").strip()[:MAX_PAGE_CHARS] for p in PdfReader(MANUAL_PATH).pages]

    key = hashlib.sha256(MANUAL_PATH.read_bytes() + f"{EMBED_MODEL}:{EMBED_DIM}".encode()).hexdigest()[:16]
    cache_file = INDEX_DIR / f"embeddings-{key}.npy"
    if cache_file.exists():
        return ManualIndex(pages, np.load(cache_file))

    vectors = _embed(client, [p or "(blank page)" for p in pages], "RETRIEVAL_DOCUMENT")
    INDEX_DIR.mkdir(exist_ok=True)
    np.save(cache_file, vectors)
    return ManualIndex(pages, vectors)


def retrieve(client: genai.Client, index: ManualIndex, query: str) -> list[int]:
    """Return 0-based indices of the most relevant pages (semantic + keyword, rank-fused), in page order."""
    n = len(index.pages)
    fused = np.zeros(n, dtype=np.float32)

    q = _embed(client, [query], "RETRIEVAL_QUERY")[0]
    fused[np.argsort(-(index.vectors @ q))] += 1 / (60 + np.arange(n))

    kw = index.bm25(query)
    kw_ranked = [i for i in np.argsort(-kw) if kw[i] > 0]
    fused[kw_ranked] += 1 / (60 + np.arange(len(kw_ranked)))

    return sorted(int(i) for i in np.argsort(-fused)[:TOP_K])


def ask(
    client: genai.Client,
    models: list[str],
    index: ManualIndex,
    history: list[dict],
    question: str,
) -> Iterator[str]:
    """Stream an answer, falling back to the next model if one is busy. `history` holds prior turns as {"role": "user"|"assistant", "content": str}."""
    # Include the previous question so short follow-ups ("and how do I reset it?") retrieve the right pages.
    prev_questions = [m["content"] for m in history if m["role"] == "user"][-1:]
    page_ids = retrieve(client, index, "\n".join([*prev_questions, question]))
    excerpts = "\n\n".join(f"[Page {i + 1}]\n{index.pages[i]}" for i in page_ids)

    contents: list[types.Content] = []
    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))
    prompt = f"Manual excerpts:\n\n{excerpts}\n\nQuestion: {question}"
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt)]))

    for i, model in enumerate(models):
        is_last = i == len(models) - 1
        yielded = False
        try:
            stream = client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                    # Skip retries on all but the last model so a busy model fails over quickly.
                    http_options=None if is_last else types.HttpOptions(
                        timeout=30_000, retry_options=types.HttpRetryOptions(attempts=1)
                    ),
                ),
            )
            for chunk in stream:
                if chunk.text:
                    yielded = True
                    yield chunk.text
            return
        except errors.APIError as e:
            if yielded or e.code not in (429, 503) or is_last:
                raise
        except httpx.TimeoutException:
            if yielded or is_last:
                raise
