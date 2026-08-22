---
name: codecompass-typer
description: >-
  API questions, known gotchas, and internals for typer (python), pinned to the installed version. Typer is a framework for building command-line applications using plain Python type hints. Instead of writing decorators or configuration files, you just write functions with type-annotated parameters and Typer automatically generates a full CLI from them with help text, validation, and tab completion. You can create simple single-command apps with `typer.run(my_function)` or complex multi-command
---

# typer

Grounded description of the installed `typer` (0.27.1), retrieved from its own upstream repository — not from training knowledge. See `vendor/typer/CLAUDE.md` for the full per-vendor digest.

Typer is a library for building CLI applications using Python type hints. According to `typer/__init__.py`, the core `Typer` class from `main` serves as the app container. The library exports `Argument` and `Option` from `params` for declaring CLI parameters. The main entry point is `run()` and `launch()` from `main`. For testing CLI applications, the material references `CliRunner` which is used to invoke and test CLI applications (mentioned in used symbols but not detailed in the provided files). The SDK also exports error handling via `Abort`, `BadParameter`, and `Exit` from vendored Click (`_click.exceptions`), plus terminal utilities like `prompt()`, `confirm()`, `progressbar()`, `echo()`, and `secho()` from Click's termui module. The library is built on top of vendored Click 8.3.1 code (as noted in alternatives.md) with Typer adding a Python-type-hints layer on top. Context and callback model types are available from `models`.

**Worth reading next:** `typer\__init__.py` — This file exports the core Typer API including the `Typer` class, `run()` function, `Argument` and `Option` parameter types, and terminal utilities like `prompt()`, demonstrating the main interfaces for building CLI applications

## References

- [references/FILETREE.md](./references/FILETREE.md)
- [references/DEPTREE.md](./references/DEPTREE.md)
