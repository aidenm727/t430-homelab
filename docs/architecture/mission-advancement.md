# Mission Advancement Architecture

## Purpose

Mission Advancement determines whether repository evidence supports advancing the active engineering mission.

It consumes Engineering Intelligence and produces an evidence-backed recommendation for human review.

## Core Principle

Mission Advancement recommends direction changes.

It does not make direction changes.

The human engineer remains responsible for approving mission updates.

## Relationship to Milestone Completion

Milestone Completion asks:

    Has the current milestone likely been completed?

Mission Advancement asks:

    Given milestone completion, repository health, synchronization, and engineering context, should the current mission advance?

A completed milestone is evidence for mission advancement, but it is not the only factor.

## Inputs

Mission Advancement may consume:

- Engineering Intelligence
- Milestone Completion Reasoning
- Repository Validation
- Repository Synchronization
- Current Mission
- Git State
- Relevant architecture documents

## Outputs

A Mission Advancement recommendation should include:

- Recommendation
- Confidence
- Supporting evidence
- Blocking concerns
- Suggested human decision
- Suggested follow-up actions

## Design Rules

Mission Advancement must:

- Use Engineering Intelligence rather than duplicating lower-level checks
- Preserve human approval
- Explain recommendations with evidence
- Avoid inventing new missions automatically
- Prefer clear next actions over vague guidance

## Non-Responsibilities

Mission Advancement should not:

- Rewrite `docs/current-mission.md`
- Invent the next milestone
- Replace strategic judgment
- Ignore repository health blockers
- Treat milestone completion alone as sufficient evidence

## Future Direction

Future Mission Advancement may suggest candidate next milestones from roadmaps, architecture, and Engineering Review, but those suggestions should remain recommendations until approved by the human engineer.
