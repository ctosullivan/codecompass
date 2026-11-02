# Workflow: the self-curation loop

Phase 85. Dogfoods the existing knowledge/evidence lifecycle
(`planning/knowledge/`, Phase 54c) against CodeCompass's own
implementation, using the existing `context-researcher`/`knowledge-
curator` roles and Phase 84's read-only knowledge API
(`src/codecompass/knowledge_api.py`). No new agent role, canonical
record kind, storage, or write path beyond one narrowly-scoped addition
(the investigation log, below). Full design: `planning/phase-85-self-
curation-knowledge-quality-validation.md`.

## The eight steps

1. **Identify a bounded investigation.** A specific, named question about
   one CodeCompass subsystem's actual behaviour, arising from ordinary
   development work. Owner: the lead.
2. **Retrieve existing knowledge/uncertainty.** `knowledge_api.search`/
   `get`/`find_gaps`/`epistemic_status`, run *before* dispatching
   research, so the investigation starts from what is already known/
   unconfirmed/missing. Owner: the lead.
3. **Investigate, in `context-researcher`'s bounded self-curation
   mode.** The dispatch is explicitly framed as a Phase 85 self-curation
   investigation (see `.claude/agents/context-researcher.md`'s own
   "Self-curation investigation mode" section). The one behavioural
   difference from ordinary mode: committing `OBS-`/`EV-` records to
   `planning/knowledge/<slug>/` is **deferred** until the candidate's own
   disposition (step 4) is known — never written at all for a declined
   candidate.
4. **Classify into one of five outcomes**, before writing anything
   (`planning/phase-85-...md` §4.E):

   | Outcome | Meaning | Where it lands |
   |---|---|---|
   | 1. Accepted new knowledge | Genuinely new, previously-unrecorded, independently-reproducible fact. | `CL-`/`DE-` pair, `planning/knowledge/<slug>/`, `status: proposed` |
   | 2. Duplicate/already-known | Matches an existing, unsuperseded Claim. | Investigation log only |
   | 3. Falsified hypothesis | A specific, testable guess tried for real and found false. | Investigation log only |
   | 4. Insufficiently supported | Could not independently reproduce enough evidence either way. | Investigation log only |
   | 5. Genuine contradictory knowledge | The negative result itself overturns or qualifies an existing, still-live Claim — not merely "this guess was wrong." | `status: contradicted` Claim citing the prior one |

   Outcome 5 is deliberately narrow: the test is "would a future reader
   of the prior Claim alone be actively misled without this correction?"
   — if not, it is outcome 3 or 4, never a canonical contradicted Claim.
   Recording every falsified hypothesis as a Claim would pollute the
   knowledge model and generate persistent, meaningless
   `find_gaps()`/`knowledge_status()` noise.
5. **Collect independently reproducible evidence.** The same
   `OBS-`→`EV-` discipline `context-researcher` already uses — a real
   executed command, a real file:line read, a real Phase 83 oracle
   result citation. No new evidentiary category.
6. **Submit.** For outcome 1/5, `context-researcher`'s own commit to
   `planning/knowledge/<slug>/` *is* the submission. For outcome 2/3/4,
   nothing is written there — the investigation-log entry (step 7) is
   the submission instead.
7. **Independently adjudicate — two sub-steps, never one.**
   - **7a, `knowledge-curator`**: independently reproduces the cited
     evidence (never trusts `context-researcher`'s own say-so), split by
     the cited Observation's own `method`:
     - `source_read`/`doc_read`/`code_read` — reproduced directly
       (`Read`/`Glob`).
     - `grep_search` — reproduced directly (`Grep`).
     - `executable`/`targeted_probe`/`test_run`/`test_execution`/
       `static_analysis` — `knowledge-curator` has no `Bash`; it
       specifies the exact command and ends its report with "lead: run
       `<command>` to confirm," the lead executes it unmodified and
       reports the real output back.
     - Any other/unrecognised `method` — reported as unclassifiable;
       never silently treated as reproduced.

     Recommends one of the five outcomes above. For outcome 2/3/4, also
     writes and finalises the investigation-log entry itself (its own
     narrow write-boundary addition). Never writes a canonical Claim/
     Evidence/Observation/Decision/Requirement record.
   - **7b, the lead**: applies the recommended disposition — edits the
     Claim's own `status`/`evidence_support_state` for outcome 1/5
     (the only role that may do this), or confirms an outcome-2/3/4 log
     entry is complete.
   - **Disagreement**: the lead never overrides a documented independent
     disagreement by picking a side — it must independently re-reproduce
     the disputed evidence itself first. An "upgrade" disagreement (a
     declined candidate `knowledge-curator` believes should have been
     outcome 1/5) is resolved by re-dispatching `context-researcher` with
     its own preserved report content to commit the record, which then
     goes through 7a/7b again.
8. **Requery.** The lead re-runs the exact step-2 queries against the
   now-updated slug, confirming `get()`/`trace_evidence()`/`find_gaps()`
   reflect the outcome (or, for outcome 2/3/4, that `planning/knowledge/`
   is untouched).

## The investigation log

`planning/retros/phase-85-self-curation-investigation-log.md` —
append-only, like `promoted.md`/`_audit-phase-84.md`, never a canonical
knowledge-record kind. Records every outcome-2/3/4 candidate, so a
rejected hypothesis keeps its own stable identity, evidence, and
reviewer without ever entering `planning/knowledge/`. One entry per
investigated candidate: `id` (`SCI-NNN`), `hypothesis`,
`investigation_scope` (what was examined + repository revision),
`evidence` (every command/file:line + real output), `reviewer`,
`disposition` (`duplicate`/`falsified`/`insufficient`/
`contradicts:<CL-id>`), `reason`, and an optional `related_knowledge`
pointer.

## On-demand knowledge-quality validation

`python scripts/check_self_knowledge_quality.py [--strict]` — a
maintainer-only, report-only-by-default script, mirroring `check_
contracts.py`/`check_knowledge_base.py`'s own exact convention. Composes
`knowledge_api.find_gaps()`, `knowledge_intermediate.knowledge_status()`,
a corpus-wide `missing_evidence` scan (via `trace_evidence()`), a
missing/malformed `test_ref`-file check, and deterministic duplicate/
overlap detection. Never duplicates `knowledge_api.py`'s own logic, never
calls an LLM, and makes no change to canonical knowledge. See the
script's own module docstring for the full severity rules — notably,
`missing_contract` is always informational: no existing decision
currently mandates an oracle contract for any subject but
`balance-from-spec` (`decisions/0081` §3).

## What this workflow does not do

No continuously running background process; no automatic, unchecked
promotion of an agent's own assertion; no new canonical storage or
record kind; no change to the evidence bar any other promotion in this
project's history already requires. A self-curation pass's own narrative
is never cited as its own evidence — only a reproduced `OBS-`/`EV-`
citation, or a real oracle result, counts.
