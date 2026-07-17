# EO-2026-013 Checkpoint B1b1 Authorization Review — July 16, 2026

- Authority class: Human-Reviewed Implementation-Planning Decision
- Canonical: No
- Generated: No
- Status: Checkpoint B1b1 Completion Accepted; B1b2 and B2 Withheld
- Date: July 16, 2026
- Repository baseline: `e89d765ab7d62c97976091f53ce59dd3f767e4cb`
- Decision authority: Owner

---

## 1. Purpose and Authority

This non-canonical dated review records the separate owner decision required after EO-2026-013 Checkpoint B1a completion.

The owner accepted the revised B1b sequence and authorized only Checkpoint B1b1 — Deterministic Selector Primitives.

Checkpoint B1b2 and Checkpoint B2 remain unauthorized.

This review does not change EO-2026-013 or any other Engineering Opportunity lifecycle state.

It does not authorize source-candidate derivation, policy dispatch, relationship verification, source selection, selection plans, omissions, unknowns, freshness, conflicts, source or payload digests, budget execution, package compilation, package integrity, explanations, Atlas commands, task-contract implementation, execution, autonomy, provider routing, AI-environment work, protected-reference behavior changes, or protected-branch content access.

---

## 2. Recorded Owner Decision

The owner recorded:

> Accept the revised EO-2026-013 B1b plan. Authorize Checkpoint B1b1 — Deterministic Selector Primitives only. Do not authorize Checkpoint B1b2 or Checkpoint B2. Preserve Checkpoint B1a and the protected-reference boundary unchanged. Preserve protected-branch content as out of scope.

Recorded July 16, 2026.

---

## 2A. Checkpoint B1b1 Completion Acceptance

The owner recorded:

> Accept EO-2026-013 Checkpoint B1b1 as complete. Authorize recording, committing, and pushing the Checkpoint B1b1 completion. Do not authorize Checkpoint B1b2 or Checkpoint B2. Preserve Checkpoint B1a and the protected-reference boundary unchanged. Preserve protected-branch content as out of scope.

Recorded July 16, 2026.

The accepted implementation:

- created exactly `tools/atlas/platform/context_compilation/selectors.py` and `tests/test_context_selectors.py`;
- modified exactly the task-context index, context-compilation exports, and immutable models;
- added the exact `SelectorOutput` model, five selector exceptions, and three selector functions;
- enforced strict bytes-only UTF-8, BOM, NUL, Unicode-scalar, bare-CR, and mixed-line-ending boundaries;
- implemented the accepted bounded Engineering Opportunity YAML grammar;
- retained plain accepted scalars as strings and top-level sequences as immutable tuples;
- implemented exact folded and literal block-string behavior;
- emitted exact repository-canonical JSON bytes for requested YAML fields;
- implemented exact ATX Markdown occurrence and section extraction with bounded backtick and tilde fence handling;
- preserved exact Markdown source bytes, whitespace, line endings, blank lines, deeper headings, and terminal-newline state;
- verified the historical EO mapping and four exact historical Markdown sections;
- corrected the mutable module-level `__all__` list to an immutable tuple before final acceptance;
- added 61 focused selector tests and passed 205 total repository tests;
- left Atlas Valid, complete, and Synchronized;
- preserved Checkpoint B1a byte-identically;
- performed no Git, filesystem, network, environment, clock, randomness, digest, policy-reasoning, relationship, selection-plan, budgeting, package, protected-reference, or protected-content behavior; and
- performed no staging, commit, or push before owner acceptance.

Checkpoint B1b2 and Checkpoint B2 remain unauthorized.

Checkpoint B1a and the protected-reference boundary remain unchanged.

Protected-branch content remains out of scope.

---

## 3. Verified Starting State

The decision begins from:

