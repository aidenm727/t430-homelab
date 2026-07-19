"""Exact selected-source materialization for EO-2026-013 Checkpoint B2a."""

from __future__ import annotations

import json
import pathlib
from collections.abc import Mapping
from typing import Any

from atlas.platform.context_compilation.canonical_json import canonicalize
from atlas.platform.context_compilation.digests import (
    byte_digest,
    omission_identifier,
    payload_identifier,
    snapshot_fingerprint,
    source_identifier,
)
from atlas.platform.context_compilation.models import (
    CompilationRequest,
    FreshnessRecord,
    IdentifiedOmission,
    ImmutableSourceIdentityRecord,
    MaterializationResult,
    MaterializedPayload,
    MaterializedSource,
    ModelValueError,
    RepositorySnapshot,
    SelectedSourcePlan,
    SelectionPlan,
)
from atlas.platform.context_compilation.selectors import (
    SelectorError,
    SelectorOutput,
    select_markdown_heading,
    select_yaml_fields,
)
from atlas.platform.context_compilation.snapshot import (
    RepositoryPathError,
    SnapshotError,
    normalize_repository_path,
    read_snapshot_blob,
)


_REQUEST_SCHEMA = "aiden.task-context.compilation-request/v1"
_SELECTION_POLICY_ID = "example.read-only-architecture-assessment"
_SELECTION_POLICY_VERSION = "1.0.1"
_SELECTION_POLICY_DIGEST = (
    "69577722ea4eb6f479424f3bf324866cc2992d5df82b3224e5f20571ef081938"
)
_REPOSITORY_IDENTITY = "github.com/aidenm727/t430-homelab"
_SNAPSHOT_MODE = "clean_committed"
_OBJECT_FORMAT = "sha1"
_OPPORTUNITY_PATH = (
    "docs/opportunities/reviewed/"
    "EO-2026-013-task-scoped-agent-context-compilation.yaml"
)
_OPPORTUNITY_OWNER = "docs/architecture/engineering-opportunity-object.md"
_MISSION_PATH = "docs/current-mission.md"
_REPOSITORY_PATH = "docs/architecture/repository.md"
_KNOWLEDGE_PATH = "docs/architecture/knowledge-authority.md"
_COLLABORATION_PATH = "docs/standards/engineering-collaboration.md"
_EXPECTED_RULE_ORDER = (
    "S010-explicit-opportunity-anchor",
    "S020-current-mission-milestone",
    "S030-canonical-repository-authority",
    "S040-mandatory-knowledge-authority",
    "S050-mandatory-collaboration",
)
_ORDINARY_CANONICAL_RULES = frozenset(
    (
        "S030-canonical-repository-authority",
        "S040-mandatory-knowledge-authority",
        "S050-mandatory-collaboration",
    )
)


class MaterializationError(RuntimeError):
    """Base class for bounded materialization failures."""


class MaterializationContractError(MaterializationError):
    """The supplied request, snapshot, or plan is unsupported or inconsistent."""


class MaterializationIdentityError(MaterializationError):
    """An immutable identity, digest link, or stable identifier is inconsistent."""


class MaterializationSourceError(MaterializationError):
    """An accepted selected source cannot be reread or selected exactly."""


def _contract_failure(message: str) -> None:
    raise MaterializationContractError(message)


def _identity_failure(message: str) -> None:
    raise MaterializationIdentityError(message)


def _known_task_id(request: CompilationRequest) -> str:
    record = request.task.get("id")
    if not isinstance(record, Mapping):
        _contract_failure("request task id contract is invalid")
    if record.get("state") != "known":
        _contract_failure("request task id must be known")
    value = record.get("value")
    if not isinstance(value, str) or not value:
        _contract_failure("request task id value is invalid")
    return value


def _expected_path(rule_id: str) -> str:
    if rule_id == "S010-explicit-opportunity-anchor":
        return _OPPORTUNITY_PATH
    if rule_id == "S020-current-mission-milestone":
        return _MISSION_PATH
    if rule_id == "S030-canonical-repository-authority":
        return _REPOSITORY_PATH
    if rule_id == "S040-mandatory-knowledge-authority":
        return _KNOWLEDGE_PATH
    if rule_id == "S050-mandatory-collaboration":
        return _COLLABORATION_PATH
    _contract_failure("selected rule is outside the first-slice contract")
    raise AssertionError("unreachable")


