# School Learning Architecture

## Purpose

School Learning provides a bounded, owner-controlled workflow for using real course materials, grounded AI assistance, practice, review, and visible learning signals.

The first release proves repeated direct value before generalized ingestion, automation, or a broad platform interface is introduced.

## Architectural Position

School Learning is a Human Agency Domain workflow primarily owned by `learning-research`. It composes:

- `knowledge-context` for course material identity, provenance, and study state;
- `artificial-intelligence` for provider-independent explanation and practice;
- `interaction-experience` for generated study and review views; and
- `security-privacy-resilience` for local personal-data boundaries.

The engineering repository owns architecture and implementation. Course materials, answers, learning history, and generated personal views remain outside Git in an owner-controlled data root.

## v0.1.1 Workflow

```text
Create course workspace
  -> Add material manually
  -> Select topic and study mode
  -> Generate bounded study brief
  -> Prepare Guided Study Handoff
  -> Attach every prepared attachment and paste the prepared prompt in an approved AI interface
  -> Record the owner-reviewed outcome
  -> Render Course Home and Review
  -> Repeat
```

## Local Data Contract

The default root is `${AIDEN_SCHOOL_DATA_ROOT:-~/.local/share/aiden-platform/school}`.

Each course owns `course.json`, `materials.json`, `topics.json`, copied materials, individual session records, and generated views. Writes are atomic. Identifiers are path-safe. Stored JSON is validated before mutation.

Materials are restricted to PDF, Markdown, and plain text. v0.1 records exact SHA-256 and byte size but performs no parsing, OCR, indexing, embedding, summarization, or model operation.

### Guided Study Handoff

A successful `./school study` run preserves the v0.1 topic and study-brief behavior and additionally replaces one complete package:

```text
generated/study-handoff/
├── START-HERE.md
├── prompt.txt
├── manifest.json
└── attachments/
    ├── study-brief.md
    └── material-<exact-material-id>.<supported-suffix>
```

The attachments directory contains the study brief plus every and only explicitly selected material. Material copies are taken only from the owner-controlled course workspace. Stored-path confinement, real regular-file status, non-symlink status, recorded byte size, recorded SHA-256, and final byte identity are validated around each copy.

The package is assembled in a confined staging directory, strictly revalidated, and published as one fail-safe directory replacement. A later successful study run cannot retain stale attachments from an earlier selection. `manifest.json` uses schema `aiden.school.study-handoff/v0.1.1` and deterministically records course, term, topic, mode, objective, attachment filenames, and material identities.

## Learning Signal

A topic has one owner-reviewed status: `unseen`, `learning`, `review`, or `solid`. A session records `correct`, `partial`, or `incorrect`, a note, and a review priority. The system does not infer mastery automatically.

## AI Boundary

The repository tool performs no network or model invocation. It generates a portable study brief and a Guided Study Handoff package. The owner manually attaches every file prepared under `attachments/`, pastes `prompt.txt` into an approved AI interface, reviews the result, and records the final outcome.

The AI consumer must identify supporting material, distinguish general knowledge from course grounding, expose insufficient evidence, and avoid inferring grades, mastery, deadlines, or course policy.

The prepared prompt also forbids inferred permission, requires a compact completion result, and preserves the final owner-reviewed recording boundary. No AI result updates learner state automatically.

## Relationship to EO-2026-013 and EO-2026-022

The accepted B2b release remains an engineering-context compiler with a fixed first-slice policy. It is evaluated through a separate read-only consumer handoff and is not expanded into the course-material runtime.

The generated Course Home is a school-specific view over local course state. It does not implement the EO-2026-022 engineering control surface or become a general AidenOS shell.

## Explicit Exclusions

- B2c or B2b expansion.
- Atlas commands or reasoning changes.
- Generalized ingestion, OCR, embeddings, vector databases, or knowledge graphs.
- LMS, Gmail, or Calendar integration.
- Provider APIs or automatic model routing.
- Automatic assistant-response ingestion.
- Scheduling, notifications, grade prediction, or full spaced repetition.
- Public deployment, authentication, multi-user use, or a persistent application database.
- Larger dashboard work, result capture, topic discovery, and broader application behavior remain future product decisions.
