from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
from typing import Any


MAX_ACTIVE_STATE_BYTES = 16_384
SUPPORTED_SCHEMA_VERSION = 1
AUTHORITY_SENTINEL = "external-not-established-by-repository-or-atlas"

_IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
_COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}\Z")
_DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
_PHASE_LIFECYCLES = frozenset({"accepted", "published", "operational"})
_WORK_SELECTION_STATUSES = frozenset({"selected", "intentional_idle"})
_CHECKPOINT_LIFECYCLES = frozenset({"selected"})
_DECISION_STATUSES = frozenset({"pending"})
_EVIDENCE_RELATIONS = frozenset(
    {
        "defines_phase",
        "records_phase",
        "supports_blocker",
        "supports_checkpoint",
        "supports_decision",
        "supports_unknown",
    }
)
_REFERENCE_RELATIONS = {
    "phase": frozenset({"defines_phase", "records_phase"}),
    "checkpoint": frozenset({"supports_checkpoint"}),
    "blocker": frozenset({"supports_blocker"}),
    "unknown": frozenset({"supports_unknown"}),
    "decision": frozenset({"supports_decision"}),
}


class ActiveStateError(ValueError):
    """Raised when the canonical active-state contract cannot be trusted."""


@dataclass(frozen=True)
class Phase:
    id: str
    name: str
    lifecycle: str
    effective_date: date
    evidence_refs: tuple[str, ...]

    @property
    def display_name(self) -> str:
        return f"{self.name} — {self.lifecycle.capitalize()}"


@dataclass(frozen=True)
class SelectedCheckpoint:
    id: str
    name: str
    lifecycle: str
    effective_date: date
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class WorkSelection:
    status: str
    selected_checkpoint: SelectedCheckpoint | None

    @property
    def intentional_idle(self) -> bool:
        return self.status == "intentional_idle"


@dataclass(frozen=True)
class StateConcern:
    id: str
    summary: str
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class DecisionRequired:
    id: str
    summary: str
    status: str
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class EvidenceLink:
    id: str
    path: str
    relation: str
    commit: str


@dataclass(frozen=True)
class Freshness:
    effective_date: date
    review_after: date | None


@dataclass(frozen=True)
class Authority:
    task: str
    implementation: str
    publication: str


@dataclass(frozen=True)
class ActiveState:
    schema_version: int
    phase: Phase
    work_selection: WorkSelection
    blockers: tuple[StateConcern, ...]
    unknowns: tuple[StateConcern, ...]
    decision_required: DecisionRequired | None
    evidence_links: tuple[EvidenceLink, ...]
    freshness: Freshness
    authority: Authority


def active_state_path(repository_root: Path) -> Path:
    return repository_root / "docs" / "current-state.json"


def _reject_constant(value: str) -> None:
    raise ActiveStateError(f"unsupported JSON constant: {value}")


def _reject_float(value: str) -> None:
    raise ActiveStateError(f"unsupported JSON numeric value: {value}")


def _parse_integer(value: str) -> int:
    if len(value) > 20:
        raise ActiveStateError("unsupported JSON integer magnitude")
    return int(value)


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ActiveStateError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _decode_json(data: bytes) -> dict[str, Any]:
    if len(data) > MAX_ACTIVE_STATE_BYTES:
        raise ActiveStateError(
            "canonical active state exceeds the 16,384-byte maximum"
        )

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ActiveStateError("canonical active state is not valid UTF-8") from error

    try:
        value = json.loads(
            text,
            object_pairs_hook=_object_without_duplicates,
            parse_constant=_reject_constant,
            parse_float=_reject_float,
            parse_int=_parse_integer,
        )
    except ActiveStateError:
        raise
    except json.JSONDecodeError as error:
        raise ActiveStateError(
            f"canonical active state is not valid JSON: {error.msg}"
        ) from error
    except (RecursionError, ValueError) as error:
        raise ActiveStateError(
            "canonical active state contains unsupported JSON structure"
        ) from error

    if type(value) is not dict:
        raise ActiveStateError("canonical active state must be a JSON object")

    return value


