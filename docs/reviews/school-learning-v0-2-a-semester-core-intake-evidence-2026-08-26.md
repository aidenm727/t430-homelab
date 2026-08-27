# School Learning v0.2-A Semester Core and Intake Evidence

## Checkpoint

- **Why:** Evolve the proven School Learning v0.1.1 workflow into the
  smallest useful Fall 2026 foundation for durable semester/course context,
  explicit opaque intake, assessments, policies, provenance/conflicts,
  generated views, and manual course-aware AI grounding.
- **Risk tier:** Tier 2 — Material Capability. The candidate changes a
  meaningful local workflow and persisted non-sensitive synthetic state. It
  does not cross a Tier-3 live-data, credential, security/access,
  canonical-authority, destructive-storage, or external-action boundary.
- **Base:** `2888548f182a08aed40b0d3aed1528a5e0dbbfd3`.
- **Candidate identity:** **UNCOMMITTED**. A publication identity does not yet
  exist and must not be guessed, predicted, or synthesized.
- **Authority:** The owner's 2026-08-26 checkpoint instruction authorized the
  exact local implementation and synthetic verification boundary below. On
  2026-08-27, the owner explicitly accepted the exact verified and independently
  reviewed SL2-A candidate, then separately authorized local repository
  finalization and local verification. Staging, commit/ref mutation,
  publication/push, deployment, external integration, and every other external
  write remain **NOT authorized**.
- **Next decision boundary:** Fresh Tier-3 independent read-only review of the
  exact locally finalized uncommitted candidate, followed by owner acceptance
  of that finalization and a separate publication-authority decision.

## Exact Authorized Path Boundary

- `tools/school_learning/core.py`
- `tools/school_learning/cli.py`
- `tools/school_learning/render.py`
- `tools/school_learning/__init__.py`
- `tests/test_school_learning.py`
- `docs/architecture/school-learning.md`
- `docs/architecture/repository.md`
- `docs/docs-map.md`
- `tools/atlas/platform/document_definitions.py`
- `docs/reviews/school-learning-v0-2-a-semester-core-intake-evidence-2026-08-26.md`

Not every authorized path is required to change. Personal course content and
state, canonical current state and mission, generated context, dependencies,
Atlas behavior, network/model actions, live-data access or migration, external
integrations, staging, refs, publication, and deployment remain excluded.

## Preflight

- Branch: `main`.
- HEAD/base: `2888548f182a08aed40b0d3aed1528a5e0dbbfd3`.
- Locally observed tracking divergence: `0` ahead / `0` behind; no fetch or
  network refresh performed.
- Working tree: deliberately dirty with the uncommitted SL2-A candidate; the
  observed paths matched the authorized candidate boundary and nothing was
  staged.
- Atlas Validate: Valid.
- Atlas Sync: Synchronized.
- Atlas Missing: complete.
- Repository Health: Healthy within declared scope.
- Python: `3.10.12`.
- Git: `2.34.1`.
- Bash: `5.1.16`.
- `atlas` and `school` launchers: executable.
- Synthetic `/var/tmp`: writable in the accepted native execution boundary
  after narrowly approved sandbox escalation for those fixtures. No live
  school root was inspected.
- School Learning import smoke: OK.
- Second-correction focused candidate baseline: 100 tests passed. This is startup
  context only and is not final correction evidence.
- Network remains restricted and was neither required nor used. No dependency,
  device, service, mount, credential, or model runtime is required.

## Implementation Summary

- Added strict term-level semester identity, registered-course inventory, and a
  deterministic cross-course Semester Home without moving existing course
  directories.
- Added an additive strict course core for capability tags, authoritative
  sources, structured metadata, assessments, policies, and provenance claims.
- Kept legacy course/topic/session state readable and implemented deliberate,
  atomic, neutral material-manifest migration with rollback and no byte,
  identity, topic, session, or learner-state reinterpretation.
- Expanded opaque byte-copy intake to PDF, Markdown, text, PowerPoint, R
  Markdown, PNG, JPEG, and WebP with explicit kind, lifecycle, date,
  relationships, and optional provenance. Intake does not parse content or
  change learning state.
- Added course-local assessment and policy state with append-preserved sourced
  claims. Distinct active values for one field remain visible and are marked
  conflicted; no silent winner is selected.
