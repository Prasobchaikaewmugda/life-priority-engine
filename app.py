import csv
import json
import re
from collections import Counter
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path
from typing import Any

import streamlit as st


DATA_DIR = Path(__file__).resolve().parent / "data"
REQUIRED_DATA_FILES = (
    "user_profile.json",
    "shift_schedule.csv",
    "exam_plan.csv",
    "health_goal.json",
    "project_list.json",
    "garden_plan.csv",
    "decision_rules.json",
    "daily_plan.csv",
    "daily_log.csv",
)
DAILY_LOG_FIELDS = (
    "date",
    "mission_id",
    "status",
    "planned_value",
    "actual_value",
    "unit",
    "reason",
    "energy",
    "workload",
    "symptom",
    "score",
    "note",
    "created_at",
)
DAILY_PLAN_FIELDS = (
    "date",
    "shift",
    "mode",
    "mission_id",
    "mission_title",
    "category",
    "target_value",
    "target_unit",
    "priority",
    "must_should_could",
    "do_not_do_note",
)

DEFAULT_PROFILE = {
    "name": "Local User",
    "study_goal": {"description": "Protect a short study block", "target_minutes_per_day": 45},
    "project_limits": {"max_minutes_per_day": 30},
}
DEFAULT_HEALTH_GOAL = {
    "goal": "Protect energy and recovery",
    "preferred_exercise_types": ["light movement"],
}
DEFAULT_PROJECTS = {"projects": []}
DEFAULT_RULES = {"rules": []}


def load_json_seed(filename: str, fallback: dict[str, Any], issues: list[str]) -> dict[str, Any]:
    path = DATA_DIR / filename
    if not path.is_file():
        issues.append(f"{filename} is missing")
        return fallback

    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            value = json.load(handle)
        if not isinstance(value, dict):
            raise ValueError("top-level JSON value must be an object")
        return value
    except (OSError, ValueError, json.JSONDecodeError):
        issues.append(f"{filename} is unreadable")
        return fallback


def load_csv_seed(filename: str, issues: list[str]) -> list[dict[str, str]]:
    path = DATA_DIR / filename
    if not path.is_file():
        issues.append(f"{filename} is missing")
        return []

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise ValueError("CSV header is missing")
            return list(reader)
    except (OSError, ValueError, csv.Error):
        issues.append(f"{filename} is unreadable")
        return []


def load_seed_data() -> tuple[dict[str, Any], list[str]]:
    issues: list[str] = []
    data = {
        "profile": load_json_seed("user_profile.json", DEFAULT_PROFILE, issues),
        "shifts": load_csv_seed("shift_schedule.csv", issues),
        "exams": load_csv_seed("exam_plan.csv", issues),
        "health": load_json_seed("health_goal.json", DEFAULT_HEALTH_GOAL, issues),
        "projects": load_json_seed("project_list.json", DEFAULT_PROJECTS, issues),
        "garden": load_csv_seed("garden_plan.csv", issues),
        "rules": load_json_seed("decision_rules.json", DEFAULT_RULES, issues),
        "daily_plan": load_csv_seed("daily_plan.csv", issues),
        "daily_log": load_csv_seed("daily_log.csv", issues),
    }
    return data, issues


def ensure_daily_log_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "daily_log.csv"

    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", encoding="utf-8", newline="") as handle:
            csv.writer(handle).writerow(DAILY_LOG_FIELDS)
        return

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        existing_header = next(csv.reader(handle), [])
    if tuple(existing_header) != DAILY_LOG_FIELDS:
        raise ValueError("daily_log.csv has an unexpected header; existing rows were not changed")


def append_daily_log_rows(rows: list[dict[str, str]]) -> None:
    ensure_daily_log_file()
    path = DATA_DIR / "daily_log.csv"
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DAILY_LOG_FIELDS)
        writer.writerows(rows)


def ensure_daily_plan_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "daily_plan.csv"

    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", encoding="utf-8", newline="") as handle:
            csv.writer(handle).writerow(DAILY_PLAN_FIELDS)
        return

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        existing_header = next(csv.reader(handle), [])
    if tuple(existing_header) != DAILY_PLAN_FIELDS:
        raise ValueError("daily_plan.csv has an unexpected header; existing rows were not changed")


def append_daily_plan_rows(rows: list[dict[str, str]]) -> None:
    ensure_daily_plan_file()
    path = DATA_DIR / "daily_plan.csv"
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DAILY_PLAN_FIELDS)
        writer.writerows(rows)


def mission_review_key(selected_date: date, index: int, mission: dict[str, str]) -> str:
    category = "".join(character for character in mission["category"].lower() if character.isalnum())
    return f"{selected_date:%Y%m%d}_{index:02d}_{category or 'mission'}"


def planned_numeric_target(planned_value: str) -> float | None:
    values = re.findall(r"\d+(?:\.\d+)?", planned_value)
    return float(values[-1]) if values else None


def mission_credit(entry: dict[str, Any]) -> float:
    status = entry["status"]
    if status == "DONE":
        return 1.0
    if status == "PARTIAL":
        actual_value = float(entry["actual_value"] or 0)
        planned_target = planned_numeric_target(entry["mission"]["amount"])
        if actual_value <= 0:
            return 0.0
        if planned_target:
            return min(actual_value / planned_target, 1.0)
        return 0.5
    if status == "MISSED":
        return {
            "Higher-priority work": 0.25,
            "Low energy": 0.20,
            "Not enough time": 0.10,
        }.get(entry["missed_reason"], 0.0)
    if status == "PROBLEM":
        return 0.40
    return 0.0


def calculate_daily_review(
    review_entries: list[dict[str, Any]], starting_day_mode: str, workload: str
) -> dict[str, Any]:
    mission_scores = [round(mission_credit(entry) * 100) for entry in review_entries]
    daily_score = round(sum(mission_scores) / len(mission_scores)) if mission_scores else 0

    problem_issues = [
        entry["problem_issue"]
        for entry in review_entries
        if entry["status"] == "PROBLEM" and entry["problem_issue"]
    ]
    problem_notes = [
        entry["problem_note"].lower()
        for entry in review_entries
        if entry["status"] == "PROBLEM" and entry["problem_note"]
    ]
    serious_issues = {
        "Very heavy shift",
        "No sleep",
        "Faint or dizzy",
        "Sick or unwell",
        "Unsafe condition",
    }
    serious_note_terms = ("faint", "dizzy", "sick", "unsafe", "no sleep", "passed out")
    serious_issue = (
        starting_day_mode == "Red Day"
        or any(issue in serious_issues for issue in problem_issues)
        or any(term in note for note in problem_notes for term in serious_note_terms)
    )
    health_relevant = serious_issue or any(
        issue in {"Low energy", "Physical discomfort"} for issue in problem_issues
    )

    has_normal_problem = any(entry["status"] == "PROBLEM" for entry in review_entries)
    has_incomplete_work = any(
        entry["status"] in {"PARTIAL", "MISSED"} for entry in review_entries
    )
    moderate_capacity = (
        starting_day_mode == "Yellow Day"
        or workload.lower() == "high"
        or has_normal_problem
        or has_incomplete_work
    )

    if serious_issue:
        classified_mode = "Red Day"
        interpretation = "A serious capacity or safety signal overrides the completion score."
    elif daily_score >= 80 and not moderate_capacity:
        classified_mode = "Green Day"
        interpretation = "Good completion with no serious issue reported."
    else:
        classified_mode = "Yellow Day"
        interpretation = "Results show partial completion, limited capacity, or a normal blocker; keep expectations realistic."

    if problem_issues:
        main_blocker = Counter(problem_issues).most_common(1)[0][0]
    else:
        missed_reasons = [
            entry["missed_reason"]
            for entry in review_entries
            if entry["status"] == "MISSED" and entry["missed_reason"]
        ]
        if missed_reasons:
            main_blocker = Counter(missed_reasons).most_common(1)[0][0]
        elif has_incomplete_work:
            main_blocker = "Partial completion"
        else:
            main_blocker = "No major blocker reported"

    health_caution = ""
    if classified_mode == "Red Day":
        health_caution = (
            "Health caution: reduce demands and avoid strenuous activity. "
            "If symptoms are severe, recurring, or you feel unsafe, seek appropriate professional help."
        )
    elif health_relevant:
        health_caution = (
            "Health caution: keep demands light and reassess capacity. "
            "Seek appropriate professional help if symptoms are severe or recurring."
        )

    return {
        "mission_scores": mission_scores,
        "daily_score": daily_score,
        "day_mode": classified_mode,
        "main_blocker": main_blocker,
        "interpretation": interpretation,
        "health_caution": health_caution,
    }


