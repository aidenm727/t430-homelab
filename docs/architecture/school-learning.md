# School Learning Architecture

## Purpose

School Learning is an owner-controlled, semester-aware local workflow for
durable course context, opaque material intake, grounded manual AI assistance,
and owner-reviewed learning state. Repository code and architecture are
engineering state; personal course content and runtime state remain outside Git
under the owner's selected data root.

## Proven Baseline and Operational-Loop Evolution

v0.1.1 proved the bounded course loop: initialize a course, copy PDF/Markdown/
text materials with exact identity, select a topic, prepare a Guided Study
Handoff, manually use an approved AI interface, record an owner-reviewed result,
and render Course Home and Review.

v0.2 SL2-A adds the smallest Fall 2026 semester foundation around that loop:

```text
Initialize semester
  -> Register/configure course profile
  -> Intake opaque materials with explicit metadata
  -> Register assessments and sourced policies/claims
  -> Render Course Home and Semester Home
  -> Prepare course context or the existing Guided Study Handoff
  -> Manually use an approved AI consumer
```

The Tier-2 School Learning Operational Loop extends that foundation without
changing the learner-state boundary:

```text
Existing material intake and durable course evidence
  -> manual course-chat interpretation
  -> structured reviewed candidate
  -> deterministic local preview
  -> explicit owner digest confirmation
  -> one bounded atomic apply
  -> durable academic and operational state
  -> derived semester planning projection
```

It does not add adaptive learner dimensions, model invocation, automatic AI
writes, raw material intake through reviewed updates, or an external
integration.

## Truth Boundaries

School Learning keeps four state/view categories distinct:

- **Academic state** is explicit stored course identity, source descriptors,
  materials, assessments, policies, dates, and provenance claims. Conflicting
  consequential claims remain side by side with their status and source.
- **Learner state** is owner-reviewed topic and session state. The retained
  statuses are `unseen`, `learning`, `review`, and `solid`; retained outcomes are
  `correct`, `partial`, and `incorrect`. Intake, source observations, reviewed
  candidates, and planning renders never infer or change learner state.
- **Operational source observation** records which registered course source
  surface was checked, when, whether the check was full or partial, its bounded
  outcome, and any explicitly related material. It is evidence about a check,
  not academic or learner truth.
- **Derived planning projection** is a temporary deterministic "what matters
  now?" view over durable state for an explicit as-of date. It is never
  canonical state and never chooses a winner from conflicting claims.

Workflow integrity remains an independent implementation boundary: confined
paths, SHA-256 identities, byte counts, generated packages, exact validation,
and atomic persistence protect all four categories.

No one truth category silently creates another. In particular, a file upload,
assessment deadline, or AI response cannot establish mastery.

## Ownership and Physical Layout

The default root is
`${AIDEN_SCHOOL_DATA_ROOT:-~/.local/share/aiden-platform/school}` and must remain
outside this repository and every Git worktree.

```text
<data-root>/<term>/
├── .school-learning/
│   ├── semester.json
│   └── generated/
│       ├── semester-home.md
│       └── semester-plan.md
└── <course-id>/
    ├── course.json
    ├── course-core.json
    ├── source-observations.json        # optional
    ├── materials.json
    ├── topics.json
    ├── materials/
    ├── sessions/
    └── generated/
```

The `.school-learning` name is outside the valid legacy course-identifier
grammar and is the reserved semester metadata namespace. Its `semester.json`
owns term identity, title, and the sorted registered-course identities. Valid
legacy course IDs such as `generated` and `semester.json` therefore remain
ordinary sibling course workspaces and can never alias semester state or
generated output. Each course continues to own its existing workspace; SL2-A
does not move material, topic, session, or generated directories. `course-core.json`
owns the additive v0.2 course profile, authoritative source descriptors,
structured metadata, assessments, policies, and their claims. Optional
`source-observations.json` owns append-only operational source checks. Its
absence is valid and means only that no source-observation state has been
recorded; it does not prove a source was never checked in reality and does not
mean that no coursework exists. `course.json`, topics, and sessions retain
their proven v0.1 contracts.

