# EO-2026-013 Checkpoint B1a Authorization Review — July 16, 2026

- Authority class: Human-Reviewed Implementation-Planning Decision
- Canonical: No
- Generated: No
- Status: B1a Complete; Revised B1b1 Authorized; B1b2 and B2 Withheld
- Date: July 16, 2026
- Repository baseline: `f0ae21a34d525e6f4ce4c7b50790779e664138c4`
- Decision authority: Owner

---

## 1. Purpose and Authority

This non-canonical dated review records the separate owner decision required after EO-2026-013 Checkpoint A.1 completion.

The owner accepted the revised B1 sequence and authorized only Checkpoint B1a — Immutable Snapshot Boundary.

Checkpoint B1b and Checkpoint B2 remain unauthorized.

This review does not change EO-2026-013 or any other Engineering Opportunity lifecycle state. It does not authorize YAML or Markdown parsing, source selection, relationship verification, payload materialization, budget execution, package compilation, package integrity, explanations, Atlas commands, task-contract implementation, agent execution, autonomy, provider routing, AI-environment work, or protected-branch content access.

---

## 2. Recorded Owner Decision

The owner recorded:

> Accept the revised EO-2026-013 B1 plan. Authorize Checkpoint B1a — Immutable Snapshot Boundary only. Do not authorize Checkpoint B1b or Checkpoint B2. Preserve protected-branch content as out of scope; authorize only exact protected-ref name and object-identity comparison in B1a, with no protected object or content access.

Recorded July 16, 2026.

---

## 2A. Checkpoint B1a Completion Acceptance

The owner recorded:

> Accept EO-2026-013 Checkpoint B1a as complete. Authorize recording, committing, and pushing the Checkpoint B1a completion. Do not authorize Checkpoint B1b or Checkpoint B2. Preserve protected-branch content as out of scope; preserve only exact protected-ref name and object-identity comparison, with no protected object or content access.

Recorded July 16, 2026.

The accepted implementation:

- created exactly `tools/atlas/platform/context_compilation/snapshot.py` and `tests/test_context_snapshot.py`;
- modified exactly the task-context index, context-compilation exports, models, and digest helpers;
- preserved the standard-library-only dependency boundary;
- implemented the accepted public snapshot models, helpers, functions, constants, and error hierarchy;
- verified explicit clean local repository targets, bounded repository identity, exact full-SHA commits, SHA-1 object format, exact root trees, and deterministic snapshot fingerprints;
- read exact regular-file blob bytes from immutable Git trees rather than mutable worktrees;
- rejected unsafe paths, symlinks, gitlinks, trees, unsupported modes, replacement refs, grafts, object alternates, lazy fetch, and unsafe ambient Git state;
- applied the fixed command-level configuration prefix disabling fsmonitor and untracked cache and redirecting hooks to the platform null device;
- rejected unsafe repository-local includes, fsmonitor, hooks, worktree redirection, filters, diff, textconv, submodule, and related configuration before clean-state inspection;
- limited protected-reference handling to exact ref-name and direct object-identity comparison;
- reproduced historical snapshot fingerprint `14053ce1b4ce71c90c18316bed3928a85a67be6d48fd1bc330ffd8a00464fed8`;
- passed 144 tests;
- left Atlas Valid, complete, and Synchronized; and
- performed no B1b, B2, dependency, canonical architecture change, lifecycle mutation, protected-content access, staging, commit, or push before owner acceptance.

Checkpoint B1b and Checkpoint B2 remain unauthorized.

The protected branch content remains out of scope. Only exact protected-ref name and direct object-identity comparison is preserved.

---

## 3. Verified Starting State

The decision begins from:

- Branch: `main`.
- HEAD, `origin/main`, and `origin/HEAD`: `f0ae21a34d525e6f4ce4c7b50790779e664138c4`.
- Commit subject: `Complete EO-2026-013 Checkpoint A.1`.
- Working tree: clean.
- Checkpoint A: complete and owner-accepted.
- Checkpoint A.1: complete and owner-accepted.
- Selection-policy instance: `1.0.1`.
- Budget-policy instance: `1.0.0`.
- Tests: 90 passing at the accepted checkpoint.
- Atlas Validate: Valid.
- Atlas Missing: no missing definitions.
- Atlas Sync: Synchronized.
- EO-2026-013 and all 21 Engineering Opportunities: `reviewed`.
- Protected branch `wip/distinctness-foundation-calibration`: unchanged at `fcbc5957b89fe65a4313a3c23eb814e02a014698`, excluded, and content-out-of-scope.

---

## 4. Accepted Revised Sequence

The accepted executable sequence is now:

1. **Checkpoint B1a — Immutable Snapshot Boundary**
2. **Checkpoint B1b — Deterministic Selectors and Selection Plan**
3. **Checkpoint B2 — Compilation, Integrity Validation, Explanation, and Golden Replay**

