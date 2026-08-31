"""Owner-controlled local semester and course workspace for School Learning."""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import stat
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable

COURSE_SCHEMA = "aiden.school.course/v0.1"
MATERIALS_SCHEMA = "aiden.school.materials/v0.1"
TOPICS_SCHEMA = "aiden.school.topics/v0.1"
SEMESTER_SCHEMA = "aiden.school.semester/v0.2"
COURSE_CORE_SCHEMA = "aiden.school.course-core/v0.2"
MATERIALS_V02_SCHEMA = "aiden.school.materials/v0.2"
SESSION_SCHEMA = "aiden.school.session/v0.1"
STUDY_HANDOFF_SCHEMA = "aiden.school.study-handoff/v0.1.1"
COURSE_HANDOFF_SCHEMA = "aiden.school.course-handoff/v0.3"
SOURCE_OBSERVATIONS_SCHEMA = "aiden.school.source-observations/v0.1"
REVIEWED_UPDATE_SCHEMA = "aiden.school.reviewed-update/v0.1"
UPDATE_CONTRACT_SCHEMA = "aiden.school.update-contract/v0.1"
SUPPORTED_SUFFIXES = {
    ".pdf": "pdf",
    ".md": "markdown",
    ".txt": "text",
    ".pptx": "powerpoint",
    ".rmd": "r-markdown",
    ".png": "png",
    ".jpg": "jpeg",
    ".jpeg": "jpeg",
    ".webp": "webp",
}
STUDY_MODES = ("explain", "practice", "review")
TOPIC_STATUSES = ("unseen", "learning", "review", "solid")
OUTCOMES = ("correct", "partial", "incorrect")
CAPABILITY_TAGS = (
    "exam-mastery",
    "prerequisite-repair",
    "creative-applied-work",
    "project-based",
    "team-based",
    "tool-skill",
    "reading-listening",
    "attendance-sensitive",
    "equipment-logistics",
    "ai-policy-sensitive",
)
MATERIAL_KINDS = (
    "unspecified",
    "lecture",
    "reading",
    "listening-reference",
    "assignment-specification",
    "syllabus",
    "announcement",
    "lab-field-guide",
    "technical-reference",
    "other",
)
MATERIAL_LIFECYCLES = ("upcoming", "current", "reference", "completed", "superseded")
ASSESSMENT_TYPES = (
    "quiz",
    "exam",
    "problem-set",
    "programming-assignment",
    "homework",
    "practice-sheet",
    "creative-assignment",
    "project",
    "sprint",
    "field-lab-activity",
    "other",
)
ASSESSMENT_STATUSES = (
    "upcoming",
    "available",
    "in-progress",
    "submitted",
    "graded",
    "reviewed",
)
CLAIM_STATUSES = ("confirmed", "provisional", "conflicted", "superseded")
SOURCE_OBSERVATION_SCOPES = ("full", "partial")
SOURCE_OBSERVATION_OUTCOMES = ("changed", "no-relevant-change", "unavailable")
REVIEWED_OPERATION_KINDS = (
    "assessment-upsert",
    "policy-upsert",
    "source-upsert",
    "source-observation",
)
PLANNER_CRITICAL_CLAIM_FIELDS = ("due-at", "available-at", "available-until")
_UPDATE_CONTRACT_RULES = (
    "Return one JSON object only, as data; do not return commands or executable code.",
    "Use only the exact operation keys and bounded values declared by this contract.",
    "Assessment and policy operations require one or more sourced claims with exact claim keys.",
    "Identifier relationship lists must be sorted and unique; nullable grading measures use JSON null.",
    "Source-observation IDs are append-only identities: each must be absent from base source observations and all prior source-observation operations in this ordered candidate.",
    "Never use the legacy due field; use due-at for normalized forward scheduling.",
    "Use due-at, available-at, and available-until for planner-critical claims, with YYYY-MM-DD or the canonical School Learning timestamp subset: seconds, an explicit Z/numeric offset, and optional 1-through-6-digit fractional seconds.",
    "Do not include raw material bytes, intake requests, paths, arbitrary writes, or external actions.",
    "Do not include learner, topic, session, mastery, or cross-course updates.",
    "The returned JSON is only a reviewed candidate and does not change local state.",
)
_COMPONENT = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_SCHOOL_TIMESTAMP = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$"
)
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_ASSESSMENT_TYPE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_ASSESSMENT_TYPE_MAX_LENGTH = 64
_REVIEWED_UPDATE_MAX_OPERATIONS = 100
_REVIEWED_UPDATE_MAX_BYTES = 1_000_000
_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_REQUIRED_DIRECTORIES = ("materials", "sessions", "generated")
_SEMESTER_METADATA_DIRECTORY = ".school-learning"


class _Unset:
    pass


_UNSET = _Unset()

