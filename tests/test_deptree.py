from depcompass.core import DepNode
from depcompass.deptree import render_deptree_json, render_deptree_markdown


def _diamond_tree() -> DepNode:
    a = DepNode(name="a", version="1.0.0", children=[DepNode(name="lodash", version="4.17.21")])
    b = DepNode(name="b", version="1.0.0", children=[DepNode(name="lodash", version="4.17.21")])
    return DepNode(name="root", version="1.0.0", children=[a, b])


def test_render_deptree_markdown_dedups_diamond_dependency() -> None:
    lines = render_deptree_markdown(_diamond_tree()).splitlines()

    assert "- root@1.0.0" in lines
    assert "  - a@1.0.0" in lines
    assert "  - b@1.0.0" in lines
    assert "    - lodash@4.17.21" in lines  # first occurrence, fully rendered
    assert "    - lodash@4.17.21 (see lodash@4.17.21 above)" in lines  # back-reference
    # Only one occurrence is a full re-expansion (there's nothing to
    # expand into for a leaf, but the back-reference text must be present
    # exactly once, not twice).
    assert lines.count("    - lodash@4.17.21 (see lodash@4.17.21 above)") == 1


def test_render_deptree_json_dedups_diamond_dependency_with_ref_marker() -> None:
    data = render_deptree_json(_diamond_tree())

    a_child = data["children"][0]["children"][0]
    b_child = data["children"][1]["children"][0]
    assert a_child == {"name": "lodash", "version": "4.17.21", "children": []}
    assert b_child == {"ref": "lodash@4.17.21"}


def test_dev_only_children_collapse_to_count() -> None:
    root = DepNode(
        name="root",
        version="1.0.0",
        children=[
            DepNode(name="lodash", version="4.17.21"),
            DepNode(name="jest", version="1.0.0", dev_only=True),
            DepNode(name="mocha", version="1.0.0", dev_only=True),
        ],
    )
    lines = render_deptree_markdown(root).splitlines()

    assert "  - lodash@4.17.21" in lines
    assert "  - 2 dev-only dependencies (not shown)" in lines
    assert not any("jest" in line for line in lines)
    assert not any("mocha" in line for line in lines)


def test_dev_only_json_uses_count_not_enumeration() -> None:
    root = DepNode(
        name="root",
        version="1.0.0",
        children=[
            DepNode(name="lodash", version="4.17.21"),
            DepNode(name="jest", version="1.0.0", dev_only=True),
        ],
    )
    data = render_deptree_json(root)

    assert data["dev_only_count"] == 1
    assert len(data["children"]) == 1
    assert data["children"][0]["name"] == "lodash"


def _chain(depth: int) -> DepNode:
    """root -> c1 -> c2 -> ... -> c{depth}, a straight-line chain."""
    leaf = DepNode(name=f"c{depth}", version="1.0.0")
    node = leaf
    for level in range(depth - 1, 0, -1):
        node = DepNode(name=f"c{level}", version="1.0.0", children=[node])
    return DepNode(name="root", version="1.0.0", children=[node])


def test_deep_chain_produces_explicit_collapse_notice_not_silent_truncation() -> None:
    tree = _chain(depth=4)  # root -> c1 -> c2 -> c3 -> c4
    markdown = render_deptree_markdown(tree, max_depth=2)

    assert "truncated at depth 2" in markdown
    assert "deptree.json" in markdown
    assert "c3" not in markdown
    assert "c4" not in markdown


def test_deep_chain_json_marks_truncated() -> None:
    tree = _chain(depth=4)
    data = render_deptree_json(tree, max_depth=2)

    # root(0) -> c1(1) -> c2(2, at cap, has children -> truncated)
    c2 = data["children"][0]["children"][0]
    assert c2["truncated"] is True
    assert "children" not in c2


def test_leaf_at_max_depth_is_not_marked_truncated() -> None:
    tree = _chain(depth=1)  # root -> c1 (leaf)
    data = render_deptree_json(tree, max_depth=1)

    c1 = data["children"][0]
    assert c1["truncated"] is False
