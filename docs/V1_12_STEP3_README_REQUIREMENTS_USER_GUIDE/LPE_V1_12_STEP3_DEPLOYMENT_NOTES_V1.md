# LPE V1.12 Step 3 — Deployment Notes V1

## Public URL

```text
https://life-priority-engine.streamlit.app
```

## GitHub baseline

- Branch: `main`
- Commit: `27e61aa3424de6e76996679e08e543189323fb62`
- Subject: `LPE V1.11 local workflow with autosave and JSON persistence`

## Streamlit Cloud Requirements

`requirements.txt` must include Streamlit.

No secrets are required for this app.

Do not add `.streamlit/secrets.toml` unless a future authorized gate requires it.

## Current storage model

Manual JSON export/import.

No login.
No database.
No cloud sync.
