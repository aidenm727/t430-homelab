from atlas import platform


NAME = "state"
HELP = "Show current engineering state."


def register(subparsers):
    parser = subparsers.add_parser(NAME, help=HELP)
    parser.set_defaults(func=run)


def readiness_message() -> str:
    if not platform.repository_clean():
        return "Working tree has changes. Review them before starting new work."

    if platform.mission_phase() == "Unknown":
        return "Mission could not be loaded. Check docs/current-mission.md."

    if platform.next_milestone() == "Unknown":
        return "Next milestone could not be loaded. Check docs/current-mission.md."

    return "Ready for engineering work."


def run(args):
    clean = platform.repository_clean()

    print("Atlas Engineering State")
    print("=======================")
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
    print(f"Working Tree: {'Clean' if clean else 'Dirty'}")
    print()

    print("Engineering Readiness")
    print("---------------------")
    print(readiness_message())