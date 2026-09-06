import hashlib
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest import mock

from tools.school_learning import (
    SchoolLearningError,
    add_material,
    append_source_observation,
    apply_update,
    build_study_brief,
    course_context_sha256,
    ensure_topic,
    initialize_course,
    initialize_semester,
    intake_material,
    iter_sessions,
    load_course,
    load_course_core,
    load_materials,
    load_semester,
    load_source_observations,
    load_topics,
    prepare_course_handoff,
    prepare_refresh,
    record_session,
    register_course,
    render_course,
    render_plan,
    render_semester,
    review_update,
    reviewed_update_digest,
    semester_workspace,
    upsert_assessment,
    upsert_policy,
    upsert_source,
    workspace,
)
from tools.school_learning import core
from tools.school_learning.cli import main as cli_main, parser as cli_parser


TIMESTAMP = "2026-07-21T15:00:00Z"


def complete_snapshot(root):
    if not root.exists() and not root.is_symlink():
        return None
    result = {".": ("directory", None)}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = ("symlink", os.readlink(path))
        elif path.is_dir():
            result[relative] = ("directory", None)
        else:
            result[relative] = ("file", path.read_bytes())
    return result


class ExternalTemporaryTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir="/var/tmp")
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()


class WorkspaceTestCase(ExternalTemporaryTestCase):
    def setUp(self):
        super().setUp()
        self.ws = self.initialize()

    def initialize(self, course_id="cs3100"):
        return initialize_course(
            self.root,
            "2026-fall",
            course_id,
            "Data Structures and Algorithms 2",
            created_at=TIMESTAMP,
        )

    def material(self, name="notes.md", content=b"# Graphs\nBreadth-first search.\n"):
        path = self.root / name
        path.write_bytes(content)
        return path

    def workspace_snapshot(self):
        return {
            path.relative_to(self.ws.course_dir).as_posix(): path.read_bytes()
            for path in self.ws.course_dir.rglob("*")
            if path.is_file() and not path.is_symlink()
        }

    def json_state(self, name):
        return json.loads((self.ws.course_dir / name).read_text(encoding="utf-8"))

    def write_json_state(self, name, value):
        (self.ws.course_dir / name).write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def assert_rejected_without_mutation(self, operation):
        before = self.workspace_snapshot()
        with self.assertRaises(SchoolLearningError):
            operation()
        self.assertEqual(self.workspace_snapshot(), before)

    def add_default_material(self, **changes):
        values = {
            "source": self.material(),
            "material_id": "lecture-graphs",
            "title": "Graph Lecture",
            "added_at": "2026-07-21T15:01:00Z",
        }
        values.update(changes)
        return add_material(self.ws, **values)

    def add_topic_and_session(self):
        self.add_default_material()
        ensure_topic(self.ws, "bfs", "Breadth-first search", ["lecture-graphs"])
        return record_session(
            self.ws,
            "bfs",
            "partial",
            "review",
            "Missed queue invariant",
            mode="practice",
            session_id="session-001",
            recorded_at="2026-07-21T15:05:00Z",
            next_review_priority=90,
        )


class SchoolLearningTests(WorkspaceTestCase):
    def test_workspace_rejects_traversal(self):
        for value in ("../escape", "a/b", "..", "/tmp"):
            with self.subTest(value=value), self.assertRaises(SchoolLearningError):
                workspace(self.root, value, "cs3100")

    def test_initial_state_uses_exact_schemas(self):
        self.assertEqual(load_course(self.ws)["schema_version"], core.COURSE_SCHEMA)
        self.assertEqual(load_materials(self.ws)["materials"], [])
        self.assertEqual(load_topics(self.ws)["topics"], [])

    def test_material_hash_and_change_detection(self):
        source = self.material(content=b"alpha\n")
        first = add_material(
            self.ws, source, "lecture-01", "Lecture 1", added_at="2026-07-21T15:01:00Z"
        )
        self.assertTrue(first["changed"])
        same = add_material(
            self.ws,
            source,
            "lecture-01",
            "Lecture 1",
            added_at="2026-07-21T15:02:00Z",
            replace=True,
        )
        self.assertFalse(same["changed"])
        source.write_bytes(b"beta\n")
        changed = add_material(
            self.ws,
            source,
            "lecture-01",
            "Lecture 1",
            added_at="2026-07-21T15:03:00Z",
            replace=True,
        )
        self.assertTrue(changed["changed"])
        self.assertNotEqual(first["sha256"], changed["sha256"])

    def test_final_stored_file_matches_independent_digest_and_byte_count(self):
        result = self.add_default_material()
        stored = self.ws.course_dir / result["stored_path"]
        content = stored.read_bytes()
        self.assertEqual(hashlib.sha256(content).hexdigest(), result["sha256"])
        self.assertEqual(len(content), result["bytes"])

    def test_matching_manifest_with_missing_destination_is_repaired(self):
        first = self.add_default_material()
        stored = self.ws.course_dir / first["stored_path"]
        stored.unlink()
        repaired = add_material(
            self.ws,
            self.root / "notes.md",
            "lecture-graphs",
            "Graph Lecture",
            added_at="2026-07-21T15:02:00Z",
            replace=True,
        )
        self.assertTrue(repaired["changed"])
        self.assertEqual(stored.read_bytes(), (self.root / "notes.md").read_bytes())
        self.assertEqual(core.sha256_file(stored), (repaired["sha256"], repaired["bytes"]))

    def test_matching_manifest_with_corrupted_destination_is_repaired(self):
        first = self.add_default_material()
        stored = self.ws.course_dir / first["stored_path"]
        stored.write_bytes(b"corrupted\n")
        repaired = add_material(
            self.ws,
            self.root / "notes.md",
            "lecture-graphs",
            "Graph Lecture",
            added_at="2026-07-21T15:02:00Z",
            replace=True,
        )
        self.assertTrue(repaired["changed"])
        self.assertEqual(core.sha256_file(stored), (repaired["sha256"], repaired["bytes"]))

    def test_source_path_replacement_during_open_copy_keeps_one_stream_identity(self):
        source = self.material(content=b"opened source bytes\n")
        replacement = self.material("replacement.md", b"later path bytes\n")
        original_open = core.os.open
        original_replace = core.os.replace
        replaced = False

        def open_then_replace(path, flags, *args, **kwargs):
            nonlocal replaced
            fd = original_open(path, flags, *args, **kwargs)
            if Path(path) == source and not replaced:
                original_replace(replacement, source)
                replaced = True
            return fd

        with mock.patch("tools.school_learning.core.os.open", side_effect=open_then_replace):
            result = add_material(
                self.ws,
                source,
                "lecture-01",
                "Lecture 1",
                added_at="2026-07-21T15:01:00Z",
            )
        stored = self.ws.course_dir / result["stored_path"]
        self.assertEqual(stored.read_bytes(), b"opened source bytes\n")
        self.assertEqual(core.sha256_file(stored), (result["sha256"], result["bytes"]))
        self.assertEqual(source.read_bytes(), b"later path bytes\n")

    def test_manifest_write_failure_after_copy_restores_old_material_and_manifest(self):
        self.add_default_material()
        before = self.workspace_snapshot()
        source = self.material("replacement.md", b"new bytes\n")

        def fail_manifest(ws, path, value):
            self.assertEqual(path.name, "materials.json")
            raise OSError("injected manifest failure")

        with mock.patch("tools.school_learning.core._atomic_write_json", side_effect=fail_manifest):
            with self.assertRaises(SchoolLearningError):
                add_material(
                    self.ws,
                    source,
                    "lecture-graphs",
                    "Replacement",
                    added_at="2026-07-21T15:02:00Z",
                    replace=True,
                )
        self.assertEqual(self.workspace_snapshot(), before)
        self.assertEqual([path.name for path in (self.ws.course_dir / "materials").iterdir()], ["lecture-graphs.md"])

    def test_extension_changing_replacement_failure_restores_complete_old_state(self):
        self.add_default_material()
        before = self.workspace_snapshot()
        source = self.material("replacement.txt", b"new text bytes\n")
        with mock.patch(
            "tools.school_learning.core._atomic_write_json",
            side_effect=OSError("injected manifest failure"),
        ):
            with self.assertRaises(SchoolLearningError):
                add_material(
                    self.ws,
                    source,
                    "lecture-graphs",
                    "Replacement",
                    added_at="2026-07-21T15:02:00Z",
                    replace=True,
                )
        self.assertEqual(self.workspace_snapshot(), before)
        self.assertTrue((self.ws.course_dir / "materials/lecture-graphs.md").exists())
        self.assertFalse((self.ws.course_dir / "materials/lecture-graphs.txt").exists())
        self.assertFalse(any("backup" in path.name or path.name.startswith(".material") for path in self.ws.course_dir.rglob("*")))

    def test_manifest_failure_after_actual_persistence_restores_exact_old_manifest(self):
        self.add_default_material()
        before = self.workspace_snapshot()
        source = self.material("replacement.md", b"replacement bytes\n")
        real_write = core._atomic_write_json

        def write_then_fail(ws, path, value):
            real_write(ws, path, value)
            raise OSError("failure after persistence")

        with mock.patch("tools.school_learning.core._atomic_write_json", side_effect=write_then_fail):
            with self.assertRaises(SchoolLearningError):
                add_material(
                    self.ws,
                    source,
                    "lecture-graphs",
                    "Replacement",
                    added_at="2026-07-21T15:02:00Z",
                    replace=True,
                )
        self.assertEqual(self.workspace_snapshot(), before)

    def test_unsupported_material_is_rejected(self):
        with self.assertRaises(SchoolLearningError):
            add_material(self.ws, self.material("video.mp4"), "video", "Video")

    def test_study_brief_is_grounded_and_inside_workspace(self):
        self.add_default_material()
        ensure_topic(self.ws, "bfs", "Breadth-first search", ["lecture-graphs"])
        brief = build_study_brief(self.ws, "bfs", "practice", "Practice BFS traversal")
        text = brief.read_text()
        self.assertIn("`lecture-graphs`", text)
        self.assertIn("insufficient", text)
        self.assertIn("does not update learning state automatically", text)
        with self.assertRaises(SchoolLearningError):
            build_study_brief(self.ws, "bfs", "practice", "Escape", output=self.root / "outside.md")

    def test_record_updates_topic_and_preserves_complete_session(self):
        self.add_default_material()
        ensure_topic(self.ws, "bfs", "Breadth-first search", ["lecture-graphs"])
        record = record_session(
            self.ws,
            "bfs",
            "partial",
            "review",
            "Missed queue invariant",
            mode="practice",
            session_id="session-001",
            recorded_at="2026-07-21T15:05:00Z",
            next_review_priority=90,
        )
        self.assertEqual(record["outcome"], "partial")
        self.assertEqual(record["mode"], "practice")
        self.assertEqual(record["material_ids"], ["lecture-graphs"])
        topic = load_topics(self.ws)["topics"][0]
        self.assertEqual(topic["status"], "review")
        self.assertEqual(topic["next_review_priority"], 90)
        self.assertEqual(iter_sessions(self.ws), [record])

    def test_invalid_json_state_is_rejected_without_mutation(self):
        path = self.ws.course_dir / "topics.json"
        path.write_text("not json", encoding="utf-8")
        self.assert_rejected_without_mutation(lambda: ensure_topic(self.ws, "bfs", "Breadth-first search"))

    def test_atomic_write_failure_preserves_old_file_and_cleans_temp(self):
        target = self.ws.course_dir / "topics.json"
        before = target.read_bytes()
        with mock.patch("tools.school_learning.core.os.replace", side_effect=OSError("blocked")):
            with self.assertRaises(SchoolLearningError):
                core._atomic_write_json(
                    self.ws,
                    target,
                    {"schema_version": core.TOPICS_SCHEMA, "topics": []},
                )
        self.assertEqual(target.read_bytes(), before)
        self.assertEqual([path for path in target.parent.iterdir() if path.name.startswith(".topics.json.")], [])

    def test_rendering_is_stable_for_identical_state_and_escapes_html(self):
        ensure_topic(self.ws, "bfs", "BFS <script>")
        record_session(
            self.ws,
            "bfs",
            "correct",
            "learning",
            "Good <work>",
            mode="explain",
            session_id="session-001",
            recorded_at="2026-07-21T15:05:00Z",
            next_review_priority=25,
        )
        first = render_course(self.ws)
        first_bytes = tuple(path.read_bytes() for path in first)
        second = render_course(self.ws)
        self.assertEqual(first_bytes, tuple(path.read_bytes() for path in second))
        html = first[0].read_text()
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_no_network_or_model_dependencies_in_production_modules(self):
        production = [
            Path(core.__file__),
            Path(__import__("tools.school_learning.render", fromlist=["x"]).__file__),
            Path(__import__("tools.school_learning.cli", fromlist=["x"]).__file__),
        ]
        forbidden = ("socket", "requests", "urllib", "httpx", "openai", "anthropic")
        combined = "\n".join(path.read_text(encoding="utf-8") for path in production)
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(f"import {token}", combined)
                self.assertNotIn(f"from {token}", combined)
        # The accepted refresh opener is CLI-only; core/render retain no process capability.
        for path in production[:2]:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("import subprocess", text)
            self.assertNotIn("from subprocess", text)


