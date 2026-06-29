import subprocess

from pathlib import Path

from atlas.platform.discovery import document_catalog
from atlas.platform.repository import repo_root


NAME = "open"
HELP = "Open a repository document in VS Code."


def register(subparsers):
    parser = subparsers.add_parser(NAME, help=HELP)
    parser.add_argument("document", help="Document path, filename, or name without .md")
    parser.set_defaults(func=run)


def vscode_path(path: Path) -> str:
    result = subprocess.run(
        ["wslpath", "-w", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return result.stdout.strip()

    return str(path)


def run(args):
    catalog = document_catalog()
    document = catalog.find(args.document)

    print("Atlas Open")
    print("==========")
    print()

    if document is None:
        print(f"No document found for: {args.document}")
        return

    path = repo_root() / document.path
    display_path = document.path
    open_path = vscode_path(path)

    print(f"Opening: {display_path}")
    subprocess.run(["code", open_path], check=False)
    