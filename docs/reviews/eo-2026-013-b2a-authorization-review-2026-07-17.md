# EO-2026-013 Checkpoint B2a Authorization Review — July 17, 2026

- Authority class: Human-Authorized Non-Canonical Implementation-Authorization Review
- Canonical: No
- Generated: No
- Status: Revised B2a boundary recommended; implementation not authorized
- Date: July 17, 2026
- Verified canonical baseline: `eb51c2952c1a10c4143cc8f59a3f7798ece1dbef`
- Active Engineering Opportunity: EO-2026-013 — Task-Scoped Agent Context Compilation
- Proposed checkpoint: B2a — Materialization and Content Identity
- Decision authority: Owner

---

## 1. Purpose and Authority Boundary

This review challenges and defines proposed Checkpoint B2a — Materialization and Content Identity before any implementation authority is considered.

It reconciles:

- the accepted task-scoped context-compilation architecture;
- the accepted Checkpoint A, A.1, B1a, B1b1, and B1b2 boundaries;
- the reviewed B2a/B2b/B2c decomposition;
- the frozen context-package schema and versioned selection policy;
- the existing snapshot, selector, reasoning, model, and digest implementations;
- the historical EO-2026-013 request and immutable repository evidence;
- public export and exception boundaries;
- portable and guarded verification requirements; and
- the need for a truthful production module boundary.

This review is non-canonical. It recommends an exact future implementation boundary but does not authorize implementation, alter canonical architecture, modify a schema or policy, change lifecycle state, or create task authority.

This review does not authorize:

- B2a, B2b, or B2c implementation;
- code or test changes;
- package compilation;
- budget execution;
- package assembly or validation;
- a golden package or explanation interface;
- an Atlas command;
- dependencies or continuous integration;
- protected-reference access or modification;
- EO-2026-022 architecture or implementation;
- AI-environment configuration;
- staging, commit, or push.

---

## 2. Verified Read-Only Baseline

The read-only authorization-review capture completed against:

- Branch: `main`.
- `HEAD`, local `main`, and `origin/main`: `eb51c2952c1a10c4143cc8f59a3f7798ece1dbef`.
- Commit subject: `Record EO-2026-013 remaining path decomposition`.
- Current phase: `Task-Scoped Agent Context Compilation Checkpoint B1b2 Complete`.
- Working tree and index: clean.
- Atlas Validate: Valid.
- Atlas Missing: no missing document definitions.
- Atlas Sync: Synchronized.
- No protected-reference test or protected-reference command was executed.
- No repository or protected-reference state was changed.
- Nothing was staged, committed, or pushed.

EO-2026-013 remained `reviewed`. EO-2026-022 — Human Engineering Control Surface remained `captured`.

---

## 3. Preserved Completed Checkpoints

The following checkpoints remain complete, owner-accepted, published, and unchanged:

1. Checkpoint A — Deterministic Foundations.
2. Checkpoint A.1 — Executable-Policy Contract Correction.
3. Checkpoint B1a — Immutable Snapshot Boundary.
4. Checkpoint B1b1 — Deterministic Selector Primitives.
5. Checkpoint B1b2 — Bounded Selection Plan.

B2a must consume these boundaries. It must not rebuild, broaden, silently correct, or reinterpret them.

---

## 4. Review Decision

### 4.1 Retain one B2a checkpoint

B2a remains one coherent independently reviewable checkpoint.

Materialization and content identity are inseparable for the first executable slice:

1. reread a source already selected by B1b2;
2. verify the immutable reread against the accepted plan;
3. execute the selector carried by the plan;
4. retain the exact payload bytes;
5. compute source and payload byte digests;
6. derive stable identities;
7. produce one deeply immutable result.

Dividing record and digest foundations from materialization orchestration would not produce an independently useful capability and would add process without strengthening the engineering boundary.

### 4.2 Revise the module boundary

B2a must not create:

- `tools/atlas/platform/context_compilation/compiler.py`;
- `tests/test_context_compilation.py`.

The accepted implementation plan defines `compiler.py` as the orchestrator for materialization, budgeting, package assembly, and validation. Creating it before those responsibilities exist would falsely imply that a complete package compiler exists.

B2a should instead create:

- `tools/atlas/platform/context_compilation/materialization.py`;
- `tests/test_context_materialization.py`.

`compiler.py` and `tests/test_context_compilation.py` are reserved for proposed B2b — Budgeted Package Assembly and Validation.

### 4.3 Exact recommended future B2a path scope

Create exactly:

1. `tools/atlas/platform/context_compilation/materialization.py`
2. `tests/test_context_materialization.py`

Modify exactly:

3. `tools/atlas/platform/context_compilation/__init__.py`
4. `tools/atlas/platform/context_compilation/models.py`
5. `tools/atlas/platform/context_compilation/digests.py`

This five-path set is recommended but not authorized by this review.

---

## 5. Exact B2a Responsibility

B2a should convert:

- one validated `CompilationRequest`;
- one accepted `RepositorySnapshot`;
- one ready B1b2 `SelectionPlan`;
- and one explicit target repository path

into one deeply immutable materialization result containing exact selected source records, exact payload bytes, content identities, deterministic first-slice freshness, identified omissions, and preserved unknowns.

B2a must perform no budget execution and must not construct a context package.

The public operation should be equivalent to:

```python
materialize_selection_plan(
    *,
    target_repository,
    request,
    snapshot,
    selection_plan,
) -> MaterializationResult
```

A separate `MaterializationRequest` is not recommended because it would duplicate identities already carried by the request, snapshot, and selection plan.

---

## 6. Input Consistency Contract

Before any immutable source read, B2a must verify:

1. `target_repository` is one explicit supported path value.
2. `request` is one validated `CompilationRequest`.
3. `snapshot` is one accepted `RepositorySnapshot`.
4. `selection_plan` is one accepted `SelectionPlan`.
5. `selection_plan.ready_for_compilation` is true.
6. Request task identity matches `selection_plan.request_task_id`.
7. Request selection-policy identifier matches the plan.
8. Request selection-policy version matches the plan.
9. Request selection-policy digest matches the plan.
10. Request repository identity matches the plan and snapshot.
11. Requested revision matches the plan and snapshot.
12. Commit matches the plan and snapshot.
13. Tree matches the plan and snapshot.
14. Object format matches the plan and snapshot.
15. Snapshot mode matches the plan and snapshot.
16. Snapshot fingerprint matches the plan and snapshot.
17. Every selected record is bound to the same commit and object format.
18. Every selected record uses an accepted first-slice selector.
19. Selected records remain in the accepted B1b2 stable order.

Any disagreement is fatal. B2a must not rebuild or repair the selection plan.

---

## 7. Deeply Immutable Record Boundary

B2a should define deeply immutable records equivalent to:

- `ByteDigestRecord`;
- `ImmutableSourceIdentityRecord`;
- `FreshnessRecord`;
- `MaterializedSource`;
- `MaterializedPayload`;
- `IdentifiedOmission`;
- `MaterializationResult`.

Exact class names may be challenged during implementation review only if the responsibility and public contract remain unchanged.

### 7.1 ByteDigestRecord

Required fields:

- `algorithm`;
- `value`.

The initial algorithm is exactly `sha256`. The value is exactly 64 lowercase hexadecimal characters.

A byte digest has no canonicalization field because it hashes exact bytes.

### 7.2 ImmutableSourceIdentityRecord

Required fields:

- `type`;
- `object_format`;
- `value`.

The initial type is `git_blob`.

### 7.3 FreshnessRecord

Required fields:

- `status`;
- `basis`;
- `rule`;
- `as_of`.

Allowed statuses are frozen by the context-package schema:

- `current_at_snapshot`;
- `stale`;
- `unknown`;
- `not_applicable`.

B2a initially emits only the reviewed first-slice statuses and rules defined below.

### 7.4 MaterializedSource

A materialized source must retain:

- the complete original `SelectedSourcePlan`;
- the deterministic package selector descriptor;
- immutable source identity;
- exact source-content byte digest;
- exact selector transformation record;
- deterministic freshness record;
- exact included UTF-8 byte count;
- stable source identifier;
- linked payload identifier.

The complete `SelectedSourcePlan` remains attached because it contains intermediate values not all carried by the frozen package source schema, including source kind, sensitivity, budget tier, rule type, mode, and the structured selector mapping.

### 7.5 MaterializedPayload

Required fields:

- stable payload identifier;
- linked source identifier;
- media type;
- encoding;
- exact content bytes outside canonical metadata;
- exact UTF-8 byte count;
- payload byte digest.

Encoding is exactly `utf-8`.

### 7.6 IdentifiedOmission

An identified omission contains:

- the architecture-defined omission identifier;
- the complete original `SelectionOmissionPlan`.

B2a must not erase trigger, selection chain, rule identity, boundary, individual identity, reason, consequence, blocking state, or reconsideration condition.

### 7.7 MaterializationResult

Required values:

- request task identity;
- repository identity;
- requested revision;
- commit;
- tree;
- object format;
- snapshot mode;
- snapshot fingerprint;
- ordered materialized sources;
- ordered materialized payloads;
- ordered identified omissions;
- ordered original `SelectionUnknownPlan` records.

