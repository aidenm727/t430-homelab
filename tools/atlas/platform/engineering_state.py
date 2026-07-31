from dataclasses import dataclass

from atlas import platform
from atlas.platform.active_state import ActiveState, load_active_state
from atlas.platform import discovery


@dataclass(frozen=True)
class EngineeringState:
    repository: str
    repository_clean: bool
    branch: str
    latest_commit: str
    active_state: ActiveState
    mission_phase: str
    phase_lifecycle: str
    next_milestone: str
    work_selection_status: str
    selected_checkpoint: str | None
    intentional_idle: bool
    state_blockers: tuple[str, ...]
    state_unknowns: tuple[str, ...]
    decision_required: str | None
    task_authority: str
    implementation_authority: str
    publication_authority: str
    architecture_sources: list[str]
    infrastructure_sources: list[str]
    operations_sources: list[str]
    roadmap_sources: list[str]
    current_context_sources: list[str]


def load() -> EngineeringState:
    catalog = discovery.document_catalog()
    active_state = load_active_state()
    checkpoint = active_state.work_selection.selected_checkpoint
    return EngineeringState(
        repository=str(platform.repo_root()),
        repository_clean=platform.repository_clean(),
        branch=platform.git_branch(),
        latest_commit=platform.latest_commit(),
        active_state=active_state,
        mission_phase=active_state.phase.display_name,
        phase_lifecycle=active_state.phase.lifecycle,
        next_milestone=(
            checkpoint.name
            if checkpoint is not None
            else "Intentional idle — no engineering checkpoint is selected."
        ),
        work_selection_status=active_state.work_selection.status,
        selected_checkpoint=checkpoint.name if checkpoint is not None else None,
        intentional_idle=active_state.work_selection.intentional_idle,
        state_blockers=tuple(
            blocker.summary for blocker in active_state.blockers
        ),
        state_unknowns=tuple(
            unknown.summary for unknown in active_state.unknowns
        ),
        decision_required=(
            active_state.decision_required.summary
            if active_state.decision_required is not None
            else None
        ),
        task_authority=active_state.authority.task,
        implementation_authority=active_state.authority.implementation,
        publication_authority=active_state.authority.publication,
        architecture_sources=catalog.paths_by_layer("Architecture"),
        infrastructure_sources=catalog.paths_by_layer("Infrastructure"),
        operations_sources=catalog.paths_by_layer("Operations"),
        roadmap_sources=catalog.paths_by_layer("Roadmaps"),
        current_context_sources=[
            "docs/current-state.json",
            *catalog.paths_by_layer("Current Context"),
        ],
    )
