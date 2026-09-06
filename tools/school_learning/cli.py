"""Command-line interface for the bounded School Learning workflow."""

from __future__ import annotations

import argparse
import hashlib
import os
import json
import shlex
import platform
import shutil
import subprocess
import sys
from pathlib import Path, PureWindowsPath

from . import core
from .core import (
    ASSESSMENT_STATUSES,
    ASSESSMENT_TYPES,
    CAPABILITY_TAGS,
    CLAIM_STATUSES,
    MATERIAL_KINDS,
    MATERIAL_LIFECYCLES,
    SOURCE_OBSERVATION_OUTCOMES,
    SOURCE_OBSERVATION_SCOPES,
    SchoolLearningError,
    add_material,
    append_source_observation,
    apply_update,
    default_data_root,
    ensure_topic,
    initialize_course,
    initialize_semester,
    intake_material,
    prepare_course_handoff,
    prepare_refresh,
    prepare_study_handoff,
    record_session,
    register_course,
    review_update,
    semester_workspace,
    upsert_assessment,
    upsert_policy,
    upsert_source,
    workspace,
)
from .render import render_course, render_plan, render_semester


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


def _refresh_open_identity(path: Path) -> tuple[int, int]:
    """Validate the completed content-addressed package without following links.

    This is an opening guard, not candidate review or package generation.
    No owner-return bytes are read and no source evidence paths are accessed.
    """
    _, manifest_bytes, _ = core._read_refresh_source(path / "manifest.json", 1_000_000)
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    package_id = manifest.pop("package_id")
    if (manifest.get("schema_version") != core.REFRESH_PACKAGE_SCHEMA
            or hashlib.sha256(core._canonical_json_bytes(manifest)).hexdigest() != package_id
            or path.name != "refresh-package-" + package_id):
        raise SchoolLearningError("completed refresh package identity does not match")
    # Reconstruct only the fixed course location, never a manifest-provided path.
    ws = workspace(path.parent.parent.parent.parent, manifest["term"], manifest["course_id"])
    if path != ws.course_dir / "generated" / ("refresh-package-" + package_id):
        raise SchoolLearningError("refresh opening target is outside its course location")
    core._inspect_real_tree(ws, path, "refresh opening target")
    before = os.lstat(path)
    required = {
        "START-HERE.md", "prompt.txt", "attachments/course-context.md",
        "attachments/update-contract.json", "attachments/refresh-context.json",
    }
    if set(manifest["generated_files"]) != required:
        raise SchoolLearningError("refresh opening target is incomplete")
    expected = {"manifest.json": manifest_bytes}
    for relative, identity in manifest["generated_files"].items():
        _, content, _ = core._read_refresh_source(path / relative, identity["bytes"])
        if len(content) != identity["bytes"] or hashlib.sha256(content).hexdigest() != identity["sha256"]:
            raise SchoolLearningError("refresh generated content changed before opening")
        expected[relative] = content
    entries = manifest["materials"] + manifest["evidence"]
    filenames = [entry["attachment_filename"] for entry in entries]
    if any(not isinstance(name, str) or Path(name).name != name or name in {".", ".."}
           or "/" in name or "\\" in name for name in filenames):
        raise SchoolLearningError("unsafe refresh opening attachment name")
    if manifest["attachment_filenames"] != sorted(
        ["course-context.md", "update-contract.json", "refresh-context.json"] + filenames
    ):
        raise SchoolLearningError("refresh opening attachment list is incomplete")
    manifest["package_id"] = package_id
    core._validate_refresh_package(ws, path, expected, manifest)
    core._confined_path(ws, path, label="refresh opening target", must_exist=True,
                        require_directory=True)
    after = os.lstat(path)
    if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
        raise SchoolLearningError("refresh opening target was replaced during validation")
    return after.st_dev, after.st_ino