def _object(
    value: Any,
    *,
    location: str,
    keys: frozenset[str],
) -> dict[str, Any]:
    if type(value) is not dict:
        raise ActiveStateError(f"{location} must be an object")

    actual = frozenset(value)
    missing = sorted(keys - actual)
    unknown = sorted(actual - keys)

    if missing:
        raise ActiveStateError(
            f"{location} is missing required key(s): {', '.join(missing)}"
        )
    if unknown:
        raise ActiveStateError(
            f"{location} has unknown key(s): {', '.join(unknown)}"
        )

    return value


def _array(value: Any, *, location: str) -> list[Any]:
    if type(value) is not list:
        raise ActiveStateError(f"{location} must be an array")
    return value


def _string(
    value: Any,
    *,
    location: str,
    maximum: int,
) -> str:
    if type(value) is not str:
        raise ActiveStateError(f"{location} must be a string")
    if not value or value.strip() != value:
        raise ActiveStateError(
            f"{location} must be non-empty without surrounding whitespace"
        )
    if len(value) > maximum:
        raise ActiveStateError(
            f"{location} exceeds the {maximum}-character maximum"
        )
    if any(character.isspace() and character != " " for character in value):
        raise ActiveStateError(
            f"{location} may contain ASCII spaces but no other whitespace"
        )
    return value


def _identifier(value: Any, *, location: str) -> str:
    identifier = _string(value, location=location, maximum=64)
    if _IDENTIFIER_PATTERN.fullmatch(identifier) is None:
        raise ActiveStateError(
            f"{location} must use lowercase kebab-case identifier syntax"
        )
    return identifier


def _enum(
    value: Any,
    *,
    location: str,
    accepted: frozenset[str],
) -> str:
    result = _string(value, location=location, maximum=64)
    if result not in accepted:
        raise ActiveStateError(
            f"{location} has unsupported value {result!r}; "
            f"expected one of: {', '.join(sorted(accepted))}"
        )
    return result


def _strict_date(value: Any, *, location: str) -> date:
    text = _string(value, location=location, maximum=10)
    if _DATE_PATTERN.fullmatch(text) is None:
        raise ActiveStateError(f"{location} must use YYYY-MM-DD syntax")
    try:
        parsed = date.fromisoformat(text)
    except ValueError as error:
        raise ActiveStateError(f"{location} is not a valid calendar date") from error
    if parsed.isoformat() != text:
        raise ActiveStateError(f"{location} is not a canonical calendar date")
    return parsed


def _evidence_refs(value: Any, *, location: str) -> tuple[str, ...]:
    refs = tuple(
        _identifier(item, location=f"{location}[{index}]")
        for index, item in enumerate(_array(value, location=location))
    )
    if len(set(refs)) != len(refs):
        raise ActiveStateError(f"{location} must not contain duplicate references")
    return refs


def _parse_phase(value: Any) -> Phase:
    obj = _object(
        value,
        location="phase",
        keys=frozenset(
            {"id", "name", "lifecycle", "effective_date", "evidence_refs"}
        ),
    )
    return Phase(
        id=_identifier(obj["id"], location="phase.id"),
        name=_string(obj["name"], location="phase.name", maximum=160),
        lifecycle=_enum(
            obj["lifecycle"],
            location="phase.lifecycle",
            accepted=_PHASE_LIFECYCLES,
        ),
        effective_date=_strict_date(
            obj["effective_date"], location="phase.effective_date"
        ),
        evidence_refs=_evidence_refs(
            obj["evidence_refs"], location="phase.evidence_refs"
        ),
    )


def _parse_checkpoint(value: Any) -> SelectedCheckpoint:
    obj = _object(
        value,
        location="work_selection.selected_checkpoint",
        keys=frozenset(
            {"id", "name", "lifecycle", "effective_date", "evidence_refs"}
        ),
    )
    return SelectedCheckpoint(
        id=_identifier(
            obj["id"], location="work_selection.selected_checkpoint.id"
        ),
        name=_string(
            obj["name"],
            location="work_selection.selected_checkpoint.name",
            maximum=200,
        ),
        lifecycle=_enum(
            obj["lifecycle"],
            location="work_selection.selected_checkpoint.lifecycle",
            accepted=_CHECKPOINT_LIFECYCLES,
        ),
        effective_date=_strict_date(
            obj["effective_date"],
            location="work_selection.selected_checkpoint.effective_date",
        ),
        evidence_refs=_evidence_refs(
            obj["evidence_refs"],
            location="work_selection.selected_checkpoint.evidence_refs",
        ),
    )


