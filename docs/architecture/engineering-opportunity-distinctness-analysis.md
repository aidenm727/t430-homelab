# Engineering Opportunity Distinctness Analysis Architecture

## Purpose

Engineering Opportunity Distinctness Analysis defines how Engineering
Opportunity Intelligence compares preserved Engineering Opportunity Objects and
explains whether they appear to represent the same, overlapping, narrower,
broader, or meaningfully distinct engineering possibilities.

Its purpose is to prevent two opposite failures:

- Preserving redundant objects indefinitely when they describe the same
  underlying opportunity.
- Collapsing related but independently valuable opportunities because their
  language, capability, or scope appears similar.

Distinctness Analysis should improve repository clarity while preserving useful
engineering knowledge, uncertainty, historical traceability, and human judgment.

---

## Core Principle

Similarity is evidence for comparison.

Similarity is not proof of duplication.

Distinctness Analysis produces rebuildable comparison findings.

It does not own canonical opportunity objects, lifecycle mutation, merge
approval, closure, or deletion.

Human engineers decide whether opportunities should remain separate, be
clarified, be organized as component and umbrella work, or be merged.

---

## Architectural Position

Distinctness Analysis belongs to Engineering Opportunity Intelligence in the
Repository Reasoning layer.

    Engineering Opportunity Objects
        ↓
    Object Quality, Evidence, Relationships,
    Capability Alignment, and Scope Classification
        ↓
    Engineering Opportunity Distinctness Analysis
        ↓
    Pairwise Comparison Findings
        ↓
    Portfolio Distinctness View
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

Distinctness Analysis owns comparison reasoning.

Engineering Opportunity Assessment consumes distinctness findings.

Engineering Intelligence may compose those findings with mission, readiness,
risk, and other evidence.

Engineering Interpretation decides what action is currently responsible.

Engineering Review presents recommendations.

Human-authorized repository workflows own mutation.

---

## Relationship to Explicit Opportunity Relationships

The existing Engineering Opportunity Relationship foundation evaluates explicit
repository declarations such as:

- `depends_on`
- `enables`
- `related_to`

Distinctness Analysis is different.

Explicit Relationship reasoning asks:

    What relationships has the repository already declared?

Distinctness Analysis asks:

    What comparison relationships are supported or suggested by current
    repository evidence?

An explicit `related_to` declaration may justify comparing two opportunities.

It does not establish duplication, overlap, component, or umbrella status.

An explicit dependency normally supports distinctness because the source and
target play different roles, but it does not make duplication impossible.

Distinctness findings should reuse explicit relationship evidence rather than
reimplement relationship validation.

---

## Relationship to Capability Alignment

Capability Alignment identifies which durable Platform Capability an
opportunity would strengthen.

Capability alignment may support comparison:

- The same resolved capability can increase comparison relevance.
- Different resolved capabilities can provide boundary or counterevidence.
- Ambiguous or unknown alignment reduces confidence.
- One broad cross-capability opportunity may contain narrower
  capability-specific components.

Capability identity alone can never establish duplication.

Two opportunities can strengthen the same capability while representing
different outcomes.

Different capability alignment does not automatically prove distinctness when
one object is broader or the alignment itself is unresolved.

---

## Relationship to Scope Classification

Scope Classification identifies the kind of engineering change represented by
an opportunity.

Scope may constrain comparison:

- Opportunities with compatible primary scopes are easier to compare directly.
- Strongly different resolved scopes may provide boundary evidence.
- A broader Strategic Direction or Capability Opportunity may organize narrower
  Architecture, Engineering System, Implementation, or Operational
  opportunities.
- Candidate, ambiguous, mixed, or insufficient scope classifications should
  reduce comparison confidence.

Scope identity alone can never establish duplication or overlap.

A component and its umbrella are expected to have related but potentially
different scopes.

Distinctness Analysis must consume Scope Classification rather than recreate it.

---

## Comparison Identity

The canonical pairwise comparison identity is an unordered pair of stable
Engineering Opportunity identifiers.

A deterministic pair key should order the two identifiers lexicographically:

    pair_key = min(opportunity_a_id, opportunity_b_id)
               + "::"
               + max(opportunity_a_id, opportunity_b_id)

This ensures that:

- `EO-A` compared with `EO-B` is the same pair as `EO-B` compared with `EO-A`.
- Portfolio analysis does not emit duplicate symmetric comparisons.
- Evidence can be composed once per pair.
- Directional findings can still identify source and target roles.

An opportunity must never be compared with itself.

Pairwise comparison identity remains stable even when titles, summaries,
lifecycle states, or repository paths change.

---

## Pairwise Analysis Model

Pairwise analysis compares exactly two Engineering Opportunity Objects.

A normal pairwise analysis should:

1. Validate that the objects have different stable identifiers.
2. Gather deterministic repository facts for both objects.
3. Gather explicit relationship and reference evidence.
4. Consume Capability Alignment for both objects.
5. Consume Scope Classification for both objects.
6. Normalize bounded text fields for transparent heuristic comparison.
7. Identify supporting evidence.
8. Identify counterevidence and boundary evidence.
9. Determine whether one or more relationship candidates are justified.
10. Expose uncertainty and confidence.
11. Produce a bounded recommendation without mutating either object.

Pairwise analysis should remain reusable independently of Atlas command
rendering.

---

## Portfolio Composition

Portfolio Distinctness Analysis composes pairwise results across a discovered
opportunity inventory.

For `n` opportunities, the maximum unordered comparison set is:

    n × (n - 1) / 2

Initial implementations may reduce unnecessary comparisons using transparent
gates, but they must not silently omit potentially relevant pairs without
exposing the gate.

Portfolio composition should:

- Produce each unordered pair at most once.
- Preserve directional component and umbrella findings inside the pair result.
- Avoid contradictory duplicate emissions.
- Group findings by opportunity identifier for assessment integration.
- Preserve pair-level evidence and confidence.
- Expose comparison counts and skipped-pair reasons.
- Remain deterministic for the same repository state and policy version.

Portfolio composition does not determine portfolio priority.

---

## Distinctness Outcomes

Distinctness Analysis may produce the following relationship outcomes.

### Duplicate Of

Two objects appear to describe the same underlying engineering possibility such
that preserving both as independent active opportunities adds little or no
distinct value.

A duplicate finding should explain:

- The shared central outcome.
- Why differences are representational rather than substantive.
- What evidence would be preserved in a merge.
- Which object is the proposed canonical target, if one can be responsibly
  proposed.
- What uncertainty remains.

Duplicate similarity is semantically symmetric at the pair level.

A proposed canonical target creates a directional recommendation, not a
directional truth about the underlying similarity.

### Overlaps With

Two opportunities share meaningful engineering scope, evidence, outcomes, or
implementation surface while remaining independently valuable.

Overlap should be preferred over duplication when:

- Each object has a distinct central outcome.
- Each can be completed independently.
- One may proceed without fully satisfying the other.
- Separate lifecycle decisions remain useful.
- The shared surface should be coordinated rather than merged.

Overlap is symmetric.

Overlap alone is not a reason to merge.

### Component Of

A narrower opportunity contributes materially to fulfilling a broader
opportunity but does not represent the same possibility.

The narrower object remains independently useful because it has a bounded
outcome, lifecycle, or verification boundary.

`component_of` is directional:

    narrower component
        component_of
    broader umbrella

### Umbrella For

A broader opportunity organizes, motivates, or is fulfilled through one or more
narrower component opportunities.

`umbrella_for` is the inverse of `component_of`:

    broader umbrella
        umbrella_for
    narrower component

A portfolio should not emit only one direction while hiding the inverse
relationship.

### Distinct From

Two opportunities have enough comparison evidence to explain that they should
remain separate despite some superficial or contextual similarity.

A distinct finding should identify the boundary, such as:

- Different central outcomes.
- Different completion conditions.
- Different lifecycle decisions.
- Different operational subjects.
- Different architecture ownership.
- Explicit dependency roles.
- Strongly incompatible resolved scopes.
- Evidence that one can be completed without satisfying the other.

`distinct_from` is symmetric.

Distinctness is not proof that the opportunities are unrelated.

### Insufficient Evidence

The repository does not contain enough evidence to produce a responsible
duplicate, overlap, component, umbrella, or distinct candidate.

Insufficient evidence should explain:

- Which comparison facts were available.
- Which evidence was missing.
- Whether clarification, references, or human review would improve the result.

