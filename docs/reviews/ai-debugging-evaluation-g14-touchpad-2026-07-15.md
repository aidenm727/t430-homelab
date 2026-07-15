# G14 Touchpad Debugging Evaluation Evidence

> **Authority class:** Source Record and Evidence
>
> **Canonical:** No
>
> **Generated:** No
>
> **Producing workflow:** owner-executed read-only diagnostic capture plus human/AI review
>
> **Conclusion owner:** `docs/reviews/ai-workflow-evaluation-cycle-2026-07.md`

## Date and Provenance

This sanitized evidence record was prepared July 15, 2026 from three owner-captured diagnostic bundles produced during a naturally occurring ASUS ROG Zephyrus G14 touchpad failure and its recovery.

The bundles were used as read-only diagnostic inputs. The human-reviewed evaluation cycle owns the interpretation and operating conclusion; this record preserves bounded source evidence and does not independently establish root cause or permanent repair.

## Sensitivity and Retention Boundary

The raw diagnostic bundles are Sensitive Source Records retained outside Git.

This repository summary contains Ordinary Personal diagnostic context. The Windows username, computer name, full raw logs, unrelated device inventory, and unnecessary device identifiers are intentionally omitted.

## Artifact Integrity

| Artifact | SHA-256 | Captured state and timestamp |
| --- | --- | --- |
| `G14-Touchpad-failed-20260714-231720.zip` | `fa756cfe52082f0d31484f551b63e86c59fc28ebe0b23f6744b11b63cbdf2a78` | Failed at `2026-07-14T23:17:20.7944671-04:00` |
| `G14-Touchpad-failed-20260715-102400.zip` | `e718e9d6fbb64d9dab5433e9be2ce1f13ad0dd265d6021124f67ce4911ce090a` | Still failed at `2026-07-15T10:24:00.9631194-04:00` |
| `G14-Touchpad-healthy-20260715-102832.zip` | `2a33ea8953fbba9b0304155ecf9d063f6e26f89af846f8b0c91b2d35e44a11c1` | Healthy at `2026-07-15T10:28:32.5605694-04:00` |

## Sanitized Environment

- System model: ASUS ROG Zephyrus G14 GA403UI.
- Architecture and operating system: x64 Windows build 26200.
- Power capability: S0 Low Power Idle available.
- Target instance: `ACPI\ASUP1208\6`.

## Trigger Context

The owner reports that physical compression immediately preceded the observed failure.

That timing makes compression a plausible trigger, but compression was not experimentally isolated and is not an established cause. Deliberate reproduction through pressure or chassis flex is not recommended.

## Failed State

Both failed captures recorded the target as:

- Device: I2C HID Device.
- Manufacturer: Microsoft.
- Class: HIDClass.
- Configuration Manager problem: `CM_PROB_FAILED_START`.
- Error: Code 10 / `0x0A`.
- Problem status: `0xC000009E`.
- Driver INF: `hidi2c.inf`.
- Service: `hidi2c`.
- Device status: Error.

The same target and failure persisted across both failed captures for approximately 11 hours, 6 minutes, and 40 seconds.

## Restart and Recovery

The owner reports performing a normal Windows Restart without first uninstalling the failing I2C HID device.

The healthy bundle independently records an orderly reboot transition at 10:26:17, subsequent boot events, and healthy device recovery. The bundles do not independently prove the absence of every separate manual action between captures, so the no-uninstall sequence remains owner-observed workflow evidence supported by the recorded reboot and recovered state.

## Healthy State

The post-restart capture recorded:

- `CM_PROB_NONE`.
- Device reported as working properly.
- Status `OK`.
- No problem devices returned.
- The signed ASUS Precision Touchpad driver and signed Microsoft I2C/HID stack restored and active.

The relevant signed-driver evidence is limited to the restored ASUS Precision Touchpad device path and the Microsoft I2C HID, HID class, and supporting I2C stack. Full driver inventory and unrelated signed-driver details are intentionally omitted.

## Interpretation and Uncertainty

The evidence establishes an intermittent touchpad I2C initialization failure and successful recovery across a normal Windows restart.

The exact root cause remains unresolved. A marginal physical connection or chassis sensitivity, firmware behavior, power-state behavior, and driver or device initialization remain open explanations. The owner-reported compression timing supports a plausible physical trigger, but does not isolate or prove one.

The recovered state is not evidence of a permanent repair.

## Operational Follow-Up

The laptop reliability issue remains operationally unresolved and should be monitored without blocking the completed Initial AI Workflow Evaluation Cycle.

For a future naturally occurring failure:

1. Capture the failed state before changing it.
2. Perform a normal Windows Restart.
3. Capture and compare the resulting state.
4. Uninstall the failing I2C HID device only if Restart does not recover it, then continue bounded diagnosis and validation.

Do not deliberately reproduce the failure through pressure, compression, or chassis flex.

## Reassessment Boundary

Future touchpad failures and recovery captures may extend this operational evidence without automatically reopening the Initial AI Workflow Evaluation Cycle. Reopening the completed cycle requires an explicit owner decision.
