# Aiden Context

Generated: 2026-07-16

## Purpose

This file is an AI-readable context packet for the Aiden Platform engineering repository.

It summarizes the canonical current mission, infrastructure state, recent changes, and operating rules so a human or AI collaborator can establish accurate engineering context.

## Current Mission

### Phase

Task-Scoped Agent Context Compilation Checkpoint B1a Implementation

---

### Mission State

The owner accepted the revised EO-2026-013 B1 plan and authorized Checkpoint B1a — Immutable Snapshot Boundary on July 16, 2026.

The authorization is recorded in `docs/reviews/eo-2026-013-b1a-authorization-review-2026-07-16.md` against Checkpoint A.1 completion commit `f0ae21a34d525e6f4ce4c7b50790779e664138c4`.

Checkpoint B1a may create exactly two files and modify exactly four existing files. It establishes the trusted immutable Git snapshot boundary only. It does not parse repository content or produce a selection plan.

Checkpoint B1b and Checkpoint B2 remain explicitly unauthorized.

The protected branch `wip/distinctness-foundation-calibration` remains unchanged at `fcbc5957b89fe65a4313a3c23eb814e02a014698`. Its content is out of scope. B1a may compare only the exact declared protected-ref name and exact object identity. It may not inspect, peel, traverse, read, select, expose, or modify the protected object or its content.

EO-2026-013 and all 21 Engineering Opportunities remain `reviewed`.

---

### Mission Intent

Establish the deterministic immutable repository boundary required before content parsing or selection reasoning begins.

Checkpoint B1a verifies an explicit clean local repository target, bounded repository identity, one exact full SHA-1 commit, root tree, object format, snapshot fingerprint, exact regular-file blob lookup, and content-blind protected-ref identity matching.

The checkpoint must keep Git execution isolated from ambient repository, worktree, index, object-store, replacement, alternate, lazy-fetch, injected-configuration, locale, pathspec, network, and write effects.

Checkpoint B1a returns for owner review before B1b begins.

Repository Synchronization Reasoning remains the deterministic check for alignment between this mission, the accepted B1a review, canonical architecture, generated context, repository metadata, and the exact B1a authorization boundary.

---

### Current Focus

- Implement an explicit target-repository snapshot adapter.
- Accept only an exact full lowercase 40-character SHA-1 commit identifier.
- Verify repository identity against the bounded accepted GitHub origin forms.
- Verify a non-bare clean target before and after every snapshot operation.
- Reject replacement refs, grafts, object alternates, injected Git-control state, and lazy object fetching.
- Verify SHA-1 object format, exact commit identity, and exact root tree.
- Add a repository-owned `snapshot_fingerprint` digest helper with the accepted canonical surface.
- Normalize exact repository paths without rewriting case or Unicode.
- Read only exact regular blob objects from the immutable tree.
- Reject symlinks, gitlinks, trees, unsupported modes, missing paths, and ambiguous paths.
- Compare only the exact protected-ref name and object identity.
- Prove no protected object content, network, target write, parsing, selection, B1b, or B2 behavior occurs.
- Create and modify only the exact six B1a implementation paths.
- Run all tests and Atlas verification.
- Return for owner acceptance before B1b.

---

### Initial Milestone

Implement and verify Checkpoint B1a — Immutable Snapshot Boundary.

#### Included

- `tools/atlas/platform/context_compilation/snapshot.py`.
- `tests/test_context_snapshot.py`.
- Bounded snapshot documentation in `docs/task-context/index.md`.
- Public snapshot exports in `tools/atlas/platform/context_compilation/__init__.py`.
- Deeply immutable snapshot and blob models in `tools/atlas/platform/context_compilation/models.py`.
- Named snapshot-fingerprint helper in `tools/atlas/platform/context_compilation/digests.py`.
- Explicit clean target path.
- Bounded repository identity normalization.
- Full-SHA commit-only requested-revision support.
- SHA-1 object-format enforcement.
- Exact commit and root-tree verification.
- Sanitized content-blind Git object plumbing.
- Exact path and regular-blob reads.
- Symlink and gitlink rejection.
- Protected-ref exact name and identity comparison only.
- Full test and Atlas verification.
- Return to owner review before B1b.

#### Excluded

