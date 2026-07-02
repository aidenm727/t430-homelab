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
    else:
        recommended_action = guidance.recommended_action
        reason = guidance.reason

    return EngineeringReviewReport(
        validation_status=intelligence.validation_status,
        synchronization_status=intelligence.synchronization_status,
        repository_clean=intelligence.repository_clean,
        current_phase=intelligence.current_phase,
        recommended_action=recommended_action,
        reason=reason,
        blockers=intelligence.blockers,
        evidence=intelligence.evidence,
        relevant_documents=intelligence.relevant_documents,
        suggested_commands=intelligence.suggested_commands,
    )
