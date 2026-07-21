import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.school_learning import (
    SchoolLearningError,
    add_material,
    build_study_brief,
    ensure_topic,
    initialize_course,
    iter_sessions,
    load_course,
    load_materials,
    load_topics,
    record_session,
    render_course,
    workspace,
)
from tools.school_learning import core


TIMESTAMP = "2026-07-21T15:00:00Z"


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