- Checkpoint B1b.
- Checkpoint B2.
- YAML parsing.
- Markdown heading parsing.
- Relationship verification.
- Source selection or candidate discovery.
- Directory, object, edge, or graph scans.
- Selected-source, omission, unknown, freshness, or conflict records.
- Source-content or payload digests.
- Payload materialization.
- Budget application.
- Package construction or integrity.
- Explanations or package fixtures.
- Atlas commands.
- Generic discovery.
- Dependencies.
- Canonical architecture changes.
- Engineering Opportunity lifecycle changes.
- Task-contract implementation, execution, autonomy, provider routing, or AI-environment changes.
- Protected object or content access.

---

### Preserved Downstream Follow-Up — AI Engineering Environment Review

A subsequent bounded AI Engineering Environment Review is preserved. The actual AI working environments have not been systematically reviewed recently, but this larger review follows the EO-2026-013 architecture design and requires its own bounded owner authorization.

The future review includes:

- ChatGPT Project instructions.
- ChatGPT Project source files and their freshness.
- Project settings, memory, and Library configuration.
- Model and reasoning workflow conventions.
- Connectors, tools, skills, and permissions.
- Codex CLI configuration and launch workflow.
- Repository instructions and reusable skills.
- Generated context delivery and refresh behavior.
- Duplicated or conflicting instructions across repository documentation, ChatGPT Projects, Codex, continuity packets, and fresh-chat openers.
- Other current or future assistant environments.

Each surface should be classified as Current and useful, Stale, Redundant, Conflicting, Missing, Unused, Poorly owned, or Not verifiable. The review should record its authoritative source, intended consumer, owner, freshness expectation, update mechanism, and evidence for retaining, changing, consolidating, or removing it.

The review may use multiple AI systems only through a structured pattern:

- Atlas and the repository provide deterministic source truth.
- Codex may collect inventory and perform later bounded repository changes.
- ChatGPT may perform primary architectural analysis and synthesis.
- An independent challenger model may review the same evidence package.
- Findings must separate agreement, disagreement, unsupported speculation, immediate corrections, later opportunities, and items that should remain unchanged.
- The owner resolves disagreements and authorizes application.

Portfolio treatment remains:

- EO-2026-008 — AI Engineering Excellence is the umbrella direction.
- EO-2026-007 — AI Collaboration Intelligence covers collaboration reliability.
- EO-2026-019 — Instruction and Context Effectiveness Evaluation covers effectiveness testing.
- EO-2026-013 provides deterministic task context and consumer boundaries.
- EO-2026-009 provides the longer-term shared personal AI context direction.
- The review is a future bounded deliverable under these existing directions.
- No new Engineering Opportunity should be created unless later evidence demonstrates a distinct recurring capability boundary.

The review is not part of the first EO-2026-013 milestone. It does not authorize live configuration cleanup or changes.

---

### Completion History

#### EO-2026-013 Revised B1 Plan and Checkpoint B1a Authorization

- Revised B1 plan accepted by the owner on July 16, 2026.
- Checkpoint B1 was split into B1a — Immutable Snapshot Boundary and B1b — Deterministic Selectors and Selection Plan.
- Checkpoint B1a authorized with an exact two-created and four-modified implementation scope.
- Checkpoint B1b and Checkpoint B2 remain unauthorized.
- Repository identity, clean state, Git environment isolation, exact commit and tree resolution, snapshot fingerprint, exact regular-blob access, and protected-ref identity matching are owned by B1a.
- YAML and Markdown parsing, relationship verification, source selection, omissions, unknowns, and selection-plan production remain withheld for B1b.
- Protected branch content remains out of scope.
- Only exact protected-ref name and object-identity comparison is authorized.
- EO-2026-013 and all 21 Engineering Opportunities remain `reviewed`.


#### EO-2026-013 Checkpoint A.1 — Executable-Policy Contract Correction

- Completion accepted by the owner on July 16, 2026.
- Recording, commit, and push authorized.
- Authorization baseline: `1f2595b8a3489979b275dfad0884b4e0fe09c585`.
- Exact implementation scope: ten modified existing files and no created or deleted files.
- Selection-policy instance advanced to `1.0.1`.
- Budget-policy instance preserved at `1.0.0`.
- All five first-replay rules gained explicit digest-bound budget tiers and `public` source sensitivity.
- Selection-policy digest changed from `708b6c73208db65dc94fcd89d1810666048895821b2e6e0feef5aa6b9ccf5448` to `69577722ea4eb6f479424f3bf324866cc2992d5df82b3224e5f20571ef081938`.
- Request digest changed from `840adc1dad2347230a05720faeee71b553c802f2cef25e08232d292f02be8390` to `4839411214fa20cde0b842a72ad9baf5d525c494fca3c931cd58d63364c8c01b`.
- Package identity digest changed from `6007762250f7992a72c91e080502104cf9fa82e90ce16039a012edd7a349b9e6` to `711062df74645329c3078b575b8ddfc737a41e3b3a0a9aeaca3ea9bafcb85678`.
- Package ID changed from `tcp-6007762250f7992a72c91e08` to `tcp-711062df74645329c3078b57`.
- Ninety tests passed.
- Atlas validation was Valid, missing definitions were clean, and synchronization was Synchronized.
- Independent final acceptance review passed.
- No B1, B2, dependency, protected-branch access, lifecycle mutation, staging, commit, or push occurred before owner acceptance.
- Checkpoint B1 and Checkpoint B2 remain unauthorized.
- Protected-branch content remains out of scope.


