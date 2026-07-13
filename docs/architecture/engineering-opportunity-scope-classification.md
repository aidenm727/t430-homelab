# Engineering Opportunity Scope Classification Architecture

## Purpose

Engineering Opportunity Scope Classification defines how Engineering Opportunity
Intelligence identifies the kind of engineering change represented by an
Engineering Opportunity Object.

Its purpose is to prevent fundamentally different opportunities from being
compared or interpreted as though they operate at the same level.

Scope Classification should help Atlas explain whether an opportunity is
primarily strategic, capability-oriented, architectural, engineering-system
oriented, implementation-focused, or operational and infrastructure-focused.

---

## Core Principle

Scope is derived engineering reasoning.

The Engineering Opportunity Object preserves the possibility.

Scope Classification interprets the central engineering outcome represented by
that possibility.

A classification is not canonical object identity, a lifecycle decision, or an
authorization to implement work.

Scope Classification must expose evidence and uncertainty rather than disguise
semantic judgment as deterministic repository truth.

---

## Architectural Position

Scope Classification belongs to Engineering Opportunity Intelligence in the
Repository Reasoning layer.

    Engineering Opportunity Object
        ↓
    Repository Facts and Explicit Evidence
        ↓
    Scope Classification
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

Engineering Opportunity Assessment consumes Scope Classification.

Engineering Intelligence may later compare opportunities within or across scope
classes.

Engineering Interpretation decides what action is responsible.

Engineering Review presents the result.

The human engineer retains authority over canonical objects and lifecycle state.

---

## Relationship to Capability Alignment

Capability and scope answer different questions.

Capability Alignment asks:

    Which durable Platform Capability would this opportunity strengthen?

Scope Classification asks:

    What kind of engineering change is this opportunity primarily proposing?

An Engineering opportunity can have any scope.

An AI and Aiden OS opportunity may be strategic direction, capability,
architecture, implementation, or operations.

Capability identity must not determine scope automatically.

Capability Alignment may provide supporting evidence, but it is never sufficient
on its own to resolve scope.

---

## Canonical Scope Taxonomy

The initial taxonomy contains six stable scope identities.

| Scope ID | Display Label |
| --- | --- |
| `strategic-direction` | Strategic Direction |
| `capability-opportunity` | Capability Opportunity |
| `architecture-opportunity` | Architecture Opportunity |
| `engineering-system-opportunity` | Engineering System Opportunity |
| `implementation-opportunity` | Implementation Opportunity |
| `operational-infrastructure-opportunity` | Operational or Infrastructure Opportunity |

Scope identifiers are durable reasoning identities.

Display labels may evolve without changing identity.

Adding, merging, or retiring a scope requires an explicit architecture decision.

---

## Scope Definitions

### Strategic Direction

A durable long-term direction that may influence several capabilities,
architectures, missions, roadmaps, or future systems.

The central outcome is directional clarity rather than one bounded capability,
architecture document, implementation, or operational change.

Examples may include personal AI direction or infrastructure sovereignty.

Typical evidence includes:

- Several capability areas are materially involved.
- The opportunity establishes a long-lived direction.
- Multiple future missions or architectures may be required.
- The opportunity is intentionally broader than one implementation path.

Strategic breadth alone does not imply immediate priority.

### Capability Opportunity

An opportunity to create or strengthen a durable platform ability independent of
a particular service, product, script, or implementation.

The central outcome is that the platform becomes able to do something reliably
that it could not do before, or does poorly today.

Typical evidence includes:

- The outcome is described as a reusable platform ability.
- Several implementations could satisfy the opportunity.
- The opportunity should remain meaningful even if tools change.
- Capability ownership is more central than one architecture artifact or
  deployment.

A capability opportunity may later produce architecture and implementation work.

### Architecture Opportunity

An opportunity whose central deliverable is durable design, ownership,
boundaries, relationships, principles, or decision rules.

Typical evidence includes:

- Missing or conflicting architecture blocks responsible implementation.
- The opportunity proposes creating or revising canonical architecture.
- Repository ownership or system boundaries must be established.
- Several implementations depend on the design decision.

Referencing an architecture document does not by itself make an opportunity an
Architecture Opportunity.

### Engineering System Opportunity

An opportunity to improve the systems used to design, understand, validate,
build, document, collaborate on, or evolve the Aiden Platform.

Typical subjects include:

