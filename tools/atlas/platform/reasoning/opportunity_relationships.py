from collections.abc import Iterable

from atlas.platform.repository_objects.models import RepositoryEntity
from atlas.platform.reasoning.models import OpportunityRelationshipFinding


def build_opportunity_relationships(
    entities: Iterable[RepositoryEntity],
) -> tuple[OpportunityRelationshipFinding, ...]:
    opportunity_entities = tuple(entities)
    known_opportunity_ids = frozenset(
        entity.id for entity in opportunity_entities
    )
    relationships: list[OpportunityRelationshipFinding] = []
    seen: set[tuple[str, str, str, str]] = set()

    def add_relationship(
        relationship_type: str,
        source_opportunity_id: str,
        target_opportunity_id: str,
        directionality: str,
        evidence: tuple[str, ...],
        explanation: str,
    ) -> None:
        key = (
            relationship_type,
            source_opportunity_id,
            target_opportunity_id,
            directionality,
        )

        if key in seen:
            return

        seen.add(key)
        relationships.append(
            OpportunityRelationshipFinding(
                relationship_type=relationship_type,
                source_opportunity_id=source_opportunity_id,
                target_opportunity_id=target_opportunity_id,
                directionality=directionality,
                evidence=evidence,
                explanation=explanation,
                confidence="High",
            )
        )

    for entity in opportunity_entities:
        for target in dict.fromkeys(entity.dependencies):
            if target == entity.id or target not in known_opportunity_ids:
                continue

            evidence = (
                f"Source object: {entity.path}",
                f"Explicit dependency target: {target}",
            )
            add_relationship(
                relationship_type="depends_on",
                source_opportunity_id=entity.id,
                target_opportunity_id=target,
                directionality="directional",
                evidence=evidence,
                explanation=(
                    f"{entity.id} explicitly declares {target} as a dependency."
                ),
            )
            add_relationship(
                relationship_type="enables",
                source_opportunity_id=target,
                target_opportunity_id=entity.id,
                directionality="inverse",
                evidence=evidence,
                explanation=(
                    f"{target} enables {entity.id} because {entity.id} "
                    f"explicitly depends on {target}."
                ),
            )

        for target in dict.fromkeys(entity.related_opportunities):
            if target == entity.id or target not in known_opportunity_ids:
                continue

            add_relationship(
                relationship_type="related_to",
                source_opportunity_id=entity.id,
                target_opportunity_id=target,
                directionality="declared",
                evidence=(
                    f"Source object: {entity.path}",
                    f"Explicit related-opportunity target: {target}",
                ),
                explanation=(
                    f"{entity.id} explicitly declares a generic relationship "
                    f"to {target}."
                ),
            )

    return tuple(
        sorted(
            relationships,
            key=lambda relationship: (
                relationship.source_opportunity_id,
                relationship.relationship_type,
                relationship.target_opportunity_id,
                relationship.directionality,
            ),
        )
    )
