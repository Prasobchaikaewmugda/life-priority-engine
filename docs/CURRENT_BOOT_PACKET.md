# CURRENT_BOOT_PACKET.md

ARTIFACT_ID = LIFE-CURRENT-BOOT-PACKET-V1  
PROJECT_NAME = Life Priority Engine  
CANONICAL_FILENAME = CURRENT_BOOT_PACKET.md  
ARTIFACT_CLASS = CURRENT_BOOT_PACKET_FOR_CODEX  
STATUS = V1_2_THAI_DASHBOARD_LAYOUT_COMPLETE  
VERSION = 1.0  
LANGUAGE = THAI_FIRST  
CURRENT_GATE = V1_2_THAI_DASHBOARD_LAYOUT_COMPLETE  
NEXT_SINGLE_ACTION = OWNER_REVIEW_AND_ACCEPT_V1_2_THAI_DASHBOARD_LAYOUT  
RUNTIME_AUTHORITY = NO  
NETWORK_AUTHORITY = NO  
API_KEY_AUTHORITY = NO  
TRADING_AUTHORITY = NO  
MEDICAL_AUTHORITY = NO  
PRODUCTION_AUTHORITY = NO  

---

# 0. หน้าที่ของไฟล์นี้

ไฟล์นี้คือ **ข้อมูลเปิดแชทใหม่ให้ Codex** สำหรับโปรเจกต์เว็บกิจวัตรประจำวัน  
ใช้เพื่อให้ Codex รู้ว่า:

- โปรเจกต์นี้คืออะไร
- ต้องอ่านไฟล์ไหนก่อน
- ตอนนี้อยู่ Gate ไหน
- งานล่าสุดคืออะไร
- งานถัดไปที่อนุญาตคืออะไร
- อะไรห้ามทำ
- ต้องส่งผลกลับมาแบบไหน

ไฟล์นี้ไม่ใช่กฎแม่บท  
ไฟล์นี้ไม่ใช่ไฟล์แผนที่  
ไฟล์นี้ไม่ใช่คำสั่งให้ทำทุก Gate พร้อมกัน  
ไฟล์นี้ใช้สำหรับ **เริ่มงานรอบถัดไปเท่านั้น**

---

# 1. Project Identity

ชื่อโปรเจกต์:

`Life Priority Engine`

คำจำกัดความสั้นที่สุด:

> เว็บหน้าเดียวที่ช่วยตอบว่า วันนี้ควรทำอะไรก่อน อะไรควรรอ อะไรห้ามทำ และพรุ่งนี้ควรปรับอย่างไรจากผลจริงของวันนี้

เป้าหมายหลัก:

> ช่วยคนที่จัดลำดับชีวิตไม่ถูก ให้ทำสิ่งสำคัญก่อนสิ่งน่าสนใจ และไม่ฝืนร่างกายเพื่อเอาชนะตาราง

---

# 2. Required Boot Order

เมื่อเปิดแชทใหม่กับ Codex ต้องส่งไฟล์ให้ Codex อ่านตามลำดับนี้:

1. `00_LIFE_PRIORITY_ENGINE_MASTER_PROJECT_MAP_V1.md`
2. `02_LIFE_PRIORITY_ENGINE_RULES_V1.md`
3. `01_LIFE_PRIORITY_ENGINE_CODEX_WORKFLOW_AND_GATE_ROADMAP_V1.md`
4. `CURRENT_BOOT_PACKET.md`

Codex ต้องสรุปก่อนลงมือว่าเข้าใจ:

- Project Identity
- North Star
- Current Gate
- Current Next Single Action
- Allowed Files
- Hard Bans
- Acceptance Criteria
- Return Contract

ถ้า Codex สรุปไม่ได้ ให้ตอบ:

`HOLD_MISSING_REQUIRED_BOOT_CONTEXT`

---

# 3. Stable Project Knowledge

## 3.1 00 Master Project Map

หน้าที่:

- อธิบายว่าเว็บคืออะไร
- ปัญหาที่เว็บแก้คืออะไร
- North Star คืออะไร
- V1 ต้องมีอะไร
- เว็บนี้ไม่ใช่อะไร

ไฟล์:

`00_LIFE_PRIORITY_ENGINE_MASTER_PROJECT_MAP_V1.md`

## 3.2 Rules / 02-like Law

หน้าที่:

- กฎของเว็บกิจวัตรประจำวัน
- Green / Yellow / Red Day
- DONE / PARTIAL / MISSED / PROBLEM
- กฎคะแนน
- กฎปรับพรุ่งนี้
- Hard Ban ของ V1

