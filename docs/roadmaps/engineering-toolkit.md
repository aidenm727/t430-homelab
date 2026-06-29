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

Atlas has evolved from a prototype engineering-state tool into the beginning of a deterministic engineering interface for the Aiden Platform.

Implemented capabilities include:

### Repository Knowledge

* Shared engineering-state model
* Repository discovery
* Document Catalog
* Structured document metadata
* Document definitions
* Repository navigation

### Current Commands

```text
atlas state
atlas doctor
atlas next
atlas docs
atlas explain
atlas missing
atlas open
```

Current engineering focus:

* Continue building reusable capabilities before adding new commands.
* Strengthen the Repository Knowledge Layer.
* Expand engineering reasoning rather than command-specific logic.
* Keep Atlas architecture-first and capability-driven.

## Future CLI Shape

Potential future commands include:

```text
atlas state
atlas doctor
atlas next
atlas docs
atlas explain
atlas missing
atlas open

atlas validate
atlas recommend
atlas impact
atlas search
atlas context
atlas change
atlas roadmap
atlas inbox
```

These commands should remain thin presentation layers built on reusable engineering capabilities.

## Candidate Future Capabilities

Future capability work includes:

* Repository relationship graph
* Documentation validation
* Repository synchronization analysis
* Engineering recommendations
* Impact analysis
* Repository search
* Context preparation for AI assistants
* Architecture-aware engineering guidance
* Engineering Inbox for capturing ideas before they become roadmap or architecture
* Repository health scoring
* Documentation lifecycle management
* Change impact prediction