- Branch: `main`.
- HEAD, `origin/main`, and `origin/HEAD`: `e89d765ab7d62c97976091f53ce59dd3f767e4cb`.
- Commit subject: `Complete EO-2026-013 Checkpoint B1a`.
- Working tree: clean.
- Checkpoint A: complete and owner-accepted.
- Checkpoint A.1: complete and owner-accepted.
- Checkpoint B1a: complete and owner-accepted.
- Selection-policy instance: `1.0.1`.
- Budget-policy instance: `1.0.0`.
- Tests: 144 passing at the accepted checkpoint.
- Atlas Validate: Valid.
- Atlas Missing: no missing definitions.
- Atlas Sync: Synchronized.
- EO-2026-013 and all 21 Engineering Opportunities: `reviewed`.
- Protected branch `wip/distinctness-foundation-calibration`: unchanged at `fcbc5957b89fe65a4313a3c23eb814e02a014698`, excluded, and content-out-of-scope.
- Protected-reference behavior: exact ref name and direct object-identity comparison only.

---

## 4. Accepted Revised Sequence

The accepted executable sequence is now:

1. **Checkpoint B1a — Immutable Snapshot Boundary** — complete.
2. **Checkpoint B1b1 — Deterministic Selector Primitives** — authorized.
3. **Checkpoint B1b2 — Bounded Selection Plan** — unauthorized.
4. **Checkpoint B2 — Compilation, Integrity Validation, Explanation, and Golden Replay** — unauthorized.

Only Checkpoint B1b1 is authorized by this decision.

Checkpoint B1b2 requires a separate owner review after B1b1 is complete and accepted.

Checkpoint B2 remains downstream and requires separate owner review after B1b2 is complete and accepted.

---

## 5. Why B1b Was Split

The former single B1b concept combined two independent engineering risk domains:

1. deterministic parsing and transformation of immutable YAML and Markdown bytes;
2. policy-driven reasoning that decides which exact candidates are selected, omitted, or unresolved.

A parser defect changes the facts visible to selection reasoning.

Selector primitives must therefore be independently implemented, verified, and owner-accepted before they become inputs to source-selection decisions.

The split preserves the architecture:

- B1a establishes trusted immutable repository bytes.
- B1b1 transforms exact bytes through exact selectors.
- B1b2 produces the bounded selected, omitted, and unknown plan.
- B2 materializes package records, applies budget, calculates digests, and validates the complete package.

---

## 6. Checkpoint B1b1 Purpose

Checkpoint B1b1 implements the exact pure selector transformations needed by the first historical replay.

It consumes bytes already trusted by B1a.

B1b1 does not decide which sources belong in task context.

It performs no Git access, repository discovery, policy lookup, relationship traversal, source selection, budgeting, hashing, package assembly, network access, or filesystem write.

---

## 7. Exact Implementation Scope

### Create

1. `tools/atlas/platform/context_compilation/selectors.py`
2. `tests/test_context_selectors.py`

### Modify

3. `docs/task-context/index.md`
4. `tools/atlas/platform/context_compilation/__init__.py`
5. `tools/atlas/platform/context_compilation/models.py`

No other path may change.

No dependency file, schema, policy, request fixture, expected-values fixture, snapshot implementation, digest implementation, reasoning module, architecture document, Current Mission record, review, or Engineering Opportunity object may change during B1b1 implementation.

Nothing may be staged, committed, or pushed before owner acceptance of the completed implementation.

---

## 8. Public Model Boundary

B1b1 may add one deeply immutable typed result:

```text
SelectorOutput
```

It carries:

- selector type;
- media type;
- encoding;
- exact selected bytes;
- source line-ending classification;
- immutable transformation metadata.

Raw selected bytes remain bytes and remain outside the canonical JSON model.

A metadata representation may exclude raw content.

`SelectorOutput` is not a package payload.

It must not carry:

- payload ID;
- payload digest;
- source-content digest;
- package source ID;
- package linkage;
- budget measurement;
- consumability;
- validation status.

---

## 9. Public Error and Function Boundary

### Errors

B1b1 may export:

```text
SelectorError
SelectorEncodingError
SelectorSyntaxError
SelectorContractError
SelectorNotFoundError
```

