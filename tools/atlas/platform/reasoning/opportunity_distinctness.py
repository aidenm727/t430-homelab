from collections import defaultdict
from collections.abc import Iterable, Mapping
from itertools import combinations
import re
import unicodedata

from atlas.platform.repository_objects.models import RepositoryEntity
from atlas.platform.reasoning.models import (
    OpportunityAssessmentRecommendation,
    OpportunityCapabilityAlignment,
    OpportunityDistinctnessComparison,
    OpportunityDistinctnessEvidence,
    OpportunityDistinctnessPortfolio,
    OpportunityDistinctnessSkippedPair,
    OpportunityRelationshipFinding,
    OpportunityScopeClassification,
)
from atlas.platform.reasoning.opportunity_capability_alignment import (
    align_opportunity_capability,
)
from atlas.platform.reasoning.opportunity_relationships import (
    build_opportunity_relationships,
)
from atlas.platform.reasoning.opportunity_scope_classification import (
    classify_opportunity_scope,
)


DISTINCTNESS_POLICY_VERSION = "distinctness-comparison-v1"
TEXT_NORMALIZATION_POLICY_VERSION = "distinctness-text-v1"

ALLOWED_RELATIONSHIP_TYPES = frozenset(
    {
        "duplicate_of",
        "overlaps_with",
        "component_of",
        "umbrella_for",
        "distinct_from",
    }
)

SYMMETRIC_RELATIONSHIP_TYPES = frozenset(
    {
        "duplicate_of",
        "overlaps_with",
        "distinct_from",
    }
)

STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "in",
        "into",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "with",
    }
)

TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")

MAJOR_TEXT_FIELDS = (
    "title",
    "summary",
    "rationale",
)

BROAD_OUTCOME_MARKERS = frozenset(
    {
        "architecture",
        "capability",
        "framework",
        "foundation",
        "intelligence",
        "platform",
        "system",
    }
)


def build_opportunity_pair_key(
    left_opportunity_id: str,
    right_opportunity_id: str,
) -> str:
    if left_opportunity_id == right_opportunity_id:
        raise ValueError(
            "Distinctness Analysis cannot compare an opportunity with itself."
        )

    left, right = sorted(
        (left_opportunity_id, right_opportunity_id)
    )
    return f"{left}::{right}"


def _canonical_pair(
    left: RepositoryEntity,
    right: RepositoryEntity,
) -> tuple[RepositoryEntity, RepositoryEntity]:
    if left.id == right.id:
        raise ValueError(
            "Distinctness Analysis cannot compare an opportunity with itself."
        )

    if left.id < right.id:
        return left, right

    return right, left


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(TOKEN_PATTERN.findall(normalized))


def _meaningful_tokens(value: str) -> frozenset[str]:
    return frozenset(
        token
        for token in _normalize_text(value).split()
        if token not in STOP_WORDS and len(token) > 1
    )


def _text_fields(
    entity: RepositoryEntity,
) -> dict[str, str]:
    fields = {
        "title": entity.title,
        "summary": entity.summary,
        "rationale": entity.rationale,
        "notes": entity.notes,
    }

    if entity.evidence:
        fields["evidence"] = "\n".join(entity.evidence)

    return fields


def _combined_tokens(
    entity: RepositoryEntity,
) -> frozenset[str]:
    return frozenset().union(
        *(
            _meaningful_tokens(value)
            for value in _text_fields(entity).values()
        )
    )


def _scope_identity(
    classification: OpportunityScopeClassification,
) -> str | None:
    return (
        classification.primary_scope_id
        or classification.leading_candidate_scope_id
    )


def _capability_ids(
    alignment: OpportunityCapabilityAlignment,
) -> frozenset[str]:
    identifiers = set(alignment.candidate_capability_ids)

    if alignment.primary_capability_id is not None:
        identifiers.add(alignment.primary_capability_id)

    return frozenset(identifiers)


def _pair_relationships(
    pair_key: str,
    relationships: Iterable[OpportunityRelationshipFinding],
) -> tuple[OpportunityRelationshipFinding, ...]:
    return tuple(
        relationship
        for relationship in relationships
        if build_opportunity_pair_key(
            relationship.source_opportunity_id,
            relationship.target_opportunity_id,
        )
        == pair_key
    )


