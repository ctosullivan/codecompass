# Open questions and conflicts

Compiled from the project's own currently-known open design questions, plus anything this reconstruction itself could not resolve from the available evidence. None of these is presented as settled — they are reported as genuinely open.

## Genuinely unresolved design/boundary questions, named in supported (not contradicted) Claims

- **Is a Derivation record always 1:1 with its Claim?** Every real instance found to date is 1:1, but nothing in the schema or the validator actually forbids a future Derivation being cited by more than one Claim. Described as "an honest 'none found yet,' not a confirmed rule."
- **Has the "only a human/project-owner authors a Decision" rule ever been genuinely tested?** Every real Decision record on file to date was authored by a lead explicitly standing in for the actual user/project-owner role — this has never yet been tested against a real, independent, non-standing-in human decision-maker.
- **How does the Claim-supersedes-Claim mechanism behave under a genuine contradiction**, as opposed to a narrow, mechanical citation-freshness correction? Described as untested, "a genuinely fuzzy, currently-unresolved boundary."
- **A real, named naming collision** between the file-based Evidence/Observation/Claim/Decision model (described in `docs/concepts/knowledge-model.md`) and an unbuilt, unfunded, graph-level entity-kind proposal sharing the same names for a different scope (structured provenance about a *target project's* own dependencies, inside `context-graph.db` itself). Not resolved, not this reconstruction's to resolve — both the knowledge-model's own research and the project's own later process notes name it as deliberately still open.
- **A Haskell `module <Name>` export-list entry's own resolution scope** — whether a minimal, no-full-parser extractor should ever attempt the one-level-removed alias/package-aggregation cases beyond file-local resolution — is named explicitly as "a scope decision the next design step must make explicitly, not an ambiguity this research can resolve on its own."
- **CPP-conditional-gated Haskell export entries** — whether the correct policy should be over-approximate (always exported), under-approximate (always skipped), or flag-for-follow-up (the policy actually implemented) is named as depending on "how much precision the adapter's whole purpose actually needs, a design choice, not a fact about [the reference project]'s own source."
- **Enumerating a no-export-list Haskell module's own top-level bindings** without a full parser — whether a Rust-adapter-tier heuristic would be good enough in practice — is explicitly named as untested, not quietly assumed solved.

## Vocabulary ambiguities, confirmed real rather than invented by this reconstruction

- **"Adapter"** has two senses in this project's own documentation (the real `EcosystemAdapter` ABC, and a purely expository "host-output adapter" label with no corresponding class) — see `docs/concepts/adapter.md`.
- **"Context"** has at least five distinct, non-interchangeable senses — see `docs/concepts/context.md`.
- **"Capability" vs. "feature"** — only the external adapter protocol has capabilities in a formal, closed-set sense; "feature" is ordinary unscoped English elsewhere — see `docs/concepts/protocol-and-capability.md`.
- **"Connector"** names nothing real in CodeCompass's own source, tests, or configuration.
- **"Invariant"** is not a formal knowledge-record kind and names at least three distinct, not-necessarily-coinciding things across the project — see `docs/concepts/knowledge-model.md`.

## A directly-observed fact with no recorded explanation

`pyproject.toml` declares the PyPI distribution name `codecompass-context`, while the importable package and CLI entry point are both `codecompass`. No evidence available to this reconstruction explains why these differ (e.g. a PyPI name collision with an unrelated project). Both names are documented accurately wherever each is the one a reader actually needs (see the root `README.md`) rather than conflating them or guessing at a reason.

## Scope asymmetry inside the project's own domain-knowledge research

Most of the project's own `codecompass-domain` knowledge-slug content describes CodeCompass's own internal Phase-54c development-*process* history (how CodeCompass's own maintainers produced their own internal knowledge base) rather than how an end user operates the shipped, general-purpose `codecompass knowledge` CLI on an arbitrary project. These are two different scopes sharing one vocabulary; this documentation has tried to be explicit about which scope each statement in `docs/concepts/knowledge-model.md` actually belongs to, but a reader consulting the project's own underlying research materials directly should expect to find the same blending there.

## A real ADR-vs-implementation naming inconsistency

See `docs/reference/protocols.md`'s own note: an older decision record's text uses "adapter" spelling for the two external repositories; every live artifact uses "adaptor." Understood as a pre-implementation drafting typo that was never corrected in the decision text itself, rather than a live, unresolved question about which spelling is canonical going forward — but no evidence confirms a corrective edit to that decision text exists.

## Not independently re-verifiable from this reconstruction's own evidence

A number of specific, quantified claims in the project's own research (exact line-number citations into a third-party reference project's source tree; an Anthropic-SDK-session-ownership real test confirming the external model broker's own "no project knowledge" isolation claim; a few specific fixture-based test results described only narratively rather than via a re-openable raw record) could not be independently re-checked from the evidence actually supplied to this reconstruction. They are reported here as *evidenced-but-not-independently-re-verified-by-this-reconstruction*, not as unverified assertions on the project's own part.