def generate_tomorrow_plan(
    seed_data: dict[str, Any],
    selected_date: date,
    review_entries: list[dict[str, Any]],
    review_result: dict[str, Any],
    mission_context: dict[str, str],
) -> dict[str, Any]:
    tomorrow_date = selected_date + timedelta(days=1)
    problem_issues = {
        entry["problem_issue"]
        for entry in review_entries
        if entry["status"] == "PROBLEM" and entry["problem_issue"]
    }
    health_issues = {
        "Low energy",
        "Physical discomfort",
        "No sleep",
        "Faint or dizzy",
        "Sick or unwell",
        "Unsafe condition",
    }
    health_issue_today = bool(problem_issues & health_issues)
    today_is_red = review_result["day_mode"] == "Red Day"
    heavy_shift_today = mission_context["workload"].lower() == "high"
    missed_study = any(
        entry["mission"]["category"] == "Study" and entry["status"] == "MISSED"
        for entry in review_entries
    )
    missed_health = any(
        entry["mission"]["category"] == "Health" and entry["status"] == "MISSED"
        for entry in review_entries
    )
    project_displaced_must = any(
        entry["missed_reason"] == "Project displaced Must Do"
        or ("project" in entry["problem_note"].lower() and "displac" in entry["problem_note"].lower())
        for entry in review_entries
    )

    recovery_required = today_is_red or health_issue_today
    if recovery_required:
        tomorrow_mode = "Recovery / Yellow Day"
        engine_mode = "Yellow Day"
    elif heavy_shift_today or review_result["day_mode"] == "Yellow Day":
        tomorrow_mode = "Yellow Day"
        engine_mode = "Yellow Day"
    else:
        tomorrow_mode = "Green Day"
        engine_mode = "Green Day"

    missions, do_not_do, tomorrow_context = generate_today_missions(
        seed_data, tomorrow_date, engine_mode
    )
    exam, days_until_exam = nearest_exam(seed_data["exams"], tomorrow_date)

    if recovery_required:
        missions = [mission for mission in missions if mission["category"] != "Project"]
        for mission in missions:
            if mission["category"] == "Health":
                mission.update(
                    {
                        "title": "Recovery first: rest and light movement",
                        "layer": "Must",
                        "reason": "Today had a Red Day or health/safety signal, so tomorrow stays recovery-focused.",
                        "amount": "Rest as needed; movement up to 10 minutes",
                    }
                )
        do_not_do.extend(
            [
                "Do not do heavy exercise tomorrow.",
                "Do not add optional high-effort work to a Recovery / Yellow Day.",
            ]
        )

    if missed_study and days_until_exam is not None and days_until_exam < 30:
        for mission in missions:
            if mission["category"] == "Study":
                study_minutes = 90 if days_until_exam < 7 else 60
                mission.update(
                    {
                        "layer": "Must",
                        "reason": (
                            f"Study was missed today and {exam.get('subject', 'the exam')} "
                            f"is in {days_until_exam} day(s), so it moves up tomorrow."
                        ),
                        "amount": f"{study_minutes} minutes",
                    }
                )

    if days_until_exam is not None and days_until_exam < 7:
        missions = [mission for mission in missions if mission["category"] != "Project"]
        do_not_do.append("Do not let project work displace study inside the 7-day exam window.")

    if project_displaced_must:
        for mission in missions:
            if mission["category"] == "Project":
                mission.update(
                    {
                        "layer": "Could",
                        "reason": "Project work displaced a Must task today, so tomorrow it is tightly limited.",
                        "amount": "Up to 10 minutes",
                    }
                )
        do_not_do.append("Do not start project work before every Must mission is protected tomorrow.")

    if heavy_shift_today:
        for mission in missions:
            if mission["category"] == "Project":
                project_target = planned_numeric_target(mission["amount"]) or 15
                mission["amount"] = f"Up to {min(round(project_target), 15)} minutes"
                mission["reason"] = "Today had a heavy shift, so optional work stays short tomorrow."
        do_not_do.append("Do not schedule high-effort optional tasks after today’s heavy shift.")

    if missed_health:
        for mission in missions:
            if mission["category"] == "Health":
                mission.update(
                    {
                        "title": "Light movement without compensation",
                        "layer": "Should",
                        "reason": "Exercise was missed today; tomorrow resumes gently instead of compensating.",
                        "amount": "10–15 minutes",
                    }
                )
        do_not_do.append("Do not compensate for missed exercise with heavier exercise tomorrow.")

    layer_order = {"Must": 0, "Should": 1, "Could": 2}
    missions.sort(key=lambda mission: layer_order[mission["layer"]])
    missions = missions[:5]
    do_not_do = list(dict.fromkeys(do_not_do))

    recovery_note = ""
    if recovery_required:
        recovery_note = (
            "Recovery note: tomorrow is constrained to Recovery / Yellow Day. "
            "Keep activity light and do not use a good score to override today’s safety signal."
        )
    elif heavy_shift_today or missed_health:
        recovery_note = (
            "Recovery note: use lighter effort tomorrow and avoid compensating for anything missed today."
        )

    return {
        "date": tomorrow_date,
        "mode": tomorrow_mode,
        "shift": tomorrow_context["shift"],
        "missions": missions,
        "do_not_do": do_not_do,
        "recovery_note": recovery_note,
        "main_blocker": review_result["main_blocker"],
        "source_day_score": review_result["daily_score"],
    }


def tomorrow_plan_rows(plan: dict[str, Any]) -> list[dict[str, str]]:
    do_not_note = " | ".join(plan["do_not_do"])
    rows: list[dict[str, str]] = []
    for index, mission in enumerate(plan["missions"], start=1):
        category = "".join(
            character for character in mission["category"].lower() if character.isalnum()
        )
        rows.append(
            {
                "date": plan["date"].isoformat(),
                "shift": plan["shift"],
                "mode": plan["mode"],
                "mission_id": f"{plan['date']:%Y%m%d}_{index:02d}_{category or 'mission'}",
                "mission_title": mission["title"],
                "category": mission["category"],
                "target_value": mission["amount"],
                "target_unit": "",
                "priority": str(index),
                "must_should_could": mission["layer"],
                "do_not_do_note": do_not_note,
            }
        )
    return rows


def generate_rough_30_day_plan(
    seed_data: dict[str, Any],
    start_date: date,
    starting_day_mode: str,
    saved_result: dict[str, Any] | None,
) -> list[dict[str, str]]:
    project_rows = seed_data["projects"].get("projects", [])
    if not isinstance(project_rows, list):
        project_rows = []
    active_project = next(
        (
            project
            for project in project_rows
            if isinstance(project, dict) and project.get("status") == "active"
        ),
        {},
    )
    project_minutes = positive_int(active_project.get("allowed_minutes_per_day"), 30)
    garden_by_date = {
        row.get("date", ""): row for row in seed_data["garden"] if row.get("date")
    }

    reviewed_mode = starting_day_mode
    health_signal_today = starting_day_mode == "Red Day"
    if saved_result and saved_result.get("date") == start_date.isoformat():
        reviewed_mode = saved_result.get("day_mode", starting_day_mode)
        health_signal_today = bool(saved_result.get("health_caution"))

    recovery_bias_date = (
        start_date + timedelta(days=1)
        if reviewed_mode == "Red Day" or health_signal_today
        else None
    )

    overview: list[dict[str, str]] = []
    for offset in range(30):
        plan_date = start_date + timedelta(days=offset)
        shift = shift_for_date(seed_data["shifts"], plan_date)
        shift_name = (shift.get("shift") or "No schedule").strip()
        workload = (shift.get("expected_workload") or "unknown").strip().lower()
        heavy_shift = workload == "high"
        exam, days_until_exam = nearest_exam(seed_data["exams"], plan_date)
        subject = exam.get("subject", "upcoming exam") if exam else ""
        garden_task = garden_by_date.get(plan_date.isoformat(), {}).get("work_item", "")

        if offset == 0 and reviewed_mode == "Red Day":
            mode_hint = "Red"
        elif recovery_bias_date == plan_date:
            mode_hint = "Recovery"
        elif days_until_exam is not None and days_until_exam <= 7:
            mode_hint = "Study Focus"
        elif heavy_shift or (offset == 0 and reviewed_mode == "Yellow Day"):
            mode_hint = "Yellow"
        else:
            mode_hint = "Green"

        if mode_hint in {"Red", "Recovery"}:
            main_focus = "Recovery and essential commitments"
            study_load = "Light review only (20–30 min)"
            allowance = "No project; garden only if essential"
            rest_note = "No heavy exercise; keep effort light and reassess daily"
        elif mode_hint == "Study Focus":
            main_focus = f"Exam preparation: {subject}"
            study_load = "High focus (90 min)" if days_until_exam is not None else "High focus"
            allowance = "Project paused; garden essential only"
            rest_note = "Protect sleep and avoid late optional work"
        elif heavy_shift:
            main_focus = f"{shift_name.title()} shift and minimum essentials"
            study_load = "Light review (20–30 min)"
            allowance = "Project up to 15 min; no garden"
            rest_note = "Keep activity light after the shift"
        else:
            if days_until_exam is not None and days_until_exam < 30:
                main_focus = f"Steady study: {subject}"
                study_load = "Medium-high (60 min)"
            elif exam:
                main_focus = f"Steady progress toward {subject}"
                study_load = "Maintenance (45 min)"
            else:
                main_focus = "Balanced essentials and recovery"
                study_load = "Maintenance (30–45 min)"

            if garden_task:
                allowance = f"Garden allowed: {garden_task}; project up to {project_minutes} min"
            else:
                allowance = f"Project up to {project_minutes} min; garden if energy allows"
            rest_note = "Normal recovery; adjust this map from the daily review"

        overview.append(
            {
                "Date": plan_date.isoformat(),
                "Mode hint": mode_hint,
                "Main focus": main_focus,
                "Study load": study_load,
                "Project / garden": allowance,
                "Rest / recovery": rest_note,
            }
        )

    return overview


def parse_iso_date(value: str) -> date | None:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def positive_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
        return parsed if parsed > 0 else default
    except (TypeError, ValueError):
        return default


def shift_for_date(shifts: list[dict[str, str]], selected_date: date) -> dict[str, str]:
    selected = selected_date.isoformat()
    return next((row for row in shifts if row.get("date") == selected), {})


def nearest_exam(exams: list[dict[str, str]], selected_date: date) -> tuple[dict[str, str], int | None]:
    upcoming: list[tuple[int, dict[str, str]]] = []
    for exam in exams:
        exam_date = parse_iso_date(exam.get("exam_date", ""))
        if exam_date is None:
            continue
        days_until = (exam_date - selected_date).days
        if days_until >= 0:
            upcoming.append((days_until, exam))

    if not upcoming:
        return {}, None

    days_until, exam = min(upcoming, key=lambda item: item[0])
    return exam, days_until


