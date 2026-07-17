# Task-Context Structured Resources

## Purpose and Stewardship

This document is the canonical human-readable owner and navigation index for the repository-owned structured resources under `docs/task-context/`.

The artifact family provides versioned machine-readable contracts and policy values for Task-Scoped Agent Context Compilation. The repository owner stewards the family through human review, exact versioning, deterministic digest recomputation, tests, Atlas validation, and repository synchronization.

The canonical architecture remains `docs/architecture/task-scoped-agent-context-compilation.md`. This index owns the identity, inventory, classification, loading contract, and maintenance boundary of the structured resource family; it does not replace or broaden that architecture.

## First-Slice Inventory

The following JSON Schema Draft 2020-12 documents are canonical machine-readable repository knowledge:

- `docs/task-context/schemas/selection-policy-v1.schema.json` — schema ID `urn:aiden-platform:task-context:schema:selection-policy:v1`; contract version `aiden.task-context.selection-policy/v1`; defines the bounded v1 selection-policy shape.
- `docs/task-context/schemas/budget-policy-v1.schema.json` — schema ID `urn:aiden-platform:task-context:schema:budget-policy:v1`; contract version `aiden.task-context.budget-policy/v1`; defines the bounded v1 UTF-8 byte-budget policy shape.
- `docs/task-context/schemas/compilation-request-v1.schema.json` — schema ID `urn:aiden-platform:task-context:schema:compilation-request:v1`; contract version `aiden.task-context.compilation-request/v1`; defines explicit request, policy-reference, compiler, freshness, authority, and protected-reference inputs.
- `docs/task-context/schemas/context-package-v1.schema.json` — schema ID `urn:aiden-platform:task-context:schema:context-package:v1`; contract version `aiden.task-context/v1`; defines the structural package boundary without establishing integrity, compilation, or consumability.

The following versioned policies are canonical machine-readable repository knowledge:

- `docs/task-context/policies/selection/example-read-only-architecture-assessment-v1.json` — policy ID `example.read-only-architecture-assessment`; version `1.0.1`; owns the exact historical example task profile, typed source rules, explicit source budget tiers and sensitivity classifications, one-hop relationship allowlist, selector data, ordering, exclusions, sensitivity ceiling, and bounded omission-candidate universe.
- `docs/task-context/policies/budget/example-utf8-65536-v1.json` — policy ID `example.utf8-byte-budget`; version `1.0.0`; owns the exact 65,536 UTF-8-byte limit, allocation order, control-envelope removal surface, mandatory-tier overflow result, and truncation prohibition.

The JSON files under `tests/fixtures/task_context/requests/` and `tests/fixtures/task_context/expected/` are non-canonical test evidence. The request fixture preserves an exact historical replay input. The expected-values fixture preserves independently reproducible Checkpoint A calculations. Neither fixture owns architecture or policy, and the expected-values fixture is neither a compiled package nor a golden package.

## Consumers

Checkpoint A consumers are repository-local validators, digest and canonicalization tests, implementation review, and future Checkpoint B code after separate authorization. Future Atlas interfaces and replaceable AI consumers may consume validated outputs only through separately reviewed capabilities; they do not become owners of these contracts or policies.

The schema `$id` values use stable repository-owned, non-network URNs because no HTTPS namespace has been established as a canonical authority for this family. They are evidence identities, not network-loading instructions, and no network resolution is required or permitted by the v1 loader contract.

## Exact-Path-and-Digest Loading Contract

Structured resources are loaded from an explicitly selected repository path. A mutable name, directory scan, schema `$id`, ambient package, provider memory, or network lookup must not choose a policy.

The loader must:

1. read exact bytes from the requested path as UTF-8 without a byte-order mark;
2. reject duplicate keys, floating-point syntax, non-finite numbers, unsafe integers, invalid Unicode scalar values, unsupported values, and unknown fixed-object fields;
3. validate the supported schema and version;
4. recompute the policy digest over canonical JSON of the complete policy with only its own top-level `digest` field excluded; and
5. require the requested policy ID, version, and complete digest record to match exactly.

Policy values are therefore identified by exact repository path plus exact self-excluding SHA-256 digest. The path locates the reviewed value and the digest binds its complete normative contents.

## Update Mechanism

