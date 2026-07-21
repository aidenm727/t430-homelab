"""Owner-controlled local course workspace for School Learning v0.1."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
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
_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_REQUIRED_DIRECTORIES = ("materials", "sessions", "generated")

_COURSE_KEYS = frozenset({"schema_version", "course_id", "term", "title", "created_at"})
_MATERIALS_KEYS = frozenset({"schema_version", "materials"})
_MATERIAL_KEYS = frozenset(
    {"id", "title", "type", "source_name", "stored_path", "sha256", "bytes", "added_at"}
)
_TOPICS_KEYS = frozenset({"schema_version", "topics"})
_TOPIC_KEYS = frozenset(
    {
        "id",
        "title",
        "status",
        "material_ids",
        "last_outcome",
        "last_session_id",
        "next_review_priority",
        "note",
    }
)
_SESSION_KEYS = frozenset(
    {
        "schema_version",
        "session_id",
        "recorded_at",
        "course_id",
        "term",
        "topic_id",
        "mode",
        "outcome",
        "status",
        "note",
        "next_review_priority",
        "material_ids",
    }
)


class SchoolLearningError(ValueError):
    """Raised when local school state violates the v0.1 contract."""


@dataclass(frozen=True)
class Workspace:
    data_root: Path
    term: str
    course_id: str
    course_dir: Path


@dataclass(frozen=True)
class _State:
    course: dict[str, Any]
    materials: dict[str, Any]
    topics: dict[str, Any]
    sessions: tuple[dict[str, Any], ...]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_data_root() -> Path:
    configured = os.environ.get("AIDEN_SCHOOL_DATA_ROOT")
    value = Path(configured) if configured else Path("~/.local/share/aiden-platform/school")
    try:
        return value.expanduser().resolve()
    except (OSError, RuntimeError) as error:
        raise SchoolLearningError("data root cannot be resolved") from error


def _component(value: object, label: str) -> str:
    if not isinstance(value, str) or not _COMPONENT.fullmatch(value):
        raise SchoolLearningError(f"{label} must match {_COMPONENT.pattern}")
    if value in {".", ".."}:
        raise SchoolLearningError(f"{label} is not safe")
    return value


def _timestamp(value: object, label: str) -> str:
    if not isinstance(value, str) or not _TIMESTAMP.fullmatch(value):
        raise SchoolLearningError(f"{label} must be a UTC v0.1 timestamp")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as error:
        raise SchoolLearningError(f"{label} must be a valid UTC v0.1 timestamp") from error
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        raise SchoolLearningError(f"{label} must be a canonical UTC v0.1 timestamp")
    return value


def _nonempty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SchoolLearningError(f"{label} must be nonempty")
    return value


def _priority(value: object, label: str = "next review priority") -> int:
    if type(value) is not int or not 0 <= value <= 100:
        raise SchoolLearningError(f"{label} must be an integer from 0 through 100")
    return value


def _exact_object(value: object, keys: frozenset[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SchoolLearningError(f"{label} must be an object")
    actual = set(value)
    if actual != keys:
        missing = sorted(keys - actual)
        unexpected = sorted(actual - keys)
        details: list[str] = []
        if missing:
            details.append(f"missing keys: {', '.join(missing)}")
        if unexpected:
            details.append(f"unexpected keys: {', '.join(unexpected)}")
        raise SchoolLearningError(f"{label} has invalid keys ({'; '.join(details)})")
    return value


def _resolved_data_root(value: Path | str) -> Path:
    try:
        root = Path(value).expanduser().resolve()
    except (OSError, RuntimeError, TypeError) as error:
        raise SchoolLearningError("data root cannot be resolved") from error
    try:
        root.relative_to(_REPOSITORY_ROOT)
    except ValueError:
        pass
    else:
        raise SchoolLearningError("course data root must remain outside the Aiden Platform repository")
    for ancestor in (root, *root.parents):
        marker = ancestor / ".git"
        try:
            if marker.is_symlink() or marker.is_file() or marker.is_dir():
                raise SchoolLearningError("course data root must remain outside every Git worktree")
        except OSError as error:
            raise SchoolLearningError("data root Git-worktree status cannot be validated") from error
    try:
        if root.exists() and not root.is_dir():
            raise SchoolLearningError("data root must be a directory")
    except OSError as error:
        raise SchoolLearningError("data root cannot be inspected") from error
    return root


def workspace(data_root: Path | str, term: str, course_id: str) -> Workspace:
    root = _resolved_data_root(data_root)
    safe_term = _component(term, "term")
    safe_course = _component(course_id, "course_id")
    course_dir = root / safe_term / safe_course
    return Workspace(root, safe_term, safe_course, course_dir)


def _workspace_dir(ws: Workspace) -> Path:
    if not isinstance(ws, Workspace):
        raise SchoolLearningError("workspace is invalid")
    root = _resolved_data_root(ws.data_root)
    safe_term = _component(ws.term, "term")
    safe_course = _component(ws.course_id, "course_id")
    expected = root / safe_term / safe_course
    if ws.data_root != root or ws.course_dir != expected:
        raise SchoolLearningError("workspace identity or path is inconsistent")
    return expected


def _lexical_absolute(path: Path | str) -> Path:
    try:
        return Path(os.path.abspath(os.fspath(path)))
    except (OSError, TypeError, ValueError) as error:
        raise SchoolLearningError("filesystem path is invalid") from error


def _confined_path(
    ws: Workspace,
    path: Path | str,
    *,
    label: str,
    must_exist: bool = False,
    require_file: bool = False,
    require_directory: bool = False,
    regular_if_present: bool = False,
) -> Path:
    base = _workspace_dir(ws)
    candidate = _lexical_absolute(path)
    try:
        relative = candidate.relative_to(base)
    except ValueError as error:
        raise SchoolLearningError(f"{label} must remain inside the course workspace") from error
    current = base
    components = ((), *tuple((part,) for part in relative.parts))
    try:
        for component in components:
            if component:
                current = current / component[0]
            if current.is_symlink():
                raise SchoolLearningError(f"{label} must not use symlinks")
            if current != candidate and current.exists() and not current.is_dir():
                raise SchoolLearningError(f"{label} has a non-directory parent")
        resolved_candidate = candidate.resolve(strict=False)
        resolved_base = base.resolve(strict=False)
        try:
            resolved_candidate.relative_to(resolved_base)
        except ValueError as error:
            raise SchoolLearningError(f"{label} escapes the course workspace") from error
        exists = candidate.exists()
        if must_exist and not exists:
            raise SchoolLearningError(f"missing {label}")
        if exists and (require_file or regular_if_present):
            mode = os.lstat(candidate).st_mode
            if not stat.S_ISREG(mode):
                raise SchoolLearningError(f"{label} must be a regular file")
        if exists and require_directory and not candidate.is_dir():
            raise SchoolLearningError(f"{label} must be a directory")
    except SchoolLearningError:
        raise
    except (OSError, RuntimeError) as error:
        raise SchoolLearningError(f"{label} cannot be safely inspected") from error
    return candidate


def _validate_layout(ws: Workspace) -> None:
    _confined_path(ws, ws.course_dir, label="course workspace", must_exist=True, require_directory=True)
    for name in _REQUIRED_DIRECTORIES:
        _confined_path(
            ws,
            ws.course_dir / name,
            label=f"{name} directory",
            must_exist=True,
            require_directory=True,
        )


def _safe_create_directory(path: Path, label: str) -> None:
    try:
        if path.is_symlink():
            raise SchoolLearningError(f"{label} must not be a symlink")
        path.mkdir()
        if path.is_symlink() or not path.is_dir():
            raise SchoolLearningError(f"{label} could not be created safely")
    except FileExistsError:
        if path.is_symlink() or not path.is_dir():
            raise SchoolLearningError(f"{label} must be a real directory")
    except SchoolLearningError:
        raise
    except OSError as error:
        raise SchoolLearningError(f"{label} could not be created") from error


def _safe_create_directory_chain(path: Path, label: str) -> None:
    missing: list[Path] = []
    current = path
    try:
        while not current.exists():
            if current.is_symlink():
                raise SchoolLearningError(f"{label} must not use symlinks")
            missing.append(current)
            current = current.parent
        if current.is_symlink() or not current.is_dir():
            raise SchoolLearningError(f"{label} must have a real directory parent")
    except SchoolLearningError:
        raise
    except OSError as error:
        raise SchoolLearningError(f"{label} cannot be safely inspected") from error
    for directory in reversed(missing):
        if directory.parent.is_symlink() or not directory.parent.is_dir():
            raise SchoolLearningError(f"{label} must have real directory parents")
        _safe_create_directory(directory, label)


def _create_temp_file(ws: Workspace, parent: Path, prefix: str) -> tuple[int, Path]:
    safe_parent = _confined_path(
        ws,
        parent,
        label="temporary-file parent",
        must_exist=True,
        require_directory=True,
    )
    try:
        fd, name = tempfile.mkstemp(prefix=prefix, dir=safe_parent)
    except OSError as error:
        raise SchoolLearningError("confined temporary file could not be created") from error
    temporary = Path(name)
    try:
        _confined_path(
            ws,
            temporary,
            label="temporary file",
            must_exist=True,
            require_file=True,
        )
    except BaseException:
        os.close(fd)
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise
    return fd, temporary


def _safe_unlink(ws: Workspace, path: Path, label: str, *, missing_ok: bool = False) -> None:
    safe = _confined_path(
        ws,
        path,
        label=label,
        must_exist=not missing_ok,
        regular_if_present=True,
    )
    try:
        safe.unlink(missing_ok=missing_ok)
    except OSError as error:
        raise SchoolLearningError(f"{label} could not be removed safely") from error


def _safe_replace(ws: Workspace, source: Path, destination: Path, label: str) -> None:
    safe_source = _confined_path(
        ws,
        source,
        label=f"{label} source",
        must_exist=True,
        require_file=True,
    )
    safe_destination = _confined_path(
        ws,
        destination,
        label=f"{label} destination",
        regular_if_present=True,
    )
    _confined_path(
        ws,
        safe_destination.parent,
        label=f"{label} parent",
        must_exist=True,
        require_directory=True,
    )
    try:
        os.replace(safe_source, safe_destination)
    except OSError as error:
        raise SchoolLearningError(f"{label} could not be completed safely") from error


def _atomic_write_bytes(ws: Workspace, path: Path, content: bytes) -> None:
    destination = _confined_path(ws, path, label="atomic-write target", regular_if_present=True)
    _confined_path(
        ws,
        destination.parent,
        label="atomic-write parent",
        must_exist=True,
        require_directory=True,
    )
    fd, temporary = _create_temp_file(ws, destination.parent, f".{destination.name}.")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        _safe_replace(ws, temporary, destination, "atomic write")
    except SchoolLearningError:
        raise
    except (OSError, TypeError, ValueError) as error:
        raise SchoolLearningError("atomic write failed") from error
    finally:
        if temporary.exists() or temporary.is_symlink():
            _safe_unlink(ws, temporary, "temporary file", missing_ok=True)


def _atomic_write_json(ws: Workspace, path: Path, value: dict[str, Any]) -> None:
    try:
        content = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    except (TypeError, ValueError) as error:
        raise SchoolLearningError("state cannot be encoded as JSON") from error
    _atomic_write_bytes(ws, path, content.encode("utf-8"))


def _read_regular_bytes(ws: Workspace, path: Path, label: str) -> bytes:
    safe = _confined_path(ws, path, label=label, must_exist=True, require_file=True)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(safe, flags)
        with os.fdopen(fd, "rb") as handle:
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                raise SchoolLearningError(f"{label} must be a regular file")
            return handle.read()
    except SchoolLearningError:
        raise
    except OSError as error:
        raise SchoolLearningError(f"{label} cannot be read safely") from error


def _read_json(ws: Workspace, path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(_read_regular_bytes(ws, path, label).decode("utf-8"))
    except SchoolLearningError:
        raise
    except (UnicodeError, json.JSONDecodeError) as error:
        raise SchoolLearningError(f"invalid JSON state: {path.name}") from error
    if not isinstance(value, dict):
        raise SchoolLearningError(f"{label} must contain a JSON object")
    return value


def _validate_course(value: object, ws: Workspace) -> dict[str, Any]:
    record = _exact_object(value, _COURSE_KEYS, "course record")
    if record["schema_version"] != COURSE_SCHEMA:
        raise SchoolLearningError("unsupported course schema")
    if _component(record["course_id"], "course id") != ws.course_id:
        raise SchoolLearningError("course id does not match its workspace")
    if _component(record["term"], "course term") != ws.term:
        raise SchoolLearningError("course term does not match its workspace")
    _nonempty_string(record["title"], "course title")
    _timestamp(record["created_at"], "course creation timestamp")
    return record


def _validate_material(value: object) -> dict[str, Any]:
    record = _exact_object(value, _MATERIAL_KEYS, "material record")
    material_id = _component(record["id"], "material id")
    _nonempty_string(record["title"], "material title")
    source_name = _nonempty_string(record["source_name"], "material source name")
    if source_name != Path(source_name).name or "/" in source_name or "\\" in source_name:
        raise SchoolLearningError("material source name must be a filename")
    stored_value = record["stored_path"]
    if not isinstance(stored_value, str) or "\\" in stored_value:
        raise SchoolLearningError("material stored path is invalid")
    stored = PurePosixPath(stored_value)
    suffix = stored.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise SchoolLearningError("material extension is unsupported")
    expected = PurePosixPath("materials") / f"{material_id}{suffix}"
    if stored != expected:
        raise SchoolLearningError("material stored path does not correspond to its id and extension")
    if record["type"] != SUPPORTED_SUFFIXES[suffix]:
        raise SchoolLearningError("material type does not correspond to its extension")
    if Path(source_name).suffix.lower() != suffix:
        raise SchoolLearningError("material source name does not correspond to its extension")
    if not isinstance(record["sha256"], str) or not _DIGEST.fullmatch(record["sha256"]):
        raise SchoolLearningError("material digest is invalid")
    if type(record["bytes"]) is not int or record["bytes"] < 0:
        raise SchoolLearningError("material byte count is invalid")
    _timestamp(record["added_at"], "material timestamp")
    return record


def _validate_materials(value: object) -> dict[str, Any]:
    manifest = _exact_object(value, _MATERIALS_KEYS, "materials manifest")
    if manifest["schema_version"] != MATERIALS_SCHEMA:
        raise SchoolLearningError("unsupported materials schema")
    if not isinstance(manifest["materials"], list):
        raise SchoolLearningError("materials must be a list")
    seen: set[str] = set()
    for value_record in manifest["materials"]:
        record = _validate_material(value_record)
        if record["id"] in seen:
            raise SchoolLearningError("material identifiers must be unique")
        seen.add(record["id"])
    return manifest


def _identifier_list(value: object, label: str) -> list[str]:
    if not isinstance(value, list):
        raise SchoolLearningError(f"{label} must be a list")
    result = [_component(item, f"{label} entry") for item in value]
    if len(set(result)) != len(result):
        raise SchoolLearningError(f"{label} entries must be unique")
    return result


def _validate_topic(value: object) -> dict[str, Any]:
    record = _exact_object(value, _TOPIC_KEYS, "topic record")
    _component(record["id"], "topic id")
    _nonempty_string(record["title"], "topic title")
    if record["status"] not in TOPIC_STATUSES:
        raise SchoolLearningError("topic status is invalid")
    _identifier_list(record["material_ids"], "topic material ids")
    if record["last_outcome"] is not None and record["last_outcome"] not in OUTCOMES:
        raise SchoolLearningError("topic outcome is invalid")
    if record["last_session_id"] is not None:
        _component(record["last_session_id"], "topic last session id")
    _priority(record["next_review_priority"])
    if not isinstance(record["note"], str):
        raise SchoolLearningError("topic note must be a string")
    return record


def _validate_topics(value: object) -> dict[str, Any]:
    manifest = _exact_object(value, _TOPICS_KEYS, "topics manifest")
    if manifest["schema_version"] != TOPICS_SCHEMA:
        raise SchoolLearningError("unsupported topics schema")
    if not isinstance(manifest["topics"], list):
        raise SchoolLearningError("topics must be a list")
    seen: set[str] = set()
    for value_record in manifest["topics"]:
        record = _validate_topic(value_record)
        if record["id"] in seen:
            raise SchoolLearningError("topic identifiers must be unique")
        seen.add(record["id"])
    return manifest


def _validate_session(value: object, path: Path, ws: Workspace) -> dict[str, Any]:
    record = _exact_object(value, _SESSION_KEYS, "session record")
    if record["schema_version"] != SESSION_SCHEMA:
        raise SchoolLearningError("unsupported session schema")
    session_id = _component(record["session_id"], "session id")
    if path.name != f"{session_id}.json":
        raise SchoolLearningError("session filename does not match its session id")
    _timestamp(record["recorded_at"], "session timestamp")
    if _component(record["course_id"], "session course id") != ws.course_id:
        raise SchoolLearningError("session course id does not match its workspace")
    if _component(record["term"], "session term") != ws.term:
        raise SchoolLearningError("session term does not match its workspace")
    _component(record["topic_id"], "session topic id")
    if record["mode"] not in STUDY_MODES:
        raise SchoolLearningError("session mode is invalid")
    if record["outcome"] not in OUTCOMES:
        raise SchoolLearningError("session outcome is invalid")
    if record["status"] not in TOPIC_STATUSES:
        raise SchoolLearningError("session status is invalid")
    if not isinstance(record["note"], str):
        raise SchoolLearningError("session note must be a string")
    _priority(record["next_review_priority"])
    _identifier_list(record["material_ids"], "session material ids")
    return record


def _material_path(ws: Workspace, record: dict[str, Any]) -> Path:
    path = ws.course_dir / record["stored_path"]
    return _confined_path(
        ws,
        path,
        label=f"stored material {record['id']}",
        regular_if_present=True,
    )


def _hash_open_file(handle: Any) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    while True:
        chunk = handle.read(1024 * 1024)
        if not chunk:
            break
        digest.update(chunk)
        size += len(chunk)
    return digest.hexdigest(), size


def _hash_confined_file(ws: Workspace, path: Path, label: str) -> tuple[str, int]:
    safe = _confined_path(ws, path, label=label, must_exist=True, require_file=True)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(safe, flags)
        with os.fdopen(fd, "rb") as handle:
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                raise SchoolLearningError(f"{label} must be a regular file")
            return _hash_open_file(handle)
    except SchoolLearningError:
        raise
    except OSError as error:
        raise SchoolLearningError(f"{label} cannot be hashed safely") from error


def sha256_file(path: Path) -> tuple[str, int]:
    source = _lexical_absolute(path)
    try:
        if source.is_symlink() or not stat.S_ISREG(os.lstat(source).st_mode):
            raise SchoolLearningError("hash source must be a regular non-symlink file")
        fd = os.open(source, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd, "rb") as handle:
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                raise SchoolLearningError("hash source must be a regular file")
            return _hash_open_file(handle)
    except SchoolLearningError:
        raise
    except OSError as error:
        raise SchoolLearningError("hash source cannot be read safely") from error


def _verify_material_identity(ws: Workspace, record: dict[str, Any]) -> None:
    path = _material_path(ws, record)
    digest, size = _hash_confined_file(ws, path, f"stored material {record['id']}")
    if digest != record["sha256"] or size != record["bytes"]:
        raise SchoolLearningError(f"stored material {record['id']} does not match its recorded identity")


def _read_sessions(ws: Workspace) -> tuple[dict[str, Any], ...]:
    sessions_dir = _confined_path(
        ws,
        ws.course_dir / "sessions",
        label="sessions directory",
        must_exist=True,
        require_directory=True,
    )
    try:
        paths = sorted(
            (path for path in sessions_dir.iterdir() if path.name.endswith(".json")),
            key=lambda path: path.name,
        )
    except OSError as error:
        raise SchoolLearningError("sessions directory cannot be read safely") from error
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in paths:
        safe = _confined_path(ws, path, label="session file", must_exist=True, require_file=True)
        record = _validate_session(_read_json(ws, safe, "session file"), safe, ws)
        if record["session_id"] in seen:
            raise SchoolLearningError("session identifiers must be unique")
        seen.add(record["session_id"])
        records.append(record)
    return tuple(records)


def _validate_references(
    materials: dict[str, Any],
    topics: dict[str, Any],
    sessions: tuple[dict[str, Any], ...],
) -> None:
    material_ids = {record["id"] for record in materials["materials"]}
    topic_by_id = {record["id"]: record for record in topics["topics"]}
    session_by_id = {record["session_id"]: record for record in sessions}
    for topic in topics["topics"]:
        unknown = set(topic["material_ids"]) - material_ids
        if unknown:
            raise SchoolLearningError(
                f"topic {topic['id']} references unknown materials: {', '.join(sorted(unknown))}"
            )
        recent = topic["last_session_id"]
        if recent is not None:
            session = session_by_id.get(recent)
            if session is None:
                raise SchoolLearningError(f"topic {topic['id']} references an unknown recent session")
            if session["topic_id"] != topic["id"]:
                raise SchoolLearningError(f"topic {topic['id']} references a session for another topic")
    for session in sessions:
        if session["topic_id"] not in topic_by_id:
            raise SchoolLearningError(f"session {session['session_id']} references an unknown topic")
        unknown = set(session["material_ids"]) - material_ids
        if unknown:
            raise SchoolLearningError(
                f"session {session['session_id']} references unknown materials: {', '.join(sorted(unknown))}"
            )


def _load_state(ws: Workspace, *, skip_material_id: str | None = None) -> _State:
    _validate_layout(ws)
    course = _validate_course(_read_json(ws, ws.course_dir / "course.json", "course state file"), ws)
    materials = _validate_materials(
        _read_json(ws, ws.course_dir / "materials.json", "materials state file")
    )
    topics = _validate_topics(_read_json(ws, ws.course_dir / "topics.json", "topics state file"))
    sessions = _read_sessions(ws)
    _validate_references(materials, topics, sessions)
    for record in materials["materials"]:
        path = _material_path(ws, record)
        if record["id"] != skip_material_id:
            _verify_material_identity(ws, record)
        else:
            _confined_path(
                ws,
                path,
                label=f"stored material {record['id']}",
                regular_if_present=True,
            )
    return _State(course, materials, topics, sessions)


def initialize_course(
    data_root: Path | str,
    term: str,
    course_id: str,
    title: str,
    *,
    created_at: str | None = None,
) -> Workspace:
    safe_title = _nonempty_string(title, "course title").strip()
    timestamp = _timestamp(created_at if created_at is not None else utc_now(), "course creation timestamp")
    ws = workspace(data_root, term, course_id)
    root = _resolved_data_root(ws.data_root)
    try:
        if ws.course_dir.exists():
            if ws.course_dir.is_symlink() or not ws.course_dir.is_dir():
                raise SchoolLearningError("course workspace must be a real directory")
            if any(ws.course_dir.iterdir()):
                raise SchoolLearningError("course workspace already exists and is not empty")
    except SchoolLearningError:
        raise
    except OSError as error:
        raise SchoolLearningError("course workspace cannot be inspected") from error

    _resolved_data_root(root)
    _safe_create_directory_chain(root, "data root")
    _resolved_data_root(root)
    _safe_create_directory(root / ws.term, "term directory")
    _resolved_data_root(root)
    _safe_create_directory(ws.course_dir, "course workspace")
    for name in _REQUIRED_DIRECTORIES:
        _confined_path(
            ws,
            ws.course_dir,
            label="course workspace",
            must_exist=True,
            require_directory=True,
        )
        _safe_create_directory(ws.course_dir / name, f"{name} directory")
    _validate_layout(ws)
    _atomic_write_json(
        ws,
        ws.course_dir / "course.json",
        {
            "schema_version": COURSE_SCHEMA,
            "course_id": ws.course_id,
            "term": ws.term,
            "title": safe_title,
            "created_at": timestamp,
        },
    )
    _atomic_write_json(
        ws,
        ws.course_dir / "materials.json",
        {"schema_version": MATERIALS_SCHEMA, "materials": []},
    )
    _atomic_write_json(
        ws,
        ws.course_dir / "topics.json",
        {"schema_version": TOPICS_SCHEMA, "topics": []},
    )
    _load_state(ws)
    return ws


def load_course(ws: Workspace) -> dict[str, Any]:
    return _load_state(ws).course


def load_materials(ws: Workspace) -> dict[str, Any]:
    return _load_state(ws).materials


def load_topics(ws: Workspace) -> dict[str, Any]:
    return _load_state(ws).topics


def _copy_source_to_temp(ws: Workspace, source: Path, destination_parent: Path) -> tuple[Path, str, int]:
    try:
        if source.is_symlink() or not stat.S_ISREG(os.lstat(source).st_mode):
            raise SchoolLearningError("material source must be an existing regular non-symlink file")
    except FileNotFoundError as error:
        raise SchoolLearningError("material source must be an existing regular file") from error
    except SchoolLearningError:
        raise
    except OSError as error:
        raise SchoolLearningError("material source cannot be safely inspected") from error
    target_fd, temporary = _create_temp_file(ws, destination_parent, ".material.")
    source_fd: int | None = None
    target_open_fd: int | None = target_fd
    completed = False
    try:
        source_fd = os.open(source, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(source_fd, "rb") as origin, os.fdopen(target_open_fd, "wb") as target:
            source_fd = None
            target_open_fd = None
            if not stat.S_ISREG(os.fstat(origin.fileno()).st_mode):
                raise SchoolLearningError("material source must be a regular file")
            digest = hashlib.sha256()
            size = 0
            while True:
                chunk = origin.read(1024 * 1024)
                if not chunk:
                    break
                target.write(chunk)
                digest.update(chunk)
                size += len(chunk)
            target.flush()
            os.fsync(target.fileno())
        completed = True
        return temporary, digest.hexdigest(), size
    except SchoolLearningError:
        raise
    except OSError as error:
        raise SchoolLearningError("material source could not be copied safely") from error
    finally:
        if source_fd is not None:
            os.close(source_fd)
        if target_open_fd is not None:
            os.close(target_open_fd)
        if not completed and (temporary.exists() or temporary.is_symlink()):
            _safe_unlink(ws, temporary, "material temporary file", missing_ok=True)


def _stored_matches(ws: Workspace, record: dict[str, Any], digest: str, size: int, path: Path) -> bool:
    if record["sha256"] != digest or record["bytes"] != size:
        return False
    if record["stored_path"] != path.relative_to(ws.course_dir).as_posix():
        return False
    try:
        stored_digest, stored_size = _hash_confined_file(ws, path, f"stored material {record['id']}")
    except SchoolLearningError as error:
        if not path.exists() and not path.is_symlink():
            return False
        raise error
    return stored_digest == digest and stored_size == size


def _as_school_error(message: str, error: BaseException) -> SchoolLearningError:
    if isinstance(error, SchoolLearningError):
        return SchoolLearningError(f"{message}: {error}")
    return SchoolLearningError(message)


def add_material(
    ws: Workspace,
    source: Path | str,
    material_id: str,
    title: str,
    *,
    added_at: str | None = None,
    replace: bool = False,
) -> dict[str, Any]:
    safe_id = _component(material_id, "material_id")
    safe_title = _nonempty_string(title, "material title").strip()
    timestamp = _timestamp(added_at if added_at is not None else utc_now(), "material timestamp")
    source_path = _lexical_absolute(Path(source).expanduser())
    suffix = source_path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise SchoolLearningError("supported material formats are PDF, Markdown, and text")
    state = _load_state(ws, skip_material_id=safe_id)
    manifest = state.materials
    records = manifest["materials"]
    existing = next((item for item in records if item["id"] == safe_id), None)
    if existing is not None and not replace:
        raise SchoolLearningError("material id already exists; use replace deliberately")

    stored_relative = Path("materials") / f"{safe_id}{suffix}"
    destination = _confined_path(
        ws,
        ws.course_dir / stored_relative,
        label="material destination",
        regular_if_present=True,
    )
    temporary, digest, size = _copy_source_to_temp(ws, source_path, destination.parent)
    old_path = _material_path(ws, existing) if existing is not None else None
    changed = existing is None or not _stored_matches(ws, existing, digest, size, destination)
    record = {
        "id": safe_id,
        "title": safe_title,
        "type": SUPPORTED_SUFFIXES[suffix],
        "source_name": source_path.name,
        "stored_path": stored_relative.as_posix(),
        "sha256": digest,
        "bytes": size,
        "added_at": timestamp,
    }
    _validate_material(record)
    if existing is None:
        records.append(record)
    else:
        records[records.index(existing)] = record
    records.sort(key=lambda item: item["id"])
    _validate_materials(manifest)

    manifest_path = _confined_path(
        ws,
        ws.course_dir / "materials.json",
        label="materials state file",
        must_exist=True,
        require_file=True,
    )
    old_manifest = _read_regular_bytes(ws, manifest_path, "materials state file")
    backup: Path | None = None
    old_moved = False
    new_installed = False
    manifest_attempted = False
    try:
        if changed:
            if old_path is not None and old_path != destination and destination.exists():
                raise SchoolLearningError("replacement destination already exists")
            if old_path is not None and old_path.exists():
                backup_fd, backup = _create_temp_file(ws, old_path.parent, f".{old_path.name}.backup.")
                os.close(backup_fd)
                _safe_replace(ws, old_path, backup, "material backup")
                old_moved = True
            _safe_replace(ws, temporary, destination, "material replacement")
            new_installed = True
        manifest_attempted = True
        _atomic_write_json(ws, manifest_path, manifest)
        _verify_material_identity(ws, record)
        if backup is not None and old_moved:
            _safe_unlink(ws, backup, "material backup")
            old_moved = False
        return {**record, "changed": changed}
    except Exception as error:
        rollback_errors: list[str] = []
        if new_installed:
            try:
                _safe_unlink(ws, destination, "failed material replacement", missing_ok=True)
                new_installed = False
            except SchoolLearningError as rollback_error:
                rollback_errors.append(str(rollback_error))
        if backup is not None and old_moved and old_path is not None:
            try:
                _safe_replace(ws, backup, old_path, "material rollback")
                old_moved = False
            except SchoolLearningError as rollback_error:
                rollback_errors.append(str(rollback_error))
        if manifest_attempted:
            try:
                _atomic_write_bytes(ws, manifest_path, old_manifest)
            except SchoolLearningError as rollback_error:
                rollback_errors.append(str(rollback_error))
        if rollback_errors:
            raise SchoolLearningError(
                "material replacement failed and rollback was incomplete: " + "; ".join(rollback_errors)
            ) from error
        raise _as_school_error("material replacement failed", error) from error
    finally:
        if temporary.exists() or temporary.is_symlink():
            _safe_unlink(ws, temporary, "material temporary file", missing_ok=True)
        if backup is not None and (backup.exists() or backup.is_symlink()):
            _safe_unlink(ws, backup, "material backup", missing_ok=True)


def _normalize_material_ids(material_ids: Iterable[str]) -> list[str]:
    if isinstance(material_ids, (str, bytes)):
        raise SchoolLearningError("material ids must be an iterable of identifiers")
    try:
        values = [_component(item, "material id") for item in material_ids]
    except TypeError as error:
        raise SchoolLearningError("material ids must be an iterable of identifiers") from error
    return sorted(set(values))


def ensure_topic(
    ws: Workspace,
    topic_id: str,
    title: str,
    material_ids: Iterable[str] = (),
) -> dict[str, Any]:
    safe_id = _component(topic_id, "topic_id")
    safe_title = _nonempty_string(title, "topic title").strip()
    normalized_materials = _normalize_material_ids(material_ids)
    state = _load_state(ws)
    known_materials = {item["id"] for item in state.materials["materials"]}
    missing = set(normalized_materials) - known_materials
    if missing:
        raise SchoolLearningError(f"unknown material ids: {', '.join(sorted(missing))}")
    topics = state.topics
    existing = next((item for item in topics["topics"] if item["id"] == safe_id), None)
    if existing is None:
        existing = {
            "id": safe_id,
            "title": safe_title,
            "status": "unseen",
            "material_ids": normalized_materials,
            "last_outcome": None,
            "last_session_id": None,
            "next_review_priority": 0,
            "note": "",
        }
        topics["topics"].append(existing)
    else:
        existing["title"] = safe_title
        existing["material_ids"] = normalized_materials
    topics["topics"].sort(key=lambda item: item["id"])
    _validate_topics(topics)
    _atomic_write_json(ws, ws.course_dir / "topics.json", topics)
    return dict(existing)


def build_study_brief(
    ws: Workspace,
    topic_id: str,
    mode: str,
    objective: str,
    *,
    output: Path | None = None,
) -> Path:
    safe_topic = _component(topic_id, "topic_id")
    if mode not in STUDY_MODES:
        raise SchoolLearningError("study mode must be explain, practice, or review")
    safe_objective = _nonempty_string(objective, "study objective").strip()
    state = _load_state(ws)
    materials = {item["id"]: item for item in state.materials["materials"]}
    topic = next((item for item in state.topics["topics"] if item["id"] == safe_topic), None)
    if topic is None:
        raise SchoolLearningError("topic does not exist")
    selected = [materials[item] for item in topic["material_ids"]]
    course = state.course
    lines = [
        "# School Learning Study Brief",
        "",
        f"- Course: {course['title']} (`{course['course_id']}`)",
        f"- Term: `{course['term']}`",
        f"- Topic: {topic['title']} (`{topic['id']}`)",
        f"- Mode: `{mode}`",
        f"- Current status: `{topic['status']}`",
        f"- Objective: {safe_objective}",
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
    destination = output if output is not None else ws.course_dir / "generated" / "study-brief.md"
    safe_destination = _confined_path(
        ws,
        destination,
        label="study brief output",
        regular_if_present=True,
    )
    _atomic_write_bytes(ws, safe_destination, "\n".join(lines).encode("utf-8"))
    return safe_destination


def record_session(
    ws: Workspace,
    topic_id: str,
    outcome: str,
    status: str,
    note: str,
    *,
    mode: str = "review",
    session_id: str | None = None,
    recorded_at: str | None = None,
    next_review_priority: int = 0,
) -> dict[str, Any]:
    safe_topic = _component(topic_id, "topic_id")
    if mode not in STUDY_MODES:
        raise SchoolLearningError("mode must be explain, practice, or review")
    if outcome not in OUTCOMES:
        raise SchoolLearningError("outcome must be correct, partial, or incorrect")
    if status not in TOPIC_STATUSES:
        raise SchoolLearningError("status must be unseen, learning, review, or solid")
    priority = _priority(next_review_priority)
    if not isinstance(note, str):
        raise SchoolLearningError("note must be a string")
    timestamp = _timestamp(recorded_at if recorded_at is not None else utc_now(), "session timestamp")
    safe_session = _component(
        session_id or timestamp.lower().replace(":", "-").replace("+", "-"),
        "session_id",
    )
    state = _load_state(ws)
    topic = next((item for item in state.topics["topics"] if item["id"] == safe_topic), None)
    if topic is None:
        raise SchoolLearningError("topic does not exist")
    session = {
        "schema_version": SESSION_SCHEMA,
        "session_id": safe_session,
        "recorded_at": timestamp,
        "course_id": ws.course_id,
        "term": ws.term,
        "topic_id": safe_topic,
        "mode": mode,
        "outcome": outcome,
        "status": status,
        "note": note.strip(),
        "next_review_priority": priority,
        "material_ids": list(topic["material_ids"]),
    }
    session_path = _confined_path(
        ws,
        ws.course_dir / "sessions" / f"{safe_session}.json",
        label="session destination",
        regular_if_present=True,
    )
    if session_path.exists():
        raise SchoolLearningError("session id already exists")
    _validate_session(session, session_path, ws)
    _atomic_write_json(ws, session_path, session)
    topic.update(
        {
            "status": status,
            "last_outcome": outcome,
            "last_session_id": safe_session,
            "next_review_priority": priority,
            "note": note.strip(),
        }
    )
    _validate_topics(state.topics)
    _atomic_write_json(ws, ws.course_dir / "topics.json", state.topics)
    return session


def iter_sessions(ws: Workspace) -> list[dict[str, Any]]:
    return list(_load_state(ws).sessions)


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
