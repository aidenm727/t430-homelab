from atlas.platform.discovery import document_catalog


NAME = "explain"
HELP = "Explain what Atlas knows about a repository document."


def register(subparsers):
    parser = subparsers.add_parser(NAME, help=HELP)
    parser.add_argument("document", help="Document path, filename, or name without .md")
    parser.set_defaults(func=run)


def print_list(title: str, values: list[str]) -> None:
    print(title)
    print("-" * len(title))

    if not values:
        print("- None")
        return

    for value in values:
        print(f"- {value}")


def run(args):
    catalog = document_catalog()
    document = catalog.find(args.document)

    if document is None:
        print("Atlas Explain")
        print("=============")
        print()
        print(f"No document found for: {args.document}")
        return

    print("Atlas Explain")
    print("=============")
    print()
    print(f"Name: {document.name}")
    print(f"Path: {document.path}")
    print(f"Layer: {document.layer}")

    if document.definition is None:
        print()
        print("Definition")
        print("----------")
        print("No document definition available yet.")
        return

    definition = document.definition

    print()
    print("Definition")
    print("----------")
    print(f"Purpose: {definition.purpose}")
    print(f"Canonical: {'Yes' if definition.canonical else 'No'}")
    print(f"Generated: {'Yes' if definition.generated else 'No'}")
    print(f"Capability: {definition.capability or 'Unknown'}")
    print()

    print_list("Related Documents", definition.related)
    