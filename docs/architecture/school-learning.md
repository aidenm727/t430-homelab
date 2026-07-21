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

## v0.1 Workflow

```text
Create course workspace
  -> Add material manually
  -> Select topic and study mode
  -> Generate bounded study brief
  -> Use the brief and selected materials in an approved AI interface
  -> Record the owner-reviewed outcome
  -> Render Course Home and Review
  -> Repeat
```

## Local Data Contract

The default root is `${AIDEN_SCHOOL_DATA_ROOT:-~/.local/share/aiden-platform/school}`.

Each course owns `course.json`, `materials.json`, `topics.json`, copied materials, individual session records, and generated views. Writes are atomic. Identifiers are path-safe. Stored JSON is validated before mutation.

Materials are restricted to PDF, Markdown, and plain text. v0.1 records exact SHA-256 and byte size but performs no parsing, OCR, indexing, embedding, summarization, or model operation.

## Learning Signal

A topic has one owner-reviewed status: `unseen`, `learning`, `review`, or `solid`. A session records `correct`, `partial`, or `incorrect`, a note, and a review priority. The system does not infer mastery automatically.

## AI Boundary

The repository tool performs no network or model invocation. It generates a portable study brief. The owner manually supplies that brief and selected materials to an approved AI interface, reviews the result, and records the final outcome.

The AI consumer must identify supporting material, distinguish general knowledge from course grounding, expose insufficient evidence, and avoid inferring grades, mastery, deadlines, or course policy.

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
