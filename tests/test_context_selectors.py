import ast
import builtins
import dataclasses
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from atlas.platform.context_compilation import (
    SelectorContractError,
    SelectorEncodingError,
    SelectorError,
    SelectorNotFoundError,
    SelectorOutput,
    SelectorSyntaxError,
    parse_bounded_yaml_mapping,
    read_snapshot_blob,
    resolve_snapshot,
    select_markdown_heading,
    select_yaml_fields,
)
from atlas.platform.context_compilation.models import ModelValueError, deep_freeze


ROOT = Path(__file__).resolve().parents[1]
BASELINE = "de97f3d87cc7a90e404c3cf4ea313e6f12e5410a"
REPOSITORY_IDENTITY = "github.com/aidenm727/t430-homelab"
HISTORICAL_COMMIT = "79eef80af3d5969ece7eb9fe7f802be35575f450"
HISTORICAL_TREE = "3d2853517e64209cffde91766a62e9f70ceb2e47"
PROTECTED_REF = "refs/heads/wip/distinctness-foundation-calibration"
PROTECTED_OBJECT = "fcbc5957b89fe65a4313a3c23eb814e02a014698"
ORIGIN = "https://github.com/aidenm727/t430-homelab.git"


def fixture_git(
    repository: Path | None,
    *arguments: str,
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
    if result.returncode != 0:
        raise AssertionError(
            f"fixture Git command failed: {arguments[0]} ({result.returncode})"
        )
    return result


class SelectorModelTests(unittest.TestCase):
    def test_selector_error_hierarchy_is_narrow(self) -> None:
        for error in (
            SelectorEncodingError,
            SelectorSyntaxError,
            SelectorContractError,
            SelectorNotFoundError,
        ):
            self.assertTrue(issubclass(error, SelectorError))

    def test_selector_output_is_frozen_and_keeps_content_outside_metadata(self) -> None:
        output = SelectorOutput(
            "heading",
            "text/markdown",
            "utf-8",
            b"## Exact\n",
            "lf",
            {"nested": ["unchanged"]},
        )
        self.assertEqual(output.content, b"## Exact\n")
        self.assertEqual(
            output.as_dict(),
            {
                "selector_type": "heading",
                "media_type": "text/markdown",
                "encoding": "utf-8",
                "source_line_endings": "lf",
                "transformation": {"nested": ("unchanged",)},
            },
        )
        self.assertNotIn("content", output.as_dict())
        with self.assertRaises(dataclasses.FrozenInstanceError):
            output.content = b"changed"  # type: ignore[misc]

    def test_selector_output_rejects_non_bytes_content(self) -> None:
        for content in (bytearray(b"x"), memoryview(b"x"), "x", object()):
            with self.subTest(content=type(content).__name__), self.assertRaises(
                ModelValueError
            ):
                SelectorOutput(
                    "heading",
                    "text/markdown",
                    "utf-8",
                    content,  # type: ignore[arg-type]
                    "none",
                    {},
                )

    def test_selector_output_validates_strings_line_endings_and_mapping(self) -> None:
        fields = ("selector_type", "media_type", "encoding", "source_line_endings")
        arguments = ["heading", "text/markdown", "utf-8", b"x", "none", {}]
        positions = {"selector_type": 0, "media_type": 1, "encoding": 2, "source_line_endings": 4}
        for field in fields:
            invalid = list(arguments)
            invalid[positions[field]] = "bad\ud800"
            with self.subTest(field=field), self.assertRaises(ModelValueError):
                SelectorOutput(*invalid)  # type: ignore[arg-type]
        with self.assertRaises(ModelValueError):
            SelectorOutput("heading", "text/markdown", "utf-8", b"x", "mixed", {})
        with self.assertRaises(ModelValueError):
            SelectorOutput("heading", "text/markdown", "utf-8", b"x", "none", [])  # type: ignore[arg-type]

    def test_transformation_is_a_deeply_immutable_copy(self) -> None:
        source = {"fields": ["id"], "nested": {"value": "original"}}
        output = SelectorOutput(
            "yaml_fields", "application/json", "utf-8", b"{}", "none", source
        )
        source["fields"][0] = "changed"
        source["nested"]["value"] = "changed"  # type: ignore[index]
        self.assertIsInstance(output.transformation, MappingProxyType)
        self.assertEqual(output.transformation["fields"], ("id",))
        self.assertEqual(output.transformation["nested"]["value"], "original")
        with self.assertRaises(TypeError):
            output.transformation["new"] = "value"  # type: ignore[index]


class SharedSelectorBoundaryTests(unittest.TestCase):
    def _calls(self, data: object) -> tuple[object, ...]:
        return (
            lambda: parse_bounded_yaml_mapping(data),  # type: ignore[arg-type]
            lambda: select_yaml_fields(data, ("id",)),  # type: ignore[arg-type]
            lambda: select_markdown_heading(data, "## Heading", 1),  # type: ignore[arg-type]
        )

    def test_all_public_functions_require_bytes(self) -> None:
        for data in ("id: value", bytearray(b"id: value"), memoryview(b"id: value"), None):
            for call in self._calls(data):
                with self.subTest(data=type(data).__name__), self.assertRaises(
                    SelectorContractError
                ):
                    call()

    def test_bom_invalid_utf8_and_nul_are_rejected(self) -> None:
        cases = (
            (b"\xef\xbb\xbfid: value", SelectorEncodingError),
            (b"id: \xff", SelectorEncodingError),
            (b"id: before\0after", SelectorEncodingError),
        )
        for data, error in cases:
            for call in self._calls(data):
                with self.subTest(data=data, call=call), self.assertRaises(error):
                    call()

    def test_mixed_line_endings_and_bare_cr_are_rejected(self) -> None:
        for data in (b"id: value\r\ntitle: text\n", b"id: value\rtitle: text"):
            for call in self._calls(data):
                with self.subTest(data=data, call=call), self.assertRaises(
                    SelectorEncodingError
                ):
                    call()

    def test_errors_do_not_carry_arbitrary_source_content(self) -> None:
        secret = "arbitrary-source-content"
        with self.assertRaises(SelectorEncodingError) as encoding:
            parse_bounded_yaml_mapping(secret.encode() + b"\xff")
        self.assertNotIn(secret, str(encoding.exception))
        self.assertIsNone(encoding.exception.__cause__)
        with self.assertRaises(SelectorSyntaxError) as syntax:
            parse_bounded_yaml_mapping(f'value: "{secret}\\q"'.encode())
        self.assertNotIn(secret, str(syntax.exception))
        self.assertIsNone(syntax.exception.__cause__)

    def test_lf_crlf_and_no_line_endings_are_classified(self) -> None:
        cases = (
            (b"id: value\n", "lf"),
            (b"id: value\r\n", "crlf"),
            (b"id: value", "none"),
        )
        for data, expected in cases:
            with self.subTest(expected=expected):
                output = select_yaml_fields(data, ("id",))
                self.assertEqual(output.source_line_endings, expected)

    def test_unicode_is_not_normalized(self) -> None:
        composed = parse_bounded_yaml_mapping("name: é".encode("utf-8"))
        decomposed = parse_bounded_yaml_mapping("name: e\u0301".encode("utf-8"))
        self.assertEqual(composed["name"], "é")
        self.assertEqual(decomposed["name"], "e\u0301")
        self.assertNotEqual(composed["name"], decomposed["name"])

    def test_repeated_outputs_are_byte_identical(self) -> None:
        yaml_data = b"title: repeat\nid: EO-1\n"
        markdown_data = b"## Repeat\nbody\n## End\n"
        yaml_output = select_yaml_fields(yaml_data, ("id", "title"))
        markdown_output = select_markdown_heading(markdown_data, "## Repeat", 1)
        for _ in range(20):
            self.assertEqual(
                select_yaml_fields(yaml_data, ("id", "title")), yaml_output
            )
            self.assertEqual(
                select_markdown_heading(markdown_data, "## Repeat", 1),
                markdown_output,
            )


class BoundedYamlTests(unittest.TestCase):
    def test_map_order_does_not_affect_canonical_json(self) -> None:
        first = select_yaml_fields(b"title: T\nid: I\n", ("title", "id"))
        second = select_yaml_fields(b"id: I\ntitle: T\n", ("id", "title"))
        self.assertEqual(first.content, b'{"id":"I","title":"T"}')
        self.assertEqual(first.content, second.content)

    def test_top_level_sequence_is_a_deeply_immutable_tuple(self) -> None:
        parsed = parse_bounded_yaml_mapping(b"related:\n  - first\n  - second\n")
        self.assertIsInstance(parsed, MappingProxyType)
        self.assertEqual(parsed["related"], ("first", "second"))
        with self.assertRaises(TypeError):
            parsed["related"] = ("changed",)  # type: ignore[index]
        with self.assertRaises(AttributeError):
            parsed["related"].append("changed")

    def test_duplicate_keys_and_tabs_are_rejected(self) -> None:
        for data in (b"id: one\nid: two\n", b"id:\tvalue\n", b"id: value\n\t"):
            with self.subTest(data=data), self.assertRaises(SelectorSyntaxError):
                parse_bounded_yaml_mapping(data)

    def test_empty_document_and_invalid_top_level_keys_are_rejected(self) -> None:
        for data in (b"", b"\n\n", b"bad key: value\n", b"9key: value\n"):
            with self.subTest(data=data), self.assertRaises(SelectorSyntaxError):
                parse_bounded_yaml_mapping(data)

    def test_directives_document_markers_and_multiple_documents_are_rejected(self) -> None:
        cases = (
            b"%YAML 1.2\nid: value\n",
            b"---\nid: value\n",
            b"id: value\n...\n",
            b"id: value\n---\ntitle: second\n",
        )
        for data in cases:
            with self.subTest(data=data), self.assertRaises(SelectorSyntaxError):
                parse_bounded_yaml_mapping(data)

    def test_anchors_aliases_merges_and_tags_are_rejected(self) -> None:
        cases = (
            b"id: &anchor value\n",
            b"id: *anchor\n",
            b"<<: *anchor\n",
            b"id: !str value\n",
            b"id: !!str value\n",
        )
        for data in cases:
            with self.subTest(data=data), self.assertRaises(SelectorSyntaxError):
                parse_bounded_yaml_mapping(data)

    def test_flow_collections_and_complex_keys_are_rejected(self) -> None:
        cases = (
            b"id: [one, two]\n",
            b"id: {name: value}\n",
            b"? complex\n: value\n",
        )
        for data in cases:
            with self.subTest(data=data), self.assertRaises(SelectorSyntaxError):
                parse_bounded_yaml_mapping(data)

    def test_nested_mappings_sequences_and_mixed_values_are_rejected(self) -> None:
        cases = (
            b"outer:\n  child: value\n",
            b"outer:\n  - child\n    - nested\n",
            b"outer:\n  - child: value\n",
        )
        for data in cases:
            with self.subTest(data=data), self.assertRaises(SelectorSyntaxError):
                parse_bounded_yaml_mapping(data)

    def test_alternate_indentation_is_rejected(self) -> None:
        cases = (
            b"items:\n - one\n",
            b"items:\n   - one\n",
            b"value: |\n one\n",
        )
        for data in cases:
            with self.subTest(data=data), self.assertRaises(SelectorSyntaxError):
                parse_bounded_yaml_mapping(data)

    def test_blank_line_between_sequence_items_is_rejected(self) -> None:
        with self.assertRaises(SelectorSyntaxError):
            parse_bounded_yaml_mapping(b"items:\n  - one\n\n  - two\n")

    def test_malformed_single_and_double_quotes_are_rejected(self) -> None:
        cases = (
            b"value: 'unterminated\n",
            b"value: 'mal'formed'\n",
            b'value: "bad\\q"\n',
            b'value: "unterminated\n',
            b'value: "\\ud800"\n',
        )
        for data in cases:
            with self.subTest(data=data), self.assertRaises(SelectorSyntaxError):
                parse_bounded_yaml_mapping(data)

    def test_supported_quoted_strings_are_exact(self) -> None:
        parsed = parse_bounded_yaml_mapping(
            b"empty: ''\napostrophe: 'owner''s'\njson: \"line\\nvalue\"\n"
        )
        self.assertEqual(
            parsed,
            {"empty": "", "apostrophe": "owner's", "json": "line\nvalue"},
        )

    def test_unsupported_block_indicators_are_rejected(self) -> None:
        for indicator in (b">-", b">+", b">2", b"|-", b"|+", b"|2"):
            with self.subTest(indicator=indicator), self.assertRaises(
                SelectorSyntaxError
            ):
                parse_bounded_yaml_mapping(b"value: " + indicator + b"\n  text\n")

    def test_trailing_structural_whitespace_is_rejected(self) -> None:
        cases = (
            b"value: plain \n",
            b"items:\n  - value \n",
            b"value: > \n  text\n",
        )
        for data in cases:
            with self.subTest(data=data), self.assertRaises(SelectorSyntaxError):
                parse_bounded_yaml_mapping(data)

    def test_comment_syntax_is_rejected_but_quoted_hash_is_data(self) -> None:
        with self.assertRaises(SelectorSyntaxError):
            parse_bounded_yaml_mapping(b"value: plain # comment\n")
        self.assertEqual(
            parse_bounded_yaml_mapping(b"value: '# data'\n")["value"], "# data"
        )

    def test_plain_scalar_lookalikes_remain_strings(self) -> None:
        parsed = parse_bounded_yaml_mapping(
            b"boolean: true\nnullish: null\ninteger: 42\nfloatish: 1.25\n"
            b"date: 2026-07-16\ntimestamp: 2026-07-16T123456Z\n"
        )
        self.assertEqual(
            parsed,
            {
                "boolean": "true",
                "nullish": "null",
                "integer": "42",
                "floatish": "1.25",
                "date": "2026-07-16",
                "timestamp": "2026-07-16T123456Z",
            },
        )
        self.assertTrue(all(isinstance(value, str) for value in parsed.values()))

    def test_folded_block_behavior_is_exact(self) -> None:
        parsed = parse_bounded_yaml_mapping(
            b"value: >\n  first\n  second\n\n  third\n\n"
        )
        self.assertEqual(parsed["value"], "first second\n\nthird\n")

    def test_literal_block_behavior_is_exact(self) -> None:
        parsed = parse_bounded_yaml_mapping(
            b"value: |\n  first\n  second\n\n  third\n\n"
        )
        self.assertEqual(parsed["value"], "first\nsecond\n\nthird\n")

    def test_block_removes_exactly_two_structural_spaces(self) -> None:
        parsed = parse_bounded_yaml_mapping(b"value: |\n    indented data\n")
        self.assertEqual(parsed["value"], "  indented data\n")

    def test_empty_and_all_blank_blocks_are_rejected(self) -> None:
        for data in (b"value: >", b"value: |\n\n  \n"):
            with self.subTest(data=data), self.assertRaises(SelectorSyntaxError):
                parse_bounded_yaml_mapping(data)

    def test_missing_duplicate_empty_and_invalid_field_contracts(self) -> None:
        data = b"id: EO-1\ntitle: Title\n"
        with self.assertRaises(SelectorNotFoundError):
            select_yaml_fields(data, ("missing",))
        with self.assertRaises(SelectorContractError):
            select_yaml_fields(data, ("id", "id"))
        with self.assertRaises(SelectorContractError):
            select_yaml_fields(data, ())
        invalid = ("id", b"id", bytearray(b"id"), memoryview(b"id"), {"id"}, 1)
        for fields in invalid:
            with self.subTest(fields=type(fields).__name__), self.assertRaises(
                SelectorContractError
            ):
                select_yaml_fields(data, fields)  # type: ignore[arg-type]
        for fields in (("",), ("\ud800",), (1,)):
            with self.subTest(fields=fields), self.assertRaises(SelectorContractError):
                select_yaml_fields(data, fields)  # type: ignore[arg-type]

    def test_canonical_json_has_no_bom_or_insignificant_whitespace(self) -> None:
        output = select_yaml_fields(
            b"title: A title\nid: EO-1\n", ("title", "id")
        )
        self.assertEqual(output.content, b'{"id":"EO-1","title":"A title"}')
        self.assertFalse(output.content.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b": ", output.content)
        self.assertNotIn(b", ", output.content)
        self.assertEqual(output.transformation, {"fields": ("title", "id")})


class MarkdownHeadingTests(unittest.TestCase):
    def test_occurrence_selection_is_exact(self) -> None:
        data = b"## Pick\nfirst\n## Pick\nsecond\n## End\n"
        self.assertEqual(
            select_markdown_heading(data, "## Pick", 1).content,
            b"## Pick\nfirst\n",
        )
        self.assertEqual(
            select_markdown_heading(data, "## Pick", 2).content,
            b"## Pick\nsecond\n",
        )

    def test_equal_and_higher_level_headings_are_boundaries(self) -> None:
        equal = b"## Pick\nbody\n## Equal\nnext\n"
        higher = b"### Pick\nbody\n# Higher\nnext\n"
        self.assertEqual(
            select_markdown_heading(equal, "## Pick", 1).content,
            b"## Pick\nbody\n",
        )
        self.assertEqual(
            select_markdown_heading(higher, "### Pick", 1).content,
            b"### Pick\nbody\n",
        )

    def test_deeper_headings_are_included_through_end_of_file(self) -> None:
        data = b"## Pick\nbody\n### Deeper\ninside"
        self.assertEqual(select_markdown_heading(data, "## Pick", 1).content, data)

    def test_terminal_newline_and_lf_bytes_are_preserved(self) -> None:
        terminated = b"## Pick\nbody\n"
        unterminated = b"## Pick\nbody"
        self.assertEqual(
            select_markdown_heading(terminated, "## Pick", 1).content, terminated
        )
        self.assertEqual(
            select_markdown_heading(unterminated, "## Pick", 1).content,
            unterminated,
        )

    def test_crlf_bytes_are_preserved(self) -> None:
        data = b"## Pick\r\n\r\nbody  \r\n## End\r\n"
        output = select_markdown_heading(data, "## Pick", 1)
        self.assertEqual(output.content, b"## Pick\r\n\r\nbody  \r\n")
        self.assertEqual(output.source_line_endings, "crlf")

    def test_backtick_and_tilde_fence_headings_are_ignored(self) -> None:
        cases = (
            b"## Pick\n```python\n## Hidden\n```\nafter\n## End\n",
            b"## Pick\n  ~~~ arbitrary info\n# Hidden\n  ~~~\nafter\n## End\n",
        )
        for data in cases:
            with self.subTest(data=data):
                output = select_markdown_heading(data, "## Pick", 1)
                self.assertTrue(output.content.endswith(b"after\n"))
                self.assertNotIn(b"## End", output.content)

    def test_longer_closing_fence_is_accepted(self) -> None:
        data = b"## Pick\n```\n# Hidden\n````\n## End\n"
        output = select_markdown_heading(data, "## Pick", 1)
        self.assertEqual(output.content, b"## Pick\n```\n# Hidden\n````\n")

    def test_shorter_closing_fence_does_not_close(self) -> None:
        data = b"## Pick\n````\n# Hidden\n```\n## Still hidden\n"
        self.assertEqual(select_markdown_heading(data, "## Pick", 1).content, data)

    def test_unclosed_fence_keeps_remainder_fenced(self) -> None:
        data = b"## Pick\n~~~\n# Hidden\n## Also hidden\n"
        self.assertEqual(select_markdown_heading(data, "## Pick", 1).content, data)

    def test_short_fence_is_ordinary_text(self) -> None:
        data = b"## Pick\n``\nbody\n## End\n"
        self.assertEqual(
            select_markdown_heading(data, "## Pick", 1).content,
            b"## Pick\n``\nbody\n",
        )

    def test_setext_blockquote_list_and_indented_pseudo_headings_are_ignored(self) -> None:
        pseudo = (
            (b"Title\n=====\n", "# Title"),
            (b"> ## Quoted\n", "## Quoted"),
            (b"- ## Listed\n", "## Listed"),
            (b"    ## Indented\n", "## Indented"),
        )
        for data, heading in pseudo:
            with self.subTest(heading=heading), self.assertRaises(
                SelectorNotFoundError
            ):
                select_markdown_heading(data, heading, 1)

    def test_heading_selector_shape_is_exact(self) -> None:
        invalid: tuple[object, ...] = (
            "Heading",
            "##No space",
            "## ",
            "####### Too deep",
            " ## Indented",
            "## Multi\nline",
            "## CR\rline",
            "## NUL\0line",
            "## bad\ud800",
            1,
        )
        for heading in invalid:
            with self.subTest(heading=repr(heading)), self.assertRaises(
                SelectorContractError
            ):
                select_markdown_heading(b"## Valid\n", heading, 1)  # type: ignore[arg-type]

    def test_occurrence_must_be_a_positive_safe_non_boolean_integer(self) -> None:
        for occurrence in (True, False, 0, -1, 9007199254740992, 1.0, "1"):
            with self.subTest(occurrence=occurrence), self.assertRaises(
                SelectorContractError
            ):
                select_markdown_heading(
                    b"## Pick\n", "## Pick", occurrence  # type: ignore[arg-type]
                )

    def test_absent_occurrence_is_not_found(self) -> None:
        with self.assertRaises(SelectorNotFoundError):
            select_markdown_heading(b"## Pick\n", "## Pick", 2)

    def test_unicode_case_whitespace_and_closing_hashes_are_literal(self) -> None:
        data = (
            "## Café\ncomposed\n"
            "## Cafe\u0301\ndecomposed\n"
            "## Case\nupper\n"
            "## case\nlower\n"
            "## Space  \nspaces\n"
            "## Closed ##\nclosed\n"
        ).encode("utf-8")
        self.assertIn(
            "decomposed".encode(),
            select_markdown_heading(data, "## Cafe\u0301", 1).content,
        )
        self.assertIn(b"upper", select_markdown_heading(data, "## Case", 1).content)
        self.assertIn(
            b"spaces", select_markdown_heading(data, "## Space  ", 1).content
        )
        self.assertIn(
            b"closed", select_markdown_heading(data, "## Closed ##", 1).content
        )
        with self.assertRaises(SelectorNotFoundError):
            select_markdown_heading(data, "## CAFÉ", 1)
        with self.assertRaises(SelectorNotFoundError):
            select_markdown_heading(data, "## Space ", 1)
        with self.assertRaises(SelectorNotFoundError):
            select_markdown_heading(data, "## Closed", 1)


class HistoricalSelectorIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.repository = Path(cls.temporary.name) / "target"
        fixture_git(
            None,
            "clone",
            "--no-local",
            "--no-hardlinks",
            str(ROOT),
            str(cls.repository),
        )
        fixture_git(cls.repository, "remote", "set-url", "origin", ORIGIN)
        fixture_git(cls.repository, "update-ref", PROTECTED_REF, PROTECTED_OBJECT)
        snapshot = resolve_snapshot(
            cls.repository,
            repository_identity=REPOSITORY_IDENTITY,
            requested_revision=HISTORICAL_COMMIT,
            expected_tree=HISTORICAL_TREE,
            protected_references=(
                {
                    "name": PROTECTED_REF,
                    "expected_object": PROTECTED_OBJECT,
                    "authoritatively_targeted": False,
                    "selection": "forbidden",
                },
            ),
        )
        cls.paths = {
            "opportunity": "docs/opportunities/reviewed/EO-2026-013-task-scoped-agent-context-compilation.yaml",
            "mission": "docs/current-mission.md",
            "repository": "docs/architecture/repository.md",
            "knowledge": "docs/architecture/knowledge-authority.md",
            "collaboration": "docs/standards/engineering-collaboration.md",
        }
        cls.blobs = {
            name: read_snapshot_blob(cls.repository, snapshot, path).content
            for name, path in cls.paths.items()
        }

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_historical_opportunity_parse_and_relationships_are_exact(self) -> None:
        parsed = parse_bounded_yaml_mapping(self.blobs["opportunity"])
        self.assertEqual(parsed["id"], "EO-2026-013")
        self.assertEqual(parsed["title"], "Task-scoped agent context compilation")
        self.assertEqual(parsed["status"], "reviewed")
        self.assertEqual(
            parsed["summary"],
            "Develop a deterministic capability that compiles a reproducible, "
            "task-specific context package for a bounded engineering mission or "
            "task without making the AI model responsible for selecting its own "
            "authoritative context.\n",
        )
        self.assertEqual(
            parsed["related_documents"],
            (
                "docs/architecture/atlas.md",
                "docs/architecture/repository.md",
                "docs/architecture/reasoning.md",
                "docs/standards/engineering-collaboration.md",
            ),
        )

    def test_historical_four_field_canonical_json_is_exact(self) -> None:
        output = select_yaml_fields(
            self.blobs["opportunity"], ("id", "title", "status", "summary")
        )
        self.assertEqual(
            output.content,
            b'{"id":"EO-2026-013","status":"reviewed","summary":"Develop a deterministic capability that compiles a reproducible, task-specific context package for a bounded engineering mission or task without making the AI model responsible for selecting its own authoritative context.\\n","title":"Task-scoped agent context compilation"}',
        )

    def test_historical_initial_milestone_section_is_exact(self) -> None:
        expected = b"""## Initial Milestone

Define the Task-Scoped Agent Context Compilation architecture and one bounded example package.

The architecture is expected to be documented later, likely under `docs/architecture/`. This mission-selection application does not create that architecture document or begin capability implementation.

### Included

- Package schema.
- Deterministic source selection.
- Source-selection explanations.
- Provenance and authority.
- Freshness.
- Conflicts and unknowns.
- Context-size behavior.
- Omissions.
- Consumer contract.
- One bounded example package.

### Excluded

- Embeddings.
- Vector databases.
- Model-based retrieval.
- LLM invocation.
- Autonomous execution.
- Broad agent authority.
- Live ChatGPT Project cleanup.
- Live Project settings changes.
- Codex configuration changes.
- Provider-specific permanent architecture.
- Engineering Opportunity lifecycle mutation.

---

"""
        self.assertEqual(
            select_markdown_heading(
                self.blobs["mission"], "## Initial Milestone", 1
            ).content,
            expected,
        )

    def test_historical_source_of_truth_section_is_exact(self) -> None:
        expected = b"""## Source of Truth Hierarchy

GitHub is the canonical documentation source.

The repository is the canonical source of truth for Aiden Platform engineering knowledge.

Architecture documents define intent.

The hierarchy is:

1. Vision defines purpose and durable direction.
2. Architecture records describe intent and structural design.
3. Standards records describe expected engineering behavior.
4. Current Mission defines active engineering work.
5. Infrastructure records describe current implementation and state.
6. Operations records describe change evidence and history.
7. Roadmaps describe likely future direction and sequencing.
8. Repository Objects preserve structured candidates and lifecycle state.
9. Generated context summarizes canonical documentation and never replaces it.
10. Git history records repository evolution.
11. Live verification resolves current operational reality.

Conversation context may explain intent but does not replace canonical repository knowledge.

---

"""
        self.assertEqual(
            select_markdown_heading(
                self.blobs["repository"], "## Source of Truth Hierarchy", 1
            ).content,
            expected,
        )

    def test_historical_generated_context_section_is_exact(self) -> None:
        expected = b"""### Generated Context

Rebuildable material derived from canonical or source records.

Examples include:

- `docs/aiden-context.md`.
- `docs/infrastructure-snapshot.md`.
- Future task context packages.
- Generated summaries.

Generated context should identify its sources and managing process.

It may be useful and accurate while remaining non-canonical.

"""
        self.assertEqual(
            select_markdown_heading(
                self.blobs["knowledge"], "### Generated Context", 1
            ).content,
            expected,
        )

    def test_historical_responsibilities_section_is_exact(self) -> None:
        expected = b"""## Responsibilities

The human engineer owns goals, judgment, execution, verification, review, commits, and final decisions.

The repository preserves canonical engineering truth through architecture, infrastructure records, operations history, roadmaps, standards, generated context, and engineering tools.

Atlas provides deterministic engineering awareness from the repository and working tree.

ChatGPT assists with architecture, planning, explanation, documentation, and implementation artifacts.

"""
        self.assertEqual(
            select_markdown_heading(
                self.blobs["collaboration"], "## Responsibilities", 1
            ).content,
            expected,
        )


class SelectorCapabilityBoundaryTests(unittest.TestCase):
    def test_selector_module_imports_no_forbidden_capability(self) -> None:
        path = ROOT / "tools/atlas/platform/context_compilation/selectors.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        forbidden = {
            "pathlib",
            "os",
            "subprocess",
            "socket",
            "urllib",
            "http",
            "tempfile",
            "shutil",
            "hashlib",
            "snapshot",
            "time",
            "datetime",
            "random",
            "locale",
        }
        self.assertTrue(imported.isdisjoint(forbidden), imported & forbidden)

    def test_selectors_perform_no_filesystem_open(self) -> None:
        with mock.patch.object(builtins, "open", side_effect=AssertionError("open")):
            self.assertEqual(parse_bounded_yaml_mapping(b"id: value")["id"], "value")
            self.assertEqual(
                select_yaml_fields(b"id: value", ("id",)).content,
                b'{"id":"value"}',
            )
            self.assertEqual(
                select_markdown_heading(b"## Heading\nbody", "## Heading", 1).content,
                b"## Heading\nbody",
            )

    def test_selector_module_has_no_mutable_global_state(self) -> None:
        import ast
        from pathlib import Path

        repository = Path(__file__).resolve().parents[1]
        source_path = repository / (
            "tools/atlas/platform/context_compilation/selectors.py"
        )
        tree = ast.parse(source_path.read_text(encoding="utf-8"))

        mutable_assignments = []
        for node in tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = node.value
                if isinstance(value, (ast.List, ast.Dict, ast.Set)):
                    mutable_assignments.append(
                        (node.lineno, type(value).__name__)
                    )

        self.assertEqual(mutable_assignments, [])

    def test_b1a_snapshot_boundary_files_match_the_authorization_baseline(self) -> None:
        result = fixture_git(
            None,
            "diff",
            "--name-only",
            BASELINE,
            "--",
            "tools/atlas/platform/context_compilation/snapshot.py",
            "tests/test_context_snapshot.py",
        )
        self.assertEqual(result.stdout, b"")

    def test_b2_paths_remain_absent(self) -> None:
        forbidden = (
            "tools/atlas/platform/context_compilation/compiler.py",
            "tools/atlas/platform/context_compilation/explanation.py",
        )
        self.assertTrue(all(not (ROOT / path).exists() for path in forbidden))

    def test_existing_deep_freeze_behavior_remains_intact(self) -> None:
        frozen = deep_freeze({"nested": ["value"]})
        self.assertIsInstance(frozen, MappingProxyType)
        self.assertEqual(frozen["nested"], ("value",))
        with self.assertRaises(ModelValueError):
            deep_freeze(b"bytes remain outside canonical JSON")


if __name__ == "__main__":
    unittest.main()
