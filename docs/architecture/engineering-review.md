# Engineering Review Architecture

## Purpose

Engineering Review is the engineering review interface for the Aiden Platform.

It presents Engineering Interpretation output so a human engineer, AI assistant, or future interface can understand the current engineering state and next responsible checkpoint.

It exists to answer:

    What does Atlas recommend now, why does it recommend it, and what evidence supports that guidance?

Engineering Review should make engineering guidance understandable, traceable, and actionable.

It should not generate guidance independently of Engineering Interpretation.

This Atlas interface is distinct from the fresh independent checkpoint review
required by Workflow v1.1. Running `./atlas review`, reviewing one’s own work,
or producing an implementation report does not satisfy that independent gate.

## Core Principle

Engineering Review presents interpreted engineering guidance.

It should not duplicate Repository Knowledge, Repository Reasoning, Engineering Intelligence, or Engineering Interpretation.

## Architectural Position

Engineering Review sits in the Engineering Interfaces layer.

    Repository
        ↓
    Repository Knowledge
        ↓
    Repository Reasoning
        ↓
    Engineering Intelligence
        ↓
    Engineering Interpretation
        ↓
    Engineering Review

Engineering Review is one interface over shared Atlas capabilities.

Other interfaces may include:

- atlas bootstrap
- atlas next
- ChatGPT project workflows
- Local AI assistants
- VS Code integrations
- Future dashboards
- Future Aiden OS engineering workflows

## Inputs

Engineering Review should consume Engineering Interpretation output.

Engineering Interpretation should already contain:

- Repository health and declared validation scope
- Synchronization status and declared synchronization scope
- Working-tree observation
- Current phase and lifecycle
- Work-selection state and selected checkpoint
- Intentional idle
- Milestone criteria
- Blockers
- Unknowns
- External authority status
- Recommended action
- Reason
- Next checkpoint
- Relevant evidence
- Suggested verification path

Engineering Review may also display selected Engineering Intelligence fields when they help explain the recommendation.

## Review Questions

Engineering Review should help the engineer answer:

- What is the repository health within the declared scope?
- What does repository health cover?
- Are there blockers?
- What is the current phase?
- Is work selected or intentionally idle?
- What authority is not established by Atlas?
- What criteria are satisfied or unsatisfied?
- What is the recommended next checkpoint?
- Why is that recommendation being made?
- What evidence supports it?
- What should be verified afterward?

## Review Process

Engineering Review should present engineering state in this order:

1. Show overall health and readiness.
2. Show blockers before new work.
3. Show current phase, work selection, and external authority status.
4. Show satisfied and unsatisfied criteria.
5. Show interpreted recommendation.
6. Show supporting evidence.
7. Show suggested commands or verification steps.

If validation, synchronization, or working tree blockers exist, Engineering Review should make those blockers visible before presenting new engineering work.

## Proportional Independent Checkpoint Review

Independent review examines the exact final candidate and its accepted brief,
not a superseded patch or implementation narrative. The reviewer starts fresh,
has not implemented the candidate, inspects the complete diff and evidence, and
does not gain implementation, acceptance, publication, or deployment authority
from the review assignment.

- **Tier 1:** Independent review is not automatic. Use it for unusual
  uncertainty, reviewer request, sensitive public wording, or escalation.
- **Tier 2:** One fresh independent review is required by default. An in-scope
  material correction receives review of the affected delta without restarting
  the full lifecycle.
- **Tier 3:** One adversarial independent review is required. A blocking
  correction requires final verification and a fresh final adversarial review
  of the corrected candidate.

Review should test scope, architecture, consequence classification, protected
boundaries, negative paths, evidence truthfulness, verification coverage,
generated synchronization, and the exact next decision. It must state
uncertainty rather than invent missing execution or external evidence.

## Finding Disposition

Each finding records its affected path or contract, evidence, consequence,
blocking status, and required action.

- A blocking finding means the candidate is not ready for owner acceptance.
  Correct it only when it remains inside the accepted checkpoint; otherwise
  stop for owner decision or redesign.
- A non-blocking finding is corrected, explicitly accepted as residual risk, or
  deferred to a separately selected checkpoint. It does not silently expand
  the current scope.