Changes require a bounded reviewed repository change. A maintainer updates the owning schema or policy, advances its version when its accepted contract changes, recomputes every affected self-excluding policy and request digest, updates non-canonical expected evidence, runs the full unittest and Atlas verification sequence, and obtains human review.

An existing version must not be silently reinterpreted. A schema or policy defect discovered after Checkpoint A returns through a bounded correction review. Checkpoint B must not silently change a frozen Checkpoint A contract.

Checkpoint A.1 is a reviewed, digest-changing, pre-executable defect correction. It advances only the selection-policy instance to `1.0.1`; the budget-policy instance remains `1.0.0`, and all four stable schema URNs remain unchanged. Every selection rule now owns an explicit source allocation `budget_tier`, and every rule source owns an explicit `sensitivity` classification.

## Canonical JSON Build-versus-Adopt Decision

Checkpoint A compared three bounded implementation paths behind the repository-owned `canonical_json.py` interface:

| Path | Correctness and RFC 8785 behavior | Dependency and maintenance burden | Auditability and cross-testing | Decision |
| --- | --- | --- | --- | --- |
| Trail of Bits `rfc8785` | Strongest maintained dependency candidate; directly targets RFC 8785, including UTF-16 property ordering and canonical escaping. Its general number behavior is broader than this repository's integer-only model, so repository checks would still be required. | Adoption requires a repository dependency mechanism, reviewed dependency metadata, version pinning, and an expanded path scope that Checkpoint A does not authorize. An ambient installation would not be reproducible. | Strong external implementation and known-vector reference. | Do not adopt in this scope. |
| RFC-referenced implementations | Useful independent references for property ordering, escaping, and known vectors across implementations. | Vendoring would create provenance, update, dependency, and reviewed-scope obligations without an accepted repository dependency path. | Retain as cross-check references only; no code is copied or vendored. | Do not vendor. |
| Restricted standard-library implementation | The normative model excludes floating point and is limited to string-keyed maps, ordered lists, strings, safe integers, booleans, and null. This makes the required serializer small and testable. | No new dependency or manifest is required. The repository owns ongoing conformance tests and maintenance. | The complete implementation is locally auditable and is cross-tested with RFC property-order and escaping vectors, nested structures, Unicode boundaries, and byte-repeat tests. | Selected for Checkpoint A. |

The selected implementation preserves `canonical_json.py` as the small stable repository interface and uses only the Python standard library. It rejects every float rather than implementing ECMAScript floating-point serialization. It treats booleans separately from integers, enforces the inclusive integer range `[-9007199254740991, 9007199254740991]`, rejects non-string keys and unsupported Python types, rejects lone UTF-16 surrogates, preserves Unicode without normalization, sorts keys recursively by unsigned UTF-16 code units, applies RFC 8785 JSON string escaping, and emits UTF-8 bytes without a byte-order mark or insignificant whitespace.

Trail of Bits `rfc8785` remains the strongest dependency candidate if a later reviewed repository dependency mechanism and expanded path scope are authorized. RFC-referenced implementations remain cross-check sources, not vendored code.

## Dependency Boundary

Checkpoint A adds no third-party dependency and relies on no ambient package. Runtime schema validation is an explicit repository-local implementation of the bounded v1 contracts; the JSON Schema documents remain the portable canonical shapes. No `jsonschema` or YAML package is required.

The strict raw JSON loader remains the contract entry point. After a mapping passes that boundary, typed request and policy constructors copy and deeply freeze every nested normative value: mappings become read-only mappings, lists and tuples become tuples, and scalar values retain their exact values without string normalization. Unsupported values, unsafe integers, invalid Unicode scalar values, and non-string mapping keys are rejected at the model boundary. The canonical JSON interface accepts these read-only mappings and tuple-backed ordered sequences, so typed values retain deterministic digest behavior without exposing mutable nested state.

The repository-local validators now enforce the accepted v1 schema constants, enums, exact fixed-object and selector shapes, non-empty string boundaries, digest forms, safe and non-negative integers, and package classification and identity patterns. They also retain bounded local cross-field checks such as requiring authoritative targeting before a protected reference may be selected. JSON Schema remains the portable canonical shape, while Python owns this local enforcement; Checkpoint A still performs structural package validation only and does not claim package integrity or consumability.

YAML parsing, YAML-field selection, heading selection, Git object access, and any dependency choice for those responsibilities remain outside Checkpoint A. A future dependency must have an authorized repository dependency mechanism and reviewed path scope before it may become normative.

