# Task-Scoped Agent Context Compilation Architecture

## Purpose

Task-Scoped Agent Context Compilation defines how the repository can produce bounded context for one authorized task without making an AI model responsible for selecting its own authoritative context.

The capability turns an authorized declaration, an immutable repository snapshot, versioned selection and budget policies, and an explicit freshness reference into a reproducible generated package. The package is suitable for replaceable consumers while remaining subordinate to its canonical sources.

This document owns the architecture of that compilation contract. It does not implement the capability.

## Core Principle

The model must not choose its own authoritative context.

Repository documentation, registered repository knowledge, structured Repository Objects, Atlas deterministic state, and explicit owner decisions remain authoritative according to their documented responsibilities.

ChatGPT Project, Codex, and future assistants consume context packages. They do not become canonical context owners.

A generated package can make authoritative material easier to consume. It cannot promote material, change its owner, or acquire the authority of the material it carries.

## Architectural Position

```text
Authorized task declaration
+ pinned repository snapshot
+ selection-policy version
+ budget-policy version
+ explicit as-of input
        ↓
Context Selection Reasoning
        ↓
Context Package Compilation
        ↓
Validated generated non-canonical package
        ↓
ChatGPT / Codex / future replaceable consumers
```

Repository Knowledge discovers registered sources, structured objects, metadata, relationships, and deterministic facts.

Context Selection Reasoning produces a deterministic plan of selected and excluded sources. It explains which rule considered each source, why it was selected or excluded, and which relationship chain reached it.

Context Package Compilation verifies the request, copies task declarations, materializes exact payloads, computes identities, hashes and sizes, applies stable ordering and budget policy, and validates the completed package.

Commands and future interfaces remain thin presentation layers over those responsibilities. A command must not hide selection reasoning, invent task authority, or introduce interface-specific canonical context.

## Responsibility

Given:

- a human- or repository-authorized task declaration;
- an exact repository snapshot;
- a versioned repository-owned source-selection policy;
- a versioned budget policy;
- and an explicit freshness reference;

the capability deterministically selects and materializes the authoritative context required for the bounded task, explains every selection and exclusion, and produces a reproducible generated non-canonical package for replaceable consumers.

The responsibility includes:

- validating the compilation request;
- resolving repository references to immutable identities;
- verifying and copying task and constraint declarations without broadening them;
- selecting exact canonical sources and required supporting evidence;
- recording authority, provenance, freshness, conflicts, unknowns, and omissions;
- applying deterministic sensitivity, scope, deduplication, ordering, and budget rules;
- materializing exact file, structured-field, and heading-bounded payloads;
- computing independent request, policy, snapshot, source, payload, and package digests;
- validating structural and integrity invariants; and
- declaring whether the result is consumable.

## Non-Responsibilities

Task-Scoped Agent Context Compilation is not responsible for:

- originating task authority;
- changing a mission;
- granting permissions;
- choosing autonomy levels;
- execution;
- action history or evidence bundles;
- skill definition;
- outcome evaluation;
- canonical knowledge promotion;
- semantic retrieval;
- model selection;
- AI-environment configuration; or
- conflict resolution requiring human judgment.

It does not implement a retrieval system, infer what a human probably intended, or turn context availability into permission to act.

## Compilation Inputs

A compilation request contains only explicit inputs. No mutable ambient value may affect normative output.

Required inputs are:

1. **Task declaration** — an authorized task identifier, type, goal, scope, non-goals, completion criteria, references, and declaration-level provenance.
2. **Constraint declaration** — permissions, forbidden actions, writable paths, approval points, required validation, and an authority source for every constraint.
3. **Repository target** — repository identity and a requested revision resolvable to an exact commit and tree.
4. **Selection policy** — repository-owned policy identifier, version, complete resolved policy value, and digest.
5. **Budget policy** — policy identifier, version, normative UTF-8 byte limit, tier rules, control-envelope rules, and digest.
6. **Freshness reference** — an explicit `as_of` value and any explicitly supplied observation times required by selected source classes.
7. **Protected-reference constraints** — protected refs and immutable identities that selection must not cross unless the task declaration explicitly and authoritatively targets them.

The request must distinguish absent, unknown, and explicit empty values. It must not use a compiler start time, filesystem time, conversation time, provider state, or implicit current branch as an input.

The selection and budget policies must be available as complete versioned values, not merely mutable names. Their digests bind the exact rules used for compilation.

## Reproducibility Boundary

The initial supported snapshot mode is `clean_committed`.

In that mode:

- the repository worktree must be clean before compilation;
- the requested revision resolves to an exact Git commit;
- the exact root tree identifies repository content;
- branch names are advisory only;
- the commit and tree identities are authoritative;
- every repository source is read from that immutable snapshot, not from an uncaptured working-tree path; and
- repository identity, commit, tree, snapshot mode, and relevant object-format information form the snapshot fingerprint.

Dirty-worktree compilation is outside the first supported boundary. A future dirty mode would have to capture and hash every relevant tracked modification, deletion, staged value, intent-to-add entry, untracked input, ignore-policy effect, submodule state, and other content-bearing difference. An uncaptured dirty worktree must fail compilation.

The same complete inputs must produce byte-identical normative output and the same package digest. Reproducibility does not imply that live observations remain true later; consumers must revalidate live state when the package says it is required.

## Task and Constraint Declarations

Task authority declares:

- goal;
- scope;
- non-goals;
- completion criteria;
- permissions;
- writable paths;
- forbidden actions;
- approval points; and
- required validation.

Context compilation:

- verifies and copies those declarations;
- selects supporting context;
- explains selection and exclusion;
- materializes exact payloads;
- records provenance, authority, freshness, conflicts, unknowns, and omissions;
- enforces budget; and
- validates package integrity.

The compiler must never invent, broaden, infer, or grant task authority.

Every declaration has a value, an authority class, a canonical or human owner, and provenance identifying the exact source declaration. Lists are never merged merely because multiple sources mention related work. When two authoritative declarations compete, the package records a conflict instead of choosing the broader or more convenient value.

Empty and unknown are different states:

- `writable_paths: []` means the authoritative declaration permits no writable paths.
- `writable_paths: {state: unknown}` means the boundary is unresolved and blocks action.
- an absent required declaration is represented as a blocking unknown; it is not interpreted as unrestricted.

The package copies authority. It does not confer it. A consumer must evaluate whether the copied declaration and its owner authorize the consumer's proposed behavior.

## Context Package Schema

The logical top-level fields are mandatory and appear in this order in human-facing representations:

| Field | Semantics |
| --- | --- |
| `schema_version` | Stable identifier for the package schema and its canonical data model. |
| `package` | Deterministic snapshot-specific package identity, identity digest, integrity digest, compilation status, generated and non-canonical declarations, and consumable or non-consumable state. |
| `compilation` | Compiler identity, complete policy identities and versions, policy digests, request digest, and explicit `as_of` input. |
| `repository` | Repository identity, exact requested revision, resolved commit and tree, advisory branch, snapshot mode and fingerprint, object format, and protected-reference constraints. |
| `task` | Task identifier and type plus individually attributed goal, scope, non-goals, completion criteria, mission references, and opportunity references. |
| `declared_constraints` | Individually attributed permissions, forbidden actions, writable paths, approval points, and required validation. |
| `sources` | Stable ordered records for every selected source and selector. |
| `payloads` | Exact materialized content, encoding, media type, UTF-8 byte count, digest, and source linkage. |
| `budget` | Normative unit, limit, fixed tier allocation, measured envelope and payload use, remaining capacity, and budget outcome. |
| `conflicts` | Explicit disagreements, affected declarations or facts, responsible owners, consequence, and blocking state. |
| `unknowns` | Unresolved required information, attempted resolution, owner, consequence, and blocking state. |
| `omissions` | Individual or deterministic policy-class exclusions, rule, reason, authority effect, budget effect, consequence, and reconsideration condition. |
| `validation` | Validation status, invariant results, errors, and explicit statement of whether executable validation occurred. |
| `consumer_contract` | Contract version and mandatory consumer obligations, prohibitions, stop conditions, and revalidation requirements. |

