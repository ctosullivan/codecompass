# Phase 79 — Clean-room conceptual understanding + documentation reconstruction (methodology hardening + template delivery)

**Status: amended a fifth time, 2026-10-01, implementing four further
corrections identified by direct review of the `done`-flipped result**
(fail-closed snapshot validation, restored documentation citations, a
corrected isolation verdict, and a real downstream template usability
exercise — full detail in §0's new "Fifth revision" entry below). The
phase's own prior terminal reconciliation (flipping it to `done` on
`planning/ROADMAP.md`) is not reopened or reversed by this amendment —
these are corrections to that already-`done` phase's own output,
following the same amend-and-implement-directly pattern this phase has
used throughout, not a reopening of the phase itself. A sixth-step
re-audit against this amendment's own final commit is still pending as
of this status line (see "Next step" at the end of §0).

Independent `release-phase-auditor` completion audit found three real
Track 1 (workflow/template completion) gaps against `cbf3582`
(`planning/retros/_audit-phase-79.md`); all three fixed (`d9b9175`); a
re-audit (`planning/retros/_audit-phase-79-reaudit.md`) returned Track 1
PASS; its own "Track 2 PASS" language is corrected by the fifth revision
(see below) to **Track 2: UNMET**, reported separately and unaffected by
Track 1.

Direct user request, 2026-09-30, amended four times (first three same
day/the following day; a fifth amendment the day after that, following
direct review of the delivered result). Full initiating prompts saved
verbatim:
`planning/phase-79-clean-room-understanding-and-documentation-reconstruction-prompt.md`
(original),
`planning/phase-79-clean-room-understanding-and-documentation-reconstruction-amendment-prompt.md`
(second revision),
`planning/phase-79-clean-room-understanding-and-documentation-reconstruction-second-amendment-prompt.md`
(third revision),
`planning/phase-79-clean-room-understanding-and-documentation-reconstruction-third-amendment-prompt.md`
(fourth revision), and
`planning/phase-79-fifth-amendment-prompt.md` (this revision). Governing
ADR: `decisions/0066` (amended in place a fourth time, this date — its
own fifth-revision addendum records the same four corrections).

**Revised objective, unchanged from the second revision**: *one
evidence-backed knowledge foundation supplies both coding context and
project documentation, with conceptual understanding incorporated
directly into the documentation and mechanical context separation
preserved.* No separate understanding-review artifact or human-
acceptance gate exists. This revision fixes six further defects the
second revision itself still contained, found by direct technical
inspection before any implementation began.

---

## 0. What changed in this revision, and why (read this first)

**Fifth revision (2026-10-01) — four corrections found by direct review
of the fourth revision's own `done`-flipped result, approved to proceed
directly into implementation, no further planning round-trip:**

