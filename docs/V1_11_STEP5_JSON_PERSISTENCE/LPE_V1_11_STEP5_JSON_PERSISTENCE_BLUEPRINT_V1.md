# LPE V1.11 Step 5 — JSON Export/Import Persistence Blueprint V1

สถานะ: Design-only / ยังไม่แก้ `app.py`  
เป้าหมาย: ออกแบบ persistence แบบไฟล์ JSON ก่อน เพื่อให้ข้อมูลไม่หายเมื่อ refresh โดยยังไม่ใช้ database, login, external API หรือ deploy

---

## 1. ปัญหาที่ต้องแก้

ตอนนี้ข้อมูลหลักยังอยู่ใน `st.session_state` เท่านั้น:

```text
- lpe_profile
- lpe_daily_contexts
- daily_plan ที่คำนวณจาก profile + context
- lpe_daily_results
```

ข้อเสีย:

```text
- refresh แล้วข้อมูลอาจหาย
- ปิด browser แล้วเริ่มใหม่ไม่ได้
- ทบทวนย้อนหลังไม่ได้
- pattern candidates ใช้ต่อวันถัดไปไม่ได้
- ยังไม่พร้อม commit/push/deploy เป็น product จริง
```

Step 5 จึงต้องออกแบบ JSON persistence ก่อนลงมือ patch

---

## 2. หลักการ Persistence

ใช้หลักนี้:

```text
1. ไม่ใช้ database ในรอบแรก
2. ไม่ใช้ login
3. ไม่ใช้ external API
4. ให้ user export/import JSON เอง
5. session_state ยังเป็น runtime หลัก
6. JSON เป็น portable snapshot
7. ห้าม auto-overwrite Core Life Profile จาก reflection
```

แนวคิดคือ:

```text
Session State = สิ่งที่ app ใช้งานตอนเปิดอยู่
JSON Snapshot = ไฟล์สำรอง/นำกลับมาใช้
```

---

## 3. ข้อมูลที่ควรเก็บ

### 3.1 Metadata

```text
- app_name
- schema_version
- exported_at
- user_label
- source
```

### 3.2 Core Life Profile

มาจาก Step 1:

```text
- nickname
- core_life_profile_version
- life_story_modes
- life_story_profile_summary
- life_story_missing_modes
- life_story_last_updated
```

### 3.3 Daily Contexts

มาจาก Step 2:

```text
lpe_daily_contexts:
  YYYY-MM-DD:
    - date
    - sleep_hours
    - energy_level
    - mood
    - today_shift
    - urgent_events
    - physical_condition
    - today_main_focus
    - today_constraints
    - today_story
    - after_save_summary
    - updated
```

### 3.4 Daily Plans

มาจาก Step 3:

```text
lpe_daily_plans:
  YYYY-MM-DD:
    - date
    - plan_summary
    - risk_level
    - confidence_level
    - time_blocks
    - avoid_today
    - sleep_protection
    - minimum_viable_day
    - missing_information
    - generated_at
```

หมายเหตุ: ตอนนี้ plan อาจยังคำนวณสด ไม่ได้เก็บใน session เสมอ  
Step 5.1 patch อาจเลือกบันทึก plan snapshot ตอนกด export

### 3.5 Daily Results

มาจาก Step 4:

```text
lpe_daily_results:
  YYYY-MM-DD:
    - date
    - result_summary
    - completion_score
    - task_results
    - daily_reflection
    - pattern_candidates
    - next_day_seed
```

### 3.6 Pattern Candidates

ควรเก็บเป็นประวัติ แต่ยังไม่เปลี่ยน profile อัตโนมัติ:

```text
pattern_candidates_history:
  - date
  - observation
  - evidence
  - confidence
  - source
  - should_update_profile
```

---

## 4. JSON Top-level Structure

```json
{
  "app_name": "Life Priority Engine",
  "schema_version": "lpe_v1_11_json_snapshot_v1",
  "exported_at": "2026-06-22T18:00:00+07:00",
  "user_label": "local_user",
  "runtime_note": "manual_export_import_no_database",
  "core_life_profile": {},
  "daily_contexts": {},
  "daily_plans": {},
  "daily_results": {},
  "pattern_candidates_history": [],
  "import_notes": []
}
```

