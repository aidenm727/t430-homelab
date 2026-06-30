from atlas.platform.discovery import document_catalog
from atlas.platform.engineering_state import load
from atlas.platform.reasoning import GuidanceReport, build_guidance


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


def print_guidance(report: GuidanceReport) -> None:
    print("Atlas Next")
    print("==========")
    print()

    print("Current Phase")
    print("-------------")
    print(report.current_phase)
    print()

    print("Recommended Action")
    print("------------------")
    print(report.recommended_action)
    print()

    print("Reason")
    print("------")
    print(report.reason)
    print()

    print_list("Reasoning Context", report.reasoning_context)
    print()
    print_list(
        "Relevant Documents",
        [document.path for document in report.relevant_documents],
    )
    print()
    print_list("Suggested Commands", report.suggested_commands)


def run(args):
    catalog = document_catalog()
    state = load()
    report = build_guidance(catalog, state)

    print_guidance(report)
