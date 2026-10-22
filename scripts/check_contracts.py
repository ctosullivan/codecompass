"""Maintainer-only validator for Phase 82's oracle-contract/oracle-result
schema (`planning/contracts/<slug>/*.yaml`). Mirrors
`scripts/check_knowledge_base.py`'s own `--strict` convention exactly —
see that script's own module docstring for the shared rationale (no YAML
*library* avoidance here though: unlike the six canonical flat-record
kinds, `oracle-contract.yaml`/`oracle-result.yaml` are genuinely new file
formats this phase introduces, parsed via `codecompass.oracle`'s own real
YAML parsing, not a hand-rolled flat parser).

See `planning/phase-82-contract-and-evidence-foundation.md` §5/§5a/§8 and
`decisions/0080`/`0081` for the full design this implements.

    python scripts/check_contracts.py [--strict] [--ledgerkit-root PATH]

Report-only by default (always exits 0). `--strict` exits 1 if any
*blocking* finding is reported. `--ledgerkit-root` points at the real
Ledgerkit checkout used to recompute `tested_subject_digest`/
`test_input_digest` live against the *current* implementation (defaults
to `~/projects/ledgerkit`); when that path does not exist, digest
recomputation against a live checkout is skipped with an informational
finding — the contract/scope/raw-output checks (which need no external
checkout) still run in full.

Not part of the `codecompass` package: like `check_knowledge_base.py`,
this checks CodeCompass's own planning artefacts, not a consuming
project's, and is not a `codecompass` subcommand.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LEDGERKIT_ROOT = Path.home() / "projects" / "ledgerkit"

_ID_PATTERN = re.compile(r"\b(OBS|EV|CL|DE|DEC|REQ)-[A-Z0-9]+-\d+\b")

# §8.3 (CLAUDE.md §1 L-075, depth not just scope): an Evidence citing a
# Ledgerkit symbol directly, in the convention this phase's own EV-
# records use: "<path>:<line>[-<line2>] def|class <symbol>".
_SOURCE_REF_WITH_SYMBOL_RE = re.compile(
    r"^(?P<path>[^:]+):(?P<start>\d+)(?:-(?P<end>\d+))?\s+(?P<kind>def|class)\s+(?P<symbol>\w+)$"
)


@dataclass
class Finding:
    rule: str
    message: str
    strict: bool = True


def _load_oracle_module():
    """Mirrors `check_knowledge_base.py::_load_knowledge_intermediate`'s
    own import-or-None pattern — a bare checkout shouldn't crash this
    whole script."""
    src_path = ROOT / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    try:
        from codecompass import oracle

        return oracle
    except Exception:
        return None


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _parse_flat_fields(text: str) -> dict[str, str]:
    """The same minimal, deliberately duplicated flat-record parse every
    other maintainer script in this repository already has its own copy
    of (`check_knowledge_base.py::parse_record_text`,
    `knowledge_intermediate.py::parse_record_text`) — only `id`/`kind`/
    `status` ever need reading here, never full prose."""
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if not line or line[0] in " \t#":
            continue
        match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip()
    return fields


def _iter_contract_slugs(root: Path) -> list[Path]:
    contracts_dir = root / "planning" / "contracts"
    if not contracts_dir.is_dir():
        return []
    return sorted(p for p in contracts_dir.iterdir() if p.is_dir())


def check_contract_schema(slug_dir: Path, oracle, root: Path = ROOT):
    """Returns `(findings, contract_or_none)`."""
    findings: list[Finding] = []
    contract_path = slug_dir / "oracle-contract.yaml"
    if not contract_path.is_file():
        findings.append(
            Finding(
                "contract-missing-oracle-contract",
                f"{slug_dir.relative_to(root)}: no oracle-contract.yaml found",
            )
        )
        return findings, None
    try:
        contract = oracle.parse_oracle_contract(contract_path)
    except oracle.OracleSchemaError as exc:
        findings.append(
            Finding(
                "contract-schema-error",
                f"{contract_path.relative_to(root)}: {exc}",
            )
        )
        return findings, None
    return findings, contract


def check_contract_id_resolves(slug: str, contract, root: Path = ROOT) -> list[Finding]:
    """`contract_id` must resolve to a real `REQ-` record in the matching
    `planning/knowledge/<slug>/` directory — a contract with no governing
    Requirement at all has nothing it is actually a contract *for*."""
    findings: list[Finding] = []
    knowledge_slug_dir = root / "planning" / "knowledge" / slug
    resolved = False
    if knowledge_slug_dir.is_dir():
        for yaml_path in knowledge_slug_dir.glob("REQ-*.yaml"):
            fields = _parse_flat_fields(yaml_path.read_text(encoding="utf-8"))
            if fields.get("id") == contract.contract_id:
                resolved = True
                break
    if not resolved:
        findings.append(
            Finding(
                "contract-dangling-contract-id",
                f"{slug}: contract_id={contract.contract_id!r} does not resolve "
                f"to a real REQ- record in planning/knowledge/{slug}/",
            )
        )
    return findings


def _iter_result_files(slug_dir: Path):
    results_dir = slug_dir / "results"
    if not results_dir.is_dir():
        return
    yield from sorted(results_dir.glob("*.yaml"))


def check_result_schema(slug_dir: Path, oracle, root: Path = ROOT):
    """Returns `(findings, results)` where `results` is
    `list[tuple[Path, OracleResult]]` — a result's own file path is
    carried alongside it rather than reconstructed from `check_id`, since
    `decisions/0082` §C's immutable `<check_id>--<run_id>.yaml` naming
    means multiple files can legitimately share one `check_id`. A
    malformed result file is its own finding and is excluded from
    `results` (never silently half-parsed)."""
    findings: list[Finding] = []
    results: list[tuple[Path, object]] = []
    for result_path in _iter_result_files(slug_dir):
        try:
            results.append((result_path, oracle.parse_oracle_result(result_path)))
        except oracle.OracleSchemaError as exc:
            findings.append(
                Finding(
                    "result-schema-error",
                    f"{result_path.relative_to(root)}: {exc}",
                )
            )
    return findings, results


def check_result_cross_references(
    slug_dir: Path, contract, results, root: Path = ROOT
) -> list[Finding]:
    findings: list[Finding] = []
    for result_path, result in results:
        id_mismatch = (
            result.contract_id != contract.contract_id
            or result.oracle_contract_id != contract.contract_id
        )
        if id_mismatch:
            findings.append(
                Finding(
                    "contract-result-contract-id-mismatch",
                    f"{result_path.relative_to(root)}: contract_id/"
                    f"oracle_contract_id does not match this slug's own "
                    f"contract_id={contract.contract_id!r}",
                )
            )
        check = contract.check_by_id(result.check_id)
        if check is None:
            findings.append(
                Finding(
                    "contract-result-dangling-check-id",
                    f"{result_path.relative_to(root)}: check_id="
                    f"{result.check_id!r} has no matching entry in this "
                    "contract's own checks: list",
                )
            )
    return findings


def check_result_integrity(
    slug_dir: Path, contract, results, oracle, *, ledgerkit_root: Path, root: Path = ROOT
) -> list[Finding]:
    """§8.5/§8.6 — tamper-evidence/integrity, via
    `oracle.evaluate_result_precedence` (the single source of truth for
    whether a result actually counts, never a self-reported field).

    `decisions/0082` §A: when the checkout is unavailable *and* a
    required check's only on-record evidence is a historically recorded
    `PASS`, this is now a blocking finding
    (`contract-current-verification-unconfirmable`), not merely the
    pre-existing informational `contract-ledgerkit-checkout-unavailable`
    note — `--strict` must not report "no findings" while silently unable
    to confirm a required check's claimed current state. An unavailable
    checkout with nothing currently relying on it (no required check has
    any recorded PASS yet) stays informational only, unchanged."""
    findings: list[Finding] = []
    repo_root = ledgerkit_root if ledgerkit_root.is_dir() else None
    contract_path = slug_dir / "oracle-contract.yaml"
    if repo_root is None:
        findings.append(
            Finding(
                "contract-ledgerkit-checkout-unavailable",
                f"{ledgerkit_root} does not exist — skipped live "
                "tested_subject_digest/test_input_digest recomputation "
                "against the current implementation (contract/scope/"
                "raw-output integrity checks still ran in full)",
                strict=False,
            )
        )
        for check in contract.checks:
            if not check.required:
                continue
            has_recorded_pass = any(
                result.check_id == check.check_id
                and oracle.evaluate_result_precedence(
                    result, contract, check, contract_path=contract_path, repo_root=None
                )[0]
                == "PASS"
                for _result_path, result in results
            )
            if has_recorded_pass:
                findings.append(
                    Finding(
                        "contract-current-verification-unconfirmable",
                        f"{slug_dir.relative_to(root)}: required check_id="
                        f"{check.check_id!r} (scope={check.scope!r}) has only a "
                        f"historically recorded PASS -- {ledgerkit_root} is "
                        "unavailable, so current verification cannot be "
                        "confirmed against the implementation actually tested",
                    )
                )
    for result_path, result in results:
        check = contract.check_by_id(result.check_id)
        if check is None:
            continue  # already reported by check_result_cross_references
        effective_outcome, reason = oracle.evaluate_result_precedence(
            result, contract, check, contract_path=contract_path, repo_root=repo_root
        )
        if effective_outcome == "INVALID" and result.outcome != "INVALID":
            findings.append(
                Finding(
                    "contract-result-integrity-mismatch",
                    f"{result_path.relative_to(root)}: recorded outcome="
                    f"{result.outcome!r} but independent recomputation finds "
                    f"this result INVALID: {reason}",
                )
            )
    return findings


def check_gap_aggregate(
    slug_dir: Path, contract, results, oracle, *, ledgerkit_root: Path, root: Path = ROOT
) -> list[Finding]:
    """Informational only — a `GAP` is a legitimate, expected state for a
    not-yet-exercised required check; it only becomes a problem in
    combination with a record claiming `status: verified`
    (`check_knowledge_base.py::check_verified_status_cites_passing_oracle_result`,
    not this script's own concern)."""
    findings: list[Finding] = []
    repo_root = ledgerkit_root if ledgerkit_root.is_dir() else None
    contract_path = slug_dir / "oracle-contract.yaml"
    plain_results = [result for _result_path, result in results]
    aggregates = oracle.aggregate_contract(
        contract, plain_results, contract_path=contract_path, repo_root=repo_root
    )
    for agg in aggregates:
        if agg.state == "GAP":
            findings.append(
                Finding(
                    "contract-check-gap",
                    f"{slug_dir.relative_to(root)}: check_id={agg.check_id!r} "
                    f"(scope={agg.scope!r}) is required but has no current, "
                    f"matching-scope PASS — observed outcomes: {agg.observed_outcomes or 'none'}",
                    strict=False,
                )
            )
    return findings


def check_source_ref_symbol_depth(
    feature_dir: Path, ledgerkit_root: Path, root: Path = ROOT
) -> list[Finding]:
    """CLAUDE.md §1 L-075 (depth, not just scope): an Evidence citing a
    Ledgerkit symbol via this phase's own `"<path>:<line> def|class
    <symbol>"` source_ref convention must have that symbol actually
    present at the cited location — not merely a file path that resolves."""
    findings: list[Finding] = []
    if not feature_dir.is_dir():
        return findings
    for yaml_path in sorted(feature_dir.glob("EV-*.yaml")):
        fields = _parse_flat_fields(yaml_path.read_text(encoding="utf-8"))
        if fields.get("kind") != "evidence":
            continue
        raw_ref = fields.get("source_ref", "")
        if not raw_ref or raw_ref == "null":
            continue
        source_ref = _unquote(raw_ref)
        match = _SOURCE_REF_WITH_SYMBOL_RE.match(source_ref)
        if not match:
            continue  # not this checkable convention -- not this check's concern
        if not ledgerkit_root.is_dir():
            findings.append(
                Finding(
                    "contract-ledgerkit-checkout-unavailable",
                    f"{yaml_path.relative_to(root)}: cites {source_ref!r} but "
                    f"{ledgerkit_root} does not exist — skipped symbol-depth check",
                    strict=False,
                )
            )
            continue
        candidate = ledgerkit_root / match.group("path")
        if not candidate.is_file():
            findings.append(
                Finding(
                    "contract-source-ref-missing-file",
                    f"{yaml_path.relative_to(root)}: cites {source_ref!r}, but "
                    f"{candidate} does not exist in the Ledgerkit checkout",
                )
            )
            continue
        start = int(match.group("start"))
        end = int(match.group("end") or start)
        kind, symbol = match.group("kind"), match.group("symbol")
        lines = candidate.read_text(encoding="utf-8").splitlines()
        window = lines[max(0, start - 3) : min(len(lines), end + 3)]
        pattern = re.compile(rf"^\s*{kind}\s+{re.escape(symbol)}\b")
        if not any(pattern.match(line) for line in window):
            findings.append(
                Finding(
                    "contract-source-ref-symbol-not-found",
                    f"{yaml_path.relative_to(root)}: cites {source_ref!r}, but "
                    f"no {kind} {symbol!r} was found near that location in "
                    f"{candidate} — the citation resolves to a real file but "
                    "not to the symbol it claims",
                )
            )
    return findings


def run_all(root: Path = ROOT, ledgerkit_root: Path = DEFAULT_LEDGERKIT_ROOT) -> list[Finding]:
    findings: list[Finding] = []
    oracle = _load_oracle_module()
    if oracle is None:
        # decisions/0082 final corrective pass §B: every oracle-contract/
        # oracle-result check below is skipped entirely when this import
        # fails -- `--strict` must not report success while silently
        # unable to run its own required assurance machinery. Blocking,
        # not informational (unlike `contract-ledgerkit-checkout-
        # unavailable`, which skips only the live-digest recomputation
        # while every other check still runs in full).
        return [
            Finding(
                "contract-codecompass-unimportable",
                "could not import codecompass.oracle (src/ not importable, or "
                "a required dependency such as pyyaml is missing) — every "
                "oracle-contract/oracle-result check was skipped; this is a "
                "failure of the verification machinery itself, not an "
                "optional check",
            )
        ]
    for slug_dir in _iter_contract_slugs(root):
        slug = slug_dir.name
        contract_findings, contract = check_contract_schema(slug_dir, oracle, root)
        findings.extend(contract_findings)
        if contract is None:
            continue
        findings.extend(check_contract_id_resolves(slug, contract, root))
        result_findings, results = check_result_schema(slug_dir, oracle, root)
        findings.extend(result_findings)
        findings.extend(check_result_cross_references(slug_dir, contract, results, root))
        findings.extend(
            check_result_integrity(
                slug_dir, contract, results, oracle, ledgerkit_root=ledgerkit_root, root=root
            )
        )
        findings.extend(
            check_gap_aggregate(
                slug_dir, contract, results, oracle, ledgerkit_root=ledgerkit_root, root=root
            )
        )
        findings.extend(
            check_source_ref_symbol_depth(
                root / "planning" / "knowledge" / slug, ledgerkit_root, root
            )
        )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--ledgerkit-root", type=Path, default=DEFAULT_LEDGERKIT_ROOT)
    args = parser.parse_args()

    findings = run_all(ROOT, args.ledgerkit_root)
    blocking = [f for f in findings if f.strict]

    if not findings:
        print("check_contracts: no findings")
    else:
        print(f"check_contracts: {len(findings)} finding(s)")
        for f in findings:
            tag = "" if f.strict else " (info)"
            print(f"  [{f.rule}]{tag} {f.message}")

    return 1 if (args.strict and blocking) else 0


if __name__ == "__main__":
    sys.exit(main())
