# LPE V1.11 Step 4 — Task Result + Daily Reflection Blueprint V1

สถานะ: Design-only / ยังไม่แก้ `app.py`  
เป้าหมาย: ออกแบบระบบรับผลลัพธ์หลังทำตามแผน เพื่อให้ระบบเริ่ม “เรียนรู้จากวันนี้” โดยยังไม่ใช้ database หรือ external AI/API

---

## 1. วัตถุประสงค์

หลัง Step 3 ระบบสร้างแผนวันนี้ได้แล้ว แต่ถ้าไม่มี Step 4 ระบบจะไม่รู้ว่าแผนนั้นใช้ได้จริงหรือไม่

Step 4 ต้องตอบ 6 คำถาม:

```text
1. วันนี้ทำอะไรสำเร็จ
2. อะไรไม่สำเร็จ
3. เพราะอะไรถึงไม่สำเร็จ
4. พลังงานจริงของวันต่างจากตอนเช็คอินไหม
5. แผนช่วงไหนใช้ได้ / ใช้ไม่ได้
6. พรุ่งนี้ควรปรับอะไร
```

---

## 2. หลักการออกแบบ

Step 4 ไม่ใช่แค่ checklist เพราะถ้าระบบรู้แค่ว่า “เสร็จ/ไม่เสร็จ” จะเรียนรู้ไม่ได้

ต้องมี 3 ชั้น:

```text
Task Result
Daily Reflection
Pattern Candidate
```

### 2.1 Task Result

เก็บผลลัพธ์ของแต่ละ time block หรือ task:

```text
- ทำสำเร็จ
- ทำบางส่วน
- ไม่ได้ทำ
- เลื่อน
- ตัดทิ้ง
```

และต้องถามเหตุผล:

```text
- พลังงานไม่พอ
- เวลาจริงไม่พอ
- มีงานแทรก
- ป่วย/เหนื่อย
- task ใหญ่เกินไป
- ไม่ชัดว่าต้องเริ่มตรงไหน
- ไม่สำคัญจริง
```

### 2.2 Daily Reflection

เก็บภาพรวมของวัน:

```text
- วันนี้เป็นวันที่พลังงานต่ำ/กลาง/สูงจริงแค่ไหน
- แผนแน่นเกินไปไหม
- อะไรทำให้แผนพัง
- อะไรช่วยให้ทำสำเร็จ
- พรุ่งนี้ควรเปลี่ยนอะไร
```

### 2.3 Pattern Candidate

ยังไม่เขียนทับ Core Life Profile ทันที  
แต่สร้าง “ข้อสังเกตชั่วคราว” ก่อน เช่น:

```text
- หลังเวรดึก พลังงานต่ำกว่าที่คิด
- ถ้านอนต่ำกว่า 6 ชั่วโมง งานโปรเจกต์มักไม่คืบ
- อ่านหนังสือสำเร็จเมื่อ block สั้นกว่า 30 นาที
- ออกกำลังช่วงเย็นทำได้ ถ้าไม่วางหลังงานหนักทันที
```

---

## 3. Input ที่ใช้

### 3.1 จาก Step 1 — Core Life Profile

```text
- goals
- time_rhythm
- health_energy
- obligations
- life_rules
```

### 3.2 จาก Step 2 — Daily Check-in

```text
- sleep_hours
- energy_level
- mood
- today_shift
- urgent_events
- physical_condition
- today_main_focus
- today_constraints
- today_story
```

### 3.3 จาก Step 3 — Daily Plan

```text
- plan_summary
- risk_level
- confidence_level
- time_blocks
- avoid_today
- sleep_protection
- minimum_viable_day
- missing_information
```

### 3.4 จากผู้ใช้หลังทำงาน

```text
- task status
- actual start/end หรือเวลาที่ใช้จริง
- reason if failed
- result note
- energy after task
- daily reflection
```

---

## 4. Output ที่ต้องได้

