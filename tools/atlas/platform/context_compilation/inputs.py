"""Strict UTF-8 JSON loading for Checkpoint A request and policy inputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Mapping

from atlas.platform.context_compilation.canonical_json import (
    MAX_SAFE_INTEGER,
    MIN_SAFE_INTEGER,
)
from atlas.platform.context_compilation.validation import (
    ContractValidationError,
    require_valid,
    validate_budget_policy,
    validate_compilation_request,
    validate_policy_reference_identity,
    validate_selection_policy,
)


class InputError(ValueError):
    """Base class for stable task-context input failures."""


class InputEncodingError(InputError):
    """Raised when input is not strict UTF-8 text."""


class InputSyntaxError(InputError):
    """Raised when input is not accepted strict JSON."""


class DuplicateKeyError(InputSyntaxError):
    """Raised when any JSON object contains a duplicate key."""


class UnsupportedJSONNumberError(InputSyntaxError):
    """Raised for floats, non-finite numbers, or unsafe integers."""


class InputContractError(InputError):
    """Raised when a parsed value violates a bounded v1 contract."""


def _pairs_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _reject_float(value: str) -> Any:
    raise UnsupportedJSONNumberError(f"floating-point syntax is forbidden: {value}")


def _reject_constant(value: str) -> Any:
    raise UnsupportedJSONNumberError(f"non-finite JSON number is forbidden: {value}")


def _safe_integer(value: str) -> int:
    parsed = int(value)
    if not MIN_SAFE_INTEGER <= parsed <= MAX_SAFE_INTEGER:
        raise UnsupportedJSONNumberError(f"integer is outside the safe range: {value}")
    return parsed


def _validate_loaded_value(value: Any) -> None:
    if value is None or isinstance(value, bool) or isinstance(value, int):
        return
    if isinstance(value, str):
        if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
            raise InputSyntaxError("JSON strings must contain valid Unicode scalars")
        return
    if isinstance(value, list):
        for item in value:
            _validate_loaded_value(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _validate_loaded_value(key)
            _validate_loaded_value(item)
        return
    raise InputSyntaxError(f"unsupported JSON value type: {type(value).__name__}")


def load_json_bytes(data: bytes) -> Any:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise InputEncodingError("input must be valid UTF-8") from error
    if text.startswith("\ufeff"):
        raise InputEncodingError("UTF-8 BOM is not accepted")
    try:
        value = json.loads(
            text,
            object_pairs_hook=_pairs_without_duplicates,
            parse_float=_reject_float,
            parse_int=_safe_integer,
            parse_constant=_reject_constant,
        )
    except (DuplicateKeyError, UnsupportedJSONNumberError):
        raise
    except (json.JSONDecodeError, UnicodeError) as error:
        raise InputSyntaxError(f"invalid strict JSON: {error}") from error
    _validate_loaded_value(value)
    return value


def load_json_file(path: str | Path) -> Any:
    return load_json_bytes(Path(path).read_bytes())


def _validated(
    path: str | Path,
    validator: Callable[[Any], Any],
) -> Mapping[str, Any]:
    value = load_json_file(path)
    try:
        require_valid(validator(value))
    except ContractValidationError as error:
        raise InputContractError(str(error)) from error
    return value


def load_selection_policy(
    path: str | Path, expected_reference: Mapping[str, Any] | None = None
) -> Mapping[str, Any]:
    value = _validated(path, validate_selection_policy)
    if expected_reference is not None:
        try:
            require_valid(
                validate_policy_reference_identity(
                    expected_reference, value, kind="selection"
                )
            )
        except ContractValidationError as error:
            raise InputContractError(str(error)) from error
    return value


def load_budget_policy(
    path: str | Path, expected_reference: Mapping[str, Any] | None = None
) -> Mapping[str, Any]:
    value = _validated(path, validate_budget_policy)
    if expected_reference is not None:
        try:
            require_valid(
                validate_policy_reference_identity(expected_reference, value, kind="budget")
            )
        except ContractValidationError as error:
            raise InputContractError(str(error)) from error
    return value


def load_compilation_request(path: str | Path) -> Mapping[str, Any]:
    return _validated(path, validate_compilation_request)
