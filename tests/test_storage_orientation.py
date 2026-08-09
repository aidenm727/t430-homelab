import builtins
from contextlib import ExitStack, redirect_stderr
from datetime import datetime, timedelta, timezone
import io
import inspect
import json
import os
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

import storage_orientation as storage


AS_OF = datetime(2026, 8, 8, 12, 0, tzinfo=timezone.utc)


def timestamp(days: float) -> str:
    value = AS_OF - timedelta(days=days)
    return value.isoformat().replace("+00:00", "Z")


def entry(
    relative_path: str,
    *,
    size: int = 1,
    modified_utc: str | None = None,
    collector: str = "wsl",
    alias: str = "wsl_src",
    entry_type: str = "file",
) -> dict:
    record = storage._base_record("entry", collector, alias)
    record.update(
        {
            "relative_path": relative_path,
            "entry_type": entry_type,
            "size_bytes": size if entry_type == "file" else 0,
            "modified_utc": modified_utc,
        }
    )
    return storage.validate_record(record)


def stream(
    entries=(),
    *,
    collector: str = "wsl",
    warning_codes=(),
    completion: str | None = None,
) -> list[dict]:
    if collector == "wsl":
        capacity_alias = "wsl_root"
        traversal_alias = "wsl_src"
    else:
        capacity_alias = "windows_c"
        traversal_alias = "windows_downloads"
    records = [
        storage.capacity_scope_record(collector, capacity_alias, 1_000_000, 400_000),
        storage.traversal_scope_record(collector, traversal_alias),
        *entries,
    ]
    records.extend(
        storage.warning_record(collector, traversal_alias, code)
        for code in warning_codes
    )
    records.append(
        storage.completion_record(
            collector,
            traversal_alias,
            completion or ("incomplete" if warning_codes else "complete"),
        )
    )
    return records


class FakeScandir:
    def __init__(self, entries):
        self.entries = entries

    def __enter__(self):
        return iter(self.entries)

    def __exit__(self, exc_type, exc, traceback):
        return False


class PartialFailureIterator:
    def __init__(self, entries, error):
        self.entries = iter(entries)
        self.error = error

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self.entries)
        except StopIteration:
            raise self.error


class FakeEntry:
    def __init__(self, name, metadata=None, error=None):
        self.name = name
        self.metadata = metadata
        self.error = error

    def stat(self, *, follow_symlinks):
        if follow_symlinks:
            raise AssertionError("collector attempted to follow a link")
        if self.error:
            raise self.error
        return self.metadata


def synthetic_collection(
    root: Path,
    *,
    max_depth: int = storage.MAX_DEPTH,
    max_entries: int = storage.MAX_ENTRIES,
    mount_points=(),
    scandir=None,
) -> list[dict]:
    capacity = SimpleNamespace(
        f_frsize=4096,
        f_bsize=4096,
        f_blocks=100,
        f_bavail=25,
    )
    with ExitStack() as stack:
        stack.enter_context(mock.patch.object(storage, "WSL_TRAVERSAL_ROOT", root))
        stack.enter_context(mock.patch.object(storage, "MAX_DEPTH", max_depth))
        stack.enter_context(mock.patch.object(storage, "MAX_ENTRIES", max_entries))
        stack.enter_context(mock.patch.object(storage.os, "geteuid", return_value=1000))
        stack.enter_context(mock.patch.object(storage.os, "statvfs", return_value=capacity))
        stack.enter_context(
            mock.patch.object(
                storage,
                "read_linux_mount_points",
                return_value=frozenset(os.path.abspath(path) for path in mount_points),
            )
        )
        if scandir is not None:
            stack.enter_context(mock.patch.object(storage.os, "scandir", side_effect=scandir))
        return storage.collect_wsl_records()


def synthetic_tree(root: Path, **options) -> list[dict]:
    return synthetic_collection(root, **options)[1:]


