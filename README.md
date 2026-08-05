# Aiden Platform

> A human-directed engineering platform for applied AI, deterministic tooling,
> and self-hosted infrastructure.

Aiden Platform is a personal engineering record for building useful capability
with explicit authority, reproducible evidence, and replaceable technology.
It is not a production SaaS platform, proof of continuous uptime, or a claim of
autonomous operation.

The human owner chooses goals, grants bounded authority, reviews evidence, and
accepts consequences. Repository state, Atlas, generated context, and AI
assistance never grant permission.

## What Exists Today

Here, **implemented** means repository code and tests exist, **operational
evidence** means a dated observation or use record exists, and **future** means
no implementation or operation is claimed.

| Capability | Status | Proof |
| --- | --- | --- |
| School Learning | Implemented; used in a bounded owner pilot | [Architecture](docs/architecture/school-learning.md), [implementation](tools/school_learning/), [tests](tests/test_school_learning.py), [pilot evaluation](docs/reviews/school-learning-v0-1-pilot-evaluation-2026-07-21.md) |
| Atlas and Workflow v1.1 | Implemented; operational as the repository workflow | [`./atlas`](atlas), [typed state](docs/current-state.json), [W1 evidence](docs/reviews/engineering-workflow-v1-1-evidence-2026-08-01.md) |
| Task-scoped context compilation | Implemented library capability; no general public CLI claim | [Architecture](docs/architecture/task-scoped-agent-context-compilation.md), [compiler](tools/atlas/platform/context_compilation/), [selection](tools/atlas/platform/reasoning/context_selection.py), [tests](tests/test_context_compilation.py) |
| Self-hosted infrastructure | Dated operational evidence; continuous state is not claimed | [Public-safe infrastructure](docs/infrastructure.md), [virtualization record](docs/infrastructure-virtualization.md), [service capabilities](docs/services.md) |

Implemented today: deterministic repository engineering tools, reproducible
task-scoped context compilation, and an owner-controlled School Learning
workflow.

Operational evidence: a small self-hosted environment has supported core
networking, observability, backup, virtualization, and selected services.
Public records are sanitized and time-bounded; they do not prove continuous
availability.

Future work: knowledge sovereignty, demonstrated recovery, and local-AI
experiments remain planned or exploratory until a dated evidence record
establishes implementation and operation.

## Architecture

```text
Human owner
  ├── goals, authority, review, acceptance
  │
  ▼
Public engineering record
  ├── architecture and standards
  ├── deterministic tooling and tests
  ├── capability implementations
  └── sanitized evidence
          │
          ├── explicit bounded handoff ──► Replaceable AI providers/runtimes
          │
          └── public-safe patterns ─────► Self-hosted execution environments

Future private operations record
  └── exact configuration, inventory, recovery, and private evidence
      (never secret values)
```

## Proof in Practice

### School Learning

The [School Learning architecture](docs/architecture/school-learning.md) defines
a local data contract, grounded Guided Study Handoff, and explicit
insufficient-evidence behavior. The [implementation](tools/school_learning/),
[negative-path tests](tests/test_school_learning.py), and [dated pilot
evaluation](docs/reviews/school-learning-v0-1-pilot-evaluation-2026-07-21.md)
show the chain from an owner problem through real use and correction. Personal
course material, answers, and learning history remain outside Git.

### Task-Scoped Context Compilation

The [context architecture](docs/architecture/task-scoped-agent-context-compilation.md)
is implemented as bounded snapshot, selector, selection, materialization,
validation, digest, and compiler layers under
[`tools/atlas/platform/context_compilation/`](tools/atlas/platform/context_compilation/).
The [snapshot](tests/test_context_snapshot.py),
[selection](tests/test_context_selection.py), and
[materialization](tests/test_context_materialization.py) tests cover immutable
identity, provenance, byte budgets, omissions, and consumer constraints. This
is a library capability, not a claim of a general public CLI or production
service.

### Atlas and Workflow v1.1

Atlas turns registered repository facts into deterministic inspection,
validation, synchronization, review, and next-action reports. The
[canonical state](docs/current-state.json),
[collaboration standard](docs/standards/engineering-collaboration.md),
[readiness tests](tests/test_atlas_readiness.py), and
[W1 evidence](docs/reviews/engineering-workflow-v1-1-evidence-2026-08-01.md)
show how typed state remains separate from owner authority.

## Engineering Quality

```text
real problem
→ owner decision
→ bounded implementation
→ negative/adversarial tests
→ independent review
→ correction
→ reproducible verification
→ owner acceptance
```

Verification counts are dated outcomes, not permanent claims about the current
suite. For example, W1 recorded 406 passing tests and one skip on 2026-08-02;
the linked evidence and Git history own that historical result. The current R1
record is an uncommitted local candidate awaiting independent review.

## Inspect or Run

From the repository root in the current checkout:

```bash
PYTHONDONTWRITEBYTECODE=1 ./atlas bootstrap
PYTHONDONTWRITEBYTECODE=1 ./school --help
PYTHONPATH=tools PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s tests -p 'test_*.py'
```

`./atlas bootstrap` inspects repository state; it does not authorize work.
School Learning keeps personal data outside Git. A final clone command for the
accepted future slug is intentionally deferred until an actual GitHub rename is
separately authorized and verified.

## Public and Private Boundary

| Fact class | Canonical owner |
| --- | --- |
| Vision, architecture, standards, code, tests, public state and evidence | This public repository |
| Sanitized infrastructure patterns and dated public evidence | This public repository |
| Exact inventory, addressing, private DNS, deployment configuration, backup destinations, recovery runbooks, incidents, and private live evidence | A future private operations repository, only when a real versioned artifact requires it |
| Secret values, private keys, tokens, and recovery keys | Secret manager or protected operational storage; never Git |
| Current live reality | Live systems and fresh observation |
| GitHub description, topics, settings, rules, and integrations | GitHub itself; only dated summaries belong here |

The canonical boundary and trigger for any future private repository are in
[Repository Architecture](docs/architecture/repository.md).

## Current and Future

The [canonical state](docs/current-state.json) currently keeps W1 as the
published phase and selects only the bounded local R1 checkpoint. The live
repository is still `aidenm727/t430-homelab`; the accepted future slug is
`aiden-platform`. No rename, redirect, GitHub metadata change, or final new-slug
clone target is claimed.

Aiden Platform began as a ThinkPad T430 homelab and grew into a broader personal
engineering platform. Current delivered capability centers on School Learning,
Atlas/Workflow v1.1, task-scoped context compilation, and public-safe dated
infrastructure evidence. Local AI, a private operations repository, broader
knowledge sovereignty, and additional recovery proof remain future or
conditional work.

## Navigate Deeper

- [Vision and human authority](docs/vision.md)
- [Platform architecture](docs/architecture/platform.md)
- [Canonical current state](docs/current-state.json)
- [Dated review evidence](docs/reviews/)
- [Full documentation map](docs/docs-map.md)