class StudyHandoffTests(WorkspaceTestCase):
    def prepare(self, material_ids=(), *, mode="practice", objective="Practice BFS traversal"):
        ensure_topic(self.ws, "bfs", "Breadth-first search", material_ids)
        return core.prepare_study_handoff(self.ws, "bfs", mode, objective)

    def handoff_snapshot(self):
        root = self.ws.course_dir / "generated/study-handoff"
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob("*")
            if path.is_file() and not path.is_symlink()
        }

    def assert_no_publication_artifacts(self):
        generated = self.ws.course_dir / "generated"
        artifacts = [
            path.relative_to(generated).as_posix()
            for path in generated.rglob("*")
            if path.name.startswith(".study-handoff")
            or path.name in {"backup", "failed-new", "placeholder", "retiring", "rollback"}
        ]
        self.assertEqual(artifacts, [])

    def add_second_material(self):
        return add_material(
            self.ws,
            self.material("chapters-1-3.pdf", b"%PDF-1.7\nsynthetic review list\n"),
            "review-list",
            "Chapters 1-3 Review List",
            added_at="2026-07-21T15:02:00Z",
        )

    def test_zero_material_handoff_has_exact_package_structure(self):
        handoff = self.prepare()
        root = handoff["root"]
        self.assertEqual(
            sorted(path.name for path in root.iterdir()),
            ["START-HERE.md", "attachments", "manifest.json", "prompt.txt"],
        )
        self.assertEqual(
            sorted(path.name for path in handoff["attachments"].iterdir()),
            ["study-brief.md"],
        )
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], core.STUDY_HANDOFF_SCHEMA)
        self.assertEqual(manifest["attachment_filenames"], ["study-brief.md"])
        self.assertEqual(manifest["material_ids"], [])
        self.assertEqual(manifest["materials"], [])

    def test_one_selected_material_is_copied_byte_identically(self):
        record = self.add_default_material()
        handoff = self.prepare(["lecture-graphs"])
        copied = handoff["attachments"] / "material-lecture-graphs.md"
        source = self.ws.course_dir / record["stored_path"]
        self.assertEqual(copied.read_bytes(), source.read_bytes())
        self.assertEqual(core.sha256_file(copied), (record["sha256"], record["bytes"]))
        self.assertEqual(
            sorted(path.name for path in handoff["attachments"].iterdir()),
            ["material-lecture-graphs.md", "study-brief.md"],
        )

    def test_multiple_selected_materials_include_exactly_the_selection(self):
        first = self.add_default_material()
        second = self.add_second_material()
        excluded = add_material(
            self.ws,
            self.material("optional.txt", b"optional material\n"),
            "optional",
            "Optional",
            added_at="2026-07-21T15:03:00Z",
        )
        handoff = self.prepare(["review-list", "lecture-graphs"])
        names = sorted(path.name for path in handoff["attachments"].iterdir())
        self.assertEqual(
            names,
            ["material-lecture-graphs.md", "material-review-list.pdf", "study-brief.md"],
        )
        self.assertNotIn(f"material-{excluded['id']}.txt", names)
        self.assertEqual(
            (handoff["attachments"] / "material-lecture-graphs.md").read_bytes(),
            (self.ws.course_dir / first["stored_path"]).read_bytes(),
        )
        self.assertEqual(
            (handoff["attachments"] / "material-review-list.pdf").read_bytes(),
            (self.ws.course_dir / second["stored_path"]).read_bytes(),
        )

    def test_manifest_rejects_duplicate_and_unsafe_attachment_filenames(self):
        self.add_default_material()
        self.add_second_material()
        handoff = self.prepare(["lecture-graphs", "review-list"])
        manifest = json.loads((handoff["root"] / "manifest.json").read_text(encoding="utf-8"))
        duplicate = json.loads(json.dumps(manifest))
        duplicate["materials"][1]["attachment_filename"] = duplicate["materials"][0][
            "attachment_filename"
        ]
        duplicate["attachment_filenames"][2] = duplicate["attachment_filenames"][1]
        with self.assertRaises(SchoolLearningError):
            core._validate_study_handoff_manifest(duplicate)
        unsafe = json.loads(json.dumps(manifest))
        unsafe["materials"][0]["attachment_filename"] = "../material-lecture-graphs.md"
        unsafe["attachment_filenames"][1] = "../material-lecture-graphs.md"
        with self.assertRaises(SchoolLearningError):
            core._validate_study_handoff_manifest(unsafe)

    def test_recorded_byte_mismatch_fails_before_handoff_output(self):
        self.add_default_material()
        ensure_topic(self.ws, "bfs", "Breadth-first search", ["lecture-graphs"])
        state = self.json_state("materials.json")
        state["materials"][0]["bytes"] += 1
        self.write_json_state("materials.json", state)
        with self.assertRaises(SchoolLearningError):
            core.prepare_study_handoff(self.ws, "bfs", "practice", "Practice")
        self.assertFalse((self.ws.course_dir / "generated/study-handoff").exists())

    def test_recorded_digest_mismatch_fails_before_handoff_output(self):
        self.add_default_material()
        ensure_topic(self.ws, "bfs", "Breadth-first search", ["lecture-graphs"])
        state = self.json_state("materials.json")
        state["materials"][0]["sha256"] = "0" * 64
        self.write_json_state("materials.json", state)
        with self.assertRaises(SchoolLearningError):
            core.prepare_study_handoff(self.ws, "bfs", "practice", "Practice")
        self.assertFalse((self.ws.course_dir / "generated/study-handoff").exists())

    def test_source_mutation_during_preparation_fails_without_publishing(self):
        record = self.add_default_material()
        ensure_topic(self.ws, "bfs", "Breadth-first search", ["lecture-graphs"])
        source = self.ws.course_dir / record["stored_path"]
        real_compare = core._files_are_identical

        def mutate_then_compare(ws, first, second):
            source.write_bytes(b"mutated while preparing\n")
            return real_compare(ws, first, second)

        with mock.patch(
            "tools.school_learning.core._files_are_identical", side_effect=mutate_then_compare
        ):
            with self.assertRaises(SchoolLearningError):
                core.prepare_study_handoff(self.ws, "bfs", "practice", "Practice")
        self.assertFalse((self.ws.course_dir / "generated/study-handoff").exists())
        self.assertFalse(
            any(path.name.startswith(".study-handoff") for path in (self.ws.course_dir / "generated").iterdir())
        )

    def test_attachment_mutation_after_copy_validation_fails_before_publication(self):
        self.add_default_material()
        self.add_second_material()
        ensure_topic(
            self.ws,
            "bfs",
            "Breadth-first search",
            ["lecture-graphs", "review-list"],
        )
        real_copy = core._copy_verified_material_attachment

        def copy_then_mutate(ws, record, destination):
            real_copy(ws, record, destination)
            if record["id"] == "review-list":
                (destination.parent / "material-lecture-graphs.md").write_bytes(
                    b"changed after individual copy validation\n"
                )

        with mock.patch(
            "tools.school_learning.core._copy_verified_material_attachment",
            side_effect=copy_then_mutate,
        ):
            with self.assertRaises(SchoolLearningError):
                core.prepare_study_handoff(self.ws, "bfs", "practice", "Practice")
        self.assertFalse((self.ws.course_dir / "generated/study-handoff").exists())
        self.assertFalse(
            any(
                path.name.startswith(".study-handoff")
                for path in (self.ws.course_dir / "generated").iterdir()
            )
        )

    def test_final_pre_install_validation_detects_mutation_after_real_retirement(self):
        self.add_default_material()
        self.prepare(["lecture-graphs"], objective="Prior objective")
        before = self.handoff_snapshot()
        real_validate = core._validate_staged_handoff
        real_replace = core.os.replace
        validation_calls = 0
        retirement_happened = False

        def observe_validation(ws, staging, manifest, expected_files, selected):
            nonlocal validation_calls
            real_validate(ws, staging, manifest, expected_files, selected)
            validation_calls += 1

        def retire_then_mutate(source, destination):
            nonlocal retirement_happened
            result = real_replace(source, destination)
            if Path(source).name == "study-handoff" and Path(destination).name == "retiring":
                retirement_happened = True
                staging = next(
                    path
                    for path in (self.ws.course_dir / "generated").iterdir()
                    if path.name.startswith(".study-handoff.staging.")
                )
                (staging / "attachments" / "material-lecture-graphs.md").write_bytes(
                    b"changed during the final pre-install transition gap\n"
                )
            return result

        with (
            mock.patch(
                "tools.school_learning.core._validate_staged_handoff",
                side_effect=observe_validation,
            ),
            mock.patch("tools.school_learning.core.os.replace", side_effect=retire_then_mutate),
        ):
            with self.assertRaisesRegex(
                SchoolLearningError,
                "material attachment lecture-graphs changed before publication",
            ):
                self.prepare(["lecture-graphs"], objective="Replacement objective")
        self.assertTrue(retirement_happened)
        self.assertEqual(validation_calls, 2)
        self.assertEqual(self.handoff_snapshot(), before)
        self.assert_no_publication_artifacts()

    def test_symlinked_material_and_handoff_destination_are_rejected(self):
        record = self.add_default_material()
        ensure_topic(self.ws, "bfs", "Breadth-first search", ["lecture-graphs"])
        stored = self.ws.course_dir / record["stored_path"]
        external_material = self.root / "external.md"
        external_material.write_bytes(stored.read_bytes())
        stored.unlink()
        stored.symlink_to(external_material)
        with self.assertRaises(SchoolLearningError):
            core.prepare_study_handoff(self.ws, "bfs", "practice", "Practice")

        stored.unlink()
        stored.write_bytes(external_material.read_bytes())
        external_dir = self.root / "external-handoff"
        external_dir.mkdir()
        sentinel = external_dir / "sentinel.txt"
        sentinel.write_bytes(b"unchanged\n")
        destination = self.ws.course_dir / "generated/study-handoff"
        destination.symlink_to(external_dir, target_is_directory=True)
        with self.assertRaises(SchoolLearningError):
            core.prepare_study_handoff(self.ws, "bfs", "practice", "Practice")
        self.assertEqual(sentinel.read_bytes(), b"unchanged\n")

    def test_confinement_failure_does_not_create_handoff(self):
        self.add_default_material()
        ensure_topic(self.ws, "bfs", "Breadth-first search", ["lecture-graphs"])
        state = self.json_state("materials.json")
        state["materials"][0]["stored_path"] = "../lecture-graphs.md"
        self.write_json_state("materials.json", state)
        with self.assertRaises(SchoolLearningError):
            core.prepare_study_handoff(self.ws, "bfs", "practice", "Practice")
        self.assertFalse((self.ws.course_dir / "generated/study-handoff").exists())

    def test_new_run_removes_every_stale_handoff_file(self):
        self.add_default_material()
        first = self.prepare(["lecture-graphs"])
        stale = first["attachments"] / "stale-review.pdf"
        stale.write_bytes(b"stale\n")
        (first["root"] / "stale.txt").write_bytes(b"stale root\n")
        second = self.prepare([])
        self.assertEqual(
            sorted(path.name for path in second["attachments"].iterdir()), ["study-brief.md"]
        )
        self.assertFalse((second["root"] / "stale.txt").exists())

    def test_publication_rename_succeeds_then_raises_and_restores_prior_handoff(self):
        self.add_default_material()
        self.prepare(["lecture-graphs"], objective="First objective")
        before = self.handoff_snapshot()
        real_replace = core.os.replace
        raised_after_effect = False

        def publish_then_raise(source, destination):
            nonlocal raised_after_effect
            result = real_replace(source, destination)
            if (
                Path(source).name.startswith(".study-handoff.staging.")
                and Path(destination).name == "study-handoff"
                and not raised_after_effect
            ):
                raised_after_effect = True
                raise OSError("injected post-publication failure")
            return result

        with mock.patch("tools.school_learning.core.os.replace", side_effect=publish_then_raise):
            with self.assertRaisesRegex(
                SchoolLearningError,
                "study handoff publication could not be completed safely",
            ):
                self.prepare([], objective="Replacement objective")
        self.assertTrue(raised_after_effect)
        self.assertEqual(self.handoff_snapshot(), before)
        self.assert_no_publication_artifacts()

    def test_retirement_rename_succeeds_then_raises_and_restores_prior_handoff(self):
        self.add_default_material()
        self.prepare(["lecture-graphs"], objective="First objective")
        before = self.handoff_snapshot()
        real_replace = core.os.replace
        raised_after_effect = False

        def retire_then_raise(source, destination):
            nonlocal raised_after_effect
            result = real_replace(source, destination)
            if (
                Path(source).name == "study-handoff"
                and Path(destination).name == "retiring"
                and not raised_after_effect
            ):
                raised_after_effect = True
                raise OSError("injected post-retirement failure")
            return result

        with mock.patch("tools.school_learning.core.os.replace", side_effect=retire_then_raise):
            with self.assertRaisesRegex(
                SchoolLearningError,
                "study handoff retirement could not be completed safely",
            ):
                self.prepare([], objective="Replacement objective")
        self.assertTrue(raised_after_effect)
        self.assertEqual(self.handoff_snapshot(), before)
        self.assert_no_publication_artifacts()

    def test_late_retirement_cleanup_post_effect_failure_uses_untouched_rollback(self):
        self.add_default_material()
        self.prepare(["lecture-graphs"], objective="First objective")
        prior_root = self.ws.course_dir / "generated/study-handoff"
        (prior_root / "extra").mkdir()
        (prior_root / "extra/first.bin").write_bytes(b"\x00first prior bytes\xff")
        (prior_root / "extra/second.bin").write_bytes(b"\x00second prior bytes\xff")
        before = self.handoff_snapshot()
        real_remove = core._safe_remove_tree
        raised_after_effect = False

        def remove_then_raise(ws, path, label):
            nonlocal raised_after_effect
            if label == "retired study handoff" and not raised_after_effect:
                self.assertTrue((path.parent / "rollback").exists())
                real_remove(ws, path, label)
                raised_after_effect = True
                raise SchoolLearningError("injected post-retirement-cleanup failure")
            return real_remove(ws, path, label)

        with mock.patch(
            "tools.school_learning.core._safe_remove_tree",
            side_effect=remove_then_raise,
        ):
            with self.assertRaisesRegex(
                SchoolLearningError,
                "injected post-retirement-cleanup failure",
            ):
                self.prepare([], objective="Replacement objective")
        self.assertTrue(raised_after_effect)
        self.assertEqual(self.handoff_snapshot(), before)
        self.assert_no_publication_artifacts()

    def test_staging_cleanup_post_effect_failure_preserves_primary_error(self):
        self.add_default_material()
        ensure_topic(self.ws, "bfs", "Breadth-first search", ["lecture-graphs"])
        real_validate = core._validate_staged_handoff
        real_remove = core._safe_remove_tree
        cleanup_raised_after_effect = False

        def validate_then_raise(ws, staging, manifest, expected_files, selected):
            real_validate(ws, staging, manifest, expected_files, selected)
            raise SchoolLearningError("injected primary validation failure")

        def cleanup_then_raise(ws, path, label):
            nonlocal cleanup_raised_after_effect
            if label == "failed study handoff staging directory":
                real_remove(ws, path, label)
                cleanup_raised_after_effect = True
                raise SchoolLearningError("injected post-staging-cleanup failure")
            return real_remove(ws, path, label)

        with (
            mock.patch(
                "tools.school_learning.core._validate_staged_handoff",
                side_effect=validate_then_raise,
            ),
            mock.patch(
                "tools.school_learning.core._safe_remove_tree",
                side_effect=cleanup_then_raise,
            ),
        ):
            with self.assertRaisesRegex(
                SchoolLearningError,
                "injected primary validation failure",
            ) as raised:
                core.prepare_study_handoff(self.ws, "bfs", "practice", "Practice")
        self.assertTrue(cleanup_raised_after_effect)
        self.assertTrue(
            any(
                "injected post-staging-cleanup failure" in detail
                for detail in raised.exception.recovery_errors
            )
        )
        self.assertFalse((self.ws.course_dir / "generated/study-handoff").exists())
        self.assert_no_publication_artifacts()

    def test_first_publication_rename_succeeds_then_raises_without_published_handoff(self):
        self.add_default_material()
        real_replace = core.os.replace
        raised_after_effect = False

        def publish_then_raise(source, destination):
            nonlocal raised_after_effect
            result = real_replace(source, destination)
            if (
                Path(source).name.startswith(".study-handoff.staging.")
                and Path(destination).name == "study-handoff"
                and not raised_after_effect
            ):
                raised_after_effect = True
                raise OSError("injected first-publication post-effect failure")
            return result

        with mock.patch("tools.school_learning.core.os.replace", side_effect=publish_then_raise):
            with self.assertRaisesRegex(
                SchoolLearningError,
                "study handoff publication could not be completed safely",
            ):
                self.prepare(["lecture-graphs"], objective="First objective")
        self.assertTrue(raised_after_effect)
        self.assertFalse((self.ws.course_dir / "generated/study-handoff").exists())
        self.assert_no_publication_artifacts()

    def test_post_commit_cleanup_failure_cannot_convert_success_to_failure(self):
        self.add_default_material()
        self.prepare(["lecture-graphs"], objective="First objective")
        before = self.handoff_snapshot()
        real_remove = core._safe_remove_tree
        cleanup_raised_after_effect = False

        def cleanup_then_raise(ws, path, label):
            nonlocal cleanup_raised_after_effect
            if label == "completed study handoff rollback copy":
                real_remove(ws, path, label)
                cleanup_raised_after_effect = True
                raise SchoolLearningError("injected post-commit cleanup failure")
            return real_remove(ws, path, label)

        with mock.patch(
            "tools.school_learning.core._safe_remove_tree",
            side_effect=cleanup_then_raise,
        ):
            result = self.prepare([], objective="Replacement objective")
        self.assertTrue(cleanup_raised_after_effect)
        self.assertEqual(result["root"], self.ws.course_dir / "generated/study-handoff")
        self.assertNotEqual(self.handoff_snapshot(), before)
        self.assert_no_publication_artifacts()

    def test_cli_preserves_unsorted_legacy_topic_and_sorts_handoff_deterministically(self):
        self.add_default_material()
        self.add_second_material()
        ensure_topic(
            self.ws,
            "bfs",
            "Breadth-first search",
            ["lecture-graphs", "review-list"],
        )
        topics = self.json_state("topics.json")
        topics["topics"][0]["material_ids"] = ["review-list", "lecture-graphs"]
        self.write_json_state("topics.json", topics)
        topics_before = (self.ws.course_dir / "topics.json").read_bytes()
        args = [
            "--data-root",
            str(self.root),
            "study",
            "2026-fall",
            "cs3100",
            "bfs",
            "Breadth-first search",
            "practice",
            "Practice BFS",
            "--material",
            "lecture-graphs",
            "--material",
            "review-list",
        ]
        with redirect_stdout(io.StringIO()):
            self.assertEqual(cli_main(args), 0)
        root = self.ws.course_dir / "generated/study-handoff"
        first_snapshot = self.handoff_snapshot()
        legacy = (self.ws.course_dir / "generated/study-brief.md").read_bytes()
        self.assertLess(legacy.index(b"`review-list`"), legacy.index(b"`lecture-graphs`"))
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["material_ids"], ["lecture-graphs", "review-list"])
        self.assertEqual(
            manifest["attachment_filenames"],
            ["study-brief.md", "material-lecture-graphs.md", "material-review-list.pdf"],
        )
        self.assertEqual(
            sorted(path.name for path in (root / "attachments").iterdir()),
            ["material-lecture-graphs.md", "material-review-list.pdf", "study-brief.md"],
        )
        self.assertEqual((root / "attachments/study-brief.md").read_bytes(), legacy)
        prompt = (root / "prompt.txt").read_bytes()
        self.assertLess(prompt.index(b"`lecture-graphs`"), prompt.index(b"`review-list`"))

        with redirect_stdout(io.StringIO()):
            self.assertEqual(cli_main(args), 0)
        self.assertEqual(self.handoff_snapshot(), first_snapshot)
        self.assertEqual((self.ws.course_dir / "topics.json").read_bytes(), topics_before)

    def test_legacy_topic_materials_still_reject_duplicates_and_unknown_ids(self):
        self.add_default_material()
        ensure_topic(self.ws, "bfs", "Breadth-first search", ["lecture-graphs"])
        topics = self.json_state("topics.json")
        for material_ids in (
            ["lecture-graphs", "lecture-graphs"],
            ["lecture-graphs", "unknown-material"],
        ):
            with self.subTest(material_ids=material_ids):
                topics["topics"][0]["material_ids"] = material_ids
                self.write_json_state("topics.json", topics)
                with self.assertRaises(SchoolLearningError):
                    core.prepare_study_handoff(self.ws, "bfs", "practice", "Practice")
                self.assertFalse((self.ws.course_dir / "generated/study-handoff").exists())

    def test_prompt_and_start_here_preserve_manual_grounding_boundary(self):
        self.add_default_material()
        handoff = self.prepare(["lecture-graphs"], mode="review", objective="Recover BFS")
        prompt = handoff["prompt"].read_text(encoding="utf-8")
        for expected in (
            "Data Structures and Algorithms 2",
            "Breadth-first search",
            "`review`",
            "Recover BFS",
            "selected course-grounding evidence",
            "material identifier",
            "general background knowledge",
            "evidence is insufficient",
            "grade, mastery, permission, deadline, or course policy",
            "compact completion result",
            "owner will review",
            "must not update learner state automatically",
        ):
            self.assertIn(expected, prompt)
        start = (handoff["root"] / "START-HERE.md").read_text(encoding="utf-8")
        self.assertIn("Open `attachments/`", start)
        self.assertIn("Attach every file", start)
        self.assertIn("complete contents of `prompt.txt`", start)
        self.assertIn("Do not substitute similarly named files", start)
        self.assertIn("does not update learner state automatically", start)

    def test_manifest_is_strict_and_deterministic(self):
        self.add_second_material()
        first = self.prepare(["review-list"], objective="Review chapters")
        first_bytes = (first["root"] / "manifest.json").read_bytes()
        manifest = json.loads(first_bytes)
        self.assertEqual(
            set(manifest),
            {
                "schema_version",
                "course_id",
                "term",
                "topic_id",
                "mode",
                "objective",
                "attachment_filenames",
                "material_ids",
                "materials",
            },
        )
        self.assertEqual(core._validate_study_handoff_manifest(manifest), manifest)
        second = self.prepare(["review-list"], objective="Review chapters")
        self.assertEqual((second["root"] / "manifest.json").read_bytes(), first_bytes)
        unexpected = dict(manifest, unexpected=True)
        with self.assertRaises(SchoolLearningError):
            core._validate_study_handoff_manifest(unexpected)
        wrong_type = json.loads(json.dumps(manifest))
        wrong_type["materials"][0]["bytes"] = True
        with self.assertRaises(SchoolLearningError):
            core._validate_study_handoff_manifest(wrong_type)

    def test_existing_state_and_five_command_workflow_remain_compatible(self):
        self.add_topic_and_session()
        sessions_before = iter_sessions(self.ws)
        rendered_before = tuple(path.read_bytes() for path in render_course(self.ws))
        self.prepare(["lecture-graphs"])
        self.assertEqual(iter_sessions(self.ws), sessions_before)
        self.assertEqual(tuple(path.read_bytes() for path in render_course(self.ws)), rendered_before)
        action = next(action for action in cli_parser()._actions if action.dest == "command")
        self.assertTrue(
            {"init", "add-material", "study", "record", "render"}.issubset(action.choices)
        )

    def test_study_cli_prints_complete_handoff_instructions(self):
        self.add_default_material()
        output = io.StringIO()
        with redirect_stdout(output):
            result = cli_main(
                [
                    "--data-root",
                    str(self.root),
                    "study",
                    "2026-fall",
                    "cs3100",
                    "bfs",
                    "Breadth-first search",
                    "practice",
                    "Practice BFS",
                    "--material",
                    "lecture-graphs",
                ]
            )
        self.assertEqual(result, 0)
        text = output.getvalue()
        handoff = self.ws.course_dir / "generated/study-handoff"
        self.assertIn(str(handoff), text)
        self.assertIn(str(handoff / "attachments"), text)
        self.assertIn(str(handoff / "prompt.txt"), text)
        self.assertIn("Attach all files under", text)


