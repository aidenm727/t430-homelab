from atlas.platform.discovery import document_catalog
from atlas.platform.reasoning import ValidationFinding, ValidationReport, validate_repository


NAME = "validate"
HELP = "Validate repository knowledge and reasoning metadata."


def register(subparsers):
    parser = subparsers.add_parser(NAME, help=HELP)
    parser.set_defaults(func=run)


def print_findings(title: str, findings: list[ValidationFinding]) -> None:
    print(title)
    print("-" * len(title))

    if not findings:
        print("- None")
        return

    for finding in findings:
        print(f"- {finding.message}")


def print_recommendations(report: ValidationReport) -> None:
    print("Recommendations")
    print("---------------")

    if not report.recommendations:
        print("- None")
        return

    for recommendation in report.recommendations:
        print(f"- {recommendation}")


def run(args):
    catalog = document_catalog()
    report = validate_repository(catalog)

    print("Atlas Validate")
    print("==============")
    print()

    print("Status")
    print("------")
    print("Valid" if report.valid else "Invalid")
    print()

    print_findings("Errors", report.errors)
    print()
    print_findings("Warnings", report.warnings)
    print()
    print_recommendations(report)
