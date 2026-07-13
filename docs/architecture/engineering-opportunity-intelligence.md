# Engineering Opportunity Intelligence Architecture

## Purpose

Engineering Opportunity Intelligence is the specialized Repository Reasoning
capability that discovers, evaluates, relates, prioritizes, and explains
potential engineering opportunities for the Aiden Platform.

Its purpose is to transform preserved Engineering Opportunity Objects and
repository evidence into structured future engineering direction.

Rather than asking only:

    What should engineering do next?

Engineering Opportunity Intelligence asks:

    What opportunities currently exist?
    Why do they matter?
    How do they relate?
    Which require additional evidence or architecture?
    Which should influence future engineering work?

---

## Core Principle

Engineering Opportunity Objects preserve engineering possibilities.

Engineering Opportunity Intelligence evaluates those possibilities.

Human engineers decide what the platform should do with them.

Opportunity Intelligence should improve engineering judgment without silently
replacing it.

---

## Architectural Position

Engineering Opportunity Intelligence is a specialized Repository Reasoning
capability.

    Repository
        ↓
    Repository Knowledge
        ↓
    Repository Reasoning
        ├── Repository Validation
        ├── Repository Synchronization
        ├── Impact Analysis
        ├── Mission and Milestone Reasoning
        └── Engineering Opportunity Intelligence
                    ↓
    Engineering Intelligence
        ↓
    Engineering Interpretation
        ↓
    Engineering Review
        ↓
    Engineering Interfaces

Engineering Opportunity Intelligence produces structured assessments.

Engineering Intelligence composes those assessments with other engineering
evidence.

Engineering Interpretation determines which action should be recommended.

Engineering Review explains recommendations to the engineer.

Interfaces present results.

This direction must remain one-way. Engineering Opportunity Intelligence should
not consume Engineering Review as an upstream reasoning source because Review
is a downstream consumer of opportunity assessments.

---

## Relationship to Engineering Opportunity

Engineering Opportunity defines:

- Repository ownership.
- Opportunity lifecycle.
- Opportunity producers and consumers.
- The separation between opportunity capture and implementation.
- The responsibility of humans to authorize lifecycle progression.

Engineering Opportunity owns the preserved possibility.

Engineering Opportunity Intelligence owns the derived assessment.

---

## Relationship to Engineering Opportunity Objects

An Engineering Opportunity Object is the canonical repository record of an
individual opportunity.

It preserves information such as:

- Stable identity.
- Lifecycle state.
- Capability ownership.
- Summary.
- Rationale.
- Evidence.
- Notes.
- Explicit relationships.
- Human decisions.

Opportunity Intelligence consumes objects without silently rewriting them.

The object remains repository truth.

The assessment remains rebuildable reasoning derived from repository truth.

---

## Relationship to Engineering Opportunity Assessment

Engineering Opportunity Assessment defines the reusable reasoning contract used
to evaluate one opportunity or compare several opportunities.

It defines:

- Facts, findings, and recommendations.
- Scope classifications.
- Opportunity relationships.
- Evaluation dimensions.
- Confidence.
- Recommendation classes.
- Contextual priority.
- Assessment pipeline.
- Structured assessment output.

This document defines the capability that produces assessments.

The assessment architecture defines the form and meaning of those assessments.

Canonical assessment architecture:

    docs/architecture/engineering-opportunity-assessment.md

---

## Inputs

Engineering Opportunity Intelligence may consume:

- Engineering Opportunity Objects.
- Engineering Opportunity Object schema and lifecycle rules.
- Repository Knowledge.
- Repository Validation findings.
- Repository Synchronization findings.
- Impact Analysis.
- Architecture documentation.
- Current mission and milestone.
- Capability definitions and maturity.
- Engineering state.
- Git state when relevant.
- Explicit opportunity relationships.
- Related documents.
- Recorded human decisions.
- Existing opportunity assessments.

Future inputs may include:

- Repository consolidation reasoning.
- Documentation analysis.
- Architecture drift detection.
- Capability gap analysis.
- Engineering session observations.
- Operational history.
- Software delivery planning.
- Infrastructure state analysis.

Conversation may reveal an opportunity, but conversation should not become the
canonical evidence store.

Important observations should first be preserved in the repository.

---

## Discovery Boundaries

Engineering Opportunity Intelligence supports two distinct forms of discovery.

### Repository Object Discovery

Repository Object Discovery identifies Engineering Opportunity Objects that
already exist.

This should be deterministic.

It includes:

- Locating opportunity objects.
- Loading structured fields.
- Validating stable identifiers.
- Reading lifecycle state.
- Identifying repository paths.
- Reading explicit relationships.
- Detecting loading and schema failures.

### Candidate Opportunity Discovery

Candidate Opportunity Discovery identifies potential opportunities from other
repository evidence.

Possible sources include:

- Architecture gaps.
- Repeated validation failures.
- Documentation drift.
- Operational friction.
- Capability maturity gaps.
- Repeated engineering-session failures.
- Repository duplication.
- Unimplemented architectural intent.

A discovered candidate is not automatically a repository object.

Candidate discovery should produce a proposed opportunity with evidence.

A human engineer should decide whether the candidate becomes a canonical
Engineering Opportunity Object.

Initial implementation should prioritize reasoning over existing objects before
attempting broad repository-wide candidate discovery.

---

## Core Reasoning Questions

For each opportunity, Engineering Opportunity Intelligence should determine:

- Is the object structurally valid?
- Is the opportunity understandable?
- Is it sufficiently distinct?
- Does the same underlying opportunity already exist?
- Which platform capability would improve?
- What scope does the opportunity operate at?
- What evidence supports it?
- What other opportunities does it relate to?
- Does it require architecture?
- Does it depend on unfinished work?
- Does it enable other opportunities?
- Is it aligned with the current mission?
- Is it mature enough for lifecycle progression?
- What should happen next?
- How confident is the assessment?

---

## Responsibilities

Engineering Opportunity Intelligence should:

- Discover existing opportunity objects.
- Validate opportunity identity and lifecycle consistency.
- Normalize opportunity evidence for reasoning.
- Produce reusable Engineering Opportunity Assessments.
- Classify opportunity scope.
- Evaluate explicit and candidate relationships.
- Identify duplicate and overlap candidates.
- Explain capability alignment.
- Evaluate architectural significance.
- Evaluate dependencies and readiness.
- Recommend responsible next actions.
- Expose evidence, uncertainty, and confidence.
- Feed opportunity assessments into Engineering Intelligence.
- Preserve human control over lifecycle mutation.

---

## Outputs

The primary output is a structured Engineering Opportunity Assessment.

Assessments may include:

- Opportunity identifier.
- Lifecycle state.
- Repository facts.
- Derived findings.
- Scope classification.
- Capability alignment.
- Relationship findings.
- Evidence evaluation.
- Architectural significance.
- Dependency readiness.
- Contextual priority.
- Recommended next action.
- Confidence.
- Blockers.
- Unresolved questions.

The exact assessment contract is defined in:

    docs/architecture/engineering-opportunity-assessment.md

Assessments should be reusable by multiple interfaces.

They should not be rendered directly inside reasoning logic.

---

## Relationship to Engineering Intelligence

Engineering Opportunity Intelligence provides structured assessments to
Engineering Intelligence.

Engineering Intelligence may correlate those assessments with:

- Repository health.
- Synchronization state.
- Working tree state.
- Current mission.
- Current milestone.
- Mission advancement.
- Milestone completion.
- Capability maturity.
- Relevant architecture.
- Engineering blockers.

Engineering Intelligence should not reimplement opportunity evaluation.

---

## Relationship to Engineering Interpretation

Engineering Interpretation consumes the composed engineering picture.

It determines:

- Whether an opportunity should be surfaced now.
- Which recommendation is currently responsible.
- Whether repository health must take precedence.
- Whether the active mission should continue.
- Whether an opportunity should influence the next mission.
- What checkpoint should be presented to the engineer.

Opportunity Intelligence evaluates possibilities.

Engineering Interpretation chooses responsible action from the complete
engineering context.

---

## Relationship to Engineering Review

Engineering Review presents opportunity recommendations when they are relevant
to current engineering work.

It may explain:

- Which opportunity matters now.
- Why it matters.
- What evidence supports it.
- What dependencies or blockers exist.
- What lifecycle action is recommended.
- How confident the platform is.

Engineering Review should consume assessments without duplicating their
reasoning.

Review observations that reveal a new possibility should first become
repository evidence or a candidate opportunity.

---

## Relationship to Atlas Interfaces

Atlas commands should remain presentation layers.

The existing command:

    ./atlas opportunities

currently presents opportunity inventory and lifecycle grouping.

Future interfaces may present:

- Opportunity assessments.
- Relationship findings.
- Duplicate candidates.
- Priority explanations.
- Lifecycle recommendations.
- Candidate opportunities.
- Portfolio summaries.

Commands should consume reusable Opportunity Intelligence capabilities.

They should not implement evaluation independently.