def _fact_evidence(
    left: RepositoryEntity,
    right: RepositoryEntity,
    left_alignment: OpportunityCapabilityAlignment,
    right_alignment: OpportunityCapabilityAlignment,
    left_scope: OpportunityScopeClassification,
    right_scope: OpportunityScopeClassification,
    explicit_relationships: tuple[
        OpportunityRelationshipFinding,
        ...,
    ],
) -> tuple[OpportunityDistinctnessEvidence, ...]:
    return (
        OpportunityDistinctnessEvidence(
            evidence_type="repository-fact",
            source=left.path,
            statement=(
                f"Left object: {left.id}; lifecycle={left.status}; "
                f"declared capability={left.capability}."
            ),
        ),
        OpportunityDistinctnessEvidence(
            evidence_type="repository-fact",
            source=right.path,
            statement=(
                f"Right object: {right.id}; lifecycle={right.status}; "
                f"declared capability={right.capability}."
            ),
        ),
        OpportunityDistinctnessEvidence(
            evidence_type="capability-fact",
            source=(
                "atlas.platform.reasoning."
                "opportunity_capability_alignment"
            ),
            statement=(
                f"{left.id} capability state="
                f"{left_alignment.alignment_state}; "
                f"primary={left_alignment.primary_capability_id}; "
                f"candidates={left_alignment.candidate_capability_ids}."
            ),
        ),
        OpportunityDistinctnessEvidence(
            evidence_type="capability-fact",
            source=(
                "atlas.platform.reasoning."
                "opportunity_capability_alignment"
            ),
            statement=(
                f"{right.id} capability state="
                f"{right_alignment.alignment_state}; "
                f"primary={right_alignment.primary_capability_id}; "
                f"candidates={right_alignment.candidate_capability_ids}."
            ),
        ),
        OpportunityDistinctnessEvidence(
            evidence_type="scope-fact",
            source=(
                "atlas.platform.reasoning."
                "opportunity_scope_classification"
            ),
            statement=(
                f"{left.id} scope state="
                f"{left_scope.classification_state}; "
                f"primary={left_scope.primary_scope_id}; "
                f"leading={left_scope.leading_candidate_scope_id}."
            ),
        ),
        OpportunityDistinctnessEvidence(
            evidence_type="scope-fact",
            source=(
                "atlas.platform.reasoning."
                "opportunity_scope_classification"
            ),
            statement=(
                f"{right.id} scope state="
                f"{right_scope.classification_state}; "
                f"primary={right_scope.primary_scope_id}; "
                f"leading={right_scope.leading_candidate_scope_id}."
            ),
        ),
        OpportunityDistinctnessEvidence(
            evidence_type="repository-fact",
            source=f"{left.path}#references",
            statement=(
                f"{left.id} references: "
                f"{len(left.dependencies)} dependencies, "
                f"{len(left.related_opportunities)} related opportunities, "
                f"{len(left.related_documents)} related documents, "
                f"{len(left.evidence)} evidence items."
            ),
        ),
        OpportunityDistinctnessEvidence(
            evidence_type="repository-fact",
            source=f"{right.path}#references",
            statement=(
                f"{right.id} references: "
                f"{len(right.dependencies)} dependencies, "
                f"{len(right.related_opportunities)} related opportunities, "
                f"{len(right.related_documents)} related documents, "
                f"{len(right.evidence)} evidence items."
            ),
        ),
        OpportunityDistinctnessEvidence(
            evidence_type="relationship-fact",
            source=(
                "atlas.platform.reasoning."
                "opportunity_relationships"
            ),
            statement=(
                "Explicit pair relationship findings: "
                f"{len(explicit_relationships)}."
            ),
        ),
    )


def _text_comparison_evidence(
    left: RepositoryEntity,
    right: RepositoryEntity,
) -> tuple[
    tuple[OpportunityDistinctnessEvidence, ...],
    tuple[OpportunityDistinctnessEvidence, ...],
    int,
    int,
    int,
]:
    supporting: list[OpportunityDistinctnessEvidence] = []
    boundary: list[OpportunityDistinctnessEvidence] = []
    left_fields = _text_fields(left)
    right_fields = _text_fields(right)
    exact_major_fields = 0
    high_overlap_major_fields = 0

    for field_name in sorted(
        set(left_fields) & set(right_fields)
    ):
        left_value = left_fields[field_name]
        right_value = right_fields[field_name]
        left_tokens = _meaningful_tokens(left_value)
        right_tokens = _meaningful_tokens(right_value)

        if not left_tokens or not right_tokens:
            continue

        shared_tokens = left_tokens & right_tokens
        union_tokens = left_tokens | right_tokens
        overlap_ratio = (
            len(shared_tokens) / len(union_tokens)
            if union_tokens
            else 0.0
        )
        exact = (
            _normalize_text(left_value)
            == _normalize_text(right_value)
            and len(left_tokens) >= 3
        )

        if exact:
            supporting.append(
                OpportunityDistinctnessEvidence(
                    evidence_type="text-exact",
                    source=(
                        f"{left.path}#{field_name};"
                        f"{right.path}#{field_name}"
                    ),
                    statement=(
                        f"Normalized {field_name} text matches exactly "
                        f"under {TEXT_NORMALIZATION_POLICY_VERSION}; "
                        f"meaningful token count={len(left_tokens)}."
                    ),
                    field_name=field_name,
                )
            )
            if field_name in MAJOR_TEXT_FIELDS:
                exact_major_fields += 1
                high_overlap_major_fields += 1
            continue

        if len(shared_tokens) >= 4 and overlap_ratio >= 0.50:
            supporting.append(
                OpportunityDistinctnessEvidence(
                    evidence_type="text-token-overlap",
                    source=(
                        f"{left.path}#{field_name};"
                        f"{right.path}#{field_name}"
                    ),
                    statement=(
                        f"Normalized {field_name} fields share "
                        f"{len(shared_tokens)} of {len(union_tokens)} "
                        "meaningful tokens "
                        f"(ratio={overlap_ratio:.2f}) under "
                        f"{TEXT_NORMALIZATION_POLICY_VERSION}; "
                        "this is a transparent heuristic signal, "
                        "not semantic proof."
                    ),
                    field_name=field_name,
                )
            )
            if field_name in MAJOR_TEXT_FIELDS:
                high_overlap_major_fields += 1
        elif field_name in MAJOR_TEXT_FIELDS:
            left_only = sorted(left_tokens - right_tokens)
            right_only = sorted(right_tokens - left_tokens)

            if left_only and right_only:
                boundary.append(
                    OpportunityDistinctnessEvidence(
                        evidence_type="text-boundary",
                        source=(
                            f"{left.path}#{field_name};"
                            f"{right.path}#{field_name}"
                        ),
                        statement=(
                            f"Normalized {field_name} fields retain "
                            "different meaningful terms. "
                            f"{left.id}-only={left_only[:8]}; "
                            f"{right.id}-only={right_only[:8]}."
                        ),
                        field_name=field_name,
                    )
                )

    shared_combined_tokens = (
        _combined_tokens(left) & _combined_tokens(right)
    )

    return (
        tuple(supporting),
        tuple(boundary),
        exact_major_fields,
        high_overlap_major_fields,
        len(shared_combined_tokens),
    )