Errors must use stable concise messages and must not expose arbitrary source content.

### Functions

B1b1 may export:

```python
parse_bounded_yaml_mapping(data: bytes)
select_yaml_fields(data: bytes, fields: Sequence[str]) -> SelectorOutput
select_markdown_heading(
    data: bytes,
    heading_text: str,
    occurrence: int,
) -> SelectorOutput
```

The parser result is a deeply immutable top-level string-keyed mapping.

These functions are pure transformations over caller-supplied bytes.

---

## 10. Shared Text Boundary

Both selector families must:

- accept bytes only;
- decode strict UTF-8;
- reject a UTF-8 byte-order mark;
- reject invalid UTF-8;
- reject NUL;
- reject lone Unicode surrogates;
- preserve Unicode scalar values without normalization;
- perform no ambient newline conversion;
- be deterministic and side-effect free.

Line-ending classification is:

- `lf`;
- `crlf`;
- `none` for single-line input with no line ending.

Mixed LF and CRLF input is rejected.

Bare CR input is rejected.

---

## 11. Bounded YAML Contract

The parser is a repository-local, standard-library-only implementation for the historical Engineering Opportunity subset.

It must not be described as a general YAML parser.

### Supported document shape

- one top-level mapping;
- plain top-level keys;
- string scalar values;
- top-level sequences of string scalar values;
- folded block strings using exactly `>`;
- literal block strings using exactly `|`;
- blank lines;
- uniform LF or CRLF source line endings;
- plain, bounded single-quoted, and JSON-compatible double-quoted string forms.

### Scalar behavior

- every accepted plain scalar remains a string;
- no implicit boolean, null, number, date, or timestamp typing;
- Unicode is not normalized;
- comments are not interpreted;
- selected values retain the exact semantics of this bounded parser.

### Block strings

Only bare `>` and `|` indicators are supported.

Chomping and indentation indicators are rejected.

- literal `|` preserves content line breaks as `\n`;
- folded `>` folds eligible single line breaks to spaces and preserves paragraph breaks deterministically;
- clip behavior produces exactly one final `\n`;
- LF versus CRLF source input does not change structured canonical JSON output.

### Sequences

Top-level string sequences use one exact indentation form.

Nested mappings, nested sequences, multiline sequence items, and mixed container values are rejected.

### Rejected features

Reject at minimum:

- duplicate keys;
- tabs;
- directives;
- multiple documents;
- document start and end markers;
- anchors;
- aliases;
- merge keys;
- tags;
- flow mappings;
- flow sequences;
- complex keys;
- nested mappings;
- nested sequences;
- explicit typed tags;
- unsupported block indicators;
- malformed quoted strings;
- unsupported indentation;
- comment or directive syntax outside the bounded model;
- any value outside strings and top-level string sequences.

The implementation must not reuse a permissive opportunity loader as the normative selector parser.

---

## 12. YAML-Field Selection Contract

`select_yaml_fields` must:

- require a non-string sequence of unique nonempty string field names;
- require every requested field to exist;
- treat the field list as the exact inclusion contract;
- construct a mapping containing exactly those fields;
- serialize that mapping through repository-owned RFC 8785 canonical JSON;
- return media type `application/json`;
- return encoding `utf-8`;
- include immutable transformation metadata recording the exact field list;
- perform no source or payload digest calculation.

The exact first-replay fields are:

```text
id
title
status
summary
```

The full bounded parsed mapping must retain `related_documents` for later B1b2 relationship verification even though `related_documents` is not included in this selector output.

---

## 13. Markdown Heading Contract

`select_markdown_heading` must:

- require one exact single-line ATX heading selector;
- require one to six leading `#` characters followed by one space and nonempty text;
- require a positive safe integer occurrence;
- match the exact heading line without case folding, trimming, normalization, or closing-hash reinterpretation;
- count only exact matches outside recognized fenced code blocks;
- include the selected heading line;
- include all following bytes until immediately before the next ATX heading of equal or higher level outside fenced code;
- include deeper-level headings inside the selected section;
- stop at end of file when no terminating heading exists;
- preserve exact source bytes, line endings, blank lines, whitespace, and terminal-newline state;
- return media type `text/markdown`;
- return encoding `utf-8`;
- include immutable transformation metadata recording exact heading and occurrence.

