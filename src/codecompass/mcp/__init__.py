"""Phase 88 -- Agent Integration and MCP.

A minimal, model-neutral, read-mostly MCP server exposing CodeCompass's
existing knowledge, provenance, contextual retrieval, change-impact
analysis, documentation and controlled verification capabilities to a
real coding agent over the standard MCP stdio transport.

See `planning/phase-88-agent-integration-mcp.md` and `decisions/0095`
for the full design -- this package implements it, it does not
re-derive it. Thin adapters only: every tool delegates to the already-
shipped `knowledge_api`/`oracle`/`knowledge_intermediate`/
`change_impact` modules; no new knowledge store, impact engine, or
verification framework is introduced here.
"""

from __future__ import annotations
