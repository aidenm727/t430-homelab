import ast
from collections import Counter
import hashlib
import ipaddress
import json
from pathlib import Path
import re
import runpy
import subprocess
import unittest
from urllib.parse import urlsplit

from atlas.platform.discovery import (
    infrastructure_documents,
    portfolio_evidence_documents,
)
from atlas.platform.document_definitions import definition_for


ROOT = Path(__file__).resolve().parents[1]
SELF = "tests/test_public_surface.py"
LEGACY_SLUG = "t430-homelab"
CURRENT_SLUG = "aiden-platform"

EXPECTED_REMOVALS = (
    "docs/aiden-context-spec.md",
    "docs/archive/Homelab_Docker_Installation_Summary.pdf",
    "docs/archive/Homelab_Maintenance_Summary.pdf",
    "docs/archive/Homelab_Status_Summary.pdf",
    "docs/archive/T430_Homelab_Setup_Recap.pdf",
    "docs/images/grafana.png",
    "docs/images/homepage.png",
    "docs/images/kuma.png",
    "docs/images/physical.jpg",
    "docs/infrastructure-gamer-pve.md",
    "docs/changes/2026-06-24-add-gamer-pve-node-monitoring.yml",
    "docs/changes/2026-06-24-add-tailscale-remote-management-for-gamer-pve.yml",
    "docs/changes/2026-06-24-deploy-immich-on-gamer-pve.yml",
)

OLD_IDENTITY_ALLOWLIST = frozenset(
    {
        "docs/architecture/repository.md",
        "docs/architecture/task-scoped-agent-context-compilation.md",
        "docs/reviews/ai-workflow-evaluation-cycle-2026-07.md",
        "docs/reviews/aiden-ai-environment-baseline-v1-2026-07-20.md",
        "docs/reviews/engineering-workflow-v1-1-evidence-2026-08-01.md",
        "docs/reviews/eo-2026-013-b1a-authorization-review-2026-07-16.md",
        "docs/reviews/repository-identity-r1-evidence-2026-08-02.md",
        "tests/test_context_materialization.py",
        "tests/test_context_selection.py",
        "tests/test_context_selectors.py",
        "tests/test_context_snapshot.py",
        "tools/atlas/platform/context_compilation/snapshot.py",
    }
)

HISTORICAL_HOST_DISPOSITIONS = {
    "docs/reviews/ai-capability-landscape-work-research-2026-07-14.md": {
        153: 1,
        396: 1,
    },
    "docs/reviews/repository-identity-r1-evidence-2026-08-02.md": {
        115: 1,
        117: 1,
        119: 1,
        122: 1,
    },
}
HISTORICAL_INTERNAL_URL_DISPOSITIONS: dict[str, dict[int, int]] = {}
HISTORICAL_ABSOLUTE_PATH_DISPOSITIONS = {
    "docs/reviews/aiden-ai-environment-baseline-v1-2026-07-20.md": {
        14: 1,
        65: 1,
        66: 1,
        67: 1,
        68: 1,
        80: 1,
        82: 1,
        306: 1,
        310: 1,
        314: 1,
        318: 1,
        322: 1,
        326: 1,
    },
    "docs/reviews/engineering-workflow-v1-1-evidence-2026-08-01.md": {
        52: 1,
    },
}

INTERNAL_IPV4_NETWORKS = tuple(
    ipaddress.ip_network(network)
    for network in (
        "10.0.0.0/8",
        "100.64.0.0/10",
        "127.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
    )
)
PRIVATE_HOST_SUFFIXES = ("lan", "local", "internal", "home.arpa")
URL_PATTERN = re.compile(r"https?://[^\s<>{}\[\]\"'`]+", re.IGNORECASE)
HISTORICAL_HOST_PATTERN = re.compile(r"\b(?:t430-beast|gamer-pve)\b")
IP_LITERAL_PATTERN = re.compile(
    r"(?<![0-9A-Fa-f:.])[0-9A-Fa-f:.]{3,}(?![0-9A-Fa-f:.])"
)
HIGH_CONFIDENCE_SECRET_PATTERNS = (
    re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
)
ABSOLUTE_OPERATIONAL_PATH_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_.-])/(?:etc|opt|srv|mnt|home|var/lib)/"
    r"[^\s<>()\[\]{}\"'`]+"
)

