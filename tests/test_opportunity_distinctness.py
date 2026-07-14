import unittest

from atlas.platform.repository_objects.models import RepositoryEntity
from atlas.platform.reasoning.models import (
    OpportunityCapabilityAlignment,
    OpportunityScopeClassification,
)
from atlas.platform.reasoning.opportunity_assessment import (
    assess_engineering_opportunities,
)
from atlas.platform.reasoning.opportunity_distinctness import (
    build_opportunity_distinctness_portfolio,
    build_opportunity_pair_key,
    compare_opportunity_distinctness,
)


def build_entity(identifier: str, **overrides) -> RepositoryEntity:
    suffix = identifier.lower().replace("-", "-")
    values = {
        "path": (
            "docs/opportunities/captured/"
            f"{identifier}-{suffix}-example.yaml"
        ),
        "object_type": "engineering-opportunity",
        "id": identifier,
        "title": f"Example {identifier}",
        "status": "captured",
        "capability": "Engineering",
        "created": "2026-07-13",
        "source": "test",
        "summary": f"Clarify engineering possibility {identifier}.",
        "rationale": f"Verify bounded comparison for {identifier}.",
        "evidence": (),
        "notes": "",
        "dependencies": (),
        "related_opportunities": (),
        "related_documents": (),
        "missing_fields": (),
    }
    values.update(overrides)
    return RepositoryEntity(**values)


def build_alignment(
    entity: RepositoryEntity,
    capability_id: str | None = "engineering",
) -> OpportunityCapabilityAlignment:
    candidates = () if capability_id is not None else ()
    return OpportunityCapabilityAlignment(
        opportunity_id=entity.id,
        repository_path=entity.path,
        declared_value=entity.capability,
        alignment_state=(
            "canonical-id"
            if capability_id is not None
            else "unknown"
        ),
        primary_capability_id=capability_id,
        primary_capability_label=(
            capability_id
            if capability_id is not None
            else None
        ),
        candidate_capability_ids=candidates,
        secondary_capability_ids=(),
        evidence=("test capability evidence",),
        provenance=("test",),
        explanation="Test capability alignment.",
        confidence="High",
        blockers=(),
        unresolved_questions=(),
    )


def build_scope(
    entity: RepositoryEntity,
    scope_id: str | None = None,
) -> OpportunityScopeClassification:
    return OpportunityScopeClassification(
        opportunity_id=entity.id,
        repository_path=entity.path,
        classification_state=(
            "resolved"
            if scope_id is not None
            else "insufficient-evidence"
        ),
        primary_scope_id=scope_id,
        primary_scope_label=scope_id,
        leading_candidate_scope_id=scope_id,
        candidate_scope_ids=(
            (scope_id,)
            if scope_id is not None
            else ()
        ),
        secondary_scope_ids=(),
        facts=(),
        evidence=(),
        counterevidence=(),
        provenance=("test",),
        explanation="Test scope classification.",
        confidence=(
            "High"
            if scope_id is not None
            else "Low"
        ),
        blockers=(),
        unresolved_questions=(),
    )


def compare(
    left: RepositoryEntity,
    right: RepositoryEntity,
    **kwargs,
):
    return compare_opportunity_distinctness(
        left,
        right,
        left_capability_alignment=kwargs.pop(
            "left_capability_alignment",
            build_alignment(left),
        ),
        right_capability_alignment=kwargs.pop(
            "right_capability_alignment",
            build_alignment(right),
        ),
        left_scope_classification=kwargs.pop(
            "left_scope_classification",
            build_scope(left),
        ),
        right_scope_classification=kwargs.pop(
            "right_scope_classification",
            build_scope(right),
        ),
        **kwargs,
    )


