# EO-2026-013 Executable-Path Review — July 16, 2026

**Date:** July 16, 2026
**Repository baseline:** `6e0fb536eac8113a2a07547661d5a9b89c0a65b6`
**Authority class:** Human-Reviewed Implementation-Planning Decision
**Canonical:** No
**Generated:** No
**Status:** Checkpoint A.1 Completion Accepted; B1 and B2 Withheld
**Owner decision recorded:** July 16, 2026
**Current state:** Checkpoint A and A.1 complete and owner-accepted; B1 and B2 unauthorized

---

## Recorded Owner Decision

> Accept the revised EO-2026-013 executable-path plan. Authorize Checkpoint A.1 — Executable-Policy Contract Correction only. Do not authorize Checkpoint B1 or Checkpoint B2. Preserve the protected branch content as out of scope; authorize only identity comparison of the declared protected ref during later B1 review.

Recorded July 16, 2026.

## Checkpoint A.1 Completion Acceptance

The owner recorded:

> Accept EO-2026-013 Checkpoint A.1 as complete. Authorize recording, committing, and pushing the Checkpoint A.1 completion. Do not authorize Checkpoint B1 or Checkpoint B2. Preserve the protected branch content as out of scope.

Recorded July 16, 2026.

The accepted implementation:

- modified exactly the ten authorized existing files;
- created and deleted no files;
- advanced the selection-policy instance to `1.0.1`;
- preserved the budget-policy instance at `1.0.0`;
- added the exact accepted budget tier and `public` sensitivity to all five first-replay sources;
- preserved the budget schema and policy byte-for-byte;
- preserved the four stable schema URNs;
- recomputed every affected policy, request, and package-identity foundation value;
- passed 90 tests;
- passed independent negative, sensitivity-bound, version, digest, identity, and structural-reference probes;
- left Atlas Valid, complete, and Synchronized; and
- performed no B1, B2, dependency, protected-branch access, staging, commit, or push before owner acceptance.

Checkpoint B1 and Checkpoint B2 remain unauthorized.

## Accepted Recommendation

Do not authorize the existing Checkpoint B plan unchanged.

The executable direction remains valid, but implementation should proceed through:

1. **Checkpoint A.1 — Executable-Policy Contract Correction**
2. **Checkpoint B1 — Immutable Snapshot, Selectors, and Selection Plan**
3. **Checkpoint B2 — Compilation, Integrity Validation, Explanation, and Golden Replay**

Checkpoint A.1 was the only implementation checkpoint authorized by that decision.

This preserves the architecture while preventing the compiler from inventing policy behavior and avoids combining Git plumbing, a strict YAML subset, source selection, budgeting, package construction, validation, explanations, and golden reproduction into one oversized implementation change.

---

## Why the Current Checkpoint B Plan Needs Revision

### 1. Budget allocation is not fully policy-owned

The budget policy defines this exact allocation order:

1. `mandatory_control_envelope`
2. `mandatory_authoritative_sources`
3. `required_supporting_sources`
4. `optional_evidence`

The selection policy rules currently contain:

- rule ID;
- rule type;
- `priority_tier`;
- source;
- selector.

They do not declare a budget tier.

Without an explicit digest-bound mapping, the compiler would need to infer or hard-code whether a source is mandatory authoritative, required supporting, or optional. That would make normative budget behavior depend on implementation knowledge rather than the versioned policy.

The same missing classification controls whether a failed mandatory selector becomes a blocking unknown or whether an optional source becomes an omission.

### 2. Sensitivity enforcement lacks a deterministic source classification

The policy declares `maximum_sensitivity: ordinary_personal`, but its rules do not classify the sensitivity of each exact source.

For this public historical replay, all five selected sources can be explicitly classified as `public`. That classification should be policy-owned and digest-bound rather than inferred from an ambient hosting assumption.

### 3. The implementation checkpoint is too broad

The current Checkpoint B combines:

- clean Git snapshot verification;
- replacement and alternate object-store rejection;
- protected-reference validation;
- raw tree/blob reads;
- strict YAML parsing;
- heading selection;
- relationship verification;
- deterministic selection and omissions;
- source and payload materialization;
- budgeting;
- package construction;
- package identity and integrity;
- invariant validation;
- explanations;
- golden-fixture generation;
- byte-identical replay tests.