def _expected_owner(rule_id: str) -> str:
    if rule_id == "S010-explicit-opportunity-anchor":
        return _OPPORTUNITY_OWNER
    if rule_id == "S020-current-mission-milestone":
        return _MISSION_PATH
    if rule_id == "S030-canonical-repository-authority":
        return _REPOSITORY_PATH
    if rule_id == "S040-mandatory-knowledge-authority":
        return _KNOWLEDGE_PATH
    if rule_id == "S050-mandatory-collaboration":
        return _COLLABORATION_PATH
    _contract_failure("selected rule is outside the first-slice contract")
    raise AssertionError("unreachable")


def _selector_descriptor(record: SelectedSourcePlan) -> str:
    selector = record.selector
    selector_type = selector.get("type")
    if record.rule_id == "S010-explicit-opportunity-anchor":
        fields = selector.get("fields")
        if (
            selector_type != "yaml_fields"
            or not isinstance(fields, (list, tuple))
            or tuple(fields) != ("id", "title", "status", "summary")
        ):
            _contract_failure("opportunity selector contract is unsupported")
        return "yaml-fields:/id,/title,/status,/summary"

    if record.rule_id == "S020-current-mission-milestone":
        expected_heading = "## Initial Milestone"
    elif record.rule_id == "S030-canonical-repository-authority":
        expected_heading = "## Source of Truth Hierarchy"
    elif record.rule_id == "S040-mandatory-knowledge-authority":
        expected_heading = "### Generated Context"
    elif record.rule_id == "S050-mandatory-collaboration":
        expected_heading = "## Responsibilities"
    else:
        _contract_failure("selected rule is outside the first-slice contract")
        raise AssertionError("unreachable")

    if (
        selector_type != "heading"
        or selector.get("heading_text") != expected_heading
        or selector.get("occurrence") != 1
    ):
        _contract_failure("heading selector contract is unsupported")
    return f"heading:{expected_heading}"


def _selected_sort_key(
    record: SelectedSourcePlan,
) -> tuple[int, str, str, bytes]:
    return (
        record.priority_tier,
        record.rule_id,
        record.normalized_path_or_object_id,
        canonicalize(record.selector),
    )


def _trace_sort_key(record: Any) -> tuple[str, str]:
    return record.rule_id, record.boundary


def _validate_selected_record(record: SelectedSourcePlan) -> None:
    expected_path = _expected_path(record.rule_id)
    if record.path != expected_path:
        _contract_failure("selected source path is inconsistent")
    try:
        normalized = normalize_repository_path(record.path)
    except RepositoryPathError:
        _contract_failure("selected source path is invalid")
    if normalized != record.path:
        _contract_failure("selected source path is not normalized")
    if record.normalized_path_or_object_id != (
        record.structured_object_identity or record.path
    ):
        _contract_failure("selected normalized identity is inconsistent")
    if record.object_format != _OBJECT_FORMAT:
        _contract_failure("selected object format is unsupported")
    if record.mode not in ("100644", "100755"):
        _contract_failure("selected source mode is unsupported")
    if record.sensitivity != "public":
        _contract_failure("selected source sensitivity is unsupported")
    if record.canonical_owner != _expected_owner(record.rule_id):
        _contract_failure("selected canonical owner is inconsistent")

    if record.rule_id == "S010-explicit-opportunity-anchor":
        if (
            record.rule_type != "explicit_anchor"
            or record.source_kind != "repository_object"
            or record.authority_class != "structured_repository_object"
            or record.structured_object_identity
            != "engineering-opportunity:EO-2026-013"
        ):
            _contract_failure("selected opportunity contract is unsupported")
    else:
        expected_rule_type = (
            "explicit_anchor"
            if record.rule_id == "S020-current-mission-milestone"
            else (
                "task_profile"
                if record.rule_id == "S040-mandatory-knowledge-authority"
                else "allowlisted_relationship"
            )
        )
        if (
            record.rule_type != expected_rule_type
            or record.source_kind != "document"
            or record.authority_class != "canonical_document"
            or record.structured_object_identity is not None
        ):
            _contract_failure("selected document contract is unsupported")
    _selector_descriptor(record)


