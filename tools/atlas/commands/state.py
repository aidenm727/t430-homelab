from atlas import platform


NAME = "state"
HELP = "Show current engineering state."


def register(subparsers):
    parser = subparsers.add_parser(NAME, help=HELP)
    parser.set_defaults(func=run)


def run(args):
    mission = platform.mission_text()

    print("Atlas Engineering State")
    print()
    print(f"Repository: {platform.repo_root()}")
    print(f"Current mission: {platform.current_mission()}")
    print()
    print("Mission Preview")
    print("---------------")
    print(mission.splitlines()[2])
    print()
    print("Status: OK")