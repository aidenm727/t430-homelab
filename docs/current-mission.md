# Current Mission

## Phase

Task-Scoped Agent Context Compilation Checkpoint B1b1 Implementation

---

## Mission State

The owner accepted the revised EO-2026-013 B1b plan and authorized Checkpoint B1b1 — Deterministic Selector Primitives on July 16, 2026.

The authorization is recorded in `docs/reviews/eo-2026-013-b1b1-authorization-review-2026-07-16.md` against Checkpoint B1a completion commit `e89d765ab7d62c97976091f53ce59dd3f767e4cb`.

Checkpoint B1b1 may create exactly two files and modify exactly three existing files. It implements pure bounded YAML and Markdown selector transformations only. It does not derive candidates, verify relationships, select sources, produce omissions or unknowns, or construct a package.

Checkpoint B1b2 and Checkpoint B2 remain explicitly unauthorized.

Checkpoint B1a and its Git snapshot boundary remain unchanged.

The protected branch `wip/distinctness-foundation-calibration` remains unchanged at `fcbc5957b89fe65a4313a3c23eb814e02a014698`. Its content remains out of scope. B1b1 performs no protected-reference operation and no Git access.

EO-2026-013 and all 21 Engineering Opportunities remain `reviewed`.

---

## Mission Intent

Establish deterministic selector primitives over immutable bytes before source-selection reasoning begins.

Checkpoint B1b1 defines strict UTF-8 and line-ending handling, one bounded Engineering Opportunity YAML subset, canonical JSON field extraction, and exact ATX Markdown section extraction with bounded fenced-code awareness.

Selector primitives remain pure transformations. They consume caller-supplied bytes and perform no Git access, repository discovery, policy lookup, relationship verification, selection reasoning, hashing, budgeting, package construction, network access, or filesystem write.

Checkpoint B1b1 returns for owner review before B1b2 begins.

Repository Synchronization Reasoning remains the deterministic check for alignment between this mission, the accepted B1b1 review, canonical architecture, generated context, repository metadata, and the exact B1b1 authorization boundary.

---

## Current Focus

- Implement a strict shared UTF-8 and line-ending boundary for selectors.
- Implement the exact bounded top-level Engineering Opportunity YAML subset.
- Preserve plain accepted scalars as strings without implicit YAML typing.
- Implement deterministic folded and literal block-string behavior.
- Reject duplicate keys, aliases, anchors, merge keys, tags, flow collections, nested structures, directives, document markers, unsupported indicators, tabs, and malformed indentation.
- Implement exact YAML-field selection into repository-owned canonical JSON.
- Retain `related_documents` in the full parsed mapping for later B1b2 use without selecting it into the first payload.
- Implement exact ATX heading selection with occurrence, section boundary, line-ending, whitespace, and terminal-newline preservation.
- Prevent fenced-code heading text from becoming a match or section boundary.
- Verify all five historical selector inputs and exact outputs through B1a immutable blob reads in tests.
- Preserve B1a unchanged.
- Create and modify only the exact five B1b1 implementation paths.
- Keep B1b2, B2, protected references, Git access inside selectors, selection reasoning, digests, budgeting, and packages withheld.
- Run all tests and Atlas verification.
- Return for owner acceptance before B1b2.

---

## Initial Milestone

Implement and verify Checkpoint B1b1 — Deterministic Selector Primitives.

### Included

- `tools/atlas/platform/context_compilation/selectors.py`.
- `tests/test_context_selectors.py`.
- Bounded selector documentation in `docs/task-context/index.md`.
- Public selector exports in `tools/atlas/platform/context_compilation/__init__.py`.
- One deeply immutable `SelectorOutput` model in `tools/atlas/platform/context_compilation/models.py`.
- Strict UTF-8, BOM, NUL, Unicode-scalar, and line-ending validation.
- Bounded top-level YAML mapping parsing for strings, string sequences, folded blocks, and literal blocks.
- Exact `yaml_fields` transformation to RFC 8785 canonical JSON bytes.
- Exact Markdown ATX heading selection with bounded backtick and tilde fence awareness.
- Exact source-byte preservation for Markdown selector output.
- Historical EO object parsing and four historical Markdown section fixtures.
- Deep immutability and side-effect-free behavior.
- Full test and Atlas verification.
- Return to owner review before B1b2.

### Excluded

