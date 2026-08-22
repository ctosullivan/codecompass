---
name: codecompass-anthropic
description: >-
  API questions, known gotchas, and internals for anthropic (python), pinned to the installed version. This is the official Python SDK for Anthropic's Claude API. It lets you make API calls to Claude from your Python code in a clean, intuitive way. You instantiate an `Anthropic` client with your API key, then call methods like `client.messages.create()` to send requests and get responses. The SDK handles all the HTTP details, error responses, retries, and authentication for you. It supports both bl
---

# anthropic

Grounded description of the installed `anthropic` (0.121.0), retrieved from its own upstream repository — not from training knowledge. See `vendor/anthropic/CLAUDE.md` for the full per-vendor digest.

The Claude SDK for Python provides access to the Claude API from Python applications. According to the `src/anthropic/__init__.py`, the SDK exports a `Client` class (aliased as `Anthropic`) that serves as the main entry point for making API calls. The module is generated from an OpenAPI specification using Stainless and provides comprehensive error handling through exception types like `APIError`, `AuthenticationError`, `RateLimitError`, and others defined in `_exceptions`. It also supports both synchronous (`Anthropic`, `Client`) and asynchronous (`AsyncAnthropic`, `AsyncClient`) clients for API interactions. The SDK includes middleware support via `Middleware` and `MiddlewareCallable` types from `_middleware`, request/response handling through `APIRequest` and `APIResponse`, and specialized integrations for AWS, Google Cloud, Bedrock, and Vertex platforms. Core types are exported through a `types` module.

## References

- [references/FILETREE.md](./references/FILETREE.md)
- [references/DEPTREE.md](./references/DEPTREE.md)
