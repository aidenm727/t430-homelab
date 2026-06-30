from atlas.platform.discovery import document_catalog
from atlas.platform.reasoning import analyze_impact


NAME = "impact"
HELP = "Analyze likely repository impact for a document."


def register(subparsers):
    parser = subparsers.add_parser(NAME, help=HELP)
    parser.add_argument("document", help="Document path, filename, or name without .md")
    parser.set_defaults(func=run)


def print_documents(title: str, documents):
    print(title)
    print("-" * len(title))

    if not documents:
        print("- None")
        return

    for document in documents:
        print(f"- {document.path}")


def run(args):
    catalog = document_catalog()
    document = catalog.find(args.document)

    print("Atlas Impact")
    print("============")
    print()

    if document is None:
        print(f"No document found for: {args.document}")
        return

    report = analyze_impact(catalog, document)

    print("Target")
    print("------")
    print(report.target.path)
    print()

    if report.target.definition is not None:
        definition = report.target.definition
        print("Repository Knowledge")
        print("--------------------")
        print(f"Capability: {definition.capability or 'Unknown'}")
        print(f"Canonical: {'Yes' if definition.canonical else 'No'}")
        print(f"Generated: {'Yes' if definition.generated else 'No'}")
        print(f"Status: {definition.status}")
        print()

    print_documents("Related Documents", report.related_documents)
    print()
    print_documents("Generated Outputs", report.generated_outputs)
    print()

    print("Suggested Actions")
    print("-----------------")
    for action in report.suggested_actions:
        print(f"- {action}")
