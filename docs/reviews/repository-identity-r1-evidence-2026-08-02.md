# R1 Repository Identity and Public/Private Boundary Evidence

**Opened:** 2026-08-02
**Final correction cycle 2:** 2026-08-04
**Risk tier:** Tier 3
**Base:** `d8a0f0d319c80b9c63258b737b20c6eb538ee289`
**Candidate:** Final corrected, unstaged, and uncommitted local candidate; one
fresh adversarial review and owner acceptance pending

## Accepted Checkpoint Brief

- **Why:** Present delivered engineering capability clearly while removing
  unnecessary public operational intelligence and preparing a truthful future
  repository identity.
- **Risk tier:** Tier 3 because public identity, privacy, canonical state, and a
  later irreversible external rename are involved.
- **Exact scope:** Only the existing, new, renamed, removed, test, and
  generator-owned paths in Section 11 of the accepted R1 design.
- **Exclusions:** No network, GitHub action, staging, commit, ref or remote
  mutation, repository or checkout rename, metadata/settings write, social
  preview, private repository, history rewrite, dependency/configuration or
  infrastructure change, deployment, S1, F2, or F3.
- **Authority established:** Owner-authorized bounded local implementation,
  correction, and verification only. Acceptance, publication, deployment, and
  every external write remain unestablished.
- **Protected boundaries:** No credential or secret-value access, protected
  reference selection or mutation, live systems, personal School Learning data,
  generated-file hand editing, unrelated paths, or existing user changes.
- **Observable result:** A public-safe candidate coherent under the current
  repository identity while the accepted future identity remains prospective.
- **Verification:** Focused context and privacy tests, path-only local scans,
  registered generation, one final full native suite after the last mutation,
  final Atlas checks, and fresh adversarial independent re-review.
- **Stop conditions:** The accepted design's scope, privacy, secret,
  integration, history, old-identity compatibility, verification, and shared
  anti-loop stops apply.
- **Next decision boundary:** Fresh read-only adversarial re-review of the exact
  corrected candidate, then owner acceptance or a bounded stop.

## Baseline, Identity, and Environment

The correction baseline was observed from
`/home/aidenm727/src/t430-homelab` on branch `main`. `HEAD`, local
`main`, and the locally observed `origin/main` were all
`d8a0f0d319c80b9c63258b737b20c6eb538ee289`; divergence was 0/0 and
nothing was staged. The 44 reviewed candidate paths and statuses were present
before correction. Atlas was Valid and Synchronized, W1 was published, and R1
alone was selected.

The independent review recorded fingerprint
`sha256:5a5a7e003cf06f00265d0a7a6e2c089ce4c5a4c99c5e006f915cae00e3587d91`.
Its construction method was not recorded, so the exact digest was not
independently reproducible. The base identity and complete reviewed path/status
set did match; no material baseline discrepancy was observed.

The native environment supplied Python 3.10.12, Git 2.34.1, Bash 5.1.16,
ripgrep 15.2.0, `file` 5.41, GNU strings 2.38, and GNU tar 1.34. Dedicated
secret scanners, PDF extraction, OCR, image-metadata tooling, and general
archive utilities were unavailable and were not installed.

The ordinary sandbox made `/tmp` read-only. An ignored checkout-local
temporary root allowed command startup but caused the dirty outer repository
to affect a deliberate non-repository context test. An owner-approved
task-specific external temporary root was therefore used inside a bubblewrap
sandbox with the host filesystem read-only and networking unshared. The same
synthetic root was mounted at `/var/tmp` for School Learning tests that
explicitly allocate there. No live or personal data root was used.

## Exact Candidate Inventory

The corrected candidate contains 45 paths: 26 changed existing paths, four
renames represented by eight working-tree paths, nine removals, and two new
paths.

### Changed Existing Paths

- `README.md`
- `docs/aiden-context.md`
- `docs/architecture/compute.md`
- `docs/architecture/repository.md`
- `docs/architecture/task-scoped-agent-context-compilation.md`
- `docs/changes.log`
- `docs/changes/2026-06-23-add-nvme-proxmox-storage-pool.yml`
- `docs/changes/2026-06-23-context-system-v1.yml`
- `docs/changes/2026-06-23-improve-change-capture-workflow.yml`
- `docs/changes/2026-06-24-refine-infrastructure-documentation-structure.yml`
- `docs/current-mission.md`
- `docs/current-state.json`
- `docs/docs-map.md`
- `docs/infrastructure-snapshot.md`
- `docs/infrastructure.md`
- `docs/services.md`
- `tests/test_context_materialization.py`
- `tests/test_context_selection.py`
- `tests/test_context_selectors.py`
- `tests/test_context_snapshot.py`
- `tools/atlas/platform/context_compilation/materialization.py`
- `tools/atlas/platform/context_compilation/snapshot.py`
- `tools/atlas/platform/discovery.py`
- `tools/atlas/platform/document_definitions.py`
- `tools/atlas/platform/reasoning/context_selection.py`
- `tools/generate-context.py`

