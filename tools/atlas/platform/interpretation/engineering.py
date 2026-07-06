from dataclasses import dataclass

from atlas.platform.reasoning.models import EngineeringIntelligenceReport, GuidanceReport


@dataclass(frozen=True)
class EngineeringInterpretationReport:
    recommended_action: str
    reason: str


def build_engineering_interpretation(
    intelligence: EngineeringIntelligenceReport,
    guidance: GuidanceReport,
) -> EngineeringInterpretationReport:
    if intelligence.blockers:
        return EngineeringInterpretationReport(
            recommended_action="Resolve blocking repository issues before starting new engineering work.",
            reason="Engineering Interpretation prioritizes repository health before new implementation.",
        )

    if intelligence.mission_should_advance:
        return EngineeringInterpretationReport(
            recommended_action="Update docs/current-mission.md to define the next engineering milestone.",
            reason="Mission Advancement Reasoning found high-confidence evidence that the current mission should advance.",
        )

    return EngineeringInterpretationReport(
        recommended_action=guidance.recommended_action,
        reason=guidance.reason,
    )
