from atlas.platform.engineering_state import EngineeringState
from atlas.platform.reasoning.models import (
    MilestoneCompletionReport,
    MissionAdvancementReport,
    SynchronizationReport,
    ValidationReport,
)


def build_mission_advancement(
    validation: ValidationReport,
    synchronization: SynchronizationReport,
    milestone: MilestoneCompletionReport,
    state: EngineeringState,
) -> MissionAdvancementReport:
    blockers: list[str] = []
    evidence: list[str] = []

    if not validation.valid:
        blockers.extend(finding.message for finding in validation.errors)

    if synchronization.errors:
        blockers.extend(finding.summary for finding in synchronization.errors)

    blockers.extend(state.state_blockers)

    evidence.extend(
        [
            f"Repository validation: {'Valid' if validation.valid else 'Invalid'}",
            f"Repository synchronization: {synchronization.status}",
            f"Working tree clean: {'Yes' if state.repository_clean else 'No'}",
            f"Milestone completion: {milestone.status} ({milestone.confidence} confidence)",
            f"Current phase: {state.mission_phase}",
            f"Current next milestone: {state.next_milestone}",
        ]
    )

    if blockers:
        return MissionAdvancementReport(
            recommendation="Do not advance the mission yet.",
            confidence="High",
            should_advance=False,
            reason="Repository health blockers must be resolved before mission advancement.",
            evidence=evidence,
            blockers=blockers,
            suggested_action="Resolve blockers, then run ./atlas review again.",
        )

    if state.intentional_idle:
        return MissionAdvancementReport(
            recommendation="Remain intentionally idle.",
            confidence="High",
            should_advance=False,
            reason=(
                "Canonical active state explicitly records intentional idle; "
                "Atlas does not select work."
            ),
            evidence=evidence,
            blockers=[],
            suggested_action=(
                "Wait for explicit owner instruction to select a checkpoint and "
                "separately establish any required authority."
            ),
        )

    if state.selected_checkpoint is not None:
        return MissionAdvancementReport(
            recommendation="Do not infer mission advancement.",
            confidence="High",
            should_advance=False,
            reason=(
                "Canonical active state selects work but does not establish "
                "completion, acceptance, or authority."
            ),
            evidence=evidence,
            blockers=[],
            suggested_action=(
                "Follow explicit owner authority for the selected checkpoint; "
                "obtain it when it has not been established externally."
            ),
        )

    if milestone.status == "Complete" and milestone.confidence == "High":
        return MissionAdvancementReport(
            recommendation="Advance the current mission.",
            confidence="High",
            should_advance=True,
            reason="Repository evidence indicates the active milestone is complete and the repository is healthy.",
            evidence=evidence,
            blockers=[],
            suggested_action="Update docs/current-mission.md to define the next engineering milestone.",
        )

    return MissionAdvancementReport(
        recommendation="Continue the current mission.",
        confidence="Medium",
        should_advance=False,
        reason="The active milestone is not complete with enough confidence to recommend mission advancement.",
        evidence=evidence,
        blockers=[],
        suggested_action=state.next_milestone,
    )
