# Life Priority Engine

Life Priority Engine is a local, single-app Streamlit tool intended to help clarify what matters today, review what actually happened, and adjust tomorrow. **V1.2: Thai Dashboard Layout and Visual System is complete.**

This is a **local-only V1 working MVP**. It is **not production software** and **not medical advice**. Day modes and health cautions are conservative planning signals only; they do not diagnose conditions or recommend treatment.

## Current scaffold

The Thai-first app currently contains:

- A dark-navy left sidebar that switches between five views without a `pages/` directory
- A default “วันนี้ต้องทำอะไร” view with four compact summary cards
- Prominent Today Mission cards with Thai Must / Should / Could presentation
- Fast Thai review controls: ทำครบ / ทำบางส่วน / ไม่ได้ทำ / มีปัญหา
- A clear “วันนี้ยังไม่ควรทำ” safety card
- Separate views for Tomorrow Plan, detailed daily guidance, the 30-day map, and read-only life settings
- A light, scrollable 30 × 6 planner that no longer appears on the daily landing view
- Thai date and capacity-mode controls in the sidebar while internal logic values remain unchanged

After review and scoring, Gate 6 generates and saves a constrained 1–5 mission plan for tomorrow on the same page.

## Local data seeds

The `data/` folder contains editable mock data only:

- Profile and planning preferences: `user_profile.json`, `health_goal.json`
- Schedules and plans: `shift_schedule.csv`, `exam_plan.csv`, `garden_plan.csv`
- Optional projects and inactive rule seeds: `project_list.json`, `decision_rules.json`
- Append-only generated-plan file: `daily_plan.csv`
- Append-only review log: `daily_log.csv`

The engine reads seed files without modifying them. Gate 6 appends reviews to `daily_log.csv` and tomorrow plans to `daily_plan.csv`; if either file is missing or empty, the app recreates its header before appending.

## Today Mission rules

The first engine uses only these rules:

- Red Day blocks heavy exercise and optional project work.
- An exam within 30 days raises study priority.
- An exam within 7 days removes the optional project mission.
- A heavy shift reduces optional project time.
- Missions are ordered Must, then Should, then Could and capped at five.

## Daily Review

Each generated mission can be reviewed as:

- `DONE`: no additional input.
- `PARTIAL`: actual amount or minutes plus unit.
- `MISSED`: a selected reason.
- `PROBLEM`: a selected issue and optional short note.

Saving appends one row per mission to `data/daily_log.csv`, preserves existing rows, writes each mission score, and displays the daily result.

## Scoring and day mode

The score is the equal-weight average of mission credits:

- `DONE`: 100% credit.
- `PARTIAL`: actual amount divided by the numeric target, capped at 100%; a nonnumeric target receives 50% when an actual amount is supplied.
- `MISSED`: 0–25% depending on the selected reason.
- `PROBLEM`: 40% credit and the issue is surfaced as a blocker, not treated as laziness.

Green Day requires a score of at least 80 with no moderate or serious capacity signal. Partial work, missed work, ordinary problems, a high workload, or a Yellow starting mode produce Yellow Day. A Red starting mode or a serious reported health/safety issue produces Red Day regardless of score.

The result card shows the daily score, classified mode, main blocker, interpretation, and a cautious non-diagnostic health message when relevant.

## Tomorrow Replanner

Saving a review generates tomorrow’s plan from today’s score, classified mode, blocker, mission statuses, exam window, workload, and safety signals. The plan contains 1–5 mission cards, reasons, a Do Not Do Tomorrow section, and a recovery note when relevant.

Simple constraints include:

- Red Day or a health/safety issue forces Recovery / Yellow Day and blocks heavy exercise.
- Missed study inside 30 days of an exam raises tomorrow’s study priority.
- The 7-day exam window removes optional project work.
- Project displacement limits tomorrow’s project work.
- A heavy shift reduces optional high-effort tasks.
- Missed exercise resumes lightly and is never compensated with heavier exercise.

Each save appends a new tomorrow-plan snapshot to `data/daily_plan.csv`; prior plan rows remain intact.

## Rough 30-Day Plan

