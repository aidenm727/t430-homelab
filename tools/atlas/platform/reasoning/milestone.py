from atlas.platform.document_catalog import DocumentCatalog
from atlas.platform.engineering_state import EngineeringState
from atlas.platform.repository import repo_root
from atlas.platform.reasoning.models import MilestoneCompletionReport


SYNCHRONIZATION_MILESTONE_TEXT = "Build Repository Synchronization Reasoning"


def build_milestone_completion(
    catalog: DocumentCatalog,
    state: EngineeringState,
) -> MilestoneCompletionReport:
    milestone = state.next_milestone

    evidence: list[str] = []
    missing: list[str] = []

    if SYNCHRONIZATION_MILESTONE_TEXT not in milestone:
        return MilestoneCompletionReport(
            status="Unknown",
            confidence="Low",
            evidence=[f"Current milestone is not recognized by this initial reasoning rule: {milestone}"],
            missing_evidence=[],
            recommendation="No milestone completion recommendation available.",
        )

    required_paths = [
        "docs/architecture/repository-synchronization.md",
        "tools/atlas/platform/reasoning/synchronization.py",
        "tools/atlas/commands/sync.py",
    ]

    for path in required_paths:
        if (repo_root() / path).exists():
            evidence.append(f"{path} exists.")
        else:
            missing.append(f"{path} is missing.")

    if not missing:
        return MilestoneCompletionReport(
            status="Complete",
            confidence="High",
            evidence=evidence,
            missing_evidence=missing,
            recommendation="Current milestone appears complete. Consider advancing docs/current-mission.md.",
        )

    return MilestoneCompletionReport(
        status="In Progress",
        confidence="Medium",
        evidence=evidence,
        missing_evidence=missing,
        recommendation="Continue implementing Repository Synchronization Reasoning before advancing the mission.",
    )
