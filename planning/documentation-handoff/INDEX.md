# Handoff index and selection criteria

## A note on `documented_revision` values you may see mentioned in this package

**Added 2026-10-09, cold-reader finding #3.** `CLEANROOM-MANIFEST.yaml`'s
own `documented_revision` field is the single authoritative value for
"what revision is this handoff built from" — always trust that field
over any other number. Some individual files in this package may
mention a different, older revision in their own prose (e.g. a note
dated when that specific file was last substantively written or
checked, as part of this handoff's own iterative preparation process).
That is a record of *when that file's own content was last verified*,
not a claim that the rest of the handoff reflects a different, older
state than the manifest says. If you find this confusing for a specific
file, prefer what the file's own content literally shows you over any
revision number attached to it, and treat the manifest's own field as
the one number that actually describes "now."

**Format clarification (2026-10-09, cold-reader finding #2, tenth
pass):** every `documented_revision`/`handoff_commit` value in this
package — including the manifest's own authoritative one — is always a
Git commit SHA (short or long form), never a sequential build number,
timestamp, or anything else. A short SHA is 7+ hexadecimal characters
(`0`–`9` and `a`–`f`); it can, by coincidence, consist entirely of
digits with no letters (as the current `documented_revision` does) and
still be a perfectly real, valid SHA — not a different kind of
identifier. If you need to describe "the revision this documentation
reflects," describe it as a Git commit reference, exactly as given,
regardless of whether it happens to look numeric.

## Files in this handoff

- `README.md` — what/why/how, start here.
- `SOURCE-OF-TRUTH.md` — evidence hierarchy, conflict handling.
- `DOCUMENTATION-TARGET.md` — required output coverage/structure.
- `OPEN-QUESTIONS.md` — every currently-known open question/conflict
  across the selected knowledge slugs.
- `CITED-EXCERPTS.md` — real, verbatim excerpts from specific evidence
  paths that are otherwise excluded from your workspace (e.g.
  `vendor/typer/CLAUDE.md`, real captured `examples/toy-project/`
  output), included because a specific Claim cites them and a citation
  you cannot open at all is not independently verifiable.
- `DISPOSITION-REPORT.md` — **orchestrator-facing only, not writer
  evidence** — records what happens to every pre-existing documentation
  file; included in this directory for the orchestrator's own later
  integration step, not because the writer needs it (it names old file
  paths, which carries no information the writer can act on from inside
  an isolated workspace with no access to those paths anyway).
- `knowledge/overview.md`, `invariants-and-constraints.md`,
  `interfaces-and-behaviours.md`, `tests-and-acceptance.md` — direct
  copies of the real, currently-rendered canonical projections for the
  selected slugs (see below), frozen at handoff-build time.
- `knowledge/workflows-and-state-transitions.md`,
  `edge-cases-and-compatibility.md` — curated syntheses (content-selected,
  not a render target), built by hand from the selected slugs' own
  canonical Claims.
- `knowledge/decisions-and-rationale.md` — a mechanically-generated
  title+status index over every ADR in `decisions/**` (the writer never
  sees the ADR corpus itself).
- `knowledge/source-and-evidence-map.md` — a mechanically-generated index
  from every Claim shown above to its own supporting Evidence's real
  `source_ref`/`doc_ref`/`test_ref`/`observations` trail.

## Handoff selection — which knowledge slugs, and why (plan §9.6, Amendment 6)

CodeCompass's own `planning/knowledge/` currently holds five slugs, all
five re-rendered and drift-checked for repository-wide consistency during
this preparation pass (`all_rendered_knowledge_slugs` in the manifest).
**Only four are selected into this handoff** (`handoff_selected_slugs`):

| Slug | Selected? | Reason |
|---|---|---|
| `codecompass-domain` | **Yes** | Project-wide domain knowledge — the clear, default case for a project-level redoc. |
| `first-party-source-symbols` | **Yes** | Describes a real, current CodeCompass capability (first-party source/symbol indexing) that a complete project redoc genuinely needs to explain. |
| `haskell-api-surface-extraction` | **Yes** | Describes a real, current CodeCompass capability (Haskell API surface extraction) for the same reason. |
| `doc-origin-pinned-reference` | **Yes** | Describes a real, current CodeCompass capability (doc-origin pinned-reference tracking) for the same reason. |
| `hledger-depth` | **No** | About a specific reference-project (Ledgerkit/hledger) engagement, not about CodeCompass's own implementation — exactly the case plan §9.6 names as *not* belonging in a project-level handoff by default, as distinct from a phase-scoped context packet, where it already correctly lives (`planning/knowledge/hledger-depth/context-packet.md`). |

This selection is the orchestrator's own judgment call, made and recorded
here — not an automatic "include everything that exists" default.