Every persisted schema uses exact-key validation. Identifiers are path-safe.
Reads and writes reject symlinks and path escapes. State and generated-file
writes use confined atomic replacement. Material and handoff publication retain
rollback behavior.

## Backward Compatibility and Deliberate Registration

Unregistered v0.1/v0.1.1 workspaces remain readable and keep their prior
behavior. Registering such a course into a v0.2 semester is the deliberate
additive migration boundary:

- existing `course.json`, topics, sessions, and copied bytes are unchanged;
- a strict `course-core.json` is added;
- `materials.json` is upgraded atomically to the v0.2 entry shape;
- legacy materials receive only neutral metadata: kind `unspecified`, lifecycle
  `reference`, no relevant date or relationships, and no invented provenance;
- SHA-256, byte size, stored path, title, source filename, and added timestamp
  remain unchanged; and
- a failed registration restores the prior course and semester state.

Semester initialization and course registration are filesystem transactions.
An existing semester is completely validated before any repair or mutation is
attempted. First-time initialization distinguishes absent paths from
pre-existing paths and records each directory creation immediately after its
`mkdir` succeeds, before post-creation validation can fail. Rollback removes
only files and directories created by that operation, with nested directories
removed deepest-first; a rollback failure is reported as incomplete rather than
as an ordinary initialization failure. Registration includes new course
initialization inside its rollback boundary: a failed new registration removes
the complete newly created workspace, while an existing or pre-existing empty
workspace is restored to its exact prior state. State-file rollback uses the
exact original bytes, including noncanonical but valid JSON formatting, rather
than re-encoding parsed JSON.

There is no directory-layout migration and no live owner-data migration in this
checkpoint.

## Course Profiles

A v0.2 profile records optional capability tags, source descriptors, and a
small string metadata map. Supported tags describe common course patterns
without forcing one course model: exam mastery, prerequisite repair,
creative/applied work, project based, team based, tool skill,
reading/listening, attendance sensitivity, equipment/logistics, and AI-policy
sensitivity. Runtime owner data supplies actual course choices; none are
hard-coded in the repository.

One source descriptor can be added or maintained by ID with `./school source`
without reconstructing the complete profile. The operation preserves unrelated
capability tags, metadata, assessments, policies, and source descriptors, and
the resulting source list remains unique and deterministically sorted.

## Operational Source Observations

`source-observations.json` uses the exact-key
`aiden.school.source-observations/v0.1` schema. Each append-only record preserves
an ID, registered `source_id`, explicit observed date or canonical School
Learning timestamp, scope (`full` or `partial`), outcome (`changed`,
`no-relevant-change`, or `unavailable`), sorted course-local material
relationships, and a note. Source and material references must resolve before
mutation. Duplicate IDs, malformed persisted state, invalid enums or dates, and
unknown references fail closed.

`./school observe` appends only explicit operational evidence. Intake never
infers an observation. The latest observation per source is derived from the
records rather than persisted separately, and no observation operation changes
topics, sessions, outcomes, review priority, mastery, or any other learner
state.

## Materials, Topics, Assessments, and Policies

These are distinct entities:

- A **material** is an opaque, byte-identical course artifact plus explicit
  intake metadata. Supported suffixes are `.pdf`, `.md`, `.txt`, `.pptx`,
  `.rmd`, `.png`, `.jpg`, `.jpeg`, and `.webp`. The runtime copies but does not
  parse or classify contents. Explicit kinds include lecture, reading,
  listening reference, assignment specification, syllabus, announcement,
  lab/field guide, technical reference, other, and unspecified. Lifecycle is
  upcoming, current, reference, completed, or superseded.
- A **topic** is an owner-reviewed learning/review unit and retains the v0.1
  learner signal.
- An **assessment** is durable coursework state with a safely normalized,
  bounded custom type string, optional grading-model strings (weight, points,
  or XP), related materials/topics, lifecycle, and sourced claims for known
  dates or other consequential facts. Values such as `presentation`, `paper`,
  `discussion`, and future course-specific types are preserved; the documented
  built-ins are conveniences rather than a closed enum.
- A **policy** identifies a policy category and preserves one or more sourced
  human-readable rule claims. SL2-A stores the evidence but does not route AI
  behavior automatically.

