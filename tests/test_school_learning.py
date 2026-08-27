import hashlib
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from tools.school_learning import (
    SchoolLearningError,
    add_material,
    build_study_brief,
    ensure_topic,
    initialize_course,
    initialize_semester,
    intake_material,
    iter_sessions,
    load_course,
    load_course_core,
    load_materials,
    load_semester,
    load_topics,
    prepare_course_handoff,
    record_session,
    register_course,
    render_course,
    render_semester,
    semester_workspace,
    upsert_assessment,
    upsert_policy,
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
        forbidden = ("socket", "requests", "urllib", "httpx", "openai", "anthropic", "subprocess")
        combined = "\n".join(path.read_text(encoding="utf-8") for path in production)
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(f"import {token}", combined)
                self.assertNotIn(f"from {token}", combined)


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
        handoff = prepare_course_handoff(self.ws, [first["id"], second["id"]])
        self.assertEqual(
            sorted(path.name for path in handoff["attachments"].iterdir()),
            ["course-context.md", "material-lecture-02.pptx", "material-reading-01.pdf"],
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
            ["course-context.md", "material-lecture-02.pptx", "material-reading-01.pdf"],
        )
        self.assertFalse((handoff["root"] / "course-context.md").exists())
        start_here = (handoff["root"] / "START-HERE.md").read_text()
        self.assertIn("Attach every file in that directory", start_here)
        self.assertIn("required distinguished `course-context.md`", start_here)
        transferred = {
            path.name: path.read_bytes() for path in handoff["attachments"].iterdir()
        }
        self.assertIn("course-context.md", transferred)
        self.assertIn(b'"capability_tags"', transferred["course-context.md"])
        self.assertIn(b'"assessments"', transferred["course-context.md"])
        self.assertIn(b'"policies"', transferred["course-context.md"])
        self.assertIn("Use course-context.md", handoff["prompt"].read_text())
        self.assertEqual(
            core.sha256_file(handoff["attachments"] / "material-lecture-02.pptx"),
            (first["sha256"], first["bytes"]),
        )
        refreshed = prepare_course_handoff(self.ws, [second["id"]])
        self.assertEqual(
            sorted(path.name for path in refreshed["attachments"].iterdir()),
            ["course-context.md", "material-reading-01.pdf"],
        )
        (refreshed["attachments"] / "stale-material.txt").write_bytes(b"stale")
        (refreshed["attachments"] / "course-context-old.md").write_bytes(b"stale context")
        zero = prepare_course_handoff(self.ws, [])
        self.assertEqual(
            sorted(path.name for path in zero["attachments"].iterdir()),
            ["course-context.md"],
        )
        zero_manifest = json.loads((zero["root"] / "manifest.json").read_text())
        self.assertEqual(zero_manifest["material_ids"], [])
        self.assertEqual(zero_manifest["materials"], [])
        self.assertEqual(zero_manifest["attachment_filenames"], ["course-context.md"])
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
