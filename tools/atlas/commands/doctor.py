import shutil
import subprocess


NAME = "doctor"
HELP = "Check local engineering environment readiness."


def register(subparsers):
    parser = subparsers.add_parser(NAME, help=HELP)
    parser.set_defaults(func=run)


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def git_available() -> bool:
    return command_exists("git")


def python3_available() -> bool:
    return command_exists("python3")


def python_available() -> bool:
    return command_exists("python")


def vscode_available() -> bool:
    return command_exists("code")


def in_git_repository() -> bool:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return False

    return result.stdout.strip() == "true"


def check(label: str, passed: bool, detail: str) -> None:
    marker = "✓" if passed else "✗"
    print(f"{marker} {label}: {detail}")


def run(args):
    print("Atlas Doctor")
    print("============")
    print()

    check("Git", git_available(), "available" if git_available() else "missing")
    check("Git Repository", in_git_repository(), "inside repository" if in_git_repository() else "not inside repository")
    check("Python 3", python3_available(), "available as python3" if python3_available() else "missing")
    check("Python", python_available(), "available as python" if python_available() else "not available; use python3")
    check("VS Code", vscode_available(), "available as code" if vscode_available() else "code command not found")

    print()
    print("Suggested Actions")
    print("-----------------")

    if not python_available() and python3_available():
        print("- Use python3 for Atlas commands, or install python-is-python3 if you want python to work.")

    if not vscode_available():
        print("- Install or enable the VS Code command-line launcher if you want to open files with code.")

    if git_available() and python3_available() and in_git_repository():
        print("- Engineering environment is ready for local Atlas work.")