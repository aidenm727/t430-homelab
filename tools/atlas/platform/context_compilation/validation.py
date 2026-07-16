"""Repository-local validation for the bounded task-context v1 contracts."""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any, Iterable

from atlas.platform.context_compilation.canonical_json import (
    MAX_SAFE_INTEGER,
    MIN_SAFE_INTEGER,
)
from atlas.platform.context_compilation.digests import (
    CANONICALIZATION,
    budget_policy_digest,
    selection_policy_digest,
)
from atlas.platform.context_compilation.models import ValidationIssue, ValidationResult


SELECTION_POLICY_SCHEMA_VERSION = "aiden.task-context.selection-policy/v1"
BUDGET_POLICY_SCHEMA_VERSION = "aiden.task-context.budget-policy/v1"
COMPILATION_REQUEST_SCHEMA_VERSION = "aiden.task-context.compilation-request/v1"
CONTEXT_PACKAGE_SCHEMA_VERSION = "aiden.task-context/v1"
CONSUMER_CONTRACT_VERSION = "aiden.task-context-consumer/v1"
SELECTION_POLICY_ID = "example.read-only-architecture-assessment"
BUDGET_POLICY_ID = "example.utf8-byte-budget"
EXAMPLE_POLICY_VERSION = "1.0.0"

RFC3339_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
LOWER_HEX_64 = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA1 = re.compile(r"^[0-9a-f]{40}$")


class ContractValidationError(ValueError):
    """Raised when a bounded v1 contract is not valid."""

    def __init__(self, result: ValidationResult):
        self.result = result
        detail = "; ".join(
            f"{issue.path}: {issue.message}" for issue in result.issues
        )
        super().__init__(detail or "contract validation failed")


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
    if value.get("maximum_sensitivity") not in (
        "public",
        "ordinary_personal",
        "sensitive",
        "highly_restricted",
    ):
        _issue(
            issues,
            "maximum_sensitivity",
            "$.maximum_sensitivity",
            "is not an accepted v1 sensitivity",
        )
    if value.get("id") != SELECTION_POLICY_ID or value.get("version") != EXAMPLE_POLICY_VERSION:
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
            rule_fields = ("id", "type", "priority_tier", "source", "selector")
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
            source = rule.get("source")
            source_allowed = ("kind", "path", "object_type", "field_contract_owner")
            if _fixed_object(source, f"{path}.source", ("kind",), source_allowed, issues):
                if source.get("kind") not in ("repository_object", "document"):
                    _issue(
                        issues,
                        "source_kind",
                        f"{path}.source.kind",
                        "must be repository_object or document",
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
    if value.get("id") != BUDGET_POLICY_ID or value.get("version") != EXAMPLE_POLICY_VERSION:
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
        or selection_reference.get("version") != EXAMPLE_POLICY_VERSION
    ):
        _issue(issues, "unsupported_policy", "$.selection_policy", "unsupported selection-policy identity or version")
    budget_reference = value.get("budget_policy")
    if isinstance(budget_reference, Mapping) and (
        budget_reference.get("id") != BUDGET_POLICY_ID
        or budget_reference.get("version") != EXAMPLE_POLICY_VERSION
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
        _string(value.get(field), f"{path}.{field}", issues)
    _boolean(value.get("blocking"), f"{path}.blocking", issues)


def _omission_record(value: Any, path: str, issues: list[ValidationIssue]) -> None:
    fields = (
        "id", "record_type", "boundary", "individual", "rule", "reason",
        "consequence", "blocking", "reconsideration_condition",
    )
    if not _fixed_object(value, path, fields, fields, issues):
        return
    _string(value.get("id"), f"{path}.id", issues)
    if value.get("record_type") not in ("individual", "policy_class"):
        _issue(issues, "omission_type", f"{path}.record_type", "is unsupported")
    for field in ("boundary", "rule", "reason", "consequence", "reconsideration_condition"):
        _string(value.get(field), f"{path}.{field}", issues)
    individual = value.get("individual")
    if individual is not None:
        if not isinstance(individual, Mapping):
            _issue(issues, "type", f"{path}.individual", "must be an object or null")
        else:
            _normative_value(individual, f"{path}.individual", issues)
    if value.get("record_type") == "policy_class" and individual is not None:
        _issue(issues, "omission_individual", f"{path}.individual", "must be null for a policy class")
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
            or selection_reference.get("version") != EXAMPLE_POLICY_VERSION
        ):
            _issue(issues, "unsupported_policy", "$.compilation.selection_policy", "unsupported selection-policy identity or version")
        budget_reference = compilation.get("budget_policy")
        if isinstance(budget_reference, Mapping) and (
            budget_reference.get("id") != BUDGET_POLICY_ID
            or budget_reference.get("version") != EXAMPLE_POLICY_VERSION
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


def require_valid(result: ValidationResult) -> None:
    if not result.valid:
        raise ContractValidationError(result)