### Renamed Paths

- `docs/infrastructure-gamer-pve.md` to
  `docs/infrastructure-virtualization.md`
- `docs/changes/2026-06-24-add-gamer-pve-node-monitoring.yml` to
  `docs/changes/2026-06-24-add-virtualization-host-node-monitoring.yml`
- `docs/changes/2026-06-24-add-tailscale-remote-management-for-gamer-pve.yml`
  to
  `docs/changes/2026-06-24-add-tailscale-remote-management-for-virtualization-host.yml`
- `docs/changes/2026-06-24-deploy-immich-on-gamer-pve.yml` to
  `docs/changes/2026-06-24-deploy-immich-on-virtualization-host.yml`

### Removed Paths

- `docs/aiden-context-spec.md`
- `docs/archive/Homelab_Docker_Installation_Summary.pdf`
- `docs/archive/Homelab_Maintenance_Summary.pdf`
- `docs/archive/Homelab_Status_Summary.pdf`
- `docs/archive/T430_Homelab_Setup_Recap.pdf`
- `docs/images/grafana.png`
- `docs/images/homepage.png`
- `docs/images/kuma.png`
- `docs/images/physical.jpg`

### New Paths

- `docs/reviews/repository-identity-r1-evidence-2026-08-02.md`
- `tests/test_public_surface.py`

Correction cycle 1 changed 11 paths relative to the reviewed candidate:
`docs/aiden-context.md`, `docs/docs-map.md`,
`docs/infrastructure-snapshot.md`, `docs/infrastructure.md`,
`docs/infrastructure-virtualization.md`,
`docs/reviews/repository-identity-r1-evidence-2026-08-02.md`,
`docs/services.md`, `tests/test_context_selectors.py`,
`tests/test_public_surface.py`,
`tools/atlas/platform/document_definitions.py`, and
`tools/generate-context.py`.

Final correction cycle 2 began from that exact unchanged 45-path candidate:
26 modified, 13 deleted, and 6 untracked paths, all inside the accepted
46-path Section 11 boundary. The accepted-but-unchanged path remained the
existing task-context fixture. Cycle 2 was authorized to modify exactly:

- `tests/test_context_selectors.py`
- `tests/test_public_surface.py`
- `docs/reviews/repository-identity-r1-evidence-2026-08-02.md`

No other repository path is part of correction cycle 2.

## Initial Verification and Independent Review

The initial evidence record made generic verification claims but retained no
exact command, count, runtime, or failure anchors. Those initial results are
therefore not reconstructible and are not repeated as established facts.

The independent review dated 2026-08-04 returned
`C. CORRECTION REQUIRED` and recorded five blocking findings:

1. the B1a snapshot capability-boundary test failed after the separately
   authorized R1 path expansion;
2. the internal-URL privacy gate used an overbroad overlay approximation,
   defective hostname suffix boundaries, and whole-file dispositions;
3. this evidence record lacked exact inventory and command/result anchors and
   overstated verification;
4. generated ownership omitted the structured change-record input set and the
   wall-clock generation date was not governed;
5. canonical and generated candidate files contained trailing whitespace.

At correction baseline, this exact isolated command reproduced finding 1:

```bash
TMPDIR=<task-temp> PYTHONPATH=tools PYTHONDONTWRITEBYTECODE=1 \
python3 -m unittest \
  tests.test_context_selectors.SelectorCapabilityBoundaryTests.test_b1a_snapshot_boundary_files_match_the_authorization_baseline
```

Result: 1 test, 1 assertion failure, 0 skips, exit 1. The failure named only
`tests/test_context_snapshot.py` and
`tools/atlas/platform/context_compilation/snapshot.py`.

## Correction Cycle 1

### Historical Capability Boundary

