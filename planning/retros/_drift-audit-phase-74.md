# Docs-drift audit — Phase 74 (Priority B provenance hardening, L-031 + L-032)

**Mode:** 1 — per-phase drift audit (`documentation-lifecycle.md` §2.5).
**Commits audited:** `1dc228f` (plan(phase-74): plan + ROADMAP row —
touches only `planning/ROADMAP.md` and the new plan file, neither a
current-truth doc in this audit's scope) and `050e366` (feat(phase-74):
the actual behaviour change). Confirmed via `git show --stat` on each
commit individually — an earlier combined-range diff
(`1dc228f~1..050e366`) transiently pulled in an unrelated `38d577c`
(Phase-73 docs cleanup, already covered by
`planning/retros/_drift-audit-phase-73.md`) sandwiched between the two;
that commit's `architecture/historical-notes.md` change is **not**
Phase 74's and is excluded from this report.

**Verdict: DRIFT — 4 findings** (all in `README.md` and `architecture/`;
the phase's own `docs/protocol-adapter/wire-protocol.md` fix is accurate
and complete, verified independently below).

## What actually changed (from the code, not the commit message)

1. `symbol_enrichment` gains a nullable `model TEXT` column
   (`graph.py`, new `_migrate_symbol_enrichment_model_column`).
   `record_symbol_enrichment` now requires a real `model: str` argument;
   `enrichment.py`'s one call site passes `_MODEL`. Net effect: every
   *new* `symbol_enrichment` row now records its producer, matching
   `vendor_enrichment`/`doc_relation_enrichment`. Only rows written
   *before* this migration can still be `NULL`.
2. `ExternalAdapterProcess.initialize` now takes a required
   keyword-only `expected_ecosystem: str` and, after the existing
   `protocol_version` check, raises `AdapterError` if the response's
   `ecosystem` doesn't match it, and raises `AdapterError` if any
   `capabilities` entry falls outside the module's closed `CAPABILITIES`
   tuple (`("dependencies", "symbols", "observations", "diagnostics")`).
   `HaskellAdapter._analyze` (`haskell.py:188`) is the one call site,
   passing `expected_ecosystem=self.config.ecosystem`.

Both are genuine behaviour changes a user-facing/developer-facing doc
could now misdescribe: (1) changes what a `symbol_enrichment` row
contains and whether it's attributed; (2) changes what happens when a
non-Haskell external adapter misreports its ecosystem or capabilities —
previously silent, now a hard `AdapterError` at `initialize`.

## `docs/protocol-adapter/wire-protocol.md` — verified accurate and complete

Checked the new "Handshake validation (closed, Phase 74)" section and
the rewritten `ecosystem`/`capabilities` table rows against the actual
code in `external_process.py` (reproduced above) and against
`haskell.py:184-188` (`_analyze`, the real call site). Findings:

- The `ecosystem` row's description of the check (compares against
  `expected_ecosystem`, raises `AdapterError`, "same posture as
  `protocol_version`") matches the code exactly.
- The `capabilities` row's description (membership check against the
  closed 4-value set, raises `AdapterError`) matches the code exactly.