- Atlas.
- Repository Knowledge.
- Repository Reasoning.
- Engineering session startup.
- Validation and synchronization.
- Artifact transport.
- Engineering collaboration.
- Reusable engineering workflows and skills.

Engineering System Opportunity is more specific than the general Engineering
capability.

The primary outcome must be an improvement to the engineering system itself, not
merely an implementation performed by engineers.

### Implementation Opportunity

A bounded implementation, refactoring, replacement, migration, or tooling change
that realizes established architecture or a sufficiently understood design.

Typical evidence includes:

- The deliverable is concrete and bounded.
- Architecture is already sufficient for responsible implementation.
- Verification can be described directly.
- The opportunity does not primarily establish a new capability or durable
  design contract.

A large implementation may still be an Implementation Opportunity when its
engineering boundary is clear.

### Operational or Infrastructure Opportunity

An opportunity focused on deployed systems, operational reliability, security,
storage, networking, compute, observability, services, backups, access, or
operating procedures.

Typical evidence includes:

- The central outcome changes or improves current operational state.
- Deployed infrastructure or service behavior is the primary subject.
- Reliability, security, recovery, access, or maintenance is central.
- Verification depends on live system behavior.

An infrastructure-themed long-term direction may instead be Strategic Direction.

---

## Primary Scope

Every resolved classification has exactly one primary scope.

Primary scope identifies the central engineering outcome of the opportunity.

It is not determined by:

- The opportunity's capability value alone.
- The repository directory containing the object.
- One keyword.
- The tool that might implement the work.
- The current mission.
- The opportunity's apparent importance.

When several scopes apply, the primary scope should answer:

    What must become true for this opportunity to be considered fulfilled?

The scope representing that central outcome is primary.

---

## Secondary Implications

An opportunity may have zero or more secondary scope implications.

Secondary implications describe meaningful consequences or supporting work that
do not own the opportunity's central outcome.

Examples include:

- A Capability Opportunity that requires architecture.
- A Strategic Direction that will create several capability and architecture
  implications.
- An Engineering System Opportunity that includes a bounded implementation.
- An Operational or Infrastructure Opportunity that requires architecture
  before deployment.

Secondary implications must not be used to avoid selecting a primary scope.

They should be evidence-backed and should remain empty when evidence is
insufficient.

The initial deterministic foundation should not infer secondary implications
from prose automatically.

---

## Classification States

Scope Classification uses explicit states.

### Resolved

One primary scope is supported strongly enough to be stated as the current
classification.

A resolved result may still include secondary implications and unresolved
questions.

High-confidence resolution normally requires explicit human-reviewed evidence or
an unambiguous repository contract.

### Candidate

One scope is the leading interpretation, but the evidence does not justify a
resolved classification.

The leading candidate should be identified with its evidence and confidence.

### Ambiguous

Two or more alternative scopes are supported, and the available evidence does
not establish one primary scope.

Candidate scope identifiers and the source of ambiguity should be exposed.

### Mixed

The opportunity combines multiple central outcomes that may need decomposition
before one primary scope can be selected.

Mixed is not a permanent substitute for clear object boundaries.

The recommendation may be to split or clarify the opportunity after human
review.

### Insufficient Evidence

The repository does not contain enough evidence to produce a defensible scope
candidate.

The result should explain what evidence is missing.

### Conflicting

Explicit human-reviewed or repository-owned scope evidence disagrees.

The conflict must be surfaced rather than normalized away.

---

## Evidence Model

Scope evidence has four levels.

### Repository Facts

Directly observable facts include:

- Opportunity identifier and path.
- Title, summary, rationale, evidence, and notes.
- Declared capability value.
- Capability Alignment result.
- Explicit related documents.
- Explicit dependencies and related opportunities.
- Lifecycle state.
- Recorded human decisions.

These facts are deterministic to read.

They are not automatically deterministic proof of scope.

### Structural Evidence

Structural evidence includes:

- A related document is canonical architecture.
- An opportunity is explicitly related to broader or narrower work.
- Capability Alignment is resolved or unresolved.
- A human decision records required architecture.
- The opportunity explicitly identifies a bounded implementation artifact.

Structural evidence can support a classification candidate.

Most structural evidence remains insufficient by itself to resolve semantic
scope.

### Heuristic Evidence

Heuristic evidence includes:

- Normalized phrases in title, summary, rationale, evidence, or notes.
- Repeated language associated with one scope definition.
- Several independent textual signals pointing toward one class.
- Similarity to human-reviewed examples.

Heuristic evidence must produce candidates, not deterministic facts.

Every heuristic rule must be inspectable and explainable.

Keyword similarity alone must never create a resolved classification.

### Human-Reviewed Evidence

Human-reviewed evidence includes:

- An explicit recorded scope decision.
- An approved architecture or opportunity review.
- A future human-authorized canonical scope field.
- A reviewed assessment promoted into repository truth.

Human-reviewed evidence may support a resolved high-confidence classification.

The initial architecture does not require adding scope to existing opportunity
objects.

---

## Provenance

Every classification should identify where its evidence came from.

Minimum provenance includes:

- Opportunity identifier.
- Opportunity repository path.
- Scope taxonomy source.
- Facts or fields used.
- Related documents or relationships used.
- Heuristic rules used, when applicable.
- Human-reviewed decision source, when applicable.
- Reasoning implementation version or module when practical.

A classification without provenance is incomplete.

---

## Deterministic, Heuristic, and Judgment Boundaries

The following behavior is deterministic:

- Loading the canonical scope taxonomy.
- Reading opportunity fields and references.
- Reading Capability Alignment.
- Identifying referenced repository document types.
- Reading explicit relationships.
- Reading explicit human decisions.
- Detecting missing, duplicate, or conflicting explicit classification evidence.
- Producing source-backed structured results.

The following behavior is heuristic:

- Interpreting natural-language descriptions.
- Producing scope candidates from transparent phrase rules.
- Comparing an opportunity with reviewed examples.
- Identifying likely mixed scope.

Heuristic results should normally have Medium or Low confidence.

The following behavior requires human or explicitly bounded AI-assisted judgment:

- Selecting the primary scope from ambiguous evidence.
- Deciding whether a mixed opportunity should be split.
- Resolving conflict between plausible scope interpretations.
- Approving a high-confidence semantic classification.
- Changing the scope taxonomy.
- Promoting a derived classification into canonical repository data.

The platform must never present AI judgment as deterministic repository truth.

---

## Confidence Model

### High Confidence

The classification follows from explicit human-reviewed evidence or an
unambiguous repository contract with little reasonable alternative.

### Medium Confidence

One interpretation is well supported by several independent structural or
semantic signals, but human review is still appropriate.

### Low Confidence

The classification is tentative, evidence is sparse, or reasonable alternatives
remain.

Confidence applies to the classification result, not to the importance of the
opportunity.

Confidence must include an explanation.

---

## Structured Assessment Contract

Scope Classification should produce a reusable structured result containing:

- Opportunity identifier.
- Repository path.
- Classification state.
- Primary scope identifier, when resolved.
- Primary scope label, when resolved.
- Leading candidate scope identifier, when applicable.
- Candidate scope identifiers.
- Secondary scope identifiers.
- Repository facts used.
- Supporting evidence.
- Counterevidence.
- Provenance.
- Explanation.
- Confidence.
- Blockers.
- Unresolved questions.
- A bounded recommendation.

A candidate Python model may resemble:

    OpportunityScopeClassification
        opportunity_id
        repository_path
        classification_state
        primary_scope_id
        primary_scope_label
        leading_candidate_scope_id
        candidate_scope_ids
        secondary_scope_ids
        facts
        evidence
        counterevidence
        provenance
        explanation
        confidence
        blockers
        unresolved_questions
        recommendation

The exact implementation may evolve.

The separation among facts, derived classification, confidence, and
recommendation must remain.

---

## Recommendation Effects

Scope Classification may recommend:

- Retain the current opportunity while scope remains unresolved.
- Enrich the summary, rationale, evidence, or relationships.
- Review the leading scope candidate.
- Clarify the opportunity boundary.
- Split a mixed opportunity.
- Record a human scope decision.
- Architect before implementation when architecture appears central.

A scope recommendation does not:

- Change lifecycle state.
- Rewrite the object.
- Merge or split objects automatically.
- Schedule implementation.
- Establish priority.
- Authorize architecture or deployment.

Unresolved scope may block comparison or lifecycle progression when the
classification is necessary for responsible review.

---

## Human Authority and Canonical Mutation

Scope Classification does not own canonical mutation.

A human-authorized workflow remains responsible for:

