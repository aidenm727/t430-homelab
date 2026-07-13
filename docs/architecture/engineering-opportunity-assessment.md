# Engineering Opportunity Assessment Architecture

## Purpose

Engineering Opportunity Assessment defines the reusable reasoning contract for
evaluating one Engineering Opportunity Object or comparing several
opportunities.

Its purpose is to ensure that Opportunity Intelligence produces assessments
that are structured, explainable, evidence-backed, confidence-aware, and
separate from lifecycle mutation.

---

## Core Principle

An assessment is derived engineering reasoning.

It is not the canonical opportunity object.

It is not a human decision.

It is not an automatic repository mutation.

An assessment should help the engineer make a better decision while preserving
the distinction between observable facts, derived findings, and recommended
actions.

---

## Architectural Position

Engineering Opportunity Assessment belongs to Engineering Opportunity
Intelligence.

    Engineering Opportunity Objects
        ↓
    Engineering Opportunity Intelligence
        ↓
    Engineering Opportunity Assessments
        ↓
    Engineering Intelligence
        ↓
    Engineering Interpretation
        ↓
    Engineering Review
        ↓
    Human Decision

Opportunity Intelligence produces assessments.

Engineering Intelligence composes them.

Engineering Interpretation determines responsible action.

Engineering Review presents the recommendation.

The human engineer authorizes lifecycle change.

---

## Relationship to Canonical Objects

Engineering Opportunity Objects preserve repository truth.

Assessments are rebuildable outputs derived from:

- Opportunity objects.
- Repository knowledge.
- Architecture.
- Current mission.
- Capability evidence.
- Dependencies.
- Relationships.
- Engineering state.

An assessment should never silently become the canonical source for:

- Opportunity identity.
- Lifecycle state.
- Human decisions.
- Acceptance.
- Rejection.
- Merge approval.
- Scheduling.
- Completion.

If an assessment reveals information that should become canonical, a
human-authorized repository change should record it.

---

## Assessment Layers

Every assessment should distinguish three layers.

### Repository Facts

Repository facts are directly observable.

Examples include:

- Opportunity identifier.
- Title.
- Lifecycle state.
- Repository path.
- Capability field.
- Created date.
- Source.
- Explicit dependencies.
- Explicit related opportunities.
- Referenced architecture.
- Current mission.
- Validation status.
- Synchronization status.

Facts should identify their source.

### Derived Findings

Derived findings are conclusions supported by facts and evidence.

Examples include:

- The opportunity overlaps another opportunity.
- The opportunity is a component of a larger opportunity.
- Required architecture does not exist.
- An explicit dependency is incomplete.
- The rationale lacks sufficient evidence.
- The opportunity aligns with the active mission.
- The opportunity appears ready for review.

Findings should expose:

- Basis.
- Supporting evidence.
- Confidence.
- Uncertainty.

### Engineering Recommendations

Recommendations interpret facts and findings.

Examples include:

- Retain the opportunity as captured.
- Enrich its evidence.
- Merge it into another opportunity.
- Review it for acceptance.
- Architect it before implementation.
- Defer it.
- Schedule it.
- Close it with a documented reason.

Recommendations must not be presented as repository facts.

---

## Scope Classification

Scope classification prevents comparison between fundamentally different kinds
of opportunities.

An opportunity may have one primary scope and several secondary implications.

### Strategic Direction

A durable long-term direction that may influence several capabilities,
architectures, missions, or roadmaps.

Examples include personal AI direction or infrastructure sovereignty.

### Capability Opportunity

An opportunity to create or strengthen a durable platform capability.

Examples include Documentation Intelligence or AI Collaboration Intelligence.

### Architecture Opportunity

An opportunity to establish, clarify, or revise durable system design.

### Engineering System Opportunity

An opportunity to improve engineering workflow, repository reasoning, Atlas,
session startup, validation, or collaboration quality.

### Implementation Opportunity

A bounded implementation, refactoring, replacement, or tooling improvement.

### Operational or Infrastructure Opportunity

An opportunity focused on deployed systems, reliability, security, storage,
networking, services, or operating procedures.

