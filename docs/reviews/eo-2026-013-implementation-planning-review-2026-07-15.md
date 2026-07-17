# EO-2026-013 Implementation Planning Review — July 15, 2026

- Authority class: Human-Reviewed Mission Advancement and Implementation-Planning Decision
- Canonical: No
- Generated: No
- Status: Checkpoint A Completion Accepted; Checkpoint B Withheld
- Date: July 15, 2026
- Owner decision recorded: July 15, 2026
- Plan acceptance and Checkpoint A authorization recorded: July 16, 2026
- Checkpoint A completion acceptance recorded: July 16, 2026
- Repository baseline: commit `2de09693ed1c922500477c5ba1c6903513ab4dd3`
- Architecture checkpoint: commit `2de09693ed1c922500477c5ba1c6903513ab4dd3`
- Decision authority: Owner

---

## 1. Purpose and Authority

This non-canonical dated review records the decision history for EO-2026-013 architecture completion, implementation planning, Checkpoint A authorization, and Checkpoint A completion acceptance.

The owner accepted the reconciled implementation plan and authorized Checkpoint A on July 16, 2026. After implementation, bounded correction, source audit, and independent final verification, the owner accepted Checkpoint A as complete and authorized recording, committing, and pushing it.

This review does not authorize Checkpoint B, change an Engineering Opportunity lifecycle state, authorize downstream AI-environment work, or broaden task authority.

## 2. Verified Repository State

Repository evidence at the start of this application:

- Branch: `main`.
- HEAD and `origin/main`: `2de09693ed1c922500477c5ba1c6903513ab4dd3`.
- Commit subject: `Define task-scoped context compilation architecture`.
- Starting worktree and index: clean.
- Atlas Validate: Valid.
- Atlas Missing: no missing definitions.
- Atlas Sync: Synchronized.
- Engineering Mode: Ready.
- Engineering Opportunities: 21 total; all 21 are `reviewed`.
- EO-2026-013: `reviewed`.
- Protected branch `wip/distinctness-foundation-calibration`: unchanged at `fcbc5957b89fe65a4313a3c23eb814e02a014698` and not accessed as a source for this change.

The generic Atlas Engineering Review result was `Unknown` with `Low` confidence because no milestone-specific reasoning rule matched. It reported no blocker. This is expected repository behavior, not contrary completion evidence.

## 3. Architecture Milestone Completion Assessment

Reviewer assessment: the milestone to define the Task-Scoped Agent Context Compilation architecture and one bounded example package is complete with high confidence.

Repository evidence supporting that assessment includes:

- the canonical architecture at `docs/architecture/task-scoped-agent-context-compilation.md`;
- explicit responsibility boundaries for task authority, repository knowledge, selection reasoning, compilation, validation, and consumers;
- deterministic selection, ordering, serialization, digest, budget, provenance, conflict, unknown, omission, and consumer-contract rules;
- an informative, manually assembled, non-consumable example package selecting five accepted sources from an immutable Git snapshot;
- explicit clean-committed-snapshot, provider-independence, lifecycle, autonomy, execution, Atlas-interface, and AI-environment boundaries;
- review corrections incorporated into the guarded architecture commit; and
- the guarded committed verification in which all 43 tests passed and Atlas reported Valid, no missing definitions, and Synchronized.

Four test errors observed during the earlier strict read-only Codex stage were caused by temporary-directory sandbox restrictions, not failed assertions. The same tests passed in the writable guarded stage. That environment limitation is not an architecture defect or milestone blocker.

The generic `Unknown / Low` Atlas result is non-blocking because Atlas has no specialized rule for this milestone. No milestone-specific rule should be added merely to alter the display status.

## 4. Recorded Owner Decision

Owner decisions recorded:

> Accept EO-2026-013 mission advancement to Implementation Planning

Recorded July 15, 2026. This accepted architecture completion and advanced the mission into planning without authorizing implementation.

> Accept the reconciled EO-2026-013 implementation plan and authorize Checkpoint A only.

Recorded July 16, 2026. This accepted the reconciled plan and authorized Checkpoint A — Deterministic Foundations within the exact create, modify, and exclude scopes recorded below.

> Accept EO-2026-013 Checkpoint A as complete. Authorize recording, committing, and pushing the Checkpoint A completion. Do not authorize Checkpoint B.

Recorded July 16, 2026. This accepted the independently verified Checkpoint A implementation and authorized its canonical repository commit and push.

None of these decisions authorizes Checkpoint B, a YAML dependency, an Atlas command, agent behavior, AI-environment changes, Engineering Opportunity lifecycle mutation, or protected-branch work.

## 5. Mission Advancement

The active phase advances to:

`Task-Scoped Agent Context Compilation Checkpoint A Complete`

The next milestone is:

`Obtain a separate owner decision on Checkpoint B — Executable Compilation Path.`

EO-2026-013 remains `reviewed`, as do all 21 opportunities. Checkpoint A is complete and accepted. Checkpoint B remains withheld. The protected branch remains unchanged and outside the mission. The broader AI Engineering Environment Review and Structured Research Orchestration direction remain downstream and separately authorized.

## 6. Proposed Current Focus

Planned future work for this phase is to:

