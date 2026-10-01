# 0066. Clean-room conceptual understanding is published directly into documentation from one shared, correctly-schemaed knowledge foundation, isolated by a verified — and honestly limited — mechanism, not prompt discipline alone

## Status

Accepted (2026-09-30, direct user instruction). **Amended in place three
times, same date, direct user instruction each time.** Not yet acted upon
by any implementation until this fourth revision's own approval, so each
amendment through the third revision is a pre-implementation correction,
not a reversal of shipped work — edited directly rather than superseded
by a new numbered decision, consistent with `CLAUDE.md` §2's append-only
rule applying to decisions that have already informed real, executed
work. **This fourth revision corrects four further defects found in the
third**, approves the overall approach subject to those corrections, and
proceeds directly into implementation — see the dated addendum at the end
of the Decision section for what changed this time and why this is the
point past which the ADR's own content stops being purely pre-
implementation.

**Post-implementation note (2026-10-01): four defects found in the
shipped result are corrected by `decisions/0067`, a new ADR, not a fifth
in-place edit here** — per `0067`'s own reasoning, this ADR has already
informed real, executed, `done`-flipped work, so its own content below
is left exactly as the fourth revision wrote it.

## Context

`decisions/0060` formalized Scope → Plan → Domain → Design → Implement
and built `context-researcher`/`domain-skeptic`/a `docs/domain/` corpus
(Phase 63D) and a blank-slate documentation proposal (Phase 64), neither
mechanically isolated from the legacy narrative each was instructed to
disregard, and neither checked against a genuinely independent
implementation reconstruction.

**This decision's first version addressed both gaps but itself contained
six defects**, corrected the same day in a second version: it gated
publication on a separate, human-reviewed `understanding-review.md`
artifact; it risked a parallel documentation-only knowledge store; it
stated the wrong `Claim` status enum; it overclaimed a curated `.git`-free
export as sufficient isolation; it left `docs-reconstructor`'s old MODE 2
as a silent fallback and the result as a permanent shadow proposal; and
its template list still carried the removed review-gate artifacts.

**The second version itself contained six further defects**, found by
direct technical inspection (not assumption) before any implementation
began, corrected in this third revision:

1. **Isolation verification remained too weak, and its own completion
   criteria let a real gap through.** A single self-reported failed read
   of one absolute path is not proof of a boundary — the second version's
   own preflight design relied on exactly that. It also omitted three
   real routes: search (`Grep`/`Glob` can locate excluded content without
   knowing its exact path), command (arbitrary `Bash` can reach or reveal
   excluded content many ways), and — the most consequential omission —
   **network**. Omitting `WebFetch`/`WebSearch` from a role's tool grant
   does nothing to stop a granted `Bash` from reaching the network via
   `curl`/`wget`/a scripting language's own HTTP client. **Direct fact,
   confirmed, not assumed: CodeCompass is a public GitHub repository** —
   its own "excluded" `README.md`/`docs/`/`architecture/` content is
   reachable at a public URL regardless of any local filesystem
   isolation. The second version's own Definition of Done let a
   `best-effort` isolation label stand alongside an otherwise-complete
   phase report with no separate, load-bearing acknowledgment that
   strict clean-room validation had not actually been achieved.
2. **The pipeline was circular.** The second version's comparison stage
   required "the published Understanding documentation"; its writing
   stage required that same published documentation *and* the
   comparison's own output; its publication stage happened only after
   writing. The artifact both earlier stages needed did not exist until
   the very end of the same sequence they were supposedly feeding.
3. **Snapshots and propagation were underspecified.** No concrete
   snapshot artifact, citation format, or integrity mechanism was
   defined; propagation started from an assertion already identified by
   hand, never from a changed source file; the transitive-dependency walk
   had no stated cycle-safety.
4. **A dependency-validation claim was verified false.** Direct,
   empirical testing of `scripts/check_knowledge_base.py::parse_record`
   confirms its hand-rolled, line-oriented parser cannot see a YAML
   *block*-style list (`depends_on:` followed by indented `- ID` lines)
   — it silently parses an empty value, so a dangling reference written
   that way would never be caught. The *inline* `[ID, ID]` form (this
   project's own existing, universal convention for every list field
   today, confirmed by reading every real record) works correctly. The
   second version's own claim that `depends_on` "already validates with
   zero code change" was true only for the form nobody had tested against
   the alternative.