Scope is normally a derived finding rather than a required object field.

The detailed canonical Scope Classification contract is defined in:

    docs/architecture/engineering-opportunity-scope-classification.md

---

## Relationship Model

Opportunity assessments should reason explicitly about relationships.

Similarity is not automatically duplication.

### Duplicate Of

Two objects describe the same underlying engineering opportunity.

A duplicate finding should identify the proposed canonical target.

### Overlaps With

Two opportunities share meaningful scope but remain independently valuable.

Overlap alone is not sufficient reason to merge.

### Component Of

A narrower opportunity contributes to a broader capability or umbrella
opportunity.

Example:

    Engineering session health assessment
        component_of
    AI Collaboration Intelligence

### Umbrella For

A broader opportunity organizes several narrower component opportunities.

### Depends On

An opportunity requires another opportunity, architecture, capability, or
engineering change before responsible progression.

### Enables

Completing an opportunity materially improves the feasibility or value of
another opportunity.

### Supersedes

A newer opportunity or architecture replaces the purpose of an older one.

### Conflicts With

Two opportunities imply incompatible architectural directions or resource
commitments.

### Related To

A meaningful relationship exists but does not fit a stronger type.

Relationship findings should include:

- Relationship type.
- Source opportunity.
- Target opportunity.
- Directionality.
- Supporting evidence.
- Explanation.
- Confidence.

Keyword similarity alone should never establish duplication.

---

## Evaluation Dimensions

Assessments may evaluate the following dimensions.

### Object Quality

- Required fields exist.
- The summary is understandable.
- The rationale explains why the opportunity matters.
- Notes preserve useful context.
- Evidence is sufficient for the current lifecycle state.

### Distinctness

- The opportunity represents one coherent possibility.
- It does not merely repeat another object.
- Its boundary from adjacent opportunities is explainable.

### Capability Value

- The opportunity strengthens a defined platform capability.
- It increases agency or engineering leverage.
- It contributes to long-term platform usefulness.

### Architectural Significance

- The opportunity requires durable design.
- It affects several systems or capabilities.
- It changes repository ownership or system boundaries.
- Architecture should precede implementation.

### Compounding Leverage

- The opportunity makes future engineering easier.
- It improves several downstream capabilities.
- It reduces repeated friction or duplicated work.
- Its value increases as the platform grows.

### Mission Relevance

- The opportunity directly supports the active mission.
- It is a prerequisite of the active milestone.
- It should remain outside the current mission.

### Evidence Strength

- Repository evidence directly supports the opportunity.
- Evidence is repeated rather than anecdotal.
- Relevant architecture, history, or operational observations exist.
- Important assumptions remain unresolved.

### Dependency Readiness

- Required architecture exists.
- Required capabilities exist.
- Blocking opportunities are understood.
- The repository can responsibly support the work.

### Effort and Complexity

- Relative engineering effort.
- Architectural complexity.
- Operational burden.
- Security implications.
- Maintenance cost.
- Verification difficulty.

### Urgency and Risk

- Existing reliability or security problems.
- Risk of knowledge loss.
- Repeated engineering failure.
- Time-sensitive external dependency.
- Cost of continued deferral.

Dimensions should produce explained findings rather than one opaque score.

---

## Determinism and Engineering Judgment

Assessment reasoning should remain deterministic where practical without
pretending all engineering judgment is deterministic.

### Deterministic Evidence

Examples include:

- Required fields.
- Identifier uniqueness.
- Lifecycle state.
- Repository location.
- Exact explicit relationships.
- Referenced document existence.
- Current mission text.
- Validation and synchronization state.

### Deterministic Derived Findings

Examples include:

- Status and directory mismatch.
- Missing dependency object.
- Duplicate stable identifier.
- Missing referenced document.
- An explicitly declared dependency is incomplete.

### Heuristic Findings

Examples include:

- Similar titles.
- Shared capability ownership.
- Shared referenced documents.
- Potential overlap based on normalized language.
- Possible component or umbrella relationships.

Heuristic findings should be presented as candidates.

### Engineering Judgment