def _structural_evidence(
    left: RepositoryEntity,
    right: RepositoryEntity,
    left_alignment: OpportunityCapabilityAlignment,
    right_alignment: OpportunityCapabilityAlignment,
    left_scope: OpportunityScopeClassification,
    right_scope: OpportunityScopeClassification,
    explicit_relationships: tuple[
        OpportunityRelationshipFinding,
        ...,
    ],
) -> tuple[
    tuple[OpportunityDistinctnessEvidence, ...],
    tuple[OpportunityDistinctnessEvidence, ...],
    tuple[OpportunityDistinctnessEvidence, ...],
    tuple[str, str] | None,
    bool,
]:
    supporting: list[OpportunityDistinctnessEvidence] = []
    counter: list[OpportunityDistinctnessEvidence] = []
    boundary: list[OpportunityDistinctnessEvidence] = []
    dependency_direction: tuple[str, str] | None = None
    explicitly_related = False

    for relationship in explicit_relationships:
        if relationship.relationship_type == "related_to":
            explicitly_related = True
            supporting.append(
                OpportunityDistinctnessEvidence(
                    evidence_type="explicit-relationship",
                    source=(
                        "atlas.platform.reasoning."
                        "opportunity_relationships"
                    ),
                    statement=(
                        f"Explicit related_to evidence connects "
                        f"{relationship.source_opportunity_id} and "
                        f"{relationship.target_opportunity_id}; "
                        "it triggers comparison but does not establish "
                        "a stronger distinctness relationship."
                    ),
                    relationship_type="related_to",
                )
            )
        elif relationship.relationship_type == "depends_on":
            dependency_direction = (
                relationship.source_opportunity_id,
                relationship.target_opportunity_id,
            )
            boundary.append(
                OpportunityDistinctnessEvidence(
                    evidence_type="explicit-dependency-boundary",
                    source=(
                        "atlas.platform.reasoning."
                        "opportunity_relationships"
                    ),
                    statement=(
                        f"{relationship.source_opportunity_id} explicitly "
                        f"depends on {relationship.target_opportunity_id}; "
                        "the objects play different dependency roles."
                    ),
                    relationship_type="depends_on",
                )
            )

    left_capabilities = _capability_ids(left_alignment)
    right_capabilities = _capability_ids(right_alignment)
    shared_capabilities = sorted(
        left_capabilities & right_capabilities
    )

    if shared_capabilities:
        supporting.append(
            OpportunityDistinctnessEvidence(
                evidence_type="capability-context",
                source=(
                    "atlas.platform.reasoning."
                    "opportunity_capability_alignment"
                ),
                statement=(
                    "Capability Alignment shares canonical context: "
                    + ", ".join(shared_capabilities)
                    + ". Shared capability alone cannot establish "
                    "duplication."
                ),
            )
        )
    elif left_capabilities and right_capabilities:
        counter.append(
            OpportunityDistinctnessEvidence(
                evidence_type="capability-counterevidence",
                source=(
                    "atlas.platform.reasoning."
                    "opportunity_capability_alignment"
                ),
                statement=(
                    f"Resolved or candidate capability identities differ: "
                    f"{left.id}={sorted(left_capabilities)}; "
                    f"{right.id}={sorted(right_capabilities)}. "
                    "This weakens duplication but does not automatically "
                    "establish distinctness."
                ),
            )
        )

    left_scope_id = _scope_identity(left_scope)
    right_scope_id = _scope_identity(right_scope)

    if left_scope_id is not None and left_scope_id == right_scope_id:
        supporting.append(
            OpportunityDistinctnessEvidence(
                evidence_type="scope-context",
                source=(
                    "atlas.platform.reasoning."
                    "opportunity_scope_classification"
                ),
                statement=(
                    f"Scope Classification shares '{left_scope_id}'. "
                    "Shared scope alone cannot establish duplication."
                ),
            )
        )
    elif left_scope_id is not None and right_scope_id is not None:
        boundary.append(
            OpportunityDistinctnessEvidence(
                evidence_type="scope-boundary",
                source=(
                    "atlas.platform.reasoning."
                    "opportunity_scope_classification"
                ),
                statement=(
                    f"Scope interpretations differ: "
                    f"{left.id}={left_scope_id}; "
                    f"{right.id}={right_scope_id}. "
                    "This supports a boundary while still permitting "
                    "component or umbrella interpretation."
                ),
            )
        )

    shared_documents = sorted(
        set(left.related_documents)
        & set(right.related_documents)
    )
    unique_left_documents = sorted(
        set(left.related_documents)
        - set(right.related_documents)
    )
    unique_right_documents = sorted(
        set(right.related_documents)
        - set(left.related_documents)
    )

    if shared_documents:
        supporting.append(
            OpportunityDistinctnessEvidence(
                evidence_type="shared-document",
                source=(
                    f"{left.path}#related-documents;"
                    f"{right.path}#related-documents"
                ),
                statement=(
                    "Shared related documents: "
                    + ", ".join(shared_documents)
                    + ". Shared documents support comparison but do not "
                    "establish duplication."
                ),
            )
        )

    if unique_left_documents and unique_right_documents:
        boundary.append(
            OpportunityDistinctnessEvidence(
                evidence_type="document-boundary",
                source=(
                    f"{left.path}#related-documents;"
                    f"{right.path}#related-documents"
                ),
                statement=(
                    "Each opportunity has unique related-document context. "
                    f"{left.id}-only={unique_left_documents}; "
                    f"{right.id}-only={unique_right_documents}."
                ),
            )
        )

    shared_evidence = sorted(
        set(left.evidence) & set(right.evidence)
    )

    if shared_evidence:
        supporting.append(
            OpportunityDistinctnessEvidence(
                evidence_type="shared-evidence",
                source=(
                    f"{left.path}#evidence;"
                    f"{right.path}#evidence"
                ),
                statement=(
                    f"The objects share {len(shared_evidence)} exact "
                    "evidence item(s). Shared evidence is comparison "
                    "context, not duplication proof."
                ),
            )
        )

    return (
        tuple(supporting),
        tuple(counter),
        tuple(boundary),
        dependency_direction,
        explicitly_related,
    )


