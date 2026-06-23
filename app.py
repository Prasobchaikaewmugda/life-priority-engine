
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
        "Step 5.1 ยังเป็น manual export/import: ไม่มี login, database, cloud sync หรือ external API"
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

