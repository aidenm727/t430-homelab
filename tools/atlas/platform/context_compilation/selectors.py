"""Pure deterministic selectors over caller-supplied immutable bytes."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, cast

from atlas.platform.context_compilation.canonical_json import (
    MAX_SAFE_INTEGER,
    canonicalize,
)
from atlas.platform.context_compilation.models import SelectorOutput, deep_freeze


class SelectorError(ValueError):
    """Base class for deterministic selector failures."""


class SelectorEncodingError(SelectorError):
    """The immutable byte input does not satisfy the strict text boundary."""


class SelectorSyntaxError(SelectorError):
    """The supplied source is malformed under the bounded source grammar."""


class SelectorContractError(SelectorError):
    """A selector argument or requested contract is unsupported."""


class SelectorNotFoundError(SelectorError):
    """A required field or requested heading occurrence is absent."""


@dataclass(frozen=True)
class _PhysicalLine:
    text: str
    start: int
    end: int


def _contains_surrogate(value: str) -> bool:
    return any(0xD800 <= ord(character) <= 0xDFFF for character in value)


def _decode_text(data: bytes) -> tuple[str, str]:
    if not isinstance(data, bytes):
        raise SelectorContractError("selector input must be bytes")
    if data.startswith(b"\xef\xbb\xbf"):
        raise SelectorEncodingError("selector input must not contain a UTF-8 BOM")
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise SelectorEncodingError("selector input must be valid UTF-8") from None
    if "\0" in text:
        raise SelectorEncodingError("selector input must not contain NUL")
    if _contains_surrogate(text):
        raise SelectorEncodingError(
            "selector input must contain only Unicode scalar values"
        )

    lf = False
    crlf = False
    index = 0
    while index < len(text):
        character = text[index]
        if character == "\r":
            if index + 1 >= len(text) or text[index + 1] != "\n":
                raise SelectorEncodingError("selector input contains a bare CR")
            crlf = True
            index += 2
            continue
        if character == "\n":
            lf = True
        index += 1
    if lf and crlf:
        raise SelectorEncodingError("selector input has mixed line endings")
    if crlf:
        return text, "crlf"
    if lf:
        return text, "lf"
    return text, "none"


def _logical_lines(text: str, line_endings: str) -> list[str]:
    if line_endings == "none":
        return [text]
    separator = "\r\n" if line_endings == "crlf" else "\n"
    lines = text.split(separator)
    if text.endswith(separator):
        lines.pop()
    return lines


def _physical_lines(data: bytes) -> list[_PhysicalLine]:
    lines: list[_PhysicalLine] = []
    start = 0
    while start < len(data):
        newline = data.find(b"\n", start)
        if newline < 0:
            end = len(data)
            content_end = end
        else:
            end = newline + 1
            content_end = newline - 1 if newline > start and data[newline - 1] == 13 else newline
        lines.append(
            _PhysicalLine(
                text=data[start:content_end].decode("utf-8"),
                start=start,
                end=end,
            )
        )
        start = end
    if not data:
        lines.append(_PhysicalLine(text="", start=0, end=0))
    return lines


def _parse_scalar(value: str) -> str:
    if not value:
        raise SelectorSyntaxError("bounded YAML scalar is invalid")
    if value[0] == "'":
        if len(value) < 2 or value[-1] != "'":
            raise SelectorSyntaxError("bounded YAML scalar is invalid")
        result: list[str] = []
        index = 1
        final = len(value) - 1
        while index < final:
            character = value[index]
            if character == "'":
                if index + 1 >= final or value[index + 1] != "'":
                    raise SelectorSyntaxError("bounded YAML scalar is invalid")
                result.append("'")
                index += 2
                continue
            result.append(character)
            index += 1
        return "".join(result)
    if value[0] == '"':
        try:
            decoded = json.loads(value)
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise SelectorSyntaxError("bounded YAML scalar is invalid") from None
        if not isinstance(decoded, str) or _contains_surrogate(decoded):
            raise SelectorSyntaxError("bounded YAML scalar is invalid")
        return decoded
    if value[0] in ("-", "?", "'", '"'):
        raise SelectorSyntaxError("bounded YAML scalar is invalid")
    if value[0].isspace() or value[-1].isspace():
        raise SelectorSyntaxError("bounded YAML scalar is invalid")
    if any(character in "#:[]{},&*!|>%@`" for character in value):
        raise SelectorSyntaxError("bounded YAML scalar is invalid")
    return value


def _parse_sequence(lines: list[str], start: int) -> tuple[tuple[str, ...], int]:
    if start >= len(lines) or not lines[start].startswith("  - "):
        raise SelectorSyntaxError("bounded YAML sequence is invalid")
    values: list[str] = []
    index = start
    while index < len(lines):
        line = lines[index]
        if line.startswith("  - "):
            if line.endswith(" "):
                raise SelectorSyntaxError("bounded YAML sequence is invalid")
            values.append(_parse_scalar(line[4:]))
            index += 1
            continue
        if line == "":
            next_nonblank = index + 1
            while next_nonblank < len(lines) and lines[next_nonblank] == "":
                next_nonblank += 1
            if next_nonblank < len(lines) and lines[next_nonblank].startswith("  - "):
                raise SelectorSyntaxError("bounded YAML sequence is invalid")
            break
        if line.startswith(" "):
            raise SelectorSyntaxError("bounded YAML sequence is invalid")
        break
    return tuple(values), index


def _block_value(content: list[str], style: str) -> str:
    while content and content[-1] == "":
        content.pop()
    if not content or not any(line != "" for line in content):
        raise SelectorSyntaxError("bounded YAML block is invalid")
    if style == "|":
        return "\n".join(content) + "\n"
    result = content[0]
    for previous, current in zip(content, content[1:]):
        result += " " if previous and current else "\n"
        result += current
    return result + "\n"


def _parse_block(
    lines: list[str], start: int, style: str
) -> tuple[str, int]:
    content: list[str] = []
    index = start
    while index < len(lines):
        line = lines[index]
        if line == "":
            content.append("")
            index += 1
            continue
        if not line.startswith(" "):
            break
        if line == "  ":
            content.append("")
        elif line.startswith("  "):
            content.append(line[2:])
        else:
            raise SelectorSyntaxError("bounded YAML block is invalid")
        index += 1
    return _block_value(content, style), index


def parse_bounded_yaml_mapping(data: bytes) -> Mapping[str, Any]:
    """Parse the documented bounded Engineering Opportunity YAML subset."""

    text, line_endings = _decode_text(data)
    if "\t" in text:
        raise SelectorSyntaxError("bounded YAML must not contain tabs")
    lines = _logical_lines(text, line_endings)
    result: dict[str, Any] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if line == "":
            index += 1
            continue
        if line in ("---", "...") or line.startswith("%"):
            raise SelectorSyntaxError("bounded YAML document syntax is invalid")
        if line.startswith(" "):
            raise SelectorSyntaxError("bounded YAML indentation is invalid")
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):(.*)", line)
        if match is None:
            raise SelectorSyntaxError("bounded YAML mapping syntax is invalid")
        key, remainder = match.groups()
        if key in result:
            raise SelectorSyntaxError("bounded YAML keys must be unique")
        if remainder == "":
            value, index = _parse_sequence(lines, index + 1)
            result[key] = value
            continue
        if not remainder.startswith(" ") or remainder.startswith("  "):
            raise SelectorSyntaxError("bounded YAML mapping syntax is invalid")
        scalar = remainder[1:]
        if scalar in (">", "|"):
            value, index = _parse_block(lines, index + 1, scalar)
            result[key] = value
            continue
        if line.endswith(" "):
            raise SelectorSyntaxError("bounded YAML structural whitespace is invalid")
        result[key] = _parse_scalar(scalar)
        index += 1
    if not result:
        raise SelectorSyntaxError("bounded YAML must contain a mapping")
    return cast(Mapping[str, Any], deep_freeze(result))


def _validated_fields(fields: Sequence[str]) -> tuple[str, ...]:
    if not isinstance(fields, Sequence) or isinstance(
        fields, (str, bytes, bytearray, memoryview)
    ):
        raise SelectorContractError("fields must be a non-string sequence")
    copied = tuple(fields)
    if not copied:
        raise SelectorContractError("fields must not be empty")
    seen: set[str] = set()
    for field in copied:
        if not isinstance(field, str) or not field or _contains_surrogate(field):
            raise SelectorContractError("field names must be nonempty Unicode strings")
        if field in seen:
            raise SelectorContractError("field names must be unique")
        seen.add(field)
    return copied


def select_yaml_fields(
    data: bytes,
    fields: Sequence[str],
) -> SelectorOutput:
    """Select exact top-level fields and emit canonical JSON UTF-8 bytes."""

    requested = _validated_fields(fields)
    parsed = parse_bounded_yaml_mapping(data)
    if any(field not in parsed for field in requested):
        raise SelectorNotFoundError("required YAML field was not found")
    _, line_endings = _decode_text(data)
    selected = {field: parsed[field] for field in requested}
    return SelectorOutput(
        selector_type="yaml_fields",
        media_type="application/json",
        encoding="utf-8",
        content=canonicalize(selected),
        source_line_endings=line_endings,
        transformation={"fields": requested},
    )


def _heading_level(line: str) -> int | None:
    level = 0
    while level < len(line) and line[level] == "#":
        level += 1
    if not 1 <= level <= 6:
        return None
    if level >= len(line) or line[level] != " ":
        return None
    if level + 1 >= len(line):
        return None
    return level


def _opening_fence(line: str) -> tuple[str, int] | None:
    indentation = 0
    while indentation < len(line) and line[indentation] == " ":
        indentation += 1
    if indentation > 3 or indentation >= len(line):
        return None
    marker = line[indentation]
    if marker not in ("`", "~"):
        return None
    end = indentation
    while end < len(line) and line[end] == marker:
        end += 1
    length = end - indentation
    if length < 3:
        return None
    if marker == "`" and "`" in line[end:]:
        return None
    return marker, length


def _is_closing_fence(line: str, marker: str, opening_length: int) -> bool:
    indentation = 0
    while indentation < len(line) and line[indentation] == " ":
        indentation += 1
    if indentation > 3:
        return False
    end = indentation
    while end < len(line) and line[end] == marker:
        end += 1
    if end - indentation < opening_length:
        return False
    return all(character == " " for character in line[end:])


def _validated_heading(heading_text: str, occurrence: int) -> int:
    if (
        not isinstance(heading_text, str)
        or _contains_surrogate(heading_text)
        or "\r" in heading_text
        or "\n" in heading_text
        or "\0" in heading_text
    ):
        raise SelectorContractError("heading_text is invalid")
    level = _heading_level(heading_text)
    if level is None:
        raise SelectorContractError("heading_text is invalid")
    if (
        not isinstance(occurrence, int)
        or isinstance(occurrence, bool)
        or not 1 <= occurrence <= MAX_SAFE_INTEGER
    ):
        raise SelectorContractError("occurrence must be a positive safe integer")
    return level


def select_markdown_heading(
    data: bytes,
    heading_text: str,
    occurrence: int,
) -> SelectorOutput:
    """Select one exact ATX-heading section while preserving its source bytes."""

    _decode_text(data)
    selected_level = _validated_heading(heading_text, occurrence)
    _, line_endings = _decode_text(data)
    selected_start: int | None = None
    matches = 0
    fence_marker: str | None = None
    fence_length = 0
    for line in _physical_lines(data):
        if fence_marker is not None:
            if _is_closing_fence(line.text, fence_marker, fence_length):
                fence_marker = None
                fence_length = 0
            continue
        opening = _opening_fence(line.text)
        if opening is not None:
            fence_marker, fence_length = opening
            continue
        level = _heading_level(line.text)
        if level is None:
            continue
        if selected_start is None:
            if line.text == heading_text:
                matches += 1
                if matches == occurrence:
                    selected_start = line.start
            continue
        if level <= selected_level:
            return SelectorOutput(
                selector_type="heading",
                media_type="text/markdown",
                encoding="utf-8",
                content=data[selected_start:line.start],
                source_line_endings=line_endings,
                transformation={
                    "heading_text": heading_text,
                    "occurrence": occurrence,
                },
            )
    if selected_start is None:
        raise SelectorNotFoundError("requested heading occurrence was not found")
    return SelectorOutput(
        selector_type="heading",
        media_type="text/markdown",
        encoding="utf-8",
        content=data[selected_start:],
        source_line_endings=line_endings,
        transformation={
            "heading_text": heading_text,
            "occurrence": occurrence,
        },
    )


__all__ = (
    "SelectorOutput",
    "SelectorError",
    "SelectorEncodingError",
    "SelectorSyntaxError",
    "SelectorContractError",
    "SelectorNotFoundError",
    "parse_bounded_yaml_mapping",
    "select_yaml_fields",
    "select_markdown_heading",
)
