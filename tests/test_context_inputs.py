import copy
import json
import tempfile
import unittest
from pathlib import Path

from atlas.platform.context_compilation.inputs import (
    DuplicateKeyError,
    InputContractError,
    InputEncodingError,
    InputSyntaxError,
    UnsupportedJSONNumberError,
    load_budget_policy,
    load_compilation_request,
    load_json_bytes,
    load_selection_policy,
)
from atlas.platform.context_compilation.canonical_json import canonicalize
from atlas.platform.context_compilation.digests import (
    budget_policy_digest,
    selection_policy_digest,
)
from atlas.platform.context_compilation.models import CompilationRequest, LoadedPolicy
from atlas.platform.context_compilation.validation import (
    BUDGET_POLICY_VERSION,
    SELECTION_POLICY_VERSION,
    SENSITIVITY_ORDER,
    SOURCE_BUDGET_TIERS,
)


ROOT = Path(__file__).resolve().parents[1]
SELECTION = ROOT / "docs/task-context/policies/selection/example-read-only-architecture-assessment-v1.json"
BUDGET = ROOT / "docs/task-context/policies/budget/example-utf8-65536-v1.json"
REQUEST = ROOT / "tests/fixtures/task_context/requests/example-eo-2026-013-read-only-assessment-v1.json"


