from atlas.platform.document_catalog import DocumentCatalog
from atlas.platform.engineering_state import EngineeringState
from atlas.platform.reasoning.guidance import build_guidance
from atlas.platform.reasoning.milestone import build_milestone_completion
from atlas.platform.reasoning.models import EngineeringIntelligenceReport
from atlas.platform.reasoning.synchronization import analyze_synchronization
from atlas.platform.reasoning.validation import validate_repository


def build_engineering_intelligence(
    catalog: DocumentCatalog,
    state: EngineeringState,
) -> EngineeringIntelligenceReport:
    validation = validate_repository(catalog)
    synchronization = analyze_synchronization(catalog)
    guidance = build_guidance(catalog, state)
    milestone = build_milestone_completion(catalog, state)

    validation_status = "Valid" if validation.valid else "Invalid"

    blockers: list[str] = []
    evidence: list[str] = []

    if not validation.valid:
        blockers.extend(finding.message for finding in validation.errors)

    if synchronization.errors:
        blockers.extend(finding.summary for finding in synchronization.errors)

    if not state.repository_clean:
        blockers.append("Working tree has uncommitted changes.")

    evidence.extend(
        [
            f"Repository validation: {validation_status}",
            f"Repository synchronization: {synchronization.status}",
            f"Working tree clean: {'Yes' if state.repository_clean else 'No'}",
            f"Current phase: {state.mission_phase}",
            f"Next milestone: {state.next_milestone}",
            f"Milestone completion: {milestone.status} ({milestone.confidence} confidence)",
            f"Milestone recommendation: {milestone.recommendation}",
        ]
    )

    suggested_commands = (
        ["./atlas validate", "./atlas sync", "git status"]
        if blockers
        else ["./atlas validate", "./atlas sync", "./atlas state", "./atlas next"]
    )

    return EngineeringIntelligenceReport(
        validation_status=validation_status,
        milestone_status=milestone.status,
        milestone_confidence=milestone.confidence,
        milestone_recommendation=milestone.recommendation,
        synchronization_status=synchronization.status,
        repository_clean=state.repository_clean,
        current_phase=state.mission_phase,
        next_milestone=state.next_milestone,
        blockers=blockers,
        evidence=evidence,
        relevant_documents=guidance.relevant_documents,
        suggested_commands=suggested_commands,
    )