Examples include:

- Whether semantically similar opportunities should merge.
- Whether an opportunity has high strategic value.
- Whether existing architecture is sufficient.
- Whether expected effort is justified.
- Whether an opportunity should influence a future mission.

AI assistance may contribute judgment.

The platform must never disguise AI judgment as deterministic repository truth.

---

## Confidence Model

Confidence should be explainable and should apply to individual findings where
practical.

### High Confidence

The conclusion follows directly from explicit repository evidence with little
reasonable ambiguity.

### Medium Confidence

The conclusion is well supported but includes interpretation or incomplete
evidence.

### Low Confidence

The conclusion is tentative, evidence is incomplete, or meaningful alternative
interpretations remain.

One assessment may contain high-confidence facts and low-confidence
recommendations.

Confidence is not a substitute for evidence.

---

## Recommendation Model

Opportunity assessments may recommend the following actions.

### Retain Captured

The opportunity is valid, but no lifecycle progression is currently justified.

### Enrich

The opportunity needs stronger summary, rationale, evidence, relationships, or
capability alignment.

### Merge Into

The opportunity appears to duplicate another object and should be merged into
an identified canonical opportunity after human review.

### Close as Duplicate

The opportunity should remain historically traceable but be closed because
another object owns the same engineering possibility.

### Review

The opportunity has enough evidence for deliberate human evaluation.

### Accept

The opportunity appears worthwhile as future platform work.

Acceptance does not schedule implementation.

### Architect

The opportunity requires durable design before implementation.

### Schedule

Architecture and dependencies appear sufficient, and the opportunity is
appropriate for active engineering planning.

### Defer

The opportunity remains valuable but is not appropriate for the current
mission, maturity, capacity, or architecture.

### Close

The opportunity should be rejected, retired, superseded, merged, completed, or
otherwise intentionally removed from active consideration.

Recommendations never mutate lifecycle state automatically.

---

## Prioritization Model

Priority is contextual rather than permanently intrinsic.

The same opportunity may change priority as missions, dependencies, risks,
capabilities, and platform maturity change.

Assessments should prioritize using principles such as:

1. Resolve active security, reliability, and repository-health risks.
2. Support prerequisites of the active mission and milestone.
3. Prefer architecture before implementation when durable design is missing.
4. Prefer opportunities with compounding engineering leverage.
5. Strengthen high-value capability gaps.
6. Respect dependencies and sequencing.
7. Consider effort, operational burden, and opportunity cost.
8. Preserve strategic opportunities without forcing premature implementation.
9. Avoid prioritizing novelty, popularity, or product hype by itself.

Possible contextual priority bands include:

- Immediate.
- Near-term.
- Strategic.
- Exploratory.
- Deferred.

Priority should always include reasons and evidence.

---

## Evaluation Pipeline

A normal assessment should follow this sequence.

### 1. Discover

Load existing Engineering Opportunity Objects.

### 2. Validate

Confirm identifiers, required fields, lifecycle state, and repository location.

### 3. Normalize

Create a consistent internal representation without changing canonical files.

### 4. Gather Evidence

Collect related architecture, mission, capability, repository, and engineering
state evidence.

### 5. Classify Scope

Identify primary scope and secondary implications.

### 6. Compare

Evaluate relationships with existing opportunities.

### 7. Assess

Evaluate value, evidence, architecture, dependencies, effort, readiness, and
risk.

### 8. Recommend

Produce a lifecycle or next-action recommendation.

### 9. Compose

Provide the structured assessment to Engineering Intelligence.

### 10. Decide

A human engineer reviews the assessment and authorizes repository changes.

The pipeline should remain inspectable.

No stage should silently mutate opportunity state.

---

## Structured Assessment Contract

