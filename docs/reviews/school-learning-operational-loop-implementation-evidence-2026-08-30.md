# School Learning Operational Loop Implementation Evidence

## Accepted Checkpoint Brief

- **Why:** Replace the prose-heavy course-chat return path and many manual
  mutations with a reviewed data-only candidate, deterministic preview,
  explicit owner confirmation, one bounded atomic apply, durable source-check
  evidence, and a compact derived semester planning view.
- **Risk tier:** Tier 2 — Material Capability. The checkpoint changes a
  meaningful owner workflow, persisted non-sensitive School Learning state,
  CLI behavior, generated views, and the course-chat/local-runtime contract. It
  does not cross a Tier-3 live-data, credential, protected-reference,
  destructive, migration, recovery, authority-semantics, or external-action
  boundary.
- **Exact scope:** Implement first-class per-course source observations and
  narrow source upsert; the exact reviewed-update preview/apply return path;
  the required course-handoff update contract; the explicit-as-of Semester
  Plan; focused synthetic coverage; this architecture update; and this one
  compound evidence record. Repository mutations are limited to the seven
  paths listed below. Product verification uses synthetic `/var/tmp` roots.
- **Exclusions:** Canvas/LMS, Gmail/email, Calendar, credentials, secrets,
  network/model invocation, live Fall 2026 data, automatic AI writes, SL2-B,
  mastery inference, planner confidence, class-calendar modeling, raw material
  intake through reviewed updates, audio, assessment-status history, claim
  taxonomy redesign, live migration, arbitrary commands/paths/writes,
  dependencies/configuration, generated repository-owned context, Git metadata
  writes, publication, deployment, and every external write.
- **Authority established:** The owner's 2026-08-30 instruction explicitly
  accepted the design and authorized implementation of this exact checkpoint,
  these exact repository paths, and narrow interactive approval requests only
  for synthetic School Learning `/var/tmp` fixture and test operations. It did
  not authorize final-candidate acceptance, staging, commit/ref mutation,
  fetching/pulling, push/publication, deployment, live service access,
  dependency/configuration changes, or another external write.
- **Protected boundaries:** No secret or credential values, protected
  references, private/live owner course data, live systems, network, generated
  repository artifacts, or unrelated user changes may be read or changed.
  Course material identity, provenance/conflict behavior, learner state,
  symlink/path confinement, strict schemas, deterministic output, and rollback
  guarantees remain protected.
- **Observable result:** The owner can record explicit source checks, maintain
  one source descriptor, transfer a course context plus exact update contract,
  preview a bounded candidate without mutation, confirm and atomically apply
  that exact candidate, and render an explicit-as-of semester plan from durable
  state without guessing unresolved dates.
- **Verification:** Run the focused School Learning module, the full native
  Python suite, Atlas validate/missing/sync/review/next, Git hygiene, complete
  diff inspection, changed-path validation, and a final scope/external-action
  audit. One fresh independent Tier-2 review of the exact final candidate is
  required after this implementation run.
- **Stop conditions:** Stop on any required out-of-scope path or capability,
  live-data/migration/integration need, inability to guarantee reviewed-update
  rollback, arbitrary execution/path requirement, date guessing, Tier-3
  boundary, unrelated unpreservable change, architecture decision, repeated
  failure without new evidence, or `/var/tmp` need beyond the authorized
  synthetic-test boundary. No stop condition was reached during implementation.
- **Next decision boundary:** Fresh independent Tier-2 review of the exact
  implemented-and-verified candidate, finding disposition if needed, then
  explicit owner acceptance or rejection. Staging, commit, publication, and
  deployment remain separate later decisions.

## Base and Preflight

- Preflight observation time: `2026-08-30T18:11:50,386168035-04:00`.
- Resolved repository root: `<repository-root>` (the exact local absolute path
  was observed during preflight but is intentionally not preserved in this
  public evidence record).
- Starting branch: `main`.
- Starting HEAD/base: `73fb72237a172f1bf64a80c15e7357651c274b59`
  (`SL2-A: finalize published lifecycle`).
