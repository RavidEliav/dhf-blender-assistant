# Commit Log

Back to [[Index]]

## 2026-10-06 14:46:34 - 2574b93
- **DHF Blender manual Q&A assistant (Streamlit + Gemini)** (by Ravid Eliav)
- Files changed:
  - .env.example
  - .gitignore
  - DHF Blender Manual.pdf
  - app.py
  - gemini_client.py
  - requirements.txt
  - run.bat

## 2026-10-06 14:57:09 - c1721dc
- **Fast page retrieval (hybrid semantic + keyword), prebuilt index, model fallback** (by Ravid Eliav)
- Files changed:
  - .env.example
  - app.py
  - gemini_client.py
  - index/embeddings-6444831935c21873.npy

## 2026-10-06 15:00:34 - 677d002
- **Longer model fallback chain, faster failover** (by Ravid Eliav)
- Files changed:
  - .env.example
  - app.py
  - gemini_client.py

## 2026-10-06 15:06:31 - 8c60697
- **Added Dev Container Folder** (by RavidEliav, via Streamlit Community Cloud)
- Files changed:
  - .devcontainer/devcontainer.json

## 2026-10-06 15:06:45 - b2bfcb5
- **Sanitize API key and show clear invalid-key message** (by Ravid Eliav)
- Files changed:
  - app.py

## 2026-10-06 15:14:27 - bde4943
- **Add Obsidian docs vault, README, and gitignore for Obsidian state** (by Ravid Eliav)
- Files changed:
  - .gitignore
  - Docs/ (vault: Index, Architecture, Retrieval Pipeline, Models and Fallback, Setup and Usage, Deployment, Troubleshooting, Test Results, Decisions, Commit Log, .obsidian settings)
  - README.md
  - app.py
