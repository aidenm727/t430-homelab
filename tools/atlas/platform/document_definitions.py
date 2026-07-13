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

    "docs/architecture/engineering-capabilities.md": DocumentDefinition(
        path="docs/architecture/engineering-capabilities.md",
        purpose="Defines reusable engineering capabilities as platform abilities exposed through Atlas and future interfaces.",
        capability="Engineering",
        tags=["engineering-capabilities", "atlas", "platform-engineering"],
        related=[
            "docs/architecture/engineering.md",
            "docs/architecture/atlas.md",
            "docs/architecture/reasoning.md",
            "docs/architecture/repository-object.md",
        ],
    ),

    "docs/architecture/engineering-review.md": DocumentDefinition(
        path="docs/architecture/engineering-review.md",
        purpose="Defines Engineering Review as the capability for composing validation, synchronization, state, and guidance into evidence-backed engineering recommendations.",
        capability="Engineering",
        tags=["engineering-review", "engineering-capabilities", "atlas"],
        related=[
            "docs/architecture/engineering-capabilities.md",
            "docs/architecture/repository-synchronization.md",
            "docs/architecture/reasoning.md",
            "docs/architecture/atlas.md",
        ],
    ),

    "docs/architecture/engineering-intelligence.md": DocumentDefinition(
        path="docs/architecture/engineering-intelligence.md",
        purpose="Defines Engineering Intelligence as the shared structured understanding consumed by Atlas, AI assistants, local agents, and future interfaces.",
        capability="Engineering",
        tags=["engineering-intelligence", "engineering-engine", "atlas"],
        related=[
            "docs/architecture/engineering-review.md",
            "docs/architecture/engineering-capabilities.md",
            "docs/architecture/reasoning.md",
            "docs/architecture/atlas.md",
        ],
    ),

    "docs/architecture/engineering-opportunity.md": DocumentDefinition(
        path="docs/architecture/engineering-opportunity.md",
        purpose="Defines Engineering Opportunity as the capability for preserving, evaluating, and prioritizing potential future engineering work.",
        capability="Engineering",
        tags=["engineering-opportunity", "engineering-intelligence", "atlas"],
        related=[
            "docs/architecture/engineering-intelligence.md",
            "docs/architecture/engineering-review.md",
            "docs/architecture/engineering-capabilities.md",
            "docs/architecture/atlas.md",
            "docs/current-mission.md",
        ],
    ),

    "docs/architecture/milestone-completion.md": DocumentDefinition(
        path="docs/architecture/milestone-completion.md",
        purpose="Defines milestone completion reasoning for determining whether the active engineering milestone appears complete based on repository evidence.",
        capability="Engineering",
        tags=["milestone-completion", "repository-reasoning", "engineering-review"],
        related=[
            "docs/architecture/engineering-review.md",
            "docs/architecture/reasoning.md",
            "docs/architecture/repository-synchronization.md",
            "docs/current-mission.md",
        ],
    ),

    "docs/architecture/mission-advancement.md": DocumentDefinition(
        path="docs/architecture/mission-advancement.md",
        purpose="Defines Mission Advancement as the capability for recommending whether the active engineering mission should advance based on Engineering Intelligence.",
        capability="Engineering",
        tags=["mission-advancement", "engineering-intelligence", "engineering-review"],
        related=[
            "docs/architecture/engineering-intelligence.md",
            "docs/architecture/milestone-completion.md",
            "docs/architecture/engineering-review.md",
            "docs/current-mission.md",
        ],
    ),

    "docs/architecture/engineering-lifecycle.md": DocumentDefinition(
        path="docs/architecture/engineering-lifecycle.md",
        purpose="Defines the Engineering Lifecycle for deliberate platform evolution from implementation through validation, synchronization, mission advancement, and context regeneration.",
        capability="Engineering",
        tags=["engineering-lifecycle", "engineering-process", "atlas"],
        related=[
            "docs/architecture/reasoning.md",
            "docs/architecture/engineering-intelligence.md",
            "docs/architecture/engineering-review.md",
            "docs/architecture/mission-advancement.md",
        ],
    ),

    "docs/architecture/architecture-registration.md": DocumentDefinition(
        path="docs/architecture/architecture-registration.md",
        purpose="Defines Architecture Registration for integrating new architecture documents into repository maps, metadata, validation, and Engineering Review.",
        capability="Engineering",
        tags=["architecture-registration", "repository-registration", "engineering-lifecycle"],
        related=[
            "docs/architecture/repository.md",
            "docs/architecture/engineering-lifecycle.md",
            "docs/architecture/engineering-intelligence.md",
            "docs/architecture/repository-object.md",
        ],
    ),

    "docs/architecture/capabilities.md": DocumentDefinition(
        path="docs/architecture/capabilities.md",
        purpose="Defines the platform capability map and capability-driven planning model.",
        capability="Platform",
        related=[
            "docs/architecture/platform.md",
            "docs/architecture/engineering.md",
            "docs/roadmaps/engineering-toolkit.md",
            "docs/architecture/engineering-opportunity-capability-alignment.md",
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

    "docs/architecture/repository-metadata.md": DocumentDefinition(
        path="docs/architecture/repository-metadata.md",
        purpose="Defines the architecture for repository-owned machine-readable metadata used by Atlas.",
        capability="Engineering",
        tags=["atlas", "repository-knowledge", "metadata"],
        related=[
            "docs/architecture/atlas.md",
            "docs/architecture/repository.md",
            "docs/standards/engineering-collaboration.md",
        ],
    ),
    "docs/standards/engineering-collaboration.md": DocumentDefinition(
        path="docs/standards/engineering-collaboration.md",
        purpose="Defines the standard for AI-assisted and human engineering collaboration on the Aiden Platform.",
        capability="Engineering",
        tags=["standards", "engineering-workflow", "collaboration"],
        related=[
            "docs/architecture/engineering.md",
            "docs/architecture/repository.md",
            "docs/architecture/repository-object.md",
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

    "docs/architecture/engineering-opportunity-object.md": DocumentDefinition(
        path="docs/architecture/engineering-opportunity-object.md",
        purpose="Defines the Engineering Opportunity Object as the repository-native representation of a potential engineering improvement throughout its lifecycle.",
        capability="Engineering",
        tags=[
            "engineering-opportunity-object",
            "repository-object",
            "engineering-opportunity",
        ],
        related=[
            "docs/architecture/engineering-opportunity.md",
            "docs/architecture/engineering-opportunity-intelligence.md",
            "docs/architecture/engineering-opportunity-assessment.md",
            "docs/architecture/engineering-intelligence.md",
            "docs/architecture/repository-object.md",
        ],
    ),

    "docs/architecture/engineering-opportunity-intelligence.md": DocumentDefinition(
        path="docs/architecture/engineering-opportunity-intelligence.md",
        purpose="Defines Engineering Opportunity Intelligence as the Repository Reasoning capability that evaluates Engineering Opportunity Objects and produces structured future engineering direction.",
        capability="Engineering",
        tags=[
            "engineering-opportunity-intelligence",
            "engineering-intelligence",
            "repository-reasoning",
        ],
        related=[
            "docs/architecture/engineering-opportunity.md",
            "docs/architecture/engineering-opportunity-object.md",
            "docs/architecture/engineering-opportunity-assessment.md",
            "docs/architecture/engineering-intelligence.md",
            "docs/architecture/reasoning.md",
            "docs/architecture/atlas.md",
        ],
    ),

    "docs/architecture/engineering-opportunity-assessment.md": DocumentDefinition(
        path="docs/architecture/engineering-opportunity-assessment.md",
        purpose="Defines the structured assessment contract used by Engineering Opportunity Intelligence to classify, relate, evaluate, prioritize, and recommend next actions for Engineering Opportunity Objects.",
        capability="Engineering",
        tags=[
            "engineering-opportunity-assessment",
            "engineering-opportunity-intelligence",
            "repository-reasoning",
            "structured-assessment",
        ],
        related=[
            "docs/architecture/engineering-opportunity.md",
            "docs/architecture/engineering-opportunity-object.md",
            "docs/architecture/engineering-opportunity-intelligence.md",
            "docs/architecture/engineering-intelligence.md",
            "docs/architecture/engineering-review.md",
            "docs/architecture/reasoning.md",
        ],
    ),

    "docs/architecture/engineering-opportunity-capability-alignment.md": DocumentDefinition(
        path="docs/architecture/engineering-opportunity-capability-alignment.md",
        purpose="Defines how Engineering Opportunity Intelligence resolves declared opportunity capability values against stable Platform Capability identities.",
        capability="Engineering",
        tags=[
            "engineering-opportunity-capability-alignment",
            "engineering-opportunity-intelligence",
            "platform-capabilities",
            "repository-reasoning",
        ],
        related=[
            "docs/architecture/capabilities.md",
            "docs/architecture/engineering-opportunity-object.md",
            "docs/architecture/engineering-opportunity-intelligence.md",
            "docs/architecture/engineering-opportunity-assessment.md",
            "docs/architecture/reasoning.md",
        ],
    ),

    "docs/architecture/artifact-transport.md": DocumentDefinition(
        path="docs/architecture/artifact-transport.md",
        purpose="Defines how implementation artifacts are safely transported from AI-assisted engineering into terminal and repository workflows.",
        capability="Engineering",
        tags=[
            "artifact-transport",
            "engineering-collaboration",
            "implementation-artifacts",
        ],
        related=[
            "docs/standards/engineering-collaboration.md",
            "docs/architecture/engineering-sessions.md",
            "docs/architecture/atlas.md",
            "docs/architecture/engineering-opportunity-object.md",
        ],
    ),


    "docs/architecture/implementation-artifacts.md": DocumentDefinition(
        path="docs/architecture/implementation-artifacts.md",
        purpose="Defines the lifecycle for generating, transporting, validating, and delivering implementation artifacts during engineering work.",
        capability="Engineering",
        tags=[
            "implementation-artifacts",
            "artifact-generation",
            "artifact-validation",
            "engineering-collaboration",
        ],
        related=[
            "docs/architecture/artifact-transport.md",
            "docs/standards/engineering-collaboration.md",
            "docs/architecture/engineering-sessions.md",
            "docs/architecture/atlas.md",
        ],
    ),


    "docs/architecture/repository-object.md": DocumentDefinition(
        path="docs/architecture/repository-object.md",
        purpose="Defines Repository Objects as structured repository-native engineering entities that Atlas can discover, validate, summarize, and reason about.",
        capability="Engineering",
        tags=[
            "repository-object",
            "repository-knowledge",
            "atlas",
            "structured-objects",
        ],
        related=[
            "docs/architecture/repository.md",
            "docs/architecture/atlas.md",
            "docs/architecture/reasoning.md",
            "docs/architecture/engineering-opportunity-object.md",
        ],
    ),

}


def definition_for(path: str) -> DocumentDefinition | None:
    return DOCUMENT_DEFINITIONS.get(path)
