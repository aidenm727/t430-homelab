import copy
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
    validate_compilation_request,
    validate_context_package,
    validate_selection_policy,
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
