"""Deterministic generated views for School Learning."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path

from .core import (
    SemesterWorkspace,
    Workspace,
    _atomic_term_bytes,
    _atomic_write_bytes,
    _confined_path,
    _date,
    _load_state,
    _school_timestamp_datetime,
    _semester_generated_dir,
    _source_observation_recency_key,
    _term_confined_path,
    load_semester,
    workspace,
)

_PLANNING_ACTIVE_ASSESSMENT_STATUSES = {"upcoming", "available", "in-progress"}
_PLANNING_MATERIAL_KINDS = {"reading", "listening-reference", "lab-field-guide"}
_CANONICAL_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_LEGACY_COMPACT_MERIDIEM = re.compile(
    r"^[A-Z][a-z]{2} (?:[1-9]|[12]\d|3[01]), \d{4}, (?:[1-9]|1[0-2]):[0-5]\d(?:am|pm)$"
)
_LEGACY_SPACED_MERIDIEM = re.compile(
    r"^[A-Z][a-z]{2} (?:[1-9]|[12]\d|3[01]), \d{4}, (?:[1-9]|1[0-2]):[0-5]\d (?:AM|PM)$"
)


def _claim_text(claim: dict[str, object]) -> str:
    return (
        f"{claim['field']}={claim['value']} — {claim['status']} — "
        f"source: {claim['source']} — observed: {claim['observed_at']}"
    )


def render_course(ws: Workspace) -> tuple[Path, Path]:
    state = _load_state(ws)
    course = state.course
    materials = state.materials["materials"]
    topics = state.topics["topics"]
    sessions = list(state.sessions)
    core = state.core

    topic_rows = "".join(
        "<tr>"
        f"<td><code>{escape(item['id'])}</code></td>"
        f"<td>{escape(item['title'])}</td>"
        f"<td>{escape(item['status'])}</td>"
        f"<td>{escape(item['last_outcome'] or '—')}</td>"
        f"<td>{item['next_review_priority']}</td>"
        f"<td>{escape(item['note'] or '')}</td>"
        "</tr>"
        for item in sorted(topics, key=lambda value: (-value["next_review_priority"], value["id"]))
    ) or '<tr><td colspan="6">No topics recorded.</td></tr>'
    material_items = "".join(
        "<li>"
        f"<code>{escape(item['id'])}</code> — {escape(item['title'])} — "
        f"{escape(item.get('kind', 'unspecified'))} / {escape(item.get('status', 'unknown'))} — "
        f"{item['bytes']} bytes"
        + (f" — date {escape(item['relevant_date'])}" if item.get("relevant_date") else "")
        + "</li>"
        for item in materials
    ) or "<li>No materials recorded.</li>"
    recent_items = "".join(
        f"<li><code>{escape(item['session_id'])}</code> — {escape(item['topic_id'])} — {escape(item['outcome'])}</li>"
        for item in sessions[-10:][::-1]
    ) or "<li>No study sessions recorded.</li>"

    if core is None:
        profile = "<p>Legacy v0.1 course; no v0.2 profile registered.</p>"
        assessment_items = "<li>No assessments recorded.</li>"
        policy_items = "<li>No policies recorded.</li>"
    else:
        tags = ", ".join(escape(item) for item in core["capability_tags"]) or "none"
        sources = "".join(
            f"<li><code>{escape(item['id'])}</code> — {escape(item['title'])} — "
            f"{escape(item['reference'])} — {escape(item['status'])}</li>"
            for item in core["sources"]
        ) or "<li>No authoritative source descriptors recorded.</li>"
        metadata = "".join(
            f"<li><code>{escape(key)}</code>: {escape(value)}</li>"
            for key, value in sorted(core["metadata"].items())
        ) or "<li>No additional course metadata recorded.</li>"
        profile = f"<p>Capabilities: {tags}</p><h3>Sources</h3><ul>{sources}</ul><h3>Metadata</h3><ul>{metadata}</ul>"
        assessment_items = "".join(
            "<li>"
            f"<code>{escape(item['id'])}</code> — {escape(item['title'])} — "
            f"{escape(item['type'])} / {escape(item['status'])}"
            + (f" — weight {escape(item['weight'])}" if item["weight"] else "")
            + (f" — points {escape(item['points'])}" if item["points"] else "")
            + (f" — XP {escape(item['xp'])}" if item["xp"] else "")
            + "<ul>"
            + ("".join(f"<li>{escape(_claim_text(claim))}</li>" for claim in item["claims"]) or "<li>No schedule claims.</li>")
            + "</ul></li>"
            for item in core["assessments"]
        ) or "<li>No assessments recorded.</li>"
        policy_items = "".join(
            "<li>"
            f"<code>{escape(item['id'])}</code> — {escape(item['title'])} — "
            f"{escape(item['category'])} / {escape(item['status'])}<ul>"
            + "".join(f"<li>{escape(_claim_text(claim))}</li>" for claim in item["claims"])
            + "</ul></li>"
            for item in core["policies"]
        ) or "<li>No policies recorded.</li>"

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(course['title'])} — School Learning</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 1080px; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }}
table {{ border-collapse: collapse; width: 100%; }} th, td {{ border: 1px solid #bbb; padding: .5rem; text-align: left; }}
code {{ white-space: nowrap; }} .meta {{ color: #555; }}
</style>
</head>
<body>
<h1>{escape(course['title'])}</h1>
<p class="meta"><code>{escape(course['course_id'])}</code> · <code>{escape(course['term'])}</code></p>
<h2>Course Profile</h2>{profile}
<h2>Materials</h2><ul>{material_items}</ul>
<h2>Assessments and Schedule Claims</h2><ul>{assessment_items}</ul>
<h2>Policies and Conflicts</h2><ul>{policy_items}</ul>
<h2>Learning Review</h2>
<table><thead><tr><th>ID</th><th>Topic</th><th>Status</th><th>Last outcome</th><th>Priority</th><th>Note</th></tr></thead><tbody>{topic_rows}</tbody></table>
<h2>Recent sessions</h2><ul>{recent_items}</ul>
</body>
</html>
"""
    review_lines = [
        f"# {course['title']} Review",
        "",
        f"Course: `{course['course_id']}`  ",
        f"Term: `{course['term']}`",
        "",
        "## Prioritized Topics",
        "",
    ]
    ordered = sorted(topics, key=lambda value: (-value["next_review_priority"], value["id"]))
    if ordered:
        for item in ordered:
            review_lines.append(
                f"- `{item['id']}` — {item['title']} — status `{item['status']}` — "
                f"outcome `{item['last_outcome'] or 'none'}` — priority `{item['next_review_priority']}`"
            )
    else:
        review_lines.append("- No topics recorded.")
    review_lines += ["", "## Recent Sessions", ""]
    if sessions:
        for item in sessions[-10:][::-1]:
            review_lines.append(
                f"- `{item['session_id']}` — `{item['topic_id']}` — `{item['outcome']}` — {item['note']}"
            )
    else:
        review_lines.append("- No sessions recorded.")
    review_lines.append("")

    generated = ws.course_dir / "generated"
    html_path = _confined_path(
        ws, generated / "course-home.html", label="generated HTML destination",
        regular_if_present=True,
    )
    review_path = _confined_path(
        ws, generated / "review.md", label="generated Markdown destination",
        regular_if_present=True,
    )
    _atomic_write_bytes(ws, html_path, html.encode("utf-8"))
    _atomic_write_bytes(ws, review_path, "\n".join(review_lines).encode("utf-8"))
    return html_path, review_path


