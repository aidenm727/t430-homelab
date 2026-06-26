# Compute Architecture

## Purpose

This document defines how compute resources are organized across the Aiden Platform.

Compute means the places where workloads run: physical hosts, VMs, LXCs, containers, AI workloads, and future orchestration systems.

## Core Principle

Workloads should run where they best fit the platform architecture, not simply wherever they are easiest to install.

## Compute Roles

## 1. Core Host

Stable production services.

Current implementation:

- t430-beast

Responsibilities:

- DNS
- Reverse proxy
- Monitoring
- Backups
- Core Docker services
- Operational tooling

## 2. Virtualization Host

Flexible workloads, experiments, and heavier services.

Current implementation:

- gamer-pve

Responsibilities:

- LXC workloads
- VM workloads
- Immich
- Future AI experimentation
- Resource-intensive services

## 3. Storage Host

Durable data home, not general app sprawl.

Current implementation:

- Future NAS

Responsibilities:

- Photos
- Documents
- Archives
- Media
- Backups
- Shared storage

## 4. AI Compute

Model inference, AI tools, and future orchestration.

Current implementation:

- ChatGPT Project workflow
- Future local AI workloads on gamer-pve or dedicated hardware

Responsibilities:

- Local models
- AI-assisted documentation
- Context generation
- Personal agents
- Future Aiden OS services

## Workload Placement Rules

## Promotion Path

Experiment → Stable workload → Documented platform service

## Current Open Questions

- Which workloads should stay permanently on t430-beast?
- Which workloads should move to gamer-pve?
- What should eventually depend on the future NAS?
- Where should local AI inference live?
- How should experimental services become production services?