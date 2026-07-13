import tempfile
import unittest
from pathlib import Path

from atlas.platform.repository_objects.loader import (
    REQUIRED_FIELDS,
    load_repository_object,
)
from atlas.platform.repository_objects.models import RepositoryEntity
from atlas.platform.reasoning.opportunity_assessment import (
    assess_engineering_opportunities,
    assess_engineering_opportunity,
)


def build_entity(**overrides) -> RepositoryEntity:
    values = {
        "path": (
            "docs/opportunities/captured/"
            "EO-2026-099-example-opportunity.yaml"
        ),
        "object_type": "engineering-opportunity",
        "id": "EO-2026-099",
        "title": "Example opportunity",
        "status": "captured",
        "capability": "Engineering",
        "created": "2026-07-13",
        "source": "test",
        "summary": "Create a bounded example opportunity.",
        "rationale": "The example verifies assessment behavior.",
        "evidence": (),
        "notes": "Observed during deterministic testing.",
        "dependencies": (),
        "related_opportunities": (),
        "related_documents": (),
        "missing_fields": (),
    }
    values.update(overrides)
    return RepositoryEntity(**values)


class EngineeringOpportunityAssessmentTests(unittest.TestCase):
    def test_loader_preserves_bounded_sequences_and_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            path = (
                root
                / "docs/opportunities/captured"
                / "EO-2026-099-example-opportunity.yaml"
            )
            path.parent.mkdir(parents=True)
            path.write_text(
                """id: EO-2026-099

title: Example opportunity

status: captured

capability: Engineering

created: 2026-07-13

source: test

summary: >
  Create a bounded example opportunity.

rationale: >
  The example verifies loader behavior.

dependencies:
  - EO-2026-097

related_opportunities:
  - EO-2026-098

related_documents:
  - docs/architecture/example.md

evidence: |
  - First evidence item continues
    across a wrapped line.
  - Second evidence item.
""",
                encoding="utf-8",
            )

            entity = load_repository_object(
                "engineering-opportunity",
                path,
                root,
            )

        self.assertEqual(entity.dependencies, ("EO-2026-097",))
        self.assertEqual(
            entity.related_opportunities,
            ("EO-2026-098",),
        )
        self.assertEqual(
            entity.related_documents,
            ("docs/architecture/example.md",),
        )
        self.assertEqual(
            entity.evidence,
            (
                "First evidence item continues across a wrapped line.",
                "Second evidence item.",
            ),
        )

    def test_valid_captured_object(self) -> None:
        self.assertIn("rationale", REQUIRED_FIELDS)

        assessment = assess_engineering_opportunity(build_entity())

        self.assertEqual(
            assessment.recommendation.action,
            "retain-captured",
        )
        self.assertEqual(assessment.blockers, ())
        self.assertIn(
            "object-structure-valid",
            {finding.code for finding in assessment.findings},
        )
        self.assertIn(
            "supplemental-evidence-present",
            {fact.name for fact in assessment.facts},
        )

    def test_incomplete_object(self) -> None:
        entity = build_entity(
            summary="",
            rationale="",
            missing_fields=("summary", "rationale"),
        )

        assessment = assess_engineering_opportunity(entity)

        self.assertEqual(assessment.recommendation.action, "enrich")
        self.assertIn(
            "missing-required-fields",
            {finding.code for finding in assessment.findings},
        )
        self.assertIn(
            "Provide required field 'summary'.",
            assessment.blockers,
        )
        self.assertIn(
            "Provide required field 'rationale'.",
            assessment.blockers,
        )

    def test_inconsistent_object(self) -> None:
        entity = build_entity(
            id="opportunity-7",
            status="reviewed",
            path=(
                "docs/opportunities/captured/"
                "unexpected-name.yaml"
            ),
        )

        assessment = assess_engineering_opportunity(entity)
        codes = {finding.code for finding in assessment.findings}

        self.assertEqual(assessment.recommendation.action, "enrich")
        self.assertIn("invalid-identifier", codes)
        self.assertIn("lifecycle-path-mismatch", codes)

    def test_valid_explicit_references(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            document = root / "docs/architecture/example.md"
            document.parent.mkdir(parents=True)
            document.write_text("# Example\n", encoding="utf-8")

            source = build_entity(
                dependencies=("EO-2026-097",),
                related_opportunities=("EO-2026-098",),
                related_documents=("docs/architecture/example.md",),
                evidence=("Observed repository behavior.",),
            )
            dependency = build_entity(
                id="EO-2026-097",
                path=(
                    "docs/opportunities/captured/"
                    "EO-2026-097-dependency.yaml"
                ),
            )
            related = build_entity(
                id="EO-2026-098",
                path=(
                    "docs/opportunities/captured/"
                    "EO-2026-098-related.yaml"
                ),
            )

            assessments = assess_engineering_opportunities(
                (source, dependency, related),
                root=root,
            )

        assessment = assessments[0]
        codes = {finding.code for finding in assessment.findings}
        facts = {(fact.name, fact.value) for fact in assessment.facts}

        self.assertEqual(assessment.blockers, ())
        self.assertIn("explicit-references-valid", codes)
        self.assertIn(("dependency", "EO-2026-097"), facts)
        self.assertIn(
            ("related-opportunity", "EO-2026-098"),
            facts,
        )
        self.assertIn(
            ("related-document", "docs/architecture/example.md"),
            facts,
        )
        self.assertIn(
            ("evidence-item", "Observed repository behavior."),
            facts,
        )

    def test_missing_opportunity_target(self) -> None:
        entity = build_entity(
            related_opportunities=("EO-2026-404",),
        )

        assessment = assess_engineering_opportunities((entity,))[0]
        codes = {finding.code for finding in assessment.findings}

        self.assertEqual(assessment.recommendation.action, "enrich")
        self.assertIn("missing-opportunity-reference", codes)
        self.assertTrue(
            any("EO-2026-404" in blocker for blocker in assessment.blockers)
        )

    def test_missing_document_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            entity = build_entity(
                related_documents=("docs/architecture/missing.md",),
            )

            assessment = assess_engineering_opportunities(
                (entity,),
                root=Path(temporary_directory),
            )[0]

        codes = {finding.code for finding in assessment.findings}

        self.assertEqual(assessment.recommendation.action, "enrich")
        self.assertIn("missing-document-reference", codes)
        self.assertTrue(
            any(
                "docs/architecture/missing.md" in blocker
                for blocker in assessment.blockers
            )
        )

    def test_absent_optional_references_remain_valid(self) -> None:
        assessment = assess_engineering_opportunities(
            (build_entity(),),
        )[0]
        codes = {finding.code for finding in assessment.findings}

        self.assertEqual(assessment.recommendation.action, "retain-captured")
        self.assertEqual(assessment.blockers, ())
        self.assertNotIn("missing-opportunity-reference", codes)
        self.assertNotIn("missing-document-reference", codes)


if __name__ == "__main__":
    unittest.main()
