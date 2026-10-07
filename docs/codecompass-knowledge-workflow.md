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

- **Provenance** tells you where this came from: `OBSERVED` (grounded in
  real, reproducible research), `DECLARED` (a maintainer's stated
  intent), `DECIDED` (authorised by an approved decision), `DERIVED`
  (reasoned from evidence), or `HISTORICAL` (superseded, kept for its
  own record).
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

To propose a **Requirement** rather than a general **Claim**, cite an
existing, already-approved Decision id explicitly in your own text (for
example, "per DEC-ARCH-003"). CodeCompass never invents a Decision on
your behalf — if you don't cite a real, approved one, your addition
becomes a Claim instead, never rejected outright.

**Editing this file does not make your statement true in CodeCompass's
own records until it has been reviewed and checked against evidence.** A
brand-new addition starts out unconfirmed — real, visible, and not yet
confirmed — because writing a sentence here is not the same thing as
CodeCompass having actually observed it. Writing "behaviour X exists"
does not itself constitute an observation of behaviour X.

## How changes are submitted and reconciled

Submit your edit as an ordinary Git commit or pull request — no special
submission channel. Reconciliation then runs in three distinct stages:

1. **Detect** (`codecompass knowledge select-candidates <slug>`) —
   purely mechanical, no AI call, writes nothing to any canonical
   record. It compares two independent hashes for every anchor: one for
   the canonical record, one for the rendered projection. If only the
   projection changed, your edit becomes a candidate for review. If only
   the canonical record changed (someone else reconciled a different
   edit), your projection is safely, automatically refreshed — no review
   needed. If **both** changed since you last saw this projection,
   that's a concurrent-change conflict: neither side is touched, and
   it's flagged for a human to look at.
2. **Review** — a human or an AI agent reads the resulting manifest,
   checks the proposed change against real evidence, and annotates it
   accept or reject. This is the only stage where judgment is applied.
3. **Apply** (`codecompass knowledge apply <manifest>`) — the only step
   that writes a canonical record, and it never simply trusts the
   review's own say-so: it re-validates everything mechanically and
   re-checks that the canonical record hasn't moved again since
   detection.

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
<!-- codecompass-grounded-by: CL-ARCH-014, REQ-ARCH-002 -->
### How sync handles idempotency
...ordinary, hand-authored prose...
<!-- /codecompass-grounded-by -->
```

This is **optional and per-region** — not every sentence needs one.
Where it's present, a change to the cited record can be traced straight
back to the documentation region it affects, and a factual edit to that
region is traced back to the records it should be reconciled against.
Where it's absent, nothing breaks — the region is just ordinary,
untracked prose, the same as any other documentation today.

`codecompass knowledge status` reports a small, purely advisory
grounding-coverage summary (how many regions are grounded, and whether
any grounded region cites a record that's since become contradicted or
unresolved) — it never blocks anything and never rewrites your
documentation on its own.

## Phase knowledge packages

For a bounded piece of work, the same projection mechanism produces a
**phase knowledge package** — the relevant slug's own `intermediate/`
files, plus a `phase-brief.md` summarising feature intent, domain
terminology, edge cases, invariants, existing/desired behaviour,
compatibility constraints, affected interfaces, test scenarios,
acceptance behaviour, and open questions. Refine it the same way you'd
refine any other intermediate document — the candidate-addition region
is there for exactly this.

## Using an AI coding tool

ChatGPT, Copilot, Claude Code, and a plain human editor all enter
through the exact same path described above — there is no special
"AI mode." Whichever tool writes the actual implementation code, the
knowledge layer reconciles the resulting project state the same way
regardless.
