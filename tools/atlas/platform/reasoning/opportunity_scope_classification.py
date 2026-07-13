from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import re

from atlas.platform.repository import repo_root
from atlas.platform.repository_objects.models import RepositoryEntity
from atlas.platform.reasoning.models import (
    OpportunityAssessmentRecommendation,
    OpportunityCapabilityAlignment,
    OpportunityScopeClassification,
    OpportunityScopeEvidence,
)
from atlas.platform.reasoning.opportunity_capability_alignment import (
    align_opportunity_capability,
)


SCOPE_ARCHITECTURE_PATH = (
    "docs/architecture/engineering-opportunity-scope-classification.md"
)
SCOPE_TABLE_ROW = re.compile(
    r"^\| `(?P<identifier>[a-z0-9-]+)` \| "
    r"(?P<label>[^|]+?) \|$",
    re.MULTILINE,
)

EXPECTED_SCOPE_IDS = (
    "strategic-direction",
    "capability-opportunity",
    "architecture-opportunity",
    "engineering-system-opportunity",
    "implementation-opportunity",
    "operational-infrastructure-opportunity",
)

SCOPE_SIGNAL_PHRASES = {
    "strategic-direction": (
        "long-term",
        "strategic direction",
        "future direction",
        "several capabilities",
        "multiple capabilities",
        "roadmap",
        "sovereignty",
    ),
    "capability-opportunity": (
        "durable capability",
        "platform capability",
        "capability expansion",
        "reusable capability",
        "be able to",
        "ability to",
    ),
    "architecture-opportunity": (
        "architecture",
        "design contract",
        "system boundaries",
        "repository ownership",
        "canonical design",
        "architect before",
    ),
    "engineering-system-opportunity": (
        "atlas",
        "repository reasoning",
        "repository knowledge",
        "engineering workflow",
        "engineering session",
        "engineering collaboration",
        "validation",
        "synchronization",
        "artifact transport",
        "engineering skills",
    ),
    "implementation-opportunity": (
        "implementation",
        "refactor",
        "migration",
        "tooling",
        "script",
        "replacement",
        "bounded change",
    ),
    "operational-infrastructure-opportunity": (
        "infrastructure",
        "deployed system",
        "operational",
        "reliability",
        "security",
        "storage",
        "networking",
        "backup",
        "service",
    ),
}

MIXED_SCOPE_MARKERS = (
    "combines",
    "includes both",
    "bundles",
    "simultaneously",
)


@dataclass(frozen=True)
class ScopeDefinition:
    identifier: str
    label: str
    source: str = SCOPE_ARCHITECTURE_PATH


def build_scope_catalog() -> tuple[ScopeDefinition, ...]:
    architecture_path = repo_root() / SCOPE_ARCHITECTURE_PATH
    content = architecture_path.read_text(encoding="utf-8")
    definitions = tuple(
        ScopeDefinition(
            identifier=match.group("identifier"),
            label=match.group("label").strip(),
        )
        for match in SCOPE_TABLE_ROW.finditer(content)
    )

    identifiers = tuple(
        definition.identifier
        for definition in definitions
    )
    labels = tuple(
        definition.label
        for definition in definitions
    )

    if identifiers != EXPECTED_SCOPE_IDS:
        raise ValueError(
            "The canonical scope taxonomy does not match the "
            f"architecture contract. Observed={identifiers}."
        )

    if len(labels) != len(set(labels)):
        raise ValueError(
            "The canonical scope taxonomy contains duplicate display labels."
        )

    return definitions


def _text_fields(
    entity: RepositoryEntity,
) -> tuple[tuple[str, str], ...]:
    fields: list[tuple[str, str]] = [
        ("title", entity.title),
        ("summary", entity.summary),
        ("rationale", entity.rationale),
        ("notes", entity.notes),
    ]
    fields.extend(
        (f"evidence[{index}]", value)
        for index, value in enumerate(entity.evidence)
    )
    return tuple(fields)


