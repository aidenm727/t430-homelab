\# Infrastructure Record

## Metadata



Last Updated:

2026-06-23



Canonical Repository:

github.com/aidenm727/t430-homelab



Documentation Version:

2.0



Authoritative Sources:



\* docs/infrastructure.md

\* \~/homelab/docs/changes.log



\## Current Phase



Phase:

Platform Expansion \& AI Workflow Foundation



Primary Objectives:



1\. Learn and establish Proxmox virtualization workflows

2\. Expand homelab capacity beyond the T430

3\. Design AI-assisted documentation and operational workflows

4\. Build foundations for Aiden OS



Current Status:



\* t430-beast remains the production services host

\* gamer-pve Proxmox host successfully deployed

\* Existing monitoring, backups, DNS, and password management operational

\* Infrastructure documentation redesign in progress

\* Aiden Context architecture under active design



Next Milestone:

Create and document the first VM deployment on gamer-pve while continuing development of the homelab documentation and context-generation workflow.


## Architecture Overview



\### Physical Infrastructure



Internet

│

├── Tailscale

│

├── t430-beast

│   ├── Pi-hole

│   ├── Traefik

│   ├── Grafana

│   ├── Prometheus

│   ├── Loki

│   ├── Alloy

│   ├── Uptime Kuma

│   └── Vaultwarden

│

└── gamer-pve

&#x20;   ├── Proxmox VE

&#x20;   └── Future VMs and Containers



\### Design Philosophy



t430-beast serves as the stable production services platform.



gamer-pve serves as the virtualization, experimentation, and future expansion platform.



Production services should remain stable and isolated from experimental workloads whenever practical.





\## Hosts



\### t430-beast



Role:

Production Services Host



Status:

Production



Hardware:



\* Lenovo ThinkPad T430

\* Intel i5-3320M

\* 8 GB RAM

\* 250 GB Samsung 840 Pro SSD



Operating System:



\* Ubuntu Server 24.04 LTS



Network:



\* LAN IP: 10.0.0.136

\* Tailscale Enabled



Responsibilities:



\* Pi-hole

\* Traefik

\* Grafana

\* Prometheus

\* Loki

\* Alloy

\* Uptime Kuma

\* Vaultwarden

\* Backup Infrastructure



\---



\### gamer-pve



Role:

Virtualization Host



Status:

Production



Hardware:



\* AMD Ryzen 5 2600

\* 16 GB DDR4

\* RTX 4060-class GPU



Storage:



\* 500 GB WDC SSD (Proxmox OS)

\* 1 TB SPCC NVMe SSD

\* 2 TB WD Blue SA510 SSD



Operating System:



\* Proxmox VE 9.2



Network:



\* LAN IP: 10.0.0.178



Responsibilities:



\* VM Hosting

\* Container Hosting

\* Future Immich Deployment

\* Future AI Workloads

\* Homelab Expansion Platform



\## Virtualization

VMs, LXCs, allocation strategy, and virtualization architecture.



\## Networking

IP addresses, DNS, Tailscale, routing, domains, and access patterns.



\## Services

Deployed applications and infrastructure services.



\## Storage

Physical disks, storage pools, backup targets, and capacity planning.



\## Monitoring \& Alerting

Observability stack, dashboards, health checks, and alerting paths.



\## Backups

Backup systems, schedules, retention policies, and restore testing.



\## Automation

Ansible, scripts, workflows, and future automation systems.



\## Security

Authentication, certificates, access controls, secrets management, and hardening.



\## Operational Rules

Standards, documentation requirements, and change management process.


### Documentation Philosophy



infrastructure.md = current state



changes.log = operational history



Git history = project evolution



\### Change Workflow



1\. Deploy / Configure

2\. Verify

3\. Document

4\. Commit \& Push


\## Roadmap

Planned projects, future phases, and long-term objectives.

