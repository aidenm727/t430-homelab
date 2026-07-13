from dataclasses import dataclass
from pathlib import Path
import re

from atlas.platform.repository import repo_root
from atlas.platform.repository_objects.models import RepositoryEntity
from atlas.platform.reasoning.models import (
    OpportunityAssessmentRecommendation,
    OpportunityCapabilityAlignment,
)


CAPABILITY_SOURCE_PATH = "docs/architecture/capabilities.md"
CAPABILITY_TABLE_ROW = re.compile(
    r"^\| `(?P<identifier>[a-z0-9-]+)` \| "
    r"(?P<label>[^|]+?) \|$",
    re.MULTILINE,
)

EXPECTED_CAPABILITY_IDS = frozenset(
    {
        "compute",
        "storage",
        "networking-access",
        "observability",
        "automation",
        "knowledge-documentation",
        "engineering",
        "personal-services",
        "ai-aiden-os",
    }
)

CAPABILITY_ALIASES = {
    "AI": "ai-aiden-os",
    "Documentation": "knowledge-documentation",
}

AMBIGUOUS_CAPABILITY_VALUES = {
    "Infrastructure": (
        "compute",
        "storage",
        "networking-access",
        "observability",
        "automation",
    ),
}


@dataclass(frozen=True)
class CapabilityDefinition:
    identifier: str
    label: str
    source: str = CAPABILITY_SOURCE_PATH


def build_capability_catalog(
    root: Path | None = None,
) -> tuple[CapabilityDefinition, ...]:
    capability_path = (root or repo_root()) / CAPABILITY_SOURCE_PATH
    content = capability_path.read_text(encoding="utf-8")
    definitions = tuple(
        CapabilityDefinition(
            identifier=match.group("identifier"),
            label=match.group("label").strip(),
        )
        for match in CAPABILITY_TABLE_ROW.finditer(content)
    )

    observed_ids = [definition.identifier for definition in definitions]
    observed_labels = [definition.label for definition in definitions]

    if len(observed_ids) != len(set(observed_ids)):
        raise ValueError(
            "The canonical capability map contains duplicate capability IDs."
        )

    if len(observed_labels) != len(set(observed_labels)):
        raise ValueError(
            "The canonical capability map contains duplicate display labels."
        )

    if frozenset(observed_ids) != EXPECTED_CAPABILITY_IDS:
        missing = sorted(EXPECTED_CAPABILITY_IDS - set(observed_ids))
        unexpected = sorted(set(observed_ids) - EXPECTED_CAPABILITY_IDS)
        raise ValueError(
            "The canonical capability catalog does not match the "
            f"architecture contract. Missing={missing}; unexpected={unexpected}."
        )

    return definitions


def _resolved_alignment(
    entity: RepositoryEntity,
    definition: CapabilityDefinition,
    alignment_state: str,
    rule: str,
    recommendation: OpportunityAssessmentRecommendation,
) -> OpportunityCapabilityAlignment:
    return OpportunityCapabilityAlignment(
        opportunity_id=entity.id,
        repository_path=entity.path,
        declared_value=entity.capability,
        alignment_state=alignment_state,
        primary_capability_id=definition.identifier,
        primary_capability_label=definition.label,
        candidate_capability_ids=(),
        secondary_capability_ids=(),
        evidence=(
            f"Source object: {entity.path}",
            f"Declared capability: {entity.capability}",
            f"Canonical capability source: {CAPABILITY_SOURCE_PATH}",
            f"Alignment rule: {rule}",
        ),
        provenance=(
            entity.path,
            CAPABILITY_SOURCE_PATH,
            "atlas.platform.reasoning.opportunity_capability_alignment",
        ),
        explanation=(
            f"Declared capability '{entity.capability}' resolves to "
            f"'{definition.identifier}' ({definition.label}) through {rule}."
        ),
        confidence="High",
        blockers=(),
        unresolved_questions=(),
        recommendation=recommendation,
    )