---

## Human Decision and Lifecycle Mutation

Engineering Opportunity Intelligence does not own lifecycle mutation.

A human-authorized workflow remains responsible for:

- Moving objects between lifecycle directories.
- Changing status.
- Recording acceptance or rejection.
- Approving a merge.
- Closing a duplicate.
- Selecting architecture work.
- Scheduling implementation.
- Recording completion.

When opportunities are merged:

- Stable identifiers should remain historically traceable.
- The canonical target should be explicit.
- The source should be closed with a reason.
- Useful evidence and notes should be preserved.
- References should not silently disappear.

A recommendation is not a repository mutation.

---

## Initial Implementation Boundary

The first operational version should remain deliberately narrow.

It should:

- Consume existing Engineering Opportunity Objects.
- Validate identity and lifecycle consistency.
- Produce the reusable assessment structure.
- Classify opportunity scope.
- Evaluate explicit relationships.
- Identify strong duplicate or overlap candidates.
- Explain capability alignment.
- Produce evidence-backed recommendations.
- Include confidence and unresolved questions.
- Feed assessments into Engineering Intelligence.
- Preserve human lifecycle control.

The first version should not:

- Automatically create opportunity objects.
- Automatically mutate lifecycle state.
- Automatically create missions or roadmaps.
- Depend on a specific language model.
- Perform broad autonomous repository discovery.
- Require opaque numeric scoring.
- Introduce permanent assessment storage prematurely.
- Move evaluation logic into the Atlas command layer.

Semantic relationships and strategic-value judgments may initially require
human or AI-assisted review.

The architecture should support later automation without pretending subjective
decisions are already deterministic.

---

## Design Rules

Engineering Opportunity Intelligence must:

- Reuse Repository Knowledge and existing reasoning.
- Produce structured assessments.
- Follow the Engineering Opportunity Assessment contract.
- Explain conclusions using repository evidence.
- Expose uncertainty and confidence.
- Avoid circular dependencies with Engineering Review.
- Preserve human architectural judgment.
- Keep lifecycle mutation separate from assessment.
- Keep contextual priority separate from permanent object identity.
- Support multiple future interfaces.
- Remain independent of any individual AI provider.
- Avoid duplicating Engineering Intelligence or Engineering Interpretation.
- Keep Atlas commands thin.

---

## Non-Responsibilities

Engineering Opportunity Intelligence should not:

- Own canonical opportunity objects.
- Automatically approve or reject ideas.
- Automatically merge objects.
- Automatically change lifecycle state.
- Automatically implement opportunities.
- Replace architecture.
- Replace Engineering Interpretation.
- Replace Engineering Review.
- Replace human prioritization.
- Become conversational memory.
- Become an opaque ranking algorithm.
- Depend on a specific AI model or interface.

---

## Architecture Completion Criteria

This architecture is considered designed when it defines:

- Architectural placement.
- Inputs.
- Discovery boundaries.
- Core reasoning questions.
- Responsibilities.
- Output ownership.
- Downstream consumers.
- Human lifecycle authority.
- Initial implementation scope.
- Relationship to the assessment architecture.

---

## Operational Completion Criteria

Engineering Opportunity Intelligence is considered operational when:

- Atlas discovers existing opportunity objects.
- Invalid objects produce useful diagnostics.
- Opportunity assessments are structured and reusable.
- Opportunity relationships can be evaluated.
- Duplicate and overlap candidates can be explained.
- Capability alignment is evidence-backed.
- Recommendations include reasons and confidence.
- Assessments remain separate from lifecycle mutation.
- Engineering Intelligence consumes opportunity assessments.
- Engineering Review presents recommendations without duplicating reasoning.
- Future missions can be informed by evaluated opportunities.
- Human engineers retain final lifecycle control.

---

## Future Direction

Engineering Opportunity Intelligence should become the platform capability that
continuously identifies high-leverage engineering possibilities across the
repository.

Future evolution may include:

- Repository-wide candidate discovery.
- Capability-gap analysis.
- Opportunity portfolio views.
- Strategic and tactical clustering.
- Historical assessment comparison.
- Dependency graph reasoning.
- Mission candidate generation.
- Roadmap support.
- Opportunity capture interfaces.
- Repository consolidation recommendations.
- AI-assisted semantic comparison.
- Continuous capability evolution intelligence.

The long-term objective is not autonomous platform planning.

The objective is a repository-native capability that preserves future
possibilities, evaluates them deliberately, and helps the human engineer choose
high-leverage work without relying on conversational memory or trend-driven
decision making.