5. **Alignment and verification were conflated.** The second version let
   an `aligned` comparison finding automatically move a Claim's own
   `status` to `verified` — wrong for a domain rule or proposed policy,
   where implementation conformance shows only that the *code* currently
   matches the *stated* rule, never that the rule itself is correct.
6. **Only documentation was independently validated.** The second version
   demonstrated that propagation *reaches* a coding-context packet — a
   citation check — but never independently assessed whether that packet
   is actually accurate, sufficient, or honest about uncertainty for a
   real task, leaving the revised objective's own central claim (one
   foundation usefully serves both outputs) asserted rather than shown for
   the coding-context half.

Direct user instruction (2026-09-30, third revision): correct all six.
Full specification:
`planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`.

## Decision

1. **The Claim schema extension is unchanged in field set from the second
   version, with one addition: every list-valued field (`depends_on`
   included) is required to use the inline `[a, b]` form, and a new
   checker rejects the block-list form outright** (confirmed empirically
   to be otherwise invisible to validation). `scripts/
   check_knowledge_base.py` gains two checks — the closed-enum validator
   for `assertion_kind`/`basis`/`evidence_support_state`, and the new
   block-list rejection — plus a third, `check_snapshot_integrity` (item
   2, below). `--strict` passing covers all three.

2. **The circular "comparison and writing both require published
   documentation that doesn't exist yet" pipeline is replaced with a
   linear one, via a new intermediate artifact: a frozen knowledge
   snapshot.** Canonical assertions (adversarially reviewed by
   `domain-skeptic`, no human gate) are frozen into a versioned,
   citable snapshot — `planning/knowledge/<topic-slug>/snapshots/
   snapshot-v<N>.md` (human-readable: included/excluded assertion ids,
   source coverage) plus `snapshot-v<N>.yaml` (machine-checkable: each
   assertion's id, a SHA-256 hash of its own `.yaml` file's content at
   freeze time, its `repository_revision`/`timestamp`). Citation format:
   `<topic-slug>@v<N>#<assertion-id>`. A new `check_snapshot_integrity`
   check re-hashes each cited assertion's *current* content against what
   a snapshot recorded, catching a later mutation the versioning
   convention alone cannot prevent (no write-time enforcement exists or
   is added — this is a detection backstop, not a prevention mechanism,
   stated honestly). Independent implementation reconstruction, then
   comparison (against the snapshot, not undefined "published prose"),
   then documentation architecture selection and the first draft (also
   from the snapshot), then legacy reconciliation, then publication into
   real, active documentation — in that order, with no stage requiring an
   artifact a later stage produces. Understanding is incorporated
   directly into documentation exactly once, at the real end of this
   chain, not implied to already exist earlier in it.

3. **Isolation verification is strengthened to cover every real route,
   with an honest, load-bearing acknowledgment of a limit this project's
   available tools cannot close.** Required preflight probes now cover
   filesystem, search, command, network, and delegation routes, each
   checked via the dispatched agent's own **raw tool-call transcript**
   (never its self-reported prose summary), run in the exact dispatch
   configuration the real stage will use. **CodeCompass being a public
   repository means the network probe is expected to succeed** (i.e. the
   leak is real and open) for any role that needs `Bash`, since neither
   `Agent(isolation: "remote")` nor omitting named network tools
   constrains what a granted `Bash` can reach over the network. A stage
   is labelled `verified` only if **both** the filesystem/search/command
   probes and the network probe fail to reach excluded content;
   `filesystem-only, network-exposed` if only the network probe succeeds;
   `best-effort` — **always**, regardless of any single probe's
   incidental result — for Tier 2 (the same-host curated export, which
   provides no architectural guarantee regardless of what one test finds).
   **The Definition of Done is split into two explicitly separate,
   separately-reported tracks**: workflow/template completion (fully
   satisfiable) and strict clean-room isolation validation (honestly
   expected to remain **unmet**, per scope, for any role needing `Bash`)
   — removing the second version's own human-review gate must not, and
   does not, relax this second track into something that can be quietly
   folded into an overall "done" verdict.