Setext headings, blockquoted headings, list-item headings, indented pseudo-headings, and heading-like content inside fenced code blocks are not section boundaries.

Fenced-code handling may implement only a bounded deterministic backtick and tilde fence model sufficient to prevent false heading matches. It must not claim full CommonMark conformance.

---

## 14. Historical Integration Evidence

B1b1 tests must use B1a immutable blob reads against the accepted historical snapshot to verify:

1. `docs/opportunities/reviewed/EO-2026-013-task-scoped-agent-context-compilation.yaml`
   - exact bounded parse;
   - exact `related_documents` sequence;
   - exact four-field canonical JSON output.

2. `docs/current-mission.md`
   - exact `## Initial Milestone`, occurrence 1.

3. `docs/architecture/repository.md`
   - exact `## Source of Truth Hierarchy`, occurrence 1.

4. `docs/architecture/knowledge-authority.md`
   - exact `### Generated Context`, occurrence 1.

5. `docs/standards/engineering-collaboration.md`
   - exact `## Responsibilities`, occurrence 1.

Historical expected outputs must be independently asserted rather than generated and immediately accepted by the same implementation under test.

The protected branch is not used as selector input.

---

## 15. Test Strategy

Tests must cover at minimum:

### Shared text behavior

- strict UTF-8;
- BOM rejection;
- invalid UTF-8;
- NUL rejection;
- LF;
- CRLF;
- no terminal newline;
- mixed line-ending rejection;
- bare-CR rejection;
- Unicode non-normalization;
- repeated byte-identical output.

### YAML behavior

- historical EO object;
- exact selected canonical JSON;
- exact related-document metadata;
- map-order-independent canonical JSON;
- duplicate keys;
- tabs;
- directives;
- document markers;
- anchors;
- aliases;
- merge keys;
- tags;
- flow collections;
- nested mappings;
- nested sequences;
- malformed indentation;
- malformed quotes;
- unsupported block indicators;
- plain scalar strings for boolean-like, null-like, number-like, and date-like text;
- folded paragraphs;
- literal blocks;
- missing selected fields;
- duplicate requested fields;
- invalid field contracts;
- canonical JSON without BOM or insignificant whitespace.

### Markdown behavior

- all four historical sections;
- exact occurrence;
- equal-level boundary;
- higher-level boundary;
- deeper-heading inclusion;
- end-of-file boundary;
- terminal-newline preservation;
- LF and CRLF byte preservation;
- mixed line-ending rejection;
- heading-like text inside backtick fences;
- heading-like text inside tilde fences;
- malformed and unclosed fences under the bounded contract;
- Setext headings ignored;
- blockquoted, listed, and indented pseudo-headings ignored;
- malformed heading selector;
- absent occurrence;
- Unicode exact matching;
- no whitespace or case normalization.

### Capability boundary

- no Git subprocess in selector code;
- no network;
- no filesystem write;
- no dependency;
- no source or payload digest;
- no package model;
- no selection reasoning;
- no B1b2 or B2 path.

---

## 16. Required Verification

Checkpoint B1b1 must prove:

- exact two-created and three-modified scope;
- no B1b2 or B2 path exists;
- no dependency is added;
- no policy, schema, request, or expected-fixture changes;
- no snapshot or digest changes;
- no canonical architecture change;
- no Engineering Opportunity lifecycle mutation;
- exact bounded YAML behavior;
- exact Markdown heading behavior;
- exact historical selector output;
- deep immutability;
- no Git, network, or write side effect from selector primitives;
- all tests pass;
- Atlas remains Valid, complete, and Synchronized;
- nothing is staged, committed, or pushed before owner acceptance.

Any implementation-discovered ambiguity in YAML folding, fence handling, line endings, or historical output must stop the checkpoint and return for bounded owner review.

