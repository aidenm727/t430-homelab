# T430 Homelab Infrastructure Record

Last Updated: 2026-03-19  
Phase: Core Platform Established (Stable)

---

# 1. System Overview

Hostname: t430-beast  
Operating System: Ubuntu Server 24.04.4 LTS (Noble Numbat)  
Kernel: 6.8.0-100-generic  

Primary Interface: enp0s25  
IP Address: 10.0.0.136  
Gateway: 10.0.0.1  

## Disk Layout
- Root filesystem on 250GB SSD
- No separate data partition

## Memory
- 8GB RAM
- No swap adjustments

---

# 2. Hardware Specifications

- Lenovo ThinkPad T430
- Intel i5-3320M (2C / 4T)
- 8GB RAM
- 250GB Samsung 840 Pro SSD
- UEFI Boot
- VT-x Enabled
- VT-d Enabled
- Secure Boot Disabled

---

# 3. Network Configuration

- Ethernet-only configuration (WiFi disabled)
- DHCP lease via Xfinity router
- Firewall: UFW enabled
- SSH enabled and persistent at boot

Rationale:  
Ethernet-only configuration improves stability for service hosting.

---

# 4. System Maintenance Baseline

System maintained with:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

Reboot performed after major updates.

---

# 5. System Architecture

The homelab follows a centralized DNS and reverse-proxy model:

**Client → Tailscale → Pi-hole (DNS) → Traefik → Docker Services**

## Responsibilities

- **Tailscale**: Secure remote access and network segmentation
- **Pi-hole**: Internal DNS resolution for `.home.lab` domains
- **Traefik**: Reverse proxy for HTTP routing
- **Docker**: Containerized service runtime

## Key Behavior

- All shared services are accessed via domain names
- Internal traffic is routed through Traefik on ports 80/443
- DNS resolution is centralized through Pi-hole
- Direct application port exposure is not used for shared users

---

# 6. Docker Platform

Docker installed via the official APT repository.

## Installed Components

- docker-ce
- docker-ce-cli
- containerd.io
- docker buildx plugin
- docker compose plugin

## Configuration

- Docker enabled at boot
- Non-root Docker usage configured
- Logging driver: `json-file`
- Log rotation: `10MB` max size, `3` files

## Verification

- `docker run hello-world` completed successfully

Result:  
Stable container host established.

---

# 7. Core Infrastructure

## Reverse Proxy — Traefik

Traefik v3.6.1 deployed via Docker Compose.

### Features

- Docker provider enabled
- `exposedbydefault=false`
- Host-based routing
- Ping endpoint enabled for internal health monitoring

### Access

- Dashboard: `http://traefik.home.lab`

### Location

`~/homelab/services/traefik`

### Network

- Shared Docker network: `proxy`

### Routing Rules

| Hostname | Destination |
|---|---|
| `kuma.home.lab` | Uptime Kuma |
| `traefik.home.lab` | Traefik dashboard |
| `dash.home.lab` | Homepage dashboard |
| `prom.home.lab` | Prometheus |
| `grafana.home.lab` | Grafana |

### Monitoring Integration

- Uptime Kuma monitors Traefik via `http://traefik/ping`

---

## Uptime Kuma

### Purpose

Service and uptime monitoring dashboard.

### Deployment

- Docker Compose
- Image: `louislam/uptime-kuma:latest`

### Location

`~/homelab/services/uptime-kuma`

### Persistent Data

`~/homelab/services/uptime-kuma/data`

### Access

- Internal container/service port: `3001`
- Routed access: `http://kuma.home.lab`

### Configuration

- Restart policy: `unless-stopped`
- Persistent storage enabled

### Monitoring Targets

- Homepage
- Prometheus
- Grafana
- Traefik

### Current Monitors

Uptime Kuma monitors the following internal services using stable Docker-network targets where appropriate:

- Grafana → `http://grafana:3000`
- Homepage → `http://homepage:3000`
- Pi-hole → `http://pihole/admin/login`
- Prometheus → `http://prometheus:9090`
- Traefik → `http://traefik/ping`

This monitoring approach avoids dependence on LAN IPs, Tailscale IPs, or external DNS for internal health checks.