def render_semester(sw: SemesterWorkspace) -> Path:
    semester = load_semester(sw)
    lines = [
        f"# {semester['title']} Semester Home",
        "",
        f"Term: `{semester['term']}`",
        "",
        "## Courses",
        "",
    ]
    states = []
    for course_id in semester["course_ids"]:
        state = _load_state(workspace(sw.data_root, sw.term, course_id))
        states.append(state)
        lines.append(f"- `{course_id}` — {state.course['title']}")
    if not states:
        lines.append("- No courses registered.")
    lines += ["", "## Known Assessments", ""]
    assessments = []
    for state in states:
        if state.core is None:
            continue
        for item in state.core["assessments"]:
            assessments.append((state.course["course_id"], item))
    if assessments:
        for course_id, item in sorted(assessments, key=lambda value: (value[0], value[1]["id"])):
            lines.append(
                f"- `{course_id}` / `{item['id']}` — {item['title']} — `{item['status']}`"
            )
            for claim in item["claims"]:
                lines.append(f"  - {_claim_text(claim)}")
    else:
        lines.append("- No assessments recorded.")
    lines += ["", "## Unresolved or Conflicted Information", ""]
    unresolved = []
    for state in states:
        if state.core is None:
            continue
        course_id = state.course["course_id"]
        for kind in ("assessments", "policies"):
            for item in state.core[kind]:
                for claim in item["claims"]:
                    if claim["status"] in {"provisional", "conflicted"}:
                        unresolved.append((course_id, kind[:-1], item["id"], claim))
    if unresolved:
        for course_id, kind, item_id, claim in sorted(
            unresolved, key=lambda value: (value[0], value[1], value[2], value[3]["id"])
        ):
            lines.append(f"- `{course_id}` / {kind} `{item_id}` — {_claim_text(claim)}")
    else:
        lines.append("- No provisional or conflicted claims recorded.")
    lines.append("")
    destination = _term_confined_path(
        sw,
        _semester_generated_dir(sw) / "semester-home.md",
        label="semester home destination",
        regular_if_present=True,
    )
    _atomic_term_bytes(sw, destination, "\n".join(lines).encode("utf-8"))
    return destination


