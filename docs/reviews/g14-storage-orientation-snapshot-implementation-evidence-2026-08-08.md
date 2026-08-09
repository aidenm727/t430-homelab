# G14 Storage Orientation Snapshot Implementation Evidence — August 8, 2026

## Record Status

- Checkpoint: `g14-storage-orientation-snapshot`
- Consequence tier: Tier 3 — privacy and canonical selected-work semantics
- Base commit: `8a2eb0a9c62ee49442a8f446decb6b020401fd8e`
- Evidence class: Dated, non-canonical Tier 3 implementation, acceptance, and
  publication-boundary evidence
- Accepted implementation identity: The exact four product/core-test SHA-256
  values recorded below; lifecycle-only public-surface and canonical-state
  synchronization does not change that accepted implementation boundary
- Correction state: The final PowerShell drive/root gate-order correction and
  bounded test-invariant correction are present. Owner-executed native Windows
  and exact normal-WSL verification apply to the current product/test hashes
  recorded below.
- Independent review: `A. ACCEPT`; no blocking or non-blocking findings
- Owner acceptance: Explicit for the exact accepted implementation candidate
  following final Tier 3 disposition
- Publication authority: Separately explicit and bounded to the eleven-path
  G14 candidate, local commit, and normal push to `origin/main`
- Lifecycle boundary: G14 is owner-accepted. Its published-and-complete state is
  established by successful publication and final Git/Atlas verification; this
  record does not predict or pretend that its publication commit exists before
  Git creates it. Publication is not complete until the authorized push
  succeeds.
- Deployment, live collection, and operational runtime: Not performed or
  claimed

## Accepted Checkpoint Brief

- **Why:** Establish the smallest useful metadata-only foundation for a future
  one-shot local storage orientation snapshot.
- **Risk tier:** Tier 3 because filesystem metadata, personal filenames, privacy
  sanitization, and canonical work selection are consequential boundaries.
- **Exact scope:** The four collector/analyzer/test programs, this evidence
  record, documentation registration, canonical state and mission, registered
  generated context, and public-surface assertions named in the owner-authorized
  eleven-path set.
- **Exclusions:** Live collection, arbitrary roots, file contents, hashing,
  hosted AI, dependencies, configuration, network or homelab access,
  deployment, and every external write outside the exact authorized normal push
  to `origin/main`.
- **Authority established:** Owner selection, design acceptance, bounded local
  implementation, final owner acceptance, lifecycle synchronization, exact
  staging and local commit, and normal publication to `origin/main` are
  separately explicit. Deployment, live collection, follow-on work, and every
  other external write remain withheld.
- **Protected boundaries:** Fixed owner-approved local aliases only; normal
  non-elevated tokens; no intentional link, reparse-point, mount, or
  cross-device traversal; protected categories are rejected before raw metadata
  emission; traversed subject-file contents are not opened.
- **Observable result:** Versioned shared JSONL, deterministic local analysis,
  owner-facing Markdown, and an independently field-constructed sanitized JSON
  derivative, exercised only with synthetic roots.
- **Verification:** Focused Python and native Windows synthetic tests, one final
  full Python suite after the last mutation, Atlas validation/missing/sync,
  registered generation, complete diff inspection, then fresh independent Tier
  3 adversarial/privacy review.
- **Stop conditions:** The owner-specified scope, architecture, privacy,
  environment, verification, generated-file, and shared anti-loop boundaries.
- **Next decision boundary:** After successful G14 publication, owner selection
  of future work; no later checkpoint is preselected.

This brief records the external authority boundary; it creates no authority.

## Correction-Cycle Disposition

- PowerShell gate order: Windows fixed traversal establishes the normal-token,
  known-folder identity, exact approved pathname, and fixed/ready `C:` drive
  gates before root metadata access or enumeration. Root/reparse checks then
  execute before traversal. Test-owned instrumented source clones cover
  not-ready and non-fixed drives through both the exported collector and direct
  private-module traversal, with zero enumerator creation, advancement, root
  metadata, or candidate metadata access before rejection.