---

## 17. Checkpoint B1b1 Explicit Exclusions

Checkpoint B1b1 does not authorize:

- Checkpoint B1b2;
- Checkpoint B2;
- source candidate derivation;
- task-profile dispatch;
- generic policy discovery;
- relationship verification;
- source selection;
- selection reasons or chains;
- stable source IDs;
- omissions;
- unknowns;
- freshness;
- conflicts;
- deduplication;
- sensitivity enforcement;
- budget-tier enforcement;
- source-content digests;
- payload digests;
- package payload records;
- package source records;
- package assembly;
- budget execution;
- integrity validation;
- explanations;
- golden replay;
- Atlas commands;
- protected-reference operations;
- Git access inside selector primitives;
- protected-object content access;
- third-party dependencies.

---

## 18. Planned Checkpoint B1b2 — Unauthorized

Checkpoint B1b2 remains unauthorized and requires a separate owner decision after B1b1 completion.

Its future bounded responsibility is to consume:

- the validated compilation request;
- exact selection policy `example.read-only-architecture-assessment` version `1.0.1`;
- the accepted B1a snapshot and immutable blob interface;
- the accepted B1b1 selector primitives.

The first replay will consider exactly five policy candidates and no discovered candidates.

It will later require a separate owner decision defining exact selected, omitted, unknown, fatal-contract, ordering, deduplication, sensitivity, and budget-tier semantics.

No B1b2 file or behavior is authorized now.

---

## 19. Checkpoint B2 — Unauthorized

Checkpoint B2 remains unauthorized.

It begins only after B1b1 and B1b2 are separately complete and accepted.

---

## 20. Preserved B1a and Protected-Reference Boundary

Checkpoint B1a remains unchanged.

This authorization does not permit:

- changes to snapshot resolution;
- changes to repository identity;
- changes to Git subprocess behavior;
- changes to protected-reference handling;
- protected-object peeling;
- protected history or tree traversal;
- protected blob reads;
- protected content selection;
- protected content exposure;
- protected ref or repository mutation.

Protected-branch content remains entirely out of scope.

---

## 21. Decision Traceability

- Architecture checkpoint: `2de09693ed1c922500477c5ba1c6903513ab4dd3`.
- Checkpoint A completion: `6e0fb536eac8113a2a07547661d5a9b89c0a65b6`.
- Checkpoint A.1 completion: `f0ae21a34d525e6f4ce4c7b50790779e664138c4`.
- Checkpoint B1a authorization: `b7046e6fdd7302e1b5aaada3db0970e35c0f0e6c`.
- Checkpoint B1a completion: `e89d765ab7d62c97976091f53ce59dd3f767e4cb`.
- Checkpoint B1b1 authorization: `de97f3d87cc7a90e404c3cf4ea313e6f12e5410a`.
- Checkpoint B1b1 completion accepted: July 16, 2026.
- Checkpoint B1b1 exact implementation scope: two created and three modified files.
- Focused selector tests: 61 passing.
- Final repository verification: 205 tests passed.
- Historical YAML output: 324 bytes.
- Historical Markdown outputs: 910, 1000, 357, and 503 bytes.
- Final technical verification: Atlas Valid, complete, and Synchronized; independent public-interface, immutable-model, pure-capability, YAML, Markdown, historical-output, scope, B1a-preservation, and mutable-global probes passed.
- Checkpoint B1b2 authorized: No.
- Checkpoint B2 authorized: No.
- Checkpoint B1a changes authorized: No.
- Protected-reference behavior changes authorized: No.
- Protected branch content in scope: No.
- Protected object or content access authorized: No.
- Third-party dependency authorized: No.
- Canonical architecture change authorized: No.
- Engineering Opportunity lifecycle state: `reviewed`.
- Next gate: separate owner authorization, revision, deferral, or rejection of Checkpoint B1b2.

STOP — Preserve Checkpoint B1b1. Do not begin B1b2 or B2 without a separate owner decision.
