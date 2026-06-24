from pathlib import Path
from datetime import datetime
import re
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SESSION = DOCS / "change-session.md"
CHANGES_DIR = DOCS / "changes"
CHANGES_LOG = DOCS / "changes.log"


def now():
    return datetime.now()


def timestamp():
    return now().strftime("%Y-%m-%d %H:%M:%S")


def today():
    return now().strftime("%Y-%m-%d")


def require_text(args, usage):
    if not args:
        print(usage)
        sys.exit(1)
    return " ".join(args)


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "homelab-change"


def extract_section(content, section):
    marker = f"## {section}"
    lines = content.splitlines()

    in_section = False
    collected = []

    for line in lines:
        if line.startswith("## "):
            if in_section:
                break
            if line.strip() == marker:
                in_section = True
                continue

        if in_section:
            collected.append(line)

    return [line.strip() for line in collected if line.strip()]


def clean_bullet(line):
    line = re.sub(r"^- \[[^\]]+\]\s*", "", line)
    line = re.sub(r"^-+\s*", "", line)
    return line.strip()


def yaml_list(items):
    cleaned = [clean_bullet(item) for item in items if clean_bullet(item)]

    if not cleaned:
        return "  - Not recorded\n"

    return "".join(f"  - {item}\n" for item in cleaned)


def start(title, change_type="documentation"):
    DOCS.mkdir(exist_ok=True)
    SESSION.write_text(
        f"""# Homelab Change Session

Started: {timestamp()}

## Change Title

{title}

## Change Type

{change_type}

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


def write_change_record(content):
    CHANGES_DIR.mkdir(exist_ok=True)

    title_lines = extract_section(content, "Change Title")
    title = title_lines[0] if title_lines else "Homelab Change"

    notes = extract_section(content, "Notes")
    change_type_lines = extract_section(content, "Change Type")
    change_type = change_type_lines[0] if change_type_lines else "documentation"
    verification = extract_section(content, "Verification")
    documentation = extract_section(content, "Documentation Outputs")
    intent = extract_section(content, "Intent")

    filename = f"{today()}-{slugify(title)}.yml"
    path = CHANGES_DIR / filename

    yaml = f"""date: {today()}
title: {title}
change_type: {change_type}
status: verified

intent:
{yaml_list(intent)}

summary:
{yaml_list(notes)}

verification:
{yaml_list(verification)}

documentation_outputs:
{yaml_list(documentation)}

source_session: docs/change-session.md
"""
    path.write_text(yaml, encoding="utf-8")
    return path, title


def append_changes_log(title):
    DOCS.mkdir(exist_ok=True)
    entry = f"{timestamp()} - {title}\n"
    with CHANGES_LOG.open("a", encoding="utf-8") as f:
        f.write(entry)


def finish():
    if not SESSION.exists():
        print("No active change session.")
        sys.exit(1)

    content = SESSION.read_text(encoding="utf-8")

    record_path, title = write_change_record(content)
    append_changes_log(title)

    print(f"Created structured change record: {record_path}")
    print(f"Appended summary to: {CHANGES_LOG}")

    generator = ROOT / "tools" / "generate-context.py"

    if generator.exists():
        subprocess.run([sys.executable, str(generator)], check=True)
        print("Regenerated docs/aiden-context.md")
    else:
        print("Context generator not found; skipped context regeneration.")


def main():
    if len(sys.argv) < 2:
        print("Usage: homelab-change.py start|intent|note|verify|doc|finish ...")
        sys.exit(1)

    command = sys.argv[1]

    if command == "start":
        args = sys.argv[2:]
        usage = 'Usage: homelab-change.py start [change_type] "Change title"'

        if not args:
            print(usage)
            sys.exit(1)

        allowed_types = {"documentation", "infrastructure", "service", "automation", "network", "storage"}

        if len(args) >= 2 and args[0] in allowed_types:
            start(" ".join(args[1:]), args[0])
        else:
            start(" ".join(args))
    elif command == "intent":
        append("Intent", require_text(sys.argv[2:], 'Usage: homelab-change.py intent "Why this change is being made"'))
    elif command == "note":
        append("Notes", require_text(sys.argv[2:], 'Usage: homelab-change.py note "What changed"'))
    elif command == "verify":
        append("Verification", require_text(sys.argv[2:], 'Usage: homelab-change.py verify "How it was verified"'))
    elif command == "doc":
        append("Documentation Outputs", require_text(sys.argv[2:], 'Usage: homelab-change.py doc "What documentation was updated"'))
    elif command == "finish":
        finish()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()