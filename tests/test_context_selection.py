import ast
import dataclasses
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from atlas.platform import reasoning as reasoning_exports
from atlas.platform.context_compilation import (
    CompilationRequest,
    LoadedPolicy,
    SelectedSourcePlan,
    SelectionOmissionPlan,
    SelectionPlan,
    SelectionUnknownPlan,
)
from atlas.platform.context_compilation.digests import snapshot_fingerprint
from atlas.platform.context_compilation.inputs import (
    load_compilation_request,
    load_selection_policy,
)
from atlas.platform.context_compilation.models import (
    DigestRecord,
    ImmutableBlob,
    RepositoryIdentityEvidence,
    RepositoryRequestIdentity,
    RepositorySnapshot,
)
from atlas.platform.context_compilation.snapshot import BlobLookupError
from atlas.platform.reasoning import (
    SelectionContractError,
    SelectionError,
    build_bounded_selection_plan,
)
from atlas.platform.reasoning import context_selection as selection_module


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_IDENTITY = "github.com/aidenm727/t430-homelab"
FUTURE_REPOSITORY_IDENTITY = "github.com/aidenm727/aiden-platform"
HISTORICAL_COMMIT = "79eef80af3d5969ece7eb9fe7f802be35575f450"
HISTORICAL_TREE = "3d2853517e64209cffde91766a62e9f70ceb2e47"
ORIGIN = "https://github.com/aidenm727/t430-homelab.git"
REQUEST_PATH = (
    ROOT
    / "tests/fixtures/task_context/requests/"
    "example-eo-2026-013-read-only-assessment-v1.json"
)
POLICY_PATH = (
    ROOT
    / "docs/task-context/policies/selection/"
    "example-read-only-architecture-assessment-v1.json"
)
OPPORTUNITY_PATH = (
    "docs/opportunities/reviewed/"
    "EO-2026-013-task-scoped-agent-context-compilation.yaml"
)
MISSION_PATH = "docs/current-mission.md"
REPOSITORY_PATH = "docs/architecture/repository.md"
KNOWLEDGE_PATH = "docs/architecture/knowledge-authority.md"
COLLABORATION_PATH = "docs/standards/engineering-collaboration.md"
EXPECTED_ORDER = (
    "S010-explicit-opportunity-anchor",
    "S020-current-mission-milestone",
    "S030-canonical-repository-authority",
    "S040-mandatory-knowledge-authority",
    "S050-mandatory-collaboration",
)
HISTORICAL_BLOBS = {
    OPPORTUNITY_PATH: "79d46f0839653d2df44778a8a5a4c63d50e8318d",
    MISSION_PATH: "3e0d5fe9887c4a935c3a5f39006b4707d64b0355",
    REPOSITORY_PATH: "039d0cf255484602f9b99d0f5397bc619f2bff5b",
    KNOWLEDGE_PATH: "4f37569dab8f855e2bbd496393e2b9f41a90dece",
    COLLABORATION_PATH: "a5a8c0e79570e42387ebb6abde5dde8224b545ef",
}


