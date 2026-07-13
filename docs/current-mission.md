# Current Mission

## Phase

Engineering Opportunity Intelligence

---

## Mission

Continue evolving Atlas into the primary deterministic engineering interface for the Aiden Platform.

The immediate objective is to design how Engineering Opportunity Intelligence should interpret, validate, and explain an opportunity's relationship to the canonical Platform Capability Map.

This milestone should resolve the capability-identity and alignment contract before implementing capability reasoning. It must distinguish explicit repository facts from derived alignment findings and must not silently reinterpret or rewrite canonical opportunity objects.

---

## Current Focus

- Design Engineering Opportunity Capability Alignment.
- Define the canonical source of capability identity.
- Clarify whether opportunity capability values are identifiers, labels, aliases, or provisional classifications.
- Define primary capability and secondary capability alignment.
- Define how existing opportunity capability values map to the canonical Platform Capability Map.
- Define evidence, confidence, ambiguity, and conflict handling.
- Preserve human authority over object changes and lifecycle progression.
- Establish a bounded implementation contract for later deterministic reasoning.

---

## Current Priorities

1. Define the relationship between Engineering Opportunity Objects and `docs/architecture/capabilities.md`.
2. Define stable capability identifiers separately from human-readable labels where appropriate.
3. Determine whether every opportunity must have exactly one primary capability.
4. Define how secondary or cross-capability alignment should be represented in derived assessments.
5. Define alias and compatibility rules for existing values such as Engineering, AI, Documentation, Infrastructure, and Learning.
6. Define how Atlas reports unknown, deprecated, ambiguous, or conflicting capability values.
7. Define the evidence and provenance required for a capability-alignment finding.
8. Separate deterministic validation from human or AI-assisted semantic judgment.
9. Define migration rules that preserve canonical object history and avoid silent mutation.
10. Define the structured capability-alignment output consumed by Engineering Opportunity Assessments.
11. Define the initial implementation boundary and focused test cases.
12. Establish deterministic milestone-completion evidence for the design.

---

## Recently Completed

- Engineering Opportunity Relationship foundation
- Typed `depends_on`, `enables`, and `related_to` relationship findings
- Deterministic portfolio relationship view
- Relationship source, target, directionality, evidence, explanation, and confidence
- Explicit self-reference detection
- Duplicate relationship declaration detection
- Conflicting explicit relationship detection
- Relationship-foundation tests
- Relationship-foundation milestone recognition
- Engineering Opportunity Evidence foundation
- Structured dependencies, related opportunities, related documents, and evidence
- Bounded top-level YAML sequence parsing
- Deterministic opportunity-reference validation
- Deterministic repository-document reference validation
- Source-backed explicit-reference and evidence facts
- Evidence-foundation tests
- Evidence-foundation milestone recognition
- Engineering Opportunity Assessment foundation
- Reusable Engineering Opportunity Assessment data model
- Deterministic Engineering Opportunity object-quality reasoning
- Assessment tests for valid, incomplete, and inconsistent objects
- Engineering Opportunity Assessment milestone recognition
- Design Engineering Opportunity Intelligence
- Engineering Opportunity Assessment architecture
- Engineering Opportunity Object architecture and lifecycle
- Engineering Opportunity repository ownership
- Initial Engineering Opportunity Object inventory
- Atlas opportunities interface
- Engineering Opportunity design milestone recognition
- Repository Synchronization Reasoning
- Mission Advancement Reasoning
- Milestone Completion Reasoning
- Engineering Intelligence
- Engineering Interpretation
- Engineering Review
- Structured milestone criteria
- Repository validation
- Repository synchronization
- Repository impact analysis
- Engineering-state awareness
- Deterministic engineering startup
- Context generation workflows

---

## Current Non-Priorities

- Implementing capability-alignment reasoning before the contract is designed
- Automatically rewriting existing opportunity capability values
- Treating display labels as stable identifiers without an explicit decision
- Inferring capability solely from title, summary, rationale, evidence, or keyword similarity
- Semantic duplicate and overlap determination
- Scope classification
- Automatic component or umbrella classification
- Architectural-significance evaluation
- Portfolio-wide prioritization
- Strategic-value scoring
- Broad autonomous candidate-opportunity discovery
- Engineering Intelligence integration
- Engineering Review presentation of opportunity recommendations
- New Atlas capability commands
- Automatic lifecycle mutation
- Automatic mission or roadmap creation
- Permanent assessment artifact storage
- Dependence on a specific AI model or provider
- Agentic Engineering Foundation implementation
- Large infrastructure expansion
- New self-hosted services
- Major hardware changes
- Building large end-user applications

---

## Current Status

The Engineering Opportunity Relationship foundation is implemented and recognized by Atlas with high confidence.

The repository now supports:

- Structured opportunity evidence and explicit references
- Deterministic validation of opportunity and document references
- Typed explicit opportunity relationships
- Directional dependency and inverse enablement views
- Generic explicit related-opportunity findings
- Portfolio relationship composition
- Relationship declaration diagnostics
- Reusable relationship findings attached to opportunity assessments
- Focused relationship tests
- Deterministic relationship milestone-completion reasoning

Engineering Opportunity Objects require a `capability` field, and the repository has a canonical Platform Capability Map. However, the current architecture does not yet define whether opportunity capability values must exactly match canonical capability names, may use aliases, may represent broader domains, or may require primary and secondary capability alignment.

The existing opportunity inventory already contains values that do not map one-to-one to the current capability labels. Implementing validation without resolving that contract would create false precision and could encourage unsafe automatic rewrites.

The next responsible step is therefore to design capability alignment before implementing it.

---

## Next Milestone

Design Engineering Opportunity Capability Alignment.

Create the architecture contract that defines how Engineering Opportunity Intelligence relates opportunity objects to the canonical Platform Capability Map.

The design should define:

- Canonical capability identity and source of truth
- Stable identifiers and human-readable labels
- Primary capability semantics
- Secondary and cross-capability alignment
- Existing-value aliases and compatibility behavior
- Unknown, deprecated, ambiguous, and conflicting values
- Evidence and provenance
- Deterministic validation boundaries
- Human or AI-assisted judgment boundaries
- Structured assessment output
- Migration and lifecycle authority
- Initial implementation scope
- Focused verification cases

This milestone should not implement capability scoring, automatically rewrite opportunity objects, infer capability from prose, rank the portfolio, or add command-specific evaluation logic.

---

## Success Criteria

The milestone is complete when:

- A canonical Engineering Opportunity Capability Alignment architecture document exists.
- The design identifies `docs/architecture/capabilities.md` as the capability source of truth or explicitly revises that ownership.
- Stable capability identity is distinguished from mutable display wording.
- Primary capability semantics are defined.
- Secondary and cross-capability alignment are defined.
- Existing opportunity capability values are inventoried and addressed by explicit compatibility or migration rules.
- Unknown, deprecated, ambiguous, and conflicting capability values have defined behavior.
- Capability-alignment facts, findings, evidence, provenance, confidence, and unresolved questions are defined.
- Deterministic validation is separated from semantic engineering judgment.
- Canonical object mutation remains human-authorized.
- The structured output contract is reusable by Engineering Opportunity Assessment and downstream reasoning.
- The initial implementation boundary and non-goals are explicit.
- Focused implementation test cases are identified.
- Required architecture metadata is registered in Repository Knowledge.
- Atlas can recognize completion of the capability-alignment design from concrete document evidence.
