# Open questions and conflicts (handoff selection)

**Rebuilt 2026-10-09, Phase 81B Amendment 4, cold-reader finding #3**:
the first version of this file contained only the unfilled candidate-
submission template for each slug (mechanically correct — nothing in
the selected Claims has `status: contradicted` — but it meant several
real, already-stated open design questions sitting inside *supported*
Claims' own prose never surfaced here, which is exactly the file whose
name and purpose promises them). The section below is curated, pulling
verbatim unresolved-question language the knowledge base's own Claims
already state; nothing here is invented.

**Second pass (2026-10-09, cold-reader finding #1, re-run)**: the first
curation pass only swept `haskell-api-surface-extraction` and missed
several more in `codecompass-domain` and `doc-origin-pinned-reference`.
This pass used a systematic grep across all four selected slugs for
self-described unresolved/untested/honest-gap language (not a manual
skim), to avoid the same partial-coverage mistake twice.

## Known limitations disclosed only in source comments (added 2026-10-09, cold-reader finding #5)

The knowledge layer does not surface every disclosed limitation living
in the allowlisted source's own comments — a writer who doesn't happen
to read a given module's docstring could miss one. One confirmed,
real example, checked directly: `src/codecompass/adapters/cargo.py`'s
own module docstring states it is **"Unverified against real cargo
output — no Rust toolchain in this dev environment... Built entirely
against the `_run_json` seam so its parsing logic is unit-tested via
hand-written fixture JSON modeled on cargo's public schema docs."** This
is a real, material limitation worth a line in your own Limitations
section. A systematic grep of `src/codecompass/adapters/*.py` for
similar disclosed-limitation language (as of this preparation pass)
found no other instance — but this was checked for this one pattern
only; read each adapter module's own docstring yourself rather than
assuming this is the only disclosed limitation in the allowlisted
source.

## Known open design questions from supported Claims

These Claims are `status: supported` — not contradicted, not wrong —
but each one's own statement explicitly names a question its own
research did not resolve. A writer should treat these as genuinely
unresolved, not as settled behaviour to describe confidently.

- **CL-ADPT-007** (`codecompass-domain`): "adapter" is a genuinely fuzzy
  boundary in this project's own vocabulary — the word names two
  distinct, unrelated things (the real `EcosystemAdapter` ABC in
  `src/codecompass/adapters/`, and a purely expository "host-output
  adapter" label for `skill.py`/`commands.py`/`index.py` with no
  corresponding class). The Claim notes this project's own
  `architecture/overview.md` already flags the same ambiguity
  independently.
- **CL-EVID-004** (`codecompass-domain`, about this project's own
  knowledge-record model, not CodeCompass's product behaviour): whether
  a Derivation record must always be 1:1 with its Claim is "a genuine,
  currently-unresolved boundary question — an honest 'none found yet'
  for a real N:1 or 1:N counterexample, not a confirmed rule."
- **CL-EVID-005** (same model, meta-level): the rule that only a
  human/project-owner authors a Decision record has "never yet been
  tested against a real, independent, non-standing-in human
  decision-maker anywhere in this repository's history."
- **CL-EVID-011** (same model, meta-level): a real, deliberately
  unresolved naming collision between this project's own file-based
  knowledge-record kinds and an unbuilt, unfunded graph-level entity
  proposal sharing the same names — the Claim calls this "this
  cluster's single most important open question."
- **CL-EVID-012** (same model, meta-level): how the Claim-supersedes-Claim
  mechanism behaves under a genuine contradiction (as opposed to this
  Claim's own narrow, mechanical correction) is explicitly named as
  untested — "a genuinely fuzzy, currently-unresolved boundary."
- **CL-DOCORIGIN-004** (`doc-origin-pinned-reference`): whether a new
  origin-tracking value's name/semantics should be scoped narrowly to
  "Git-commit-pinned" (the only pipeline that currently exists) or
  written more generally to anticipate a future non-Git source is "a
  naming/scope judgment call this research does not resolve."
- **CL-HSAPI-002** (`haskell-api-surface-extraction`): a `module <Name>`
  entry inside a Haskell export list cannot be resolved into a flat set
  of exported names by reading that one line alone — it may need a
  cross-file read of another module's own export list, a file-local
  `import ... as <Name>` alias expansion, or resolve to "this module's
  own complete surface." The Claim is explicit: *"a scope decision the
  next design step must make explicitly, not an ambiguity this research
  can resolve on its own."*
- **CL-HSAPI-003** (`haskell-api-surface-extraction`): a real
  C-preprocessor conditional (`#if MIN_VERSION_time(1,11,0)` /
  `#endif`) can gate whether a name is exported at all (confirmed real
  in `hledger-lib/Hledger/Data/Types.hs`, gating `Year`) — a
  non-preprocessing line scanner cannot evaluate this from the file's
  own text alone. Three handling strategies are named
  (over-approximate / under-approximate / flag-for-follow-up); the
  Claim states plainly: *"This research does not resolve which of
  (a)/(b)/(c) is correct — it depends on... a design choice, not a fact
  about hledger's own source."*
- **CL-HSAPI-006** (`haskell-api-surface-extraction`): a module with no
  export list at all is real (confirmed 17 times in a pinned hledger
  checkout) and exports every top-level binding per Haskell's own
  semantics — but *enumerating* those bindings mechanically, without a
  full parser, depends on Haskell's own column/layout rule in a way
  Rust's `pub fn` keyword-based approach does not need to. The Claim
  states: *"whether a Rust-adapter-tier heuristic... is good enough in
  practice remains untested and is named here as an open question, not
  quietly assumed solved."*

## Per-slug candidate-submission regions (structural, for future
knowledge additions — not itself open-questions content)

## Source: `codecompass-domain`

# codecompass-domain — open questions and conflicts

## Candidate additions

Add new domain knowledge, edge cases, invariants, or open questions below, strictly between the two marker comments. Content outside this region — including this paragraph — is never read as knowledge; it is just narrative framing CodeCompass leaves untouched.

Plain prose becomes an unclassified Claim (a factual hypothesis, not yet evidence-backed) — this is the default and the common case. Merely mentioning a Decision id anywhere in your prose does NOT make your addition a Requirement, and merely using the word "should" or "must" does NOT make it declared intent — both need the explicit structured forms below.

To propose a REQUIREMENT, start the block with a line reading exactly "Type: Requirement", followed by:
  Decision: <id of an existing, already-approved Decision>
  Statement: <the requirement itself, one line>
  Example: <a Given/When/Then acceptance example>
CodeCompass never invents a Decision on your behalf — a missing or not-yet-approved Decision id, or an Example that doesn't structurally read as Given/When/Then, falls back to an ordinary Claim using your Statement text, never a fabricated placeholder example.

To declare project INTENT (a proposed policy, not yet a fact about the system), start the block with a line reading exactly "Type: Intent", followed by the intended behaviour as plain prose on the lines after it.

Anything else — plain prose with no Type: header — stays an unclassified Claim until a reviewer looks at it.

<!-- codecompass-candidates:start --><!-- codecompass-candidates:end -->

---

## Source: `doc-origin-pinned-reference`

# doc-origin-pinned-reference — open questions and conflicts

## Candidate additions

Add new domain knowledge, edge cases, invariants, or open questions below, strictly between the two marker comments. Content outside this region — including this paragraph — is never read as knowledge; it is just narrative framing CodeCompass leaves untouched.

Plain prose becomes an unclassified Claim (a factual hypothesis, not yet evidence-backed) — this is the default and the common case. Merely mentioning a Decision id anywhere in your prose does NOT make your addition a Requirement, and merely using the word "should" or "must" does NOT make it declared intent — both need the explicit structured forms below.

To propose a REQUIREMENT, start the block with a line reading exactly "Type: Requirement", followed by:
  Decision: <id of an existing, already-approved Decision>
  Statement: <the requirement itself, one line>
  Example: <a Given/When/Then acceptance example>
CodeCompass never invents a Decision on your behalf — a missing or not-yet-approved Decision id, or an Example that doesn't structurally read as Given/When/Then, falls back to an ordinary Claim using your Statement text, never a fabricated placeholder example.

To declare project INTENT (a proposed policy, not yet a fact about the system), start the block with a line reading exactly "Type: Intent", followed by the intended behaviour as plain prose on the lines after it.

Anything else — plain prose with no Type: header — stays an unclassified Claim until a reviewer looks at it.

<!-- codecompass-candidates:start --><!-- codecompass-candidates:end -->

---

## Source: `first-party-source-symbols`

# first-party-source-symbols — open questions and conflicts

## Candidate additions

Add new domain knowledge, edge cases, invariants, or open questions below, strictly between the two marker comments. Content outside this region — including this paragraph — is never read as knowledge; it is just narrative framing CodeCompass leaves untouched.

Plain prose becomes an unclassified Claim (a factual hypothesis, not yet evidence-backed) — this is the default and the common case. Merely mentioning a Decision id anywhere in your prose does NOT make your addition a Requirement, and merely using the word "should" or "must" does NOT make it declared intent — both need the explicit structured forms below.

To propose a REQUIREMENT, start the block with a line reading exactly "Type: Requirement", followed by:
  Decision: <id of an existing, already-approved Decision>
  Statement: <the requirement itself, one line>
  Example: <a Given/When/Then acceptance example>
CodeCompass never invents a Decision on your behalf — a missing or not-yet-approved Decision id, or an Example that doesn't structurally read as Given/When/Then, falls back to an ordinary Claim using your Statement text, never a fabricated placeholder example.

To declare project INTENT (a proposed policy, not yet a fact about the system), start the block with a line reading exactly "Type: Intent", followed by the intended behaviour as plain prose on the lines after it.

Anything else — plain prose with no Type: header — stays an unclassified Claim until a reviewer looks at it.

<!-- codecompass-candidates:start --><!-- codecompass-candidates:end -->

---

## Source: `haskell-api-surface-extraction`

# haskell-api-surface-extraction — open questions and conflicts

## Candidate additions

Add new domain knowledge, edge cases, invariants, or open questions below, strictly between the two marker comments. Content outside this region — including this paragraph — is never read as knowledge; it is just narrative framing CodeCompass leaves untouched.

Plain prose becomes an unclassified Claim (a factual hypothesis, not yet evidence-backed) — this is the default and the common case. Merely mentioning a Decision id anywhere in your prose does NOT make your addition a Requirement, and merely using the word "should" or "must" does NOT make it declared intent — both need the explicit structured forms below.

To propose a REQUIREMENT, start the block with a line reading exactly "Type: Requirement", followed by:
  Decision: <id of an existing, already-approved Decision>
  Statement: <the requirement itself, one line>
  Example: <a Given/When/Then acceptance example>
CodeCompass never invents a Decision on your behalf — a missing or not-yet-approved Decision id, or an Example that doesn't structurally read as Given/When/Then, falls back to an ordinary Claim using your Statement text, never a fabricated placeholder example.

To declare project INTENT (a proposed policy, not yet a fact about the system), start the block with a line reading exactly "Type: Intent", followed by the intended behaviour as plain prose on the lines after it.

Anything else — plain prose with no Type: header — stays an unclassified Claim until a reviewer looks at it.

<!-- codecompass-candidates:start --><!-- codecompass-candidates:end -->
