# School Learning Architecture

## Purpose

School Learning is an owner-controlled, semester-aware local workflow for
durable course context, opaque material intake, grounded manual AI assistance,
and owner-reviewed learning state. Repository code and architecture are
engineering state; personal course content and runtime state remain outside Git
under the owner's selected data root.

## Proven Baseline and SL2-A Evolution

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

It does not add adaptive learner dimensions, model invocation, or an external
integration.

## Truth Boundaries

School Learning keeps three kinds of truth distinct:

- **Academic truth** is explicit stored course identity, source descriptors,
  materials, assessments, policies, dates, and provenance claims. Conflicting
  consequential claims remain side by side with their status and source.
- **Learner truth** is owner-reviewed topic and session state. The retained
  statuses are `unseen`, `learning`, `review`, and `solid`; retained outcomes are
  `correct`, `partial`, and `incorrect`. Intake never changes learner truth.
- **Operational truth** is the local file identity and workflow state: confined
  paths, SHA-256, byte counts, generated packages, and atomic persistence.

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
│       └── semester-home.md
└── <course-id>/
    ├── course.json
    ├── course-core.json
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
structured metadata, assessments, policies, and their claims. `course.json`,
topics, and sessions retain their proven v0.1 contracts.

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

## Generated Views

Course Home remains static deterministic HTML and escapes user-supplied values.
It shows course profile, material kind/lifecycle, assessments and schedule
claims, policies/conflicts, existing topic review state, and recent sessions.
The Review Markdown remains available.

Semester Home is deterministic Markdown over registered local course state. It
shows courses, known assessments and their claims, and provisional/conflicted
information. It does not claim knowledge of personal availability, work shifts,
Calendar state, or recommended study scheduling.

## Local AI Boundary and Portable Handoffs

The existing Guided Study Handoff remains intact. SL2-A also provides a course
handoff that does not require a study topic. It contains strict durable course
context, a grounding prompt, a manifest, and every and only explicitly selected
material attachment. `attachments/course-context.md` is a required,
distinguished context/support attachment even when zero materials are selected;
the manifest records it separately from selected material records and IDs.
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
permission, grades, readiness, or mastery. AI output is never ingested or used
to update learner state automatically.

## Explicit Exclusions and Future SL2-B

SL2-A excludes LMS/Canvas scraping, Calendar, email, OCR, semantic extraction,
embeddings, vector databases, knowledge graphs, provider/model APIs, automatic
assistant-response ingestion, autonomous scheduling or notifications, grade or
readiness inference, and live personal-data migration.

SL2-B is future adaptive learning and coursework behavior. Multidimensional
learner state, prerequisite adaptation, automatic mastery inference, policy
routing, and schedule-aware recommendations are not implemented here.

## Relationship to Other Platform Work

The accepted EO-2026-013 B2b release remains a separate engineering-context
compiler. Course and Semester Home are school-specific local views; they do not
implement the EO-2026-022 engineering control surface or become a general
AidenOS shell.