- After correction, rerun affected focused checks and the tier-appropriate
  final broad verification after the last mutation. Tier 2 rechecks a material
  affected delta; Tier 3 applies the fresh-final-review rule above.
- Preserve the finding and disposition in the compact compound evidence. Do not
  erase a resolved blocking finding from the review chain.

Owner acceptance follows required verification and finding disposition and
applies only to the exact candidate. It does not authorize staging, commit,
publication, deployment, migration, or another external write.

## Owner-Facing Status

Use this compact presentation:

    Goal:
    Lifecycle state:
    Risk tier:
    Authority:
      Task:
      Implementation:
      Publication/deployment:
    Changed:
    Verification:
    Independent review:
    Unresolved risks:
    Exact next decision:

Allowed lifecycle descriptions are Designed, Accepted for implementation,
Implementing, Verifying, Under independent review, Correction in progress,
Implementation accepted, Awaiting publication, Published, and Stopped.

This status is a human-readable presentation, not a new repository object or
canonical-state system. It reports selected work and external authority as
separate facts, never selects work, and never creates authority.

## Outputs

An Engineering Review report should include:

- Overall engineering health
- Readiness state
- Blocking issues
- Current mission
- Current milestone
- Milestone criteria
- Interpreted recommendation
- Reason for recommendation
- Supporting evidence
- Suggested next commands
- Relevant documents

The report must not collapse a healthy repository, selected work, and
implementation permission into one readiness value.

## Recommendation Standard

Every recommendation must include evidence.

A good recommendation should explain:

- What should happen next
- Why it matters
- Which capability it improves
- Which repository evidence supports it
- What should be verified afterward

Engineering Review should avoid vague recommendations.

## Capability Maturity

Engineering Review should eventually classify capabilities by maturity.

Suggested maturity levels:

- Architectural — designed but not implemented
- Early — implemented in basic form
- Growing — useful but still limited
- Operational — works reliably for current workflows
- Platform Native — integrated across multiple interfaces and workflows

Capability maturity should help prioritize improvements.

## Design Rules

Engineering Review must:

- Reuse existing capabilities
- Keep commands thin
- Explain recommendations with evidence
- Prefer consolidation before expansion
- Prefer strengthening existing capabilities before adding new ones
- Preserve human architectural judgment
- Remain deterministic where practical

## Completion Criteria

The Engineering Review capability is considered complete when:

- Repository Knowledge owns repository facts.
- Repository Reasoning owns engineering evaluation.
- Engineering Intelligence composes reasoning outputs into a structured engineering picture.
- Engineering Interpretation produces engineering recommendations from structured intelligence.
- Engineering Review remains a thin presentation interface.
- Atlas commands consume Engineering Review rather than duplicating engineering logic.
- AI-assisted engineering sessions naturally begin from Engineering Review.
- Engineering recommendations are evidence-backed, deterministic, and traceable to canonical repository knowledge.

Completion of this capability does not imply Engineering Review is feature-complete.

Future improvements should extend Repository Knowledge, Repository Reasoning, Engineering Intelligence, and Engineering Interpretation rather than increasing interface complexity.

## Non-Responsibilities

Engineering Review should not:

- Make architecture decisions automatically
- Replace human prioritization
- Hide uncertainty
- Modify repository contents
- Duplicate validation or synchronization checks
- Become conversational memory
- Depend on a single AI provider or interface
- Grant or infer task, implementation, publication, deployment, or external-write authority

## Relationship to Atlas

Atlas should expose Engineering Review through a thin interface when the capability is ready.

Possible future interfaces include:

- atlas review
- atlas next
- engineering session startup reports
- generated AI context summaries
- ChatGPT project startup prompts
- local AI engineering agents

The first interface does not need to be the final interface.

## Future Direction

Engineering Review should eventually become the normal starting point for Aiden Platform engineering sessions.

A future engineering session should begin by asking:

    Is the repository healthy?
    Is it synchronized?
    What capability should improve next?
    What is the highest-leverage engineering checkpoint?

Engineering Review should help the platform improve itself deliberately rather than relying only on conversational memory or intuition.
