from dataclasses import dataclass

from atlas.platform import docs
from atlas import platform


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


def load() -> EngineeringState:
    return EngineeringState(
        repository=str(platform.repo_root()),
        repository_clean=platform.repository_clean(),
        branch=platform.git_branch(),
        latest_commit=platform.latest_commit(),
        mission_phase=platform.mission_phase(),
        next_milestone=platform.next_milestone(),
        architecture_sources=docs.relative_paths(
            docs.architecture_sources()
        ),
        infrastructure_sources=docs.relative_paths(
            docs.infrastructure_sources()
        ),
        operations_sources=docs.relative_paths(
            docs.operations_sources()
        ),
    )