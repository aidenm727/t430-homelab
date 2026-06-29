from atlas.platform.discovery import document_catalog


NAME = "missing"
HELP = "Show discovered documents without Atlas metadata definitions."


def register(subparsers):
    parser = subparsers.add_parser(NAME, help=HELP)
    parser.set_defaults(func=run)


def run(args):
    catalog = document_catalog()
    documents = catalog.without_definitions()

    print("Atlas Missing")
    print("=============")
    print()

    if not documents:
        print("All discovered documents have metadata definitions.")
        return

    print("Documents Without Definitions")
    print("-----------------------------")

    for document in documents:
        print(f"- [{document.layer}] {document.path}")
        