Insufficient evidence is a valid result, not a reasoning failure.

---

## Directionality and Inverse Semantics

Pair identity is unordered, but some findings are directional.

The architecture defines:

| Relationship | Symmetry | Inverse |
| --- | --- | --- |
| `duplicate_of` | Pair-symmetric similarity; target proposal is directional | `duplicate_of` |
| `overlaps_with` | Symmetric | `overlaps_with` |
| `component_of` | Directional | `umbrella_for` |
| `umbrella_for` | Directional | `component_of` |
| `distinct_from` | Symmetric | `distinct_from` |
| `insufficient_evidence` | Pair-level state | `insufficient_evidence` |

A pairwise result should store the canonical unordered pair and represent
directional source and target roles explicitly.

A portfolio view may expose inverse findings for convenient per-opportunity
consumption, but both views must derive from one canonical pair result.

---

## Duplicate and Overlap Boundaries

Duplicate and overlap findings must be separated deliberately.

A duplicate candidate requires evidence that both objects share substantially
the same central outcome and completion condition.

An overlap candidate requires evidence that the objects share meaningful surface
while retaining independently useful outcomes.

Evidence supporting duplication may include:

- Equivalent central outcomes stated in different language.
- Equivalent completion conditions.
- Equivalent affected system boundaries.
- The same narrow capability and scope with no substantive boundary evidence.
- Human-reviewed evidence that one object restates another.
- One object preserving no unique rationale, evidence, relationship, or
  deliverable after comparison.

Evidence supporting overlap instead may include:

- Shared terminology with different completion conditions.
- Shared architecture with different implementation or operational outcomes.
- Shared capability with different primary scopes.
- Shared evidence addressing different causes or interventions.
- Coordination value without merge value.
- Each object enabling separate lifecycle or scheduling decisions.

Keyword, token, embedding, or title similarity alone is never sufficient for a
duplicate finding.

When duplicate and overlap interpretations are both plausible, the result should
be ambiguous and recommend human review.

---

## Component and Umbrella Boundaries

Component and umbrella findings describe decomposition rather than redundancy.

A component candidate should have:

- A narrower central outcome.
- A completion condition that advances but does not fully satisfy the broader
  opportunity.
- A meaningful independent verification or lifecycle boundary.
- Evidence that the broader opportunity remains incomplete after the component
  is completed.

An umbrella candidate should have:

- A broader outcome that organizes several possible components.
- A completion condition that cannot be satisfied by one narrow change alone.
- Evidence spanning several capabilities, scopes, systems, or engineering
  checkpoints.

Breadth alone does not prove umbrella status.

A long document is not necessarily broader.

An older opportunity is not necessarily an umbrella.

A component and umbrella should not be marked duplicates merely because their
language overlaps heavily.

---

## Explicit Relationship and Reference Evidence

Distinctness Analysis may consume:

- Explicit dependencies.
- Explicit related opportunities.
- Existing typed relationship findings.
- Related architecture documents.
- Related infrastructure, operations, roadmap, or standards documents.
- Shared evidence references.
- Recorded human decisions.
- Lifecycle state.
- Repository paths and stable identifiers.

Evidence roles include:

### Supporting Comparison Evidence

- An explicit `related_to` declaration.
- Shared related documents.
- Shared evidence references.
- Shared dependency targets.
- Shared resolved capability.
- Compatible scope classifications.

### Boundary or Counterevidence

- One opportunity explicitly depends on the other.
- Different authoritative architecture ownership.
- Different resolved capabilities.
- Strongly different resolved scopes.
- Different operational systems or verification boundaries.
- Unique evidence that materially changes the central outcome.

Explicit relationships should influence comparison but never be silently
reclassified into stronger relationships.

---

## Capability-Aware Comparison

Capability comparison should expose:

- Declared raw capability values.
- Capability Alignment state.
- Resolved primary capability identifiers.
- Candidate capability identifiers.
- Alignment confidence and unresolved questions.

The initial design rules are:

- Same resolved capability: supporting context only.
- Different resolved capabilities: boundary evidence, not automatic
  distinctness.
- Ambiguous or unknown capability: comparison uncertainty.
- Broad and narrow capability relationships: possible component or umbrella
  evidence requiring semantic review.
- Capability aliases: compare canonical identifiers, not raw labels.

