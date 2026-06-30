from atlas.platform.discovery import document_catalog
from atlas.platform.engineering_state import EngineeringState, load
from atlas.platform.reasoning import analyze_impact


NAME = "next"
HELP = "Show the recommended next engineering action."


FOCUS_DOCUMENTS = [
    "docs/architecture/reasoning.md",
    "docs/architecture/atlas.md",
    "docs/architecture/repository.md",
    "docs/roadmaps/engineering-toolkit.md",
]


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

    return (
        "The current mission defines the next milestone, and Atlas can now use "
        "repository knowledge plus the reasoning layer to guide the next checkpoint."
    )


def print_list(title: str, values: list[str]) -> None:
    print(title)
    print("-" * len(title))

    if not values:
        print("- None")
        return

    for value in values:
        print(f"- {value}")


def related_reasoning_documents() -> list[str]:
    catalog = document_catalog()
    paths: list[str] = []

    for path in FOCUS_DOCUMENTS:
        document = catalog.find(path)
        if document is None:
            continue

        paths.append(document.path)

    return paths


def suggested_commands(state: EngineeringState) -> list[str]:
    if not state.repository_clean:
        return [
            "git status",
            "git diff",
            "python3 tools/atlas.py state",
        ]

    return [
        "python3 tools/atlas.py state",
        "python3 tools/atlas.py impact docs/architecture/reasoning.md",
        "python3 tools/atlas.py explain docs/architecture/reasoning.md",
    ]


def reasoning_summary() -> list[str]:
    catalog = document_catalog()
    reasoning_doc = catalog.find("docs/architecture/reasoning.md")

    if reasoning_doc is None:
        return [
            "Repository reasoning architecture is not documented yet.",
            "Create docs/architecture/reasoning.md before expanding reasoning commands.",
        ]

    report = analyze_impact(catalog, reasoning_doc)
    related_count = len(report.related_documents)
    generated_count = len(report.generated_outputs)

    return [
        "Repository reasoning architecture exists.",
        f"Atlas can inspect {related_count} directly related document(s).",
        f"Atlas can identify {generated_count} generated output(s) affected by reasoning architecture changes.",
    ]


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
    print()

    print_list("Reasoning Context", reasoning_summary())
    print()
    print_list("Relevant Documents", related_reasoning_documents())
    print()
    print_list("Suggested Commands", suggested_commands(state))