- The new section's claim that `HaskellAdapter._analyze` passes
  `expected_ecosystem=self.config.ecosystem` is verified correct
  (`self.config.ecosystem` is a `core.Ecosystem` `StrEnum` member, per
  `config.py`'s `_require_enum(..., Ecosystem)`).
- No dangling references to the old section elsewhere in the file (its
  heading changed from "A real, observed gap — not enforced by code,
  only by specification" to "Handshake validation (closed, Phase 74)";
  grepped the rest of the file's `## ` headings, no other section still
  refers to the old name or restates the old "not validated" claim).

This fix is accurate and complete for its own file. No follow-up needed
here.

## Findings — current-truth docs this phase's changes made false

### 1. `README.md:276-278` — BLOCKING

> - **`symbol_enrichment` rows carry no producer/model attribution**
>   (see "Evidence & provenance" above) — a known, disclosed asymmetry
>   with the other two enrichment tables, not yet fixed.

False as of this phase: `symbol_enrichment` now has a `model` column
and every new write supplies a real value (`enrichment.py`'s
`record_symbol_enrichment(..., model=_MODEL)` call site). The asymmetry
this bullet discloses is exactly what L-031 closed. (The nullable
legacy-row case — rows written before this migration have `NULL` — is a
real, narrower caveat that could replace this bullet, but the bullet as
written is a blanket, now-false claim.)

### 2. `README.md:165-178` ("Evidence & provenance" section) — BLOCKING

> AI-enriched content ... record **which model or agent produced them**
> ... — per-symbol purposes currently do **not** carry this same
> producer tag, a known, disclosed asymmetry (tracked in
> `planning/ROADMAP.md`'s future-improvement backlog, not yet fixed).

Same underlying claim as Finding 1, restated in the section it
cross-references. Also now false, and also cites `planning/ROADMAP.md`'s
future-improvement backlog — worth checking that L-031 has actually been
removed from that backlog table (the Phase 74 plan commit's own message
claims "L-031/L-032 removed from the Future-improvement backlog table");
if so, this sentence is doubly stale (both the claim and its own cited
tracking location).

### 3. `README.md:279-282` — BLOCKING

> - **The external-adapter wire protocol's `ecosystem` and
>   `capabilities` fields are received but not validated** against what
>   CodeCompass itself expects — an adapter reporting a mismatched value
>   is currently accepted uncomplainingly.

False as of this phase: both fields are now validated at `initialize`,
raising `AdapterError` on mismatch (L-032, verified above against
`external_process.py`). This is the README's own Limitations-section
twin of the gap `docs/protocol-adapter/wire-protocol.md` already fixed
in this phase's own commit — `docs-maintainer` updated the wire-protocol
page but missed this restatement in `README.md`.

### 4. `architecture/context-graph-schema.md:94-96` — BLOCKING

> - **`symbol_enrichment`** — one row per symbol (`symbol_id` UNIQUE),
>   `purpose`, `generated_at`. Written only by
>   `graph.record_symbol_enrichment`.

The column list is now wrong: it omits `model`, the column this phase
added. Contrast with the same list's own entries immediately above/below
for `vendor_enrichment` and `doc_relation_enrichment`, both of which
explicitly list `model` in their column enumeration — `symbol_enrichment`
used to legitimately omit it (that absence *was* the asymmetry L-031
closed); now it's simply an incomplete/wrong schema description, the
kind of doc a developer would trust to know what columns exist without
reading `graph.py` directly.

### 5. `docs/developer/writing-an-adapter.md:153-166` — BLOCKING

The code block is explicitly captioned "(`haskell.py`'s `_analyze`, real
code, ...)" but line 158 reads:

```python
process.initialize()
```

The real, current `haskell.py:188` is
`process.initialize(expected_ecosystem=self.config.ecosystem)`.
`initialize`'s `expected_ecosystem` parameter is keyword-only and has no
default, so the code as printed would raise `TypeError` if copied
verbatim — and the page asserts this is real code, not illustrative
pseudocode.

### 6. `docs/protocol-adapter/integrating-a-new-external-adapter.md` — BLOCKING (two sub-findings)

- **Line 54**: "Construct one `ExternalAdapterProcess([executable_path])`
  ... call `.initialize()`, then `.analyze_project(...)`, then
  `.shutdown()`." Same issue as Finding 5 — a future second
  external-adapter author following this instruction literally gets a
  `TypeError`; the call now requires `expected_ecosystem=` and there is
  no default to omit it.
- **Line 88-90**: "Respond to `initialize` with your `protocol_version`
  (currently `1`), `adapter_name`, `adapter_version`, `ecosystem` (free
  text), and the subset of the four capabilities you can actually
  produce." Calling `ecosystem` "free text" is no longer the operative
  constraint from this guide's own audience's point of view: the
  Python-side caller now validates the response's `ecosystem` field
  against the exact `expected_ecosystem` value it was constructed with
  (`self.config.ecosystem`, a `core.Ecosystem` member's string value) and
  raises `AdapterError` on any mismatch. A new adapter author reading
  "free text" could reasonably send any string and only discover the
  real constraint (must match CodeCompass's own configured ecosystem
  name for that vendor) at runtime failure. Not literally false — the
  wire-level *type* is still free text at the schema level, matching
  `SCHEMA.md` — but materially incomplete for this specific guide's
  purpose (advising a new adapter author what to actually send), which
  is exactly what `wire-protocol.md`'s own now-correct entry for the same
  field already captures.

### Non-blocking observation (not counted in the drift total)

`docs/protocol-adapter/integrating-a-new-external-adapter.md:20-29`'s
"What CodeCompass provides for free" bullet list (spawning the
subprocess, the `initialize` handshake including the `protocol_version`
mismatch check, JSON-Lines framing, `error`→`AdapterError` mapping,
`shutdown()`) doesn't mention the two new checks (`ecosystem`,
`capabilities` validation) this phase added to that same handshake. The
list is introduced with "It handles:" rather than an explicit "only,"
and the `protocol_version` bullet's own "including" wording already
signals non-exhaustiveness, so this isn't a false statement — but it's
an omission a docs-maintainer pass should probably close alongside
Finding 6, since it's the same section of the same page.

## Domain-claim staleness candidates (not drift findings — flagged for `domain-skeptic`, out of this audit's scope per the dispatch)

This phase's diff touches exactly the two things multiple
`docs/domain/concepts/*.md` pages cite as open gaps in their own
references/discussion:

- **L-031 (`symbol_enrichment.model`)**: cited in
  `docs/domain/concepts/provenance.md` (lines ~24, 74, 81, 83, 112 —
  "`symbol_enrichment` ... has no `model` column"),
  `docs/domain/concepts/evidence.md` (~108, 114 — "`symbol_enrichment`
  carries [no `model`]"), `docs/domain/concepts/observation.md` (~60),
  `docs/domain/concepts/relationship-edge.md` (~119), and
  `docs/domain/open-questions.md` item 9 (~113-118, "`symbol_enrichment`
  has no provenance column at all").
- **L-032 (ecosystem/capabilities handshake validation)**: cited in
  `docs/domain/concepts/capability.md` (~64-76 — "not validated ...
  against that closed 4-value set at parse time"),
  `docs/domain/concepts/ecosystem.md` (~57-69 — "stored but never
  subsequently read"), `docs/domain/concepts/protocol.md` (~69-79 —
  "free text at the wire-protocol level ... no negotiation"), and
  `docs/domain/open-questions.md` item 10 (~121-128).

Per this dispatch's own instructions, `domain-skeptic` is already
separately checking these — I have not formed or am not asserting any
view on whether the concept pages are now wrong, only naming that this
phase's diff is exactly what their own citations point at.

## Scope note

**Checked:** every current-truth doc surfaced by grepping for the
affected symbols/behaviour (`symbol_enrichment`, `record_symbol_enrichment`,
`initialize(`, `expected_ecosystem`, `ecosystem`/`capabilities`
validation language, "not validated"/"uncomplainingly"/"observed gap"
phrasing) across `README.md`, `docs/**`, `architecture/**`, `ai-docs/**`.
Independently re-verified the code (`graph.py`, `external_process.py`,
`haskell.py`, `enrichment.py`) rather than trusting the commit message or
`docs-maintainer`'s own claim that only `wire-protocol.md` needed
updating — that claim turned out to be incomplete (Findings 1-6 above).

**Not checked / deliberately out of scope:** `docs/domain/**` (explicitly
descoped to `domain-skeptic` per the dispatch — see candidates list
above, which is informational only, not a drift verdict input); the test
files changed in `050e366` (`test_graph.py`,
`test_adapters_external_process.py`, `test_adapter_haskell.py`,
`tests/fixtures/fake_adapter.py`) — internal test scaffolding, no
observable-behaviour claim in any current-truth doc rests on them;
`architecture/historical-notes.md`'s Phase-73 change that appeared in an
overly-wide diff range — confirmed not part of Phase 74's own commits
(see header) and already covered by
`planning/retros/_drift-audit-phase-73.md`; minor pre-existing line-number
citations in `wire-protocol.md` (e.g. `external_process.py:75-80` for the
`protocol_version` check) that shifted by a few lines because of this
phase's own insertions above them — genuinely trivial, not a
misdescription of behaviour, not reported as a finding.
