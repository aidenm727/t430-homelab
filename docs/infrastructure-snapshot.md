\# Infrastructure Snapshot



\## Production Host



t430-beast



\- Role: Production services host

\- OS: Ubuntu Server 24.04 LTS

\- LAN IP: 10.0.0.136

\- Responsibilities:

&#x20; - Pi-hole

&#x20; - Traefik

&#x20; - Grafana

&#x20; - Prometheus

&#x20; - Loki

&#x20; - Alloy

&#x20; - Uptime Kuma

&#x20; - Vaultwarden

&#x20; - Backup infrastructure



\## Virtualization Host



gamer-pve



\- Role: Proxmox virtualization host

\- OS: Proxmox VE 9.2

\- LAN IP: 10.0.0.178

\- Hardware:

&#x20; - Ryzen 5 2600

&#x20; - 16 GB DDR4

&#x20; - RTX 4060-class GPU

\- Storage:

&#x20; - 500 GB WDC SSD: Proxmox OS

&#x20; - 1 TB SPCC NVMe SSD: preserved storage

&#x20; - 2 TB WD Blue SA510 SSD: preserved storage

\- Purpose:

&#x20; - VM hosting

&#x20; - Container hosting

&#x20; - Future Immich deployment

&#x20; - Future AI workloads



\## Active Services



\- Pi-hole

\- Traefik

\- Homepage

\- Uptime Kuma

\- Grafana

\- Prometheus

\- Loki

\- Alloy

\- Vaultwarden

