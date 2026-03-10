# T430 Homelab Infrastructure Record

Last Updated: 2026-03-10  
Phase: Initial Services Deployment  

---

## 1. System Overview

Hostname: t430-beast  
Operating System: Ubuntu Server 24.04.4 LTS (Noble Numbat)  
Kernel: 6.8.0-100-generic  
Primary Interface: enp0s25  
IP Address: 10.0.0.136  
Gateway: 10.0.0.1

Disk Layout:
- Root filesystem on 250GB SSD
- No separate data partition (current state)

Memory:
- 8GB RAM available
- No swap adjustments made

---

## 2. Hardware Specifications

- Lenovo ThinkPad T430
- Intel i5-3320M (2C / 4T)
- 8GB RAM
- 250GB Samsung 840 Pro SSD
- UEFI Boot
- VT-x Enabled
- VT-d Enabled
- Secure Boot Disabled

---

## 3. Network Configuration

- Ethernet-only configuration (WiFi disabled for stability)
- DHCP lease stable via Xfinity router
- Firewall: UFW enabled
- SSH enabled and persistent at boot

Rationale:  
Ethernet-only configuration reduces IP switching and improves reliability for service hosting.

---

## 4. System Maintenance Baseline

System updated and cleaned using:

sudo apt update  
sudo apt upgrade -y  
sudo apt autoremove -y  

Reboot performed after major updates.

---

## 5. Docker Installation (Phase 1 Complete)

Docker installed from official Docker APT repository.

Installed components:
- docker-ce
- docker-ce-cli
- containerd.io
- docker buildx plugin
- docker compose plugin

Post-install configuration:
- Docker service enabled at boot
- Non-root Docker usage configured
- Logging driver: json-file
- Log rotation: 10MB max size, 3 files
- Verified with `docker run hello-world`

Result:  
System functioning as stable container host.

---

## 6. Deployed Services

### Uptime Kuma

Purpose:  
Network and service uptime monitoring dashboard.

Deployment Method:  
Docker Compose

Container Image:  
louislam/uptime-kuma:latest

Location:
~/homelab/services/uptime-kuma

Port Mapping:
3001 → 3001

Persistent Data:
~/homelab/services/uptime-kuma/data

Access URL:
http://10.0.0.136:3001

Configuration Details:
- Restart policy: `unless-stopped`
- Data persistence through mounted Docker volume
- Service deployed using `docker compose up -d`

Result:
First persistent Docker Compose service successfully deployed on the homelab host.

---

## 7. Operational Logging

Server-side operational log maintained at:

~/homelab/docs/changes.log

All infrastructure modifications must be recorded there.

---

## 8. Next Phase

Introduce additional infrastructure services to expand the homelab environment.

Planned areas:

- Reverse proxy (Traefik or Nginx Proxy Manager)
- Central service dashboard
- System monitoring stack (Prometheus + Grafana)
- Static IP / DHCP reservation stabilization

Goal:
Gradually evolve the host from a single-service container machine into a structured multi-service homelab platform.