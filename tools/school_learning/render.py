"""Deterministic generated views for School Learning v0.1."""

from __future__ import annotations

from html import escape
from pathlib import Path

from .core import Workspace, _atomic_write_bytes, iter_sessions, load_course, load_materials, load_topics


def render_course(ws: Workspace) -> tuple[Path, Path]:
    course = load_course(ws)
    materials = load_materials(ws)["materials"]
    topics = load_topics(ws)["topics"]
    sessions = iter_sessions(ws)

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
        f"<li><code>{escape(item['id'])}</code> — {escape(item['title'])} — {item['bytes']} bytes</li>"
        for item in materials
    ) or "<li>No materials recorded.</li>"
    recent_items = "".join(
        f"<li><code>{escape(item['session_id'])}</code> — {escape(item['topic_id'])} — {escape(item['outcome'])}</li>"
        for item in sessions[-10:][::-1]
    ) or "<li>No study sessions recorded.</li>"
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
<h2>Topics</h2>
<table><thead><tr><th>ID</th><th>Topic</th><th>Status</th><th>Last outcome</th><th>Priority</th><th>Note</th></tr></thead><tbody>{topic_rows}</tbody></table>
<h2>Materials</h2><ul>{material_items}</ul>
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
    html_path = generated / "course-home.html"
    review_path = generated / "review.md"
    _atomic_write_bytes(html_path, html.encode("utf-8"))
    _atomic_write_bytes(review_path, "\n".join(review_lines).encode("utf-8"))
    return html_path, review_path


__all__ = ("render_course",)