A conceptual assessment may contain:

    opportunity_id: EO-2026-007
    lifecycle_state: captured

    scope:
      primary: capability
      secondary:
        - engineering-system

    capability_alignment:
      primary: Engineering
      confidence: high

    facts:
      - source: repository-object
        statement: The object is currently captured.

    findings:
      - type: relationship
        relationship: umbrella_for
        target: EO-2026-002
        confidence: high
        basis: Explicit opportunity notes.

    evaluation:
      object_quality: sufficient
      distinctness: sufficient
      architectural_significance: high
      mission_relevance: medium
      dependency_readiness: low

    recommended_priority: strategic
    recommendation: architect
    confidence: medium

    blockers:
      - Assessment implementation does not yet exist.

    unresolved_questions:
      - Which relationships should become canonical object metadata?

    suggested_next_action:
      Define the reusable assessment data model.

This example defines conceptual meaning.

It does not require a permanent storage or serialization format.

---

## Portfolio Assessment

Opportunity Intelligence may also compare a set of opportunities.

A portfolio assessment may identify:

- Strategic and tactical clusters.
- Duplicate candidates.
- Umbrella and component relationships.
- Dependency chains.
- Capability concentration.
- Missing capability coverage.
- Mission relevance.
- High-leverage opportunities.
- Opportunities that should remain preserved but deferred.

Portfolio comparison should not collapse every opportunity into one global
numeric ranking.

Different scopes should remain distinguishable.

---

## Human Decision Boundary

A human engineer remains responsible for:

- Accepting or rejecting recommendations.
- Approving merges.
- Selecting canonical objects.
- Changing lifecycle state.
- Recording decisions.
- Selecting architecture work.
- Scheduling implementation.
- Determining whether effort is justified.

When a merge is approved:

- Stable identifiers remain historically traceable.
- The canonical target is recorded.
- The source is closed with a reason.
- Useful evidence is preserved.
- Existing references are not silently discarded.

---

## Initial Assessment Boundary

The first implementation should support:

- Existing opportunity objects.
- Identity and lifecycle validation.
- Scope classification.
- Explicit relationships.
- Strong duplicate or overlap candidates.
- Capability alignment.
- Evidence-backed recommendations.
- Confidence.
- Unresolved questions.
- Structured reusable outputs.

The first implementation should not require:

- Broad autonomous candidate discovery.
- Fully automatic semantic judgment.
- Numeric scoring.
- Permanent assessment files.
- Automatic lifecycle mutation.
- Automatic mission creation.
- Dependence on one AI provider.

---

## Design Rules

Engineering Opportunity Assessments must:

- Separate facts, findings, and recommendations.
- Reference supporting evidence.
- Expose confidence and uncertainty.
- Distinguish relationships from duplication.
- Keep priority contextual.
- Preserve human decision authority.
- Remain rebuildable from canonical evidence.
- Support multiple interfaces.
- Avoid opaque scoring.
- Avoid silently modifying opportunity objects.

---

## Non-Responsibilities

Engineering Opportunity Assessment should not:

- Replace Engineering Opportunity Objects.
- Own lifecycle state.
- Approve or reject opportunities automatically.
- Merge objects automatically.
- Replace architecture.
- Replace Engineering Interpretation.
- Replace Engineering Review.
- Replace human judgment.
- Become conversational memory.
- Require a specific AI model.
- Become an unexplainable ranking system.

---

## Completion Criteria

This architecture is considered established when:

- Assessment layers are defined.
- Scope classes are defined.
- Relationship types are defined.
- Evaluation dimensions are defined.
- Deterministic and judgment boundaries are defined.
- Confidence is defined.
- Recommendations are defined.
- Priority principles are defined.
- The evaluation pipeline is defined.
- The structured output contract is defined.
- Human decision boundaries are defined.
- Initial implementation boundaries are defined.

---

## Future Direction

Engineering Opportunity Assessment should become the shared evaluation contract
for Atlas, ChatGPT, local AI, VS Code, and future Aiden Platform interfaces.

Future improvements may include:

- Historical assessment comparison.
- Relationship graph reasoning.
- Portfolio-level analysis.
- Capability-gap analysis.
- Mission candidate assessment.
- Roadmap support.
- AI-assisted semantic comparison.
- Explainable prioritization.
- Human review and decision recording.

The long-term objective is consistent opportunity reasoning across every
engineering interface while the repository remains canonical and the human
engineer remains responsible for decisions.