- record the first executable slice's responsibility boundaries;
- define exact repository locations for schemas, policies, fixtures, implementation, and tests;
- define minimal Atlas visibility for the structured artifact family through a canonical Markdown owner/index;
- define interoperable RFC 8785 safe-integer behavior;
- make compiler identity and version explicit compilation inputs;
- pin the executable request to its exact historical revision and define the clean committed Git snapshot protocol;
- define exact selector, serialization, digest, budget, validation, and golden-fixture behavior;
- separate independently verified foundation expected values from the compiler-produced executable golden package;
- preserve the manual architecture example as informative evidence;
- divide implementation into independently reviewable checkpoints with exact future create, modify, and exclude scopes;
- keep Atlas interfaces, execution, autonomy, agent consumption, and AI-environment changes outside the milestone; and
- return for owner acceptance before implementation.

## 7. Included and Excluded Boundaries

The planning record includes responsibility decomposition, exact planned paths, minimal Atlas visibility for structured resources, serialization and reproducibility rules, validation and test strategy, two exact future implementation checkpoints, practical value, a first consumer, risks, open decisions, and an explicit owner-acceptance gate.

It excludes implementation files, executable schemas and policies, fixtures, tests, Atlas commands, general EO-2026-014 task-contract implementation, autonomy or approval automation, execution records or evidence bundles, agent execution or provider routing, ChatGPT Project or Codex configuration, AI Engineering Environment Review execution, embeddings, vector databases, semantic retrieval, LLM selection, dirty-worktree support, external live observations, broad Personal AI implementation, Engineering Opportunity lifecycle mutation, protected-branch access or change, and milestone-specific Atlas reasoning.

## 8. Implementation-Planning Completion Criteria

The implementation-planning milestone is complete only when:

1. A reviewed plan records every responsibility and exact artifact path.
2. Selection-policy and budget-policy schemas are defined in the plan.
3. Package and compilation-request schemas needed by the slice are defined in the plan.
4. Normative integers are limited to `[-9007199254740991, 9007199254740991]`; byte counts and limits are additionally non-negative.
5. Compiler identity and version are mandatory explicit inputs with no ambient default.
6. Package identity and package integrity remain distinct.
7. Foundation expected-value evidence, the executable golden package, and the manual example are distinguished accurately.
8. The executable request is pinned to the exact historical commit, and clean-snapshot verification and immutable Git reads are specified.
9. Required first-slice tests and deferred tests are separated.
10. Atlas command work is explicitly deferred.
11. Implementation and downstream EO boundaries remain explicit.
12. The structured artifact family has a planned canonical Markdown owner/index registered through existing Atlas document discovery without generic structured-resource discovery.
13. Future implementation is divided into at least two independently reviewable checkpoints with exact create, modify, and exclude scopes: deterministic foundations, then the executable compilation path.
14. Heading selectors carry a one-based occurrence index and define deterministic missing-occurrence behavior.
15. The omission candidate universe is bounded to explicit anchors, exact task-profile candidates, and allowlisted one-hop relationship candidates rather than the whole repository.
16. Protected-reference aliasing, stale expected identities, transitive discovery, and mismatch behavior are resolved in the plan.
17. RFC 8785 and strict YAML implementation choices pass explicit build-versus-adopt and dependency gates rather than relying on ambient packages.
18. Completed external research and independent challenge evidence are reconciled without converting either into repository authority.
19. The owner accepts the recorded plan before implementation begins.

All 19 implementation-planning completion criteria are now satisfied. Criterion 19 was satisfied by the owner's July 16, 2026 acceptance of the reconciled plan and authorization of Checkpoint A only.

## 9. Responsibility Decomposition

Planned future responsibilities are separated as follows:

- Repository-owned JSON Schemas define the accepted selection-policy, budget-policy, compilation-request, and context-package shapes without embedding runtime behavior.
- Repository-owned policy instances define the exact five-source selection rules, ordering, exclusions, sensitivity ceiling, UTF-8 byte budget, allocation order, and non-self-referential measurement surface.
- `docs/task-context/index.md` owns the human-readable identity, inventory, stewardship, purpose, version, consumers, update mechanism, architecture relationship, and exact-path-and-digest loading contract for the structured artifact family. It makes the family visible through existing Markdown discovery without treating each JSON resource as a `DocumentDefinition`.
- Strict input loading rejects duplicate JSON keys, unsupported JSON values, schema violations, unknown policy versions, and ambiguous or unsupported YAML values before selection.
- `models.py` owns internal typed request, policy, selection-plan, snapshot, source, omission, package, validation, and explanation values; it does not invent task authority.
- `canonical_json.py` owns the repository-local canonical-JSON interface, RFC 8785 conformance, safe-integer enforcement, and known-vector verification. Checkpoint A must compare a maintained dependency, an RFC-referenced implementation, and a restricted local implementation before choosing the implementation behind that interface.
- `inputs.py` owns strict request and policy loading, schema application, version compatibility, and the requirement for explicit compiler identity and version.
- `snapshot.py` owns clean-checkout verification, one-time revision resolution, immutable commit/tree/blob identities, raw Git-object reads, and post-compilation non-mutation verification.
- `context_selection.py` owns deterministic typed selected-source and omitted-candidate reasoning from explicit request, repository knowledge, and resolved selection policy. It does not materialize payloads or make human decisions.
- `selectors.py` owns exact structured YAML-field and heading-bounded byte selection from immutable blobs. It must not reuse the current working-tree-oriented `parse_simple_yaml` loader as its strict parser. Heading selectors carry exact ATX heading text plus a one-based occurrence index. YAML selectors verify policy-allowlisted fields against the canonical source-object contract.
- `digests.py` owns the architecture-defined SHA-256 digest surfaces and Git-object identity separation.
- `compiler.py` orchestrates already validated inputs, selection, immutable materialization, budgeting, package assembly, and validation without becoming an Atlas interface.
- `validation.py` owns structural and cross-field invariant validation, consumability, and identical-input verification hooks.
- `explanation.py` presents typed selected and omitted reasoning without reconstructing or changing selection.
- `__init__.py` exposes the smallest reusable Python capability beneath Atlas; it exposes no command and supplies no ambient compiler defaults.
- Tests and fixtures own executable contract evidence, boundary coverage, byte-identical golden reproduction, and proof that repository state is not mutated.