Only Checkpoint B1a is authorized by this decision.

Checkpoint B1b requires a separate owner review after B1a is complete and accepted.

Checkpoint B2 remains downstream and requires a separate owner review after B1b is complete and accepted.

---

## 5. Why B1 Was Split

The previously planned B1 combined two different engineering risk domains:

1. establishing a trusted immutable Git and repository boundary;
2. parsing repository content and producing deterministic selection decisions.

A defect in repository identity, Git environment isolation, commit or tree resolution, object lookup, or protected-reference handling would make every later selector operate on untrusted bytes.

The immutable snapshot boundary must therefore be independently implemented, verified, and owner-accepted before selector or selection-reasoning work begins.

---

## 6. Checkpoint B1a Purpose

Checkpoint B1a establishes a deterministic, content-blind trust boundary for one explicit local repository target and one immutable historical commit.

B1a may:

- validate an explicit target repository path;
- validate clean state before and after snapshot operations;
- verify repository identity from a bounded set of accepted origin URL forms;
- accept only one exact full lowercase SHA-1 commit identifier;
- verify object format, commit, and root tree;
- compute a repository-owned snapshot fingerprint;
- normalize and validate exact repository paths;
- read exact regular-file blob bytes from the immutable tree;
- reject symlinks, gitlinks, trees, unsupported modes, ambiguous paths, and unsupported path syntax;
- compare the exact declared protected-ref name and exact object identity without reading protected object content.

B1a does not select task context and does not interpret repository content.

---

## 7. Exact Implementation Scope

### Create

1. `tools/atlas/platform/context_compilation/snapshot.py`
2. `tests/test_context_snapshot.py`

### Modify

3. `docs/task-context/index.md`
4. `tools/atlas/platform/context_compilation/__init__.py`
5. `tools/atlas/platform/context_compilation/models.py`
6. `tools/atlas/platform/context_compilation/digests.py`

No other path may change.

No dependency file may be created or modified.

No canonical architecture file may change.

---

## 8. Initial Repository Identity Contract

The request identity remains:

```text
github.com/aidenm727/t430-homelab
```

For the initial GitHub-hosted slice, B1a may normalize only these `origin` fetch URL forms:

- `git@github.com:aidenm727/t430-homelab.git`
- `ssh://git@github.com/aidenm727/t430-homelab.git`
- `https://github.com/aidenm727/t430-homelab.git`
- `https://github.com/aidenm727/t430-homelab`

No network call is authorized.

Absent origin, multiple conflicting fetch identities, a different host or path, unsupported URL syntax, or repository identity disagreement must fail verification.

A broader repository identity mechanism requires separate review.

---

## 9. Initial Requested-Revision Contract

B1a accepts only:

```text
^[0-9a-f]{40}$
```

The supplied value must resolve exactly to a commit object with the same object ID.

B1a rejects:

- branch names;
- tag names;
- abbreviated object IDs;
- symbolic refs;
- revision operators;
- reflog expressions;
- leading option syntax;
- uppercase or mixed-case object IDs;
- non-commit objects.

For the first historical replay:

- requested commit: `79eef80af3d5969ece7eb9fe7f802be35575f450`;
- expected root tree: `3d2853517e64209cffde91766a62e9f70ceb2e47`.

The resolved commit and root tree must match those exact immutable identities.

---

## 10. Git Execution Boundary

Every Git subprocess must:

- use an argument list without a shell;
- use an explicit target repository path;
- use `git --no-replace-objects`;
- set `GIT_NO_REPLACE_OBJECTS=1`;
- set `GIT_NO_LAZY_FETCH=1`;
- set `GIT_OPTIONAL_LOCKS=0`;
- set `GIT_LITERAL_PATHSPECS=1`;
- set `LC_ALL=C` and `LANG=C`;
- remove inherited repository, worktree, index, object-store, and injected-configuration override variables;
- avoid filters, text conversion, external diffs, hooks, checkout, worktree-content reads, and network access;
- capture stdout and stderr as bytes;
- expose stable bounded error information without protected content.

B1a rejects at minimum:

- `GIT_DIR`;
- `GIT_WORK_TREE`;
- `GIT_COMMON_DIR`;
- `GIT_INDEX_FILE`;
- `GIT_OBJECT_DIRECTORY`;
- `GIT_ALTERNATE_OBJECT_DIRECTORIES`;
- injected Git configuration variables;
- repository `objects/info/alternates`;
- repository `objects/info/http-alternates`;
- `.git/info/grafts`;
- any `refs/replace/*`;
- missing local objects that would require lazy fetching.

---

## 11. Clean-State Contract

The target must be a non-bare working-tree repository.

Before and after snapshot work, B1a must run the equivalent of:

```text
git status --porcelain=v1 -z --untracked-files=all --ignore-submodules=none
```

Any output fails the clean-state check.

Ignored files remain outside the initial tracked `clean_committed` snapshot because B1a reads only committed Git objects and executes no repository content.

B1a must never write to the target repository.

---

## 12. Object Format and Snapshot Fingerprint

The first executable slice supports only SHA-1 repositories.

Snapshot mode is exactly:

```text
clean_committed
```

The snapshot fingerprint is SHA-256 over repository-owned canonical JSON with the exact surface:

```json
{
  "repository_identity": "github.com/aidenm727/t430-homelab",
  "object_format": "sha1",
  "commit": "79eef80af3d5969ece7eb9fe7f802be35575f450",
  "tree": "3d2853517e64209cffde91766a62e9f70ceb2e47",
  "snapshot_mode": "clean_committed"
}
```

The named `snapshot_fingerprint` helper belongs in `tools/atlas/platform/context_compilation/digests.py`.

The digest formula must not be hidden inside Git subprocess code.

---

## 13. Path and Blob Contract

Repository paths are UTF-8 scalar strings using `/`.

B1a rejects:

- absolute paths;
- empty paths;
- empty path components;
- `.` or `..` components;
- backslashes;
- NUL;
- leading or trailing `/`;
- normalization or case rewriting;
- non-UTF-8 path bytes.

Tree lookup must use exact NUL-safe object plumbing.

Only these regular blob modes are accepted:

- `100644`
- `100755`

B1a rejects:

- symbolic links (`120000`);
- gitlinks or submodules (`160000`);
- tree objects where a blob is required;
- unsupported modes;
- missing or ambiguous entries.

Blob content is returned from the exact blob object identity without filters or text conversion.

B1a does not decode, parse, select, transform, compute source-payload digests, or apply a budget to the returned bytes.

---

## 14. Protected-Reference Boundary

For each declared protected reference, B1a may compare only:

- exact ref name;
- expected object identity;
- actual object identity;
- match or blocking-mismatch state.

B1a requires:

- `selection: forbidden`;
- `authoritatively_targeted: false`.

Missing or mismatched identity is a blocking snapshot-verification failure.

B1a must not:

- peel or inspect the protected object;
- read its commit, tree, or blobs;
- enumerate paths;
- traverse history;
- checkout or switch;
- select content;
- merge, update, delete, or mutate the ref;
- expose protected-object content in errors or logs.

The protected branch's content remains completely out of scope.

---

## 15. Typed Model Boundary

B1a may add deeply immutable typed values sufficient for:

- normalized repository identity evidence;
- requested revision;
- resolved commit;
- root tree;
- object format;
- snapshot mode;
- snapshot fingerprint;
- protected-reference identity result;
- immutable blob identity, mode, path, and raw bytes.

New nested values must preserve the existing deep-immutability guarantees.

B1a must not add selector, selected-source, omission, unknown, freshness, conflict, payload, budget, or package models.

---

## 16. Test Strategy

Tests must operate against an isolated temporary full local clone made without hardlink or alternate-object behavior.

The test harness may:

- clone committed repository objects into a temporary target;
- set the temporary clone's origin to an accepted GitHub identity form;
- create the declared protected ref in the temporary target;
- keep the target clean;
- execute implementation code from the development worktree against the explicit clean target.

Production snapshot code must never write to the target.

Tests must cover at minimum:

- exact historical commit and tree;
- repeatable snapshot fingerprint;
- all supported origin URL forms;
- absent origin and repository identity mismatch;
- revision syntax rejection;
- non-commit object rejection;
- dirty tracked, staged, and untracked states;
- explicit submodule-dirtiness behavior;
- SHA-256 repository rejection when locally supported by Git;
- replacement refs;
- grafts;
- environment and file-based alternates;
- lazy-fetch prevention;
- path-normalization attacks;
- missing paths;
- regular executable blobs;
- symlinks;
- gitlinks;
- protected-ref match, missing, and mismatch;
- evidence that protected object content was never requested;
- unchanged target before and after;
- byte-identical repeated typed output;
- no network and no target write.

Unsupported test prerequisites must be reported explicitly rather than silently skipped when they are required to establish the accepted boundary.

---

## 17. Required Verification

Checkpoint B1a must prove:

- exact two-created and four-modified scope;
- no B1b or B2 path exists;
- no dependency is added;
- no canonical architecture changes;
- no Engineering Opportunity lifecycle mutation;
- full-SHA requested-revision enforcement;
- exact historical commit and tree verification;
- SHA-1 object-format enforcement;
- repeatable snapshot fingerprint;
- repository identity normalization and mismatch rejection;
- clean pre-state and post-state;
- replacement, graft, alternate-object-store, and lazy-fetch rejection;
- exact path validation and regular-blob reads;
- symlink and gitlink rejection;
- exact protected-ref identity comparison only;
- no protected object or content access;
- no target writes or network access;
- all tests pass;
- Atlas remains Valid, complete, and Synchronized;
- nothing is staged, committed, or pushed before owner acceptance of the implementation.