def align_opportunity_capability(
    entity: RepositoryEntity,
    root: Path | None = None,
) -> OpportunityCapabilityAlignment:
    catalog = build_capability_catalog(root)
    by_identifier = {
        definition.identifier: definition
        for definition in catalog
    }
    by_label = {
        definition.label: definition
        for definition in catalog
    }
    declared_value = entity.capability

    if declared_value in by_identifier:
        definition = by_identifier[declared_value]
        return _resolved_alignment(
            entity,
            definition,
            alignment_state="canonical-id",
            rule="an exact canonical identifier match",
            recommendation=OpportunityAssessmentRecommendation(
                action="retain-capability",
                reason=(
                    "The declared capability already uses the stable "
                    "canonical identifier."
                ),
                confidence="High",
            ),
        )

    if declared_value in by_label:
        definition = by_label[declared_value]
        return _resolved_alignment(
            entity,
            definition,
            alignment_state="canonical-label",
            rule="an exact canonical display-label match",
            recommendation=OpportunityAssessmentRecommendation(
                action="review-capability-migration",
                reason=(
                    "The declared display label resolves deterministically. "
                    "Migration to the stable identifier remains a separate "
                    "human-authorized repository change."
                ),
                confidence="High",
            ),
        )

    if declared_value in CAPABILITY_ALIASES:
        definition = by_identifier[CAPABILITY_ALIASES[declared_value]]
        return _resolved_alignment(
            entity,
            definition,
            alignment_state="alias",
            rule=f"the curated alias '{declared_value}'",
            recommendation=OpportunityAssessmentRecommendation(
                action="review-capability-migration",
                reason=(
                    "The curated alias resolves deterministically. Migration "
                    "to the stable identifier remains human-authorized."
                ),
                confidence="High",
            ),
        )

    if declared_value in AMBIGUOUS_CAPABILITY_VALUES:
        candidates = AMBIGUOUS_CAPABILITY_VALUES[declared_value]
        blocker = (
            f"Declared capability '{declared_value}' does not identify one "
            "primary canonical capability."
        )
        return OpportunityCapabilityAlignment(
            opportunity_id=entity.id,
            repository_path=entity.path,
            declared_value=declared_value,
            alignment_state="ambiguous",
            primary_capability_id=None,
            primary_capability_label=None,
            candidate_capability_ids=candidates,
            secondary_capability_ids=(),
            evidence=(
                f"Source object: {entity.path}",
                f"Declared capability: {declared_value}",
                f"Canonical capability source: {CAPABILITY_SOURCE_PATH}",
                "Compatibility rule: broad legacy Infrastructure domain",
                "Candidate capabilities: " + ", ".join(candidates),
            ),
            provenance=(
                entity.path,
                CAPABILITY_SOURCE_PATH,
                "atlas.platform.reasoning.opportunity_capability_alignment",
            ),
            explanation=(
                f"Declared capability '{declared_value}' spans multiple "
                "canonical capabilities and cannot be reduced "
                "deterministically to one primary capability."
            ),
            confidence="High",
            blockers=(blocker,),
            unresolved_questions=(
                "Which canonical capability should be selected as the "
                f"primary capability for {entity.id}?",
            ),
            recommendation=OpportunityAssessmentRecommendation(
                action="resolve-capability",
                reason=(
                    "Select one primary canonical capability through human "
                    "review before lifecycle progression."
                ),
                confidence="High",
            ),
        )

    blocker = (
        f"Declared capability '{declared_value}' does not resolve to a "
        "canonical capability identifier, label, or curated alias."
    )
    return OpportunityCapabilityAlignment(
        opportunity_id=entity.id,
        repository_path=entity.path,
        declared_value=declared_value,
        alignment_state="unknown",
        primary_capability_id=None,
        primary_capability_label=None,
        candidate_capability_ids=(),
        secondary_capability_ids=(),
        evidence=(
            f"Source object: {entity.path}",
            f"Declared capability: {declared_value}",
            f"Canonical capability source: {CAPABILITY_SOURCE_PATH}",
            "Alignment rule: no canonical identifier, label, alias, or "
            "recognized broad compatibility value matched",
        ),
        provenance=(
            entity.path,
            CAPABILITY_SOURCE_PATH,
            "atlas.platform.reasoning.opportunity_capability_alignment",
        ),
        explanation=(
            f"Declared capability '{declared_value}' is unknown to the "
            "current canonical Platform Capability Map."
        ),
        confidence="High",
        blockers=(blocker,),
        unresolved_questions=(
            "Should the opportunity be reclassified to an existing "
            "capability, or should the Platform Capability Map evolve?",
        ),
        recommendation=OpportunityAssessmentRecommendation(
            action="review-capability",
            reason=(
                "Resolve the unknown declared capability through human "
                "architecture and opportunity review."
            ),
            confidence="High",
        ),
    )
