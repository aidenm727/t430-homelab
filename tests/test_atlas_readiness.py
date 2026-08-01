from contextlib import redirect_stdout
from dataclasses import replace
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from atlas.commands import bootstrap, next as next_command, review, state as state_command
from atlas.platform.active_state import (
    AUTHORITY_SENTINEL,
    ActiveStateError,
    SelectedCheckpoint,
    WorkSelection,
)
from atlas.platform.discovery import document_catalog
from atlas.platform.engineering_state import load
from atlas.platform.interpretation.readiness import (
    build_readiness_projection,
    project_readiness,
)
from atlas.platform.reasoning.guidance import build_guidance
from atlas.platform.reasoning.milestone import build_milestone_completion
from atlas.platform.reasoning.models import (
    EngineeringIntelligenceReport,
    GuidanceReport,
)
from atlas.platform.reasoning.synchronization import (
    check_current_mission,
    check_generated_context,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = "Clean Foundation F1 — Canonical State, Authority, and Orientation"
SYNTHETIC_CHECKPOINT = "Synthetic Selected Checkpoint"
INTENTIONAL_IDLE_MILESTONE = (
    "Intentional idle — no engineering checkpoint is selected."
)


def intelligence(**overrides) -> EngineeringIntelligenceReport:
    values = {
        "validation_status": "Valid",
        "milestone_status": "Selected",
        "milestone_confidence": "High",
        "milestone_satisfied_criteria": [],
        "milestone_unsatisfied_criteria": [],
        "milestone_next_actions": [],
        "mission_advancement_recommendation": "Do not infer mission advancement.",
        "mission_advancement_confidence": "High",
        "mission_should_advance": False,
        "synchronization_status": "Synchronized",
        "repository_clean": True,
        "current_phase": "Synthetic Phase — Published",
        "phase_lifecycle": "published",
        "next_milestone": SYNTHETIC_CHECKPOINT,
        "work_selection_status": "selected",
        "selected_checkpoint": SYNTHETIC_CHECKPOINT,
        "intentional_idle": False,
        "unknowns": [],
        "task_authority": AUTHORITY_SENTINEL,
        "implementation_authority": AUTHORITY_SENTINEL,
        "publication_authority": AUTHORITY_SENTINEL,
        "decision_required": "Owner review is required.",
        "blockers": [],
        "evidence": [],
        "relevant_documents": [],
        "suggested_commands": [],
    }
    values.update(overrides)
    return EngineeringIntelligenceReport(**values)


def guidance() -> GuidanceReport:
    return GuidanceReport(
        current_phase="Synthetic Phase — Published",
        recommended_action=(
            "Obtain or follow explicit owner task and implementation authority "
            f"for {SYNTHETIC_CHECKPOINT}; Atlas does not establish that authority."
        ),
        reason=(
            "Canonical state selects the checkpoint, while authority remains "
            "external and is not established by Atlas."
        ),
    )


def synthetic_selected_state():
    loaded = load()
    checkpoint = SelectedCheckpoint(
        id="synthetic-selected-checkpoint",
        name=SYNTHETIC_CHECKPOINT,
        lifecycle="selected",
        effective_date=loaded.active_state.freshness.effective_date,
        evidence_refs=(),
    )
    active_state = replace(
        loaded.active_state,
        work_selection=WorkSelection(
            status="selected",
            selected_checkpoint=checkpoint,
        ),
        decision_required=None,
    )
    return replace(
        loaded,
        active_state=active_state,
        next_milestone=SYNTHETIC_CHECKPOINT,
        work_selection_status="selected",
        selected_checkpoint=SYNTHETIC_CHECKPOINT,
        intentional_idle=False,
        decision_required=None,
        task_authority=AUTHORITY_SENTINEL,
        implementation_authority=AUTHORITY_SENTINEL,
        publication_authority=AUTHORITY_SENTINEL,
    )


def synthetic_intentional_idle_state():
    selected = synthetic_selected_state()
    active_state = replace(
        selected.active_state,
        work_selection=WorkSelection(
            status="intentional_idle",
            selected_checkpoint=None,
        ),
        decision_required=None,
    )
    return replace(
        selected,
        active_state=active_state,
        next_milestone=INTENTIONAL_IDLE_MILESTONE,
        work_selection_status="intentional_idle",
        selected_checkpoint=None,
        intentional_idle=True,
        decision_required=None,
    )


class AtlasReadinessProjectionTests(unittest.TestCase):
    def test_selected_checkpoint_does_not_imply_authority(self) -> None:
        projection = project_readiness(intelligence(), guidance())

        self.assertEqual(projection.repository_health, "Healthy within declared scope")
        self.assertEqual(projection.work_selection_state, "selected")
        self.assertEqual(projection.selected_checkpoint, SYNTHETIC_CHECKPOINT)
        self.assertFalse(projection.intentional_idle)
        self.assertEqual(projection.task_authority, AUTHORITY_SENTINEL)
        self.assertEqual(projection.implementation_authority, AUTHORITY_SENTINEL)
        self.assertEqual(projection.publication_authority, AUTHORITY_SENTINEL)
        self.assertIn("explicit owner", projection.recommended_action)
        self.assertIn("does not establish", projection.recommended_action)

    def test_intentional_idle_is_high_confidence_and_not_implementation_ready(
        self,
    ) -> None:
        idle = intelligence(
            milestone_status="Not Applicable",
            next_milestone=(
                "Intentional idle — no engineering checkpoint is selected."
            ),
            work_selection_status="intentional_idle",
            selected_checkpoint=None,
            intentional_idle=True,
            decision_required=None,
        )
        projection = project_readiness(idle, guidance())

        self.assertTrue(projection.intentional_idle)
        self.assertIsNone(projection.selected_checkpoint)
        self.assertIn("Remain intentionally idle", projection.recommended_action)
        self.assertNotIn("milestone rule", projection.recommended_action)
        self.assertNotIn("implementation ready", projection.recommended_action)

    def test_dirty_worktree_is_an_observation_not_authority_or_health(self) -> None:
        projection = project_readiness(
            intelligence(repository_clean=False),
            guidance(),
        )

        self.assertEqual(projection.working_tree_observation, "Dirty")
        self.assertEqual(projection.repository_health, "Healthy within declared scope")
        self.assertEqual(projection.implementation_authority, AUTHORITY_SENTINEL)

    def test_blockers_change_health_without_granting_resolution_authority(
        self,
    ) -> None:
        projection = project_readiness(
            intelligence(blockers=["Canonical state is contradictory."]),
            guidance(),
        )

        self.assertEqual(
            projection.repository_health,
            "Needs attention within declared scope",
        )
        self.assertEqual(
            projection.blockers,
            ("Canonical state is contradictory.",),
        )
        self.assertIn("explicit owner authority", projection.recommended_action)

    def test_validation_and_synchronization_scopes_are_explicit(self) -> None:
        projection = project_readiness(intelligence(), guidance())

        self.assertIn(
            "canonical active-state structure, evidence, and authority invariants",
            projection.validation_scope,
        )
        self.assertIn(
            "canonical active state and Current Mission compatibility fields",
            projection.synchronization_scope,
        )

    def test_typed_idle_precedes_historical_milestone_phrase_matching(self) -> None:
        idle_state = synthetic_intentional_idle_state()

        report = build_milestone_completion(document_catalog(), idle_state)

        self.assertEqual(report.status, "Not Applicable")
        self.assertEqual(report.confidence, "High")
        self.assertEqual(report.unsatisfied_criteria, [])
        self.assertEqual(report.next_actions, [])
        self.assertNotIn("milestone rule", " ".join(report.evidence))

    def test_canonical_projection_uses_typed_state(self) -> None:
        loaded = load()
        projection = build_readiness_projection(document_catalog(), loaded)
        selected_checkpoint = loaded.active_state.work_selection.selected_checkpoint

        self.assertEqual(projection.phase, loaded.active_state.phase.display_name)
        self.assertEqual(
            projection.selected_checkpoint,
            selected_checkpoint.name if selected_checkpoint is not None else None,
        )
        self.assertEqual(
            projection.work_selection_state,
            loaded.active_state.work_selection.status,
        )
        self.assertEqual(
            projection.intentional_idle,
            loaded.active_state.work_selection.intentional_idle,
        )
        self.assertEqual(projection.task_authority, AUTHORITY_SENTINEL)

    def test_guidance_never_treats_selected_state_as_permission(self) -> None:
        state = synthetic_selected_state()
        report = build_guidance(document_catalog(), state)

        self.assertIn("explicit bounded owner", report.recommended_action)
        self.assertIn("does not establish", report.recommended_action)
        self.assertNotIn("Proceed", report.recommended_action)

    def test_guidance_prioritizes_pending_owner_decision(self) -> None:
        loaded = load()
        report = build_guidance(document_catalog(), loaded)

        self.assertIsNotNone(loaded.decision_required)
        self.assertIn("pending explicit owner decision", report.recommended_action)
        self.assertIn(loaded.decision_required, report.recommended_action)
        self.assertIn(
            "does not establish or grant authority",
            report.recommended_action,
        )
        self.assertNotIn(
            "task and implementation authority",
            report.recommended_action,
        )

    def test_guidance_falls_back_to_bounded_implementation_authority(self) -> None:
        state = synthetic_selected_state()
        report = build_guidance(document_catalog(), state)

        self.assertIn(
            "explicit bounded owner task and implementation authority",
            report.recommended_action,
        )
        self.assertIn("does not establish", report.recommended_action)
        self.assertEqual(state.task_authority, AUTHORITY_SENTINEL)
        self.assertEqual(state.implementation_authority, AUTHORITY_SENTINEL)
        self.assertEqual(state.publication_authority, AUTHORITY_SENTINEL)

    def test_guidance_handles_intentional_idle_separately(self) -> None:
        state = synthetic_intentional_idle_state()
        report = build_guidance(document_catalog(), state)

        self.assertIn("Remain intentionally idle", report.recommended_action)
        self.assertIn("does not select or authorize work", report.reason)
        self.assertNotIn(
            "bounded owner task and implementation authority",
            report.recommended_action,
        )
        self.assertEqual(state.task_authority, AUTHORITY_SENTINEL)
        self.assertEqual(state.implementation_authority, AUTHORITY_SENTINEL)
        self.assertEqual(state.publication_authority, AUTHORITY_SENTINEL)

    def test_mission_phase_disagreement_is_a_synchronization_error(self) -> None:
        with patch(
            "atlas.platform.reasoning.synchronization.mission_phase",
            return_value="Contradictory prose phase",
        ):
            findings = check_current_mission()

        disagreement = [
            finding
            for finding in findings
            if finding.domain == "Active State ↔ Current Mission"
            and "phase disagrees" in finding.summary
        ]
        self.assertEqual(len(disagreement), 1)
        self.assertEqual(disagreement[0].severity, "Error")
        self.assertIn("machine-readable state wins", disagreement[0].recommended_action)

    def test_mission_selection_disagreement_is_a_synchronization_error(
        self,
    ) -> None:
        with patch(
            "atlas.platform.reasoning.synchronization.next_milestone",
            return_value="Different checkpoint",
        ):
            findings = check_current_mission()

        disagreement = [
            finding
            for finding in findings
            if finding.domain == "Active State ↔ Current Mission"
            and "next milestone disagrees" in finding.summary
        ]
        self.assertEqual(len(disagreement), 1)
        self.assertEqual(disagreement[0].severity, "Error")

    def test_generated_context_contains_state_and_non_authority_projection(
        self,
    ) -> None:
        context = (REPOSITORY_ROOT / "docs" / "aiden-context.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("## Canonical Active State", context)
        self.assertIn(CHECKPOINT, context)
        self.assertIn(
            f"- Implementation: {AUTHORITY_SENTINEL}",
            context,
        )
        self.assertIn("Repository state and Atlas do not establish authority.", context)

    def assert_generated_context_unsynchronized(self, context: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary_context = Path(directory) / "aiden-context.md"
            temporary_context.write_text(context, encoding="utf-8")
            with patch(
                "atlas.platform.reasoning.synchronization.read_repository_file",
                return_value=temporary_context.read_text(encoding="utf-8"),
            ):
                findings = check_generated_context()

        projection_errors = [
            finding
            for finding in findings
            if finding.domain == "Generated Context"
            and finding.severity == "Error"
            and "active-state projection" in finding.summary
        ]
        self.assertEqual(len(projection_errors), 1)

    def test_generated_context_exact_projection_is_synchronized(self) -> None:
        findings = check_generated_context()
        projection_findings = [
            finding
            for finding in findings
            if finding.domain == "Generated Context"
            and "active-state projection" in finding.summary
        ]

        self.assertEqual(len(projection_findings), 1)
        self.assertEqual(projection_findings[0].severity, "OK")

    def test_generated_context_rejects_each_hostile_projected_field_drift(
        self,
    ) -> None:
        context = (REPOSITORY_ROOT / "docs" / "aiden-context.md").read_text(
            encoding="utf-8"
        )
        evidence_prefix = "### Evidence\n\n- `"
        evidence_start = context.index(evidence_prefix) + len(evidence_prefix)
        evidence_end = context.index("`:", evidence_start)
        evidence_id = context[evidence_start:evidence_end]
        self.assertTrue(evidence_id)
        projection_end = context.index("\n## Current Mission Companion")
        projection = context[:projection_end]
        remainder = context[projection_end:]
        projected_line_prefixes = (
            "- Schema version:",
            "- Effective date:",
            "- Phase:",
            "- Phase lifecycle:",
            "- Work selection:",
            "- Selected checkpoint:",
            "- Intentional idle:",
            "- Decision required:",
            "- Task:",
            "- Implementation:",
            "- Publication:",
        )

        for prefix in projected_line_prefixes:
            with self.subTest(projected_field=prefix):
                lines = projection.splitlines()
                matching = [
                    index
                    for index, line in enumerate(lines)
                    if line.startswith(prefix)
                ]
                self.assertEqual(len(matching), 1)
                lines[matching[0]] += " hostile-drift"
                self.assert_generated_context_unsynchronized(
                    "\n".join(lines) + remainder
                )

        section_drifts = {
            "blockers": (
                "### Blockers\n\n- None",
                "### Blockers\n\n- Hostile blocker drift",
            ),
            "unknowns": (
                "### Unknowns\n\n- None",
                "### Unknowns\n\n- Hostile unknown drift",
            ),
            "evidence": (
                f"### Evidence\n\n- `{evidence_id}`:",
                f"### Evidence\n\n- `{evidence_id}-hostile-drift`:",
            ),
        }
        for field, (original, hostile) in section_drifts.items():
            with self.subTest(projected_field=field):
                self.assertIn(original, context)
                self.assert_generated_context_unsynchronized(
                    context.replace(original, hostile, 1)
                )

    def test_generated_context_rejects_missing_duplicated_and_misplaced_values(
        self,
    ) -> None:
        context = (REPOSITORY_ROOT / "docs" / "aiden-context.md").read_text(
            encoding="utf-8"
        )
        lifecycle = "- Phase lifecycle: published"
        self.assertEqual(context.count(lifecycle), 1)

        hostile_contexts = {
            "missing": context.replace(f"{lifecycle}\n", "", 1),
            "duplicated": context.replace(
                lifecycle,
                f"{lifecycle}\n{lifecycle}",
                1,
            ),
            "misplaced": context.replace(
                f"{lifecycle}\n",
                "",
                1,
            ).replace(
                "## Current Mission Companion",
                f"## Current Mission Companion\n\n{lifecycle}",
                1,
            ),
        }
        for drift, hostile_context in hostile_contexts.items():
            with self.subTest(drift=drift):
                self.assert_generated_context_unsynchronized(hostile_context)


class AtlasReadinessCommandTests(unittest.TestCase):
    def render(self, command) -> str:
        output = StringIO()
        with redirect_stdout(output):
            command.run(None)
        return output.getvalue()

    def test_bootstrap_state_review_and_next_share_authority_conclusion(
        self,
    ) -> None:
        outputs = [
            self.render(bootstrap),
            self.render(state_command),
            self.render(review),
            self.render(next_command),
        ]

        for output in outputs:
            self.assertIn(CHECKPOINT, output)
            self.assertIn(
                f"Task: {AUTHORITY_SENTINEL}",
                output,
            )
            self.assertIn(
                f"Implementation: {AUTHORITY_SENTINEL}",
                output,
            )
            self.assertIn(
                f"Publication: {AUTHORITY_SENTINEL}",
                output,
            )
            self.assertIn("Atlas Authority Conclusion: Not established", output)
            self.assertIn("explicit owner", output)
            self.assertNotIn("Proceed using", output)
            self.assertNotIn("Engineering Mode has been established", output)
            self.assertNotIn("Ready for engineering work", output)

    def test_state_command_fails_closed_without_prose_fallback(self) -> None:
        output = StringIO()
        with patch.object(
            state_command,
            "load",
            side_effect=ActiveStateError("canonical state missing"),
        ):
            with redirect_stdout(output):
                with self.assertRaises(SystemExit) as raised:
                    state_command.run(None)

        self.assertEqual(raised.exception.code, 1)
        self.assertIn("Invalid — Atlas failed closed.", output.getvalue())
        self.assertNotIn("Current Mission", output.getvalue())


if __name__ == "__main__":
    unittest.main()