```text
daily_result
├─ date
├─ result_summary
├─ completion_score
├─ task_results
│  ├─ block_id
│  ├─ planned_activity
│  ├─ status
│  ├─ actual_minutes
│  ├─ reason
│  ├─ result_note
│  ├─ energy_after
│  └─ next_adjustment
├─ daily_reflection
│  ├─ actual_energy
│  ├─ what_worked
│  ├─ what_failed
│  ├─ main_blocker
│  ├─ tomorrow_adjustment
│  └─ free_story
├─ pattern_candidates
│  ├─ observation
│  ├─ evidence
│  ├─ confidence
│  └─ should_update_profile
└─ next_day_seed
   ├─ recommended_focus
   ├─ recommended_energy_mode
   ├─ suggested_minimum_day
   └─ warnings
```

---

## 5. Status Vocabulary

Task status ต้องใช้คำจำกัดความที่เสถียร:

```text
done = ทำสำเร็จ
partial = ทำบางส่วน
skipped = ไม่ได้ทำ
moved = เลื่อนไปวันอื่น
dropped = ตัดทิ้ง
```

Reason vocabulary:

```text
low_energy
not_enough_time
urgent_event
health_issue
task_too_big
unclear_start
low_priority
distraction
overplanned
other
```

---

## 6. Rule-based Reflection Logic

### 6.1 Completion Score

```text
done = 1.0
partial = 0.5
moved = 0.25
skipped = 0
dropped = neutral ถ้าเป็นการตัดที่ดี
```

แสดงเป็น:

```text
0–30% = วันนี้แผนไม่ตรงชีวิตจริง
31–60% = วันนี้ทำได้บางส่วน ต้องลด/จัดใหม่
61–85% = วันนี้แผนใช้ได้
86–100% = วันนี้แผนค่อนข้างแม่น
```

### 6.2 Pattern Candidate Rules

ถ้าเกิดซ้ำในอนาคตจึงค่อยเสนอแก้ profile

ใน MVP ยังไม่มี persistence ดังนั้น Step 4 patch ควรแสดงเป็น “candidate” ก่อน:

```text
ถ้า sleep < 6 และงานหลักไม่สำเร็จ:
- candidate: วันที่นอนน้อยควรใช้ minimum plan

ถ้า energy <= 2 และโปรเจกต์ไม่สำเร็จ:
- candidate: วันที่พลังต่ำไม่ควรวางโปรเจกต์หนัก

ถ้า task status = done และ actual_minutes <= planned block:
- candidate: task ขนาดนี้เหมาะกับวันแบบนี้

ถ้า reason = unclear_start:
- candidate: task ต้องแตกเป็นขั้นย่อยก่อนวางแผน
```

---

## 7. Page Design

หน้า Step 4 ควรชื่อ:

```text
ผลลัพธ์วันนี้
```

หรือ:

```text
ทบทวนวันนี้
```

แนะนำ route:

```text
ทบทวนวันนี้
```

โครงหน้า:

```text
1. สรุปแผนที่ระบบตั้งไว้
2. กรอกผลลัพธ์ของแต่ละ task
3. กรอก reflection รวมของวัน
4. ระบบสรุปสิ่งที่เรียนรู้
5. ระบบแนะนำ seed สำหรับพรุ่งนี้
```

---

## 8. Acceptance สำหรับ Step 4 Patch

Step 4 patch จะถือว่า PASS เมื่อ:

```text
1. เพิ่ม route “ทบทวนวันนี้”
2. เพิ่ม page_daily_reflection หรือ page_task_result
3. อ่าน plan จาก Step 3 ได้
4. แสดง task blocks ให้กรอก status
5. รับ actual_minutes / reason / note
6. รับ daily reflection
7. คำนวณ completion_score
8. แสดง pattern_candidates
9. แสดง next_day_seed
10. py_compile PASS
11. duplicate function scan PASS
12. ไม่มี login/database/API/persistence/deploy
13. WEB_RUN=NO
```

---

## 9. สิ่งที่ยังไม่ทำ

```text
- ยังไม่บันทึกถาวร
- ยังไม่สร้าง learned patterns จริง
- ยังไม่แก้ Core Life Profile อัตโนมัติ
- ยังไม่ทำ export/import JSON
- ยังไม่ใช้ AI/API
- ยังไม่ commit/push/deploy
```

---

## 10. Next After Step 4

หลัง Step 4 ควรเป็น:

```text
Step 4.1 — Task Result + Daily Reflection Patch Local Only No Web
Step 5 — JSON Export/Import Persistence Design
Step 5.1 — JSON Persistence Patch
Step 6 — Static UX Text Consolidation
Step 7 — One Local Web Run
```