ไฟล์:

`02_LIFE_PRIORITY_ENGINE_RULES_V1.md`

## 3.3 Codex Workflow Roadmap

หน้าที่:

- บอกให้ Codex ทำงานทีละ Gate
- กำหนด Acceptance Criteria
- กำหนด Return Contract
- ป้องกัน Scope Drift

ไฟล์:

`01_LIFE_PRIORITY_ENGINE_CODEX_WORKFLOW_AND_GATE_ROADMAP_V1.md`

---

# 4. Current Project Position

สถานะล่าสุดของโปรเจกต์:

```text
PROJECT_MAP_00_CREATED = YES
RULES_FILE_CREATED = YES
CODEX_WORKFLOW_ROADMAP_CREATED = YES
HTML_PROTOTYPE_CREATED = YES
STREAMLIT_PROJECT_CREATED = YES
APP_PY_CREATED = YES
DATA_FILES_CREATED = YES
TODAY_MISSION_ENGINE_CREATED = YES
ONE_PAGE_UI_MVP_CREATED = YES
DAILY_REVIEW_SYSTEM_CREATED = YES
DAILY_LOG_APPEND_ENABLED = YES
SCORING_CREATED = YES
DAY_MODE_CLASSIFICATION_CREATED = YES
TOMORROW_REPLANNER_CREATED = YES
DAILY_PLAN_APPEND_ENABLED = YES
ROUGH_30_DAY_PLANNER_CREATED = YES
UX_POLISH_CREATED = YES
EVIDENCE_AND_TEST_PASS_CREATED = YES
V1_WORKING_MVP_VERIFIED = YES
THAI_PUBLIC_UX_READINESS_CREATED = YES
USER_FACING_THAI_FIRST = YES
TECHNICAL_GATE_LABELS_HIDDEN = YES
DAILY_USE_UX_REFINEMENT_CREATED = YES
RAW_HTML_UI_BUG_FIXED = YES
REVIEW_CONTROLS_INTEGRATED = YES
THAI_DASHBOARD_LAYOUT_CREATED = YES
SIDEBAR_NAVIGATION_CREATED = YES
DETAILED_DAILY_PRESENTATION_CREATED = YES
THIRTY_DAY_VIEW_SEPARATED = YES
README_CREATED = YES
REQUIREMENTS_CREATED = YES
```

Current Gate:

`V1_2_THAI_DASHBOARD_LAYOUT_COMPLETE`

Current Stage:

`V1_2_THAI_DASHBOARD_LAYOUT_COMPLETE`

Current Blocker:

`NONE`

Current Next Single Action:

`รอเจ้าของตรวจรับ V1.2 Thai Dashboard Layout and Visual System`

---

# 5. V1.2 Thai Dashboard Layout Status

งาน presentation ที่ Codex ได้รับอนุญาต:

```text
REFINE_THAI_DASHBOARD_LAYOUT_AND_VISUAL_SYSTEM_ONLY
IMPLEMENTATION_STATUS = COMPLETE
```

ปรับเฉพาะ presentation layer ให้เป็นหนึ่ง Streamlit app ที่สลับ 5 มุมมองด้วย sidebar โดยไม่เปลี่ยน mission, review, scoring, safety, tomorrow, 30-day logic หรือ data schema และไม่สร้าง `pages/`

Refinement Files:

```text
app.py
README.md
docs/CURRENT_BOOT_PACKET.md
docs/UI_UX_BRIEF_V1.md
```

Current Behavior:

- default view คือ `🏠 วันนี้ต้องทำอะไร`
- sidebar สี navy สลับ 5 มุมมองภายใน `app.py` เดียว
- หน้า Today แสดง summary 4 ใบ: ภารกิจ คะแนนล่าสุด โหมด และสิ่งที่ต้องระวัง
- Review อยู่ใต้ mission แต่ละใบโดยตรง
- inactive เป็นเทา; active ใช้เขียว / เหลือง / แดง / ม่วงตามสถานะ
- ปุ่มบันทึกเด่นและหาได้ง่าย
- สรุปหลังบันทึกใช้ native progress, คะแนน, โหมด, ปัญหาหลัก และข้อความสั้น
- แก้ raw HTML bug; ไม่พบ `<div class=...>` หรือ class name ใน visible text
- Tomorrow Plan เป็นมุมมองแยกและคงการ์ดสั้น 1–5 รายการ
- แผนละเอียดรายวันแสดงเวลา งาน/อ่าน อาหารทั่วไป calorie ที่ผู้ใช้กำหนดเอง และระดับการเคลื่อนไหวแบบทั่วไป
- 30-day planner ครบ 30 × 6 และอยู่ในมุมมองแยก
- ตั้งค่าชีวิตเป็น read-only summary จาก seed เดิม
- palette จำกัดเป็น navy / cream / white / purple / green / yellow / warning red
- UI เป็น Thai-first และไม่แสดง Gate / engine / replanner wording
- schema และ logic เดิมไม่เปลี่ยน; ไม่มี forbidden feature เพิ่ม

