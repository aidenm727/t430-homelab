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
    catalog = discovery.document_catalog()
    return EngineeringState(
        repository=str(platform.repo_root()),
        repository_clean=platform.repository_clean(),
        branch=platform.git_branch(),
        latest_commit=platform.latest_commit(),
        mission_phase=platform.mission_phase(),
        next_milestone=platform.next_milestone(),
        architecture_sources=catalog.paths_by_layer("Architecture"),
        infrastructure_sources=catalog.paths_by_layer("Infrastructure"),
        operations_sources=catalog.paths_by_layer("Operations"),
        roadmap_sources=catalog.paths_by_layer("Roadmaps"),
        current_context_sources=catalog.paths_by_layer("Current Context"),
    )
