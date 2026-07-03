from atlas.platform.discovery import document_catalog
from atlas.platform.engineering_state import load
from atlas.platform.reasoning import build_guidance
from atlas.platform.reasoning.review import build_engineering_review


NAME = "bootstrap"
HELP = "Bootstrap a new engineering session with live repository state."


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
    review = build_engineering_review(catalog, state)
    guidance = build_guidance(catalog, state)

    print("Atlas Engineering Bootstrap")
    print("===========================")
    print()

    print("Purpose")
    print("-------")
    print("Use this output to establish live engineering state before entering Engineering Mode.")
    print()

    print("Session Readiness")
    print("-----------------")
    print(f"Health: {review.health}")
    print(f"Validation: {review.validation_status}")
    print(f"Synchronization: {review.synchronization_status}")
    print(f"Working Tree: {'Clean' if review.repository_clean else 'Dirty'}")
    print(f"Current Phase: {review.current_phase}")
    print()

    print("Mission")
    print("-------")
    print(f"Phase: {state.mission_phase}")
    print(f"Next Milestone: {state.next_milestone}")
    print()

    print("Recommended Action")
    print("------------------")
    print(review.recommended_action)
    print()

    print("Reason")
    print("------")
    print(review.reason)
    print()

    print("Milestone")
    print("---------")
    print(f"Status: {review.milestone_status}")
    print(f"Confidence: {review.milestone_confidence}")
    print(f"Recommendation: {review.milestone_recommendation}")
    print()
    print_list("Satisfied Criteria", review.milestone_satisfied_criteria)
    print()
    print_list("Unsatisfied Criteria", review.milestone_unsatisfied_criteria)
    print()
    print_list("Next Milestone Actions", review.milestone_next_actions)
    print()

    print_list("Blockers", review.blockers)
    print()
    print_list("Evidence", review.evidence)
    print()
    print_list(
        "Relevant Documents",
        [document.path for document in review.relevant_documents],
    )
    print()

    ready = not review.blockers

    print("Repository Understanding")
    print("------------------------")
    print("Provided by canonical repository documentation.")
    print()

    print("Live Engineering State")
    print("----------------------")
    print("INSPECTED")
    print()

    print("Engineering Mode")
    print("----------------")
    print("READY" if ready else "NOT READY")
    print()

    print("Engineering Mode Reason")
    print("-----------------------")
    if ready:
        print("Repository validation, synchronization, and live engineering state support implementation.")
    else:
        print(review.reason)
    print()

    print("ChatGPT Guidance")
    print("----------------")
    if ready:
        print("Engineering Mode has been established.")
        print("Proceed using the active engineering capability and current engineering checkpoint.")
    else:
        print("Engineering Mode has not been established.")
        print("Resolve the blockers above before proposing implementation.")
    print()

    print("Next Checkpoint")
    print("---------------")
    print(guidance.recommended_action)
    print()

    print_list("Suggested Commands", review.suggested_commands)
