from dataclasses import dataclass

from atlas.platform.reasoning.models import EngineeringIntelligenceReport, GuidanceReport


@dataclass(frozen=True)
class EngineeringInterpretationReport:
    recommended_action: str
    reason: str
    milestone_recommendation: str


def _interpret_milestone(intelligence: EngineeringIntelligenceReport) -> str:
    if intelligence.milestone_status == "Complete":
        return "Current milestone appears complete. Consider advancing docs/current-mission.md."

    if intelligence.milestone_status == "Unknown":
        return "No milestone completion recommendation available."

    if intelligence.milestone_unsatisfied_criteria:
        return "Continue resolving unsatisfied milestone criteria before advancing the mission."

    if intelligence.milestone_next_actions:
        return "Continue the next milestone actions before advancing the mission."

    return "Continue the current milestone before advancing the mission."


def build_engineering_interpretation(
    intelligence: EngineeringIntelligenceReport,
    guidance: GuidanceReport,
) -> EngineeringInterpretationReport:
    milestone_recommendation = _interpret_milestone(intelligence)

    if intelligence.blockers:
        return EngineeringInterpretationReport(
            recommended_action="Resolve blocking repository issues before starting new engineering work.",
            reason="Engineering Interpretation prioritizes repository health before new implementation.",
            milestone_recommendation=milestone_recommendation,
        )

    if intelligence.mission_should_advance:
        return EngineeringInterpretationReport(
            recommended_action="Update docs/current-mission.md to define the next engineering milestone.",
            reason="Mission Advancement Reasoning found high-confidence evidence that the current mission should advance.",
            milestone_recommendation=milestone_recommendation,
        )

    return EngineeringInterpretationReport(
        recommended_action=guidance.recommended_action,
        reason=guidance.reason,
        milestone_recommendation=milestone_recommendation,
    )