- Checkpoint B1b2.
- Checkpoint B2.
- Generic YAML support.
- CommonMark conformance claims.
- Git access inside selector primitives.
- Protected-reference operations or changes.
- Source candidate derivation.
- Task-profile dispatch.
- Generic policy discovery.
- Relationship verification.
- Source selection.
- Selection reasons or chains.
- Source IDs.
- Omissions.
- Unknowns.
- Freshness.
- Conflicts.
- Deduplication.
- Sensitivity or budget-tier enforcement.
- Source-content or payload digests.
- Package source or payload records.
- Budget execution.
- Package assembly or integrity.
- Explanations or golden replay.
- Atlas commands.
- Dependencies.
- Canonical architecture changes.
- Engineering Opportunity lifecycle changes.
- Task-contract implementation, execution, autonomy, provider routing, or AI-environment changes.
- Protected object or content access.

---

## Preserved Downstream Follow-Up — AI Engineering Environment Review

A subsequent bounded AI Engineering Environment Review is preserved. The actual AI working environments have not been systematically reviewed recently, but this larger review follows the EO-2026-013 architecture design and requires its own bounded owner authorization.

The future review includes:

- ChatGPT Project instructions.
- ChatGPT Project source files and their freshness.
- Project settings, memory, and Library configuration.
- Model and reasoning workflow conventions.
- Connectors, tools, skills, and permissions.
- Codex CLI configuration and launch workflow.
- Repository instructions and reusable skills.
- Generated context delivery and refresh behavior.
- Duplicated or conflicting instructions across repository documentation, ChatGPT Projects, Codex, continuity packets, and fresh-chat openers.
- Other current or future assistant environments.

Each surface should be classified as Current and useful, Stale, Redundant, Conflicting, Missing, Unused, Poorly owned, or Not verifiable. The review should record its authoritative source, intended consumer, owner, freshness expectation, update mechanism, and evidence for retaining, changing, consolidating, or removing it.

The review may use multiple AI systems only through a structured pattern:

- Atlas and the repository provide deterministic source truth.
- Codex may collect inventory and perform later bounded repository changes.
- ChatGPT may perform primary architectural analysis and synthesis.
- An independent challenger model may review the same evidence package.
- Findings must separate agreement, disagreement, unsupported speculation, immediate corrections, later opportunities, and items that should remain unchanged.
- The owner resolves disagreements and authorizes application.

Portfolio treatment remains:

- EO-2026-008 — AI Engineering Excellence is the umbrella direction.
- EO-2026-007 — AI Collaboration Intelligence covers collaboration reliability.
- EO-2026-019 — Instruction and Context Effectiveness Evaluation covers effectiveness testing.
- EO-2026-013 provides deterministic task context and consumer boundaries.
- EO-2026-009 provides the longer-term shared personal AI context direction.
- The review is a future bounded deliverable under these existing directions.
- No new Engineering Opportunity should be created unless later evidence demonstrates a distinct recurring capability boundary.

The review is not part of the first EO-2026-013 milestone. It does not authorize live configuration cleanup or changes.

---

## Completion History

### EO-2026-013 Revised B1b Plan and Checkpoint B1b1 Authorization

- Revised B1b plan accepted by the owner on July 16, 2026.
- Checkpoint B1b was split into B1b1 — Deterministic Selector Primitives and B1b2 — Bounded Selection Plan.
- Checkpoint B1b1 authorized with an exact two-created and three-modified implementation scope.
- Checkpoint B1b2 and Checkpoint B2 remain unauthorized.
- Strict input handling, bounded YAML parsing, canonical JSON field selection, exact Markdown heading selection, and historical selector verification are owned by B1b1.
- Candidate derivation, relationship verification, source selection, selected, omitted, and unknown planning, stable ordering, sensitivity enforcement, and budget-tier enforcement remain withheld for B1b2.
- Checkpoint B1a remains unchanged.
- Protected-reference behavior remains unchanged.
- Protected branch content remains out of scope.
- EO-2026-013 and all 21 Engineering Opportunities remain `reviewed`.


### EO-2026-013 Checkpoint B1a — Immutable Snapshot Boundary