References are course-local and must resolve before mutation. Unknown or
cross-course material, topic, or assessment references are rejected.

Material metadata and course-local references that do not depend on source
bytes are validated against the complete proposed manifest before a temporary
copy is created. Once copying begins, the one-stream copy, SHA-256 and byte
count, replacement, manifest write, identity verification, rollback, and
temporary cleanup remain inside one protected transaction. Rejected semantic
intake leaves the complete course workspace unchanged and retains no temporary
or backup artifact.

Assessment and material updates are field-wise partial updates. Omitted
optional fields preserve existing durable values. Explicit values change only
their named fields, while explicit clear operations set nullable fields to
`null` or relationship lists to empty. In particular, a claim-only assessment
update and a byte-only material replacement do not erase grading metadata,
relationships, lifecycle, relevant date, or provenance. New records still
receive the documented neutral defaults, and the legacy `add-material` behavior
remains compatible.

## Provenance and Conflict Model

Material provenance records a source descriptor, observed date/timestamp, and
one of `confirmed`, `provisional`, `conflicted`, or `superseded`.

Assessments and policies use sorted claim records. Each claim retains its field,
human-readable value, source, observed date/timestamp, and the same status set.
Adding a distinct active value for the same field preserves both claims and
marks every active claim in that field as conflicted. The invariant is checked
on every load and mutation: an active disagreement cannot contain a confirmed
or provisional silent winner, and a field without an active disagreement
cannot retain a conflicted claim. Re-submission and status transitions
recompute the complete field set; superseded claims do not participate. When
supersession leaves one active value, any formerly conflicted survivor returns
to provisional until explicitly confirmed. No value is deleted or selected as
a winner. Policy aggregate status is deterministically derived from its claims
and persisted state is rejected if the aggregate diverges.

## Reviewed Structured Update Return Path

The manual course-chat return path is:

```text
evidence -> candidate -> preview -> owner approval -> bounded apply
```

`aiden.school.reviewed-update/v0.1` is an exact-key, data-only candidate
schema. Its root names one term and course, the SHA-256 of the exact current
`course-context.md` bytes, and an ordered operation list. Those deterministic
context bytes are the reviewed semantic-state identity: they include the exact
complete course core, including `created_at` and `updated_at`, plus the course,
materials, topics, and source-observation state that reviewed operations inspect,
validate against, or may overwrite. The initial operation allowlist is
assessment upsert, policy upsert, source upsert, and source observation.
Assessment and policy operations contain one or more sourced claims and reuse
the existing provenance/conflict model. The schema cannot express shell
commands, executable code, raw byte intake, arbitrary paths or file writes,
external actions, learner/mastery changes, or references outside the named
course.

New reviewed candidates cannot use the legacy scheduling field `due`; they use
`due-at` for normalized forward scheduling. `due-at`, `available-at`, and
`available-until` values must be canonical `YYYY-MM-DD` or use the canonical
School Learning timestamp subset. That timestamp subset requires the complete
date and time through whole seconds plus an explicit `Z` or numeric
`+/-HH:MM` offset. Fractional seconds are optional; when present they contain
exactly 1 through 6 digits. Seven or more digits, an omitted seconds field, an
omitted timezone, or a malformed offset is invalid. The runtime parses those
validated components deterministically and right-pads accepted fractional
digits for microsecond representation; it never delegates grammar acceptance
to a Python-version-specific ISO parser and never truncates excess precision.
Source-observation timestamps use the same canonical subset. Other claim fields
remain extensible human-readable strings and continue to preserve conflicts.

Reviewed source-observation material relationships must already be valid,
sorted, and unique; candidate validation never repairs their ordering or
duplicates before semantic digesting. A source-observation ID is an append-only
identity, not an update key: it must satisfy the identifier grammar, must not
already occur in `source_observations[*].id` from the supplied base context, and
must not match an ID from any earlier source-observation operation in the same
ordered candidate. Existing observation IDs cannot be overwritten or reused.

`./school review-update PATH` exactly validates the candidate and all proposed
cross-references, recomputes the current strict course-context identity,
simulates the complete ordered operation list in memory, prints a deterministic
durable-state diff, and prints the semantic SHA-256 of canonical validated JSON.
Preview performs no durable or generated-state mutation. A base-context mismatch
fails as stale before approval.

