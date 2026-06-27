from atlas import platform


NAME = "next"
HELP = "Show the recommended next engineering action."


def register(subparsers):
    parser = subparsers.add_parser(NAME, help=HELP)
    parser.set_defaults(func=run)


def recommended_action() -> str:
    if not platform.repository_clean():
        return "Review and resolve current working tree changes before starting new work."

    if platform.mission_phase() == "Unknown":
        return "Restore or update docs/current-mission.md so Atlas can determine the active phase."

    if platform.next_milestone() == "Unknown":
        return "Define the next milestone in docs/current-mission.md."

    return platform.next_milestone()


def reason() -> str:
    if not platform.repository_clean():
        return "Atlas avoids recommending new work while the repository has uncommitted changes."

    if platform.mission_phase() == "Unknown" or platform.next_milestone() == "Unknown":
        return "Atlas depends on current mission documentation as the source of planning truth."

    return "Repository is clean and the current mission defines an active next milestone."


def run(args):
    print("Atlas Next")
    print("==========")
    print()

    print("Current Phase")
    print("-------------")
    print(platform.mission_phase())
    print()

    print("Recommended Action")
    print("------------------")
    print(recommended_action())
    print()

    print("Reason")
    print("------")
    print(reason())
