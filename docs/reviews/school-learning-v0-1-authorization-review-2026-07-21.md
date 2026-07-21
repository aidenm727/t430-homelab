# School Learning v0.1 Authorization Review

## Original Authorization Record

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

The preceding section preserves the original authorization at baseline `e564ca6ffb2698b456689a582cf322b37a5fe1c8`. Its merge exclusion describes the authority at that checkpoint and is superseded only by the later owner publication decision recorded below.

## Post-Authorization Implementation Evidence

This section records implementation evidence, not an independent-review judgment or owner decision.

- Original baseline: `e564ca6ffb2698b456689a582cf322b37a5fe1c8`.
- Implementation commit: `d017885bc1e86877f494ce70a3c83d193dbd9122` (`feat: add school learning v0.1`).
- Implementation branch: `agent/school-learning-v01`.
- Implementation stayed within the exact thirteen-path boundary in the original authorization record:
  - `docs/aiden-context.md`
  - `docs/architecture/repository.md`
  - `docs/architecture/school-learning.md`
  - `docs/current-mission.md`
  - `docs/docs-map.md`
  - `docs/reviews/school-learning-v0-1-authorization-review-2026-07-21.md`
  - `school`
  - `tests/test_school_learning.py`
  - `tools/atlas/platform/document_definitions.py`
  - `tools/school_learning/__init__.py`
  - `tools/school_learning/cli.py`
  - `tools/school_learning/core.py`
  - `tools/school_learning/render.py`

## First Independent-Review Outcome

This section records the independent-review outcome. It does not itself grant correction or publication authority.

- Disposition: `BOUNDED CORRECTION REQUIRED`.
- SL-01 — Persisted-state validation: require exact keys, types, enum and timestamp bounds, workspace identities, and cross-record references before mutation or rendering.
- SL-02 — Path and repository confinement: reject repository or linked-worktree data roots and prevent symlink-mediated reads, writes, deletion, or generated-output escape.
- SL-03 — Material identity and atomic replacement: derive the digest, byte count, and copy from one opened source stream; verify stored identity; and restore the complete prior material and manifest state on failure.
- SL-04 — Session provenance: persist and validate study mode and selected material identifiers, expose mode through the `record` command, and reject inconsistent session identity or provenance.

## Owner-Authorized Bounded Correction

This section records implementation evidence produced under the owner's acceptance of SL-01 through SL-04.

- Correction commit: `df8cd6cab2f3a16a2ae6ac864f9cb76a50424a55` (`fix: harden school learning state and paths`).
- Exact four-path correction boundary:
  - `tests/test_school_learning.py`
  - `tools/school_learning/cli.py`
  - `tools/school_learning/core.py`
  - `tools/school_learning/render.py`
- All four correction paths stayed within the original thirteen-path PR boundary.
- The accepted implementation head after correction is `df8cd6cab2f3a16a2ae6ac864f9cb76a50424a55`.

## Final Verification Evidence

This section records the final verification results accepted for the corrected implementation head. The documentation-only acceptance pass does not rerun the executable suites.

- 50 focused School Learning tests passed.
- Python compilation passed.
- All five CLI commands passed.
- 321 safe broad-regression tests passed with one expected guarded skip.
- Atlas Validate was Valid with zero errors and zero warnings.
- Atlas Missing was complete.
- Atlas Sync was Synchronized with zero errors and zero warnings.
- The read-only B2b consumer handoff proof passed.
- `git diff --check` passed.
- Secret, privacy, scope, and unauthorized-path audits passed.
- Course data and temporary state remained outside Git.

## Fresh Independent Re-Review Outcome

This section records the final independent judgment. It does not itself grant owner acceptance or publication authority.

- Disposition: `ACCEPT — implementation-complete and suitable for owner acceptance and merge`.
- The accepted review target is `df8cd6cab2f3a16a2ae6ac864f9cb76a50424a55`.

## Owner Decision

On 2026-07-21, the owner explicitly accepted the fresh independent `ACCEPT` disposition. School Learning v0.1 is owner-accepted, implementation-complete at `df8cd6cab2f3a16a2ae6ac864f9cb76a50424a55`, and suitable for merge.

This decision does not invent or predeclare the final canonical `main` merge commit. That commit will be established only by the separately authorized PR #1 merge.

## Publication Authority

The owner authorizes the guarded merge of PR #1 as the final School Learning v0.1 publication action. The already-authorized connector-side PR-description update and ready-state transition may precede that merge.

The publication authority does not authorize direct modification of `main`, amend, rebase, squash, force-push, branch deletion, or any content change outside the accepted PR. Branch deletion is explicitly not authorized.

## Remaining Exclusions and Next Step

- B2b remains fixed.
- B2c remains unauthorized.
- EO-2026-022 remains captured and unimplemented.
- No additional School Learning implementation, broader school or career work, lifecycle advancement, dependency, CI, deployment, or next implementation is authorized.
- No next implementation is selected.
- After merge, the next step is pilot use and evaluation, not automatic capability expansion.
