"""SHA-256 digest surfaces for task-context foundations and snapshots."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any

from atlas.platform.context_compilation.canonical_json import canonicalize
from atlas.platform.context_compilation.models import DigestRecord


ALGORITHM = "sha256"
CANONICALIZATION = "rfc8785-jcs"


def sha256_bytes(value: bytes) -> str:
    """Return lowercase SHA-256 hexadecimal for exact bytes."""

    return hashlib.sha256(value).hexdigest()


def digest_bytes(value: bytes, *, canonicalization: str = "none") -> DigestRecord:
    return DigestRecord(ALGORITHM, canonicalization, sha256_bytes(value))


def digest_canonical_json(value: Any) -> DigestRecord:
    return DigestRecord(ALGORITHM, CANONICALIZATION, sha256_bytes(canonicalize(value)))


def _without_own_digest(policy: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in policy.items() if key != "digest"}


def selection_policy_digest(policy: Mapping[str, Any]) -> DigestRecord:
    return digest_canonical_json(_without_own_digest(policy))


def budget_policy_digest(policy: Mapping[str, Any]) -> DigestRecord:
    return digest_canonical_json(_without_own_digest(policy))


def snapshot_fingerprint_surface(
    repository_identity: str,
    object_format: str,
    commit: str,
    tree: str,
    snapshot_mode: str,
) -> dict[str, str]:
    return {
        "repository_identity": repository_identity,
        "object_format": object_format,
        "commit": commit,
        "tree": tree,
        "snapshot_mode": snapshot_mode,
    }


def snapshot_fingerprint(
    repository_identity: str,
    object_format: str,
    commit: str,
    tree: str,
    snapshot_mode: str,
) -> DigestRecord:
    return digest_canonical_json(
        snapshot_fingerprint_surface(
            repository_identity,
            object_format,
            commit,
            tree,
            snapshot_mode,
        )
    )


def request_digest(request: Mapping[str, Any]) -> DigestRecord:
    repository = request["repository_request"]
    surface = {
        "repository_request": {
            "identity": repository["identity"],
            "requested_revision": repository["requested_revision"],
        },
        "task": request["task"],
        "declared_constraints": request["declared_constraints"],
        "selection_policy": request["selection_policy"],
        "budget_policy": request["budget_policy"],
        "protected_references": request["protected_references"],
        "as_of": request["as_of"],
    }
    return digest_canonical_json(surface)


def package_identity_surface(
    request_digest_value: str, snapshot_fingerprint_value: str
) -> dict[str, str]:
    return {
        "request_digest": request_digest_value,
        "snapshot_fingerprint": snapshot_fingerprint_value,
    }


def package_identity(
    request_digest_value: str, snapshot_fingerprint_value: str
) -> tuple[DigestRecord, str]:
    digest = digest_canonical_json(
        package_identity_surface(request_digest_value, snapshot_fingerprint_value)
    )
    return digest, f"tcp-{digest.value[:24]}"
