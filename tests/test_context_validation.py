import copy
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from types import MappingProxyType

from atlas.platform.context_compilation.canonical_json import (
    UnsafeIntegerError,
    canonicalize,
    canonicalize_text,
)
from atlas.platform.context_compilation.digests import (
    budget_policy_digest,
    package_identity,
    package_identity_surface,
    request_digest,
    selection_policy_digest,
    sha256_bytes,
    unknown_identifier,
)
from atlas.platform.context_compilation.inputs import (
    load_budget_policy,
    load_compilation_request,
    load_json_file,
    load_selection_policy,
)
from atlas.platform.context_compilation.models import (
    AttributedValue,
    Authority,
    CompilationRequest,
    LoadedPolicy,
    ModelValueError,
    Provenance,
    deep_freeze,
)
from atlas.platform.context_compilation.validation import (
    BUDGET_POLICY_VERSION,
    SELECTION_POLICY_VERSION,
    SENSITIVITY_ORDER,
    SOURCE_BUDGET_TIERS,
    validate_budget_policy,
    validate_compiled_context_package,
    validate_compilation_request,
    validate_context_package,
    validate_selection_policy,
)
from atlas.platform.context_compilation import compiler as compiler_module
from tests import test_context_materialization as b2a_fixtures
from tests.test_context_compilation import (
    build_hypothetical_optional_inputs,
    compile_fixture,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "selection_policy": ROOT / "docs/task-context/schemas/selection-policy-v1.schema.json",
    "budget_policy": ROOT / "docs/task-context/schemas/budget-policy-v1.schema.json",
    "compilation_request": ROOT / "docs/task-context/schemas/compilation-request-v1.schema.json",
    "context_package": ROOT / "docs/task-context/schemas/context-package-v1.schema.json",
}
SCHEMA_IDS = {
    "selection_policy": "urn:aiden-platform:task-context:schema:selection-policy:v1",
    "budget_policy": "urn:aiden-platform:task-context:schema:budget-policy:v1",
    "compilation_request": "urn:aiden-platform:task-context:schema:compilation-request:v1",
    "context_package": "urn:aiden-platform:task-context:schema:context-package:v1",
}
SELECTION = ROOT / "docs/task-context/policies/selection/example-read-only-architecture-assessment-v1.json"
BUDGET = ROOT / "docs/task-context/policies/budget/example-utf8-65536-v1.json"
REQUEST = ROOT / "tests/fixtures/task_context/requests/example-eo-2026-013-read-only-assessment-v1.json"
EXPECTED = ROOT / "tests/fixtures/task_context/expected/example-eo-2026-013-foundation-values-v1.json"


def independent_canonical_json(value: object) -> bytes:
    """Canonicalize the package test domain without production digest helpers."""

    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def independently_finalize_package(package: dict) -> None:
    """Recompute measurement and package digest independently for tamper probes."""

    control = copy.deepcopy(package)
    control["package"].pop("digest", None)
    control["budget"].pop("measurement", None)
    for payload in control["payloads"]:
        payload.pop("content", None)
    control_bytes = len(independent_canonical_json(control))
    payload_bytes = sum(
        len(payload["content"].encode("utf-8"))
        for payload in package["payloads"]
    )
    consumed = control_bytes + payload_bytes
    package["budget"]["measurement"] = {
        "control_envelope_bytes": control_bytes,
        "included_payload_bytes": payload_bytes,
        "consumed_bytes": consumed,
        "remaining_bytes": max(package["budget"]["limit_bytes"] - consumed, 0),
    }

    integrity = copy.deepcopy(package)
    integrity["package"].pop("digest", None)
    package["package"]["digest"] = {
        "algorithm": "sha256",
        "canonicalization": "rfc8785-jcs",
        "value": hashlib.sha256(independent_canonical_json(integrity)).hexdigest(),
    }


def independent_source_identifier(source: dict) -> str:
    surface = {
        "source_identity": {
            "path": source["path"],
            "commit": source["commit"],
            "blob": source["immutable_source_identity"]["value"],
        },
        "selector": source["selector"],
    }
    return "src-" + hashlib.sha256(independent_canonical_json(surface)).hexdigest()[:16]


def independent_omission_identifier(omission: dict) -> str:
    surface = {
        "rule": omission["rule"],
        "boundary": omission["boundary"],
        "individual": omission["individual"],
    }
    return "omit-" + hashlib.sha256(independent_canonical_json(surface)).hexdigest()[:16]


class ContextValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.selection = load_selection_policy(SELECTION)
        cls.budget = load_budget_policy(BUDGET)
        cls.request = load_compilation_request(REQUEST)
        cls.expected = load_json_file(EXPECTED)

    def test_all_schemas_parse_and_have_stable_ids(self) -> None:
        for name, path in SCHEMAS.items():
            with self.subTest(schema=name):
                schema = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
                self.assertEqual(schema["$id"], SCHEMA_IDS[name])

    def test_selection_schema_requires_rule_classifications(self) -> None:
        schema = json.loads(SCHEMAS["selection_policy"].read_text(encoding="utf-8"))
        rule = schema["$defs"]["selectionRule"]
        source = schema["$defs"]["source"]
        self.assertIn("budget_tier", rule["required"])
        self.assertEqual(tuple(rule["properties"]["budget_tier"]["enum"]), SOURCE_BUDGET_TIERS)
        self.assertIn("sensitivity", source["required"])
        self.assertEqual(tuple(source["properties"]["sensitivity"]["enum"]), SENSITIVITY_ORDER)

    def test_policy_versions_and_reference_schema_constants_are_independent(self) -> None:
        self.assertEqual(self.selection["version"], SELECTION_POLICY_VERSION)
        self.assertEqual(self.budget["version"], BUDGET_POLICY_VERSION)
        self.assertTrue(validate_selection_policy(self.selection).valid)
        self.assertTrue(validate_budget_policy(self.budget).valid)

        request_schema = json.loads(
            SCHEMAS["compilation_request"].read_text(encoding="utf-8")
        )
        package_schema = json.loads(
            SCHEMAS["context_package"].read_text(encoding="utf-8")
        )
        self.assertEqual(
            request_schema["properties"]["selection_policy"]["allOf"][1]["properties"]["version"]["const"],
            SELECTION_POLICY_VERSION,
        )
        self.assertEqual(
            request_schema["properties"]["budget_policy"]["allOf"][1]["properties"]["version"]["const"],
            BUDGET_POLICY_VERSION,
        )
        self.assertEqual(
            package_schema["properties"]["compilation"]["properties"]["selection_policy"]["allOf"][1]["properties"]["version"]["const"],
            SELECTION_POLICY_VERSION,
        )
        self.assertEqual(
            package_schema["properties"]["compilation"]["properties"]["budget_policy"]["allOf"][1]["properties"]["version"]["const"],
            BUDGET_POLICY_VERSION,
        )

    def test_source_budget_tiers_match_loaded_budget_allocation_order(self) -> None:
        self.assertEqual(tuple(self.budget["allocation_order"][1:]), SOURCE_BUDGET_TIERS)
        selected_tiers = [rule["budget_tier"] for rule in self.selection["rules"]]
        self.assertTrue(set(selected_tiers).issubset(set(self.budget["allocation_order"])))
        self.assertNotIn(SOURCE_BUDGET_TIERS[-1], selected_tiers)

    def test_runtime_validators_accept_repository_fixtures(self) -> None:
        self.assertTrue(validate_selection_policy(self.selection).valid)
        self.assertTrue(validate_compilation_request(self.request).valid)
        load_selection_policy(SELECTION, self.request["selection_policy"])
        load_budget_policy(BUDGET, self.request["budget_policy"])

    def test_policy_and_request_digest_recomputation(self) -> None:
        self.assertEqual(selection_policy_digest(self.selection).as_dict(), self.selection["digest"])
        self.assertEqual(budget_policy_digest(self.budget).as_dict(), self.budget["digest"])
        self.assertEqual(request_digest(self.request).as_dict(), self.expected["request_digest"])

    def test_expected_foundation_values_match_executable_calculations(self) -> None:
        expected = self.expected
        self.assertTrue(expected["classification"]["foundation_evidence"])
        self.assertFalse(expected["classification"]["compiled_package"])
        self.assertFalse(expected["classification"]["golden_package"])
        for vector in expected["canonicalization_vectors"]:
            with self.subTest(vector=vector["name"]):
                output = canonicalize(vector["input"])
                self.assertEqual(output.decode("utf-8"), vector["canonical_utf8"])
                self.assertEqual(output.hex(), vector["canonical_utf8_hex"])
        for value in expected["safe_integer_boundaries"]["accepted"]:
            self.assertEqual(canonicalize_text(value), str(value))
        for text in expected["safe_integer_boundaries"]["rejected_decimal_strings"]:
            with self.assertRaises(UnsafeIntegerError):
                canonicalize(int(text))
        exact_bytes = expected["exact_byte_sha256_vector"]
        self.assertEqual(sha256_bytes(exact_bytes["input_utf8"].encode()), exact_bytes["value"])
        self.assertEqual(expected["selection_policy_digest"], self.selection["digest"])
        self.assertEqual(expected["budget_policy_digest"], self.budget["digest"])
        self.assertEqual(expected["policy_versions"]["selection"], self.selection["version"])
        self.assertEqual(expected["policy_versions"]["budget"], self.budget["version"])
        self.assertEqual(request_digest(self.request).as_dict(), expected["request_digest"])
        self.assertEqual(self.request["selection_policy"]["digest"], self.selection["digest"])
        self.assertEqual(self.request["budget_policy"]["digest"], self.budget["digest"])

    def test_package_identity_helper_vector(self) -> None:
        vector = self.expected["package_identity_helper"]
        self.assertTrue(vector["foundation_only"])
        surface = package_identity_surface(
            self.expected["request_digest"]["value"],
            vector["synthetic_snapshot_fingerprint"],
        )
        self.assertEqual(surface, vector["surface"])
        self.assertEqual(canonicalize_text(surface), vector["canonical_utf8"])
        identity_digest, package_id = package_identity(
            surface["request_digest"], surface["snapshot_fingerprint"]
        )
        self.assertEqual(identity_digest.as_dict(), vector["identity_digest"])
        self.assertEqual(package_id, vector["package_id"])

    def _structural_package(self) -> dict:
        vector = self.expected["package_identity_helper"]
        zero_digest = {
            "algorithm": "sha256",
            "canonicalization": "rfc8785-jcs",
            "value": "0" * 64,
        }
        return {
            "schema_version": "aiden.task-context/v1",
            "package": {
                "id": vector["package_id"],
                "identity_digest": vector["identity_digest"],
                "digest": zero_digest,
                "status": "checkpoint_a_structural_test_only",
                "generated": True,
                "canonical": False,
                "consumability": "non_consumable",
                "non_consumable_reasons": ["illustrative_not_validated"],
            },
            "compilation": {
                "compiler": copy.deepcopy(self.request["compiler"]),
                "selection_policy": copy.deepcopy(self.request["selection_policy"]),
                "budget_policy": copy.deepcopy(self.request["budget_policy"]),
                "request_digest": copy.deepcopy(self.expected["request_digest"]),
                "as_of": self.request["as_of"],
            },
            "repository": {
                "identity": self.request["repository_request"]["identity"],
                "requested_revision": self.request["repository_request"]["requested_revision"],
                "object_format": "synthetic_not_resolved",
                "commit": "synthetic_not_resolved",
                "tree": "synthetic_not_resolved",
                "snapshot_mode": "clean_committed",
                "snapshot_fingerprint": zero_digest,
                "protected_references": copy.deepcopy(
                    self.request["protected_references"]
                ),
            },
            "task": copy.deepcopy(self.request["task"]),
            "declared_constraints": copy.deepcopy(
                self.request["declared_constraints"]
            ),
            "sources": [],
            "payloads": [],
            "budget": {
                "normative_unit": "utf8_bytes",
                "limit_bytes": 65536,
                "allocation_order": copy.deepcopy(self.budget["allocation_order"]),
                "measurement": {
                    "control_envelope_bytes": 0,
                    "included_payload_bytes": 0,
                    "consumed_bytes": 0,
                    "remaining_bytes": 65536,
                },
                "outcome": "not_compiled",
            },
            "conflicts": [],
            "unknowns": [],
            "omissions": [],
            "validation": {
                "status": "structural_test_only",
                "executable_validation_performed": False,
                "checks": [],
                "errors": [],
                "limitations": ["Checkpoint A does not compile or validate package integrity."],
            },
            "consumer_contract": {
                "version": "aiden.task-context-consumer/v1",
                "must": [],
                "must_not": [],
                "stop_conditions": ["package_is_non_consumable"],
                "live_revalidation_required": [],
            },
        }

    def test_structural_context_package_validation_does_not_claim_compilation(self) -> None:
        package = self._structural_package()
        result = validate_context_package(package)
        self.assertTrue(result.valid, result.issues)
        self.assertEqual(package["package"]["consumability"], "non_consumable")
        self.assertFalse(package["validation"]["executable_validation_performed"])

    def test_complete_executable_validation_accepts_compiler_output(self) -> None:
        result = compile_fixture()
        validation = validate_compiled_context_package(result.package)
        self.assertTrue(validation.valid, validation.issues)
        self.assertTrue(result.package["validation"]["executable_validation_performed"])
        self.assertEqual(result.package["validation"]["status"], "passed")
        self.assertEqual(result.package["package"]["consumability"], "consumable")

    def test_complete_executable_validation_rejects_cross_field_tampering(self) -> None:
        package = json.loads(compile_fixture().canonical_json)

        def changed(mutator):
            value = copy.deepcopy(package)
            mutator(value)
            return value

        cases = (
            (
                "package_identity",
                changed(
                    lambda value: value["package"]["identity_digest"].update(
                        value="0" * 64
                    )
                ),
                "package_identity_digest_mismatch",
            ),
            (
                "package_digest",
                changed(
                    lambda value: value["package"]["digest"].update(
                        value="0" * 64
                    )
                ),
                "package_digest_mismatch",
            ),
            (
                "source_id",
                changed(
                    lambda value: value["sources"][0].update(
                        id="src-0000000000000000"
                    )
                ),
                "source_id_mismatch",
            ),
            (
                "source_digest",
                changed(
                    lambda value: value["sources"][0][
                        "source_content_digest"
                    ].update(value="0" * 64)
                ),
                "package_digest_mismatch",
            ),
            (
                "payload_id",
                changed(
                    lambda value: value["payloads"][0].update(
                        id="payload-0000000000000000"
                    )
                ),
                "payload_id_mismatch",
            ),
            (
                "payload_digest",
                changed(
                    lambda value: value["payloads"][0]["digest"].update(
                        value="0" * 64
                    )
                ),
                "payload_digest_mismatch",
            ),
            (
                "payload_byte_count",
                changed(
                    lambda value: value["payloads"][0].update(
                        utf8_bytes=value["payloads"][0]["utf8_bytes"] + 1
                    )
                ),
                "payload_size_mismatch",
            ),
            (
                "source_byte_count",
                changed(
                    lambda value: value["sources"][0].update(
                        included_utf8_bytes=value["sources"][0][
                            "included_utf8_bytes"
                        ]
                        + 1
                    )
                ),
                "source_size_mismatch",
            ),
            (
                "source_payload_linkage",
                changed(
                    lambda value: value["sources"][0].update(
                        payload_ref=value["payloads"][1]["id"]
                    )
                ),
                "source_payload_linkage",
            ),
            (
                "ordering",
                changed(
                    lambda value: value["sources"].__setitem__(
                        slice(0, 2),
                        [value["sources"][1], value["sources"][0]],
                    )
                ),
                "source_ordering",
            ),
            (
                "budget_measurement",
                changed(
                    lambda value: value["budget"]["measurement"].update(
                        consumed_bytes=value["budget"]["measurement"][
                            "consumed_bytes"
                        ]
                        + 1
                    )
                ),
                "budget_measurement_mismatch",
            ),
            (
                "consumer_contract",
                changed(
                    lambda value: value["consumer_contract"]["must"].pop()
                ),
                "consumer_contract_mismatch",
            ),
            (
                "generated_classification",
                changed(lambda value: value["package"].update(generated=False)),
                "classification",
            ),
            (
                "canonical_classification",
                changed(lambda value: value["package"].update(canonical=True)),
                "classification",
            ),
            (
                "consumability_reasons",
                changed(
                    lambda value: value["package"][
                        "non_consumable_reasons"
                    ].append("blocking_unknown")
                ),
                "consumability_reasons_mismatch",
            ),
        )
        for name, tampered, expected_code in cases:
            with self.subTest(case=name):
                result = validate_compiled_context_package(tampered)
                self.assertFalse(result.valid)
                self.assertIn(
                    expected_code,
                    {issue.code for issue in result.issues},
                    result.issues,
                )

    def test_unknown_identifier_has_an_independent_frozen_vector(self) -> None:
        surface = {
            "field": "task.permissions",
            "attempted_resolution": "checked explicit input",
            "owner": "repository_owner",
            "consequence": "authority unavailable",
            "blocking": True,
        }
        self.assertEqual(
            independent_canonical_json(surface),
            b'{"attempted_resolution":"checked explicit input","blocking":true,'
            b'"consequence":"authority unavailable","field":"task.permissions",'
            b'"owner":"repository_owner"}',
        )
        expected = "unknown-ba14e75cf8ead556"
        self.assertEqual(
            "unknown-"
            + hashlib.sha256(independent_canonical_json(surface)).hexdigest()[:16],
            expected,
        )
        self.assertEqual(unknown_identifier(**surface), expected)

    def test_coherent_fixed_rule_tampering_is_independently_refinalized_and_rejected(
        self,
    ) -> None:
        original = json.loads(compile_fixture().canonical_json)

        def selector_tamper(value: dict) -> None:
            source = value["sources"][0]
            source["selector"] = "yaml-fields:/id,/title,/status"
            source["id"] = independent_source_identifier(source)
            value["payloads"][0]["source_ref"] = source["id"]

        def remove_mandatory(value: dict) -> None:
            value["sources"].pop()
            value["payloads"].pop()

        cases = (
            (
                "canonical_owner",
                lambda value: value["sources"][0].update(
                    canonical_owner="tampered-owner"
                ),
                "fixed_source_contract_mismatch",
            ),
            ("selector", selector_tamper, "fixed_source_contract_mismatch"),
            (
                "priority_tier",
                lambda value: value["sources"][0].update(priority_tier=99),
                "fixed_source_contract_mismatch",
            ),
            (
                "freshness_rule",
                lambda value: value["sources"][0]["freshness"].update(
                    rule="F999-tampered"
                ),
                "freshness_contract_mismatch",
            ),
            (
                "freshness_status",
                lambda value: value["sources"][0]["freshness"].update(
                    status="stale"
                ),
                "freshness_contract_mismatch",
            ),
            (
                "selection_chain",
                lambda value: value["sources"][0].update(
                    selection_chain=["tampered", "chain"]
                ),
                "fixed_source_contract_mismatch",
            ),
            (
                "mandatory_source_removal",
                remove_mandatory,
                "mandatory_source_completeness",
            ),
            (
                "mandatory_source_relabeling",
                lambda value: value["sources"][-1].update(
                    selection_rule="S999-fabricated-optional"
                ),
                "unsupported_source_rule",
            ),
        )
        for name, mutator, expected_code in cases:
            with self.subTest(case=name):
                tampered = copy.deepcopy(original)
                mutator(tampered)
                independently_finalize_package(tampered)
                canonical_bytes = independent_canonical_json(tampered)
                self.assertEqual(json.loads(canonical_bytes), tampered)
                result = validate_compiled_context_package(tampered)
                self.assertFalse(result.valid)
                self.assertIn(
                    expected_code,
                    {issue.code for issue in result.issues},
                    result.issues,
                )

    def test_payload_integrity_and_whole_source_authenticity_boundary_is_explicit(
        self,
    ) -> None:
        original = json.loads(compile_fixture().canonical_json)
        limitation = (
            "Excerpt-only package validation independently verifies payload bytes "
            "and payload digests; whole-source content digests are compiler-carried "
            "claims that require immutable Git blob revalidation outside the package."
        )
        live_requirement = (
            "verify_immutable_git_blob_identity_and_whole_source_content_digest_"
            "before_relying_on_whole_source_authenticity"
        )
        self.assertIn(limitation, original["validation"]["limitations"])
        self.assertEqual(
            original["consumer_contract"]["live_revalidation_required"],
            [live_requirement],
        )
        self.assertIn(
            "verify_payload_digests_and_treat_whole_source_digests_as_claims_"
            "pending_immutable_source_revalidation",
            original["consumer_contract"]["must"],
        )
        self.assertNotIn(
            "source_payload_identity_integrity_linkage_and_ordering",
            [check["invariant"] for check in original["validation"]["checks"]],
        )

        payload_tampered = copy.deepcopy(original)
        payload_tampered["payloads"][0]["digest"]["value"] = "0" * 64
        independently_finalize_package(payload_tampered)
        payload_result = validate_compiled_context_package(payload_tampered)
        self.assertFalse(payload_result.valid)
        self.assertIn(
            "payload_digest_mismatch",
            {issue.code for issue in payload_result.issues},
        )

        coherent_source_claim = copy.deepcopy(original)
        coherent_source_claim["sources"][0]["source_content_digest"]["value"] = (
            "0" * 64
        )
        independently_finalize_package(coherent_source_claim)
        source_result = validate_compiled_context_package(coherent_source_claim)
        self.assertTrue(source_result.valid, source_result.issues)

        contract_cases = (
            lambda value: value["consumer_contract"][
                "live_revalidation_required"
            ].clear(),
            lambda value: value["consumer_contract"][
                "live_revalidation_required"
            ].__setitem__(0, "weaker-revalidation"),
            lambda value: value["validation"]["limitations"].remove(limitation),
        )
        for mutator in contract_cases:
            tampered = copy.deepcopy(original)
            mutator(tampered)
            independently_finalize_package(tampered)
            result = validate_compiled_context_package(tampered)
            self.assertFalse(result.valid)
            self.assertTrue(
                {"consumer_contract_mismatch", "validation_record_mismatch"}
                & {issue.code for issue in result.issues},
                result.issues,
            )

    def test_capacity_omission_coherent_tampering_is_rejected_field_by_field(
        self,
    ) -> None:
        oversized = (
            b"# Collaboration\n\n## Responsibilities\n\n"
            + (b"x" * 70000)
            + b"\n"
        )
        request, policy, snapshot, materialization = (
            build_hypothetical_optional_inputs(
                content_overrides={b2a_fixtures.COLLABORATION_PATH: oversized}
            )
        )
        original = compiler_module._allocate_context_package(
            request=request,
            budget_policy=policy,
            snapshot=snapshot,
            materialization=materialization,
        )
        independently_finalize_package(original)
        capacity = original["omissions"][0]
        self.assertEqual(capacity["rule"], "B2b-budget-capacity")
        self.assertEqual(capacity["record_type"], "individual")
        self.assertFalse(capacity["blocking"])
        self.assertEqual(
            set(capacity["individual"]),
            {
                "source_id",
                "payload_id",
                "path",
                "structured_object_identity",
                "selector",
                "selection_rule",
                "budget_tier",
                "commit",
                "immutable_source_identity",
                "source_content_digest",
                "payload_utf8_bytes",
                "payload_digest",
            },
        )
        self.assertFalse(validate_compiled_context_package(original).valid)

        def change_individual(value: dict, field: str, replacement: object) -> None:
            omission = value["omissions"][0]
            omission["individual"][field] = replacement
            omission["id"] = independent_omission_identifier(omission)

        def change_byte_count(value: dict) -> None:
            omission = value["omissions"][0]
            changed = omission["individual"]["payload_utf8_bytes"] + 1
            omission["individual"]["payload_utf8_bytes"] = changed
            omission["consequence"] = (
                f"Excluded the complete optional {changed}-byte payload; "
                "no content was truncated or summarized."
            )
            omission["id"] = independent_omission_identifier(omission)

        cases = (
            (
                "reason",
                lambda value: value["omissions"][0].update(reason="tampered"),
                "budget_omission_reason",
            ),
            (
                "consequence",
                lambda value: value["omissions"][0].update(
                    consequence="tampered"
                ),
                "budget_omission_consequence",
            ),
            (
                "reconsideration",
                lambda value: value["omissions"][0].update(
                    reconsideration_condition="tampered"
                ),
                "budget_omission_reconsideration",
            ),
            (
                "source_id",
                lambda value: change_individual(
                    value, "source_id", "src-0000000000000000"
                ),
                "budget_omission_source_id",
            ),
            (
                "payload_id",
                lambda value: change_individual(
                    value, "payload_id", "payload-0000000000000000"
                ),
                "budget_omission_payload_id",
            ),
            (
                "byte_count",
                change_byte_count,
                "budget_omission_rule_not_optional",
            ),
            (
                "budget_tier",
                lambda value: change_individual(
                    value, "budget_tier", "mandatory_authoritative_sources"
                ),
                "budget_omission_rule_projection",
            ),
        )
        for name, mutator, expected_code in cases:
            with self.subTest(case=name):
                tampered = copy.deepcopy(original)
                mutator(tampered)
                independently_finalize_package(tampered)
                result = validate_compiled_context_package(tampered)
                self.assertFalse(result.valid)
                self.assertIn(
                    expected_code,
                    {issue.code for issue in result.issues},
                    result.issues,
                )

    def test_malformed_unknown_and_omission_records_fail_safe(self) -> None:
        original = json.loads(compile_fixture().canonical_json)
        valid_unknown = {
            "id": "unknown-0000000000000000",
            "field": "task.permissions",
            "attempted_resolution": "checked explicit input",
            "owner": "repository_owner",
            "consequence": "authority unavailable",
            "blocking": True,
        }
        valid_omission = {
            "id": "omit-0000000000000000",
            "record_type": "individual",
            "boundary": "ambient-provider-context",
            "individual": {"candidate": "conversation-memory"},
            "rule": "X020-provider-or-conversation-memory",
            "reason": "outside explicit inputs",
            "consequence": "not selected",
            "blocking": False,
            "reconsideration_condition": "supply explicit evidence",
        }

        cases: list[tuple[str, dict]] = []
        for field in ("field", "attempted_resolution", "owner", "consequence"):
            package = copy.deepcopy(original)
            record = copy.deepcopy(valid_unknown)
            record[field] = ""
            package["unknowns"].append(record)
            cases.append((f"empty_unknown_{field}", package))
        malformed_unknown_id = copy.deepcopy(original)
        malformed_unknown_id["unknowns"].append(copy.deepcopy(valid_unknown))
        cases.append(("malformed_unknown_id_surface", malformed_unknown_id))

        for field in ("rule", "boundary"):
            package = copy.deepcopy(original)
            record = copy.deepcopy(valid_omission)
            record[field] = ""
            package["omissions"].append(record)
            cases.append((f"empty_omission_{field}", package))
        malformed_individual = copy.deepcopy(original)
        record = copy.deepcopy(valid_omission)
        record["individual"] = ["not", "a", "mapping"]
        malformed_individual["omissions"].append(record)
        cases.append(("malformed_omission_individual", malformed_individual))
        malformed_omission_id = copy.deepcopy(original)
        malformed_omission_id["omissions"].append(copy.deepcopy(valid_omission))
        cases.append(("malformed_omission_identity_surface", malformed_omission_id))
        malformed_capacity_identity = copy.deepcopy(original)
        record = copy.deepcopy(valid_omission)
        record.update(
            rule="B2b-budget-capacity",
            boundary=b2a_fixtures.COLLABORATION_PATH,
            individual={"source_id": []},
        )
        malformed_capacity_identity["omissions"].append(record)
        cases.append(
            ("malformed_capacity_individual_identity", malformed_capacity_identity)
        )

        for name, package in cases:
            with self.subTest(case=name):
                result = validate_compiled_context_package(package)
                self.assertFalse(result.valid)

    def _assert_coherent_omission_identity_contract_rejection(
        self,
        *,
        record_type: str,
        individual: object,
    ) -> None:
        package = json.loads(compile_fixture().canonical_json)
        self.assertTrue(validate_compiled_context_package(package).valid)
        omission = {
            "id": "",
            "record_type": record_type,
            "boundary": "ambient-provider-context",
            "individual": individual,
            "rule": "X020-provider-or-conversation-memory",
            "reason": "outside explicit inputs",
            "consequence": "not selected",
            "blocking": False,
            "reconsideration_condition": "supply explicit evidence",
        }
        omission["id"] = independent_omission_identifier(omission)
        package["omissions"].append(omission)
        independently_finalize_package(package)
        canonical_bytes = independent_canonical_json(package)
        consumer_value = json.loads(canonical_bytes)

        try:
            result = validate_compiled_context_package(consumer_value)
        except Exception as error:  # pragma: no cover - assertion reports boundary leaks
            self.fail(f"validator raised {type(error).__name__}: {error}")

        issue_codes = {issue.code for issue in result.issues}
        self.assertFalse(result.valid)
        self.assertIn("omission_individual_identity", issue_codes)
        self.assertNotIn("package_digest_mismatch", issue_codes)

    def test_individual_omission_with_null_identity_is_rejected_coherently(self) -> None:
        self._assert_coherent_omission_identity_contract_rejection(
            record_type="individual",
            individual=None,
        )

    def test_individual_omission_with_empty_identity_is_rejected_coherently(self) -> None:
        self._assert_coherent_omission_identity_contract_rejection(
            record_type="individual",
            individual={},
        )

    def test_individual_omission_with_non_mapping_identity_is_rejected_coherently(
        self,
    ) -> None:
        self._assert_coherent_omission_identity_contract_rejection(
            record_type="individual",
            individual=["not", "a", "mapping"],
        )

    def test_policy_class_omission_with_mapping_identity_is_rejected_coherently(
        self,
    ) -> None:
        self._assert_coherent_omission_identity_contract_rejection(
            record_type="policy_class",
            individual={"candidate": "conversation-memory"},
        )

    def test_request_and_package_policy_reference_versions_are_required(self) -> None:
        request_selection = copy.deepcopy(self.request)
        request_selection["selection_policy"]["version"] = BUDGET_POLICY_VERSION
        self.assertFalse(validate_compilation_request(request_selection).valid)
        request_budget = copy.deepcopy(self.request)
        request_budget["budget_policy"]["version"] = SELECTION_POLICY_VERSION
        self.assertFalse(validate_compilation_request(request_budget).valid)

        package_selection = self._structural_package()
        package_selection["compilation"]["selection_policy"]["version"] = BUDGET_POLICY_VERSION
        self.assertFalse(validate_context_package(package_selection).valid)
        package_budget = self._structural_package()
        package_budget["compilation"]["budget_policy"]["version"] = SELECTION_POLICY_VERSION
        self.assertFalse(validate_context_package(package_budget).valid)

    def test_typed_models_are_deeply_immutable_copies(self) -> None:
        source_request = copy.deepcopy(self.request)
        source_policy = copy.deepcopy(self.selection)
        typed_request = CompilationRequest.from_validated_mapping(source_request)
        typed_policy = LoadedPolicy.from_validated_mapping(source_policy)

        self.assertIsInstance(typed_request.task, MappingProxyType)
        self.assertIsInstance(typed_request.task["scope"]["value"], tuple)
        self.assertIsInstance(typed_request.protected_references[0], MappingProxyType)
        self.assertIsInstance(typed_policy.value, MappingProxyType)
        with self.assertRaises(TypeError):
            typed_request.task["goal"] = "changed"
        with self.assertRaises(TypeError):
            typed_request.task["goal"]["value"] = "changed"
        with self.assertRaises(AttributeError):
            typed_request.task["scope"]["value"].append("changed")
        with self.assertRaises(TypeError):
            typed_policy.value["task_profile"] = "changed"

        source_request["task"]["scope"]["value"][0] = "changed after construction"
        source_request["protected_references"][0]["selection"] = "allowed"
        source_policy["rules"][0]["source"]["kind"] = "changed"
        self.assertEqual(
            typed_request.task["scope"]["value"][0],
            self.request["task"]["scope"]["value"][0],
        )
        self.assertEqual(
            typed_request.protected_references[0]["selection"], "forbidden"
        )
        self.assertEqual(
            typed_policy.value["rules"][0]["source"]["kind"],
            "repository_object",
        )

    def test_attributed_values_freeze_and_model_boundary_rejects_invalid_values(self) -> None:
        source = {"nested": ["unchanged"]}
        attributed = AttributedValue(
            state="known",
            value=source,
            authority=Authority("human_declaration", "repository_owner"),
            provenance=Provenance("request", "task.goal"),
        )
        source["nested"][0] = "changed"
        self.assertEqual(attributed.value["nested"], ("unchanged",))
        with self.assertRaises(TypeError):
            attributed.value["new"] = "value"
        for invalid in ({1: "non-string key"}, {"unsafe": 9007199254740992}, {"set": {1}}):
            with self.subTest(invalid=invalid), self.assertRaises(ModelValueError):
                deep_freeze(invalid)

    def test_context_package_schema_constants_and_boundaries_are_enforced(self) -> None:
        cases = []
        invalid_id = self._structural_package()
        invalid_id["package"]["id"] = "tcp-not-hex"
        cases.append(("package_id", invalid_id))
        invalid_generated = self._structural_package()
        invalid_generated["package"]["generated"] = False
        cases.append(("generated", invalid_generated))
        invalid_canonical = self._structural_package()
        invalid_canonical["package"]["canonical"] = True
        cases.append(("canonical", invalid_canonical))
        invalid_snapshot = self._structural_package()
        invalid_snapshot["repository"]["snapshot_mode"] = "dirty"
        cases.append(("snapshot_mode", invalid_snapshot))
        invalid_compiler = self._structural_package()
        invalid_compiler["compilation"]["compiler"]["version"] = ""
        cases.append(("compiler_version", invalid_compiler))
        invalid_consumer = self._structural_package()
        invalid_consumer["consumer_contract"]["version"] = "aiden.task-context-consumer/v2"
        cases.append(("consumer_contract", invalid_consumer))
        invalid_digest = self._structural_package()
        invalid_digest["package"]["digest"]["canonicalization"] = "plain-json"
        cases.append(("digest_canonicalization", invalid_digest))
        invalid_digest_value = self._structural_package()
        invalid_digest_value["package"]["digest"]["value"] = "A" * 64
        cases.append(("digest_pattern", invalid_digest_value))
        boolean_bytes = self._structural_package()
        boolean_bytes["budget"]["limit_bytes"] = True
        cases.append(("boolean_integer", boolean_bytes))
        negative_bytes = self._structural_package()
        negative_bytes["budget"]["measurement"]["remaining_bytes"] = -1
        cases.append(("negative_integer", negative_bytes))

        for name, package in cases:
            with self.subTest(case=name):
                self.assertFalse(validate_context_package(package).valid)

    def test_tampering_is_detected(self) -> None:
        policy = copy.deepcopy(self.selection)
        policy["task_profile"] = "tampered"
        self.assertFalse(validate_selection_policy(policy).valid)

        request = copy.deepcopy(self.request)
        request["task"]["goal"]["value"] = "tampered"
        self.assertNotEqual(request_digest(request).as_dict(), self.expected["request_digest"])

        expected = copy.deepcopy(self.expected)
        expected["package_identity_helper"]["package_id"] = "tcp-000000000000000000000000"
        _, actual_id = package_identity(
            expected["request_digest"]["value"],
            expected["package_identity_helper"]["synthetic_snapshot_fingerprint"],
        )
        self.assertNotEqual(actual_id, expected["package_identity_helper"]["package_id"])

        package = self._structural_package()
        package["package"]["unexpected"] = True
        self.assertFalse(validate_context_package(package).valid)

        nested_type = copy.deepcopy(self.request)
        nested_type["task"]["goal"]["value"] = 1.0
        self.assertFalse(validate_compilation_request(nested_type).valid)

        package = self._structural_package()
        package["sources"].append({"unexpected": True})
        self.assertFalse(validate_context_package(package).valid)

    def test_no_ambient_dependency_is_required(self) -> None:
        code = (
            "from atlas.platform.context_compilation.canonical_json import canonicalize; "
            "from atlas.platform.context_compilation.inputs import load_json_bytes; "
            "assert canonicalize(load_json_bytes(b'{\\\"b\\\":1,\\\"a\\\":2}')) == b'{\\\"a\\\":2,\\\"b\\\":1}'"
        )
        environment = {"PYTHONPATH": str(ROOT / "tools")}
        result = subprocess.run(
            [sys.executable, "-S", "-c", code],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
