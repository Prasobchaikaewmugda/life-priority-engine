# Life Priority Engine

Life Priority Engine คือเว็บ Streamlit สำหรับช่วยจัดลำดับชีวิตรายวันแบบใช้งานจริง

เป้าหมายหลัก:

> ช่วยให้ผู้ใช้ไม่ทำสิ่งไม่สำคัญก่อนสิ่งสำคัญ
> และไม่ฝืนร่างกายเพื่อเอาชนะตาราง

สถานะปัจจุบัน: **V1.11 public usable baseline accepted**

- Latest baseline commit: `27e61aa`
- Full commit: `27e61aa3424de6e76996679e08e543189323fb62`
- Commit subject: `LPE V1.11 local workflow with autosave and JSON persistence`
- Public app: https://life-priority-engine.streamlit.app

---

## 1. ใช้เว็บ public

เปิด:

```text
https://life-priority-engine.streamlit.app
```

หน้าใช้งานหลักมี 5 หน้า:

1. ตั้งค่าชีวิต
2. เช็คอินวันนี้
3. แผนวันนี้
4. ทบทวนวันนี้
5. สำรองข้อมูล

ถ้าเปิด public app แล้วข้อมูลว่าง ให้ไปหน้า **สำรองข้อมูล** แล้วนำเข้าไฟล์ JSON snapshot ของคุณ

---

## 2. วิธีใช้รอบปกติ

### ขั้นที่ 1 — ตั้งค่าชีวิต

กรอกข้อมูลชีวิตระยะยาว 5 โหมด:

1. เป้าหมายและปัญหาที่อยากแก้
2. เวลาและจังหวะชีวิต
3. สุขภาพและพลังงาน
4. งาน / เงิน / ภาระที่ห้ามพลาด
5. เรื่องราวชีวิตและกฎส่วนตัว

เป้าหมายคือให้ขึ้นครบ:

```text
ครบ 5/5 โหมด — พร้อมใช้เป็นฐานชีวิต
```

### ขั้นที่ 2 — เช็คอินวันนี้

กรอกบริบทเฉพาะวันนี้ เช่น:

- นอนกี่ชั่วโมง
- พลังงานวันนี้
- เวร/งานวันนี้
- เรื่องด่วน
- โฟกัสหลักวันนี้
- ข้อจำกัดที่ห้ามฝืน

### ขั้นที่ 3 — แผนวันนี้

ระบบสร้างแผนรายวันจากข้อมูลชีวิต + บริบทวันนี้

แผนควรมี:

- งานหลัก
- งานรอง
- สิ่งที่ควรเลี่ยง
- fallback ถ้าเหนื่อย

### ขั้นที่ 4 — ทบทวนวันนี้

บันทึกผลจริง:

- ทำอะไรสำเร็จ
- อะไรหลุด
- ตัวขวางหลัก
- พรุ่งนี้ควรปรับอย่างไร

### ขั้นที่ 5 — สำรองข้อมูล

Export JSON ทุกครั้งหลังใช้งานสำคัญ เพื่อกันข้อมูลหายจาก session/browser

---

## 3. สำรองและกู้คืนข้อมูล JSON

ระบบนี้ยังไม่มีบัญชีผู้ใช้และไม่มีฐานข้อมูล cloud

ดังนั้นข้อมูลสำคัญต้องสำรองด้วย JSON

### Export

ไปหน้า **สำรองข้อมูล** แล้วกดดาวน์โหลด JSON snapshot

ตัวอย่างชื่อไฟล์:

```text
life_priority_engine_snapshot_YYYYMMDD_HHMMSS.json
```

### Import

ไปหน้า **สำรองข้อมูล** แล้ว upload JSON snapshot

หลัง import สำเร็จ ให้กลับไปหน้า **ตั้งค่าชีวิต** และตรวจว่าแสดงครบ 5/5 โหมด

---

## 4. รันบนเครื่องตัวเอง

ไปที่โฟลเดอร์โปรเจกต์:

```bash
cd /mnt/d/LIFE_PRIORITY_ENGINE
```

ถ้าใช้ virtualenv ของโปรเจกต์:

```bash
.venv/bin/python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

เปิดใน browser:

```text
http://localhost:8501
```

หรือจาก WSL network:

```text
http://172.21.122.17:8501
```

> หมายเหตุ: เครื่องนี้เคยพบว่า `streamlit run app.py` ตรง ๆ และ `python3 -m streamlit` ใช้ไม่ได้ เพราะ Streamlit อยู่ใน `.venv`

---

## 5. ติดตั้ง dependencies

```bash
cd /mnt/d/LIFE_PRIORITY_ENGINE
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

---

## 6. Data safety

V1 ใช้ session/local JSON เท่านั้น

สิ่งที่ไม่มีในระบบนี้:

- ไม่มี login
- ไม่มี multi-user
- ไม่มี cloud database
- ไม่มี API key
- ไม่มี broker/trading order
- ไม่มี medical diagnosis
- ไม่มีระบบ sync อัตโนมัติ

ไฟล์ที่ไม่ควร commit:

- `data/lpe_local_snapshot.json`
- `life_priority_engine_snapshot_*.json`
- `backups/`
- `reports/`

---

## 7. ขอบเขตสุขภาพ

ระบบนี้ช่วยปรับความหนักของแผนตามพลังงาน/การนอน/เวรได้

ระบบนี้ไม่ใช่แพทย์ และไม่ทำสิ่งต่อไปนี้:

- ไม่วินิจฉัยโรค
- ไม่สั่งยา
- ไม่รับประกันว่าอาการปลอดภัย
- ไม่แทนการพบแพทย์เมื่อมีอาการรุนแรงหรือเป็นซ้ำ

---

## 8. สถานะ Release

### Public usable baseline

```text
LOCAL_CORE_FLOW = PASS
JSON_IMPORT_EXPORT = PASS
PUBLIC_DEPLOYMENT = PASS
PUBLIC_ACCEPTANCE = PASS
```

### Clean release package

ยัง HOLD เพราะยังต้องเก็บงาน:

1. ตรวจ README / requirements / user guide
2. จัดการ untracked docs/scripts จำนวนมาก
3. เตรียม release tag
4. ค่อยพิจารณา feature ฉลาดขึ้นหลัง baseline สะอาด

---

## 9. Roadmap ถัดไป

ลำดับที่ถูกต้องตอนนี้:

1. Project completion audit
2. README + requirements + user guide
3. Repo cleanup plan
4. Release tag preparation
5. หลังจากนั้นค่อยกลับไปเพิ่ม adaptive planning หรือใช้ระบบเพื่ออ่านหนังสือจริง

---

## 10. Hard bans

ห้ามเพิ่มโดยไม่ผ่าน gate:

- Login
- Cloud database
- API key
- Broker API
- Trading logic
- Medical diagnosis
- Multi-user system
- Notification
- Mobile app
- Overengineering

---

## 11. Current limitation

ระบบนี้ยังต้อง export/import JSON เอง เพราะยังไม่มี account หรือ database

นี่เป็นข้อจำกัดที่ตั้งใจไว้ใน V1 เพื่อให้ระบบง่าย ปลอดภัย และ deploy ได้เร็ว
