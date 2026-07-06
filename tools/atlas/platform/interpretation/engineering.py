from dataclasses import dataclass

from atlas.platform.interpretation.milestone import interpret_milestone
from atlas.platform.interpretation.readiness import interpret_readiness
from atlas.platform.reasoning.models import EngineeringIntelligenceReport, GuidanceReport


@dataclass(frozen=True)
class EngineeringInterpretationReport:
    recommended_action: str
    reason: str
    milestone_recommendation: str


def build_engineering_interpretation(
    intelligence: EngineeringIntelligenceReport,
    guidance: GuidanceReport,
) -> EngineeringInterpretationReport:
    readiness = interpret_readiness(intelligence, guidance)
    milestone_recommendation = interpret_milestone(intelligence)

    return EngineeringInterpretationReport(
        recommended_action=readiness.recommended_action,
        reason=readiness.reason,
        milestone_recommendation=milestone_recommendation,
    )
