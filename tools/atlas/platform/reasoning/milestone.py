from atlas.platform.document_catalog import DocumentCatalog
from atlas.platform.engineering_state import EngineeringState
from atlas.platform.repository import repo_root
from atlas.platform.reasoning.models import MilestoneCompletionReport


SYNCHRONIZATION_MILESTONE_TEXT = "Build Repository Synchronization Reasoning"
ENGINEERING_REVIEW_MILESTONE_TEXT = (
    "Strengthen Engineering Review as the primary Atlas engineering checkpoint"
)
OPPORTUNITY_INTELLIGENCE_MILESTONE_TEXT = (
    "Design Engineering Opportunity Intelligence"
)


def _path_evidence(required_paths: list[str]) -> tuple[list[str], list[str]]:
    evidence: list[str] = []
    missing: list[str] = []

    for path in required_paths:
        if (repo_root() / path).exists():
            evidence.append(f"{path} exists.")
        else:
            missing.append(f"{path} is missing.")

    return evidence, missing


def _document_design_evidence(
    catalog: DocumentCatalog,
    requirements: dict[str, dict[str, str]],
) -> tuple[list[str], list[str]]:
    evidence: list[str] = []
    missing: list[str] = []

    for path, required_markers in requirements.items():
        full_path = repo_root() / path

        if not full_path.exists():
            missing.append(f"{path} is missing.")
            continue

        evidence.append(f"{path} exists.")

        document = catalog.find(path)

        if document is None:
            missing.append(
                f"{path} is not discovered by Repository Knowledge."
            )
        elif not document.has_definition:
            missing.append(
                f"{path} is missing registered document metadata."
            )
        else:
            evidence.append(
                f"{path} is registered in document metadata."
            )

        document_content = full_path.read_text(encoding="utf-8")

        for marker, description in required_markers.items():
            if marker in document_content:
                evidence.append(f"{path}: {description}.")
            else:
                missing.append(
                    f"{path} is missing required design evidence: "
                    f"{description}."
                )

    return evidence, missing


def build_milestone_completion(
    catalog: DocumentCatalog,
    state: EngineeringState,
) -> MilestoneCompletionReport:
    milestone = state.next_milestone

    if OPPORTUNITY_INTELLIGENCE_MILESTONE_TEXT in milestone:
        requirements = {
            "docs/architecture/engineering-opportunity.md": {
                "## Opportunity Lifecycle":
                    "defines the opportunity lifecycle",
                "## Repository Ownership":
                    "defines repository ownership",
            },
            "docs/architecture/engineering-opportunity-object.md": {
                "## Required Fields":
                    "defines the repository object contract",
                "## Lifecycle":
                    "defines object lifecycle behavior",
                "## Relationship to Engineering Opportunity Intelligence":
                    "defines the object and reasoning boundary",
            },
            "docs/architecture/engineering-opportunity-intelligence.md": {
                "## Architectural Position":
                    "defines architectural placement",
                "## Relationship to Engineering Opportunity Assessment":
                    "defines the assessment boundary",
                "## Human Decision and Lifecycle Mutation":
                    "preserves human lifecycle authority",
                "## Initial Implementation Boundary":
                    "defines the initial implementation boundary",
            },
            "docs/architecture/engineering-opportunity-assessment.md": {
                "## Assessment Layers":
                    "separates facts, findings, and recommendations",
                "## Relationship Model":
                    "defines opportunity relationships",
                "## Determinism and Engineering Judgment":
                    "defines deterministic and judgment boundaries",
                "## Structured Assessment Contract":
                    "defines the structured assessment contract",
                "## Human Decision Boundary":
                    "preserves human decision authority",
                "## Initial Assessment Boundary":
                    "defines the initial assessment scope",
            },
        }

        evidence, missing = _document_design_evidence(
            catalog,
            requirements,
        )

        if not missing:
            return MilestoneCompletionReport(
                status="Complete",
                confidence="High",
                evidence=evidence,
                missing_evidence=[],
                satisfied_criteria=[
                    "Engineering Opportunity lifecycle and repository ownership are designed.",
                    "Engineering Opportunity Object structure and lifecycle are designed.",
                    "Engineering Opportunity Intelligence is positioned as Repository Reasoning.",
                    "Engineering Opportunity Assessment is separated from canonical objects.",
                    "Scope, relationships, evaluation, confidence, and recommendations are defined.",
                    "Deterministic reasoning is separated from heuristic and human judgment.",
                    "Lifecycle mutation remains human-authorized.",
                    "The initial implementation boundary is documented.",
                    "Required architecture documents are registered in repository metadata.",
                ],
                unsatisfied_criteria=[],
                next_actions=[
                    "Current milestone design criteria are satisfied. Advance docs/current-mission.md before beginning the next milestone.",
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
                "Complete the missing Engineering Opportunity Intelligence design evidence before advancing the mission.",
            ],
        )

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
                status="Complete",
                confidence="High",
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
        evidence=[
            f"Current milestone is not recognized by milestone reasoning: {milestone}"
        ],
        missing_evidence=[],
        satisfied_criteria=[],
        unsatisfied_criteria=[
            "No milestone-specific reasoning rule matched the current mission milestone.",
        ],
        next_actions=[
            "Add a milestone reasoning rule for the current mission milestone.",
        ],
    )
