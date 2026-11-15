"""Phase 82 — oracle contract/result schema, tested-subject digesting, and
deterministic PASS/FAIL/GAP/INVALID precedence/aggregation.

See `planning/phase-82-contract-and-evidence-foundation.md` §5/§5a and
`decisions/0080`/`0081` for the full design — this module implements it,
it does not re-derive it.

Two new, minimal, machine-readable file formats under
`planning/contracts/<slug>/`, read as real YAML (`pyyaml`, an existing
dependency) — unlike the six canonical knowledge-record kinds
(`knowledge_intermediate.py`), which deliberately use a hand-rolled flat
parser, these are genuinely new file formats this phase introduces, not
an extension of the existing six-kind record shape.

Exactly one `execution_provider` is implemented (`pytest`) — this is
deliberately not a provider-plugin framework (`decisions/0081`'s own
"avoid designing a general-purpose execution-provider framework").

`GAP` is never a value `OracleResult.outcome` itself takes — it is
computed by `aggregate_contract`, never trusted from a self-reported
field (`decisions/0081` §2).
"""

from __future__ import annotations

import hashlib
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import yaml

_SCHEMA_VERSION = 1
_SUPPORTED_SCHEMA_VERSIONS = {1}
_SUPPORTED_EXECUTION_PROVIDERS = {"pytest"}

# Phase 88 §5.3: `run_pytest_check` has no timeout/output cap at all for
# a maintainer at a terminal who can interrupt a hang -- unacceptable
# for a remotely-triggerable MCP tool. Defaults chosen to comfortably
# exceed this project's own real pytest run durations against
# Ledgerkit's current suite size while still bounding a genuine hang.
DEFAULT_CHECK_TIMEOUT_SECONDS = 300.0
DEFAULT_CHECK_MAX_OUTPUT_BYTES = 10 * 1024 * 1024


class OracleSchemaError(ValueError):
    """A contract or result file is missing a required field, uses a
    value outside its own closed enum, or is otherwise structurally
    malformed. Raised by the parse functions; `scripts/check_contracts.py`
    catches this and turns it into a reportable Finding rather than
    letting it propagate as an uncaught exception."""


class OracleDigestError(ValueError):
    """A named `tested_paths`/`test_input_paths` entry could not be read
    at digest-computation time (missing file, unreadable). Per
    `decisions/0081` §4, a digest is never computed over a partial file
    set — this always aborts the whole computation rather than silently
    omitting the unresolvable path."""


# ---------------------------------------------------------------------------
# Hashing — reuses scripts/prepare_cleanroom_branch.py's own
# sha256_file/sha256_bytes/_canonical_digest_of_hashes construction
# (decisions/0077's payload_tree_sha256 precedent), duplicated rather than
# imported because scripts/ is deliberately not part of the installed
# package (the same reason knowledge_intermediate.py duplicates
# check_knowledge_base.py's own parser instead of importing it).
# ---------------------------------------------------------------------------


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_digest_of_hashes(file_hashes: dict[str, str]) -> str:
    """SHA-256 over a canonical, sorted "hash  path" manifest — identical
    construction to `prepare_cleanroom_branch.py::_canonical_digest_of_hashes`."""
    canonical_lines = [f"{file_hashes[rel]}  {rel}" for rel in sorted(file_hashes)]
    canonical_text = "\n".join(canonical_lines) + "\n"
    return sha256_bytes(canonical_text.encode("utf-8"))


def compute_tree_digest(root: Path, relpaths: list[str]) -> str:
    """The content digest of exactly `relpaths` (resolved under `root`) —
    `decisions/0081` §4's `tested_subject_digest`/`test_input_digest`
    construction. Raises `OracleDigestError`, naming every unresolvable
    path, if even one cannot be read — never computed over a partial set.
    A dirty worktree needs no special detection: this always hashes
    whatever bytes are actually on disk, so a dirty checkout simply
    produces a different digest than a clean one."""
    missing: list[str] = []
    per_file: dict[str, str] = {}
    for rel in relpaths:
        candidate = root / rel
        if not candidate.is_file():
            missing.append(rel)
            continue
        per_file[rel] = sha256_file(candidate)
    if missing:
        raise OracleDigestError(
            f"cannot compute digest under {root}: missing or unreadable path(s) {missing}"
        )
    return canonical_digest_of_hashes(per_file)


# ---------------------------------------------------------------------------
# Schema dataclasses
# ---------------------------------------------------------------------------


@dataclass
class OracleCheck:
    check_id: str
    scope: str
    execution_provider: str
    check_reference: str
    test_input_paths: list[str]
    required: bool