def _open_refresh_directory(path: Path) -> None:
    """Best-effort WSL/Windows convenience, independent of package success."""
    try:
        if sys.platform != "linux" or "microsoft" not in platform.release().lower():
            raise OSError("directory opening is unsupported on this host")
        converter = shutil.which("wslpath")
        explorer = shutil.which("explorer.exe")
        if not converter or not explorer:
            raise OSError("wslpath or explorer.exe is unavailable")
        prepared_identity = _refresh_open_identity(path)
        converted = subprocess.run(
            [converter, "-w", str(path)], check=True, capture_output=True,
            text=True, encoding="utf-8", timeout=5,
        ).stdout.removesuffix("\n")
        if (not PureWindowsPath(converted).is_absolute()
                or any(char in converted for char in "\r\n\x00")):
            raise OSError("invalid Windows package path conversion")
        roundtrip = subprocess.run(
            [converter, "-u", converted], check=True, capture_output=True,
            text=True, encoding="utf-8", timeout=5,
        ).stdout.removesuffix("\n")
        if roundtrip != str(path):
            raise OSError("Windows package path conversion did not round-trip exactly")
        # The conversion calls can yield to another process. Recheck the exact
        # completed package and inode immediately before the host launch.
        if _refresh_open_identity(path) != prepared_identity:
            raise SchoolLearningError("refresh opening target was replaced before launch")
        subprocess.run([explorer, converted], check=True, capture_output=True, timeout=5)
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError) as error:
        print(f"Warning: package is ready but could not be opened ({type(error).__name__}). "
              f"Open the package directory manually: {path}", file=sys.stderr)


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

    source = commands.add_parser("source", help="add or maintain one course source descriptor")
    source.add_argument("term")
    source.add_argument("course_id")
    source.add_argument("source_id")
    source.add_argument("title")
    source.add_argument("reference")
    source.add_argument("--status", choices=CLAIM_STATUSES, default="provisional")
    source.add_argument("--recorded-at")

    observe = commands.add_parser("observe", help="append one durable course source observation")
    observe.add_argument("term")
    observe.add_argument("course_id")
    observe.add_argument("source_id")
    observe.add_argument("--scope", choices=SOURCE_OBSERVATION_SCOPES, required=True)
    observe.add_argument("--outcome", choices=SOURCE_OBSERVATION_OUTCOMES, required=True)
    observe.add_argument("--material", action="append", default=[])
    observe.add_argument("--note", default="")
    observe.add_argument("--observed-at")
    observe.add_argument("--id", dest="observation_id")

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

    refresh = commands.add_parser("prepare-refresh", help="prepare an explicit course refresh package")
    refresh.add_argument("term")
    refresh.add_argument("course_id")
    refresh.add_argument("--material", action="append", nargs="+", default=[])
    refresh.add_argument("--evidence", action="append", nargs="+", default=[])
    refresh_notes = refresh.add_mutually_exclusive_group()
    refresh_notes.add_argument("--notes")
    refresh_notes.add_argument("--notes-file")
    refresh.add_argument("--open", action="store_true")

    review = commands.add_parser("review-update", help="validate and preview a reviewed candidate")
    review.add_argument("path")

    apply = commands.add_parser("apply-update", help="atomically apply a confirmed reviewed candidate")
    apply.add_argument("path")
    apply.add_argument("--confirm", required=True)

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

    plan = commands.add_parser("render-plan", help="render a deterministic derived semester plan")
    plan.add_argument("term")
    plan.add_argument("--as-of", required=True)
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
        elif args.command == "source":
            value = upsert_source(
                workspace(root, args.term, args.course_id),
                args.source_id,
                args.title,
                args.reference,
                status=args.status,
                recorded_at=args.recorded_at,
            )
            print(json.dumps(value, sort_keys=True))
        elif args.command == "observe":
            value = append_source_observation(
                workspace(root, args.term, args.course_id),
                args.source_id,
                args.scope,
                args.outcome,
                material_ids=args.material,
                note=args.note,
                observed_at=args.observed_at,
                observation_id=args.observation_id,
            )
            print(json.dumps(value, sort_keys=True))
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
        elif args.command == "prepare-refresh":
            package = prepare_refresh(
                workspace(root, args.term, args.course_id),
                [item for group in args.material for item in group],
                [item for group in args.evidence for item in group],
                notes=args.notes, notes_file=args.notes_file,
            )
            print("Refresh package ready.")
            print(f"Package: {package['root']}")
            print(f"Attach every file in: {package['attachments']}")
            print(f"Then paste: {package['prompt']}")
            print(f"Save the UTF-8 candidate to: {package['reviewed_update']}")
            print("Review command:")
            print(shlex.join(["./school", "--data-root", str(root), "review-update",
                              str(package["reviewed_update"])]))
            if args.open:
                _open_refresh_directory(package["root"])
        elif args.command == "review-update":
            result = review_update(root, args.path)
            print(result["preview"], end="")
            print("Apply command:")
            print(
                shlex.join(
                    [
                        "./school",
                        "--data-root",
                        str(root),
                        "apply-update",
                        str(result["path"]),
                        "--confirm",
                        result["digest"],
                    ]
                )
            )
        elif args.command == "apply-update":
            print(json.dumps(apply_update(root, args.path, args.confirm), sort_keys=True, default=str))
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
        elif args.command == "render-plan":
            print(render_plan(semester_workspace(root, args.term), args.as_of))
        else:  # pragma: no cover
            raise AssertionError(args.command)
    except SchoolLearningError as error:
        cli.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
