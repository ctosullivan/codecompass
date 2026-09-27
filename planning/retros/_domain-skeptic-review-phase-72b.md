# Domain-skeptic review — Phase 72 freshness reconciliation, follow-on pass

## Scope

Follow-on to `planning/retros/_domain-skeptic-review-phase-72.md`
(`EV-SKEP-006`/`OBS-SKEP-007`), same cluster. `docs-reconstructor`'s
per-phase drift audit (`planning/retros/_drift-audit-phase-72.md`,
committed at `f2f7cbf`) found remediation commit `336b4cd` — which fixed
four "Stage E's own future Domain stage" citations — left three sibling
instances of the identical "Stage C/E" pattern unfixed in the same
files, plus a weaker fourth citation-staleness candidate. Independently
checked per this role's charter (`decisions/0060`,
`planning/phase-63d-domain-reconstruction.md` §4), not taken on the
audit's own framing.

## What I checked

- Read the current text at `docs/domain/concepts/decision.md:27`,
  `:101`, `docs/domain/concepts/observation.md:51`, and
  `docs/domain/concepts/evidence.md:106` directly, in full page
  context.
- Re-read `decisions/0062` in full (Decision, Alternatives,
  Consequences).
- Re-read `planning/v1-redefinition/conditional-generalisation.md:27-33`'s
  own 2026-09-27 amendment note.
- Grepped `planning/v1-redefinition/roadmap.md` for every `## STAGE`
  heading to confirm the full A–G lettered-stage scheme and each
  stage's current status label.
- Grepped `planning/pre-v1-disposition.md` and `planning/ROADMAP.md`
  for "Stage C" — zero hits in either current planning document.
- Re-read `relationship-edge.md:38-46`'s already-corrected sentence
  verbatim, as the template.
- Ran `git show 336b4cd -- docs/domain/concepts/relationship-edge.md
  docs/domain/concepts/decision.md docs/domain/concepts/claim.md
  docs/domain/open-questions.md` to see exactly what wording the prior
  fix used and exactly what it left untouched.
- Read `CL-EVID-009.yaml`, `CL-EVID-011.yaml`, `CL-EVID-003.yaml`,
  `CL-EVID-012.yaml` in full to determine which superseding Claim
  correctly backs the specific fact `evidence.md:106` cites.
- Ran `scripts/check_knowledge_base.py` after appending new records —
  no findings.

## Verdict: genuine staleness, same pattern as `EV-SKEP-006` — the drift audit's framing is accurate, not overstated

### Three confirmed-stale instances

- **`docs/domain/concepts/decision.md:27`** — "Those queues promote
  into a Stage C/E *roadmap* decision (an ADR, a new detection
  heuristic, a new graph capability)..."
- **`docs/domain/concepts/decision.md:101`** — "**Narrower cousin of →
  a Stage C/E gated roadmap decision** reached via
  `context-gaps`/learning-lifecycle promotion..."
- **`docs/domain/concepts/observation.md:51`** — "...its promotion path
  is a Stage C/E gated roadmap decision."

All three describe the identical `context-gaps`/`context-observations`
→ gated-ADR promotion mechanism `relationship-edge.md`'s own
already-corrected sentence describes, and all three name "Stage C" and
"Stage E" together as a currently-live gate pair. Confirmed both labels
are retired, not just "Stage E":

- `decisions/0062`'s own words: "The old Stage E phase grouping (Phases
  56-59...) is superseded as a phase group."
- `conditional-generalisation.md`'s own 2026-09-27 amendment, in its
  own voice, goes further than "Stage E" alone: "post-v1 work is no
  longer organised into lettered stages **at all**" — this necessarily
  covers "Stage C" as a future-destination label too, not only "Stage
  E."