_COURSE_KEYS = frozenset({"schema_version", "course_id", "term", "title", "created_at"})
_MATERIALS_KEYS = frozenset({"schema_version", "materials"})
_MATERIAL_KEYS = frozenset(
    {"id", "title", "type", "source_name", "stored_path", "sha256", "bytes", "added_at"}
)
_MATERIAL_V02_KEYS = _MATERIAL_KEYS | frozenset(
    {"kind", "status", "relevant_date", "topic_ids", "assessment_ids", "provenance"}
)
_PROVENANCE_KEYS = frozenset({"source", "observed_at", "status"})
_CLAIM_KEYS = frozenset({"id", "field", "value", "source", "observed_at", "status"})
_SEMESTER_KEYS = frozenset({"schema_version", "term", "title", "course_ids", "created_at"})
_COURSE_CORE_KEYS = frozenset(
    {
        "schema_version",
        "course_id",
        "term",
        "capability_tags",
        "sources",
        "metadata",
        "assessments",
        "policies",
        "created_at",
        "updated_at",
    }
)
_SOURCE_KEYS = frozenset({"id", "title", "reference", "status"})
_ASSESSMENT_KEYS = frozenset(
    {
        "id",
        "title",
        "type",
        "status",
        "weight",
        "points",
        "xp",
        "material_ids",
        "topic_ids",
        "claims",
    }
)
_POLICY_KEYS = frozenset({"id", "title", "category", "status", "claims"})
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
_HANDOFF_KEYS = frozenset(
    {
        "schema_version",
        "course_id",
        "term",
        "topic_id",
        "mode",
        "objective",
        "attachment_filenames",
        "material_ids",
        "materials",
    }
)
_HANDOFF_MATERIAL_KEYS = frozenset({"id", "attachment_filename", "sha256", "bytes"})
_COURSE_HANDOFF_KEYS = frozenset(
    {
        "schema_version",
        "course_id",
        "term",
        "attachment_filenames",
        "context_attachment",
        "update_contract_attachment",
        "material_ids",
        "materials",
    }
)
_COURSE_HANDOFF_CONTEXT_KEYS = frozenset(
    {"role", "attachment_filename", "sha256", "bytes"}
)
_SOURCE_OBSERVATIONS_KEYS = frozenset({"schema_version", "observations"})
_SOURCE_OBSERVATION_KEYS = frozenset(
    {"id", "source_id", "observed_at", "scope", "outcome", "material_ids", "note"}
)
_REVIEWED_UPDATE_KEYS = frozenset(
    {"schema_version", "term", "course_id", "base_context_sha256", "operations"}
)
_REVIEWED_CLAIM_KEYS = frozenset({"field", "value", "source", "observed_at", "status"})
_REVIEWED_ASSESSMENT_KEYS = frozenset(
    {
        "kind",
        "id",
        "title",
        "type",
        "status",
        "weight",
        "points",
        "xp",
        "material_ids",
        "topic_ids",
        "claims",
        "recorded_at",
    }
)
_REVIEWED_POLICY_KEYS = frozenset(
    {"kind", "id", "title", "category", "claims", "recorded_at"}
)
_REVIEWED_SOURCE_KEYS = frozenset(
    {"kind", "id", "title", "reference", "status", "recorded_at"}
)
_REVIEWED_OBSERVATION_KEYS = _SOURCE_OBSERVATION_KEYS | frozenset({"kind"})
_UPDATE_CONTRACT_KEYS = frozenset(
    {
        "schema_version",
        "reviewed_update_schema_version",
        "term",
        "course_id",
        "base_context_sha256",
        "allowed_operation_kinds",
        "candidate_keys",
        "operation_keys",
        "claim_keys",
        "bounded_values",
        "max_operations",
        "constraints",
        "rules",
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
class SemesterWorkspace:
    data_root: Path
    term: str
    term_dir: Path


@dataclass(frozen=True)
class _State:
    course: dict[str, Any]
    materials: dict[str, Any]
    topics: dict[str, Any]
    sessions: tuple[dict[str, Any], ...]
    core: dict[str, Any] | None = None
    source_observations: dict[str, Any] | None = None


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


def _date(value: object, label: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not _DATE.fullmatch(value):
        raise SchoolLearningError(f"{label} must be a canonical YYYY-MM-DD date")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
    except ValueError as error:
        raise SchoolLearningError(f"{label} must be a valid date") from error
    if parsed.strftime("%Y-%m-%d") != value:
        raise SchoolLearningError(f"{label} must be a canonical date")
    return value


def _observed_at(value: object, label: str) -> str:
    if isinstance(value, str) and _DATE.fullmatch(value):
        return _date(value, label) or ""  # pragma: no cover - non-optional contract
    _school_timestamp_datetime(value, label)
    return value


def _school_timestamp_datetime(value: object, label: str) -> datetime:
    if not isinstance(value, str) or not _SCHOOL_TIMESTAMP.fullmatch(value):
        raise SchoolLearningError(
            f"{label} must use the canonical School Learning timestamp subset with "
            "seconds, an explicit Z/offset, and at most 6 fractional-second digits"
        )
    date_text = value[:10]
    zone_text = "Z" if value.endswith("Z") else value[-6:]
    clock_text = value[11:-1] if zone_text == "Z" else value[11:-6]
    whole_seconds, separator, fraction = clock_text.partition(".")
    if separator:
        microsecond = int(fraction.ljust(6, "0"))
    else:
        microsecond = 0
    if zone_text == "Z":
        zone = timezone.utc
    else:
        offset_hours = int(zone_text[1:3])
        offset_minutes = int(zone_text[4:6])
        if offset_hours > 23 or offset_minutes > 59:
            raise SchoolLearningError(f"{label} has an invalid numeric timezone offset")
        offset = timedelta(hours=offset_hours, minutes=offset_minutes)
        zone = timezone(-offset if zone_text[0] == "-" else offset)
    try:
        parsed = datetime(
            int(date_text[0:4]),
            int(date_text[5:7]),
            int(date_text[8:10]),
            int(whole_seconds[0:2]),
            int(whole_seconds[3:5]),
            int(whole_seconds[6:8]),
            microsecond=microsecond,
            tzinfo=zone,
        )
    except ValueError as error:
        raise SchoolLearningError(
            f"{label} must be a valid canonical School Learning timestamp"
        ) from error
    return parsed


def _nonempty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SchoolLearningError(f"{label} must be nonempty")
    return value


def _normalize_assessment_type(value: object, label: str = "assessment type") -> str:
    text = _nonempty_string(value, label).strip().lower()
    normalized = re.sub(r"\s+", "-", text)
    if len(normalized) > _ASSESSMENT_TYPE_MAX_LENGTH or not _ASSESSMENT_TYPE.fullmatch(normalized):
        raise SchoolLearningError(
            f"{label} must be at most {_ASSESSMENT_TYPE_MAX_LENGTH} lowercase letters, "
            "digits, or single hyphen-separated words"
        )
    return normalized


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


def semester_workspace(data_root: Path | str, term: str) -> SemesterWorkspace:
    root = _resolved_data_root(data_root)
    safe_term = _component(term, "term")
    return SemesterWorkspace(root, safe_term, root / safe_term)


def _semester_metadata_dir(sw: SemesterWorkspace) -> Path:
    return _semester_dir(sw) / _SEMESTER_METADATA_DIRECTORY


def _semester_state_path(sw: SemesterWorkspace) -> Path:
    return _semester_metadata_dir(sw) / "semester.json"


def _semester_generated_dir(sw: SemesterWorkspace) -> Path:
    return _semester_metadata_dir(sw) / "generated"


def _semester_dir(sw: SemesterWorkspace) -> Path:
    if not isinstance(sw, SemesterWorkspace):
        raise SchoolLearningError("semester workspace is invalid")
    root = _resolved_data_root(sw.data_root)
    safe_term = _component(sw.term, "term")
    expected = root / safe_term
    if sw.data_root != root or sw.term_dir != expected:
        raise SchoolLearningError("semester identity or path is inconsistent")
    return expected


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


def _term_confined_path(
    sw: SemesterWorkspace,
    path: Path | str,
    *,
    label: str,
    must_exist: bool = False,
    require_file: bool = False,
    require_directory: bool = False,
    regular_if_present: bool = False,
) -> Path:
    base = _semester_dir(sw)
    candidate = _lexical_absolute(path)
    try:
        if base.is_symlink():
            raise SchoolLearningError("semester workspace must not be a symlink")
        if base.exists() and not base.is_dir():
            raise SchoolLearningError("semester workspace must be a real directory")
    except SchoolLearningError:
        raise
    except OSError as error:
        raise SchoolLearningError("semester workspace cannot be safely inspected") from error
    try:
        relative = candidate.relative_to(base)
    except ValueError as error:
        raise SchoolLearningError(f"{label} must remain inside the semester workspace") from error
    current = base
    try:
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                raise SchoolLearningError(f"{label} must not use symlinks")
            if current != candidate and current.exists() and not current.is_dir():
                raise SchoolLearningError(f"{label} has a non-directory parent")
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(base.resolve(strict=False))
        exists = candidate.exists()
        if must_exist and not exists:
            raise SchoolLearningError(f"missing {label}")
        if exists and (require_file or regular_if_present):
            if not stat.S_ISREG(os.lstat(candidate).st_mode):
                raise SchoolLearningError(f"{label} must be a regular file")
        if exists and require_directory and not candidate.is_dir():
            raise SchoolLearningError(f"{label} must be a directory")
    except SchoolLearningError:
        raise
    except (OSError, RuntimeError, ValueError) as error:
        raise SchoolLearningError(f"{label} cannot be safely inspected") from error
    return candidate


def _atomic_term_bytes(sw: SemesterWorkspace, path: Path, content: bytes) -> None:
    destination = _term_confined_path(sw, path, label="semester write target", regular_if_present=True)
    parent = _term_confined_path(
        sw,
        destination.parent,
        label="semester write parent",
        must_exist=True,
        require_directory=True,
    )
    try:
        fd, name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=parent)
        temporary = Path(name)
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        _term_confined_path(sw, temporary, label="semester temporary file", must_exist=True, require_file=True)
        _term_confined_path(
            sw, destination, label="semester write target", regular_if_present=True
        )
        os.replace(temporary, destination)
    except SchoolLearningError:
        raise
    except (OSError, TypeError, ValueError) as error:
        raise SchoolLearningError("atomic semester write failed") from error
    finally:
        if "temporary" in locals():
            try:
                if temporary.exists() or temporary.is_symlink():
                    _term_confined_path(
                        sw,
                        temporary,
                        label="semester temporary file",
                        regular_if_present=True,
                    ).unlink(missing_ok=True)
            except OSError as error:
                raise SchoolLearningError("semester temporary file could not be removed") from error


def _atomic_term_json(sw: SemesterWorkspace, path: Path, value: dict[str, Any]) -> None:
    try:
        content = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    except (TypeError, ValueError) as error:
        raise SchoolLearningError("semester state cannot be encoded as JSON") from error
    _atomic_term_bytes(sw, path, content.encode("utf-8"))


def _read_term_json(sw: SemesterWorkspace, path: Path, label: str) -> dict[str, Any]:
    content = _read_term_bytes(sw, path, label)
    try:
        value = json.loads(content.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise SchoolLearningError(f"invalid JSON state: {Path(path).name}") from error
    if not isinstance(value, dict):
        raise SchoolLearningError(f"{label} must contain a JSON object")
    return value


def _read_term_bytes(sw: SemesterWorkspace, path: Path, label: str) -> bytes:
    safe = _term_confined_path(sw, path, label=label, must_exist=True, require_file=True)
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
        raise SchoolLearningError(f"{label} could not be read safely") from error


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


def _safe_create_directory(
    path: Path,
    label: str,
    created: list[Path] | None = None,
) -> bool:
    try:
        if path.is_symlink():
            raise SchoolLearningError(f"{label} must not be a symlink")
        path.mkdir()
        if created is not None:
            created.append(path)
        if path.is_symlink() or not path.is_dir():
            raise SchoolLearningError(f"{label} could not be created safely")
        return True
    except FileExistsError:
        if path.is_symlink() or not path.is_dir():
            raise SchoolLearningError(f"{label} must be a real directory")
        return False
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


def _safe_create_directory_chain_tracking(
    path: Path, label: str, created: list[Path]
) -> None:
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
        _safe_create_directory(directory, label, created)


def _rollback_created_directories(created: list[Path], label: str) -> list[str]:
    errors: list[str] = []
    for directory in reversed(created):
        try:
            if not directory.exists() and not directory.is_symlink():
                continue
            if directory.is_symlink() or not directory.is_dir():
                raise SchoolLearningError(f"{label} created path is not a real directory")
            directory.rmdir()
        except (OSError, SchoolLearningError) as error:
            errors.append(f"{directory}: {error}")
    return errors


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


def _inspect_real_tree(ws: Workspace, path: Path, label: str) -> Path:
    root = _confined_path(
        ws,
        path,
        label=label,
        must_exist=True,
        require_directory=True,
    )
    try:
        entries = sorted(root.iterdir(), key=lambda item: item.name)
    except OSError as error:
        raise SchoolLearningError(f"{label} cannot be inspected safely") from error
    for entry in entries:
        try:
            mode = os.lstat(entry).st_mode
        except OSError as error:
            raise SchoolLearningError(f"{label} cannot be inspected safely") from error
        if stat.S_ISLNK(mode):
            raise SchoolLearningError(f"{label} must not contain symlinks")
        if stat.S_ISDIR(mode):
            _inspect_real_tree(ws, entry, label)
        elif not stat.S_ISREG(mode):
            raise SchoolLearningError(f"{label} must contain only regular files and directories")
        else:
            _confined_path(ws, entry, label=label, must_exist=True, require_file=True)
    return root


def _remove_real_tree(ws: Workspace, path: Path, label: str) -> None:
    root = _inspect_real_tree(ws, path, label)
    try:
        entries = sorted(root.iterdir(), key=lambda item: item.name, reverse=True)
    except OSError as error:
        raise SchoolLearningError(f"{label} cannot be removed safely") from error
    for entry in entries:
        try:
            mode = os.lstat(entry).st_mode
        except OSError as error:
            raise SchoolLearningError(f"{label} cannot be removed safely") from error
        if stat.S_ISDIR(mode):
            _remove_real_tree(ws, entry, label)
        else:
            _safe_unlink(ws, entry, label)
    try:
        root.rmdir()
    except OSError as error:
        raise SchoolLearningError(f"{label} cannot be removed safely") from error


def _safe_remove_tree(ws: Workspace, path: Path, label: str) -> None:
    _remove_real_tree(ws, path, label)


def _restore_empty_course_workspace(ws: Workspace, label: str) -> None:
    root = _inspect_real_tree(ws, ws.course_dir, label)
    try:
        entries = sorted(root.iterdir(), key=lambda item: item.name, reverse=True)
    except OSError as error:
        raise SchoolLearningError(f"{label} cannot be inspected safely") from error
    for entry in entries:
        try:
            mode = os.lstat(entry).st_mode
        except OSError as error:
            raise SchoolLearningError(f"{label} cannot be inspected safely") from error
        if stat.S_ISDIR(mode):
            _safe_remove_tree(ws, entry, label)
        else:
            _safe_unlink(ws, entry, label)


def _create_temp_directory(ws: Workspace, parent: Path, prefix: str) -> Path:
    safe_parent = _confined_path(
        ws,
        parent,
        label="temporary-directory parent",
        must_exist=True,
        require_directory=True,
    )
    try:
        path = Path(tempfile.mkdtemp(prefix=prefix, dir=safe_parent))
    except OSError as error:
        raise SchoolLearningError("confined temporary directory could not be created") from error
    return _confined_path(
        ws,
        path,
        label="temporary directory",
        must_exist=True,
        require_directory=True,
    )


def _safe_replace_directory(ws: Workspace, source: Path, destination: Path, label: str) -> None:
    safe_source = _confined_path(
        ws,
        source,
        label=f"{label} source",
        must_exist=True,
        require_directory=True,
    )
    safe_destination = _confined_path(
        ws,
        destination,
        label=f"{label} destination",
        require_directory=True,
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


def _prepare_directory_replace(
    ws: Workspace,
    source: Path,
    destination: Path,
    label: str,
) -> tuple[Path, Path]:
    safe_source = _confined_path(
        ws,
        source,
        label=f"{label} source",
        must_exist=True,
        require_directory=True,
    )
    safe_destination = _confined_path(
        ws,
        destination,
        label=f"{label} destination",
        require_directory=True,
    )
    _confined_path(
        ws,
        safe_destination.parent,
        label=f"{label} parent",
        must_exist=True,
        require_directory=True,
    )
    return safe_source, safe_destination


def _copy_real_tree(ws: Workspace, source: Path, destination: Path, label: str) -> None:
    safe_source = _inspect_real_tree(ws, source, f"{label} source")
    safe_destination = _confined_path(
        ws,
        destination,
        label=f"{label} destination",
        require_directory=True,
    )
    _safe_create_directory(safe_destination, f"{label} destination")
    try:
        entries = sorted(safe_source.iterdir(), key=lambda item: item.name)
    except OSError as error:
        raise SchoolLearningError(f"{label} source cannot be copied safely") from error
    for entry in entries:
        try:
            mode = os.lstat(entry).st_mode
        except OSError as error:
            raise SchoolLearningError(f"{label} source cannot be copied safely") from error
        target = safe_destination / entry.name
        if stat.S_ISDIR(mode):
            _copy_real_tree(ws, entry, target, label)
            continue
        if not stat.S_ISREG(mode):
            raise SchoolLearningError(f"{label} source must contain only regular files")
        content = _read_regular_bytes(ws, entry, f"{label} source file")
        _atomic_write_bytes(ws, target, content)
        if _read_regular_bytes(ws, entry, f"{label} source file") != content:
            raise SchoolLearningError(f"{label} source changed while it was copied")
        if _read_regular_bytes(ws, target, f"{label} copied file") != content:
            raise SchoolLearningError(f"{label} copy is not byte-identical")


def _record_recovery_error(causal: SchoolLearningError, label: str, error: BaseException) -> None:
    detail = f"{label}: {type(error).__name__}: {error}"
    recorded = getattr(causal, "recovery_errors", ())
    causal.recovery_errors = (*recorded, detail)


def _directory_is_present(ws: Workspace, path: Path, label: str) -> bool:
    try:
        mode = os.lstat(path).st_mode
    except FileNotFoundError:
        return False
    except OSError as error:
        raise SchoolLearningError(f"{label} cannot be inspected safely") from error
    if not stat.S_ISDIR(mode):
        raise SchoolLearningError(f"{label} must be a real directory")
    _confined_path(
        ws,
        path,
        label=label,
        must_exist=True,
        require_directory=True,
    )
    return True


def _reconcile_directory_replace(
    ws: Workspace,
    source: Path,
    destination: Path,
    label: str,
    causal: SchoolLearningError,
) -> bool | None:
    try:
        source_present = _directory_is_present(ws, source, f"{label} source")
        destination_present = _directory_is_present(ws, destination, f"{label} destination")
    except SchoolLearningError as error:
        _record_recovery_error(causal, f"{label} effect reconciliation failed", error)
        return None
    if not source_present and destination_present:
        return True
    if source_present and not destination_present:
        return False
    _record_recovery_error(
        causal,
        f"{label} effect reconciliation failed",
        SchoolLearningError("rename source and destination are in an unexpected state"),
    )
    return None


def _recover_replace_directory(
    ws: Workspace,
    source: Path,
    destination: Path,
    label: str,
    causal: SchoolLearningError,
) -> bool:
    try:
        _safe_replace_directory(ws, source, destination, label)
        return True
    except SchoolLearningError as error:
        _record_recovery_error(causal, f"{label} first attempt failed", error)
        effect = _reconcile_directory_replace(ws, source, destination, label, causal)
        if effect is True:
            return True
    try:
        safe_source = _confined_path(
            ws,
            source,
            label=f"{label} source",
            must_exist=True,
            require_directory=True,
        )
        safe_destination = _confined_path(
            ws,
            destination,
            label=f"{label} destination",
            require_directory=True,
        )
        _confined_path(
            ws,
            safe_destination.parent,
            label=f"{label} parent",
            must_exist=True,
            require_directory=True,
        )
        os.replace(safe_source, safe_destination)
        return True
    except (OSError, SchoolLearningError) as error:
        _record_recovery_error(causal, f"{label} fallback failed", error)
        effect = _reconcile_directory_replace(ws, source, destination, label, causal)
        return effect is True


def _recover_remove_tree(
    ws: Workspace,
    path: Path,
    label: str,
    causal: SchoolLearningError,
) -> bool:
    if not path.exists() and not path.is_symlink():
        return True
    try:
        _safe_remove_tree(ws, path, label)
        return True
    except SchoolLearningError as error:
        _record_recovery_error(causal, f"{label} first attempt failed", error)
        if not path.exists() and not path.is_symlink():
            return True
    try:
        _remove_real_tree(ws, path, label)
        return True
    except SchoolLearningError as error:
        _record_recovery_error(causal, f"{label} fallback failed", error)
        return False


def _recover_remove_empty_directory(
    ws: Workspace,
    path: Path,
    label: str,
    causal: SchoolLearningError,
) -> bool:
    if not path.exists() and not path.is_symlink():
        return True
    try:
        safe = _confined_path(
            ws,
            path,
            label=label,
            must_exist=True,
            require_directory=True,
        )
        safe.rmdir()
        return True
    except (OSError, SchoolLearningError) as error:
        _record_recovery_error(causal, f"{label} first attempt failed", error)
        if not path.exists() and not path.is_symlink():
            return True
    try:
        safe = _confined_path(
            ws,
            path,
            label=label,
            must_exist=True,
            require_directory=True,
        )
        safe.rmdir()
        return True
    except (OSError, SchoolLearningError) as error:
        _record_recovery_error(causal, f"{label} fallback failed", error)
        return False


def _rollback_directory_publication(
    ws: Workspace,
    transaction: Path,
    destination: Path,
    rollback: Path,
    retiring: Path,
    *,
    new_published: bool,
    causal: SchoolLearningError,
) -> None:
    failed_new = transaction / "failed-new"
    prior_restored = not new_published and destination.exists()
    if new_published and (destination.exists() or destination.is_symlink()):
        new_preserved = _recover_replace_directory(
            ws,
            destination,
            failed_new,
            "failed-new study handoff preservation",
            causal,
        )
        if not new_preserved and (destination.exists() or destination.is_symlink()):
            _recover_remove_tree(ws, destination, "failed-new study handoff cleanup", causal)
    if not destination.exists() and rollback.exists():
        prior_restored = _recover_replace_directory(
            ws,
            rollback,
            destination,
            "study handoff rollback",
            causal,
        )
    if retiring.exists() or retiring.is_symlink():
        _recover_remove_tree(ws, retiring, "partial retired study handoff", causal)
    if failed_new.exists() or failed_new.is_symlink():
        _recover_remove_tree(ws, failed_new, "failed-new study handoff cleanup", causal)
    if prior_restored and (rollback.exists() or rollback.is_symlink()):
        _recover_remove_tree(ws, rollback, "redundant study handoff rollback", causal)
    if prior_restored:
        _recover_remove_empty_directory(
            ws,
            transaction,
            "study handoff transaction placeholder cleanup",
            causal,
        )


def _publication_error(label: str, error: BaseException) -> SchoolLearningError:
    if isinstance(error, SchoolLearningError):
        return error
    causal = SchoolLearningError(f"{label} could not be completed safely")
    causal.__cause__ = error
    return causal


def _cleanup_committed_publication(
    ws: Workspace,
    transaction: Path,
    rollback: Path,
) -> None:
    cleanup = SchoolLearningError("committed study handoff cleanup encountered an error")
    _recover_remove_tree(
        ws,
        rollback,
        "completed study handoff rollback copy",
        cleanup,
    )
    _recover_remove_empty_directory(
        ws,
        transaction,
        "completed study handoff transaction placeholder",
        cleanup,
    )


def _publish_directory(
    ws: Workspace,
    staging: Path,
    destination: Path,
    final_validator: Callable[[], None],
) -> None:
    safe_staging = _inspect_real_tree(ws, staging, "study handoff staging directory")
    safe_destination = _confined_path(
        ws,
        destination,
        label="study handoff destination",
        require_directory=True,
    )
    destination_exists = safe_destination.exists()
    if not destination_exists:
        publication_source, publication_destination = _prepare_directory_replace(
            ws,
            safe_staging,
            safe_destination,
            "study handoff publication",
        )
        final_validator()
        try:
            os.replace(publication_source, publication_destination)
        except Exception as error:
            causal = _publication_error("study handoff publication", error)
            published = _reconcile_directory_replace(
                ws,
                publication_source,
                publication_destination,
                "study handoff publication",
                causal,
            )
            if published:
                _recover_remove_tree(
                    ws,
                    publication_destination,
                    "failed first study handoff publication",
                    causal,
                )
            if causal is error:
                raise
            raise causal from error
        return

    _inspect_real_tree(ws, safe_destination, "existing study handoff")
    transaction = _create_temp_directory(
        ws,
        safe_destination.parent,
        ".study-handoff.transaction.",
    )
    rollback = transaction / "rollback"
    retiring = transaction / "retiring"
    old_moved = False
    new_published = False
    try:
        _copy_real_tree(
            ws,
            safe_destination,
            rollback,
            "study handoff rollback copy",
        )
        retirement_source, retirement_destination = _prepare_directory_replace(
            ws,
            safe_destination,
            retiring,
            "study handoff retirement",
        )
        publication_source, publication_destination = _prepare_directory_replace(
            ws,
            safe_staging,
            safe_destination,
            "study handoff publication",
        )
        final_validator()
        try:
            os.replace(retirement_source, retirement_destination)
        except Exception as error:
            causal = _publication_error("study handoff retirement", error)
            old_moved = _reconcile_directory_replace(
                ws,
                retirement_source,
                retirement_destination,
                "study handoff retirement",
                causal,
            ) is not False
            if causal is error:
                raise
            raise causal from error
        old_moved = True
        final_validator()
        try:
            os.replace(publication_source, publication_destination)
        except Exception as error:
            causal = _publication_error("study handoff publication", error)
            new_published = _reconcile_directory_replace(
                ws,
                publication_source,
                publication_destination,
                "study handoff publication",
                causal,
            ) is not False
            if causal is error:
                raise
            raise causal from error
        new_published = True
        _safe_remove_tree(ws, retiring, "retired study handoff")

        # Irreversible commit point: the new handoff is published and retirement
        # completed while the untouched rollback copy still made every earlier
        # failure recoverable. Cleanup after this point cannot report failure.
        old_moved = False
        new_published = False
        _cleanup_committed_publication(ws, transaction, rollback)
    except SchoolLearningError as error:
        if old_moved or not safe_destination.exists():
            _rollback_directory_publication(
                ws,
                transaction,
                safe_destination,
                rollback,
                retiring,
                new_published=new_published,
                causal=error,
            )
        else:
            _recover_remove_tree(
                ws,
                transaction,
                "failed study handoff publication transaction",
                error,
            )
        raise


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


def _validate_provenance(value: object, label: str, *, optional: bool = False) -> dict[str, Any] | None:
    if value is None and optional:
        return None
    record = _exact_object(value, _PROVENANCE_KEYS, label)
    _nonempty_string(record["source"], f"{label} source")
    _observed_at(record["observed_at"], f"{label} observed date")
    if record["status"] not in CLAIM_STATUSES:
        raise SchoolLearningError(f"{label} status is invalid")
    return record


def _validate_claim(value: object, label: str) -> dict[str, Any]:
    record = _exact_object(value, _CLAIM_KEYS, label)
    _component(record["id"], f"{label} id")
    _component(record["field"], f"{label} field")
    _nonempty_string(record["value"], f"{label} value")
    _nonempty_string(record["source"], f"{label} source")
    _observed_at(record["observed_at"], f"{label} observed date")
    if record["status"] not in CLAIM_STATUSES:
        raise SchoolLearningError(f"{label} status is invalid")
    return record


def _validate_claim_set_invariant(claims: list[dict[str, Any]], label: str) -> None:
    fields = sorted({item["field"] for item in claims})
    for field in fields:
        active = [
            item for item in claims if item["field"] == field and item["status"] != "superseded"
        ]
        values = {item["value"] for item in active}
        if len(values) > 1 and any(item["status"] != "conflicted" for item in active):
            raise SchoolLearningError(
                f"{label} field {field} has differing active values that are not all conflicted"
            )
        if len(values) <= 1 and any(item["status"] == "conflicted" for item in active):
            raise SchoolLearningError(
                f"{label} field {field} has conflicted claims without an active disagreement"
            )


def _normalize_claim_sets(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for field in sorted({item["field"] for item in claims}):
        active = [
            item for item in claims if item["field"] == field and item["status"] != "superseded"
        ]
        if len({item["value"] for item in active}) > 1:
            for item in active:
                item["status"] = "conflicted"
        else:
            for item in active:
                if item["status"] == "conflicted":
                    item["status"] = "provisional"
    claims.sort(key=lambda item: item["id"])
    _validate_claim_set_invariant(claims, "claims")
    return claims


def _aggregate_claim_status(claims: list[dict[str, Any]]) -> str:
    _validate_claim_set_invariant(claims, "policy claims")
    active_statuses = {item["status"] for item in claims if item["status"] != "superseded"}
    for status in ("conflicted", "confirmed", "provisional"):
        if status in active_statuses:
            return status
    return "superseded"


def _validate_claims(value: object, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise SchoolLearningError(f"{label} must be a list")
    records = [_validate_claim(item, f"{label} entry") for item in value]
    ids = [item["id"] for item in records]
    if len(set(ids)) != len(ids):
        raise SchoolLearningError(f"{label} identifiers must be unique")
    if ids != sorted(ids):
        raise SchoolLearningError(f"{label} must be sorted by identifier")
    _validate_claim_set_invariant(records, label)
    return records


def _validate_material(value: object, schema: str = MATERIALS_SCHEMA) -> dict[str, Any]:
    keys = _MATERIAL_V02_KEYS if schema == MATERIALS_V02_SCHEMA else _MATERIAL_KEYS
    record = _exact_object(value, keys, "material record")
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
    if schema == MATERIALS_V02_SCHEMA:
        if record["kind"] not in MATERIAL_KINDS:
            raise SchoolLearningError("material kind is invalid")
        if record["status"] not in MATERIAL_LIFECYCLES:
            raise SchoolLearningError("material lifecycle is invalid")
        _date(record["relevant_date"], "material relevant date", optional=True)
        _identifier_list(record["topic_ids"], "material topic ids")
        _identifier_list(record["assessment_ids"], "material assessment ids")
        _validate_provenance(record["provenance"], "material provenance", optional=True)
    return record


def _validate_materials(value: object) -> dict[str, Any]:
    manifest = _exact_object(value, _MATERIALS_KEYS, "materials manifest")
    if manifest["schema_version"] not in {MATERIALS_SCHEMA, MATERIALS_V02_SCHEMA}:
        raise SchoolLearningError("unsupported materials schema")
    if not isinstance(manifest["materials"], list):
        raise SchoolLearningError("materials must be a list")
    seen: set[str] = set()
    for value_record in manifest["materials"]:
        record = _validate_material(value_record, manifest["schema_version"])
        if record["id"] in seen:
            raise SchoolLearningError("material identifiers must be unique")
        seen.add(record["id"])
    return manifest


def _validate_semester(value: object, sw: SemesterWorkspace) -> dict[str, Any]:
    record = _exact_object(value, _SEMESTER_KEYS, "semester record")
    if record["schema_version"] != SEMESTER_SCHEMA:
        raise SchoolLearningError("unsupported semester schema")
    if _component(record["term"], "semester term") != sw.term:
        raise SchoolLearningError("semester term does not match its workspace")
    _nonempty_string(record["title"], "semester title")
    course_ids = _identifier_list(record["course_ids"], "semester course ids")
    if course_ids != sorted(course_ids):
        raise SchoolLearningError("semester course ids must be sorted")
    _timestamp(record["created_at"], "semester creation timestamp")
    return record


def _validate_source(value: object) -> dict[str, Any]:
    record = _exact_object(value, _SOURCE_KEYS, "course source descriptor")
    _component(record["id"], "course source id")
    _nonempty_string(record["title"], "course source title")
    _nonempty_string(record["reference"], "course source reference")
    if record["status"] not in CLAIM_STATUSES:
        raise SchoolLearningError("course source status is invalid")
    return record


def _optional_measure(value: object, label: str) -> str | None:
    if value is None:
        return None
    return _nonempty_string(value, label).strip()


def _validate_assessment(value: object) -> dict[str, Any]:
    record = _exact_object(value, _ASSESSMENT_KEYS, "assessment record")
    _component(record["id"], "assessment id")
    _nonempty_string(record["title"], "assessment title")
    if _normalize_assessment_type(record["type"]) != record["type"]:
        raise SchoolLearningError("assessment type must use its deterministic normalized form")
    if record["status"] not in ASSESSMENT_STATUSES:
        raise SchoolLearningError("assessment status is invalid")
    _optional_measure(record["weight"], "assessment weight")
    _optional_measure(record["points"], "assessment points")
    _optional_measure(record["xp"], "assessment XP")
    _identifier_list(record["material_ids"], "assessment material ids")
    _identifier_list(record["topic_ids"], "assessment topic ids")
    _validate_claims(record["claims"], "assessment claims")
    return record


def _validate_policy(value: object) -> dict[str, Any]:
    record = _exact_object(value, _POLICY_KEYS, "policy record")
    _component(record["id"], "policy id")
    _nonempty_string(record["title"], "policy title")
    _component(record["category"], "policy category")
    if record["status"] not in CLAIM_STATUSES:
        raise SchoolLearningError("policy status is invalid")
    claims = _validate_claims(record["claims"], "policy claims")
    if not claims:
        raise SchoolLearningError("policy must preserve at least one sourced rule claim")
    if record["status"] != _aggregate_claim_status(claims):
        raise SchoolLearningError("policy status does not match its active claim set")
    return record


def _validate_course_core(value: object, ws: Workspace) -> dict[str, Any]:
    record = _exact_object(value, _COURSE_CORE_KEYS, "course core record")
    if record["schema_version"] != COURSE_CORE_SCHEMA:
        raise SchoolLearningError("unsupported course core schema")
    if _component(record["course_id"], "course core id") != ws.course_id:
        raise SchoolLearningError("course core id does not match its workspace")
    if _component(record["term"], "course core term") != ws.term:
        raise SchoolLearningError("course core term does not match its workspace")
    tags = _identifier_list(record["capability_tags"], "course capability tags")
    if tags != sorted(tags) or any(tag not in CAPABILITY_TAGS for tag in tags):
        raise SchoolLearningError("course capability tags are invalid or unsorted")
    if not isinstance(record["sources"], list):
        raise SchoolLearningError("course sources must be a list")
    sources = [_validate_source(item) for item in record["sources"]]
    source_ids = [item["id"] for item in sources]
    if len(set(source_ids)) != len(source_ids) or source_ids != sorted(source_ids):
        raise SchoolLearningError("course sources must have unique sorted identifiers")
    if not isinstance(record["metadata"], dict):
        raise SchoolLearningError("course metadata must be an object")
    for key, item in record["metadata"].items():
        _component(key, "course metadata key")
        _nonempty_string(item, f"course metadata {key}")
    if not isinstance(record["assessments"], list):
        raise SchoolLearningError("course assessments must be a list")
    assessments = [_validate_assessment(item) for item in record["assessments"]]
    assessment_ids = [item["id"] for item in assessments]
    if len(set(assessment_ids)) != len(assessment_ids) or assessment_ids != sorted(assessment_ids):
        raise SchoolLearningError("assessments must have unique sorted identifiers")
    if not isinstance(record["policies"], list):
        raise SchoolLearningError("course policies must be a list")
    policies = [_validate_policy(item) for item in record["policies"]]
    policy_ids = [item["id"] for item in policies]
    if len(set(policy_ids)) != len(policy_ids) or policy_ids != sorted(policy_ids):
        raise SchoolLearningError("policies must have unique sorted identifiers")
    _timestamp(record["created_at"], "course core creation timestamp")
    _timestamp(record["updated_at"], "course core update timestamp")
    return record


def _empty_source_observations() -> dict[str, Any]:
    return {"schema_version": SOURCE_OBSERVATIONS_SCHEMA, "observations": []}


def _validate_source_observation(value: object, label: str = "source observation") -> dict[str, Any]:
    record = _exact_object(value, _SOURCE_OBSERVATION_KEYS, label)
    _component(record["id"], f"{label} id")
    _component(record["source_id"], f"{label} source id")
    _observed_at(record["observed_at"], f"{label} observed date")
    if record["scope"] not in SOURCE_OBSERVATION_SCOPES:
        raise SchoolLearningError(f"{label} scope is invalid")
    if record["outcome"] not in SOURCE_OBSERVATION_OUTCOMES:
        raise SchoolLearningError(f"{label} outcome is invalid")
    material_ids = _identifier_list(record["material_ids"], f"{label} material ids")
    if material_ids != sorted(material_ids):
        raise SchoolLearningError(f"{label} material ids must be sorted")
    if not isinstance(record["note"], str):
        raise SchoolLearningError(f"{label} note must be a string")
    return record


def _source_observation_recency_key(value: object) -> tuple[datetime, str]:
    record = _validate_source_observation(value, "source observation recency candidate")
    observed_at = record["observed_at"]
    if _DATE.fullmatch(observed_at):
        _date(observed_at, "source observation recency date")
        instant = datetime(
            int(observed_at[0:4]),
            int(observed_at[5:7]),
            int(observed_at[8:10]),
            tzinfo=timezone.utc,
        )
    else:
        instant = _school_timestamp_datetime(
            observed_at, "source observation recency timestamp"
        ).astimezone(timezone.utc)
    return instant, record["id"]


def _validate_source_observations(value: object) -> dict[str, Any]:
    state = _exact_object(value, _SOURCE_OBSERVATIONS_KEYS, "source observations state")
    if state["schema_version"] != SOURCE_OBSERVATIONS_SCHEMA:
        raise SchoolLearningError("unsupported source observations schema")
    if not isinstance(state["observations"], list):
        raise SchoolLearningError("source observations must be a list")
    records = [
        _validate_source_observation(item, "source observation entry")
        for item in state["observations"]
    ]
    ids = [item["id"] for item in records]
    if len(set(ids)) != len(ids):
        raise SchoolLearningError("source observation identifiers must be unique")
    return state


def _validate_source_observation_references(
    observations: dict[str, Any], materials: dict[str, Any], core: dict[str, Any] | None
) -> None:
    if observations["observations"] and core is None:
        raise SchoolLearningError("source observations require registered v0.2 course core state")
    source_ids = set() if core is None else {item["id"] for item in core["sources"]}
    material_ids = {item["id"] for item in materials["materials"]}
    for observation in observations["observations"]:
        if observation["source_id"] not in source_ids:
            raise SchoolLearningError(
                f"source observation {observation['id']} references unknown source: "
                f"{observation['source_id']}"
            )
        unknown = set(observation["material_ids"]) - material_ids
        if unknown:
            raise SchoolLearningError(
                f"source observation {observation['id']} references unknown materials: "
                + ", ".join(sorted(unknown))
            )


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


def _attachment_filename(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise SchoolLearningError(f"{label} must be a nonempty filename")
    if value != Path(value).name or "/" in value or "\\" in value:
        raise SchoolLearningError(f"{label} must be a safe filename")
    return value


def _validate_study_handoff_manifest(value: object) -> dict[str, Any]:
    manifest = _exact_object(value, _HANDOFF_KEYS, "study handoff manifest")
    if manifest["schema_version"] != STUDY_HANDOFF_SCHEMA:
        raise SchoolLearningError("unsupported study handoff schema")
    _component(manifest["course_id"], "handoff course id")
    _component(manifest["term"], "handoff term")
    _component(manifest["topic_id"], "handoff topic id")
    if manifest["mode"] not in STUDY_MODES:
        raise SchoolLearningError("handoff mode is invalid")
    _nonempty_string(manifest["objective"], "handoff objective")
    if not isinstance(manifest["attachment_filenames"], list):
        raise SchoolLearningError("handoff attachment filenames must be a list")
    filenames = [
        _attachment_filename(item, "handoff attachment filename")
        for item in manifest["attachment_filenames"]
    ]
    if len(set(filenames)) != len(filenames):
        raise SchoolLearningError("handoff attachment filenames must be unique")
    material_ids = _identifier_list(manifest["material_ids"], "handoff material ids")
    if material_ids != sorted(material_ids):
        raise SchoolLearningError("handoff material ids must be sorted")
    if not isinstance(manifest["materials"], list):
        raise SchoolLearningError("handoff materials must be a list")
    material_records: list[dict[str, Any]] = []
    for value_record in manifest["materials"]:
        record = _exact_object(value_record, _HANDOFF_MATERIAL_KEYS, "handoff material record")
        material_id = _component(record["id"], "handoff material id")
        filename = _attachment_filename(
            record["attachment_filename"], "handoff material attachment filename"
        )
        suffix = Path(filename).suffix.lower()
        if suffix not in SUPPORTED_SUFFIXES or filename != f"material-{material_id}{suffix}":
            raise SchoolLearningError("handoff material attachment filename is invalid")
        if not isinstance(record["sha256"], str) or not _DIGEST.fullmatch(record["sha256"]):
            raise SchoolLearningError("handoff material digest is invalid")
        if type(record["bytes"]) is not int or record["bytes"] < 0:
            raise SchoolLearningError("handoff material byte count is invalid")
        material_records.append(record)
    record_ids = [record["id"] for record in material_records]
    if record_ids != material_ids:
        raise SchoolLearningError("handoff material records must match sorted material ids")
    expected_filenames = ["study-brief.md"] + [
        record["attachment_filename"] for record in material_records
    ]
    if filenames != expected_filenames:
        raise SchoolLearningError("handoff attachment filenames do not match its materials")
    return manifest


def _update_contract_value(term: str, course_id: str, base_context_sha256: str) -> dict[str, Any]:
    definitions = {
        "date": {
            "calendar_valid": True,
            "pattern": _DATE.pattern,
            "type": "string",
        },
        "identifier": {
            "forbidden_values": [".", ".."],
            "path_safe": True,
            "pattern": _COMPONENT.pattern,
            "type": "string",
        },
        "identifier_list": {
            "items": {"ref": "identifier"},
            "sorted": True,
            "type": "array",
            "unique": True,
        },
        "nonempty_string": {
            "min_trimmed_length": 1,
            "normalization": "strip",
            "type": "string",
        },
        "nullable_measure": {
            "allowed_types": ["null", "string"],
            "string_min_trimmed_length": 1,
            "string_normalization": "strip",
        },
        "observed_at": {
            "calendar_valid": True,
            "one_of_patterns": [_DATE.pattern, _SCHOOL_TIMESTAMP.pattern],
            "timestamp_fractional_seconds": {
                "max_digits": 6,
                "min_digits_when_present": 1,
                "optional": True,
            },
            "timestamp_seconds": "required",
            "timestamp_subset": "canonical-school-learning",
            "timestamp_timezone": "explicit-Z-or-numeric-offset",
            "type": "string",
        },
        "plain_string": {"type": "string"},
        "planner_value": {
            "calendar_valid": True,
            "one_of_patterns": [_DATE.pattern, _SCHOOL_TIMESTAMP.pattern],
            "timestamp_fractional_seconds": {
                "max_digits": 6,
                "min_digits_when_present": 1,
                "optional": True,
            },
            "timestamp_seconds": "required",
            "timestamp_subset": "canonical-school-learning",
            "timestamp_timezone": "explicit-Z-or-numeric-offset",
            "type": "string",
        },
        "sha256": {
            "algorithm": "sha256",
            "lowercase_hex": True,
            "pattern": _DIGEST.pattern,
            "type": "string",
        },
        "utc_timestamp": {
            "calendar_valid": True,
            "pattern": _TIMESTAMP.pattern,
            "seconds": "required",
            "timezone": "Z",
            "type": "string",
        },
    }
    claim = {
        "exact_keys": sorted(_REVIEWED_CLAIM_KEYS),
        "fields": {
            "field": {
                "forbidden_values": ["due"],
                "planner_critical_values": list(PLANNER_CRITICAL_CLAIM_FIELDS),
                "ref": "identifier",
            },
            "observed_at": {"ref": "observed_at"},
            "source": {"ref": "nonempty_string"},
            "status": {"enum": list(CLAIM_STATUSES), "type": "string"},
            "value": {
                "planner_critical_ref": "planner_value",
                "ref": "nonempty_string",
            },
        },
        "type": "object",
    }
    claim_list = {
        "items": {"ref": "claim"},
        "min_items": 1,
        "semantic_identity_fields": ["field", "value", "source", "observed_at"],
        "semantic_identity_unique": True,
        "type": "array",
    }
    operations = {
        "assessment-upsert": {
            "exact_keys": sorted(_REVIEWED_ASSESSMENT_KEYS),
            "fields": {
                "claims": claim_list,
                "id": {"ref": "identifier"},
                "kind": {"const": "assessment-upsert", "type": "string"},
                "material_ids": {
                    "must_resolve": "current-course-materials",
                    "ref": "identifier_list",
                },
                "points": {"ref": "nullable_measure"},
                "recorded_at": {"ref": "utc_timestamp"},
                "status": {"enum": list(ASSESSMENT_STATUSES), "type": "string"},
                "title": {"ref": "nonempty_string"},
                "topic_ids": {
                    "must_resolve": "current-course-topics",
                    "ref": "identifier_list",
                },
                "type": {
                    "already_normalized": True,
                    "max_length": _ASSESSMENT_TYPE_MAX_LENGTH,
                    "pattern": _ASSESSMENT_TYPE.pattern,
                    "type": "string",
                },
                "weight": {"ref": "nullable_measure"},
                "xp": {"ref": "nullable_measure"},
            },
            "type": "object",
        },
        "policy-upsert": {
            "exact_keys": sorted(_REVIEWED_POLICY_KEYS),
            "fields": {
                "category": {"ref": "identifier"},
                "claims": {**claim_list, "item_field_const": "rule"},
                "id": {"ref": "identifier"},
                "kind": {"const": "policy-upsert", "type": "string"},
                "recorded_at": {"ref": "utc_timestamp"},
                "title": {"ref": "nonempty_string"},
            },
            "type": "object",
        },
        "source-observation": {
            "exact_keys": sorted(_REVIEWED_OBSERVATION_KEYS),
            "fields": {
                "id": {
                    "append_only_identity": True,
                    "novelty": {
                        "existing_state_unique_against": "source_observations[*].id",
                        "ordered_candidate_unique_against": (
                            "prior source-observation operations[*].id"
                        ),
                    },
                    "overwrite_existing": False,
                    "ref": "identifier",
                    "reuse_existing": False,
                },
                "kind": {"const": "source-observation", "type": "string"},
                "material_ids": {
                    "must_resolve": "current-course-materials",
                    "ref": "identifier_list",
                },
                "note": {"ref": "plain_string"},
                "observed_at": {"ref": "observed_at"},
                "outcome": {
                    "enum": list(SOURCE_OBSERVATION_OUTCOMES),
                    "type": "string",
                },
                "scope": {"enum": list(SOURCE_OBSERVATION_SCOPES), "type": "string"},
                "source_id": {
                    "must_resolve": "current-or-prior-operation-course-sources",
                    "ref": "identifier",
                },
            },
            "type": "object",
        },
        "source-upsert": {
            "exact_keys": sorted(_REVIEWED_SOURCE_KEYS),
            "fields": {
                "id": {"ref": "identifier"},
                "kind": {"const": "source-upsert", "type": "string"},
                "recorded_at": {"ref": "utc_timestamp"},
                "reference": {"ref": "nonempty_string"},
                "status": {"enum": list(CLAIM_STATUSES), "type": "string"},
                "title": {"ref": "nonempty_string"},
            },
            "type": "object",
        },
    }
    return {
        "schema_version": UPDATE_CONTRACT_SCHEMA,
        "reviewed_update_schema_version": REVIEWED_UPDATE_SCHEMA,
        "term": term,
        "course_id": course_id,
        "base_context_sha256": base_context_sha256,
        "allowed_operation_kinds": list(REVIEWED_OPERATION_KINDS),
        "candidate_keys": sorted(_REVIEWED_UPDATE_KEYS),
        "operation_keys": {
            "assessment-upsert": sorted(_REVIEWED_ASSESSMENT_KEYS),
            "policy-upsert": sorted(_REVIEWED_POLICY_KEYS),
            "source-upsert": sorted(_REVIEWED_SOURCE_KEYS),
            "source-observation": sorted(_REVIEWED_OBSERVATION_KEYS),
        },
        "claim_keys": sorted(_REVIEWED_CLAIM_KEYS),
        "bounded_values": {
            "assessment_status": list(ASSESSMENT_STATUSES),
            "claim_status": list(CLAIM_STATUSES),
            "planner_critical_claim_field": list(PLANNER_CRITICAL_CLAIM_FIELDS),
            "source_observation_outcome": list(SOURCE_OBSERVATION_OUTCOMES),
            "source_observation_scope": list(SOURCE_OBSERVATION_SCOPES),
        },
        "max_operations": _REVIEWED_UPDATE_MAX_OPERATIONS,
        "constraints": {
            "base_identity": {
                "algorithm": "sha256",
                "attachment": "course-context.md",
                "complete_semantic_sections": [
                    "course",
                    "course_core",
                    "materials",
                    "source_observations",
                    "topics",
                ],
                "digest_field": "base_context_sha256",
                "exact_attachment_bytes": True,
            },
            "candidate_file": {
                "encoding": "UTF-8",
                "max_bytes": _REVIEWED_UPDATE_MAX_BYTES,
                "top_level_type": "object",
            },
            "claim": claim,
            "definitions": definitions,
            "operations": operations,
            "root": {
                "exact_keys": sorted(_REVIEWED_UPDATE_KEYS),
                "fields": {
                    "base_context_sha256": {
                        "const": base_context_sha256,
                        "ref": "sha256",
                    },
                    "course_id": {"const": course_id, "ref": "identifier"},
                    "operations": {
                        "discriminator": "kind",
                        "kinds": list(REVIEWED_OPERATION_KINDS),
                        "max_items": _REVIEWED_UPDATE_MAX_OPERATIONS,
                        "min_items": 1,
                        "ordered": True,
                        "type": "array",
                    },
                    "schema_version": {
                        "const": REVIEWED_UPDATE_SCHEMA,
                        "type": "string",
                    },
                    "term": {"const": term, "ref": "identifier"},
                },
                "registered_course_required": True,
                "type": "object",
            },
        },
        "rules": list(_UPDATE_CONTRACT_RULES),
    }


def _validate_update_contract(value: object) -> dict[str, Any]:
    record = _exact_object(value, _UPDATE_CONTRACT_KEYS, "course update contract")
    if record["schema_version"] != UPDATE_CONTRACT_SCHEMA:
        raise SchoolLearningError("unsupported course update contract schema")
    if record["reviewed_update_schema_version"] != REVIEWED_UPDATE_SCHEMA:
        raise SchoolLearningError("course update contract reviewed-update schema is invalid")
    term = _component(record["term"], "course update contract term")
    course_id = _component(record["course_id"], "course update contract course id")
    digest = record["base_context_sha256"]
    if not isinstance(digest, str) or not _DIGEST.fullmatch(digest):
        raise SchoolLearningError("course update contract base context digest is invalid")
    expected = _update_contract_value(term, course_id, digest)
    if record != expected:
        raise SchoolLearningError("course update contract rules or operation bounds are invalid")
    return record


def _validate_course_handoff_manifest(value: object) -> dict[str, Any]:
    manifest = _exact_object(value, _COURSE_HANDOFF_KEYS, "course handoff manifest")
    if manifest["schema_version"] != COURSE_HANDOFF_SCHEMA:
        raise SchoolLearningError("unsupported course handoff schema")
    _component(manifest["course_id"], "course handoff course id")
    _component(manifest["term"], "course handoff term")
    filenames = [
        _attachment_filename(item, "course handoff attachment filename")
        for item in manifest["attachment_filenames"]
    ] if isinstance(manifest["attachment_filenames"], list) else []
    if not isinstance(manifest["attachment_filenames"], list):
        raise SchoolLearningError("course handoff attachment filenames must be a list")
    if len(set(filenames)) != len(filenames):
        raise SchoolLearningError("course handoff attachment filenames must be unique")
    context = _exact_object(
        manifest["context_attachment"],
        _COURSE_HANDOFF_CONTEXT_KEYS,
        "course handoff context attachment",
    )
    if context["role"] != "course-context":
        raise SchoolLearningError("course handoff context attachment role is invalid")
    if _attachment_filename(
        context["attachment_filename"], "course handoff context attachment filename"
    ) != "course-context.md":
        raise SchoolLearningError("course handoff context attachment filename is invalid")
    if not isinstance(context["sha256"], str) or not _DIGEST.fullmatch(context["sha256"]):
        raise SchoolLearningError("course handoff context attachment digest is invalid")
    if type(context["bytes"]) is not int or context["bytes"] < 0:
        raise SchoolLearningError("course handoff context attachment byte count is invalid")
    contract = _exact_object(
        manifest["update_contract_attachment"],
        _COURSE_HANDOFF_CONTEXT_KEYS,
        "course handoff update contract attachment",
    )
    if contract["role"] != "update-contract":
        raise SchoolLearningError("course handoff update contract attachment role is invalid")
    if _attachment_filename(
        contract["attachment_filename"], "course handoff update contract attachment filename"
    ) != "update-contract.json":
        raise SchoolLearningError("course handoff update contract attachment filename is invalid")
    if not isinstance(contract["sha256"], str) or not _DIGEST.fullmatch(contract["sha256"]):
        raise SchoolLearningError("course handoff update contract attachment digest is invalid")
    if type(contract["bytes"]) is not int or contract["bytes"] < 0:
        raise SchoolLearningError("course handoff update contract attachment byte count is invalid")
    material_ids = _identifier_list(manifest["material_ids"], "course handoff material ids")
    if material_ids != sorted(material_ids):
        raise SchoolLearningError("course handoff material ids must be sorted")
    if not isinstance(manifest["materials"], list):
        raise SchoolLearningError("course handoff materials must be a list")
    records: list[dict[str, Any]] = []
    for item in manifest["materials"]:
        record = _exact_object(item, _HANDOFF_MATERIAL_KEYS, "course handoff material record")
        material_id = _component(record["id"], "course handoff material id")
        filename = _attachment_filename(
            record["attachment_filename"], "course handoff material filename"
        )
        suffix = Path(filename).suffix.lower()
        if suffix not in SUPPORTED_SUFFIXES or filename != f"material-{material_id}{suffix}":
            raise SchoolLearningError("course handoff material filename is invalid")
        if not isinstance(record["sha256"], str) or not _DIGEST.fullmatch(record["sha256"]):
            raise SchoolLearningError("course handoff material digest is invalid")
        if type(record["bytes"]) is not int or record["bytes"] < 0:
            raise SchoolLearningError("course handoff material byte count is invalid")
        records.append(record)
    if [item["id"] for item in records] != material_ids:
        raise SchoolLearningError("course handoff materials do not match sorted material ids")
    expected_filenames = [context["attachment_filename"], contract["attachment_filename"]] + [
        item["attachment_filename"] for item in records
    ]
    if filenames != expected_filenames:
        raise SchoolLearningError("course handoff attachment filenames do not match materials")
    return manifest


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


def _validate_v02_references(
    materials: dict[str, Any], topics: dict[str, Any], core: dict[str, Any] | None
) -> None:
    if materials["schema_version"] == MATERIALS_V02_SCHEMA and core is None:
        raise SchoolLearningError("v0.2 materials require registered course core state")
    if core is None:
        return
    material_ids = {item["id"] for item in materials["materials"]}
    topic_ids = {item["id"] for item in topics["topics"]}
    assessment_ids = {item["id"] for item in core["assessments"]}
    for material in materials["materials"]:
        if materials["schema_version"] != MATERIALS_V02_SCHEMA:
            continue
        unknown_topics = set(material["topic_ids"]) - topic_ids
        unknown_assessments = set(material["assessment_ids"]) - assessment_ids
        if unknown_topics:
            raise SchoolLearningError(
                f"material {material['id']} references unknown topics: "
                + ", ".join(sorted(unknown_topics))
            )
        if unknown_assessments:
            raise SchoolLearningError(
                f"material {material['id']} references unknown assessments: "
                + ", ".join(sorted(unknown_assessments))
            )
    for assessment in core["assessments"]:
        unknown_materials = set(assessment["material_ids"]) - material_ids
        unknown_topics = set(assessment["topic_ids"]) - topic_ids
        if unknown_materials:
            raise SchoolLearningError(
                f"assessment {assessment['id']} references unknown materials: "
                + ", ".join(sorted(unknown_materials))
            )
        if unknown_topics:
            raise SchoolLearningError(
                f"assessment {assessment['id']} references unknown topics: "
                + ", ".join(sorted(unknown_topics))
            )


def _load_state(ws: Workspace, *, skip_material_id: str | None = None) -> _State:
    _validate_layout(ws)
    course = _validate_course(_read_json(ws, ws.course_dir / "course.json", "course state file"), ws)
    materials = _validate_materials(
        _read_json(ws, ws.course_dir / "materials.json", "materials state file")
    )
    topics = _validate_topics(_read_json(ws, ws.course_dir / "topics.json", "topics state file"))
    sessions = _read_sessions(ws)
    core_path = ws.course_dir / "course-core.json"
    core = None
    if core_path.exists() or core_path.is_symlink():
        core = _validate_course_core(_read_json(ws, core_path, "course core state file"), ws)
    observations_path = ws.course_dir / "source-observations.json"
    source_observations = _empty_source_observations()
    if observations_path.exists() or observations_path.is_symlink():
        source_observations = _validate_source_observations(
            _read_json(ws, observations_path, "source observations state file")
        )
    _validate_references(materials, topics, sessions)
    _validate_v02_references(materials, topics, core)
    _validate_source_observation_references(source_observations, materials, core)
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
    return _State(course, materials, topics, sessions, core, source_observations)


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
        course_dir_preexisting = ws.course_dir.exists() or ws.course_dir.is_symlink()
        if course_dir_preexisting:
            if ws.course_dir.is_symlink() or not ws.course_dir.is_dir():
                raise SchoolLearningError("course workspace must be a real directory")
            if any(ws.course_dir.iterdir()):
                raise SchoolLearningError("course workspace already exists and is not empty")
    except SchoolLearningError:
        raise
    except OSError as error:
        raise SchoolLearningError("course workspace cannot be inspected") from error

    created_directories: list[Path] = []
    created_files: list[Path] = []
    try:
        _resolved_data_root(root)
        _safe_create_directory_chain_tracking(root, "data root", created_directories)
        _resolved_data_root(root)
        term_dir = root / ws.term
        if not term_dir.exists():
            _safe_create_directory(term_dir, "term directory", created_directories)
        elif term_dir.is_symlink() or not term_dir.is_dir():
            raise SchoolLearningError("term directory must be a real directory")
        _resolved_data_root(root)
        if not course_dir_preexisting:
            if not _safe_create_directory(
                ws.course_dir, "course workspace", created_directories
            ):
                course_dir_preexisting = True
                if any(ws.course_dir.iterdir()):
                    raise SchoolLearningError("course workspace appeared nonempty during initialization")
        for name in _REQUIRED_DIRECTORIES:
            _confined_path(
                ws,
                ws.course_dir,
                label="course workspace",
                must_exist=True,
                require_directory=True,
            )
            directory = ws.course_dir / name
            _safe_create_directory(directory, f"{name} directory", created_directories)
        _validate_layout(ws)
        initial_files = (
            (
                ws.course_dir / "course.json",
                {
                    "schema_version": COURSE_SCHEMA,
                    "course_id": ws.course_id,
                    "term": ws.term,
                    "title": safe_title,
                    "created_at": timestamp,
                },
            ),
            (
                ws.course_dir / "materials.json",
                {"schema_version": MATERIALS_SCHEMA, "materials": []},
            ),
            (
                ws.course_dir / "topics.json",
                {"schema_version": TOPICS_SCHEMA, "topics": []},
            ),
        )
        for path, value in initial_files:
            created_files.append(path)
            _atomic_write_json(ws, path, value)
        _load_state(ws)
        return ws
    except Exception as error:
        rollback_errors: list[str] = []
        if ws.course_dir.exists() and not ws.course_dir.is_symlink():
            for path in reversed(created_files):
                try:
                    if path.exists() or path.is_symlink():
                        _safe_unlink(ws, path, "failed course initialization", missing_ok=True)
                except SchoolLearningError as rollback_error:
                    rollback_errors.append(str(rollback_error))
        rollback_errors.extend(
            _rollback_created_directories(created_directories, "failed course initialization")
        )
        if rollback_errors:
            raise SchoolLearningError(
                "course initialization failed and rollback was incomplete: "
                + "; ".join(rollback_errors)
            ) from error
        raise _as_school_error("course initialization failed", error) from error


def load_course(ws: Workspace) -> dict[str, Any]:
    return _load_state(ws).course


def load_materials(ws: Workspace) -> dict[str, Any]:
    return _load_state(ws).materials


def load_topics(ws: Workspace) -> dict[str, Any]:
    return _load_state(ws).topics


def load_source_observations(ws: Workspace) -> dict[str, Any]:
    observations = _load_state(ws).source_observations
    if observations is None:  # pragma: no cover - _load_state always supplies the optional default
        return _empty_source_observations()
    return observations


def initialize_semester(
    data_root: Path | str,
    term: str,
    title: str,
    *,
    created_at: str | None = None,
) -> SemesterWorkspace:
    safe_title = _nonempty_string(title, "semester title").strip()
    timestamp = _timestamp(
        created_at if created_at is not None else utc_now(), "semester creation timestamp"
    )
    sw = semester_workspace(data_root, term)
    metadata = _semester_metadata_dir(sw)
    state_path = _semester_state_path(sw)
    generated = _semester_generated_dir(sw)
    try:
        for path, label in ((sw.data_root, "data root"), (sw.term_dir, "term directory")):
            if path.exists() or path.is_symlink():
                if path.is_symlink() or not path.is_dir():
                    raise SchoolLearningError(f"{label} must be a real directory")
        metadata_present = metadata.exists() or metadata.is_symlink()
        if metadata_present and (metadata.is_symlink() or not metadata.is_dir()):
            raise SchoolLearningError("semester metadata namespace must be a real directory")
    except SchoolLearningError:
        raise
    except OSError as error:
        raise SchoolLearningError("semester metadata namespace cannot be safely inspected") from error
    if metadata_present:
        existing = load_semester(sw)
        if existing["title"] != safe_title:
            raise SchoolLearningError("semester already exists with a different title")
        return sw
    state = {
        "schema_version": SEMESTER_SCHEMA,
        "term": sw.term,
        "title": safe_title,
        "course_ids": [],
        "created_at": timestamp,
    }
    _validate_semester(state, sw)
    created_directories: list[Path] = []
    state_attempted = False
    try:
        _safe_create_directory_chain_tracking(sw.data_root, "data root", created_directories)
        if not sw.term_dir.exists():
            _safe_create_directory(sw.term_dir, "term directory", created_directories)
        if not _safe_create_directory(
            metadata, "semester metadata namespace", created_directories
        ):
            raise SchoolLearningError("semester metadata namespace appeared during initialization")
        if not _safe_create_directory(
            generated, "semester generated directory", created_directories
        ):
            raise SchoolLearningError("semester generated directory appeared during initialization")
        state_attempted = True
        _atomic_term_json(sw, state_path, state)
        load_semester(sw)
        return sw
    except Exception as error:
        rollback_errors: list[str] = []
        if state_attempted and (state_path.exists() or state_path.is_symlink()):
            try:
                safe_state = _term_confined_path(
                    sw,
                    state_path,
                    label="failed semester state",
                    regular_if_present=True,
                )
                safe_state.unlink(missing_ok=True)
            except (OSError, SchoolLearningError) as rollback_error:
                rollback_errors.append(str(rollback_error))
        rollback_errors.extend(
            _rollback_created_directories(created_directories, "failed semester initialization")
        )
        if rollback_errors:
            raise SchoolLearningError(
                "semester initialization failed and rollback was incomplete: "
                + "; ".join(rollback_errors)
            ) from error
        raise _as_school_error("semester initialization failed", error) from error


def load_semester(sw: SemesterWorkspace) -> dict[str, Any]:
    _term_confined_path(
        sw, sw.term_dir, label="semester workspace", must_exist=True, require_directory=True
    )
    _term_confined_path(
        sw,
        _semester_metadata_dir(sw),
        label="semester metadata namespace",
        must_exist=True,
        require_directory=True,
    )
    _term_confined_path(
        sw,
        _semester_generated_dir(sw),
        label="semester generated directory",
        must_exist=True,
        require_directory=True,
    )
    record = _validate_semester(
        _read_term_json(sw, _semester_state_path(sw), "semester state file"), sw
    )
    for course_id in record["course_ids"]:
        state = _load_state(workspace(sw.data_root, sw.term, course_id))
        if state.core is None:
            raise SchoolLearningError(f"semester course {course_id} lacks v0.2 course core state")
    return record


def load_course_core(ws: Workspace) -> dict[str, Any]:
    state = _load_state(ws)
    if state.core is None:
        raise SchoolLearningError("course is readable as v0.1 but is not registered for v0.2")
    return state.core


def _migrated_materials(manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest["schema_version"] == MATERIALS_V02_SCHEMA:
        return manifest
    migrated = {
        "schema_version": MATERIALS_V02_SCHEMA,
        "materials": [
            {
                **item,
                "kind": "unspecified",
                "status": "reference",
                "relevant_date": None,
                "topic_ids": [],
                "assessment_ids": [],
                "provenance": None,
            }
            for item in manifest["materials"]
        ],
    }
    return _validate_materials(migrated)


def register_course(
    sw: SemesterWorkspace,
    course_id: str,
    title: str,
    *,
    capability_tags: Iterable[str] = (),
    sources: Iterable[dict[str, Any]] = (),
    metadata: dict[str, str] | None = None,
    recorded_at: str | None = None,
) -> Workspace:
    semester = load_semester(sw)
    semester_path = _semester_state_path(sw)
    old_semester = _read_term_bytes(sw, semester_path, "semester state file")
    safe_id = _component(course_id, "course id")
    safe_title = _nonempty_string(title, "course title").strip()
    timestamp = _timestamp(
        recorded_at if recorded_at is not None else utc_now(), "course registration timestamp"
    )
    tags = sorted(set(_component(item, "course capability tag") for item in capability_tags))
    if any(item not in CAPABILITY_TAGS for item in tags):
        raise SchoolLearningError("course capability tag is unsupported")
    try:
        source_records = sorted((dict(item) for item in sources), key=lambda item: item.get("id", ""))
    except (TypeError, ValueError) as error:
        raise SchoolLearningError("course sources must be descriptor objects") from error
    for item in source_records:
        _validate_source(item)
    source_ids = [item["id"] for item in source_records]
    if len(set(source_ids)) != len(source_ids):
        raise SchoolLearningError("course source identifiers must be unique")
    try:
        metadata_record = {} if metadata is None else dict(metadata)
    except (TypeError, ValueError) as error:
        raise SchoolLearningError("course metadata must be a string mapping") from error
    for key, item in metadata_record.items():
        _component(key, "course metadata key")
        _nonempty_string(item, f"course metadata {key}")

    ws = workspace(sw.data_root, sw.term, safe_id)
    try:
        course_existed = ws.course_dir.exists() or ws.course_dir.is_symlink()
        if course_existed and (ws.course_dir.is_symlink() or not ws.course_dir.is_dir()):
            raise SchoolLearningError("course workspace must be a real directory")
        course_was_empty = course_existed and not any(ws.course_dir.iterdir())
    except SchoolLearningError:
        raise
    except OSError as error:
        raise SchoolLearningError("course workspace cannot be inspected") from error

    state: _State | None = None
    if course_existed and not course_was_empty:
        state = _load_state(ws)
        if state.course["title"] != safe_title:
            raise SchoolLearningError("registered course title disagrees with existing course identity")

    core_path = ws.course_dir / "course-core.json"
    materials_path = ws.course_dir / "materials.json"
    old_core: bytes | None = None
    old_materials: bytes | None = None
    core_attempted = False
    materials_attempted = False
    semester_attempted = False
    initialization_attempted = False
    try:
        if state is None:
            initialization_attempted = True
            ws = initialize_course(sw.data_root, sw.term, safe_id, safe_title, created_at=timestamp)
            state = _load_state(ws)

        existing_core = state.core
        core = {
            "schema_version": COURSE_CORE_SCHEMA,
            "course_id": safe_id,
            "term": sw.term,
            "capability_tags": tags,
            "sources": source_records,
            "metadata": metadata_record,
            "assessments": [] if existing_core is None else existing_core["assessments"],
            "policies": [] if existing_core is None else existing_core["policies"],
            "created_at": timestamp if existing_core is None else existing_core["created_at"],
            "updated_at": timestamp,
        }
        _validate_course_core(core, ws)
        migrated = _migrated_materials(state.materials)
        _validate_v02_references(migrated, state.topics, core)
        old_core = (
            _read_regular_bytes(ws, core_path, "course core state file")
            if existing_core is not None
            else None
        )
        old_materials = _read_regular_bytes(ws, materials_path, "materials state file")
        core_attempted = True
        _atomic_write_json(ws, core_path, core)
        if state.materials["schema_version"] != MATERIALS_V02_SCHEMA:
            materials_attempted = True
            _atomic_write_json(ws, materials_path, migrated)
        _load_state(ws)
        if safe_id not in semester["course_ids"]:
            semester["course_ids"].append(safe_id)
            semester["course_ids"].sort()
            _validate_semester(semester, sw)
            semester_attempted = True
            _atomic_term_json(sw, semester_path, semester)
        load_semester(sw)
        return ws
    except Exception as error:
        rollback_errors: list[str] = []
        if semester_attempted:
            try:
                _atomic_term_bytes(sw, semester_path, old_semester)
            except SchoolLearningError as rollback_error:
                rollback_errors.append(str(rollback_error))
        if materials_attempted and old_materials is not None:
            try:
                _atomic_write_bytes(ws, materials_path, old_materials)
            except SchoolLearningError as rollback_error:
                rollback_errors.append(str(rollback_error))
        if core_attempted:
            try:
                if old_core is None:
                    _safe_unlink(ws, core_path, "failed course registration", missing_ok=True)
                else:
                    _atomic_write_bytes(ws, core_path, old_core)
            except SchoolLearningError as rollback_error:
                rollback_errors.append(str(rollback_error))
        if not course_existed and (ws.course_dir.exists() or ws.course_dir.is_symlink()):
            try:
                _safe_remove_tree(ws, ws.course_dir, "failed new course registration")
            except SchoolLearningError as rollback_error:
                rollback_errors.append(str(rollback_error))
        elif course_was_empty and initialization_attempted:
            try:
                _restore_empty_course_workspace(ws, "failed empty-workspace course registration")
            except SchoolLearningError as rollback_error:
                rollback_errors.append(str(rollback_error))
        if rollback_errors:
            raise SchoolLearningError(
                "course registration failed and rollback was incomplete: "
                + "; ".join(rollback_errors)
            ) from error
        raise _as_school_error("course registration failed", error) from error


def intake_material(
    ws: Workspace,
    source: Path | str,
    material_id: str,
    title: str,
    *,
    kind: object = _UNSET,
    status: object = _UNSET,
    relevant_date: object = _UNSET,
    topic_ids: object = _UNSET,
    assessment_ids: object = _UNSET,
    source_descriptor: object = _UNSET,
    provenance_status: str = "provisional",
    observed_at: str | None = None,
    added_at: str | None = None,
    replace: bool = False,
) -> dict[str, Any]:
    state = _load_state(ws)
    if state.core is None or state.materials["schema_version"] != MATERIALS_V02_SCHEMA:
        raise SchoolLearningError("intake requires deliberate v0.2 semester/course registration")
    timestamp = added_at if added_at is not None else utc_now()
    existing = next(
        (item for item in state.materials["materials"] if item["id"] == material_id), None
    )
    provenance: object = _UNSET
    if (source_descriptor is _UNSET or source_descriptor is None) and observed_at is not None:
        raise SchoolLearningError("material provenance observed date requires a source descriptor")
    if source_descriptor is None:
        provenance = None
    elif source_descriptor is not _UNSET:
        provenance = {
            "source": _nonempty_string(source_descriptor, "material source descriptor").strip(),
            "observed_at": observed_at if observed_at is not None else timestamp,
            "status": provenance_status,
        }
        _validate_provenance(provenance, "material provenance")
    resolved_kind = "unspecified" if kind is _UNSET and existing is None else kind
    resolved_status = "current" if status is _UNSET and existing is None else status
    return add_material(
        ws,
        source,
        material_id,
        title,
        added_at=timestamp,
        replace=replace,
        kind=resolved_kind,
        status=resolved_status,
        relevant_date=relevant_date,
        topic_ids=topic_ids,
        assessment_ids=assessment_ids,
        provenance=provenance,
    )


def _new_claim(
    field: str,
    value: str,
    source: str,
    observed_at: str,
    status: str,
) -> dict[str, Any]:
    safe_field = _component(field, "claim field")
    safe_value = _nonempty_string(value, "claim value").strip()
    safe_source = _nonempty_string(source, "claim source").strip()
    safe_observed = _observed_at(observed_at, "claim observed date")
    if status not in CLAIM_STATUSES:
        raise SchoolLearningError("claim status is invalid")
    identity = json.dumps(
        [safe_field, safe_value, safe_source, safe_observed],
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    claim = {
        "id": "claim-" + hashlib.sha256(identity).hexdigest()[:20],
        "field": safe_field,
        "value": safe_value,
        "source": safe_source,
        "observed_at": safe_observed,
        "status": status,
    }
    return _validate_claim(claim, "claim")


def _append_claim_preserving_conflict(
    claims: list[dict[str, Any]], claim: dict[str, Any]
) -> list[dict[str, Any]]:
    existing = next((item for item in claims if item["id"] == claim["id"]), None)
    if existing is not None:
        if {key: existing[key] for key in _CLAIM_KEYS - {"status"}} != {
            key: claim[key] for key in _CLAIM_KEYS - {"status"}
        }:
            raise SchoolLearningError("claim identifier collision")
        existing["status"] = claim["status"]
    else:
        claims.append(claim)
    _normalize_claim_sets(claims)
    _validate_claims(claims, "claims")
    return claims


def _write_course_core(ws: Workspace, core: dict[str, Any]) -> dict[str, Any]:
    state = _load_state(ws)
    if state.core is None:
        raise SchoolLearningError("v0.2 course core state is required")
    _validate_course_core(core, ws)
    _validate_v02_references(state.materials, state.topics, core)
    path = ws.course_dir / "course-core.json"
    previous = _read_regular_bytes(ws, path, "course core state file")
    attempted = False
    try:
        attempted = True
        _atomic_write_json(ws, path, core)
        validated = _load_state(ws).core
        if validated is None:  # pragma: no cover - guarded by strict load
            raise SchoolLearningError("course core write did not persist")
        return validated
    except Exception as error:
        if attempted:
            try:
                _atomic_write_bytes(ws, path, previous)
            except SchoolLearningError as rollback_error:
                raise SchoolLearningError(
                    f"course core update failed and rollback was incomplete: {rollback_error}"
                ) from error
        raise _as_school_error("course core update failed", error) from error


def _upsert_source_record(
    core: dict[str, Any],
    source_id: str,
    title: str,
    reference: str,
    status: str,
    recorded_at: str,
) -> dict[str, Any]:
    record = {
        "id": _component(source_id, "course source id"),
        "title": _nonempty_string(title, "course source title").strip(),
        "reference": _nonempty_string(reference, "course source reference").strip(),
        "status": status,
    }
    _validate_source(record)
    existing = next((item for item in core["sources"] if item["id"] == record["id"]), None)
    if existing is None:
        core["sources"].append(record)
    else:
        core["sources"][core["sources"].index(existing)] = record
    core["sources"].sort(key=lambda item: item["id"])
    core["updated_at"] = _timestamp(recorded_at, "course source update timestamp")
    return record


def upsert_source(
    ws: Workspace,
    source_id: str,
    title: str,
    reference: str,
    *,
    status: str = "provisional",
    recorded_at: str | None = None,
) -> dict[str, Any]:
    core = json.loads(json.dumps(load_course_core(ws)))
    record = _upsert_source_record(
        core,
        source_id,
        title,
        reference,
        status,
        recorded_at if recorded_at is not None else utc_now(),
    )
    written = _write_course_core(ws, core)
    return next(item for item in written["sources"] if item["id"] == record["id"])


def _source_observation_record(
    source_id: str,
    scope: str,
    outcome: str,
    *,
    material_ids: Iterable[str] = (),
    note: str = "",
    observed_at: str,
    observation_id: str | None = None,
) -> dict[str, Any]:
    safe_source = _component(source_id, "source observation source id")
    safe_materials = _normalize_material_ids(material_ids)
    if not isinstance(note, str):
        raise SchoolLearningError("source observation note must be a string")
    safe_observed = _observed_at(observed_at, "source observation observed date")
    if observation_id is None:
        identity = json.dumps(
            [safe_source, safe_observed, scope, outcome, safe_materials, note],
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        safe_id = "observation-" + hashlib.sha256(identity).hexdigest()[:20]
    else:
        safe_id = _component(observation_id, "source observation id")
    record = {
        "id": safe_id,
        "source_id": safe_source,
        "observed_at": safe_observed,
        "scope": scope,
        "outcome": outcome,
        "material_ids": safe_materials,
        "note": note,
    }
    return _validate_source_observation(record)


def _append_source_observation_record(
    observations: dict[str, Any],
    record: dict[str, Any],
    materials: dict[str, Any],
    core: dict[str, Any],
) -> None:
    _validate_source_observations(observations)
    _validate_source_observation(record)
    if any(item["id"] == record["id"] for item in observations["observations"]):
        raise SchoolLearningError("source observation identifier already exists")
    observations["observations"].append(record)
    _validate_source_observations(observations)
    _validate_source_observation_references(observations, materials, core)


def append_source_observation(
    ws: Workspace,
    source_id: str,
    scope: str,
    outcome: str,
    *,
    material_ids: Iterable[str] = (),
    note: str = "",
    observed_at: str | None = None,
    observation_id: str | None = None,
) -> dict[str, Any]:
    state = _load_state(ws)
    if state.core is None or state.source_observations is None:
        raise SchoolLearningError("source observation requires v0.2 course registration")
    record = _source_observation_record(
        source_id,
        scope,
        outcome,
        material_ids=material_ids,
        note=note,
        observed_at=observed_at if observed_at is not None else utc_now(),
        observation_id=observation_id,
    )
    proposed = json.loads(json.dumps(state.source_observations))
    _append_source_observation_record(proposed, record, state.materials, state.core)
    path = ws.course_dir / "source-observations.json"
    existed = path.exists()
    previous = _read_regular_bytes(ws, path, "source observations state file") if existed else None
    attempted = False
    try:
        attempted = True
        _atomic_write_json(ws, path, proposed)
        validated = load_source_observations(ws)
        return next(item for item in validated["observations"] if item["id"] == record["id"])
    except Exception as error:
        if attempted:
            try:
                if previous is None:
                    _safe_unlink(ws, path, "failed source observation append", missing_ok=True)
                else:
                    _atomic_write_bytes(ws, path, previous)
            except SchoolLearningError as rollback_error:
                raise SchoolLearningError(
                    "source observation append failed and rollback was incomplete: "
                    f"{rollback_error}"
                ) from error
        raise _as_school_error("source observation append failed", error) from error


def upsert_assessment(
    ws: Workspace,
    assessment_id: str,
    title: str,
    assessment_type: object = _UNSET,
    status: object = _UNSET,
    *,
    weight: object = _UNSET,
    points: object = _UNSET,
    xp: object = _UNSET,
    material_ids: object = _UNSET,
    topic_ids: object = _UNSET,
    claim_field: str | None = None,
    claim_value: str | None = None,
    claim_source: str | None = None,
    claim_observed_at: str | None = None,
    claim_status: str = "provisional",
    recorded_at: str | None = None,
) -> dict[str, Any]:
    core = json.loads(json.dumps(load_course_core(ws)))
    safe_id = _component(assessment_id, "assessment id")
    existing = next((item for item in core["assessments"] if item["id"] == safe_id), None)
    claims = [] if existing is None else existing["claims"]
    claim_values = (claim_field, claim_value, claim_source, claim_observed_at)
    if any(item is not None for item in claim_values):
        if claim_field is None or claim_value is None or claim_source is None:
            raise SchoolLearningError("assessment claim requires field, value, and source")
        observed = claim_observed_at if claim_observed_at is not None else utc_now()
        _append_claim_preserving_conflict(
            claims, _new_claim(claim_field, claim_value, claim_source, observed, claim_status)
        )
    if existing is None and (assessment_type is _UNSET or status is _UNSET):
        raise SchoolLearningError("new assessment requires type and status")

    def resolved_optional(field: str, supplied: object) -> object:
        if supplied is not _UNSET:
            return supplied
        return None if existing is None else existing[field]

    def resolved_ids(field: str, supplied: object) -> list[str]:
        if supplied is _UNSET:
            return [] if existing is None else list(existing[field])
        return _normalize_material_ids(supplied)  # type: ignore[arg-type]

    resolved_type = (
        existing["type"]
        if assessment_type is _UNSET and existing is not None
        else _normalize_assessment_type(assessment_type)
    )
    resolved_status = existing["status"] if status is _UNSET and existing is not None else status
    record = {
        "id": safe_id,
        "title": _nonempty_string(title, "assessment title").strip(),
        "type": resolved_type,
        "status": resolved_status,
        "weight": resolved_optional("weight", weight),
        "points": resolved_optional("points", points),
        "xp": resolved_optional("xp", xp),
        "material_ids": resolved_ids("material_ids", material_ids),
        "topic_ids": resolved_ids("topic_ids", topic_ids),
        "claims": claims,
    }
    _validate_assessment(record)
    if existing is None:
        core["assessments"].append(record)
    else:
        core["assessments"][core["assessments"].index(existing)] = record
    core["assessments"].sort(key=lambda item: item["id"])
    core["updated_at"] = _timestamp(
        recorded_at if recorded_at is not None else utc_now(), "assessment update timestamp"
    )
    written = _write_course_core(ws, core)
    return next(item for item in written["assessments"] if item["id"] == safe_id)


def upsert_policy(
    ws: Workspace,
    policy_id: str,
    title: str,
    category: str,
    rule: str,
    source: str,
    *,
    status: str = "provisional",
    observed_at: str | None = None,
    recorded_at: str | None = None,
) -> dict[str, Any]:
    core = json.loads(json.dumps(load_course_core(ws)))
    safe_id = _component(policy_id, "policy id")
    existing = next((item for item in core["policies"] if item["id"] == safe_id), None)
    claims = [] if existing is None else existing["claims"]
    observed = observed_at if observed_at is not None else utc_now()
    claim = _new_claim("rule", rule, source, observed, status)
    _append_claim_preserving_conflict(claims, claim)
    record_status = _aggregate_claim_status(claims)
    record = {
        "id": safe_id,
        "title": _nonempty_string(title, "policy title").strip(),
        "category": _component(category, "policy category"),
        "status": record_status,
        "claims": claims,
    }
    _validate_policy(record)
    if existing is None:
        core["policies"].append(record)
    else:
        core["policies"][core["policies"].index(existing)] = record
    core["policies"].sort(key=lambda item: item["id"])
    core["updated_at"] = _timestamp(
        recorded_at if recorded_at is not None else utc_now(), "policy update timestamp"
    )
    written = _write_course_core(ws, core)
    return next(item for item in written["policies"] if item["id"] == safe_id)


def _canonical_planner_claim_value(value: object, label: str) -> str:
    text = _nonempty_string(value, label).strip()
    if _DATE.fullmatch(text):
        return _date(text, label) or ""  # pragma: no cover - non-optional contract
    _school_timestamp_datetime(text, label)
    return text


def _validate_reviewed_claim(value: object, label: str) -> dict[str, Any]:
    record = _exact_object(value, _REVIEWED_CLAIM_KEYS, label)
    field = _component(record["field"], f"{label} field")
    if field == "due":
        raise SchoolLearningError(f"{label} field due is legacy; use due-at")
    claim_value = _nonempty_string(record["value"], f"{label} value").strip()
    if field in PLANNER_CRITICAL_CLAIM_FIELDS:
        claim_value = _canonical_planner_claim_value(claim_value, f"{label} value")
    source = _nonempty_string(record["source"], f"{label} source").strip()
    observed_at = _observed_at(record["observed_at"], f"{label} observed date")
    if record["status"] not in CLAIM_STATUSES:
        raise SchoolLearningError(f"{label} status is invalid")
    return {
        "field": field,
        "value": claim_value,
        "source": source,
        "observed_at": observed_at,
        "status": record["status"],
    }


def _validate_reviewed_claims(value: object, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise SchoolLearningError(f"{label} must contain one or more sourced claims")
    records = [_validate_reviewed_claim(item, f"{label} entry") for item in value]
    identities = [
        _new_claim(
            item["field"], item["value"], item["source"], item["observed_at"], item["status"]
        )["id"]
        for item in records
    ]
    if len(set(identities)) != len(identities):
        raise SchoolLearningError(f"{label} must not contain duplicate claims")
    return [item for _, item in sorted(zip(identities, records, strict=True))]


def _reviewed_identifier_list(value: object, label: str) -> list[str]:
    result = _identifier_list(value, label)
    if result != sorted(result):
        raise SchoolLearningError(f"{label} must be sorted")
    return result


def _validate_reviewed_operation(value: object, index: int) -> dict[str, Any]:
    label = f"reviewed operation {index}"
    if not isinstance(value, dict):
        raise SchoolLearningError(f"{label} must be an object")
    kind = value.get("kind")
    if kind not in REVIEWED_OPERATION_KINDS:
        raise SchoolLearningError(f"{label} kind is unsupported")
    if kind == "assessment-upsert":
        record = _exact_object(value, _REVIEWED_ASSESSMENT_KEYS, label)
        assessment_type = _normalize_assessment_type(record["type"], f"{label} type")
        if assessment_type != record["type"]:
            raise SchoolLearningError(f"{label} type must use its canonical normalized form")
        if record["status"] not in ASSESSMENT_STATUSES:
            raise SchoolLearningError(f"{label} status is invalid")
        return {
            "kind": kind,
            "id": _component(record["id"], f"{label} id"),
            "title": _nonempty_string(record["title"], f"{label} title").strip(),
            "type": assessment_type,
            "status": record["status"],
            "weight": _optional_measure(record["weight"], f"{label} weight"),
            "points": _optional_measure(record["points"], f"{label} points"),
            "xp": _optional_measure(record["xp"], f"{label} XP"),
            "material_ids": _reviewed_identifier_list(
                record["material_ids"], f"{label} material ids"
            ),
            "topic_ids": _reviewed_identifier_list(record["topic_ids"], f"{label} topic ids"),
            "claims": _validate_reviewed_claims(record["claims"], f"{label} claims"),
            "recorded_at": _timestamp(record["recorded_at"], f"{label} timestamp"),
        }
    if kind == "policy-upsert":
        record = _exact_object(value, _REVIEWED_POLICY_KEYS, label)
        claims = _validate_reviewed_claims(record["claims"], f"{label} claims")
        if any(item["field"] != "rule" for item in claims):
            raise SchoolLearningError(f"{label} claims must use the policy field rule")
        return {
            "kind": kind,
            "id": _component(record["id"], f"{label} id"),
            "title": _nonempty_string(record["title"], f"{label} title").strip(),
            "category": _component(record["category"], f"{label} category"),
            "claims": claims,
            "recorded_at": _timestamp(record["recorded_at"], f"{label} timestamp"),
        }
    if kind == "source-upsert":
        record = _exact_object(value, _REVIEWED_SOURCE_KEYS, label)
        source = {
            "id": _component(record["id"], f"{label} id"),
            "title": _nonempty_string(record["title"], f"{label} title").strip(),
            "reference": _nonempty_string(record["reference"], f"{label} reference").strip(),
            "status": record["status"],
        }
        _validate_source(source)
        return {
            "kind": kind,
            **source,
            "recorded_at": _timestamp(record["recorded_at"], f"{label} timestamp"),
        }
    record = _exact_object(value, _REVIEWED_OBSERVATION_KEYS, label)
    material_ids = _reviewed_identifier_list(
        record["material_ids"], f"{label} material ids"
    )
    observation = _source_observation_record(
        record["source_id"],
        record["scope"],
        record["outcome"],
        material_ids=material_ids,
        note=record["note"],
        observed_at=record["observed_at"],
        observation_id=record["id"],
    )
    return {"kind": kind, **observation}


def _validate_reviewed_update(value: object) -> dict[str, Any]:
    record = _exact_object(value, _REVIEWED_UPDATE_KEYS, "reviewed update")
    if record["schema_version"] != REVIEWED_UPDATE_SCHEMA:
        raise SchoolLearningError("unsupported reviewed update schema")
    term = _component(record["term"], "reviewed update term")
    course_id = _component(record["course_id"], "reviewed update course id")
    base = record["base_context_sha256"]
    if not isinstance(base, str) or not _DIGEST.fullmatch(base):
        raise SchoolLearningError("reviewed update base context digest is invalid")
    if not isinstance(record["operations"], list) or not record["operations"]:
        raise SchoolLearningError("reviewed update must contain one or more operations")
    if len(record["operations"]) > _REVIEWED_UPDATE_MAX_OPERATIONS:
        raise SchoolLearningError(
            f"reviewed update may contain at most {_REVIEWED_UPDATE_MAX_OPERATIONS} operations"
        )
    operations = [
        _validate_reviewed_operation(item, index)
        for index, item in enumerate(record["operations"], start=1)
    ]
    return {
        "schema_version": REVIEWED_UPDATE_SCHEMA,
        "term": term,
        "course_id": course_id,
        "base_context_sha256": base,
        "operations": operations,
    }


def _canonical_json_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise SchoolLearningError("value cannot be encoded as canonical JSON") from error


def reviewed_update_digest(value: object) -> str:
    return hashlib.sha256(_canonical_json_bytes(_validate_reviewed_update(value))).hexdigest()


def _read_reviewed_update(path: Path | str) -> tuple[Path, dict[str, Any]]:
    candidate = Path(path).expanduser().absolute()
    try:
        inspected = os.lstat(candidate)
        if not stat.S_ISREG(inspected.st_mode):
            raise SchoolLearningError("reviewed update path must be a regular non-symlink file")
        if inspected.st_size > _REVIEWED_UPDATE_MAX_BYTES:
            raise SchoolLearningError(
                f"reviewed update file exceeds the {_REVIEWED_UPDATE_MAX_BYTES:,}-byte limit"
            )
        fd = os.open(candidate, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd, "rb") as handle:
            opened = os.fstat(handle.fileno())
            if _stat_signature(opened) != _stat_signature(inspected):
                raise SchoolLearningError("reviewed update file changed before it could be read")
            content = handle.read(_REVIEWED_UPDATE_MAX_BYTES + 1)
            if _stat_signature(os.fstat(handle.fileno())) != _stat_signature(opened):
                raise SchoolLearningError("reviewed update file changed while it was being read")
    except SchoolLearningError:
        raise
    except OSError as error:
        raise SchoolLearningError("reviewed update file cannot be read safely") from error
    if len(content) > _REVIEWED_UPDATE_MAX_BYTES:
        raise SchoolLearningError(
            f"reviewed update file exceeds the {_REVIEWED_UPDATE_MAX_BYTES:,}-byte limit"
        )
    try:
        value = json.loads(content.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise SchoolLearningError("reviewed update file is not valid UTF-8 JSON") from error
    return candidate, _validate_reviewed_update(value)


def _simulate_reviewed_update(
    ws: Workspace, state: _State, candidate: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    if state.core is None or state.source_observations is None:
        raise SchoolLearningError("reviewed update requires v0.2 course registration")
    core = json.loads(json.dumps(state.core))
    observations = json.loads(json.dumps(state.source_observations))
    for operation in candidate["operations"]:
        kind = operation["kind"]
        if kind == "source-upsert":
            _upsert_source_record(
                core,
                operation["id"],
                operation["title"],
                operation["reference"],
                operation["status"],
                operation["recorded_at"],
            )
        elif kind == "source-observation":
            record = {key: operation[key] for key in _SOURCE_OBSERVATION_KEYS}
            _append_source_observation_record(observations, record, state.materials, core)
        elif kind == "assessment-upsert":
            existing = next(
                (item for item in core["assessments"] if item["id"] == operation["id"]), None
            )
            claims = [] if existing is None else json.loads(json.dumps(existing["claims"]))
            for candidate_claim in operation["claims"]:
                _append_claim_preserving_conflict(
                    claims,
                    _new_claim(
                        candidate_claim["field"],
                        candidate_claim["value"],
                        candidate_claim["source"],
                        candidate_claim["observed_at"],
                        candidate_claim["status"],
                    ),
                )
            assessment = {
                "id": operation["id"],
                "title": operation["title"],
                "type": operation["type"],
                "status": operation["status"],
                "weight": operation["weight"],
                "points": operation["points"],
                "xp": operation["xp"],
                "material_ids": operation["material_ids"],
                "topic_ids": operation["topic_ids"],
                "claims": claims,
            }
            _validate_assessment(assessment)
            if existing is None:
                core["assessments"].append(assessment)
            else:
                core["assessments"][core["assessments"].index(existing)] = assessment
            core["assessments"].sort(key=lambda item: item["id"])
            core["updated_at"] = operation["recorded_at"]
        elif kind == "policy-upsert":
            existing = next(
                (item for item in core["policies"] if item["id"] == operation["id"]), None
            )
            claims = [] if existing is None else json.loads(json.dumps(existing["claims"]))
            for candidate_claim in operation["claims"]:
                _append_claim_preserving_conflict(
                    claims,
                    _new_claim(
                        candidate_claim["field"],
                        candidate_claim["value"],
                        candidate_claim["source"],
                        candidate_claim["observed_at"],
                        candidate_claim["status"],
                    ),
                )
            policy = {
                "id": operation["id"],
                "title": operation["title"],
                "category": operation["category"],
                "status": _aggregate_claim_status(claims),
                "claims": claims,
            }
            _validate_policy(policy)
            if existing is None:
                core["policies"].append(policy)
            else:
                core["policies"][core["policies"].index(existing)] = policy
            core["policies"].sort(key=lambda item: item["id"])
            core["updated_at"] = operation["recorded_at"]
        else:  # pragma: no cover - exact operation validation guards this branch
            raise AssertionError(kind)
        _validate_course_core(core, ws)
        _validate_v02_references(state.materials, state.topics, core)
        _validate_source_observations(observations)
        _validate_source_observation_references(observations, state.materials, core)
    return core, observations


def _pretty_json_bytes(value: object) -> bytes:
    try:
        return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode(
            "utf-8"
        )
    except (TypeError, ValueError) as error:
        raise SchoolLearningError("state cannot be encoded as JSON") from error


def _reviewed_update_preview(
    candidate: dict[str, Any],
    digest: str,
    current_core: dict[str, Any],
    proposed_core: dict[str, Any],
    current_observations: dict[str, Any],
    proposed_observations: dict[str, Any],
) -> str:
    lines = [
        "Reviewed update preview",
        f"Term: {candidate['term']}",
        f"Course: {candidate['course_id']}",
        f"Base course-context SHA-256: {candidate['base_context_sha256']}",
        f"Semantic candidate SHA-256: {digest}",
        "Operations:",
    ]
    for index, operation in enumerate(candidate["operations"], start=1):
        lines.append(f"  {index}. {operation['kind']} {operation['id']}")
    lines.append("Durable state diff:")
    pairs = (
        ("course-core.json", current_core, proposed_core),
        ("source-observations.json", current_observations, proposed_observations),
    )
    changed = False
    for filename, before, after in pairs:
        before_lines = _pretty_json_bytes(before).decode("utf-8").splitlines()
        after_lines = _pretty_json_bytes(after).decode("utf-8").splitlines()
        if before_lines == after_lines:
            continue
        changed = True
        lines.extend(
            difflib.unified_diff(
                before_lines,
                after_lines,
                fromfile=f"current/{filename}",
                tofile=f"proposed/{filename}",
                lineterm="",
            )
        )
    if not changed:
        lines.append("  No semantic durable-state change.")
    return "\n".join(lines) + "\n"


def _reviewed_semantic_state_sha256(state: _State) -> str:
    return hashlib.sha256(_course_context_bytes(state)).hexdigest()


def _prepare_reviewed_update(
    data_root: Path | str, candidate_path: Path | str
) -> tuple[Path, Workspace, _State, dict[str, Any], dict[str, Any], dict[str, Any], str]:
    path, candidate = _read_reviewed_update(candidate_path)
    sw = semester_workspace(data_root, candidate["term"])
    semester = load_semester(sw)
    if candidate["course_id"] not in semester["course_ids"]:
        raise SchoolLearningError("reviewed update course is not registered in the named semester")
    ws = workspace(sw.data_root, candidate["term"], candidate["course_id"])
    state = _load_state(ws)
    context_digest = _reviewed_semantic_state_sha256(state)
    if candidate["base_context_sha256"] != context_digest:
        raise SchoolLearningError("reviewed update base course context is stale or mismatched")
    proposed_core, proposed_observations = _simulate_reviewed_update(ws, state, candidate)
    digest = reviewed_update_digest(candidate)
    return path, ws, state, candidate, proposed_core, proposed_observations, digest


def review_update(data_root: Path | str, candidate_path: Path | str) -> dict[str, Any]:
    (
        path,
        _ws,
        state,
        candidate,
        proposed_core,
        proposed_observations,
        digest,
    ) = _prepare_reviewed_update(data_root, candidate_path)
    if state.core is None or state.source_observations is None:  # pragma: no cover - prepared above
        raise SchoolLearningError("reviewed update requires v0.2 course registration")
    return {
        "path": path,
        "digest": digest,
        "preview": _reviewed_update_preview(
            candidate,
            digest,
            state.core,
            proposed_core,
            state.source_observations,
            proposed_observations,
        ),
    }


def _restore_reviewed_update_file(
    ws: Workspace, path: Path, previous: bytes | None, label: str
) -> None:
    if previous is None:
        _safe_unlink(ws, path, label, missing_ok=True)
    else:
        _atomic_write_bytes(ws, path, previous)


def apply_update(
    data_root: Path | str, candidate_path: Path | str, confirm: str
) -> dict[str, Any]:
    path, candidate = _read_reviewed_update(candidate_path)
    digest = reviewed_update_digest(candidate)
    if not isinstance(confirm, str) or not _DIGEST.fullmatch(confirm) or confirm != digest:
        raise SchoolLearningError("reviewed update confirmation digest does not match the candidate")
    (
        prepared_path,
        ws,
        state,
        prepared_candidate,
        proposed_core,
        proposed_observations,
        prepared_digest,
    ) = _prepare_reviewed_update(data_root, path)
    if prepared_path != path or prepared_candidate != candidate or prepared_digest != digest:
        raise SchoolLearningError("reviewed update changed while it was being prepared")
    if state.core is None or state.source_observations is None:  # pragma: no cover - prepared above
        raise SchoolLearningError("reviewed update requires v0.2 course registration")

    latest_path, latest_candidate = _read_reviewed_update(path)
    latest_state = _load_state(ws)
    if latest_path != path or latest_candidate != candidate:
        raise SchoolLearningError("reviewed update changed before persistence")
    if _reviewed_semantic_state_sha256(latest_state) != candidate["base_context_sha256"]:
        raise SchoolLearningError("reviewed update base course context became stale before persistence")
    state = latest_state
    proposed_core, proposed_observations = _simulate_reviewed_update(ws, state, candidate)

    core_path = ws.course_dir / "course-core.json"
    observations_path = ws.course_dir / "source-observations.json"
    old_core = _read_regular_bytes(ws, core_path, "course core state file")
    observations_existed = observations_path.exists()
    old_observations = (
        _read_regular_bytes(ws, observations_path, "source observations state file")
        if observations_existed
        else None
    )
    writes = []
    if proposed_core != state.core:
        writes.append((core_path, proposed_core, old_core, "course-core.json"))
    if proposed_observations != state.source_observations:
        writes.append(
            (
                observations_path,
                proposed_observations,
                old_observations,
                "source-observations.json",
            )
        )
    attempted: list[tuple[Path, bytes | None, str]] = []
    try:
        for destination, value, previous, label in writes:
            attempted.append((destination, previous, label))
            _atomic_write_json(ws, destination, value)
        persisted = _load_state(ws)
        if persisted.core != proposed_core or persisted.source_observations != proposed_observations:
            raise SchoolLearningError("reviewed update did not persist the complete proposed state")
    except Exception as error:
        rollback_errors: list[str] = []
        for destination, previous, label in reversed(attempted):
            try:
                _restore_reviewed_update_file(
                    ws, destination, previous, f"failed reviewed update rollback for {label}"
                )
            except SchoolLearningError as rollback_error:
                rollback_errors.append(str(rollback_error))
        for destination, previous, label in attempted:
            try:
                if previous is None:
                    if destination.exists() or destination.is_symlink():
                        rollback_errors.append(f"{label} should be absent after rollback")
                elif _read_regular_bytes(ws, destination, f"rollback verification for {label}") != previous:
                    rollback_errors.append(f"{label} bytes differ after rollback")
            except SchoolLearningError as rollback_error:
                rollback_errors.append(str(rollback_error))
        if rollback_errors:
            raise SchoolLearningError(
                "reviewed update failed and rollback was incomplete: " + "; ".join(rollback_errors)
            ) from error
        raise _as_school_error("reviewed update failed; exact prior state was restored", error) from error
    return {
        "path": path,
        "digest": digest,
        "operation_count": len(candidate["operations"]),
        "changed_files": [item[3] for item in writes],
    }


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
    kind: object = _UNSET,
    status: object = _UNSET,
    relevant_date: object = _UNSET,
    topic_ids: object = _UNSET,
    assessment_ids: object = _UNSET,
    provenance: object = _UNSET,
) -> dict[str, Any]:
    safe_id = _component(material_id, "material_id")
    safe_title = _nonempty_string(title, "material title").strip()
    timestamp = _timestamp(added_at if added_at is not None else utc_now(), "material timestamp")
    source_path = _lexical_absolute(Path(source).expanduser())
    suffix = source_path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise SchoolLearningError("material extension is unsupported")
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
    old_path = _material_path(ws, existing) if existing is not None else None
    record = {
        "id": safe_id,
        "title": safe_title,
        "type": SUPPORTED_SUFFIXES[suffix],
        "source_name": source_path.name,
        "stored_path": stored_relative.as_posix(),
        "sha256": "0" * 64,
        "bytes": 0,
        "added_at": timestamp,
    }
    if kind is None:
        kind = _UNSET
    if status is None:
        status = _UNSET
    rich_metadata_supplied = any(
        item is not _UNSET
        for item in (kind, status, relevant_date, topic_ids, assessment_ids, provenance)
    )
    if manifest["schema_version"] == MATERIALS_V02_SCHEMA:
        def resolved_metadata(field: str, supplied: object, default: object) -> object:
            if supplied is not _UNSET:
                return supplied
            return default if existing is None else existing[field]

        def resolved_metadata_ids(field: str, supplied: object) -> list[str]:
            if supplied is _UNSET:
                return [] if existing is None else list(existing[field])
            return _normalize_material_ids(supplied)  # type: ignore[arg-type]

        metadata = {
            "kind": resolved_metadata("kind", kind, "unspecified"),
            "status": resolved_metadata("status", status, "reference"),
            "relevant_date": resolved_metadata("relevant_date", relevant_date, None),
            "topic_ids": resolved_metadata_ids("topic_ids", topic_ids),
            "assessment_ids": resolved_metadata_ids("assessment_ids", assessment_ids),
            "provenance": resolved_metadata("provenance", provenance, None),
        }
        record.update(metadata)
    elif rich_metadata_supplied:
        raise SchoolLearningError("rich material metadata requires deliberate v0.2 course registration")
    _validate_material(record, manifest["schema_version"])
    if existing is None:
        records.append(record)
    else:
        records[records.index(existing)] = record
    records.sort(key=lambda item: item["id"])
    _validate_materials(manifest)
    _validate_v02_references(manifest, state.topics, state.core)

    manifest_path = _confined_path(
        ws,
        ws.course_dir / "materials.json",
        label="materials state file",
        must_exist=True,
        require_file=True,
    )
    old_manifest = _read_regular_bytes(ws, manifest_path, "materials state file")
    temporary: Path | None = None
    backup: Path | None = None
    old_moved = False
    new_installed = False
    manifest_attempted = False
    try:
        temporary, digest, size = _copy_source_to_temp(ws, source_path, destination.parent)
        record["sha256"] = digest
        record["bytes"] = size
        _validate_material(record, manifest["schema_version"])
        changed = existing is None or not _stored_matches(
            ws, existing, digest, size, destination
        )
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
        if temporary is not None and (temporary.exists() or temporary.is_symlink()):
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
        changed = True
    else:
        changed = existing["title"] != safe_title
        if changed:
            existing["title"] = safe_title
        if set(existing["material_ids"]) != set(normalized_materials):
            existing["material_ids"] = normalized_materials
            changed = True
    if not changed:
        return dict(existing)
    topics["topics"].sort(key=lambda item: item["id"])
    _validate_topics(topics)
    _atomic_write_json(ws, ws.course_dir / "topics.json", topics)
    return dict(existing)


def _study_payload(
    ws: Workspace,
    topic_id: str,
    mode: str,
    objective: str,
) -> tuple[_State, dict[str, Any], list[dict[str, Any]], str, bytes]:
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
    return state, topic, selected, safe_objective, "\n".join(lines).encode("utf-8")


def build_study_brief(
    ws: Workspace,
    topic_id: str,
    mode: str,
    objective: str,
    *,
    output: Path | None = None,
) -> Path:
    _, _, _, _, content = _study_payload(ws, topic_id, mode, objective)
    destination = output if output is not None else ws.course_dir / "generated" / "study-brief.md"
    safe_destination = _confined_path(
        ws,
        destination,
        label="study brief output",
        regular_if_present=True,
    )
    _atomic_write_bytes(ws, safe_destination, content)
    return safe_destination


def _stat_signature(value: os.stat_result) -> tuple[int, int, int, int, int]:
    return (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)


def _files_are_identical(ws: Workspace, first: Path, second: Path) -> bool:
    safe_first = _confined_path(
        ws,
        first,
        label="material identity source",
        must_exist=True,
        require_file=True,
    )
    safe_second = _confined_path(
        ws,
        second,
        label="material identity copy",
        must_exist=True,
        require_file=True,
    )
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        first_fd = os.open(safe_first, flags)
        with os.fdopen(first_fd, "rb") as first_handle:
            second_fd = os.open(safe_second, flags)
            with os.fdopen(second_fd, "rb") as second_handle:
                if not stat.S_ISREG(os.fstat(first_handle.fileno()).st_mode):
                    raise SchoolLearningError("material identity source must be a regular file")
                if not stat.S_ISREG(os.fstat(second_handle.fileno()).st_mode):
                    raise SchoolLearningError("material identity copy must be a regular file")
                while True:
                    first_chunk = first_handle.read(1024 * 1024)
                    second_chunk = second_handle.read(1024 * 1024)
                    if first_chunk != second_chunk:
                        return False
                    if not first_chunk:
                        return True
    except SchoolLearningError:
        raise
    except OSError as error:
        raise SchoolLearningError("material byte identity cannot be checked safely") from error


def _copy_verified_material_attachment(
    ws: Workspace,
    record: dict[str, Any],
    destination: Path,
) -> None:
    source = _material_path(ws, record)
    safe_destination = _confined_path(
        ws,
        destination,
        label=f"material attachment {record['id']}",
        regular_if_present=True,
    )
    _confined_path(
        ws,
        safe_destination.parent,
        label="material attachments directory",
        must_exist=True,
        require_directory=True,
    )
    if safe_destination.exists():
        raise SchoolLearningError("material attachment filename is duplicated")

    try:
        before = os.lstat(source)
    except OSError as error:
        raise SchoolLearningError(f"stored material {record['id']} cannot be inspected") from error
    if not stat.S_ISREG(before.st_mode):
        raise SchoolLearningError(f"stored material {record['id']} must be a regular file")
    before_signature = _stat_signature(before)
    before_digest, before_size = _hash_confined_file(
        ws, source, f"stored material {record['id']} before handoff copy"
    )
    try:
        after_initial_hash = os.lstat(source)
    except OSError as error:
        raise SchoolLearningError(f"stored material {record['id']} cannot be reinspected") from error
    if _stat_signature(after_initial_hash) != before_signature:
        raise SchoolLearningError(f"stored material {record['id']} changed during handoff preparation")
    if before_digest != record["sha256"] or before_size != record["bytes"]:
        raise SchoolLearningError(f"stored material {record['id']} does not match its recorded identity")

    source_fd: int | None = None
    target_fd: int | None = None
    completed = False
    try:
        source_fd = os.open(source, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        opened_signature = _stat_signature(os.fstat(source_fd))
        if opened_signature != before_signature:
            raise SchoolLearningError(f"stored material {record['id']} changed before handoff copy")
        target_fd = os.open(
            safe_destination,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
        with os.fdopen(source_fd, "rb") as origin, os.fdopen(target_fd, "wb") as target:
            source_fd = None
            target_fd = None
            if not stat.S_ISREG(os.fstat(origin.fileno()).st_mode):
                raise SchoolLearningError(f"stored material {record['id']} must be a regular file")
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
            if _stat_signature(os.fstat(origin.fileno())) != before_signature:
                raise SchoolLearningError(
                    f"stored material {record['id']} changed during handoff preparation"
                )
        if digest.hexdigest() != record["sha256"] or size != record["bytes"]:
            raise SchoolLearningError(f"stored material {record['id']} changed during handoff copy")

        source = _confined_path(
            ws,
            source,
            label=f"stored material {record['id']} after handoff copy",
            must_exist=True,
            require_file=True,
        )
        try:
            after_copy = os.lstat(source)
        except OSError as error:
            raise SchoolLearningError(f"stored material {record['id']} cannot be reinspected") from error
        if _stat_signature(after_copy) != before_signature:
            raise SchoolLearningError(f"stored material {record['id']} changed during handoff preparation")
        after_digest, after_size = _hash_confined_file(
            ws, source, f"stored material {record['id']} after handoff copy"
        )
        output_digest, output_size = _hash_confined_file(
            ws, safe_destination, f"copied material {record['id']}"
        )
        if (after_digest, after_size) != (record["sha256"], record["bytes"]):
            raise SchoolLearningError(f"stored material {record['id']} changed during handoff preparation")
        if (output_digest, output_size) != (record["sha256"], record["bytes"]):
            raise SchoolLearningError(f"copied material {record['id']} failed identity verification")
        if not _files_are_identical(ws, source, safe_destination):
            raise SchoolLearningError(f"copied material {record['id']} is not byte-identical")
        try:
            final_source = os.lstat(source)
        except OSError as error:
            raise SchoolLearningError(f"stored material {record['id']} cannot be reinspected") from error
        if _stat_signature(final_source) != before_signature:
            raise SchoolLearningError(f"stored material {record['id']} changed during handoff preparation")
        completed = True
    except SchoolLearningError:
        raise
    except OSError as error:
        raise SchoolLearningError(f"material {record['id']} could not be copied safely") from error
    finally:
        if source_fd is not None:
            os.close(source_fd)
        if target_fd is not None:
            os.close(target_fd)
        if not completed and (safe_destination.exists() or safe_destination.is_symlink()):
            _safe_unlink(ws, safe_destination, "failed material attachment", missing_ok=True)


def _prompt_bytes(
    course: dict[str, Any],
    topic: dict[str, Any],
    selected: list[dict[str, Any]],
    mode: str,
    objective: str,
) -> bytes:
    identifiers = ", ".join(f"`{record['id']}`" for record in selected) or "none"
    lines = [
        f"Help me study {topic['title']} (`{topic['id']}`) for {course['title']} (`{course['course_id']}`), term `{course['term']}`.",
        f"Mode: `{mode}`.",
        f"Objective: {objective}",
        "",
        "Use the attached `study-brief.md` as the study contract. Treat only the attached files whose names begin with `material-` as selected course-grounding evidence.",
        f"The selected material identifiers are: {identifiers}.",
        "Cite the material identifier supporting every consequential explanation or correction.",
        "Clearly label general background knowledge separately from material-backed statements.",
        "If the selected materials do not support an answer, disclose that the supplied evidence is insufficient.",
        "Do not infer any grade, mastery, permission, deadline, or course policy.",
        "End with a compact completion result containing an outcome suggestion (`correct`, `partial`, or `incorrect`), weak points, and the recommended next review.",
        "The owner will review the result and make any final learner-state recording with `./school record`; this AI result must not update learner state automatically.",
        "",
    ]
    return "\n".join(lines).encode("utf-8")


def _start_here_bytes() -> bytes:
    return (
        "# Start Here\n\n"
        "1. Open `attachments/`.\n"
        "2. Attach every file in that directory to the approved AI interface.\n"
        "3. Paste the complete contents of `prompt.txt` as the opening message.\n"
        "4. Do not substitute similarly named files from elsewhere in the course workspace.\n"
        "5. Review the AI result yourself. It does not update learner state automatically.\n"
    ).encode("utf-8")


def _validate_staged_handoff(
    ws: Workspace,
    staging: Path,
    manifest: dict[str, Any],
    expected_files: dict[str, bytes],
    selected: list[dict[str, Any]],
) -> None:
    root = _inspect_real_tree(ws, staging, "study handoff staging directory")
    try:
        root_names = {path.name for path in root.iterdir()}
    except OSError as error:
        raise SchoolLearningError("study handoff staging directory cannot be read") from error
    if root_names != {"START-HERE.md", "prompt.txt", "manifest.json", "attachments"}:
        raise SchoolLearningError("study handoff package structure is invalid")
    attachments = _confined_path(
        ws,
        root / "attachments",
        label="study handoff attachments",
        must_exist=True,
        require_directory=True,
    )
    try:
        attachment_names = sorted(path.name for path in attachments.iterdir())
    except OSError as error:
        raise SchoolLearningError("study handoff attachments cannot be read") from error
    if attachment_names != sorted(manifest["attachment_filenames"]):
        raise SchoolLearningError("study handoff attachments do not match the manifest")
    for relative, expected in expected_files.items():
        path = root / relative
        if _read_regular_bytes(ws, path, f"study handoff file {relative}") != expected:
            raise SchoolLearningError(f"study handoff file {relative} is not deterministic")
    encoded_manifest = _read_json(ws, root / "manifest.json", "study handoff manifest")
    _validate_study_handoff_manifest(encoded_manifest)
    if encoded_manifest != manifest:
        raise SchoolLearningError("study handoff manifest changed during preparation")
    selected_by_id = {record["id"]: record for record in selected}
    if set(selected_by_id) != set(manifest["material_ids"]):
        raise SchoolLearningError("study handoff materials do not match the selected materials")
    for material in manifest["materials"]:
        material_id = material["id"]
        record = selected_by_id[material_id]
        suffix = Path(record["stored_path"]).suffix.lower()
        if material["attachment_filename"] != f"material-{material_id}{suffix}":
            raise SchoolLearningError(f"material attachment {material_id} has the wrong filename")
        if material["sha256"] != record["sha256"] or material["bytes"] != record["bytes"]:
            raise SchoolLearningError(f"material attachment {material_id} has the wrong identity")
        attachment = _confined_path(
            ws,
            attachments / material["attachment_filename"],
            label=f"final material attachment {material_id}",
            must_exist=True,
            require_file=True,
        )
        if attachment.parent != attachments:
            raise SchoolLearningError(f"material attachment {material_id} escapes its package")
        source = _material_path(ws, record)
        source_digest, source_size = _hash_confined_file(
            ws, source, f"selected stored material {material_id} before publication"
        )
        attachment_digest, attachment_size = _hash_confined_file(
            ws, attachment, f"final material attachment {material_id}"
        )
        expected_identity = (material["sha256"], material["bytes"])
        if (source_digest, source_size) != expected_identity:
            raise SchoolLearningError(
                f"selected stored material {material_id} changed before publication"
            )
        if (attachment_digest, attachment_size) != expected_identity:
            raise SchoolLearningError(f"material attachment {material_id} changed before publication")
        if not _files_are_identical(ws, source, attachment):
            raise SchoolLearningError(
                f"material attachment {material_id} is not byte-identical before publication"
            )


def _course_context_bytes(state: _State) -> bytes:
    if state.core is None or state.source_observations is None:
        raise SchoolLearningError("course context requires v0.2 course core state")
    payload = {
        "course": state.course,
        "course_core": state.core,
        "profile": {
            "capability_tags": state.core["capability_tags"],
            "sources": state.core["sources"],
            "metadata": state.core["metadata"],
        },
        "materials": state.materials["materials"],
        "assessments": state.core["assessments"],
        "policies": state.core["policies"],
        "source_observations": state.source_observations,
        "topics": state.topics["topics"],
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
    return (
        "# Course Context\n\n"
        "Durable local state follows as strict JSON. Conflicting claims are intentionally preserved.\n\n"
        "```json\n"
        + encoded
        + "\n```\n"
    ).encode("utf-8")


def course_context_bytes(ws: Workspace) -> bytes:
    return _course_context_bytes(_load_state(ws))


def course_context_sha256(ws: Workspace) -> str:
    return _reviewed_semantic_state_sha256(_load_state(ws))


def _course_prompt_bytes(course: dict[str, Any]) -> bytes:
    return (
        f"Use course-context.md and the exact selected attachments to assist with "
        f"{course['title']} ({course['course_id']}, {course['term']}).\n\n"
        "Treat stored claims as claims with their recorded provenance and status. Preserve conflicts; "
        "do not choose a silent winner. Do not invent missing course facts, dates, deadlines, policies, "
        "permission, grades, readiness, or learner mastery. Clearly separate general knowledge from "
        "course-grounded statements. If evidence is insufficient, say so. When the user explicitly asks "
        "to synchronize reviewed findings, return one candidate matching update-contract.json. The "
        "candidate is data only: never claim that returning it changed local state. This package stays "
        "manual and no AI response updates local state automatically.\n"
    ).encode("utf-8")


def _validate_staged_course_handoff(
    ws: Workspace,
    staging: Path,
    manifest: dict[str, Any],
    expected_files: dict[str, bytes],
    selected: list[dict[str, Any]],
) -> None:
    root = _inspect_real_tree(ws, staging, "course handoff staging directory")
    try:
        names = {path.name for path in root.iterdir()}
    except OSError as error:
        raise SchoolLearningError("course handoff staging directory cannot be read") from error
    if names != {"START-HERE.md", "prompt.txt", "manifest.json", "attachments"}:
        raise SchoolLearningError("course handoff package structure is invalid")
    attachments = _confined_path(
        ws, root / "attachments", label="course handoff attachments", must_exist=True,
        require_directory=True,
    )
    try:
        filenames = sorted(path.name for path in attachments.iterdir())
    except OSError as error:
        raise SchoolLearningError("course handoff attachments cannot be read") from error
    if filenames != sorted(manifest["attachment_filenames"]):
        raise SchoolLearningError("course handoff attachments do not match the manifest")
    for relative, expected in expected_files.items():
        if _read_regular_bytes(ws, root / relative, f"course handoff file {relative}") != expected:
            raise SchoolLearningError(f"course handoff file {relative} is not deterministic")
    encoded = _read_json(ws, root / "manifest.json", "course handoff manifest")
    _validate_course_handoff_manifest(encoded)
    if encoded != manifest:
        raise SchoolLearningError("course handoff manifest changed during preparation")
    selected_by_id = {item["id"]: item for item in selected}
    if set(selected_by_id) != set(manifest["material_ids"]):
        raise SchoolLearningError("course handoff materials do not exactly match the selection")
    context_entry = manifest["context_attachment"]
    context_path = attachments / context_entry["attachment_filename"]
    if _hash_confined_file(ws, context_path, "course context attachment") != (
        context_entry["sha256"],
        context_entry["bytes"],
    ):
        raise SchoolLearningError("course context attachment has the wrong identity")
    contract_entry = manifest["update_contract_attachment"]
    contract_path = attachments / contract_entry["attachment_filename"]
    if _hash_confined_file(ws, contract_path, "course update contract attachment") != (
        contract_entry["sha256"],
        contract_entry["bytes"],
    ):
        raise SchoolLearningError("course update contract attachment has the wrong identity")
    contract = _validate_update_contract(
        _read_json(ws, contract_path, "course update contract attachment")
    )
    if contract["term"] != manifest["term"] or contract["course_id"] != manifest["course_id"]:
        raise SchoolLearningError("course update contract identity does not match the handoff")
    if contract["base_context_sha256"] != context_entry["sha256"]:
        raise SchoolLearningError("course update contract base digest does not match course context")
    for entry in manifest["materials"]:
        record = selected_by_id.get(entry["id"])
        if record is None:
            raise SchoolLearningError("course handoff contains an unselected material")
        attachment = attachments / entry["attachment_filename"]
        source = _material_path(ws, record)
        expected_identity = (entry["sha256"], entry["bytes"])
        if _hash_confined_file(ws, source, "selected course handoff material") != expected_identity:
            raise SchoolLearningError(f"selected material {entry['id']} changed before publication")
        if _hash_confined_file(ws, attachment, "course handoff attachment") != expected_identity:
            raise SchoolLearningError(f"course handoff attachment {entry['id']} changed")
        if not _files_are_identical(ws, source, attachment):
            raise SchoolLearningError(f"course handoff attachment {entry['id']} is not byte-identical")


def prepare_study_handoff(
    ws: Workspace,
    topic_id: str,
    mode: str,
    objective: str,
) -> dict[str, Path]:
    state, topic, selected, safe_objective, brief = _study_payload(ws, topic_id, mode, objective)
    legacy_brief = _confined_path(
        ws,
        ws.course_dir / "generated" / "study-brief.md",
        label="study brief output",
        regular_if_present=True,
    )
    _atomic_write_bytes(ws, legacy_brief, brief)

    handoff_selected = sorted(selected, key=lambda record: record["id"])
    material_entries = []
    for record in handoff_selected:
        suffix = Path(record["stored_path"]).suffix.lower()
        filename = f"material-{record['id']}{suffix}"
        material_entries.append(
            {
                "id": record["id"],
                "attachment_filename": filename,
                "sha256": record["sha256"],
                "bytes": record["bytes"],
            }
        )
    manifest = {
        "schema_version": STUDY_HANDOFF_SCHEMA,
        "course_id": state.course["course_id"],
        "term": state.course["term"],
        "topic_id": topic["id"],
        "mode": mode,
        "objective": safe_objective,
        "attachment_filenames": ["study-brief.md"]
        + [entry["attachment_filename"] for entry in material_entries],
        "material_ids": [entry["id"] for entry in material_entries],
        "materials": material_entries,
    }
    _validate_study_handoff_manifest(manifest)

    generated = _confined_path(
        ws,
        ws.course_dir / "generated",
        label="generated directory",
        must_exist=True,
        require_directory=True,
    )
    destination = generated / "study-handoff"
    staging = _create_temp_directory(ws, generated, ".study-handoff.staging.")
    try:
        attachments = staging / "attachments"
        _safe_create_directory(attachments, "study handoff attachments directory")
        prompt = _prompt_bytes(state.course, topic, handoff_selected, mode, safe_objective)
        start_here = _start_here_bytes()
        manifest_bytes = (
            json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        ).encode("utf-8")
        expected_files = {
            "START-HERE.md": start_here,
            "prompt.txt": prompt,
            "manifest.json": manifest_bytes,
            "attachments/study-brief.md": brief,
        }
        _atomic_write_bytes(ws, staging / "START-HERE.md", start_here)
        _atomic_write_bytes(ws, staging / "prompt.txt", prompt)
        _atomic_write_bytes(ws, attachments / "study-brief.md", brief)
        for record, entry in zip(handoff_selected, material_entries, strict=True):
            _copy_verified_material_attachment(
                ws,
                record,
                attachments / entry["attachment_filename"],
            )
        _atomic_write_bytes(ws, staging / "manifest.json", manifest_bytes)
        _validate_staged_handoff(ws, staging, manifest, expected_files, handoff_selected)
        _publish_directory(
            ws,
            staging,
            destination,
            lambda: _validate_staged_handoff(
                ws,
                staging,
                manifest,
                expected_files,
                handoff_selected,
            ),
        )
    except Exception as error:
        if isinstance(error, SchoolLearningError):
            causal = error
        else:
            causal = SchoolLearningError("study handoff preparation failed")
            causal.__cause__ = error
        _recover_remove_tree(
            ws,
            staging,
            "failed study handoff staging directory",
            causal,
        )
        if causal is error:
            raise
        raise causal from error
    return {
        "root": destination,
        "attachments": destination / "attachments",
        "prompt": destination / "prompt.txt",
        "study_brief": legacy_brief,
    }


def prepare_course_handoff(
    ws: Workspace, material_ids: Iterable[str] = ()
) -> dict[str, Path]:
    state = _load_state(ws)
    if state.core is None:
        raise SchoolLearningError("course handoff requires v0.2 course registration")
    selected_ids = _normalize_material_ids(material_ids)
    by_id = {item["id"]: item for item in state.materials["materials"]}
    unknown = set(selected_ids) - set(by_id)
    if unknown:
        raise SchoolLearningError(
            "course handoff references unknown materials: " + ", ".join(sorted(unknown))
        )
    selected = [by_id[item] for item in selected_ids]
    entries = [
        {
            "id": item["id"],
            "attachment_filename": (
                f"material-{item['id']}{Path(item['stored_path']).suffix.lower()}"
            ),
            "sha256": item["sha256"],
            "bytes": item["bytes"],
        }
        for item in selected
    ]
    context = _course_context_bytes(state)
    context_entry = {
        "role": "course-context",
        "attachment_filename": "course-context.md",
        "sha256": hashlib.sha256(context).hexdigest(),
        "bytes": len(context),
    }
    update_contract = _update_contract_value(
        ws.term, ws.course_id, context_entry["sha256"]
    )
    _validate_update_contract(update_contract)
    update_contract_bytes = _pretty_json_bytes(update_contract)
    update_contract_entry = {
        "role": "update-contract",
        "attachment_filename": "update-contract.json",
        "sha256": hashlib.sha256(update_contract_bytes).hexdigest(),
        "bytes": len(update_contract_bytes),
    }
    manifest = {
        "schema_version": COURSE_HANDOFF_SCHEMA,
        "course_id": ws.course_id,
        "term": ws.term,
        "attachment_filenames": [
            context_entry["attachment_filename"],
            update_contract_entry["attachment_filename"],
        ]
        + [item["attachment_filename"] for item in entries],
        "context_attachment": context_entry,
        "update_contract_attachment": update_contract_entry,
        "material_ids": selected_ids,
        "materials": entries,
    }
    _validate_course_handoff_manifest(manifest)
    prompt = _course_prompt_bytes(state.course)
    start = (
        "# Start Here\n\n"
        "1. Open `attachments/`.\n"
        "2. Attach every file in that directory, including the required distinguished "
        "`course-context.md` and `update-contract.json`, to the approved AI interface.\n"
        "3. Paste the complete contents of `prompt.txt` as the opening message.\n"
        "4. Do not substitute similarly named files from elsewhere in the course workspace.\n"
        "5. Review the AI result yourself. It does not update local state automatically.\n"
    ).encode("utf-8")
    manifest_bytes = (
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    generated = _confined_path(
        ws,
        ws.course_dir / "generated",
        label="generated directory",
        must_exist=True,
        require_directory=True,
    )
    destination = generated / "course-handoff"
    staging = _create_temp_directory(ws, generated, ".course-handoff.staging.")
    try:
        attachments = staging / "attachments"
        _safe_create_directory(attachments, "course handoff attachments directory")
        expected = {
            "START-HERE.md": start,
            "prompt.txt": prompt,
            "attachments/course-context.md": context,
            "attachments/update-contract.json": update_contract_bytes,
            "manifest.json": manifest_bytes,
        }
        _atomic_write_bytes(ws, staging / "START-HERE.md", start)
        _atomic_write_bytes(ws, staging / "prompt.txt", prompt)
        _atomic_write_bytes(ws, attachments / "course-context.md", context)
        _atomic_write_bytes(ws, attachments / "update-contract.json", update_contract_bytes)
        _atomic_write_bytes(ws, staging / "manifest.json", manifest_bytes)
        for record, entry in zip(selected, entries, strict=True):
            _copy_verified_material_attachment(
                ws, record, attachments / entry["attachment_filename"]
            )
        _validate_staged_course_handoff(ws, staging, manifest, expected, selected)
        _publish_directory(
            ws,
            staging,
            destination,
            lambda: _validate_staged_course_handoff(ws, staging, manifest, expected, selected),
        )
    except Exception as error:
        causal = error if isinstance(error, SchoolLearningError) else SchoolLearningError(
            "course handoff preparation failed"
        )
        _recover_remove_tree(ws, staging, "failed course handoff staging directory", causal)
        if causal is error:
            raise
        raise causal from error
    return {
        "root": destination,
        "attachments": destination / "attachments",
        "prompt": destination / "prompt.txt",
        "context": destination / "attachments" / "course-context.md",
        "update_contract": destination / "attachments" / "update-contract.json",
    }


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
    "ASSESSMENT_STATUSES",
    "ASSESSMENT_TYPES",
    "CAPABILITY_TAGS",
    "CLAIM_STATUSES",
    "COURSE_CORE_SCHEMA",
    "COURSE_HANDOFF_SCHEMA",
    "COURSE_SCHEMA",
    "MATERIALS_V02_SCHEMA",
    "MATERIALS_SCHEMA",
    "MATERIAL_KINDS",
    "MATERIAL_LIFECYCLES",
    "OUTCOMES",
    "PLANNER_CRITICAL_CLAIM_FIELDS",
    "REVIEWED_OPERATION_KINDS",
    "REVIEWED_UPDATE_SCHEMA",
    "SESSION_SCHEMA",
    "SEMESTER_SCHEMA",
    "SOURCE_OBSERVATIONS_SCHEMA",
    "SOURCE_OBSERVATION_OUTCOMES",
    "SOURCE_OBSERVATION_SCOPES",
    "STUDY_HANDOFF_SCHEMA",
    "STUDY_MODES",
    "SUPPORTED_SUFFIXES",
    "SchoolLearningError",
    "TOPICS_SCHEMA",
    "TOPIC_STATUSES",
    "Workspace",
    "add_material",
    "append_source_observation",
    "apply_update",
    "build_study_brief",
    "course_context_bytes",
    "course_context_sha256",
    "default_data_root",
    "ensure_topic",
    "initialize_course",
    "initialize_semester",
    "intake_material",
    "iter_sessions",
    "load_course",
    "load_course_core",
    "load_materials",
    "load_semester",
    "load_source_observations",
    "load_topics",
    "prepare_course_handoff",
    "prepare_study_handoff",
    "record_session",
    "register_course",
    "review_update",
    "reviewed_update_digest",
    "semester_workspace",
    "sha256_file",
    "upsert_assessment",
    "upsert_policy",
    "upsert_source",
    "workspace",
)
