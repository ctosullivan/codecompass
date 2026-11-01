# Drift audit — Phase 84 final corrective amendment (`decisions/0093`)

**Scope:** commits `23f6826` (fix) and `085a68c` (docs/changelog/retro) only
— the two correctness fixes to `trace_evidence()` (Requirement indirect
evidence via `depends_on`, new `dangling_dependency_reference` gap kind)
and `find_gaps()` (`repo_root` threaded into `aggregate_contract()`/
`evaluate_result_precedence()` for `stale_test_citation`, qualified
wording). Audited against current-truth docs: `README.md`, `docs/**`,
`architecture/**` (none exist as a top-level dir in this repo; docs live
under `docs/architecture/`), `ai-docs/**`.

**Method:** read both commits' full diffs directly (`git show 23f6826`,
`git show 085a68c`); read the current, unmodified `epistemic_status()`
docstring and the modified `trace_evidence()`/`find_gaps()` docstrings in
`src/codecompass/knowledge_api.py`; read `docs/reference/cli.md`'s Phase
84 section in full; read `docs/architecture/overview.md` and
`docs/architecture/components.md`'s `knowledge_api.py` entries; grepped
`docs/`, `README.md`, `ai-docs/` for `trace_evidence`, `find_gaps`,
`depends_on`, `stale_test_citation`, `missing_evidence`,
`supporting_evidence`, `contradicting_evidence`, `dangling_evidence_
reference`, `dangling_dependency_reference`; read `planning/CONTEXT.md`'s
current Phase 84 section; read `decisions/0093` in full for the
authoritative statement of what each fixed function is now meant to do
and how it relates to `epistemic_status()`. No `git stash` or any
tree-mutating command was used — only `git show`/`grep`/`Read`.

## Verdict: DRIFT — 2 findings (both non-blocking)

No current-truth doc makes a statement about the amended behaviour that
is now **false**. The two findings below are completeness gaps in an
existing itemized enumeration and a currently-stale-but-separately-
reconciled session file — neither misleads a reader into believing
something incorrect about current behaviour.

### Finding 1 (non-blocking) — `docs/reference/cli.md:204-212`, `gaps` bullet omits the new `dangling_dependency_reference` gap kind

The `- **\`gaps [SLUG]\`** —` bullet (lines 204-212) itemizes the specific
gap kinds `find_gaps()` can return: unverified required oracle scope,
contradicted record, stale test-evidence citation, **dangling evidence
reference** (named explicitly, with `decisions/0092` cited — added
during the *prior* corrective pass specifically to document that gap
kind once it was introduced corpus-wide), and missing oracle contract.

`find_gaps()` now also performs a corpus-wide `dangling_dependency_
reference` scan (`23f6826`, new code block right after the existing
`dangling_evidence_reference` scan: "an equivalent corpus-wide scan
added to `find_gaps()`" per the function's own updated docstring and
`decisions/0093` Consequences section). This is a new, named, user-
visible gap kind a plain `codecompass knowledge gaps` call can now
surface — and the bullet's own established editorial pattern (itemize
each kind by name, cite the ADR that introduced it) was exactly followed
for `dangling_evidence_reference` one pass ago. Omitting the new kind
here is inconsistent with that established pattern and leaves the
bullet's own enumeration incomplete as of this amendment.

Not misleading on its own terms — the bullet never claims to be
exhaustive, and nothing it says about the kinds it does list is false —
so this is completeness, not misdescription. Suggested fix (for
`docs-maintainer`, not performed here): append a clause parallel to the
existing `dangling_evidence_reference` one, e.g. "...or a dangling
`depends_on` reference (`dangling_dependency_reference`,
`decisions/0093`)."

### Finding 2 (non-blocking, explicitly reconciled separately per task) — `planning/CONTEXT.md:10-74`

The current Phase 84 section describes the system exactly as of the
*first* corrective pass (`decisions/0091`/`0092`, 2026-10-29) — the
"Independently re-audited" closing paragraph (lines 64-74) references
only that pass's own audit and drift-audit reports and promoted
learnings (`L-108`/`L-109`). There is zero mention of `decisions/0093`,
the Requirement indirect-evidence fix, the new
`dangling_dependency_reference` gap kind, or the `find_gaps()`
`repo_root`-threading fix for `stale_test_citation`. Confirmed by
`git show 085a68c --stat`: that commit touched `CHANGELOG.md`, the plan
file, and the retro file only — not `planning/CONTEXT.md`.