def generate_today_missions(
    seed_data: dict[str, Any], selected_date: date, day_mode: str
) -> tuple[list[dict[str, str]], list[str], dict[str, str]]:
    missions: list[dict[str, str]] = []
    do_not_do: list[str] = []

    profile = seed_data["profile"]
    health = seed_data["health"]
    shift = shift_for_date(seed_data["shifts"], selected_date)
    exam, days_until_exam = nearest_exam(seed_data["exams"], selected_date)

    shift_name = (shift.get("shift") or "No scheduled shift").strip()
    expected_workload = (shift.get("expected_workload") or "unknown").strip().lower()
    heavy_shift = expected_workload == "high"
    is_red_day = day_mode == "Red Day"

    if shift_name.upper() not in {"", "OFF", "NO SCHEDULED SHIFT"}:
        missions.append(
            {
                "title": f"Complete the {shift_name.lower()} shift",
                "category": "Work",
                "layer": "Must",
                "reason": "A scheduled shift is a fixed commitment and stays ahead of optional work.",
                "amount": "Scheduled shift",
            }
        )

    study_goal = profile.get("study_goal", {})
    if not isinstance(study_goal, dict):
        study_goal = {}
    base_study_minutes = positive_int(study_goal.get("target_minutes_per_day"), 45)

    if exam and days_until_exam is not None:
        subject = exam.get("subject") or "upcoming exam"
        first_unit = (exam.get("study_units") or "next study unit").split("|")[0]
        if days_until_exam < 7:
            study_minutes = max(base_study_minutes, 90)
            study_reason = f"{subject} is in {days_until_exam} day(s), so study takes priority over projects."
        elif days_until_exam < 30:
            study_minutes = max(base_study_minutes, 60)
            study_reason = f"{subject} is in {days_until_exam} day(s), inside the 30-day priority window."
        else:
            study_minutes = base_study_minutes
            study_reason = f"A steady study block protects progress toward {subject}."

        missions.append(
            {
                "title": f"Study {subject}: {first_unit}",
                "category": "Study",
                "layer": "Must" if days_until_exam < 30 else "Should",
                "reason": study_reason,
                "amount": f"{study_minutes} minutes",
            }
        )
    else:
        missions.append(
            {
                "title": study_goal.get("description") or "Protect a short study block",
                "category": "Study",
                "layer": "Should",
                "reason": "No dated exam is available, so the engine keeps a small maintenance block.",
                "amount": f"{base_study_minutes} minutes",
            }
        )

    preferred_exercise = health.get("preferred_exercise_types", ["light movement"])
    if not isinstance(preferred_exercise, list) or not preferred_exercise:
        preferred_exercise = ["light movement"]

    if is_red_day:
        missions.append(
            {
                "title": "Protect recovery and essential needs",
                "category": "Health",
                "layer": "Must",
                "reason": "Red Day capacity overrides the planned schedule.",
                "amount": "Rest as needed",
            }
        )
        do_not_do.append("Do not do heavy exercise on a Red Day.")
    elif day_mode == "Yellow Day" or heavy_shift:
        missions.append(
            {
                "title": "Use light movement or recovery",
                "category": "Health",
                "layer": "Should",
                "reason": "Limited capacity or a heavy shift calls for a lighter health task.",
                "amount": "10–15 minutes",
            }
        )
    else:
        missions.append(
            {
                "title": f"Do {preferred_exercise[0]}",
                "category": "Health",
                "layer": "Should",
                "reason": "A Green Day can include a modest health-supporting activity.",
                "amount": "20–30 minutes",
            }
        )

    project_rows = seed_data["projects"].get("projects", [])
    if not isinstance(project_rows, list):
        project_rows = []
    active_project = next(
        (project for project in project_rows if isinstance(project, dict) and project.get("status") == "active"),
        None,
    )

    project_reduced_for_exam = days_until_exam is not None and days_until_exam < 7
    if active_project and not is_red_day and not project_reduced_for_exam:
        project_minutes = positive_int(active_project.get("allowed_minutes_per_day"), 30)
        reason = "Optional project work is allowed only after all Must missions."
        if heavy_shift:
            project_minutes = min(project_minutes, 15)
            reason = "The heavy shift rule reduces optional project time."

        missions.append(
            {
                "title": f"Optional: {active_project.get('name') or 'personal project'}",
                "category": "Project",
                "layer": "Could",
                "reason": reason,
                "amount": f"Up to {project_minutes} minutes",
            }
        )
    elif project_reduced_for_exam:
        do_not_do.append("Do not let project work displace study inside the 7-day exam window.")
    elif is_red_day:
        do_not_do.append("Do not start optional project work on a Red Day.")

    garden_row = next(
        (row for row in seed_data["garden"] if row.get("date") == selected_date.isoformat()),
        None,
    )
    if garden_row and not is_red_day and not heavy_shift and not project_reduced_for_exam:
        missions.append(
            {
                "title": garden_row.get("work_item") or "Small garden task",
                "category": "Life Maintenance",
                "layer": "Could",
                "reason": "The local garden plan has a task for this date and no higher-priority rule blocks it.",
                "amount": f"Up to {positive_int(garden_row.get('estimated_minutes'), 20)} minutes",
            }
        )

    if heavy_shift:
        do_not_do.append("Do not extend optional project work beyond the reduced time limit after a heavy shift.")
    do_not_do.append("Do not begin Could missions before Must missions are protected.")

    layer_order = {"Must": 0, "Should": 1, "Could": 2}
    missions.sort(key=lambda mission: layer_order[mission["layer"]])
    missions = missions[:5]

    if not missions:
        missions.append(
            {
                "title": "Choose one essential commitment",
                "category": "Life Maintenance",
                "layer": "Must",
                "reason": "Local seed data is incomplete, so the engine uses a safe planning placeholder.",
                "amount": "15 minutes to define it",
            }
        )

    context = {
        "shift": shift_name,
        "workload": expected_workload.title(),
        "exam": (
            f"{exam.get('subject', 'Exam')} in {days_until_exam} day(s)"
            if exam and days_until_exam is not None
            else "No upcoming dated exam"
        ),
    }
    return missions, do_not_do, context


THAI_CATEGORY = {
    "Work": "งาน / เวร",
    "Study": "อ่านหนังสือ",
    "Health": "สุขภาพ",
    "Project": "โปรเจกต์",
    "Life Maintenance": "ดูแลชีวิตประจำวัน",
}
THAI_LAYER = {"Must": "ต้องทำ", "Should": "ควรทำ", "Could": "ทำได้ถ้ามีแรง"}
THAI_DAY_MODE = {
    "Green Day": "วันพลังพร้อม",
    "Yellow Day": "วันพลังจำกัด",
    "Red Day": "วันพักฟื้น",
    "Recovery / Yellow Day": "พักฟื้น / พลังจำกัด",
}
THAI_STATUS = {
    "DONE": "ทำครบ",
    "PARTIAL": "ทำบางส่วน",
    "MISSED": "ไม่ได้ทำ",
    "PROBLEM": "มีปัญหา",
}
THAI_MISSED_REASON = {
    "Not enough time": "เวลาไม่พอ",
    "Higher-priority work": "มีงานสำคัญกว่าแทรก",
    "Project displaced Must Do": "โปรเจกต์แย่งเวลางานที่ต้องทำ",
    "Low energy": "พลังงานไม่พอ",
    "Forgot": "ลืม",
    "Other": "เหตุผลอื่น",
}
THAI_PROBLEM_ISSUE = {
    "Heavy workload": "ภาระงานหนัก",
    "Very heavy shift": "เวรหนักมาก",
    "Low energy": "พลังงานต่ำ",
    "Physical discomfort": "ไม่สบายตัว / ปวดเมื่อย",
    "No sleep": "ไม่ได้นอน",
    "Faint or dizzy": "เป็นลมหรือเวียนหัว",
    "Sick or unwell": "ป่วยหรือไม่สบาย",
    "Unsafe condition": "สถานการณ์ไม่ปลอดภัย",
    "Unexpected task": "มีงานด่วนแทรก",
    "Technical issue": "ปัญหาทางเทคนิค",
    "Other": "ปัญหาอื่น",
}
THAI_UNIT = {
    "minutes": "นาที",
    "items": "รายการ",
    "percent": "เปอร์เซ็นต์",
    "other": "หน่วยอื่น",
}


def thai_seed_text(value: str) -> str:
    replacements = {
        "Demo Subject A": "วิชาตัวอย่าง A",
        "Demo Subject B": "วิชาตัวอย่าง B",
        "Unit 1": "บทที่ 1",
        "Unit 2": "บทที่ 2",
        "Unit 3": "บทที่ 3",
        "Module A": "หัวข้อ A",
        "Module B": "หัวข้อ B",
        "Demo Personal Project": "โปรเจกต์ส่วนตัวตัวอย่าง",
        "Demo File Cleanup": "จัดระเบียบไฟล์ตัวอย่าง",
    }
    for source, localized in replacements.items():
        value = value.replace(source, localized)
    return value


def thai_shift(value: str) -> str:
    return {
        "OFF": "วันหยุด",
        "MORNING": "เวรเช้า",
        "EVENING": "เวรเย็น",
        "NIGHT": "เวรดึก",
        "No scheduled shift": "ไม่มีเวรที่กำหนด",
    }.get(value, value)


def thai_workload(value: str) -> str:
    return {
        "Low": "เบา",
        "Medium": "ปานกลาง",
        "High": "หนัก",
        "Unknown": "ยังไม่ระบุ",
    }.get(value, value)


def thai_amount(value: str) -> str:
    exact = {
        "Scheduled shift": "ตามเวลาเวร",
        "Rest as needed": "พักตามที่ร่างกายต้องการ",
        "Rest as needed; movement up to 10 minutes": "พักตามที่ต้องการ; ขยับเบา ๆ ไม่เกิน 10 นาที",
        "15 minutes to define it": "ใช้เวลา 15 นาทีเพื่อกำหนดงาน",
    }
    if value in exact:
        return exact[value]
    patterns = (
        (r"^Up to (\d+) minutes$", r"ไม่เกิน \1 นาที"),
        (r"^(\d+)[–-](\d+) minutes$", r"\1–\2 นาที"),
        (r"^(\d+) minutes$", r"\1 นาที"),
    )
    for pattern, replacement in patterns:
        if re.match(pattern, value):
            return re.sub(pattern, replacement, value)
    return value


def thai_mission_title(value: str) -> str:
    exact = {
        "Protect a short study block": "รักษาช่วงอ่านหนังสือสั้น ๆ",
        "Protect recovery and essential needs": "พักฟื้นและทำเฉพาะสิ่งจำเป็น",
        "Use light movement or recovery": "ขยับเบา ๆ หรือพักฟื้น",
        "Recovery first: rest and light movement": "พักฟื้นก่อน: พักและขยับเบา ๆ",
        "Light movement without compensation": "กลับมาเคลื่อนไหวเบา ๆ โดยไม่เร่งชดเชย",
        "Choose one essential commitment": "เลือกสิ่งจำเป็นที่สุดหนึ่งอย่าง",
        "Small garden task": "งานสวนเล็ก ๆ",
        "Inspect demo garden area": "ตรวจดูพื้นที่สวนตัวอย่าง",
        "Water demo plants": "รดน้ำต้นไม้ตัวอย่าง",
    }
    if value in exact:
        return exact[value]
    match = re.match(r"^Complete the (.+) shift$", value)
    if match:
        shift_name = match.group(1).upper()
        return f"ทำ{thai_shift(shift_name)}ให้เรียบร้อย"
    match = re.match(r"^Study (.+): (.+)$", value)
    if match:
        return f"อ่าน {thai_seed_text(match.group(1))}: {thai_seed_text(match.group(2))}"
    if value.startswith("Optional: "):
        return "ทำเมื่อมีแรงเหลือ: " + thai_seed_text(value.removeprefix("Optional: "))
    if value.startswith("Do "):
        activity = value.removeprefix("Do ")
        activity = {"walking": "เดิน", "light movement": "ขยับร่างกายเบา ๆ"}.get(
            activity, activity
        )
        return f"ดูแลสุขภาพ: {activity}"
    return value


def thai_reason(value: str) -> str:
    exact = {
        "A scheduled shift is a fixed commitment and stays ahead of optional work.": "เวรเป็นงานที่กำหนดไว้ จึงมาก่อนงานเสริม",
        "No dated exam is available, so the engine keeps a small maintenance block.": "ยังไม่มีวันสอบ จึงคงช่วงอ่านสั้น ๆ ไว้ก่อน",
        "Red Day capacity overrides the planned schedule.": "วันนี้ร่างกายต้องมาก่อนแผน",
        "Limited capacity or a heavy shift calls for a lighter health task.": "วันนี้พลังจำกัด จึงเลือกกิจกรรมเบา",
        "A Green Day can include a modest health-supporting activity.": "วันนี้พลังพร้อม จึงดูแลสุขภาพแบบพอดีได้",
        "Optional project work is allowed only after all Must missions.": "ทำได้หลังงานที่ต้องทำครบแล้ว",
        "The heavy shift rule reduces optional project time.": "เวรหนัก จึงลดเวลาโปรเจกต์",
        "The local garden plan has a task for this date and no higher-priority rule blocks it.": "วันนี้มีงานสวนและไม่มีงานสำคัญกว่าขวาง",
        "Local seed data is incomplete, so the engine uses a safe planning placeholder.": "ข้อมูลยังไม่ครบ จึงใช้ภารกิจสำรองที่ปลอดภัย",
        "Today had a Red Day or health/safety signal, so tomorrow stays recovery-focused.": "วันนี้มีสัญญาณความปลอดภัย พรุ่งนี้จึงเน้นพักฟื้น",
        "Project work displaced a Must task today, so tomorrow it is tightly limited.": "วันนี้โปรเจกต์แย่งงานสำคัญ พรุ่งนี้จึงจำกัดเวลา",
        "Today had a heavy shift, so optional work stays short tomorrow.": "วันนี้เวรหนัก พรุ่งนี้จึงลดงานเสริม",
        "Exercise was missed today; tomorrow resumes gently instead of compensating.": "พรุ่งนี้กลับมาเบา ๆ โดยไม่เร่งชดเชย",
    }
    if value in exact:
        return exact[value]
    dynamic_patterns = (
        (
            r"^(.+) is in (\d+) day\(s\), so study takes priority over projects\.$",
            lambda m: f"เหลือ {m.group(2)} วันก่อนสอบ {thai_seed_text(m.group(1))} จึงให้อ่านหนังสือมาก่อนโปรเจกต์",
        ),
        (
            r"^(.+) is in (\d+) day\(s\), inside the 30-day priority window\.$",
            lambda m: f"เหลือ {m.group(2)} วันก่อนสอบ {thai_seed_text(m.group(1))} ซึ่งอยู่ในช่วงเร่งความสำคัญ 30 วัน",
        ),
        (
            r"^A steady study block protects progress toward (.+)\.$",
            lambda m: f"การอ่านอย่างสม่ำเสมอช่วยรักษาความคืบหน้าไปสู่ {thai_seed_text(m.group(1))}",
        ),
        (
            r"^Study was missed today and (.+) is in (\d+) day\(s\), so it moves up tomorrow\.$",
            lambda m: f"วันนี้พลาดการอ่าน และเหลือ {m.group(2)} วันก่อนสอบ {thai_seed_text(m.group(1))} พรุ่งนี้จึงเลื่อนขึ้นเป็นงานสำคัญ",
        ),
    )
    for pattern, formatter in dynamic_patterns:
        match = re.match(pattern, value)
        if match:
            return formatter(match)
    return value