---

# 6. Not Authorized

Codex ยังไม่อนุญาตให้ทำ:

```text
LOGIN = NO
MULTI_USER = NO
CLOUD_DATABASE = NO
API_KEY = NO
EXTERNAL_API = NO
BROKER_API = NO
TRADING_LOGIC = NO
V_MAX_TRADING_FLOW = NO
MEDICAL_DIAGNOSIS = NO
NUTRITION_PRESCRIPTION = NO
AI_COACH_FULL_SYSTEM = NO
PDF_EXPORT = NO
NOTIFICATION = NO
MOBILE_APP = NO
COMPLEX_DASHBOARD = NO
MULTI_PAGE_ADMIN_SYSTEM = NO
```

ถ้า Codex เสนอสิ่งเหล่านี้ ให้ถือว่า:

`HOLD_SCOPE_DRIFT`

---

# 7. Work Unit Protocol for Codex

Codex ต้องทำงานแบบนี้ทุกครั้ง:

```text
READ
→ SUMMARIZE CURRENT GATE
→ CONFIRM ALLOWED FILES
→ IMPLEMENT ONE STEP
→ TEST LOCALLY IF POSSIBLE
→ REPORT RESULT
→ SUGGEST ONE NEXT STEP ONLY
```

ห้ามทำ:

```text
READ
→ BUILD EVERYTHING
→ ADD EXTRA FEATURES
→ CLAIM COMPLETE WITHOUT TEST
```

---

# 8. Current V1.2 Presentation Task

## Gate

`V1.2 — Thai Dashboard Layout and Visual System`

## Goal

ทำให้แอปสั้นลงในแต่ละมุมมอง น่าใช้ทุกวัน และมี visual system แบบ Thai dashboard โดยยังเป็น Streamlit app เดียว

## Exact Task

Presentation focus:

```text
one app.py; no pages/ directory
five-view sidebar navigation
Today is the default landing view
dashboard summary cards
review controls directly under each mission
semantic toggle-style active states
separate Tomorrow / detailed daily / 30-day / settings views
30 × 6 plan outside the daily landing view
controlled navy / cream / white / purple / green / yellow / warning-red palette
no technical wording
```

## UX Boundary

- presentation helpers เท่านั้น
- ไม่แก้ mission, review, scoring, safety, tomorrow หรือ 30-day logic
- ไม่เพิ่ม data schema หรือ feature
- one Streamlit app เท่านั้น
- ไม่มี `pages/` directory

---

# 9. V1.2 Acceptance Criteria

Refinement ถือว่าผ่านเมื่อ:

```text
ONE_STREAMLIT_APP = YES
APP_SYNTAX_VALID = YES
STREAMLIT_STARTS = YES
NO_PAGES_DIRECTORY = YES
SIDEBAR_NAVIGATION = PASS
DEFAULT_VIEW_TODAY = YES
FIVE_THAI_VIEWS = PASS
THAI_UI_DOMINANT = YES
TECHNICAL_GATE_LABELS_VISIBLE = NO
VISIBLE_ENGINE_OR_REPLANNER_WORDING = NO
RAW_HTML_VISIBLE = NO
TODAY_MISSION_MOST_PROMINENT = YES
SUMMARY_CARDS = PASS
REVIEW_CONTROLS_ADJACENT_TO_MISSIONS = YES
TOGGLE_ACTIVE_COLORS = PASS
REVIEW_THAI_CONTROLS = PASS
NATIVE_PROGRESS_SUMMARY = PASS
SCORING_AND_DAY_MODE = PASS
HIGH_SCORE_SERIOUS_SIGNAL_FORCES_RED = PASS
TOMORROW_REPLANNER = PASS
DETAILED_DAILY_PRESENTATION = PASS
GENERAL_NUTRITION_AND_EXERCISE_ONLY = YES
LIGHT_ROUGH_PLAN_30_BY_6 = PASS
ROUGH_PLAN_IN_OWN_VIEW = YES
CSV_JSON_SCHEMAS_CHANGED = NO
APP_LOGIC_CHANGED = NO
NEW_FEATURES_ADDED = NO
NO_MULTIPLE_PAGES = YES
NO_LOGIN = YES
NO_CLOUD = YES
NO_API_KEY = YES
NO_EXTERNAL_API_OR_NETWORK = YES
NO_BROKER_OR_TRADING = YES
NO_AI_COACH = YES
NO_TRADING_LOGIC = YES
NO_MEDICAL_DIAGNOSIS = YES
NO_PDF = YES
NO_MULTI_USER = YES
NOT_PRODUCTION = YES
NOT_MEDICAL_ADVICE = YES
LOCAL_ONLY_V1 = YES
```