class CollectorBoundaryTests(unittest.TestCase):
    def test_production_collector_has_no_root_or_gate_bypass_parameters(self):
        self.assertEqual(list(inspect.signature(storage.collect_wsl_records).parameters), [])
        self.assertFalse(hasattr(storage, "collect_tree_records"))
        with self.assertRaises(TypeError):
            storage.collect_wsl_records(traversal_root=Path("/tmp"))

    def test_allowed_root_validation_accepts_exact_synthetic_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(storage.validate_exact_local_root(root, root), root)

    def test_allowed_root_validation_rejects_different_root(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            with self.assertRaisesRegex(storage.CollectorError, "root_not_allowlisted"):
                storage.validate_exact_local_root(Path(first), Path(second))

    def test_allowed_root_validation_rejects_a_symlinked_parent(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            actual_parent = base / "actual"
            actual_parent.mkdir()
            (actual_parent / "root").mkdir()
            linked_parent = base / "linked"
            linked_parent.symlink_to(actual_parent, target_is_directory=True)
            lexical_root = linked_parent / "root"
            with self.assertRaisesRegex(storage.CollectorError, "root_not_directory"):
                storage.validate_exact_local_root(lexical_root, lexical_root)

    def test_root_execution_is_rejected_before_collection(self):
        with mock.patch.object(storage.os, "geteuid", return_value=0):
            with self.assertRaisesRegex(storage.CollectorError, "elevated_execution_rejected"):
                storage.require_non_elevated()

    def test_non_root_execution_is_accepted(self):
        with mock.patch.object(storage.os, "geteuid", return_value=1000):
            storage.require_non_elevated()

    def test_symlink_is_reported_and_never_followed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.txt"
            target.write_bytes(b"target")
            (root / "link.txt").symlink_to(target)
            records = synthetic_tree(root)
        warnings = [record for record in records if record["record_type"] == "warning"]
        paths = [
            record["relative_path"]
            for record in records
            if record["record_type"] == "entry"
        ]
        self.assertIn("symlink_skipped", {record["reason_code"] for record in warnings})
        self.assertNotIn("link.txt", paths)

    def test_cross_device_entry_is_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root_device = os.lstat(root).st_dev
            fake = FakeEntry(
                "foreign.bin",
                SimpleNamespace(
                    st_mode=stat.S_IFREG | 0o600,
                    st_dev=root_device + 1,
                    st_mtime=0,
                    st_size=10,
                ),
            )
            records = synthetic_tree(
                root, scandir=lambda unused: FakeScandir([fake])
            )
        self.assertIn(
            "cross_device_skipped",
            {record.get("reason_code") for record in records},
        )
        self.assertFalse(any(record["record_type"] == "entry" for record in records))

    def test_mount_point_is_not_traversed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mounted = root / "mounted"
            mounted.mkdir()
            (mounted / "inside.txt").write_bytes(b"not visited")
            records = synthetic_tree(root, mount_points=(mounted,))
        self.assertIn(
            "mount_point_skipped",
            {record.get("reason_code") for record in records},
        )
        self.assertNotIn(
            "mounted/inside.txt",
            {record.get("relative_path") for record in records},
        )
        self.assertNotIn(
            "mounted",
            {record.get("relative_path") for record in records},
        )

    def test_same_device_file_mount_is_skipped_before_stat_or_emission(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mounted_file = root / "mounted-file"
            fake = FakeEntry(
                mounted_file.name,
                error=AssertionError("mount-point metadata was accessed"),
            )
            records = synthetic_tree(
                root,
                mount_points=(mounted_file,),
                scandir=lambda unused: FakeScandir([fake]),
            )
        self.assertIn(
            "mount_point_skipped",
            {record.get("reason_code") for record in records},
        )
        self.assertNotIn(
            mounted_file.name,
            {record.get("relative_path") for record in records},
        )

    def test_linux_mountinfo_detects_same_device_bind_mounts(self):
        rows = [
            "25 1 8:1 / / rw,relatime - ext4 /dev/root rw\n",
            "31 25 8:1 /bound /synthetic/root/bind rw,relatime - ext4 /dev/root rw\n",
            "32 25 8:1 /space /synthetic/root/with\\040space rw,relatime - ext4 /dev/root rw\n",
        ]
        observed = storage.parse_linux_mount_points(rows)
        self.assertIn("/synthetic/root/bind", observed)
        self.assertIn("/synthetic/root/with space", observed)

    def test_allowlisted_root_that_is_a_bind_mount_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(storage.CollectorError, "root_is_mount"):
                synthetic_collection(root, mount_points=(root,))

    def test_directory_replaced_by_symlink_before_open_is_not_followed(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            child = root / "child"
            child.mkdir()
            outside_root = Path(outside)
            (outside_root / "outside.txt").write_bytes(b"must not be observed")
            displaced = root / "displaced"
            original_open = os.open
            replaced = False

            def replace_then_open(path, flags, *args, **kwargs):
                nonlocal replaced
                if path == "child" and kwargs.get("dir_fd") is not None and not replaced:
                    child.rename(displaced)
                    child.symlink_to(outside_root, target_is_directory=True)
                    replaced = True
                return original_open(path, flags, *args, **kwargs)

            with mock.patch.object(storage.os, "open", side_effect=replace_then_open):
                records = synthetic_tree(root)
        self.assertTrue(replaced)
        self.assertNotIn(
            "child/outside.txt",
            {record.get("relative_path") for record in records},
        )
        self.assertEqual(records[-1]["reason_code"], "incomplete")

    def test_protected_directory_name_is_not_traversed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (".ssh", "Documents"):
                protected = root / name
                protected.mkdir()
                (protected / "private-material").write_bytes(b"not read")
            records = synthetic_tree(root)
        self.assertIn(
            "protected_directory_skipped",
            {record.get("reason_code") for record in records},
        )
        self.assertNotIn(
            ".ssh/private-material",
            {record.get("relative_path") for record in records},
        )
        self.assertNotIn(
            "Documents/private-material",
            {record.get("relative_path") for record in records},
        )
        self.assertNotIn(
            ".ssh",
            {record.get("relative_path") for record in records},
        )
        self.assertNotIn(
            "Documents",
            {record.get("relative_path") for record in records},
        )

    def test_browser_and_password_manager_variants_are_skipped_before_emission(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            names = (
                "Google Chrome User Data",
                "MOZILLA FIREFOX PROFILES",
                "Microsoft Edge Profile Default",
                "BraveSoftware User Data",
                "1PASSWORD 8",
                "KeePassXC Databases",
            )
            for name in names:
                protected = root / name
                protected.mkdir()
                (protected / "vault.bin").write_bytes(b"not read")
            records = synthetic_tree(root)
        entry_paths = {
            record.get("relative_path")
            for record in records
            if record["record_type"] == "entry"
        }
        for name in names:
            with self.subTest(name=name):
                self.assertNotIn(name, entry_paths)
                self.assertNotIn(f"{name}/vault.bin", entry_paths)

    def test_protected_key_and_history_names_are_not_statted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root_device = os.lstat(root).st_dev
            protected_entries = [
                FakeEntry(
                    name,
                    metadata=SimpleNamespace(
                        st_mode=stat.S_IFREG | 0o600,
                        st_dev=root_device,
                        st_mtime=0,
                        st_size=10,
                    ),
                    error=AssertionError("protected metadata was accessed"),
                )
                for name in (
                    "id_rsa",
                    "id_ecdsa",
                    "id_ed25519",
                    "id_ecdsa_sk",
                    "id_ed25519_sk",
                    "id_ed25519_sk.backup",
                    "id_ecdsa_sk-copy",
                    ".bash_history.bak",
                    "certificate.pem.backup",
                    "putty.PPK",
                    "service.KEY~",
                )
            ]
            records = synthetic_tree(
                root, scandir=lambda unused: FakeScandir(protected_entries)
            )
        self.assertEqual(
            sum(record.get("reason_code") == "protected_file_skipped" for record in records),
            len(protected_entries),
        )
        self.assertFalse(any(record["record_type"] == "entry" for record in records))

    def test_maximum_depth_reports_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            child = root / "one"
            child.mkdir()
            (child / "unvisited.txt").write_bytes(b"bounded")
            records = synthetic_tree(root, max_depth=1)
        self.assertIn("max_depth_reached", {record.get("reason_code") for record in records})
        self.assertEqual(records[-1]["reason_code"], "incomplete")
        self.assertNotIn(
            "one/unvisited.txt",
            {record.get("relative_path") for record in records},
        )

    def test_maximum_entry_count_is_hard_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("a", "b", "c"):
                (root / name).write_bytes(name.encode("ascii"))
            records = synthetic_tree(root, max_entries=2)
        observed_entries = [record for record in records if record["record_type"] == "entry"]
        self.assertEqual(len(observed_entries), 2)
        self.assertIn("max_entries_reached", {record.get("reason_code") for record in records})

    def test_inaccessible_entry_has_only_a_bounded_pathless_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake = FakeEntry("sensitive-name.txt", error=PermissionError("raw path"))
            records = synthetic_tree(
                root, scandir=lambda unused: FakeScandir([fake])
            )
        warning = next(record for record in records if record["record_type"] == "warning")
        self.assertEqual(warning["reason_code"], "access_denied")
        self.assertNotIn("relative_path", warning)
        self.assertNotIn("sensitive-name", json.dumps(warning))

    def test_inaccessible_directory_enumeration_is_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def denied(unused):
                raise PermissionError("raw path is suppressed")

            records = synthetic_tree(root, scandir=denied)
        self.assertEqual(records[1]["reason_code"], "access_denied")
        self.assertEqual(records[-1]["reason_code"], "incomplete")

    def test_repeated_metadata_failures_consume_the_inspection_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            failing = [
                FakeEntry(f"failure-{index}", error=PermissionError("suppressed"))
                for index in range(20)
            ]
            records = synthetic_tree(
                root,
                max_entries=3,
                scandir=lambda unused: FakeScandir(failing),
            )
        warnings = [record for record in records if record["record_type"] == "warning"]
        self.assertEqual(len(warnings), 4)
        self.assertEqual(
            sum(record["reason_code"] == "access_denied" for record in warnings),
            3,
        )
        self.assertEqual(records[-1]["reason_code"], "incomplete")

    def test_partial_enumeration_failure_preserves_yielded_budget_and_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            child = root / "a-directory"
            child.mkdir()
            (child / "child.txt").write_bytes(b"child")
            (root / "z-file.txt").write_bytes(b"root")
            root_entries = list(os.scandir(root))
            original_scandir = os.scandir
            calls = 0

            def fail_after_root_candidates(directory_fd):
                nonlocal calls
                calls += 1
                if calls == 1:
                    return FakeScandir(
                        PartialFailureIterator(
                            root_entries,
                            PermissionError("raw path is suppressed"),
                        )
                    )
                return original_scandir(directory_fd)

            records = synthetic_tree(
                root,
                max_entries=3,
                scandir=fail_after_root_candidates,
            )
        entry_paths = {
            record["relative_path"]
            for record in records
            if record["record_type"] == "entry"
        }
        warning_reasons = {
            record["reason_code"]
            for record in records
            if record["record_type"] == "warning"
        }
        self.assertEqual(
            entry_paths,
            {"a-directory", "a-directory/child.txt", "z-file.txt"},
        )
        self.assertIn("access_denied", warning_reasons)
        self.assertIn("max_entries_reached", warning_reasons)
        self.assertEqual(records[-1]["reason_code"], "incomplete")

    def test_many_directories_with_failing_candidates_remain_globally_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("a", "b", "c"):
                (root / name).mkdir()
            original_scandir = os.scandir
            calls = 0

            def failing_children(directory_fd):
                nonlocal calls
                calls += 1
                if calls == 1:
                    return original_scandir(directory_fd)
                return FakeScandir(
                    [FakeEntry("denied.bin", error=PermissionError("suppressed"))]
                )

            records = synthetic_tree(
                root,
                max_entries=6,
                scandir=failing_children,
            )
        entries = [record for record in records if record["record_type"] == "entry"]
        warnings = [record for record in records if record["record_type"] == "warning"]
        self.assertEqual(len(entries), 3)
        self.assertLessEqual(len(warnings), 7)
        self.assertIn("max_entries_reached", {record["reason_code"] for record in warnings})
        self.assertEqual(records[-1]["reason_code"], "incomplete")

    def test_file_contents_are_never_opened(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "content.bin").write_bytes(b"content must remain unread")
            original_os_open = os.open

            def directory_only_open(path, flags, *args, **kwargs):
                self.assertTrue(flags & os.O_DIRECTORY, f"subject file was opened: {path}")
                self.assertFalse(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT))
                return original_os_open(path, flags, *args, **kwargs)

            with mock.patch.object(
                builtins,
                "open",
                side_effect=AssertionError("subject file contents were opened"),
            ), mock.patch.object(storage.os, "open", side_effect=directory_only_open):
                records = synthetic_tree(root)
        self.assertTrue(any(record["record_type"] == "entry" for record in records))

    def test_wsl_collector_uses_synthetic_capacity_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            records = synthetic_collection(root)
        self.assertEqual(records[0]["capacity_total_bytes"], 409_600)
        self.assertEqual(records[0]["capacity_free_bytes"], 102_400)

    def test_unexpected_collector_error_does_not_emit_raw_exception_text(self):
        stderr = io.StringIO()
        with mock.patch.object(
            storage,
            "collect_wsl_records",
            side_effect=OSError("sensitive path text"),
        ), redirect_stderr(stderr):
            result = storage.main(["collect-wsl"])
        self.assertEqual(result, 2)
        self.assertEqual(
            stderr.getvalue(),
            "storage_orientation_error:invalid_environment\n",
        )


class AnalysisTests(unittest.TestCase):
    def test_aggregates_are_deterministic(self):
        records = stream(
            [
                entry("folder", entry_type="directory"),
                entry("folder/a.txt", size=10, modified_utc=timestamp(10)),
                entry("b.jpg", size=20, modified_utc=timestamp(100)),
            ]
        )
        first = storage.analyze_records(records, as_of=AS_OF)
        second = storage.analyze_records(records, as_of=AS_OF)
        self.assertEqual(storage.sanitized_summary(first), storage.sanitized_summary(second))
        self.assertEqual(
            first["totals"],
            {
                "file_count": 2,
                "directory_count": 1,
                "file_size_bytes": 30,
                "skipped_or_error_count": 0,
                "incomplete_scope_count": 0,
            },
        )

    def test_top_twenty_order_is_size_then_identity(self):
        entries = [
            entry(f"file-{index:02d}.bin", size=index, modified_utc=timestamp(1))
            for index in range(25)
        ]
        analysis = storage.analyze_records(stream(entries), as_of=AS_OF)
        self.assertEqual(len(analysis["largest"]), 20)
        self.assertEqual(
            [record["size_bytes"] for record in analysis["largest"]],
            list(range(24, 4, -1)),
        )

    def test_age_bucket_boundaries(self):
        cases = {
            "future": AS_OF + timedelta(microseconds=1),
            "<30 days": AS_OF - timedelta(days=30) + timedelta(microseconds=1),
            "30–89": AS_OF - timedelta(days=30),
            "90–179": AS_OF - timedelta(days=90),
            "180–364": AS_OF - timedelta(days=180),
            "365+": AS_OF - timedelta(days=365),
        }
        for expected, value in cases.items():
            with self.subTest(expected=expected):
                observed = storage.age_bucket(
                    value.isoformat().replace("+00:00", "Z"), AS_OF
                )
                self.assertEqual(observed, expected)
        self.assertEqual(storage.age_bucket(None, AS_OF), "unknown")

    def test_seven_digit_windows_timestamp_keeps_100ns_age_precision(self):
        self.assertEqual(
            storage.age_bucket("2026-08-08T12:00:00.0000001Z", AS_OF),
            "future",
        )
        self.assertEqual(
            storage.age_bucket("2026-07-09T12:00:00.0000001Z", AS_OF),
            "<30 days",
        )

    def test_fixed_extension_categories(self):
        cases = {
            "paper.PDF": "document",
            "photo.JpG": "image",
            "sound.flac": "audio",
            "movie.mkv": "video",
            "bundle.tar.gz": "archive",
            "script.py": "code",
            "rows.jsonl": "data",
            "setup.EXE": "installer/executable",
            "opaque.custom": "other",
            "README": "no-extension",
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                self.assertEqual(storage.extension_category(path), expected)

    def test_duplicate_candidate_heuristic_is_not_a_duplicate_claim(self):
        records = stream(
            [
                entry("one/Report.PDF", size=100, modified_utc=timestamp(1)),
                entry("two/report.pdf", size=100, modified_utc=timestamp(2)),
                entry("three/report.pdf", size=101, modified_utc=timestamp(2)),
            ]
        )
        analysis = storage.analyze_records(records, as_of=AS_OF)
        self.assertEqual(len(analysis["duplicates"]), 1)
        self.assertEqual(analysis["duplicates"][0]["group_id"], "DUP-0001")
        self.assertEqual(len(analysis["duplicates"][0]["members"]), 2)
        report = storage.render_markdown(analysis)
        self.assertIn("Duplicate Candidates", report)
        self.assertIn("candidates based only", report)

    def test_candidate_ids_are_stable_across_entry_order(self):
        members = [
            entry("z/item.txt", size=8, modified_utc=timestamp(1)),
            entry("a/item.txt", size=8, modified_utc=timestamp(1)),
        ]
        first = storage.analyze_records(stream(members), as_of=AS_OF)
        second = storage.analyze_records(stream(list(reversed(members))), as_of=AS_OF)
        first_ids = {
            record["relative_path"]: record["candidate_id"] for record in first["largest"]
        }
        second_ids = {
            record["relative_path"]: record["candidate_id"] for record in second["largest"]
        }
        self.assertEqual(first_ids, second_ids)
        self.assertEqual(first["duplicates"][0]["group_id"], second["duplicates"][0]["group_id"])

    def test_empty_traversal_scope_has_explicit_zero_root_total(self):
        analysis = storage.analyze_records(stream([]), as_of=AS_OF)
        self.assertEqual(
            analysis["root_totals"]["wsl_src"],
            {"file_count": 0, "directory_count": 0, "file_size_bytes": 0},
        )
        self.assertIn("| `wsl_src` | 0 | 0 | 0 |", storage.render_markdown(analysis))

    def test_skipped_and_incomplete_counts_are_explicit(self):
        analysis = storage.analyze_records(
            stream([], warning_codes=("access_denied", "symlink_skipped")),
            as_of=AS_OF,
        )
        self.assertEqual(analysis["totals"]["skipped_or_error_count"], 2)
        self.assertEqual(analysis["totals"]["incomplete_scope_count"], 1)
        self.assertEqual(analysis["reason_counts"]["access_denied"], 1)

    def test_local_markdown_contains_paths_and_exact_scope(self):
        analysis = storage.analyze_records(
            stream([entry("local/example.txt", modified_utc=timestamp(1))]),
            as_of=AS_OF,
        )
        report = storage.render_markdown(analysis)
        expected_root = str(Path("/").joinpath("home", "aidenm727", "src"))
        self.assertIn(expected_root, report)
        self.assertIn("local/example&#46;txt", report)

    def test_markdown_path_rendering_neutralizes_hostile_syntax_and_bidi(self):
        hostile = "![x](javascript:alert)`_*\u202e.txt"
        analysis = storage.analyze_records(
            stream([entry(hostile, modified_utc=timestamp(1))]),
            as_of=AS_OF,
        )
        report = storage.render_markdown(analysis)
        self.assertNotIn(hostile, report)
        self.assertNotIn("\u202e", report)
        self.assertIn("U+202E", report)
        self.assertIn("&#33;&#91;x&#93;&#40;", report)

    def test_sanitizer_excludes_paths_names_extensions_and_timestamps(self):
        raw_timestamp = timestamp(10)
        records = stream(
            [
                entry("private-segment/identifying-name.supersecret", size=55, modified_utc=raw_timestamp),
                entry("other/IDENTIFYING-NAME.supersecret", size=55, modified_utc=raw_timestamp),
            ]
        )
        analysis = storage.analyze_records(records, as_of=AS_OF)
        analysis["unknown_passthrough"] = "must-not-appear"
        summary = storage.sanitized_summary(analysis)
        serialized = json.dumps(summary, sort_keys=True)
        for forbidden in (
            "private-segment",
            "identifying-name",
            ".supersecret",
            raw_timestamp,
            "must-not-appear",
        ):
            self.assertNotIn(forbidden.casefold(), serialized.casefold())
        self.assertIn("DUP-0001", serialized)
        self.assertEqual(summary["summary_kind"], "storage_orientation_sanitized")

    def test_sanitizer_omits_unexpected_fields_at_every_nested_level(self):
        analysis = storage.analyze_records(
            stream(
                [
                    entry("one/same.txt", size=5, modified_utc=timestamp(1)),
                    entry("two/SAME.txt", size=5, modified_utc=timestamp(1)),
                ]
            ),
            as_of=AS_OF,
        )
        secret = "must-not-cross-sanitizer"
        analysis["unexpected"] = secret
        analysis["findings"] = [{"detail": secret}]
        analysis["limitations"] = [{"detail": secret}]
        analysis["totals"]["unexpected"] = secret
        analysis["root_totals"]["wsl_src"]["unexpected"] = secret
        analysis["scopes"][0]["unexpected"] = secret
        analysis["categories"]["unexpected"] = {"detail": secret}
        analysis["categories"]["document"]["unexpected"] = secret
        analysis["ages"]["unexpected"] = {"detail": secret}
        analysis["ages"]["<30 days"]["unexpected"] = secret
        analysis["largest"][0]["unexpected"] = secret
        analysis["duplicates"][0]["unexpected"] = secret
        analysis["duplicates"][0]["members"][0]["unexpected"] = secret
        serialized = json.dumps(storage.sanitized_summary(analysis), sort_keys=True)
        self.assertNotIn(secret, serialized)
        for forbidden_key in ("unexpected", "findings", "root_totals"):
            self.assertNotIn(f'"{forbidden_key}"', serialized)

    def test_sanitizer_fails_closed_on_unallowlisted_limitation(self):
        analysis = storage.analyze_records(stream([]), as_of=AS_OF)
        analysis["reason_counts"]["private-finding"] = 1
        with self.assertRaisesRegex(storage.StorageOrientationError, "limitation"):
            storage.sanitized_summary(analysis)


class RecordContractTests(unittest.TestCase):
    def assert_invalid(self, records, message):
        with self.assertRaisesRegex(storage.StorageOrientationError, message):
            storage.validate_stream(records)

    def test_unknown_fields_fail_closed(self):
        record = entry("safe.txt")
        record["unexpected"] = "value"
        with self.assertRaisesRegex(storage.StorageOrientationError, "fields are not exact"):
            storage.validate_record(record)

    def test_malformed_json_is_rejected(self):
        with self.assertRaisesRegex(storage.StorageOrientationError, "malformed JSON"):
            storage.parse_jsonl(["{not-json}\n"])

    def test_duplicate_json_keys_are_rejected(self):
        with self.assertRaisesRegex(storage.StorageOrientationError, "duplicate JSON"):
            storage.parse_jsonl(['{"schema_version":1,"schema_version":1}\n'])

    def test_mixed_schema_versions_are_rejected(self):
        records = stream([])
        records[1] = dict(records[1], schema_version=2)
        self.assert_invalid(records, "mixed schema_version")

    def test_duplicate_completion_is_rejected(self):
        records = stream([])
        records.append(storage.completion_record("wsl", "wsl_src", "complete"))
        self.assert_invalid(records, "after collector completion")

    def test_exact_duplicate_logical_entry_is_rejected(self):
        duplicate = entry("same/path.txt")
        self.assert_invalid(
            stream([duplicate, dict(duplicate)]),
            "duplicate logical entry path",
        )

    def test_conflicting_entry_types_for_one_logical_path_are_rejected(self):
        self.assert_invalid(
            stream(
                [
                    entry("same/path"),
                    entry("same/path", entry_type="directory"),
                ]
            ),
            "duplicate logical entry path",
        )

    def test_windows_case_only_logical_duplicate_is_rejected(self):
        self.assert_invalid(
            stream(
                [
                    entry(
                        "Folder/Name.txt",
                        collector="windows",
                        alias="windows_downloads",
                    ),
                    entry(
                        "folder/name.TXT",
                        collector="windows",
                        alias="windows_downloads",
                    ),
                ],
                collector="windows",
            ),
            "duplicate logical entry path",
        )

    def test_wsl_case_distinct_logical_paths_remain_distinct(self):
        records = stream([entry("Name.txt"), entry("name.txt")])
        storage.validate_stream(records)
        self.assertEqual(
            storage.analyze_records(records, as_of=AS_OF)["totals"]["file_count"],
            2,
        )

    def test_incomplete_stream_without_completion_is_rejected(self):
        records = stream([])[:-1]
        self.assert_invalid(records, "stream is incomplete")

    def test_entry_before_scope_is_rejected(self):
        records = stream([entry("early.txt")])
        records[1], records[2] = records[2], records[1]
        self.assert_invalid(records, "before its scope")

    def test_scope_after_data_is_rejected(self):
        records = stream([entry("early.txt")])
        records[0], records[1], records[2] = records[1], records[2], records[0]
        self.assert_invalid(records, "out of order")

    def test_complete_stream_cannot_contain_warning(self):
        records = stream([], warning_codes=("access_denied",), completion="complete")
        self.assert_invalid(records, "complete stream contains warnings")

    def test_per_scope_entry_and_warning_caps_fail_closed(self):
        too_many_entries = stream(
            [entry("a"), entry("b"), entry("c")],
            completion="complete",
        )
        with mock.patch.object(storage, "MAX_ENTRIES", 2):
            self.assert_invalid(too_many_entries, "entry scope exceeds")

        too_many_warnings = stream(
            [],
            warning_codes=(
                "access_denied",
                "metadata_unavailable",
                "enumeration_failed",
                "symlink_skipped",
            ),
        )
        with mock.patch.object(storage, "MAX_WARNING_RECORDS_PER_SCOPE", 3):
            self.assert_invalid(too_many_warnings, "warning scope exceeds")

    def test_two_maximum_size_collector_streams_fit_the_global_bound(self):
        maximum_entries = 2
        maximum_warnings = 3

        def maximum_collector(collector):
            alias = "wsl_src" if collector == "wsl" else "windows_downloads"
            entries = [
                entry(f"file-{index}.bin", collector=collector, alias=alias)
                for index in range(maximum_entries)
            ]
            return stream(
                entries,
                collector=collector,
                warning_codes=(
                    "access_denied",
                    "metadata_unavailable",
                    "max_entries_reached",
                ),
            )

        records = maximum_collector("wsl") + maximum_collector("windows")
        with mock.patch.multiple(
            storage,
            MAX_ENTRIES=maximum_entries,
            MAX_WARNING_RECORDS_PER_SCOPE=maximum_warnings,
            MAX_RECORDS_PER_COLLECTOR=8,
            MAX_RECORDS=16,
        ):
            serialized = storage.serialize_jsonl(records)
            self.assertEqual(storage.parse_jsonl(io.StringIO(serialized)), records)
            self.assertEqual(len(records), storage.MAX_RECORDS)

    def test_global_record_limit_fails_before_unbounded_accumulation(self):
        records = stream([])
        lines = [json.dumps(record) + "\n" for record in records]
        with mock.patch.object(storage, "MAX_RECORDS", len(records) - 1):
            with self.assertRaisesRegex(storage.StorageOrientationError, "bounded count"):
                storage.parse_jsonl(lines)

    def test_relative_paths_are_canonical(self):
        for relative_path in ("/absolute", "../parent", "a\\b", "a//b"):
            with self.subTest(relative_path=relative_path):
                raw = storage._base_record("entry", "wsl", "wsl_src")
                raw.update(
                    {
                        "relative_path": relative_path,
                        "entry_type": "file",
                        "size_bytes": 1,
                        "modified_utc": None,
                    }
                )
                with self.assertRaises(storage.StorageOrientationError):
                    storage.validate_record(raw)

    def test_power_shell_jsonl_shape_and_timestamp_are_compatible(self):
        lines = [
            '{"schema_version":1,"record_type":"scope","collector":"windows","root_alias":"windows_c","root_kind":"capacity","capacity_total_bytes":1000,"capacity_free_bytes":250}',
            '{"schema_version":1,"record_type":"scope","collector":"windows","root_alias":"windows_downloads","root_kind":"traversal","capacity_total_bytes":null,"capacity_free_bytes":null}',
            '{"schema_version":1,"record_type":"entry","collector":"windows","root_alias":"windows_downloads","root_kind":"traversal","relative_path":"synthetic/file.txt","entry_type":"file","size_bytes":12,"modified_utc":"2026-08-08T12:00:00.0000000Z"}',
            '{"schema_version":1,"record_type":"completion","collector":"windows","root_alias":"windows_downloads","root_kind":"traversal","reason_code":"complete"}',
        ]
        records = storage.parse_jsonl(line + "\n" for line in lines)
        analysis = storage.analyze_records(records, as_of=AS_OF)
        self.assertEqual(analysis["totals"]["file_count"], 1)

    def test_jsonl_round_trip_is_deterministic(self):
        records = stream([entry("safe.txt", modified_utc=timestamp(1))])
        serialized = storage.serialize_jsonl(records)
        self.assertEqual(storage.parse_jsonl(io.StringIO(serialized)), records)


if __name__ == "__main__":
    unittest.main()