`./school apply-update PATH --confirm DIGEST` rereads and revalidates the file,
requires the exact semantic digest, rechecks the context base, and re-simulates
all operations. Immediately before final persistence it reloads the complete
mutation-relevant state, recomputes the same semantic-state identity used by
preview, rejects any mismatch, and simulates from that rechecked state. A changed
candidate needs a new preview and digest; even a timestamp-only course-core
mutation makes the old candidate stale. The complete proposed academic and
observation state is validated before persistence. When more than one state file
changes, exact prior bytes and existence are retained and a failure restores the
complete prior state; a newly created observation file is removed on rollback.
No partial reviewed update may survive.

Returning a candidate from an AI interface does not approve it and does not
change local state. The owner remains the only approval boundary, and reviewed
updates never accept raw material-byte intake.

## Generated Views

Course Home remains static deterministic HTML and escapes user-supplied values.
It shows course profile, material kind/lifecycle, assessments and schedule
claims, policies/conflicts, existing topic review state, and recent sessions.
The Review Markdown remains available.

Semester Home is deterministic Markdown over registered local course state. It
shows courses, known assessments and their claims, and provisional/conflicted
information. It does not claim knowledge of personal availability, work shifts,
Calendar state, or recommended study scheduling.

Semester Plan is a separate derived Markdown projection written to
`.school-learning/generated/semester-plan.md`. `./school render-plan TERM
--as-of YYYY-MM-DD` requires an explicit date so repeated rendering over the
same durable bytes is deterministic. The compact view separates due/overdue,
next-three-day, next-seven-day, dated preparation material, source coverage,
assessment availability windows, planning conflicts, longer-horizon summaries,
and scheduling values that cannot safely be interpreted. It assigns no urgency
or confidence score and never becomes canonical state.

Active assessment planning treats active legacy `due` and normalized `due-at`
claims as one complete semantic due-date family and ignores superseded claims.
A due value may be ranked only when every active family member is supported by
the bounded parser and every interpreted value has the same semantic meaning.
Equal supported aliases therefore rank once. Differing supported meanings, or
any mixture of supported and unsupported active family members, produce no
winner; the complete active set, including source and observation provenance,
remains in the conflict section, and each unsupported value is also shown as
unstructured scheduling information. If every active member is unsupported,
all remain unstructured and none is ranked; when that set has multiple members,
the complete set also remains a planning conflict. A single supported active
member ranks normally, while a single unsupported member remains unstructured.
Submitted, graded, and reviewed assessments are not active due work. Dated
preparation is limited to explicit relevant dates on planner-useful reading,
listening-reference, and lab/field-guide materials; syllabus and course
snapshots do not become preparation merely because they have a date. Source
coverage shows the latest durable observation or explicitly says that a
registered source has never been observed in durable state; it does not decide
whether a source is fresh enough. For Semester Plan source-coverage recency,
canonical timestamps are compared as UTC instants using the shared School
Learning timestamp parser, with observation ID used only to break a semantic
instant tie. For this ordering only, a date-only observation is represented by
the UTC start-of-day sentinel for that date, so `2026-09-01` orders equally with
`2026-09-01T00:00:00Z`. This deterministic cross-precision convention is not
evidence that a date-only observation actually occurred at midnight and does
not assign it local-time semantics.

The normalized formats above are the forward contract. For existing SL2-A
state, the planner also has a small explicit legacy parser for `Sep 8, 2026,
11:59pm`, `Aug 30, 2026, 11:59 PM`, and `YYYY-MM-DD` shapes. It is not a natural
language parser. Unsupported values are reported under unstructured scheduling
claims and are never guessed. Semester Home remains the complete audit-oriented
inventory; Semester Plan is the as-of operational projection.

## Local AI Boundary and Portable Handoffs

