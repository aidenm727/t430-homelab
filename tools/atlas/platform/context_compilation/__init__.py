"""Public Checkpoint A foundations for task-context compilation."""

from atlas.platform.context_compilation.canonical_json import (
    MAX_SAFE_INTEGER,
    MIN_SAFE_INTEGER,
    CanonicalJSONError,
    InvalidMappingKeyError,
    InvalidUnicodeError,
    UnsafeIntegerError,
    UnsupportedTypeError,
    canonicalize,
    canonicalize_text,
)
from atlas.platform.context_compilation.digests import (
    budget_policy_digest,
    package_identity,
    request_digest,
    selection_policy_digest,
    sha256_bytes,
)

__all__ = [
    "MAX_SAFE_INTEGER",
    "MIN_SAFE_INTEGER",
    "CanonicalJSONError",
    "InvalidMappingKeyError",
    "InvalidUnicodeError",
    "UnsafeIntegerError",
    "UnsupportedTypeError",
    "canonicalize",
    "canonicalize_text",
    "budget_policy_digest",
    "package_identity",
    "request_digest",
    "selection_policy_digest",
    "sha256_bytes",
]