Per the task framing this is non-blocking and reconciled separately (the
`roadmap-context-curator`'s own step); flagging only so it isn't missed
at that reconciliation.

## Checked and found accurate (no finding)

1. **`docs/reference/cli.md:194-203`, `trace` bullet.** Still accurate:
   "`--evidence` instead runs `trace_evidence` (supporting + contradicting
   evidence, reporting an explicit gap when an obligation-bearing record
   has no evidence at all, or when a declared citation doesn't resolve to
   a real record — `dangling_evidence_reference`, `decisions/0092`)."
   This is written as a general, non-exhaustive description (one example
   gap kind named parenthetically, not an itemized list the way the
   `gaps` bullet is), and every clause remains literally true after the
   amendment — a Requirement's "no evidence at all" now correctly checks
   indirect evidence too, but the bullet's own wording doesn't claim
   otherwise either way. Judged as reasonable generality, not a gap:
   adding "(or indirectly, for a Requirement, through its `depends_on`
   Claims)" would be nice-to-have, not required to keep this sentence
   true. Not raised as a finding.

2. **`docs/reference/cli.md:204-212`, "a different, currently-passing
   result... exists in `S`'s own results/ directory" phrasing re:
   `stale_test_citation`.** The bullet's looser "current `PASS`" language
   doesn't carry the new "live-reconfirmed vs. contract-relative-only"
   distinction the fixed `reason` string now states explicitly. This
   imprecision is pre-existing (the underlying `repo_root`-drop bug this
   amendment fixes predates this diff; the doc's own looseness was never
   tied to that bug one way or the other) and not newly introduced or
   newly falsified by this amendment — the bullet never claimed the
   "current PASS" was unconditionally live-confirmed, so nothing it says
   is now wrong, only slightly less precise than the underlying code now
   is. Not raised as a finding.

