# EO-2026-013 Checkpoint B2a Structured-Object Ownership Contract-Correction Review — July 17, 2026

- Authority class: Human-Authorized Non-Canonical Contract-Correction Review
- Canonical: No
- Generated: No
- Status: Correction recorded; implementation correction not authorized
- Date: July 17, 2026
- Verified canonical baseline: `937dc844ce894ec6237e1aaa3a31dfa514c3f419`
- Active Engineering Opportunity: EO-2026-013 — Task-Scoped Agent Context Compilation
- Checkpoint: B2a — Materialization and Content Identity
- Decision authority: Owner

---

## 1. Purpose and Authority Boundary

This review records a bounded correction to the previously published B2a authorization-review contract after the first guarded historical integration exposed an ownership-semantic mismatch.

It determines:

- the distinction between an immutable selected source path, a structured object identity, and a canonical or field-contract owner;
- the exact first-slice ownership and freshness conditions for the selected EO-2026-013 object;
- the ownership rule that continues to apply to ordinary canonical documents;
- whether the defect belongs to architecture, schema, policy, B1b2, the B2a review, or the current B2a implementation;
- the exact future documentation and implementation correction scope;
- the required regression tests;
- completion and stop conditions; and
- the downstream B2b boundary for final package projection.

This review is non-canonical. It records a correction decision but does not implement or authorize the correction, accept B2a as complete, begin B2b or B2c, change architecture, change a schema or policy, alter Engineering Opportunity lifecycle state, or modify protected-reference behavior.

The original B2a authorization review remains unchanged as historical evidence.

---

## 2. Verified In-Progress State

The review used canonical repository commit:

`937dc844ce894ec6237e1aaa3a31dfa514c3f419`

The working tree contained exactly the authorized five-path in-progress B2a implementation:

1. `tools/atlas/platform/context_compilation/materialization.py`
2. `tests/test_context_materialization.py`
3. `tools/atlas/platform/context_compilation/__init__.py`
4. `tools/atlas/platform/context_compilation/models.py`
5. `tools/atlas/platform/context_compilation/digests.py`

Verification established:

- all 11 focused portable B2a tests passed;
- the guarded historical integration stopped before source materialization;
- the exact error was `MaterializationContractError: selected canonical owner is inconsistent`;
- no implementation file changed during either verification-resume attempt;
- the exact five implementation SHA-256 values remained stable;
- the staged set remained empty;
- nothing was committed or pushed.

The guarded stop was an authorized contract-review condition rather than evidence that completed B1b2 behavior should be changed.

---

## 3. Confirmed Conflict

The original B2a authorization review required the selected Engineering Opportunity object's `canonical_owner` to match the selected source path.

The accepted B1b2 contract instead carries three separate values:

- selected immutable source path;
- structured object identity;
- canonical or field-contract owner.

For EO-2026-013, B1b2 emits:

```text
selected immutable source path:
docs/opportunities/reviewed/EO-2026-013-task-scoped-agent-context-compilation.yaml

structured object identity:
engineering-opportunity:EO-2026-013

canonical or field-contract owner:
docs/architecture/engineering-opportunity-object.md
```

The current B2a implementation incorrectly applied one universal invariant:

```text
canonical_owner == selected source path
```

The portable EO fixture repeated that incorrect assumption, so portable coverage did not expose the conflict. The guarded historical integration consumed the accepted B1b2 plan and correctly stopped.

---

## 4. Correct Semantic Distinction

### 4.1 Selected immutable source path

The selected immutable source path identifies the exact repository file whose bytes are reread from the accepted B1a snapshot.

For EO-2026-013:

```text
docs/opportunities/reviewed/EO-2026-013-task-scoped-agent-context-compilation.yaml
```

This path participates in:

- immutable Git tree lookup;
- exact mode and blob verification;
- source-content digest calculation;
- source identifier construction;
- selector execution; and
- payload materialization.

It does not by itself define the structured object type's field contract.

### 4.2 Structured object identity

The structured object identity identifies the logical Repository Object independently of its lifecycle directory or physical file path.

For EO-2026-013:

```text
engineering-opportunity:EO-2026-013
```

This identity must remain stable when an Engineering Opportunity moves between lifecycle directories.

It is not a Git path and is not the field-contract owner.

### 4.3 Canonical or field-contract owner

For the first-slice structured Engineering Opportunity source, `canonical_owner` identifies the repository architecture document that owns the object's field and lifecycle contract:

```text
docs/architecture/engineering-opportunity-object.md
```

This value explains who defines the structured object's contract. It does not replace the selected immutable source path and must not be used as the blob-read path.

For ordinary canonical documents, the selected document is also the canonical owner of the selected knowledge, so `canonical_owner` continues to equal the selected path.

---

## 5. Corrected First-Slice EO Contract