def _validate_as_of(value: str) -> None:
    try:
        FreshnessRecord(
            status="unknown",
            basis="Explicit request freshness reference validated before source reads.",
            rule="F000-explicit-reference-validation",
            as_of=value,
        )
    except ModelValueError as error:
        raise MaterializationContractError(
            "request as_of contract is invalid"
        ) from error


def _validate_input_contract(
    *,
    target_repository: str | pathlib.Path,
    request: CompilationRequest,
    snapshot: RepositorySnapshot,
    selection_plan: SelectionPlan,
) -> None:
    if not isinstance(target_repository, (str, pathlib.Path)):
        _contract_failure("target repository must be an explicit path")
    if isinstance(target_repository, str) and not target_repository:
        _contract_failure("target repository path must not be empty")
    if not isinstance(request, CompilationRequest):
        _contract_failure("request must be a CompilationRequest")
    if not isinstance(snapshot, RepositorySnapshot):
        _contract_failure("snapshot must be a RepositorySnapshot")
    if not isinstance(selection_plan, SelectionPlan):
        _contract_failure("selection_plan must be a SelectionPlan")

    if request.schema_version != _REQUEST_SCHEMA:
        _contract_failure("request schema is unsupported")
    if (
        request.selection_policy.id != _SELECTION_POLICY_ID
        or request.selection_policy.version != _SELECTION_POLICY_VERSION
        or request.selection_policy.digest.algorithm != "sha256"
        or request.selection_policy.digest.canonicalization != "rfc8785-jcs"
        or request.selection_policy.digest.value != _SELECTION_POLICY_DIGEST
    ):
        _contract_failure("request selection policy identity is unsupported")
    _validate_as_of(request.as_of)

    task_id = _known_task_id(request)
    if selection_plan.request_task_id != task_id:
        _contract_failure("request task identity does not match the selection plan")
    if (
        selection_plan.selection_policy_id != request.selection_policy.id
        or selection_plan.selection_policy_version
        != request.selection_policy.version
        or selection_plan.selection_policy_digest
        != request.selection_policy.digest
    ):
        _contract_failure("request selection policy does not match the plan")

    if (
        request.repository.identity != _REPOSITORY_IDENTITY
        or snapshot.repository.requested_identity != _REPOSITORY_IDENTITY
        or snapshot.repository.normalized_identity != _REPOSITORY_IDENTITY
        or selection_plan.repository_identity != _REPOSITORY_IDENTITY
    ):
        _contract_failure("repository identities do not match")
    if (
        request.repository.requested_revision != snapshot.requested_revision
        or request.repository.requested_revision != snapshot.commit
        or selection_plan.requested_revision != snapshot.requested_revision
        or selection_plan.commit != snapshot.commit
    ):
        _contract_failure("requested revisions and commits do not match")
    if selection_plan.tree != snapshot.tree:
        _contract_failure("selection plan tree does not match the snapshot")
    if (
        snapshot.object_format != _OBJECT_FORMAT
        or selection_plan.object_format != snapshot.object_format
    ):
        _contract_failure("object formats do not match")
    if (
        snapshot.snapshot_mode != _SNAPSHOT_MODE
        or selection_plan.snapshot_mode != snapshot.snapshot_mode
    ):
        _contract_failure("snapshot modes do not match")

    expected_fingerprint = snapshot_fingerprint(
        snapshot.repository.normalized_identity,
        snapshot.object_format,
        snapshot.commit,
        snapshot.tree,
        snapshot.snapshot_mode,
    )
    if (
        snapshot.fingerprint != expected_fingerprint
        or selection_plan.snapshot_fingerprint != snapshot.fingerprint
    ):
        _contract_failure("snapshot fingerprints do not match")

    if not selection_plan.ready_for_compilation:
        _contract_failure("selection plan is not ready for compilation")

    selected = tuple(selection_plan.selected)
    if selected != tuple(sorted(selected, key=_selected_sort_key)):
        _contract_failure("selected sources are not in accepted stable order")
    if tuple(selection_plan.omissions) != tuple(
        sorted(selection_plan.omissions, key=_trace_sort_key)
    ):
        _contract_failure("selection omissions are not in accepted stable order")
    if tuple(selection_plan.unknowns) != tuple(
        sorted(selection_plan.unknowns, key=_trace_sort_key)
    ):
        _contract_failure("selection unknowns are not in accepted stable order")

    seen_rules: set[str] = set()
    seen_candidates: set[tuple[str, bytes]] = set()
    last_rule_index = -1
    for record in selected:
        _validate_selected_record(record)
        if record.commit != snapshot.commit:
            _contract_failure("selected source commit does not match the snapshot")
        if record.rule_id in seen_rules:
            _contract_failure("selected rule identifiers must be unique")
        seen_rules.add(record.rule_id)
        try:
            rule_index = _EXPECTED_RULE_ORDER.index(record.rule_id)
        except ValueError:
            _contract_failure("selected rule is outside the accepted order")
        if rule_index <= last_rule_index:
            _contract_failure("selected rule order is inconsistent")
        last_rule_index = rule_index
        candidate = (record.path, canonicalize(record.selector))
        if candidate in seen_candidates:
            _contract_failure("selected candidate identity is duplicated")
        seen_candidates.add(candidate)


