#!/usr/bin/env python3
"""Bounded metadata-only storage collection and deterministic orientation."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, time, timezone
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import unicodedata
from typing import Any, Iterable, Mapping, Sequence, TextIO


SCHEMA_VERSION = 1
MAX_DEPTH = 8
MAX_ENTRIES = 100_000
MAX_JSON_LINE_BYTES = 16_384
MAX_MOUNTINFO_LINES = 100_000

WSL_CAPACITY_ROOT = Path("/")
WSL_TRAVERSAL_ROOT = Path("/").joinpath("home", "aidenm727", "src")

SCOPE_SPECS = {
    ("wsl", "wsl_root"): "capacity",
    ("wsl", "wsl_src"): "traversal",
    ("windows", "windows_c"): "capacity",
    ("windows", "windows_downloads"): "traversal",
}
COLLECTOR_ALIASES = {
    "wsl": frozenset({"wsl_root", "wsl_src"}),
    "windows": frozenset({"windows_c", "windows_downloads"}),
}
MAX_WARNING_RECORDS_PER_SCOPE = MAX_ENTRIES + 1
MAX_RECORDS_PER_COLLECTOR = (
    2 + MAX_ENTRIES + MAX_WARNING_RECORDS_PER_SCOPE + 1
)
MAX_RECORDS = len(COLLECTOR_ALIASES) * MAX_RECORDS_PER_COLLECTOR
LOCAL_SCOPE_LABELS = {
    "wsl_root": "/ logical capacity aggregate",
    "wsl_src": str(WSL_TRAVERSAL_ROOT) + " (metadata traversal only)",
    "windows_c": "C: capacity/free aggregate",
    "windows_downloads": (
        "C:" + "\\" + "Users" + "\\" + "acmen" + "\\" + "Downloads"
        + " (metadata traversal only)"
    ),
}

WARNING_REASON_CODES = frozenset(
    {
        "access_denied",
        "containment_rejected",
        "cross_device_skipped",
        "enumeration_failed",
        "max_depth_reached",
        "max_entries_reached",
        "metadata_unavailable",
        "mount_point_skipped",
        "protected_directory_skipped",
        "protected_file_skipped",
        "reparse_point_skipped",
        "symlink_skipped",
        "timestamp_unavailable",
        "unsupported_entry_type",
    }
)
COMPLETION_REASON_CODES = frozenset({"complete", "incomplete"})
COLLECTOR_ERROR_CODES = frozenset(
    {
        "capacity_unavailable",
        "elevated_execution_rejected",
        "root_is_mount",
        "root_not_allowlisted",
        "root_not_directory",
        "root_not_local",
        "root_unavailable",
    }
)

PROTECTED_DIRECTORY_NAMES = frozenset(
    name.casefold()
    for name in (
        ".aws",
        ".azure",
        ".gnupg",
        ".kube",
        ".password-store",
        ".secrets",
        ".ssh",
        "1password",
        "appdata",
        "bitwarden",
        "brave",
        "browser profiles",
        "chrome",
        "chromium",
        "credential manager",
        "credential-provider",
        "credential-providers",
        "credentials",
        "dashlane",
        "desktop",
        "documents",
        "edge",
        "firefox",
        "keepass",
        "keepassxc",
        "lastpass",
        "microsoft edge",
        "mozilla firefox",
        "opera",
        "opera gx stable",
        "opera stable",
        "passwords",
        "secrets",
        "google chrome",
    )
)
PROTECTED_FILE_NAMES = frozenset(
    name.casefold()
    for name in (
        ".bash_history",
        ".lesshst",
        ".node_repl_history",
        ".python_history",
        ".sqlite_history",
        ".zsh_history",
        "consolehost_history.txt",
    )
)
PROTECTED_FILE_SUFFIXES = frozenset({".key", ".p12", ".pem", ".pfx", ".ppk"})
BACKUP_SUFFIXES = (
    ".backup",
    ".bak",
    ".old",
    ".orig",
    ".save",
    ".swp",
    ".tmp",
    "~",
)
PROTECTED_DIRECTORY_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"(?:google\s+)?chrome(?:\s+(?:user\s+data|profile(?:s|\s+.+)?))?\Z",
        r"(?:mozilla\s+)?firefox(?:\s+(?:profile(?:s|\s+.+)?))?\Z",
        r"(?:microsoft\s+)?edge(?:\s+(?:user\s+data|profile(?:s|\s+.+)?))?\Z",
        r"brave(?:software)?(?:\s+(?:user\s+data|profile(?:s|\s+.+)?))?\Z",
        r"opera(?:\s+(?:gx\s+stable|stable|profile(?:s|\s+.+)?))?\Z",
        r"1password(?:\s+\d+)?\Z",
        r"bitwarden(?:\s+desktop)?\Z",
        r"keepass(?:xc)?(?:\s+(?:database|profile)(?:s|\s+.+)?)?\Z",
        r"(?:dashlane|lastpass)(?:\s+(?:profile|vault)(?:s|\s+.+)?)?\Z",
    )
)

CATEGORY_EXTENSIONS = {
    "document": frozenset(
        {
            ".doc", ".docx", ".epub", ".md", ".mobi", ".odp", ".ods",
            ".odt", ".pdf", ".ppt", ".pptx", ".rtf", ".tex", ".txt",
            ".xls", ".xlsx",
        }
    ),
    "image": frozenset(
        {
            ".avif", ".bmp", ".gif", ".heic", ".heif", ".jpeg", ".jpg",
            ".png", ".raw", ".svg", ".tif", ".tiff", ".webp",
        }
    ),
    "audio": frozenset(
        {".aac", ".flac", ".m4a", ".mp3", ".ogg", ".opus", ".wav", ".wma"}
    ),
    "video": frozenset(
        {".avi", ".m4v", ".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".webm", ".wmv"}
    ),
    "archive": frozenset(
        {".7z", ".bz2", ".gz", ".rar", ".tar", ".tgz", ".xz", ".zip", ".zst"}
    ),
    "code": frozenset(
        {
            ".bat", ".c", ".cc", ".cmd", ".cpp", ".cs", ".css", ".go",
            ".h", ".hpp", ".html", ".ini", ".java", ".js", ".jsx", ".kt",
            ".kts", ".lua", ".php", ".ps1", ".py", ".rb", ".rs", ".sh",
            ".swift", ".toml", ".ts", ".tsx", ".vue", ".yaml", ".yml",
        }
    ),
    "data": frozenset(
        {
            ".csv", ".db", ".json", ".jsonl", ".ndjson", ".parquet",
            ".sqlite", ".sqlite3", ".sql", ".tsv", ".xml",
        }
    ),
    "installer/executable": frozenset(
        {
            ".appimage", ".bin", ".com", ".deb", ".dmg", ".exe", ".iso",
            ".jar", ".msi", ".msix", ".pkg", ".rpm", ".scr",
        }
    ),
}
CATEGORY_ORDER = (
    "document",
    "image",
    "audio",
    "video",
    "archive",
    "code",
    "data",
    "installer/executable",
    "other",
    "no-extension",
)
AGE_BUCKET_ORDER = (
    "<30 days",
    "30–89",
    "90–179",
    "180–364",
    "365+",
    "future",
    "unknown",
)

RECORD_KEYS = {
    "scope": frozenset(
        {
            "schema_version",
            "record_type",
            "collector",
            "root_alias",
            "root_kind",
            "capacity_total_bytes",
            "capacity_free_bytes",
        }
    ),
    "entry": frozenset(
        {
            "schema_version",
            "record_type",
            "collector",
            "root_alias",
            "root_kind",
            "relative_path",
            "entry_type",
            "size_bytes",
            "modified_utc",
        }
    ),
    "warning": frozenset(
        {
            "schema_version",
            "record_type",
            "collector",
            "root_alias",
            "root_kind",
            "reason_code",
        }
    ),
    "completion": frozenset(
        {
            "schema_version",
            "record_type",
            "collector",
            "root_alias",
            "root_kind",
            "reason_code",
        }
    ),
}
UTC_TIMESTAMP_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,7})?Z\Z"
)


class StorageOrientationError(ValueError):
    """Raised when input cannot be trusted or a bounded collector must stop."""


class CollectorError(StorageOrientationError):
    def __init__(self, reason_code: str):
        if reason_code not in COLLECTOR_ERROR_CODES:
            raise ValueError("collector reason code is not bounded")
        super().__init__(reason_code)
        self.reason_code = reason_code


def _is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _bounded_string(value: Any, field: str, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise StorageOrientationError(f"{field} must be a bounded non-empty string")
    if value != value.strip() or any(ord(character) < 32 for character in value):
        raise StorageOrientationError(f"{field} contains unsupported whitespace")
    return value


def _parse_utc_timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    timestamp = _bounded_string(value, "modified_utc", maximum=40)
    if UTC_TIMESTAMP_PATTERN.fullmatch(timestamp) is None:
        raise StorageOrientationError("modified_utc must be UTC with a Z suffix")
    normalized = timestamp[:-1]
    if "." in normalized:
        prefix, fraction = normalized.rsplit(".", 1)
        normalized = prefix + "." + (fraction + "000000")[:6]
    try:
        parsed = datetime.fromisoformat(normalized + "+00:00")
    except ValueError as error:
        raise StorageOrientationError("modified_utc is invalid") from error
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise StorageOrientationError("modified_utc must be UTC")
    return parsed


def _validate_timestamp(value: Any) -> None:
    _parse_utc_timestamp(value)


def _validate_relative_path(value: Any) -> str:
    relative_path = _bounded_string(value, "relative_path", maximum=4096)
    path = PurePosixPath(relative_path)
    if (
        path.is_absolute()
        or str(path) != relative_path
        or any(part in {"", ".", ".."} for part in path.parts)
        or "\\" in relative_path
    ):
        raise StorageOrientationError("relative_path must be canonical and relative")
    if any(len(part) > 255 for part in path.parts):
        raise StorageOrientationError("relative_path component is too long")
    return relative_path


def validate_record(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise StorageOrientationError("record must be an object")
    if record.get("schema_version") != SCHEMA_VERSION:
        raise StorageOrientationError("unsupported or mixed schema_version")
    record_type = record.get("record_type")
    if record_type not in RECORD_KEYS:
        raise StorageOrientationError("record_type is unsupported")
    if frozenset(record) != RECORD_KEYS[record_type]:
        raise StorageOrientationError(f"{record_type} record fields are not exact")

    collector = _bounded_string(record["collector"], "collector")
    root_alias = _bounded_string(record["root_alias"], "root_alias")
    root_kind = _bounded_string(record["root_kind"], "root_kind")
    expected_kind = SCOPE_SPECS.get((collector, root_alias))
    if expected_kind is None or root_kind != expected_kind:
        raise StorageOrientationError("collector/root scope is not recognized")

    if record_type == "scope":
        total = record["capacity_total_bytes"]
        free = record["capacity_free_bytes"]
        if root_kind == "capacity":
            if not _is_integer(total) or not _is_integer(free):
                raise StorageOrientationError("capacity values must be integers")
            if total < 0 or free < 0 or free > total:
                raise StorageOrientationError("capacity values are invalid")
        elif total is not None or free is not None:
            raise StorageOrientationError("traversal scope must not contain capacity")
    elif record_type == "entry":
        if root_kind != "traversal":
            raise StorageOrientationError("entries require a traversal scope")
        _validate_relative_path(record["relative_path"])
        if record["entry_type"] not in {"file", "directory"}:
            raise StorageOrientationError("entry_type is unsupported")
        size = record["size_bytes"]
        if not _is_integer(size) or size < 0:
            raise StorageOrientationError("size_bytes must be a non-negative integer")
        if record["entry_type"] == "directory" and size != 0:
            raise StorageOrientationError("directory size_bytes must be zero")
        _validate_timestamp(record["modified_utc"])
    elif record_type == "warning":
        if root_kind != "traversal":
            raise StorageOrientationError("warnings require a traversal scope")
        if record["reason_code"] not in WARNING_REASON_CODES:
            raise StorageOrientationError("warning reason_code is unsupported")
    else:
        if root_kind != "traversal":
            raise StorageOrientationError("completion requires a traversal scope")
        if record["reason_code"] not in COMPLETION_REASON_CODES:
            raise StorageOrientationError("completion reason_code is unsupported")
    return record


def _strict_object(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StorageOrientationError("duplicate JSON object key")
        result[key] = value
    return result


def parse_jsonl(source: Iterable[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(source, start=1):
        if len(raw_line.encode("utf-8")) > MAX_JSON_LINE_BYTES:
            raise StorageOrientationError("JSON line exceeds the bounded size")
        line = raw_line.strip()
        if not line:
            raise StorageOrientationError("blank JSON line is not allowed")
        try:
            value = json.loads(
                line,
                object_pairs_hook=_strict_object,
                parse_constant=lambda value: (_ for _ in ()).throw(
                    StorageOrientationError("non-finite JSON value")
                ),
            )
        except (json.JSONDecodeError, UnicodeError) as error:
            raise StorageOrientationError(
                f"malformed JSON at line {line_number}"
            ) from error
        records.append(validate_record(value))
        if len(records) > MAX_RECORDS:
            raise StorageOrientationError("record stream exceeds the bounded count")
    if not records:
        raise StorageOrientationError("record stream is empty")
    validate_stream(records)
    return records


def validate_stream(records: Sequence[Mapping[str, Any]]) -> None:
    scopes: set[tuple[str, str]] = set()
    collectors: set[str] = set()
    collector_data_started: set[str] = set()
    collector_completed: set[str] = set()
    entry_counts: Counter[tuple[str, str]] = Counter()
    warning_counts: Counter[tuple[str, str]] = Counter()
    collector_record_counts: Counter[str] = Counter()
    entry_paths: set[tuple[str, str, str]] = set()

    for raw_record in records:
        record = validate_record(dict(raw_record))
        collector = record["collector"]
        alias = record["root_alias"]
        key = (collector, alias)
        record_type = record["record_type"]
        collectors.add(collector)
        collector_record_counts[collector] += 1
        if collector_record_counts[collector] > MAX_RECORDS_PER_COLLECTOR:
            raise StorageOrientationError("collector stream exceeds the bounded count")

        if collector in collector_completed:
            raise StorageOrientationError("record appears after collector completion")
        if record_type == "scope":
            if collector in collector_data_started:
                raise StorageOrientationError("scope record is out of order")
            if key in scopes:
                raise StorageOrientationError("duplicate scope record")
            scopes.add(key)
            continue

        collector_data_started.add(collector)
        if key not in scopes:
            raise StorageOrientationError("record appears before its scope")
        if record_type == "entry":
            relative_path = record["relative_path"]
            path_identity = (
                relative_path.casefold()
                if collector == "windows"
                else relative_path
            )
            entry_key = (collector, alias, path_identity)
            if entry_key in entry_paths:
                raise StorageOrientationError("duplicate logical entry path")
            entry_paths.add(entry_key)
            entry_counts[key] += 1
            if entry_counts[key] > MAX_ENTRIES:
                raise StorageOrientationError("entry scope exceeds the bounded count")
        elif record_type == "warning":
            warning_counts[key] += 1
            if warning_counts[key] > MAX_WARNING_RECORDS_PER_SCOPE:
                raise StorageOrientationError("warning scope exceeds the bounded count")
        elif record_type == "completion":
            expected_traversal = {
                candidate
                for candidate in scopes
                if candidate[0] == collector
                and SCOPE_SPECS[candidate] == "traversal"
            }
            if key not in expected_traversal:
                raise StorageOrientationError("completion scope is invalid")
            if record["reason_code"] == "complete" and warning_counts[key]:
                raise StorageOrientationError("complete stream contains warnings")
            collector_completed.add(collector)

    for collector in collectors:
        aliases = {alias for candidate, alias in scopes if candidate == collector}
        if aliases != COLLECTOR_ALIASES[collector]:
            raise StorageOrientationError("collector scope set is incomplete")
        if collector not in collector_completed:
            raise StorageOrientationError("collector stream is incomplete")


def _base_record(record_type: str, collector: str, alias: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": record_type,
        "collector": collector,
        "root_alias": alias,
        "root_kind": SCOPE_SPECS[(collector, alias)],
    }


def capacity_scope_record(
    collector: str, alias: str, total_bytes: int, free_bytes: int
) -> dict[str, Any]:
    record = _base_record("scope", collector, alias)
    record.update(
        {
            "capacity_total_bytes": total_bytes,
            "capacity_free_bytes": free_bytes,
        }
    )
    return validate_record(record)


def traversal_scope_record(collector: str, alias: str) -> dict[str, Any]:
    record = _base_record("scope", collector, alias)
    record.update(
        {"capacity_total_bytes": None, "capacity_free_bytes": None}
    )
    return validate_record(record)


def warning_record(collector: str, alias: str, reason_code: str) -> dict[str, Any]:
    record = _base_record("warning", collector, alias)
    record["reason_code"] = reason_code
    return validate_record(record)


def completion_record(
    collector: str, alias: str, reason_code: str
) -> dict[str, Any]:
    record = _base_record("completion", collector, alias)
    record["reason_code"] = reason_code
    return validate_record(record)


def is_protected_directory_name(name: str) -> bool:
    normalized = re.sub(r"[\s._-]+", " ", name.casefold()).strip()
    if name.casefold() in PROTECTED_DIRECTORY_NAMES:
        return True
    return any(pattern.fullmatch(normalized) for pattern in PROTECTED_DIRECTORY_PATTERNS)


def _without_backup_suffixes(name: str) -> str:
    normalized = name.casefold()
    while True:
        for suffix in BACKUP_SUFFIXES:
            if normalized.endswith(suffix) and len(normalized) > len(suffix):
                normalized = normalized[: -len(suffix)]
                break
        else:
            return normalized


def is_protected_file_name(name: str) -> bool:
    normalized = _without_backup_suffixes(name)
    if normalized in PROTECTED_FILE_NAMES:
        return True
    if normalized.startswith("id_"):
        return True
    return PurePosixPath(normalized).suffix in PROTECTED_FILE_SUFFIXES


def parse_linux_mount_points(source: Iterable[str]) -> frozenset[str]:
    mount_points: set[str] = set()
    for line_number, raw_line in enumerate(source, start=1):
        if line_number > MAX_MOUNTINFO_LINES:
            raise CollectorError("root_unavailable")
        if len(raw_line.encode("utf-8")) > MAX_JSON_LINE_BYTES:
            raise CollectorError("root_unavailable")
        fields = raw_line.rstrip("\n").split(" ")
        if len(fields) < 10 or "-" not in fields[6:]:
            raise CollectorError("root_unavailable")
        encoded_mount_point = fields[4]

        def replace_escape(match: re.Match[str]) -> str:
            return chr(int(match.group(1), 8))

        mount_point = re.sub(r"\\(040|011|012|134)", replace_escape, encoded_mount_point)
        if not mount_point.startswith("/") or "\x00" in mount_point:
            raise CollectorError("root_unavailable")
        mount_points.add(os.path.abspath(mount_point))
    if not mount_points:
        raise CollectorError("root_unavailable")
    return frozenset(mount_points)


def read_linux_mount_points() -> frozenset[str]:
    try:
        with Path("/proc/self/mountinfo").open(
            "r", encoding="utf-8", errors="strict"
        ) as source:
            return parse_linux_mount_points(source)
    except CollectorError:
        raise
    except (OSError, UnicodeError) as error:
        raise CollectorError("root_unavailable") from error


def validate_exact_local_root(root: Path, expected_root: Path) -> Path:
    root_text = os.path.abspath(os.fspath(root))
    expected_text = os.path.abspath(os.fspath(expected_root))
    if not root.is_absolute() or root_text != expected_text:
        raise CollectorError("root_not_allowlisted")
    if root_text.startswith("//"):
        raise CollectorError("root_not_local")
    normalized_root = Path(root_text)
    root_stat = None
    current = Path(normalized_root.anchor)
    try:
        for part in normalized_root.parts[1:]:
            current /= part
            root_stat = os.lstat(current)
            if stat.S_ISLNK(root_stat.st_mode):
                raise CollectorError("root_not_directory")
    except CollectorError:
        raise
    except OSError as error:
        raise CollectorError("root_unavailable") from error
    if root_stat is None:
        root_stat = os.lstat(root_text)
    if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):
        raise CollectorError("root_not_directory")
    if os.path.ismount(root_text):
        raise CollectorError("root_is_mount")
    return Path(root_text)


def require_non_elevated() -> None:
    if os.geteuid() == 0:
        raise CollectorError("elevated_execution_rejected")


def _warning_reason(error: OSError, *, enumeration: bool = False) -> str:
    if isinstance(error, PermissionError):
        return "access_denied"
    return "enumeration_failed" if enumeration else "metadata_unavailable"


def _utc_timestamp(timestamp: float) -> str | None:
    try:
        return (
            datetime.fromtimestamp(timestamp, tz=timezone.utc)
            .isoformat(timespec="microseconds")
            .replace("+00:00", "Z")
        )
    except (OverflowError, OSError, ValueError):
        return None


def collect_wsl_records() -> list[dict[str, Any]]:
    """Collect only the fixed production WSL scopes after all authority gates."""

    require_non_elevated()
    approved = validate_exact_local_root(WSL_TRAVERSAL_ROOT, WSL_TRAVERSAL_ROOT)
    root_text = os.fspath(approved)
    mount_points = read_linux_mount_points()
    if root_text in mount_points:
        raise CollectorError("root_is_mount")
    if os.path.abspath(os.fspath(WSL_CAPACITY_ROOT)) != "/":
        raise CollectorError("root_not_allowlisted")
    try:
        capacity = os.statvfs(os.fspath(WSL_CAPACITY_ROOT))
        fragment_size = capacity.f_frsize or capacity.f_bsize
        total_bytes = capacity.f_blocks * fragment_size
        free_bytes = capacity.f_bavail * fragment_size
    except (AttributeError, OSError, OverflowError) as error:
        raise CollectorError("capacity_unavailable") from error

    if MAX_DEPTH < 1 or MAX_ENTRIES < 1:
        raise ValueError("collector bounds must be positive")
    output: list[dict[str, Any]] = [
        capacity_scope_record("wsl", "wsl_root", total_bytes, free_bytes),
        traversal_scope_record("wsl", "wsl_src"),
    ]
    warning_count = 0
    inspected_count = 0
    exhausted = False
    incomplete = False

    def add_warning(reason_code: str) -> None:
        nonlocal warning_count, incomplete
        incomplete = True
        if warning_count < MAX_ENTRIES + 1:
            output.append(warning_record("wsl", "wsl_src", reason_code))
            warning_count += 1

    def contained_candidate(parts: tuple[str, ...], name: Any) -> tuple[str, str] | None:
        if (
            not isinstance(name, str)
            or not name
            or name in {".", ".."}
            or os.sep in name
            or (os.altsep is not None and os.altsep in name)
            or "\x00" in name
        ):
            return None
        relative = "/".join((*parts, name))
        candidate = os.path.abspath(os.path.join(root_text, *parts, name))
        try:
            if os.path.commonpath((root_text, candidate)) != root_text:
                return None
        except ValueError:
            return None
        return relative, candidate

    open_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    if hasattr(os, "O_CLOEXEC"):
        open_flags |= os.O_CLOEXEC

    def visit(directory_fd: int, parts: tuple[str, ...], depth: int) -> None:
        nonlocal inspected_count, exhausted
        if exhausted:
            return
        entries: list[Any] = []
        try:
            with os.scandir(directory_fd) as iterator:
                while not exhausted:
                    try:
                        candidate_entry = next(iterator)
                    except StopIteration:
                        break
                    inspected_count += 1
                    entries.append(candidate_entry)
                    if inspected_count >= MAX_ENTRIES:
                        add_warning("max_entries_reached")
                        exhausted = True
        except OSError as error:
            add_warning(_warning_reason(error, enumeration=True))

        entries.sort(key=lambda item: (item.name.casefold(), item.name))
        for candidate_entry in entries:
            candidate_identity = contained_candidate(parts, candidate_entry.name)
            if candidate_identity is None:
                add_warning("containment_rejected")
            else:
                relative, candidate = candidate_identity
                if candidate in mount_points:
                    add_warning("mount_point_skipped")
                elif is_protected_directory_name(candidate_entry.name):
                    add_warning("protected_directory_skipped")
                elif is_protected_file_name(candidate_entry.name):
                    add_warning("protected_file_skipped")
                else:
                    try:
                        metadata = candidate_entry.stat(follow_symlinks=False)
                    except OSError as error:
                        add_warning(_warning_reason(error))
                    else:
                        mode = metadata.st_mode
                        if stat.S_ISLNK(mode):
                            add_warning("symlink_skipped")
                        elif metadata.st_dev != starting_device:
                            add_warning("cross_device_skipped")
                        elif stat.S_ISDIR(mode):
                            modified = _utc_timestamp(metadata.st_mtime)
                            entry_record = _base_record("entry", "wsl", "wsl_src")
                            entry_record.update(
                                {
                                    "relative_path": relative,
                                    "entry_type": "directory",
                                    "size_bytes": 0,
                                    "modified_utc": modified,
                                }
                            )
                            output.append(validate_record(entry_record))
                            if modified is None:
                                add_warning("timestamp_unavailable")
                            child_depth = depth + 1
                            if child_depth >= MAX_DEPTH:
                                add_warning("max_depth_reached")
                            else:
                                child_fd: int | None = None
                                try:
                                    child_fd = os.open(
                                        candidate_entry.name,
                                        open_flags,
                                        dir_fd=directory_fd,
                                    )
                                    opened = os.fstat(child_fd)
                                    if (
                                        not stat.S_ISDIR(opened.st_mode)
                                        or opened.st_dev != metadata.st_dev
                                        or opened.st_ino != metadata.st_ino
                                    ):
                                        add_warning("metadata_unavailable")
                                    elif opened.st_dev != starting_device:
                                        add_warning("cross_device_skipped")
                                    else:
                                        visit(child_fd, (*parts, candidate_entry.name), child_depth)
                                except OSError as error:
                                    add_warning(_warning_reason(error))
                                finally:
                                    if child_fd is not None:
                                        os.close(child_fd)
                        elif stat.S_ISREG(mode):
                            modified = _utc_timestamp(metadata.st_mtime)
                            entry_record = _base_record("entry", "wsl", "wsl_src")
                            entry_record.update(
                                {
                                    "relative_path": relative,
                                    "entry_type": "file",
                                    "size_bytes": metadata.st_size,
                                    "modified_utc": modified,
                                }
                            )
                            output.append(validate_record(entry_record))
                            if modified is None:
                                add_warning("timestamp_unavailable")
                        else:
                            add_warning("unsupported_entry_type")

    root_fd: int | None = None
    try:
        root_fd = os.open(root_text, open_flags)
        root_metadata = os.fstat(root_fd)
        if not stat.S_ISDIR(root_metadata.st_mode):
            raise CollectorError("root_not_directory")
        starting_device = root_metadata.st_dev
        visit(root_fd, (), 0)
    except CollectorError:
        raise
    except OSError as error:
        raise CollectorError("root_unavailable") from error
    finally:
        if root_fd is not None:
            os.close(root_fd)

    output.append(
        completion_record(
            "wsl",
            "wsl_src",
            "incomplete" if incomplete else "complete",
        )
    )
    validate_stream(output)
    return output


def serialize_jsonl(records: Iterable[Mapping[str, Any]]) -> str:
    validated = [validate_record(dict(record)) for record in records]
    if len(validated) > MAX_RECORDS:
        raise StorageOrientationError("record stream exceeds the bounded count")
    validate_stream(validated)
    return "\n".join(
        json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        for record in validated
    ) + "\n"


def extension_category(relative_path: str) -> str:
    suffix = PurePosixPath(relative_path).suffix.casefold()
    if not suffix:
        return "no-extension"
    for category in CATEGORY_ORDER:
        if suffix in CATEGORY_EXTENSIONS.get(category, frozenset()):
            return category
    return "other"


def parse_utc_timestamp(value: str | None) -> datetime | None:
    return _parse_utc_timestamp(value)


def _utc_100ns_ticks(value: str) -> int:
    _parse_utc_timestamp(value)
    timestamp = value[:-1]
    if "." in timestamp:
        whole, fraction = timestamp.rsplit(".", 1)
    else:
        whole, fraction = timestamp, ""
    parsed_whole = datetime.strptime(whole, "%Y-%m-%dT%H:%M:%S").replace(
        tzinfo=timezone.utc
    )
    epoch = datetime(1, 1, 1, tzinfo=timezone.utc)
    delta = parsed_whole - epoch
    whole_ticks = (delta.days * 86_400 + delta.seconds) * 10_000_000
    return whole_ticks + int((fraction + "0000000")[:7])


def _datetime_100ns_ticks(value: datetime) -> int:
    epoch = datetime(1, 1, 1, tzinfo=timezone.utc)
    delta = value - epoch
    return (
        (delta.days * 86_400 + delta.seconds) * 10_000_000
        + delta.microseconds * 10
    )


def age_bucket(modified_utc: str | None, as_of: datetime) -> str:
    if modified_utc is None:
        return "unknown"
    if as_of.tzinfo is None or as_of.utcoffset() != timezone.utc.utcoffset(as_of):
        raise StorageOrientationError("as_of must be timezone-aware UTC")
    age_ticks = _datetime_100ns_ticks(as_of) - _utc_100ns_ticks(modified_utc)
    if age_ticks < 0:
        return "future"
    ticks_per_day = 86_400 * 10_000_000
    if age_ticks < 30 * ticks_per_day:
        return "<30 days"
    if age_ticks < 90 * ticks_per_day:
        return "30–89"
    if age_ticks < 180 * ticks_per_day:
        return "90–179"
    if age_ticks < 365 * ticks_per_day:
        return "180–364"
    return "365+"


def _file_identity_key(record: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        record["collector"],
        record["root_alias"],
        record["relative_path"].casefold(),
        record["relative_path"],
        record["size_bytes"],
        record["modified_utc"] or "",
    )


def analyze_records(
    records: Sequence[Mapping[str, Any]], *, as_of: datetime
) -> dict[str, Any]:
    validated = [validate_record(dict(record)) for record in records]
    validate_stream(validated)
    scopes = [record for record in validated if record["record_type"] == "scope"]
    entries = [record for record in validated if record["record_type"] == "entry"]
    warnings = [record for record in validated if record["record_type"] == "warning"]
    completions = [
        record for record in validated if record["record_type"] == "completion"
    ]
    files = [record for record in entries if record["entry_type"] == "file"]
    directories = [
        record for record in entries if record["entry_type"] == "directory"
    ]

    candidate_ids = {
        id(record): f"FILE-{index:06d}"
        for index, record in enumerate(sorted(files, key=_file_identity_key), start=1)
    }
    enriched_files: list[dict[str, Any]] = []
    for record in files:
        enriched_files.append(
            {
                **record,
                "candidate_id": candidate_ids[id(record)],
                "category": extension_category(record["relative_path"]),
                "age_bucket": age_bucket(record["modified_utc"], as_of),
            }
        )

    categories = {
        category: {"file_count": 0, "size_bytes": 0}
        for category in CATEGORY_ORDER
    }
    ages = {
        bucket: {"file_count": 0, "size_bytes": 0}
        for bucket in AGE_BUCKET_ORDER
    }
    for record in enriched_files:
        categories[record["category"]]["file_count"] += 1
        categories[record["category"]]["size_bytes"] += record["size_bytes"]
        ages[record["age_bucket"]]["file_count"] += 1
        ages[record["age_bucket"]]["size_bytes"] += record["size_bytes"]

    largest = sorted(
        enriched_files,
        key=lambda record: (-record["size_bytes"],) + _file_identity_key(record),
    )[:20]

    duplicate_members: defaultdict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for record in enriched_files:
        normalized_name = unicodedata.normalize(
            "NFKC", PurePosixPath(record["relative_path"]).name
        ).casefold()
        duplicate_members[(record["size_bytes"], normalized_name)].append(record)
    candidate_groups = [
        (signature, sorted(members, key=_file_identity_key))
        for signature, members in duplicate_members.items()
        if len(members) > 1
    ]
    candidate_groups.sort(
        key=lambda item: (-item[0][0], item[0][1], tuple(_file_identity_key(member) for member in item[1]))
    )
    duplicates = [
        {
            "group_id": f"DUP-{index:04d}",
            "size_bytes": signature[0],
            "members": members,
        }
        for index, (signature, members) in enumerate(candidate_groups, start=1)
    ]

    root_totals: dict[str, dict[str, int]] = {}
    traversal_aliases = {
        scope["root_alias"]
        for scope in scopes
        if scope["root_kind"] == "traversal"
    }
    for alias in sorted(traversal_aliases):
        root_entries = [entry for entry in entries if entry["root_alias"] == alias]
        root_totals[alias] = {
            "file_count": sum(entry["entry_type"] == "file" for entry in root_entries),
            "directory_count": sum(
                entry["entry_type"] == "directory" for entry in root_entries
            ),
            "file_size_bytes": sum(
                entry["size_bytes"]
                for entry in root_entries
                if entry["entry_type"] == "file"
            ),
        }

    reason_counts = Counter(record["reason_code"] for record in warnings)
    return {
        "schema_version": SCHEMA_VERSION,
        "scopes": scopes,
        "completions": completions,
        "totals": {
            "file_count": len(files),
            "directory_count": len(directories),
            "file_size_bytes": sum(record["size_bytes"] for record in files),
            "skipped_or_error_count": len(warnings),
            "incomplete_scope_count": sum(
                record["reason_code"] == "incomplete" for record in completions
            ),
        },
        "root_totals": root_totals,
        "categories": categories,
        "ages": ages,
        "largest": largest,
        "duplicates": duplicates,
        "reason_counts": dict(sorted(reason_counts.items())),
    }


def _summary_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise StorageOrientationError(f"{field} must be an object")
    return value


def _summary_sequence(value: Any, field: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise StorageOrientationError(f"{field} must be an array")
    return value


def _summary_count(value: Any, field: str) -> int:
    if not _is_integer(value) or value < 0:
        raise StorageOrientationError(f"{field} must be a non-negative integer")
    return value


def _summary_identifier(value: Any, field: str, pattern: str) -> str:
    identifier = _bounded_string(value, field, maximum=32)
    if re.fullmatch(pattern, identifier) is None:
        raise StorageOrientationError(f"{field} is invalid")
    return identifier


def sanitized_summary(analysis: Mapping[str, Any]) -> dict[str, Any]:
    """Construct the public-safe schema field by field; no input object is spread."""

    source = _summary_mapping(analysis, "analysis")
    totals_source = _summary_mapping(source.get("totals"), "totals")
    totals = {
        "file_count": _summary_count(totals_source.get("file_count"), "file_count"),
        "directory_count": _summary_count(
            totals_source.get("directory_count"), "directory_count"
        ),
        "file_size_bytes": _summary_count(
            totals_source.get("file_size_bytes"), "file_size_bytes"
        ),
        "skipped_or_error_count": _summary_count(
            totals_source.get("skipped_or_error_count"),
            "skipped_or_error_count",
        ),
        "incomplete_scope_count": _summary_count(
            totals_source.get("incomplete_scope_count"),
            "incomplete_scope_count",
        ),
    }

    roots: list[dict[str, Any]] = []
    capacity: list[dict[str, Any]] = []
    seen_aliases: set[str] = set()
    known_alias_kinds = {
        alias: root_kind for (_, alias), root_kind in SCOPE_SPECS.items()
    }
    for raw_scope in _summary_sequence(source.get("scopes"), "scopes"):
        scope = _summary_mapping(raw_scope, "scope")
        alias = _bounded_string(scope.get("root_alias"), "root_alias")
        root_kind = _bounded_string(scope.get("root_kind"), "root_kind")
        if known_alias_kinds.get(alias) != root_kind or alias in seen_aliases:
            raise StorageOrientationError("sanitized scope is invalid")
        seen_aliases.add(alias)
        roots.append({"root_alias": alias, "root_kind": root_kind})
        if root_kind == "capacity":
            total_bytes = _summary_count(
                scope.get("capacity_total_bytes"), "capacity_total_bytes"
            )
            free_bytes = _summary_count(
                scope.get("capacity_free_bytes"), "capacity_free_bytes"
            )
            if free_bytes > total_bytes:
                raise StorageOrientationError("sanitized capacity is invalid")
            capacity.append(
                {
                    "root_alias": alias,
                    "total_bytes": total_bytes,
                    "free_bytes": free_bytes,
                }
            )
    roots.sort(key=lambda value: value["root_alias"])
    capacity.sort(key=lambda value: value["root_alias"])

    categories_source = _summary_mapping(source.get("categories"), "categories")
    categories: list[dict[str, Any]] = []
    for category in CATEGORY_ORDER:
        values = _summary_mapping(categories_source.get(category), "category")
        categories.append(
            {
                "category": category,
                "file_count": _summary_count(values.get("file_count"), "file_count"),
                "size_bytes": _summary_count(values.get("size_bytes"), "size_bytes"),
            }
        )

    ages_source = _summary_mapping(source.get("ages"), "ages")
    age_buckets: list[dict[str, Any]] = []
    for bucket in AGE_BUCKET_ORDER:
        values = _summary_mapping(ages_source.get(bucket), "age_bucket")
        age_buckets.append(
            {
                "age_bucket": bucket,
                "file_count": _summary_count(values.get("file_count"), "file_count"),
                "size_bytes": _summary_count(values.get("size_bytes"), "size_bytes"),
            }
        )

    largest_file_candidates: list[dict[str, Any]] = []
    for raw_record in _summary_sequence(source.get("largest"), "largest"):
        record = _summary_mapping(raw_record, "largest candidate")
        candidate_id = _summary_identifier(
            record.get("candidate_id"), "candidate_id", r"FILE-\d{6}"
        )
        category = _bounded_string(record.get("category"), "category")
        age_value = _bounded_string(record.get("age_bucket"), "age_bucket")
        if category not in CATEGORY_ORDER or age_value not in AGE_BUCKET_ORDER:
            raise StorageOrientationError("sanitized candidate classification is invalid")
        largest_file_candidates.append(
            {
                "candidate_id": candidate_id,
                "category": category,
                "size_bytes": _summary_count(record.get("size_bytes"), "size_bytes"),
                "age_bucket": age_value,
            }
        )

    duplicate_candidate_groups: list[dict[str, Any]] = []
    for raw_group in _summary_sequence(source.get("duplicates"), "duplicates"):
        group = _summary_mapping(raw_group, "duplicate group")
        candidate_ids: list[str] = []
        for raw_member in _summary_sequence(group.get("members"), "duplicate members"):
            member = _summary_mapping(raw_member, "duplicate member")
            candidate_ids.append(
                _summary_identifier(
                    member.get("candidate_id"), "candidate_id", r"FILE-\d{6}"
                )
            )
        duplicate_candidate_groups.append(
            {
                "group_id": _summary_identifier(
                    group.get("group_id"), "group_id", r"DUP-\d{4}"
                ),
                "size_bytes": _summary_count(group.get("size_bytes"), "size_bytes"),
                "candidate_ids": candidate_ids,
            }
        )

    reason_counts_source = _summary_mapping(
        source.get("reason_counts"), "reason_counts"
    )
    limitations = {
        "candidate_id_ordering_metadata_derived",
        "concurrent_namespace_mutation_not_race_proof",
        "duplicate_candidates_only",
        "metadata_only",
        "no_hashing",
    }
    for reason, raw_count in reason_counts_source.items():
        if reason not in WARNING_REASON_CODES:
            raise StorageOrientationError("sanitized limitation is invalid")
        _summary_count(raw_count, "reason count")
        limitations.add(reason)
    if totals["incomplete_scope_count"]:
        limitations.add("incomplete_collection")

    return {
        "schema_version": SCHEMA_VERSION,
        "summary_kind": "storage_orientation_sanitized",
        "roots": roots,
        "capacity": capacity,
        "totals": totals,
        "categories": categories,
        "age_buckets": age_buckets,
        "largest_file_candidates": largest_file_candidates,
        "duplicate_candidate_groups": duplicate_candidate_groups,
        "limitations": sorted(limitations),
    }


def _format_bytes(value: int) -> str:
    return f"{value:,} B ({value / (1024 ** 3):.2f} GiB)"


def _cell(value: str) -> str:
    rendered: list[str] = []
    for character in value:
        category = unicodedata.category(character)
        if category in {"Cc", "Cf", "Cs", "Zl", "Zp"}:
            rendered.append(f"U+{ord(character):04X}")
        elif character.isascii() and (character.isalnum() or character in {" ", "/"}):
            rendered.append(character)
        else:
            rendered.append(f"&#{ord(character)};")
    return "".join(rendered)


def render_markdown(analysis: Mapping[str, Any]) -> str:
    lines = [
        "# Storage Orientation Snapshot",
        "",
        "Metadata-only local owner report. Traversed subject-file contents were not read and no hashing was performed; collectors may read operating-system mount metadata solely to enforce traversal boundaries.",
        "",
        "## Exact Local Scope",
        "",
    ]
    for scope in sorted(analysis["scopes"], key=lambda value: value["root_alias"]):
        lines.append(f"- `{scope['root_alias']}`: {_cell(LOCAL_SCOPE_LABELS[scope['root_alias']])}")

    lines.extend(["", "## Completeness and Limitations", ""])
    totals = analysis["totals"]
    lines.append(
        f"- Traversal scopes incomplete: {totals['incomplete_scope_count']}"
    )
    lines.append(
        f"- Skipped/inaccessible/error observations: {totals['skipped_or_error_count']}"
    )
    lines.append("- Duplicate groups are candidates based only on exact size and normalized case-insensitive filename/extension.")
    lines.append("- Candidate IDs are report-local deterministic ordinals assigned using metadata/path ordering; they are cross-references, not stable identities, and their order can reflect source ordering.")
    lines.append("- Existing symlinks, reparse points, mount points, cross-device entries, protected directories, and bounded-limit overflows are not traversed.")
    lines.append("- Concurrent namespace or mount mutation is outside the one-owner one-shot operating model; pathname-based Windows checks and mount-table timing are not claimed to be adversarially race-proof.")
    if analysis["reason_counts"]:
        for reason, count in analysis["reason_counts"].items():
            lines.append(f"- `{reason}`: {count}")
    else:
        lines.append("- Bounded reason codes: none")

    lines.extend(["", "## Capacity", "", "| Scope | Total | Free |", "|---|---:|---:|"])
    for scope in sorted(analysis["scopes"], key=lambda value: value["root_alias"]):
        if scope["root_kind"] == "capacity":
            lines.append(
                f"| `{scope['root_alias']}` | {_format_bytes(scope['capacity_total_bytes'])} | {_format_bytes(scope['capacity_free_bytes'])} |"
            )

    lines.extend(["", "## Totals", "", "| Scope | Files | Directories | File bytes |", "|---|---:|---:|---:|"])
    for alias, values in sorted(analysis["root_totals"].items()):
        lines.append(
            f"| `{alias}` | {values['file_count']} | {values['directory_count']} | {values['file_size_bytes']:,} |"
        )
    lines.append(
        f"| **All traversal scopes** | **{totals['file_count']}** | **{totals['directory_count']}** | **{totals['file_size_bytes']:,}** |"
    )

    lines.extend(["", "## Category Distribution", "", "| Category | Files | Bytes |", "|---|---:|---:|"])
    for category in CATEGORY_ORDER:
        values = analysis["categories"][category]
        lines.append(f"| {category} | {values['file_count']} | {values['size_bytes']:,} |")

    lines.extend(["", "## Age Distribution", "", "| Age bucket | Files | Bytes |", "|---|---:|---:|"])
    for bucket in AGE_BUCKET_ORDER:
        values = analysis["ages"][bucket]
        lines.append(f"| {bucket} | {values['file_count']} | {values['size_bytes']:,} |")

    lines.extend(["", "## Top 20 Largest Files", "", "| ID | Scope | Relative path | Category | Age | Bytes |", "|---|---|---|---|---|---:|"])
    if analysis["largest"]:
        for record in analysis["largest"]:
            lines.append(
                f"| `{record['candidate_id']}` | `{record['root_alias']}` | {_cell(record['relative_path'])} | {record['category']} | {record['age_bucket']} | {record['size_bytes']:,} |"
            )
    else:
        lines.append("| — | — | None | — | — | 0 |")

    lines.extend(["", "## Duplicate Candidates", ""])
    if analysis["duplicates"]:
        for group in analysis["duplicates"]:
            lines.append(
                f"- `{group['group_id']}` — {group['size_bytes']:,} bytes each"
            )
            for member in group["members"]:
                lines.append(
                    f"  - `{member['candidate_id']}` / `{member['root_alias']}` / {_cell(member['relative_path'])}"
                )
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"


def parse_as_of(value: str) -> datetime:
    try:
        if len(value) == 10:
            parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
            return datetime.combine(parsed_date, time.max, tzinfo=timezone.utc)
        if not value.endswith("Z"):
            raise ValueError
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "as-of must be YYYY-MM-DD or an RFC3339 UTC timestamp ending in Z"
        ) from error
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise argparse.ArgumentTypeError("as-of must be UTC")
    return parsed


def _load_and_analyze(stdin: TextIO, as_of: datetime) -> dict[str, Any]:
    return analyze_records(parse_jsonl(stdin), as_of=as_of)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("collect-wsl", help="emit fixed-scope WSL metadata JSONL")
    for name, help_text in (
        ("report", "render a local owner Markdown report from JSONL stdin"),
        ("sanitize", "render a sanitized JSON derivative from JSONL stdin"),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--as-of", required=True, type=parse_as_of)
    arguments = parser.parse_args(argv)

    try:
        if arguments.command == "collect-wsl":
            sys.stdout.write(serialize_jsonl(collect_wsl_records()))
        elif arguments.command == "report":
            sys.stdout.write(render_markdown(_load_and_analyze(sys.stdin, arguments.as_of)))
        else:
            summary = sanitized_summary(
                _load_and_analyze(sys.stdin, arguments.as_of)
            )
            sys.stdout.write(
                json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n"
            )
    except CollectorError as error:
        print(f"storage_orientation_error:{error.reason_code}", file=sys.stderr)
        return 2
    except StorageOrientationError:
        print("storage_orientation_error:invalid_input", file=sys.stderr)
        return 2
    except Exception:
        print("storage_orientation_error:invalid_environment", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