Those are two coherent engineering checkpoints, not one.

### 4. Golden generation needs a clean target repository separate from the implementation worktree

The compiler’s target repository must be clean before and after compilation. During implementation, the source worktree is necessarily dirty.

The implementation must therefore:

- accept an explicit target repository path rather than silently using the current working directory;
- run historical replay tests against an isolated clean full clone or equivalent target;
- execute compiler code from the implementation environment while reading only immutable objects from the clean target;
- never write to the target repository.

### 5. Protected-reference validation needs an exact authorization boundary

Checkpoint B must compare the declared protected ref name with its expected immutable object identity.

That authorizes only identity resolution. It does not authorize:

- checkout;
- switching;
- tree or blob reads;
- selection;
- traversal;
- modification;
- merge;
- deletion.

The protected branch’s content remains completely out of scope.

### 6. Relationship verification must use historical repository-object metadata

The two relationship-selected documents must be verified against the pinned EO object’s `related_documents` metadata.

The strict YAML subset therefore needs two distinct uses:

- materialize only the policy-allowlisted payload fields `id`, `title`, `status`, and `summary`;
- inspect `related_documents` as repository-object relationship metadata without adding it to the payload.

A rule of type `allowlisted_relationship` is valid only when the exact named target is present in the historical relationship field and the relationship type/direction is allowlisted.

The global relationship allowlist must not trigger a whole-edge scan. Only exact policy-named relationship candidates are considered.

---

## Checkpoint A.1 — Executable-Policy Contract Correction

### Purpose

Complete the policy information required for deterministic budgeting, missing-selector behavior, and sensitivity enforcement before executable work begins.

### Exact policy changes

Add to every selection rule:

```json
"budget_tier": "mandatory_authoritative_sources | required_supporting_sources | optional_evidence"
```

Add to every rule source:

```json
"sensitivity": "public | ordinary_personal | sensitive | highly_restricted"
```

Assign:

| Rule | Budget tier | Sensitivity |
|---|---|---|
| `S010-explicit-opportunity-anchor` | `mandatory_authoritative_sources` | `public` |
| `S020-current-mission-milestone` | `mandatory_authoritative_sources` | `public` |
| `S030-canonical-repository-authority` | `required_supporting_sources` | `public` |
| `S040-mandatory-knowledge-authority` | `required_supporting_sources` | `public` |
| `S050-mandatory-collaboration` | `required_supporting_sources` | `public` |

No optional source exists in the first replay.

### Version decision

Advance the selection-policy instance from `1.0.0` to `1.0.1`.

Keep the budget policy at `1.0.0`.

Split the current shared runtime version constant into separate selection-policy and budget-policy constants.

The v1 schema receives an explicitly recorded pre-executable defect correction. This is not silent reinterpretation: the correction is reviewed, digest-changing, tested, and committed before any executable package exists.

### Exact implementation scope

Modify only:

- `docs/task-context/index.md`
- `docs/task-context/schemas/selection-policy-v1.schema.json`
- `docs/task-context/schemas/compilation-request-v1.schema.json`
- `docs/task-context/schemas/context-package-v1.schema.json`
- `docs/task-context/policies/selection/example-read-only-architecture-assessment-v1.json`
- `tests/fixtures/task_context/requests/example-eo-2026-013-read-only-assessment-v1.json`
- `tests/fixtures/task_context/expected/example-eo-2026-013-foundation-values-v1.json`
- `tools/atlas/platform/context_compilation/validation.py`
- `tests/test_context_inputs.py`
- `tests/test_context_validation.py`

No files are created.

### Required verification

- selection policy version is `1.0.1`;
- budget policy version remains `1.0.0`;
- selection-policy digest is recomputed;
- request digest is recomputed;
- package-identity helper values are recomputed;
- all five rules have exact budget tier and sensitivity;
- every source sensitivity is at or below the maximum;
- budget tier values are members of the budget policy’s source allocation tiers;
- no compiler, snapshot adapter, selector, selection reasoning, package fixture, or Checkpoint B test is created;
- all tests and Atlas checks pass.

---

## Checkpoint B1 — Immutable Selection Path

B1 remains unauthorized and requires a separate owner decision after A.1 completion.

### Create

