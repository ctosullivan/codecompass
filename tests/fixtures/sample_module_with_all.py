"""Sample module for testing static API-surface extraction via ast."""

__all__ = ["greet", "Greeter"]


def greet(name: str) -> str:
    """Return a friendly greeting."""
    return f"Hello, {name}!"


class Greeter:
    """Greets people repeatedly."""

    def __init__(self, name: str) -> None:
        self.name = name
