# Homelab Services Record

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

Logging Stack

Components:
- Grafana Loki
- Grafana Alloy

Purpose:
- Centralized Docker container log aggregation
- Historical log retention
- Grafana-based log exploration and filtering

Verified Log Sources:
- Homepage
- Pi-hole
- Uptime Kuma

Capabilities:
- Container log search
- Log filtering
- Error investigation
- Centralized troubleshooting

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

## Vaultwarden

Purpose:
- Self-hosted Bitwarden-compatible password manager

Location:
~/homelab/services/vaultwarden

Access:
https://vault.home.lab

Persistent Data:
~/homelab/services/vaultwarden/data

Notes:
- Routed through Traefik
- HTTPS enabled
- Public registrations disabled
- Protected by existing backup system

---