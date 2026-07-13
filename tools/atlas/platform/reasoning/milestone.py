from atlas.platform.document_catalog import DocumentCatalog
from atlas.platform.engineering_state import EngineeringState
from atlas.platform.repository import repo_root
from atlas.platform.reasoning.models import MilestoneCompletionReport


SYNCHRONIZATION_MILESTONE_TEXT = "Build Repository Synchronization Reasoning"
ENGINEERING_REVIEW_MILESTONE_TEXT = (
    "Strengthen Engineering Review as the primary Atlas engineering checkpoint"
)
OPPORTUNITY_INTELLIGENCE_MILESTONE_TEXT = (
    "Design Engineering Opportunity Intelligence"
)
OPPORTUNITY_ASSESSMENT_MILESTONE_TEXT = (
    "Build Engineering Opportunity Assessment Foundation"
)
OPPORTUNITY_EVIDENCE_MILESTONE_TEXT = (
    "Build Engineering Opportunity Evidence Foundation"
)
OPPORTUNITY_RELATIONSHIP_MILESTONE_TEXT = (
    "Build Engineering Opportunity Relationship Foundation"
)


def _path_evidence(required_paths: list[str]) -> tuple[list[str], list[str]]:
    evidence: list[str] = []
    missing: list[str] = []

    for path in required_paths:
        if (repo_root() / path).exists():
            evidence.append(f"{path} exists.")
        else:
            missing.append(f"{path} is missing.")

    return evidence, missing


def _implementation_evidence(
    requirements: dict[str, dict[str, str]],
) -> tuple[list[str], list[str]]:
    evidence: list[str] = []
    missing: list[str] = []

    for path, required_markers in requirements.items():
        full_path = repo_root() / path

        if not full_path.exists():
            missing.append(f"{path} is missing.")
            continue

        evidence.append(f"{path} exists.")
        content = full_path.read_text(encoding="utf-8")

        for marker, description in required_markers.items():
            if marker in content:
                evidence.append(f"{path}: {description}.")
            else:
                missing.append(
                    f"{path} is missing implementation evidence: "
                    f"{description}."
                )

    return evidence, missing


def _document_design_evidence(
    catalog: DocumentCatalog,
    requirements: dict[str, dict[str, str]],
) -> tuple[list[str], list[str]]:
    evidence: list[str] = []
    missing: list[str] = []

    for path, required_markers in requirements.items():
        full_path = repo_root() / path

        if not full_path.exists():
            missing.append(f"{path} is missing.")
            continue

        evidence.append(f"{path} exists.")

        document = catalog.find(path)

        if document is None:
            missing.append(
                f"{path} is not discovered by Repository Knowledge."
            )
        elif not document.has_definition:
            missing.append(
                f"{path} is missing registered document metadata."
            )
        else:
            evidence.append(
                f"{path} is registered in document metadata."
            )

        document_content = full_path.read_text(encoding="utf-8")

        for marker, description in required_markers.items():
            if marker in document_content:
                evidence.append(f"{path}: {description}.")
            else:
                missing.append(
                    f"{path} is missing required design evidence: "
                    f"{description}."
                )

    return evidence, missing


