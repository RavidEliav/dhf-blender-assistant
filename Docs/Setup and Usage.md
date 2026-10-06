# Setup and Usage

Back to [[Index]] · Related: [[Deployment]]

## Requirements
- Windows with Python 3.10+ on PATH (tested with Python 3.14)
- A Gemini API key from https://aistudio.google.com/apikey

## Run locally
1. Double-click `run.bat` in `C:\Scripts\PDF`. It:
   - creates `.venv` if missing,
   - installs `requirements.txt`,
   - creates `.env` from `.env.example` if missing,
   - starts Streamlit on **http://localhost:8501** (bound to localhost only, so others on the network can't use your key).
2. Put the key in `.env` (`GEMINI_API_KEY=...`) or type it in the sidebar.
3. Ask questions in English or Hebrew.

## `.env` settings
| Variable | Purpose |
| --- | --- |
| `GEMINI_API_KEY` | Gemini API key (never commit; `.env` is gitignored) |
| `GEMINI_MODEL` | Main chat model |
| `GEMINI_FALLBACK_MODEL` | Comma-separated models tried when the main one is busy |

After editing `.env`, **restart** `run.bat` — values are read once at startup.

## Using the app
- **Chat box** — ask any question; follow-ups use the conversation history.
- **🗑️ New chat** — clears the conversation.
- **Sidebar** — manual name, page count, main and fallback models.
- Answers cite pages as `(p. N)` = PDF page numbers (open the PDF and jump to that page).
- Hebrew answers render right-to-left automatically.

## Example questions
- How do I flush the daytanks?
- What is UPW used for?
- איך מבצעים שטיפה לתא הדגימה?

## Rebuilding the index
Only needed if the PDF is replaced or `EMBED_MODEL` / `EMBED_DIM` change:
1. Delete the old `index/embeddings-*.npy`.
2. Start the app (or call `build_index`) — the new file is created automatically (≈ 6–7 min on the free tier).
3. Commit the new `index/` file so the cloud app doesn't rebuild it.
