# Reference-project plan — Ledgerkit (required output 9)

The **harder second** proof point. Used in Stage D to decide whether
redefined-v1 scope must expand beyond package-source grounding.

Repo: **https://github.com/ctosullivan/ledgerkit**

## 1. Inspection findings (this planning session, 2026-09-09)

| Aspect | Finding |
|---|---|
| Purpose | "A bridge to the hledger plain-text accounting ecosystem." Parse journal files, query transactions, export reports to pandas DataFrames. |
| Language | Pure Python 3.8–3.12. **No third-party runtime dependencies.** `pandas` is an optional extra. |
| Structure | `/ledgerkit` (library), `/tests`, `/docs` (user), `/dev-docs` (architecture + API specs). |
| Features | Journal parsing "compatible with hledger 1.52 format"; directives (`include`, `account`, `commodity`, `payee`, `alias`, price rules); CLI `balance` / `register` / `print` / `accounts` / `stats` / `check`; multi-commodity tree rollup. |
| hledger alignment | Modelled "primarily on the hledger 1.52 specification"; credits hledger's maintainer. |
| Governance | `CLAUDE.md` / `CONTEXT.md` / `ROADMAP.md`; AI-assisted workflow; sparse-checkout option to clone source without AI-workflow metadata. |
| State | 37 commits, single `main` branch, 0 open issues, 4 stars. Active planning. |
| Confirm at Phase 52 | exact roadmap state, test layout, `dev-docs/` contents, current priorities — the repo will have moved. |

### Why this is the harder test

Ledgerkit's real technical dependencies are, in rough order of
importance:

1. the **`hledger` executable** — its actual runtime behaviour;
2. **hledger manuals / reference documentation** — journal format,
   query semantics, the `hledger`/`hledger-ui`/`hledger-web` command
   docs;
3. **journal syntax** as a file-format / grammar;
4. **query semantics** (hledger's query language);
5. general **accounting / plain-text-accounting reference material**;
6. **observed black-box hledger behaviour** (where docs are silent or
   ambiguous, established by experiment);
7. the **local Ledgerkit implementation**;
8. **compatibility tests** pinning 1–7 together.

None of 1–6 is a package. CodeCompass's current model represents exactly
one of these (7, partially, as "the project's own source") and relates
nothing.

## 2. Stage D plan

### Phase 52 — Register + baseline (EXPERIMENTAL)
Clone at a pinned commit; run CodeCompass as-is; record the (expected
near-empty) result precisely; `context-evaluator` baseline report for
2–3 "what does this depend on / what governs this behaviour" questions.
Output: `planning/reference-projects/ledgerkit.md`.

### Phase 53 — Doc / reference test (EXPERIMENTAL)
Question: can CodeCompass usefully **index and relate reference
material** — the hledger manual (as fetched/vendored text), the journal
format spec, command docs — to Ledgerkit's local implementation and
compatibility tests, **as evidence nodes with provenance**, without a
premature schema commitment?

- Try it with the mechanisms that already exist: register the manual
  text the way vendor upstream docs are registered (`kind='vendor_doc'`
  precedent, Phase 27/29); see whether mechanical mention-detection +
  the doc-relations graph produce anything trustworthy linking "manual
  section on X" ↔ "ledgerkit code implementing X" ↔ "test verifying X".
- `context-evaluator` rates whether the resulting relations are accurate,
  grounded, and materially useful for a real Ledgerkit task (e.g. a
  journal-directive compatibility fix).

### Phase 54 — Behavioural / executable test (EXPERIMENTAL)
Question: can CodeCompass **consume and relate** externally-produced
behavioural evidence?

- **CodeCompass does not run `hledger`.** Ledgerkit-specific tooling (a
  script in Ledgerkit, or a scratch harness) executes `hledger`, creates
  fixtures, inspects outputs, does differential tests, and emits evidence
  records (a small structured file: "input journal J, `hledger balance`
  produced O, at hledger version V, date D").
- CodeCompass's role under test: ingest those evidence records and relate
  them — "behaviour B is *documented by* manual §M, *observed by*
  experiment E, *implemented by* `ledgerkit/report.py:balance`,
  *verified by* `tests/test_balance.py::test_multi_commodity`."
- `context-evaluator` rates whether that assembled map is accurate and
  whether it would genuinely help an agent working on a real hledger
  compatibility gap — versus the agent just running `hledger` itself and
  reading the manual.

### Phase 55 — Decision (EXPERIMENTAL → GATE DD, gate G7)
Written decision at `planning/reference-projects/ledgerkit/findings.md`:

1. Is a generalised **technical-dependency** concept necessary for v1?
   If yes — which kinds beyond `package` (executable? manual/reference?
   spec? file-format? behavioural contract?), each backed by a Ledgerkit
   (and ideally also Technical Clipper) finding.
2. Is first-class **provenance/evidence** necessary for v1? If yes —
   which distinctions (source-derived fact / doc statement / spec
   requirement / observed behaviour / test result / ADR / agent
   inference), and which per-claim attributes (what is claimed / which
   version / evidence source / verification state / route back /
   relationship to local impl+tests).
3. **What is the smallest model** that covers the demonstrated need?
   (`conditional-generalisation.md` structures this.)
4. Or: "not justified for v1 — the package-source model plus Stage C
   improvements is the redefined v1; Ledgerkit-driven scope becomes
   v1.x." This is a fully acceptable outcome.

## 3. Hard boundaries (task instruction)

- CodeCompass is **not** the hledger black-box experiment runner
  (`README.md` §1.9).
- The Ledgerkit relationship model
  (`external behaviour → documented by / observed by / implemented by /
  verified by`) is a **candidate to validate**, not a design to
  implement before the experiment.
- No feature is added to Ledgerkit to make CodeCompass easier to
  evaluate; Stage D is subordinate to Ledgerkit's own roadmap.