The selected EO source may receive:

- freshness status: `current_at_snapshot`;
- freshness rule: `F010-pinned-canonical-source`;

only when all of the following independently hold:

1. The selected path is exactly:
   `docs/opportunities/reviewed/EO-2026-013-task-scoped-agent-context-compilation.yaml`.
2. The selected structured object identity is exactly:
   `engineering-opportunity:EO-2026-013`.
3. The selected canonical or field-contract owner is exactly:
   `docs/architecture/engineering-opportunity-object.md`.
4. The authority class is exactly:
   `structured_repository_object`.
5. The source kind is exactly:
   `repository_object`.
6. The rule identifier is exactly:
   `S010-explicit-opportunity-anchor`.
7. The rule type is exactly:
   `explicit_anchor`.
8. The exact path, commit, mode, object format, blob identity, and selector match the accepted B1b2 plan.
9. The selector output identifies `EO-2026-013`.
10. The selector output carries lifecycle status `reviewed`.
11. No blocking B1b2 omission or unknown exists.
12. No new selection reasoning is introduced.

The selected source path, structured identity, and field-contract owner are three separate validated values.

The corrected contract supersedes only the original review clause requiring the structured EO object's owner to equal its selected source path.

---

## 6. Ordinary Canonical Documents and Current Mission

### 6.1 Ordinary canonical documents

The following selected ordinary canonical documents continue to require `canonical_owner` to equal their selected path:

- Repository Architecture:
  `docs/architecture/repository.md`;
- Knowledge Authority Architecture:
  `docs/architecture/knowledge-authority.md`;
- Engineering Collaboration Standard:
  `docs/standards/engineering-collaboration.md`.

Their first-slice freshness may remain `current_at_snapshot` through `F010-pinned-canonical-source` only under the already reviewed immutable-source, selector, owner, snapshot, and nonblocking-plan conditions.

### 6.2 Current Mission

Current Mission continues to use:

- selected path:
  `docs/current-mission.md`;
- canonical owner:
  `docs/current-mission.md`;
- freshness status:
  `unknown`;
- freshness rule:
  `F020-current-mission-synchronization-unverified`.

Owner equality does not provide independent synchronization evidence.

B2a must not invoke Atlas, inspect generated context, read an unselected source, use wall-clock time, or use the working tree to upgrade Current Mission freshness.

---

## 7. Defect Classification

### 7.1 Original B2a authorization-review defect

Confirmed.

The review conflated the structured object's selected immutable source location with the architecture document that owns its field contract.

The original review remains unchanged as historical evidence. This correction review supersedes only that ownership clause.

### 7.2 Current B2a implementation defect

Confirmed and bounded.

`materialization.py` applies the incorrect owner-equals-path invariant universally and repeats it in the EO freshness condition.

### 7.3 Focused portable-test defect

Confirmed and bounded.

The portable EO fixture uses the selected YAML path as `canonical_owner`, so it does not reproduce the accepted B1b2 plan.

### 7.4 Accepted B1b2 defect

Not found.

B1b2 intentionally retains the selected source path, structured object identity, and field-contract owner separately. That distinction is useful and must remain unchanged.

### 7.5 Selection-policy defect

Not found.

The accepted first-slice selection contract binds the Engineering Opportunity object to the Engineering Opportunity Object Architecture as its field-contract owner.

### 7.6 Schema defect

Not found for B2a.

The source schema carries repository path or structured identity separately from canonical owner and does not impose universal owner equality.

### 7.7 Architecture defect

No architecture change is required to complete B2a.

An older informative manual package example used the EO YAML path as `canonical_owner`, while accepted B1b2 uses the architecture document as field-contract owner. This does not block B2a because B2a retains the complete accepted `SelectedSourcePlan`.

Final package projection remains a B2b decision. B2b must stop for bounded architecture or schema clarification if one final package field cannot preserve the accepted distinction without ambiguity or information loss.

---

## 8. Exact Future Implementation Correction Scope

The existing five-path implementation may be retained.

A future separately authorized correction should modify only:

1. `tools/atlas/platform/context_compilation/materialization.py`
2. `tests/test_context_materialization.py`

These existing in-progress implementation files must remain byte-identical during this documentation-only recording:

1. `tools/atlas/platform/context_compilation/__init__.py`
2. `tools/atlas/platform/context_compilation/models.py`
3. `tools/atlas/platform/context_compilation/digests.py`

### 8.1 Materialization correction

Replace universal owner equality with exact rule-specific owner validation:

| Rule | Required owner |
| --- | --- |
| `S010-explicit-opportunity-anchor` | `docs/architecture/engineering-opportunity-object.md` |
| `S020-current-mission-milestone` | `docs/current-mission.md` |
| `S030-canonical-repository-authority` | `docs/architecture/repository.md` |
| `S040-mandatory-knowledge-authority` | `docs/architecture/knowledge-authority.md` |
| `S050-mandatory-collaboration` | `docs/standards/engineering-collaboration.md` |

