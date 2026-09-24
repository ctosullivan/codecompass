# Milestone documentation closeout checklist

Executed at a **major milestone** — for the redefined-v1 effort that is
**Phase 69** (`planning/v1-redefinition/roadmap.md`; corrected from
this document's own original "Phase 66," which predated the Phase 63D
insertion and the Stage F/G +4 renumbering, `decisions/0056`/`decisions/0060`).
Not run per phase.

This is the operational form of
`planning/v1-redefinition/documentation-lifecycle.md` §5. It is a
checklist, not a script — steps 3, 4, 6, 7 involve judgement that must
not be mechanised. Work top to bottom; each step names its owner and its
"done" signal.

The milestone is not closed until every box is checked or explicitly
waived in writing (with a reason) in the milestone closeout artifact
(step 10).

---

## 1. Deterministic documentation checks pass

- **Owner:** lead (or `docs-maintainer`).
- **Do:** `python scripts/check_user_docs.py --strict` → exit 0. Every
  `(info)` finding has been looked at and either resolved or noted as
  deliberately accepted.
- **Done when:** exit 0, and no un-triaged `(info)` findings.

## 2. Blank-slate reconstruction done

- **Owner:** `docs-reconstructor` (MODE 2), dispatched by the lead.
- **Do:** the agent derives, from authoritative project reality only
  (source, tests, CLI `--help`, config/schema, real generated outputs,
  ADRs, current planning state — **not** the current narrative docs as a
  structure), a proposal under `planning/v1-docs-reconstruction/`:
  proposed `README.md`, proposed `docs/` set, proposed `architecture/`
  set (current-state only), and `concepts-to-retire.md`.
- **Done when:** `planning/v1-docs-reconstruction/` contains the four
  artifacts and the agent has returned a summary of the biggest
  divergences from the current docs.

## 3. Comparison / reconciliation done

- **Owner:** lead + `docs-maintainer`.
- **Do:** for **each** current doc and each proposed doc, record a
  decision — retain / rewrite / consolidate / split / replace / remove /
  preserve-only-in-historical-state — with a one-line rationale, in
  `planning/v1-docs-reconstruction/reconciliation.md`. Then action the
  decisions.
- **Expected large item:** `architecture/overview.md` split into a lean
  current-state document + history moved out (to ADR addenda where it's
  rationale, dropped where git history already covers it). The
  `docs-maintainer`'s per-phase "split candidates" flags feed this.
- **Done when:** `reconciliation.md` covers every doc; every decision is
  actioned or scheduled with an owner.

## 4. Obsolete current documentation deleted (not annotated)

- **Owner:** `docs-maintainer`.
- **Do:** remove docs / sections the reconciliation marked
  remove / preserve-only-in-historical-state. Deleted, not wrapped in a
  "this section is outdated" note.
- **Done when:** `git status` shows the deletions; no "outdated"/"legacy"
  wrapper notes remain in current-truth docs.

## 5. Link / example / reference validation passes

- **Owner:** lead.
- **Do:** re-run `python scripts/check_user_docs.py --strict` after the
  reconciliation edits (links moved/renamed docs are the usual break).
  Spot-check that `README.md`'s quickstart steps work verbatim against a
  scratch project.
- **Done when:** exit 0; quickstart confirmed by running it.

## 6. Architecture documentation review — current-state only

- **Owner:** lead + `docs-maintainer`.
- **Do:** read every `architecture/**` doc end to end. Confirm it
  describes *what exists now*, with no "Phase N added… later changed…"
  narration, no "superseded by" pointers inline (those live in ADRs), no
  historical footnotes.
- **Done when:** a reviewer can read `architecture/` and not be able to
  tell from it alone how the system got here — only what it is.

## 7. ADR status review

- **Owner:** lead.
- **Do:** every ADR has an accurate `Status` (Accepted / Superseded by
  NNNN). Every ADR superseded during the milestone carries its "superseded
  by" addendum (a note, not an edit to the original decision). Every
  non-obvious tradeoff decided during the milestone that lacks an ADR
  gets one now. `check_adr_status_and_supersedes` passes.
- **Done when:** the check passes and the lead has eyeballed each ADR
  touched this milestone.

## 8. Final current-doc freeze for the milestone

- **Owner:** lead.
- **Do:** announce the freeze. No further current-truth doc edits until
  after the tag — except fixes to problems the freeze review itself
  surfaces.
- **Done when:** freeze declared in the closeout artifact.

## 9. Phase retros reviewed in bulk

- **Owner:** lead + `knowledge-curator`.
- **Do:** read every `planning/retros/phase-NN-*.md` since the last
  milestone. Extract recurring process feedback. Anything actionable
  becomes a `knowledge-curator` promotion — a workflow edit, a roster
  change, a `CLAUDE.md` proposal — and is distilled into the closeout
  artifact.
- **Done when:** each retro's "Process-improvement feedback" section has
  been dispositioned (actioned / filed as a candidate learning /
  consciously dropped).

## 10. Milestone closeout artifact written

- **Owner:** lead.
- **Do:** write `planning/<milestone>-closeout.md` (for redefined-v1:
  `planning/v1-closeout.md`) — architecture summary, what shipped, what
  was deferred + revisit triggers, key ADRs, reference-project evaluation
  results, distilled process lessons from the retros, any waived
  checklist steps with reasons.
- **Done when:** the artifact exists and covers all of the above.

## 11. Git tag / release preserving the complete historical state

- **When:** this step is **Phase 70** (redefined-v1), not Phase 69 —
  steps 1–10 above are the Phase 69 documentation closeout; the release
  itself is the next phase and its own human-decision gate. *(Corrected
  from this document's own original "Phase 67"/"Phase 66" — see the
  header note above.)*
- **Owner:** lead — **human-decision gate G9** (redefined-v1).
- **Do:** only after every step above. Bump the version (drop `.dev0`),
  promote `CHANGELOG.md`'s `[Unreleased]` to a dated section — **flatten
  it to canonical Keep-a-Changelog type grouping** (`Added` / `Changed` /
  `Fixed` across the whole release, not per-phase subsections) at the
  same time — `git tag`, and (if releasing) `twine upload`. Irreversible —
  needs explicit user go-ahead.
- **Done when:** tag pushed; `CHANGELOG.md` has the dated, type-grouped
  section.

---

## Not in this checklist

- Per-phase documentation upkeep (that is `docs-maintainer` +
  `docs-reconstructor`'s per-phase drift audit, every phase — see
  `documentation-lifecycle.md` §2 / §2.5).
- Deciding *whether* to release — that is the milestone's own
  human-decision gate, referenced in step 11.
