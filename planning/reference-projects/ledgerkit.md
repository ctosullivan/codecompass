# Reference project — Ledgerkit

- **Repository URL:** https://github.com/ctosullivan/ledgerkit
- **Starting revision:** `a3cf2a77ca0075fabd4f7153d2a19f45c6e69b97` (2026-09-12, "feat: close out Stage A — agent roster and compatibility-register harness")
- **CodeCompass revision:** `6c3f34e` (this repo's HEAD at registration time)
- **Working copy location:** session scratchpad (`.../scratchpad/ledgerkit`) — never added to this repo, `vendor.toml`, or `context-graph.db`

## Inspection findings (at the starting revision)

**Superseding note:** the 2026-09-12 desk/`gh` assessment in
`planning/v1-redefinition/ledgerkit-plan.md` §1 is **stale as of this
registration**, exactly as that document anticipated ("confirm at Phase
45/46 — the repo will have moved again by then"). Ledgerkit underwent its
own **"Core redefinition"** the same day, *after* that assessment was
written. This record reflects the live clone, which supersedes the desk
assessment per Phase 45's own design decision.

| Aspect | Finding |
|---|---|
| Purpose | "A deterministic, Python-native accounting and query engine with a documented hledger-compatible foundation" (redefined from the earlier "a Python implementation of the hledger journal format"). |
| Language | Pure Python, `>=3.8`. **Zero mandatory runtime dependencies** (`pyproject.toml` `dependencies = []`); `pandas>=1.3` is a genuinely optional extra (`[project.optional-dependencies]`). |
| Licence | **GPL-3.0-or-later** (matches CodeCompass's own post-Phase-43d licence and `hledger`'s). |
| Structure | `/ledgerkit` (library: `parser.py`, `models.py`, `loader.py`, `writer.py`, `reports.py`, `checks.py`, `editor_model.py`, `commodity_style.py`, `cli.py`, `_pandas_compat.py`), `/tests`, `/docs` (user-facing: `getting-started.md`, `journal-format.md`, `python-api.md`, `usage.md`), `/dev-docs` (architecture/API/compatibility specs + the entire `dev-docs/planning/core-redefinition/` governance package), `/knowledge` (`DECISIONS.md`, `EDGE_CASES.md`, `ANTIPATTERNS.md`, `DOMAIN_RULES.md`), `/validation/codecompass` (Ledgerkit's own findings-intake mechanism — see below). |
| Governance | `CLAUDE.md`, `CONTEXT.md` (explicitly "throwaway"), `ROADMAP.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.claude/agents/` (7 roles: `compat-differential-tester`, `context-curator`, `docs-maintainer`, `docs-reconstructor`, `hledger-researcher`, `release-phase-auditor`, `roadmap-context-curator`). |
| **Major finding — Ledgerkit has already adopted CodeCompass's own adoption blueprint (Phase 43e).** | Its newly-closed **Stage A** ("Development foundation — agent roster, CodeCompass integration, compatibility harness, learning/doc lifecycle") explicitly mirrors CodeCompass's own agent-led model. `dev-docs/planning/core-redefinition/04-codecompass-integration.md` cites CodeCompass's *own* `ledgerkit-plan.md` and correctly states CodeCompass's real current capabilities (no false assumptions). A live `.claude/agents/context-curator.md` role and `validation/codecompass/{README.md,findings/TEMPLATE.md}` mechanism exist, structurally matching `codecompass-feedback-ingestion.md`'s design almost exactly (a `CC-LK-NNN` finding ID scheme, PASS/PASS WITH GAPS/FAIL + LOW/MODERATE/HIGH advantage rating, "never edits CodeCompass directly" rule). **No findings filed yet** ("none exist yet") — first real usage is expected once Stage B/C generate genuine tasks, per Ledgerkit's own Stage A closeout note. |
| **Roadmap state — materially changed from the desk assessment.** | The old "Milestone 5 — CLI Filter Flags" (the task `ledgerkit-plan.md` and this project's own Phase 45/46 stanzas were built around) is now **`[SUPERSEDED]`** (2026-09-12): "wiring CLI flags directly to today's `Query` dataclass... would build exactly the narrow ad-hoc filtering the Core redefinition replaces with a proper query AST." The underlying user need is preserved, folded into the new **Stage C (Query System)**, not yet started. Milestones 0–4 remain `[DONE]` (485 tests passing). Forward roadmap is now **Stages A–I**: A `[DONE]` (2026-09-12), B (Core model) `[PLANNED]` next, C (Query system) `[PLANNED]`, D–I `[PLANNED]`. |
| Tests | 485+ tests passing as of Milestone 4/Stage A close (unconfirmed exact current count at this pinned commit — not re-run as part of registration, per the non-invasiveness check). |

### Why this remains the harder test (unchanged from `ledgerkit-plan.md`)

Confirmed live, not just assumed: Ledgerkit's real technical dependencies
are still, in order, the `hledger` executable's behaviour, hledger
manuals/reference docs, journal syntax, query semantics, general
plain-text-accounting reference material, observed black-box hledger
behaviour, the local implementation, and compatibility tests pinning all
of the above together. **None of 1–6 is a package.** This registration
confirms CodeCompass's current model represents *none* of them and
additionally **cannot even see** Ledgerkit's own primary documentation of
several (`dev-docs/hledger-compatibility.md` — see baseline finding
below and `CG-002`).

## Baseline evaluation (Phase 45)

CodeCompass was run against the pinned clone as-is (`codecompass
--budget 0`, bare auto-discovery + `codecompass check`):

- **0 vendors discovered** — `dependencies = []`; `pandas` correctly not
  auto-discovered as it's a genuinely optional extra. Matches the
  expected near-empty result.
- **`README.md` / `docs/*.md` indexed as spec docs, zero relations** —
  accurately "thin" (nothing to relate to with 0 vendors), not wrong.
- **`dev-docs/hledger-compatibility.md` — the file that actually states
  what governs hledger-1.52 compatibility — is entirely invisible**:
  `codecompass query relations dev-docs/hledger-compatibility.md` →
  `error: not found in context-graph.db`. Root cause confirmed by
  reading `src/codecompass/spec_docs.py::_DEFAULT_GLOBS` directly: no
  `dev-docs/**/*.md` entry. Filed as **`planning/context-gaps/CG-002`**
  — the same category of fix as Phase 37's `ai-docs/` glob addition, this
  time surfaced by an external reference project rather than
  CodeCompass's own dogfooding.
- **No mechanism at all for "what is this project's current
  roadmap/development-stage state"** — not a gap CodeCompass has ever
  claimed to fill; noted for completeness, not filed as a context-gap.

Full per-question `context-evaluator` reports:
[`planning/reference-projects/ledgerkit/00-baseline.md`](ledgerkit/00-baseline.md).

`context-health-planner`'s first genuine solo run (tracked forward from
Phase 43c) assessed graph adequacy for the upcoming Phase 46 task —
see `planning/context-health.md`'s 2026-09-13 Ledgerkit section. Verdict:
LOW context-advantage predicted for Phase 46, CG-002 directly
load-bearing (Stage B's task material lives in `dev-docs/`).

## Evaluations

| # | Pinned revision | Task | CodeCompass revision | Verdict | Advantage | Report |
|---|---|---|---|---|---|---|
| 00.Q1 | `a3cf2a7` | Baseline: runtime dependencies | `6c3f34e` | PASS WITH GAPS | LOW | [`ledgerkit/00-baseline.md`](ledgerkit/00-baseline.md#q1--runtime-dependencies) |
| 00.Q2 | `a3cf2a7` | Baseline: what governs hledger-1.52 compatibility | `6c3f34e` | **FAIL** | LOW (negative) | [`ledgerkit/00-baseline.md`](ledgerkit/00-baseline.md#q2--what-governs-ledgerkits-hledger-152-journal-format-compatibility) |
| 00.Q3 | `a3cf2a7` | Baseline: current roadmap/stage state | `6c3f34e` | PASS WITH GAPS | LOW | [`ledgerkit/00-baseline.md`](ledgerkit/00-baseline.md#q3--ledgerkits-current-development-stage--roadmap-state) |

**Q2 is CodeCompass's first FAIL verdict of the redefined-v1 effort.** Not
an honest "no relations found" — a confident-sounding "not found in
context-graph.db" for a real, current, 238-line file
(`dev-docs/hledger-compatibility.md`) that is precisely the project's own
designated hledger-1.52-compatibility governance document. Root cause:
`CG-002` (the `dev-docs/**/*.md` glob-coverage gap). A second, distinct
symptom-layer finding (the "not found" error is indistinguishable from a
genuine typo, giving no signal to suspect a coverage gap) filed as
**L-016**. Q1's optional-dependency silence filed as **L-015**. Per
`context-quality-evaluation.md` §6, every "would this have misled the
agent — yes/partially" verdict is listed in full as the highest-priority
GATE DB input: **Q1 partially, Q2 yes, Q3 no.**

*(Task-specific evaluations — e.g. the genuine Stage B task Phase 46 will
attempt — are added as rows `01`, `02`, ... once that phase runs.)*

## Non-invasiveness check (per phase, reference-project-protocol.md §2.7)

- **Phase 45:** confirmed. No change was proposed or made to Ledgerkit's
  real, pushable repository — only its own generated artifacts
  (`vendor.toml`, `CLAUDE.md`'s auto-generated routing-table block) were
  written *inside the disposable scratch clone* as CodeCompass's normal
  operating behaviour when run against any project; nothing was
  committed, pushed, or proposed upstream. No CodeCompass repair was made
  to force a result — the near-empty baseline and the `dev-docs/` gap
  were recorded exactly as found.