## Atlas Registration Boundary

Only this Markdown index is registered as a `DocumentDefinition` and listed in `docs/docs-map.md`. The six JSON resources remain canonical machine-readable repository knowledge owned through this index, but they are not individually presented as Markdown documents.

This minimal registration makes the family visible through existing Atlas document discovery. Generic structured-resource discovery, directory scanning, schema-ID resolution, and policy lookup remain deferred capabilities and are not implemented by Checkpoint A.

## Checkpoint Boundary

Checkpoint A and its A.1 contract correction establish deterministic foundations only: schemas, exact policies, a strict request fixture, independently reproducible expected values, immutable typed values, strict JSON loading, canonical JSON, digest and identifier helpers, and structural validation.

Checkpoint A.1 does not resolve a Git snapshot, traverse relationships, select sources, parse YAML or headings, materialize payloads, execute budgeting, compile or assemble a package, calculate package integrity, render explanations, add an Atlas command, or produce a package fixture. Structural validation of a deliberately non-consumable test object demonstrates only the accepted package shape and does not establish compilation, integrity, or consumability.

Checkpoint B1a establishes only the immutable local Git snapshot boundary. It requires an explicit existing non-bare target repository in `clean_committed` mode, verifies the bounded repository identity from repository-local origin fetch URLs, accepts one exact full lowercase SHA-1 commit, verifies its exact root tree and SHA-1 object format, and computes the snapshot fingerprint over repository identity, object format, commit, tree, and snapshot mode. It also provides exact repository-relative path validation and raw regular-file blob access from the immutable root tree rather than HEAD or worktree content.

Every production Git operation in this boundary is read-only, replacement-disabled, alternate-free, lazy-fetch-disabled, literal-path, locale-stable, network-free, and target-write-free. The adapter rejects ambient repository, worktree, index, object-store, and injected-configuration control state; replacement refs, grafts, and alternate metadata; dirty tracked, staged, untracked, or submodule state; unsupported object formats; and non-regular tree entries. Clean state is checked before and after each snapshot operation.

Protected-reference handling is content-blind. B1a queries only an exact declared full ref name, compares only its direct object identity with the expected identity, and never peels, traverses, reads, selects, exposes, checks out, or mutates protected content. Missing or mismatched protected-ref identity is blocking.

Returned blob content remains exact raw bytes. B1a does not decode, parse, select, transform, summarize, hash as source content or payload, apply a budget, or construct a package. B1a remains unchanged by the separately authorized B1b1 selector boundary below. Checkpoint B1b2 remains unauthorized for relationship verification and selection reasoning. Checkpoint B2 remains unauthorized for compilation, integrity validation, explanation, budgeting, and golden replay. Protected-branch content remains out of scope.

Checkpoint B1b1 adds only pure deterministic selector primitives over caller-supplied immutable bytes. All selector inputs cross one strict UTF-8 boundary that rejects a byte-order mark, invalid UTF-8, NUL, lone surrogates, bare carriage returns, and mixed LF and CRLF input. Accepted source line endings are classified explicitly as `lf`, `crlf`, or `none`, without Unicode normalization or ambient newline conversion.

The bounded YAML parser supports only the documented historical Engineering Opportunity subset: one top-level mapping containing strings, top-level string sequences, and bare folded or literal block strings. It is not a general YAML parser. `yaml_fields` includes exactly the caller-requested fields and emits repository-owned canonical JSON UTF-8 bytes. Folded blocks replace a break between two nonempty logical lines with one ASCII space, preserve a break adjacent to an empty logical line as `\n`, remove trailing empty logical lines, and apply exactly one final `\n`. Literal blocks join the remaining logical lines with `\n` and likewise apply exactly one final `\n`.

The Markdown `heading` selector matches one exact ATX heading occurrence outside the bounded backtick and tilde fence model. It returns the selected heading and following section through the byte immediately before the next outside-fence ATX heading of equal or higher level, or through end of file. The returned section preserves the exact original bytes, including LF or CRLF endings, blank lines, whitespace, and terminal-newline state.

B1b1 performs no Git access, repository discovery, generic policy selection, relationship verification, source selection, digest calculation, budget execution, or package work. Checkpoint B1a and its content-blind protected-reference behavior remain unchanged. B1b2 and B2 remain unauthorized, and protected content remains outside the selector input and capability boundary.
