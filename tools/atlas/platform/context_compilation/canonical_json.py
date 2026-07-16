"""Restricted RFC 8785 canonical JSON for the task-context data model."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


MIN_SAFE_INTEGER = -9007199254740991
MAX_SAFE_INTEGER = 9007199254740991


class CanonicalJSONError(ValueError):
    """Base error for values outside the canonical task-context model."""


class UnsupportedTypeError(CanonicalJSONError):
    """Raised when a value has no normative task-context representation."""


class UnsafeIntegerError(CanonicalJSONError):
    """Raised when an integer is outside the interoperable safe range."""


class InvalidUnicodeError(CanonicalJSONError):
    """Raised when a string contains a non-scalar Unicode value."""


class InvalidMappingKeyError(CanonicalJSONError):
    """Raised when a mapping key is not a string."""


def _validate_string(value: str) -> None:
    for character in value:
        codepoint = ord(character)
        if 0xD800 <= codepoint <= 0xDFFF:
            raise InvalidUnicodeError("strings must contain only Unicode scalar values")


def _utf16_sort_key(value: str) -> bytes:
    _validate_string(value)
    return value.encode("utf-16-be")


def _serialize(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        if not MIN_SAFE_INTEGER <= value <= MAX_SAFE_INTEGER:
            raise UnsafeIntegerError(
                f"integer {value} is outside [{MIN_SAFE_INTEGER}, {MAX_SAFE_INTEGER}]"
            )
        return str(value)
    if isinstance(value, str):
        _validate_string(value)
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_serialize(item) for item in value) + "]"
    if isinstance(value, Mapping):
        keys = list(value.keys())
        if any(not isinstance(key, str) for key in keys):
            raise InvalidMappingKeyError("canonical JSON mapping keys must be strings")
        ordered_keys = sorted(keys, key=_utf16_sort_key)
        return "{" + ",".join(
            f"{_serialize(key)}:{_serialize(value[key])}" for key in ordered_keys
        ) + "}"
    raise UnsupportedTypeError(
        f"unsupported canonical JSON type: {type(value).__name__}"
    )


def canonicalize(value: Any) -> bytes:
    """Return restricted RFC 8785 canonical JSON as UTF-8 bytes."""

    return _serialize(value).encode("utf-8")


def canonicalize_text(value: Any) -> str:
    """Return the canonical representation as text for review and fixtures."""

    return canonicalize(value).decode("utf-8")
