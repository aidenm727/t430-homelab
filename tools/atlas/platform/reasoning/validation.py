from pathlib import Path

from atlas.platform.document_catalog import DocumentCatalog
from atlas.platform.reasoning.models import ValidationFinding, ValidationReport


def repository_path_exists(path: str) -> bool:
    return Path(path).exists()


def validate_repository(catalog: DocumentCatalog) -> ValidationReport:
    errors: list[ValidationFinding] = []
    warnings: list[ValidationFinding] = []
    recommendations: list[str] = []

    for document in catalog.without_definitions():
        errors.append(
            ValidationFinding(
                severity="error",
                message=f"{document.path} is discovered but has no metadata definition.",
            )
        )

    for document in catalog.with_definitions():
        definition = document.definition
        if definition is None:
            continue

        if definition.generated and definition.canonical:
            errors.append(
                ValidationFinding(
                    severity="error",
                    message=f"{document.path} cannot be both generated and canonical.",
                )
            )

        if definition.generated and not definition.generated_from:
            warnings.append(
                ValidationFinding(
                    severity="warning",
                    message=f"{document.path} is generated but does not declare generated_from sources.",
                )
            )

        if definition.generated and definition.managed_by is None:
            warnings.append(
                ValidationFinding(
                    severity="warning",
                    message=f"{document.path} is generated but does not declare a managing tool.",
                )
            )

        for related_path in definition.related:
            if catalog.find(related_path) is None and not repository_path_exists(related_path):
                warnings.append(
                    ValidationFinding(
                        severity="warning",
                        message=f"{document.path} references missing related repository path {related_path}.",
                    )
                )

        for source_path in definition.generated_from:
            if catalog.find(source_path) is None and not repository_path_exists(source_path):
                warnings.append(
                    ValidationFinding(
                        severity="warning",
                        message=f"{document.path} is generated from missing source {source_path}.",
                    )
                )

        if definition.managed_by is not None and not repository_path_exists(definition.managed_by):
            warnings.append(
                ValidationFinding(
                    severity="warning",
                    message=f"{document.path} declares missing managing tool {definition.managed_by}.",
                )
            )

    if not errors and not warnings:
        recommendations.append("Repository metadata is internally consistent.")
    if errors:
        recommendations.append("Fix validation errors before adding new reasoning capabilities.")
    if warnings:
        recommendations.append("Review warnings before relying on validation for synchronization decisions.")

    return ValidationReport(errors=errors, warnings=warnings, recommendations=recommendations)
