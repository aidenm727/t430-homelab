# Aiden Platform

The Aiden Platform is a personal, human-directed capability platform designed
to increase owner agency across learning, engineering, infrastructure, and
future life domains. Human judgment and consequential authority remain
owner-controlled.

This repository is the canonical engineering record for the platform. It owns
durable architecture, standards, deterministic tools, implemented capability
code, repository state, and evidence links. It does not own personal School
Learning data or prove live infrastructure state.

## Start Here

- [`docs/current-state.json`](docs/current-state.json) — strict canonical typed
  active state.
- [`docs/current-mission.md`](docs/current-mission.md) — short human-readable
  state companion and current intent.
- [`docs/docs-map.md`](docs/docs-map.md) — documentation and architecture
  navigation.
- [`docs/vision.md`](docs/vision.md) — platform purpose, principles, and human
  authority.
- [`docs/architecture/platform.md`](docs/architecture/platform.md) — platform
  structure and capability model.

Machine-readable current state wins if it disagrees with Current Mission.
Detailed completion and publication history remains available through dated
reviews and Git history.

## Primary Entrypoints

### Atlas

Atlas is the deterministic repository engineering interface:

```text
./atlas bootstrap
./atlas state
./atlas review
./atlas next
./atlas validate
./atlas sync
```

Atlas reports repository health, declared validation and synchronization scope,
working-tree observation, current phase, selected work, blockers, unknowns, and
recommended action. It does not grant task, implementation, publication,
deployment, or external-write authority.

### School Learning

School Learning is the implemented local, owner-controlled learning workflow:

```text
./school --help
```

Its architecture and privacy boundary are defined in
[`docs/architecture/school-learning.md`](docs/architecture/school-learning.md).
Personal course materials, learner state, answers, and generated personal views
remain outside this engineering repository.

## Repository Navigation

- Platform and capability architecture: [`docs/architecture/`](docs/architecture/)
- Engineering authority interpretation: [`AGENTS.md`](AGENTS.md)
- Documentation map: [`docs/docs-map.md`](docs/docs-map.md)
- Dated review evidence: [`docs/reviews/`](docs/reviews/)
- Strategic direction: [`docs/roadmaps/`](docs/roadmaps/)
- Deterministic tooling: [`tools/`](tools/)
- Portable tests: [`tests/`](tests/)

Generated files such as
[`docs/aiden-context.md`](docs/aiden-context.md) and
[`docs/infrastructure-snapshot.md`](docs/infrastructure-snapshot.md) are derived
views, not canonical replacements.

## Authority Boundary

Repository state may select work but grants no permission. Explicit current
owner instruction establishes task authority; implementation authority must be
bounded separately; publication, deployment, and external writes require
separate explicit authorization. [`AGENTS.md`](AGENTS.md) is the primary
repository-local authority-interpretation contract.

## Infrastructure History

The original T430 homelab is one infrastructure environment within the wider
Aiden Platform. Its canonical and historical records remain available in:

- [`docs/infrastructure.md`](docs/infrastructure.md)
- [`docs/infrastructure-gamer-pve.md`](docs/infrastructure-gamer-pve.md)
- [`docs/services.md`](docs/services.md)
- [`docs/changes.log`](docs/changes.log)
- [`docs/changes/`](docs/changes/)

These records are engineering documentation, not proof of current deployed or
reachable state; live infrastructure requires separate observation.
