from pathlib import Path
import subprocess

def repo_root() -> Path:
    """
    Return the root of the Aiden Platform repository.
    """
    return Path(__file__).resolve().parents[2]


def docs_dir() -> Path:
    return repo_root() / "docs"


def architecture_dir() -> Path:
    return docs_dir() / "architecture"


def current_mission() -> Path:
    return docs_dir() / "current-mission.md"


def context_file() -> Path:
    return docs_dir() / "aiden-context.md"

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def mission_text() -> str:
    return read_text(current_mission())

def mission_lines() -> list[str]:
    return mission_text().splitlines()


def mission_phase() -> str:
    for line in mission_lines():
        if line.startswith("Phase:"):
            return line.replace("Phase:", "", 1).strip()

    return "Unknown"


def next_milestone() -> str:
    lines = mission_lines()

    for index, line in enumerate(lines):
        if line.strip() == "Next Milestone:":
            for next_line in lines[index + 1:]:
                if next_line.strip():
                    return next_line.strip()

    return "Unknown"

def run_git_command(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root(),
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def git_branch() -> str:
    return run_git_command(["branch", "--show-current"])


def latest_commit() -> str:
    return run_git_command(["log", "-1", "--oneline"])


def repository_clean() -> bool:
    return run_git_command(["status", "--porcelain"]) == ""