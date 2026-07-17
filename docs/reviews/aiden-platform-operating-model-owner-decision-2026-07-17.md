# Aiden Platform Operating Model — Owner Decision Record

**Date:** July 17, 2026  
**Status:** Accepted for later repository processing  
**Implementation authorization:** Not granted  
**Active-work boundary:** EO-2026-013 remains unchanged.

## Purpose

This record captures the owner’s decisions following the operating-model discovery report, the external design-validation study, and the design-validation decision brief.

These decisions accept a narrowed future architecture direction. They do not create a new active mission, authorize implementation, authorize autonomous merge or deployment, or modify EO-2026-013.

## Accepted Decisions

### 1. Near-term interface name

**Working name:** `Aiden Platform Console`

This name is accepted for current architecture and planning, but naming remains open. The owner is interested in potentially choosing a product name that does not directly use the owner’s name.

Current interpretation:

- `Aiden Platform` remains the platform and product-family name for now.
- `Atlas` remains the deterministic engineering interface.
- `Aiden Platform Console` remains the working name for the human control surface.
- `Aiden OS` remains a broader long-term vision term, not the initial implementation name.

Naming should not block architecture work. A later naming exercise may evaluate a neutral or distinct product name.

### 2. Canonical task-state model

**Accepted:** Hybrid repository and GitHub model.

The repository-owned structured task object owns deterministic technical state, including:

- task identifier
- lifecycle state
- objective and success criteria
- base revision
- in-scope and out-of-scope paths
- authority and prohibited actions
- required outputs and verification
- evidence references
- completion disposition

The GitHub issue owns human coordination, including:

- discussion
- rationale
- questions
- progress notes
- links
- review conversation

The GitHub pull request owns the proposed repository change, including:

- implementation diff
- test and validation evidence
- code review
- merge decision

Atlas validates synchronization among the task object, issue, branch, pull request, context package, repository revision, and evidence.

### 3. Initial console scope

**Accepted:** Minimal V1.

The first control-surface slice should contain only:

1. **Home**
   - active work
   - current mission
   - pending approvals
   - blockers
   - recent completions
   - next valid actions

2. **Task Detail**
   - objective
   - lifecycle
   - scope
   - authority
   - repository revision
   - linked issue, branch, and pull request
   - evidence
   - next valid action

3. **Approval Queue**
   - plan approvals
   - privileged-action approvals
   - merge approvals
   - deployment approvals

4. **Review and Evidence**
   - changed paths
   - verification
   - architecture impact
   - documentation synchronization
   - unresolved risks
   - owner disposition

5. **Platform Map**
   - capabilities
   - systems
   - documents
   - workflows
   - tasks
   - agents
   - infrastructure
   - dependencies
   - lifecycle and health state

Brainstorm, Research, Automate, Operate, Learn, and broader Aiden OS experiences remain long-term product areas, not V1 requirements.

### 4. Approval gates

**Accepted:** Keep all four gates distinct.

#### Plan approval

Approves the objective, scope, exclusions, success criteria, intended workspace, and expected outputs.

#### Privileged-action approval

Required before protected-path changes, broader access, new network access, workflow changes, infrastructure work, secret-adjacent work, or authority expansion.

#### Merge approval

Approves integration into the canonical repository. An agent cannot satisfy the required human review of its own work.

#### Deployment approval

Approves operational execution or deployment. Merge authorization does not imply deployment authorization.

### 5. Initial agent authority

**Accepted ceiling:** Agents may inspect, analyze, propose, prepare, modify explicitly bounded scope, run verification, create a branch, open a draft pull request, and produce an evidence bundle.

Agents may not:

- merge
- deploy
- change architecture without approval
- broaden scope without approval
- alter protected boundaries
- perform broad cleanup without explicit authorization
- treat passing tests as sufficient acceptance evidence

Authority may expand only after repeated real-task evidence and a separate owner decision.

### 6. First real pilot

**Accepted selection strategy:**

Primary candidate:

> A small, low-risk Atlas cleanup or refactor.

Fallback candidate:

> A generated-context or metadata-synchronization improvement.

