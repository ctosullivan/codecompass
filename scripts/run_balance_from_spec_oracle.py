"""Maintainer-only script: executes Phase 82's one real oracle contract
(`planning/contracts/balance-from-spec/oracle-contract.yaml`) against a
real Ledgerkit checkout and writes the resulting `oracle-result.yaml`
files (and their raw pytest output) into
`planning/contracts/balance-from-spec/results/`.

This is the "manual/scripted pytest invocation" the Phase 82 plan
explicitly scopes this phase to (§1's own deferred-scope list: "any
actual execution-provider integration beyond a manual/scripted pytest
invocation... is Phase 83/84 territory") — a maintainer-run script, like
`scripts/prepare_cleanroom_branch.py`, not a shipped `codecompass`
command.

    python scripts/run_balance_from_spec_oracle.py [--ledgerkit-root PATH]

Overwrites the committed result files in place — each run represents
"the current accepted result for this check" (one file per check_id, not
one file per run; `run_id` inside each file is still unique per
execution). Never mints or advances a baseline (`CLAUDE.md` §1 L-087) —
that is `scripts/accept_balance_from_spec_baseline.py`'s own, separate,
explicit action.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLUG_DIR = ROOT / "planning" / "contracts" / "balance-from-spec"
DEFAULT_LEDGERKIT_ROOT = Path.home() / "projects" / "ledgerkit"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledgerkit-root", type=Path, default=DEFAULT_LEDGERKIT_ROOT)
    parser.add_argument("--baseline-id", default=None, help="nullable -- see CLAUDE.md L-087")
    args = parser.parse_args()

    src_path = ROOT / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from codecompass import oracle

    contract_path = SLUG_DIR / "oracle-contract.yaml"
    contract = oracle.parse_oracle_contract(contract_path)
    results_dir = SLUG_DIR / "results"
    # Relative to ROOT (not absolute) so a committed oracle-result.yaml's
    # own raw_output_ref is portable across checkouts/machines.
    raw_dir = results_dir.relative_to(ROOT) / "raw"

    import os

    os.chdir(ROOT)
    for check in contract.checks:
        result = oracle.evaluate_check(
            contract,
            check,
            contract_path=contract_path,
            repo_root=args.ledgerkit_root,
            raw_output_dir=raw_dir,
            baseline_id=args.baseline_id,
        )
        out_path = results_dir / f"{check.check_id}.yaml"
        oracle.write_oracle_result(out_path, result)
        print(f"{check.check_id}: {result.outcome} -> {out_path.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
