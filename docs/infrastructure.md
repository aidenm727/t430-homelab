# T430 Homelab Infrastructure Record

**Last Updated:** 2026-06-01
**Current Phase:** Platform Foundation Established (Monitoring, DNS, HTTPS, and Backups)

---

# 1. Purpose

This document is the canonical infrastructure record for the T430 homelab.

It describes:

* Current deployed infrastructure
* Service inventory
* Network architecture
* Access model
* Backup strategy
* Security controls
* Operational procedures
* Future roadmap

Chronological history is maintained separately in:

```text
~/homelab/docs/changes.log
```

---

# 2. System Overview

| Item              | Value                     |
| ----------------- | ------------------------- |
| Hostname          | `t430-beast`              |
| Hardware          | Lenovo ThinkPad T430      |
| Operating System  | Ubuntu Server 24.04.4 LTS |
| Primary Interface | `enp0s25`                 |
| Remote Access     | Tailscale                 |
| DNS Domain        | `home.lab`                |
| Deployment Method | Docker Compose            |

## Hardware

* Lenovo ThinkPad T430
* Intel i5-3320M
* 2 Cores / 4 Threads
* 8 GB RAM
* 250 GB Samsung 840 Pro SSD
* UEFI Boot
* VT-x Enabled
* VT-d Enabled
* Secure Boot Disabled

## Storage

* Root filesystem on internal SSD
* No dedicated data partition
* Service data footprint currently under 1 GB
* Local Restic backup repository configured

## Maintenance Notes

System successfully rebooted into kernel 6.8.0-117-generic after scheduled maintenance.

All containerized services recovered automatically and were verified operational after reboot.

---

# 3. Service Inventory

| Service           | Purpose                 | Access                          |
| ----------------- | ----------------------- | ------------------------------- |
| Homepage          | Service dashboard       | `https://dash.home.lab`         |
| Uptime Kuma       | Uptime monitoring       | `https://kuma.home.lab`         |
| Grafana           | Metrics visualization   | `https://grafana.home.lab`      |
| Prometheus        | Metrics collection      | `https://prom.home.lab`         |
| Pi-hole           | DNS management          | `https://pihole.home.lab/admin` |
| Traefik Dashboard | Reverse proxy dashboard | `https://traefik.home.lab`      |

---

# 4. Directory Layout

## Root Directory

```text
~/homelab
```

## Primary Directories

```text
~/homelab/docs
~/homelab/services
~/homelab/backups
```

## Service Directories

```text
~/homelab/services/traefik
~/homelab/services/uptime-kuma
~/homelab/services/homepage
~/homelab/services/pihole
~/homelab/services/monitoring
```

## Documentation

```text
~/homelab/docs/changes.log
```

---

# 5. Architecture

## High-Level Flow

```text
Client Device
    │
    ▼
 Tailscale
    │
    ▼
  Pi-hole
    │
    ▼
  Traefik
    │
    ▼
 Docker Services
```

## Design Principles

* Services are accessed through DNS names rather than IP addresses.
* Shared web services are routed through Traefik.
* Tailscale provides secure remote access.
* Pi-hole provides internal DNS resolution.
* Docker Compose manages deployments.
* Infrastructure changes are documented immediately after verification.

---

# 6. Network and Access Model

## Physical Network

* Wired Ethernet only
* Wi-Fi disabled
* DHCP provided by home router

## Firewall

UFW is enabled.

### Current Policy

```text
Default Incoming: Deny
Default Outgoing: Allow
Allowed Service: OpenSSH
```

### Note

Docker publishes ports using its own iptables rules.

Any future hardening should verify both:

* UFW configuration
* Docker port exposure

## Published Host Ports

| Port      | Purpose       |
| --------- | ------------- |
| `53/tcp`  | Pi-hole DNS   |
| `53/udp`  | Pi-hole DNS   |
| `80/tcp`  | Traefik HTTP  |
| `443/tcp` | Traefik HTTPS |

Uptime Kuma host port `3001` has been removed.

---

# 7. DNS

## Pi-hole

Pi-hole provides internal DNS resolution for homelab services.

### Location

```text
~/homelab/services/pihole
```

### Persistent Data

```text
~/homelab/services/pihole/etc-pihole
~/homelab/services/pihole/etc-dnsmasq.d
```

## DNS Records

```text
dash.home.lab
grafana.home.lab
kuma.home.lab
pihole.home.lab
prom.home.lab
traefik.home.lab
```