Task authority remains external to compilation. Repository sources retain canonical ownership. A package copies authorized declarations but creates no permission, approval, execution authority, or lifecycle authority.

The canonical Engineering Opportunity Object architecture owns the Engineering Opportunity field contract. `tools/atlas/platform/repository_objects/models.py` and `loader.py` operationalize part of that contract for current Atlas reasoning, but the current loader reads working-tree files and does not provide the strict immutable-byte parsing or rejection semantics required by context compilation. The first-slice selection policy therefore allowlists the exact Engineering Opportunity fields `id`, `title`, `status`, and `summary` for the historical example and records the canonical object type as their field-contract owner. No second global YAML-field registry is created.

Actual relationship edges remain owned by Repository Objects and existing Repository Knowledge/Reasoning. The selection policy may allowlist relationship types and directions for this task profile, but it must not copy or become a second owner of relationship data.

The four planned schemas have these first-slice boundaries:

- The selection-policy schema requires a schema version, policy identifier and version, task profile, bounded relationship traversal, allowlisted relationship types and directions, exact source ordering, typed rules with identifiers, priorities and deterministic selectors, explicit source-specific field allowlists, explicit exclusion rules, sensitivity ceiling, and a self-excluding policy digest. It rejects unknown fields and any selector or traversal form not supported by this slice. Its omission candidate universe is limited to explicit request anchors, exact task-profile candidates, and candidates reached through an allowlisted one-hop relationship; it does not scan the full repository merely to emit omissions.
- The budget-policy schema requires a schema version, policy identifier and version, `utf8_bytes` as the normative unit, a non-negative safe-integer byte limit, exact allocation order, the architecture-defined control-envelope removal surface, mandatory-tier overflow behavior, arbitrary-character truncation prohibition, and a self-excluding policy digest. It rejects token counts as normative budget input.
- The compilation-request schema requires a schema version, explicit repository identity and requested revision, complete attributed task declarations, complete attributed constraints, exact selection-policy and budget-policy references with identifiers, versions and expected digests, protected-reference constraints, an explicit RFC 3339 `as_of` string, and explicit compiler `{identity, version}`. It permits no ambient compiler value, current time, branch inference, provider memory, or hidden request field.
- The context-package schema requires the architecture-defined top-level package identity and integrity, compilation inputs and resolved policies, immutable repository snapshot, copied task and constraint declarations, ordered sources and payloads, conflicts, unknowns, omissions, budget measurement, validation state, and consumer contract. Fixed objects reject unknown fields; every digest and identifier surface is reconstructible from carried typed values; consumability follows structural and invariant validation rather than schema validity alone.

All four schemas apply the shared bounded data model and safe-integer rules. Schema validation is necessary but does not replace cross-field invariant validation.

## 10. Repository Convention Findings

Repository evidence and reviewer interpretation support these planned conventions:

- Canonical architecture remains under `docs/architecture/`; the accepted architecture is not replaced by executable artifacts.
- Versioned structured task-context contracts and policy values belong under a dedicated repository-owned `docs/task-context/` hierarchy.
- A canonical `docs/task-context/index.md` should own and enumerate that hierarchy. Registering only this Markdown document in `docs/docs-map.md` and `tools/atlas/platform/document_definitions.py` makes the resource family visible and explainable through existing Atlas discovery while preserving later generic structured-resource discovery as a separate capability.
- Reusable Python capability belongs beneath `tools/atlas/platform/`, with selection reasoning separate from compilation responsibilities.
- Repository tests use `tests/test_*.py`; executable examples belong under `tests/fixtures/` rather than inside canonical architecture.
- Atlas commands are thin interface layers over platform capability and are not required for the first slice.
- Generated context is tool-managed. Planned package fixtures are generated/non-canonical test evidence, not canonical sources.

The first implementation should therefore be a reusable Python capability beneath Atlas with no Atlas command.

## 11. Planned Artifact and Module Locations

Planned structured artifacts:

- `docs/task-context/index.md`
- `docs/task-context/schemas/selection-policy-v1.schema.json`
- `docs/task-context/schemas/budget-policy-v1.schema.json`
- `docs/task-context/schemas/compilation-request-v1.schema.json`
- `docs/task-context/schemas/context-package-v1.schema.json`
- `docs/task-context/policies/selection/example-read-only-architecture-assessment-v1.json`
- `docs/task-context/policies/budget/example-utf8-65536-v1.json`

Planned fixtures:

- `tests/fixtures/task_context/requests/example-eo-2026-013-read-only-assessment-v1.json`
- `tests/fixtures/task_context/expected/example-eo-2026-013-foundation-values-v1.json`
- `tests/fixtures/task_context/packages/example-eo-2026-013-read-only-assessment-v1.json`

Planned implementation:

- `tools/atlas/platform/reasoning/context_selection.py`
- `tools/atlas/platform/context_compilation/__init__.py`
- `tools/atlas/platform/context_compilation/models.py`
- `tools/atlas/platform/context_compilation/canonical_json.py`
- `tools/atlas/platform/context_compilation/inputs.py`
- `tools/atlas/platform/context_compilation/snapshot.py`
- `tools/atlas/platform/context_compilation/selectors.py`
- `tools/atlas/platform/context_compilation/digests.py`
- `tools/atlas/platform/context_compilation/compiler.py`
- `tools/atlas/platform/context_compilation/validation.py`
- `tools/atlas/platform/context_compilation/explanation.py`

Planned tests:

- `tests/test_context_canonical_json.py`
- `tests/test_context_inputs.py`
- `tests/test_context_selection.py`
- `tests/test_context_snapshot.py`
- `tests/test_context_compilation.py`
- `tests/test_context_validation.py`

Planned registration modifications:

- `docs/docs-map.md`, only to register `docs/task-context/index.md`.
- `tools/atlas/platform/document_definitions.py`, only to register `docs/task-context/index.md`.

These are planned paths only. None is created, modified, or registered by this mission-advancement change. Checkpoints A and B below assign every planned path to an exact future Git scope.

## 12. Planned Checkpoint A — Deterministic Foundations

Checkpoint A is the currently authorized, independently reviewable implementation change. It establishes deterministic contracts, strict inputs, canonicalization, digest and identifier primitives, structural validation foundations, minimal Atlas visibility, and independently executable expected values. It does not pretend that a complete context package has been compiled.

Checkpoint A is authorized to create exactly:

- `docs/task-context/index.md`
- `docs/task-context/schemas/selection-policy-v1.schema.json`
- `docs/task-context/schemas/budget-policy-v1.schema.json`
- `docs/task-context/schemas/compilation-request-v1.schema.json`
- `docs/task-context/schemas/context-package-v1.schema.json`
- `docs/task-context/policies/selection/example-read-only-architecture-assessment-v1.json`
- `docs/task-context/policies/budget/example-utf8-65536-v1.json`
- `tests/fixtures/task_context/requests/example-eo-2026-013-read-only-assessment-v1.json`
- `tests/fixtures/task_context/expected/example-eo-2026-013-foundation-values-v1.json`
- `tools/atlas/platform/context_compilation/__init__.py`
- `tools/atlas/platform/context_compilation/models.py`
- `tools/atlas/platform/context_compilation/canonical_json.py`
- `tools/atlas/platform/context_compilation/inputs.py`
- `tools/atlas/platform/context_compilation/digests.py`
- `tools/atlas/platform/context_compilation/validation.py`
- `tests/test_context_canonical_json.py`
- `tests/test_context_inputs.py`
- `tests/test_context_validation.py`

Checkpoint A is authorized to modify exactly:

- `docs/docs-map.md`
- `tools/atlas/platform/document_definitions.py`

Those two modifications may only register `docs/task-context/index.md`. The index must identify the `docs/task-context/` artifact family; list every first-slice versioned schema and policy path; classify each as a canonical machine-readable schema or canonical versioned policy; record owner, purpose, version, consumers, update mechanism, and relationship to the canonical architecture; state that JSON resources are loaded by exact path and digest; explain that the index exposes the family through existing Markdown discovery without pretending each JSON file is a `DocumentDefinition`; and preserve generic structured-resource discovery as a later capability.

Checkpoint A creates the request fixture and the independently verified foundation-values fixture. The foundation-values fixture may carry exact expected policy digests, request-surface behavior, safe-integer boundaries, canonicalization vectors, identifier primitives, and other deterministic results that Checkpoint A can execute and independently verify. It is not a compiled package and is not a golden package fixture.

Before `canonical_json.py` is accepted in Checkpoint A, the checkpoint must record a bounded build-versus-adopt comparison covering correctness, RFC 8785 and UTF-16 ordering behavior, safe-integer handling, dependency burden, maintenance, auditability, and known-vector cross-testing. The result may choose a maintained dependency or a restricted local implementation, but the plan does not predetermine that outcome.

Checkpoint A explicitly excludes:

- the package golden fixture;
- Git snapshot resolution;
- source selection;
- payload materialization;
- full compilation;
- Atlas commands;
- Current Mission changes;
- Engineering Opportunity lifecycle changes; and
- AI-environment changes.

In particular, Checkpoint A must not create `tests/fixtures/task_context/packages/example-eo-2026-013-read-only-assessment-v1.json` or claim complete golden reproduction.

## 13. Planned Checkpoint B — Executable Compilation Path

Checkpoint B is a later, independently reviewable implementation change that remains unauthorized and depends on an accepted and verified Checkpoint A. It adds the immutable Git snapshot adapter, deterministic source selection and materialization, the real compiler, complete invariant validation, explanations, and independently verified golden reproduction.

Checkpoint B plans to create exactly:

- `tests/fixtures/task_context/packages/example-eo-2026-013-read-only-assessment-v1.json`
- `tools/atlas/platform/reasoning/context_selection.py`
- `tools/atlas/platform/context_compilation/snapshot.py`
- `tools/atlas/platform/context_compilation/selectors.py`
- `tools/atlas/platform/context_compilation/compiler.py`
- `tools/atlas/platform/context_compilation/explanation.py`
- `tests/test_context_selection.py`
- `tests/test_context_snapshot.py`
- `tests/test_context_compilation.py`

