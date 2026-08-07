import dataclasses
import hashlib
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from atlas.platform.context_compilation.canonical_json import canonicalize
from atlas.platform.context_compilation.digests import (
    snapshot_fingerprint,
    snapshot_fingerprint_surface,
)
from atlas.platform.context_compilation.models import (
    ImmutableBlob,
    ModelValueError,
    ProtectedReferenceIdentity,
    RepositoryIdentityEvidence,
    RepositorySnapshot,
    deep_freeze,
)
from atlas.platform.context_compilation import snapshot as snapshot_module
from atlas.platform.context_compilation.snapshot import (
    SNAPSHOT_MODE,
    BlobLookupError,
    ObjectFormatError,
    ProtectedReferenceError,
    RepositoryIdentityError,
    RepositoryPathError,
    RepositoryStateError,
    RevisionError,
    SnapshotEnvironmentError,
    TreeMismatchError,
    normalize_repository_path,
    read_snapshot_blob,
    resolve_snapshot,
)


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_REPOSITORY_IDENTITY = "github.com/aidenm727/aiden-platform"
OLD_CANONICAL_REPOSITORY_IDENTITY = "github.com/aidenm727/t430-homelab"
HISTORICAL_COMMIT = "79eef80af3d5969ece7eb9fe7f802be35575f450"
HISTORICAL_TREE = "3d2853517e64209cffde91766a62e9f70ceb2e47"
PROTECTED_REF = "refs/heads/wip/distinctness-foundation-calibration"
PROTECTED_OBJECT = "fcbc5957b89fe65a4313a3c23eb814e02a014698"
CURRENT_ORIGINS = (
    "git@github.com:aidenm727/aiden-platform.git",
    "ssh://git@github.com/aidenm727/aiden-platform.git",
    "https://github.com/aidenm727/aiden-platform.git",
    "https://github.com/aidenm727/aiden-platform",
)
LEGACY_ORIGINS = (
    "git@github.com:aidenm727/t430-homelab.git",
    "ssh://git@github.com/aidenm727/t430-homelab.git",
    "https://github.com/aidenm727/t430-homelab.git",
    "https://github.com/aidenm727/t430-homelab",
)


