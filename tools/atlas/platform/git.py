import subprocess

from atlas.platform.repository import repo_root


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