Checkpoint B plans to modify exactly:

- `tools/atlas/platform/context_compilation/__init__.py`
- `tools/atlas/platform/context_compilation/models.py`
- `tools/atlas/platform/context_compilation/digests.py`
- `tools/atlas/platform/context_compilation/validation.py`
- `tests/test_context_validation.py`

Only after the real compiler produces `tests/fixtures/task_context/packages/example-eo-2026-013-read-only-assessment-v1.json` and the executable validator independently verifies it may the artifact be called the golden package fixture. It is authoritative only for the exact executable request fixture and implemented compiler contract.

Checkpoint B begins with a strict-YAML dependency decision. The currently installed `yaml` module is ambient workstation state, not a repository-declared dependency, and cannot be treated as part of the reproducible compiler contract. The checkpoint must either introduce an explicitly reviewed repository dependency mechanism or implement and test a bounded parser that satisfies the required rejection semantics. A new dependency requires explicit owner acceptance within the Checkpoint B review.

The Engineering Opportunity selector verifies `id`, `title`, `status`, and `summary` against the canonical Engineering Opportunity Object contract and the exact source-specific policy allowlist. It parses the immutable Git blob independently of the existing working-tree loader.

Checkpoint B explicitly excludes:

- changes to accepted schemas or policies unless a separately reviewed defect requires returning to Checkpoint A;
- Atlas commands;
- generic repository discovery;
- Current Mission changes;
- canonical architecture changes;
- Engineering Opportunity lifecycle changes;
- agent execution;
- autonomy; and
- AI-environment changes.

Any need to alter a frozen Checkpoint A schema or policy stops Checkpoint B and returns through a bounded correction review rather than silently expanding its scope.

Checkpoint A is authorized by the owner's July 16, 2026 decision. Checkpoint B remains unauthorized and requires a later owner decision after Checkpoint A verification.

## 14. Serialization and Reproducibility Decisions

The proposed plan preserves these normative architecture decisions:

- Canonical JSON conforms to RFC 8785 for maps with string keys, ordered lists, strings, integers, booleans, and null. Unsupported types, including floating-point values, are rejected. `canonical_json.py` is the repository-owned interface and validation boundary; Checkpoint A decides whether its implementation is an audited dependency or a restricted local implementation after the required comparison.
- Every normative integer must be in `[-9007199254740991, 9007199254740991]`. Byte counts, budgets, and limits must also be non-negative. Enforcement occurs at strict input loading, model construction, canonical serialization, calculation, and final validation so an out-of-range value cannot enter a digest surface.
- Map keys use RFC 8785 UTF-16 code-unit ordering. Canonical output is UTF-8 without BOM and contains only valid Unicode scalar values. No Unicode normalization is performed.
- RFC 3339 time values are strings with an explicit numeric offset or `Z`. The supplied valid string is preserved exactly; no timezone conversion or reformatting occurs.
- List ordering is architecture-defined and normative independently of map-key serialization. Source order is fixed by priority tier, selection-rule identifier, normalized path or object identifier, and selector. Policy-defined list orders remain exact.
- JSON loading rejects duplicate object keys at every depth before schema validation.
- YAML-field selection uses a strict safe subset and rejects duplicate keys, aliases, anchors, merge keys, tags, implicit timestamps, and unsupported scalars. The source-specific selection policy allowlists fields against the canonical source-object contract; the first example permits only `id`, `title`, `status`, and `summary`. Selected fields are serialized as canonical JSON.
- A heading selector contains exact ATX heading text and a one-based occurrence index. Selection begins at that exact occurrence and ends before the next ATX heading of equal or greater level, or at end of file. If the occurrence does not exist, a mandatory source produces a blocking `selector_not_found` unknown and an optional source produces an explicit omission. Exact LF or CRLF payload bytes from immutable Git blobs are preserved; ambient newline conversion is forbidden.
- Compiler `{identity, version}` is a mandatory explicit compilation input. There is no environment, package, CLI, or hard-coded ambient default.
- Compiler identity and version are required request inputs and are carried as `compilation.compiler` in the package, but they do not alter the architecture's exact request-digest or package-identity surfaces. They are bound, together with validation and the consumer contract, by package integrity. Two conforming compilers may therefore produce the same package identity for the same request identity and snapshot while producing different package-integrity values if any carried compiler or output value differs.
- Package identity and package integrity remain distinct. Package identity is derived from request identity and snapshot fingerprint. Package integrity is the SHA-256 digest of the complete canonical package after removing only `package.digest`.
- Compiler identity, validation results, and the consumer contract are inside the package-integrity surface. The package integrity value is never copied into its own digest surface.
- Budget measurement remains non-self-referential: `control_envelope_bytes` measures canonical package bytes after removing `package.digest`, every `payloads[*].content`, and the entire `budget.measurement`; `included_payload_bytes` sums exact payload UTF-8 bytes; `consumed_bytes` is their sum.
- All architecture-defined content and package digests use SHA-256 lowercase hexadecimal. Git SHA-1 commit, tree, and blob identities remain explicit and distinct from SHA-256 content and package digests.
- Identical explicit inputs and the same immutable snapshot must produce byte-identical canonical JSON and identical digests, identifiers, selections, omissions, budget values, validation state, and explanations.

