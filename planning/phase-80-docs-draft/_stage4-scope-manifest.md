# Phase 80 Stage 4 — fresh documentation draft export scope manifest

Export root: `/tmp/claude-1000/-home-cormac-projects-codecompass/0b2afcc0-cb03-48e4-8480-bf16722dc977/scratchpad/phase80-docs-draft-export`

## Included

- `knowledge-base/snapshot-codecompass-overview-v1.toml` + the 94
  Claim/Evidence/Derivation YAML files it cites (verified evidence, not
  legacy narrative).
- `phase80-implementation-reconstruction.md` (Stage 2's model-blind
  reconstruction report).
- `phase80-alignment-report.md` (Stage 3's comparison, including its own
  explicit "what to draft from / what to exclude" guidance).

## Explicitly excluded

- `README.md`, `docs/`, `architecture/`, `ai-docs/`, `CLAUDE.md`,
  `CONTRIBUTING.md`, `decisions/`, and all other `planning/` content —
  no legacy narrative, no inherited headings/structure. This is the
  isolation boundary that matters for Stage 4: not "no implementation
  evidence" (the reconstruction report IS implementation evidence,
  already cross-checked in Stage 3 with zero conflicts), but "no
  existing published prose to anchor on."

## Isolation tier

Tier 2 (curated same-host export), `best-effort` only — same posture as
Stages 2/3 and Phase 79's own established labelling.