- Completion accepted by the owner on July 16, 2026.
- Recording, commit, and push authorized.
- Authorization baseline: `b7046e6fdd7302e1b5aaada3db0970e35c0f0e6c`.
- Exact implementation scope: two created files and four modified existing files.
- Historical commit verified: `79eef80af3d5969ece7eb9fe7f802be35575f450`.
- Historical root tree verified: `3d2853517e64209cffde91766a62e9f70ceb2e47`.
- Historical snapshot fingerprint verified: `14053ce1b4ce71c90c18316bed3928a85a67be6d48fd1bc330ffd8a00464fed8`.
- Production Git execution is shell-free, replacement-disabled, lazy-fetch-disabled, optional-lock-disabled, literal-path, locale-stable, network-free, and target-write-free.
- The fixed command prefix disables fsmonitor and untracked cache and redirects hooks to the platform null device.
- Unsafe ambient and repository-local Git configuration is rejected before clean-state inspection.
- Exact regular blob bytes are read from the immutable root tree rather than the worktree.
- Protected-reference handling is limited to exact ref-name and direct object-identity comparison.
- One hundred forty-four tests passed.
- Atlas validation was Valid, missing definitions were clean, and synchronization was Synchronized.
- Independent final acceptance review passed.
- No B1b, B2, dependency, canonical architecture change, lifecycle mutation, protected-content access, staging, commit, or push occurred before owner acceptance.
- Checkpoint B1b and Checkpoint B2 remain unauthorized.
- Protected-branch content remains out of scope.


### EO-2026-013 Revised B1 Plan and Checkpoint B1a Authorization

- Revised B1 plan accepted by the owner on July 16, 2026.
- Checkpoint B1 was split into B1a — Immutable Snapshot Boundary and B1b — Deterministic Selectors and Selection Plan.
- Checkpoint B1a authorized with an exact two-created and four-modified implementation scope.
- Checkpoint B1b and Checkpoint B2 remain unauthorized.
- Repository identity, clean state, Git environment isolation, exact commit and tree resolution, snapshot fingerprint, exact regular-blob access, and protected-ref identity matching are owned by B1a.
- YAML and Markdown parsing, relationship verification, source selection, omissions, unknowns, and selection-plan production remain withheld for B1b.
- Protected branch content remains out of scope.
- Only exact protected-ref name and object-identity comparison is authorized.
- EO-2026-013 and all 21 Engineering Opportunities remain `reviewed`.


### EO-2026-013 Checkpoint A.1 — Executable-Policy Contract Correction

- Completion accepted by the owner on July 16, 2026.
- Recording, commit, and push authorized.
- Authorization baseline: `1f2595b8a3489979b275dfad0884b4e0fe09c585`.
- Exact implementation scope: ten modified existing files and no created or deleted files.
- Selection-policy instance advanced to `1.0.1`.
- Budget-policy instance preserved at `1.0.0`.
- All five first-replay rules gained explicit digest-bound budget tiers and `public` source sensitivity.
- Selection-policy digest changed from `708b6c73208db65dc94fcd89d1810666048895821b2e6e0feef5aa6b9ccf5448` to `69577722ea4eb6f479424f3bf324866cc2992d5df82b3224e5f20571ef081938`.
- Request digest changed from `840adc1dad2347230a05720faeee71b553c802f2cef25e08232d292f02be8390` to `4839411214fa20cde0b842a72ad9baf5d525c494fca3c931cd58d63364c8c01b`.
- Package identity digest changed from `6007762250f7992a72c91e080502104cf9fa82e90ce16039a012edd7a349b9e6` to `711062df74645329c3078b575b8ddfc737a41e3b3a0a9aeaca3ea9bafcb85678`.
- Package ID changed from `tcp-6007762250f7992a72c91e08` to `tcp-711062df74645329c3078b57`.
- Ninety tests passed.
- Atlas validation was Valid, missing definitions were clean, and synchronization was Synchronized.
- Independent final acceptance review passed.
- No B1, B2, dependency, protected-branch access, lifecycle mutation, staging, commit, or push occurred before owner acceptance.
- Checkpoint B1 and Checkpoint B2 remain unauthorized.
- Protected-branch content remains out of scope.


### EO-2026-013 Revised Executable-Path Plan Acceptance

- Revised executable-path plan accepted by the owner on July 16, 2026.
- Checkpoint A.1 — Executable-Policy Contract Correction authorized.
- Checkpoint B1 and Checkpoint B2 remain unauthorized.
- The original single Checkpoint B shape was replaced by A.1, B1, and B2 review gates.
- Source budget tier and sensitivity must become explicit, policy-owned, and digest-bound.
- The protected branch content remains out of scope.
- Only future identity comparison of the declared protected ref may be considered during a separately authorized B1 review.
- EO-2026-013 and all 21 Engineering Opportunities remain `reviewed`.


### EO-2026-013 Checkpoint A — Deterministic Foundations

