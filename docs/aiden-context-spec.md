\# Aiden Context Specification



\## Purpose



Define the information required for AI systems (ChatGPT projects, future Aiden OS assistants, local models, agents) to accurately understand and assist with the homelab.



The AI should consume generated context, not serve as the source of truth.



Canonical sources remain:



\* docs/infrastructure.md

\* \~/homelab/docs/changes.log

\* Git history

\* Live infrastructure state



\---



\## Context Categories



\### Infrastructure State



Current hosts:



\* T430 production server

\* gamer-pve Proxmox host



Current services:



\* Pi-hole

\* Traefik

\* Grafana

\* Prometheus

\* Loki

\* Alloy

\* Uptime Kuma

\* Vaultwarden



Network:



\* LAN addressing

\* Tailscale addressing

\* DNS records

\* Hostnames



Storage:



\* Physical disks

\* Backup destinations

\* Retention policies



\---



\### Operations



Recent changes:



\* Derived from changes.log



Current issues:



\* Known problems

\* Technical debt

\* Pending migrations



Verification status:



\* Last successful checks

\* Backup validation status

\* Monitoring status



\---



\### Projects



Current phase:



\* Homelab expansion

\* Proxmox adoption



Active projects:



\* Immich

\* AI workflow improvements

\* Aiden OS



Future projects:



\* Local AI

\* Daily intelligence briefing

\* Automated documentation



\---



\### Workflow Rules



Change management:



1\. Deploy

2\. Verify

3\. Document



Documentation requirements:



\* Update changes.log

\* Update infrastructure.md

\* Commit and push



Security requirements:



\* No secrets in Git

\* Environment variables preferred

\* Backups required



\---



\## Desired Outputs



AI systems should be capable of generating:



\* changes.log entries

\* infrastructure.md updates

\* commit messages

\* implementation plans

\* infrastructure summaries

\* onboarding context



\---



\## Future Context Sources



Potential future integrations:



\* Proxmox API

\* Docker state

\* Ansible inventory

\* GitHub repository state

\* Obsidian knowledge base

\* Monitoring systems



\---



\## Long-Term Goal



Generate a machine-readable context package automatically from authoritative sources and provide it to AI systems so they always operate with current infrastructure knowledge.