#### EO-2026-013 Revised Executable-Path Plan Acceptance

- Revised executable-path plan accepted by the owner on July 16, 2026.
- Checkpoint A.1 — Executable-Policy Contract Correction authorized.
- Checkpoint B1 and Checkpoint B2 remain unauthorized.
- The original single Checkpoint B shape was replaced by A.1, B1, and B2 review gates.
- Source budget tier and sensitivity must become explicit, policy-owned, and digest-bound.
- The protected branch content remains out of scope.
- Only future identity comparison of the declared protected ref may be considered during a separately authorized B1 review.
- EO-2026-013 and all 21 Engineering Opportunities remain `reviewed`.


#### EO-2026-013 Checkpoint A — Deterministic Foundations

- Completion accepted by the owner on July 16, 2026.
- Completion authorization included recording, committing, and pushing Checkpoint A.
- Exact implementation scope: 18 created files and 2 registration-only existing-file modifications.
- Four stable schema URNs replaced an unowned HTTPS namespace.
- Policy and request foundation digests remained unchanged.
- Typed values are deeply immutable at construction boundaries.
- Local validators enforce the accepted portable-schema boundaries and documented cross-field rules.
- Restricted canonical JSON remains standard-library-only and rejects floating point.
- Independent final acceptance review passed.
- Eighty-three tests passed.
- Atlas validation was Valid, missing definitions were clean, and synchronization was Synchronized.
- No third-party dependency, Checkpoint B path, Atlas command, lifecycle mutation, AI-environment change, staging, commit, or push occurred before owner acceptance.
- Checkpoint B remains explicitly unauthorized.
- The protected branch remained unchanged and out of scope.


#### EO-2026-013 Reconciled Implementation Plan Acceptance

- Reconciled implementation plan accepted by the owner on July 16, 2026.
- Checkpoint A — Deterministic Foundations authorized.
- Checkpoint B — Executable Compilation Path remains withheld.
- External implementation-readiness research and constrained independent challenge evidence were reconciled into the accepted plan.
- No Engineering Opportunity lifecycle state changed.
- No implementation was performed by the acceptance decision itself.
- The protected branch remained unchanged and out of scope.


#### EO-2026-013 Task-Scoped Agent Context Compilation Architecture

- Architecture completion accepted by the owner on July 15, 2026.
- Architecture commit: `2de09693ed1c922500477c5ba1c6903513ab4dd3` (`Define task-scoped context compilation architecture`).
- Canonical architecture: `docs/architecture/task-scoped-agent-context-compilation.md`.
- The architecture defines deterministic task authority, source selection, ordering, provenance, freshness, conflicts, unknowns, omissions, UTF-8 byte budgeting, digest surfaces, validation invariants, and consumer boundaries.
- One bounded, manually assembled, informative, non-executable example records five accepted sources and exact selector behavior without claiming compiler or validator execution.
- Human review corrections were incorporated before the guarded architecture commit.
- The guarded committed run preserved evidence that all 43 tests passed.
- Atlas validation was Valid, missing definitions were clean, and synchronization was Synchronized.
- Engineering Review's generic `Unknown / Low` result was non-blocking because no specialized milestone reasoning rule exists or is required.
- EO-2026-013 and all 21 Engineering Opportunities remained `reviewed`.
- No compiler, selector, validator, policy, fixture, lifecycle, Atlas command, Atlas reasoning, agent behavior, or AI-environment configuration change was introduced.
- The protected branch remained unchanged at `fcbc5957b89fe65a4313a3c23eb814e02a014698`.

#### Canonical Knowledge Promotion Workflow Operationalization

