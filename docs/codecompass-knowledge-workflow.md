# The CodeCompass knowledge workflow

This guide is self-contained. You don't need to know anything else about
CodeCompass's own internals to use it — it is written for a human
contributor, an AI coding tool (ChatGPT, GitHub Copilot, Claude Code),
or any other agent landing on this repository cold.

## What this is

CodeCompass keeps a structured record of what a project knows, intends,
requires, and why — concepts, architectural decisions, invariants,
behaviours, open questions — under `planning/knowledge/<slug>/`, one
directory per bounded topic. Each fact is a small, plain-text record
(`.yaml`), not a database file. That's the **canonical** knowledge.

Every slug's own records are projected into **editable Markdown** under
`planning/knowledge/<slug>/intermediate/*.md` — a live view of what the
canonical records currently say, that you can edit directly, in an
ordinary text editor, with no special tooling required to read or
propose a change.

## What is canonical, what is editable

| Location | What it is | May you edit it? |
|---|---|---|
| `planning/knowledge/<slug>/*.yaml` | The canonical records | No — edit the projection instead, and let reconciliation update these |
| `planning/knowledge/<slug>/intermediate/*.md` | A live, editable projection | **Yes** — this is the supported way to propose a change |
| `planning/knowledge/<slug>/snapshots/*.toml` | A frozen, historical snapshot | No — frozen by design |
| `planning/knowledge/<slug>/reconciliation/*.toml` | A reconciliation manifest (see below) | No — written by tooling, read by a reviewer |
| `planning/knowledge/<slug>/intermediate/.presentation-cache.toml` | Cached wording for a Claim whose meaning hasn't changed | No — written automatically |

Every rendered block in a projection looks like this:

```markdown
<!-- codecompass-knowledge: CL-ARCH-014 semantic-sha256:3f9a1c... projection-sha256:9e04bb... -->
### CL-ARCH-014

The sync pipeline can be invoked any number of times without changing
its own result.

Status: status=supported
Provenance: OBSERVED
<!-- /codecompass-knowledge -->
```

