#!/usr/bin/env python3
"""Phase 81B Amendment 4 -- runs INSIDE the clean-room sandbox.

Reads only the sandbox's own already-isolated, allow-listed, .git-free
mounted evidence tree (never anything else, since nothing else exists
in this process's own mount namespace), assembles one complete prompt
from it, and calls the broker (via cleanroom_broker_client.py, the only
other thing bind-mounted into this sandbox besides the one socket) to
get a single model response.

This script is mechanical glue, not "the AI" -- it does not reason about
the evidence, it only concatenates it. The actual reasoning happens
inside the model response the broker returns. Running the assembly step
itself inside the sandbox (rather than on the trusted host) matters:
the orchestrator must never be the one deciding what the writer "sees",
beyond the allow-list/exclusion rules already baked into the handoff
package it was given.

Usage: cleanroom_prompt_assembler.py <role> <evidence-root> <broker-socket>
  role: "cold-reader" or "writer"
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cleanroom_broker_client as client  # noqa: E402

# A real cold-reader finding (Phase 81B Amendment 4): a fixed suffix
# allow-list here silently dropped real evidence content the writer
# needed (.hs Haskell source, .cabal/.lock build files, .gitmodules) the
# moment prepare_cleanroom_branch.py's own ALLOW_PATHS grew to cover new
# file types -- the two lists drifted independently with nothing to keep
# them in sync. Every allow-listed file is a real decision already made
# by ALLOW_PATHS; this script's only remaining job is deciding whether
# that file's own bytes are safely representable as text in the prompt,
# which decoding itself answers directly -- no separate, parallel
# extension list to maintain and forget to update.
_SKIP_DIR_NAMES = {"__pycache__", ".pytest_cache", ".ruff_cache", ".stack-work"}
_SKIP_BASENAMES = {".DS_Store"}

_COLD_READER_SYSTEM_PROMPT = """\
You are a cold-reader evaluating a documentation handoff package for a
software project called CodeCompass. You have never seen this project
before. You are NOT writing documentation. Your only job: determine
whether the supplied intermediary knowledge and source evidence are
SUFFICIENT for a different, equally-fresh writer (with no other
context) to reconstruct complete, accurate project documentation from
it alone.

Be concrete and specific. If something is unclear, ambiguous, missing,
or unverifiable from what you were given, name exactly what it is and
where you expected to find it. Do not invent facts to fill a gap you
find -- a gap is a reportable finding, not something to guess past.

Respond in exactly this format:
VERDICT: SUFFICIENT or GAPS FOUND
If GAPS FOUND, follow with a numbered list of specific, concrete gaps.
"""

_WRITER_SYSTEM_PROMPT = """\
You are a documentation-writing agent for a software project called
CodeCompass. You have never seen this project before and have no
access to anything beyond what is supplied to you in this one request.
Using ONLY that evidence, write complete, accurate, current
documentation for CodeCompass.

Do not reference, assume, or reconstruct anything not supplied to you.
Do not fabricate a fact to fill a gap -- if something is genuinely
unclear from your evidence, say so explicitly in an "Open questions"
section rather than guessing.

Output your complete work as a sequence of files, each one delimited
exactly like this:

=== FILE: <relative/path.md> ===
<complete file content>
=== END FILE ===

Produce as many files as needed for complete coverage (a root
README.md plus a docs/ tree). Adapt structure to your own findings
rather than mechanically filling a fixed template.
"""


def _iter_evidence_files(root: Path):
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part in _SKIP_DIR_NAMES for part in p.parts):
            continue
        if p.name in _SKIP_BASENAMES:
            continue
        yield p


def assemble_evidence_blob(evidence_root: Path) -> str:
    root = evidence_root.resolve()
    parts = []
    for p in _iter_evidence_files(root):
        rel = p.relative_to(root)
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as exc:
            print(
                f"cleanroom_prompt_assembler: skipping non-text evidence file {rel}: {exc}",
                file=sys.stderr,
            )
            continue
        parts.append(f"=== EVIDENCE FILE: {rel} ===\n{text}\n")
    return "\n".join(parts)


_REVISE_SYSTEM_PROMPT = """\
You are a documentation-writing agent for a software project called
CodeCompass, continuing a prior clean-room documentation effort. You
have never seen this project before beyond what is supplied to you in
this one request -- you do not have access to any other conversation,
including whatever earlier draft produced the current state of these
docs.

You are asked to verify and, where necessary, revise specific existing
documentation files so they fully cover a short list of specific,
independently-verified facts. Each fact is given with its own exact
source location in your workspace -- verify it yourself by reading that
location, exactly as you would verify anything else, before adding it.
Do not take the fact list on faith; confirm each one against the cited
source first.

Output ONLY the files that genuinely need a change, each one complete
(not a diff/patch), delimited exactly like this:

=== FILE: <relative/path.md> ===
<complete, revised file content>
=== END FILE ===

If a named file already fully covers its assigned fact, do not include
it in your output at all -- do not restate a file that needs no change.
"""


def main(argv: list[str]) -> int:
    if len(argv) not in (4, 5):
        print(
            f"usage: {argv[0]} <cold-reader|writer|revise> <evidence-root> <broker-socket> "
            "[revision-instructions-file]",
            file=sys.stderr,
        )
        return 2
    role, evidence_root_str, socket_path = argv[1], argv[2], argv[3]
    if role not in ("cold-reader", "writer", "revise"):
        print(f"unknown role: {role!r}", file=sys.stderr)
        return 2

    evidence_root = Path(evidence_root_str)
    blob = assemble_evidence_blob(evidence_root)

    if role == "cold-reader":
        system_prompt = _COLD_READER_SYSTEM_PROMPT
        instruction = (
            "Here is the complete clean-room handoff package and allow-listed source/test "
            "evidence. Evaluate its sufficiency per your instructions."
        )
    elif role == "writer":
        system_prompt = _WRITER_SYSTEM_PROMPT
        instruction = (
            "Here is the complete clean-room handoff package and allow-listed source/test "
            "evidence. Write the complete documentation per your instructions."
        )
    else:
        system_prompt = _REVISE_SYSTEM_PROMPT
        if len(argv) != 5:
            print("revise mode requires a revision-instructions-file argument", file=sys.stderr)
            return 2
        revision_instructions = Path(argv[4]).read_text(encoding="utf-8")
        instruction = (
            "Here is the complete clean-room handoff package and allow-listed source/test "
            "evidence, followed by the specific facts to verify and incorporate:\n\n"
            + revision_instructions
        )

    full_prompt = f"{instruction}\n\n{blob}"
    result = client.call(
        socket_path,
        system_prompt=system_prompt,
        messages=[{"role": "user", "content": full_prompt}],
    )
    if not result.get("ok"):
        print(f"BROKER ERROR: {result.get('error')}", file=sys.stderr)
        return 1
    print(result["output"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