def _execute_selector(
    record: SelectedSourcePlan,
    content: bytes,
) -> tuple[str, SelectorOutput]:
    descriptor = _selector_descriptor(record)
    try:
        if record.rule_id == "S010-explicit-opportunity-anchor":
            output = select_yaml_fields(
                content,
                tuple(record.selector["fields"]),
            )
        else:
            output = select_markdown_heading(
                content,
                record.selector["heading_text"],
                record.selector["occurrence"],
            )
    except SelectorError as error:
        raise MaterializationSourceError(
            f"accepted selector failed for rule {record.rule_id}"
        ) from error

    if output.encoding != "utf-8" or not isinstance(output.content, bytes):
        raise MaterializationSourceError(
            f"accepted selector returned invalid payload metadata for rule "
            f"{record.rule_id}"
        )
    return descriptor, output


def _transformation(
    record: SelectedSourcePlan,
    output: SelectorOutput,
) -> Mapping[str, Any]:
    if record.rule_id == "S010-explicit-opportunity-anchor":
        expected = {"fields": ("id", "title", "status", "summary")}
        if output.selector_type != "yaml_fields" or output.transformation != expected:
            _contract_failure("YAML selector transformation is inconsistent")
        return {
            "type": "yaml_field_selection",
            "selected_fields": ("/id", "/title", "/status", "/summary"),
            "output": "rfc8785-jcs",
            "line_endings": "not_applicable",
        }

    expected = {
        "heading_text": record.selector["heading_text"],
        "occurrence": 1,
    }
    if output.selector_type != "heading" or output.transformation != expected:
        _contract_failure("heading selector transformation is inconsistent")
    return {
        "type": "heading_bounded_excerpt",
        "start_heading": record.selector["heading_text"],
        "occurrence": 1,
        "end_rule": "before_next_atx_heading_of_equal_or_greater_level_or_eof",
        "source_line_endings": output.source_line_endings,
        "content_change": "none",
    }