class ContextInputTests(unittest.TestCase):
    def _write(self, value: object) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "input.json"
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return path

    def test_duplicate_keys_at_top_and_nested_depth_are_rejected(self) -> None:
        for value in (b'{"a":1,"a":2}', b'{"outer":{"a":1,"a":2}}'):
            with self.subTest(value=value), self.assertRaises(DuplicateKeyError):
                load_json_bytes(value)

    def test_floats_nan_and_infinity_are_rejected(self) -> None:
        for value in (b"1.0", b"1e0", b"NaN", b"Infinity", b"-Infinity"):
            with self.subTest(value=value), self.assertRaises(UnsupportedJSONNumberError):
                load_json_bytes(value)

    def test_invalid_utf8_and_bom_are_rejected(self) -> None:
        with self.assertRaises(InputEncodingError):
            load_json_bytes(b'"\xff"')
        with self.assertRaises(InputEncodingError):
            load_json_bytes(b"\xef\xbb\xbf{}")

    def test_invalid_unicode_scalar_is_rejected(self) -> None:
        with self.assertRaises(InputSyntaxError):
            load_json_bytes(b'"\\ud800"')

    def test_repository_selection_budget_and_request_load(self) -> None:
        selection = load_selection_policy(SELECTION)
        budget = load_budget_policy(BUDGET)
        request = load_compilation_request(REQUEST)
        self.assertEqual(selection["version"], SELECTION_POLICY_VERSION)
        self.assertEqual(budget["version"], BUDGET_POLICY_VERSION)
        self.assertEqual(request["selection_policy"]["version"], SELECTION_POLICY_VERSION)
        self.assertEqual(request["budget_policy"]["version"], BUDGET_POLICY_VERSION)
        self.assertEqual(selection["id"], request["selection_policy"]["id"])
        self.assertEqual(budget["id"], request["budget_policy"]["id"])
        load_selection_policy(SELECTION, request["selection_policy"])
        load_budget_policy(BUDGET, request["budget_policy"])

    def test_first_replay_rule_classifications_are_exact(self) -> None:
        selection = load_selection_policy(SELECTION)
        expected_tiers = {
            "S010-explicit-opportunity-anchor": "mandatory_authoritative_sources",
            "S020-current-mission-milestone": "mandatory_authoritative_sources",
            "S030-canonical-repository-authority": "required_supporting_sources",
            "S040-mandatory-knowledge-authority": "required_supporting_sources",
            "S050-mandatory-collaboration": "required_supporting_sources",
        }
        self.assertEqual(
            {rule["id"]: rule["budget_tier"] for rule in selection["rules"]},
            expected_tiers,
        )
        self.assertEqual(
            [rule["source"]["sensitivity"] for rule in selection["rules"]],
            [SENSITIVITY_ORDER[0]] * 5,
        )
        self.assertNotIn(SOURCE_BUDGET_TIERS[-1], expected_tiers.values())

    def test_validated_mappings_construct_exact_typed_values(self) -> None:
        selection = load_selection_policy(SELECTION)
        request = load_compilation_request(REQUEST)
        typed_policy = LoadedPolicy.from_validated_mapping(selection)
        typed_request = CompilationRequest.from_validated_mapping(request)

        self.assertEqual(canonicalize(typed_policy.value), canonicalize(selection))
        self.assertEqual(canonicalize(typed_request.as_dict()), canonicalize(request))
        self.assertEqual(
            typed_policy.reference.as_dict(),
            {
                "id": selection["id"],
                "version": selection["version"],
                "digest": selection["digest"],
            },
        )
        self.assertEqual(typed_request.compiler.identity, request["compiler"]["identity"])
        self.assertEqual(
            typed_request.repository.requested_revision,
            request["repository_request"]["requested_revision"],
        )

    def test_unknown_field_and_missing_required_field_are_rejected(self) -> None:
        request = json.loads(REQUEST.read_text(encoding="utf-8"))
        unknown = copy.deepcopy(request)
        unknown["ambient"] = "forbidden"
        missing = copy.deepcopy(request)
        del missing["task"]["goal"]
        for value in (unknown, missing):
            with self.subTest(keys=value.keys()), self.assertRaises(InputContractError):
                load_compilation_request(self._write(value))

    def test_unsupported_schema_version_is_rejected(self) -> None:
        request = json.loads(REQUEST.read_text(encoding="utf-8"))
        request["schema_version"] = "aiden.task-context.compilation-request/v2"
        with self.assertRaises(InputContractError):
            load_compilation_request(self._write(request))

        selection = json.loads(SELECTION.read_text(encoding="utf-8"))
        selection["version"] = "2.0.0"
        with self.assertRaises(InputContractError):
            load_selection_policy(self._write(selection))

    def test_embedded_and_expected_policy_digest_mismatches_are_rejected(self) -> None:
        selection = json.loads(SELECTION.read_text(encoding="utf-8"))
        selection["digest"]["value"] = "0" * 64
        with self.assertRaises(InputContractError):
            load_selection_policy(self._write(selection))

        request = json.loads(REQUEST.read_text(encoding="utf-8"))
        reference = copy.deepcopy(request["selection_policy"])
        reference["digest"]["value"] = "f" * 64
        with self.assertRaises(InputContractError):
            load_selection_policy(SELECTION, reference)

    def test_missing_compiler_identity_or_version_is_rejected(self) -> None:
        request = json.loads(REQUEST.read_text(encoding="utf-8"))
        for field in ("identity", "version"):
            tampered = copy.deepcopy(request)
            del tampered["compiler"][field]
            with self.subTest(field=field), self.assertRaises(InputContractError):
                load_compilation_request(self._write(tampered))

    def test_empty_schema_required_request_strings_are_rejected(self) -> None:
        request = json.loads(REQUEST.read_text(encoding="utf-8"))
        paths = (
            ("repository_request", "identity"),
            ("repository_request", "requested_revision"),
            ("compiler", "identity"),
            ("compiler", "version"),
        )
        for parent, field in paths:
            tampered = copy.deepcopy(request)
            tampered[parent][field] = ""
            with self.subTest(path=f"{parent}.{field}"), self.assertRaises(InputContractError):
                load_compilation_request(self._write(tampered))

        for parent, field in (("authority", "owner"), ("provenance", "source")):
            tampered = copy.deepcopy(request)
            tampered["task"]["goal"][parent][field] = ""
            with self.subTest(path=f"task.goal.{parent}.{field}"), self.assertRaises(InputContractError):
                load_compilation_request(self._write(tampered))

    def test_invalid_rfc3339_as_of_is_rejected(self) -> None:
        request = json.loads(REQUEST.read_text(encoding="utf-8"))
        for value in (
            "2026-07-15",
            "2026-07-15T15:40:26",
            "2026-99-99T15:40:26Z",
            "now",
            "",
        ):
            tampered = copy.deepcopy(request)
            tampered["as_of"] = value
            with self.subTest(value=value), self.assertRaises(InputContractError):
                load_compilation_request(self._write(tampered))

    def test_invalid_protected_reference_records_are_rejected(self) -> None:
        request = json.loads(REQUEST.read_text(encoding="utf-8"))
        cases = []
        missing = copy.deepcopy(request)
        del missing["protected_references"][0]["expected_object"]
        cases.append(missing)
        invalid_identity = copy.deepcopy(request)
        invalid_identity["protected_references"][0]["expected_object"] = "main"
        cases.append(invalid_identity)
        unauthorized = copy.deepcopy(request)
        unauthorized["protected_references"][0]["selection"] = "allowed"
        cases.append(unauthorized)
        for value in cases:
            with self.assertRaises(InputContractError):
                load_compilation_request(self._write(value))

    def test_booleans_are_rejected_where_integers_are_required(self) -> None:
        budget = json.loads(BUDGET.read_text(encoding="utf-8"))
        budget["limit_bytes"] = True
        with self.assertRaises(InputContractError):
            load_budget_policy(self._write(budget))

    def test_selection_policy_schema_enums_and_selector_shapes_are_enforced(self) -> None:
        selection = json.loads(SELECTION.read_text(encoding="utf-8"))
        invalid_sensitivity = copy.deepcopy(selection)
        invalid_sensitivity["maximum_sensitivity"] = "secret"
        invalid_source_kind = copy.deepcopy(selection)
        invalid_source_kind["rules"][0]["source"]["kind"] = "provider_memory"
        invalid_direction = copy.deepcopy(selection)
        invalid_direction["relationship_traversal"]["allowlisted"][0]["direction"] = "sideways"
        invalid_selector_type = copy.deepcopy(selection)
        invalid_selector_type["rules"][0]["selector"]["type"] = "semantic"
        invalid_selector_shape = copy.deepcopy(selection)
        invalid_selector_shape["rules"][1]["selector"]["fields"] = ["id"]
        invalid_budget_tier = copy.deepcopy(selection)
        invalid_budget_tier["rules"][0]["budget_tier"] = "mandatory_control_envelope"
        missing_budget_tier = copy.deepcopy(selection)
        del missing_budget_tier["rules"][0]["budget_tier"]
        invalid_source_sensitivity = copy.deepcopy(selection)
        invalid_source_sensitivity["rules"][0]["source"]["sensitivity"] = "secret"
        missing_source_sensitivity = copy.deepcopy(selection)
        del missing_source_sensitivity["rules"][0]["source"]["sensitivity"]
        for value in (
            invalid_sensitivity,
            invalid_source_kind,
            invalid_direction,
            invalid_selector_type,
            invalid_selector_shape,
            invalid_budget_tier,
            missing_budget_tier,
            invalid_source_sensitivity,
            missing_source_sensitivity,
        ):
            with self.subTest(value=value), self.assertRaises(InputContractError):
                load_selection_policy(self._write(value))

    def test_source_sensitivity_ceiling_is_enforced(self) -> None:
        selection = json.loads(SELECTION.read_text(encoding="utf-8"))
        above_maximum = copy.deepcopy(selection)
        above_maximum["maximum_sensitivity"] = SENSITIVITY_ORDER[0]
        above_maximum["rules"][0]["source"]["sensitivity"] = SENSITIVITY_ORDER[1]
        above_maximum["digest"] = selection_policy_digest(above_maximum).as_dict()
        with self.assertRaises(InputContractError):
            load_selection_policy(self._write(above_maximum))

        permitted = copy.deepcopy(selection)
        permitted["maximum_sensitivity"] = SENSITIVITY_ORDER[0]
        permitted["digest"] = selection_policy_digest(permitted).as_dict()
        self.assertEqual(
            load_selection_policy(self._write(permitted))["maximum_sensitivity"],
            SENSITIVITY_ORDER[0],
        )

    def test_selection_and_budget_runtime_versions_are_independent(self) -> None:
        selection = json.loads(SELECTION.read_text(encoding="utf-8"))
        selection["version"] = BUDGET_POLICY_VERSION
        selection["digest"] = selection_policy_digest(selection).as_dict()
        with self.assertRaises(InputContractError):
            load_selection_policy(self._write(selection))

        budget = json.loads(BUDGET.read_text(encoding="utf-8"))
        budget["version"] = SELECTION_POLICY_VERSION
        budget["digest"] = budget_policy_digest(budget).as_dict()
        with self.assertRaises(InputContractError):
            load_budget_policy(self._write(budget))

    def test_budget_limit_is_safe_and_non_negative(self) -> None:
        budget = json.loads(BUDGET.read_text(encoding="utf-8"))
        negative = copy.deepcopy(budget)
        negative["limit_bytes"] = -1
        with self.assertRaises(InputContractError):
            load_budget_policy(self._write(negative))

        unsafe = copy.deepcopy(budget)
        unsafe["limit_bytes"] = 9007199254740992
        with self.assertRaises(UnsupportedJSONNumberError):
            load_budget_policy(self._write(unsafe))


if __name__ == "__main__":
    unittest.main()
