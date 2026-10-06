# Deployment

Back to [[Index]] · Related: [[Setup and Usage]], [[Troubleshooting]]

## GitHub
- Repo: **RavidEliav/dhf-blender-assistant** (private) — https://github.com/RavidEliav/dhf-blender-assistant
- Branch: `main`
- Private because the manual is vendor documentation and a public app would expose the API quota.
- Never committed: `.env`, `.venv/`, `.cache/`, `.streamlit/secrets.toml`, Obsidian workspace state.

## Streamlit Community Cloud
1. https://share.streamlit.io → sign in with GitHub as **RavidEliav** (grant private-repo access).
2. **Create app** → repo `RavidEliav/dhf-blender-assistant`, branch `main`, main file `app.py`.
3. **Advanced settings** → Python 3.12, and **Secrets**:
   ```toml
   GEMINI_API_KEY = "<your full key>"
   GEMINI_MODEL = "gemini-3.8-flash"
   GEMINI_FALLBACK_MODEL = "gemini-3.7-flash,gemini-3.6-flash,gemini-3.5-flash,gemini-3.1-flash-lite"
   ```
   - Root-level secrets are exposed as environment variables, so `os.getenv` in `app.py` reads them.
   - Keep the double quotes; no `[section]` header above the keys.
4. **Deploy**. Apps from a private repo are private — share with specific emails via **Share**.

## Updating
- Every `git push` to `main` redeploys automatically.
- Changing Secrets: app **⋮ → Settings → Secrets → Save** (the app restarts).
- Streamlit Cloud commits `.devcontainer/devcontainer.json` to the repo on first deploy — run `git pull --rebase` before pushing if a push is rejected.