class SemesterCoreTests(ExternalTemporaryTestCase):
    def setUp(self):
        super().setUp()
        self.sw = initialize_semester(
            self.root, "2026-fall", "Fall 2026", created_at="2026-08-26T12:00:00Z"
        )
        self.ws = register_course(
            self.sw,
            "cs3100",
            "Algorithms <Core>",
            capability_tags=["exam-mastery", "prerequisite-repair"],
            sources=[
                {
                    "id": "syllabus",
                    "title": "Syllabus <official>",
                    "reference": "local syllabus",
                    "status": "confirmed",
                }
            ],
            metadata={"section": "001"},
            recorded_at="2026-08-26T12:01:00Z",
        )

    def source(self, name="lecture.pptx", content=b"synthetic binary\x00payload"):
        path = self.root / name
        path.write_bytes(content)
        return path

    def semester_state_path(self):
        return self.sw.term_dir / ".school-learning" / "semester.json"

    def semester_generated_dir(self):
        return self.sw.term_dir / ".school-learning" / "generated"

    def intake(self, material_id="lecture-02", name="lecture.pptx", **kwargs):
        values = {
            "source": self.source(name),
            "material_id": material_id,
            "title": "Lecture <2>",
            "kind": "lecture",
            "status": "upcoming",
            "relevant_date": "2026-08-27",
            "source_descriptor": "course site",
            "provenance_status": "confirmed",
            "observed_at": "2026-08-26",
            "added_at": "2026-08-26T12:02:00Z",
        }
        values.update(kwargs)
        return intake_material(self.ws, **values)

    def candidate(self, operations, **changes):
        value = {
            "schema_version": core.REVIEWED_UPDATE_SCHEMA,
            "term": self.ws.term,
            "course_id": self.ws.course_id,
            "base_context_sha256": course_context_sha256(self.ws),
            "operations": operations,
        }
        value.update(changes)
        return value

    def write_candidate(self, value, name="reviewed-update.json"):
        path = self.root / name
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        return path

    def assessment_operation(self, **changes):
        value = {
            "kind": "assessment-upsert",
            "id": "ps-2",
            "title": "Problem Set 2",
            "type": "problem-set",
            "status": "upcoming",
            "weight": None,
            "points": "100",
            "xp": None,
            "material_ids": [],
            "topic_ids": [],
            "claims": [
                {
                    "field": "due-at",
                    "value": "2026-08-30",
                    "source": "syllabus",
                    "observed_at": "2026-08-29",
                    "status": "confirmed",
                }
            ],
            "recorded_at": "2026-08-29T12:00:00Z",
        }
        value.update(changes)
        return value

    def source_observation_operation(self, **changes):
        value = {
            "kind": "source-observation",
            "id": "reviewed-observation",
            "source_id": "syllabus",
            "observed_at": "2026-08-29",
            "scope": "full",
            "outcome": "changed",
            "material_ids": [],
            "note": "Synthetic reviewed observation.",
        }
        value.update(changes)
        return value

    def test_semester_initialization_is_strict_and_course_identity_is_consistent(self):
        semester = load_semester(self.sw)
        self.assertEqual(semester["schema_version"], core.SEMESTER_SCHEMA)
        self.assertEqual(semester["course_ids"], ["cs3100"])
        course_core = load_course_core(self.ws)
        self.assertEqual(course_core["capability_tags"], ["exam-mastery", "prerequisite-repair"])
        self.assertEqual(load_materials(self.ws)["schema_version"], core.MATERIALS_V02_SCHEMA)
        with self.assertRaises(SchoolLearningError):
            register_course(self.sw, "cs3100", "Different title")
        malformed = json.loads(self.semester_state_path().read_text())
        malformed["unexpected"] = True
        self.semester_state_path().write_text(json.dumps(malformed), encoding="utf-8")
        with self.assertRaises(SchoolLearningError):
            render_semester(self.sw)

    def test_legacy_workspace_remains_readable_and_migration_is_neutral_and_non_lossy(self):
        legacy = initialize_course(
            self.root, "2026-fall", "legacy101", "Legacy", created_at="2026-08-26T10:00:00Z"
        )
        source = self.source("legacy.md", b"legacy bytes\n")
        material = add_material(
            legacy, source, "notes", "Notes", added_at="2026-08-26T10:01:00Z"
        )
        ensure_topic(legacy, "intro", "Intro", ["notes"])
        record_session(
            legacy,
            "intro",
            "partial",
            "review",
            "review",
            session_id="legacy-session",
            recorded_at="2026-08-26T10:02:00Z",
        )
        before_bytes = (legacy.course_dir / material["stored_path"]).read_bytes()
        before_topics = load_topics(legacy)
        before_sessions = iter_sessions(legacy)
        self.assertEqual(load_materials(legacy)["schema_version"], core.MATERIALS_SCHEMA)
        register_course(
            self.sw, "legacy101", "Legacy", recorded_at="2026-08-26T12:03:00Z"
        )
        migrated = load_materials(legacy)
        self.assertEqual(migrated["schema_version"], core.MATERIALS_V02_SCHEMA)
        self.assertEqual(migrated["materials"][0]["kind"], "unspecified")
        self.assertIsNone(migrated["materials"][0]["provenance"])
        self.assertEqual((legacy.course_dir / material["stored_path"]).read_bytes(), before_bytes)
        self.assertEqual(load_topics(legacy), before_topics)
        self.assertEqual(iter_sessions(legacy), before_sessions)

    def test_migration_failure_restores_exact_legacy_manifest(self):
        legacy = initialize_course(
            self.root, "2026-fall", "legacyfail", "Legacy Fail",
            created_at="2026-08-26T10:00:00Z",
        )
        add_material(
            legacy, self.source("legacyfail.txt", b"preserve me"), "notes", "Notes",
            added_at="2026-08-26T10:01:00Z",
        )
        before = (legacy.course_dir / "materials.json").read_bytes()
        real_write = core._atomic_write_json

        def fail_materials(ws, path, value):
            if path.name == "materials.json":
                raise SchoolLearningError("synthetic migration failure")
            return real_write(ws, path, value)

        with mock.patch.object(core, "_atomic_write_json", side_effect=fail_materials):
            with self.assertRaises(SchoolLearningError):
                register_course(
                    self.sw, "legacyfail", "Legacy Fail",
                    recorded_at="2026-08-26T12:03:00Z",
                )
        self.assertEqual((legacy.course_dir / "materials.json").read_bytes(), before)
        self.assertFalse((legacy.course_dir / "course-core.json").exists())
        self.assertNotIn("legacyfail", load_semester(self.sw)["course_ids"])

    def test_failed_new_registration_removes_partial_workspace_and_restores_semester(self):
        before = self.semester_state_path().read_bytes()
        real_write = core._atomic_term_json

        def fail_registration(sw, path, value):
            if "newfail" in value.get("course_ids", []):
                raise SchoolLearningError("synthetic semester registration failure")
            return real_write(sw, path, value)

        with mock.patch.object(core, "_atomic_term_json", side_effect=fail_registration):
            with self.assertRaises(SchoolLearningError):
                register_course(
                    self.sw, "newfail", "New Fail",
                    recorded_at="2026-08-26T12:03:00Z",
                )
        self.assertFalse((self.sw.term_dir / "newfail").exists())
        self.assertEqual(self.semester_state_path().read_bytes(), before)

    def test_all_new_opaque_formats_preserve_hash_and_bytes(self):
        for index, suffix in enumerate((".pptx", ".rmd", ".png", ".jpg", ".jpeg", ".webp")):
            with self.subTest(suffix=suffix):
                content = b"opaque\x00" + suffix.encode("ascii")
                record = intake_material(
                    self.ws,
                    self.source(f"source-{index}{suffix}", content),
                    f"material-{index}",
                    f"Material {index}",
                    added_at="2026-08-26T12:04:00Z",
                )
                stored = self.ws.course_dir / record["stored_path"]
                self.assertEqual(stored.read_bytes(), content)
                self.assertEqual(core.sha256_file(stored), (record["sha256"], record["bytes"]))
        with self.assertRaises(SchoolLearningError):
            intake_material(
                self.ws, self.source("unsafe.docx"), "unsafe", "Unsafe",
                added_at="2026-08-26T12:04:00Z",
            )

    def test_intake_validates_metadata_without_mutating_learner_state(self):
        ensure_topic(self.ws, "graphs", "Graphs")
        topics_before = load_topics(self.ws)
        sessions_before = iter_sessions(self.ws)
        record = self.intake(topic_ids=["graphs"])
        self.assertEqual(record["kind"], "lecture")
        self.assertEqual(record["status"], "upcoming")
        self.assertEqual(record["relevant_date"], "2026-08-27")
        self.assertEqual(record["topic_ids"], ["graphs"])
        self.assertEqual(record["provenance"]["source"], "course site")
        self.assertEqual(load_topics(self.ws), topics_before)
        self.assertEqual(iter_sessions(self.ws), sessions_before)
        with self.assertRaises(SchoolLearningError):
            self.intake(material_id="bad-status", status="urgent")
        with self.assertRaises(SchoolLearningError):
            self.intake(material_id="bad-date", relevant_date="2026-02-30")
        with self.assertRaises(SchoolLearningError):
            self.intake(material_id="unknown-topic", topic_ids=["other-course-topic"])

    def test_invalid_material_metadata_and_references_leave_no_intake_artifacts(self):
        invalid_cases = (
            ("kind", {"kind": "invalid-kind"}),
            ("lifecycle", {"status": "invalid-lifecycle"}),
            ("date", {"relevant_date": "2026-02-30"}),
            (
                "provenance",
                {
                    "provenance": {
                        "source": "course site",
                        "observed_at": "invalid-date",
                        "status": "confirmed",
                    }
                },
            ),
            ("topic", {"topic_ids": ["unknown-topic"]}),
            ("assessment", {"assessment_ids": ["unknown-assessment"]}),
        )
        for label, metadata in invalid_cases:
            source = self.source(
                f"invalid-{label}.pptx",
                f"realistic synthetic {label} material bytes".encode("utf-8"),
            )
            before = complete_snapshot(self.ws.course_dir)
            with self.subTest(label=label), self.assertRaises(SchoolLearningError):
                add_material(
                    self.ws,
                    source,
                    f"invalid-{label}",
                    f"Invalid {label}",
                    added_at="2026-08-26T12:04:30Z",
                    **metadata,
                )
            self.assertEqual(complete_snapshot(self.ws.course_dir), before)
            self.assertEqual(list(self.ws.course_dir.rglob(".material.*")), [])

        successful_bytes = b"validated intake bytes\x00with exact identity"
        successful = add_material(
            self.ws,
            self.source("validated-success.pptx", successful_bytes),
            "validated-success",
            "Validated Success",
            kind="lecture",
            status="current",
            added_at="2026-08-26T12:04:31Z",
        )
        stored = self.ws.course_dir / successful["stored_path"]
        self.assertEqual(stored.read_bytes(), successful_bytes)
        self.assertEqual(
            (successful["sha256"], successful["bytes"]),
            (hashlib.sha256(successful_bytes).hexdigest(), len(successful_bytes)),
        )
        self.assertEqual(list(self.ws.course_dir.rglob(".material.*")), [])

    def test_invalid_metadata_replacement_preserves_material_and_manifest_exactly(self):
        original = self.intake(
            material_id="replacement-target", name="replacement-original.pptx"
        )
        manifest_path = self.ws.course_dir / "materials.json"
        stored_path = self.ws.course_dir / original["stored_path"]
        before = complete_snapshot(self.ws.course_dir)
        before_manifest = manifest_path.read_bytes()
        before_stored = stored_path.read_bytes()
        before_identity = (original["sha256"], original["bytes"])
        replacement = self.source(
            "replacement-invalid.pptx", b"rejected replacement bytes"
        )

        with self.assertRaises(SchoolLearningError):
            add_material(
                self.ws,
                replacement,
                original["id"],
                original["title"],
                status="invalid-lifecycle",
                replace=True,
                added_at="2026-08-26T12:04:32Z",
            )

        self.assertEqual(complete_snapshot(self.ws.course_dir), before)
        self.assertEqual(manifest_path.read_bytes(), before_manifest)
        self.assertEqual(stored_path.read_bytes(), before_stored)
        preserved = next(
            item
            for item in load_materials(self.ws)["materials"]
            if item["id"] == original["id"]
        )
        self.assertEqual((preserved["sha256"], preserved["bytes"]), before_identity)
        self.assertEqual(list(self.ws.course_dir.rglob(".material.*")), [])

    def test_assessments_validate_references_and_preserve_conflicting_schedule_claims(self):
        ensure_topic(self.ws, "graphs", "Graphs")
        material = self.intake(topic_ids=["graphs"])
        first = upsert_assessment(
            self.ws,
            "exam-1",
            "Exam 1",
            "exam",
            "upcoming",
            weight="20%",
            points="100",
            material_ids=[material["id"]],
            topic_ids=["graphs"],
            claim_field="due",
            claim_value="2026-09-10",
            claim_source="syllabus",
            claim_observed_at="2026-08-26",
            claim_status="confirmed",
            recorded_at="2026-08-26T12:05:00Z",
        )
        self.assertEqual(first["claims"][0]["status"], "confirmed")
        second = upsert_assessment(
            self.ws,
            "exam-1",
            "Exam 1",
            "exam",
            "upcoming",
            weight="20%",
            points="100",
            material_ids=[material["id"]],
            topic_ids=["graphs"],
            claim_field="due",
            claim_value="2026-09-12",
            claim_source="announcement",
            claim_observed_at="2026-08-27",
            claim_status="provisional",
            recorded_at="2026-08-27T12:05:00Z",
        )
        self.assertEqual({item["value"] for item in second["claims"]}, {"2026-09-10", "2026-09-12"})
        self.assertEqual({item["status"] for item in second["claims"]}, {"conflicted"})
        with self.assertRaises(SchoolLearningError):
            upsert_assessment(
                self.ws, "bad", "Bad", "quiz", "upcoming",
                material_ids=["material-from-another-course"],
            )
        with self.assertRaises(SchoolLearningError):
            upsert_assessment(self.ws, "bad", "Bad", "unsafe/type", "upcoming")

    def test_policies_preserve_conflicts_without_a_silent_winner(self):
        first = upsert_policy(
            self.ws,
            "ai-use",
            "AI Use",
            "ai",
            "AI allowed for brainstorming",
            "syllabus",
            status="confirmed",
            observed_at="2026-08-26",
            recorded_at="2026-08-26T12:06:00Z",
        )
        self.assertEqual(first["status"], "confirmed")
        second = upsert_policy(
            self.ws,
            "ai-use",
            "AI Use",
            "ai",
            "AI prohibited for all work",
            "assignment specification",
            observed_at="2026-08-27",
            recorded_at="2026-08-27T12:06:00Z",
        )
        self.assertEqual(second["status"], "conflicted")
        self.assertEqual(len(second["claims"]), 2)
        self.assertEqual({item["status"] for item in second["claims"]}, {"conflicted"})
        malformed = json.loads((self.ws.course_dir / "course-core.json").read_text())
        malformed["policies"][0]["claims"][0]["source"] = ""
        (self.ws.course_dir / "course-core.json").write_text(json.dumps(malformed), encoding="utf-8")
        before = {
            path.relative_to(self.ws.course_dir).as_posix(): path.read_bytes()
            for path in self.ws.course_dir.rglob("*")
            if path.is_file()
        }
        with self.assertRaises(SchoolLearningError):
            render_course(self.ws)
        with self.assertRaises(SchoolLearningError):
            intake_material(
                self.ws, self.source("rejected.png"), "rejected", "Rejected",
                added_at="2026-08-27T12:07:00Z",
            )
        self.assertEqual(
            {
                path.relative_to(self.ws.course_dir).as_posix(): path.read_bytes()
                for path in self.ws.course_dir.rglob("*")
                if path.is_file()
            },
            before,
        )

    def test_claim_sets_recompute_on_reconfirmation_supersession_and_resolution(self):
        first = upsert_assessment(
            self.ws,
            "exam-conflict",
            "Conflict Exam",
            "exam",
            "upcoming",
            claim_field="due",
            claim_value="2026-09-10",
            claim_source="syllabus",
            claim_observed_at="2026-08-26",
            claim_status="confirmed",
            recorded_at="2026-08-26T14:00:00Z",
        )
        self.assertEqual(first["claims"][0]["status"], "confirmed")
        conflicted = upsert_assessment(
            self.ws,
            "exam-conflict",
            "Conflict Exam",
            claim_field="due",
            claim_value="2026-09-12",
            claim_source="announcement",
            claim_observed_at="2026-08-27",
            claim_status="provisional",
            recorded_at="2026-08-27T14:00:00Z",
        )
        self.assertEqual({item["status"] for item in conflicted["claims"]}, {"conflicted"})
        reconfirmed = upsert_assessment(
            self.ws,
            "exam-conflict",
            "Conflict Exam",
            claim_field="due",
            claim_value="2026-09-10",
            claim_source="syllabus",
            claim_observed_at="2026-08-26",
            claim_status="confirmed",
            recorded_at="2026-08-27T14:01:00Z",
        )
        self.assertEqual({item["status"] for item in reconfirmed["claims"]}, {"conflicted"})
        superseded = upsert_assessment(
            self.ws,
            "exam-conflict",
            "Conflict Exam",
            claim_field="due",
            claim_value="2026-09-12",
            claim_source="announcement",
            claim_observed_at="2026-08-27",
            claim_status="superseded",
            recorded_at="2026-08-27T14:02:00Z",
        )
        by_value = {item["value"]: item["status"] for item in superseded["claims"]}
        self.assertEqual(by_value, {"2026-09-10": "provisional", "2026-09-12": "superseded"})
        resolved = upsert_assessment(
            self.ws,
            "exam-conflict",
            "Conflict Exam",
            claim_field="due",
            claim_value="2026-09-10",
            claim_source="syllabus",
            claim_observed_at="2026-08-26",
            claim_status="confirmed",
            recorded_at="2026-08-27T14:03:00Z",
        )
        self.assertEqual(
            {item["value"]: item["status"] for item in resolved["claims"]},
            {"2026-09-10": "confirmed", "2026-09-12": "superseded"},
        )
        self.assertEqual(load_course_core(self.ws)["assessments"][0], resolved)

    def test_malformed_confirmed_conflict_is_rejected_on_reload_before_mutation(self):
        upsert_assessment(
            self.ws,
            "malformed-conflict",
            "Malformed Conflict",
            "exam",
            "upcoming",
            claim_field="due",
            claim_value="2026-09-10",
            claim_source="syllabus",
            claim_observed_at="2026-08-26",
            recorded_at="2026-08-26T14:04:00Z",
        )
        upsert_assessment(
            self.ws,
            "malformed-conflict",
            "Malformed Conflict",
            claim_field="due",
            claim_value="2026-09-12",
            claim_source="announcement",
            claim_observed_at="2026-08-27",
            recorded_at="2026-08-27T14:04:00Z",
        )
        path = self.ws.course_dir / "course-core.json"
        malformed = json.loads(path.read_text())
        for claim in malformed["assessments"][0]["claims"]:
            claim["status"] = "confirmed"
        path.write_text(json.dumps(malformed), encoding="utf-8")
        before = complete_snapshot(self.ws.course_dir)
        with self.assertRaises(SchoolLearningError):
            load_course_core(self.ws)
        with self.assertRaises(SchoolLearningError):
            render_course(self.ws)
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)

    def test_equal_value_claims_and_policy_aggregate_status_are_coherent(self):
        first = upsert_policy(
            self.ws,
            "attendance-equal",
            "Attendance",
            "attendance",
            "Attend every lab",
            "syllabus",
            status="confirmed",
            observed_at="2026-08-26",
            recorded_at="2026-08-26T14:05:00Z",
        )
        second = upsert_policy(
            self.ws,
            "attendance-equal",
            "Attendance",
            "attendance",
            "Attend every lab",
            "course site",
            status="provisional",
            observed_at="2026-08-27",
            recorded_at="2026-08-27T14:05:00Z",
        )
        self.assertEqual(first["status"], "confirmed")
        self.assertEqual(second["status"], "confirmed")
        self.assertEqual(
            {item["status"] for item in second["claims"]}, {"confirmed", "provisional"}
        )
        self.assertEqual(load_course_core(self.ws)["policies"][0], second)
        path = self.ws.course_dir / "course-core.json"
        malformed = json.loads(path.read_text())
        malformed["policies"][0]["status"] = "provisional"
        path.write_text(json.dumps(malformed), encoding="utf-8")
        with self.assertRaises(SchoolLearningError):
            load_course_core(self.ws)

    def test_assessment_partial_updates_preserve_metadata_and_support_explicit_clear(self):
        ensure_topic(self.ws, "graphs", "Graphs")
        material = self.intake(topic_ids=["graphs"])
        original = upsert_assessment(
            self.ws,
            "presentation-1",
            "Presentation 1",
            "presentation",
            "upcoming",
            weight="20%",
            points="100",
            xp="500",
            material_ids=[material["id"]],
            topic_ids=["graphs"],
            claim_field="due",
            claim_value="2026-09-10",
            claim_source="syllabus",
            claim_observed_at="2026-08-26",
            recorded_at="2026-08-26T14:06:00Z",
        )
        claim_update = upsert_assessment(
            self.ws,
            "presentation-1",
            "Presentation 1",
            claim_field="room",
            claim_value="Studio A",
            claim_source="course site",
            claim_observed_at="2026-08-27",
            recorded_at="2026-08-27T14:06:00Z",
        )
        for field in ("type", "status", "weight", "points", "xp", "material_ids", "topic_ids"):
            self.assertEqual(claim_update[field], original[field])
        with redirect_stdout(io.StringIO()):
            self.assertEqual(
                cli_main(
                    [
                        "--data-root", str(self.root), "assessment", "2026-fall", "cs3100",
                        "presentation-1", "Presentation 1", "--weight", "25%",
                    ]
                ),
                0,
            )
        one_field = next(
            item
            for item in load_course_core(self.ws)["assessments"]
            if item["id"] == "presentation-1"
        )
        self.assertEqual(one_field["weight"], "25%")
        for field in ("type", "status", "points", "xp", "material_ids", "topic_ids", "claims"):
            self.assertEqual(one_field[field], claim_update[field])
        cleared = upsert_assessment(
            self.ws,
            "presentation-1",
            "Presentation 1",
            points=None,
            material_ids=[],
            topic_ids=[],
            recorded_at="2026-08-27T14:08:00Z",
        )
        self.assertIsNone(cleared["points"])
        self.assertEqual(cleared["material_ids"], [])
        self.assertEqual(cleared["topic_ids"], [])
        self.assertEqual(cleared["weight"], "25%")
        self.assertEqual(cleared["xp"], "500")

    def test_material_byte_replacement_preserves_metadata_and_updates_only_supplied_fields(self):
        ensure_topic(self.ws, "graphs", "Graphs")
        first = self.intake(topic_ids=["graphs"])
        upsert_assessment(
            self.ws,
            "exam-material",
            "Material Exam",
            "exam",
            "upcoming",
            material_ids=[first["id"]],
            topic_ids=["graphs"],
            recorded_at="2026-08-26T14:09:00Z",
        )
        linked = intake_material(
            self.ws,
            self.root / "lecture.pptx",
            first["id"],
            "Lecture <2>",
            topic_ids=["graphs"],
            assessment_ids=["exam-material"],
            replace=True,
            added_at="2026-08-26T14:10:00Z",
        )
        preserved_fields = (
            "kind", "status", "relevant_date", "topic_ids", "assessment_ids", "provenance"
        )
        replacement_source = self.source("replacement.pptx", b"replacement bytes")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(
                cli_main(
                    [
                        "--data-root", str(self.root), "intake", "2026-fall", "cs3100",
                        first["id"], "Lecture <2>", str(replacement_source), "--replace",
                    ]
                ),
                0,
            )
        replaced = next(
            item for item in load_materials(self.ws)["materials"] if item["id"] == first["id"]
        )
        for field in preserved_fields:
            self.assertEqual(replaced[field], linked[field])
        self.assertEqual((self.ws.course_dir / replaced["stored_path"]).read_bytes(), b"replacement bytes")
        kind_only = intake_material(
            self.ws,
            replacement_source,
            first["id"],
            "Lecture <2>",
            kind="reading",
            replace=True,
            added_at="2026-08-26T14:12:00Z",
        )
        self.assertEqual(kind_only["kind"], "reading")
        for field in ("status", "relevant_date", "topic_ids", "assessment_ids", "provenance"):
            self.assertEqual(kind_only[field], replaced[field])
        cleared = intake_material(
            self.ws,
            replacement_source,
            first["id"],
            "Lecture <2>",
            relevant_date=None,
            topic_ids=[],
            assessment_ids=[],
            source_descriptor=None,
            replace=True,
            added_at="2026-08-26T14:13:00Z",
        )
        self.assertIsNone(cleared["relevant_date"])
        self.assertEqual(cleared["topic_ids"], [])
        self.assertEqual(cleared["assessment_ids"], [])
        self.assertIsNone(cleared["provenance"])
        self.assertEqual(cleared["kind"], "reading")
        self.assertEqual(cleared["status"], "upcoming")

    def test_legacy_add_material_behavior_remains_v01_compatible(self):
        legacy = initialize_course(
            self.root, "2026-fall", "legacy-add", "Legacy Add",
            created_at="2026-08-26T14:14:00Z",
        )
        source = self.source("legacy-add.txt", b"legacy add bytes")
        first = add_material(
            legacy, source, "notes", "Notes", added_at="2026-08-26T14:14:30Z"
        )
        second = add_material(
            legacy, source, "notes", "Notes", replace=True,
            added_at="2026-08-26T14:15:00Z",
        )
        self.assertEqual(load_materials(legacy)["schema_version"], core.MATERIALS_SCHEMA)
        self.assertFalse(second["changed"])
        self.assertEqual(first["sha256"], second["sha256"])

    def test_custom_assessment_type_survives_api_cli_render_and_handoff(self):
        value = upsert_assessment(
            self.ws,
            "presentation-final",
            "Final Presentation",
            "Presentation",
            "upcoming",
            recorded_at="2026-08-26T14:16:00Z",
        )
        self.assertEqual(value["type"], "presentation")
        self.assertEqual(load_course_core(self.ws)["assessments"][0]["type"], "presentation")
        html_path, _ = render_course(self.ws)
        self.assertIn("presentation", html_path.read_text())
        handoff = prepare_course_handoff(self.ws)
        self.assertIn('"type": "presentation"', handoff["context"].read_text())
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(
                cli_main(
                    [
                        "--data-root", str(self.root), "assessment", "2026-fall", "cs3100",
                        "presentation-cli", "CLI Presentation", "--type", "presentation",
                        "--status", "upcoming",
                    ]
                ),
                0,
            )
        self.assertIn('"type": "presentation"', output.getvalue())
        for invalid in ("", "unsafe/type", "a" * 65, "-presentation"):
            with self.subTest(invalid=invalid), self.assertRaises(SchoolLearningError):
                upsert_assessment(
                    self.ws, f"invalid-{len(invalid)}", "Invalid", invalid, "upcoming"
                )

    def test_course_core_atomic_failure_restores_exact_state(self):
        before = (self.ws.course_dir / "course-core.json").read_bytes()
        real_replace = core._safe_replace
        failed = False

        def fail_once(ws, source, destination, label):
            nonlocal failed
            if destination.name == "course-core.json" and not failed:
                failed = True
                raise SchoolLearningError("synthetic atomic replace failure")
            return real_replace(ws, source, destination, label)

        with mock.patch.object(core, "_safe_replace", side_effect=fail_once):
            with self.assertRaises(SchoolLearningError):
                upsert_policy(
                    self.ws,
                    "atomic",
                    "Atomic",
                    "other",
                    "Rule",
                    "source",
                    observed_at="2026-08-26",
                    recorded_at="2026-08-26T12:07:00Z",
                )
        self.assertEqual((self.ws.course_dir / "course-core.json").read_bytes(), before)
        self.assertEqual(
            list((self.ws.course_dir).glob(".course-core.json.*")), []
        )

    def test_source_observations_are_optional_append_only_and_fail_closed(self):
        observations_path = self.ws.course_dir / "source-observations.json"
        self.assertFalse(observations_path.exists())
        self.assertEqual(
            load_source_observations(self.ws),
            {"schema_version": core.SOURCE_OBSERVATIONS_SCHEMA, "observations": []},
        )
        material = self.intake()
        learner_before = (self.ws.course_dir / "topics.json").read_bytes()
        observation = append_source_observation(
            self.ws,
            "syllabus",
            "partial",
            "changed",
            material_ids=[material["id"]],
            note="Assessment details changed.",
            observed_at="2026-08-29",
            observation_id="syllabus-2026-08-29",
        )
        self.assertEqual(observation["source_id"], "syllabus")
        self.assertEqual((self.ws.course_dir / "topics.json").read_bytes(), learner_before)
        self.assertEqual(load_source_observations(self.ws)["observations"], [observation])

        invalid = (
            ("unknown source", {"source_id": "canvas"}),
            ("unknown material", {"material_ids": ["outside-course"]}),
            ("scope", {"scope": "complete"}),
            ("outcome", {"outcome": "fresh"}),
            ("date", {"observed_at": "Aug 29"}),
            ("duplicate", {"observation_id": observation["id"]}),
        )
        for label, changes in invalid:
            values = {
                "source_id": "syllabus",
                "scope": "full",
                "outcome": "no-relevant-change",
                "material_ids": [],
                "observed_at": "2026-08-30",
                "observation_id": f"invalid-{label.replace(' ', '-')}",
            }
            values.update(changes)
            before = complete_snapshot(self.ws.course_dir)
            with self.subTest(label=label), self.assertRaises(SchoolLearningError):
                append_source_observation(self.ws, **values)
            self.assertEqual(complete_snapshot(self.ws.course_dir), before)

        malformed = json.loads(observations_path.read_text())
        malformed["unexpected"] = "closed"
        observations_path.write_text(json.dumps(malformed), encoding="utf-8")
        before_malformed = complete_snapshot(self.ws.course_dir)
        with self.assertRaises(SchoolLearningError):
            upsert_source(
                self.ws,
                "announcement",
                "Announcements",
                "local announcements",
                recorded_at="2026-08-30T12:00:00Z",
            )
        self.assertEqual(complete_snapshot(self.ws.course_dir), before_malformed)

    def test_source_upsert_preserves_unrelated_profile_state_and_sorted_uniqueness(self):
        upsert_assessment(
            self.ws,
            "quiz-1",
            "Quiz 1",
            "quiz",
            "upcoming",
            recorded_at="2026-08-28T10:00:00Z",
        )
        before = load_course_core(self.ws)
        added = upsert_source(
            self.ws,
            "announcements",
            "Announcements",
            "local announcements",
            status="confirmed",
            recorded_at="2026-08-29T10:00:00Z",
        )
        after = load_course_core(self.ws)
        self.assertEqual(added["id"], "announcements")
        self.assertEqual([item["id"] for item in after["sources"]], ["announcements", "syllabus"])
        for field in ("capability_tags", "metadata", "assessments", "policies", "created_at"):
            self.assertEqual(after[field], before[field])
        updated = upsert_source(
            self.ws,
            "announcements",
            "Course Announcements",
            "local announcement archive",
            status="provisional",
            recorded_at="2026-08-30T10:00:00Z",
        )
        self.assertEqual(updated["title"], "Course Announcements")
        self.assertEqual(
            [item["id"] for item in load_course_core(self.ws)["sources"]],
            ["announcements", "syllabus"],
        )
        snapshot = complete_snapshot(self.ws.course_dir)
        with self.assertRaises(SchoolLearningError):
            upsert_source(self.ws, "bad/source", "Bad", "reference")
        self.assertEqual(complete_snapshot(self.ws.course_dir), snapshot)

    def test_reviewed_candidate_preview_is_exact_bounded_and_has_zero_mutation(self):
        material = self.intake()
        second_material = self.intake(
            material_id="lecture-03", name="lecture-03.pptx"
        )
        operation = self.assessment_operation(
            material_ids=[material["id"]],
            claims=[
                {
                    "field": "due-at",
                    "value": "2026-08-30T23:59:00-04:00",
                    "source": "syllabus",
                    "observed_at": "2026-08-29",
                    "status": "confirmed",
                },
                {
                    "field": "submission-format",
                    "value": "Submit in the format named by the assignment.",
                    "source": "assignment specification",
                    "observed_at": "2026-08-29",
                    "status": "provisional",
                },
            ],
        )
        candidate = self.candidate([operation])
        path = self.write_candidate(candidate)
        before = complete_snapshot(self.sw.term_dir)
        reviewed = review_update(self.root, path)
        self.assertEqual(complete_snapshot(self.sw.term_dir), before)
        self.assertEqual(reviewed["digest"], reviewed_update_digest(candidate))
        self.assertIn("Durable state diff", reviewed["preview"])
        self.assertIn("assessment-upsert ps-2", reviewed["preview"])
        compact = self.write_candidate(candidate, "candidate-compact.json")
        compact.write_text(json.dumps(candidate, separators=(",", ":")), encoding="utf-8")
        self.assertEqual(review_update(self.root, compact)["digest"], reviewed["digest"])

        invalid_candidates = []
        extra_root = json.loads(json.dumps(candidate))
        extra_root["path"] = "/tmp/arbitrary"
        invalid_candidates.append(("exact root", extra_root))
        unsupported = self.candidate([{"kind": "shell", "command": "touch /tmp/no"}])
        invalid_candidates.append(("unsupported operation", unsupported))
        arbitrary = json.loads(json.dumps(candidate))
        arbitrary["operations"][0]["output_path"] = "/tmp/no"
        invalid_candidates.append(("arbitrary operation key", arbitrary))
        invalid_date = json.loads(json.dumps(candidate))
        invalid_date["operations"][0]["claims"][0]["value"] = "next Sunday"
        invalid_candidates.append(("planner date", invalid_date))
        legacy_due = json.loads(json.dumps(candidate))
        legacy_due["operations"][0]["claims"][0]["field"] = "due"
        legacy_due["operations"][0]["claims"][0]["value"] = "2026-08-30"
        invalid_candidates.append(("legacy due field", legacy_due))
        missing_seconds = json.loads(json.dumps(candidate))
        missing_seconds["operations"][0]["claims"][0]["value"] = "2026-08-30T23:59Z"
        invalid_candidates.append(("planner timestamp without seconds", missing_seconds))
        observation = {
            "kind": "source-observation",
            "id": "reviewed-observation",
            "source_id": "syllabus",
            "observed_at": "2026-08-29",
            "scope": "full",
            "outcome": "changed",
            "material_ids": [second_material["id"], material["id"]],
            "note": "Synthetic reviewed observation.",
        }
        invalid_candidates.append(
            ("unsorted observation relationships", self.candidate([observation]))
        )
        duplicate_observation = json.loads(json.dumps(observation))
        duplicate_observation["material_ids"] = [material["id"], material["id"]]
        invalid_candidates.append(
            ("duplicate observation relationships", self.candidate([duplicate_observation]))
        )
        unknown_material = json.loads(json.dumps(candidate))
        unknown_material["operations"][0]["material_ids"] = ["another-course-material"]
        invalid_candidates.append(("unknown material", unknown_material))
        wrong_term = json.loads(json.dumps(candidate))
        wrong_term["term"] = "2027-spring"
        invalid_candidates.append(("wrong term", wrong_term))
        wrong_course = json.loads(json.dumps(candidate))
        wrong_course["course_id"] = "outside-course"
        invalid_candidates.append(("wrong course", wrong_course))
        for index, (label, invalid) in enumerate(invalid_candidates):
            invalid_path = self.write_candidate(invalid, f"invalid-candidate-{index}.json")
            durable_before = complete_snapshot(self.ws.course_dir)
            with self.subTest(label=label), self.assertRaises(SchoolLearningError):
                review_update(self.root, invalid_path)
            self.assertEqual(complete_snapshot(self.ws.course_dir), durable_before)

    def test_reviewed_source_observation_ids_are_novel_append_only_identities(self):
        append_source_observation(
            self.ws,
            "syllabus",
            "full",
            "no-relevant-change",
            observed_at="2026-08-29",
            observation_id="existing-observation",
        )
        existing_collision = self.write_candidate(
            self.candidate(
                [self.source_observation_operation(id="existing-observation")]
            ),
            "existing-observation-collision.json",
        )
        before = complete_snapshot(self.ws.course_dir)
        with self.assertRaises(SchoolLearningError):
            review_update(self.root, existing_collision)
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)

        duplicate_candidate_id = self.write_candidate(
            self.candidate(
                [
                    self.source_observation_operation(id="new-observation"),
                    self.source_observation_operation(
                        id="new-observation",
                        observed_at="2026-08-30",
                        note="Second operation reuses the identifier.",
                    ),
                ]
            ),
            "duplicate-candidate-observation.json",
        )
        with self.assertRaises(SchoolLearningError):
            review_update(self.root, duplicate_candidate_id)
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)

        valid = self.write_candidate(
            self.candidate(
                [
                    self.source_observation_operation(
                        id="new-observation-a",
                        observed_at="2026-08-30T00:00:00.1Z",
                    ),
                    self.source_observation_operation(
                        id="new-observation-b",
                        observed_at="2026-08-30T00:00:00.100001-04:00",
                    ),
                ]
            ),
            "novel-candidate-observations.json",
        )
        reviewed = review_update(self.root, valid)
        apply_update(self.root, valid, reviewed["digest"])
        self.assertEqual(
            {
                item["id"]
                for item in load_source_observations(self.ws)["observations"]
            },
            {
                "existing-observation",
                "new-observation-a",
                "new-observation-b",
            },
        )

    def test_reviewed_candidate_uses_canonical_school_timestamp_subset(self):
        accepted = [
            "2026-09-01T00:00:00Z",
            "2026-09-01T00:00:00.1Z",
            "2026-09-01T00:00:00.123Z",
            "2026-09-01T00:00:00.123456Z",
            "2026-09-01T00:00:00.123456-04:00",
        ]
        for index, value in enumerate(accepted):
            operation = self.assessment_operation(
                id=f"accepted-timestamp-{index}",
                claims=[
                    {
                        "field": "due-at",
                        "value": value,
                        "source": "synthetic accepted timestamp",
                        "observed_at": "2026-08-29",
                        "status": "confirmed",
                    }
                ],
            )
            path = self.write_candidate(
                self.candidate([operation]), f"accepted-timestamp-{index}.json"
            )
            with self.subTest(accepted=value):
                self.assertEqual(
                    review_update(self.root, path)["digest"],
                    reviewed_update_digest(self.candidate([operation])),
                )

        rejected = [
            "2026-09-01T00:00:00.1234567Z",
            "2026-09-01T00:00Z",
            "2026-09-01T00:00:00",
            "2026-09-01T00:00:00+24:00",
        ]
        for index, value in enumerate(rejected):
            operation = self.assessment_operation(
                id=f"rejected-timestamp-{index}",
                claims=[
                    {
                        "field": "due-at",
                        "value": value,
                        "source": "synthetic rejected timestamp",
                        "observed_at": "2026-08-29",
                        "status": "confirmed",
                    }
                ],
            )
            path = self.write_candidate(
                self.candidate([operation]), f"rejected-timestamp-{index}.json"
            )
            with self.subTest(rejected=value), self.assertRaises(SchoolLearningError):
                review_update(self.root, path)

        first = append_source_observation(
            self.ws,
            "syllabus",
            "full",
            "no-relevant-change",
            observed_at="2026-09-01T00:00:00.1Z",
            observation_id="fractional-source-observation",
        )
        second = append_source_observation(
            self.ws,
            "syllabus",
            "partial",
            "changed",
            observed_at="2026-09-01T00:00:00.123456-04:00",
            observation_id="offset-source-observation",
        )
        self.assertEqual(first["observed_at"], "2026-09-01T00:00:00.1Z")
        self.assertEqual(second["observed_at"], "2026-09-01T00:00:00.123456-04:00")
        before = complete_snapshot(self.ws.course_dir)
        with self.assertRaises(SchoolLearningError):
            append_source_observation(
                self.ws,
                "syllabus",
                "full",
                "changed",
                observed_at="2026-09-01T00:00:00.1234567Z",
                observation_id="over-precision-source-observation",
            )
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)

    def test_reviewed_update_applies_ordered_operations_and_preserves_conflicts(self):
        material = self.intake()
        upsert_assessment(
            self.ws,
            "ps-2",
            "Problem Set 2",
            "problem-set",
            "upcoming",
            material_ids=[material["id"]],
            claim_field="submission-format",
            claim_value="Submit one PDF.",
            claim_source="syllabus",
            claim_observed_at="2026-08-28",
            recorded_at="2026-08-28T12:00:00Z",
        )
        operations = [
            {
                "kind": "source-upsert",
                "id": "course-site",
                "title": "Course Site",
                "reference": "local reviewed course-site reference",
                "status": "confirmed",
                "recorded_at": "2026-08-29T12:00:00Z",
            },
            {
                "kind": "source-observation",
                "id": "course-site-check-001",
                "source_id": "course-site",
                "observed_at": "2026-08-29",
                "scope": "full",
                "outcome": "changed",
                "material_ids": [material["id"]],
                "note": "Reviewed synthetic course-site changes.",
            },
            self.assessment_operation(
                material_ids=[material["id"]],
                claims=[
                    {
                        "field": "due-at",
                        "value": "2026-08-30",
                        "source": "course-site",
                        "observed_at": "2026-08-29",
                        "status": "confirmed",
                    },
                    {
                        "field": "submission-format",
                        "value": "Submit separate files.",
                        "source": "assignment specification",
                        "observed_at": "2026-08-29",
                        "status": "provisional",
                    },
                ],
            ),
            {
                "kind": "policy-upsert",
                "id": "collaboration",
                "title": "Collaboration",
                "category": "collaboration",
                "claims": [
                    {
                        "field": "rule",
                        "value": "Discuss concepts but submit individual work.",
                        "source": "syllabus",
                        "observed_at": "2026-08-29",
                        "status": "confirmed",
                    }
                ],
                "recorded_at": "2026-08-29T12:00:00Z",
            },
        ]
        candidate = self.candidate(operations)
        path = self.write_candidate(candidate)
        reviewed = review_update(self.root, path)
        before = complete_snapshot(self.ws.course_dir)
        with self.assertRaises(SchoolLearningError):
            apply_update(self.root, path, "0" * 64)
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)
        topics_before = (self.ws.course_dir / "topics.json").read_bytes()
        materials_before = (self.ws.course_dir / "materials.json").read_bytes()
        applied = apply_update(self.root, path, reviewed["digest"])
        self.assertEqual(
            applied["changed_files"], ["course-core.json", "source-observations.json"]
        )
        self.assertEqual((self.ws.course_dir / "topics.json").read_bytes(), topics_before)
        self.assertEqual((self.ws.course_dir / "materials.json").read_bytes(), materials_before)
        applied_core = load_course_core(self.ws)
        self.assertIn("course-site", {item["id"] for item in applied_core["sources"]})
        assessment = next(item for item in applied_core["assessments"] if item["id"] == "ps-2")
        format_claims = [item for item in assessment["claims"] if item["field"] == "submission-format"]
        self.assertEqual({item["status"] for item in format_claims}, {"conflicted"})
        self.assertEqual({item["value"] for item in format_claims}, {"Submit one PDF.", "Submit separate files."})
        self.assertEqual(load_source_observations(self.ws)["observations"][0]["source_id"], "course-site")
        self.assertEqual(applied_core["policies"][0]["status"], "confirmed")

    def test_reviewed_update_rechecks_candidate_digest_and_base_context(self):
        candidate = self.candidate([self.assessment_operation()])
        path = self.write_candidate(candidate)
        first = review_update(self.root, path)
        changed = json.loads(json.dumps(candidate))
        changed["operations"][0]["title"] = "Changed After Preview"
        self.write_candidate(changed)
        before = complete_snapshot(self.ws.course_dir)
        with self.assertRaises(SchoolLearningError):
            apply_update(self.root, path, first["digest"])
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)
        second = review_update(self.root, path)
        self.assertNotEqual(second["digest"], first["digest"])

        upsert_source(
            self.ws,
            "announcements",
            "Announcements",
            "local announcements",
            recorded_at="2026-08-30T14:00:00Z",
        )
        stale_before = complete_snapshot(self.ws.course_dir)
        with self.assertRaises(SchoolLearningError):
            apply_update(self.root, path, second["digest"])
        self.assertEqual(complete_snapshot(self.ws.course_dir), stale_before)

        mismatched = json.loads(json.dumps(changed))
        mismatched["base_context_sha256"] = "f" * 64
        mismatch_path = self.write_candidate(mismatched, "mismatched-base.json")
        with self.assertRaises(SchoolLearningError):
            review_update(self.root, mismatch_path)

    def test_reviewed_update_base_identity_covers_timestamp_only_core_changes(self):
        candidate = self.candidate([self.assessment_operation()])
        path = self.write_candidate(candidate, "timestamp-bound-update.json")
        identity = course_context_sha256(self.ws)
        self.assertEqual(course_context_sha256(self.ws), identity)
        reviewed = review_update(self.root, path)
        before_core = load_course_core(self.ws)

        upsert_source(
            self.ws,
            "syllabus",
            "Syllabus <official>",
            "local syllabus",
            status="confirmed",
            recorded_at="2026-08-30T14:00:00Z",
        )
        after_core = load_course_core(self.ws)
        self.assertEqual(after_core["sources"], before_core["sources"])
        self.assertEqual(after_core["created_at"], before_core["created_at"])
        self.assertNotEqual(after_core["updated_at"], before_core["updated_at"])
        self.assertNotEqual(course_context_sha256(self.ws), identity)

        stale_before = complete_snapshot(self.ws.course_dir)
        with self.assertRaises(SchoolLearningError):
            review_update(self.root, path)
        with self.assertRaises(SchoolLearningError):
            apply_update(self.root, path, reviewed["digest"])
        self.assertEqual(complete_snapshot(self.ws.course_dir), stale_before)

    def test_reviewed_update_failure_restores_exact_multi_file_prior_state(self):
        operations = [
            {
                "kind": "source-upsert",
                "id": "course-site",
                "title": "Course Site",
                "reference": "synthetic local reference",
                "status": "confirmed",
                "recorded_at": "2026-08-29T12:00:00Z",
            },
            {
                "kind": "source-observation",
                "id": "course-site-check-001",
                "source_id": "course-site",
                "observed_at": "2026-08-29",
                "scope": "full",
                "outcome": "changed",
                "material_ids": [],
                "note": "Synthetic check.",
            },
        ]
        path = self.write_candidate(self.candidate(operations))
        digest = review_update(self.root, path)["digest"]
        before = complete_snapshot(self.ws.course_dir)
        real_write = core._atomic_write_json

        def persist_observation_then_fail(ws, destination, value):
            real_write(ws, destination, value)
            if destination.name == "source-observations.json":
                raise SchoolLearningError("synthetic post-persistence observation failure")

        with mock.patch.object(core, "_atomic_write_json", side_effect=persist_observation_then_fail):
            with self.assertRaises(SchoolLearningError):
                apply_update(self.root, path, digest)
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)
        self.assertFalse((self.ws.course_dir / "source-observations.json").exists())

        append_source_observation(
            self.ws,
            "syllabus",
            "partial",
            "no-relevant-change",
            observed_at="2026-08-29",
            observation_id="existing-check",
        )
        observations_path = self.ws.course_dir / "source-observations.json"
        existing_value = json.loads(observations_path.read_text())
        observations_path.write_text(json.dumps(existing_value), encoding="utf-8")
        exact_existing = observations_path.read_bytes()
        existing_core = (self.ws.course_dir / "course-core.json").read_bytes()
        second_operations = [
            {
                "kind": "source-upsert",
                "id": "syllabus",
                "title": "Updated Syllabus",
                "reference": "same local syllabus",
                "status": "confirmed",
                "recorded_at": "2026-08-30T12:00:00Z",
            },
            {
                "kind": "source-observation",
                "id": "second-check",
                "source_id": "syllabus",
                "observed_at": "2026-08-30",
                "scope": "full",
                "outcome": "changed",
                "material_ids": [],
                "note": "Second synthetic check.",
            },
        ]
        second_path = self.write_candidate(self.candidate(second_operations), "second-update.json")
        second_digest = review_update(self.root, second_path)["digest"]
        with mock.patch.object(core, "_atomic_write_json", side_effect=persist_observation_then_fail):
            with self.assertRaises(SchoolLearningError):
                apply_update(self.root, second_path, second_digest)
        self.assertEqual(observations_path.read_bytes(), exact_existing)
        self.assertEqual((self.ws.course_dir / "course-core.json").read_bytes(), existing_core)

    def test_course_handoff_rejects_update_contract_tampering_and_preserves_prior_package(self):
        prior = prepare_course_handoff(self.ws)
        before = complete_snapshot(prior["root"])
        real_write = core._atomic_write_bytes

        def tamper_contract(ws, destination, content):
            if destination.name == "update-contract.json":
                value = json.loads(content)
                value["base_context_sha256"] = "0" * 64
                content = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
            return real_write(ws, destination, content)

        with mock.patch.object(core, "_atomic_write_bytes", side_effect=tamper_contract):
            with self.assertRaises(SchoolLearningError):
                prepare_course_handoff(self.ws)
        self.assertEqual(complete_snapshot(prior["root"]), before)

    def test_course_handoff_update_contract_has_complete_independent_constraint_matrix(self):
        handoff = prepare_course_handoff(self.ws)
        contract = json.loads(handoff["update_contract"].read_text(encoding="utf-8"))
        base_digest = hashlib.sha256(handoff["context"].read_bytes()).hexdigest()
        claim_statuses = ["confirmed", "provisional", "conflicted", "superseded"]
        assessment_statuses = [
            "upcoming",
            "available",
            "in-progress",
            "submitted",
            "graded",
            "reviewed",
        ]
        operation_kinds = [
            "assessment-upsert",
            "policy-upsert",
            "source-upsert",
            "source-observation",
        ]
        candidate_keys = [
            "base_context_sha256",
            "course_id",
            "operations",
            "schema_version",
            "term",
        ]
        claim_keys = ["field", "observed_at", "source", "status", "value"]
        operation_keys = {
            "assessment-upsert": [
                "claims",
                "id",
                "kind",
                "material_ids",
                "points",
                "recorded_at",
                "status",
                "title",
                "topic_ids",
                "type",
                "weight",
                "xp",
            ],
            "policy-upsert": [
                "category",
                "claims",
                "id",
                "kind",
                "recorded_at",
                "title",
            ],
            "source-upsert": [
                "id",
                "kind",
                "recorded_at",
                "reference",
                "status",
                "title",
            ],
            "source-observation": [
                "id",
                "kind",
                "material_ids",
                "note",
                "observed_at",
                "outcome",
                "scope",
                "source_id",
            ],
        }
        self.assertEqual(
            set(contract),
            {
                "allowed_operation_kinds",
                "base_context_sha256",
                "bounded_values",
                "candidate_keys",
                "claim_keys",
                "constraints",
                "course_id",
                "max_operations",
                "operation_keys",
                "reviewed_update_schema_version",
                "rules",
                "schema_version",
                "term",
            },
        )
        self.assertEqual(contract["schema_version"], "aiden.school.update-contract/v0.1")
        self.assertEqual(
            contract["reviewed_update_schema_version"],
            "aiden.school.reviewed-update/v0.1",
        )
        self.assertEqual(contract["term"], "2026-fall")
        self.assertEqual(contract["course_id"], "cs3100")
        self.assertEqual(contract["base_context_sha256"], base_digest)
        self.assertEqual(contract["allowed_operation_kinds"], operation_kinds)
        self.assertEqual(contract["candidate_keys"], candidate_keys)
        self.assertEqual(contract["operation_keys"], operation_keys)
        self.assertEqual(contract["claim_keys"], claim_keys)
        self.assertEqual(contract["max_operations"], 100)
        self.assertEqual(
            contract["bounded_values"],
            {
                "assessment_status": assessment_statuses,
                "claim_status": claim_statuses,
                "planner_critical_claim_field": [
                    "due-at",
                    "available-at",
                    "available-until",
                ],
                "source_observation_outcome": [
                    "changed",
                    "no-relevant-change",
                    "unavailable",
                ],
                "source_observation_scope": ["full", "partial"],
            },
        )
        self.assertEqual(
            contract["rules"],
            [
                "Return one JSON object only, as data; do not return commands or executable code.",
                "Use only the exact operation keys and bounded values declared by this contract.",
                "Assessment and policy operations require one or more sourced claims with exact claim keys.",
                "Identifier relationship lists must be sorted and unique; nullable grading measures use JSON null.",
                "Source-observation IDs are append-only identities: each must be absent from base source observations and all prior source-observation operations in this ordered candidate.",
                "Never use the legacy due field; use due-at for normalized forward scheduling.",
                "Use due-at, available-at, and available-until for planner-critical claims, with YYYY-MM-DD or the canonical School Learning timestamp subset: seconds, an explicit Z/numeric offset, and optional 1-through-6-digit fractional seconds.",
                "Do not include raw material bytes, intake requests, paths, arbitrary writes, or external actions.",
                "Do not include learner, topic, session, mastery, or cross-course updates.",
                "The returned JSON is only a reviewed candidate and does not change local state.",
            ],
        )

        identifier_list = {
            "items": {"ref": "identifier"},
            "sorted": True,
            "type": "array",
            "unique": True,
        }
        claim_list = {
            "items": {"ref": "claim"},
            "min_items": 1,
            "semantic_identity_fields": ["field", "value", "source", "observed_at"],
            "semantic_identity_unique": True,
            "type": "array",
        }
        expected_constraints = {
            "base_identity": {
                "algorithm": "sha256",
                "attachment": "course-context.md",
                "complete_semantic_sections": [
                    "course",
                    "course_core",
                    "materials",
                    "source_observations",
                    "topics",
                ],
                "digest_field": "base_context_sha256",
                "exact_attachment_bytes": True,
            },
            "candidate_file": {
                "encoding": "UTF-8",
                "max_bytes": 1_000_000,
                "top_level_type": "object",
            },
            "claim": {
                "exact_keys": claim_keys,
                "fields": {
                    "field": {
                        "forbidden_values": ["due"],
                        "planner_critical_values": [
                            "due-at",
                            "available-at",
                            "available-until",
                        ],
                        "ref": "identifier",
                    },
                    "observed_at": {"ref": "observed_at"},
                    "source": {"ref": "nonempty_string"},
                    "status": {"enum": claim_statuses, "type": "string"},
                    "value": {
                        "planner_critical_ref": "planner_value",
                        "ref": "nonempty_string",
                    },
                },
                "type": "object",
            },
            "definitions": {
                "date": {
                    "calendar_valid": True,
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                    "type": "string",
                },
                "identifier": {
                    "forbidden_values": [".", ".."],
                    "path_safe": True,
                    "pattern": r"^[a-z0-9][a-z0-9._-]*$",
                    "type": "string",
                },
                "identifier_list": identifier_list,
                "nonempty_string": {
                    "min_trimmed_length": 1,
                    "normalization": "strip",
                    "type": "string",
                },
                "nullable_measure": {
                    "allowed_types": ["null", "string"],
                    "string_min_trimmed_length": 1,
                    "string_normalization": "strip",
                },
                "observed_at": {
                    "calendar_valid": True,
                    "one_of_patterns": [
                        r"^\d{4}-\d{2}-\d{2}$",
                        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$",
                    ],
                    "timestamp_fractional_seconds": {
                        "max_digits": 6,
                        "min_digits_when_present": 1,
                        "optional": True,
                    },
                    "timestamp_seconds": "required",
                    "timestamp_subset": "canonical-school-learning",
                    "timestamp_timezone": "explicit-Z-or-numeric-offset",
                    "type": "string",
                },
                "plain_string": {"type": "string"},
                "planner_value": {
                    "calendar_valid": True,
                    "one_of_patterns": [
                        r"^\d{4}-\d{2}-\d{2}$",
                        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$",
                    ],
                    "timestamp_fractional_seconds": {
                        "max_digits": 6,
                        "min_digits_when_present": 1,
                        "optional": True,
                    },
                    "timestamp_seconds": "required",
                    "timestamp_subset": "canonical-school-learning",
                    "timestamp_timezone": "explicit-Z-or-numeric-offset",
                    "type": "string",
                },
                "sha256": {
                    "algorithm": "sha256",
                    "lowercase_hex": True,
                    "pattern": r"^[0-9a-f]{64}$",
                    "type": "string",
                },
                "utc_timestamp": {
                    "calendar_valid": True,
                    "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
                    "seconds": "required",
                    "timezone": "Z",
                    "type": "string",
                },
            },
            "operations": {
                "assessment-upsert": {
                    "exact_keys": operation_keys["assessment-upsert"],
                    "fields": {
                        "claims": claim_list,
                        "id": {"ref": "identifier"},
                        "kind": {"const": "assessment-upsert", "type": "string"},
                        "material_ids": {
                            "must_resolve": "current-course-materials",
                            "ref": "identifier_list",
                        },
                        "points": {"ref": "nullable_measure"},
                        "recorded_at": {"ref": "utc_timestamp"},
                        "status": {"enum": assessment_statuses, "type": "string"},
                        "title": {"ref": "nonempty_string"},
                        "topic_ids": {
                            "must_resolve": "current-course-topics",
                            "ref": "identifier_list",
                        },
                        "type": {
                            "already_normalized": True,
                            "max_length": 64,
                            "pattern": r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
                            "type": "string",
                        },
                        "weight": {"ref": "nullable_measure"},
                        "xp": {"ref": "nullable_measure"},
                    },
                    "type": "object",
                },
                "policy-upsert": {
                    "exact_keys": operation_keys["policy-upsert"],
                    "fields": {
                        "category": {"ref": "identifier"},
                        "claims": {**claim_list, "item_field_const": "rule"},
                        "id": {"ref": "identifier"},
                        "kind": {"const": "policy-upsert", "type": "string"},
                        "recorded_at": {"ref": "utc_timestamp"},
                        "title": {"ref": "nonempty_string"},
                    },
                    "type": "object",
                },
                "source-observation": {
                    "exact_keys": operation_keys["source-observation"],
                    "fields": {
                        "id": {
                            "append_only_identity": True,
                            "novelty": {
                                "existing_state_unique_against": (
                                    "source_observations[*].id"
                                ),
                                "ordered_candidate_unique_against": (
                                    "prior source-observation operations[*].id"
                                ),
                            },
                            "overwrite_existing": False,
                            "ref": "identifier",
                            "reuse_existing": False,
                        },
                        "kind": {"const": "source-observation", "type": "string"},
                        "material_ids": {
                            "must_resolve": "current-course-materials",
                            "ref": "identifier_list",
                        },
                        "note": {"ref": "plain_string"},
                        "observed_at": {"ref": "observed_at"},
                        "outcome": {
                            "enum": ["changed", "no-relevant-change", "unavailable"],
                            "type": "string",
                        },
                        "scope": {"enum": ["full", "partial"], "type": "string"},
                        "source_id": {
                            "must_resolve": "current-or-prior-operation-course-sources",
                            "ref": "identifier",
                        },
                    },
                    "type": "object",
                },
                "source-upsert": {
                    "exact_keys": operation_keys["source-upsert"],
                    "fields": {
                        "id": {"ref": "identifier"},
                        "kind": {"const": "source-upsert", "type": "string"},
                        "recorded_at": {"ref": "utc_timestamp"},
                        "reference": {"ref": "nonempty_string"},
                        "status": {"enum": claim_statuses, "type": "string"},
                        "title": {"ref": "nonempty_string"},
                    },
                    "type": "object",
                },
            },
            "root": {
                "exact_keys": candidate_keys,
                "fields": {
                    "base_context_sha256": {
                        "const": base_digest,
                        "ref": "sha256",
                    },
                    "course_id": {"const": "cs3100", "ref": "identifier"},
                    "operations": {
                        "discriminator": "kind",
                        "kinds": operation_kinds,
                        "max_items": 100,
                        "min_items": 1,
                        "ordered": True,
                        "type": "array",
                    },
                    "schema_version": {
                        "const": "aiden.school.reviewed-update/v0.1",
                        "type": "string",
                    },
                    "term": {"const": "2026-fall", "ref": "identifier"},
                },
                "registered_course_required": True,
                "type": "object",
            },
        }
        self.assertEqual(contract["constraints"], expected_constraints)

    def test_semester_plan_replays_weekend_work_conflicts_and_source_coverage(self):
        plan_root = self.root / "planning-root"
        sw = initialize_semester(
            plan_root, "2026-fall", "Fall 2026", created_at="2026-08-29T10:00:00Z"
        )

        def course(course_id, title):
            return register_course(
                sw,
                course_id,
                title,
                sources=[
                    {
                        "id": "course-site",
                        "title": "Course Site",
                        "reference": f"local {course_id} course-site reference",
                        "status": "confirmed",
                    }
                ],
                recorded_at="2026-08-29T10:01:00Z",
            )

        apma = course("apma", "Applied Mathematics")
        eco = course("eco", "Ecology")
        cs3240 = course("cs3240", "Advanced Software Development")
        dsa = course("dsa", "Data Structures and Algorithms")
        register_course(
            sw,
            "no-sources",
            "Course Without Source Descriptors",
            recorded_at="2026-08-29T10:01:30Z",
        )
        upsert_source(
            eco,
            "announcements",
            "Announcements",
            "local Eco announcements",
            recorded_at="2026-08-29T10:02:00Z",
        )

        upsert_assessment(
            apma,
            "ps-2",
            "APMA Problem Set 2",
            "problem-set",
            "in-progress",
            claim_field="due-at",
            claim_value="2026-08-30",
            claim_source="course-site",
            claim_observed_at="2026-08-29",
            claim_status="confirmed",
            recorded_at="2026-08-29T11:00:00Z",
        )
        for index, value in enumerate(("Submit one PDF.", "Submit separate files."), start=1):
            upsert_assessment(
                apma,
                "ps-2",
                "APMA Problem Set 2",
                claim_field="submission-format",
                claim_value=value,
                claim_source=f"apma-source-{index}",
                claim_observed_at=f"2026-08-{28 + index}",
                recorded_at=f"2026-08-{28 + index}T11:01:00Z",
            )
        upsert_assessment(
            apma,
            "legacy-due",
            "APMA Legacy Timestamp Check",
            "homework",
            "upcoming",
            claim_field="due",
            claim_value="Aug 30, 2026, 11:59 PM",
            claim_source="legacy course record",
            claim_observed_at="2026-08-29",
            recorded_at="2026-08-29T11:02:00Z",
        )
        upsert_assessment(
            apma,
            "submitted",
            "Already Submitted Work",
            "homework",
            "submitted",
            claim_field="due-at",
            claim_value="2026-08-30",
            claim_source="course-site",
            claim_observed_at="2026-08-29",
            recorded_at="2026-08-29T11:03:00Z",
        )
        upsert_assessment(
            apma,
            "unstructured",
            "Unsupported Scheduling Value",
            "homework",
            "upcoming",
            claim_field="due",
            claim_value="sometime next week",
            claim_source="synthetic prose",
            claim_observed_at="2026-08-29",
            recorded_at="2026-08-29T11:04:00Z",
        )
        upsert_assessment(
            apma,
            "conflicted-date",
            "Conflicted Date",
            "homework",
            "upcoming",
            claim_field="due-at",
            claim_value="2026-08-31",
            claim_source="syllabus",
            claim_observed_at="2026-08-29",
            recorded_at="2026-08-29T11:05:00Z",
        )
        upsert_assessment(
            apma,
            "conflicted-date",
            "Conflicted Date",
            claim_field="due-at",
            claim_value="2026-09-01",
            claim_source="announcement",
            claim_observed_at="2026-08-30",
            recorded_at="2026-08-30T11:05:00Z",
        )

        upsert_assessment(
            cs3240,
            "django-next",
            "Django Implementation Work",
            "sprint",
            "in-progress",
            claim_field="due-at",
            claim_value="2026-09-01",
            claim_source="course-site",
            claim_observed_at="2026-08-29",
            recorded_at="2026-08-29T12:00:00Z",
        )
        for index, value in enumerate(("Sprint 1", "Sprint A"), start=1):
            upsert_assessment(
                cs3240,
                "django-next",
                "Django Implementation Work",
                claim_field="sprint-label",
                claim_value=value,
                claim_source=f"cs-source-{index}",
                claim_observed_at=f"2026-08-{28 + index}",
                recorded_at=f"2026-08-{28 + index}T12:01:00Z",
            )
        for field, value, recorded_at in (
            ("available-at", "2026-08-31", "2026-08-30T12:02:00Z"),
            ("available-until", "2026-09-02T23:59:00-04:00", "2026-08-30T12:03:00Z"),
        ):
            upsert_assessment(
                cs3240,
                "django-next",
                "Django Implementation Work",
                claim_field=field,
                claim_value=value,
                claim_source="course-site",
                claim_observed_at="2026-08-30",
                recorded_at=recorded_at,
            )
        upsert_assessment(
            dsa,
            "ps-0",
            "DSA Problem Set 0",
            "problem-set",
            "upcoming",
            claim_field="due",
            claim_value="Sep 8, 2026, 11:59pm",
            claim_source="legacy course record",
            claim_observed_at="2026-08-29",
            recorded_at="2026-08-29T13:00:00Z",
        )

        for filename, content in (
            ("truax.pdf", b"%PDF Truax reading"),
            ("island.txt", b"Island listening reference"),
            ("eco-snapshot.md", b"# Syllabus snapshot"),
        ):
            (plan_root / filename).write_bytes(content)
        intake_material(
            eco,
            plan_root / "truax.pdf",
            "truax-reading",
            "Eco Truax Reading",
            kind="reading",
            status="upcoming",
            relevant_date="2026-09-01",
            added_at="2026-08-29T14:00:00Z",
        )
        intake_material(
            eco,
            plan_root / "island.txt",
            "island-listening",
            "Eco Island Listening",
            kind="listening-reference",
            status="upcoming",
            relevant_date="2026-09-01",
            added_at="2026-08-29T14:01:00Z",
        )
        intake_material(
            eco,
            plan_root / "eco-snapshot.md",
            "syllabus-snapshot",
            "Eco Syllabus Snapshot",
            kind="syllabus",
            status="reference",
            relevant_date="2026-09-01",
            added_at="2026-08-29T14:02:00Z",
        )

        for ws, outcome, scope in (
            (apma, "changed", "full"),
            (eco, "no-relevant-change", "full"),
            (cs3240, "unavailable", "partial"),
            (dsa, "no-relevant-change", "partial"),
        ):
            append_source_observation(
                ws,
                "course-site",
                scope,
                outcome,
                observed_at="2026-08-30",
                observation_id=f"{ws.course_id}-coverage",
            )

        destination = render_plan(sw, "2026-08-30")
        first = destination.read_bytes()
        self.assertEqual(render_plan(sw, "2026-08-30").read_bytes(), first)
        text = first.decode()
        self.assertIn("DUE TODAY 2026-08-30 — `apma` / `ps-2`", text)
        self.assertIn("Eco Truax Reading", text)
        self.assertIn("Eco Island Listening", text)
        self.assertNotIn("Eco Syllabus Snapshot", text)
        self.assertIn("Django Implementation Work", text)
        self.assertIn("AVAILABLE 2026-08-31 — `cs3240` / `django-next`", text)
        self.assertIn("CLOSES 2026-09-02 — `cs3240` / `django-next`", text)
        due_sections = text.split("## Due / Overdue / Due Today", 1)[1].split(
            "## Assessment Availability Windows", 1
        )[0]
        self.assertNotIn("2026-08-31 — `cs3240`", due_sections)
        self.assertIn("`dsa` — next 2026-09-08 assessment `ps-0`", text)
        self.assertNotIn("Already Submitted Work", text)
        self.assertIn("active `submission-format` conflict", text)
        self.assertIn("active `sprint-label` conflict", text)
        self.assertIn("active `due-at` conflict", text)
        next_three = text.split("## Next 3 Days", 1)[1].split("## Next 7 Days", 1)[0]
        self.assertNotIn("conflicted-date", next_three)
        self.assertIn("due=sometime next week", text)
        self.assertIn("observed 2026-08-30 — changed", text)
        self.assertIn("observed 2026-08-30 — no relevant change", text)
        self.assertIn("observed 2026-08-30 — unavailable", text)
        self.assertIn("`eco` / `announcements` — never observed in durable state", text)
        self.assertIn("`no-sources` — no course source descriptors recorded", text)
        self.assertNotIn("confidence", text.lower().replace("does not assign urgency or confidence scores", ""))
        with self.assertRaises(SchoolLearningError):
            render_plan(sw, "August 30")
        with mock.patch("sys.stderr", new=io.StringIO()), self.assertRaises(SystemExit):
            cli_parser().parse_args(["render-plan", "2026-fall"])

    def test_semester_plan_source_coverage_uses_semantic_observation_recency(self):
        cases = [
            (
                "fraction-equality",
                [
                    (
                        "fraction-equality-a",
                        "2026-09-01T00:00:00.1Z",
                        "partial",
                        "unavailable",
                    ),
                    (
                        "fraction-equality-z",
                        "2026-09-01T00:00:00.100000Z",
                        "full",
                        "changed",
                    ),
                ],
                "- `cs3100` / `fraction-equality` — observed "
                "2026-09-01T00:00:00.100000Z — changed (`full` scope)",
            ),
            (
                "fraction-difference",
                [
                    (
                        "fraction-difference-z",
                        "2026-09-01T00:00:00.1Z",
                        "full",
                        "unavailable",
                    ),
                    (
                        "fraction-difference-a",
                        "2026-09-01T00:00:00.100001Z",
                        "partial",
                        "changed",
                    ),
                ],
                "- `cs3100` / `fraction-difference` — observed "
                "2026-09-01T00:00:00.100001Z — changed (`partial` scope)",
            ),
            (
                "offset-equality",
                [
                    (
                        "offset-equality-a",
                        "2026-09-01T02:00:00+02:00",
                        "partial",
                        "unavailable",
                    ),
                    (
                        "offset-equality-z",
                        "2026-09-01T00:00:00Z",
                        "full",
                        "no-relevant-change",
                    ),
                ],
                "- `cs3100` / `offset-equality` — observed "
                "2026-09-01T00:00:00Z — no relevant change (`full` scope)",
            ),
            (
                "offset-difference",
                [
                    (
                        "offset-difference-z",
                        "2026-09-01T02:00:00+02:00",
                        "full",
                        "unavailable",
                    ),
                    (
                        "offset-difference-a",
                        "2026-08-31T20:00:01-04:00",
                        "partial",
                        "changed",
                    ),
                ],
                "- `cs3100` / `offset-difference` — observed "
                "2026-08-31T20:00:01-04:00 — changed (`partial` scope)",
            ),
            (
                "date-equality",
                [
                    (
                        "date-equality-a",
                        "2026-09-01T00:00:00Z",
                        "full",
                        "unavailable",
                    ),
                    (
                        "date-equality-z",
                        "2026-09-01",
                        "partial",
                        "changed",
                    ),
                ],
                "- `cs3100` / `date-equality` — observed "
                "2026-09-01 — changed (`partial` scope)",
            ),
            (
                "timestamp-after-date",
                [
                    (
                        "timestamp-after-date-z",
                        "2026-09-01",
                        "full",
                        "unavailable",
                    ),
                    (
                        "timestamp-after-date-a",
                        "2026-09-01T00:00:01Z",
                        "partial",
                        "no-relevant-change",
                    ),
                ],
                "- `cs3100` / `timestamp-after-date` — observed "
                "2026-09-01T00:00:01Z — no relevant change (`partial` scope)",
            ),
            (
                "date-after-timestamp",
                [
                    (
                        "date-after-timestamp-z",
                        "2026-08-31T23:59:59Z",
                        "full",
                        "unavailable",
                    ),
                    (
                        "date-after-timestamp-a",
                        "2026-09-01",
                        "partial",
                        "changed",
                    ),
                ],
                "- `cs3100` / `date-after-timestamp` — observed "
                "2026-09-01 — changed (`partial` scope)",
            ),
        ]

        for source_id, observations, _expected_line in cases:
            upsert_source(
                self.ws,
                source_id,
                f"Synthetic {source_id}",
                f"local {source_id} reference",
                recorded_at="2026-08-30T12:00:00Z",
            )
            for observation_id, observed_at, scope, outcome in observations:
                append_source_observation(
                    self.ws,
                    source_id,
                    scope,
                    outcome,
                    observed_at=observed_at,
                    observation_id=observation_id,
                )

        text = render_plan(self.sw, "2026-08-31").read_text()
        coverage_section = text.split("## Source Coverage / Observations", 1)[1].split(
            "## Planning-Relevant Unresolved Conflicts", 1
        )[0]
        coverage_lines = coverage_section.splitlines()
        for source_id, _observations, expected_line in cases:
            selected = [line for line in coverage_lines if f"/ `{source_id}` —" in line]
            with self.subTest(source_id=source_id):
                self.assertEqual(selected, [expected_line])

    def test_semester_plan_treats_due_and_due_at_as_one_semantic_family(self):
        def add_claim(
            assessment_id,
            title,
            field,
            value,
            source,
            observed_at,
            recorded_at,
            claim_status="confirmed",
        ):
            return upsert_assessment(
                self.ws,
                assessment_id,
                title,
                "homework",
                "upcoming",
                claim_field=field,
                claim_value=value,
                claim_source=source,
                claim_observed_at=observed_at,
                claim_status=claim_status,
                recorded_at=recorded_at,
            )

        add_claim(
            "legacy-only",
            "Legacy Due Only",
            "due",
            "2026-09-01",
            "legacy-only source",
            "2026-08-28",
            "2026-08-28T10:00:00Z",
        )
        add_claim(
            "normalized-only",
            "Normalized Due Only",
            "due-at",
            "2026-09-02",
            "normalized-only source",
            "2026-08-28",
            "2026-08-28T10:01:00Z",
        )
        add_claim(
            "equal-aliases",
            "Equal Due Aliases",
            "due",
            "2026-09-03",
            "legacy equal source",
            "2026-08-28",
            "2026-08-28T10:02:00Z",
        )
        add_claim(
            "equal-aliases",
            "Equal Due Aliases",
            "due-at",
            "2026-09-03",
            "normalized equal source",
            "2026-08-29",
            "2026-08-29T10:02:00Z",
        )
        add_claim(
            "conflicting-aliases",
            "Conflicting Due Aliases",
            "due",
            "2026-09-01",
            "legacy conflict source",
            "2026-08-28",
            "2026-08-28T10:03:00Z",
        )
        add_claim(
            "conflicting-aliases",
            "Conflicting Due Aliases",
            "due-at",
            "2026-09-02",
            "normalized conflict source",
            "2026-08-29",
            "2026-08-29T10:03:00Z",
        )
        add_claim(
            "superseded-legacy",
            "Superseded Legacy Due",
            "due",
            "discarded unsupported phrase",
            "legacy supersession source",
            "2026-08-28",
            "2026-08-28T10:04:00Z",
        )
        add_claim(
            "superseded-legacy",
            "Superseded Legacy Due",
            "due",
            "discarded unsupported phrase",
            "legacy supersession source",
            "2026-08-28",
            "2026-08-29T10:04:00Z",
            claim_status="superseded",
        )
        add_claim(
            "superseded-legacy",
            "Superseded Legacy Due",
            "due-at",
            "2026-09-02",
            "normalized supersession source",
            "2026-08-29",
            "2026-08-29T10:05:00Z",
        )
        add_claim(
            "unsupported-legacy",
            "Unsupported Legacy Due",
            "due",
            "next Sunday",
            "unsupported legacy source",
            "2026-08-28",
            "2026-08-29T10:06:00Z",
        )
        add_claim(
            "same-field-mixed",
            "Same-Field Supported Unsupported",
            "due-at",
            "2026-09-01",
            "same-field supported source",
            "2026-08-28",
            "2026-08-29T10:07:00Z",
        )
        add_claim(
            "same-field-mixed",
            "Same-Field Supported Unsupported",
            "due-at",
            "next Sunday",
            "same-field unsupported source",
            "2026-08-29",
            "2026-08-29T10:08:00Z",
        )
        add_claim(
            "mixed-alias-supported-unsupported",
            "Mixed-Alias Supported Unsupported",
            "due",
            "2026-09-02",
            "mixed-alias supported source",
            "2026-08-28",
            "2026-08-29T10:09:00Z",
        )
        add_claim(
            "mixed-alias-supported-unsupported",
            "Mixed-Alias Supported Unsupported",
            "due-at",
            "after the review session",
            "mixed-alias unsupported source",
            "2026-08-29",
            "2026-08-29T10:10:00Z",
        )
        add_claim(
            "all-active-unsupported",
            "All Active Unsupported",
            "due",
            "when announced",
            "all-unsupported legacy source",
            "2026-08-28",
            "2026-08-29T10:11:00Z",
        )
        add_claim(
            "all-active-unsupported",
            "All Active Unsupported",
            "due-at",
            "after the lab",
            "all-unsupported normalized source",
            "2026-08-29",
            "2026-08-29T10:12:00Z",
        )

        text = render_plan(self.sw, "2026-08-31").read_text()
        due_sections = text.split("## Due / Overdue / Due Today", 1)[1].split(
            "## Assessment Availability Windows", 1
        )[0]
        conflict_section = text.split("## Planning-Relevant Unresolved Conflicts", 1)[1].split(
            "## Longer-Horizon Summary", 1
        )[0]
        unstructured_section = text.split(
            "## Unstructured Scheduling Claims That Cannot Safely Be Interpreted", 1
        )[1]

        self.assertIn("2026-09-01 — `cs3100` / `legacy-only`", due_sections)
        self.assertIn("2026-09-02 — `cs3100` / `normalized-only`", due_sections)
        self.assertEqual(due_sections.count("`cs3100` / `equal-aliases`"), 1)
        self.assertNotIn("`cs3100` / `conflicting-aliases`", due_sections)
        self.assertIn("active `due/due-at` conflict", conflict_section)
        self.assertIn(
            "due=2026-09-01 — source: legacy conflict source", conflict_section
        )
        self.assertIn(
            "due-at=2026-09-02 — source: normalized conflict source", conflict_section
        )
        self.assertIn("2026-09-02 — `cs3100` / `superseded-legacy`", due_sections)
        self.assertNotIn("2026-09-01 — `cs3100` / `superseded-legacy`", due_sections)
        self.assertNotIn("legacy supersession source", text)
        self.assertNotIn("`cs3100` / `unsupported-legacy`", due_sections)
        self.assertIn("due=next Sunday", unstructured_section)
        self.assertIn("source: unsupported legacy source", unstructured_section)
        self.assertNotIn("`cs3100` / `same-field-mixed`", due_sections)
        self.assertIn(
            "`cs3100` / `same-field-mixed` — active `due-at` conflict",
            conflict_section,
        )
        self.assertIn(
            "due-at=2026-09-01 — source: same-field supported source — observed: 2026-08-28",
            conflict_section,
        )
        self.assertIn(
            "due-at=next Sunday — source: same-field unsupported source — observed: 2026-08-29",
            conflict_section,
        )
        self.assertIn("due-at=next Sunday", unstructured_section)
        self.assertNotIn("`cs3100` / `mixed-alias-supported-unsupported`", due_sections)
        self.assertIn(
            "`cs3100` / `mixed-alias-supported-unsupported` — active `due/due-at` conflict",
            conflict_section,
        )
        self.assertIn(
            "due=2026-09-02 — source: mixed-alias supported source — observed: 2026-08-28",
            conflict_section,
        )
        self.assertIn(
            "due-at=after the review session — source: mixed-alias unsupported source — observed: 2026-08-29",
            conflict_section,
        )
        self.assertIn("due-at=after the review session", unstructured_section)
        self.assertNotIn("`cs3100` / `all-active-unsupported`", due_sections)
        self.assertIn(
            "`cs3100` / `all-active-unsupported` — active `due/due-at` conflict",
            conflict_section,
        )
        self.assertIn(
            "due=when announced — source: all-unsupported legacy source — observed: 2026-08-28",
            conflict_section,
        )
        self.assertIn(
            "due-at=after the lab — source: all-unsupported normalized source — observed: 2026-08-29",
            conflict_section,
        )
        self.assertIn("due=when announced", unstructured_section)
        self.assertIn("source: all-unsupported legacy source", unstructured_section)
        self.assertIn("due-at=after the lab", unstructured_section)
        self.assertIn("source: all-unsupported normalized source", unstructured_section)

    def test_semester_plan_uses_canonical_timestamp_subset_and_fractional_instants(self):
        def add_due(assessment_id, title, value, source, observed_at, recorded_at):
            return upsert_assessment(
                self.ws,
                assessment_id,
                title,
                "homework",
                "upcoming",
                claim_field="due-at",
                claim_value=value,
                claim_source=source,
                claim_observed_at=observed_at,
                recorded_at=recorded_at,
            )

        accepted = {
            "whole-seconds-z": "2026-09-01T00:00:00Z",
            "fraction-1": "2026-09-01T00:00:00.1Z",
            "fraction-3": "2026-09-01T00:00:00.123Z",
            "fraction-6": "2026-09-01T00:00:00.123456Z",
            "numeric-offset": "2026-09-01T00:00:00.123456-04:00",
        }
        for index, (assessment_id, value) in enumerate(accepted.items()):
            add_due(
                assessment_id,
                f"Accepted {assessment_id}",
                value,
                f"accepted source {index}",
                "2026-08-29",
                f"2026-08-29T10:0{index}:00Z",
            )

        rejected = {
            "fraction-7": "2026-09-01T00:00:00.1234567Z",
            "seconds-omitted": "2026-09-01T00:00Z",
            "timezone-omitted": "2026-09-01T00:00:00",
            "malformed-offset": "2026-09-01T00:00:00+24:00",
        }
        for index, (assessment_id, value) in enumerate(rejected.items()):
            add_due(
                assessment_id,
                f"Rejected {assessment_id}",
                value,
                f"rejected source {index}",
                "2026-08-29",
                f"2026-08-29T11:0{index}:00Z",
            )

        add_due(
            "same-fractional-instant",
            "Same Fractional Instant",
            "2026-09-01T00:00:00.1Z",
            "same instant short fraction",
            "2026-08-29",
            "2026-08-29T12:00:00Z",
        )
        add_due(
            "same-fractional-instant",
            "Same Fractional Instant",
            "2026-09-01T00:00:00.100000Z",
            "same instant six-digit fraction",
            "2026-08-30",
            "2026-08-30T12:00:00Z",
        )
        add_due(
            "different-fractional-instants",
            "Different Fractional Instants",
            "2026-09-01T00:00:00.1Z",
            "different instant first source",
            "2026-08-29",
            "2026-08-29T13:00:00Z",
        )
        add_due(
            "different-fractional-instants",
            "Different Fractional Instants",
            "2026-09-01T00:00:00.100001Z",
            "different instant second source",
            "2026-08-30",
            "2026-08-30T13:00:00Z",
        )

        text = render_plan(self.sw, "2026-08-31").read_text()
        due_sections = text.split("## Due / Overdue / Due Today", 1)[1].split(
            "## Assessment Availability Windows", 1
        )[0]
        conflict_section = text.split(
            "## Planning-Relevant Unresolved Conflicts", 1
        )[1].split("## Longer-Horizon Summary", 1)[0]
        unstructured_section = text.split(
            "## Unstructured Scheduling Claims That Cannot Safely Be Interpreted", 1
        )[1]

        for assessment_id in accepted:
            self.assertEqual(due_sections.count(f"`cs3100` / `{assessment_id}`"), 1)
        for assessment_id in rejected:
            self.assertNotIn(f"`cs3100` / `{assessment_id}`", due_sections)
            self.assertIn(f"`cs3100` / `{assessment_id}`", unstructured_section)
        self.assertEqual(
            due_sections.count("`cs3100` / `same-fractional-instant`"), 1
        )
        self.assertNotIn("same-fractional-instant", conflict_section)
        self.assertNotIn("`cs3100` / `different-fractional-instants`", due_sections)
        self.assertIn(
            "`cs3100` / `different-fractional-instants` — active `due-at` conflict",
            conflict_section,
        )
        self.assertIn("due-at=2026-09-01T00:00:00.1Z", conflict_section)
        self.assertIn("due-at=2026-09-01T00:00:00.100001Z", conflict_section)

    def test_operational_loop_cli_source_observe_review_apply_and_plan(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(
                cli_main(
                    [
                        "--data-root",
                        str(self.root),
                        "source",
                        "2026-fall",
                        "cs3100",
                        "course-site",
                        "Course Site",
                        "local course-site reference",
                        "--status",
                        "confirmed",
                        "--recorded-at",
                        "2026-08-29T12:00:00Z",
                    ]
                ),
                0,
            )
            self.assertEqual(
                cli_main(
                    [
                        "--data-root",
                        str(self.root),
                        "observe",
                        "2026-fall",
                        "cs3100",
                        "course-site",
                        "--scope",
                        "full",
                        "--outcome",
                        "no-relevant-change",
                        "--observed-at",
                        "2026-08-29",
                        "--id",
                        "cli-course-site-check",
                    ]
                ),
                0,
            )
        candidate = self.candidate([self.assessment_operation(id="cli-assessment")])
        path = self.write_candidate(candidate, "cli-reviewed-update.json")
        review_output = io.StringIO()
        with redirect_stdout(review_output):
            self.assertEqual(
                cli_main(["--data-root", str(self.root), "review-update", str(path)]), 0
            )
        digest = reviewed_update_digest(candidate)
        self.assertIn(f"Semantic candidate SHA-256: {digest}", review_output.getvalue())
        self.assertIn(
            f"apply-update {path} --confirm {digest}", review_output.getvalue()
        )
        with redirect_stdout(io.StringIO()):
            self.assertEqual(
                cli_main(
                    [
                        "--data-root",
                        str(self.root),
                        "apply-update",
                        str(path),
                        "--confirm",
                        digest,
                    ]
                ),
                0,
            )
            self.assertEqual(
                cli_main(
                    [
                        "--data-root",
                        str(self.root),
                        "render-plan",
                        "2026-fall",
                        "--as-of",
                        "2026-08-30",
                    ]
                ),
                0,
            )
        self.assertIn(
            "cli-assessment",
            {item["id"] for item in load_course_core(self.ws)["assessments"]},
        )
        self.assertTrue((self.semester_generated_dir() / "semester-plan.md").exists())

    def test_course_and_semester_home_are_deterministic_and_html_safe(self):
        self.intake()
        upsert_policy(
            self.ws,
            "attendance",
            "Attendance <required>",
            "attendance",
            "Attend <all> labs",
            "syllabus <source>",
            status="provisional",
            observed_at="2026-08-26",
            recorded_at="2026-08-26T12:07:00Z",
        )
        first_course = tuple(path.read_bytes() for path in render_course(self.ws))
        first_semester_path = render_semester(self.sw)
        first_semester = first_semester_path.read_bytes()
        self.assertEqual(first_course, tuple(path.read_bytes() for path in render_course(self.ws)))
        self.assertEqual(first_semester, render_semester(self.sw).read_bytes())
        html = first_course[0].decode("utf-8")
        self.assertNotIn("<official>", html)
        self.assertNotIn("<required>", html)
        self.assertIn("&lt;official&gt;", html)
        self.assertIn("&lt;required&gt;", html)
        self.assertIn("provisional", first_semester.decode("utf-8"))

    def test_course_handoff_includes_exact_selection_and_removes_stale_files(self):
        first = self.intake()
        second = intake_material(
            self.ws,
            self.source("reading.pdf", b"%PDF synthetic"),
            "reading-01",
            "Reading",
            kind="reading",
            added_at="2026-08-26T12:08:00Z",
        )
        observation = append_source_observation(
            self.ws,
            "syllabus",
            "full",
            "no-relevant-change",
            material_ids=[second["id"]],
            observed_at="2026-08-27",
            observation_id="syllabus-check-001",
        )
        handoff = prepare_course_handoff(self.ws, [first["id"], second["id"]])
        self.assertEqual(
            sorted(path.name for path in handoff["attachments"].iterdir()),
            [
                "course-context.md",
                "material-lecture-02.pptx",
                "material-reading-01.pdf",
                "update-contract.json",
            ],
        )
        prompt = handoff["prompt"].read_text()
        self.assertIn("do not choose a silent winner", prompt)
        self.assertIn("learner mastery", prompt)
        manifest = json.loads((handoff["root"] / "manifest.json").read_text())
        self.assertEqual(manifest["material_ids"], ["lecture-02", "reading-01"])
        self.assertEqual(manifest["context_attachment"]["role"], "course-context")
        self.assertEqual(
            manifest["context_attachment"]["attachment_filename"], "course-context.md"
        )
        self.assertEqual(
            manifest["attachment_filenames"],
            [
                "course-context.md",
                "update-contract.json",
                "material-lecture-02.pptx",
                "material-reading-01.pdf",
            ],
        )
        self.assertEqual(
            manifest["update_contract_attachment"]["attachment_filename"],
            "update-contract.json",
        )
        self.assertFalse((handoff["root"] / "course-context.md").exists())
        start_here = (handoff["root"] / "START-HERE.md").read_text()
        self.assertIn("Attach every file in that directory", start_here)
        self.assertIn("required distinguished `course-context.md`", start_here)
        transferred = {
            path.name: path.read_bytes() for path in handoff["attachments"].iterdir()
        }
        self.assertIn("course-context.md", transferred)
        self.assertIn("update-contract.json", transferred)
        self.assertIn(b'"capability_tags"', transferred["course-context.md"])
        self.assertIn(b'"assessments"', transferred["course-context.md"])
        self.assertIn(b'"policies"', transferred["course-context.md"])
        self.assertIn(b'"course_core"', transferred["course-context.md"])
        self.assertIn(b'"created_at"', transferred["course-context.md"])
        self.assertIn(b'"updated_at"', transferred["course-context.md"])
        self.assertIn(observation["id"].encode(), transferred["course-context.md"])
        contract = json.loads(transferred["update-contract.json"])
        self.assertEqual(contract["schema_version"], core.UPDATE_CONTRACT_SCHEMA)
        self.assertEqual(
            contract["base_context_sha256"],
            hashlib.sha256(transferred["course-context.md"]).hexdigest(),
        )
        self.assertEqual(contract["allowed_operation_kinds"], list(core.REVIEWED_OPERATION_KINDS))
        self.assertEqual(contract["candidate_keys"], sorted(core._REVIEWED_UPDATE_KEYS))
        constraints = contract["constraints"]
        self.assertEqual(
            constraints["base_identity"]["complete_semantic_sections"],
            ["course", "course_core", "materials", "source_observations", "topics"],
        )
        self.assertTrue(constraints["base_identity"]["exact_attachment_bytes"])
        self.assertEqual(
            constraints["root"]["fields"]["schema_version"]["const"],
            core.REVIEWED_UPDATE_SCHEMA,
        )
        self.assertEqual(constraints["root"]["fields"]["operations"]["min_items"], 1)
        self.assertEqual(constraints["root"]["fields"]["operations"]["max_items"], 100)
        self.assertEqual(
            constraints["definitions"]["identifier"]["pattern"],
            r"^[a-z0-9][a-z0-9._-]*$",
        )
        self.assertEqual(
            constraints["definitions"]["utc_timestamp"]["pattern"],
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
        )
        self.assertEqual(
            constraints["definitions"]["observed_at"]["one_of_patterns"],
            [
                r"^\d{4}-\d{2}-\d{2}$",
                r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$",
            ],
        )
        self.assertEqual(
            constraints["definitions"]["planner_value"]["timestamp_seconds"],
            "required",
        )
        assessment_fields = constraints["operations"]["assessment-upsert"]["fields"]
        self.assertEqual(assessment_fields["type"]["max_length"], 64)
        self.assertEqual(assessment_fields["type"]["pattern"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertEqual(
            assessment_fields["weight"], {"ref": "nullable_measure"}
        )
        self.assertEqual(
            constraints["operations"]["policy-upsert"]["fields"]["claims"][
                "item_field_const"
            ],
            "rule",
        )
        self.assertEqual(
            constraints["operations"]["source-observation"]["fields"]["material_ids"][
                "ref"
            ],
            "identifier_list",
        )
        observation_id = constraints["operations"]["source-observation"]["fields"]["id"]
        self.assertTrue(observation_id["append_only_identity"])
        self.assertEqual(
            observation_id["novelty"],
            {
                "existing_state_unique_against": "source_observations[*].id",
                "ordered_candidate_unique_against": (
                    "prior source-observation operations[*].id"
                ),
            },
        )
        self.assertFalse(observation_id["overwrite_existing"])
        self.assertFalse(observation_id["reuse_existing"])
        self.assertEqual(
            constraints["claim"]["fields"]["field"]["forbidden_values"], ["due"]
        )
        self.assertEqual(
            constraints["claim"]["fields"]["source"], {"ref": "nonempty_string"}
        )
        self.assertIn("only a reviewed candidate", " ".join(contract["rules"]))
        self.assertIn("Use course-context.md", handoff["prompt"].read_text())
        self.assertEqual(
            core.sha256_file(handoff["attachments"] / "material-lecture-02.pptx"),
            (first["sha256"], first["bytes"]),
        )
        refreshed = prepare_course_handoff(self.ws, [second["id"]])
        self.assertEqual(
            sorted(path.name for path in refreshed["attachments"].iterdir()),
            ["course-context.md", "material-reading-01.pdf", "update-contract.json"],
        )
        (refreshed["attachments"] / "stale-material.txt").write_bytes(b"stale")
        (refreshed["attachments"] / "course-context-old.md").write_bytes(b"stale context")
        zero = prepare_course_handoff(self.ws, [])
        self.assertEqual(
            sorted(path.name for path in zero["attachments"].iterdir()),
            ["course-context.md", "update-contract.json"],
        )
        zero_manifest = json.loads((zero["root"] / "manifest.json").read_text())
        self.assertEqual(zero_manifest["material_ids"], [])
        self.assertEqual(zero_manifest["materials"], [])
        self.assertEqual(
            zero_manifest["attachment_filenames"],
            ["course-context.md", "update-contract.json"],
        )
        cli_output = io.StringIO()
        with redirect_stdout(cli_output):
            self.assertEqual(
                cli_main(
                    [
                        "--data-root", str(self.root), "course-context", "2026-fall", "cs3100"
                    ]
                ),
                0,
            )
        self.assertIn("Attach every required file under", cli_output.getvalue())
        self.assertIn("attachments/course-context.md", cli_output.getvalue())
        stored = self.ws.course_dir / second["stored_path"]
        before_failure = {
            path.relative_to(zero["root"]).as_posix(): path.read_bytes()
            for path in zero["root"].rglob("*")
            if path.is_file()
        }
        stored.write_bytes(b"stale mutation")
        with self.assertRaises(SchoolLearningError):
            prepare_course_handoff(self.ws, [second["id"]])
        self.assertEqual(
            {
                path.relative_to(zero["root"]).as_posix(): path.read_bytes()
                for path in zero["root"].rglob("*")
                if path.is_file()
            },
            before_failure,
        )

    def test_semester_symlink_escape_is_rejected(self):
        external = self.root / "external"
        external.mkdir()
        sentinel = external / "sentinel"
        sentinel.write_bytes(b"preserve")
        generated = self.semester_generated_dir()
        generated.rmdir()
        generated.symlink_to(external, target_is_directory=True)
        with self.assertRaises(SchoolLearningError):
            render_semester(self.sw)
        self.assertEqual(sentinel.read_bytes(), b"preserve")
        self.assertEqual(sorted(item.name for item in external.iterdir()), ["sentinel"])

    def test_reserved_semester_namespace_does_not_contaminate_legacy_course_ids(self):
        collision_root = self.root / "collision-root"
        generated_course = initialize_course(
            collision_root, "2027-spring", "generated", "Generated Course",
            created_at="2026-08-26T13:00:00Z",
        )
        state_named_course = initialize_course(
            collision_root, "2027-spring", "semester.json", "State Named Course",
            created_at="2026-08-26T13:00:00Z",
        )
        before_generated = complete_snapshot(generated_course.course_dir)
        before_state_named = complete_snapshot(state_named_course.course_dir)
        sw = initialize_semester(
            collision_root, "2027-spring", "Spring 2027",
            created_at="2026-08-26T13:01:00Z",
        )
        self.assertEqual(complete_snapshot(generated_course.course_dir), before_generated)
        self.assertEqual(complete_snapshot(state_named_course.course_dir), before_state_named)
        self.assertTrue((sw.term_dir / ".school-learning/semester.json").is_file())
        self.assertTrue((sw.term_dir / ".school-learning/generated").is_dir())
        self.assertTrue((sw.term_dir / "generated/course.json").is_file())
        self.assertTrue((sw.term_dir / "semester.json/course.json").is_file())

    def test_semester_initialization_failures_remove_only_first_time_artifacts(self):
        transaction_parent = self.root / "semester-init-transactions"
        transaction_parent.mkdir()
        real_create = core._safe_create_directory
        real_write = core._atomic_term_json

        def run(stage, patch_target, side_effect):
            before = complete_snapshot(transaction_parent)
            with self.subTest(stage=stage), mock.patch.object(
                core, patch_target, side_effect=side_effect
            ):
                with self.assertRaises(SchoolLearningError):
                    initialize_semester(
                        transaction_parent / f"data-{stage}",
                        f"2027-{stage}",
                        "Transactional Semester",
                        created_at="2026-08-26T13:02:00Z",
                    )
            self.assertEqual(complete_snapshot(transaction_parent), before)

        def fail_term(path, label, created=None):
            if path.name == "2027-term":
                raise SchoolLearningError("synthetic term directory failure")
            return real_create(path, label, created)

        def fail_metadata(path, label, created=None):
            if path.name == ".school-learning":
                raise SchoolLearningError("synthetic metadata directory failure")
            return real_create(path, label, created)

        def fail_generated(path, label, created=None):
            if path.name == "generated" and path.parent.name == ".school-learning":
                raise SchoolLearningError("synthetic generated directory failure")
            return real_create(path, label, created)

        def fail_state(sw, path, value):
            if path.name == "semester.json":
                raise SchoolLearningError("synthetic semester state failure")
            return real_write(sw, path, value)

        run("term", "_safe_create_directory", fail_term)
        run("metadata", "_safe_create_directory", fail_metadata)
        run("generated", "_safe_create_directory", fail_generated)
        run("state", "_atomic_term_json", fail_state)
        run(
            "validate",
            "load_semester",
            lambda sw: (_ for _ in ()).throw(
                SchoolLearningError("synthetic final semester validation failure")
            ),
        )

    def test_post_effect_semester_directory_failures_restore_snapshot_and_allow_retry(self):
        transaction_parent = self.root / "post-effect-semester-init"
        transaction_parent.mkdir()
        sibling = transaction_parent / "sibling-sentinel.bin"
        sibling.write_bytes(b"unrelated sibling bytes\x00")
        real_is_dir = Path.is_dir

        for stage in ("data-root", "term", "metadata", "generated"):
            with self.subTest(stage=stage):
                if stage == "data-root":
                    data_root = transaction_parent / "new-chain" / "nested-data-root"
                    term = "2027-data-root"
                    failure_target = transaction_parent / "new-chain"
                else:
                    data_root = transaction_parent / f"existing-data-root-{stage}"
                    data_root.mkdir()
                    term = f"2027-{stage}"
                    term_dir = data_root / term
                    if stage in {"metadata", "generated"}:
                        term_dir.mkdir()
                        course_sibling = term_dir / "existing-course"
                        course_sibling.mkdir()
                        (course_sibling / "sentinel.bin").write_bytes(
                            b"pre-existing course sibling\x00"
                        )
                    failure_target = {
                        "term": term_dir,
                        "metadata": term_dir / ".school-learning",
                        "generated": term_dir / ".school-learning" / "generated",
                    }[stage]
                before = complete_snapshot(transaction_parent)
                validation_failed_after_creation = False

                def fail_post_creation_validation(path):
                    nonlocal validation_failed_after_creation
                    if (
                        path == failure_target
                        and path.exists()
                        and not validation_failed_after_creation
                    ):
                        validation_failed_after_creation = True
                        raise OSError(
                            f"synthetic post-effect {stage} validation failure"
                        )
                    return real_is_dir(path)

                with mock.patch.object(
                    Path, "is_dir", new=fail_post_creation_validation
                ):
                    with self.assertRaises(SchoolLearningError):
                        initialize_semester(
                            data_root,
                            term,
                            "Transactional Semester",
                            created_at="2026-08-27T12:00:00Z",
                        )

                self.assertTrue(validation_failed_after_creation)
                self.assertEqual(complete_snapshot(transaction_parent), before)
                self.assertEqual(sibling.read_bytes(), b"unrelated sibling bytes\x00")
                self.assertEqual(
                    [
                        path
                        for path in transaction_parent.rglob("*")
                        if path.name.startswith(".semester.json.")
                    ],
                    [],
                )

                retry = initialize_semester(
                    data_root,
                    term,
                    "Transactional Semester",
                    created_at="2026-08-27T12:00:00Z",
                )
                self.assertEqual(load_semester(retry)["title"], "Transactional Semester")
                self.assertEqual(sibling.read_bytes(), b"unrelated sibling bytes\x00")
                self.assertEqual(
                    [
                        path
                        for path in retry.term_dir.rglob("*")
                        if path.name.startswith(".semester.json.")
                    ],
                    [],
                )

    def test_semester_directory_rollback_is_deepest_first(self):
        transaction_parent = self.root / "rollback-order"
        transaction_parent.mkdir()
        sentinel = transaction_parent / "sentinel.bin"
        sentinel.write_bytes(b"preserve rollback-order sibling")
        data_root = transaction_parent / "outer" / "inner"
        term = "2027-order"
        generated = data_root / term / ".school-learning" / "generated"
        real_create = core._safe_create_directory
        real_rmdir = Path.rmdir
        removed = []

        def create_then_fail(path, label, created=None):
            result = real_create(path, label, created)
            if path == generated:
                raise SchoolLearningError("synthetic post-effect generated failure")
            return result

        def record_rmdir(path):
            removed.append(path)
            return real_rmdir(path)

        before = complete_snapshot(transaction_parent)
        with mock.patch.object(
            core, "_safe_create_directory", side_effect=create_then_fail
        ), mock.patch.object(Path, "rmdir", new=record_rmdir):
            with self.assertRaises(SchoolLearningError):
                initialize_semester(
                    data_root,
                    term,
                    "Rollback Order",
                    created_at="2026-08-27T12:01:00Z",
                )

        self.assertEqual(
            removed,
            [
                generated,
                generated.parent,
                generated.parent.parent,
                data_root,
                data_root.parent,
            ],
        )
        self.assertEqual(complete_snapshot(transaction_parent), before)
        self.assertEqual(sentinel.read_bytes(), b"preserve rollback-order sibling")

    def test_semester_directory_rollback_failure_is_reported_as_incomplete(self):
        transaction_parent = self.root / "rollback-failure"
        transaction_parent.mkdir()
        sentinel = transaction_parent / "sentinel.bin"
        sentinel.write_bytes(b"preserve rollback-failure sibling")
        data_root = transaction_parent / "data-root"
        term = "2027-rollback-failure"
        metadata = data_root / term / ".school-learning"
        generated = metadata / "generated"
        real_create = core._safe_create_directory
        real_rmdir = Path.rmdir

        def create_then_fail(path, label, created=None):
            result = real_create(path, label, created)
            if path == generated:
                raise SchoolLearningError("synthetic post-effect generated failure")
            return result

        def fail_metadata_rollback(path):
            if path == metadata:
                raise OSError("synthetic metadata rollback failure")
            return real_rmdir(path)

        with mock.patch.object(
            core, "_safe_create_directory", side_effect=create_then_fail
        ), mock.patch.object(Path, "rmdir", new=fail_metadata_rollback):
            with self.assertRaisesRegex(
                SchoolLearningError,
                "semester initialization failed and rollback was incomplete",
            ):
                initialize_semester(
                    data_root,
                    term,
                    "Rollback Failure",
                    created_at="2026-08-27T12:02:00Z",
                )

        self.assertTrue(metadata.is_dir())
        self.assertEqual(sentinel.read_bytes(), b"preserve rollback-failure sibling")

    def test_existing_valid_semester_is_not_tracked_as_newly_created(self):
        before = complete_snapshot(self.sw.term_dir)
        with mock.patch.object(core, "_safe_create_directory") as create:
            same = initialize_semester(
                self.root,
                "2026-fall",
                "Fall 2026",
                created_at="2026-08-27T12:03:00Z",
            )
        create.assert_not_called()
        self.assertEqual(same, self.sw)
        self.assertEqual(complete_snapshot(self.sw.term_dir), before)

    def test_existing_malformed_semester_is_rejected_before_any_mutation(self):
        path = self.semester_state_path()
        path.write_bytes(b'{"malformed": true}\n')
        before = complete_snapshot(self.sw.term_dir)
        with self.assertRaises(SchoolLearningError):
            initialize_semester(self.root, "2026-fall", "Fall 2026")
        self.assertEqual(complete_snapshot(self.sw.term_dir), before)

    def test_new_registration_failure_matrix_restores_complete_term_snapshot(self):
        real_initialize = core.initialize_course
        real_json_write = core._atomic_write_json
        real_term_write = core._atomic_term_json
        real_load_semester = core.load_semester
        post_effect_artifacts = set()

        def exercise(course_id, patch_target, side_effect):
            before = complete_snapshot(self.sw.term_dir)
            with self.subTest(course_id=course_id), mock.patch.object(
                core, patch_target, side_effect=side_effect
            ):
                with self.assertRaises(SchoolLearningError):
                    register_course(
                        self.sw, course_id, course_id.title(),
                        recorded_at="2026-08-26T13:03:00Z",
                    )
            self.assertEqual(complete_snapshot(self.sw.term_dir), before)

        def initialize_then_fail(*args, **kwargs):
            ws = real_initialize(*args, **kwargs)
            post_effect_artifacts.update(
                path.relative_to(ws.course_dir).as_posix()
                for path in ws.course_dir.rglob("*")
            )
            (ws.course_dir / "synthetic-partial.txt").write_bytes(b"partial")
            raise SchoolLearningError("synthetic new course initialization failure")

        exercise("fail-init", "initialize_course", initialize_then_fail)
        self.assertTrue(
            {
                "course.json",
                "materials.json",
                "topics.json",
                "materials",
                "sessions",
                "generated",
            }.issubset(post_effect_artifacts)
        )

        def fail_core(ws, path, value):
            if path.name == "course-core.json":
                real_json_write(ws, path, value)
                raise SchoolLearningError("synthetic course core failure")
            return real_json_write(ws, path, value)

        exercise("fail-core", "_atomic_write_json", fail_core)

        def fail_material_upgrade(ws, path, value):
            if path.name == "materials.json" and value.get("schema_version") == core.MATERIALS_V02_SCHEMA:
                real_json_write(ws, path, value)
                raise SchoolLearningError("synthetic materials upgrade failure")
            return real_json_write(ws, path, value)

        exercise("fail-materials", "_atomic_write_json", fail_material_upgrade)

        original_semester = json.dumps(load_semester(self.sw), separators=(",", ":")).encode()
        self.semester_state_path().write_bytes(original_semester)

        def write_semester_then_fail(sw, path, value):
            result = real_term_write(sw, path, value)
            if "fail-semester" in value.get("course_ids", []):
                raise SchoolLearningError("synthetic semester registration failure")
            return result

        exercise("fail-semester", "_atomic_term_json", write_semester_then_fail)
        self.assertEqual(self.semester_state_path().read_bytes(), original_semester)

        load_calls = 0

        def fail_final_cross_state(sw):
            nonlocal load_calls
            load_calls += 1
            value = real_load_semester(sw)
            if load_calls == 2:
                raise SchoolLearningError("synthetic final cross-state validation failure")
            return value

        exercise("fail-final", "load_semester", fail_final_cross_state)

    def test_post_effect_initializer_failure_restores_preexisting_empty_workspace(self):
        course_dir = self.sw.term_dir / "preexisting-empty"
        course_dir.mkdir()
        before = complete_snapshot(self.sw.term_dir)
        real_initialize = core.initialize_course
        post_effect_artifacts = set()

        def initialize_then_fail(*args, **kwargs):
            ws = real_initialize(*args, **kwargs)
            post_effect_artifacts.update(
                path.relative_to(ws.course_dir).as_posix()
                for path in ws.course_dir.rglob("*")
            )
            raise SchoolLearningError("synthetic post-effect initialization failure")

        with mock.patch.object(core, "initialize_course", side_effect=initialize_then_fail):
            with self.assertRaises(SchoolLearningError):
                register_course(
                    self.sw,
                    "preexisting-empty",
                    "Preexisting Empty",
                    recorded_at="2026-08-26T13:03:30Z",
                )

        self.assertTrue(
            {
                "course.json",
                "materials.json",
                "topics.json",
                "materials",
                "sessions",
                "generated",
            }.issubset(post_effect_artifacts)
        )
        self.assertEqual(complete_snapshot(self.sw.term_dir), before)
        self.assertTrue(course_dir.is_dir())
        self.assertEqual(list(course_dir.iterdir()), [])

    def test_existing_course_upgrade_failure_restores_byte_exact_complete_snapshot(self):
        legacy = initialize_course(
            self.root, "2026-fall", "legacy-rollback", "Legacy Rollback",
            created_at="2026-08-26T13:04:00Z",
        )
        add_material(
            legacy,
            self.source("legacy-rollback.md", b"legacy rollback bytes"),
            "notes",
            "Notes",
            added_at="2026-08-26T13:04:30Z",
        )
        state = load_semester(self.sw)
        self.semester_state_path().write_bytes(
            json.dumps(state, separators=(",", ":")).encode("utf-8")
        )
        before = complete_snapshot(self.sw.term_dir)
        real_load = core.load_semester
        calls = 0

        def fail_final(sw):
            nonlocal calls
            calls += 1
            value = real_load(sw)
            if calls == 2:
                raise SchoolLearningError("synthetic existing-course final validation failure")
            return value

        with mock.patch.object(core, "load_semester", side_effect=fail_final):
            with self.assertRaises(SchoolLearningError):
                register_course(
                    self.sw,
                    "legacy-rollback",
                    "Legacy Rollback",
                    recorded_at="2026-08-26T13:05:00Z",
                )
        self.assertEqual(complete_snapshot(self.sw.term_dir), before)

    def test_symlinked_term_workspace_is_rejected(self):
        moved = self.root / "moved-semester"
        self.sw.term_dir.rename(moved)
        self.sw.term_dir.symlink_to(moved, target_is_directory=True)
        with self.assertRaises(SchoolLearningError):
            load_semester(self.sw)

    def test_new_cli_commands_smoke(self):
        root = self.root / "cli-root"
        source = self.source("cli.png", b"png synthetic")
        commands = [
            ["semester", "2026-fall", "Fall 2026"],
            [
                "course", "2026-fall", "art100", "Art", "--capability", "creative-applied-work",
                "--source", "syllabus|Syllabus|local|confirmed", "--metadata", "section=002",
            ],
            [
                "intake", "2026-fall", "art100", "image-01", "Reference Image", str(source),
                "--kind", "technical-reference", "--status", "reference", "--date", "2026-08-27",
            ],
            [
                "assessment", "2026-fall", "art100", "project-1", "Project 1", "--type", "project",
                "--status", "upcoming", "--material", "image-01", "--claim-field", "due",
                "--claim-value", "2026-09-01", "--claim-source", "syllabus",
            ],
            [
                "policy", "2026-fall", "art100", "ai", "AI Policy", "ai", "Disclose AI use",
                "syllabus", "--status", "confirmed",
            ],
            ["render", "2026-fall", "art100"],
            ["render-semester", "2026-fall"],
            ["course-context", "2026-fall", "art100", "--material", "image-01"],
        ]
        for command in commands:
            with self.subTest(command=command[0]), redirect_stdout(io.StringIO()):
                self.assertEqual(cli_main(["--data-root", str(root), *command]), 0)

class RefreshPackageTests(ExternalTemporaryTestCase):
    def setUp(self):
        super().setUp()
        self.sw = initialize_semester(self.root, "2026-fall", "Synthetic Fall", created_at=TIMESTAMP)
        self.ws = register_course(self.sw, "apma", "Synthetic APMA", recorded_at=TIMESTAMP)

    def source(self, name="Assignments.png", content=b"synthetic assignments"):
        path = self.root / name
        path.write_bytes(content)
        return path

    def durable_snapshot(self):
        return {key: value for key, value in complete_snapshot(self.ws.course_dir).items()
                if key != "generated" and not key.startswith("generated/")}

    def test_apma_explicit_refresh_has_exact_attachments_and_no_promotion(self):
        paths = [self.source(), self.source("Modules.png", b"modules"),
                 self.source("new-assignment.pdf", b"new assignment")]
        durable = add_material(self.ws, self.source("lecture.pdf", b"lecture"), "lecture", "Lecture")
        before = self.durable_snapshot()
        result = prepare_refresh(self.ws, [durable["id"]], paths, notes="Post-class refresh")
        manifest = json.loads((result["root"] / "manifest.json").read_bytes())
        context = json.loads(result["refresh_context"].read_bytes())
        self.assertEqual(self.durable_snapshot(), before)
        self.assertEqual(manifest["material_ids"], ["lecture"])
        self.assertEqual(len(manifest["evidence"]), 3)
        self.assertEqual(sorted(p.name for p in result["attachments"].iterdir()),
                         manifest["attachment_filenames"])
        self.assertEqual(context["attachment_filenames"], manifest["attachment_filenames"])
        self.assertFalse(result["reviewed_update"].exists())
        for path in paths:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            entry = next(x for x in manifest["evidence"] if x["id"] == "evidence-" + digest)
            self.assertEqual((result["attachments"] / entry["attachment_filename"]).read_bytes(),
                             path.read_bytes())
        for path in [result["refresh_context"], result["root"] / "manifest.json", result["prompt"]]:
            self.assertNotIn(str(self.root), path.read_text())
        identity = manifest.pop("package_id")
        self.assertEqual(identity, hashlib.sha256(core._canonical_json_bytes(manifest)).hexdigest())
        self.assertEqual(result["root"].name, "refresh-package-" + identity)
        self.assertFalse((self.ws.course_dir / "generated/course-handoff").exists())

    def test_cs3240_partial_lecture_preserves_exact_notes_separately(self):
        ws = register_course(self.sw, "cs3240", "Synthetic CS3240", recorded_at=TIMESTAMP)
        notes = b"  stopped around slide 25\r\n\r\n  "
        note_file = self.source("owner-notes.txt", notes)
        result = prepare_refresh(ws, evidence=[self.source("partial.pptx", b"slides")], notes_file=note_file)
        owner = json.loads(result["refresh_context"].read_bytes())["owner_notes"]
        self.assertEqual(owner["text"].encode("utf-8"), notes)
        self.assertEqual(owner["sha256"], hashlib.sha256(notes).hexdigest())
        self.assertEqual(owner["bytes"], len(notes))
        self.assertNotIn("stopped around slide 25", result["prompt"].read_text())
        inline = prepare_refresh(ws, evidence=[self.root / "partial.pptx"], notes=notes.decode())
        self.assertEqual(result, inline)
        changed = prepare_refresh(ws, evidence=[self.root / "partial.pptx"], notes=notes.decode().strip())
        self.assertNotEqual(result["root"], changed["root"])

    def test_transient_collision_with_selected_or_unselected_durable_id_is_atomic(self):
        evidence = self.source(content=b"transient collision bytes")
        identity = "evidence-" + hashlib.sha256(evidence.read_bytes()).hexdigest()
        durable = add_material(self.ws, self.source("durable.txt", b"different durable bytes"),
                               identity, "Existing compatible durable ID")
        self.assertEqual(durable["id"], identity)
        self.assertIn(identity, [item["id"] for item in load_materials(self.ws)["materials"]])
        prior = prepare_refresh(self.ws, notes="existing package")
        prior["reviewed_update"].write_bytes(b"preserve owner return")
        before = complete_snapshot(self.ws.course_dir)
        for selected in ([], [identity]):
            with self.subTest(selected=bool(selected)), \
                 mock.patch.object(core, "_create_temp_directory") as staging, \
                 mock.patch.object(core, "_publish_directory") as publication:
                with self.assertRaisesRegex(SchoolLearningError, "collides with an existing durable material ID"):
                    prepare_refresh(self.ws, selected, [evidence])
                staging.assert_not_called()
                publication.assert_not_called()
                self.assertEqual(complete_snapshot(self.ws.course_dir), before)
        normal = prepare_refresh(self.ws, [identity], [self.source("normal.txt", b"non-colliding")])
        manifest = json.loads((normal["root"] / "manifest.json").read_bytes())
        self.assertEqual(manifest["material_ids"], [identity])
        self.assertNotEqual(manifest["evidence"][0]["id"], identity)
        self.assertEqual(prior["reviewed_update"].read_bytes(), b"preserve owner return")

    def test_evidence_shaped_durable_id_remains_valid_for_review_and_apply(self):
        identity = "evidence-" + hashlib.sha256(b"synthetic identity").hexdigest()
        add_material(self.ws, self.source("durable.txt", b"durable bytes"), identity, "Durable")
        package = prepare_refresh(self.ws, [identity], [self.source(content=b"other evidence")])
        candidate = {
            "schema_version": core.REVIEWED_UPDATE_SCHEMA, "term": self.ws.term,
            "course_id": self.ws.course_id, "base_context_sha256": course_context_sha256(self.ws),
            "operations": [{"kind": "assessment-upsert", "id": "hw", "title": "Homework",
                "type": "homework", "status": "submitted", "weight": None, "points": None,
                "xp": None, "material_ids": [identity], "topic_ids": [], "recorded_at": TIMESTAMP,
                "claims": [{"field": "submission", "value": "Submitted",
                            "source": "Synthetic owner", "observed_at": "2026-09-06",
                            "status": "confirmed"}]}],
        }
        path = package["reviewed_update"]
        path.write_text(json.dumps(candidate), encoding="utf-8")
        before = complete_snapshot(self.ws.course_dir)
        preview = review_update(self.root, path)
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)
        with self.assertRaisesRegex(SchoolLearningError, "confirmation digest"):
            apply_update(self.root, path, "0" * 64)
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)
        apply_update(self.root, path, preview["digest"])
        self.assertEqual(load_course_core(self.ws)["assessments"][0]["material_ids"], [identity])
        with self.assertRaisesRegex(SchoolLearningError, "stale"):
            review_update(self.root, path)

    def test_filename_drift_preserves_evidence_identity_but_changes_metadata_package(self):
        first = self.source("Assignments.png", b"same bytes")
        second = self.source("Assignments (1).png", b"same bytes")
        a = prepare_refresh(self.ws, evidence=[first])
        b = prepare_refresh(self.ws, evidence=[second])
        ea = json.loads(a["refresh_context"].read_bytes())["evidence"][0]
        eb = json.loads(b["refresh_context"].read_bytes())["evidence"][0]
        self.assertEqual(ea["id"], eb["id"])
        self.assertEqual(ea["attachment_filename"], eb["attachment_filename"])
        self.assertNotEqual(ea["source_name"], eb["source_name"])
        self.assertNotEqual(a["root"], b["root"])

    def test_deterministic_order_and_return_preservation_without_trusting_json(self):
        paths = [self.source(), self.source("Modules.png", b"modules")]
        result = prepare_refresh(self.ws, evidence=paths)
        result["reviewed_update"].write_bytes(b"```json\nnot valid\n```")
        before = complete_snapshot(self.ws.course_dir)
        rerun = prepare_refresh(self.ws, evidence=reversed(paths))
        self.assertEqual(result, rerun)
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)
        with self.assertRaises(SchoolLearningError):
            review_update(self.root, result["reviewed_update"])
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)

    def test_submission_candidate_unchanged_review_confirm_and_stale_path(self):
        result = prepare_refresh(self.ws, evidence=[self.source()])
        evidence_id = json.loads(result["refresh_context"].read_bytes())["evidence"][0]["id"]
        candidate = {
            "schema_version": core.REVIEWED_UPDATE_SCHEMA, "term": self.ws.term,
            "course_id": self.ws.course_id,
            "base_context_sha256": hashlib.sha256(result["context"].read_bytes()).hexdigest(),
            "operations": [{"kind": "assessment-upsert", "id": "hw-1", "title": "Homework 1",
                "type": "homework", "status": "submitted", "weight": None, "points": None,
                "xp": None, "material_ids": [], "topic_ids": [], "recorded_at": TIMESTAMP,
                "claims": [{"field": "submission", "value": "Submitted by owner",
                            "source": evidence_id, "observed_at": "2026-09-06",
                            "status": "confirmed"}]}],
        }
        path = result["reviewed_update"]
        path.write_text(json.dumps(candidate), encoding="utf-8")
        before = self.durable_snapshot()
        preview = review_update(self.root, path)
        self.assertEqual(self.durable_snapshot(), before)
        with self.assertRaisesRegex(SchoolLearningError, "confirmation digest"):
            apply_update(self.root, path, "0" * 64)
        self.assertEqual(self.durable_snapshot(), before)
        apply_update(self.root, path, preview["digest"])
        self.assertEqual(load_course_core(self.ws)["assessments"][0]["status"], "submitted")
        after = self.durable_snapshot()
        with self.assertRaisesRegex(SchoolLearningError, "stale"):
            review_update(self.root, path)
        self.assertEqual(self.durable_snapshot(), after)
        candidate["base_context_sha256"] = course_context_sha256(self.ws)
        candidate["operations"][0]["material_ids"] = [evidence_id]
        path.write_text(json.dumps(candidate))
        with self.assertRaises(SchoolLearningError):
            review_update(self.root, path)
        self.assertEqual(self.durable_snapshot(), after)

    def test_invalid_excessive_duplicate_and_notes_inputs_leave_workspace_unchanged(self):
        source = self.source()
        duplicate = self.source("copy.png", source.read_bytes())
        bad_type = self.source("bad.exe")
        bad_notes = self.source("bad-notes.txt", b"\xff")
        cases = [dict(evidence=[source, duplicate]), dict(evidence=[source] * 101),
                 dict(evidence=[bad_type]), dict(evidence=[self.root / "missing.pdf"]),
                 dict(evidence=str(source)), dict(notes="x", notes_file=bad_notes),
                 dict(notes_file=bad_notes), dict(notes="x" * (core._REFRESH_NOTES_MAX_BYTES + 1)),
                 dict(material_ids=["missing"]), dict(evidence=[self.root])]
        before = complete_snapshot(self.ws.course_dir)
        for kwargs in cases:
            with self.subTest(kwargs=list(kwargs)):
                with self.assertRaises(SchoolLearningError):
                    prepare_refresh(self.ws, **kwargs)
                self.assertEqual(complete_snapshot(self.ws.course_dir), before)
        with mock.patch.object(core, "_REFRESH_MAX_BYTES", 3):
            with self.assertRaisesRegex(SchoolLearningError, "byte limit"):
                prepare_refresh(self.ws, evidence=[source])
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)

    def test_aggregate_budget_includes_durable_and_transient_bytes(self):
        material = add_material(self.ws, self.source("durable.pdf", b"1234"), "m", "M")
        evidence = self.source(content=b"5678")
        before = complete_snapshot(self.ws.course_dir)
        with mock.patch.object(core, "_REFRESH_MAX_BYTES", 7):
            with self.assertRaisesRegex(SchoolLearningError, "byte limit"):
                prepare_refresh(self.ws, [material["id"]], [evidence])
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)

    def test_external_symlink_ancestor_traversal_fifo_and_notes_links_rejected(self):
        source = self.source()
        alias = self.root / "alias.png"
        alias.symlink_to(source)
        directory = self.root / "linked"
        directory.symlink_to(self.root, target_is_directory=True)
        fifo = self.root / "pipe.png"
        os.mkfifo(fifo)
        before = complete_snapshot(self.ws.course_dir)
        for path in [alias, directory / source.name, self.root / "unused/../Assignments.png", fifo]:
            with self.subTest(path=path.name), self.assertRaises(SchoolLearningError):
                prepare_refresh(self.ws, evidence=[path])
        with self.assertRaises(SchoolLearningError):
            prepare_refresh(self.ws, notes_file=alias)
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)

    def test_changed_source_during_copy_fails_closed_and_removes_staging(self):
        source = self.source()
        before = complete_snapshot(self.ws.course_dir)
        write = core._atomic_write_bytes
        def change(ws, path, content):
            write(ws, path, content)
            if path.name.startswith("evidence-"):
                source.write_bytes(b"changed evidence")
        with mock.patch.object(core, "_atomic_write_bytes", side_effect=change):
            with self.assertRaisesRegex(SchoolLearningError, "changed|byte limit"):
                prepare_refresh(self.ws, evidence=[source])
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)

    def test_source_replaced_by_symlink_during_copy_fails_closed(self):
        source = self.source()
        target = self.source("other.png", b"other")
        before = complete_snapshot(self.ws.course_dir)
        write = core._atomic_write_bytes
        def change(ws, path, content):
            write(ws, path, content)
            if path.name.startswith("evidence-"):
                source.unlink()
                source.symlink_to(target)
        with mock.patch.object(core, "_atomic_write_bytes", side_effect=change):
            with self.assertRaises(SchoolLearningError):
                prepare_refresh(self.ws, evidence=[source])
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)

    def test_existing_package_tampering_rejected_without_overwriting_return(self):
        source = self.source()
        result = prepare_refresh(self.ws, evidence=[source])
        result["reviewed_update"].write_bytes(b"owner return")
        targets = [result["prompt"], result["refresh_context"], result["root"] / "manifest.json",
                   next(result["attachments"].glob("evidence-*"))]
        for target in targets:
            original = target.read_bytes()
            target.write_bytes(b"tampered")
            before = complete_snapshot(self.ws.course_dir)
            with self.assertRaisesRegex(SchoolLearningError, "tampered"):
                prepare_refresh(self.ws, evidence=[source])
            self.assertEqual(complete_snapshot(self.ws.course_dir), before)
            target.write_bytes(original)
        result["reviewed_update"].unlink()
        result["reviewed_update"].symlink_to(source)
        with self.assertRaises(SchoolLearningError):
            prepare_refresh(self.ws, evidence=[source])

    def test_staged_tampering_rejected(self):
        source = self.source()
        before = complete_snapshot(self.ws.course_dir)
        write = core._atomic_write_bytes
        def tamper(ws, path, content):
            write(ws, path, b"tampered" if path.name == "prompt.txt" else content)
        with mock.patch.object(core, "_atomic_write_bytes", side_effect=tamper):
            with self.assertRaises(SchoolLearningError):
                prepare_refresh(self.ws, evidence=[source])
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)

    def test_publication_failure_before_and_after_rename_restores_absence(self):
        source = self.source()
        replace = core.os.replace
        before = complete_snapshot(self.ws.course_dir)
        for after_effect in [False, True]:
            def fail(src, dst):
                if Path(src).name.startswith(".refresh-package.staging."):
                    if after_effect:
                        replace(src, dst)
                    raise OSError("synthetic publication failure")
                return replace(src, dst)
            with mock.patch.object(core.os, "replace", side_effect=fail):
                with self.assertRaises(SchoolLearningError):
                    prepare_refresh(self.ws, evidence=[source])
            self.assertEqual(complete_snapshot(self.ws.course_dir), before)

    def test_cleanup_failure_reports_incomplete_recovery(self):
        source = self.source()
        recover = core._recover_remove_tree
        def fail(ws, path, label, causal):
            if label == "failed refresh package staging directory":
                raise SchoolLearningError("synthetic recovery incomplete")
            return recover(ws, path, label, causal)
        with mock.patch.object(core, "_validate_refresh_package", side_effect=SchoolLearningError("tamper")), \
             mock.patch.object(core, "_recover_remove_tree", side_effect=fail):
            with self.assertRaisesRegex(SchoolLearningError, "recovery incomplete"):
                prepare_refresh(self.ws, evidence=[source])
        self.assertFalse(list((self.ws.course_dir / "generated").glob("refresh-package-*")))

    def test_cli_prepare_and_open_is_opt_in(self):
        source = self.source()
        argv = ["--data-root", str(self.root), "prepare-refresh", self.ws.term,
                self.ws.course_id, "--evidence", str(source), "--notes", "stopped around slide 25"]
        output = io.StringIO()
        with mock.patch("tools.school_learning.cli._open_refresh_directory") as opener, redirect_stdout(output):
            self.assertEqual(cli_main(argv), 0)
            opener.assert_not_called()
            self.assertEqual(cli_main(argv + ["--open"]), 0)
            opener.assert_called_once()
            self.assertTrue(opener.call_args.args[0].is_dir())
        self.assertIn("review-update", output.getvalue())
        self.assertIn("Refresh package ready", output.getvalue())

    def test_opener_safe_arrays_exact_conversion_and_failures_warn(self):
        from tools.school_learning import cli
        package = prepare_refresh(self.ws)["root"]
        windows = "C:" + chr(92) + "Synthetic folder" + chr(92) + "package"
        replies = [mock.Mock(stdout=windows + "\n"), mock.Mock(stdout=str(package) + "\n"), mock.Mock()]
        with mock.patch.object(cli.sys, "platform", "linux"), \
             mock.patch.object(cli.platform, "release", return_value="microsoft-standard-WSL2"), \
             mock.patch.object(cli.shutil, "which", side_effect=lambda name: "/synthetic/" + name), \
             mock.patch.object(cli.subprocess, "run", side_effect=replies) as run:
            cli._open_refresh_directory(package)
            self.assertEqual(run.call_args_list[-1].args[0], ["/synthetic/explorer.exe", windows])
            for call in run.call_args_list:
                self.assertIsInstance(call.args[0], list)
                self.assertNotIn("shell", call.kwargs)
                self.assertEqual(call.kwargs["timeout"], 5)
        failures = [OSError("missing"), cli.subprocess.TimeoutExpired("synthetic", 5),
                    cli.subprocess.CalledProcessError(1, "synthetic")]
        for failure in failures:
            with mock.patch.object(cli.sys, "platform", "linux"), \
                 mock.patch.object(cli.platform, "release", return_value="microsoft"), \
                 mock.patch.object(cli.shutil, "which", return_value="synthetic"), \
                 mock.patch.object(cli.subprocess, "run", side_effect=failure), redirect_stderr(io.StringIO()) as warning:
                cli._open_refresh_directory(package)
                self.assertIn(str(package), warning.getvalue())
        with mock.patch.object(cli.sys, "platform", "unsupported"), \
             mock.patch.object(cli.subprocess, "run") as run, redirect_stderr(io.StringIO()) as warning:
            cli._open_refresh_directory(package)
            run.assert_not_called()
            self.assertIn("Warning", warning.getvalue())

    def test_notes_source_changes_and_course_changes_during_copy_are_rejected(self):
        source = self.source()
        notes = self.source("notes.txt", b"exact notes")
        before = complete_snapshot(self.ws.course_dir)
        write = core._atomic_write_bytes
        def change(ws, path, content):
            write(ws, path, content)
            if path.name.startswith("evidence-"):
                notes.write_bytes(b"other notes")
        with mock.patch.object(core, "_atomic_write_bytes", side_effect=change):
            with self.assertRaises(SchoolLearningError):
                prepare_refresh(self.ws, evidence=[source], notes_file=notes)
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)
        with mock.patch.object(core, "course_context_bytes", return_value=b"changed"):
            with self.assertRaisesRegex(SchoolLearningError, "course context changed"):
                prepare_refresh(self.ws, evidence=[source])
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)

    def test_generated_parent_symlink_and_extra_package_attachment_are_rejected(self):
        source = self.source()
        result = prepare_refresh(self.ws, evidence=[source])
        extra = result["attachments"] / "extra.txt"
        extra.write_bytes(b"unselected")
        before = complete_snapshot(self.ws.course_dir)
        with self.assertRaises(SchoolLearningError):
            prepare_refresh(self.ws, evidence=[source])
        self.assertEqual(complete_snapshot(self.ws.course_dir), before)
        ws = register_course(self.sw, "isolated", "Synthetic", recorded_at=TIMESTAMP)
        generated = ws.course_dir / "generated"
        generated.rmdir()
        generated.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(SchoolLearningError):
            prepare_refresh(ws, evidence=[source])

    def test_cli_real_opener_failure_still_returns_success_and_usable_package(self):
        from tools.school_learning import cli
        source = self.source()
        output, warning = io.StringIO(), io.StringIO()
        with mock.patch.object(cli.sys, "platform", "unsupported"), \
             redirect_stdout(output), redirect_stderr(warning):
            code = cli_main(["--data-root", str(self.root), "prepare-refresh", self.ws.term,
                             self.ws.course_id, "--evidence", str(source), "--open"])
        self.assertEqual(code, 0)
        package = prepare_refresh(self.ws, evidence=[source])
        self.assertIn(str(package["root"]), output.getvalue())
        self.assertIn(str(package["root"]), warning.getvalue())

    def test_open_revalidates_symlink_replacement_and_tampering_after_conversion(self):
        from tools.school_learning import cli
        import shutil
        for attack in ("symlink", "replacement", "tamper", "missing"):
            with self.subTest(attack=attack):
                package = prepare_refresh(self.ws, notes=attack)["root"]
                saved = package.with_name("saved-" + package.name)
                calls = []
                def convert(argv, **kwargs):
                    calls.append(argv)
                    self.assertNotIn("explorer.exe", argv[0])
                    if argv[1] == "-w":
                        return mock.Mock(stdout="C:/synthetic/package\n")
                    if attack == "tamper":
                        (package / "prompt.txt").write_bytes(b"tampered")
                    else:
                        package.rename(saved)
                        if attack == "symlink":
                            package.symlink_to(saved, target_is_directory=True)
                        elif attack == "replacement":
                            shutil.copytree(saved, package)
                    return mock.Mock(stdout=str(package) + "\n")
                with mock.patch.object(cli.sys, "platform", "linux"), \
                     mock.patch.object(cli.platform, "release", return_value="microsoft"), \
                     mock.patch.object(cli.shutil, "which", side_effect=lambda name: "/synthetic/" + name), \
                     mock.patch.object(cli.subprocess, "run", side_effect=convert), \
                     redirect_stderr(io.StringIO()) as warning:
                    cli._open_refresh_directory(package)
                self.assertEqual(len(calls), 2)
                self.assertIn("Warning", warning.getvalue())
                self.assertIn(str(package), warning.getvalue())

    def test_cli_package_swap_after_preparation_warns_without_host_launch(self):
        from tools.school_learning import cli
        prepare = cli.prepare_refresh
        saved = []
        def swap(*args, **kwargs):
            result = prepare(*args, **kwargs)
            original = result["root"]
            moved = original.with_name("saved-" + original.name)
            original.rename(moved)
            original.symlink_to(moved, target_is_directory=True)
            saved.append(moved)
            return result
        with mock.patch.object(cli, "prepare_refresh", side_effect=swap), \
             mock.patch.object(cli.sys, "platform", "linux"), \
             mock.patch.object(cli.platform, "release", return_value="microsoft"), \
             mock.patch.object(cli.shutil, "which", return_value="synthetic"), \
             mock.patch.object(cli.subprocess, "run") as run, \
             redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as warning:
            code = cli_main(["--data-root", str(self.root), "prepare-refresh", self.ws.term,
                             self.ws.course_id, "--notes", "swap after prepare", "--open"])
        self.assertEqual(code, 0)
        run.assert_not_called()
        self.assertIn("Refresh package ready", output.getvalue())
        self.assertIn("Warning", warning.getvalue())
        self.assertTrue((saved[0] / "manifest.json").is_file())

    def test_opener_rejects_bad_conversion_and_missing_tools(self):
        from tools.school_learning import cli
        package = prepare_refresh(self.ws)["root"]
        for replies in [[mock.Mock(stdout="relative\n")],
                        [mock.Mock(stdout="C:/valid\n"), mock.Mock(stdout="/wrong\n")]]:
            with mock.patch.object(cli.sys, "platform", "linux"), \
                 mock.patch.object(cli.platform, "release", return_value="microsoft"), \
                 mock.patch.object(cli.shutil, "which", return_value="synthetic"), \
                 mock.patch.object(cli.subprocess, "run", side_effect=replies) as run, \
                 redirect_stderr(io.StringIO()) as warning:
                cli._open_refresh_directory(package)
                self.assertEqual(run.call_count, len(replies))
                self.assertIn("Warning", warning.getvalue())
        with mock.patch.object(cli.sys, "platform", "linux"), \
             mock.patch.object(cli.platform, "release", return_value="microsoft"), \
             mock.patch.object(cli.shutil, "which", return_value=None), \
             mock.patch.object(cli.subprocess, "run") as run, redirect_stderr(io.StringIO()):
            cli._open_refresh_directory(package)
            run.assert_not_called()


