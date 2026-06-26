from pathlib import Path


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