- Evolved deterministic HTML-safe Course Home, added Semester Home, retained the
  Guided Study Handoff, and added a topic-independent course handoff with exact
  selected attachment identities and stale-file-safe package replacement.
- Added proportionate CLI commands for semester/course registration, intake,
  assessments, policies, semester render, and course context while retaining
  the legacy `init`, `add-material`, `study`, `record`, and `render` commands.
- Kept production code network/model free and owner data outside Git.

## Initial Independent Review and First Bounded Correction

Fresh independent review disposition was **BOUNDED CORRECTION REQUIRED**. It
reported six blocking findings:

1. `course-context.md` was generated but was not part of the attachments the
   human transfer instructions told the owner to send.
2. Claim conflicts were recomputed only for a newly appended claim, allowing
   contradictory active status combinations and divergent policy aggregates.
3. Omitted assessment and material-update arguments erased durable optional
   metadata.
4. Term-level `generated` and `semester.json` metadata paths collided with
   valid legacy course identifiers of those names.
5. Semester initialization and course registration did not cover all filesystem
   mutations with byte-exact transactional rollback.
6. Assessment type was a closed enum and discarded valid course-specific type
   information.

The owner authorized a bounded correction of this exact uncommitted checkpoint;
no new checkpoint or implementation scope was created. The correction:

- makes `attachments/course-context.md` a required distinguished support
  attachment recorded separately from exact selected material IDs and records,
  with START-HERE and CLI transfer instructions that send every attachment;
- enforces one load-time and mutation-time invariant per claim field, recomputes
  the entire affected active set on append/re-submission/status transition,
  excludes superseded claims from disagreements, and validates the deterministically
  derived policy aggregate;
- uses explicit omitted/value/clear semantics so existing assessment and
  material metadata is preserved field by field, while CLI clear flags and API
  `None`/empty lists provide deliberate clears;
- moves semester-owned state and output into the reserved
  `<term>/.school-learning/` namespace, which is outside the legacy course ID
  grammar and leaves courses named `generated` and `semester.json` untouched;
- validates existing semester state before mutation, tracks only first-time
  artifacts, includes course initialization in registration rollback, removes
  complete new failed workspaces, restores existing non-empty workspaces, and
  snapshots mutable state files as exact original bytes; the second review
  below identified one remaining pre-existing-empty-workspace gap; and
- accepts bounded normalized custom assessment types such as `presentation`
  while retaining known values as documented conveniences.

Focused regressions follow the generated transfer instructions; exercise zero,
exact, and stale attachment sets; validate conflicts and malformed reloads;
verify partial updates and explicit clears; snapshot collision workspaces; and
inject failures before and after state effects across initialization,
registration, migration, writes, and final cross-state validation.

## Second Independent Review and Bounded Correction

The second fresh independent review disposition was **BOUNDED CORRECTION
REQUIRED**. It confirmed closure of five prior blockers: course-context
transfer, the claim-conflict invariant, partial-update preservation, the
reserved semester namespace, and flexible assessment types. It identified two
remaining blocking defects:

1. Registration cleanup for a pre-existing empty course workspace depended on
   `initialize_course()` returning successfully. If that initializer wrote
   course files and directories and then raised, the originally empty
   workspace could remain contaminated.
2. `add_material()` created a `.material.*` byte copy before validating rich
   metadata and course-local topic/assessment references. Rejected intake or
   replacement could therefore leave a duplicate temporary artifact.

The owner authorized a second bounded correction of this exact uncommitted
SL2-A candidate. This was not a new checkpoint and did not expand path,
capability, data, publication, or deployment authority. The correction:

- records course initialization as effectful before invocation, while retaining
  the pre-call distinction between absent, pre-existing empty, and existing
  non-empty workspaces; any post-effect initializer failure now removes a
  newly created workspace or restores a pre-existing empty directory to its
  exact empty state, and existing non-empty rollback remains byte-exact;
- builds and validates the complete proposed material record and all
  course-local references in memory before opening or copying the source;
- begins the one-stream source copy only after deterministic semantic and
  reference validation succeeds, with hashing, byte counting, comparison,
  replacement, manifest persistence, identity verification, rollback, and
  temporary cleanup inside the existing protected transaction; and