def _validate_human_relationships(
    relationship_types: tuple[str, ...],
) -> tuple[str, ...]:
    unique_types = tuple(dict.fromkeys(relationship_types))
    unknown = sorted(
        set(unique_types) - ALLOWED_RELATIONSHIP_TYPES
    )

    if unknown:
        raise ValueError(
            "human_reviewed_relationship_types contains unsupported "
            f"relationship types: {unknown}."
        )

    return unique_types


def _validate_pair_member(
    value: str | None,
    pair_ids: frozenset[str],
    field_name: str,
) -> str | None:
    if value is not None and value not in pair_ids:
        raise ValueError(
            f"{field_name} must identify one member of the pair."
        )

    return value


def _resolved_human_comparison(
    left: RepositoryEntity,
    right: RepositoryEntity,
    facts: tuple[OpportunityDistinctnessEvidence, ...],
    supporting: tuple[OpportunityDistinctnessEvidence, ...],
    counter: tuple[OpportunityDistinctnessEvidence, ...],
    boundary: tuple[OpportunityDistinctnessEvidence, ...],
    relationship_type: str,
    human_source_id: str | None,
    human_target_id: str | None,
    canonical_target_id: str | None,
) -> OpportunityDistinctnessComparison:
    pair_key = build_opportunity_pair_key(left.id, right.id)
    pair_ids = frozenset((left.id, right.id))

    human_source_id = _validate_pair_member(
        human_source_id,
        pair_ids,
        "human_reviewed_source_opportunity_id",
    )
    human_target_id = _validate_pair_member(
        human_target_id,
        pair_ids,
        "human_reviewed_target_opportunity_id",
    )
    canonical_target_id = _validate_pair_member(
        canonical_target_id,
        pair_ids,
        "canonical_target_candidate_id",
    )

    inverse_relationship_type: str | None = None
    source_id: str | None = None
    target_id: str | None = None

    if relationship_type in {"component_of", "umbrella_for"}:
        if (
            human_source_id is None
            or human_target_id is None
            or human_source_id == human_target_id
        ):
            raise ValueError(
                "Directional human-reviewed relationships require "
                "different source and target opportunity IDs."
            )

        source_id = human_source_id
        target_id = human_target_id
        inverse_relationship_type = (
            "umbrella_for"
            if relationship_type == "component_of"
            else "component_of"
        )

    if (
        canonical_target_id is not None
        and relationship_type != "duplicate_of"
    ):
        raise ValueError(
            "A canonical target candidate is only valid for duplicate_of."
        )

    human_evidence = OpportunityDistinctnessEvidence(
        evidence_type="human-reviewed",
        source="human-review-input",
        statement=(
            f"Human-reviewed relationship decision: "
            f"{relationship_type}."
        ),
        relationship_type=relationship_type,
    )

    action = {
        "duplicate_of": "review-duplicate-closure",
        "overlaps_with": "retain-and-coordinate",
        "component_of": "record-component-relationship",
        "umbrella_for": "record-umbrella-relationship",
        "distinct_from": "retain-separate",
    }[relationship_type]

    explanation = (
        f"Human-reviewed evidence resolves pair {pair_key} as "
        f"'{relationship_type}'."
    )

    if canonical_target_id is not None:
        explanation += (
            f" The human-reviewed canonical target candidate is "
            f"{canonical_target_id}; repository mutation remains separate."
        )

    return OpportunityDistinctnessComparison(
        pair_key=pair_key,
        left_opportunity_id=left.id,
        left_repository_path=left.path,
        right_opportunity_id=right.id,
        right_repository_path=right.path,
        analysis_state="resolved",
        relationship_type=relationship_type,
        inverse_relationship_type=inverse_relationship_type,
        source_opportunity_id=source_id,
        target_opportunity_id=target_id,
        canonical_target_candidate_id=canonical_target_id,
        alternative_relationship_types=(),
        facts=facts,
        supporting_evidence=supporting + (human_evidence,),
        counterevidence=counter,
        boundary_evidence=boundary,
        provenance=(
            left.path,
            right.path,
            "human-review-input",
            DISTINCTNESS_POLICY_VERSION,
        ),
        explanation=explanation,
        confidence="High",
        blockers=(),
        unresolved_questions=(),
        recommendation=OpportunityAssessmentRecommendation(
            action=action,
            reason=(
                "Apply the human-reviewed distinctness decision through a "
                "separate repository workflow that preserves both stable "
                "identifiers and history."
            ),
            confidence="High",
        ),
    )


