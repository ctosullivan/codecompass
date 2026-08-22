---
name: codecompass-typer
description: >-
  API questions, known gotchas, and internals for typer (python), pinned to the installed version. Typer makes it really easy to build professional CLI tools using just Python type hints. You define a function, add type annotations to its parameters, decorate it with `@app.command()`, and Typer automatically generates a CLI with help text, argument validation, and even shell completion. It's inspired by FastAPI but for command-line apps instead of web APIs. Under the hood it uses Click, which T
---

# typer

Grounded description of the installed `typer` (0.27.1), retrieved from its own upstream repository — not from training knowledge. See `vendor/typer/CLAUDE.md` for the full per-vendor digest.

Typer is a CLI framework for building command-line applications using Python type hints. It is built on top of Click (which Typer has vendored internally since version 0.26.0, as noted in README.md) and provides a decorator-based API for defining CLI commands. The core `Typer` class (from `typer/main.py` and exported in `typer/__init__.py`) acts as an app factory that you decorate functions with via `@app.command()`. Core parameter types include `Argument` (positional parameters from `typer/params.py`) and `Option` (named parameters with `--` prefix). The `Context` class (from `typer/models.py`) provides access to the current command context. The `confirm` function (from `typer/_click/termui.py`) provides user prompts for yes/no questions. `CliRunner` (not shown in the explicit exports but used for testing) is Click's testing utility for simulating CLI invocations. The `Exit` exception (from `typer/_click/exceptions.py`) can be raised to exit the program with a specific code.

**Worth reading next:** `typer/__init__.py` — This file exports all the public API of Typer including the main `Typer` class, parameter types like `Argument` and `Option`, testing utilities, and utilities imported from the vendored Click library.

## References

- [references/FILETREE.md](./references/FILETREE.md)
- [references/DEPTREE.md](./references/DEPTREE.md)
