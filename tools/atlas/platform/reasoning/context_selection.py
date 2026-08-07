"""Bounded deterministic source-selection reasoning for EO-2026-013 B1b2."""

from __future__ import annotations

import pathlib
from collections.abc import Mapping, Sequence
from typing import Any

from atlas.platform.context_compilation.canonical_json import canonicalize
from atlas.platform.context_compilation.digests import (
    selection_policy_digest,
    snapshot_fingerprint,
)
from atlas.platform.context_compilation.models import (
    CompilationRequest,
    ImmutableBlob,
    LoadedPolicy,
    RepositorySnapshot,
    SelectedSourcePlan,
    SelectionOmissionPlan,
    SelectionPlan,
    SelectionUnknownPlan,
)
from atlas.platform.context_compilation.selectors import (
    SelectorContractError,
    SelectorEncodingError,
    SelectorNotFoundError,
    SelectorSyntaxError,
    parse_bounded_yaml_mapping,
    select_markdown_heading,
    select_yaml_fields,
)
from atlas.platform.context_compilation.snapshot import (
    BlobLookupError,
    RepositoryPathError,
    SnapshotError,
    normalize_repository_path,
    read_snapshot_blob,
)


_REQUEST_SCHEMA = "aiden.task-context.compilation-request/v1"
_POLICY_ID = "example.read-only-architecture-assessment"
_POLICY_VERSION = "1.0.1"
_POLICY_DIGEST = "69577722ea4eb6f479424f3bf324866cc2992d5df82b3224e5f20571ef081938"
_CANONICAL_REPOSITORY_IDENTITY = "github.com/aidenm727/aiden-platform"
_TASK_TYPE = "architecture_assessment"
_TASK_PROFILE = "eo-architecture-assessment"
_OPPORTUNITY_PATH = (
    "docs/opportunities/reviewed/"
    "EO-2026-013-task-scoped-agent-context-compilation.yaml"
)
_MISSION_PATH = "docs/current-mission.md"
_SNAPSHOT_MODE = "clean_committed"
_OBJECT_FORMAT = "sha1"
_MAXIMUM_SENSITIVITY = "ordinary_personal"
_EXPECTED_ORDERING = (
    "priority_tier",
    "selection_rule_id",
    "normalized_path_or_object_id",
    "selector",
)
_EXPECTED_CANDIDATE_UNIVERSE = (
    "explicit_request_anchors",
    "exact_task_profile_candidates",
    "allowlisted_one_hop_relationship_candidates",
)


def _expected_relationship() -> Mapping[str, Any]:
    return {
        "max_hops": 1,
        "allowlisted": (
            {
                "type": "related_documents",
                "direction": "outbound",
            },
        ),
    }


_SENSITIVITY_ORDER = (
    "public",
    "ordinary_personal",
    "sensitive",
    "highly_restricted",
)


class SelectionError(ValueError):
    """Base class for bounded deterministic selection failures."""


class SelectionContractError(SelectionError):
    """The caller supplied an unsupported or contradictory selection contract."""


def _rule_contracts() -> tuple[Mapping[str, Any], ...]:
    return (
        {
            "id": "S010-explicit-opportunity-anchor",
            "type": "explicit_anchor",
            "priority_tier": 10,
            "budget_tier": "mandatory_authoritative_sources",
            "source": {
                "kind": "repository_object",
                "sensitivity": "public",
                "object_type": "engineering-opportunity",
                "field_contract_owner": (
                    "docs/architecture/engineering-opportunity-object.md"
                ),
            },
            "selector": {
                "type": "yaml_fields",
                "fields": ("id", "title", "status", "summary"),
            },
        },
        {
            "id": "S020-current-mission-milestone",
            "type": "explicit_anchor",
            "priority_tier": 10,
            "budget_tier": "mandatory_authoritative_sources",
            "source": {
                "kind": "document",
                "sensitivity": "public",
                "path": _MISSION_PATH,
            },
            "selector": {
                "type": "heading",
                "heading_text": "## Initial Milestone",
                "occurrence": 1,
            },
        },
        {
            "id": "S030-canonical-repository-authority",
            "type": "allowlisted_relationship",
            "priority_tier": 20,
            "budget_tier": "required_supporting_sources",
            "source": {
                "kind": "document",
                "sensitivity": "public",
                "path": "docs/architecture/repository.md",
            },
            "selector": {
                "type": "heading",
                "heading_text": "## Source of Truth Hierarchy",
                "occurrence": 1,
            },
        },
        {
            "id": "S040-mandatory-knowledge-authority",
            "type": "task_profile",
            "priority_tier": 30,
            "budget_tier": "required_supporting_sources",
            "source": {
                "kind": "document",
                "sensitivity": "public",
                "path": "docs/architecture/knowledge-authority.md",
            },
            "selector": {
                "type": "heading",
                "heading_text": "### Generated Context",
                "occurrence": 1,
            },
        },
        {
            "id": "S050-mandatory-collaboration",
            "type": "allowlisted_relationship",
            "priority_tier": 30,
            "budget_tier": "required_supporting_sources",
            "source": {
                "kind": "document",
                "sensitivity": "public",
                "path": "docs/standards/engineering-collaboration.md",
            },
            "selector": {
                "type": "heading",
                "heading_text": "## Responsibilities",
                "occurrence": 1,
            },
        },
    )


