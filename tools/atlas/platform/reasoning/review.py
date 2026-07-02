from atlas.platform.document_catalog import DocumentCatalog
from atlas.platform.engineering_state import EngineeringState
from atlas.platform.reasoning.guidance import build_guidance
from atlas.platform.reasoning.models import EngineeringReviewReport
from atlas.platform.reasoning.synchronization import analyze_synchronization
from atlas.platform.reasoning.validation import validate_repository


def build_engineering_review(
    catalog: DocumentCatalog,
    state: EngineeringState,
) -> EngineeringReviewReport:
    validation = validate_repository(catalog)
    synchronization = analyze_synchronization(catalog)
    guidance = build_guidance(catalog, state)

    blockers: list[str] = []
    evidence: list[str] = []

    validation_status = "Valid" if validation.valid else "Invalid"

    if not validation.valid:
        blockers.extend(finding.message for finding in validation.errors)

    if synchronization.errors:
        blockers.extend(finding.summary for finding in synchronization.errors)

    if not state.repository_clean:
        blockers.append("Working tree has uncommitted changes.")

    evidence.append(f"Repository validation: {validation_status}")
    evidence.append(f"Repository synchronization: {synchronization.status}")
    evidence.append(f"Working tree clean: {'Yes' if state.repository_clean else 'No'}")
    evidence.append(f"Current phase: {state.mission_phase}")
    evidence.append(f"Next milestone: {state.next_milestone}")

    if blockers:
        recommended_action = "Resolve blocking repository issues before starting new engineering work."
        reason = "Engineering Review prioritizes repository health before new implementation."
        suggested_commands = [
            "./atlas validate",
            "./atlas sync",
            "git status",
        ]
    else:
        recommended_action = guidance.recommended_action
        reason = guidance.reason
        suggested_commands = [
            "./atlas validate",
            "./atlas sync",
            "./atlas state",
            "./atlas next",
        ]

    return EngineeringReviewReport(
        validation_status=validation_status,
        synchronization_status=synchronization.status,
        repository_clean=state.repository_clean,
        current_phase=state.mission_phase,
        recommended_action=recommended_action,
        reason=reason,
        blockers=blockers,
        evidence=evidence,
        relevant_documents=guidance.relevant_documents,
        suggested_commands=suggested_commands,
    )
