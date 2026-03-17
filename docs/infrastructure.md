# T430 Homelab Infrastructure Record

Last Updated: 2026-03-17 
Phase: Phase: Core Platform Established (Stable)

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

# System Architecture

The homelab follows a centralized routing and DNS model:

Client → Pi-hole (DNS) → Traefik (Reverse Proxy) → Docker Services

- Pi-hole resolves internal domains (e.g., grafana.home.lab)
- Traefik routes HTTP requests to the correct container
- Services run in isolated Docker containers on a shared network

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
Traefik
- Dashboard routed at `http://traefik.home.lab`
- Ping endpoint enabled for internal health monitoring
- Uptime Kuma monitor checks `http://traefik/ping`

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

Uptime Kuma
- Internal monitors configured for:
  - Homepage
  - Prometheus
  - Grafana
  - Traefik

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

## Pi-hole

Purpose
Provides local DNS service for homelab hostname resolution and prepares the environment for network-wide DNS control.

Deployment Method
Docker Compose

Container Image
`pihole/pihole:latest`

Location
`~/homelab/services/pihole`

Persistent Data
- `~/homelab/services/pihole/etc-pihole`
- `~/homelab/services/pihole/etc-dnsmasq.d`

Ports
- `53/tcp`
- `53/udp`

Configuration Details
- Host port 53 was freed by disabling `systemd-resolved`
- Host resolver configured to use Pi-hole for local DNS resolution
- Connected to shared Docker network: `proxy`
- Intended routed hostname: `pihole.home.lab`
- Container health verified after deployment
- Adjusted DNS listening mode to allow queries from all interfaces, resolving LAN accessibility issue

System Integration
- Host system resolver updated to use Pi-hole (127.0.0.1)
- Verified external DNS resolution via Pi-hole

Authentication
- Admin password configured using `pihole setpassword` inside container due to persistent config overriding environment variable

Client Integration
- Test client configured to use Pi-hole (10.0.0.136) as DNS server
- Verified resolution of internal domains (e.g., grafana.home.lab)
- Confirmed full DNS → Traefik → service routing flow

Result
DNS foundation is now deployed, enabling migration away from per-device hosts-file entries toward centralized homelab name resolution.

## Tailscale VPN

Purpose  
Provides secure remote access to the homelab without exposing services to the public internet.

Deployment Method  
Installed via official Tailscale install script.

Configuration Details
- Node joined to tailnet using Google authentication
- Tailscale IP assigned (100.x.x.x range)
- MagicDNS enabled for device name resolution
- Pi-hole configured as DNS server for tailnet
- Local DNS records updated to use Tailscale IP instead of LAN IP

Capabilities Enabled
- Remote SSH access to server
- Remote access to all services via .home.lab domains
- Secure device-to-device communication using WireGuard

Result  
Homelab is now accessible securely from any network without port forwarding.

### Access Control (ACLs)

Tailscale ACLs implemented to enforce principle of least privilege.

Configuration
- `group:admin` → full network access
- `group:web` → restricted to HTTP/HTTPS (ports 80/443) on server
- Default open access rule removed

Security Model
- Only admin devices can SSH into the server
- Future users (friends, guests) will be placed in `group:web`
- Ensures safe sharing of services without exposing system-level access

Result
Secure multi-user architecture established for controlled homelab access.

Monitoring Stack

Node Exporter
Collects host-level metrics (CPU, memory, disk, network).

Prometheus
Scrapes metrics from exporters and stores time-series data.

Grafana
Visualization platform connected to Prometheus.

Routes:
- prom.home.lab → Prometheus
- grafana.home.lab → Grafana


Dashboard:
- Node Exporter Full (ID 1860)

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

Current DNS Work
- Validate Pi-hole health
- Create local DNS records for homelab services
- Transition clients from hosts-file overrides to Pi-hole-based resolution

Goal  
Gradually evolve the host from a small service host into a structured multi-service homelab platform with proper observability, monitoring, and management tooling.