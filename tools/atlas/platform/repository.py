from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def docs_dir() -> Path:
    return repo_root() / "docs"


def architecture_dir() -> Path:
    return docs_dir() / "architecture"


def current_mission() -> Path:
    return docs_dir() / "current-mission.md"


def current_state() -> Path:
    return docs_dir() / "current-state.json"


def context_file() -> Path:
    return docs_dir() / "aiden-context.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")
