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
from typing import Any, Callable, Iterable

COURSE_SCHEMA = "aiden.school.course/v0.1"
MATERIALS_SCHEMA = "aiden.school.materials/v0.1"
TOPICS_SCHEMA = "aiden.school.topics/v0.1"
SESSION_SCHEMA = "aiden.school.session/v0.1"
STUDY_HANDOFF_SCHEMA = "aiden.school.study-handoff/v0.1.1"
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
    "STUDY_HANDOFF_SCHEMA",
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
    "prepare_study_handoff",
    "record_session",
    "sha256_file",
    "workspace",
)