- preserves legacy intake, partial-update semantics, exact stored-byte/hash
  identity, non-symlink regular-file checks, confined atomic replacement, and
  rollback-failure reporting.

New focused regressions capture complete term/course snapshots; inject
post-effect initializer failures after realistic `course.json`,
`materials.json`, `topics.json`, and directory creation for both absent and
pre-existing empty course paths; retain the existing non-empty legacy rollback
case; and exercise invalid kind, lifecycle, date, provenance, topic reference,
and assessment reference. Invalid replacement separately proves that stored
bytes, hash, and manifest remain exact, every rejected case proves no
`.material.*` survivor, and successful intake re-proves exact digest, size, and
byte-copy behavior.

## Latest Independent Review and Third Bounded Correction

The latest fresh independent review disposition was **BOUNDED CORRECTION
REQUIRED**. It confirmed that both blockers from the second review were closed:
pre-existing empty course workspaces are restored after post-effect initializer
failure, and invalid intake metadata leaves no temporary byte copy. It also
confirmed that the five earlier blockers remain closed: course-context
transfer, the claim-conflict invariant, partial-update preservation, the
reserved semester namespace, and flexible assessment types.

The review identified one new blocking defect. Directory creation was recorded
in the semester initialization rollback list only after the creation helper
returned. A successful `mkdir` followed by a post-creation validation failure
could therefore leave an untracked data-root component, term directory,
`.school-learning` metadata directory, or `generated` directory and contaminate
retry.

The owner authorized a third bounded correction of this exact uncommitted SL2-A
candidate. This was not a new checkpoint and did not expand path, capability,
data, publication, or deployment authority. The correction:

- adds transaction-aware directory creation that appends an absent path to the
  transaction's created-directory list immediately after `mkdir` succeeds and
  before post-effect symlink/directory validation;
- preserves the exact pre-existing distinction because a `FileExistsError`
  path is validated but never appended;
- applies immediate effect tracking to each newly created data-root chain
  component, the term directory, semester metadata namespace, generated
  directory, and the existing course-initialization transaction stages;
- retains reverse-order rollback, so nested paths are removed deepest-first,
  pre-existing ancestors and siblings are preserved, and any removal failure
  produces a truthful incomplete-rollback `SchoolLearningError`; and
- leaves existing state-file, course-registration, pre-existing-empty-course,
  material-upgrade, atomic-write, path, symlink, digest, and exact-byte rollback
  behavior unchanged.

Focused real-filesystem regressions use only synthetic `/var/tmp` roots. They
inject one-shot failures from the creation helper's own validation path after a
real `mkdir` for a data-root chain component, term directory,
`.school-learning`, and `generated`; compare complete pre/post snapshots;
preserve byte-identical sibling sentinels and pre-existing ancestors/courses;
prove artifact-free successful retry without manual cleanup; verify explicit
deepest-first removal order; report incomplete rollback truthfully; and prove a
pre-existing valid semester does not enter directory creation or tracking.

## Final Independent Review and Owner Candidate Acceptance

Fresh final independent review of the exact corrected SL2-A implementation
candidate returned **ACCEPT**. No blocking findings and no non-blocking material
findings remain. The post-effect semester-directory rollback blocker is closed,
and all seven previously closed material findings remain closed. Review scope
was respected, and the candidate remained byte-for-byte unmodified throughout
review.

On 2026-08-27, the owner explicitly accepted that exact verified SL2-A
candidate. Acceptance establishes neither staging, commit/ref mutation,
publication/push, deployment, live-data migration, nor external-integration
authority.

The latest native local verification supporting the accepted candidate remains:

- Focused School Learning suite: 107 tests passed.
- Full repository suite: 522 tests passed, 1 skipped.
- Python compilation of `core.py`, `cli.py`, and `render.py`: passed.
- Atlas Validate: Valid; Missing: complete; Sync: Synchronized.
- `git diff --check`: passed.

## Tier-3 Repository-Finalization Checkpoint Brief

- **Why:** Finalize truthful local lifecycle and canonical active-state records
  for the owner-accepted SL2-A candidate without changing School Learning
  product behavior.