def thai_do_not(value: str) -> str:
    return {
        "Do not do heavy exercise on a Red Day.": "งดออกกำลังกายหนักในวันพักฟื้น",
        "Do not let project work displace study inside the 7-day exam window.": "อย่าให้โปรเจกต์แย่งเวลาอ่านหนังสือในช่วง 7 วันก่อนสอบ",
        "Do not start optional project work on a Red Day.": "งดเริ่มโปรเจกต์เสริมในวันพักฟื้น",
        "Do not extend optional project work beyond the reduced time limit after a heavy shift.": "หลังเวรหนัก อย่าทำโปรเจกต์เกินเวลาที่ลดไว้",
        "Do not begin Could missions before Must missions are protected.": "อย่าเริ่มงานที่ทำได้ถ้ามีแรง ก่อนปกป้องงานที่ต้องทำ",
        "Do not do heavy exercise tomorrow.": "พรุ่งนี้งดออกกำลังกายหนัก",
        "Do not add optional high-effort work to a Recovery / Yellow Day.": "อย่าเพิ่มงานเสริมที่ใช้แรงมากในวันพักฟื้นหรือพลังจำกัด",
        "Do not start project work before every Must mission is protected tomorrow.": "พรุ่งนี้อย่าเริ่มโปรเจกต์ก่อนปกป้องงานที่ต้องทำทั้งหมด",
        "Do not schedule high-effort optional tasks after today’s heavy shift.": "หลังเวรหนักวันนี้ อย่าวางงานเสริมที่ใช้แรงมากไว้พรุ่งนี้",
        "Do not compensate for missed exercise with heavier exercise tomorrow.": "อย่าชดเชยการออกกำลังกายที่พลาดด้วยการออกหนักขึ้นพรุ่งนี้",
    }.get(value, value)


def thai_result_text(value: str) -> str:
    direct = {
        "A serious capacity or safety signal overrides the completion score.": "สัญญาณสุขภาพหรือความปลอดภัยที่สำคัญ อยู่เหนือคะแนนความสำเร็จ",
        "Good completion with no serious issue reported.": "ทำภารกิจได้ดีและไม่มีสัญญาณปัญหารุนแรง",
        "Results show partial completion, limited capacity, or a normal blocker; keep expectations realistic.": "วันนี้ทำได้บางส่วนหรือมีข้อจำกัด ควรตั้งเป้าพรุ่งนี้ให้เหมาะกับพลังจริง",
        "No major blocker reported": "ไม่พบอุปสรรคหลัก",
        "Partial completion": "ทำได้บางส่วน",
        "Health caution: reduce demands and avoid strenuous activity. If symptoms are severe, recurring, or you feel unsafe, seek appropriate professional help.": "คำเตือนด้านสุขภาพ: ลดภาระและงดกิจกรรมหนัก หากอาการรุนแรง เป็นซ้ำ หรือรู้สึกไม่ปลอดภัย ควรขอความช่วยเหลือจากบุคลากรที่เหมาะสม",
        "Health caution: keep demands light and reassess capacity. Seek appropriate professional help if symptoms are severe or recurring.": "คำเตือนด้านสุขภาพ: ลดภาระและประเมินกำลังอีกครั้ง หากอาการรุนแรงหรือเป็นซ้ำ ควรขอความช่วยเหลือจากบุคลากรที่เหมาะสม",
        "Recovery note: tomorrow is constrained to Recovery / Yellow Day. Keep activity light and do not use a good score to override today’s safety signal.": "หมายเหตุการฟื้นตัว: พรุ่งนี้เป็นวันพักฟื้น / พลังจำกัด ให้ทำกิจกรรมเบา ๆ และอย่าใช้คะแนนที่ดีลบล้างสัญญาณความปลอดภัยของวันนี้",
        "Recovery note: use lighter effort tomorrow and avoid compensating for anything missed today.": "หมายเหตุการฟื้นตัว: พรุ่งนี้ลดแรงลง และไม่ต้องเร่งชดเชยสิ่งที่พลาดวันนี้",
    }
    if value in direct:
        return direct[value]
    if value in THAI_MISSED_REASON:
        return THAI_MISSED_REASON[value]
    if value in THAI_PROBLEM_ISSUE:
        return THAI_PROBLEM_ISSUE[value]
    return value


def thai_exam_context(value: str) -> str:
    if value == "No upcoming dated exam":
        return "ยังไม่มีวันสอบที่กำหนด"
    match = re.match(r"^(.+) in (\d+) day\(s\)$", value)
    if match:
        return f"{thai_seed_text(match.group(1))} · เหลือ {match.group(2)} วัน"
    return value


def thai_data_issue(value: str) -> str:
    if value.endswith(" is missing"):
        return f"ไม่พบไฟล์ {value.removesuffix(' is missing')}"
    if value.endswith(" is unreadable"):
        return f"อ่านไฟล์ {value.removesuffix(' is unreadable')} ไม่ได้"
    if "unexpected header" in value:
        return "หัวตารางของไฟล์บันทึกไม่ตรงรูปแบบเดิม ระบบไม่ได้แก้ข้อมูลเก่า"
    return value