All values must be deeply immutable and deterministically serializable except exact payload bytes, which remain outside canonical metadata until B2b constructs package values.

---

## 8. Selector Descriptor Contract

B1b2 carries structured selector mappings. The frozen package schema carries one selector string. B2a must retain both the complete structured mapping and one deterministic package descriptor.

### 8.1 YAML-field selector

The first-slice descriptor is:

```text
yaml-fields:/id,/title,/status,/summary
```

Rules:

- preserve the policy field order;
- prefix each field with `/`;
- join fields with commas and no spaces;
- reject empty or unsupported fields;
- do not infer or reorder fields.

### 8.2 Markdown-heading selector

For the first heading occurrence, the descriptor is:

```text
heading:## Initial Milestone
```

Rules:

- preserve heading text exactly;
- accept occurrence `1` only for this first slice;
- introduce no whitespace normalization;
- reject later occurrence values until a separately accepted descriptor contract exists.

The deterministic package descriptor is the selector value used by the source-identifier surface.

---

## 9. Digest and Identity Surfaces

### 9.1 Source-content digest

```text
SHA-256(exact immutable source blob bytes)
```

The Git object header is excluded. No decoding, normalization, or selector transformation occurs before this digest.

### 9.2 Payload digest

```text
SHA-256(exact SelectorOutput.content bytes)
```

The bytes are the exact deterministic selector output.

### 9.3 Source identifier

The source identifier is:

```text
src- + first 16 lowercase hexadecimal characters of:
SHA-256(
  RFC 8785 canonical JSON UTF-8 bytes of:
  {
    "source_identity": {
      "path": path,
      "commit": commit,
      "blob": blob
    },
    "selector": package_selector_descriptor
  }
)
```

### 9.4 Payload identifier

The payload identifier is:

```text
payload- + first 16 lowercase hexadecimal characters of payload digest
```

### 9.5 Omission identifier

The omission identifier is:

```text
omit- + first 16 lowercase hexadecimal characters of:
SHA-256(
  RFC 8785 canonical JSON UTF-8 bytes of:
  {
    "rule": exclusion_rule_id,
    "boundary": boundary,
    "individual": individual
  }
)
```

For policy-class omissions, `individual` is null.

### 9.6 Collision behavior

Any duplicate or collision involving:

- source identifiers;
- payload identifiers;
- omission identifiers;
- incompatible source-to-payload links;
- or identities with unequal complete records

is fatal.

B2a must not silently deduplicate, suffix, renumber, or reinterpret colliding identities.

---

## 10. Immutable Reread and Selector Execution

For each selected record in accepted stable order, B2a must:

1. call the accepted immutable `read_snapshot_blob`;
2. require exact path equality;
3. require exact mode equality;
4. require exact object-format equality;
5. require exact blob-identity equality;
6. require the selected record commit to equal the snapshot commit;
7. require the selection plan tree to equal the snapshot tree;
8. execute only the selector carried by the selected record;
9. retain the exact selector output bytes;
10. build exact transformation metadata;
11. compute the reviewed digests and identities;
12. construct immutable source and payload records.

B1b2 already determined that these records are selected.

Therefore, after an accepted plan:

- missing or mismatched immutable source identity is fatal;
- blob reread failure is fatal;
- selector encoding failure is fatal;
- selector syntax failure is fatal;
- selector target failure is fatal;
- unsupported selector behavior is fatal.

B2a must not convert these failures into new omissions or unknowns. Doing so would silently change B1b2 selection reasoning.

---

## 11. First-Slice Freshness Contract

Freshness is snapshot-relative and does not claim present-day real-world currency.

`as_of` is copied exactly from the request. It is the comparison reference and is not evidence by itself.

B2a must not use:

- wall-clock time;
- file age;
- provider memory;
- network state;
- Atlas execution;
- unselected source reads;
- working-tree content;
- external observations;
- inferred synchronization state.

### 11.1 Selected Engineering Opportunity object

Emit:

- status: `current_at_snapshot`;
- rule: `F010-pinned-canonical-source`.

Only when:

- the exact immutable blob matches the selected plan;
- the registered object path and structured object identity match;
- the canonical owner matches the selected path;
- the selected lifecycle value comes from the accepted selector output;
- no blocking B1b2 record exists for the boundary.

### 11.2 Selected ordinary canonical documents

For the selected Repository Architecture, Knowledge Authority Architecture, and Engineering Collaboration Standard, emit:

- status: `current_at_snapshot`;
- rule: `F010-pinned-canonical-source`.

Only when:

- the exact immutable blob and selector match the accepted plan;
- the canonical owner matches the selected path;
- the requested snapshot is the task authority boundary;
- no selected evidence marks the source superseded or stale;
- no blocking B1b2 record exists for the boundary.

### 11.3 Current Mission

For `docs/current-mission.md`, emit:

- status: `unknown`;
- rule: `F020-current-mission-synchronization-unverified`.

Basis:

> The exact Current Mission source is established at the pinned snapshot, but the compilation inputs contain no independent synchronization finding proving semantic alignment.

B2a must not invoke Atlas, read generated context, or use the current working tree to upgrade this status.

### 11.4 Unsupported freshness classes

B2a does not initially emit `stale` or `not_applicable`.

A selected source class or evidence condition outside these exact rules stops the checkpoint for bounded review.

---

## 12. Omission and Unknown Preservation

### 12.1 Omissions

B2a enriches each `SelectionOmissionPlan` only with its architecture-defined omission identifier.

It must preserve the complete original plan record unchanged.

It must not add budget consequence values because budget behavior belongs to B2b.

### 12.2 Unknowns

B2a preserves every `SelectionUnknownPlan` unchanged.

It must not invent a package unknown identifier because the accepted architecture does not define that identity surface.

It must not perform additional resolution attempts.

### 12.3 B2b trace decision

Final package unknown identifiers and final package trace projection remain B2b decisions.

The frozen package schema is narrower than the B1b2 planning records. If B2b cannot preserve the accepted trace contract without modifying the schema, B2b must stop and return through a separately authorized bounded correction review.

No schema defect is declared by this B2a review.

---

## 13. Exception Boundary

Recommended public hierarchy:

```text
MaterializationError
├── MaterializationContractError
├── MaterializationIdentityError
└── MaterializationSourceError
```

### MaterializationContractError

Covers:

- wrong input types;
- request, snapshot, or selection-plan inconsistency;
- unready plan;
- unsupported selector descriptor;
- unsupported freshness class;
- invalid ordering;
- unsupported first-slice behavior.

### MaterializationIdentityError

Covers:

- immutable reread identity mismatch;
- digest or identifier collision;
- source-to-payload linkage disagreement;
- malformed identity inputs.

### MaterializationSourceError

Covers:

- accepted immutable-blob reread failure;
- selector execution failure after an accepted plan;
- invalid exact payload bytes.

Exceptions must not contain arbitrary source or payload content.

Snapshot and selector implementation exceptions remain owned by their accepted modules. The public materialization operation should translate them into the bounded materialization hierarchy while preserving safe causality.

---

## 14. Minimal Public Exports

Recommended additions to the context-compilation public interface:

- `materialize_selection_plan`;
- `MaterializationError`;
- `MaterializationContractError`;
- `MaterializationIdentityError`;
- `MaterializationSourceError`;
- `ByteDigestRecord`;
- `ImmutableSourceIdentityRecord`;
- `FreshnessRecord`;
- `MaterializedSource`;
- `MaterializedPayload`;
- `IdentifiedOmission`;
- `MaterializationResult`;
- reviewed byte-digest and identity helpers required for independent verification.

Exports must be explicit and immutable.

No compiler, package, budget, validation, consumability, explanation, Atlas, repository-discovery, network, clock, or mutable-global capability may be exported.

---

## 15. Portable Verification Boundary

`tests/test_context_materialization.py` should contain pure portable tests for:

- deeply immutable records;
- defensive copies of nested input values;
- exact byte-digest vectors;
- exact YAML selector descriptor;
- exact Markdown selector descriptor;
- rejected unsupported selectors or occurrences;
- exact source-identifier vectors;
- exact payload-identifier vectors;
- exact omission-identifier vectors;
- request, snapshot, and plan consistency checks;
- unready plan rejection;
- injected exact immutable blob values;
- exact source and payload byte preservation;
- exact transformation records;
- exact UTF-8 byte counts;
- deterministic freshness records;
- Current Mission freshness remaining `unknown`;
- omission-ID enrichment without semantic change;
- unknown records preserved without semantic change;
- stable ordering;
- duplicate and collision rejection;
- repeatability;
- safe exception messages;
- no mutable module-level state;
- exact minimal public exports;
- no filesystem open, subprocess, network, environment, clock, randomness, budget, compiler, validator, package, explanation, or Atlas capability.

Portable tests must not resolve a Git snapshot or inspect a protected reference.

---

## 16. Guarded Historical Integration Boundary

The guarded historical integration must use:

- commit: `79eef80af3d5969ece7eb9fe7f802be35575f450`;
- tree: `3d2853517e64209cffde91766a62e9f70ceb2e47`.