- **Risk tier:** Tier 3 — High Consequence, triggered by canonical active-state
  semantics. This is separate from the accepted Tier-2 SL2-A implementation.
- **Exact scope:** Narrow lifecycle updates to `docs/current-state.json`,
  `docs/current-mission.md`, this compound evidence record, `docs/docs-map.md`,
  and `tests/test_public_surface.py`; regenerate `docs/aiden-context.md` through
  `tools/generate-context.py`. The generator may rewrite
  `docs/infrastructure-snapshot.md`, which must remain content-identical and
  absent from the final diff.
- **Exclusions:** New School Learning behavior, frozen accepted substantive
  paths, SL2-B, schema or Atlas behavior changes, dependencies, staging,
  commit/ref mutation, network access, fetch/pull/push, publication, deployment,
  live School Learning data, migration, external integrations, and all external
  writes.
- **Authority established:** The owner explicitly established local
  repository-finalization and local-verification authority on 2026-08-27 for
  this exact boundary. Owner acceptance of the Tier-2 implementation is
  established. Staging, commit, publication/push, and deployment authority are
  not established.
- **Protected boundaries:** Secrets and protected references remain unread;
  private/live School Learning data and live systems remain untouched;
  generated ownership is preserved; unrelated user changes are excluded; and
  the seven accepted substantive paths remain byte-exact to the hashes below.
- **Observable result:** Canonical state remains intentionally idle with no
  selected implementation checkpoint and truthfully records the pending owner
  decision on SL2-A publication authority; SL2-A remains owner-accepted but not
  published.
- **Verification:** Run focused public-surface and School Learning suites, then
  the complete repository suite after the last mutation; run Atlas Validate,
  Missing, Sync, Review, and Next; inspect complete diff/status, staged state,
  branch/HEAD, generator result, and frozen hashes. Exact post-finalization
  results are returned to the owner after the last mutation rather than added
  through a self-referential evidence-update loop. Fresh Tier-3 independent
  review remains required.
- **Stop conditions:** Stop on any identity/status or unrelated-path drift,
  frozen-byte change, scope expansion, schema/Atlas behavior requirement,
  invented commit identity, unexpected infrastructure-snapshot change,
  material out-of-scope verification failure, or need for staging, commit,
  network, external integration, publication, or deployment.
- **Next decision boundary:** Fresh Tier-3 independent read-only review of this
  exact locally finalized uncommitted candidate, then owner finalization
  acceptance and a separate decision on staging, local commit, and publication.

## Accepted Implementation SHA-256 Freeze

The accepted substantive implementation boundary was hashed before repository
finalization and must remain byte-exact throughout it:

- `tools/school_learning/core.py` — `2f9a7da0b2fbc3706baf9d0018632b4b7395580f2e51f2d21bb1acc65d40a268`
- `tools/school_learning/cli.py` — `ed34185fc8bec0761fc2a26d6aab4fc0e4a1b7ad7aa91e3d5f9eb95a0fac06f6`
- `tools/school_learning/render.py` — `0fb5cbb3406e0d5da698e9371d4f550bf3f14c08629577cad2315cd09317fc2d`
- `tools/school_learning/__init__.py` — `3d10b013e233be68aae523ac48cff64d6d70395d9fb558516b82eafac5513793`
- `tests/test_school_learning.py` — `e46dc2391012d6a294d143664cd12dd005b33125efd8d16f5c1eedcd25546915`
- `docs/architecture/school-learning.md` — `7711e5b44b4708337e9d7637ccfca9440539c69447593cc01e9807b3d41ef682`
- `tools/atlas/platform/document_definitions.py` — `55e965ff6323244b2a0217a878664ed3f0ac52bc50566221dd4e448138c42411`

## Changed Paths

- `docs/architecture/school-learning.md`
- `docs/docs-map.md`
- `docs/reviews/school-learning-v0-2-a-semester-core-intake-evidence-2026-08-26.md`
- `tests/test_school_learning.py`
- `tools/atlas/platform/document_definitions.py`
- `tools/school_learning/__init__.py`
- `tools/school_learning/cli.py`
- `tools/school_learning/core.py`
- `tools/school_learning/render.py`

`docs/architecture/repository.md` required no change: its existing canonical
engineering-state versus external personal-school-state boundary already
covers SL2-A.

