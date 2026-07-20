"""Repository-local validation for the bounded task-context v1 contracts."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

from atlas.platform.context_compilation.canonical_json import (
    MAX_SAFE_INTEGER,
    MIN_SAFE_INTEGER,
    canonicalize,
)
from atlas.platform.context_compilation.digests import (
    CANONICALIZATION,
    budget_policy_digest,
    control_envelope_bytes,
    omission_identifier,
    package_digest,
    package_identity,
    payload_identifier,
    request_digest,
    selection_policy_digest,
    sha256_bytes,
    snapshot_fingerprint,
    source_identifier,
    unknown_identifier,
)
from atlas.platform.context_compilation.models import ValidationIssue, ValidationResult


SELECTION_POLICY_SCHEMA_VERSION = "aiden.task-context.selection-policy/v1"
BUDGET_POLICY_SCHEMA_VERSION = "aiden.task-context.budget-policy/v1"
COMPILATION_REQUEST_SCHEMA_VERSION = "aiden.task-context.compilation-request/v1"
CONTEXT_PACKAGE_SCHEMA_VERSION = "aiden.task-context/v1"
CONSUMER_CONTRACT_VERSION = "aiden.task-context-consumer/v1"
SELECTION_POLICY_ID = "example.read-only-architecture-assessment"
BUDGET_POLICY_ID = "example.utf8-byte-budget"
SELECTION_POLICY_VERSION = "1.0.1"
BUDGET_POLICY_VERSION = "1.0.0"
SELECTION_POLICY_DIGEST_VALUE = (
    "69577722ea4eb6f479424f3bf324866cc2992d5df82b3224e5f20571ef081938"
)
BUDGET_POLICY_DIGEST_VALUE = (
    "717dabd3850eaea04caf2439ca77b859a3e0343ec52bc336b2e01ee42727db05"
)
BUDGET_CAPACITY_OMISSION_RULE = "B2b-budget-capacity"
BUDGET_CAPACITY_OMISSION_REASON = (
    "Optional source and payload pair exceeds remaining UTF-8 byte capacity."
)
BUDGET_CAPACITY_RECONSIDERATION = (
    "Increase the byte budget or reduce earlier higher-priority package content "
    "and recompile."
)
SOURCE_BUDGET_TIERS = (
    "mandatory_authoritative_sources",
    "required_supporting_sources",
    "optional_evidence",
)
SENSITIVITY_ORDER = (
    "public",
    "ordinary_personal",
    "sensitive",
    "highly_restricted",
)

RFC3339_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
LOWER_HEX_64 = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA1 = re.compile(r"^[0-9a-f]{40}$")

CONSUMER_MUST = (
    "verify_schema_compatibility",
    (
        "verify_payload_digests_and_treat_whole_source_digests_as_claims_pending_"
        "immutable_source_revalidation"
    ),
    "verify_repository_revision",
    "preserve_authority_and_provenance",
    "treat_constraints_as_copied_declarations_not_package_created_permissions",
    "refuse_to_infer_approval_from_missing_information",
    "stop_on_blocking_conflicts_or_unknowns",
    "request_recompilation_or_owner_resolution_for_stale_conflicting_insufficient_or_oversized_context",
    "revalidate_live_state_when_required",
    "distinguish_source_content_from_consumer_inference",
    "preserve_provider_independence",
)
CONSUMER_MUST_NOT = (
    "replace_authoritative_sources",
    "broaden_goal_scope_permissions_writable_paths_approval_or_autonomy",
    "silently_discard_mandatory_context",
    "silently_resolve_consequential_conflicts",
    "promote_generated_content_or_inference_to_canonical_status",
    "treat_package_as_authorization_execution_evidence_or_proof_of_completion",
    "mutate_repository_because_an_item_is_present_in_context",
)
CONSUMER_STOP_CONDITIONS = (
    "package_is_non_consumable",
    "integrity_verification_fails",
    "repository_revision_does_not_match",
    "blocking_conflict_or_unknown_exists",
    "required_live_state_cannot_be_revalidated",
)
IMMUTABLE_SOURCE_LIVE_REVALIDATION_REQUIREMENT = (
    "verify_immutable_git_blob_identity_and_whole_source_content_digest_before_"
    "relying_on_whole_source_authenticity"
)
EXECUTABLE_VALIDATION_CHECKS = (
    "supported_schema_policy_and_consumer_contract",
    "request_snapshot_and_package_identity",
    "fixed_source_identity_authority_and_payload_integrity_linkage_and_ordering",
    "budget_measurement_allocation_and_no_truncation",
    "package_integrity_and_classification",
    "consumability_state_and_reasons",
)
EXECUTABLE_VALIDATION_LIMITATIONS = (
    "Deterministic validation cannot establish absence of every semantic conflict.",
    (
        "Excerpt-only package validation independently verifies payload bytes and "
        "payload digests; whole-source content digests are compiler-carried claims "
        "that require immutable Git blob revalidation outside the package."
    ),
)


@dataclass(frozen=True)
class _FirstSliceRuleContract:
    rule_id: str
    rule_type: str
    priority_tier: int
    budget_tier: str
    source_kind: str
    sensitivity: str
    path: str
    structured_object_identity: str | None
    selector_type: str
    selector_fields: tuple[str, ...]
    heading_text: str | None
    occurrence: int | None
    selector_descriptor: str
    authority_class: str
    canonical_owner: str
    selection_reason: str
    trigger: str
    selection_chain: tuple[str, ...]
    media_type: str
    freshness_status: str
    freshness_basis: str
    freshness_rule: str

    @property
    def normalized_identity(self) -> str:
        return self.structured_object_identity or self.path


_PINNED_CANONICAL_FRESHNESS_BASIS = (
    "The registered Engineering Opportunity object is read from the exact "
    "requested snapshot, its source path, structured identity, and field-contract "
    "owner match, and the accepted selected lifecycle value is reviewed."
)
_MISSION_FRESHNESS_BASIS = (
    "The exact Current Mission source is established at the pinned snapshot, but "
    "the compilation inputs contain no independent synchronization finding proving "
    "semantic alignment."
)
_CANONICAL_DOCUMENT_FRESHNESS_BASIS = (
    "The selected canonical document is read from the exact requested snapshot, "
    "its canonical owner matches its normalized path, and no blocking B1b2 record "
    "exists for the boundary."
)

# This tuple is the single immutable, digest-bound first-slice rule contract used
# by both the public compiler boundary and offline executable validation. It is a
# code projection of selection policy 1.0.1 plus the accepted B1b2/B2a trace,
# authority, selector, transformation, media, and freshness contracts.
FIRST_SLICE_RULE_CONTRACT = (
    _FirstSliceRuleContract(
        rule_id="S010-explicit-opportunity-anchor",
        rule_type="explicit_anchor",
        priority_tier=10,
        budget_tier="mandatory_authoritative_sources",
        source_kind="repository_object",
        sensitivity="public",
        path=(
            "docs/opportunities/reviewed/"
            "EO-2026-013-task-scoped-agent-context-compilation.yaml"
        ),
        structured_object_identity="engineering-opportunity:EO-2026-013",
        selector_type="yaml_fields",
        selector_fields=("id", "title", "status", "summary"),
        heading_text=None,
        occurrence=None,
        selector_descriptor="yaml-fields:/id,/title,/status,/summary",
        authority_class="structured_repository_object",
        canonical_owner="docs/architecture/engineering-opportunity-object.md",
        selection_reason="explicit_opportunity_reference",
        trigger="task.opportunity_references[0]",
        selection_chain=(
            "task.opportunity_references[0]",
            "S010-explicit-opportunity-anchor",
        ),
        media_type="application/json",
        freshness_status="current_at_snapshot",
        freshness_basis=_PINNED_CANONICAL_FRESHNESS_BASIS,
        freshness_rule="F010-pinned-canonical-source",
    ),
    _FirstSliceRuleContract(
        rule_id="S020-current-mission-milestone",
        rule_type="explicit_anchor",
        priority_tier=10,
        budget_tier="mandatory_authoritative_sources",
        source_kind="document",
        sensitivity="public",
        path="docs/current-mission.md",
        structured_object_identity=None,
        selector_type="heading",
        selector_fields=(),
        heading_text="## Initial Milestone",
        occurrence=1,
        selector_descriptor="heading:## Initial Milestone",
        authority_class="canonical_document",
        canonical_owner="docs/current-mission.md",
        selection_reason="explicit_mission_reference",
        trigger="task.mission_references[0]",
        selection_chain=(
            "task.mission_references[0]",
            "S020-current-mission-milestone",
        ),
        media_type="text/markdown",
        freshness_status="unknown",
        freshness_basis=_MISSION_FRESHNESS_BASIS,
        freshness_rule="F020-current-mission-synchronization-unverified",
    ),
    _FirstSliceRuleContract(
        rule_id="S030-canonical-repository-authority",
        rule_type="allowlisted_relationship",
        priority_tier=20,
        budget_tier="required_supporting_sources",
        source_kind="document",
        sensitivity="public",
        path="docs/architecture/repository.md",
        structured_object_identity=None,
        selector_type="heading",
        selector_fields=(),
        heading_text="## Source of Truth Hierarchy",
        occurrence=1,
        selector_descriptor="heading:## Source of Truth Hierarchy",
        authority_class="canonical_document",
        canonical_owner="docs/architecture/repository.md",
        selection_reason="allowlisted_related_document",
        trigger="task.opportunity_references[0]",
        selection_chain=(
            "task.opportunity_references[0]",
            "related_documents:outbound",
            "docs/architecture/repository.md",
            "S030-canonical-repository-authority",
        ),
        media_type="text/markdown",
        freshness_status="current_at_snapshot",
        freshness_basis=_CANONICAL_DOCUMENT_FRESHNESS_BASIS,
        freshness_rule="F010-pinned-canonical-source",
    ),
    _FirstSliceRuleContract(
        rule_id="S040-mandatory-knowledge-authority",
        rule_type="task_profile",
        priority_tier=30,
        budget_tier="required_supporting_sources",
        source_kind="document",
        sensitivity="public",
        path="docs/architecture/knowledge-authority.md",
        structured_object_identity=None,
        selector_type="heading",
        selector_fields=(),
        heading_text="### Generated Context",
        occurrence=1,
        selector_descriptor="heading:### Generated Context",
        authority_class="canonical_document",
        canonical_owner="docs/architecture/knowledge-authority.md",
        selection_reason="task_profile_required_source",
        trigger="task.type=architecture_assessment",
        selection_chain=(
            "task.type=architecture_assessment",
            "task_profile=eo-architecture-assessment",
            "S040-mandatory-knowledge-authority",
        ),
        media_type="text/markdown",
        freshness_status="current_at_snapshot",
        freshness_basis=_CANONICAL_DOCUMENT_FRESHNESS_BASIS,
        freshness_rule="F010-pinned-canonical-source",
    ),
    _FirstSliceRuleContract(
        rule_id="S050-mandatory-collaboration",
        rule_type="allowlisted_relationship",
        priority_tier=30,
        budget_tier="required_supporting_sources",
        source_kind="document",
        sensitivity="public",
        path="docs/standards/engineering-collaboration.md",
        structured_object_identity=None,
        selector_type="heading",
        selector_fields=(),
        heading_text="## Responsibilities",
        occurrence=1,
        selector_descriptor="heading:## Responsibilities",
        authority_class="canonical_document",
        canonical_owner="docs/standards/engineering-collaboration.md",
        selection_reason="allowlisted_related_document",
        trigger="task.opportunity_references[0]",
        selection_chain=(
            "task.opportunity_references[0]",
            "related_documents:outbound",
            "docs/standards/engineering-collaboration.md",
            "S050-mandatory-collaboration",
        ),
        media_type="text/markdown",
        freshness_status="current_at_snapshot",
        freshness_basis=_CANONICAL_DOCUMENT_FRESHNESS_BASIS,
        freshness_rule="F010-pinned-canonical-source",
    ),
)


def fixed_first_slice_rule(rule_id: Any) -> _FirstSliceRuleContract | None:
    """Return the immutable fixed-rule contract for one accepted rule ID."""

    for rule in FIRST_SLICE_RULE_CONTRACT:
        if rule.rule_id == rule_id:
            return rule
    return None


def fixed_first_slice_selector(rule: _FirstSliceRuleContract) -> dict[str, Any]:
    """Return a fresh policy selector projection for one fixed rule."""

    if rule.selector_type == "yaml_fields":
        return {"type": "yaml_fields", "fields": list(rule.selector_fields)}
    return {
        "type": "heading",
        "heading_text": rule.heading_text,
        "occurrence": rule.occurrence,
    }


def fixed_first_slice_transformation_matches(
    rule: _FirstSliceRuleContract,
    transformation: Any,
    payload_content: bytes,
) -> bool:
    """Check the exact selector transformation shape available in-package."""

    if not isinstance(transformation, Mapping):
        return False
    if rule.selector_type == "yaml_fields":
        return _mutable_json_value(transformation) == {
            "type": "yaml_field_selection",
            "selected_fields": ["/id", "/title", "/status", "/summary"],
            "output": "rfc8785-jcs",
            "line_endings": "not_applicable",
        }

    line_endings = transformation.get("source_line_endings")
    if line_endings not in ("lf", "crlf", "none"):
        return False
    expected = {
        "type": "heading_bounded_excerpt",
        "start_heading": rule.heading_text,
        "occurrence": 1,
        "end_rule": "before_next_atx_heading_of_equal_or_greater_level_or_eof",
        "source_line_endings": line_endings,
        "content_change": "none",
    }
    if _mutable_json_value(transformation) != expected:
        return False
    if line_endings == "crlf":
        return b"\r\n" in payload_content and b"\n" not in payload_content.replace(
            b"\r\n", b""
        )
    if line_endings == "lf":
        return b"\r" not in payload_content and b"\n" in payload_content
    return b"\r" not in payload_content and b"\n" not in payload_content


def fixed_first_slice_freshness(
    rule: _FirstSliceRuleContract,
    as_of: str,
) -> dict[str, str]:
    """Return the exact first-slice freshness projection for one fixed rule."""

    return {
        "status": rule.freshness_status,
        "basis": rule.freshness_basis,
        "rule": rule.freshness_rule,
        "as_of": as_of,
    }


def budget_capacity_consequence(payload_utf8_bytes: int) -> str:
    """Return the stable whole-pair capacity consequence for one byte count."""

    return (
        f"Excluded the complete optional {payload_utf8_bytes}-byte payload; "
        "no content was truncated or summarized."
    )


class ContractValidationError(ValueError):
    """Raised when a bounded v1 contract is not valid."""

    def __init__(self, result: ValidationResult):
        self.result = result
        detail = "; ".join(
            f"{issue.path}: {issue.message}" for issue in result.issues
        )
        super().__init__(detail or "contract validation failed")


def consumer_contract_value() -> dict[str, Any]:
    """Return the fixed first-slice consumer contract as a fresh value."""

    return {
        "version": CONSUMER_CONTRACT_VERSION,
        "must": list(CONSUMER_MUST),
        "must_not": list(CONSUMER_MUST_NOT),
        "stop_conditions": list(CONSUMER_STOP_CONDITIONS),
        "live_revalidation_required": [
            IMMUTABLE_SOURCE_LIVE_REVALIDATION_REQUIREMENT
        ],
    }


def executable_validation_value() -> dict[str, Any]:
    """Return the fixed executable-validation record carried by B2b packages."""

    return {
        "status": "passed",
        "executable_validation_performed": True,
        "checks": [
            {"invariant": invariant, "status": "passed"}
            for invariant in EXECUTABLE_VALIDATION_CHECKS
        ],
        "errors": [],
        "limitations": list(EXECUTABLE_VALIDATION_LIMITATIONS),
    }


def _issue(issues: list[ValidationIssue], code: str, path: str, message: str) -> None:
    issues.append(ValidationIssue(code=code, path=path, message=message))


def _mapping(value: Any, path: str, issues: list[ValidationIssue]) -> bool:
    if not isinstance(value, Mapping):
        _issue(issues, "type", path, "must be an object")
        return False
    return True


def _fixed_object(
    value: Any,
    path: str,
    required: Iterable[str],
    allowed: Iterable[str],
    issues: list[ValidationIssue],
) -> bool:
    if not _mapping(value, path, issues):
        return False
    required_set = set(required)
    allowed_set = set(allowed)
    for field in sorted(required_set - set(value)):
        _issue(issues, "required", f"{path}.{field}", "is required")
    for field in sorted(set(value) - allowed_set):
        _issue(issues, "unknown_field", f"{path}.{field}", "is not allowed")
    return True


def _string(
    value: Any,
    path: str,
    issues: list[ValidationIssue],
    *,
    non_empty: bool = False,
) -> bool:
    if not isinstance(value, str):
        _issue(issues, "type", path, "must be a string")
        return False
    if non_empty and not value:
        _issue(issues, "min_length", path, "must be a non-empty string")
        return False
    if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        _issue(issues, "unicode_scalar", path, "must contain valid Unicode scalars")
        return False
    return True


def _integer(
    value: Any, path: str, issues: list[ValidationIssue], *, non_negative: bool = False
) -> bool:
    if isinstance(value, bool) or not isinstance(value, int):
        _issue(issues, "type", path, "must be an integer, not a boolean")
        return False
    if not MIN_SAFE_INTEGER <= value <= MAX_SAFE_INTEGER:
        _issue(issues, "safe_integer", path, "must be within the safe-integer range")
        return False
    if non_negative and value < 0:
        _issue(issues, "non_negative", path, "must be non-negative")
        return False
    return True


def _boolean(value: Any, path: str, issues: list[ValidationIssue]) -> bool:
    if not isinstance(value, bool):
        _issue(issues, "type", path, "must be a boolean")
        return False
    return True


def _string_list(value: Any, path: str, issues: list[ValidationIssue]) -> bool:
    if not isinstance(value, list):
        _issue(issues, "type", path, "must be an array")
        return False
    for index, item in enumerate(value):
        _string(item, f"{path}[{index}]", issues)
    return True


def _normative_value(value: Any, path: str, issues: list[ValidationIssue]) -> bool:
    if value is None or isinstance(value, bool):
        return True
    if isinstance(value, int):
        return _integer(value, path, issues)
    if isinstance(value, str):
        return _string(value, path, issues)
    if isinstance(value, list):
        for index, item in enumerate(value):
            _normative_value(item, f"{path}[{index}]", issues)
        return True
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                _issue(issues, "mapping_key", path, "all mapping keys must be strings")
                continue
            _string(key, f"{path}.<key>", issues)
            _normative_value(item, f"{path}.{key}", issues)
        return True
    _issue(issues, "normative_type", path, f"unsupported value type: {type(value).__name__}")
    return False


def _rfc3339(value: Any, path: str, issues: list[ValidationIssue]) -> bool:
    if not isinstance(value, str) or not RFC3339_PATTERN.fullmatch(value):
        _issue(issues, "rfc3339", path, "must include an explicit Z or numeric offset")
        return False
    try:
        datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError:
        _issue(issues, "rfc3339", path, "must be a valid RFC 3339 date and time")
        return False
    return True


def _digest_record(value: Any, path: str, issues: list[ValidationIssue]) -> bool:
    if not _fixed_object(
        value,
        path,
        ("algorithm", "canonicalization", "value"),
        ("algorithm", "canonicalization", "value"),
        issues,
    ):
        return False
    if value.get("algorithm") != "sha256":
        _issue(issues, "digest_algorithm", f"{path}.algorithm", "must be sha256")
    if value.get("canonicalization") != CANONICALIZATION:
        _issue(
            issues,
            "digest_canonicalization",
            f"{path}.canonicalization",
            f"must be {CANONICALIZATION}",
        )
    digest_value = value.get("value")
    if not isinstance(digest_value, str) or not LOWER_HEX_64.fullmatch(digest_value):
        _issue(issues, "digest_value", f"{path}.value", "must be 64 lowercase hex")
    return True


def _byte_digest_record(value: Any, path: str, issues: list[ValidationIssue]) -> bool:
    if not _fixed_object(
        value, path, ("algorithm", "value"), ("algorithm", "value"), issues
    ):
        return False
    if value.get("algorithm") != "sha256":
        _issue(issues, "digest_algorithm", f"{path}.algorithm", "must be sha256")
    digest_value = value.get("value")
    if not isinstance(digest_value, str) or not LOWER_HEX_64.fullmatch(digest_value):
        _issue(issues, "digest_value", f"{path}.value", "must be 64 lowercase hex")
    return True


def _policy_reference(value: Any, path: str, issues: list[ValidationIssue]) -> bool:
    if not _fixed_object(
        value, path, ("id", "version", "digest"), ("id", "version", "digest"), issues
    ):
        return False
    _string(value.get("id"), f"{path}.id", issues, non_empty=True)
    _string(value.get("version"), f"{path}.version", issues, non_empty=True)
    _digest_record(value.get("digest"), f"{path}.digest", issues)
    return True


def _protected_reference(value: Any, path: str, issues: list[ValidationIssue]) -> bool:
    fields = ("name", "expected_object", "authoritatively_targeted", "selection")
    if not _fixed_object(value, path, fields, fields, issues):
        return False
    _string(value.get("name"), f"{path}.name", issues, non_empty=True)
    expected = value.get("expected_object")
    if not isinstance(expected, str) or not GIT_SHA1.fullmatch(expected):
        _issue(issues, "git_identity", f"{path}.expected_object", "must be 40 lowercase hex")
    _boolean(value.get("authoritatively_targeted"), f"{path}.authoritatively_targeted", issues)
    if value.get("selection") not in ("forbidden", "allowed"):
        _issue(issues, "protected_selection", f"{path}.selection", "must be forbidden or allowed")
    if value.get("selection") == "allowed" and value.get("authoritatively_targeted") is not True:
        _issue(issues, "protected_authority", path, "allowed selection requires authoritative targeting")
    return True


def _attributed(
    value: Any,
    path: str,
    issues: list[ValidationIssue],
    *,
    allow_unknown: bool = False,
) -> bool:
    fields = ("state", "value", "authority", "provenance")
    if not _fixed_object(value, path, fields, fields, issues):
        return False
    accepted_states = ("known", "unknown") if allow_unknown else ("known",)
    if value.get("state") not in accepted_states:
        _issue(issues, "attributed_state", f"{path}.state", "is not accepted in this v1 contract")
    if "value" in value:
        _normative_value(value["value"], f"{path}.value", issues)
    authority = value.get("authority")
    if _fixed_object(
        authority,
        f"{path}.authority",
        ("class", "owner"),
        ("class", "owner"),
        issues,
    ):
        _string(
            authority.get("class"),
            f"{path}.authority.class",
            issues,
            non_empty=True,
        )
        _string(
            authority.get("owner"),
            f"{path}.authority.owner",
            issues,
            non_empty=True,
        )
    provenance = value.get("provenance")
    if _fixed_object(
        provenance,
        f"{path}.provenance",
        ("source", "selector"),
        ("source", "selector"),
        issues,
    ):
        _string(
            provenance.get("source"),
            f"{path}.provenance.source",
            issues,
            non_empty=True,
        )
        _string(
            provenance.get("selector"),
            f"{path}.provenance.selector",
            issues,
            non_empty=True,
        )
    return True


def _attributed_group(
    value: Any,
    path: str,
    required_fields: tuple[str, ...],
    issues: list[ValidationIssue],
    *,
    allow_unknown: bool = False,
) -> bool:
    if not _fixed_object(value, path, required_fields, required_fields, issues):
        return False
    for field in required_fields:
        if field in value:
            _attributed(
                value[field],
                f"{path}.{field}",
                issues,
                allow_unknown=allow_unknown,
            )
    return True


def validate_selection_policy(value: Any) -> ValidationResult:
    issues: list[ValidationIssue] = []
    fields = (
        "schema_version",
        "id",
        "version",
        "task_profile",
        "relationship_traversal",
        "source_ordering",
        "rules",
        "exclusion_rules",
        "maximum_sensitivity",
        "omission_candidate_universe",
        "digest",
    )
    if not _fixed_object(value, "$", fields, fields, issues):
        return ValidationResult(tuple(issues))
    if value.get("schema_version") != SELECTION_POLICY_SCHEMA_VERSION:
        _issue(issues, "unsupported_version", "$.schema_version", "unsupported selection-policy schema")
    for field in ("id", "version", "task_profile"):
        _string(value.get(field), f"$.{field}", issues, non_empty=True)
    maximum_sensitivity = value.get("maximum_sensitivity")
    if maximum_sensitivity not in SENSITIVITY_ORDER:
        _issue(
            issues,
            "maximum_sensitivity",
            "$.maximum_sensitivity",
            "is not an accepted v1 sensitivity",
        )
    if value.get("id") != SELECTION_POLICY_ID or value.get("version") != SELECTION_POLICY_VERSION:
        _issue(issues, "unsupported_policy", "$.id", "unsupported selection-policy identity or version")
    traversal = value.get("relationship_traversal")
    if _fixed_object(
        traversal,
        "$.relationship_traversal",
        ("max_hops", "allowlisted"),
        ("max_hops", "allowlisted"),
        issues,
    ):
        _integer(traversal.get("max_hops"), "$.relationship_traversal.max_hops", issues, non_negative=True)
        if traversal.get("max_hops") != 1:
            _issue(issues, "relationship_bound", "$.relationship_traversal.max_hops", "must be exactly 1")
        allowlisted = traversal.get("allowlisted")
        if not isinstance(allowlisted, list):
            _issue(issues, "type", "$.relationship_traversal.allowlisted", "must be an array")
        else:
            for index, relationship in enumerate(allowlisted):
                path = f"$.relationship_traversal.allowlisted[{index}]"
                if _fixed_object(relationship, path, ("type", "direction"), ("type", "direction"), issues):
                    _string(
                        relationship.get("type"),
                        f"{path}.type",
                        issues,
                        non_empty=True,
                    )
                    if relationship.get("direction") not in ("outbound", "inbound"):
                        _issue(issues, "relationship_direction", f"{path}.direction", "must be outbound or inbound")
    expected_order = [
        "priority_tier",
        "selection_rule_id",
        "normalized_path_or_object_id",
        "selector",
    ]
    if value.get("source_ordering") != expected_order:
        _issue(issues, "source_ordering", "$.source_ordering", "must match the v1 exact ordering")
    rules = value.get("rules")
    if not isinstance(rules, list) or not rules:
        _issue(issues, "type", "$.rules", "must be a non-empty array")
    else:
        seen: set[str] = set()
        for index, rule in enumerate(rules):
            path = f"$.rules[{index}]"
            rule_fields = (
                "id",
                "type",
                "priority_tier",
                "budget_tier",
                "source",
                "selector",
            )
            if not _fixed_object(rule, path, rule_fields, rule_fields, issues):
                continue
            rule_id = rule.get("id")
            _string(rule_id, f"{path}.id", issues, non_empty=True)
            if isinstance(rule_id, str):
                if rule_id in seen:
                    _issue(issues, "duplicate_rule", f"{path}.id", "must be unique")
                seen.add(rule_id)
            if rule.get("type") not in ("explicit_anchor", "task_profile", "allowlisted_relationship"):
                _issue(issues, "rule_type", f"{path}.type", "is unsupported")
            _integer(rule.get("priority_tier"), f"{path}.priority_tier", issues, non_negative=True)
            if rule.get("budget_tier") not in SOURCE_BUDGET_TIERS:
                _issue(
                    issues,
                    "budget_tier",
                    f"{path}.budget_tier",
                    "is not an accepted source budget tier",
                )
            source = rule.get("source")
            source_allowed = (
                "kind",
                "sensitivity",
                "path",
                "object_type",
                "field_contract_owner",
            )
            if _fixed_object(
                source,
                f"{path}.source",
                ("kind", "sensitivity"),
                source_allowed,
                issues,
            ):
                if source.get("kind") not in ("repository_object", "document"):
                    _issue(
                        issues,
                        "source_kind",
                        f"{path}.source.kind",
                        "must be repository_object or document",
                    )
                sensitivity = source.get("sensitivity")
                if sensitivity not in SENSITIVITY_ORDER:
                    _issue(
                        issues,
                        "source_sensitivity",
                        f"{path}.source.sensitivity",
                        "is not an accepted v1 sensitivity",
                    )
                elif maximum_sensitivity in SENSITIVITY_ORDER and (
                    SENSITIVITY_ORDER.index(sensitivity)
                    > SENSITIVITY_ORDER.index(maximum_sensitivity)
                ):
                    _issue(
                        issues,
                        "sensitivity_ceiling",
                        f"{path}.source.sensitivity",
                        "must not exceed maximum_sensitivity",
                    )
                for field in ("path", "object_type", "field_contract_owner"):
                    if field in source:
                        _string(
                            source[field],
                            f"{path}.source.{field}",
                            issues,
                            non_empty=True,
                        )
            selector = rule.get("selector")
            selector_allowed = ("type", "fields", "heading_text", "occurrence")
            if _fixed_object(selector, f"{path}.selector", ("type",), selector_allowed, issues):
                selector_type = selector.get("type")
                if selector_type == "yaml_fields":
                    if set(selector) != {"type", "fields"}:
                        _issue(issues, "selector_shape", f"{path}.selector", "yaml_fields requires only type and fields")
                    if _string_list(selector.get("fields"), f"{path}.selector.fields", issues):
                        if selector.get("fields") != ["id", "title", "status", "summary"]:
                            _issue(issues, "field_allowlist", f"{path}.selector.fields", "must match the EO v1 field allowlist")
                elif selector_type == "heading":
                    if set(selector) != {"type", "heading_text", "occurrence"}:
                        _issue(issues, "selector_shape", f"{path}.selector", "heading requires exact text and occurrence")
                    _string(
                        selector.get("heading_text"),
                        f"{path}.selector.heading_text",
                        issues,
                        non_empty=True,
                    )
                    if _integer(selector.get("occurrence"), f"{path}.selector.occurrence", issues, non_negative=True):
                        if selector.get("occurrence") < 1:
                            _issue(issues, "occurrence", f"{path}.selector.occurrence", "must be one-based")
                else:
                    _issue(issues, "selector_type", f"{path}.selector.type", "is unsupported")
    exclusions = value.get("exclusion_rules")
    if not isinstance(exclusions, list) or not exclusions:
        _issue(issues, "type", "$.exclusion_rules", "must be a non-empty array")
    else:
        for index, exclusion in enumerate(exclusions):
            path = f"$.exclusion_rules[{index}]"
            fields = ("id", "type", "reason")
            if _fixed_object(exclusion, path, fields, fields, issues):
                for field in fields:
                    _string(
                        exclusion.get(field),
                        f"{path}.{field}",
                        issues,
                        non_empty=True,
                    )
    expected_universe = [
        "explicit_request_anchors",
        "exact_task_profile_candidates",
        "allowlisted_one_hop_relationship_candidates",
    ]
    if value.get("omission_candidate_universe") != expected_universe:
        _issue(issues, "omission_universe", "$.omission_candidate_universe", "must match the bounded v1 universe")
    _digest_record(value.get("digest"), "$.digest", issues)
    if not issues:
        expected = selection_policy_digest(value).as_dict()
        if value["digest"] != expected:
            _issue(issues, "digest_mismatch", "$.digest", "does not match the self-excluding policy digest")
    return ValidationResult(tuple(issues))


def validate_budget_policy(value: Any) -> ValidationResult:
    issues: list[ValidationIssue] = []
    fields = (
        "schema_version",
        "id",
        "version",
        "normative_unit",
        "limit_bytes",
        "allocation_order",
        "control_envelope_measurement",
        "mandatory_tier_overflow",
        "arbitrary_character_truncation",
        "digest",
    )
    if not _fixed_object(value, "$", fields, fields, issues):
        return ValidationResult(tuple(issues))
    if value.get("schema_version") != BUDGET_POLICY_SCHEMA_VERSION:
        _issue(issues, "unsupported_version", "$.schema_version", "unsupported budget-policy schema")
    for field in ("id", "version"):
        _string(value.get(field), f"$.{field}", issues)
    if value.get("id") != BUDGET_POLICY_ID or value.get("version") != BUDGET_POLICY_VERSION:
        _issue(issues, "unsupported_policy", "$.id", "unsupported budget-policy identity or version")
    if value.get("normative_unit") != "utf8_bytes":
        _issue(issues, "budget_unit", "$.normative_unit", "must be utf8_bytes")
    if _integer(value.get("limit_bytes"), "$.limit_bytes", issues, non_negative=True):
        if value.get("limit_bytes") != 65536:
            _issue(issues, "budget_limit", "$.limit_bytes", "example policy limit must be 65536")
    expected_order = [
        "mandatory_control_envelope",
        "mandatory_authoritative_sources",
        "required_supporting_sources",
        "optional_evidence",
    ]
    if value.get("allocation_order") != expected_order:
        _issue(issues, "allocation_order", "$.allocation_order", "must match the v1 exact order")
    measurement = value.get("control_envelope_measurement")
    if _fixed_object(
        measurement,
        "$.control_envelope_measurement",
        ("canonicalization", "remove"),
        ("canonicalization", "remove"),
        issues,
    ):
        if measurement.get("canonicalization") != CANONICALIZATION:
            _issue(issues, "canonicalization", "$.control_envelope_measurement.canonicalization", "must be rfc8785-jcs")
        if measurement.get("remove") != ["package.digest", "payloads[*].content", "budget.measurement"]:
            _issue(issues, "removal_surface", "$.control_envelope_measurement.remove", "must match the architecture surface")
    if value.get("mandatory_tier_overflow") != "non_consumable_budget_exceeded":
        _issue(issues, "overflow", "$.mandatory_tier_overflow", "must be non_consumable_budget_exceeded")
    if value.get("arbitrary_character_truncation") != "forbidden":
        _issue(issues, "truncation", "$.arbitrary_character_truncation", "must be forbidden")
    _digest_record(value.get("digest"), "$.digest", issues)
    if not issues:
        expected = budget_policy_digest(value).as_dict()
        if value["digest"] != expected:
            _issue(issues, "digest_mismatch", "$.digest", "does not match the self-excluding policy digest")
    return ValidationResult(tuple(issues))


TASK_FIELDS = (
    "id",
    "type",
    "goal",
    "scope",
    "non_goals",
    "completion_criteria",
    "mission_references",
    "opportunity_references",
)
CONSTRAINT_FIELDS = (
    "permissions",
    "forbidden_actions",
    "writable_paths",
    "approval_points",
    "required_validation",
)


def validate_compilation_request(value: Any) -> ValidationResult:
    issues: list[ValidationIssue] = []
    required = (
        "schema_version",
        "repository_request",
        "task",
        "declared_constraints",
        "selection_policy",
        "budget_policy",
        "protected_references",
        "as_of",
        "compiler",
    )
    allowed = required + ("fixture_evidence",)
    if not _fixed_object(value, "$", required, allowed, issues):
        return ValidationResult(tuple(issues))
    if value.get("schema_version") != COMPILATION_REQUEST_SCHEMA_VERSION:
        _issue(issues, "unsupported_version", "$.schema_version", "unsupported compilation-request schema")
    repository = value.get("repository_request")
    if _fixed_object(
        repository,
        "$.repository_request",
        ("identity", "requested_revision"),
        ("identity", "requested_revision"),
        issues,
    ):
        _string(
            repository.get("identity"),
            "$.repository_request.identity",
            issues,
            non_empty=True,
        )
        _string(
            repository.get("requested_revision"),
            "$.repository_request.requested_revision",
            issues,
            non_empty=True,
        )
    _attributed_group(value.get("task"), "$.task", TASK_FIELDS, issues)
    _attributed_group(value.get("declared_constraints"), "$.declared_constraints", CONSTRAINT_FIELDS, issues)
    _policy_reference(value.get("selection_policy"), "$.selection_policy", issues)
    _policy_reference(value.get("budget_policy"), "$.budget_policy", issues)
    selection_reference = value.get("selection_policy")
    if isinstance(selection_reference, Mapping) and (
        selection_reference.get("id") != SELECTION_POLICY_ID
        or selection_reference.get("version") != SELECTION_POLICY_VERSION
    ):
        _issue(issues, "unsupported_policy", "$.selection_policy", "unsupported selection-policy identity or version")
    budget_reference = value.get("budget_policy")
    if isinstance(budget_reference, Mapping) and (
        budget_reference.get("id") != BUDGET_POLICY_ID
        or budget_reference.get("version") != BUDGET_POLICY_VERSION
    ):
        _issue(issues, "unsupported_policy", "$.budget_policy", "unsupported budget-policy identity or version")
    protected = value.get("protected_references")
    if not isinstance(protected, list):
        _issue(issues, "type", "$.protected_references", "must be an array")
    else:
        for index, record in enumerate(protected):
            _protected_reference(record, f"$.protected_references[{index}]", issues)
    _rfc3339(value.get("as_of"), "$.as_of", issues)
    compiler = value.get("compiler")
    if _fixed_object(compiler, "$.compiler", ("identity", "version"), ("identity", "version"), issues):
        for field in ("identity", "version"):
            _string(
                compiler.get(field),
                f"$.compiler.{field}",
                issues,
                non_empty=True,
            )
    if "fixture_evidence" in value:
        evidence = value["fixture_evidence"]
        if _fixed_object(evidence, "$.fixture_evidence", ("expected_tree",), ("expected_tree",), issues):
            tree = evidence.get("expected_tree")
            if not isinstance(tree, str) or not GIT_SHA1.fullmatch(tree):
                _issue(issues, "git_identity", "$.fixture_evidence.expected_tree", "must be 40 lowercase hex")
    return ValidationResult(tuple(issues))


def validate_policy_reference_identity(
    reference: Mapping[str, Any], policy: Mapping[str, Any], *, kind: str
) -> ValidationResult:
    issues: list[ValidationIssue] = []
    digest_function = selection_policy_digest if kind == "selection" else budget_policy_digest
    for field in ("id", "version"):
        if reference.get(field) != policy.get(field):
            _issue(issues, "policy_identity_mismatch", f"$.{field}", f"does not match loaded {kind} policy")
    expected_digest = digest_function(policy).as_dict()
    if reference.get("digest") != expected_digest:
        _issue(issues, "policy_digest_mismatch", "$.digest", f"does not match loaded {kind} policy")
    return ValidationResult(tuple(issues))


def _source_record(value: Any, path: str, issues: list[ValidationIssue]) -> None:
    fields = (
        "id", "path", "structured_object_identity", "selector", "priority_tier",
        "selection_rule", "selection_reason", "trigger", "selection_chain",
        "authority_class", "canonical_owner", "commit", "immutable_source_identity",
        "source_content_digest", "transformation", "freshness", "included_utf8_bytes",
        "payload_ref",
    )
    if not _fixed_object(value, path, fields, fields, issues):
        return
    for field in (
        "id", "path", "selector", "selection_rule", "selection_reason", "trigger",
        "authority_class", "canonical_owner", "commit", "payload_ref",
    ):
        _string(value.get(field), f"{path}.{field}", issues)
    identity = value.get("structured_object_identity")
    if identity is not None:
        _string(identity, f"{path}.structured_object_identity", issues)
    _integer(value.get("priority_tier"), f"{path}.priority_tier", issues, non_negative=True)
    _string_list(value.get("selection_chain"), f"{path}.selection_chain", issues)
    immutable = value.get("immutable_source_identity")
    immutable_fields = ("type", "object_format", "value")
    if _fixed_object(immutable, f"{path}.immutable_source_identity", immutable_fields, immutable_fields, issues):
        for field in immutable_fields:
            _string(immutable.get(field), f"{path}.immutable_source_identity.{field}", issues)
    _byte_digest_record(value.get("source_content_digest"), f"{path}.source_content_digest", issues)
    transformation = value.get("transformation")
    transformation_allowed = (
        "type", "selected_fields", "output", "line_endings", "start_heading",
        "occurrence", "end_rule", "source_line_endings", "content_change",
    )
    if _fixed_object(transformation, f"{path}.transformation", ("type",), transformation_allowed, issues):
        _string(transformation.get("type"), f"{path}.transformation.type", issues)
        if "selected_fields" in transformation:
            _string_list(transformation["selected_fields"], f"{path}.transformation.selected_fields", issues)
        for field in ("output", "line_endings", "start_heading", "end_rule", "source_line_endings", "content_change"):
            if field in transformation:
                _string(transformation[field], f"{path}.transformation.{field}", issues)
        if "occurrence" in transformation:
            if _integer(transformation["occurrence"], f"{path}.transformation.occurrence", issues, non_negative=True) and transformation["occurrence"] < 1:
                _issue(issues, "occurrence", f"{path}.transformation.occurrence", "must be one-based")
    freshness = value.get("freshness")
    freshness_fields = ("status", "basis", "rule", "as_of")
    if _fixed_object(freshness, f"{path}.freshness", freshness_fields, freshness_fields, issues):
        if freshness.get("status") not in ("current_at_snapshot", "stale", "unknown", "not_applicable"):
            _issue(issues, "freshness", f"{path}.freshness.status", "is unsupported")
        _string(freshness.get("basis"), f"{path}.freshness.basis", issues)
        _string(freshness.get("rule"), f"{path}.freshness.rule", issues)
        _rfc3339(freshness.get("as_of"), f"{path}.freshness.as_of", issues)
    _integer(value.get("included_utf8_bytes"), f"{path}.included_utf8_bytes", issues, non_negative=True)


def _payload_record(value: Any, path: str, issues: list[ValidationIssue]) -> None:
    fields = ("id", "source_ref", "media_type", "encoding", "content", "utf8_bytes", "digest")
    if not _fixed_object(value, path, fields, fields, issues):
        return
    for field in ("id", "source_ref", "media_type", "content"):
        _string(value.get(field), f"{path}.{field}", issues)
    if value.get("encoding") != "utf-8":
        _issue(issues, "encoding", f"{path}.encoding", "must be utf-8")
    _integer(value.get("utf8_bytes"), f"{path}.utf8_bytes", issues, non_negative=True)
    _byte_digest_record(value.get("digest"), f"{path}.digest", issues)


def _conflict_record(value: Any, path: str, issues: list[ValidationIssue]) -> None:
    fields = ("id", "affected_fields", "claims", "detection_rule", "blocking")
    if not _fixed_object(value, path, fields, fields, issues):
        return
    _string(value.get("id"), f"{path}.id", issues)
    _string_list(value.get("affected_fields"), f"{path}.affected_fields", issues)
    claims = value.get("claims")
    if not isinstance(claims, list):
        _issue(issues, "type", f"{path}.claims", "must be an array")
    else:
        for index, claim in enumerate(claims):
            _normative_value(claim, f"{path}.claims[{index}]", issues)
    _string(value.get("detection_rule"), f"{path}.detection_rule", issues)
    _boolean(value.get("blocking"), f"{path}.blocking", issues)


def _unknown_record(value: Any, path: str, issues: list[ValidationIssue]) -> None:
    fields = ("id", "field", "attempted_resolution", "owner", "consequence", "blocking")
    if not _fixed_object(value, path, fields, fields, issues):
        return
    for field in ("id", "field", "attempted_resolution", "owner", "consequence"):
        _string(value.get(field), f"{path}.{field}", issues, non_empty=True)
    _boolean(value.get("blocking"), f"{path}.blocking", issues)


def _omission_record(value: Any, path: str, issues: list[ValidationIssue]) -> None:
    fields = (
        "id", "record_type", "boundary", "individual", "rule", "reason",
        "consequence", "blocking", "reconsideration_condition",
    )
    if not _fixed_object(value, path, fields, fields, issues):
        return
    _string(value.get("id"), f"{path}.id", issues, non_empty=True)
    record_type = value.get("record_type")
    if record_type not in ("individual", "policy_class"):
        _issue(issues, "omission_type", f"{path}.record_type", "is unsupported")
    for field in ("boundary", "rule", "reason", "consequence", "reconsideration_condition"):
        _string(value.get(field), f"{path}.{field}", issues, non_empty=True)
    individual = value.get("individual")
    if record_type == "individual":
        if not isinstance(individual, Mapping) or not individual:
            _issue(
                issues,
                "omission_individual_identity",
                f"{path}.individual",
                "must be a nonempty object for an individual omission",
            )
        else:
            _normative_value(individual, f"{path}.individual", issues)
    elif record_type == "policy_class":
        if individual is not None:
            _issue(
                issues,
                "omission_individual_identity",
                f"{path}.individual",
                "must be null for a policy-class omission",
            )
            if isinstance(individual, Mapping):
                _normative_value(individual, f"{path}.individual", issues)
    elif individual is not None:
        if not isinstance(individual, Mapping):
            _issue(issues, "type", f"{path}.individual", "must be an object or null")
        else:
            _normative_value(individual, f"{path}.individual", issues)
    _boolean(value.get("blocking"), f"{path}.blocking", issues)


def validate_context_package(value: Any) -> ValidationResult:
    """Validate the structural v1 boundary without claiming consumability."""

    issues: list[ValidationIssue] = []
    top_fields = (
        "schema_version",
        "package",
        "compilation",
        "repository",
        "task",
        "declared_constraints",
        "sources",
        "payloads",
        "budget",
        "conflicts",
        "unknowns",
        "omissions",
        "validation",
        "consumer_contract",
    )
    if not _fixed_object(value, "$", top_fields, top_fields, issues):
        return ValidationResult(tuple(issues))
    if value.get("schema_version") != CONTEXT_PACKAGE_SCHEMA_VERSION:
        _issue(issues, "unsupported_version", "$.schema_version", "unsupported context-package schema")
    package = value.get("package")
    package_fields = (
        "id", "identity_digest", "digest", "status", "generated", "canonical",
        "consumability", "non_consumable_reasons",
    )
    if _fixed_object(package, "$.package", package_fields, package_fields, issues):
        _string(package.get("id"), "$.package.id", issues)
        package_id = package.get("id")
        if not isinstance(package_id, str) or not re.fullmatch(
            r"tcp-[0-9a-f]{24}", package_id
        ):
            _issue(
                issues,
                "package_id",
                "$.package.id",
                "must match ^tcp-[0-9a-f]{24}$",
            )
        _digest_record(package.get("identity_digest"), "$.package.identity_digest", issues)
        _digest_record(package.get("digest"), "$.package.digest", issues)
        _string(package.get("status"), "$.package.status", issues, non_empty=True)
        _boolean(package.get("generated"), "$.package.generated", issues)
        _boolean(package.get("canonical"), "$.package.canonical", issues)
        if package.get("generated") is not True or package.get("canonical") is not False:
            _issue(issues, "classification", "$.package", "must be generated and non-canonical")
        if package.get("consumability") not in ("consumable", "non_consumable"):
            _issue(issues, "consumability", "$.package.consumability", "is unsupported")
        _string_list(package.get("non_consumable_reasons"), "$.package.non_consumable_reasons", issues)
    compilation = value.get("compilation")
    compilation_fields = ("compiler", "selection_policy", "budget_policy", "request_digest", "as_of")
    if _fixed_object(compilation, "$.compilation", compilation_fields, compilation_fields, issues):
        compiler = compilation.get("compiler")
        if _fixed_object(compiler, "$.compilation.compiler", ("identity", "version"), ("identity", "version"), issues):
            _string(
                compiler.get("identity"),
                "$.compilation.compiler.identity",
                issues,
                non_empty=True,
            )
            _string(
                compiler.get("version"),
                "$.compilation.compiler.version",
                issues,
                non_empty=True,
            )
        _policy_reference(compilation.get("selection_policy"), "$.compilation.selection_policy", issues)
        _policy_reference(compilation.get("budget_policy"), "$.compilation.budget_policy", issues)
        selection_reference = compilation.get("selection_policy")
        if isinstance(selection_reference, Mapping) and (
            selection_reference.get("id") != SELECTION_POLICY_ID
            or selection_reference.get("version") != SELECTION_POLICY_VERSION
        ):
            _issue(issues, "unsupported_policy", "$.compilation.selection_policy", "unsupported selection-policy identity or version")
        budget_reference = compilation.get("budget_policy")
        if isinstance(budget_reference, Mapping) and (
            budget_reference.get("id") != BUDGET_POLICY_ID
            or budget_reference.get("version") != BUDGET_POLICY_VERSION
        ):
            _issue(issues, "unsupported_policy", "$.compilation.budget_policy", "unsupported budget-policy identity or version")
        _digest_record(compilation.get("request_digest"), "$.compilation.request_digest", issues)
        _rfc3339(compilation.get("as_of"), "$.compilation.as_of", issues)
    repository = value.get("repository")
    repository_fields = (
        "identity", "requested_revision", "object_format", "commit", "tree",
        "snapshot_mode", "snapshot_fingerprint", "protected_references",
    )
    repository_allowed = repository_fields + ("advisory_branch",)
    if _fixed_object(repository, "$.repository", repository_fields, repository_allowed, issues):
        for field in ("identity", "requested_revision", "object_format", "commit", "tree"):
            _string(
                repository.get(field),
                f"$.repository.{field}",
                issues,
                non_empty=True,
            )
        if repository.get("snapshot_mode") != "clean_committed":
            _issue(
                issues,
                "snapshot_mode",
                "$.repository.snapshot_mode",
                "must be clean_committed",
            )
        if "advisory_branch" in repository and repository["advisory_branch"] is not None:
            _string(repository["advisory_branch"], "$.repository.advisory_branch", issues)
        _digest_record(repository.get("snapshot_fingerprint"), "$.repository.snapshot_fingerprint", issues)
        protected_references = repository.get("protected_references")
        if not isinstance(protected_references, list):
            _issue(issues, "type", "$.repository.protected_references", "must be an array")
        else:
            for index, record in enumerate(protected_references):
                _protected_reference(record, f"$.repository.protected_references[{index}]", issues)
    _attributed_group(value.get("task"), "$.task", TASK_FIELDS, issues, allow_unknown=True)
    _attributed_group(
        value.get("declared_constraints"),
        "$.declared_constraints",
        CONSTRAINT_FIELDS,
        issues,
        allow_unknown=True,
    )
    record_validators = {
        "sources": _source_record,
        "payloads": _payload_record,
        "conflicts": _conflict_record,
        "unknowns": _unknown_record,
        "omissions": _omission_record,
    }
    for field, validator in record_validators.items():
        records = value.get(field)
        if not isinstance(records, list):
            _issue(issues, "type", f"$.{field}", "must be an array")
        else:
            for index, record in enumerate(records):
                validator(record, f"$.{field}[{index}]", issues)
    budget = value.get("budget")
    budget_fields = ("normative_unit", "limit_bytes", "allocation_order", "measurement", "outcome")
    if _fixed_object(budget, "$.budget", budget_fields, budget_fields, issues):
        if budget.get("normative_unit") != "utf8_bytes":
            _issue(issues, "budget_unit", "$.budget.normative_unit", "must be utf8_bytes")
        _integer(budget.get("limit_bytes"), "$.budget.limit_bytes", issues, non_negative=True)
        _string_list(budget.get("allocation_order"), "$.budget.allocation_order", issues)
        measurement = budget.get("measurement")
        measurement_fields = ("control_envelope_bytes", "included_payload_bytes", "consumed_bytes", "remaining_bytes")
        if _fixed_object(measurement, "$.budget.measurement", measurement_fields, measurement_fields, issues):
            for field in measurement_fields:
                _integer(measurement.get(field), f"$.budget.measurement.{field}", issues, non_negative=True)
        _string(budget.get("outcome"), "$.budget.outcome", issues)
    validation = value.get("validation")
    validation_fields = ("status", "executable_validation_performed", "checks", "errors", "limitations")
    if _fixed_object(validation, "$.validation", validation_fields, validation_fields, issues):
        _string(validation.get("status"), "$.validation.status", issues)
        _boolean(validation.get("executable_validation_performed"), "$.validation.executable_validation_performed", issues)
        checks = validation.get("checks")
        if not isinstance(checks, list):
            _issue(issues, "type", "$.validation.checks", "must be an array")
        else:
            for index, check in enumerate(checks):
                check_path = f"$.validation.checks[{index}]"
                if _fixed_object(check, check_path, ("invariant", "status"), ("invariant", "status"), issues):
                    _string(check.get("invariant"), f"{check_path}.invariant", issues)
                    _string(check.get("status"), f"{check_path}.status", issues)
        for field in ("errors", "limitations"):
            _string_list(validation.get(field), f"$.validation.{field}", issues)
    contract = value.get("consumer_contract")
    contract_fields = ("version", "must", "must_not", "stop_conditions", "live_revalidation_required")
    if _fixed_object(contract, "$.consumer_contract", contract_fields, contract_fields, issues):
        if contract.get("version") != CONSUMER_CONTRACT_VERSION:
            _issue(issues, "unsupported_version", "$.consumer_contract.version", "unsupported consumer contract")
        for field in ("must", "must_not", "stop_conditions", "live_revalidation_required"):
            _string_list(contract.get(field), f"$.consumer_contract.{field}", issues)
    return ValidationResult(tuple(issues))


def _mutable_json_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _mutable_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_mutable_json_value(item) for item in value]
    return value


def _normalized_repository_path(value: Any) -> bool:
    if (
        not isinstance(value, str)
        or not value
        or value.startswith("/")
        or "\\" in value
        or "\x00" in value
    ):
        return False
    return all(part not in ("", ".", "..") for part in value.split("/"))


def _expected_policy_reference(
    policy_id: str,
    version: str,
    digest_value: str,
) -> dict[str, Any]:
    return {
        "id": policy_id,
        "version": version,
        "digest": {
            "algorithm": "sha256",
            "canonicalization": CANONICALIZATION,
            "value": digest_value,
        },
    }


def _payload_matches_fixed_selector(
    rule: _FirstSliceRuleContract,
    content: str,
) -> bool:
    payload_bytes = content.encode("utf-8")
    if rule.selector_type == "yaml_fields":
        try:
            parsed = json.loads(content)
        except (json.JSONDecodeError, TypeError, ValueError):
            return False
        return (
            isinstance(parsed, dict)
            and set(parsed) == set(rule.selector_fields)
            and parsed.get("id") == "EO-2026-013"
            and parsed.get("status") == "reviewed"
            and canonicalize(parsed) == payload_bytes
        )

    assert rule.heading_text is not None
    return (
        content == rule.heading_text
        or content.startswith(f"{rule.heading_text}\n")
        or content.startswith(f"{rule.heading_text}\r\n")
    )


def _capacity_issue(
    issues: list[ValidationIssue],
    code: str,
    path: str,
    message: str,
) -> None:
    _issue(issues, code, path, message)


def _validate_capacity_omission(
    omission: Mapping[str, Any],
    path: str,
    repository: Mapping[str, Any],
    included_source_ids: set[str],
    included_payload_ids: set[str],
    issues: list[ValidationIssue],
) -> None:
    if omission.get("record_type") != "individual":
        _capacity_issue(
            issues,
            "budget_omission_record_type",
            f"{path}.record_type",
            "must be individual for a B2b capacity omission",
        )
    if omission.get("blocking") is not False:
        _capacity_issue(
            issues,
            "budget_omission_blocking",
            f"{path}.blocking",
            "must be false for a B2b capacity omission",
        )
    if omission.get("reason") != BUDGET_CAPACITY_OMISSION_REASON:
        _capacity_issue(
            issues,
            "budget_omission_reason",
            f"{path}.reason",
            "must match the stable whole-pair capacity reason",
        )
    if omission.get("reconsideration_condition") != BUDGET_CAPACITY_RECONSIDERATION:
        _capacity_issue(
            issues,
            "budget_omission_reconsideration",
            f"{path}.reconsideration_condition",
            "must match the stable capacity reconsideration condition",
        )

    individual = omission.get("individual")
    if not isinstance(individual, Mapping):
        _capacity_issue(
            issues,
            "budget_omission_individual",
            f"{path}.individual",
            "must be the complete deterministic optional-pair identity",
        )
        return
    individual_fields = {
        "source_id",
        "payload_id",
        "path",
        "structured_object_identity",
        "selector",
        "selection_rule",
        "budget_tier",
        "commit",
        "immutable_source_identity",
        "source_content_digest",
        "payload_utf8_bytes",
        "payload_digest",
    }
    if set(individual) != individual_fields:
        _capacity_issue(
            issues,
            "budget_omission_individual_surface",
            f"{path}.individual",
            "must contain exactly the fixed optional-pair identity fields",
        )

    selection_rule = individual.get("selection_rule")
    rule = fixed_first_slice_rule(selection_rule)
    if rule is None:
        _capacity_issue(
            issues,
            "budget_omission_rule_identity",
            f"{path}.individual.selection_rule",
            "must identify an accepted fixed first-slice rule",
        )
    else:
        expected_rule_fields = {
            "path": rule.path,
            "structured_object_identity": rule.structured_object_identity,
            "selector": rule.selector_descriptor,
            "budget_tier": rule.budget_tier,
        }
        for field, expected in expected_rule_fields.items():
            if individual.get(field) != expected:
                _capacity_issue(
                    issues,
                    "budget_omission_rule_projection",
                    f"{path}.individual.{field}",
                    "does not match the fixed omitted-rule contract",
                )
        if omission.get("boundary") != rule.normalized_identity:
            _capacity_issue(
                issues,
                "budget_omission_boundary",
                f"{path}.boundary",
                "must equal the fixed omitted-rule normalized identity",
            )
        if rule.budget_tier != "optional_evidence":
            _capacity_issue(
                issues,
                "budget_omission_rule_not_optional",
                f"{path}.individual.selection_rule",
                "the fixed first-slice contract does not make this rule optional",
            )

    commit = individual.get("commit")
    if commit != repository.get("commit"):
        _capacity_issue(
            issues,
            "budget_omission_commit",
            f"{path}.individual.commit",
            "must match the package repository commit",
        )
    immutable = individual.get("immutable_source_identity")
    immutable_value = None
    if not isinstance(immutable, Mapping) or set(immutable) != {
        "type",
        "object_format",
        "value",
    }:
        _capacity_issue(
            issues,
            "budget_omission_immutable_identity",
            f"{path}.individual.immutable_source_identity",
            "must be the exact immutable Git blob identity shape",
        )
    else:
        immutable_value = immutable.get("value")
        if (
            immutable.get("type") != "git_blob"
            or immutable.get("object_format") != repository.get("object_format")
            or not isinstance(immutable_value, str)
            or GIT_SHA1.fullmatch(immutable_value) is None
        ):
            _capacity_issue(
                issues,
                "budget_omission_immutable_identity",
                f"{path}.individual.immutable_source_identity",
                "must identify one SHA-1 Git blob in the package object format",
            )

    source_digest = individual.get("source_content_digest")
    if (
        not isinstance(source_digest, Mapping)
        or set(source_digest) != {"algorithm", "value"}
        or source_digest.get("algorithm") != "sha256"
        or not isinstance(source_digest.get("value"), str)
        or LOWER_HEX_64.fullmatch(source_digest["value"]) is None
    ):
        _capacity_issue(
            issues,
            "budget_omission_source_digest",
            f"{path}.individual.source_content_digest",
            "must carry one SHA-256 whole-source claim",
        )

    source_id = individual.get("source_id")
    expected_source_id = None
    if rule is not None and isinstance(commit, str) and isinstance(immutable_value, str):
        try:
            expected_source_id = source_identifier(
                rule.path,
                commit,
                immutable_value,
                rule.selector_descriptor,
            )
        except (TypeError, ValueError):
            expected_source_id = None
    if source_id != expected_source_id:
        _capacity_issue(
            issues,
            "budget_omission_source_id",
            f"{path}.individual.source_id",
            "does not match the omitted immutable source identity",
        )

    payload_digest = individual.get("payload_digest")
    payload_digest_value = None
    if (
        not isinstance(payload_digest, Mapping)
        or set(payload_digest) != {"algorithm", "value"}
        or payload_digest.get("algorithm") != "sha256"
        or not isinstance(payload_digest.get("value"), str)
        or LOWER_HEX_64.fullmatch(payload_digest["value"]) is None
    ):
        _capacity_issue(
            issues,
            "budget_omission_payload_digest",
            f"{path}.individual.payload_digest",
            "must carry one SHA-256 omitted-payload digest",
        )
    else:
        payload_digest_value = payload_digest["value"]
    expected_payload_id = None
    if isinstance(payload_digest_value, str):
        try:
            expected_payload_id = payload_identifier(payload_digest_value)
        except (TypeError, ValueError):
            expected_payload_id = None
    payload_id = individual.get("payload_id")
    if payload_id != expected_payload_id:
        _capacity_issue(
            issues,
            "budget_omission_payload_id",
            f"{path}.individual.payload_id",
            "does not match the omitted payload digest",
        )

    payload_bytes = individual.get("payload_utf8_bytes")
    if (
        isinstance(payload_bytes, bool)
        or not isinstance(payload_bytes, int)
        or not 0 <= payload_bytes <= MAX_SAFE_INTEGER
    ):
        _capacity_issue(
            issues,
            "budget_omission_payload_size",
            f"{path}.individual.payload_utf8_bytes",
            "must be a nonnegative safe UTF-8 byte count",
        )
    elif omission.get("consequence") != budget_capacity_consequence(payload_bytes):
        _capacity_issue(
            issues,
            "budget_omission_consequence",
            f"{path}.consequence",
            "must be derived exactly from the omitted payload byte count",
        )

    if (
        isinstance(source_id, str)
        and source_id in included_source_ids
    ) or (
        isinstance(payload_id, str)
        and payload_id in included_payload_ids
    ):
        _capacity_issue(
            issues,
            "budget_omission_overlap",
            f"{path}.individual",
            "omitted source and payload IDs must not overlap included records",
        )


def validate_compiled_context_package(value: Any) -> ValidationResult:
    """Recompute B2b integrity and consumability after structural validation."""

    package = _mutable_json_value(value)
    structural = validate_context_package(package)
    if not structural.valid:
        return structural

    issues: list[ValidationIssue] = []
    package_record = package["package"]
    compilation = package["compilation"]
    repository = package["repository"]
    sources = package["sources"]
    payloads = package["payloads"]
    omissions = package["omissions"]
    unknowns = package["unknowns"]
    conflicts = package["conflicts"]
    budget = package["budget"]

    if package_record["status"] != "compiled":
        _issue(
            issues,
            "compilation_status",
            "$.package.status",
            "B2b executable packages must have status compiled",
        )

    expected_selection = _expected_policy_reference(
        SELECTION_POLICY_ID,
        SELECTION_POLICY_VERSION,
        SELECTION_POLICY_DIGEST_VALUE,
    )
    expected_budget = _expected_policy_reference(
        BUDGET_POLICY_ID,
        BUDGET_POLICY_VERSION,
        BUDGET_POLICY_DIGEST_VALUE,
    )
    if compilation["selection_policy"] != expected_selection:
        _issue(
            issues,
            "selection_policy_identity",
            "$.compilation.selection_policy",
            "must match the accepted first-slice selection policy",
        )
    if compilation["budget_policy"] != expected_budget:
        _issue(
            issues,
            "budget_policy_identity",
            "$.compilation.budget_policy",
            "must match the accepted first-slice budget policy",
        )

    request_surface = {
        "repository_request": {
            "identity": repository["identity"],
            "requested_revision": repository["requested_revision"],
        },
        "task": package["task"],
        "declared_constraints": package["declared_constraints"],
        "selection_policy": compilation["selection_policy"],
        "budget_policy": compilation["budget_policy"],
        "protected_references": repository["protected_references"],
        "as_of": compilation["as_of"],
    }
    expected_request_digest = request_digest(request_surface).as_dict()
    if compilation["request_digest"] != expected_request_digest:
        _issue(
            issues,
            "request_digest_mismatch",
            "$.compilation.request_digest",
            "does not match the request surface reconstructed from the package",
        )

    if repository["object_format"] != "sha1":
        _issue(
            issues,
            "object_format",
            "$.repository.object_format",
            "the accepted first slice requires sha1 Git identities",
        )
    if repository["requested_revision"] != repository["commit"]:
        _issue(
            issues,
            "requested_revision_commit_linkage",
            "$.repository.requested_revision",
            "must equal the exact compiled repository commit",
        )
    for field in ("commit", "tree"):
        if not GIT_SHA1.fullmatch(repository[field]):
            _issue(
                issues,
                "git_identity",
                f"$.repository.{field}",
                "must be 40 lowercase hexadecimal characters",
            )
    expected_snapshot_fingerprint = snapshot_fingerprint(
        repository["identity"],
        repository["object_format"],
        repository["commit"],
        repository["tree"],
        repository["snapshot_mode"],
    ).as_dict()
    if repository["snapshot_fingerprint"] != expected_snapshot_fingerprint:
        _issue(
            issues,
            "snapshot_fingerprint_mismatch",
            "$.repository.snapshot_fingerprint",
            "does not match the exact repository snapshot surface",
        )

    identity_digest, package_id = package_identity(
        compilation["request_digest"]["value"],
        repository["snapshot_fingerprint"]["value"],
    )
    if package_record["identity_digest"] != identity_digest.as_dict():
        _issue(
            issues,
            "package_identity_digest_mismatch",
            "$.package.identity_digest",
            "does not match request digest and snapshot fingerprint",
        )
    if package_record["id"] != package_id:
        _issue(
            issues,
            "package_id_mismatch",
            "$.package.id",
            "does not match the package identity digest",
        )

    if len(sources) != len(payloads):
        _issue(
            issues,
            "source_payload_count",
            "$.payloads",
            "must contain exactly one payload for every source",
        )
    seen_source_ids: set[str] = set()
    seen_payload_ids: set[str] = set()
    seen_rule_ids: set[str] = set()
    source_rule_order: list[str] = []
    for index, source in enumerate(sources):
        source_path = f"$.sources[{index}]"
        selection_rule = source["selection_rule"]
        source_rule_order.append(selection_rule)
        rule = fixed_first_slice_rule(selection_rule)
        if rule is None:
            _issue(
                issues,
                "unsupported_source_rule",
                f"{source_path}.selection_rule",
                "is outside the fixed first-slice rule contract",
            )
        elif selection_rule in seen_rule_ids:
            _issue(
                issues,
                "duplicate_source_rule",
                f"{source_path}.selection_rule",
                "must occur exactly once",
            )
        seen_rule_ids.add(selection_rule)

        if not _normalized_repository_path(source["path"]):
            _issue(
                issues,
                "repository_path",
                f"{source_path}.path",
                "must be an exact normalized repository-relative POSIX path",
            )
        if source["commit"] != repository["commit"]:
            _issue(
                issues,
                "source_commit",
                f"{source_path}.commit",
                "must match the package repository commit",
            )
        immutable = source["immutable_source_identity"]
        if (
            immutable["type"] != "git_blob"
            or immutable["object_format"] != repository["object_format"]
            or not GIT_SHA1.fullmatch(immutable["value"])
        ):
            _issue(
                issues,
                "immutable_source_identity",
                f"{source_path}.immutable_source_identity",
                "must be a valid blob identity in the package object format",
            )
        try:
            expected_source_id = source_identifier(
                source["path"],
                source["commit"],
                immutable["value"],
                source["selector"],
            )
        except (TypeError, ValueError):
            expected_source_id = None
        if source["id"] != expected_source_id:
            _issue(
                issues,
                "source_id_mismatch",
                f"{source_path}.id",
                "does not match the source identity surface",
            )
        if source["id"] in seen_source_ids:
            _issue(
                issues,
                "duplicate_source_id",
                f"{source_path}.id",
                "must be unique",
            )
        seen_source_ids.add(source["id"])

        if index >= len(payloads):
            continue
        payload = payloads[index]
        payload_path = f"$.payloads[{index}]"
        payload_bytes = payload["content"].encode("utf-8")
        expected_payload_digest = {
            "algorithm": "sha256",
            "value": sha256_bytes(payload_bytes),
        }
        if payload["digest"] != expected_payload_digest:
            _issue(
                issues,
                "payload_digest_mismatch",
                f"{payload_path}.digest",
                "does not match the exact UTF-8 content bytes",
            )
        expected_payload_id = payload_identifier(expected_payload_digest["value"])
        if payload["id"] != expected_payload_id:
            _issue(
                issues,
                "payload_id_mismatch",
                f"{payload_path}.id",
                "does not match the payload digest",
            )
        if payload["id"] in seen_payload_ids:
            _issue(
                issues,
                "duplicate_payload_id",
                f"{payload_path}.id",
                "must be unique",
            )
        seen_payload_ids.add(payload["id"])
        if payload["utf8_bytes"] != len(payload_bytes):
            _issue(
                issues,
                "payload_size_mismatch",
                f"{payload_path}.utf8_bytes",
                "must equal the exact UTF-8 content byte count",
            )
        if source["included_utf8_bytes"] != len(payload_bytes):
            _issue(
                issues,
                "source_size_mismatch",
                f"{source_path}.included_utf8_bytes",
                "must equal the linked payload byte count",
            )
        if (
            source["payload_ref"] != payload["id"]
            or payload["source_ref"] != source["id"]
        ):
            _issue(
                issues,
                "source_payload_linkage",
                source_path,
                "source and payload references must be reciprocal and ordered",
            )

        if rule is not None:
            fixed_source_fields = {
                "path": rule.path,
                "structured_object_identity": rule.structured_object_identity,
                "selector": rule.selector_descriptor,
                "priority_tier": rule.priority_tier,
                "selection_rule": rule.rule_id,
                "selection_reason": rule.selection_reason,
                "trigger": rule.trigger,
                "selection_chain": list(rule.selection_chain),
                "authority_class": rule.authority_class,
                "canonical_owner": rule.canonical_owner,
            }
            for field, expected in fixed_source_fields.items():
                if source[field] != expected:
                    _issue(
                        issues,
                        "fixed_source_contract_mismatch",
                        f"{source_path}.{field}",
                        "does not match the accepted fixed-rule projection",
                    )
            if source["freshness"] != fixed_first_slice_freshness(
                rule,
                compilation["as_of"],
            ):
                _issue(
                    issues,
                    "freshness_contract_mismatch",
                    f"{source_path}.freshness",
                    "does not match the fixed first-slice freshness behavior",
                )
            if payload["media_type"] != rule.media_type:
                _issue(
                    issues,
                    "payload_media_type",
                    f"{payload_path}.media_type",
                    "does not match the fixed selector output media type",
                )
            if not _payload_matches_fixed_selector(rule, payload["content"]):
                _issue(
                    issues,
                    "payload_selector_relationship",
                    f"{payload_path}.content",
                    "does not have the content shape required by the fixed selector",
                )
            if not fixed_first_slice_transformation_matches(
                rule,
                source["transformation"],
                payload_bytes,
            ):
                _issue(
                    issues,
                    "transformation_contract_mismatch",
                    f"{source_path}.transformation",
                    "does not match the fixed selector and payload relationship",
                )

    expected_rule_order = [rule.rule_id for rule in FIRST_SLICE_RULE_CONTRACT]
    if source_rule_order != expected_rule_order:
        _issue(
            issues,
            "source_ordering",
            "$.sources",
            "must contain the five fixed mandatory rules once in deterministic order",
        )
    for rule in FIRST_SLICE_RULE_CONTRACT:
        if rule.budget_tier != "optional_evidence" and source_rule_order.count(
            rule.rule_id
        ) != 1:
            _issue(
                issues,
                "mandatory_source_completeness",
                "$.sources",
                f"must contain fixed mandatory rule {rule.rule_id} exactly once",
            )

    seen_unknown_ids: set[str] = set()
    for index, unknown in enumerate(unknowns):
        try:
            expected_unknown_id = unknown_identifier(
                unknown["field"],
                unknown["attempted_resolution"],
                unknown["owner"],
                unknown["consequence"],
                unknown["blocking"],
            )
        except (TypeError, ValueError):
            expected_unknown_id = None
            _issue(
                issues,
                "unknown_identity_surface",
                f"$.unknowns[{index}]",
                "must contain a complete nonempty unknown identity surface",
            )
        if unknown["id"] != expected_unknown_id:
            _issue(
                issues,
                "unknown_id_mismatch",
                f"$.unknowns[{index}].id",
                "does not match the retained unknown identity surface",
            )
        if unknown["id"] in seen_unknown_ids:
            _issue(
                issues,
                "duplicate_unknown_id",
                f"$.unknowns[{index}].id",
                "must be unique",
            )
        seen_unknown_ids.add(unknown["id"])

    seen_omission_ids: set[str] = set()
    capacity_omissions = 0
    for index, omission in enumerate(omissions):
        omission_path = f"$.omissions[{index}]"
        try:
            expected_omission_id = omission_identifier(
                omission["rule"],
                omission["boundary"],
                omission["individual"],
            )
        except (TypeError, ValueError):
            expected_omission_id = None
            _issue(
                issues,
                "omission_identity_surface",
                omission_path,
                "must contain a complete nonempty omission identity surface",
            )
        if omission["id"] != expected_omission_id:
            _issue(
                issues,
                "omission_id_mismatch",
                f"$.omissions[{index}].id",
                "does not match the omission identity surface",
            )
        if omission["id"] in seen_omission_ids:
            _issue(
                issues,
                "duplicate_omission_id",
                f"$.omissions[{index}].id",
                "must be unique",
            )
        seen_omission_ids.add(omission["id"])
        if omission["rule"] == BUDGET_CAPACITY_OMISSION_RULE:
            capacity_omissions += 1
            _validate_capacity_omission(
                omission,
                omission_path,
                repository,
                seen_source_ids,
                seen_payload_ids,
                issues,
            )

    if conflicts:
        _issue(
            issues,
            "unsupported_conflict_input",
            "$.conflicts",
            "the accepted B2b first slice emits no inferred conflicts",
        )

    expected_allocation = [
        "mandatory_control_envelope",
        "mandatory_authoritative_sources",
        "required_supporting_sources",
        "optional_evidence",
    ]
    if (
        budget["normative_unit"] != "utf8_bytes"
        or budget["limit_bytes"] != 65536
        or budget["allocation_order"] != expected_allocation
    ):
        _issue(
            issues,
            "budget_policy_projection",
            "$.budget",
            "must project the accepted budget policy exactly",
        )
    expected_control_bytes = control_envelope_bytes(package)
    expected_payload_bytes = sum(
        len(payload["content"].encode("utf-8")) for payload in payloads
    )
    expected_consumed = expected_control_bytes + expected_payload_bytes
    expected_remaining = max(budget["limit_bytes"] - expected_consumed, 0)
    expected_measurement = {
        "control_envelope_bytes": expected_control_bytes,
        "included_payload_bytes": expected_payload_bytes,
        "consumed_bytes": expected_consumed,
        "remaining_bytes": expected_remaining,
    }
    if budget["measurement"] != expected_measurement:
        _issue(
            issues,
            "budget_measurement_mismatch",
            "$.budget.measurement",
            "does not match exact control-envelope and payload-byte arithmetic",
        )
    if expected_consumed > budget["limit_bytes"]:
        expected_outcome = "budget_exceeded"
    elif capacity_omissions:
        expected_outcome = "within_budget_optional_sources_omitted"
    else:
        expected_outcome = "within_budget"
    if budget["outcome"] != expected_outcome:
        _issue(
            issues,
            "budget_outcome",
            "$.budget.outcome",
            "does not match measured capacity and optional omissions",
        )

    if package["consumer_contract"] != consumer_contract_value():
        _issue(
            issues,
            "consumer_contract_mismatch",
            "$.consumer_contract",
            "must match the fixed integrity-bound first-slice contract",
        )
    if package["validation"] != executable_validation_value():
        _issue(
            issues,
            "validation_record_mismatch",
            "$.validation",
            "must match the fixed executable B2b validation record",
        )

    expected_reasons: list[str] = []
    if expected_consumed > budget["limit_bytes"]:
        expected_reasons.append("budget_exceeded")
    if any(conflict["blocking"] for conflict in conflicts):
        expected_reasons.append("blocking_conflict")
    if any(unknown["blocking"] for unknown in unknowns):
        expected_reasons.append("blocking_unknown")
    if any(omission["blocking"] for omission in omissions):
        expected_reasons.append("blocking_omission")
    expected_consumability = (
        "non_consumable" if expected_reasons else "consumable"
    )
    if package_record["consumability"] != expected_consumability:
        _issue(
            issues,
            "consumability_mismatch",
            "$.package.consumability",
            "does not match blocking records and measured budget state",
        )
    if package_record["non_consumable_reasons"] != expected_reasons:
        _issue(
            issues,
            "consumability_reasons_mismatch",
            "$.package.non_consumable_reasons",
            "must be the exact stable reasons implied by package state",
        )

    expected_package_digest = package_digest(package).as_dict()
    if package_record["digest"] != expected_package_digest:
        _issue(
            issues,
            "package_digest_mismatch",
            "$.package.digest",
            "does not match the complete package integrity surface",
        )
    return ValidationResult(tuple(issues))


def require_valid(result: ValidationResult) -> None:
    if not result.valid:
        raise ContractValidationError(result)