class PersistedStateValidationTests(WorkspaceTestCase):
    def test_missing_keys_are_rejected_before_mutation(self):
        state = self.json_state("course.json")
        del state["title"]
        self.write_json_state("course.json", state)
        self.assert_rejected_without_mutation(lambda: ensure_topic(self.ws, "bfs", "BFS"))

    def test_unexpected_keys_are_rejected_before_rendering(self):
        state = self.json_state("topics.json")
        state["unexpected"] = "value"
        self.write_json_state("topics.json", state)
        self.assert_rejected_without_mutation(lambda: render_course(self.ws))

    def test_wrong_field_types_are_rejected(self):
        state = self.json_state("course.json")
        state["title"] = ["not", "a", "string"]
        self.write_json_state("course.json", state)
        self.assert_rejected_without_mutation(lambda: load_course(self.ws))

    def test_boolean_material_byte_count_is_rejected(self):
        self.add_default_material()
        state = self.json_state("materials.json")
        state["materials"][0]["bytes"] = True
        self.write_json_state("materials.json", state)
        self.assert_rejected_without_mutation(lambda: load_materials(self.ws))

    def test_boolean_topic_priority_is_rejected(self):
        ensure_topic(self.ws, "bfs", "BFS")
        state = self.json_state("topics.json")
        state["topics"][0]["next_review_priority"] = True
        self.write_json_state("topics.json", state)
        self.assert_rejected_without_mutation(lambda: render_course(self.ws))

    def test_invalid_priority_range_is_rejected(self):
        ensure_topic(self.ws, "bfs", "BFS")
        state = self.json_state("topics.json")
        state["topics"][0]["next_review_priority"] = 101
        self.write_json_state("topics.json", state)
        self.assert_rejected_without_mutation(lambda: render_course(self.ws))

    def test_invalid_enum_values_are_rejected(self):
        ensure_topic(self.ws, "bfs", "BFS")
        state = self.json_state("topics.json")
        state["topics"][0]["status"] = "mastered"
        self.write_json_state("topics.json", state)
        self.assert_rejected_without_mutation(lambda: render_course(self.ws))

    def test_invalid_timestamp_is_rejected(self):
        state = self.json_state("course.json")
        state["created_at"] = "yesterday"
        self.write_json_state("course.json", state)
        self.assert_rejected_without_mutation(lambda: load_course(self.ws))

    def test_unknown_topic_material_reference_is_controlled(self):
        ensure_topic(self.ws, "bfs", "BFS")
        state = self.json_state("topics.json")
        state["topics"][0]["material_ids"] = ["unknown-material"]
        self.write_json_state("topics.json", state)
        self.assert_rejected_without_mutation(
            lambda: build_study_brief(self.ws, "bfs", "practice", "Practice")
        )

    def test_missing_stored_material_is_rejected_when_operation_depends_on_it(self):
        record = self.add_default_material()
        (self.ws.course_dir / record["stored_path"]).unlink()
        self.assert_rejected_without_mutation(lambda: render_course(self.ws))

    def test_invalid_session_record_is_rejected(self):
        self.add_topic_and_session()
        path = self.ws.course_dir / "sessions/session-001.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        del state["mode"]
        path.write_text(json.dumps(state), encoding="utf-8")
        self.assert_rejected_without_mutation(lambda: iter_sessions(self.ws))

    def test_boolean_session_priority_is_rejected(self):
        self.add_topic_and_session()
        path = self.ws.course_dir / "sessions/session-001.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        state["next_review_priority"] = True
        path.write_text(json.dumps(state), encoding="utf-8")
        self.assert_rejected_without_mutation(lambda: render_course(self.ws))

    def test_invalid_session_mode_is_rejected(self):
        self.add_topic_and_session()
        path = self.ws.course_dir / "sessions/session-001.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        state["mode"] = "guess"
        path.write_text(json.dumps(state), encoding="utf-8")
        self.assert_rejected_without_mutation(lambda: render_course(self.ws))

    def test_unknown_session_material_reference_is_rejected(self):
        self.add_topic_and_session()
        path = self.ws.course_dir / "sessions/session-001.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        state["material_ids"] = ["unknown-material"]
        path.write_text(json.dumps(state), encoding="utf-8")
        self.assert_rejected_without_mutation(lambda: render_course(self.ws))

    def test_session_filename_and_id_disagreement_is_rejected(self):
        self.add_topic_and_session()
        old = self.ws.course_dir / "sessions/session-001.json"
        old.rename(self.ws.course_dir / "sessions/wrong-name.json")
        self.assert_rejected_without_mutation(lambda: iter_sessions(self.ws))

    def test_session_course_disagreement_is_rejected(self):
        self.add_topic_and_session()
        path = self.ws.course_dir / "sessions/session-001.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        state["course_id"] = "other-course"
        path.write_text(json.dumps(state), encoding="utf-8")
        self.assert_rejected_without_mutation(lambda: render_course(self.ws))

    def test_session_term_disagreement_is_rejected(self):
        self.add_topic_and_session()
        path = self.ws.course_dir / "sessions/session-001.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        state["term"] = "2027-spring"
        path.write_text(json.dumps(state), encoding="utf-8")
        self.assert_rejected_without_mutation(lambda: render_course(self.ws))

    def test_course_term_disagreement_is_rejected(self):
        state = self.json_state("course.json")
        state["term"] = "2027-spring"
        self.write_json_state("course.json", state)
        self.assert_rejected_without_mutation(lambda: load_course(self.ws))

    def test_missing_workspace_directories_are_rejected(self):
        for index, name in enumerate(("materials", "sessions", "generated"), start=1):
            with self.subTest(name=name):
                ws = self.initialize(f"cs31{index:02d}")
                (ws.course_dir / name).rmdir()
                before = {
                    path.relative_to(ws.course_dir).as_posix(): path.read_bytes()
                    for path in ws.course_dir.rglob("*")
                    if path.is_file()
                }
                with self.assertRaises(SchoolLearningError):
                    load_course(ws)
                after = {
                    path.relative_to(ws.course_dir).as_posix(): path.read_bytes()
                    for path in ws.course_dir.rglob("*")
                    if path.is_file()
                }
                self.assertEqual(after, before)

    def test_malformed_render_input_is_rejected_before_output(self):
        ensure_topic(self.ws, "bfs", "BFS")
        state = self.json_state("topics.json")
        state["topics"][0]["title"] = 123
        self.write_json_state("topics.json", state)
        generated = self.ws.course_dir / "generated"
        self.assertEqual(list(generated.iterdir()), [])
        self.assert_rejected_without_mutation(lambda: render_course(self.ws))
        self.assertEqual(list(generated.iterdir()), [])