- Locally observed upstream: `origin/main`; local-only divergence: `0` ahead /
  `0` behind. No fetch or other network refresh was performed.
- Starting working tree: clean; staged, unstaged, untracked, name-status, and
  `git diff --check` observations were empty/clean.
- Atlas bootstrap/state/validate/missing/sync/review/next: repository healthy
  within declared scope, canonical state valid, generated ownership
  synchronized, no missing definitions, work selection intentionally idle.
  That repository state granted no authority and did not contradict the
  explicit owner-selected external checkpoint.
- Canonical state and mission were read and remained outside the writable path
  set. School Learning architecture, engineering-session architecture,
  collaboration standard, repository/knowledge authority, core, CLI, render,
  public boundary, and focused tests were inspected before mutation.
- Python: `3.10.12`; Git: `2.34.1`; `python3`, `git`, `./atlas`, and `./school`
  resolved locally.
- Every authorized repository target was writable. The task-specific
  `/var/tmp/aiden-school-learning-tier2-preflight-20260830` directory was
  created through narrow interactive approval, an exact write probe succeeded,
  and an existing focused synthetic School Learning test passed. Product
  verification used only synthetic `/var/tmp` roots. The exact probe and empty
  task-specific preflight directory were removed before final verification.
- Network remained unused/restricted. No dependency, configuration, credential,
  device, mount, external service, or live owner-data access was required.

## Exact Authorized Repository Paths

- `tools/school_learning/core.py`
- `tools/school_learning/cli.py`
- `tools/school_learning/render.py`
- `tools/school_learning/__init__.py`
- `tests/test_school_learning.py`
- `docs/architecture/school-learning.md`
- `docs/reviews/school-learning-operational-loop-implementation-evidence-2026-08-30.md`

No other repository path was authorized or changed.

## Implementation Summary

- Added optional exact-schema `source-observations.json`, missing-file neutral
  semantics, append-only validated observations, registered-source and
  course-local material references, derived latest coverage, and a narrow
  source-descriptor upsert that preserves unrelated course profile state.
- Added exact `aiden.school.reviewed-update/v0.1` validation with four operation
  kinds, canonical planner-critical claim values, flexible generic claims,
  canonical semantic digest, strict course-context base identity, deterministic
  in-memory preview/diff, zero preview mutation, explicit digest confirmation,
  stale revalidation, ordered simulation, and complete multi-file rollback to
  exact prior bytes/existence.
- Bumped the course-handoff manifest to its bounded v0.3 contract and made
  exact source-observation context plus `update-contract.json` required,
  distinguished, digest-verified attachments. The prompt preserves
  provenance/conflicts and states that a returned candidate never updates local
  state.
- Added derived `.school-learning/generated/semester-plan.md` with explicit
  `--as-of`, active due horizons, submitted/graded/reviewed exclusion, dated
  preparation material, assessment availability windows, per-source
  observations, unresolved near-term conflicts, concise longer-horizon
  summaries, and a small explicit legacy date parser. Unsupported scheduling
  prose is displayed, never guessed.
- Retained Semester Home as the complete audit-oriented inventory; preserved
  v0.1/v0.2 missing-observation compatibility, learner-state isolation, opaque
  materials, conflict semantics, deterministic output, confinement, and
  hardened publication behavior.

## Original Implementation-Run Verification Observations

The following actual native observations cover the original implementation and
architecture increments before the fresh independent Tier-2 review. They are
historical candidate evidence and do not substitute for final post-freeze
verification of the current exact candidate.

- Command-start readiness:
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
  tests.test_school_learning.SemesterCoreTests.test_semester_initialization_is_strict_and_course_identity_is_consistent`
  — 1 test passed.
- Coherent operational-loop increment:
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
  tests.test_school_learning.SemesterCoreTests` — 41 tests passed.
