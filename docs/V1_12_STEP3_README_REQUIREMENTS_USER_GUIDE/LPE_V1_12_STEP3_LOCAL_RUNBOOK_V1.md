# LPE V1.12 Step 3 — Local Runbook V1

## Run locally

```bash
cd /mnt/d/LIFE_PRIORITY_ENGINE
.venv/bin/python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## Install dependencies

```bash
cd /mnt/d/LIFE_PRIORITY_ENGINE
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

## Verify

Open:

```text
http://localhost:8501
```

Expected navigation:

```text
ตั้งค่าชีวิต
เช็คอินวันนี้
แผนวันนี้
ทบทวนวันนี้
สำรองข้อมูล
```

## Stop server

Press Ctrl+C in the terminal running Streamlit.
