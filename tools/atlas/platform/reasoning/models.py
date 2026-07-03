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


@dataclass(frozen=True)
class ValidationFinding:
    severity: str
    message: str


@dataclass(frozen=True)
class ValidationReport:
    errors: list[ValidationFinding] = field(default_factory=list)
    warnings: list[ValidationFinding] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class SynchronizationFinding:
    domain: str
    severity: str
    summary: str
    evidence: str
    recommended_action: str


@dataclass(frozen=True)
class SynchronizationReport:
    findings: list[SynchronizationFinding] = field(default_factory=list)

    @property
    def errors(self) -> list[SynchronizationFinding]:
        return [finding for finding in self.findings if finding.severity == "Error"]

    @property
    def warnings(self) -> list[SynchronizationFinding]:
        return [finding for finding in self.findings if finding.severity == "Warning"]

    @property
    def status(self) -> str:
        if self.errors:
            return "Unsynchronized"
        if self.warnings:
            return "Partially synchronized"
        return "Synchronized"



@dataclass(frozen=True)
class MissionAdvancementReport:
    recommendation: str
    confidence: str
    should_advance: bool
    reason: str
    suggested_action: str
    evidence: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EngineeringReviewReport:
    validation_status: str
    synchronization_status: str
    repository_clean: bool
    current_phase: str
    milestone_status: str
    milestone_confidence: str
    milestone_recommendation: str
    recommended_action: str
    reason: str
    blockers: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    relevant_documents: list[Document] = field(default_factory=list)
    suggested_commands: list[str] = field(default_factory=list)

    @property
    def health(self) -> str:
        if self.blockers:
            return "Blocked"
        if self.synchronization_status != "Synchronized":
            return "Needs attention"
        return "Ready"


@dataclass(frozen=True)
class EngineeringIntelligenceReport:
    validation_status: str
    milestone_status: str
    milestone_confidence: str
    milestone_recommendation: str
    mission_advancement_recommendation: str
    mission_advancement_confidence: str
    mission_should_advance: bool
    synchronization_status: str
    repository_clean: bool
    current_phase: str
    next_milestone: str
    blockers: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    relevant_documents: list[Document] = field(default_factory=list)
    suggested_commands: list[str] = field(default_factory=list)

    @property
    def health(self) -> str:
        if self.blockers:
            return "Blocked"
        if self.synchronization_status != "Synchronized":
            return "Needs attention"
        return "Ready"


@dataclass(frozen=True)
class MilestoneCompletionReport:
    status: str
    confidence: str
    evidence: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    satisfied_criteria: list[str] = field(default_factory=list)
    unsatisfied_criteria: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    recommendation: str = "No recommendation."
