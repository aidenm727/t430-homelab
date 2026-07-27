"""Command-line interface for the bounded School Learning v0.1 workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import (
    SchoolLearningError,
    add_material,
    default_data_root,
    ensure_topic,
    initialize_course,
    prepare_study_handoff,
    record_session,
    workspace,
)
from .render import render_course


def _root(value: str | None) -> Path:
    return Path(value).expanduser().resolve() if value else default_data_root()


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        prog="school", description="School Learning v0.1.1 local course workspace"
    )
    result.add_argument("--data-root", help="owner-controlled course-data root")
    commands = result.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init")
    init.add_argument("term")
    init.add_argument("course_id")
    init.add_argument("title")

    add = commands.add_parser("add-material")
    add.add_argument("term")
    add.add_argument("course_id")
    add.add_argument("material_id")
    add.add_argument("title")
    add.add_argument("source")
    add.add_argument("--replace", action="store_true")

    study = commands.add_parser("study")
    study.add_argument("term")
    study.add_argument("course_id")
    study.add_argument("topic_id")
    study.add_argument("topic_title")
    study.add_argument("mode", choices=("explain", "practice", "review"))
    study.add_argument("objective")
    study.add_argument("--material", action="append", default=[])

    record = commands.add_parser("record")
    record.add_argument("term")
    record.add_argument("course_id")
    record.add_argument("topic_id")
    record.add_argument("outcome", choices=("correct", "partial", "incorrect"))
    record.add_argument("status", choices=("unseen", "learning", "review", "solid"))
    record.add_argument("note")
    record.add_argument("--mode", choices=("explain", "practice", "review"), default="review")
    record.add_argument("--priority", type=int, default=0)
    record.add_argument("--session-id")

    render = commands.add_parser("render")
    render.add_argument("term")
    render.add_argument("course_id")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        root = _root(args.data_root)
        if args.command == "init":
            ws = initialize_course(root, args.term, args.course_id, args.title)
            print(ws.course_dir)
        elif args.command == "add-material":
            ws = workspace(root, args.term, args.course_id)
            value = add_material(ws, args.source, args.material_id, args.title, replace=args.replace)
            print(json.dumps(value, sort_keys=True))
        elif args.command == "study":
            ws = workspace(root, args.term, args.course_id)
            ensure_topic(ws, args.topic_id, args.topic_title, args.material)
            handoff = prepare_study_handoff(ws, args.topic_id, args.mode, args.objective)
            print("Study handoff ready.")
            print(f"Handoff: {handoff['root']}")
            print(f"Attachments: {handoff['attachments']}")
            print(f"Prompt: {handoff['prompt']}")
            print(
                "Attach all files under "
                f"{handoff['attachments']} to the approved AI interface, then paste prompt.txt."
            )
        elif args.command == "record":
            ws = workspace(root, args.term, args.course_id)
            value = record_session(
                ws,
                args.topic_id,
                args.outcome,
                args.status,
                args.note,
                mode=args.mode,
                session_id=args.session_id,
                next_review_priority=args.priority,
            )
            print(json.dumps(value, sort_keys=True))
        elif args.command == "render":
            ws = workspace(root, args.term, args.course_id)
            print("\n".join(str(path) for path in render_course(ws)))
        else:  # pragma: no cover
            raise AssertionError(args.command)
    except SchoolLearningError as error:
        parser().error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
