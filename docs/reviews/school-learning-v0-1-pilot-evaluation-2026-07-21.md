# School Learning v0.1 Pilot Evaluation

## Record Status

- Date: 2026-07-21
- Evidence class: Dated, non-canonical pilot evidence
- Decision authority: Owner
- Evaluated release: School Learning v0.1 — Manual Course Workspace and Study Loop
- Authorized follow-up: School Learning v0.1.1 — Guided Study Handoff
- Current checkpoint: Independently and owner accepted as implementation-complete; bounded publication authorized

This record preserves the pilot observation and the bounded product decision that followed it. Canonical product intent remains in `docs/architecture/school-learning.md`, and active checkpoint state remains in `docs/current-mission.md`.

## Observed Evidence

The v0.1 manual study loop worked in genuine owner-controlled use. The pilot confirmed:

- grounded tutoring from explicitly selected course materials;
- genuine recovery of course knowledge during the study interaction;
- safe insufficient-evidence behavior when the supplied attachments did not ground an answer;
- owner review before any learner-state recording; and
- deterministic rendering of the local Course Home and Review views.

The pilot also confirmed recurring friction:

- manual path handling to locate generated briefs and course materials;
- ambiguous generated and material filenames;
- error-prone attachment selection;
- repeated reconstruction of the opening prompt;
- a passive dashboard that displays state without guiding the study handoff; and
- manual recording of the reviewed result.

In one genuine pilot, `generated/review.md` was attached instead of the selected Chapters 1–3 review-list PDF. The AI consumer safely disclosed insufficient grounding rather than inventing support. That response confirmed the existing evidence boundary, while the attachment error demonstrated that v0.1 placed avoidable file-selection work on the owner.

## Product Inference

The narrow product problem is not course ingestion, provider automation, or learner-state inference. It is the gap between a successful `./school study` command and a clear, correctly grounded manual handoff to an approved AI interface.

A deterministic local package can remove that gap while retaining provider independence and human authority. The package should make the selected evidence mechanically obvious, supply a ready-to-paste prompt, and keep the final recording step owner-reviewed.

## Accepted Product Decision

Define v0.1.1 as **Guided Study Handoff**.

On every successful study run, School Learning prepares one replaceable package under `generated/study-handoff/` containing:

- plain-language start instructions;
- a ready-to-paste prompt;
- strictly validated deterministic metadata; and
- an attachments directory containing the study brief and every and only explicitly selected material.

Selected materials remain owner-controlled local files. Their copied attachments retain exact material identifiers in their filenames and are verified against recorded byte size and SHA-256 identity before and after copying. The tool still performs no provider or model invocation, and the AI result still does not update learner state automatically.

## Preserved Authority Boundary

Provider-independent manual AI use remains the operating model. The owner chooses the approved AI interface, attaches every prepared file, reviews the result, and decides whether and how to record it with `./school record`.

The following remain future decisions rather than implied parts of v0.1.1:

- a larger or interactive dashboard;
- automatic or assisted result capture;
- automatic topic discovery;
- scheduling or notifications;
- provider or model integration; and
- a public or multi-user application.

LMS, Gmail, Calendar, OCR, parsing, indexing, embeddings, databases, B2b or B2c changes, and Engineering Opportunity lifecycle changes also remain outside this checkpoint.

## Local Verification Evidence

Observed local results for the implementation candidate:

- 74 focused School Learning tests passed.
- Python compilation passed for the School Learning package and focused test module.
- A fresh synthetic temporary-data-root smoke flow passed through `init`, `add-material`, `study`, `record`, and `render`.
- Manual smoke inspection confirmed the exact handoff structure, ready-to-paste prompt, strict manifest, and byte-identical selected PDF attachment.
- 345 broad-regression tests passed with one expected guarded skip.
- Atlas Validate reported Valid with zero errors and zero warnings.
- Atlas Missing reported that every discovered document has a metadata definition.
- Atlas Sync reported Synchronized with zero errors and zero warnings.

These results established the locally verified implementation candidate reviewed at the acceptance gate. They are implementation evidence rather than the independent judgment or owner decision recorded below.

## Independent Acceptance Outcome

The independent acceptance review of the exact nine-path local candidate completed with disposition:

`A. ACCEPT — implementation-complete and suitable for owner acceptance`

This disposition is the independent judgment. It does not itself grant owner acceptance or publication authority.

## Owner Acceptance and Publication Authority

On 2026-07-27, the owner accepted the independent disposition and owner-accepted School Learning v0.1.1 — Guided Study Handoff as implementation-complete.

The owner separately authorized the bounded publication checkpoint for the exact accepted candidate: truthful acceptance recording, repository-owned generated-context regeneration, exact-candidate verification, staging of exactly the existing eight modified tracked paths and this untracked pilot-evaluation record, the minimum coherent commit or commits, direct push to `origin/main`, and final repository, Atlas, and published-documentation verification.

Pull-request creation, unrelated paths, dependencies, architecture or product expansion, branch deletion, another capability, deployment, and every other external action remain outside that authority.

## Next Gate

Publish the exact accepted nine-path candidate to `origin/main`, verify the final state, and stop.