The existing Guided Study Handoff remains intact. SL2-A also provides a course
handoff that does not require a study topic. It contains strict durable course
context, a grounding prompt, a manifest, a deterministic update contract, and
every and only explicitly selected material attachment.
`attachments/course-context.md` includes exact source-observation state and is
a required distinguished context/support attachment even when zero materials
are selected. `attachments/update-contract.json` is a second required
distinguished attachment. It records the reviewed-update schema, term, course,
exact course-context SHA-256, operation keys, bounded enums, and a deterministic
machine-readable constraint map. That map is self-contained for candidate
construction: it states exact keys and constants, identifier and assessment-type
grammars, string and nullability rules, the canonical timestamp/date forms,
source-observation append-only identity plus base-state and prior-operation
novelty scopes, list and claim constraints, cross-reference rules, operation
bounds, the complete base identity coverage, and the fact that AI output is
only a candidate. The manifest records both required attachments separately
from selected material records and IDs.
`START-HERE.md` and CLI output direct the owner to attach every required file in
`attachments/` and then paste `prompt.txt`, so durable profile, assessment,
policy, provenance, and conflict state reach the consumer. Each selected
material attachment is checked against recorded SHA-256 and byte size and
copied with the hardened confined package-publication machinery, so a later run
cannot retain stale context or material files.

The production runtime has no network or model dependency. The owner manually
transfers a prepared package to an approved AI consumer. The prompt requires
the consumer to preserve conflicts, distinguish general knowledge, disclose
insufficient evidence, and not invent course facts, deadlines, policies,
permission, grades, readiness, or mastery. When the owner explicitly asks to
synchronize reviewed findings, the prompt requires a candidate matching the
attached contract and forbids claiming that the candidate changed local state.
AI output is never automatically applied or used to update learner state.

## Refresh Transport and Packaging

`./school prepare-refresh TERM COURSE [--material ID ...] [--evidence PATH ...]
[--notes TEXT | --notes-file PATH] [--open]` prepares a complete refresh in one
step. Repeated selection options are supported. It shares course-handoff
content construction, exact course-context and update-contract generation,
verified durable-material copying, confinement, and atomic publication/recovery
with `prepare_course_handoff`; ordinary `course-context` behavior is unchanged.
There is no prepare/finalize draft or separate reviewed-update architecture.

The completed directory is
`generated/refresh-package-<full-package-sha256>/`. It contains:

- `START-HERE.md` and stable `prompt.txt` protocol instructions;
- `manifest.json` using `aiden.school.refresh-package/v0.1`;
- required `attachments/course-context.md`, `attachments/update-contract.json`,
  and `attachments/refresh-context.json`;
- every and only explicitly selected durable material and transient evidence
  attachment; and
- an initially absent `reviewed-update.json` owner/external-return slot.

The refresh context uses `aiden.school.refresh-context/v0.1` and carries term,
course, the complete attachment filename list, exact owner notes, and transient
evidence metadata. Notes are situational context, not stable protocol, academic
truth, or executable instructions. UTF-8 note content is preserved without
trimming, newline conversion, or Unicode normalization; its exact UTF-8 byte
count and full SHA-256 are recorded. An inline note and a notes file containing
identical UTF-8 bytes have the same identity. Invalid UTF-8 fails closed.

Transient evidence supports the existing opaque material suffix set. It is
never parsed, classified, discovered by crawling, or promoted to durable
materials. Each item has the identity `evidence-<full-content-sha256>` and an
attachment filename consisting of that identity plus its lowercase accepted
suffix. Original/display basename and type are metadata; the absolute source
path is not exported. Duplicate selected evidence bytes fail clearly, even
under different names or suffixes. Filename drift preserves evidence identity;
changed display metadata creates a different package so provenance remains
exact. Before staging or publication, refresh preparation rejects any computed
transient evidence identity that equals any existing durable material ID in the
course, including materials not selected for attachment. This refresh-boundary
check prevents ambiguous identities without reserving a global prefix or changing
the existing durable material ID grammar, reviewed-update validation, or apply
semantics. A transient identity in a successfully prepared package therefore
cannot resolve as a durable `material_ids` entry in its base course state.
Packaging creates no source observation, source descriptor, or academic fact.

