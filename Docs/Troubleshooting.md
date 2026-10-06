# Troubleshooting

Back to [[Index]] · Related: [[Models and Fallback]], [[Deployment]]

| Symptom | Cause | Fix |
| --- | --- | --- |
| `models/gemini-2.5-flash is no longer available to new users` | Model retired for new keys | Use `gemini-3.8-flash` (set `GEMINI_MODEL`) |
| `503 UNAVAILABLE ... high demand` | Gemini free-tier capacity spikes | Automatic failover through the fallback list; retry later; enable billing |
| `429 RESOURCE_EXHAUSTED` while chatting | Quota exceeded for a model | Failover to the next model; remove that model from fallbacks |
| `429 RESOURCE_EXHAUSTED` while indexing | Embedding tokens-per-minute limit | `_embed` waits 30 s and retries (up to 10×); index is prebuilt and committed |
| App spins forever, no answer | Full-PDF requests hung without a timeout | Added 120 s client timeout (30 s for non-last models) and switched to retrieval |
| Answers take 45–200 s | Whole 380-page PDF sent per question | Hybrid page retrieval — see [[Retrieval Pipeline]] |
| Correct page not found (e.g. daytank flush) | Embedding-only retrieval | Added BM25 keyword fusion and raised `TOP_K` to 12 |
| `API key not valid. Please pass a valid API key.` (cloud) | Wrong/placeholder key in Streamlit Secrets | Fix `GEMINI_API_KEY` in Secrets; the app now shows the masked key (first/last 4 chars + length) to compare |
| `.env` change ignored | Env vars are read once per process | Restart `run.bat` |
| `git push` rejected (fetch first) | Streamlit Cloud added `.devcontainer/` | `git pull --rebase` then `git push` |
| Hebrew shows as garbage in the terminal | Console encoding only | Not an app issue — the browser renders it correctly |
| `git push` shows a red `NativeCommandError` in PowerShell | git writes progress to stderr | Harmless if the output ends with `main -> main` |

## Diagnostics
Check which models the key can use:
```powershell
.\.venv\Scripts\python.exe -c "import os; from dotenv import load_dotenv; load_dotenv(); from google import genai; c=genai.Client(api_key=os.environ['GEMINI_API_KEY']); print([m.name for m in c.models.list() if 'flash' in m.name])"
```
