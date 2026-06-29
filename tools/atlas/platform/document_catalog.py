from dataclasses import dataclass

from atlas.platform.document_definitions import DocumentDefinition, definition_for


@dataclass(frozen=True)
class Document:
    name: str
    path: str
    layer: str
    definition: DocumentDefinition | None = None

    @property
    def has_definition(self) -> bool:
        return self.definition is not None


@dataclass(frozen=True)
class DocumentCatalog:
    documents: list[Document]

    def by_layer(self, layer: str) -> list[Document]:
        return [
            document
            for document in self.documents
            if document.layer == layer
        ]

    def paths_by_layer(self, layer: str) -> list[str]:
        return [
            document.path
            for document in self.by_layer(layer)
        ]

    def find(self, query: str) -> Document | None:
        normalized = query.strip()

        for document in self.documents:
            if document.path == normalized:
                return document

            if document.name == normalized:
                return document

            if document.name.removesuffix(".md") == normalized:
                return document

        return None 

    def with_definitions(self) -> list[Document]:
        return [
            document
            for document in self.documents
            if document.has_definition
        ]

    def without_definitions(self) -> list[Document]:
        return [
            document
            for document in self.documents
            if not document.has_definition
        ]


def make_document(name: str, path: str, layer: str) -> Document:
    return Document(
        name=name,
        path=path,
        layer=layer,
        definition=definition_for(path),
    )