def compare_opportunity_distinctness(
    left: RepositoryEntity,
    right: RepositoryEntity,
    *,
    left_capability_alignment: OpportunityCapabilityAlignment | None = None,
    right_capability_alignment: OpportunityCapabilityAlignment | None = None,
    left_scope_classification: OpportunityScopeClassification | None = None,
    right_scope_classification: OpportunityScopeClassification | None = None,
    explicit_relationships: tuple[
        OpportunityRelationshipFinding,
        ...,
    ] | None = None,
    human_reviewed_relationship_types: tuple[str, ...] = (),
    human_reviewed_source_opportunity_id: str | None = None,
    human_reviewed_target_opportunity_id: str | None = None,
    canonical_target_candidate_id: str | None = None,
) -> OpportunityDistinctnessComparison:
    left, right = _canonical_pair(left, right)
    pair_key = build_opportunity_pair_key(left.id, right.id)
    relationship_types = _validate_human_relationships(
        human_reviewed_relationship_types
    )
    relationships = (
        explicit_relationships
        if explicit_relationships is not None
        else build_opportunity_relationships((left, right))
    )
    relationships = _pair_relationships(pair_key, relationships)
    left_alignment = (
        left_capability_alignment
        if left_capability_alignment is not None
        else align_opportunity_capability(left)
    )
    right_alignment = (
        right_capability_alignment
        if right_capability_alignment is not None
        else align_opportunity_capability(right)
    )
    left_scope = (
        left_scope_classification
        if left_scope_classification is not None
        else classify_opportunity_scope(
            left,
            capability_alignment=left_alignment,
        )
    )
    right_scope = (
        right_scope_classification
        if right_scope_classification is not None
        else classify_opportunity_scope(
            right,
            capability_alignment=right_alignment,
        )
    )
    facts = _fact_evidence(
        left,
        right,
        left_alignment,
        right_alignment,
        left_scope,
        right_scope,
        relationships,
    )
    (
        structural_supporting,
        counterevidence,
        structural_boundary,
        dependency_direction,
        explicitly_related,
    ) = _structural_evidence(
        left,
        right,
        left_alignment,
        right_alignment,
        left_scope,
        right_scope,
        relationships,
    )
    (
        text_supporting,
        text_boundary,
        exact_major_fields,
        high_overlap_major_fields,
        shared_combined_token_count,
    ) = _text_comparison_evidence(left, right)
    supporting = structural_supporting + text_supporting
    boundary = structural_boundary + text_boundary
    provenance = (
        left.path,
        right.path,
        "atlas.platform.reasoning.opportunity_relationships",
        "atlas.platform.reasoning.opportunity_capability_alignment",
        "atlas.platform.reasoning.opportunity_scope_classification",
        TEXT_NORMALIZATION_POLICY_VERSION,
        DISTINCTNESS_POLICY_VERSION,
    )

    if len(relationship_types) > 1:
        blocker = (
            "Conflicting human-reviewed distinctness evidence identifies "
            "more than one relationship for the same pair."
        )
        return OpportunityDistinctnessComparison(
            pair_key=pair_key,
            left_opportunity_id=left.id,
            left_repository_path=left.path,
            right_opportunity_id=right.id,
            right_repository_path=right.path,
            analysis_state="conflicting",
            relationship_type=None,
            inverse_relationship_type=None,
            source_opportunity_id=None,
            target_opportunity_id=None,
            canonical_target_candidate_id=None,
            alternative_relationship_types=relationship_types,
            facts=facts,
            supporting_evidence=supporting
            + tuple(
                OpportunityDistinctnessEvidence(
                    evidence_type="human-reviewed",
                    source="human-review-input",
                    statement=(
                        f"Human-reviewed relationship evidence: "
                        f"{relationship_type}."
                    ),
                    relationship_type=relationship_type,
                )
                for relationship_type in relationship_types
            ),
            counterevidence=counterevidence,
            boundary_evidence=boundary,
            provenance=provenance + ("human-review-input",),
            explanation=blocker,
            confidence="High",
            blockers=(blocker,),
            unresolved_questions=(
                "Which human-reviewed relationship decision should remain "
                "authoritative for this pair?",
            ),
            recommendation=OpportunityAssessmentRecommendation(
                action="resolve-distinctness-conflict",
                reason=(
                    "Resolve the conflicting human-reviewed relationship "
                    "decisions before repository mutation."
                ),
                confidence="High",
            ),
        )

    if len(relationship_types) == 1:
        return _resolved_human_comparison(
            left,
            right,
            facts,
            supporting,
            counterevidence,
            boundary,
            relationship_types[0],
            human_reviewed_source_opportunity_id,
            human_reviewed_target_opportunity_id,
            canonical_target_candidate_id,
        )

    duplicate_supported = (
        exact_major_fields >= 2
        and dependency_direction is None
    )
    duplicate_tentative = (
        exact_major_fields >= 1
        and high_overlap_major_fields >= 2
        and not duplicate_supported
    )
    overlap_supported = (
        high_overlap_major_fields >= 2
        and not duplicate_supported
    ) or (
        high_overlap_major_fields >= 1
        and any(
            evidence.evidence_type
            in {"shared-document", "shared-evidence"}
            for evidence in structural_supporting
        )
    )

    component_direction: tuple[str, str] | None = None

    if (
        dependency_direction is not None
        and shared_combined_token_count >= 4
    ):
        dependent_id, prerequisite_id = dependency_direction
        by_id = {
            left.id: left,
            right.id: right,
        }
        dependent = by_id[dependent_id]
        prerequisite = by_id[prerequisite_id]
        dependent_tokens = _combined_tokens(dependent)
        prerequisite_tokens = _combined_tokens(prerequisite)

        if (
            prerequisite_tokens & BROAD_OUTCOME_MARKERS
            and len(prerequisite_tokens) >= len(dependent_tokens)
        ):
            component_direction = (
                dependent_id,
                prerequisite_id,
            )

    distinct_supported = (
        dependency_direction is not None
        and component_direction is None
        and high_overlap_major_fields == 0
        and exact_major_fields == 0
    )

    candidates: list[str] = []

    if duplicate_supported or duplicate_tentative:
        candidates.append("duplicate_of")
    if overlap_supported:
        candidates.append("overlaps_with")
    if component_direction is not None:
        candidates.append("component_of")
    if distinct_supported:
        candidates.append("distinct_from")

    candidates = list(dict.fromkeys(candidates))

    if len(candidates) > 1:
        return OpportunityDistinctnessComparison(
            pair_key=pair_key,
            left_opportunity_id=left.id,
            left_repository_path=left.path,
            right_opportunity_id=right.id,
            right_repository_path=right.path,
            analysis_state="ambiguous",
            relationship_type=None,
            inverse_relationship_type=None,
            source_opportunity_id=None,
            target_opportunity_id=None,
            canonical_target_candidate_id=None,
            alternative_relationship_types=tuple(candidates),
            facts=facts,
            supporting_evidence=supporting,
            counterevidence=counterevidence,
            boundary_evidence=boundary,
            provenance=provenance,
            explanation=(
                "Transparent comparison evidence supports multiple "
                "plausible distinctness relationships: "
                + ", ".join(candidates)
                + ". No relationship is resolved."
            ),
            confidence="Low",
            blockers=(),
            unresolved_questions=(
                "Which relationship best describes the central boundary "
                "between these opportunities?",
            ),
            recommendation=OpportunityAssessmentRecommendation(
                action="review-distinctness-boundary",
                reason=(
                    "Review the competing relationship interpretations "
                    "before recording canonical relationship or lifecycle "
                    "changes."
                ),
                confidence="Low",
            ),
        )

    if len(candidates) == 1:
        relationship_type = candidates[0]
        inverse_relationship_type: str | None = None
        source_id: str | None = None
        target_id: str | None = None

        if relationship_type == "component_of":
            source_id, target_id = component_direction
            inverse_relationship_type = "umbrella_for"

        action = {
            "duplicate_of": "review-duplicate-candidate",
            "overlaps_with": "review-overlap-candidate",
            "component_of": "review-component-umbrella-candidate",
            "distinct_from": "retain-separate-candidate",
        }[relationship_type]

        confidence = (
            "Medium"
            if relationship_type
            in {"duplicate_of", "overlaps_with", "component_of"}
            else "High"
        )
        canonical_target = (
            _validate_pair_member(
                canonical_target_candidate_id,
                frozenset((left.id, right.id)),
                "canonical_target_candidate_id",
            )
            if relationship_type == "duplicate_of"
            else None
        )

        if (
            canonical_target_candidate_id is not None
            and relationship_type != "duplicate_of"
        ):
            raise ValueError(
                "A canonical target candidate is only valid for duplicate_of."
            )

        explanation = (
            f"Transparent repository and text evidence supports "
            f"'{relationship_type}' as a review candidate. "
            "The result remains derived reasoning and does not authorize "
            "repository mutation."
        )

        if canonical_target is not None:
            explanation += (
                f" Canonical target candidate {canonical_target} was "
                "provided explicitly and remains a recommendation."
            )

        return OpportunityDistinctnessComparison(
            pair_key=pair_key,
            left_opportunity_id=left.id,
            left_repository_path=left.path,
            right_opportunity_id=right.id,
            right_repository_path=right.path,
            analysis_state="candidate",
            relationship_type=relationship_type,
            inverse_relationship_type=inverse_relationship_type,
            source_opportunity_id=source_id,
            target_opportunity_id=target_id,
            canonical_target_candidate_id=canonical_target,
            alternative_relationship_types=(),
            facts=facts,
            supporting_evidence=supporting,
            counterevidence=counterevidence,
            boundary_evidence=boundary,
            provenance=provenance,
            explanation=explanation,
            confidence=confidence,
            blockers=(),
            unresolved_questions=(
                "Should human review confirm, revise, or reject this "
                "relationship candidate?",
            ),
            recommendation=OpportunityAssessmentRecommendation(
                action=action,
                reason=(
                    "Review the explainable candidate while preserving both "
                    "opportunity objects, lifecycle states, references, and "
                    "stable identifiers."
                ),
                confidence=confidence,
            ),
        )

    return OpportunityDistinctnessComparison(
        pair_key=pair_key,
        left_opportunity_id=left.id,
        left_repository_path=left.path,
        right_opportunity_id=right.id,
        right_repository_path=right.path,
        analysis_state="insufficient-evidence",
        relationship_type=None,
        inverse_relationship_type=None,
        source_opportunity_id=None,
        target_opportunity_id=None,
        canonical_target_candidate_id=None,
        alternative_relationship_types=(),
        facts=facts,
        supporting_evidence=supporting,
        counterevidence=counterevidence,
        boundary_evidence=boundary,
        provenance=provenance,
        explanation=(
            "Current repository evidence does not support a responsible "
            "duplicate, overlap, component, umbrella, or distinct candidate."
        ),
        confidence="Low",
        blockers=(),
        unresolved_questions=(
            "What central outcome, completion boundary, or explicit "
            "relationship evidence would clarify this pair?",
        ),
        recommendation=OpportunityAssessmentRecommendation(
            action=(
                "review-related-opportunities"
                if explicitly_related
                else "enrich-distinctness-evidence"
            ),
            reason=(
                "Preserve both opportunities and improve boundary evidence "
                "before relying on a distinctness conclusion."
            ),
            confidence="Low",
        ),
    )