- Completion accepted by the owner on July 16, 2026.
- Completion authorization included recording, committing, and pushing Checkpoint A.
- Exact implementation scope: 18 created files and 2 registration-only existing-file modifications.
- Four stable schema URNs replaced an unowned HTTPS namespace.
- Policy and request foundation digests remained unchanged.
- Typed values are deeply immutable at construction boundaries.
- Local validators enforce the accepted portable-schema boundaries and documented cross-field rules.
- Restricted canonical JSON remains standard-library-only and rejects floating point.
- Independent final acceptance review passed.
- Eighty-three tests passed.
- Atlas validation was Valid, missing definitions were clean, and synchronization was Synchronized.
- No third-party dependency, Checkpoint B path, Atlas command, lifecycle mutation, AI-environment change, staging, commit, or push occurred before owner acceptance.
- Checkpoint B remains explicitly unauthorized.
- The protected branch remained unchanged and out of scope.


### EO-2026-013 Reconciled Implementation Plan Acceptance

- Reconciled implementation plan accepted by the owner on July 16, 2026.
- Checkpoint A — Deterministic Foundations authorized.
- Checkpoint B — Executable Compilation Path remains withheld.
- External implementation-readiness research and constrained independent challenge evidence were reconciled into the accepted plan.
- No Engineering Opportunity lifecycle state changed.
- No implementation was performed by the acceptance decision itself.
- The protected branch remained unchanged and out of scope.


### EO-2026-013 Task-Scoped Agent Context Compilation Architecture

- Architecture completion accepted by the owner on July 15, 2026.
- Architecture commit: `2de09693ed1c922500477c5ba1c6903513ab4dd3` (`Define task-scoped context compilation architecture`).
- Canonical architecture: `docs/architecture/task-scoped-agent-context-compilation.md`.
- The architecture defines deterministic task authority, source selection, ordering, provenance, freshness, conflicts, unknowns, omissions, UTF-8 byte budgeting, digest surfaces, validation invariants, and consumer boundaries.
- One bounded, manually assembled, informative, non-executable example records five accepted sources and exact selector behavior without claiming compiler or validator execution.
- Human review corrections were incorporated before the guarded architecture commit.
- The guarded committed run preserved evidence that all 43 tests passed.
- Atlas validation was Valid, missing definitions were clean, and synchronization was Synchronized.
- Engineering Review's generic `Unknown / Low` result was non-blocking because no specialized milestone reasoning rule exists or is required.
- EO-2026-013 and all 21 Engineering Opportunities remained `reviewed`.
- No compiler, selector, validator, policy, fixture, lifecycle, Atlas command, Atlas reasoning, agent behavior, or AI-environment configuration change was introduced.
- The protected branch remained unchanged at `fcbc5957b89fe65a4313a3c23eb814e02a014698`.

### Canonical Knowledge Promotion Workflow Operationalization

- Completion accepted by the owner on July 15, 2026.
- Completion commit: `11d355809a07bf0721e86f9234ba8d2f57ecf9e1` (`Operationalize canonical knowledge promotion workflow`).
- Clean-state validation exists for the committed checkpoint.
- The reusable human-reviewed operating procedure is documented in `docs/knowledge-promotion.md`.
- The first bounded manual flow and its traceability evidence are preserved in `docs/reviews/knowledge-promotion-pilot-engineering-validation-2026-07-15.md`.
- The exact Validation Gate Standard was accepted by the owner and separately applied to `docs/standards/engineering-collaboration.md`.
- The guarded committed run preserved evidence that all 43 tests passed.
- Atlas validation was Valid, missing definitions were clean, and synchronization was Synchronized.
- Engineering Review's Unknown/Low milestone result was non-blocking because no specialized milestone reasoning rule exists or is required.
- EO-2026-020 remained reviewed.
- No new Repository Object type, automatic promotion, or authority expansion was introduced.
- The protected Distinctness calibration branch remained unchanged at `fcbc5957b89fe65a4313a3c23eb814e02a014698`.

---

## Recently Completed

