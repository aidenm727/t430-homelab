from atlas.platform.active_state import (
    ActiveState,
    ActiveStateError,
    EvidenceLink,
    StateConcern,
    load_active_state,
)
from atlas.platform.document_catalog import DocumentCatalog
from atlas.platform.mission import mission_phase, next_milestone
from atlas.platform.repository import repo_root
from atlas.platform.reasoning.models import SynchronizationFinding, SynchronizationReport


SYNCHRONIZATION_SCOPE = (
    "required canonical and generated documents",
    "canonical active state and Current Mission compatibility fields",
    "generated context active-state projection",
    "registered generated-artifact ownership",
    "selected architecture and standards predicates",
)


REQUIRED_DOCUMENTS = [
    "docs/current-state.json",
    "docs/current-mission.md",
    "docs/aiden-context.md",
    "docs/infrastructure-snapshot.md",
    "docs/architecture/platform.md",
    "docs/architecture/repository.md",
    "docs/architecture/atlas.md",
    "docs/architecture/reasoning.md",
    "docs/architecture/repository-synchronization.md",
]


GENERATED_CONTEXT_ACTIVE_STATE_HEADING = "## Canonical Active State"


def _render_state_concerns(concerns: tuple[StateConcern, ...]) -> str:
    if not concerns:
        return "- None"
    return "\n".join(
        f"- `{concern.id}`: {concern.summary}" for concern in concerns
    )


def _render_evidence_links(evidence_links: tuple[EvidenceLink, ...]) -> str:
    if not evidence_links:
        return "- None"
    return "\n".join(
        (
            f"- `{link.id}`: `{link.path}` at `{link.commit}` "
            f"({link.relation})"
        )
        for link in evidence_links
    )


def render_generated_context_active_state(active_state: ActiveState) -> str:
    """Render the exact bounded active-state projection for generated context."""
    checkpoint = active_state.work_selection.selected_checkpoint
    selected_checkpoint = checkpoint.name if checkpoint is not None else "None"
    decision = active_state.decision_required
    decision_required = (
        f"`{decision.id}` — {decision.summary}"
        if decision is not None
        else "None"
    )

    return f"""{GENERATED_CONTEXT_ACTIVE_STATE_HEADING}

- Schema version: {active_state.schema_version}
- Effective date: {active_state.freshness.effective_date.isoformat()}
- Phase: {active_state.phase.display_name}
- Phase lifecycle: {active_state.phase.lifecycle}
- Work selection: {active_state.work_selection.status}
- Selected checkpoint: {selected_checkpoint}
- Intentional idle: {"Yes" if active_state.work_selection.intentional_idle else "No"}
- Decision required: {decision_required}

### Blockers

{_render_state_concerns(active_state.blockers)}

### Unknowns

{_render_state_concerns(active_state.unknowns)}

### Evidence

{_render_evidence_links(active_state.evidence_links)}

### Authority

- Task: {active_state.authority.task}
- Implementation: {active_state.authority.implementation}
- Publication: {active_state.authority.publication}

Repository state and Atlas do not establish authority."""


def _generated_context_active_state_section(
    context: str,
) -> tuple[str | None, str]:
    lines = context.splitlines()
    headings = [
        index
        for index, line in enumerate(lines)
        if line == GENERATED_CONTEXT_ACTIVE_STATE_HEADING
    ]

    if len(headings) != 1:
        return (
            None,
            (
                "Expected exactly one Canonical Active State section; "
                f"found {len(headings)}."
            ),
        )

    start = headings[0]
    end = next(
        (
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith("## ")
        ),
        len(lines),
    )
    section = "\n".join(lines[start:end]).rstrip("\n")
    return section, (
        "Compared the exact Canonical Active State section with the shared "
        "canonical-state rendering contract."
    )


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
    try:
        active_state = load_active_state()
    except ActiveStateError as error:
        return [
            finding(
                domain="Canonical Active State",
                severity="Error",
                summary="Canonical active state is invalid.",
                evidence=str(error),
                recommended_action=(
                    "Correct docs/current-state.json before relying on mission "
                    "synchronization."
                ),
            )
        ]

    phase = mission_phase()
    milestone = next_milestone()
    expected_phase = active_state.phase.display_name
    checkpoint = active_state.work_selection.selected_checkpoint
    expected_milestone = (
        checkpoint.name
        if checkpoint is not None
        else "Intentional idle — no engineering checkpoint is selected."
    )

    return [
        finding(
            domain="Canonical Active State",
            severity="OK",
            summary="Canonical active state is valid.",
            evidence=(
                f"Schema version: {active_state.schema_version}; "
                f"effective date: {active_state.freshness.effective_date.isoformat()}"
            ),
            recommended_action="No action required.",
        ),
        finding(
            domain="Active State ↔ Current Mission",
            severity="OK" if phase == expected_phase else "Error",
            summary=(
                "Current Mission phase agrees with canonical active state."
                if phase == expected_phase
                else "Current Mission phase disagrees with canonical active state."
            ),
            evidence=(
                f"Canonical phase: {expected_phase}; "
                f"Current Mission phase: {phase}"
            ),
            recommended_action=(
                "No action required."
                if phase == expected_phase
                else (
                    "Update the Current Mission companion; machine-readable "
                    "state wins on conflict."
                )
            ),
        ),
        finding(
            domain="Active State ↔ Current Mission",
            severity="OK" if milestone == expected_milestone else "Error",
            summary=(
                "Current Mission next milestone agrees with canonical work selection."
                if milestone == expected_milestone
                else (
                    "Current Mission next milestone disagrees with canonical "
                    "work selection."
                )
            ),
            evidence=(
                f"Canonical selection: {expected_milestone}; "
                f"Current Mission next milestone: {milestone}"
            ),
            recommended_action=(
                "No action required."
                if milestone == expected_milestone
                else (
                    "Update the Current Mission companion; machine-readable "
                    "state wins on conflict."
                )
            ),
        ),
    ]


def check_generated_context() -> list[SynchronizationFinding]:
    context = read_repository_file("docs/aiden-context.md")
    try:
        active_state = load_active_state()
    except ActiveStateError as error:
        return [
            finding(
                domain="Generated Context",
                severity="Error",
                summary=(
                    "Generated context cannot be checked against invalid "
                    "canonical active state."
                ),
                evidence=str(error),
                recommended_action=(
                    "Correct docs/current-state.json, then regenerate AI context."
                ),
            )
        ]

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

    expected = render_generated_context_active_state(active_state)
    actual, comparison_evidence = _generated_context_active_state_section(context)
    projection_matches = actual == expected
    generation_marker_present = "Generated:" in context

    return [
        finding(
            domain="Generated Context",
            severity="OK" if projection_matches else "Error",
            summary=(
                "Generated context exactly matches the canonical active-state projection."
                if projection_matches
                else (
                    "Generated context does not exactly match the canonical "
                    "active-state projection."
                )
            ),
            evidence=comparison_evidence,
            recommended_action=(
                "No action required."
                if projection_matches
                else "Regenerate docs/aiden-context.md from canonical sources."
            ),
        ),
        finding(
            domain="Generated Context",
            severity="OK" if generation_marker_present else "Error",
            summary=(
                "Generated context includes a generation marker."
                if generation_marker_present
                else "Generated context does not include a generation marker."
            ),
            evidence="Checked docs/aiden-context.md for a Generated marker.",
            recommended_action=(
                "No action required."
                if generation_marker_present
                else "Regenerate AI context with a generation marker."
            ),
        ),
    ]


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
