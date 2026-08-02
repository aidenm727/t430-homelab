# Engineering Methodology

## Purpose

Defines how the Aiden Platform evolves from idea to architecture to implementation.

## Core Principle

The platform evolves by improving capabilities, not by randomly installing services.

## Collaboration Contract

Engineering sessions are governed by:

    docs/standards/engineering-collaboration.md

That document owns Engineering Workflow v1.1: consequence-based tiers, the
checkpoint brief, authority gates, proportional assurance, evidence, and
publication/deployment procedure.

This architecture document defines engineering intent.

The collaboration contract defines how that intent is applied during active engineering work.

## Workflow v1.1 Entry Point

1. Classify the checkpoint by its highest potential consequence.
2. Record one concise checkpoint brief.
3. Establish design and implementation authority appropriate to the tier.
4. Complete repository and native-environment preflight.
5. Implement within the exact boundary using focused verification.
6. Run the tier-appropriate final broad verification after the last mutation.
7. Complete proportional independent review and owner acceptance when required.
8. Obtain separate, exact publication or deployment authority before any
   commit, push, deployment, or external write.

Session startup and environment preflight are owned by
`docs/architecture/engineering-sessions.md`. Verification and correction
sequencing are owned by `docs/architecture/engineering-lifecycle.md`.
Independent review and owner-facing status are owned by
`docs/architecture/engineering-review.md`.

## Decision Rules

## Experiment vs Production

## Capability-Driven Planning

## Documentation Rules

## Change Management

## Promotion Path

Idea → Experiment → Documented capability → Production service

## Current Standard

A verified local candidate is not thereby accepted, committed, published,
deployed, or operational. Those lifecycle facts and authorities remain
distinct at every risk tier.
