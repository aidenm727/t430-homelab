import tempfile
import unittest
from pathlib import Path

from atlas.platform.repository_objects.models import RepositoryEntity
from atlas.platform.reasoning.opportunity_assessment import (
    assess_engineering_opportunity,
)
from atlas.platform.reasoning.opportunity_scope_classification import (
    EXPECTED_SCOPE_IDS,
    build_scope_catalog,
    classify_opportunity_scope,
)


def build_entity(**overrides) -> RepositoryEntity:
    values = {
        "path": (
            "docs/opportunities/captured/"
            "EO-2026-099-scope-classification-example.yaml"
        ),
        "object_type": "engineering-opportunity",
        "id": "EO-2026-099",
        "title": "Example opportunity",
        "status": "captured",
        "capability": "Engineering",
        "created": "2026-07-13",
        "source": "test",
        "summary": "Clarify an example engineering possibility.",
        "rationale": "The example verifies bounded scope reasoning.",
        "evidence": (),
        "notes": "",
        "dependencies": (),
        "related_opportunities": (),
        "related_documents": (),
        "missing_fields": (),
    }
    values.update(overrides)
    return RepositoryEntity(**values)


class EngineeringOpportunityScopeClassificationTests(unittest.TestCase):
    def test_catalog_contains_six_architecture_owned_scopes(self) -> None:
        catalog = build_scope_catalog()

        self.assertEqual(
            tuple(definition.identifier for definition in catalog),
            EXPECTED_SCOPE_IDS,
        )
        self.assertEqual(len(catalog), 6)

    def test_several_transparent_signals_produce_candidate(self) -> None:
        classification = classify_opportunity_scope(
            build_entity(
                title="Atlas engineering workflow",
                summary=(
                    "Improve repository reasoning and engineering session "
                    "startup."
                ),
            )
        )

        self.assertEqual(classification.classification_state, "candidate")
        self.assertIsNone(classification.primary_scope_id)
        self.assertEqual(
            classification.leading_candidate_scope_id,
            "engineering-system-opportunity",
        )
        self.assertEqual(classification.confidence, "Medium")

    def test_one_keyword_cannot_resolve_scope(self) -> None:
        classification = classify_opportunity_scope(
            build_entity(
                title="Architecture",
                summary="Clarify this opportunity.",
                rationale="More evidence is required.",
            )
        )

        self.assertEqual(
            classification.classification_state,
            "insufficient-evidence",
        )
        self.assertIsNone(classification.primary_scope_id)

    def test_competing_signals_produce_ambiguous_result(self) -> None:
        classification = classify_opportunity_scope(
            build_entity(
                summary=(
                    "Create a durable capability and reusable capability "
                    "through architecture and explicit system boundaries."
                ),
            )
        )

        self.assertEqual(
            classification.classification_state,
            "ambiguous",
        )
        self.assertIn(
            "capability-opportunity",
            classification.candidate_scope_ids,
        )
        self.assertIn(
            "architecture-opportunity",
            classification.candidate_scope_ids,
        )
        self.assertIsNone(classification.primary_scope_id)

    def test_bundled_outcomes_produce_mixed_result(self) -> None:
        classification = classify_opportunity_scope(
            build_entity(
                summary=(
                    "Combines a platform capability and reusable capability "
                    "with a bounded implementation and refactor."
                ),
            )
        )

        self.assertEqual(classification.classification_state, "mixed")
        self.assertIn(
            "capability-opportunity",
            classification.candidate_scope_ids,
        )
        self.assertIn(
            "implementation-opportunity",
            classification.candidate_scope_ids,
        )

    def test_sparse_evidence_produces_insufficient_result(self) -> None:
        classification = classify_opportunity_scope(
            build_entity(
                title="Improve this idea",
                summary="Make the idea clearer.",
                rationale="The current description is sparse.",
            )
        )

        self.assertEqual(
            classification.classification_state,
            "insufficient-evidence",
        )
        self.assertEqual(classification.candidate_scope_ids, ())
        self.assertTrue(classification.unresolved_questions)

    def test_conflicting_human_reviewed_scopes_are_exposed(self) -> None:
        classification = classify_opportunity_scope(
            build_entity(),
            human_reviewed_scope_ids=(
                "capability-opportunity",
                "architecture-opportunity",
            ),
        )

        self.assertEqual(
            classification.classification_state,
            "conflicting",
        )
        self.assertIsNone(classification.primary_scope_id)
        self.assertTrue(classification.blockers)
        self.assertEqual(
            classification.recommendation.action,
            "resolve-scope-conflict",
        )

    def test_human_reviewed_scope_resolves_with_high_confidence(self) -> None:
        classification = classify_opportunity_scope(
            build_entity(),
            human_reviewed_scope_ids=(
                "engineering-system-opportunity",
            ),
        )

        self.assertEqual(classification.classification_state, "resolved")
        self.assertEqual(
            classification.primary_scope_id,
            "engineering-system-opportunity",
        )
        self.assertEqual(
            classification.primary_scope_label,
            "Engineering System Opportunity",
        )
        self.assertEqual(classification.confidence, "High")

    def test_secondary_scopes_remain_separate_from_primary(self) -> None:
        classification = classify_opportunity_scope(
            build_entity(),
            human_reviewed_scope_ids=("capability-opportunity",),
            human_reviewed_secondary_scope_ids=(
                "architecture-opportunity",
                "implementation-opportunity",
            ),
        )

        self.assertEqual(
            classification.primary_scope_id,
            "capability-opportunity",
        )
        self.assertEqual(
            classification.secondary_scope_ids,
            (
                "architecture-opportunity",
                "implementation-opportunity",
            ),
        )

    def test_capability_identity_alone_does_not_resolve_scope(self) -> None:
        classification = classify_opportunity_scope(
            build_entity(
                capability="AI",
                title="Example possibility",
                summary="Clarify the central outcome.",
                rationale="Capability identity is only supporting context.",
            )
        )

        self.assertEqual(
            classification.classification_state,
            "insufficient-evidence",
        )
        self.assertIsNone(classification.primary_scope_id)

    def test_related_architecture_is_structural_not_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            document = root / "docs/architecture/example.md"
            document.parent.mkdir(parents=True)
            document.write_text("# Example\n", encoding="utf-8")

            classification = classify_opportunity_scope(
                build_entity(
                    related_documents=(
                        "docs/architecture/example.md",
                    ),
                ),
                root=root,
            )

        self.assertEqual(
            classification.classification_state,
            "insufficient-evidence",
        )
        self.assertIsNone(classification.primary_scope_id)
        self.assertTrue(
            any(
                "Related architecture document" in item.statement
                for item in classification.evidence
            )
        )

    def test_raw_opportunity_object_is_not_mutated(self) -> None:
        entity = build_entity(
            title="Atlas engineering workflow",
            summary=(
                "Improve repository reasoning and engineering session "
                "startup."
            ),
        )
        original = entity

        classification = classify_opportunity_scope(entity)

        self.assertEqual(
            classification.classification_state,
            "candidate",
        )
        self.assertEqual(entity, original)
        self.assertEqual(entity.status, "captured")

    def test_assessment_consumes_scope_classification(self) -> None:
        assessment = assess_engineering_opportunity(
            build_entity(
                title="Atlas engineering workflow",
                summary=(
                    "Improve repository reasoning and engineering session "
                    "startup."
                ),
            )
        )

        self.assertIsNotNone(assessment.scope_classification)
        self.assertEqual(
            assessment.scope_classification.classification_state,
            "candidate",
        )
        self.assertIn(
            ("scope-classification-state", "candidate"),
            {(fact.name, fact.value) for fact in assessment.facts},
        )
        self.assertEqual(
            assessment.recommendation.action,
            "retain-captured",
        )

    def test_scope_classification_never_mutates_lifecycle_state(self) -> None:
        entity = build_entity(status="reviewed", path=(
            "docs/opportunities/reviewed/"
            "EO-2026-099-scope-classification-example.yaml"
        ))

        classification = classify_opportunity_scope(
            entity,
            human_reviewed_scope_ids=(
                "implementation-opportunity",
            ),
        )

        self.assertEqual(classification.classification_state, "resolved")
        self.assertEqual(entity.status, "reviewed")


if __name__ == "__main__":
    unittest.main()