### Uptime Kuma Routing Fix
- Resolved a Traefik routing issue affecting `kuma.home.lab`
- Root cause: the Uptime Kuma container was attached to both `proxy` and `uptime-kuma_default`, which created network ambiguity for Traefik
- Fix: removed the extra default network and attached Uptime Kuma only to the shared `proxy` network
- Verified routed access at `http://kuma.home.lab`

### Network Exposure

- Uptime Kuma no longer publishes host port `3001`
- Access is provided only through Traefik at `http://kuma.home.lab`
- Container port `3001/tcp` remains internal to Docker networking

Result:  
Direct app-port exposure removed; Uptime Kuma now follows the reverse-proxy-only access model.

Result:  
Service monitoring platform successfully deployed.

---

## Homepage Dashboard

### Purpose

Central entry point for homelab services.

### Deployment

- Docker Compose
- Image: `ghcr.io/gethomepage/homepage:latest`

### Location

`~/homelab/services/homepage`

### Persistent Configuration

`~/homelab/services/homepage/config`

### Access

- `http://dash.home.lab`

### Configuration

- Connected to the shared `proxy` network
- Routed through Traefik using host-based routing
- Host validation enabled via `HOMEPAGE_ALLOWED_HOSTS`

Result:  
Dashboard deployed for service discovery and navigation.

---

## Pi-hole

### Purpose

Provides centralized DNS for homelab hostname resolution.

### Deployment

- Docker Compose
- Image: `pihole/pihole:latest`

### Location

`~/homelab/services/pihole`

### Persistent Data

- `~/homelab/services/pihole/etc-pihole`
- `~/homelab/services/pihole/etc-dnsmasq.d`

### Ports

- `53/tcp`
- `53/udp`

### Configuration Details

- Host port 53 was freed by disabling `systemd-resolved`
- Host resolver configured to use Pi-hole locally
- Pi-hole listens on all interfaces
- Connected to the shared `proxy` network

### System Integration

- Host resolver uses Pi-hole at `127.0.0.1`
- External DNS resolution verified through Pi-hole
- Internal `.home.lab` resolution verified

### Authentication

- Admin password configured with `pihole setpassword` inside the container

### Pi-hole Local DNS Records
- Added Pi-hole local DNS records for homelab service domains:
  - `pihole.home.lab`
  - `kuma.home.lab`
  - `grafana.home.lab`
  - `prom.home.lab`
  - `dash.home.lab`
  - `traefik.home.lab`
- All records currently resolve to the server Tailscale IP: `100.105.40.106`
- Verified routed access through Traefik using service hostnames, including `pihole.home.lab` and `grafana.home.lab`
- Direct host-port access is not required for services that are reverse-proxied through Traefik

### Temporary Bootstrap Access
- Pi-hole web UI was temporarily exposed on host port `8080` for DNS bootstrap and troubleshooting.
- Temporary access URL: `http://100.105.40.106:8080/admin`
- Purpose: allow access to Pi-hole before `.home.lab` DNS records were established.
- This exposure is intended to be removed after DNS records are added and routed access is working.

Result:  
Centralized DNS is established for both local and tailnet clients.

---

## Tailscale VPN

### Purpose

Provides secure remote access to the homelab without exposing services to the public internet.

### Deployment

Installed via the official Tailscale install method.

### Configuration Details

- Node joined to tailnet using Google authentication
- Tailscale IP assigned in the `100.x.x.x` range
- MagicDNS enabled
- Pi-hole configured as DNS for the tailnet
- Internal DNS records use the Tailscale IP for shared remote access

### Capabilities Enabled

- Secure remote access from any network
- Device-to-device encrypted communication
- No public port forwarding required

### Cross-Device Tailscale DNS Validation
- Added `home.lab` as a Tailscale DNS search domain alongside the tailnet domain
- Verified iPhone resolution and access to `pihole.home.lab` over Tailscale
- Confirmed cross-device internal service discovery now works through:
  - Tailscale
  - Pi-hole DNS
  - Traefik host-based routing

Result:  
Homelab services are securely accessible over Tailscale.

### Access Control (ACLs)

Tailscale ACLs enforce least privilege.

#### Groups

- `group:admin` → full network access
- `group:web` → restricted shared-service access

#### Allowed Access Model

