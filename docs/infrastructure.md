# T430 Homelab Infrastructure Record

Last Updated: 2026-03-10  
Phase: Core Platform Established

---

# 1. System Overview

Hostname: t430-beast  
Operating System: Ubuntu Server 24.04.4 LTS (Noble Numbat)  
Kernel: 6.8.0-100-generic  

Primary Interface: enp0s25  
IP Address: 10.0.0.136  
Gateway: 10.0.0.1  

Disk Layout
- Root filesystem on 250GB SSD
- No separate data partition (current state)

Memory
- 8GB RAM available
- No swap adjustments made

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

- Ethernet-only configuration (WiFi disabled for stability)
- DHCP lease provided by Xfinity router
- Firewall: UFW enabled
- SSH enabled and persistent at boot

Rationale  
Ethernet-only configuration reduces IP switching and improves reliability for service hosting.

---

# 4. System Maintenance Baseline

System updated and cleaned using:
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y

Reboot performed after major updates.

---

# 5. Docker Platform

Docker installed from the official Docker APT repository.

Installed Components
- docker-ce
- docker-ce-cli
- containerd.io
- docker buildx plugin
- docker compose plugin

Post-install Configuration
- Docker service enabled at boot
- Non-root Docker usage configured
- Logging driver: `json-file`
- Log rotation: `10MB` max size, `3` files
- Verified installation using `docker run hello-world`

Result  
System functioning as a stable container host.

---

# 6. Core Infrastructure

## Reverse Proxy (Traefik)

Traefik v3.6.1 deployed via Docker Compose.

Location  
`~/homelab/services/traefik`

Shared Docker Network  
`proxy`

Configuration
- Docker provider enabled
- `exposedbydefault=false`
- Host-based routing enabled

Routing Rules

| Hostname | Destination |
|--------|-------------|
| kuma.home.lab | Uptime Kuma |
| traefik.home.lab | Traefik dashboard |
| dash.home.lab | Homepage dashboard |

---

## Uptime Kuma

Purpose  
Network and service uptime monitoring dashboard.

Deployment Method  
Docker Compose

Container Image  
`louislam/uptime-kuma:latest`

Location  
`~/homelab/services/uptime-kuma`

Persistent Data  
`~/homelab/services/uptime-kuma/data`

Access
- Internal Port: `3001`
- Routed URL: `http://kuma.home.lab`

Configuration Details
- Restart policy: `unless-stopped`
- Persistent storage via mounted Docker volume

Result  
Service monitoring platform successfully deployed.

---

## Homepage Dashboard

Purpose  
Central entry point for homelab services.

Deployment Method  
Docker Compose

Container Image  
`ghcr.io/gethomepage/homepage:latest`

Location  
`~/homelab/services/homepage`

Persistent Configuration  
`~/homelab/services/homepage/config`

Configuration Details
- Connected to shared Docker network: `proxy`
- Routed through Traefik using host-based routing
- Host validation enabled via `HOMEPAGE_ALLOWED_HOSTS`

Access  
`http://dash.home.lab`

Result  
Central dashboard deployed for service discovery and navigation.

---

# 7. Operational Logging

Server-side operational log maintained at:
~/homelab/docs/changes.log

All infrastructure modifications must be recorded in this file.

---

# 8. Next Phase

Introduce monitoring infrastructure to expand observability of the homelab environment.

Planned Services

- Node Exporter (host metrics)
- Prometheus (metrics collection and storage)
- Grafana (metrics visualization)

Future Expansion Areas

- DNS infrastructure (Pi-hole)
- Container management interface (Portainer)
- Additional monitoring integrations
- Static IP or DHCP reservation stabilization

Goal  
Gradually evolve the host from a small service host into a structured multi-service homelab platform with proper observability, monitoring, and management tooling.