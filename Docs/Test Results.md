# Test Results

Back to [[Index]] · Related: [[Retrieval Pipeline]], [[Models and Fallback]]

All tests on 2026-10-06, Gemini free tier.

## Full-PDF approach (before retrieval)
Question: *"What is UPW? One sentence."* — whole PDF attached.

| Model | Result | Time |
| --- | --- | --- |
| gemini-3.8-flash | OK | 199 s |
| gemini-3.7-flash | OK | 75 s |
| gemini-flash-latest | 429 quota exhausted | 135 s |
| gemini-3.6-flash | OK | 45 s |

## Hybrid retrieval
| Question | Pages retrieved | Result | Time |
| --- | --- | --- | --- |
| How do I flush the daytanks? | 48, 51, 59, 61, 115, 132, 141, 143, 144, 188, 193, 206 | Correct procedure from p. 143 (connect ½" UPW line, flush and fill, recirculate) + safety warning | 34 s |
| איך מבצעים שטיפה לתא הדגימה? | 48, 50, 125–127, 130–132, 188, 192, 193, 240 | Correct Hebrew answer: manual spray-gun rinse (p. 130), RINSE service (pp. 131–132), optional auto-rinse via AOV.L1.210 (p. 50) + safety warning | 131 s* |

\* Long time caused by several models returning 503 in a row before one answered.

## Behaviour checks
- [x] Off-topic question ("clean the blender jar") → says the manual doesn't cover it and points to related pages
- [x] Hebrew question → Hebrew answer, RTL in the browser
- [x] Page citations present in every answer
- [x] Safety warnings reproduced
- [x] Missing API key → clear error + sidebar key box
- [x] Invalid API key → masked key shown with fix instructions