- Complete focused module after the core implementation: 115 tests passed;
  after final CLI/coverage additions, the same command passed 116 tests:
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
  tests.test_school_learning`.
- Full Python suite:
  `PYTHONPATH=tools PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s
  tests -p 'test_*.py'` — 531 tests passed, 1 skipped.
- Atlas: `./atlas validate` Valid; `./atlas missing` complete; `./atlas sync`
  Synchronized; `./atlas review` healthy within declared scope with the expected
  authorized dirty tree; `./atlas next` continued to report intentional idle
  because Atlas does not establish the owner's external authority.
- Git hygiene: `git diff --check` passed; `git diff --cached --name-status` was
  empty; the unstaged changed-path list contained only the six then-existing
  authorized product/test/architecture paths. This evidence record becomes the
  seventh authorized path.

Complete diff inspection then produced one ordinary in-scope final correction:
the generated update contract now enumerates exact candidate root keys and
identifier/null rules; apply performs an additional candidate and context
staleness check immediately before persistence; candidate file reads detect
identity changes during open/read; and structured near-term `available-at` /
`available-until` claims are visible as assessment availability boundaries.
The focused and broad observations that followed belong to that historical
candidate and are not final evidence for the current corrected tree.

One focused run then executed all 116 tests and exposed one
test-only assertion defect: an assertion intended to prove that CS3240 had no
Aug 31 due assessment also matched the newly visible Aug 31 availability
boundary. The product output correctly distinguished `AVAILABLE` from due
work. The assertion was narrowed to the due sections; no product behavior or
checkpoint boundary changed, and verification restarted.

The following full-suite run then exposed two public-surface assertions caused
by preserving the local absolute checkout path in this record: that path
contained a protected historical repository-identity literal and matched the
historical-absolute-path gate. The repository-wide public-surface contract was
outside the writable set and required no change. This authorized record now
preserves the observation as `<repository-root>` without publishing the local
absolute path; product behavior was unchanged and verification restarted.

## Negative and Compatibility Coverage

- Missing, valid, duplicate, malformed, invalid-enum/date, unknown-source, and
  unknown-material observation paths; reviewed base-state and same-candidate
  observation-ID collisions; two distinct new reviewed observation IDs; exact
  learner-state non-mutation.
- Source upsert preservation, validation, sorted uniqueness, and no unrelated
  profile reconstruction.
- Candidate root/operation exactness; unsupported/arbitrary operation data;
  wrong term/course; unknown references; canonical planner dates; flexible
  generic claims; preserved conflict semantics; zero-mutation preview;
  base/digest/candidate staleness; ordered source-upsert plus observation;
  successful multi-operation apply; and confirmation mismatch.
- Injected post-persistence failure across `course-core.json` and
  `source-observations.json`, exact old-byte restoration, and removal of a new
  observation file on rollback.
- Required context/contract manifest records, exact base hash, observation
  context, update-contract tampering rejection, stale-package preservation, and
  unchanged selected-material identity guarantees.
- Explicit as-of parsing; repeat determinism; due-today/three-day/seven-day
  grouping; submitted exclusion; Eco-style reading/listening; snapshot
  exclusion; source coverage states; single/equal/differing/superseded due-family
  handling; same-field and mixed-alias supported/unsupported conflicts with
  complete provenance; all-unsupported isolation; canonical timestamps with
  0, 1, 3, and 6 fractional digits; 7-digit and structurally incomplete
  rejection; equal and differing fractional-instant semantics; both accepted
  legacy timestamp shapes; and concise DSA-style longer-horizon summary.
- An independent literal matrix covers every material generated update-contract
  constraint, including exact keys, identity, bounds, formats, statuses,
  canonical relationships, claim semantics, cross-references, both
  source-observation ID novelty scopes, and the exact 1-through-6-digit
  fractional timestamp grammar.
- Existing v0.1/v0.2, material identity, handoff publication, rollback,
  symlink/path confinement, exact state validation, and SL2-A behavior remained
  covered by the complete 116-test focused module. No live-data migration is
  required.

## Independent Review Findings and Correction Disposition

A fresh independent Tier-2 review of the original uncommitted seven-path
candidate completed after the original implementation verification. It reported
five findings. This correction pass remained within the accepted checkpoint,
paths, operations, architecture, data boundary, dependencies, observable
result, and stop conditions.

1. **Base-context / semantic-state identity — corrected.** The exact
   deterministic `course-context.md` identity now includes the complete
   `course-core.json` semantic state, including `created_at` and `updated_at`,
   while retaining course, material, topic, source-observation, profile,
   assessment, and policy grounding. Preview and apply use the same identity;
   apply reloads, recomputes, rejects mismatch, and re-simulates immediately
   before persistence. A timestamp-only same-value source update now changes
   the identity and invalidates the old preview.
2. **Mixed `due` / `due-at` silent winner — corrected.** Reviewed candidates
   reject legacy `due` claims and require normalized forward scheduling through
   `due-at`. The planner treats supported active `due` and `due-at` claims as
   one semantic family, ignores superseded claims, ranks one agreed meaning,
   preserves complete provenance for mixed conflicts, and leaves unsupported
   legacy values unstructured. Existing ordinary claim-status behavior remains
   available to supersede legacy claims; no migration was added.
3. **Incomplete update contract — corrected.** `update-contract.json` now
   carries a deterministic self-contained constraint map for exact root and
   operation keys, constants and identity, identifier and assessment-type
   grammars, nonempty/plain/nullable strings, strict date/timestamp forms,
   operation and claim bounds, policy `rule`, status enums, canonical
   relationships, cross-reference rules, planner fields, and candidate file
   limits.
4. **Canonical relationship/timestamp forms — corrected.** Reviewed source-
   observation relationships must arrive sorted and unique rather than being
   repaired before digesting. One strict RFC3339 parser now requires seconds
   and an explicit `Z` or numeric offset for reviewed planner values and the
   corresponding planner interpretation path.
5. **Final verification durability — corrected by the current freeze model.**
   The earlier result-only repository attestation was rejected by the subsequent
   independent review because writing results after a run still mutates the
   candidate. This record now defines the complete final gate before freeze and
   intentionally contains no result values for that later run. Final post-freeze
   results are preserved only in the owner-facing handoff.

The fresh post-correction independent Tier-2 review then reported two material
findings and one minor finding. All three corrections remained ordinary and
in-scope:

1. **Supported plus unsupported active due claims — corrected.** The planner
   now considers the complete active `due` / `due-at` family and permits a
   ranked value only when every active member is supported and every interpreted
   meaning agrees. A supported/unsupported mixture produces no winner, exposes
   the complete active set with source and observation provenance as a planning
   conflict, and separately exposes each unsupported value without guessing.
   All-unsupported and singleton-unsupported sets remain unstructured; equal
   supported aliases, differing supported aliases, singleton-supported values,
   and superseded legacy behavior retain their accepted semantics.
2. **Final verification/evidence self-reference — corrected.** Every evidence
   edit completes before the seven paths freeze. The required focused, full,
   Atlas, Git-hygiene, and read-only inspection sequence follows that freeze,
   no candidate path may change afterward, and exact results are reported only
   in the owner-facing handoff. Recording those values here afterward would
   itself invalidate their post-last-mutation status.
3. **Update-contract test independence — corrected.** A literal expected
   constraint matrix now independently locks root identity and bounds,
   identifier/string/null rules, date/timestamp forms, every operation shape and
   status, relationship canonicalization, claim identity/scheduling rules, and
   course-local cross-reference requirements. It does not derive expectations
   from the contract generator or its self-validator.

The final fresh independent Tier-2 review of that candidate then reported two
remaining material contract/runtime mismatches. Both corrections remained
ordinary and inside the same accepted checkpoint and seven-path boundary:

1. **M1 — source-observation ID novelty omission — corrected.** Ordered runtime
   simulation already rejected an observation ID present in the base course
   source-observation state or introduced by an earlier source-observation
   operation in the same candidate, but `update-contract.json` described only
   identifier syntax. The self-contained contract now marks the ID as an
   append-only identity, forbids overwrite/reuse, names
   `source_observations[*].id` as its existing-state uniqueness scope, and
   names `prior source-observation operations[*].id` as its ordered-candidate
   uniqueness scope. Independent literal contract expectations and behavioral
   regressions cover a base-state collision, a repeated same-candidate ID, and
   two distinct successful new IDs.
2. **M2 — fractional timestamp grammar mismatch — corrected.** The former
   contract regex admitted arbitrary nonempty fractional precision while
   runtime acceptance depended on Python 3.10 `datetime.fromisoformat`
   behavior. School Learning now defines one explicit canonical timestamp
   subset: date and time through seconds plus `Z` or numeric `+/-HH:MM`
   timezone are required; fractional seconds are optional and, when present,
   contain exactly 1 through 6 digits. Seven or more digits are rejected
   without truncation. One explicit component parser validates the shared
   grammar before constructing a timezone-aware `datetime`, right-pads shorter
   fractions for microsecond representation, and drives reviewed planner
   values, observed timestamps, contract constraints, semester planning, and
   due-family comparison. Candidate and planner regressions cover 0/1/3/6
   digits, `Z` and numeric offsets, 7-digit/seconds/timezone/offset rejection,
   equality of `.1` and `.100000`, and disagreement/no-winner behavior for
   `.1` versus `.100001`.

All earlier review findings and correction dispositions above remain in force.
The production generator/self-validator is not the sole source of either new
expectation: the independent literal contract matrix locks the exact bounded
timestamp pattern and both observation-ID novelty scopes.

The latest fresh independent Tier-2 review then reported one remaining material
finding. Its correction remained ordinary and inside the same accepted
checkpoint and seven-path boundary:

1. **M3 — lexical source-observation recency — corrected.** Semester Plan
   source coverage formerly selected the latest matching observation by the raw
   `observed_at` string and then ID. It now uses one semantic recency key: the
   shared explicit School Learning timestamp parser normalizes canonical
   timestamps to comparable UTC instants, and observation ID breaks a tie only
   after semantic instant equality. Fractional spellings such as `.1Z` and
   `.100000Z`, and equivalent numeric-offset spellings, therefore compare
   equally; `.100001Z` remains later than `.1Z`. For source-coverage ordering
   only, a date-only observation uses the UTC start-of-day sentinel for that
   date. This convention makes `2026-09-01` equal for ordering to
   `2026-09-01T00:00:00Z`, later than `2026-08-31T23:59:59Z`, and earlier than
   `2026-09-01T00:00:01Z`; it is not evidence that the observation occurred at
   midnight and adds no local-time inference. The focused regression uses
   visibly distinct IDs, outcomes, and scopes to cover fractional equality and
   difference, offset equality and UTC-order difference, all three date-only
   boundaries, and the outcome/scope selected from the semantically latest
   observation. Persisted observation validation remains unchanged and fails
   closed before planning.

All previous material and minor findings remain dispositioned as recorded
above. The exact final verification commands and freeze sequencing below remain
unchanged: this record completes before candidate freeze, final post-freeze
values remain owner-facing rather than being written back afterward, a fresh
independent review remains pending, owner acceptance remains pending, and
staging, commit, publication, and deployment remain unauthorized.

## Pre-Freeze Candidate Checks (Not Final)

These checks preceded this evidence-record mutation and therefore are useful
candidate checks, not final post-last-mutation evidence:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
  tests.test_school_learning` — 118 tests passed.
