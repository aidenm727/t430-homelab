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
    state = load()
    report = build_engineering_review(catalog, state)

    print("Atlas Engineering Review")
    print("========================")
    print()

    print("Health")
    print("------")
    print(report.health)
    print()

    print("Status")
    print("------")
    print(f"Validation: {report.validation_status}")
    print(f"Synchronization: {report.synchronization_status}")
    print(f"Working Tree: {'Clean' if report.repository_clean else 'Dirty'}")
    print(f"Current Phase: {report.current_phase}")
    print()

    print("Milestone")
    print("---------")
    print(f"Status: {report.milestone_status}")
    print(f"Confidence: {report.milestone_confidence}")
    print(f"Recommendation: {report.milestone_recommendation}")
    print()

    print_list("Blockers", report.blockers)
    print()
    print_list("Evidence", report.evidence)
    print()

    print("Recommended Action")
    print("------------------")
    print(report.recommended_action)
    print()

    print("Reason")
    print("------")
    print(report.reason)
    print()

    print_list(
        "Relevant Documents",
        [document.path for document in report.relevant_documents],
    )
    print()
    print_list("Suggested Commands", report.suggested_commands)
