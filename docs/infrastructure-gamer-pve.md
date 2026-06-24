# gamer-pve Infrastructure Record

## Purpose

Proxmox virtualization platform used for:

- VM hosting
- LXC hosting
- Immich
- AI experimentation
- Future workloads

Relationship to Homelab:

- Managed separately from t430-beast
- Uses Tailscale for remote administration
- Intended to host resource-intensive workloads

## Host System

Hostname: gamer-pve

Hardware:

- Ryzen 5 2600
- 16 GB DDR4
- RTX 4060-class GPU

Operating System:

- Proxmox VE 9

Management:

- Web UI
- SSH
- Tailscale

## Network

Management IP:

10.0.0.178

Tailscale:

100.80.182.80

## Storage

500 GB SSD

- Proxmox OS

1 TB NVMe

- nvme-lvm

2 TB WD Blue

- Archive storage

## Proxmox Storage Pools

local

local-lvm

nvme-lvm

## LXC Inventory

### 200 - Immich

OS:

Debian 12

Resources:

- 4 vCPU
- 6 GB RAM
- 2 GB swap
- 128 GB root disk

IP:

10.0.0.132

Status:

Operational

## Current Status

- Prometheus node monitoring enabled via node_exporter
- External access integration pending
- Backup strategy not yet implemented
