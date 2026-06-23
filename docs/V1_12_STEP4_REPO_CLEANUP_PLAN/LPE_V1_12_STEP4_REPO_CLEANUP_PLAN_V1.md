# LPE V1.12 Step 4 — Repo Cleanup Plan V1

## Purpose

Create a safe cleanup plan before any delete, stage, commit, push, or deploy action.

This gate performs static classification only.

## Hard Result

- No files deleted.
- No files moved.
- No files staged.
- No commit.
- No push.
- No deploy.
- `app.py` must remain unchanged.

## Why This Matters

The project already has a public usable baseline.

The remaining risk is not app logic.
The remaining risk is accidentally committing local runners, reports, backups, prototypes, or private snapshots.

## Category Summary

| Category | Count | Safe Default Action |
|---|---:|---|
| COMMIT_CANDIDATE_CORE_RELEASE | 2 | stage later only after final gate review |
| LOCAL_RUNNER_ARCHIVE_DO_NOT_COMMIT_BY_DEFAULT | 60 | keep local runner archive; do not commit by default |
| REVIEW_CANONICAL_DOC_MAY_COMMIT | 3 | review content then decide |
| REVIEW_DOCS_NOT_CLASSIFIED | 9 | manual review |
| REVIEW_OLD_PHASE_DOCS_NOT_CORE_RELEASE | 5 | review/possibly archive; not core release |
| REVIEW_SCRIPT_DOC_ARTIFACT | 4 | review before any commit |
| REVIEW_UNKNOWN | 1 | manual review |

## Safe Cleanup Policy

### Commit candidates

Can be committed later only after a guarded staging gate:

- README.md
- requirements.txt
- docs/V1_12_STEP1_PROJECT_COMPLETION_SCOPE_AUDIT/
- docs/V1_12_STEP2_PROJECT_COMPLETION_AUDIT_REPORT/
- docs/V1_12_STEP3_README_REQUIREMENTS_USER_GUIDE/
- docs/V1_12_STEP4_REPO_CLEANUP_PLAN/

### Review before commit

Needs owner review:

- docs/00_LIFE_PRIORITY_ENGINE_MASTER_PROJECT_MAP_V1.md
- docs/01_LIFE_PRIORITY_ENGINE_CODEX_WORKFLOW_AND_GATE_ROADMAP_V1.md
- docs/02_LIFE_PRIORITY_ENGINE_RULES_V1.md
- old phase docs under docs/
- script-side document artifacts

### Do not commit by default

Keep local or archive locally:

- scripts/run_lpe_*.sh
- scripts/run_vmax_*.sh
- reports/
- backups/
- prototypes/
- life_priority_engine_snapshot_*.json
- data/lpe_local_snapshot.json

## Next Safe Action

The next gate should not delete anything.

Recommended next gate:

`LPE_V1_12_STEP5_GUARDED_STAGING_FOR_COMPLETION_DOCS_NO_PUSH`

That gate should stage only:
- README.md
- requirements.txt
- docs/V1_12_STEP1_PROJECT_COMPLETION_SCOPE_AUDIT/
- docs/V1_12_STEP2_PROJECT_COMPLETION_AUDIT_REPORT/
- docs/V1_12_STEP3_README_REQUIREMENTS_USER_GUIDE/
- docs/V1_12_STEP4_REPO_CLEANUP_PLAN/
