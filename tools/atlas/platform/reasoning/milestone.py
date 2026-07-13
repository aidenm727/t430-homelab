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
OPPORTUNITY_CAPABILITY_ALIGNMENT_DESIGN_MILESTONE_TEXT = (
    "Design Engineering Opportunity Capability Alignment"
)
OPPORTUNITY_CAPABILITY_ALIGNMENT_MILESTONE_TEXT = (
    "Build Engineering Opportunity Capability Alignment Foundation"
)
OPPORTUNITY_SCOPE_CLASSIFICATION_DESIGN_MILESTONE_TEXT = (
    "Design Engineering Opportunity Scope Classification"
)
OPPORTUNITY_SCOPE_CLASSIFICATION_MILESTONE_TEXT = (
    "Build Engineering Opportunity Scope Classification Foundation"
)
OPPORTUNITY_DISTINCTNESS_ANALYSIS_DESIGN_MILESTONE_TEXT = (
    "Design Engineering Opportunity Distinctness Analysis"
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

    if OPPORTUNITY_DISTINCTNESS_ANALYSIS_DESIGN_MILESTONE_TEXT in milestone:
        design_requirements = {
            "docs/architecture/engineering-opportunity-distinctness-analysis.md": {
                "## Comparison Identity":
                    "defines stable unordered pair identity",
                "## Pairwise Analysis Model":
                    "defines reusable pairwise comparison",
                "## Portfolio Composition":
                    "defines deterministic portfolio comparison",
                "## Distinctness Outcomes":
                    "defines duplicate, overlap, component, umbrella, distinct, and insufficient outcomes",
                "## Directionality and Inverse Semantics":
                    "defines symmetric and directional relationships",
                "## Duplicate and Overlap Boundaries":
                    "separates redundancy from independent value",
                "## Component and Umbrella Boundaries":
                    "defines decomposition relationships",
                "## Explicit Relationship and Reference Evidence":
                    "defines existing relationship evidence roles",
                "## Capability-Aware Comparison":
                    "defines capability comparison boundaries",
                "## Scope-Aware Comparison":
                    "defines scope comparison boundaries",
                "## Text Normalization and Heuristic Boundaries":
                    "defines transparent semantic comparison limits",
                "## Evidence, Counterevidence, and Provenance":
                    "requires source-backed comparison evidence",
                "## Negative and Boundary Evidence":
                    "defines positive evidence for distinctness",
                "## Analysis States and Confidence":
                    "defines resolved, candidate, ambiguous, insufficient, and conflicting states",
                "## Canonical Target Candidates":
                    "defines non-mutating canonical target proposals",
                "## Structured Assessment Contracts":
                    "defines pairwise and portfolio outputs",
                "## Engineering Opportunity Assessment Integration":
                    "defines assessment composition",
                "## Recommendation Effects":
                    "keeps recommendations separate from mutation",
                "## Human Authority and Historical Traceability":
                    "preserves human merge authority and stable identity",
                "## Initial Implementation Boundary":
                    "defines bounded safe implementation",
                "## Verification Cases":
                    "defines focused implementation tests",
                "Keyword, token, embedding, or title similarity alone is never sufficient":
                    "rejects lexical similarity as duplication proof",
            },
            "docs/architecture/engineering-opportunity-assessment.md": {
                "docs/architecture/engineering-opportunity-distinctness-analysis.md":
                    "references the canonical Distinctness Analysis contract",
            },
        }
        registration_requirements = {
            "docs/architecture/repository.md": {
                "docs/architecture/engineering-opportunity-distinctness-analysis.md":
                    "lists the architecture in repository ownership",
            },
            "docs/docs-map.md": {
                "docs/architecture/engineering-opportunity-distinctness-analysis.md":
                    "lists the architecture in the documentation map",
            },
            "tools/atlas/platform/document_definitions.py": {
                '"docs/architecture/engineering-opportunity-distinctness-analysis.md"':
                    "registers architecture metadata",
            },
        }

        design_evidence, design_missing = _document_design_evidence(
            catalog,
            design_requirements,
        )
        registration_evidence, registration_missing = _implementation_evidence(
            registration_requirements,
        )
        evidence = design_evidence + registration_evidence
        missing = design_missing + registration_missing

        if not missing:
            return MilestoneCompletionReport(
                status="Complete",
                confidence="High",
                evidence=evidence,
                missing_evidence=[],
                satisfied_criteria=[
                    "Stable unordered pair identity is defined.",
                    "Reusable pairwise and portfolio comparison models are defined.",
                    "Duplicate, overlap, component, umbrella, distinct, and insufficient-evidence outcomes are explicit.",
                    "Symmetric, directional, and inverse relationship semantics are defined.",
                    "Duplicate and overlap boundaries preserve independent value.",
                    "Component and umbrella boundaries preserve decomposition.",
                    "Explicit relationships and references have bounded evidence roles.",
                    "Capability Alignment supports comparison without proving duplication.",
                    "Scope Classification constrains comparison without proving duplication.",
                    "Text normalization remains transparent and lexical similarity alone is insufficient.",
                    "Supporting evidence, counterevidence, boundary evidence, and provenance are required.",
                    "Positive boundary evidence is required for distinctness.",
                    "Resolved, candidate, ambiguous, insufficient-evidence, and conflicting states are defined.",
                    "Canonical-target candidates remain non-mutating recommendations.",
                    "Reusable pairwise and portfolio assessment contracts are defined.",
                    "Engineering Opportunity Assessment integration avoids duplicated comparison logic.",
                    "Recommendations remain separate from lifecycle and repository mutation.",
                    "Human merge authority and stable historical traceability are preserved.",
                    "The initial implementation boundary avoids false semantic certainty.",
                    "Focused verification cases are explicit.",
                    "The architecture is registered in Repository Knowledge.",
                ],
                unsatisfied_criteria=[],
                next_actions=[
                    "Distinctness Analysis architecture is designed. Verify, document, commit, and consider advancing to the bounded implementation milestone.",
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
                "Complete the missing Engineering Opportunity Distinctness Analysis design evidence.",
            ],
        )

    if OPPORTUNITY_SCOPE_CLASSIFICATION_MILESTONE_TEXT in milestone:
        requirements = {
            "tools/atlas/platform/reasoning/models.py": {
                "class OpportunityScopeEvidence":
                    "defines structured scope evidence",
                "class OpportunityScopeClassification":
                    "defines the structured classification result",
                "scope_classification: OpportunityScopeClassification | None":
                    "attaches classification to opportunity assessments",
            },
            "tools/atlas/platform/reasoning/opportunity_scope_classification.py": {
                "class ScopeDefinition":
                    "defines stable scope identity",
                "def build_scope_catalog":
                    "builds the six-scope taxonomy catalog",
                "def classify_opportunity_scope":
                    "implements bounded scope reasoning",
                "SCOPE_SIGNAL_PHRASES":
                    "defines transparent heuristic signals",
                'classification_state="candidate"':
                    "produces bounded candidates",
                'classification_state="ambiguous"':
                    "reports competing candidates",
                'classification_state="mixed"':
                    "reports bundled central outcomes",
                'classification_state="insufficient-evidence"':
                    "reports sparse evidence",
                'classification_state="conflicting"':
                    "reports conflicting explicit evidence",
                'classification_state="resolved"':
                    "supports human-reviewed resolution",
            },
            "tools/atlas/platform/reasoning/opportunity_assessment.py": {
                "scope_classification = classify_opportunity_scope(":
                    "consumes reusable Scope Classification",
                '"scope-classification-state"':
                    "exposes classification state as an assessment fact",
                "scope_classification=scope_classification":
                    "attaches the structured result to the assessment",
            },
            "tests/test_opportunity_scope_classification.py": {
                "test_catalog_contains_six_architecture_owned_scopes":
                    "tests the canonical taxonomy",
                "test_several_transparent_signals_produce_candidate":
                    "tests bounded heuristic candidates",
                "test_one_keyword_cannot_resolve_scope":
                    "tests the single-keyword boundary",
                "test_competing_signals_produce_ambiguous_result":
                    "tests ambiguity",
                "test_bundled_outcomes_produce_mixed_result":
                    "tests mixed scope",
                "test_sparse_evidence_produces_insufficient_result":
                    "tests insufficient evidence",
                "test_conflicting_human_reviewed_scopes_are_exposed":
                    "tests explicit conflict handling",
                "test_human_reviewed_scope_resolves_with_high_confidence":
                    "tests high-confidence human resolution",
                "test_capability_identity_alone_does_not_resolve_scope":
                    "tests capability and scope separation",
                "test_related_architecture_is_structural_not_resolution":
                    "tests architecture-reference boundaries",
                "test_raw_opportunity_object_is_not_mutated":
                    "tests object non-mutation",
                "test_assessment_consumes_scope_classification":
                    "tests assessment integration",
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
                    "A reusable six-scope taxonomy catalog exists.",
                    "The catalog contains all architecture-owned identifiers and labels.",
                    "Structured OpportunityScopeEvidence and OpportunityScopeClassification models exist.",
                    "At most one resolved primary scope is represented.",
                    "Secondary implications remain separate from primary scope.",
                    "Deterministic repository facts, structural evidence, and provenance are collected.",
                    "Transparent bounded heuristic rules produce candidates without claiming resolution.",
                    "One keyword cannot produce a resolved classification.",
                    "Competing candidates produce an ambiguous result.",
                    "Bundled central outcomes can produce a mixed result.",
                    "Sparse evidence produces an insufficient-evidence result.",
                    "Conflicting explicit evidence produces a conflicting result.",
                    "Human-reviewed evidence can resolve a high-confidence primary scope.",
                    "Capability identity alone does not determine scope.",
                    "Architecture references support evidence without automatically resolving scope.",
                    "Classification results expose evidence, counterevidence, confidence, blockers, unresolved questions, and recommendations.",
                    "Engineering Opportunity Assessments consume reusable Scope Classification.",
                    "Canonical objects and lifecycle state are not mutated.",
                    "Focused tests verify taxonomy, uncertainty states, integration, and non-mutation.",
                    "Reasoning remains independent of Atlas command rendering and language models.",
                ],
                unsatisfied_criteria=[],
                next_actions=[
                    "The Engineering Opportunity Scope Classification foundation is implemented. Verify, document, commit, and consider advancing the mission.",
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
                "Complete the missing Engineering Opportunity Scope Classification foundation evidence.",
            ],
        )

    if OPPORTUNITY_SCOPE_CLASSIFICATION_DESIGN_MILESTONE_TEXT in milestone:
        design_requirements = {
            "docs/architecture/engineering-opportunity-scope-classification.md": {
                "## Canonical Scope Taxonomy":
                    "defines the six-class scope taxonomy",
                "| `strategic-direction` | Strategic Direction |":
                    "defines stable scope identifiers and labels",
                "## Primary Scope":
                    "defines exactly-one-primary-scope semantics",
                "## Secondary Implications":
                    "defines secondary scope implications",
                "## Classification States":
                    "defines resolved, candidate, ambiguous, mixed, insufficient, and conflicting states",
                "## Evidence Model":
                    "defines repository, structural, heuristic, and human-reviewed evidence",
                "## Provenance":
                    "defines source attribution requirements",
                "## Deterministic, Heuristic, and Judgment Boundaries":
                    "separates deterministic evidence from semantic judgment",
                "## Confidence Model":
                    "defines explainable classification confidence",
                "## Structured Assessment Contract":
                    "defines reusable scope-classification output",
                "## Recommendation Effects":
                    "keeps recommendations separate from mutation",
                "## Human Authority and Canonical Mutation":
                    "preserves human repository authority",
                "## Initial Implementation Boundary":
                    "defines a bounded safe implementation",
                "## Verification Cases":
                    "defines focused implementation tests",
            },
            "docs/architecture/engineering-opportunity-assessment.md": {
                "docs/architecture/engineering-opportunity-scope-classification.md":
                    "references the canonical Scope Classification contract",
            },
        }
        registration_requirements = {
            "docs/architecture/repository.md": {
                "docs/architecture/engineering-opportunity-scope-classification.md":
                    "lists the architecture in repository ownership",
            },
            "docs/docs-map.md": {
                "docs/architecture/engineering-opportunity-scope-classification.md":
                    "lists the architecture in the documentation map",
            },
            "tools/atlas/platform/document_definitions.py": {
                '"docs/architecture/engineering-opportunity-scope-classification.md"':
                    "registers architecture metadata",
            },
        }

        design_evidence, design_missing = _document_design_evidence(
            catalog,
            design_requirements,
        )
        registration_evidence, registration_missing = _implementation_evidence(
            registration_requirements,
        )
        evidence = design_evidence + registration_evidence
        missing = design_missing + registration_missing

        if not missing:
            return MilestoneCompletionReport(
                status="Complete",
                confidence="High",
                evidence=evidence,
                missing_evidence=[],
                satisfied_criteria=[
                    "The six-class scope taxonomy is canonical and explicit.",
                    "Stable scope identifiers are separated from display labels.",
                    "Exactly-one-primary-scope semantics are defined.",
                    "Secondary scope implications are defined separately.",
                    "Resolved, candidate, ambiguous, mixed, insufficient-evidence, and conflicting states are defined.",
                    "Repository facts, structural evidence, heuristics, and human-reviewed evidence are distinguished.",
                    "Classification provenance and counterevidence are required.",
                    "Deterministic reasoning is separated from heuristic and semantic judgment.",
                    "Explainable confidence behavior is defined.",
                    "A reusable structured Scope Classification result is defined.",
                    "Recommendations remain separate from lifecycle and repository mutation.",
                    "Human authority over canonical objects and taxonomy changes is preserved.",
                    "The initial implementation boundary avoids false semantic precision.",
                    "Focused verification cases are explicit.",
                    "The architecture is integrated with Engineering Opportunity Assessment.",
                    "The architecture is registered in Repository Knowledge.",
                ],
                unsatisfied_criteria=[],
                next_actions=[
                    "Scope Classification architecture is designed. Verify, document, commit, and consider advancing to the bounded implementation milestone.",
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
                "Complete the missing Engineering Opportunity Scope Classification design evidence.",
            ],
        )

    if OPPORTUNITY_CAPABILITY_ALIGNMENT_MILESTONE_TEXT in milestone:
        requirements = {
            "tools/atlas/platform/reasoning/models.py": {
                "class OpportunityCapabilityAlignment":
                    "defines the structured capability-alignment result",
                "capability_alignment: OpportunityCapabilityAlignment | None":
                    "attaches capability alignment to opportunity assessments",
            },
            "tools/atlas/platform/reasoning/opportunity_capability_alignment.py": {
                "class CapabilityDefinition":
                    "defines canonical capability identity",
                "def build_capability_catalog":
                    "builds the bounded repository-owned capability catalog",
                "def align_opportunity_capability":
                    "implements deterministic capability alignment",
                '"AI": "ai-aiden-os"':
                    "defines the curated AI alias",
                '"Documentation": "knowledge-documentation"':
                    "defines the curated Documentation alias",
                '"Infrastructure": (':
                    "defines ambiguous Infrastructure candidates",
                'alignment_state="unknown"':
                    "reports unsupported capability values",
            },
            "tools/atlas/platform/reasoning/opportunity_assessment.py": {
                "capability_alignment = align_opportunity_capability(entity)":
                    "consumes reusable capability alignment",
                '"capability-alignment-state"':
                    "exposes alignment state as an assessment fact",
                "capability_alignment=capability_alignment":
                    "attaches the structured result to the assessment",
            },
            "tests/test_opportunity_capability_alignment.py": {
                "test_catalog_contains_architecture_owned_capabilities":
                    "tests the nine canonical capabilities",
                "test_exact_canonical_identifier_resolves":
                    "tests canonical identifier resolution",
                "test_exact_canonical_label_resolves":
                    "tests canonical label resolution",
                "test_ai_alias_resolves":
                    "tests the AI alias",
                "test_documentation_alias_resolves":
                    "tests the Documentation alias",
                "test_infrastructure_is_ambiguous":
                    "tests ambiguous Infrastructure handling",
                "test_learning_is_unknown":
                    "tests unknown Learning handling",
                "test_raw_declared_value_is_preserved_without_mutation":
                    "tests raw-value preservation and non-mutation",
                "test_assessment_consumes_resolved_alignment":
                    "tests reusable assessment integration",
                "test_alignment_does_not_infer_from_prose":
                    "tests the semantic-inference boundary",
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
                    "A reusable canonical capability catalog exists.",
                    "The catalog contains the nine architecture-owned identifiers and labels.",
                    "A reusable structured OpportunityCapabilityAlignment result exists.",
                    "Raw declared capability values are preserved.",
                    "Canonical identifiers and labels resolve deterministically.",
                    "AI and Documentation aliases resolve deterministically.",
                    "Infrastructure produces an ambiguous result with explicit candidates.",
                    "Learning and unsupported values produce unknown results.",
                    "Alignment results expose evidence, provenance, explanation, confidence, blockers, unresolved questions, and recommendations.",
                    "Engineering Opportunity Assessments consume reusable alignment results.",
                    "Unresolved alignment recommends enrichment without object mutation.",
                    "Capability is not inferred from opportunity prose.",
                    "Focused tests cover deterministic resolution and non-mutation.",
                    "Reasoning remains independent of Atlas command rendering and language models.",
                ],
                unsatisfied_criteria=[],
                next_actions=[
                    "The Engineering Opportunity Capability Alignment foundation is implemented. Verify, document, commit, and consider advancing the mission.",
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
                "Complete the missing Engineering Opportunity Capability Alignment foundation evidence.",
            ],
        )

    if OPPORTUNITY_CAPABILITY_ALIGNMENT_DESIGN_MILESTONE_TEXT in milestone:
        design_requirements = {
            "docs/architecture/engineering-opportunity-capability-alignment.md": {
                "## Canonical Capability Source":
                    "defines canonical capability ownership",
                "## Capability Identity Model":
                    "defines stable identifiers and display labels",
                "## Opportunity Capability Semantics":
                    "defines declared, primary, and secondary capability meaning",
                "## Compatibility and Migration":
                    "defines existing-value compatibility and migration",
                "## Alignment States":
                    "defines canonical, alias, ambiguous, unknown, deprecated, and conflicting states",
                "## Evidence and Provenance":
                    "defines source-backed alignment evidence",
                "## Structured Assessment Contract":
                    "defines reusable capability-alignment output",
                "## Deterministic and Judgment Boundaries":
                    "separates deterministic validation from semantic judgment",
                "## Human Authority and Lifecycle Mutation":
                    "preserves human mutation authority",
                "## Initial Implementation Boundary":
                    "defines bounded implementation scope",
                "## Verification Cases":
                    "defines focused implementation verification",
                "| `Infrastructure` |":
                    "addresses the ambiguous legacy infrastructure value",
                "| `Learning` |":
                    "addresses the unknown legacy learning value",
            },
            "docs/architecture/capabilities.md": {
                "## Capability Identity":
                    "defines stable capability identity",
                "| `engineering` | Engineering |":
                    "defines the Engineering capability identifier",
                "| `ai-aiden-os` | AI and Aiden OS |":
                    "defines the AI and Aiden OS capability identifier",
            },
        }
        registration_requirements = {
            "docs/architecture/repository.md": {
                "docs/architecture/engineering-opportunity-capability-alignment.md":
                    "lists the architecture in repository ownership",
            },
            "docs/docs-map.md": {
                "docs/architecture/engineering-opportunity-capability-alignment.md":
                    "lists the architecture in the documentation map",
            },
            "tools/atlas/platform/document_definitions.py": {
                '"docs/architecture/engineering-opportunity-capability-alignment.md"':
                    "registers architecture metadata",
            },
        }

        design_evidence, design_missing = _document_design_evidence(
            catalog,
            design_requirements,
        )
        registration_evidence, registration_missing = _implementation_evidence(
            registration_requirements,
        )
        evidence = design_evidence + registration_evidence
        missing = design_missing + registration_missing

        if not missing:
            return MilestoneCompletionReport(
                status="Complete",
                confidence="High",
                evidence=evidence,
                missing_evidence=[],
                satisfied_criteria=[
                    "The Platform Capability Map owns canonical capability identity.",
                    "Stable capability identifiers are separated from display labels.",
                    "Primary capability semantics are defined.",
                    "Secondary and cross-capability alignment boundaries are defined.",
                    "Existing opportunity capability values have explicit compatibility handling.",
                    "Unknown, ambiguous, deprecated, and conflicting states are defined.",
                    "Capability-alignment evidence, provenance, confidence, blockers, and unresolved questions are defined.",
                    "Deterministic validation is separated from semantic engineering judgment.",
                    "Canonical object mutation and lifecycle progression remain human-authorized.",
                    "A reusable structured assessment contract is defined.",
                    "The initial implementation boundary and verification cases are explicit.",
                    "The architecture is registered in Repository Knowledge.",
                ],
                unsatisfied_criteria=[],
                next_actions=[
                    "Capability Alignment architecture is designed. Verify, document, commit, and consider advancing to the bounded implementation milestone.",
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
                "Complete the missing Engineering Opportunity Capability Alignment design evidence.",
            ],
        )

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
