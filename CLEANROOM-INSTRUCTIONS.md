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

Write a complete new README and docs tree from zero.

Do not simply paraphrase the intermediary package mechanically.

See `planning/documentation-handoff/DOCUMENTATION-TARGET.md` for the
required coverage and expected structure.
