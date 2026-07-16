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
    "docs/vision.md": DocumentDefinition(
        path="docs/vision.md",
        purpose="Defines why the Aiden Platform exists, its North Star, principles, human authority, non-goals, and long-term direction.",
        capability="Platform Direction and Governance",
        tags=["vision", "platform-governance", "human-agency"],
        related=[
            "docs/architecture/platform.md",
            "docs/architecture/capabilities.md",
            "docs/roadmaps/platform-strategy.md",
            "docs/current-mission.md",
        ],
    ),
    "docs/architecture/platform.md": DocumentDefinition(
        path="docs/architecture/platform.md",
        purpose="Defines the structural architecture of the Aiden Platform, including Platform Foundations, Human Agency Domains, and major system boundaries.",
        capability="Platform Direction and Governance",
        tags=["platform-architecture", "capability-architecture", "human-agency"],
        related=[
            "docs/vision.md",
            "docs/architecture/capabilities.md",
            "docs/architecture/ai.md",
            "docs/architecture/repository.md",
            "docs/architecture/atlas.md",
            "docs/roadmaps/platform-strategy.md",
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
        purpose="Defines the current engineering phase, bounded scope, priorities, non-priorities, success criteria, and next milestone.",
        capability="Engineering and Evolution",
        tags=["current-mission", "engineering-state", "active-work"],
        related=[
            "docs/vision.md",
            "docs/architecture/platform.md",
            "docs/roadmaps/platform-strategy.md",
            "docs/aiden-context.md",
            "docs/architecture/atlas.md",
            "docs/architecture/repository-synchronization.md",
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
        purpose="Defines the layered Platform Foundation and Human Agency Domain taxonomy, stable identities, maturity model, and legacy compatibility strategy.",
        capability="Platform Direction and Governance",
        tags=["platform-capabilities", "capability-taxonomy", "capability-maturity"],
        related=[
            "docs/vision.md",
            "docs/architecture/platform.md",
            "docs/architecture/ai.md",
            "docs/architecture/engineering.md",
            "docs/roadmaps/platform-strategy.md",
            "docs/architecture/engineering-opportunity-capability-alignment.md",
        ],
    ),
    "docs/architecture/repository.md": DocumentDefinition(
        path="docs/architecture/repository.md",
        purpose="Defines repository layers, canonical ownership, source-of-truth order, placement rules, registration, and repository health.",
        capability="Engineering and Evolution",
        tags=["repository-architecture", "canonical-ownership", "source-of-truth"],
        related=[
            "docs/vision.md",
            "docs/architecture/platform.md",
            "docs/architecture/atlas.md",
            "docs/docs-map.md",
            "docs/roadmaps/platform-strategy.md",
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
        purpose="Defines Artificial Intelligence and Personal AI architecture, data sensitivity, provider strategy, context authority, action boundaries, and evaluation.",
        capability="Artificial Intelligence",
        tags=["artificial-intelligence", "personal-ai", "ai-governance"],
        related=[
            "docs/vision.md",
            "docs/architecture/platform.md",
            "docs/architecture/capabilities.md",
            "docs/architecture/atlas.md",
            "docs/roadmaps/platform-strategy.md",
            "docs/roadmaps/ai-engineering.md",
            "docs/architecture/ai-operating-model.md",
            "docs/architecture/knowledge-authority.md",
        ],
    ),

    "docs/architecture/ai-operating-model.md": DocumentDefinition(
        path="docs/architecture/ai-operating-model.md",
        purpose="Defines task-based provider and model selection, hosted/local/hybrid assignment, data-sensitivity operating rules, evaluation evidence, fallback behavior, and approval boundaries.",
        capability="Artificial Intelligence",
        tags=[
            "artificial-intelligence",
            "ai-operating-model",
            "provider-evaluation",
            "model-selection",
            "data-sensitivity",
        ],
        related=[
            "docs/architecture/ai.md",
            "docs/architecture/knowledge-authority.md",
            "docs/architecture/capabilities.md",
            "docs/vision.md",
            "docs/roadmaps/platform-strategy.md",
            "docs/current-mission.md",
        ],
    ),
    "docs/architecture/knowledge-authority.md": DocumentDefinition(
        path="docs/architecture/knowledge-authority.md",
        purpose="Defines knowledge authority classes, provenance, canonical ownership, conflict handling, and the human-reviewed Canonical Knowledge Promotion Workflow.",
        capability="Knowledge and Context",
        tags=[
            "knowledge-context",
            "knowledge-authority",
            "provenance",
            "canonical-knowledge",
            "knowledge-promotion",
        ],
        related=[
            "docs/architecture/repository.md",
            "docs/architecture/ai.md",
            "docs/architecture/ai-operating-model.md",
            "docs/architecture/capabilities.md",
            "docs/architecture/repository-object.md",
            "docs/current-mission.md",
        ],
    ),

    "docs/architecture/task-scoped-agent-context-compilation.md": DocumentDefinition(
        path="docs/architecture/task-scoped-agent-context-compilation.md",
        purpose="Defines deterministic, repository-owned compilation of reproducible task-specific context packages for replaceable AI consumers.",
        canonical=True,
        generated=False,
        capability="Knowledge and Context",
        tags=[
            "architecture",
            "knowledge-and-context",
            "context-selection",
            "task-context",
            "provenance",
            "reproducibility",
            "consumer-contract",
        ],
        related=[
            "docs/architecture/platform.md",
            "docs/architecture/repository.md",
            "docs/architecture/atlas.md",
            "docs/architecture/reasoning.md",
            "docs/architecture/repository-metadata.md",
            "docs/architecture/knowledge-authority.md",
            "docs/architecture/engineering-sessions.md",
            "docs/standards/engineering-collaboration.md",
            "docs/current-mission.md",
            "docs/opportunities/reviewed/EO-2026-013-task-scoped-agent-context-compilation.yaml",
        ],
    ),

    "docs/task-context/index.md": DocumentDefinition(
        path="docs/task-context/index.md",
        purpose="Owns the identity, inventory, stewardship, loading contract, and checkpoint boundary for repository-owned task-context schemas and policies.",
        canonical=True,
        generated=False,
        capability="Knowledge and Context",
        tags=[
            "knowledge-and-context",
            "task-context",
            "structured-resources",
            "schemas",
            "policies",
        ],
        related=[
            "docs/architecture/task-scoped-agent-context-compilation.md",
            "docs/architecture/knowledge-authority.md",
            "docs/architecture/repository.md",
            "docs/current-mission.md",
        ],
    ),

    "docs/knowledge-promotion.md": DocumentDefinition(
        path="docs/knowledge-promotion.md",
        purpose="Defines the canonical human-applied Operations procedure for preparing, deciding, applying, validating, and tracing deliberate knowledge promotion.",
        canonical=True,
        generated=False,
        capability="Knowledge and Context",
        status="active",
        tags=[
            "operations",
            "knowledge-promotion",
            "human-review",
            "provenance",
            "canonical",
        ],
        related=[
            "docs/architecture/knowledge-authority.md",
            "docs/architecture/repository.md",
            "docs/standards/engineering-collaboration.md",
            "docs/current-mission.md",
            "docs/opportunities/reviewed/EO-2026-020-canonical-knowledge-promotion-workflow.yaml",
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
    "docs/roadmaps/platform-strategy.md": DocumentDefinition(
        path="docs/roadmaps/platform-strategy.md",
        purpose="Defines dated one-, three-, and five-year outcomes, six initiatives, dependencies, sequencing, evidence, and deliberate deferrals.",
        capability="Platform Direction and Governance",
        tags=["roadmap", "platform-strategy", "strategic-initiatives"],
        related=[
            "docs/vision.md",
            "docs/architecture/platform.md",
            "docs/architecture/capabilities.md",
            "docs/architecture/ai.md",
            "docs/current-mission.md",
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

    "docs/reviews/ai-workflow-evaluation-cycle-2026-07.md": DocumentDefinition(
        path="docs/reviews/ai-workflow-evaluation-cycle-2026-07.md",
        purpose="Records the completed human-reviewed AI workflow evaluation cycle, including configuration checks, firsthand task evidence, validation, friction, challenger comparisons, and the final operating decision.",
        capability="Artificial Intelligence",
        tags=[
            "artificial-intelligence",
            "workflow-evaluation",
            "firsthand-evidence",
            "provider-comparison",
            "human-reviewed",
        ],
        related=[
            "docs/architecture/ai-operating-model.md",
            "docs/architecture/knowledge-authority.md",
            "docs/reviews/ai-operating-baseline-2026-07-14.md",
            "docs/reviews/ai-capability-landscape-work-research-2026-07-14.md",
            "docs/reviews/ai-capability-landscape-claude-free-independent-audit-2026-07-14.md",
            "docs/reviews/ai-debugging-evaluation-g14-touchpad-2026-07-15.md",
            "docs/current-mission.md",
        ],
    ),

    "docs/reviews/mission-selection-review-2026-07-15.md": DocumentDefinition(
        path="docs/reviews/mission-selection-review-2026-07-15.md",
        purpose="Preserves mission-completion evidence, owner-originated candidate directions, portfolio overlap, engineering-session health assessment, the accepted selection of EO-2026-013, and the deferred AI Engineering Environment Review.",
        canonical=False,
        generated=False,
        capability="Engineering",
        status="accepted",
        tags=[
            "mission-selection",
            "candidate-directions",
            "session-health",
            "portfolio-review",
            "human-decision",
            "owner-decision",
            "task-context",
            "ai-environment-review",
            "dated-evidence",
            "non-canonical",
        ],
        related=[
            "docs/current-mission.md",
            "docs/knowledge-promotion.md",
            "docs/architecture/mission-advancement.md",
            "docs/architecture/engineering-sessions.md",
            "docs/reviews/ai-workflow-evaluation-cycle-2026-07.md",
            "docs/opportunities/reviewed/EO-2026-002-engineering-session-health-assessment.yaml",
            "docs/opportunities/reviewed/EO-2026-013-task-scoped-agent-context-compilation.yaml",
            "docs/opportunities/reviewed/EO-2026-020-canonical-knowledge-promotion-workflow.yaml",
        ],
    ),

    "docs/reviews/eo-2026-013-implementation-planning-review-2026-07-15.md": DocumentDefinition(
        path="docs/reviews/eo-2026-013-implementation-planning-review-2026-07-15.md",
        purpose="Preserves architecture-completion evidence, owner-approved mission advancement into implementation planning, the bounded vertical-slice plan, and the explicit implementation-authorization gate.",
        canonical=False,
        generated=False,
        capability="Engineering",
        status="accepted",
        tags=[
            "mission-advancement",
            "implementation-planning",
            "task-context",
            "context-compilation",
            "architecture-completion",
            "owner-decision",
            "human-reviewed",
            "dated-evidence",
            "non-canonical",
        ],
        related=[
            "docs/current-mission.md",
            "docs/architecture/task-scoped-agent-context-compilation.md",
            "docs/architecture/mission-advancement.md",
            "docs/architecture/engineering-sessions.md",
            "docs/standards/engineering-collaboration.md",
            "docs/reviews/mission-selection-review-2026-07-15.md",
            "docs/opportunities/reviewed/EO-2026-013-task-scoped-agent-context-compilation.yaml",
        ],
    ),

    "docs/reviews/knowledge-promotion-pilot-engineering-validation-2026-07-15.md": DocumentDefinition(
        path="docs/reviews/knowledge-promotion-pilot-engineering-validation-2026-07-15.md",
        purpose="Preserves the first non-canonical knowledge-promotion pilot as an accepted candidate with its decision, bounded application, execution evidence, validation, and repository traceability.",
        canonical=False,
        generated=False,
        capability="Engineering",
        status="accepted",
        tags=[
            "candidate-finding",
            "execution-evidence",
            "knowledge-promotion",
            "human-decision",
            "dated-evidence",
            "non-canonical",
        ],
        related=[
            "docs/knowledge-promotion.md",
            "docs/architecture/knowledge-authority.md",
            "docs/standards/engineering-collaboration.md",
            "docs/current-mission.md",
        ],
    ),

    "docs/reviews/ai-debugging-evaluation-g14-touchpad-2026-07-15.md": DocumentDefinition(
        path="docs/reviews/ai-debugging-evaluation-g14-touchpad-2026-07-15.md",
        purpose="Preserves sanitized dated diagnostic evidence for the G14 touchpad debugging evaluation as a non-canonical source record under human-reviewed interpretation.",
        canonical=False,
        generated=False,
        capability="Artificial Intelligence",
        status="evidence",
        tags=[
            "debugging-evaluation",
            "diagnostic-evidence",
            "source-record",
            "dated-evidence",
            "non-canonical",
        ],
        related=[
            "docs/architecture/knowledge-authority.md",
            "docs/architecture/ai-operating-model.md",
            "docs/reviews/ai-workflow-evaluation-cycle-2026-07.md",
            "docs/current-mission.md",
        ],
    ),

    "docs/reviews/ai-capability-landscape-work-research-2026-07-14.md": DocumentDefinition(
        path="docs/reviews/ai-capability-landscape-work-research-2026-07-14.md",
        purpose="Preserves the complete dated ChatGPT Work cloud-AI capability landscape report as non-canonical source evidence for human-reviewed workflow evaluation.",
        canonical=False,
        generated=False,
        capability="Artificial Intelligence",
        status="evidence",
        tags=[
            "artificial-intelligence",
            "research-evidence",
            "source-record",
            "chatgpt-work",
            "dated-evidence",
            "non-canonical",
        ],
        related=[
            "docs/architecture/knowledge-authority.md",
            "docs/architecture/ai-operating-model.md",
            "docs/reviews/ai-operating-baseline-2026-07-14.md",
            "docs/reviews/ai-workflow-evaluation-cycle-2026-07.md",
            "docs/current-mission.md",
        ],
    ),

    "docs/reviews/ai-capability-landscape-claude-free-independent-audit-2026-07-14.md": DocumentDefinition(
        path="docs/reviews/ai-capability-landscape-claude-free-independent-audit-2026-07-14.md",
        purpose="Preserves the complete dated Claude Free independent audit of the cloud-AI capability landscape as non-canonical source evidence for human-reviewed workflow evaluation.",
        canonical=False,
        generated=False,
        capability="Artificial Intelligence",
        status="evidence",
        tags=[
            "artificial-intelligence",
            "claude-free",
            "independent-audit",
            "independent-provider",
            "source-record",
            "dated-evidence",
            "non-canonical",
        ],
        related=[
            "docs/architecture/knowledge-authority.md",
            "docs/reviews/ai-capability-landscape-work-research-2026-07-14.md",
            "docs/reviews/ai-workflow-evaluation-cycle-2026-07.md",
            "docs/reviews/ai-operating-baseline-2026-07-14.md",
            "docs/current-mission.md",
        ],
    ),

    "docs/reviews/ai-operating-baseline-2026-07-14.md": DocumentDefinition(
        path="docs/reviews/ai-operating-baseline-2026-07-14.md",
        purpose="Records the dated current AI access inventory, task profiles, provisional operating decisions, privacy boundaries, challenger policy, evaluation method, and reassessment triggers.",
        capability="Artificial Intelligence",
        tags=[
            "artificial-intelligence",
            "ai-operating-baseline",
            "provider-evaluation",
            "workflow-evaluation",
            "human-reviewed",
        ],
        related=[
            "docs/architecture/ai.md",
            "docs/architecture/ai-operating-model.md",
            "docs/architecture/knowledge-authority.md",
            "docs/current-mission.md",
            "docs/reviews/engineering-opportunity-portfolio-recalibration.md",
            "docs/roadmaps/platform-strategy.md",
        ],
    ),

    "docs/reviews/engineering-opportunity-portfolio-recalibration.md": DocumentDefinition(
        path="docs/reviews/engineering-opportunity-portfolio-recalibration.md",
        purpose="Records the accepted human-reviewed classification, relationships, dispositions, priorities, and Distinctness branch decision for the Engineering Opportunity portfolio.",
        capability="Engineering and Evolution",
        tags=[
            "engineering-opportunity",
            "portfolio-review",
            "human-reviewed",
            "strategic-recalibration",
        ],
        related=[
            "docs/current-mission.md",
            "docs/vision.md",
            "docs/architecture/capabilities.md",
            "docs/architecture/engineering-opportunity.md",
            "docs/architecture/engineering-opportunity-assessment.md",
            "docs/architecture/engineering-opportunity-distinctness-analysis.md",
            "docs/roadmaps/platform-strategy.md",
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
            "docs/architecture/engineering-opportunity-scope-classification.md",
            "docs/architecture/engineering-opportunity-distinctness-analysis.md",
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

    "docs/architecture/engineering-opportunity-scope-classification.md": DocumentDefinition(
        path="docs/architecture/engineering-opportunity-scope-classification.md",
        purpose="Defines how Engineering Opportunity Intelligence classifies primary scope and secondary implications while preserving evidence, uncertainty, and human judgment.",
        capability="Engineering",
        tags=[
            "engineering-opportunity-scope-classification",
            "engineering-opportunity-intelligence",
            "structured-assessment",
            "repository-reasoning",
        ],
        related=[
            "docs/architecture/engineering-opportunity-object.md",
            "docs/architecture/engineering-opportunity-intelligence.md",
            "docs/architecture/engineering-opportunity-assessment.md",
            "docs/architecture/engineering-opportunity-capability-alignment.md",
            "docs/architecture/reasoning.md",
        ],
    ),

    "docs/architecture/engineering-opportunity-distinctness-analysis.md": DocumentDefinition(
        path="docs/architecture/engineering-opportunity-distinctness-analysis.md",
        purpose="Defines how Engineering Opportunity Intelligence compares opportunity objects and produces evidence-backed duplicate, overlap, component, umbrella, distinct, and insufficient-evidence findings.",
        capability="Engineering",
        tags=[
            "engineering-opportunity-distinctness-analysis",
            "engineering-opportunity-intelligence",
            "opportunity-comparison",
            "repository-reasoning",
        ],
        related=[
            "docs/architecture/engineering-opportunity-object.md",
            "docs/architecture/engineering-opportunity-intelligence.md",
            "docs/architecture/engineering-opportunity-assessment.md",
            "docs/architecture/engineering-opportunity-capability-alignment.md",
            "docs/architecture/engineering-opportunity-scope-classification.md",
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