The final pilot must be selected from live repository evidence after Atlas review, Engineering Opportunity overlap review, current-mission review, risk assessment, and verification-path confirmation.

The pilot must:

- be useful and small
- be easy to verify
- avoid architectural change
- exercise task-state handoff
- exercise context compilation
- produce an evidence bundle
- end in a draft pull request
- require owner review
- prohibit automatic merge and deployment

No specific code change is authorized by this decision.

### 7. Overall disposition

**Accepted:** The validated direction may proceed to later repository processing without changing EO-2026-013 or authorizing implementation.

Accepted principles:

- durable task and protocol state
- a human control surface
- Atlas as deterministic knowledge and validation layer
- GitHub and the repository as canonical engineering foundation
- replaceable AI workspaces
- explicit approval gates
- gradual agent authority
- a Git-native V1
- no separate mutable application database in V1
- no general workflow engine in V1
- no broad console implementation before a bounded pilot
- no autonomous merge or deployment

## Interpretation of Owner Trust

The owner accepted most recommendations because the supporting reasoning was judged sound.

This is not blanket authorization for future recommendations.

The operating rule remains:

- AI may recommend and challenge.
- AI may prepare bounded artifacts when authorized.
- The owner accepts architecture, scope expansion, privileged actions, merge, and deployment.

## Accepted Near-Term Architecture

```text
Aiden Platform Console
Human orientation, task visibility, evidence review, and approvals
        ↓
Atlas
Deterministic knowledge, synchronization, context compilation,
validation, protocol enforcement, and next-action reasoning
        ↓
Repository and GitHub
Canonical structured objects, code, documentation, history,
issues, branches, pull requests, and evidence
        ↓
Replaceable AI and automation workspaces
ChatGPT, Deep Research, Work, Codex, future models, CI,
and bounded agents
```

The console must remain a generated human view over canonical evidence, not an independent source of truth.

## Accepted Future Checkpoint Candidate

### Working title

**Durable Engineering Task and First Human Control-Surface Slice**

### Status

Accepted as a future checkpoint candidate for repository overlap review and opportunity processing.

Implementation is not authorized.

### Intended proof

Demonstrate that one durable task object, one complete protocol, one Atlas context package, one evidence bundle, and one minimal human interface make real engineering work easier to understand and review.

### Candidate deliverables

- engineering-task schema
- lifecycle protocol
- Atlas validation
- hybrid GitHub linkage
- context-package compilation
- evidence-bundle format
- generated Home view
- generated Task Detail view
- approval visibility
- one bounded pilot ending in a draft pull request

### Expansion rule

Do not expand into a broad console until the pilot demonstrates clearer ownership, handoff, review, and completion.

## Naming Follow-Up

A later naming exercise may evaluate:

- whether `Aiden` remains the product-family name
- whether the control surface receives an independent product name
- whether `Atlas` remains limited to engineering intelligence
- whether `Aiden OS` remains a long-term environment name
- whether a neutral name better supports future public or multi-user use

Naming criteria should include clarity, memorability, product hierarchy, founder identity, extensibility, and distinction among platform, intelligence layer, and interface.

## Repository Processing Instructions

When this record is processed later:

1. Inspect live repository state through Atlas.
2. Review existing Engineering Opportunities for overlap.
3. Preserve the discovery report, research report, decision brief, and this record as linked evidence.
4. Do not modify EO-2026-013.
5. Do not change the active mission automatically.
6. Determine whether the operating model, durable task handoff, and human control surface belong in one opportunity or linked opportunities.
7. Record dependencies on EO-2026-013.
8. Preserve the open naming question.
9. Return proposed repository objects for owner review.
10. Do not implement without later explicit authorization.

## Decision Summary

```text
1. Working name: Aiden Platform Console; naming remains open.
2. Task state: hybrid repository YAML + GitHub issue/PR model.
3. Console V1: minimal five-view scope.
4. Approvals: plan, privileged action, merge, deployment remain distinct.
5. Agent authority: bounded changes and draft PRs; no merge or deployment.
6. Pilot: small Atlas refactor, or context/metadata synchronization fallback.
7. Direction: accepted for later processing; EO-2026-013 unchanged.
```