def localize_rough_plan(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    mode_labels = {
        "Green": "พลังพร้อม",
        "Yellow": "พลังจำกัด",
        "Red": "พักฟื้น",
        "Recovery": "ฟื้นตัว",
        "Study Focus": "เน้นอ่านสอบ",
    }
    main_focus = {
        "Recovery and essential commitments": "พักฟื้นและทำเฉพาะสิ่งจำเป็น",
        "Balanced essentials and recovery": "สมดุลงานจำเป็นกับการพัก",
    }
    study_load = {
        "Light review only (20–30 min)": "ทบทวนเบา ๆ 20–30 นาที",
        "High focus (90 min)": "เน้นสูง 90 นาที",
        "High focus": "เน้นสูง",
        "Light review (20–30 min)": "ทบทวนเบา ๆ 20–30 นาที",
        "Medium-high (60 min)": "ปานกลาง–สูง 60 นาที",
        "Maintenance (45 min)": "รักษาความต่อเนื่อง 45 นาที",
        "Maintenance (30–45 min)": "รักษาความต่อเนื่อง 30–45 นาที",
    }
    rest_notes = {
        "No heavy exercise; keep effort light and reassess daily": "งดออกกำลังกายหนัก ทำเบา ๆ และประเมินใหม่ทุกวัน",
        "Protect sleep and avoid late optional work": "ปกป้องเวลานอน และงดงานเสริมช่วงดึก",
        "Keep activity light after the shift": "หลังเวรให้ทำกิจกรรมเบา ๆ",
        "Normal recovery; adjust this map from the daily review": "พักตามปกติ และปรับแผนจากผลจริงรายวัน",
    }
    localized: list[dict[str, str]] = []
    for row in rows:
        focus = row["Main focus"]
        focus = main_focus.get(focus, focus)
        focus = re.sub(r"^Exam preparation: (.+)$", r"เตรียมสอบ: \1", focus)
        focus = re.sub(r"^Steady study: (.+)$", r"อ่านต่อเนื่อง: \1", focus)
        focus = re.sub(r"^Steady progress toward (.+)$", r"ค่อย ๆ เดินหน้า: \1", focus)
        focus = re.sub(r"^(.+) shift and minimum essentials$", r"เวร \1 และงานจำเป็นขั้นต่ำ", focus)
        focus = thai_seed_text(focus).replace("เวร Night", "เวรดึก").replace("เวร Morning", "เวรเช้า").replace("เวร Evening", "เวรเย็น")

        allowance = row["Project / garden"]
        allowance = allowance.replace("No project; garden only if essential", "งดโปรเจกต์; ทำสวนเฉพาะจำเป็น")
        allowance = allowance.replace("Project paused; garden essential only", "พักโปรเจกต์; ทำสวนเฉพาะจำเป็น")
        allowance = re.sub(r"^Project up to (\d+) min; no garden$", r"โปรเจกต์ไม่เกิน \1 นาที; งดงานสวน", allowance)
        allowance = re.sub(
            r"^Garden allowed: (.+); project up to (\d+) min$",
            r"ทำสวนได้: \1; โปรเจกต์ไม่เกิน \2 นาที",
            allowance,
        )
        allowance = re.sub(
            r"^Project up to (\d+) min; garden if energy allows$",
            r"โปรเจกต์ไม่เกิน \1 นาที; ทำสวนเมื่อมีแรง",
            allowance,
        )
        allowance = allowance.replace("Inspect demo garden area", "ตรวจดูพื้นที่สวนตัวอย่าง")
        allowance = allowance.replace("Water demo plants", "รดน้ำต้นไม้ตัวอย่าง")

        localized.append(
            {
                "วันที่": row["Date"],
                "แนวโน้มวัน": mode_labels.get(row["Mode hint"], row["Mode hint"]),
                "เป้าหมายหลัก": focus,
                "เวลาอ่าน": study_load.get(row["Study load"], row["Study load"]),
                "โปรเจกต์ / สวน": allowance,
                "พัก / ฟื้นตัว": rest_notes.get(row["Rest / recovery"], row["Rest / recovery"]),
            }
        )
    return localized


def rough_plan_table_html(rows: list[dict[str, str]]) -> str:
    headers = ("วันที่", "แนวโน้มวัน", "เป้าหมายหลัก", "เวลาอ่าน", "โปรเจกต์ / สวน", "พัก / ฟื้นตัว")
    mode_classes = {
        "พลังพร้อม": "green",
        "พลังจำกัด": "yellow",
        "พักฟื้น": "red",
        "ฟื้นตัว": "recovery",
        "เน้นอ่านสอบ": "study",
    }
    header_html = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body_rows = []
    for row in rows:
        mode = row["แนวโน้มวัน"]
        mode_class = mode_classes.get(mode, "neutral")
        cells = [f"<td>{escape(row['วันที่'])}</td>"]
        cells.append(
            f'<td><span class="plan-mode plan-mode-{mode_class}">{escape(mode)}</span></td>'
        )
        cells.extend(f"<td>{escape(row[header])}</td>" for header in headers[2:])
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    return f"""
    <div class="plan-table-shell" data-plan-rows="{len(rows)}" data-plan-columns="{len(headers)}">
        <table class="plan-table">
            <thead><tr>{header_html}</tr></thead>
            <tbody>{''.join(body_rows)}</tbody>
        </table>
    </div>
    """


def mission_card_html(
    mission: dict[str, str], index: int, *, compact: bool = False, integrated: bool = False
) -> str:
    layer = mission["layer"]
    layer_class = layer.lower()
    display_class = " mission-compact" if compact else ""
    featured_class = " mission-featured" if index == 1 and not compact else ""
    integrated_class = " mission-integrated" if integrated else ""
    category_icon = {
        "Work": "▣",
        "Study": "◆",
        "Health": "●",
        "Project": "◇",
        "Life Maintenance": "■",
    }.get(mission["category"], "•")

    return f"""
    <div class="mission-card mission-{layer_class}{display_class}{featured_class}{integrated_class}">
        <div class="mission-card-top">
            <span class="mission-number">{index:02d}</span>
            <span class="priority-badge priority-{layer_class}">{escape(THAI_LAYER.get(layer, layer))}</span>
        </div>
        <div class="mission-title">{escape(thai_mission_title(mission['title']))}</div>
        <div class="mission-meta">
            <span class="meta-chip">{category_icon} {escape(THAI_CATEGORY.get(mission['category'], mission['category']))}</span>
            <span class="meta-chip">◷ {escape(thai_amount(mission['amount']))}</span>
        </div>
        <div class="mission-reason"><strong>เหตุผล:</strong> {escape(thai_reason(mission['reason']))}</div>
    </div>
    """


NAV_SECTIONS = (
    "🏠 วันนี้ต้องทำอะไร",
    "🌤 แผนพรุ่งนี้",
    "🕒 แผนละเอียดรายวัน",
    "📅 ภาพรวม 30 วัน",
    "⚙️ ตั้งค่าชีวิต",
)


def section_header_html(title: str, subtitle: str, icon: str) -> str:
    return f"""
    <div class="section-hero">
        <div class="section-hero-icon">{escape(icon)}</div>
        <div>
            <div class="section-kicker">ผู้ช่วยวางแผนชีวิตประจำวัน</div>
            <h1>{escape(title)}</h1>
            <p>{escape(subtitle)}</p>
        </div>
    </div>
    """


def dashboard_summary_html(
    missions: list[dict[str, str]],
    day_mode: str,
    do_not_do: list[str],
    saved_summary: dict[str, Any] | None,
) -> str:
    score = f"{saved_summary['daily_score']}/100" if saved_summary else "ยังไม่บันทึก"
    mode = saved_summary["day_mode"] if saved_summary else day_mode
    caution = (
        thai_result_text(saved_summary["health_caution"])
        if saved_summary and saved_summary.get("health_caution")
        else thai_do_not(do_not_do[0]) if do_not_do else "ทำตามลำดับและพักเมื่อพลังไม่พอ"
    )
    cards = (
        ("จำนวนภารกิจวันนี้", str(len(missions)), "รายการ"),
        ("คะแนนล่าสุด", score, "หลังบันทึกผล"),
        ("โหมดของวัน", THAI_DAY_MODE.get(mode, mode), "ตามพลังและความปลอดภัย"),
        ("สิ่งที่ต้องระวัง", caution, "วันนี้"),
    )
    return '<div class="summary-grid">' + "".join(
        f"""
        <div class="summary-card">
            <span>{escape(label)}</span>
            <strong>{escape(value)}</strong>
            <small>{escape(note)}</small>
        </div>
        """
        for label, value, note in cards
    ) + "</div>"


def daily_detail_html(
    missions: list[dict[str, str]], seed_data: dict[str, Any], day_mode: str
) -> str:
    time_labels = {
        "Work": "ตามเวลาเวรหรือช่วงงานหลัก",
        "Study": "ช่วงที่มีสมาธิดี",
        "Health": "หลังงานหลักหรือช่วงเย็น",
        "Project": "เมื่อภารกิจหลักเสร็จแล้ว",
        "Life Maintenance": "ช่วงสั้น ๆ ระหว่างวัน",
    }
    rows = "".join(
        f"""
        <div class="daily-row">
            <span class="daily-time">{escape(time_labels.get(mission['category'], 'เลือกช่วงที่พร้อม'))}</span>
            <div><strong>{escape(thai_mission_title(mission['title']))}</strong><small>{escape(THAI_CATEGORY.get(mission['category'], mission['category']))} · {escape(thai_amount(mission['amount']))}</small></div>
        </div>
        """
        for mission in missions
    )
    health = seed_data.get("health", {})
    profile = seed_data.get("profile", {})
    food_map = {
        "regular balanced meals": "มื้ออาหารสมดุลทั่วไป",
        "adequate water": "ดื่มน้ำให้เพียงพอตามปกติ",
    }
    food_patterns = health.get("preferred_food_patterns", [])
    food_text = " · ".join(food_map.get(item, item) for item in food_patterns) or "เลือกมื้อทั่วไปที่สมดุล"
    calorie_target = health.get("daily_calorie_target") or profile.get("daily_calorie_target")
    calorie_text = f"{calorie_target} กิโลแคลอรี่ (ผู้ใช้กำหนดเอง)" if calorie_target else "ยังไม่ได้กำหนด — ระบบไม่คำนวณแทน"
    exercise_text = {
        "Red Day": "พักฟื้น งดกิจกรรมหนัก",
        "Yellow Day": "กิจกรรมเบา ตามพลังจริง",
        "Green Day": "เบาถึงปานกลางตามแผนเดิม",
    }.get(day_mode, "เลือกตามพลังจริง")
    return f"""
    <div class="daily-layout">
        <section class="daily-card daily-card-wide">
            <h3>ช่วงเวลาแนะนำ · งาน/อ่านหนังสือที่ควรทำ</h3>
            {rows}
        </section>
        <section class="daily-card">
            <h3>หมวดอาหารแบบทั่วไป</h3>
            <p>{escape(food_text)}</p>
            <small>เป็นเพียงการจัดหมวดอาหารทั่วไป</small>
        </section>
        <section class="daily-card">
            <h3>เป้าหมายแคลอรี่</h3>
            <p>{escape(calorie_text)}</p>
            <small>แสดงเฉพาะค่าที่ผู้ใช้กำหนดเอง</small>
        </section>
        <section class="daily-card">
            <h3>ออกกำลังแบบเบา / ปานกลาง / พักฟื้น</h3>
            <p>{escape(exercise_text)}</p>
            <small>วางแผนทั่วไป ไม่ใช่คำแนะนำทางการแพทย์</small>
        </section>
    </div>
    """


def settings_summary_html(seed_data: dict[str, Any]) -> str:
    profile = seed_data.get("profile", {})
    health = seed_data.get("health", {})
    study = profile.get("study_goal", {})
    projects = profile.get("project_limits", {})
    calorie_target = health.get("daily_calorie_target") or profile.get("daily_calorie_target")
    exercise_map = {"walking": "เดิน", "light mobility": "ขยับร่างกายเบา ๆ"}
    exercises = " · ".join(exercise_map.get(item, item) for item in health.get("preferred_exercise_types", [])) or "ยังไม่ได้กำหนด"
    items = (
        ("ผู้ใช้ในเครื่อง", profile.get("name", "ผู้ใช้ในเครื่อง")),
        ("เวลาเริ่ม / เวลาพัก", f"{profile.get('wake_time', '—')} / {profile.get('sleep_target', '—')}"),
        ("เวลาอ่านต่อวัน", f"{study.get('target_minutes_per_day', '—')} นาที"),
        ("เวลาโปรเจกต์สูงสุด", f"{projects.get('max_minutes_per_day', '—')} นาที"),
        ("การเคลื่อนไหวที่ชอบ", exercises),
        ("เป้าหมายแคลอรี่", f"{calorie_target} กิโลแคลอรี่" if calorie_target else "ยังไม่ได้กำหนด"),
    )
    return '<div class="settings-grid">' + "".join(
        f'<div class="settings-card"><span>{escape(label)}</span><strong>{escape(str(value))}</strong></div>'
        for label, value in items
    ) + "</div>"


st.set_page_config(
    page_title="วันนี้ควรทำอะไรก่อน?",
    page_icon="🧭",
    layout="wide",
)

st.markdown(
    """
    <style>
        :root {
            --ink: #172033;
            --muted: #5d6676;
            --line: #e2ded5;
            --surface: #ffffff;
            --navy: #1f2a44;
            --cream: #f7f4ec;
            --primary: #5b4bd7;
            --primary-deep: #4638b6;
            --success: #15896b;
            --must: #c8483d;
            --must-soft: #fff2ef;
            --should: #a87313;
            --should-soft: #fff6df;
            --could: #5b4bd7;
            --could-soft: #f0edff;
        }
        [data-testid="stAppViewContainer"] {
            background: var(--cream);
            color: var(--ink);
        }
        [data-testid="stSidebar"] {
            border-right: 0;
            background: var(--navy);
        }
        [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            padding-top: 1.1rem;
        }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
            color: #f7f8fc !important;
        }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            color: #c9cfdd !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] > div {
            gap: 0.35rem;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            padding: 0.62rem 0.72rem;
            border: 1px solid transparent;
            border-radius: 0.72rem;
            background: transparent;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
            border-color: rgba(255, 255, 255, 0.12);
            background: var(--primary);
            box-shadow: 0 7px 16px rgba(0, 0, 0, 0.16);
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label p {
            color: #e6e9f2 !important;
            font-weight: 720 !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] input {
            accent-color: var(--success);
        }
        [data-testid="stAppViewContainer"] h1,
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] h3,
        [data-testid="stAppViewContainer"] p,
        [data-testid="stAppViewContainer"] label,
        [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] {
            color: var(--ink);
        }
        [data-testid="stCaptionContainer"] p,
        [data-testid="stWidgetLabel"] p,
        [data-testid="stMetricLabel"] p {
            color: #5d6676 !important;
        }
        [data-testid="stMetricValue"] div {
            color: #202944 !important;
        }
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        #MainMenu,
        footer {
            display: none !important;
        }
        header[data-testid="stHeader"] {
            height: 0;
            background: transparent;
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: #e4dfd6 !important;
            border-radius: 1.1rem !important;
            background: rgba(255, 255, 255, 0.96);
            box-shadow: 0 8px 24px rgba(32, 41, 68, 0.06);
        }
        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div,
        [data-baseweb="base-input"],
        input {
            background: #ffffff !important;
            color: var(--ink) !important;
        }
        [data-baseweb="select"] span,
        [data-baseweb="select"] div {
            color: var(--ink) !important;
        }
        [role="listbox"], [role="option"] {
            background: #ffffff !important;
            color: var(--ink) !important;
        }
        .block-container {
            max-width: 1100px;
            padding-top: 1.1rem;
            padding-bottom: 3rem;
        }
        h2 {
            color: var(--ink);
            letter-spacing: -0.02em;
        }
        .hero-card {
            position: relative;
            overflow: hidden;
            padding: 2.15rem 2.3rem;
            margin-bottom: 1.15rem;
            border: 1px solid rgba(255, 255, 255, 0.22);
            border-radius: 1.45rem;
            background: var(--navy);
            box-shadow: 0 18px 42px rgba(31, 42, 68, 0.18);
        }
        .hero-card::after {
            content: "";
            position: absolute;
            width: 180px;
            height: 180px;
            right: -45px;
            top: -70px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.10);
        }
        .hero-brand {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            margin-bottom: 1rem;
            padding: 0.35rem 0.7rem;
            border: 1px solid rgba(255, 255, 255, 0.24);
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.10);
            color: #ffffff;
            font-size: 0.78rem;
            font-weight: 750;
        }
        .hero-eyebrow {
            margin-bottom: 0.55rem;
            color: #ddd9ff;
            font-size: 0.76rem;
            font-weight: 750;
            letter-spacing: 0.04em;
        }
        .hero-card h1 {
            margin: 0;
            color: #ffffff !important;
            font-size: clamp(2rem, 4vw, 2.8rem);
            letter-spacing: -0.035em;
        }
        .hero-card p {
            max-width: 720px;
            margin: 0.65rem 0 0;
            color: #f1f3ff !important;
            font-size: 1.06rem;
            line-height: 1.55;
        }
        [data-testid="stMetric"] {
            padding: 0.85rem 0.95rem;
            border: 1px solid #e6e1d8;
            border-radius: 0.95rem;
            background: #ffffff;
            box-shadow: 0 4px 14px rgba(32, 41, 68, 0.05);
        }
        .context-summary {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin: 0.75rem 0 0.15rem;
        }
        .context-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.38rem 0.65rem;
            border: 1px solid #e1ddd5;
            border-radius: 999px;
            background: #faf9f6;
            color: #4d5668;
            font-size: 0.78rem;
            font-weight: 700;
        }
        .mission-card {
            margin: 0.75rem 0;
            padding: 1.05rem 1.1rem 1.08rem;
            border: 1px solid var(--line);
            border-left-width: 5px;
            border-radius: 1rem;
            background: var(--surface);
            box-shadow: 0 6px 18px rgba(32, 41, 68, 0.07);
        }
        .mission-featured {
            border-color: #cfc8f6;
            background: linear-gradient(135deg, #ffffff 0%, #f4f2ff 100%);
            box-shadow: 0 10px 26px rgba(77, 66, 190, 0.13);
        }
        .mission-featured .mission-number::after {
            content: "เริ่มตรงนี้";
            margin-left: 0.45rem;
            padding: 0.16rem 0.42rem;
            border-radius: 999px;
            background: #e8e5ff;
            color: #463bb0;
            font-size: 0.62rem;
            letter-spacing: 0;
        }
        .mission-integrated {
            margin: 0 0 0.45rem;
            padding: 0.2rem 0 0.72rem;
            border: 0;
            border-bottom: 1px solid #ece8e1;
            border-radius: 0;
            background: transparent;
            box-shadow: none;
        }
        .mission-integrated.mission-featured {
            margin: -0.25rem -0.25rem 0.65rem;
            padding: 0.85rem 0.9rem;
            border: 1px solid #cfc8f6;
            border-left: 5px solid var(--must);
            border-radius: 0.9rem;
            background: linear-gradient(135deg, #ffffff 0%, #f4f2ff 100%);
            box-shadow: 0 8px 20px rgba(77, 66, 190, 0.10);
        }
        .mission-compact {
            margin: 0.55rem 0;
            padding: 0.78rem 0.9rem 0.82rem;
            box-shadow: none;
        }
        .mission-compact .mission-card-top { margin-bottom: 0.35rem; }
        .mission-compact .mission-title { margin-bottom: 0.45rem; font-size: 0.98rem; }
        .mission-compact .mission-meta { margin-bottom: 0.45rem; }
        .mission-compact .mission-reason { padding-top: 0.48rem; font-size: 0.82rem; }
        .mission-must { border-left-color: var(--must); }
        .mission-should { border-left-color: var(--should); }
        .mission-could { border-left-color: var(--could); }
        .mission-card-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            margin-bottom: 0.55rem;
        }
        .mission-number {
            color: #82918c;
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.1em;
        }
        .priority-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.58rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }
        .priority-must { color: var(--must); background: var(--must-soft); }
        .priority-should { color: var(--should); background: var(--should-soft); }
        .priority-could { color: var(--could); background: var(--could-soft); }
        .mission-title {
            margin-bottom: 0.65rem;
            color: #1c2439;
            font-size: 1.04rem;
            font-weight: 760;
            line-height: 1.35;
        }
        .mission-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin-bottom: 0.7rem;
        }
        .meta-chip {
            padding: 0.24rem 0.52rem;
            border: 1px solid #e1ded7;
            border-radius: 0.5rem;
            background: #faf9f6;
            color: #4d5668;
            font-size: 0.78rem;
            font-weight: 650;
        }
        .mission-reason {
            padding-top: 0.65rem;
            border-top: 1px solid #ece8e1;
            color: var(--muted);
            font-size: 0.88rem;
            line-height: 1.48;
            display: -webkit-box;
            overflow: hidden;
            -webkit-box-orient: vertical;
            -webkit-line-clamp: 2;
        }
        .avoid-card {
            margin-top: 1rem;
            padding: 1rem 1.05rem;
            border: 1px solid #efc9c4;
            border-radius: 1rem;
            background: #fff5f3;
        }
        .avoid-title {
            margin-bottom: 0.5rem;
            color: #8f2118;
            font-weight: 800;
        }
        .avoid-card ul {
            margin: 0;
            padding-left: 1.2rem;
            color: #6f3d37;
        }
        .avoid-card li + li { margin-top: 0.35rem; }
        .placeholder-card {
            margin-top: 0.8rem;
            padding: 0.9rem 1rem;
            border: 1px dashed #ccd8d4;
            border-radius: 0.8rem;
            background: #f8faf9;
            color: #62716c;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        .focus-strip {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            margin: 0.3rem 0 0.85rem;
            padding: 0.65rem 0.75rem;
            border-radius: 0.7rem;
            border: 1px solid #d6efe6;
            background: #eef9f5;
            color: #245c4d;
            font-size: 0.84rem;
            font-weight: 650;
        }
        .focus-strip strong { color: #0d604c; }
        [data-testid="stMain"] div[data-testid="stRadio"] > div {
            gap: 0.35rem;
        }
        [data-testid="stMain"] div[data-testid="stRadio"] label {
            padding: 0.28rem 0.5rem;
            border: 1px solid #d8d8d6;
            border-radius: 999px;
            background: #ffffff;
        }
        [data-testid="stMain"] div[data-testid="stRadio"] label:has(input:checked) {
            border-color: #64bda2;
            background: #e9f8f2;
            box-shadow: 0 0 0 1px rgba(15, 143, 112, 0.10);
        }
        [data-testid="stMain"] div[data-testid="stRadio"] label p {
            color: #626a78 !important;
            font-size: 0.82rem !important;
            font-weight: 700 !important;
        }
        [data-testid="stMain"] div[data-testid="stRadio"] label:has(input:checked) p {
            color: #11664f !important;
        }
        [data-testid="stMain"] div[data-testid="stRadio"] label:nth-of-type(2):has(input:checked) {
            border-color: #e7bd62;
            background: #fff4d8;
            box-shadow: 0 0 0 1px rgba(166, 93, 0, 0.10);
        }
        [data-testid="stMain"] div[data-testid="stRadio"] label:nth-of-type(2):has(input:checked) p {
            color: #815000 !important;
        }
        [data-testid="stMain"] div[data-testid="stRadio"] label:nth-of-type(3):has(input:checked) {
            border-color: #e49a92;
            background: #ffebe8;
            box-shadow: 0 0 0 1px rgba(201, 54, 43, 0.10);
        }
        [data-testid="stMain"] div[data-testid="stRadio"] label:nth-of-type(3):has(input:checked) p {
            color: #9f2d24 !important;
        }
        [data-testid="stMain"] div[data-testid="stRadio"] label:nth-of-type(4):has(input:checked) {
            border-color: #bfa7e8;
            background: #f3eaff;
            box-shadow: 0 0 0 1px rgba(112, 36, 217, 0.10);
        }
        [data-testid="stMain"] div[data-testid="stRadio"] label:nth-of-type(4):has(input:checked) p {
            color: #6632a0 !important;
        }
        [data-testid="stMain"] div[data-testid="stRadio"] input { accent-color: var(--success); }
        .review-prompt {
            margin: 0 0 0.35rem;
            color: #677080;
            font-size: 0.76rem;
            font-weight: 700;
        }
        div[data-testid="stButton"] button[kind="primary"] {
            min-height: 2.85rem;
            border: 0;
            border-radius: 0.8rem;
            background: linear-gradient(100deg, #4b42d1 0%, #7024d9 100%);
            color: #ffffff !important;
            font-weight: 800;
            box-shadow: 0 8px 18px rgba(85, 55, 190, 0.22);
        }
        div[data-testid="stButton"] button[kind="primary"] p {
            color: #ffffff !important;
        }
        div[data-testid="stButton"] button[kind="primary"]:hover {
            filter: brightness(1.05);
            box-shadow: 0 10px 22px rgba(85, 55, 190, 0.28);
        }
        [data-testid="stProgress"] > div > div > div {
            background: linear-gradient(90deg, #4b42d1 0%, #0f8f70 100%) !important;
        }
        [data-testid="stProgress"] p {
            color: #343c50 !important;
            font-weight: 800 !important;
        }
        .recovery-note {
            margin: 0.8rem 0;
            padding: 0.85rem 0.95rem;
            border: 1px solid #bfd9e7;
            border-radius: 0.75rem;
            background: #f0f8fc;
            color: #315b70;
            font-size: 0.88rem;
            line-height: 1.5;
        }
        .plan-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
            margin: 0.25rem 0 0.75rem;
        }
        .plan-strip span {
            padding: 0.3rem 0.58rem;
            border-radius: 0.55rem;
            background: #f0edff;
            color: #443aa8;
            font-size: 0.76rem;
            font-weight: 700;
        }
        .plan-note {
            min-height: 98px;
            padding: 0.9rem 1rem;
            border: 1px solid #dde6e3;
            border-radius: 0.8rem;
            background: #fbfcfc;
        }
        .plan-note strong {
            display: block;
            margin-bottom: 0.35rem;
            color: #29483f;
        }
        .plan-note span {
            color: #65746f;
            font-size: 0.86rem;
            line-height: 1.45;
        }
        .placeholder-note {
            color: #66756f;
            font-style: italic;
        }
        [data-testid="stExpander"] {
            overflow: hidden;
            border: 1px solid #e3ded5 !important;
            border-radius: 1rem !important;
            background: #ffffff;
        }
        [data-testid="stExpander"] summary p {
            color: #352c91 !important;
            font-weight: 800 !important;
        }
        .plan-help {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            margin: 0.4rem 0 0.8rem;
            padding: 0.7rem 0.8rem;
            border: 1px solid #e4def8;
            border-radius: 0.75rem;
            background: #f7f5ff;
            color: #4c4670;
            font-size: 0.84rem;
        }
        .plan-table-shell {
            max-height: 370px;
            overflow: auto;
            border: 1px solid #e4e0d8;
            border-radius: 0.9rem;
            background: #ffffff;
        }
        .plan-table {
            width: 100%;
            min-width: 980px;
            border-collapse: separate;
            border-spacing: 0;
            color: #252d40;
            font-size: 0.8rem;
        }
        .plan-table th {
            position: sticky;
            top: 0;
            z-index: 1;
            padding: 0.72rem 0.75rem;
            border-bottom: 1px solid #ddd7cd;
            background: #f0edf9;
            color: #3b347d;
            font-weight: 800;
            text-align: left;
            white-space: nowrap;
        }
        .plan-table td {
            padding: 0.68rem 0.75rem;
            border-bottom: 1px solid #eeeae3;
            background: #ffffff;
            color: #384052;
            line-height: 1.4;
            vertical-align: top;
        }
        .plan-table tr:nth-child(even) td { background: #fbfaf7; }
        .plan-table tr:last-child td { border-bottom: 0; }
        .plan-mode {
            display: inline-flex;
            padding: 0.22rem 0.48rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 800;
            white-space: nowrap;
        }
        .plan-mode-green { color: #12654f; background: #e8f7f1; }
        .plan-mode-yellow { color: #8a5900; background: #fff4d8; }
        .plan-mode-red { color: #9f2d24; background: #ffebe8; }
        .plan-mode-recovery { color: #24647f; background: #e8f5fb; }
        .plan-mode-study { color: #4938a8; background: #eeeaff; }
        .sidebar-brand {
            margin-bottom: 0.7rem;
            padding: 0.7rem 0.25rem 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.13);
        }
        .sidebar-brand strong {
            display: block;
            color: #ffffff;
            font-size: 1.02rem;
        }
        .sidebar-brand span {
            display: block;
            margin-top: 0.25rem;
            color: #c9cfdd;
            font-size: 0.76rem;
        }
        .section-hero {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
            padding: 1.35rem 1.45rem;
            border-radius: 1.15rem;
            background: var(--navy);
            box-shadow: 0 12px 30px rgba(31, 42, 68, 0.16);
        }
        .section-hero-icon {
            display: grid;
            width: 3rem;
            height: 3rem;
            flex: 0 0 3rem;
            place-items: center;
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 0.9rem;
            background: rgba(255, 255, 255, 0.10);
            font-size: 1.35rem;
        }
        .section-kicker {
            margin-bottom: 0.2rem;
            color: #c9cfdd;
            font-size: 0.72rem;
            font-weight: 750;
            letter-spacing: 0.04em;
        }
        .section-hero h1 {
            margin: 0;
            color: #ffffff !important;
            font-size: clamp(1.65rem, 3vw, 2.25rem);
        }
        .section-hero p {
            margin: 0.28rem 0 0;
            color: #e6e9f2 !important;
            line-height: 1.45;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 0.8rem 0 1rem;
        }
        .summary-card {
            min-height: 112px;
            padding: 0.9rem 0.95rem;
            border: 1px solid var(--line);
            border-radius: 0.95rem;
            background: #ffffff;
            box-shadow: 0 6px 18px rgba(31, 42, 68, 0.06);
        }
        .summary-card span,
        .summary-card small {
            display: block;
            color: var(--muted);
            font-size: 0.75rem;
        }
        .summary-card strong {
            display: -webkit-box;
            overflow: hidden;
            margin: 0.42rem 0 0.28rem;
            color: var(--navy);
            font-size: 1.05rem;
            line-height: 1.25;
            -webkit-box-orient: vertical;
            -webkit-line-clamp: 2;
        }
        .daily-layout {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.8rem;
        }
        .daily-card {
            padding: 1rem;
            border: 1px solid var(--line);
            border-radius: 1rem;
            background: #ffffff;
            box-shadow: 0 6px 18px rgba(31, 42, 68, 0.06);
        }
        .daily-card-wide { grid-column: 1 / -1; }
        .daily-card h3 { margin: 0 0 0.7rem; color: var(--navy); font-size: 1rem; }
        .daily-card p { margin: 0.2rem 0 0.45rem; line-height: 1.5; }
        .daily-card small { color: var(--muted); }
        .daily-row {
            display: grid;
            grid-template-columns: minmax(145px, 0.8fr) minmax(0, 2fr);
            gap: 0.8rem;
            padding: 0.7rem 0;
            border-top: 1px solid #ece9e2;
        }
        .daily-row:first-of-type { border-top: 0; }
        .daily-row strong,
        .daily-row small { display: block; }
        .daily-row small { margin-top: 0.2rem; color: var(--muted); }
        .daily-time { color: var(--primary-deep); font-size: 0.82rem; font-weight: 750; }
        .settings-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.8rem;
        }
        .settings-card {
            padding: 1rem;
            border: 1px solid var(--line);
            border-radius: 0.95rem;
            background: #ffffff;
            box-shadow: 0 6px 18px rgba(31, 42, 68, 0.06);
        }
        .settings-card span,
        .settings-card strong { display: block; }
        .settings-card span { color: var(--muted); font-size: 0.76rem; }
        .settings-card strong { margin-top: 0.35rem; color: var(--navy); }
        .empty-state {
            padding: 1.2rem;
            border: 1px dashed #cfc9be;
            border-radius: 1rem;
            background: #ffffff;
            color: var(--muted);
            text-align: center;
        }
        .app-footer {
            margin-top: 1.2rem;
            padding: 0.9rem 1rem;
            border-top: 1px solid #e1ddd5;
            color: #697181;
            font-size: 0.78rem;
            text-align: center;
        }
        @media (max-width: 720px) {
            .block-container { padding-top: 0.8rem; }
            .hero-card { padding: 1.4rem 1.25rem; }
            .mission-card { padding: 0.9rem; }
            .review-result-grid { grid-template-columns: 1fr; }
            .summary-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .daily-layout,
            .settings-grid { grid-template-columns: 1fr; }
            .daily-card-wide { grid-column: auto; }
            .daily-row { grid-template-columns: 1fr; gap: 0.25rem; }
            [data-testid="stMetric"] { padding: 0.7rem 0.75rem; }
            .plan-table-shell { max-height: 330px; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

storage_issues: list[str] = []
try:
    ensure_daily_log_file()
except (OSError, ValueError) as error:
    storage_issues.append(str(error))
try:
    ensure_daily_plan_file()
except (OSError, ValueError) as error:
    storage_issues.append(str(error))

seed_data, data_issues = load_seed_data()
data_issues.extend(storage_issues)

with st.sidebar:
    st.html(
        """
        <div class="sidebar-brand">
            <strong>🧭 ผู้ช่วยจัดลำดับชีวิต</strong>
            <span>เลือกมุมมองที่ต้องการใช้วันนี้</span>
        </div>
        """
    )
    active_section = st.radio(
        "เมนูหลัก",
        NAV_SECTIONS,
        index=0,
        label_visibility="collapsed",
        key="main_navigation",
    )
    st.divider()
    st.markdown("### ความพร้อมวันนี้")
    selected_date = st.date_input("วันที่วางแผน", value=date.today())
    day_mode = st.selectbox(
        "ระดับพลังเริ่มต้น",
        ("Green Day", "Yellow Day", "Red Day"),
        format_func=lambda value: THAI_DAY_MODE.get(value, value),
    )
    st.caption("ข้อมูลทั้งหมดเก็บไว้ในเครื่องนี้")

missions, do_not_do, mission_context = generate_today_missions(seed_data, selected_date, day_mode)
saved_result = st.session_state.get("latest_review_summary")
saved_for_date = (
    saved_result
    if saved_result and saved_result["date"] == selected_date.isoformat()
    else None
)

if data_issues:
    st.warning("ระบบกำลังใช้ข้อมูลสำรองที่ปลอดภัย: " + "; ".join(thai_data_issue(issue) for issue in data_issues))

if active_section == "🌤 แผนพรุ่งนี้":
    st.html(section_header_html("แผนพรุ่งนี้", "มองก้าวถัดไปแบบพอดี ไม่เร่งชดเชยสิ่งที่พลาด", "🌤"))
    if saved_for_date and saved_for_date.get("tomorrow_plan"):
        tomorrow_plan = saved_for_date["tomorrow_plan"]
        st.html(
            f"""
            <div class="plan-strip">
                <span>พรุ่งนี้ · {tomorrow_plan['date']:%d/%m/%Y}</span>
                <span>{escape(THAI_DAY_MODE.get(tomorrow_plan['mode'], tomorrow_plan['mode']))}</span>
                <span>{saved_for_date['plan_rows']} ภารกิจ</span>
            </div>
            """
        )
        if tomorrow_plan["recovery_note"]:
            st.html(
                f'<div class="recovery-note">{escape(thai_result_text(tomorrow_plan["recovery_note"]))}</div>'
            )
        for index, mission in enumerate(tomorrow_plan["missions"], start=1):
            st.html(mission_card_html(mission, index, compact=True))
        tomorrow_avoid_items = "".join(
            f"<li>{escape(thai_do_not(item))}</li>" for item in tomorrow_plan["do_not_do"]
        )
        st.html(
            f"""
            <div class="avoid-card">
                <div class="avoid-title">⊘ พรุ่งนี้ยังไม่ควรทำ</div>
                <ul>{tomorrow_avoid_items}</ul>
            </div>
            """
        )
    else:
        st.html('<div class="empty-state">บันทึกผลภารกิจวันนี้ก่อน แล้วแผนพรุ่งนี้จะปรากฏตรงนี้</div>')
    st.html('<div class="app-footer">แผนจะยึดความปลอดภัยและพลังจริงของวันนี้เป็นหลัก</div>')
    st.stop()

if active_section == "🕒 แผนละเอียดรายวัน":
    st.html(section_header_html("แผนละเอียดรายวัน", "ดูช่วงเวลา งาน อาหารทั่วไป และระดับการเคลื่อนไหวในมุมมองเดียว", "🕒"))
    st.html(
        f"""
        <div class="context-summary">
            <span class="context-chip">📅 {selected_date:%d/%m/%Y}</span>
            <span class="context-chip">● {escape(THAI_DAY_MODE.get(day_mode, day_mode))}</span>
            <span class="context-chip">◷ {escape(thai_shift(mission_context['shift']))}</span>
        </div>
        """
    )
    st.html(daily_detail_html(missions, seed_data, day_mode))
    st.info("อาหารและการเคลื่อนไหวเป็นการวางแผนทั่วไปเท่านั้น ไม่ใช่การวินิจฉัยหรือคำแนะนำการรักษา")
    st.html('<div class="app-footer">ปรับตามเวลาจริงและพลังของคุณได้เสมอ</div>')
    st.stop()

if active_section == "📅 ภาพรวม 30 วัน":
    st.html(section_header_html("ภาพรวม 30 วัน", "ใช้เป็นแผนที่คร่าว ๆ แล้วปรับจากผลจริงของแต่ละวัน", "📅"))
    rough_plan = generate_rough_30_day_plan(
        seed_data, selected_date, day_mode, saved_for_date
    )
    localized_rough_plan = localize_rough_plan(rough_plan)
    st.html(
        '<div class="plan-help">✦ <span>ตารางนี้แยกออกจากหน้าหลัก เพื่อให้การใช้งานประจำวันสั้นและไม่หนักสายตา</span></div>'
    )
    st.html(rough_plan_table_html(localized_rough_plan))
    st.caption("แผน 30 วันเป็นแนวทางแบบยืดหยุ่น ไม่ใช่คำสั่งตายตัว")
    st.html('<div class="app-footer">ผลจริงและความปลอดภัยของแต่ละวันสำคัญกว่าแผน</div>')
    st.stop()

if active_section == "⚙️ ตั้งค่าชีวิต":
    st.html(section_header_html("ตั้งค่าชีวิต", "สรุปค่าพื้นฐานจากไฟล์ข้อมูลในเครื่องของคุณ", "⚙️"))
    st.html(settings_summary_html(seed_data))
    st.info("มุมมองนี้แสดงข้อมูลเดิมแบบอ่านอย่างเดียว หากต้องการแก้ไขให้แก้ไฟล์ข้อมูลในโฟลเดอร์ data")
    st.html('<div class="app-footer">ยังไม่มีบัญชีผู้ใช้ ฐานข้อมูล หรือการเชื่อมต่อระบบภายนอก</div>')
    st.stop()

st.html(section_header_html("วันนี้ต้องทำอะไร", "เริ่มจากสิ่งสำคัญ ทำตามพลังจริง แล้วบันทึกผลในจุดเดียว", "🏠"))
st.html(dashboard_summary_html(missions, day_mode, do_not_do, saved_for_date))
st.html(
    f"""
    <div class="context-summary">
        <span class="context-chip">📅 {selected_date:%d/%m/%Y}</span>
        <span class="context-chip">● {escape(THAI_DAY_MODE.get(day_mode, day_mode))}</span>
        <span class="context-chip">◷ {escape(thai_shift(mission_context['shift']))}</span>
        <span class="context-chip">📚 {escape(thai_exam_context(mission_context['exam']))}</span>
    </div>
    """
)

with st.container(border=True):
    st.subheader("🎯 ภารกิจวันนี้")
    st.caption(f"{len(missions)} ภารกิจ · เลือกผลไว้ใต้แต่ละการ์ดได้ทันที")
    st.html(
        '<div class="focus-strip">◎ <span><strong>เริ่มจากการ์ดแรก</strong> แล้วค่อยดูว่าพลังยังพอสำหรับงานถัดไปไหม</span></div>'
    )

    review_entries: list[dict[str, Any]] = []
    status_options = ("DONE", "PARTIAL", "MISSED", "PROBLEM")

    for index, mission in enumerate(missions, start=1):
        review_key = mission_review_key(selected_date, index, mission)
        with st.container(border=True):
            st.html(mission_card_html(mission, index, integrated=True))
            st.html('<div class="review-prompt">วันนี้ทำภารกิจนี้ได้แค่ไหน?</div>')
            status = st.radio(
                f"ผลของภารกิจที่ {index}",
                status_options,
                horizontal=True,
                key=f"status_{review_key}",
                label_visibility="collapsed",
                format_func=lambda value: THAI_STATUS.get(value, value),
            )

            actual_value: float | None = None
            actual_unit = ""
            missed_reason = ""
            problem_issue = ""
            problem_note = ""

            if status == "PARTIAL":
                detail_amount, detail_unit = st.columns((1.2, 0.8))
                with detail_amount:
                    actual_value = st.number_input(
                        "ทำได้จริงเท่าไร",
                        min_value=0.0,
                        step=5.0,
                        key=f"actual_{review_key}",
                    )
                with detail_unit:
                    actual_unit = st.selectbox(
                        "หน่วย",
                        ("minutes", "items", "percent", "other"),
                        key=f"unit_{review_key}",
                        format_func=lambda value: THAI_UNIT.get(value, value),
                    )
            elif status == "MISSED":
                missed_reason = st.selectbox(
                    "เหตุผลที่ไม่ได้ทำ",
                    (
                        "Not enough time",
                        "Higher-priority work",
                        "Project displaced Must Do",
                        "Low energy",
                        "Forgot",
                        "Other",
                    ),
                    key=f"missed_reason_{review_key}",
                    format_func=lambda value: THAI_MISSED_REASON.get(value, value),
                )
            elif status == "PROBLEM":
                problem_issue = st.selectbox(
                    "ปัญหาที่พบ",
                    (
                        "Heavy workload",
                        "Very heavy shift",
                        "Low energy",
                        "Physical discomfort",
                        "No sleep",
                        "Faint or dizzy",
                        "Sick or unwell",
                        "Unsafe condition",
                        "Unexpected task",
                        "Technical issue",
                        "Other",
                    ),
                    key=f"problem_issue_{review_key}",
                    format_func=lambda value: THAI_PROBLEM_ISSUE.get(value, value),
                )
                problem_note = st.text_input(
                    "บันทึกสั้น ๆ",
                    max_chars=160,
                    key=f"problem_note_{review_key}",
                    placeholder="เช่น เวียนหัวหลังเลิกเวร",
                )

            review_entries.append(
                {
                    "mission": mission,
                    "mission_id": review_key,
                    "status": status,
                    "actual_value": actual_value,
                    "actual_unit": actual_unit,
                    "missed_reason": missed_reason,
                    "problem_issue": problem_issue,
                    "problem_note": problem_note,
                }
            )

    avoid_items = "".join(f"<li>{escape(thai_do_not(item))}</li>" for item in do_not_do)
    st.html(
        f"""
        <div class="avoid-card">
            <div class="avoid-title">⊘ วันนี้ยังไม่ควรทำ</div>
            <ul>{avoid_items}</ul>
        </div>
        """
    )

    save_review = st.button(
        "บันทึกผลวันนี้",
        type="primary",
        use_container_width=True,
    )
    if save_review:
            partial_without_amount = any(
                entry["status"] == "PARTIAL" and not entry["actual_value"]
                for entry in review_entries
            )
            if partial_without_amount:
                st.error("กรุณาระบุจำนวนที่ทำได้จริงให้มากกว่า 0 สำหรับภารกิจที่ทำบางส่วน")
            else:
                created_at = datetime.now().astimezone().isoformat(timespec="seconds")
                review_result = calculate_daily_review(
                    review_entries, day_mode, mission_context["workload"]
                )
                tomorrow_plan = generate_tomorrow_plan(
                    seed_data,
                    selected_date,
                    review_entries,
                    review_result,
                    mission_context,
                )
                log_rows: list[dict[str, str]] = []
                for entry, mission_score in zip(
                    review_entries, review_result["mission_scores"]
                ):
                    mission = entry["mission"]
                    status = entry["status"]
                    actual_value = ""
                    unit = ""
                    reason = ""
                    symptom = ""
                    note = ""

                    if status == "DONE":
                        actual_value = mission["amount"]
                    elif status == "PARTIAL":
                        actual_value = f"{entry['actual_value']:g}"
                        unit = entry["actual_unit"]
                    elif status == "MISSED":
                        reason = entry["missed_reason"]
                    elif status == "PROBLEM":
                        reason = "Problem reported"
                        symptom = entry["problem_issue"]
                        note = entry["problem_note"]

                    log_rows.append(
                        {
                            "date": selected_date.isoformat(),
                            "mission_id": entry["mission_id"],
                            "status": status,
                            "planned_value": mission["amount"],
                            "actual_value": actual_value,
                            "unit": unit,
                            "reason": reason,
                            "energy": day_mode.replace(" Day", ""),
                            "workload": mission_context["workload"],
                            "symptom": symptom,
                            "score": str(mission_score),
                            "note": note,
                            "created_at": created_at,
                        }
                    )

                plan_rows = tomorrow_plan_rows(tomorrow_plan)
                review_saved = False
                try:
                    append_daily_log_rows(log_rows)
                    review_saved = True
                    append_daily_plan_rows(plan_rows)
                except (OSError, ValueError) as error:
                    if review_saved:
                        st.error(f"บันทึกผลวันนี้แล้ว แต่บันทึกแผนพรุ่งนี้ไม่สำเร็จ: {thai_data_issue(str(error))}")
                    else:
                        st.error(f"บันทึกผลวันนี้ไม่สำเร็จ: {thai_data_issue(str(error))}")
                else:
                    counts = {
                        status: sum(entry["status"] == status for entry in review_entries)
                        for status in status_options
                    }
                    st.session_state["latest_review_summary"] = {
                        "date": selected_date.isoformat(),
                        "rows": len(log_rows),
                        "counts": counts,
                        "daily_score": review_result["daily_score"],
                        "day_mode": review_result["day_mode"],
                        "main_blocker": review_result["main_blocker"],
                        "interpretation": review_result["interpretation"],
                        "health_caution": review_result["health_caution"],
                        "tomorrow_plan": tomorrow_plan,
                        "plan_rows": len(plan_rows),
                    }

    saved_summary = st.session_state.get("latest_review_summary")
    if saved_summary and saved_summary["date"] == selected_date.isoformat():
        st.success("บันทึกผลวันนี้แล้ว")
        with st.container(border=True):
            st.markdown("### ✨ สรุปวันนี้")
            st.progress(
                saved_summary["daily_score"] / 100,
                text=f"คะแนนวันนี้ {saved_summary['daily_score']}/100",
            )
            score_column, mode_column = st.columns(2)
            score_column.metric("คะแนนวันนี้", f"{saved_summary['daily_score']}/100")
            mode_column.metric(
                "โหมดวันนี้",
                THAI_DAY_MODE.get(saved_summary["day_mode"], saved_summary["day_mode"]),
            )
            st.markdown(
                f"**ปัญหาหลัก:** {thai_result_text(saved_summary['main_blocker'])}"
            )
            st.caption(thai_result_text(saved_summary["interpretation"]))
            status_line = " · ".join(
                f"{THAI_STATUS[status]} {saved_summary['counts'][status]}"
                for status in status_options
                if saved_summary["counts"][status]
            )
            if status_line:
                st.caption(status_line)
            if saved_summary["health_caution"]:
                st.warning(thai_result_text(saved_summary["health_caution"]))
    else:
        st.caption("เลือกผลให้ครบ แล้วกดปุ่มสีม่วงเพื่อดูคะแนนและแผนพรุ่งนี้")

st.html(
    '<div class="app-footer">ข้อมูลอยู่ในเครื่องของคุณ · ระบบช่วยวางแผน ไม่ใช่คำแนะนำทางการแพทย์</div>'
)