def _freshness(
    record: SelectedSourcePlan,
    output: SelectorOutput,
    as_of: str,
) -> FreshnessRecord:
    if record.rule_id == "S020-current-mission-milestone":
        return FreshnessRecord(
            status="unknown",
            basis=(
                "The exact Current Mission source is established at the pinned "
                "snapshot, but the compilation inputs contain no independent "
                "synchronization finding proving semantic alignment."
            ),
            rule="F020-current-mission-synchronization-unverified",
            as_of=as_of,
        )

    if record.rule_id == "S010-explicit-opportunity-anchor":
        try:
            selected = json.loads(output.content.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            _contract_failure("selected opportunity payload is not canonical JSON")
        if (
            not isinstance(selected, dict)
            or selected.get("id") != "EO-2026-013"
            or selected.get("status") != "reviewed"
            or record.path != _OPPORTUNITY_PATH
            or record.structured_object_identity
            != "engineering-opportunity:EO-2026-013"
            or record.canonical_owner != _OPPORTUNITY_OWNER
            or record.authority_class != "structured_repository_object"
            or record.source_kind != "repository_object"
        ):
            _contract_failure(
                "selected opportunity freshness evidence is unsupported"
            )
        return FreshnessRecord(
            status="current_at_snapshot",
            basis=(
                "The registered Engineering Opportunity object is read from the "
                "exact requested snapshot, its source path, structured identity, "
                "and field-contract owner match, and the accepted selected "
                "lifecycle value is reviewed."
            ),
            rule="F010-pinned-canonical-source",
            as_of=as_of,
        )

    if record.rule_id not in _ORDINARY_CANONICAL_RULES:
        _contract_failure("selected freshness class is unsupported")
    return FreshnessRecord(
        status="current_at_snapshot",
        basis=(
            "The selected canonical document is read from the exact requested "
            "snapshot, its canonical owner matches its normalized path, and no "
            "blocking B1b2 record exists for the boundary."
        ),
        rule="F010-pinned-canonical-source",
        as_of=as_of,
    )


def materialize_selection_plan(
    *,
    target_repository: str | pathlib.Path,
    request: CompilationRequest,
    snapshot: RepositorySnapshot,
    selection_plan: SelectionPlan,
) -> MaterializationResult:
    """Materialize one accepted B1b2 plan without budget or package work."""

    _validate_input_contract(
        target_repository=target_repository,
        request=request,
        snapshot=snapshot,
        selection_plan=selection_plan,
    )

    sources: list[MaterializedSource] = []
    payloads: list[MaterializedPayload] = []
    source_ids: set[str] = set()
    payload_ids: set[str] = set()

    for record in selection_plan.selected:
        try:
            blob = read_snapshot_blob(
                target_repository,
                snapshot,
                record.path,
            )
        except SnapshotError as error:
            raise MaterializationSourceError(
                f"accepted immutable source reread failed for rule {record.rule_id}"
            ) from error

        if (
            blob.path != record.path
            or blob.mode != record.mode
            or blob.object_format != record.object_format
            or blob.object_id != record.blob
        ):
            _identity_failure(
                f"immutable source identity disagrees for rule {record.rule_id}"
            )

        descriptor, output = _execute_selector(record, blob.content)
        source_digest = byte_digest(blob.content)
        payload_digest = byte_digest(output.content)
        source_id = source_identifier(
            record.path,
            record.commit,
            record.blob,
            descriptor,
        )
        payload_id = payload_identifier(payload_digest.value)

        if source_id in source_ids:
            _identity_failure("source identifier collision")
        if payload_id in payload_ids:
            _identity_failure("payload identifier collision")
        source_ids.add(source_id)
        payload_ids.add(payload_id)

        payload = MaterializedPayload(
            id=payload_id,
            source_ref=source_id,
            media_type=output.media_type,
            encoding=output.encoding,
            content=output.content,
            utf8_bytes=len(output.content),
            digest=payload_digest,
        )
        source = MaterializedSource(
            id=source_id,
            plan=record,
            selector_descriptor=descriptor,
            immutable_source_identity=ImmutableSourceIdentityRecord(
                type="git_blob",
                object_format=blob.object_format,
                value=blob.object_id,
            ),
            source_content_digest=source_digest,
            transformation=_transformation(record, output),
            freshness=_freshness(record, output, request.as_of),
            included_utf8_bytes=len(output.content),
            payload_ref=payload_id,
        )
        if payload.source_ref != source.id or source.payload_ref != payload.id:
            _identity_failure("source and payload linkage is inconsistent")
        sources.append(source)
        payloads.append(payload)

    omissions: list[IdentifiedOmission] = []
    omission_ids: set[str] = set()
    for record in selection_plan.omissions:
        identifier = omission_identifier(
            record.exclusion_rule_id,
            record.boundary,
            record.individual,
        )
        if identifier in omission_ids:
            _identity_failure("omission identifier collision")
        omission_ids.add(identifier)
        omissions.append(IdentifiedOmission(identifier, record))

    return MaterializationResult(
        request_task_id=selection_plan.request_task_id,
        repository_identity=selection_plan.repository_identity,
        requested_revision=selection_plan.requested_revision,
        commit=selection_plan.commit,
        tree=selection_plan.tree,
        object_format=selection_plan.object_format,
        snapshot_mode=selection_plan.snapshot_mode,
        snapshot_fingerprint=selection_plan.snapshot_fingerprint,
        sources=tuple(sources),
        payloads=tuple(payloads),
        omissions=tuple(omissions),
        unknowns=selection_plan.unknowns,
    )


__all__ = (
    "MaterializationError",
    "MaterializationContractError",
    "MaterializationIdentityError",
    "MaterializationSourceError",
    "materialize_selection_plan",
)