The dedicated “ภาพรวม 30 วัน” sidebar view shows 30 compact daily hints starting from the selected mission date. Each row contains the date, expected mode hint, main focus, study load, project/garden allowance, and rest/recovery note.

The map uses local shift, exam, project, and garden seeds. Exam proximity raises study focus, the final seven days reduce optional projects, heavy shifts limit project/garden work, and a saved Red Day or health signal gives the following day a Recovery bias with no heavy exercise.

This overview is deliberately rough: it is a map, not a fixed command. Today Mission and Daily Review remain authoritative when real capacity differs from the map.

## Gate 8 UX polish

The one-page layout now gives Today Mission more visual weight, keeps review choices compact, and separates completion score from safety-aware day mode. Tomorrow missions use a denser card treatment, while the 30-day map remains a compact scrollable table. These are presentation changes only; mission, scoring, review persistence, replanning, and 30-day planning rules are unchanged.

## V1.1 Thai Public UX Readiness

The public-facing interface is now Thai-first and removes visible technical Gate labels. The visual system uses a light cream background, rounded white cards, deep readable text, a purple-gradient primary button, gray inactive review choices, and green active choices. Today Mission remains the widest and most prominent panel.

Mission content, categories, priority badges, review labels, score interpretation, safety cautions, Tomorrow Plan, empty/help text, and the 30-day overview are localized at the presentation layer. Internal status values, decision rules, stored values, and all CSV/JSON schemas remain unchanged.

The former dense dark 30-day grid is presented as a light 30 × 6 HTML table inside a collapsed, scrollable section. It remains a flexible map rather than a command.

## V1.1 Thai daily-use refinement

The daily flow now uses one clear vertical sequence instead of a split dashboard: Today Mission → review choice directly under each mission → Save → today’s result → Tomorrow Plan → collapsed 30-day map.

Review choices use toggle-style presentation with gray inactive states and semantic active states: green for ทำครบ, yellow for ทำบางส่วน, red for ไม่ได้ทำ, and purple for มีปัญหา. Mission explanations are shorter and limited to two lines.

The saved result uses native Streamlit elements—a progress bar, score, day mode, main blocker, and short interpretation. This removes the fragile HTML summary that could expose raw text such as `<div class="summary-badges">`.

Tomorrow Plan remains 1–5 concise cards. The 30-day plan stays collapsed by default and no longer controls the visual weight of the page.

## V1.2 Thai dashboard layout and visual system

V1.2 keeps one `app.py` Streamlit application and adds dashboard-style navigation inside `st.sidebar`. It does not create a `pages/` directory. The five presentation views are:

- 🏠 วันนี้ต้องทำอะไร — default daily landing view with mission count, latest score, day mode, caution, missions, reviews, and save action
- 🌤 แผนพรุ่งนี้ — concise 1–5 mission plan available after the selected day is saved
- 🕒 แผนละเอียดรายวัน — presentation-only time suggestions, current work/study missions, general food categories, user-defined calorie target display, and general activity level
- 📅 ภาพรวม 30 วัน — the existing 30 × 6 map in its own view
- ⚙️ ตั้งค่าชีวิต — read-only summary of existing local profile and health-planning seeds

The visual palette is deliberately narrow: navy navigation and section headers, cream background, white cards, purple primary action, green success/active, yellow caution, and red only for warnings. Rounded cards and soft shadows follow the owner-provided Thai interface references without adding their unrelated admin or analytics features.

Nutrition and exercise content is general planning only. The app displays a calorie target only if the user has already defined one in local data; it does not calculate, prescribe, diagnose, or recommend treatment. Mission generation, review persistence, scoring, serious-safety override, Tomorrow Plan, 30-day logic, and every CSV/JSON schema are unchanged.

## Run locally

### Cursor terminal / WSL

When Cursor is opened at `/mnt/d/LIFE_PRIORITY_ENGINE`, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
streamlit run app.py
```

### Windows PowerShell

From the project root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print the local URL in the terminal, typically `http://localhost:8501`.

## Utility scripts

The launch scripts prefer the project-local `.venv` when it exists and otherwise use Python from `PATH`. They do not install dependencies, change application data, or call external services.

