from atlas.platform.repository import current_mission, read_text


def mission_text() -> str:
    return read_text(current_mission())


def mission_lines() -> list[str]:
    return mission_text().splitlines()


def value_after_heading(heading: str) -> str:
    lines = mission_lines()

    for index, line in enumerate(lines):
        stripped = line.strip()

        if stripped == f"{heading}:":
            return stripped.replace(f"{heading}:", "", 1).strip()

        if stripped == f"## {heading}":
            for next_line in lines[index + 1:]:
                next_stripped = next_line.strip()

                if not next_stripped or next_stripped == "---":
                    continue

                if next_stripped.startswith("#"):
                    break

                return next_stripped

    return "Unknown"


def mission_phase() -> str:
    return value_after_heading("Phase")


def next_milestone() -> str:
    return value_after_heading("Next Milestone")