Distinctness Analysis must not mutate Capability Alignment.

---

## Scope-Aware Comparison

Scope comparison should expose:

- Classification state.
- Resolved primary scope, if available.
- Leading and alternative candidates.
- Secondary implications.
- Confidence and unresolved questions.

The initial design rules are:

- Same resolved primary scope: supporting context only.
- Different resolved primary scopes: boundary evidence unless component or
  umbrella interpretation explains the difference.
- Candidate or ambiguous scope: lower-confidence comparison.
- Mixed scope: possible object-boundary problem that may affect distinctness.
- Insufficient scope evidence: comparison uncertainty.
- Scope similarity: never automatic duplication.

Distinctness Analysis must not resolve or mutate Scope Classification.

---

## Text Normalization and Heuristic Boundaries

Text comparison may inspect:

- Title.
- Summary.
- Rationale.
- Evidence items.
- Notes.

A bounded normalization policy may include:

- Unicode normalization.
- Case folding.
- Whitespace normalization.
- Punctuation separation.
- Transparent stop-word handling.
- Stable tokenization.
- Exact phrase and token-set comparison.
- Field-aware provenance.

Every normalized signal should remain explainable.

The implementation should preserve:

- Which source fields contributed.
- Which normalized terms or phrases matched.
- Which important terms differed.
- Which policy version produced the signal.

The implementation must not:

- Treat one matching keyword as duplication.
- Hide an opaque similarity score.
- Use model embeddings as repository truth.
- Discard field provenance.
- Treat longer shared boilerplate as stronger evidence than central-outcome
  language.
- Infer canonical decisions from title similarity.

Future AI-assisted semantic review may consume normalized evidence, but its
judgment must remain labeled as interpretation.

---

## Evidence, Counterevidence, and Provenance

Every pairwise result should separate:

### Repository Facts

Directly observable information for each object.

### Supporting Evidence

Evidence favoring one or more relationship candidates.

### Counterevidence

Evidence weakening a relationship candidate.

### Boundary Evidence

Evidence explaining why two opportunities remain independently valuable.

### Provenance

Sources and reasoning policies used to produce the comparison.

Minimum provenance includes:

- Pair key.
- Both opportunity identifiers and paths.
- Capability Alignment sources.
- Scope Classification sources.
- Relationship findings used.
- Related documents and evidence references used.
- Text fields and normalization rules used.
- Human-reviewed decision sources, when applicable.
- Reasoning module or policy version when practical.

A finding without provenance is incomplete.

Counterevidence must not be suppressed merely because supporting evidence is
strong.

---

## Negative and Boundary Evidence

Distinctness Analysis must reason about why opportunities are different, not
only why they are similar.

Boundary evidence may include:

- Different central verbs or intended outcomes.
- Different completion criteria.
- Different affected systems.
- Different responsible capability areas.
- Different resolved scopes.
- One opportunity depending on the other.
- One opportunity remaining valuable after the other is completed.
- Unique architecture or operational references.
- Unique evidence and rationale.
- Human-reviewed decisions to retain both separately.

Absence of similarity is not automatically strong distinctness evidence.

A `distinct_from` candidate requires an explainable positive boundary.

---

## Analysis States and Confidence

Each pairwise analysis has one analysis state.

### Resolved

A human-reviewed decision or unambiguous repository contract establishes the
relationship with little reasonable ambiguity.

High-confidence duplicate resolution requires human-reviewed evidence.

### Candidate

One relationship interpretation is supported strongly enough to surface for
review but is not canonical truth.

### Ambiguous

Two or more relationship interpretations remain plausible.

Common examples include:

- Duplicate versus overlap.
- Overlap versus component.
- Component direction is unclear.
- Distinct versus insufficient evidence.

### Insufficient Evidence

The available repository evidence does not support a responsible relationship
candidate.

### Conflicting

Explicit human-reviewed or repository-owned decisions disagree.

Confidence applies to each finding and should be explained.

#### High Confidence

The finding follows from explicit human-reviewed evidence or an unambiguous
repository contract.

#### Medium Confidence

Several independent signals support the finding, but semantic review remains
necessary.

#### Low Confidence

The finding is tentative, evidence is sparse, or alternatives remain plausible.

Opaque numeric thresholds should not replace explained evidence.

---