### Package

`package.identity_digest` is SHA-256 over the RFC 8785 canonical JSON bytes of the exact package-identity surface `{"request_digest":request_digest,"snapshot_fingerprint":snapshot_fingerprint}`, where each value is the lowercase hexadecimal digest value rather than its surrounding digest record. `package.id` is `tcp-` followed by the first 24 lowercase hexadecimal characters of `package.identity_digest`. This makes identity deterministic and snapshot-specific without making it self-referential.

The identity digest identifies the request and resolved snapshot; it is not the package integrity digest. `package.digest` records the algorithm, canonicalization contract, and digest of the package digest surface. `package.status` reports compilation outcome independently of consumability. `package.generated` must be `true`, and `package.canonical` must be `false`.

`package.consumability` is either `consumable` or `non_consumable`. A non-consumable result includes stable reasons such as `budget_exceeded`, `blocking_conflict`, `blocking_unknown`, `integrity_failure`, `unsupported_schema`, or `illustrative_not_validated`.

### Compilation

`compilation.compiler` identifies the implementation and version that performed compilation. Manual examples identify manual assembly and must not impersonate an implemented compiler.

`compilation.selection_policy` and `compilation.budget_policy` each contain an identifier, version, complete resolved policy value or immutable reference, and a policy digest. `compilation.request_digest` binds the normalized request. `compilation.as_of` is supplied by the caller. Every request-digest input is carried in the package with its exact typed value, so the digest can be reconstructed without ambient conversation, hidden script state, or an unrecorded request object.

There is no implicit `generated_at`. A wall-clock value appears only if it was supplied as an explicit input and has defined semantics. An implementation's diagnostic runtime logs are execution evidence outside the normative package.

### Repository

`repository.identity` is stable across local checkout paths. `requested_revision` is the exact revision string supplied by the request and is distinct from the resolved immutable `commit` and `tree`. `advisory_branch` is informational and may be absent. `snapshot_mode` initially must be `clean_committed`.

`snapshot_fingerprint` binds repository identity, object format, commit, tree, and snapshot mode. `protected_references` identifies prohibited refs and their expected immutable identities plus whether the task authoritatively targets them.

### Task

`task.id` and `task.type` identify the bounded work. `goal`, `scope`, `non_goals`, and `completion_criteria` each contain a typed value and authority record. Mission and opportunity references are declarations, not implicit lifecycle changes.

Each authority record identifies authority class, owner, and provenance. Provenance identifies the request declaration or immutable repository source and exact selector from which the value was copied.

### Declared Constraints

`declared_constraints` records permissions, forbidden actions, writable paths, approval points, and required validation with separate authority records. A constraint has either a known explicit value or an explicit unknown state. Unknown action boundaries are blocking.

The package never normalizes a prohibition away because a selected source describes a related capability.

### Sources

Every selected source records:

- stable source identifier;
- repository path or structured object identity;
- selector;
- selection rule;
- selection reason;
- trigger;
- selection chain;
- authority class;
- canonical owner;
- commit;
- Git blob or equivalent immutable source identity;
- source content digest;
- transformation or excerpt record;
- freshness status and basis;
- included UTF-8 byte count; and
- payload reference.

One source record represents one immutable source and one selector. Multiple selectors over one file produce separate source records while retaining the same blob and source-content digest.

The initial `sources[*].id` is `src-` followed by the first 16 lowercase hexadecimal characters of the SHA-256 digest of canonical JSON with this exact shape: `{"source_identity":{"path":path,"commit":commit,"blob":blob},"selector":selector}`. A later non-Git source type must define an equally explicit identity surface in its schema version.

### Payloads

A payload is exact selected content, not a generated summary. It records the source record, media type, UTF-8 encoding, exact content, byte count, and payload digest. Unsupported encodings or binary payloads are excluded unless a later policy defines a deterministic safe representation.

The initial `payloads[*].id` is `payload-` followed by the first 16 lowercase hexadecimal characters of its payload digest.

### Results and Traces

`conflicts`, `unknowns`, and `omissions` are explicit arrays. An empty array means the compiler considered the relevant rules and found none; it never means the field was skipped.

The initial omission identifier is `omit-` followed by the first 16 lowercase hexadecimal characters of the SHA-256 digest of canonical JSON with this exact shape: `{"rule":rule,"boundary":boundary,"individual":individual}`. For an individual omission, `boundary` is the stable normalized candidate boundary, initially the normalized repository path or structured object identity, and `individual` is the complete individual candidate identity record. For a policy-class omission, `boundary` is the complete deterministic class-boundary string and `individual` is null.

`validation` distinguishes an executable result from a manual demonstration. `consumer_contract` is part of the package integrity surface so a consumer cannot substitute weaker obligations without changing the digest.

## Source Selection

Selection follows this order:

1. Validate the compilation request.
2. Resolve mutable references to immutable repository identities.
3. Select explicit task anchors.
4. Select canonical owners for targeted facts and responsibilities.
5. Apply the versioned repository-owned task profile.
6. Add mandatory governance and collaboration sources.
7. Traverse only allowlisted typed relationships.
8. Limit default traversal to one hop.
9. Include required deterministic Atlas state.
10. Prefer canonical sources over generated summaries.
11. Apply sensitivity and scope exclusions.
12. Deduplicate deterministically.
13. Apply fixed budget priorities.
14. Materialize exact payloads.
15. Calculate digests.
16. Validate the completed package.

The task profile maps explicit task types and declared targets to stable selection rules. A rule names exact paths, registered object types, structured fields, or heading selectors. It cannot delegate selection to a model.

Relationship traversal is allowlisted, typed, stable, and initially limited to one hop unless an explicit policy rule names a larger bound. A relationship is traversable only when repository metadata defines its type and direction and the selection policy allowlists that type for the task profile. Free-text mentions are not edges.

Required deterministic Atlas state is included only when a policy rule identifies a specific structured fact needed by the task. The package records the state producer, immutable repository basis, input, output identity, and freshness. Command prose or presentation order is not a selection interface.

Stable source ordering is:

```text
priority tier
→ selection rule identifier
→ normalized repository path or object identifier
→ selector
```

Each component uses Unicode scalar-value lexical ordering after schema-defined path normalization. Ties are invalid unless the records are byte-identical duplicates, in which case deterministic deduplication retains one trace and records the coalesced triggers.

Selection must not depend on:

- semantic similarity;
- embeddings;
- vector search;
- model judgment;
- conversational memory;
- Project memory;
- filesystem modification-time order;
- provider rankings; or
- provider-specific token limits.

## Source Exclusion and Deduplication

The initial policies exclude:

- provider memory, Project files, or conversation history unless supplied as explicitly labeled non-canonical evidence;
- sources outside the pinned repository boundary;
- protected-branch content unless explicitly and authoritatively targeted;
- secrets and disallowed sensitivity classes;
- unsupported binary content;
- generated summaries that duplicate selected canonical sources;
- free-text relationship expansion;
- recursive opportunity expansion merely because objects are related; and
- model-generated summaries or inferred facts.