- `PYTHONPATH=tools PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s
  tests -p 'test_*.py'` — 533 tests passed, 1 skipped.
- The 44-test `SemesterCoreTests` candidate check first exposed one expected-
  output mismatch after pure `due-at` conflicts were labeled as mixed aliases.
  The label was narrowed without changing no-winner behavior; both affected
  planner regressions then passed before the complete focused and full checks
  above.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
  tests.test_school_learning.SemesterCoreTests.test_semester_plan_treats_due_and_due_at_as_one_semantic_family
  tests.test_school_learning.SemesterCoreTests.test_course_handoff_update_contract_has_complete_independent_constraint_matrix`
  — 2 tests passed during the current correction; this is not the final frozen
  candidate run.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
  tests.test_school_learning.SemesterCoreTests.test_reviewed_source_observation_ids_are_novel_append_only_identities
  tests.test_school_learning.SemesterCoreTests.test_reviewed_candidate_uses_canonical_school_timestamp_subset
  tests.test_school_learning.SemesterCoreTests.test_semester_plan_uses_canonical_timestamp_subset_and_fractional_instants
  tests.test_school_learning.SemesterCoreTests.test_course_handoff_update_contract_has_complete_independent_constraint_matrix`
  — 4 tests passed after the M1/M2 corrections; this remains a pre-freeze
  candidate check rather than final evidence.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
  tests.test_school_learning.SemesterCoreTests.test_semester_plan_source_coverage_uses_semantic_observation_recency`
  — 1 test passed after the M3 correction; this remains a pre-freeze candidate
  check rather than final evidence.

## Required Final Freeze and Verification Commands

Before freeze, run the Git boundary checks below, inspect the complete tracked
diff, inspect this complete untracked evidence record, and confirm that the
exact changed-path set is the seven authorized paths with nothing staged:

```text
git diff --check
git diff --name-status
git diff --cached --name-status
git status --short --branch
git diff -- tools/school_learning/core.py tools/school_learning/cli.py tools/school_learning/render.py tools/school_learning/__init__.py tests/test_school_learning.py docs/architecture/school-learning.md
sed -n '1,999p' docs/reviews/school-learning-operational-loop-implementation-evidence-2026-08-30.md
```

After that inspection, freeze all seven candidate paths. Run this complete final
gate after the freeze and make no later repository mutation:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_school_learning

PYTHONPATH=tools PYTHONDONTWRITEBYTECODE=1 \
python3 -m unittest discover -s tests -p 'test_*.py'

PYTHONDONTWRITEBYTECODE=1 ./atlas validate
PYTHONDONTWRITEBYTECODE=1 ./atlas missing
PYTHONDONTWRITEBYTECODE=1 ./atlas sync
PYTHONDONTWRITEBYTECODE=1 ./atlas review
PYTHONDONTWRITEBYTECODE=1 ./atlas next

git diff --check
git diff --name-status
git diff --cached --name-status
git status --short --branch
git branch --show-current
git rev-parse HEAD
```

