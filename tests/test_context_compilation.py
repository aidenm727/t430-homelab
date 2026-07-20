import ast
import copy
import dataclasses
import json
import os
import random
import socket
import subprocess
import time
import unittest
from pathlib import Path
from types import MappingProxyType
from unittest import mock

import atlas.platform.context_compilation as context_exports
from atlas.platform.context_compilation import (
    CompilationContractError,
    CompilationResult,
    ProtectedReferenceIdentity,
    compile_context_package,
    control_envelope_bytes,
    control_envelope_surface,
    omission_identifier,
    package_digest,
    package_identity,
    payload_identifier,
    request_digest,
    unknown_identifier,
    validate_compiled_context_package,
)
from atlas.platform.context_compilation import compiler as compiler_module
from atlas.platform.context_compilation import materialization as materialization_module
from atlas.platform.context_compilation.canonical_json import canonicalize
from atlas.platform.context_compilation.inputs import (
    load_budget_policy,
    load_compilation_request,
)
from atlas.platform.context_compilation.materialization import (
    materialize_selection_plan,
)
from atlas.platform.context_compilation.models import (
    CompilationRequest,
    IdentifiedOmission,
    ImmutableBlob,
    LoadedPolicy,
    MaterializationResult,
    RepositoryRequestIdentity,
    SelectionOmissionPlan,
    SelectionUnknownPlan,
)
from atlas.platform.context_compilation.validation import (
    BUDGET_CAPACITY_OMISSION_RULE,
)
from tests import test_context_materialization as b2a_fixtures


ROOT = Path(__file__).resolve().parents[1]
REQUEST = (
    ROOT
    / "tests/fixtures/task_context/requests/"
    "example-eo-2026-013-read-only-assessment-v1.json"
)
BUDGET = (
    ROOT
    / "docs/task-context/policies/budget/"
    "example-utf8-65536-v1.json"
)
TOP_LEVEL_FIELDS = (
    "schema_version",
    "package",
    "compilation",
    "repository",
    "task",
    "declared_constraints",
    "sources",
    "payloads",
    "budget",
    "conflicts",
    "unknowns",
    "omissions",
    "validation",
    "consumer_contract",
)


def accepted_selected_record(rule_id: str, blob_character: str):
    """Return a portable record with the exact accepted B1b2 trace values."""

    record = b2a_fixtures.selected_record(rule_id, blob_character)
    trace = {
        "S010-explicit-opportunity-anchor": (
            "explicit_opportunity_reference",
            "task.opportunity_references[0]",
            (
                "task.opportunity_references[0]",
                "S010-explicit-opportunity-anchor",
            ),
        ),
        "S020-current-mission-milestone": (
            "explicit_mission_reference",
            "task.mission_references[0]",
            (
                "task.mission_references[0]",
                "S020-current-mission-milestone",
            ),
        ),
        "S030-canonical-repository-authority": (
            "allowlisted_related_document",
            "task.opportunity_references[0]",
            (
                "task.opportunity_references[0]",
                "related_documents:outbound",
                b2a_fixtures.REPOSITORY_PATH,
                "S030-canonical-repository-authority",
            ),
        ),
        "S040-mandatory-knowledge-authority": (
            "task_profile_required_source",
            "task.type=architecture_assessment",
            (
                "task.type=architecture_assessment",
                "task_profile=eo-architecture-assessment",
                "S040-mandatory-knowledge-authority",
            ),
        ),
        "S050-mandatory-collaboration": (
            "allowlisted_related_document",
            "task.opportunity_references[0]",
            (
                "task.opportunity_references[0]",
                "related_documents:outbound",
                b2a_fixtures.COLLABORATION_PATH,
                "S050-mandatory-collaboration",
            ),
        ),
    }[rule_id]
    return dataclasses.replace(
        record,
        selection_reason=trace[0],
        trigger=trace[1],
        selection_chain=trace[2],
    )


