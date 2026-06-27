from atlas.platform.discovery import document_layers


NAME = "docs"
HELP = "Show canonical documentation by repository layer."


def register(subparsers):
    parser = subparsers.add_parser(NAME, help=HELP)
    parser.set_defaults(func=run)


def print_paths(paths: list[str]) -> None:
    if not paths:
        print("- None found")
        return

    for path in paths:
        print(f"- {path}")


def run(args):
    print("Atlas Docs")
    print("==========")
    print()

    for layer in document_layers():
        print(layer.name)
        print("-" * len(layer.name))
        print_paths(layer.paths)
        print()