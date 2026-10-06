# Models and Fallback

Back to [[Index]] · Related: [[Troubleshooting]]

## Configuration
Set in `.env` locally or in Streamlit Secrets on the cloud:

```ini
GEMINI_MODEL=gemini-3.8-flash
GEMINI_FALLBACK_MODEL=gemini-3.7-flash,gemini-3.6-flash,gemini-3.5-flash,gemini-3.1-flash-lite
```

The same values are the defaults in `app.py` if the variables are missing.

## Failover rules (`ask()`)
- Models are tried in order: main model, then each fallback.
- A model is skipped when it returns **429** (quota), **503** (high demand) or times out — but only if no text was streamed yet.
- All models except the last use **1 attempt and a 30 s timeout**, so a busy model fails over quickly.
- The last model uses the client defaults: **3 attempts, 120 s timeout**.
- Any other error (e.g. invalid API key) is raised immediately and shown in the UI.

## Model history
| Date | Change | Reason |
| --- | --- | --- |
| 2026-10-06 | Started with `gemini-2.5-flash` | Plan default |
| 2026-10-06 | Switched to `gemini-3.8-flash` | API: "no longer available to new users" |
| 2026-10-06 | Added fallbacks 3.7 → flash-latest | 503 high demand on 3.8 |
| 2026-10-06 | Replaced `gemini-flash-latest` with `gemini-3.6-flash` | 429 quota exhausted on flash-latest |
| 2026-10-06 | Added `gemini-3.5-flash`, `gemini-3.1-flash-lite` | All three models returned 503 at once |

## Embeddings
`gemini-embedding-001` (768-dim) — see [[Retrieval Pipeline]].

## Free tier note
Most errors (503, 429) come from the Gemini free tier. Enabling billing on the key in Google AI Studio
should make answers consistently fast.
