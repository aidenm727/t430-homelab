from atlas.platform.document_catalog import Document, DocumentCatalog
from atlas.platform.engineering_state import EngineeringState
from atlas.platform.reasoning.impact import analyze_impact
from atlas.platform.reasoning.models import GuidanceReport


FOCUS_DOCUMENT_PATHS = [
    "docs/architecture/engineering-review.md",
    "docs/architecture/engineering-intelligence.md",
    "docs/architecture/mission-advancement.md",
    "docs/architecture/reasoning.md",
    "docs/architecture/atlas.md",
    "docs/architecture/repository.md",
    "docs/roadmaps/engineering-toolkit.md",
]


def reasoning_context(catalog: DocumentCatalog, reasoning_doc: Document | None) -> list[str]:
    if reasoning_doc is None:
        return [
            "Repository reasoning architecture is not documented yet.",
            "Create docs/architecture/reasoning.md before expanding reasoning commands.",
        ]

    report = analyze_impact(catalog, reasoning_doc)

    return [
        "Repository reasoning architecture exists.",
        f"Atlas can inspect {len(report.related_documents)} directly related document(s).",
        f"Atlas can identify {len(report.generated_outputs)} generated output(s) affected by reasoning architecture changes.",
    ]


def build_guidance(catalog: DocumentCatalog, state: EngineeringState) -> GuidanceReport:
    reasoning_doc = catalog.find("docs/architecture/reasoning.md")
    relevant_documents = [
        document
        for path in FOCUS_DOCUMENT_PATHS
        if (document := catalog.find(path)) is not None
    ]

    if state.state_blockers:
        return GuidanceReport(
            current_phase=state.mission_phase,
            recommended_action="Resolve the blockers recorded in canonical active state.",
            reason=(
                "Canonical blockers take priority over work-selection guidance; "
                "Atlas does not grant authority to resolve them."
            ),
            reasoning_context=reasoning_context(catalog, reasoning_doc),
            relevant_documents=relevant_documents,
            suggested_commands=["./atlas state", "./atlas validate", "./atlas sync"],
        )

    if state.decision_required is not None:
        return GuidanceReport(
            current_phase=state.mission_phase,
            recommended_action=(
                "Prioritize the pending explicit owner decision: "
                f"{state.decision_required} Atlas reports that decision but "
                "does not establish or grant authority to make or act on it."
            ),
            reason=(
                "Canonical active state records a pending owner decision. That "
                "decision takes precedence over implementation-authority "
                "guidance; task, implementation, and publication authority "
                "remain external and are not established by repository state "
                "or Atlas."
            ),
            reasoning_context=reasoning_context(catalog, reasoning_doc),
            relevant_documents=relevant_documents,
            suggested_commands=[
                "./atlas state",
                "./atlas review",
                "./atlas validate",
                "./atlas sync",
            ],
        )

    if state.intentional_idle:
        return GuidanceReport(
            current_phase=state.mission_phase,
            recommended_action=(
                "Remain intentionally idle until explicit owner instruction "
                "selects work and establishes any required authority."
            ),
            reason=(
                "Canonical active state intentionally selects no checkpoint, "
                "and Atlas does not select or authorize work."
            ),
            reasoning_context=reasoning_context(catalog, reasoning_doc),
            relevant_documents=relevant_documents,
            suggested_commands=[
                "./atlas state",
                "./atlas review",
                "./atlas validate",
                "./atlas sync",
            ],
        )

    checkpoint = state.selected_checkpoint
    return GuidanceReport(
        current_phase=state.mission_phase,
        recommended_action=(
            "Obtain or follow explicit bounded owner task and implementation "
            f"authority for {checkpoint}; Atlas does not establish that authority."
        ),
        reason=(
            "Canonical state selects the checkpoint, while task, implementation, "
            "and publication authority remain external and are not established "
            "by repository state or Atlas."
        ),
        reasoning_context=reasoning_context(catalog, reasoning_doc),
        relevant_documents=relevant_documents,
        suggested_commands=[
            "./atlas review",
            "./atlas validate",
            "./atlas sync",
            "./atlas bootstrap",
            "./atlas impact docs/architecture/engineering-review.md",
            "./atlas explain docs/architecture/engineering-review.md",
        ],
    )
