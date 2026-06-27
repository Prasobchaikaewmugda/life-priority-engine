
from __future__ import annotations

import csv
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import streamlit as st

# BEGIN LPE_PHASE11A_PROFILE_PERSISTENCE_PATCH_V1
# Local-only persistence for the 5-module detailed interview answers.
# Scope: Phase11A blocker fix only. No cloud, no database, no login, no external API.
def _lpe11a_profile_persistence_file():
    from pathlib import Path
    return Path("data") / "lpe_phase11a_profile_answers.json"


def _lpe11a_profile_persistence_load():
    import json
    path = _lpe11a_profile_persistence_file()
    if not path.exists():
        return {"schema_version": "lpe_phase11a_profile_answers_v1", "answers_by_title": {}, "answers_by_key": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"schema_version": "lpe_phase11a_profile_answers_v1", "answers_by_title": {}, "answers_by_key": {}}
    if not isinstance(data, dict):
        data = {}
    data.setdefault("schema_version", "lpe_phase11a_profile_answers_v1")
    data.setdefault("answers_by_title", {})
    data.setdefault("answers_by_key", {})
    if not isinstance(data.get("answers_by_title"), dict):
        data["answers_by_title"] = {}
    if not isinstance(data.get("answers_by_key"), dict):
        data["answers_by_key"] = {}
    return data


def _lpe11a_profile_persistence_save(data):
    import json
    from datetime import datetime, timezone
    path = _lpe11a_profile_persistence_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    data["schema_version"] = "lpe_phase11a_profile_answers_v1"
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _lpe11a_profile_persistence_bootstrap_module_keys(modules):
    """Load saved 5-module answers into stable Streamlit widget keys before rendering textareas."""
    try:
        data = _lpe11a_profile_persistence_load()
        by_title = data.get("answers_by_title", {}) or {}
        by_key = data.get("answers_by_key", {}) or {}
        module_meta = []
        for module in modules:
            key = str(module.get("key", "")).strip()
            title = str(module.get("title", "")).strip()
            if not key:
                continue
            module_meta.append({"key": key, "title": title})
            widget_key = "lpe10oc_answer_" + key
            current = str(st.session_state.get(widget_key, "") or "")
            saved = str(by_key.get(key, "") or by_title.get(title, "") or "")
            if saved.strip() and not current.strip():
                st.session_state[widget_key] = saved
        st.session_state["_lpe11a_profile_module_meta"] = module_meta
        st.session_state["_lpe11a_profile_persistence_loaded"] = True
    except Exception as exc:
        st.session_state["_lpe11a_profile_persistence_error"] = str(exc)


def _lpe11a_profile_persistence_autosave_session():
    """Autosave current 5-module answers from session_state to local JSON after render."""
    try:
        meta = st.session_state.get("_lpe11a_profile_module_meta", [])
        if not isinstance(meta, list) or not meta:
            return
        data = _lpe11a_profile_persistence_load()
        by_title = data.setdefault("answers_by_title", {})
        by_key = data.setdefault("answers_by_key", {})
        changed = False
        for item in meta:
            if not isinstance(item, dict):
                continue
            key = str(item.get("key", "")).strip()
            title = str(item.get("title", "")).strip()
            if not key:
                continue
            widget_key = "lpe10oc_answer_" + key
            value = str(st.session_state.get(widget_key, "") or "")
            if value.strip():
                if by_key.get(key) != value:
                    by_key[key] = value
                    changed = True
                if title and by_title.get(title) != value:
                    by_title[title] = value
                    changed = True
        if changed:
            _lpe11a_profile_persistence_save(data)
            st.session_state["_lpe11a_profile_persistence_last_saved"] = data.get("updated_at", "")
    except Exception as exc:
        st.session_state["_lpe11a_profile_persistence_error"] = str(exc)
# END LPE_PHASE11A_PROFILE_PERSISTENCE_PATCH_V1


# BEGIN LPE_PHASE11A_PROFILE_PERSISTENCE_PATCH_V2_PER_MODULE_KEYS
# Runtime fix: each detailed-interview module has its own stable textarea key.
# This prevents answer loss when switching 1→2→1. Local JSON only; no cloud/database/network.
def _lpe11a_profile_v2_widget_key(module_key):
    safe = str(module_key or "").strip() or "unknown"
    return "lpe11a_profile_answer_v2_" + safe


def _lpe11a_profile_v2_load():
    data = _lpe11a_profile_persistence_load()
    data.setdefault("answers_by_title", {})
    data.setdefault("answers_by_key", {})
    if not isinstance(data.get("answers_by_title"), dict):
        data["answers_by_title"] = {}
    if not isinstance(data.get("answers_by_key"), dict):
        data["answers_by_key"] = {}
    return data


def _lpe11a_profile_v2_save(data):
    _lpe11a_profile_persistence_save(data)


def _lpe11a_profile_v2_module_answer(module_key, module_title):
    data = _lpe11a_profile_v2_load()
    by_key = data.get("answers_by_key", {}) or {}
    by_title = data.get("answers_by_title", {}) or {}
    return str(by_key.get(str(module_key), "") or by_title.get(str(module_title), "") or "")


def _lpe11a_profile_v2_seed_widget(module_key, module_title):
    widget_key = _lpe11a_profile_v2_widget_key(module_key)
    saved = _lpe11a_profile_v2_module_answer(module_key, module_title)
    # Seed only when the widget key is absent or empty. Never overwrite typed text during rerun.
    if saved.strip() and not str(st.session_state.get(widget_key, "") or "").strip():
        st.session_state[widget_key] = saved
    return widget_key


def _lpe11a_profile_v2_save_answer(module_key, module_title, value):
    value = str(value or "")
    # Avoid saving the generic placeholder as a real answer.
    generic = "ตอบเป็นภาษาคนธรรมดาได้เลย"
    if not value.strip() or generic in value:
        return False
    data = _lpe11a_profile_v2_load()
    by_key = data.setdefault("answers_by_key", {})
    by_title = data.setdefault("answers_by_title", {})
    changed = False
    if by_key.get(str(module_key)) != value:
        by_key[str(module_key)] = value
        changed = True
    if module_title and by_title.get(str(module_title)) != value:
        by_title[str(module_title)] = value
        changed = True
    if changed:
        _lpe11a_profile_v2_save(data)
        st.session_state["_lpe11a_profile_persistence_last_saved"] = data.get("updated_at", "")
    return changed


def _lpe11a_profile_v2_sync_legacy_keys(modules):
    """Keep old completeness checks compatible while rendering with v2 widget keys."""
    for module in modules:
        key = str(module.get("key", ""))
        title = str(module.get("title", ""))
        saved = _lpe11a_profile_v2_module_answer(key, title)
        legacy_key = "lpe10oc_answer_" + key
        if saved.strip():
            st.session_state[legacy_key] = saved
        widget_key = _lpe11a_profile_v2_widget_key(key)
        current = str(st.session_state.get(widget_key, "") or "")
        if current.strip() and "ตอบเป็นภาษาคนธรรมดาได้เลย" not in current:
            _lpe11a_profile_v2_save_answer(key, title, current)
            st.session_state[legacy_key] = current
# END LPE_PHASE11A_PROFILE_PERSISTENCE_PATCH_V2_PER_MODULE_KEYS




# PHASE10H_SHIFT_AWARE_DAILY_SCHEDULE_CONTENT_AND_PREMIUM_ROW_STATUS_PATCH_V1
# PHASE10H_COLUMN_TAXONOMY
# PHASE10H_SHIFT_AWARE_SCHEDULE
# PHASE10H_MORNING_SHIFT_TEMPLATE
# PHASE10H_AFTERNOON_SHIFT_TEMPLATE
# PHASE10H_NIGHT_SHIFT_TEMPLATE
# PHASE10H_DAYOFF_TEMPLATE
# PHASE10H_DEEPER_BODY_CARE_CONTENT
# PHASE10H_DEEPER_REASON_CONTENT
# PHASE10H_DEEPER_SUCCESS_TECHNIQUE_CONTENT
# PHASE10H_ROW_CARD_BORDER
# PHASE10H_TYPOGRAPHY_HIERARCHY
# PHASE10H_PREMIUM_STATUS_SWITCH
# PHASE10H_SCOPE_GUARD

def _lpe_phase10h_css():
    st.markdown("""
    <style>
      .stApp { background: #eef5fb; color: #062447; }
      section[data-testid="stSidebar"] { background: linear-gradient(180deg, #174f8f 0%, #0f477f 100%) !important; }
      section[data-testid="stSidebar"] * { color: #ffffff !important; }
      .block-container { padding-top: 1.15rem !important; max-width: 1120px !important; }
      .lpe10h-hero { background: #ffffff; border: 1px solid #d5e6f6; border-radius: 20px; padding: 20px 22px; box-shadow: 0 10px 28px rgba(15, 76, 129, 0.08); margin-bottom: 16px; }
      .lpe10h-hero h1 { margin: 0 0 8px 0; font-size: 1.85rem; line-height: 1.15; color: #062447; font-weight: 900; }
      .lpe10h-hero p { margin: 0; color: #334155; font-weight: 550; }
      .lpe10h-chip-row { display:flex; gap:10px; flex-wrap:wrap; margin-top: 14px; }
      .lpe10h-chip { display:inline-flex; align-items:center; border:1px solid #bdd7f2; background:#edf6ff; color:#073b76; border-radius: 999px; padding: 7px 12px; font-weight:800; font-size:.86rem; }
      .lpe10h-metrics { display:grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 12px; margin: 0 0 16px 0; }
      .lpe10h-metric { background:#fff; border:1px solid #d8e8f6; border-radius:16px; padding:14px 16px; box-shadow: 0 7px 18px rgba(15, 76, 129, .06); }
      .lpe10h-metric .label { color:#64748b; font-weight:750; font-size:.86rem; margin-bottom: 4px; }
      .lpe10h-metric .value { color:#062447; font-weight:950; font-size:1.45rem; }
      .lpe10h-board-note { color:#475569; font-weight:650; margin: 8px 0 12px 0; }
      .lpe10h-header-grid { display:grid; grid-template-columns: .85fr 1.65fr 1.7fr 1.9fr 2.25fr .7fr; gap:10px; margin: 10px 0 8px 0; }
      .lpe10h-header-cell { background:#e9f4ff; color:#062447; border:1px solid #cbdff4; border-radius:10px; padding:9px 10px; font-weight:900; font-size:.88rem; }
      div[data-testid="stVerticalBlockBorderWrapper"] { border: 1px solid #d9e8f6 !important; border-radius: 16px !important; background: rgba(255,255,255,.76) !important; box-shadow: 0 5px 15px rgba(15, 76, 129, .045) !important; }
      div[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #b9d7f4 !important; box-shadow: 0 8px 22px rgba(15, 76, 129, .075) !important; }
      .lpe10h-time-pill { display:inline-flex; align-items:center; justify-content:center; padding:7px 11px; border-radius:999px; background:#eef7ff; border:1px solid #bad7f3; color:#07569b; font-weight:950; }
      .lpe10h-activity { font-weight:950; color:#062447; line-height:1.35; }
      .lpe10h-text { color:#12344f; font-weight:650; line-height:1.45; font-size:.92rem; }
      .lpe10h-tech strong, .lpe10h-text strong { color:#062447; font-weight:950; }
      .lpe10h-small { color:#64748b; font-weight:650; font-size:.84rem; }
      div[data-testid="stTextInput"] input, div[data-baseweb="select"] > div, textarea { background:#ffffff !important; color:#062447 !important; border-color:#cbdff4 !important; border-radius:10px !important; }
      input::placeholder, textarea::placeholder { color:#70859c !important; opacity: 1 !important; }
      div[data-testid="stToggle"] { display:flex !important; justify-content:center !important; align-items:center !important; min-height:42px !important; }
      div[data-testid="stToggle"] label { min-height: 36px !important; }
      div[data-testid="stToggle"] p { display:none !important; }
      .lpe10h-summary-card { background:#fff; border:1px solid #d8e8f6; border-radius:18px; padding:16px; box-shadow:0 7px 18px rgba(15,76,129,.06); }
      @media (max-width: 900px) {
        .lpe10h-metrics { grid-template-columns: repeat(2, minmax(0,1fr)); }
        .lpe10h-header-grid { display:none; }
      }
    </style>
    """, unsafe_allow_html=True)


def _lpe_phase10h_schedule_templates():
    # Local static templates only. No medical diagnosis, no nutrition prescription, no supplement dosage prescription.
    safety = "ถ้ามีอาหารเสริมหรือวิตามินที่ใช้อยู่แล้ว ให้ยึดตามฉลากหรือคำแนะนำผู้เชี่ยวชาญ"
    return {
        "เวรเช้า": [
            ("06:30", "ตื่น / ดื่มน้ำ / รับแสงเช้า", "น้ำเปล่า 1 แก้ว และโดนแสงเช้าสั้น ๆ ถ้าทำได้", "เริ่มวันแบบไม่ใช้แรงตัดสินใจเยอะ ลดโอกาสไถมือถือทันทีหลังตื่น", "วางน้ำไว้ข้างเตียงตั้งแต่คืนก่อน และ<strong>ลุกก่อนจับมือถือ</strong>"),
            ("07:00", "อาบน้ำ / เตรียมไปทำงาน", "อาหารรองท้องเบา ๆ ถ้าหิว และเตรียมน้ำติดตัว", "ลดความเร่งและลดอารมณ์หงุดหงิดตอนเช้า", "เตรียมของออกจากบ้านตั้งแต่เมื่อคืน เช่น ชุด กระเป๋า เอกสาร"),
            ("07:30", "อาหารเช้า / วิตามินที่ใช้ประจำ", "โปรตีน + คาร์บเล็กน้อย เช่น ไข่ ข้าวเล็กน้อย ผัก หรือเมนูที่ย่อยง่าย; " + safety, "อาหารเช้าที่ไม่หวานจัดช่วยให้พลังงานนิ่งกว่าเริ่มวันด้วยน้ำตาลสูง", "ใช้เมนูซ้ำง่าย ไม่ต้องคิดใหม่ทุกวัน เช่น <strong>ไข่ + ข้าวน้อย + ผัก</strong>"),
            ("08:00", "เข้าเวร / งานหลัก 1 อย่าง", "กาแฟได้ถ้าจำเป็น แต่ลดหวานและดื่มน้ำร่วมด้วย", "ช่วงเช้าเหมาะกับงานที่ต้องใช้สมาธิและการตัดสินใจ", "เริ่มจากงานสำคัญที่สุด 1 อย่างก่อน และ<strong>ไม่เปิด scope ใหม่</strong>"),
            ("10:30", "พักสั้น / รีเซ็ตสมอง", "น้ำเปล่า และพักสายตา 3-5 นาที", "ลดล้าและคืนสมาธิก่อนงานช่วงถัดไป", "เดินสั้น ๆ หรือยืดตัว หลีกเลี่ยงไถมือถือยาว"),
            ("12:00", "พักเที่ยง", "ข้าว + โปรตีน + ผัก และน้ำเปล่า", "เติมพลังโดยไม่ให้บ่ายง่วงมาก ถ้ากินหนักเกินจะเสียสมาธิช่วงบ่าย", "กินอิ่มประมาณ <strong>70-80%</strong> แล้วเดินเบา ๆ ก่อนกลับงาน"),
            ("13:00", "กลับเข้างาน / งานต่อเนื่อง", "น้ำเปล่า วางขวดไว้ใกล้มือ", "รักษา momentum หลังพักเที่ยง ไม่ให้หลุดยาว", "ทวนรายการเดียวก่อนเริ่ม แล้วทำต่อแบบไม่เปลี่ยนงานบ่อย"),
            ("15:30", "พักตา / จัดคิว / รีโฟกัส", "น้ำเปล่าหรือของว่างเบา ๆ ถ้าจำเป็น", "กันพลังตกช่วงบ่ายปลายและลดงานค้างในหัว", "ตั้งเวลา 5 นาที แล้วกลับมาดู <strong>next action เดิม</strong>"),
            ("17:30", "ออกกำลังกาย / เดิน / ยืด", "น้ำเปล่า ก่อนและหลังออกกำลัง", "ช่วยเคลียร์ความเครียดหลังงานและลดความล้าสะสม", "20-30 นาทีพอ ไม่ต้องหนักทุกวัน เน้นต่อเนื่อง"),
            ("19:00", "อาหารเย็น / ลดงานหนัก", "โปรตีนเบา + ผัก / ลดหวานมัน", "ช่วยให้ไม่แน่นท้องก่อนนอนและไม่ลากงานหนักถึงดึก", "เลือกอาหารที่ทำได้จริง ไม่ต้อง perfect"),
            ("21:30", "ปิดงาน / สรุปวัน / เตรียมพรุ่งนี้", "น้ำเล็กน้อย และลดสิ่งกระตุ้น", "ลดเรื่องค้างในหัวก่อนนอน", "เขียน <strong>next single action</strong> แค่ 1 บรรทัด"),
            ("23:00", "เข้านอน", "เลี่ยงมื้อหนักและลดจอก่อนนอนถ้าทำได้", "เวลานอนสม่ำเสมอช่วยให้วันถัดไปเริ่มง่ายขึ้น", "ปิดจอ 30-60 นาที หรือวางมือถือให้ไกลมือ"),
        ],
        "เวรบ่าย": [
            ("08:00", "ตื่นแบบไม่เร่ง / ดื่มน้ำ", "น้ำเปล่า 1 แก้ว และรับแสงเช้าสั้น ๆ", "เริ่มวันแบบฟื้นตัวก่อน ไม่ใช้พลังหมดก่อนเข้าเวร", "ลุกจากเตียงก่อนเช็กมือถือ เพื่อคุมจังหวะวัน"),
            ("08:30", "อาหารเช้า / ตั้งหลัก", "โปรตีน + คาร์บเล็กน้อย และน้ำเปล่า", "ทำให้พลังงานช่วงเช้านิ่งพอสำหรับงานส่วนตัว", "เลือกเมนูซ้ำง่าย ไม่ต้องเสียแรงคิด"),
            ("09:30", "อ่านหนังสือ / งานส่วนตัว 1 อย่าง", "น้ำเปล่า วางใกล้มือ", "ช่วงก่อนเวรเหมาะกับงานส่วนตัวที่ต้องใช้สมาธิ", "ทำแค่ 1 block 25-45 นาที แล้วหยุดก่อนหมดแรง"),
            ("11:30", "อาหารก่อนเข้าเวร", "ข้าว + โปรตีน + ผัก ในปริมาณไม่หนักเกิน", "ลดหิวระหว่างเวรและไม่ให้จุกก่อนเริ่มงาน", "กินอิ่มพอดี ไม่แน่นท้อง"),
            ("12:30", "เตรียมตัว / เดินทาง", "น้ำติดตัว และของใช้จำเป็น", "ลดความเร่งก่อนเริ่มเวร", "เช็กของ 3 อย่าง: กระเป๋า เอกสาร น้ำ"),
            ("14:00", "เริ่มเวรบ่าย", "กาแฟได้ถ้าจำเป็น แต่ไม่หวานมาก", "เริ่มเวรด้วยงานสำคัญก่อนพลังงานตก", "เปิดงานหลักก่อนงานจุกจิก"),
            ("17:30", "พัก / กินเบา ๆ", "น้ำเปล่า หรือของว่างเบา ๆ", "กันพลังตกช่วงกลางเวร", "พักจริง 5-10 นาที ไม่ไถมือถือจนหลุด"),
            ("20:00", "รีโฟกัสช่วงท้ายเวร", "น้ำเปล่า", "ช่วงท้ายเวรมักล้า ต้องลดงานค้างและจบให้ชัด", "เลือก 1 งานปิดท้าย ไม่เปิดงานใหม่ใหญ่"),
            ("22:00", "เลิกเวร / ลดจอ / กลับบ้าน", "น้ำเปล่า และเลี่ยงมื้อหนักทันทีถ้าไม่หิวมาก", "ลดการกระตุ้นก่อนนอน", "กลับถึงบ้านแล้วลดแสง ลดจอให้เร็ว"),
            ("23:00", "อาหารเบา / อาบน้ำ", "อาหารเบา ถ้าหิวจริง เช่น โปรตีนเบา ๆ", "ช่วยไม่ให้แน่นท้องก่อนนอน", "กินเท่าที่จำเป็น ไม่ใช้มื้อดึกแก้เครียด"),
            ("00:00", "ปิดวัน / เข้านอน", "ลดจอและวางมือถือไกลมือ", "ปกป้องเวลานอนหลังเวรบ่าย", "เขียน next action สั้น ๆ แล้วจบวัน"),
        ],
        "เวรดึก": [
            ("10:00", "ตื่น / ฟื้นตัว", "น้ำเปล่า 1 แก้ว และรับแสงเท่าที่ทำได้", "วันเวรดึกต้องเริ่มจากการฟื้นตัว ไม่ใช่ฝืน productive หนัก", "ให้เวลาร่างกายตื่น 20-30 นาทีก่อนงานจริง"),
            ("11:00", "อาหารหลักมื้อแรก", "ข้าว + โปรตีน + ผัก และน้ำเปล่า", "เป็นฐานพลังงานก่อนวันยาวและเวรกลางคืน", "กินพอดี ไม่หนักจนง่วงยาว"),
            ("13:00", "งานเบา / ธุระจำเป็น", "น้ำเปล่า", "เคลียร์สิ่งจำเป็นก่อนเข้าสู่โหมดเวรดึก", "ทำเฉพาะงานที่ต้องทำจริง ไม่เปิดงานใหญ่เกิน"),
            ("15:00", "อ่านหนังสือ / งานส่วนตัวสั้น", "น้ำเปล่าหรือของว่างเบา ๆ", "รักษา momentum โดยไม่ใช้พลังหมดก่อนเวร", "ใช้รอบสั้น 20-30 นาทีพอ"),
            ("17:00", "ออกกำลังกายเบา", "น้ำเปล่า ก่อนและหลัง", "ช่วยคลายความตึงและเตรียมร่างกายก่อนเวร", "เดิน ยืด หรือเบา ๆ ไม่ต้องหนัก"),
            ("18:30", "อาหารก่อนเวร", "โปรตีน + คาร์บพอดี ลดของมันหนัก", "ลดหิวช่วงดึกและไม่ให้จุกก่อนเข้าเวร", "กินอาหารที่ย่อยง่ายและทำซ้ำได้"),
            ("19:30", "งีบ / ลดสิ่งกระตุ้น", "น้ำเล็กน้อยก่อนพัก", "งีบช่วยปกป้องพลังงานสำหรับเวรดึก", "ปิดแจ้งเตือน ลดแสง และตั้งปลุกชัดเจน"),
            ("21:00", "เตรียมเข้าเวร", "น้ำติดตัว และของจำเป็น", "ลดความเร่งก่อนเริ่มเวร", "เช็กของก่อนออกจากบ้าน 3 อย่าง"),
            ("22:00", "เริ่มเวรดึก", "น้ำเปล่า และของกินเบา ๆ ถ้าจำเป็น", "ช่วงเริ่มเวรต้องคุมพลังงานไม่ให้หมดเร็ว", "เริ่มจากงานสำคัญและอย่าเปิด scope ใหม่"),
            ("02:00", "พักสั้น / น้ำ / ของกินเบา", "น้ำเปล่า หรือของกินเบา ๆ ที่ไม่หวานจัด", "กันพลังตกกลางดึกโดยไม่กระตุ้นเกินไป", "พักจริง 5-10 นาที แล้วกลับงาน"),
            ("06:00", "จบเวร / ลดแสง / กลับบ้าน", "น้ำเปล่า เลี่ยงคาเฟอีนช่วงจบเวร", "ช่วยให้ร่างกายเข้าสู่โหมดพักเร็วขึ้น", "ลดแสง ลดจอ และไม่เปิดงานใหม่"),
            ("07:00", "นอนฟื้นตัว", "เลี่ยงมื้อหนักก่อนนอนหลังเวร", "การนอนหลังเวรคือภารกิจหลักของวันเวรดึก", "ทำห้องให้มืด เย็น เงียบที่สุดเท่าที่ทำได้"),
        ],
        "วันหยุด": [
            ("08:00", "ตื่น / ดื่มน้ำ", "น้ำเปล่า 1 แก้ว", "เริ่มวันหยุดแบบไม่ปล่อยให้ไหลจนเสียทั้งวัน", "ตื่นแล้วทำ 1 อย่างเล็ก ๆ ทันที"),
            ("09:00", "อาหารเช้า", "โปรตีน + คาร์บพอดี + ผักถ้ามี", "ให้พลังงานนิ่งสำหรับงานส่วนตัว", "เลือกเมนูง่ายและซ้ำได้"),
            ("10:00", "อ่านหนังสือ / งานสำคัญส่วนตัว", "น้ำเปล่า วางใกล้มือ", "วันหยุดเหมาะกับงานที่เลื่อนมานาน", "เลือกงานเดียว 45-60 นาที ไม่เปิดหลายเรื่อง"),
            ("12:00", "พักเที่ยง", "ข้าว + โปรตีน + ผัก", "เติมพลังและกันบ่ายหมดแรง", "กินพอดีแล้วเดินเบา ๆ"),
            ("14:00", "ธุระ / จัดบ้าน / เตรียมของ", "น้ำเปล่า", "ลดภาระสะสมในวันทำงาน", "ตั้งเวลา 30-60 นาที แล้วจบเป็นรอบ"),
            ("16:30", "ออกกำลังกาย / เดิน", "น้ำเปล่า ก่อนและหลัง", "ช่วยฟื้นพลังและลดความเครียดสะสม", "เลือกกิจกรรมที่ทำได้จริง ไม่ต้องหนัก"),
            ("18:30", "อาหารเย็น", "โปรตีนเบา + ผัก / ลดหวานมัน", "ช่วยให้คืนนี้นอนง่ายขึ้น", "กินเรียบง่าย ไม่ใช้มื้อเย็นเป็นรางวัลหนักเกิน"),
            ("20:30", "วางแผนเวรถัดไป", "น้ำเล็กน้อย", "เตรียมใจและลดความกังวลก่อนวันทำงาน", "เขียน 3 อย่าง: เวร พลังงาน งานหลัก"),
            ("22:30", "ลดจอ / เตรียมนอน", "เลี่ยงมื้อหนักก่อนนอน", "ทำให้วันถัดไปเริ่มง่าย", "วางมือถือให้ไกลมือ และเตรียมของพรุ่งนี้"),
            ("23:00", "เข้านอน", "พักให้พอ", "รักษาจังหวะนอนแม้เป็นวันหยุด", "จบวันด้วย next single action 1 บรรทัด"),
        ],
    }


def _lpe_phase10h_select_schedule_key(raw_shift):
    value = str(raw_shift or "").strip()
    if value in ["เวรเช้า", "เช้า"]:
        return "เวรเช้า"
    if value in ["เวรบ่าย", "บ่าย"]:
        return "เวรบ่าย"
    if value in ["เวรดึก", "ดึก"]:
        return "เวรดึก"
    if value in ["วันหยุด", "หยุด"]:
        return "วันหยุด"
    return "เวรเช้า"


def _lpe_phase10h_sidebar():
    with st.sidebar:
        st.checkbox("โหมดระบบถูกย้ายไปด้านบน", value=False, key="lpe_phase10h_legacy_escape_disabled", disabled=True, help="Phase 10J repair: ปิด renderer เก่าเพื่อป้องกัน sidebar ซ้ำ")
        legacy = False  # PHASE10J_REPAIR_SIDEBAR_DUPLICATE_NORMAL_MODE_ONLY_V1
        st.markdown("### ผู้ช่วยจัดลำดับชีวิต")
        st.caption("daily-use เหลือ 2 หน้า")
        page = st.radio(
            "เมนูหลัก",
            ["ตารางกิจวัตรประจำวัน", "สรุปวันนี้ / เตรียมพรุ่งนี้"],
            index=0,
            key="lpe_phase10h_page",
        )
    return legacy, page


def _lpe_phase10h_render_hero(done_count, total_count, shift_key, energy):
    st.markdown(
        f"""
        <div class="lpe10h-hero">
          <h1>ตารางกิจวัตรประจำวัน</h1>
          <p>วันนี้ควรทำอะไร เวลาไหน ดูแลร่างกายอย่างไร เพราะอะไร และเทคนิคอะไรช่วยให้ทำสำเร็จ</p>
          <div class="lpe10h-chip-row">
            <span class="lpe10h-chip">เวรวันนี้: {shift_key}</span>
            <span class="lpe10h-chip">พลังงาน: {energy}</span>
            <span class="lpe10h-chip">โหมด: Shift-aware Premium Board</span>
            <span class="lpe10h-chip">ทำแล้ว: {done_count}/{total_count}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _lpe_phase10h_render_metrics(done_count, total_count, shift_key, energy):
    st.markdown(
        f"""
        <div class="lpe10h-metrics">
          <div class="lpe10h-metric"><div class="label">ทำแล้ววันนี้</div><div class="value">{done_count}/{total_count}</div></div>
          <div class="lpe10h-metric"><div class="label">เวรวันนี้</div><div class="value">{shift_key}</div></div>
          <div class="lpe10h-metric"><div class="label">พลังงานตั้งต้น</div><div class="value">{energy}</div></div>
          <div class="lpe10h-metric"><div class="label">เป้าหมาย</div><div class="value">1 งาน</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _lpe_phase10h_render_schedule():
    # PHASE10O_B_TABLE_FIRST_DAILY_TIMETABLE_V1D
    def _rows():
        try:
            data = _lpe10l_build_rows()
        except Exception:
            data = []
        return data if isinstance(data, list) else []

    def _pick(row, *keys, default="-"):
        for key in keys:
            try:
                value = row.get(key)
            except Exception:
                value = None
            if value not in (None, ""):
                return str(value)
        return default

    def _shift_th(code):
        return {
            "M": "เช้า",
            "A": "บ่าย",
            "N": "ดึก",
            "O": "หยุด",
            "V": "ลา",
            "N_A": "ดึก + บ่าย",
        }.get(str(code), str(code or "-"))

    def _mode_th(planning_mode, study_load):
        pm = str(planning_mode or "")
        sl = str(study_load or "")
        if "OFF_STUDY" in pm or "VAC_STUDY" in pm or "DEEP_STUDY" in sl:
            return "วันอ่านหลัก / ชดเชย"
        if "PRE_NIGHT" in pm:
            return "กันแรงก่อนเวรดึก"
        if "CONSECUTIVE_NIGHT" in pm or "SLEEP_FIRST" in sl:
            return "นอนก่อน / งานเบา"
        if "DOUBLE_SHIFT" in pm:
            return "วันเวรหนัก / เอาตัวรอด"
        if "MORNING_DEEP" in sl:
            return "อ่านช่วงเช้า"
        if "MICRO" in sl:
            return "ทวนสั้นรักษา momentum"
        return "แผนยืดหยุ่น"

    def _build_table(row):
        shift = _pick(row, "รหัสเวร", "เวร", "shift", "today_shift")
        pm = _pick(row, "planning_mode")
        sl = _pick(row, "study_load")
        if shift in {"O", "V"} or "OFF_STUDY" in pm or "VAC_STUDY" in pm:
            return [
                {"เวลา": "09:00-11:00", "กิจวัตร": "อ่านหลัก / ชดเชยบทค้าง", "เหตุผล": _mode_th(pm, sl)},
                {"เวลา": "13:00-15:00", "กิจวัตร": "งานชีวิตจำเป็น / ธุระสั้น", "เหตุผล": "ไม่เปิดงานยาวเกินวันหยุด"},
                {"เวลา": "19:00-20:00", "กิจวัตร": "ทบทวน / สรุปโน้ต", "เหตุผล": "ต่อยอดจากช่วงอ่านหลัก"},
                {"เวลา": "21:30", "กิจวัตร": "ปิดวัน + เตรียมพรุ่งนี้", "เหตุผล": "รักษา rolling target"},
            ]
        if shift == "M":
            return [
                {"เวลา": "05:30-07:30", "กิจวัตร": "ตื่น / เตรียมตัว / เดินทาง", "เหตุผล": "กันสายก่อนเวรเช้า"},
                {"เวลา": "08:00-16:00", "กิจวัตร": "เวรเช้า", "เหตุผล": "งานหลักของวัน"},
                {"เวลา": "19:00-20:00", "กิจวัตร": "ทวนเบา / งานจำเป็น 1 อย่าง", "เหตุผล": _mode_th(pm, sl)},
                {"เวลา": "21:30", "กิจวัตร": "ปิดจอ / เตรียมนอน", "เหตุผล": "กันพลังงานตกวันถัดไป"},
            ]
        if shift == "A":
            return [
                {"เวลา": "09:00-11:00", "กิจวัตร": "งานสำคัญ / อ่านตามกำลัง", "เหตุผล": _mode_th(pm, sl)},
                {"เวลา": "13:30-15:30", "กิจวัตร": "เตรียมตัวก่อนเวร", "เหตุผล": "ลด friction ก่อนออกงาน"},
                {"เวลา": "16:00-00:00", "กิจวัตร": "เวรบ่าย", "เหตุผล": "งานหลักของวัน"},
                {"เวลา": "หลังเวร", "กิจวัตร": "พัก / ปิดวันสั้น ๆ", "เหตุผล": "ไม่เปิดงานใหม่ตอนล้า"},
            ]
        if shift == "N_A":
            return [
                {"เวลา": "00:00-08:00", "กิจวัตร": "เวรดึก", "เหตุผล": "ช่วงงานหลักแรก"},
                {"เวลา": "09:00-14:30", "กิจวัตร": "นอน / ฟื้นตัว", "เหตุผล": "double shift ต้องกันนอนก่อน"},
                {"เวลา": "16:00-00:00", "กิจวัตร": "เวรบ่าย", "เหตุผล": "ช่วงงานหลักที่สอง"},
                {"เวลา": "หลังเวร", "กิจวัตร": "พักจริง", "เหตุผล": "ไม่ยัดงานเพิ่ม"},
            ]
        if shift == "N":
            return [
                {"เวลา": "09:00-15:00", "กิจวัตร": "นอน / ฟื้นตัว", "เหตุผล": "หลังเวรดึกต้องคืนพลังงาน"},
                {"เวลา": "16:00-18:00", "กิจวัตร": "งานจำเป็นสั้น ๆ", "เหตุผล": _mode_th(pm, sl)},
                {"เวลา": "21:00-23:00", "กิจวัตร": "เตรียมตัว / นอนนำ", "เหตุผล": "กันแรงก่อนเข้าดึก"},
                {"เวลา": "00:00-08:00", "กิจวัตร": "เวรดึก", "เหตุผล": "งานหลักของวัน"},
            ]
        return [
            {"เวลา": "เริ่มวัน", "กิจวัตร": "เลือกงานสำคัญ 1 อย่าง", "เหตุผล": _mode_th(pm, sl)},
            {"เวลา": "ช่วงหลัก", "กิจวัตร": "ทำตารางตามพลังงานจริง", "เหตุผล": "ไม่ยัดงานเกินจริง"},
            {"เวลา": "ท้ายวัน", "กิจวัตร": "สรุปวันนี้ + เตรียมพรุ่งนี้", "เหตุผล": "ลด friction วันถัดไป"},
        ]

    rows = _rows()
    if not rows:
        st.warning("ยังไม่มีข้อมูลเวร/shift-chain สำหรับสร้างตารางกิจวัตรประจำวัน")
        return
    date_options = [str(r.get("วันที่", "")) for r in rows if isinstance(r, dict) and r.get("วันที่")]
    if not date_options:
        st.warning("ยังไม่มีวันที่ในข้อมูลเวร")
        return
    default_date = "2026-06-26" if "2026-06-26" in date_options else date_options[0]
    selected_date = st.selectbox("เลือกวันที่", date_options, index=date_options.index(default_date), key="lpe10ob_table_first_date")
    row = next((r for r in rows if str(r.get("วันที่", "")) == str(selected_date)), rows[0])

    shift = _pick(row, "รหัสเวร", "เวร", "shift", "today_shift")
    prev_chain = _pick(row, "จากเมื่อวาน", "prev_chain", "chain")
    next_chain = _pick(row, "ไปพรุ่งนี้", "next_chain", "chain")
    planning_mode = _pick(row, "planning_mode")
    study_load = _pick(row, "study_load")
    mode_label = _mode_th(planning_mode, study_load)
    table_rows = _build_table(row)

    completed = 0
    for i in range(len(table_rows)):
        if st.session_state.get(f"lpe10ob_status_{selected_date}_{i}") == "ทำแล้ว":
            completed += 1

    st.markdown("## ตารางกิจวัตรประจำวัน")
    st.markdown(
        f'<div class="lpe10ob-strip">'
        f'<span class="lpe10ob-badge lpe10ob-badge-gray">เวรวันนี้: {_shift_th(shift)}</span>'
        f'<span class="lpe10ob-badge lpe10ob-badge-green">โหมดวันนี้: {mode_label}</span>'
        f'<span class="lpe10ob-badge lpe10ob-badge-blue">ทำแล้ว: {completed}/{len(table_rows)}</span>'
        f'<span class="lpe10ob-badge lpe10ob-badge-gray">chain: {prev_chain} / {next_chain}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    header = st.columns([1.15, 3.0, 2.2, 1.45])
    header[0].markdown("**เวลา**")
    header[1].markdown("**วันนี้เวลานี้ทำอะไร**")
    header[2].markdown("**ทำไมต้องทำช่วงนี้**")
    header[3].markdown("**สถานะ**")

    for i, item in enumerate(table_rows):
        c1, c2, c3, c4 = st.columns([1.15, 3.0, 2.2, 1.45])
        c1.markdown(str(item.get("เวลา", "-")))
        c2.markdown("**" + str(item.get("กิจวัตร", "-")) + "**")
        c3.caption(str(item.get("เหตุผล", "-")))
        status = c4.selectbox(
            "สถานะ",
            ["ยังไม่เริ่ม", "กำลังทำ", "ทำแล้ว", "เลื่อน"],
            key=f"lpe10ob_status_{selected_date}_{i}",
            label_visibility="collapsed",
        )
        if status == "ทำแล้ว":
            c4.success("ทำแล้ว")
        elif status == "กำลังทำ":
            c4.info("กำลังทำ")
        elif status == "เลื่อน":
            c4.warning("เลื่อน")
        else:
            c4.caption("ยังไม่เริ่ม")

    with st.expander("เหตุผลของระบบ / แผนจาก shift-chain", expanded=False):
        st.markdown(
            f'<span class="lpe10ob-badge lpe10ob-badge-gray">planning_mode: {planning_mode}</span>'
            f'<span class="lpe10ob-badge lpe10ob-badge-gray">study_load: {study_load}</span>'
            f'<span class="lpe10ob-badge lpe10ob-badge-gray">shift-chain: {prev_chain} / {next_chain}</span>',
            unsafe_allow_html=True,
        )
        try:
            _lpe10m_render_daily_board_shift_study(selected_date=selected_date, selected_row=row)
        except TypeError:
            _lpe10m_render_daily_board_shift_study()
        except Exception as _engine_detail_error:
            st.caption(f"แสดงเหตุผลของระบบไม่ได้: {_engine_detail_error}")


def _lpe_phase10h_render_summary():
    templates = _lpe_phase10h_schedule_templates()
    shift_key = _lpe_phase10h_select_schedule_key(st.session_state.get("lpe_phase10h_shift_input", st.session_state.get("lpe_phase10h_shift", "เวรเช้า")))
    rows = templates[shift_key]
    done_count = sum(1 for i, _ in enumerate(rows) if st.session_state.get(f"lpe_phase10h_done_{shift_key}_{i}", False))
    total_count = len(rows)
    energy = int(st.session_state.get("lpe_phase10h_energy_input", st.session_state.get("lpe_phase10h_energy", 3)))
    _lpe_phase10h_render_hero(done_count, total_count, shift_key, energy)
    _lpe_phase10h_render_metrics(done_count, total_count, shift_key, energy)
    st.markdown("### สรุปวันนี้")
    a, b = st.columns(2)
    with a:
        st.selectbox("วันนี้โดยรวม", ["ยังไม่สรุป", "ดี", "พอใช้", "เหนื่อย", "หลุดแผน"], key="lpe_phase10h_today_summary")
    with b:
        st.slider("พลังงานท้ายวัน", 1, 5, energy, key="lpe_phase10h_end_energy")
    st.markdown("### เตรียมพรุ่งนี้")
    c, d = st.columns(2)
    with c:
        st.selectbox("พรุ่งนี้เวรอะไร", ["ยังไม่ระบุ", "วันหยุด", "เวรเช้า", "เวรบ่าย", "เวรดึก"], key="lpe_phase10h_tomorrow_shift")
    with d:
        st.text_input("พรุ่งนี้ต้องทำอะไรเป็นอันดับ 1", placeholder="เช่น งานหลัก / พัก / อ่านหนังสือ", key="lpe_phase10h_tomorrow_first")
    st.text_input("Next single action ตอนเปิดเว็บครั้งถัดไป", placeholder="เช่น เปิดเว็บ -> ดูตาราง -> ทำรายการแรก", key="lpe_phase10h_next_action")
    st.text_area("หมายเหตุเสริม", placeholder="สั้น ๆ ก็พอ", key="lpe_phase10h_extra_note")


# PHASE10N_RUNTIME_AUTHORITY_REPAIR_V2B_FIX_DRAFT_STRING_AND_BIND_ACTIVE_RENDERERS
def _lpe10oc_readability_css():
    """PHASE10O_C_READABILITY_CSS_V1C: daily-use readability repair only."""
    st.markdown("""
<style id="PHASE10O_C_READABILITY_CSS_V1C">
/* PHASE10O_C_READABILITY_DASHBOARD_LABELS_V1C */
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] .stTextInput label,
[data-testid="stAppViewContainer"] .stTextArea label,
[data-testid="stAppViewContainer"] .stSelectbox label,
[data-testid="stAppViewContainer"] .stSlider label,
[data-testid="stAppViewContainer"] .stRadio label {
  color: #0f172a !important;
  opacity: 1 !important;
  font-weight: 800 !important;
  letter-spacing: 0.01em !important;
}
[data-testid="stAppViewContainer"] .stMarkdown,
[data-testid="stAppViewContainer"] .stMarkdown p,
[data-testid="stAppViewContainer"] .stCaptionContainer,
[data-testid="stAppViewContainer"] .stCaptionContainer p,
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] p {
  color: #1e293b !important;
  opacity: 1 !important;
}
[data-testid="stAppViewContainer"] input,
[data-testid="stAppViewContainer"] textarea {
  color: #0f172a !important;
  background: #ffffff !important;
  border: 1px solid #94a3b8 !important;
}
[data-testid="stAppViewContainer"] input::placeholder,
[data-testid="stAppViewContainer"] textarea::placeholder {
  color: #475569 !important;
  opacity: 1 !important;
}
[data-testid="stAppViewContainer"] div[data-baseweb="select"] * {
  color: #0f172a !important;
}
[data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] div {
  color: #0f172a !important;
}
[data-testid="stAppViewContainer"] div[role="radiogroup"] label,
[data-testid="stAppViewContainer"] div[role="radiogroup"] span {
  color: #0f172a !important;
  opacity: 1 !important;
  font-weight: 700 !important;
}
[data-testid="stAppViewContainer"] div[data-testid="stSlider"] div,
[data-testid="stAppViewContainer"] div[data-testid="stSlider"] span {
  color: #0f172a !important;
  opacity: 1 !important;
}
[data-testid="stAppViewContainer"] div[data-testid="stExpander"] details summary p,
[data-testid="stAppViewContainer"] div[data-testid="stExpander"] summary {
  color: #0f172a !important;
  font-weight: 800 !important;
}
.lpe10oc-status-label {
  display: inline-block;
  min-width: 92px;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  font-weight: 800;
  font-size: 0.92rem;
  border: 1px solid #cbd5e1;
  background: #f8fafc;
  color: #0f172a;
}
.lpe10oc-status-gray { background: #f1f5f9; color: #334155; }
.lpe10oc-status-blue { background: #dbeafe; color: #1d4ed8; border-color: #93c5fd; }
.lpe10oc-status-green { background: #dcfce7; color: #15803d; border-color: #86efac; }
.lpe10oc-status-yellow { background: #fef3c7; color: #92400e; border-color: #fde68a; }
</style>
""", unsafe_allow_html=True)

def _lpe_phase10h_main():
    _lpe10oc_readability_css()
    # PHASE10O_B_DAILY_USE_PRODUCT_REFRAME_PATCH_TABLE_FIRST_SUMMARY_SIMPLE_SETTINGS_FIVE_MODULES_V1D
    _lpe_phase10h_css()
    st.markdown("""
    <style>
    .lpe10ob-date-only { margin: 0.10rem 0 0.75rem 0; }
    .lpe10ob-subtle { color: #475569; font-size: 0.92rem; }
    .lpe10ob-strip {
        border: 1px solid #dbe4ef;
        background: #f8fafc;
        border-radius: 16px;
        padding: 14px 16px;
        margin: 8px 0 16px 0;
    }
    .lpe10ob-badge {
        display: inline-block;
        border-radius: 999px;
        padding: 0.28rem 0.65rem;
        margin: 0.12rem 0.18rem 0.12rem 0;
        font-weight: 650;
        font-size: 0.90rem;
        line-height: 1.35;
        white-space: normal;
        border: 1px solid #cbd5e1;
        color: #0f172a;
        background: #f1f5f9;
    }
    .lpe10ob-badge-green { background: #dcfce7; border-color: #86efac; color: #14532d; }
    .lpe10ob-badge-blue { background: #dbeafe; border-color: #93c5fd; color: #1e3a8a; }
    .lpe10ob-badge-yellow { background: #fef9c3; border-color: #fde68a; color: #713f12; }
    .lpe10ob-badge-gray { background: #f1f5f9; border-color: #cbd5e1; color: #334155; }
    div[data-testid="stRadio"] label, div[data-testid="stSelectbox"] label { color: #0f172a !important; font-weight: 650 !important; }
    </style>
    """, unsafe_allow_html=True)
    legacy, page = _lpe_phase10h_sidebar()
    if legacy:
        st.info("โหมดเก่าถูกปิดไว้เพื่อให้ daily-use เหลือ 2 หน้า")
    if page == "ตารางกิจวัตรประจำวัน":
        _lpe_phase10h_render_schedule()
    else:
        try:
            _lpe10n_render_end_of_day_tomorrow_refinement()
        except Exception as _lpe10ob_summary_error:
            st.warning(f"เปิดสรุปวันนี้แบบใหม่ไม่ได้ จึงแสดง fallback: {_lpe10ob_summary_error}")
            _lpe_phase10h_render_summary()
    return True


# --- PHASE10K_REPAIR_NAVIGATION_GATE_BEFORE_PHASE10H_STOP_V1 BEGIN ---
# LPE10K_EARLY_MODE_GATE_BEFORE_PHASE10H_STOP_V1
# LPE10K_EARLY_PROFILE_SETUP_DIRECT_ACCESS_V1
# LPE10K_EARLY_ROSTER_REPORT_DIRECT_ACCESS_V1
# This gate must run before Phase10H calls st.stop(). It keeps daily-use simple.
def _lpe10k_gate_normalize_shift(raw_value):
    raw_text = str(raw_value or "").strip()
    star_note = "*" in raw_text
    cleaned = raw_text.replace("*", "").strip()
    if cleaned in {"ด/บ", "N/A", "N_A", "NA"}:
        return {"raw": raw_text, "code": "N_A", "first": "N", "last": "A", "star_note": star_note}
    mapping = {"ช": "M", "บ": "A", "ด": "N", "O": "O", "0": "O", "V": "V", "M": "M", "A": "A", "N": "N"}
    code = mapping.get(cleaned, cleaned or "UNKNOWN")
    return {"raw": raw_text, "code": code, "first": code, "last": code, "star_note": star_note}


def _lpe10k_gate_chain_between(left_last, right_first):
    left = str(left_last or "").strip()
    right = str(right_first or "").strip()
    if not left or not right or left == "UNKNOWN" or right == "UNKNOWN":
        return ""
    pairs = {
        ("M", "N"): "M_TO_N",
        ("A", "M"): "A_TO_M",
        ("N", "A"): "N_TO_A",
        ("N", "N"): "N_TO_N",
        ("N", "O"): "N_TO_O",
        ("O", "A"): "O_TO_A",
        ("O", "M"): "O_TO_M",
        ("O", "N"): "O_TO_N",
        ("V", "A"): "V_TO_A",
        ("V", "M"): "V_TO_M",
        ("V", "N"): "V_TO_N",
    }
    return pairs.get((left, right), f"{left}_TO_{right}")


def _lpe10k_gate_planning_mode(today_code, prev_chain, next_chain):
    code = str(today_code or "")
    prev_value = str(prev_chain or "")
    next_value = str(next_chain or "")
    if code == "N_A":
        return "DOUBLE_SHIFT_SURVIVAL_DAY"
    if prev_value == "A_TO_M" and next_value == "M_TO_N":
        return "HIGH_SLEEP_RISK_DAY"
    if next_value == "M_TO_N":
        return "PRE_NIGHT_PROTECTION_DAY"
    if prev_value == "A_TO_M":
        return "AFTERNOON_TO_MORNING_SLEEP_RISK_DAY"
    if prev_value == "N_TO_A":
        return "NIGHT_TO_AFTERNOON_SURVIVAL_DAY"
    if prev_value == "N_TO_O":
        return "POST_NIGHT_RECOVERY_DAY"
    if code == "O":
        return "OFF_STUDY_DAY"
    if code == "V":
        return "VAC_STUDY_DAY"
    if code == "M":
        return "NORMAL_MORNING_DAY"
    if code == "A":
        return "NORMAL_AFTERNOON_DAY"
    if code == "N":
        return "NORMAL_NIGHT_DAY"
    return "NORMAL_DAY"


def _lpe10k_gate_june_roster():
    return {
        "2026-06-01": "ช",
        "2026-06-02": "ด/บ",
        "2026-06-03": "ช",
        "2026-06-04": "ด*",
        "2026-06-05": "ด*",
        "2026-06-06": "O",
        "2026-06-07": "ช",
        "2026-06-08": "ด",
        "2026-06-09": "ด*",
        "2026-06-10": "O",
        "2026-06-11": "บ",
        "2026-06-12": "ช",
        "2026-06-13": "ด",
        "2026-06-14": "ช",
        "2026-06-15": "ด",
        "2026-06-16": "O",
        "2026-06-17": "O",
        "2026-06-18": "V",
        "2026-06-19": "V",
        "2026-06-20": "ช*",
        "2026-06-21": "ด",
        "2026-06-22": "ช*",
        "2026-06-23": "ด",
        "2026-06-24": "ด",
        "2026-06-25": "บ",
        "2026-06-26": "O",
        "2026-06-27": "บ",
        "2026-06-28": "ช",
        "2026-06-29": "ด",
        "2026-06-30": "ด",
    }


def _lpe10k_gate_build_report_rows():
    roster = _lpe10k_gate_june_roster()
    dates = sorted(roster.keys())
    rows = []
    normalized = {date_value: _lpe10k_gate_normalize_shift(raw_value) for date_value, raw_value in roster.items()}
    for index, date_value in enumerate(dates):
        today = normalized[date_value]
        previous = normalized.get(dates[index - 1]) if index > 0 else None
        tomorrow = normalized.get(dates[index + 1]) if index + 1 < len(dates) else None
        prev_chain = _lpe10k_gate_chain_between(previous.get("last"), today.get("first")) if previous else ""
        next_chain = _lpe10k_gate_chain_between(today.get("last"), tomorrow.get("first")) if tomorrow else ""
        rows.append({
            "วันที่": date_value,
            "เวรดิบ": today.get("raw"),
            "รหัสเวร": today.get("code"),
            "จากเมื่อวาน": prev_chain or "-",
            "ไปพรุ่งนี้": next_chain or "-",
            "planning_mode": _lpe10k_gate_planning_mode(today.get("code"), prev_chain, next_chain),
            "star_note": "yes" if today.get("star_note") else "no",
        })
    return rows


def _lpe10k_gate_render_profile_setup():
    # PHASE10O_C_GUIDED_QUESTIONS_EXPANSION_PATCH_V1C
    st.markdown("# ⚙️ ตั้งค่าชีวิตละเอียด")
    st.caption("โฟกัสหลักคือ 5 หมวดชีวิต + คำถามนำทาง เพื่อให้ตารางวันนี้ตรงกับชีวิตจริง")

    memory_text = "\n".join([
        "เวรเช้า 08:00-16:00",
        "เวรบ่าย 16:00-00:00",
        "เวรดึก 00:00-08:00",
        "เตรียมตัว 90 นาที",
        "เดินทาง 15 นาที",
        "มี ช→ด / บ→ช / ด/บ และวันฟื้นตัวสำคัญ",
        "เป้าหมายคือจัดตารางวันนี้ให้ไม่ฝืนพลังงานจริง",
    ])
    with st.expander("ข้อมูลที่ระบบจำไว้แล้ว", expanded=False):
        st.info(memory_text)

    setup_mode = st.radio(
        "รูปแบบการกรอก",
        ["สัมภาษณ์ละเอียด 5 หมวด", "ข้อมูลเดิม / แก้ไขต่อ", "Quick setup"],
        horizontal=True,
        key="lpe10oc_setup_style_v1c",
    )

    modules = [
        {
            "title": "1. เป้าหมายและปัญหาที่อยากแก้",
            "key": "goal_problem",
            "core": [
                "ตอนนี้เป้าหมายหลักที่สุดที่อยากให้ชีวิตดีขึ้นคืออะไร",
                "ปัญหาที่ทำให้แผนพังบ่อยที่สุดคืออะไร",
                "อะไรคือผลลัพธ์ที่อยากเห็นภายใน 7 วัน",
                "ถ้าวันนี้เหนื่อยมาก minimum success คืออะไร",
                "สิ่งไหนห้ามพลาดเด็ดขาดในช่วงนี้",
                "อะไรควรถูกลดหรือเลื่อนเมื่อเวลาน้อย",
            ],
            "deep": [
                "งาน/การอ่านแบบไหนทำแล้วรู้สึกคุ้มค่าที่สุด",
                "อะไรคือสิ่งที่ทำแล้วเสียเวลาแต่ไม่ช่วยเป้าหมาย",
                "เมื่อแผนพัง ระบบควรช่วยเริ่มใหม่แบบไหน",
                "เป้าหมายนี้ควรแบ่งเป็นกี่ช่วงต่อวันจึงไม่หนักเกินไป",
            ],
            "use": [
                "เลือกลำดับงานสำคัญในตารางวันนี้",
                "ตั้ง minimum action ในวันที่พลังงานต่ำ",
                "ตัดงานที่ไม่จำเป็นออกเมื่อเจอเวรหนักหรือเวลาน้อย",
            ],
        },
        {
            "title": "2. เวลาและจังหวะชีวิต",
            "key": "time_rhythm",
            "core": [
                "ช่วงเวลาไหนสมองดีที่สุด",
                "ช่วงเวลาไหนพลังตกง่ายที่สุด",
                "ก่อนเวรต้องเตรียมตัวกี่นาทีจึงไม่รีบเกินไป",
                "หลังเวรต้องพักขั้นต่ำเท่าไร",
                "วันหยุดควรใช้เป็นวันอ่านหลักหรือวันฟื้นตัว",
                "ถ้ามีเวรต่อเนื่อง ระบบควรลดงานแบบไหน",
                "ช่วงไหนไม่ควรใส่งานยาวเด็ดขาด",
            ],
            "deep": [
                "เวลาเดินทางจริงโดยเฉลี่ยเท่าไร และมี buffer แค่ไหน",
                "ถ้าต้องอ่านหนังสือ ควรอ่านช่วงไหนถึงจำได้ดีที่สุด",
                "ช่วงก่อนนอนควรปิดงานแบบไหนเพื่อไม่ให้วันถัดไปพัง",
                "วันเวรเช้า/บ่าย/ดึกควรมีโครงวันต่างกันอย่างไร",
            ],
            "use": [
                "จัดเวลาอ่าน งาน พัก และเตรียมตัวให้ตรงพลังงานจริง",
                "กันเวลานอนใน chain เสี่ยง เช่น ช→ด หรือ บ→ช",
                "กำหนดช่วง deep work เฉพาะวันที่เหมาะจริง",
            ],
        },
        {
            "title": "3. สุขภาพและพลังงาน",
            "key": "health_energy",
            "core": [
                "สัญญาณว่าเริ่มฝืนเกินไปคืออะไร",
                "อะไรทำให้พลังงานฟื้นเร็วที่สุด",
                "อะไรทำให้เสียพลังโดยไม่จำเป็น",
                "วันที่นอนน้อยควรเหลือแผนขั้นต่ำอะไร",
                "อาหาร/น้ำ/พักแบบไหนที่ช่วยให้วันไม่พัง",
                "สิ่งที่ระบบควรเตือนแบบไม่กดดันคืออะไร",
            ],
            "deep": [
                "ถ้ามีพลังงาน 1/5 ระบบควรให้ทำอะไรเท่านั้น",
                "ถ้ามีพลังงาน 3/5 ควรทำงานระดับไหน",
                "ถ้ามีพลังงาน 5/5 ควรใช้โอกาสกับงานอะไร",
                "อะไรคือกิจกรรมพักที่ช่วยจริง ไม่ใช่พักแล้วเหนื่อยกว่าเดิม",
            ],
            "use": [
                "ปรับตารางตามพลังงานจริง ไม่ใช่ยัดงานทุกวันเท่ากัน",
                "เลือก micro-review ในวันเสี่ยงนอนน้อย",
                "เตือนให้พักก่อนเกิด sleep debt สะสม",
            ],
        },
        {
            "title": "4. งาน / เงิน / ภาระที่ห้ามพลาด",
            "key": "work_money_obligations",
            "core": [
                "งานประจำที่ต้องกันเวลาเสมอคืออะไร",
                "งานไหนเลื่อนได้ งานไหนเลื่อนไม่ได้",
                "ภาระการเงินหรือธุระไหนต้องเตือนล่วงหน้า",
                "งานบ้าน/ชีวิตอะไรที่มักสะสมจนกลายเป็นปัญหา",
                "ถ้ามีเวลา 30 นาที ควรทำงานประเภทไหนก่อน",
                "สิ่งไหนไม่ควรถูกแทรกในวันเวรหนัก",
            ],
            "deep": [
                "งานที่ต้องใช้สมาธิสูงควรอยู่ช่วงไหนของวัน",
                "งานสั้นที่ใช้ปิดช่องว่างระหว่างวันคืออะไร",
                "งานไหนถ้าไม่ทำวันนี้จะกระทบพรุ่งนี้ทันที",
                "มี deadline รายสัปดาห์หรือรายเดือนอะไรที่ระบบควรจำ",
            ],
            "use": [
                "กันเวลางานห้ามพลาดก่อนงานรอง",
                "แทรกงานสั้นในช่องว่างโดยไม่ทำให้ตารางหลักพัง",
                "เตือนงานสำคัญก่อนกลายเป็นงานด่วน",
            ],
        },
        {
            "title": "5. เรื่องราวชีวิตและกฎส่วนตัว",
            "key": "life_story_rules",
            "core": [
                "กฎส่วนตัวที่อยากให้ระบบเคารพคืออะไร",
                "สิ่งที่ทำให้รู้สึกว่าชีวิตกำลังดีขึ้นคืออะไร",
                "วิธีเตือนแบบไหนที่รับได้",
                "วิธีเตือนแบบไหนที่ไม่ชอบ",
                "ถ้าแผนพัง ระบบควรช่วย restart อย่างไร",
                "pattern ที่เกิดซ้ำและควรให้ระบบจำไว้คืออะไร",
            ],
            "deep": [
                "อะไรคือสิ่งที่คุณอยากปกป้องในชีวิตประจำวัน",
                "อะไรคือสิ่งที่ทำให้หมดแรงทางใจบ่อยที่สุด",
                "ระบบควรพูดกับคุณแบบเข้มงวดหรืออ่อนโยนแค่ไหน",
                "ขอบเขตไหนที่ระบบไม่ควรแนะนำเกินไป",
            ],
            "use": [
                "ทำให้คำแนะนำไม่ฝืนบุคลิกและกฎส่วนตัว",
                "เลือกน้ำเสียงและระดับความกดดันให้เหมาะ",
                "ช่วยรีสตาร์ทแผนโดยไม่ทำให้รู้สึกล้มเหลว",
            ],
        },
    ]

    if setup_mode == "Quick setup":
        st.markdown("## Quick setup")
        st.text_input("ชื่อที่ให้ระบบเรียก", value="ประสบชัย", key="lpe10oc_quick_name_v1c")
        st.text_area("เป้าหมายหลัก / งานด่วน / พรุ่งนี้ต้องระวัง", key="lpe10oc_quick_goal_v1c", height=140)
        return

    if setup_mode == "ข้อมูลเดิม / แก้ไขต่อ":
        st.markdown("## ข้อมูลเดิม / แก้ไขต่อ")
        st.text_area("อะไรเปลี่ยนจากข้อมูลเดิม", key="lpe10oc_known_update_v1c", height=160, placeholder="ข้อมูลไหนเปลี่ยนแล้ว หรือมีอะไรที่ระบบยังไม่รู้")
        return

    _lpe11a_profile_persistence_bootstrap_module_keys(modules)
    # BEGIN LPE_PHASE11A_PROFILE_PERSISTENCE_PATCH_V2_PER_MODULE_KEYS_RENDER
    _lpe11a_profile_v2_sync_legacy_keys(modules)
    labels = [m["title"] for m in modules] + ["ตรวจความครบ"]
    selected = st.selectbox("เลือกหมวด", labels, key="lpe11a_profile_selected_module_v2")

    if selected == "ตรวจความครบ":
        st.markdown("## ตรวจความครบของ 5 หมวด")
        _lpe11a_profile_v2_sync_legacy_keys(modules)
        completed_count = 0
        for m in modules:
            title = str(m.get("title", ""))
            module_key = str(m.get("key", ""))
            value = _lpe11a_profile_v2_module_answer(module_key, title).strip()
            if value:
                completed_count += 1
                st.success("กรอกแล้ว: " + title)
            else:
                st.warning("ยังไม่ครบ: " + title)
        st.markdown("### ความครบของตั้งค่าชีวิต")
        st.markdown(f"## {completed_count}/5 หมวด")
        st.caption("ข้อมูลครบไม่ใช่แปลว่าต้องยาว แต่ควรพอให้ระบบจัดตารางจริงโดยไม่เดา")
    else:
        selected_module = next((m for m in modules if m.get("title") == selected), modules[0])
        module_key = str(selected_module.get("key", ""))
        module_title = str(selected_module.get("title", selected))
        widget_key = _lpe11a_profile_v2_seed_widget(module_key, module_title)

        st.markdown("## " + module_title)
        st.markdown("### คำถามนำทางหลัก")
        for q in selected_module.get("questions", []):
            st.markdown("- " + str(q))

        deep_questions = selected_module.get("deep_questions", []) or selected_module.get("deep", []) or []
        if deep_questions:
            with st.expander("คำถามเจาะลึก ถ้าต้องการให้ระบบแม่นขึ้น"):
                for q in deep_questions:
                    st.markdown("- " + str(q))

        answer = st.text_area(
            "คำตอบของคุณ",
            key=widget_key,
            height=170,
            placeholder="ตอบเป็นภาษาคนธรรมดาได้เลย เช่น สิ่งที่อยากแก้ เวลาที่พังบ่อย ข้อจำกัดจริง และสิ่งที่ไม่อยากให้ระบบเดา",
        )
        _lpe11a_profile_v2_save_answer(module_key, module_title, answer)
        st.session_state["lpe10oc_answer_" + module_key] = str(answer or "")
        if str(answer or "").strip():
            st.success("บันทึกอัตโนมัติแล้วสำหรับหมวดนี้")
        elif _lpe11a_profile_v2_module_answer(module_key, module_title).strip():
            st.info("มีข้อมูลที่บันทึกไว้แล้ว แต่ยังไม่ถูกแสดงในช่องนี้ ให้ refresh หน้านี้หนึ่งครั้ง")
    # END LPE_PHASE11A_PROFILE_PERSISTENCE_PATCH_V2_PER_MODULE_KEYS_RENDER
    # PHASE11A_PROFILE_INPUT_PERSISTENCE_PATCH_V2D_LINE_REPAIR_ONLY_MODULE_USE_LOCAL_ONLY_NO_STAGE_NO_COMMIT_NO_PUSH
    if selected != "ตรวจความครบ":
        st.markdown("### ระบบเข้าใจเบื้องต้น / ใช้ข้อมูลนี้เพื่อ")
        for item in selected_module.get("use", []):
            st.markdown("- " + str(item))


def _lpe10k_gate_render_roster_report():
    st.markdown("## 🧭 ตรวจตารางเวร/shift-chain มิ.ย.69")
    st.caption("ตรวจ manual roster map และ chain ก่อนนำไปผูกกับตารางอ่านและ daily board")
    rows = _lpe10k_gate_build_report_rows()
    try:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    except Exception:
        st.table(rows)
    lookup = {row["วันที่"]: row for row in rows}
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("2026-06-01", lookup.get("2026-06-01", {}).get("ไปพรุ่งนี้", "missing"))
    with c2:
        st.metric("2026-06-02", lookup.get("2026-06-02", {}).get("รหัสเวร", "missing"))
    with c3:
        st.metric("2026-06-03", lookup.get("2026-06-03", {}).get("จากเมื่อวาน", "missing"))
    st.info("ค่าที่ต้องตรวจ: 2026-06-01 ไปพรุ่งนี้=M_TO_N, 2026-06-02 รหัสเวร=N_A, 2026-06-03 จากเมื่อวาน=A_TO_M")


def _lpe10k_gate_before_phase10h_stop():
    st.markdown("### โหมดระบบ")
    mode = st.radio(
        "เลือกโหมด",
        ["ใช้งานประจำวัน", "ตั้งค่าชีวิตละเอียด", "ตรวจตารางเวร/shift-chain"],
        horizontal=True,
        key="lpe10k_gate_before_phase10h_stop_mode",
    )
    if mode == "ตั้งค่าชีวิตละเอียด":
        _lpe10k_gate_render_profile_setup()
        return True
    if mode == "ตรวจตารางเวร/shift-chain":
        _lpe10k_gate_render_roster_report()
        return True
    return False


try:
    if _lpe10k_gate_before_phase10h_stop():
        st.stop()
except Exception as _lpe10k_gate_error:
    st.error("Phase10K navigation gate error")
    st.exception(_lpe10k_gate_error)
    st.stop()
# --- PHASE10K_REPAIR_NAVIGATION_GATE_BEFORE_PHASE10H_STOP_V1 END ---



# --- PHASE10L_STUDY_PLAN_ALIGNMENT_WITH_SHIFT_CHAIN_PATCH_V1 BEGIN ---
# LPE10L_STUDY_PLAN_ALIGNMENT_WITH_SHIFT_CHAIN
# LPE10L_STUDY_LOAD_BY_PLANNING_MODE
# LPE10L_ROLLING_STUDY_TARGET
# LPE10L_STUDY_CHAIN_ALIGNMENT_REPORT
# LPE10L_LOCAL_ONLY_MANUAL_STUDY_INPUT
try:
    import datetime as _lpe10l_datetime
    import streamlit as _lpe10l_st
except Exception:
    _lpe10l_datetime = None
    _lpe10l_st = None

PHASE10L_STUDY_PLAN_ALIGNMENT_WITH_SHIFT_CHAIN_PATCH_V1 = True

_LPE10L_JUNE_ROSTER_RAW = {
    "2026-06-01": "ช",
    "2026-06-02": "ด/บ",
    "2026-06-03": "ช",
    "2026-06-04": "ด*",
    "2026-06-05": "ด*",
    "2026-06-06": "O",
    "2026-06-07": "ช",
    "2026-06-08": "ด",
    "2026-06-09": "ด*",
    "2026-06-10": "O",
    "2026-06-11": "บ",
    "2026-06-12": "ช",
    "2026-06-13": "ด",
    "2026-06-14": "ช",
    "2026-06-15": "ด",
    "2026-06-16": "O",
    "2026-06-17": "O",
    "2026-06-18": "V",
    "2026-06-19": "V",
    "2026-06-20": "ช*",
    "2026-06-21": "ด",
    "2026-06-22": "ช*",
    "2026-06-23": "ด",
    "2026-06-24": "ด",
    "2026-06-25": "บ",
    "2026-06-26": "O",
    "2026-06-27": "บ",
    "2026-06-28": "ช",
    "2026-06-29": "ด",
    "2026-06-30": "ด",
}

_LPE10L_SHIFT_WINDOWS = {
    "M": "08:00-16:00",
    "A": "16:00-00:00",
    "N": "00:00-08:00",
    "N_A": "00:00-08:00 + 16:00-00:00",
    "O": "หยุด",
    "V": "ลา",
}

_LPE10L_STUDY_LOAD_RULES = {
    "DOUBLE_SHIFT_SURVIVAL_DAY": ("MICRO_REVIEW_ONLY", "ทวน 5-15 นาที ถ้าไหว / ไม่เปิดบทใหม่"),
    "HIGH_SLEEP_RISK_DAY": ("MICRO_OR_LIGHT", "อ่านเบา 10-20 นาที และล็อกเวลานอน"),
    "PRE_NIGHT_PROTECTION_DAY": ("LIGHT_REVIEW_BEFORE_SLEEP", "ทวนสั้นก่อนนอนเตรียมดึก"),
    "AFTERNOON_TO_MORNING_SLEEP_RISK_DAY": ("LIGHT_REVIEW_ONLY", "เลี่ยงอ่านยาวหลังเลิกบ่าย"),
    "CONSECUTIVE_NIGHT_SHIFT_DAY": ("SLEEP_FIRST_MICRO_REVIEW", "นอนกลางวันก่อน แล้วค่อยทวนสั้น"),
    "POST_NIGHT_RECOVERY_DAY": ("RECOVERY_LIGHT_REVIEW", "พักก่อน แล้วอ่านเบา/ชดเชยเล็กน้อย"),
    "VAC_STUDY_DAY": ("DEEP_STUDY_OR_CATCHUP", "ใช้เป็นวันอ่านหลักหรือชดเชยบทค้าง"),
    "OFF_STUDY_DAY": ("DEEP_STUDY_OR_CATCHUP", "ใช้เป็นวันอ่านหลักหรือชดเชยบทค้าง"),
    "NORMAL_AFTERNOON_DAY": ("MORNING_DEEP_STUDY", "ใช้ช่วงเช้าอ่านหลักก่อนเวรบ่าย"),
    "NORMAL_MORNING_DAY": ("SHORT_EVENING_REVIEW", "หลังเวรเช้าให้ทวนสั้นหรืออ่านเบา"),
    "NORMAL_NIGHT_DAY": ("LIGHT_PRE_SHIFT_REVIEW", "ก่อนเวรดึกให้เบาและกันเวลาพัก"),
}


def _lpe10l_normalize_shift(raw_value):
    raw_text = str(raw_value or "").strip()
    star_note = "*" in raw_text
    cleaned = raw_text.replace("*", "").strip()
    if cleaned in {"ด/บ", "N/A", "N_A", "NA"}:
        return {"raw": raw_text, "code": "N_A", "first": "N", "last": "A", "star_note": star_note}
    mapping = {"ช": "M", "บ": "A", "ด": "N", "O": "O", "0": "O", "V": "V", "M": "M", "A": "A", "N": "N"}
    code = mapping.get(cleaned, cleaned or "UNKNOWN")
    return {"raw": raw_text, "code": code, "first": code, "last": code, "star_note": star_note}


def _lpe10l_chain(left, right):
    if not left or not right:
        return "-"
    if left in {"UNKNOWN", "-"} or right in {"UNKNOWN", "-"}:
        return "-"
    return f"{left}_TO_{right}"


def _lpe10l_planning_mode(code, prev_chain, next_chain):
    if code == "N_A":
        return "DOUBLE_SHIFT_SURVIVAL_DAY"
    if prev_chain == "A_TO_M" and next_chain == "M_TO_N":
        return "HIGH_SLEEP_RISK_DAY"
    if prev_chain == "N_TO_N" or next_chain == "N_TO_N":
        return "CONSECUTIVE_NIGHT_SHIFT_DAY"
    if next_chain == "M_TO_N":
        return "PRE_NIGHT_PROTECTION_DAY"
    if prev_chain == "A_TO_M":
        return "AFTERNOON_TO_MORNING_SLEEP_RISK_DAY"
    if prev_chain == "N_TO_O":
        return "POST_NIGHT_RECOVERY_DAY"
    if code == "O":
        return "OFF_STUDY_DAY"
    if code == "V":
        return "VAC_STUDY_DAY"
    if code == "M":
        return "NORMAL_MORNING_DAY"
    if code == "A":
        return "NORMAL_AFTERNOON_DAY"
    if code == "N":
        return "NORMAL_NIGHT_DAY"
    return "NORMAL_DAY"


def _lpe10l_build_rows():
    dates = sorted(_LPE10L_JUNE_ROSTER_RAW)
    rows = []
    normalized = {d: _lpe10l_normalize_shift(_LPE10L_JUNE_ROSTER_RAW[d]) for d in dates}
    for idx, date_text in enumerate(dates):
        today = normalized[date_text]
        prev = normalized[dates[idx - 1]] if idx > 0 else None
        nxt = normalized[dates[idx + 1]] if idx + 1 < len(dates) else None
        prev_chain = _lpe10l_chain(prev["last"], today["first"]) if prev else "-"
        next_chain = _lpe10l_chain(today["last"], nxt["first"]) if nxt else "-"
        planning_mode = _lpe10l_planning_mode(today["code"], prev_chain, next_chain)
        study_load, study_action = _LPE10L_STUDY_LOAD_RULES.get(planning_mode, ("NORMAL_REVIEW", "อ่านตามพลังงานจริง"))
        rows.append({
            "วันที่": date_text,
            "เวรดิบ": today["raw"],
            "รหัสเวร": today["code"],
            "จากเมื่อวาน": prev_chain,
            "ไปพรุ่งนี้": next_chain,
            "planning_mode": planning_mode,
            "study_load": study_load,
            "แนะนำการอ่าน": study_action,
            "star_note": "yes" if today["star_note"] else "no",
        })
    return rows


def _lpe10l_render_study_plan_alignment():
    st = _lpe10l_st
    if st is None:
        return
    st.markdown("---")
    st.subheader("📚 ตารางอ่าน/สอบ × shift-chain")
    st.caption("Phase10L: ใช้ planning_mode จากตารางเวรเพื่อกำหนดความหนักของการอ่านแบบ rolling target")

    with st.expander("ตั้งค่าตารางอ่านช่วง 19 มิ.ย.–19 ก.ค. / เป้าหมายสอบ", expanded=True):
        st.text_area(
            "แผนอ่านหลัก / หน่วยที่ต้องจบ",
            value="19 มิ.ย.–19 ก.ค. อ่านตามหน่วยที่กำหนด\nวันเวรหนักให้ทวนสั้น วันหยุดหรือวันลาใช้ชดเชยบทค้าง",
            key="lpe10l_study_plan_source_text",
            height=90,
        )
        col_a, col_b = st.columns(2)
        with col_a:
            st.text_input("minimum success วันที่เหนื่อย", value="ทวน 5-15 นาที หรืออ่าน 1 หัวข้อย่อย", key="lpe10l_minimum_success")
        with col_b:
            st.text_input("สิ่งที่ต้องเลี่ยง", value="ไม่เปิดโปรเจกต์ยาวในวันควงเวรหรือวันต้องนอน", key="lpe10l_study_avoid")

    rows = _lpe10l_build_rows()
    study_window_rows = [row for row in rows if row["วันที่"] >= "2026-06-19"]
    deep_count = sum(1 for row in study_window_rows if row["study_load"] in {"DEEP_STUDY_OR_CATCHUP", "MORNING_DEEP_STUDY"})
    micro_count = sum(1 for row in study_window_rows if "MICRO" in row["study_load"])
    risk_count = sum(1 for row in study_window_rows if row["planning_mode"] in {"DOUBLE_SHIFT_SURVIVAL_DAY", "HIGH_SLEEP_RISK_DAY", "CONSECUTIVE_NIGHT_SHIFT_DAY", "PRE_NIGHT_PROTECTION_DAY"})

    c1, c2, c3 = st.columns(3)
    c1.metric("วันอ่านหลัก/ชดเชย", deep_count)
    c2.metric("วัน micro/review", micro_count)
    c3.metric("วันต้องกันนอน", risk_count)

    st.markdown("### แผนอ่านตามเวร 19–30 มิ.ย.69")
    st.dataframe(study_window_rows, use_container_width=True, hide_index=True)

    critical = [row for row in study_window_rows if row["planning_mode"] in {"DOUBLE_SHIFT_SURVIVAL_DAY", "HIGH_SLEEP_RISK_DAY", "CONSECUTIVE_NIGHT_SHIFT_DAY", "PRE_NIGHT_PROTECTION_DAY"}]
    if critical:
        st.warning("วันที่ต้องระวัง: " + ", ".join([f"{row['วันที่']}={row['planning_mode']}" for row in critical[:12]]))
    st.success("หลัก Phase10L: ตารางอ่านเป็น rolling target — วันเวรหนักลดเป็นทวนสั้น แล้วชดเชยในวันหยุด/วันบ่ายเช้าโล่ง")
# --- PHASE10L_STUDY_PLAN_ALIGNMENT_WITH_SHIFT_CHAIN_PATCH_V1 END ---

# PHASE10K_RESTORE_DEEP_GUIDED_PROFILE_QUESTIONNAIRE_IN_NEW_MODE_V1
# LPE10K_DEEP_GUIDED_PROFILE_RESTORE_V1
# LPE10K_DEEP_QUESTIONNAIRE_IN_NEW_MODE_V1
# LPE10K_PROFILE_MEMORY_PREFILL_AND_REVIEW_V1
# LPE10K_ROSTER_REPORT_KEEP_V1
try:
    import streamlit as _lpe10k_deep_st
except Exception:
    _lpe10k_deep_st = None

if _lpe10k_deep_st is not None:
    def _lpe10k_deep_normalize_shift(raw_value):
        raw_text = str(raw_value or "").strip()
        star_note = "*" in raw_text
        cleaned = raw_text.replace("*", "").strip()
        if cleaned in {"ด/บ", "N/A", "N_A", "NA"}:
            return {"raw": raw_text, "code": "N_A", "first": "N", "last": "A", "star_note": star_note}
        mapping = {"ช": "M", "บ": "A", "ด": "N", "O": "O", "0": "O", "V": "V", "M": "M", "A": "A", "N": "N"}
        code = mapping.get(cleaned, cleaned or "UNKNOWN")
        return {"raw": raw_text, "code": code, "first": code, "last": code, "star_note": star_note}

    def _lpe10k_deep_june_roster():
        return {
            "2026-06-01": "ช", "2026-06-02": "ด/บ", "2026-06-03": "ช", "2026-06-04": "ด*", "2026-06-05": "ด*",
            "2026-06-06": "O", "2026-06-07": "ช", "2026-06-08": "ด", "2026-06-09": "ด*", "2026-06-10": "O",
            "2026-06-11": "บ", "2026-06-12": "ช", "2026-06-13": "ด", "2026-06-14": "ช", "2026-06-15": "ด",
            "2026-06-16": "O", "2026-06-17": "O", "2026-06-18": "V", "2026-06-19": "V", "2026-06-20": "ช*",
            "2026-06-21": "ด", "2026-06-22": "ช*", "2026-06-23": "ด", "2026-06-24": "ด", "2026-06-25": "บ",
            "2026-06-26": "O", "2026-06-27": "บ", "2026-06-28": "ช", "2026-06-29": "ด", "2026-06-30": "ด",
        }

    def _lpe10k_deep_chain(left, right):
        if not left or not right or left == "UNKNOWN" or right == "UNKNOWN":
            return "-"
        if left == "N_A":
            left = "A"
        if right == "N_A":
            right = "N"
        return f"{left}_TO_{right}"

    def _lpe10k_deep_planning_mode(today_code, prev_chain, next_chain):
        if today_code == "N_A":
            return "DOUBLE_SHIFT_SURVIVAL_DAY"
        if prev_chain == "A_TO_M" and next_chain == "M_TO_N":
            return "HIGH_SLEEP_RISK_DAY"
        if prev_chain == "N_TO_N" or next_chain == "N_TO_N":
            return "CONSECUTIVE_NIGHT_SHIFT_DAY"
        if next_chain == "M_TO_N":
            return "PRE_NIGHT_PROTECTION_DAY"
        if prev_chain == "A_TO_M":
            return "AFTERNOON_TO_MORNING_SLEEP_RISK_DAY"
        if prev_chain in {"N_TO_O", "N_TO_V"}:
            return "POST_NIGHT_RECOVERY_DAY"
        if today_code == "M":
            return "NORMAL_MORNING_DAY"
        if today_code == "A":
            return "NORMAL_AFTERNOON_DAY"
        if today_code == "N":
            return "NORMAL_NIGHT_DAY"
        if today_code == "V":
            return "VAC_STUDY_DAY"
        if today_code == "O":
            return "OFF_STUDY_DAY"
        return "NORMAL_DAY"

    def _lpe10k_deep_rows():
        roster = _lpe10k_deep_june_roster()
        dates = sorted(roster.keys())
        parsed = {d: _lpe10k_deep_normalize_shift(roster[d]) for d in dates}
        rows = []
        for idx, date in enumerate(dates):
            prev_date = dates[idx - 1] if idx > 0 else None
            next_date = dates[idx + 1] if idx + 1 < len(dates) else None
            today = parsed[date]
            prev_chain = _lpe10k_deep_chain(parsed[prev_date]["last"], today["first"]) if prev_date else "-"
            next_chain = _lpe10k_deep_chain(today["last"], parsed[next_date]["first"]) if next_date else "-"
            rows.append({
                "วันที่": date,
                "เวรดิบ": today["raw"],
                "รหัสเวร": today["code"],
                "จากเมื่อวาน": prev_chain,
                "ไปพรุ่งนี้": next_chain,
                "planning_mode": _lpe10k_deep_planning_mode(today["code"], prev_chain, next_chain),
                "star_note": "yes" if today["star_note"] else "no",
            })
        return rows

    def _lpe10k_deep_memory_preview():
        _lpe10k_deep_st.info(
            "ข้อมูลที่ระบบรู้อยู่แล้ว: เวรเช้า 08:00-16:00, เวรบ่าย 16:00-00:00, เวรดึก 00:00-08:00, "
            "เตรียมตัว 90 นาที, เดินทาง 15 นาที, มีรูปแบบ ช→ด / บ→ช / ด/บ, "
            "ช่วงนี้การอ่านสอบสำคัญ, โปรเจกต์ห้ามกินเวลาอ่านและนอน, และกฎหลักคือพูดตรง ไม่เปิด scope ใหม่"
        )

    def _lpe10k_deep_keywords(text_value):
        value = str(text_value or "").strip()
        if not value:
            return []
        candidates = ["สอบ", "อ่าน", "เวร", "นอน", "งาน", "โปรเจกต์", "ออกกำลัง", "อาหาร", "พลังงาน", "เดินทาง", "ครอบครัว", "บ้านสวน", "ลดน้ำหนัก"]
        found = [word for word in candidates if word in value]
        return found[:8]

    def _lpe10k_deep_understanding_box(answer, module):
        answer = str(answer or "").strip()
        keys = _lpe10k_deep_keywords(answer)
        with _lpe10k_deep_st.expander("ระบบเข้าใจเบื้องต้น / ใช้ข้อมูลนี้เพื่อ", expanded=True):
            if answer:
                preview = answer[:170] + ("..." if len(answer) > 170 else "")
                _lpe10k_deep_st.markdown(f"- สิ่งที่เล่า: {preview}")
            else:
                _lpe10k_deep_st.markdown("- ยังไม่มีคำตอบละเอียดในหมวดนี้")
            _lpe10k_deep_st.markdown("- สัญญาณสำคัญที่พบ: " + (", ".join(keys) if keys else "ยังไม่ชัด"))
            _lpe10k_deep_st.markdown("- ระบบจะใช้ข้อมูลนี้เพื่อ: " + module.get("use", "ปรับตารางรายวันให้ตรงชีวิตจริง"))

    def _lpe10k_deep_module_data():
        return [
            {
                "title": "1) เป้าหมายและปัญหาที่อยากแก้",
                "subtitle": "เริ่มจากปัญหาจริง ไม่ใช่แค่ todo list",
                "key": "lpe10k_deep_m1_answer",
                "questions": [
                    "ตอนนี้เป้าหมายหลักที่อยากให้ชีวิตดีขึ้นคืออะไร",
                    "ปัญหาที่ทำให้แผนพังบ่อยที่สุดคืออะไร",
                    "อะไรคือสิ่งที่พลาดไม่ได้ใน 30 วันนี้",
                    "ถ้าวันเหนื่อยมาก minimum success คืออะไร",
                    "อะไรควรถูกลดหรือเลื่อนเมื่อเวลาน้อย",
                ],
                "placeholder": "เช่น อ่านสอบ 18-19 ก.ค. ให้ทัน, ลดน้ำหนัก, โปรเจกต์สำคัญ, งานประจำ, งานบ้านที่ต้องดูแล...",
                "default": "ตั้งใจอ่านหนังสือสอบ 18-19 ก.ค.69, อยากลดน้ำหนัก, ต้องมีเวลาพัก, และไม่อยากให้โปรเจกต์กินเวลาอ่านกับนอน",
                "use": "จัดลำดับว่าอะไรเป็นพระเอกของวัน ลดงานรองเมื่อเป้าหมายหลักเสี่ยงหลุด และเลือก minimum action เมื่อพลังงานต่ำ",
            },
            {
                "title": "2) เวลาและจังหวะชีวิต",
                "subtitle": "ให้ระบบรู้เวลาจริง เพื่อไม่วางแผนชนงานหรือชนเวลานอน",
                "key": "lpe10k_deep_m2_answer",
                "questions": [
                    "เวลาตื่นและเวลานอนปกติคือเมื่อไร",
                    "งาน/เวรเริ่มและเลิกกี่โมง",
                    "เตรียมตัวและเดินทางใช้เวลากี่นาที",
                    "ช่วงไหนสมองดีที่สุด",
                    "หลังเวลาไหนไม่ควรเริ่มงานหนัก",
                    "เวรต่อแบบไหนต้องระวัง เช่น ช→ด, บ→ช, ด/บ",
                ],
                "placeholder": "เช่น เวรเช้า 08-16, บ่าย 16-00, ดึก 00-08, เตรียมตัว 90 นาที, เดินทาง 15 นาที...",
                "default": "ทำงาน 8 ชั่วโมง, เวรเช้า 08:00-16:00, เวรบ่าย 16:00-00:00, เวรดึก 00:00-08:00, เตรียมตัว 90 นาที, เดินทาง 15 นาที, ช→ด ต้องนอนก่อนดึก",
                "use": "หาเวลาว่างจริง กันเวลานอนและเวลาเตรียมตัว และเลือกตารางประจำวันที่ไม่ชนเวรต่อเวร",
            },
            {
                "title": "3) สุขภาพและพลังงาน",
                "subtitle": "ใช้แผนไม่ฝืนร่างกาย และปรับตามพลังงานจริง",
                "key": "lpe10k_deep_m3_answer",
                "questions": [
                    "เป้าหมายสุขภาพหรือพลังงานคืออะไร",
                    "พลังงานหลังเลิกงานปกติเป็นอย่างไร",
                    "ชอบขยับตัวหรือออกกำลังแบบไหน",
                    "มีข้อจำกัดร่างกายหรืออาหารที่ต้องระวังไหม",
                    "อาหารที่กินง่ายและเหมาะกับชีวิตจริงคืออะไร",
                ],
                "placeholder": "เช่น อยากลดน้ำหนัก, ชอบเดิน/วิ่ง/ยืด, อาหารที่มีง่ายคือไข่ ไก่ทอด ผักนึ่ง ผลไม้...",
                "default": "อยากลดน้ำหนักและหุ่นดี, ชอบเดินหรือวิ่ง, มีอุปกรณ์ที่บ้าน, อาหารที่กินได้ง่ายคือไข่ ไก่ทอด ผักนึ่ง ผลไม้, ไม่ต้องการคำแนะนำเกินจริง",
                "use": "เลือกการขยับตัวตามสภาพจริง ลดความหนักในวันที่นอนน้อยหรือเวรหนัก และแนะนำอาหารทั่วไปแบบไม่ใช่คำแนะนำเฉพาะทาง",
            },
            {
                "title": "4) งาน / เงิน / ภาระที่ห้ามพลาด",
                "subtitle": "ให้ระบบรู้อะไรคือข้อผูกมัดที่ห้ามกระทบ",
                "key": "lpe10k_deep_m4_answer",
                "questions": [
                    "งานหรือเวรที่ห้ามกระทบคืออะไร",
                    "งานที่พลาดไม่ได้มีอะไรบ้าง",
                    "โปรเจกต์ไหนสำคัญต่ออนาคตหรือรายได้",
                    "ถ้าวันมีงานหนัก ระบบควรลดอะไร",
                    "อะไรคือความรับผิดชอบที่ต้องกินเวลาเสมอ",
                ],
                "placeholder": "เช่น เวรประจำ, โปรเจกต์, เทรด, เตรียมสอบ, งานบ้าน, ดูแลครอบครัว...",
                "default": "งานประจำและเวรต้องมาก่อน, สอบพลาดไม่ได้, โปรเจกต์และงานเสริมสำคัญแต่ต้องไม่ชนการนอนและการอ่านสอบ",
                "use": "กันเวลางานประจำและความรับผิดชอบไม่ให้เสีย จัด priority เมื่อเรียน งาน สุขภาพ และโปรเจกต์ชนกัน",
            },
            {
                "title": "5) เรื่องราวชีวิตและกฎส่วนตัว",
                "subtitle": "ทำให้ระบบไม่ generic และรู้ข้อห้ามเฉพาะตัว",
                "key": "lpe10k_deep_m5_answer",
                "questions": [
                    "ชีวิตช่วงนี้กำลังแบกอะไรอยู่",
                    "ปัญหาซ้ำ ๆ ที่ทำให้แผนพังบ่อยคืออะไร",
                    "อยากให้ระบบเตือนแบบอ่อนโยนหรือเข้มงวด",
                    "ถ้าพลังต่ำมาก แผนขั้นต่ำควรเหลืออะไร",
                    "สิ่งที่ระบบไม่ควรแนะนำคืออะไร",
                ],
                "placeholder": "เช่น ต้องการความจริง ไม่ชอบคำอวยเกินจริง ไม่อยากเปิด scope ใหม่ ต้องการแผนที่ทำได้จริง...",
                "default": "ต้องการความจริง ไม่เอาคำแนะนำสวยแต่ทำไม่ได้ ไม่เปิด scope ใหม่ และอยากให้ระบบช่วยเลือกสิ่งสำคัญที่สุดของวัน",
                "use": "ตั้งกฎส่วนตัวให้แผนรายวัน ลดคำแนะนำที่ไม่ตรงนิสัย และกำหนด fallback plan วันที่เหนื่อยหรือเวลาไม่พอ",
            },
        ]

    def _lpe10k_deep_render_module(module):
        _lpe10k_deep_st.markdown(f"## {module['title']}")
        _lpe10k_deep_st.caption(module["subtitle"])
        with _lpe10k_deep_st.expander("คำถามนำทาง", expanded=True):
            for q in module["questions"]:
                _lpe10k_deep_st.markdown(f"- {q}")
        answer = _lpe10k_deep_st.text_area(
            "ช่องเล่าเรื่องหมวดนี้",
            value=module.get("default", ""),
            placeholder=module.get("placeholder", ""),
            key=module["key"],
            height=150,
        )
        _lpe10k_deep_understanding_box(answer, module)

    def _lpe10k_deep_render_guided_profile_setup():
        _lpe10k_deep_st.markdown("# ⚙️ ตั้งค่าชีวิตละเอียด")
        _lpe10k_deep_st.caption("โหมดนี้รวมโครงใหม่กับคำถามละเอียดแบบเดิม: เล่าให้ระบบเข้าใจชีวิตจริง แล้วระบบจะนำไปจัดตารางรายวัน")
        _lpe10k_deep_memory_preview()
        setup_mode = _lpe10k_deep_st.radio(
            "รูปแบบการกรอก",
            ["สัมภาษณ์ละเอียด 5 หมวด", "ข้อมูลเดิม / แก้ไขต่อ", "Quick setup"],
            horizontal=True,
            key="lpe10k_deep_setup_style_v1",
        )
        if setup_mode == "Quick setup":
            _lpe10k_deep_st.subheader("Quick setup")
            _lpe10k_deep_st.text_input("ชื่อที่ให้ระบบเรียก", value="ประสบชัย", key="lpe10k_deep_quick_name")
            _lpe10k_deep_st.selectbox("รูปแบบชีวิตหลัก", ["ทำงานเวร", "ออฟฟิศ", "นักเรียน/นักศึกษา", "ฟรีแลนซ์", "ค้าขาย", "ดูแลครอบครัว", "อื่น ๆ"], key="lpe10k_deep_quick_pattern")
            _lpe10k_deep_st.text_area("เป้าหมายหลัก / งานด่วน / พรุ่งนี้ต้องระวัง", placeholder="ตอบสั้น ๆ เพื่อเริ่มใช้งานเร็ว", key="lpe10k_deep_quick_goal")
            return
        if setup_mode == "ข้อมูลเดิม / แก้ไขต่อ":
            _lpe10k_deep_st.subheader("ข้อมูลเดิม / แก้ไขต่อ")
            _lpe10k_deep_st.text_area("ข้อมูลพื้นฐานที่ระบบควรยึด", value="เวรเช้า 08:00-16:00\nเวรบ่าย 16:00-00:00\nเวรดึก 00:00-08:00\nเตรียมตัว 90 นาที\nเดินทาง 15 นาที\nช→ด ต้องกันเวลานอนก่อนดึก\nด/บ คือ 00:00-08:00 และ 16:00-00:00 วันเดียวกัน", key="lpe10k_deep_known_facts", height=220)
            _lpe10k_deep_st.text_area("สิ่งที่ต้องแก้หรือเพิ่มจากข้อมูลเดิม", placeholder="ข้อมูลไหนเปลี่ยนแล้ว หรือมีอะไรที่ระบบยังไม่รู้", key="lpe10k_deep_known_update")
            return
        modules = _lpe10k_deep_module_data()
        labels = [m["title"] for m in modules] + ["ตรวจความครบ"]
        selected = _lpe10k_deep_st.selectbox("เลือกหมวดที่ต้องการกรอก", labels, key="lpe10k_deep_module_selector_v1")
        if selected == "ตรวจความครบ":
            _lpe10k_deep_st.markdown("## ตรวจความครบของตั้งค่าชีวิต")
            completed = 0
            for m in modules:
                value = str(_lpe10k_deep_st.session_state.get(m["key"], "")).strip()
                if len(value) >= 40:
                    completed += 1
                    _lpe10k_deep_st.success(f"กรอกแล้ว: {m['title']}")
                else:
                    _lpe10k_deep_st.warning(f"ยังควรเติม: {m['title']}")
            _lpe10k_deep_st.metric("ความครบของตั้งค่าชีวิต", f"{completed}/5 หมวด")
            _lpe10k_deep_st.info("ก่อน Phase10L ควรมีข้อมูลเป้าหมาย เวลา/เวร พลังงาน งานที่ห้ามพลาด และกฎส่วนตัวครบอย่างน้อยระดับใช้งานได้")
        else:
            module = next(m for m in modules if m["title"] == selected)
            _lpe10k_deep_render_module(module)

    def _lpe10k_deep_render_roster_report():
        rows = _lpe10k_deep_rows()
        _lpe10k_deep_st.markdown("# 🧭 ตรวจตารางเวร/shift-chain มิ.ย.69")
        _lpe10k_deep_st.caption("ตรวจ manual roster map และ chain ก่อนนำไปผูกกับตารางอ่านและ daily board")
        checks = {"2026-06-01": "M_TO_N", "2026-06-02": "N_A", "2026-06-03": "A_TO_M"}
        c1, c2, c3, c4 = _lpe10k_deep_st.columns(4)
        c1.metric("จำนวนวัน", len(rows))
        c2.metric("M_TO_N", sum(1 for r in rows if r["ไปพรุ่งนี้"] == "M_TO_N"))
        c3.metric("N_A", sum(1 for r in rows if r["รหัสเวร"] == "N_A"))
        c4.metric("วันที่เสี่ยงสูง", sum(1 for r in rows if r["planning_mode"] in {"DOUBLE_SHIFT_SURVIVAL_DAY", "HIGH_SLEEP_RISK_DAY", "PRE_NIGHT_PROTECTION_DAY", "CONSECUTIVE_NIGHT_SHIFT_DAY"}))
        for date, expected in checks.items():
            row = next((r for r in rows if r["วันที่"] == date), None)
            actual = row["รหัสเวร"] if expected == "N_A" else (row["ไปพรุ่งนี้"] if date == "2026-06-01" else row["จากเมื่อวาน"])
            if actual == expected:
                _lpe10k_deep_st.success(f"{date}: PASS = {expected}")
            else:
                _lpe10k_deep_st.error(f"{date}: CHECK expected {expected}, actual {actual}")
        _lpe10k_deep_st.dataframe(rows, use_container_width=True, hide_index=True)
        _lpe10k_deep_st.warning("ตรวจคุณภาพก่อน Phase10L: ดึกต่อดึกควรถือเป็นวันที่ต้องปกป้องการนอนและไม่ควรยัดงานหนัก")

    def _lpe10k_deep_mode_gate():
        _lpe10k_deep_st.markdown("## โหมดระบบ")
        _lpe10k_deep_st.caption("เลือกโหมดหลักก่อนใช้งาน: daily-use, ตั้งค่าฐานชีวิตละเอียด, หรือตรวจตารางเวร")
        mode = _lpe10k_deep_st.radio(
            "เลือกโหมด",
            ["ใช้งานประจำวัน", "ตั้งค่าชีวิตละเอียด", "ตรวจตารางเวร/shift-chain"],
            horizontal=True,
            key="lpe10k_deep_main_mode_selector_v1",
        )
        if mode == "ตั้งค่าชีวิตละเอียด":
            _lpe10k_deep_render_guided_profile_setup()
            _lpe10k_deep_st.stop()
        if mode == "ตรวจตารางเวร/shift-chain":
            _lpe10k_deep_render_roster_report()
            try:
                _lpe10l_render_study_plan_alignment()
            except Exception as _lpe10l_error:
                st.warning(f"Phase10L study alignment error: {_lpe10l_error}")
            _lpe10k_deep_st.stop()


    # --- PHASE10M_DAILY_BOARD_USE_PLANNING_MODE_AND_STUDY_LOAD_PATCH_V3_AFTER_MODE_GATE BEGIN ---
    PHASE10M_DAILY_BOARD_USE_PLANNING_MODE_AND_STUDY_LOAD_PATCH_V3_AFTER_MODE_GATE = True
    def _lpe10m_pick_value(_row, *_keys, _default="-"):
        for _key in _keys:
            try:
                _value = _row.get(_key)
            except Exception:
                _value = None
            if _value not in (None, ""):
                return _value
        return _default

    def _lpe10m_build_daily_slots(_planning_mode, _study_load, _shift_label):
        _pm = str(_planning_mode or "")
        _sl = str(_study_load or "")
        _shift = str(_shift_label or "")
        if "DOUBLE_SHIFT" in _pm or "CONSECUTIVE_NIGHT" in _pm or "SLEEP_FIRST" in _sl:
            return [
                {"ช่วง": "หลังเวร/หลังตื่น", "งานหลัก": "นอน/พักก่อน", "เหตุผล": "วันนี้เสี่ยง sleep debt สูง"},
                {"ช่วง": "พลังงานพอ", "งานหลัก": "ทวน micro 5-15 นาที", "เหตุผล": _sl or "MICRO_REVIEW_ONLY"},
                {"ช่วง": "ก่อนนอน", "งานหลัก": "เตรียมของเวรถัดไป + ปิดจอ", "เหตุผล": _pm or "กันวันพัง"},
            ]
        if "PRE_NIGHT" in _pm or "M_TO_N" in _shift:
            return [
                {"ช่วง": "เช้า/หลังตื่น", "งานหลัก": "งานจำเป็นสั้น ๆ", "เหตุผล": "วันนี้ต้องกันแรงก่อนเวรดึก"},
                {"ช่วง": "เย็น", "งานหลัก": "ทวนเบา / ไม่เปิดงานยาว", "เหตุผล": _pm or "PRE_NIGHT_PROTECTION_DAY"},
                {"ช่วง": "ก่อนเวร", "งานหลัก": "นอนนำ + เตรียมตัว", "เหตุผล": "ป้องกันพลังงานตกช่วงดึก"},
            ]
        if "OFF_STUDY" in _pm or "VAC_STUDY" in _pm or "DEEP_STUDY" in _sl:
            return [
                {"ช่วง": "ช่วงสมองดีที่สุด", "งานหลัก": "อ่านหลัก / ชดเชยบทค้าง", "เหตุผล": _sl or "DEEP_STUDY_OR_CATCHUP"},
                {"ช่วง": "ช่วงรอง", "งานหลัก": "สรุปโน้ต / ทำโจทย์สั้น", "เหตุผล": "ต่อยอดจาก deep study"},
                {"ช่วง": "ท้ายวัน", "งานหลัก": "สรุปวันนี้ + เตรียมพรุ่งนี้", "เหตุผล": "รักษา rolling target"},
            ]
        if "MORNING_DEEP" in _sl:
            return [
                {"ช่วง": "เช้า", "งานหลัก": "อ่านหลักก่อนเวร/ก่อนงาน", "เหตุผล": _sl},
                {"ช่วง": "บ่าย/เย็น", "งานหลัก": "เวร/งานหลัก", "เหตุผล": _shift},
                {"ช่วง": "ก่อนนอน", "งานหลัก": "ทวนสั้น + ปิดวัน", "เหตุผล": "ไม่ให้แผนอ่านกินเวลานอน"},
            ]
        return [
            {"ช่วง": "เริ่มวัน", "งานหลัก": "เลือก 1 งานสำคัญ", "เหตุผล": _pm or "NORMAL_DAY"},
            {"ช่วง": "ช่วงอ่าน", "งานหลัก": "ทวน/อ่านตามกำลัง", "เหตุผล": _sl or "LIGHT_REVIEW"},
            {"ช่วง": "ท้ายวัน", "งานหลัก": "สรุปวันนี้ + เตรียมพรุ่งนี้", "เหตุผล": "คุมความต่อเนื่อง"},
        ]

    def _lpe10m_render_daily_board_shift_study(selected_date=None, selected_row=None):
        # PHASE10O_B_ENGINE_DETAILS_SECONDARY_EXPANDER_V1D
        _st = globals().get("_lpe10l_st") or globals().get("_lpe10k_deep_st") or globals().get("st")
        if _st is None:
            return
        def _pick(row, *keys, default="-"):
            for key in keys:
                try:
                    value = row.get(key)
                except Exception:
                    value = None
                if value not in (None, ""):
                    return str(value)
            return default
        try:
            rows = _lpe10l_build_rows()
        except Exception as _rows_error:
            _st.caption(f"ยังอ่าน shift-chain ไม่ได้: {_rows_error}")
            return
        if not rows:
            _st.caption("ยังไม่มีข้อมูล shift-chain")
            return
        row = selected_row
        if not isinstance(row, dict):
            if selected_date:
                row = next((r for r in rows if str(r.get("วันที่", "")) == str(selected_date)), rows[0])
            else:
                row = rows[0]
        planning_mode = _pick(row, "planning_mode")
        study_load = _pick(row, "study_load")
        shift = _pick(row, "รหัสเวร", "เวร", "shift", "today_shift")
        prev_chain = _pick(row, "จากเมื่อวาน", "prev_chain", "chain")
        next_chain = _pick(row, "ไปพรุ่งนี้", "next_chain", "chain")
        _st.markdown("### แผนที่ระบบแนะนำ")
        _st.caption("ส่วนนี้เป็นเหตุผลประกอบ ไม่ใช่จุดโฟกัสหลักของหน้า")
        try:
            rec_rows = _lpe10m_build_daily_slots(planning_mode, study_load, next_chain or shift)
        except Exception:
            rec_rows = []
        if rec_rows:
            _st.dataframe(rec_rows, use_container_width=True, hide_index=True)
        _st.markdown(
            f'<span class="lpe10ob-badge lpe10ob-badge-gray">เวร: {shift}</span>'
            f'<span class="lpe10ob-badge lpe10ob-badge-gray">จากเมื่อวาน: {prev_chain}</span>'
            f'<span class="lpe10ob-badge lpe10ob-badge-gray">ไปพรุ่งนี้: {next_chain}</span>'
            f'<span class="lpe10ob-badge lpe10ob-badge-gray">planning_mode: {planning_mode}</span>'
            f'<span class="lpe10ob-badge lpe10ob-badge-gray">study_load: {study_load}</span>',
            unsafe_allow_html=True,
        )
    # --- PHASE10M_DAILY_BOARD_USE_PLANNING_MODE_AND_STUDY_LOAD_PATCH_V3_AFTER_MODE_GATE END ---

# --- PHASE10N_END_OF_DAY_AND_TOMORROW_REFINEMENT_USING_PLANNING_MODE_AND_STUDY_LOAD_PATCH_V1 BEGIN ---
PHASE10N_END_OF_DAY_AND_TOMORROW_REFINEMENT_USING_PLANNING_MODE_AND_STUDY_LOAD_PATCH_V1 = True


def _lpe10n_safe_text(value, fallback="-"):
    try:
        if value is None:
            return fallback
        value = str(value)
        return value if value.strip() else fallback
    except Exception:
        return fallback


def _lpe10n_rows():
    try:
        rows = _lpe10l_build_rows()
    except Exception:
        rows = []
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _lpe10n_default_date_index(date_options):
    if not date_options:
        return 0
    for target in ("2026-06-26", "2026-06-20", "2026-06-19"):
        if target in date_options:
            return date_options.index(target)
    return max(0, min(len(date_options) - 1, 0))


def _lpe10n_day_class(row):
    planning_mode = _lpe10n_safe_text(row.get("planning_mode"))
    study_load = _lpe10n_safe_text(row.get("study_load"))
    if planning_mode in {"DOUBLE_SHIFT_SURVIVAL_DAY", "HIGH_SLEEP_RISK_DAY", "CONSECUTIVE_NIGHT_SHIFT_DAY", "PRE_NIGHT_PROTECTION_DAY"}:
        return "กันนอนและลดงานหนัก"
    if planning_mode in {"OFF_STUDY_DAY", "VAC_STUDY_DAY"} or study_load in {"DEEP_STUDY_OR_CATCHUP", "MORNING_DEEP_STUDY"}:
        return "อ่านหลักหรือชดเชย"
    if "MICRO" in study_load:
        return "micro review / รักษา momentum"
    return "วันปกติแบบยืดหยุ่น"


def _lpe10n_tomorrow_plan_rows(tomorrow):
    planning_mode = _lpe10n_safe_text(tomorrow.get("planning_mode"))
    study_load = _lpe10n_safe_text(tomorrow.get("study_load"))
    shift_code = _lpe10n_safe_text(tomorrow.get("รหัสเวร"))
    next_chain = _lpe10n_safe_text(tomorrow.get("ไปพรุ่งนี้"))

    if planning_mode in {"DOUBLE_SHIFT_SURVIVAL_DAY", "HIGH_SLEEP_RISK_DAY", "CONSECUTIVE_NIGHT_SHIFT_DAY", "PRE_NIGHT_PROTECTION_DAY"}:
        return [
            {"หัวข้อ": "นอน/ฟื้นตัว", "แผนพรุ่งนี้": "ล็อกเวลานอนก่อน แล้วลดงานหนัก", "เหตุผล": planning_mode},
            {"หัวข้อ": "อ่าน/สอบ", "แผนพรุ่งนี้": "ทำ micro review 5-15 นาที หรือหัวข้อย่อยเดียว", "เหตุผล": study_load},
            {"หัวข้อ": "งานหลัก", "แผนพรุ่งนี้": "เลือกงานสำคัญที่สุด 1 อย่างเท่านั้น", "เหตุผล": "กันแผนพังจากเวรหนัก"},
            {"หัวข้อ": "เตรียมก่อนนอน", "แผนพรุ่งนี้": "เตรียมของ/เอกสาร/ชุดทำงานล่วงหน้า", "เหตุผล": f"เวร={shift_code}, chain={next_chain}"},
        ]
    if planning_mode in {"OFF_STUDY_DAY", "VAC_STUDY_DAY"} or study_load in {"DEEP_STUDY_OR_CATCHUP", "MORNING_DEEP_STUDY"}:
        return [
            {"หัวข้อ": "อ่านหลัก", "แผนพรุ่งนี้": "ใช้ช่วงสมองดีที่สุดทำ deep study หรือชดเชยบทค้าง", "เหตุผล": study_load},
            {"หัวข้อ": "งานบ้าน/ชีวิต", "แผนพรุ่งนี้": "เคลียร์งานจำเป็นที่ค้างแบบไม่เปิด scope ใหม่", "เหตุผล": planning_mode},
            {"หัวข้อ": "พัก", "แผนพรุ่งนี้": "ใส่พักจริงหลังอ่านหลักเพื่อไม่ให้หมดแรงต่อเนื่อง", "เหตุผล": "รักษา rolling target"},
            {"หัวข้อ": "ปิดวัน", "แผนพรุ่งนี้": "สรุป 3 บรรทัด: อ่านอะไร / ค้างอะไร / พรุ่งนี้ทำอะไรต่อ", "เหตุผล": "ต่อยอดแผนถัดไป"},
        ]
    return [
        {"หัวข้อ": "งานหลัก", "แผนพรุ่งนี้": "ทำงานสำคัญ 1 อย่างก่อนงานรอง", "เหตุผล": planning_mode},
        {"หัวข้อ": "อ่าน/สอบ", "แผนพรุ่งนี้": "อ่านสั้นแบบไม่ฝืน ถ้าพลังงานดีก็ค่อยเพิ่ม", "เหตุผล": study_load},
        {"หัวข้อ": "พลังงาน", "แผนพรุ่งนี้": "เช็คพลังงานจริงก่อนเพิ่มงาน", "เหตุผล": "กันตารางแน่นเกินจริง"},
        {"หัวข้อ": "ปิดวัน", "แผนพรุ่งนี้": "เลือก next single action สำหรับวันถัดไป", "เหตุผล": "ลด friction ตอนเริ่มวัน"},
    ]


def _lpe10n_render_end_of_day_tomorrow_refinement():
    # PHASE10O_B_SIMPLE_SUMMARY_TOMORROW_V1D
    st = globals().get("_lpe10l_st") or globals().get("_lpe10k_deep_st") or globals().get("st")
    if st is None:
        try:
            import streamlit as st  # type: ignore
        except Exception:
            return
    def _safe(value, fallback="-"):
        try:
            text = str(value)
            return text if text.strip() else fallback
        except Exception:
            return fallback
    try:
        rows = _lpe10l_build_rows()
    except Exception:
        rows = []
    rows = rows if isinstance(rows, list) else []
    if not rows:
        st.warning("ยังไม่มีข้อมูลเวรสำหรับสรุปวันนี้")
        return
    date_options = [_safe(r.get("วันที่")) for r in rows if isinstance(r, dict) and r.get("วันที่")]
    if not date_options:
        st.warning("ยังไม่มีวันที่ในข้อมูลเวร")
        return
    default_date = "2026-06-26" if "2026-06-26" in date_options else date_options[0]
    selected_date = st.selectbox("เลือกวันที่", date_options, index=date_options.index(default_date), key="lpe10ob_summary_date")
    idx = date_options.index(selected_date)
    today = rows[idx]
    tomorrow = rows[idx + 1] if idx + 1 < len(rows) else today

    st.markdown("## สรุปวันนี้ / เตรียมพรุ่งนี้")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<span class="lpe10ob-badge lpe10ob-badge-gray">วันนี้: {_safe(today.get("วันที่"))}</span>', unsafe_allow_html=True)
    c2.markdown(f'<span class="lpe10ob-badge lpe10ob-badge-blue">พรุ่งนี้: {_safe(tomorrow.get("วันที่"))}</span>', unsafe_allow_html=True)
    c3.markdown(f'<span class="lpe10ob-badge lpe10ob-badge-green">เวรพรุ่งนี้: {_safe(tomorrow.get("รหัสเวร"), _safe(tomorrow.get("เวร")))}</span>', unsafe_allow_html=True)

    st.markdown("### สรุปวันนี้")
    st.text_area("วันนี้สำเร็จอะไรบ้าง", value="ทำสิ่งสำคัญอย่างน้อย 1 อย่าง / รักษาแผนตามพลังงานจริง", key="lpe10ob_today_done", height=90)
    st.text_area("อะไรต้องเลื่อนหรือกันพลาด", value="งานที่ไม่จำเป็นหรือเกินพลังงาน ให้เลื่อนไปตาม rolling target", key="lpe10ob_today_move", height=90)
    st.slider("พลังงานท้ายวัน", 1, 5, 3, key="lpe10ob_end_energy")

    st.markdown("### เตรียมพรุ่งนี้")
    tomorrow_plan = [
        {"หัวข้อ": "เวร / จังหวะวัน", "พรุ่งนี้ต้องรู้": f"เวร={_safe(tomorrow.get('รหัสเวร'), _safe(tomorrow.get('เวร')))} | chain={_safe(tomorrow.get('จากเมื่อวาน'))} / {_safe(tomorrow.get('ไปพรุ่งนี้'))}"},
        {"หัวข้อ": "สิ่งแรก", "พรุ่งนี้ต้องรู้": "เริ่มจากงานหรืออ่านที่สำคัญที่สุด 1 อย่างก่อนเปิด scope ใหม่"},
        {"หัวข้อ": "กันพลาด", "พรุ่งนี้ต้องรู้": "กันเวลานอน/เตรียมของ/ลดงานที่ไม่จำเป็นตามพลังงานจริง"},
    ]
    st.dataframe(tomorrow_plan, use_container_width=True, hide_index=True)
    st.text_input("next single action พรุ่งนี้", value="เปิดตาราง -> ทำรายการแรกของวัน", key="lpe10ob_tomorrow_next_single_action")

    with st.expander("เหตุผลของระบบ", expanded=False):
        st.markdown(
            f'<span class="lpe10ob-badge lpe10ob-badge-gray">planning_mode วันนี้: {_safe(today.get("planning_mode"))}</span>'
            f'<span class="lpe10ob-badge lpe10ob-badge-gray">study_load วันนี้: {_safe(today.get("study_load"))}</span>'
            f'<span class="lpe10ob-badge lpe10ob-badge-gray">planning_mode พรุ่งนี้: {_safe(tomorrow.get("planning_mode"))}</span>'
            f'<span class="lpe10ob-badge lpe10ob-badge-gray">study_load พรุ่งนี้: {_safe(tomorrow.get("study_load"))}</span>',
            unsafe_allow_html=True,
        )
# --- PHASE10N_END_OF_DAY_AND_TOMORROW_REFINEMENT_USING_PLANNING_MODE_AND_STUDY_LOAD_PATCH_V1 END ---

    # PHASE10N_RUNTIME_AUTHORITY_REPAIR_V2B_REMOVED_MISPLACED_ROUTER

# PHASE10L_SYNTAX_REPAIR_DEEP_TRY_BLOCK_V2
# END PHASE10K_RESTORE_DEEP_GUIDED_PROFILE_QUESTIONNAIRE_IN_NEW_MODE_V1

try:
    if _lpe_phase10h_main():
        st.stop()
except Exception as _phase10h_error:
    st.error("Phase10H daily board render error")
    st.exception(_phase10h_error)
    st.stop()


# VERSION_A_PHASE8E_PROFILE_HELPER_NAMEERROR_REPAIR_V1
# Early profile helper bridge: defined before any Phase renderer can call it.
def _lpe_phase8_get_profile_for_export():
    """Return the active local personal profile from known session keys."""
    try:
        state = st.session_state
    except Exception:
        return None

    candidate_keys = [
        "lpe_version_a_personal_profile_v1",
        "lpe_version_a_personal_profile",
        "personal_profile",
        "life_profile",
        "lpe_life_profile",
        "profile",
        "lpe_version_a_personal_dashboard_profile",
    ]
    for key in candidate_keys:
        val = state.get(key)
        if isinstance(val, dict) and val:
            return val

    bundle_like_keys = [
        "lpe_version_a_profile_bundle",
        "life_settings_profile",
        "lpe_life_settings_profile",
        "lpe_version_a_settings_profile",
    ]
    for key in bundle_like_keys:
        val = state.get(key)
        if not isinstance(val, dict) or not val:
            continue
        for inner_key in ("profile", "personal_profile", "life_profile", "data", "core_life_profile"):
            inner_val = val.get(inner_key)
            if isinstance(inner_val, dict) and inner_val:
                return inner_val
        return val

    return None


APP_URL = "https://life-priority-engine.streamlit.app"
DATA_DIR = Path("data")

PRIMARY_NAV_ITEMS = (
    "🏠 วันนี้",
    "🧭 เริ่มต้น",
    "🌤 พรุ่งนี้",
    "🕒 แผนรายวัน",
    "••• เพิ่มเติม",
)
PRIMARY_NAV_DESTINATIONS = {
    "🏠 วันนี้": "วันนี้ต้องทำอะไร",
    "🧭 เริ่มต้น": "เริ่มต้นใช้งาน",
    "🌤 พรุ่งนี้": "แผนพรุ่งนี้",
    "🕒 แผนรายวัน": "แผนละเอียดรายวัน",
    "••• เพิ่มเติม": "เพิ่มเติม",
}
DESTINATION_TO_PRIMARY_NAV = {
    destination: label for label, destination in PRIMARY_NAV_DESTINATIONS.items()
}
DESKTOP_NAV_ITEMS = (
    "วันนี้ต้องทำอะไร",
    "เริ่มต้นใช้งาน",
    "แผนพรุ่งนี้",
    "แผนละเอียดรายวัน",
    "เพิ่มเติม",
    "ภาพรวม 30 วัน",
    "ตั้งค่าชีวิต",
)

st.set_page_config(
    page_title="ผู้ช่วยจัดลำดับชีวิต",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)






# PHASE10K_REPAIR_ADVANCED_MODE_AND_ROSTER_REPORT_NAVIGATION_BATCH_V1
# LPE10K_REPAIR_MODE_SELECTOR_MAIN_FALLBACK_V1
# LPE10K_REPAIR_ROSTER_REPORT_DIRECT_ACCESS_V1
# LPE10K_REPAIR_PROFILE_SETUP_DIRECT_ACCESS_V1
# LPE10K_REPAIR_SIDEBAR_TOGGLE_BYPASS_V1
try:
    import streamlit as st
except Exception:
    st = None

if st is not None:
    def _lpe10k_repair_normalize_shift(raw_value):
        raw_text = str(raw_value or "").strip()
        star_note = "*" in raw_text
        cleaned = raw_text.replace("*", "").strip()
        if cleaned in {"ด/บ", "N/A", "N_A", "NA"}:
            return {"raw": raw_text, "code": "N_A", "first": "N", "last": "A", "star_note": star_note}
        mapping = {"ช": "M", "บ": "A", "ด": "N", "O": "O", "0": "O", "V": "V", "M": "M", "A": "A", "N": "N"}
        code = mapping.get(cleaned, cleaned or "UNKNOWN")
        return {"raw": raw_text, "code": code, "first": code, "last": code, "star_note": star_note}

    def _lpe10k_repair_chain(left_code, right_code):
        if not left_code or not right_code:
            return "NONE"
        if left_code in {"O", "V"} and right_code in {"M", "A", "N"}:
            return f"{left_code}_TO_{right_code}"
        if left_code in {"M", "A", "N"} and right_code in {"M", "A", "N", "O", "V"}:
            return f"{left_code}_TO_{right_code}"
        return "NONE"

    def _lpe10k_repair_planning_mode(today_code, prev_chain, next_chain):
        if today_code == "N_A":
            return "DOUBLE_SHIFT_SURVIVAL_DAY"
        if prev_chain == "A_TO_M" and next_chain == "M_TO_N":
            return "HIGH_SLEEP_RISK_DAY"
        if next_chain == "M_TO_N":
            return "PRE_NIGHT_PROTECTION_DAY"
        if prev_chain == "A_TO_M":
            return "AFTERNOON_TO_MORNING_SLEEP_RISK_DAY"
        if prev_chain == "N_TO_A":
            return "NIGHT_TO_AFTERNOON_SURVIVAL_DAY"
        if prev_chain in {"N_TO_O", "N_TO_V"}:
            return "POST_NIGHT_RECOVERY_DAY"
        if today_code == "M":
            return "NORMAL_MORNING_DAY"
        if today_code == "A":
            return "NORMAL_AFTERNOON_DAY"
        if today_code == "N":
            return "NORMAL_NIGHT_DAY"
        if today_code == "O":
            return "OFF_STUDY_DAY"
        if today_code == "V":
            return "VAC_STUDY_DAY"
        return "REVIEW_REQUIRED"

    def _lpe10k_repair_june_roster_rows():
        roster = {
            "2026-06-01": "ช",
            "2026-06-02": "ด/บ",
            "2026-06-03": "ช",
            "2026-06-04": "ด*",
            "2026-06-05": "ด*",
            "2026-06-06": "O",
            "2026-06-07": "ช",
            "2026-06-08": "ด",
            "2026-06-09": "ด*",
            "2026-06-10": "O",
            "2026-06-11": "บ",
            "2026-06-12": "ช",
            "2026-06-13": "ด",
            "2026-06-14": "ช",
            "2026-06-15": "ด",
            "2026-06-16": "O",
            "2026-06-17": "O",
            "2026-06-18": "V",
            "2026-06-19": "V",
            "2026-06-20": "ช*",
            "2026-06-21": "ด",
            "2026-06-22": "ช*",
            "2026-06-23": "ด",
            "2026-06-24": "ด",
            "2026-06-25": "บ",
            "2026-06-26": "O",
            "2026-06-27": "บ",
            "2026-06-28": "ช",
            "2026-06-29": "ด",
            "2026-06-30": "ด",
        }
        dates = sorted(roster)
        rows = []
        normalized = {date: _lpe10k_repair_normalize_shift(raw) for date, raw in roster.items()}
        for index, date in enumerate(dates):
            today = normalized[date]
            prev_date = dates[index - 1] if index > 0 else None
            next_date = dates[index + 1] if index + 1 < len(dates) else None
            prev_info = normalized.get(prev_date, {}) if prev_date else {}
            next_info = normalized.get(next_date, {}) if next_date else {}
            prev_chain = _lpe10k_repair_chain(prev_info.get("last"), today.get("first")) if prev_info else "NONE"
            next_chain = _lpe10k_repair_chain(today.get("last"), next_info.get("first")) if next_info else "NONE"
            rows.append({
                "date": date,
                "raw_shift": today["raw"],
                "shift": today["code"],
                "prev_chain": prev_chain,
                "next_chain": next_chain,
                "planning_mode": _lpe10k_repair_planning_mode(today["code"], prev_chain, next_chain),
                "note": "* kept only as note" if today.get("star_note") else "",
            })
        return rows

    def _lpe10k_repair_render_roster_report():
        st.title("🧭 ตรวจตารางเวร / shift-chain มิ.ย.69")
        st.caption("ทางเข้าตรงสำหรับตรวจ Phase10K เมื่อ sidebar checkbox ใช้งานไม่ได้")
        rows = _lpe10k_repair_june_roster_rows()
        check_01 = next((r for r in rows if r["date"] == "2026-06-01"), {})
        check_02 = next((r for r in rows if r["date"] == "2026-06-02"), {})
        check_03 = next((r for r in rows if r["date"] == "2026-06-03"), {})
        c1, c2, c3 = st.columns(3)
        c1.metric("2026-06-01", check_01.get("next_chain", "-"))
        c2.metric("2026-06-02", check_02.get("shift", "-"))
        c3.metric("2026-06-03", check_03.get("prev_chain", "-"))
        st.info("เกณฑ์ตรวจเร็ว: 2026-06-01 ต้องเป็น M_TO_N, 2026-06-02 ต้องเป็น N_A, 2026-06-03 ต้องเป็น A_TO_M")
        st.dataframe(rows, use_container_width=True, hide_index=True)

    def _lpe10k_repair_render_profile_setup():
        st.title("⚙️ ตั้งค่าชีวิตแบบละเอียด")
        st.caption("ทางเข้าตรงแบบ fallback สำหรับแก้ข้อมูลชีวิต โดยไม่ใช้ checkbox เดิม")
        tab_identity, tab_work, tab_rest, tab_move, tab_goal, tab_rule, tab_daily = st.tabs([
            "ตัวตน", "งาน/เวร", "พัก/อาหาร", "ขยับตัว", "เป้าหมาย", "กฎส่วนตัว", "วันนี้/พรุ่งนี้"
        ])
        with tab_identity:
            st.text_input("ชื่อที่อยากให้ระบบเรียก", value="", placeholder="เช่น ประสบชัย", key="lpe10k_repair_profile_name")
            st.selectbox("รูปแบบชีวิตหลัก", ["ทำงานเวร", "ทำงานประจำ", "นักเรียน/นักศึกษา", "ค้าขาย", "ดูแลครอบครัว", "ฟรีแลนซ์", "อื่นๆ"], key="lpe10k_repair_life_type")
            st.selectbox("สไตล์คำแนะนำ", ["พูดตรง ใช้งานได้จริง", "สุภาพและให้กำลังใจ", "เข้มงวดแบบโค้ช", "สั้นที่สุด", "ละเอียดพร้อมเหตุผล"], key="lpe10k_repair_advice_style")
        with tab_work:
            c1, c2 = st.columns(2)
            c1.number_input("เวลาเตรียมตัวก่อนออกจากบ้าน (นาที)", min_value=0, max_value=240, value=90, step=5, key="lpe10k_repair_prep_min")
            c2.number_input("เวลาเดินทางเฉลี่ย (นาที)", min_value=0, max_value=240, value=15, step=5, key="lpe10k_repair_commute_min")
            st.text_area("ตารางเวรรายเดือนแบบ manual", value="2026-06-01 = ช\n2026-06-02 = ด/บ\n2026-06-03 = ช", key="lpe10k_repair_roster_text")
            st.text_area("หมายเหตุเวรต่อ/เวรซ้อน", value="ช→ด ต้องกันเวลานอนก่อนเวร\nด/บ เป็นวันทำงานสองช่วง", key="lpe10k_repair_shift_note")
        with tab_rest:
            c1, c2 = st.columns(2)
            c1.number_input("ชั่วโมงนอนขั้นต่ำ", min_value=0.0, max_value=14.0, value=6.0, step=0.5, key="lpe10k_repair_min_sleep")
            c2.number_input("ชั่วโมงนอนเป้าหมาย", min_value=0.0, max_value=14.0, value=8.0, step=0.5, key="lpe10k_repair_target_sleep")
            st.text_area("อาหารที่กินได้บ่อย", placeholder="เช่น ไข่ ไก่ทอด ผักนึ่ง", key="lpe10k_repair_food_ok")
            st.text_area("อาหาร/พฤติกรรมที่ควรลด", placeholder="เช่น น้ำหวาน ของทอดหนัก คาเฟอีนดึก", key="lpe10k_repair_food_reduce")
        with tab_move:
            st.text_area("กิจกรรมที่ชอบ", placeholder="เช่น เดิน ยืด วิ่งเบา", key="lpe10k_repair_move_like")
            st.text_input("minimum movement ถ้าเหนื่อยมาก", value="เดิน/ยืด 5-10 นาที", key="lpe10k_repair_min_move")
        with tab_goal:
            st.text_area("เป้าหมายหลักตอนนี้", placeholder="เช่น อ่านสอบให้จบตามแผน", key="lpe10k_repair_goal_main")
            st.text_area("ตารางอ่าน/deadline", placeholder="เช่น 19 มิ.ย.-19 ก.ค. อ่านตามหน่วย", key="lpe10k_repair_study_plan")
        with tab_rule:
            st.text_area("กฎส่วนตัว", value="พูดตรง ไม่เปิด scope ใหม่ ไม่ให้งานยาวชนเวลานอน", key="lpe10k_repair_rules")
        with tab_daily:
            st.slider("พลังงานวันนี้", 1, 5, 3, key="lpe10k_repair_energy_today")
            st.text_input("เวร/งานพรุ่งนี้", placeholder="เช่น ด, บ, O, เดินทาง", key="lpe10k_repair_tomorrow_shift")
            st.text_area("หมายเหตุสำหรับพรุ่งนี้", placeholder="สิ่งที่ต้องระวัง / สิ่งที่ต้องลด", key="lpe10k_repair_tomorrow_note")

    _lpe10k_repair_mode = st.radio(
        "โหมดระบบ",
        ["ใช้งานประจำวัน", "ตั้งค่าชีวิตละเอียด", "ตรวจตารางเวร/shift-chain"],
        horizontal=True,
        key="lpe10k_repair_main_mode_selector",
    )
    if _lpe10k_repair_mode == "ตั้งค่าชีวิตละเอียด":
        _lpe10k_repair_render_profile_setup()
        st.stop()
    if _lpe10k_repair_mode == "ตรวจตารางเวร/shift-chain":
        _lpe10k_repair_render_roster_report()
        st.stop()
# END PHASE10K_REPAIR_ADVANCED_MODE_AND_ROSTER_REPORT_NAVIGATION_BATCH_V1

# === PHASE10J_PROFILE_SETUP_SCHEMA_AND_ADVANCED_SETTINGS_REDESIGN_PATCH_V2 ===
# PHASE10J_REPAIR_ADVANCED_SETTINGS_UI_STRUCTURE_ONLY_V1
# PHASE10J_REPAIR_SIDEBAR_DUPLICATE_NORMAL_MODE_ONLY_V1
# Scope: collapsed advanced life setup layer only. Daily-use dashboard remains two pages:
# 1) ตารางวันนี้  2) สรุปวันนี้ / เตรียมพรุ่งนี้
# This block prepares richer user profile categories for future roster, shift-chain,
# study-plan, daily-context, and end-of-day analysis. It does not add accounts,
# remote storage, external calls, or release authority.

def _lpe10j_text_to_lines(value):
    if not value:
        return []
    return [line.strip() for line in str(value).splitlines() if line.strip()]


def _lpe10j_profile_snapshot():
    import streamlit as st
    return {
        "schema_version": "LPE_PROFILE_SCHEMA_PHASE10J_V1",
        "life_identity": {
            "display_name": st.session_state.get("lpe10j_display_name", ""),
            "life_pattern": st.session_state.get("lpe10j_life_pattern", ""),
            "advice_style": st.session_state.get("lpe10j_advice_style", "พูดตรง ใช้งานได้จริง"),
        },
        "work_and_roster": {
            "work_pattern": st.session_state.get("lpe10j_work_pattern", ""),
            "morning_shift": "08:00-16:00",
            "afternoon_shift": "16:00-00:00",
            "night_shift": "00:00-08:00",
            "prep_minutes": st.session_state.get("lpe10j_prep_minutes", 90),
            "commute_minutes": st.session_state.get("lpe10j_commute_minutes", 15),
            "monthly_roster_notes": _lpe10j_text_to_lines(st.session_state.get("lpe10j_roster_notes", "")),
            "chain_notes": _lpe10j_text_to_lines(st.session_state.get("lpe10j_chain_notes", "")),
        },
        "sleep_energy_food": {
            "minimum_sleep_hours": st.session_state.get("lpe10j_min_sleep", 6.0),
            "target_sleep_hours": st.session_state.get("lpe10j_target_sleep", 8.0),
            "energy_pattern": st.session_state.get("lpe10j_energy_pattern", ""),
            "common_foods": _lpe10j_text_to_lines(st.session_state.get("lpe10j_common_foods", "")),
            "foods_to_reduce": _lpe10j_text_to_lines(st.session_state.get("lpe10j_foods_to_reduce", "")),
            "recovery_rules": _lpe10j_text_to_lines(st.session_state.get("lpe10j_recovery_rules", "")),
        },
        "movement": {
            "preferred_movement": _lpe10j_text_to_lines(st.session_state.get("lpe10j_preferred_movement", "")),
            "minimum_movement": st.session_state.get("lpe10j_min_movement", "เดิน/ยืด 5-10 นาที"),
            "avoid_heavy_days": _lpe10j_text_to_lines(st.session_state.get("lpe10j_avoid_heavy_days", "")),
        },
        "goals_study_project": {
            "current_main_goal": st.session_state.get("lpe10j_main_goal", ""),
            "exam_or_deadline_notes": _lpe10j_text_to_lines(st.session_state.get("lpe10j_deadline_notes", "")),
            "study_plan_notes": _lpe10j_text_to_lines(st.session_state.get("lpe10j_study_plan_notes", "")),
            "project_rules": _lpe10j_text_to_lines(st.session_state.get("lpe10j_project_rules", "")),
        },
        "personal_rules": {
            "priority_rules": _lpe10j_text_to_lines(st.session_state.get("lpe10j_priority_rules", "")),
            "do_not_do": _lpe10j_text_to_lines(st.session_state.get("lpe10j_do_not_do", "")),
            "success_techniques": _lpe10j_text_to_lines(st.session_state.get("lpe10j_success_techniques", "")),
        },
        "daily_and_tomorrow_context": {
            "today_energy": st.session_state.get("lpe10j_today_energy", 3),
            "today_must_do": st.session_state.get("lpe10j_today_must_do", ""),
            "tomorrow_shift_or_event": st.session_state.get("lpe10j_tomorrow_shift", ""),
            "tomorrow_warning": st.session_state.get("lpe10j_tomorrow_warning", ""),
            "next_single_action": st.session_state.get("lpe10j_next_action", ""),
        },
    }


def _lpe10j_render_life_profile_setup():
    import streamlit as st

    with st.sidebar.expander("⚙️ ตั้งค่าชีวิต / ขั้นสูง", expanded=False):
        show_profile_setup = st.checkbox(
            "เปิดหน้าแก้ตั้งค่าชีวิตละเอียดชั่วคราว",
            value=False,
            key="lpe10j_show_profile_setup",
            help="ใช้กรอกครั้งแรกหรือเมื่อชีวิตเปลี่ยน หน้าใช้งานประจำวันยังคงเป็น 2 หน้า",
        )
        st.caption("Phase 10J: เพิ่มชั้นข้อมูลชีวิต แต่ไม่เพิ่มหน้ารายวันให้ซับซ้อน")

    if not st.session_state.get("lpe10j_show_profile_setup", False):
        return False

    st.markdown("### ⚙️ ตั้งค่าชีวิตแบบละเอียด")
    st.markdown(
        """
        <style>
        div[data-baseweb="tab-list"] button[role="tab"] {
            color: #0f172a !important;
            font-weight: 700 !important;
            opacity: 1 !important;
            border-bottom: 1px solid rgba(15, 23, 42, 0.16) !important;
        }
        div[data-baseweb="tab-list"] button[aria-selected="true"] {
            color: #dc2626 !important;
            border-bottom: 2px solid #dc2626 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.caption("กรอกข้อมูลฐานชีวิตให้ระบบเข้าใจงาน เวร การนอน อาหาร การขยับตัว เป้าหมาย และกฎส่วนตัว ก่อนสร้างตารางวันนี้")

    tabs = st.tabs([
        "ตัวตน",
        "งาน/เวร",
        "พัก/อาหาร",
        "ขยับตัว",
        "เป้าหมาย",
        "กฎส่วนตัว",
        "วันนี้/พรุ่งนี้",
        "ตรวจ schema",
    ])

    with tabs[0]:
        st.text_input("ชื่อที่อยากให้ระบบเรียก", key="lpe10j_display_name", placeholder="เช่น ประสบชัย")
        st.selectbox(
            "รูปแบบชีวิตหลัก",
            ["", "ทำงานเวร", "ทำงานเวลาคงที่", "นักเรียน/นักศึกษา", "ฟรีแลนซ์", "ค้าขาย", "ดูแลครอบครัว", "อื่น ๆ"],
            key="lpe10j_life_pattern",
        )
        st.selectbox(
            "สไตล์คำแนะนำที่ต้องการ",
            ["พูดตรง ใช้งานได้จริง", "สุภาพและให้กำลังใจ", "เข้มงวดแบบโค้ช", "สั้นที่สุด", "ละเอียดพร้อมเหตุผล"],
            key="lpe10j_advice_style",
        )

    with tabs[1]:
        st.selectbox(
            "รูปแบบงาน/ตารางผูกมัด",
            ["", "เวรเช้า/บ่าย/ดึก", "งานประจำเวลาแน่นอน", "เรียนตามตาราง", "งานกะไม่แน่นอน", "งานฟรีแลนซ์", "งานบ้าน/ดูแลคนอื่น"],
            key="lpe10j_work_pattern",
        )
        cols = st.columns(2)
        with cols[0]:
            st.number_input("เวลาเตรียมตัวก่อนออกจากบ้าน (นาที)", min_value=0, max_value=240, value=90, step=5, key="lpe10j_prep_minutes")
        with cols[1]:
            st.number_input("เวลาเดินทางเฉลี่ย (นาที)", min_value=0, max_value=240, value=15, step=5, key="lpe10j_commute_minutes")
        st.info("รหัสเวรพื้นฐาน: M=ช 08:00-16:00, A=บ 16:00-00:00, N=ด 00:00-08:00, N_A=ด/บ วันเดียวกัน, O=หยุด, V=ลา")
        st.text_area(
            "ตารางเวรหรือเวลาผูกมัดรายเดือน (กรอกแบบ manual)",
            key="lpe10j_roster_notes",
            placeholder="ตัวอย่าง\n2026-06-01 = ช\n2026-06-02 = ด/บ\n2026-06-03 = ช",
            height=150,
        )
        st.text_area(
            "หมายเหตุเวรต่อ/เวลาต้องเตรียมตัว",
            key="lpe10j_chain_notes",
            placeholder="ตัวอย่าง\nช→ด ต้องนอนก่อนเวรดึก\nบ→ช เสี่ยงนอนน้อย\nด/บ เป็นวันทำงานสองช่วง",
            height=120,
        )

    with tabs[2]:
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("ชั่วโมงนอนขั้นต่ำ", min_value=0.0, max_value=12.0, value=6.0, step=0.5, key="lpe10j_min_sleep")
        with c2:
            st.number_input("ชั่วโมงนอนเป้าหมาย", min_value=0.0, max_value=12.0, value=8.0, step=0.5, key="lpe10j_target_sleep")
        st.text_area("รูปแบบพลังงานของตัวเอง", key="lpe10j_energy_pattern", placeholder="เช่น เช้าดี บ่ายตก ดึกหลังเวรต้องพัก", height=80)
        st.text_area("อาหารที่กินได้บ่อย / มีง่าย", key="lpe10j_common_foods", placeholder="เช่น ไข่, ไก่ทอด, ผักนึ่ง, ผลไม้", height=100)
        st.text_area("อาหาร/พฤติกรรมที่ควรลด", key="lpe10j_foods_to_reduce", placeholder="เช่น น้ำหวาน, ของทอดมากเกิน, กาแฟช่วงดึก", height=100)
        st.text_area("กฎพักฟื้นทั่วไป", key="lpe10j_recovery_rules", placeholder="เช่น ลงดึกแล้วต้องมีช่วงนอนชดเชย / วันเวรต่อกันต้องลดงานยาว", height=100)
        st.caption("ข้อมูลส่วนนี้ใช้เพื่อจัดกิจวัตรทั่วไป ไม่ใช่คำสั่งรักษาหรือแผนโภชนาการเฉพาะโรค")

    with tabs[3]:
        st.text_area("การขยับตัวที่ชอบหรือทำได้จริง", key="lpe10j_preferred_movement", placeholder="เช่น เดิน, ยืด, วิ่งเบา, bodyweight", height=100)
        st.text_input("minimum movement ถ้าวันเหนื่อย", key="lpe10j_min_movement", value="เดิน/ยืด 5-10 นาที")
        st.text_area("วันที่ควรเลี่ยงกิจกรรมหนัก", key="lpe10j_avoid_heavy_days", placeholder="เช่น ด/บ, บ→ช, หลังลงดึก", height=100)

    with tabs[4]:
        st.text_input("เป้าหมายหลักช่วงนี้", key="lpe10j_main_goal", placeholder="เช่น อ่านสอบให้จบตามแผน")
        st.text_area("วันสอบ / deadline / งานที่พลาดไม่ได้", key="lpe10j_deadline_notes", placeholder="ระบุวันและสิ่งที่ต้องเสร็จ", height=120)
        st.text_area("ตารางอ่าน / แผนเรียน / แผนโปรเจกต์", key="lpe10j_study_plan_notes", placeholder="เช่น 19 มิ.ย.-19 ก.ค. อ่านตามหน่วย", height=120)
        st.text_area("กฎสำหรับโปรเจกต์", key="lpe10j_project_rules", placeholder="เช่น โปรเจกต์ต้องไม่กินเวลานอนและอ่านสอบ", height=100)

    with tabs[5]:
        st.text_area("ลำดับความสำคัญส่วนตัว", key="lpe10j_priority_rules", placeholder="เช่น เวร > นอน > สอบ > โปรเจกต์ > งานรอง", height=100)
        st.text_area("สิ่งที่ระบบไม่ควรทำ/ไม่ควรแนะนำ", key="lpe10j_do_not_do", placeholder="เช่น ไม่เปิด scope ใหม่ตอนใกล้สอบ / ไม่วางงานยาวหลังเลิกบ่าย", height=100)
        st.text_area("เทคนิคที่ช่วยให้ทำสำเร็จ", key="lpe10j_success_techniques", placeholder="เช่น เริ่ม 20 นาที, เตรียมของก่อนเวร, จบวันด้วย next action 1 บรรทัด", height=120)

    with tabs[6]:
        st.slider("พลังงานวันนี้", min_value=1, max_value=5, value=3, key="lpe10j_today_energy")
        st.text_area("วันนี้ต้องทำอะไรให้ได้", key="lpe10j_today_must_do", height=80)
        st.text_input("พรุ่งนี้เวร/งาน/นัดสำคัญ", key="lpe10j_tomorrow_shift", placeholder="เช่น ด, บ, ด/บ, สอบ, เดินทาง")
        st.text_area("พรุ่งนี้ต้องระวังอะไร / ต้องลดอะไร", key="lpe10j_tomorrow_warning", height=100)
        st.text_input("next single action", key="lpe10j_next_action", placeholder="หนึ่งสิ่งที่ต้องทำต่อทันที")

    with tabs[7]:
        profile_snapshot = _lpe10j_profile_snapshot()
        st.success("Profile schema พร้อมใช้เป็นฐานให้ Phase ถัดไป")
        st.json(profile_snapshot)
        st.caption("Phase 10J ยังเป็นชั้นตั้งค่าชีวิต ไม่ใช่ตัว resolver ตารางเวรเต็มรูปแบบ")

    return True


try:
    if _lpe10j_render_life_profile_setup():
        import streamlit as st
        st.stop()
except Exception as _lpe10j_error:
    try:
        import streamlit as st
        st.warning(f"Phase 10J profile setup section skipped: {_lpe10j_error}")
    except Exception:
        pass
# === END_PHASE10J_PROFILE_SETUP_SCHEMA_AND_ADVANCED_SETTINGS_REDESIGN_PATCH_V2 ===
# --- PHASE10G_COMPACT_REAL_TIME_DAILY_SCHEDULE_AND_PREMIUM_STATUS_PATCH_V1 ---
PHASE10G_COMPACT_REAL_TIME_DAILY_SCHEDULE_AND_PREMIUM_STATUS_PATCH_V1 = True

def _lpe10g_apply_premium_light_css():
    st.markdown("""
<style>
.stApp, [data-testid="stAppViewContainer"] { background: radial-gradient(circle at top left, #eef7ff 0, #f4f8fb 34%, #f7fbff 100%) !important; color: #0f2742 !important; }
.block-container { max-width: 1180px !important; padding-top: 1.25rem !important; padding-bottom: 2.2rem !important; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #174a86 0%, #1f5a9d 48%, #174a86 100%) !important; }
section[data-testid="stSidebar"] * { color: #eef7ff !important; }
h1, h2, h3, h4, h5, h6, p, label, span, div { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Tahoma, Arial, sans-serif; }
.lpe10g-hero { background: rgba(255,255,255,.94); border: 1px solid rgba(30,90,168,.16); border-radius: 18px; box-shadow: 0 16px 40px rgba(15,23,42,.07); padding: 20px 24px 18px; margin: 0 0 14px; }
.lpe10g-hero h1 { margin: 0 0 7px; color: #102a43 !important; font-size: 1.95rem; letter-spacing: -.03em; line-height: 1.14; }
.lpe10g-hero p { margin: 0 0 13px; color: #334155 !important; font-size: .99rem; }
.lpe10g-chip-row { display:flex; flex-wrap:wrap; gap:10px; align-items:center; }
.lpe10g-chip { display:inline-flex; align-items:center; border:1px solid rgba(30,90,168,.18); background:#eaf4ff; color:#0f3f77 !important; border-radius:999px; padding:7px 13px; font-weight:750; font-size:.91rem; }
.lpe10g-board-caption { margin: 0 0 10px; color:#53657d !important; font-size:.93rem; }
.lpe10g-grid-head { display:grid; grid-template-columns:.72fr 1.42fr 1.35fr 1.45fr 1.85fr .62fr; gap:10px; margin:8px 0; }
.lpe10g-grid-head div { background:#eaf4ff; color:#173b63 !important; border:1px solid rgba(30,90,168,.14); border-radius:10px; padding:8px 10px; font-weight:850; font-size:.86rem; }
div[data-testid="stVerticalBlockBorderWrapper"] { border:1px solid rgba(30,90,168,.12) !important; border-radius:15px !important; background:rgba(255,255,255,.94) !important; box-shadow:0 8px 22px rgba(15,23,42,.045) !important; padding:.72rem .84rem !important; }
div[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color:rgba(30,90,168,.26) !important; box-shadow:0 12px 28px rgba(15,23,42,.07) !important; }
.lpe10g-time { display:inline-flex; align-items:center; justify-content:center; min-width:64px; padding:6px 9px; border-radius:999px; background:#eef6ff; color:#0f3f77 !important; border:1px solid rgba(30,90,168,.16); font-weight:900; font-size:.92rem; }
.lpe10g-main { color:#0f2742 !important; font-weight:900; font-size:.96rem; line-height:1.35; }
.lpe10g-sub { color:#475569 !important; font-weight:600; font-size:.86rem; line-height:1.42; }
.lpe10g-tip { color:#1f3b57 !important; font-weight:700; font-size:.86rem; line-height:1.46; }
.lpe10g-status-wrap { display:flex; align-items:center; justify-content:center; min-height:38px; }
.stTextInput input, .stTextArea textarea { background:#fff !important; border:1px solid rgba(15,23,42,.20) !important; border-radius:10px !important; color:#0f172a !important; caret-color:#0f172a !important; }
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color:#64748b !important; opacity:1 !important; }
.lpe10g-summary-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin:0 0 16px; }
.lpe10g-metric-card { background:#fff; border:1px solid rgba(30,90,168,.14); border-radius:16px; padding:16px; box-shadow:0 10px 26px rgba(15,23,42,.055); }
.lpe10g-metric-label { color:#64748b !important; font-weight:700; font-size:.9rem; margin-bottom:4px; }
.lpe10g-metric-value { color:#12385f !important; font-weight:950; font-size:1.72rem; letter-spacing:-.035em; }
.lpe10g-card-title { color:#102a43 !important; font-size:1.18rem; font-weight:900; margin:0 0 8px; }
@media (max-width: 900px) { .lpe10g-grid-head { display:none; } .lpe10g-summary-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } }
</style>
    """, unsafe_allow_html=True)

def _lpe10g_schedule_items():
    return [
        {"time":"06:30","task":"ตื่น / ดื่มน้ำ / รับแสงเช้า","food":"น้ำเปล่า 1 แก้ว","why":"เริ่มวันแบบไม่ใช้แรงตัดสินใจเยอะ","tip":"วางน้ำไว้ใกล้เตียงตั้งแต่คืนก่อน"},
        {"time":"07:00","task":"อาบน้ำ / เตรียมไปทำงาน","food":"อาหารเช้าเบา ๆ ถ้าหิว","why":"ลดความเร่งและลดการหลุดแผนตอนเช้า","tip":"เตรียมของออกจากบ้านให้จบก่อนจับมือถือยาว"},
        {"time":"07:30","task":"อาหารเช้า / วิตามินที่ใช้ประจำ","food":"โปรตีนเบา + ข้าว/ผักเล็กน้อย","why":"ช่วยให้อิ่มนานและลดง่วงช่วงต้นงาน","tip":"วิตามินให้ยึดฉลากหรือคำแนะนำผู้เชี่ยวชาญ ถ้าระคายท้องให้กินพร้อมอาหาร"},
        {"time":"08:00","task":"เริ่มงาน / เวรเช้า / งานหลัก 1 อย่าง","food":"กาแฟไม่หวานถ้าจำเป็น","why":"ช่วงแรกของงานเหมาะกับงานที่ต้องใช้สมาธิ","tip":"เริ่มจากงานสำคัญที่สุด 1 อย่างก่อนเปิด scope ใหม่"},
        {"time":"10:30","task":"พักสั้น / รีเซ็ตสมอง","food":"น้ำเปล่า","why":"ลดล้าและกันหลุดโฟกัสยาว","tip":"เดิน 3-5 นาที ไม่ไถมือถือยาว"},
        {"time":"12:00","task":"พักเที่ยง","food":"ข้าว + โปรตีน + ผัก","why":"เติมพลังโดยไม่ทำให้บ่ายง่วงมาก","tip":"กินอิ่มประมาณ 70-80% เลี่ยงทอด/หวานจัดถ้าต้องทำงานต่อ"},
        {"time":"13:00","task":"กลับเข้างาน / งานต่อเนื่อง","food":"น้ำเปล่า","why":"รักษา momentum หลังพักเที่ยง","tip":"ทำรายการเดียวให้จบก่อนเปลี่ยนงาน"},
        {"time":"15:30","task":"พักตา / จัดโต๊ะ / รีโฟกัส","food":"น้ำเปล่า หรือของว่างเบา ๆ ถ้าหิวจริง","why":"กันพลังตกช่วงบ่ายปลาย","tip":"ตั้งเวลา 5 นาที แล้วกลับมาดู next action เดิม"},
        {"time":"17:30","task":"ออกกำลังกาย / เดิน / ยืดเหยียด","food":"น้ำเปล่า ก่อนและหลังออกกำลัง","why":"ช่วยฟื้นตัวและลดความตึงจากงาน","tip":"20-30 นาทีพอ ไม่ต้องหนักทุกวัน"},
        {"time":"19:00","task":"อาหารเย็น / ลดงานหนัก","food":"โปรตีนเบา + ผัก / ลดหวานมัน","why":"ช่วยไม่แน่นท้องก่อนนอน","tip":"เลือกอาหารที่ทำได้จริง ไม่ต้อง perfect"},
        {"time":"21:30","task":"ปิดงาน / สรุปวันนี้ / เตรียมพรุ่งนี้","food":"น้ำเปล่าเล็กน้อย","why":"ลดความคิดค้างก่อนนอน","tip":"เขียน next single action แค่ 1 บรรทัด"},
        {"time":"23:00","task":"เข้านอน","food":"หลีกเลี่ยงมื้อหนักก่อนนอน","why":"เวลานอนสม่ำเสมอช่วยให้วันถัดไปดีขึ้น","tip":"ปิดจอ 30-60 นาที ถ้าทำได้"},
    ]

def _lpe10g_done_count():
    return sum(1 for i, _item in enumerate(_lpe10g_schedule_items()) if st.session_state.get(f"lpe10g_done_{i}", False))

def _lpe10g_sidebar():
    with st.sidebar:
        advanced = st.checkbox("โหมดระบบถูกย้ายไปด้านบน", value=False, key="lpe10g_advanced_legacy")
        st.markdown("### ผู้ช่วยจัดลำดับชีวิต")
        st.caption("daily-use เหลือ 2 หน้า")
        page = st.radio("เมนูหลัก", ["ตารางกิจวัตรประจำวัน", "สรุปวันนี้ / เตรียมพรุ่งนี้"], key="lpe10g_page")
    return advanced, page

def _lpe10g_render_hero(done_count, total_count):
    st.markdown(f"""
<div class="lpe10g-hero"><h1>ตารางกิจวัตรประจำวัน</h1><p>วันนี้ควรทำอะไร เวลาไหน กิน/พักอย่างไร เพราะอะไร และจบแต่ละช่วงด้วยสวิตช์ขวาสุด</p><div class="lpe10g-chip-row"><span class="lpe10g-chip">โหมด: Premium Light Board</span><span class="lpe10g-chip">พลังงาน: 3</span><span class="lpe10g-chip">เป้าหมาย: เลือกงานหลัก 1 อย่าง</span><span class="lpe10g-chip">ทำแล้ว: {done_count}/{total_count}</span></div></div>
    """, unsafe_allow_html=True)

def _lpe10g_render_daily_board():
    items = _lpe10g_schedule_items()
    done_count = _lpe10g_done_count()
    _lpe10g_render_hero(done_count, len(items))
    st.markdown('<p class="lpe10g-board-caption">ตารางจริงทั้งวัน: หนึ่งแถวคือหนึ่งช่วงเวลา อ่านจากซ้ายไปขวา แล้วเลื่อนสวิตช์ขวาสุดเมื่อทำเสร็จ</p>', unsafe_allow_html=True)
    st.markdown('<div class="lpe10g-grid-head"><div>เวลา</div><div>ทำอะไร</div><div>กิน / เสริม / พัก</div><div>เพราะอะไร</div><div>เทคนิค / คำแนะนำ</div><div>สถานะ</div></div>', unsafe_allow_html=True)
    for i, item in enumerate(items):
        with st.container(border=True):
            c_time, c_task, c_food, c_why, c_tip, c_status = st.columns([0.72, 1.42, 1.35, 1.45, 1.85, 0.62], gap="small")
            with c_time:
                st.markdown(f'<div class="lpe10g-time">{item["time"]}</div>', unsafe_allow_html=True)
            with c_task:
                st.markdown(f'<div class="lpe10g-main">{item["task"]}</div>', unsafe_allow_html=True)
            with c_food:
                st.markdown(f'<div class="lpe10g-sub">{item["food"]}</div>', unsafe_allow_html=True)
            with c_why:
                st.markdown(f'<div class="lpe10g-sub">{item["why"]}</div>', unsafe_allow_html=True)
            with c_tip:
                st.markdown(f'<div class="lpe10g-tip">{item["tip"]}</div>', unsafe_allow_html=True)
            with c_status:
                st.markdown('<div class="lpe10g-status-wrap">', unsafe_allow_html=True)
                st.toggle("สถานะ", key=f"lpe10g_done_{i}", label_visibility="collapsed")
                st.markdown('</div>', unsafe_allow_html=True)
    done_count = _lpe10g_done_count()
    st.progress(done_count / len(items) if items else 0, text=f"ทำแล้ว {done_count}/{len(items)} ช่วงเวลา")

def _lpe10g_render_summary():
    items = _lpe10g_schedule_items()
    done_count = _lpe10g_done_count()
    _lpe10g_render_hero(done_count, len(items))
    st.markdown(f'<div class="lpe10g-summary-grid"><div class="lpe10g-metric-card"><div class="lpe10g-metric-label">ทำแล้ววันนี้</div><div class="lpe10g-metric-value">{done_count}/{len(items)}</div></div><div class="lpe10g-metric-card"><div class="lpe10g-metric-label">โหมดวันนี้</div><div class="lpe10g-metric-value">Light</div></div><div class="lpe10g-metric-card"><div class="lpe10g-metric-label">พลังงานตั้งต้น</div><div class="lpe10g-metric-value">3</div></div><div class="lpe10g-metric-card"><div class="lpe10g-metric-label">เป้าหมาย</div><div class="lpe10g-metric-value">1 งาน</div></div></div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="lpe10g-card-title">สรุปวันนี้</div>', unsafe_allow_html=True)
        a, b = st.columns([1, 1], gap="large")
        with a:
            st.selectbox("วันนี้โดยรวม", ["ยังไม่สรุป", "ดี", "พอใช้", "เหนื่อย", "หลุดแผน"], key="lpe10g_today_summary")
        with b:
            st.slider("พลังงานท้ายวัน", 1, 5, 3, key="lpe10g_end_energy")
    with st.container(border=True):
        st.markdown('<div class="lpe10g-card-title">เตรียมพรุ่งนี้</div>', unsafe_allow_html=True)
        a, b = st.columns([1, 1], gap="large")
        with a:
            st.selectbox("พรุ่งนี้เวรอะไร", ["ยังไม่ระบุ", "หยุด", "เวรเช้า", "เวรบ่าย", "เวรดึก", "อ่านสอบ/งานส่วนตัว"], key="lpe10g_tomorrow_shift")
        with b:
            st.text_input("พรุ่งนี้ต้องทำอะไรเป็นอันดับ 1", placeholder="เช่น งานหลัก / พัก / อ่านหนังสือ", key="lpe10g_tomorrow_top")
        st.text_input("Next single action ตอนเปิดเว็บครั้งถัดไป", placeholder="สั้น ๆ เช่น เปิดตาราง -> ทำช่วงเวลาแรก", key="lpe10g_next_action")
        st.text_area("หมายเหตุเสริม (ไม่บังคับ)", placeholder="สั้น ๆ ก็พอ", height=80, key="lpe10g_extra_note")

try:
    _lpe10g_apply_premium_light_css()
    _lpe10g_advanced, _lpe10g_page = _lpe10g_sidebar()
    if not _lpe10g_advanced:
        if _lpe10g_page == "ตารางกิจวัตรประจำวัน":
            _lpe10g_render_daily_board()
        else:
            _lpe10g_render_summary()
        st.stop()
except Exception as _lpe10g_exception:
    st.error("Phase 10G UI error: compact daily schedule could not render.")
    st.exception(_lpe10g_exception)
    st.stop()
# --- END PHASE10G_COMPACT_REAL_TIME_DAILY_SCHEDULE_AND_PREMIUM_STATUS_PATCH_V1 ---


# PHASE10F_UNIFIED_LIGHT_ROW_CARD_ACTION_TABLE_V1
# Scope: two daily-use pages, light row-card action table, short note in row, status checkbox on right, no database/cloud/API.
def _lpe10f_apply_light_action_board_style():
    st.markdown("""
<style>
:root {
  --lpe10f-navy: #0f2f57;
  --lpe10f-text: #102033;
  --lpe10f-muted: #53657a;
  --lpe10f-line: #d6e3f1;
  --lpe10f-card: #ffffff;
  --lpe10f-bg: #f3f8fd;
  --lpe10f-blue-soft: #eaf4ff;
  --lpe10f-green-soft: #e9f9ef;
  --lpe10f-green-line: #90d5a3;
  --lpe10f-gray-soft: #f8fafc;
}
.stApp { background: var(--lpe10f-bg) !important; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #194b86 0%, #215b9d 100%) !important; }
section[data-testid="stSidebar"] * { color: #ffffff !important; }
.block-container { max-width: 1280px !important; padding-top: 2.2rem !important; }
.lpe10f-hero, .lpe10f-card, .lpe10f-section {
  background: var(--lpe10f-card);
  border: 1px solid var(--lpe10f-line);
  border-radius: 22px;
  box-shadow: 0 18px 42px rgba(25, 75, 134, 0.08);
  padding: 24px 28px;
  margin-bottom: 18px;
}
.lpe10f-hero h1 { color: var(--lpe10f-navy); font-size: 2rem; margin: 0 0 8px 0; line-height: 1.2; }
.lpe10f-hero p, .lpe10f-section p { color: var(--lpe10f-text); margin: 0 0 10px 0; }
.lpe10f-chip-row { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 12px; }
.lpe10f-chip { display: inline-block; background: var(--lpe10f-blue-soft); color: var(--lpe10f-navy); border: 1px solid #c9def6; border-radius: 999px; padding: 7px 14px; font-weight: 700; font-size: 0.92rem; }
.lpe10f-table-title { color: var(--lpe10f-navy); font-size: 1.35rem; font-weight: 800; margin: 4px 0 4px 0; }
.lpe10f-help { color: var(--lpe10f-muted); font-size: 0.92rem; margin-bottom: 12px; }
.lpe10f-head {
  background: #e8f2fc;
  color: var(--lpe10f-navy);
  border: 1px solid var(--lpe10f-line);
  border-radius: 12px;
  padding: 10px 12px;
  font-weight: 800;
  min-height: 42px;
}
.lpe10f-cell-title { color: var(--lpe10f-navy); font-weight: 800; font-size: 0.97rem; margin-bottom: 2px; }
.lpe10f-cell-body { color: var(--lpe10f-text); font-size: 0.94rem; line-height: 1.45; }
.lpe10f-row-caption { color: var(--lpe10f-muted); font-size: 0.84rem; }
div[data-testid="stVerticalBlockBorderWrapper"] {
  background: #ffffff !important;
  border-color: var(--lpe10f-line) !important;
  border-radius: 16px !important;
  box-shadow: 0 6px 18px rgba(16, 32, 51, 0.04) !important;
}
.stTextInput input, .stTextArea textarea, div[data-baseweb="select"] > div {
  background-color: #ffffff !important;
  color: #102033 !important;
  border: 1px solid #b8c9dc !important;
  border-radius: 10px !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
  color: #66788e !important;
  opacity: 1 !important;
}
label, .stMarkdown, .stCaption, .stText { color: #102033 !important; }
.stCheckbox label p { color: var(--lpe10f-navy) !important; font-weight: 800 !important; }
.lpe10f-status-done { background: var(--lpe10f-green-soft); border: 1px solid var(--lpe10f-green-line); color: #166534; border-radius: 999px; padding: 5px 10px; font-weight: 800; display: inline-block; margin-top: 4px; }
.lpe10f-status-todo { background: #f1f5f9; border: 1px solid #cbd5e1; color: #334155; border-radius: 999px; padding: 5px 10px; font-weight: 800; display: inline-block; margin-top: 4px; }
.lpe10f-summary-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.lpe10f-mini-card { background: #ffffff; border: 1px solid var(--lpe10f-line); border-radius: 16px; padding: 16px; }
.lpe10f-mini-card b { color: var(--lpe10f-navy); }
@media (max-width: 900px) { .lpe10f-summary-grid { grid-template-columns: 1fr; } }
</style>
""", unsafe_allow_html=True)


def _lpe10f_default_tasks():
    return [
        {"time": "ช่วงงาน/เวร", "task": "งานหลัก / เวร", "why": "งานหลักที่ดีไม่ใช่ดีอย่างเดียว ต้องมาก่อนงานเสริม", "tip": "ก่อนเข้าเวรอย่าเปิด scope ใหม่ ให้เลือกงานที่ปิดจบได้จริง"},
        {"time": "ท้ายวัน", "task": "ปิดวันและเตรียมพรุ่งนี้", "why": "ทำให้วันถัดไปเริ่มต่อได้ทันที", "tip": "จด next single action เพียง 1 อย่างก็พอ"},
        {"time": "เช้า", "task": "อ่านหนังสือ 20-30 นาที", "why": "งานอ่านสอบมี deadline และต้องกันไว้ก่อนโปรเจกต์", "tip": "ใช้ timer 25 นาที แล้วหยุดพักสั้นเพื่อให้เริ่มง่าย"},
        {"time": "เย็น", "task": "อาหารเบา / ลดหวาน / ลดมื้อหนัก", "why": "ช่วยลดอาการหนักท้องและปกป้องเวลานอน", "tip": "เลือกอาหารง่ายที่ทำจริง เช่น ไข่ ผัก โปรตีนเบา"},
        {"time": "หลังตื่น", "task": "ดื่มน้ำ / ตั้งหลัก / เปิดแผนวันนี้", "why": "ลดความเปลืองพลังตั้งต้นและเริ่มวันแบบไม่ใช้แรงเกิน", "tip": "วางน้ำไว้ใกล้ตัวและเริ่มจากงานเล็กที่สุด"},
    ]


def _lpe10f_done_key(i):
    return "lpe10f_done_" + str(i)


def _lpe10f_note_key(i):
    return "lpe10f_note_" + str(i)


def _lpe10f_completed_count(tasks):
    return sum(1 for i, _ in enumerate(tasks) if st.session_state.get(_lpe10f_done_key(i), False))


def _lpe10f_render_hero(title, subtitle, chips):
    chip_html = "".join(["<span class='lpe10f-chip'>" + str(c) + "</span>" for c in chips])
    st.markdown(
        "<div class='lpe10f-hero'><h1>" + title + "</h1><p>" + subtitle + "</p><div class='lpe10f-chip-row'>" + chip_html + "</div></div>",
        unsafe_allow_html=True,
    )


def _lpe10f_render_action_board():
    tasks = _lpe10f_default_tasks()
    done_count = _lpe10f_completed_count(tasks)
    _lpe10f_render_hero(
        "ตารางกิจวัติประจำวัน",
        "เปิดหน้านี้แล้วรู้ทันทีว่าวันนี้ควรทำอะไร เพราะอะไร และมีเทคนิคอะไรที่ช่วยทำจริง",
        ["โหมด: Light Action Board", "พลังงาน: 3", "เป้าหมาย: เลือกงานหลัก 1 อย่าง", "ทำแล้ว: " + str(done_count) + "/" + str(len(tasks))],
    )
    st.markdown("<div class='lpe10f-section'><div class='lpe10f-table-title'>ตารางวันนี้</div><div class='lpe10f-help'>หนึ่งแถวคือหนึ่งงาน อ่านจากซ้ายไปขวา แล้วติ๊กทำแล้วที่ขวาสุด</div>", unsafe_allow_html=True)
    h = st.columns([1.0, 2.0, 2.6, 3.2, 2.1, 1.35], gap="small")
    headers = ["เวลา", "ทำอะไร", "เพราะอะไร", "เทคนิค/คำแนะนำ", "หมายเหตุสั้น", "สถานะ"]
    for col, label in zip(h, headers):
        with col:
            st.markdown("<div class='lpe10f-head'>" + label + "</div>", unsafe_allow_html=True)
    for i, item in enumerate(tasks):
        done = bool(st.session_state.get(_lpe10f_done_key(i), False))
        with st.container(border=True):
            c = st.columns([1.0, 2.0, 2.6, 3.2, 2.1, 1.35], gap="small")
            with c[0]:
                st.markdown("<div class='lpe10f-cell-title'>" + item["time"] + "</div>", unsafe_allow_html=True)
            with c[1]:
                st.markdown("<div class='lpe10f-cell-title'>" + item["task"] + "</div>", unsafe_allow_html=True)
            with c[2]:
                st.markdown("<div class='lpe10f-cell-body'>" + item["why"] + "</div>", unsafe_allow_html=True)
            with c[3]:
                st.markdown("<div class='lpe10f-cell-body'>" + item["tip"] + "</div>", unsafe_allow_html=True)
            with c[4]:
                st.text_input("หมายเหตุสั้น " + str(i + 1), key=_lpe10f_note_key(i), placeholder="สั้น ๆ เช่น ง่วง / ติดงาน / ทำครึ่งเดียว", label_visibility="collapsed")
            with c[5]:
                st.checkbox("ทำแล้ว", key=_lpe10f_done_key(i))
                if done:
                    st.markdown("<span class='lpe10f-status-done'>ทำแล้ว</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='lpe10f-status-todo'>ยังไม่ทำ</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    done_count = _lpe10f_completed_count(tasks)
    st.progress(done_count / max(len(tasks), 1))
    st.caption("ทำแล้ว " + str(done_count) + "/" + str(len(tasks)) + " รายการ")


def _lpe10f_render_reflection_page():
    tasks = _lpe10f_default_tasks()
    done_count = _lpe10f_completed_count(tasks)
    _lpe10f_render_hero(
        "สรุปวันนี้ / เตรียมพรุ่งนี้",
        "กรอกเฉพาะข้อมูลสำคัญ ไม่ต้องเขียนยาว ระบบใช้สถานะจากตารางวันนี้ช่วยสรุป",
        ["วันนี้ทำแล้ว: " + str(done_count) + "/" + str(len(tasks))],
    )
    st.markdown("<div class='lpe10f-card'><div class='lpe10f-summary-grid'><div class='lpe10f-mini-card'><b>ผลจากตารางวันนี้</b><br>ทำแล้ว " + str(done_count) + "/" + str(len(tasks)) + " รายการ</div><div class='lpe10f-mini-card'><b>หลักวันนี้</b><br>สรุปสั้นพอ ไม่ต้องทำแบบฟอร์มยาว</div><div class='lpe10f-mini-card'><b>หลักพรุ่งนี้</b><br>เลือก next single action เพียงอย่างเดียว</div></div></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.selectbox("วันนี้โดยรวม", ["ยังไม่สรุป", "ดี", "พอใช้", "เหนื่อย", "หลุดแผน"], key="lpe10f_today_summary")
        st.slider("พลังงานท้ายวัน", 1, 5, 3, key="lpe10f_end_energy")
    with c2:
        st.selectbox("พรุ่งนี้มีอะไร", ["ยังไม่ระบุ", "เวร", "หยุด", "อ่านสอบ", "โปรเจกต์", "ธุระส่วนตัว"], key="lpe10f_tomorrow_type")
        st.text_input("พรุ่งนี้ต้องทำอะไรเป็นอันดับ 1", key="lpe10f_tomorrow_priority", placeholder="เช่น อ่านบทถัดไป / พัก / งานหลัก")
    st.text_input("Next single action ตอนเปิดเว็บครั้งถัดไป", key="lpe10f_next_single_action", placeholder="เช่น เปิดเว็บ -> ดูตาราง -> ทำรายการแรก")
    st.text_area("หมายเหตุเสริม (ไม่บังคับ)", key="lpe10f_optional_note", placeholder="สั้น ๆ ก็พอ", height=100)


def _lpe10f_main():
    _lpe10f_apply_light_action_board_style()
    st.sidebar.markdown("### ผู้ช่วยจัดลำดับชีวิต")
    st.sidebar.caption("daily-use เหลือ 2 หน้า")
    page = st.sidebar.radio("เมนูหลัก", ["ตารางกิจวัติประจำวัน", "สรุปวันนี้ / เตรียมพรุ่งนี้"], key="lpe10f_page")
    if page == "ตารางกิจวัติประจำวัน":
        _lpe10f_render_action_board()
    else:
        _lpe10f_render_reflection_page()


_lpe10f_legacy_mode = st.sidebar.checkbox("โหมดระบบถูกย้ายไปด้านบน", value=False, key="lpe10f_legacy_advanced_mode")
if not _lpe10f_legacy_mode:
    _lpe10f_main()
    st.stop()
# PHASE10F_DEFAULT_UI_STOPS_BEFORE_LEGACY_V1



# === PHASE10E_REPAIR4_MARKER: Daily board row layout and form contrast patch ===
def _lpe_phase10e_repair4_enabled():
    import streamlit as st
    try:
        if st.sidebar.checkbox("โหมดระบบถูกย้ายไปด้านบน", value=False, key="lpe10e_show_legacy"):
            return False
    except Exception:
        return True
    return True

def _lpe_phase10e_repair4_style():
    import streamlit as st
    st.markdown("""
<style>
:root { --lpe-bg:#f6faff; --lpe-card:#ffffff; --lpe-border:#d6e2ef; --lpe-text:#1f2937; --lpe-muted:#475569; --lpe-blue:#1f4e8c; --lpe-blue-soft:#eaf4ff; --lpe-green:#22c55e; --lpe-gray:#94a3b8; }
.stApp { background: var(--lpe-bg); color: var(--lpe-text); }
section[data-testid="stSidebar"] { background: linear-gradient(180deg,#173b6d 0%,#1f4e8c 100%); }
section[data-testid="stSidebar"] * { color: #ffffff !important; }
.lpe10e-hero { background:#ffffff; border:1px solid var(--lpe-border); border-radius:18px; padding:20px 24px; margin:6px 0 18px 0; box-shadow:0 10px 28px rgba(15,23,42,.06); }
.lpe10e-hero h1 { color:#12315a; font-size:30px; margin:0 0 8px 0; line-height:1.2; }
.lpe10e-hero p { color:#475569; margin:0; font-size:15px; }
.lpe10e-chip-row { display:flex; flex-wrap:wrap; gap:8px; margin-top:14px; }
.lpe10e-chip { display:inline-flex; align-items:center; border:1px solid #cfe0f5; background:#eaf4ff; color:#15335d; border-radius:999px; padding:6px 12px; font-weight:700; font-size:13px; }
.lpe10e-panel { background:#ffffff; border:1px solid var(--lpe-border); border-radius:16px; padding:16px; margin:12px 0; box-shadow:0 8px 18px rgba(15,23,42,.045); }
.lpe10e-panel-title { color:#12315a; font-size:18px; font-weight:800; margin-bottom:8px; }
.lpe10e-note { color:#475569; font-size:13px; margin-top:4px; }
.stTextInput label, .stTextArea label, .stSelectbox label, .stSlider label, .stNumberInput label { color:#1f2937 !important; font-weight:700 !important; }
.stTextInput input, .stTextArea textarea, .stNumberInput input { background:#ffffff !important; color:#111827 !important; border:1px solid #cbd5e1 !important; border-radius:10px !important; }
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color:#64748b !important; opacity:1 !important; }
[data-testid="stDataFrame"] { border:1px solid var(--lpe-border); border-radius:16px; overflow:hidden; background:#ffffff; }
.lpe10e-status-help { color:#334155; font-size:13px; margin:6px 0 10px 0; }
</style>
""", unsafe_allow_html=True)

def _lpe_phase10e_repair4_rows():
    import streamlit as st
    ctx = st.session_state.get("lpe_version_a_daily_context", {}) or st.session_state.get("daily_context", {}) or {}
    timetable = st.session_state.get("lpe_version_a_daily_timetable_result", {}) or st.session_state.get("daily_timetable_result", {}) or {}
    blocks = timetable.get("blocks") or []
    rows = []
    for b in blocks:
        rows.append({
            "เวลา": str(b.get("เวลา", "")),
            "ทำอะไร": str(b.get("ทำอะไร", "")),
            "เพราะอะไร": str(b.get("เหตุผล", "")),
            "เทคนิค/คำแนะนำ": str(b.get("ถ้าเหนื่อยมาก", "")) or "ทำให้เล็กลงและเริ่มจากขั้นแรกที่ง่ายที่สุด",
            "หมายเหตุสั้น": "",
            "ทำแล้ว": False,
        })
    if not rows:
        rows = [
            {"เวลา":"หลังตื่น", "ทำอะไร":"ดื่มน้ำ / ตั้งหลัก / เปิดแผนวันนี้", "เพราะอะไร":"ลดความเบลอหลังตื่นและเริ่มวันแบบไม่ใช้แรงเกิน", "เทคนิค/คำแนะนำ":"วางน้ำไว้ใกล้ตัวและเริ่มจากงานเล็กที่สุด", "หมายเหตุสั้น":"", "ทำแล้ว":False},
            {"เวลา":"เช้า", "ทำอะไร": ctx.get("study_focus") or "อ่านหนังสือ 20-30 นาที", "เพราะอะไร":"งานอ่านสอบมี deadline และต้องกันไว้ก่อนโปรเจกต์", "เทคนิค/คำแนะนำ":"ใช้ timer 25 นาที แล้วหยุดพักสั้นเพื่อให้เริ่มง่าย", "หมายเหตุสั้น":"", "ทำแล้ว":False},
            {"เวลา":"ช่วงงาน/เวร", "ทำอะไร": ctx.get("today_shift") or "งานหลัก / เวร", "เพราะอะไร":"งานหลักหลีกไม่ได้ ต้องมาก่อนงานเสริม", "เทคนิค/คำแนะนำ":"ก่อนเข้าเวรอย่าเปิด scope ใหม่", "หมายเหตุสั้น":"", "ทำแล้ว":False},
            {"เวลา":"เย็น", "ทำอะไร":"อาหารเบา / ลดหวาน / ลดมื้อหนัก", "เพราะอะไร":"ช่วยลดอาการหนักท้องและปกป้องเวลานอน", "เทคนิค/คำแนะนำ":"เลือกอาหารง่ายที่มีจริง เช่น ไข่ ผัก โปรตีนเบา", "หมายเหตุสั้น":"", "ทำแล้ว":False},
            {"เวลา":"ท้ายวัน", "ทำอะไร":"ปิดวันและเตรียมพรุ่งนี้", "เพราะอะไร":"ทำให้วันถัดไปเริ่มต่อได้ทันที", "เทคนิค/คำแนะนำ":"จด next single action เพียง 1 อย่างก็พอ", "หมายเหตุสั้น":"", "ทำแล้ว":False},
        ]
    return rows

def _lpe_phase10e_repair4_render_board():
    import streamlit as st
    import pandas as pd
    _lpe_phase10e_repair4_style()
    ctx = st.session_state.get("lpe_version_a_daily_context", {}) or st.session_state.get("daily_context", {}) or {}
    mode = "Yellow / Controlled Day"
    energy = ctx.get("energy_level", 3)
    focus = ctx.get("primary_focus", "เลือกงานหลัก 1 อย่าง")
    st.markdown("<div class='lpe10e-hero'><h1>ตารางกิจวัติประจำวัน</h1><p>เปิดหน้านี้แล้วรู้ทันทีว่าวันนี้ควรทำอะไร เพราะอะไร และมีเทคนิคอะไรที่ช่วยทำจริง</p><div class='lpe10e-chip-row'><span class='lpe10e-chip'>โหมด: " + str(mode) + "</span><span class='lpe10e-chip'>พลังงาน: " + str(energy) + "</span><span class='lpe10e-chip'>เป้าหมาย: " + str(focus) + "</span></div></div>", unsafe_allow_html=True)
    st.markdown("<div class='lpe10e-panel'><div class='lpe10e-panel-title'>ตารางวันนี้</div><div class='lpe10e-note'>หนึ่งแถวคือหนึ่งงาน: อ่านแผนจากซ้ายไปขวา แล้วติ๊กทำแล้วที่คอลัมน์ขวาสุด</div></div>", unsafe_allow_html=True)
    key = "lpe_phase10e_repair4_action_rows"
    if key not in st.session_state:
        st.session_state[key] = _lpe_phase10e_repair4_rows()
    df = pd.DataFrame(st.session_state[key])
    edited = st.data_editor(
        df,
        key="lpe_phase10e_repair4_data_editor",
        hide_index=True,
        use_container_width=True,
        height=min(520, 84 + max(1, len(df)) * 62),
        column_order=["เวลา", "ทำอะไร", "เพราะอะไร", "เทคนิค/คำแนะนำ", "หมายเหตุสั้น", "ทำแล้ว"],
        column_config={
            "เวลา": st.column_config.TextColumn("เวลา", width="small"),
            "ทำอะไร": st.column_config.TextColumn("ทำอะไร", width="medium"),
            "เพราะอะไร": st.column_config.TextColumn("เพราะอะไร", width="medium"),
            "เทคนิค/คำแนะนำ": st.column_config.TextColumn("เทคนิค/คำแนะนำ", width="large"),
            "หมายเหตุสั้น": st.column_config.TextColumn("หมายเหตุสั้น", width="medium"),
            "ทำแล้ว": st.column_config.CheckboxColumn("ทำแล้ว", width="small"),
        },
        disabled=["เวลา", "ทำอะไร", "เพราะอะไร", "เทคนิค/คำแนะนำ"],
    )
    rows = edited.to_dict("records") if hasattr(edited, "to_dict") else list(edited)
    st.session_state[key] = rows
    done = sum(1 for r in rows if bool(r.get("ทำแล้ว")))
    total = max(1, len(rows))
    st.progress(done / total)
    st.caption(f"ทำแล้ว {done}/{total} รายการ")
    st.session_state["lpe_phase10e_repair4_board_result"] = {"rows": rows, "done": done, "total": total, "schema_version":"lpe_phase10e_repair4_daily_board_v1"}

def _lpe_phase10e_repair4_render_summary():
    import streamlit as st
    _lpe_phase10e_repair4_style()
    st.markdown("<div class='lpe10e-hero'><h1>สรุปวันนี้ / เตรียมพรุ่งนี้</h1><p>กรอกเฉพาะข้อมูลสำคัญ ไม่ต้องเขียนยาว ระบบใช้สถานะจากตารางช่วยสรุป</p></div>", unsafe_allow_html=True)
    board = st.session_state.get("lpe_phase10e_repair4_board_result", {})
    done = board.get("done", 0); total = board.get("total", 0)
    st.markdown(f"<div class='lpe10e-panel'><div class='lpe10e-panel-title'>ผลจากตารางวันนี้</div><div class='lpe10e-note'>ทำแล้ว {done}/{total} รายการ</div></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        day_result = st.selectbox("วันนี้โดยรวม", ["ดี", "กลาง", "แย่"], key="lpe10e_day_result")
        end_energy = st.slider("พลังงานท้ายวัน", 1, 5, 3, key="lpe10e_end_energy")
    with c2:
        tomorrow_shift = st.selectbox("พรุ่งนี้เวรอะไร", ["ไม่แน่ใจ", "หยุด", "เวรเช้า", "เวรบ่าย", "เวรดึก"], key="lpe10e_tomorrow_shift")
        tomorrow_must = st.text_input("พรุ่งนี้ต้องทำอะไรอันดับ 1", key="lpe10e_tomorrow_must", placeholder="เช่น อ่านบทถัดไป / พัก / งานหลัก")
    next_action = st.text_input("Next single action", key="lpe10e_next_single_action", placeholder="เปิดเว็บ -> ดูตาราง -> ทำรายการแรก")
    note = st.text_input("หมายเหตุเสริม (ไม่บังคับ)", key="lpe10e_optional_note", placeholder="สั้น ๆ ก็พอ")
    st.session_state["lpe_phase10e_repair4_quick_reflection"] = {"day_result":day_result,"end_energy":end_energy,"tomorrow_shift":tomorrow_shift,"tomorrow_must":tomorrow_must,"next_single_action":next_action,"note":note,"schema_version":"lpe_phase10e_repair4_quick_reflection_v1"}

def _lpe_phase10e_repair4_bootstrap():
    import streamlit as st
    if not _lpe_phase10e_repair4_enabled():
        return False
    page = st.sidebar.radio("เมนูหลัก", ["ตารางกิจวัติประจำวัน", "สรุปวันนี้ / เตรียมพรุ่งนี้"], key="lpe_phase10e_repair4_nav")
    if page == "ตารางกิจวัติประจำวัน":
        _lpe_phase10e_repair4_render_board()
    else:
        _lpe_phase10e_repair4_render_summary()
    st.stop()
    return True

_lpe_phase10e_repair4_bootstrap()
# === END PHASE10E_REPAIR4_MARKER ===


# PHASE10D_DAILY_BOARD_TABLE_VISUAL_POLISH_V1_START
# Owner visual review goal: make the Daily Action Board table look professional, clean, framed, and readable.
def _lpe_phase10d_apply_daily_board_visual_polish():
    st.markdown("""
    <style>
      /* PHASE10D_DAILY_BOARD_TABLE_VISUAL_POLISH_V1 */
      :root {
        --lpe-bg: #F6FAFF;
        --lpe-card: #FFFFFF;
        --lpe-sidebar: #1F4E8C;
        --lpe-sidebar-2: #163B6E;
        --lpe-ink: #1F2937;
        --lpe-muted: #64748B;
        --lpe-line: #D6E2EF;
        --lpe-head: #EAF4FF;
        --lpe-blue: #2563EB;
        --lpe-green: #22C55E;
        --lpe-gray: #CBD5E1;
        --lpe-warning: #FFF7D6;
      }
      .stApp { background: var(--lpe-bg) !important; color: var(--lpe-ink) !important; }
      .block-container { padding-top: 2.0rem !important; padding-bottom: 2rem !important; max-width: 1500px !important; }
      section[data-testid="stSidebar"] { background: linear-gradient(180deg, var(--lpe-sidebar), var(--lpe-sidebar-2)) !important; }
      section[data-testid="stSidebar"] * { color: #F8FBFF !important; }
      section[data-testid="stSidebar"] .stRadio label,
      section[data-testid="stSidebar"] .stCheckbox label { color: #F8FBFF !important; }

      /* Light form controls: remove dark leftover controls from previous phases */
      div[data-testid="stTextInput"] input,
      div[data-testid="stNumberInput"] input,
      div[data-testid="stTextArea"] textarea,
      div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
      div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
        background: #FFFFFF !important;
        color: var(--lpe-ink) !important;
        border: 1px solid var(--lpe-line) !important;
        border-radius: 10px !important;
        box-shadow: none !important;
      }
      div[data-testid="stTextInput"] input:focus,
      div[data-testid="stNumberInput"] input:focus,
      div[data-testid="stTextArea"] textarea:focus {
        border-color: #93C5FD !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
      }
      div[data-testid="stSelectbox"] [data-baseweb="select"] span,
      div[data-testid="stSelectbox"] [data-baseweb="select"] div {
        color: var(--lpe-ink) !important;
      }

      /* Cards / alerts */
      div[data-testid="stAlert"] {
        border-radius: 14px !important;
        border: 1px solid #F8D678 !important;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06) !important;
      }
      [data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid var(--lpe-line) !important;
        border-radius: 16px !important;
        padding: 14px 16px !important;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05) !important;
      }

      /* Professional Daily Board table */
      table {
        width: 100% !important;
        border-collapse: separate !important;
        border-spacing: 0 !important;
        background: var(--lpe-card) !important;
        border: 1px solid var(--lpe-line) !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 14px 38px rgba(15, 23, 42, 0.07) !important;
        table-layout: fixed !important;
      }
      thead tr, table tr:first-child {
        background: var(--lpe-head) !important;
      }
      th {
        background: var(--lpe-head) !important;
        color: #173B68 !important;
        font-weight: 800 !important;
        font-size: 0.94rem !important;
        line-height: 1.35 !important;
        padding: 15px 16px !important;
        border-bottom: 1px solid var(--lpe-line) !important;
        border-right: 1px solid var(--lpe-line) !important;
        vertical-align: top !important;
      }
      td {
        background: #FFFFFF !important;
        color: var(--lpe-ink) !important;
        font-size: 0.95rem !important;
        line-height: 1.55 !important;
        padding: 16px !important;
        border-bottom: 1px solid var(--lpe-line) !important;
        border-right: 1px solid var(--lpe-line) !important;
        vertical-align: top !important;
        overflow-wrap: anywhere !important;
      }
      tr:nth-child(even) td { background: #FBFDFF !important; }
      tr:hover td { background: #F2F8FF !important; }
      th:last-child, td:last-child { border-right: none !important; }
      tr:last-child td { border-bottom: none !important; }

      /* Column proportions for the action table. Works with regular markdown/html tables. */
      table th:nth-child(1), table td:nth-child(1) { width: 12% !important; font-weight: 800 !important; color: #0F3F72 !important; }
      table th:nth-child(2), table td:nth-child(2) { width: 22% !important; font-weight: 700 !important; }
      table th:nth-child(3), table td:nth-child(3) { width: 24% !important; }
      table th:nth-child(4), table td:nth-child(4) { width: 30% !important; }
      table th:nth-child(5), table td:nth-child(5) { width: 12% !important; text-align: center !important; }

      /* Toggle/status area: reduce default awkwardness */
      div[data-testid="stToggle"] {
        background: #F8FAFC !important;
        border: 1px solid var(--lpe-line) !important;
        border-radius: 999px !important;
        padding: 6px 10px !important;
        width: fit-content !important;
        min-width: 118px !important;
      }
      div[data-testid="stToggle"] label p { color: var(--lpe-ink) !important; font-weight: 700 !important; }
      div[data-testid="stToggle"] [role="switch"][aria-checked="true"] { background: var(--lpe-green) !important; }
      div[data-testid="stToggle"] [role="switch"][aria-checked="false"] { background: var(--lpe-gray) !important; }
      div[data-testid="stCheckbox"] label { color: var(--lpe-ink) !important; font-weight: 700 !important; }

      /* Daily board content rhythm */
      h1, h2, h3 { color: #0F2F57 !important; letter-spacing: -0.02em !important; }
      p, li { color: var(--lpe-ink) !important; }
      hr { border-color: var(--lpe-line) !important; }

      /* Small chips / pills if markdown HTML exists */
      .lpe-chip, .lpe-pill, .lpe-phase10c-chip {
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        background: #EAF4FF !important;
        color: #17426F !important;
        border: 1px solid #BFDBFE !important;
        border-radius: 999px !important;
        padding: 7px 12px !important;
        font-weight: 800 !important;
        font-size: 0.88rem !important;
        margin: 3px 6px 3px 0 !important;
      }
      .lpe-card, .lpe-board-card, .lpe-summary-card {
        background: #FFFFFF !important;
        border: 1px solid var(--lpe-line) !important;
        border-radius: 18px !important;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.07) !important;
      }

      /* Remove visual noise from helper text where possible */
      .stCaptionContainer, small { color: var(--lpe-muted) !important; }

      @media (max-width: 900px) {
        .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
        table { table-layout: auto !important; font-size: 0.9rem !important; }
        th, td { padding: 11px !important; }
      }
    </style>
    """, unsafe_allow_html=True)

_lpe_phase10d_apply_daily_board_visual_polish()
# PHASE10D_DAILY_BOARD_TABLE_VISUAL_POLISH_V1_END



# === LPE_VERSION_A_PHASE10C_TWO_PAGE_DAILY_BOARD_NAV_TABLE_REDESIGN_V1 START ===
# Owner visual review pivot: two daily-use pages, side navigation, table-first light dashboard.
# Scope: app.py local UI only; no account, remote sync, cloud storage, database, external model/API, notification, or deployment.

def _lpe_phase10c_apply_light_dashboard_style():
    st.markdown("""
    <style>
    :root {
      --lpe-bg: #f4f8fc;
      --lpe-panel: #ffffff;
      --lpe-panel-soft: #f7fbff;
      --lpe-line: #d9e4ee;
      --lpe-text: #17212b;
      --lpe-muted: #5f6f7f;
      --lpe-blue: #2563eb;
      --lpe-blue-soft: #eaf3ff;
      --lpe-green: #18a058;
      --lpe-green-soft: #e8f8ef;
      --lpe-gray: #e5e7eb;
      --lpe-yellow: #fff6d6;
    }
    .stApp { background: var(--lpe-bg) !important; color: var(--lpe-text) !important; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg,#174078 0%,#2357a8 100%) !important; }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea,
    section[data-testid="stSidebar"] select,
    section[data-testid="stSidebar"] [data-baseweb="select"] * { color: #17212b !important; }
    .main .block-container { max-width: 1500px; padding-top: 1.1rem; padding-bottom: 3rem; }
    h1, h2, h3, h4, p, li, span, label, div { color: var(--lpe-text); }
    div[data-testid="stAlert"] { border-radius: 14px; }
    .lpe10c-hero {
      background: #ffffff;
      border: 1px solid var(--lpe-line);
      border-radius: 22px;
      padding: 22px 24px;
      box-shadow: 0 10px 28px rgba(30, 64, 120, 0.08);
      margin-bottom: 18px;
    }
    .lpe10c-title { font-size: 2.05rem; font-weight: 850; line-height: 1.16; margin: 0 0 6px 0; }
    .lpe10c-subtitle { color: var(--lpe-muted); font-weight: 520; margin: 0; }
    .lpe10c-pillbar { display:flex; flex-wrap:wrap; gap:10px; margin: 14px 0 6px 0; }
    .lpe10c-pill {
      display:inline-block; padding: 7px 13px; border-radius: 999px;
      background: var(--lpe-blue-soft); color:#174078 !important; border:1px solid #cde4ff;
      font-weight: 780; font-size: .92rem;
    }
    .lpe10c-warning {
      background: var(--lpe-yellow); border: 1px solid #f4cf72; border-radius: 14px;
      padding: 12px 15px; font-weight: 720; margin: 12px 0;
    }
    .lpe10c-table-wrap {
      background: var(--lpe-panel);
      border: 1px solid var(--lpe-line);
      border-radius: 18px;
      overflow: hidden;
      box-shadow: 0 10px 22px rgba(30, 64, 120, .07);
      margin-top: 12px;
    }
    .lpe10c-table-head, .lpe10c-table-row {
      display: grid;
      grid-template-columns: 1.05fr 1.85fr 2.05fr 2.55fr 1.25fr;
      gap: 0;
      align-items: stretch;
    }
    .lpe10c-table-head > div {
      background: #e9f3ff;
      border-right: 1px solid var(--lpe-line);
      border-bottom: 1px solid var(--lpe-line);
      padding: 13px 14px;
      font-weight: 850;
      color: #123358 !important;
    }
    .lpe10c-table-row > div {
      background: #ffffff;
      border-right: 1px solid var(--lpe-line);
      border-bottom: 1px solid var(--lpe-line);
      padding: 14px 14px;
      min-height: 82px;
      font-size: .96rem;
      line-height: 1.45;
    }
    .lpe10c-table-row:nth-child(odd) > div { background: #fbfdff; }
    .lpe10c-time { font-weight: 850; color:#0f3b69 !important; }
    .lpe10c-action { font-weight: 780; }
    .lpe10c-muted { color: var(--lpe-muted) !important; font-size:.9rem; }
    .lpe10c-status-shell {
      background: var(--lpe-panel);
      border: 1px solid var(--lpe-line);
      border-radius: 16px;
      padding: 13px 14px;
      min-height: 112px;
      box-shadow: 0 5px 16px rgba(30,64,120,.05);
      margin-bottom: 8px;
    }
    .lpe10c-status-done { background: var(--lpe-green-soft); border-color: #b6e7c7; }
    .lpe10c-status-pending { background: #f3f4f6; border-color: #d1d5db; }
    .lpe10c-section-card {
      background: #ffffff; border: 1px solid var(--lpe-line); border-radius: 20px;
      padding: 18px 20px; margin: 14px 0 18px 0;
      box-shadow: 0 8px 20px rgba(30,64,120,.06);
    }
    .lpe10c-small-label { color: var(--lpe-muted) !important; font-size: .86rem; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)


def _lpe_phase10c_first(*values, default=""):
    for v in values:
        if v is not None and v != "":
            return v
    return default


def _lpe_phase10c_get_profile():
    for k in (
        "lpe_version_a_personal_profile_v1",
        "lpe_version_a_personal_profile",
        "personal_profile",
    ):
        v = st.session_state.get(k)
        if isinstance(v, dict):
            return v
    return {}


def _lpe_phase10c_get_daily_context():
    ctx = {}
    for k in (
        "lpe_version_a_daily_context",
        "daily_context",
        "version_a_phase2_daily_context",
    ):
        v = st.session_state.get(k)
        if isinstance(v, dict):
            ctx.update(v)
    quick = st.session_state.get("lpe_phase10c_quick_checkin", {})
    if isinstance(quick, dict):
        ctx.update({k: v for k, v in quick.items() if v not in (None, "")})
    return ctx


def _lpe_phase10c_get_latest_timetable():
    for k in (
        "lpe_phase10b_daily_action_board_result",
        "lpe_version_a_daily_timetable_result",
        "daily_timetable_result",
        "lpe_daily_timetable_result",
    ):
        v = st.session_state.get(k)
        if isinstance(v, dict):
            return v
    return {}


def _lpe_phase10c_guidance_for(action_text, ctx):
    text = str(action_text or "")
    energy = int(float(_lpe_phase10c_first(ctx.get("energy_level"), ctx.get("energy"), default=3) or 3))
    avoid = str(ctx.get("avoid_today") or "")
    food = str(ctx.get("available_food") or "")
    if any(w in text for w in ["อ่าน", "สอบ", "หนังสือ", "สรุป"]):
        return "ใช้บล็อก 20–30 นาทีหรือ 1 หัวข้อย่อยก่อน งานอ่านจะเริ่มง่ายขึ้นเมื่อเป้าหมายเล็กและจบชัดเจน"
    if any(w in text for w in ["กิน", "อาหาร", "ตั้งหลัก"]):
        base = "เลือกของที่ทำตามได้จริง เช่น โปรตีนง่าย + ผัก + น้ำเปล่า ลดหวาน/มันช่วงเย็นเพื่อไม่หนักท้อง"
        return base + (f" วันนี้มี: {food}" if food else "")
    if any(w in text for w in ["เวร", "งานหลัก", "งาน"]):
        return "ก่อนงานหลักอย่าเปิดงานใหม่ เก็บพลังงานไว้กับงานที่หลีกไม่ได้ แล้วค่อยบันทึก next action หลังจบงาน"
    if any(w in text for w in ["โปรเจกต์", "project"]):
        return "จำกัดเป็น 1 งานย่อยที่จบได้ในรอบเดียว ถ้าเริ่มบานให้หยุดที่ handoff/next action ไม่เปิด scope ใหม่"
    if any(w in text for w in ["ออกกำลัง", "ยืด", "เดิน", "สุขภาพ"]):
        return "ถ้าพลังงานไม่สูง ให้เลือกเบา 10–20 นาทีเพื่อรักษาความต่อเนื่อง ไม่ชดเชยด้วยการฝืนหนัก"
    if any(w in text for w in ["นอน", "ปิดวัน", "ท้ายวัน"]):
        return "ปิดจอ/ลดแสง/จด next action เดียวพอ การเตรียมก่อนนอนช่วยลดภาระสมองวันถัดไป"
    if energy <= 2:
        return "วันนี้พลังงานต่ำ ให้เลือกงานสำคัญ 1 อย่างก่อน งานรองเป็น optional เพื่อไม่ให้วันพังทั้งระบบ"
    if avoid:
        return f"วันนี้ต้องระวัง: {avoid} — ใช้เป็นเส้นกันหลุดจากงานหลักและเวลานอน"
    return "เลือกงานหลักก่อนงานรอง ทำให้จบเป็นรอบสั้น ๆ และทบทวนผลทันทีเพื่อให้ระบบวันถัดไปแม่นขึ้น"


def _lpe_phase10c_build_actions(ctx, timetable):
    blocks = []
    if isinstance(timetable, dict):
        raw_blocks = timetable.get("blocks") or timetable.get("action_items") or []
        if isinstance(raw_blocks, list):
            for b in raw_blocks:
                if isinstance(b, dict):
                    blocks.append({
                        "time": _lpe_phase10c_first(b.get("เวลา"), b.get("time"), default="ช่วงวันนี้"),
                        "action": _lpe_phase10c_first(b.get("ทำอะไร"), b.get("action"), default="ทำงานสำคัญ"),
                        "why": _lpe_phase10c_first(b.get("เหตุผล"), b.get("why"), default="ช่วยให้วันนี้ไม่หลุดจากเป้าหมายหลัก"),
                    })
    if not blocks:
        wake = _lpe_phase10c_first(ctx.get("wake_time"), ctx.get("wake"), default="หลังตื่น")
        work_start = _lpe_phase10c_first(ctx.get("work_start"), default="ช่วงงาน")
        work_end = _lpe_phase10c_first(ctx.get("work_end"), default="")
        study = _lpe_phase10c_first(ctx.get("study_focus"), ctx.get("primary_focus"), default="อ่านหรือสรุป 1 หัวข้อ")
        project = _lpe_phase10c_first(ctx.get("project_focus"), default="โปรเจกต์ 1 block สั้น")
        blocks = [
            {"time": f"หลังตื่น {wake}", "action": "กินง่าย / ดื่มน้ำ / ตั้งหลัก", "why": "เริ่มวันโดยไม่ใช้พลังงานเกินจำเป็น"},
            {"time": "ช่วงโฟกัสดีที่สุด", "action": study, "why": "งานอ่าน/สอบเป็น must-not-miss และมี deadline จริง"},
            {"time": "block โปรเจกต์สั้น", "action": project, "why": "รักษา momentum แต่ต้องไม่กินเวลาอ่านสอบและนอน"},
            {"time": f"{work_start}" + (f"–{work_end}" if work_end else ""), "action": f"เวร/งานหลัก ({_lpe_phase10c_first(ctx.get('today_shift'), default='วันนี้')})", "why": "งานหลักหลีกไม่ได้ ต้องมาก่อนงานเสริม"},
            {"time": "ท้ายวัน", "action": "ปิดวันและบันทึกสั้น ๆ", "why": "ให้พรุ่งนี้เริ่มต่อได้ทันทีโดยไม่ต้องคิดใหม่ทั้งหมด"},
        ]
    clean=[]
    seen=set()
    for i,b in enumerate(blocks[:8], start=1):
        key=f"{b.get('time','')}|{b.get('action','')}"
        if key in seen: continue
        seen.add(key)
        clean.append({"id": f"a{i}", **b, "guidance": _lpe_phase10c_guidance_for(b.get("action"), ctx)})
    return clean


def _lpe_phase10c_store_board(actions, ctx, timetable):
    st.session_state["lpe_phase10c_daily_board_result"] = {
        "schema_version": "lpe_version_a_phase10c_daily_action_board_v1",
        "mode": _lpe_phase10c_first(timetable.get("day_mode") if isinstance(timetable, dict) else None, default="Daily Board"),
        "today_shift": _lpe_phase10c_first(ctx.get("today_shift"), default="ไม่ระบุ"),
        "energy_level": _lpe_phase10c_first(ctx.get("energy_level"), ctx.get("energy"), default=3),
        "primary_focus": _lpe_phase10c_first(ctx.get("primary_focus"), ctx.get("study_focus"), default="เลือกงานหลัก 1 อย่าง"),
        "actions": actions,
        "status": st.session_state.get("lpe_phase10c_action_status", {}),
        "notes": st.session_state.get("lpe_phase10c_action_notes", {}),
    }


def _lpe_phase10c_render_sidebar():
    with st.sidebar:
        st.markdown("### 🎯 ผู้ช่วยจัดลำดับชีวิต")
        st.caption("daily-use เหลือ 2 หน้า")
        nav = st.radio(
            "เมนูหลัก",
            ["📋 ตารางกิจวัติประจำวัน", "🌙 สรุปวันนี้ / เตรียมพรุ่งนี้"],
            key="lpe_phase10c_nav_radio",
        )
        with st.expander("⚙️ ข้อมูลส่วนตัว / ขั้นสูง"):
            st.caption("ข้อมูลส่วนตัวควรตั้งค่าไว้นาน ๆ ครั้ง ไม่ใช่ flow หลักทุกวัน")
            legacy = st.checkbox("เปิดระบบเดิม/หน้าขั้นสูง", value=False, key="lpe_phase10c_allow_legacy")
        return nav, legacy


def _lpe_phase10c_render_daily_board():
    _lpe_phase10c_apply_light_dashboard_style()
    ctx = _lpe_phase10c_get_daily_context()
    timetable = _lpe_phase10c_get_latest_timetable()
    mode = _lpe_phase10c_first(timetable.get("day_mode") if isinstance(timetable, dict) else None, default="ยังไม่สร้างโหมด")
    shift = _lpe_phase10c_first(ctx.get("today_shift"), default="ไม่ระบุเวร")
    energy = _lpe_phase10c_first(ctx.get("energy_level"), ctx.get("energy"), default=3)
    focus = _lpe_phase10c_first(ctx.get("primary_focus"), ctx.get("study_focus"), default="เลือกงานหลัก 1 อย่าง")
    st.markdown(f"""
    <div class="lpe10c-hero">
      <div class="lpe10c-title">📋 ตารางกิจวัติประจำวัน</div>
      <p class="lpe10c-subtitle">เปิดหน้านี้แล้วรู้ทันทีว่า วันนี้เวลาไหนควรทำอะไร เพราะอะไร และมีเทคนิคอะไรที่ช่วยทำจริง</p>
      <div class="lpe10c-pillbar">
        <span class="lpe10c-pill">โหมด: {mode}</span>
        <span class="lpe10c-pill">เวรวันนี้: {shift}</span>
        <span class="lpe10c-pill">พลังงาน: {energy}</span>
        <span class="lpe10c-pill">เป้าหมาย: {focus}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("✏️ ข้อมูลวันนี้แบบย่อ — แก้เฉพาะที่จำเป็น", expanded=not bool(ctx)):
        c1,c2,c3,c4 = st.columns([1.1,1,1.2,2])
        quick = dict(st.session_state.get("lpe_phase10c_quick_checkin", {}))
        with c1:
            quick["wake_time"] = st.text_input("เวลาตื่น", value=str(quick.get("wake_time", ctx.get("wake_time", ""))), placeholder="เช่น 07.00", key="lpe10c_wake")
        with c2:
            quick["energy_level"] = st.slider("พลังงาน", 1, 5, int(float(quick.get("energy_level", ctx.get("energy_level", 3)) or 3)), key="lpe10c_energy")
        with c3:
            current_shift = str(quick.get("today_shift", ctx.get("today_shift", "หยุด")) or "หยุด")
            options=["หยุด","เวรเช้า","เวรบ่าย","เวรดึก","งานทั่วไป"]
            quick["today_shift"] = st.selectbox("เวรวันนี้", options, index=options.index(current_shift) if current_shift in options else 0, key="lpe10c_shift")
        with c4:
            quick["primary_focus"] = st.text_input("เป้าหมายหลักวันนี้", value=str(quick.get("primary_focus", ctx.get("primary_focus", ""))), placeholder="เช่น อ่านบท 8 / เวร / โปรเจกต์แบบจำกัด", key="lpe10c_focus")
        quick["avoid_today"] = st.text_input("สิ่งที่ต้องเลี่ยงวันนี้", value=str(quick.get("avoid_today", ctx.get("avoid_today", ""))), placeholder="เช่น เปิด scope ใหม่ / โปรเจกต์ยาว / กินหวาน", key="lpe10c_avoid")
        st.session_state["lpe_phase10c_quick_checkin"] = quick
        ctx.update({k:v for k,v in quick.items() if v not in (None,"")})
    actions = _lpe_phase10c_build_actions(ctx, timetable)
    status = dict(st.session_state.get("lpe_phase10c_action_status", {}))
    notes = dict(st.session_state.get("lpe_phase10c_action_notes", {}))
    st.markdown("### ตารางวันนี้")
    st.caption("ตารางนี้คือหัวใจหลัก: เวลา / ทำอะไร / เพราะอะไร / เทคนิคเสริม / สถานะเทา-เขียว")
    st.markdown("""
    <div class="lpe10c-table-wrap">
      <div class="lpe10c-table-head">
        <div>เวลา</div><div>ทำอะไร</div><div>เพราะอะไร</div><div>เทคนิค / ความรู้เสริม</div><div>สถานะ</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    done_count = 0
    for item in actions:
        key=item["id"]
        is_done=bool(status.get(key, False))
        st.markdown(f"""
        <div class="lpe10c-table-wrap" style="margin-top:0;border-top:0;border-radius:0;box-shadow:none;">
          <div class="lpe10c-table-row">
            <div class="lpe10c-time">{item['time']}</div>
            <div class="lpe10c-action">{item['action']}</div>
            <div>{item['why']}</div>
            <div>{item['guidance']}</div>
            <div class="lpe10c-muted">เทา = ยังไม่ทำ / เขียว = ทำแล้ว</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        c1,c2 = st.columns([1,4])
        with c1:
            done = st.toggle("ทำแล้ว", value=is_done, key=f"lpe_phase10c_done_{key}")
            status[key]=bool(done)
            if done: done_count += 1
        with c2:
            notes[key] = st.text_input("หมายเหตุ", value=str(notes.get(key,"")), placeholder="เช่น สั้น ๆ / ติดงาน / ทำได้ครึ่งเดียว", key=f"lpe_phase10c_note_{key}")
    st.session_state["lpe_phase10c_action_status"] = status
    st.session_state["lpe_phase10c_action_notes"] = notes
    _lpe_phase10c_store_board(actions, ctx, timetable)
    total=len(actions)
    st.markdown(f"<div class='lpe10c-warning'>ความคืบหน้าวันนี้: {done_count}/{total} รายการ</div>", unsafe_allow_html=True)
    st.info("หลังจบวัน ไปหน้า 🌙 สรุปวันนี้ / เตรียมพรุ่งนี้ เพื่อเลือกผลรวม กำหนดเวรพรุ่งนี้ และ next single action")


def _lpe_phase10c_render_end_day():
    _lpe_phase10c_apply_light_dashboard_style()
    board = st.session_state.get("lpe_phase10c_daily_board_result", {})
    actions = board.get("actions", []) if isinstance(board, dict) else []
    status = st.session_state.get("lpe_phase10c_action_status", {})
    done_count = sum(1 for a in actions if status.get(a.get("id"))) if isinstance(actions, list) else 0
    total = len(actions) if isinstance(actions, list) else 0
    st.markdown(f"""
    <div class="lpe10c-hero">
      <div class="lpe10c-title">🌙 สรุปวันนี้ / เตรียมพรุ่งนี้</div>
      <p class="lpe10c-subtitle">ไม่ต้องกรอกยาว ระบบดึงผลจากตารางวันนี้ แล้วถามเฉพาะข้อมูลที่จำเป็นสำหรับพรุ่งนี้</p>
      <div class="lpe10c-pillbar"><span class="lpe10c-pill">วันนี้ทำแล้ว: {done_count}/{total}</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div class='lpe10c-section-card'>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1.2,1,1.2])
    with c1:
        today_result = st.selectbox("วันนี้โดยรวม", ["ยังไม่สรุป","ดี","กลาง","แย่"], key="lpe10c_today_result")
    with c2:
        end_energy = st.slider("พลังงานท้ายวัน", 1, 5, 3, key="lpe10c_end_energy")
    with c3:
        tomorrow_shift = st.selectbox("พรุ่งนี้เวรอะไร", ["ยังไม่ระบุ","หยุด","เวรเช้า","เวรบ่าย","เวรดึก","งานทั่วไป"], key="lpe10c_tomorrow_shift")
    tomorrow_must = st.text_input("พรุ่งนี้ต้องทำอะไรเป็นอันดับ 1", placeholder="เช่น อ่านบทถัดไป / พักก่อนเวร / เวรบ่าย", key="lpe10c_tomorrow_must")
    next_action = st.text_input("next single action ตอนเปิดเว็บครั้งถัดไป", placeholder="เช่น เปิดตาราง → อ่าน 20 นาที → ติ๊กผล", key="lpe10c_next_action")
    optional_note = st.text_area("หมายเหตุเสริม (ไม่บังคับ)", placeholder="เขียนสั้น ๆ เฉพาะสิ่งที่ระบบควรรู้", key="lpe10c_optional_note")
    if not next_action:
        st.warning("next single action ยังว่าง — จาก Day 1–3 พบว่าเป็นจุดหลุดซ้ำ ควรใส่สั้น ๆ ก่อนจบวัน")
    st.session_state["lpe_phase10c_quick_reflection"] = {
        "schema_version":"lpe_version_a_phase10c_quick_reflection_v1",
        "done_count": done_count,
        "total_count": total,
        "today_result": today_result,
        "end_energy": end_energy,
        "tomorrow_shift": tomorrow_shift,
        "tomorrow_must": tomorrow_must,
        "next_single_action": next_action,
        "optional_note": optional_note,
    }
    st.markdown("</div>", unsafe_allow_html=True)
    st.success("บันทึกใน session แล้ว: ใช้หน้า สำรองข้อมูล/export เดิมเพื่อเก็บ JSON ถ้าต้องการ")


def _lpe_phase10c_bootstrap_two_page_daily_use():
    nav, legacy = _lpe_phase10c_render_sidebar()
    if legacy:
        st.info("เปิดระบบเดิม/ขั้นสูงแล้ว — เลื่อนลงเพื่อใช้ flow เดิม")
        return
    if nav == "📋 ตารางกิจวัติประจำวัน":
        _lpe_phase10c_render_daily_board()
        st.stop()
    if nav == "🌙 สรุปวันนี้ / เตรียมพรุ่งนี้":
        _lpe_phase10c_render_end_day()
        st.stop()

_lpe_phase10c_bootstrap_two_page_daily_use()
# === LPE_VERSION_A_PHASE10C_TWO_PAGE_DAILY_BOARD_NAV_TABLE_REDESIGN_V1 END ===


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --navy: #1f2d4a;
            --cream: #f7f3ea;
            --paper: #ffffff;
            --ink: #172033;
            --muted: #667085;
            --line: #e6ded2;
            --purple: #6d4df2;
            --green: #18a876;
            --yellow: #d99012;
            --red: #e3483e;
        }
        .stApp {
            background: var(--cream);
            color: var(--ink);
        }
        .block-container {
            max-width: 1160px;
            padding-top: 1.5rem;
            padding-bottom: 4rem;
        }
        section[data-testid="stSidebar"] {
            background: var(--navy);
            color: white;
        }
        section[data-testid="stSidebar"] * {
            color: white;
        }
        .hero {
            background: var(--navy);
            color: white;
            border-radius: 22px;
            padding: 30px 34px;
            box-shadow: 0 18px 40px rgba(31,45,74,.18);
            margin-bottom: 26px;
        }
        .hero-eyebrow {
            opacity: .72;
            font-weight: 700;
            letter-spacing: .02em;
            margin-bottom: 6px;
        }
        .hero-title {
            font-size: 2.45rem;
            line-height: 1.1;
            font-weight: 900;
            margin: 0;
        }
        .hero-subtitle {
            font-size: 1.1rem;
            opacity: .94;
            margin-top: 12px;
            max-width: 760px;
        }
        .mobile-nav-note {
            background: #f0edff;
            border: 1px solid #d7cffc;
            border-radius: 14px;
            padding: 12px 14px;
            color: #34267d;
            margin-bottom: 10px;
            font-weight: 750;
        }
        .demo-warning {
            background: #fff7e6;
            border: 1px solid #ffd591;
            border-radius: 14px;
            padding: 12px 14px;
            color: #6b4200;
            margin: 14px 0;
            font-weight: 650;
        }
        .card {
            background: var(--paper);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 20px;
            box-shadow: 0 8px 22px rgba(28,35,49,.06);
            min-height: 120px;
        }
        .card-label {
            color: var(--muted);
            font-size: .92rem;
            margin-bottom: 8px;
        }
        .card-value {
            color: var(--ink);
            font-size: 1.4rem;
            font-weight: 900;
            line-height: 1.25;
        }
        .pill-row {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin: 16px 0 22px 0;
        }
        .pill {
            border: 1px solid var(--line);
            background: white;
            border-radius: 999px;
            padding: 8px 12px;
            font-weight: 700;
            color: var(--ink);
            font-size: .92rem;
        }
        .mission-card {
            background: white;
            border: 1px solid var(--line);
            border-left: 7px solid var(--purple);
            border-radius: 18px;
            padding: 20px 20px 18px 20px;
            box-shadow: 0 10px 24px rgba(28,35,49,.07);
            margin: 16px 0;
        }
        .mission-card.must { border-left-color: var(--red); }
        .mission-card.should { border-left-color: var(--yellow); }
        .mission-card.could { border-left-color: var(--purple); }
        .mission-meta {
            color: var(--muted);
            font-size: .9rem;
        }
        .mission-title {
            font-size: 1.16rem;
            font-weight: 900;
            margin: 8px 0;
        }
        .badge {
            display: inline-block;
            border-radius: 999px;
            padding: 5px 9px;
            font-size: .78rem;
            font-weight: 900;
            margin-right: 6px;
            background: #f0edff;
            color: #4b32c3;
        }
        .badge.must { background: #ffe7e7; color: #c92a2a; }
        .badge.should { background: #fff2cc; color: #9a6200; }
        .badge.could { background: #f0edff; color: #4b32c3; }
        .safe-note {
            background: #ecfdf5;
            border: 1px solid #c7f5df;
            color: #085e45;
            padding: 12px 14px;
            border-radius: 14px;
            margin: 12px 0;
            font-weight: 650;
        }
        .danger-note {
            background: #fff1f0;
            border: 1px solid #ffccc7;
            color: #8c1d18;
            padding: 12px 14px;
            border-radius: 14px;
            margin: 12px 0;
            font-weight: 650;
        }
        .section-title {
            font-size: 1.7rem;
            font-weight: 900;
            margin: 28px 0 8px 0;
        }
        .section-subtitle {
            color: var(--muted);
            margin-bottom: 16px;
        }
        div[data-testid="stRadio"] > div {
            gap: .35rem;
        }
        div[data-testid="stRadio"] label {
            border: 1px solid var(--line);
            background: white;
            border-radius: 999px;
            padding: 8px 11px;
            min-height: 44px;
            color: var(--ink) !important;
        }
        div[data-testid="stRadio"] label p {
            color: var(--ink) !important;
            font-weight: 800 !important;
        }
        div[data-testid="stRadio"] label:has(input:checked) {
            border-color: #087456;
            background: #0b7f5e;
        }
        div[data-testid="stRadio"] label:has(input:checked) p {
            color: white !important;
        }
        div[data-baseweb="select"] > div {
            min-height: 48px;
            border-color: #a79aef !important;
            background: white !important;
            color: var(--ink) !important;
        }
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] input,
        div[data-baseweb="select"] svg {
            color: var(--ink) !important;
            fill: var(--ink) !important;
        }
        .st-key-lpe_nav_mobile div[data-baseweb="select"] > div {
            border: 2px solid var(--purple) !important;
            box-shadow: 0 5px 14px rgba(109,77,242,.12);
        }
        .st-key-lpe_nav_mobile [data-testid="stWidgetLabel"] p {
            color: var(--ink) !important;
            font-size: .92rem !important;
            font-weight: 850 !important;
        }
        button[kind="primary"], .stButton > button, [data-testid="stFormSubmitButton"] button {
            border-radius: 14px !important;
            font-weight: 800 !important;
            min-height: 46px;
        }
        .stButton > button,
        [data-testid="stFormSubmitButton"] button {
            border: 1px solid #cfc7bc !important;
            background: white !important;
            color: var(--ink) !important;
        }
        .stButton > button p,
        [data-testid="stFormSubmitButton"] button p {
            color: inherit !important;
            font-weight: 850 !important;
        }
        .stButton > button[kind="primary"],
        [data-testid="stFormSubmitButton"] button[kind="primary"] {
            border-color: var(--purple) !important;
            background: var(--purple) !important;
            color: white !important;
            box-shadow: 0 8px 18px rgba(109,77,242,.22);
        }
        .onboarding-step {
            margin: 14px 0 18px;
            padding: 16px 18px;
            border: 1px solid var(--line);
            border-radius: 16px;
            background: white;
            box-shadow: 0 7px 18px rgba(28,35,49,.05);
        }
        .onboarding-step strong {
            display: block;
            margin-bottom: 5px;
            color: var(--navy);
            font-size: 1.08rem;
        }
        .onboarding-step span {
            color: var(--muted);
            line-height: 1.5;
        }
        [data-testid="stExpander"] {
            border-color: var(--line) !important;
            border-radius: 14px !important;
            background: white;
        }
        [data-testid="stExpander"] summary p {
            color: var(--ink) !important;
            font-weight: 800 !important;
        }
        @media (max-width: 760px) {
            .block-container {
                padding: .75rem .9rem 5rem .9rem;
            }
            .hero {
                padding: 22px 20px;
                border-radius: 20px;
                margin-top: 4px;
            }
            .hero-title {
                font-size: 2.1rem;
            }
            .hero-subtitle {
                font-size: 1rem;
            }
            .card {
                min-height: 110px;
                padding: 17px;
            }
            .card-value {
                font-size: 1.25rem;
            }
            .mission-card {
                padding: 18px;
            }
            div[data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
            }
            div[data-testid="stRadio"] > div {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                width: 100%;
            }
            div[data-testid="stRadio"] label {
                width: 100%;
                justify-content: center;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def read_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback


def read_csv(path: Path) -> list[dict[str, str]]:
    try:
        if path.exists():
            with path.open("r", encoding="utf-8-sig", newline="") as f:
                return list(csv.DictReader(f))
    except Exception:
        pass
    return []


def parse_date(value: Any, fallback: date | None = None) -> date:
    if fallback is None:
        fallback = date.today()
    if isinstance(value, date):
        return value
    text = str(value or "").strip()
    for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except Exception:
            continue
    return fallback


def clean_public_text(value: Any, replacement: str) -> str:
    text = str(value or "").strip()
    lowered = text.lower()
    unclear_defaults = (
        "maintain consistent light activity and adequate recovery",
    )
    if (
        not text
        or lowered in unclear_defaults
        or any(marker in lowered for marker in ("demo", "mock", "example"))
        or "ตัวอย่าง" in text
    ):
        return replacement
    return text


def thai_shift(value: Any) -> str:
    text = str(value or "").strip()
    return {
        "OFF": "วันหยุด",
        "MORNING": "เวรเช้า",
        "EVENING": "เวรบ่าย",
        "NIGHT": "เวรดึก",
    }.get(text.upper(), clean_public_text(text, "วันหยุด"))


def seed_profile() -> dict[str, Any]:
    user_profile = read_json(DATA_DIR / "user_profile.json", {})
    health_goal = read_json(DATA_DIR / "health_goal.json", {})
    projects = read_json(DATA_DIR / "project_list.json", [])
    exams = read_csv(DATA_DIR / "exam_plan.csv")
    shifts = read_csv(DATA_DIR / "shift_schedule.csv")
    garden = read_csv(DATA_DIR / "garden_plan.csv")

    first_exam = exams[0] if exams else {}
    project_rows = projects.get("projects", []) if isinstance(projects, dict) else projects
    first_project = project_rows[0] if isinstance(project_rows, list) and project_rows else {}
    first_shift = shifts[0] if shifts else {}
    first_garden = garden[0] if garden else {}

    exam_date = parse_date(
        first_exam.get("exam_date") or first_exam.get("date") or first_exam.get("วันสอบ"),
        date.today() + timedelta(days=24),
    )
    subject = clean_public_text(
        first_exam.get("subject") or first_exam.get("วิชา"), "วิชาหลักของคุณ"
    )
    study_minutes = int(float(first_exam.get("target_minutes") or first_exam.get("minutes") or 60))
    project_name = clean_public_text(
        first_project.get("name") or first_project.get("project"),
        "โปรเจกต์ส่วนตัวของคุณ",
    )
    shift = thai_shift(first_shift.get("shift") or first_shift.get("type"))
    health_goal_text = clean_public_text(
        health_goal.get("goal") or health_goal.get("name"), "ขยับเบา ๆ หรือพักให้พอ"
    )
    calorie_note = health_goal.get("calorie_target") or health_goal.get("calories") or ""

    return _lpe_v111_story_profile_defaults(
        {
            "nickname": clean_public_text(
                user_profile.get("nickname") or user_profile.get("name"), "คุณ"
            ),
            "plan_date": date.today(),
            "start_mode": "วันพลังพร้อม",
            "subject": subject,
            "exam_date": exam_date,
            "study_minutes": study_minutes,
            "health_goal": health_goal_text,
            "project_name": project_name,
            "garden_task": clean_public_text(
                first_garden.get("task")
                or first_garden.get("activity")
                or first_garden.get("work_item"),
                "งานบ้านหรือสวนที่อยากไม่ลืม",
            ),
            "shift": shift,
            "calorie_note": calorie_note,
        }
    )


def init_state() -> None:
    if "lpe_profile" not in st.session_state:
        st.session_state.lpe_profile = seed_profile()
    if "lpe_review" not in st.session_state:
        st.session_state.lpe_review = {}
    if "lpe_saved_summary" not in st.session_state:
        st.session_state.lpe_saved_summary = None
    if "lpe_nav" not in st.session_state:
        st.session_state.lpe_nav = "วันนี้ต้องทำอะไร"
    if "lpe_nav_mobile" not in st.session_state:
        st.session_state.lpe_nav_mobile = DESTINATION_TO_PRIMARY_NAV.get(
            st.session_state.lpe_nav, "••• เพิ่มเติม"
        )
    if "lpe_nav_sidebar" not in st.session_state:
        st.session_state.lpe_nav_sidebar = (
            st.session_state.lpe_nav
            if st.session_state.lpe_nav in DESKTOP_NAV_ITEMS
            else "วันนี้ต้องทำอะไร"
        )
    if "lpe_onboarding_step" not in st.session_state:
        st.session_state.lpe_onboarding_step = 1


def navigate_to(page: str) -> None:
    # Widget-safe navigation.
    # Do not mutate Streamlit widget keys after those widgets have been instantiated.
    # Store the route in a private pending key, then sync widget keys at the top of main()
    # on the next rerun before navigation widgets are created.
    page = str(page or "").strip()
    if not page:
        return
    st.session_state["_lpe_pending_page"] = page
    st.session_state["lpe_current_page"] = page
    try:
        st.rerun()
    except Exception:
        return

def sync_mobile_navigation() -> None:
    destination = PRIMARY_NAV_DESTINATIONS[st.session_state.lpe_nav_mobile]
    navigate_to(destination)


def sync_sidebar_navigation() -> None:
    navigate_to(st.session_state.lpe_nav_sidebar)


def days_to_exam(profile: dict[str, Any], plan_date: date | None = None) -> int:
    if plan_date is None:
        plan_date = parse_date(profile.get("plan_date"))
    exam_date = parse_date(profile.get("exam_date"), plan_date + timedelta(days=24))
    return (exam_date - plan_date).days


def mode_label(mode: str) -> str:
    mapping = {
        "วันพลังพร้อม": "วันพลังพร้อม",
        "วันพลังจำกัด": "วันพลังจำกัด",
        "วันพักฟื้น": "วันพักฟื้น",
    }
    return mapping.get(mode, "วันพลังพร้อม")


def generate_missions(profile: dict[str, Any], for_tomorrow: bool = False) -> tuple[list[dict[str, Any]], list[str]]:
    plan_date = parse_date(profile.get("plan_date"))
    if for_tomorrow:
        plan_date = plan_date + timedelta(days=1)
    mode = mode_label(profile.get("start_mode", "วันพลังพร้อม"))
    dte = days_to_exam(profile, plan_date)
    missions: list[dict[str, Any]] = []
    avoid: list[str] = []

    if for_tomorrow and st.session_state.get("lpe_saved_summary"):
        summary = st.session_state.lpe_saved_summary
        if summary.get("mode") == "วันพักฟื้น":
            mode = "วันพลังจำกัด"
            avoid.append("อย่าชดเชยด้วยการออกแรงหนักทันทีหลังวันพักฟื้น")

    if dte <= 7:
        study_target = max(60, int(profile.get("study_minutes", 60)))
        avoid.append("อย่าเริ่มโปรเจกต์ยาวก่อนอ่านหนังสือ")
    elif dte <= 30:
        study_target = int(profile.get("study_minutes", 60))
    else:
        study_target = min(45, int(profile.get("study_minutes", 45)))

    missions.append(
        {
            "id": "study",
            "kind": "must",
            "title": f"อ่าน {profile.get('subject', 'วิชาหลัก')}: บทที่ 1",
            "tag": "อ่านหนังสือ",
            "minutes": f"{study_target} นาที",
            "reason": f"เหลือ {max(dte, 0)} วันก่อนสอบ จึงต้องกันเวลาสำหรับวิชาหลักก่อน",
        }
    )

    if mode == "วันพักฟื้น":
        missions.append(
            {
                "id": "recovery",
                "kind": "must",
                "title": "พักฟื้นและดูแลพื้นฐาน",
                "tag": "สุขภาพ",
                "minutes": "10–15 นาที",
                "reason": "วันนี้ร่างกายสำคัญกว่าการเพิ่มงานใหม่",
            }
        )
        avoid.append("งดออกกำลังกายหนัก งดเพิ่มงานใหม่")
    else:
        missions.append(
            {
                "id": "movement",
                "kind": "should",
                "title": "ขยับเบา ๆ หรือพักฟื้น",
                "tag": "สุขภาพ",
                "minutes": "10–20 นาที",
                "reason": "ให้ร่างกายได้ขยับโดยไม่ฝืนเกินจริง",
            }
        )

    if mode == "วันพลังพร้อม" and dte > 7:
        missions.append(
            {
                "id": "project",
                "kind": "could",
                "title": f"ทำเมื่อมีแรงเหลือ: {profile.get('project_name', 'โปรเจกต์ส่วนตัว')}",
                "tag": "โปรเจกต์",
                "minutes": "ไม่เกิน 30 นาที",
                "reason": "ทำได้หลังภารกิจต้องทำเสร็จแล้วเท่านั้น",
            }
        )
        missions.append(
            {
                "id": "garden",
                "kind": "could",
                "title": profile.get("garden_task", "ตรวจจุดพื้นที่สวน"),
                "tag": "ดูแลชีวิตประจำวัน",
                "minutes": "ไม่เกิน 30 นาที",
                "reason": "งานรองที่ทำได้ถ้าไม่เบียดงานหลัก",
            }
        )
    else:
        missions.append(
            {
                "id": "close_day",
                "kind": "should",
                "title": "สรุปวันนี้สั้น ๆ ก่อนนอน",
                "tag": "รีวิว",
                "minutes": "3 นาที",
                "reason": "ใช้ผลจริงปรับแผนพรุ่งนี้ ไม่ใช่เดาจากความรู้สึก",
            }
        )
        avoid.append("งดโปรเจกต์ยาวถ้างานหลักยังไม่เสร็จ")

    if not avoid:
        avoid.append("อย่าเริ่มงานที่ทำได้ถ้ามีแรง ก่อนปกป้องงานที่ต้องทำ")

    return missions[:5], avoid[:3]


def mission_score(status: str) -> float:
    return {
        "ทำครบ": 1.0,
        "ทำบางส่วน": 0.55,
        "ไม่ได้ทำ": 0.0,
        "มีปัญหา": 0.35,
    }.get(status, 0.0)


def summarize_day(missions: list[dict[str, Any]]) -> dict[str, Any]:
    review = st.session_state.lpe_review
    scores = [mission_score(review.get(m["id"], {}).get("status", "ไม่ได้ทำ")) for m in missions]
    score = round((sum(scores) / max(len(scores), 1)) * 100)
    reasons = [review.get(m["id"], {}).get("reason", "") for m in missions]
    serious_words = ("เป็นลม", "เจ็บหน้าอก", "หายใจไม่ออก", "เวียนหัวมาก", "ป่วย")
    has_serious = any(any(word in reason for word in serious_words) for reason in reasons)
    if has_serious:
        mode = "วันพักฟื้น"
    elif score >= 80:
        mode = "วันพลังพร้อม"
    elif score >= 45:
        mode = "วันพลังจำกัด"
    else:
        mode = "วันพักฟื้น"

    blocker = "ไม่มีปัญหาหลัก"
    for m in missions:
        item = review.get(m["id"], {})
        if item.get("status") in ("ทำบางส่วน", "ไม่ได้ทำ", "มีปัญหา"):
            blocker = item.get("reason") or item.get("status") or "ทำได้บางส่วน"
            break

    return {"score": score, "mode": mode, "blocker": blocker, "has_serious": has_serious}


def save_review(missions: list[dict[str, Any]]) -> None:
    st.session_state.lpe_saved_summary = summarize_day(missions)


def render_hero(title: str, subtitle: str, icon: str = "🏠") -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-eyebrow">ผู้ช่วยวางแผนชีวิตประจำวัน</div>
            <div style="display:flex;gap:18px;align-items:center;">
                <div style="font-size:2rem;background:rgba(255,255,255,.08);padding:14px;border-radius:18px;">{icon}</div>
                <div>
                    <h1 class="hero-title">{title}</h1>
                    <div class="hero-subtitle">{subtitle}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_demo_warning() -> None:
    st.markdown(
        """
        <div class="demo-warning">
        ⚠️ เวอร์ชันทดลอง: ข้อมูลอยู่เฉพาะเบราว์เซอร์นี้ รีเฟรชแล้วอาจหาย อย่ากรอกข้อมูลส่วนตัวจริง
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_demo_about() -> None:
    with st.expander("เกี่ยวกับเวอร์ชันทดลอง", expanded=False):
        st.markdown(
            """
            - ข้อมูลที่กรอกและผลรีวิวอยู่ชั่วคราวเฉพาะการใช้งานครั้งนี้
            - ไม่มีบัญชีผู้ใช้และไม่มีฐานข้อมูลส่วนตัว
            - ระบบไม่เขียนข้อมูลที่กรอกลงไฟล์ CSV กลาง
            - เป็นเครื่องมือวางแผนทั่วไป ไม่ใช่คำแนะนำทางการแพทย์ โภชนาการ หรือการรักษา
            """
        )



# === LPE_V1_11_STEP2_3_CLEAN_CONSOLIDATED_CORE_START ===
def _lpe_v111_story_mode_specs() -> dict[str, dict[str, Any]]:
    return {
        "goals": {
            "title": "1) เป้าหมายและปัญหาที่อยากแก้",
            "short": "แยกพระเอกของช่วงนี้ออกจากสิ่งที่อยากทำทั้งหมด",
            "questions": [
                "3 สิ่งที่สำคัญที่สุดใน 30 วันนี้คืออะไร และเรียงลำดับอย่างไร",
                "สิ่งไหนมี deadline ชัดเจน หรือถ้าพลาดแล้วเสียหายจริง",
                "ถ้าวันนี้ทำได้แค่อย่างเดียว ควรเลือกอะไรเพื่อไม่ให้ชีวิตหลุด",
                "ปัญหาซ้ำที่ทำให้เป้าหมายหลุดคืออะไร เช่น วินัย เวลา พลังงาน หรือสิ่งล่อใจ",
                "minimum action ที่เล็กที่สุดคืออะไร เมื่อเหนื่อยมากแต่ยังไม่อยากหลุด",
            ],
            "use_for": [
                "จัดลำดับพระเอกของวัน",
                "ลดงานรองเมื่อ deadline หรือเป้าหมายหลักเสี่ยง",
                "เลือก minimum action เมื่อพลังงานต่ำ",
            ],
            "summary_keywords": ["สอบ", "อ่าน", "ลดน้ำหนัก", "โปรเจกต์", "เทรด", "วินัย", "deadline"],
        },
        "time_rhythm": {
            "title": "2) เวลาและจังหวะชีวิต",
            "short": "ให้ระบบรู้เวลาจริง เวรจริง และเวลานอนที่ต้องปกป้อง",
            "questions": [
                "ปกติมีเวร/งานกี่แบบ แต่ละแบบเริ่ม-เลิกกี่โมง",
                "ก่อนเริ่มงานต้องใช้เวลาเตรียมตัวและเดินทางรวมกี่นาที",
                "หลังเวรแบบไหนยังพอทำงานใช้สมาธิได้ และหลังเวรแบบไหนควรพักเท่านั้น",
                "เวลานอนขั้นต่ำที่ต้องปกป้องคือช่วงไหน โดยเฉพาะก่อนขึ้นเวรดึกหรือเวรเช้า",
                "ถ้าเวรชนกับแผน ระบบควรลดอะไรเป็นอย่างแรก",
            ],
            "use_for": [
                "กันเวลางานและเวลานอนก่อนวางแผน",
                "เลือกช่วงสมองดีที่สุด",
                "ลดงานเมื่อเวรหนักหรือเวลาพักไม่พอ",
            ],
            "summary_keywords": ["เวร", "ตื่น", "นอน", "ดึก", "เช้า", "บ่าย", "เดินทาง", "พัก"],
        },
        "health_energy": {
            "title": "3) สุขภาพและพลังงาน",
            "short": "วางแผนไม่ฝืนร่างกาย และแยกวันพร้อมออกจากวันต้องพัก",
            "questions": [
                "เป้าหมายสุขภาพตอนนี้คืออะไร และอยากให้เห็นผลแบบไหนก่อน",
                "สภาพร่างกายแบบไหนคือสัญญาณว่าเริ่มฝืนหรือเสี่ยงวูบ",
                "ออกกำลังกายขั้นต่ำที่ปลอดภัยในวันเหนื่อยมากคืออะไร",
                "อาหาร/โปรตีน/น้ำที่ทำได้จริงในชีวิตประจำวันคืออะไร",
                "ถ้าวันนี้พลังงานต่ำ ระบบควรเลือกพัก เดินเบา หรือออกกำลังแบบไหน",
            ],
            "use_for": [
                "ลดความหนักของแผนเมื่อร่างกายไม่พร้อม",
                "เลือกการออกกำลังขั้นต่ำที่ปลอดภัย",
                "กันไม่ให้สุขภาพโดนโปรเจกต์หรืองานกลืน",
            ],
            "summary_keywords": ["น้ำหนัก", "ลด", "วิ่ง", "อาหาร", "โปรตีน", "วูบ", "เหนื่อย", "พัก"],
        },
        "obligations": {
            "title": "4) งาน / เงิน / ภาระที่ห้ามพลาด",
            "short": "กันสิ่งที่เสียไม่ได้ ก่อนจัดงานฝันหรือโปรเจกต์รอง",
            "questions": [
                "งาน/เวร/สอบ/ภาระใดที่ห้ามพลาด เพราะกระทบงาน เงิน หรืออนาคต",
                "อะไรคือความรับผิดชอบที่ต้องกันเวลาไว้เสมอ แม้วันนั้นเหนื่อย",
                "โปรเจกต์ใดสำคัญต่ออนาคต แต่สามารถทำทีละนิดได้",
                "ถ้าวันนี้งานประจำหรือเวรหนัก ระบบควรตัด ลด หรือเลื่อนอะไร",
                "คำแนะนำแบบไหนที่ระบบห้ามให้ เพราะจะกระทบรายได้ งาน หรือหน้าที่หลัก",
            ],
            "use_for": [
                "กันงานที่เสียไม่ได้ก่อน",
                "จัด priority เมื่องาน/เรียน/สุขภาพ/โปรเจกต์ชนกัน",
                "ไม่แนะนำแผนที่กระทบรายได้หรือหน้าที่หลัก",
            ],
            "summary_keywords": ["งาน", "เวร", "สอบ", "โปรเจกต์", "เทรด", "เงิน", "รายได้", "หน้าที่"],
        },
        "life_rules": {
            "title": "5) เรื่องราวชีวิตและกฎส่วนตัว",
            "short": "ทำให้ระบบไม่ generic และรู้ว่าต้องเตือนแบบไหนถึงได้ผล",
            "questions": [
                "ช่วงนี้ชีวิตกำลังแบกอะไรอยู่ ที่คนอื่นอาจมองไม่เห็น",
                "นิสัยหรือ pattern ใดทำให้แผนพังบ่อย เช่น ผัดวัน ฆ่าเวลา หรือหลุดโฟกัส",
                "อยากให้ระบบเตือนแบบเข้มแค่ไหน และมีถ้อยคำแบบไหนที่ยอมรับได้",
                "ถ้าวันแย่มาก แผนขั้นต่ำควรเหลืออะไรเพื่อรักษา momentum",
                "สิ่งที่ระบบห้ามทำหรือห้ามพูดคืออะไร เช่น เอาใจเกินจริง โกหก หรือแนะนำสิ่งเสี่ยง",
            ],
            "use_for": [
                "ตั้งกฎส่วนตัวให้แผนรายวัน",
                "กำหนด fallback plan ในวันที่แย่",
                "ลดคำแนะนำที่ไม่ตรงนิสัยหรือชีวิตจริง",
            ],
            "summary_keywords": ["วินัย", "เข้มงวด", "โกหก", "ความจริง", "fallback", "ชีวิต", "นิสัย"],
        },
    }


def _lpe_v111_story_profile_defaults(profile: dict[str, Any] | None) -> dict[str, Any]:
    profile = dict(profile or {})
    profile.setdefault("core_life_profile_version", "v1.11-story")
    profile.setdefault("nickname", "คุณ")
    profile.setdefault("plan_date", date.today())
    profile.setdefault("start_mode", "วันพลังพร้อม")
    profile.setdefault("subject", "วิชาหลักของคุณ")
    profile.setdefault("exam_date", date.today() + timedelta(days=24))
    profile.setdefault("study_minutes", 60)
    profile.setdefault("health_goal", "ขยับเบา ๆ หรือพักให้พอ")
    profile.setdefault("project_name", "โปรเจกต์ส่วนตัวของคุณ")
    profile.setdefault("garden_task", "งานบ้านหรือสวนที่อยากไม่ลืม")
    profile.setdefault("shift", "เวรตามจริง")
    profile.setdefault("calorie_note", "")

    modes = profile.get("life_story_modes")
    if not isinstance(modes, dict):
        modes = {}
    for key, spec in _lpe_v111_story_mode_specs().items():
        existing = modes.get(key) if isinstance(modes.get(key), dict) else {}
        modes[key] = {
            "title": spec["title"],
            "story": str(existing.get("story", "")),
            "last_summary": list(existing.get("last_summary", [])) if isinstance(existing.get("last_summary", []), list) else [],
            "updated": existing.get("updated", ""),
        }
    profile["life_story_modes"] = modes
    profile.setdefault("life_story_profile_summary", [])
    profile.setdefault("life_story_missing_modes", [])
    profile.setdefault("life_story_last_updated", "")
    return profile


def _lpe_v111_extract_story_signals(story: str, keywords: list[str]) -> list[str]:
    story = str(story or "").strip()
    found = []
    for keyword in keywords:
        if keyword and keyword.lower() in story.lower():
            found.append(keyword)
    return found[:8]


def _lpe_v111_story_mode_summary(mode_key: str, story: str) -> list[str]:
    specs = _lpe_v111_story_mode_specs()
    spec = specs.get(mode_key, {})
    story = str(story or "").strip()
    if not story:
        return ["ยังไม่มีเรื่องเล่าในโหมดนี้ ระบบจึงยังวิเคราะห์ส่วนนี้ได้ไม่แม่น"]

    signals = _lpe_v111_extract_story_signals(story, spec.get("keywords", []))
    preview = story.replace("\n", " ").strip()
    if len(preview) > 160:
        preview = preview[:160].rstrip() + "..."

    summary = [f"สิ่งที่เล่า: {preview}"]
    if signals:
        summary.append("สัญญาณสำคัญที่พบ: " + ", ".join(signals))
    else:
        summary.append("มีข้อมูลแล้ว แต่ควรเพิ่มเวลา/ข้อจำกัด/เป้าหมายให้เฉพาะขึ้น")
    summary.append("ระบบจะใช้ส่วนนี้เพื่อ: " + " / ".join(spec.get("used_for", [])[:3]))
    return summary


def _lpe_v111_build_overall_story_summary(profile) -> tuple[list[str], list[str]]:
    profile = _lpe_v111_story_profile_defaults(profile)
    specs = _lpe_v111_story_mode_specs()
    modes = profile.get("life_story_modes", {})

    summary = []
    missing = []

    for key, spec in specs.items():
        title = spec.get("title", key)
        item = modes.get(key, {})
        story = ""
        if isinstance(item, dict):
            story = str(item.get("story", "")).strip()

        if not story:
            missing.append(title)
            continue

        keywords = []
        for word in spec.get("summary_keywords", []):
            if word and word in story:
                keywords.append(word)

        if keywords:
            summary.append(f"{title}: พบประเด็น {', '.join(keywords[:5])}")
        elif len(story) < 20:
            summary.append(f"{title}: มีข้อมูลแล้ว แต่ยังสั้น ควรเพิ่มรายละเอียดเพื่อให้แผนแม่นขึ้น")
        else:
            summary.append(f"{title}: มีข้อมูลแล้ว ใช้เป็นฐานวางแผนได้")

    return summary, missing


def _lpe_v111_completion_label(profile) -> str:
    profile = _lpe_v111_story_profile_defaults(profile)
    specs = _lpe_v111_story_mode_specs()
    modes = profile.get("life_story_modes", {})
    filled = 0
    for key in specs.keys():
        item = modes.get(key, {})
        if isinstance(item, dict) and str(item.get("story", "")).strip():
            filled += 1

    total = len(specs)
    missing = total - filled
    if filled == total:
        return f"ครบ {filled}/{total} โหมด — พร้อมใช้เป็นฐานชีวิต"
    return f"กรอกแล้ว {filled}/{total} โหมด — ยังขาด {missing} โหมด"


def _lpe_v111_today_key() -> str:
    return str(date.today())


def _lpe_v111_daily_context_defaults(ctx: dict[str, Any] | None = None) -> dict[str, Any]:
    ctx = dict(ctx or {})
    ctx.setdefault("date", _lpe_v111_today_key())
    ctx.setdefault("today_story", "")
    ctx.setdefault("sleep_hours", "")
    ctx.setdefault("energy_level", "3")
    ctx.setdefault("mood", "ปกติ")
    ctx.setdefault("today_shift", "ตามปกติ")
    ctx.setdefault("urgent_events", "")
    ctx.setdefault("physical_condition", "")
    ctx.setdefault("today_main_focus", "")
    ctx.setdefault("today_constraints", "")
    ctx.setdefault("after_save_summary", [])
    ctx.setdefault("updated", "")
    return ctx


def _lpe_v111_get_daily_context() -> dict[str, Any]:
    if "lpe_daily_contexts" not in st.session_state or not isinstance(st.session_state.lpe_daily_contexts, dict):
        st.session_state.lpe_daily_contexts = {}
    today_key = _lpe_v111_today_key()
    existing = st.session_state.lpe_daily_contexts.get(today_key, {})
    return _lpe_v111_daily_context_defaults(existing)


def _lpe_v111_daily_context_summary(ctx: dict[str, Any]) -> list[str]:
    ctx = _lpe_v111_daily_context_defaults(ctx)
    summary: list[str] = []

    try:
        energy = int(str(ctx.get("energy_level", "3")).strip() or "3")
    except Exception:
        energy = 3

    sleep_text = str(ctx.get("sleep_hours", "")).strip()
    try:
        sleep_float = float(sleep_text) if sleep_text else None
    except Exception:
        sleep_float = None

    if sleep_float is not None:
        if sleep_float < 6:
            summary.append("วันนี้นอนน้อย ควรลดงานหนักและกันเวลาพัก/นอน")
        elif sleep_float >= 7:
            summary.append("วันนี้การนอนค่อนข้างพร้อม สามารถวางงานใช้สมาธิได้มากขึ้น")
        else:
            summary.append("วันนี้การนอนระดับกลาง ควรวางแผนแบบไม่อัดแน่นเกินไป")
    else:
        summary.append("ยังไม่รู้จำนวนชั่วโมงนอน แผนพลังงานยังไม่แม่น")

    if energy <= 2:
        summary.append("พลังงานต่ำ ควรใช้แผนขั้นต่ำและมี fallback")
    elif energy == 3:
        summary.append("พลังงานปานกลาง ควรเลือกงานสำคัญ 1 อย่างก่อน")
    else:
        summary.append("พลังงานดี สามารถทำงานหลักและงานรองแบบพอดีได้")

    if str(ctx.get("today_shift", "")).strip() not in {"", "ตามปกติ"}:
        summary.append(f"วันนี้มีบริบทเวร/งาน: {ctx.get('today_shift')}")

    if str(ctx.get("urgent_events", "")).strip():
        summary.append("มีเรื่องด่วนวันนี้ ต้องกันเวลาและลดงานรอง")
    if str(ctx.get("physical_condition", "")).strip():
        summary.append("มีสภาพร่างกาย/อารมณ์ที่ต้องนำไปปรับความหนักของแผน")
    if str(ctx.get("today_main_focus", "")).strip():
        summary.append(f"โฟกัสหลักวันนี้: {ctx.get('today_main_focus')}")
    if str(ctx.get("today_constraints", "")).strip():
        summary.append("มีข้อจำกัดเฉพาะวันนี้ ต้องใช้กำหนดสิ่งที่ควรเลี่ยง")
    if str(ctx.get("today_story", "")).strip():
        summary.append("มีเรื่องเล่าวันนี้แล้ว ระบบสามารถใช้ประกอบแผนรายวันขั้นถัดไป")
    return summary


def _lpe_v111_app_nav_options() -> list[str]:
    return [
        "ตั้งค่าชีวิต",
        "เช็คอินวันนี้",
        "แผนวันนี้",
        "ทบทวนวันนี้",
        "สำรองข้อมูล",
    ]


def _lpe_v111_normalize_route(value) -> str:
    text = str(value or "").strip()
    lowered = text.lower()

    if "เช็คอิน" in text or "check" in lowered:
        return "เช็คอินวันนี้"
    if "ทบทวน" in text or "reflection" in lowered or "result" in lowered:
        return "ทบทวนวันนี้"
    if "สำรอง" in text or "ข้อมูลของฉัน" in text or "backup" in lowered or "export" in lowered or "import" in lowered:
        return "สำรองข้อมูล"
    if "แผนวันนี้" in text or "daily plan" in lowered:
        return "แผนวันนี้"
    if "ตั้งค่าชีวิต" in text:
        return "ตั้งค่าชีวิต"

    # Legacy routes are intentionally hidden from the new product flow.
    return "ตั้งค่าชีวิต"


def _lpe_v111_set_route(route: str) -> None:
    route = _lpe_v111_normalize_route(route)
    st.session_state.lpe_v111_active_route = route
    st.session_state.section = route


def _lpe_v111_global_readability_css() -> None:
    st.markdown(
        "<style>"
        "html,body,.stApp,[data-testid='stAppViewContainer']{background:#0f172a!important;color:#f8fafc!important;}"
        "[data-testid='stSidebar'],[data-testid='stSidebar']>div{background:#1e3a5f!important;}"
        "[data-testid='stSidebar'] *{color:#f8fafc!important;opacity:1!important;}"
        "section.main *{opacity:1!important;text-shadow:none!important;}"
        ".lpe-panel{background:#f8fafc!important;color:#0f172a!important;border:2px solid #cbd5e1!important;border-radius:18px!important;padding:1rem 1.15rem!important;margin:1rem 0!important;}"
        ".lpe-panel *{color:#0f172a!important;opacity:1!important;}"
        ".lpe-head{background:#e0f2fe!important;border-color:#0284c7!important;}"
        ".lpe-next{background:#fef3c7!important;border-color:#f59e0b!important;font-weight:800!important;}"
        "[data-testid='stAlert'],[data-testid='stAlert']>div{background:#fef3c7!important;color:#0f172a!important;border:2px solid #f59e0b!important;border-radius:12px!important;}"
        "[data-testid='stAlert'] *{color:#0f172a!important;opacity:1!important;font-weight:700!important;}"
        "textarea,input,[data-baseweb='textarea'] textarea,[data-baseweb='input'] input,.stTextArea textarea,.stTextInput input{background:#ffffff!important;color:#0f172a!important;border:2px solid #2563eb!important;border-radius:12px!important;font-size:1rem!important;line-height:1.55!important;caret-color:#0f172a!important;opacity:1!important;}"
        "textarea::placeholder,input::placeholder{color:#64748b!important;opacity:1!important;}"
        "[data-baseweb='select'],[data-baseweb='select'] *,[role='listbox'],[role='listbox'] *,[data-testid='stSelectbox'] *{background:#ffffff!important;color:#0f172a!important;opacity:1!important;}"
        "[data-baseweb='popover'] *,[data-baseweb='menu'] *,[role='option']{background:#ffffff!important;color:#0f172a!important;opacity:1!important;}"
        "div[data-testid='stButton'] button{background:#16a34a!important;color:#ffffff!important;border:2px solid #15803d!important;border-radius:12px!important;font-weight:900!important;opacity:1!important;}"
        "div[data-testid='stButton'] button *{color:#ffffff!important;opacity:1!important;}"
        "[data-testid='stRadio'] label{background:#ffffff!important;border:1px solid #cbd5e1!important;border-radius:10px!important;padding:.25rem .55rem!important;}"
        "[data-testid='stRadio'] label *,[data-testid='stRadio'] span{color:#0f172a!important;opacity:1!important;}"
        "hr{border-color:#e2e8f0!important;opacity:1!important;}"
        "</style>",
        unsafe_allow_html=True,
    )
# === LPE_V1_11_STEP2_3_CLEAN_CONSOLIDATED_CORE_END ===


def render_nav() -> str:
    options = _lpe_v111_app_nav_options()
    active = _lpe_v111_normalize_route(
        st.session_state.get("lpe_v111_active_route", st.session_state.get("section", "ตั้งค่าชีวิต"))
    )
    if active not in options:
        active = "ตั้งค่าชีวิต"

    st.sidebar.markdown("### 🎯 ผู้ช่วยจัดลำดับชีวิต")
    st.sidebar.caption("เลือกขั้นตอนที่ต้องการทำ")
    with st.sidebar:
        sidebar_choice = st.selectbox(
            "มุมมองสำหรับจอใหญ่",
            options,
            index=options.index(active),
            key="lpe_v111_sidebar_route_clean",
        )

    st.info("เลือกสิ่งที่ต้องการทำ แล้วระบบจะแสดงเฉพาะส่วนนั้น")
    main_choice = st.selectbox(
        "เมนูหลัก",
        options,
        index=options.index(_lpe_v111_normalize_route(sidebar_choice)),
        key="lpe_v111_main_route_clean",
    )

    active = _lpe_v111_normalize_route(main_choice)
    st.session_state.lpe_v111_active_route = active
    st.session_state.section = active
    return active


def render_cards(profile: dict[str, Any], missions: list[dict[str, Any]]) -> None:
    summary = st.session_state.get("lpe_saved_summary")
    score_text = "ยังไม่บันทึก" if not summary else f"{summary['score']}/100"
    mode_text = mode_label(profile.get("start_mode", "วันพลังพร้อม")) if not summary else summary["mode"]
    avoid = generate_missions(profile)[1][0]
    cols = st.columns(4)
    values = [
        ("จำนวนภารกิจวันนี้", f"{len(missions)}", "รายการ"),
        ("คะแนนล่าสุด", score_text, "หลังบันทึกผล"),
        ("โหมดของวัน", mode_text, "ตามพลังและความปลอดภัย"),
        ("สิ่งที่ต้องระวัง", avoid[:36] + ("..." if len(avoid) > 36 else ""), "วันนี้"),
    ]
    for col, (label, value, sub) in zip(cols, values):
        with col:
            st.markdown(f'<div class="card"><div class="card-label">{label}</div><div class="card-value">{value}</div><div class="card-label">{sub}</div></div>', unsafe_allow_html=True)


def render_pills(profile: dict[str, Any]) -> None:
    plan_date = parse_date(profile.get("plan_date"))
    dte = max(days_to_exam(profile, plan_date), 0)
    st.markdown(
        f"""
        <div class="pill-row">
            <span class="pill">🗓️ {plan_date.strftime('%d/%m/%Y')}</span>
            <span class="pill">● {mode_label(profile.get('start_mode', 'วันพลังพร้อม'))}</span>
            <span class="pill">◷ {profile.get('shift', 'วันหยุด')}</span>
            <span class="pill">📚 {profile.get('subject', 'วิชาหลัก')} · เหลือ {dte} วัน</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mission_card(mission: dict[str, Any], index: int, with_review: bool = True) -> None:
    kind = mission["kind"]
    kind_th = {"must": "ต้องทำ", "should": "ควรทำ", "could": "ทำได้ถ้ามีแรง"}[kind]
    st.markdown(
        f"""
        <div class="mission-card {kind}">
            <div class="mission-meta">{index:02d} <span class="badge {kind}">{kind_th}</span></div>
            <div class="mission-title">{mission['title']}</div>
            <div><span class="pill">◆ {mission['tag']}</span><span class="pill">◷ {mission['minutes']}</span></div>
            <hr style="border:none;border-top:1px solid #eee3d4;margin:14px 0;">
            <div class="mission-meta"><b>เหตุผล:</b> {mission['reason']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if with_review:
        st.caption("วันนี้ทำภารกิจนี้ได้แค่ไหน?")
        cols = st.columns([2, 1.1, 1.1])
        with cols[0]:
            status = st.radio(
                "สถานะ",
                ["ทำครบ", "ทำบางส่วน", "ไม่ได้ทำ", "มีปัญหา"],
                horizontal=True,
                key=f"status_{mission['id']}",
                label_visibility="collapsed",
            )
        st.session_state.lpe_review.setdefault(mission["id"], {})
        st.session_state.lpe_review[mission["id"]]["status"] = status
        if status != "ทำครบ":
            with cols[1]:
                amount = st.number_input("ทำได้จริงเท่าไร", min_value=0, max_value=300, value=0, step=5, key=f"amount_{mission['id']}")
            with cols[2]:
                unit = st.selectbox("หน่วย", ["นาที", "บท", "ครั้ง", "รายการ"], key=f"unit_{mission['id']}")
            reason = st.selectbox(
                "เหตุผล/ปัญหา",
                ["ไม่มีเวลา", "เวรหนัก", "เหนื่อย", "นอนน้อย", "ตะคริว", "เวียนหัวมาก", "เป็นลม", "เจ็บหน้าอก", "ป่วย", "งานแทรก", "อื่น ๆ"],
                key=f"reason_{mission['id']}",
            )
            st.session_state.lpe_review[mission["id"]].update({"amount": amount, "unit": unit, "reason": reason})
        else:
            st.session_state.lpe_review[mission["id"]].update({"amount": mission.get("minutes", ""), "unit": "", "reason": ""})


def page_today() -> None:
    profile = st.session_state.lpe_profile
    missions, avoid = generate_missions(profile)
    render_hero("วันนี้ต้องทำอะไร", "เริ่มจากสิ่งสำคัญ ทำตามพลังจริง แล้วบันทึกผลในจุดเดียว")
    render_demo_warning()
    render_demo_about()
    if st.session_state.pop("lpe_onboarding_complete_notice", False):
        st.success("สร้างแผนวันนี้แล้ว เริ่มจากภารกิจแรกได้เลย")
    render_cards(profile, missions)
    render_pills(profile)

    st.markdown('<div class="section-title">🎯 ภารกิจวันนี้</div><div class="section-subtitle">ทำตามลำดับ แล้วเลือกผลใต้แต่ละภารกิจเมื่อจบวัน</div>', unsafe_allow_html=True)
    st.markdown('<div class="safe-note">⊙ เริ่มจากการ์ดแรก แล้วค่อยดูว่ายังมีพลังพอสำหรับงานถัดไปไหม</div>', unsafe_allow_html=True)

    for i, mission in enumerate(missions, 1):
        render_mission_card(mission, i)

    st.markdown('<div class="danger-note">⊘ วันนี้ยังไม่ควรทำ<br>' + "<br>".join([f"• {x}" for x in avoid]) + "</div>", unsafe_allow_html=True)

    if st.button("บันทึกผลวันนี้", type="primary", use_container_width=True):
        save_review(missions)
        st.success("บันทึกผลวันนี้แล้ว")
        st.rerun()

    if st.session_state.lpe_saved_summary:
        summary = st.session_state.lpe_saved_summary
        st.markdown('<div class="section-title">สรุปวันนี้</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("คะแนนวันนี้", f"{summary['score']}/100")
        c2.metric("โหมดของวัน", summary["mode"])
        c3.metric("อุปสรรคหลัก", summary["blocker"])
        if summary["has_serious"]:
            st.warning("มีสัญญาณร่างกายที่ควรระวัง หากเป็นลม เจ็บหน้าอก หายใจไม่ออก หรือเวียนหัวรุนแรง ควรปรึกษาบุคลากรสุขภาพ")


def render_onboarding_step(step: int, title: str, description: str) -> None:
    st.progress(step / 4, text=f"ขั้นที่ {step} จาก 4")
    st.markdown(
        f'<div class="onboarding-step"><strong>{title}</strong><span>{description}</span></div>',
        unsafe_allow_html=True,
    )


def page_onboarding() -> None:
    profile = st.session_state.lpe_profile
    step = int(st.session_state.get("lpe_onboarding_step", 1))
    render_hero("เริ่มต้นใช้งาน", "ตอบทีละขั้น แล้วระบบจะสร้างแผนวันนี้ให้", "🧭")
    render_demo_warning()
    render_demo_about()

    if step == 1:
        render_onboarding_step(
            1,
            "เป้าหมายหลักของคุณตอนนี้คืออะไร",
            "บอกสิ่งเดียวที่อยากกันเวลาไว้ก่อน เช่น วิชาที่ต้องสอบ หรืองานสำคัญ",
        )
        with st.form("onboarding_goal_form"):
            subject = st.text_input(
                "เป้าหมายหลัก",
                value=clean_public_text(profile.get("subject"), "วิชาหลักของคุณ"),
                placeholder="เช่น วิชาหลักของคุณ",
            )
            st.caption("ใช้ข้อความสั้น ๆ เพื่อให้ชื่อภารกิจอ่านง่าย")
            next_step = st.form_submit_button(
                "ต่อไป: วันสอบหรือเดดไลน์", type="primary", use_container_width=True
            )
        if next_step:
            profile["subject"] = subject.strip() or "วิชาหลักของคุณ"
            st.session_state.lpe_onboarding_step = 2
            st.rerun()
        return

    if st.button("← ย้อนกลับ", key=f"onboarding_back_{step}"):
        st.session_state.lpe_onboarding_step = step - 1
        st.rerun()

    if step == 2:
        render_onboarding_step(
            2,
            "มีวันสอบหรือเดดไลน์เมื่อไร",
            "วันที่นี้ช่วยให้ระบบรู้ว่าควรเพิ่มเวลาอ่านและลดงานรองเมื่อไร",
        )
        with st.form("onboarding_deadline_form"):
            exam_date = st.date_input(
                "วันสอบ/เดดไลน์",
                value=parse_date(profile.get("exam_date"), date.today() + timedelta(days=24)),
            )
            study_minutes = st.number_input(
                "เวลาอ่านหรือทำงานหลักต่อวันที่ตั้งใจไว้",
                min_value=10,
                max_value=240,
                value=int(profile.get("study_minutes", 60)),
                step=5,
                help="ตั้งเป็นเวลาที่ทำได้จริง ไม่จำเป็นต้องมากที่สุด",
            )
            next_step = st.form_submit_button(
                "ต่อไป: พลังของวันนี้", type="primary", use_container_width=True
            )
        if next_step:
            profile["exam_date"] = exam_date
            profile["study_minutes"] = int(study_minutes)
            st.session_state.lpe_onboarding_step = 3
            st.rerun()
        return

    if step == 3:
        render_onboarding_step(
            3,
            "วันนี้พลังคุณเป็นแบบไหน",
            "เลือกตามสภาพจริง เพื่อไม่ให้แผนหนักเกินกำลัง",
        )
        with st.form("onboarding_energy_form"):
            energy_options = ["วันพลังพร้อม", "วันพลังจำกัด", "วันพักฟื้น"]
            start_mode = st.radio(
                "พลังวันนี้",
                energy_options,
                index=energy_options.index(mode_label(profile.get("start_mode", "วันพลังพร้อม"))),
                captions=["ทำงานหลักและงานรองสั้น ๆ ได้", "ลดงานรองและเผื่อเวลาพัก", "ทำเฉพาะสิ่งจำเป็นและพักให้พอ"],
            )
            with st.expander("ข้อมูลเสริม (ไม่จำเป็น)", expanded=False):
                shift_options = ["วันหยุด", "เวรเช้า", "เวรบ่าย", "เวรดึก", "งานหนัก", "ไม่แน่ใจ"]
                current_shift = thai_shift(profile.get("shift"))
                shift = st.selectbox(
                    "งานหรือเวรวันนี้",
                    shift_options,
                    index=shift_options.index(current_shift) if current_shift in shift_options else 0,
                )
                health_goal = st.text_input(
                    "แนวทางดูแลตัวเอง",
                    value=clean_public_text(profile.get("health_goal"), "ขยับเบา ๆ หรือพักให้พอ"),
                    placeholder="เช่น ขยับเบา ๆ หรือพักให้พอ",
                )
                project_name = st.text_input(
                    "โปรเจกต์ที่ทำเมื่อมีแรงเหลือ",
                    value=clean_public_text(profile.get("project_name"), "โปรเจกต์ส่วนตัวของคุณ"),
                )
                garden_task = st.text_input(
                    "งานบ้านหรือสวนที่อยากไม่ลืม",
                    value=clean_public_text(profile.get("garden_task"), "งานบ้านหรือสวนที่อยากไม่ลืม"),
                )
                calorie_note = st.text_input(
                    "แนวทางอาหารที่คุณกำหนดเอง",
                    value=str(profile.get("calorie_note", "")),
                    placeholder="เช่น กินให้ครบมื้อ หรือเว้นว่างไว้",
                )
            next_step = st.form_submit_button(
                "ต่อไป: ตรวจแผน", type="primary", use_container_width=True
            )
        if next_step:
            profile.update(
                {
                    "start_mode": start_mode,
                    "shift": shift,
                    "health_goal": health_goal.strip() or "ขยับเบา ๆ หรือพักให้พอ",
                    "project_name": project_name.strip() or "โปรเจกต์ส่วนตัวของคุณ",
                    "garden_task": garden_task.strip() or "งานบ้านหรือสวนที่อยากไม่ลืม",
                    "calorie_note": calorie_note.strip(),
                }
            )
            st.session_state.lpe_onboarding_step = 4
            st.rerun()
        return

    render_onboarding_step(
        4,
        "สร้างแผนวันนี้",
        "ตรวจข้อมูลสั้น ๆ แล้วเริ่มจากภารกิจสำคัญที่สุด",
    )
    st.markdown(
        f"""
        <div class="card">
            <div class="card-label">เป้าหมายหลัก</div>
            <div class="card-value">{profile.get('subject', 'วิชาหลักของคุณ')}</div>
            <div class="card-label">เดดไลน์ {parse_date(profile.get('exam_date')):%d/%m/%Y} · {profile.get('study_minutes', 60)} นาทีต่อวัน · {mode_label(profile.get('start_mode', 'วันพลังพร้อม'))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("สร้างแผนวันนี้", type="primary", use_container_width=True):
        st.session_state.lpe_saved_summary = None
        st.session_state.lpe_onboarding_step = 1
        st.session_state.lpe_onboarding_complete_notice = True
        navigate_to("วันนี้ต้องทำอะไร")
        st.rerun()


def page_tomorrow() -> None:
    profile = dict(st.session_state.lpe_profile)
    profile["plan_date"] = parse_date(profile.get("plan_date")) + timedelta(days=1)
    missions, avoid = generate_missions(st.session_state.lpe_profile, for_tomorrow=True)
    render_hero("แผนพรุ่งนี้", "ไม่ใช่การลงโทษจากวันนี้ แต่เป็นการปรับเส้นทางจากผลจริง", "🌤️")
    if st.session_state.lpe_saved_summary:
        s = st.session_state.lpe_saved_summary
        st.info(f"ผลล่าสุด: {s['score']}/100 · โหมด {s['mode']} · อุปสรรคหลัก: {s['blocker']}")
    else:
        st.warning("ยังไม่มีผลสรุปวันนี้ ระบบจะแสดงแผนพรุ่งนี้แบบประมาณการ")
    for i, mission in enumerate(missions, 1):
        render_mission_card(mission, i, with_review=False)
    st.markdown('<div class="danger-note">⊘ พรุ่งนี้ยังไม่ควรทำ<br>' + "<br>".join([f"• {x}" for x in avoid]) + "</div>", unsafe_allow_html=True)


def page_daily_detail() -> None:
    profile = st.session_state.lpe_profile
    render_hero("แผนละเอียดรายวัน", "แบ่งช่วงเวลาแบบง่ายเพื่อให้ทำได้จริง ไม่ใช่ตารางแน่นเกินไป", "🕘")
    meals = "กินให้ครบมื้อ ดื่มน้ำ และเลือกอาหารย่อยง่าย"
    if profile.get("calorie_note"):
        meals += f" · เป้าหมายที่ผู้ใช้ตั้งไว้: {profile.get('calorie_note')}"
    rows = [
        ("เช้า", "อ่านหัวข้อหลัก 25–30 นาที", "เริ่มจากบทที่ 1 ของ " + str(profile.get("subject", "วิชาหลัก"))),
        ("กลางวัน", meals, "เป็นคำแนะนำทั่วไป ไม่ใช่คำแนะนำทางการแพทย์"),
        ("เย็น", str(profile.get("health_goal", "ขยับเบา ๆ หรือพักฟื้น")), "เดิน/ยืดเหยียดเบา ๆ 10–20 นาที ถ้าร่างกายพร้อม"),
        ("ก่อนนอน", "บันทึกผลวันนี้", "ใช้เวลา 3 นาทีเพื่อให้แผนพรุ่งนี้แม่นขึ้น"),
    ]
    for period, task, note in rows:
        st.markdown(f'<div class="card"><div class="card-label">{period}</div><div class="card-value">{task}</div><div class="card-label">{note}</div></div><br>', unsafe_allow_html=True)


def page_30day() -> None:
    profile = st.session_state.lpe_profile
    st.button("← กลับไปเพิ่มเติม", on_click=navigate_to, args=("เพิ่มเติม",))
    render_hero("ภาพรวม 30 วัน", "ใช้เป็นเข็มทิศคร่าว ๆ แผนจริงยังต้องปรับจากผลแต่ละวัน", "🗺️")
    start = parse_date(profile.get("plan_date"))
    rows = []
    for i in range(30):
        d = start + timedelta(days=i)
        dte = max((parse_date(profile.get("exam_date")) - d).days, 0)
        if dte <= 7:
            focus = "เน้นอ่านสอบ"
            study = "เข้มข้น 60–90 นาที"
            project = "พักโปรเจกต์"
        elif dte <= 30:
            focus = "อ่านสม่ำเสมอ"
            study = f"{int(profile.get('study_minutes', 60))} นาที"
            project = "ทำได้ไม่เกิน 30 นาทีหลังงานหลัก"
        else:
            focus = "รักษาระบบชีวิต"
            study = "ทบทวนเบา"
            project = "ทำได้ถ้ามีแรง"
        rows.append(
            {
                "วันที่": d.strftime("%Y-%m-%d"),
                "แนวโน้มวัน": focus,
                "เป้าหมายหลัก": profile.get("subject", "วิชาหลัก"),
                "เวลาอ่าน": study,
                "โปรเจกต์/สวน": project,
                "พัก/ฟื้นตัว": "นอนให้พอและไม่ชดเชยหนักเกินจริง",
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)


def page_more() -> None:
    render_hero("เพิ่มเติม", "เปิดดูภาพระยะยาวหรือปรับข้อมูลเมื่อจำเป็น", "•••")
    left, right = st.columns(2)
    with left:
        st.markdown(
            '<div class="card"><div class="card-label">มองล่วงหน้า</div><div class="card-value">ภาพรวม 30 วัน</div><div class="card-label">ดูแนวโน้มแบบคร่าว ๆ โดยไม่รบกวนหน้าวันนี้</div></div>',
            unsafe_allow_html=True,
        )
        st.button(
            "เปิดภาพรวม 30 วัน",
            key="open_30_day",
            use_container_width=True,
            on_click=navigate_to,
            args=("ภาพรวม 30 วัน",),
        )
    with right:
        st.markdown(
            '<div class="card"><div class="card-label">ปรับข้อมูล</div><div class="card-value">ตั้งค่าชีวิต</div><div class="card-label">ดูหรือแก้ข้อมูลทดลองที่ใช้สร้างแผน</div></div>',
            unsafe_allow_html=True,
        )
        st.button(
            "เปิดตั้งค่าชีวิต",
            key="open_settings",
            use_container_width=True,
            on_click=navigate_to,
            args=("ตั้งค่าชีวิต",),
        )
    render_demo_about()

def page_settings() -> None:
    st.markdown(
        "<div class='lpe-panel lpe-head'>"
        "<h1>⚙️ ตั้งค่าชีวิต</h1>"
        "<p><b>เป้าหมายของหน้านี้:</b> เล่าเรื่องชีวิต 5 โหมด เพื่อให้ระบบเข้าใจคุณก่อนสร้างแผนรายวัน</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    profile = _lpe_v111_story_profile_defaults(st.session_state.get("lpe_profile", {}))
    st.session_state.lpe_profile = profile
    specs = _lpe_v111_story_mode_specs()

    st.info("นี่คือ Core Life Profile ระยะยาว หลังบันทึกแล้วให้ไป Step 2: เช็คอินวันนี้")
    st.metric("ความครบของตั้งค่าชีวิต", _lpe_v111_completion_label(profile))

    for idx, (mode_key, spec) in enumerate(specs.items(), start=1):
        st.markdown(
            f"<div class='lpe-panel'><h3>{spec['title']}</h3><p>{spec['short']}</p></div>",
            unsafe_allow_html=True,
        )
        with st.expander("คำถามนำทาง", expanded=(idx == 1)):
            for prompt in spec.get("questions", spec.get("prompts", [])):
                st.markdown(f"- {prompt}")

        current_story = profile.get("life_story_modes", {}).get(mode_key, {}).get("story", "")
        st.text_area(
            f"ช่องเล่าเรื่องโหมดที่ {idx}",
            value=str(current_story),
            key=f"lpe_story_clean_{mode_key}",
            height=140,
            placeholder=spec.get("placeholder", "เล่าเป็นข้อ ๆ หรือเล่าเป็นเรื่องเดียวก็ได้ เน้นข้อมูลจริงที่ระบบควรรู้ก่อนวางแผน"),
        )

        live_story = st.session_state.get(f"lpe_story_clean_{mode_key}", current_story)
        with st.expander("ระบบเข้าใจเบื้องต้น / ใช้ข้อมูลนี้เพื่อ", expanded=False):
            for line in _lpe_v111_story_mode_summary(mode_key, live_story):
                st.markdown(f"- {line}")
            st.markdown("**ระบบจะใช้ข้อมูลนี้เพื่อ:**")
            for line in spec.get("use_for", spec.get("used_for", [])):
                st.markdown(f"- {line}")

    if st.button("บันทึกตั้งค่าชีวิต 5 โหมด", type="primary", use_container_width=True, key="save_life_story_clean"):
        profile = _lpe_v111_story_profile_defaults(st.session_state.get("lpe_profile", {}))
        for mode_key, spec in specs.items():
            story = str(st.session_state.get(f"lpe_story_clean_{mode_key}", "")).strip()
            profile["life_story_modes"][mode_key] = {
                "title": spec["title"],
                "story": story,
                "last_summary": _lpe_v111_story_mode_summary(mode_key, story),
                "updated": str(date.today()),
            }
        overall, missing = _lpe_v111_build_overall_story_summary(profile)
        profile["life_story_profile_summary"] = overall
        profile["life_story_missing_modes"] = missing
        profile["life_story_last_updated"] = str(date.today())
        st.session_state.lpe_profile = profile
        _lpe_v111_save_local_snapshot("settings_profile_saved")
        st.success("บันทึกตั้งค่าชีวิตใน session แล้ว")

    profile = _lpe_v111_story_profile_defaults(st.session_state.get("lpe_profile", {}))
    overall, missing = _lpe_v111_build_overall_story_summary(profile)
    st.subheader("สรุปภาพรวมที่ระบบเข้าใจ")
    for item in overall:
        st.markdown(f"- {item}")

    if missing:
        st.warning("โหมดที่ยังควรเล่าเพิ่ม: " + ", ".join(missing))
    else:
        st.success("ครบทั้ง 5 โหมดแล้ว พร้อมไปเช็คอินวันนี้")

    st.markdown(
        "<div class='lpe-panel lpe-next'>ขั้นต่อไป: ไปหน้า <b>เช็คอินวันนี้</b> เพื่อกรอกข้อมูลเฉพาะวันนี้</div>",
        unsafe_allow_html=True,
    )
    st.button(
        "ไปเช็คอินวันนี้",
        use_container_width=True,
        key="go_daily_checkin_clean",
        on_click=_lpe_v111_set_route,
        args=("เช็คอินวันนี้",),
    )


def _lpe_v110b3_sync_pending_navigation() -> None:
    """Sync pending route before Streamlit navigation widgets are instantiated."""
    pending_page = st.session_state.pop("_lpe_pending_page", None)
    if not pending_page:
        return
    pending_page = str(pending_page).strip()
    st.session_state["lpe_current_page"] = pending_page

    try:
        if "DESTINATION_TO_PRIMARY_NAV" in globals():
            mobile_label = DESTINATION_TO_PRIMARY_NAV.get(pending_page)
            if mobile_label:
                st.session_state["lpe_nav_mobile"] = mobile_label
        if "DESKTOP_NAV_ITEMS" in globals() and pending_page in DESKTOP_NAV_ITEMS:
            st.session_state["lpe_nav_desktop"] = pending_page
            st.session_state["lpe_sidebar_nav"] = pending_page
            st.session_state["lpe_nav_sidebar"] = pending_page
    except Exception:
        st.session_state["lpe_current_page"] = pending_page


def _lpe_v110b3_readability_css() -> None:
    """Focused readability CSS for sidebar/nav/metric/setting pages."""
    st.markdown('\n<style id="lpe-v110b3-stabilization">\n:root {\n  --lpe-v3-navy: #203254;\n  --lpe-v3-ink: #101827;\n  --lpe-v3-muted: #334155;\n  --lpe-v3-border: #d6deeb;\n  --lpe-v3-active: #6d4df2;\n  --lpe-v3-red: #ff4b5c;\n  --lpe-v3-cream: #fffaf0;\n}\n\n[data-testid="stAppViewContainer"] .block-container,\n[data-testid="stAppViewContainer"] .block-container p,\n[data-testid="stAppViewContainer"] .block-container span,\n[data-testid="stAppViewContainer"] .block-container li,\n[data-testid="stAppViewContainer"] .block-container label {\n  color: var(--lpe-v3-ink) !important;\n  opacity: 1 !important;\n}\n\n.lpe-hero, .hero, .header-card, .title-card,\ndiv[class*="hero"], div[class*="Header"], div[class*="header"] {\n  background-color: var(--lpe-v3-navy);\n}\n.lpe-hero *, .hero *, .header-card *, .title-card *,\ndiv[class*="hero"] *, div[class*="Header"] *, div[class*="header"] * {\n  color: #ffffff !important;\n  opacity: 1 !important;\n}\n\nsection[data-testid="stSidebar"] {\n  background: var(--lpe-v3-navy) !important;\n}\nsection[data-testid="stSidebar"] h1,\nsection[data-testid="stSidebar"] h2,\nsection[data-testid="stSidebar"] h3,\nsection[data-testid="stSidebar"] p,\nsection[data-testid="stSidebar"] span,\nsection[data-testid="stSidebar"] label,\nsection[data-testid="stSidebar"] small {\n  color: #ffffff !important;\n  opacity: 1 !important;\n}\n\nsection[data-testid="stSidebar"] [data-testid="stSelectbox"] label p,\nsection[data-testid="stSidebar"] [data-testid="stSelectbox"] label span {\n  color: #ffffff !important;\n  font-weight: 800 !important;\n}\nsection[data-testid="stSidebar"] div[data-baseweb="select"] > div {\n  background: #ffffff !important;\n  border: 2px solid #b8c2d8 !important;\n  color: var(--lpe-v3-ink) !important;\n  min-height: 48px !important;\n}\nsection[data-testid="stSidebar"] div[data-baseweb="select"] span,\nsection[data-testid="stSidebar"] div[data-baseweb="select"] div,\nsection[data-testid="stSidebar"] div[data-baseweb="select"] input {\n  color: var(--lpe-v3-ink) !important;\n  opacity: 1 !important;\n}\nsection[data-testid="stSidebar"] div[data-baseweb="select"] svg {\n  fill: var(--lpe-v3-ink) !important;\n  color: var(--lpe-v3-ink) !important;\n}\n\nsection[data-testid="stSidebar"] button,\nsection[data-testid="stSidebar"] [data-testid="stButton"] button {\n  background: #ffffff !important;\n  color: var(--lpe-v3-ink) !important;\n  border: 1px solid #cbd5e1 !important;\n  min-height: 44px !important;\n  font-weight: 800 !important;\n}\nsection[data-testid="stSidebar"] button *,\nsection[data-testid="stSidebar"] [data-testid="stButton"] button * {\n  color: var(--lpe-v3-ink) !important;\n  opacity: 1 !important;\n}\n\n[data-testid="stRadio"] div[role="radiogroup"] label {\n  background: #ffffff !important;\n  border: 1px solid var(--lpe-v3-border) !important;\n  color: var(--lpe-v3-ink) !important;\n  min-height: 42px !important;\n}\n[data-testid="stRadio"] div[role="radiogroup"] label *,\n[data-testid="stRadio"] div[role="radiogroup"] label p,\n[data-testid="stRadio"] div[role="radiogroup"] label span {\n  color: var(--lpe-v3-ink) !important;\n  opacity: 1 !important;\n  visibility: visible !important;\n  font-weight: 800 !important;\n}\n[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {\n  background: var(--lpe-v3-navy) !important;\n  border-color: var(--lpe-v3-navy) !important;\n}\n[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) *,\n[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p,\n[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) span {\n  color: #ffffff !important;\n}\n\n[data-testid="stMetric"],\n[data-testid="stMetric"] *,\ndiv[class*="metric"] *,\ndiv[class*="summary"] *,\ndiv[class*="card"] .metric *,\ndiv[class*="card"] .summary * {\n  color: var(--lpe-v3-ink) !important;\n  opacity: 1 !important;\n}\n[data-testid="stMetricValue"],\n[data-testid="stMetricDelta"],\n[data-testid="stMetricLabel"] {\n  color: var(--lpe-v3-ink) !important;\n}\n\n[data-testid="stExpander"] summary,\n[data-testid="stExpander"] summary *,\n[data-testid="stExpander"] p,\n[data-testid="stExpander"] li {\n  color: var(--lpe-v3-ink) !important;\n  opacity: 1 !important;\n}\n\n[data-testid="stTextInput"] label,\n[data-testid="stTextArea"] label,\n[data-testid="stSelectbox"] label,\n[data-testid="stNumberInput"] label,\n[data-testid="stDateInput"] label,\n[data-testid="stSlider"] label,\n[data-testid="stMultiSelect"] label {\n  color: var(--lpe-v3-ink) !important;\n  font-weight: 850 !important;\n  opacity: 1 !important;\n}\n\n@media (max-width: 820px) {\n  section[data-testid="stSidebar"] {\n    display: none !important;\n  }\n  .block-container {\n    padding-left: 1rem !important;\n    padding-right: 1rem !important;\n    max-width: 100% !important;\n  }\n  [data-testid="stRadio"] div[role="radiogroup"] {\n    display: flex !important;\n    flex-wrap: nowrap !important;\n    overflow-x: auto !important;\n    gap: 8px !important;\n    padding-bottom: 6px !important;\n  }\n  [data-testid="stRadio"] div[role="radiogroup"] label {\n    flex: 0 0 auto !important;\n    white-space: nowrap !important;\n    min-width: max-content !important;\n    max-width: 82vw !important;\n  }\n  [data-testid="column"] {\n    min-width: 100% !important;\n  }\n}\n</style>\n', unsafe_allow_html=True)
# === LPE_V1_10B_3_NAV_STATE_READABILITY_HELPERS_END ===

def page_daily_checkin() -> None:
    st.markdown(
        "<div class='lpe-panel lpe-head'>"
        "<h1>✅ เช็คอินวันนี้</h1>"
        "<p><b>เป้าหมาย:</b> บอกระบบว่าวันนี้ต่างจากชีวิตปกติอย่างไร ก่อนสร้างแผนวันนี้</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    ctx = _lpe_v111_get_daily_context()
    st.info("Step 2 ยังเป็น session-only: ใช้กรอกข้อมูลเฉพาะวันนี้และสรุปเบื้องต้น ยังไม่ใช่ Daily Plan Engine")

    col1, col2 = st.columns(2)
    with col1:
        sleep_hours = st.text_input(
            "เมื่อคืน/วันนี้นอนกี่ชั่วโมง",
            value=str(ctx.get("sleep_hours", "")),
            placeholder="เช่น 5.5 หรือ 7",
            key="lpe_today_sleep_hours_clean",
        )
    with col2:
        energy_level = st.select_slider(
            "พลังงานวันนี้",
            options=["1", "2", "3", "4", "5"],
            value=str(ctx.get("energy_level", "3")),
            key="lpe_today_energy_level_clean",
        )

    mood = st.text_input(
        "อารมณ์วันนี้",
        value=str(ctx.get("mood", "ปกติ")),
        placeholder="เช่น ปกติ / เครียด / ง่วง / สดชื่น",
        key="lpe_today_mood_clean",
    )
    today_shift = st.text_input(
        "วันนี้มีเวร/งาน/เวลาผูกมัดอะไร",
        value=str(ctx.get("today_shift", "ตามปกติ")),
        placeholder="เช่น เวรเช้า 08:00-16:00 / วันหยุด / มีนัด",
        key="lpe_today_shift_clean",
    )
    today_main_focus = st.text_input(
        "วันนี้อยากเน้นอะไรเป็นพิเศษ",
        value=str(ctx.get("today_main_focus", "")),
        placeholder="เช่น อ่านหนังสือ 30 นาที / พักให้พอ / เดินเบา ๆ",
        key="lpe_today_main_focus_clean",
    )
    urgent_events = st.text_area(
        "เรื่องด่วนหรือเหตุการณ์พิเศษวันนี้",
        value=str(ctx.get("urgent_events", "")),
        height=90,
        placeholder="เช่น มีธุระด่วน งานแทรก ฝนตก ต้องเดินทาง",
        key="lpe_today_urgent_events_clean",
    )
    physical_condition = st.text_area(
        "สภาพร่างกาย/อารมณ์ที่ต้องระวัง",
        value=str(ctx.get("physical_condition", "")),
        height=90,
        placeholder="เช่น ปวดหัว เจ็บเข่า ง่วงมาก เครียด ไม่มีแรง",
        key="lpe_today_physical_condition_clean",
    )
    today_constraints = st.text_area(
        "ข้อจำกัดของวันนี้",
        value=str(ctx.get("today_constraints", "")),
        height=90,
        placeholder="เช่น ห้ามนอนดึก พรุ่งนี้เวรเช้า มีเวลาแค่ 1 ชั่วโมง",
        key="lpe_today_constraints_clean",
    )
    today_story = st.text_area(
        "เล่าเรื่องวันนี้เพิ่มเติม",
        value=str(ctx.get("today_story", "")),
        height=120,
        placeholder="เล่าว่าวันนี้เกิดอะไรขึ้น รู้สึกอย่างไร และอยากให้ระบบช่วยปรับแผนตรงไหน",
        key="lpe_today_story_clean",
    )

    if st.button("บันทึกเช็คอินวันนี้", type="primary", use_container_width=True, key="save_daily_checkin_clean"):
        saved = _lpe_v111_daily_context_defaults(
            {
                "date": _lpe_v111_today_key(),
                "today_story": today_story,
                "sleep_hours": sleep_hours,
                "energy_level": energy_level,
                "mood": mood,
                "today_shift": today_shift,
                "urgent_events": urgent_events,
                "physical_condition": physical_condition,
                "today_main_focus": today_main_focus,
                "today_constraints": today_constraints,
                "updated": str(date.today()),
            }
        )
        saved["after_save_summary"] = _lpe_v111_daily_context_summary(saved)
        if "lpe_daily_contexts" not in st.session_state or not isinstance(st.session_state.lpe_daily_contexts, dict):
            st.session_state.lpe_daily_contexts = {}
        st.session_state.lpe_daily_contexts[_lpe_v111_today_key()] = saved
        _lpe_v111_save_local_snapshot("daily_checkin_saved")
        st.success("บันทึกเช็คอินวันนี้ใน session แล้ว")

    live_ctx = _lpe_v111_daily_context_defaults(
        {
            "date": _lpe_v111_today_key(),
            "today_story": st.session_state.get("lpe_today_story_clean", ctx.get("today_story", "")),
            "sleep_hours": st.session_state.get("lpe_today_sleep_hours_clean", ctx.get("sleep_hours", "")),
            "energy_level": st.session_state.get("lpe_today_energy_level_clean", ctx.get("energy_level", "3")),
            "mood": st.session_state.get("lpe_today_mood_clean", ctx.get("mood", "ปกติ")),
            "today_shift": st.session_state.get("lpe_today_shift_clean", ctx.get("today_shift", "ตามปกติ")),
            "urgent_events": st.session_state.get("lpe_today_urgent_events_clean", ctx.get("urgent_events", "")),
            "physical_condition": st.session_state.get("lpe_today_physical_condition_clean", ctx.get("physical_condition", "")),
            "today_main_focus": st.session_state.get("lpe_today_main_focus_clean", ctx.get("today_main_focus", "")),
            "today_constraints": st.session_state.get("lpe_today_constraints_clean", ctx.get("today_constraints", "")),
        }
    )

    st.subheader("ระบบเข้าใจวันนี้เบื้องต้น")
    for item in _lpe_v111_daily_context_summary(live_ctx):
        st.markdown(f"- {item}")

    st.markdown(
        "<div class='lpe-panel lpe-next'>ขั้นต่อไปของโปรเจกต์คือ Step 3: Daily Plan Engine — สร้างแผนวันนี้จาก ตั้งค่าชีวิต + เช็คอินวันนี้</div>",
        unsafe_allow_html=True,
    )



# === LPE_V1_11_STEP3_1_DAILY_PLAN_ENGINE_START ===
def _lpe_v111_plan_float(value, default=None):
    try:
        text = str(value or "").strip()
        if not text:
            return default
        return float(text)
    except Exception:
        return default


def _lpe_v111_plan_int(value, default=3):
    try:
        return int(str(value or default).strip() or default)
    except Exception:
        return default


def _lpe_v111_profile_story_text(profile: dict, mode_key: str) -> str:
    profile = _lpe_v111_story_profile_defaults(profile)
    return str(profile.get("life_story_modes", {}).get(mode_key, {}).get("story", "") or "").strip()


def _lpe_v111_daily_plan_missing_information(profile: dict, ctx: dict) -> list[str]:
    profile = _lpe_v111_story_profile_defaults(profile)
    ctx = _lpe_v111_daily_context_defaults(ctx)
    missing = []

    if len(_lpe_v111_profile_story_text(profile, "goals")) < 10:
        missing.append("เป้าหมายหลักยังสั้นเกินไป")
    if len(_lpe_v111_profile_story_text(profile, "time_rhythm")) < 10:
        missing.append("ยังไม่รู้เวลา/เวร/จังหวะชีวิตปกติชัดเจน")
    if len(_lpe_v111_profile_story_text(profile, "health_energy")) < 10:
        missing.append("ยังไม่รู้ข้อจำกัดสุขภาพหรือพลังงานปกติชัดเจน")
    if not str(ctx.get("sleep_hours", "")).strip():
        missing.append("ยังไม่ได้กรอกชั่วโมงนอนวันนี้")
    if not str(ctx.get("today_shift", "")).strip() or str(ctx.get("today_shift", "")).strip() == "ตามปกติ":
        missing.append("ยังไม่ได้กรอกเวร/งาน/เวลาผูกมัดของวันนี้แบบเฉพาะเจาะจง")
    if not str(ctx.get("today_main_focus", "")).strip():
        missing.append("ยังไม่ได้ระบุโฟกัสหลักวันนี้")
    return missing


def _lpe_v111_daily_plan_risk_level(ctx: dict) -> str:
    ctx = _lpe_v111_daily_context_defaults(ctx)
    energy = _lpe_v111_plan_int(ctx.get("energy_level"), 3)
    sleep = _lpe_v111_plan_float(ctx.get("sleep_hours"), None)
    urgent = bool(str(ctx.get("urgent_events", "")).strip())
    physical = bool(str(ctx.get("physical_condition", "")).strip())

    if energy <= 2 or (sleep is not None and sleep < 6) or urgent or physical:
        return "สูง"
    if energy == 3 or (sleep is not None and sleep < 7):
        return "กลาง"
    return "ต่ำ"


def _lpe_v111_daily_plan_confidence_level(missing: list[str]) -> str:
    if len(missing) >= 4:
        return "ต่ำ"
    if len(missing) >= 2:
        return "กลาง"
    return "สูง"


def _lpe_v111_primary_focus(profile: dict, ctx: dict) -> str:
    ctx = _lpe_v111_daily_context_defaults(ctx)
    today_focus = str(ctx.get("today_main_focus", "")).strip()
    if today_focus:
        return today_focus

    goals = _lpe_v111_profile_story_text(profile, "goals")
    if goals:
        return goals[:80]
    return "เลือกงานสำคัญ 1 อย่างที่ทำให้วันนี้ไม่หลุด"


def _lpe_v111_daily_plan_generate(profile: dict, ctx: dict) -> dict:
    profile = _lpe_v111_story_profile_defaults(profile)
    ctx = _lpe_v111_daily_context_defaults(ctx)

    missing = _lpe_v111_daily_plan_missing_information(profile, ctx)
    risk_level = _lpe_v111_daily_plan_risk_level(ctx)
    confidence_level = _lpe_v111_daily_plan_confidence_level(missing)
    energy = _lpe_v111_plan_int(ctx.get("energy_level"), 3)
    sleep = _lpe_v111_plan_float(ctx.get("sleep_hours"), None)
    focus = _lpe_v111_primary_focus(profile, ctx)

    time_blocks = []
    avoid_today = []
    sleep_protection = []
    minimum_day = []

    if sleep is None:
        sleep_protection.append("ยังไม่รู้ชั่วโมงนอน จึงใช้แผนอนุรักษ์ไว้ก่อน")
    elif sleep < 6:
        sleep_protection.append("วันนี้นอนน้อย: ลด deep work และห้ามลากงานดึก")
        avoid_today.append("หลีกเลี่ยงงานหนักต่อเนื่องยาว ๆ")
    elif sleep < 7:
        sleep_protection.append("วันนี้นอนปานกลาง: วางงานสำคัญเป็นช่วงสั้น")
    else:
        sleep_protection.append("วันนี้นอนพอใช้: ทำงานหลักได้ แต่ยังควรกันเวลาพัก")

    if energy <= 2:
        plan_summary = "วันนี้พลังงานต่ำ ใช้แผนขั้นต่ำเพื่อไม่หลุดและไม่ทำให้พรุ่งนี้พัง"
        time_blocks.extend(
            [
                {
                    "start_time": "ช่วงแรกที่ว่าง",
                    "end_time": "20 นาทีถัดไป",
                    "activity": "พัก/กินน้ำ/จัดพื้นที่ให้พร้อม",
                    "category": "rest",
                    "reason": "พลังงานต่ำ ไม่ควรเริ่มด้วยงานหนักทันที",
                    "fallback_if_tired": "นั่งพัก 10 นาทีและหายใจช้า ๆ",
                    "success_condition": "รู้สึกพร้อมขึ้นเล็กน้อย",
                },
                {
                    "start_time": "หลังพัก",
                    "end_time": "15–30 นาที",
                    "activity": focus,
                    "category": "study",
                    "reason": "ยังต้องแตะเป้าหมายหลัก แม้ทำแบบสั้น",
                    "fallback_if_tired": "ทำ 10 นาที หรือสรุป 3 bullet",
                    "success_condition": "มีผลลัพธ์เล็กที่สุดที่นับว่าไม่หลุด",
                },
                {
                    "start_time": "ก่อนดึก",
                    "end_time": "ก่อนนอน",
                    "activity": "ปิดงานหนักและเตรียมนอน",
                    "category": "sleep",
                    "reason": "ป้องกันวันพรุ่งนี้พัง",
                    "fallback_if_tired": "วางมือถือและนอนทันที",
                    "success_condition": "หยุดงานหนักได้จริง",
                },
            ]
        )
        avoid_today.extend(["อย่าเริ่มโปรเจกต์ใหญ่ตอนดึก", "อย่าเพิ่ม task ใหม่โดยไม่จำเป็น"])
        minimum_day.extend(["แตะเป้าหมายหลัก 10–15 นาที", "พักให้พอ", "ไม่ลากงานจนเสียการนอน"])

    elif energy == 3:
        plan_summary = "วันนี้พลังงานปานกลาง เลือกงานหลัก 1 อย่างก่อน แล้วงานรองเป็น optional"
        time_blocks.extend(
            [
                {
                    "start_time": "ช่วงแรกที่ว่าง",
                    "end_time": "20–30 นาที",
                    "activity": "รีเซ็ตตัวเอง: พัก กินน้ำ หรือจัดโต๊ะ",
                    "category": "rest",
                    "reason": "ลดแรงเสียดทานก่อนเริ่มงานหลัก",
                    "fallback_if_tired": "พัก 10 นาที",
                    "success_condition": "พร้อมเริ่มงานหลัก",
                },
                {
                    "start_time": "ช่วงสมองดีที่สุดที่เหลือวันนี้",
                    "end_time": "30–45 นาที",
                    "activity": focus,
                    "category": "study",
                    "reason": "เป้าหมายหลักควรได้ block ที่ดีที่สุดของวัน",
                    "fallback_if_tired": "ลดเหลือ 20 นาที + สรุปสิ่งที่ค้าง",
                    "success_condition": "ได้ output 1 ชิ้นหรืออ่านจบ 1 ช่วง",
                },
                {
                    "start_time": "หลังงานหลัก",
                    "end_time": "15–25 นาที",
                    "activity": "เดินเบา/ยืดเหยียด/ดูแลสุขภาพ",
                    "category": "health",
                    "reason": "รักษาพลังงานและสุขภาพโดยไม่ฝืน",
                    "fallback_if_tired": "ยืดเหยียด 5 นาที",
                    "success_condition": "ขยับร่างกายอย่างน้อยเล็กน้อย",
                },
                {
                    "start_time": "ก่อนนอน",
                    "end_time": "10 นาที",
                    "activity": "สรุปวันนี้และปิดงานหนัก",
                    "category": "admin",
                    "reason": "เตรียมข้อมูลให้แผนพรุ่งนี้",
                    "fallback_if_tired": "เขียนแค่ 1 บรรทัด",
                    "success_condition": "รู้ว่าวันนี้ทำอะไรสำเร็จและพรุ่งนี้ต้องต่ออะไร",
                },
            ]
        )
        avoid_today.extend(["อย่าวางงานรองก่อนงานหลัก", "อย่าทำหลายเป้าหมายพร้อมกัน"])
        minimum_day.extend(["ทำงานหลัก 20–30 นาที", "ขยับร่างกายเบา ๆ", "หยุดงานหนักก่อนดึก"])

    else:
        plan_summary = "วันนี้พลังงานค่อนข้างดี ทำงานหลักได้เต็มขึ้น แต่ยังต้องกันพักและเวลานอน"
        time_blocks.extend(
            [
                {
                    "start_time": "ช่วงแรกที่ว่าง",
                    "end_time": "15–20 นาที",
                    "activity": "เตรียมพื้นที่และเลือกงานหลักให้ชัด",
                    "category": "admin",
                    "reason": "ลดการสลับงานและเริ่มอย่างมีทิศทาง",
                    "fallback_if_tired": "เขียน task เดียวที่ต้องปิด",
                    "success_condition": "รู้ชัดว่าจะเริ่มอะไร",
                },
                {
                    "start_time": "ช่วงสมองดีที่สุด",
                    "end_time": "45–60 นาที",
                    "activity": focus,
                    "category": "study",
                    "reason": "ใช้พลังงานดีไปกับเป้าหมายหลักก่อน",
                    "fallback_if_tired": "ลดเหลือ 30 นาที",
                    "success_condition": "ได้ output ชัดเจน 1 ชิ้น",
                },
                {
                    "start_time": "ช่วงถัดไป",
                    "end_time": "25–40 นาที",
                    "activity": "โปรเจกต์หรือ task รองที่ไม่ชนงานหลัก",
                    "category": "project",
                    "reason": "พลังงานพอทำงานรองได้ แต่ยังต้องจำกัดขอบเขต",
                    "fallback_if_tired": "เลือก task ย่อยที่ปิดได้ใน 15 นาที",
                    "success_condition": "ปิดงานย่อย 1 อย่าง",
                },
                {
                    "start_time": "ช่วงเย็น/หลังงาน",
                    "end_time": "20–40 นาที",
                    "activity": "ออกกำลังกายเบา-ปานกลางตามสภาพจริง",
                    "category": "health",
                    "reason": "ข้อมูลชีวิตระบุว่าสนใจสุขภาพ/ออกกำลังช่วงเย็น",
                    "fallback_if_tired": "เดิน 10 นาที",
                    "success_condition": "ขยับร่างกายโดยไม่ฝืน",
                },
                {
                    "start_time": "ก่อนนอน",
                    "end_time": "10 นาที",
                    "activity": "ปิดงานหนักและสรุปผล",
                    "category": "sleep",
                    "reason": "กันไม่ให้พลังดีพาไหลจนดึก",
                    "fallback_if_tired": "ปิดจอและนอน",
                    "success_condition": "หยุดงานหนักก่อนเวลานอน",
                },
            ]
        )
        avoid_today.extend(["อย่าเพิ่ม scope งานหลักกลางคัน", "อย่าลากโปรเจกต์จนชนเวลานอน"])
        minimum_day.extend(["ปิดงานหลัก 1 block", "ดูแลสุขภาพ 10–20 นาที", "สรุปก่อนนอน"])

    if str(ctx.get("urgent_events", "")).strip():
        avoid_today.append("อย่าวางแผนแน่น เพราะมีเรื่องด่วนแทรก")
    if str(ctx.get("physical_condition", "")).strip():
        avoid_today.append("อย่าฝืนร่างกายเกินสภาพวันนี้")
    if str(ctx.get("today_constraints", "")).strip():
        avoid_today.append("อย่าทำสิ่งที่ชนข้อจำกัดของวันนี้")

    return {
        "date": _lpe_v111_today_key(),
        "plan_summary": plan_summary,
        "risk_level": risk_level,
        "confidence_level": confidence_level,
        "time_blocks": time_blocks,
        "avoid_today": avoid_today,
        "sleep_protection": sleep_protection,
        "minimum_viable_day": minimum_day,
        "missing_information": missing,
    }


def page_daily_plan() -> None:
    st.markdown(
        "<div class='lpe-panel lpe-head'>"
        "<h1>🗓️ แผนวันนี้</h1>"
        "<p><b>เป้าหมาย:</b> สร้างแผนวันนี้จาก ตั้งค่าชีวิต + เช็คอินวันนี้ แบบ rule-based ตรวจสอบได้</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    profile = _lpe_v111_story_profile_defaults(st.session_state.get("lpe_profile", {}))
    ctx = _lpe_v111_get_daily_context()
    plan = _lpe_v111_daily_plan_generate(profile, ctx)

    st.info("Step 3.1 ยังเป็น session-only และ rule-based: ยังไม่ใช่ persistence, database หรือ external AI/API")

    col1, col2, col3 = st.columns(3)
    col1.metric("ระดับความเสี่ยงวันนี้", plan["risk_level"])
    col2.metric("ความมั่นใจของแผน", plan["confidence_level"])
    col3.metric("จำนวนช่วงแผน", len(plan["time_blocks"]))

    st.subheader("สรุปแผนวันนี้")
    st.markdown(f"- {plan['plan_summary']}")

    st.subheader("แผนเป็นช่วง")
    for idx, block in enumerate(plan["time_blocks"], start=1):
        with st.expander(f"{idx}. {block['start_time']} → {block['end_time']} | {block['activity']}", expanded=(idx == 1)):
            st.markdown(f"**หมวด:** {block['category']}")
            st.markdown(f"**เหตุผล:** {block['reason']}")
            st.markdown(f"**ถ้าเหนื่อยให้ลดเหลือ:** {block['fallback_if_tired']}")
            st.markdown(f"**ถือว่าสำเร็จเมื่อ:** {block['success_condition']}")

    st.subheader("สิ่งที่ควรเลี่ยงวันนี้")
    for item in plan["avoid_today"]:
        st.markdown(f"- {item}")

    st.subheader("การปกป้องเวลานอน/พลังงาน")
    for item in plan["sleep_protection"]:
        st.markdown(f"- {item}")

    st.subheader("Minimum Viable Day")
    for item in plan["minimum_viable_day"]:
        st.markdown(f"- {item}")

    if plan["missing_information"]:
        st.warning("ข้อมูลที่ยังขาด ทำให้แผนยังไม่แม่นเต็มที่")
        for item in plan["missing_information"]:
            st.markdown(f"- {item}")
    else:
        st.success("ข้อมูลหลักพอสำหรับสร้างแผนวันนี้แบบเบื้องต้นแล้ว")

    st.markdown(
        "<div class='lpe-panel lpe-next'>ขั้นต่อไปของโปรเจกต์คือ Step 4: บันทึกผลลัพธ์ของ task และ reflection เพื่อให้ระบบเรียนรู้จากวันนี้</div>",
        unsafe_allow_html=True,
    )
# === LPE_V1_11_STEP3_1_DAILY_PLAN_ENGINE_END ===



# === LPE_V1_11_STEP4_1_TASK_RESULT_DAILY_REFLECTION_START ===
def _lpe_v111_task_status_options() -> dict[str, str]:
    return {
        "done": "ทำสำเร็จ",
        "partial": "ทำบางส่วน",
        "skipped": "ไม่ได้ทำ",
        "moved": "เลื่อนไปวันอื่น",
        "dropped": "ตัดทิ้ง",
    }


def _lpe_v111_task_reason_options() -> dict[str, str]:
    return {
        "low_energy": "พลังงานไม่พอ",
        "not_enough_time": "เวลาจริงไม่พอ",
        "urgent_event": "มีงาน/เรื่องด่วนแทรก",
        "health_issue": "สุขภาพ/ร่างกายไม่พร้อม",
        "task_too_big": "task ใหญ่เกินไป",
        "unclear_start": "ไม่ชัดว่าต้องเริ่มตรงไหน",
        "low_priority": "ไม่สำคัญจริงในวันนี้",
        "distraction": "ถูกรบกวน/เสียสมาธิ",
        "overplanned": "วางแผนแน่นเกินไป",
        "other": "เหตุผลอื่น",
    }


def _lpe_v111_status_score(status: str) -> float:
    status = str(status or "").strip()
    if status == "done":
        return 1.0
    if status == "partial":
        return 0.5
    if status == "moved":
        return 0.25
    if status == "dropped":
        return 0.0
    return 0.0


def _lpe_v111_result_completion_label(score: float) -> str:
    if score <= 30:
        return "วันนี้แผนไม่ตรงชีวิตจริง ต้องลด/ปรับใหม่"
    if score <= 60:
        return "วันนี้ทำได้บางส่วน ต้องลดขนาดงานหรือจัดเวลาใหม่"
    if score <= 85:
        return "วันนี้แผนใช้ได้พอสมควร"
    return "วันนี้แผนค่อนข้างแม่น"


def _lpe_v111_current_daily_plan() -> dict:
    profile = _lpe_v111_story_profile_defaults(st.session_state.get("lpe_profile", {}))
    ctx = _lpe_v111_get_daily_context()
    return _lpe_v111_daily_plan_generate(profile, ctx)


def _lpe_v111_reflection_defaults(reflection: dict | None = None) -> dict:
    reflection = dict(reflection or {})
    reflection.setdefault("actual_energy", "3")
    reflection.setdefault("what_worked", "")
    reflection.setdefault("what_failed", "")
    reflection.setdefault("main_blocker", "")
    reflection.setdefault("tomorrow_adjustment", "")
    reflection.setdefault("free_story", "")
    return reflection


def _lpe_v111_task_result_defaults(item: dict | None = None) -> dict:
    item = dict(item or {})
    item.setdefault("block_id", "")
    item.setdefault("planned_activity", "")
    item.setdefault("status", "partial")
    item.setdefault("actual_minutes", 0)
    item.setdefault("reason", "other")
    item.setdefault("result_note", "")
    item.setdefault("energy_after", "3")
    item.setdefault("next_adjustment", "")
    return item


def _lpe_v111_pattern_candidates(plan: dict, task_results: list[dict], reflection: dict) -> list[dict]:
    candidates = []
    plan = dict(plan or {})
    reflection = _lpe_v111_reflection_defaults(reflection)

    low_energy_count = sum(1 for item in task_results if item.get("reason") == "low_energy")
    unclear_count = sum(1 for item in task_results if item.get("reason") == "unclear_start")
    overplanned_count = sum(1 for item in task_results if item.get("reason") == "overplanned")
    success_count = sum(1 for item in task_results if item.get("status") == "done")
    failed_count = sum(1 for item in task_results if item.get("status") in {"skipped", "partial", "moved"})

    if low_energy_count:
        candidates.append(
            {
                "observation": "วันนี้พลังงานเป็นตัวจำกัดหลัก",
                "evidence": f"มี {low_energy_count} task ที่ติดเหตุผลพลังงานไม่พอ",
                "confidence": "กลาง",
                "should_update_profile": False,
            }
        )

    if unclear_count:
        candidates.append(
            {
                "observation": "บาง task ยังใหญ่หรือไม่ชัด ต้องแตกเป็นขั้นย่อยก่อนวางแผน",
                "evidence": f"มี {unclear_count} task ที่ติดเหตุผลไม่ชัดว่าต้องเริ่มตรงไหน",
                "confidence": "กลาง",
                "should_update_profile": False,
            }
        )

    if overplanned_count:
        candidates.append(
            {
                "observation": "แผนอาจแน่นเกินชีวิตจริงของวันนี้",
                "evidence": f"มี {overplanned_count} task ที่สะท้อนว่า overplanned",
                "confidence": "กลาง",
                "should_update_profile": False,
            }
        )

    if success_count and not failed_count:
        candidates.append(
            {
                "observation": "ขนาดแผนวันนี้ใกล้เคียงกับพลังงานจริง",
                "evidence": "task ทั้งหมดทำสำเร็จ",
                "confidence": "สูง",
                "should_update_profile": False,
            }
        )

    if str(reflection.get("main_blocker", "")).strip():
        candidates.append(
            {
                "observation": "ตัวขวางหลักของวันนี้ควรใช้ปรับแผนพรุ่งนี้",
                "evidence": str(reflection.get("main_blocker", "")).strip(),
                "confidence": "กลาง",
                "should_update_profile": False,
            }
        )

    if not candidates:
        candidates.append(
            {
                "observation": "ยังไม่มี pattern ชัดเจน ต้องเก็บผลลัพธ์เพิ่ม",
                "evidence": "ข้อมูลวันนี้ยังน้อยหรือไม่มีเหตุผลล้มเหลวที่เด่น",
                "confidence": "ต่ำ",
                "should_update_profile": False,
            }
        )
    return candidates


def _lpe_v111_next_day_seed(plan: dict, task_results: list[dict], reflection: dict, completion_score: float) -> dict:
    reflection = _lpe_v111_reflection_defaults(reflection)
    failed = [item for item in task_results if item.get("status") in {"skipped", "partial", "moved"}]
    low_energy = any(item.get("reason") == "low_energy" for item in task_results)

    if completion_score <= 30:
        energy_mode = "low"
        suggested_minimum = ["เลือกเป้าหมายหลัก 1 อย่าง", "ลดเหลืองานสั้น 10–20 นาที", "กันเวลาพักและนอน"]
        warnings = ["อย่าวางแผนแน่นเหมือนเดิม", "อย่าเริ่มงานใหญ่ถ้ายังไม่แตก task"]
    elif completion_score <= 60:
        energy_mode = "medium"
        suggested_minimum = ["ทำงานหลัก 1 block", "งานรองเป็น optional", "มี fallback ทุกช่วง"]
        warnings = ["ตรวจว่า task ใหญ่เกินไปหรือไม่"]
    else:
        energy_mode = "high"
        suggested_minimum = ["คง block งานหลัก", "เพิ่มงานรองได้แต่ต้องไม่ชนเวลานอน"]
        warnings = ["อย่าเพิ่ม scope จนล้น"]

    if low_energy:
        energy_mode = "low"
        warnings.append("พรุ่งนี้ควรเริ่มแบบ conservative เพราะวันนี้ติดเรื่องพลังงาน")

    recommended_focus = str(reflection.get("tomorrow_adjustment", "")).strip()
    if not recommended_focus and failed:
        recommended_focus = f"ปรับ task แรกที่ค้าง: {failed[0].get('planned_activity', 'งานหลักที่ยังไม่จบ')}"
    if not recommended_focus:
        recommended_focus = "ทำเป้าหมายหลักต่อด้วยขนาดงานที่ทำได้จริง"

    return {
        "recommended_focus": recommended_focus,
        "recommended_energy_mode": energy_mode,
        "suggested_minimum_day": suggested_minimum,
        "warnings": warnings,
    }


def _lpe_v111_build_daily_result(plan: dict, task_results: list[dict], reflection: dict) -> dict:
    plan = dict(plan or {})
    reflection = _lpe_v111_reflection_defaults(reflection)
    normalized_results = [_lpe_v111_task_result_defaults(item) for item in task_results]

    if normalized_results:
        score = sum(_lpe_v111_status_score(item.get("status", "")) for item in normalized_results) / len(normalized_results) * 100
    else:
        score = 0.0

    result_summary = _lpe_v111_result_completion_label(score)
    patterns = _lpe_v111_pattern_candidates(plan, normalized_results, reflection)
    next_seed = _lpe_v111_next_day_seed(plan, normalized_results, reflection, score)

    return {
        "date": _lpe_v111_today_key(),
        "result_summary": result_summary,
        "completion_score": round(score, 1),
        "task_results": normalized_results,
        "daily_reflection": reflection,
        "pattern_candidates": patterns,
        "next_day_seed": next_seed,
    }


def _lpe_v111_status_label_to_key(label: str) -> str:
    options = _lpe_v111_task_status_options()
    for key, value in options.items():
        if value == label:
            return key
    return "partial"


def _lpe_v111_reason_label_to_key(label: str) -> str:
    options = _lpe_v111_task_reason_options()
    for key, value in options.items():
        if value == label:
            return key
    return "other"


def page_daily_reflection() -> None:
    st.markdown(
        "<div class='lpe-panel lpe-head'>"
        "<h1>🧾 ทบทวนวันนี้</h1>"
        "<p><b>เป้าหมาย:</b> บันทึกผลลัพธ์หลังทำตามแผน เพื่อให้ระบบรู้ว่าแผนใช้ได้จริงแค่ไหน</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    plan = _lpe_v111_current_daily_plan()
    blocks = list(plan.get("time_blocks", []))
    st.info("Step 4.1 ยังเป็น session-only: ยังไม่บันทึกถาวร และยังไม่แก้ Core Life Profile อัตโนมัติ")

    st.subheader("สรุปแผนที่ใช้ทบทวน")
    st.markdown(f"- {plan.get('plan_summary', 'ยังไม่มีสรุปแผน')}")
    st.markdown(f"- ความเสี่ยงวันนี้: {plan.get('risk_level', '-')}")
    st.markdown(f"- ความมั่นใจของแผน: {plan.get('confidence_level', '-')}")

    status_options = _lpe_v111_task_status_options()
    reason_options = _lpe_v111_task_reason_options()

    task_results = []
    st.subheader("ผลลัพธ์ของแต่ละช่วง")
    if not blocks:
        st.warning("ยังไม่มี time blocks จากแผนวันนี้ ระบบจะให้กรอก reflection รวมก่อน")
    for idx, block in enumerate(blocks, start=1):
        block_title = f"{idx}. {block.get('start_time', '-')} → {block.get('end_time', '-')} | {block.get('activity', '-')}"
        with st.expander(block_title, expanded=(idx == 1)):
            status_label = st.selectbox(
                "ผลลัพธ์",
                list(status_options.values()),
                index=1,
                key=f"lpe_result_status_{idx}",
            )
            actual_minutes = st.number_input(
                "ใช้เวลาจริงกี่นาที",
                min_value=0,
                max_value=600,
                value=0,
                step=5,
                key=f"lpe_result_actual_minutes_{idx}",
            )
            reason_label = st.selectbox(
                "เหตุผลหลัก ถ้าไม่สำเร็จเต็มที่",
                list(reason_options.values()),
                index=list(reason_options.keys()).index("other"),
                key=f"lpe_result_reason_{idx}",
            )
            result_note = st.text_area(
                "บันทึกผลลัพธ์ของช่วงนี้",
                value="",
                height=80,
                placeholder="เช่น อ่านได้ 20 นาที / ไม่ได้ทำเพราะมีงานแทรก / task ใหญ่เกินไป",
                key=f"lpe_result_note_{idx}",
            )
            energy_after = st.select_slider(
                "พลังงานหลังช่วงนี้",
                options=["1", "2", "3", "4", "5"],
                value="3",
                key=f"lpe_result_energy_after_{idx}",
            )
            next_adjustment = st.text_input(
                "รอบหน้าควรปรับอะไร",
                value="",
                placeholder="เช่น ลดเหลือ 20 นาที / แตก task ให้เล็กลง / ย้ายไปช่วงเช้า",
                key=f"lpe_result_next_adjustment_{idx}",
            )

            task_results.append(
                {
                    "block_id": idx,
                    "planned_activity": block.get("activity", ""),
                    "status": _lpe_v111_status_label_to_key(status_label),
                    "actual_minutes": actual_minutes,
                    "reason": _lpe_v111_reason_label_to_key(reason_label),
                    "result_note": result_note,
                    "energy_after": energy_after,
                    "next_adjustment": next_adjustment,
                }
            )

    st.subheader("Reflection รวมของวัน")
    actual_energy = st.select_slider(
        "พลังงานจริงทั้งวัน",
        options=["1", "2", "3", "4", "5"],
        value="3",
        key="lpe_reflection_actual_energy",
    )
    what_worked = st.text_area(
        "วันนี้อะไรใช้ได้ผล",
        height=80,
        key="lpe_reflection_what_worked",
    )
    what_failed = st.text_area(
        "วันนี้อะไรใช้ไม่ได้ผล",
        height=80,
        key="lpe_reflection_what_failed",
    )
    main_blocker = st.text_area(
        "ตัวขวางหลักของวันนี้คืออะไร",
        height=80,
        key="lpe_reflection_main_blocker",
    )
    tomorrow_adjustment = st.text_area(
        "พรุ่งนี้ควรปรับอะไร",
        height=80,
        key="lpe_reflection_tomorrow_adjustment",
    )
    free_story = st.text_area(
        "เล่าเรื่องวันนี้เพิ่มเติม",
        height=120,
        key="lpe_reflection_free_story",
    )

    reflection = _lpe_v111_reflection_defaults(
        {
            "actual_energy": actual_energy,
            "what_worked": what_worked,
            "what_failed": what_failed,
            "main_blocker": main_blocker,
            "tomorrow_adjustment": tomorrow_adjustment,
            "free_story": free_story,
        }
    )

    daily_result = _lpe_v111_build_daily_result(plan, task_results, reflection)

    if st.button("บันทึกทบทวนวันนี้", type="primary", use_container_width=True, key="save_daily_reflection_clean"):
        if "lpe_daily_results" not in st.session_state or not isinstance(st.session_state.lpe_daily_results, dict):
            st.session_state.lpe_daily_results = {}
        st.session_state.lpe_daily_results[_lpe_v111_today_key()] = daily_result
        _lpe_v111_save_local_snapshot("daily_reflection_saved")
        st.success("บันทึกผลลัพธ์วันนี้ใน session แล้ว")

    st.subheader("คะแนนความตรงของแผน")
    st.metric("Completion score", f"{daily_result['completion_score']}%")
    st.markdown(f"- {daily_result['result_summary']}")

    st.subheader("Pattern candidates")
    for item in daily_result["pattern_candidates"]:
        st.markdown(f"- **ข้อสังเกต:** {item['observation']}")
        st.markdown(f"  - หลักฐาน: {item['evidence']}")
        st.markdown(f"  - ความมั่นใจ: {item['confidence']}")
        st.markdown("  - ยังไม่แก้ Core Life Profile อัตโนมัติ")

    st.subheader("Seed สำหรับพรุ่งนี้")
    seed = daily_result["next_day_seed"]
    st.markdown(f"- โฟกัสที่แนะนำ: {seed['recommended_focus']}")
    st.markdown(f"- โหมดพลังงานที่แนะนำ: {seed['recommended_energy_mode']}")
    st.markdown("- Minimum day ที่แนะนำ:")
    for item in seed["suggested_minimum_day"]:
        st.markdown(f"  - {item}")
    if seed["warnings"]:
        st.markdown("- คำเตือน:")
        for item in seed["warnings"]:
            st.markdown(f"  - {item}")

    st.markdown(
        "<div class='lpe-panel lpe-next'>ขั้นต่อไปของโปรเจกต์คือ Step 5: JSON Export/Import Persistence เพื่อให้ข้อมูลไม่หายเมื่อ refresh</div>",
        unsafe_allow_html=True,
    )
# === LPE_V1_11_STEP4_1_TASK_RESULT_DAILY_REFLECTION_END ===



# === LPE_V1_11_STEP5_1_JSON_PERSISTENCE_START ===
def _lpe_v111_json_snapshot_version() -> str:
    return "lpe_v1_11_json_snapshot_v1"


def _lpe_v111_json_supported_versions() -> list[str]:
    return [_lpe_v111_json_snapshot_version()]


def _lpe_v111_json_safe(value):
    if isinstance(value, dict):
        return {str(k): _lpe_v111_json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_lpe_v111_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_lpe_v111_json_safe(v) for v in value]
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:
            return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _lpe_v111_build_json_snapshot() -> dict:
    profile = _lpe_v111_story_profile_defaults(st.session_state.get("lpe_profile", {}))

    daily_contexts = st.session_state.get("lpe_daily_contexts", {})
    if not isinstance(daily_contexts, dict):
        daily_contexts = {}

    daily_results = st.session_state.get("lpe_daily_results", {})
    if not isinstance(daily_results, dict):
        daily_results = {}

    daily_plans = st.session_state.get("lpe_daily_plans", {})
    if not isinstance(daily_plans, dict):
        daily_plans = {}

    today_key = _lpe_v111_today_key()
    try:
        current_plan = _lpe_v111_daily_plan_generate(profile, _lpe_v111_get_daily_context())
        current_plan["generated_at"] = datetime.now().isoformat()
        daily_plans = dict(daily_plans)
        daily_plans.setdefault(today_key, current_plan)
    except Exception as exc:
        daily_plans = dict(daily_plans)
        daily_plans.setdefault(today_key, {"error": f"could_not_generate_current_plan: {exc}"})

    pattern_history = []
    for date_key, result in daily_results.items():
        if isinstance(result, dict):
            for item in result.get("pattern_candidates", []) or []:
                if isinstance(item, dict):
                    row = dict(item)
                    row.setdefault("date", date_key)
                    row.setdefault("source", "daily_result")
                    pattern_history.append(row)

    snapshot = {
        "app_name": "Life Priority Engine",
        "schema_version": _lpe_v111_json_snapshot_version(),
        "exported_at": datetime.now().isoformat(),
        "user_label": "local_user",
        "runtime_note": "manual_export_import_no_database",
        "core_life_profile": profile,
        "daily_contexts": daily_contexts,
        "daily_plans": daily_plans,
        "daily_results": daily_results,
        "pattern_candidates_history": pattern_history,
        "import_notes": [],
    }
    return _lpe_v111_json_safe(snapshot)


def _lpe_v111_json_snapshot_text(snapshot: dict) -> str:
    return json.dumps(_lpe_v111_json_safe(snapshot), ensure_ascii=False, indent=2, sort_keys=True)


def _lpe_v111_json_snapshot_filename() -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"life_priority_engine_snapshot_{stamp}.json"


def _lpe_v111_validate_json_snapshot(snapshot) -> tuple[bool, list[str], dict]:
    errors = []
    normalized = {}

    if not isinstance(snapshot, dict):
        return False, ["ไฟล์ JSON ต้องเป็น object ระดับบนสุด"], {}

    schema_version = snapshot.get("schema_version")
    if schema_version not in _lpe_v111_json_supported_versions():
        errors.append(f"schema_version ไม่รองรับ: {schema_version}")

    core_life_profile = snapshot.get("core_life_profile", {})
    daily_contexts = snapshot.get("daily_contexts", {})
    daily_plans = snapshot.get("daily_plans", {})
    daily_results = snapshot.get("daily_results", {})
    pattern_history = snapshot.get("pattern_candidates_history", [])
    import_notes = snapshot.get("import_notes", [])

    if not isinstance(core_life_profile, dict):
        errors.append("core_life_profile ต้องเป็น object")
        core_life_profile = {}
    if not isinstance(daily_contexts, dict):
        errors.append("daily_contexts ต้องเป็น object")
        daily_contexts = {}
    if not isinstance(daily_plans, dict):
        errors.append("daily_plans ต้องเป็น object")
        daily_plans = {}
    if not isinstance(daily_results, dict):
        errors.append("daily_results ต้องเป็น object")
        daily_results = {}
    if not isinstance(pattern_history, list):
        errors.append("pattern_candidates_history ต้องเป็น list")
        pattern_history = []
    if not isinstance(import_notes, list):
        import_notes = []

    normalized = {
        "app_name": str(snapshot.get("app_name", "Life Priority Engine")),
        "schema_version": schema_version,
        "exported_at": str(snapshot.get("exported_at", "")),
        "user_label": str(snapshot.get("user_label", "local_user")),
        "runtime_note": str(snapshot.get("runtime_note", "manual_export_import_no_database")),
        "core_life_profile": _lpe_v111_story_profile_defaults(core_life_profile),
        "daily_contexts": _lpe_v111_json_safe(daily_contexts),
        "daily_plans": _lpe_v111_json_safe(daily_plans),
        "daily_results": _lpe_v111_json_safe(daily_results),
        "pattern_candidates_history": _lpe_v111_json_safe(pattern_history),
        "import_notes": _lpe_v111_json_safe(import_notes),
    }

    return len(errors) == 0, errors, normalized


def _lpe_v111_import_json_snapshot_to_session(snapshot: dict, autosave_after_import: bool = True) -> tuple[bool, list[str]]:
    ok, errors, normalized = _lpe_v111_validate_json_snapshot(snapshot)
    if not ok:
        return False, errors

    st.session_state.lpe_profile = normalized["core_life_profile"]
    st.session_state.lpe_daily_contexts = normalized["daily_contexts"]
    st.session_state.lpe_daily_plans = normalized["daily_plans"]
    st.session_state.lpe_daily_results = normalized["daily_results"]
    st.session_state.lpe_pattern_candidates_history = normalized["pattern_candidates_history"]
    st.session_state.lpe_last_import_notes = normalized.get("import_notes", [])
    if autosave_after_import:
        _lpe_v111_save_local_snapshot("json_imported")
    return True, []


def page_json_persistence() -> None:
    st.markdown(
        "<div class='lpe-panel lpe-head'>"
        "<h1>💾 สำรองข้อมูล</h1>"
        "<p><b>เป้าหมาย:</b> export/import ข้อมูลเป็น JSON เพื่อให้ข้อมูลไม่หายเมื่อ refresh หรือปิดเว็บ</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.warning(
        "ไฟล์ JSON นี้อาจมีข้อมูลส่วนตัว เช่น เรื่องชีวิต งาน เวร สุขภาพ และ reflection "
        "ควรเก็บไว้ในที่ปลอดภัย และไม่อัปโหลดสาธารณะ"
    )

    st.info(
        "Step 5.1 ยังเป็น manual export/import: ไม่มี login, database, remote sync หรือ external API"
    )

    st.caption(f"Local autosave file: {st.session_state.get('lpe_local_snapshot_path', str(_lpe_v111_local_snapshot_path()))}")
    if st.session_state.get("lpe_local_snapshot_restore_status") == "RESTORED":
        st.success("กู้ข้อมูลจาก local autosave แล้ว")

    snapshot = _lpe_v111_build_json_snapshot()
    snapshot_text = _lpe_v111_json_snapshot_text(snapshot)

    st.subheader("Export JSON")
    col1, col2, col3 = st.columns(3)
    col1.metric("schema_version", snapshot.get("schema_version", "-"))
    col2.metric("daily_contexts", len(snapshot.get("daily_contexts", {})))
    col3.metric("daily_results", len(snapshot.get("daily_results", {})))

    with st.expander("ดู preview สิ่งที่จะสำรอง", expanded=False):
        st.json(snapshot)

    st.download_button(
        label="ดาวน์โหลดไฟล์สำรอง JSON",
        data=snapshot_text.encode("utf-8"),
        file_name=_lpe_v111_json_snapshot_filename(),
        mime="application/json",
        use_container_width=True,
        key="download_lpe_json_snapshot",
    )

    st.subheader("Import JSON")
    uploaded = st.file_uploader(
        "เลือกไฟล์ JSON snapshot ที่เคย export จากระบบนี้",
        type=["json"],
        key="upload_lpe_json_snapshot",
    )

    if uploaded is not None:
        try:
            raw = uploaded.read()
            if len(raw) > 2_000_000:
                st.error("ไฟล์ใหญ่เกินไปสำหรับ MVP นี้")
                return
            imported = json.loads(raw.decode("utf-8"))
            ok, errors, normalized = _lpe_v111_validate_json_snapshot(imported)
            if ok:
                st.success("ตรวจไฟล์ผ่าน สามารถนำเข้า session ได้")
                with st.expander("Preview ข้อมูลที่จะนำเข้า", expanded=False):
                    st.json(normalized)

                confirm = st.checkbox(
                    "ยืนยันว่าจะนำเข้าและเขียนทับ session ปัจจุบัน",
                    key="confirm_import_lpe_json_snapshot",
                )
                if st.button(
                    "นำเข้าข้อมูลเข้า session",
                    type="primary",
                    use_container_width=True,
                    key="import_lpe_json_snapshot_button",
                    disabled=not confirm,
                ):
                    imported_ok, import_errors = _lpe_v111_import_json_snapshot_to_session(normalized)
                    if imported_ok:
                        st.success("นำเข้า JSON เข้า session แล้ว")
                    else:
                        st.error("นำเข้าไม่สำเร็จ")
                        for err in import_errors:
                            st.markdown(f"- {err}")
            else:
                st.error("ไฟล์ไม่ผ่าน validation")
                for err in errors:
                    st.markdown(f"- {err}")
        except Exception as exc:
            st.error(f"อ่านไฟล์ JSON ไม่สำเร็จ: {exc}")

    st.markdown(
        "<div class='lpe-panel lpe-next'>หลัง Step 5.1 ขั้นต่อไปคือ Static Product Flow Audit แล้วค่อยรันเว็บ local รอบเดียว</div>",
        unsafe_allow_html=True,
    )
# === LPE_V1_11_STEP5_1_JSON_PERSISTENCE_END ===



# === LPE_V1_11_STEP6_2_AUTOSAVE_GUIDED_QUESTIONS_START ===
def _lpe_v111_local_snapshot_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "lpe_local_snapshot.json"


def _lpe_v111_profile_has_story(profile: dict | None = None) -> bool:
    try:
        profile = _lpe_v111_story_profile_defaults(profile or {})
        modes = profile.get("life_story_modes", {})
        return any(str(item.get("story", "")).strip() for item in modes.values() if isinstance(item, dict))
    except Exception:
        return False


def _lpe_v111_session_has_meaningful_data() -> bool:
    if _lpe_v111_profile_has_story(st.session_state.get("lpe_profile", {})):
        return True
    contexts = st.session_state.get("lpe_daily_contexts", {})
    results = st.session_state.get("lpe_daily_results", {})
    if isinstance(contexts, dict) and bool(contexts):
        return True
    if isinstance(results, dict) and bool(results):
        return True
    return False


def _lpe_v111_save_local_snapshot(reason: str = "autosave") -> tuple[bool, str]:
    try:
        path = _lpe_v111_local_snapshot_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        snapshot = _lpe_v111_build_json_snapshot()
        snapshot["local_autosave_reason"] = str(reason)
        snapshot["local_autosaved_at"] = datetime.now().isoformat()
        path.write_text(_lpe_v111_json_snapshot_text(snapshot), encoding="utf-8")
        st.session_state.lpe_last_local_autosave_path = str(path)
        st.session_state.lpe_last_local_autosave_reason = str(reason)
        st.session_state.lpe_last_local_autosave_error = ""
        return True, str(path)
    except Exception as exc:
        st.session_state.lpe_last_local_autosave_error = str(exc)
        return False, str(exc)


def _lpe_v111_restore_local_snapshot_if_needed() -> None:
    if st.session_state.get("lpe_local_snapshot_restore_checked"):
        return
    st.session_state.lpe_local_snapshot_restore_checked = True

    path = _lpe_v111_local_snapshot_path()
    st.session_state.lpe_local_snapshot_path = str(path)

    if not path.exists():
        st.session_state.lpe_local_snapshot_restore_status = "NO_FILE"
        return

    if _lpe_v111_session_has_meaningful_data():
        st.session_state.lpe_local_snapshot_restore_status = "SKIP_SESSION_HAS_DATA"
        return

    try:
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        ok, errors = _lpe_v111_import_json_snapshot_to_session(snapshot, autosave_after_import=False)
        if ok:
            st.session_state.lpe_local_snapshot_restore_status = "RESTORED"
            st.session_state.lpe_local_snapshot_restored_at = datetime.now().isoformat()
        else:
            st.session_state.lpe_local_snapshot_restore_status = "ERROR"
            st.session_state.lpe_local_snapshot_restore_errors = errors
    except Exception as exc:
        st.session_state.lpe_local_snapshot_restore_status = "ERROR"
        st.session_state.lpe_local_snapshot_restore_errors = [str(exc)]
# === LPE_V1_11_STEP6_2_AUTOSAVE_GUIDED_QUESTIONS_END ===


def main() -> None:
    init_state()
    _lpe_v111_restore_local_snapshot_if_needed()
    _lpe_v111_global_readability_css()
    section = _lpe_v111_normalize_route(render_nav())

    if section == "สำรองข้อมูล":
        page_json_persistence()
    elif section == "ทบทวนวันนี้":
        page_daily_reflection()
    elif section == "แผนวันนี้":
        page_daily_plan()
    elif section == "เช็คอินวันนี้":
        page_daily_checkin()
    else:
        page_settings()


if __name__ == "__main__":
    main()

# --- LPE_VERSION_A_PHASE1_PERSONAL_DASHBOARD_SCHEMA_PATCH START ---
# Purpose: Version A Personal MVP profile schema and sidebar dashboard.
# Scope: local single-user JSON/session-state schema only.
# Hard bans preserved: no login, no admin, no multi-user, no database, no remote sync, no external AI/API.

LPE_VERSION_A_PHASE1_SCHEMA_VERSION = "version_a_personal_dashboard_schema_v1"
LPE_VERSION_A_PROFILE_STATE_KEY = "lpe_version_a_personal_profile_v1"


def _lpe_phase1_default_personal_profile():
    """Return the default Version A personal dashboard schema."""
    return {
        "schema_version": LPE_VERSION_A_PHASE1_SCHEMA_VERSION,
        "identity_work": {
            "display_name": "",
            "primary_work": "งานประจำ / เวร",
            "shift_pattern": "เช้า / บ่าย / ดึก / หยุด",
            "usual_work_time": "",
            "commute_buffer_minutes": 30,
            "minimum_sleep_hours": 6.0,
            "normal_wake_time": "",
            "target_sleep_time": "",
            "key_constraints": "",
        },
        "goals": {
            "exam_goal": "",
            "project_goal": "",
            "health_goal": "",
            "future_goal": "",
            "must_not_miss": "",
        },
        "health_food": {
            "current_weight_kg": 0.0,
            "target_weight_kg": 0.0,
            "common_foods": "ไข่, ผัก, ผลไม้",
            "simple_food_options": "ไข่ต้ม, ผัก, ผลไม้, โปรตีนเบา",
            "foods_to_reduce": "แป้งหนักตอนเย็น, ของหวาน, ของทอด",
            "foods_that_cause_sleepiness": "",
            "health_limits": "",
        },
        "exercise": {
            "fitness_level": "เริ่มต้น / ปานกลาง / ดี",
            "preferred_exercise": "เดินเร็ว, ยืดเหยียด, bodyweight เบา",
            "exercise_to_avoid": "",
            "best_time": "",
            "exercise_goal": "ลดน้ำหนัก / เพิ่มแรง / ลดล้า",
        },
        "personal_rules": {
            "direct_feedback": True,
            "no_scope_bloat": True,
            "night_shift_sleep_protection": True,
            "exam_priority_rule": True,
            "low_energy_minimum_plan": True,
            "project_one_task_limit": True,
            "custom_rules": "",
        },
    }


def _lpe_phase1_deep_merge_profile(default, raw):
    """Merge imported/session profile into the default schema without trusting missing fields."""
    if not isinstance(raw, dict):
        raw = {}
    merged = dict(default)
    for key, default_value in default.items():
        raw_value = raw.get(key)
        if isinstance(default_value, dict):
            merged[key] = _lpe_phase1_deep_merge_profile(default_value, raw_value if isinstance(raw_value, dict) else {})
        elif raw_value is not None:
            merged[key] = raw_value
    merged["schema_version"] = LPE_VERSION_A_PHASE1_SCHEMA_VERSION
    return merged


def _lpe_phase1_get_personal_profile():
    default = _lpe_phase1_default_personal_profile()
    current = st.session_state.get(LPE_VERSION_A_PROFILE_STATE_KEY, {})
    profile = _lpe_phase1_deep_merge_profile(default, current)
    st.session_state[LPE_VERSION_A_PROFILE_STATE_KEY] = profile
    return profile


def _lpe_phase1_profile_json(profile):
    import json
    return json.dumps(profile, ensure_ascii=False, indent=2)


def render_lpe_version_a_personal_dashboard_schema_sidebar():
    """Render Version A personal dashboard schema in the sidebar."""
    import json
    from datetime import date

    profile = _lpe_phase1_get_personal_profile()

    with st.sidebar.expander("Version A — Personal Dashboard", expanded=False):
        st.caption("ข้อมูลถาวรที่ระบบจะใช้สร้างตารางกิจวัตรรายวัน ไม่ใช่ login/database/cloud")

        uploaded_profile = st.file_uploader(
            "Import personal profile JSON",
            type=["json"],
            key="lpe_phase1_profile_import_json",
            help="นำเข้าเฉพาะ JSON profile ของ Life Priority Engine Version A",
        )
        if uploaded_profile is not None:
            try:
                imported = json.loads(uploaded_profile.getvalue().decode("utf-8"))
                st.session_state[LPE_VERSION_A_PROFILE_STATE_KEY] = _lpe_phase1_deep_merge_profile(
                    _lpe_phase1_default_personal_profile(), imported
                )
                profile = st.session_state[LPE_VERSION_A_PROFILE_STATE_KEY]
                st.success("นำเข้า profile สำเร็จ")
            except Exception as exc:
                st.error(f"นำเข้า profile ไม่สำเร็จ: {exc}")

        identity = profile["identity_work"]
        goals = profile["goals"]
        health_food = profile["health_food"]
        exercise = profile["exercise"]
        personal_rules = profile["personal_rules"]

        st.markdown("**A) ข้อมูลชีวิตหลัก**")
        identity["display_name"] = st.text_input("ชื่อเล่น/ชื่อผู้ใช้", identity.get("display_name", ""), key="lpe_phase1_identity_display_name")
        identity["primary_work"] = st.text_input("งานหลัก", identity.get("primary_work", ""), key="lpe_phase1_identity_primary_work")
        identity["shift_pattern"] = st.text_input("รูปแบบเวร", identity.get("shift_pattern", ""), key="lpe_phase1_identity_shift_pattern")
        identity["usual_work_time"] = st.text_input("เวลางานทั่วไป", identity.get("usual_work_time", ""), key="lpe_phase1_identity_usual_work_time")
        identity["commute_buffer_minutes"] = st.number_input("buffer เดินทาง/เตรียมตัว (นาที)", min_value=0, max_value=240, value=int(identity.get("commute_buffer_minutes", 30) or 0), step=5, key="lpe_phase1_identity_commute_buffer")
        identity["minimum_sleep_hours"] = st.number_input("เวลานอนขั้นต่ำ (ชั่วโมง)", min_value=0.0, max_value=16.0, value=float(identity.get("minimum_sleep_hours", 6.0) or 0.0), step=0.5, key="lpe_phase1_identity_min_sleep")
        identity["normal_wake_time"] = st.text_input("เวลาตื่นปกติ", identity.get("normal_wake_time", ""), key="lpe_phase1_identity_wake_time")
        identity["target_sleep_time"] = st.text_input("เวลานอนเป้าหมาย", identity.get("target_sleep_time", ""), key="lpe_phase1_identity_sleep_time")
        identity["key_constraints"] = st.text_area("ข้อจำกัดสำคัญ", identity.get("key_constraints", ""), key="lpe_phase1_identity_constraints")

        st.markdown("**B) เป้าหมายหลัก**")
        goals["exam_goal"] = st.text_area("เป้าหมายสอบ", goals.get("exam_goal", ""), key="lpe_phase1_goals_exam")
        goals["project_goal"] = st.text_area("เป้าหมายโปรเจกต์", goals.get("project_goal", ""), key="lpe_phase1_goals_project")
        goals["health_goal"] = st.text_area("เป้าหมายสุขภาพ", goals.get("health_goal", ""), key="lpe_phase1_goals_health")
        goals["future_goal"] = st.text_area("เป้าหมายอนาคต/การเงิน", goals.get("future_goal", ""), key="lpe_phase1_goals_future")
        goals["must_not_miss"] = st.text_area("สิ่งที่ห้ามพลาด", goals.get("must_not_miss", ""), key="lpe_phase1_goals_must_not_miss")

        st.markdown("**C) สุขภาพและอาหารทั่วไป**")
        health_food["current_weight_kg"] = st.number_input("น้ำหนักปัจจุบัน (kg)", min_value=0.0, max_value=300.0, value=float(health_food.get("current_weight_kg", 0.0) or 0.0), step=0.5, key="lpe_phase1_health_current_weight")
        health_food["target_weight_kg"] = st.number_input("เป้าหมายน้ำหนัก (kg)", min_value=0.0, max_value=300.0, value=float(health_food.get("target_weight_kg", 0.0) or 0.0), step=0.5, key="lpe_phase1_health_target_weight")
        health_food["common_foods"] = st.text_area("อาหารที่มีบ่อย", health_food.get("common_foods", ""), key="lpe_phase1_food_common")
        health_food["simple_food_options"] = st.text_area("อาหารง่ายที่ใช้เป็น default", health_food.get("simple_food_options", ""), key="lpe_phase1_food_simple")
        health_food["foods_to_reduce"] = st.text_area("อาหารที่ควรลด", health_food.get("foods_to_reduce", ""), key="lpe_phase1_food_reduce")
        health_food["foods_that_cause_sleepiness"] = st.text_area("อาหารที่กินแล้วง่วง/แน่นท้อง", health_food.get("foods_that_cause_sleepiness", ""), key="lpe_phase1_food_sleepy")
        health_food["health_limits"] = st.text_area("ข้อจำกัดสุขภาพเบื้องต้น", health_food.get("health_limits", ""), key="lpe_phase1_health_limits")

        st.markdown("**D) ออกกำลังกายทั่วไป**")
        exercise["fitness_level"] = st.text_input("ระดับความฟิต", exercise.get("fitness_level", ""), key="lpe_phase1_exercise_fitness")
        exercise["preferred_exercise"] = st.text_area("ท่าหรือกิจกรรมที่ทำได้", exercise.get("preferred_exercise", ""), key="lpe_phase1_exercise_preferred")
        exercise["exercise_to_avoid"] = st.text_area("ท่าหรือกิจกรรมที่ควรเลี่ยง", exercise.get("exercise_to_avoid", ""), key="lpe_phase1_exercise_avoid")
        exercise["best_time"] = st.text_input("เวลาที่สะดวก", exercise.get("best_time", ""), key="lpe_phase1_exercise_best_time")
        exercise["exercise_goal"] = st.text_area("เป้าหมายการออกกำลังกาย", exercise.get("exercise_goal", ""), key="lpe_phase1_exercise_goal")

        st.markdown("**E) กฎส่วนตัว**")
        personal_rules["direct_feedback"] = st.checkbox("เตือนตรง ไม่อวย", bool(personal_rules.get("direct_feedback", True)), key="lpe_phase1_rule_direct")
        personal_rules["no_scope_bloat"] = st.checkbox("ห้ามปล่อยงานบาน", bool(personal_rules.get("no_scope_bloat", True)), key="lpe_phase1_rule_no_bloat")
        personal_rules["night_shift_sleep_protection"] = st.checkbox("ถ้าเวรดึกต้องป้องกันการนอน", bool(personal_rules.get("night_shift_sleep_protection", True)), key="lpe_phase1_rule_night_shift")
        personal_rules["exam_priority_rule"] = st.checkbox("ถ้าสอบใกล้ การอ่านมาก่อนโปรเจกต์", bool(personal_rules.get("exam_priority_rule", True)), key="lpe_phase1_rule_exam")
        personal_rules["low_energy_minimum_plan"] = st.checkbox("พลังงานต่ำใช้ minimum plan", bool(personal_rules.get("low_energy_minimum_plan", True)), key="lpe_phase1_rule_minimum")
        personal_rules["project_one_task_limit"] = st.checkbox("โปรเจกต์ทำ task เดียว ไม่แตก scope", bool(personal_rules.get("project_one_task_limit", True)), key="lpe_phase1_rule_one_task")
        personal_rules["custom_rules"] = st.text_area("กฎส่วนตัวเพิ่มเติม", personal_rules.get("custom_rules", ""), key="lpe_phase1_rule_custom")

        profile["identity_work"] = identity
        profile["goals"] = goals
        profile["health_food"] = health_food
        profile["exercise"] = exercise
        profile["personal_rules"] = personal_rules
        profile["schema_version"] = LPE_VERSION_A_PHASE1_SCHEMA_VERSION
        st.session_state[LPE_VERSION_A_PROFILE_STATE_KEY] = profile

        st.download_button(
            "Export Version A personal profile JSON",
            data=_lpe_phase1_profile_json(profile),
            file_name=f"lpe_version_a_personal_profile_{date.today().isoformat()}.json",
            mime="application/json",
            key="lpe_phase1_profile_export_json",
        )

        st.caption("Phase 1 เท่านั้น: เก็บ schema/profile สำหรับ engine รอบถัดไป ยังไม่ใช่ timetable engine")


try:
    render_lpe_version_a_personal_dashboard_schema_sidebar()
except Exception as _lpe_phase1_sidebar_error:
    try:
        st.sidebar.warning(f"Version A profile sidebar โหลดไม่สำเร็จ: {_lpe_phase1_sidebar_error}")
    except Exception:
        pass

# --- LPE_VERSION_A_PHASE1_PERSONAL_DASHBOARD_SCHEMA_PATCH END ---

# LPE_VERSION_A_PHASE2_GUIDED_DAILY_QUESTIONS_PATCH_START
LPE_VERSION_A_PHASE2_GUIDED_DAILY_QUESTIONS_SCHEMA = {
    "schema_version": "version_a_phase2_guided_daily_questions_v1",
    "purpose": "daily_checkin_inputs_for_future_rule_bank_and_routine_engine",
    "hard_bans": ["no_login", "no_cloud", "no_external_ai", "no_medical_diagnosis"],
    "fields": [
        "wake_time", "sleep_hours", "energy_level", "today_shift", "tomorrow_shift",
        "work_start", "work_end", "primary_focus", "urgent_today", "study_focus",
        "project_focus", "available_food", "food_to_avoid_today", "exercise_capacity",
        "body_warning", "rest_deadline", "avoid_today", "minimum_success"
    ],
}


def _lpe_va_p2_safe_get_session_dict(key, default_factory):
    if key not in st.session_state or not isinstance(st.session_state.get(key), dict):
        st.session_state[key] = default_factory()
    return st.session_state[key]


def _lpe_va_p2_default_daily_context():
    from datetime import date
    return {
        "schema_version": "version_a_phase2_guided_daily_questions_v1",
        "date": date.today().isoformat(),
        "wake_time": "13:00",
        "sleep_hours": 6.0,
        "energy_level": 3,
        "today_shift": "เวรดึก",
        "tomorrow_shift": "ไม่แน่ใจ",
        "work_start": "00:00",
        "work_end": "08:00",
        "primary_focus": "อ่านสอบ + ทำโปรเจกต์แบบจำกัด",
        "urgent_today": "",
        "study_focus": "อ่าน 1 หัวข้อ หรือสรุป 1 หน้า",
        "project_focus": "ทำ task เดียว ไม่เปิด scope ใหม่",
        "available_food": "ไข่ ผัก ผลไม้ น้ำเปล่า",
        "food_to_avoid_today": "แป้งหนักก่อนนอน / ของหวานเยอะ",
        "exercise_capacity": "เบา",
        "body_warning": "ไม่มี",
        "rest_deadline": "20:00",
        "avoid_today": "เปิดงานใหม่ / ทำโปรเจกต์ยาวจนเสียเวลานอน",
        "minimum_success": "อ่าน 20 นาที + กินง่าย + พักก่อนเวร",
        "notes": "",
    }


def _lpe_va_p2_select_index(options, current_value):
    try:
        return options.index(current_value)
    except ValueError:
        return 0


def _lpe_va_p2_render_guided_daily_questions():
    from datetime import date

    current = _lpe_va_p2_safe_get_session_dict("lpe_version_a_daily_context", _lpe_va_p2_default_daily_context)
    current.setdefault("date", date.today().isoformat())

    st.markdown("---")
    st.markdown("## 🧭 Phase 2 — คำถามนำทางรายวัน")
    st.caption("ตอบเฉพาะข้อมูลที่เปลี่ยนวันนี้ ใช้เป็น input ให้กฎและแผนรายวันใน Phase ถัดไป")

    with st.form("lpe_version_a_phase2_guided_daily_questions_form"):
        st.markdown("### 1) สภาพวันนี้")
        c1, c2, c3 = st.columns(3)
        wake_time = c1.text_input("วันนี้ตื่นกี่โมง", value=str(current.get("wake_time", "13:00")), key="lpe_p2_wake_time")
        sleep_hours = c2.number_input("นอนมากี่ชั่วโมง", min_value=0.0, max_value=14.0, step=0.5, value=float(current.get("sleep_hours", 6.0)), key="lpe_p2_sleep_hours")
        energy_level = c3.slider("พลังงานตอนนี้", min_value=1, max_value=5, value=int(current.get("energy_level", 3)), key="lpe_p2_energy_level")

        st.markdown("### 2) เวร / เวลา / ข้อจำกัด")
        shift_options = ["หยุด", "เวรเช้า", "เวรบ่าย", "เวรดึก", "หลังลงเวร", "ต่อเวร", "ไม่แน่ใจ"]
        c4, c5, c6 = st.columns(3)
        today_shift = c4.selectbox("วันนี้มีเวรอะไร", shift_options, index=_lpe_va_p2_select_index(shift_options, current.get("today_shift", "เวรดึก")), key="lpe_p2_today_shift")
        tomorrow_shift = c5.selectbox("พรุ่งนี้มีเวรอะไร", shift_options, index=_lpe_va_p2_select_index(shift_options, current.get("tomorrow_shift", "ไม่แน่ใจ")), key="lpe_p2_tomorrow_shift")
        rest_deadline = c6.text_input("ต้องพัก/นอนก่อนกี่โมง", value=str(current.get("rest_deadline", "20:00")), key="lpe_p2_rest_deadline")
        c7, c8 = st.columns(2)
        work_start = c7.text_input("เริ่มงานกี่โมง", value=str(current.get("work_start", "00:00")), key="lpe_p2_work_start")
        work_end = c8.text_input("เลิกงานกี่โมง", value=str(current.get("work_end", "08:00")), key="lpe_p2_work_end")

        st.markdown("### 3) สิ่งสำคัญวันนี้")
        primary_focus = st.text_input("เรื่องสำคัญที่สุดวันนี้", value=str(current.get("primary_focus", "อ่านสอบ + ทำโปรเจกต์แบบจำกัด")), key="lpe_p2_primary_focus")
        urgent_today = st.text_area("เรื่องด่วน/งานแทรกวันนี้", value=str(current.get("urgent_today", "")), height=80, key="lpe_p2_urgent_today")
        c9, c10 = st.columns(2)
        study_focus = c9.text_area("วันนี้ควรอ่านอะไร", value=str(current.get("study_focus", "อ่าน 1 หัวข้อ หรือสรุป 1 หน้า")), height=90, key="lpe_p2_study_focus")
        project_focus = c10.text_area("วันนี้ทำโปรเจกต์ได้แค่ไหน", value=str(current.get("project_focus", "ทำ task เดียว ไม่เปิด scope ใหม่")), height=90, key="lpe_p2_project_focus")

        st.markdown("### 4) อาหาร / ออกกำลัง / ร่างกาย")
        exercise_options = ["พัก", "ยืด 3–5 นาที", "เบา", "ปานกลาง", "ทำได้เต็ม", "ไม่แน่ใจ"]
        c11, c12 = st.columns(2)
        available_food = c11.text_area("วันนี้มีอาหารอะไร", value=str(current.get("available_food", "ไข่ ผัก ผลไม้ น้ำเปล่า")), height=90, key="lpe_p2_available_food")
        food_to_avoid_today = c12.text_area("วันนี้ควรเลี่ยงอาหารอะไร", value=str(current.get("food_to_avoid_today", "แป้งหนักก่อนนอน / ของหวานเยอะ")), height=90, key="lpe_p2_food_to_avoid_today")
        c13, c14 = st.columns(2)
        exercise_capacity = c13.selectbox("วันนี้ออกกำลังกายได้แค่ไหน", exercise_options, index=_lpe_va_p2_select_index(exercise_options, current.get("exercise_capacity", "เบา")), key="lpe_p2_exercise_capacity")
        body_warning = c14.text_input("มีอาการ/สัญญาณร่างกายไหม", value=str(current.get("body_warning", "ไม่มี")), key="lpe_p2_body_warning")

        st.markdown("### 5) กรอบกันหลุด")
        avoid_today = st.text_area("วันนี้ต้องเลี่ยงอะไร", value=str(current.get("avoid_today", "เปิดงานใหม่ / ทำโปรเจกต์ยาวจนเสียเวลานอน")), height=80, key="lpe_p2_avoid_today")
        minimum_success = st.text_area("สำเร็จขั้นต่ำของวันนี้คืออะไร", value=str(current.get("minimum_success", "อ่าน 20 นาที + กินง่าย + พักก่อนเวร")), height=80, key="lpe_p2_minimum_success")
        notes = st.text_area("หมายเหตุเพิ่มเติม", value=str(current.get("notes", "")), height=80, key="lpe_p2_notes")

        submitted = st.form_submit_button("บันทึกคำตอบวันนี้")

    if submitted:
        updated = {
            "schema_version": "version_a_phase2_guided_daily_questions_v1",
            "date": date.today().isoformat(),
            "wake_time": wake_time,
            "sleep_hours": sleep_hours,
            "energy_level": energy_level,
            "today_shift": today_shift,
            "tomorrow_shift": tomorrow_shift,
            "work_start": work_start,
            "work_end": work_end,
            "primary_focus": primary_focus,
            "urgent_today": urgent_today,
            "study_focus": study_focus,
            "project_focus": project_focus,
            "available_food": available_food,
            "food_to_avoid_today": food_to_avoid_today,
            "exercise_capacity": exercise_capacity,
            "body_warning": body_warning,
            "rest_deadline": rest_deadline,
            "avoid_today": avoid_today,
            "minimum_success": minimum_success,
            "notes": notes,
        }
        st.session_state["lpe_version_a_daily_context"] = updated
        daily_contexts = _lpe_va_p2_safe_get_session_dict("daily_contexts", dict)
        daily_contexts[updated["date"]] = updated
        st.session_state["daily_contexts"] = daily_contexts
        st.success("บันทึกคำตอบวันนี้แล้ว — พร้อมใช้เป็น input ให้ Rule Bank / Routine Engine ใน Phase ถัดไป")

    saved_context = st.session_state.get("lpe_version_a_daily_context", current)
    with st.expander("ดูข้อมูลเช็คอินวันนี้แบบย่อ", expanded=False):
        st.json(saved_context)


try:
    _lpe_va_p2_render_guided_daily_questions()
except Exception as _lpe_va_p2_error:
    st.warning("Phase 2 guided daily questions แสดงผลไม่สำเร็จ แต่ระบบหลักยังทำงานอยู่")
    st.caption(str(_lpe_va_p2_error))
# LPE_VERSION_A_PHASE2_GUIDED_DAILY_QUESTIONS_PATCH_END

# --- LPE VERSION A PHASE 3 RULE BANK ENGINE PATCH START ---
LPE_VERSION_A_PHASE3_RULE_BANK_ENGINE_PATCH = True
LPE_VERSION_A_RULE_BANK_VERSION = "version_a_rule_bank_v1"

def lpe_vA3_pick(data, keys, default=""):
    if not isinstance(data, dict):
        return default
    for key in keys:
        if key in data and data.get(key) not in (None, ""):
            return data.get(key)
    lowered = {str(k).lower(): v for k, v in data.items()}
    for key in keys:
        lk = str(key).lower()
        if lk in lowered and lowered[lk] not in (None, ""):
            return lowered[lk]
    return default

def lpe_vA3_as_float(value, default=None):
    try:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value).strip().replace("ชั่วโมง", "").replace("ชม.", "").replace("ชม", "")
        text = text.replace("/5", "").replace(",", ".")
        return float(text)
    except Exception:
        return default

def lpe_vA3_to_minutes(value):
    if value is None:
        return None
    text = str(value).strip().replace("น.", "").replace(" ", "")
    if not text:
        return None
    text = text.replace(".", ":")
    parts = text.split(":")
    try:
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        if hour == 24:
            hour = 0
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return None
        return hour * 60 + minute
    except Exception:
        return None

def lpe_vA3_shift_from_time(start_value, end_value):
    start = lpe_vA3_to_minutes(start_value)
    end = lpe_vA3_to_minutes(end_value)
    if start is None or end is None:
        return "ไม่พอข้อมูลเวลา"
    if 7 * 60 <= start <= 9 * 60 and 15 * 60 <= end <= 17 * 60:
        return "เวรเช้า"
    if 15 * 60 <= start <= 17 * 60 and (end <= 60 or 23 * 60 <= end <= 24 * 60):
        return "เวรบ่าย"
    if start <= 60 or 23 * 60 <= start <= 24 * 60:
        return "เวรดึก"
    return "เวลางานพิเศษ/ไม่เข้า pattern เวร"

def lpe_vA3_text_has_any(value, words):
    text = str(value or "").lower()
    return any(str(w).lower() in text for w in words)

def lpe_vA3_classify_day_mode(context):
    energy = lpe_vA3_as_float(lpe_vA3_pick(context, ["energy", "พลังงานตอนนี้", "พลังงาน"], ""), None)
    sleep_hours = lpe_vA3_as_float(lpe_vA3_pick(context, ["sleep_hours", "นอนมากี่ชั่วโมง", "sleep"], ""), None)
    symptom = lpe_vA3_pick(context, ["symptom", "มีอาการ/สัญญาณร่างกายไหม", "body_warning", "อาการ"], "")
    workload = lpe_vA3_pick(context, ["urgent_today", "เรื่องด่วน/งานแทรกวันนี้", "workload", "งานแทรก"], "")
    red_reasons = []
    yellow_reasons = []
    if energy is not None and energy <= 1:
        red_reasons.append("พลังงาน 1/5 ต้องใช้แผนขั้นต่ำ")
    elif energy is not None and energy <= 3:
        yellow_reasons.append("พลังงานปานกลางหรือต่ำ ต้องจำกัดงาน")
    if sleep_hours is not None and sleep_hours < 5:
        red_reasons.append("นอนน้อยมาก ต้องปกป้องการพัก")
    elif sleep_hours is not None and sleep_hours < 7:
        yellow_reasons.append("นอนยังไม่พอเต็มที่")
    if symptom and str(symptom).strip() not in ("ไม่มี", "ไม่มีอาการ", "-"):
        red_reasons.append("มีสัญญาณร่างกาย ต้องลดงานหนัก")
    if workload:
        yellow_reasons.append("มีงานแทรก/ภาระวันนี้")
    if red_reasons:
        return "Red / Low Energy Day", red_reasons
    if yellow_reasons:
        return "Yellow / Controlled Day", yellow_reasons
    return "Green / Normal Day", ["ข้อมูลพลังงานและอาการยังรับได้"]

def lpe_vA3_build_rule_bank(profile=None, context=None):
    profile = profile if isinstance(profile, dict) else {}
    context = context if isinstance(context, dict) else {}
    today_shift = lpe_vA3_pick(context, ["today_shift", "วันนี้มีเวรอะไร", "shift_today"], "")
    tomorrow_shift = lpe_vA3_pick(context, ["tomorrow_shift", "พรุ่งนี้มีเวรอะไร", "shift_tomorrow"], "")
    work_start = lpe_vA3_pick(context, ["work_start", "เริ่มงานกี่โมง", "start_work"], "")
    work_end = lpe_vA3_pick(context, ["work_end", "เลิกงานกี่โมง", "end_work"], "")
    energy = lpe_vA3_as_float(lpe_vA3_pick(context, ["energy", "พลังงานตอนนี้", "พลังงาน"], ""), None)
    important = lpe_vA3_pick(context, ["main_priority", "เรื่องสำคัญที่สุดวันนี้", "priority_today"], "")
    study_focus = lpe_vA3_pick(context, ["study_focus", "วันนี้ควรอ่านอะไร", "อ่าน"], "")
    project_limit = lpe_vA3_pick(context, ["project_capacity", "วันนี้ทำโปรเจกต์ได้แค่ไหน", "โปรเจกต์"], "")
    exercise_capacity = lpe_vA3_pick(context, ["exercise_capacity", "วันนี้ออกกำลังกายได้แค่ไหน", "ออกกำลังกาย"], "")
    food_available = lpe_vA3_pick(context, ["food_available", "วันนี้มีอาหารอะไร", "อาหาร"], "")
    avoid_food = lpe_vA3_pick(context, ["food_to_avoid", "วันนี้ควรเลี่ยงอาหารอะไร"], "")
    avoid_today = lpe_vA3_pick(context, ["avoid_today", "วันนี้ต้องเลี่ยงอะไร"], "")
    minimum_success = lpe_vA3_pick(context, ["minimum_success", "สำเร็จขั้นต่ำของวันนี้คืออะไร"], "")
    shift_by_time = lpe_vA3_shift_from_time(work_start, work_end)
    warnings = []
    if today_shift and shift_by_time not in ("ไม่พอข้อมูลเวลา", "เวลางานพิเศษ/ไม่เข้า pattern เวร") and today_shift != shift_by_time:
        warnings.append(f"เวรที่กรอก ({today_shift}) ขัดกับเวลา {work_start}-{work_end} ซึ่งดูเหมือน {shift_by_time}; ให้ใช้เวลาเป็นหลักชั่วคราว")
    day_mode, mode_reasons = lpe_vA3_classify_day_mode(context)
    rules = []
    def add(group, condition, action, reason):
        rules.append({"กลุ่มกฎ": group, "เงื่อนไข": condition, "การตัดสินใจ": action, "เหตุผล": reason})
    if energy is not None and energy <= 1:
        add("Energy", "พลังงาน <= 1", "ใช้ minimum plan / ห้ามวางงานแน่น", "ถ้าฝืนวันนี้จะเสียงานหลักและการนอน")
    elif energy is not None and energy <= 3:
        add("Energy", "พลังงาน <= 3", "ทำ Must ก่อน แล้วค่อย Project แบบสั้น", "ยังทำได้แต่ต้องคุม scope")
    if lpe_vA3_text_has_any(important + " " + study_focus, ["สอบ", "อ่าน"]):
        add("Study", "มีสอบ/อ่านหนังสือในเป้าหมายวันนี้", "Study เป็น Must Do อย่างน้อย 30-60 นาทีหรือ 1 บทย่อย", "สอบมี deadline และพลาดแล้วเสียหายจริง")
    if project_limit or lpe_vA3_text_has_any(important, ["โปรเจกต์", "เว็บ"]):
        add("Project", "มีโปรเจกต์วันนี้", "จำกัดเป็น 1 next action หรือ block สั้น", "โปรเจกต์สำคัญแต่ห้ามกินเวลานอนและการสอบ")
    if shift_by_time != "ไม่พอข้อมูลเวลา" or today_shift:
        add("Shift", "มีเวร/เวลางาน", "งานและ sleep protection มาก่อนงานเสริม", "เวรเป็นงานหลักที่หลีกไม่ได้")
    if tomorrow_shift:
        add("Sleep", "พรุ่งนี้มีเวร", "กันเวลาพัก/นอนล่วงหน้า", "เวรวันถัดไปทำให้การนอนวันนี้มี priority")
    if food_available:
        add("Food", "มีอาหารที่กินได้", "เลือกอาหารเบา โปรตีน/ผัก/น้ำเปล่า", "ช่วยอิ่มโดยไม่แน่นท้องก่อนพักหรือทำงาน")
    if avoid_food:
        add("Food", "มีอาหารควรเลี่ยง", f"เลี่ยง: {avoid_food}", "กันง่วง แน่นท้อง และพลังงานตก")
    if exercise_capacity and ("พัก" in str(exercise_capacity) or (energy is not None and energy <= 1)):
        add("Exercise", "วันนี้ควรพักหรือพลังงานต่ำ", "พักหรือยืดเบา 3-5 นาทีเท่านั้น", "ไม่ชดเชยสุขภาพด้วยการฝืนหนัก")
    elif exercise_capacity:
        add("Exercise", "วันนี้ออกกำลังได้", "เลือกเบา/ปานกลางตามพลังงาน", "เป็นคำแนะนำทั่วไป ไม่ใช่โค้ชเต็มระบบ")
    if avoid_today:
        add("Avoid", "มีสิ่งที่ต้องเลี่ยง", avoid_today, "กันหลุดจาก Must Do และการนอน")
    if minimum_success:
        add("Minimum", "มีสำเร็จขั้นต่ำ", minimum_success, "ทำให้วันพังน้อยลงแม้พลังงานต่ำ")
    return {
        "rule_bank_version": LPE_VERSION_A_RULE_BANK_VERSION,
        "day_mode": day_mode,
        "mode_reasons": mode_reasons,
        "shift_by_time": shift_by_time,
        "shift_warning": warnings,
        "must_do": ["งาน/เวรที่หลีกไม่ได้", "อ่านสอบขั้นต่ำ", "ปกป้องการนอน"],
        "should_do": ["อาหารเบา", "โปรเจกต์แบบจำกัด", "ทบทวนผลวันนี้"],
        "could_do": ["งานเสริม", "สวน/จัดของ", "โปรเจกต์เพิ่มเมื่อพลังงานเหลือ"],
        "avoid_today": avoid_today or "เปิดงานใหม่ / ทำโปรเจกต์ยาวจนเสียเวลานอน",
        "rules": rules,
    }

def lpe_vA3_render_rule_bank_panel():
    try:
        import pandas as pd
    except Exception:
        pd = None
    profile = st.session_state.get("lpe_version_a_personal_profile_v1") or st.session_state.get("lpe_version_a_personal_profile") or st.session_state.get("personal_profile") or {}
    context = st.session_state.get("lpe_version_a_daily_context") or st.session_state.get("daily_context") or {}
    st.markdown("---")
    st.subheader("🧠 Phase 3 — Rule Bank")
    st.caption("กฎตัดสินใจจาก profile + check-in วันนี้ ยังไม่ใช่ตารางกิจวัตรรายวันเต็มระบบ")
    if not isinstance(context, dict) or not context:
        st.warning("ยังไม่มี daily context จาก Phase 2 — ให้กรอกและบันทึกคำถามวันนี้ก่อน")
        return
    result = lpe_vA3_build_rule_bank(profile, context)
    st.session_state["lpe_version_a_rule_bank_result"] = result
    c1, c2 = st.columns(2)
    c1.metric("โหมดวันนี้", result.get("day_mode", ""))
    c2.metric("เวรจากเวลา", result.get("shift_by_time", ""))
    for warning in result.get("shift_warning", []):
        st.warning(warning)
    st.markdown("**เหตุผลของโหมดวันนี้**")
    for reason in result.get("mode_reasons", []):
        st.write("- " + str(reason))
    st.markdown("**Must / Should / Could วันนี้**")
    col1, col2, col3 = st.columns(3)
    col1.write("Must")
    for item in result.get("must_do", []):
        col1.write("- " + str(item))
    col2.write("Should")
    for item in result.get("should_do", []):
        col2.write("- " + str(item))
    col3.write("Could")
    for item in result.get("could_do", []):
        col3.write("- " + str(item))
    st.markdown("**วันนี้ควรเลี่ยง**")
    st.write(result.get("avoid_today", ""))
    rules = result.get("rules", [])
    if rules:
        st.markdown("**Rule Bank ที่ใช้ตัดสินใจ**")
        if pd:
            st.dataframe(pd.DataFrame(rules), use_container_width=True, hide_index=True)
        else:
            for rule in rules:
                st.write(rule)
    st.info("ขอบเขต: กฎอาหาร/ออกกำลังเป็นคำแนะนำทั่วไป ไม่ใช่การวินิจฉัยหรือแผนรักษา")

try:
    if st.session_state.get("lpe_phase10b_show_legacy_phase3_5", False):
        lpe_vA3_render_rule_bank_panel()
except Exception as exc:
    st.error(f"Phase 3 Rule Bank legacy render error: {exc}")
# --- LPE VERSION A PHASE 3 RULE BANK ENGINE PATCH END ---


# LPE_VERSION_A_PHASE4_DAILY_TIMETABLE_ENGINE_MARKER_V1
# Version A Personal MVP — Phase 4 Daily Timetable Engine
# Local-only, session-only, rule-based timetable builder. No network, no background storage service, no deployment action.

from datetime import datetime as _lpe_v4_datetime
import re as _lpe_v4_re


def _lpe_v4_to_text(value):
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        return " ".join(_lpe_v4_to_text(v) for v in value.values())
    if isinstance(value, (list, tuple, set)):
        return " ".join(_lpe_v4_to_text(v) for v in value)
    return str(value)


def _lpe_v4_find_value(data, candidates, default=""):
    if not isinstance(data, dict):
        return default
    lowered = [(str(k).lower(), k) for k in data.keys()]
    for needle in candidates:
        n = str(needle).lower()
        for kl, original in lowered:
            if n in kl:
                value = data.get(original)
                if value not in (None, ""):
                    return value
    for value in data.values():
        if isinstance(value, dict):
            found = _lpe_v4_find_value(value, candidates, None)
            if found not in (None, ""):
                return found
    return default


def _lpe_v4_latest_from_collection(collection):
    if isinstance(collection, list) and collection:
        return collection[-1]
    if isinstance(collection, dict) and collection:
        # Prefer obvious latest/today keys, otherwise last insertion-order value.
        for key in ("today", "latest", "current", "ล่าสุด", "วันนี้"):
            if key in collection:
                return collection[key]
        try:
            return list(collection.values())[-1]
        except Exception:
            return {}
    return {}


def _lpe_v4_get_profile():
    for key in (
        "lpe_version_a_personal_profile_v1",
        "lpe_version_a_personal_profile",
        "lpe_personal_profile",
        "lpe_personal_profile",
        "personal_profile",
        "life_profile",
        "lpe_life_profile",
        "core_life_profile",
        "profile",
        "profile",
    ):
        value = st.session_state.get(key)
        if isinstance(value, dict) and value:
            return value
    return {}


def _lpe_v4_get_daily_context():
    for key in (
        "lpe_version_a_daily_context",
        "daily_context",
        "today_context",
        "current_daily_context",
    ):
        value = st.session_state.get(key)
        if isinstance(value, dict) and value:
            return value
    return _lpe_v4_latest_from_collection(st.session_state.get("daily_contexts"))


def _lpe_v4_get_rule_bank():
    for key in (
        "lpe_version_a_rule_bank_result",
        "rule_bank_result",
        "daily_rule_bank_result",
    ):
        value = st.session_state.get(key)
        if isinstance(value, dict) and value:
            return value
    return {}


def _lpe_v4_num(value, default=None):
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value or "")
    match = _lpe_v4_re.search(r"-?\d+(?:\.\d+)?", text)
    if match:
        try:
            return float(match.group(0))
        except Exception:
            return default
    return default


def _lpe_v4_norm_time(value):
    text = str(value or "").strip()
    if not text:
        return ""
    match = _lpe_v4_re.search(r"(\d{1,2})(?:[:\.](\d{2}))?", text)
    if not match:
        return text
    hour = int(match.group(1))
    minute = int(match.group(2) or "00")
    return f"{hour:02d}:{minute:02d}"


def _lpe_v4_shift_from_time(start_time, end_time):
    start = _lpe_v4_norm_time(start_time)
    end = _lpe_v4_norm_time(end_time)
    if start.startswith("08") and end.startswith("16"):
        return "เวรเช้า"
    if start.startswith("16") and (end.startswith("00") or end.startswith("24")):
        return "เวรบ่าย"
    if start.startswith("00") and end.startswith("08"):
        return "เวรดึก"
    return ""


def _lpe_v4_conflict_warning(shift_label, work_start, work_end):
    label = str(shift_label or "").strip()
    inferred = _lpe_v4_shift_from_time(work_start, work_end)
    if label and inferred and label != inferred:
        return f"พบข้อมูลเวรขัดกัน: เลือก '{label}' แต่เวลา {work_start}-{work_end} ใกล้เคียง '{inferred}' — ใช้เวลาเริ่ม/เลิกงานเป็นตัวตัดสินชั่วคราว"
    return ""


def _lpe_v4_build_timetable(profile, daily_context, rule_bank):
    minimum_sleep = _lpe_v4_num(_lpe_v4_find_value(profile, ["minimum_sleep", "นอนขั้นต่ำ"], 8), 8)
    wake = _lpe_v4_find_value(daily_context, ["wake", "ตื่น"], "")
    sleep_hours = _lpe_v4_num(_lpe_v4_find_value(daily_context, ["sleep_hours", "นอนมากี่", "ชั่วโมง"], ""), None)
    energy = _lpe_v4_num(_lpe_v4_find_value(daily_context, ["energy", "พลังงาน"], ""), None)
    today_shift = _lpe_v4_find_value(daily_context, ["today_shift", "เวรวันนี้"], "")
    tomorrow_shift = _lpe_v4_find_value(daily_context, ["tomorrow_shift", "พรุ่งนี้มีเวร", "เวรพรุ่งนี้"], "")
    work_start = _lpe_v4_find_value(daily_context, ["work_start", "start_work", "เริ่มงาน"], "")
    work_end = _lpe_v4_find_value(daily_context, ["work_end", "end_work", "เลิกงาน"], "")
    rest_before = _lpe_v4_find_value(daily_context, ["rest_before", "นอนก่อน", "พัก/นอนก่อน"], "")
    urgent = _lpe_v4_find_value(daily_context, ["urgent", "แทรก", "ด่วน", "ช่วยแม่"], "")
    study = _lpe_v4_find_value(daily_context, ["study", "อ่าน", "หนังสือ"], "อ่านสอบขั้นต่ำ 30–60 นาที")
    project = _lpe_v4_find_value(daily_context, ["project", "โปรเจกต์"], "ทำโปรเจกต์ 1 งานย่อย")
    avoid = _lpe_v4_find_value(daily_context, ["avoid_today", "ต้องเลี่ยง", "เลี่ยงอะไร"], "เปิดงานใหม่ / ทำยาวจนเสียเวลานอน")
    food = _lpe_v4_find_value(daily_context, ["food", "อาหาร"], "กินง่าย ย่อยง่าย และดื่มน้ำ")
    exercise = _lpe_v4_find_value(daily_context, ["exercise", "ออกกำลัง"], "พักหรือยืดเบา")
    minimum_success = _lpe_v4_find_value(daily_context, ["minimum_success", "สำเร็จขั้นต่ำ"], "ไม่หลุดจากสิ่งสำคัญที่สุด")

    warnings = []
    conflict = _lpe_v4_conflict_warning(today_shift, work_start, work_end)
    if conflict:
        warnings.append(conflict)
    if not profile:
        warnings.append("ยังไม่พบ profile ใน session: ให้ import personal profile JSON ก่อนใช้ตารางเต็ม")
    if not daily_context:
        warnings.append("ยังไม่พบคำตอบวันนี้ใน session: ให้กรอก Phase 2 แล้วบันทึกก่อน")
    if sleep_hours is not None and minimum_sleep is not None and sleep_hours < minimum_sleep:
        warnings.append(f"นอน {sleep_hours:g} ชม. ต่ำกว่าเป้าขั้นต่ำ {minimum_sleep:g} ชม. — ต้องลดงานรอง")

    if energy is None:
        mode = "Yellow — ข้อมูลพลังงานไม่ชัด"
        project_cap = "ทำเฉพาะ next single action"
        exercise_plan = "พักหรือยืดเบา"
    elif energy <= 2:
        mode = "Red / Low Energy — กันหลุดและปกป้องการนอน"
        project_cap = "จำกัดโปรเจกต์ 1 งานย่อย ไม่เปิด scope ใหม่"
        exercise_plan = "พัก หรือยืดเบา 3–5 นาที"
    elif energy <= 3:
        mode = "Yellow — ทำงานหลักได้ แต่ต้องมี buffer"
        project_cap = "โปรเจกต์ 1–2 block สั้น"
        exercise_plan = "เดินเบา/ยืดเบา ถ้าไม่เพลีย"
    else:
        mode = "Green — ทำแผนเต็มได้แบบไม่ลืมพัก"
        project_cap = "โปรเจกต์ทำได้มากขึ้น แต่ยังต้องไม่ชนเวลานอน"
        exercise_plan = "ออกกำลังเบา-ปานกลางตามสภาพจริง"

    has_work_time = bool(_lpe_v4_norm_time(work_start) and _lpe_v4_norm_time(work_end))
    has_urgent_10_12 = "10" in str(urgent) and "12" in str(urgent)

    blocks = []
    if wake:
        blocks.append({"เวลา": f"หลังตื่น {wake}", "ทำอะไร": "กินง่าย / ตั้งหลัก / งานเบา", "เหตุผล": "เริ่มวันโดยไม่ใช้พลังงานเกินจำเป็น", "ถ้าเหนื่อยมาก": "ล้างหน้า ดื่มน้ำ เปิดแผนวันนี้พอ"})
    else:
        blocks.append({"เวลา": "ช่วงเริ่มวัน", "ทำอะไร": "ตั้งหลักและดูข้อจำกัดวันนี้", "เหตุผล": "ต้องรู้พลังงานและเวรก่อนใส่งาน", "ถ้าเหนื่อยมาก": "เปิดแผนและเลือก 1 งานเล็ก"})

    if has_urgent_10_12:
        blocks.append({"เวลา": "10:00–12:00", "ทำอะไร": urgent, "เหตุผล": "เป็นงานแทรกจริง ต้องล็อกเวลาไว้ก่อน", "ถ้าเหนื่อยมาก": "ทำเท่าที่จำเป็น แล้วกลับมาพัก"})
    elif urgent:
        blocks.append({"เวลา": "ช่วงงานแทรก", "ทำอะไร": urgent, "เหตุผล": "กันงานจริงไม่ให้ชนกับอ่านสอบ/นอน", "ถ้าเหนื่อยมาก": "ลดงานรองออก"})

    blocks.append({"เวลา": "ก่อนเริ่มงานหลัก", "ทำอะไร": str(study), "เหตุผล": "สอบเป็น must-not-miss และมี deadline จริง", "ถ้าเหนื่อยมาก": "อ่านขั้นต่ำ 30 นาที หรือสรุปหัวข้อย่อยเดียว"})
    blocks.append({"เวลา": "block โปรเจกต์สั้น", "ทำอะไร": str(project_cap), "เหตุผล": "โปรเจกต์สำคัญ แต่ห้ามกินเวลานอนและอ่านสอบ", "ถ้าเหนื่อยมาก": "ทำ handoff/บันทึก next action เท่านั้น"})

    if has_work_time:
        blocks.append({"เวลา": f"{_lpe_v4_norm_time(work_start)}–{_lpe_v4_norm_time(work_end)}", "ทำอะไร": f"เวร/งานหลัก ({today_shift or _lpe_v4_shift_from_time(work_start, work_end)})", "เหตุผล": "งานหลักหลีกไม่ได้ ต้องมาก่อนงานฝัน", "ถ้าเหนื่อยมาก": "ไม่เพิ่มงานใหม่หลังเลิกงาน"})
    elif today_shift:
        blocks.append({"เวลา": "ช่วงเวร/งาน", "ทำอะไร": f"{today_shift}", "เหตุผล": "ต้องกันพลังงานไว้สำหรับงานหลัก", "ถ้าเหนื่อยมาก": "ตัดงานรองทั้งหมด"})

    if rest_before:
        blocks.append({"เวลา": f"ก่อน {rest_before}", "ทำอะไร": "ปิดงาน / เตรียมนอน / ไม่เปิดงานใหม่", "เหตุผล": "sleep protection สำคัญกว่า project expansion", "ถ้าเหนื่อยมาก": "หยุดทันที เหลือแค่เตรียมนอน"})
    else:
        blocks.append({"เวลา": "ท้ายวัน", "ทำอะไร": "ปิดวันและบันทึกสั้น ๆ", "เหตุผล": "ให้แชท/ระบบรุ่นถัดไปสานต่องานได้", "ถ้าเหนื่อยมาก": "บันทึก 3 บรรทัด: ทำอะไรแล้ว / ติดอะไร / ต่ออะไร"})

    must = ["เวร/งานหลัก", "อ่านสอบขั้นต่ำ", "ปกป้องเวลานอน"]
    should = ["โปรเจกต์แบบจำกัดงาน", str(food), exercise_plan]
    could = ["งานรองเพิ่มเมื่อพลังงานเหลือ", "จัดบ้านสวนเฉพาะงานจำเป็น"]
    avoid_list = [str(avoid), "เปิดงานใหม่", "ทำโปรเจกต์ยาวจนเสียเวลานอน"]

    result = {
        "schema_version": "lpe_version_a_daily_timetable_engine_v1",
        "created_at": _lpe_v4_datetime.now().isoformat(timespec="seconds"),
        "day_mode": mode,
        "inputs_used": {
            "wake": str(wake),
            "sleep_hours": sleep_hours,
            "energy": energy,
            "today_shift": str(today_shift),
            "tomorrow_shift": str(tomorrow_shift),
            "work_start": str(work_start),
            "work_end": str(work_end),
            "rest_before": str(rest_before),
            "minimum_success": str(minimum_success),
        },
        "warnings": warnings,
        "must": must,
        "should": should,
        "could": could,
        "avoid": avoid_list,
        "blocks": blocks,
        "fallback_rule": "ถ้าเหนื่อยมาก ให้เหลือ: งานหลัก + อ่านขั้นต่ำ 30 นาที + บันทึก next action + นอน",
    }
    return result


def _lpe_v4_render_daily_timetable_engine():
    st.markdown("---")
    st.header("🧱 Phase 4 — Daily Timetable Engine")
    st.caption("แปลง profile + คำตอบวันนี้ + rule bank เป็นตารางกิจวัตรรายวันแบบ local/session-only")

    profile = _lpe_v4_get_profile()
    daily_context = _lpe_v4_get_daily_context()
    rule_bank = _lpe_v4_get_rule_bank()

    if not profile or not daily_context:
        st.warning("ยังมีข้อมูลไม่ครบหลังรีเปิดเว็บ: ให้ import personal profile JSON และบันทึก Phase 2 ก่อน เพื่อให้ตารางแม่นขึ้น")

    result = _lpe_v4_build_timetable(profile, daily_context, rule_bank)
    st.session_state["lpe_version_a_daily_timetable_result"] = result

    st.subheader("โหมดของวันนี้")
    st.info(result["day_mode"])

    if result.get("warnings"):
        st.subheader("คำเตือนก่อนใช้ตาราง")
        for item in result["warnings"]:
            st.warning(item)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**MUST — ต้องทำ**")
        for item in result["must"]:
            st.write(f"- {item}")
    with c2:
        st.markdown("**SHOULD — ควรทำ**")
        for item in result["should"]:
            st.write(f"- {item}")
    with c3:
        st.markdown("**COULD — ทำได้ถ้าเหลือแรง**")
        for item in result["could"]:
            st.write(f"- {item}")

    st.subheader("ตารางกิจวัตรวันนี้")
    st.table(result["blocks"])

    st.subheader("สิ่งที่ต้องเลี่ยง")
    for item in result["avoid"]:
        st.write(f"- {item}")

    st.success(result["fallback_rule"])

    with st.expander("ดูข้อมูล engine แบบย่อ"):
        st.json(result)



# LPE_VERSION_A_PHASE10B_DAILY_ACTION_BOARD_LAYOUT_MARKER_V1
# Version A Personal MVP — Phase 10B Daily Action Board Layout Patch
# Local/session-only one-page board. No account, no remote sync, no background service.


def _lpe10b_pick(mapping, keys, default=""):
    if not isinstance(mapping, dict):
        return default
    for key in keys:
        if key in mapping and mapping.get(key) not in (None, ""):
            return mapping.get(key)
    lowered = {str(k).lower(): v for k, v in mapping.items()}
    for key in keys:
        lk = str(key).lower()
        if lk in lowered and lowered[lk] not in (None, ""):
            return lowered[lk]
    return default


def _lpe10b_to_text(value, default=""):
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _lpe10b_get_profile():
    if "_lpe_v4_get_profile" in globals():
        try:
            value = _lpe_v4_get_profile()
            if isinstance(value, dict) and value:
                return value
        except Exception:
            pass
    for key in ("lpe_version_a_personal_profile_v1", "lpe_version_a_personal_profile", "personal_profile", "profile"):
        value = st.session_state.get(key)
        if isinstance(value, dict) and value:
            return value
    return {}


def _lpe10b_get_daily_context():
    if "_lpe_v4_get_daily_context" in globals():
        try:
            value = _lpe_v4_get_daily_context()
            if isinstance(value, dict) and value:
                return value
        except Exception:
            pass
    for key in ("lpe_version_a_daily_context", "daily_context", "today_context", "current_daily_context"):
        value = st.session_state.get(key)
        if isinstance(value, dict) and value:
            return value
    collection = st.session_state.get("daily_contexts")
    if isinstance(collection, dict) and collection:
        try:
            return list(collection.values())[-1]
        except Exception:
            return {}
    if isinstance(collection, list) and collection:
        return collection[-1] if isinstance(collection[-1], dict) else {}
    return {}


def _lpe10b_get_rule_bank(profile, daily_context):
    value = st.session_state.get("lpe_version_a_rule_bank_result")
    if isinstance(value, dict) and value:
        return value
    if "lpe_vA3_build_rule_bank" in globals():
        try:
            built = lpe_vA3_build_rule_bank(profile, daily_context)
            if isinstance(built, dict) and built:
                st.session_state["lpe_version_a_rule_bank_result"] = built
                return built
        except Exception:
            pass
    return {}


def _lpe10b_get_timetable(profile, daily_context, rule_bank):
    value = st.session_state.get("lpe_version_a_daily_timetable_result")
    if isinstance(value, dict) and value and value.get("blocks"):
        return value, "session_result"
    if "_lpe_v4_build_timetable" in globals():
        try:
            built = _lpe_v4_build_timetable(profile, daily_context, rule_bank)
            if isinstance(built, dict) and built:
                st.session_state["lpe_version_a_daily_timetable_result"] = built
                return built, "rebuilt_from_existing_engine"
        except Exception as exc:
            return {"warnings": [f"Daily Action Board rebuild warning: {exc}"]}, "rebuild_warning"
    return {}, "missing"


def _lpe10b_normalize_blocks(timetable, daily_context):
    blocks = []
    raw_blocks = timetable.get("blocks", []) if isinstance(timetable, dict) else []
    if isinstance(raw_blocks, list):
        for idx, item in enumerate(raw_blocks):
            if not isinstance(item, dict):
                continue
            time_text = _lpe10b_to_text(item.get("เวลา"), f"Block {idx+1}")
            action = _lpe10b_to_text(item.get("ทำอะไร"), "งานสำคัญของช่วงนี้")
            reason = _lpe10b_to_text(item.get("เหตุผล"), "ช่วยให้วันนี้ไม่หลุดจากเป้าหมายหลัก")
            blocks.append({"time": time_text, "action": action, "reason": reason})
    if blocks:
        return blocks

    wake = _lpe10b_pick(daily_context, ["wake_time", "ตื่นกี่โมง"], "หลังตื่น")
    study = _lpe10b_pick(daily_context, ["study_focus", "วันนี้ควรอ่านอะไร"], "อ่านหนังสือขั้นต่ำ 20–30 นาที")
    project = _lpe10b_pick(daily_context, ["project_focus", "วันนี้ทำโปรเจกต์ได้แค่ไหน"], "โปรเจกต์ 1 block สั้น")
    food = _lpe10b_pick(daily_context, ["available_food", "food_available", "วันนี้มีอาหารอะไร"], "อาหารง่าย โปรตีน + ผัก ถ้ามี")
    start = _lpe10b_pick(daily_context, ["work_start", "เริ่มงานกี่โมง"], "เวลางาน")
    end = _lpe10b_pick(daily_context, ["work_end", "เลิกงานกี่โมง"], "")
    shift = _lpe10b_pick(daily_context, ["today_shift", "วันนี้มีเวรอะไร"], "งานหลัก")
    return [
        {"time": f"หลังตื่น {wake}", "action": "ดื่มน้ำ / ตั้งหลัก / เปิดแผนวันนี้", "reason": "เริ่มวันแบบไม่ใช้แรงใจมากเกินไป"},
        {"time": "มื้อแรก", "action": food, "reason": "เลือกอาหารที่ทำตามได้จริงก่อนคิดเมนูสมบูรณ์แบบ"},
        {"time": "ช่วงโฟกัสแรก", "action": study, "reason": "งานสอบ/การอ่านมี deadline และควรได้ก่อนโปรเจกต์"},
        {"time": "block โปรเจกต์", "action": project, "reason": "รักษา momentum แต่ห้ามกินเวลานอนและการอ่าน"},
        {"time": f"{start}–{end}".strip("–"), "action": f"เวร/งานหลัก ({shift})", "reason": "งานหลักเป็น Must Do ของวัน"},
        {"time": "ท้ายวัน", "action": "ปิดวัน + จด next action 1 บรรทัด", "reason": "ให้วันถัดไปเริ่มต่อได้ทันทีโดยไม่ต้องคิดใหม่"},
    ]


def _lpe10b_guidance(action, reason, daily_context):
    text = f"{action} {reason}".lower()
    energy = _lpe10b_to_text(_lpe10b_pick(daily_context, ["energy_level", "energy", "พลังงานตอนนี้"], ""))
    avoid_food = _lpe10b_to_text(_lpe10b_pick(daily_context, ["food_to_avoid_today", "food_to_avoid", "วันนี้ควรเลี่ยงอาหารอะไร"], ""))

    if "อ่าน" in text or "study" in text:
        return "ใช้บล็อก 20–30 นาทีหรือ 1 หัวข้อย่อยก่อน งานอ่านจะเริ่มง่ายขึ้นเมื่อเป้าหมายเล็กและจบชัด"
    if "เวร" in text or "งานหลัก" in text or "work" in text:
        return "ก่อนเข้าเวรอย่าเปิดงานใหม่ เก็บพลังงานให้พอสำหรับงานหลัก แล้วค่อยบันทึก next action หลังจบเวร"
    if "โปรเจกต์" in text or "project" in text:
        return "เลือกงานย่อยเดียวที่ปิดได้ในรอบสั้น ห้ามขยาย scope ระหว่างทำ เพราะจะเบียดอ่านหนังสือและเวลานอน"
    if "อาหาร" in text or "กิน" in text or "มื้อ" in text or "ไข่" in text or "ผัก" in text:
        extra = f" วันนี้ควรระวัง: {avoid_food}" if avoid_food else ""
        return "เลือกของที่ทำตามได้จริง เช่น โปรตีนง่าย + ผัก + น้ำเปล่า ลดหวาน/มันช่วงเย็นเพื่อลดหนักท้อง" + extra
    if "ออกกำลัง" in text or "ยืด" in text or "เดิน" in text:
        return f"พลังงานวันนี้ {energy or 'ไม่ระบุ'}: เลือกเบาไว้ก่อน เช่น เดิน/ยืด 10–20 นาที เพื่อรักษาความต่อเนื่องโดยไม่ทำให้พรุ่งนี้ล้า"
    if "นอน" in text or "พัก" in text or "ปิดวัน" in text:
        return "ปิดจอก่อนนอนและจด next action แค่ 1 บรรทัด ลดภาระสมองของวันถัดไป"
    return "ทำช่วงนี้ให้จบแบบเล็กและชัด ดีกว่าเปิดงานใหญ่หลายอย่างพร้อมกัน"


def _lpe10b_status_badge(done):
    if done:
        return "<span class='lpe10b-badge-done'>เขียว · ทำแล้ว</span>"
    return "<span class='lpe10b-badge-pending'>เทา · ยังไม่ทำ</span>"


def _lpe10b_render_daily_action_board_layout_v1():
    try:
        from datetime import datetime as _lpe10b_datetime
    except Exception:
        _lpe10b_datetime = None

    profile = _lpe10b_get_profile()
    daily_context = _lpe10b_get_daily_context()
    rule_bank = _lpe10b_get_rule_bank(profile, daily_context)
    timetable, source = _lpe10b_get_timetable(profile, daily_context, rule_bank)
    blocks = _lpe10b_normalize_blocks(timetable, daily_context)

    day_mode = _lpe10b_to_text((timetable or {}).get("day_mode"), _lpe10b_to_text((rule_bank or {}).get("day_mode"), "ยังไม่มีโหมดวันนี้"))
    today_shift = _lpe10b_to_text(_lpe10b_pick(daily_context, ["today_shift", "วันนี้มีเวรอะไร"], "ไม่ระบุ"))
    energy = _lpe10b_to_text(_lpe10b_pick(daily_context, ["energy_level", "energy", "พลังงานตอนนี้"], "ไม่ระบุ"))
    primary_focus = _lpe10b_to_text(_lpe10b_pick(daily_context, ["primary_focus", "main_priority", "เรื่องสำคัญที่สุดวันนี้"], "ยังไม่ระบุ"))
    avoid_today = _lpe10b_to_text(_lpe10b_pick(daily_context, ["avoid_today", "วันนี้ต้องเลี่ยงอะไร"], _lpe10b_to_text((rule_bank or {}).get("avoid_today"), "เปิด scope ใหม่")))

    st.markdown("---")
    st.markdown("""
<style>
.lpe10b-wrap {background:#ffffff; border:1px solid #e5eef8; border-radius:18px; padding:18px 18px 10px 18px; margin:8px 0 18px 0; box-shadow:0 4px 18px rgba(15,23,42,0.05);}
.lpe10b-title {font-size:1.45rem; font-weight:800; color:#0f172a; margin-bottom:2px;}
.lpe10b-sub {color:#475569; font-size:0.94rem; margin-bottom:8px;}
.lpe10b-chip {display:inline-block; padding:6px 10px; margin:3px 5px 3px 0; border-radius:999px; background:#eff6ff; color:#1d4ed8; font-size:0.86rem; font-weight:650;}
.lpe10b-row {border-top:1px solid #eef2f7; padding:10px 0;}
.lpe10b-badge-done {display:inline-block; background:#dcfce7; color:#166534; padding:4px 8px; border-radius:999px; font-size:0.82rem; font-weight:700;}
.lpe10b-badge-pending {display:inline-block; background:#f1f5f9; color:#475569; padding:4px 8px; border-radius:999px; font-size:0.82rem; font-weight:700;}
.lpe10b-small {font-size:0.86rem; color:#64748b;}
</style>
""", unsafe_allow_html=True)
    st.markdown("<div class='lpe10b-wrap'>", unsafe_allow_html=True)
    st.markdown("<div class='lpe10b-title'>📋 Phase 10B — Daily Action Board</div>", unsafe_allow_html=True)
    st.markdown("<div class='lpe10b-sub'>ตารางวันนี้หน้าเดียว: เวลา · ทำอะไร · เพราะอะไร · เทคนิคเสริม · สถานะเทา/เขียว</div>", unsafe_allow_html=True)
    st.markdown(
        f"<span class='lpe10b-chip'>โหมด: {day_mode}</span>"
        f"<span class='lpe10b-chip'>เวรวันนี้: {today_shift}</span>"
        f"<span class='lpe10b-chip'>พลังงาน: {energy}</span>"
        f"<span class='lpe10b-chip'>เป้าหมาย: {primary_focus}</span>",
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='lpe10b-small'>ควรเลี่ยงวันนี้: {avoid_today}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if not profile or not daily_context:
        st.warning("Daily Action Board ยังใช้ fallback: ให้ import profile และกรอก Phase 2 เพื่อให้คำแนะนำแม่นขึ้น")

    warnings = []
    if isinstance(timetable, dict):
        warnings.extend([str(x) for x in timetable.get("warnings", []) if str(x).strip()])
    if isinstance(rule_bank, dict):
        warnings.extend([str(x) for x in rule_bank.get("shift_warning", []) if str(x).strip()])
    for w in dict.fromkeys(warnings):
        st.warning(w)

    st.subheader("ตารางวันนี้")
    st.caption("สถานะ: ปิด/เทา = ยังไม่ทำ, เปิด/เขียว = ทำแล้ว · หมายเหตุใส่เฉพาะจำเป็น")

    status_state = st.session_state.get("lpe_version_a_phase10b_action_status_v1")
    if not isinstance(status_state, dict):
        status_state = {}
    note_state = st.session_state.get("lpe_version_a_phase10b_action_notes_v1")
    if not isinstance(note_state, dict):
        note_state = {}

    action_records = []
    header = st.columns([1.1, 2.0, 2.0, 2.5, 1.1, 1.5])
    header[0].markdown("**เวลา**")
    header[1].markdown("**ทำอะไร**")
    header[2].markdown("**เพราะอะไร**")
    header[3].markdown("**เทคนิค / ความรู้เสริม**")
    header[4].markdown("**สถานะ**")
    header[5].markdown("**หมายเหตุ**")

    for idx, block in enumerate(blocks):
        item_id = f"phase10b_action_{idx:02d}_{abs(hash(str(block))) % 100000}"
        time_text = _lpe10b_to_text(block.get("time"), f"Block {idx+1}")
        action = _lpe10b_to_text(block.get("action"), "งานสำคัญ")
        reason = _lpe10b_to_text(block.get("reason"), "ช่วยให้วันนี้เดินต่อได้")
        tip = _lpe10b_guidance(action, reason, daily_context)
        cols = st.columns([1.1, 2.0, 2.0, 2.5, 1.1, 1.5])
        cols[0].markdown(f"**{time_text}**")
        cols[1].write(action)
        cols[2].write(reason)
        cols[3].write(tip)
        current_done = bool(status_state.get(item_id, False))
        done = cols[4].toggle("ทำแล้ว", value=current_done, key=f"lpe10b_toggle_{idx}")
        status_state[item_id] = bool(done)
        cols[4].markdown(_lpe10b_status_badge(done), unsafe_allow_html=True)
        note = cols[5].text_input(" ", value=_lpe10b_to_text(note_state.get(item_id), ""), key=f"lpe10b_note_{idx}", placeholder="สั้น ๆ")
        note_state[item_id] = note
        action_records.append({
            "id": item_id,
            "time": time_text,
            "action": action,
            "reason": reason,
            "guidance": tip,
            "done": bool(done),
            "note": note,
        })

    st.session_state["lpe_version_a_phase10b_action_status_v1"] = status_state
    st.session_state["lpe_version_a_phase10b_action_notes_v1"] = note_state

    done_count = sum(1 for item in action_records if item.get("done"))
    total_count = len(action_records)
    st.success(f"ความคืบหน้าวันนี้: {done_count}/{total_count} รายการ")

    with st.expander("Quick summary จากตารางนี้"):
        st.write("ระบบใช้สถานะเทา/เขียวและหมายเหตุสั้น ๆ ในหน้านี้ เพื่อลดภาระการกรอกท้ายวัน")
        st.write("ข้อจำกัด: คำแนะนำอาหาร/ออกกำลังเป็นคำแนะนำทั่วไป ไม่ใช่การรักษา ไม่ใช่แผนโภชนาการหรือฟิตเนสเฉพาะบุคคล")
        st.json({
            "source": source,
            "day_mode": day_mode,
            "today_shift": today_shift,
            "energy": energy,
            "done_count": done_count,
            "total_count": total_count,
            "actions": action_records,
        })

    result = {
        "schema_version": "lpe_version_a_phase10b_daily_action_board_layout_v1",
        "created_at": _lpe10b_datetime.now().isoformat(timespec="seconds") if _lpe10b_datetime else "",
        "source": source,
        "day_mode": day_mode,
        "today_shift": today_shift,
        "energy": energy,
        "primary_focus": primary_focus,
        "avoid_today": avoid_today,
        "done_count": done_count,
        "total_count": total_count,
        "actions": action_records,
        "safety_boundary": "practical guidance only; no diagnosis, no nutrition prescription, no full fitness coaching",
    }
    st.session_state["lpe_version_a_phase10b_daily_action_board_result"] = result

    legacy = st.checkbox("แสดง Phase 3–5 เดิมชั่วคราวเพื่อเทียบผล", value=bool(st.session_state.get("lpe_phase10b_show_legacy_phase3_5", False)), key="lpe10b_legacy_checkbox")
    st.session_state["lpe_phase10b_show_legacy_phase3_5"] = bool(legacy)


try:
    _lpe10b_render_daily_action_board_layout_v1()
except Exception as exc:
    st.error(f"Phase 10B Daily Action Board render error: {exc}")
# LPE_VERSION_A_PHASE10B_DAILY_ACTION_BOARD_LAYOUT_END_V1


# LPE_VERSION_A_PHASE5_MAIN_TIMETABLE_UI_MARKER_V1
# Version A Personal MVP — Phase 5 Main Timetable UI
# Local-only, session-only display layer for the existing daily timetable result.


def _lpe_v5_bool_label(value):
    return "พร้อม" if value else "ยังไม่ครบ"


def _lpe_v5_get_profile_safe():
    if "_lpe_v4_get_profile" in globals():
        try:
            return _lpe_v4_get_profile()
        except Exception:
            pass
    for key in ("lpe_version_a_personal_profile_v1", "lpe_version_a_personal_profile", "lpe_personal_profile", "personal_profile", "life_profile", "profile"):
        value = st.session_state.get(key)
        if isinstance(value, dict) and value:
            return value
    return {}


def _lpe_v5_get_daily_context_safe():
    if "_lpe_v4_get_daily_context" in globals():
        try:
            return _lpe_v4_get_daily_context()
        except Exception:
            pass
    for key in ("lpe_version_a_daily_context", "daily_context", "today_context", "current_daily_context"):
        value = st.session_state.get(key)
        if isinstance(value, dict) and value:
            return value
    collection = st.session_state.get("daily_contexts")
    if isinstance(collection, list) and collection:
        return collection[-1]
    if isinstance(collection, dict) and collection:
        return list(collection.values())[-1]
    return {}


def _lpe_v5_get_rule_bank_safe():
    value = st.session_state.get("lpe_version_a_rule_bank_result")
    if isinstance(value, dict) and value:
        return value
    for key in ("rule_bank_result", "daily_rule_bank_result"):
        value = st.session_state.get(key)
        if isinstance(value, dict) and value:
            return value
    return {}


def _lpe_v5_get_timetable_result_safe(profile, daily_context, rule_bank):
    result = st.session_state.get("lpe_version_a_daily_timetable_result")
    if isinstance(result, dict) and result:
        return result, "session_result"
    if "_lpe_v4_build_timetable" in globals():
        try:
            built = _lpe_v4_build_timetable(profile, daily_context, rule_bank)
            if isinstance(built, dict) and built:
                st.session_state["lpe_version_a_daily_timetable_result"] = built
                return built, "rebuilt_from_phase4_engine"
        except Exception as exc:
            return {"warnings": [f"Phase 4 engine rebuild error: {exc}"]}, "rebuild_error"
    return {}, "missing"


def _lpe_v5_normalize_blocks(blocks):
    if isinstance(blocks, list):
        clean = []
        for item in blocks:
            if isinstance(item, dict):
                clean.append({
                    "เวลา": str(item.get("เวลา", "")),
                    "ทำอะไร": str(item.get("ทำอะไร", "")),
                    "เหตุผล": str(item.get("เหตุผล", "")),
                    "ถ้าเหนื่อยมาก": str(item.get("ถ้าเหนื่อยมาก", "")),
                })
        return clean
    return []


def _lpe_v5_data_quality(profile, daily_context, rule_bank, timetable, source):
    has_profile = bool(profile)
    has_daily = bool(daily_context)
    has_rule_bank = bool(rule_bank)
    has_timetable = bool(timetable and _lpe_v5_normalize_blocks(timetable.get("blocks", [])))
    complete = has_profile and has_daily and has_timetable
    warnings = []
    if not has_profile:
        warnings.append("ยังไม่พบ personal profile ใน session: ให้ import profile JSON ก่อน")
    if not has_daily:
        warnings.append("ยังไม่พบคำตอบ Phase 2 ของวันนี้ใน session: ให้กรอกและบันทึกก่อน")
    if not has_rule_bank:
        warnings.append("ยังไม่พบผล Rule Bank ใน session: ตารางอาจใช้ fallback มากกว่ากฎเต็ม")
    if source != "session_result":
        warnings.append("ตารางนี้ไม่ได้มาจากผล session เดิมโดยตรง: ระบบ rebuild/fallback จากข้อมูลที่พบ")
    if not has_timetable:
        warnings.append("ยังไม่มี time blocks ที่ใช้ได้: ต้องเติม profile + Phase 2 ก่อน")
    return {
        "has_profile": has_profile,
        "has_daily_context": has_daily,
        "has_rule_bank_result": has_rule_bank,
        "has_daily_timetable": has_timetable,
        "complete_enough_for_main_table": complete,
        "source": source,
        "warnings": warnings,
    }


def _lpe_v5_render_status_cards(quality):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Profile", _lpe_v5_bool_label(quality["has_profile"]))
    with c2:
        st.metric("Phase 2 วันนี้", _lpe_v5_bool_label(quality["has_daily_context"]))
    with c3:
        st.metric("Rule Bank", _lpe_v5_bool_label(quality["has_rule_bank_result"]))
    with c4:
        st.metric("ตารางหลัก", _lpe_v5_bool_label(quality["has_daily_timetable"]))


def _lpe_v5_render_list(title, items, empty_text="ยังไม่มีข้อมูล"):
    st.markdown(f"**{title}**")
    if not items:
        st.caption(empty_text)
        return
    for item in items:
        st.write(f"- {item}")


def _lpe_v5_render_main_timetable_ui():
    st.markdown("---")
    st.header("🧭 Phase 5 — Main Timetable UI")
    st.caption("ทำให้ตารางวันนี้เป็นหน้าหลัก อ่านง่าย และบอกชัดว่าใช้ข้อมูลครบหรือยัง")

    profile = _lpe_v5_get_profile_safe()
    daily_context = _lpe_v5_get_daily_context_safe()
    rule_bank = _lpe_v5_get_rule_bank_safe()
    timetable, source = _lpe_v5_get_timetable_result_safe(profile, daily_context, rule_bank)
    quality = _lpe_v5_data_quality(profile, daily_context, rule_bank, timetable, source)
    st.session_state["lpe_version_a_main_timetable_ui_status"] = quality

    if quality["complete_enough_for_main_table"]:
        st.success("ข้อมูลหลักพร้อมใช้ — ตารางนี้ใช้เป็นแผนวันนี้ได้")
    else:
        st.warning("ตารางนี้ยังมี fallback เพราะข้อมูลยังไม่ครบ: เติม profile + Phase 2 เพื่อให้แม่นขึ้น")

    _lpe_v5_render_status_cards(quality)

    warnings = list(timetable.get("warnings", [])) if isinstance(timetable, dict) else []
    warnings.extend(quality.get("warnings", []))
    if warnings:
        st.subheader("คำเตือนข้อมูลก่อนใช้ตาราง")
        for item in dict.fromkeys(str(w) for w in warnings if str(w).strip()):
            st.warning(item)

    day_mode = timetable.get("day_mode", "ยังไม่มีโหมดของวันนี้") if isinstance(timetable, dict) else "ยังไม่มีโหมดของวันนี้"
    st.subheader("โหมดวันนี้")
    st.info(day_mode)

    blocks = _lpe_v5_normalize_blocks(timetable.get("blocks", [])) if isinstance(timetable, dict) else []
    st.subheader("ตารางหลักวันนี้")
    if blocks:
        st.table(blocks)
    else:
        st.error("ยังสร้างตารางหลักไม่ได้ — ต้อง import profile JSON และกรอก Phase 2 ก่อน")

    st.subheader("ตัดสินใจเร็ว")
    c1, c2, c3 = st.columns(3)
    with c1:
        _lpe_v5_render_list("MUST — ต้องทำ", timetable.get("must", []) if isinstance(timetable, dict) else [])
    with c2:
        _lpe_v5_render_list("SHOULD — ควรทำ", timetable.get("should", []) if isinstance(timetable, dict) else [])
    with c3:
        _lpe_v5_render_list("COULD — ทำได้ถ้าเหลือแรง", timetable.get("could", []) if isinstance(timetable, dict) else [])

    st.subheader("สิ่งที่ต้องเลี่ยง")
    _lpe_v5_render_list("Avoid", timetable.get("avoid", []) if isinstance(timetable, dict) else [])

    fallback = timetable.get("fallback_rule", "ถ้าเหนื่อยมาก ให้เหลือเฉพาะงานหลัก + อ่านขั้นต่ำ + บันทึก next action + นอน") if isinstance(timetable, dict) else "ถ้าเหนื่อยมาก ให้เหลือเฉพาะงานหลัก + อ่านขั้นต่ำ + บันทึก next action + นอน"
    st.success(f"Fallback: {fallback}")

    with st.expander("ดูสถานะข้อมูล/engine แบบย่อ"):
        st.json({"quality": quality, "timetable_source": source, "timetable": timetable})


if st.session_state.get("lpe_phase10b_show_legacy_phase3_5", False):
    _lpe_v5_render_main_timetable_ui()

# -----------------------------------------------------------------------------
# LPE VERSION A PHASE 6 - BOTTOM NEXT-DAY INPUT PATCH V1
# Purpose: collect end-of-day reflection and tomorrow adjustment input.
# Scope: local/session-only; no persistent storage service.
# -----------------------------------------------------------------------------
LPE_VERSION_A_PHASE6_BOTTOM_NEXT_DAY_INPUT_VERSION = "lpe_version_a_phase6_bottom_next_day_input_v1"


def _lpe_vA_phase6_safe_get_session(key, default=None):
    try:
        return st.session_state.get(key, default)
    except Exception:
        return default


def _lpe_vA_phase6_ready_flag(value):
    if isinstance(value, dict):
        return bool(value)
    if isinstance(value, list):
        return len(value) > 0
    return bool(value)


def _lpe_vA_phase6_today_text():
    try:
        from datetime import date
        return date.today().isoformat()
    except Exception:
        return "today"


def _lpe_vA_phase6_build_next_day_input_status():
    profile = (
        _lpe_vA_phase6_safe_get_session("lpe_version_a_personal_profile_v1", {}) or _lpe_vA_phase6_safe_get_session("lpe_version_a_personal_profile", {})
        or _lpe_vA_phase6_safe_get_session("life_profile", {})
        or _lpe_vA_phase6_safe_get_session("profile", {})
    )
    daily_context = (
        _lpe_vA_phase6_safe_get_session("lpe_version_a_daily_context", {})
        or _lpe_vA_phase6_safe_get_session("daily_context", {})
    )
    rule_bank = _lpe_vA_phase6_safe_get_session("lpe_version_a_rule_bank_result", {})
    timetable = _lpe_vA_phase6_safe_get_session("lpe_version_a_daily_timetable_result", {})
    status = {
        "profile_ready": _lpe_vA_phase6_ready_flag(profile),
        "daily_context_ready": _lpe_vA_phase6_ready_flag(daily_context),
        "rule_bank_ready": _lpe_vA_phase6_ready_flag(rule_bank),
        "timetable_ready": _lpe_vA_phase6_ready_flag(timetable),
        "schema_version": LPE_VERSION_A_PHASE6_BOTTOM_NEXT_DAY_INPUT_VERSION,
    }
    st.session_state["lpe_version_a_next_day_input_status"] = status
    return status


def _lpe_vA_phase6_render_bottom_next_day_input():
    st.markdown("---")
    st.header("🌙 Phase 6 — สรุปวันนี้ / เตรียมพรุ่งนี้")
    st.caption("เก็บ input ท้ายวันใน session เพื่อให้ Phase 7 ใช้ปรับแผนวันถัดไป")

    status = _lpe_vA_phase6_build_next_day_input_status()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Profile", "พร้อม" if status.get("profile_ready") else "ยังไม่ครบ")
    c2.metric("Phase 2 วันนี้", "พร้อม" if status.get("daily_context_ready") else "ยังไม่ครบ")
    c3.metric("Rule Bank", "พร้อม" if status.get("rule_bank_ready") else "ยังไม่ครบ")
    c4.metric("ตารางวันนี้", "พร้อม" if status.get("timetable_ready") else "ยังไม่ครบ")

    if not status.get("timetable_ready"):
        st.warning("ยังไม่พบตารางวันนี้ใน session: ให้กลับไปสร้าง Phase 4/5 ก่อน แล้วค่อยบันทึกสรุปท้ายวัน")
    if not status.get("profile_ready"):
        st.warning("ยังไม่พบ profile ใน session: ให้ import profile JSON ก่อน เพื่อให้ Phase 7 ปรับพรุ่งนี้ได้แม่นขึ้น")

    prior = _lpe_vA_phase6_safe_get_session("lpe_version_a_next_day_input_result", {}) or {}

    st.subheader("บันทึกผลจริงของวันนี้")
    with st.form("lpe_version_a_phase6_bottom_next_day_input_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            day_result = st.selectbox(
                "วันนี้จบแบบไหน",
                ["ยังไม่ระบุ", "ทำได้ดี", "พอใช้/กันหลุดได้", "หลุดบางส่วน", "เหนื่อยมาก/ทำได้น้อย"],
                index=0,
                key="lpe_phase6_day_result_select",
            )
            end_energy = st.slider(
                "พลังงานท้ายวัน",
                min_value=1,
                max_value=5,
                value=int(prior.get("end_energy", 3) or 3),
                key="lpe_phase6_end_energy_slider",
            )
            actual_sleep_hours = st.number_input(
                "นอนจริง/นอนสะสมวันนี้ประมาณกี่ชั่วโมง",
                min_value=0.0,
                max_value=16.0,
                value=float(prior.get("actual_sleep_hours", 0.0) or 0.0),
                step=0.5,
                key="lpe_phase6_actual_sleep_hours_input",
            )
        with col_b:
            tomorrow_shift = st.selectbox(
                "พรุ่งนี้มีเวรอะไร",
                ["ยังไม่ระบุ", "เวรเช้า", "เวรบ่าย", "เวรดึก", "หยุด", "อื่น ๆ"],
                index=0,
                key="lpe_phase6_tomorrow_shift_select",
            )
            tomorrow_must = st.text_area(
                "พรุ่งนี้สิ่งที่ห้ามพลาดคืออะไร",
                value=str(prior.get("tomorrow_must", "")),
                height=80,
                key="lpe_phase6_tomorrow_must_text",
            )
            tomorrow_reduce = st.text_area(
                "พรุ่งนี้ควรลด/ตัดอะไรออก",
                value=str(prior.get("tomorrow_reduce", "")),
                height=80,
                key="lpe_phase6_tomorrow_reduce_text",
            )

        completed_today = st.text_area(
            "วันนี้ทำอะไรสำเร็จจริง",
            value=str(prior.get("completed_today", "")),
            height=90,
            key="lpe_phase6_completed_today_text",
        )
        missed_today = st.text_area(
            "วันนี้อะไรยังไม่เสร็จ / ติดตรงไหน",
            value=str(prior.get("missed_today", "")),
            height=90,
            key="lpe_phase6_missed_today_text",
        )
        adjust_tomorrow = st.text_area(
            "พรุ่งนี้ควรปรับแผนอย่างไรจากผลจริงวันนี้",
            value=str(prior.get("adjust_tomorrow", "")),
            height=100,
            key="lpe_phase6_adjust_tomorrow_text",
        )
        next_single_action = st.text_input(
            "next single action ตอนเปิดเว็บครั้งถัดไป",
            value=str(prior.get("next_single_action", "")),
            key="lpe_phase6_next_single_action_text",
        )
        note_for_next_chat = st.text_area(
            "บันทึกสั้น ๆ สำหรับแชท/รอบถัดไป",
            value=str(prior.get("note_for_next_chat", "")),
            height=80,
            key="lpe_phase6_note_for_next_chat_text",
        )

        save_phase6 = st.form_submit_button("บันทึก input สำหรับพรุ่งนี้")

    if save_phase6:
        result = {
            "schema_version": LPE_VERSION_A_PHASE6_BOTTOM_NEXT_DAY_INPUT_VERSION,
            "date": _lpe_vA_phase6_today_text(),
            "day_result": day_result,
            "end_energy": end_energy,
            "actual_sleep_hours": actual_sleep_hours,
            "completed_today": completed_today.strip(),
            "missed_today": missed_today.strip(),
            "tomorrow_shift": tomorrow_shift,
            "tomorrow_must": tomorrow_must.strip(),
            "tomorrow_reduce": tomorrow_reduce.strip(),
            "adjust_tomorrow": adjust_tomorrow.strip(),
            "next_single_action": next_single_action.strip(),
            "note_for_next_chat": note_for_next_chat.strip(),
            "readiness_status": status,
            "phase7_ready": True,
        }
        st.session_state["lpe_version_a_next_day_input_result"] = result
        existing = st.session_state.get("lpe_version_a_next_day_inputs", [])
        if not isinstance(existing, list):
            existing = []
        existing.append(result)
        st.session_state["lpe_version_a_next_day_inputs"] = existing
        st.success("บันทึก input สำหรับพรุ่งนี้แล้ว — Phase 7 จะใช้ข้อมูลนี้เพื่อปรับแผนวันถัดไป")

    saved = _lpe_vA_phase6_safe_get_session("lpe_version_a_next_day_input_result", {}) or {}
    if saved:
        st.subheader("สรุป input สำหรับพรุ่งนี้ล่าสุด")
        col1, col2, col3 = st.columns(3)
        col1.metric("ผลวันนี้", saved.get("day_result", "ยังไม่ระบุ"))
        col2.metric("พลังงานท้ายวัน", saved.get("end_energy", "-"))
        col3.metric("เวรพรุ่งนี้", saved.get("tomorrow_shift", "ยังไม่ระบุ"))
        st.info(f"พรุ่งนี้ควรปรับ: {saved.get('adjust_tomorrow') or 'ยังไม่ได้กรอก'}")
        st.caption(f"Next single action: {saved.get('next_single_action') or 'ยังไม่ได้กรอก'}")


try:
    _lpe_vA_phase6_render_bottom_next_day_input()
except Exception as _lpe_phase6_error:
    st.error(f"Phase 6 next-day input แสดงผลไม่สำเร็จ: {_lpe_phase6_error}")



# ============================================================
# LPE_VERSION_A_PHASE7_REFLECTION_ADAPTATION_ENGINE_V1
# Local/session-only. No login/admin/multi-user/database/cloud/external AI/API.
# Purpose: convert today's actual result + next-day input into tomorrow adjustment guidance.
# ============================================================

LPE_VERSION_A_PHASE7_REFLECTION_ADAPTATION_ENGINE_VERSION = "version_a_phase7_reflection_adaptation_engine_v1"


def _lpe_vA_phase7_safe_str(value, default=""):
    if value is None:
        return default
    return str(value).strip()


def _lpe_vA_phase7_safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _lpe_vA_phase7_pick(mapping, keys, default=""):
    if not isinstance(mapping, dict):
        return default
    for key in keys:
        if key in mapping and mapping.get(key) not in (None, ""):
            return mapping.get(key)
    return default


def _lpe_vA_phase7_get_context_snapshot():
    profile = st.session_state.get("lpe_version_a_personal_profile_v1") or st.session_state.get("lpe_version_a_personal_profile") or st.session_state.get("personal_profile") or {}
    daily_context = st.session_state.get("lpe_version_a_daily_context") or {}
    rule_bank = st.session_state.get("lpe_version_a_rule_bank_result") or {}
    timetable = st.session_state.get("lpe_version_a_daily_timetable_result") or {}
    next_day_input = st.session_state.get("lpe_version_a_next_day_input_result") or {}
    return {
        "profile": _lpe_phase8_get_profile_for_export(),
        "daily_context": daily_context,
        "rule_bank": rule_bank,
        "timetable": timetable,
        "next_day_input": next_day_input,
    }


def _lpe_vA_phase7_profile_ready(profile):
    if not isinstance(profile, dict) or not profile:
        return False
    return bool(profile.get("identity_work") or profile.get("goals") or profile.get("personal_rules"))


def _lpe_vA_phase7_assess_today(next_day_input, daily_context, timetable):
    energy_end = _lpe_vA_phase7_safe_float(
        _lpe_vA_phase7_pick(next_day_input, ["end_energy", "energy_end", "พลังงานท้ายวัน"], 0),
        0,
    )
    sleep_actual = _lpe_vA_phase7_safe_float(
        _lpe_vA_phase7_pick(next_day_input, ["actual_sleep_hours", "sleep_actual_hours", "นอนจริง"], 0),
        0,
    )
    done_text = _lpe_vA_phase7_safe_str(_lpe_vA_phase7_pick(next_day_input, ["done_today", "completed_today", "วันนี้ทำอะไรสำเร็จจริง"], ""))
    unfinished = _lpe_vA_phase7_safe_str(_lpe_vA_phase7_pick(next_day_input, ["unfinished_today", "blocked_today", "วันนี้อะไรยังไม่เสร็จ"], ""))
    mistake = _lpe_vA_phase7_safe_str(_lpe_vA_phase7_pick(next_day_input, ["missed_or_overdid", "พรุ่งนี้สิ่งที่ห้ามพลาดคืออะไร"], ""))
    tomorrow_shift = _lpe_vA_phase7_safe_str(_lpe_vA_phase7_pick(next_day_input, ["tomorrow_shift", "พรุ่งนี้มีเวรอะไร"], ""))
    next_action = _lpe_vA_phase7_safe_str(_lpe_vA_phase7_pick(next_day_input, ["next_single_action", "next single action ตอนเปิดเว็บครั้งถัดไป"], ""))
    return {
        "energy_end": energy_end,
        "sleep_actual": sleep_actual,
        "done_text": done_text,
        "unfinished": unfinished,
        "mistake": mistake,
        "tomorrow_shift": tomorrow_shift,
        "next_action": next_action,
        "has_reflection_input": any([energy_end, sleep_actual, done_text, unfinished, mistake, tomorrow_shift, next_action]),
    }


def _lpe_vA_phase7_decide_tomorrow_mode(assessment, profile, daily_context):
    reasons = []
    energy = assessment.get("energy_end", 0)
    sleep = assessment.get("sleep_actual", 0)
    tomorrow_shift = assessment.get("tomorrow_shift", "")
    if energy and energy <= 2:
        reasons.append("พลังงานท้ายวันต่ำ ต้องลดแผนพรุ่งนี้")
    if sleep and sleep < 7:
        reasons.append("นอนจริงต่ำกว่าเป้าควรชดเชย/ปกป้องการนอน")
    if "ดึก" in tomorrow_shift:
        reasons.append("พรุ่งนี้มีเวรดึก ต้องจัดแผนแบบกันหลุดและกันนอนเสีย")
    elif "บ่าย" in tomorrow_shift:
        reasons.append("พรุ่งนี้มีเวรบ่าย ต้องอ่าน/ทำโปรเจกต์ก่อนเริ่มเวรแบบจำกัด")
    elif "เช้า" in tomorrow_shift:
        reasons.append("พรุ่งนี้มีเวรเช้า ต้องไม่ทำงานดึก")
    unfinished = assessment.get("unfinished", "")
    if unfinished:
        reasons.append("ยังมีงานค้าง ต้องเลือกเฉพาะสิ่งสำคัญ ไม่เพิ่มงานใหม่")
    if not reasons:
        reasons.append("ไม่มีสัญญาณเสี่ยงหนักจาก input ท้ายวัน")
    if (energy and energy <= 2) or (sleep and sleep < 6):
        mode = "Red / Recovery Day"
        mode_reason = "ลดเหลือขั้นต่ำ ปกป้องนอน และทำเฉพาะสิ่งห้ามพลาด"
    elif (energy and energy <= 3) or assessment.get("unfinished") or any(word in tomorrow_shift for word in ["ดึก", "บ่าย", "เช้า"]):
        mode = "Yellow / Controlled Day"
        mode_reason = "ยังทำงานหลักได้ แต่ต้องมี buffer และจำกัดโปรเจกต์"
    else:
        mode = "Green / Normal Day"
        mode_reason = "ทำแผนปกติได้ แต่ยังต้องไม่เปิด scope ใหม่"
    return mode, mode_reason, reasons


def _lpe_vA_phase7_build_adaptation():
    snapshot = _lpe_vA_phase7_get_context_snapshot()
    profile = snapshot["profile"]
    daily_context = snapshot["daily_context"]
    timetable = snapshot["timetable"]
    next_day_input = snapshot["next_day_input"]
    assessment = _lpe_vA_phase7_assess_today(next_day_input, daily_context, timetable)
    profile_ready = _lpe_vA_phase7_profile_ready(profile)
    mode, mode_reason, reasons = _lpe_vA_phase7_decide_tomorrow_mode(assessment, profile, daily_context)

    keep = [
        "งาน/เวรหลักเป็น Must Do",
        "อ่านสอบขั้นต่ำทุกวัน เพราะสอบมี deadline จริง",
        "ใช้ project one-task limit เพื่อไม่ให้กินเวลานอน",
    ]
    reduce = []
    cut = ["เปิดงานใหม่", "ทำโปรเจกต์ยาวจนเสียเวลานอน"]
    tomorrow_shift = assessment.get("tomorrow_shift") or _lpe_vA_phase7_pick(daily_context, ["tomorrow_shift", "พรุ่งนี้มีเวรอะไร"], "ยังไม่ระบุ")
    if assessment.get("energy_end", 0) and assessment.get("energy_end", 0) <= 2:
        reduce += ["ลดโปรเจกต์เหลือ 1 งานย่อย", "ลดออกกำลังเป็นเดิน/ยืดเบา หรือพัก"]
    else:
        reduce += ["คุมโปรเจกต์เป็น block สั้น", "ออกกำลังเบาได้ถ้าไม่เพลีย"]
    if assessment.get("sleep_actual", 0) and assessment.get("sleep_actual", 0) < 7:
        reduce.append("ลดงานรองเพื่อชดเชยนอน")
        keep.append("sleep protection ก่อนงานเสริม")

    minimum_plan = [
        "อ่านสอบขั้นต่ำ 20–30 นาที หรือสรุปหัวข้อย่อย 1 หน้า",
        "ทำงาน/เวรหลักให้ครบ",
        "บันทึก next action สั้น ๆ เพื่อส่งต่อรอบถัดไป",
    ]
    if "ดึก" in tomorrow_shift:
        minimum_plan.insert(0, "นอนก่อนเวรดึก/กันเวลาพักก่อนเริ่มงาน")
    elif "บ่าย" in tomorrow_shift:
        minimum_plan.insert(0, "ทำงานสำคัญช่วงก่อนเวรบ่ายแบบจำกัด")
    elif "เช้า" in tomorrow_shift:
        minimum_plan.insert(0, "ห้ามลากงานดึกก่อนเวรเช้า")

    result = {
        "schema_version": LPE_VERSION_A_PHASE7_REFLECTION_ADAPTATION_ENGINE_VERSION,
        "profile_ready": profile_ready,
        "has_reflection_input": assessment.get("has_reflection_input", False),
        "tomorrow_mode": mode,
        "tomorrow_mode_reason": mode_reason,
        "reasons": reasons,
        "tomorrow_shift": tomorrow_shift,
        "keep": keep,
        "reduce": reduce,
        "cut": cut,
        "minimum_plan": minimum_plan,
        "next_single_action": assessment.get("next_action") or "เปิดเว็บ → import profile ถ้าหาย → กรอก Phase 2 → ใช้ตารางหลัก",
        "warnings": [],
        "phase8_ready_signal": "session-only result ready for JSON persistence phase; no background storage service here",
    }
    if not profile_ready:
        result["warnings"].append("ยังไม่พบ profile ใน session: ให้ import personal profile JSON ก่อนใช้ผลปรับพรุ่งนี้แบบเต็ม")
    if not assessment.get("has_reflection_input"):
        result["warnings"].append("ยังไม่มี input ท้ายวัน: ผลปรับพรุ่งนี้ยังเป็น fallback จากกฎหลัก")
    st.session_state["lpe_version_a_reflection_adaptation_result"] = result
    st.session_state.setdefault("lpe_version_a_reflection_adaptations", [])
    if result not in st.session_state["lpe_version_a_reflection_adaptations"][-3:]:
        st.session_state["lpe_version_a_reflection_adaptations"].append(result)
    return result


def render_lpe_version_a_phase7_reflection_adaptation_engine():
    st.divider()
    st.header("🔁 Phase 7 — Reflection / Adaptation Engine")
    st.caption("แปลงผลจริงท้ายวันเป็นข้อปรับแผนพรุ่งนี้แบบ local/session-only")
    result = _lpe_vA_phase7_build_adaptation()

    cols = st.columns(4)
    cols[0].metric("Profile", "พร้อม" if result.get("profile_ready") else "ยังไม่ครบ")
    cols[1].metric("Input ท้ายวัน", "พร้อม" if result.get("has_reflection_input") else "ยังไม่มี")
    cols[2].metric("โหมดพรุ่งนี้", result.get("tomorrow_mode", "-").split("/")[0].strip())
    cols[3].metric("เวรพรุ่งนี้", result.get("tomorrow_shift") or "ยังไม่ระบุ")

    for warning in result.get("warnings", []):
        st.warning(warning)

    st.subheader("โหมดพรุ่งนี้")
    st.info(f"{result.get('tomorrow_mode')} — {result.get('tomorrow_mode_reason')}")

    st.subheader("เหตุผลที่ระบบปรับแผน")
    for reason in result.get("reasons", []):
        st.write(f"- {reason}")

    a, b, c = st.columns(3)
    with a:
        st.subheader("KEEP — คงไว้")
        for item in result.get("keep", []):
            st.write(f"- {item}")
    with b:
        st.subheader("REDUCE — ลดลง")
        for item in result.get("reduce", []):
            st.write(f"- {item}")
    with c:
        st.subheader("CUT — ตัดออก")
        for item in result.get("cut", []):
            st.write(f"- {item}")

    st.subheader("Minimum Plan พรุ่งนี้")
    for item in result.get("minimum_plan", []):
        st.write(f"- {item}")

    st.warning(f"Next single action: {result.get('next_single_action')}")
    st.caption("Phase 7 result พร้อมให้ Phase 8 ทำ JSON persistence ในขั้นถัดไป — ตอนนี้ยังไม่ทำ database/cloud/background storage service")


try:
    render_lpe_version_a_phase7_reflection_adaptation_engine()
except Exception as exc:
    st.error(f"Phase 7 Reflection Adaptation Engine error: {exc}")



# ============================================================
# LPE_VERSION_A_PHASE8_JSON_PERSISTENCE_LOCAL_ONLY
# Manual JSON export/import only. No login. No database. No remote sync. No external API.
# Purpose: restore session after browser/app restart without adding any service dependency.
# ============================================================
LPE_VERSION_A_PHASE8_JSON_PERSISTENCE_VERSION = "version_a_phase8_json_persistence_local_only_v1"


def _lpe_phase8_safe_get_session_value(key, default=None):
    try:
        return st.session_state.get(key, default)
    except Exception:
        return default


def _lpe_phase8_compact_status(value):
    if value is None:
        return "ยังไม่มี"
    if isinstance(value, (dict, list, tuple, set)) and len(value) == 0:
        return "ยังไม่มี"
    if value == "":
        return "ยังไม่มี"
    return "พร้อม"




# LPE_VERSION_A_PHASE8D_PROFILE_PERSISTENCE_RESTORE_REPAIR
# Profile compatibility bridge for Version A profile key v1 and legacy/local profile keys.
LPE_VERSION_A_PHASE8D_PROFILE_REPAIR_VERSION = "version_a_phase8d_profile_persistence_restore_repair_v1"
LPE_VERSION_A_PHASE8D_PROFILE_KEYS = [
    "lpe_version_a_personal_profile_v1",
    "lpe_version_a_personal_profile",
    "lpe_personal_profile",
    "personal_profile",
    "life_profile",
    "lpe_life_profile",
    "core_life_profile",
    "profile",
]


def _lpe_phase8d_profile_is_usable(value):
    if not isinstance(value, dict) or not value:
        return False
    if value.get("schema_version") == "version_a_personal_dashboard_schema_v1":
        return True
    required_profile_sections = {"identity_work", "goals", "health_food", "exercise", "personal_rules"}
    return required_profile_sections.issubset(set(value.keys()))


def _lpe_phase8_get_profile_for_export():
    """Find the Version A profile across Phase 1 v1 key and compatibility keys."""
    for key in LPE_VERSION_A_PHASE8D_PROFILE_KEYS:
        try:
            value = st.session_state.get(key)
        except Exception:
            value = None
        if _lpe_phase8d_profile_is_usable(value):
            try:
                st.session_state["lpe_version_a_personal_profile_v1"] = value
                st.session_state["lpe_version_a_personal_profile"] = value
                st.session_state["personal_profile"] = value
            except Exception:
                pass
            return value
    try:
        items = list(st.session_state.items())
    except Exception:
        items = []
    for _key, value in items:
        if _lpe_phase8d_profile_is_usable(value):
            try:
                st.session_state["lpe_version_a_personal_profile_v1"] = value
                st.session_state["lpe_version_a_personal_profile"] = value
                st.session_state["personal_profile"] = value
            except Exception:
                pass
            return value
    return None


def _lpe_phase8_extract_profile_from_payload(state, raw, bundle):
    """Extract profile from normalized bundle, raw session payload, direct profile JSON, or compatibility keys."""
    candidates = []
    if isinstance(state, dict):
        candidates.append(state.get("profile"))
    if isinstance(raw, dict):
        for key in LPE_VERSION_A_PHASE8D_PROFILE_KEYS:
            candidates.append(raw.get(key))
    if _lpe_phase8d_profile_is_usable(bundle):
        candidates.append(bundle)
    for value in candidates:
        if _lpe_phase8d_profile_is_usable(value):
            return value
    return None


def _lpe_phase8_collect_bundle():
    """Collect Version A local/session-only state for manual JSON export."""
    import json as _lpe_phase8_json
    from datetime import datetime as _lpe_phase8_datetime

    known_keys = [
        "lpe_version_a_personal_profile_v1",
        "lpe_version_a_personal_profile_v1",
        "lpe_version_a_personal_profile",
        "lpe_personal_profile",
        "personal_profile",
        "life_profile",
        "lpe_life_profile",
        "core_life_profile",
        "profile",
        "lpe_version_a_daily_context",
        "daily_contexts",
        "lpe_version_a_rule_bank_result",
        "lpe_version_a_daily_timetable_result",
        "lpe_version_a_main_timetable_status",
        "lpe_version_a_next_day_input_result",
        "lpe_version_a_next_day_inputs",
        "lpe_version_a_reflection_adaptation_result",
        "lpe_version_a_reflection_adaptations",
    ]
    # Compatibility aliases from earlier local builds.
    alias_keys = [
        "personal_profile",
        "life_profile",
        "daily_context",
        "rule_bank_result",
        "daily_timetable_result",
        "next_day_input_result",
        "reflection_adaptation_result",
    ]

    session_payload = {}
    for key in known_keys + alias_keys:
        try:
            if key in st.session_state:
                session_payload[key] = st.session_state.get(key)
        except Exception:
            pass

    bundle = {
        "schema_version": "lpe_version_a_phase8_session_bundle_v1",
        "created_at_local": _lpe_phase8_datetime.now().isoformat(timespec="seconds"),
        "scope": "local_manual_json_export_import_only_no_database_no_cloud_no_login_no_external_api",
        "hard_bans": [
            "no_login",
            "no_database",
            "no_remote_sync",
            "no_external_api",
            "no_external_ai",
            "no_multi_user",
            "no_commit_push_deploy_from_app",
        ],
        "version_a_state": {
            "profile": _lpe_phase8_safe_get_session_value("lpe_version_a_personal_profile") or _lpe_phase8_safe_get_session_value("personal_profile") or _lpe_phase8_safe_get_session_value("life_profile"),
            "daily_context": _lpe_phase8_safe_get_session_value("lpe_version_a_daily_context") or _lpe_phase8_safe_get_session_value("daily_context"),
            "daily_contexts": _lpe_phase8_safe_get_session_value("daily_contexts", []),
            "rule_bank_result": _lpe_phase8_safe_get_session_value("lpe_version_a_rule_bank_result") or _lpe_phase8_safe_get_session_value("rule_bank_result"),
            "daily_timetable_result": _lpe_phase8_safe_get_session_value("lpe_version_a_daily_timetable_result") or _lpe_phase8_safe_get_session_value("daily_timetable_result"),
            "main_timetable_status": _lpe_phase8_safe_get_session_value("lpe_version_a_main_timetable_status"),
            "next_day_input_result": _lpe_phase8_safe_get_session_value("lpe_version_a_next_day_input_result") or _lpe_phase8_safe_get_session_value("next_day_input_result"),
            "next_day_inputs": _lpe_phase8_safe_get_session_value("lpe_version_a_next_day_inputs", []),
            "reflection_adaptation_result": _lpe_phase8_safe_get_session_value("lpe_version_a_reflection_adaptation_result") or _lpe_phase8_safe_get_session_value("reflection_adaptation_result"),
            "reflection_adaptations": _lpe_phase8_safe_get_session_value("lpe_version_a_reflection_adaptations", []),
        },
        "raw_session_payload": session_payload,
    }
    # Ensure serializable for download; fallback to string for odd local objects.
    _lpe_phase8_json.dumps(bundle, ensure_ascii=False, default=str)
    return bundle


def _lpe_phase8_restore_bundle(bundle):
    """Restore known Version A state keys from manual JSON bundle into Streamlit session."""
    restored = []
    warnings = []
    if not isinstance(bundle, dict):
        return restored, ["ไฟล์ JSON ไม่ใช่ object"]

    state = bundle.get("version_a_state") if isinstance(bundle.get("version_a_state"), dict) else {}
    raw = bundle.get("raw_session_payload") if isinstance(bundle.get("raw_session_payload"), dict) else {}

    def restore(key, value):
        if value is not None:
            st.session_state[key] = value
            restored.append(key)

    # First restore normalized Phase 8 bundle.
    profile_value = _lpe_phase8_extract_profile_from_payload(state, raw, bundle)
    if profile_value is not None:
        restore("lpe_version_a_personal_profile_v1", profile_value)
        restore("lpe_version_a_personal_profile", profile_value)
        restore("personal_profile", profile_value)
    restore("lpe_version_a_daily_context", state.get("daily_context"))
    restore("daily_contexts", state.get("daily_contexts"))
    restore("lpe_version_a_rule_bank_result", state.get("rule_bank_result"))
    restore("lpe_version_a_daily_timetable_result", state.get("daily_timetable_result"))
    restore("lpe_version_a_main_timetable_status", state.get("main_timetable_status"))
    restore("lpe_version_a_next_day_input_result", state.get("next_day_input_result"))
    restore("lpe_version_a_next_day_inputs", state.get("next_day_inputs"))
    restore("lpe_version_a_reflection_adaptation_result", state.get("reflection_adaptation_result"))
    restore("lpe_version_a_reflection_adaptations", state.get("reflection_adaptations"))

    # Then restore exact raw known keys if present.
    allowed_raw_keys = [
        "lpe_version_a_personal_profile",
        "lpe_version_a_daily_context",
        "daily_contexts",
        "lpe_version_a_rule_bank_result",
        "lpe_version_a_daily_timetable_result",
        "lpe_version_a_main_timetable_status",
        "lpe_version_a_next_day_input_result",
        "lpe_version_a_next_day_inputs",
        "lpe_version_a_reflection_adaptation_result",
        "lpe_version_a_reflection_adaptations",
    ]
    for key in allowed_raw_keys:
        if key in raw and raw.get(key) is not None:
            st.session_state[key] = raw.get(key)
            if key not in restored:
                restored.append(key)

    # Compatibility: if user imports the Phase 1 personal profile JSON directly.
    if not restored and bundle.get("schema_version") == "version_a_personal_dashboard_schema_v1":
        st.session_state["lpe_version_a_personal_profile_v1"] = bundle
        st.session_state["lpe_version_a_personal_profile"] = bundle
        st.session_state["personal_profile"] = bundle
        restored.extend(["lpe_version_a_personal_profile_v1", "lpe_version_a_personal_profile", "personal_profile"])
        warnings.append("นำเข้าเป็น personal profile JSON โดยตรง ไม่ใช่ full session bundle")

    if not restored:
        warnings.append("ไม่พบ Version A session keys ที่ restore ได้")
    return restored, warnings


def render_lpe_version_a_phase8_json_persistence():
    """Render local/manual JSON export-import controls. No database/cloud/login/API."""
    import json as _lpe_phase8_json
    from datetime import datetime as _lpe_phase8_datetime

    st.divider()
    st.header("💾 Phase 8 — Local JSON Persistence")
    st.caption("บันทึก/กู้คืน session ด้วยไฟล์ JSON แบบ manual เท่านั้น — ไม่ใช้ database, cloud, login หรือ external API")
    profile = _lpe_phase8_get_profile_for_export()
    daily_context = _lpe_phase8_safe_get_session_value("lpe_version_a_daily_context") or _lpe_phase8_safe_get_session_value("daily_context")
    rule_bank = _lpe_phase8_safe_get_session_value("lpe_version_a_rule_bank_result") or _lpe_phase8_safe_get_session_value("rule_bank_result")
    timetable = _lpe_phase8_safe_get_session_value("lpe_version_a_daily_timetable_result") or _lpe_phase8_safe_get_session_value("daily_timetable_result")
    next_day = _lpe_phase8_safe_get_session_value("lpe_version_a_next_day_input_result") or _lpe_phase8_safe_get_session_value("next_day_input_result")
    adaptation = _lpe_phase8_safe_get_session_value("lpe_version_a_reflection_adaptation_result") or _lpe_phase8_safe_get_session_value("reflection_adaptation_result")

    cols = st.columns(6)
    labels = [
        ("Profile", profile),
        ("Phase 2 วันนี้", daily_context),
        ("Rule Bank", rule_bank),
        ("Timetable", timetable),
        ("Next-Day Input", next_day),
        ("Adaptation", adaptation),
    ]
    for col, (name, value) in zip(cols, labels):
        with col:
            st.caption(name)
            st.subheader(_lpe_phase8_compact_status(value))

    if _lpe_phase8_compact_status(profile) != "พร้อม":
        st.warning("ยังไม่พบ profile ใน session: import personal profile JSON หรือ full session bundle ก่อนใช้งานรอบถัดไปให้แม่น")
    if _lpe_phase8_compact_status(daily_context) != "พร้อม":
        st.warning("ยังไม่พบ Phase 2 daily context ใน session: ตาราง/กฎอาจใช้ fallback")

    st.subheader("Export session เป็น JSON")
    bundle = _lpe_phase8_collect_bundle()
    export_text = _lpe_phase8_json.dumps(bundle, ensure_ascii=False, indent=2, default=str)
    filename = "lpe_version_a_session_bundle_" + _lpe_phase8_datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
    st.download_button(
        "ดาวน์โหลด JSON session bundle",
        data=export_text.encode("utf-8"),
        file_name=filename,
        mime="application/json",
        key="lpe_version_a_phase8_download_session_bundle",
    )
    with st.expander("ดูตัวอย่าง JSON ที่จะ export"):
        st.code(export_text[:6000], language="json")

    st.subheader("Import / Restore session จาก JSON")
    uploaded = st.file_uploader(
        "เลือกไฟล์ JSON ที่ export จาก Phase 8 หรือ personal profile JSON",
        type=["json"],
        key="lpe_version_a_phase8_restore_json_uploader",
    )
    if uploaded is not None:
        try:
            raw_text = uploaded.getvalue().decode("utf-8")
            incoming = _lpe_phase8_json.loads(raw_text)
            restored, warnings = _lpe_phase8_restore_bundle(incoming)
            if restored:
                st.success("Restore session สำเร็จ: " + ", ".join(restored))
            for warning in warnings:
                st.warning(warning)
            st.info("หลัง restore ให้เลื่อนดู Phase 3–7 อีกครั้ง หรือกด rerun/เปลี่ยนเมนูเพื่อให้ผลคำนวณอ่าน session ใหม่")
        except Exception as exc:
            st.error(f"Import JSON ไม่สำเร็จ: {exc}")

    st.caption("Phase 8 local/manual JSON only: ไม่มี database, remote sync, login, external API, AI provider หรือ background storage service")


try:
    render_lpe_version_a_phase8_json_persistence()
except Exception as _lpe_phase8_exc:
    try:
        st.error(f"Phase 8 JSON Persistence error: {_lpe_phase8_exc}")
    except Exception:
        pass

# PHASE10D_VISUAL_POLISH_COPY_PATCH_COUNT=4

# --- PHASE10K_MONTHLY_ROSTER_AND_SHIFT_CHAIN_RESOLVER_PATCH_V1 BEGIN ---
# LPE10K_JUNE_2026_ROSTER_MAP
# LPE10K_SHIFT_CHAIN_RESOLVER
# LPE10K_PLANNING_MODE_RESOLVER
# LPE10K_ROSTER_CHAIN_REPORT
# LPE10K_NO_OCR_MANUAL_MAP
try:
    import datetime as _lpe10k_datetime
    import streamlit as _lpe10k_st
except Exception:
    _lpe10k_datetime = None
    _lpe10k_st = None

PHASE10K_MONTHLY_ROSTER_AND_SHIFT_CHAIN_RESOLVER_PATCH_V1 = True

LPE10K_SHIFT_WINDOWS = {
    "M": "08:00-16:00",
    "A": "16:00-00:00",
    "N": "00:00-08:00",
    "N_A": "00:00-08:00 + 16:00-00:00",
    "O": "หยุด",
    "V": "ลา",
}

LPE10K_JUNE_2026_ROSTER_RAW = {
    "2026-06-01": "ช",
    "2026-06-02": "ด/บ",
    "2026-06-03": "ช",
    "2026-06-04": "ด*",
    "2026-06-05": "ด*",
    "2026-06-06": "O",
    "2026-06-07": "ช",
    "2026-06-08": "ด",
    "2026-06-09": "ด*",
    "2026-06-10": "O",
    "2026-06-11": "บ",
    "2026-06-12": "ช",
    "2026-06-13": "ด",
    "2026-06-14": "ช",
    "2026-06-15": "ด",
    "2026-06-16": "O",
    "2026-06-17": "O",
    "2026-06-18": "V",
    "2026-06-19": "V",
    "2026-06-20": "ช*",
    "2026-06-21": "ด",
    "2026-06-22": "ช*",
    "2026-06-23": "ด",
    "2026-06-24": "ด",
    "2026-06-25": "บ",
    "2026-06-26": "O",
    "2026-06-27": "บ",
    "2026-06-28": "ช",
    "2026-06-29": "ด",
    "2026-06-30": "ด",
}


def lpe10k_normalize_shift(raw_shift):
    raw = "" if raw_shift is None else str(raw_shift).strip()
    star_note = "*" in raw
    clean = raw.replace("*", "").replace(" ", "").strip()
    if clean in {"ช", "M", "m", "เช้า"}:
        code = "M"
    elif clean in {"บ", "A", "a", "บ่าย"}:
        code = "A"
    elif clean in {"ด", "N", "n", "ดึก"}:
        code = "N"
    elif clean in {"ด/บ", "ดบ", "N/A", "N_A", "n_a"}:
        code = "N_A"
    elif clean.upper() == "O" or clean in {"หยุด", "OFF", "off"}:
        code = "O"
    elif clean.upper() == "V" or clean in {"ลา"}:
        code = "V"
    else:
        code = "UNKNOWN"
    return {
        "raw_shift": raw,
        "normalized_shift": code,
        "star_note": star_note,
        "planning_effect": "none" if star_note else "standard",
    }


def lpe10k_first_work_shift(code):
    if code == "N_A":
        return "N"
    if code in {"M", "A", "N"}:
        return code
    return code


def lpe10k_last_work_shift(code):
    if code == "N_A":
        return "A"
    if code in {"M", "A", "N"}:
        return code
    return code


def lpe10k_chain_between(left_code, right_code):
    if not left_code or not right_code or left_code == "UNKNOWN" or right_code == "UNKNOWN":
        return "UNKNOWN_CHAIN"
    left = lpe10k_last_work_shift(left_code)
    right = lpe10k_first_work_shift(right_code)
    if left in {"O", "V"} and right in {"M", "A", "N"}:
        return f"O_TO_{right}"
    if left == "N" and right in {"O", "V"}:
        return "N_TO_O"
    if left in {"M", "A", "N"} and right in {"M", "A", "N"}:
        return f"{left}_TO_{right}"
    if left in {"O", "V"} and right in {"O", "V"}:
        return "REST_TO_REST"
    return f"{left}_TO_{right}"


def lpe10k_planning_mode(today_code, prev_chain, next_chain):
    if today_code == "N_A":
        return "DOUBLE_SHIFT_SURVIVAL_DAY"
    if prev_chain == "A_TO_M" and next_chain == "M_TO_N":
        return "HIGH_SLEEP_RISK_DAY"
    if next_chain == "M_TO_N":
        return "PRE_NIGHT_PROTECTION_DAY"
    if prev_chain == "A_TO_M":
        return "AFTERNOON_TO_MORNING_SLEEP_RISK_DAY"
    if prev_chain == "N_TO_A":
        return "NIGHT_TO_AFTERNOON_SURVIVAL_DAY"
    if prev_chain == "N_TO_O":
        return "POST_NIGHT_RECOVERY_DAY"
    if today_code == "M":
        return "NORMAL_MORNING_DAY"
    if today_code == "A":
        return "NORMAL_AFTERNOON_DAY"
    if today_code == "N":
        return "NORMAL_NIGHT_DAY"
    if today_code == "O":
        return "OFF_STUDY_DAY"
    if today_code == "V":
        return "VAC_STUDY_DAY"
    return "REVIEW_REQUIRED_DAY"


def lpe10k_mode_guidance(planning_mode):
    guidance = {
        "DOUBLE_SHIFT_SURVIVAL_DAY": "เวรซ้อนในวันเดียว: เวร + นอน + กิน + ทวนสั้นเท่านั้น",
        "HIGH_SLEEP_RISK_DAY": "มีแรงกดจากเวรก่อนและเวรถัดไป: ลดงานยาวและกันเวลานอน",
        "PRE_NIGHT_PROTECTION_DAY": "วันนี้ต้องกันช่วงเย็นเพื่อเตรียมนอนก่อนเวรดึก",
        "AFTERNOON_TO_MORNING_SLEEP_RISK_DAY": "ระวังนอนน้อยจากบ่ายต่อเช้า",
        "NIGHT_TO_AFTERNOON_SURVIVAL_DAY": "ลงดึกแล้วต่อบ่าย: กันเวลานอนช่วงกลางวัน",
        "POST_NIGHT_RECOVERY_DAY": "ลงดึกแล้วพัก: ใช้เพื่อฟื้นตัวและงานเบา",
        "NORMAL_MORNING_DAY": "เวรเช้าปกติ: เลือกงานหลัก 1 อย่างหลังเวรตามพลังงาน",
        "NORMAL_AFTERNOON_DAY": "เวรบ่ายปกติ: ใช้ช่วงเช้าทำงาน/อ่านที่สำคัญ",
        "NORMAL_NIGHT_DAY": "เวรดึกปกติ: กันเวลาพักก่อนขึ้นเวร",
        "OFF_STUDY_DAY": "วันหยุด: ใช้เป็นวันอ่าน/ชดเชย/งานบ้านแบบไม่บวม",
        "VAC_STUDY_DAY": "วันลา: ใช้เป็นวันฟื้นตัวหรืออ่านหลักตามเป้าหมาย",
    }
    return guidance.get(planning_mode, "ต้องตรวจตารางเวรด้วยตนเอง")


def lpe10k_resolve_roster_day(date_key, roster=None):
    roster = roster or LPE10K_JUNE_2026_ROSTER_RAW
    keys = sorted(roster.keys())
    if date_key not in roster:
        return {
            "date": date_key,
            "raw_shift": "",
            "normalized_shift": "UNKNOWN",
            "prev_chain": "UNKNOWN_CHAIN",
            "next_chain": "UNKNOWN_CHAIN",
            "planning_mode": "REVIEW_REQUIRED_DAY",
            "guidance": "ไม่พบวันที่ใน roster map",
        }
    idx = keys.index(date_key)
    today = lpe10k_normalize_shift(roster.get(date_key))
    prev_code = lpe10k_normalize_shift(roster.get(keys[idx - 1]))["normalized_shift"] if idx > 0 else None
    next_code = lpe10k_normalize_shift(roster.get(keys[idx + 1]))["normalized_shift"] if idx < len(keys) - 1 else None
    today_code = today["normalized_shift"]
    prev_chain = lpe10k_chain_between(prev_code, today_code) if prev_code else "MONTH_START"
    next_chain = lpe10k_chain_between(today_code, next_code) if next_code else "MONTH_END"
    mode = lpe10k_planning_mode(today_code, prev_chain, next_chain)
    return {
        "date": date_key,
        "raw_shift": today["raw_shift"],
        "normalized_shift": today_code,
        "star_note": today["star_note"],
        "prev_shift": prev_code or "",
        "next_shift": next_code or "",
        "prev_chain": prev_chain,
        "next_chain": next_chain,
        "planning_mode": mode,
        "guidance": lpe10k_mode_guidance(mode),
    }


def lpe10k_resolve_month(roster=None):
    roster = roster or LPE10K_JUNE_2026_ROSTER_RAW
    return [lpe10k_resolve_roster_day(date_key, roster) for date_key in sorted(roster.keys())]


def lpe10k_render_roster_chain_report():
    if _lpe10k_st is None:
        return
    rows = lpe10k_resolve_month()
    with _lpe10k_st.expander("🧭 รายงานตารางเวรและรหัสวัน Phase10K", expanded=False):
        _lpe10k_st.caption("manual roster map เดือน มิ.ย.69: * ไม่มีผลต่อ planning, ด/บ คือดึกและบ่ายในวันเดียว")
        date_keys = [row["date"] for row in rows]
        default_index = 0
        if _lpe10k_datetime is not None:
            today_key = _lpe10k_datetime.date.today().isoformat()
            if today_key in date_keys:
                default_index = date_keys.index(today_key)
        selected = _lpe10k_st.selectbox("เลือกวันที่เพื่อตรวจรหัสเวร", date_keys, index=default_index, key="phase10k_selected_roster_date")
        selected_row = lpe10k_resolve_roster_day(selected)
        c1, c2, c3, c4 = _lpe10k_st.columns(4)
        c1.metric("เวรดิบ", selected_row["raw_shift"])
        c2.metric("รหัสวันนี้", selected_row["normalized_shift"])
        c3.metric("ก่อนหน้า", selected_row["prev_chain"])
        c4.metric("ถัดไป", selected_row["next_chain"])
        _lpe10k_st.info(f"โหมดวันนี้: {selected_row['planning_mode']} — {selected_row['guidance']}")
        report_rows = [
            {
                "วันที่": row["date"],
                "เวรดิบ": row["raw_shift"],
                "รหัส": row["normalized_shift"],
                "ก่อนหน้า": row["prev_chain"],
                "ถัดไป": row["next_chain"],
                "โหมด": row["planning_mode"],
            }
            for row in rows
        ]
        _lpe10k_st.dataframe(report_rows, use_container_width=True, hide_index=True)

try:
    lpe10k_render_roster_chain_report()
except Exception as _lpe10k_error:
    if _lpe10k_st is not None:
        _lpe10k_st.warning(f"Phase10K roster report ยังแสดงผลไม่ได้: {_lpe10k_error}")
# --- PHASE10K_MONTHLY_ROSTER_AND_SHIFT_CHAIN_RESOLVER_PATCH_V1 END ---

# BEGIN LPE_PHASE11A_PROFILE_PERSISTENCE_AUTOSAVE_CALL_V1
try:
    _lpe11a_profile_persistence_autosave_session()
except Exception:
    pass
# END LPE_PHASE11A_PROFILE_PERSISTENCE_AUTOSAVE_CALL_V1

