# Engineering Opportunity Capability Alignment Architecture

## Purpose

Engineering Opportunity Capability Alignment defines how Engineering Opportunity Intelligence interprets an opportunity's declared `capability` value against the canonical Platform Capability Architecture.

Its purpose is to preserve repository facts while producing explicit, evidence-backed compatibility and migration guidance.

No alignment result silently rewrites an Engineering Opportunity Object.

---

## Core Principle

Capability alignment is derived reasoning over a declared repository fact.

- The opportunity object owns its declared value.
- `docs/architecture/capabilities.md` owns canonical capability identity.
- Capability Alignment explains whether the value is canonical, compatible, deprecated, ambiguous, or unknown.
- Human review owns object migration and lifecycle mutation.

---

## Canonical Capability Source

`docs/architecture/capabilities.md` is the canonical source of Platform Foundation and Human Agency Domain identities.

The current canonical identifiers are:

| Capability ID | Display Label |
| --- | --- |
| `platform-governance` | Platform Direction and Governance |
| `engineering-evolution` | Engineering and Evolution |
| `knowledge-context` | Knowledge and Context |
| `artificial-intelligence` | Artificial Intelligence |
| `automation-integration` | Automation and Integration |
| `infrastructure-operations` | Infrastructure and Operations |
| `security-privacy-resilience` | Security, Privacy, and Resilience |
| `interaction-experience` | Interaction and Experience |
| `learning-research` | Learning and Research |
| `health-wellbeing` | Health and Wellbeing |
| `economic-agency` | Economic Agency |
| `personal-operations` | Personal Operations |
| `creativity-expression` | Creativity and Expression |

Stable identifiers change only through explicit architecture decisions.

Display labels may evolve without changing identity.

Document metadata vocabularies remain separate unless future architecture explicitly unifies them.

---

## Opportunity Capability Semantics

The `capability` field is a declared repository fact.

Existing values remain visible even when they are aliases, deprecated identifiers, ambiguous combined identities, or unknown.

An opportunity may resolve to no more than one primary canonical capability.

Ambiguous legacy values may expose multiple candidates without selecting one automatically.

Secondary capability alignment remains future derived work requiring explicit evidence.

It is not inferred from prose or from a broad legacy value alone.

---

## Compatibility Model

The capability architecture replaced a flat nine-capability model with layered Platform Foundations and Human Agency Domains.

Existing opportunity objects remain readable during migration.

### Current Human-Readable Values

| Declared Value | Deterministic Interpretation | State |
| --- | --- | --- |
| `Engineering` | `engineering-evolution` | `alias` |
| `AI` | `artificial-intelligence` | `alias` |
| `Documentation` | `knowledge-context` | `alias` |
| `Infrastructure` | `infrastructure-operations` | `alias` |
| `Learning` | `learning-research` | `alias` |
| `Compute` | `infrastructure-operations` | `alias` |
| `Storage` | `infrastructure-operations` | `alias` |
| `Observability` | `infrastructure-operations` | `alias` |
| `Automation` | `automation-integration` | `alias` |

### Deprecated One-to-One Identifiers

| Legacy ID | Replacement |
| --- | --- |
| `compute` | `infrastructure-operations` |
| `storage` | `infrastructure-operations` |
| `observability` | `infrastructure-operations` |
| `automation` | `automation-integration` |
| `engineering` | `engineering-evolution` |

### Ambiguous Combined Identities

| Legacy Value | Candidates |
| --- | --- |
| `networking-access` or `Networking and Access` | `infrastructure-operations`, `security-privacy-resilience` |
| `knowledge-documentation` or `Knowledge and Documentation` | `knowledge-context`, `engineering-evolution` |
| `personal-services` or `Personal Services` | Human Agency Domains selected by service responsibility |
| `ai-aiden-os` or `AI and Aiden OS` | `artificial-intelligence`, `interaction-experience` |

Combined identities must not be collapsed automatically.

---

## Alignment States

- `canonical-id`: exact canonical identifier.
- `canonical-label`: exact canonical display label.
- `alias`: curated one-to-one compatibility mapping.
- `deprecated`: previously accepted identifier with explicit replacement.
- `ambiguous`: recognized value spanning multiple canonical identities.
- `unknown`: no explicit deterministic rule matches.
- `conflicting`: explicit repository facts imply incompatible primary identities.

---

## Deterministic Boundaries

Deterministic behavior includes:

- Reading the declared value.
- Reading canonical identifiers and labels.
- Exact identifier and label matching.
- Applying curated one-to-one aliases.
- Applying explicit deprecated replacements.
- Exposing explicit ambiguous candidates.
- Identifying unknown values.
- Preserving evidence and provenance.

Human or bounded review is required for:

- Inferring capability from natural-language prose.
- Selecting a primary capability from an ambiguous value.
- Determining secondary capabilities.
- Approving object migration.
- Adding or retiring capabilities.
- Advancing lifecycle state.

---

## Structured Assessment Contract

Capability Alignment produces:

- Opportunity identifier and repository path.
- Raw declared value.
- Alignment state.
- Primary canonical identifier and label when resolved.
- Candidate identifiers when ambiguous.
- Secondary identifiers only when explicitly supported.
- Evidence and provenance.
- Explanation and confidence.
- Blockers and unresolved questions.
- A bounded recommendation.

---

## Migration Workflow

```text
Assess Existing Value
  -> Explain Alignment State
  -> Human Review
  -> Approve Canonical Identifier
  -> Update Object in a Separate Change
  -> Verify and Preserve History
```

Capability Alignment does not mutate objects.

Architecture migration is not opportunity duplication.

---

## Initial Implementation Boundary

The implementation should:

- Build the thirteen-identity canonical catalog from repository architecture.
- Preserve raw declared values.
- Resolve canonical identifiers and labels.
- Resolve current one-to-one aliases.
- Resolve deprecated one-to-one identifiers.
- Expose ambiguous combined legacy identities.
- Preserve evidence, provenance, blockers, and questions.
- Attach results to Engineering Opportunity Assessments.
- Avoid semantic inference and lifecycle mutation.

It should not rewrite opportunity objects, determine secondary alignment, rank opportunities, detect duplicates, depend on a language model, or move reasoning into an Atlas command.

---

## Verification Cases

Tests cover:

- The thirteen canonical identities.
- Exact canonical identifier and label resolution.
- Current human-readable aliases.
- Deprecated legacy identifiers.
- Ambiguous `ai-aiden-os`.
- Unknown values.
- Raw-value preservation.
- Resolved and unresolved assessment behavior.
- No prose-based inference.
- No object mutation.

---

## Human Authority

Humans remain responsible for changing an opportunity's declared capability, selecting a primary capability from ambiguity, approving migration, adding or retiring capabilities, approving future secondary metadata, and advancing lifecycle state.

---

## Relationships

- `docs/architecture/capabilities.md` owns capability identity.
- `docs/architecture/engineering-opportunity-object.md` owns the declared field.
- Engineering Opportunity Assessment consumes alignment results.
- Scope Classification consumes the result without redefining it.
- Distinctness Analysis may use capability alignment as evidence but must not treat shared capability as duplication.

---

## Future Direction

Later work may include repository-owned machine-readable mappings, explicit secondary alignment, maturity correlation, mission and roadmap alignment, capability-gap analysis, and human-reviewed semantic assistance.

These improvements must preserve stable identity, transparent evidence, and human migration authority.