3. **`docs/architecture/overview.md:10,18` and
   `docs/architecture/components.md:36` — `knowledge_api.py` entries.**
   Checked specifically for (a) any claim that Requirements and Claims
   are treated identically for evidence purposes, and (b) any claim this
   amendment falsifies about read-only-ness, logical-vs-physical
   consolidation, or the consistency envelope. Found neither. Both
   entries describe the module at the level of: no new database, no new
   persisted identifier, no mutation path; reuses `knowledge_
   intermediate.py`/`oracle.py`'s existing functions *unmodified*; a
   result/check is `current` only once positively reconfirmed against a
   live checkout. All of these remain true post-amendment — confirmed
   directly against the diff and `decisions/0093`'s own Consequences
   section ("No change to `oracle.py`, `graph.py`, or
   `knowledge_intermediate.py`"). Neither doc makes any claim at all
   about how Requirement vs. Claim evidence resolution differs, so there
   is nothing for this amendment to falsify there.

4. **Grep sweep** — `trace_evidence`, `find_gaps`, `depends_on`,
   `stale_test_citation`, `missing_evidence`, `supporting_evidence`,
   `contradicting_evidence` across `docs/`, `README.md`, `ai-docs/`.
   Hits beyond `docs/reference/cli.md` (already covered above):
   - `docs/concepts/knowledge-model.md:31` — describes
     `knowledge_intermediate.py::derive_epistemic_profile` reading
     `depends_on`/`evidence_support_state`/`contradicting_evidence` for a
     Claim or Requirement, and states it is "not yet exposed through any
     `codecompass` CLI surface — library-only as of Phase 82." This
     function is unchanged by this amendment (confirmed: `trace_
     evidence()`'s new code does not call `derive_epistemic_profile`; it
     reuses only the *selection pattern* `epistemic_status()` already
     established, per `decisions/0093`). Whether this sentence is itself
     stale regarding Phase 84's own `epistemic_status()` CLI wiring is a
     **pre-existing question from Phase 84 itself**, unrelated to and
     unaffected by this amendment's diff — out of scope here, not raised
     as a finding of this audit.
   - `docs/architecture/data-and-control-flow.md:34,37` — `depends_on_
     edges`, the context-graph's own mechanically-detected edge table
     (a different concept from the knowledge-record `depends_on` field
     this amendment touches). Unrelated, unaffected.
   - `docs/workflows/knowledge-reconciliation-loop.md:30` — describes a
     competing Claim's `depends_on` field citing the original record
     under the `knowledge apply` mutation workflow, a different code
     path (`knowledge_intermediate.py`'s apply logic, not `knowledge_
     api.py`) not touched by this diff. Unrelated, unaffected.
   No reference to `dangling_evidence_reference`/`dangling_dependency_
   reference` exists anywhere outside `docs/reference/cli.md` and the
   source file itself.

5. **`epistemic_status()`'s own (unmodified) docstring vs.
   `trace_evidence()`'s new docstring — mutual consistency.**
   `epistemic_status()` (unmodified, `src/codecompass/knowledge_api.py`
   lines ~1239-1246): "For a Requirement (which has no
   `supporting_evidence` field of its own), the profile is computed per
   dependent Claim (its own `depends_on`) and the verified/gap/
   unconfirmed scope lists are unioned — a Requirement's own evidence is
   always indirect, through the Claims it depends on." `trace_evidence()`
   (amended) states the identical underlying fact — a Requirement has no
   `supporting_evidence` field, its evidence is always indirect through
   `depends_on` — and then goes further to state the two functions ask
   deliberately different questions: `epistemic_status()` decides "is
   this scope actually, oracle-confirmed, verified" (reusing `derive_
   epistemic_profile`); `trace_evidence()` decides the narrower "does
   citable evidence exist and resolve at all" (walking `depends_on`
   directly, never calling `derive_epistemic_profile`). These are
   consistent, not contradictory — confirmed directly against
   `decisions/0093`'s own "Consequences" section, which states exactly
   this division of labour as a deliberate, reviewed design point ("kept
   the three functions semantically consistent without duplicating
   validation logic"). No drift between the two docstrings.

## Scope note

Checked: both commits' full diffs; every docstring the diff touched
(`Gap.kind` comment, `trace_evidence()`, `find_gaps()`) plus the one
unmodified docstring (`epistemic_status()`) whose consistency with the
amended ones the task specifically asked about; `docs/reference/
cli.md`'s full Phase 84 section; `docs/architecture/overview.md` and
`docs/architecture/components.md`'s `knowledge_api.py` entries; a grep
sweep of `docs/`, `README.md`, `ai-docs/` for every term named in the
task; `planning/CONTEXT.md`'s current Phase 84 section; `decisions/0093`
in full as the authoritative rationale source.

Deliberately not re-audited: anything already covered and closed by the
*prior* drift audit (`planning/retros/_drift-audit-phase-84-corrective-
pass.md`, `decisions/0092`) that this amendment's diff does not touch —
e.g. the `ConsistencyEnvelope` fail-closed-default fix, the `get_
context_packet()` bounding fix, and the `--repo-root` live-reconfirmation
semantics for `get`/`context` are unaffected by `23f6826`/`085a68c` and
were not re-checked here beyond confirming (grep sweep above) that
nothing in this amendment's diff contradicts what those docs already say
about them. `planning/phase-84-consolidated-knowledge-api.md` and
`planning/retros/phase-84-consolidated-knowledge-api.md` (both touched by
`085a68c`) are plan/retro files, not current-truth docs under this
audit's own remit (`README.md`/`docs/`/`architecture/`/`ai-docs/`
per `CLAUDE.md` §5) — read for context only, not audited as drift
targets in their own right.

## Follow-up (2026-11-02, lead)

Finding 1 (above) fixed: `docs/reference/cli.md`'s `trace`/`gaps`
bullets now mention `dangling_dependency_reference` and the Requirement
indirect-evidence behavior, citing `decisions/0093`. Confirmed via
`scripts/check_user_docs.py --strict` (exit 0, no findings) and
independently re-checked by the `release-phase-auditor`'s own
same-amendment re-audit (`planning/retros/_audit-phase-84.md`'s "FINAL
CORRECTIVE AMENDMENT RE-AUDIT" section, item 6). Finding 2
(`planning/CONTEXT.md` staleness) is addressed separately in the
terminal `roadmap-context-curator`-style reconciliation commit. This
file's own verdict line above is left as originally written
(`DRIFT -- 2 findings, both NON-BLOCKING`), describing this audit's own
state *at the moment it was written*, per this phase's own established
append-only correction convention -- not re-run to a fresh `NO DRIFT`
verdict, since both findings are independently confirmed fixed by other
means above.
