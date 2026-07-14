# Aiden Context

Generated: 2026-07-14

## Purpose

This file is an AI-readable context packet for the Aiden Platform engineering repository.

It summarizes the canonical current mission, infrastructure state, recent changes, and operating rules so a human or AI collaborator can establish accurate engineering context.

## Current Mission

### Phase

Platform Strategic Recalibration

---

### Mission

Recalibrate the existing Engineering Opportunity portfolio against the canonical Aiden Platform Vision, layered capability architecture, AI architecture, and strategic roadmap.

The immediate objective is to turn the current set of Engineering Opportunity Objects into a coherent, human-reviewed portfolio of potential platform work without losing original declarations, evidence, provenance, lifecycle state, or historical context.

This milestone should clarify which opportunities remain distinct, which overlap, which are components of broader initiatives, which are obsolete or superseded, and which should guide the next engineering phase.

---

### Current Focus

- Inventory the complete current Engineering Opportunity portfolio.
- Review each opportunity against the thirteen canonical Platform Foundation and Human Agency Domain capabilities.
- Preserve raw declared capability values while determining human-reviewed canonical alignment.
- Identify important secondary capability implications without collapsing them into the primary capability.
- Review explicit and inferred relationships among opportunities.
- Distinguish duplicate, overlapping, component, umbrella, complementary, superseded, and genuinely distinct opportunities.
- Evaluate whether each opportunity still aligns with the canonical Vision and Platform Strategy.
- Reassess the preserved Distinctness Analysis implementation against the new capability architecture.
- Produce a coherent portfolio interpretation before selecting or implementing the next capability.
- Use Repository Synchronization Reasoning, validation, Engineering Review, documentation, commit, and push to verify the completed portfolio checkpoint.

---

### Current Priorities

1. Establish the authoritative inventory of existing Engineering Opportunity Objects.
2. Review the declared capability, scope, evidence, rationale, and relationships of each opportunity.
3. Determine a human-reviewed primary canonical capability where evidence is sufficient.
4. Record important secondary capability implications separately from primary identity.
5. Identify obsolete assumptions introduced by the former flat capability model.
6. Identify likely duplicate, overlap, component, umbrella, and distinct relationships.
7. Determine whether repository schema or assessment architecture must change before portfolio decisions can be recorded safely.
8. Preserve lifecycle state unless a separate human-authorized decision explicitly changes it.
9. Evaluate the Distinctness calibration branch against the recalibrated architecture rather than merging it automatically.
10. Produce a prioritized portfolio interpretation and recommend the next bounded platform milestone.

---

### Recently Completed

- Established `docs/vision.md` as the canonical owner of platform purpose, principles, human authority, non-goals, and long-term direction.
- Established a layered Platform Architecture separating Platform Foundations from Human Agency Domains.
- Established thirteen canonical capability identities.
- Defined compatibility handling for the former nine flat capability identities.
- Clarified the boundaries among Atlas, the repository, Personal AI, AidenOS, infrastructure, services, and tools.
- Recalibrated Artificial Intelligence Architecture around Personal AI, provider independence, data sensitivity, provenance, and human authority.
- Created the dated Aiden Platform Strategy roadmap.
- Updated Repository Architecture and the Documentation Map.
- Registered the new canonical documents with Atlas.
- Updated Engineering Opportunity Capability Alignment for the new capability architecture.
- Confirmed 43 passing tests on `main`.
- Confirmed repository validation is Valid.
- Confirmed repository synchronization is Synchronized.
- Preserved the Distinctness Analysis implementation on `wip/distinctness-foundation-calibration`.
- Confirmed the preserved branch remains at `fcbc5957b89fe65a4313a3c23eb814e02a014698`.
- Completed and accepted the human-reviewed classification of all 21 Engineering Opportunity Objects.
- Recorded the decision to retain and recalibrate, rather than merge, the preserved Distinctness implementation.
- Transitioned all 21 Engineering Opportunity Objects from `captured` to `reviewed` after human acceptance, preserving their original declarations, evidence, and stable identifiers.

---

### Current Non-Priorities

- Implementing a new end-user platform capability
- Resuming Distinctness Analysis implementation before portfolio review
- Merging the Distinctness Analysis calibration branch
- Automatically rewriting Engineering Opportunity capability values
- Automatically changing Engineering Opportunity lifecycle states
- Treating shared capability identity as evidence of duplication
- Expanding Atlas reasoning without a demonstrated portfolio need
- Building Personal AI
- Building AidenOS interfaces
- Building nutrition or personal intelligence briefing applications
- Deploying new self-hosted services
- Purchasing or expanding local AI hardware
- Broad infrastructure changes
- Reorganizing the entire repository
- Implementing autonomous or multi-agent engineering
- Creating a universal opaque opportunity score

---

### Current Status

The live `main` branch is clean, valid, synchronized, and contains the canonical Platform Vision, layered capability architecture, AI architecture, Platform Strategy roadmap, and updated capability compatibility reasoning.

The Engineering Opportunity portfolio was captured before the strategic recalibration and therefore contains declarations, labels, assumptions, and relationships that may no longer align cleanly with the canonical platform model.

The portfolio must now be reviewed as repository knowledge rather than treated as a ready-made implementation queue.

The preserved Distinctness Analysis branch remains useful evidence, but it was designed against the previous capability architecture and must not be merged without recalibration.

The human-reviewed portfolio assessment is accepted and preserved as canonical evidence, and all 21 Engineering Opportunity Objects now have `reviewed` lifecycle state. The portfolio recalibration milestone is ready for final verification and mission advancement.

---

### Next Milestone

Recalibrate the Engineering Opportunity Portfolio.

Review the complete current portfolio against canonical platform architecture, preserve original repository facts, establish human-reviewed capability and relationship interpretations, and determine the highest-leverage next engineering direction.

---

### Success Criteria

The milestone is complete when:

- The complete Engineering Opportunity inventory has been verified.
- Every existing opportunity has been reviewed against the canonical Platform Vision and Platform Strategy.
- Every opportunity has a reviewed primary capability interpretation or an explicit unresolved-capability finding.
- Important secondary capability implications remain separate from primary identity.
- Raw declared capability values and original evidence remain preserved.
- No lifecycle state changes occur implicitly.
- Legacy capability assumptions are identified and handled through explicit compatibility or reviewed migration.
- Duplicate, overlap, component, umbrella, complementary, superseded, and distinct relationships are assessed where evidence supports them.
- Shared capability identity alone is not treated as duplicate evidence.
- The portfolio distinguishes platform foundations, human agency domains, systems, services, tools, and implementation ideas.
- Any required schema or assessment changes are designed before object mutation.
- The preserved Distinctness Analysis implementation is reviewed against the canonical capability model.
- A decision is recorded to retain, recalibrate, replace, or defer the preserved implementation.
- A coherent portfolio summary identifies the strongest opportunities, major dependency groups, and likely next platform milestone.
- Opportunity changes, if any, remain bounded, reviewable, and historically traceable.
- All tests pass.
- Repository validation reports Valid.
- Repository synchronization reports Synchronized.
- Engineering Review reports no blocking repository inconsistency after commit.
- The final working tree is clean.
- The Distinctness Analysis calibration branch remains unchanged unless a separately authorized decision is made.

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