def fixture_git(
    repository: Path | None,
    *arguments: str,
    check: bool = True,
) -> subprocess.CompletedProcess[bytes]:
    command = ["git"]
    if repository is not None:
        command.extend(("-C", str(repository)))
    command.extend(arguments)
    result = subprocess.run(
        command,
        env=os.environ.copy(),
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


def typed_request_and_policy() -> tuple[CompilationRequest, LoadedPolicy]:
    request_value = load_compilation_request(REQUEST_PATH)
    policy_value = load_selection_policy(
        POLICY_PATH,
        request_value["selection_policy"],
    )
    return (
        CompilationRequest.from_validated_mapping(request_value),
        LoadedPolicy.from_validated_mapping(policy_value),
    )


def historical_snapshot() -> RepositorySnapshot:
    repository = RepositoryIdentityEvidence(
        requested_identity=REPOSITORY_IDENTITY,
        origin_urls=(ORIGIN,),
        normalized_identity=REPOSITORY_IDENTITY,
    )
    fingerprint = snapshot_fingerprint(
        REPOSITORY_IDENTITY,
        "sha1",
        HISTORICAL_COMMIT,
        HISTORICAL_TREE,
        "clean_committed",
    )
    return RepositorySnapshot(
        repository=repository,
        requested_revision=HISTORICAL_COMMIT,
        object_format="sha1",
        commit=HISTORICAL_COMMIT,
        tree=HISTORICAL_TREE,
        snapshot_mode="clean_committed",
        fingerprint=fingerprint,
        protected_references=(),
    )


class SelectionFixture:
    def setUp(self) -> None:
        super().setUp()
        self.request, self.policy = typed_request_and_policy()
        self.snapshot = historical_snapshot()
        self.contents = {
            OPPORTUNITY_PATH: (
                b"id: EO-2026-013\n"
                b"title: Task scoped context\n"
                b"status: reviewed\n"
                b"summary: >\n"
                b"  Deterministic bounded context.\n"
                b"related_documents:\n"
                b"  - docs/architecture/repository.md\n"
                b"  - docs/standards/engineering-collaboration.md\n"
            ),
            MISSION_PATH: (
                b"# Current Mission\n\n"
                b"## Initial Milestone\n\n"
                b"Checkpoint evidence.\n"
                b"## Next\n\n"
                b"Later.\n"
            ),
            REPOSITORY_PATH: (
                b"# Repository\n\n"
                b"## Source of Truth Hierarchy\n\n"
                b"Canonical order.\n"
            ),
            KNOWLEDGE_PATH: (
                b"# Knowledge\n\n"
                b"### Generated Context\n\n"
                b"Generated context is non-canonical.\n"
            ),
            COLLABORATION_PATH: (
                b"# Collaboration\n\n"
                b"## Responsibilities\n\n"
                b"The owner decides.\n"
            ),
        }
        self.read_paths: list[str] = []

    def fake_read(
        self,
        target_repository: str | Path,
        snapshot: RepositorySnapshot,
        path: str,
    ) -> ImmutableBlob:
        del target_repository
        self.assertIs(snapshot, self.snapshot)
        self.read_paths.append(path)
        if path not in self.contents:
            raise BlobLookupError(
                "repository path does not identify exactly one entry"
            )
        object_id = (
            str(len(self.read_paths) % 10) * 40
            if path not in HISTORICAL_BLOBS
            else HISTORICAL_BLOBS[path]
        )
        return ImmutableBlob(
            path=path,
            mode="100644",
            object_format="sha1",
            object_id=object_id,
            content=self.contents[path],
        )

    def build(self) -> SelectionPlan:
        with mock.patch.object(
            selection_module,
            "read_snapshot_blob",
            side_effect=self.fake_read,
        ):
            return build_bounded_selection_plan(
                target_repository=ROOT,
                request=self.request,
                selection_policy=self.policy,
                snapshot=self.snapshot,
            )


class SelectionModelTests(SelectionFixture, unittest.TestCase):
    def test_public_error_and_function_exports(self) -> None:
        self.assertTrue(issubclass(SelectionContractError, SelectionError))
        self.assertIs(
            reasoning_exports.build_bounded_selection_plan,
            build_bounded_selection_plan,
        )

    def test_plan_models_are_frozen_and_deeply_immutable(self) -> None:
        plan = self.build()
        selected = plan.selected[0]
        self.assertIsInstance(selected.selector, MappingProxyType)
        self.assertIsInstance(selected.selection_chain, tuple)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            selected.rule_id = "changed"  # type: ignore[misc]
        with self.assertRaises(TypeError):
            selected.selector["type"] = "changed"  # type: ignore[index]
        with self.assertRaises(dataclasses.FrozenInstanceError):
            plan.selected = ()  # type: ignore[misc]

    def test_readiness_is_derived_from_blocking_records(self) -> None:
        plan = self.build()
        self.assertTrue(plan.ready_for_compilation)
        omission = SelectionOmissionPlan(
            rule_id="S",
            exclusion_rule_id="X",
            boundary="path",
            individual={"path": "path"},
            trigger="trigger",
            selection_chain=("trigger", "S"),
            reason="reason",
            consequence="consequence",
            blocking=True,
            reconsideration_condition="condition",
        )
        blocked = dataclasses.replace(plan, omissions=(omission,))
        self.assertFalse(blocked.ready_for_compilation)
        self.assertNotIn("ready_for_compilation", plan.__dataclass_fields__)


class BoundedSelectionTests(SelectionFixture, unittest.TestCase):
    def test_future_identity_is_rejected_before_the_github_rename(self) -> None:
        self.request = dataclasses.replace(
            self.request,
            repository=RepositoryRequestIdentity(
                FUTURE_REPOSITORY_IDENTITY,
                HISTORICAL_COMMIT,
            ),
        )
        with self.assertRaisesRegex(
            SelectionContractError,
            "repository identities do not match",
        ):
            self.build()
        self.assertEqual(self.read_paths, [])

    def test_exact_five_rule_success_plan(self) -> None:
        plan = self.build()
        self.assertEqual(tuple(item.rule_id for item in plan.selected), EXPECTED_ORDER)
        self.assertEqual(plan.omissions, ())
        self.assertEqual(plan.unknowns, ())
        self.assertTrue(plan.ready_for_compilation)
        self.assertEqual(
            tuple(item.budget_tier for item in plan.selected),
            (
                "mandatory_authoritative_sources",
                "mandatory_authoritative_sources",
                "required_supporting_sources",
                "required_supporting_sources",
                "required_supporting_sources",
            ),
        )
        self.assertEqual(
            tuple(item.sensitivity for item in plan.selected),
            ("public",) * 5,
        )
        self.assertEqual(
            tuple(item.selection_reason for item in plan.selected),
            (
                "explicit_opportunity_reference",
                "explicit_mission_reference",
                "allowlisted_related_document",
                "task_profile_required_source",
                "allowlisted_related_document",
            ),
        )
        self.assertNotIn("content", plan.selected[0].as_dict())
        self.assertNotIn("included_utf8_bytes", plan.selected[0].as_dict())

    def test_missing_exact_relationship_is_blocking_omission_without_source_read(
        self,
    ) -> None:
        self.contents[OPPORTUNITY_PATH] = self.contents[OPPORTUNITY_PATH].replace(
            b"  - docs/architecture/repository.md\n",
            b"",
        )
        plan = self.build()
        self.assertEqual(
            tuple(item.rule_id for item in plan.omissions),
            ("S030-canonical-repository-authority",),
        )
        omission = plan.omissions[0]
        self.assertEqual(omission.reason, "required_relationship_absent")
        self.assertTrue(omission.blocking)
        self.assertNotIn(REPOSITORY_PATH, self.read_paths)
        self.assertFalse(plan.ready_for_compilation)

    def test_invalid_relationship_evidence_creates_two_rule_unknowns_and_no_reads(
        self,
    ) -> None:
        self.contents[OPPORTUNITY_PATH] = self.contents[OPPORTUNITY_PATH].replace(
            b"related_documents:\n"
            b"  - docs/architecture/repository.md\n"
            b"  - docs/standards/engineering-collaboration.md\n",
            b"related_documents: unavailable\n",
        )
        plan = self.build()
        relationship_unknowns = tuple(
            item
            for item in plan.unknowns
            if item.field == "related_documents"
        )
        self.assertEqual(
            tuple(item.rule_id for item in relationship_unknowns),
            (
                "S030-canonical-repository-authority",
                "S050-mandatory-collaboration",
            ),
        )
        self.assertNotIn(REPOSITORY_PATH, self.read_paths)
        self.assertNotIn(COLLABORATION_PATH, self.read_paths)

    def test_missing_blob_is_rule_specific_unknown(self) -> None:
        del self.contents[KNOWLEDGE_PATH]
        plan = self.build()
        unknown = next(
            item
            for item in plan.unknowns
            if item.rule_id == "S040-mandatory-knowledge-authority"
        )
        self.assertEqual(unknown.field, "immutable_blob")
        self.assertTrue(unknown.blocking)

    def test_missing_heading_is_rule_specific_unknown(self) -> None:
        self.contents[MISSION_PATH] = b"# Current Mission\n\nNo milestone.\n"
        plan = self.build()
        unknown = next(
            item
            for item in plan.unknowns
            if item.rule_id == "S020-current-mission-milestone"
        )
        self.assertEqual(unknown.field, "selector_target")

    def test_source_text_boundary_failures_are_x060_omissions(self) -> None:
        cases = (
            b"\xef\xbb\xbf## Initial Milestone\nbody\n",
            b"## Initial Milestone\nbad \xff\n",
            b"## Initial Milestone\nbad\0value\n",
            b"## Initial Milestone\rbody",
            b"## Initial Milestone\r\nbody\n",
        )
        for content in cases:
            with self.subTest(content=content):
                self.setUp()
                self.contents[MISSION_PATH] = content
                plan = self.build()
                omission = next(
                    item
                    for item in plan.omissions
                    if item.rule_id == "S020-current-mission-milestone"
                )
                self.assertEqual(
                    omission.exclusion_rule_id,
                    "X060-unsupported-binary",
                )
                self.assertEqual(omission.reason, "unsupported_text_source")

    def test_malformed_opportunity_creates_source_and_relationship_unknowns(
        self,
    ) -> None:
        self.contents[OPPORTUNITY_PATH] = (
            b"id: EO-2026-013\n"
            b"id: duplicate\n"
        )
        plan = self.build()
        self.assertEqual(
            tuple(item.rule_id for item in plan.unknowns),
            (
                "S010-explicit-opportunity-anchor",
                "S030-canonical-repository-authority",
                "S050-mandatory-collaboration",
            ),
        )

    def test_contradictory_opportunity_identity_is_fatal(self) -> None:
        self.contents[OPPORTUNITY_PATH] = self.contents[OPPORTUNITY_PATH].replace(
            b"id: EO-2026-013",
            b"id: EO-2026-999",
        )
        with self.assertRaisesRegex(
            SelectionContractError,
            "opportunity object identity contradicts",
        ):
            self.build()

    def test_above_ceiling_source_is_omitted_before_blob_read(self) -> None:
        rules = [dict(rule) for rule in selection_module._rule_contracts()]
        rule = dict(rules[3])
        source = dict(rule["source"])
        source["sensitivity"] = "sensitive"
        rule["source"] = source
        rules[3] = rule
        with (
            mock.patch.object(
                selection_module,
                "_validate_policy",
                return_value=tuple(rules),
            ),
            mock.patch.object(
                selection_module,
                "read_snapshot_blob",
                side_effect=self.fake_read,
            ),
        ):
            plan = build_bounded_selection_plan(
                target_repository=ROOT,
                request=self.request,
                selection_policy=self.policy,
                snapshot=self.snapshot,
            )
        omission = next(
            item
            for item in plan.omissions
            if item.rule_id == "S040-mandatory-knowledge-authority"
        )
        self.assertEqual(
            omission.exclusion_rule_id,
            "X050-disallowed-sensitivity",
        )
        self.assertNotIn(KNOWLEDGE_PATH, self.read_paths)

    def test_duplicate_candidate_identity_is_fatal(self) -> None:
        rules = [dict(rule) for rule in selection_module._rule_contracts()]
        duplicate = dict(rules[4])
        duplicate["source"] = dict(rules[3]["source"])
        duplicate["selector"] = dict(rules[3]["selector"])
        rules[4] = duplicate
        with self.assertRaisesRegex(
            SelectionContractError,
            "duplicate candidate identity",
        ):
            selection_module._validate_distinct_candidates(
                tuple(rules),
                self.request,
            )

    def test_wrong_public_types_and_snapshot_mismatch_are_fatal(self) -> None:
        invalid_calls = (
            {
                "target_repository": object(),
                "request": self.request,
                "selection_policy": self.policy,
                "snapshot": self.snapshot,
            },
            {
                "target_repository": ROOT,
                "request": object(),
                "selection_policy": self.policy,
                "snapshot": self.snapshot,
            },
        )
        for arguments in invalid_calls:
            with self.subTest(arguments=arguments), self.assertRaises(
                SelectionContractError
            ):
                build_bounded_selection_plan(**arguments)  # type: ignore[arg-type]
        changed = dataclasses.replace(
            self.snapshot,
            requested_revision="0" * 40,
            commit="0" * 40,
        )
        with self.assertRaises(SelectionContractError):
            build_bounded_selection_plan(
                target_repository=ROOT,
                request=self.request,
                selection_policy=self.policy,
                snapshot=changed,
            )

    def test_policy_digest_or_selector_contract_mismatch_is_fatal(self) -> None:
        bad_digest = DigestRecord(
            "sha256",
            "rfc8785-jcs",
            "0" * 64,
        )
        changed_policy = dataclasses.replace(
            self.policy,
            reference=dataclasses.replace(
                self.policy.reference,
                digest=bad_digest,
            ),
        )
        with self.assertRaises(SelectionContractError):
            build_bounded_selection_plan(
                target_repository=ROOT,
                request=self.request,
                selection_policy=changed_policy,
                snapshot=self.snapshot,
            )

        rules = [dict(rule) for rule in selection_module._rule_contracts()]
        changed_rule = dict(rules[1])
        changed_rule["selector"] = {"type": "unsupported"}
        rules[1] = changed_rule
        with (
            mock.patch.object(
                selection_module,
                "_validate_policy",
                return_value=tuple(rules),
            ),
            mock.patch.object(
                selection_module,
                "read_snapshot_blob",
                side_effect=self.fake_read,
            ),
            self.assertRaises(SelectionContractError),
        ):
            build_bounded_selection_plan(
                target_repository=ROOT,
                request=self.request,
                selection_policy=self.policy,
                snapshot=self.snapshot,
            )


class HistoricalSelectionIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repository = Path(self.temporary.name) / "target"
        fixture_git(
            None,
            "clone",
            "--no-local",
            "--no-hardlinks",
            "--single-branch",
            "--branch",
            "main",
            "--no-tags",
            str(ROOT),
            str(self.repository),
        )
        fixture_git(
            self.repository,
            "remote",
            "set-url",
            "origin",
            ORIGIN,
        )
        self.assertEqual(
            fixture_git(
                self.repository,
                "status",
                "--porcelain=v1",
                "-z",
                "--untracked-files=all",
                "--ignore-submodules=none",
            ).stdout,
            b"",
        )

    def test_historical_five_source_plan_and_exact_blob_oracles(self) -> None:
        request, policy = typed_request_and_policy()
        plan = build_bounded_selection_plan(
            target_repository=self.repository,
            request=request,
            selection_policy=policy,
            snapshot=historical_snapshot(),
        )
        self.assertEqual(tuple(item.rule_id for item in plan.selected), EXPECTED_ORDER)
        self.assertEqual(
            {item.path: item.blob for item in plan.selected},
            HISTORICAL_BLOBS,
        )
        self.assertEqual(plan.omissions, ())
        self.assertEqual(plan.unknowns, ())
        self.assertTrue(plan.ready_for_compilation)
        self.assertEqual(
            fixture_git(
                self.repository,
                "status",
                "--porcelain=v1",
                "-z",
                "--untracked-files=all",
                "--ignore-submodules=none",
            ).stdout,
            b"",
        )


class SelectionCapabilityBoundaryTests(unittest.TestCase):
    def test_context_selection_has_no_mutable_module_level_state(self) -> None:
        path = (
            ROOT
            / "tools/atlas/platform/reasoning/context_selection.py"
        )
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            value = node.value
            self.assertNotIsInstance(
                value,
                (ast.List, ast.Dict, ast.Set),
                ast.dump(node),
            )

    def test_context_selection_has_no_forbidden_direct_capability(self) -> None:
        path = (
            ROOT
            / "tools/atlas/platform/reasoning/context_selection.py"
        )
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_roots: set[str] = set()
        called_names: set[str] = set()
        attribute_calls: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(
                    alias.name.split(".", 1)[0] for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_names.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    attribute_calls.add(node.func.attr)
        self.assertTrue(
            {
                "subprocess",
                "socket",
                "requests",
                "urllib",
                "http",
                "time",
                "datetime",
                "random",
                "secrets",
                "hashlib",
            }.isdisjoint(imported_roots)
        )
        self.assertNotIn("resolve_snapshot", called_names)
        self.assertNotIn("show-ref", source)
        self.assertTrue(
            {
                "write_text",
                "write_bytes",
                "open",
                "unlink",
                "rename",
                "replace",
                "mkdir",
            }.isdisjoint(attribute_calls)
        )

    def test_only_authorized_public_models_are_added(self) -> None:
        for model in (
            SelectedSourcePlan,
            SelectionOmissionPlan,
            SelectionUnknownPlan,
            SelectionPlan,
        ):
            self.assertTrue(dataclasses.is_dataclass(model))
            self.assertTrue(model.__dataclass_params__.frozen)


if __name__ == "__main__":
    unittest.main()
