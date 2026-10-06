# Decisions

Back to [[Index]]

| # | Decision | Alternatives | Why |
| --- | --- | --- | --- |
| 1 | **Google Gemini** as LLM | OpenAI, Azure OpenAI, Ollama, Claude | User choice |
| 2 | **Streamlit** chat UI | Gradio, desktop app | User choice; simplest browser chat UI |
| 3 | Reply in the **question's language** (EN/HE) | English only | User choice; RTL handled via CSS `unicode-bidi: plaintext` |
| 4 | Page citations, chat history, one-click `run.bat` | — | User-selected extras |
| 5 | First version: send the **whole PDF** via Gemini Files API | Local OCR (Tesseract) | Manual was assumed scanned; Gemini reads images natively |
| 6 | Switched to **page retrieval** | Keep full PDF; context caching | Full PDF took 45–199 s and often hit 503; PDF turned out to have a full text layer |
| 7 | **Hybrid** semantic + BM25 with rank fusion | Embeddings only | Embeddings alone missed the daytank-flush procedure |
| 8 | **Commit the embedding index** | Build on each cold start | Avoids ~6.5 min rebuild and free-tier quota on Streamlit Cloud |
| 9 | **Model fallback chain** with fast failover | Single model | Free-tier 503/429 errors are frequent |
| 10 | **Private** repo + private Streamlit app | Public | Vendor manual; protects the API quota |
| 11 | Bind local server to **localhost** | Default (all interfaces) | Prevents others on the network using the key |
| 12 | Obsidian vault in `Docs/` inside the repo | Separate vault | Same convention as other projects (e.g. ValveCountsTag) |

## Known limitations
- Diagrams/images are not used — only the PDF text layer (figure captions are included).
- Page numbers are PDF page numbers, not the printed `chapter-page` numbers (e.g. p. 143 = printed 5-5).
- Free-tier latency and availability vary; billing would remove most delays.
