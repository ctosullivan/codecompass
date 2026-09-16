# Phase 54 reference-ingestion experiment

Real, tested, but deliberately **outside `src/codecompass/`** for this
phase — see `../../phase-54-heterogeneous-reference-material-experiment.md`'s
"Design decisions". Implements the pipeline the phase's governing prompt
proposed, for exactly one reference source (hledger) and exactly the
selections one real Ledgerkit task needs (a `tag:` query-semantics
brief):

```
references.toml -> resolve tag to commit -> references.lock
-> fetch/cache -> extract selected files/sections -> index with provenance
-> relate to Ledgerkit code/tests/docs
```

## Files

- `references.toml` — declares the hledger source and every selected
  file/line-range, with a human-readable `note` on why each was chosen.
- `references.lock` — generated; records the resolved commit + a
  content hash per selection. Regenerate with `python reference_pipeline.py`.
- `reference_pipeline.py` — the pipeline itself: `load_references_toml`,
  `resolve_ref`, `resolve_and_extract`, `write_lock`,
  `write_extracted_markdown`, `run_pipeline`, plus
  `match_compat_register_evidence` (the §3.3 relation fallback — see
  below).
- `extracted/*.md` — the pipeline's actual output: one Markdown file per
  selection, YAML frontmatter provenance block + the excerpt itself.
- `tests/test_reference_pipeline.py` — runs against the real, already-
  pinned local hledger clone (`/home/cormac/projects/hledger`) and the
  real Ledgerkit compat-register (`/home/cormac/projects/ledgerkit`);
  skips itself if either isn't present. No live network call in any
  test (`decisions/0014`'s posture, honoured here too).
- `baseline-tag-query-brief.md` / `treatment-tag-query-brief.md` — the
  phase's own comparison-task write-ups (see the plan's §4/§6).

## Reproducing

```bash
cd planning/reference-projects/ledgerkit/reference-experiment
python reference_pipeline.py            # regenerates references.lock + extracted/
python -m pytest tests/ -v
```

To reproduce the treatment run's `codecompass` side: copy a fresh
Ledgerkit working tree to a scratch location (never the real clone —
this repo does not commit one), copy `extracted/hledger-tag-query-*.md`
into `dev-docs/hledger-reference/` inside it, then run `codecompass
sync --budget 0` and `codecompass query relations
dev-docs/hledger-reference/<file>.md` from that scratch copy.

## What this phase found (see the plan/retro for the full account)

- **Detection** of the ingested material works with **zero CodeCompass
  code changes** — `spec_docs.py`'s existing `dev-docs/**/*.md` glob
  (Phase 49) already reaches it.
- **Mechanical relation detection** (`mentions_artifact`) found **zero**
  edges between the ingested material and anything else in the project
  — `spec_doc`-kind rows never get a `name`, and `mentions_artifact`
  only matches named artifacts. A real, reproducible negative result for
  the plan's §3.2 hypothesis.
- **`match_compat_register_evidence`** (this module) is a real, tested
  fallback: it parses a Ledgerkit compat-register YAML's own structured
  `evidence.ref` citations and matches them against `references.lock`'s
  selections by file+overlapping-line-range — demonstrated working
  against the real, already-published `LK-COMPAT-QUERY-DATE-001.yaml`.
  Not currently wired into `context-graph.db` — a candidate for Phase
  55/GATE DD to weigh, not something this phase's own scope ships as a
  CodeCompass feature.
