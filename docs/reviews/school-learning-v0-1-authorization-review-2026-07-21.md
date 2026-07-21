# School Learning v0.1 Authorization Review

- Date: 2026-07-21
- Canonical baseline reviewed: `e564ca6ffb2698b456689a582cf322b37a5fe1c8`
- Decision authority: Owner
- Implementation and publication authorization: Exact thirteen-path implementation, verification, staging, one intentional commit, implementation-branch push, and one draft pull request against `main`
- Merge, direct `main` modification, deployment, Project changes, and lifecycle changes: Not authorized

## Decision

The owner selected School Learning v0.1 — Manual Course Workspace and Study Loop as the next implementation checkpoint.

The release uses owner-controlled local course storage, manual PDF/Markdown/text intake, provider-independent study briefs, owner-reviewed learning signals, and generated static course views. It does not invoke a model or network service.

EO-2026-010 remains a strategic learning direction. EO-2026-022 remains captured. EO-2026-013 B2b remains fixed and B2c remains unauthorized.

## Exact Path Boundary

### Create

- `docs/architecture/school-learning.md`
- `docs/reviews/school-learning-v0-1-authorization-review-2026-07-21.md`
- `school`
- `tools/school_learning/__init__.py`
- `tools/school_learning/core.py`
- `tools/school_learning/render.py`
- `tools/school_learning/cli.py`
- `tests/test_school_learning.py`

### Modify

- `docs/current-mission.md`
- `docs/docs-map.md`
- `docs/architecture/repository.md`
- `tools/atlas/platform/document_definitions.py`
- `docs/aiden-context.md`

## Kill Switch

Stop for owner review if implementation requires a dependency, network or provider integration, Atlas command, context-compilation change, schema or policy change outside the school-local contract, personal data in Git, path outside the exact boundary, or broader interface infrastructure.

## Verification Requirements

Focused tests must cover safe paths, atomic writes, JSON validation, material digests and replacement detection, deterministic rendering, HTML escaping, local-only operation, and synthetic fixtures. Repository integration additionally requires the safe broad suite, Atlas validation, synchronization, and an exact-path review in a live checkout.

Publication is limited to commit subject `feat: add school learning v0.1` on `agent/school-learning-v01` and a draft pull request titled `School Learning v0.1 — Manual Course Workspace and Study Loop` against `main`. Independent acceptance and merge remain later owner decisions.