Final post-freeze verification results are reported in the owner-facing handoff
because recording those results into this repository record afterward would
itself mutate the exact candidate and invalidate their post-last-mutation
status. This evidence record remains unchanged after the freeze and does not
invent final result values.

If final external results must later become repository-owned under the compound
evidence standard, that is a later publication/lifecycle sequencing concern
requiring its own explicit authorization. It is not performed in this
correction pass.

## Final Candidate Boundary and Lifecycle Status

Final expected changed-path list for this implementation candidate:

- `docs/architecture/school-learning.md`
- `docs/reviews/school-learning-operational-loop-implementation-evidence-2026-08-30.md`
- `tests/test_school_learning.py`
- `tools/school_learning/__init__.py`
- `tools/school_learning/cli.py`
- `tools/school_learning/core.py`
- `tools/school_learning/render.py`

- Fresh independent Tier-2 review of the original candidate: **completed with
  five findings; correction disposition above**.
- Fresh post-correction independent Tier-2 review: **completed with two material
  findings and one minor finding; all are corrected above**.
- Final pre-this-correction independent Tier-2 review: **completed with the M1
  and M2 material findings; both are corrected above**.
- Latest pre-current-correction independent Tier-2 review: **completed with the
  M3 material finding; it is corrected above**.
- New fresh independent Tier-2 review of the exact frozen candidate:
  **pending**.
- Owner acceptance of the exact final candidate: **pending**.
- Candidate state: uncommitted implementation candidate based on
  `73fb72237a172f1bf64a80c15e7357651c274b59`; no future commit identity is
  claimed.
- Staging, commit/ref mutation, fetching/pulling, push/publication, deployment,
  dependency/configuration changes, external writes, network access, and live
  School Learning data access: **not authorized and not performed**.
