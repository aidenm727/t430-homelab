# Aiden Platform Operating Model — External Design-Validation Research Request

**Date context:** July 17, 2026  
**Status:** Research request preserved for provenance  
**Repository authority:** Connected live GitHub repository is canonical  
**Implementation authorization:** None

Treat the attached July 17 architecture discovery report as a proposal to validate or challenge. Use the connected live GitHub repository as canonical wherever it conflicts with attached or generated context.

## Research objective

Conduct an external architecture and design-validation study for the proposed Aiden Platform Operating Model and Human Control Surface.

The Aiden Platform is a personal capability and engineering platform. GitHub is the canonical engineering record. Atlas is the deterministic engineering interface that understands repository state, compiles task-scoped context, validates engineering work, and exposes evidence-backed reasoning. AI systems such as ChatGPT, Codex, research environments, alternative frontier models, and future agents should remain replaceable workspaces rather than becoming the canonical owners of platform state.

The owner identified these current problems:

- Important intent and authorization can remain trapped in AI conversations.
- Transitions between ChatGPT discussion and repository implementation are difficult to follow.
- The repository and CLI are useful for AI and engineering execution but are not sufficient as a human operating interface.
- The owner needs a visual way to understand active work, capabilities, dependencies, completion state, approvals, and next actions.
- Future unattended engineering will require durable task state, explicit permissions, verification, auditability, and human approval boundaries.
- Agent-generated changes may increase throughput while also increasing hidden redundancy, technical debt, review burden, and architectural drift.

A proposed architecture introduces:

1. Aiden OS or Aiden Platform Console as the human control surface.
2. Atlas as the deterministic knowledge, validation, context-compilation, and reasoning layer.
3. GitHub as canonical architecture, code, documentation, history, and evidence.
4. AI and automation environments as replaceable workers.
5. Durable task objects as the bridge between human intent, AI workspaces, and repository changes.
6. Explicit lifecycle protocols for Engineering Opportunities, research, implementation, review, and automation.
7. A gradual autonomy ladder from observation through bounded draft pull requests.

Determine which proven architecture, workflow, and safety patterns should inform this design. Do not merely list AI products. Research capability and operating patterns across serious software engineering, workflow orchestration, developer platforms, agent systems, and human-in-the-loop automation.

## Questions

1. How do leading agentic software environments externalize task state rather than relying on conversation history?
2. How do they represent task objectives, repository revision, scope, permissions, prohibited actions, expected outputs, verification, approvals, retries, failures, resumability, and audit history?
3. How do systems safely transfer work between human discussion, planning, coding agents, branches and worktrees, CI, pull requests, human review, and deployment or completion?
4. What patterns exist for durable human-in-the-loop approval workflows?
5. Which state belongs in Git, GitHub issues or pull requests, workflow engines, databases, structured repository objects, AI conversations, and generated context packages?
6. How should a system distinguish lifecycle state, capability maturity, implementation health, verification status, human authorization, and agent permission level?
7. What are the major failure modes of agent-generated software changes, especially hidden redundancy, unnecessary abstraction, quiet technical debt, false confidence from passing tests, context loss, scope expansion, stale assumptions, insecure tool access, and review overload?
8. What evidence should be required before accepting an agent-generated change?
9. Which maintenance activities are appropriate for unattended agents today, and which should remain explicitly human-gated?
10. What autonomy ladder is supported by current evidence?
11. What human-facing interfaces are effective for presenting current mission, work in progress, approval queues, agent activity, system health, dependency maps, evidence, and next actions?
12. Should the Aiden Platform initially use repository-owned task files, GitHub issues, pull requests, GitHub Actions, a workflow engine, Atlas-generated JSON, a generated static site, a separate application database, or a hybrid?
13. Which parts of the proposed architecture are well supported by external precedent?
14. Which parts appear premature, unnecessarily complex, or risky?
15. What is the smallest architecture checkpoint that would produce meaningful evidence before building a large interface?

## Required sources

Prioritize primary and authoritative material:

- official OpenAI Codex documentation and engineering publications
- official GitHub Agentic Workflows, Copilot coding-agent, pull-request, and security publications
- official Anthropic agent, context-engineering, and evaluation publications
- durable workflow and human-approval documentation from established workflow systems
- relevant standards
- original research on agent-generated code quality, technical debt, software-agent evaluation, and human review
- source repositories where implementation details are material

Use social media, YouTube, Reddit, and secondary reporting only to discover leads. Do not use them as primary evidence for architectural conclusions.

## Required output

Produce:

1. Executive conclusion.
2. Evidence-backed architecture principles.
3. A comparison of external system patterns.
4. A recommended Aiden task-state model.
5. A recommended human-approval model.
6. A recommended workspace-handoff model.
7. A recommended agent authority model.
8. A recommended verification and acceptance model.
9. A recommended V1 control-surface architecture.
10. A list of patterns the Aiden Platform should avoid.
11. A smallest responsible implementation checkpoint.
12. A risk register.
13. Unresolved owner decisions.
14. A source ledger containing exact title, organization, publication date, canonical raw URL, source type, exact claim supported, and whether it supports documented fact, analogy, inference, or recommendation.

Clearly distinguish documented external facts, architectural analogies, inferred implications, and recommendations for the Aiden Platform.

Do not modify the connected repository. Do not create commits or pull requests. Do not assume that the proposed architecture has already been accepted. Do not modify or expand EO-2026-013. Treat the discovery report as a proposal requiring independent validation, not as a conclusion to defend.