ผล: PASS ตามรายการข้างต้น โดย Streamlit component render, live health, browser DOM navigation, computed visual palette, visible-text scan และ isolated save ผ่าน

---

# 10. Expected Return Format from Codex

Codex ต้องตอบกลับแบบนี้:

```text
GATE:
STEP:
FILES_CHANGED:
WHAT_CHANGED:
UX_CHANGES_SUMMARY:
COLOR_SYSTEM:
NAVIGATION_STRUCTURE:
LOGIC_UNCHANGED_CONFIRMATION:
TEST_RESULT:
LIMITATIONS:
HARD_BANS_CONFIRMED:
SHOULD_OWNER_ACCEPT:
NEXT_SINGLE_STEP:
```

ถ้าไม่มี `TEST_RESULT` ให้ถือว่ายังไม่ปิด Gate

---

# 11. Current Handoff

V1.2 Thai Dashboard Layout and Visual System เสร็จแล้วและพร้อมให้เจ้าของตรวจรับ โดยยังไม่อนุญาต deployment, production หรือ feature expansion

```text
CURRENT_GATE = V1_2_THAI_DASHBOARD_LAYOUT_COMPLETE
CURRENT_BLOCKER = NONE
NEXT_SINGLE_ACTION = OWNER_REVIEW_AND_ACCEPT_V1_2_THAI_DASHBOARD_LAYOUT
```

---

# 12. Status After V1.2 Presentation Pass

V1.2 dashboard layout ปิดแล้วและรอ owner acceptance

`NO_FURTHER_WORK_UNIT_AUTHORIZED`

การเริ่ม work unit ถัดไปหรือ production hardening ต้องมี owner authorization และ scope ใหม่โดยชัดเจน

```text
SCORING_CREATED = YES
DAY_MODE_CLASSIFICATION_CREATED = YES
TOMORROW_REPLANNER_CREATED = YES
ROUGH_30_DAY_PLANNER_CREATED = YES
UX_POLISH_CREATED = YES
GATE_8_AUTHORIZED = YES
GATE_9_AUTHORIZED = YES
GATE_9_COMPLETE = YES
V1_LOCAL_ONLY = YES
V1_1_THAI_PUBLIC_UX_READINESS = YES
V1_1_THAI_DAILY_USE_UX_REFINEMENT = YES
V1_2_THAI_DASHBOARD_LAYOUT = YES
ONE_STREAMLIT_APP = YES
SIDEBAR_NAVIGATION = YES
PAGES_DIRECTORY = NO
DEFAULT_VIEW_TODAY = YES
ROUGH_30_DAY_PLAN_OWN_VIEW = YES
THAI_UI_DOMINANT = YES
TECHNICAL_GATE_LABELS_VISIBLE = NO
RAW_HTML_UI_BUG_FIXED = YES
PRODUCTION_READY = NO
MEDICAL_ADVICE = NO
DEPLOYMENT_AUTHORIZED = NO
NEXT_WORK_UNIT_AUTHORIZED = NO
```

ห้ามเริ่ม upgrade หรือ production scope โดยไม่มีคำสั่งใหม่จากเจ้าของ

---

# 13. Final Reminder

กฎจำหลัก:

> ทำทีละ Gate  
> หนึ่งรอบ หนึ่งงาน  
> เว็บต้องใช้ได้ก่อน  
> ค่อยสวยขึ้น  
> แล้วค่อยฉลาดขึ้น  
> ห้ามสร้างระบบใหญ่ก่อนพิสูจน์ว่าเปิดใช้จริงได้

END OF FILE
