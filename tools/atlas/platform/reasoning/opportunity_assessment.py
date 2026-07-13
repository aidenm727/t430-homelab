import re
from pathlib import Path

from atlas.platform.repository_objects.models import RepositoryEntity
from atlas.platform.reasoning.models import (
    EngineeringOpportunityAssessment,
    OpportunityAssessmentFact,
    OpportunityAssessmentFinding,
    OpportunityAssessmentRecommendation,
)


ENGINEERING_OPPORTUNITY_TYPE = "engineering-opportunity"

LIFECYCLE_STATES = (
    "captured",
    "reviewed",
    "accepted",
    "architected",
    "scheduled",
    "implemented",
    "closed",
)

IDENTIFIER_PATTERN = re.compile(r"^EO-\d{4}-\d{3}$")


def assess_engineering_opportunity(
    entity: RepositoryEntity,
) -> EngineeringOpportunityAssessment:
    facts: list[OpportunityAssessmentFact] = []
    findings: list[OpportunityAssessmentFinding] = []
    blockers: list[str] = []
    unresolved_questions: list[str] = []

    facts.extend(
        [
            OpportunityAssessmentFact(
                name="object-type",
                value=entity.object_type,
                source=entity.path,
            ),
            OpportunityAssessmentFact(
                name="identifier",
                value=entity.id,
                source=entity.path,
            ),
            OpportunityAssessmentFact(
                name="lifecycle-state",
                value=entity.status,
                source=entity.path,
            ),
            OpportunityAssessmentFact(
                name="repository-path",
                value=entity.path,
                source=entity.path,
            ),
            OpportunityAssessmentFact(
                name="capability",
                value=entity.capability,
                source=entity.path,
            ),
            OpportunityAssessmentFact(
                name="summary-present",
                value="yes" if entity.summary.strip() else "no",
                source=entity.path,
            ),
            OpportunityAssessmentFact(
                name="rationale-present",
                value="yes" if entity.rationale.strip() else "no",
                source=entity.path,
            ),
        ]
    )

    supplemental_evidence_present = bool(
        entity.evidence.strip() or entity.notes.strip()
    )

    facts.append(
        OpportunityAssessmentFact(
            name="supplemental-evidence-present",
            value="yes" if supplemental_evidence_present else "no",
            source=entity.path,
        )
    )

    if entity.object_type != ENGINEERING_OPPORTUNITY_TYPE:
        statement = (
            f"Object type '{entity.object_type}' is not "
            f"'{ENGINEERING_OPPORTUNITY_TYPE}'."
        )
        findings.append(
            OpportunityAssessmentFinding(
                code="invalid-object-type",
                severity="Error",
                statement=statement,
                evidence=(f"Repository object path: {entity.path}",),
            )
        )
        blockers.append(statement)

    if entity.missing_fields:
        missing = ", ".join(entity.missing_fields)
        statement = f"Required fields are missing: {missing}."
        findings.append(
            OpportunityAssessmentFinding(
                code="missing-required-fields",
                severity="Error",
                statement=statement,
                evidence=tuple(
                    f"Required field '{field}' has no value."
                    for field in entity.missing_fields
                ),
            )
        )
        blockers.extend(
            f"Provide required field '{field}'."
            for field in entity.missing_fields
        )

    identifier_valid = bool(IDENTIFIER_PATTERN.fullmatch(entity.id))

    if not identifier_valid:
        statement = (
            f"Identifier '{entity.id}' does not match EO-YYYY-NNN."
        )
        findings.append(
            OpportunityAssessmentFinding(
                code="invalid-identifier",
                severity="Error",
                statement=statement,
                evidence=(f"Observed identifier: {entity.id}",),
            )
        )
        blockers.append(statement)

    object_path = Path(entity.path)

    if identifier_valid:
        expected_prefix = f"{entity.id}-"
        if not object_path.name.startswith(expected_prefix):
            statement = (
                f"Filename '{object_path.name}' does not begin with "
                f"the stable identifier '{entity.id}'."
            )
            findings.append(
                OpportunityAssessmentFinding(
                    code="identifier-path-mismatch",
                    severity="Error",
                    statement=statement,
                    evidence=(
                        f"Identifier: {entity.id}",
                        f"Repository path: {entity.path}",
                    ),
                )
            )
            blockers.append(statement)

    if entity.status not in LIFECYCLE_STATES:
        statement = (
            f"Lifecycle state '{entity.status}' is not recognized."
        )
        findings.append(
            OpportunityAssessmentFinding(
                code="invalid-lifecycle-state",
                severity="Error",
                statement=statement,
                evidence=(
                    "Recognized states: " + ", ".join(LIFECYCLE_STATES),
                ),
            )
        )
        blockers.append(statement)
    else:
        lifecycle_directory = object_path.parent.name

        if lifecycle_directory != entity.status:
            statement = (
                f"Lifecycle state '{entity.status}' does not match "
                f"repository directory '{lifecycle_directory}'."
            )
            findings.append(
                OpportunityAssessmentFinding(
                    code="lifecycle-path-mismatch",
                    severity="Error",
                    statement=statement,
                    evidence=(
                        f"Lifecycle state: {entity.status}",
                        f"Repository path: {entity.path}",
                    ),
                )
            )
            blockers.append(statement)

    if not supplemental_evidence_present:
        unresolved_questions.append(
            "Whether additional supporting evidence should be recorded "
            "before human review."
        )

    if blockers:
        recommendation = OpportunityAssessmentRecommendation(
            action="enrich",
            reason=(
                "Resolve deterministic object-quality findings before "
                "considering lifecycle progression."
            ),
            confidence="High",
        )
    else:
        findings.append(
            OpportunityAssessmentFinding(
                code="object-structure-valid",
                severity="Info",
                statement=(
                    "The opportunity object satisfies the current "
                    "deterministic structural checks."
                ),
                evidence=(
                    "Required fields are present.",
                    "The identifier format is valid.",
                    "Lifecycle state and repository placement agree.",
                ),
            )
        )

        if entity.status == "captured":
            recommendation = OpportunityAssessmentRecommendation(
                action="retain-captured",
                reason=(
                    "The object is structurally valid, but deterministic "
                    "object quality alone does not authorize lifecycle "
                    "progression."
                ),
                confidence="High",
            )
        else:
            recommendation = OpportunityAssessmentRecommendation(
                action="retain-current-state",
                reason=(
                    "The object is structurally consistent with its "
                    "current lifecycle state."
                ),
                confidence="High",
            )

    return EngineeringOpportunityAssessment(
        opportunity_id=entity.id,
        lifecycle_state=entity.status,
        repository_path=entity.path,
        facts=tuple(facts),
        findings=tuple(findings),
        recommendation=recommendation,
        blockers=tuple(blockers),
        unresolved_questions=tuple(unresolved_questions),
    )