Every considered exclusion produces either an individual omission record or a deterministic policy-class omission record. Every record has the common `boundary` field. An individual record uses its stable normalized candidate boundary and complete `individual` identity record; a class record uses its complete deterministic class-boundary string and null `individual` value. The boundary and rule make the same inputs produce the same record.

Deduplication compares immutable source identity plus selector output. When the same payload is reached through multiple allowed rules, the earliest stable-order source record remains and records every trigger and selection chain. Equal payload digests from different canonical owners are not silently deduplicated because their authority and conflict implications may differ.

Exclusion does not claim irrelevance in general. It states that a deterministic rule excluded the item for this request and records the consequence.

## Authority and Provenance

Authority class follows Knowledge Authority Architecture. At minimum, a package distinguishes canonical knowledge, structured Repository Object state, deterministic Atlas or Git state, source evidence, generated non-canonical context, live observation, human declaration, and unknown information.

Provenance is a chain, not just a path. It records the task trigger, selection rule, relationship edges if any, immutable source identity, selector, materialization transform, and payload digest.

`canonical_owner` names the repository document, object, external authority, or human role responsible for the selected fact. Compilation may report competing ownership claims but may not decide a consequential ownership dispute.

A selected generated artifact retains generated and non-canonical labels and names its canonical inputs and managing process when known. Copying canonical content into a payload does not make the payload canonical.

## Freshness

Every source has one freshness status:

- `current_at_snapshot`
- `stale`
- `unknown`
- `not_applicable`

File age alone must not establish freshness. The explicit `as_of` input is the comparison reference, not evidence by itself.

Freshness is determined by source class:

| Source class | Freshness basis |
| --- | --- |
| Canonical document | `current_at_snapshot` when the pinned snapshot is the requested authority boundary and no repository freshness rule marks it superseded or stale; otherwise `stale` or `unknown`. |
| Current Mission | `current_at_snapshot` only when it is the mission owner at the pinned snapshot and synchronization findings do not show disagreement; a different requested mission or blocking synchronization finding makes it stale or unknown. |
| Generated artifact | Compare immutable source identities and generator contract with its declared `generated_from` and `managed_by`; disagreement is `stale`, incomplete evidence is `unknown`. |
| Repository Object | Evaluate registered schema, lifecycle value, canonical object path, and any object-specific freshness rule at the snapshot; age alone is irrelevant. |
| Atlas or Git state | Bind the exact deterministic producer version and inputs; repository-derived state is current for those inputs, while working-tree state requires a captured snapshot. |
| Live observation | Compare its explicit observation time, target identity, and source-class policy with `as_of`; absent or unverifiable observation metadata is `unknown`. |
| Non-canonical evidence | Use the evidence's declared observation/publication time, target, provenance, and policy; lack of a canonical freshness guarantee is not automatically stale. |

`not_applicable` means that temporal currency does not apply to the selected value, not that freshness was unexamined. Each status includes a human-readable basis and the deterministic rule identifier that produced it.

## Conflicts

Conflicts preserve the responsible authority boundary. A conflict record identifies competing claims, their owners and provenance, affected task or context fields, the detection rule, and whether consumption must stop.

The first deterministic design detects:

- explicitly declared conflicts;
- competing canonical-owner claims;
- path, status, or schema disagreement;
- stale generated-source relationships;
- contradictory task constraints; and
- blocking Atlas validation or synchronization findings.

Contradictory constraints are blocking. A permissive value cannot override a prohibition without an explicit decision from the responsible authority.

Semantic conflict discovery is incomplete without crossing the excluded model-reasoning boundary. The package must state that limitation. Deterministic absence of a detected conflict is not proof that all source meanings agree.

Conflict resolution requiring judgment remains with the responsible owner. Recompilation follows the owner decision or corrected canonical source.

## Unknowns and Omissions

An unknown records required information that could not be established deterministically. It names the field or decision affected, attempted resolution, owner, consequence, and blocking state.

Missing task authority, unresolved permission, unknown writable paths, absent required validation, uncertain repository identity, unsupported policy, or unverified mandatory source integrity is blocking.

An omission records information considered but not included. It contains:

- stable omission identifier or policy class;
- a common `boundary` value containing the stable normalized candidate boundary or complete deterministic class boundary;
- the complete `individual` candidate identity record, or null for a policy-class omission;
- trigger and selection chain when individual;
- exclusion rule and reason;
- authority and freshness information when known;
- byte consequence when budget-related;
- effect on task sufficiency;
- blocking state; and
- exact condition for reconsideration.

Unknown means the compiler cannot establish a required fact. Omitted means the compiler established enough about a candidate to exclude it under policy. Neither is silently converted to an empty value.

## Size and Budget Behavior

The normative budget unit is UTF-8 bytes. Provider token estimates are advisory adapter data only and never change selection, ordering, digest values, or consumability.

Budget allocation order is:

1. Reserve the mandatory control envelope.
2. Include mandatory authoritative sources.
3. Include required supporting sources.
4. Include optional evidence by fixed deterministic priority.

The control envelope contains schema, identity, task and constraint declarations, source and exclusion traces, authority, freshness, conflict and unknown records, integrity metadata, validation state, and the consumer contract. A policy defines the exact control-envelope digest surface and capacity calculation before selection begins.

The first schema measures `control_envelope_bytes` as the UTF-8 byte length of the canonical JSON package after removing `package.digest`, every `payloads[*].content`, and the entire `budget.measurement` value. Removing the measurement value prevents size self-reference. `included_payload_bytes` is the sum of each exact payload's UTF-8 length. `consumed_bytes` is their sum. The budget must cover both values.

Budget rules are strict:

- Never truncate arbitrary characters.
- Never silently remove a source.
- Use an excerpt only when an exact selector is authorized by policy.
- Exclude an entire source or selected section when it cannot fit.
- Record the omission and consequence.
- Do not replace a selected canonical source with a smaller generated summary.
- Emit a non-consumable `budget_exceeded` result when the mandatory control envelope or any mandatory source tier cannot fit.

Heading-bounded excerpts start at the exact selected ATX heading line and end immediately before the next ATX heading of equal or greater level, or at end of file. They preserve the selected source bytes, including line endings. Structured YAML-field selectors resolve schema-known mapping keys, reject aliases and duplicate keys, and serialize the selected mapping as canonical JSON; the selector field list controls inclusion and canonical JSON controls map ordering. Whole-file selectors preserve the Git blob bytes when they are valid UTF-8 text.

## Digest and Serialization Model

All normative digests use SHA-256 and lowercase hexadecimal output unless a later schema version explicitly selects another algorithm.

The normative package data model contains only maps with string keys, ordered lists, UTF-8 strings, integers, booleans, and null. Floating-point numbers, YAML aliases, merge keys, duplicate map keys, implicit timestamps, and implementation-specific scalar tags are forbidden.

Canonical serialization uses RFC 8785 JSON Canonicalization Scheme bytes encoded as UTF-8 without a byte-order mark. Human-facing YAML is an informative representation of the same typed data model. YAML key display order follows the schema for reviewability, but map order does not affect canonical JSON. List order is normative. Text strings preserve their declared Unicode scalar values and line endings; repository text selectors preserve LF or CRLF from the immutable source and never apply ambient newline conversion.

Digest scopes are independent:

| Digest | Exact surface |
| --- | --- |
| Request digest | Canonical JSON of repository request identity and requested revision, attributed task declarations, attributed constraints, selection-policy identifier/version/digest, budget-policy identifier/version/digest, protected-reference constraints, and explicit `as_of`. Resolved commit and tree are excluded because resolution follows request validation. |
| Package identity digest | Canonical JSON of the exact request-digest value and snapshot-fingerprint value. |
| Selection-policy digest | Canonical JSON of the complete resolved selection-policy value excluding its own `digest` field. |
| Budget-policy digest | Canonical JSON of the complete resolved budget-policy value excluding its own `digest` field. |
| Snapshot fingerprint | Canonical JSON of repository identity, object format, exact commit, exact tree, and snapshot mode. Advisory branch and local checkout path are excluded. |
| Source content digest | Raw immutable source bytes before selection or transformation. For Git text, these are exact blob contents, not the Git object header. |
| Payload digest | Exact materialized payload UTF-8 bytes after the declared deterministic selector or transformation. |
| Package digest | Canonical JSON of the complete package after removing only `package.digest`. No other field, including validation and consumer contract, is excluded. |

Git blob identities use the repository's object format and remain distinct from SHA-256 source-content digests.

The initial snapshot-fingerprint object has the exact keys `repository_identity`, `object_format`, `commit`, `tree`, and `snapshot_mode`. The request-digest object has the exact top-level keys `repository_request`, `task`, `declared_constraints`, `selection_policy`, `budget_policy`, `protected_references`, and `as_of`. Its `repository_request` value has the exact shape `{"identity":identity,"requested_revision":requested_revision}`. `task` and `declared_constraints` are their complete attributed package values. Each policy input has the exact shape `{"id":id,"version":version,"digest":digest}`, where `digest` is the complete algorithm, canonicalization, and value map carried by that policy. `protected_references` is the complete ordered package value, and `as_of` is the exact package string. Thus the request digest is reconstructible solely from the package.

The package-identity object has the exact shape `{"request_digest":request_digest,"snapshot_fingerprint":snapshot_fingerprint}` using the two lowercase hexadecimal digest values. `package.identity_digest` is SHA-256 over its RFC 8785 canonical JSON bytes, and `package.id` is `tcp-` plus its first 24 lowercase hexadecimal characters.

The package digest is not self-referential because its own field is absent from its digest surface. A digest value must never be duplicated elsewhere inside the package digest surface as a purported package digest. Validation records refer to the check by name rather than copying the value.

Selectors operate on immutable bytes. Path normalization accepts repository-relative POSIX paths, rejects absolute paths, `.` and `..` segments, NUL, backslash separators, and paths that escape the repository. Selection rules define list ordering before serialization.

No implicit wall-clock generation timestamp is allowed. Any as-of or observation time affecting output is an explicit compilation input. Identical compilation inputs must produce byte-identical normative output and the same package digest.

## Consumer Contract

A consumer must:

- verify schema compatibility;
- verify package, source, and payload digests;
- verify the repository revision;
- preserve authority and provenance labels;
- treat task constraints as copied authoritative declarations rather than permissions created by the package;
- refuse to infer approval from missing information;
- stop on blocking conflicts or unknowns;
- request recompilation or owner resolution when context is stale, conflicting, insufficient, or oversized;
- revalidate live state when required;
- distinguish source content from consumer inference; and
- preserve provider independence.

A consumer must not:

- replace authoritative sources on its own;
- broaden goal, scope, permissions, writable paths, approval, or autonomy;
- silently discard mandatory context;
- resolve consequential conflicts silently;
- promote generated content or inference to canonical status;
- treat the package as authorization, execution evidence, or proof of completion;
- mutate the repository merely because an item is present in context;
- use provider memory to fill a blocking unknown; or
- reinterpret advisory token estimates as the normative budget.

The package is context, not capability. A consumer still requires an authorized task contract, applicable autonomy and approval policy, and any live-state checks owned by the execution environment.

## Validation Invariants

A consumable package satisfies all of these invariants:

- supported schema version;
- supported consumer-contract version;
- exact immutable repository snapshot;
- correct snapshot-specific package identity digest and deterministic package identifier;
- correct digest scopes and values;
- matching source and payload sizes;
- normalized repository-contained paths;
- deterministic selectors;
- selection trace for every included source;
- omission trace for every considered exclusion;
- authority, provenance, and freshness for every source;
- explicit task boundaries;
- explicit constraints or blocking unknowns;
- no declaration broader than its authoritative source;
- no silent truncation;
- budget fit;
- mandatory tiers complete;
- stable ordering;
- prohibited sensitivity absent;
- generated and non-canonical status explicit;
- all conflicts, unknowns, and omissions represented; and
- identical-input recompilation produces identical normative output.

Validation failure makes the package non-consumable. An unsupported schema or consumer contract cannot be downgraded to a warning. A manual example may demonstrate values but cannot claim executable validation.

## Atlas Relationships

Atlas is the likely deterministic interface boundary, not the owner of task authority or canonical context.

Repository Knowledge should expose registered documents, Repository Objects, metadata, generated-artifact ownership, typed relationships, immutable Git identities, and deterministic Atlas state.

Context Selection Reasoning should consume that knowledge with an explicit task profile and produce structured selected-source and omission plans. It remains a distinct reasoning producer and does not evaluate outcomes or make human decisions.

Context Package Compilation should consume the plan and immutable inputs, materialize exact content, enforce the byte budget, compute digests, and validate the result.

Engineering Intelligence or future interfaces may present package status and selection explanations. They must not reconstruct different source selection. Any future `atlas context` command remains a thin interface over these reusable layers.

This milestone adds no Atlas command, compiler, validator, discovery behavior, reasoning rule, or execution capability.

## Boundary with Related Engineering Opportunities

- EO-2026-014 owns task contracts and scope boundaries.
- EO-2026-015 owns autonomy and approval policy.
- EO-2026-016 owns execution records and evidence bundles.
- EO-2026-017 owns stable agent-ready interfaces.
- EO-2026-018 owns reusable engineering skills.
- EO-2026-019 owns effectiveness evaluation.
- EO-2026-013 may carry declarations and references owned by those capabilities but must not absorb their responsibility.

The preserved AI Engineering Environment Review remains downstream and outside this milestone. It requires separate owner authorization and does not become part of context compilation merely because future consumers include ChatGPT Project or Codex.

## Bounded Informative Example

The following complete YAML package is informative, generated/non-canonical in classification, illustrative, and non-executable. It demonstrates a narrow read-only EO-2026-013 architecture-assessment task against commit `79eef80af3d5969ece7eb9fe7f802be35575f450`.

It was manually assembled to demonstrate this contract. It was not produced by an implemented compiler, and no package validator executed. Its integrity values are reproducible applications of the digest surfaces defined above, but its `illustrative_not_validated` state makes it non-consumable.

