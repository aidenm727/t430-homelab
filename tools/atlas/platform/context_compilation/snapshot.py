"""Read-only immutable Git snapshot boundary for Checkpoint B1a."""

from __future__ import annotations

import os
import pathlib
import re
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Callable, TypeVar

from atlas.platform.context_compilation.digests import snapshot_fingerprint
from atlas.platform.context_compilation.models import (
    ImmutableBlob,
    ProtectedReferenceIdentity,
    RepositoryIdentityEvidence,
    RepositorySnapshot,
)


SNAPSHOT_MODE = "clean_committed"

# Post-rename R1 boundary: requests use the canonical current identity. The
# prior slug remains accepted only as an explicit legacy origin locator.
_CANONICAL_REPOSITORY_IDENTITY = "github.com/aidenm727/aiden-platform"
_CURRENT_ORIGIN_LOCATORS = frozenset(
    (
        "git@github.com:aidenm727/aiden-platform.git",
        "ssh://git@github.com/aidenm727/aiden-platform.git",
        "https://github.com/aidenm727/aiden-platform.git",
        "https://github.com/aidenm727/aiden-platform",
    )
)
_LEGACY_ORIGIN_LOCATORS = frozenset(
    (
        "git@github.com:aidenm727/t430-homelab.git",
        "ssh://git@github.com/aidenm727/t430-homelab.git",
        "https://github.com/aidenm727/t430-homelab.git",
        "https://github.com/aidenm727/t430-homelab",
    )
)
_SUPPORTED_ORIGIN_LOCATORS = _CURRENT_ORIGIN_LOCATORS | _LEGACY_ORIGIN_LOCATORS
_SHA1_PATTERN = re.compile(r"[0-9a-f]{40}\Z")
_FORBIDDEN_GIT_ENVIRONMENT = frozenset(
    (
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_COMMON_DIR",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_CONFIG",
        "GIT_CONFIG_COUNT",
        "GIT_CONFIG_SYSTEM",
        "GIT_CONFIG_GLOBAL",
        "GIT_CONFIG_NOSYSTEM",
        "GIT_NAMESPACE",
        "GIT_SHALLOW_FILE",
        "GIT_QUARANTINE_PATH",
    )
)
_PRESERVED_PROCESS_ENVIRONMENT = (
    "PATH",
    "PATHEXT",
    "SYSTEMROOT",
    "WINDIR",
    "TMPDIR",
    "TMP",
    "TEMP",
)
_GIT_COMMAND_PREFIX = (
    "git",
    "--no-replace-objects",
    "-c",
    "core.fsmonitor=false",
    "-c",
    "core.untrackedCache=false",
    "-c",
    f"core.hooksPath={os.devnull}",
)
_FORBIDDEN_LOCAL_CONFIG_KEYS = frozenset(
    (
        "core.fsmonitor",
        "core.hookspath",
        "core.worktree",
        "core.untrackedcache",
        "extensions.worktreeconfig",
        "status.submodulesummary",
        "submodule.recurse",
        "diff.external",
    )
)
_FORBIDDEN_REF_CHARACTERS = frozenset(" ~^:?*[\\")