## Verification After First Bounded Correction

Post-correction checks completed before this evidence record was finalized:

- Focused School Learning suite: 100 tests passed.
- Full repository suite: 515 tests passed, 1 skipped.
- Python compilation of `core.py`, `cli.py`, and `render.py`: passed.
- Atlas Validate: Valid.
- Atlas Missing: complete.
- Atlas Sync: Synchronized.
- `git diff --check`: passed.
- Changed-path inspection: confined to the authorized boundary.

The exact post-record candidate is rerun through the checkpoint's full final
sequence after this record is frozen. That rerun, the complete diff inspection,
exact Git status, and Atlas outcomes are reported in the owner-facing completion
handoff; any material failure prevents completion.

## Verification After Second Bounded Correction

Second-correction checks completed before this evidence record was finalized:

- Focused School Learning suite: 103 tests passed.
- Full repository suite: 518 tests passed, 1 skipped.
- Python compilation of `core.py`, `cli.py`, and `render.py`: passed, with
  compilation artifacts redirected to the synthetic `/var/tmp` root.
- Atlas Validate: Valid.
- Atlas Missing: complete.
- Atlas Sync: Synchronized.
- `git diff --check`: passed.
- Changed-path inspection remained confined to the authorized boundary.

The exact post-record candidate is rerun through the complete required final
sequence after this record is frozen. The complete final diff, untracked
evidence record, and exact status are then inspected against the authorized
boundary. Any later mutation invalidates that run as final evidence.

## Verification After Third Bounded Correction

Third-correction checks completed before this evidence record was finalized:

- Focused School Learning suite: 107 tests passed.
- Full repository suite: 522 tests passed, 1 skipped.
- Python compilation of `core.py`, `cli.py`, and `render.py`: passed, with
  compilation artifacts redirected to the synthetic `/var/tmp` root.
- Atlas Validate: Valid.
- Atlas Missing: complete.
- Atlas Sync: Synchronized.
- `git diff --check`: passed.
- Changed-path inspection remained confined to the authorized boundary.

The exact post-record candidate is rerun through the complete required final
sequence after this record is frozen. The complete tracked diff, complete
untracked evidence record, exact changed-path boundary, staged state, branch,
and HEAD are then inspected. Any later mutation invalidates that run as final
evidence.

## Remaining Limitations

- SL2-B adaptive learner dimensions, automatic mastery/readiness inference,
  and AI-policy routing are not implemented.
- No OCR, content parsing/classification, embeddings, vector/graph store,
  provider/model call, automatic AI-response ingestion, LMS/Canvas, Calendar,
  email, schedule recommendation, notification, publication, or deployment is
  included.
- Semester Home derives only from stored course state and knows nothing about
  available time, work/life constraints, or external calendars.
- The checkpoint proves migration and behavior only on synthetic `/var/tmp`
  workspaces; owner live school data was not accessed or migrated.

## Lifecycle Gates

- Initial independent review: **BOUNDED CORRECTION REQUIRED**.
- First bounded correction: **performed and locally verified**.
- Second fresh independent review: **BOUNDED CORRECTION REQUIRED**; five prior
  blockers closed and two remaining failure-safety blockers identified.
- Second bounded correction: **performed and locally verified**.
- Latest fresh independent review: **BOUNDED CORRECTION REQUIRED**; both
  second-review blockers closed, all five earlier blockers remain closed, and
  one post-effect semester-directory tracking blocker identified.
- Third bounded correction: **performed and locally verified**.
- Fresh final independent review of the exact corrected uncommitted
  implementation candidate: **ACCEPT**; no blocking or non-blocking material
  findings remain, all correction cycles are closed, and scope was respected.
- Owner candidate acceptance: **explicitly established on 2026-08-27** for the
  exact verified and reviewed SL2-A candidate.
- Repository-finalization authority: **explicitly established** for local
  finalization and local verification.
- Finalization independent review: **pending**.
- Finalization owner acceptance: **pending**.
- Staging authority: **NOT established**.
- Commit authority: **NOT established**.
- Publication/push authority: **NOT established**.
- Deployment authority: **NOT established**.
- Candidate publication identity: **does not yet exist and must not be
  guessed**.
- Candidate state: **UNCOMMITTED**.
