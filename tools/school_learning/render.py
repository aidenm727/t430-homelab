"""Deterministic generated views for School Learning."""

from __future__ import annotations

from html import escape
from pathlib import Path

from .core import (
    SemesterWorkspace,
    Workspace,
    _atomic_term_bytes,
    _atomic_write_bytes,
    _confined_path,
    _load_state,
    _semester_generated_dir,
    _term_confined_path,
    load_semester,
    workspace,
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


__all__ = ("render_course", "render_semester")
