"""Immutable values for task-context foundations and selectors."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Tuple, cast

from atlas.platform.context_compilation.canonical_json import (
    MAX_SAFE_INTEGER,
    MIN_SAFE_INTEGER,
)


class ModelValueError(ValueError):
    """Raised when a value cannot enter the immutable typed domain model."""


def deep_freeze(value: Any) -> Any:
    """Copy and recursively freeze one supported normative model value."""

    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        if not MIN_SAFE_INTEGER <= value <= MAX_SAFE_INTEGER:
            raise ModelValueError(
                f"integer {value} is outside [{MIN_SAFE_INTEGER}, {MAX_SAFE_INTEGER}]"
            )
        return value
    if isinstance(value, str):
        if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
            raise ModelValueError("strings must contain only Unicode scalar values")
        return value
    if isinstance(value, (list, tuple)):
        return tuple(deep_freeze(item) for item in value)
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ModelValueError("model mapping keys must be strings")
            frozen[key] = deep_freeze(item)
        return MappingProxyType(frozen)
    raise ModelValueError(f"unsupported model value type: {type(value).__name__}")


@dataclass(frozen=True)
class DigestRecord:
    algorithm: str
    canonicalization: str
    value: str

    @classmethod
    def from_validated_mapping(cls, value: Mapping[str, Any]) -> DigestRecord:
        return cls(
            algorithm=value["algorithm"],
            canonicalization=value["canonicalization"],
            value=value["value"],
        )

    def as_dict(self) -> dict[str, str]:
        return {
            "algorithm": self.algorithm,
            "canonicalization": self.canonicalization,
            "value": self.value,
        }


@dataclass(frozen=True)
class CompilerIdentity:
    identity: str
    version: str

    @classmethod
    def from_validated_mapping(cls, value: Mapping[str, Any]) -> CompilerIdentity:
        return cls(identity=value["identity"], version=value["version"])

    def as_dict(self) -> dict[str, str]:
        return {"identity": self.identity, "version": self.version}


@dataclass(frozen=True)
class PolicyReference:
    id: str
    version: str
    digest: DigestRecord

    @classmethod
    def from_validated_mapping(cls, value: Mapping[str, Any]) -> PolicyReference:
        return cls(
            id=value["id"],
            version=value["version"],
            digest=DigestRecord.from_validated_mapping(value["digest"]),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "digest": self.digest.as_dict(),
        }


@dataclass(frozen=True)
class LoadedPolicy:
    reference: PolicyReference
    value: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", deep_freeze(self.value))

    @classmethod
    def from_validated_mapping(cls, value: Mapping[str, Any]) -> LoadedPolicy:
        return cls(
            reference=PolicyReference.from_validated_mapping(value),
            value=value,
        )


@dataclass(frozen=True)
class RepositoryRequestIdentity:
    identity: str
    requested_revision: str

    @classmethod
    def from_validated_mapping(
        cls, value: Mapping[str, Any]
    ) -> RepositoryRequestIdentity:
        return cls(
            identity=value["identity"],
            requested_revision=value["requested_revision"],
        )

    def as_dict(self) -> dict[str, str]:
        return {
            "identity": self.identity,
            "requested_revision": self.requested_revision,
        }


@dataclass(frozen=True)
class Provenance:
    source: str
    selector: str


@dataclass(frozen=True)
class Authority:
    authority_class: str
    owner: str


@dataclass(frozen=True)
class AttributedValue:
    state: str
    value: Any
    authority: Authority
    provenance: Provenance

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", deep_freeze(self.value))


@dataclass(frozen=True)
class CompilationRequest:
    schema_version: str
    repository: RepositoryRequestIdentity
    task: Mapping[str, Any]
    declared_constraints: Mapping[str, Any]
    selection_policy: PolicyReference
    budget_policy: PolicyReference
    protected_references: Tuple[Mapping[str, Any], ...]
    as_of: str
    compiler: CompilerIdentity
    fixture_evidence: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "task", deep_freeze(self.task))
        object.__setattr__(
            self, "declared_constraints", deep_freeze(self.declared_constraints)
        )
        object.__setattr__(
            self,
            "protected_references",
            cast(Tuple[Mapping[str, Any], ...], deep_freeze(self.protected_references)),
        )
        if self.fixture_evidence is not None:
            object.__setattr__(
                self, "fixture_evidence", deep_freeze(self.fixture_evidence)
            )

    @classmethod
    def from_validated_mapping(cls, value: Mapping[str, Any]) -> CompilationRequest:
        return cls(
            schema_version=value["schema_version"],
            repository=RepositoryRequestIdentity.from_validated_mapping(
                value["repository_request"]
            ),
            task=value["task"],
            declared_constraints=value["declared_constraints"],
            selection_policy=PolicyReference.from_validated_mapping(
                value["selection_policy"]
            ),
            budget_policy=PolicyReference.from_validated_mapping(value["budget_policy"]),
            protected_references=tuple(value["protected_references"]),
            as_of=value["as_of"],
            compiler=CompilerIdentity.from_validated_mapping(value["compiler"]),
            fixture_evidence=value.get("fixture_evidence"),
        )

    def as_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "schema_version": self.schema_version,
            "repository_request": self.repository.as_dict(),
            "task": self.task,
            "declared_constraints": self.declared_constraints,
            "selection_policy": self.selection_policy.as_dict(),
            "budget_policy": self.budget_policy.as_dict(),
            "protected_references": self.protected_references,
            "as_of": self.as_of,
            "compiler": self.compiler.as_dict(),
        }
        if self.fixture_evidence is not None:
            value["fixture_evidence"] = self.fixture_evidence
        return value


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    issues: Tuple[ValidationIssue, ...] = ()

    @property
    def valid(self) -> bool:
        return not self.issues


@dataclass(frozen=True)
class FoundationIdentifierValues:
    request_digest: DigestRecord
    snapshot_fingerprint: DigestRecord
    identity_digest: DigestRecord
    package_id: str


@dataclass(frozen=True)
class RepositoryIdentityEvidence:
    requested_identity: str
    origin_urls: Tuple[str, ...]
    normalized_identity: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "origin_urls", tuple(self.origin_urls))

    def as_dict(self) -> dict[str, Any]:
        return {
            "requested_identity": self.requested_identity,
            "origin_urls": list(self.origin_urls),
            "normalized_identity": self.normalized_identity,
        }


@dataclass(frozen=True)
class ProtectedReferenceIdentity:
    name: str
    expected_object: str
    actual_object: str | None
    authoritatively_targeted: bool
    selection: str
    matched: bool
    blocking: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "expected_object": self.expected_object,
            "actual_object": self.actual_object,
            "authoritatively_targeted": self.authoritatively_targeted,
            "selection": self.selection,
            "matched": self.matched,
            "blocking": self.blocking,
        }


@dataclass(frozen=True)
class RepositorySnapshot:
    repository: RepositoryIdentityEvidence
    requested_revision: str
    object_format: str
    commit: str
    tree: str
    snapshot_mode: str
    fingerprint: DigestRecord
    protected_references: Tuple[ProtectedReferenceIdentity, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "protected_references", tuple(self.protected_references)
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "repository": self.repository.as_dict(),
            "requested_revision": self.requested_revision,
            "object_format": self.object_format,
            "commit": self.commit,
            "tree": self.tree,
            "snapshot_mode": self.snapshot_mode,
            "fingerprint": self.fingerprint.as_dict(),
            "protected_references": [
                reference.as_dict() for reference in self.protected_references
            ],
        }


@dataclass(frozen=True)
class ImmutableBlob:
    path: str
    mode: str
    object_format: str
    object_id: str
    content: bytes

    def as_dict(self) -> dict[str, str]:
        """Return JSON-compatible metadata; raw content remains bytes."""

        return {
            "path": self.path,
            "mode": self.mode,
            "object_format": self.object_format,
            "object_id": self.object_id,
        }


@dataclass(frozen=True)
class SelectorOutput:
    selector_type: str
    media_type: str
    encoding: str
    content: bytes
    source_line_endings: str
    transformation: Mapping[str, Any]

    def __post_init__(self) -> None:
        for field_name in (
            "selector_type",
            "media_type",
            "encoding",
            "source_line_endings",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or any(
                0xD800 <= ord(character) <= 0xDFFF for character in value
            ):
                raise ModelValueError(
                    f"{field_name} must contain only Unicode scalar values"
                )
        if not isinstance(self.content, bytes):
            raise ModelValueError("selector content must be bytes")
        if self.source_line_endings not in ("lf", "crlf", "none"):
            raise ModelValueError("source_line_endings is invalid")
        if not isinstance(self.transformation, Mapping):
            raise ModelValueError("selector transformation must be a mapping")
        object.__setattr__(
            self,
            "transformation",
            cast(Mapping[str, Any], deep_freeze(self.transformation)),
        )

    def as_dict(self) -> dict[str, Any]:
        """Return selector metadata without inspecting raw selected bytes."""

        return {
            "selector_type": self.selector_type,
            "media_type": self.media_type,
            "encoding": self.encoding,
            "source_line_endings": self.source_line_endings,
            "transformation": self.transformation,
        }

def _require_model_string(value: Any, field_name: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or any(0xD800 <= ord(character) <= 0xDFFF for character in value)
    ):
        raise ModelValueError(
            f"{field_name} must be a nonempty Unicode-scalar string"
        )
    return value


def _freeze_model_string_tuple(
    value: Any,
    field_name: str,
) -> Tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise ModelValueError(f"{field_name} must be a sequence")
    copied = tuple(value)
    for item in copied:
        _require_model_string(item, field_name)
    return copied


@dataclass(frozen=True)
class SelectedSourcePlan:
    rule_id: str
    rule_type: str
    priority_tier: int
    budget_tier: str
    source_kind: str
    sensitivity: str
    path: str
    structured_object_identity: str | None
    normalized_path_or_object_id: str
    selector: Mapping[str, Any]
    selection_reason: str
    trigger: str
    selection_chain: Tuple[str, ...]
    authority_class: str
    canonical_owner: str
    commit: str
    mode: str
    object_format: str
    blob: str

    def __post_init__(self) -> None:
        for field_name in (
            "rule_id",
            "rule_type",
            "budget_tier",
            "source_kind",
            "sensitivity",
            "path",
            "normalized_path_or_object_id",
            "selection_reason",
            "trigger",
            "authority_class",
            "canonical_owner",
            "commit",
            "mode",
            "object_format",
            "blob",
        ):
            _require_model_string(getattr(self, field_name), field_name)
        if self.structured_object_identity is not None:
            _require_model_string(
                self.structured_object_identity,
                "structured_object_identity",
            )
        if (
            not isinstance(self.priority_tier, int)
            or isinstance(self.priority_tier, bool)
            or not 0 <= self.priority_tier <= MAX_SAFE_INTEGER
        ):
            raise ModelValueError(
                "priority_tier must be a nonnegative safe integer"
            )
        if not isinstance(self.selector, Mapping):
            raise ModelValueError("selector must be a mapping")
        object.__setattr__(
            self,
            "selector",
            cast(Mapping[str, Any], deep_freeze(self.selector)),
        )
        object.__setattr__(
            self,
            "selection_chain",
            _freeze_model_string_tuple(
                self.selection_chain,
                "selection_chain",
            ),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_type": self.rule_type,
            "priority_tier": self.priority_tier,
            "budget_tier": self.budget_tier,
            "source_kind": self.source_kind,
            "sensitivity": self.sensitivity,
            "path": self.path,
            "structured_object_identity": self.structured_object_identity,
            "normalized_path_or_object_id": self.normalized_path_or_object_id,
            "selector": self.selector,
            "selection_reason": self.selection_reason,
            "trigger": self.trigger,
            "selection_chain": self.selection_chain,
            "authority_class": self.authority_class,
            "canonical_owner": self.canonical_owner,
            "commit": self.commit,
            "mode": self.mode,
            "object_format": self.object_format,
            "blob": self.blob,
        }


@dataclass(frozen=True)
class SelectionOmissionPlan:
    rule_id: str
    exclusion_rule_id: str
    boundary: str
    individual: Mapping[str, Any]
    trigger: str
    selection_chain: Tuple[str, ...]
    reason: str
    consequence: str
    blocking: bool
    reconsideration_condition: str

    def __post_init__(self) -> None:
        for field_name in (
            "rule_id",
            "exclusion_rule_id",
            "boundary",
            "trigger",
            "reason",
            "consequence",
            "reconsideration_condition",
        ):
            _require_model_string(getattr(self, field_name), field_name)
        if not isinstance(self.individual, Mapping):
            raise ModelValueError("individual must be a mapping")
        if not isinstance(self.blocking, bool):
            raise ModelValueError("blocking must be a boolean")
        object.__setattr__(
            self,
            "individual",
            cast(Mapping[str, Any], deep_freeze(self.individual)),
        )
        object.__setattr__(
            self,
            "selection_chain",
            _freeze_model_string_tuple(
                self.selection_chain,
                "selection_chain",
            ),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "exclusion_rule_id": self.exclusion_rule_id,
            "boundary": self.boundary,
            "individual": self.individual,
            "trigger": self.trigger,
            "selection_chain": self.selection_chain,
            "reason": self.reason,
            "consequence": self.consequence,
            "blocking": self.blocking,
            "reconsideration_condition": self.reconsideration_condition,
        }


@dataclass(frozen=True)
class SelectionUnknownPlan:
    rule_id: str
    boundary: str
    field: str
    attempted_resolution: str
    owner: str
    trigger: str
    selection_chain: Tuple[str, ...]
    consequence: str
    blocking: bool

    def __post_init__(self) -> None:
        for field_name in (
            "rule_id",
            "boundary",
            "field",
            "attempted_resolution",
            "owner",
            "trigger",
            "consequence",
        ):
            _require_model_string(getattr(self, field_name), field_name)
        if not isinstance(self.blocking, bool):
            raise ModelValueError("blocking must be a boolean")
        object.__setattr__(
            self,
            "selection_chain",
            _freeze_model_string_tuple(
                self.selection_chain,
                "selection_chain",
            ),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "boundary": self.boundary,
            "field": self.field,
            "attempted_resolution": self.attempted_resolution,
            "owner": self.owner,
            "trigger": self.trigger,
            "selection_chain": self.selection_chain,
            "consequence": self.consequence,
            "blocking": self.blocking,
        }


@dataclass(frozen=True)
class SelectionPlan:
    request_task_id: str
    selection_policy_id: str
    selection_policy_version: str
    selection_policy_digest: DigestRecord
    repository_identity: str
    requested_revision: str
    commit: str
    tree: str
    object_format: str
    snapshot_mode: str
    snapshot_fingerprint: DigestRecord
    selected: Tuple[SelectedSourcePlan, ...]
    omissions: Tuple[SelectionOmissionPlan, ...]
    unknowns: Tuple[SelectionUnknownPlan, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "request_task_id",
            "selection_policy_id",
            "selection_policy_version",
            "repository_identity",
            "requested_revision",
            "commit",
            "tree",
            "object_format",
            "snapshot_mode",
        ):
            _require_model_string(getattr(self, field_name), field_name)
        if not isinstance(self.selection_policy_digest, DigestRecord):
            raise ModelValueError(
                "selection_policy_digest must be a DigestRecord"
            )
        if not isinstance(self.snapshot_fingerprint, DigestRecord):
            raise ModelValueError(
                "snapshot_fingerprint must be a DigestRecord"
            )
        selected = tuple(self.selected)
        omissions = tuple(self.omissions)
        unknowns = tuple(self.unknowns)
        if not all(isinstance(item, SelectedSourcePlan) for item in selected):
            raise ModelValueError(
                "selected must contain SelectedSourcePlan values"
            )
        if not all(
            isinstance(item, SelectionOmissionPlan) for item in omissions
        ):
            raise ModelValueError(
                "omissions must contain SelectionOmissionPlan values"
            )
        if not all(
            isinstance(item, SelectionUnknownPlan) for item in unknowns
        ):
            raise ModelValueError(
                "unknowns must contain SelectionUnknownPlan values"
            )
        object.__setattr__(self, "selected", selected)
        object.__setattr__(self, "omissions", omissions)
        object.__setattr__(self, "unknowns", unknowns)

    @property
    def ready_for_compilation(self) -> bool:
        return not any(
            record.blocking for record in (*self.omissions, *self.unknowns)
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "request_task_id": self.request_task_id,
            "selection_policy_id": self.selection_policy_id,
            "selection_policy_version": self.selection_policy_version,
            "selection_policy_digest": self.selection_policy_digest.as_dict(),
            "repository_identity": self.repository_identity,
            "requested_revision": self.requested_revision,
            "commit": self.commit,
            "tree": self.tree,
            "object_format": self.object_format,
            "snapshot_mode": self.snapshot_mode,
            "snapshot_fingerprint": self.snapshot_fingerprint.as_dict(),
            "selected": [record.as_dict() for record in self.selected],
            "omissions": [record.as_dict() for record in self.omissions],
            "unknowns": [record.as_dict() for record in self.unknowns],
            "ready_for_compilation": self.ready_for_compilation,
        }