- **Provenance** tells you where this came from: `OBSERVED` (every
  relevant piece of evidence actually traces to a real, recorded
  Observation), `DECLARED` (a maintainer's stated intent, or evidence
  that cites a source/doc/test directly with no discrete Observation
  behind it), `DECIDED` (authorised by an approved decision), `DERIVED`
  (reasoned from evidence), `HISTORICAL` (superseded, kept for its own
  record), `MIXED` (the record's own evidence chain combines both
  observed and non-observed sources), or `UNCLASSIFIED` (a brand-new
  external candidate nobody has classified yet — see "How to add new
  material" below). Ambiguity always resolves to the more cautious
  label, never the stronger one.
- **Never edit the anchor comment itself** — edit the prose between the
  markers. The anchor is how CodeCompass finds its way back to the
  exact record you changed.

## How to add new material

Every projected file ends with a bounded region:

```markdown
## Candidate additions

<!-- codecompass-candidates:start -->

<!-- codecompass-candidates:end -->
```

Write your new domain knowledge, edge case, invariant, or open question
**strictly between these two marker comments**. Prose anywhere else in
the file — including reorganising headings, adding commentary, or
reformatting — is never read as knowledge; it's just narrative framing
CodeCompass leaves untouched.

**An ordinary block of prose becomes a Claim — a plain, unclassified
factual statement.** Writing "the system currently does X" does not
itself constitute an observation of X, so CodeCompass never guesses
whether your statement expresses settled project intent or just an
unverified hypothesis about current behaviour; it stays genuinely
unclassified (`Provenance: UNCLASSIFIED`, no `basis` field at all) until
someone actually checks it and the record's classification is set
explicitly, by a human or an agent, during review.

**To mark a block as declared project intent instead** (not a factual
claim about current behaviour, but a statement of what *should* be
true), start it with its own line, exactly:

```
Type: Intent
The CLI should expose a --json flag for every reporting command.
```

**To propose a Requirement** rather than a Claim, the block must be
explicit and structured — merely mentioning an approved Decision's id
anywhere in ordinary prose is never enough on its own:

```
Type: Requirement
Decision: DEC-ARCH-003
Statement: The CLI must expose a --json flag for status output.
Example: Given the status command runs with --json, when output is
captured, then it is valid JSON matching the existing schema.
```

All four lines are required: a real, already-`approved` Decision id, a
clear statement, and an Example that actually reads like a Given/When/
Then acceptance scenario. CodeCompass never invents a Decision on your
behalf, and never fabricates a placeholder example to paper over a gap
— if the Decision doesn't resolve to something real and approved, or the
example isn't genuinely there, your proposal is preserved as an ordinary
Claim instead, never silently dropped.

**Editing this file does not make your statement true in CodeCompass's
own records until it has been reviewed and checked against evidence.** A
brand-new addition starts out unconfirmed — real, visible, and not yet
confirmed — because writing a sentence here is not the same thing as
CodeCompass having actually observed it.

**Submitting the same content twice never creates a duplicate record.**
Once your candidate text has been promoted into a real record, it is
removed from the live candidate region — a later `select-candidates` run
will not rediscover it, and re-running `apply` against a manifest that
has already succeeded is a safe no-op (it checks its own recorded state
first). Two separate candidate blocks with byte-identical text, anywhere
in the same file, are treated as one contribution by design.

## How changes are submitted and reconciled

Submit your edit as an ordinary Git commit or pull request — no special
submission channel. Before any of this, someone has to have run
`codecompass knowledge render [<slug>]` at least once — this is what
produces the editable projection in the first place, and it's also how
you (or anyone) refresh a projection's own prose by hand later, outside
the reconciliation flow below (reconciliation's own `apply` step never
re-renders on its own — a later `select-candidates` run, or an explicit
`render`, is what actually updates the Markdown file's wording).
Reconciliation itself then runs in three stages requiring a human/agent
decision, plus one purely mechanical step either side of them:

0. **Render** (`codecompass knowledge render [<slug>]`) — deterministic,
   no AI call, produces or refreshes the editable projection you edit.
1. **Detect** (`codecompass knowledge select-candidates <slug>`) —
   purely mechanical, no AI call, writes nothing to any canonical
   record. It compares two independent hashes for every anchor: one for
   the canonical record, one for the rendered projection — classifying
   every block in the whole projection *before* touching anything. If
   only the projection changed, your edit becomes a candidate for
   review. If only the canonical record changed (someone else reconciled
   a different edit), that one block is refreshed in place — targeted,
   block-by-block, never a wholesale rewrite of the file, so refreshing
   one block can never erase an unrelated pending edit sitting in
   another block of the same file. If **both** changed since you last
   saw this projection, that's a concurrent-change conflict: neither
   side is touched, and it's flagged for a human to look at.
2. **Review** — a human or an AI agent reads the resulting manifest,
   checks the proposed change against real evidence, and annotates it
   accept or reject. For a wording-only edit, review also marks it
   `presentation_only` — **this is a reviewer's own judgment call, never
   something `apply` mechanically proves** (checking whether two pieces
   of prose mean the same thing isn't something this project attempts
   to automate). This is the only stage where judgment is applied.
3. **Apply** (`codecompass knowledge apply <manifest>`) — the only step
   that writes a canonical record, and it never simply trusts the
   review's own say-so: it re-validates everything mechanically and
   re-checks that the canonical record hasn't moved again since
   detection. It's also idempotent — re-running `apply` against a
   manifest it has already processed is a safe no-op, checked first,
   before anything else.
4. **Render again** — run `codecompass knowledge render [<slug>]` once
   more to see the newly-reconciled wording reflected in the projection.

A rendered block showing accepted presentation wording always keeps the
record's own real canonical statement available too — as a machine-facing
HTML comment right above the visible prose, invisible to an ordinary
rendered-Markdown reader but present in the raw file any agent or
development-context consumer actually reads. Cached wording can diverge
from canonical meaning in how it *reads*, but it can never become the
only representation of what a record actually, canonically says.

## What happens when your edit disagrees with existing evidence

It stays visible, not silently discarded and not silently accepted. If
review finds your addition is unsupported, it stays marked as such until
real evidence is gathered. If it genuinely contradicts what's already
known, both sides are preserved and the disagreement is recorded
explicitly — CodeCompass never quietly picks a side to keep things
looking consistent.

## Editing ≠ immediate truth

To say it one more time, because it's the single most important rule
here: **editing this file does not make your statement canonical.**
Until reconciliation has checked it, your addition is visible and real,
but not yet confirmed. The reconciled `planning/knowledge/` corpus — not
any Markdown file, including this one — is CodeCompass's own source of
truth once reconciliation has run.

## Project documentation (README, CONTRIBUTING, etc.)

A documentation region can optionally cite the exact knowledge records
that ground it:

```markdown
<!-- codecompass-grounded-by: CL-ARCH-014, REQ-ARCH-002 region:sync-idempotency -->
### How sync handles idempotency
...ordinary, hand-authored prose...
<!-- /codecompass-grounded-by -->
```

This is **optional and per-region** — not every sentence needs one.
Where it's absent, nothing breaks — the region is just ordinary,
untracked prose, the same as any other documentation today.

The trailing `region:<id>` token is optional but recommended for any
marker you intend to keep long-term: it gives the region a **stable
identity** that survives you inserting or reordering content around it
later. A marker with no `region:` token still works, identified instead
by its position among grounded regions in the same file — fine for a
short-lived marker, fragile if you later add or move a region above it.
Two markers must never claim the same explicit `region:<id>` — detection
fails closed (loudly, non-zero exit) rather than silently picking one.

Where a grounding marker is present, that region genuinely participates
in reconciliation, in both directions — run
`codecompass knowledge doc-select-candidates`:

- **You edit the factual prose, the cited record doesn't change**: the
  edit becomes a real reconciliation candidate, written into the cited
  record's own slug and reconciled through the exact same review/apply
  path as any other knowledge edit. Reviewing it requires one more
  explicit call than an ordinary candidate: set the item's own
  `semantic_change` field to `false` if this is purely presentational
  (rewording, a typo fix — canonical knowledge is untouched, nothing new
  is created once applied) or `true` if it asserts something new about
  the system (a candidate Claim is created, never auto-promoted to
  verified truth, exactly like any other new candidate). This is always a
  reviewer's own judgment call — never something `apply` mechanically
  proves. Immediately before writing, `apply` re-verifies *both* the
  region's own text *and* every cited record's own content against what
  was true at detection time — either moving refuses the apply closed,
  the same concurrency protection an intermediate-document anchor edit
  already gets.
- **The cited record changes, the prose doesn't**: surfaced as
  "potentially stale, worth a look" — informational only, no manifest
  item, since there's a human judgment call about whether the prose
  still reads accurately, not a mechanical edit to reconcile. This stays
  flagged on every subsequent detection run until explicitly dismissed
  with `codecompass knowledge doc-acknowledge-stale <doc> <region>`
  (`<region>` being the region's own `region:<id>` value, or its
  positional index if it has none) — merely detecting the staleness again
  never clears it on its own.
- **Both change at once**: an explicit concurrent-change conflict,
  reported clearly; neither side is touched, the same as an intermediate-
  document conflict. This is never auto-resolved — it keeps being
  reported until the underlying facts genuinely change again.

When a semantic documentation edit is applied, the region's own marker is
updated to also cite the newly created Claim (`grounded-by: CL-OLD,
CL-NEW`) — the connection to prior knowledge is preserved, not dropped,
and the new Claim becomes discoverable from this region going forward.

**Detecting a change is never the same as acknowledging it.** None of the
three cases above, nor running `doc-select-candidates` itself, ever moves
a baseline on its own — the one exception is a region seen for the very
first time, where there's no prior state to lose by establishing one
immediately. A `doc_candidate` only advances its own baseline once
actually applied; a `claims_changed` finding only clears once explicitly
acknowledged.

`codecompass knowledge status` also reports a real, advisory-only
grounding-coverage summary: how many regions are grounded, how many
*changed* grounded regions there are, and — reusing the same heading-
based chunking `context-graph.db`'s own documentation tracking already
uses — how many *changed but ungrounded* regions exist, worth a look.
This, too, is never auto-cleared by merely looking — dismiss it
explicitly with `codecompass knowledge doc-acknowledge-chunks` once
you've actually reviewed the changes. None of this ever blocks anything,
and it never converts ungrounded prose into a canonical Claim on its own;
that always requires an explicit grounding marker and an explicit
reconciliation step.

## Phase knowledge packages

For a bounded piece of work, `codecompass knowledge render <slug>`
already produces a **phase knowledge package** — the relevant slug's own
`intermediate/` files, plus `phase-brief.md`: a single, mechanically-
compiled entry point (record counts and ids per category — concepts/
architecture, invariants/constraints, interfaces/behaviours, test
scenarios where any Requirement exists, open questions) linking into the
other files, never a separate representation of the same knowledge or a
narrative summary written on your behalf. Refine the underlying files
the same way you'd refine any other intermediate document — the
candidate-addition region is there for exactly this, on `phase-brief.md`
too.

## Using an AI coding tool

ChatGPT, Copilot, Claude Code, and a plain human editor all enter
through the exact same path described above — there is no special
"AI mode." Whichever tool writes the actual implementation code, the
knowledge layer reconciles the resulting project state the same way
regardless.
