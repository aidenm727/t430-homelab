from dataclasses import dataclass, field

from atlas.platform.document_catalog import Document, DocumentCatalog


@dataclass(frozen=True)
class ImpactReport:
    target: Document
    related_documents: list[Document] = field(default_factory=list)
    generated_outputs: list[Document] = field(default_factory=list)
    suggested_actions: list[str] = field(default_factory=list)


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
