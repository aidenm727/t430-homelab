from atlas import platform


NAME = "state"
HELP = "Show current engineering state."


def register(subparsers):
    parser = subparsers.add_parser(NAME, help=HELP)
    parser.set_defaults(func=run)


def run(args):
    print("Atlas Engineering State")
    print()
    print(f"Repository: {platform.repo_root()}")
    print()
    print("Mission")
    print("-------")
    print(f"Phase: {platform.mission_phase()}")
    print(f"Next Milestone: {platform.next_milestone()}")
    print()
    print("Git")
    print("---")
    print(f"Branch: {platform.git_branch()}")
    print(f"Latest Commit: {platform.latest_commit()}")
    print(f"Clean: {'Yes' if platform.repository_clean() else 'No'}")
    print()
    print("Status: OK")