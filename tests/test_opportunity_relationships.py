import unittest

from atlas.platform.repository_objects.models import RepositoryEntity
from atlas.platform.reasoning.opportunity_assessment import (
    assess_engineering_opportunities,
)
from atlas.platform.reasoning.opportunity_relationships import (
    build_opportunity_relationships,
)


def build_entity(identifier: str, **overrides) -> RepositoryEntity:
    values = {
        "path": (
            "docs/opportunities/captured/"
            f"{identifier}-example-opportunity.yaml"
        ),
        "object_type": "engineering-opportunity",
        "id": identifier,
        "title": "Example opportunity",
        "status": "captured",
        "capability": "Engineering",
        "created": "2026-07-13",
        "source": "test",
        "summary": "Create a bounded example opportunity.",
        "rationale": "The example verifies relationship behavior.",
        "evidence": ("Observed during deterministic testing.",),
        "notes": "",
        "dependencies": (),
        "related_opportunities": (),
        "related_documents": (),
        "missing_fields": (),
    }
    values.update(overrides)
    return RepositoryEntity(**values)


class EngineeringOpportunityRelationshipTests(unittest.TestCase):
    def test_dependency_builds_directional_and_inverse_relationships(self) -> None:
        source = build_entity(
            "EO-2026-099",
            dependencies=("EO-2026-098",),
        )
        target = build_entity("EO-2026-098")

        relationships = build_opportunity_relationships((source, target))
        signatures = {
            (
                relationship.relationship_type,
                relationship.source_opportunity_id,
                relationship.target_opportunity_id,
                relationship.directionality,
            )
            for relationship in relationships
        }

        self.assertIn(
            (
                "depends_on",
                "EO-2026-099",
                "EO-2026-098",
                "directional",
            ),
            signatures,
        )
        self.assertIn(
            (
                "enables",
                "EO-2026-098",
                "EO-2026-099",
                "inverse",
            ),
            signatures,
        )
        self.assertTrue(
            all(relationship.confidence == "High" for relationship in relationships)
        )
        self.assertTrue(all(relationship.evidence for relationship in relationships))

    def test_related_opportunity_builds_declared_relationship(self) -> None:
        source = build_entity(
            "EO-2026-099",
            related_opportunities=("EO-2026-098",),
        )
        target = build_entity("EO-2026-098")

        relationships = build_opportunity_relationships((source, target))

        self.assertEqual(len(relationships), 1)
        self.assertEqual(relationships[0].relationship_type, "related_to")
        self.assertEqual(relationships[0].directionality, "declared")
        self.assertEqual(
            relationships[0].source_opportunity_id,
            "EO-2026-099",
        )
        self.assertEqual(
            relationships[0].target_opportunity_id,
            "EO-2026-098",
        )

    def test_assessments_receive_portfolio_relationships(self) -> None:
        source = build_entity(
            "EO-2026-099",
            dependencies=("EO-2026-098",),
        )
        target = build_entity("EO-2026-098")

        assessments = assess_engineering_opportunities((source, target))
        by_id = {
            assessment.opportunity_id: assessment
            for assessment in assessments
        }

        self.assertEqual(
            by_id["EO-2026-099"].relationships[0].relationship_type,
            "depends_on",
        )
        self.assertEqual(
            by_id["EO-2026-098"].relationships[0].relationship_type,
            "enables",
        )

    def test_self_reference_produces_finding(self) -> None:
        entity = build_entity(
            "EO-2026-099",
            dependencies=("EO-2026-099",),
        )

        assessment = assess_engineering_opportunities((entity,))[0]
        codes = {finding.code for finding in assessment.findings}

        self.assertEqual(assessment.recommendation.action, "enrich")
        self.assertIn("self-opportunity-relationship", codes)
        self.assertTrue(
            any("itself" in blocker for blocker in assessment.blockers)
        )
        self.assertEqual(assessment.relationships, ())

    def test_duplicate_declaration_produces_finding(self) -> None:
        source = build_entity(
            "EO-2026-099",
            dependencies=("EO-2026-098", "EO-2026-098"),
        )
        target = build_entity("EO-2026-098")

        assessment = assess_engineering_opportunities((source, target))[0]
        codes = {finding.code for finding in assessment.findings}

        self.assertEqual(assessment.recommendation.action, "enrich")
        self.assertIn("duplicate-relationship-declaration", codes)
        self.assertEqual(
            sum(
                relationship.relationship_type == "depends_on"
                for relationship in assessment.relationships
            ),
            1,
        )

    def test_conflicting_declarations_produce_finding(self) -> None:
        source = build_entity(
            "EO-2026-099",
            dependencies=("EO-2026-098",),
            related_opportunities=("EO-2026-098",),
        )
        target = build_entity("EO-2026-098")

        assessment = assess_engineering_opportunities((source, target))[0]
        codes = {finding.code for finding in assessment.findings}
        relationship_types = {
            relationship.relationship_type
            for relationship in assessment.relationships
        }

        self.assertEqual(assessment.recommendation.action, "enrich")
        self.assertIn("conflicting-relationship-declaration", codes)
        self.assertIn("depends_on", relationship_types)
        self.assertIn("related_to", relationship_types)

    def test_absent_relationships_remain_valid(self) -> None:
        assessment = assess_engineering_opportunities(
            (build_entity("EO-2026-099"),)
        )[0]
        codes = {finding.code for finding in assessment.findings}

        self.assertEqual(assessment.recommendation.action, "retain-captured")
        self.assertEqual(assessment.relationships, ())
        self.assertNotIn("self-opportunity-relationship", codes)
        self.assertNotIn("duplicate-relationship-declaration", codes)
        self.assertNotIn("conflicting-relationship-declaration", codes)


if __name__ == "__main__":
    unittest.main()
