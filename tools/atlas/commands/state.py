from atlas.platform.engineering_state import EngineeringState, load


NAME = "state"
HELP = "Show current engineering state."


def register(subparsers):
    parser = subparsers.add_parser(NAME, help=HELP)
    parser.set_defaults(func=run)


def readiness_message(state: EngineeringState) -> str:
    if not state.repository_clean:
        return "Working tree has changes. Review them before starting new work."

    if state.mission_phase == "Unknown":
        return "Mission could not be loaded. Check docs/current-mission.md."

    if state.next_milestone == "Unknown":
        return "Next milestone could not be loaded. Check docs/current-mission.md."

    return "Ready for engineering work."


def print_paths(paths: list[str]) -> None:
    if not paths:
        print("- None found")
        return

    for path in paths:
        print(f"- {path}")


def run(args):
    state = load()

    print("Atlas Engineering State")
    print("=======================")
    print()
    print(f"Repository: {state.repository}")
    print()

    print("Mission")
    print("-------")
    print(f"Phase: {state.mission_phase}")
    print(f"Next Milestone: {state.next_milestone}")
    print()

    print("Git")
    print("---")
    print(f"Branch: {state.branch}")
    print(f"Latest Commit: {state.latest_commit}")
    print(f"Working Tree: {'Clean' if state.repository_clean else 'Dirty'}")
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

    print("Engineering Readiness")
    print("---------------------")
    print(readiness_message(state))
