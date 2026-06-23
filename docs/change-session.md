# Homelab Change Session

Started: 2026-06-23 19:42:35

## Change Title

Add NVMe Proxmox Storage Pool

## Intent

## Notes
- [2026-06-23 19:43:12] Added Proxmox storage target nvme-lvm for VM disks and LXC root disks
- [2026-06-23 19:43:12] Created volume group nvme-vg
- [2026-06-23 19:43:12] Created LVM physical volume on /dev/nvme0n1
- [2026-06-23 19:43:12] Repurposed the 1 TB SPCC NVMe SSD for Proxmox workloads
- [2026-06-23 19:43:11] Designated the 2 TB WD Blue SA510 SSD as the canonical Preservation archive drive
- [2026-06-23 19:43:11] Verified Preservation archive exists on both the 1 TB NVMe and 2 TB SSD before modifying storage

## Verification
- [2026-06-23 19:43:42] Verified nvme-lvm appears in the Proxmox web UI
- [2026-06-23 19:43:42] Verified storage availability using pvesm status
- [2026-06-23 19:44:00] Verified volume group creation using vgs
- [2026-06-23 19:43:42] Verified PV creation using pvs
- [2026-06-23 19:43:42] Verified archive readability from the 2 TB SSD using read-only mount

## Documentation Outputs
- [2026-06-23 19:48:41] Updated docs/infrastructure.md with gamer-pve NVMe storage and archive drive roles

