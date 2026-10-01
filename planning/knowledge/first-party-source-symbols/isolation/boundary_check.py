"""Mechanical boundary-check: scans a dispatch's real, original JSONL
transcript for every Read/Glob/Grep tool_use's target path and every
Bash tool_use's command text, and reports any absolute path referenced
that falls outside the dispatch's own assigned export directory.

This is derived from the ORIGINAL subagent transcript files still
present on disk under ~/.claude/projects/.../subagents/ -- not a rerun,
not a self-report. Genuine mechanical evidence of what was actually
accessed.
"""
import json
import re
import sys
from pathlib import Path

SUBAGENTS = Path(
    "/home/cormac/.claude/projects/-home-cormac-projects-codecompass/"
    "0b2afcc0-cb03-48e4-8480-bf16722dc977/subagents"
)

PATH_RE = re.compile(r"/tmp/claude-1000/[^\s\"'\\)]+|/home/cormac/[^\s\"'\\)]+")


def analyze(agent_id: str, assigned_dir: str, label: str) -> None:
    path = SUBAGENTS / f"agent-{agent_id}.jsonl"
    print(f"\n=== {label} ({agent_id}) ===")
    print(f"Assigned directory: {assigned_dir}")
    if not path.is_file():
        print("TRANSCRIPT MISSING -- cannot verify.")
        return

    tool_calls = []
    with path.open() as f:
        for line in f:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") != "assistant":
                continue
            for c in obj.get("message", {}).get("content", []):
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    tool_calls.append(c)

    read_count = sum(1 for c in tool_calls if c["name"] in ("Read", "Glob", "Grep"))
    bash_count = sum(1 for c in tool_calls if c["name"] == "Bash")
    write_count = sum(1 for c in tool_calls if c["name"] in ("Write", "Edit"))
    print(f"Tool calls: {len(tool_calls)} total ({read_count} Read/Glob/Grep, "
          f"{bash_count} Bash, {write_count} Write/Edit)")

    out_of_scope = []
    for c in tool_calls:
        name = c["name"]
        inp = c.get("input", {})
        if name in ("Read", "Glob"):
            target = inp.get("file_path") or inp.get("path") or inp.get("pattern", "")
            if target.startswith("/") and assigned_dir not in target:
                out_of_scope.append((name, target))
        elif name == "Grep":
            target = inp.get("path", "")
            if target.startswith("/") and assigned_dir not in target:
                out_of_scope.append((name, target))
        elif name == "Bash":
            command = inp.get("command", "")
            for m in PATH_RE.finditer(command):
                p = m.group(0)
                if assigned_dir not in p and "/scratchpad/" in p:
                    # Another scratchpad path (e.g. a sandbox the agent
                    # built itself to run tests) -- not necessarily a
                    # violation, flag separately for manual read.
                    out_of_scope.append((f"{name} (scratch, own sandbox?)", p))
                elif assigned_dir not in p and "/scratchpad/" not in p:
                    out_of_scope.append((name, p))

    if out_of_scope:
        print(f"Paths referenced outside {assigned_dir}:")
        seen = set()
        for kind, p in out_of_scope:
            key = (kind, p)
            if key in seen:
                continue
            seen.add(key)
            print(f"  [{kind}] {p}")
    else:
        print("No path outside the assigned directory was referenced by any "
              "Read/Glob/Grep/Bash tool call.")


if __name__ == "__main__":
    analyze(
        "aeb8e7f6db41e0547",
        "/tmp/claude-1000/-home-cormac-projects-codecompass/0b2afcc0-cb03-48e4-8480-bf16722dc977/scratchpad/phase79-understanding-export",
        "Understanding reconstruction (context-researcher)",
    )
    analyze(
        "ad03cd2cd0213f19e",
        "/tmp/claude-1000/-home-cormac-projects-codecompass/0b2afcc0-cb03-48e4-8480-bf16722dc977/scratchpad/phase79-implementation-export",
        "Implementation reconstruction, pass 1 (general-purpose)",
    )
    analyze(
        "a24159175726b88a7",
        "/tmp/claude-1000/-home-cormac-projects-codecompass/0b2afcc0-cb03-48e4-8480-bf16722dc977/scratchpad/phase79-implementation-export",
        "Implementation reconstruction, pass 2 / re-run",
    )
    analyze(
        "a1d1d1a9168a90fb7",
        "/tmp/claude-1000/-home-cormac-projects-codecompass/0b2afcc0-cb03-48e4-8480-bf16722dc977/scratchpad/phase79-docs-export",
        "Documentation draft (docs-reconstructor)",
    )