- `tools/atlas/platform/reasoning/context_selection.py`
- `tools/atlas/platform/context_compilation/snapshot.py`
- `tools/atlas/platform/context_compilation/selectors.py`
- `tests/test_context_selection.py`
- `tests/test_context_snapshot.py`
- `tests/test_context_selectors.py`

### Modify

- `tools/atlas/platform/context_compilation/__init__.py`
- `tools/atlas/platform/context_compilation/models.py`

### Responsibilities

- explicit target repository path;
- clean pre/post state;
- one-time commit/tree resolution;
- repository identity verification;
- SHA-1 object-format verification for the fixture;
- raw tree/blob reads;
- path normalization;
- replacement and alternate object-store rejection;
- symlink/gitlink rejection;
- identity-only protected-ref verification;
- strict bounded YAML parsing;
- exact heading selection with LF/CRLF preservation;
- historical relationship verification;
- typed selected, omitted, unknown, and selection-plan output;
- stable selection ordering and reasons.

### Excluded

- compiler;
- budget calculation;
- package assembly;
- package digest;
- package fixture;
- explanation renderer;
- consumability;
- Atlas command.

---

## Checkpoint B2 — Compilation and Golden Replay

B2 remains unauthorized and requires a separate owner decision after B1 completion.

### Create

- `tests/fixtures/task_context/packages/example-eo-2026-013-read-only-assessment-v1.json`
- `tools/atlas/platform/context_compilation/compiler.py`
- `tools/atlas/platform/context_compilation/explanation.py`
- `tests/test_context_compilation.py`
- `tests/test_context_explanation.py`

### Modify

- `tools/atlas/platform/context_compilation/__init__.py`
- `tools/atlas/platform/context_compilation/models.py`
- `tools/atlas/platform/context_compilation/digests.py`
- `tools/atlas/platform/context_compilation/validation.py`
- `tests/test_context_validation.py`

### Responsibilities

- payload materialization from the accepted B1 plan;
- source, payload, snapshot, identity, and package digests;
- deterministic budget application using policy-owned tiers;
- package assembly;
- internal validation state before integrity hashing;
- package integrity computation;
- independent complete invariant validation;
- deterministic explanations derived only from typed plan/package values;
- canonical JSON golden fixture;
- identical-input byte reproduction.

### Excluded

- Atlas command;
- generic discovery;
- task-contract implementation;
- execution;
- autonomy;
- provider routing;
- AI-environment integration;
- lifecycle mutation.

---

## Strict YAML Decision

Use a repository-local standard-library bounded parser in `selectors.py`.

Do not introduce PyYAML or another dependency in this checkpoint.

The parser supports only the exact top-level subset needed by the historical Engineering Opportunity object:

- string keys;
- plain or quoted string scalars;
- top-level string sequences;
- folded (`>`) and literal (`|`) block strings;
- UTF-8 without BOM.

It rejects:

- duplicate keys;
- anchors and aliases;
- merge keys;
- tags;
- implicit timestamps, booleans, nulls, and numbers;
- flow collections;
- nested mappings;
- complex keys;
- tabs;
- multi-document streams;
- unsupported directives or scalar forms.

This parser must not reuse the existing working-tree `parse_simple_yaml` implementation.

---

## Decision Traceability

- Checkpoint A completion: `6e0fb536eac8113a2a07547661d5a9b89c0a65b6`.
- Revised executable-path plan accepted: July 16, 2026.
- Checkpoint A.1 authorization baseline: `1f2595b8a3489979b275dfad0884b4e0fe09c585`.
- Checkpoint A.1 completion accepted: July 16, 2026.
- Checkpoint A.1 exact implementation scope: ten modified existing files, no created or deleted files.
- Selection-policy version: `1.0.1`.
- Budget-policy version: `1.0.0`.
- Final technical verification: 90 tests passed; Atlas Valid, complete, and Synchronized; independent contract and deterministic-transition probes passed.
- Checkpoint B1 authorized: No.
- Checkpoint B2 authorized: No.
- Protected branch content in scope: No.
- Protected-ref identity comparison authorized: No.
- Future protected-ref identity comparison: planned only, subject to separate B1 authorization.
- EO-2026-013 lifecycle state: `reviewed`.
- Next decision gate: separate owner authorization, revision, deferral, or rejection of Checkpoint B1.

STOP — Preserve Checkpoint A.1. Do not begin B1 or B2 without a separate owner decision.
