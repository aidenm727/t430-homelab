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
    milestone_satisfied_criteria: list[str]
    milestone_unsatisfied_criteria: list[str]
    milestone_next_actions: list[str]
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
    milestone_satisfied_criteria: list[str]
    milestone_unsatisfied_criteria: list[str]
    milestone_next_actions: list[str]
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
class OpportunityAssessmentFact:
    name: str
    value: str
    source: str


@dataclass(frozen=True)
class OpportunityAssessmentFinding:
    code: str
    severity: str
    statement: str
    evidence: tuple[str, ...] = ()
    confidence: str = "High"


@dataclass(frozen=True)
class OpportunityRelationshipFinding:
    relationship_type: str
    source_opportunity_id: str
    target_opportunity_id: str
    directionality: str
    evidence: tuple[str, ...]
    explanation: str
    confidence: str = "High"


@dataclass(frozen=True)
class OpportunityAssessmentRecommendation:
    action: str
    reason: str
    confidence: str


@dataclass(frozen=True)
class OpportunityCapabilityAlignment:
    opportunity_id: str
    repository_path: str
    declared_value: str
    alignment_state: str
    primary_capability_id: str | None
    primary_capability_label: str | None
    candidate_capability_ids: tuple[str, ...]
    secondary_capability_ids: tuple[str, ...]
    evidence: tuple[str, ...]
    provenance: tuple[str, ...]
    explanation: str
    confidence: str
    blockers: tuple[str, ...]
    unresolved_questions: tuple[str, ...]
    recommendation: OpportunityAssessmentRecommendation | None = None


@dataclass(frozen=True)
class OpportunityScopeEvidence:
    evidence_type: str
    source: str
    statement: str
    scope_id: str | None = None


@dataclass(frozen=True)
class OpportunityScopeClassification:
    opportunity_id: str
    repository_path: str
    classification_state: str
    primary_scope_id: str | None
    primary_scope_label: str | None
    leading_candidate_scope_id: str | None
    candidate_scope_ids: tuple[str, ...]
    secondary_scope_ids: tuple[str, ...]
    facts: tuple[OpportunityScopeEvidence, ...]
    evidence: tuple[OpportunityScopeEvidence, ...]
    counterevidence: tuple[OpportunityScopeEvidence, ...]
    provenance: tuple[str, ...]
    explanation: str
    confidence: str
    blockers: tuple[str, ...]
    unresolved_questions: tuple[str, ...]
    recommendation: OpportunityAssessmentRecommendation | None = None


@dataclass(frozen=True)
class OpportunityDistinctnessEvidence:
    evidence_type: str
    source: str
    statement: str
    field_name: str | None = None
    relationship_type: str | None = None


@dataclass(frozen=True)
class OpportunityDistinctnessSkippedPair:
    pair_key: str
    left_opportunity_id: str
    right_opportunity_id: str
    reason: str


@dataclass(frozen=True)
class OpportunityDistinctnessComparison:
    pair_key: str
    left_opportunity_id: str
    left_repository_path: str
    right_opportunity_id: str
    right_repository_path: str
    analysis_state: str
    relationship_type: str | None
    inverse_relationship_type: str | None
    source_opportunity_id: str | None
    target_opportunity_id: str | None
    canonical_target_candidate_id: str | None
    alternative_relationship_types: tuple[str, ...]
    facts: tuple[OpportunityDistinctnessEvidence, ...]
    supporting_evidence: tuple[OpportunityDistinctnessEvidence, ...]
    counterevidence: tuple[OpportunityDistinctnessEvidence, ...]
    boundary_evidence: tuple[OpportunityDistinctnessEvidence, ...]
    provenance: tuple[str, ...]
    explanation: str
    confidence: str
    blockers: tuple[str, ...]
    unresolved_questions: tuple[str, ...]
    recommendation: OpportunityAssessmentRecommendation | None = None


@dataclass(frozen=True)
class OpportunityDistinctnessPortfolio:
    opportunity_ids: tuple[str, ...]
    comparison_count: int
    skipped_pair_count: int
    comparisons: tuple[OpportunityDistinctnessComparison, ...]
    skipped_pairs: tuple[OpportunityDistinctnessSkippedPair, ...]
    findings_by_opportunity: tuple[tuple[str, tuple[str, ...]], ...]
    provenance: tuple[str, ...]


@dataclass(frozen=True)
class EngineeringOpportunityAssessment:
    opportunity_id: str
    lifecycle_state: str
    repository_path: str
    facts: tuple[OpportunityAssessmentFact, ...] = ()
    findings: tuple[OpportunityAssessmentFinding, ...] = ()
    relationships: tuple[OpportunityRelationshipFinding, ...] = ()
    capability_alignment: OpportunityCapabilityAlignment | None = None
    scope_classification: OpportunityScopeClassification | None = None
    distinctness_comparisons: tuple[OpportunityDistinctnessComparison, ...] = ()
    recommendation: OpportunityAssessmentRecommendation | None = None
    blockers: tuple[str, ...] = ()
    unresolved_questions: tuple[str, ...] = ()


@dataclass(frozen=True)
class MilestoneCompletionReport:
    status: str
    confidence: str
    evidence: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    satisfied_criteria: list[str] = field(default_factory=list)
    unsatisfied_criteria: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
