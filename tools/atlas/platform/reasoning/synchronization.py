from atlas.platform.document_catalog import DocumentCatalog
from atlas.platform.mission import mission_phase, next_milestone
from atlas.platform.repository import repo_root
from atlas.platform.reasoning.models import SynchronizationFinding, SynchronizationReport


REQUIRED_DOCUMENTS = [
    "docs/current-mission.md",
    "docs/aiden-context.md",
    "docs/infrastructure-snapshot.md",
    "docs/architecture/platform.md",
    "docs/architecture/repository.md",
    "docs/architecture/atlas.md",
    "docs/architecture/reasoning.md",
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


def repository_path(path: str):
    return repo_root() / path


def repository_file_exists(path: str) -> bool:
    return repository_path(path).exists()


def read_repository_file(path: str) -> str:
    file_path = repository_path(path)

    if not file_path.exists():
        return ""

    return file_path.read_text(encoding="utf-8")


def check_required_documents() -> list[SynchronizationFinding]:
    findings: list[SynchronizationFinding] = []

    for path in REQUIRED_DOCUMENTS:
        exists = repository_file_exists(path)

        findings.append(
            finding(
                domain="Required Documents",
                severity="OK" if exists else "Error",
                summary=f"{path} exists." if exists else f"{path} is missing.",
                evidence=f"Checked repository path: {path}",
                recommended_action="No action required." if exists else "Create or restore the missing document.",
            )
        )

    return findings


def check_current_mission() -> list[SynchronizationFinding]:
    findings: list[SynchronizationFinding] = []

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

    sync_architecture_exists = repository_file_exists("docs/architecture/repository-synchronization.md")
    milestone_mentions_sync = "synchronization" in milestone.lower()

    findings.append(
        finding(
            domain="Architecture ↔ Current Mission",
            severity="OK" if sync_architecture_exists and milestone_mentions_sync else "Warning",
            summary="Current mission is aligned with Repository Synchronization architecture."
            if sync_architecture_exists and milestone_mentions_sync
            else "Current mission may not align with Repository Synchronization architecture.",
            evidence=(
                f"Synchronization architecture exists: {'Yes' if sync_architecture_exists else 'No'}; "
                f"milestone references synchronization: {'Yes' if milestone_mentions_sync else 'No'}"
            ),
            recommended_action="No action required."
            if sync_architecture_exists and milestone_mentions_sync
            else "Review docs/current-mission.md and docs/architecture/repository-synchronization.md for alignment.",
        )
    )

    return findings


def check_generated_context() -> list[SynchronizationFinding]:
    findings: list[SynchronizationFinding] = []
    context = read_repository_file("docs/aiden-context.md")
    phase = mission_phase()
    milestone = next_milestone()

    if not context:
        return [
            finding(
                domain="Generated Context",
                severity="Error",
                summary="Generated AI context is missing.",
                evidence="docs/aiden-context.md could not be read.",
                recommended_action="Regenerate docs/aiden-context.md.",
            )
        ]

    checks = [
        (
            "Generated Context",
            "## Current Mission" in context,
            "Generated context includes current mission.",
            "Generated context may not include current mission.",
            "Checked docs/aiden-context.md for a Current Mission section.",
            "Regenerate AI context.",
        ),
        (
            "Generated Context",
            "Generated:" in context,
            "Generated context includes a generation marker.",
            "Generated context does not include a generation marker.",
            "Checked docs/aiden-context.md for a Generated marker.",
            "Regenerate AI context with a generation marker.",
        ),
        (
            "Generated Context",
            phase != "Unknown" and phase in context,
            "Generated context includes the active mission phase.",
            "Generated context may not include the active mission phase.",
            f"Active phase: {phase}",
            "Regenerate AI context after confirming docs/current-mission.md.",
        ),
        (
            "Generated Context",
            milestone != "Unknown" and milestone in context,
            "Generated context includes the active next milestone.",
            "Generated context may not include the active next milestone.",
            f"Active next milestone: {milestone}",
            "Regenerate AI context after confirming docs/current-mission.md.",
        ),
    ]

    for domain, passed, ok_summary, warn_summary, evidence, action in checks:
        findings.append(
            finding(
                domain=domain,
                severity="OK" if passed else "Warning",
                summary=ok_summary if passed else warn_summary,
                evidence=evidence,
                recommended_action="No action required." if passed else action,
            )
        )

    return findings


def check_generated_artifact_metadata(catalog: DocumentCatalog) -> list[SynchronizationFinding]:
    findings: list[SynchronizationFinding] = []

    generated_documents = [
        document
        for document in catalog.with_definitions()
        if document.definition is not None and document.definition.generated
    ]

    if not generated_documents:
        return [
            finding(
                domain="Generated Artifact Metadata",
                severity="Warning",
                summary="No generated artifacts are registered in document metadata.",
                evidence="Catalog returned no generated document definitions.",
                recommended_action="Register generated artifacts in Atlas document definitions.",
            )
        ]

    for document in generated_documents:
        definition = document.definition
        assert definition is not None

        exists = repository_file_exists(document.path)
        has_sources = bool(definition.generated_from)
        manager_exists = bool(definition.managed_by and repository_file_exists(definition.managed_by))

        if not exists:
            severity = "Error"
            summary = f"{document.path} is registered as generated but does not exist."
            action = "Regenerate or restore the generated artifact."
        elif not has_sources:
            severity = "Warning"
            summary = f"{document.path} does not declare canonical source documents."
            action = "Add generated_from metadata to the document definition."
        elif not manager_exists:
            severity = "Warning"
            summary = f"{document.path} does not have a valid managing tool."
            action = "Add or correct managed_by metadata in the document definition."
        else:
            severity = "OK"
            summary = f"{document.path} has generated artifact ownership metadata."
            action = "No action required."

        findings.append(
            finding(
                domain="Generated Artifact Metadata",
                severity=severity,
                summary=summary,
                evidence=(
                    f"exists={'Yes' if exists else 'No'}; "
                    f"generated_from={', '.join(definition.generated_from) if has_sources else 'None'}; "
                    f"managed_by={definition.managed_by if definition.managed_by else 'None'}"
                ),
                recommended_action=action,
            )
        )

    return findings


def check_architecture_layering() -> list[SynchronizationFinding]:
    atlas = read_repository_file("docs/architecture/atlas.md")
    repository = read_repository_file("docs/architecture/repository.md")

    checks = [
        (
            "Atlas Architecture ↔ Atlas Implementation",
            "Repository Knowledge Layer" in atlas and "Repository Reasoning Layer" in atlas,
            "Atlas architecture defines knowledge and reasoning layers.",
            "Atlas architecture may not clearly define knowledge and reasoning layers.",
            "Checked docs/architecture/atlas.md for Repository Knowledge Layer and Repository Reasoning Layer.",
            "Update docs/architecture/atlas.md before expanding Atlas implementation.",
        ),
        (
            "Repository Source of Truth",
            "Source of Truth" in repository and "Architecture documents define intent" in repository,
            "Repository source-of-truth rules are documented.",
            "Repository source-of-truth rules may be missing or unclear.",
            "Checked docs/architecture/repository.md for source-of-truth hierarchy.",
            "Update docs/architecture/repository.md with source-of-truth rules.",
        ),
    ]

    findings: list[SynchronizationFinding] = []

    for domain, passed, ok_summary, warn_summary, evidence, action in checks:
        findings.append(
            finding(
                domain=domain,
                severity="OK" if passed else "Warning",
                summary=ok_summary if passed else warn_summary,
                evidence=evidence,
                recommended_action="No action required." if passed else action,
            )
        )

    return findings


def check_standards_layer(catalog: DocumentCatalog) -> list[SynchronizationFinding]:
    standards = catalog.paths_by_layer("Standards")

    return [
        finding(
            domain="Standards",
            severity="OK" if standards else "Warning",
            summary="Standards layer is discovered." if standards else "Standards layer is not discovered.",
            evidence=f"Discovered standards: {', '.join(standards) if standards else 'None'}",
            recommended_action="No action required." if standards else "Check docs/standards and Atlas discovery.",
        )
    ]


def analyze_synchronization(catalog: DocumentCatalog) -> SynchronizationReport:
    findings: list[SynchronizationFinding] = []

    findings.extend(check_required_documents())
    findings.extend(check_current_mission())
    findings.extend(check_generated_context())
    findings.extend(check_generated_artifact_metadata(catalog))
    findings.extend(check_architecture_layering())
    findings.extend(check_standards_layer(catalog))

    return SynchronizationReport(findings=findings)