4. **`implementation-reconstructor` and the extended `domain-skeptic`
   comparison role are unchanged from the second version, with one
   correction: alignment is not verification.** An `aligned`/`partial`/
   `conflicting`/`not_implemented`/`insufficiently_verified` comparison
   finding is recorded in the alignment report only and never
   automatically written back into a Claim's own `status`. Moving a
   Claim to `verified` requires a separate, claim-specific check against
   primary evidence, recorded on that Claim's own trail — a materially
   higher bar for a `rule`/`invariant`/`proposed_policy`-basis assertion,
   where implementation conformance alone never establishes the rule's
   own correctness.

5. **Propagation now starts from a changed source, not a manually-
   identified assertion, and is explicitly cycle-safe.** `Evidence`
   records' own `source_ref`/`doc_ref`/`test_ref` fields (simple scalar
   strings, confirmed reliably parseable) are `grep`ed for a changed
   file's own path to find affected Evidence; affected Claims follow via
   the existing `supporting_evidence`/`contradicting_evidence` citation.
   The transitive `depends_on` walk maintains a visited-id set, never
   re-queuing an id already seen — safe against a dependency cycle by
   construction, not by assumption. "Needs reassessment" and "proven
   incorrect" remain explicitly distinguished. **The demonstration runs
   in a disposable fixture** (a scratch copy of the topic's snapshot,
   packet, and documentation page, outside either repository's tracked
   tree), never against real canonical knowledge or real published
   documentation — the fixture is deleted once the demonstration is
   recorded, leaving no synthetic contradiction anywhere real.

6. **A new coding-context validation step is added, independent of and
   parallel to the documentation validation the second version already
   had.** A bounded, task-specific question is frozen before a real
   `context-packet.md` is generated from the *same* snapshot the
   documentation cites; a fresh `context-evaluator` dispatch independently
   assesses it against primary evidence using this project's own
   existing `context-quality-evaluation.md` rubric (Accuracy/Relevance/
   Completeness/Freshness/Grounding/Noise/Safety, plus a LOW/MODERATE/
   HIGH advantage rating) — not a new rubric. A LOW rating is an
   acceptable, honest outcome (this project's own established
   precedent); an inaccurate or unsupported packet is the real failure
   this step exists to catch.

7. **This is not Priority B; the template gets portable, CodeCompass-
   agnostic instructions; MIT licensing is preserved** — all unchanged
   from the second version.

### Fourth-revision addendum (2026-09-30, approved, proceeding to implementation)

Four further defects, found by direct inspection of the third revision
before implementation began, corrected here; the overall approach is
then approved and this same instruction proceeds directly into building
it:

8. **Snapshot integrity item 2, above, conflated three questions.**
   Hashing a cited assertion's *current, live* file and comparing against
   a freeze-time hash treats a legitimate lifecycle transition (the very
   next commit that supersedes or withdraws that same assertion, editing
   its own `status` field in place) as indistinguishable from tampering.
   **Corrected**: a snapshot's own hash is computed from `git show
   <repository_revision>:<path>` — the exact historical git blob — never
   the live file, and the snapshot's own sidecar preserves the full
   evidentiary chain (each cited Claim's `supporting_evidence`/
   `contradicting_evidence`/`derivation`, each with its own
   `repository_revision` and original `source_ref`/`doc_ref`/`test_ref`),
   not only the Claim's own hash. Three distinct checks replace the one:
   `check_snapshot_historical_integrity` (the historical git blob still
   matches the recorded hash — should always pass; a failure means
   tampering or rewritten history), `check_snapshot_current_divergence`
   (informational only: does the *current* live file still say the same
   thing — a legitimate supersession is expected to diverge here, without
   ever failing the first check), and evidence/source staleness named
   distinctly within that divergence report.
9. **The block-list checker (item 1, above) could be bypassed.** Direct
   re-review found it missed an intervening comment or blank line before
   the first list item, and an indentless block list (no leading
   whitespace on the `- item` lines, which its own `^\s+-\s` pattern
   never matches). **Corrected**: validate the *parsed field value*
   directly against the inline-form regex, rather than pattern-matching
   the raw YAML text for one named bad shape — this catches every
   representation the hand-rolled parser cannot reconstruct, uniformly,
   not only the one first found.
10. **The propagation demonstration (item 5, above) never actually
    exercised source-to-evidence discovery, a dependency cycle, or a
    snapshot-level citation** — it edited an assertion directly, the
    thing this revision's own item 5 added a discovery step specifically
    to avoid starting from. **Corrected**: the disposable fixture now
    includes a real source file, the Evidence record citing it, three
    assertions arranged in a genuine cycle (`A depends_on B depends_on A`),
    and a snapshot citing one of them — the demonstrated change is to the
    fixture's own source file, and the traversal is shown to discover the
    evidence, walk the cycle exactly once each ID (terminating, not
    looping), flag the snapshot, and reach both derived-output kinds.
11. **Two remaining statements were factually imprecise**, corrected
    directly: Phase 78 (still `planned`, never executed or evaluated) is
    removed from any list of phases whose real LOW-advantage results this
    decision cites as precedent (Phases 75 and 77 only); and every
    roadmap/context restatement of this ADR's own pipeline is reconciled
    to state plainly that independent implementation reconstruction is
    model-blind — it does not consume the snapshot at all — and that
    comparison and documentation writing are what consume it, afterward.

**The overall approach, corrected as above, is approved.** This same
instruction directs proceeding directly into implementation and
validation of the corrected phase, without a further planning-review
round-trip — the phase's own Definition of Done (§12 of the phase plan,
its two separately-reported tracks unchanged by this addendum) remains
the standard implementation is checked against.

## Alternatives considered

- **Accept a single-probe, self-reported isolation check as sufficient,
  since it at least tests something.** Rejected: this is precisely the
  gap this revision's own direct inspection found — a self-reported
  result is not independently checkable, and omits routes (search,
  command, network, delegation) a real adversarial reading of "prevent
  indirect narrative leakage" must cover.
- **Treat the public-repository network leak as out of scope, since this
  project cannot configure the underlying sandbox's own network policy
  anyway.** Rejected: not being able to *close* a gap is not a reason to
  omit *reporting* it — the corrected design probes for it explicitly and
  reports the resulting label honestly, including when that label is
  `filesystem-only, network-exposed` rather than `verified`.
- **Keep "published Understanding documentation" as comparison's and
  writing's own input, and simply reorder the sections without
  introducing a new snapshot artifact.** Rejected: the circularity is
  structural (an artifact both earlier stages need does not exist until a
  later stage produces it), not a presentation-order problem — a genuine
  intermediate artifact (the frozen snapshot) is required to break it.
- **Auto-promote to `verified` on any `aligned` finding, since it is
  simpler than a separate claim-specific check.** Rejected: this
  conflates two different questions (does the code match the stated rule;
  is the stated rule itself correct) that this project's own evidence-
  layer discipline (Knowledge sources / Project understanding /
  Implementation evidence, kept distinct throughout this whole phase) 
  requires to stay separate.
- **Demonstrate propagation against real canonical data, then restore it
  afterward.** Rejected in favour of a disposable fixture: restoration
  completeness is itself a real, avoidable risk (a botched revert leaves
  a synthetic contradiction in real knowledge or real published
  documentation), whereas a fixture that is simply deleted carries no
  such risk.

## Consequences

- Rewritten files: `planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  (third revision), this decision record (amended in place again), a new
  saved verbatim prompt file for this revision.
- `development-methodology.md` and `documentation-lifecycle.md`'s own
  forward-pointing amendment notes are updated to match (snapshot-based
  ordering; alignment-is-not-verification; the public-repository
  isolation finding).
- No `src/codecompass/` change. No `context-graph.db` schema change. No
  new database or graph subsystem.
- The phase's own implementation — `scripts/check_knowledge_base.py`'s
  four checker additions (`check_optional_enum_fields`,
  `check_list_fields_are_inline`, `check_snapshot_historical_integrity`,
  `check_snapshot_current_divergence`), the source-originating,
  cycle-and-snapshot-covering disposable-fixture propagation
  demonstration, and the coding-context validation step's own
  dispatches — **begins immediately following this fourth revision's own
  approval**, per this same instruction's own explicit direction not to
  request a further planning-review round-trip. **This decision's own
  honest expectation, stated for the record, is that strict clean-room
  isolation validation will likely remain unmet for at least the network
  dimension when this phase is actually executed** — a disclosed,
  accepted limitation of this project's currently available tools against
  a publicly-hosted repository, not a defect in this decision's own
  design, and not a reason to delay reporting the workflow/template
  track's own real completion separately.