def build_milestone_completion(
    catalog: DocumentCatalog,
    state: EngineeringState,
) -> MilestoneCompletionReport:
    milestone = state.next_milestone

    if OPPORTUNITY_RELATIONSHIP_MILESTONE_TEXT in milestone:
        requirements = {
            "tools/atlas/platform/reasoning/models.py": {
                "class OpportunityRelationshipFinding":
                    "defines typed opportunity relationship findings",
                "relationships: tuple[OpportunityRelationshipFinding, ...]":
                    "attaches relationship findings to reusable assessments",
            },
            "tools/atlas/platform/reasoning/opportunity_relationships.py": {
                "def build_opportunity_relationships":
                    "builds a deterministic portfolio relationship view",
                'relationship_type="depends_on"':
                    "represents explicit dependencies directionally",
                'relationship_type="enables"':
                    "represents deterministic inverse enablement",
                'relationship_type="related_to"':
                    "represents generic explicit relationships",
            },
            "tools/atlas/platform/reasoning/opportunity_assessment.py": {
                "self-opportunity-relationship":
                    "reports explicit self references",
                "duplicate-relationship-declaration":
                    "reports duplicate declarations",
                "conflicting-relationship-declaration":
                    "reports conflicting explicit inputs",
                "relationships_by_source":
                    "attaches portfolio relationships to assessments",
            },
            "tests/test_opportunity_relationships.py": {
                "test_dependency_builds_directional_and_inverse_relationships":
                    "tests dependency and inverse enablement findings",
                "test_related_opportunity_builds_declared_relationship":
                    "tests generic explicit relationships",
                "test_self_reference_produces_finding":
                    "tests self-reference diagnostics",
                "test_duplicate_declaration_produces_finding":
                    "tests duplicate declaration diagnostics",
                "test_conflicting_declarations_produce_finding":
                    "tests conflicting relationship diagnostics",
                "test_absent_relationships_remain_valid":
                    "tests opportunities without relationships",
            },
        }

        evidence, missing = _implementation_evidence(requirements)

        if not missing:
            return MilestoneCompletionReport(
                status="Complete",
                confidence="High",
                evidence=evidence,
                missing_evidence=[],
                satisfied_criteria=[
                    "A reusable typed opportunity-relationship model exists.",
                    "Relationship findings preserve source, target, type, directionality, evidence, explanation, and confidence.",
                    "Explicit dependencies produce directional depends_on findings.",
                    "Dependency targets expose deterministic inverse enables findings.",
                    "Explicit related opportunities produce related_to findings without semantic inference.",
                    "A deterministic portfolio relationship view is reusable by assessments.",
                    "Self-references produce explicit findings and blockers.",
                    "Duplicate declarations produce explicit findings and blockers.",
                    "Conflicting explicit inputs produce explicit findings and blockers.",
                    "Objects without explicit relationships remain valid and assessable.",
                    "Relationship reasoning remains independent of command rendering.",
                    "Canonical objects and lifecycle state are not mutated.",
                ],
                unsatisfied_criteria=[],
                next_actions=[
                    "The Engineering Opportunity Relationship foundation is implemented. Verify, document, commit, and consider advancing the mission.",
                ],
            )

        return MilestoneCompletionReport(
            status="In Progress",
            confidence="Medium",
            evidence=evidence,
            missing_evidence=missing,
            satisfied_criteria=evidence,
            unsatisfied_criteria=missing,
            next_actions=[
                "Complete the missing Engineering Opportunity Relationship foundation evidence.",
            ],
        )

    if OPPORTUNITY_EVIDENCE_MILESTONE_TEXT in milestone:
        requirements = {
            "tools/atlas/platform/repository_objects/models.py": {
                "dependencies: tuple[str, ...]":
                    "preserves explicit dependency references",
                "related_opportunities: tuple[str, ...]":
                    "preserves explicit opportunity relationships",
                "related_documents: tuple[str, ...]":
                    "preserves related repository documents",
                "evidence: tuple[str, ...]":
                    "preserves structured evidence items",
            },
            "tools/atlas/platform/repository_objects/loader.py": {
                "def load_repository_object":
                    "builds one normalized repository object",
                "def _sequence_value":
                    "normalizes bounded YAML sequences and evidence",
                "dependencies=_sequence_value":
                    "loads dependency references",
                "related_opportunities=_sequence_value":
                    "loads related opportunity references",
                "related_documents=_sequence_value":
                    "loads related document references",
                "evidence=_sequence_value":
                    "loads structured evidence",
            },
            "tools/atlas/platform/reasoning/opportunity_assessment.py": {
                "def assess_engineering_opportunities":
                    "assesses objects against a discovered inventory",
                "missing-opportunity-reference":
                    "reports unresolved opportunity references",
                "missing-document-reference":
                    "reports unresolved document references",
                "explicit-references-valid":
                    "reports successful explicit-reference validation",
                '"evidence-item"':
                    "exposes structured evidence as source-backed facts",
            },
            "tests/test_opportunity_assessment.py": {
                "test_loader_preserves_bounded_sequences_and_evidence":
                    "tests structured object loading",
                "test_valid_explicit_references":
                    "tests valid opportunity and document references",
                "test_missing_opportunity_target":
                    "tests unresolved opportunity references",
                "test_missing_document_target":
                    "tests unresolved document references",
                "test_absent_optional_references_remain_valid":
                    "tests objects without optional references",
            },
        }

        evidence, missing = _implementation_evidence(requirements)

        if not missing:
            return MilestoneCompletionReport(
                status="Complete",
                confidence="High",
                evidence=evidence,
                missing_evidence=[],
                satisfied_criteria=[
                    "Opportunity objects preserve structured dependencies, relationships, documents, and evidence.",
                    "The bounded YAML loader preserves top-level sequences and evidence items.",
                    "Assessments expose explicit references and evidence as source-backed facts.",
                    "Opportunity references are validated against discovered repository objects.",
                    "Document references are validated against repository files.",
                    "Missing references produce deterministic findings and blockers.",
                    "Objects without optional references remain valid and assessable.",
                    "Focused tests cover valid and missing reference cases.",
                    "Assessment reasoning remains independent of command rendering.",
                    "Canonical objects and lifecycle state are not mutated.",
                ],
                unsatisfied_criteria=[],
                next_actions=[
                    "The Engineering Opportunity Evidence foundation is implemented. Verify, document, commit, and consider advancing the mission.",
                ],
            )

        return MilestoneCompletionReport(
            status="In Progress",
            confidence="Medium",
            evidence=evidence,
            missing_evidence=missing,
            satisfied_criteria=evidence,
            unsatisfied_criteria=missing,
            next_actions=[
                "Complete the missing Engineering Opportunity Evidence foundation evidence.",
            ],
        )

    if OPPORTUNITY_ASSESSMENT_MILESTONE_TEXT in milestone:
        requirements = {
            "tools/atlas/platform/reasoning/models.py": {
                "class OpportunityAssessmentFact":
                    "defines source-backed assessment facts",
                "class OpportunityAssessmentFinding":
                    "defines confidence-aware findings",
                "class OpportunityAssessmentRecommendation":
                    "defines bounded recommendations",
                "class EngineeringOpportunityAssessment":
                    "defines the reusable assessment output",
            },
            "tools/atlas/platform/reasoning/opportunity_assessment.py": {
                "def assess_engineering_opportunity":
                    "implements reusable single-object assessment",
                "missing-required-fields":
                    "checks required object fields",
                "invalid-identifier":
                    "checks stable identifier format",
                "lifecycle-path-mismatch":
                    "checks lifecycle and repository placement",
                "retain-captured":
                    "preserves lifecycle authority",
            },
            "tools/atlas/platform/repository_objects/loader.py": {
                '"rationale",':
                    "loads rationale as a required canonical field",
                'raw_value in {">", "|"}':
                    "supports folded and literal YAML blocks",
            },
            "tests/test_opportunity_assessment.py": {
                "test_valid_captured_object":
                    "tests valid object assessment",
                "test_incomplete_object":
                    "tests missing required fields",
                "test_inconsistent_object":
                    "tests identifier and lifecycle inconsistency",
            },
        }

        evidence, missing = _implementation_evidence(requirements)

        if not missing:
            return MilestoneCompletionReport(
                status="Complete",
                confidence="High",
                evidence=evidence,
                missing_evidence=[],
                satisfied_criteria=[
                    "A reusable Engineering Opportunity Assessment data model exists.",
                    "Facts, findings, and recommendations are separated.",
                    "Assessment evidence and confidence are explicit.",
                    "Existing repository objects are assessed without mutation.",
                    "Required fields and rationale are evaluated deterministically.",
                    "Stable identifiers are evaluated deterministically.",
                    "Lifecycle state and repository placement are evaluated deterministically.",
                    "Valid, incomplete, and inconsistent object cases are tested.",
                    "Assessment reasoning remains independent of command rendering.",
                    "Human lifecycle authority is preserved.",
                ],
                unsatisfied_criteria=[],
                next_actions=[
                    "The Engineering Opportunity Assessment foundation is implemented. Verify, document, commit, and consider advancing the mission.",
                ],
            )

        return MilestoneCompletionReport(
            status="In Progress",
            confidence="Medium",
            evidence=evidence,
            missing_evidence=missing,
            satisfied_criteria=evidence,
            unsatisfied_criteria=missing,
            next_actions=[
                "Complete the missing Engineering Opportunity Assessment foundation evidence.",
            ],
        )

    if OPPORTUNITY_INTELLIGENCE_MILESTONE_TEXT in milestone:
        requirements = {
            "docs/architecture/engineering-opportunity.md": {
                "## Opportunity Lifecycle":
                    "defines the opportunity lifecycle",
                "## Repository Ownership":
                    "defines repository ownership",
            },
            "docs/architecture/engineering-opportunity-object.md": {
                "## Required Fields":
                    "defines the repository object contract",
                "## Lifecycle":
                    "defines object lifecycle behavior",
                "## Relationship to Engineering Opportunity Intelligence":
                    "defines the object and reasoning boundary",
            },
            "docs/architecture/engineering-opportunity-intelligence.md": {
                "## Architectural Position":
                    "defines architectural placement",
                "## Relationship to Engineering Opportunity Assessment":
                    "defines the assessment boundary",
                "## Human Decision and Lifecycle Mutation":
                    "preserves human lifecycle authority",
                "## Initial Implementation Boundary":
                    "defines the initial implementation boundary",
            },
            "docs/architecture/engineering-opportunity-assessment.md": {
                "## Assessment Layers":
                    "separates facts, findings, and recommendations",
                "## Relationship Model":
                    "defines opportunity relationships",
                "## Determinism and Engineering Judgment":
                    "defines deterministic and judgment boundaries",
                "## Structured Assessment Contract":
                    "defines the structured assessment contract",
                "## Human Decision Boundary":
                    "preserves human decision authority",
                "## Initial Assessment Boundary":
                    "defines the initial assessment scope",
            },
        }

        evidence, missing = _document_design_evidence(
            catalog,
            requirements,
        )

        if not missing:
            return MilestoneCompletionReport(
                status="Complete",
                confidence="High",
                evidence=evidence,
                missing_evidence=[],
                satisfied_criteria=[
                    "Engineering Opportunity lifecycle and repository ownership are designed.",
                    "Engineering Opportunity Object structure and lifecycle are designed.",
                    "Engineering Opportunity Intelligence is positioned as Repository Reasoning.",
                    "Engineering Opportunity Assessment is separated from canonical objects.",
                    "Scope, relationships, evaluation, confidence, and recommendations are defined.",
                    "Deterministic reasoning is separated from heuristic and human judgment.",
                    "Lifecycle mutation remains human-authorized.",
                    "The initial implementation boundary is documented.",
                    "Required architecture documents are registered in repository metadata.",
                ],
                unsatisfied_criteria=[],
                next_actions=[
                    "Current milestone design criteria are satisfied. Advance docs/current-mission.md before beginning the next milestone.",
                ],
            )

        return MilestoneCompletionReport(
            status="In Progress",
            confidence="Medium",
            evidence=evidence,
            missing_evidence=missing,
            satisfied_criteria=evidence,
            unsatisfied_criteria=missing,
            next_actions=[
                "Complete the missing Engineering Opportunity Intelligence design evidence before advancing the mission.",
            ],
        )

    if ENGINEERING_REVIEW_MILESTONE_TEXT in milestone:
        required_paths = [
            "docs/architecture/engineering-review.md",
            "docs/architecture/engineering-intelligence.md",
            "tools/atlas/platform/reasoning/review.py",
            "tools/atlas/platform/reasoning/intelligence.py",
            "tools/atlas/commands/review.py",
            "tools/atlas/commands/bootstrap.py",
        ]

        evidence, missing = _path_evidence(required_paths)

        if not missing:
            return MilestoneCompletionReport(
                status="Complete",
                confidence="High",
                evidence=evidence,
                missing_evidence=missing,
                satisfied_criteria=[
                    "Engineering Review architecture exists.",
                    "Engineering Intelligence architecture exists.",
                    "Engineering Interpretation architecture exists.",
                    "Engineering Review reasoning implementation exists.",
                    "Engineering Intelligence composition exists.",
                    "Engineering Interpretation implementation exists.",
                    "Milestone reasoning produces structured criteria instead of recommendation text.",
                    "Review command exposes Engineering Review.",
                    "Bootstrap command consumes Engineering Review.",
                ],
                unsatisfied_criteria=[],
                next_actions=[
                    "Current milestone criteria are satisfied. Consider advancing docs/current-mission.md.",
                ],
            )

        return MilestoneCompletionReport(
            status="In Progress",
            confidence="Medium",
            evidence=evidence,
            missing_evidence=missing,
            satisfied_criteria=evidence,
            unsatisfied_criteria=missing,
            next_actions=[
                "Create the missing Engineering Review foundation files.",
            ],
        )

    if SYNCHRONIZATION_MILESTONE_TEXT in milestone:
        required_paths = [
            "docs/architecture/repository-synchronization.md",
            "tools/atlas/platform/reasoning/synchronization.py",
            "tools/atlas/commands/sync.py",
        ]

        evidence, missing = _path_evidence(required_paths)

        if not missing:
            return MilestoneCompletionReport(
                status="Complete",
                confidence="High",
                evidence=evidence,
                missing_evidence=missing,
                satisfied_criteria=evidence,
                unsatisfied_criteria=[],
                next_actions=[
                    "Consider advancing docs/current-mission.md.",
                ],
            )

        return MilestoneCompletionReport(
            status="In Progress",
            confidence="Medium",
            evidence=evidence,
            missing_evidence=missing,
            satisfied_criteria=evidence,
            unsatisfied_criteria=missing,
            next_actions=[
                "Continue implementing Repository Synchronization Reasoning before advancing the mission.",
            ],
        )

    return MilestoneCompletionReport(
        status="Unknown",
        confidence="Low",
        evidence=[
            f"Current milestone is not recognized by milestone reasoning: {milestone}"
        ],
        missing_evidence=[],
        satisfied_criteria=[],
        unsatisfied_criteria=[
            "No milestone-specific reasoning rule matched the current mission milestone.",
        ],
        next_actions=[
            "Add a milestone reasoning rule for the current mission milestone.",
        ],
    )