def _parse_work_selection(value: Any) -> WorkSelection:
    obj = _object(
        value,
        location="work_selection",
        keys=frozenset({"status", "selected_checkpoint"}),
    )
    status_value = _enum(
        obj["status"],
        location="work_selection.status",
        accepted=_WORK_SELECTION_STATUSES,
    )
    raw_checkpoint = obj["selected_checkpoint"]

    if status_value == "selected":
        if raw_checkpoint is None:
            raise ActiveStateError(
                "work_selection.selected_checkpoint must be an object "
                "when work_selection.status is 'selected'"
            )
        checkpoint = _parse_checkpoint(raw_checkpoint)
    else:
        if raw_checkpoint is not None:
            raise ActiveStateError(
                "work_selection.selected_checkpoint must be null "
                "when work_selection.status is 'intentional_idle'"
            )
        checkpoint = None

    return WorkSelection(status=status_value, selected_checkpoint=checkpoint)


def _parse_concerns(value: Any, *, location: str) -> tuple[StateConcern, ...]:
    concerns: list[StateConcern] = []
    for index, item in enumerate(_array(value, location=location)):
        item_location = f"{location}[{index}]"
        obj = _object(
            item,
            location=item_location,
            keys=frozenset({"id", "summary", "evidence_refs"}),
        )
        evidence_refs = _evidence_refs(
            obj["evidence_refs"], location=f"{item_location}.evidence_refs"
        )
        if not evidence_refs:
            raise ActiveStateError(
                f"{item_location}.evidence_refs must contain canonical evidence"
            )
        concerns.append(
            StateConcern(
                id=_identifier(obj["id"], location=f"{item_location}.id"),
                summary=_string(
                    obj["summary"],
                    location=f"{item_location}.summary",
                    maximum=500,
                ),
                evidence_refs=evidence_refs,
            )
        )
    return tuple(concerns)


def _parse_decision(value: Any) -> DecisionRequired | None:
    if value is None:
        return None
    obj = _object(
        value,
        location="decision_required",
        keys=frozenset({"id", "summary", "status", "evidence_refs"}),
    )
    return DecisionRequired(
        id=_identifier(obj["id"], location="decision_required.id"),
        summary=_string(
            obj["summary"], location="decision_required.summary", maximum=500
        ),
        status=_enum(
            obj["status"],
            location="decision_required.status",
            accepted=_DECISION_STATUSES,
        ),
        evidence_refs=_evidence_refs(
            obj["evidence_refs"], location="decision_required.evidence_refs"
        ),
    )


def _parse_evidence_links(value: Any) -> tuple[EvidenceLink, ...]:
    links: list[EvidenceLink] = []
    for index, item in enumerate(_array(value, location="evidence_links")):
        location = f"evidence_links[{index}]"
        obj = _object(
            item,
            location=location,
            keys=frozenset({"id", "path", "relation", "commit"}),
        )
        commit = _string(
            obj["commit"], location=f"{location}.commit", maximum=40
        )
        if _COMMIT_PATTERN.fullmatch(commit) is None:
            raise ActiveStateError(
                f"{location}.commit must be a full lowercase Git commit identity"
            )
        links.append(
            EvidenceLink(
                id=_identifier(obj["id"], location=f"{location}.id"),
                path=_string(
                    obj["path"], location=f"{location}.path", maximum=240
                ),
                relation=_enum(
                    obj["relation"],
                    location=f"{location}.relation",
                    accepted=_EVIDENCE_RELATIONS,
                ),
                commit=commit,
            )
        )
    return tuple(links)


def _parse_freshness(value: Any) -> Freshness:
    obj = _object(
        value,
        location="freshness",
        keys=frozenset({"effective_date", "review_after"}),
    )
    effective_date = _strict_date(
        obj["effective_date"], location="freshness.effective_date"
    )
    raw_review_after = obj["review_after"]
    review_after = (
        None
        if raw_review_after is None
        else _strict_date(raw_review_after, location="freshness.review_after")
    )
    if review_after is not None and review_after < effective_date:
        raise ActiveStateError(
            "freshness.review_after must not precede freshness.effective_date"
        )
    return Freshness(
        effective_date=effective_date,
        review_after=review_after,
    )