def _fail(message: str) -> None:
    raise SelectionContractError(message)


def _mapping(value: Any, message: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail(message)
    return value


def _sequence(value: Any, message: str) -> tuple[Any, ...]:
    if not isinstance(value, Sequence) or isinstance(
        value, (str, bytes, bytearray, memoryview)
    ):
        _fail(message)
    return tuple(value)


def _known_task_value(request: CompilationRequest, field: str) -> Any:
    record = _mapping(request.task.get(field), f"task {field} contract is invalid")
    if record.get("state") != "known" or "value" not in record:
        _fail(f"task {field} must be known")
    return record["value"]


def _validate_request_and_snapshot(
    request: CompilationRequest,
    snapshot: RepositorySnapshot,
) -> str:
    if request.schema_version != _REQUEST_SCHEMA:
        _fail("request schema is unsupported")
    if (
        request.repository.identity != _CANONICAL_REPOSITORY_IDENTITY
        or snapshot.repository.requested_identity != _CANONICAL_REPOSITORY_IDENTITY
        or snapshot.repository.normalized_identity != _CANONICAL_REPOSITORY_IDENTITY
    ):
        _fail("request and snapshot repository identities do not match")
    if (
        request.repository.requested_revision != snapshot.requested_revision
        or request.repository.requested_revision != snapshot.commit
    ):
        _fail("request and snapshot revisions do not match")
    if (
        snapshot.snapshot_mode != _SNAPSHOT_MODE
        or snapshot.object_format != _OBJECT_FORMAT
    ):
        _fail("snapshot contract is unsupported")
    expected_fingerprint = snapshot_fingerprint(
        snapshot.repository.normalized_identity,
        snapshot.object_format,
        snapshot.commit,
        snapshot.tree,
        snapshot.snapshot_mode,
    )
    if expected_fingerprint != snapshot.fingerprint:
        _fail("snapshot fingerprint is inconsistent")

    task_id = _known_task_value(request, "id")
    if not isinstance(task_id, str) or not task_id:
        _fail("task id contract is invalid")
    task_type = _known_task_value(request, "type")
    if task_type != _TASK_TYPE:
        _fail("task type is unsupported")

    opportunity_references = _sequence(
        _known_task_value(request, "opportunity_references"),
        "opportunity reference contract is invalid",
    )
    if opportunity_references != (_OPPORTUNITY_PATH,):
        _fail("opportunity reference contract is unsupported")
    mission_references = _sequence(
        _known_task_value(request, "mission_references"),
        "mission reference contract is invalid",
    )
    if mission_references != (_MISSION_PATH,):
        _fail("mission reference contract is unsupported")
    return task_id


def _validate_policy(
    request: CompilationRequest,
    selection_policy: LoadedPolicy,
) -> tuple[Mapping[str, Any], ...]:
    reference = selection_policy.reference
    if request.selection_policy != reference:
        _fail("request and loaded selection policy do not match")
    if (
        reference.id != _POLICY_ID
        or reference.version != _POLICY_VERSION
        or reference.digest.algorithm != "sha256"
        or reference.digest.canonicalization != "rfc8785-jcs"
        or reference.digest.value != _POLICY_DIGEST
    ):
        _fail("selection policy identity is unsupported")
    if selection_policy_digest(selection_policy.value) != reference.digest:
        _fail("selection policy digest does not match its value")

    value = selection_policy.value
    policy_digest = _mapping(value.get("digest"), "policy digest contract is invalid")
    if (
        policy_digest.get("algorithm") != reference.digest.algorithm
        or policy_digest.get("canonicalization") != reference.digest.canonicalization
        or policy_digest.get("value") != reference.digest.value
    ):
        _fail("loaded policy digest record is inconsistent")
    if value.get("schema_version") != "aiden.task-context.selection-policy/v1":
        _fail("selection policy schema is unsupported")
    if (
        value.get("id") != _POLICY_ID
        or value.get("version") != _POLICY_VERSION
        or value.get("task_profile") != _TASK_PROFILE
    ):
        _fail("selection policy profile is unsupported")
    if canonicalize(value.get("relationship_traversal")) != canonicalize(
        _expected_relationship()
    ):
        _fail("relationship traversal contract is unsupported")
    if tuple(value.get("source_ordering", ())) != _EXPECTED_ORDERING:
        _fail("source ordering contract is unsupported")
    if value.get("maximum_sensitivity") != _MAXIMUM_SENSITIVITY:
        _fail("maximum sensitivity contract is unsupported")
    if tuple(value.get("omission_candidate_universe", ())) != (
        _EXPECTED_CANDIDATE_UNIVERSE
    ):
        _fail("omission candidate universe is unsupported")

    rules = _sequence(value.get("rules"), "selection rules contract is invalid")
    expected = _rule_contracts()
    if len(rules) != len(expected):
        _fail("selection policy must contain exactly five rules")
    rule_ids: set[str] = set()
    validated: list[Mapping[str, Any]] = []
    for actual, required in zip(rules, expected):
        actual_mapping = _mapping(actual, "selection rule contract is invalid")
        rule_id = actual_mapping.get("id")
        if not isinstance(rule_id, str) or rule_id in rule_ids:
            _fail("selection rule identifiers must be unique")
        rule_ids.add(rule_id)
        if canonicalize(actual_mapping) != canonicalize(required):
            _fail("selection rule contract is unsupported")
        validated.append(actual_mapping)

    exclusions = _sequence(
        value.get("exclusion_rules"), "exclusion rule contract is invalid"
    )
    exclusion_by_id: dict[str, Mapping[str, Any]] = {}
    for record in exclusions:
        mapping = _mapping(record, "exclusion rule contract is invalid")
        identifier = mapping.get("id")
        if not isinstance(identifier, str) or identifier in exclusion_by_id:
            _fail("exclusion rule identifiers must be unique")
        exclusion_by_id[identifier] = mapping
    if (
        exclusion_by_id.get("X050-disallowed-sensitivity", {}).get("type")
        != "sensitivity"
        or exclusion_by_id.get("X060-unsupported-binary", {}).get("type")
        != "unsupported_binary"
    ):
        _fail("required exclusion rules are unsupported")
    return tuple(validated)


def _path_for_rule(
    rule: Mapping[str, Any],
    request: CompilationRequest,
) -> str:
    rule_id = rule["id"]
    if rule_id == "S010-explicit-opportunity-anchor":
        value = _known_task_value(request, "opportunity_references")
        path = _sequence(value, "opportunity reference contract is invalid")[0]
    elif rule_id == "S020-current-mission-milestone":
        value = _known_task_value(request, "mission_references")
        path = _sequence(value, "mission reference contract is invalid")[0]
    else:
        source = _mapping(rule.get("source"), "rule source contract is invalid")
        path = source.get("path")
    try:
        return normalize_repository_path(path)
    except RepositoryPathError:
        _fail("candidate repository path is invalid")
    raise AssertionError("unreachable")


def _candidate_identity(path: str, selector: Mapping[str, Any]) -> tuple[str, bytes]:
    return path, canonicalize(selector)


def _validate_distinct_candidates(
    rules: tuple[Mapping[str, Any], ...],
    request: CompilationRequest,
) -> None:
    seen: set[tuple[str, bytes]] = set()
    stable_keys: set[tuple[int, str, str, bytes]] = set()
    for rule in rules:
        path = _path_for_rule(rule, request)
        selector = _mapping(rule.get("selector"), "selector contract is invalid")
        identity = _candidate_identity(path, selector)
        if identity in seen:
            _fail("duplicate candidate identity is unsupported")
        seen.add(identity)
        key = (rule["priority_tier"], rule["id"], path, canonicalize(selector))
        if key in stable_keys:
            _fail("stable ordering tie is unsupported")
        stable_keys.add(key)


def _blocking(rule: Mapping[str, Any]) -> bool:
    tier = rule.get("budget_tier")
    if tier not in (
        "mandatory_authoritative_sources",
        "required_supporting_sources",
    ):
        _fail("budget tier contract is unsupported")
    return True


def _candidate_metadata(
    rule: Mapping[str, Any],
) -> tuple[str, str, str | None, str]:
    rule_id = rule["id"]
    if rule_id == "S010-explicit-opportunity-anchor":
        return (
            "structured_repository_object",
            "docs/architecture/engineering-opportunity-object.md",
            "engineering-opportunity:EO-2026-013",
            "explicit_opportunity_reference",
        )
    if rule_id == "S020-current-mission-milestone":
        return (
            "canonical_document",
            _MISSION_PATH,
            None,
            "explicit_mission_reference",
        )
    if rule_id == "S030-canonical-repository-authority":
        return (
            "canonical_document",
            "docs/architecture/repository.md",
            None,
            "allowlisted_related_document",
        )
    if rule_id == "S040-mandatory-knowledge-authority":
        return (
            "canonical_document",
            "docs/architecture/knowledge-authority.md",
            None,
            "task_profile_required_source",
        )
    if rule_id == "S050-mandatory-collaboration":
        return (
            "canonical_document",
            "docs/standards/engineering-collaboration.md",
            None,
            "allowlisted_related_document",
        )
    _fail("selection rule is unsupported")
    raise AssertionError("unreachable")


def _trigger_and_chain(
    rule: Mapping[str, Any],
    path: str,
) -> tuple[str, tuple[str, ...]]:
    rule_id = rule["id"]
    if rule_id == "S010-explicit-opportunity-anchor":
        trigger = "task.opportunity_references[0]"
        return trigger, (trigger, rule_id)
    if rule_id == "S020-current-mission-milestone":
        trigger = "task.mission_references[0]"
        return trigger, (trigger, rule_id)
    if rule_id in (
        "S030-canonical-repository-authority",
        "S050-mandatory-collaboration",
    ):
        trigger = "task.opportunity_references[0]"
        return trigger, (
            trigger,
            "related_documents:outbound",
            path,
            rule_id,
        )
    if rule_id == "S040-mandatory-knowledge-authority":
        trigger = "task.type=architecture_assessment"
        return trigger, (
            trigger,
            "task_profile=eo-architecture-assessment",
            rule_id,
        )
    _fail("selection rule is unsupported")
    raise AssertionError("unreachable")


def _individual_identity(
    path: str,
    structured_object_identity: str | None,
    selector: Mapping[str, Any],
) -> Mapping[str, Any]:
    return {
        "path": path,
        "structured_object_identity": structured_object_identity,
        "selector": selector,
    }


def _omission(
    rule: Mapping[str, Any],
    path: str,
    *,
    exclusion_rule_id: str,
    reason: str,
    consequence: str,
    reconsideration_condition: str,
) -> SelectionOmissionPlan:
    _, _, structured_identity, _ = _candidate_metadata(rule)
    trigger, chain = _trigger_and_chain(rule, path)
    selector = _mapping(rule["selector"], "selector contract is invalid")
    return SelectionOmissionPlan(
        rule_id=rule["id"],
        exclusion_rule_id=exclusion_rule_id,
        boundary=path,
        individual=_individual_identity(path, structured_identity, selector),
        trigger=trigger,
        selection_chain=chain,
        reason=reason,
        consequence=consequence,
        blocking=_blocking(rule),
        reconsideration_condition=reconsideration_condition,
    )


def _unknown(
    rule: Mapping[str, Any],
    path: str,
    *,
    field: str,
    attempted_resolution: str,
    consequence: str,
) -> SelectionUnknownPlan:
    authority_class, owner, _, _ = _candidate_metadata(rule)
    del authority_class
    trigger, chain = _trigger_and_chain(rule, path)
    return SelectionUnknownPlan(
        rule_id=rule["id"],
        boundary=path,
        field=field,
        attempted_resolution=attempted_resolution,
        owner=owner,
        trigger=trigger,
        selection_chain=chain,
        consequence=consequence,
        blocking=_blocking(rule),
    )


def _above_sensitivity_ceiling(rule: Mapping[str, Any]) -> bool:
    source = _mapping(rule.get("source"), "rule source contract is invalid")
    sensitivity = source.get("sensitivity")
    try:
        actual = _SENSITIVITY_ORDER.index(sensitivity)
        maximum = _SENSITIVITY_ORDER.index(_MAXIMUM_SENSITIVITY)
    except ValueError:
        _fail("source sensitivity contract is unsupported")
    return actual > maximum


def _read_blob(
    target_repository: str | pathlib.Path,
    snapshot: RepositorySnapshot,
    rule: Mapping[str, Any],
    path: str,
) -> tuple[ImmutableBlob | None, SelectionOmissionPlan | SelectionUnknownPlan | None]:
    if _above_sensitivity_ceiling(rule):
        return None, _omission(
            rule,
            path,
            exclusion_rule_id="X050-disallowed-sensitivity",
            reason="source_above_sensitivity_ceiling",
            consequence="required source is unavailable for compilation",
            reconsideration_condition=(
                "Use a policy with an authoritatively approved sensitivity ceiling."
            ),
        )
    try:
        return read_snapshot_blob(target_repository, snapshot, path), None
    except BlobLookupError:
        return None, _unknown(
            rule,
            path,
            field="immutable_blob",
            attempted_resolution="Read the exact regular blob from the accepted snapshot.",
            consequence="required source identity could not be established",
        )
    except SnapshotError:
        _fail("snapshot access failed")
    raise AssertionError("unreachable")


def _apply_selector(
    rule: Mapping[str, Any],
    blob: ImmutableBlob,
) -> None:
    selector = _mapping(rule.get("selector"), "selector contract is invalid")
    selector_type = selector.get("type")
    try:
        if selector_type == "yaml_fields":
            fields = _sequence(selector.get("fields"), "selector fields are invalid")
            select_yaml_fields(blob.content, fields)
            return
        if selector_type == "heading":
            select_markdown_heading(
                blob.content,
                selector.get("heading_text"),
                selector.get("occurrence"),
            )
            return
    except SelectorContractError:
        _fail("policy selector contract is unsupported")
    if selector_type not in ("yaml_fields", "heading"):
        _fail("policy selector type is unsupported")


def _selected(
    rule: Mapping[str, Any],
    path: str,
    snapshot: RepositorySnapshot,
    blob: ImmutableBlob,
) -> SelectedSourcePlan:
    authority_class, owner, structured_identity, reason = _candidate_metadata(rule)
    trigger, chain = _trigger_and_chain(rule, path)
    source = _mapping(rule["source"], "rule source contract is invalid")
    selector = _mapping(rule["selector"], "selector contract is invalid")
    return SelectedSourcePlan(
        rule_id=rule["id"],
        rule_type=rule["type"],
        priority_tier=rule["priority_tier"],
        budget_tier=rule["budget_tier"],
        source_kind=source["kind"],
        sensitivity=source["sensitivity"],
        path=path,
        structured_object_identity=structured_identity,
        normalized_path_or_object_id=structured_identity or path,
        selector=selector,
        selection_reason=reason,
        trigger=trigger,
        selection_chain=chain,
        authority_class=authority_class,
        canonical_owner=owner,
        commit=snapshot.commit,
        mode=blob.mode,
        object_format=blob.object_format,
        blob=blob.object_id,
    )


def _evaluate_candidate(
    target_repository: str | pathlib.Path,
    snapshot: RepositorySnapshot,
    rule: Mapping[str, Any],
    path: str,
) -> tuple[
    SelectedSourcePlan | None,
    SelectionOmissionPlan | None,
    SelectionUnknownPlan | None,
    ImmutableBlob | None,
]:
    blob, access_result = _read_blob(target_repository, snapshot, rule, path)
    if isinstance(access_result, SelectionOmissionPlan):
        return None, access_result, None, None
    if isinstance(access_result, SelectionUnknownPlan):
        return None, None, access_result, None
    assert blob is not None
    try:
        _apply_selector(rule, blob)
    except SelectorEncodingError:
        return (
            None,
            _omission(
                rule,
                path,
                exclusion_rule_id="X060-unsupported-binary",
                reason="unsupported_text_source",
                consequence="required source cannot enter the deterministic text domain",
                reconsideration_condition=(
                    "Provide source bytes accepted by the bounded UTF-8 text contract."
                ),
            ),
            None,
            blob,
        )
    except SelectorNotFoundError:
        return (
            None,
            None,
            _unknown(
                rule,
                path,
                field="selector_target",
                attempted_resolution="Apply the exact digest-bound selector.",
                consequence="required selector target could not be established",
            ),
            blob,
        )
    except SelectorSyntaxError:
        return (
            None,
            None,
            _unknown(
                rule,
                path,
                field="source_syntax",
                attempted_resolution="Parse the source through the bounded selector grammar.",
                consequence="required structured source facts could not be established",
            ),
            blob,
        )
    return _selected(rule, path, snapshot, blob), None, None, blob


def _append_result(
    result: tuple[
        SelectedSourcePlan | None,
        SelectionOmissionPlan | None,
        SelectionUnknownPlan | None,
        ImmutableBlob | None,
    ],
    selected: list[SelectedSourcePlan],
    omissions: list[SelectionOmissionPlan],
    unknowns: list[SelectionUnknownPlan],
) -> ImmutableBlob | None:
    selected_record, omission_record, unknown_record, blob = result
    if selected_record is not None:
        selected.append(selected_record)
    if omission_record is not None:
        omissions.append(omission_record)
    if unknown_record is not None:
        unknowns.append(unknown_record)
    return blob


def _relationship_unknown(
    rule: Mapping[str, Any],
    path: str,
) -> SelectionUnknownPlan:
    return _unknown(
        rule,
        path,
        field="related_documents",
        attempted_resolution=(
            "Parse the explicit Engineering Opportunity related_documents field."
        ),
        consequence="relationship traversal authority could not be established",
    )


def _evaluate_opportunity(
    target_repository: str | pathlib.Path,
    snapshot: RepositorySnapshot,
    rule: Mapping[str, Any],
    path: str,
    selected: list[SelectedSourcePlan],
    omissions: list[SelectionOmissionPlan],
    unknowns: list[SelectionUnknownPlan],
) -> tuple[str, ...] | None:
    blob, access_result = _read_blob(target_repository, snapshot, rule, path)
    if isinstance(access_result, SelectionOmissionPlan):
        omissions.append(access_result)
        return None
    if isinstance(access_result, SelectionUnknownPlan):
        unknowns.append(access_result)
        return None
    assert blob is not None

    try:
        parsed = parse_bounded_yaml_mapping(blob.content)
    except SelectorEncodingError:
        omissions.append(
            _omission(
                rule,
                path,
                exclusion_rule_id="X060-unsupported-binary",
                reason="unsupported_text_source",
                consequence="required source cannot enter the deterministic text domain",
                reconsideration_condition=(
                    "Provide source bytes accepted by the bounded UTF-8 text contract."
                ),
            )
        )
        return None
    except SelectorSyntaxError:
        unknowns.append(
            _unknown(
                rule,
                path,
                field="source_syntax",
                attempted_resolution=(
                    "Parse the Engineering Opportunity through the bounded YAML grammar."
                ),
                consequence="required repository-object facts could not be established",
            )
        )
        return None

    object_id = parsed.get("id")
    if object_id is None:
        unknowns.append(
            _unknown(
                rule,
                path,
                field="id",
                attempted_resolution="Read the Engineering Opportunity id field.",
                consequence="repository-object identity could not be established",
            )
        )
        return None
    if object_id != "EO-2026-013":
        _fail("opportunity object identity contradicts the request")

    try:
        _apply_selector(rule, blob)
    except SelectorNotFoundError:
        unknowns.append(
            _unknown(
                rule,
                path,
                field="selector_target",
                attempted_resolution="Apply the exact digest-bound YAML field selector.",
                consequence="required selector target could not be established",
            )
        )
    except SelectorContractError:
        _fail("policy selector contract is unsupported")
    else:
        selected.append(_selected(rule, path, snapshot, blob))

    related = parsed.get("related_documents")
    if not isinstance(related, tuple) or not all(
        isinstance(item, str) for item in related
    ):
        return None
    return related


def _sort_selected(record: SelectedSourcePlan) -> tuple[int, str, str, bytes]:
    return (
        record.priority_tier,
        record.rule_id,
        record.normalized_path_or_object_id,
        canonicalize(record.selector),
    )


def _sort_trace(
    record: SelectionOmissionPlan | SelectionUnknownPlan,
) -> tuple[str, str]:
    return record.rule_id, record.boundary


def build_bounded_selection_plan(
    *,
    target_repository: str | pathlib.Path,
    request: CompilationRequest,
    selection_policy: LoadedPolicy,
    snapshot: RepositorySnapshot,
) -> SelectionPlan:
    """Build one immutable five-rule selection plan without compiling payloads."""

    if not isinstance(target_repository, (str, pathlib.Path)):
        _fail("target repository must be an explicit path")
    if not isinstance(request, CompilationRequest):
        _fail("request must be a CompilationRequest")
    if not isinstance(selection_policy, LoadedPolicy):
        _fail("selection_policy must be a LoadedPolicy")
    if not isinstance(snapshot, RepositorySnapshot):
        _fail("snapshot must be a RepositorySnapshot")

    task_id = _validate_request_and_snapshot(request, snapshot)
    rules = _validate_policy(request, selection_policy)
    _validate_distinct_candidates(rules, request)

    selected: list[SelectedSourcePlan] = []
    omissions: list[SelectionOmissionPlan] = []
    unknowns: list[SelectionUnknownPlan] = []

    rule_by_id = {rule["id"]: rule for rule in rules}
    opportunity_rule = rule_by_id["S010-explicit-opportunity-anchor"]
    opportunity_path = _path_for_rule(opportunity_rule, request)
    relationships = _evaluate_opportunity(
        target_repository,
        snapshot,
        opportunity_rule,
        opportunity_path,
        selected,
        omissions,
        unknowns,
    )

    mission_rule = rule_by_id["S020-current-mission-milestone"]
    _append_result(
        _evaluate_candidate(
            target_repository,
            snapshot,
            mission_rule,
            _path_for_rule(mission_rule, request),
        ),
        selected,
        omissions,
        unknowns,
    )

    for rule_id in (
        "S030-canonical-repository-authority",
        "S050-mandatory-collaboration",
    ):
        rule = rule_by_id[rule_id]
        path = _path_for_rule(rule, request)
        if relationships is None:
            unknowns.append(_relationship_unknown(rule, path))
            continue
        if path not in relationships:
            omissions.append(
                _omission(
                    rule,
                    path,
                    exclusion_rule_id="relationship_not_declared",
                    reason="required_relationship_absent",
                    consequence=(
                        "required supporting source lacks traversal authority"
                    ),
                    reconsideration_condition=(
                        "Add the exact reviewed related_documents edge to the "
                        "authoritative Engineering Opportunity."
                    ),
                )
            )
            continue
        _append_result(
            _evaluate_candidate(target_repository, snapshot, rule, path),
            selected,
            omissions,
            unknowns,
        )

    profile_rule = rule_by_id["S040-mandatory-knowledge-authority"]
    _append_result(
        _evaluate_candidate(
            target_repository,
            snapshot,
            profile_rule,
            _path_for_rule(profile_rule, request),
        ),
        selected,
        omissions,
        unknowns,
    )

    selected.sort(key=_sort_selected)
    omissions.sort(key=_sort_trace)
    unknowns.sort(key=_sort_trace)

    return SelectionPlan(
        request_task_id=task_id,
        selection_policy_id=selection_policy.reference.id,
        selection_policy_version=selection_policy.reference.version,
        selection_policy_digest=selection_policy.reference.digest,
        repository_identity=snapshot.repository.normalized_identity,
        requested_revision=snapshot.requested_revision,
        commit=snapshot.commit,
        tree=snapshot.tree,
        object_format=snapshot.object_format,
        snapshot_mode=snapshot.snapshot_mode,
        snapshot_fingerprint=snapshot.fingerprint,
        selected=tuple(selected),
        omissions=tuple(omissions),
        unknowns=tuple(unknowns),
    )


__all__ = (
    "SelectionError",
    "SelectionContractError",
    "build_bounded_selection_plan",
)
