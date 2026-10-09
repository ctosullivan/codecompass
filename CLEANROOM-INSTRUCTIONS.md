# Clean-room documentation writer instructions

You have no prior knowledge of this project.

Construct its documentation from first principles.

Use only the evidence supplied in this workspace -- the allowlisted
source/tests/configuration you can see, and the
`planning/documentation-handoff/` package, specifically.

The `planning/documentation-handoff/` package represents the project's
prepared semantic understanding. Start with its own `README.md`.

Use the current source, tests, configuration, and schemas in your own
workspace to verify and add technical detail the knowledge layer doesn't
carry.

Do not attempt to recover previous project documentation. None exists
anywhere in your own workspace, in any form.

Do not use Git history, external repository search, internet search, or
other repositories as project-documentation sources -- none of these are
technically reachable from inside your own workspace.

Do not assume undocumented behaviour.

Every important technical statement must either:
1. be supported by the supplied intermediary/evidence material; or
2. be independently verified by you against the current source/tests/
   configuration in your own workspace.

If evidence conflicts, preserve the conflict or uncertainty -- do not
silently resolve it.

Your workspace's `scripts/` directory contains maintainer-only tooling,
not part of the `codecompass` package itself (each one's own module
docstring says so). `check_knowledge_base.py`, `check_user_docs.py`, and
`prepare_cleanroom_branch.py` are ordinary repository-maintenance
tooling -- you may mention their existence and purpose briefly in a
development/contributing section if you judge that useful, the same way
you would any other maintainer script. `cleanroom_broker.py`,
`cleanroom_broker_client.py`, and `cleanroom_prompt_assembler.py`
specifically implement the clean-room mechanism that produced the
workspace you are reading right now -- do not describe, explain, or
reference this mechanism in the documentation you write; it is
orchestrator-internal tooling, not a CodeCompass product capability, and
is entirely out of scope for what you are being asked to document.

Write a complete new README and docs tree from zero.

Do not simply paraphrase the intermediary package mechanically.

See `planning/documentation-handoff/DOCUMENTATION-TARGET.md` for the
required coverage and expected structure.
