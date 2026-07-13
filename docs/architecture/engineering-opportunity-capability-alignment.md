# Engineering Opportunity Capability Alignment Architecture

## Purpose

Engineering Opportunity Capability Alignment defines how Engineering Opportunity Intelligence interprets an opportunity's declared `capability` value against the canonical Platform Capability Map.

Its purpose is to make capability reasoning explicit, evidence-backed, stable, and safe before Atlas begins validating or recommending changes to opportunity capability values.

---

## Core Principle

Capability alignment is derived reasoning over a declared repository fact.

The opportunity object preserves what was declared.

The capability map defines canonical platform capability identity.

Engineering Opportunity Intelligence explains whether the declared value resolves cleanly, requires compatibility handling, remains ambiguous, or needs human review.

No alignment result silently rewrites the canonical opportunity object.

---

## Architectural Position

Capability alignment belongs to Engineering Opportunity Intelligence in the Repository Reasoning layer.

    Platform Capability Map
        ↓
    Capability Identity Catalog
        ↓
    Engineering Opportunity Object
        ↓
    Capability Alignment Assessment
        ↓
    Engineering Opportunity Assessment
        ↓
    Engineering Intelligence
        ↓
    Engineering Interpretation
        ↓
    Engineering Review
        ↓
    Human Decision

The capability map owns capability identity.

The opportunity object owns its declared value.

Capability Alignment produces a rebuildable interpretation of the relationship between them.

---

## Canonical Capability Source

`docs/architecture/capabilities.md` is the canonical source of truth for Platform Capability identity.

Each canonical capability has:

- A stable machine-readable identifier.
- A human-readable label.
- A documented purpose and boundary.

Stable identifiers should change only through an explicit architecture decision.

Human-readable labels may evolve without changing identity.

Document metadata fields that also use the word `capability` are not automatically governed by this contract. Their vocabularies currently include values such as `Platform`, `Engineering Workflow`, and `Artificial Intelligence`. Those values must not be treated as Engineering Opportunity capability identifiers unless a later architecture explicitly unifies the vocabularies.

---

## Capability Identity Model

Canonical capability identity consists of a stable identifier and a display label.

The initial canonical identifiers are:

| Capability ID | Display Label |
| --- | --- |
| `compute` | Compute |
| `storage` | Storage |
| `networking-access` | Networking and Access |
| `observability` | Observability |
| `automation` | Automation |
| `knowledge-documentation` | Knowledge and Documentation |
| `engineering` | Engineering |
| `personal-services` | Personal Services |
| `ai-aiden-os` | AI and Aiden OS |

The identifier is the durable identity.

The label is presentation.

Aliases are compatibility rules, not additional capability identities.

---

## Opportunity Capability Semantics

### Declared Capability

The `capability` field on an Engineering Opportunity Object is a declared repository fact.

It records the capability identity or legacy capability value selected when the opportunity was captured.

The declared value should remain visible in assessments even when it is unknown, ambiguous, deprecated, or mapped through an alias.

### Primary Capability

Every opportunity should resolve to no more than one primary canonical capability.

A resolved primary capability means that the opportunity's central intended improvement belongs to that capability.

An unresolved primary capability does not make the object unloadable or erase the opportunity. It should produce an explicit finding and may block lifecycle progression until a human resolves the ambiguity.

New opportunity objects should eventually prefer canonical capability identifiers once migration is approved.

### Secondary and Cross-Capability Alignment

An opportunity may strengthen additional capabilities beyond its primary capability.

Secondary capability alignment is derived assessment output. It is not inferred from the single `capability` field alone and is not part of the initial deterministic implementation.

Future secondary alignment may use explicit architecture, related documents, typed opportunity relationships, or human-reviewed semantic evidence.

Secondary alignment must include evidence, confidence, and provenance. It must never silently replace the primary capability.

---

## Compatibility and Migration

Existing opportunity values must remain readable while the repository transitions toward stable capability identifiers.

Compatibility handling should preserve the raw declared value and produce one of the defined alignment states.

The current inventory is:

| Declared Value | Deterministic Interpretation | Initial Status | Required Handling |
| --- | --- | --- | --- |
| `Engineering` | Canonical label for `engineering` | `canonical-label` | Resolve with high confidence; no automatic rewrite. |
| `AI` | Curated one-to-one alias for `ai-aiden-os` | `alias` | Resolve with high confidence and expose the alias rule. |
| `Documentation` | Curated one-to-one alias for `knowledge-documentation` | `alias` | Resolve with high confidence and expose the alias rule. |
| `Infrastructure` | Broad legacy domain spanning several canonical capabilities | `ambiguous` | Preserve the value, expose candidate capabilities, and require human selection of a primary capability. |
| `Learning` | No current canonical capability identity | `unknown` | Preserve the value and require a decision to reclassify the opportunity or evolve the capability map. |

`Infrastructure` must not be collapsed automatically because it may refer to Compute, Storage, Networking and Access, Observability, Automation, or a combination of them.

`Learning` must not be mapped automatically to AI and Aiden OS, Engineering, or Personal Services merely because those capabilities may support learning workflows.

Migration should follow:

    Assess Existing Value
        ↓
    Explain Alignment State
        ↓
    Human Review
        ↓
    Approve Canonical Identifier
        ↓
    Update Object in a Separate Repository Change
        ↓
    Verify and Preserve Git History

No design or reasoning path owns automatic migration.

---

## Alignment States

Capability alignment should use explicit states.

### Canonical ID

The declared value exactly matches a canonical capability identifier.

Confidence is high.

### Canonical Label

The declared value exactly matches the display label of one canonical capability.

Confidence is high, but migration to the stable identifier may still be recommended.

### Alias

The declared value matches a curated one-to-one compatibility alias.

Confidence is high when the alias rule is explicit and versioned.

### Ambiguous

The declared value plausibly refers to multiple canonical capabilities.

No primary capability is resolved automatically.

Candidate capabilities and the reason for ambiguity should be exposed.

### Unknown

The declared value matches no canonical identifier, label, alias, or recognized broad compatibility value.

The unknown detection is deterministic. The correct replacement remains a human judgment.

### Deprecated

The declared value was previously accepted but has an explicit replacement or retirement rule.

The assessment should expose the replacement and migration evidence without mutating the object.

### Conflicting

Multiple explicit repository facts imply incompatible primary capability identities.

The conflict should be reported rather than normalized away.

---

## Evidence and Provenance

Every capability-alignment assessment should identify its evidence sources.

Minimum provenance includes:

- The opportunity object path.
- The raw declared `capability` value.
- The canonical capability definition source.
- The identifier, label, alias, ambiguity, or deprecation rule used.
- Any candidate capability identifiers.
- The reasoning implementation or catalog version when practical.

Title, summary, rationale, notes, and keyword similarity are not deterministic capability evidence in the initial implementation.

They may support later human or AI-assisted review only when clearly separated from deterministic results.

---

## Structured Assessment Contract

Capability Alignment should produce a reusable structured result containing:

- Opportunity identifier.
- Opportunity repository path.
- Raw declared capability value.
- Alignment state.
- Resolved primary capability identifier, when available.
- Resolved display label, when available.
- Candidate capability identifiers for ambiguous values.
- Secondary capability identifiers, when explicitly supported in a later phase.
- Supporting evidence.
- Provenance.
- Explanation.
- Confidence.
- Blockers.
- Unresolved questions.
- A bounded recommendation.

A candidate Python model may resemble:

    OpportunityCapabilityAlignment
        opportunity_id
        repository_path
        declared_value
        alignment_state
        primary_capability_id
        primary_capability_label
        candidate_capability_ids
        secondary_capability_ids
        evidence
        provenance
        explanation
        confidence
        blockers
        unresolved_questions
        recommendation

The exact implementation may evolve, but the separation between declared facts, derived alignment, and recommended action must remain.

---

## Deterministic and Judgment Boundaries

The following behavior is deterministic:

- Reading the declared capability value.
- Reading canonical capability identifiers and labels.
- Exact identifier matching.
- Exact label matching.
- Applying a curated one-to-one alias.
- Identifying a curated broad ambiguous value.
- Identifying an unknown value.
- Identifying a deprecated value with an explicit rule.
- Reporting conflicting explicit inputs.
- Producing source-backed findings.

The following behavior requires human or explicitly bounded AI-assisted judgment:

- Inferring capability from natural-language opportunity content.
- Selecting one primary capability from an ambiguous broad domain.
- Deciding whether the capability map should gain a new capability.
- Determining secondary capability alignment.
- Resolving cross-capability strategic direction.
- Approving migration of canonical objects.

Deterministic reasoning must not pretend that semantic classification is already solved.

---

## Human Authority and Lifecycle Mutation

Capability alignment does not own object mutation or lifecycle progression.

A human-authorized workflow remains responsible for:

- Changing the declared capability value.
- Migrating a legacy label or alias to a canonical identifier.
- Selecting a primary capability for an ambiguous opportunity.
- Adding or retiring canonical capabilities.
- Approving secondary capability metadata if it later becomes canonical.
- Advancing an opportunity lifecycle state.

A capability-alignment recommendation is not a repository mutation.

---

## Relationship to Existing Reasoning

Engineering Opportunity Assessment should consume Capability Alignment rather than reimplement it.

Engineering Opportunity Intelligence may combine capability alignment with:

- Object quality.
- Evidence strength.
- Typed opportunity relationships.
- Scope classification.
- Architectural significance.
- Dependency readiness.
- Mission relevance.

Engineering Intelligence may later compose capability-alignment findings with platform maturity and active mission state.

Engineering Interpretation decides whether a capability issue should block progression or become the next responsible checkpoint.

Atlas commands remain presentation layers.

---

## Initial Implementation Boundary

The first implementation should:

- Build a bounded canonical capability catalog from repository-owned architecture.
- Preserve raw declared capability values.
- Match canonical identifiers exactly.
- Match canonical labels exactly.
- Apply the curated `AI` and `Documentation` aliases.
- Report `Infrastructure` as ambiguous with explicit candidate capabilities.
- Report `Learning` and other unsupported values as unknown.
- Produce the structured Capability Alignment result.
- Attach the result to reusable Engineering Opportunity Assessments.
- Include evidence, provenance, explanation, confidence, blockers, and unresolved questions.
- Preserve human lifecycle and migration authority.

The first implementation should not:

- Infer capability from titles, summaries, rationale, evidence, or notes.
- Determine secondary capability alignment.
- Rewrite opportunity objects.
- Add or remove canonical capabilities.
- Rank opportunities.
- Perform duplicate detection.
- Move reasoning into an Atlas command.
- Depend on a language model.

---

## Verification Cases

The initial implementation should test:

- Exact canonical identifier resolution.
- Exact canonical label resolution.
- One-to-one alias resolution for `AI`.
- One-to-one alias resolution for `Documentation`.
- Ambiguous broad-domain handling for `Infrastructure`.
- Unknown-value handling for `Learning`.
- Unknown-value handling for an arbitrary unsupported string.
- Deprecated-value handling when a rule exists.
- Conflicting explicit capability inputs when supported by the object model.
- Preservation of the raw declared value.
- Assessment behavior for an unresolved capability.
- No automatic object mutation.
- No semantic inference from opportunity prose.

---

## Non-Responsibilities

Capability Alignment should not:

- Replace the Platform Capability Map.
- Redefine document metadata capability semantics.
- Infer opportunity scope.
- Detect duplicate opportunities.
- Determine portfolio priority.
- Rewrite canonical opportunity objects.
- Add capabilities without architecture review.
- Advance lifecycle state.
- Replace human architectural judgment.
- Become an opaque classification score.

---

## Architecture Completion Criteria

This architecture is considered designed when it defines:

- Canonical capability ownership.
- Stable capability identity.
- Primary capability semantics.
- Secondary and cross-capability boundaries.
- Compatibility and migration rules.
- Current legacy-value handling.
- Alignment states.
- Evidence and provenance.
- Structured assessment output.
- Deterministic and judgment boundaries.
- Human mutation authority.
- Initial implementation scope.
- Verification cases.

---

## Future Direction

Capability Alignment should eventually help Atlas explain how potential work strengthens the platform without collapsing nuanced engineering judgment into labels.

Later evolution may include:

- A machine-readable capability registry derived from canonical architecture.
- Secondary capability alignment based on explicit evidence.
- Capability maturity correlation.
- Mission and roadmap alignment.
- Capability-gap analysis.
- Human-reviewed semantic classification assistance.

These improvements should build on stable capability identity and transparent evidence rather than replacing them.
