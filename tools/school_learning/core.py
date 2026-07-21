"""Owner-controlled local course workspace for School Learning v0.1."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

COURSE_SCHEMA = "aiden.school.course/v0.1"
MATERIALS_SCHEMA = "aiden.school.materials/v0.1"
TOPICS_SCHEMA = "aiden.school.topics/v0.1"
SESSION_SCHEMA = "aiden.school.session/v0.1"
SUPPORTED_SUFFIXES = {".pdf": "pdf", ".md": "markdown", ".txt": "text"}
STUDY_MODES = ("explain", "practice", "review")
TOPIC_STATUSES = ("unseen", "learning", "review", "solid")
OUTCOMES = ("correct", "partial", "incorrect")
_COMPONENT = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


class SchoolLearningError(ValueError):
    """Raised when local school state violates the v0.1 contract."""


@dataclass(frozen=True)
class Workspace:
    data_root: Path
    term: str
    course_id: str
    course_dir: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_data_root() -> Path:
    configured = os.environ.get("AIDEN_SCHOOL_DATA_ROOT")
    value = Path(configured) if configured else Path("~/.local/share/aiden-platform/school")
    return value.expanduser().resolve()


def _component(value: str, label: str) -> str:
    if not isinstance(value, str) or not _COMPONENT.fullmatch(value):
        raise SchoolLearningError(f"{label} must match {_COMPONENT.pattern}")
    if value in {".", ".."}:
        raise SchoolLearningError(f"{label} is not safe")
    return value


def workspace(data_root: Path | str, term: str, course_id: str) -> Workspace:
    root = Path(data_root).expanduser().resolve()
    safe_term = _component(term, "term")
    safe_course = _component(course_id, "course_id")
    course_dir = (root / safe_term / safe_course).resolve()
    try:
        course_dir.relative_to(root)
    except ValueError as error:
        raise SchoolLearningError("course workspace escapes the configured data root") from error
    return Workspace(root, safe_term, safe_course, course_dir)


def _atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    content = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    _atomic_write_bytes(path, content.encode("utf-8"))


def _read_json(path: Path, schema: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise SchoolLearningError(f"missing state file: {path.name}") from error
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SchoolLearningError(f"invalid JSON state: {path.name}") from error
    if not isinstance(value, dict) or value.get("schema_version") != schema:
        raise SchoolLearningError(f"unsupported or missing schema in {path.name}")
    return value


def initialize_course(
    data_root: Path | str,
    term: str,
    course_id: str,
    title: str,
    *,
    created_at: str | None = None,
) -> Workspace:
    ws = workspace(data_root, term, course_id)
    if not isinstance(title, str) or not title.strip():
        raise SchoolLearningError("course title must be nonempty")
    if ws.course_dir.exists() and any(ws.course_dir.iterdir()):
        raise SchoolLearningError("course workspace already exists and is not empty")
    for directory in ("materials", "sessions", "generated"):
        (ws.course_dir / directory).mkdir(parents=True, exist_ok=True)
    timestamp = created_at or utc_now()
    _atomic_write_json(
        ws.course_dir / "course.json",
        {
            "schema_version": COURSE_SCHEMA,
            "course_id": ws.course_id,
            "term": ws.term,
            "title": title.strip(),
            "created_at": timestamp,
        },
    )
    _atomic_write_json(
        ws.course_dir / "materials.json",
        {"schema_version": MATERIALS_SCHEMA, "materials": []},
    )
    _atomic_write_json(
        ws.course_dir / "topics.json",
        {"schema_version": TOPICS_SCHEMA, "topics": []},
    )
    return ws


def load_course(ws: Workspace) -> dict[str, Any]:
    value = _read_json(ws.course_dir / "course.json", COURSE_SCHEMA)
    if value.get("course_id") != ws.course_id or value.get("term") != ws.term:
        raise SchoolLearningError("course identity does not match its workspace")
    if not isinstance(value.get("title"), str) or not value["title"].strip():
        raise SchoolLearningError("course title is invalid")
    return value


def load_materials(ws: Workspace) -> dict[str, Any]:
    value = _read_json(ws.course_dir / "materials.json", MATERIALS_SCHEMA)
    if not isinstance(value.get("materials"), list):
        raise SchoolLearningError("materials must be a list")
    seen: set[str] = set()
    for record in value["materials"]:
        if not isinstance(record, dict):
            raise SchoolLearningError("material record must be an object")
        material_id = _component(record.get("id"), "material id")
        if material_id in seen:
            raise SchoolLearningError("material identifiers must be unique")
        seen.add(material_id)
        if record.get("type") not in SUPPORTED_SUFFIXES.values():
            raise SchoolLearningError("material type is unsupported")
        digest = record.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise SchoolLearningError("material digest is invalid")
        if not isinstance(record.get("bytes"), int) or record["bytes"] < 0:
            raise SchoolLearningError("material byte count is invalid")
        stored = Path(record.get("stored_path", ""))
        if stored.is_absolute() or ".." in stored.parts or stored.parts[:1] != ("materials",):
            raise SchoolLearningError("material stored path is unsafe")
    return value


def load_topics(ws: Workspace) -> dict[str, Any]:
    value = _read_json(ws.course_dir / "topics.json", TOPICS_SCHEMA)
    if not isinstance(value.get("topics"), list):
        raise SchoolLearningError("topics must be a list")
    seen: set[str] = set()
    for record in value["topics"]:
        if not isinstance(record, dict):
            raise SchoolLearningError("topic record must be an object")
        topic_id = _component(record.get("id"), "topic id")
        if topic_id in seen:
            raise SchoolLearningError("topic identifiers must be unique")
        seen.add(topic_id)
        if record.get("status") not in TOPIC_STATUSES:
            raise SchoolLearningError("topic status is invalid")
        if record.get("last_outcome") not in (None, *OUTCOMES):
            raise SchoolLearningError("topic outcome is invalid")
        material_ids = record.get("material_ids")
        if not isinstance(material_ids, list) or not all(isinstance(item, str) for item in material_ids):
            raise SchoolLearningError("topic material ids are invalid")
    return value


def sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def add_material(
    ws: Workspace,
    source: Path | str,
    material_id: str,
    title: str,
    *,
    added_at: str | None = None,
    replace: bool = False,
) -> dict[str, Any]:
    load_course(ws)
    source_path = Path(source).expanduser().resolve()
    if not source_path.is_file():
        raise SchoolLearningError("material source must be an existing regular file")
    suffix = source_path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise SchoolLearningError("supported material formats are PDF, Markdown, and text")
    safe_id = _component(material_id, "material_id")
    if not isinstance(title, str) or not title.strip():
        raise SchoolLearningError("material title must be nonempty")
    manifest = load_materials(ws)
    records = manifest["materials"]
    existing = next((item for item in records if item["id"] == safe_id), None)
    if existing is not None and not replace:
        raise SchoolLearningError("material id already exists; use replace deliberately")
    digest, size = sha256_file(source_path)
    stored_relative = Path("materials") / f"{safe_id}{suffix}"
    destination = ws.course_dir / stored_relative
    changed = existing is None or existing["sha256"] != digest or existing["stored_path"] != stored_relative.as_posix()
    if changed:
        destination.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary_name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
        temporary = Path(temporary_name)
        try:
            with os.fdopen(fd, "wb") as target, source_path.open("rb") as origin:
                shutil.copyfileobj(origin, target)
                target.flush()
                os.fsync(target.fileno())
            os.replace(temporary, destination)
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    record = {
        "id": safe_id,
        "title": title.strip(),
        "type": SUPPORTED_SUFFIXES[suffix],
        "source_name": source_path.name,
        "stored_path": stored_relative.as_posix(),
        "sha256": digest,
        "bytes": size,
        "added_at": added_at or utc_now(),
    }
    if existing is None:
        records.append(record)
    else:
        old_path = ws.course_dir / existing["stored_path"]
        index = records.index(existing)
        records[index] = record
        if old_path != destination:
            old_path.unlink(missing_ok=True)
    records.sort(key=lambda item: item["id"])
    _atomic_write_json(ws.course_dir / "materials.json", manifest)
    return {**record, "changed": changed}


def ensure_topic(
    ws: Workspace,
    topic_id: str,
    title: str,
    material_ids: Iterable[str] = (),
) -> dict[str, Any]:
    safe_id = _component(topic_id, "topic_id")
    if not isinstance(title, str) or not title.strip():
        raise SchoolLearningError("topic title must be nonempty")
    materials = load_materials(ws)["materials"]
    known_materials = {item["id"] for item in materials}
    normalized_materials = sorted({_component(item, "material id") for item in material_ids})
    missing = set(normalized_materials) - known_materials
    if missing:
        raise SchoolLearningError(f"unknown material ids: {', '.join(sorted(missing))}")
    topics = load_topics(ws)
    existing = next((item for item in topics["topics"] if item["id"] == safe_id), None)
    if existing is None:
        existing = {
            "id": safe_id,
            "title": title.strip(),
            "status": "unseen",
            "material_ids": normalized_materials,
            "last_outcome": None,
            "last_session_id": None,
            "next_review_priority": 0,
            "note": "",
        }
        topics["topics"].append(existing)
    else:
        existing["title"] = title.strip()
        existing["material_ids"] = normalized_materials
    topics["topics"].sort(key=lambda item: item["id"])
    _atomic_write_json(ws.course_dir / "topics.json", topics)
    return dict(existing)


def build_study_brief(
    ws: Workspace,
    topic_id: str,
    mode: str,
    objective: str,
    *,
    output: Path | None = None,
) -> Path:
    course = load_course(ws)
    topics = load_topics(ws)["topics"]
    materials = {item["id"]: item for item in load_materials(ws)["materials"]}
    safe_topic = _component(topic_id, "topic_id")
    if mode not in STUDY_MODES:
        raise SchoolLearningError("study mode must be explain, practice, or review")
    if not isinstance(objective, str) or not objective.strip():
        raise SchoolLearningError("study objective must be nonempty")
    topic = next((item for item in topics if item["id"] == safe_topic), None)
    if topic is None:
        raise SchoolLearningError("topic does not exist")
    selected = [materials[item] for item in topic["material_ids"]]
    lines = [
        "# School Learning Study Brief",
        "",
        f"- Course: {course['title']} (`{course['course_id']}`)",
        f"- Term: `{course['term']}`",
        f"- Topic: {topic['title']} (`{topic['id']}`)",
        f"- Mode: `{mode}`",
        f"- Current status: `{topic['status']}`",
        f"- Objective: {objective.strip()}",
        "",
        "## Selected Materials",
        "",
    ]
    if selected:
        for record in selected:
            lines.append(
                f"- `{record['id']}` — {record['title']} — `{record['stored_path']}` — SHA-256 `{record['sha256']}`"
            )
    else:
        lines.append("- None. State clearly that grounded help is unavailable until material is selected.")
    lines += [
        "",
        "## Consumer Instructions",
        "",
        "1. Use only the selected materials as course-grounding evidence.",
        "2. Cite the material identifier supporting each consequential explanation or correction.",
        "3. Distinguish material-backed statements from general background knowledge.",
        "4. Say that the supplied material is insufficient when the answer is not grounded by it.",
        "5. Do not infer grades, mastery, permissions, deadlines, or unstated course policy.",
        "6. End with a compact result: outcome suggestion (`correct`, `partial`, or `incorrect`), weak points, and recommended next review.",
        "",
        "## Manual Completion",
        "",
        "The owner reviews the result and records the final outcome with `./school record`. This brief does not update learning state automatically.",
        "",
    ]
    destination = output or (ws.course_dir / "generated" / "study-brief.md")
    destination = destination.resolve()
    try:
        destination.relative_to(ws.course_dir.resolve())
    except ValueError as error:
        raise SchoolLearningError("study brief output must remain inside the course workspace") from error
    _atomic_write_bytes(destination, "\n".join(lines).encode("utf-8"))
    return destination


def record_session(
    ws: Workspace,
    topic_id: str,
    outcome: str,
    status: str,
    note: str,
    *,
    session_id: str | None = None,
    recorded_at: str | None = None,
    next_review_priority: int = 0,
) -> dict[str, Any]:
    load_course(ws)
    safe_topic = _component(topic_id, "topic_id")
    if outcome not in OUTCOMES:
        raise SchoolLearningError("outcome must be correct, partial, or incorrect")
    if status not in TOPIC_STATUSES:
        raise SchoolLearningError("status must be unseen, learning, review, or solid")
    if not isinstance(next_review_priority, int) or not 0 <= next_review_priority <= 100:
        raise SchoolLearningError("next review priority must be an integer from 0 through 100")
    if not isinstance(note, str):
        raise SchoolLearningError("note must be a string")
    timestamp = recorded_at or utc_now()
    safe_session = _component(session_id or timestamp.lower().replace(":", "-").replace("+", "-"), "session_id")
    topics = load_topics(ws)
    topic = next((item for item in topics["topics"] if item["id"] == safe_topic), None)
    if topic is None:
        raise SchoolLearningError("topic does not exist")
    session = {
        "schema_version": SESSION_SCHEMA,
        "session_id": safe_session,
        "recorded_at": timestamp,
        "course_id": ws.course_id,
        "term": ws.term,
        "topic_id": safe_topic,
        "outcome": outcome,
        "status": status,
        "note": note.strip(),
        "next_review_priority": next_review_priority,
    }
    session_path = ws.course_dir / "sessions" / f"{safe_session}.json"
    if session_path.exists():
        raise SchoolLearningError("session id already exists")
    _atomic_write_json(session_path, session)
    topic.update(
        {
            "status": status,
            "last_outcome": outcome,
            "last_session_id": safe_session,
            "next_review_priority": next_review_priority,
            "note": note.strip(),
        }
    )
    _atomic_write_json(ws.course_dir / "topics.json", topics)
    return session


def iter_sessions(ws: Workspace) -> list[dict[str, Any]]:
    sessions_dir = ws.course_dir / "sessions"
    values: list[dict[str, Any]] = []
    for path in sorted(sessions_dir.glob("*.json")):
        value = _read_json(path, SESSION_SCHEMA)
        if value.get("course_id") != ws.course_id or value.get("term") != ws.term:
            raise SchoolLearningError("session identity does not match workspace")
        values.append(value)
    return values


__all__ = (
    "COURSE_SCHEMA",
    "MATERIALS_SCHEMA",
    "OUTCOMES",
    "SESSION_SCHEMA",
    "STUDY_MODES",
    "SUPPORTED_SUFFIXES",
    "SchoolLearningError",
    "TOPICS_SCHEMA",
    "TOPIC_STATUSES",
    "Workspace",
    "add_material",
    "build_study_brief",
    "default_data_root",
    "ensure_topic",
    "initialize_course",
    "iter_sessions",
    "load_course",
    "load_materials",
    "load_topics",
    "record_session",
    "sha256_file",
    "workspace",
)
