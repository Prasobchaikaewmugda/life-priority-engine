# LPE V1.11 Step 3 Daily Plan Engine Acceptance Criteria V1

## Gate Type

Design-only for this step. No `app.py` mutation.

## Static Preconditions

```text
- page_settings exists
- page_daily_checkin exists
- lpe_profile schema exists
- lpe_daily_contexts schema exists
- py_compile PASS
- duplicate function scan PASS
```

## Step 3 Patch Must Add Later

```text
- page_daily_plan or equivalent page
- route option for “แผนวันนี้”
- rule-based plan generator
- time_blocks
- reason per block
- fallback per block
- missing_information
- sleep_protection
- avoid_today
```

## Must Not Add Yet

```text
- login
- database
- API
- permanent persistence
- commit
- push
- deploy
```

## Manual Verification When Web Is Run Once

```text
1. กรอกตั้งค่าชีวิต
2. กรอกเช็คอินวันนี้
3. เปิดแผนวันนี้
4. เห็นแผนแบบเวลา
5. เห็นเหตุผล
6. เห็น fallback
7. เห็นสิ่งที่ควรเลี่ยง
8. เห็นข้อมูลที่ยังขาดถ้ากรอกไม่พอ
```