| Group | Access |
|---|---|
| `group:admin` | Full network access |
| `group:web` | `tcp:80`, `tcp:443`, `udp:53`, `tcp:53` to `100.105.40.106` |

#### Security Model

- Only admin users can access SSH
- Restricted users can access DNS and web-routed services only
- Shared users cannot access direct application ports
- Shared access is routed through Pi-hole + Traefik

Result:  
Secure multi-user access control is established.

### Shared User Validation

A secondary user was added to the tailnet to validate restricted-access behavior.

#### Verified Results

- Invited user devices must join the same tailnet as the server
- Restricted users can resolve DNS through Pi-hole over Tailscale
- Restricted users can access:
  - `http://kuma.home.lab`
  - `http://traefik.home.lab`
- Restricted users cannot access:
  - `http://<tailscale-ip>:3001`
  - SSH or unintended services

Result:  
Shared users now reach approved services only through DNS + Traefik on ports 80/443.

---

## Monitoring Stack

### Components

- **Node Exporter**: Host-level metrics (CPU, memory, disk, network)
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization layer for metrics

### Routes

- `prom.home.lab`
- `grafana.home.lab`

### Dashboard

- Node Exporter Full (ID 1860)

Result:  
Baseline observability stack deployed and integrated into the homelab.

---

## Backup System

Restic is installed for encrypted homelab backups.

### Repository

- Local repository: `~/homelab/backups/restic-repo`
- Password file: `~/homelab/backups/restic-password`
- Password file permissions: `600`

### Backed Up Paths

- `~/homelab/services`
- `~/homelab/docs`

### Restore Verification

- Restore test completed successfully
- Latest snapshot restored into `~/homelab/restore-test`
- Confirmed restored `docs` and `services` directories
- Test restore directory removed after verification

### Current Status

- First clean backup snapshot created: `10282baa`
- Backups currently run manually with `sudo restic`
- Future improvement: automate backups and move repository to dedicated external storage

Result:  
Initial encrypted backup system established for service configuration, persistent service data, and operational documentation.

### HTTPS/TLS Preparation

- Added Traefik `websecure` entrypoint on port `443`
- Published host port `443:443`
- Existing HTTP routing remains active on `web`
- TLS certificates and HTTPS routers are not yet configured

Result:  
Traefik is prepared to serve HTTPS traffic, pending certificate configuration.

### Internal TLS / PKI

- Created internal Root CA: `Aiden Homelab Root CA`
- Issued wildcard certificate for `*.home.lab` and `home.lab`
- Traefik now loads TLS certificates through the file provider
- Uptime Kuma has both HTTP and HTTPS routers
- Verified `https://kuma.home.lab` routes successfully using the wildcard certificate
- Client devices must trust the internal Root CA before browsers show the connection as fully trusted

Security note:
- Private key files must not be committed to GitHub

---

### Trusted HTTPS

Client trust established for the internal PKI.

- Root CA imported into Windows trust store
- Browser validates `*.home.lab` certificate chain
- Verified trusted HTTPS access to `https://kuma.home.lab`

Current state:
- Internal PKI operational
- Trusted TLS available for homelab services

# 8. Operational Logging

Server-side operational log maintained at:

```text
~/homelab/docs/changes.log
```

All meaningful infrastructure modifications must be recorded in this file.

---

# 9. Current State Summary

The homelab currently provides:

- Stable Ubuntu Server host on dedicated hardware
- Docker-based service platform
- Centralized internal DNS via Pi-hole
- Reverse proxy routing via Traefik
- Secure remote access via Tailscale
- Multi-user access control using Tailscale ACLs
- Central dashboard and monitoring services
- Shared service access without public exposure or direct app-port sharing

---

# 10. Next Phase

Focus: **Platform Maturity and Expansion**

## Immediate Priorities

- Keep documentation aligned with deployed state
- Continue validating service health and routing behavior
- Improve understanding and organization of the existing monitoring stack

## Potential Next Additions

- Portainer or another container management interface
- Internal HTTPS / TLS for routed services
- Backup strategy for service data and configuration
- DHCP reservation or static addressing improvements
- Additional user-facing services exposed through Traefik

---

# Goal

Continue evolving the system from a small service host into a structured, production-style homelab platform with strong security, clear documentation, centralized routing, and scalable service management.
