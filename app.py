
from __future__ import annotations

import csv
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import streamlit as st


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

    return {
        "nickname": clean_public_text(
            user_profile.get("nickname") or user_profile.get("name"), "คุณ"
        ),
        "plan_date": date.today(),
        "start_mode": "วันพลังพร้อม",
        "subject": clean_public_text(
            first_exam.get("subject") or first_exam.get("วิชา"), "วิชาหลักของคุณ"
        ),
        "exam_date": exam_date,
        "study_minutes": int(float(first_exam.get("target_minutes") or first_exam.get("minutes") or 60)),
        "health_goal": clean_public_text(
            health_goal.get("goal") or health_goal.get("name"), "ขยับเบา ๆ หรือพักให้พอ"
        ),
        "project_name": clean_public_text(
            first_project.get("name") or first_project.get("project"),
            "โปรเจกต์ส่วนตัวของคุณ",
        ),
        "garden_task": clean_public_text(
            first_garden.get("task")
            or first_garden.get("activity")
            or first_garden.get("work_item"),
            "งานบ้านหรือสวนที่อยากไม่ลืม",
        ),
        "shift": thai_shift(first_shift.get("shift") or first_shift.get("type")),
        "calorie_note": health_goal.get("calorie_target") or health_goal.get("calories") or "",
    }


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


def navigate_to(destination: str) -> None:
    st.session_state.lpe_nav = destination
    st.session_state.lpe_nav_mobile = DESTINATION_TO_PRIMARY_NAV.get(
        destination, "••• เพิ่มเติม"
    )
    if destination in DESKTOP_NAV_ITEMS:
        st.session_state.lpe_nav_sidebar = destination


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


