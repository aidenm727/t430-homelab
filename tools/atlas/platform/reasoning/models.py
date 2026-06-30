from dataclasses import dataclass, field

from atlas.platform.document_catalog import Document


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
