# Engineering Review Architecture

## Purpose

Engineering Review is the engineering review interface for the Aiden Platform.

It presents Engineering Interpretation output so a human engineer, AI assistant, or future interface can understand the current engineering state and next responsible checkpoint.

It exists to answer:

    What does Atlas recommend now, why does it recommend it, and what evidence supports that guidance?

Engineering Review should make engineering guidance understandable, traceable, and actionable.

It should not generate guidance independently of Engineering Interpretation.

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

- Repository health
- Synchronization status
- Working tree readiness
- Current mission
- Current milestone
- Milestone criteria
- Blockers
- Recommended action
- Reason
- Next checkpoint
- Relevant evidence
- Suggested verification path

Engineering Review may also display selected Engineering Intelligence fields when they help explain the recommendation.

## Review Questions

Engineering Review should help the engineer answer:

- Is the repository ready for engineering work?
- Are there blockers?
- What is the current mission?
- What is the current milestone?
- What criteria are satisfied or unsatisfied?
- What is the recommended next checkpoint?
- Why is that recommendation being made?
- What evidence supports it?
- What should be verified afterward?

## Review Process

Engineering Review should present engineering state in this order:

1. Show overall health and readiness.
2. Show blockers before new work.
3. Show current mission and milestone.
4. Show satisfied and unsatisfied criteria.
5. Show interpreted recommendation.
6. Show supporting evidence.
7. Show suggested commands or verification steps.

If validation, synchronization, or working tree blockers exist, Engineering Review should make those blockers visible before presenting new engineering work.

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

## Non-Responsibilities

Engineering Review should not:

- Make architecture decisions automatically
- Replace human prioritization
- Hide uncertainty
- Modify repository contents
- Duplicate validation or synchronization checks
- Become conversational memory
- Depend on a single AI provider or interface

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
