from atlas.platform.reasoning.models import EngineeringIntelligenceReport


def interpret_milestone(intelligence: EngineeringIntelligenceReport) -> str:
    if intelligence.milestone_status == "Not Applicable":
        return "Milestone completion is not applicable while intentionally idle."

    if intelligence.milestone_status == "Selected":
        return (
            "The checkpoint is selected; repository state and Atlas do not "
            "establish completion, acceptance, or authority."
        )

    if intelligence.milestone_status == "Complete":
        return "Current milestone appears complete. Consider advancing docs/current-mission.md."

    if intelligence.milestone_status == "Unknown":
        return "No milestone completion recommendation available."

    if intelligence.milestone_unsatisfied_criteria:
        return "Continue resolving unsatisfied milestone criteria before advancing the mission."

    if intelligence.milestone_next_actions:
        return "Continue the next milestone actions before advancing the mission."

    return "Continue the current milestone before advancing the mission."