- Established the canonical Aiden Platform Vision and layered capability architecture.
- Completed and accepted the Engineering Opportunity portfolio recalibration.
- Transitioned all 21 Engineering Opportunity Objects to `reviewed`.
- Established the AI Operating Model Architecture.
- Established the Knowledge Authority Architecture and documented the Canonical Knowledge Promotion Workflow.
- Established the dated Current AI Operating Baseline for July 14, 2026.
- Verified the account-level training control and Aiden Platform Project memory configuration.
- Completed the Aiden Platform architecture and repository-engineering evaluation.
- Completed Evaluation 2 using a naturally occurring G14 touchpad I2C initialization failure, overnight persistence evidence, normal-restart recovery, and an uncertainty-calibrated operational follow-up.
- Completed the current-information research evaluation and first ChatGPT Work pilot.
- Completed the difficult AI and computer-science learning evaluation with demonstrated transfer.
- Completed the bounded Codex repository-integration pilot with exact scope and deterministic verification.
- Completed the Claude Free independent-provider comparison and retained it as an occasional bounded audit lane.
- Completed the Initial AI Workflow Evaluation Cycle on July 15, 2026.
- Adopted the final operating stack while deferring additional subscriptions, API spending, automatic routing, local AI, and broad agent authority.
- Preserved the laptop reliability issue as operational follow-up rather than a blocker on the completed AI cycle.
- Completed the Canonical Knowledge Promotion Workflow Operationalization mission and obtained owner acceptance on July 15, 2026.
- Completed the EO-2026-013 Task-Scoped Agent Context Compilation architecture milestone and obtained owner acceptance on July 15, 2026.

---

## Current Non-Priorities

- Beginning Checkpoint B1b2 or Checkpoint B2.
- Modifying any path outside the exact five B1b1 implementation paths.
- Modifying Checkpoint B1a snapshot or protected-reference behavior.
- Treating the bounded YAML parser as general YAML.
- Claiming CommonMark conformance.
- Git subprocesses, repository discovery, network access, or filesystem writes inside selector primitives.
- Source candidate derivation or task-profile dispatch.
- Generic policy discovery.
- Historical relationship verification.
- Source selection, selection reasons, chains, IDs, omissions, unknowns, freshness, conflicts, or deduplication.
- Sensitivity or budget-tier enforcement.
- Source-content or payload digests.
- Payload materialization or budget execution.
- Package compilation, integrity, explanations, or golden replay.
- Atlas commands or generic structured-resource discovery.
- Third-party dependencies.
- Canonical architecture changes.
- Engineering Opportunity lifecycle mutation.
- Task-contract implementation, execution, autonomy, provider routing, or AI-environment changes.
- Reading, peeling, traversing, selecting, exposing, or mutating protected-object content.
- Implementing Structured Research Orchestration inside EO-2026-013.
- Resuming or merging the Distinctness implementation.

---

## Current Status

EO-2026-013 Checkpoint A, Checkpoint A.1, and Checkpoint B1a are complete and owner-accepted.

The revised B1b plan is accepted. Checkpoint B1b1 — Deterministic Selector Primitives is authorized within the exact two-created and three-modified scope recorded in `docs/reviews/eo-2026-013-b1b1-authorization-review-2026-07-16.md`.

Checkpoint B1b2 and Checkpoint B2 remain unauthorized. Checkpoint B1a remains unchanged. Protected-reference behavior remains unchanged, and protected-branch content remains out of scope. EO-2026-013 and all 21 Engineering Opportunities remain `reviewed`.

---

## Next Milestone

Implement and verify Checkpoint B1b1 — Deterministic Selector Primitives, then obtain owner acceptance before B1b2.

No selection-plan or package-compilation implementation begins automatically from this authorization.

---

## Decision Boundary

- Human decision: Revised EO-2026-013 B1b plan accepted on July 16, 2026.
- Checkpoint B1a completion: `e89d765ab7d62c97976091f53ce59dd3f767e4cb`.
- Checkpoint B1b1 authorized: Yes, exact two-created and three-modified scope.
- Checkpoint B1b2 authorized: No.
- Checkpoint B2 authorized: No.
- B1b1 created paths authorized: `selectors.py` and `test_context_selectors.py`.
- B1b1 modified paths authorized: task-context index, context-compilation exports, and models.
- Selector families authorized: bounded `yaml_fields` and exact ATX `heading`.
- Selector Git access authorized: No.
- Source-selection reasoning authorized: No.
- Relationship verification authorized: No.
- Source or payload digest work authorized: No.
- Package records or budget execution authorized: No.
- Checkpoint B1a changes authorized: No.
- Protected branch content in scope: No.
- Protected-reference behavior changes authorized: No.
- Protected object peel, traversal, content read, selection, exposure, or mutation authorized: No.
- Third-party dependency authorized: No.
- Canonical architecture changes authorized: No.
- Atlas command or generic discovery authorized: No.
- Engineering Opportunity lifecycle changed: No.
- EO-2026-013 lifecycle state: Reviewed.
- AI Engineering Environment Review authorized: No.
- Structured Research Orchestration implementation authorized: No.

STOP — Implement and verify Checkpoint B1b1 only. Do not begin B1b2 or B2.