```yaml
schema_version: aiden.task-context/v1
package:
  id: tcp-192cb659e5992f4be51c9f65
  identity_digest:
    algorithm: sha256
    canonicalization: rfc8785-jcs
    value: 192cb659e5992f4be51c9f65fdff1520a4dc39d1ccce19d0bfdf3a4878354ac7
  digest:
    algorithm: sha256
    canonicalization: rfc8785-jcs
    value: 0176746211dd656b57180aee0d196a03021f06471fff92f342cc05ee98244292
  status: illustrative_not_validated
  generated: true
  canonical: false
  consumability: non_consumable
  non_consumable_reasons:
  - illustrative_not_validated
compilation:
  compiler:
    identity: manual-example-assembly
    version: 1.0.0
    implemented_compiler: false
  selection_policy:
    id: example.read-only-architecture-assessment
    version: 1.0.0
    task_profile: eo-architecture-assessment
    default_relationship_hops: 1
    allowlisted_relationships:
    - related_documents
    ordering:
    - priority_tier
    - selection_rule_id
    - normalized_path_or_object_id
    - selector
    rules:
    - id: S010-explicit-opportunity-anchor
      priority_tier: 10
      selector: yaml-fields:/id,/title,/status,/summary
    - id: S020-current-mission-milestone
      priority_tier: 10
      selector: heading:## Initial Milestone
    - id: S030-canonical-repository-authority
      priority_tier: 20
      selector: heading:## Source of Truth Hierarchy
    - id: S040-mandatory-knowledge-authority
      priority_tier: 30
      selector: heading:### Generated Context
    - id: S050-mandatory-collaboration
      priority_tier: 30
      selector: heading:## Responsibilities
    exclusion_rules:
    - X010-generated-duplicate
    - X020-provider-or-conversation-memory
    - X030-outside-pinned-snapshot
    - X040-protected-reference
    - X050-disallowed-sensitivity
    - X060-unsupported-binary
    - X070-free-text-relationship
    - X080-recursive-opportunity-expansion
    - X090-model-generated-or-inferred
    maximum_sensitivity: ordinary_personal
    digest:
      algorithm: sha256
      canonicalization: rfc8785-jcs
      value: 6942d57d11c30c0a03e49aafc6b60f9810024b612470c6332060dedd91a3080f
  budget_policy:
    id: example.utf8-byte-budget
    version: 1.0.0
    normative_unit: utf8_bytes
    limit_bytes: 65536
    allocation_order:
    - mandatory_control_envelope
    - mandatory_authoritative_sources
    - required_supporting_sources
    - optional_evidence
    control_envelope_measurement:
      canonicalization: rfc8785-jcs
      remove:
      - package.digest
      - payloads[*].content
      - budget.measurement
    overflow_behavior: non_consumable_budget_exceeded
    arbitrary_character_truncation: forbidden
    digest:
      algorithm: sha256
      canonicalization: rfc8785-jcs
      value: 457f2435cdf8ec9edb971665bc5a24b70df1050204a0577fac6f7073a806db1f
  request_digest:
    algorithm: sha256
    canonicalization: rfc8785-jcs
    value: 197535e4459248f3a4a5c3b4b72ff8b0472c723bc78b51bf00450f44c93a39fc
  as_of: '2026-07-15T15:40:26-04:00'
  wall_clock_generation_time: null
repository:
  identity: github.com/aidenm727/t430-homelab
  requested_revision: refs/heads/main
  object_format: sha1
  commit: 79eef80af3d5969ece7eb9fe7f802be35575f450
  tree: 3d2853517e64209cffde91766a62e9f70ceb2e47
  advisory_branch: main
  snapshot_mode: clean_committed
  snapshot_fingerprint:
    algorithm: sha256
    canonicalization: rfc8785-jcs
    value: 14053ce1b4ce71c90c18316bed3928a85a67be6d48fd1bc330ffd8a00464fed8
  protected_references:
  - name: refs/heads/wip/distinctness-foundation-calibration
    expected_object: fcbc5957b89fe65a4313a3c23eb814e02a014698
    authoritatively_targeted: false
    selection: forbidden
task:
  id:
    state: known
    value: example-eo-2026-013-read-only-assessment
    authority:
      class: human_declaration
      owner: repository_owner
    provenance:
      source: manual-example-request-v1
      selector: task.id
  type:
    state: known
    value: architecture_assessment
    authority:
      class: human_declaration
      owner: repository_owner
    provenance:
      source: manual-example-request-v1
      selector: task.type
  goal:
    state: known
    value: Assess the repository-owned architecture basis for a bounded EO-2026-013 context-compilation design checkpoint.
    authority:
      class: human_declaration
      owner: repository_owner
    provenance:
      source: manual-example-request-v1
      selector: task.goal
  scope:
    state: known
    value:
    - Read immutable repository sources selected by the example policy.
    - Identify the authority, reproducibility, selection, and consumer boundaries required by the design.
    authority:
      class: human_declaration
      owner: repository_owner
    provenance:
      source: manual-example-request-v1
      selector: task.scope
  non_goals:
    state: known
    value:
    - Implement a compiler, validator, Atlas command, retrieval system, or execution capability.
    - Modify repository content, mission state, opportunity lifecycle state, protected refs, or AI-environment configuration.
    authority:
      class: human_declaration
      owner: repository_owner
    provenance:
      source: manual-example-request-v1
      selector: task.non_goals
  completion_criteria:
    state: known
    value:
    - Selected sources and exclusions are explained with immutable provenance.
    - Architecture responsibilities and unresolved implementation work are reported for human review.
    authority:
      class: human_declaration
      owner: repository_owner
    provenance:
      source: manual-example-request-v1
      selector: task.completion_criteria
  mission_references:
    state: known
    value:
    - docs/current-mission.md
    authority:
      class: human_declaration
      owner: repository_owner
    provenance:
      source: manual-example-request-v1
      selector: task.mission_references
  opportunity_references:
    state: known
    value:
    - docs/opportunities/reviewed/EO-2026-013-task-scoped-agent-context-compilation.yaml
    authority:
      class: human_declaration
      owner: repository_owner
    provenance:
      source: manual-example-request-v1
      selector: task.opportunity_references
declared_constraints:
  permissions:
    state: known
    value:
    - Read content from the pinned repository snapshot.
    - Compute deterministic selectors, UTF-8 byte sizes, and hashes in temporary local workspace.
    authority:
      class: human_declaration
      owner: repository_owner
    provenance:
      source: manual-example-request-v1
      selector: declared_constraints.permissions
  forbidden_actions:
    state: known
    value:
    - Write or mutate repository content.
    - Stage, commit, push, create or switch branches, or modify refs.
    - Change the active mission or any Engineering Opportunity lifecycle state.
    - Read from or modify the protected branch.
    - Implement or execute the proposed context-compilation capability.
    - Modify ChatGPT Project, Codex, or other AI-environment configuration.
    authority:
      class: human_declaration
      owner: repository_owner
    provenance:
      source: manual-example-request-v1
      selector: declared_constraints.forbidden_actions
  writable_paths:
    state: known
    value: []
    authority:
      class: human_declaration
      owner: repository_owner
    provenance:
      source: manual-example-request-v1
      selector: declared_constraints.writable_paths
  approval_points:
    state: known
    value:
    - Human review is required before any architecture application, implementation, staging, or commit.
    authority:
      class: human_declaration
      owner: repository_owner
    provenance:
      source: manual-example-request-v1
      selector: declared_constraints.approval_points
  required_validation:
    state: known
    value:
    - Verify the pinned commit and tree identities.
    - Verify every selected source blob, source digest, selector output, payload size, and payload digest.
    - State that this manual example did not execute a compiler or package validator.
    authority:
      class: human_declaration
      owner: repository_owner
    provenance:
      source: manual-example-request-v1
      selector: declared_constraints.required_validation
sources:
- id: src-f05784f789d7a5b1
  path: docs/opportunities/reviewed/EO-2026-013-task-scoped-agent-context-compilation.yaml
  structured_object_identity: engineering-opportunity:EO-2026-013
  selector: yaml-fields:/id,/title,/status,/summary
  priority_tier: 10
  selection_rule: S010-explicit-opportunity-anchor
  selection_reason: The task declaration explicitly targets EO-2026-013.
  trigger: task.opportunity_references
  selection_chain:
  - manual-example-request-v1
  - task.opportunity_references
  - EO-2026-013
  authority_class: repository_object_state
  canonical_owner: docs/opportunities/reviewed/EO-2026-013-task-scoped-agent-context-compilation.yaml
  commit: 79eef80af3d5969ece7eb9fe7f802be35575f450
  immutable_source_identity:
    type: git_blob
    object_format: sha1
    value: 79d46f0839653d2df44778a8a5a4c63d50e8318d
  source_content_digest:
    algorithm: sha256
    value: 36b73d6a19d091d580d3319225cdbaf04a7dda222979179711144789a371997f
  transformation:
    type: yaml_field_selection
    selected_fields:
    - /id
    - /title
    - /status
    - /summary
    output: rfc8785-jcs
    line_endings: not_applicable
  freshness:
    status: current_at_snapshot
    basis: The registered opportunity object is read at the pinned snapshot and its selected status is reviewed.
    rule: F010-pinned-canonical-source
    as_of: '2026-07-15T15:40:26-04:00'
  included_utf8_bytes: 324
  payload_ref: payload-cf7550262b7e9352
- id: src-3e334b99840bad45
  path: docs/current-mission.md
  structured_object_identity: null
  selector: heading:## Initial Milestone
  priority_tier: 10
  selection_rule: S020-current-mission-milestone
  selection_reason: The task references Current Mission and the selected heading owns the active design milestone and its included and excluded boundary.
  trigger: task.mission_references
  selection_chain:
  - manual-example-request-v1
  - task.mission_references
  - docs/current-mission.md
  authority_class: canonical_knowledge
  canonical_owner: docs/current-mission.md
  commit: 79eef80af3d5969ece7eb9fe7f802be35575f450
  immutable_source_identity:
    type: git_blob
    object_format: sha1
    value: 3e0d5fe9887c4a935c3a5f39006b4707d64b0355
  source_content_digest:
    algorithm: sha256
    value: cc3d8d2272411e327bc25ca5f6f63080ee4dc456199e54a1e3e3ae4ece1fc941
  transformation:
    type: heading_bounded_excerpt
    start_heading: '## Initial Milestone'
    end_rule: before_next_atx_heading_of_equal_or_greater_level_or_eof
    source_line_endings: lf
    content_change: none
  freshness:
    status: current_at_snapshot
    basis: Current Mission is the canonical active-work owner at the pinned snapshot, repository synchronization does not show disagreement for that snapshot, and as_of is the explicit comparison reference rather than proof of freshness.
    rule: F010-pinned-canonical-source
    as_of: '2026-07-15T15:40:26-04:00'
  included_utf8_bytes: 910
  payload_ref: payload-4ed09ad6e143a64e
- id: src-ce5f32a8805d0c2f
  path: docs/architecture/repository.md
  structured_object_identity: null
  selector: heading:## Source of Truth Hierarchy
  priority_tier: 20
  selection_rule: S030-canonical-repository-authority
  selection_reason: The assessment targets context authority, whose repository source-of-truth order is canonically owned by Repository Architecture.
  trigger: related_documents
  selection_chain:
  - EO-2026-013
  - related_documents
  - docs/architecture/repository.md
  authority_class: canonical_knowledge
  canonical_owner: docs/architecture/repository.md
  commit: 79eef80af3d5969ece7eb9fe7f802be35575f450
  immutable_source_identity:
    type: git_blob
    object_format: sha1
    value: 039d0cf255484602f9b99d0f5397bc619f2bff5b
  source_content_digest:
    algorithm: sha256
    value: 6b1f18f3f97fd58767895fd41ae5b0285ec64f6a1679193ef89ce8f078d6bcac
  transformation:
    type: heading_bounded_excerpt
    start_heading: '## Source of Truth Hierarchy'
    end_rule: before_next_atx_heading_of_equal_or_greater_level_or_eof
    source_line_endings: lf
    content_change: none
  freshness:
    status: current_at_snapshot
    basis: The canonical architecture document is selected from the exact requested snapshot with no repository rule declaring it superseded.
    rule: F010-pinned-canonical-source
    as_of: '2026-07-15T15:40:26-04:00'
  included_utf8_bytes: 1000
  payload_ref: payload-a799667da407c495
- id: src-2b9bc68b8e6a6b9c
  path: docs/architecture/knowledge-authority.md
  structured_object_identity: null
  selector: heading:### Generated Context
  priority_tier: 30
  selection_rule: S040-mandatory-knowledge-authority
  selection_reason: The task profile requires the canonical classification and ownership boundary for generated context.
  trigger: task_profile.mandatory_governance
  selection_chain:
  - eo-architecture-assessment
  - mandatory_governance
  - docs/architecture/knowledge-authority.md
  authority_class: canonical_knowledge
  canonical_owner: docs/architecture/knowledge-authority.md
  commit: 79eef80af3d5969ece7eb9fe7f802be35575f450
  immutable_source_identity:
    type: git_blob
    object_format: sha1
    value: 4f37569dab8f855e2bbd496393e2b9f41a90dece
  source_content_digest:
    algorithm: sha256
    value: a70452eb97ebb7471171c456548bea3f20d222f8794e643e6ae651639617dac2
  transformation:
    type: heading_bounded_excerpt
    start_heading: '### Generated Context'
    end_rule: before_next_atx_heading_of_equal_or_greater_level_or_eof
    source_line_endings: lf
    content_change: none
  freshness:
    status: current_at_snapshot
    basis: The canonical architecture document is selected from the exact requested snapshot with no repository rule declaring it superseded.
    rule: F010-pinned-canonical-source
    as_of: '2026-07-15T15:40:26-04:00'
  included_utf8_bytes: 357
  payload_ref: payload-2724757ec5bd1d14
- id: src-a6a52f599da035ed
  path: docs/standards/engineering-collaboration.md
  structured_object_identity: null
  selector: heading:## Responsibilities
  priority_tier: 30
  selection_rule: S050-mandatory-collaboration
  selection_reason: The task profile requires the collaboration responsibility boundary for the owner, repository, Atlas, and ChatGPT.
  trigger: related_documents
  selection_chain:
  - EO-2026-013
  - related_documents
  - docs/standards/engineering-collaboration.md
  authority_class: canonical_knowledge
  canonical_owner: docs/standards/engineering-collaboration.md
  commit: 79eef80af3d5969ece7eb9fe7f802be35575f450
  immutable_source_identity:
    type: git_blob
    object_format: sha1
    value: a5a8c0e79570e42387ebb6abde5dde8224b545ef
  source_content_digest:
    algorithm: sha256
    value: 98accba61d270275226d58f3304634e724f795b297e3b360cb597a403cae9e64
  transformation:
    type: heading_bounded_excerpt
    start_heading: '## Responsibilities'
    end_rule: before_next_atx_heading_of_equal_or_greater_level_or_eof
    source_line_endings: lf
    content_change: none
  freshness:
    status: current_at_snapshot
    basis: The canonical standard is selected from the exact requested snapshot with no repository rule declaring it superseded.
    rule: F010-pinned-canonical-source
    as_of: '2026-07-15T15:40:26-04:00'
  included_utf8_bytes: 503
  payload_ref: payload-41d0657c08be387a
payloads:
- id: payload-cf7550262b7e9352
  source_ref: src-f05784f789d7a5b1
  media_type: application/json
  encoding: utf-8
  content: '{"id":"EO-2026-013","status":"reviewed","summary":"Develop a deterministic capability that compiles a reproducible, task-specific context package for a bounded engineering mission or task without making the AI model responsible for selecting its own authoritative context.\n","title":"Task-scoped agent context compilation"}'
  utf8_bytes: 324
  digest:
    algorithm: sha256
    value: cf7550262b7e935234a6edafa07e807b36a3b54ee04d50bffd57c37d93b18a3c
- id: payload-4ed09ad6e143a64e
  source_ref: src-3e334b99840bad45
  media_type: text/markdown
  encoding: utf-8
  content: |+
    ## Initial Milestone

    Define the Task-Scoped Agent Context Compilation architecture and one bounded example package.

    The architecture is expected to be documented later, likely under `docs/architecture/`. This mission-selection application does not create that architecture document or begin capability implementation.

    ### Included

    - Package schema.
    - Deterministic source selection.
    - Source-selection explanations.
    - Provenance and authority.
    - Freshness.
    - Conflicts and unknowns.
    - Context-size behavior.
    - Omissions.
    - Consumer contract.
    - One bounded example package.

    ### Excluded

    - Embeddings.
    - Vector databases.
    - Model-based retrieval.
    - LLM invocation.
    - Autonomous execution.
    - Broad agent authority.
    - Live ChatGPT Project cleanup.
    - Live Project settings changes.
    - Codex configuration changes.
    - Provider-specific permanent architecture.
    - Engineering Opportunity lifecycle mutation.

    ---

  utf8_bytes: 910
  digest:
    algorithm: sha256
    value: 4ed09ad6e143a64e08e491c72dba7d6e9a7bc3bf3dc2e329b19393ae9e89a9e4
- id: payload-a799667da407c495
  source_ref: src-ce5f32a8805d0c2f
  media_type: text/markdown
  encoding: utf-8
  content: |+
    ## Source of Truth Hierarchy

    GitHub is the canonical documentation source.

    The repository is the canonical source of truth for Aiden Platform engineering knowledge.

    Architecture documents define intent.

    The hierarchy is:

    1. Vision defines purpose and durable direction.
    2. Architecture records describe intent and structural design.
    3. Standards records describe expected engineering behavior.
    4. Current Mission defines active engineering work.
    5. Infrastructure records describe current implementation and state.
    6. Operations records describe change evidence and history.
    7. Roadmaps describe likely future direction and sequencing.
    8. Repository Objects preserve structured candidates and lifecycle state.
    9. Generated context summarizes canonical documentation and never replaces it.
    10. Git history records repository evolution.
    11. Live verification resolves current operational reality.

    Conversation context may explain intent but does not replace canonical repository knowledge.

    ---

  utf8_bytes: 1000
  digest:
    algorithm: sha256
    value: a799667da407c49563d2cfe03bb44e5ba18840aa71d962b805d8741b60a8cf07
- id: payload-2724757ec5bd1d14
  source_ref: src-2b9bc68b8e6a6b9c
  media_type: text/markdown
  encoding: utf-8
  content: |+
    ### Generated Context

    Rebuildable material derived from canonical or source records.

    Examples include:

    - `docs/aiden-context.md`.
    - `docs/infrastructure-snapshot.md`.
    - Future task context packages.
    - Generated summaries.

    Generated context should identify its sources and managing process.

    It may be useful and accurate while remaining non-canonical.

  utf8_bytes: 357
  digest:
    algorithm: sha256
    value: 2724757ec5bd1d1460f3754d4e3a8a76c41d84f0d811cdb11e5605ade619f97e
- id: payload-41d0657c08be387a
  source_ref: src-a6a52f599da035ed
  media_type: text/markdown
  encoding: utf-8
  content: |+
    ## Responsibilities

    The human engineer owns goals, judgment, execution, verification, review, commits, and final decisions.

    The repository preserves canonical engineering truth through architecture, infrastructure records, operations history, roadmaps, standards, generated context, and engineering tools.

    Atlas provides deterministic engineering awareness from the repository and working tree.

    ChatGPT assists with architecture, planning, explanation, documentation, and implementation artifacts.

  utf8_bytes: 503
  digest:
    algorithm: sha256
    value: 41d0657c08be387a100892d64cc2bd4dfa3ead10ef51e7cf90dc29e9c52883f8
budget:
  normative_unit: utf8_bytes
  limit_bytes: 65536
  allocation_order:
  - mandatory_control_envelope
  - mandatory_authoritative_sources
  - required_supporting_sources
  - optional_evidence
  measurement:
    control_envelope_bytes: 26391
    included_payload_bytes: 3094
    consumed_bytes: 29485
    remaining_bytes: 36051
  outcome: fits
  provider_token_estimates: []
conflicts: []
unknowns: []
omissions:
- id: omit-8c38387b8298816e
  record_type: individual
  boundary: docs/aiden-context.md
  individual:
    path: docs/aiden-context.md
    commit: 79eef80af3d5969ece7eb9fe7f802be35575f450
    immutable_source_identity:
      type: git_blob
      object_format: sha1
      value: f39b7836c133d17ede5c37da5d53df0cbb658399
    source_content_digest:
      algorithm: sha256
      value: 795cfbcddae98fbe40242df0d41bf4155f2531fd2cfafc99885b4a8afe918123
    selection_chain:
    - docs/current-mission.md
    - generated_from
    - docs/aiden-context.md
    freshness:
      status: unknown
      basis: Freshness was not evaluated because canonical deduplication excluded the candidate before freshness evaluation.
  trigger: selection_policy.exclusion_rules
  selection_chain:
  - docs/current-mission.md
  - generated_from
  - docs/aiden-context.md
  rule: X010-generated-duplicate
  reason: Generated context duplicates the selected canonical Current Mission source.
  authority_effect: No selected canonical authority is replaced by the omitted material.
  freshness:
    status: unknown
    basis: Freshness was not evaluated because canonical deduplication excluded the candidate before freshness evaluation.
  budget_bytes_not_included: null
  consequence: No loss of authority; the canonical source is included.
  blocking: false
  reconsideration_condition: Reconsider only if a later task profile requires generated-artifact synchronization evidence.
- id: omit-9bc13a08315b132b
  record_type: policy_class
  boundary: provider memory, Project files, and conversation history not explicitly supplied as labeled evidence
  individual: null
  trigger: selection_policy.exclusion_rules
  selection_chain: []
  rule: X020-provider-or-conversation-memory
  reason: The policy forbids ambient provider context as authoritative input.
  authority_effect: No selected canonical authority is replaced by the omitted material.
  freshness:
    status: unknown
    basis: Freshness is unknown because this omission represents a policy class rather than an individual candidate with evaluable freshness.
  budget_bytes_not_included: null
  consequence: Consumer-specific memory cannot alter the package.
  blocking: false
  reconsideration_condition: Supply an exact non-canonical evidence artifact through an authorized request.
- id: omit-e4f8ce25471b9194
  record_type: policy_class
  boundary: repository or filesystem content outside the exact pinned commit and tree
  individual: null
  trigger: selection_policy.exclusion_rules
  selection_chain: []
  rule: X030-outside-pinned-snapshot
  reason: The clean committed snapshot is the reproducibility boundary.
  authority_effect: No selected canonical authority is replaced by the omitted material.
  freshness:
    status: unknown
    basis: Freshness is unknown because this omission represents a policy class rather than an individual candidate with evaluable freshness.
  budget_bytes_not_included: null
  consequence: Uncaptured external content cannot influence selection.
  blocking: false
  reconsideration_condition: Authorize and immutably identify an external evidence boundary in a later policy.
- id: omit-a3f86e7d95109184
  record_type: policy_class
  boundary: refs/heads/wip/distinctness-foundation-calibration and its content
  individual: null
  trigger: selection_policy.exclusion_rules
  selection_chain: []
  rule: X040-protected-reference
  reason: The protected reference is not authoritatively targeted and is explicitly forbidden.
  authority_effect: No selected canonical authority is replaced by the omitted material.
  freshness:
    status: unknown
    basis: Freshness is unknown because this omission represents a policy class rather than an individual candidate with evaluable freshness.
  budget_bytes_not_included: null
  consequence: Protected-branch content cannot influence the assessment.
  blocking: false
  reconsideration_condition: Provide a new authoritative task declaration that explicitly targets the protected ref.
- id: omit-56176915e66f3e06
  record_type: policy_class
  boundary: secrets and content above ordinary_personal sensitivity
  individual: null
  trigger: selection_policy.exclusion_rules
  selection_chain: []
  rule: X050-disallowed-sensitivity
  reason: The example policy disallows those sensitivity classes.
  authority_effect: No selected canonical authority is replaced by the omitted material.
  freshness:
    status: unknown
    basis: Freshness is unknown because this omission represents a policy class rather than an individual candidate with evaluable freshness.
  budget_bytes_not_included: null
  consequence: Sensitive content is absent from the package.
  blocking: false
  reconsideration_condition: Use a separately authorized policy and consumer boundary capable of handling the class.
- id: omit-c71822ff0b1828e6
  record_type: policy_class
  boundary: binary or non-UTF-8 source content
  individual: null
  trigger: selection_policy.exclusion_rules
  selection_chain: []
  rule: X060-unsupported-binary
  reason: The initial selector and payload contract supports exact UTF-8 text only.
  authority_effect: No selected canonical authority is replaced by the omitted material.
  freshness:
    status: unknown
    basis: Freshness is unknown because this omission represents a policy class rather than an individual candidate with evaluable freshness.
  budget_bytes_not_included: null
  consequence: Binary content cannot be included or summarized.
  blocking: false
  reconsideration_condition: Adopt a later deterministic binary representation policy.
- id: omit-0fecfd1a161ab314
  record_type: policy_class
  boundary: relationships inferred from prose or unregistered mentions
  individual: null
  trigger: selection_policy.exclusion_rules
  selection_chain: []
  rule: X070-free-text-relationship
  reason: Only allowlisted typed repository relationships may be traversed.
  authority_effect: No selected canonical authority is replaced by the omitted material.
  freshness:
    status: unknown
    basis: Freshness is unknown because this omission represents a policy class rather than an individual candidate with evaluable freshness.
  budget_bytes_not_included: null
  consequence: Prose mentions do not expand context.
  blocking: false
  reconsideration_condition: Register and allowlist an exact typed relationship.
- id: omit-fb7b2bb005ecd465
  record_type: policy_class
  boundary: opportunities related to EO-2026-013 beyond explicitly selected EO-2026-013
  individual: null
  trigger: selection_policy.exclusion_rules
  selection_chain: []
  rule: X080-recursive-opportunity-expansion
  reason: Relationship traversal is limited to one hop and the task profile does not select related opportunities.
  authority_effect: No selected canonical authority is replaced by the omitted material.
  freshness:
    status: unknown
    basis: Freshness is unknown because this omission represents a policy class rather than an individual candidate with evaluable freshness.
  budget_bytes_not_included: null
  consequence: The package remains bounded to the selected opportunity.
  blocking: false
  reconsideration_condition: Add an explicit task anchor or policy rule for a named related opportunity.
- id: omit-7431ffd5efc0febf
  record_type: policy_class
  boundary: model-generated summaries, semantic retrieval results, and inferred facts
  individual: null
  trigger: selection_policy.exclusion_rules
  selection_chain: []
  rule: X090-model-generated-or-inferred
  reason: The selection policy permits only deterministic exact sources and selectors.
  authority_effect: No selected canonical authority is replaced by the omitted material.
  freshness:
    status: unknown
    basis: Freshness is unknown because this omission represents a policy class rather than an individual candidate with evaluable freshness.
  budget_bytes_not_included: null
  consequence: No model judgment enters the authoritative payload.
  blocking: false
  reconsideration_condition: A future evidence policy may carry labeled non-canonical inference without replacing sources.
validation:
  status: illustrative_not_executed
  executable_validation_performed: false
  checks:
  - invariant: pinned_source_and_payload_identity_values
    status: manually_demonstrated
  - invariant: digest_surfaces_and_utf8_sizes
    status: manually_demonstrated
  - invariant: executable_schema_and_package_validation
    status: not_executed
  - invariant: identical_input_recompilation
    status: not_executed
  errors: []
  limitations:
  - No context compiler or package validator exists for this architecture checkpoint.
  - Deterministic checks cannot establish absence of every semantic conflict.
consumer_contract:
  version: aiden.task-context-consumer/v1
  must:
  - verify_schema_compatibility
  - verify_package_source_and_payload_digests
  - verify_repository_revision
  - preserve_authority_and_provenance
  - treat_constraints_as_copied_declarations_not_package_created_permissions
  - refuse_to_infer_approval_from_missing_information
  - stop_on_blocking_conflicts_or_unknowns
  - request_recompilation_or_owner_resolution_for_stale_conflicting_insufficient_or_oversized_context
  - revalidate_live_state_when_required
  - distinguish_source_content_from_consumer_inference
  - preserve_provider_independence
  must_not:
  - replace_authoritative_sources
  - broaden_goal_scope_permissions_writable_paths_approval_or_autonomy
  - silently_discard_mandatory_context
  - silently_resolve_consequential_conflicts
  - promote_generated_content_or_inference_to_canonical_status
  - treat_package_as_authorization_execution_evidence_or_proof_of_completion
  - mutate_repository_because_an_item_is_present_in_context
  stop_conditions:
  - package_is_non_consumable
  - integrity_verification_fails
  - repository_revision_does_not_match
  - blocking_conflict_or_unknown_exists
  - required_live_state_cannot_be_revalidated
  live_revalidation_required: []
```