def fixture_git(
    repository: Path | None,
    *arguments: str,
    input_bytes: bytes | None = None,
    check: bool = True,
    extra_environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[bytes]:
    command = ["git"]
    if repository is not None:
        command.extend(("-C", str(repository)))
    command.extend(arguments)
    environment = os.environ.copy()
    if extra_environment:
        environment.update(extra_environment)
    result = subprocess.run(
        command,
        input=input_bytes,
        env=environment,
        capture_output=True,
        text=False,
        shell=False,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"fixture Git command failed: {arguments[0]} ({result.returncode})"
        )
    return result


class ContextSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.workspace = Path(self.temporary.name)
        self.repository = self.workspace / "target"
        fixture_git(
            None,
            "clone",
            "--no-local",
            "--no-hardlinks",
            str(ROOT),
            str(self.repository),
        )
        fixture_git(
            self.repository,
            "remote",
            "set-url",
            "origin",
            CURRENT_ORIGINS[2],
        )
        fixture_git(
            self.repository,
            "update-ref",
            PROTECTED_REF,
            PROTECTED_OBJECT,
        )
        fixture_git(self.repository, "config", "user.name", "Snapshot Fixture")
        fixture_git(
            self.repository,
            "config",
            "user.email",
            "snapshot-fixture@example.invalid",
        )
        self.assertEqual(self._status(), b"")

    def _status(self, repository: Path | None = None) -> bytes:
        return fixture_git(
            repository or self.repository,
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
            "--ignore-submodules=none",
        ).stdout

    def _protected(self, **changes: object) -> list[dict[str, object]]:
        value: dict[str, object] = {
            "name": PROTECTED_REF,
            "expected_object": PROTECTED_OBJECT,
            "authoritatively_targeted": False,
            "selection": "forbidden",
        }
        value.update(changes)
        return [value]

    def _resolve(self, **changes: object) -> RepositorySnapshot:
        arguments: dict[str, object] = {
            "repository_identity": CANONICAL_REPOSITORY_IDENTITY,
            "requested_revision": HISTORICAL_COMMIT,
            "expected_tree": HISTORICAL_TREE,
            "protected_references": self._protected(),
        }
        arguments.update(changes)
        return resolve_snapshot(self.repository, **arguments)  # type: ignore[arg-type]

    def _synthetic_snapshot(self) -> RepositorySnapshot:
        regular = fixture_git(
            self.repository,
            "hash-object",
            "-w",
            "--stdin",
            input_bytes=b"regular bytes\x00remain raw\n",
        ).stdout.strip()
        executable = fixture_git(
            self.repository,
            "hash-object",
            "-w",
            "--stdin",
            input_bytes=b"#!/bin/sh\nexit 0\n",
        ).stdout.strip()
        link = fixture_git(
            self.repository,
            "hash-object",
            "-w",
            "--stdin",
            input_bytes=b"regular.txt",
        ).stdout.strip()
        nested = fixture_git(
            self.repository,
            "hash-object",
            "-w",
            "--stdin",
            input_bytes=b"nested\n",
        ).stdout.strip()
        subtree_input = b"100644 blob " + nested + b"\tnested.txt\0"
        subtree = fixture_git(
            self.repository, "mktree", "-z", input_bytes=subtree_input
        ).stdout.strip()
        entries = (
            b"100755 blob " + executable + b"\texec.sh\0"
            b"040000 tree " + subtree + b"\tfolder\0"
            b"160000 commit " + HISTORICAL_COMMIT.encode() + b"\tgitlink\0"
            b"120000 blob " + link + b"\tlink\0"
            b"100644 blob " + regular + b"\tregular.txt\0"
        )
        tree = fixture_git(
            self.repository, "mktree", "-z", input_bytes=entries
        ).stdout.strip().decode("ascii")
        commit = fixture_git(
            self.repository, "commit-tree", tree, "-m", "synthetic snapshot"
        ).stdout.strip().decode("ascii")
        return self._resolve(requested_revision=commit, expected_tree=tree)

    def _target_evidence(self) -> tuple[bytes, bytes, bytes, bytes]:
        index = (self.repository / ".git/index").read_bytes()
        refs = fixture_git(
            self.repository,
            "for-each-ref",
            "--format=%(refname):%(objectname)",
        ).stdout
        objects = fixture_git(self.repository, "count-objects", "-v").stdout
        return index, refs, objects, self._status()

    def _marker_hook(self, name: str) -> tuple[Path, Path]:
        marker = self.workspace / f"{name}.marker"
        hook = self.workspace / f"{name}.sh"
        hook.write_text(
            f"#!/bin/sh\n: > '{marker}'\n",
            encoding="utf-8",
        )
        hook.chmod(0o700)
        return hook, marker

    def _set_local_config(self, key: str, value: str) -> None:
        fixture_git(
            None,
            "config",
            "--file",
            str(self.repository / ".git/config"),
            key,
            value,
        )

    def _unset_local_config(self, key: str) -> None:
        fixture_git(
            None,
            "config",
            "--file",
            str(self.repository / ".git/config"),
            "--unset-all",
            key,
            check=False,
        )

    def test_exact_historical_commit_and_tree_resolution(self) -> None:
        snapshot = self._resolve()
        self.assertEqual(snapshot.commit, HISTORICAL_COMMIT)
        self.assertEqual(snapshot.requested_revision, HISTORICAL_COMMIT)
        self.assertEqual(snapshot.tree, HISTORICAL_TREE)
        self.assertEqual(snapshot.object_format, "sha1")
        self.assertEqual(snapshot.snapshot_mode, SNAPSHOT_MODE)

    def test_repeatable_snapshot_fingerprint_and_exact_surface(self) -> None:
        surface = snapshot_fingerprint_surface(
            CANONICAL_REPOSITORY_IDENTITY,
            "sha1",
            HISTORICAL_COMMIT,
            HISTORICAL_TREE,
            SNAPSHOT_MODE,
        )
        self.assertEqual(
            surface,
            {
                "repository_identity": CANONICAL_REPOSITORY_IDENTITY,
                "object_format": "sha1",
                "commit": HISTORICAL_COMMIT,
                "tree": HISTORICAL_TREE,
                "snapshot_mode": SNAPSHOT_MODE,
            },
        )
        independent = hashlib.sha256(canonicalize(surface)).hexdigest()
        calculated = snapshot_fingerprint(**surface)
        self.assertEqual(calculated.value, independent)
        self.assertEqual(
            independent,
            "0c97cda6c0684fe846186766b75c760dade350eae294a1a7b84a73abe6ad2a14",
        )
        self.assertEqual(self._resolve().fingerprint, calculated)
        self.assertEqual(self._resolve().fingerprint, calculated)

    def test_all_current_origin_forms(self) -> None:
        for origin in CURRENT_ORIGINS:
            with self.subTest(origin=origin):
                fixture_git(self.repository, "remote", "set-url", "origin", origin)
                snapshot = self._resolve()
                self.assertEqual(snapshot.repository.origin_urls, (origin,))
                self.assertEqual(
                    snapshot.repository.normalized_identity,
                    CANONICAL_REPOSITORY_IDENTITY,
                )

    def test_all_legacy_origin_forms_normalize_to_current_identity(self) -> None:
        for origin in LEGACY_ORIGINS:
            with self.subTest(origin=origin):
                fixture_git(self.repository, "remote", "set-url", "origin", origin)
                snapshot = self._resolve()
                self.assertEqual(
                    snapshot.repository.requested_identity,
                    CANONICAL_REPOSITORY_IDENTITY,
                )
                self.assertEqual(snapshot.repository.origin_urls, (origin,))
                self.assertEqual(
                    snapshot.repository.normalized_identity,
                    CANONICAL_REPOSITORY_IDENTITY,
                )

    def test_duplicate_accepted_origins_are_deterministic(self) -> None:
        fixture_git(
            self.repository, "config", "--add", "remote.origin.url", LEGACY_ORIGINS[0]
        )
        fixture_git(
            self.repository, "config", "--add", "remote.origin.url", CURRENT_ORIGINS[2]
        )
        fixture_git(
            self.repository, "config", "--add", "remote.origin.url", CURRENT_ORIGINS[1]
        )
        snapshot = self._resolve()
        self.assertEqual(
            snapshot.repository.origin_urls,
            (CURRENT_ORIGINS[2], LEGACY_ORIGINS[0], CURRENT_ORIGINS[1]),
        )

    def test_absent_origin_is_rejected(self) -> None:
        fixture_git(
            self.repository,
            "config",
            "--unset-all",
            "remote.origin.url",
            check=False,
        )
        with self.assertRaises(RepositoryIdentityError):
            self._resolve()

    def test_empty_origin_is_rejected(self) -> None:
        fixture_git(self.repository, "config", "remote.origin.url", "")
        with self.assertRaises(RepositoryIdentityError):
            self._resolve()

    def test_conflicting_origin_identities_are_rejected(self) -> None:
        fixture_git(
            self.repository,
            "config",
            "--add",
            "remote.origin.url",
            "https://github.com/another/repository.git",
        )
        with self.assertRaises(RepositoryIdentityError):
            self._resolve()

    def test_unsupported_origin_boundaries_are_rejected(self) -> None:
        invalid = (
            "https://gitlab.com/aidenm727/aiden-platform.git",
            "https://github.com/other/aiden-platform.git",
            "https://github.com/aidenm727/other.git",
            "https://github.com/aidenm727/aiden-platform.git/extra",
            "https://github.com/aidenm727/aiden-platform.git?x=1",
            "https://github.com/aidenm727/aiden-platform.git#x",
            "https://user@github.com/aidenm727/aiden-platform.git",
            "https://github.com:443/aidenm727/aiden-platform.git",
            "ssh://other@github.com/aidenm727/aiden-platform.git",
        )
        for origin in invalid:
            with self.subTest(origin=origin):
                fixture_git(self.repository, "remote", "set-url", "origin", origin)
                with self.assertRaises(RepositoryIdentityError):
                    self._resolve()

    def test_repository_identity_disagreement_is_rejected(self) -> None:
        with self.assertRaises(RepositoryIdentityError):
            self._resolve(repository_identity="github.com/other/repository")

    def test_old_canonical_identity_is_rejected_as_current_request(self) -> None:
        with self.assertRaises(RepositoryIdentityError):
            self._resolve(repository_identity=OLD_CANONICAL_REPOSITORY_IDENTITY)

    def test_revision_syntax_boundaries_are_rejected(self) -> None:
        invalid = (
            "main",
            "v1",
            HISTORICAL_COMMIT[:12],
            f"{HISTORICAL_COMMIT}^",
            f"{HISTORICAL_COMMIT}@{{0}}",
            f"{HISTORICAL_COMMIT}^{{commit}}",
            "--all",
            HISTORICAL_COMMIT.upper(),
            "g" * 40,
            "",
        )
        for revision in invalid:
            with self.subTest(revision=revision), self.assertRaises(RevisionError):
                self._resolve(requested_revision=revision)

    def test_non_commit_requested_revision_is_rejected(self) -> None:
        blob = fixture_git(
            self.repository,
            "rev-parse",
            f"{HISTORICAL_COMMIT}:docs/current-mission.md",
        ).stdout.strip().decode("ascii")
        with self.assertRaises(RevisionError):
            self._resolve(requested_revision=blob)

    def test_expected_tree_malformed_and_mismatch_are_rejected(self) -> None:
        for tree in ("main", HISTORICAL_TREE.upper(), "0" * 39):
            with self.subTest(tree=tree), self.assertRaises(TreeMismatchError):
                self._resolve(expected_tree=tree)
        with self.assertRaises(TreeMismatchError):
            self._resolve(expected_tree="0" * 40)

    def test_dirty_unstaged_tracked_state_is_rejected(self) -> None:
        (self.repository / "README.md").write_text("dirty\n", encoding="utf-8")
        with self.assertRaises(RepositoryStateError):
            self._resolve()

    def test_dirty_staged_state_is_rejected(self) -> None:
        (self.repository / "README.md").write_text("staged\n", encoding="utf-8")
        fixture_git(self.repository, "add", "README.md")
        with self.assertRaises(RepositoryStateError):
            self._resolve()

    def test_untracked_state_is_rejected(self) -> None:
        (self.repository / "untracked.txt").write_bytes(b"untracked\n")
        with self.assertRaises(RepositoryStateError):
            self._resolve()

    def test_dirty_submodule_state_is_rejected_explicitly(self) -> None:
        source = self.workspace / "submodule-source"
        source.mkdir()
        fixture_git(source, "init")
        fixture_git(source, "config", "user.name", "Submodule Fixture")
        fixture_git(source, "config", "user.email", "submodule@example.invalid")
        (source / "tracked.txt").write_text("clean\n", encoding="utf-8")
        fixture_git(source, "add", "tracked.txt")
        fixture_git(source, "commit", "-m", "submodule fixture")
        fixture_git(
            self.repository,
            "-c",
            "protocol.file.allow=always",
            "submodule",
            "add",
            str(source),
            "vendor/submodule",
        )
        fixture_git(self.repository, "commit", "-am", "add fixture submodule")
        nested = self.repository / "vendor/submodule/tracked.txt"
        nested.write_text("dirty\n", encoding="utf-8")
        self.assertNotEqual(self._status(), b"")
        with self.assertRaises(RepositoryStateError):
            self._resolve()

    def test_bare_repository_is_rejected(self) -> None:
        bare = self.workspace / "bare.git"
        fixture_git(
            None,
            "clone",
            "--bare",
            "--no-local",
            "--no-hardlinks",
            str(ROOT),
            str(bare),
        )
        with self.assertRaises(RepositoryStateError):
            resolve_snapshot(
                bare,
                repository_identity=CANONICAL_REPOSITORY_IDENTITY,
                requested_revision=HISTORICAL_COMMIT,
                expected_tree=HISTORICAL_TREE,
                protected_references=self._protected(),
            )

    def test_sha256_repository_is_rejected_when_git_supports_it(self) -> None:
        sha256_repository = self.workspace / "sha256"
        result = fixture_git(
            None,
            "init",
            "--object-format=sha256",
            str(sha256_repository),
            check=False,
        )
        if result.returncode != 0:
            self.fail("installed Git lacks required SHA-256 repository support")
        fixture_git(
            sha256_repository,
            "remote",
            "add",
            "origin",
            CURRENT_ORIGINS[2],
        )
        with self.assertRaises(ObjectFormatError):
            resolve_snapshot(
                sha256_repository,
                repository_identity=CANONICAL_REPOSITORY_IDENTITY,
                requested_revision="0" * 40,
                expected_tree="0" * 40,
                protected_references=[],
            )

    def test_replacement_reference_is_rejected(self) -> None:
        current = fixture_git(self.repository, "rev-parse", "HEAD").stdout.strip()
        fixture_git(
            self.repository,
            "replace",
            HISTORICAL_COMMIT,
            current.decode("ascii"),
        )
        with mock.patch.object(
            snapshot_module, "_run_git", wraps=snapshot_module._run_git
        ) as spy, self.assertRaises(RepositoryStateError):
            self._resolve()
        commands = [call.args[1:] for call in spy.call_args_list]
        self.assertFalse(any(command[0] == "cat-file" for command in commands))
        self.assertFalse(
            any(
                current.decode("ascii") in argument
                for command in commands
                for argument in command
            )
        )

    def test_graft_metadata_is_rejected(self) -> None:
        graft = self.repository / ".git/info/grafts"
        graft.write_text(f"{HISTORICAL_COMMIT}\n", encoding="ascii")
        with self.assertRaises(RepositoryStateError):
            self._resolve()

    def test_ambient_alternate_is_rejected_before_git(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"GIT_ALTERNATE_OBJECT_DIRECTORIES": str(self.repository / ".git/objects")},
        ), mock.patch.object(snapshot_module, "_run_git", wraps=snapshot_module._run_git) as spy:
            with self.assertRaises(SnapshotEnvironmentError):
                self._resolve()
            spy.assert_not_called()

    def test_file_alternate_is_rejected(self) -> None:
        alternate = self.repository / ".git/objects/info/alternates"
        alternate.write_text(str(self.repository / ".git/objects") + "\n", encoding="utf-8")
        with self.assertRaises(RepositoryStateError):
            self._resolve()

    def test_http_alternate_is_rejected(self) -> None:
        alternate = self.repository / ".git/objects/info/http-alternates"
        alternate.write_text("https://example.invalid/objects\n", encoding="utf-8")
        with self.assertRaises(RepositoryStateError):
            self._resolve()

    def test_injected_git_configuration_is_rejected(self) -> None:
        cases = (
            {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.bare", "GIT_CONFIG_VALUE_0": "true"},
            {"GIT_CONFIG": str(self.workspace / "config")},
            {"GIT_CONFIG_KEY_9": "core.worktree"},
            {"GIT_CONFIG_VALUE_9": "outside"},
        )
        for environment in cases:
            with self.subTest(environment=tuple(environment)), mock.patch.dict(
                os.environ, environment
            ), self.assertRaises(SnapshotEnvironmentError):
                self._resolve()

    def test_other_ambient_git_control_variables_are_rejected(self) -> None:
        names = (
            "GIT_DIR",
            "GIT_WORK_TREE",
            "GIT_COMMON_DIR",
            "GIT_INDEX_FILE",
            "GIT_OBJECT_DIRECTORY",
            "GIT_CONFIG_SYSTEM",
            "GIT_CONFIG_GLOBAL",
            "GIT_CONFIG_NOSYSTEM",
            "GIT_NAMESPACE",
            "GIT_SHALLOW_FILE",
            "GIT_QUARANTINE_PATH",
        )
        for name in names:
            with self.subTest(name=name), mock.patch.dict(
                os.environ, {name: "forbidden"}
            ), self.assertRaises(SnapshotEnvironmentError):
                self._resolve()

    def test_local_executable_fsmonitor_is_rejected_without_execution(self) -> None:
        hook, marker = self._marker_hook("fsmonitor")
        self._set_local_config("core.fsMonitor", str(hook))
        with mock.patch.object(
            snapshot_module, "_run_git", wraps=snapshot_module._run_git
        ) as spy, self.assertRaisesRegex(
            RepositoryStateError, "repository-local configuration is unsafe"
        ):
            self._resolve()
        self.assertFalse(marker.exists())
        commands = [call.args[1:] for call in spy.call_args_list]
        self.assertEqual(
            commands,
            [
                (
                    "config",
                    "--local",
                    "--no-includes",
                    "--null",
                    "--name-only",
                    "--list",
                )
            ],
        )

    def test_local_include_is_rejected_without_application_or_execution(self) -> None:
        hook, marker = self._marker_hook("included-fsmonitor")
        included = self.workspace / "included.config"
        included.write_text(
            f"[core]\n\tfsmonitor = {hook}\n",
            encoding="utf-8",
        )
        self._set_local_config("include.path", str(included))
        with mock.patch.object(
            snapshot_module, "_run_git", wraps=snapshot_module._run_git
        ) as spy, self.assertRaises(RepositoryStateError):
            self._resolve()
        self.assertFalse(marker.exists())
        commands = [call.args[1:] for call in spy.call_args_list]
        self.assertEqual(
            commands[0],
            (
                "config",
                "--local",
                "--no-includes",
                "--null",
                "--name-only",
                "--list",
            ),
        )
        self.assertFalse(any(command[0] == "status" for command in commands))

    def test_local_external_filters_are_rejected_without_execution(self) -> None:
        for suffix in ("clean", "process"):
            with self.subTest(suffix=suffix):
                hook, marker = self._marker_hook(f"filter-{suffix}")
                key = f"filter.danger.{suffix}"
                self._set_local_config(key, str(hook))
                try:
                    with self.assertRaises(RepositoryStateError):
                        self._resolve()
                    self.assertFalse(marker.exists())
                finally:
                    self._unset_local_config(key)

    def test_local_external_diff_and_textconv_configuration_is_rejected(self) -> None:
        cases = (
            "diff.external",
            "diff.danger.command",
            "diff.danger.textconv",
        )
        for key in cases:
            with self.subTest(key=key):
                hook, marker = self._marker_hook(key.replace(".", "-"))
                self._set_local_config(key, str(hook))
                try:
                    with self.assertRaises(RepositoryStateError):
                        self._resolve()
                    self.assertFalse(marker.exists())
                finally:
                    self._unset_local_config(key)

    def test_other_unsafe_local_configuration_classes_are_rejected(self) -> None:
        cases = (
            "core.hooksPath",
            "core.worktree",
            "core.untrackedCache",
            "extensions.worktreeConfig",
            "status.submoduleSummary",
            "submodule.recurse",
            "filter.danger.smudge",
            "filter.danger.required",
        )
        for key in cases:
            with self.subTest(key=key):
                value = str(self.workspace) if key == "core.worktree" else "true"
                self._set_local_config(key, value)
                try:
                    with self.assertRaises(
                        (RepositoryStateError, SnapshotEnvironmentError)
                    ):
                        self._resolve()
                finally:
                    self._unset_local_config(key)

    def test_ordinary_safe_local_configuration_remains_accepted(self) -> None:
        fixture_git(
            self.repository,
            "config",
            "branch.main.description",
            "fixture branch",
        )
        fixture_git(self.repository, "config", "core.abbrev", "12")
        snapshot = self._resolve()
        self.assertEqual(snapshot.commit, HISTORICAL_COMMIT)

    def test_regular_100644_blob_read_is_exact(self) -> None:
        snapshot = self._synthetic_snapshot()
        blob = read_snapshot_blob(self.repository, snapshot, "regular.txt")
        self.assertEqual(blob.mode, "100644")
        self.assertEqual(blob.content, b"regular bytes\x00remain raw\n")
        self.assertEqual(blob.path, "regular.txt")

    def test_executable_100755_blob_read_is_exact(self) -> None:
        snapshot = self._synthetic_snapshot()
        blob = read_snapshot_blob(self.repository, snapshot, "exec.sh")
        self.assertEqual(blob.mode, "100755")
        self.assertEqual(blob.content, b"#!/bin/sh\nexit 0\n")

    def test_missing_blob_path_is_rejected(self) -> None:
        with self.assertRaises(BlobLookupError):
            read_snapshot_blob(self.repository, self._resolve(), "missing.txt")

    def test_repository_path_attack_boundaries_are_rejected(self) -> None:
        invalid: tuple[object, ...] = (
            "",
            "/absolute",
            "C:/absolute",
            "C:\\absolute",
            "\\\\server\\share",
            "//server/share",
            "leading//empty",
            "trailing/",
            "./dot",
            "a/./dot",
            "../parent",
            "a/../parent",
            "back\\slash",
            "nul\0path",
            "surrogate\ud800",
            1,
            None,
        )
        for path in invalid:
            with self.subTest(path=repr(path)), self.assertRaises(RepositoryPathError):
                normalize_repository_path(path)  # type: ignore[arg-type]

    def test_valid_repository_path_is_returned_without_rewrite(self) -> None:
        for path in ("docs/current-mission.md", "é/e\u0301/Case.txt"):
            with self.subTest(path=path):
                result = normalize_repository_path(path)
                self.assertEqual(result, path)
                self.assertIs(result, path)

    def test_symlink_is_rejected(self) -> None:
        with self.assertRaises(BlobLookupError):
            read_snapshot_blob(self.repository, self._synthetic_snapshot(), "link")

    def test_gitlink_is_rejected(self) -> None:
        with self.assertRaises(BlobLookupError):
            read_snapshot_blob(self.repository, self._synthetic_snapshot(), "gitlink")

    def test_tree_object_is_rejected(self) -> None:
        with self.assertRaises(BlobLookupError):
            read_snapshot_blob(self.repository, self._synthetic_snapshot(), "folder")

    def test_protected_reference_match_is_non_blocking(self) -> None:
        identity = self._resolve().protected_references[0]
        self.assertEqual(identity.name, PROTECTED_REF)
        self.assertEqual(identity.expected_object, PROTECTED_OBJECT)
        self.assertEqual(identity.actual_object, PROTECTED_OBJECT)
        self.assertTrue(identity.matched)
        self.assertFalse(identity.blocking)

    def test_missing_protected_reference_is_blocking(self) -> None:
        fixture_git(self.repository, "update-ref", "-d", PROTECTED_REF)
        with self.assertRaises(ProtectedReferenceError) as raised:
            self._resolve()
        self.assertIsNotNone(raised.exception.identity)
        self.assertIsNone(raised.exception.identity.actual_object)  # type: ignore[union-attr]
        self.assertTrue(raised.exception.identity.blocking)  # type: ignore[union-attr]

    def test_mismatched_protected_reference_is_blocking(self) -> None:
        with self.assertRaises(ProtectedReferenceError) as raised:
            self._resolve(protected_references=self._protected(expected_object="0" * 40))
        self.assertIsNotNone(raised.exception.identity)
        self.assertFalse(raised.exception.identity.matched)  # type: ignore[union-attr]
        self.assertTrue(raised.exception.identity.blocking)  # type: ignore[union-attr]

    def test_duplicate_protected_reference_name_is_rejected(self) -> None:
        records = self._protected() + self._protected()
        with self.assertRaises(ProtectedReferenceError):
            self._resolve(protected_references=records)

    def test_invalid_protected_reference_contract_is_rejected(self) -> None:
        base = self._protected()[0]
        cases = []
        for key in tuple(base):
            missing = dict(base)
            del missing[key]
            cases.append(missing)
        cases.extend(
            (
                {**base, "extra": True},
                {**base, "name": "heads/not-full"},
                {**base, "name": "refs/heads/bad..name"},
                {**base, "expected_object": "main"},
                {**base, "authoritatively_targeted": True},
                {**base, "authoritatively_targeted": 0},
                {**base, "selection": "allowed"},
            )
        )
        for record in cases:
            with self.subTest(record=record), self.assertRaises(ProtectedReferenceError):
                self._resolve(protected_references=[record])

    def test_protected_object_content_is_never_requested(self) -> None:
        with mock.patch.object(
            snapshot_module, "_run_git", wraps=snapshot_module._run_git
        ) as spy:
            self._resolve()
        commands = [call.args[1:] for call in spy.call_args_list]
        self.assertTrue(any(command[0] == "show-ref" for command in commands))
        self.assertFalse(
            any(PROTECTED_OBJECT in argument for command in commands for argument in command)
        )
        for command in commands:
            if command[0] == "show-ref":
                self.assertEqual(command, ("show-ref", "--verify", "--hash", PROTECTED_REF))

    def test_production_commands_are_bounded_non_network_and_non_mutating(self) -> None:
        snapshot = self._synthetic_snapshot()
        with mock.patch.object(
            snapshot_module, "_run_git", wraps=snapshot_module._run_git
        ) as spy:
            read_snapshot_blob(self.repository, snapshot, "regular.txt")
        commands = [call.args[1:] for call in spy.call_args_list]
        allowed = {
            "rev-parse",
            "status",
            "config",
            "for-each-ref",
            "show-ref",
            "cat-file",
            "ls-tree",
        }
        forbidden = {
            "clone",
            "fetch",
            "pull",
            "push",
            "ls-remote",
            "upload-pack",
            "checkout",
            "switch",
            "reset",
            "clean",
            "add",
            "commit",
            "merge",
            "rebase",
            "update-ref",
            "worktree",
            "maintenance",
            "gc",
            "repack",
            "prune",
        }
        self.assertTrue(commands)
        self.assertTrue(all(command[0] in allowed for command in commands))
        self.assertFalse(any(command[0] in forbidden for command in commands))
        self.assertIn(
            (
                "config",
                "--local",
                "--no-includes",
                "--null",
                "--name-only",
                "--list",
            ),
            commands,
        )
        self.assertIn(
            (
                "config",
                "--local",
                "--no-includes",
                "--null",
                "--get-all",
                "remote.origin.url",
            ),
            commands,
        )
        for call in spy.call_args_list:
            self.assertEqual(call.args[0], self.repository.resolve())

    def test_subprocess_environment_is_sanitized_and_fixed(self) -> None:
        real_run = subprocess.run
        with mock.patch.object(
            snapshot_module.subprocess, "run", wraps=real_run
        ) as spy:
            self._resolve()
        fixed_git_environment = {
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_NO_LAZY_FETCH": "1",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_LITERAL_PATHSPECS": "1",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
        }
        fixed_command_prefix = (
            "git",
            "--no-replace-objects",
            "-c",
            "core.fsmonitor=false",
            "-c",
            "core.untrackedCache=false",
            "-c",
            f"core.hooksPath={os.devnull}",
        )
        self.assertEqual(snapshot_module._GIT_COMMAND_PREFIX, fixed_command_prefix)
        self.assertTrue(spy.call_args_list)
        for call in spy.call_args_list:
            command = call.args[0]
            environment = call.kwargs["env"]
            self.assertEqual(
                tuple(command[: len(fixed_command_prefix)]), fixed_command_prefix
            )
            self.assertEqual(
                command[len(fixed_command_prefix) : len(fixed_command_prefix) + 2],
                ["-C", str(self.repository.resolve())],
            )
            self.assertEqual(
                {key: value for key, value in environment.items() if key.startswith("GIT_")},
                fixed_git_environment,
            )
            self.assertEqual(environment["LC_ALL"], "C")
            self.assertEqual(environment["LANG"], "C")
            self.assertEqual(call.kwargs["cwd"], self.repository.resolve())
            self.assertFalse(call.kwargs["text"])
            self.assertFalse(call.kwargs["shell"])
            self.assertTrue(call.kwargs["capture_output"])

    def test_post_clean_failure_preserves_primary_blob_error(self) -> None:
        snapshot = self._resolve()
        real_run_git = snapshot_module._run_git

        def mutate_after_lookup(
            repository: Path, *arguments: str
        ) -> subprocess.CompletedProcess[bytes]:
            result = real_run_git(repository, *arguments)
            if arguments and arguments[0] == "ls-tree":
                (self.repository / "post-operation-untracked").write_bytes(b"dirty\n")
            return result

        with mock.patch.object(snapshot_module, "_run_git", side_effect=mutate_after_lookup):
            with self.assertRaises(BlobLookupError) as raised:
                read_snapshot_blob(self.repository, snapshot, "missing.txt")
        self.assertIsInstance(
            raised.exception.post_state_error, RepositoryStateError
        )
        self.assertIn("post-operation clean-state check also failed", str(raised.exception))

    def test_target_evidence_is_unchanged_after_success_and_failure(self) -> None:
        before = self._target_evidence()
        snapshot = self._resolve()
        read_snapshot_blob(self.repository, snapshot, "docs/current-mission.md")
        self.assertEqual(self._target_evidence(), before)
        with self.assertRaises(BlobLookupError):
            read_snapshot_blob(self.repository, snapshot, "missing.txt")
        self.assertEqual(self._target_evidence(), before)

    def test_repeated_snapshot_and_blob_results_are_equal(self) -> None:
        first_snapshot = self._resolve()
        second_snapshot = self._resolve()
        self.assertEqual(first_snapshot, second_snapshot)
        first_blob = read_snapshot_blob(
            self.repository, first_snapshot, "docs/current-mission.md"
        )
        second_blob = read_snapshot_blob(
            self.repository, second_snapshot, "docs/current-mission.md"
        )
        self.assertEqual(first_blob, second_blob)

    def test_blob_bytes_come_from_historical_tree_not_worktree(self) -> None:
        blob = read_snapshot_blob(
            self.repository, self._resolve(), "docs/current-mission.md"
        )
        historical = fixture_git(
            self.repository,
            "show",
            f"{HISTORICAL_COMMIT}:docs/current-mission.md",
        ).stdout
        worktree = (self.repository / "docs/current-mission.md").read_bytes()
        self.assertEqual(blob.content, historical)
        self.assertNotEqual(blob.content, worktree)

    def test_snapshot_models_are_frozen_and_json_models_are_deterministic(self) -> None:
        snapshot = self._resolve()
        self.assertEqual(snapshot.as_dict(), snapshot.as_dict())
        self.assertEqual(snapshot.repository.origin_urls, tuple(snapshot.repository.origin_urls))
        with self.assertRaises(dataclasses.FrozenInstanceError):
            snapshot.tree = "0" * 40  # type: ignore[misc]
        identity = ProtectedReferenceIdentity(
            PROTECTED_REF, PROTECTED_OBJECT, PROTECTED_OBJECT, False, "forbidden", True, False
        )
        repository = RepositoryIdentityEvidence(
            CANONICAL_REPOSITORY_IDENTITY,
            list(CURRENT_ORIGINS[:1]),  # type: ignore[arg-type]
            CANONICAL_REPOSITORY_IDENTITY,
        )
        copied = RepositorySnapshot(
            repository,
            HISTORICAL_COMMIT,
            "sha1",
            HISTORICAL_COMMIT,
            HISTORICAL_TREE,
            SNAPSHOT_MODE,
            snapshot.fingerprint,
            [identity],  # type: ignore[arg-type]
        )
        self.assertIsInstance(copied.repository.origin_urls, tuple)
        self.assertIsInstance(copied.protected_references, tuple)

    def test_immutable_blob_keeps_raw_bytes_outside_canonical_json(self) -> None:
        blob = ImmutableBlob("path", "100644", "sha1", "0" * 40, b"\x00\xff")
        self.assertEqual(blob.content, b"\x00\xff")
        self.assertNotIn("content", blob.as_dict())
        with self.assertRaises(ModelValueError):
            deep_freeze(blob.content)

    def test_unavailable_file_and_non_repository_targets_are_rejected(self) -> None:
        file_target = self.workspace / "file"
        file_target.write_bytes(b"not a repository")
        directory_target = self.workspace / "directory"
        directory_target.mkdir()
        for target in ("", self.workspace / "absent", file_target, directory_target):
            with self.subTest(target=target), self.assertRaises(SnapshotEnvironmentError):
                resolve_snapshot(
                    target,
                    repository_identity=CANONICAL_REPOSITORY_IDENTITY,
                    requested_revision=HISTORICAL_COMMIT,
                    expected_tree=HISTORICAL_TREE,
                    protected_references=self._protected(),
                )


if __name__ == "__main__":
    unittest.main()