It must:

1. verify the clean current repository before execution;
2. verify expected current branch and refs without accessing protected content;
3. construct the already accepted historical `RepositorySnapshot`;
4. use the accepted historical request and selection policy identities;
5. build or load the accepted B1b2 five-source selection plan;
6. reread only the five selected immutable blobs;
7. execute only the accepted YAML-field and heading selectors;
8. verify exact source blob identities;
9. verify exact raw source SHA-256 values;
10. verify exact selector output bytes;
11. verify exact payload SHA-256 values;
12. verify exact UTF-8 byte counts;
13. verify exact source, payload, and omission identifiers;
14. verify exact transformation records;
15. verify exact source ordering;
16. verify exact first-slice freshness values;
17. verify worktree, index, refs, and accepted source files remain unchanged;
18. record the exact Git commands invoked;
19. prove no protected-reference command, ref mutation, network operation, repository write, Atlas command, budget behavior, or package compilation occurred.

The guarded integration remains separately classified from generic portable tests.

---

## 17. Completion Criteria

B2a would be implementation-complete only when:

1. The exact authorized future path set is respected.
2. Every selected B1b2 record produces exactly one materialized source and payload.
3. Raw source bytes and selected payload bytes remain distinct.
4. Git object identity, source-content SHA-256, and payload SHA-256 remain distinct.
5. Source, payload, and omission identifiers match the accepted surfaces.
6. Exact selector output bytes are retained.
7. Exact UTF-8 payload sizes are correct.
8. Complete B1b2 source planning records are preserved.
9. Omissions gain only their deterministic IDs.
10. Unknowns remain semantically unchanged.
11. First-slice freshness follows the exact reviewed rules.
12. Ordering remains deterministic.
13. All returned values are deeply immutable.
14. Identical inputs produce equal values and identical normative metadata.
15. All collision and disagreement cases stop.
16. No budget, package, validation, consumability, explanation, or golden-fixture capability exists.
17. Portable tests pass.
18. The separately classified guarded historical integration passes.
19. The repository and protected-reference state remain unchanged.
20. Atlas remains Valid, complete, and Synchronized.
21. An independent final acceptance review passes.
22. The owner separately accepts completion before recording, commit, or push.

---

## 18. Stop Conditions

B2a must stop and return for separately authorized review if implementation requires:

- any context-package schema modification;
- any selection or budget policy modification;
- a change to Checkpoint A, A.1, B1a, B1b1, or B1b2 behavior;
- a third-party dependency;
- a new source type;
- a broader selector contract;
- a heading occurrence beyond the reviewed first slice;
- external or live freshness observation;
- Atlas execution;
- unselected freshness reads;
- protected-content access;
- protected-reference behavior changes;
- budget behavior;
- package construction;
- final package unknown-ID invention;
- final package trace loss;
- paths outside the separately accepted future implementation scope;
- task-authority expansion;
- lifecycle mutation;
- AI-environment changes.

No such issue may be silently absorbed into B2a.

---

## 19. Excluded Future Responsibilities

B2a excludes:

- `compiler.py`;
- `tests/test_context_compilation.py`;
- `explanation.py`;
- package fixtures;
- budget allocation;
- control-envelope measurement;
- package metadata and status;
- package identity assignment beyond existing accepted helpers;
- package integrity;
- complete package construction;
- final unknown and omission package projection;
- cross-field package validation;
- consumability;
- golden replay;
- explanation rendering;
- Atlas commands;
- provider adapters;
- task execution;
- autonomy or approval policy;
- dependency and CI changes;
- protected-reference behavior changes.

These remain proposed B2b, B2c, or separately reviewed future responsibilities.

---

## 20. Decision

| Question | Result |
| --- | --- |
| Retain B2a as one checkpoint | Yes |
| Divide B2a further | No |
| Use `compiler.py` in B2a | No |
| Use `materialization.py` in B2a | Recommended |
| Use `test_context_materialization.py` in B2a | Recommended |
| Reserve compiler and compilation tests for B2b | Yes |
| Recommend exact five-path B2a scope | Yes |
| Use complete B1b2 source records internally | Yes |
| Preserve unknown records unchanged | Yes |
| Add omission IDs in B2a | Yes |
| Define final package unknown IDs in B2a | No |
| Implement B2a | No |
| Authorize B2a | No |
| Authorize B2b | No |
| Authorize B2c | No |
| Change architecture, schema, or policy | No |
| Change EO lifecycle state | No |

The next bounded milestone is obtaining a separate owner decision on implementation of the revised B2a boundary.

No implementation begins from this review.
