import unittest

from atlas.platform.repository_objects.loader import REQUIRED_FIELDS
from atlas.platform.repository_objects.models import RepositoryEntity
from atlas.platform.reasoning.opportunity_assessment import (
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
        "evidence": "",
        "notes": "Observed during deterministic testing.",
        "missing_fields": (),
    }
    values.update(overrides)
    return RepositoryEntity(**values)


class EngineeringOpportunityAssessmentTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