def build_compilation_inputs(
    *,
    content_overrides: dict[str, bytes] | None = None,
) -> tuple[
    CompilationRequest,
    LoadedPolicy,
    object,
    MaterializationResult,
]:
    request = CompilationRequest.from_validated_mapping(
        load_compilation_request(REQUEST)
    )
    budget_policy = LoadedPolicy.from_validated_mapping(load_budget_policy(BUDGET))
    protected = request.protected_references[0]
    snapshot = dataclasses.replace(
        b2a_fixtures.historical_snapshot(),
        protected_references=(
            ProtectedReferenceIdentity(
                name=protected["name"],
                expected_object=protected["expected_object"],
                actual_object=protected["expected_object"],
                authoritatively_targeted=protected["authoritatively_targeted"],
                selection=protected["selection"],
                matched=True,
                blocking=False,
            ),
        ),
    )
    records = tuple(
        accepted_selected_record(rule_id, str(index))
        for index, rule_id in enumerate(b2a_fixtures.EXPECTED_ORDER, start=1)
    )
    plan = dataclasses.replace(
        b2a_fixtures.portable_plan(records),
        request_task_id=request.task["id"]["value"],
    )
    contents = dict(b2a_fixtures.PORTABLE_CONTENTS)
    if content_overrides:
        contents.update(content_overrides)

    def fake_read(
        target_repository: str | Path,
        read_snapshot: object,
        path: str,
    ) -> ImmutableBlob:
        del target_repository
        if read_snapshot is not snapshot:
            raise AssertionError("unexpected snapshot")
        record = next(item for item in plan.selected if item.path == path)
        return ImmutableBlob(
            path=path,
            mode=record.mode,
            object_format=record.object_format,
            object_id=record.blob,
            content=contents[path],
        )

    with mock.patch.object(
        materialization_module,
        "read_snapshot_blob",
        side_effect=fake_read,
    ):
        materialization = materialize_selection_plan(
            target_repository=ROOT,
            request=request,
            snapshot=snapshot,
            selection_plan=plan,
        )
    return request, budget_policy, snapshot, materialization


def build_hypothetical_optional_inputs(
    *,
    content_overrides: dict[str, bytes] | None = None,
) -> tuple[CompilationRequest, LoadedPolicy, object, MaterializationResult]:
    """Create a hypothetical optional pair only for the private allocator tests."""

    request, budget_policy, snapshot, materialization = build_compilation_inputs(
        content_overrides=content_overrides
    )
    last_source = materialization.sources[-1]
    optional_plan = dataclasses.replace(
        last_source.plan,
        budget_tier="optional_evidence",
    )
    hypothetical = dataclasses.replace(
        materialization,
        sources=materialization.sources[:-1]
        + (dataclasses.replace(last_source, plan=optional_plan),),
    )
    return request, budget_policy, snapshot, hypothetical


def compile_fixture(**kwargs: object) -> CompilationResult:
    request, budget_policy, snapshot, materialization = build_compilation_inputs(
        **kwargs
    )
    return compile_context_package(
        request=request,
        budget_policy=budget_policy,
        snapshot=snapshot,
        materialization=materialization,
    )