- Recording a canonical scope decision.
- Adding an optional scope field in a future schema revision.
- Splitting a mixed opportunity.
- Changing object summary or rationale.
- Changing the scope taxonomy.
- Advancing lifecycle state.
- Approving architecture or implementation.

Derived classifications remain rebuildable reasoning until intentionally
promoted through a repository change.

---

## Relationship to Existing Reasoning

Engineering Opportunity Assessment should consume Scope Classification rather
than reimplement it.

Scope Classification may consume:

- Object-quality findings.
- Structured evidence and references.
- Typed opportunity relationships.
- Capability Alignment.
- Registered document metadata.
- Human decisions.

Duplicate and overlap reasoning may later use scope to avoid comparing
fundamentally different opportunity types.

Architectural-significance reasoning may use scope but must remain a separate
evaluation dimension.

Contextual priority must remain separate from scope.

Atlas commands remain presentation layers.

---

## Initial Implementation Boundary

The first implementation should build a safe foundation rather than claim full
semantic classification.

It should:

- Define a reusable scope taxonomy catalog with six stable identifiers and
  labels.
- Define the structured `OpportunityScopeClassification` result.
- Collect deterministic repository facts and provenance.
- Expose explicit structural evidence.
- Support transparent bounded heuristic candidate rules.
- Produce `candidate`, `ambiguous`, `mixed`, or `insufficient-evidence` results
  when semantic resolution is not justified.
- Reserve `resolved` high-confidence results for explicit human-reviewed or
  unambiguous repository evidence.
- Preserve primary and secondary scope separation.
- Attach Scope Classification to reusable Engineering Opportunity Assessments.
- Include explanation, confidence, blockers, unresolved questions, and bounded
  recommendations.
- Preserve canonical object and lifecycle authority.
- Remain independent of Atlas command rendering and language models.

The first implementation should not:

- Force all existing opportunities into resolved classifications.
- Treat capability identity as scope.
- Resolve scope from one keyword.
- Infer secondary implications automatically from prose.
- Rewrite opportunity objects.
- Add a required scope field.
- Rank opportunities.
- Detect duplicates.
- Evaluate full architectural significance.
- Mutate lifecycle state.
- Depend on a language model.

---

## Verification Cases

The initial implementation should test:

- The six canonical scope identities and labels.
- Primary scope allows at most one resolved value.
- Secondary implications remain separate from primary scope.
- Capability identity alone does not resolve scope.
- Related architecture provides structural evidence but does not automatically
  resolve Architecture Opportunity.
- A single keyword cannot create a resolved classification.
- Several transparent signals may create a candidate with explained confidence.
- Competing signals produce an ambiguous result.
- Bundled central outcomes may produce a mixed result.
- Sparse evidence produces insufficient evidence.
- Conflicting explicit evidence produces a conflicting result.
- Human-reviewed evidence may resolve a high-confidence primary scope.
- Raw opportunity objects remain unchanged.
- Scope Classification attaches to Engineering Opportunity Assessment.
- No lifecycle mutation occurs.
- No Atlas command contains independent classification logic.

---

## Non-Responsibilities

Scope Classification should not:

- Replace Capability Alignment.
- Replace duplicate or overlap reasoning.
- Determine architectural significance by itself.
- Determine priority.
- Estimate effort.
- Decide mission relevance.
- Approve architecture.
- Authorize implementation.
- Rewrite canonical opportunity objects.
- Change lifecycle state.
- Become an opaque numeric classifier.
- Depend on a specific AI model.
- Become command-specific logic.

---

## Architecture Completion Criteria

This architecture is considered designed when it defines:

- Scope-classification purpose and ownership.
- The canonical six-class taxonomy.
- Stable identifiers and display labels.
- Primary and secondary semantics.
- Classification states.
- Evidence and provenance.
- Deterministic, heuristic, and judgment boundaries.
- Confidence behavior.
- Structured assessment output.
- Recommendation effects.
- Human mutation authority.
- Relationship to existing reasoning.
- Initial implementation scope.
- Verification cases.

---

## Future Direction

Scope Classification may later evolve through:

- Human-reviewed example sets.
- Optional canonical scope declarations.
- Repository-owned classification policies.
- Bounded AI-assisted semantic review.
- Cross-scope portfolio summaries.
- Scope-aware duplicate and overlap reasoning.
- Scope-aware Engineering Intelligence composition.

Future automation should increase explainability and engineering judgment rather
than hide uncertainty.