Cycle 1 pinned the two later-authorized snapshot paths and their candidate blob
identities. The second adversarial review determined that its R1 Git pathspec
contained only those two paths, so it could not observe a change to one of the
other four paths in the complete historical B1a boundary. This finding remained
blocking after cycle 1.

The corrected isolated command ran 1 test in 0.031 seconds with 0 skips and
exit 0.

### Public-Surface Privacy Gate

Cycle 1 made the gate parse URL hostnames, detect exactly the standards-defined shared
overlay range rather than all addresses with the same first octet, handles
suffixes at hostname boundaries independently of port or path, and reports
findings only as paths and line numbers. Historical hostname, internal-URL, and
absolute-path dispositions are line/count scoped. The second adversarial review
nevertheless found that the repository-level IP, hostname, internal-URL, and
high-confidence-secret scans still excluded the complete privacy-test source.
This finding remained blocking after cycle 1.

Negative coverage proves that a public hostname containing a private-looking
substring passes, a private-suffix hostname and a true overlay URL fail, and a
new internal URL in an otherwise disposed historical file remains visible.

Protected historical operational-path findings remain scanned and are disposed
without copying literals. The path-only dispositions are:

- `docs/reviews/ai-capability-landscape-work-research-2026-07-14.md`
- `docs/reviews/aiden-ai-environment-baseline-v1-2026-07-20.md`
- `docs/reviews/engineering-workflow-v1-1-evidence-2026-08-01.md`

The corrected exact URL semantics found no actual protected historical internal
URL; the prior two broad-`100.*` file findings were false positives.

After generation, this command passed 16 tests in 0.209 seconds with 0 skips
and exit 0:

```bash
TMPDIR=<task-temp> PYTHONPATH=tools PYTHONDONTWRITEBYTECODE=1 \
python3 -m unittest tests.test_public_surface
```

The suite scans all present tracked and untracked UTF-8 candidate files, while
binary files are inventoried by suffix and NUL detection.

### Generated Ownership and Date

`docs/aiden-context.md` is registered as generated from:

- `docs/current-state.json`
- `docs/current-mission.md`
- `docs/infrastructure-snapshot.md`
- `docs/changes`, whose precise generator input set is its `*.yml` records

`docs/infrastructure-snapshot.md` remains registered from the three public
infrastructure owners. Focused coverage loads the generator without executing
it, compares its declared inputs exactly with Atlas metadata, checks the
structured-record set, and requires the rendered source graph in the artifact.
Atlas validates the directory owner locally.