The EO freshness check must validate source path, structured identity, owner, authority class, source kind, selected object identity, and selected lifecycle state independently.

Ownership disagreement remains fatal. It must not become a new omission or unknown.

### 8.2 Focused-test correction

The portable EO fixture must use the accepted B1b2 field-contract owner.

Portable tests must prove that the three concepts cannot be substituted for one another.

---

## 9. Required Regression Tests

The bounded correction must add or preserve tests proving:

1. The exact EO YAML path, EO structured identity, and EO architecture owner succeed together.
2. An EO plan whose owner incorrectly equals its YAML source path fails before any blob read.
3. An EO plan with the correct owner but wrong source path fails before any blob read.
4. An EO plan with the correct owner and path but wrong structured identity fails before any blob read.
5. An EO plan with the wrong authority class fails before any blob read.
6. An EO plan with the wrong source kind fails before any blob read.
7. An ordinary canonical document whose owner equals its selected path succeeds.
8. An ordinary canonical document whose owner points to the EO architecture fails before any blob read.
9. Current Mission remains freshness `unknown`.
10. The materialized EO source retains the complete original `SelectedSourcePlan` unchanged.
11. Ownership disagreement creates no new omission or unknown.
12. The guarded historical five-source integration passes.
13. Historical source order remains exact.
14. Historical blob identities remain exact.
15. Historical raw source digests remain exact.
16. Historical selector outputs remain exact.
17. Historical payload digests and byte counts remain exact.
18. Historical transformations remain exact.
19. Historical source and payload identifiers remain exact.
20. Repository and protected-reference state remain unchanged.
21. `__init__.py`, `models.py`, and `digests.py` remain byte-identical through the correction.

---

## 10. Completion Conditions

The correction would be complete only when:

1. A separate owner decision authorizes the exact two-file implementation correction.
2. Only `materialization.py` and `test_context_materialization.py` change from the current in-progress state.
3. The other three B2a implementation files remain byte-identical.
4. All focused portable B2a tests pass.
5. The separately classified guarded historical integration passes.
6. The safe broad regression passes with explicit protected-reference exclusions.
7. Exact source, payload, omission, ownership, freshness, ordering, and trace contracts remain intact.
8. No architecture, schema, policy, dependency, CI, lifecycle, protected-reference, EO-2026-022, or AI-environment change occurs.
9. Atlas Validate is Valid.
10. Atlas Missing reports no missing definitions.
11. Atlas Sync is Synchronized.
12. `git diff --check` passes.
13. The exact authorized working-tree scope remains and the index is empty.
14. An independent acceptance review confirms that B1b2 was not reinterpreted.
15. The owner separately accepts B2a completion before recording, staging, commit, or push.

---

## 11. Stop Conditions

Stop and return for separately authorized review if the correction requires:

- changing Checkpoint A, A.1, B1a, B1b1, or B1b2;
- changing the selection policy;
- changing the context-package schema;
- changing canonical architecture;
- adding a second owner field;
- deciding the final B2b package projection;
- weakening or removing ownership validation;
- reading an additional source for freshness;
- invoking Atlas from materialization;
- using wall-clock time or external observations;
- accessing protected content;
- changing protected-reference behavior;
- changing any implementation path outside the exact two-file correction scope;
- adding a dependency;
- changing CI;
- changing Engineering Opportunity lifecycle state;
- changing EO-2026-022;
- changing AI-environment configuration.

No such requirement may be silently absorbed.

---

## 12. Decision

| Question | Result |
| --- | --- |
| Source path and owner are universally equal | No |
| EO selected source path is the reviewed EO YAML | Yes |
| EO structured identity is `engineering-opportunity:EO-2026-013` | Yes |
| EO field-contract owner is the EO Object Architecture | Yes |
| Ordinary canonical document owner equals selected path | Yes |
| Current Mission freshness remains `unknown` | Yes |
| Accepted B1b2 defect found | No |
| Selection-policy defect found | No |
| B2a schema defect found | No |
| B2a architecture change required | No |
| Original B2a review ownership clause requires correction | Yes |
| Current materialization ownership check requires correction | Yes |
| Portable EO fixture requires correction | Yes |
| Existing five-path implementation may otherwise be retained | Yes |
| Future implementation correction scope is exactly two files | Yes |
| Final structured-owner package projection decided in B2a | No |
| B2a complete | No |
| B2b authorized | No |
| B2c authorized | No |
| Staging, commit, or push authorized | No |

B2a remains in progress at a bounded contract-correction gate.

The next milestone is a separate owner decision on the exact two-file correction.