- Completion accepted by the owner on July 15, 2026.
- Completion commit: `11d355809a07bf0721e86f9234ba8d2f57ecf9e1` (`Operationalize canonical knowledge promotion workflow`).
- Clean-state validation exists for the committed checkpoint.
- The reusable human-reviewed operating procedure is documented in `docs/knowledge-promotion.md`.
- The first bounded manual flow and its traceability evidence are preserved in `docs/reviews/knowledge-promotion-pilot-engineering-validation-2026-07-15.md`.
- The exact Validation Gate Standard was accepted by the owner and separately applied to `docs/standards/engineering-collaboration.md`.
- The guarded committed run preserved evidence that all 43 tests passed.
- Atlas validation was Valid, missing definitions were clean, and synchronization was Synchronized.
- Engineering Review's Unknown/Low milestone result was non-blocking because no specialized milestone reasoning rule exists or is required.
- EO-2026-020 remained reviewed.
- No new Repository Object type, automatic promotion, or authority expansion was introduced.
- The protected Distinctness calibration branch remained unchanged at `fcbc5957b89fe65a4313a3c23eb814e02a014698`.

---

### Recently Completed

- Established the canonical Aiden Platform Vision and layered capability architecture.
- Completed and accepted the Engineering Opportunity portfolio recalibration.
- Transitioned all 21 Engineering Opportunity Objects to `reviewed`.
- Established the AI Operating Model Architecture.
- Established the Knowledge Authority Architecture and documented the Canonical Knowledge Promotion Workflow.
- Established the dated Current AI Operating Baseline for July 14, 2026.
- Verified the account-level training control and Aiden Platform Project memory configuration.
- Completed the Aiden Platform architecture and repository-engineering evaluation.
- Completed Evaluation 2 using a naturally occurring G14 touchpad I2C initialization failure, overnight persistence evidence, normal-restart recovery, and an uncertainty-calibrated operational follow-up.
- Completed the current-information research evaluation and first ChatGPT Work pilot.
- Completed the difficult AI and computer-science learning evaluation with demonstrated transfer.
- Completed the bounded Codex repository-integration pilot with exact scope and deterministic verification.
- Completed the Claude Free independent-provider comparison and retained it as an occasional bounded audit lane.
- Completed the Initial AI Workflow Evaluation Cycle on July 15, 2026.
- Adopted the final operating stack while deferring additional subscriptions, API spending, automatic routing, local AI, and broad agent authority.
- Preserved the laptop reliability issue as operational follow-up rather than a blocker on the completed AI cycle.
- Completed the Canonical Knowledge Promotion Workflow Operationalization mission and obtained owner acceptance on July 15, 2026.
- Completed the EO-2026-013 Task-Scoped Agent Context Compilation architecture milestone and obtained owner acceptance on July 15, 2026.

---

### Current Non-Priorities

- Beginning Checkpoint B1b or Checkpoint B2.
- Modifying any path outside the exact six B1a implementation paths.
- Accepting branch names, tags, abbreviated object IDs, revision expressions, reflog syntax, or non-commit objects as requested revisions.
- Reading selected content from the target worktree.
- Reading, peeling, traversing, selecting, or exposing protected-object content.
- Checkout, switching, merge, ref mutation, target-repository writes, or network access.
- YAML parsing or Markdown heading selection.
- Historical relationship verification.
- Source selection, candidate discovery, omissions, unknowns, freshness, conflicts, or selection plans.
- Payload materialization or budget execution.
- Package compilation, package integrity, explanations, or golden replay.
- Atlas commands or generic structured-resource discovery.
- Third-party dependencies.
- Canonical architecture changes.
- Engineering Opportunity lifecycle mutation.
- Task-contract implementation, execution, autonomy, provider routing, or AI-environment changes.
- Implementing Structured Research Orchestration inside EO-2026-013.
- Resuming or merging the Distinctness implementation.

---

### Current Status

EO-2026-013 Checkpoint A and Checkpoint A.1 are complete and owner-accepted.

The revised B1 plan is accepted. Checkpoint B1a — Immutable Snapshot Boundary is authorized within the exact two-created and four-modified scope recorded in `docs/reviews/eo-2026-013-b1a-authorization-review-2026-07-16.md`.

Checkpoint B1b and Checkpoint B2 remain unauthorized. Protected-branch content remains out of scope. EO-2026-013 and all 21 Engineering Opportunities remain `reviewed`.

---

### Next Milestone

Implement and verify Checkpoint B1a — Immutable Snapshot Boundary, then obtain owner acceptance before B1b.

