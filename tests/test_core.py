import pytest

from depcompass.core import DepNode, Depth, Ecosystem, VendorConfig, VendorDigest


def test_vendor_config_full_needs_no_companion_field() -> None:
    config = VendorConfig(name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.FULL)
    assert config.depth is Depth.FULL


def test_vendor_config_is_frozen() -> None:
    config = VendorConfig(name="lodash", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)
    with pytest.raises(AttributeError):
        config.name = "not-lodash"  # type: ignore[misc]


def test_depnode_default_children_are_independent_lists() -> None:
    a = DepNode(name="a", version="1.0.0")
    b = DepNode(name="b", version="2.0.0")
    a.children.append(b)
    assert a.children == [b]
    assert DepNode(name="c", version="3.0.0").children == []


def test_depnode_nested_tree() -> None:
    leaf = DepNode(name="leaf", version="1.0.0")
    root = DepNode(name="root", version="2.0.0", children=[leaf])
    assert root.children[0].name == "leaf"


def test_vendor_digest_default_side_effects_are_independent_lists() -> None:
    config = VendorConfig(name="lodash", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)
    a = VendorDigest(config=config, installed_version="4.17.21")
    a.side_effects.append("postinstall script")
    assert VendorDigest(config=config, installed_version="4.17.21").side_effects == []


def test_vendor_digest_description_fields_default_to_none() -> None:
    config = VendorConfig(name="lodash", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)
    digest = VendorDigest(config=config, installed_version="4.17.21")
    assert digest.technical_description is None
    assert digest.conversational_overview is None
    assert digest.description_error is None
