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

    "docs/infrastructure.md": DocumentDefinition(
        path="docs/infrastructure.md",
        purpose="Canonical infrastructure record for deployed homelab hosts, services, networking, access, backups, and operations.",
        capability="Infrastructure",
        tags=["infrastructure", "t430-beast", "services", "backups", "networking"],
        related=[
            "docs/infrastructure-gamer-pve.md",
            "docs/services.md",
            "docs/infrastructure-snapshot.md",
        ],
    ),
    "docs/infrastructure-gamer-pve.md": DocumentDefinition(
        path="docs/infrastructure-gamer-pve.md",
        purpose="Infrastructure record for the gamer-pve Proxmox virtualization host and its workloads.",
        capability="Compute",
        tags=["infrastructure", "proxmox", "compute", "gamer-pve", "immich"],
        related=[
            "docs/infrastructure.md",
            "docs/architecture/compute.md",
            "docs/infrastructure-snapshot.md",
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

    "docs/change-session.md": DocumentDefinition(
        path="docs/change-session.md",
        purpose="Tracks the currently active engineering change session before it is finalized into permanent change records.",
        capability="Engineering Workflow",
        tags=["operations", "change-session", "workflow"],
        related=[
            "docs/change-schema.md",
            "docs/changes.log",
        ],
    ),
    "docs/change-schema.md": DocumentDefinition(
        path="docs/change-schema.md",
        purpose="Defines the structured schema used for homelab and platform change records.",
        capability="Engineering Workflow",
        tags=["operations", "change-management", "schema"],
        related=[
            "docs/change-session.md",
            "docs/changes.log",
        ],
    ),
    "docs/changes.log": DocumentDefinition(
        path="docs/changes.log",
        purpose="Human-readable operational history log for platform and homelab changes.",
        capability="Engineering Workflow",
        tags=["operations", "change-log", "history"],
        related=[
            "docs/change-session.md",
            "docs/change-schema.md",
            "docs/changes",
        ],
    ),
    "docs/roadmaps/ai-engineering.md": DocumentDefinition(
        path="docs/roadmaps/ai-engineering.md",
        purpose="Roadmap for future AI engineering capabilities and long-term intelligence workflows.",
        capability="Artificial Intelligence",
        tags=["roadmap", "ai", "future-work"],
        related=[
            "docs/architecture/ai.md",
            "docs/architecture/platform.md",
        ],
    ),
    "docs/roadmaps/engineering-toolkit.md": DocumentDefinition(
        path="docs/roadmaps/engineering-toolkit.md",
        purpose="Roadmap for Atlas and the Aiden engineering toolkit.",
        capability="Engineering",
        tags=["roadmap", "atlas", "engineering-toolkit"],
        related=[
            "docs/architecture/atlas.md",
            "docs/architecture/engineering.md",
            "docs/architecture/repository.md",
        ],
    ),

    "docs/architecture/reasoning.md": DocumentDefinition(
        path="docs/architecture/reasoning.md",
        purpose="Defines the repository reasoning layer that turns repository knowledge into engineering implications and guidance.",
        capability="Engineering",
        related=[
            "docs/architecture/atlas.md",
            "docs/architecture/repository.md",
            "docs/roadmaps/engineering-toolkit.md",
        ],
        tags=["atlas", "reasoning", "engineering"],
    ),

    "docs/architecture/repository-synchronization.md": DocumentDefinition(
        path="docs/architecture/repository-synchronization.md",
        purpose="Defines Repository Synchronization Reasoning as an Atlas reasoning capability for detecting drift across repository layers.",
        capability="Engineering",
        tags=["atlas", "repository-reasoning", "synchronization"],
        related=[
            "docs/architecture/atlas.md",
            "docs/architecture/repository.md",
            "docs/current-mission.md",
            "docs/aiden-context.md",
        ],
    ),

    "docs/architecture/engineering-sessions.md": DocumentDefinition(
        path="docs/architecture/engineering-sessions.md",
        purpose="Defines how engineering sessions begin, how startup context is established, and how Atlas should support deterministic session bootstrap.",
        capability="Engineering",
        tags=["atlas", "engineering-workflow", "session-bootstrap"],
        related=[
            "docs/architecture/engineering.md",
            "docs/architecture/atlas.md",
            "docs/architecture/repository.md",
            "docs/architecture/repository-synchronization.md",
            "docs/current-mission.md",
        ],
    ),
}


def definition_for(path: str) -> DocumentDefinition | None:
    return DOCUMENT_DEFINITIONS.get(path)