1. **Snapshot validation still did not fail closed** (§5.3, the fourth
   revision's own fix was incomplete): `check_knowledge_base.py`'s
   historical-integrity/current-divergence checks only ever validate
   entries already *present* in a snapshot's own `assertions` table — a
   sidecar reduced to nothing but its own `snapshot_id` iterates zero
   entries and reports zero findings, indistinguishable from a genuinely
   complete, small snapshot. Fixed by a new `check_snapshot_completeness`
   function validating what the fourth revision's design never checked:
   required top-level metadata and types, that `assertions` is present as
   a table, that every real Claim existing at the snapshot's own freeze
   revision (checked against the historical `git ls-tree` listing at
   `repository_revision_at_freeze`, never the live filesystem — a
   snapshot frozen before a later Claim existed must never be flagged for
   lacking it) has a captured entry unless named in `excluded_assertions`,
   that each captured entry's own `path` resolves to a record whose real
   `id` matches the key it's filed under, and that each captured
   assertion's own historical `supporting_evidence`/
   `contradicting_evidence`/`derivation` citations are each present as a
   nested snapshot entry — closing exactly the "remaining hashes still
   validate" gap named. Every malformed-input path produces a `Finding`,
   never an exception. 13 new disposable-git-fixture tests.
2. **Published documentation never actually cited the frozen knowledge
   foundation** (§11, a gap in how §9's publication step was executed,
   not a defect in the plan's own design): the clean-room draft's own
   inline `first-party-source-symbols@v2#CL-FPSS-NNN` citations were
   lost when `docs-maintainer`'s legacy-reconciliation pass merged the
   draft's content into the existing `architecture/overview.md`/
   `architecture/context-graph-schema.md` pages — the merge preserved the
   prose but dropped every citation. Fixed by restoring a citation (with
   a navigable relative link to the real backing Claim record) at every
   point in both pages tracing to a specific assertion, including the two
   newly-documented limitations; every citation verified to resolve to a
   real file and an actual snapshot-v2 member.
3. **The closeout's own isolation verdict conflated honest labelling with
   strict isolation being achieved** (§6, a reporting defect, not a
   design defect — the plan's own §6.5 rule, "Tier 2 is always
   best-effort," was never violated in substance): both the original and
   re-audit reports said "Track 2 (strict clean-room isolation
   validation): PASS." That phrasing reads as isolation having succeeded;
   what had actually been verified was that the dispatches' own honest
   `best-effort` self-labelling held. Fixed in two parts: (a) the
   evidentiary basis itself was thin — the persisted Tier 1 preflight
   record was the probe dispatch's own prose handback, and no
   per-dispatch manifest, raw transcript, or independent boundary check
   existed for any of the six isolation-sensitive pilot dispatches beyond
   that one probe. This session's own original dispatch transcripts were
   still present on local disk (not rerun, not reconstructed); a real,
   mechanical boundary-check script was built and run against all six,
   recovering genuine access-log evidence that did not exist before —
   finding, among other things, a real boundary deviation in one
   dispatch (the coding-context packet-assembly step read two files
   outside its stated scope) that the original prose-only evidence had no
   way of catching. (b) The verdict language itself is corrected
   wherever it appeared (both audit reports via a non-destructive notice
   at the top, preserving their original text as historical record;
   `planning/CONTEXT.md`/`planning/ROADMAP.md`'s own current-state
   narrative, rewritten directly) to **Track 2: UNMET** — reported
   separately from, and unaffected by, Track 1's own real PASS.
4. **The template usability exercise never actually exercised the
   template** (§11's own closeout step): a fresh-clone link-integrity
   check confirms every markdown path resolves, which says nothing about
   whether a real adopter could actually follow the instructions. Fixed
   by dispatching a fresh, context-free agent with only the current
   template clone and a small invented, non-CodeCompass project (a tiny
   todo-list CLI with one genuinely non-obvious design decision),
   instructed to actually adopt and use the template end to end. This
   found and fixed a real defect (the adoption instructions' "copy its
   contents into an existing one" silently collides with two files any
   real project already has — its own `README.md`, replaced with a
   description of the template instead of the project, and `LICENSE`, a
   real per-project choice) and surfaced a genuine, inherent tension
   (freezing a snapshot requires a commit; the exercise's own no-commit
   rule meant one record was honestly left partially frozen rather than
   given a fabricated revision) that no link-checker could ever have
   found. Full exercise report and the complete adopted-project tree
   preserved as checkable evidence, not just narrated.

**Next step**: a fresh `release-phase-auditor` pass against this
amendment's own final commit, then `roadmap-context-curator`
reconciliation updating `planning/ROADMAP.md`'s Phase 79 row,
`planning/CONTEXT.md`'s current-state section, and this file's own
Status line to reflect the amendment's own completion — the same
closeout sequence the fourth revision itself used, applied again to this
fifth revision's own result.

---

**Fourth revision (2026-10-01) — four corrections, approved to proceed
directly into implementation, no further planning round-trip:**

1. **Snapshot integrity conflated three questions** (§5.3): hashing a
   cited assertion's *current, live* file treated a legitimate
   supersession/withdrawal (which legitimately edits that same file's own
   `status` field in place) as indistinguishable from tampering. Fixed by
   hashing the exact historical `git show <repository_revision>:<path>`
   blob instead of the live file, preserving the full evidentiary chain
   (Evidence/Derivation, their own revisions and original source
   locators — not just the Claim), and splitting one check into three:
   historical-content integrity (should always pass), current-record
   divergence (informational, expected over time), and evidence/source
   staleness named distinctly within it.
2. **List validation did not fail closed** (§4.2): the block-list
   detector missed an intervening comment/blank line and an indentless
   list (no leading whitespace, which its own pattern never matched).
   Fixed by validating the *parsed field value* directly against the
   inline-form regex, uniformly, rather than pattern-matching the raw
   text for one named bad shape.
3. **The propagation demonstration never exercised source-to-evidence
   discovery, a cycle, or a snapshot citation** (§10.4): it edited an
   assertion directly. Fixed: the fixture now includes a real source
   file, its citing Evidence, three assertions in a genuine dependency
   cycle, and a snapshot citing one of them — the change is to the
   fixture's own source file, and the traversal is shown to discover the
   evidence, terminate on the cycle, flag the snapshot, and reach both
   derived-output kinds.
4. **Two statements were factually imprecise**: Phase 78 (still
   `planned`, never executed or evaluated) removed from the LOW-advantage
   precedent list (§9.4); every roadmap/context restatement of the
   pipeline corrected to state implementation reconstruction is
   model-blind and does not consume the snapshot, which comparison and
   writing consume only afterward.

**Third revision (2026-09-30) — six corrections, on top of the second
revision, made before any implementation began:**

1. **Isolation verification was too weak and its completion criteria let
   a real gap through.** A single self-reported failed read is not proof
   of a boundary. This revision requires multiple, independently-checked
   preflight probes (filesystem, search, command, network, delegation),
   confirms Tier 2 is *always* `best-effort` regardless of any one
   probe's outcome, and — the most consequential finding of this
   revision — **establishes that CodeCompass is a public GitHub
   repository, so network egress alone (regardless of filesystem
   isolation) can reach the "excluded" narrative documentation at its
   public URL.** Strict clean-room validation is now explicitly
   separated from workflow/template completion, and is very likely to
   remain **unmet** rather than quietly declared satisfied (§6, §12).
2. **The pipeline was circular.** Comparison (§7, old numbering) required
   "published Understanding documentation," documentation writing (§8)
   also required that same published documentation, and publication (§8.4)
   happened only after writing — meaning the input both earlier stages
   needed did not yet exist. Replaced with a linear chain: canonical
   assertions → a **frozen knowledge snapshot** (new, §5) → independent
   implementation reconstruction → comparison → documentation
   architecture/draft (consuming the snapshot, not prose that doesn't
   exist yet) → legacy reconciliation → publication. Understanding is
   still incorporated directly into the final published documentation —
   it just happens once, at the real end of the chain, not implied to
   already exist at the start of it.
3. **Snapshots and propagation were underspecified.** §5 now defines the
   exact snapshot artifact (per-assertion id, content hash, repository
   revision, timestamp), its citation format, and a mechanical integrity
   check that later record mutations cannot silently invalidate what an
   earlier snapshot represented. Propagation (§10) now covers the step
   the second revision skipped — finding which Evidence/assertions a
   changed *source file* actually touches in the first place, not only
   walking forward from an assertion already identified by hand — and
   makes the transitive-dependency walk explicitly cycle-safe.
4. **The dependency-validation claim was wrong, verified empirically.**
   Direct testing (not assumption) confirms `scripts/
   check_knowledge_base.py`'s hand-rolled parser is blind to a YAML
   *block*-style list (`depends_on:` followed by indented `- ID` lines)
   — it silently sees an empty value and finds zero ids to check,
   meaning a dangling dependency written that way would never be caught.
   The inline `[ID, ID]` form (this project's own existing, universal
   convention for every list field today) is correctly validated. This
   revision requires the inline form and adds a new check that rejects
   the block form outright, rather than repeating the false claim that
   `depends_on` already validates with zero code change (§4.2).
5. **Alignment and verification were conflated.** The second revision let
   an `aligned` comparison finding automatically move a Claim's own
   `status` to `verified`. This is wrong for anything whose `basis` is a
   domain rule or a proposed policy: implementation conformance shows the
   *code* currently matches the *stated* rule, never that the rule itself
   is the right one. `verified` now requires its own claim-specific,
   independently-checked verification action, never an automatic
   byproduct of the broader comparison pass (§7.3).
6. **Only documentation was validated — coding context was not.** The
   second revision demonstrated propagation *reaches* a coding-context
   packet, but never independently assessed whether that packet is
   actually accurate, sufficient, or honest about uncertainty for a real
   task — the citation appearing in both places is not, by itself,
   evidence the shared foundation supplies *useful* task context. A new
   §9 freezes a bounded coding-context task, generates a real packet from
   the same snapshot the documentation uses, and independently assesses
   it with the same rubric this project already uses for exactly this
   question (`context-quality-evaluation.md`'s LOW/MODERATE/HIGH
   advantage rating) — reused, not reinvented.

Everything not named above (the schema's field set, the
`implementation-reconstructor` role, the draft-before-reconciliation
ordering, the Priority-B boundary, the removed human-review gate, the
validation topic) carries forward from the second revision, corrected
where this list says so.

## 1. Verified current state (re-checked live for this revision)

- **CodeCompass HEAD:** `8965490` on `main`, working tree clean before
  this commit. Phase 78 is still `planned`, twice-amended, **not
  executed** — this revision does not touch, reorder, or depend on it.
- **The block-list parsing gap is empirically confirmed, not assumed.**
  A real test against `scripts/check_knowledge_base.py::parse_record`
  with a `depends_on:` field written as a YAML block list (`depends_on:`
  followed by indented `- CL-TEST-999` lines) parses to
  `fields["depends_on"] == ""` — the parser's own loop explicitly skips
  any line starting with whitespace (`if not line or line[0] in " \t#":
  continue`), so the indented list items are silently invisible. The same
  test with the inline form (`depends_on: [CL-TEST-999, CL-TEST-998]`)
  correctly parses and both ids are extracted by
  `check_cross_references_resolve`. Grepping every real record under
  `planning/knowledge/codecompass-domain/*.yaml` confirms every existing
  list-valued field (`supporting_evidence`, `contradicting_evidence`) is
  already, universally, authored inline — the gap is real but this
  project has never actually hit it in practice, purely by an
  unenforced convention that happens to have held so far.
- **`source_ref`/`doc_ref`/`test_ref` are simple, single-line scalar
  fields**, confirmed by reading real `EV-*.yaml` records directly (e.g.
  `source_ref: "src/codecompass/adapters/haskell.py:1-288; ..."`) — a
  `grep` for a changed file's own path against these fields is reliable
  today, with no parser change needed, for the "which Evidence cites this
  source" direction of propagation (§10.1).
- **CodeCompass is a public repository**
  (`https://github.com/ctosullivan/codecompass`) — its `README.md`,
  `docs/`, and `architecture/` content is reachable at a public URL
  regardless of any local filesystem isolation. **This is the single most
  consequential fact this revision adds**: no export design, no
  undisclosed path, and no local-filesystem sandbox closes a leak that
  network egress makes available directly from the public mirror. Closing
  it requires the isolation-sensitive dispatch to also have **no network
  egress at all** — a property this plan can probe for but cannot itself
  configure, since neither `Agent(isolation: "remote")` nor a
  tool-grant restriction on `WebFetch`/`WebSearch` says anything about
  what a granted `Bash` can reach via `curl`/`wget`/a Python HTTP client
  (§6.1, §6.4).
- **The `Agent` tool's own documented semantics, re-confirmed**: only
  `subagent_type: "fork"` inherits the dispatching session's full
  conversation context; any other `subagent_type`, combined with
  `isolation: "remote"`, starts genuinely fresh with no shared filesystem
  and no inherited context — confirmed by direct reading of the tool's
  own description, not assumed.
- **Everything else** (the real `Claim` status enum, the `Agent` tool's
  worktree/remote isolation options, the confirmed `codecompass` editable-
  install leak, Phase 78's independence, `docs/domain/`'s frontmatter
  convention, `codecompass-template`'s structure, Priority A/B/D's
  boundaries) is unchanged from the second revision's own verified state
  — not re-derived here.

## 2. Problem statement (unchanged in substance from the second revision)

CodeCompass's Domain/blank-slate-reconstruction mechanism (Phases
63D/64/65) produces real, useful output but has never mechanically
enforced the isolation it is only prompt-instructed to keep, has never
produced an independent, model-blind implementation reconstruction
checked against the conceptual model in both directions, and has no
record-schema field distinguishing evidence-support from human review.
This phase closes those gaps — and, per this revision, does so honestly
about a hard limit the previous drafts missed: for a public repository,
"clean-room" is a filesystem-and-network property together, and this
project's own available tools may not be able to fully guarantee the
network half at all.

## 3. Goals, non-goals, and the Priority B distinction

**Goals** (renumbered to match this revision's own section order):

1. Extend the existing Claim record shape with the real, corrected status
   enum plus optional `assertion_kind`/`basis`/`examples`/
   `counterexamples`/`depends_on`/`open_questions`/`evidence_support_state`
   fields, with `depends_on` restricted to the inline `[ID, ID]` form and
   mechanically checked (§4).
2. Freeze canonical assertions into a citable, integrity-checked snapshot
   — the shared input both the coding-context packet and the
   documentation draft consume, replacing the second revision's circular
   "published documentation" framing (§5).
3. Identify, probe, and honestly label an isolation mechanism across
   filesystem, search, command, network, and delegation routes — with
   Tier 2 always `best-effort` and strict clean-room explicitly
   separated from, and possibly unmet alongside, workflow completion
   (§6).
4. Independently reconstruct the as-built implementation, model-blind and
   legacy-blind, freeze it, then classify alignment against the snapshot
   in both directions without either forcing agreement or automatically
   promoting a Claim's own verification status (§7).
5. Stage documentation writing from the snapshot (not from
   not-yet-existing published prose), preserve the first complete draft,
   reconcile legacy narrative only afterward, and publish the reconciled
   result into real, active documentation (§8).
6. Independently validate the **coding-context** side, not only
   documentation: a frozen, bounded, task-specific packet generated from
   the same snapshot, assessed with this project's own existing context-
   quality rubric (§9).
7. Add minimal, file-based, cycle-safe propagation that starts from a
   changed *source*, not an already-identified assertion, distinguishing
   "needs reassessment" from "proven incorrect," demonstrated in a
   disposable fixture — never leaving a synthetic contradiction in
   canonical knowledge or published documentation (§10).
8. Deliver portable, CodeCompass-agnostic templates, verified by a fresh
   downstream usability exercise (§11).

**Non-goals (unchanged):**

- No `src/codecompass/` change, no `context-graph.db` schema change, no
  new database, no graph subsystem, no comprehensive ontology.
- No re-application of the hardened workflow to the whole `docs/domain/`
  corpus or the whole `planning/v1-docs-reconstruction/` proposal.
- No change to Phase 78's own scope, ordering, or execution.
- No numerical confidence scores anywhere.
- No expansion into Priority B's own future runtime capability.

**This is not Priority B**, unchanged: Priority B (`decisions/0062`) is a
future, not-yet-planned `src/`-level capability for a downstream user's
own runtime project data. This phase makes zero `src/` changes.

## 4. Assertion record schema

No new record kind. `Observation`/`Evidence`/`Derivation` are unchanged.
The **real** `Claim` status enum, verified against `scripts/
check_knowledge_base.py`, is kept exactly as-is:

```
proposed → supported | contradicted → verified → superseded
```

**This phase does not add, rename, or reinterpret any of these five
values, and — corrected in this revision — does not automatically set
`verified` from a comparison finding either (§7.3).**

A Claim record used as a project-understanding **assertion** gains these
optional fields:

| Field | Values / shape | Validation | Purpose |
|---|---|---|---|
| `assertion_kind` | `definition` \| `relationship` \| `rule` \| `invariant` \| `state_transformation` \| `boundary` | New closed-enum check, when present (§4.2) | What kind of statement this is. |
| `basis` | `directly_stated` \| `inferred` \| `proposed_policy` \| `observed_behaviour` | New closed-enum check, when present | How the statement was arrived at. |
| `examples` | list of short strings/citations, **inline `[...]` form only** | `check_list_fields_are_inline`, when present (§4.2) | Concrete illustrating cases. |
| `counterexamples` | list of short strings/citations, **inline `[...]` form only** | `check_list_fields_are_inline`, when present | Cases that test or bound the assertion; an empty list means "none found." |
| `depends_on` | list of assertion ids, **inline `[ID, ID]` form only — required, not merely conventional** | `check_list_fields_are_inline` (fail-closed, §4.2) plus the existing `check_cross_references_resolve` (works today for the inline form, confirmed empirically, §1) | Explicit dependency edges, for transitive propagation (§10). |
| `open_questions` | list of short strings, **inline `[...]` form only** | `check_list_fields_are_inline`, when present | Genuinely unresolved matters. |
| `evidence_support_state` | `supported` \| `partially_supported` \| `unsupported` \| `conflicting` | New closed-enum check, when present | A qualitative read of evidence completeness — never a number, never conflated with `status`. |

**No `human_review_state` field.** Publication and phase completion never
depend on one. Any existing page-level review metadata (`docs/domain/`'s
own Phase-63D-era frontmatter) is preserved where it exists and is not
required of this phase's own new content.

**No numerical confidence score anywhere.**

**Versioning discipline (unchanged)**: a changed *statement* requires a
new Claim record whose `supersedes` field names the prior one; the prior
record's own `status` moves to `superseded`. A withdrawn assertion needs
no invented successor — its own `status` simply moves to `contradicted`.
Every prior version stays on disk, permanently citable. **This
convention is not itself mechanically enforced** (nothing stops a future
edit to an existing `.yaml` file in place) — §5.3's snapshot-integrity
check is the mechanical backstop that *detects* a violation after the
fact, since preventing one outright would need a write-time hook this
phase's own minimal, file-based scope does not add.

### 4.1 One shared foundation, two derived outputs (unchanged)

These records are the single knowledge foundation. A discovery made while
writing documentation, doing implementation reconstruction, or
reconciling legacy material must first become a canonical Observation/
Evidence/Claim record before it is reflected in any derived output.
Documentation prose is never itself evidence for a claim.

### 4.2 Checker changes (in implementation scope, revised)

`scripts/check_knowledge_base.py` gains **two** new checks (the second
revision only specified one):

**1. Closed-enum validation for the new optional fields** (unchanged from
the second revision):

```python
_OPTIONAL_ENUM_FIELDS: dict[str, dict[str, set[str]]] = {
    "claim": {
        "assertion_kind": {
            "definition", "relationship", "rule", "invariant",
            "state_transformation", "boundary",
        },
        "basis": {
            "directly_stated", "inferred", "proposed_policy",
            "observed_behaviour",
        },
        "evidence_support_state": {
            "supported", "partially_supported", "unsupported", "conflicting",
        },
    },
}


def check_optional_enum_fields(feature_dir: Path) -> list[Finding]:
    """Any of the fields in _OPTIONAL_ENUM_FIELDS, if present at all,
    must use one of its own closed values."""
```

**2. Positive, fail-closed validation of the inline form — corrected
this revision.** The second revision's own detector looked for a
specific *bad pattern* (a bare `key:` line immediately followed by an
indented `- item` line) — found, on direct re-review, to miss three real
cases: a comment or blank line between the key and its first list item
(the detector only inspects the *immediately next* line), an **indentless**
block list (`- item` with no leading whitespace at all, which the
detector's own `^\s+-\s` pattern requires and therefore never matches),
and a malformed non-bracket value like `depends_on: CL-1, CL-2`. Rather
than continue enumerating bad shapes, this revision validates the
*parsed field value directly* — **fail closed**: if a list-valued field
is present at all, its value must match the inline form exactly; anything
else fails, regardless of what YAML shape produced it:

```python
_LIST_VALUED_FIELDS = {
    "supporting_evidence", "contradicting_evidence",
    "examples", "counterexamples", "depends_on", "open_questions",
}
_INLINE_LIST_RE = re.compile(r"^\[.*\]$")


def check_list_fields_are_inline(feature_dir: Path) -> list[Finding]:
    """Every list-valued field this parser can validate at all must use
    the inline `[a, b]` form. Rather than pattern-match the raw YAML
    text for known-bad shapes (which a comment line, a blank line, or an
    indentless list can each slip past), this validates the *parsed*
    value directly: parse_record's own single-line key:value capture
    means any of those alternate forms parses to an empty or malformed
    string regardless of surrounding whitespace/comments, so checking
    the parsed value catches all of them uniformly, including shapes not
    enumerated here by name."""
    findings: list[Finding] = []
    for yaml_path in sorted(feature_dir.glob("*.yaml")):
        fields = parse_record(yaml_path)
        if fields.get("kind") != "claim":
            continue
        for field in _LIST_VALUED_FIELDS:
            if field not in fields:
                continue  # absent is fine -- every one of these is optional
            value = fields[field]
            if not _INLINE_LIST_RE.match(value):
                findings.append(
                    Finding(
                        "knowledge-base-non-inline-list",
                        f"{yaml_path.relative_to(ROOT)}: field {field!r} "
                        f"is present but its parsed value {value!r} is "
                        "not the inline `[a, b]` form this parser can "
                        "validate -- if this was written as a YAML block "
                        "list (indented or not, with or without "
                        "intervening comments), it parses as an empty "
                        "string and would otherwise silently skip all "
                        "cross-reference/dangling-id checking",
                    )
                )
    return findings
```

Verified compatible with every existing record: every real
`supporting_evidence`/`contradicting_evidence` value in
`planning/knowledge/codecompass-domain/*.yaml` is already inline
(confirmed by direct `grep`, §1), so this check produces zero findings
against current content. Dangling-id checking for a confirmed-inline
`depends_on` still runs through the existing, unmodified
`check_cross_references_resolve` (verified empirically to work for this
form, §1) — this check only guards the representation, not the
reference resolution itself, which was never broken for the inline form.

— both checks registered in `CHECKS`, alongside `check_snapshot_
historical_integrity` and `check_snapshot_current_divergence` (§5.3).
**Correction from the second revision, restated precisely**: cross-
reference resolution for the *inline* form works today with no change
(verified empirically); the inline-form *validation* is new code, added
because a record author has no way today to know the block form silently
fails open, not because the existing mechanism already covered every
representation. `python3 scripts/check_knowledge_base.py --strict`
remains a required Definition-of-Done verification command (§12), now
covering all four checks.

## 5. Frozen knowledge snapshot (replaces the second revision's circular "published understanding")

**This section replaces the second revision's own §5**, which had
comparison (old §7) and documentation writing (old §8) both consuming
"the published Understanding documentation" — an artifact that, per old
§8.4, did not actually get published until *after* both of those stages
ran. That was circular, found by direct re-reading of this revision's
own predecessor. The fix: the intermediate artifact both later stages
consume is a **frozen knowledge snapshot** — a versioned, citable,
mechanically-integrity-checked rendering of the assertion store — never
itself "the documentation," never gated on human review.

### 5.1 Producing the assertions (unchanged from the second revision)

`context-researcher` produces the assertion records (§4) under
`planning/knowledge/<topic-slug>/`. `domain-skeptic` adversarially
reviews them (unsupported claims, internal contradictions, missing
counterexamples) — an agent-level quality check, not a human-approval
gate — resolving what it can with further evidence, recording the rest
as genuine `open_questions`.

### 5.2 Snapshot creation — the exact artifact, format, and citation (corrected this revision)

**Correction, this revision**: the second revision's own design hashed
each cited assertion's *current, live* file — which legitimately changes
the moment that same assertion is superseded or withdrawn (its own
`status` field is edited in place, by design, per §4's versioning
discipline), so a routine, correct lifecycle transition would have been
indistinguishable from tampering. The fix: **preserve the assertion's
content exactly as it was at freeze time, using the assertion's own
`repository_revision` and this repository's own git history — not the
live file** — so a later, legitimate status change on the *current* file
never touches what the snapshot itself represents.

Once the assertions have been through adversarial review (no further
gate), a snapshot is created:

- **`planning/knowledge/<topic-slug>/snapshots/snapshot-v<N>.md`**
  (human-readable): the snapshot's own id (`<topic-slug>@v<N>`), creation
  timestamp, the CodeCompass repository revision at freeze time, the full
  list of included assertion ids with a one-line restatement of each
  `statement`, and an explicit list of assertions considered but
  **excluded** (still `proposed`, insufficiently evidenced).
- **`planning/knowledge/<topic-slug>/snapshots/snapshot-v<N>.toml`**
  (machine-checkable sidecar — **TOML, not YAML**, corrected during
  implementation to match this project's own already-established
  convention: `pyproject.toml` itself notes `requires-python >=3.11`
  specifically so stdlib `tomllib` can parse structured config with no
  new dependency, and this script's own docstring already cites
  `reference_pipeline.py::load_references_toml` as the precedent for "a
  comparably simple format" — the snapshot's own genuinely nested
  structure, unlike every other flat record this checker parses, is
  better served by a real, stdlib-parseable format than by extending the
  hand-rolled flat parser to handle nesting it was never designed for):
  for every included assertion, a full **evidentiary chain**, not just
  the Claim itself — corrected this revision per the user's own explicit
  instruction that only preserving Claim hashes is insufficient to
  reconstruct the supporting evidence:

  ```toml
  snapshot_id = "<topic-slug>@v1"
  created = "<timestamp>"
  repository_revision_at_freeze = "<CodeCompass HEAD sha at freeze time>"
  excluded_assertions = ["CL-XYZ-004"]

  [assertions."CL-XYZ-001"]
  path = "planning/knowledge/<topic-slug>/CL-XYZ-001.yaml"
  repository_revision = "<the exact commit this Claim cites>"
  content_hash = "<sha256 of `git show <rev>:<path>`>"

  [assertions."CL-XYZ-001".supporting_evidence."EV-XYZ-001"]
  path = "planning/knowledge/<topic-slug>/EV-XYZ-001.yaml"
  repository_revision = "<rev>"
  content_hash = "<sha256 of the Evidence record's own content at that rev>"
  source_ref = "<verbatim, from the Evidence record itself>"
  doc_ref = "<verbatim>"
  test_ref = "<verbatim>"

  # contradicting_evidence: same shape, if any

  [assertions."CL-XYZ-001".derivation."DE-XYZ-001"]
  path = "planning/knowledge/<topic-slug>/DE-XYZ-001.yaml"
  repository_revision = "<rev>"
  content_hash = "<sha256 at that rev>"
  ```

  (`path` is stored explicitly, per record — never inferred from the id —
  since this workflow's own convention allows a record file to be named
  however is convenient, matching `check_knowledge_base.py`'s own existing
  docstring.)

  Every hash is computed from `git show <repository_revision>:<path>` —
  the exact historical git blob — never the live working-tree file. This
  makes the snapshot self-sufficient to trace all the way back to
  original source locators (`source_ref`/`doc_ref`/`test_ref`) without
  depending on any other record staying unchanged.
- **Citation format**: `<topic-slug>@v<N>#<assertion-id>` — used by a
  coding-context packet (§9), a documentation page (§8), or a `design.md`.

### 5.3 Integrity validation — three distinct questions, not one (corrected this revision)

**Correction, this revision**: a single "does the live file still match
the stored hash" check conflates three genuinely different questions,
which the second revision's own design could not tell apart. This
revision names and checks each separately:

1. **Historical-content integrity (corruption)** — `check_snapshot_
   historical_integrity(snapshot_path)`: for every assertion (and its
   evidence/derivation) the snapshot cites, re-run `git show
   <recorded-repository_revision>:<path>` and hash it; compare against
   the snapshot's own stored hash. **This should always pass** in normal
   operation — git history at an already-committed revision does not
   change on its own. A mismatch means either the snapshot's own sidecar
   file was hand-edited after the fact, or git history itself was
   rewritten (rebase/force-push) since that revision — a genuine,
   serious finding, reported as `knowledge-base-snapshot-tampering`.
   **A legitimate supersession or withdrawal never triggers this** —
   editing the *current* file's `status` field, or creating a brand-new
   successor record, never touches the historical git blob at the old
   revision the snapshot actually cites.
2. **Current-record divergence (informational, not corruption)** —
   `check_snapshot_current_divergence(snapshot_path)`: compare the same
   historical, git-revision-pinned content against the assertion's
   **current, live** `.yaml` file at the same path. A difference here is
   expected and healthy over time (the assertion may have been
   legitimately superseded, or its `status` moved to `contradicted`) —
   reported as an **informational** finding only
   (`knowledge-base-snapshot-current-divergence`, never `--strict`-blocking),
   naming exactly what changed (e.g. `status: supported → superseded`).
   This is also the mechanical hook propagation (§10.2) uses to flag a
   snapshot-level citation as `needs reassessment`.
3. **Evidence/source staleness** — a divergence found in step 2 that
   traces to the assertion's own **evidence**, not merely its lifecycle
   `status`, is the specific signal that should trigger re-derivation
   (a fresh `context-researcher` pass), not just a documentation update —
   named distinctly in the divergence report so a reader can tell "the
   record was formally superseded" (expected, routine) apart from "the
   underlying evidence itself may now be wrong" (worth investigating).

This three-way split is what lets **a normal supersession preserve an
intact historical snapshot's own integrity** (check 1 keeps passing)
while **still surfacing that something has moved on** (check 2 reports
the divergence, non-blocking) — exactly the distinction the second
revision's single-hash design could not make.

### 5.4 No human-acceptance gate (unchanged principle, now attached to the correct artifact)

Freezing a snapshot requires no human sign-off — the adversarial review
(§5.1) is the quality gate, same as the second revision established.
What changes is *what* gets published without a human gate: it is this
snapshot (an evidence/version artifact), not yet the final documentation
prose, which is written later, from the snapshot, at §8.

## 6. Mechanical isolation — verified enforcement across every real route, honestly labelled

### 6.1 The public-repository finding — read this before anything else in this section

**CodeCompass is a public GitHub repository.** Its `README.md`, `docs/`,
and `architecture/` content — everything this workflow's Understanding
and Implementation-reconstruction stages are meant to exclude — is
reachable at a public URL (`https://github.com/ctosullivan/codecompass`
and its raw-content mirror) by anything with outbound network access,
regardless of what is or isn't present on the local filesystem an
isolated dispatch can see. **Local filesystem isolation, however
rigorous, does not by itself close this.** Closing it requires the
isolation-sensitive dispatch to also have **no network egress at all** —
a property neither `Agent(isolation: "remote")` (a *filesystem*
isolation primitive; nothing in its own documentation says anything
about network policy) nor omitting `WebFetch`/`WebSearch` from a role's
`tools:` list (a granted `Bash` can still `curl`/`wget`/use a scripting
language's own HTTP client) actually guarantees. This plan can **probe**
for network egress (§6.3); it cannot **configure** the underlying
sandbox's own network policy, which is outside any tool this project has
available. This is the single most consequential technical finding in
this revision and is treated as such throughout — see §12's own explicit
separation of workflow completion from strict clean-room validation.

### 6.2 What is genuinely enforceable, and what is not

- **Tool-category grants**, via a custom `.claude/agents/*.md` role's
  `tools:` frontmatter, are real: a role not granted `WebFetch`,
  `WebSearch`, or `Agent` structurally cannot call them by name.
  **This does not close the Bash-based network bypass** (§6.1) — a role
  granted `Bash` for legitimate command execution (running tests,
  inspecting schema) can use it to reach the network regardless of which
  named network tools are withheld. This must be tested directly (§6.3),
  never assumed closed by tool-list omission alone.
- **`Agent(isolation: "remote")`**, where available, provides genuine
  filesystem isolation (no shared mount, no inherited conversation
  context for a non-`fork` dispatch, confirmed by direct reading of the
  tool's own description, §1) — but says nothing about network policy.
- **Not enforceable at all, confirmed**: confining `Read`/`Grep`/`Glob`/
  `Bash`, once granted, to a specific directory on the same host. These
  tools reach anywhere the host OS permits.

### 6.3 Required, multi-route preflight probes — observed, not self-reported

**A single self-reported failed read of one absolute path is
insufficient** — the second revision's own single-probe design is
replaced with a set of independently-checked probes covering every route
named in this revision's own instruction, run using the **exact same
dispatch configuration** (tools, isolation mode) the real stage will use
— never a generic, separately-configured test assumed to generalize:

| Route | Probe | Independently checked by |
|---|---|---|
| **Filesystem** | Attempt to read the exact absolute path of a real, known-excluded file (e.g. the main checkout's own `README.md`) | The lead reads the dispatched agent's own **raw tool-call transcript** (the actual `Read` invocation and its actual return value/error) — never the agent's own prose summary of what happened, which could misreport a success as a failure. |
| **Search** | Attempt a `Glob`/`Grep` for a known-excluded filename pattern across a broad root (e.g. `Glob("/home/**/codecompass/README.md")` or `Grep` for a distinctive string only the excluded content contains) | Same — the raw tool-call transcript, not the agent's own narrative. |
| **Command** | Attempt a `Bash` command that would reveal or reach excluded content indirectly (e.g. `find / -iname "*codecompass*" 2>/dev/null`, `env`, `pwd -P`) | Same. |
| **Network** | Attempt `curl -sS --max-time 5 <a public URL for the excluded content's own real GitHub location>` (or, if that succeeds trivially, escalate to confirming it returns the actual excluded text) | Same — and **this probe is the one this revision expects to fail to deny, per §6.1**; a successful fetch is recorded as a genuine, likely-permanent limitation, not retried differently or wished away. |
| **Delegation** | Confirm the role's own `tools:` grant excludes `Agent` (a static, reviewable fact about the role definition, not something to probe at runtime) | Read the role's own `.claude/agents/*.md` frontmatter directly. |
| **Transferred content / inherited context** | Confirm (a) the export's own file listing matches its manifest exactly (§6.7's boundary-check) and (b) the dispatch is not `subagent_type: "fork"` (a static fact about how it was invoked) | Direct inspection of the export directory and the dispatch call itself. |

**Labelling rule**: a stage may be labelled `isolation: verified` only if
**both** the filesystem/search/command probes fail to reach excluded
content **and** the network probe fails to reach it. If the filesystem
probes fail but the network probe succeeds, the stage is labelled
`isolation: filesystem-only, network-exposed` — **not** `verified`, and
**not** treated as clean-room, since the excluded content remains
reachable by a route this label names explicitly. If any probe succeeds
unexpectedly, or Tier 1 is unavailable, the stage falls to Tier 2 and is
labelled `isolation: best-effort` per §6.5, unconditionally.

### 6.4 The network bypass, stated as its own rule

**Omitting `WebFetch`/`WebSearch` from a role's tool grant does not
restrict networking done through a granted `Bash`.** Every isolation-
sensitive role that needs `Bash` for a legitimate reason (running tests,
inspecting schema, invoking `codecompass` for real behaviour observation)
is, by that same grant, potentially network-capable unless the
*execution environment itself* blocks egress — a property this plan
tests for (§6.3) but does not control. A role that does not need `Bash`
at all (documentation-only answering, §6.6) is granted `Read`/`Grep`/
`Glob` only, with no way to reach the network through any granted tool —
this is the one scope in this workflow where the network route is
closed by tool-grant alone, confirmed by the absence of any
network-capable tool in its own grant.

### 6.5 The two-tier mechanism, corrected

**Tier 1**: `Agent(isolation: "remote")`, seeded only with the scope's
own curated export content. Labelled `verified` only per §6.3's combined
filesystem-and-network bar; labelled `filesystem-only, network-exposed`
if the network probe alone succeeds; unavailable or otherwise failing its
own probes falls to Tier 2.

**Tier 2 (fallback): the curated export, on this same host, with the
narrowest tool grant each role's job allows.** **Correction from the
second revision**: Tier 2 is **always** labelled `isolation: best-effort`
— never `verified`, never upgraded on the strength of any single probe's
outcome, because the underlying mechanism (shared host filesystem, tools
that reach anywhere the OS permits) provides no architectural guarantee
regardless of what one test run happened to find. **An incidental failed
read during a Tier-2 dispatch is not evidence of a real boundary and must
never be reported as such.**

**Which tier is actually available, and what it can honestly be
labelled, is determined live, by the probes above, run in the same
environment and configuration the real stage will use — this plan does
not assume the answer, and given §6.1's own finding, the most likely
honest outcome for at least the network dimension is that neither tier
achieves `verified` in the strict sense.**

### 6.6 Indirect-leakage checklist (unchanged from the second revision, still checked)

- **Databases**: `context-graph.db` excluded entirely from the
  Implementation-reconstruction export (an ordinary sync embeds narrative
  content into it).
- **Symlinks**: export construction dereferences them on copy.
- **Caches**: `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `vendor/`
  excluded.
- **Import paths**: `codecompass`'s own confirmed editable install (§1)
  resolves to the real checkout regardless of an export's own working
  directory — any dispatch running real `codecompass` commands is told
  this explicitly and instructed not to introspect the resolved module's
  own file path.
- **Auto-loaded instructions**: no real `CLAUDE.md` in any isolation-
  sensitive export's own working directory — a minimal, purpose-written
  one only (§6.8).
- **Inherited context**: never `subagent_type: "fork"`; the lead never
  performs an isolation-sensitive stage's own work directly.

### 6.7 Scope coverage table (tool grants unchanged from the second revision; labelling column added)

| Scope | Tool grant | Network route closed by tool grant alone? |
|---|---|---|
| **Understanding reconstruction** (`context-researcher`) | Read, Grep, Glob, Bash (no `WebFetch`/`WebSearch`, no `Agent`) | **No** — `Bash` remains network-capable unless the environment itself blocks egress (§6.3's network probe decides the real label). |
| **Implementation reconstruction** (`implementation-reconstructor`) | Read, Grep, Glob, Bash (same restriction) | **No**, same reason. |
| **Documentation architecture + writing** (`docs-reconstructor`, extended) | Read, Grep, Glob (no `Bash`, no network, no `Agent`) | **Yes** — no network-capable tool granted at all. |
| **Documentation-only answering** (fresh `general-purpose`) | Read, Grep, Glob only | **Yes**, same reason. |
| **Legacy reconciliation** (`docs-maintainer` + lead) | Full, as `docs-maintainer` already has | N/A — this scope's own inputs are unrestricted by design (§6.9). |

(Permitted/excluded content per scope is unchanged from the second
revision's own table — restated in full in `docs/mechanical-isolation.md`
at implementation time, §11.)

### 6.8 Minimal reviewed bootstrap (unchanged)

Each export's own working directory contains, at most: the permitted
content, a purpose-written `TASK.md`, and, only where genuinely needed, a
minimal `CLAUDE.md` with tool-usage mechanics only — never the real
project's own history/governance file.

### 6.9 Legacy reconciliation's own full access (unchanged, restated for clarity)

Legacy reconciliation is the one scope where full access is correct by
design — the clean-room draft it compares against is already committed
and immutable at that point (§8.2's ordering gate), so nothing this
stage sees can retroactively contaminate it.

### 6.10 Persisted per-dispatch (under `planning/knowledge/<topic-slug>/isolation/`)

- `<scope>.manifest` — allow-list, source revisions, tier and label
  actually assigned (`verified` / `filesystem-only, network-exposed` /
  `best-effort`).
- `<scope>.preflight.md` — **every** probe's own exact prompt and raw
  tool-call transcript (§6.3) — not a summary.
- `<scope>.access-log.md` — the dispatched agent's own observable
  research trace (Phase 78's own §5.3.4 convention, reused verbatim).
- `<scope>.boundary-check.md` — the export's own file listing checked
  against its manifest.

### 6.11 Breach protocol (unchanged)

A boundary-check finding an unlisted file, a preflight probe unexpectedly
succeeding on a scope already labelled `verified`, or an access-log
naming an out-of-scope path voids that stage's own output; the export is
rebuilt, a fresh agent re-runs the stage, and the breach is recorded, not
absorbed. No stage is ever relabelled upward after a detected breach.

## 7. Independent implementation reconstruction and comparison

### 7.1 `implementation-reconstructor` (unchanged)

Given only the Implementation-reconstruction export, recovers modules,
APIs/CLI, data/persistence, dependencies, runtime paths, extension
points, build/config, tests, and limitations —
`planning/knowledge/<topic-slug>/implementation-reconstruction.md` — with
no access to the snapshot at this stage.

### 7.2 Comparison — extends `domain-skeptic`, consumes the snapshot

Once the as-built report is frozen (committed), a **fresh** `domain-
skeptic` dispatch receives both the frozen snapshot (§5, not
"published documentation" — corrected from the second revision) and the
frozen as-built report, and classifies every relevant behaviour:
`aligned` / `partial` / `conflicting` / `not_implemented` /
`insufficiently_verified`. Neither side is revised to force agreement. A
`conflicting` or `not_implemented` finding becomes a new `open_questions`
entry on the relevant assertion (a new Claim version, per §4's versioning
discipline — the frozen snapshot itself is never edited) and a flagged
section in the documentation-architecture stage's own output (§8.1).

### 7.3 Alignment is not verification — corrected this revision

**The second revision's own rule — "an `aligned` classification is a
legitimate basis for moving the Claim's own `status` to `verified`" — is
removed.** `aligned`/`partial`/`conflicting`/`not_implemented`/
`insufficiently_verified` are comparison-classification labels, recorded
in the alignment report **only** — they never automatically write back
into a Claim's own `status` field, for a precise reason: implementation
conformance shows the *code* currently matches the *stated* assertion; it
does not, by itself, establish that a domain **rule** or **proposed
policy** assertion is itself correct — only that current code happens to
be consistent with it. Moving a Claim's own `status` to `verified`
requires a **separate, claim-specific, deliberately-run check against
primary evidence** — e.g. an agent directly exercising the exact
described behaviour and confirming it, or checking the rule against an
authoritative external source where one exists — with the specific
check performed recorded on the Claim's own `derivation`/evidence trail,
never merely "the broader comparison pass found this aligned." This bar
is deliberately higher for `assertion_kind: rule`/`invariant` or
`basis: proposed_policy` than for a directly-observable
`state_transformation`, where an aligned comparison finding is closer to
(but still not automatically) sufficient — the distinction is preserved
explicitly in whichever record documents the verification action, not
collapsed into one rule for every assertion kind.

## 8. Staged documentation writing, publication, and legacy reconciliation

### 8.1 Documentation architecture — selected by a fresh, isolated dispatch

A fresh, isolated `docs-reconstructor` dispatch, given the
Documentation-writing export (§6.7) — **the frozen snapshot (§5) and its
cited assertion ids, plus the Implementation-reconstruction report and
alignment classification (§7)**, corrected from the second revision's
"published Understanding documentation" input — opens its own output by
stating the information architecture it selects (arc42/C4-inspired
views, Diátaxis-style categories, used selectively) and why, then writes
the complete draft under that structure in the same dispatch.

### 8.2 Clean-room first draft

The same dispatch produces the complete first draft, citing: domain
concepts from the snapshot's own assertion ids (`<topic-slug>@v<N>#<id>`,
§5.2); project policies from the relevant Decision/ADR, labelled
intent/rationale; supported behaviour from the alignment report's
`aligned`/`partial` findings; and future intentions from `not_implemented`
findings, explicitly labelled as such. **This is the first point in the
entire pipeline where conceptual understanding is actually written into
documentation prose** — corrected from the second revision's implication
that this had already happened earlier. **This draft is committed to
`main`, under `planning/v1-docs-reconstruction/<topic-slug>/`, before the
next step begins** — the mechanical ordering gate (§12).

### 8.3 Legacy reconciliation — only after the draft is preserved (unchanged)

`docs-maintainer` + the lead, now with full access to both the preserved
draft and the legacy narrative, classify every relevant historical claim:
`supported` / `stale_or_contradicted` / `rationale_requiring_verification`
/ `useful_example` / `obsolete`. Any legacy claim folded in is
re-grounded in cited evidence at the point of incorporation.

### 8.4 Publication into real, active project documentation (unchanged)

The reconciled result is published into the real, active documentation
tree: a new or extended `docs/domain/concepts/<topic-slug>.md`, and the
corresponding updates to `docs/cli-reference.md`,
`architecture/context-graph-schema.md`, and `README.md` — superseding
the existing Phase-77-authored prose on this topic only. Zero `src/
codecompass/` change; not a Priority B capability.

### 8.5 Default route; a missing prerequisite blocks, it does not silently fall back (unchanged)

`docs-reconstructor`'s old, unrestricted MODE 2 is retired as a silent
fallback. A missing snapshot or implementation-reconstruction report for
a future topic is a named blocker, not a reason to revert to unrestricted
reading.

### 8.6 Documentation-only answering and independent verification (unchanged from the second revision)

The question set is written and frozen before any answering dispatch. A
fresh `general-purpose` agent (no `Bash`, no network-capable tool, §6.7)
answers using only the final, published documentation tree.
`context-evaluator` independently verifies each preserved answer against
real repository evidence. A material incorrect or unsupported claim is
fixed in the published documentation itself, not merely recorded.

## 9. Coding-context validation — new this revision

**The second revision validated documentation but never independently
validated the coding-context side of the shared foundation** — it
demonstrated propagation *reaches* a packet (old §9.1), which is a
citation check, not a usefulness check.

### 9.1 Freeze a bounded, task-specific coding-context question

Before generating anything, a small, realistic, bounded task for the
validation topic is written and frozen (e.g., for the first-party
source/symbol subsystem: *"add a new `exposure` value for a hypothetical
sixth visibility tier — what existing code, tests, and constraints does
an implementer need to know?"*) — frozen the same way §8.6 freezes its
documentation questions, before any packet exists to answer it.

### 9.2 Generate the packet from the same snapshot

`knowledge-curator`'s existing packet-assembly mode (Phase 54c,
unchanged) assembles a real `context-packet.md` for this frozen task,
citing assertion ids from the **same** snapshot (`<topic-slug>@v<N>`)
the published documentation cites — the concrete mechanism by which "one
shared foundation" is not merely asserted but exercised identically on
both derived-output paths.

### 9.3 Independent assessment — reusing this project's own existing rubric

A fresh `context-evaluator` dispatch independently assesses the packet
against the frozen task, using the **existing**
`context-quality-evaluation.md` rubric this project already applies to
every real-task Priority A trial run to date (Phases 75-77; Phase 78 is
still `planned` and has not itself been evaluated) — no new rubric
invented:
Accuracy / Relevance / Completeness / Freshness / Grounding-provenance /
Noise / Safety-trustworthiness, plus a **LOW / MODERATE / HIGH** context-
advantage rating specifically for this task. The evaluator independently
re-derives the correct answer from primary evidence (source, tests) —
never from the packet's own claims — before judging the packet against
it, the same "establish ground truth directly" discipline this role
already has.

### 9.4 What this demonstrates, and what it does not

A LOW advantage rating is an honest, acceptable outcome (this project's
own established precedent — Phases 75 and 77 both rated LOW; Phase 78,
still `planned`, is not part of this precedent since it has not been
executed or evaluated) — it is not, by itself, a
failure of this phase. What this step exists to catch is a packet that
is **inaccurate or unsupported**, which would be a real failure: the
shared foundation producing something *wrong*, not merely something
*unimpressive*. Per the user's own explicit instruction, **shared
citations or reassessment flags alone are not sufficient evidence** that
the foundation supplies useful task context — this independent,
primary-evidence-grounded assessment is what actually establishes it,
whatever the resulting rating.

## 10. Change propagation (minimal, file-based, corrected this revision)

### 10.1 Finding what a changed *source* actually touches — new this revision

**The second revision's own traversal started from an assertion already
identified by hand.** This revision adds the missing first step:

1. Given a changed source file (e.g. `src/codecompass/source_symbols.py`),
   `grep` for its own path across every Evidence record's
   `source_ref`/`doc_ref`/`test_ref` fields (simple scalar strings,
   confirmed parseable with no code change, §1) — this finds every
   Evidence record that cites the changed file.
2. For each such Evidence id, `grep` for it across every Claim's
   `supporting_evidence`/`contradicting_evidence` fields (inline-list
   form, already reliably parsed) — this finds every Claim/assertion the
   changed evidence actually backs or contradicts.

### 10.2 Transitive closure — cycle-safe, corrected this revision

3. **Transitive dependents**: any assertion whose own `depends_on` names
   an assertion found in step 2, walked recursively. **Cycle-safety,
   corrected this revision**: the walk maintains a `visited` set of
   assertion ids; an id already in `visited` is never re-queued or
   re-processed, guaranteeing termination regardless of whether the
   dependency graph contains a cycle (e.g. `A depends_on B`, `B
   depends_on A`) — a real possibility this project's own minimal,
   `grep`-based traversal must handle explicitly rather than assume away.
4. **Snapshot-level citations**: any snapshot (§5.2) whose own
   `snapshot-v<N>.toml` lists an affected assertion id is itself flagged
   — a snapshot is immutable and is never edited, but the *fact* that a
   published, cited snapshot now rests on since-changed evidence is
   itself a finding worth surfacing, recorded without altering the
   snapshot file.
5. **Both derived-output kinds**: every coding-context packet and every
   documentation page citing an affected assertion id (direct or
   transitive) — the existing citation mechanism, `grep`, no new index.

### 10.3 "Needs reassessment" vs. "proven incorrect" (unchanged)

A citer is *proven incorrect* only if it asserted the specific thing the
new evidence contradicts; every other citer found above is *needs
reassessment*.

### 10.4 Demonstration — from a changed *source*, in a disposable fixture, with cycle and snapshot coverage (corrected this revision)

**Two defects in the second revision's own demonstration, corrected
here**: (a) it changed an *assertion* directly, never exercising §10.1's
own source-to-evidence discovery step at all — the very thing this
revision added because the second revision's traversal skipped it; and
(b) it never included a dependency cycle or a snapshot-level citation, so
§10.2's own cycle-safety and snapshot-flagging logic were never actually
exercised, only described. This revision's demonstration fixture is built
to exercise the **entire** chain named in §10's own header
(`source → evidence → assertions → transitive dependents → snapshots →
both outputs`), not a shortened version of it:

1. **Fixture contents** — copied into a disposable directory under the
   session scratchpad, never inside either repository's tracked tree:
   - the validation topic's real, relevant **source file(s)** (e.g. a
     copy of `src/codecompass/source_symbols.py`);
   - the real Evidence record(s) whose `source_ref` cites that file;
   - at least three real Claim/assertion records arranged so that **one
     depends on another which depends on the first** — a genuine cycle
     (`CL-A depends_on: [CL-B]`, `CL-B depends_on: [CL-A]`), constructed
     deliberately for this fixture specifically to exercise §10.2's own
     visited-set termination logic, not found by chance in real data;
   - the real, already-frozen snapshot that cites at least one of these
     assertions;
   - a representative coding-context packet and the published
     documentation page, both citing the same assertion(s).
2. **The demonstrated change is to the fixture's own copy of the source
   file** — a deliberate, disclosed edit (e.g. a changed docstring or a
   renamed parameter in the fixture's own copy) — never to an assertion
   directly, so the discovery step (§10.1: source → Evidence via
   `source_ref`, Evidence → Claim via `supporting_evidence`) is the thing
   actually exercised, not skipped.
3. **Run the full traversal (§10.1-10.3) against the fixture**, and
   confirm, concretely:
   - the changed source file's own path is found in the fixture's
     Evidence record (§10.1 step 1);
   - the correct Claim(s) are found via that Evidence (§10.1 step 2);
   - **the cycle is walked exactly once each and the traversal
     terminates** — the visited-set mechanism (§10.2) is what makes this
     provable, not merely assumed; the demonstration report states the
     visit order and confirms no infinite loop occurred;
   - the fixture's own snapshot is flagged as citing an affected
     assertion (§10.2 step 4) — proving snapshot-level citation discovery
     works, not only direct/transitive assertion citers;
   - both the fixture's coding-context packet and its documentation page
     are re-flagged `needs reassessment` (§10.2 step 5), from the
     **same** underlying source change.
4. **Delete the fixture** once the demonstration is recorded — only
   `propagation-deltas.md` (naming every citer found, the cycle-traversal
   order, and the snapshot-level flag) and a short description of the
   exercise are preserved. **No synthetic change, contradiction, or
   `CONTROLLED TEST` label is left in real canonical
   `planning/knowledge/<topic-slug>/` records, real snapshots, or real
   published documentation at any point.**

A changed *source* file reaching both derived-output kinds — through a
genuine multi-hop, cycle-containing dependency graph and a flagged
snapshot citation, not a direct one-hop assertion edit — is the concrete
evidence this revision's own corrected propagation design actually works
end to end, proven without touching real project state.

## 11. Template delivery (`codecompass-template`)

Preserves the existing MIT licence and lightweight role; no
CodeCompass-specific agent roster, history, or governance requirement.

**Files** (added at implementation time; largely unchanged from the
second revision, descriptions updated for this revision's corrections):

- `planning/knowledge/assertions/TEMPLATE.md` — the shared assertion
  shape, **explicitly requiring the inline `[...]` form for every list
  field**, with the corrected real status lifecycle.
- `planning/knowledge/snapshots/TEMPLATE.md` — **revised**: the exact
  snapshot format (§5.2 — id list, content hashes, citation format),
  not just "how to name and cite" in general terms.
- `docs/conceptual-documentation-guide.md` — how to write understanding
  directly into project documentation, sourced from a frozen snapshot
  (not a separate reviewed packet), with inline evidence citations.
- `planning/knowledge/coding-context-selection/TEMPLATE.md` — **revised**:
  now includes the freeze-question → generate-from-snapshot →
  independently-assess procedure (§9), not just "how to assemble a
  packet."
- `docs/mechanical-isolation.md` — **substantially revised**: the
  multi-route preflight procedure (§6.3), the explicit network-egress-
  via-Bash bypass warning (§6.4), the public-repository caveat generalized
  for any downstream project whose own repository is also public, and the
  "Tier 2 is always best-effort, never upgraded" rule stated plainly for
  a project with no remote-isolation tooling at all.
- `planning/knowledge/implementation-comparison/TEMPLATE.md` — the
  five-way alignment classification, **with the alignment-is-not-
  verification rule (§7.3) stated explicitly**.
- `planning/knowledge/propagation/TEMPLATE.md` — **revised**: the
  source-to-evidence discovery step (§10.1) and cycle-safe traversal
  (§10.2), not only the delta-note format.
- `planning/knowledge/legacy-reconciliation/TEMPLATE.md` — unchanged.
- `planning/knowledge/documentation-verification/TEMPLATE.md` — unchanged.

**Required**: files actually committed, plus a fresh downstream
usability exercise (a fresh `general-purpose` agent, given only the
updated template repository, attempts the workflow on a small invented
non-CodeCompass scenario) — findings fixed before this phase's own
Definition of Done is met.

## 12. Definition of Done — workflow/template completion is tracked separately from strict clean-room validation

**Corrected this revision, per the user's own explicit instruction**:
removing the human-review gate (second revision) must not be read as
license to also soften the isolation requirement. This Definition of
Done is split into two explicitly separate tracks, reported separately,
never merged into one "done" verdict:

### 12.1 Workflow and template completion (can be fully satisfied)

1. Schema correction + both new checks (§4.2) implemented,
   `check_knowledge_base.py --strict` passing.
2. Assertions produced and adversarially reviewed (§5.1).
3. Snapshot created, cited correctly, integrity check passing (§5.2-5.3).
4. Implementation reconstruction complete, model-blind and legacy-blind
   (§7.1); comparison complete, citing the snapshot, with no automatic
   status promotion (§7.2-7.3).
5. Documentation architecture selected and complete first draft produced
   by a fresh, isolated dispatch, committed before reconciliation begins
   (§8.1-8.2).
6. Legacy reconciliation complete, every incorporated claim re-grounded
   (§8.3); reconciled result published into real, active documentation
   (§8.4).
7. Documentation-only Q&A run against frozen questions, independently
   verified, material findings fixed (§8.6).
8. Coding-context task frozen, packet generated from the same snapshot,
   independently assessed with the existing context-quality rubric (§9).
9. Propagation demonstrated in a disposable fixture, reaching both
   derived-output kinds, with the fixture deleted and no synthetic
   contradiction left in real canonical knowledge or documentation
   (§10.4).
10. Template deliverables committed, fresh downstream usability exercise
    run, findings fixed (§11).
11. Standard closeout (`CLAUDE.md` §5): docs drift audit, phase retro,
    learning triage, independent `release-phase-auditor` completion
    audit, terminal `roadmap-context-curator` reconciliation.

### 12.2 Strict clean-room isolation validation (tracked separately — may remain unmet)

12. **For every isolation-sensitive scope (§6.7): all required preflight
    probes run with observed (not self-reported) transcripts persisted
    (§6.3, §6.10).** The **label actually achieved** — `verified` /
    `filesystem-only, network-exposed` / `best-effort` — is reported
    exactly, per scope, with no rounding up. **Given §6.1's own finding,
    the honest expectation, stated in advance, is that at least the
    network dimension will not reach `verified` for any scope that needs
    `Bash`** — this is reported as **unmet** for those scopes, explicitly,
    not folded into an overall "done" verdict alongside track 12.1.

**A phase report that says "done" without separately, explicitly stating
track 12.2's own per-scope labels is incomplete.** Track 12.1 can be
fully satisfied while track 12.2 remains partially or wholly unmet — this
is the expected, honest, disclosed outcome this revision requires,
not a failure condition to be argued around.

## 13. Files expected to change

### 13.1 This planning commit (now)

- **Rewritten:** this file; `decisions/0066-...md` (amended in place
  again); `planning/ROADMAP.md` / `planning/CONTEXT.md`.
- **New:** `planning/phase-79-clean-room-understanding-and-documentation-reconstruction-second-amendment-prompt.md`.
- **`planning/v1-redefinition/development-methodology.md` /
  `documentation-lifecycle.md`:** amendment notes updated for this
  revision's own corrections (snapshot-not-published-docs ordering,
  alignment-is-not-verification, the public-repo isolation finding).

### 13.2 At implementation time — CodeCompass repository

- `.claude/agents/implementation-reconstructor.md` (new).
- `.claude/agents/domain-skeptic.md` (extended: comparison mode §7.2-7.3
  — no auto-promotion to `verified`).
- `.claude/agents/docs-reconstructor.md` (MODE 2 retired as a silent
  fallback; consumes the snapshot, §8.1).
- `.claude/agents/docs-maintainer.md` (extended: five-way classification,
  §8.3; fix-not-just-record for §8.6).
- `.claude/agents/context-researcher.md` (operating mode under this
  workflow documented, §6.7).
- `.claude/agents/context-evaluator.md` (new task type: coding-context
  packet assessment, §9.3 — reuses its existing charter, documented as
  an additional use case, not a new role).
- `scripts/check_knowledge_base.py` (four new checks: `check_optional_
  enum_fields`, `check_list_fields_are_inline`, §4.2; `check_snapshot_
  historical_integrity`, `check_snapshot_current_divergence`, §5.3).
- `planning/v1-redefinition/agent-led-development.md` (§2.11
  `context-researcher`, §2.13 `domain-skeptic`, §2.2 `context-evaluator`
  entries updated; new §2.14 `implementation-reconstructor`, with the
  former §2.14 "Roles deliberately NOT created" renumbered §2.15 to keep
  the roster in ascending file order).
- `planning/knowledge/<topic-slug>/**` (assertion records, snapshots,
  implementation-reconstruction report, alignment report, isolation
  manifests/preflight transcripts/access-logs/boundary-checks,
  coding-context packet + assessment, propagation-deltas from the
  disposable-fixture exercise).
- `docs/domain/concepts/<topic-slug>.md` (new or extended, §8.4).
- `docs/cli-reference.md`, `architecture/context-graph-schema.md`,
  `README.md` (updated for the topic, §8.4).
- `planning/v1-docs-reconstruction/<topic-slug>/` (staged draft +
  reconciliation report).
- Standard closeout files.

### 13.3 At implementation time — `codecompass-template` repository

- The nine `TEMPLATE.md`/guide files named in §11 (descriptions revised,
  file list unchanged in count from the second revision).
- `README.md` cross-link update.

## 14. Validation topic (unchanged)

Proposed, provisionally: CodeCompass's own first-party source/symbol
subsystem — confirmed real and available, an internal-intent-only case
that does not validate the richer external-manual case, as a complete
topic-level pilot, not whole-project redocumentation. Unchanged from the
second revision's own verification.

## 15. Roadmap placement (unchanged)

Tracked in `planning/ROADMAP.md`'s "Post-v1 development" table, cross-
referenced from Priority D's own status cell — not a new lettered
priority.

## 16. Human decision gates (unchanged in kind, one new open technical question)

One real judgment call, presented for review: the validation topic
choice (§14). No gate in this revision requires a specific named human to
act before the phase can be reported done (unchanged from the second
revision) — track 12.2's own honest "likely unmet" isolation status is a
**disclosed technical limitation**, not a human-decision gate, and is not
resolved by waiting for a person to decide something; it is resolved (or
not) by what the preflight probes actually find.

## 17. Rollback / cleanup requirements

Unchanged, plus: the disposable fixture (§10.4) is deleted after its own
demonstration is recorded, leaving zero trace in either repository's
tracked content.

## 18. Verification commands

- `.venv/bin/pytest -q`
- `.venv/bin/ruff check .`
- `python3 scripts/check_user_docs.py --strict`
- `python3 scripts/check_knowledge_base.py --strict` (now covering four
  new checks: the two from §4.2 plus §5.3's two snapshot checks —
  `check_snapshot_current_divergence` is informational/non-blocking by
  design, §5.3 point 2, and never fails `--strict` on its own).
- At implementation time: every scope's own `<scope>.preflight.md`
  (§6.10, now covering all five probe routes) checked before that
  scope's output is treated as valid at any label; `propagation-deltas.md`
  confirmed to reference only the disposable fixture (§10.4), never a
  real canonical record.

## 19. Remaining technical uncertainties

1. **Whether the network-egress probe (§6.3) will fail to reach the
   public GitHub mirror for any isolation-sensitive scope that needs
   `Bash`** — the honest expectation, stated in advance, is that it will
   succeed (i.e. the leak is real and open) unless the underlying
   execution environment happens to block egress for reasons unrelated to
   this plan. This is not resolvable at planning time and is exactly
   what track 12.2 (§12.2) exists to report honestly either way.
2. **Whether `Agent(isolation: "remote")` will actually be available and
   working when this phase is executed** — unverifiable at planning
   time, resolved live by the preflight probes.
3. **Whether the editable-install leak (§6.6) can be fully closed without
   Tier 1 isolation** — unchanged from the second revision: a genuinely
   clean fix needs a non-editable, export-local install, real unscoped
   additional work.
4. **Whether a genuinely clean-room-capable execution environment (no
   filesystem access to the main checkout AND no network egress) is
   available to this project at all** — this revision's own honest
   answer, absent evidence otherwise, is "possibly not," which is why
   track 12.2 is designed to be reportable as unmet without blocking
   track 12.1's own real, useful completion.