PUBLIC_OPERATIONAL_OWNERS = (
    "README.md",
    "docs/infrastructure.md",
    "docs/infrastructure-virtualization.md",
    "docs/services.md",
    "docs/infrastructure-snapshot.md",
    "docs/aiden-context.md",
    "docs/architecture/compute.md",
    "docs/architecture/repository.md",
)

# Each intentional privacy-test literal is bound to its exact match class,
# test function (or module scope), line, literal digest, and expected count.
SELF_PRIVACY_DISPOSITIONS: dict[tuple[str, str, int, str], int]


def candidate_paths() -> tuple[str, ...]:
    result = subprocess.run(
        (
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ),
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    return tuple(
        sorted(
            path
            for path in result.stdout.decode("utf-8").split("\0")
            if path and (ROOT / path).is_file()
        )
    )


def candidate_text() -> dict[str, str]:
    result = {}
    for path in candidate_paths():
        data = (ROOT / path).read_bytes()
        if b"\0" in data:
            continue
        try:
            result[path] = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
    return result


def line_match_counts(text: str, pattern: re.Pattern[str]) -> dict[int, int]:
    counts: dict[int, int] = {}
    for match in pattern.finditer(text):
        line_number = text.count("\n", 0, match.start()) + 1
        counts[line_number] = counts.get(line_number, 0) + 1
    return counts


def pattern_literal_matches(
    text: str,
    pattern: re.Pattern[str],
) -> tuple[tuple[int, str], ...]:
    return tuple(
        (text.count("\n", 0, match.start()) + 1, match.group(0))
        for match in pattern.finditer(text)
    )


def ip_literal_matches(text: str) -> tuple[tuple[int, str], ...]:
    matches = []
    for match in IP_LITERAL_PATTERN.finditer(text):
        token = match.group(0).strip(".:")
        if not token or ("." not in token and ":" not in token):
            continue
        try:
            ipaddress.ip_address(token)
        except ValueError:
            continue
        matches.append((text.count("\n", 0, match.start()) + 1, token))
    return tuple(matches)


def high_confidence_secret_matches(text: str) -> tuple[tuple[int, str], ...]:
    matches = []
    for pattern in HIGH_CONFIDENCE_SECRET_PATTERNS:
        matches.extend(pattern_literal_matches(text, pattern))
    return tuple(sorted(matches))


def hostname_is_internal(hostname: str) -> bool:
    host = hostname.casefold().rstrip(".")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        if host == "localhost" or host.endswith(".localhost"):
            return True
        return any(
            host == suffix or host.endswith(f".{suffix}")
            for suffix in PRIVATE_HOST_SUFFIXES
        )

    return address.version == 4 and any(
        address in network for network in INTERNAL_IPV4_NETWORKS
    )


def internal_url_matches(text: str) -> tuple[tuple[int, str], ...]:
    matches = []
    for match in URL_PATTERN.finditer(text):
        candidate = match.group(0).rstrip(".,;:!?)]}")
        try:
            hostname = urlsplit(candidate).hostname
        except ValueError:
            continue
        if hostname is None or not hostname_is_internal(hostname):
            continue
        line_number = text.count("\n", 0, match.start()) + 1
        matches.append((line_number, candidate))
    return tuple(matches)


def internal_url_line_counts(text: str) -> dict[int, int]:
    counts: dict[int, int] = {}
    for line_number, _ in internal_url_matches(text):
        counts[line_number] = counts.get(line_number, 0) + 1
    return counts


def test_function_scopes(text: str) -> tuple[tuple[int, int, str], ...]:
    tree = ast.parse(text)
    return tuple(
        (node.lineno, node.end_lineno or node.lineno, node.name)
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    )


def self_match_counts(
    text: str,
    match_class: str,
    matches: tuple[tuple[int, str], ...],
) -> Counter[tuple[str, str, int, str]]:
    scopes = test_function_scopes(text)
    counts: Counter[tuple[str, str, int, str]] = Counter()
    for line_number, literal in matches:
        function = next(
            (
                name
                for start, end, name in scopes
                if start <= line_number <= end
            ),
            "<module>",
        )
        digest = hashlib.sha256(literal.encode("utf-8")).hexdigest()
        counts[(match_class, function, line_number, digest)] += 1
    return counts


def self_disposition_mismatch_lines(
    text: str,
    match_class: str,
    matches: tuple[tuple[int, str], ...],
    dispositions: dict[tuple[str, str, int, str], int] | None = None,
) -> tuple[int, ...]:
    expected = SELF_PRIVACY_DISPOSITIONS if dispositions is None else dispositions
    expected_class = Counter(
        {
            key: count
            for key, count in expected.items()
            if key[0] == match_class
        }
    )
    observed = self_match_counts(text, match_class, matches)
    return tuple(
        sorted(
            {
                key[2]
                for key in set(observed) | set(expected_class)
                if observed.get(key, 0) != expected_class.get(key, 0)
            }
        )
    )


def disposition_mismatches(
    observed: dict[str, dict[int, int]],
    expected: dict[str, dict[int, int]],
) -> dict[str, tuple[int, ...]]:
    mismatches = {}
    for path in sorted(set(observed) | set(expected)):
        observed_lines = observed.get(path, {})
        expected_lines = expected.get(path, {})
        changed_lines = tuple(
            line_number
            for line_number in sorted(set(observed_lines) | set(expected_lines))
            if observed_lines.get(line_number) != expected_lines.get(line_number)
        )
        if changed_lines:
            mismatches[path] = changed_lines
    return mismatches


class PublicSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.paths = candidate_paths()
        cls.text = candidate_text()

    def test_obsolete_and_binary_artifacts_are_absent(self) -> None:
        for path in EXPECTED_REMOVALS:
            with self.subTest(path=path):
                self.assertFalse((ROOT / path).exists())

        prohibited_suffixes = {
            ".pdf",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",
            ".zip",
            ".7z",
            ".tar",
            ".gz",
        }
        remaining = [
            path for path in self.paths if Path(path).suffix.lower() in prohibited_suffixes
        ]
        self.assertEqual(remaining, [])

    def test_candidate_contains_no_ip_address_literals(self) -> None:
        findings = {}
        for path, text in self.text.items():
            matches = ip_literal_matches(text)
            if path == SELF:
                lines = self_disposition_mismatch_lines(
                    text,
                    "ip_literal",
                    matches,
                )
            else:
                lines = tuple(sorted({line for line, _ in matches}))
            if lines:
                findings[path] = lines
        self.assertEqual(findings, {})

    def test_legacy_repository_identity_is_confined_to_truthful_allowlist(self) -> None:
        matches = set()
        findings = {}
        pattern = re.compile(re.escape(LEGACY_SLUG))
        for path, text in self.text.items():
            literal_matches = pattern_literal_matches(text, pattern)
            if path == SELF:
                lines = self_disposition_mismatch_lines(
                    text,
                    "legacy_identity",
                    literal_matches,
                )
                if lines:
                    findings[path] = lines
            elif literal_matches:
                matches.add(path)
        self.assertEqual(findings, {})
        self.assertEqual(matches, OLD_IDENTITY_ALLOWLIST)
        self.assertIn(
            "tools/atlas/platform/context_compilation/snapshot.py",
            matches,
        )

    def test_current_identity_has_the_canonical_clone_claim(self) -> None:
        readme = self.text["README.md"]
        self.assertIn(CURRENT_SLUG, readme)
        self.assertRegex(
            readme,
            r"git\s+clone\s+https://github\.com/aidenm727/aiden-platform\.git",
        )

    def test_old_host_names_are_historical_only(self) -> None:
        observed = {}
        self_findings = {}
        for path, text in self.text.items():
            matches = pattern_literal_matches(text, HISTORICAL_HOST_PATTERN)
            if path == SELF:
                lines = self_disposition_mismatch_lines(
                    text,
                    "historical_host",
                    matches,
                )
                if lines:
                    self_findings[path] = lines
            elif matches:
                observed[path] = line_match_counts(text, HISTORICAL_HOST_PATTERN)
        self.assertEqual(self_findings, {})
        self.assertEqual(
            disposition_mismatches(observed, HISTORICAL_HOST_DISPOSITIONS),
            {},
        )

    def test_internal_urls_are_historical_only(self) -> None:
        observed = {}
        self_findings = {}
        for path, text in self.text.items():
            matches = internal_url_matches(text)
            if path == SELF:
                lines = self_disposition_mismatch_lines(
                    text,
                    "internal_url",
                    matches,
                )
                if lines:
                    self_findings[path] = lines
            elif matches:
                observed[path] = internal_url_line_counts(text)
        self.assertEqual(self_findings, {})
        self.assertEqual(
            disposition_mismatches(
                observed,
                HISTORICAL_INTERNAL_URL_DISPOSITIONS,
            ),
            {},
        )

    def test_internal_url_classifier_uses_exact_boundaries(self) -> None:
        public_urls = "\n".join(
            (
                "https://public-internal.example:443/path",
                "https://service.local.example/path",
                "https://100.63.255.255/path",
                "https://100.128.0.1/path",
            )
        )
        self.assertEqual(internal_url_line_counts(public_urls), {})

        private_urls = "\n".join(
            (
                "https://service.internal:8443/path",
                "https://100.64.0.1/path",
                "https://100.127.255.254:9443/path",
            )
        )
        self.assertEqual(internal_url_line_counts(private_urls), {1: 1, 2: 1, 3: 1})

    def test_historical_disposition_cannot_hide_an_added_internal_url(self) -> None:
        path = "docs/reviews/protected-example.md"
        original = "historical https://service.internal/path"
        dispositions = {path: {1: 1}}
        observed = {path: internal_url_line_counts(original)}
        self.assertEqual(disposition_mismatches(observed, dispositions), {})

        augmented = original + "\nnew https://100.64.0.8/path"
        observed = {path: internal_url_line_counts(augmented)}
        self.assertEqual(
            disposition_mismatches(observed, dispositions),
            {path: (2,)},
        )

    def test_self_disposition_cannot_hide_a_new_match_in_the_same_test(self) -> None:
        original_url = "https://" + "service.internal/path"
        added_url = "https://" + "100.64.0.8/path"
        original = f'def test_fixture():\n    value = "{original_url}"\n'
        original_matches = internal_url_matches(original)
        dispositions = dict(
            self_match_counts(original, "internal_url", original_matches)
        )
        self.assertEqual(
            self_disposition_mismatch_lines(
                original,
                "internal_url",
                original_matches,
                dispositions,
            ),
            (),
        )

        augmented = original.replace(original_url, f"{original_url} {added_url}")
        self.assertEqual(
            self_disposition_mismatch_lines(
                augmented,
                "internal_url",
                internal_url_matches(augmented),
                dispositions,
            ),
            (2,),
        )

    def test_no_undispositioned_high_confidence_secret_pattern_appears(self) -> None:
        findings = {}
        for path, text in self.text.items():
            matches = high_confidence_secret_matches(text)
            if path == SELF:
                lines = self_disposition_mismatch_lines(
                    text,
                    "high_confidence_secret",
                    matches,
                )
            else:
                lines = tuple(sorted({line for line, _ in matches}))
            if lines:
                findings[path] = lines
        self.assertEqual(findings, {})

    def test_new_plausible_secret_in_self_is_not_dispositioned_by_scope(self) -> None:
        disposed = "AKIA" + "A" * 16
        added = "AKIA" + "B" * 16
        original = f'def test_fixture():\n    value = "{disposed}"\n'
        original_matches = high_confidence_secret_matches(original)
        dispositions = dict(
            self_match_counts(
                original,
                "high_confidence_secret",
                original_matches,
            )
        )
        augmented = original.replace(disposed, f"{disposed} {added}")
        self.assertEqual(
            self_disposition_mismatch_lines(
                augmented,
                "high_confidence_secret",
                high_confidence_secret_matches(augmented),
                dispositions,
            ),
            (2,),
        )

    def test_active_operational_owners_contain_no_raw_private_fields_or_paths(self) -> None:
        raw_field = re.compile(
            r"^\s*(?:ip|address|hostname|private_dns|port|container_id|"
            r"device_path|mount_path|bucket|backup_repository|credential_path|"
            r"secret_path)\s*:",
            re.IGNORECASE | re.MULTILINE,
        )
        absolute_path = re.compile(r"(?<![A-Za-z0-9_.-])/(?:etc|opt|srv|mnt|home|var/lib)/\S+")
        provider_identity = re.compile(r"(?:s3://|backblaze|named backup bucket)", re.IGNORECASE)
        findings = []
        for path in PUBLIC_OPERATIONAL_OWNERS:
            text = self.text[path]
            if raw_field.search(text) or absolute_path.search(text) or provider_identity.search(text):
                findings.append(path)
        self.assertEqual(findings, [])

    def test_protected_historical_absolute_paths_have_narrow_dispositions(self) -> None:
        observed = {
            path: counts
            for path, text in self.text.items()
            if path.startswith("docs/reviews/")
            and path != "docs/reviews/repository-identity-r1-evidence-2026-08-02.md"
            and (
                counts := line_match_counts(
                    text,
                    ABSOLUTE_OPERATIONAL_PATH_PATTERN,
                )
            )
        }
        self.assertEqual(
            disposition_mismatches(
                observed,
                HISTORICAL_ABSOLUTE_PATH_DISPOSITIONS,
            ),
            {},
        )

    def test_readme_has_the_accepted_proof_surface_and_resolving_links(self) -> None:
        readme = self.text["README.md"]
        for heading in (
            "# Aiden Platform",
            "## What Exists Today",
            "## Architecture",
            "## Proof in Practice",
            "## Engineering Quality",
            "## Inspect or Run",
            "## Public and Private Boundary",
            "## Current and Future",
            "## Navigate Deeper",
        ):
            self.assertIn(heading, readme)

        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", readme)
        self.assertTrue(links)
        missing = []
        for link in links:
            target = link.split("#", 1)[0]
            if not target or "://" in target:
                continue
            if not (ROOT / target).exists():
                missing.append(target)
        self.assertEqual(missing, [])

    def test_active_state_and_mission_preserve_r1_lifecycle_truth(self) -> None:
        state = json.loads(self.text["docs/current-state.json"])
        self.assertEqual(state["phase"]["id"], "engineering-workflow-v1-1")
        self.assertEqual(state["phase"]["lifecycle"], "published")
        self.assertEqual(state["work_selection"]["status"], "intentional_idle")
        self.assertIsNone(state["work_selection"]["selected_checkpoint"])
        self.assertEqual(state["blockers"], [])
        self.assertEqual(state["unknowns"], [])
        self.assertEqual(set(state["authority"].values()), {"external-not-established-by-repository-or-atlas"})
        mission = self.text["docs/current-mission.md"]
        self.assertRegex(mission, r"R1 — Repository Identity and Public/Private Boundary is\s+owner-accepted, published, and complete\.")
        self.assertIn("S1, F2, F3", mission)
        self.assertIn("Not selected", mission)
        self.assertIn("Status: Intentional idle", mission)
        self.assertIn("owner selection of future work", mission.casefold())
        self.assertNotRegex(mission.casefold(), r"fresh adversarial review|pending")

    def test_renamed_documents_and_evidence_are_registered(self) -> None:
        infrastructure = infrastructure_documents()
        self.assertIn("docs/infrastructure-virtualization.md", infrastructure)
        self.assertNotIn("docs/infrastructure-gamer-pve.md", infrastructure)
        self.assertEqual(
            portfolio_evidence_documents(),
            ["docs/reviews/repository-identity-r1-evidence-2026-08-02.md"],
        )
        self.assertIsNotNone(definition_for("docs/infrastructure-virtualization.md"))
        self.assertIsNotNone(
            definition_for(
                "docs/reviews/repository-identity-r1-evidence-2026-08-02.md"
            )
        )

    def test_generated_ownership_matches_the_generator_input_graph(self) -> None:
        snapshot_definition = definition_for("docs/infrastructure-snapshot.md")
        self.assertIsNotNone(snapshot_definition)
        assert snapshot_definition is not None
        self.assertTrue(snapshot_definition.generated)
        self.assertEqual(
            snapshot_definition.generated_from,
            [
                "docs/infrastructure.md",
                "docs/infrastructure-virtualization.md",
                "docs/services.md",
            ],
        )
        self.assertEqual(
            snapshot_definition.managed_by,
            "tools/generate-context.py",
        )

        generator = runpy.run_path(str(ROOT / "tools/generate-context.py"))
        context_definition = definition_for("docs/aiden-context.md")
        self.assertIsNotNone(context_definition)
        assert context_definition is not None
        generator_sources = list(generator["AIDEN_CONTEXT_GENERATED_FROM"])
        self.assertEqual(context_definition.generated_from, generator_sources)
        self.assertIn("docs/changes", generator_sources)
        self.assertTrue(all((ROOT / path).exists() for path in generator_sources))

        structured_change_paths = generator["structured_change_paths"]()
        self.assertTrue(structured_change_paths)
        self.assertEqual(
            structured_change_paths,
            sorted((ROOT / "docs/changes").glob("*.yml")),
        )
        source_graph = generator["render_source_graph"]()
        self.assertIn("- docs/changes/ (`*.yml` structured records)", source_graph)
        self.assertIn(source_graph, self.text["docs/aiden-context.md"])

    def test_generated_date_is_deterministic_from_canonical_state(self) -> None:
        state = json.loads(self.text["docs/current-state.json"])
        expected = (
            f"Generated: {state['freshness']['effective_date']} "
            "(canonical-state effective date; deterministic)"
        )
        self.assertIn(expected, self.text["docs/aiden-context.md"])

    def test_active_r1_truth_is_separate_from_historical_candidate_chronology(
        self,
    ) -> None:
        evidence_path = (
            "docs/reviews/repository-identity-r1-evidence-2026-08-02.md"
        )
        docs_map_match = re.search(
            rf"(?ms)^- `{re.escape(evidence_path)}` — (?P<entry>.*?)"
            r"(?=^- `docs/reviews/|\Z)",
            self.text["docs/docs-map.md"],
        )
        self.assertIsNotNone(docs_map_match)
        assert docs_map_match is not None

        evidence_definition = definition_for(evidence_path)
        self.assertIsNotNone(evidence_definition)
        assert evidence_definition is not None

        evidence = self.text[evidence_path]
        final_heading = "## Final R1 Publication"
        self.assertEqual(evidence.count(final_heading), 1)
        before_final, found_final_heading, final_publication_body = (
            evidence.partition(final_heading)
        )
        self.assertEqual(found_final_heading, final_heading)

        chronology_boundary = re.search(r"(?m)^## ", before_final)
        self.assertIsNotNone(chronology_boundary)
        assert chronology_boundary is not None
        active_header_summary = before_final[: chronology_boundary.start()]
        historical_chronology = before_final[chronology_boundary.start() :]
        final_publication = found_final_heading + final_publication_body

        active_surfaces = {
            "README active prose": self.text["README.md"],
            "R1 docs-map entry": docs_map_match.group("entry"),
            "R1 document-definition purpose": evidence_definition.purpose,
            "R1 evidence active header/summary": active_header_summary,
            "R1 evidence final publication": final_publication,
        }
        stale_active_marker_patterns = (
            r"\bunstaged\b",
            r"\buncommitted\b",
            r"\bprospective publication commit\b",
            r"\bremaining publication boundary\b",
            r"(?:publication|review|owner acceptance)[^.\n]*"
            r"\bremain(?:s)? pending\b",
            r"\bpending (?:review|owner acceptance|acceptance|publication)\b",
        )
        for surface, text in active_surfaces.items():
            for marker in stale_active_marker_patterns:
                with self.subTest(surface=surface, marker=marker):
                    self.assertNotRegex(text.casefold(), marker)

        self.assertIn("unstaged and uncommitted", historical_chronology.casefold())
        publication_commit = "483f1111257c9b1608c100cb88c8304a17d85314"
        self.assertRegex(
            final_publication,
            rf"(?s)\bimmutable commit\s+`{publication_commit}`",
        )
        self.assertRegex(
            final_publication.casefold(),
            r"\bpublication outcome (?:occurred|was completed)\b",
        )


SELF_PRIVACY_DISPOSITIONS = {
    (
        "ip_literal",
        "<module>",
        95,
        "b0d56c1d28390f7e4ece0ae355b30ebe8c8618788c2d769736a939a7e0bb4dd4",
    ): 1,
    (
        "ip_literal",
        "<module>",
        96,
        "4b2228c26597aecab7d5894eb1ec83d915bc2e1a75d758b3b53471ce6aa2c91c",
    ): 1,
    (
        "ip_literal",
        "<module>",
        97,
        "b6da1098e40c579e98e90db3586dbc51897b22b28133a30c45aa6f31a5f0b88e",
    ): 1,
    (
        "ip_literal",
        "<module>",
        98,
        "4fb0798e0eb02d5310d95142b51ddadf3d03fcd929382309589f573c0f923264",
    ): 1,
    (
        "ip_literal",
        "<module>",
        99,
        "5da4236dba69f926f858153f06d49edc73f54ce8cd226d7239d1948e663610e0",
    ): 1,
    (
        "ip_literal",
        "test_internal_url_classifier_uses_exact_boundaries",
        449,
        "25ecb11bfd4a7ea50ba30b45ce32bdb1d3c083445643f00a75d3e039a1f39133",
    ): 1,
    (
        "ip_literal",
        "test_internal_url_classifier_uses_exact_boundaries",
        450,
        "0622464c1cff74f0dc58479d1b5329cb5edc290e50377b38b42c36d528853b3d",
    ): 1,
    (
        "ip_literal",
        "test_internal_url_classifier_uses_exact_boundaries",
        458,
        "9fee1dbd126b61ad5eb62f3d8f5e212f23c9b2e198dc972306821b4b2b9df745",
    ): 1,
    (
        "ip_literal",
        "test_historical_disposition_cannot_hide_an_added_internal_url",
        471,
        "99e68e6fb6f98ae9bbcea0fb5d7c831c326653011c5092cfe5daf4357f555984",
    ): 1,
    (
        "ip_literal",
        "test_self_disposition_cannot_hide_a_new_match_in_the_same_test",
        480,
        "99e68e6fb6f98ae9bbcea0fb5d7c831c326653011c5092cfe5daf4357f555984",
    ): 1,
    (
        "internal_url",
        "test_internal_url_classifier_uses_exact_boundaries",
        457,
        "3973e8f72e6b3292d4e95be96157a236e5c9b7444a4987892cf1253ca1c970eb",
    ): 1,
    (
        "internal_url",
        "test_internal_url_classifier_uses_exact_boundaries",
        458,
        "e02f7a62bd538cff9e53b3bec05f5f740f1c3fd639751346c476f871fe13f97e",
    ): 1,
    (
        "internal_url",
        "test_internal_url_classifier_uses_exact_boundaries",
        459,
        "f9d411589dde0d9963506dcf7ae3ab6108c10cf5b7bf1ed96a764e89504d46fc",
    ): 1,
    (
        "internal_url",
        "test_historical_disposition_cannot_hide_an_added_internal_url",
        466,
        "746095370fe2a67aaaa7f2414f15f9abf9312655094bf9166a3cbd76150be34a",
    ): 1,
    (
        "internal_url",
        "test_historical_disposition_cannot_hide_an_added_internal_url",
        471,
        "f1243b397a9d95c04fcc3ff96cdd383f067d1999e6773c198ffa0ebcfc8fd5df",
    ): 1,
    (
        "historical_host",
        "<module>",
        35,
        "28417f2fb39f8b22a594692ee92a59b717cc74570eefcf1d117be17937933163",
    ): 1,
    (
        "historical_host",
        "<module>",
        36,
        "28417f2fb39f8b22a594692ee92a59b717cc74570eefcf1d117be17937933163",
    ): 1,
    (
        "historical_host",
        "<module>",
        37,
        "28417f2fb39f8b22a594692ee92a59b717cc74570eefcf1d117be17937933163",
    ): 1,
    (
        "historical_host",
        "<module>",
        38,
        "28417f2fb39f8b22a594692ee92a59b717cc74570eefcf1d117be17937933163",
    ): 1,
    (
        "historical_host",
        "<module>",
        104,
        "28417f2fb39f8b22a594692ee92a59b717cc74570eefcf1d117be17937933163",
    ): 1,
    (
        "historical_host",
        "<module>",
        104,
        "49b3511f5ae71e18fb91cdd08fba6916608c5ea654f59e478bc433c93b5056cf",
    ): 1,
    (
        "historical_host",
        "test_renamed_documents_and_evidence_are_registered",
        629,
        "28417f2fb39f8b22a594692ee92a59b717cc74570eefcf1d117be17937933163",
    ): 1,
    (
        "legacy_identity",
        "<module>",
        22,
        "25255e764a9dd3bac6f2a542ba33fff8d97ef7030a82e3a0c033d6abe43c28cb",
    ): 1,
}


if __name__ == "__main__":
    unittest.main()