## Initial Operating Boundary

The first engineering checkpoint is architecture only. It defines:

- the logical package schema;
- task-authority separation;
- clean committed snapshot reproducibility;
- deterministic exact selectors;
- source selection and exclusion order;
- typed one-hop relationship traversal;
- authority, provenance, freshness, conflict, unknown, and omission records;
- normative UTF-8 byte budgeting;
- canonical digest surfaces;
- consumer obligations and prohibitions; and
- one manually assembled bounded example.

It does not authorize or provide:

- a compiler or validator;
- an Atlas command;
- retrieval, embeddings, or a vector database;
- model-driven selection or summarization;
- dirty-worktree support;
- execution or autonomy;
- AI-environment changes;
- a new Repository Object type;
- opportunity lifecycle changes; or
- milestone-specific Atlas reasoning.

Clean committed repository snapshots are the only initially supported reproducibility boundary. An uncaptured dirty worktree fails compilation.

## Future Direction

After human architecture review, a separate checkpoint may define an implementation plan for repository-owned selection-policy and budget-policy artifacts, typed context-selection reasoning output, compiler boundaries, validators, and thin interfaces.

Later work may consider captured dirty snapshots, additional deterministic selectors, signed or attestable packages, live-observation adapters, sensitivity-aware external evidence, multi-hop relationship policies, and provider adapters that report advisory token estimates.

Those directions remain subordinate to the core rules: task authority is external to compilation, canonical ownership stays with responsible sources, selection remains explainable and reproducible, and replaceable consumers never choose their own authoritative context.