def render_nav() -> str:
    st.markdown(
        '<div class="mobile-nav-note">เลือกสิ่งที่ต้องการทำ แล้วระบบจะแสดงเฉพาะส่วนนั้น</div>',
        unsafe_allow_html=True,
    )
    st.selectbox(
        "เมนูหลัก",
        PRIMARY_NAV_ITEMS,
        key="lpe_nav_mobile",
        on_change=sync_mobile_navigation,
    )

    with st.sidebar:
        st.markdown("### 🎯 ผู้ช่วยจัดลำดับชีวิต")
        st.caption("เมนูด้านข้างเป็นตัวช่วยสำหรับจอใหญ่")
        st.selectbox(
            "มุมมองสำหรับจอใหญ่",
            DESKTOP_NAV_ITEMS,
            key="lpe_nav_sidebar",
            on_change=sync_sidebar_navigation,
        )
        st.divider()
        st.markdown("### ความพร้อมวันนี้")
        st.date_input("วันที่วางแผน", key="sidebar_plan_date", value=parse_date(st.session_state.lpe_profile.get("plan_date")))
        st.selectbox("ระดับพลังเริ่มต้น", ["วันพลังพร้อม", "วันพลังจำกัด", "วันพักฟื้น"], key="sidebar_mode", index=["วันพลังพร้อม", "วันพลังจำกัด", "วันพักฟื้น"].index(mode_label(st.session_state.lpe_profile.get("start_mode", "วันพลังพร้อม"))))
        if st.button("ใช้ค่านี้กับวันนี้", use_container_width=True):
            st.session_state.lpe_profile["plan_date"] = st.session_state.sidebar_plan_date
            st.session_state.lpe_profile["start_mode"] = st.session_state.sidebar_mode
            st.rerun()
    return st.session_state.lpe_nav


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
    st.button("← กลับไปเพิ่มเติม", on_click=navigate_to, args=("เพิ่มเติม",), key="settings_back")
    render_hero("ตั้งค่าชีวิต", "ดูข้อมูลที่ใช้สร้างแผน และกลับไปแก้ทีละขั้นได้", "⚙️")
    render_demo_warning()
    render_demo_about()
    profile = st.session_state.lpe_profile
    st.markdown(
        f"""
        <div class="card">
            <div class="card-label">เป้าหมายหลัก</div>
            <div class="card-value">{profile.get('subject', 'วิชาหลักของคุณ')}</div>
            <div class="card-label">เดดไลน์ {parse_date(profile.get('exam_date')):%d/%m/%Y} · {mode_label(profile.get('start_mode', 'วันพลังพร้อม'))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.button(
        "แก้ข้อมูลเริ่มต้น",
        use_container_width=True,
        on_click=navigate_to,
        args=("เริ่มต้นใช้งาน",),
    )
    payload = json.dumps(
        {
            "profile": {k: str(v) for k, v in profile.items()},
            "review": st.session_state.lpe_review,
            "summary": st.session_state.lpe_saved_summary,
        },
        ensure_ascii=False,
        indent=2,
    )
    with st.expander("จัดการข้อมูลทดลอง", expanded=False):
        st.download_button(
            "ดาวน์โหลดสำเนาข้อมูลทดลอง",
            payload,
            "life_priority_engine_demo.json",
            "application/json",
        )
        if st.button("ล้างข้อมูลชั่วคราว", type="secondary"):
            for key in ["lpe_profile", "lpe_review", "lpe_saved_summary"]:
                st.session_state.pop(key, None)
            st.rerun()


def main() -> None:
    inject_styles()
    init_state()
    nav = render_nav()

    if nav == "เริ่มต้นใช้งาน":
        page_onboarding()
    elif nav == "แผนพรุ่งนี้":
        page_tomorrow()
    elif nav == "แผนละเอียดรายวัน":
        page_daily_detail()
    elif nav == "เพิ่มเติม":
        page_more()
    elif nav == "ภาพรวม 30 วัน":
        page_30day()
    elif nav == "ตั้งค่าชีวิต":
        page_settings()
    else:
        page_today()

    st.divider()
    st.caption("เวอร์ชันทดลองสำหรับวางแผนทั่วไป · ข้อมูลอาจหายเมื่อรีเฟรช")


if __name__ == "__main__":
    main()

# === LPE_V1_10B_1_MOBILE_USABILITY_RESCUE_FIXED_START ===
# UI-only readability patch. No login, database, API, deployment, git push, or core scoring rewrite.
try:
    import streamlit as st

    def _lpe_v110b1_readability_patch():
        st.markdown('\n<style id="lpe-v110b1-readability-patch">\n:root {\n  --lpe-navy: #203254;\n  --lpe-navy-dark: #17243f;\n  --lpe-ink: #111827;\n  --lpe-muted: #374151;\n  --lpe-border: #d7deea;\n  --lpe-active: #ff4b5c;\n  --lpe-cream: #fffaf0;\n}\n\nhtml, body, [data-testid="stAppViewContainer"], .main, .block-container {\n  color: var(--lpe-ink) !important;\n}\np, span, div, label, li, small {\n  opacity: 1 !important;\n}\nh1, h2, h3, h4, h5, h6 {\n  color: var(--lpe-ink) !important;\n}\n\n.lpe-hero, .hero, .header-card, .title-card,\ndiv[class*="hero"], div[class*="Header"], div[class*="header"] {\n  color: #ffffff !important;\n}\n.lpe-hero *, .hero *, .header-card *, .title-card *,\ndiv[class*="hero"] *, div[class*="Header"] *, div[class*="header"] * {\n  color: #ffffff !important;\n  opacity: 1 !important;\n}\n\nsection[data-testid="stSidebar"] {\n  background: var(--lpe-navy) !important;\n  color: #ffffff !important;\n}\nsection[data-testid="stSidebar"] * {\n  opacity: 1 !important;\n}\nsection[data-testid="stSidebar"] h1,\nsection[data-testid="stSidebar"] h2,\nsection[data-testid="stSidebar"] h3,\nsection[data-testid="stSidebar"] p,\nsection[data-testid="stSidebar"] span,\nsection[data-testid="stSidebar"] label,\nsection[data-testid="stSidebar"] small {\n  color: #ffffff !important;\n  opacity: 1 !important;\n}\n\n/* Sidebar radio pills */\nsection[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label {\n  min-height: 42px !important;\n  border-radius: 999px !important;\n  padding: 8px 12px !important;\n  background: #ffffff !important;\n  border: 1px solid var(--lpe-border) !important;\n  color: var(--lpe-ink) !important;\n  display: flex !important;\n  align-items: center !important;\n}\nsection[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label * {\n  color: var(--lpe-ink) !important;\n  opacity: 1 !important;\n  visibility: visible !important;\n}\nsection[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {\n  border: 2px solid var(--lpe-active) !important;\n}\n\n/* Top navigation radio pills */\n[data-testid="stRadio"] div[role="radiogroup"] {\n  display: flex !important;\n  flex-wrap: wrap !important;\n  gap: 8px !important;\n  align-items: center !important;\n}\n[data-testid="stRadio"] div[role="radiogroup"] label {\n  min-height: 42px !important;\n  border-radius: 999px !important;\n  padding: 8px 14px !important;\n  background: #ffffff !important;\n  border: 1px solid var(--lpe-border) !important;\n  color: var(--lpe-ink) !important;\n  opacity: 1 !important;\n  box-shadow: 0 1px 2px rgba(17, 24, 39, 0.06) !important;\n}\n[data-testid="stRadio"] div[role="radiogroup"] label *,\n[data-testid="stRadio"] div[role="radiogroup"] label p,\n[data-testid="stRadio"] div[role="radiogroup"] label span,\n[data-testid="stRadio"] div[role="radiogroup"] label div {\n  color: var(--lpe-ink) !important;\n  opacity: 1 !important;\n  visibility: visible !important;\n}\n[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {\n  background: var(--lpe-navy) !important;\n  border-color: var(--lpe-navy) !important;\n}\n[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) *,\n[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p,\n[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) span {\n  color: #ffffff !important;\n}\n\n/* Form labels and input contrast */\n[data-testid="stTextInput"] label,\n[data-testid="stTextArea"] label,\n[data-testid="stSelectbox"] label,\n[data-testid="stNumberInput"] label,\n[data-testid="stDateInput"] label,\n[data-testid="stSlider"] label,\n[data-testid="stMultiSelect"] label,\nlabel {\n  color: var(--lpe-ink) !important;\n  font-weight: 800 !important;\n  opacity: 1 !important;\n}\n[data-testid="stTextInput"] input,\n[data-testid="stTextArea"] textarea,\n[data-testid="stNumberInput"] input,\n[data-testid="stDateInput"] input,\n[data-baseweb="select"] * {\n  opacity: 1 !important;\n}\n\n/* Warning/readability */\n[data-testid="stAlert"] {\n  background: #fff7e6 !important;\n  border: 1px solid #f2be5c !important;\n  border-radius: 14px !important;\n}\n[data-testid="stAlert"] *,\n[data-testid="stAlert"] p,\n[data-testid="stAlert"] span {\n  color: #6b3f00 !important;\n  opacity: 1 !important;\n  font-weight: 700 !important;\n}\n\n/* Mobile rescue */\n@media (max-width: 820px) {\n  section[data-testid="stSidebar"] {\n    display: none !important;\n  }\n  [data-testid="stAppViewContainer"] {\n    margin-left: 0 !important;\n  }\n  .block-container {\n    padding-left: 1rem !important;\n    padding-right: 1rem !important;\n    max-width: 100% !important;\n  }\n  [data-testid="stRadio"] div[role="radiogroup"] {\n    flex-wrap: nowrap !important;\n    overflow-x: auto !important;\n    padding-bottom: 6px !important;\n    scrollbar-width: thin !important;\n  }\n  [data-testid="stRadio"] div[role="radiogroup"] label {\n    flex: 0 0 auto !important;\n    min-width: max-content !important;\n    max-width: 80vw !important;\n    white-space: nowrap !important;\n  }\n  [data-testid="column"] {\n    min-width: 100% !important;\n  }\n  h1 {\n    font-size: 2rem !important;\n    line-height: 1.2 !important;\n  }\n}\n</style>\n', unsafe_allow_html=True)

    _lpe_v110b1_readability_patch()
except Exception:
    pass
# === LPE_V1_10B_1_MOBILE_USABILITY_RESCUE_FIXED_END ===