The first executable request fixture resolves the historical replay now. Its `requested_revision` is the exact immutable commit `79eef80af3d5969ece7eb9fe7f802be35575f450`, whose expected tree is `3d2853517e64209cffde91766a62e9f70ceb2e47`. It must not use `refs/heads/main` as the requested revision; `main` may appear only as advisory metadata. The compiler reads those historical objects from the current repository through Git plumbing, so later movement of `main` cannot change the replay.

This executable request intentionally differs from the manually assembled architecture example, whose request string was `refs/heads/main`. The executable request digest, package identity, compiler-dependent fields, budget measurement, validation state, and final package digest are therefore expected to differ from the manual example. The first implementation must not claim full byte equality with that example. Invariant source blobs, selected payload bytes, source-content digests, payload digests, selectors, and policy semantics should match where the executable request uses the same historical content and policy. The executable golden package is authoritative only for the executable request fixture and the implemented compiler contract.

The clean committed snapshot protocol is planned as follows:

1. Require `git status --porcelain=v1 -z --untracked-files=all` to return no entries before resolution; staged, unstaged, and untracked content all block compilation.
2. Accept one explicit repository identity and requested revision, then resolve that revision once to an exact commit and its exact tree. Record the advisory branch separately and never use it as immutable identity.
3. Disable replacement-object interpretation for reads, verify the repository object format, and use Git object plumbing against the resolved commit/tree for path lookup and raw blob reads. Do not read source payloads through checkout files, text-conversion filters, or the working tree.
4. Normalize and validate repository-relative POSIX paths before tree lookup; reject absolute, escaping, NUL-containing, backslash, `.`-segment, and `..`-segment paths.
5. Record Git commit, tree, and blob identities alongside SHA-256 raw-source and selected-payload digests.
6. Re-run the same porcelain clean check after compilation and fail if repository state changed. Tests also compare refs and status before and after the call.

Tree entries with mode `120000` (symlink) and `160000` (gitlink/submodule) are unsupported source types in v1. An unsupported mandatory source blocks compilation; an optional source is omitted with an exact reason. Any active replacement ref or alternate object database is a repository-level blocking validation failure in v1 because it changes or obscures the immutable object-resolution boundary.

Protected-reference validation resolves declared ref names and expected immutable identities before selection. A transitively reached protected ref remains excluded unless the request explicitly and authoritatively targets it. Protected and unprotected names resolving to the same object do not erase the protected boundary. A stale or mismatched expected identity blocks compilation rather than silently accepting the currently resolved object.

Dirty-worktree compilation, captured dirty snapshots, submodule traversal, external observations, replacement-object semantics, and worktree-content reads are deferred.

## 15. Validation and Test Strategy

Checkpoint A tests and the foundation-values fixture establish independently verifiable request, policy, canonicalization, safe-integer, identifier, digest, loading, and structural-validation foundations. They do not perform Git resolution, source selection, payload materialization, complete compilation, or golden package reproduction. Checkpoint B adds those executable responsibilities, extends invariant validation, and creates the package fixture only from real compiler output that receives an independent executable verification.

Required first-slice tests are planned to cover:

- all safe-integer boundary values, one-beyond-bound rejection, non-negative byte values, unsupported types, booleans distinct from integers, valid Unicode scalar handling, no normalization, UTF-16 key ordering, UTF-8 without BOM, and byte-identical canonical output;
- duplicate-key JSON rejection and strict request/policy schema and version loading;
- YAML duplicate-key, alias, anchor, merge-key, tag, implicit-timestamp, and unsupported-scalar rejection;
- exact LF and CRLF heading-bounded payload preservation, duplicate-heading occurrence selection, missing-occurrence behavior, and exact policy-allowlisted YAML-field canonical output;
- explicit compiler identity/version presence and absence of ambient defaults;
- clean-status precondition, immutable one-time commit/tree resolution, raw blob reads, protected-reference exclusion, alias and stale-identity behavior, symlink and gitlink handling, replacement-ref and alternate-object-store rejection, dirty-state rejection, post-run clean verification, and no ref/index/worktree mutation;
- fixed five-source selection and ordering, typed reasons, all considered exclusions, unknown-versus-omitted behavior, and stable explanations;
- exact request, policy, snapshot, source, payload, identity, and package digest surfaces;
- distinct package identity and package integrity;
- exact non-self-referential budget values and mandatory-tier failure behavior;
- structural plus invariant validation, including compiler and consumer-contract integrity binding;
- complete golden package reproduction and a second identical-input run producing byte-identical output; and
- rejection of any mismatch in schema, selector output, sizes, digests, ordering, validation, or repository state.

Deferred tests include informative YAML rendering, Atlas commands, agent consumption, live external observations, dirty-worktree capture, submodules, alternate object formats beyond the planned SHA-1 fixture repository, provider token adapters, embeddings, semantic or model selection, execution, autonomy, approval automation, evidence bundles, multi-hop relationships, and AI-environment integration.

The manual YAML architecture example remains informative evidence. It was manually assembled, uses `manual-example-assembly`, is `illustrative_not_validated`, and is non-consumable. The Checkpoint A foundation-values fixture is independently verified deterministic evidence, not a complete compiled package. The Checkpoint B JSON golden package fixture must be produced by the implemented compiler, independently verified with the executable validator, conform to executable schemas, and pass structural and invariant validation. It replays the original EO-2026-013 read-only architecture-assessment handoff using the exact requested commit `79eef80af3d5969ece7eb9fe7f802be35575f450` and expected tree `3d2853517e64209cffde91766a62e9f70ceb2e47`, selects the same accepted five source contents and selector meanings where those contents and policies are invariant, and preserves the architecture-defined digest relationships. It must not be described as byte-for-byte serialization of the illustrative YAML, used to claim full byte equality with that manual example, or retroactively convert that manual artifact into executable evidence.

