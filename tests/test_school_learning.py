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
    load_materials,
    load_topics,
    record_session,
    render_course,
    workspace,
)
from tools.school_learning import core


class SchoolLearningTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.ws = initialize_course(
            self.root,
            "2026-fall",
            "cs3100",
            "Data Structures and Algorithms 2",
            created_at="2026-07-21T15:00:00Z",
        )

    def tearDown(self):
        self.temporary.cleanup()

    def material(self, name="notes.md", content=b"# Graphs\nBreadth-first search.\n"):
        path = self.root / name
        path.write_bytes(content)
        return path

    def test_workspace_rejects_traversal(self):
        for value in ("../escape", "a/b", "..", "/tmp"):
            with self.subTest(value=value), self.assertRaises(SchoolLearningError):
                workspace(self.root, value, "cs3100")

    def test_initial_state_uses_exact_schemas(self):
        self.assertEqual(json.loads((self.ws.course_dir / "course.json").read_text())["schema_version"], "aiden.school.course/v0.1")
        self.assertEqual(load_materials(self.ws)["materials"], [])
        self.assertEqual(load_topics(self.ws)["topics"], [])

    def test_material_hash_and_change_detection(self):
        source = self.material(content=b"alpha\n")
        first = add_material(self.ws, source, "lecture-01", "Lecture 1", added_at="2026-07-21T15:01:00Z")
        self.assertTrue(first["changed"])
        same = add_material(self.ws, source, "lecture-01", "Lecture 1", added_at="2026-07-21T15:02:00Z", replace=True)
        self.assertFalse(same["changed"])
        source.write_bytes(b"beta\n")
        changed = add_material(self.ws, source, "lecture-01", "Lecture 1", added_at="2026-07-21T15:03:00Z", replace=True)
        self.assertTrue(changed["changed"])
        self.assertNotEqual(first["sha256"], changed["sha256"])

    def test_unsupported_material_is_rejected(self):
        with self.assertRaises(SchoolLearningError):
            add_material(self.ws, self.material("video.mp4"), "video", "Video")

    def test_study_brief_is_grounded_and_inside_workspace(self):
        source = self.material()
        add_material(self.ws, source, "lecture-graphs", "Graph Lecture", added_at="2026-07-21T15:01:00Z")
        ensure_topic(self.ws, "bfs", "Breadth-first search", ["lecture-graphs"])
        brief = build_study_brief(self.ws, "bfs", "practice", "Practice BFS traversal")
        text = brief.read_text()
        self.assertIn("`lecture-graphs`", text)
        self.assertIn("insufficient", text)
        self.assertIn("does not update learning state automatically", text)
        with self.assertRaises(SchoolLearningError):
            build_study_brief(self.ws, "bfs", "practice", "Escape", output=self.root / "outside.md")

    def test_record_updates_topic_and_preserves_session(self):
        ensure_topic(self.ws, "bfs", "Breadth-first search")
        record = record_session(
            self.ws,
            "bfs",
            "partial",
            "review",
            "Missed queue invariant",
            session_id="session-001",
            recorded_at="2026-07-21T15:05:00Z",
            next_review_priority=90,
        )
        self.assertEqual(record["outcome"], "partial")
        topic = load_topics(self.ws)["topics"][0]
        self.assertEqual(topic["status"], "review")
        self.assertEqual(topic["next_review_priority"], 90)
        self.assertTrue((self.ws.course_dir / "sessions/session-001.json").exists())

    def test_invalid_json_state_is_rejected_without_mutation(self):
        path = self.ws.course_dir / "topics.json"
        path.write_text("not json", encoding="utf-8")
        before = path.read_bytes()
        with self.assertRaises(SchoolLearningError):
            ensure_topic(self.ws, "bfs", "Breadth-first search")
        self.assertEqual(path.read_bytes(), before)

    def test_atomic_write_failure_preserves_old_file(self):
        target = self.ws.course_dir / "topics.json"
        before = target.read_bytes()
        with mock.patch("tools.school_learning.core.os.replace", side_effect=OSError("blocked")):
            with self.assertRaises(OSError):
                core._atomic_write_json(target, {"schema_version": core.TOPICS_SCHEMA, "topics": [{"id": "x"}]})
        self.assertEqual(target.read_bytes(), before)
        leftovers = [path for path in target.parent.iterdir() if path.name.startswith(".topics.json.")]
        self.assertEqual(leftovers, [])

    def test_rendering_is_stable_for_identical_state_and_escapes_html(self):
        ensure_topic(self.ws, "bfs", "BFS <script>")
        record_session(
            self.ws,
            "bfs",
            "correct",
            "learning",
            "Good <work>",
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

    def test_data_root_environment_default(self):
        expected = self.root / "configured"
        with mock.patch.dict(os.environ, {"AIDEN_SCHOOL_DATA_ROOT": str(expected)}):
            self.assertEqual(core.default_data_root(), expected.resolve())


if __name__ == "__main__":
    unittest.main()