All service records resolve to the homelab server through Pi-hole.

## Tailscale Integration

* MagicDNS enabled
* Pi-hole used as DNS resolver
* `home.lab` configured as a search domain
* Cross-device DNS resolution verified

---

# 8. Tailscale

Tailscale provides secure remote access without public port forwarding.

## Access Groups

| Group         | Purpose                    |
| ------------- | -------------------------- |
| `group:admin` | Full administrative access |
| `group:web`   | Restricted web access      |

Restricted users should only access approved services through:

```text
80/tcp
443/tcp
```

SSH access remains restricted.

---

# 9. Docker Platform

Docker is installed from the official Docker repository.

## Components

* Docker Engine
* Docker Compose Plugin
* Docker Buildx
* Containerd

## Configuration

* Docker enabled at boot
* Non-root Docker access configured
* JSON log rotation enabled

### Log Rotation

```text
Max Size: 10 MB
Max Files: 3
```

## Networks

| Network      | Purpose                     |
| ------------ | --------------------------- |
| `proxy`      | Shared Traefik network      |
| `monitoring` | Internal monitoring network |

---

# 10. Reverse Proxy and HTTPS

## Traefik

Traefik v3.6.1 serves as the reverse proxy for all routed services.

### Location

```text
~/homelab/services/traefik
```

### Features

* Docker provider enabled
* File provider enabled
* Host-based routing
* HTTP and HTTPS entrypoints
* Internal health endpoint enabled
* Shared proxy network

## Entrypoints

| Entrypoint  | Port | Purpose |
| ----------- | ---- | ------- |
| `web`       | 80   | HTTP    |
| `websecure` | 443  | HTTPS   |

---

## Internal PKI

An internal Public Key Infrastructure (PKI) is used for trusted HTTPS.

### Root CA

```text
Aiden Homelab Root CA
```

### Wildcard Certificate

```text
*.home.lab
home.lab
```

### Certificate Storage

```text
~/homelab/services/traefik/certs/ca
~/homelab/services/traefik/certs/live
~/homelab/services/traefik/dynamic/tls.yml
```

### Security Requirements

* Never commit private keys
* Never commit certificate secrets
* Never commit backup passwords
* Root CA certificate may be installed on trusted devices

### Trusted Device Status

The Root CA has been successfully installed and validated on trusted client systems.

---

# 11. Routed Services

| Service     | HTTP                           | HTTPS                           | Backend            |
| ----------- | ------------------------------ | ------------------------------- | ------------------ |
| Homepage    | `http://dash.home.lab`         | `https://dash.home.lab`         | `homepage:3000`    |
| Uptime Kuma | `http://kuma.home.lab`         | `https://kuma.home.lab`         | `uptime-kuma:3001` |
| Grafana     | `http://grafana.home.lab`      | `https://grafana.home.lab`      | `grafana:3000`     |
| Prometheus  | `http://prom.home.lab`         | `https://prom.home.lab`         | `prometheus:9090`  |
| Pi-hole     | `http://pihole.home.lab/admin` | `https://pihole.home.lab/admin` | `pihole:80`        |
| Traefik     | `http://traefik.home.lab`      | `https://traefik.home.lab`      | `api@internal`     |

## HTTPS Status

All routed services are operational over HTTPS using the internal wildcard certificate.

HTTP remains available during the transition period.

Future decision:

* Keep dual-stack HTTP/HTTPS
* Or force HTTP → HTTPS redirects

---

# 12. Services

## Homepage

### Purpose

Central dashboard for homelab services.

### Location

```text
~/homelab/services/homepage
```

### Access

```text
https://dash.home.lab
```

### Notes

* Routed through Traefik
* Connected to `proxy`
* Dashboard links use HTTPS

---

## Uptime Kuma

### Purpose

Uptime monitoring and health verification.

### Location

```text
~/homelab/services/uptime-kuma
```

### Access

```text
https://kuma.home.lab
```

### Persistent Data

```text
~/homelab/services/uptime-kuma/data
```

### Notes

* No direct host port exposure
* Routed through Traefik
* Uses Docker-network targets where possible

---

## Monitoring Stack

### Components

| Component     | Purpose               |
| ------------- | --------------------- |
| Node Exporter | Host metrics          |
| Prometheus    | Metrics collection    |
| Grafana       | Metrics visualization |

### Grafana

Access:

```text
https://grafana.home.lab
```

Persistent Data:

```text
~/homelab/services/monitoring/grafana/data
```

### Prometheus

Access:

```text
https://prom.home.lab
```

Configuration:

```text
~/homelab/services/monitoring/prometheus/prometheus.yml
```

Storage:

```text
Docker volume: prometheus_data
```

---

## Pi-hole

### Purpose

Internal DNS and DNS management.

### Access

```text
https://pihole.home.lab/admin
```

### Notes

* Publishes DNS on port 53
* Routed through Traefik
* Attached to proxy network
* Local host uses Pi-hole DNS

---

# 13. Backup System

Restic is used for encrypted homelab backups.

## Repository

```text
~/homelab/backups/restic-repo
```

## Password File

```text
~/homelab/backups/restic-password
```

Permissions:

```text
600
```

## Protected Paths

```text
~/homelab/services
~/homelab/docs
```

## Current State

* Repository initialized
* Backup verified
* Restore verified
* Backups currently manual

## Restore Test

A full restore test was successfully completed.

Restore target:

```text
~/homelab/restore-test
```

Validated:

```text
~/homelab/docs
~/homelab/services
```

## Current Limitations

* Local repository only
* No scheduling
* No retention policy
* No off-device copy

## Planned Improvements

* Systemd timer
* Retention policy
* Backup monitoring
* External backup storage

### Automation

Backups are executed automatically through systemd.

Service:
- homelab-restic-backup.service

Timer:
- homelab-restic-backup.timer

Schedule:
- Daily at 03:00 local server time

Retention:
- 7 daily snapshots
- 4 weekly snapshots
- 6 monthly snapshots

The timer uses Persistent=true so missed backups run automatically after the system comes back online.

### Backup Health Monitoring

Successful backups update:

~/homelab/backups/last-successful-backup.txt

A validation script checks backup freshness:

~/homelab/scripts/check-backup-freshness.sh

The script returns success when the most recent backup is less than 25 hours old and failure otherwise.

### Backup Monitoring

Backup status is exposed through a dedicated health endpoint.

Service:
- health-endpoint (nginx)

Purpose:
- Serves backup status files from ~/homelab/health

URL:
- https://health.home.lab/backup.txt

Monitoring:
- Uptime Kuma monitor: Backup Health
- Internal target: http://health-endpoint/backup.txt

This provides automated monitoring of the backup subsystem.

---

# 14. Operational Procedures

## Standard Change Workflow

```text
Deploy / Configure
       ↓
Verify Functionality
       ↓
Document Immediately
```

## Required Documentation

### Server

Append:

```text
~/homelab/docs/changes.log
```

### GitHub

Update:

```text
docs/infrastructure.md
```

### Version Control

Commit and push using a professional commit message.

## Repository

```text
https://github.com/aidenm727/t430-homelab
```

Canonical documentation is maintained in GitHub.

---

# 15. Security Notes

## Strengths

* No public port forwarding
* Tailscale-secured access
* ACL separation
* UFW enabled
* Internal trusted HTTPS
* Reverse proxy architecture
* Encrypted backups
* Restore-tested backups

## Critical Rules

Never commit:

* Passwords
* API keys
* Tokens
* `.env` files
* Certificate private keys
* Restic password files

The Root CA private key must remain offline and protected.

---

# 16. Current State Summary

The homelab currently provides:

* Ubuntu Server host
* Docker Compose platform
* Internal DNS
* Reverse proxy routing
* Trusted HTTPS
* Internal PKI
* Secure remote access
* Service dashboard
* Uptime monitoring
* Metrics collection
* Metrics visualization
* Encrypted backups
* Verified restores
* Operational documentation

---

# 17. Known Gaps and Next Phase

## Immediate Priority

Automate Restic backups.

### Recommended Next Task

```text
Scheduled Restic backups with retention policy and monitoring
```

## Near-Term Improvements

* Systemd backup timer
* Retention policy
* Backup monitoring
* HTTP → HTTPS decision
* External backup storage
* Remove obsolete Compose version fields
* Reboot into updated kernel

## Future Platform Additions

* Ansible
* Centralized logging
* Alerting
* Vaultwarden
* Paperless-ngx
* Immich
* Jellyfin
* Additional storage
* Infrastructure automation

---

# 18. Long-Term Goal

Continue evolving the T430 into a production-style homelab platform focused on:

* Clear documentation
* Secure access
* Trusted HTTPS
* Reliable backups
* Restore validation
* Intentional service deployment
* Scalable operational practices
