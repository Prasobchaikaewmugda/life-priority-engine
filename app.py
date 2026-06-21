
from __future__ import annotations

import csv
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import streamlit as st


APP_URL = "https://life-priority-engine.streamlit.app"
DATA_DIR = Path("data")

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
            background: #eef7ff;
            border: 1px solid #c9e7ff;
            border-radius: 14px;
            padding: 12px 14px;
            color: #20415f;
            margin-bottom: 14px;
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
        .mission-card.could { border-left-color: #3b6eea; }
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
        .badge.could { background: #e8efff; color: #244fba; }
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
            padding: 7px 10px;
            min-height: 36px;
        }
        button[kind="primary"], .stButton > button {
            border-radius: 14px !important;
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


def seed_profile() -> dict[str, Any]:
    user_profile = read_json(DATA_DIR / "user_profile.json", {})
    health_goal = read_json(DATA_DIR / "health_goal.json", {})
    projects = read_json(DATA_DIR / "project_list.json", [])
    exams = read_csv(DATA_DIR / "exam_plan.csv")
    shifts = read_csv(DATA_DIR / "shift_schedule.csv")
    garden = read_csv(DATA_DIR / "garden_plan.csv")

    first_exam = exams[0] if exams else {}
    first_project = projects[0] if isinstance(projects, list) and projects else {}
    first_shift = shifts[0] if shifts else {}
    first_garden = garden[0] if garden else {}

    exam_date = parse_date(
        first_exam.get("exam_date") or first_exam.get("date") or first_exam.get("วันสอบ"),
        date.today() + timedelta(days=24),
    )

    return {
        "nickname": user_profile.get("nickname") or user_profile.get("name") or "ผู้ใช้ทดลอง",
        "plan_date": date.today(),
        "start_mode": "วันพลังพร้อม",
        "subject": first_exam.get("subject") or first_exam.get("วิชา") or "วิชาตัวอย่าง A",
        "exam_date": exam_date,
        "study_minutes": int(float(first_exam.get("target_minutes") or first_exam.get("minutes") or 60)),
        "health_goal": health_goal.get("goal") or health_goal.get("name") or "ขยับเบา ๆ หรือพักฟื้น",
        "project_name": first_project.get("name") or first_project.get("project") or "โปรเจกต์ส่วนตัวตัวอย่าง",
        "garden_task": first_garden.get("task") or first_garden.get("activity") or "ตรวจจุดพื้นที่สวนตัวอย่าง",
        "shift": first_shift.get("shift") or first_shift.get("type") or "วันหยุด",
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
        ⚠️ เวอร์ชันทดลองสาธารณะ: ข้อมูลในหน้านี้เก็บเฉพาะใน session ของเบราว์เซอร์ ไม่ควรกรอกข้อมูลส่วนตัวจริง และไม่ใช่คำแนะนำทางการแพทย์/โภชนาการ/การรักษา
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_nav() -> str:
    items = [
        "วันนี้ต้องทำอะไร",
        "เริ่มต้นใช้งาน",
        "แผนพรุ่งนี้",
        "แผนละเอียดรายวัน",
        "ภาพรวม 30 วัน",
        "ตั้งค่าชีวิต",
    ]
    st.markdown(
        '<div class="mobile-nav-note">📱 มือถือใช้เมนูแถวนี้เป็นหลัก ไม่ต้องเปิดแถบด้านข้าง</div>',
        unsafe_allow_html=True,
    )
    current = st.radio("เมนูหลัก", items, horizontal=True, label_visibility="collapsed", key="lpe_nav_radio")
    st.session_state.lpe_nav = current

    with st.sidebar:
        st.markdown("### 🎯 ผู้ช่วยจัดลำดับชีวิต")
        st.caption("เมนูด้านข้างเป็นตัวช่วยสำหรับจอใหญ่")
        st.radio("มุมมอง", items, key="lpe_nav_sidebar", index=items.index(current))
        if st.session_state.lpe_nav_sidebar != current:
            st.session_state.lpe_nav = st.session_state.lpe_nav_sidebar
            current = st.session_state.lpe_nav_sidebar
        st.divider()
        st.markdown("### ความพร้อมวันนี้")
        st.date_input("วันที่วางแผน", key="sidebar_plan_date", value=parse_date(st.session_state.lpe_profile.get("plan_date")))
        st.selectbox("ระดับพลังเริ่มต้น", ["วันพลังพร้อม", "วันพลังจำกัด", "วันพักฟื้น"], key="sidebar_mode", index=["วันพลังพร้อม", "วันพลังจำกัด", "วันพักฟื้น"].index(mode_label(st.session_state.lpe_profile.get("start_mode", "วันพลังพร้อม"))))
        if st.button("ใช้ค่านี้กับวันนี้", use_container_width=True):
            st.session_state.lpe_profile["plan_date"] = st.session_state.sidebar_plan_date
            st.session_state.lpe_profile["start_mode"] = st.session_state.sidebar_mode
            st.rerun()
    return current


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
        st.caption("วันนี้ภารกิจนี้ได้แค่ไหน?")
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
    render_cards(profile, missions)
    render_pills(profile)

    st.markdown('<div class="section-title">🎯 ภารกิจวันนี้</div><div class="section-subtitle">เลือกผลได้ใต้แต่ละภารกิจทันที ข้อมูลไม่เขียนลงไฟล์กลาง</div>', unsafe_allow_html=True)
    st.markdown('<div class="safe-note">⊙ เริ่มจากการ์ดแรก แล้วค่อยดูว่ายังมีพลังพอสำหรับงานถัดไปไหม</div>', unsafe_allow_html=True)

    for i, mission in enumerate(missions, 1):
        render_mission_card(mission, i)

    st.markdown('<div class="danger-note">⊘ วันนี้ยังไม่ควรทำ<br>' + "<br>".join([f"• {x}" for x in avoid]) + "</div>", unsafe_allow_html=True)

    if st.button("บันทึกผลวันนี้ใน session นี้", type="primary", use_container_width=True):
        save_review(missions)
        st.success("บันทึกผลใน session นี้แล้ว — ไม่มีการเขียนทับ CSV กลาง")
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


def page_onboarding() -> None:
    profile = st.session_state.lpe_profile
    render_hero("เริ่มต้นใช้งาน", "กรอกข้อมูลตั้งต้นแบบไม่ต้องสมัครสมาชิก ข้อมูลอยู่เฉพาะ session นี้", "🧭")
    render_demo_warning()

    with st.form("onboarding_form"):
        c1, c2 = st.columns(2)
        with c1:
            nickname = st.text_input("ชื่อเล่น/ชื่อที่อยากให้ระบบเรียก", value=str(profile.get("nickname", "")))
            subject = st.text_input("วิชาหรือเรื่องหลักที่ต้องอ่าน", value=str(profile.get("subject", "")))
            exam_date = st.date_input("วันสอบ/วันสำคัญ", value=parse_date(profile.get("exam_date"), date.today() + timedelta(days=24)))
            study_minutes = st.number_input("เวลาอ่านต่อวันเป้าหมาย", min_value=10, max_value=240, value=int(profile.get("study_minutes", 60)), step=5)
        with c2:
            start_mode = st.selectbox("ระดับพลังวันนี้", ["วันพลังพร้อม", "วันพลังจำกัด", "วันพักฟื้น"], index=["วันพลังพร้อม", "วันพลังจำกัด", "วันพักฟื้น"].index(mode_label(profile.get("start_mode", "วันพลังพร้อม"))))
            shift = st.selectbox("สถานะงาน/เวรวันนี้", ["วันหยุด", "เวรเช้า", "เวรบ่าย", "เวรดึก", "งานหนัก", "ไม่แน่ใจ"], index=0)
            health_goal = st.text_input("เป้าหมายสุขภาพแบบปลอดภัย", value=str(profile.get("health_goal", "")))
            calorie_note = st.text_input("เป้าหมายอาหาร/แคลอรี่ ถ้ามี", value=str(profile.get("calorie_note", "")), placeholder="เช่น กินให้ครบมื้อ / ไม่ต้องใส่ก็ได้")
        project_name = st.text_input("โปรเจกต์ส่วนตัวที่อยากทำเมื่อมีแรงเหลือ", value=str(profile.get("project_name", "")))
        garden_task = st.text_input("งานบ้าน/สวน/ชีวิตประจำวันที่อยากไม่ลืม", value=str(profile.get("garden_task", "")))

        submitted = st.form_submit_button("ใช้ข้อมูลนี้สร้างแผนทดลอง", type="primary", use_container_width=True)

    if submitted:
        st.session_state.lpe_profile.update(
            {
                "nickname": nickname or "ผู้ใช้ทดลอง",
                "subject": subject or "วิชาหลัก",
                "exam_date": exam_date,
                "study_minutes": int(study_minutes),
                "start_mode": start_mode,
                "shift": shift,
                "health_goal": health_goal or "ขยับเบา ๆ หรือพักฟื้น",
                "calorie_note": calorie_note,
                "project_name": project_name or "โปรเจกต์ส่วนตัว",
                "garden_task": garden_task or "งานดูแลชีวิตประจำวัน",
            }
        )
        st.session_state.lpe_saved_summary = None
        st.success("สร้างข้อมูลทดลองใน session นี้แล้ว ไปที่เมนู “วันนี้ต้องทำอะไร” ได้เลย")


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


def page_settings() -> None:
    render_hero("ตั้งค่าชีวิต", "จัดการข้อมูลทดลองของ session นี้ และเข้าใจข้อจำกัดของระบบ", "⚙️")
    render_demo_warning()
    profile = st.session_state.lpe_profile
    st.json(
        {
            "ข้อมูล session ปัจจุบัน": {
                "nickname": profile.get("nickname"),
                "subject": profile.get("subject"),
                "exam_date": str(profile.get("exam_date")),
                "start_mode": profile.get("start_mode"),
                "storage": "session_state only — ไม่เขียน CSV กลาง",
            }
        }
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
    st.download_button("ดาวน์โหลดข้อมูล session เป็น JSON", payload, "life_priority_engine_session_demo.json", "application/json")
    if st.button("ล้างข้อมูล session นี้", type="secondary"):
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
    elif nav == "ภาพรวม 30 วัน":
        page_30day()
    elif nav == "ตั้งค่าชีวิต":
        page_settings()
    else:
        page_today()

    st.divider()
    st.caption("Public demo · session-only storage · no login · no database · not medical/nutrition/treatment advice")


if __name__ == "__main__":
    main()

