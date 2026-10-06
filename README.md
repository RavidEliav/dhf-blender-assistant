# DHF Blender Manual Assistant

Streamlit chat app that answers English or Hebrew questions about the DHF Inline Blender manual
(doc 928880 Rev A) using Google Gemini. Answers are based only on the manual and cite page numbers.

## Run locally (Windows)
1. Double-click `run.bat` (creates `.venv`, installs requirements, creates `.env`).
2. Set `GEMINI_API_KEY` in `.env` (or enter it in the sidebar) and restart.
3. Open http://localhost:8501.

## Deploy
Streamlit Community Cloud → main file `app.py`, with `GEMINI_API_KEY`, `GEMINI_MODEL` and
`GEMINI_FALLBACK_MODEL` in Secrets.

## Docs
Full documentation is an Obsidian vault in [`Docs/`](Docs/Index.md).