class DataRootTests(ExternalTemporaryTestCase):
    def test_builtin_default_root_is_accepted_without_creating_course_state(self):
        with mock.patch.dict(os.environ):
            os.environ.pop("AIDEN_SCHOOL_DATA_ROOT", None)
            root = core.default_data_root()
            ws = workspace(root, "2026-fall", "cs3100")
        self.assertEqual(root, Path("~/.local/share/aiden-platform/school").expanduser().resolve())
        self.assertEqual(ws.course_dir, root / "2026-fall" / "cs3100")

    def test_data_root_environment_default_is_accepted_without_writing_user_data(self):
        expected = self.root / "not-created"
        with mock.patch.dict(os.environ, {"AIDEN_SCHOOL_DATA_ROOT": str(expected)}):
            root = core.default_data_root()
            ws = workspace(root, "2026-fall", "cs3100")
        self.assertEqual(root, expected.resolve())
        self.assertEqual(ws.data_root, expected.resolve())
        self.assertFalse(expected.exists())

    def test_external_temporary_root_works(self):
        ws = initialize_course(
            self.root / "nested" / "school",
            "2026-fall",
            "cs3100",
            "Algorithms",
            created_at=TIMESTAMP,
        )
        self.assertTrue(ws.course_dir.is_dir())
        self.assertEqual(load_course(ws)["title"], "Algorithms")

    def test_repository_root_is_rejected_without_creation(self):
        before = set(core._REPOSITORY_ROOT.iterdir())
        with self.assertRaises(SchoolLearningError):
            initialize_course(
                core._REPOSITORY_ROOT,
                "2026-fall",
                "cs3100",
                "Algorithms",
                created_at=TIMESTAMP,
            )
        self.assertEqual(set(core._REPOSITORY_ROOT.iterdir()), before)

    def test_repository_descendant_is_rejected_before_creation(self):
        target = core._REPOSITORY_ROOT / ".school-learning-rejected-test"
        self.assertFalse(target.exists())
        with self.assertRaises(SchoolLearningError):
            initialize_course(target, "2026-fall", "cs3100", "Algorithms", created_at=TIMESTAMP)
        self.assertFalse(target.exists())

    def test_separate_git_worktree_descendant_is_rejected_before_creation(self):
        worktree = self.root / "synthetic-worktree"
        worktree.mkdir()
        (worktree / ".git").write_text("gitdir: /nonexistent/control\n", encoding="utf-8")
        target = worktree / "nested" / "school"
        with self.assertRaises(SchoolLearningError):
            initialize_course(target, "2026-fall", "cs3100", "Algorithms", created_at=TIMESTAMP)
        self.assertFalse(target.exists())


