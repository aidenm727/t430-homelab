from pathlib import Path
from datetime import datetime
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SESSION = DOCS / "change-session.md"


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def require_text(args, usage):
    if not args:
        print(usage)
        sys.exit(1)
    return " ".join(args)


def start(title):
    DOCS.mkdir(exist_ok=True)
    SESSION.write_text(
        f"""# Homelab Change Session

Started: {timestamp()}

## Change Title

{title}

## Intent

## Notes

## Verification

## Documentation Outputs

""",
        encoding="utf-8",
    )
    print(f"Started change session: {title}")


def append(section, text):
    if not SESSION.exists():
        print("No active change session. Run start first.")
        sys.exit(1)

    content = SESSION.read_text(encoding="utf-8")
    marker = f"## {section}\n"
    entry = f"- [{timestamp()}] {text}\n"

    if marker not in content:
        content += f"\n{marker}{entry}"
    else:
        content = content.replace(marker, marker + entry)

    SESSION.write_text(content, encoding="utf-8")
    print(f"Added {section.lower()}: {text}")


def finish():
    if not SESSION.exists():
        print("No active change session.")
        sys.exit(1)

    print("Change session ready for documentation review:")
    print(SESSION)

    generator = ROOT / "tools" / "generate-context.py"

    if generator.exists():
        subprocess.run([sys.executable, str(generator)], check=True)
        print("Regenerated docs/aiden-context.md")
    else:
        print("Context generator not found; skipped context regeneration.")


def main():
    if len(sys.argv) < 2:
        print("Usage: homelab-change.py start|note|verify|finish ...")
        sys.exit(1)

    command = sys.argv[1]

    if command == "start":
        start(require_text(sys.argv[2:], 'Usage: homelab-change.py start "Change title"'))
    elif command == "note":
        append("Notes", require_text(sys.argv[2:], 'Usage: homelab-change.py note "What changed"'))
    elif command == "verify":
        append("Verification", require_text(sys.argv[2:], 'Usage: homelab-change.py verify "How it was verified"'))
    elif command == "finish":
        finish()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()