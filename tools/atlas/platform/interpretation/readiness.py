from dataclasses import dataclass

from atlas.platform.reasoning.models import EngineeringIntelligenceReport, GuidanceReport


@dataclass(frozen=True)
class ReadinessInterpretation:
    recommended_action: str
    reason: str


def interpret_readiness(
    intelligence: EngineeringIntelligenceReport,
    guidance: GuidanceReport,
) -> ReadinessInterpretation:
    if intelligence.blockers:
        return ReadinessInterpretation(
            recommended_action="Resolve blocking repository issues before starting new engineering work.",
            reason="Engineering Interpretation prioritizes repository health before new implementation.",
        )

    if intelligence.mission_should_advance:
        return ReadinessInterpretation(
            recommended_action="Update docs/current-mission.md to define the next engineering milestone.",
            reason="Mission Advancement Reasoning found high-confidence evidence that the current mission should advance.",
        )

    return ReadinessInterpretation(
        recommended_action=guidance.recommended_action,
        reason=guidance.reason,
    )
