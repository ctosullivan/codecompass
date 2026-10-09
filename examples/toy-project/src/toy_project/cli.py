"""A tiny CLI that fetches a URL and prints its status — real usage of
both of this toy project's dependencies, so codecompass's usage-driven
enrichment has something genuine to detect.
"""

from __future__ import annotations

import click
import requests


@click.command()
@click.argument("url")
def fetch(url: str) -> None:
    """Fetch URL and print its HTTP status code."""
    response = requests.get(url, timeout=10)
    click.echo(f"{url} -> {response.status_code}")


if __name__ == "__main__":
    fetch()
