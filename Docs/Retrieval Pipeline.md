# Retrieval Pipeline

Back to [[Index]] · Related: [[Architecture]], [[Decisions]]

## Why retrieval
Sending the whole 380-page PDF with every question took **45–199 s** per answer and often hit
"high demand" errors (see [[Troubleshooting]]). The PDF has a full text layer (610k characters,
only 5 near-empty pages), so the app now sends only the most relevant pages.

## Indexing (one-time)
1. `pypdf` extracts text for each page (truncated to 8000 chars; empty pages become `(blank page)`).
2. Pages are embedded with `gemini-embedding-001`, `task_type=RETRIEVAL_DOCUMENT`, 768 dimensions, batches of 20.
3. Vectors are L2-normalized and saved to `index/embeddings-<hash>.npy`.
   - `<hash>` = first 16 hex chars of SHA-256(PDF bytes + `gemini-embedding-001:768`).
   - Replacing the PDF or changing the model/dimension creates a new file automatically.
4. On the free tier the build took **388 s** because of tokens-per-minute limits (the code sleeps 30 s on each 429, up to 10 times per batch).

The index is **committed to the repo**, so Streamlit Cloud never needs to rebuild it.

## Per question
1. Query text = previous user question (if any) + current question — so short follow-ups still find the right pages.
2. **Semantic ranking:** the query is embedded (`RETRIEVAL_QUERY`) and compared to all page vectors (cosine).
3. **Keyword ranking:** BM25 over page tokens (lowercase `[a-z0-9]+`, small stop-word list, trailing `s` stripped for words > 4 chars).
4. **Fusion:** reciprocal-rank fusion, `score = Σ 1 / (60 + rank)`; only pages with a positive BM25 score join the keyword ranking.
5. Top **12** pages, sorted by page number, are sent as `[Page N]` excerpts with the question.

## Why hybrid
Embeddings alone missed the daytank-flush procedure (p. 143) for *"How do I flush the daytanks?"*.
Adding BM25 brought p. 143 into the results and the answer became correct (see [[Test Results]]).
Hebrew questions rely on the multilingual embeddings, since keywords won't match the English text.

## Tuning knobs (`gemini_client.py`)
| Constant | Value | Effect |
| --- | --- | --- |
| `TOP_K` | 12 | Pages sent per question (more = better recall, slower/costlier) |
| `MAX_PAGE_CHARS` | 8000 | Max text per page |
| `EMBED_DIM` | 768 | Embedding size (changing it requires a new index) |
| `EMBED_BATCH` | 20 | Pages per embedding request |