## Canonical Target Candidates

A duplicate candidate may propose a canonical target.

Canonical-target selection is a recommendation, not a mutation.

Possible supporting factors include:

- A human-reviewed canonical decision.
- Clearer and more complete summary and rationale.
- Stronger preserved evidence.
- More accurate relationships and references.
- More mature lifecycle state when that maturity is valid.
- Broader historical continuity.
- Explicit architecture ownership.
- A stable object already referenced by other repository records.

The following factors are insufficient alone:

- Lower numeric identifier.
- Earlier creation date.
- Longer text.
- More related documents.
- More advanced lifecycle state.
- Lexical similarity.

When no target is clearly preferable, the result should omit a canonical target
and recommend human selection.

A canonical target proposal must explain what information from the other object
would need preservation.

---

## Structured Assessment Contracts

Distinctness Analysis should define reusable pairwise and portfolio outputs.

A candidate pairwise model may resemble:

    OpportunityDistinctnessComparison
        pair_key
        left_opportunity_id
        left_repository_path
        right_opportunity_id
        right_repository_path
        analysis_state
        relationship_type
        source_opportunity_id
        target_opportunity_id
        canonical_target_candidate_id
        alternative_relationship_types
        facts
        supporting_evidence
        counterevidence
        boundary_evidence
        provenance
        explanation
        confidence
        blockers
        unresolved_questions
        recommendation

A candidate portfolio model may resemble:

    OpportunityDistinctnessPortfolio
        opportunity_ids
        comparison_count
        skipped_pair_count
        comparisons
        findings_by_opportunity
        duplicate_candidates
        overlap_candidates
        component_candidates
        ambiguous_comparisons
        insufficient_evidence_comparisons
        provenance

The exact implementation may evolve.

The architecture requires:

- One canonical pair result per unordered pair.
- Explicit source and target for directional findings.
- Separate supporting, counter, and boundary evidence.
- Confidence and unresolved questions.
- No embedded repository mutation.

---

## Engineering Opportunity Assessment Integration

Engineering Opportunity Assessment should consume reusable distinctness results.

Per-opportunity assessment integration may expose:

- Duplicate candidates involving the opportunity.
- Overlap candidates.
- Component and umbrella candidates.
- Distinctness findings.
- Ambiguous comparisons.
- Insufficient-evidence comparisons relevant to review.
- Canonical-target candidates.
- Recommendations and unresolved questions.

Assessment integration should not independently compare opportunity content.

Portfolio comparison should occur once and be distributed to assessments by
stable identifier.

Distinctness findings should remain separate from explicit relationship findings
while being composable with them.

---

## Recommendation Effects

Distinctness Analysis may recommend:

- Retain both opportunities separately.
- Clarify the boundary between opportunities.
- Record an explicit overlap relationship.
- Review a component and umbrella relationship.
- Select a canonical target.
- Merge evidence into a canonical target.
- Close a source as duplicate while preserving history.
- Split a mixed opportunity.
- Enrich evidence before comparison.
- Record a human-reviewed decision.

A recommendation does not:

- Merge objects.
- Move files.
- Change lifecycle state.
- Delete an identifier.
- Rewrite references.
- Select architecture work.
- Schedule implementation.
- Establish priority.

---

## Human Authority and Historical Traceability

Distinctness Analysis does not own canonical mutation.

A human-authorized workflow remains responsible for:

- Approving duplicate status.
- Selecting a canonical target.
- Approving component and umbrella relationships.
- Clarifying object boundaries.
- Merging evidence and notes.
- Updating references.
- Moving lifecycle directories.
- Closing an object.
- Recording a merge or duplicate reason.

When opportunities are merged or one is closed as duplicate:

- Every stable identifier must remain historically traceable.
- The canonical target must be explicit.
- The source object must retain a closure or merge reason.
- Useful evidence, rationale, and notes must be preserved.
- References must be migrated or intentionally retained.
- The repository must not silently delete the source history.

Human decisions should be represented as canonical repository evidence that
future analysis can consume.

---

## Initial Implementation Boundary

The first implementation should establish a safe, transparent comparison
foundation.

It should:

