from atlas.platform.active_state import ActiveStateError
from atlas.platform.discovery import document_catalog
from atlas.platform.engineering_state import load
from atlas.platform.interpretation.readiness import build_readiness_projection
from atlas.platform.reasoning.models import ReadinessProjection


NAME = "next"
HELP = "Show the recommended next engineering action."


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


def print_guidance(report: ReadinessProjection) -> None:
    print("Atlas Next")
    print("==========")
    print()

    print("Current Phase")
    print("-------------")
    print(report.phase)
    print()

    print("Selected Work")
    print("-------------")
    print(f"Phase Lifecycle: {report.phase_lifecycle}")
    print(f"Work Selection: {report.work_selection_state}")
    print(f"Selected Checkpoint: {report.selected_checkpoint or 'None'}")
    print(f"Intentional Idle: {'Yes' if report.intentional_idle else 'No'}")
    print()

    print("Repository Observation")
    print("----------------------")
    print(f"Health: {report.repository_health}")
    print(f"Validation: {report.validation_status}")
    print(f"Synchronization: {report.synchronization_status}")
    print(f"Working Tree: {report.working_tree_observation}")
    print()

    print("External Authority")
    print("------------------")
    print(f"Task: {report.task_authority}")
    print(f"Implementation: {report.implementation_authority}")
    print(f"Publication: {report.publication_authority}")
    print("Atlas Authority Conclusion: Not established")
    print(f"Decision Required: {report.decision_required or 'None'}")
    print()

    print("Recommended Action")
    print("------------------")
    print(report.recommended_action)
    print()

    print("Reason")
    print("------")
    print(report.reason)
    print()

    print_list("Blockers", list(report.blockers))
    print()
    print_list("Unknowns", list(report.unknowns))
    print()
    print_list("Validation Scope", list(report.validation_scope))
    print()
    print_list("Synchronization Scope", list(report.synchronization_scope))


def run(args):
    catalog = document_catalog()
    try:
        state = load()
    except ActiveStateError as error:
        print("Atlas Next")
        print("==========")
        print()
        print("Canonical Active State")
        print("----------------------")
        print("Invalid — Atlas failed closed.")
        print(str(error))
        raise SystemExit(1) from error
    report = build_readiness_projection(catalog, state)

    print_guidance(report)
