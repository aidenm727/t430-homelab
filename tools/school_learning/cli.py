"""Command-line interface for the bounded School Learning workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import (
    ASSESSMENT_STATUSES,
    ASSESSMENT_TYPES,
    CAPABILITY_TAGS,
    CLAIM_STATUSES,
    MATERIAL_KINDS,
    MATERIAL_LIFECYCLES,
    SchoolLearningError,
    add_material,
    default_data_root,
    ensure_topic,
    initialize_course,
    initialize_semester,
    intake_material,
    prepare_course_handoff,
    prepare_study_handoff,
    record_session,
    register_course,
    semester_workspace,
    upsert_assessment,
    upsert_policy,
    workspace,
)
from .render import render_course, render_semester


def _root(value: str | None) -> Path:
    return Path(value).expanduser().resolve() if value else default_data_root()


def _metadata(values: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        key, separator, item = value.partition("=")
        if not separator or not key or not item:
            raise SchoolLearningError("course metadata must use KEY=VALUE")
        if key in result:
            raise SchoolLearningError(f"duplicate course metadata key: {key}")
        result[key] = item
    return result


def _sources(values: list[str]) -> list[dict[str, str]]:
    result = []
    for value in values:
        parts = value.split("|", 3)
        if len(parts) != 4 or any(not part for part in parts):
            raise SchoolLearningError("course source must use ID|TITLE|REFERENCE|STATUS")
        result.append(dict(zip(("id", "title", "reference", "status"), parts, strict=True)))
    return result


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        prog="school", description="School Learning v0.2 local semester/course workspace"
    )
    result.add_argument("--data-root", help="owner-controlled course-data root")
    commands = result.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="initialize a legacy-compatible course workspace")
    init.add_argument("term")
    init.add_argument("course_id")
    init.add_argument("title")

    semester = commands.add_parser("semester", help="initialize a semester")
    semester.add_argument("term")
    semester.add_argument("title")

    course = commands.add_parser("course", help="register or configure a v0.2 course")
    course.add_argument("term")
    course.add_argument("course_id")
    course.add_argument("title")
    course.add_argument("--capability", action="append", choices=CAPABILITY_TAGS, default=[])
    course.add_argument("--source", action="append", default=[], metavar="ID|TITLE|REF|STATUS")
    course.add_argument("--metadata", action="append", default=[], metavar="KEY=VALUE")

    add = commands.add_parser("add-material")
    add.add_argument("term")
    add.add_argument("course_id")
    add.add_argument("material_id")
    add.add_argument("title")
    add.add_argument("source")
    add.add_argument("--replace", action="store_true")

    intake = commands.add_parser("intake", help="intake opaque material with explicit metadata")
    intake.add_argument("term")
    intake.add_argument("course_id")
    intake.add_argument("material_id")
    intake.add_argument("title")
    intake.add_argument("source")
    intake.add_argument("--kind", choices=MATERIAL_KINDS)
    intake.add_argument("--status", choices=MATERIAL_LIFECYCLES)
    intake_date = intake.add_mutually_exclusive_group()
    intake_date.add_argument("--date")
    intake_date.add_argument("--clear-date", action="store_true")
    intake_topics = intake.add_mutually_exclusive_group()
    intake_topics.add_argument("--topic", action="append")
    intake_topics.add_argument("--clear-topics", action="store_true")
    intake_assessments = intake.add_mutually_exclusive_group()
    intake_assessments.add_argument("--assessment", action="append")
    intake_assessments.add_argument("--clear-assessments", action="store_true")
    intake_provenance = intake.add_mutually_exclusive_group()
    intake_provenance.add_argument("--provenance")
    intake_provenance.add_argument("--clear-provenance", action="store_true")
    intake.add_argument("--observed-at")
    intake.add_argument("--provenance-status", choices=CLAIM_STATUSES, default="provisional")
    intake.add_argument("--replace", action="store_true")

    assessment = commands.add_parser("assessment", help="register or update an assessment")
    assessment.add_argument("term")
    assessment.add_argument("course_id")
    assessment.add_argument("assessment_id")
    assessment.add_argument("title")
    assessment.add_argument(
        "--type",
        help="normalized custom type; common values include " + ", ".join(ASSESSMENT_TYPES),
    )
    assessment.add_argument("--status", choices=ASSESSMENT_STATUSES)
    assessment_weight = assessment.add_mutually_exclusive_group()
    assessment_weight.add_argument("--weight")
    assessment_weight.add_argument("--clear-weight", action="store_true")
    assessment_points = assessment.add_mutually_exclusive_group()
    assessment_points.add_argument("--points")
    assessment_points.add_argument("--clear-points", action="store_true")
    assessment_xp = assessment.add_mutually_exclusive_group()
    assessment_xp.add_argument("--xp")
    assessment_xp.add_argument("--clear-xp", action="store_true")
    assessment_materials = assessment.add_mutually_exclusive_group()
    assessment_materials.add_argument("--material", action="append")
    assessment_materials.add_argument("--clear-materials", action="store_true")
    assessment_topics = assessment.add_mutually_exclusive_group()
    assessment_topics.add_argument("--topic", action="append")
    assessment_topics.add_argument("--clear-topics", action="store_true")
    assessment.add_argument("--claim-field")
    assessment.add_argument("--claim-value")
    assessment.add_argument("--claim-source")
    assessment.add_argument("--claim-observed-at")
    assessment.add_argument("--claim-status", choices=CLAIM_STATUSES, default="provisional")

    policy = commands.add_parser("policy", help="register or update a sourced policy")
    policy.add_argument("term")
    policy.add_argument("course_id")
    policy.add_argument("policy_id")
    policy.add_argument("title")
    policy.add_argument("category")
    policy.add_argument("rule")
    policy.add_argument("source")
    policy.add_argument("--status", choices=CLAIM_STATUSES, default="provisional")
    policy.add_argument("--observed-at")

    study = commands.add_parser("study")
    study.add_argument("term")
    study.add_argument("course_id")
    study.add_argument("topic_id")
    study.add_argument("topic_title")
    study.add_argument("mode", choices=("explain", "practice", "review"))
    study.add_argument("objective")
    study.add_argument("--material", action="append", default=[])

    context = commands.add_parser("course-context", help="prepare a portable course handoff")
    context.add_argument("term")
    context.add_argument("course_id")
    context.add_argument("--material", action="append", default=[])

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

    semester_render = commands.add_parser("render-semester")
    semester_render.add_argument("term")
    return result


def main(argv: list[str] | None = None) -> int:
    cli = parser()
    args = cli.parse_args(argv)
    try:
        root = _root(args.data_root)
        if args.command == "init":
            ws = initialize_course(root, args.term, args.course_id, args.title)
            print(ws.course_dir)
        elif args.command == "semester":
            sw = initialize_semester(root, args.term, args.title)
            print(sw.term_dir)
        elif args.command == "course":
            sw = semester_workspace(root, args.term)
            ws = register_course(
                sw,
                args.course_id,
                args.title,
                capability_tags=args.capability,
                sources=_sources(args.source),
                metadata=_metadata(args.metadata),
            )
            print(ws.course_dir)
        elif args.command == "add-material":
            ws = workspace(root, args.term, args.course_id)
            value = add_material(ws, args.source, args.material_id, args.title, replace=args.replace)
            print(json.dumps(value, sort_keys=True))
        elif args.command == "intake":
            intake_updates = {}
            for argument, field in (("kind", "kind"), ("status", "status")):
                value = getattr(args, argument)
                if value is not None:
                    intake_updates[field] = value
            if args.clear_date:
                intake_updates["relevant_date"] = None
            elif args.date is not None:
                intake_updates["relevant_date"] = args.date
            if args.clear_topics:
                intake_updates["topic_ids"] = []
            elif args.topic is not None:
                intake_updates["topic_ids"] = args.topic
            if args.clear_assessments:
                intake_updates["assessment_ids"] = []
            elif args.assessment is not None:
                intake_updates["assessment_ids"] = args.assessment
            if args.clear_provenance:
                intake_updates["source_descriptor"] = None
            elif args.provenance is not None:
                intake_updates["source_descriptor"] = args.provenance
            value = intake_material(
                workspace(root, args.term, args.course_id),
                args.source,
                args.material_id,
                args.title,
                provenance_status=args.provenance_status,
                observed_at=args.observed_at,
                replace=args.replace,
                **intake_updates,
            )
            print(
                f"Intake: {value['id']} | {value['kind']}/{value['status']} | "
                f"{value['bytes']} bytes | sha256 {value['sha256']}"
            )
        elif args.command == "assessment":
            assessment_updates = {}
            if args.type is not None:
                assessment_updates["assessment_type"] = args.type
            if args.status is not None:
                assessment_updates["status"] = args.status
            for field in ("weight", "points", "xp"):
                if getattr(args, f"clear_{field}"):
                    assessment_updates[field] = None
                elif getattr(args, field) is not None:
                    assessment_updates[field] = getattr(args, field)
            if args.clear_materials:
                assessment_updates["material_ids"] = []
            elif args.material is not None:
                assessment_updates["material_ids"] = args.material
            if args.clear_topics:
                assessment_updates["topic_ids"] = []
            elif args.topic is not None:
                assessment_updates["topic_ids"] = args.topic
            value = upsert_assessment(
                workspace(root, args.term, args.course_id),
                args.assessment_id,
                args.title,
                claim_field=args.claim_field,
                claim_value=args.claim_value,
                claim_source=args.claim_source,
                claim_observed_at=args.claim_observed_at,
                claim_status=args.claim_status,
                **assessment_updates,
            )
            print(json.dumps(value, sort_keys=True))
        elif args.command == "policy":
            value = upsert_policy(
                workspace(root, args.term, args.course_id),
                args.policy_id,
                args.title,
                args.category,
                args.rule,
                args.source,
                status=args.status,
                observed_at=args.observed_at,
            )
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
        elif args.command == "course-context":
            handoff = prepare_course_handoff(
                workspace(root, args.term, args.course_id), args.material
            )
            print("Course handoff ready.")
            print(f"Handoff: {handoff['root']}")
            print(f"Attachments: {handoff['attachments']}")
            print(f"Context: {handoff['context']}")
            print(f"Prompt: {handoff['prompt']}")
            print(
                "Attach every required file under "
                f"{handoff['attachments']} to the approved AI interface, then paste prompt.txt."
            )
        elif args.command == "record":
            value = record_session(
                workspace(root, args.term, args.course_id),
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
            print("\n".join(str(path) for path in render_course(workspace(root, args.term, args.course_id))))
        elif args.command == "render-semester":
            print(render_semester(semester_workspace(root, args.term)))
        else:  # pragma: no cover
            raise AssertionError(args.command)
    except SchoolLearningError as error:
        cli.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
