# Engineering Review Architecture

## Purpose

Engineering Review is the capability that helps determine the next highest-leverage engineering investment for the Aiden Platform.

It exists to answer:

    Given the current repository state, synchronization state, validation state, architecture, and capability maturity, what should engineering focus on next?

Engineering Review should turn existing repository knowledge and reasoning outputs into an evidence-backed engineering recommendation.

## Core Principle

Engineering Review composes existing capabilities.

It should not duplicate repository validation, synchronization, state inspection, impact analysis, or guidance logic.

## Architectural Position

Engineering Review sits above individual engineering capabilities and below engineering interfaces.

    Repository
        ↓
    Repository Knowledge
        ↓
    Repository Reasoning
        ↓
    Engineering Capabilities
        ↓
    Engineering Review
        ↓
    Interfaces

Interfaces may include:

- Atlas CLI
- ChatGPT project workflows
- Local AI assistants
- VS Code integrations
- Future Aiden OS engineering workflows

## Inputs

Engineering Review should consume evidence from existing capabilities.

Initial inputs include:

- Repository Validation
- Repository Synchronization
- Engineering State Inspection
- Impact Analysis
- Engineering Guidance
- Engineering Capability Architecture
- Current Mission
- Git working state

## Review Questions

Engineering Review should answer:

- Is the repository structurally valid?
- Is the repository synchronized?
- Is the working tree clean?
- What is the active mission?
- What is the current next milestone?
- Which capabilities are mature, growing, early, planned, or architectural?
- Which capability improvement would unlock the most future engineering leverage?
- Which architecture documents are most relevant to the next investment?
- What should be done next, and why?

## Review Process

Engineering Review should evaluate engineering state in this order:

1. Validate repository consistency.
2. Check synchronization state.
3. Inspect current engineering state.
4. Identify active mission and milestone.
5. Review capability maturity.
6. Identify blockers or drift.
7. Recommend the highest-leverage next engineering investment.

If validation or synchronization reports errors, Engineering Review should prioritize resolving those before recommending new work.

## Outputs

An Engineering Review report should include:

- Overall engineering health
- Blocking issues
- Synchronization status
- Current mission
- Capability maturity summary
- Highest-leverage recommendation
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
