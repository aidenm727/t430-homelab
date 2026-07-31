from dataclasses import dataclass

from atlas.platform.document_catalog import DocumentCatalog
from atlas.platform.engineering_state import EngineeringState
from atlas.platform.reasoning.models import (
    EngineeringIntelligenceReport,
    GuidanceReport,
    ReadinessProjection,
)
from atlas.platform.reasoning.synchronization import SYNCHRONIZATION_SCOPE
from atlas.platform.reasoning.validation import VALIDATION_SCOPE


@dataclass(frozen=True)
class ReadinessInterpretation:
    recommended_action: str
    reason: str


def project_readiness(
    intelligence: EngineeringIntelligenceReport,
    guidance: GuidanceReport,
) -> ReadinessProjection:
    healthy = (
        intelligence.validation_status == "Valid"
        and intelligence.synchronization_status == "Synchronized"
        and not intelligence.blockers
    )

    if intelligence.blockers:
        recommended_action = (
            "Resolve the reported blockers only under explicit owner authority, "
            "then rerun Atlas validation and synchronization."
        )
        reason = (
            "Repository health or canonical state has blocking findings. Atlas "
            "reports them but does not grant authority to change them."
        )
    elif intelligence.intentional_idle:
        recommended_action = (
            "Remain intentionally idle until explicit owner instruction selects "
            "work and establishes any required task or implementation authority."
        )
        reason = (
            "Canonical active state intentionally selects no checkpoint. Atlas "
            "does not select work or establish authority."
        )
    else:
        recommended_action = guidance.recommended_action
        reason = guidance.reason

    return ReadinessProjection(
        repository_health=(
            "Healthy within declared scope"
            if healthy
            else "Needs attention within declared scope"
        ),
        validation_status=intelligence.validation_status,
        validation_scope=VALIDATION_SCOPE,
        synchronization_status=intelligence.synchronization_status,
        synchronization_scope=SYNCHRONIZATION_SCOPE,
        working_tree_observation=(
            "Clean" if intelligence.repository_clean else "Dirty"
        ),
        phase=intelligence.current_phase,
        phase_lifecycle=intelligence.phase_lifecycle,
        work_selection_state=intelligence.work_selection_status,
        selected_checkpoint=intelligence.selected_checkpoint,
        intentional_idle=intelligence.intentional_idle,
        blockers=tuple(intelligence.blockers),
        unknowns=tuple(intelligence.unknowns),
        task_authority=intelligence.task_authority,
        implementation_authority=intelligence.implementation_authority,
        publication_authority=intelligence.publication_authority,
        decision_required=intelligence.decision_required,
        recommended_action=recommended_action,
        reason=reason,
    )


def build_readiness_projection(
    catalog: DocumentCatalog,
    state: EngineeringState,
) -> ReadinessProjection:
    from atlas.platform.reasoning.guidance import build_guidance
    from atlas.platform.reasoning.intelligence import build_engineering_intelligence

    intelligence = build_engineering_intelligence(catalog, state)
    guidance = build_guidance(catalog, state)
    return project_readiness(intelligence, guidance)


def interpret_readiness(
    intelligence: EngineeringIntelligenceReport,
    guidance: GuidanceReport,
) -> ReadinessInterpretation:
    projection = project_readiness(intelligence, guidance)
    return ReadinessInterpretation(
        recommended_action=projection.recommended_action,
        reason=projection.reason,
    )
