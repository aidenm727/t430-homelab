from atlas.platform.repository import current_mission, read_text


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