from atlas.platform.document_catalog import Document, DocumentCatalog
from atlas.platform.reasoning.models import ImpactReport


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
    related_documents: list[Document] = []
    generated_outputs: list[Document] = []
    suggested_actions: list[str] = []

    if target.definition is not None:
        for related_path in target.definition.related:
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
