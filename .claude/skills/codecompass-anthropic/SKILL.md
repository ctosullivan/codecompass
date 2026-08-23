---
name: codecompass-anthropic
description: >-
  API questions, known gotchas, and internals for anthropic (python), pinned to the installed version. This is the official Python SDK for Claude, Anthropic's AI model. You use it to send messages to Claude and get responses back. You create an `Anthropic` client object, pass it your API key, and then call methods like `messages.create()` to have Claude process your inputs. The SDK handles all the HTTP communication, error handling, and retries for you. It also provides proper exception types so yo
---

# anthropic

Grounded description of the installed `anthropic` (0.109.1), retrieved from its own upstream repository — not from training knowledge. See `vendor/anthropic/CLAUDE.md` for the full per-vendor digest.

The Anthropic Python SDK provides a client interface to the Claude API. The core export is the `Anthropic` class (defined in `src/anthropic/__init__.py` and `_client.py`), which is instantiated with an API key and provides a `messages.create()` method for interacting with Claude models. The SDK is built on top of HTTP client infrastructure (using httpx) and provides request/response handling through `APIRequest` and `APIResponse` classes. The `AnthropicError` is the base exception class from `_exceptions.py` that all API-related errors inherit from, including `APIStatusError`, `APITimeoutError`, `APIConnectionError`, and various HTTP status code-specific errors like `BadRequestError`, `AuthenticationError`, `NotFoundError`, `RateLimitError`, etc. The SDK also exports utility types like `NOT_GIVEN`, `NotGiven`, and `Omit` from `_types.py` for handling optional parameters, and supports both synchronous (`Anthropic`, `Client`) and asynchronous (`AsyncAnthropic`, `AsyncClient`) usage patterns.

**Worth reading next:** `src/anthropic/__init__.py` — This file shows the main exports and structure of the SDK, including how to instantiate the Anthropic client and the exception hierarchy.

## References

- [references/FILETREE.md](./references/FILETREE.md)
- [references/DEPTREE.md](./references/DEPTREE.md)