- Define reusable pairwise and portfolio result models.
- Build deterministic unordered pair identities.
- Reject self-comparison.
- Gather object, relationship, capability, scope, document, and evidence facts.
- Normalize bounded text fields transparently.
- Produce explainable exact and token-based heuristic signals.
- Expose supporting, counter, and boundary evidence.
- Produce candidate, ambiguous, distinct, and insufficient-evidence results.
- Support component and umbrella directionality.
- Reserve resolved duplicate findings for explicit human-reviewed evidence.
- Allow canonical-target candidates only when evidence is explained.
- Compose one result per unordered pair.
- Attach portfolio findings to Engineering Opportunity Assessments.
- Preserve canonical objects and lifecycle state.
- Remain independent of Atlas command rendering and language models.

The first implementation should not:

- Automatically merge or close objects.
- Produce resolved semantic duplicates from heuristics.
- Use keyword similarity alone.
- Depend on embeddings or a language model.
- Introduce an opaque numeric ranking.
- Compare every pair without an explainable gate when the portfolio becomes
  large.
- Rewrite explicit relationships.
- Select portfolio priority.
- Evaluate strategic value.
- Mutate lifecycle state.
- Add command-specific comparison logic.
- Store permanent derived comparison artifacts prematurely.

---

## Verification Cases

The initial implementation should test:

- Pair keys are stable and order-independent.
- Self-comparison is rejected.
- Portfolio composition emits each unordered pair once.
- Duplicate similarity remains pair-symmetric.
- Canonical-target proposals remain directional recommendations.
- Overlap is symmetric and does not recommend automatic merge.
- Component and umbrella are directional inverses.
- Same capability alone cannot establish duplication.
- Different capabilities provide counterevidence without automatic
  distinctness.
- Same scope alone cannot establish duplication.
- Different scopes provide boundary evidence while permitting component or
  umbrella interpretation.
- Explicit `related_to` triggers comparison but not a stronger relationship.
- Explicit dependency provides boundary evidence.
- Shared architecture documents support comparison but do not establish
  duplication.
- One matching keyword produces insufficient evidence.
- Transparent multi-field similarity can produce a candidate.
- Strong boundary evidence can produce a distinct candidate.
- Duplicate versus overlap uncertainty produces an ambiguous result.
- Human-reviewed evidence can resolve a duplicate with high confidence.
- Conflicting human-reviewed evidence produces a conflicting result.
- Canonical-target selection explains evidence and may remain unset.
- Source object identity and lifecycle state remain unchanged.
- Pairwise results attach to portfolio and opportunity assessments without
  duplicated comparison logic.
- No Atlas command contains independent distinctness logic.

---

## Non-Responsibilities

Distinctness Analysis should not:

- Own Engineering Opportunity Objects.
- Replace explicit relationship validation.
- Replace Capability Alignment.
- Replace Scope Classification.
- Determine priority.
- Estimate effort.
- Decide mission relevance.
- Evaluate full architectural significance.
- Automatically merge, close, or delete objects.
- Erase stable identifiers.
- Become an opaque similarity engine.
- Depend on a specific AI model.
- Become command-specific logic.

---

## Architecture Completion Criteria

This architecture is considered designed when it defines:

- Architectural purpose and ownership.
- Comparison identity.
- Pairwise analysis.
- Portfolio composition.
- Supported distinctness outcomes.
- Directionality and inverse semantics.
- Duplicate and overlap boundaries.
- Component and umbrella boundaries.
- Explicit relationship and reference evidence.
- Capability-aware and scope-aware comparison.
- Text normalization and heuristic boundaries.
- Supporting, counter, boundary, and provenance evidence.
- Negative and distinctness evidence.
- Analysis states and confidence.
- Canonical-target candidate behavior.
- Structured pairwise and portfolio contracts.
- Assessment integration.
- Recommendation effects.
- Human authority and historical traceability.
- Initial implementation boundaries.
- Verification cases.

---

## Future Direction

Distinctness Analysis may later evolve through:

- Human-reviewed comparison example sets.
- Repository-owned comparison policies.
- Bounded AI-assisted semantic review.
- Scope-aware and capability-aware comparison gates.
- Incremental portfolio recomputation.
- Explicit merge and closure workflows.
- Reference migration assistance.
- Distinctness-aware Engineering Intelligence.
- Engineering Review presentation of comparison candidates.

Future automation should make repository knowledge clearer without hiding
uncertainty or replacing human control.