- Independently confirmed "Stage C" was already historical, not merely
  newly retired: `planning/v1-redefinition/roadmap.md`'s own `## STAGE
  C` heading reads "· **COMPLETE** (GATE DB ratified 2026-09-13; GATE DC
  confirmed 2026-09-14)" — a finished phase group, not a live promotion
  destination — and "Stage C" does not appear anywhere in
  `planning/pre-v1-disposition.md` or `planning/ROADMAP.md`'s current
  post-v1 structure.

This is exactly `EV-SKEP-006`'s pattern repeated: an unrelated planning
restructure invalidating an interpretive gloss layered on top of an
otherwise-unedited, still-true mechanism. The underlying fact — a
context-gap or agent-suggested edge only becomes a real graph fact
through a separately-gated ADR, per `decisions/0051` — is exactly as
true as before; only the two lettered labels naming which future gate
pair does the gating have gone stale. `docs-reconstructor`'s framing in
`_drift-audit-phase-72.md` §3 is accurate on this point, not overstated.

### One confirmed weaker instance: a stale citation, not stale prose

`docs/domain/concepts/evidence.md:106`'s parenthetical `(CL-EVID-009)`
cites a Claim whose `status` is `superseded` (`supersedes: null`,
correctly unedited per `decisions/0060`'s append-only model) rather
than its direct replacement, `CL-EVID-011` (`status: supported`,
`supersedes: CL-EVID-009`), which carries the exact "not yet built, not
funded" fact this citation backs forward verbatim in its own
`statement` field. This is the direct sibling of `decision.md:38-41`'s
citation for the neighbouring "graph-level Decision entity-kind" fact,
which `336b4cd` already updated to cite `CL-EVID-011` alone —
`evidence.md:106`'s citation is for the graph-level *Evidence*
entity-kind specifically, which is `CL-EVID-009`/`CL-EVID-011`'s own
subject, not `CL-EVID-003`/`CL-EVID-012`'s (that pair is specific to
the graph-level *Claim* entity-kind collision documented on
`claim.md`, which is why `claim.md`'s fixed citation lists both
`CL-EVID-012, CL-EVID-011` while `decision.md`'s lists `CL-EVID-011`
alone). So `evidence.md:106` should match `decision.md`'s
single-citation pattern, not `claim.md`'s two-citation pattern. This
resolves the drift audit's own hedge ("may be part of the unchanged
remainder of CL-EVID-009's statement") — the fact is indeed unchanged,
but per `decisions/0060`'s model a citation should point at the
current, `supported` Claim carrying it forward, exactly as `336b4cd`
already did for the sibling `decision.md` citation. Treating this as a
real finding, not merely a weaker candidate to set aside.

### None of the four requires a Claim revision

Unlike `EV-SKEP-006`'s finding (which required `context-researcher` to
revise `CL-EVID-009`/`CL-EVID-003` themselves, since the stale language
originated in the Claim records), all four fixes here are pure
corpus-prose/citation corrections traceable directly to
`decisions/0062`'s already-final text and to an already-existing,
already-`supported` Claim (`CL-EVID-011`) — no new synthesis needed.

## Resolved myself (no escalation — researchable facts, not a genuine ambiguity)

New records appended to `planning/knowledge/codecompass-domain/`:

- **`OBS-SKEP-008.yaml`** — the direct checks performed (listed above),
  with full raw results.
- **`EV-SKEP-007.yaml`** — the conclusion: genuine staleness for three
  instances, a genuine (not merely "weaker") citation-staleness finding
  for the fourth, and the exact fix for each.

### Exact fix needed (for the lead / whoever holds `docs/domain/` write access)

1. **`docs/domain/concepts/decision.md:27`** — replace "Those queues
   promote into a Stage C/E *roadmap* decision (an ADR, a new detection
   heuristic, a new graph capability)" with "Those queues promote into
   a mechanical-detection or graph-capability *roadmap* decision (an
   ADR, a new detection heuristic, a new graph capability) — the old
   'Stage C'/'Stage E' phase-group labels are retired
   (`decisions/0062`), but the same gated-ADR promotion mechanism
   `decisions/0051` describes still applies."
2. **`docs/domain/concepts/decision.md:101`** — replace "**Narrower
   cousin of → a Stage C/E gated roadmap decision** reached via
   `context-gaps`/learning-lifecycle promotion" with "**Narrower cousin
   of → a mechanical-detection or graph-capability gated roadmap
   decision** reached via `context-gaps`/learning-lifecycle promotion
   (the old 'Stage C'/'Stage E' phase-group labels for this gate pair
   are retired, `decisions/0062`)."
3. **`docs/domain/concepts/observation.md:51`** — replace "its
   promotion path is a Stage C/E gated roadmap decision" with "its
   promotion path is a mechanical-detection or graph-capability gated
   roadmap decision — the old 'Stage C'/'Stage E' phase-group labels
   are retired (`decisions/0062`), but the same gated-ADR promotion
   mechanism `decisions/0051` describes still applies."
4. **`docs/domain/concepts/evidence.md:106`** — replace the trailing
   "(`CL-EVID-009`)" with "(`CL-EVID-011`)".

No Claim/Derivation revision is needed for any of these four (contrast
`EV-SKEP-006`'s `CL-EVID-009`/`CL-EVID-003` finding, which did require
one).

## Escalations

None. All four are mechanical citation/framing corrections traceable
directly to `decisions/0062`'s already-final text and to an
already-existing, already-`supported` Claim — not a genuine, unresolved
product/domain ambiguity. Nothing here required or received a ruling
from this role; the fix is named, not applied (write boundary,
`decisions/0060`).

## Write-boundary compliance

- No edits made to `docs/domain/`, `decisions/`, `planning/
  v1-redefinition/`, or any source/design content — read-only, as
  required.
- Two new records appended under `planning/knowledge/codecompass-domain/`
  (`OBS-SKEP-008.yaml`, `EV-SKEP-007.yaml`) — Observation/Evidence only,
  no Claim, Derivation, or Decision record written.
- `scripts/check_knowledge_base.py` run after appending — no findings.
