"""Deterministic DEPTREE.md (+ deptree.json) rendering from DepNode trees.

No AI calls, runs regardless of `depth`. See architecture/overview.md's
"Tree generation" section and planning/phase-3-tree-generation.md.
"""

from __future__ import annotations

from codecompass.core import DepNode

_DEPTREE_MAX_DEPTH = 20


def render_deptree_markdown(root: DepNode, *, max_depth: int = _DEPTREE_MAX_DEPTH) -> str:
    """Diamond-dependency dedup (repeat `name@version` nodes render a
    back-reference instead of a re-expanded subtree), dev-only children
    always collapsed to a count, and an explicit collapse notice — never
    silent truncation — once `max_depth` is exceeded.
    """
    lines: list[str] = []
    _render_node(root, depth=0, max_depth=max_depth, seen=set(), lines=lines)
    return "\n".join(lines)


def render_deptree_json(root: DepNode, *, max_depth: int = _DEPTREE_MAX_DEPTH) -> dict:
    """Mirrors `render_deptree_markdown`'s deduplicated, depth-capped
    shape — a repeat `name@version` node becomes `{"ref": "name@version"}`
    rather than a re-expanded subtree — instead of the adapter's full raw
    tree. See planning/phase-3-tree-generation.md's Design decisions.
    """
    return _node_to_dict(root, depth=0, max_depth=max_depth, seen=set())


def _key(node: DepNode) -> str:
    return f"{node.name}@{node.version}"


def _split_children(node: DepNode) -> tuple[list[DepNode], int]:
    normal = [c for c in node.children if not c.dev_only]
    dev_count = sum(1 for c in node.children if c.dev_only)
    return normal, dev_count


def _render_node(
    node: DepNode, *, depth: int, max_depth: int, seen: set[str], lines: list[str]
) -> None:
    indent = "  " * depth
    key = _key(node)
    if depth > 0 and key in seen:
        lines.append(f"{indent}- {key} (see {key} above)")
        return
    seen.add(key)
    lines.append(f"{indent}- {key}")

    if depth >= max_depth:
        if node.children:
            lines.append(
                f"{indent}  ... (truncated at depth {max_depth} — "
                "see deptree.json for the full tree)"
            )
        return

    normal_children, dev_count = _split_children(node)
    for child in normal_children:
        _render_node(child, depth=depth + 1, max_depth=max_depth, seen=seen, lines=lines)
    if dev_count:
        child_indent = "  " * (depth + 1)
        lines.append(f"{child_indent}- {dev_count} dev-only dependencies (not shown)")


def _node_to_dict(node: DepNode, *, depth: int, max_depth: int, seen: set[str]) -> dict:
    key = _key(node)
    if depth > 0 and key in seen:
        return {"ref": key}
    seen.add(key)

    result: dict = {"name": node.name, "version": node.version}
    if depth >= max_depth:
        result["truncated"] = bool(node.children)
        return result

    normal_children, dev_count = _split_children(node)
    result["children"] = [
        _node_to_dict(c, depth=depth + 1, max_depth=max_depth, seen=seen)
        for c in normal_children
    ]
    if dev_count:
        result["dev_only_count"] = dev_count
    return result
