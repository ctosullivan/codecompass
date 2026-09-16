# Baseline run — `tag:` query semantics brief (no CodeCompass reference-ingestion)

Produced following `.claude/agents/hledger-researcher.md`'s own real
process, exactly as documented (read the manual, consult the pinned
local source if the manual is ambiguous), with **no CodeCompass
ingestion or query involved at all** — this is the workflow Ledgerkit's
own `hledger-researcher` role already uses today. Read-only: not
committed to the real Ledgerkit repository.

## Step 1 — read the manual (live `WebFetch`, `https://hledger.org/1.52/hledger.html#queries`)

Prompted: "Find and return the section that documents the `tag:` query
term syntax... the infix-matching rule, and any tag-inheritance rules."

**Result** (verbatim from the live fetch):

> Syntax Form: `tag:.=202[1-3]` (an example), implying the pattern
> `tag:NAMEREGEX[=VALREGEX]`.
> Matching Behavior: hledger's regular expressions are "infix matching."
> Tag Inheritance Rules: "Postings inherit tags from their account,"
> "Postings inherit tags from their transaction," "Transactions also
> acquire the tags of their postings."

**Friction, recorded honestly**: this is *usable but imprecise*. It
correctly conveys the syntax shape and the infix-matching rule, but:

- It never surfaces the formal `### tag: query` section's exact
  `tag:NAMEREGEX[=VALREGEX]` heading, the `^`/`$` complete-match
  escape hatch, or the `tag:.=VALREGEX` value-only-matching shortcut.
- It **omits the account-level inheritance rule entirely** ("Accounts
  also inherit the tags of their parent accounts") — a real correctness
  gap: a real compat-register entry needs this rule to describe
  `matchesAccountExtra`'s behaviour, and the live-fetch summary simply
  doesn't mention it.
- The fetch is a WebFetch-summarized answer (an AI model's own
  paraphrase of the page), not the manual's own exact wording — a
  `hledger-researcher` brief that quoted this directly would be quoting
  a paraphrase of a paraphrase, one step removed from what the manual
  actually says.

## Step 2 — manual ambiguous on inheritance precision, consult the pinned local source

`grep -n "tag:" hledger/hledger.1` (the pinned local clone,
`/home/cormac/projects/hledger`, confirmed at commit
`33fa849e7ae841968bd21c427094c4fb4a4ec38d`) locates the formal section
at `hledger.1:7372-7392` — full text, exact wording, all three
inheritance rules present and precise. `grep -n "Tag\b" hledger-lib/Hledger/Query.hs`
locates `parseTag` (`Query.hs:482-487`), `matchesAccountExtra`'s `Tag`
case (`Query.hs:896`), `matchesPosting`'s `Tag` case (`Query.hs:921-924`),
`matchesTransaction`'s `Tag` case (`Query.hs:968-972`), and
`patternsMatchTags`/`matchesTag` (`Query.hs:1008-1024`).

## Resulting brief

**Target behaviour**: `tag:NAMEREGEX[=VALREGEX]` matches by tag name,
optionally also by tag value, using infix (not anchored) regex matching
on both. `tag:.=VALREGEX` matches by value alone. `payee:`/`note:` are
implemented as synthetic tag names inside the same `Tag` query
constructor (`Query.hs:921-924`, `968-972`), not separate query types —
worth noting since Ledgerkit's own `payeeTag`/`noteTag` may need the
same synthetic-name framing (not confirmed against Ledgerkit's real
`ledgerkit/query/` implementation in this baseline run — out of scope
for a doc/reference-only brief; `compat-differential-tester`'s job).

**Inheritance** (the part the manual's live-fetch summary got wrong):
accounts inherit their parent accounts' tags; postings inherit their
account's and their transaction's tags; transactions acquire their
postings' tags — a three-way propagation, not the two-way relationship
the WebFetch summary described.

**Evidence** (in the exact shape a real `LK-COMPAT-QUERY-TAG-001.yaml`
entry would need):

```yaml
evidence:
  - kind: manual
    ref: "https://hledger.org/1.52/hledger.html#tag-query (hledger.1:7372-7392)"
    pinned_at: "1.52.4"
  - kind: source
    ref: "hledger-lib/Hledger/Query.hs:482-487 (parseTag), 896 (matchesAccountExtra), 921-924 (matchesPosting), 968-972 (matchesTransaction), 1008-1024 (patternsMatchTags/matchesTag)"
    pinned_at: "1.52.4 (commit 33fa849e7ae841968bd21c427094c4fb4a4ec38d)"
```

**Proposed classification**: `compatible` or `unsupported`, pending
confirmation of what Ledgerkit's own `ledgerkit/query/` subpackage
currently implements for `tag:` (not checked in this baseline run —
Ledgerkit's Stage C row already states `tag:` is deferred, i.e. not yet
implemented at all, which would make this `LK-UNSUP-QUERY-TAG-001`, not
`LK-COMPAT-...` — a `hledger-researcher` brief would confirm this
against `ledgerkit/query/parser.py` directly before choosing).

## Time / effort

Two tool calls (one `WebFetch`, one local `grep` follow-up) plus direct
`Read` of the two exact line ranges surfaced. No CodeCompass command
run at any point in this baseline.