@dataclass
class OracleContract:
    schema_version: int
    contract_id: str
    tested_paths: list[str]
    checks: list[OracleCheck]

    def check_by_id(self, check_id: str) -> OracleCheck | None:
        return next((c for c in self.checks if c.check_id == check_id), None)


@dataclass
class OracleResult:
    schema_version: int
    run_id: str
    contract_id: str
    check_id: str
    scope: str
    baseline_id: str | None
    tested_subject_digest: str
    oracle_contract_id: str
    oracle_contract_content_hash: str
    test_input_digest: str
    raw_output_ref: str
    raw_output_sha256: str
    outcome: str  # "PASS" | "FAIL" | "INVALID" -- never "GAP" (see module docstring)
    executed_at: str
    execution_provider: str
    environment_descriptor: str | None = None
    invalid_reason: str | None = None


_CONTRACT_REQUIRED_TOP = {"schema_version", "contract_id", "tested_paths", "checks"}
_CHECK_REQUIRED = {
    "check_id",
    "scope",
    "execution_provider",
    "check_reference",
    "test_input_paths",
    "required",
}
_RESULT_REQUIRED = {
    "schema_version",
    "run_id",
    "contract_id",
    "check_id",
    "scope",
    "baseline_id",
    "tested_subject_digest",
    "oracle_contract_id",
    "oracle_contract_content_hash",
    "test_input_digest",
    "raw_output_ref",
    "raw_output_sha256",
    "outcome",
    "executed_at",
    "execution_provider",
}
_OUTCOME_VALUES = {"PASS", "FAIL", "INVALID"}


def _safe_load_yaml(path: Path, *, text: str | None = None) -> object:
    """Malformed YAML becomes a reportable `OracleSchemaError`, never an
    uncaught `yaml.YAMLError` -- the same controlled-finding discipline
    `check_contracts.py`/`check_knowledge_base.py` already apply to every
    other failure mode (`decisions/0082` §D).

    `text`, when given (plan `planning/phase-88-agent-integration-mcp.md`
    §17.3/§18.1), is used verbatim instead of re-reading `path` -- the
    caller has already performed its own atomic, confined read (e.g. an
    `O_NOFOLLOW` open, possibly `dir_fd`-relative) and this function must
    not reopen `path` by name a second time, which would reintroduce the
    exact check-then-use race the confined read was meant to close.
    `path` is still used for every error message and is never itself
    read when `text` is supplied."""
    try:
        raw_text = text if text is not None else path.read_text(encoding="utf-8")
        return yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise OracleSchemaError(f"{path}: malformed YAML: {exc}") from exc


