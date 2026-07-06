from atlas.platform.document_catalog import DocumentCatalog
from atlas.platform.engineering_state import EngineeringState
from atlas.platform.repository import repo_root
from atlas.platform.reasoning.models import MilestoneCompletionReport


SYNCHRONIZATION_MILESTONE_TEXT = "Build Repository Synchronization Reasoning"
ENGINEERING_REVIEW_MILESTONE_TEXT = "Strengthen Engineering Review as the primary Atlas engineering checkpoint"


def _path_evidence(required_paths: list[str]) -> tuple[list[str], list[str]]:
    evidence: list[str] = []
    missing: list[str] = []

    for path in required_paths:
        if (repo_root() / path).exists():
            evidence.append(f"{path} exists.")
        else:
            missing.append(f"{path} is missing.")

    return evidence, missing


def build_milestone_completion(
    catalog: DocumentCatalog,
    state: EngineeringState,
) -> MilestoneCompletionReport:
    milestone = state.next_milestone

    if ENGINEERING_REVIEW_MILESTONE_TEXT in milestone:
        required_paths = [
            "docs/architecture/engineering-review.md",
            "docs/architecture/engineering-intelligence.md",
            "tools/atlas/platform/reasoning/review.py",
            "tools/atlas/platform/reasoning/intelligence.py",
            "tools/atlas/commands/review.py",
            "tools/atlas/commands/bootstrap.py",
        ]

        evidence, missing = _path_evidence(required_paths)

        if not missing:
            return MilestoneCompletionReport(
                status="In Progress",
                confidence="Medium",
                evidence=evidence,
                missing_evidence=missing,
                satisfied_criteria=[
                    "Engineering Review architecture exists.",
                    "Engineering Intelligence architecture exists.",
                    "Engineering Interpretation architecture exists.",
                    "Engineering Review reasoning implementation exists.",
                    "Engineering Intelligence composition exists.",
                    "Engineering Interpretation implementation exists.",
                    "Milestone reasoning produces structured criteria instead of recommendation text.",
                    "Review command exposes Engineering Review.",
                    "Bootstrap command consumes Engineering Review.",
                ],
                unsatisfied_criteria=[],
                next_actions=[
                    "Current milestone criteria are satisfied. Consider advancing docs/current-mission.md.",
                ],
            )

        return MilestoneCompletionReport(
            status="In Progress",
            confidence="Medium",
            evidence=evidence,
            missing_evidence=missing,
            satisfied_criteria=evidence,
            unsatisfied_criteria=missing,
            next_actions=[
                "Create the missing Engineering Review foundation files.",
            ],
        )

    if SYNCHRONIZATION_MILESTONE_TEXT in milestone:
        required_paths = [
            "docs/architecture/repository-synchronization.md",
            "tools/atlas/platform/reasoning/synchronization.py",
            "tools/atlas/commands/sync.py",
        ]

        evidence, missing = _path_evidence(required_paths)

        if not missing:
            return MilestoneCompletionReport(
                status="Complete",
                confidence="High",
                evidence=evidence,
                missing_evidence=missing,
                satisfied_criteria=evidence,
                unsatisfied_criteria=[],
                next_actions=[
                    "Consider advancing docs/current-mission.md.",
                ],
            )

        return MilestoneCompletionReport(
            status="In Progress",
            confidence="Medium",
            evidence=evidence,
            missing_evidence=missing,
            satisfied_criteria=evidence,
            unsatisfied_criteria=missing,
            next_actions=[
                "Continue implementing Repository Synchronization Reasoning before advancing the mission.",
            ],
        )

    return MilestoneCompletionReport(
        status="Unknown",
        confidence="Low",
        evidence=[f"Current milestone is not recognized by milestone reasoning: {milestone}"],
        missing_evidence=[],
        satisfied_criteria=[],
        unsatisfied_criteria=[
            "No milestone-specific reasoning rule matched the current mission milestone.",
        ],
        next_actions=[
            "Add a milestone reasoning rule for the current mission milestone.",
        ],
    )