def _comparison_gate(
    left: RepositoryEntity,
    right: RepositoryEntity,
    left_alignment: OpportunityCapabilityAlignment,
    right_alignment: OpportunityCapabilityAlignment,
    left_scope: OpportunityScopeClassification,
    right_scope: OpportunityScopeClassification,
    explicit_relationships: tuple[
        OpportunityRelationshipFinding,
        ...,
    ],
) -> tuple[bool, str]:
    if explicit_relationships:
        return (
            True,
            "Explicit opportunity relationship evidence exists.",
        )

    if set(left.related_documents) & set(right.related_documents):
        return (
            True,
            "The opportunities share at least one related document.",
        )

    if _capability_ids(left_alignment) & _capability_ids(right_alignment):
        return (
            True,
            "Capability Alignment provides shared comparison context.",
        )

    left_scope_id = _scope_identity(left_scope)
    right_scope_id = _scope_identity(right_scope)

    if (
        left_scope_id is not None
        and left_scope_id == right_scope_id
    ):
        return (
            True,
            "Scope Classification provides shared comparison context.",
        )

    shared_tokens = _combined_tokens(left) & _combined_tokens(right)

    if len(shared_tokens) >= 2:
        return (
            True,
            "The objects share at least two normalized meaningful tokens.",
        )

    return (
        False,
        "No explicit relationship, shared document, shared capability, "
        "shared scope, or two-token text signal justified pair analysis.",
    )


