# EO-2026-013 Remaining Executable Path Review — July 17, 2026

- Authority class: Human-Authorized Non-Canonical Implementation-Sequencing Review
- Canonical: No
- Generated: No
- Status: Three-checkpoint decomposition recommended; no checkpoint authorized
- Date: July 17, 2026
- Verified repository baseline: `042897590bf90de33a345cf6ab8fad346a45a4c1`
- Active Engineering Opportunity: EO-2026-013 — Task-Scoped Agent Context Compilation
- Decision authority: Owner

---

## 1. Purpose and Authority Boundary

This dated review evaluates the executable work remaining after completion of EO-2026-013 Checkpoint B1b2 — Bounded Selection Plan.

It reconciles:

- the accepted task-scoped context compilation architecture;
- the accepted implementation plan;
- the completed Checkpoint A, A.1, B1a, B1b1, and B1b2 boundaries;
- the current models, digest helpers, validators, schemas, policies, fixtures, public exports, and tests;
- the original Checkpoint B path allocation;
- the read-only remaining-path evidence capture; and
- the need for independently reviewable implementation and verification gates.

This review is non-canonical. It refines implementation sequencing without changing canonical architecture, schemas, policies, Engineering Opportunity lifecycle state, task authority, or consumer authority.

This review does not authorize:

- proposed Checkpoint B2a, B2b, or B2c;
- code or test implementation;
- a package compiler;
- a committed golden package;
- an explanation interface;
- dependencies or continuous integration;
- Atlas commands or generic discovery;
- EO-2026-022 architecture or implementation;
- AI-environment configuration;
- protected-reference access or changes;
- staging, commit, or push.

---

## 2. Verified Baseline

The read-only capture verified:

- Branch: `main`.
- `HEAD`, local `main`, and `origin/main`: `042897590bf90de33a345cf6ab8fad346a45a4c1`.
- Commit subject: `Synchronize mission after EO-2026-013 B1b2`.
- Current phase: `Task-Scoped Agent Context Compilation Checkpoint B1b2 Complete`.
- Working tree and index: clean.
- Atlas Validate: Valid.
- Atlas Missing: no missing document definitions.
- Atlas Sync: Synchronized.
- No protected-reference test or command was executed.
- Nothing was modified, staged, committed, or pushed by the capture.

EO-2026-013 remains `reviewed`. EO-2026-022 — Human Engineering Control Surface remains `captured`.

---

## 3. Completed EO-2026-013 Path

The following checkpoints remain complete, independently verified, owner-accepted, and published:

1. Architecture.
2. Checkpoint A — Deterministic Foundations.
3. Checkpoint A.1 — Executable-Policy Contract Correction.
4. Checkpoint B1a — Immutable Snapshot Boundary.
5. Checkpoint B1b1 — Deterministic Selector Primitives.
6. Checkpoint B1b2 — Bounded Selection Plan.

The accepted path now provides:

- repository-owned schemas and versioned policies;
- strict request and policy loading;
- restricted RFC 8785 canonical JSON;
- request, policy, snapshot, and package-identity helpers;
- structural validation foundations;
- immutable clean-committed Git snapshots;
- content-blind protected-reference identity comparison;
- exact immutable blob reads;
- bounded YAML-field and Markdown-heading selectors;
- deterministic five-candidate source-selection reasoning;
- explicit selected, omitted, and unknown plan records;
- stable ordering and derived readiness.

No completed checkpoint is reopened or modified by this review.

---

## 4. Original Checkpoint B Realization

The accepted implementation plan assigned nine create paths to the original Checkpoint B.

Five of those create paths were completed through later bounded checkpoints:

| Path | Completed by |
| --- | --- |
| `tools/atlas/platform/reasoning/context_selection.py` | B1b2 |
| `tools/atlas/platform/context_compilation/snapshot.py` | B1a |
| `tools/atlas/platform/context_compilation/selectors.py` | B1b1 |
| `tests/test_context_selection.py` | B1b2 |
| `tests/test_context_snapshot.py` | B1a |

Four originally planned create paths remain absent:

- `tests/fixtures/task_context/packages/example-eo-2026-013-read-only-assessment-v1.json`;
- `tools/atlas/platform/context_compilation/compiler.py`;
- `tools/atlas/platform/context_compilation/explanation.py`;
- `tests/test_context_compilation.py`.

Five originally planned modify paths remain subject to residual implementation review:

- `tools/atlas/platform/context_compilation/__init__.py`;
- `tools/atlas/platform/context_compilation/models.py`;
- `tools/atlas/platform/context_compilation/digests.py`;
- `tools/atlas/platform/context_compilation/validation.py`;
- `tests/test_context_validation.py`.

The current code contains no materialized source or payload models, no source-content or payload digest helpers, no budget execution, no package assembly, no package integrity helper, no executable compiler, no explanation interface, no committed golden package, and no compilation test module.

---

## 5. Decomposition Decision

### 5.1 Original single B2 checkpoint

Retaining the original single B2 checkpoint is rejected as too broad.

It would combine:

- materialization;
- content identities;
- source and payload models;
- freshness;
- package-ready omissions and unknowns;
- budget measurement and allocation;
- complete package models;
- package assembly;
- package integrity;
- full cross-field validation;
- consumability;
- explanation rendering;
- committed golden reproduction;
- identical-input replay.

That scope would obscure responsibility, increase correction risk, and weaken independent acceptance.

### 5.2 Proposed two-checkpoint B2a/B2b split

The earlier two-checkpoint hypothesis is also rejected as still unbalanced.

Combining materialization and content identity with budgeted package construction would place most remaining models, digest surfaces, orchestration, budget behavior, validation, and tests into one checkpoint. The second checkpoint would then contain mostly evidence and presentation.

### 5.3 Reviewed recommendation

This review recommends, but does not authorize:

1. **B2a — Materialization and Content Identity**
2. **B2b — Budgeted Package Assembly and Validation**
3. **B2c — Golden Replay and Explanation**

The decomposition follows responsibility boundaries already present in the accepted architecture. It does not amend canonical architecture.

---

## 6. Proposed B2a — Materialization and Content Identity

### 6.1 Purpose

Convert one accepted B1b2 selection plan and one accepted B1a immutable snapshot into exact deeply immutable source, payload, and package-ready trace records without applying the byte budget or constructing a context package.

### 6.2 Responsibilities

Proposed B2a would:

- accept an already validated request, loaded policies, accepted repository snapshot, and ready B1b2 selection plan;
- reread only sources selected by B1b2;
- verify exact path, mode, object format, blob identity, and snapshot identity against the plan;
- execute only the selector already carried by each selected plan record;
- retain exact selected payload bytes;
- compute SHA-256 over exact raw immutable source bytes;
- compute SHA-256 over exact selected payload bytes;
- derive the architecture-defined source identifier;
- derive the architecture-defined payload identifier;
- carry selection rule, reason, trigger, chain, authority class, canonical owner, sensitivity, budget tier, selector, transformation, Git identity, source digest, payload digest, media type, encoding, and byte count;
- derive deterministic first-slice freshness status and basis from explicit inputs and immutable repository evidence;
- transform B1b2 omissions and unknowns into package-ready typed records without changing their meaning;
- preserve stable ordering;
- produce one deeply immutable materialization result;
- perform no package or budget work.

The exact freshness record shape must follow the frozen context-package schema and accepted architecture. B2a must not infer external live freshness or use ambient time.

### 6.3 Likely paths

Proposed create paths:

- `tools/atlas/platform/context_compilation/compiler.py`;
- `tests/test_context_compilation.py`.

Proposed modify paths:

- `tools/atlas/platform/context_compilation/__init__.py`;
- `tools/atlas/platform/context_compilation/models.py`;
- `tools/atlas/platform/context_compilation/digests.py`.

`compiler.py` would initially expose narrowly testable materialization capability. It must not claim that complete package compilation exists.

The exact authorized path set requires a separate B2a review. This list is a recommendation, not an implementation scope.

### 6.4 Completion criteria

Proposed B2a would be complete only when:

1. Every selected B1b2 record produces exactly one source record and one payload record.
2. Raw source bytes and selected payload bytes remain distinct.
3. Git object identity, SHA-256 source-content digest, and SHA-256 payload digest remain distinct.
4. Source and payload identifiers match the architecture-defined canonical surfaces.
5. Exact UTF-8 payload byte counts are correct.
6. Selector output bytes and transformation metadata are retained exactly.
7. Authority, provenance, selection trace, sensitivity, budget tier, freshness, and payload linkage are complete.
8. Omissions and unknowns retain their accepted meaning and blocking status.
9. Ordering is deterministic.
10. All returned values are deeply immutable.
11. Identical inputs produce identical materialization values.
12. The repository remains unchanged.
13. No byte budget, package assembly, package integrity, consumability, explanation, or golden fixture is produced.
14. Portable unit tests and a separately classified guarded historical integration test pass.
15. Atlas remains Valid, complete, and Synchronized.

### 6.5 Exclusions

Proposed B2a excludes:

- control-envelope measurement;
- payload allocation or exclusion for capacity;
- budget outcomes;
- package metadata or package status;
- package identity assignment beyond the already accepted helper;
- package integrity digest;
- complete context-package construction;
- full package validation;
- consumability;
- explanation rendering;
- committed golden package;
- Atlas commands;
- dependencies;
- protected-reference behavior changes;
- protected-content access.

### 6.6 Verification boundary

Portable B2a tests should use explicit typed snapshots, plans, and injected or bounded immutable-blob readers without resolving protected references.

A guarded historical integration test may exercise exact immutable reads and selectors against the accepted historical commit. It must remain separately identified from generic portable tests.

### 6.7 Stop conditions

B2a must stop and return for separate review if it requires:

- a schema or policy modification;
- a change to accepted B1a, B1b1, or B1b2 behavior;
- a new dependency;
- protected-content access;
- a new source type;
- external freshness observations;
- package or budget behavior;
- paths outside an accepted future scope.

---

## 7. Proposed B2b — Budgeted Package Assembly and Validation

### 7.1 Purpose

Transform one accepted B2a materialization result into the first complete deterministic context package, enforce the UTF-8 byte budget, compute package integrity, complete invariant validation, and derive consumability.

### 7.2 Responsibilities

Proposed B2b would:

- define the remaining deeply immutable package, budget, validation, conflict, consumer-contract, and consumability models required by the frozen schema;
- copy validated request declarations and resolved policy values without broadening authority;
- assemble repository, task, declared-constraint, source, payload, omission, unknown, conflict, validation, and consumer-contract records;
- reserve and measure the mandatory control envelope through the exact non-self-referential removal surface;
- calculate included payload bytes, consumed bytes, and remaining capacity;
- apply fixed budget-tier allocation order;
- prohibit arbitrary character truncation;
- create deterministic budget omissions only through accepted whole-source or exact-selector boundaries;
- mark mandatory control-envelope or mandatory-tier overflow as non-consumable;
- compute package identity through the accepted request-digest and snapshot-fingerprint helper;
- compute the complete package integrity digest after removing only `package.digest`;
- enforce structural and complete cross-field invariants;
- derive package status, consumability, and stable non-consumable reasons;
- verify source and payload sizes, IDs, digests, ordering, authority, provenance, freshness, traces, sensitivity, mandatory-tier completeness, and consumer contract;
- verify repository non-mutation before returning;
- expose the smallest reusable Python compilation function;
- produce byte-identical canonical JSON for identical explicit inputs.

### 7.3 Likely paths

Proposed modify paths:

- `tools/atlas/platform/context_compilation/compiler.py`;
- `tools/atlas/platform/context_compilation/__init__.py`;
- `tools/atlas/platform/context_compilation/models.py`;
- `tools/atlas/platform/context_compilation/digests.py`;
- `tools/atlas/platform/context_compilation/validation.py`;
- `tests/test_context_compilation.py`;
- `tests/test_context_validation.py`.

The exact authorized path set requires a separate B2b review.

### 7.4 Completion criteria

Proposed B2b would be complete only when:

1. A complete typed package matching every frozen schema section is assembled in memory.
2. The control-envelope measurement excludes exactly `package.digest`, every `payloads[*].content`, and the entire `budget.measurement`.
3. Budget arithmetic uses safe non-negative integers and exact UTF-8 bytes.
4. Allocation follows the versioned budget policy.
5. Mandatory overflow produces the accepted non-consumable result.
6. No arbitrary character truncation or generated-summary substitution occurs.
7. Package identity and package integrity remain distinct.
8. Package integrity removes only `package.digest`.
9. Complete cross-field validation is independent of any committed golden fixture.
10. Consumability derives only from accepted validation and blocking outcomes.
11. The consumer contract is included in the integrity surface.
12. Identical explicit inputs produce byte-identical canonical package output and identical digest values.
13. The repository remains unchanged.
14. Portable package tests pass.
15. Separately classified guarded integration tests pass.
16. Atlas remains Valid, complete, and Synchronized.

### 7.5 Exclusions

Proposed B2b excludes:

- a committed golden fixture;
- explanation rendering;
- Atlas commands;
- provider adapters;
- task execution;
- autonomy or approval policy;
- schema or policy changes;
- dependencies;
- CI;
- protected-reference behavior changes;
- EO lifecycle changes.

### 7.6 Verification boundary

Complete package validation and consumability must be proven without relying on a committed golden package.

Portable tests should verify deterministic package assembly, budget behavior, digest scopes, schema shape, and invariant failures using explicit immutable inputs.

The historical end-to-end replay remains a separately classified guarded integration test.

### 7.7 Stop conditions

B2b must stop and return for separate review if it requires:

- changing an accepted schema or policy;
- changing accepted B1 or B2a behavior;
- a new dependency;
- weakening digest, budget, authority, or consumer-contract invariants;
- an Atlas command;
- protected-content access;
- hidden ambient time, provider memory, or runtime defaults;
- paths outside an accepted future scope.

---

## 8. Proposed B2c — Golden Replay and Explanation

### 8.1 Purpose

Independently prove the completed executable contract and provide a pure typed explanation projection without reconstructing or changing selection, materialization, budget, validation, or consumability.

### 8.2 Responsibilities

Proposed B2c would:

- create a pure explanation layer over accepted typed selection, materialization, budget, omission, unknown, validation, and consumability records;
- prohibit explanation from discovering sources, rerunning selection, reading repository content, changing ordering, resolving conflicts, or modifying package state;
- compile the accepted historical request through the accepted B2b compiler;
- create the exact committed golden package fixture only after production behavior has passed independent review;
- compare generated canonical package bytes byte-for-byte with the committed fixture;
- independently verify all source IDs, payload IDs, omission IDs, Git identities, source-content digests, payload digests, sizes, ordering, budget measurements, request digest, snapshot fingerprint, package identity, package digest, validation results, and consumer-contract values;
- prove identical-input repeatability;
- prove repository and protected-reference non-mutation;
- add final public-interface, side-effect, mutable-global, and explanation-purity probes.

### 8.3 Likely paths

Proposed create paths:

- `tools/atlas/platform/context_compilation/explanation.py`;
- `tests/fixtures/task_context/packages/example-eo-2026-013-read-only-assessment-v1.json`.

Likely modify paths:

- `tools/atlas/platform/context_compilation/__init__.py`;
- `tests/test_context_compilation.py`.

A dedicated `tests/test_context_explanation.py` is preferred for disjoint test ownership, but it was not part of the original implementation plan. A future B2c authorization must explicitly accept or reject that additional path.

`tools/atlas/platform/context_compilation/models.py` may be modified only if a separately reviewed typed explanation value is necessary. Explanation must not require compiler, digest, budget, or validation behavior changes.

### 8.4 Completion criteria

Proposed B2c would be complete only when:

1. Explanation is a pure deterministic projection over already accepted typed values.
2. Explanation cannot alter source selection, ordering, omissions, unknowns, budget, validation, or consumability.
3. The committed fixture is produced by the accepted real compiler.
4. The fixture is authoritative only for the exact executable request and compiler contract.
5. Compiler output matches the fixture byte-for-byte.
6. Independent expected-value checks verify every normative identity, digest, size, order, trace, budget, validation, and consumer-contract field.
7. Repeated runs produce byte-identical canonical output.
8. Production code has no unreviewed side effects or mutable global state.
9. Repository and protected-reference state remain unchanged.
10. Atlas remains Valid, complete, and Synchronized.

### 8.5 Exclusions

Proposed B2c excludes:

- source discovery;
- selection changes;
- materialization changes;
- budget changes;
- package assembly changes;
- validator changes;
- schema or policy changes;
- Atlas commands;
- execution or autonomy;
- AI-environment changes.

### 8.6 Verification boundary

B2c owns independent golden and explanation evidence, not compiler self-approval.

Expected values must be derived independently from the compiler path wherever practical. The historical replay must remain a clearly identified guarded integration test.

### 8.7 Stop conditions

B2c must stop and return for bounded correction review if evidence reveals a defect requiring any change to:

- accepted schemas or policies;
- B1 behavior;
- B2a materialization;
- B2b budget, package, digest, validation, or consumability behavior;
- protected-reference handling;
- the accepted path scope.

A golden mismatch must not be resolved by silently updating the fixture.

---

## 9. Strict-YAML Dependency Decision

The original Checkpoint B plan required a strict-YAML dependency decision.

Checkpoint B1b1 resolved that first-slice requirement through a repository-owned bounded standard-library parser that:

- accepts only the documented historical Engineering Opportunity subset;
- rejects duplicate keys, anchors, aliases, merge keys, tags, implicit typing, unsupported structures, unsupported indentation, and malformed syntax;
- preserves accepted scalar values as strings;
- supports the required top-level string sequences and block strings;
- produces exact canonical JSON for selected fields.

No third-party YAML dependency is required for proposed B2a, B2b, or B2c.

Any future requirement for a broader YAML contract is outside this first slice and requires separate architecture and dependency review.

---

## 10. Validation, Golden, and Explanation Placement

The decomposition assigns:

- complete package validation and consumability to proposed B2b;
- committed golden-package creation to proposed B2c;
- explanation rendering to proposed B2c.

Complete validation cannot depend on the golden fixture because future packages must validate without a preexisting fixture.

The committed golden fixture must not be created until the production compiler has passed independent review.

Explanation must consume typed accepted results and must not reconstruct selection or compilation.

---

## 11. Shared Verification Rules

Across all proposed checkpoints:

- portable pure tests must remain separable from guarded repository integration tests;
- protected-reference operations must never be hidden inside an unclassified generic test command;
- exact historical replay must identify its immutable commit and tree;
- no test may treat provider memory, ambient time, network state, or working-tree content as normative input;
- repository and ref state must be checked before and after guarded integration;
- public exports must remain minimal and immutable;
- no checkpoint may add an Atlas command;
- no checkpoint may add a dependency without separate owner acceptance;
- generated packages remain non-canonical;
- package presence never creates task authority or execution permission.

---

## 12. Shared Stop Condition

Any need to modify a frozen schema or policy stops the active checkpoint and returns through a separately authorized bounded correction review.

The same stop-and-review rule applies to:

- required changes to a completed checkpoint boundary;
- protected-content access;
- new dependencies;
- new source types;
- external live observations;
- task authority expansion;
- path-scope expansion;
- Atlas-command work;
- lifecycle mutation;
- AI-environment changes.

No active checkpoint may absorb such a change silently.

---

## 13. Decision

The reviewed implementation-sequencing decision is:

| Option | Result |
| --- | --- |
| Retain original single B2 | Rejected as too broad |
| Use two checkpoints B2a/B2b | Rejected as still unbalanced |
| Recommend B2a/B2b/B2c | Recommended |
| Authorize B2a | No |
| Authorize B2b | No |
| Authorize B2c | No |
| Change canonical architecture | No |
| Change EO lifecycle state | No |

The next bounded milestone is obtaining a separate owner decision on proposed B2a — Materialization and Content Identity.

No implementation begins from this review.
