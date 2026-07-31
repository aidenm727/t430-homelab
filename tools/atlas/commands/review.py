from atlas.platform.active_state import ActiveStateError
from atlas.platform.discovery import document_catalog
from atlas.platform.engineering_state import load
from atlas.platform.reasoning.review import build_engineering_review


NAME = "review"
HELP = "Review engineering engine state and recommend the next investment."


def register(subparsers):
    parser = subparsers.add_parser(NAME, help=HELP)
    parser.set_defaults(func=run)


def print_list(title: str, values: list[str]) -> None:
    print(title)
    print("-" * len(title))

    if not values:
        print("- None")
        return

    for value in values:
        print(f"- {value}")


def run(args):
    catalog = document_catalog()
    try:
        state = load()
    except ActiveStateError as error:
        print("Atlas Engineering Review")
        print("========================")
        print()
        print("Canonical Active State")
        print("----------------------")
        print("Invalid — Atlas failed closed.")
        print(str(error))
        raise SystemExit(1) from error
    report = build_engineering_review(catalog, state)
    readiness = report.readiness

    print("Atlas Engineering Review")
    print("========================")
    print()

    print("Health")
    print("------")
    print(readiness.repository_health)
    print()

    print("Status")
    print("------")
    print(f"Validation: {readiness.validation_status}")
    print(f"Synchronization: {readiness.synchronization_status}")
    print(f"Working Tree: {readiness.working_tree_observation}")
    print(f"Current Phase: {readiness.phase}")
    print(f"Phase Lifecycle: {readiness.phase_lifecycle}")
    print(f"Work Selection: {readiness.work_selection_state}")
    print(f"Selected Checkpoint: {readiness.selected_checkpoint or 'None'}")
    print(f"Intentional Idle: {'Yes' if readiness.intentional_idle else 'No'}")
    print()

    print_list("Validation Scope", list(readiness.validation_scope))
    print()
    print_list("Synchronization Scope", list(readiness.synchronization_scope))
    print()

    print("External Authority")
    print("------------------")
    print(f"Task: {readiness.task_authority}")
    print(f"Implementation: {readiness.implementation_authority}")
    print(f"Publication: {readiness.publication_authority}")
    print("Atlas Authority Conclusion: Not established")
    print(f"Decision Required: {readiness.decision_required or 'None'}")
    print()

    print("Milestone")
    print("---------")
    print(f"Status: {report.milestone_status}")
    print(f"Confidence: {report.milestone_confidence}")
    print(f"Recommendation: {report.milestone_recommendation}")
    print()
    print_list("Satisfied Criteria", report.milestone_satisfied_criteria)
    print()
    print_list("Unsatisfied Criteria", report.milestone_unsatisfied_criteria)
    print()
    print_list("Next Milestone Actions", report.milestone_next_actions)
    print()

    print_list("Blockers", list(readiness.blockers))
    print()
    print_list("Unknowns", list(readiness.unknowns))
    print()
    print_list("Evidence", report.evidence)
    print()

    print("Recommended Action")
    print("------------------")
    print(readiness.recommended_action)
    print()

    print("Reason")
    print("------")
    print(readiness.reason)
    print()

    print_list(
        "Relevant Documents",
        [document.path for document in report.relevant_documents],
    )
    print()
    print_list("Suggested Commands", report.suggested_commands)