The `Generated:` date is deterministic: it is
`docs/current-state.json.freshness.effective_date`, currently 2026-08-02, not
wall-clock time. Registered generation used only:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 tools/generate-context.py
```

Result: exit 0. Before/after path hashing showed that only
`docs/aiden-context.md` and `docs/infrastructure-snapshot.md` changed.

### Whitespace

Trailing whitespace was removed from the three canonical public infrastructure
owners and the generated outputs were rebuilt. A candidate-path-complete check
over the union of tracked changes and untracked files reported only this
evidence record's former header lines immediately before its replacement.
`git diff --check` and the same path/line-only candidate scan are rerun after
this record update.

## Second Adversarial Review and Final Correction Cycle 2

The second adversarial review dated 2026-08-04 returned
`C. CORRECTION REQUIRED`. It preserved two blocking product findings:

1. the historical invariant did not observe all six B1a paths; and
2. four repository-level privacy checks excluded the complete privacy-test
   source.

It also found that the correction-cycle-1 fingerprint lacked exact byte
framing and therefore was not reproducible, and that the stale-current-identity
evidence count was 16 rather than 15. Generated ownership, deterministic
generation, whitespace, the public privacy content, README behavior, and the
45-path candidate boundary remained resolved.

Final correction cycle 2 resolves the historical invariant over this complete
six-path B1a set:

- `docs/task-context/index.md`
- `tests/test_context_snapshot.py`
- `tools/atlas/platform/context_compilation/__init__.py`
- `tools/atlas/platform/context_compilation/digests.py`
- `tools/atlas/platform/context_compilation/models.py`
- `tools/atlas/platform/context_compilation/snapshot.py`

The invariant compares the accepted R1 base with the candidate across all six
paths. It requires exactly the two snapshot paths to have modified status,
requires the other four to remain unchanged, and pins the corrected Git blob
identities of both authorized paths. Negative cases cover each of the four
unauthorized boundary paths, deletion of either authorized path, and a content
rewrite of either authorized path.

The privacy gate now scans `tests/test_public_surface.py` itself for IP
literals, internal URLs, historical private-host forms, high-confidence secret
patterns, and the current-identity literal. Intentional fixtures are accepted
only by exact match class, exact test function or module scope, exact line,
SHA-256 of the exact literal, and exact expected count. A new literal, a moved
literal, a duplicate, or an extra match in an already disposed test or line is
not covered. Negative cases prove that an added internal URL in the same test
and line and an added plausible secret in the same test and line remain
findings. Protected historical evidence remains scanned under narrow
path/line/count dispositions. Failure output contains paths and line numbers,
never suspected values.

Focused pre-final results before this evidence update were:

- isolated complete historical invariant: 1 test, pass, 0 skips, 0.009 seconds,
  exit 0;
- all `tests.test_context_selectors`: 62 tests, pass, 0 skips, 0.920 seconds,
  exit 0;
- affected selectors/snapshot/materialization/selection group: 153 tests,
  pass, 1 documented skip, 32.918 seconds, exit 0;
- complete public-surface suite: 18 tests, pass, 0 skips, 0.265 seconds,
  exit 0; and
- independent path/line-only scan: 212 present UTF-8 candidate files,
  privacy-test source included, zero findings, exit 0.

The fresh current-identity scan found exactly 16 non-self paths, equal to the
declared compatibility, fixture, test, and dated-evidence allowlist. The exact
intentional current-identity literal in the privacy-test source was scanned and
narrowly dispositioned; it is not included in the 16-path evidence count. No
stale active reference was found.

## Candidate Fingerprint V2 Specification

The only authoritative candidate-fingerprint serialization for the final
cycle-2 candidate is `AIDEN-R1-CANDIDATE-FINGERPRINT-V2`. Earlier recorded
fingerprints `sha256:5a5a7e003cf06f00265d0a7a6e2c089ce4c5a4c99c5e006f915cae00e3587d91`
and `sha256:b9e059540e4d2ad02df15f1f9ea923f4b52a93039a7b04d142f519d1870ced5a`
are explicitly non-authoritative because their exact serializations were not
recorded and could not be independently reproduced.

### Inputs

The repository root is the current Git worktree. The base commit is the
lowercase 40-character ASCII output, excluding the command's terminating
newline, of:

```bash
git rev-parse --verify HEAD^{commit}
```

The tracked-diff bytes are the exact stdout bytes of:

```bash
LC_ALL=C git \
  -c color.ui=false \
  -c core.quotepath=false \
  diff \
  --binary \
  --full-index \
  --no-ext-diff \
  --no-textconv \
  HEAD --
```

The untracked-path bytes are the NUL-delimited stdout bytes of:

```bash
LC_ALL=C git \
  -c core.quotepath=false \
  ls-files \
  --others \
  --exclude-standard \
  -z
