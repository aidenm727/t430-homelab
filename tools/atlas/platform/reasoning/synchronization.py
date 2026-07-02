from atlas.platform.document_catalog import DocumentCatalog
from atlas.platform.mission import mission_phase, next_milestone
from atlas.platform.repository import repo_root
from atlas.platform.reasoning.models import SynchronizationFinding, SynchronizationReport


REQUIRED_DOCUMENTS = [
    "docs/current-mission.md",
    "docs/aiden-context.md",
    "docs/architecture/platform.md",
    "docs/architecture/repository.md",
    "docs/architecture/atlas.md",
    "docs/architecture/repository-synchronization.md",
]


def finding(
    domain: str,
    severity: str,
    summary: str,
    evidence: str,
    recommended_action: str,
) -> SynchronizationFinding:
    return SynchronizationFinding(
        domain=domain,
        severity=severity,
        summary=summary,
        evidence=evidence,
        recommended_action=recommended_action,
    )


def repository_file_exists(path: str) -> bool:
    return (repo_root() / path).exists()


def generated_context_text() -> str:
    path = repo_root() / "docs/aiden-context.md"

    if not path.exists():
        return ""

    return path.read_text(encoding="utf-8")


def analyze_synchronization(catalog: DocumentCatalog) -> SynchronizationReport:
    findings: list[SynchronizationFinding] = []

    for path in REQUIRED_DOCUMENTS:
        if repository_file_exists(path):
            findings.append(
                finding(
                    domain="Required Documents",
                    severity="OK",
                    summary=f"{path} exists.",
                    evidence=f"Found {path}.",
                    recommended_action="No action required.",
                )
            )
        else:
            findings.append(
                finding(
                    domain="Required Documents",
                    severity="Error",
                    summary=f"{path} is missing.",
                    evidence=f"Expected repository path {path} was not found.",
                    recommended_action="Create or restore the missing document.",
                )
            )

    phase = mission_phase()
    milestone = next_milestone()

    findings.append(
        finding(
            domain="Current Mission",
            severity="OK" if phase != "Unknown" else "Error",
            summary="Current mission phase is defined." if phase != "Unknown" else "Current mission phase is missing.",
            evidence=f"Phase: {phase}",
            recommended_action="No action required." if phase != "Unknown" else "Update docs/current-mission.md with the active phase.",
        )
    )

    findings.append(
        finding(
            domain="Current Mission",
            severity="OK" if milestone != "Unknown" else "Error",
            summary="Next milestone is defined." if milestone != "Unknown" else "Next milestone is missing.",
            evidence=f"Next Milestone: {milestone}",
            recommended_action="No action required." if milestone != "Unknown" else "Update docs/current-mission.md with the next milestone.",
        )
    )

    context = generated_context_text()

    if context:
        findings.append(
            finding(
                domain="Generated Context",
                severity="OK" if "## Current Mission" in context else "Warning",
                summary="Generated context includes current mission." if "## Current Mission" in context else "Generated context may not include current mission.",
                evidence="Checked docs/aiden-context.md for a Current Mission section.",
                recommended_action="No action required." if "## Current Mission" in context else "Regenerate AI context.",
            )
        )

        findings.append(
            finding(
                domain="Generated Context",
                severity="OK" if "Generated:" in context else "Warning",
                summary="Generated context includes a generation marker." if "Generated:" in context else "Generated context does not include a generation marker.",
                evidence="Checked docs/aiden-context.md for a Generated marker.",
                recommended_action="No action required." if "Generated:" in context else "Regenerate AI context with a generation marker.",
            )
        )

    standards = catalog.paths_by_layer("Standards")
    findings.append(
        finding(
            domain="Standards",
            severity="OK" if standards else "Warning",
            summary="Standards layer is discovered." if standards else "Standards layer is not discovered.",
            evidence=f"Discovered standards: {', '.join(standards) if standards else 'None'}",
            recommended_action="No action required." if standards else "Check docs/standards and Atlas discovery.",
        )
    )

    return SynchronizationReport(findings=findings)
