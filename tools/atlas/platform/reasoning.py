from dataclasses import dataclass, field

from atlas.platform.document_catalog import Document, DocumentCatalog
from atlas.platform.engineering_state import EngineeringState


FOCUS_DOCUMENT_PATHS = [
    "docs/architecture/reasoning.md",
    "docs/architecture/atlas.md",
    "docs/architecture/repository.md",
    "docs/roadmaps/engineering-toolkit.md",
]


@dataclass(frozen=True)
class ImpactReport:
    target: Document
    related_documents: list[Document] = field(default_factory=list)
    generated_outputs: list[Document] = field(default_factory=list)
    suggested_actions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GuidanceReport:
    current_phase: str
    recommended_action: str
    reason: str
    reasoning_context: list[str] = field(default_factory=list)
    relevant_documents: list[Document] = field(default_factory=list)
    suggested_commands: list[str] = field(default_factory=list)


def unique_documents(documents: list[Document]) -> list[Document]:
    seen: set[str] = set()
    unique: list[Document] = []

    for document in documents:
        if document.path in seen:
            continue

        seen.add(document.path)
        unique.append(document)

    return unique


def analyze_impact(catalog: DocumentCatalog, target: Document) -> ImpactReport:
    definition = target.definition

    related_documents: list[Document] = []
    generated_outputs: list[Document] = []
    suggested_actions: list[str] = []

    if definition is not None:
        for related_path in definition.related:
            related = catalog.find(related_path)
            if related is not None:
                related_documents.append(related)

    for document in catalog.documents:
        if document.definition is None:
            continue

        if target.path in document.definition.generated_from:
            generated_outputs.append(document)

    related_documents = unique_documents(related_documents)
    generated_outputs = unique_documents(generated_outputs)

    if target.definition and target.definition.canonical:
        suggested_actions.append("Review related canonical and generated documents.")

    if generated_outputs:
        suggested_actions.append("Regenerate or review generated context artifacts.")

    if target.definition and target.definition.generated:
        suggested_actions.append("Update canonical sources instead of editing this generated file directly.")

    if not suggested_actions:
        suggested_actions.append("Review the target document and related repository context.")

    return ImpactReport(
        target=target,
        related_documents=related_documents,
        generated_outputs=generated_outputs,
        suggested_actions=suggested_actions,
    )


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
            suggested_commands=[
                "git status",
                "git diff",
                "python3 tools/atlas.py state",
            ],
        )

    if state.mission_phase == "Unknown":
        return GuidanceReport(
            current_phase=state.mission_phase,
            recommended_action="Restore or update docs/current-mission.md so Atlas can determine the active phase.",
            reason="Atlas depends on current mission documentation as the source of planning truth.",
            reasoning_context=reasoning_context(catalog, reasoning_doc),
            relevant_documents=relevant_documents,
            suggested_commands=[
                "python3 tools/atlas.py docs",
                "python3 tools/atlas.py explain docs/current-mission.md",
            ],
        )

    if state.next_milestone == "Unknown":
        return GuidanceReport(
            current_phase=state.mission_phase,
            recommended_action="Define the next milestone in docs/current-mission.md.",
            reason="Atlas needs an explicit next milestone before it can provide reliable engineering guidance.",
            reasoning_context=reasoning_context(catalog, reasoning_doc),
            relevant_documents=relevant_documents,
            suggested_commands=[
                "python3 tools/atlas.py explain docs/current-mission.md",
                "code docs/current-mission.md",
            ],
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