def _supported_planning_value(
    value: object,
) -> tuple[tuple[str, date | datetime], date] | None:
    if not isinstance(value, str):
        return None
    try:
        if _CANONICAL_DATE.fullmatch(value):
            _date(value, "planning date")
            parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
            return ("date", parsed_date), parsed_date
        if "T" in value:
            parsed = _school_timestamp_datetime(value, "planning timestamp")
            return ("instant", parsed.astimezone(timezone.utc)), parsed.date()
        if _LEGACY_COMPACT_MERIDIEM.fullmatch(value):
            parsed = datetime.strptime(value, "%b %d, %Y, %I:%M%p")
            return ("legacy-local-time", parsed), parsed.date()
        if _LEGACY_SPACED_MERIDIEM.fullmatch(value):
            parsed = datetime.strptime(value, "%b %d, %Y, %I:%M %p")
            return ("legacy-local-time", parsed), parsed.date()
    except (ValueError, TypeError):
        return None
    return None


def _active_claims(item: dict[str, object], field: str) -> list[dict[str, object]]:
    return [
        claim
        for claim in item["claims"]  # type: ignore[index]
        if claim["field"] == field and claim["status"] != "superseded"
    ]


def _due_claims(item: dict[str, object]) -> list[dict[str, object]]:
    return [
        claim
        for claim in item["claims"]  # type: ignore[index]
        if claim["field"] in {"due", "due-at"} and claim["status"] != "superseded"
    ]


def _append_section(lines: list[str], title: str, entries: list[str], empty: str) -> None:
    lines.extend(["", f"## {title}", ""])
    lines.extend(entries if entries else [f"- {empty}"])


def _assessment_line(
    due: date, course_id: str, assessment: dict[str, object], *, prefix: str = ""
) -> str:
    marker = f"{prefix} " if prefix else ""
    return (
        f"- {marker}{due.isoformat()} — `{course_id}` / `{assessment['id']}` — "
        f"{assessment['title']} (`{assessment['status']}`)"
    )


def _conflict_line(
    course_id: str, assessment: dict[str, object], field: str, claims: list[dict[str, object]]
) -> str:
    values = "; ".join(
        f"{claim['field']}={claim['value']} — source: {claim['source']} — "
        f"observed: {claim['observed_at']}"
        for claim in sorted(claims, key=lambda item: str(item["id"]))
    )
    return (
        f"- `{course_id}` / `{assessment['id']}` — active `{field}` conflict: {values}"
    )