class SymlinkConfinementTests(WorkspaceTestCase):
    def external_target(self, name, content=b"external sentinel\n"):
        path = self.root / name
        path.mkdir()
        sentinel = path / "sentinel.txt"
        sentinel.write_bytes(content)
        return path, sentinel

    def replace_directory_with_symlink(self, name, target):
        directory = self.ws.course_dir / name
        directory.rmdir()
        directory.symlink_to(target, target_is_directory=True)

    def test_symlinked_materials_directory_is_rejected_without_external_write(self):
        external, sentinel = self.external_target("external-materials")
        before = sentinel.read_bytes()
        self.replace_directory_with_symlink("materials", external)
        source = self.material()
        with self.assertRaises(SchoolLearningError):
            add_material(self.ws, source, "lecture-01", "Lecture", added_at=TIMESTAMP)
        self.assertEqual(sentinel.read_bytes(), before)
        self.assertEqual(sorted(path.name for path in external.iterdir()), ["sentinel.txt"])

    def test_symlinked_sessions_directory_is_rejected_without_external_write(self):
        ensure_topic(self.ws, "bfs", "BFS")
        external, sentinel = self.external_target("external-sessions")
        before = sentinel.read_bytes()
        self.replace_directory_with_symlink("sessions", external)
        with self.assertRaises(SchoolLearningError):
            record_session(
                self.ws,
                "bfs",
                "correct",
                "solid",
                "done",
                session_id="session-001",
                recorded_at=TIMESTAMP,
            )
        self.assertEqual(sentinel.read_bytes(), before)
        self.assertEqual(sorted(path.name for path in external.iterdir()), ["sentinel.txt"])

    def test_symlinked_generated_directory_is_rejected_before_any_output(self):
        ensure_topic(self.ws, "bfs", "BFS")
        external, sentinel = self.external_target("external-generated")
        before = sentinel.read_bytes()
        self.replace_directory_with_symlink("generated", external)
        with self.assertRaises(SchoolLearningError):
            build_study_brief(self.ws, "bfs", "review", "Review")
        with self.assertRaises(SchoolLearningError):
            render_course(self.ws)
        self.assertEqual(sentinel.read_bytes(), before)
        self.assertEqual(sorted(path.name for path in external.iterdir()), ["sentinel.txt"])

    def test_unsafe_existing_stored_path_is_rejected_before_external_deletion(self):
        self.add_default_material()
        victim = self.root / "victim.md"
        victim.write_bytes(b"do not delete or replace\n")
        before = victim.read_bytes()
        state = self.json_state("materials.json")
        state["materials"][0]["stored_path"] = "../../../victim.md"
        self.write_json_state("materials.json", state)
        with self.assertRaises(SchoolLearningError):
            add_material(
                self.ws,
                self.root / "notes.md",
                "lecture-graphs",
                "Replacement",
                added_at="2026-07-21T15:02:00Z",
                replace=True,
            )
        self.assertEqual(victim.read_bytes(), before)

    def test_symlinked_material_file_is_rejected_without_external_read_or_write(self):
        record = self.add_default_material()
        stored = self.ws.course_dir / record["stored_path"]
        stored.unlink()
        victim = self.root / "external-material.md"
        victim.write_bytes(b"private external bytes\n")
        before = victim.read_bytes()
        stored.symlink_to(victim)
        with self.assertRaises(SchoolLearningError):
            load_materials(self.ws)
        with self.assertRaises(SchoolLearningError):
            add_material(
                self.ws,
                self.root / "notes.md",
                "lecture-graphs",
                "Replacement",
                added_at="2026-07-21T15:02:00Z",
                replace=True,
            )
        self.assertEqual(victim.read_bytes(), before)

    def test_symlinked_render_destination_is_rejected_before_other_output_changes(self):
        victim = self.root / "external-render.html"
        victim.write_bytes(b"external render sentinel\n")
        before = victim.read_bytes()
        (self.ws.course_dir / "generated/course-home.html").symlink_to(victim)
        with self.assertRaises(SchoolLearningError):
            render_course(self.ws)
        self.assertEqual(victim.read_bytes(), before)
        self.assertFalse((self.ws.course_dir / "generated/review.md").exists())

    def test_symlinked_study_brief_destination_is_rejected_without_external_write(self):
        ensure_topic(self.ws, "bfs", "BFS")
        victim = self.root / "external-brief.md"
        victim.write_bytes(b"external brief sentinel\n")
        before = victim.read_bytes()
        (self.ws.course_dir / "generated/study-brief.md").symlink_to(victim)
        with self.assertRaises(SchoolLearningError):
            build_study_brief(self.ws, "bfs", "review", "Review")
        self.assertEqual(victim.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