def _require_non_empty_str(value: object, field_name: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OracleSchemaError(
            f"{path}: {field_name} must be a non-empty string, got {value!r}"
        )
    return value


def _require_str_list(value: object, field_name: str, path: Path) -> list[str]:
    if not isinstance(value, list) or not value:
        raise OracleSchemaError(f"{path}: {field_name} must be a non-empty list")
    for i, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise OracleSchemaError(
                f"{path}: {field_name}[{i}] must be a non-empty string, got {item!r}"
            )
    return list(value)


def _require_bool(value: object, field_name: str, path: Path) -> bool:
    if not isinstance(value, bool):
        raise OracleSchemaError(
            f"{path}: {field_name} must be a real YAML boolean (true/false), got "
            f"{value!r} ({type(value).__name__}) -- a string is never interpreted "
            "as a boolean here (decisions/0082 §D)"
        )
    return value


def _require_int(value: object, field_name: str, path: Path) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise OracleSchemaError(f"{path}: {field_name} must be an integer, got {value!r}")
    return value


def _require_schema_version(value: object, path: Path) -> int:
    version = _require_int(value, "schema_version", path)
    if version not in _SUPPORTED_SCHEMA_VERSIONS:
        raise OracleSchemaError(
            f"{path}: schema_version={version!r} is not supported "
            f"(supported: {sorted(_SUPPORTED_SCHEMA_VERSIONS)})"
        )
    return version


def _require_execution_provider(value: object, field_name: str, path: Path) -> str:
    provider = _require_non_empty_str(value, field_name, path)
    if provider not in _SUPPORTED_EXECUTION_PROVIDERS:
        raise OracleSchemaError(
            f"{path}: {field_name}={provider!r} is not supported "
            f"(supported: {sorted(_SUPPORTED_EXECUTION_PROVIDERS)})"
        )
    return provider


def parse_oracle_contract(path: Path, *, text: str | None = None) -> OracleContract:
    """`text`, when given, is used in place of reading `path` (see
    `_safe_load_yaml`'s own docstring) -- added for `find_gaps`'s own
    `dir_fd`-confined contract read (§18.1)."""
    raw = _safe_load_yaml(path, text=text)
    if not isinstance(raw, dict):
        raise OracleSchemaError(f"{path}: top level must be a mapping")
    missing = _CONTRACT_REQUIRED_TOP - raw.keys()
    if missing:
        raise OracleSchemaError(f"{path}: missing required field(s) {sorted(missing)}")
    schema_version = _require_schema_version(raw["schema_version"], path)
    contract_id = _require_non_empty_str(raw["contract_id"], "contract_id", path)
    tested_paths = _require_str_list(raw["tested_paths"], "tested_paths", path)
    checks_raw = raw["checks"]
    if not isinstance(checks_raw, list) or not checks_raw:
        raise OracleSchemaError(
            f"{path}: 'checks' must be a non-empty list — an empty or absent "
            "checks collection can never establish verification"
        )
    checks: list[OracleCheck] = []
    seen_ids: set[str] = set()
    for i, entry in enumerate(checks_raw):
        if not isinstance(entry, dict):
            raise OracleSchemaError(f"{path}: checks[{i}] must be a mapping")
        missing_check = _CHECK_REQUIRED - entry.keys()
        if missing_check:
            raise OracleSchemaError(
                f"{path}: checks[{i}] missing required field(s) {sorted(missing_check)}"
            )
        check_id = _require_non_empty_str(entry["check_id"], f"checks[{i}].check_id", path)
        if check_id in seen_ids:
            raise OracleSchemaError(
                f"{path}: duplicate check_id {check_id!r} — check_id must "
                "be unique within one contract"
            )
        seen_ids.add(check_id)
        scope = _require_non_empty_str(entry["scope"], f"checks[{i}].scope", path)
        execution_provider = _require_execution_provider(
            entry["execution_provider"], f"checks[{i}].execution_provider", path
        )
        check_reference = _require_non_empty_str(
            entry["check_reference"], f"checks[{i}].check_reference", path
        )
        test_input_paths = _require_str_list(
            entry["test_input_paths"], f"checks[{i}].test_input_paths", path
        )
        required = _require_bool(entry["required"], f"checks[{i}].required", path)
        checks.append(
            OracleCheck(
                check_id=check_id,
                scope=scope,
                execution_provider=execution_provider,
                check_reference=check_reference,
                test_input_paths=test_input_paths,
                required=required,
            )
        )
    return OracleContract(
        schema_version=schema_version,
        contract_id=contract_id,
        tested_paths=tested_paths,
        checks=checks,
    )


def parse_oracle_result(path: Path, *, text: str | None = None) -> OracleResult:
    """`text`, when given, is used in place of reading `path` (see
    `_safe_load_yaml`'s own docstring) -- added for `knowledge_api.py`'s
    own confined-read call sites (§17.3/§18.1), so a result already read
    atomically (possibly `dir_fd`-relative) is never reopened by name."""
    raw = _safe_load_yaml(path, text=text)
    if not isinstance(raw, dict):
        raise OracleSchemaError(f"{path}: top level must be a mapping")
    missing = _RESULT_REQUIRED - raw.keys()
    if missing:
        raise OracleSchemaError(f"{path}: missing required field(s) {sorted(missing)}")
    outcome = raw["outcome"]
    # Type validated *before* the enum-membership check: `outcome not in
    # a_set` computes hash(outcome) first, and an unhashable value (a
    # YAML list/mapping from malformed input) raises an uncaught
    # `TypeError` rather than reaching this function's own controlled
    # `OracleSchemaError` -- confirmed this session (decisions/0082 final
    # corrective pass §C).
    if not isinstance(outcome, str):
        raise OracleSchemaError(
            f"{path}: outcome must be a string, got {outcome!r} ({type(outcome).__name__})"
        )
    if outcome not in _OUTCOME_VALUES:
        raise OracleSchemaError(
            f"{path}: outcome={outcome!r} is not one of {sorted(_OUTCOME_VALUES)} "
            "-- GAP is never a per-result outcome (decisions/0081 §2)"
        )
    invalid_reason_raw = raw.get("invalid_reason")
    if invalid_reason_raw is not None and not isinstance(invalid_reason_raw, str):
        raise OracleSchemaError(
            f"{path}: invalid_reason must be a string or absent, got "
            f"{invalid_reason_raw!r} ({type(invalid_reason_raw).__name__})"
        )
    if outcome == "INVALID" and not invalid_reason_raw:
        raise OracleSchemaError(
            f"{path}: outcome: INVALID requires a non-empty invalid_reason"
        )
    for optional_field in ("baseline_id", "environment_descriptor"):
        optional_value = raw.get(optional_field)
        if optional_value is not None and not isinstance(optional_value, str):
            raise OracleSchemaError(
                f"{path}: {optional_field} must be a string or absent, got "
                f"{optional_value!r} ({type(optional_value).__name__})"
            )
    schema_version = _require_schema_version(raw["schema_version"], path)
    for field_name in (
        "run_id", "contract_id", "check_id", "scope", "oracle_contract_id",
        "oracle_contract_content_hash", "raw_output_ref", "raw_output_sha256", "executed_at",
    ):
        _require_non_empty_str(raw[field_name], field_name, path)
    # tested_subject_digest/test_input_digest may legitimately be the
    # empty string only when outcome: INVALID -- evaluate_check's own
    # digest-computation-failed branch records exactly this (a named path
    # could not be read at all, so no digest could ever be computed); any
    # other outcome must carry a real, non-empty digest.
    for digest_field in ("tested_subject_digest", "test_input_digest"):
        if outcome != "INVALID":
            _require_non_empty_str(raw[digest_field], digest_field, path)
        elif not isinstance(raw[digest_field], str):
            raise OracleSchemaError(f"{path}: {digest_field} must be a string")
    execution_provider = _require_execution_provider(
        raw["execution_provider"], "execution_provider", path
    )
    return OracleResult(
        schema_version=schema_version,
        run_id=raw["run_id"],
        contract_id=raw["contract_id"],
        check_id=raw["check_id"],
        scope=raw["scope"],
        baseline_id=raw.get("baseline_id"),
        tested_subject_digest=raw["tested_subject_digest"],
        oracle_contract_id=raw["oracle_contract_id"],
        oracle_contract_content_hash=raw["oracle_contract_content_hash"],
        test_input_digest=raw["test_input_digest"],
        raw_output_ref=raw["raw_output_ref"],
        raw_output_sha256=raw["raw_output_sha256"],
        outcome=outcome,
        executed_at=raw["executed_at"],
        execution_provider=execution_provider,
        environment_descriptor=raw.get("environment_descriptor"),
        invalid_reason=raw.get("invalid_reason"),
    )


def write_oracle_result(path: Path, result: OracleResult) -> None:
    data = {
        "schema_version": result.schema_version,
        "run_id": result.run_id,
        "contract_id": result.contract_id,
        "check_id": result.check_id,
        "scope": result.scope,
        "baseline_id": result.baseline_id,
        "tested_subject_digest": result.tested_subject_digest,
        "oracle_contract_id": result.oracle_contract_id,
        "oracle_contract_content_hash": result.oracle_contract_content_hash,
        "test_input_digest": result.test_input_digest,
        "environment_descriptor": result.environment_descriptor,
        "raw_output_ref": result.raw_output_ref,
        "raw_output_sha256": result.raw_output_sha256,
        "outcome": result.outcome,
        "executed_at": result.executed_at,
        "execution_provider": result.execution_provider,
        "invalid_reason": result.invalid_reason,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Execution — exactly one provider (pytest), a manual/scripted invocation,
# not a provider-plugin framework (decisions/0081 §1).
# ---------------------------------------------------------------------------


def _interpreter_for(repo_root: Path) -> str:
    """Prefers the target repository's own `.venv` interpreter (the real
    environment its own tests are meant to run under — confirmed
    necessary this session: CodeCompass's own interpreter has no
    `pytest`, and Ledgerkit's dependencies are only installed into its
    own `.venv`) — falls back to this process's own interpreter only
    when the target has no `.venv` of its own."""
    candidate = repo_root / ".venv" / "bin" / "python"
    return str(candidate) if candidate.is_file() else sys.executable


def _classify_pytest_junit(
    junit_path: Path, returncode: int
) -> tuple[str, str | None]:
    """Classifies a completed pytest invocation from its own structured
    `--junit-xml` report (a feature already built into pytest -- no new
    dependency) rather than from its bare exit code, since real pytest
    (confirmed this session, 9.1.1) reuses exit code 1 for both a genuine
    assertion failure and other conditions, and separately returns 2 for
    a collection error, 4 for an invalid/nonexistent node id or file
    path, and 5 for a syntactically valid file with zero matching tests
    -- none of which is a behavioural defect in the tested subject
    (`decisions/0082` §B). Also rejects an all-skipped execution as
    `INVALID` rather than `PASS` (real pytest 9.1.1, confirmed this
    session: an all-skipped run exits 0 with `tests` counting every
    skipped testcase, so `tests > 0` alone is not sufficient evidence
    that anything actually ran -- decisions/0082 final corrective pass
    §A). Returns `(outcome, invalid_reason)` where `outcome` is always
    one of `PASS`/`FAIL`/`INVALID`."""
    if not junit_path.is_file():
        return "INVALID", (
            f"pytest produced no junit-xml report (returncode={returncode}) -- "
            "the execution environment itself failed before any test could run "
            "(e.g. a missing pytest/dependency installation); see raw output"
        )
    try:
        root = ET.fromstring(junit_path.read_text(encoding="utf-8"))
    except ET.ParseError as exc:
        return "INVALID", f"could not parse junit-xml report: {exc}"
    suite = root.find("testsuite")
    if suite is None:
        return "INVALID", "junit-xml report has no <testsuite> element"
    tests = int(suite.get("tests", "0"))
    errors = int(suite.get("errors", "0"))
    failures = int(suite.get("failures", "0"))
    skipped = int(suite.get("skipped", "0"))
    if tests == 0:
        return "INVALID", (
            "check_reference resolved to zero collected tests -- an invalid, "
            "mistyped, or no-longer-existent pytest node id (or a file with no "
            "matching test function) can never establish PASS or FAIL"
        )
    if tests - skipped <= 0:
        return "INVALID", (
            f"all {tests} collected test(s) were skipped, not executed -- a "
            "skipped test asserts nothing about the tested subject's actual "
            "behaviour and can never by itself establish PASS (decisions/0082 "
            "final corrective pass §A); see raw output for the skip reason(s)"
        )
    if errors:
        messages = []
        for testcase in suite.findall("testcase"):
            error_el = testcase.find("error")
            if error_el is None:
                continue
            messages.append(
                f"{testcase.get('classname')}::{testcase.get('name')}: "
                f"{error_el.get('message', 'collection error')}"
            )
        return "INVALID", (
            f"{errors} collection/execution error(s), not a behavioural test "
            f"failure: {'; '.join(messages) or 'see raw output'}"
        )
    if failures:
        return "FAIL", None
    return "PASS", None


def _read_bounded(
    stream, key: str, captured: dict[str, list[str]], byte_counts: dict[str, int],
    max_output_bytes: int, cap_breached: threading.Event,
) -> None:
    """Reads `stream` incrementally in fixed-size chunks, accumulating
    into `captured[key]` and tracking `byte_counts[key]`, stopping as
    soon as the combined total across both streams exceeds
    `max_output_bytes` -- bounded *during* execution, not a post-hoc
    truncation of an already-fully-buffered result (§5.3, second-round
    correction: `subprocess.run(..., capture_output=True)` buffers the
    entire output in memory before any cap could apply at all, so a
    flooding process already exhausts memory before that cap would ever
    run). Runs in its own thread so one stream filling its OS pipe
    buffer can never block the other from being drained."""
    try:
        while True:
            chunk = stream.read(4096)
            if not chunk:
                break
            captured[key].append(chunk)
            byte_counts[key] += len(chunk.encode("utf-8", errors="replace"))
            if sum(byte_counts.values()) > max_output_bytes:
                cap_breached.set()
                break
    except (OSError, ValueError):
        # The pipe can legitimately raise once the process group is
        # killed out from under this read (e.g. closed/invalid fd) --
        # treated as end-of-stream, never an uncaught exception from a
        # background thread.
        pass
    finally:
        try:
            stream.close()
        except OSError:
            pass


def run_pytest_check(
    repo_root: Path,
    check_reference: str,
    *,
    timeout_seconds: float = DEFAULT_CHECK_TIMEOUT_SECONDS,
    max_output_bytes: int = DEFAULT_CHECK_MAX_OUTPUT_BYTES,
) -> tuple[str, str | None, str]:
    """Runs `pytest <check_reference>` with `cwd=repo_root`, under
    `repo_root`'s own interpreter when it has a `.venv`. Returns
    `(outcome, invalid_reason, raw_output_text)` -- `outcome` is always
    one of `PASS`/`FAIL`/`INVALID` (`_classify_pytest_junit`, decisions/
    0082 §B), never derived from the bare exit code alone.
    `raw_output_text` is the combined stdout+stderr, captured verbatim
    for independent re-inspection (§5's `raw_output_ref`/
    `raw_output_sha256`).

    `PYTHONPATH` is explicitly set to `repo_root` itself, so the package
    actually imported is the one physically present under `repo_root` —
    never an ambient editable install elsewhere on `sys.path` pointing at
    a *different* checkout (confirmed necessary this session: Ledgerkit's
    own `pip install -e .` registers its real `~/projects/ledgerkit`, so
    without this, running against a disposable scratch copy would
    silently exercise the real checkout's own code instead of the
    scratch mutation under test — defeating the negative control
    entirely).

    A launch failure (the interpreter cannot be executed at all -- e.g.
    a broken symlink, a non-executable file, a permissions error) is
    itself an execution-environment failure, not a behavioural defect in
    the tested subject: it is caught and classified `INVALID` with the
    `OSError`'s own text preserved as diagnostic evidence, rather than
    propagating as an uncaught exception out of this function
    (decisions/0082 final corrective pass §C).

    **Phase 88 §5.3 additions**: `timeout_seconds` bounds the whole
    execution (a `subprocess.TimeoutExpired`-equivalent classifies
    `INVALID` with an explicit reason, the same controlled-finding
    pattern already used for a launch `OSError`); `max_output_bytes`
    bounds total captured stdout+stderr *while the process runs*, not
    after. On either breach, the subprocess is launched in its own
    process group (POSIX `start_new_session=True`) and the **whole
    group** is killed (`os.killpg`, `SIGKILL`) on breach -- not only the
    direct pytest child -- so a descendant process the tested code
    itself spawns (e.g. a hung worker) is also reaped, not left orphaned
    after this call returns. Named explicitly as a POSIX-only mechanism
    (this project's own stated platform, no Windows support claimed) and
    as addressing the common case, not a hermetic guarantee against
    every process-escape technique (e.g. a double-fork that detaches
    from its own group) -- a residual limitation disclosed here, not
    papered over."""
    interpreter = _interpreter_for(repo_root)
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(repo_root) + (f":{existing}" if existing else "")
    command = [interpreter, "-m", "pytest", "-q", "--junit-xml=<tmp>", check_reference]
    with tempfile.TemporaryDirectory() as tmp_dir:
        junit_path = Path(tmp_dir) / "junit.xml"
        real_command = [
            interpreter, "-m", "pytest", "-q", f"--junit-xml={junit_path}", check_reference
        ]
        try:
            proc = subprocess.Popen(
                real_command,
                cwd=repo_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                start_new_session=True,
            )
        except OSError as exc:
            raw = (
                f"$ {' '.join(command)}\n(cwd={repo_root})\n\n"
                f"could not launch the test interpreter: {exc}\n"
            )
            return (
                "INVALID",
                f"failed to launch pytest via {interpreter!r}: {exc} -- an "
                "execution-environment failure, not a behavioural result",
                raw,
            )

        captured: dict[str, list[str]] = {"stdout": [], "stderr": []}
        byte_counts: dict[str, int] = {"stdout": 0, "stderr": 0}
        cap_breached = threading.Event()
        readers = [
            threading.Thread(
                target=_read_bounded,
                args=(proc.stdout, "stdout", captured, byte_counts, max_output_bytes, cap_breached),
                daemon=True,
            ),
            threading.Thread(
                target=_read_bounded,
                args=(proc.stderr, "stderr", captured, byte_counts, max_output_bytes, cap_breached),
                daemon=True,
            ),
        ]
        for reader in readers:
            reader.start()

        timed_out = False
        deadline = time.monotonic() + timeout_seconds
        while True:
            remaining = deadline - time.monotonic()
            if cap_breached.wait(timeout=max(0.0, min(remaining, 0.5))):
                break
            if remaining <= 0:
                timed_out = proc.poll() is None
                break
            if proc.poll() is not None:
                break

        if timed_out or cap_breached.is_set():
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
        proc.wait()
        for reader in readers:
            reader.join(timeout=5)

        stdout_text = "".join(captured["stdout"])
        stderr_text = "".join(captured["stderr"])
        base_header = (
            f"$ {interpreter} -m pytest -q --junit-xml=<tmp> {check_reference}\n"
            f"(cwd={repo_root})\n\n--- stdout ---\n{stdout_text}\n--- stderr ---\n{stderr_text}\n"
        )

        if timed_out:
            raw = base_header + f"--- TERMINATED: exceeded {timeout_seconds}s timeout ---\n"
            return (
                "INVALID",
                f"pytest execution exceeded the configured timeout of {timeout_seconds}s "
                "-- the whole process group was terminated; see raw output",
                raw,
            )
        if cap_breached.is_set():
            raw = base_header + f"--- TERMINATED: output exceeded {max_output_bytes}-byte cap ---\n"
            return (
                "INVALID",
                f"raw output exceeded the configured cap of {max_output_bytes} bytes; "
                "execution terminated early",
                raw,
            )

        outcome, invalid_reason = _classify_pytest_junit(junit_path, proc.returncode)
    raw = base_header + f"--- returncode: {proc.returncode} ---\n"
    return outcome, invalid_reason, raw


def evaluate_check(
    contract: OracleContract,
    check: OracleCheck,
    *,
    contract_path: Path,
    repo_root: Path,
    raw_output_dir: Path,
    baseline_id: str | None = None,
    environment_descriptor: str | None = None,
    timeout_seconds: float = DEFAULT_CHECK_TIMEOUT_SECONDS,
    max_output_bytes: int = DEFAULT_CHECK_MAX_OUTPUT_BYTES,
) -> OracleResult:
    """Executes `check` against `repo_root` (a real Ledgerkit checkout —
    the sibling project this phase's one pinned contract targets, never
    the live ~/projects/ledgerkit itself for a negative-control run) and
    returns a fully-populated `OracleResult`. A digest that cannot be
    computed (a named path missing) produces `outcome: INVALID` with a
    named `invalid_reason` — never a partial-file-set digest presented as
    complete (`decisions/0081` §4)."""
    run_id = f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')}-{uuid.uuid4().hex[:8]}"
    oracle_contract_content_hash = sha256_file(contract_path)
    executed_at = datetime.now(UTC).isoformat()

    # Immutable per-run naming (decisions/0082 §C): run_id is already
    # guaranteed unique, so a later run of the same check never
    # overwrites an earlier run's own result/raw-output file.
    raw_output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_output_dir / f"{check.check_id}--{run_id}.txt"

    try:
        tested_subject_digest = compute_tree_digest(repo_root, contract.tested_paths)
        test_input_digest = compute_tree_digest(repo_root, check.test_input_paths)
    except OracleDigestError as exc:
        raw_text = f"digest computation failed: {exc}\n"
        raw_path.write_text(raw_text, encoding="utf-8")
        return OracleResult(
            schema_version=_SCHEMA_VERSION,
            run_id=run_id,
            contract_id=contract.contract_id,
            check_id=check.check_id,
            scope=check.scope,
            baseline_id=baseline_id,
            tested_subject_digest="",
            oracle_contract_id=contract.contract_id,
            oracle_contract_content_hash=oracle_contract_content_hash,
            test_input_digest="",
            raw_output_ref=str(raw_path),
            raw_output_sha256=sha256_text(raw_text),
            outcome="INVALID",
            executed_at=executed_at,
            execution_provider=check.execution_provider,
            environment_descriptor=environment_descriptor,
            invalid_reason=str(exc),
        )

    if check.execution_provider != "pytest":
        raise OracleSchemaError(
            f"unsupported execution_provider {check.execution_provider!r} — "
            "Phase 82 implements exactly 'pytest' (decisions/0081 §1)"
        )
    outcome, invalid_reason, raw_text = run_pytest_check(
        repo_root, check.check_reference,
        timeout_seconds=timeout_seconds, max_output_bytes=max_output_bytes,
    )
    raw_path.write_text(raw_text, encoding="utf-8")

    return OracleResult(
        schema_version=_SCHEMA_VERSION,
        run_id=run_id,
        contract_id=contract.contract_id,
        check_id=check.check_id,
        scope=check.scope,
        baseline_id=baseline_id,
        tested_subject_digest=tested_subject_digest,
        oracle_contract_id=contract.contract_id,
        oracle_contract_content_hash=oracle_contract_content_hash,
        test_input_digest=test_input_digest,
        raw_output_ref=str(raw_path),
        raw_output_sha256=sha256_file(raw_path),
        outcome=outcome,
        executed_at=executed_at,
        execution_provider=check.execution_provider,
        environment_descriptor=environment_descriptor,
        invalid_reason=invalid_reason,
    )


# ---------------------------------------------------------------------------
# Baseline acceptance (§7) -- an explicit, separately-logged action; never
# minted automatically by evaluate_check/run_pytest_check (CLAUDE.md §1
# L-087: observing a change differs from acting on it).
# ---------------------------------------------------------------------------


def compute_baseline_id(tested_subject_revision: str, oracle_contract_content_hash: str) -> str:
    return sha256_text(f"{tested_subject_revision}\n{oracle_contract_content_hash}\n")


@dataclass
class BaselineAcceptance:
    baseline_id: str
    tested_subject_revision: str
    oracle_contract_content_hash: str
    accepted_at: str
    accepted_by: str


def accept_baseline(
    path: Path,
    *,
    tested_subject_revision: str,
    oracle_contract_content_hash: str,
    accepted_by: str,
) -> BaselineAcceptance:
    """The one explicit acceptance action that may ever create or advance
    a baseline — never called automatically by `evaluate_check`."""
    acceptance = BaselineAcceptance(
        baseline_id=compute_baseline_id(tested_subject_revision, oracle_contract_content_hash),
        tested_subject_revision=tested_subject_revision,
        oracle_contract_content_hash=oracle_contract_content_hash,
        accepted_at=datetime.now(UTC).isoformat(),
        accepted_by=accepted_by,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            {
                "baseline_id": acceptance.baseline_id,
                "tested_subject_revision": acceptance.tested_subject_revision,
                "oracle_contract_content_hash": acceptance.oracle_contract_content_hash,
                "accepted_at": acceptance.accepted_at,
                "accepted_by": acceptance.accepted_by,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return acceptance


# ---------------------------------------------------------------------------
# Precedence and aggregation (§5a, decisions/0081 §2)
# ---------------------------------------------------------------------------


def evaluate_result_precedence(
    result: OracleResult,
    contract: OracleContract,
    check: OracleCheck,
    *,
    contract_path: Path,
    repo_root: Path | None = None,
) -> tuple[str, str | None]:
    """The fixed, three-rule precedence order (§5a): returns
    `(effective_outcome, reason)` where `effective_outcome` is always one
    of `PASS`/`FAIL`/`INVALID` — this function, not a stored field, is the
    single source of truth for whether a given result actually counts.
    `repo_root`, when given, re-executes the digest recomputation against
    a live checkout; when omitted (the checkout isn't available in this
    environment), only the contract/scope/raw-output checks run and the
    tested-subject/test-input digests are trusted as recorded — callers
    needing the full guarantee must supply `repo_root`."""
    live_contract_hash = sha256_file(contract_path)
    if result.oracle_contract_content_hash != live_contract_hash:
        return "INVALID", (
            "oracle_contract_content_hash does not match the live "
            f"oracle-contract.yaml ({contract_path})"
        )
    id_mismatch = (
        result.contract_id != contract.contract_id
        or result.oracle_contract_id != contract.contract_id
    )
    if id_mismatch:
        return "INVALID", "contract_id/oracle_contract_id does not match the live contract_id"

    if repo_root is not None:
        try:
            live_tested = compute_tree_digest(repo_root, contract.tested_paths)
        except OracleDigestError as exc:
            return "INVALID", f"tested_subject_digest could not be recomputed: {exc}"
        if result.tested_subject_digest != live_tested:
            return "INVALID", (
                "tested_subject_digest does not match the current implementation "
                "-- a modified or stale candidate is not covered by this result"
            )
        try:
            live_input = compute_tree_digest(repo_root, check.test_input_paths)
        except OracleDigestError as exc:
            return "INVALID", f"test_input_digest could not be recomputed: {exc}"
        if result.test_input_digest != live_input:
            return "INVALID", (
                "test_input_digest does not match the current fixture/test files"
            )

    raw_path = Path(result.raw_output_ref)
    if not raw_path.is_file():
        return "INVALID", f"raw_output_ref {result.raw_output_ref!r} does not exist"
    if sha256_file(raw_path) != result.raw_output_sha256:
        return "INVALID", (
            f"raw_output_ref {result.raw_output_ref!r} content does not match "
            "its own recorded raw_output_sha256 -- tampered or corrupted"
        )

    if result.scope != check.scope:
        return "INVALID", (
            f"result scope {result.scope!r} does not match check "
            f"{check.check_id!r}'s own scope {check.scope!r}"
        )

    return result.outcome, result.invalid_reason


@dataclass
class CheckAggregate:
    check_id: str
    scope: str
    required: bool
    state: str  # "PASS" | "GAP" | "NOT_REQUIRED"
    passing_result: OracleResult | None
    observed_outcomes: list[str] = field(default_factory=list)


def aggregate_contract(
    contract: OracleContract,
    results: list[OracleResult],
    *,
    contract_path: Path,
    repo_root: Path | None = None,
) -> list[CheckAggregate]:
    """Per-`(contract_id, check_id)` aggregation (§5a): `GAP` is computed
    here, never read from any result's own field. A `FAIL`/`INVALID`
    result is retained in `observed_outcomes` even when a later `PASS`
    exists for the same check — it is never erased by the aggregate
    state."""
    aggregates: list[CheckAggregate] = []
    for check in contract.checks:
        check_results = [r for r in results if r.check_id == check.check_id]
        observed: list[str] = []
        passing: OracleResult | None = None
        for r in check_results:
            outcome, _reason = evaluate_result_precedence(
                r, contract, check, contract_path=contract_path, repo_root=repo_root
            )
            observed.append(outcome)
            if outcome == "PASS" and passing is None:
                passing = r
        if passing is not None:
            state = "PASS"
        elif check.required:
            state = "GAP"
        else:
            state = "NOT_REQUIRED"
        aggregates.append(
            CheckAggregate(
                check_id=check.check_id,
                scope=check.scope,
                required=check.required,
                state=state,
                passing_result=passing,
                observed_outcomes=observed,
            )
        )
    return aggregates