---

## 5. Export Flow

หน้าแนะนำ:

```text
สำรองข้อมูล
```

หรือ:

```text
ข้อมูลของฉัน
```

Route แนะนำ:

```text
สำรองข้อมูล
```

Export UI:

```text
1. ปุ่ม “เตรียมไฟล์สำรอง JSON”
2. preview ว่าจะ export อะไร
3. download_button สำหรับไฟล์ .json
4. แสดง schema_version
5. แสดงคำเตือนว่าเป็นไฟล์ส่วนตัว
```

Filename format:

```text
life_priority_engine_snapshot_YYYYMMDD_HHMMSS.json
```

---

## 6. Import Flow

Import UI:

```text
1. file_uploader รับ .json
2. validate schema_version
3. preview ข้อมูลที่จะนำเข้า
4. checkbox ยืนยันว่าเข้าใจว่าจะเขียนทับ session ปัจจุบัน
5. ปุ่ม “นำเข้าข้อมูลเข้า session”
```

Validation ขั้นต่ำ:

```text
- file ต้องเป็น JSON
- schema_version ต้องตรงหรืออยู่ใน supported versions
- core_life_profile ต้องเป็น object
- daily_contexts ต้องเป็น object
- daily_results ต้องเป็น object
- ห้าม execute code จากไฟล์
- ห้ามรับไฟล์ใหญ่เกินจำเป็น
```

---

## 7. Conflict Strategy

ถ้านำเข้าข้อมูลชนกับ session ปัจจุบัน:

MVP ใช้ 2 mode:

```text
replace_session = เขียนทับ session ทั้งหมด
merge_by_date = รวม daily_contexts/daily_results ตามวันที่
```

รอบแรกควรใช้:

```text
replace_session only
```

เพราะง่าย ตรวจสอบได้ และลด bug

merge_by_date ค่อยเป็น Step 5.2

---

## 8. Security / Privacy

JSON snapshot อาจมีข้อมูลส่วนตัว:

```text
- ชีวิตส่วนตัว
- งาน/เวร
- สุขภาพ
- การเรียน
- reflection
- pattern candidates
```

ต้องแสดงคำเตือน:

```text
ไฟล์นี้อาจมีข้อมูลส่วนตัว ควรเก็บไว้ในที่ปลอดภัย และไม่อัปโหลดสาธารณะ
```

ห้าม:

```text
- ส่งไฟล์ไป server ภายนอก
- upload ไป API
- เก็บ token
- เก็บ password
- เก็บข้อมูลบัตร/บัญชี
```

---

## 9. Acceptance สำหรับ Step 5.1 Patch

Step 5.1 จะถือว่า PASS เมื่อ:

```text
1. เพิ่ม route “สำรองข้อมูล”
2. เพิ่ม page_json_persistence หรือ page_data_backup
3. มี export snapshot เป็น dict
4. มี download_button สำหรับ JSON
5. มี file_uploader สำหรับ import JSON
6. validate schema_version
7. import เข้า session_state ได้
8. py_compile PASS
9. duplicate function scan PASS
10. route scan PASS
11. persistence scan PASS
12. ไม่มี login/database/API/deploy
13. WEB_RUN=NO
```

---

## 10. สิ่งที่ยังไม่ทำใน Step 5

```text
- ยังไม่ใช้ database
- ยังไม่ทำ user account
- ยังไม่ sync cloud
- ยังไม่ auto-save
- ยังไม่ merge conflict ขั้นสูง
- ยังไม่ encrypt file
- ยังไม่ deploy
```

---

## 11. One Web Run Later

เมื่อ batch ครบ ค่อยรันเว็บรอบเดียว และทดสอบ flow:

```text
1. ตั้งค่าชีวิต
2. เช็คอินวันนี้
3. แผนวันนี้
4. ทบทวนวันนี้
5. สำรองข้อมูล
6. download JSON
7. refresh หรือเปิดใหม่
8. import JSON
9. ตรวจว่าข้อมูลกลับมา
```

---

## 12. Next After Step 5

```text
Step 5.1 — JSON Export/Import Persistence Patch Local Only No Web
Step 6 — Static Product Flow Audit
Step 7 — One Local Web Run
Step 8 — Commit preparation gate
```