## 16. Atlas Interface Decision

The first implementation is planned as reusable Python capability beneath Atlas. `context_selection.py` may consume deterministic Repository Knowledge and return typed reasoning output, while the compilation package remains a separate platform module.

Checkpoint A registers the canonical Markdown owner/index `docs/task-context/index.md` in `docs/docs-map.md` and `tools/atlas/platform/document_definitions.py`. This minimal registration makes the structured family visible and explainable through existing Markdown discovery; it does not register each JSON resource as a `DocumentDefinition` and does not add generic structured-resource discovery.

No `atlas context` command, command registration, presentation logic, generic discovery capability, milestone reasoning rule, or other Atlas interface work is included. A future command or generic structured-resource discovery mechanism, if separately authorized, must remain a thin interface and must not reconstruct selection, invent task authority, or create interface-specific canonical context.

## 17. Practical Value and First Consumer

The planned first real slice should accept one explicit versioned read-only compilation request, load one repository-owned selection policy and one budget policy, resolve one clean committed repository snapshot, select the five accepted EO-2026-013 example sources, materialize exact YAML-field and heading-bounded payloads from Git objects, compute every architecture-defined digest, identity, omission, and budget value, emit deterministic canonical JSON, validate schema and invariants, return structured selected and omitted explanations, and reproduce byte-identical output for identical inputs.

Its first real consumer should be an independent replay or audit of the original EO-2026-013 read-only architecture-assessment handoff using the compiled package instead of manually reconstructed context. This tests practical handoff value and source reproducibility without authorizing execution, agent behavior, or provider routing. Informative YAML rendering is deferred.

The accepted five source/selector pairs are:

1. `docs/opportunities/reviewed/EO-2026-013-task-scoped-agent-context-compilation.yaml` — policy-allowlisted Engineering Opportunity fields `id`, `title`, `status`, and `summary`, owned semantically by the canonical Engineering Opportunity Object contract.
2. `docs/current-mission.md` — ATX heading `## Initial Milestone`, occurrence `1`, at the pinned source snapshot.
3. `docs/architecture/repository.md` — ATX heading `## Source of Truth Hierarchy`, occurrence `1`.
4. `docs/architecture/knowledge-authority.md` — ATX heading `### Generated Context`, occurrence `1`.
5. `docs/standards/engineering-collaboration.md` — ATX heading `## Responsibilities`, occurrence `1`.

The fixture request uses `79eef80af3d5969ece7eb9fe7f802be35575f450` as `requested_revision` and verifies tree `3d2853517e64209cffde91766a62e9f70ceb2e47`; it does not request `refs/heads/main`. The compiler reads the historical objects from the current repository through Git plumbing, and later Current Mission advancement or movement of `main` cannot silently change the replay payload. `main` may remain advisory metadata only.

## 18. Risks and Open Decisions

Risks and open decisions to resolve during plan review or implementation review include:

- choosing stable schema `$id` values and exact version-compatibility/error taxonomy without implying network resolution;
- fixing the initial compiler identity/version values as explicit fixture inputs without creating a general ambient default;
- completing the strict-YAML build-versus-adopt decision and introducing no ambient or undeclared dependency;
- completing the RFC 8785 build-versus-adopt comparison while proving UTF-16 ordering, safe-integer handling, and Unicode-scalar rejection consistently across supported Python builds;
- resolving genuinely implementation-specific Git-plumbing details, including the exact commands and error taxonomy used to verify object format, disable replacement-object interpretation, perform tree lookup, and read raw blobs;
- ensuring Git configuration, replacement objects, filters, and platform newline behavior cannot affect immutable reads;
- enforcing the bounded omission candidate universe without a whole-repository candidate scan;
- validating protected-reference aliases, transitive discovery, and stale or mismatched expected identities without weakening the protected boundary;
- keeping explanation presentation derived from typed selection output so it cannot diverge from package contents; and
- reviewing golden fixture changes deliberately so a regenerated fixture cannot conceal a behavioral regression.

The historical snapshot choice is not open: the executable request is pinned to commit `79eef80af3d5969ece7eb9fe7f802be35575f450` with expected tree `3d2853517e64209cffde91766a62e9f70ceb2e47`. If Checkpoint B exposes a defect in an accepted Checkpoint A schema or policy, work stops and returns through a bounded correction review; the schema or policy is not silently changed within Checkpoint B.

The current Atlas document-discovery layers do not include `docs/reviews/`. Consequently, the new review has an exact metadata definition and passes metadata validation, but `./atlas docs` does not list it and `./atlas explain` cannot resolve it under the current implementation. Changing `tools/atlas/platform/discovery.py` is outside this authorized scope and must not be added merely to make this checkpoint green. Any decision to make review documents directly discoverable is separate Atlas interface work.

These are planning and implementation-review questions. They do not authorize external research, dependency installation, broader scope, or implementation now.

## 19. Completed Research Reconciliation

External implementation-readiness research was completed on July 16, 2026 against repository commit `2de09693ed1c922500477c5ba1c6903513ab4dd3`. A citation-portability appendix reconstructed canonical URLs, claim mappings, and the pinned repository corpus. An independent Claude Free challenge pass was also completed under constrained mobile, free-tier, and repository-access conditions.