class EngineeringOpportunityDistinctnessTests(unittest.TestCase):
    def test_pair_key_is_stable_and_order_independent(self) -> None:
        forward = build_opportunity_pair_key(
            "EO-2026-002",
            "EO-2026-001",
        )
        reverse = build_opportunity_pair_key(
            "EO-2026-001",
            "EO-2026-002",
        )

        self.assertEqual(forward, "EO-2026-001::EO-2026-002")
        self.assertEqual(forward, reverse)

    def test_self_comparison_is_rejected(self) -> None:
        entity = build_entity("EO-2026-001")

        with self.assertRaises(ValueError):
            compare(entity, entity)

    def test_portfolio_emits_each_unordered_pair_once(self) -> None:
        entities = (
            build_entity("EO-2026-001"),
            build_entity("EO-2026-002"),
            build_entity("EO-2026-003"),
        )
        portfolio = build_opportunity_distinctness_portfolio(
            entities,
            capability_alignments={
                entity.id: build_alignment(entity)
                for entity in entities
            },
            scope_classifications={
                entity.id: build_scope(entity)
                for entity in entities
            },
        )

        self.assertEqual(portfolio.comparison_count, 3)
        self.assertEqual(portfolio.skipped_pair_count, 0)
        self.assertEqual(
            len(
                {
                    comparison.pair_key
                    for comparison in portfolio.comparisons
                }
            ),
            3,
        )

    def test_duplicate_candidate_remains_pair_symmetric(self) -> None:
        left = build_entity(
            "EO-2026-001",
            title="Reliable context transport",
            summary="Build reliable context transport for engineering.",
            rationale="Prevent corruption during engineering delivery.",
        )
        right = build_entity(
            "EO-2026-002",
            title="Reliable context transport",
            summary="Build reliable context transport for engineering.",
            rationale="Prevent corruption during engineering delivery.",
        )

        forward = compare(left, right)
        reverse = compare(right, left)

        self.assertEqual(forward.analysis_state, "candidate")
        self.assertEqual(
            forward.relationship_type,
            "duplicate_of",
        )
        self.assertEqual(forward.pair_key, reverse.pair_key)
        self.assertIsNone(forward.source_opportunity_id)
        self.assertIsNone(forward.target_opportunity_id)

    def test_canonical_target_is_directional_recommendation(self) -> None:
        left = build_entity(
            "EO-2026-001",
            title="Reliable context transport",
            summary="Build reliable context transport for engineering.",
            rationale="Prevent corruption during engineering delivery.",
        )
        right = build_entity(
            "EO-2026-002",
            title="Reliable context transport",
            summary="Build reliable context transport for engineering.",
            rationale="Prevent corruption during engineering delivery.",
        )

        result = compare(
            left,
            right,
            canonical_target_candidate_id=left.id,
        )

        self.assertEqual(
            result.canonical_target_candidate_id,
            left.id,
        )
        self.assertIn(
            "provided explicitly",
            result.explanation,
        )
        self.assertEqual(
            result.recommendation.action,
            "review-duplicate-candidate",
        )

    def test_overlap_is_symmetric_and_does_not_merge(self) -> None:
        left = build_entity(
            "EO-2026-001",
            title="Task context compilation",
            summary=(
                "Build reusable context packages for scoped agent "
                "engineering tasks."
            ),
            rationale=(
                "Improve reliable agent execution with focused repository "
                "context and task boundaries."
            ),
        )
        right = build_entity(
            "EO-2026-002",
            title="Agent context package workflow",
            summary=(
                "Create reusable context packages for engineering agent "
                "tasks with bounded scope."
            ),
            rationale=(
                "Improve agent execution reliability through focused task "
                "context and repository boundaries."
            ),
        )

        result = compare(left, right)

        self.assertEqual(result.analysis_state, "candidate")
        self.assertEqual(
            result.relationship_type,
            "overlaps_with",
        )
        self.assertIsNone(result.source_opportunity_id)
        self.assertNotIn(
            "merge",
            result.recommendation.action,
        )

    def test_component_and_umbrella_are_directional_inverses(self) -> None:
        umbrella = build_entity(
            "EO-2026-001",
            title="AI collaboration intelligence platform",
            summary=(
                "Build an engineering collaboration intelligence platform "
                "system for reliable sessions and repository reasoning."
            ),
            rationale=(
                "The broad platform capability organizes multiple "
                "engineering collaboration improvements."
            ),
        )
        component = build_entity(
            "EO-2026-002",
            title="Engineering session intelligence assessment",
            summary=(
                "Build a session assessment for engineering collaboration "
                "intelligence and reliable sessions."
            ),
            rationale=(
                "The assessment improves one bounded part of the platform "
                "system."
            ),
            dependencies=(umbrella.id,),
        )

        result = compare(component, umbrella)

        self.assertEqual(result.analysis_state, "candidate")
        self.assertEqual(
            result.relationship_type,
            "component_of",
        )
        self.assertEqual(
            result.inverse_relationship_type,
            "umbrella_for",
        )
        self.assertEqual(
            result.source_opportunity_id,
            component.id,
        )
        self.assertEqual(
            result.target_opportunity_id,
            umbrella.id,
        )

    def test_same_capability_alone_cannot_establish_duplication(self) -> None:
        left = build_entity(
            "EO-2026-001",
            title="Session startup",
            summary="Improve deterministic startup checks.",
            rationale="Reduce bootstrap uncertainty.",
        )
        right = build_entity(
            "EO-2026-002",
            title="Artifact delivery",
            summary="Validate generated terminal artifacts.",
            rationale="Prevent copy corruption.",
        )

        result = compare(left, right)

        self.assertEqual(
            result.analysis_state,
            "insufficient-evidence",
        )
        self.assertNotEqual(
            result.relationship_type,
            "duplicate_of",
        )

    def test_different_capabilities_are_counterevidence_not_distinctness(self) -> None:
        left = build_entity(
            "EO-2026-001",
            title="Session startup",
            summary="Improve deterministic startup checks.",
            rationale="Reduce bootstrap uncertainty.",
        )
        right = build_entity(
            "EO-2026-002",
            title="Personal storage",
            summary="Improve reliable private storage.",
            rationale="Preserve personal data.",
            capability="Storage",
        )

        result = compare(
            left,
            right,
            right_capability_alignment=build_alignment(
                right,
                "storage",
            ),
        )

        self.assertEqual(
            result.analysis_state,
            "insufficient-evidence",
        )
        self.assertTrue(
            any(
                evidence.evidence_type
                == "capability-counterevidence"
                for evidence in result.counterevidence
            )
        )

    def test_same_scope_alone_cannot_establish_duplication(self) -> None:
        left = build_entity(
            "EO-2026-001",
            title="Session startup",
            summary="Improve deterministic startup checks.",
            rationale="Reduce bootstrap uncertainty.",
        )
        right = build_entity(
            "EO-2026-002",
            title="Artifact delivery",
            summary="Validate generated terminal artifacts.",
            rationale="Prevent copy corruption.",
        )
        result = compare(
            left,
            right,
            left_scope_classification=build_scope(
                left,
                "engineering-system-opportunity",
            ),
            right_scope_classification=build_scope(
                right,
                "engineering-system-opportunity",
            ),
        )

        self.assertEqual(
            result.analysis_state,
            "insufficient-evidence",
        )
        self.assertNotEqual(
            result.relationship_type,
            "duplicate_of",
        )

    def test_different_scopes_create_boundary_not_automatic_distinctness(self) -> None:
        left = build_entity(
            "EO-2026-001",
            title="Design context architecture",
            summary="Define repository context architecture.",
            rationale="Clarify durable system boundaries.",
        )
        right = build_entity(
            "EO-2026-002",
            title="Implement context script",
            summary="Build the bounded context generation script.",
            rationale="Deliver a working implementation.",
        )
        result = compare(
            left,
            right,
            left_scope_classification=build_scope(
                left,
                "architecture-opportunity",
            ),
            right_scope_classification=build_scope(
                right,
                "implementation-opportunity",
            ),
        )

        self.assertNotEqual(result.analysis_state, "resolved")
        self.assertTrue(
            any(
                evidence.evidence_type == "scope-boundary"
                for evidence in result.boundary_evidence
            )
        )

    def test_related_to_triggers_comparison_not_stronger_relationship(self) -> None:
        right = build_entity("EO-2026-002")
        left = build_entity(
            "EO-2026-001",
            related_opportunities=(right.id,),
        )

        result = compare(left, right)

        self.assertEqual(
            result.analysis_state,
            "insufficient-evidence",
        )
        self.assertTrue(
            any(
                evidence.relationship_type == "related_to"
                for evidence in result.supporting_evidence
            )
        )

    def test_dependency_provides_positive_boundary_evidence(self) -> None:
        right = build_entity(
            "EO-2026-002",
            title="Repository metadata",
            summary="Create stable repository metadata definitions.",
            rationale="Support deterministic document discovery.",
        )
        left = build_entity(
            "EO-2026-001",
            title="Travel meal planner",
            summary="Plan travel meals and grocery choices.",
            rationale="Improve nutrition while traveling.",
            dependencies=(right.id,),
        )

        result = compare(left, right)

        self.assertEqual(result.analysis_state, "candidate")
        self.assertEqual(
            result.relationship_type,
            "distinct_from",
        )
        self.assertTrue(
            any(
                evidence.evidence_type
                == "explicit-dependency-boundary"
                for evidence in result.boundary_evidence
            )
        )

    def test_shared_architecture_document_does_not_establish_duplication(self) -> None:
        reference = "docs/architecture/atlas.md"
        left = build_entity(
            "EO-2026-001",
            title="Session startup",
            summary="Improve deterministic startup checks.",
            rationale="Reduce bootstrap uncertainty.",
            related_documents=(reference,),
        )
        right = build_entity(
            "EO-2026-002",
            title="Artifact delivery",
            summary="Validate generated terminal artifacts.",
            rationale="Prevent copy corruption.",
            related_documents=(reference,),
        )

        result = compare(left, right)

        self.assertNotEqual(
            result.relationship_type,
            "duplicate_of",
        )
        self.assertTrue(
            any(
                evidence.evidence_type == "shared-document"
                for evidence in result.supporting_evidence
            )
        )

    def test_one_matching_keyword_produces_insufficient_evidence(self) -> None:
        left = build_entity(
            "EO-2026-001",
            title="Atlas startup",
            summary="Improve deterministic boot checks.",
            rationale="Reduce uncertainty.",
        )
        right = build_entity(
            "EO-2026-002",
            title="Atlas artifact transport",
            summary="Validate generated shell files.",
            rationale="Prevent corruption.",
        )

        result = compare(left, right)

        self.assertEqual(
            result.analysis_state,
            "insufficient-evidence",
        )

    def test_multi_field_similarity_produces_bounded_candidate(self) -> None:
        left = build_entity(
            "EO-2026-001",
            title="Task context compilation",
            summary=(
                "Build reusable context packages for scoped agent "
                "engineering tasks."
            ),
            rationale=(
                "Improve reliable agent execution with focused repository "
                "context and task boundaries."
            ),
        )
        right = build_entity(
            "EO-2026-002",
            title="Agent context package workflow",
            summary=(
                "Create reusable context packages for engineering agent "
                "tasks with bounded scope."
            ),
            rationale=(
                "Improve agent execution reliability through focused task "
                "context and repository boundaries."
            ),
        )

        result = compare(left, right)

        self.assertEqual(result.analysis_state, "candidate")
        self.assertEqual(result.confidence, "Medium")
        self.assertTrue(
            any(
                evidence.evidence_type
                == "text-token-overlap"
                for evidence in result.supporting_evidence
            )
        )

    def test_duplicate_overlap_uncertainty_is_ambiguous(self) -> None:
        left = build_entity(
            "EO-2026-001",
            title="Agent context workflow",
            summary=(
                "Build reusable context packages for scoped agent "
                "engineering tasks."
            ),
            rationale=(
                "Improve reliable execution with focused repository "
                "context and task boundaries."
            ),
        )
        right = build_entity(
            "EO-2026-002",
            title="Agent context workflow",
            summary=(
                "Create reusable context packages for engineering agent "
                "tasks with bounded scope."
            ),
            rationale=(
                "Improve execution reliability through focused task "
                "context and repository boundaries."
            ),
        )

        result = compare(left, right)

        self.assertEqual(result.analysis_state, "ambiguous")
        self.assertIn(
            "duplicate_of",
            result.alternative_relationship_types,
        )
        self.assertIn(
            "overlaps_with",
            result.alternative_relationship_types,
        )

    def test_human_review_can_resolve_duplicate_with_high_confidence(self) -> None:
        left = build_entity("EO-2026-001")
        right = build_entity("EO-2026-002")

        result = compare(
            left,
            right,
            human_reviewed_relationship_types=("duplicate_of",),
            canonical_target_candidate_id=left.id,
        )

        self.assertEqual(result.analysis_state, "resolved")
        self.assertEqual(result.relationship_type, "duplicate_of")
        self.assertEqual(result.confidence, "High")
        self.assertEqual(
            result.canonical_target_candidate_id,
            left.id,
        )

    def test_conflicting_human_review_is_exposed(self) -> None:
        left = build_entity("EO-2026-001")
        right = build_entity("EO-2026-002")

        result = compare(
            left,
            right,
            human_reviewed_relationship_types=(
                "duplicate_of",
                "distinct_from",
            ),
        )

        self.assertEqual(result.analysis_state, "conflicting")
        self.assertTrue(result.blockers)
        self.assertEqual(
            result.recommendation.action,
            "resolve-distinctness-conflict",
        )

    def test_canonical_target_may_remain_unset(self) -> None:
        left = build_entity(
            "EO-2026-001",
            title="Reliable context transport",
            summary="Build reliable context transport for engineering.",
            rationale="Prevent corruption during engineering delivery.",
        )
        right = build_entity(
            "EO-2026-002",
            title="Reliable context transport",
            summary="Build reliable context transport for engineering.",
            rationale="Prevent corruption during engineering delivery.",
        )

        result = compare(left, right)

        self.assertEqual(result.relationship_type, "duplicate_of")
        self.assertIsNone(
            result.canonical_target_candidate_id,
        )

    def test_skipped_pairs_expose_reason(self) -> None:
        left = build_entity(
            "EO-2026-001",
            title="Alpine nutrition",
            summary="Plan mountain meals.",
            rationale="Improve travel nutrition.",
        )
        right = build_entity(
            "EO-2026-002",
            title="Network observability",
            summary="Collect switch telemetry.",
            rationale="Detect infrastructure failures.",
        )
        portfolio = build_opportunity_distinctness_portfolio(
            (left, right),
            capability_alignments={
                left.id: build_alignment(left, "personal-services"),
                right.id: build_alignment(right, "observability"),
            },
            scope_classifications={
                left.id: build_scope(
                    left,
                    "personal-services",
                ),
                right.id: build_scope(
                    right,
                    "operational-infrastructure-opportunity",
                ),
            },
        )

        self.assertEqual(portfolio.comparison_count, 0)
        self.assertEqual(portfolio.skipped_pair_count, 1)
        self.assertTrue(portfolio.skipped_pairs[0].reason)

    def test_raw_objects_and_lifecycle_state_are_not_mutated(self) -> None:
        left = build_entity("EO-2026-001")
        right = build_entity("EO-2026-002")
        original_left = left
        original_right = right

        compare(
            left,
            right,
            human_reviewed_relationship_types=("duplicate_of",),
            canonical_target_candidate_id=left.id,
        )

        self.assertEqual(left, original_left)
        self.assertEqual(right, original_right)
        self.assertEqual(left.status, "captured")
        self.assertEqual(right.status, "captured")

    def test_assessments_consume_one_portfolio_comparison(self) -> None:
        left = build_entity(
            "EO-2026-001",
            title="Reliable context transport",
            summary="Build reliable context transport for engineering.",
            rationale="Prevent corruption during engineering delivery.",
        )
        right = build_entity(
            "EO-2026-002",
            title="Reliable context transport",
            summary="Build reliable context transport for engineering.",
            rationale="Prevent corruption during engineering delivery.",
        )

        assessments = assess_engineering_opportunities(
            (left, right)
        )

        self.assertEqual(
            len(assessments[0].distinctness_comparisons),
            1,
        )
        self.assertEqual(
            len(assessments[1].distinctness_comparisons),
            1,
        )
        self.assertIs(
            assessments[0].distinctness_comparisons[0],
            assessments[1].distinctness_comparisons[0],
        )
        self.assertEqual(
            assessments[0].distinctness_comparisons[0].pair_key,
            "EO-2026-001::EO-2026-002",
        )

    def test_assessment_integration_does_not_change_recommendation(self) -> None:
        left = build_entity(
            "EO-2026-001",
            title="Reliable context transport",
            summary="Build reliable context transport for engineering.",
            rationale="Prevent corruption during engineering delivery.",
        )
        right = build_entity(
            "EO-2026-002",
            title="Reliable context transport",
            summary="Build reliable context transport for engineering.",
            rationale="Prevent corruption during engineering delivery.",
        )

        assessments = assess_engineering_opportunities(
            (left, right)
        )

        self.assertEqual(
            assessments[0].recommendation.action,
            "retain-captured",
        )
        self.assertEqual(
            assessments[1].recommendation.action,
            "retain-captured",
        )


if __name__ == "__main__":
    unittest.main()
