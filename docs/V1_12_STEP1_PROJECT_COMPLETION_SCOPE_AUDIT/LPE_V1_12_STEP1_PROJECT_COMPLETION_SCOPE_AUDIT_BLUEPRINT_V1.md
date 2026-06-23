# LPE V1.12 Step 1 — Project Completion Scope Audit Blueprint V1

## Purpose

This gate changes the direction of V1.12.

The owner clarified that the current goal is not to optimize one daily plan yet.

The current goal is:

> Finish the Life Priority Engine project to a stable usable level first.
> After the system is complete enough, the owner will shift attention away from building this system and use it to support study.

## Correct Scope

The next work must audit project completeness.

It must not treat one day's reflection as the project roadmap.

## Completion Definition

The project is "complete enough for current phase" only when:

1. Public app is usable.
2. The 5-step flow works:
   - ตั้งค่าชีวิต
   - เช็คอินวันนี้
   - แผนวันนี้
   - ทบทวนวันนี้
   - สำรองข้อมูล
3. JSON import/export works.
4. A user can restore their profile from JSON on public Streamlit.
5. The repo contains only intentional committed files.
6. README explains how to run and use the app.
7. requirements.txt is correct for Streamlit Cloud.
8. No local private data is committed.
9. No dead runner/report/backups are pushed.
10. Remaining backlog is explicit.

## Out of Scope for This Gate

- No adaptive tomorrow feature yet.
- No new AI logic.
- No login.
- No database.
- No notification.
- No mobile app.
- No trading system.
- No medical advice expansion.
- No deployment mutation.
- No commit/push from this design gate.

## Completion Audit Categories

### A. Product Acceptance

Checks:
- Public app opens.
- 5-page flow visible.
- Legacy pages hidden.
- Import JSON works.
- Profile shows 5/5 after import.

Status source:
- Owner manual acceptance screenshots and current snapshot.

### B. Data Safety

Checks:
- `data/lpe_local_snapshot.json` ignored.
- JSON snapshots ignored.
- backups/reports ignored.
- no secrets committed.

### C. Repo Hygiene

Checks:
- `.gitignore` present.
- `app.py` committed.
- required docs committed.
- untracked files reviewed.
- old runners not pushed unless intentionally selected.

### D. User Docs

Checks:
- README has:
  - What this app does.
  - How to run locally.
  - How to use public app.
  - How to export/import JSON.
  - What is not included.
  - Data safety note.

### E. Release Evidence

Checks:
- latest commit hash recorded.
- push status recorded.
- public acceptance recorded.
- known limitations recorded.

## Recommended Next Gates

### V1.12 Step 2 — Completion Audit Report Patch

Create a static completion report from current repo state and known acceptance evidence.

Allowed:
- docs/V1_12_STEP1_PROJECT_COMPLETION_SCOPE_AUDIT/*
- README.md if authorized later

No app mutation.

### V1.12 Step 3 — README and User Guide Patch

Improve README and add concise public user guide.

### V1.12 Step 4 — Repo Cleanup Plan

Decide what to keep, ignore, archive, or delete locally.

### V1.12 Step 5 — Release Tag Preparation

Prepare v1.11-public-accepted or v1.12-completion-baseline tag only after docs are clean.

## Owner Rule

Until project completion gates are done, do not force the owner to switch to study planning.

The app exists to help the owner, but the current project-management truth is:
- Building the system is the present focus.
- Studying becomes the next focus after the system is stable enough.
