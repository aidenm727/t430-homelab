from dataclasses import dataclass

from atlas import platform
from atlas.platform import discovery


@dataclass(frozen=True)
class EngineeringState:
    repository: str
    repository_clean: bool
    branch: str
    latest_commit: str
    mission_phase: str
    next_milestone: str
    architecture_sources: list[str]
    infrastructure_sources: list[str]
    operations_sources: list[str]
    roadmap_sources: list[str]
    current_context_sources: list[str]


def load() -> EngineeringState:
    return EngineeringState(
        repository=str(platform.repo_root()),
        repository_clean=platform.repository_clean(),
        branch=platform.git_branch(),
        latest_commit=platform.latest_commit(),
        mission_phase=platform.mission_phase(),
        next_milestone=platform.next_milestone(),
        architecture_sources=discovery.architecture_documents(),
        infrastructure_sources=discovery.infrastructure_documents(),
        operations_sources=discovery.operations_documents(),
        roadmap_sources=discovery.roadmap_documents(),
        current_context_sources=discovery.current_context_documents(),
    )
