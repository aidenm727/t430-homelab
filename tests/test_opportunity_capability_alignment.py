import unittest

from atlas.platform.repository_objects.models import RepositoryEntity
from atlas.platform.reasoning.opportunity_assessment import (
    assess_engineering_opportunity,
)
from atlas.platform.reasoning.opportunity_capability_alignment import (
    EXPECTED_CAPABILITY_IDS,
    align_opportunity_capability,
    build_capability_catalog,
)


def build_entity(capability: str, **overrides) -> RepositoryEntity:
    values = {
        "path": (
            "docs/opportunities/captured/"
            "EO-2026-099-capability-alignment-example.yaml"
        ),
        "object_type": "engineering-opportunity",
        "id": "EO-2026-099",
        "title": "Capability alignment example",
        "status": "captured",
        "capability": capability,
        "created": "2026-07-13",
        "source": "test",
        "summary": "Create a bounded capability alignment example.",
        "rationale": "The example verifies deterministic capability reasoning.",
        "evidence": ("Observed during deterministic testing.",),
        "notes": "",
        "dependencies": (),
        "related_opportunities": (),
        "related_documents": (),
        "missing_fields": (),
    }
    values.update(overrides)
    return RepositoryEntity(**values)


class EngineeringOpportunityCapabilityAlignmentTests(unittest.TestCase):
    def test_catalog_contains_architecture_owned_capabilities(self) -> None:
        catalog = build_capability_catalog()

        self.assertEqual(
            {definition.identifier for definition in catalog},
            EXPECTED_CAPABILITY_IDS,
        )
        self.assertEqual(len(catalog), 9)

    def test_exact_canonical_identifier_resolves(self) -> None:
        alignment = align_opportunity_capability(
            build_entity("engineering")
        )

        self.assertEqual(alignment.alignment_state, "canonical-id")
        self.assertEqual(alignment.primary_capability_id, "engineering")
        self.assertEqual(alignment.primary_capability_label, "Engineering")
        self.assertEqual(alignment.blockers, ())

    def test_exact_canonical_label_resolves(self) -> None:
        alignment = align_opportunity_capability(
            build_entity("Engineering")
        )

        self.assertEqual(alignment.alignment_state, "canonical-label")
        self.assertEqual(alignment.primary_capability_id, "engineering")
        self.assertEqual(
            alignment.recommendation.action,
            "review-capability-migration",
        )

    def test_ai_alias_resolves(self) -> None:
        alignment = align_opportunity_capability(build_entity("AI"))

        self.assertEqual(alignment.alignment_state, "alias")
        self.assertEqual(alignment.primary_capability_id, "ai-aiden-os")
        self.assertIn("curated alias", alignment.explanation)

    def test_documentation_alias_resolves(self) -> None:
        alignment = align_opportunity_capability(
            build_entity("Documentation")
        )

        self.assertEqual(alignment.alignment_state, "alias")
        self.assertEqual(
            alignment.primary_capability_id,
            "knowledge-documentation",
        )

    def test_infrastructure_is_ambiguous(self) -> None:
        alignment = align_opportunity_capability(
            build_entity("Infrastructure")
        )

        self.assertEqual(alignment.alignment_state, "ambiguous")
        self.assertIsNone(alignment.primary_capability_id)
        self.assertEqual(
            alignment.candidate_capability_ids,
            (
                "compute",
                "storage",
                "networking-access",
                "observability",
                "automation",
            ),
        )
        self.assertTrue(alignment.blockers)
        self.assertTrue(alignment.unresolved_questions)

    def test_learning_is_unknown(self) -> None:
        alignment = align_opportunity_capability(
            build_entity("Learning")
        )

        self.assertEqual(alignment.alignment_state, "unknown")
        self.assertIsNone(alignment.primary_capability_id)
        self.assertEqual(
            alignment.recommendation.action,
            "review-capability",
        )

    def test_arbitrary_unsupported_value_is_unknown(self) -> None:
        alignment = align_opportunity_capability(
            build_entity("Unregistered Capability")
        )

        self.assertEqual(alignment.alignment_state, "unknown")
        self.assertIn(
            "Unregistered Capability",
            alignment.explanation,
        )

    def test_raw_declared_value_is_preserved_without_mutation(self) -> None:
        entity = build_entity("AI")
        original = entity

        alignment = align_opportunity_capability(entity)

        self.assertEqual(alignment.declared_value, "AI")
        self.assertEqual(entity, original)
        self.assertEqual(entity.capability, "AI")

    def test_assessment_consumes_resolved_alignment(self) -> None:
        assessment = assess_engineering_opportunity(
            build_entity("Engineering")
        )

        self.assertIsNotNone(assessment.capability_alignment)
        self.assertEqual(
            assessment.capability_alignment.alignment_state,
            "canonical-label",
        )
        self.assertEqual(assessment.blockers, ())
        self.assertIn(
            ("capability-alignment-state", "canonical-label"),
            {(fact.name, fact.value) for fact in assessment.facts},
        )

    def test_unresolved_alignment_recommends_enrichment(self) -> None:
        assessment = assess_engineering_opportunity(
            build_entity("Infrastructure")
        )
        codes = {finding.code for finding in assessment.findings}

        self.assertEqual(assessment.recommendation.action, "enrich")
        self.assertIn("capability-alignment-ambiguous", codes)
        self.assertTrue(
            any("primary canonical capability" in blocker
                for blocker in assessment.blockers)
        )

    def test_alignment_does_not_infer_from_prose(self) -> None:
        entity = build_entity(
            "Unregistered Capability",
            title="Engineering automation",
            summary="Improve Engineering and Automation.",
            rationale="The work is clearly related to Engineering.",
            notes="Keywords must not override the declared value.",
        )

        alignment = align_opportunity_capability(entity)

        self.assertEqual(alignment.alignment_state, "unknown")
        self.assertIsNone(alignment.primary_capability_id)


if __name__ == "__main__":
    unittest.main()
