# LPE V1.11 Step 5 JSON Persistence Acceptance Criteria V1

## Gate Type

Design-only for this step. No `app.py` mutation.

## Preconditions

```text
- page_settings exists
- page_daily_checkin exists
- page_daily_plan exists
- page_daily_reflection exists
- py_compile PASS
```

## Step 5.1 Patch Must Add Later

```text
- route “สำรองข้อมูล”
- page_json_persistence or page_data_backup
- build_json_snapshot function
- validate_json_snapshot function
- import_json_snapshot_to_session function
- download_button for JSON
- file_uploader for JSON
- schema_version validation
- privacy warning
```

## Must Not Add

```text
- login
- database
- external API
- cloud sync
- token storage
- password storage
- commit
- push
- deploy
```

## Static Verification For Patch

```text
- py_compile PASS
- duplicate function scan PASS
- route scan PASS
- persistence scan PASS
- forbidden scope scan PASS
- WEB_RUN=NO
```

## Manual Verification When Web Is Run Once

```text
1. กรอกตั้งค่าชีวิต
2. กรอกเช็คอินวันนี้
3. เปิดแผนวันนี้
4. เปิดทบทวนวันนี้
5. เปิดสำรองข้อมูล
6. download JSON
7. refresh app
8. import JSON
9. ตรวจว่าข้อมูลกลับมาใน session
```
