from atlas.platform.document_catalog import Document, DocumentCatalog
from atlas.platform.engineering_state import EngineeringState
from atlas.platform.reasoning.impact import analyze_impact
from atlas.platform.reasoning.models import GuidanceReport


FOCUS_DOCUMENT_PATHS = [
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

    if not state.repository_clean:
        return GuidanceReport(
            current_phase=state.mission_phase,
            recommended_action="Review and resolve current working tree changes before starting new work.",
            reason="Atlas avoids recommending new work while the repository has uncommitted changes.",
            reasoning_context=reasoning_context(catalog, reasoning_doc),
            relevant_documents=relevant_documents,
            suggested_commands=["git status", "git diff", "python3 tools/atlas.py state"],
        )

    return GuidanceReport(
        current_phase=state.mission_phase,
        recommended_action=state.next_milestone,
        reason=(
            "The current mission defines the next milestone, and Atlas can now use "
            "repository knowledge plus the reasoning layer to guide the next checkpoint."
        ),
        reasoning_context=reasoning_context(catalog, reasoning_doc),
        relevant_documents=relevant_documents,
        suggested_commands=[
            "python3 tools/atlas.py state",
            "python3 tools/atlas.py impact docs/architecture/reasoning.md",
            "python3 tools/atlas.py explain docs/architecture/reasoning.md",
        ],
    )