No selector, selection-plan, or package-compilation implementation begins automatically from this authorization.

---

### Decision Boundary

- Human decision: Revised EO-2026-013 B1 plan accepted on July 16, 2026.
- Checkpoint A.1 completion: `f0ae21a34d525e6f4ce4c7b50790779e664138c4`.
- Checkpoint B1a authorized: Yes, exact two-created and four-modified scope.
- Checkpoint B1b authorized: No.
- Checkpoint B2 authorized: No.
- B1a created paths authorized: `snapshot.py` and `test_context_snapshot.py`.
- B1a modified paths authorized: task-context index, context-compilation exports, models, and digests.
- Requested revision boundary: exact full lowercase SHA-1 commit only.
- Initial object format: SHA-1 only.
- Target repository writes authorized: No.
- Network access authorized: No.
- Protected branch content in scope: No.
- Protected-ref exact name and object-identity comparison authorized: Yes.
- Protected object peel, traversal, content read, selection, or exposure authorized: No.
- YAML or Markdown selector work authorized: No.
- Selection reasoning authorized: No.
- Third-party dependency authorized: No.
- Canonical architecture changes authorized: No.
- Atlas command or generic discovery authorized: No.
- Engineering Opportunity lifecycle changed: No.
- EO-2026-013 lifecycle state: Reviewed.
- AI Engineering Environment Review authorized: No.
- Structured Research Orchestration implementation authorized: No.

STOP — Implement and verify Checkpoint B1a only. Do not begin B1b or B2.

## Infrastructure Snapshot

> Generated context artifact.
> Do not edit directly; update canonical infrastructure records instead.

### Production Host

t430-beast

* Role: Production services host
* OS: Ubuntu Server 24.04.4 LTS
* LAN IP: 10.0.0.136

Responsibilities:

* Pi-hole
* Traefik
* Homepage
* Grafana
* Prometheus
* Loki
* Alloy
* Uptime Kuma
* Vaultwarden
* Backup infrastructure

### Virtualization Host

gamer-pve

* Role: Proxmox virtualization host
* OS: Proxmox VE 9
* LAN IP: 10.0.0.178
* Tailscale IP: 100.80.182.80

Hardware:

* Ryzen 5 2600
* 16 GB DDR4
* RTX 4060-class GPU

Storage:

* 500 GB SSD (Proxmox OS)
* 1 TB NVMe SSD
* 2 TB SATA SSD

Purpose:

* VM hosting
* LXC hosting
* Immich
* AI experimentation
* Future workloads

### Active Workloads

#### LXC 200 - Immich

* Debian 12
* Docker Engine
* Docker Compose
* 128 GB root disk
* LAN IP: 10.0.0.132

### Active Services

* Pi-hole
* Traefik
* Homepage
* Uptime Kuma
* Grafana
* Prometheus
* Loki
* Alloy
* Vaultwarden
* Immich

## Recent Changes

- 2026-06-23 — Add NVMe Proxmox Storage Pool
- 2026-06-23 — Improve change capture workflow
- 2026-06-26 — Prototype Aiden engineering toolkit
- 2026-06-24 — Improve recent changes ordering
- 2026-06-23 — Homelab documentation and AI context system v1

## Authoritative Sources

- docs/infrastructure.md
- ~/homelab/docs/changes.log
- Git history
- Live infrastructure state

## Operational Rules

- Deploy / Configure
- Verify functionality
- Document immediately
- Commit and push from the local machine
- Never commit secrets

## Known Constraints

- t430-beast should remain the stable production services host
- gamer-pve should be used for virtualization, experimentation, and heavier workloads
- changes.log currently lives only on the server
- GitHub documentation remains the canonical public documentation source

## Active Change Session

# Homelab Change Session

Started: 2026-06-26 12:02:06

## Change Title

Prototype Aiden engineering toolkit

## Change Type

automation

## Intent
- [2026-06-26 12:02:06] Begin organizing existing repository tools into a future Aiden engineering toolkit

## Notes
- [2026-06-26 12:07:09] Updated aiden-context-loader.py to summarize engineering state instead of dumping full source documents

## Verification
- [2026-06-26 12:07:09] Ran python3 tools/aiden-context-loader.py and verified it reports git status, active change session, recent changes, architecture docs, context docs, roadmaps, tools, and next step

## Documentation Outputs
- [2026-06-26 12:07:09] Updated tools/aiden-context-loader.py as the first prototype of the Aiden engineering toolkit