```

Split that output on NUL, discard the final empty item, and sort the paths by
raw byte value in ascending lexicographic order. For each untracked path, use
the path bytes exactly as emitted by Git and require the path to resolve inside
the repository. Classify its Git mode as `100644` for a regular file with no
execute bit, `100755` for a regular file with any execute bit, or `120000` for
a symbolic link; otherwise stop. Content bytes are the exact file bytes for a
regular file and the exact link-target bytes from `os.readlink()` encoded with
`os.fsencode()` for a symbolic link. The content digest is lowercase ASCII
SHA-256 hexadecimal, exactly 64 bytes.

### Serialized Byte Stream

Concatenate these bytes in this exact order:

1. literal ASCII `AIDEN-R1-CANDIDATE-FINGERPRINT-V2`;
2. one NUL byte;
3. base-commit ASCII bytes;
4. one NUL byte;
5. literal ASCII `TRACKED-DIFF`;
6. one NUL byte;
7. decimal ASCII byte length of the tracked diff;
8. one NUL byte;
9. exact tracked-diff bytes;
10. one NUL byte;
11. literal ASCII `UNTRACKED`;
12. one NUL byte;
13. decimal ASCII count of sorted untracked paths;
14. one NUL byte;
15. for each sorted untracked path, concatenate:
    - literal ASCII `PATH`;
    - NUL;
    - decimal ASCII byte length of the path;
    - NUL;
    - exact path bytes;
    - NUL;
    - literal ASCII `MODE`;
    - NUL;
    - six ASCII Git-mode bytes;
    - NUL;
    - literal ASCII `SHA256`;
    - NUL;
    - 64 lowercase ASCII hexadecimal digest bytes;
    - NUL;
16. literal ASCII `END`; and
17. one final NUL byte.

The candidate fingerprint is lowercase hexadecimal SHA-256 of the complete
serialized byte stream, prefixed in reports with `sha256:`. Reproduction code
is ephemeral under the authorized task-specific temporary root and is not a
repository artifact.

The final fingerprint and the post-last-mutation full-suite result belong in
the stable correction-cycle-2 attestation. Embedding the candidate fingerprint
inside this untracked evidence file, which itself participates in the
fingerprint, would be self-referential. No final V2 digest or prospective final
suite result is recorded here.

## Scan Record

All scans are local and emit no matched content.

- **Privacy:** the 18-test public-surface suite checks address literals,
  exact internal URLs, historical hostnames, active raw private fields,
  operational absolute paths, provider identifiers, and the current/future
  repository-identity boundary, including its own source under exact narrow
  dispositions. Result before the evidence update: pass.
- **Stale identity:** 16 non-self present paths contain the current repository
  slug; all are current compatibility, dated evidence, fixtures, or explicit
  tests. The self literal is scanned under its exact narrow disposition. No
  stale active reference was found.
- **Archives and images:** an extension inventory of all present tracked and
  untracked files returned zero paths; all accepted PDF and image removals were
  absent.
- **Candidate secrets:** high-confidence private-key-header and provider-token
  pattern classes are mandatory failures in the public-surface suite. Result:
  zero path/line findings.
- **Reachable-main secrets:** the same high-confidence classes were scanned
  path-only across commits reachable from local `main`; zero paths were
  returned. Protected references were not selected or traversed.
- **Generated ownership:** focused tests, Atlas validation, Atlas
  synchronization, and before/after generation hashing agreed.
- **Whitespace:** only paths and line numbers are emitted; final result follows
  the evidence update.

No plausible real secret was found. Dedicated unavailable tools were not
silently substituted with claims they could uniquely establish. Removed
binaries were not opened, parsed, OCR-processed, or replaced.

## Focused and Broad Verification

The affected context command was:

```bash
TMPDIR=<task-temp> PYTHONPATH=tools PYTHONDONTWRITEBYTECODE=1 \
python3 -m unittest -q \
  tests.test_context_selectors \
  tests.test_context_snapshot \
  tests.test_context_materialization \
  tests.test_context_selection
```

An ignored checkout-local temporary root produced 152 tests with 1 skip and 1
environment error because a deliberate non-repository target inherited the
dirty outer checkout. Under the accepted external root and network-isolated
sandbox, the same 152 tests passed with 1 skip in 32.381 seconds, exit 0.

The first pre-evidence complete-suite rehearsal reached 425 tests with 1 skip
and 74 environment errors because `/var/tmp` was read-only. With the same
synthetic task root also mounted at that required path, this inner native
command passed:

```bash
TMPDIR=<task-temp> \
PYTHONPATH=tools \
PYTHONDONTWRITEBYTECODE=1 \
python3 -m unittest discover -s tests -p 'test_*.py'
```

Result: 425 tests, 1 skip, 37.641 seconds reported by unittest, exit 0. This is
pre-evidence broad verification, not the authoritative last-mutation run.

Focused pre-evidence Atlas results were Valid with 0 errors and 0 warnings, and
Synchronized with the generated context input set including `docs/changes`.

## Final Verification Boundary

This evidence update is the last repository mutation in correction cycle 2.
The exact authorized final sequence is one full native suite, followed without
repository mutation by the isolated historical invariant, complete
public-surface suite, independent path/line-only privacy and exact stale-
identity scans, whitespace and candidate-boundary checks, clean-room generated
comparison, Atlas checks, and two independent V2 computations. Their exact
results form the stable correction-cycle-2 attestation; recording them here
afterward would violate the no-post-suite-mutation rule.

## Lifecycle and Pending Work

W1 remains published. R1 alone remains selected, unstaged, uncommitted,
unaccepted, unpublished, unrenamed, undeployed, and non-operational. Final
correction cycle 2 is complete only when its post-last-mutation verification
and stable attestation pass. One final fresh adversarial review and owner
acceptance remain pending.

GitHub preflight, stable repository identity observation, rename, settings and
metadata changes, publication, controlled external-reference updates, and
social-preview creation, review, and upload are pending. No external authority
or action is established by this record. S1, F2, and F3 remain unselected.
