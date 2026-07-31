from atlas.platform.document_catalog import DocumentCatalog
from atlas.platform.engineering_state import EngineeringState
from atlas.platform.reasoning.guidance import build_guidance
from atlas.platform.reasoning.milestone import build_milestone_completion
from atlas.platform.reasoning.mission_advancement import build_mission_advancement
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
    mission_advancement = build_mission_advancement(validation, synchronization, milestone, state)

    validation_status = "Valid" if validation.valid else "Invalid"

    blockers: list[str] = []
    evidence: list[str] = []

    if not validation.valid:
        blockers.extend(finding.message for finding in validation.errors)

    if synchronization.errors:
        blockers.extend(finding.summary for finding in synchronization.errors)

    blockers.extend(state.state_blockers)

    evidence.extend(
        [
            f"Repository validation: {validation_status}",
            f"Repository synchronization: {synchronization.status}",
            f"Working tree clean: {'Yes' if state.repository_clean else 'No'}",
            f"Current phase: {state.mission_phase}",
            f"Phase lifecycle: {state.phase_lifecycle}",
            f"Work selection: {state.work_selection_status}",
            f"Selected checkpoint: {state.selected_checkpoint or 'None'}",
            f"Task authority: {state.task_authority}",
            f"Implementation authority: {state.implementation_authority}",
            f"Publication authority: {state.publication_authority}",
            f"Mission advancement: {mission_advancement.recommendation} ({mission_advancement.confidence} confidence)",
        ]
    )

    suggested_commands = (
        ["./atlas validate", "./atlas sync", "git status"]
        if blockers
        else ["./atlas bootstrap", "./atlas validate", "./atlas sync", "./atlas next"]
    )

    return EngineeringIntelligenceReport(
        validation_status=validation_status,
        milestone_status=milestone.status,
        milestone_confidence=milestone.confidence,
        milestone_satisfied_criteria=milestone.satisfied_criteria,
        milestone_unsatisfied_criteria=milestone.unsatisfied_criteria,
        milestone_next_actions=milestone.next_actions,
        mission_advancement_recommendation=mission_advancement.recommendation,
        mission_advancement_confidence=mission_advancement.confidence,
        mission_should_advance=mission_advancement.should_advance,
        synchronization_status=synchronization.status,
        repository_clean=state.repository_clean,
        current_phase=state.mission_phase,
        phase_lifecycle=state.phase_lifecycle,
        next_milestone=state.next_milestone,
        work_selection_status=state.work_selection_status,
        selected_checkpoint=state.selected_checkpoint,
        intentional_idle=state.intentional_idle,
        unknowns=list(state.state_unknowns),
        task_authority=state.task_authority,
        implementation_authority=state.implementation_authority,
        publication_authority=state.publication_authority,
        decision_required=state.decision_required,
        blockers=blockers,
        evidence=evidence,
        relevant_documents=guidance.relevant_documents,
        suggested_commands=suggested_commands,
    )
