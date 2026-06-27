from atlas.platform.engineering_state import EngineeringState, load


NAME = "next"
HELP = "Show the recommended next engineering action."


def register(subparsers):
    parser = subparsers.add_parser(NAME, help=HELP)
    parser.set_defaults(func=run)


def recommended_action(state: EngineeringState) -> str:
    if not state.repository_clean:
        return "Review and resolve current working tree changes before starting new work."

    if state.mission_phase == "Unknown":
        return "Restore or update docs/current-mission.md so Atlas can determine the active phase."

    if state.next_milestone == "Unknown":
        return "Define the next milestone in docs/current-mission.md."

    return state.next_milestone


def reason(state: EngineeringState) -> str:
    if not state.repository_clean:
        return "Atlas avoids recommending new work while the repository has uncommitted changes."

    if state.mission_phase == "Unknown" or state.next_milestone == "Unknown":
        return "Atlas depends on current mission documentation as the source of planning truth."

    return "Repository is clean and the current mission defines an active next milestone."


def run(args):
    state = load()

    print("Atlas Next")
    print("==========")
    print()

    print("Current Phase")
    print("-------------")
    print(state.mission_phase)
    print()

    print("Recommended Action")
    print("------------------")
    print(recommended_action(state))
    print()

    print("Reason")
    print("------")
    print(reason(state))
