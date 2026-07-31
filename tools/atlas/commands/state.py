from atlas.platform.active_state import ActiveStateError
from atlas.platform.discovery import document_catalog
from atlas.platform.engineering_state import load
from atlas.platform.interpretation.readiness import build_readiness_projection
from atlas.platform.reasoning.models import ReadinessProjection


NAME = "state"
HELP = "Show current engineering state."


def register(subparsers):
    parser = subparsers.add_parser(NAME, help=HELP)
    parser.set_defaults(func=run)


def readiness_message(projection: ReadinessProjection) -> str:
    return projection.recommended_action


def print_paths(paths: list[str]) -> None:
    if not paths:
        print("- None found")
        return

    for path in paths:
        print(f"- {path}")


def run(args):
    try:
        state = load()
    except ActiveStateError as error:
        print("Atlas Engineering State")
        print("=======================")
        print()
        print("Canonical Active State")
        print("----------------------")
        print("Invalid — Atlas failed closed.")
        print(str(error))
        raise SystemExit(1) from error
    projection = build_readiness_projection(document_catalog(), state)

    print("Atlas Engineering State")
    print("=======================")
    print()
    print(f"Repository: {state.repository}")
    print()

    print("Canonical Active State")
    print("----------------------")
    print(f"Phase: {projection.phase}")
    print(f"Phase Lifecycle: {projection.phase_lifecycle}")
    print(f"Work Selection: {projection.work_selection_state}")
    print(f"Selected Checkpoint: {projection.selected_checkpoint or 'None'}")
    print(f"Intentional Idle: {'Yes' if projection.intentional_idle else 'No'}")
    print(f"Effective Date: {state.active_state.freshness.effective_date.isoformat()}")
    print(f"Decision Required: {projection.decision_required or 'None'}")
    print()

    print("Git")
    print("---")
    print(f"Branch: {state.branch}")
    print(f"Latest Commit: {state.latest_commit}")
    print(f"Working Tree: {projection.working_tree_observation}")
    print()

    print("Readiness Projection")
    print("--------------------")
    print(f"Repository Health: {projection.repository_health}")
    print(f"Validation: {projection.validation_status}")
    print(f"Synchronization: {projection.synchronization_status}")
    print()

    print("Validation Scope")
    print("----------------")
    print_paths(list(projection.validation_scope))
    print()

    print("Synchronization Scope")
    print("---------------------")
    print_paths(list(projection.synchronization_scope))
    print()

    print("External Authority")
    print("------------------")
    print(f"Task: {projection.task_authority}")
    print(f"Implementation: {projection.implementation_authority}")
    print(f"Publication: {projection.publication_authority}")
    print("Atlas Authority Conclusion: Not established")
    print()

    print("Blockers")
    print("--------")
    print_paths(list(projection.blockers))
    print()

    print("Unknowns")
    print("--------")
    print_paths(list(projection.unknowns))
    print()

    print("Architecture Sources")
    print("--------------------")
    print_paths(state.architecture_sources)
    print()

    print("Infrastructure Sources")
    print("----------------------")
    print_paths(state.infrastructure_sources)
    print()

    print("Operations Sources")
    print("------------------")
    print_paths(state.operations_sources)
    print()

    print("Roadmap Sources")
    print("---------------")
    print_paths(state.roadmap_sources)
    print()

    print("Current Context Sources")
    print("-----------------------")
    print_paths(state.current_context_sources)
    print()

    print("Engineering Readiness")
    print("---------------------")
    print(readiness_message(projection))