def _parse_authority(value: Any) -> Authority:
    obj = _object(
        value,
        location="authority",
        keys=frozenset({"task", "implementation", "publication"}),
    )
    parsed: dict[str, str] = {}
    for dimension in ("task", "implementation", "publication"):
        sentinel = _string(
            obj[dimension], location=f"authority.{dimension}", maximum=64
        )
        if sentinel != AUTHORITY_SENTINEL:
            raise ActiveStateError(
                f"authority.{dimension} must be the fixed non-authority sentinel "
                f"{AUTHORITY_SENTINEL!r}"
            )
        parsed[dimension] = sentinel
    return Authority(**parsed)


def _validate_repository_relative_file(repository_root: Path, path: str) -> None:
    if "\\" in path:
        raise ActiveStateError(
            f"evidence path must use repository-relative POSIX syntax: {path}"
        )

    relative = PurePosixPath(path)
    if (
        relative.is_absolute()
        or not relative.parts
        or any(part in {"", ".", ".."} for part in relative.parts)
        or relative.as_posix() != path
    ):
        raise ActiveStateError(
            f"evidence path is not a confined repository-relative path: {path}"
        )

    root = repository_root.resolve(strict=True)
    current = root
    for index, part in enumerate(relative.parts):
        current = current / part
        try:
            metadata = current.lstat()
        except FileNotFoundError as error:
            raise ActiveStateError(f"evidence path does not exist: {path}") from error

        if stat.S_ISLNK(metadata.st_mode):
            raise ActiveStateError(f"evidence path must not traverse a symlink: {path}")
        if index < len(relative.parts) - 1 and not stat.S_ISDIR(metadata.st_mode):
            raise ActiveStateError(
                f"evidence path parent is not a directory: {path}"
            )

    if not stat.S_ISREG(current.lstat().st_mode):
        raise ActiveStateError(
            f"evidence path must identify a regular file: {path}"
        )

    try:
        current.resolve(strict=True).relative_to(root)
    except ValueError as error:
        raise ActiveStateError(
            f"evidence path escapes the repository root: {path}"
        ) from error