From the project root on Windows PowerShell:

```powershell
.\scripts\check_project_state.ps1
.\scripts\run_app.ps1
```

If local script execution is blocked by PowerShell policy, use a process-local bypass without changing the system policy:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check_project_state.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_app.ps1
```

From the project root on WSL/Linux:

```bash
bash scripts/run_app.sh
```

Run the setup commands above first if Streamlit is not installed yet. The project-state checker is read-only and exits with a nonzero status if a required file is missing.

## Current boundaries

The app and its seed data are local and remain one Streamlit application. It does not include login, multi-user support, cloud services, external APIs, API keys, broker or trading features, V.MAX trading flow, medical diagnosis or treatment advice, an AI coach, PDF export, advanced analytics, or detailed 30-day optimization.

## V1 evidence checklist

Final Gate 9 checks completed on 2026-06-20:

- `app.py` parses successfully and Streamlit starts with a healthy local endpoint.
- The app renders one page with Today Mission, Daily Review, Tomorrow Plan, and the Rough 30-Day Plan; no `pages/` directory exists.
- All nine required data files exist. All four JSON files parse as objects, and all five CSV files match their expected headers.
- Mission generation returns 1–5 ordered missions and applies Red Day, exam-window, heavy-shift, and Must-before-Could constraints.
- DONE, PARTIAL, MISSED, and PROBLEM review controls render their expected conditional fields and can be saved in an isolated test copy.
- Scoring produced the expected sample credits: DONE 100%, PARTIAL 25%, MISSED 25%, and PROBLEM 40%. A mixed sample scored 48/100 Yellow.
- A serious health/safety signal forced Red Day at 85/100, confirming that a high score cannot override safety.
- Tomorrow Replanner checks passed for recovery after Red/health signals, missed-study priority, near-exam project reduction, project displacement, heavy shifts, and no exercise compensation.
- The rough planner renders exactly 30 rows × 6 columns, including Red-to-Recovery bias.
- Isolated save tests appended review and plan rows, then both generated CSVs were restored to header-only. The project copies of `daily_log.csv` and `daily_plan.csv` remain header-only.
- Static scope audit found no application networking, login, broker/trading, AI coach, medical diagnosis/treatment, PDF, multi-user, multipage, chart, or dashboard-expansion code.

## V1 limitations

- Local, single-user, mock-seed workflow only; there is no authentication, cloud sync, backup service, or production hardening.
- Rules are simple and deterministic. The app does not perform forecasting, optimization, advanced analytics, or medical assessment.
- CSV saves are append-only snapshots. Repeated saves create additional rows; there is no deduplication or concurrent-user protection.
- Plans depend on the accuracy and dates of user-edited local seed files.
- The automated Streamlit render and live health checks passed; in-app browser screenshot attachment was unavailable in the Windows test sandbox.

## Gate status

```text
DATE: 2026-06-21
GATE: V1.2 — Thai Dashboard Layout and Visual System
STATUS: PASS
WHAT_WORKS: One app.py uses a five-view Thai sidebar with Today as the default; daily review remains adjacent to missions; score and safety state remain clear; Tomorrow, detailed daily planning, 30-day, and settings views are separated; the complete 30x6 plan is outside the daily landing view.
WHAT_DOES_NOT_WORK: Production operation, multi-user concurrency, deduplication, forecasting, optimization, advanced analytics, and all forbidden scope remain intentionally unimplemented.
FILES_CHANGED: app.py, README.md, docs/CURRENT_BOOT_PACKET.md, docs/UI_UX_BRIEF_V1.md
TEST_DONE: Syntax; Streamlit component render and live health; browser DOM verification; all five sidebar views; default Today view; review status conditions; isolated 85-point serious-signal Red override save; Tomorrow Plan; 30x6 plan; no raw HTML/Gate wording; unchanged real data hashes and schemas; forbidden-scope audit.
KNOWN_LIMITATIONS: Local-only, single-user, append-only V1.2; not production and not medical advice. The settings view is read-only and calorie display depends on an explicitly user-defined local value.
NEXT_SINGLE_STEP: Owner review and acceptance of V1.2. Deployment remains unauthorized.
```
