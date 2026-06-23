# LPE V1.12 Step 4 — Safe Staging Allowlist V1

## Allowed for next guarded staging gate

```text
README.md
requirements.txt
docs/V1_12_STEP1_PROJECT_COMPLETION_SCOPE_AUDIT/
docs/V1_12_STEP2_PROJECT_COMPLETION_AUDIT_REPORT/
docs/V1_12_STEP3_README_REQUIREMENTS_USER_GUIDE/
docs/V1_12_STEP4_REPO_CLEANUP_PLAN/
```

## Explicitly not allowed by default

```text
reports/
backups/
prototypes/
scripts/run_lpe_*.sh
scripts/run_vmax_*.sh
life_priority_engine_snapshot_*.json
data/lpe_local_snapshot.json
```

## Conditional review only

```text
docs/00_LIFE_PRIORITY_ENGINE_MASTER_PROJECT_MAP_V1.md
docs/01_LIFE_PRIORITY_ENGINE_CODEX_WORKFLOW_AND_GATE_ROADMAP_V1.md
docs/02_LIFE_PRIORITY_ENGINE_RULES_V1.md
docs/ACCEPTANCE_RECORDS/
docs/CODEX_SUPPORT/
docs/DEPLOYMENT_PREP/
docs/GITHUB_*/
docs/STREAMLIT_*/
docs/PUBLIC_DEMO_HARDENING/
docs/V1_11_STEP1_LIFE_SETTINGS/
scripts/LPE_*
```
