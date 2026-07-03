from atlas.platform.document_catalog import DocumentCatalog
from atlas.platform.engineering_state import EngineeringState
from atlas.platform.reasoning.guidance import build_guidance
from atlas.platform.reasoning.intelligence import build_engineering_intelligence
from atlas.platform.reasoning.models import EngineeringReviewReport


def build_engineering_review(
    catalog: DocumentCatalog,
    state: EngineeringState,
) -> EngineeringReviewReport:
    intelligence = build_engineering_intelligence(catalog, state)
    guidance = build_guidance(catalog, state)

    if intelligence.blockers:
        recommended_action = "Resolve blocking repository issues before starting new engineering work."
        reason = "Engineering Review prioritizes repository health before new implementation."
    elif intelligence.mission_should_advance:
        recommended_action = "Update docs/current-mission.md to define the next engineering milestone."
        reason = "Mission Advancement Reasoning found high-confidence evidence that the current mission should advance."
    else:
        recommended_action = guidance.recommended_action
        reason = guidance.reason

    return EngineeringReviewReport(
        validation_status=intelligence.validation_status,
        synchronization_status=intelligence.synchronization_status,
        repository_clean=intelligence.repository_clean,
        current_phase=intelligence.current_phase,
        milestone_status=intelligence.milestone_status,
        milestone_confidence=intelligence.milestone_confidence,
        milestone_recommendation=intelligence.milestone_recommendation,
        milestone_satisfied_criteria=intelligence.milestone_satisfied_criteria,
        milestone_unsatisfied_criteria=intelligence.milestone_unsatisfied_criteria,
        milestone_next_actions=intelligence.milestone_next_actions,
        recommended_action=recommended_action,
        reason=reason,
        blockers=intelligence.blockers,
        evidence=intelligence.evidence,
        relevant_documents=intelligence.relevant_documents,
        suggested_commands=intelligence.suggested_commands,
    )