def render_plan(sw: SemesterWorkspace, as_of: str) -> Path:
    as_of_value = _date(as_of, "semester plan as-of date")
    if as_of_value is None:  # pragma: no cover - non-optional contract
        raise ValueError("as-of date is required")
    today = datetime.strptime(as_of_value, "%Y-%m-%d").date()
    three_days = today + timedelta(days=3)
    seven_days = today + timedelta(days=7)
    semester = load_semester(sw)
    states = [
        _load_state(workspace(sw.data_root, sw.term, course_id))
        for course_id in semester["course_ids"]
    ]

    due_now: list[tuple[date, str, str, str]] = []
    due_three: list[tuple[date, str, str, str]] = []
    due_seven: list[tuple[date, str, str, str]] = []
    availability: list[tuple[date, str, str, str, str]] = []
    preparation: list[tuple[date, str, str, str]] = []
    conflicts: list[tuple[str, str, str, str]] = []
    unstructured: list[tuple[str, str, str, str, str]] = []
    future_by_course: dict[str, list[tuple[date, str, str, str]]] = {
        course_id: [] for course_id in semester["course_ids"]
    }

    for state in states:
        course_id = state.course["course_id"]
        if state.core is not None:
            for assessment in state.core["assessments"]:
                if assessment["status"] not in _PLANNING_ACTIVE_ASSESSMENT_STATUSES:
                    continue
                due_claims = _due_claims(assessment)
                supported_due_values: list[
                    tuple[dict[str, object], tuple[tuple[str, date | datetime], date]]
                ] = []
                for claim in due_claims:
                    parsed = _supported_planning_value(claim["value"])
                    if parsed is None:
                        unstructured.append(
                            (
                                course_id,
                                assessment["id"],
                                claim["field"],
                                claim["id"],
                                _claim_text(claim),
                            )
                        )
                    else:
                        supported_due_values.append((claim, parsed))
                resolved_due: date | None = None
                unsupported_due_count = len(due_claims) - len(supported_due_values)
                meanings = {item[1][0] for item in supported_due_values}
                planning_dates = {item[1][1] for item in supported_due_values}
                due_conflict = False
                if unsupported_due_count and len(due_claims) > 1:
                    due_conflict = True
                elif len(meanings) == 1 and len(planning_dates) == 1:
                    resolved_due = next(iter(planning_dates))
                elif len(meanings) > 1 or len(planning_dates) > 1:
                    due_conflict = True
                if due_conflict:
                    due_fields = sorted({str(claim["field"]) for claim in due_claims})
                    conflict_field = due_fields[0] if len(due_fields) == 1 else "due/due-at"
                    conflicts.append(
                        (
                            course_id,
                            assessment["id"],
                            conflict_field,
                            _conflict_line(
                                course_id, assessment, conflict_field, due_claims
                            ),
                        )
                    )
                if resolved_due is not None:
                    line = _assessment_line(resolved_due, course_id, assessment)
                    if resolved_due <= today:
                        prefix = "DUE TODAY" if resolved_due == today else "OVERDUE"
                        due_now.append(
                            (
                                resolved_due,
                                course_id,
                                assessment["id"],
                                _assessment_line(
                                    resolved_due, course_id, assessment, prefix=prefix
                                ),
                            )
                        )
                    elif resolved_due <= three_days:
                        due_three.append((resolved_due, course_id, assessment["id"], line))
                    elif resolved_due <= seven_days:
                        due_seven.append((resolved_due, course_id, assessment["id"], line))
                    else:
                        future_by_course[course_id].append(
                            (resolved_due, "assessment", assessment["id"], assessment["title"])
                        )
                near_term = resolved_due is not None and resolved_due <= seven_days
                if near_term:
                    conflict_fields = sorted(
                        {
                            claim["field"]
                            for claim in assessment["claims"]
                            if claim["status"] == "conflicted"
                            and claim["field"] not in {"due", "due-at"}
                        }
                    )
                    for field in conflict_fields:
                        field_claims = _active_claims(assessment, field)
                        conflicts.append(
                            (
                                course_id,
                                assessment["id"],
                                field,
                                _conflict_line(course_id, assessment, field, field_claims),
                            )
                        )
                for field in ("available-at", "available-until"):
                    field_claims = _active_claims(assessment, field)
                    distinct_values = sorted({claim["value"] for claim in field_claims})
                    for claim in field_claims:
                        if _supported_planning_value(claim["value"]) is None:
                            unstructured.append(
                                (
                                    course_id,
                                    assessment["id"],
                                    field,
                                    claim["id"],
                                    _claim_text(claim),
                                )
                            )
                    if len(distinct_values) > 1:
                        conflicts.append(
                            (
                                course_id,
                                assessment["id"],
                                field,
                                _conflict_line(course_id, assessment, field, field_claims),
                            )
                        )
                    elif len(distinct_values) == 1:
                        available_value = _supported_planning_value(distinct_values[0])
                        available_date = None if available_value is None else available_value[1]
                        if available_date is not None and today <= available_date <= seven_days:
                            label = "AVAILABLE" if field == "available-at" else "CLOSES"
                            availability.append(
                                (
                                    available_date,
                                    course_id,
                                    assessment["id"],
                                    field,
                                    f"- {label} {available_date.isoformat()} — `{course_id}` / "
                                    f"`{assessment['id']}` — {assessment['title']}",
                                )
                            )

        for material in state.materials["materials"]:
            if (
                material.get("kind") not in _PLANNING_MATERIAL_KINDS
                or material.get("status") in {"completed", "superseded"}
                or material.get("relevant_date") is None
            ):
                continue
            relevant = datetime.strptime(material["relevant_date"], "%Y-%m-%d").date()
            if today <= relevant <= seven_days:
                preparation.append(
                    (
                        relevant,
                        course_id,
                        material["id"],
                        f"- {relevant.isoformat()} — `{course_id}` / `{material['id']}` — "
                        f"{material['title']} (`{material['kind']}` / `{material['status']}`)",
                    )
                )
            elif relevant > seven_days:
                future_by_course[course_id].append(
                    (relevant, "material", material["id"], material["title"])
                )

    coverage: list[str] = []
    for state in states:
        course_id = state.course["course_id"]
        if state.core is None or not state.core["sources"]:
            coverage.append(f"- `{course_id}` — no course source descriptors recorded")
            continue
        observations = (
            [] if state.source_observations is None else state.source_observations["observations"]
        )
        for source in state.core["sources"]:
            matching = [item for item in observations if item["source_id"] == source["id"]]
            if not matching:
                coverage.append(
                    f"- `{course_id}` / `{source['id']}` — never observed in durable state"
                )
                continue
            latest = max(matching, key=_source_observation_recency_key)
            outcome = latest["outcome"].replace("-", " ")
            coverage.append(
                f"- `{course_id}` / `{source['id']}` — observed {latest['observed_at']} — "
                f"{outcome} (`{latest['scope']}` scope)"
            )
    if not states:
        coverage.append("- No registered courses; no course source descriptors recorded.")

    longer: list[str] = []
    for course_id in semester["course_ids"]:
        items = sorted(future_by_course[course_id], key=lambda item: (item[0], item[1], item[2]))
        if not items:
            longer.append(f"- `{course_id}` — no later dated active item recorded.")
            continue
        first = items[0]
        remainder = len(items) - 1
        count_text = f"; {remainder} additional later item" + ("s" if remainder != 1 else "")
        if remainder == 0:
            count_text = "; no additional later items"
        longer.append(
            f"- `{course_id}` — next {first[0].isoformat()} {first[1]} `{first[2]}` — "
            f"{first[3]}{count_text}."
        )

    lines = [
        f"# {semester['title']} Semester Plan",
        "",
        f"Term: `{semester['term']}`  ",
        f"As of: `{as_of_value}`",
        "",
        "Derived only from durable School Learning state. This projection is not a source of truth and does not assign urgency or confidence scores.",
    ]
    _append_section(
        lines,
        "Due / Overdue / Due Today",
        [item[3] for item in sorted(due_now)],
        "No resolved active assessment is due today or overdue.",
    )
    _append_section(
        lines,
        "Next 3 Days",
        [item[3] for item in sorted(due_three)],
        "No resolved active assessment is due in the next 3 days.",
    )
    _append_section(
        lines,
        "Next 7 Days",
        [item[3] for item in sorted(due_seven)],
        "No additional resolved active assessment is due in days 4 through 7.",
    )
    _append_section(
        lines,
        "Assessment Availability Windows",
        [item[4] for item in sorted(availability)],
        "No resolved assessment availability boundary is recorded in the next 7 days.",
    )
    _append_section(
        lines,
        "Dated Course Preparation / Materials",
        [item[3] for item in sorted(preparation)],
        "No dated reading, listening reference, or lab/field guide is recorded in the next 7 days.",
    )
    _append_section(lines, "Source Coverage / Observations", coverage, "No source coverage recorded.")
    _append_section(
        lines,
        "Planning-Relevant Unresolved Conflicts",
        [item[3] for item in sorted(set(conflicts))],
        "No planning-relevant active assessment conflict is recorded.",
    )
    _append_section(
        lines,
        "Longer-Horizon Summary",
        longer,
        "No registered courses or later dated active items are recorded.",
    )
    _append_section(
        lines,
        "Unstructured Scheduling Claims That Cannot Safely Be Interpreted",
        [f"- `{item[0]}` / `{item[1]}` — {item[4]}" for item in sorted(set(unstructured))],
        "No unsupported active scheduling claim is recorded.",
    )
    lines.append("")
    destination = _term_confined_path(
        sw,
        _semester_generated_dir(sw) / "semester-plan.md",
        label="semester plan destination",
        regular_if_present=True,
    )
    _atomic_term_bytes(sw, destination, "\n".join(lines).encode("utf-8"))
    return destination


__all__ = ("render_course", "render_plan", "render_semester")
