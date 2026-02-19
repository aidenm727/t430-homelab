# T430 Homelab Infrastructure Record

Last Updated: 2026-02-18  
Phase: Docker Baseline Complete  

---

## 1. System Overview

Hostname: t430-beast  
Operating System: Ubuntu Server 24.04.4 LTS (Noble Numbat)  
Kernel: 6.8.0-100-generic  
Primary Interface: enp0s25  
IP Address: 10.0.0.136  
Gateway: 10.0.0.1  

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

## 6. Operational Logging

Server-side operational log maintained at:

~/homelab/docs/changes.log

All infrastructure modifications must be recorded there.
