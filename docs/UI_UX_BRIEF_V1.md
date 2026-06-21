# UI/UX BRIEF V1 — Life Priority Engine

## Design direction

- Thai-first user-facing interface
- dark navy sidebar and section headers
- light cream page background
- rounded white cards with soft shadows
- deep navy readable typography
- purple gradient for the primary action
- green success and active-selection states
- gray inactive-selection states
- yellow caution and red only for warnings
- compact badges, subtle icons, and generous spacing

Visual inspiration comes from the owner-provided Thai UI references. The app uses only their approachable card, form, spacing, and color language; it does not copy admin, analytics, PDF, or management features.

## UX priorities

1. “วันนี้ต้องทำอะไร” is the default landing view and visual center.
2. Daily Review stays adjacent to each mission and is fast and obvious.
3. Mission count, latest score, day mode, and caution appear as four concise summary cards.
4. Tomorrow Plan is concise, safety-aware, and separated into its own view.
5. Detailed daily guidance remains general planning, with no calorie calculation or health prescription.
6. The 30-day plan remains complete but is separated from the daily landing view.
7. Normal user-facing text is Thai-first.

## Presentation rules

- Internal values such as `DONE`, `PARTIAL`, `MISSED`, `PROBLEM`, `Green Day`, and `Red Day` remain unchanged for logic and storage.
- Thai labels are applied only at the presentation layer.
- Technical Gate labels are never shown in the normal app UI.
- Sidebar navigation switches conditional sections inside one `app.py`; it does not use Streamlit multipage files.
- The five views are วันนี้ต้องทำอะไร, แผนพรุ่งนี้, แผนละเอียดรายวัน, ภาพรวม 30 วัน, and ตั้งค่าชีวิต.
- The 30-day planner is presented as a light, scrollable 30 × 6 table only in its own view.
- Settings is a read-only presentation of existing local seeds.
- Health language remains cautious and non-diagnostic.

## Keep unchanged

- one Streamlit app and no `pages/` directory
- mission generation logic
- Daily Review and append-only persistence
- scoring and serious health/safety override
- Tomorrow Replanner rules
- rough 30-day planner logic
- CSV and JSON schemas

## Hard bans

- no login or multi-user system
- no multi-page or admin mode
- no cloud, database server, API key, or external API
- no AI coach
- no medical diagnosis or treatment advice
- no trading, broker, or V.MAX flow
- no PDF export
- no charts or heavy analytics dashboard

## Verification status

`V1_2_THAI_DASHBOARD_LAYOUT = PASS`

- syntax and Streamlit render pass
- dark-navy sidebar contains five working Thai views
- default view is วันนี้ต้องทำอะไร
- Thai labels dominate the normal UI
- no visible Gate labels
- review controls retain their original internal values
- 100-point Green result and 85-point serious-signal Red override pass
- Tomorrow Replanner passes
- detailed daily view shows time, current work/study, general food, user-defined calorie display, and general movement level
- light 30-day presentation contains 30 rows × 6 columns in its own view
- schemas and forbidden-scope audit pass

Browser DOM verification confirmed sidebar navigation, the default landing view, no raw HTML or Gate wording, computed navy/cream/white styling, green active review state, purple primary action, and the 30 × 6 planner. Screenshot capture timed out, while component rendering, live health, DOM checks, and computed-style checks passed.

## V1.9 Mobile First Public Demo

- Mobile users must not depend on opening the Streamlit sidebar.
- Main page includes top navigation for all views.
- New users get an onboarding form for demo data.
- Demo data is stored in session_state only.
- Public demo warning must be visible.