- Authority surfaces: Python production collection remains a zero-argument fixed
  WSL entry. Every PowerShell command owned by the production module that
  directly enumerates must be a no-root-parameter fixed Downloads traversal and
  perform its own normal-token, known-folder resolution, fixed expected-root,
  exact-path, fixed/ready-drive, and root/reparse gates before enumeration. The
  current module has one such private traversal, and the sole exported collector
  reaches enumeration only through it. The former arbitrary-root traversal
  command and a callable caller-supplied-enumerator helper are absent. Synthetic
  Windows traversal uses a global test-owned in-memory source clone with fixed
  temporary-root replacements and ordering instrumentation; it is not owned or
  exported by the production module.
- Native classifier correction: A later native failure exposed a test-invariant
  defect: an unfiltered module-scope `Get-Command` query also classified the
  global synthetic-module helper because its definition contains the enumeration
  method name only in instrumentation strings. It did not identify a new product
  privacy bypass or a second production enumeration capability. The corrected
  test filters on production-module ownership, validates every resulting direct
  enumeration capability, and probes elevation, known-folder, exact-root,
  not-ready, and non-fixed rejection through both exported and direct private-
  module invocation before drive construction or filesystem access as
  applicable.
- Mount/link boundary: WSL reads bounded Linux mount metadata to recognize
  existing nested mounts, including same-device bind-mounted directories and
  regular files. A recognized mount point is rejected before stat or entry
  emission for every entry type. Descriptor-relative `O_NOFOLLOW` directory
  opens and device/inode checks remain. Windows continues to reject reparse
  points before ordinary entry metadata/traversal.
- TOCTOU limitation: No absolute adversarial race-proof guarantee is made.
  Concurrent mount-namespace mutation between the Linux mount snapshot and
  directory open, replacement of an allowlisted root ancestor, or Windows path
  replacement after the last reparse check could expose metadata outside the
  intended traversal. The accepted one-owner, one-shot local model has no
  concurrent mutating actor, so this is not expected to occur in approved use.
  Closing it for an adversarial concurrent-mutator model would require a
  materially different Linux `openat2`/mount-ID and Windows native
  handle-relative traversal design; that is not introduced here.
- Bounds: Each candidate consumes inspection budget when yielded by either
  enumerator. Candidates already yielded remain charged and processable if a
  later enumerator operation fails. Neither implementation requests a candidate
  beyond the hard cap; truncation is incomplete. Reaching the cap exactly may
  conservatively report incomplete because proving exhaustion would require one
  additional enumerator operation.
- Protected metadata: Known protected directory variants and a conservative
  case-insensitive `id_*` OpenSSH-identity filename rule are applied before
  protected-file stat/emission, including security-key names and practical
  backup/suffixed forms. Key-file suffix rules remain. These deterministic
  safeguards are intentionally conservative and are not an exhaustive secret-
  filename detector.
- Stream integrity: Shared validation now permits one entry per logical path and
  scope. Identical or type-conflicting replays are rejected; Windows identities
  are compared case-insensitively and WSL identities case-sensitively, preventing
  replayed records from inflating totals or rankings.
- Sanitization: Every allowed nested output key is independently constructed and
  validated. Raw input dictionaries, paths, names, timestamps, findings, and
  unexpected nested fields are not spread into the sanitized derivative.
- Additional retained corrections: Windows 100-nanosecond timestamp precision
  is honored at age boundaries; empty traversal scopes receive zero totals;
  Markdown name rendering neutralizes markup and bidi controls; candidate IDs
  remain documented as report-local metadata/path-order-derived ordinals, not
  stable identities.

## Review, Acceptance, and Lifecycle Disposition

- The fresh final Tier 3 adversarial/privacy review returned `A. ACCEPT` for the
  exact implementation candidate identified by the four hashes below.