The research materially supported the architecture's deterministic authority, immutable Git snapshot, RFC 8785, JSON Schema, explicit provenance, context-not-capability, and security boundaries. It also produced the bounded revisions now incorporated into this plan:

- heading occurrence and missing-occurrence semantics;
- explicit omission-candidate bounds;
- protected-reference alias, transitive, and stale-identity handling;
- repository-level rejection of replacement refs and alternate object stores;
- source-level handling of symlinks and gitlinks;
- explicit ownership of Engineering Opportunity fields without a duplicate YAML registry;
- strict-YAML dependency review rather than reliance on ambient `PyYAML`;
- an RFC 8785 build-versus-adopt comparison rather than a predetermined local implementation; and
- clearer separation between relationship data owned by Repository Knowledge and relationship-type allowlists owned by selection policy.

The Claude run is retained as constrained challenge evidence, not as authoritative repository verification or a broad model-quality judgment. Its repository-access failure caused false uncertainty about public repository files, while several implementation-size, YAML, dependency, and test-proportionality critiques remained useful.

The Deep Research workflow itself demonstrated a promising future Aiden Platform capability for structured research orchestration and evidence portability. Future repeated research may combine social-signal intake, primary-source research, daily/weekly/monthly synthesis, model-budget decisions, portable citations, rejected-source logs, independent critique, and human promotion decisions. This finding remains non-canonical and downstream. No new Engineering Opportunity, subscription, recurring automation, or AI-environment change is authorized by this planning review.

The research cycle is sufficient for owner review of this plan. Further external research is not required before the current decision gate. A standards ambiguity or dependency choice discovered during implementation must return through the bounded checkpoint review rather than silently expanding scope.

## 20. Explicit Non-Authorization

Checkpoint A completion authorizes only recording, committing, and pushing the accepted Checkpoint A implementation and its completion-state documentation.

It does not authorize the Checkpoint B package fixture, Git snapshot adapter, source-selection implementation, YAML or heading selectors, payload materialization, compiler, package-integrity implementation, explanations, Checkpoint B tests, Atlas commands, generic repository discovery, milestone-specific Atlas reasoning, a YAML dependency, agent behavior, task-contract implementation, autonomy or approval automation, execution records, provider routing, AI-environment configuration, Engineering Opportunity lifecycle mutation, protected refs, or protected-branch work.

Checkpoint A completion does not automatically authorize Checkpoint B. A separate owner decision remains mandatory.

## 21. Decision Traceability

- July 15, 2026 owner mission selection: EO-2026-013 selected for architecture and design; preserved in `docs/reviews/mission-selection-review-2026-07-15.md`.
- Canonical architecture: `docs/architecture/task-scoped-agent-context-compilation.md`.
- Architecture checkpoint: `2de09693ed1c922500477c5ba1c6903513ab4dd3` — `Define task-scoped context compilation architecture`.
- July 15, 2026 owner decision: architecture completion accepted and mission advanced to Implementation Planning.
- July 16, 2026 owner decision: reconciled implementation plan accepted and Checkpoint A — Deterministic Foundations authorized.
- Checkpoint A authorization baseline: `6d1ee11f4e79b7e7781746b5cf44a17f00390e01` — `Authorize EO-2026-013 Checkpoint A`.
- July 16, 2026 technical verification: exact 18-created / 2-modified scope; no Checkpoint B paths or unapproved dependencies; stable schema URNs; preserved policy and request digests; deep immutability; validator parity; 83 passing tests; Atlas Valid, complete, and Synchronized.
- July 16, 2026 owner decision: Checkpoint A accepted as complete; recording, commit, and push authorized; Checkpoint B explicitly withheld.
- Lifecycle decision: EO-2026-013 and all 21 opportunities remain `reviewed`.
- Atlas decision: no command, generic structured-resource discovery, or milestone-specific rule is authorized.
- Dependency decision: no YAML dependency is authorized; the restricted standard-library canonicalizer remains the accepted Checkpoint A implementation.
- Protected-reference decision: `wip/distinctness-foundation-calibration` remains unchanged at `fcbc5957b89fe65a4313a3c23eb814e02a014698` and out of scope.
- Downstream decision: Checkpoint B, the AI Engineering Environment Review, recurring research automation, and Structured Research Orchestration remain separately governed.
- Current authorization: record, commit, and push accepted Checkpoint A completion only.
- Next decision gate: separate owner authorization, revision, deferral, or rejection of Checkpoint B.

STOP — Preserve Checkpoint A. Do not begin Checkpoint B without a separate owner decision.

## 22. Superseding Executable-Path Decision

The original single Checkpoint B implementation shape in this review is superseded for future authorization purposes by `docs/reviews/eo-2026-013-executable-path-review-2026-07-16.md`.

On July 16, 2026, the owner accepted a revised sequence:

1. Checkpoint A.1 — Executable-Policy Contract Correction.
2. Checkpoint B1 — Immutable Snapshot, Selectors, and Selection Plan.
3. Checkpoint B2 — Compilation, Integrity Validation, Explanation, and Golden Replay.

Only Checkpoint A.1 is authorized. B1 and B2 remain unauthorized.

The protected branch content remains out of scope. Only future identity comparison of the declared protected ref may be considered during a separately authorized B1 review.

STOP — Use the July 16 executable-path review as the active authorization source for work after Checkpoint A.
