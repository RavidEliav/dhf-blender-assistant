# DHF Blender Manual Assistant — Project Docs (Obsidian Vault)

This folder is an [Obsidian](https://obsidian.md) vault that documents the DHF Blender Manual Assistant project.
Open this `Docs/` folder as a vault in Obsidian.

## What the project is
A Streamlit chat app that answers free-language questions (English or Hebrew) about the
**DHF Inline Blender, with Integrated Daytanks** manual (doc 928880, Revision A, October 2015, 380 pages).
Answers are grounded only in the manual and cite PDF page numbers.

- Repo (private): https://github.com/RavidEliav/dhf-blender-assistant
- Local: `C:\Scripts\PDF` → double-click `run.bat` → http://localhost:8501
- Hosting: Streamlit Community Cloud (private app, invited viewers only)

## Notes
- [[Architecture]] — components, data flow and file layout.
- [[Retrieval Pipeline]] — how the relevant manual pages are found for each question.
- [[Models and Fallback]] — Gemini models used, failover order, timeouts and retries.
- [[Setup and Usage]] — running locally, `.env` settings, rebuilding the index.
- [[Deployment]] — GitHub repo and Streamlit Community Cloud setup.
- [[Troubleshooting]] — every error hit so far and how it was fixed.
- [[Test Results]] — verified questions, answers and timings.
- [[Decisions]] — design decisions and why they were made.
- [[Commit Log]] — one entry per git commit.

## Quick facts
| Item | Value |
| --- | --- |
| UI | Streamlit chat (`app.py`) |
| LLM | Google Gemini (`gemini-3.8-flash` + fallbacks) |
| Retrieval | Gemini embeddings + BM25 keyword search, rank-fused, top 12 pages |
| Index | `index/embeddings-<hash>.npy` (prebuilt, committed) |
| Languages | Replies in the language of the question (EN / HE, RTL supported) |
| Secrets | `GEMINI_API_KEY` in `.env` (local) or Streamlit Secrets (cloud) — never committed |
