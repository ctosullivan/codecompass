---
name: codecompass-anthropic
description: >-
  API questions, known gotchas, and internals for anthropic (python), pinned to the installed version. This is Anthropic's official Python SDK for talking to the Claude API. You create an `Anthropic` client, configure it with your API key, and then call methods like `messages.create()` to send prompts to Claude and get responses back. It handles all the HTTP communication and gives you nice error types when things go wrong. There's also async versions if you need them, and you can even add custom m
---

# anthropic

Grounded description of the installed `anthropic` (0.121.0), retrieved from its own upstream repository — not from training knowledge. See `vendor/anthropic/CLAUDE.md` for the full per-vendor digest.

The Anthropic SDK is a Python client library for accessing the Claude API (as documented in the README and `src/anthropic/__init__.py`). The main entry point is the `Anthropic` class, which is a synchronous HTTP client that provides access to Claude models via `client.messages.create()` calls with parameters like `max_tokens`, `messages`, and `model`. The SDK is generated from an OpenAPI specification using Stainless and exports a comprehensive exception hierarchy in the `_exceptions` module. The `AnthropicError` is the base exception class for all API errors, with more specific subclasses like `APIStatusError`, `BadRequestError`, `AuthenticationError`, `RateLimitError`, and others. The SDK also provides `AsyncAnthropic` for async operations, streaming support via `Stream` and `AsyncStream`, middleware support through `Middleware` and `MiddlewareCallable`, and utility functions like `file_from_path`. The SDK requires Python 3.10+.

**Worth reading next:** `src/anthropic/__init__.py` — This file shows all the exported symbols from the SDK, including the client classes and the full exception hierarchy, providing a clear overview of the public API.

## References

- [references/FILETREE.md](./references/FILETREE.md)
- [references/DEPTREE.md](./references/DEPTREE.md)
