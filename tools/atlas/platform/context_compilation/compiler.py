"""Pure deterministic context-package compilation for EO-2026-013 B2b."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from atlas.platform.context_compilation.canonical_json import canonicalize
from atlas.platform.context_compilation.digests import (
    budget_policy_digest,
    byte_digest,
    control_envelope_bytes,
    omission_identifier,
    package_digest,
    package_identity,
    payload_identifier,
    request_digest,
    snapshot_fingerprint,
    source_identifier,
    unknown_identifier,
)
from atlas.platform.context_compilation.models import (
    CompilationRequest,
    CompilationResult,
    LoadedPolicy,
    MaterializationResult,
    MaterializedPayload,
    MaterializedSource,
    RepositorySnapshot,
)
from atlas.platform.context_compilation.validation import (
    BUDGET_CAPACITY_OMISSION_RULE,
    BUDGET_CAPACITY_OMISSION_REASON,
    BUDGET_CAPACITY_RECONSIDERATION,
    BUDGET_POLICY_DIGEST_VALUE,
    BUDGET_POLICY_ID,
    BUDGET_POLICY_VERSION,
    FIRST_SLICE_RULE_CONTRACT,
    SELECTION_POLICY_DIGEST_VALUE,
    SELECTION_POLICY_ID,
    SELECTION_POLICY_VERSION,
    budget_capacity_consequence,
    consumer_contract_value,
    executable_validation_value,
    fixed_first_slice_freshness,
    fixed_first_slice_rule,
    fixed_first_slice_selector,
    fixed_first_slice_transformation_matches,
    require_valid,
    validate_budget_policy,
    validate_compilation_request,
    validate_compiled_context_package,
)


_REQUEST_SCHEMA_VERSION = "aiden.task-context.compilation-request/v1"
_PACKAGE_SCHEMA_VERSION = "aiden.task-context/v1"
_SNAPSHOT_MODE = "clean_committed"
_OBJECT_FORMAT = "sha1"


class CompilationContractError(ValueError):
    """Raised when supplied typed inputs do not form one accepted B2b boundary."""


def _fail(message: str) -> None:
    raise CompilationContractError(message)


def _mutable_json_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _mutable_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_mutable_json_value(item) for item in value]
    return value


def _normalized_repository_path(value: str) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and not value.startswith("/")
        and "\\" not in value
        and "\x00" not in value
        and all(part not in ("", ".", "..") for part in value.split("/"))
    )


def _known_task_id(request: CompilationRequest) -> str:
    record = request.task.get("id")
    if not isinstance(record, Mapping) or record.get("state") != "known":
        _fail("request task id must be an explicit known declaration")
    task_id = record.get("value")
    if not isinstance(task_id, str) or not task_id:
        _fail("request task id value must be a nonempty string")
    return task_id


def _validate_protected_references(
    request: CompilationRequest,
    snapshot: RepositorySnapshot,
) -> None:
    if len(request.protected_references) != len(snapshot.protected_references):
        _fail("request and snapshot protected-reference boundaries do not match")
    for requested, resolved in zip(
        request.protected_references,
        snapshot.protected_references,
    ):
        expected = {
            "name": resolved.name,
            "expected_object": resolved.expected_object,
            "authoritatively_targeted": resolved.authoritatively_targeted,
            "selection": resolved.selection,
        }
        if _mutable_json_value(requested) != expected:
            _fail("request and snapshot protected-reference identities do not match")
        if (
            not resolved.matched
            or resolved.blocking
            or resolved.actual_object != resolved.expected_object
        ):
            _fail("snapshot contains a blocking protected-reference identity")


def _validate_inputs(
    *,
    request: CompilationRequest,
    budget_policy: LoadedPolicy,
    snapshot: RepositorySnapshot,
    materialization: MaterializationResult,
) -> None:
    if not isinstance(request, CompilationRequest):
        _fail("request must be a CompilationRequest")
    if not isinstance(budget_policy, LoadedPolicy):
        _fail("budget_policy must be a LoadedPolicy")
    if not isinstance(snapshot, RepositorySnapshot):
        _fail("snapshot must be a RepositorySnapshot")
    if not isinstance(materialization, MaterializationResult):
        _fail("materialization must be a MaterializationResult")

    try:
        require_valid(validate_compilation_request(_mutable_json_value(request.as_dict())))
        require_valid(validate_budget_policy(_mutable_json_value(budget_policy.value)))
    except ValueError as error:
        raise CompilationContractError(
            "request or budget policy violates the accepted structural contract"
        ) from error

    if request.schema_version != _REQUEST_SCHEMA_VERSION:
        _fail("request schema version is unsupported")
    expected_selection_reference = {
        "id": SELECTION_POLICY_ID,
        "version": SELECTION_POLICY_VERSION,
        "digest": {
            "algorithm": "sha256",
            "canonicalization": "rfc8785-jcs",
            "value": SELECTION_POLICY_DIGEST_VALUE,
        },
    }
    if request.selection_policy.as_dict() != expected_selection_reference:
        _fail("request selection-policy identity or digest is unsupported")
    expected_budget_reference = {
        "id": BUDGET_POLICY_ID,
        "version": BUDGET_POLICY_VERSION,
        "digest": {
            "algorithm": "sha256",
            "canonicalization": "rfc8785-jcs",
            "value": BUDGET_POLICY_DIGEST_VALUE,
        },
    }
    if (
        request.budget_policy.as_dict() != expected_budget_reference
        or budget_policy.reference.as_dict() != expected_budget_reference
        or budget_policy_digest(budget_policy.value).as_dict()
        != expected_budget_reference["digest"]
    ):
        _fail("loaded budget-policy identity or digest does not match the request")

    expected_fingerprint = snapshot_fingerprint(
        snapshot.repository.normalized_identity,
        snapshot.object_format,
        snapshot.commit,
        snapshot.tree,
        snapshot.snapshot_mode,
    )
    if snapshot.fingerprint != expected_fingerprint:
        _fail("snapshot fingerprint does not match its exact identity surface")
    if (
        request.repository.identity != snapshot.repository.requested_identity
        or request.repository.identity != snapshot.repository.normalized_identity
        or request.repository.requested_revision != snapshot.requested_revision
        or request.repository.requested_revision != snapshot.commit
        or snapshot.object_format != _OBJECT_FORMAT
        or snapshot.snapshot_mode != _SNAPSHOT_MODE
    ):
        _fail("request and snapshot repository identities do not agree")
    _validate_protected_references(request, snapshot)

    task_id = _known_task_id(request)
    if (
        materialization.request_task_id != task_id
        or materialization.repository_identity
        != snapshot.repository.normalized_identity
        or materialization.requested_revision != snapshot.requested_revision
        or materialization.commit != snapshot.commit
        or materialization.tree != snapshot.tree
        or materialization.object_format != snapshot.object_format
        or materialization.snapshot_mode != snapshot.snapshot_mode
        or materialization.snapshot_fingerprint != snapshot.fingerprint
    ):
        _fail("materialization identity does not match request and snapshot")
    _validate_materialization(materialization, request)


def _source_sort_key(source: MaterializedSource) -> tuple[int, str, str, bytes]:
    plan = source.plan
    return (
        plan.priority_tier,
        plan.rule_id,
        plan.normalized_path_or_object_id,
        canonicalize(plan.selector),
    )


def _validate_materialization(
    materialization: MaterializationResult,
    request: CompilationRequest,
) -> None:
    if len(materialization.sources) != len(materialization.payloads):
        _fail("materialization must contain exactly one payload per source")
    if tuple(materialization.sources) != tuple(
        sorted(materialization.sources, key=_source_sort_key)
    ):
        _fail("materialized sources are not in deterministic accepted order")
    if tuple(materialization.omissions) != tuple(
        sorted(
            materialization.omissions,
            key=lambda item: (item.plan.rule_id, item.plan.boundary),
        )
    ):
        _fail("materialized omissions are not in deterministic accepted order")
    if tuple(materialization.unknowns) != tuple(
        sorted(
            materialization.unknowns,
            key=lambda item: (item.rule_id, item.boundary),
        )
    ):
        _fail("materialized unknowns are not in deterministic accepted order")

    source_ids: set[str] = set()
    payload_ids: set[str] = set()
    seen_rules: set[str] = set()
    for source, payload in zip(
        materialization.sources,
        materialization.payloads,
    ):
        plan = source.plan
        rule = fixed_first_slice_rule(plan.rule_id)
        if rule is None:
            _fail("materialized source rule is outside the fixed first-slice policy")
        if plan.rule_id in seen_rules:
            _fail("materialized source rule is duplicated")
        seen_rules.add(plan.rule_id)
        if (
            plan.rule_type != rule.rule_type
            or plan.priority_tier != rule.priority_tier
            or plan.budget_tier != rule.budget_tier
            or plan.source_kind != rule.source_kind
            or plan.sensitivity != rule.sensitivity
            or plan.path != rule.path
            or plan.structured_object_identity
            != rule.structured_object_identity
            or plan.normalized_path_or_object_id != rule.normalized_identity
            or _mutable_json_value(plan.selector)
            != fixed_first_slice_selector(rule)
            or plan.selection_reason != rule.selection_reason
            or plan.trigger != rule.trigger
            or tuple(plan.selection_chain) != rule.selection_chain
            or plan.authority_class != rule.authority_class
            or plan.canonical_owner != rule.canonical_owner
        ):
            _fail(
                "materialized source changes a fixed first-slice policy or "
                "selection-trace value"
            )
        if not _normalized_repository_path(plan.path):
            _fail("materialized source path is not normalized")
        if (
            plan.commit != materialization.commit
            or plan.object_format != materialization.object_format
            or source.immutable_source_identity.type != "git_blob"
            or source.immutable_source_identity.object_format != plan.object_format
            or source.immutable_source_identity.value != plan.blob
        ):
            _fail("materialized source immutable identity is inconsistent")
        expected_source_id = source_identifier(
            plan.path,
            plan.commit,
            plan.blob,
            source.selector_descriptor,
        )
        expected_payload_digest = byte_digest(payload.content)
        expected_payload_id = payload_identifier(expected_payload_digest.value)
        if (
            source.id != expected_source_id
            or payload.id != expected_payload_id
            or payload.digest != expected_payload_digest
            or payload.utf8_bytes != len(payload.content)
            or source.included_utf8_bytes != len(payload.content)
            or source.payload_ref != payload.id
            or payload.source_ref != source.id
            or source.selector_descriptor != rule.selector_descriptor
            or payload.media_type != rule.media_type
            or payload.encoding != "utf-8"
            or source.freshness.as_dict()
            != fixed_first_slice_freshness(rule, request.as_of)
            or not fixed_first_slice_transformation_matches(
                rule,
                source.transformation,
                payload.content,
            )
        ):
            _fail("materialized source and payload identity or linkage is invalid")
        if source.source_content_digest.algorithm != "sha256":
            _fail("materialized source content digest is unsupported")
        if source.id in source_ids or payload.id in payload_ids:
            _fail("materialized source or payload identity is duplicated")
        source_ids.add(source.id)
        payload_ids.add(payload.id)

    expected_rules = {rule.rule_id for rule in FIRST_SLICE_RULE_CONTRACT}
    if seen_rules != expected_rules:
        _fail("materialization omits a fixed mandatory first-slice rule")

    omission_ids: set[str] = set()
    for omission in materialization.omissions:
        expected = omission_identifier(
            omission.plan.exclusion_rule_id,
            omission.plan.boundary,
            omission.plan.individual,
        )
        if omission.id != expected or omission.id in omission_ids:
            _fail("materialized omission identity is invalid or duplicated")
        omission_ids.add(omission.id)


def _source_value(source: MaterializedSource) -> dict[str, Any]:
    plan = source.plan
    return {
        "id": source.id,
        "path": plan.path,
        "structured_object_identity": plan.structured_object_identity,
        "selector": source.selector_descriptor,
        "priority_tier": plan.priority_tier,
        "selection_rule": plan.rule_id,
        "selection_reason": plan.selection_reason,
        "trigger": plan.trigger,
        "selection_chain": list(plan.selection_chain),
        "authority_class": plan.authority_class,
        "canonical_owner": plan.canonical_owner,
        "commit": plan.commit,
        "immutable_source_identity": source.immutable_source_identity.as_dict(),
        "source_content_digest": source.source_content_digest.as_dict(),
        "transformation": _mutable_json_value(source.transformation),
        "freshness": source.freshness.as_dict(),
        "included_utf8_bytes": source.included_utf8_bytes,
        "payload_ref": source.payload_ref,
    }


def _payload_value(payload: MaterializedPayload) -> dict[str, Any]:
    return {
        "id": payload.id,
        "source_ref": payload.source_ref,
        "media_type": payload.media_type,
        "encoding": payload.encoding,
        "content": payload.content.decode("utf-8", errors="strict"),
        "utf8_bytes": payload.utf8_bytes,
        "digest": payload.digest.as_dict(),
    }


def _existing_omission_value(omission: Any) -> dict[str, Any]:
    plan = omission.plan
    return {
        "id": omission.id,
        "record_type": "individual",
        "boundary": plan.boundary,
        "individual": _mutable_json_value(plan.individual),
        "rule": plan.exclusion_rule_id,
        "reason": plan.reason,
        "consequence": plan.consequence,
        "blocking": plan.blocking,
        "reconsideration_condition": plan.reconsideration_condition,
    }


def _unknown_value(unknown: Any) -> dict[str, Any]:
    return {
        "id": unknown_identifier(
            unknown.field,
            unknown.attempted_resolution,
            unknown.owner,
            unknown.consequence,
            unknown.blocking,
        ),
        "field": unknown.field,
        "attempted_resolution": unknown.attempted_resolution,
        "owner": unknown.owner,
        "consequence": unknown.consequence,
        "blocking": unknown.blocking,
    }


def _budget_omission_value(
    source: MaterializedSource,
    payload: MaterializedPayload,
) -> dict[str, Any]:
    individual = {
        "source_id": source.id,
        "payload_id": payload.id,
        "path": source.plan.path,
        "structured_object_identity": source.plan.structured_object_identity,
        "selector": source.selector_descriptor,
        "selection_rule": source.plan.rule_id,
        "budget_tier": source.plan.budget_tier,
        "commit": source.plan.commit,
        "immutable_source_identity": source.immutable_source_identity.as_dict(),
        "source_content_digest": source.source_content_digest.as_dict(),
        "payload_utf8_bytes": payload.utf8_bytes,
        "payload_digest": payload.digest.as_dict(),
    }
    boundary = source.plan.normalized_path_or_object_id
    return {
        "id": omission_identifier(
            BUDGET_CAPACITY_OMISSION_RULE,
            boundary,
            individual,
        ),
        "record_type": "individual",
        "boundary": boundary,
        "individual": individual,
        "rule": BUDGET_CAPACITY_OMISSION_RULE,
        "reason": BUDGET_CAPACITY_OMISSION_REASON,
        "consequence": budget_capacity_consequence(payload.utf8_bytes),
        "blocking": False,
        "reconsideration_condition": BUDGET_CAPACITY_RECONSIDERATION,
    }


def _blocking_reasons(
    omissions: list[dict[str, Any]],
    unknowns: list[dict[str, Any]],
    *,
    budget_exceeded: bool,
) -> list[str]:
    reasons: list[str] = []
    if budget_exceeded:
        reasons.append("budget_exceeded")
    if any(record["blocking"] for record in unknowns):
        reasons.append("blocking_unknown")
    if any(record["blocking"] for record in omissions):
        reasons.append("blocking_omission")
    return reasons


def _package_value(
    *,
    request: CompilationRequest,
    budget_policy: LoadedPolicy,
    snapshot: RepositorySnapshot,
    included: list[tuple[MaterializedSource, MaterializedPayload]],
    omissions: list[dict[str, Any]],
    unknowns: list[dict[str, Any]],
    outcome: str,
    reasons: list[str],
) -> dict[str, Any]:
    request_digest_record = request_digest(_mutable_json_value(request.as_dict()))
    identity_digest, package_id = package_identity(
        request_digest_record.value,
        snapshot.fingerprint.value,
    )
    return {
        "schema_version": _PACKAGE_SCHEMA_VERSION,
        "package": {
            "id": package_id,
            "identity_digest": identity_digest.as_dict(),
            "status": "compiled",
            "generated": True,
            "canonical": False,
            "consumability": "non_consumable" if reasons else "consumable",
            "non_consumable_reasons": list(reasons),
        },
        "compilation": {
            "compiler": request.compiler.as_dict(),
            "selection_policy": request.selection_policy.as_dict(),
            "budget_policy": budget_policy.reference.as_dict(),
            "request_digest": request_digest_record.as_dict(),
            "as_of": request.as_of,
        },
        "repository": {
            "identity": snapshot.repository.normalized_identity,
            "requested_revision": snapshot.requested_revision,
            "object_format": snapshot.object_format,
            "commit": snapshot.commit,
            "tree": snapshot.tree,
            "snapshot_mode": snapshot.snapshot_mode,
            "snapshot_fingerprint": snapshot.fingerprint.as_dict(),
            "protected_references": _mutable_json_value(
                request.protected_references
            ),
        },
        "task": _mutable_json_value(request.task),
        "declared_constraints": _mutable_json_value(
            request.declared_constraints
        ),
        "sources": [_source_value(source) for source, _ in included],
        "payloads": [_payload_value(payload) for _, payload in included],
        "budget": {
            "normative_unit": budget_policy.value["normative_unit"],
            "limit_bytes": budget_policy.value["limit_bytes"],
            "allocation_order": _mutable_json_value(
                budget_policy.value["allocation_order"]
            ),
            "outcome": outcome,
        },
        "conflicts": [],
        "unknowns": unknowns,
        "omissions": omissions,
        "validation": executable_validation_value(),
        "consumer_contract": consumer_contract_value(),
    }


def _measure(package: dict[str, Any]) -> int:
    control_bytes = control_envelope_bytes(package)
    payload_bytes = sum(
        payload["utf8_bytes"] for payload in package["payloads"]
    )
    consumed = control_bytes + payload_bytes
    package["budget"]["measurement"] = {
        "control_envelope_bytes": control_bytes,
        "included_payload_bytes": payload_bytes,
        "consumed_bytes": consumed,
        "remaining_bytes": max(package["budget"]["limit_bytes"] - consumed, 0),
    }
    return consumed


def _finish(package: dict[str, Any]) -> CompilationResult:
    _measure(package)
    package["package"]["digest"] = package_digest(package).as_dict()
    validation = validate_compiled_context_package(package)
    if not validation.valid:
        detail = "; ".join(
            f"{issue.path}: {issue.message}" for issue in validation.issues
        )
        _fail(f"compiled package failed executable validation: {detail}")
    return CompilationResult(
        package=package,
        canonical_json=canonicalize(package),
        validation=validation,
    )


def _allocate_context_package(
    *,
    request: CompilationRequest,
    budget_policy: LoadedPolicy,
    snapshot: RepositorySnapshot,
    materialization: MaterializationResult,
) -> dict[str, Any]:
    """Allocate whole pairs below the public fixed-policy trust boundary."""

    pairs = list(zip(materialization.sources, materialization.payloads))
    mandatory = [
        pair for pair in pairs if pair[0].plan.budget_tier != "optional_evidence"
    ]
    optional = [
        pair for pair in pairs if pair[0].plan.budget_tier == "optional_evidence"
    ]
    existing_omissions = [
        _existing_omission_value(record) for record in materialization.omissions
    ]
    unknowns = [_unknown_value(record) for record in materialization.unknowns]

    # First reserve the complete control envelope with every optional candidate
    # represented as an omission, then greedily test optional pairs in exact source
    # order. Each trial treats all later undecided candidates as whole-pair
    # omissions. This accounts for changing source and omission records while
    # guaranteeing that accepted candidates fit; content is never truncated or
    # replaced by a generated summary.
    initial_budget_omissions = [
        _budget_omission_value(source, payload) for source, payload in optional
    ]
    trial_omissions = existing_omissions + initial_budget_omissions
    trial_reasons = _blocking_reasons(
        trial_omissions,
        unknowns,
        budget_exceeded=False,
    )
    trial = _package_value(
        request=request,
        budget_policy=budget_policy,
        snapshot=snapshot,
        included=mandatory,
        omissions=trial_omissions,
        unknowns=unknowns,
        outcome=(
            "within_budget_optional_sources_omitted"
            if optional
            else "within_budget"
        ),
        reasons=trial_reasons,
    )
    mandatory_consumed = _measure(trial)
    if mandatory_consumed > budget_policy.value["limit_bytes"]:
        reasons = _blocking_reasons(
            trial_omissions,
            unknowns,
            budget_exceeded=True,
        )
        overflow = _package_value(
            request=request,
            budget_policy=budget_policy,
            snapshot=snapshot,
            included=mandatory,
            omissions=trial_omissions,
            unknowns=unknowns,
            outcome="budget_exceeded",
            reasons=reasons,
        )
        return overflow

    included = list(mandatory)
    rejected: list[tuple[MaterializedSource, MaterializedPayload]] = []
    for index, candidate in enumerate(optional):
        later = optional[index + 1 :]
        trial_rejected = rejected + later
        capacity_omissions = [
            _budget_omission_value(source, payload)
            for source, payload in trial_rejected
        ]
        candidate_omissions = existing_omissions + capacity_omissions
        candidate_reasons = _blocking_reasons(
            candidate_omissions,
            unknowns,
            budget_exceeded=False,
        )
        candidate_package = _package_value(
            request=request,
            budget_policy=budget_policy,
            snapshot=snapshot,
            included=included + [candidate],
            omissions=candidate_omissions,
            unknowns=unknowns,
            outcome=(
                "within_budget_optional_sources_omitted"
                if capacity_omissions
                else "within_budget"
            ),
            reasons=candidate_reasons,
        )
        if _measure(candidate_package) <= budget_policy.value["limit_bytes"]:
            included.append(candidate)
        else:
            rejected.append(candidate)

    final_budget_omissions = [
        _budget_omission_value(source, payload) for source, payload in rejected
    ]
    final_omissions = existing_omissions + final_budget_omissions
    final_reasons = _blocking_reasons(
        final_omissions,
        unknowns,
        budget_exceeded=False,
    )
    package = _package_value(
        request=request,
        budget_policy=budget_policy,
        snapshot=snapshot,
        included=included,
        omissions=final_omissions,
        unknowns=unknowns,
        outcome=(
            "within_budget_optional_sources_omitted"
            if final_budget_omissions
            else "within_budget"
        ),
        reasons=final_reasons,
    )
    return package


def compile_context_package(
    *,
    request: CompilationRequest,
    budget_policy: LoadedPolicy,
    snapshot: RepositorySnapshot,
    materialization: MaterializationResult,
) -> CompilationResult:
    """Compile accepted B2a values into one immutable deterministic v1 package."""

    _validate_inputs(
        request=request,
        budget_policy=budget_policy,
        snapshot=snapshot,
        materialization=materialization,
    )
    package = _allocate_context_package(
        request=request,
        budget_policy=budget_policy,
        snapshot=snapshot,
        materialization=materialization,
    )
    return _finish(package)


__all__ = (
    "CompilationContractError",
    "compile_context_package",
)