- Blocking findings: None.
- Non-blocking findings: None.
- The owner explicitly accepted that candidate following the final review. No
  renewed owner decision is required for the bounded lifecycle-only
  synchronization.
- W1 remains owner-accepted, published, and complete. G14 transitions from
  selected work to owner-accepted, published, and complete upon successful
  publication. Work selection then returns to intentional idle with no selected
  checkpoint.
- S1, F2, F3, and all future checkpoints remain unselected. The next decision
  is owner selection of future work; repository state and Atlas grant no
  authority themselves.
- No live collection, deployment, or operational-runtime state is established.
  The accepted residual threat-model limitations remain those documented in
  the correction-cycle disposition above.

## Final Verification Boundary

- Current enumeration-invariant-corrected product/test boundary:
  - `tools/storage_orientation.py` — SHA-256
    `6d56ac6c57cef67734b05d3fc0124ce78065ab2aa0e995ffce714e1320c8093a`
  - `tools/storage_orientation_windows.ps1` — SHA-256
    `fe429f016e19a68d7361c73bcbc7cf59646d896eee46fbe7516e310b9782edfe`
  - `tests/test_storage_orientation.py` — SHA-256
    `2b3f0beb0211b26eb750e0f08829175f6f4f8cf785da6e600dfbec2992f23d6c`
  - `tests/test_storage_orientation_windows.ps1` — SHA-256
    `ce8e93e1973e98e22aa8f6027851fdef097d65316bcb8e654f60222fe40bb5d3`
- Final native Windows verification was owner-executed in normal, non-elevated
  interactive Windows PowerShell, with the WSL-hosted product/test scripts
  approved using Run once and with no live Downloads collection: `PASS: 237
  assertions; 0 environment-dependent checks skipped`.
- Final current lifecycle/publication-candidate Python verification was
  owner-executed in normal WSL with writable `/var/tmp`, after the lifecycle
  transition and the lifecycle-only `tests/test_public_surface.py` update,
  using `PYTHONPATH=tools PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
  discover -s tests -p 'test_*.py'`: `Ran 489 tests in 47.222s`; `OK
  (skipped=1)`.
- The lifecycle-only `tests/test_public_surface.py` verified by that run has
  SHA-256
  `270d80f56034c44a86929d4f41b3e18c694ce0036e0f0d1bd08de305bf26ae1a`.
- The native result applies to the exact four frozen substantive
  product/core-test hashes above. The 489-test result is the final complete
  Python-suite result for the current lifecycle/publication candidate. After
  that result, evidence finalization changed only this Markdown record; no
  product or test byte changed. Focused public-surface verification after this
  evidence-only mutation is sufficient and is required before staging.
- Native Windows verification is not rerun because both the Windows product and
  core-test files remain frozen at the exact verified hashes.
- Earlier native failures, lower assertion-count passes, and earlier WSL runs
  belong only to prior candidate revisions and are not current final
  implementation evidence.
- This section is the final planned content mutation before publication-candidate
  verification. Git history and the owner-facing publication report preserve
  the resulting execution and publication identities without a prospective
  claim or an unnecessary follow-up mutation.

## Candidate Boundary

- Synthetic temporary roots only were exercised. No future approved live
  traversal or capacity collection was run. No subject-file content, credential
  or browser/password-manager store, protected reference, network or mapped
  volume, legacy archive, or homelab system was accessed.
- Publication-candidate inspection must show only the owner-authorized
  eleven-path boundary; `docs/infrastructure-snapshot.md` must remain
  content-identical, and deliberate staging must include only those exact paths.
- Duplicate groups remain metadata-only candidates based on size and normalized
  filename. The local owner report may contain local names. The sanitized output
  exposes explicit aggregates, report-local candidate cross-references, bounded
  reason codes, and explicit limitations only. No hosted-AI call or persistent
  program-managed report exists.
- Publication uses the minimum truthful commit sequence. This record does not
  guess its containing commit identity; Git history and final local/remote
  alignment own the immutable publication identity.
