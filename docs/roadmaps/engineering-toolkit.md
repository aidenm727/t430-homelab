# Aiden Engineering Toolkit Roadmap

## Purpose

The Aiden Engineering Toolkit is the software layer that helps maintain a coherent understanding of the Aiden Platform.

Its purpose is to reduce friction, prevent duplicated work, expose current engineering state, and help humans and AI assistants understand what has already been built.

## Current Tools

### generate-context.py

Generates AI-facing context documents.

### homelab-change.py

Manages change sessions, structured change records, changes.log updates, and context regeneration.

### aiden-context-loader.py

Prototype engineering state summary tool.

## Problem

The repository now contains architecture documents, infrastructure records, generated AI context, change workflows, roadmaps, and tools.

These pieces are useful, but they are not yet unified into one clear engineering interface.

## Goal

Create a future unified toolkit that can answer:

- What is the current engineering state?
- What change session is active?
- Which documents exist?
- Which tools exist?
- What changed recently?
- What should happen next?
- Which existing tool should be used?

## Current Progress

Atlas has begun replacing standalone engineering utilities with a unified engineering interface.

Current implemented commands:

```text
atlas state
atlas doctor
atlas next
```

Current focus:

* Expand deterministic engineering-state capabilities.
* Reuse existing repository information rather than duplicate it.
* Keep Atlas architecture-first and capability-driven.

## Future CLI Shape

Possible future commands:

```text
atlas state
atlas doctor
atlas next
atlas context
atlas docs
atlas change
atlas roadmap
atlas inbox
```

## Candidate Future Capabilities

The following ideas are intentionally tracked as roadmap items rather than architecture. They represent potential capabilities that may be promoted into the platform after further engineering review.

* Shared engineering-state model used by all Atlas commands.
* Engineering Inbox for capturing and organizing ideas before they become roadmap or architecture.
* Documentation discovery and validation.
* Repository consistency checks.
* Context preparation for AI assistants.
* Architecture-aware engineering guidance.