Any implementation-discovered contract ambiguity must stop the checkpoint and return for bounded owner review.

---

## 18. Checkpoint B1a Explicit Exclusions

Checkpoint B1a does not authorize:

- Checkpoint B1b;
- Checkpoint B2;
- YAML parsing;
- Markdown heading parsing;
- relationship verification;
- source selection;
- candidate discovery;
- directory, object, edge, or graph scans;
- selector output;
- selected-source records;
- omissions;
- unknowns;
- freshness;
- conflicts;
- source-content or payload digests;
- payload materialization;
- budget application;
- package construction;
- package integrity;
- explanations;
- package fixtures;
- Atlas commands;
- generic structured-resource discovery;
- task-contract implementation;
- execution;
- autonomy;
- provider routing;
- AI-environment integration;
- lifecycle mutation;
- protected object or content access;
- third-party dependencies.

---

## 19. Planned Checkpoint B1b — Unauthorized

Checkpoint B1b remains unauthorized and requires a separate owner decision after B1a completion.

Its future planned responsibilities are:

- strict UTF-8 selector input;
- bounded top-level YAML parsing;
- exact `yaml_fields` extraction;
- exact ATX Markdown heading extraction;
- deterministic line-ending behavior;
- historical relationship membership verification;
- exact five-rule candidate universe;
- no whole-repository or whole-edge scan;
- sensitivity and budget-tier enforcement;
- stable selected, omitted, and unknown records;
- deterministic source ordering;
- immutable selection-plan output.

No B1b file or behavior is authorized now.

---

## 20. Checkpoint B2 — Unauthorized

Checkpoint B2 remains unauthorized.

It begins only after B1a and B1b are separately complete and accepted.

---

## Superseding B1b1 and B1b2 Decision

The former single Checkpoint B1b plan in this review is superseded for future authorization purposes by `docs/reviews/eo-2026-013-b1b1-authorization-review-2026-07-16.md`.

On July 16, 2026, the owner accepted this revised sequence:

1. Checkpoint B1b1 — Deterministic Selector Primitives.
2. Checkpoint B1b2 — Bounded Selection Plan.
3. Checkpoint B2 — Compilation, Integrity Validation, Explanation, and Golden Replay.

Only Checkpoint B1b1 is authorized.

B1b1 implements pure selector transformations over immutable bytes. B1b2 remains separately withheld for candidate derivation, relationship verification, source selection, omissions, unknowns, sensitivity and budget-tier enforcement, and selection-plan production. B2 remains separately withheld for package compilation and golden replay.

Checkpoint B1a and the protected-reference boundary remain unchanged.

Protected branch content remains out of scope.

STOP — Use the B1b1 authorization review as the active authorization source after Checkpoint B1a.

---

## 21. Decision Traceability

- Architecture checkpoint: `2de09693ed1c922500477c5ba1c6903513ab4dd3`.
- Checkpoint A completion: `6e0fb536eac8113a2a07547661d5a9b89c0a65b6`.
- Checkpoint A.1 authorization: `1f2595b8a3489979b275dfad0884b4e0fe09c585`.
- Checkpoint A.1 completion: `f0ae21a34d525e6f4ce4c7b50790779e664138c4`.
- Checkpoint B1a authorization: `b7046e6fdd7302e1b5aaada3db0970e35c0f0e6c`.
- Checkpoint B1a completion accepted: July 16, 2026.
- Checkpoint B1a exact implementation scope: two created and four modified files.
- Historical commit: `79eef80af3d5969ece7eb9fe7f802be35575f450`.
- Historical root tree: `3d2853517e64209cffde91766a62e9f70ceb2e47`.
- Historical snapshot fingerprint: `14053ce1b4ce71c90c18316bed3928a85a67be6d48fd1bc330ffd8a00464fed8`.
- Final technical verification: 144 tests passed; Atlas Valid, complete, and Synchronized; independent public-interface, configuration-isolation, command-boundary, snapshot, blob, and protected-reference probes passed.
- Checkpoint B1b authorized: No.
- Checkpoint B2 authorized: No.
- Protected branch content in scope: No.
- Protected-ref exact name and direct object-identity comparison preserved: Yes.
- Protected object or content access authorized: No.
- Third-party dependency authorized: No.
- Canonical architecture change authorized: No.
- Engineering Opportunity lifecycle state: `reviewed`.
- Next gate: separate owner authorization, revision, deferral, or rejection of Checkpoint B1b.

STOP — Preserve Checkpoint B1a. Do not begin B1b or B2 without a separate owner decision.
