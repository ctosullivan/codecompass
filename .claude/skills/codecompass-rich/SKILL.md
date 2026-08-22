---
name: codecompass-rich
description: >-
  API questions, known gotchas, and internals for rich (python), pinned to the installed version. Rich makes it super easy to create beautiful, colored, formatted output in the terminal. Instead of struggling with ANSI codes or terminal quirks, you create a `Console` object and call `.print()` with markup tags (like `[bold red]text[/bold red]`) to style your output. It handles all the terminal compatibility stuff for you. You can also render tables, markdown documents, syntax-highlighted code,
---

# rich

Grounded description of the installed `rich` (15.0.0), retrieved from its own upstream repository — not from training knowledge. See `vendor/rich/CLAUDE.md` for the full per-vendor digest.

Rich is a Python library for rendering rich text and beautiful formatting to the terminal. Based on the retrieved material, the core `Console` class (from `rich.console.Console` as documented in README.cn.md) is the main interface for outputting styled text with support for colors, emphasis, and markup similar to BBCode syntax. The library exports a `Markdown` class (from `rich.markdown.Markdown`) for rendering markdown content to the terminal. The `Table` class enables creation of formatted tables with configurable borders, styles, and cell alignment. The library also provides a `Prompt` class for interactive terminal input (referenced in the exports). These renderables follow a Console Protocol that allows custom implementations. Additional components include logging handlers, progress bars, status animations, tree rendering, and syntax highlighting via Pygments integration. The library automatically handles terminal width, text wrapping, and color/emoji support across platforms.

**Worth reading next:** `rich\__init__.py` — This file shows the main public API exports including `get_console()`, `print()`, and `inspect()` functions, demonstrating how Console is initialized and used as the central interface

## References

- [references/FILETREE.md](./references/FILETREE.md)
- [references/DEPTREE.md](./references/DEPTREE.md)