def _contains_phrase(text: str, phrase: str) -> bool:
    pattern = re.compile(
        rf"(?<!\w){re.escape(phrase.lower())}(?!\w)"
    )
    return bool(pattern.search(text.lower()))


def _repository_facts(
    entity: RepositoryEntity,
    capability_alignment: OpportunityCapabilityAlignment,
) -> tuple[OpportunityScopeEvidence, ...]:
    return (
        OpportunityScopeEvidence(
            evidence_type="repository-fact",
            source=f"{entity.path}#title",
            statement=f"Title: {entity.title}",
        ),
        OpportunityScopeEvidence(
            evidence_type="repository-fact",
            source=f"{entity.path}#status",
            statement=f"Lifecycle state: {entity.status}",
        ),
        OpportunityScopeEvidence(
            evidence_type="repository-fact",
            source=f"{entity.path}#capability",
            statement=f"Declared capability: {entity.capability}",
        ),
        OpportunityScopeEvidence(
            evidence_type="repository-fact",
            source=(
                "atlas.platform.reasoning."
                "opportunity_capability_alignment"
            ),
            statement=(
                "Capability Alignment state: "
                f"{capability_alignment.alignment_state}"
            ),
        ),
        OpportunityScopeEvidence(
            evidence_type="repository-fact",
            source=entity.path,
            statement=(
                "Explicit references: "
                f"{len(entity.dependencies)} dependencies, "
                f"{len(entity.related_opportunities)} related opportunities, "
                f"{len(entity.related_documents)} related documents."
            ),
        ),
    )


def _structural_evidence(
    entity: RepositoryEntity,
    capability_alignment: OpportunityCapabilityAlignment,
    root: Path,
) -> tuple[OpportunityScopeEvidence, ...]:
    evidence: list[OpportunityScopeEvidence] = [
        OpportunityScopeEvidence(
            evidence_type="structural",
            source=(
                "atlas.platform.reasoning."
                "opportunity_capability_alignment"
            ),
            statement=(
                "Capability Alignment is available as supporting context "
                f"with state '{capability_alignment.alignment_state}'. "
                "Capability identity does not determine scope."
            ),
        )
    ]

    for reference in entity.related_documents:
        reference_path = Path(reference)
        exists = (
            not reference_path.is_absolute()
            and ".." not in reference_path.parts
            and (root / reference_path).is_file()
        )
        if reference.startswith("docs/architecture/"):
            evidence.append(
                OpportunityScopeEvidence(
                    evidence_type="structural",
                    source=f"{entity.path}#related-document",
                    statement=(
                        f"Related architecture document: {reference}; "
                        f"exists={'yes' if exists else 'no'}. "
                        "An architecture reference supports review but does "
                        "not automatically resolve Architecture Opportunity."
                    ),
                    scope_id="architecture-opportunity",
                )
            )
        else:
            evidence.append(
                OpportunityScopeEvidence(
                    evidence_type="structural",
                    source=f"{entity.path}#related-document",
                    statement=(
                        f"Related repository document: {reference}; "
                        f"exists={'yes' if exists else 'no'}."
                    ),
                )
            )

    if entity.dependencies:
        evidence.append(
            OpportunityScopeEvidence(
                evidence_type="structural",
                source=f"{entity.path}#dependencies",
                statement=(
                    f"The opportunity declares {len(entity.dependencies)} "
                    "explicit dependencies."
                ),
            )
        )

    if entity.related_opportunities:
        evidence.append(
            OpportunityScopeEvidence(
                evidence_type="structural",
                source=f"{entity.path}#related-opportunities",
                statement=(
                    "The opportunity declares "
                    f"{len(entity.related_opportunities)} related "
                    "opportunities."
                ),
            )
        )

    return tuple(evidence)