class ContextCompilationTests(unittest.TestCase):
    def setUp(self) -> None:
        (
            self.request,
            self.budget_policy,
            self.snapshot,
            self.materialization,
        ) = build_compilation_inputs()

    def compile(self, **overrides: object) -> CompilationResult:
        values = {
            "request": self.request,
            "budget_policy": self.budget_policy,
            "snapshot": self.snapshot,
            "materialization": self.materialization,
        }
        values.update(overrides)
        return compile_context_package(**values)

    def test_historical_shape_compiles_to_a_complete_consumable_package(self) -> None:
        result = self.compile()
        self.assertIsInstance(result, CompilationResult)
        self.assertTrue(result.consumable)
        self.assertEqual(result.non_consumable_reasons, ())
        self.assertTrue(result.validation.valid)
        self.assertTrue(validate_compiled_context_package(result.package).valid)
        self.assertEqual(result.package["schema_version"], "aiden.task-context/v1")
        self.assertEqual(tuple(result.package), TOP_LEVEL_FIELDS)
        self.assertEqual(len(result.package["sources"]), 5)
        self.assertEqual(len(result.package["payloads"]), 5)
        self.assertEqual(result.package["conflicts"], ())

    def test_exact_schema_shapes_are_emitted(self) -> None:
        package = self.compile().package
        self.assertEqual(
            set(package["package"]),
            {
                "id",
                "identity_digest",
                "digest",
                "status",
                "generated",
                "canonical",
                "consumability",
                "non_consumable_reasons",
            },
        )
        self.assertEqual(
            set(package["budget"]),
            {
                "normative_unit",
                "limit_bytes",
                "allocation_order",
                "measurement",
                "outcome",
            },
        )
        self.assertEqual(
            set(package["sources"][0]),
            {
                "id",
                "path",
                "structured_object_identity",
                "selector",
                "priority_tier",
                "selection_rule",
                "selection_reason",
                "trigger",
                "selection_chain",
                "authority_class",
                "canonical_owner",
                "commit",
                "immutable_source_identity",
                "source_content_digest",
                "transformation",
                "freshness",
                "included_utf8_bytes",
                "payload_ref",
            },
        )

    def test_result_is_deeply_immutable(self) -> None:
        result = self.compile()
        self.assertIsInstance(result.package, MappingProxyType)
        self.assertIsInstance(result.package["sources"], tuple)
        self.assertIsInstance(result.package["sources"][0], MappingProxyType)
        with self.assertRaises(TypeError):
            result.package["schema_version"] = "changed"
        with self.assertRaises(TypeError):
            result.package["package"]["status"] = "changed"
        with self.assertRaises(AttributeError):
            result.package["payloads"].append("changed")

    def test_identical_explicit_inputs_are_value_and_byte_deterministic(self) -> None:
        first = self.compile()
        second = self.compile()
        self.assertEqual(first, second)
        self.assertEqual(first.package, second.package)
        self.assertEqual(first.canonical_json, second.canonical_json)
        self.assertEqual(canonicalize(first.package), first.canonical_json)
        self.assertEqual(json.loads(first.canonical_json), json.loads(second.canonical_json))

    def test_request_digest_package_identity_and_integrity_recompute(self) -> None:
        result = self.compile()
        package = result.package
        expected_request = request_digest(self.request.as_dict())
        identity_digest, package_id = package_identity(
            expected_request.value,
            self.snapshot.fingerprint.value,
        )
        self.assertEqual(
            package["compilation"]["request_digest"],
            expected_request.as_dict(),
        )
        self.assertEqual(package["package"]["id"], package_id)
        self.assertEqual(
            package["package"]["identity_digest"], identity_digest.as_dict()
        )
        self.assertEqual(package["package"]["digest"], package_digest(package).as_dict())

    def test_sources_and_payloads_project_exact_content_metadata_and_order(self) -> None:
        package = self.compile().package
        self.assertEqual(
            tuple(source["id"] for source in package["sources"]),
            tuple(source.id for source in self.materialization.sources),
        )
        self.assertEqual(
            tuple(payload["id"] for payload in package["payloads"]),
            tuple(payload.id for payload in self.materialization.payloads),
        )
        for source_value, payload_value, source, payload in zip(
            package["sources"],
            package["payloads"],
            self.materialization.sources,
            self.materialization.payloads,
        ):
            self.assertEqual(source_value["path"], source.plan.path)
            self.assertEqual(source_value["selector"], source.selector_descriptor)
            self.assertEqual(payload_value["content"].encode("utf-8"), payload.content)
            self.assertEqual(payload_value["digest"], payload.digest.as_dict())
            self.assertEqual(source_value["payload_ref"], payload_value["id"])
            self.assertEqual(payload_value["source_ref"], source_value["id"])

    def test_exact_utf8_bytes_and_budget_arithmetic(self) -> None:
        package = self.compile().package
        expected_payload_bytes = sum(
            len(payload.content) for payload in self.materialization.payloads
        )
        measurement = package["budget"]["measurement"]
        self.assertEqual(
            measurement["included_payload_bytes"], expected_payload_bytes
        )
        for payload in package["payloads"]:
            self.assertEqual(
                payload["utf8_bytes"], len(payload["content"].encode("utf-8"))
            )
        self.assertEqual(
            measurement["consumed_bytes"],
            measurement["control_envelope_bytes"]
            + measurement["included_payload_bytes"],
        )
        self.assertEqual(
            measurement["remaining_bytes"],
            package["budget"]["limit_bytes"] - measurement["consumed_bytes"],
        )

    def test_control_envelope_removes_exactly_the_policy_surface(self) -> None:
        package = self.compile().package
        surface = control_envelope_surface(package)
        self.assertNotIn("digest", surface["package"])
        self.assertNotIn("measurement", surface["budget"])
        self.assertTrue(
            all("content" not in payload for payload in surface["payloads"])
        )
        self.assertIn("identity_digest", surface["package"])
        self.assertIn("digest", surface["payloads"][0])
        self.assertIn("validation", surface)
        self.assertIn("consumer_contract", surface)
        self.assertEqual(
            len(canonicalize(surface)),
            package["budget"]["measurement"]["control_envelope_bytes"],
        )
        self.assertEqual(control_envelope_bytes(package), len(canonicalize(surface)))

    def test_mandatory_sources_fit_without_omission(self) -> None:
        package = self.compile().package
        self.assertEqual(package["budget"]["outcome"], "within_budget")
        self.assertEqual(package["omissions"], ())
        self.assertLessEqual(
            package["budget"]["measurement"]["consumed_bytes"], 65536
        )

    def test_mandatory_overflow_returns_valid_non_consumable_result(self) -> None:
        oversized_mission = (
            b"# Current Mission\n\n## Initial Milestone\n\n"
            + (b"x" * 70000)
            + b"\n\n## Later\n"
        )
        result = compile_fixture(
            content_overrides={b2a_fixtures.MISSION_PATH: oversized_mission}
        )
        self.assertFalse(result.consumable)
        self.assertEqual(result.non_consumable_reasons[0], "budget_exceeded")
        self.assertEqual(result.package["budget"]["outcome"], "budget_exceeded")
        self.assertGreater(
            result.package["budget"]["measurement"]["consumed_bytes"], 65536
        )
        self.assertEqual(
            result.package["budget"]["measurement"]["remaining_bytes"], 0
        )
        self.assertTrue(validate_compiled_context_package(result.package).valid)

    def test_private_optional_allocator_includes_a_whole_pair_when_it_fits(self) -> None:
        request, policy, snapshot, materialization = (
            build_hypothetical_optional_inputs()
        )
        package = compiler_module._allocate_context_package(
            request=request,
            budget_policy=policy,
            snapshot=snapshot,
            materialization=materialization,
        )
        self.assertEqual(len(package["sources"]), 5)
        self.assertFalse(
            any(
                omission["rule"] == BUDGET_CAPACITY_OMISSION_RULE
                for omission in package["omissions"]
            )
        )

    def test_private_optional_allocator_omits_a_whole_pair_without_truncation(self) -> None:
        optional_content = (
            b"# Collaboration\n\n## Responsibilities\n\n"
            + ("é" * 30000).encode("utf-8")
            + b"\n"
        )
        request, policy, snapshot, materialization = build_hypothetical_optional_inputs(
            content_overrides={
                b2a_fixtures.COLLABORATION_PATH: optional_content
            },
        )
        omitted_payload = materialization.payloads[-1]
        package = compiler_module._allocate_context_package(
            request=request,
            budget_policy=policy,
            snapshot=snapshot,
            materialization=materialization,
        )
        self.assertEqual(len(package["sources"]), 4)
        self.assertEqual(len(package["payloads"]), 4)
        self.assertNotIn(
            omitted_payload.id,
            tuple(payload["id"] for payload in package["payloads"]),
        )
        capacity = [
            record
            for record in package["omissions"]
            if record["rule"] == BUDGET_CAPACITY_OMISSION_RULE
        ]
        self.assertEqual(len(capacity), 1)
        self.assertEqual(
            capacity[0]["individual"]["payload_utf8_bytes"],
            len(omitted_payload.content),
        )
        self.assertIn("no content was truncated or summarized", capacity[0]["consequence"])
        for payload in package["payloads"]:
            source_payload = next(
                item for item in materialization.payloads if item.id == payload["id"]
            )
            self.assertEqual(payload["content"].encode("utf-8"), source_payload.content)

    def test_private_allocator_rejects_an_earlier_pair_and_keeps_a_later_fit(self) -> None:
        oversized_knowledge = (
            b"# Knowledge\n\n### Generated Context\n\n"
            + (b"x" * 70000)
            + b"\n"
        )
        request, policy, snapshot, materialization = build_compilation_inputs(
            content_overrides={
                b2a_fixtures.KNOWLEDGE_PATH: oversized_knowledge,
            }
        )
        hypothetical_sources = list(materialization.sources)
        for index in (3, 4):
            source = hypothetical_sources[index]
            hypothetical_sources[index] = dataclasses.replace(
                source,
                plan=dataclasses.replace(
                    source.plan,
                    budget_tier="optional_evidence",
                ),
            )
        hypothetical = dataclasses.replace(
            materialization,
            sources=tuple(hypothetical_sources),
        )
        first = compiler_module._allocate_context_package(
            request=request,
            budget_policy=policy,
            snapshot=snapshot,
            materialization=hypothetical,
        )
        second = compiler_module._allocate_context_package(
            request=request,
            budget_policy=policy,
            snapshot=snapshot,
            materialization=hypothetical,
        )
        self.assertEqual(first, second)
        included_rules = tuple(
            source["selection_rule"] for source in first["sources"]
        )
        self.assertNotIn("S040-mandatory-knowledge-authority", included_rules)
        self.assertIn("S050-mandatory-collaboration", included_rules)
        capacity_rules = tuple(
            omission["individual"]["selection_rule"]
            for omission in first["omissions"]
            if omission["rule"] == BUDGET_CAPACITY_OMISSION_RULE
        )
        self.assertEqual(
            capacity_rules,
            ("S040-mandatory-knowledge-authority",),
        )

    def test_public_boundary_rejects_required_collaboration_relabeling(self) -> None:
        collaboration = self.materialization.sources[-1]
        relabeled = dataclasses.replace(
            collaboration,
            plan=dataclasses.replace(
                collaboration.plan,
                budget_tier="optional_evidence",
            ),
        )
        materialization = dataclasses.replace(
            self.materialization,
            sources=self.materialization.sources[:-1] + (relabeled,),
        )
        with self.assertRaisesRegex(
            CompilationContractError,
            "fixed first-slice policy",
        ):
            self.compile(materialization=materialization)

    def test_public_boundary_binds_every_fixed_rule_property_and_completeness(self) -> None:
        source = self.materialization.sources[-1]
        plan_changes = (
            {"rule_id": "S999-unknown"},
            {"rule_type": "task_profile"},
            {"priority_tier": 99},
            {"source_kind": "repository_object"},
            {"sensitivity": "ordinary_personal"},
            {"path": "docs/current-mission.md"},
            {"structured_object_identity": "document:collaboration"},
            {"selector": {"type": "heading", "heading_text": "## Other", "occurrence": 1}},
            {"selection_reason": "changed_reason"},
            {"trigger": "changed_trigger"},
            {"selection_chain": ("changed",)},
            {"authority_class": "structured_repository_object"},
            {"canonical_owner": "docs/current-mission.md"},
        )
        for changes in plan_changes:
            with self.subTest(changes=changes):
                changed_source = dataclasses.replace(
                    source,
                    plan=dataclasses.replace(source.plan, **changes),
                )
                materialization = dataclasses.replace(
                    self.materialization,
                    sources=self.materialization.sources[:-1] + (changed_source,),
                )
                with self.assertRaises(CompilationContractError):
                    self.compile(materialization=materialization)

        omitted = dataclasses.replace(
            self.materialization,
            sources=self.materialization.sources[:-1],
            payloads=self.materialization.payloads[:-1],
        )
        with self.assertRaises(CompilationContractError):
            self.compile(materialization=omitted)

        duplicate = dataclasses.replace(
            self.materialization,
            sources=self.materialization.sources[:-1]
            + (self.materialization.sources[-2],),
            payloads=self.materialization.payloads[:-1]
            + (self.materialization.payloads[-2],),
        )
        with self.assertRaises(CompilationContractError):
            self.compile(materialization=duplicate)

    def test_blocking_unknown_is_stably_identified_and_non_consumable(self) -> None:
        unknown = SelectionUnknownPlan(
            rule_id="U010-test",
            boundary="task.permissions",
            field="declared_constraints.permissions",
            attempted_resolution="Checked the explicit request declaration.",
            owner="repository_owner",
            trigger="portable-test",
            selection_chain=("portable-test", "U010-test"),
            consequence="Execution authority cannot be established.",
            blocking=True,
        )
        materialization = dataclasses.replace(
            self.materialization,
            unknowns=(unknown,),
        )
        package = compiler_module._allocate_context_package(
            request=self.request,
            budget_policy=self.budget_policy,
            snapshot=self.snapshot,
            materialization=materialization,
        )
        self.assertEqual(package["package"]["consumability"], "non_consumable")
        self.assertEqual(
            package["package"]["non_consumable_reasons"],
            ["blocking_unknown"],
        )
        record = package["unknowns"][0]
        self.assertEqual(
            record["id"],
            unknown_identifier(
                record["field"],
                record["attempted_resolution"],
                record["owner"],
                record["consequence"],
                record["blocking"],
            ),
        )

    def test_existing_omission_is_projected_without_semantic_change(self) -> None:
        plan = SelectionOmissionPlan(
            rule_id="X020-provider-memory",
            exclusion_rule_id="X020-provider-or-conversation-memory",
            boundary="ambient-provider-context",
            individual={"candidate": "conversation-memory"},
            trigger="portable-test",
            selection_chain=("portable-test", "X020-provider-memory"),
            reason="Ambient provider context is outside the explicit inputs.",
            consequence="No provider memory enters authoritative context.",
            blocking=False,
            reconsideration_condition="Supply labeled evidence explicitly.",
        )
        materialization = dataclasses.replace(
            self.materialization,
            omissions=(IdentifiedOmission(
                omission_identifier(
                    plan.exclusion_rule_id,
                    plan.boundary,
                    plan.individual,
                ),
                plan,
            ),),
        )
        package = compiler_module._allocate_context_package(
            request=self.request,
            budget_policy=self.budget_policy,
            snapshot=self.snapshot,
            materialization=materialization,
        )
        omission = package["omissions"][0]
        self.assertEqual(omission["boundary"], plan.boundary)
        self.assertEqual(omission["individual"], plan.individual)
        self.assertEqual(omission["rule"], plan.exclusion_rule_id)
        self.assertEqual(omission["reason"], plan.reason)
        self.assertEqual(omission["consequence"], plan.consequence)
        self.assertEqual(
            omission["id"],
            omission_identifier(plan.exclusion_rule_id, plan.boundary, plan.individual),
        )

    def test_identity_mismatches_and_wrong_types_are_rejected(self) -> None:
        mismatched_request = dataclasses.replace(
            self.request,
            repository=RepositoryRequestIdentity(
                self.request.repository.identity,
                "f" * 40,
            ),
        )
        mismatched_policy = dataclasses.replace(
            self.budget_policy,
            reference=dataclasses.replace(
                self.budget_policy.reference,
                version="9.9.9",
            ),
        )
        mismatched_snapshot = dataclasses.replace(self.snapshot, tree="f" * 40)
        mismatched_materialization = dataclasses.replace(
            self.materialization,
            tree="f" * 40,
        )
        cases = (
            {"request": mismatched_request},
            {"budget_policy": mismatched_policy},
            {"snapshot": mismatched_snapshot},
            {"materialization": mismatched_materialization},
            {"request": object()},
            {"budget_policy": object()},
            {"snapshot": object()},
            {"materialization": object()},
        )
        for overrides in cases:
            with self.subTest(overrides=tuple(overrides)), self.assertRaises(
                CompilationContractError
            ):
                self.compile(**overrides)

    def test_inputs_remain_unmodified(self) -> None:
        request_before = canonicalize(self.request.as_dict())
        policy_before = canonicalize(self.budget_policy.value)
        snapshot_before = copy.deepcopy(self.snapshot.as_dict())
        materialization_before = canonicalize(self.materialization.as_dict())
        payloads_before = tuple(payload.content for payload in self.materialization.payloads)
        self.compile()
        self.assertEqual(canonicalize(self.request.as_dict()), request_before)
        self.assertEqual(canonicalize(self.budget_policy.value), policy_before)
        self.assertEqual(self.snapshot.as_dict(), snapshot_before)
        self.assertEqual(
            canonicalize(self.materialization.as_dict()), materialization_before
        )
        self.assertEqual(
            tuple(payload.content for payload in self.materialization.payloads),
            payloads_before,
        )

    def test_compiler_has_no_ambient_or_external_capability(self) -> None:
        source = Path(compiler_module.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        forbidden_modules = {
            "datetime",
            "os",
            "pathlib",
            "random",
            "secrets",
            "socket",
            "subprocess",
            "time",
            "urllib",
        }
        imported = {
            node.names[0].name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
        }
        imported.update(
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )
        self.assertTrue(imported.isdisjoint(forbidden_modules))

        with (
            mock.patch("builtins.open") as open_call,
            mock.patch.object(os, "getenv") as getenv_call,
            mock.patch.object(subprocess, "run") as subprocess_call,
            mock.patch.object(time, "time") as time_call,
            mock.patch.object(random, "random") as random_call,
            mock.patch.object(socket, "socket") as socket_call,
        ):
            result = self.compile()
        self.assertTrue(result.validation.valid)
        for capability in (
            open_call,
            getenv_call,
            subprocess_call,
            time_call,
            random_call,
            socket_call,
        ):
            capability.assert_not_called()

    def test_public_exports_are_minimal_and_immutable(self) -> None:
        self.assertEqual(
            compiler_module.__all__,
            ("CompilationContractError", "compile_context_package"),
        )
        self.assertIsInstance(compiler_module.__all__, tuple)
        self.assertIsInstance(context_exports.__all__, tuple)
        for name in (
            "CompilationContractError",
            "CompilationResult",
            "compile_context_package",
            "validate_compiled_context_package",
        ):
            self.assertIn(name, context_exports.__all__)
        self.assertNotIn("_package_value", context_exports.__all__)


if __name__ == "__main__":
    unittest.main()