def _git_output(repository_root: Path, arguments: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise ActiveStateError(
            "local Git evidence identity could not be verified"
        ) from error
    return result.stdout.strip()


def _validate_local_git_evidence(
    repository_root: Path,
    link: EvidenceLink,
) -> None:
    resolved_commit = _git_output(
        repository_root,
        ["rev-parse", "--verify", f"{link.commit}^{{commit}}"],
    )
    if resolved_commit != link.commit:
        raise ActiveStateError(
            f"evidence commit does not resolve to its declared identity: {link.id}"
        )

    object_type = _git_output(
        repository_root,
        ["cat-file", "-t", f"{link.commit}:{link.path}"],
    )
    if object_type != "blob":
        raise ActiveStateError(
            f"evidence path is not a file at its declared commit: {link.id}"
        )


def _validate_reference_group(
    *,
    refs: tuple[str, ...],
    owner: str,
    evidence_by_id: dict[str, EvidenceLink],
) -> None:
    accepted_relations = _REFERENCE_RELATIONS[owner]
    for reference in refs:
        link = evidence_by_id.get(reference)
        if link is None:
            raise ActiveStateError(
                f"{owner} evidence reference does not resolve: {reference}"
            )
        if link.relation not in accepted_relations:
            raise ActiveStateError(
                f"{owner} evidence reference {reference!r} has incompatible "
                f"relation {link.relation!r}"
            )


def _validate_cross_fields(
    state: ActiveState,
    *,
    repository_root: Path,
    verify_evidence: bool,
) -> None:
    identifiers = [state.phase.id]
    if state.work_selection.selected_checkpoint is not None:
        identifiers.append(state.work_selection.selected_checkpoint.id)
    identifiers.extend(concern.id for concern in state.blockers)
    identifiers.extend(concern.id for concern in state.unknowns)
    if state.decision_required is not None:
        identifiers.append(state.decision_required.id)
    identifiers.extend(link.id for link in state.evidence_links)

    if len(set(identifiers)) != len(identifiers):
        raise ActiveStateError("all active-state entity IDs must be globally unique")

    evidence_by_id = {link.id: link for link in state.evidence_links}
    if len(evidence_by_id) != len(state.evidence_links):
        raise ActiveStateError("evidence link IDs must be unique")

    if not state.phase.evidence_refs:
        raise ActiveStateError("phase.evidence_refs must contain canonical evidence")

    _validate_reference_group(
        refs=state.phase.evidence_refs,
        owner="phase",
        evidence_by_id=evidence_by_id,
    )

    checkpoint = state.work_selection.selected_checkpoint
    if checkpoint is not None:
        _validate_reference_group(
            refs=checkpoint.evidence_refs,
            owner="checkpoint",
            evidence_by_id=evidence_by_id,
        )
        if checkpoint.effective_date > state.freshness.effective_date:
            raise ActiveStateError(
                "selected checkpoint effective date must not follow state "
                "freshness effective date"
            )

    for concern in state.blockers:
        _validate_reference_group(
            refs=concern.evidence_refs,
            owner="blocker",
            evidence_by_id=evidence_by_id,
        )
    for concern in state.unknowns:
        _validate_reference_group(
            refs=concern.evidence_refs,
            owner="unknown",
            evidence_by_id=evidence_by_id,
        )
    if state.decision_required is not None:
        _validate_reference_group(
            refs=state.decision_required.evidence_refs,
            owner="decision",
            evidence_by_id=evidence_by_id,
        )

    if state.phase.effective_date > state.freshness.effective_date:
        raise ActiveStateError(
            "phase effective date must not follow state freshness effective date"
        )

    if verify_evidence:
        for link in state.evidence_links:
            _validate_repository_relative_file(repository_root, link.path)
            _validate_local_git_evidence(repository_root, link)


def parse_active_state_bytes(
    data: bytes,
    *,
    repository_root: Path,
    verify_evidence: bool = True,
) -> ActiveState:
    raw = _object(
        _decode_json(data),
        location="active state",
        keys=frozenset(
            {
                "schema_version",
                "phase",
                "work_selection",
                "blockers",
                "unknowns",
                "decision_required",
                "evidence_links",
                "freshness",
                "authority",
            }
        ),
    )

    schema_version = raw["schema_version"]
    if type(schema_version) is not int:
        raise ActiveStateError("schema_version must be an integer")
    if schema_version != SUPPORTED_SCHEMA_VERSION:
        raise ActiveStateError(
            f"unsupported active-state schema version: {schema_version}"
        )

    state = ActiveState(
        schema_version=schema_version,
        phase=_parse_phase(raw["phase"]),
        work_selection=_parse_work_selection(raw["work_selection"]),
        blockers=_parse_concerns(raw["blockers"], location="blockers"),
        unknowns=_parse_concerns(raw["unknowns"], location="unknowns"),
        decision_required=_parse_decision(raw["decision_required"]),
        evidence_links=_parse_evidence_links(raw["evidence_links"]),
        freshness=_parse_freshness(raw["freshness"]),
        authority=_parse_authority(raw["authority"]),
    )
    _validate_cross_fields(
        state,
        repository_root=repository_root,
        verify_evidence=verify_evidence,
    )
    return state


def load_active_state(
    path: Path | None = None,
    *,
    repository_root: Path | None = None,
    verify_evidence: bool = True,
) -> ActiveState:
    if repository_root is None:
        from atlas.platform.repository import repo_root

        repository_root = repo_root()
    if path is None:
        path = active_state_path(repository_root)

    try:
        metadata = path.lstat()
    except OSError as error:
        raise ActiveStateError(
            f"canonical active state could not be read: {path}"
        ) from error
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ActiveStateError(
            "canonical active state must be a non-symlink regular file"
        )
    if metadata.st_size > MAX_ACTIVE_STATE_BYTES:
        raise ActiveStateError(
            "canonical active state exceeds the 16,384-byte maximum"
        )
    try:
        data = path.read_bytes()
    except OSError as error:
        raise ActiveStateError(
            f"canonical active state could not be read: {path}"
        ) from error

    return parse_active_state_bytes(
        data,
        repository_root=repository_root,
        verify_evidence=verify_evidence,
    )


__all__ = [
    "AUTHORITY_SENTINEL",
    "MAX_ACTIVE_STATE_BYTES",
    "SUPPORTED_SCHEMA_VERSION",
    "ActiveState",
    "ActiveStateError",
    "Authority",
    "DecisionRequired",
    "EvidenceLink",
    "Freshness",
    "Phase",
    "SelectedCheckpoint",
    "StateConcern",
    "WorkSelection",
    "active_state_path",
    "load_active_state",
    "parse_active_state_bytes",
]