def _heuristic_evidence(
    entity: RepositoryEntity,
) -> tuple[
    dict[str, tuple[OpportunityScopeEvidence, ...]],
    tuple[str, ...],
]:
    fields = _text_fields(entity)
    evidence_by_scope: dict[
        str,
        list[OpportunityScopeEvidence],
    ] = defaultdict(list)

    for scope_id, phrases in SCOPE_SIGNAL_PHRASES.items():
        for phrase in phrases:
            matching_fields = [
                field_name
                for field_name, value in fields
                if _contains_phrase(value, phrase)
            ]
            if not matching_fields:
                continue

            evidence_by_scope[scope_id].append(
                OpportunityScopeEvidence(
                    evidence_type="heuristic",
                    source=(
                        entity.path
                        + "#"
                        + ",".join(matching_fields)
                    ),
                    statement=(
                        f"Transparent phrase signal '{phrase}' appears in "
                        f"{', '.join(matching_fields)}."
                    ),
                    scope_id=scope_id,
                )
            )

    combined_text = "\n".join(value for _, value in fields)
    mixed_markers = tuple(
        marker
        for marker in MIXED_SCOPE_MARKERS
        if _contains_phrase(combined_text, marker)
    )

    return (
        {
            scope_id: tuple(scope_evidence)
            for scope_id, scope_evidence in evidence_by_scope.items()
        },
        mixed_markers,
    )


def _ordered_scope_ids(
    scores: dict[str, int],
) -> tuple[str, ...]:
    order = {
        scope_id: index
        for index, scope_id in enumerate(EXPECTED_SCOPE_IDS)
    }
    return tuple(
        scope_id
        for scope_id, _ in sorted(
            scores.items(),
            key=lambda item: (
                -item[1],
                order[item[0]],
            ),
        )
    )


def _validate_explicit_scope_ids(
    scope_ids: tuple[str, ...],
    field_name: str,
) -> tuple[str, ...]:
    unique_ids = tuple(dict.fromkeys(scope_ids))
    unknown = [
        scope_id
        for scope_id in unique_ids
        if scope_id not in EXPECTED_SCOPE_IDS
    ]
    if unknown:
        raise ValueError(
            f"{field_name} contains unknown scope IDs: {unknown}."
        )
    return unique_ids


