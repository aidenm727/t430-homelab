from atlas.platform.discovery import document_catalog
from atlas.platform.reasoning.synchronization import analyze_synchronization


NAME = "sync"
HELP = "Analyze repository synchronization state."


def register(subparsers):
    parser = subparsers.add_parser(NAME, help=HELP)
    parser.set_defaults(func=run)


def run(args):
    catalog = document_catalog()
    report = analyze_synchronization(catalog)

    print("Atlas Sync")
    print("==========")
    print()

    print("Status")
    print("------")
    print(report.status)
    print()

    print("Findings")
    print("--------")

    for finding in report.findings:
        print(f"- [{finding.severity}] {finding.domain}: {finding.summary}")
        print(f"  Evidence: {finding.evidence}")
        print(f"  Action: {finding.recommended_action}")

    print()

    print("Summary")
    print("-------")
    print(f"Errors: {len(report.errors)}")
    print(f"Warnings: {len(report.warnings)}")