Selection is bounded to 100 combined durable-material/evidence inputs and
100,000,000 aggregate selected attachment bytes. Notes are separately bounded
to 1,000,000 bytes. These follow School Learning's explicit 100-item/1 MB
bounded-input convention, with a larger aggregate allowance for opaque slide
decks and images. The aggregate budget also bounds transient in-memory
snapshots; context/contract generation retains the existing course-state
behavior. External reads require POSIX descriptor-relative no-follow support
(as available in the native WSL environment); unsupported hosts fail closed.
Each ancestor and the final file are opened without following symlinks, parent
traversal is rejected, and only regular files are read. Descriptor signatures,
bounded reads, and exact source-byte rechecks after copying detect source
changes before publication. No source is opened by the GUI.

The manifest records hashes and byte counts for deterministic generated files
and selected attachments. Package identity hashes the canonical manifest
before its `package_id` field is added. It includes protocol and refresh
context identities, selected bytes and display metadata, but excludes the
later owner-return bytes; there is no hash cycle. Identical reruns validate all
generated content and selected attachment identities, then reuse the package
without replacing it. An existing regular owner-return file is preserved
regardless of its contents and is never accepted as valid by package
validation. Tampered generated content, extra attachments, unsafe paths, or
source changes fail closed. Changed inputs use a different package directory.
New package publication reuses the existing rollback/recovery machinery. No
automatic retention or deletion policy is introduced.

The owner attaches every file in `attachments/` and pastes `prompt.txt` into an
approved AI interface. Generated instructions require completeness checks,
current-package grounding, preservation of provenance/uncertainty/conflicts,
and separation of notes from protocol. When transient evidence materially
supports a returned claim, human-readable provenance/source text should include
its deterministic `evidence-<sha256>` identity where practical. This requires
no candidate-schema change.

The preferred return is a downloadable UTF-8 `reviewed-update.json`. If file
artifact creation is unavailable, the fallback is exactly one raw fenced JSON
object; the owner manually saves only the JSON object as UTF-8. School Learning
never strips fences, repairs Markdown, or loosens strict validation. When no
durable update is warranted, the AI should say so rather than manufacture an
invalid empty candidate. The owner uses the unchanged `review-update` preview,
stale-base check, semantic digest, explicit approval, and `apply-update
--confirm` path. Package location grants no trust and no AI return changes
local state automatically.

`--open` is optional CLI-side convenience. On supported WSL/Windows hosts,
argument-array calls to `wslpath` convert the completed directory to an absolute
Windows path and require an exact reverse conversion before invoking
`explorer.exe` with that one directory argument. Before conversion and again
immediately before Explorer launch, the CLI validates the content-addressed
manifest, expected course confinement, complete generated content and attachment
identities, and non-symlink package tree. It also requires the directory's device
and inode to remain the same across conversion, rejecting even a byte-identical
directory replacement. The owner-return slot remains untrusted and its bytes are
not read by this guard. Validation failure warns without changing package
construction success. Explorer accepts a pathname, not the validated directory
descriptor; this last-moment check cannot make the later host filesystem lookup
atomic against a concurrent writer. Calls have five-second
timeouts and use no shell interpolation or `cmd /c`. Unsupported hosts, absent
tools, invalid conversion, timeout, or opener failure warn and retain the
successful package and printed usable path. Without `--open`, no opener or
conversion process runs. Actual GUI behavior is separate from core package
semantics and requires host verification; mocked subprocess checks do not
claim that a real window opened.

## Explicit Exclusions and Future SL2-B

This checkpoint excludes LMS/Canvas scraping, Calendar, Gmail/email, OCR,
audio/MP3 intake, semantic extraction, embeddings, vector databases, knowledge
graphs, provider/model APIs, automatic assistant-response application,
automatic mastery inference, planner-confidence scoring, class-calendar
models, autonomous scheduling or notifications, assessment-status event
history, claim-taxonomy redesign, and live personal-data migration or rewrite.
Future Canvas, Calendar, or email capabilities could be separately designed as
producers or consumers of bounded state, but they are not integrations or an
architecture established here.

SL2-B is future adaptive learning and coursework behavior. Multidimensional
learner state, prerequisite adaptation, automatic mastery inference, policy
routing, and schedule-aware recommendations are not implemented here.

## Relationship to Other Platform Work

The accepted EO-2026-013 B2b release remains a separate engineering-context
compiler. Course and Semester Home are school-specific local views; they do not
implement the EO-2026-022 engineering control surface or become a general
AidenOS shell.
