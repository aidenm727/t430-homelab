import copy
from datetime import date, timedelta
import json
from pathlib import Path
import tempfile
import unittest

from atlas.platform.active_state import (
    AUTHORITY_SENTINEL,
    MAX_ACTIVE_STATE_BYTES,
    ActiveStateError,
    load_active_state,
    parse_active_state_bytes,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_STATE_PATH = REPOSITORY_ROOT / "docs" / "current-state.json"


class ActiveStateContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.valid = self.synthetic_valid_state()

    @staticmethod
    def synthetic_valid_state(
        *,
        decision_summary: str = "Owner decision on the synthetic checkpoint.",
        phase_effective_date: str = "2026-01-10",
        checkpoint_effective_date: str = "2026-01-12",
        freshness_effective_date: str = "2026-01-15",
        review_after: str | None = None,
    ) -> dict:
        return {
            "schema_version": 1,
            "phase": {
                "id": "synthetic-phase",
                "name": "Synthetic Phase",
                "lifecycle": "published",
                "effective_date": phase_effective_date,
                "evidence_refs": ["synthetic-phase-definition"],
            },
            "work_selection": {
                "status": "selected",
                "selected_checkpoint": {
                    "id": "synthetic-checkpoint",
                    "name": "Synthetic Checkpoint",
                    "lifecycle": "selected",
                    "effective_date": checkpoint_effective_date,
                    "evidence_refs": [],
                },
            },
            "blockers": [],
            "unknowns": [],
            "decision_required": {
                "id": "synthetic-owner-decision",
                "summary": decision_summary,
                "status": "pending",
                "evidence_refs": [],
            },
            "evidence_links": [
                {
                    "id": "synthetic-phase-definition",
                    "path": "docs/architecture/school-learning.md",
                    "relation": "defines_phase",
                    "commit": "9782eebec049b9b932cc583def499a44f1cbba2c",
                }
            ],
            "freshness": {
                "effective_date": freshness_effective_date,
                "review_after": review_after,
            },
            "authority": {
                "task": AUTHORITY_SENTINEL,
                "implementation": AUTHORITY_SENTINEL,
                "publication": AUTHORITY_SENTINEL,
            },
        }

    def parse(
        self,
        value=None,
        *,
        repository_root: Path = REPOSITORY_ROOT,
        verify_evidence: bool = False,
    ):
        if value is None:
            value = self.valid
        data = json.dumps(value, ensure_ascii=False).encode("utf-8")
        return parse_active_state_bytes(
            data,
            repository_root=repository_root,
            verify_evidence=verify_evidence,
        )

    def assert_invalid(self, value, message: str) -> None:
        with self.assertRaisesRegex(ActiveStateError, message):
            self.parse(value)

    def test_canonical_state_loads_with_verified_local_git_evidence(self) -> None:
        state = load_active_state()

        self.assertEqual(state.schema_version, 1)
        self.assertTrue(state.phase.evidence_refs)
        self.assertTrue(state.evidence_links)
        self.assertGreaterEqual(
            state.freshness.effective_date,
            state.phase.effective_date,
        )
        checkpoint = state.work_selection.selected_checkpoint
        if checkpoint is not None:
            self.assertGreaterEqual(
                state.freshness.effective_date,
                checkpoint.effective_date,
            )
        self.assertEqual(state.authority.task, AUTHORITY_SENTINEL)
        self.assertEqual(state.authority.implementation, AUTHORITY_SENTINEL)
        self.assertEqual(state.authority.publication, AUTHORITY_SENTINEL)

    def test_synthetic_decision_summary_is_preserved_without_live_claims(self) -> None:
        summary = "Owner decision on the synthetic checkpoint is pending."
        value = self.synthetic_valid_state(decision_summary=summary)
        state = self.parse(value)
        decision = state.decision_required

        self.assertIsNotNone(decision)
        assert decision is not None
        self.assertEqual(decision.summary, summary)
        for unsupported_claim in (
            "locally implemented",
            "verified",
            "current worktree",
            "test results",
        ):
            self.assertNotIn(unsupported_claim, decision.summary.lower())

    def test_missing_state_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.json"
            with self.assertRaisesRegex(
                ActiveStateError, "canonical active state could not be read"
            ):
                load_active_state(
                    missing,
                    repository_root=REPOSITORY_ROOT,
                    verify_evidence=False,
                )

    def test_symlinked_canonical_state_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.json"
            target.write_text("{}", encoding="utf-8")
            linked = root / "current-state.json"
            linked.symlink_to(target)

            with self.assertRaisesRegex(
                ActiveStateError, "non-symlink regular file"
            ):
                load_active_state(
                    linked,
                    repository_root=REPOSITORY_ROOT,
                    verify_evidence=False,
                )

    def test_invalid_utf8_is_rejected(self) -> None:
        with self.assertRaisesRegex(ActiveStateError, "not valid UTF-8"):
            parse_active_state_bytes(
                b"\xff",
                repository_root=REPOSITORY_ROOT,
                verify_evidence=False,
            )

    def test_oversized_state_is_rejected_before_decoding(self) -> None:
        with self.assertRaisesRegex(ActiveStateError, "16,384-byte maximum"):
            parse_active_state_bytes(
                b" " * (MAX_ACTIVE_STATE_BYTES + 1),
                repository_root=REPOSITORY_ROOT,
                verify_evidence=False,
            )

    def test_top_level_array_is_rejected(self) -> None:
        with self.assertRaisesRegex(ActiveStateError, "must be a JSON object"):
            parse_active_state_bytes(
                b"[]",
                repository_root=REPOSITORY_ROOT,
                verify_evidence=False,
            )

    def test_duplicate_keys_are_rejected_at_nested_levels(self) -> None:
        raw = (
            '{"schema_version":1,"schema_version":1,"phase":{},'
            '"work_selection":{},"blockers":[],"unknowns":[],'
            '"decision_required":null,"evidence_links":[],'
            '"freshness":{},"authority":{}}'
        ).encode("utf-8")
        with self.assertRaisesRegex(ActiveStateError, "duplicate JSON object key"):
            parse_active_state_bytes(
                raw,
                repository_root=REPOSITORY_ROOT,
                verify_evidence=False,
            )

    def test_nan_is_rejected(self) -> None:
        raw = json.dumps(self.valid, ensure_ascii=False).replace(
            '"schema_version": 1', '"schema_version": NaN'
        )
        with self.assertRaisesRegex(ActiveStateError, "unsupported JSON constant"):
            parse_active_state_bytes(
                raw.encode("utf-8"),
                repository_root=REPOSITORY_ROOT,
                verify_evidence=False,
            )

    def test_floating_point_values_are_rejected(self) -> None:
        raw = json.dumps(self.valid, ensure_ascii=False).replace(
            '"schema_version": 1', '"schema_version": 1.0'
        )
        with self.assertRaisesRegex(
            ActiveStateError, "unsupported JSON numeric value"
        ):
            parse_active_state_bytes(
                raw.encode("utf-8"),
                repository_root=REPOSITORY_ROOT,
                verify_evidence=False,
            )

    def test_unsupported_integer_in_string_field_is_rejected(self) -> None:
        value = copy.deepcopy(self.valid)
        value["phase"]["name"] = 2
        self.assert_invalid(value, "phase.name must be a string")

    def test_excessive_integer_magnitude_is_rejected(self) -> None:
        raw = json.dumps(self.valid, ensure_ascii=False).replace(
            '"schema_version": 1',
            '"schema_version": 999999999999999999999999999999999999999999',
        )
        with self.assertRaisesRegex(
            ActiveStateError, "unsupported JSON integer magnitude"
        ):
            parse_active_state_bytes(
                raw.encode("utf-8"),
                repository_root=REPOSITORY_ROOT,
                verify_evidence=False,
            )

    def test_missing_top_level_key_is_rejected(self) -> None:
        value = copy.deepcopy(self.valid)
        del value["authority"]
        self.assert_invalid(value, "missing required key.*authority")

    def test_unknown_top_level_key_is_rejected(self) -> None:
        value = copy.deepcopy(self.valid)
        value["live_head"] = "not-allowed"
        self.assert_invalid(value, "unknown key.*live_head")

    def test_unknown_nested_key_is_rejected(self) -> None:
        value = copy.deepcopy(self.valid)
        value["phase"]["branch"] = "main"
        self.assert_invalid(value, "phase has unknown key.*branch")

    def test_unknown_evidence_key_is_rejected(self) -> None:
        value = copy.deepcopy(self.valid)
        value["evidence_links"][0]["test_total"] = 1
        self.assert_invalid(
            value, r"evidence_links\[0\] has unknown key.*test_total"
        )

    def test_unsupported_schema_version_is_rejected(self) -> None:
        value = copy.deepcopy(self.valid)
        value["schema_version"] = 2
        self.assert_invalid(value, "unsupported active-state schema version")

    def test_boolean_schema_version_is_not_an_integer(self) -> None:
        value = copy.deepcopy(self.valid)
        value["schema_version"] = True
        self.assert_invalid(value, "schema_version must be an integer")

    def test_surrounding_whitespace_is_rejected(self) -> None:
        value = copy.deepcopy(self.valid)
        value["phase"]["name"] = " School Learning "
        self.assert_invalid(value, "without surrounding whitespace")

    def test_non_ascii_whitespace_is_rejected(self) -> None:
        value = copy.deepcopy(self.valid)
        value["decision_required"]["summary"] = "Owner\u00a0review"
        self.assert_invalid(value, "no other whitespace")

    def test_identifier_syntax_is_bounded_and_lowercase(self) -> None:
        value = copy.deepcopy(self.valid)
        value["phase"]["id"] = "School_Learning"
        self.assert_invalid(value, "lowercase kebab-case")

    def test_phase_lifecycle_is_strict(self) -> None:
        value = copy.deepcopy(self.valid)
        value["phase"]["lifecycle"] = "complete"
        self.assert_invalid(value, "phase.lifecycle has unsupported value")

    def test_checkpoint_lifecycle_is_strict(self) -> None:
        value = copy.deepcopy(self.valid)
        value["work_selection"]["selected_checkpoint"]["lifecycle"] = "published"
        self.assert_invalid(
            value, "work_selection.selected_checkpoint.lifecycle has unsupported"
        )

    def test_selected_work_requires_a_checkpoint(self) -> None:
        value = copy.deepcopy(self.valid)
        value["work_selection"]["selected_checkpoint"] = None
        self.assert_invalid(value, "must be an object")

    def test_intentional_idle_requires_a_null_checkpoint(self) -> None:
        value = copy.deepcopy(self.valid)
        value["work_selection"]["status"] = "intentional_idle"
        self.assert_invalid(value, "must be null")

    def test_intentional_idle_with_null_checkpoint_is_valid(self) -> None:
        value = copy.deepcopy(self.valid)
        value["work_selection"] = {
            "status": "intentional_idle",
            "selected_checkpoint": None,
        }
        state = self.parse(value)
        self.assertTrue(state.work_selection.intentional_idle)
        self.assertIsNone(state.work_selection.selected_checkpoint)

    def test_duplicate_entity_ids_are_rejected_globally(self) -> None:
        value = copy.deepcopy(self.valid)
        value["work_selection"]["selected_checkpoint"]["id"] = value["phase"]["id"]
        self.assert_invalid(value, "entity IDs must be globally unique")

    def test_unresolved_evidence_reference_is_rejected(self) -> None:
        value = copy.deepcopy(self.valid)
        value["phase"]["evidence_refs"] = ["not-present"]
        self.assert_invalid(value, "phase evidence reference does not resolve")

    def test_incompatible_evidence_relation_is_rejected(self) -> None:
        value = copy.deepcopy(self.valid)
        value["phase"]["evidence_refs"] = ["synthetic-phase-definition"]
        value["evidence_links"][0]["relation"] = "supports_decision"
        self.assert_invalid(value, "phase evidence reference.*incompatible relation")

    def test_blockers_require_canonical_evidence(self) -> None:
        value = copy.deepcopy(self.valid)
        value["blockers"] = [
            {
                "id": "unverified-blocker",
                "summary": "This blocker has no evidence.",
                "evidence_refs": [],
            }
        ]
        self.assert_invalid(value, "must contain canonical evidence")

    def test_strict_calendar_dates_are_required(self) -> None:
        value = copy.deepcopy(self.valid)
        value["freshness"]["effective_date"] = "2026-02-30"
        self.assert_invalid(value, "not a valid calendar date")

    def test_dates_require_canonical_syntax(self) -> None:
        value = copy.deepcopy(self.valid)
        value["phase"]["effective_date"] = "20260727"
        self.assert_invalid(value, "must use YYYY-MM-DD syntax")

    def test_phase_cannot_postdate_state_effective_date(self) -> None:
        value = copy.deepcopy(self.valid)
        effective_date = date.fromisoformat(value["freshness"]["effective_date"])
        value["phase"]["effective_date"] = (
            effective_date + timedelta(days=1)
        ).isoformat()
        self.assert_invalid(value, "phase effective date must not follow")

    def test_checkpoint_cannot_postdate_state_effective_date(self) -> None:
        value = copy.deepcopy(self.valid)
        effective_date = date.fromisoformat(value["freshness"]["effective_date"])
        value["work_selection"]["selected_checkpoint"][
            "effective_date"
        ] = (effective_date + timedelta(days=1)).isoformat()
        self.assert_invalid(value, "selected checkpoint effective date")

    def test_review_after_cannot_precede_effective_date(self) -> None:
        value = copy.deepcopy(self.valid)
        effective_date = date.fromisoformat(value["freshness"]["effective_date"])
        value["freshness"]["review_after"] = (
            effective_date - timedelta(days=1)
        ).isoformat()
        self.assert_invalid(value, "review_after must not precede")

    def test_authority_values_are_fixed_non_authority_sentinels(self) -> None:
        value = copy.deepcopy(self.valid)
        value["authority"]["implementation"] = "authorized"
        self.assert_invalid(value, "fixed non-authority sentinel")

    def test_evidence_paths_must_be_repository_relative(self) -> None:
        value = copy.deepcopy(self.valid)
        value["evidence_links"][0]["path"] = "/tmp/evidence.md"
        with self.assertRaisesRegex(ActiveStateError, "confined repository-relative"):
            self.parse(value, verify_evidence=True)

    def test_evidence_paths_must_not_traverse_parent(self) -> None:
        value = copy.deepcopy(self.valid)
        value["evidence_links"][0]["path"] = "docs/../README.md"
        with self.assertRaisesRegex(ActiveStateError, "confined repository-relative"):
            self.parse(value, verify_evidence=True)

    def test_evidence_paths_must_be_regular_files(self) -> None:
        value = copy.deepcopy(self.valid)
        value["evidence_links"][0]["path"] = "docs"
        with self.assertRaisesRegex(ActiveStateError, "regular file"):
            self.parse(value, verify_evidence=True)

    def test_evidence_paths_must_not_be_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "evidence.md").write_text("evidence", encoding="utf-8")
            (root / "linked.md").symlink_to("evidence.md")

            value = copy.deepcopy(self.valid)
            value["phase"]["evidence_refs"] = ["temporary-evidence"]
            value["evidence_links"] = [
                {
                    "id": "temporary-evidence",
                    "path": "linked.md",
                    "relation": "records_phase",
                    "commit": "0" * 40,
                }
            ]
            with self.assertRaisesRegex(ActiveStateError, "must not traverse a symlink"):
                self.parse(
                    value,
                    repository_root=root,
                    verify_evidence=True,
                )

    def test_local_evidence_commit_must_exist(self) -> None:
        value = copy.deepcopy(self.valid)
        value["evidence_links"][0]["commit"] = "0" * 40
        with self.assertRaisesRegex(
            ActiveStateError, "local Git evidence identity could not be verified"
        ):
            self.parse(value, verify_evidence=True)

    def test_evidence_path_must_exist_at_declared_commit(self) -> None:
        value = copy.deepcopy(self.valid)
        value["evidence_links"][0]["path"] = "docs/current-state.json"
        with self.assertRaisesRegex(
            ActiveStateError, "local Git evidence identity could not be verified"
        ):
            self.parse(value, verify_evidence=True)


if __name__ == "__main__":
    unittest.main()