class SnapshotError(RuntimeError):
    """Base class for immutable snapshot failures."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.primary_message = message
        self.post_state_error: SnapshotError | None = None

    def __str__(self) -> str:
        if self.post_state_error is None:
            return self.primary_message
        return (
            f"{self.primary_message}; post-operation clean-state check also failed: "
            f"{self.post_state_error.primary_message}"
        )


class SnapshotEnvironmentError(SnapshotError):
    """The explicit target or process environment is unsafe."""


class RepositoryStateError(SnapshotError):
    """The repository state is outside the clean committed boundary."""


class RepositoryIdentityError(SnapshotError):
    """The local origin does not prove the requested repository identity."""


class RevisionError(SnapshotError):
    """The requested revision is not one exact local commit."""


class ObjectFormatError(SnapshotError):
    """The repository object format is unsupported."""


class TreeMismatchError(SnapshotError):
    """The requested commit root tree does not match the expected tree."""


class ProtectedReferenceError(SnapshotError):
    """A protected reference contract or direct identity is invalid."""

    def __init__(
        self,
        message: str,
        identity: ProtectedReferenceIdentity | None = None,
    ) -> None:
        super().__init__(message)
        self.identity = identity


class RepositoryPathError(SnapshotError):
    """A repository path is not an exact safe repository-relative path."""


class BlobLookupError(SnapshotError):
    """An exact immutable regular blob could not be read."""


@dataclass(frozen=True)
class _RepositoryBoundary:
    target: pathlib.Path
    git_dir: pathlib.Path
    common_dir: pathlib.Path
    object_dir: pathlib.Path


_T = TypeVar("_T")


def _validate_ambient_environment() -> None:
    for name in os.environ:
        if (
            name in _FORBIDDEN_GIT_ENVIRONMENT
            or name.startswith("GIT_CONFIG_KEY_")
            or name.startswith("GIT_CONFIG_VALUE_")
        ):
            raise SnapshotEnvironmentError("ambient Git control state is forbidden")


def _git_environment() -> dict[str, str]:
    environment = {
        name: os.environ[name]
        for name in _PRESERVED_PROCESS_ENVIRONMENT
        if name in os.environ
    }
    environment.update(
        {
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_NO_LAZY_FETCH": "1",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_LITERAL_PATHSPECS": "1",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "LC_ALL": "C",
            "LANG": "C",
        }
    )
    return environment


def _run_git(
    repository: pathlib.Path, *arguments: str
) -> subprocess.CompletedProcess[bytes]:
    """Execute every production Git command through one sanitized boundary."""

    _validate_ambient_environment()
    try:
        return subprocess.run(
            [*_GIT_COMMAND_PREFIX, "-C", str(repository), *arguments],
            cwd=repository,
            env=_git_environment(),
            capture_output=True,
            text=False,
            shell=False,
            check=False,
        )
    except OSError as error:
        raise SnapshotEnvironmentError("Git could not be executed") from error


def _require_git(
    repository: pathlib.Path,
    family: str,
    *arguments: str,
) -> bytes:
    result = _run_git(repository, family, *arguments)
    if result.returncode != 0:
        raise SnapshotEnvironmentError(
            f"Git {family} failed with return code {result.returncode}"
        )
    return result.stdout


def _decode_metadata_path(value: bytes) -> pathlib.Path:
    try:
        decoded = value.rstrip(b"\n").decode("utf-8")
    except UnicodeDecodeError as error:
        raise SnapshotEnvironmentError("repository metadata path is malformed") from error
    if not decoded or "\n" in decoded or "\r" in decoded:
        raise SnapshotEnvironmentError("repository metadata path is malformed")
    return pathlib.Path(decoded).resolve()


def _resolve_target(target_repository: str | pathlib.Path) -> pathlib.Path:
    if not isinstance(target_repository, (str, pathlib.Path)):
        raise SnapshotEnvironmentError("target repository must be an explicit path")
    try:
        if isinstance(target_repository, str) and not target_repository:
            raise SnapshotEnvironmentError("target repository path must not be empty")
        target = pathlib.Path(target_repository).resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise SnapshotEnvironmentError("target repository directory is unavailable") from error
    if not target.is_dir():
        raise SnapshotEnvironmentError("target repository must be an existing directory")
    return target


def _local_config_key_is_forbidden(name: str) -> bool:
    normalized = name.casefold()
    if normalized in _FORBIDDEN_LOCAL_CONFIG_KEYS:
        return True
    if normalized.startswith(("include.", "includeif.")):
        return True
    if re.fullmatch(r"diff\..+\.(?:command|textconv)", normalized):
        return True
    return re.fullmatch(
        r"filter\..+\.(?:clean|smudge|process|required)", normalized
    ) is not None


def _reject_local_configuration(target: pathlib.Path) -> None:
    result = _run_git(
        target,
        "config",
        "--local",
        "--no-includes",
        "--null",
        "--name-only",
        "--list",
    )
    if result.returncode != 0:
        raise SnapshotEnvironmentError(
            f"Git config failed with return code {result.returncode}"
        )
    names = result.stdout.split(b"\0")
    if names and names[-1] == b"":
        names.pop()
    try:
        decoded_names = (name.decode("utf-8") for name in names)
        if any(_local_config_key_is_forbidden(name) for name in decoded_names):
            raise RepositoryStateError("repository-local configuration is unsafe")
    except UnicodeDecodeError as error:
        raise RepositoryStateError(
            "repository-local configuration is unsafe"
        ) from error


def _repository_boundary(
    target_repository: str | pathlib.Path,
) -> _RepositoryBoundary:
    _validate_ambient_environment()
    target = _resolve_target(target_repository)
    _reject_local_configuration(target)
    inside = _require_git(target, "rev-parse", "--is-inside-work-tree").strip()
    bare = _require_git(target, "rev-parse", "--is-bare-repository").strip()
    if inside != b"true" or bare != b"false":
        raise RepositoryStateError(
            "target must be a non-bare working-tree repository"
        )

    git_dir = _decode_metadata_path(
        _require_git(target, "rev-parse", "--path-format=absolute", "--git-dir")
    )
    common_dir = _decode_metadata_path(
        _require_git(
            target, "rev-parse", "--path-format=absolute", "--git-common-dir"
        )
    )
    object_dir = _decode_metadata_path(
        _require_git(
            target,
            "rev-parse",
            "--path-format=absolute",
            "--git-path",
            "objects",
        )
    )
    if not git_dir.is_dir() or not common_dir.is_dir() or not object_dir.is_dir():
        raise SnapshotEnvironmentError("repository metadata is unavailable")
    if object_dir != (common_dir / "objects").resolve():
        raise RepositoryStateError("repository object store is outside the common directory")

    boundary = _RepositoryBoundary(target, git_dir, common_dir, object_dir)
    _reject_repository_metadata(boundary)
    return boundary


def _metadata_exists(path: pathlib.Path) -> bool:
    return os.path.lexists(path)


def _reject_repository_metadata(boundary: _RepositoryBoundary) -> None:
    replacements = _require_git(
        boundary.target,
        "for-each-ref",
        "--format=%(refname)",
        "refs/replace/",
    )
    if replacements:
        raise RepositoryStateError("replacement references are forbidden")
    forbidden = (
        boundary.common_dir / "info" / "grafts",
        boundary.object_dir / "info" / "alternates",
        boundary.object_dir / "info" / "http-alternates",
    )
    if any(_metadata_exists(path) for path in forbidden):
        raise RepositoryStateError("alternate or graft repository metadata is forbidden")


def _check_clean(boundary: _RepositoryBoundary) -> None:
    result = _run_git(
        boundary.target,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
        "--ignore-submodules=none",
    )
    if result.returncode != 0:
        raise RepositoryStateError(
            f"Git status failed with return code {result.returncode}"
        )
    if result.stdout:
        raise RepositoryStateError("target repository is not clean")


def _within_clean_boundary(
    boundary: _RepositoryBoundary, operation: Callable[[], _T]
) -> _T:
    primary: Exception | None = None
    try:
        _check_clean(boundary)
        return operation()
    except Exception as error:
        primary = error
        raise
    finally:
        try:
            _check_clean(boundary)
        except SnapshotError as post_error:
            if primary is None:
                raise
            if isinstance(primary, SnapshotError):
                primary.post_state_error = post_error
            else:
                raise post_error from primary


def _repository_identity(
    boundary: _RepositoryBoundary, requested_identity: str
) -> RepositoryIdentityEvidence:
    if requested_identity != _CANONICAL_REPOSITORY_IDENTITY:
        raise RepositoryIdentityError("requested repository identity is unsupported")
    result = _run_git(
        boundary.target,
        "config",
        "--local",
        "--no-includes",
        "--null",
        "--get-all",
        "remote.origin.url",
    )
    if result.returncode == 1:
        raise RepositoryIdentityError("origin URL is absent")
    if result.returncode != 0:
        raise RepositoryIdentityError(
            f"Git config failed with return code {result.returncode}"
        )
    values = result.stdout.split(b"\0")
    if values and values[-1] == b"":
        values.pop()
    if not values:
        raise RepositoryIdentityError("origin URL is absent")

    ordered_urls: list[str] = []
    seen: set[str] = set()
    for raw_url in values:
        try:
            url = raw_url.decode("utf-8")
        except UnicodeDecodeError as error:
            raise RepositoryIdentityError("origin URL is unsupported") from error
        if not url:
            raise RepositoryIdentityError("origin URL is empty")
        if url not in _SUPPORTED_ORIGIN_LOCATORS:
            raise RepositoryIdentityError("origin URL is unsupported")
        if url not in seen:
            seen.add(url)
            ordered_urls.append(url)
    return RepositoryIdentityEvidence(
        requested_identity=requested_identity,
        origin_urls=tuple(ordered_urls),
        normalized_identity=_CANONICAL_REPOSITORY_IDENTITY,
    )


def _object_format(boundary: _RepositoryBoundary) -> str:
    value = _require_git(
        boundary.target, "rev-parse", "--show-object-format"
    ).strip()
    if value != b"sha1":
        raise ObjectFormatError("repository object format must be sha1")
    return "sha1"


def _require_sha1(value: object, *, tree: bool = False) -> str:
    if not isinstance(value, str) or _SHA1_PATTERN.fullmatch(value) is None:
        if tree:
            raise TreeMismatchError("expected tree must be an exact lowercase SHA-1")
        raise RevisionError("requested revision must be an exact lowercase SHA-1")
    return value


def _resolve_commit_and_tree(
    boundary: _RepositoryBoundary,
    requested_revision: str,
    expected_tree: str,
) -> tuple[str, str]:
    result = _run_git(boundary.target, "cat-file", "-t", requested_revision)
    if result.returncode != 0 or result.stdout.strip() != b"commit":
        raise RevisionError("requested revision is not an available commit")
    resolved = _require_git(
        boundary.target,
        "rev-parse",
        "--verify",
        "--end-of-options",
        requested_revision,
    ).strip()
    if resolved != requested_revision.encode("ascii"):
        raise RevisionError("resolved commit does not match requested revision")
    tree = _require_git(
        boundary.target,
        "rev-parse",
        "--verify",
        "--end-of-options",
        f"{requested_revision}^{{tree}}",
    ).strip()
    if _SHA1_PATTERN.fullmatch(tree.decode("ascii", errors="ignore")) is None:
        raise RevisionError("commit root tree is malformed")
    actual_tree = tree.decode("ascii")
    if actual_tree != expected_tree:
        raise TreeMismatchError("commit root tree does not match expected tree")
    return requested_revision, actual_tree


def _valid_full_ref(name: object) -> bool:
    if not isinstance(name, str) or not name.startswith("refs/"):
        return False
    if any(0xD800 <= ord(character) <= 0xDFFF for character in name):
        return False
    if name == "refs/" or name.endswith(("/", ".")) or "//" in name:
        return False
    if ".." in name or "@{" in name:
        return False
    if any(ord(character) < 32 or ord(character) == 127 for character in name):
        return False
    if any(character in _FORBIDDEN_REF_CHARACTERS for character in name):
        return False
    components = name.split("/")
    return all(
        component
        and component not in (".", "..")
        and not component.startswith(".")
        and not component.endswith(".lock")
        for component in components
    )


def _protected_reference_identities(
    boundary: _RepositoryBoundary,
    records: Sequence[Mapping[str, object]],
) -> tuple[ProtectedReferenceIdentity, ...]:
    if not isinstance(records, Sequence) or isinstance(records, (str, bytes)):
        raise ProtectedReferenceError("protected reference contract is invalid")
    identities: list[ProtectedReferenceIdentity] = []
    names: set[str] = set()
    required_keys = {
        "name",
        "expected_object",
        "authoritatively_targeted",
        "selection",
    }
    for record in records:
        if not isinstance(record, Mapping) or set(record.keys()) != required_keys:
            raise ProtectedReferenceError("protected reference contract is invalid")
        name = record["name"]
        expected_object = record["expected_object"]
        if not _valid_full_ref(name):
            raise ProtectedReferenceError("protected reference name is invalid")
        if name in names:
            raise ProtectedReferenceError("protected reference name is duplicated")
        names.add(name)
        if (
            not isinstance(expected_object, str)
            or _SHA1_PATTERN.fullmatch(expected_object) is None
            or record["authoritatively_targeted"] is not False
            or record["selection"] != "forbidden"
        ):
            raise ProtectedReferenceError("protected reference contract is invalid")

        lookup = _run_git(
            boundary.target, "show-ref", "--verify", "--hash", name
        )
        actual_object: str | None = None
        if lookup.returncode == 0:
            raw_identity = lookup.stdout.strip()
            if (
                len(raw_identity) != 40
                or _SHA1_PATTERN.fullmatch(
                    raw_identity.decode("ascii", errors="ignore")
                )
                is None
            ):
                raise ProtectedReferenceError(
                    "protected reference identity is malformed"
                )
            actual_object = raw_identity.decode("ascii")
        elif lookup.returncode not in (1, 128):
            raise ProtectedReferenceError(
                f"Git show-ref failed with return code {lookup.returncode}"
            )

        matched = actual_object == expected_object
        identity = ProtectedReferenceIdentity(
            name=name,
            expected_object=expected_object,
            actual_object=actual_object,
            authoritatively_targeted=False,
            selection="forbidden",
            matched=matched,
            blocking=not matched,
        )
        if not matched:
            raise ProtectedReferenceError(
                "protected reference identity does not match", identity
            )
        identities.append(identity)
    return tuple(identities)


def resolve_snapshot(
    target_repository: str | pathlib.Path,
    *,
    repository_identity: str,
    requested_revision: str,
    expected_tree: str,
    protected_references: Sequence[Mapping[str, object]],
) -> RepositorySnapshot:
    """Resolve one exact clean local commit without reading protected content."""

    boundary = _repository_boundary(target_repository)

    def operation() -> RepositorySnapshot:
        exact_revision = _require_sha1(requested_revision)
        exact_tree = _require_sha1(expected_tree, tree=True)
        repository = _repository_identity(boundary, repository_identity)
        object_format = _object_format(boundary)
        commit, tree = _resolve_commit_and_tree(
            boundary, exact_revision, exact_tree
        )
        protected = _protected_reference_identities(
            boundary, protected_references
        )
        fingerprint = snapshot_fingerprint(
            repository.normalized_identity,
            object_format,
            commit,
            tree,
            SNAPSHOT_MODE,
        )
        return RepositorySnapshot(
            repository=repository,
            requested_revision=exact_revision,
            object_format=object_format,
            commit=commit,
            tree=tree,
            snapshot_mode=SNAPSHOT_MODE,
            fingerprint=fingerprint,
            protected_references=protected,
        )

    return _within_clean_boundary(boundary, operation)


def normalize_repository_path(path: str) -> str:
    """Validate one exact UTF-8 scalar repository-relative POSIX path."""

    if not isinstance(path, str):
        raise RepositoryPathError("repository path must be a string")
    if not path:
        raise RepositoryPathError("repository path must not be empty")
    if any(0xD800 <= ord(character) <= 0xDFFF for character in path):
        raise RepositoryPathError("repository path must contain Unicode scalars")
    if "\0" in path or "\\" in path:
        raise RepositoryPathError("repository path contains a forbidden character")
    if path.startswith("/") or re.match(r"[A-Za-z]:", path) or path.startswith("//"):
        raise RepositoryPathError("repository path must be relative")
    if path.startswith("/") or path.endswith("/"):
        raise RepositoryPathError("repository path must not have a boundary slash")
    components = path.split("/")
    if any(component in ("", ".", "..") for component in components):
        raise RepositoryPathError("repository path contains a forbidden component")
    try:
        path.encode("utf-8")
    except UnicodeEncodeError as error:
        raise RepositoryPathError("repository path is not valid UTF-8") from error
    return path


def _validate_supplied_snapshot(snapshot: RepositorySnapshot) -> None:
    if not isinstance(snapshot, RepositorySnapshot):
        raise RepositoryStateError("snapshot value is invalid")
    if (
        snapshot.snapshot_mode != SNAPSHOT_MODE
        or snapshot.object_format != "sha1"
        or _SHA1_PATTERN.fullmatch(snapshot.commit) is None
        or _SHA1_PATTERN.fullmatch(snapshot.tree) is None
        or snapshot.requested_revision != snapshot.commit
    ):
        raise RepositoryStateError("snapshot value is inconsistent")
    expected = snapshot_fingerprint(
        snapshot.repository.normalized_identity,
        snapshot.object_format,
        snapshot.commit,
        snapshot.tree,
        snapshot.snapshot_mode,
    )
    if expected != snapshot.fingerprint:
        raise RepositoryStateError("snapshot fingerprint is inconsistent")


def _lookup_blob(
    boundary: _RepositoryBoundary,
    snapshot: RepositorySnapshot,
    path: str,
) -> ImmutableBlob:
    actual_repository = _repository_identity(
        boundary, snapshot.repository.requested_identity
    )
    if actual_repository.normalized_identity != snapshot.repository.normalized_identity:
        raise RepositoryIdentityError("snapshot repository identity no longer matches")
    if _object_format(boundary) != snapshot.object_format:
        raise ObjectFormatError("snapshot object format no longer matches")

    lookup = _run_git(boundary.target, "ls-tree", "-z", snapshot.tree, "--", path)
    if lookup.returncode != 0:
        raise BlobLookupError(
            f"Git ls-tree failed with return code {lookup.returncode}"
        )
    entries = lookup.stdout.split(b"\0")
    if entries and entries[-1] == b"":
        entries.pop()
    if len(entries) != 1:
        raise BlobLookupError("repository path does not identify exactly one entry")
    try:
        metadata, raw_path = entries[0].split(b"\t", 1)
        mode_bytes, type_bytes, object_bytes = metadata.split(b" ")
    except ValueError as error:
        raise BlobLookupError("tree entry is malformed") from error
    expected_path = path.encode("utf-8")
    try:
        decoded_path = raw_path.decode("utf-8")
        mode = mode_bytes.decode("ascii")
        object_type = type_bytes.decode("ascii")
        object_id = object_bytes.decode("ascii")
    except UnicodeDecodeError as error:
        raise BlobLookupError("tree entry encoding is malformed") from error
    if raw_path != expected_path or decoded_path != path:
        raise BlobLookupError("tree entry path does not match exactly")
    if _SHA1_PATTERN.fullmatch(object_id) is None:
        raise BlobLookupError("tree entry object identity is malformed")
    if mode not in ("100644", "100755") or object_type != "blob":
        raise BlobLookupError("tree entry is not a supported regular blob")

    content_result = _run_git(boundary.target, "cat-file", "blob", object_id)
    if content_result.returncode != 0:
        raise BlobLookupError(
            f"Git cat-file failed with return code {content_result.returncode}"
        )
    return ImmutableBlob(
        path=path,
        mode=mode,
        object_format=snapshot.object_format,
        object_id=object_id,
        content=content_result.stdout,
    )


def read_snapshot_blob(
    target_repository: str | pathlib.Path,
    snapshot: RepositorySnapshot,
    path: str,
) -> ImmutableBlob:
    """Read exact raw bytes for one regular blob in an immutable root tree."""

    boundary = _repository_boundary(target_repository)

    def operation() -> ImmutableBlob:
        normalized_path = normalize_repository_path(path)
        _validate_supplied_snapshot(snapshot)
        return _lookup_blob(boundary, snapshot, normalized_path)

    return _within_clean_boundary(boundary, operation)