def build_opportunity_distinctness_portfolio(
    entities: Iterable[RepositoryEntity],
    *,
    capability_alignments: Mapping[
        str,
        OpportunityCapabilityAlignment,
    ] | None = None,
    scope_classifications: Mapping[
        str,
        OpportunityScopeClassification,
    ] | None = None,
    relationships: tuple[
        OpportunityRelationshipFinding,
        ...,
    ] | None = None,
) -> OpportunityDistinctnessPortfolio:
    opportunity_entities = tuple(
        sorted(
            entities,
            key=lambda entity: entity.id,
        )
    )
    opportunity_ids = tuple(
        entity.id
        for entity in opportunity_entities
    )

    if len(opportunity_ids) != len(set(opportunity_ids)):
        raise ValueError(
            "Distinctness portfolio analysis requires unique opportunity IDs."
        )

    alignment_by_id = (
        dict(capability_alignments)
        if capability_alignments is not None
        else {
            entity.id: align_opportunity_capability(entity)
            for entity in opportunity_entities
        }
    )
    scope_by_id = (
        dict(scope_classifications)
        if scope_classifications is not None
        else {
            entity.id: classify_opportunity_scope(
                entity,
                capability_alignment=alignment_by_id[entity.id],
            )
            for entity in opportunity_entities
        }
    )
    relationship_findings = (
        relationships
        if relationships is not None
        else build_opportunity_relationships(opportunity_entities)
    )
    relationships_by_pair: dict[
        str,
        list[OpportunityRelationshipFinding],
    ] = defaultdict(list)

    for relationship in relationship_findings:
        relationships_by_pair[
            build_opportunity_pair_key(
                relationship.source_opportunity_id,
                relationship.target_opportunity_id,
            )
        ].append(relationship)

    comparisons_found: list[
        OpportunityDistinctnessComparison
    ] = []
    skipped_pairs: list[
        OpportunityDistinctnessSkippedPair
    ] = []

    for left, right in combinations(opportunity_entities, 2):
        pair_key = build_opportunity_pair_key(left.id, right.id)
        pair_relationships = tuple(
            relationships_by_pair.get(pair_key, ())
        )
        should_compare, reason = _comparison_gate(
            left,
            right,
            alignment_by_id[left.id],
            alignment_by_id[right.id],
            scope_by_id[left.id],
            scope_by_id[right.id],
            pair_relationships,
        )

        if not should_compare:
            skipped_pairs.append(
                OpportunityDistinctnessSkippedPair(
                    pair_key=pair_key,
                    left_opportunity_id=left.id,
                    right_opportunity_id=right.id,
                    reason=reason,
                )
            )
            continue

        comparisons_found.append(
            compare_opportunity_distinctness(
                left,
                right,
                left_capability_alignment=alignment_by_id[left.id],
                right_capability_alignment=alignment_by_id[right.id],
                left_scope_classification=scope_by_id[left.id],
                right_scope_classification=scope_by_id[right.id],
                explicit_relationships=pair_relationships,
            )
        )

    pair_keys_by_opportunity: dict[str, list[str]] = {
        opportunity_id: []
        for opportunity_id in opportunity_ids
    }

    for comparison in comparisons_found:
        pair_keys_by_opportunity[
            comparison.left_opportunity_id
        ].append(comparison.pair_key)
        pair_keys_by_opportunity[
            comparison.right_opportunity_id
        ].append(comparison.pair_key)

    return OpportunityDistinctnessPortfolio(
        opportunity_ids=opportunity_ids,
        comparison_count=len(comparisons_found),
        skipped_pair_count=len(skipped_pairs),
        comparisons=tuple(comparisons_found),
        skipped_pairs=tuple(skipped_pairs),
        findings_by_opportunity=tuple(
            (
                opportunity_id,
                tuple(pair_keys_by_opportunity[opportunity_id]),
            )
            for opportunity_id in opportunity_ids
        ),
        provenance=(
            "atlas.platform.reasoning.opportunity_relationships",
            "atlas.platform.reasoning.opportunity_capability_alignment",
            "atlas.platform.reasoning.opportunity_scope_classification",
            TEXT_NORMALIZATION_POLICY_VERSION,
            DISTINCTNESS_POLICY_VERSION,
        ),
    )
