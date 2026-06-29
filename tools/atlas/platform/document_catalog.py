from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    name: str
    path: str
    layer: str


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
