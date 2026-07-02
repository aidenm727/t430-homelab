# Milestone Completion Reasoning Architecture

## Purpose

Milestone Completion Reasoning determines whether the current engineering milestone has likely been completed based on repository evidence.

It does not decide what the next milestone should be.

Instead, it provides deterministic evidence that helps engineers determine when the current mission should advance.

## Core Principle

Milestone Completion Reasoning evaluates engineering progress.

It does not create engineering direction.

Architectural decisions remain human responsibilities.

## Architectural Position

Milestone Completion Reasoning is part of the Repository Reasoning Layer.

    Repository
        ↓
    Repository Knowledge
        ↓
    Repository Reasoning
        ↓
    Milestone Completion Reasoning
        ↓
    Engineering Review
        ↓
    Interfaces

## Inputs

Milestone Completion Reasoning may consume evidence from:

- Repository Validation
- Repository Synchronization
- Engineering State
- Engineering Guidance
- Repository Knowledge
- Current Mission
- Repository Metadata

## Engineering Questions

The capability should answer questions such as:

- Has the current milestone already been substantially implemented?
- Does repository evidence support advancing the current mission?
- Which evidence supports completion?
- Which evidence contradicts completion?
- What confidence should be assigned?

## Evidence

Evidence may include:

- Architecture exists.
- Implementation exists.
- Validation succeeds.
- Synchronization succeeds.
- Commands exist.
- Capability is operational.
- Documentation has been updated.
- Repository metadata is complete.

Evidence should remain deterministic whenever practical.

## Outputs

The reasoning output should include:

- Completion status
- Confidence
- Supporting evidence
- Missing evidence
- Recommendation

Possible completion states:

- Not Started
- In Progress
- Substantially Complete
- Complete
- Unknown

Confidence should be reported independently of completion.

## Relationship to Engineering Review

Engineering Review consumes Milestone Completion Reasoning.

Engineering Review may recommend advancing the current mission when Milestone Completion Reasoning reports that the active milestone is complete with sufficient confidence.

Engineering Review should explain that recommendation using repository evidence.

## Non-Responsibilities

Milestone Completion Reasoning should not:

- Modify the current mission
- Invent new milestones
- Rewrite documentation
- Replace architectural judgment
- Infer undocumented intent

Its responsibility is to evaluate completion, not determine strategy.

## Future Direction

Future implementations may compare:

- Roadmap progress
- Capability maturity
- Repository evolution
- Documentation freshness
- Cross-document consistency

Milestone Completion Reasoning establishes the first step toward broader engineering evolution reasoning while remaining intentionally focused on one engineering question.
