import ast
import dataclasses
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import MappingProxyType
from unittest import mock

import atlas.platform.context_compilation as context_exports
from atlas.platform.context_compilation import (
    ByteDigestRecord,
    CompilationRequest,
    MaterializationContractError,
    MaterializationError,
    MaterializationIdentityError,
    MaterializationResult,
    MaterializationSourceError,
    RepositorySnapshot,
    SelectionOmissionPlan,
    SelectionPlan,
    SelectionUnknownPlan,
    byte_digest,
    materialize_selection_plan,
    omission_identifier,
    payload_identifier,
    source_identifier,
)
from atlas.platform.context_compilation import materialization as materialization_module
from atlas.platform.context_compilation import snapshot as snapshot_module
from atlas.platform.context_compilation.digests import snapshot_fingerprint
from atlas.platform.context_compilation.inputs import (
    load_compilation_request,
    load_selection_policy,
)
from atlas.platform.context_compilation.models import (
    CompilerIdentity,
    DigestRecord,
    ImmutableBlob,
    LoadedPolicy,
    PolicyReference,
    RepositoryIdentityEvidence,
    RepositoryRequestIdentity,
    SelectedSourcePlan,
)
from atlas.platform.reasoning import build_bounded_selection_plan


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_IDENTITY = "github.com/aidenm727/t430-homelab"
FUTURE_REPOSITORY_IDENTITY = "github.com/aidenm727/aiden-platform"
HISTORICAL_COMMIT = "79eef80af3d5969ece7eb9fe7f802be35575f450"
HISTORICAL_TREE = "3d2853517e64209cffde91766a62e9f70ceb2e47"
ORIGIN = "https://github.com/aidenm727/t430-homelab.git"
SELECTION_DIGEST = (
    "69577722ea4eb6f479424f3bf324866cc2992d5df82b3224e5f20571ef081938"
)
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
OPPORTUNITY_OWNER = "docs/architecture/engineering-opportunity-object.md"
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
HISTORICAL_SOURCE_DIGESTS = {
    OPPORTUNITY_PATH: "36b73d6a19d091d580d3319225cdbaf04a7dda222979179711144789a371997f",
    MISSION_PATH: "cc3d8d2272411e327bc25ca5f6f63080ee4dc456199e54a1e3e3ae4ece1fc941",
    REPOSITORY_PATH: "6b1f18f3f97fd58767895fd41ae5b0285ec64f6a1679193ef89ce8f078d6bcac",
    KNOWLEDGE_PATH: "a70452eb97ebb7471171c456548bea3f20d222f8794e643e6ae651639617dac2",
    COLLABORATION_PATH: "98accba61d270275226d58f3304634e724f795b297e3b360cb597a403cae9e64",
}
HISTORICAL_SOURCE_IDS = {
    OPPORTUNITY_PATH: "src-f05784f789d7a5b1",
    MISSION_PATH: "src-3e334b99840bad45",
    REPOSITORY_PATH: "src-ce5f32a8805d0c2f",
    KNOWLEDGE_PATH: "src-2b9bc68b8e6a6b9c",
    COLLABORATION_PATH: "src-a6a52f599da035ed",
}
HISTORICAL_PAYLOAD_DIGESTS = {
    OPPORTUNITY_PATH: "cf7550262b7e935234a6edafa07e807b36a3b54ee04d50bffd57c37d93b18a3c",
    MISSION_PATH: "4ed09ad6e143a64e08e491c72dba7d6e9a7bc3bf3dc2e329b19393ae9e89a9e4",
    REPOSITORY_PATH: "a799667da407c49563d2cfe03bb44e5ba18840aa71d962b805d8741b60a8cf07",
    KNOWLEDGE_PATH: "2724757ec5bd1d1460f3754d4e3a8a76c41d84f0d811cdb11e5605ade619f97e",
    COLLABORATION_PATH: "41d0657c08be387a100892d64cc2bd4dfa3ead10ef51e7cf90dc29e9c52883f8",
}
HISTORICAL_PAYLOAD_BYTES = {
    OPPORTUNITY_PATH: 324,
    MISSION_PATH: 910,
    REPOSITORY_PATH: 1000,
    KNOWLEDGE_PATH: 357,
    COLLABORATION_PATH: 503,
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


def historical_snapshot() -> RepositorySnapshot:
    repository = RepositoryIdentityEvidence(
        requested_identity=REPOSITORY_IDENTITY,
        origin_urls=(ORIGIN,),
        normalized_identity=REPOSITORY_IDENTITY,
    )
    return RepositorySnapshot(
        repository=repository,
        requested_revision=HISTORICAL_COMMIT,
        object_format="sha1",
        commit=HISTORICAL_COMMIT,
        tree=HISTORICAL_TREE,
        snapshot_mode="clean_committed",
        fingerprint=snapshot_fingerprint(
            REPOSITORY_IDENTITY,
            "sha1",
            HISTORICAL_COMMIT,
            HISTORICAL_TREE,
            "clean_committed",
        ),
        protected_references=(),
    )


def portable_request() -> CompilationRequest:
    return CompilationRequest(
        schema_version="aiden.task-context.compilation-request/v1",
        repository=RepositoryRequestIdentity(
            REPOSITORY_IDENTITY,
            HISTORICAL_COMMIT,
        ),
        task={
            "id": {
                "state": "known",
                "value": "portable-materialization-test",
            }
        },
        declared_constraints={},
        selection_policy=PolicyReference(
            id="example.read-only-architecture-assessment",
            version="1.0.1",
            digest=DigestRecord(
                "sha256",
                "rfc8785-jcs",
                SELECTION_DIGEST,
            ),
        ),
        budget_policy=PolicyReference(
            id="example.utf8-byte-budget",
            version="1.0.0",
            digest=DigestRecord("sha256", "rfc8785-jcs", "a" * 64),
        ),
        protected_references=(),
        as_of="2026-07-15T15:40:26-04:00",
        compiler=CompilerIdentity("aiden.context-compilation", "1.0.0"),
    )


def selected_record(rule_id: str, blob_character: str) -> SelectedSourcePlan:
    contracts = {
        "S010-explicit-opportunity-anchor": (
            10,
            "mandatory_authoritative_sources",
            "explicit_anchor",
            "repository_object",
            OPPORTUNITY_PATH,
            "engineering-opportunity:EO-2026-013",
            "structured_repository_object",
            OPPORTUNITY_OWNER,
            {"type": "yaml_fields", "fields": ("id", "title", "status", "summary")},
        ),
        "S020-current-mission-milestone": (
            10,
            "mandatory_authoritative_sources",
            "explicit_anchor",
            "document",
            MISSION_PATH,
            None,
            "canonical_document",
            MISSION_PATH,
            {
                "type": "heading",
                "heading_text": "## Initial Milestone",
                "occurrence": 1,
            },
        ),
        "S030-canonical-repository-authority": (
            20,
            "required_supporting_sources",
            "allowlisted_relationship",
            "document",
            REPOSITORY_PATH,
            None,
            "canonical_document",
            REPOSITORY_PATH,
            {
                "type": "heading",
                "heading_text": "## Source of Truth Hierarchy",
                "occurrence": 1,
            },
        ),
        "S040-mandatory-knowledge-authority": (
            30,
            "required_supporting_sources",
            "task_profile",
            "document",
            KNOWLEDGE_PATH,
            None,
            "canonical_document",
            KNOWLEDGE_PATH,
            {
                "type": "heading",
                "heading_text": "### Generated Context",
                "occurrence": 1,
            },
        ),
        "S050-mandatory-collaboration": (
            30,
            "required_supporting_sources",
            "allowlisted_relationship",
            "document",
            COLLABORATION_PATH,
            None,
            "canonical_document",
            COLLABORATION_PATH,
            {
                "type": "heading",
                "heading_text": "## Responsibilities",
                "occurrence": 1,
            },
        ),
    }
    (
        priority,
        budget_tier,
        rule_type,
        source_kind,
        path,
        structured,
        authority_class,
        canonical_owner,
        selector,
    ) = contracts[rule_id]
    return SelectedSourcePlan(
        rule_id=rule_id,
        rule_type=rule_type,
        priority_tier=priority,
        budget_tier=budget_tier,
        source_kind=source_kind,
        sensitivity="public",
        path=path,
        structured_object_identity=structured,
        normalized_path_or_object_id=structured or path,
        selector=selector,
        selection_reason="portable_test_reason",
        trigger="portable_test_trigger",
        selection_chain=("portable", rule_id),
        authority_class=authority_class,
        canonical_owner=canonical_owner,
        commit=HISTORICAL_COMMIT,
        mode="100644",
        object_format="sha1",
        blob=blob_character * 40,
    )


def portable_plan(
    selected: tuple[SelectedSourcePlan, ...],
    *,
    omissions: tuple[SelectionOmissionPlan, ...] = (),
    unknowns: tuple[SelectionUnknownPlan, ...] = (),
) -> SelectionPlan:
    snapshot = historical_snapshot()
    return SelectionPlan(
        request_task_id="portable-materialization-test",
        selection_policy_id="example.read-only-architecture-assessment",
        selection_policy_version="1.0.1",
        selection_policy_digest=DigestRecord(
            "sha256",
            "rfc8785-jcs",
            SELECTION_DIGEST,
        ),
        repository_identity=REPOSITORY_IDENTITY,
        requested_revision=HISTORICAL_COMMIT,
        commit=HISTORICAL_COMMIT,
        tree=HISTORICAL_TREE,
        object_format="sha1",
        snapshot_mode="clean_committed",
        snapshot_fingerprint=snapshot.fingerprint,
        selected=selected,
        omissions=omissions,
        unknowns=unknowns,
    )


PORTABLE_CONTENTS = {
    OPPORTUNITY_PATH: (
        b"id: EO-2026-013\n"
        b"title: Portable materialization\n"
        b"status: reviewed\n"
        b"summary: >\n"
        b"  Exact selected content.\n"
    ),
    MISSION_PATH: (
        b"# Current Mission\n\n"
        b"## Initial Milestone\n\n"
        b"Checkpoint evidence.\n\n"
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


class PortableFixture:
    def setUp(self) -> None:
        super().setUp()
        self.request = portable_request()
        self.snapshot = historical_snapshot()
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
        plan_record = next(
            record for record in self.plan.selected if record.path == path
        )
        return ImmutableBlob(
            path=path,
            mode=plan_record.mode,
            object_format=plan_record.object_format,
            object_id=plan_record.blob,
            content=PORTABLE_CONTENTS[path],
        )

    def materialize(self) -> MaterializationResult:
        with mock.patch.object(
            materialization_module,
            "read_snapshot_blob",
            side_effect=self.fake_read,
        ):
            return materialize_selection_plan(
                target_repository=ROOT,
                request=self.request,
                snapshot=self.snapshot,
                selection_plan=self.plan,
            )


class MaterializationPortableTests(PortableFixture, unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan = portable_plan(
            (
                selected_record("S010-explicit-opportunity-anchor", "1"),
                selected_record("S020-current-mission-milestone", "2"),
                selected_record("S030-canonical-repository-authority", "3"),
                selected_record("S040-mandatory-knowledge-authority", "4"),
                selected_record("S050-mandatory-collaboration", "5"),
            )
        )

    def test_public_boundary_is_minimal_and_immutable(self) -> None:
        self.assertTrue(issubclass(MaterializationContractError, MaterializationError))
        self.assertTrue(issubclass(MaterializationIdentityError, MaterializationError))
        self.assertTrue(issubclass(MaterializationSourceError, MaterializationError))
        self.assertEqual(
            materialization_module.__all__,
            (
                "MaterializationError",
                "MaterializationContractError",
                "MaterializationIdentityError",
                "MaterializationSourceError",
                "materialize_selection_plan",
            ),
        )
        self.assertIsInstance(materialization_module.__all__, tuple)
        self.assertIsInstance(context_exports.__all__, tuple)
        for name in (
            "ByteDigestRecord",
            "ImmutableSourceIdentityRecord",
            "FreshnessRecord",
            "MaterializedSource",
            "MaterializedPayload",
            "IdentifiedOmission",
            "MaterializationResult",
            "byte_digest",
            "source_identifier",
            "payload_identifier",
            "omission_identifier",
            "materialize_selection_plan",
        ):
            self.assertIn(name, context_exports.__all__)

    def test_future_identity_is_rejected_before_the_github_rename(self) -> None:
        self.request = dataclasses.replace(
            self.request,
            repository=RepositoryRequestIdentity(
                FUTURE_REPOSITORY_IDENTITY,
                HISTORICAL_COMMIT,
            ),
        )
        with self.assertRaisesRegex(
            MaterializationContractError,
            "repository identities do not match",
        ):
            self.materialize()
        self.assertEqual(self.read_paths, [])

    def test_records_are_frozen_deeply_immutable_and_hide_payload_bytes(self) -> None:
        result = self.materialize()
        source = result.sources[0]
        payload = result.payloads[0]
        self.assertIs(source.plan, self.plan.selected[0])
        self.assertIsInstance(source.transformation, MappingProxyType)
        self.assertIsInstance(result.sources, tuple)
        self.assertIsInstance(result.payloads, tuple)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            source.id = "changed"  # type: ignore[misc]
        with self.assertRaises(TypeError):
            source.transformation["type"] = "changed"  # type: ignore[index]
        with self.assertRaises(dataclasses.FrozenInstanceError):
            payload.content = b"changed"  # type: ignore[misc]
        self.assertNotIn("content", payload.as_dict())
        self.assertNotIn("content", result.as_dict()["payloads"][0])

    def test_structured_opportunity_dimensions_are_independent_and_preserved(
        self,
    ) -> None:
        opportunity = selected_record("S010-explicit-opportunity-anchor", "1")
        self.plan = portable_plan((opportunity,))

        result = self.materialize()

        self.assertEqual(self.read_paths, [OPPORTUNITY_PATH])
        self.assertEqual(len(result.sources), 1)
        self.assertIs(result.sources[0].plan, opportunity)
        self.assertEqual(result.sources[0].plan.path, OPPORTUNITY_PATH)
        self.assertEqual(
            result.sources[0].plan.structured_object_identity,
            "engineering-opportunity:EO-2026-013",
        )
        self.assertEqual(
            result.sources[0].plan.canonical_owner,
            OPPORTUNITY_OWNER,
        )
        self.assertEqual(
            result.sources[0].plan.authority_class,
            "structured_repository_object",
        )
        self.assertEqual(result.sources[0].plan.source_kind, "repository_object")
        self.assertEqual(result.sources[0].freshness.status, "current_at_snapshot")
        self.assertEqual(result.omissions, ())
        self.assertEqual(result.unknowns, ())

    def test_structured_opportunity_contract_failures_are_fatal_before_reads(
        self,
    ) -> None:
        opportunity = selected_record("S010-explicit-opportunity-anchor", "1")
        cases = {
            "owner_equals_source_path": dataclasses.replace(
                opportunity,
                canonical_owner=OPPORTUNITY_PATH,
            ),
            "wrong_source_path": dataclasses.replace(
                opportunity,
                path=(
                    "docs/opportunities/reviewed/"
                    "EO-2026-999-wrong-object.yaml"
                ),
            ),
            "wrong_structured_identity": dataclasses.replace(
                opportunity,
                structured_object_identity="engineering-opportunity:EO-2026-999",
                normalized_path_or_object_id="engineering-opportunity:EO-2026-999",
            ),
            "wrong_authority_class": dataclasses.replace(
                opportunity,
                authority_class="canonical_document",
            ),
            "wrong_source_kind": dataclasses.replace(
                opportunity,
                source_kind="document",
            ),
        }

        for name, changed in cases.items():
            self.plan = portable_plan((changed,))
            with self.subTest(case=name), mock.patch.object(
                materialization_module,
                "read_snapshot_blob",
            ) as reader, self.assertRaises(MaterializationContractError):
                materialize_selection_plan(
                    target_repository=ROOT,
                    request=self.request,
                    snapshot=self.snapshot,
                    selection_plan=self.plan,
                )
            reader.assert_not_called()
            self.assertEqual(self.plan.omissions, ())
            self.assertEqual(self.plan.unknowns, ())

    def test_ordinary_canonical_owner_must_equal_selected_path(self) -> None:
        for rule_id, blob_character in (
            ("S030-canonical-repository-authority", "3"),
            ("S040-mandatory-knowledge-authority", "4"),
            ("S050-mandatory-collaboration", "5"),
        ):
            valid = selected_record(rule_id, blob_character)
            self.plan = portable_plan((valid,))
            result = self.materialize()
            self.assertEqual(result.sources[0].plan.canonical_owner, valid.path)

            invalid = dataclasses.replace(
                valid,
                canonical_owner=OPPORTUNITY_OWNER,
            )
            self.plan = portable_plan((invalid,))
            with self.subTest(rule_id=rule_id), mock.patch.object(
                materialization_module,
                "read_snapshot_blob",
            ) as reader, self.assertRaises(MaterializationContractError):
                materialize_selection_plan(
                    target_repository=ROOT,
                    request=self.request,
                    snapshot=self.snapshot,
                    selection_plan=self.plan,
                )
            reader.assert_not_called()

    def test_exact_digest_and_identity_vectors(self) -> None:
        self.assertEqual(
            byte_digest(b"foundation-bytes"),
            ByteDigestRecord(
                "sha256",
                "b9b135cd6eb09da3bbc86f09b6f67e22504409829b5af552710d752f905a1a1b",
            ),
        )
        self.assertEqual(
            source_identifier(
                "docs/example.md",
                "1" * 40,
                "2" * 40,
                "heading:## Example",
            ),
            "src-ed685d51d2becf50",
        )
        payload_digest = byte_digest(b"payload")
        self.assertEqual(
            payload_identifier(payload_digest.value),
            "payload-239f59ed55e737c7",
        )
        individual = {
            "path": "docs/example.md",
            "structured_object_identity": None,
            "selector": {
                "type": "heading",
                "heading_text": "## Example",
                "occurrence": 1,
            },
        }
        self.assertEqual(
            omission_identifier(
                "X010-test",
                "docs/example.md",
                individual,
            ),
            "omit-56a8ab6167561715",
        )

    def test_exact_selectors_transformations_sizes_and_freshness(self) -> None:
        result = self.materialize()
        self.assertEqual(
            tuple(source.plan.rule_id for source in result.sources),
            EXPECTED_ORDER,
        )
        self.assertEqual(
            tuple(source.selector_descriptor for source in result.sources),
            (
                "yaml-fields:/id,/title,/status,/summary",
                "heading:## Initial Milestone",
                "heading:## Source of Truth Hierarchy",
                "heading:### Generated Context",
                "heading:## Responsibilities",
            ),
        )
        self.assertEqual(
            result.sources[0].transformation,
            {
                "type": "yaml_field_selection",
                "selected_fields": ("/id", "/title", "/status", "/summary"),
                "output": "rfc8785-jcs",
                "line_endings": "not_applicable",
            },
        )
        self.assertEqual(
            result.sources[1].transformation,
            {
                "type": "heading_bounded_excerpt",
                "start_heading": "## Initial Milestone",
                "occurrence": 1,
                "end_rule": (
                    "before_next_atx_heading_of_equal_or_greater_level_or_eof"
                ),
                "source_line_endings": "lf",
                "content_change": "none",
            },
        )
        self.assertEqual(
            tuple(source.included_utf8_bytes for source in result.sources),
            tuple(len(payload.content) for payload in result.payloads),
        )
        self.assertEqual(result.sources[0].freshness.status, "current_at_snapshot")
        self.assertEqual(result.sources[0].freshness.rule, "F010-pinned-canonical-source")
        self.assertEqual(result.sources[1].freshness.status, "unknown")
        self.assertEqual(
            result.sources[1].freshness.rule,
            "F020-current-mission-synchronization-unverified",
        )
        self.assertEqual(
            tuple(source.freshness.as_of for source in result.sources),
            (self.request.as_of,) * 5,
        )

    def test_identical_inputs_are_repeatable(self) -> None:
        first = self.materialize()
        self.read_paths.clear()
        second = self.materialize()
        self.assertEqual(first, second)
        self.assertEqual(first.as_dict(), second.as_dict())

    def test_input_contract_failures_occur_before_source_reads(self) -> None:
        blocking = SelectionUnknownPlan(
            rule_id="S010-explicit-opportunity-anchor",
            boundary=OPPORTUNITY_PATH,
            field="required",
            attempted_resolution="Attempted.",
            owner="repository_owner",
            trigger="portable",
            selection_chain=("portable",),
            consequence="Unavailable.",
            blocking=True,
        )
        cases = (
            dataclasses.replace(self.plan, tree="0" * 40),
            dataclasses.replace(
                self.plan,
                selection_policy_digest=DigestRecord(
                    "sha256", "rfc8785-jcs", "0" * 64
                ),
            ),
            dataclasses.replace(self.plan, unknowns=(blocking,)),
        )
        for changed in cases:
            with self.subTest(plan=changed), mock.patch.object(
                materialization_module,
                "read_snapshot_blob",
            ) as reader, self.assertRaises(MaterializationContractError):
                materialize_selection_plan(
                    target_repository=ROOT,
                    request=self.request,
                    snapshot=self.snapshot,
                    selection_plan=changed,
                )
            reader.assert_not_called()

    def test_reread_identity_disagreement_is_fatal(self) -> None:
        self.plan = portable_plan(
            (selected_record("S030-canonical-repository-authority", "3"),)
        )

        def wrong_read(*args: object, **kwargs: object) -> ImmutableBlob:
            del args, kwargs
            record = self.plan.selected[0]
            return ImmutableBlob(
                path=record.path,
                mode=record.mode,
                object_format=record.object_format,
                object_id="9" * 40,
                content=PORTABLE_CONTENTS[record.path],
            )

        with mock.patch.object(
            materialization_module,
            "read_snapshot_blob",
            side_effect=wrong_read,
        ), self.assertRaises(MaterializationIdentityError):
            materialize_selection_plan(
                target_repository=ROOT,
                request=self.request,
                snapshot=self.snapshot,
                selection_plan=self.plan,
            )

    def test_post_plan_selector_failure_is_fatal_and_content_safe(self) -> None:
        self.plan = portable_plan(
            (selected_record("S020-current-mission-milestone", "2"),)
        )
        secret = b"secret-payload-that-must-not-enter-the-exception"

        def bad_read(*args: object, **kwargs: object) -> ImmutableBlob:
            del args, kwargs
            record = self.plan.selected[0]
            return ImmutableBlob(
                path=record.path,
                mode=record.mode,
                object_format=record.object_format,
                object_id=record.blob,
                content=secret,
            )

        with mock.patch.object(
            materialization_module,
            "read_snapshot_blob",
            side_effect=bad_read,
        ), self.assertRaises(MaterializationSourceError) as captured:
            materialize_selection_plan(
                target_repository=ROOT,
                request=self.request,
                snapshot=self.snapshot,
                selection_plan=self.plan,
            )
        self.assertNotIn(secret.decode("utf-8"), str(captured.exception))

    def test_omissions_gain_only_ids_and_unknowns_are_preserved(self) -> None:
        omission = SelectionOmissionPlan(
            rule_id="S040-mandatory-knowledge-authority",
            exclusion_rule_id="X050-disallowed-sensitivity",
            boundary=KNOWLEDGE_PATH,
            individual={
                "path": KNOWLEDGE_PATH,
                "structured_object_identity": None,
                "selector": {
                    "type": "heading",
                    "heading_text": "### Generated Context",
                    "occurrence": 1,
                },
            },
            trigger="portable",
            selection_chain=("portable", "S040"),
            reason="excluded",
            consequence="not included",
            blocking=False,
            reconsideration_condition="authorize a different policy",
        )
        unknown = SelectionUnknownPlan(
            rule_id="S050-mandatory-collaboration",
            boundary=COLLABORATION_PATH,
            field="evidence",
            attempted_resolution="Attempted exact resolution.",
            owner="repository_owner",
            trigger="portable",
            selection_chain=("portable", "S050"),
            consequence="Unresolved nonblocking evidence.",
            blocking=False,
        )
        self.plan = portable_plan(
            (selected_record("S030-canonical-repository-authority", "3"),),
            omissions=(omission,),
            unknowns=(unknown,),
        )
        result = self.materialize()
        self.assertEqual(result.omissions[0].plan, omission)
        self.assertEqual(
            result.omissions[0].id,
            omission_identifier(
                omission.exclusion_rule_id,
                omission.boundary,
                omission.individual,
            ),
        )
        self.assertIs(result.unknowns[0], unknown)

    def test_payload_identifier_collision_is_fatal(self) -> None:
        self.plan = portable_plan(
            (
                selected_record("S030-canonical-repository-authority", "3"),
                selected_record("S040-mandatory-knowledge-authority", "4"),
            )
        )
        with mock.patch.object(
            materialization_module,
            "read_snapshot_blob",
            side_effect=self.fake_read,
        ), mock.patch.object(
            materialization_module,
            "payload_identifier",
            return_value="payload-" + "0" * 16,
        ), self.assertRaises(MaterializationIdentityError):
            materialize_selection_plan(
                target_repository=ROOT,
                request=self.request,
                snapshot=self.snapshot,
                selection_plan=self.plan,
            )

    def test_materialization_module_has_no_forbidden_direct_capability(self) -> None:
        path = (
            ROOT
            / "tools/atlas/platform/context_compilation/materialization.py"
        )
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_roots: set[str] = set()
        called_names: set[str] = set()
        attribute_calls: set[str] = set()
        mutable_assignments = []
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
        for node in tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)) and isinstance(
                node.value, (ast.List, ast.Dict, ast.Set)
            ):
                mutable_assignments.append(ast.dump(node))
        self.assertTrue(
            {
                "os",
                "subprocess",
                "socket",
                "requests",
                "urllib",
                "http",
                "time",
                "datetime",
                "random",
                "secrets",
            }.isdisjoint(imported_roots)
        )
        self.assertNotIn("resolve_snapshot", called_names)
        self.assertTrue(
            {
                "open",
                "write_text",
                "write_bytes",
                "unlink",
                "rename",
                "replace",
                "mkdir",
                "system",
                "popen",
            }.isdisjoint(attribute_calls)
        )
        self.assertEqual(mutable_assignments, [])
        self.assertNotIn("compiler.py", source)
        self.assertNotIn("explanation.py", source)


@unittest.skipUnless(
    os.environ.get("AIDEN_RUN_GUARDED_B2A") == "1",
    "guarded B2a historical integration is separately enabled",
)
class GuardedHistoricalMaterializationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source_status_before = fixture_git(
            ROOT,
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
            "--ignore-submodules=none",
        ).stdout
        self.source_refs_before = tuple(
            fixture_git(ROOT, "rev-parse", ref).stdout
            for ref in ("HEAD", "refs/heads/main", "refs/remotes/origin/main")
        )
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

    def test_guarded_historical_materialization(self) -> None:
        request_value = load_compilation_request(REQUEST_PATH)
        policy_value = load_selection_policy(
            POLICY_PATH,
            request_value["selection_policy"],
        )
        request = CompilationRequest.from_validated_mapping(request_value)
        policy = LoadedPolicy.from_validated_mapping(policy_value)
        snapshot = historical_snapshot()

        original_run_git = snapshot_module._run_git
        commands: list[tuple[str, ...]] = []

        def recording_run_git(
            repository: Path,
            *arguments: str,
        ) -> subprocess.CompletedProcess[bytes]:
            commands.append(tuple(arguments))
            return original_run_git(repository, *arguments)

        with mock.patch.object(
            snapshot_module,
            "_run_git",
            side_effect=recording_run_git,
        ):
            plan = build_bounded_selection_plan(
                target_repository=self.repository,
                request=request,
                selection_policy=policy,
                snapshot=snapshot,
            )
            self.assertEqual(plan.selected[0].path, OPPORTUNITY_PATH)
            self.assertEqual(
                plan.selected[0].structured_object_identity,
                "engineering-opportunity:EO-2026-013",
            )
            self.assertEqual(plan.selected[0].canonical_owner, OPPORTUNITY_OWNER)
            self.assertEqual(
                plan.selected[0].authority_class,
                "structured_repository_object",
            )
            self.assertEqual(plan.selected[0].source_kind, "repository_object")
            self.assertEqual(
                tuple(source.canonical_owner for source in plan.selected[1:]),
                (MISSION_PATH, REPOSITORY_PATH, KNOWLEDGE_PATH, COLLABORATION_PATH),
            )
            materialization_start = len(commands)
            result = materialize_selection_plan(
                target_repository=self.repository,
                request=request,
                snapshot=snapshot,
                selection_plan=plan,
            )

        materialization_commands = commands[materialization_start:]
        self.assertEqual(
            tuple(source.plan.rule_id for source in result.sources),
            EXPECTED_ORDER,
        )
        self.assertEqual(
            {source.plan.path: source.plan.blob for source in result.sources},
            HISTORICAL_BLOBS,
        )
        self.assertEqual(
            {
                source.plan.path: source.source_content_digest.value
                for source in result.sources
            },
            HISTORICAL_SOURCE_DIGESTS,
        )
        self.assertEqual(
            {source.plan.path: source.id for source in result.sources},
            HISTORICAL_SOURCE_IDS,
        )
        payload_by_path = {
            source.plan.path: payload
            for source, payload in zip(result.sources, result.payloads)
        }
        self.assertEqual(
            {
                path: payload.digest.value
                for path, payload in payload_by_path.items()
            },
            HISTORICAL_PAYLOAD_DIGESTS,
        )
        self.assertEqual(
            {
                path: payload.utf8_bytes
                for path, payload in payload_by_path.items()
            },
            HISTORICAL_PAYLOAD_BYTES,
        )
        self.assertEqual(
            {
                path: payload.id
                for path, payload in payload_by_path.items()
            },
            {
                path: f"payload-{digest[:16]}"
                for path, digest in HISTORICAL_PAYLOAD_DIGESTS.items()
            },
        )
        self.assertEqual(result.omissions, ())
        self.assertEqual(result.unknowns, ())
        self.assertEqual(result.sources[0].freshness.status, "current_at_snapshot")
        self.assertEqual(result.sources[1].freshness.status, "unknown")
        self.assertEqual(
            result.sources[1].freshness.rule,
            "F020-current-mission-synchronization-unverified",
        )
        self.assertEqual(
            tuple(source.freshness.as_of for source in result.sources),
            (request.as_of,) * 5,
        )
        self.assertEqual(
            result.sources[0].transformation,
            {
                "type": "yaml_field_selection",
                "selected_fields": ("/id", "/title", "/status", "/summary"),
                "output": "rfc8785-jcs",
                "line_endings": "not_applicable",
            },
        )
        self.assertTrue(
            all(
                source.transformation["type"] == "heading_bounded_excerpt"
                for source in result.sources[1:]
            )
        )

        allowed_families = {
            "config",
            "rev-parse",
            "for-each-ref",
            "status",
            "ls-tree",
            "cat-file",
        }
        self.assertTrue(
            all(command and command[0] in allowed_families for command in commands)
        )
        rendered_commands = "\n".join(" ".join(command) for command in commands)
        self.assertNotIn("show-ref", rendered_commands)
        self.assertNotIn(
            "refs/heads/wip/distinctness-foundation-calibration",
            rendered_commands,
        )
        forbidden_families = {
            "fetch",
            "push",
            "clone",
            "update-ref",
            "symbolic-ref",
            "commit",
            "add",
            "checkout",
            "switch",
            "merge",
            "rebase",
            "reset",
            "clean",
            "branch",
            "worktree",
        }
        self.assertTrue(
            forbidden_families.isdisjoint(
                {command[0] for command in commands}
            )
        )

        materialized_blob_reads = tuple(
            command[2]
            for command in materialization_commands
            if len(command) == 3
            and command[0] == "cat-file"
            and command[1] == "blob"
        )
        expected_paths = (
            OPPORTUNITY_PATH,
            MISSION_PATH,
            REPOSITORY_PATH,
            KNOWLEDGE_PATH,
            COLLABORATION_PATH,
        )
        self.assertEqual(
            materialized_blob_reads,
            tuple(HISTORICAL_BLOBS[path] for path in expected_paths),
        )
        materialized_paths = tuple(
            command[-1]
            for command in materialization_commands
            if command and command[0] == "ls-tree"
        )
        self.assertEqual(materialized_paths, expected_paths)

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
        self.assertEqual(
            fixture_git(
                ROOT,
                "status",
                "--porcelain=v1",
                "-z",
                "--untracked-files=all",
                "--ignore-submodules=none",
            ).stdout,
            self.source_status_before,
        )
        self.assertEqual(
            tuple(
                fixture_git(ROOT, "rev-parse", ref).stdout
                for ref in ("HEAD", "refs/heads/main", "refs/remotes/origin/main")
            ),
            self.source_refs_before,
        )
        print(
            "GUARDED_PRODUCTION_GIT_COMMANDS="
            + json.dumps([list(command) for command in commands], separators=(",", ":"))
        )
        print(
            "GUARDED_MATERIALIZATION_PATHS="
            + json.dumps(list(materialized_paths), separators=(",", ":"))
        )


if __name__ == "__main__":
    unittest.main()