def classify_opportunity_scope(
    entity: RepositoryEntity,
    capability_alignment: OpportunityCapabilityAlignment | None = None,
    root: Path | None = None,
    human_reviewed_scope_ids: tuple[str, ...] = (),
    human_reviewed_secondary_scope_ids: tuple[str, ...] = (),
) -> OpportunityScopeClassification:
    catalog = build_scope_catalog()
    definitions = {
        definition.identifier: definition
        for definition in catalog
    }
    alignment = (
        capability_alignment
        if capability_alignment is not None
        else align_opportunity_capability(entity)
    )
    repository_root = root or repo_root()
    facts = _repository_facts(entity, alignment)
    structural = _structural_evidence(
        entity,
        alignment,
        repository_root,
    )
    heuristic_by_scope, mixed_markers = _heuristic_evidence(entity)
    scores = {
        scope_id: len(scope_evidence)
        for scope_id, scope_evidence in heuristic_by_scope.items()
    }
    ordered_signals = _ordered_scope_ids(scores)
    heuristic_evidence = tuple(
        item
        for scope_id in ordered_signals
        for item in heuristic_by_scope[scope_id]
    )
    provenance = (
        entity.path,
        SCOPE_ARCHITECTURE_PATH,
        "atlas.platform.reasoning.opportunity_scope_classification",
    )

    explicit_primary = _validate_explicit_scope_ids(
        human_reviewed_scope_ids,
        "human_reviewed_scope_ids",
    )
    explicit_secondary = _validate_explicit_scope_ids(
        human_reviewed_secondary_scope_ids,
        "human_reviewed_secondary_scope_ids",
    )

    human_evidence = tuple(
        OpportunityScopeEvidence(
            evidence_type="human-reviewed",
            source="human-review-input",
            statement=(
                f"Human-reviewed primary scope evidence: {scope_id}."
            ),
            scope_id=scope_id,
        )
        for scope_id in explicit_primary
    )

    if len(explicit_primary) > 1:
        blocker = (
            "Conflicting human-reviewed primary scope evidence identifies "
            "more than one primary scope."
        )
        return OpportunityScopeClassification(
            opportunity_id=entity.id,
            repository_path=entity.path,
            classification_state="conflicting",
            primary_scope_id=None,
            primary_scope_label=None,
            leading_candidate_scope_id=None,
            candidate_scope_ids=explicit_primary,
            secondary_scope_ids=explicit_secondary,
            facts=facts,
            evidence=structural + human_evidence,
            counterevidence=(),
            provenance=provenance,
            explanation=(
                "Explicit human-reviewed scope evidence conflicts and cannot "
                "be normalized into one primary scope."
            ),
            confidence="High",
            blockers=(blocker,),
            unresolved_questions=(
                "Which human-reviewed scope decision should remain "
                "authoritative?",
            ),
            recommendation=OpportunityAssessmentRecommendation(
                action="resolve-scope-conflict",
                reason=(
                    "Resolve the conflicting explicit scope decisions through "
                    "human review before using scope for progression."
                ),
                confidence="High",
            ),
        )

    if len(explicit_primary) == 1:
        primary_scope_id = explicit_primary[0]
        primary = definitions[primary_scope_id]
        secondary = tuple(
            scope_id
            for scope_id in explicit_secondary
            if scope_id != primary_scope_id
        )
        return OpportunityScopeClassification(
            opportunity_id=entity.id,
            repository_path=entity.path,
            classification_state="resolved",
            primary_scope_id=primary.identifier,
            primary_scope_label=primary.label,
            leading_candidate_scope_id=primary.identifier,
            candidate_scope_ids=(primary.identifier,),
            secondary_scope_ids=secondary,
            facts=facts,
            evidence=structural + human_evidence,
            counterevidence=heuristic_evidence,
            provenance=provenance + ("human-review-input",),
            explanation=(
                f"Human-reviewed evidence resolves primary scope to "
                f"'{primary.identifier}' ({primary.label})."
            ),
            confidence="High",
            blockers=(),
            unresolved_questions=(),
            recommendation=OpportunityAssessmentRecommendation(
                action="retain-scope",
                reason=(
                    "Retain the human-reviewed primary scope while preserving "
                    "canonical object and lifecycle authority."
                ),
                confidence="High",
            ),
        )

    supported_scores = {
        scope_id: score
        for scope_id, score in scores.items()
        if score >= 2
    }
    candidate_scope_ids = _ordered_scope_ids(supported_scores)
    leading_candidate_scope_id: str | None = None

    if candidate_scope_ids:
        highest = supported_scores[candidate_scope_ids[0]]
        next_highest = (
            supported_scores[candidate_scope_ids[1]]
            if len(candidate_scope_ids) > 1
            else -1
        )
        if highest > next_highest:
            leading_candidate_scope_id = candidate_scope_ids[0]

    counterevidence = tuple(
        item
        for scope_id in ordered_signals
        if scope_id not in candidate_scope_ids
        for item in heuristic_by_scope[scope_id]
    )

    if len(candidate_scope_ids) >= 2 and mixed_markers:
        return OpportunityScopeClassification(
            opportunity_id=entity.id,
            repository_path=entity.path,
            classification_state="mixed",
            primary_scope_id=None,
            primary_scope_label=None,
            leading_candidate_scope_id=leading_candidate_scope_id,
            candidate_scope_ids=candidate_scope_ids,
            secondary_scope_ids=(),
            facts=facts,
            evidence=structural + heuristic_evidence,
            counterevidence=counterevidence,
            provenance=provenance,
            explanation=(
                "Transparent heuristic evidence supports several scope "
                "classes, and explicit mixed-outcome language was observed: "
                + ", ".join(mixed_markers)
                + ". No primary scope is resolved."
            ),
            confidence="Medium",
            blockers=(),
            unresolved_questions=(
                "Does this opportunity need clarification or decomposition "
                "before one primary scope can be selected?",
            ),
            recommendation=OpportunityAssessmentRecommendation(
                action="clarify-or-split-scope",
                reason=(
                    "Review the bundled central outcomes and decide whether "
                    "the opportunity should be clarified or split."
                ),
                confidence="Medium",
            ),
        )

    if len(candidate_scope_ids) >= 2:
        return OpportunityScopeClassification(
            opportunity_id=entity.id,
            repository_path=entity.path,
            classification_state="ambiguous",
            primary_scope_id=None,
            primary_scope_label=None,
            leading_candidate_scope_id=leading_candidate_scope_id,
            candidate_scope_ids=candidate_scope_ids,
            secondary_scope_ids=(),
            facts=facts,
            evidence=structural + heuristic_evidence,
            counterevidence=counterevidence,
            provenance=provenance,
            explanation=(
                "Transparent heuristic evidence supports multiple plausible "
                "scope classes. No primary scope is resolved."
            ),
            confidence="Low",
            blockers=(),
            unresolved_questions=(
                "Which candidate best represents the central engineering "
                "outcome of this opportunity?",
            ),
            recommendation=OpportunityAssessmentRecommendation(
                action="clarify-scope",
                reason=(
                    "Review the competing scope candidates and record clearer "
                    "evidence before comparison or progression depends on "
                    "scope."
                ),
                confidence="Low",
            ),
        )

    if len(candidate_scope_ids) == 1:
        candidate = candidate_scope_ids[0]
        label = definitions[candidate].label
        return OpportunityScopeClassification(
            opportunity_id=entity.id,
            repository_path=entity.path,
            classification_state="candidate",
            primary_scope_id=None,
            primary_scope_label=None,
            leading_candidate_scope_id=candidate,
            candidate_scope_ids=(candidate,),
            secondary_scope_ids=(),
            facts=facts,
            evidence=structural + heuristic_evidence,
            counterevidence=counterevidence,
            provenance=provenance,
            explanation=(
                f"Several transparent signals support '{candidate}' "
                f"({label}) as the leading candidate. Semantic evidence is "
                "not treated as a resolved primary scope."
            ),
            confidence="Medium",
            blockers=(),
            unresolved_questions=(
                f"Should human review confirm '{candidate}' as the primary "
                "scope?",
            ),
            recommendation=OpportunityAssessmentRecommendation(
                action="review-scope-candidate",
                reason=(
                    "Review the leading candidate and its evidence without "
                    "rewriting the canonical opportunity object."
                ),
                confidence="Medium",
            ),
        )

    return OpportunityScopeClassification(
        opportunity_id=entity.id,
        repository_path=entity.path,
        classification_state="insufficient-evidence",
        primary_scope_id=None,
        primary_scope_label=None,
        leading_candidate_scope_id=None,
        candidate_scope_ids=(),
        secondary_scope_ids=(),
        facts=facts,
        evidence=structural + heuristic_evidence,
        counterevidence=counterevidence,
        provenance=provenance,
        explanation=(
            "The repository does not contain at least two transparent "
            "independent phrase signals for any scope. No primary scope or "
            "candidate is asserted."
        ),
        confidence="Low",
        blockers=(),
        unresolved_questions=(
            "What central engineering outcome would make this opportunity "
            "complete?",
        ),
        recommendation=OpportunityAssessmentRecommendation(
            action="enrich-scope-evidence",
            reason=(
                "Clarify the opportunity's central outcome before relying on "
                "scope classification."
            ),
            confidence="Low",
        ),
    )
