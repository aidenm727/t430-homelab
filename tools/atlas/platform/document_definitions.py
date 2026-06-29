from dataclasses import dataclass, field


@dataclass(frozen=True)
class DocumentDefinition:
    path: str
    purpose: str
    canonical: bool = True
    generated: bool = False
    capability: str | None = None
    status: str = "active"
    tags: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    generated_from: list[str] = field(default_factory=list)
    managed_by: str | None = None


DOCUMENT_DEFINITIONS = {
    "docs/architecture/platform.md": DocumentDefinition(
        path="docs/architecture/platform.md",
        purpose="Defines the long-term Aiden Platform architecture and vision.",
        capability="Platform",
        related=[
            "docs/architecture/capabilities.md",
            "docs/architecture/repository.md",
        ],
    ),
    "docs/architecture/atlas.md": DocumentDefinition(
        path="docs/architecture/atlas.md",
        purpose="Defines Atlas as the deterministic engineering interface for the Aiden Platform.",
        capability="Engineering",
        related=[
            "docs/architecture/engineering.md",
            "docs/architecture/repository.md",
            "docs/roadmaps/engineering-toolkit.md",
        ],
    ),
    "docs/current-mission.md": DocumentDefinition(
        path="docs/current-mission.md",
        purpose="Defines the current engineering phase, focus, priorities, and next milestone.",
        capability="Engineering",
        related=[
            "docs/aiden-context.md",
            "docs/architecture/atlas.md",
        ],
    ),
    "docs/aiden-context.md": DocumentDefinition(
        path="docs/aiden-context.md",
        purpose="Generated AI-readable context summary for assistant workflows.",
        canonical=False,
        generated=True,
        capability="AI Context",
        status="generated",
        tags=["ai-context", "generated-context", "engineering"],
        related=[
            "docs/current-mission.md",
            "docs/infrastructure-snapshot.md",
        ],
        generated_from=[
            "docs/current-mission.md",
            "docs/infrastructure-snapshot.md",
        ],
        managed_by="tools/generate-context.py",
    ),
    "docs/infrastructure-snapshot.md": DocumentDefinition(
        path="docs/infrastructure-snapshot.md",
        purpose="Generated infrastructure summary for AI context and quick reference.",
        canonical=False,
        generated=True,
        capability="Knowledge and Documentation",
        status="generated",
        tags=["infrastructure", "generated-context"],
        related=[
            "docs/infrastructure.md",
            "docs/infrastructure-gamer-pve.md",
            "docs/services.md",
        ],
        generated_from=[
            "docs/infrastructure.md",
            "docs/infrastructure-gamer-pve.md",
            "docs/services.md",
        ],
        managed_by="tools/generate-context.py",
    ),

    "docs/architecture/capabilities.md": DocumentDefinition(
        path="docs/architecture/capabilities.md",
        purpose="Defines the platform capability map and capability-driven planning model.",
        capability="Platform",
        related=[
            "docs/architecture/platform.md",
            "docs/architecture/engineering.md",
            "docs/roadmaps/engineering-toolkit.md",
        ],
    ),
    "docs/architecture/repository.md": DocumentDefinition(
        path="docs/architecture/repository.md",
        purpose="Defines how the repository is organized and how repository layers should evolve.",
        capability="Engineering",
        related=[
            "docs/architecture/atlas.md",
            "docs/docs-map.md",
            "docs/roadmaps/engineering-toolkit.md",
        ],
    ),

    "docs/architecture/engineering.md": DocumentDefinition(
        path="docs/architecture/engineering.md",
        purpose="Defines the engineering methodology and workflow used to evolve the Aiden Platform.",
        capability="Engineering",
        related=[
            "docs/architecture/platform.md",
            "docs/architecture/atlas.md",
            "docs/architecture/repository.md",
        ],
    ),
    "docs/architecture/engineering-environment.md": DocumentDefinition(
        path="docs/architecture/engineering-environment.md",
        purpose="Defines the engineering environment, tooling, and development workflow.",
        capability="Engineering",
        related=[
            "docs/architecture/engineering.md",
            "docs/architecture/repository.md",
        ],
    ),
    "docs/architecture/compute.md": DocumentDefinition(
        path="docs/architecture/compute.md",
        purpose="Defines the platform's compute architecture and the roles of compute resources.",
        capability="Compute",
        related=[
            "docs/architecture/platform.md",
            "docs/infrastructure.md",
            "docs/infrastructure-gamer-pve.md",
        ],
    ),
    "docs/architecture/ai.md": DocumentDefinition(
        path="docs/architecture/ai.md",
        purpose="Defines the AI architecture and long-term direction for intelligence capabilities across the platform.",
        capability="Artificial Intelligence",
        related=[
            "docs/architecture/platform.md",
            "docs/architecture/atlas.md",
            "docs/roadmaps/ai-engineering.md",
        ],
    ),

    "docs/services.md": DocumentDefinition(
        path="docs/services.md",
        purpose="Describes the deployed homelab services and their operational details.",
        capability="Personal Services",
        related=[
            "docs/infrastructure.md",
            "docs/infrastructure-snapshot.md",
        ],
    ),
}


def definition_for(path: str) -> DocumentDefinition | None:
    return DOCUMENT_DEFINITIONS.get(path)
