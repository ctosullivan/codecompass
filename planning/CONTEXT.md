# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and
`planning/retros/` for history; per `CLAUDE.md` §4, this file is for
session-resumption, not a project history.

## Current phase

**Phase 87 — Documentation Schema and Knowledge-Compiled
Documentation — restructured into three stages (87A/87B/87C); Stage
87A implemented, hardened, and independently re-audited (second pass,
PASS WITH NON-BLOCKING OBSERVATIONS); Stage 87B implemented and now
**done** (2026-11-07) — a two-document schema-governance extension,
project-wide `docs maintain` discovery, a cross-document region-id
uniqueness check, a publication-time concurrency guard, a real
sandboxed execution harness, and a genuine, worktree-isolated
knowledge-change demonstration with comparator, all independently
audited through a real FAIL→fix→PASS cycle, then **hardened a fourth
time (2026-11-09, same day)** against a further publication-integrity
defect (`schema_section_sha256` covered only a schema section's own
dict, never the schema's top-level `document`/`audience`/
`acceptance_criteria` fields, letting an already-reviewed draft be
silently retargeted to a different, never-reviewed-against document
after both reviews had passed), fixed with a new shared
`doc_compiler.compute_schema_section_identity_sha256` and 11 new
regression tests, independently audited **PASS** (see "What was just
completed" below for the full account); Stage 87B is now hardened
against four found-and-fixed publication-integrity defects total
across its history. Stage 87C's plan (§S) was then **amended** the
same day to correct several factual/scope inconsistencies a fresh
governing task found after §S's own first review round (Getting
Started's section/verification counts, the Concepts compilation scope
resolved to 4 pages, schema/document/region arithmetic corrected to 6
total schemas, the incremental-change proof's second affected region
swapped to a verified, already-shared `CL-ADPT-005` dependency, a
comparator setup-vs-marginal cost split and predeclared threshold, a
new §S.4a safe existing-document migration procedure, and a new §S.9a
exit-gate cross-check), independently re-reviewed a second time:
**READY WITH NON-BLOCKING OBSERVATIONS**, after finding and the lead
correcting two citation-accuracy defects (a misattributed quote; a
mischaracterised `decisions/0085` §6 citation). Implementation
remains separately, explicitly **not authorised** — the plan
authorises nothing beyond itself; Phase 87 overall remains `not
done`.** Plan:
`planning/phase-87-documentation-schema-knowledge-compiled-documentation.md`.
A second review (after the first pass's own READY WITH NON-BLOCKING
OBSERVATIONS verdict) found the single-stage scope too large and four
real implementation-contract defects (§G: grounded-region identifiers
must be hyphenated, not dotted — the real parser truncates at `.`;
`prepare_cleanroom_branch.py` exports from a pinned git revision, never
working-tree disk, so a runtime evidence packet needs its own
ephemeral hash-verified handoff, not an allow-list change; reader-
visible citation display and always-on machine-readable grounding are
separate concepts; an untagged factual claim needs its own explicit
completeness question, folded into the existing claim-verification
dispatch). The plan was restructured (§D/§E/§F split by stage) and all
four defects corrected, independently re-reviewed to **READY WITH
NON-BLOCKING OBSERVATIONS** (§M).

**Stage 87A — implemented, independently audited, PASS WITH
NON-BLOCKING OBSERVATIONS (2026-11-04)** after one FAIL round (missing
DoD paper trail: this file, `ROADMAP.md`, `CHANGELOG.md`, the phase
retro, a persisted drift-audit report, learnings triage,
`docs/reference/cli.md`, and an architecture doc were all still
reflecting the pre-Phase-87 state despite the implementation itself
being independently confirmed solid — closed in the same session, see
`planning/retros/phase-87-stage-87a-knowledge-compilation.md`).
Delivered: `src/codecompass/doc_compiler.py` (knowledge resolution/
hydration/gap-detection/citation-scope-check/publish/maintain),
`scripts/check_doc_schema.py` (schema validator), `scripts/
compile_doc_section.py` (the clean-room section-compilation adapter,
using a corrected ephemeral evidence handoff rather than
`prepare_cleanroom_branch.py`'s git-revision export), a new
`codecompass docs schema-init|compile|publish|maintain` CLI group. A
real, complete, end-to-end demonstration ran three times against the
real repository (no mocking, no synthetic fixture): round 1 and round
2 both correctly FAILED independent review (an invented elaboration
not in the cited record; auditor-facing phrasing and a self-referential
terminology tangent — plus two real implementation bugs the process
itself caught: a stray-space citation-stripping defect and a
schema-slug dot-truncation defect, both fixed with regression tests);
round 3 passed both independent dispatches and was published —
`README.md`'s "Understanding Digests" section, grounded in
`CL-CTXT-005`.

**Stage 87A hardening pass — implemented, first independent audit
FAIL, fix round complete, re-audit pending (2026-11-04)**, plan's own
§N. A follow-up review found three integration defects in the
publication path itself (not the compiled content or the real
demonstration, both independently reconfirmed sound first): `docs
publish` accepted a manually typed verdict string as sufficient
evidence of independent review — fixed by a new `docs record-review`
command that persists each review bound by hash to the exact draft/
evidence/schema-section identity, validated by `docs publish` instead
of trusted at face value; the publication write target was unconfined
— fixed by a single, reusable `doc_compiler.resolve_publication_target`
(confines to `README.md`/`docs/**/*.md`, symlink-aware, resolved-path
comparison, never a string-prefix check), enforced at both
schema-validation and publish time; the clean-room broker's prompt was
built from the in-memory evidence packet rather than its own verified
on-disk bytes — fixed by sourcing the prompt from a fresh read of the
verified file, with the ephemeral staging directory always removed on
both the success and failure path.

**The first `release-phase-auditor` dispatch against this hardening
work returned FAIL** — not on the three fixes themselves (independently
re-confirmed sound) but on three process defects in the *same* commit:
(1) this file and `ROADMAP.md` asserted "independently re-audited" for
the hardening pass before any such audit had actually run — the exact
audit-sequencing failure mode this pass's own §N.D exists to prevent,
recurring in a new, self-contradictory form; (2) the claimed "21 new
regression tests" overstated the real, reconciled count (the real
delta across `tests/test_cli.py`/`tests/test_compile_doc_section.py`
was 15, matching the suite's own 1275→1290); (3) the schema-validation-
time half of the path-confinement fix (`check_doc_schema.py`'s
`_check_document_path`) had no direct regression test. All three fixed
in the same session: this file's own prose corrected to accurate tense;
the test count corrected and 4 new tests added for the previously-
uncovered schema-validation-time path (`tests/test_check_doc_schema.py`,
14 → 18); total new regression tests across this hardening pass: 19
net (`test_cli.py` +12 net from 13 newly-written tests replacing 1
pre-hardening test that encoded the old CLI contract; `test_compile_
doc_section.py` +3; `test_check_doc_schema.py` +4). Full suite 1294
passed, 2 skipped; ruff and all strict validators re-confirmed clean
(Phase 85 baseline unchanged). One candidate learning filed and
triaged (`L-120`, retained).

**A second, fresh `release-phase-auditor` dispatch against the fix
round's own commit independently re-confirmed all three FAIL-driving
defects genuinely closed** — including by directly reproducing the
"13 confirmed failing pre-fix" claim itself (a disposable `git
worktree` at the pre-hardening commit, not merely re-reading the prior
claim) — and returned **PASS WITH NON-BLOCKING OBSERVATIONS**: three
minor wording/cross-reference clarity issues (a confusingly-phrased
test-count sentence in `CHANGELOG.md`; a dangling cross-reference in
the retro's "Lessons learnt" section; the retro's "Where we're going"
not naming the re-audit itself as the immediate next step), none
asserting an event before it happened, all fixed in the same session.
**Stage 87A's hardening is genuinely closed.** Full detail: `planning/
retros/phase-87-stage-87a-hardening.md`,
`planning/retros/_audit-phase-87-stage-87a-hardening.md` (both the
original FAIL and the re-audit's PASS WITH NON-BLOCKING OBSERVATIONS
sections, preserved append-only).

**Stage 87B now has an implementation-ready plan (plan's own §O),
independently reviewed to READY across three rounds total: §P (the
first round found and the original pass fixed two blocking factual
errors against the real `docs/getting-started.md` content and command
set; the second, narrow re-check confirmed the fix), then §Q
(2026-11-05 — a separate, code-level review of the already-READY plan
found seven further findings: §O.E's comparator targeted a
non-existent `## Known gotchas` section; `docs publish` had no
publication-time concurrency check against a live human edit;
§O.C's execution-harness design had no real vendor-source redirection
mechanism and included two paid-API-triggering commands a
credential-less sandbox can never complete; §O.B's section
classification conflated compiled/schema-governed/factually-verified
into one axis, missing that `## After the first run` makes real
implementation claims; §O.D cited `acknowledge_stale_grounded_region`
as if it demonstrated a document update, which it structurally cannot;
no accepted canonical knowledge record actually supports the proposed
README install/first-step additions; and both pre-existing README
regions were wrongly assumed `noop` when one is a real, pre-existing,
unresolved `doc_candidate`. All seven corrected in place (§O.I),
independently re-verified against the real repository by a fresh
dispatch, and re-reviewed **READY WITH NON-BLOCKING OBSERVATIONS**
(two further narrow specification gaps found and fixed in the same
pass)) — then amended a further round the same day, finding and fixing
five more findings (including a materially strengthened
publication-concurrency design), before the governing task explicitly
authorised Stage 87B implementation.

**Stage 87B implementation then proceeded and is now genuinely
`done`.** Commit `0f6a268` delivered the full §O.D scope: the second
schema-governed document (`docs/getting-started.md`, its
self-contradicting "## First run" section corrected); project-wide
`**/*.schema.yaml` discovery so `docs maintain` with no arguments
reconciles every schema-governed document in one call, plus an
idempotency fix so repeated `maintain` runs never pile up duplicate
`doc_candidate` manifests; a new cross-document
`doc-schema-duplicate-region-id` schema-validation-time check (shared
`doc_compiler.compute_schema_slug`); and a publication-time
concurrency guard — `docs publish` now runs inside a cooperating-writer
file lock and, immediately before writing, re-detects the live
region's state via a new `doc_compiler.decide_publish_safety`,
refusing to overwrite a live human edit or a live-and-knowledge-both-
changed conflict. Commit `88cfa8d` then closed the plan's own
mandatory real knowledge-change demonstration (§O.E) and comparator:
a genuine, previously-undescribed gap in `CL-CTXT-005` (the real,
already-implemented, already-tested `sync_vendor` clone-failure
fallback, confirmed by direct code/test reading before the
demonstration began) was amended into evidence inside an isolated,
discarded `git worktree` — never touching production
`planning/knowledge/` — correctly detected by
`detect_grounded_region_changes` (alongside the real, unaffected,
pre-existing `intermediate-knowledge-layer` `doc_candidate`, left
untouched throughout), compiled, independently reviewed twice
(semantic-support and editorial-quality, both passing on the first
attempt), published through the new concurrency guard's
`claims_changed`-proceeds branch for the first time against anything
other than a synthetic fixture, and correctly reconciled by a
follow-up `docs maintain` (`noop` for the republished region, still
`doc_candidate` for the untouched finding) — confirmed by a
byte-for-byte diff that every line outside the one republished region
is unchanged. A parallel, identically-seeded comparator — a
`general-purpose` dispatch editing the same fact by hand, with no
compiler, no schema, and no citations — passed independent
semantic-support review but **failed** independent editorial review
for the same register problem Stage 87A's own writing-contract
hardening (`L-119`) was specifically built to catch; the compiled
arm's own draft passed that identical editorial bar on its first
attempt. Full account:
`planning/retros/phase-87-stage-87b-knowledge-change-demonstration.md`.

An independent `release-phase-auditor` pass against `0f6a268` plus
this closeout's own uncommitted changes then returned **FAIL**:
§O.D.3's own six-item required-regression-test list for the
concurrency guard was only four-sixths covered, and writing the
missing "two concurrent `docs publish` invocations serialise through
the lock" test surfaced a real, previously-undetected implementation
gap, not just a missing test — reproduced directly before fixing
anything: the write-boundary revalidation the design claimed existed
in fact ran only once, before the lock was acquired, with nothing
re-checking the live document or cited-knowledge state a second time
immediately before the write, so a mutation injected inside that
window (on either side) was silently clobbered. Fixed by re-running
both the grounded-region detect-and-decide and the evidence/
schema-section freshness check a second time, inside the lock,
immediately before the write — narrowing, but, per
`_doc_publish_lock`'s own docstring, honestly not fully closing (a
full transactional write would close it completely and was
deliberately not built, per this stage's own smallest-coherent-change
instruction) the remaining window between that second check and the
write itself. Three new regression tests, each confirmed to fail
against the pre-fix code first; full suite 1337 passed, 2 skipped (up
from 1334); ruff and both strict validators re-confirmed clean. Two
non-blocking numeric self-report errors in the implementation
commit's own message (claimed "47 new regression tests"/"6
pre-existing ruff findings," real figures 40/176) were corrected in
`CHANGELOG.md` rather than rewriting the already-landed commit, per
this project's own established practice. A fresh, independent
re-audit dispatch — which directly defeated the lock and shadowed the
pre-fix module to reproduce both the race and the clobber for real,
not merely re-reading the fix's own account — returned **PASS**. Full
audit trail: `planning/retros/_audit-phase-87-stage-87b.md`.

`L-121` (four real `unshare`/`pivot_root` namespace-sandbox
construction footguns — venv-mount path aliasing, missing `/dev`
nodes, an unmounted git-mirror data bind-mount, a `PATH`-less setup
chain) promoted to `docs/architecture/overview.md`'s "Known footguns".
`L-122` (the clean-room broker's own usage/cost figures are never
surfaced by `docs compile`'s CLI output, even though the data exists
in the broker's own response) filed `candidate`, now landed as a
backlog/revisit-trigger row in `planning/ROADMAP.md`'s
"Future-improvement backlog" section by this reconciliation (its own
`promoted.md` line is a separate, follow-up `knowledge-curator` step,
not taken by this reconciliation, which may not touch
`planning/learnings/**`). **Stage 87B is genuinely `done`.**

**Stage 87B post-closeout hardening pass — closed (2026-11-09).** A
fresh review of Stage 87B's already-closed, already-PASS-audited work
found three further integration defects in `docs publish`'s own
safety mechanics (none in the real demonstration's own generated
content, both independently reconfirmed sound first): (1) **reviewed-
draft integrity** — `docs publish` never verified that `draft_body`
(what actually gets written) genuinely derived from the reviewed
`tagged_draft` text, so an independently-rewritten `draft_body` could
publish unreviewed content with both review records still showing as
passing — fixed by recomputing the draft's own identity from
`tagged_draft` and cross-checking it against `draft_sha256`/
`draft_body`, re-checked a second time against a freshly re-read copy
of the manifest immediately before the write. (2) **live schema
freshness** — the write-boundary re-check added by the original
hardening pass reused schema/section objects parsed once at the top of
the request, so a schema file edited mid-publish was invisible to
every "re-check" — fixed by rereading the schema from disk and
re-resolving the section fresh on every call. (3) **residual
write-boundary race, narrowed further** — a new `doc_compiler.
document_identity`/`DocPublishConflictError` compare-and-swap catches
a document mutation landing after the detect-based re-check, and
`publish_section`'s writes now go through a new atomic
write-then-rename helper; the remaining window (between that identity
re-check and the write itself, both plain synchronous Python with no
cross-process lock) is honestly disclosed, not claimed closed, in both
`publish_section`'s and `_doc_publish_lock`'s own docstrings, and
recorded as `L-124`. 15 new regression tests (full suite 1337 → 1352
passed, 2 skipped); a fresh independent audit directly reproduced 14
of the 15 against a disposable `git worktree` at the pre-fix commit. A
real, evidence-backed `CL-CTXT-005` amendment candidate the original
demonstration surfaced was re-derived independently as `EV-CTXT-021`
and filed as `L-123` for the ordinary knowledge-reconciliation
workflow — not applied directly; a successful demonstration is still
not maintainer acceptance (see "Next concrete step" below). A first
independent `release-phase-auditor` dispatch against this hardening
commit returned **FAIL**: this work's own `CHANGELOG.md` entry falsely
claimed an audit had already run and passed before any audit had
actually been dispatched (a self-certification defect, caught directly
by the auditor), plus an overstated test-reproduction count ("13 of
15" claimed, true figure 14 of 15) — both fixed same-day, and a fresh,
independent re-audit — which directly re-verified the underlying
mechanisms, re-ran the full suite and every strict validator itself,
and confirmed no protected-file drift since Stage 87B's own prior
closeout — returned **PASS**. **Stage 87B's post-closeout hardening
pass is genuinely closed.** Full detail:
`planning/retros/phase-87-stage-87b-knowledge-change-
demonstration.md`'s "Addendum 2"; `planning/retros/
_audit-phase-87-stage-87b-hardening.md` (the FAIL);
`planning/retros/_audit-phase-87-stage-87b-hardening-reaudit.md` (the
PASS). Stage 87C (the complete minimum publication suite, the real
matched-baseline experiment) remains separately planned, **not
authorised**, and untouched by any of this work. Phase 87 itself
remains `not done` until Stage 87C's own exit gate (the complete
minimum publication suite, the matched-baseline comparison, final
audits) is met.

**Stage 87B hardened a fourth time — closed (2026-11-09, same day).**
A fresh code-inspection review of the already-twice-hardened `docs
publish` path, independent of the prior pass's three findings, found
`schema_section_sha256` (the hash every persisted review record and
pending manifest is bound to) was computed from only the schema
section's own dict, even after the prior fix bound the section's own
identity to the live schema on every re-check — the schema's
**top-level** `document` (the actual publication target), `audience`,
and `acceptance_criteria` fields were never part of that hash, at
compile time or at any publish-time re-check. Reproduced directly
before any fix was written: a standalone script compiled a section
against a schema targeting one document, recorded both passing
reviews, then rewrote only the schema's own top-level `document`
field to a different target, leaving the section dict byte-identical
— `docs publish` exited 0 and published the already-reviewed draft to
the new, never-reviewed-against target. Fixed with one new, shared
`doc_compiler.compute_schema_section_identity_sha256`, binding the
section together with the schema's `document`/`audience`/
`acceptance_criteria` fields; `docs compile` now computes the
persisted hash through it, `docs publish`'s freshness check recomputes
the identical structure from the live schema on every call
(pre-lock and at the write boundary), and the actual write target is
now also re-resolved from the live schema at the write boundary rather
than trusted from the one-time resolution at the top of the function.
11 new regression tests, each confirmed to fail against a disposable
pre-fix worktree first (full suite 1352 → 1363 passed, 2 skipped). An
independent `release-phase-auditor` dispatch independently reproduced
the exploit against that same disposable pre-fix worktree, confirmed
the fix closes it, sampled 5 of the 11 new tests directly, re-ran the
full suite and every strict validator itself, and specifically
re-checked for a recurrence of this session's earlier self-
certification defect — none found: **PASS**. **Stage 87B is now
hardened against four found-and-fixed publication-integrity defects
total across its history.** Full detail: `planning/retros/
phase-87-stage-87b-knowledge-change-demonstration.md`'s "Addendum 3";
`planning/retros/_audit-phase-87-stage-87b-second-hardening-pass.md`.

**Stage 87C's plan amended and re-reviewed a second time (2026-11-09,
same day).** A fresh governing task found and required correction of
several real factual/scope inconsistencies in the Stage 87C plan
(§S) after its own first review round: Getting Started's section/
verification counts were stated inaccurately (claimed 5-of-6
execution-verified; real: 3-of-5, the other 2 verified by two
specifically-named other tests); the Concepts compilation list named
five pages while the implementation sequence and knowledge-readiness
assessment had already, inconsistently, settled on four — resolved in
favour of four, moving `protocol-and-capability.md` to the human-
authored list; schema/document/region arithmetic referenced "five
schemas" against a real total of six (2 existing + 4 new); the
incremental-change proof's second affected region was a page never
scheduled for compilation, failing to guarantee a genuine two-
compiled-region demonstration — replaced with a verified, already-real
dependency (both `adapter.md` and `vendor-and-ecosystem.md` cite
`CL-ADPT-005`, confirmed by reading both pages' actual prose); the
comparator measured generation cost with no predeclared material-
improvement threshold or setup-vs-marginal cost split; and no existing-
document migration procedure was specified despite `publish_section`'s
own append-not-replace behaviour for an unmarked page — a real risk of
duplicating existing Concepts prose rather than governing it, closed by
a new §S.4a specifying a safe, zero-new-code migration sequence using
existing baseline/noop machinery. A new §S.9a cross-checks every
original Phase 87 exit-gate requirement against the amended plan's own
disposition. Independently re-reviewed, with the reviewer instructed
to inspect real repository files rather than assess internal coherence
alone: **READY WITH NON-BLOCKING OBSERVATIONS**. Two citation-accuracy
defects found and corrected in place: a misattributed quote, and a
mischaracterised `decisions/0085` §6 citation (§6 actually withdraws a
threshold-based criterion; the predeclared threshold is this
amendment's own voluntary strengthening, not a restored requirement).
The first review round's own verdict is preserved unchanged as
historical record. Full detail: the plan's own §S.12 "Second review
round".

**Stage 87C — implemented and independently audited PASS
(2026-11-10)** (full account under "What was just completed" below;
`planning/retros/_audit-phase-87-stage-87c.md`). Three further
`docs/concepts/` pages (`adapter.md`, `vendor-and-ecosystem.md`,
`knowledge-model.md`) were migrated into schema-governed,
knowledge-compiled regions; `context.md`'s migration was attempted and
honestly declined, left human-authored. A real `CL-ADPT-005`
multi-region maintenance demonstration and a matched-baseline
comparator (honest non-advantage result) both ran for real. A first
independent audit **FAIL** on three missing DoD artifacts (changelog
entry, an incomplete retro, no learnings filed/triaged) was fixed in
the same session; a fresh re-audit returned **PASS**. **Stage 87C is
done.** **Phase 87 overall remains `not done`**: a deterministic
`docs/reference/cli.md` generator and a semantic cross-document
consistency checker were both explicitly deferred from Stage 87C's own
scope (plan's own §S.11) and require their own separate authorisation
before Phase 87's own closeout is assessed again.

**Stage 87C corrective-closeout pass — closed (2026-11-10, plan's own
§T)**. A separately authorised corrective-review governing task, run
against the already-`done` Stage 87C after its own original PASS audit
(preserved unmodified), found and fixed five real issues: a seeded
`knowledge-model.md` doc annotation resolved through the real
`codecompass knowledge apply` reconciliation workflow (two real apply
cycles), never a hand-edited `.grounding-state.toml`; a real
canonical-knowledge governance violation — Stage 87C's own
implementation had amended `CL-ADPT-005` directly in place, violating
the supersession-only rule (`planning/phase-54c-evidence-knowledge-
workflow.md` §2.4) — fixed by restoring `CL-ADPT-005` to its original
text (`status: superseded`) and writing a new superseding Claim,
`CL-ADPT-012`, with the two dependent published regions' citations
swapped through the same real reconciliation workflow (the underlying
fact was never reverted, only the record structure); a wrong
documentation-coverage claim about `CONTRIBUTING.md` (never
schema-governed, wrongly described as one of Stage 87A/87B's compiled
documents) corrected to the real figures (5 schema-governed documents,
4 with published regions, 6 published regions, 1 further pre-existing
Phase-81-era grounded region); an explicit six-item limitations
assessment added to the matched-baseline comparator (the original two
verdicts unchanged); and `L-125`-`L-129`'s own triage independently
re-confirmed already substantive, not a rubber stamp. Verification: full
regression suite (1363 passed, 2 skipped, unchanged), applicable strict
validators clean, a fresh `docs maintain` run across all five
schema-governed documents, a fresh independent `docs-reconstructor`
pass, and a fresh independent `release-phase-auditor` pass. A first
`release-phase-auditor` dispatch returned **FAIL** (missing
`CHANGELOG.md` entry); fixed same-day; a fresh re-audit returned
**PASS** (`planning/retros/_audit-phase-87-stage-87c-corrective-
closeout.md`). **This corrective pass does not reopen or change Stage
87C's own `done` status or its original PASS audit's own verdict** —
both stand unchanged; it repairs defects found after that verdict was
reached, the same "reopened for a focused corrective pass" pattern this
project already uses for Phase 81's post-closeout corrective passes.
Full account: `planning/retros/phase-87-stage-87c-knowledge-compiled-
documentation.md`'s own "Addendum: Stage 87C corrective-closeout pass"
section.

**Stage 87D plan drafted and independently reviewed (2026-11-10, plan's
own §U/§V) — planned and reviewed only, implementation not
authorised.** Re-deriving every requirement directly from
`decisions/0085` §5-§6 and `planning/v2-roadmap.md`'s own Phase 87
section (not assumed from prior stages' retros), the plan concludes
exactly one item is genuinely outstanding against the original Phase 87
requirements: a deterministic, drift-checked `docs/reference/cli.md`/
`configuration.md` generator (§U.2, 10 top-level commands + 27
subcommands confirmed via direct Click/Typer introspection). A semantic
cross-document consistency checker (§U.3) is scoped as a voluntary,
separately gateable addition — `decisions/0085` §5 names "consistent
terminology" as an editorial requirement, but leaves it to the existing
dual-review process, not a dedicated automated mechanism — not a
closeout requirement (§U.1/§U.4). Independently reviewed: **READY WITH
NON-BLOCKING OBSERVATIONS** (§V) — four textual/precision corrections
applied (a wrong CLI subcommand count, corrected via direct
introspection, which also surfaced a second real undocumented default
on `knowledge context`'s `--max-items`/`--max-chars`; an incorrect
"one heading per command" assumption about `cli.md`'s real
synopsis-line convention; an overstated "no mention of cross-document
consistency anywhere" claim, corrected to name and address the §5
counterevidence; a named module home, `scripts/check_doc_consistency.py`,
for §U.3's new logic) — none architectural, per the review's own
finding. **Implementation is explicitly not authorised by this pass and
has not begun; a separate governing task must authorise it before any
Stage 87D code is written.** Phase 87 overall remains `not done`.

**Stage 87D plan amended after a fresh governing task found five
implementation-readiness gaps in the first §U draft, and
independently re-reviewed a second time (2026-11-11, plan's own §U.8/§V
"Second review round," commits `6e05aee`/`7d226d8`) — still planned and
reviewed only, implementation not authorised, not begun.** (A) §U.2's
default-value checker had a genuine logical contradiction — it could
only catch a documented-but-wrong default, never one omitted entirely —
fixed with an explicit four-point disclosure policy; an exhaustive
`ast`-based scan of all 37 commands (not a sample) confirmed exactly
five real undocumented defaults (`knowledge trace --relation`/
`--depth`, `knowledge context --max-items`/`--max-chars`, `knowledge
export --project-id`) and two real, already-correct positive controls.
(B) A suspected installed-package execution-boundary defect was
independently reproduced for real: a built wheel installed into an
isolated venv confirms `codecompass docs compile` crashes with an
uncaught `FileNotFoundError` trying to load a `scripts/`-resident
module `pyproject.toml` never ships — confined to exactly one command,
concluded maintainer-only (a documentation-disclosure requirement, not
a packaging fix, and not a Phase 87 exit-gate blocker); new §U.2a
documents this in full. (C) §U.2's originally-proposed new validator
script would have duplicated two checks `scripts/check_user_docs.py`
already has (`check_cli_commands_documented`, itself carrying a real
pre-existing 19-subcommand coverage gap, and
`check_vendor_config_fields_documented`) — redesigned to extend that
existing file in place instead of building a parallel validator. (D)
`L-129`'s real `codecompass undo` first-run artifact-tracking gap,
re-verified still live at current HEAD, now requires an explicit
documentation-disclosure requirement in the plan (not a fix to `undo`
itself). (E) §U.3 (cross-document semantic consistency) is now
explicitly deferred beyond Stage 87D — not a voluntary lead choice —
with its design preserved and seven outstanding specifications named
for a future, separately authorised phase. A new §U.8 states Stage
87D's exactly two mandatory deliverables (deterministic reference
assurance; final Phase 87 assurance and closeout). A second independent
planning review — re-deriving everything from scratch, including its
own independent wheel build/reproduction in a second isolated venv and
an independent `ast`-based re-derivation of the five gaps — returned
**READY WITH NON-BLOCKING OBSERVATIONS** again, with two further minor
precision corrections applied (a wrong parameter-instance count; an
overstated documentation-citation claim), neither affecting the plan's
substance. **Stage 87D implementation remains not authorised and has
not begun; Phase 87 overall remains `not done`.**

**Phase 86 — Knowledge-Placement and Code-Quality Review — is `done`
(2026-11-03)**. Plan amended and independently reviewed across four
rounds before implementation (full history: `planning/phase-86-
knowledge-placement-code-quality-review.md`'s own top section and
§12/§13) — in short: a `.md`→`.yaml` typo disclosure and a 14th-agent
design revision (rounds 1-2); deferring `docstring-contradicted-by-
oracle-result` (would have treated `INVALID`/stale oracle evidence as
a demonstrated `FAIL`) plus a real regex capture-direction bug caught
and fixed (round 3); deferring `decision-citation-status-mismatch`
(the real `decisions/0019`/`0061` relationship proves a literal
recorded-vs-effective status comparison is unsafe), widening
supersession-section scanning to title/Status/Decision/Consequences
(verified against the real corpus: exactly 8 files match), generalising
the real-dogfood acceptance criteria, and a real
`ast.get_docstring(clean=True)` line-provenance bug caught and fixed
(round 4, three issues found and fixed across two follow-up review
passes). Final verdict: **READY**.

**Implemented**: `scripts/check_knowledge_placement.py` (32 tests) —
two mechanical checks (`decision-citation-exists`, blocking;
`decision-citation-superseded`, informational) plus an always-blocking
`knowledge-placement-unparseable-source-file` diagnostic for a per-file
parse failure; `docs/concepts/knowledge-placement-policy.md`/`docs/
workflows/knowledge-placement-review.md` (the policy and the ad-hoc
reviewer's own brief — no new standing agent, confirmed by the
unchanged 13-file `.claude/agents/` roster); `decisions/0094` (the
five non-obvious tradeoffs this phase's plan amendments surfaced).
**Real dogfood**: `src/codecompass/source_resolution.py`'s own module
docstring cited `decisions/0019` (superseded by `decisions/0035` per
`decisions/0061`) as if it still justified the module's current
purpose, when the real current caller (`sync.py`'s `sync_vendor`,
`decisions/0021`/`0033`) never cites it at all — independently found
(ad-hoc reviewer dispatch), adjudicated, corrected by the lead, and
re-verified independently (a forked dispatch confirmed the rewritten
docstring now reads as historical, not current, justification).
`oracle.py`/`staleness.py` confirmed clean negative controls throughout.
`release-phase-auditor`: PASS WITH NON-BLOCKING OBSERVATIONS (`planning/
retros/_audit-phase-86.md`) — re-verified the dogfood fix, test
coverage, and all pre-existing strict-validator baselines directly,
found no gap. `L-116` filed (a plan citing a specific stdlib API name
needs that name verified by direct execution during review, not only
its surrounding logic — `tokenize.TokenizeError` does not exist, the
real name is `tokenize.TokenError`, caught on the first test run, never
committed in its broken form); `knowledge-curator` recommends
**promote** to `CLAUDE.md` §1, draft text in `planning/v1-redefinition/
proposed-governance-changes.md` §L, **pending the user's own explicit
`CLAUDE.md` §0 approval** — not yet applied; `L-116`'s own `status` is
`retained` (curation/recommendation complete, blocked only on that
pending approval, not on further investigation).

**Corrective pass closed (2026-11-03, "CodeCompass Orchestrator —
Phase 86 Corrective Closeout")**. Five findings from an independent
closeout review, none reopening the plan's own design (no new ADR —
matches Phase 85's own identical-shape precedent, `95309f1`): (A) no
`planning/retros/_drift-audit-phase-86.md` had ever been persisted — a
fresh, independent `docs-reconstructor` dispatch (not a reconstruction;
the release audit's own secondhand mention wasn't a reliable enough
source) found 2 non-blocking stale-by-omission findings in `docs/
development/contributing.md`/`docs/concepts/knowledge-placement-
policy.md`, both fixed same-day; (B) `_extract_file_citations` caught
`OSError` on a source read but not `UnicodeDecodeError` (not an
`OSError` subclass), crashing on invalid-UTF-8 source content — fixed
by widening the caught exception set; (C) `_build_superseded_map`
caught `OSError` on an ADR read and silently `continue`d — a citation
to an ADR actually superseded *by* the unreadable file would report as
clean, misrepresenting a partially-examined corpus as complete;
`UnicodeDecodeError` escaped entirely — both fixed with a new,
always-blocking `knowledge-placement-unreadable-decision-file`
diagnostic, every other readable ADR still processed, `decision-
citation-superseded`'s own informational severity unaffected; (D) the
real-dogfood regression test pinned the specific historical `decisions/
0019` citation by name, which would have broken a future, unrelated,
correct edit removing or relocating now-legitimate historical context —
refactored to assert the detector's general correctness instead,
without altering the retro's own original "Real dogfood" record; (E)
`L-116` corrected from bare `candidate` to `retained` (see above). A
sixth, optional point found a real line-provenance bug (an escaped `\n`
inside one physical docstring source line overcounted a later
citation's physical line) — fixed via a raw-source-text slice. 8 new
regression tests (32 → 40). Full suite 1206 passed/2 skipped (unchanged
baseline + the new tests); `ruff` clean; real-corpus `--strict` run: 10
informational findings, exit 0, byte-identical across two runs;
`check_contracts.py`/`check_knowledge_base.py`/`check_self_knowledge_
quality.py --strict` re-run clean against their documented baselines
(the last: 35 findings, 26 blocking/9 informational, unchanged — no
Phase 85 finding suppressed). `release-phase-auditor`'s independent
corrective re-audit: **PASS WITH NON-BLOCKING OBSERVATIONS** (one
cosmetic test-count self-contradiction in the plan's own §14, caught by
the auditor and fixed).

**Second corrective pass closed (2026-11-04)**: a further independent
review found `_docstring_citations()` sliced docstring text using
`ast`'s `col_offset`/`end_col_offset` as character offsets, when
CPython's `ast` reports them as UTF-8 *byte* offsets — a multibyte
identifier preceding an inline docstring on the same physical source
line silently lost the citation entirely (reproduced directly; every
fixture across four planning-review rounds and two prior audits had
been pure ASCII). Fixed by slicing each line's own UTF-8-encoded bytes
before decoding; filed as `L-117`, triaged by `knowledge-curator`:
**retained**, promotion to `CLAUDE.md` §1 drafted (`planning/
v1-redefinition/proposed-governance-changes.md` §M), pending the user's
own explicit `CLAUDE.md` §0 approval — not yet applied. Also fixed:
`--files`'s `nargs="*"` accepted an explicit, empty selection as an
apparently-successful zero-file scan; now `nargs="+"` (usage error,
exit 2). Corrected a stale "+7 tests" reference inside `planning/
retros/_drift-audit-phase-86.md` to "+8". Closed an audit-sequencing
gap: the first corrective pass's own re-audit (`64dba3c`) had completed
its verification *before* two later audited-scope commits (`e682994`,
`2ac5dd4`) landed, despite being recorded to disk after them — resolved
with a fresh, comprehensive `release-phase-auditor` dispatch covering
the true final state through `648be97`, the first audit to genuinely
reflect it. 4 new regression tests (40 → 44). Full suite 1210
passed/2 skipped; `ruff` clean; real-corpus `--strict` run: 10
informational findings, exit 0, byte-identical across two runs and
byte-identical to the pre-fix output (no real latent defect in this
project's own source tree). Pre-existing validator baselines re-counted
directly, all unchanged. `release-phase-auditor`'s fresh re-audit:
**PASS WITH NON-BLOCKING OBSERVATIONS** (five documentation/triage
follow-ups it named, all closed in this same session). Full detail:
the plan's own §14/§15; both retro addenda; `planning/retros/
_drift-audit-phase-86.md`; `planning/
retros/_audit-phase-86.md`'s own two appended "Corrective-pass
re-audit" sections.

Phase 85's own outstanding `--strict` baseline (35 findings, 26
blocking, 9 informational) was re-verified unchanged throughout Phase
86's own work; `L-114`/`L-107` remain retained, untouched, not
Phase-86-relevant.

**Phase 85 — Self-Curation and Knowledge-Quality Validation — is `done`
(2026-11-03)**. The plan was amended twice and independently reviewed
three times before implementation began (one material gap fixed each
round — the disposition-write split, a `Bash`-tool-boundary correction,
and three final issues: `missing_contract` severity, a `context-
researcher` write-path conflict, and an incomplete Observation-`method`
taxonomy). Delivered: `docs/workflows/self-curation-loop.md` (the
eight-step self-curation loop); `scripts/check_self_knowledge_quality.py`
+ 20 tests (composes `knowledge_api.find_gaps`/`knowledge_intermediate.
knowledge_status`/`trace_evidence`/`oracle.parse_oracle_result`;
`missing_contract` always informational per `decisions/0081` §3; a new
`test_ref`-file-integrity check scoped to contract-bearing slugs only —
an as-built fix discovered by running it against the real corpus);
`planning/retros/phase-85-self-curation-investigation-log.md` (new,
non-canonical, append-only — a five-outcome candidate-disposition
procedure keeps a merely-falsified hypothesis out of canonical knowledge
as a `status: contradicted` Claim); narrowly-scoped mode additions to
`.claude/agents/context-researcher.md` (deferred-write self-curation
investigation mode) and `.claude/agents/knowledge-curator.md`
(independent-adjudication mode, including the `Bash`-tool-boundary
reproduction split and one narrow write-boundary addition) — no new
agent role, no new tool grant. Real dogfood against `planning/knowledge/
first-party-source-symbols/`: `context-researcher` tried four genuinely
different constructs against the real, unmodified source-symbol
extractors; two defeated them (`CL-FPSS-009`, independently adjudicated
— including the lead re-running every executable probe verbatim — and
promoted to `status: supported`); two were genuinely tried and falsified
(`SCI-001`/`SCI-002`, investigation log only, nothing written to
`planning/knowledge/` for either). Both required real-dogfood outcomes
demonstrated independently; neither manufactured. No change to `src/
codecompass/knowledge_api.py`/`oracle.py`/`knowledge_intermediate.py` or
any canonical record schema. `release-phase-auditor`: FAIL (one missing
DoD artifact, a drift-audit report, reconstructed faithfully from the
underlying pass's own real findings) → re-audited PASS WITH NON-BLOCKING
OBSERVATIONS. Full detail: `planning/phase-85-self-curation-knowledge-
quality-validation.md`; retro: `planning/retros/phase-85-self-curation-
knowledge-quality-validation.md`; audits: `planning/retros/
_audit-phase-85.md`, `planning/retros/_drift-audit-phase-85.md`.

**Corrective pass closed (2026-11-03, "CodeCompass Orchestrator — Phase
85 Final Corrective Closeout")**. Two defects in `scripts/check_self_
knowledge_quality.py` fixed, each with a regression test confirmed to
fail against the pre-fix source first: (1) a `contradiction` finding
was blocking even when its subject (`CL-ADPT-008`, `status: superseded`)
was genuinely, credibly resolved by another record's own `supersedes`
field (`CL-ADPT-010`) — now informational in exactly that case, reusing
`knowledge_intermediate.derive_provenance_label`'s own existing
`"superseded" -> "HISTORICAL"` classification, with an explicit
fail-closed guard against an orphaned or not-credibly-resolved
`superseded` record; (2) an `OSError` reading an existing `test_ref`
file (distinct from `oracle.OracleSchemaError`) previously crashed the
whole validator run uncaught — now a distinct, always-blocking
`self-knowledge-quality-unreadable-test-ref-file` finding. 8 new
regression tests (20 → 28). Real-corpus `--strict` baseline reconciled,
not merely re-run: 35 findings both before and after, 27 → 26 blocking
(only `CL-ADPT-008`'s own contradiction moved; every other finding's
classification unchanged), confirmed deterministic. The 26 remaining
blocking findings are two genuine, pre-existing knowledge-debt
categories — neither a validator defect — filed as `L-114`: (a) nine
`status: verified` Requirements with no evidence citation at all
(`REQ-DOCORIGIN-001/002/003`, `REQ-HSAPI-001`-`006`), not covered by
`decisions/0081` §3's own, narrower oracle-contract-citation exemption,
genuinely new, `retained`; (b) `balance-from-spec`'s own
`unverified_required_scope`/`stale_test_citation` findings, cross-
referenced by `knowledge-curator` into the pre-existing `L-107` rather
than duplicated — `L-107`'s own "moves forward when" condition (ii) is
now confirmed **not triggered** (Phase 85 shipped the detector `L-107`
anticipated but never re-cited the Evidence records). `--strict` is
documented as **not currently suitable** as an unconditional CI gate
against this corpus. A reproducibility addendum (concrete fixture +
command + independently re-verified byte-for-byte output) was appended,
append-only, to the investigation log for `SCI-001`/`SCI-002` — neither
original entry edited, no new canonical record created. `docs-
reconstructor` found and the lead fixed 2 non-blocking stale-by-omission
doc findings (`docs/development/contributing.md`, `docs/workflows/
self-curation-loop.md` both omitted the new "unreadable" finding and the
superseded-contradiction carve-out). `release-phase-auditor`'s first
re-audit pass returned **FAIL** (the retro's own corrective-pass
addendum didn't yet exist; real closeout work sat uncommitted) — both
fixed same-day, re-audited **PASS WITH NON-BLOCKING OBSERVATIONS** across
two further passes (the second specifically covering the `L-115`
promotion commit). `L-115` promoted: an agent with both `Bash` and
`Write` that materializes a prior git revision into the live, tracked
working tree for its own before/after comparison must restore it before
returning its report (`.claude/agents/release-phase-auditor.md` "Hard
rules" + `planning/v1-redefinition/agent-led-development.md` §1) —
discovered when exactly this happened during this corrective pass's own
first audit dispatch, caught by the lead via an unrelated harness notice
rather than the dispatch's own report (the auditor's own transcript
evidence disputes the precise causal attribution; the incident and fix
stand regardless). No change to `src/codecompass/knowledge_api.py`/
`oracle.py`/`knowledge_intermediate.py`, the dogfood records
(`CL-FPSS-009`, `SCI-001`/`SCI-002` originals), or any canonical record
schema. Commits: `95309f1`, `4242bf4`, `ee58b03`, `e8398a2`.

**Phase 84 — Consolidated Knowledge API and Query CLI — is `done`,
corrective pass and final corrective amendment both closed (2026-11-02,
`decisions/0091`/`0092`/`0093`)**.
`src/codecompass/knowledge_api.py` is a new, read-only, typed interface
over `context-graph.db`, `planning/knowledge/`, and `planning/
contracts/` combined: `get`/`search`/`traverse`/`trace_evidence`/
`epistemic_status`/`find_gaps`/`get_context_packet`/`export_snapshot`,
each returning one uniform `result`/`empty`/`gap` response with a
per-item authority tag (`primary_evidence`/`derived_index`/
`stated_intent`/`accepted_obligation`/`scoped_verification`/
`editable_projection`/`presentation_artifact`) and a response-time
consistency envelope — never claiming current verification from
historical evidence alone. Natural-key string identities (`symbol:`/
`vendor:`/`doc:`/`contract:`/`check:`/`result:`) stand in for any table
whose own row id is not stable across a rebuild; connects to
`context-graph.db` read-only, never through `graph.open_graph` (which
can create/migrate it), so no call has any filesystem side effect. Six
new read-only CLI commands (`knowledge get/search/trace/gaps/context/
export`); `query relations` migrated onto this API's own `doc_mentions`
relation — JSON output byte-identical, table output verified by content
(Rich truncates several cells at this table's own render width, so a
full literal comparison isn't meaningful there). `decisions/0084`/
`0085` (architecture) and `0091` (implementation-time resolutions:
`ApiResponse` shape, natural-key string encoding, `ContextPacket`
design) govern the original implementation.

A later, independent post-completion source review found three
correctness defects in the `done` implementation, fixed as a corrective
pass (`decisions/0092`): `ConsistencyEnvelope` previously defaulted to
`status="current"`, and `repo_root` was accepted but never threaded into
the oracle-result/check retrieval paths, so a historical `PASS` could be
reported "current" without ever being live-reconfirmed — now fail-closed
by default, and `--repo-root` (CLI)/`repo_root` (API) genuinely gate
"current" on a live digest reconfirmation actually running;
`trace_evidence()`/`find_gaps()` previously silently dropped a
`supporting_evidence`/`contradicting_evidence` citation that didn't
resolve to a real record — now report an explicit
`dangling_evidence_reference` gap per unresolved citation while still
returning every resolved one; `get_context_packet()` previously bypassed
its own `max_items`/`max_chars` bounds on its non-knowledge-record path —
now one shared bounding function covers both paths. 20 new regression
tests (`tests/test_knowledge_api.py` 47 → 65; two new CLI-level
`--repo-root` forwarding tests in `tests/test_cli.py`). Re-demonstrated
against the real `balance-from-spec` corpus and the real
`~/projects/ledgerkit` checkout: the latest real
`single-section-expense-subtotal` oracle result reports `unconfirmed`
without `--repo-root` and `current` only with a reachable Ledgerkit
checkout, while three contract-superseded historical results report
`stale` regardless; `find_gaps` still correctly surfaces the pre-existing
`stale_test_citation` finding (`EV-BFS-002`/`EV-BFS-003`, `L-107`,
retained, unchanged by this pass) and found zero dangling evidence
references in the real corpus (confirmed clean, not merely unchecked).
Full suite 1121 passed (+ the 2 new CLI tests), 2 pre-existing
environment-gated skips (`cargo`/`npm` not installed); all three strict
validators unaffected (same pre-existing informational findings).
Independently re-audited: `release-phase-auditor` returned **PASS WITH
NON-BLOCKING OBSERVATIONS** (addendum to `planning/retros/
_audit-phase-84.md`); a second `docs-reconstructor` drift pass returned
**NO DRIFT** (`planning/retros/_drift-audit-phase-84-corrective-
pass.md`). Two further candidate learnings promoted:
`L-108` (a corrective pass must write and confirm a failing regression
test against the pre-fix source before writing the fix — three
independent occurrences, `planning/v1-redefinition/agent-led-
development.md` §1 + `.claude/agents/release-phase-auditor.md` item 11)
and `L-109` (Rich `Table` cells truncate at default render width —
`docs/architecture/overview.md` "Known footguns"). `L-107` remains
retained, pending a second real oracle-contract-extension occurrence
before a process-change ADR is warranted — **updated 2026-11-03**: its
own "moves forward when" condition (ii), "Phase 85's self-curation work
acts on this specific finding directly," is now confirmed **not
triggered** — Phase 85 shipped the corpus-wide detector (`scripts/
check_self_knowledge_quality.py`) that *finds* this exact condition
(`EV-BFS-002`/`EV-BFS-003` still citing stale results) but did not
re-cite the Evidence records, so the gap is unchanged; this same single
root cause now also surfaces as 17 of the 26 blocking findings that
validator reports against the real corpus, raising the cost of leaving
it open without yet meeting condition (i) (a second contract-extension
event). See `L-114` below.

A second, independent post-completion source review then found two
further defects, fixed as a final corrective amendment
(`decisions/0093`): `trace_evidence()` checked only a Requirement's own
(always-absent) `supporting_evidence` field, reporting a false
`missing_evidence` gap for every Requirement unconditionally — now
resolves one hop through `depends_on` Claims instead, tagging results
`supporting_indirect`/`contradicting_indirect` with a `via_claim`
provenance detail; a dangling `depends_on` id is a new
`dangling_dependency_reference` gap. `find_gaps()`'s `stale_test_
citation` detection accepted `repo_root` but never forwarded it into
`aggregate_contract()`/`evaluate_result_precedence()` — now threaded
through both, with wording distinguishing a live-reconfirmed finding
from a contract-relative-only one. 15 new regression tests
(`tests/test_knowledge_api.py` 65 → 80). The first fix attempt
introduced an undisclosed regression (a Claim with one declared-but-
dangling citation started reporting two gaps instead of one) — caught
by the independent audit's own first pass (**FAIL**), fixed same-day
(restored to a purely declared-list-based signal, symmetric across
Claims and Requirements), and confirmed by a re-audit of the same
auditor: **PASS WITH NON-BLOCKING OBSERVATIONS**
(`planning/retros/_audit-phase-84.md`'s "FINAL CORRECTIVE AMENDMENT"
sections). Re-demonstrated against the real corpus:
`trace_evidence(REPO_ROOT, "REQ-BFS-001")` now reports `status="result"`
with full per-Claim provenance, where it previously reported a false
gap. Full suite 1138 passed, 2 pre-existing skips; all three strict
validators unchanged. Two further candidate learnings: `L-111`
(a function dispatching on record/input kind needs direct test
coverage of each kind it claims to handle — promoted to
`.claude/agents/release-phase-auditor.md` "What to check" item 12) and
`L-110` (a scoping/override parameter dropped on a sibling call within
one function, now recurring a third time across two phases — extends
`L-105`; proposed `CLAUDE.md` §1 amendment drafted in
`planning/v1-redefinition/proposed-governance-changes.md` §K, **held at
`status: candidate`, not yet applied — requires the user's own explicit
§0 approval before `CLAUDE.md` is touched**).

**Phase 83 — Semantic Change Assurance — is `done`, corrective line of
work fully closed (2026-10-29, `decisions/0090`)**. A fourth, final,
narrowly scoped defect — `classify_symbol()`'s historical test-Evidence
validation checked a result's `contract_id` against the live contract
but never its own `oracle_contract_id` — was found, fixed with one added
field comparison, and covered by one new regression test (47 total in
`tests/test_assess_change_impact.py`), confirmed to genuinely reproduce
the defect before the fix was restored. Full suite 1055 passed, 2
skipped; Phase 82 regression and all three strict validators unaffected
(unchanged finding counts). Independently audited: see `planning/retros/
_audit-phase-83.md`'s final-amendment section. No further Phase 83
corrective passes are open. Earlier in the same corrective line
(2026-10-28, `planning/ROADMAP.md`'s own row): `release-phase-auditor`
returned PASS on re-audit against commit `d076023`
(`planning/retros/_audit-phase-83.md`) — an initial FAIL pass
against the implementation commit `b1a8447` found two real gaps (a
missing fixture-driven test named by `decisions/0087` §2; no
`knowledge-curator` triage of two retro-surfaced learnings), both
genuinely fixed, independently re-verified, before the re-audit's PASS.
`scripts/assess_change_impact.py` now exists, built
entirely on Phase 82's unmodified `oracle.py`/`knowledge_
intermediate.py`: it resolves a changed source range to its enclosing
first-party symbol (gated on the target graph's own `source_files.
content_hash` matching the live file — `stale_index` otherwise),
classifies it `no_recorded_relationship`/`relevant_no_coverage_link`/
`behavioural_risk` purely from existing Evidence/Claim citation chains,
and, with `--run-checks`, freshly re-executes each applicable check and
reports `CONFIRMED_REGRESSION`/`INVALID_ASSESSMENT`/`VERIFIED_SCOPE`/
`VERIFICATION_GAP` from that one fresh result alone. Dogfooded for real:
a deliberately introduced OR-union double-counting mutation passes
Ledgerkit's full, unmodified 935-test suite 100% while a new, independent
check fails, and the tool itself reports `CONFIRMED_REGRESSION`. One
real, independently-demonstrated defect found and fixed along the way in
`scripts/check_contracts.py` (`decisions/0088`). **One outstanding,
separately-gated item**: the real Ledgerkit test has not landed in the
real `~/projects/ledgerkit` checkout — a cross-repository action still
requiring its own explicit authorisation, named explicitly, never
silently treated as done. Full detail: `planning/retros/phase-83-
semantic-change-assurance.md`, `decisions/0086`/`0087`/`0088`.

**Phase 82 — Contract and Evidence Foundation — is `done`**, including
two corrective passes that together fixed seven real assurance defects
found by two separate independent post-completion reviews of the shipped
code. The v2 dependency root (`planning/v2-roadmap.md`) is real: one
evidence-linked behavioural contract for `ledgerkit/reports.py::balance_
from_spec` exists end to end — Requirement → Claims → Evidence citing
real source locations → a versioned, multi-check oracle contract → real
`PASS` results against the current, unmodified `~/projects/ledgerkit`
checkout → a real, demonstrated `FAIL` against a deliberately mutated
scratch copy. `decisions/0078`-`0083` govern this phase's design; none of
Phases 84-92 has begun. **The v2 roadmap itself was realigned 2026-10-23**
(`decisions/0084`/`0085`) and **approved as governing, with Phase 83/84
planned, 2026-10-24** (`decisions/0086`/`0087` then corrected Phase 83's
own plan the same day and again on 2026-10-28, immediately before
implementation) — none of this reopened Phase 82's own design.

- `decisions/0078` — the original v2 repositioning.
- `decisions/0079` — the Cross-Project Semantic Overlay track's
  three-layer model and project-qualified reference envelope (post-v2,
  still not authorised to implement).
- `decisions/0080` — corrects Phase 82's epistemic-state design to a
  derived, read-time view (no new persisted field) and strengthens
  oracle-result identity to bind to the exact tested subject via a
  content digest.
- `decisions/0081` — corrects four remaining structural gaps found by
  direct review: a singular check replaced by an explicit, versioned
  `checks:` collection; PASS/FAIL/GAP/INVALID given a deterministic
  precedence/aggregation rule (`GAP` is strictly an aggregate, never a
  per-result field); vacuous verification structurally prevented, with
  a named, explicit compatibility exemption for twelve pre-existing
  `status: verified` records that predate this mechanism; tested-
  subject/test-input digests scoped to explicit, reviewable file lists.
  **Also explicitly authorised Phase 82 implementation in the same
  session** — the first v2 session where planning correction and
  implementation happened together rather than across separate,
  maintainer-gated sessions.
- `decisions/0082` — a later, separate corrective pass against the
  already-`done` Phase 82's own *shipped code* (not its plan): fixes
  current-vs-historical verification conflation, execution-failure
  misclassification (bare pytest exit code instead of its own structured
  `--junit-xml` report), destructive oracle-result/raw-output overwrite,
  and insufficient oracle-schema type/value enforcement. Does not reopen
  `decisions/0080`/`0081`'s own design.
- `decisions/0083` — a second, further corrective pass against the
  already-corrected code, triggered by a separate independent review:
  an all-skipped pytest execution could classify `PASS` (pytest's own
  junit-xml counts a skip toward its `tests` total); both strict
  validators reported a broken required oracle/knowledge-module import as
  merely informational, letting `--strict` report success while every
  oracle check was silently skipped; `parse_oracle_result` checked
  `outcome`'s enum membership against a `set` before confirming its type,
  so an unhashable malformed value raised an uncaught `TypeError`. Does
  not reopen `decisions/0080`/`0081`/`0082`'s own design.
- `decisions/0084` — realigns the v2 roadmap around Knowledge-Driven
  Software Development: inserts four new phases (Consolidated Knowledge
  API, Self-Curation, Knowledge-Placement Review, Documentation
  Compiler) ahead of the former MCP phase, merges MCP with the former
  reconciliation phase, renumbers the former Phases 86-88 to 89-91.
- `decisions/0085` — a same-day corrective amendment to `decisions/0084`:
  formalises Phase 84's logical knowledge model and narrows its CLI
  scope; formalises Phase 86's enforcement classes and placement policy;
  specifies Phase 87's minimum documentation suite and corrects its
  quality baseline; splits the merged Phase 88 back into an MCP-only
  Phase 88 and a reconciliation-only Phase 89 (independently
  deliverable); renumbers the former Phases 89-91 to 90-92; strengthens
  Phase 90's evaluation methodology. Does not reopen Phase 82/83 or
  `decisions/0084`'s own architecture decision (§1: one logical model,
  unchanged physical storage, no new database).

- `decisions/0086` — Phase 83's first corrective planning amendment
  (2026-10-24): replaces `test_input_paths`-based coverage inference with
  a Claim-mediated three-tier relevance/coverage model; fixes an
  impossible aggregate-`FAIL` expectation; adopts `source_files.
  content_hash` for revision consistency; resolves the new obligation's
  contract/Requirement identity by extending the existing contract in
  place, naming the resulting content-hash-invalidation cost explicitly.
- `decisions/0087` — Phase 83's second corrective planning amendment
  (2026-10-28, same session as implementation): fixes a precedence-
  reachability defect in `0086`'s own design (checking aggregate `GAP`
  before `INVALID` made `INVALID_ASSESSMENT` unreachable — classification
  now reads solely the one fresh result's own effective outcome); fixes
  the Ledgerkit scratch-copy demonstration's sequencing. Authorises
  Phase 83 implementation.
- `decisions/0088` — a real, independently-demonstrated defect found
  *during* Phase 83 implementation (not planning): `check_contracts.
  py::check_result_integrity` no longer blocks `--strict` on a historical
  result superseded by a current, different `PASS` for the same
  `check_id`. `src/codecompass/oracle.py` unmodified.

Phase 84's own plan (`planning/phase-84-consolidated-knowledge-api.md`)
is unaffected by any of the above and remains not authorised to
implement.

**What exists now, concretely**:

- `src/codecompass/oracle.py` (shipped, corrected twice): `OracleContract`/
  `OracleCheck`/`OracleResult` schema parsing (real YAML, `pyyaml`, now
  with strict type/value enforcement — a real boolean required for
  `required`, a supported `schema_version`/`execution_provider` checked
  at parse time, malformed YAML caught as a controlled error, `outcome`'s
  type validated before its enum membership so an unhashable malformed
  value can never raise an uncaught `TypeError`, every optional field
  type-checked), Phase 81B-style content digesting (`compute_tree_digest`,
  reusing `_canonical_digest_of_hashes`'s construction) scoped to each
  contract's own explicit `tested_paths`/`test_input_paths`, one
  `pytest` execution provider (pins the target repo's own interpreter
  and `PYTHONPATH` — confirmed necessary this phase, see `L-101`;
  classifies outcomes from pytest's own structured `--junit-xml` report,
  not a bare exit code — see `L-102`; rejects an all-skipped execution as
  `INVALID`, requiring at least one genuinely executed test before
  `PASS`; a subprocess-launch failure is caught and classified `INVALID`
  rather than propagating uncaught), immutable per-run
  `<check_id>--<run_id>` result/raw-output naming, the
  `evaluate_result_precedence`/`aggregate_contract` PASS/FAIL/GAP/
  INVALID rule, and `accept_baseline` (the one explicit, never-automatic
  baseline-minting action, `CLAUDE.md` §1 L-087).
- `knowledge_intermediate.py::derive_epistemic_profile` (zero new
  persisted fields): INTENDED/OBSERVED/VERIFIED/CONTESTED, each computed
  independently, reusing `derive_provenance_label`'s own id-resolution
  helpers. Now also reports `unconfirmed_scopes` — a required scope
  whose only citation is a historically recorded `PASS` that could not
  be reconfirmed against a live, reachable `repo_root` — distinct from
  both `verified_scopes` (confirmed current) and `known_gap_scopes` (no
  evidence at all).
- `scripts/check_contracts.py` (maintainer script) and
  `check_knowledge_base.py::check_verified_status_cites_passing_oracle_
  result` (check): schema, cross-reference, tamper-evidence, GAP-
  aggregate, and depth-not-scope validators. The `status: verified`
  check applies **only** to a slug with a `planning/contracts/<slug>/`
  directory — a named, explicit compatibility exemption covers every
  pre-existing `status: verified` record (`REQ-DOCORIGIN-001/002/003`,
  `REQ-HSAPI-001`-`006`, `CL-DEPTH-001`, `CL-FPSS-006/007`), confirmed
  untouched. Both scripts now fail closed (a blocking finding, not
  informational) when current verification is claimed but the Ledgerkit
  checkout is unavailable to confirm it — `check_contracts.py --strict`
  via a new `contract-current-verification-unconfirmable` finding,
  `check_knowledge_base.py` via a real `--ledgerkit-root` flag threaded
  into `derive_epistemic_profile` instead of a hardcoded `None`. Both
  also now fail closed when their own required `codecompass.oracle`/
  `knowledge_intermediate` import fails outright — previously
  informational, letting `--strict` report success while every oracle
  check was silently skipped entirely. **Since `decisions/0088` (Phase
  83)**: `check_result_integrity`'s own blocking finding is downgraded to
  informational specifically when a different, current `PASS` already
  exists for the same `check_id` — a superseded historical result, found
  by actually extending a real contract for the first time.
- One real contract family: `planning/knowledge/balance-from-spec/` (2
  REQ, 5 CL — `CL-BFS-003` superseded by `CL-BFS-005`, Phase 83 — 3 EV, 2
  DEC, 1 OBS) + `planning/contracts/balance-from-spec/` (3 required
  checks as of Phase 83; 6 immutably-preserved historical result files
  across the two originally-required checks, now informationally
  superseded by 2 fresh ones under the extended contract's own content
  hash; the new third check has no result on file yet — its real test
  does not exist in the live Ledgerkit checkout).
- `scripts/run_balance_from_spec_oracle.py` (maintainer script, like
  `prepare_cleanroom_branch.py`) — re-runs the real oracle against a
  given Ledgerkit checkout, writing one new, permanent result/raw-output
  file pair per execution, never overwriting a prior run's own evidence.
  `--check-id` (repeatable, Phase 83) runs only the named check(s).
- `scripts/assess_change_impact.py` (Phase 83, maintainer script) —
  evidence-backed change-impact assessment: resolves a changed range to
  its enclosing symbol gated on `source_files.content_hash` matching live
  content; classifies `no_recorded_relationship`/`relevant_no_coverage_
  link`/`behavioural_risk` purely from existing Evidence/Claim citation
  chains; with `--run-checks`, freshly re-executes applicable checks and
  reports `CONFIRMED_REGRESSION`/`INVALID_ASSESSMENT`/`VERIFIED_SCOPE`/
  `VERIFICATION_GAP` from the one fresh result's own effective outcome
  alone, never the aggregate state or a historical result. Not a shipped
  `codecompass` command. 27 tests (`tests/test_assess_change_impact.py`).
- 77 new tests total across the original implementation and both
  corrective passes (`tests/test_oracle.py`, `tests/test_check_contracts.py`,
  plus additions to `tests/test_knowledge_intermediate.py` and
  `tests/test_check_knowledge_base.py`), covering every one of the
  governing prompt's original twelve required verification scenarios,
  the first corrective pass's own four defect-specific negative controls,
  and the final corrective pass's own three (all-skipped execution,
  both strict validators' import fail-closed behaviour, outcome-type-
  before-membership plus optional-field type validation and a
  subprocess-launch failure).

`decisions/0062`'s Priority A-F framework remains superseded as the
primary strategic framework by `decisions/0078`. Phase 81B (clean-room
redocumentation, `done`) and Phase 81 (the intermediate knowledge layer
Phase 82 directly extends, `done`) are reused-foundation background,
unmodified by Phase 82 — full detail in `planning/ROADMAP.md`'s own rows
and each phase's retro.

## What was just completed

**Phase 87 Stage 87D plan amended to close five implementation-
readiness gaps, and independently re-reviewed a second time**,
2026-11-11, direct user request (commits `6e05aee`, `7d226d8`). A fresh
governing task found five real gaps in the first §U draft (already
independently reviewed once, READY WITH NON-BLOCKING OBSERVATIONS):
(A) §U.2's default-value checker had a genuine logical contradiction —
it could only catch a documented-but-wrong default, never one omitted
entirely — fixed with an explicit four-point disclosure policy; an
exhaustive `ast`-based scan of all 37 commands (not a sample) confirmed
exactly five real undocumented defaults (`knowledge trace --relation`/
`--depth`, `knowledge context --max-items`/`--max-chars`, `knowledge
export --project-id`) and two real, already-correct positive controls.
(B) A suspected installed-package execution-boundary defect was
independently reproduced for real: a built wheel installed into an
isolated venv confirms `codecompass docs compile` crashes with an
uncaught `FileNotFoundError` trying to load a `scripts/`-resident
module `pyproject.toml` never ships — confined to exactly one command,
concluded maintainer-only (a documentation-disclosure requirement, not
a packaging fix, not a Phase 87 exit-gate blocker); new §U.2a documents
this in full. (C) §U.2's originally-proposed new validator script would
have duplicated two checks `scripts/check_user_docs.py` already has —
redesigned to extend that existing file in place instead. (D) `L-129`'s
real `codecompass undo` first-run gap, re-verified still live, now
requires an explicit documentation-disclosure requirement in the plan,
not an `undo` fix. (E) §U.3 (cross-document semantic consistency) is
now explicitly deferred beyond Stage 87D, not a voluntary lead choice,
with seven outstanding specifications named for a future, separately
authorised phase. A new §U.8 states Stage 87D's exactly two mandatory
deliverables (deterministic reference assurance; final Phase 87
assurance and closeout). A second independent planning review —
re-deriving everything from scratch, including its own independent
wheel build/reproduction and an independent `ast`-based re-derivation
of the five gaps — returned **READY WITH NON-BLOCKING OBSERVATIONS**
again, with two minor precision corrections applied (a wrong
parameter-instance count; an overstated documentation-citation claim),
neither affecting the plan's substance. **Stage 87D implementation
remains not authorised and has not begun. Phase 87 overall remains
`not done`.** Full detail: plan's own §U.2a/§U.8, §V "Second review
round"; see "Current phase" above and "Next concrete step" below.

**Phase 87 Stage 87C corrective-closeout pass closed, and a new Stage
87D plan drafted and independently reviewed**, 2026-11-10 (commits
`9db863f`, `d52d18e`, `90e844f`, `f434883`, `92e718c`, `9034b98`,
`35d8ebd`, `a860825`, `0cac8bd`). A separately authorised
corrective-review governing task found and fixed five real issues
against the already-`done` Stage 87C: a seeded doc annotation resolved
through the real `knowledge apply` reconciliation workflow; a real
canonical-knowledge governance violation (`CL-ADPT-005` had been edited
in place instead of superseded) fixed by restoring the original record
and writing superseding Claim `CL-ADPT-012`; a wrong documentation-
coverage claim about `CONTRIBUTING.md` corrected; an explicit
limitations assessment added to the matched-baseline comparator; and a
learnings-triage re-confirmation. A first independent audit returned
**FAIL** (missing `CHANGELOG.md` entry); fixed; a fresh re-audit
returned **PASS** (`planning/retros/_audit-phase-87-stage-87c-
corrective-closeout.md`). **Stage 87C's own original `done` status and
its original completion audit's PASS verdict are unchanged — this pass
does not reopen either.** Separately, a new Stage 87D plan
("documentation consistency, deterministic reference generation, and
Phase 87 closeout," plan's own §U) was drafted and independently
reviewed: **READY WITH NON-BLOCKING OBSERVATIONS** (§V, four textual
corrections applied). Against the original Phase 87 requirements, only
one item is genuinely outstanding — a deterministic/drift-checked CLI
and configuration reference (§U.2); everything else is already done,
and cross-document consistency checking (§U.3) is scoped as a
voluntary, separately gateable addition, not a closeout requirement.
**Stage 87D is planned and reviewed only — not authorised for
implementation, not implemented.** Full detail: plan's own §T (the
corrective-closeout pass) and §U/§V (the Stage 87D plan and its
review); see "Current phase" above and "Next concrete step" below.

**Phase 87 Stage 87C implemented and independently audited PASS**,
2026-11-10, direct user request (commits `0ea4001`, `1fba77d`,
`28c3a6c`, `1d9d626`, `3e425c5`). Three further `docs/concepts/` pages
were migrated into schema-governed, knowledge-compiled regions
(`adapter.md`: two regions; `vendor-and-ecosystem.md`: one;
`knowledge-model.md`: two, deliberately narrowed); `context.md`'s
migration was attempted and honestly declined, reverted
byte-identical and left human-authored. A real `CL-ADPT-005` Claim
amendment (new evidence `EV-ADPT-013`) correctly triggered
`claims_changed` in exactly the two regions citing it, both
recompiled, independently reviewed, and republished — the plan's own
mandatory multi-region incremental-maintenance proof. A
matched-baseline documentation-quality comparator ran honestly: the
quality bar was met but no net time/cost advantage was demonstrated
against the predeclared threshold. An independent usability exercise
surfaced one genuine, out-of-scope `codecompass undo` first-run
ordering gap, filed as a learning. A first independent
`release-phase-auditor` pass returned **FAIL** on three missing DoD
artifacts (no `CHANGELOG.md` entry; the retro only 4 of
`TEMPLATE.md`'s 11 sections; no candidate learnings filed or
triaged) — all three closed same-day (changelog entry added; retro
completed to all 11 sections; five candidate learnings, `L-125`-
`L-129`, filed and independently triaged by `knowledge-curator`, all
dispositioned `promote`, `status` left `candidate` pending their
destination artifacts actually landing). A fresh, independent re-audit
returned **PASS**, re-verifying every prior finding plus the full
regression suite (1363 passed, 2 skipped), all strict validators, and
zero protected-file drift. Full detail: `planning/retros/
phase-87-stage-87c-knowledge-compiled-documentation.md`;
`planning/retros/_audit-phase-87-stage-87c.md`. **Stage 87C is done.
Phase 87 overall remains `not done`** — a deterministic
`docs/reference/cli.md` generator and a semantic cross-document
consistency checker remain explicitly deferred (plan's own §S.11),
requiring their own separate authorisation; see "Next concrete step"
below.

**Phase 87 Stage 87C plan amended and independently re-reviewed**,
2026-11-09, direct user request (commit `779ce21`). A fresh governing
task found and required correction of several real factual/scope
inconsistencies in the Stage 87C plan (§S) after its own first
independent review round: Getting Started's section/verification
counts (corrected from a claimed 5-of-6 execution-verified to the real
3-of-5, the other 2 verified by two specifically-named other tests);
the Concepts compilation scope (resolved to 4 pages, not the
inconsistently-stated 5, moving `protocol-and-capability.md` to the
human-authored list); schema/document/region arithmetic (6 total
schemas — 2 existing + 4 new — not "five"); the incremental-change
proof's second affected region (swapped from a page never scheduled
for compilation to a verified, already-shared `CL-ADPT-005` dependency
genuinely cited by both `adapter.md` and `vendor-and-ecosystem.md`,
two pages this plan actually compiles); the comparator (§S.7) gaining
a setup-vs-marginal cost split and a predeclared material-improvement
threshold; a new §S.4a specifying a safe existing-document migration
procedure (no target Concepts page has a grounded-region marker yet,
and `publish_section` appends rather than replaces when none exists —
§S.4a uses only existing machinery, zero new code); and a new §S.9a
cross-checking every original Phase 87 exit-gate requirement
(`decisions/0085` §5-§6, §F) against the amended plan's own
disposition. Independently re-reviewed a second time (§S.12's own
"Second review round," same commit): **READY WITH NON-BLOCKING
OBSERVATIONS**, after finding and the lead correcting two citation-
accuracy defects (a misattributed quote; a mischaracterised
`decisions/0085` §6 citation). The first review round's own verdict is
preserved unchanged as historical record. **This plan authorises
nothing beyond itself: Stage 87C implementation itself remains
separately, explicitly not authorised.** Phase 87 overall remains `not
done`; see "Next concrete step" below.

**Phase 87 Stage 87B hardened a fourth time, independently audited
PASS**, 2026-11-09, direct user request (commits `cd81892`,
`fc197cf`). A fresh code-inspection review of the already-twice-
hardened `docs publish` path found `schema_section_sha256` covered
only a schema section's own dict, never the schema's top-level
`document` (the actual publication target), `audience`, or
`acceptance_criteria` fields — reproduced directly, before any fix was
written, by retargeting a schema's `document` field alone after both
independent reviews had already passed, silently redirecting an
already-reviewed draft to a different, never-reviewed-against
document. Fixed with one new, shared `doc_compiler.compute_schema_
section_identity_sha256` binding the section to those top-level
fields, with the write target also re-resolved from the live schema at
the write boundary; 11 new regression tests (full suite 1352 → 1363
passed, 2 skipped). An independent `release-phase-auditor` dispatch
independently reproduced the exploit against a disposable pre-fix
worktree, confirmed the fix, sampled 5 of the 11 new tests directly,
re-ran the full suite and every strict validator itself, and
specifically re-checked for a recurrence of this session's earlier
self-certification defect — none found: **PASS** (`planning/retros/
_audit-phase-87-stage-87b-second-hardening-pass.md`). Stage 87B is now
hardened against four found-and-fixed publication-integrity defects
total across its history. Stage 87C remains separately planned, not
authorised, and untouched; Phase 87 overall remains `not done`; see
"Next concrete step" below.

**Phase 87 Stage 87C implementation-ready plan, independently
reviewed**, 2026-11-09, direct user request (commit `8b97ed8`). Full
detail: the plan's own new §S, `planning/
phase-87-documentation-schema-knowledge-compiled-documentation.md`. In
short: a new §S plan for Stage 87C (the complete minimum documentation
suite — README, Getting Started, Concepts, Architecture, Reference,
Contributor Guide — plus the matched-baseline quality comparison
required to close Phase 87 overall) covers a real current-state/
coverage assessment against `decisions/0085` §5's minimum suite (finds
Concepts, not Architecture/Reference, is the real knowledge-compilation
gap, and that `decisions/0085`'s own named gap — epistemic distinctions
and the reconciliation loop — is already substantially closed by
existing prose), a document/section ownership matrix, knowledge/
evidence prerequisites, a reused-pipeline architecture (one real
addition: a schema file per Concepts page, no new modules), a concrete
implementation sequence, a real incremental-change proof candidate, a
comparator methodology extending Stage 87B's own design, acceptance
criteria, risks/explicit non-goals, and backlog implications. §S.12
records a fresh, independent planning review: **READY WITH
NON-BLOCKING OBSERVATIONS** (three narrow findings — a deferred fact
already directly confirmable; a rubric line conflating two of
`decisions/0085` §6's distinct required baseline measurements; a
loosely worded Claim-id range nominally including two already-excluded
superseded ids — all corrected in place in the same commit). **This
plan authorises nothing beyond itself: Stage 87C implementation itself
remains separately, explicitly not authorised.** Phase 87 overall
remains `not done`; see "Next concrete step" below for what actually
comes next.

**Phase 87 Stage 87B post-closeout hardening pass, fix round, and
independent audit FAIL→fix→PASS cycle**, 2026-11-09, direct user
request. Full detail: see "Current phase" above;
`planning/retros/phase-87-stage-87b-knowledge-change-
demonstration.md`'s "Addendum 2"; `planning/retros/
_audit-phase-87-stage-87b-hardening.md`;
`planning/retros/_audit-phase-87-stage-87b-hardening-reaudit.md`. In
short: commit `1e3301f` fixed three further `docs publish` integration
defects found by a fresh review of the already-closed, already-PASS-
audited Stage 87B work (reviewed-draft integrity, live schema
freshness, a narrower write-boundary race), with 15 new regression
tests (1337 → 1352 passed, 2 skipped), and filed two learnings
(`L-123`, a real `CL-CTXT-005` amendment candidate handed to the
ordinary knowledge-reconciliation workflow; `L-124`, the residual
write-boundary race, now narrowed twice); commit `9cdbb6f` corrected a
self-certification defect a first independent audit caught (the
changelog claimed an audit had already passed before one had run,
plus an overstated test-reproduction count); commit `dacdd1c` closed
the pass after a fresh, independent re-audit returned **PASS**. Stage
87B's post-closeout hardening is now genuinely closed; Stage 87C
remains separately planned, not authorised, and untouched; Phase 87
overall remains `not done`; see "Next concrete step" below.

**Phase 87 Stage 87B implementation, real knowledge-change
demonstration, and independent audit FAIL→fix→PASS cycle**,
2026-11-07, direct user request. Full detail: see "Current phase"
above; `planning/retros/phase-87-stage-87b-knowledge-change-
demonstration.md`; `planning/retros/_audit-phase-87-stage-87b.md`. In
short: commit `0f6a268` implemented Stage 87B's full scope (a second
schema-governed document, project-wide `docs maintain` discovery, a
cross-document region-id check, the publication-time concurrency
guard, the real sandboxed execution harness); commit `88cfa8d` closed
the plan's own mandatory real knowledge-change demonstration and
comparator (a genuine `CL-CTXT-005` gap compiled and published through
the new concurrency guard's `claims_changed` branch for the first time
against real production knowledge, inside an isolated, discarded
worktree; a hand-edited comparator passed semantic-support review but
failed editorial review for the same register problem Stage 87A's own
writing-contract hardening targets) together with a full independent
audit cycle: a first `release-phase-auditor` pass returned **FAIL** on
a missing required concurrency regression test whose absence concealed
a real write-boundary revalidation gap (an intervening document edit
or cited-knowledge change inside the publish lock's own critical
section was silently clobbered); the gap was fixed (both checks now
re-run a second time, inside the lock, immediately before the write —
narrowed, not fully closed, per the docstring's own honest disclosure)
with three new regression tests (1334 → 1337 passed, 2 skipped); a
second, independent `release-phase-auditor` dispatch — reproducing the
race and the clobber directly rather than trusting the fix's own
account — returned **PASS**. `L-121` promoted; `L-122` filed
`candidate`, landed by this reconciliation as a `planning/ROADMAP.md`
backlog row. **Stage 87B is now `done`.** Stage 87C remains separately
planned, not authorised, and untouched; Phase 87 overall remains `not
done`; see "Next concrete step" below.

**Phase 87 Stage 87B corrective planning amendment**, 2026-11-05,
direct user request ("CodeCompass Orchestrator — Stage 87B Corrective
Planning Amendment," planning-only — Stage 87B implementation remains
unauthorised). A code-level review of the already-READY Stage 87B plan
(§O/§P) found seven further findings, each verified against the real
repository before amending: (A) §O.E's conventional-agent comparator
targeted `## Known gotchas`, text inside a fenced illustration, not a
real section — corrected to target the real `vendor-digest-concept`
region. (B) `docs publish` had no concurrency check against a live
human edit before overwriting a region — confirmed by reading
`publish_section` directly; fixed by a new guard reusing `knowledge_
intermediate._apply_doc_region_edit`'s own existing re-verification
pattern, plus a baseline-advance step after a successful publish. (C)
the execution-harness design had no real vendor-source redirection
mechanism (`source_resolution._git_clone` has no redirection knob of
its own) and included two paid-API-triggering commands a
credential-less sandbox can never complete — fixed with a `git
insteadOf`-based redirect and a narrowed allow-list (the two paid
commands verified by a mocked test instead). (D) section classification
conflated compiled/schema-governed/factually-verified into one axis,
missing that `## After the first run` makes real, checkable
implementation claims — fixed with three independent questions and a
per-section table. (E) `acknowledge_stale_grounded_region` was cited as
if it demonstrated a document update, which it structurally cannot
(confirmed by reading it — it never touches document text) — fixed
with a real, worktree-isolated, evidence-backed knowledge-change
demonstration. (F) no accepted canonical knowledge record supports the
originally-proposed README install/first-step additions (confirmed by
searching the real corpus) — fixed by adding no new compiled sections
and anchoring the mandatory demonstration on the one real section that
already exists. (G) both pre-existing README regions were wrongly
assumed `noop` — confirmed by directly running `detect_
grounded_region_changes`: `intermediate-knowledge-layer` is a real,
pre-existing, unresolved `doc_candidate`, preserved and never
artificially resolved. All seven corrected in place (§O.I, a concise
dated summary, not a new extensive retrospective); independently
re-reviewed by a fresh dispatch with no reliance on prior verdicts:
**READY WITH NON-BLOCKING OBSERVATIONS** (§Q — two further narrow
specification gaps found and fixed in the same pass). No source code,
tests, documentation content, or canonical knowledge changed — planning
only. Stage 87B implementation has not begun and remains unauthorised;
see "Next concrete step" below.

**Phase 87 Stage 87A hardening pass, then Stage 87B planning**,
2026-11-04, direct user request ("CodeCompass Orchestrator — Stage 87A
Hardening, Final Closeout and Stage 87B Planning"). See "Current
phase" above; full detail: `planning/retros/
phase-87-stage-87a-hardening.md`, and the plan's own §N/§O/§P. In
short: three publication-path defects found and corrected (manually
typed review verdicts replaced by a hash-bound persisted review
record; an unconfined publication write target replaced by a single,
reusable, symlink-aware path-confinement policy; the clean-room
broker's prompt rebuilt to source from the evidence packet's own
verified on-disk bytes rather than an in-memory copy), each reproduced
as a failing test against the pre-hardening code first; the first
independent audit of this fix returned FAIL on three process defects
in the fix's own closeout prose (caught and corrected in the same
session, see "Current phase" above), the second returned PASS WITH
NON-BLOCKING OBSERVATIONS. Stage 87B's own implementation-ready plan
was then drafted and independently reviewed to READY (two rounds, one
NOT READY on real factual errors against `docs/getting-started.md`'s
actual content, found and fixed) — committed separately, as required.
Stage 87B implementation itself was not started and remains
unauthorised; see "Next concrete step" below.

**Phase 83 corrective pass**, 2026-10-28 (same day, post-completion
source review, "CodeCompass Orchestrator — Phase 83 Corrective Pass").
Full detail: `decisions/0089`; `planning/retros/phase-83-semantic-
change-assurance.md`'s own "Corrective pass" section (actual commands/
results/evidence). Three correctness defects in `scripts/assess_change_
impact.py`, each verified real by direct source reading and reproduced
with a standalone script against the unfixed code before correcting it:
`classify_symbol()` matched Evidence by symbol name alone (a same-named
symbol in a different file could inherit unrelated Evidence — fixed by
also matching the `source_ref`'s own path, normalised); `resolve_
changed_range()` resolved only the symbol enclosing a range's own start
and never validated `end` against the file's own extent (fixed —
`resolve_intersecting_symbols` resolves every symbol whose own span
intersects the full range; a range only partly covered is reported
`partially_resolved`, naming the gap, never silently discarded);
`classify_symbol()` accepted a referenced historical result via a bare
YAML key check with no schema/identity/scope validation (fixed — now
routes through `oracle.parse_oracle_result` plus explicit `contract_id`/
`check_id`/`scope` checks against the live contract). No change to
`oracle.py`/`graph.py`/`knowledge_intermediate.py`. 18 new tests
(`tests/test_assess_change_impact.py`, 46 total); full suite `1054
passed, 2 skipped`; re-validated end to end against fresh disposable
Ledgerkit scratch copies (identical pinned HEAD/mutation/935-passed
result to the original demonstration) and against real, unmutated
Ledgerkit data for the multi-symbol/EOF fixes. Independent audit of this
corrective pass is in progress. Phase 83 stays `done`; this was not a
reopening.

**Phase 83 — Semantic Change Assurance — implemented**, 2026-10-28,
direct user request ("CodeCompass Orchestrator — Amend and Implement
Phase 83"). Full detail: `planning/retros/phase-83-semantic-change-
assurance.md` (actual commands/results/evidence); `decisions/0087`
(second corrective planning pass, fixing a precedence-reachability
defect in `0086`'s own design and authorising implementation) and
`decisions/0088` (one real defect found and fixed in `scripts/check_
contracts.py` during implementation itself). Summary: `scripts/assess_
change_impact.py` built and dogfooded end to end against real Ledgerkit
— a deliberately introduced OR-union double-counting mutation passes
Ledgerkit's full, unmodified 935-test suite 100% while a new,
independent check fails, and the tool itself reports `CONFIRMED_
REGRESSION` with the co-existing `GAP` aggregate shown explicitly, on a
disposable scratch copy (never the real checkout). `oracle-contract.yaml`
extended with one new required check; the resulting content-hash
invalidation of Phase 82's six historical results resolved by two fresh
re-runs. New knowledge records `REQ-BFS-002`/`DEC-BFS-002`/`CL-BFS-004`
(relevance only, no coverage claim yet); `CL-BFS-003` superseded by
`CL-BFS-005`. 1036 passed, 2 skipped — the full repository suite, green
(the +1 is the fixture-driven tamper test added to close the audit's
own named gap). Two retro-surfaced learnings triaged for real by
`knowledge-curator`: `L-104` (retained — the one real instance is
already fixed with its own tests, no second live instance found) and
`L-105` (promoted — a pre-existing regression test already guards it).
**One outstanding, separately-gated item, named explicitly, not silently
treated as done**: the real Ledgerkit test has not landed in the real
`~/projects/ledgerkit` checkout — a cross-repository action requiring
its own explicit authorisation. `planning/ROADMAP.md`'s Phase 83 row now
reads `done`.

**Phase 83 corrective planning amendment**, 2026-10-24 (same day as the
approval below), direct user request ("CodeCompass Orchestrator — Phase
83 Corrective Planning Amendment," planning-only — Phase 83 implementation
remains unauthorised). Independently re-inspected `src/codecompass/
oracle.py`, `graph.py`, `knowledge_intermediate.py::derive_epistemic_
profile`, `scripts/check_contracts.py`, and the real `planning/knowledge/
balance-from-spec/`/`planning/contracts/balance-from-spec/` record set,
rather than trusting the first pass's own prose, and found five concrete
defects (full grounding: `decisions/0086`):

- `test_input_paths` was being used to infer behavioural coverage; it
  only bounds a check's own test-input content digest. Replaced with a
  three-tier model read directly off each Claim's own `supporting_
  evidence` chain: `no_recorded_relationship` (no Evidence cites the
  touched symbol — explicitly *not* read as "safe"), `relevant_no_
  coverage_link` (a citing Evidence exists but no Claim bridges it to a
  check-resolving test-evidence), `behavioural_risk` (a Claim bridges
  both). `EV-BFS-001` already cites `balance_from_spec` this way — no new
  mechanism, an existing one simply put to use correctly.
- The plan expected a check's aggregate state to show `FAIL`;
  `CheckAggregate.state` (`oracle.py`) only ever takes `PASS`/`GAP`/
  `NOT_REQUIRED` — a required check with an observed `FAIL` and no
  `PASS` aggregates to `GAP` (`decisions/0081` §2, confirmed by direct
  reading). Replaced with an explicit four-way precedence —
  CONFIRMED_REGRESSION (any observed `FAIL`, highest precedence, never
  downgraded) / VERIFIED_SCOPE (aggregate `PASS`) / VERIFICATION_GAP
  (aggregate `GAP`) / INVALID_ASSESSMENT — that always shows a `FAIL`
  and its co-existing `GAP` aggregate state together, never one
  presented as if it erased the other.
- Revision consistency for changed-line coordinates had no concrete
  mechanism. `source_files.content_hash` (already populated,
  `sha256`-of-exact-bytes, identical construction to `oracle.
  sha256_file`) is reused: a touched file's live hash must match the
  graph's own recorded hash before its `source_symbols.line` data is
  trusted for symbol resolution; a mismatch reports `stale_index`
  explicitly rather than guessing.
- The new OR-union obligation's contract/Requirement placement was left
  undecided, and the option the first pass implied (a second contract
  file under the same slug) is not supported by `check_contracts.
  py::_iter_contract_slugs` (exactly one `oracle-contract.yaml` per
  slug). Resolved: extend the existing `oracle-contract.yaml`'s `checks:`
  list in place (same `contract_id: REQ-BFS-001`); a new, separate
  `REQ-BFS-002`/`DEC-BFS-002`/`CL-BFS-004` in the *same* knowledge slug
  states the third obligation without editing `REQ-BFS-001`'s own
  statement (Requirements have no supersession mechanism — confirmed by
  direct reading, `supersedes` is Claim/Decision-only) — schema-valid
  because `derive_epistemic_profile` matches via each record's own
  evidence-citation chain, never by requiring its `id` to equal the
  contract's `contract_id` (confirmed by direct reading).
- **Named for the first time**: extending the contract file changes its
  own content hash, which (via `evaluate_result_precedence` rule 1)
  invalidates all six of Phase 82's existing `PASS` results for the two
  pre-existing checks on next evaluation. Resolved as a required,
  bounded, one-time action in the same commit: re-run both pre-existing
  checks once against current Ledgerkit HEAD, producing fresh results
  under the new hash; the original six result files are never deleted or
  edited (Phase 82's own append-only discipline, unchanged) — a required
  before/after aggregate-state test is now part of the plan's own
  acceptance criteria.

Produced `decisions/0086` and rewrote `planning/phase-83-semantic-
change-assurance.md` in place (§0, §2-§13 materially revised; §1/§8's
substance preserved). No change to `src/codecompass/oracle.py`, `graph.
py`, or `knowledge_intermediate.py` — every correction is resolved by how
Phase 83's own (not-yet-written) tooling is specified to use these
modules' existing, unmodified behaviour; no defect was found in Phase
82's own shipped code. `decisions/0078`-`0085` are not edited.

**v2 roadmap approval and Phase 83/84 planning**, 2026-10-24, direct user
request ("CodeCompass Orchestrator — Approve v2 Roadmap and Plan Phases
83-84," planning-only — explicit stop condition unchanged: neither phase
is authorised to implement). Re-verified, against live repository state
rather than the prior session's own retelling: Phase 82 still `done`,
unreopened; Phase 83 still next, unreopened; the CLI's `query`/
`knowledge`/`enrich` sub-apps unchanged; `context-graph.db`'s real
`rebuild_deterministic` behaviour (which tables are wholesale deleted and
reinserted on every sync vs. incrementally upserted by natural key);
Ledgerkit's HEAD (`7224bb5`) and its own separate `context-graph.db`
(confirmed CodeCompass's own self-referential graph has no real knowledge
of Ledgerkit at all — any Phase 83 tooling must point explicitly at
Ledgerkit's own graph). Approved the corrected roadmap (Phases 82-92,
`decisions/0084`/`0085`) as governing, subject to this confirmation.
Produced two new implementation-ready plan files:

- `planning/phase-83-semantic-change-assurance.md` — grounds the Phase 83
  dogfood scenario in a real, confirmed blind spot found by direct
  reading of Ledgerkit's own test suite: `reports.py::balance_from_spec`'s
  OR-union section-account matching can double-count a posting matching
  more than one of `section.accounts`'s own patterns, and no existing
  Ledgerkit test (including the one test that does construct multiple
  patterns) asserts the resulting arithmetic, only membership. Resolves
  "structural proximity vs. genuine behavioural risk" via symbol-line-
  range localisation against the target checkout's own graph, cross-
  referenced against existing `EV-*.yaml` `source_ref` citations — no new
  graph table, no call-graph.
- `planning/phase-84-consolidated-knowledge-api.md` — resolves the
  governing prompt's three mandatory architectural considerations by
  generalising already-shipped precedent rather than new infrastructure:
  stable identities reuse `decisions/0038`'s natural-key-table pattern
  (already solved once, for `doc_relation_enrichment`, for exactly the
  wholesale-rebuild-volatility problem); snapshot consistency reuses the
  `meta` table's existing revision fields, `_current_cited_hashes`, and
  `derive_epistemic_profile`'s existing three-way currency distinction;
  primary-authority-vs-derived-index is a pure classification tag over
  existing record kinds. One existing command (`query relations`) is
  migrated onto the new API as proof it is not a redundant wrapper; no
  other command is migrated.

Independent review of both plans against the governing prompt's own
§6 checklist found no material defect requiring correction before
closeout; see this session's own closing report for the point-by-point
record. No implementation of either phase was undertaken; no `src/`
change; `decisions/0078`-`0085` are not edited.

**v2 roadmap corrective amendment**, 2026-10-23 (same day as the
realignment below), direct user request ("CodeCompass Orchestrator —
Corrective Amendment to v2 Knowledge-Driven Development Roadmap," also
planning-only — explicit stop condition unchanged). Re-verified Phase
82 `done` and Phase 83 next/unchanged (no defect found in either, so
neither reopened), and re-confirmed by direct inspection that `query`/
`knowledge`/`enrich` remain three independent `typer.Typer()` sub-apps
with no shared interface. Produced `decisions/0085`, which: (1)
formalises Phase 84's logical knowledge model into nine explicit points
(identity, canonical-vs-derived status, authoritative sources,
provenance, epistemic dimensions, contradictions/gaps, read-only/
mutation separation, missing-knowledge handling, versioned export) and
narrows its CLI scope to incremental, optional migration with a
read-only-only API (no mutation path at all); (2) formalises Phase 86
into a Knowledge Placement Policy table (eight categories → this
project's real artifacts) and three named enforcement classes
(mechanical/behavioural/semantic-editorial, the last always advisory);
(3) specifies Phase 87's complete minimum documentation suite (README,
Getting Started, Concepts, Architecture, Reference, Contributor Guide,
mapped onto existing files), a versioned schema, and withdraws the
"materially less correction than Phase 80" comparison in favour of a
reproducible, matched baseline (or a fresh comparison if the historical
one can't be reconstructed); (4) splits the merged Phase 88 back into
an MCP-only Phase 88 and a reconciliation-only Phase 89, confirming
neither depends on the other; (5) renumbers the former Phases 89-91 to
90-92; (6) strengthens Phase 90's evaluation methodology (Arm A now
included in documentation-quality measurement; the concise-instructions
comparator now mandatory for the principal net-efficiency conclusion,
still not a release dependency; cumulative benefit measured across a
task sequence, not one task). Updated, in the same session: `planning/
v2-roadmap.md` (Phase 84/86/87 sections rewritten in place; old merged
Phase 88 replaced with two new sections 88/89; old 89-91 renumbered
90-92; dependency graph/adoption-levels/federation-review/deferred-scope
sections updated); `planning/ROADMAP.md`'s v2 table (rows 84-92);
`planning/v2-evaluation-methodology.md` (a second dated amendment, title
and cross-references renumbered 89→90); `planning/v2-migration-
assessment.md` and `planning/post-v2-cross-project-overlay-backlog.md`
(phase-number cross-references updated for the split/renumbering, no
substantive posture change); `docs/decisions.md` (new `0085` row);
`CHANGELOG.md` (new `[Unreleased]` entry). An explicit independent
review against the governing prompt's own ten-point closeout checklist
is recorded in `decisions/0085`'s own "Independent review" section,
including three honestly-recorded unresolved uncertainties left to each
named phase's own future planning time. No `planning/phase-83-*.md` or
later plan file was written; no `src/codecompass/` or `context-graph.db`
change was made; `decisions/0078`-`0084` are not edited.

**v2 roadmap realignment**, 2026-10-23, direct user request
("CodeCompass Orchestrator — v2 Strategic Roadmap Realignment," a
planning-only task). Reviewed the actual repository state (Phase
77/79-81B/82 implementation status, `decisions/0078`-`0083`, the
existing `query`/`knowledge`/`enrich` CLI surface, `src/codecompass/`
module list) and confirmed, by direct inspection rather than
assumption: no MCP server, no consolidated knowledge-query API, and no
documentation compiler exist anywhere in this codebase; no
`planning/phase-83-*.md` (or later) plan file exists. Produced
`decisions/0084`, which decided the consolidated-knowledge-API
architecture (one new, typed read/traversal library in front of the
existing, unchanged physical stores, no new database), inserted four new
phases, merged the former MCP and reconciliation phases, and renumbered
the former Phases 86-88 to 89-91. Full detail: `decisions/0084` itself.
**Superseded as "what was just completed" by the corrective amendment
above** — every phase-number and scope reference this realignment
introduced is further corrected there.

**Phase 82 final corrective pass** (prior session, 2026-10-22, six
commits `65840ca`/`04c0ed2`/`97ef607`/`4407b38`/`9e828c1`/`33b1e39`):
fixed three further assurance weaknesses (all-skipped pytest execution
misclassified `PASS`; both strict validators failing open on a broken
required import; `parse_oracle_result` checking enum membership before
type, raising an uncaught `TypeError` on malformed `outcome`), each with
real negative controls, independently audited **PASS**. Full detail
preserved in `planning/retros/phase-82-final-corrective-pass.md` and
`decisions/0083` — summarised here only to the extent needed for
session resumption; superseded as "what was just completed" by the
amendments above.

## Known standing gaps (current-state facts, not phase history)

- Cargo adapter (`decisions/0014`) never validated against real `cargo
  metadata` output or a real crate — no Rust toolchain available yet.
- `extract_npm_symbols` untested against real-world `.d.ts` authoring
  styles beyond hand-written fixtures.
- `chat.py` never run against the real Anthropic API in this
  environment.
- `staleness.py`'s version parser has no real PEP 440/semver
  correctness — string comparison only.
- No formal trigger-accuracy evaluation harness for per-vendor Skills.
- Cursor `.mdc` export has no `globs` field.
- A pre-Phase-74 `symbol_enrichment` row's producer remains honestly
  unknown (`NULL`) — new rows are attributed, historical ones cannot be
  retroactively.
- A submodule pin/checkout mismatch has no field distinguishing
  committed-parent-state divergence from purely local uncommitted
  checkout state (`CG-010`, filed Phase 76) — `codecompass query
  topology` gives the two SHAs and a match/mismatch verdict, but
  determining *why* they differ still requires `git status`/`git diff
  --cached` directly.
- A sibling worktree's dirtiness, when unprobed/stale, is honestly
  reported as such but carries no inline CLI signal that this could be
  the case — only `--help` text documents the sync-time-snapshot
  guarantee (`CG-011`, filed Phase 76).
- **Phase 83's new oracle check has no real result against the live
  `~/projects/ledgerkit` checkout** (`overlapping-account-patterns-
  no-double-count`, `REQ-BFS-002`/`CL-BFS-004`) — its `check_reference`
  names a test that does not yet exist there; landing it is a separate,
  explicitly authorised, cross-repository action, not yet given. Running
  `scripts/run_balance_from_spec_oracle.py --check-id overlapping-
  account-patterns-no-double-count` against the real checkout today
  would honestly report `INVALID` ("zero collected tests") — expected,
  not a defect, and not attempted/recorded in this phase.
- `vendor/` and a local `.venv/` exist in this checkout (both
  gitignored, freely regeneratable) — live artifacts, not fixtures.
  **Note from Phase 82**: this project's own `.venv` is where `pytest`
  actually lives — the bare `python3`/`/usr/bin/python` on this machine
  has no `pytest` installed; always invoke tests via `.venv/bin/python
  -m pytest`, not a bare `python`/`pytest` on `$PATH`.
- Several `.claude/agents/*.md` files still reference the now-deleted
  `docs/domain/` and a bare `architecture/overview.md` (now
  `docs/architecture/overview.md`) as if current — filed as `L-098`
  (`planning/learnings/inbox.md`), not yet acted on (editing
  agent-workflow definitions is its own, separate decision).
- One non-blocking residual remains from the first Phase 82 corrective
  pass's own independent audit (the other — an all-skipped pytest run
  classifying `PASS` — was fixed by the final corrective pass,
  `decisions/0083`): `derive_epistemic_profile` reports a required check
  whose cited result's digest mismatches an *existing-but-wrong* decoy
  directory via `known_gap_scopes` rather than the more precise
  `unconfirmed_scopes` (the fail-closed `status: verified` rejection
  still fires correctly either way — a labelling imprecision, not a
  safety gap). A candidate for whoever next touches `oracle.py`'s
  execution-provider logic (Phase 83); not named by either corrective
  pass's own governing prompt, so not reopened or touched by either.
- `L-103` (retained, `planning/learnings/inbox.md`): a Python `in`/
  `not in`-against-a-`set` membership check is only safe once the checked
  value's type is confirmed first (`hash()` runs before the comparison
  and raises on an unhashable value). No second live instance exists in
  the current codebase (confirmed by a repo-wide `knowledge-curator`
  grep) — worth re-checking the next time a new closed-enum/status check
  is added against externally-sourced or YAML-parsed input.
- `L-114` (retained, `planning/learnings/inbox.md`): nine pre-existing
  `status: verified` Requirements (`REQ-DOCORIGIN-001/002/003`,
  `REQ-HSAPI-001`-`006`) have no evidence citation (`depends_on`) at
  all, and are not covered by `decisions/0081` §3's own, narrower
  oracle-contract-citation exemption — `scripts/check_self_knowledge_
  quality.py --strict` fails on this. Resolve via a `context-researcher`
  evidence-finding dispatch against `doc-origin-pinned-reference`/
  `haskell-api-surface-extraction`, or a new, explicitly-named ADR
  exemption mirroring `decisions/0081` §3's own precedent. (The
  companion `balance-from-spec` category this entry originally also
  named is tracked instead at `L-107`, above — not duplicated here.)

## Next concrete step

**Phase 83 is `done`** (see "Current phase"/"What was just completed"
above) — its one remaining *outstanding, separately-gated* item
(landing the real test in `~/projects/ledgerkit`) was never part of its
own `CLAUDE.md` §5 completion gate — it is named, tracked, and requires
its own future, separate explicit authorisation whenever it is taken up.

**Phase 84 (Consolidated Knowledge API and Query CLI) is `done`,
corrective pass and final corrective amendment both closed** (2026-11-02,
`decisions/0091`/`0092`/`0093`) — see "Current phase" above. No further
Phase 84 corrective work is open.

**Phase 85 (Self-Curation and Knowledge-Quality Validation) is `done`,
corrective pass closed** (2026-11-03) — see "Current phase" above for
full detail. No further Phase 85 corrective work is open; the two
genuine knowledge-debt categories the reconciled `--strict` baseline
still carries are tracked as standing gaps (`L-114`, `L-107`, above),
not phase work.

**Phase 86 (Knowledge-Placement and Code-Quality Review) is `done`,
both corrective passes closed** (2026-11-03, 2026-11-04) — see "Current
phase" above for full detail. No further Phase 86 corrective work is
open. Two items await a separate, explicit user decision before they
can close out fully: `L-116`'s recommended promotion to `CLAUDE.md` §1
(draft text: `planning/v1-redefinition/proposed-governance-changes.md`
§L) and `L-117`'s recommended promotion (same file, §M) — both
learnings' own `status` is `retained` pending this, requiring the
user's own `CLAUDE.md` §0 approval; not something this or any future
session may apply on the user's behalf. Two further, same-shape items
from Phase 87 Stage 87A (below) carry the identical pending-approval
disposition: `L-118`'s recommended promotion (same file, §N) and
`L-119`'s (same file, §O) — both also `status: retained`, awaiting the
same `CLAUDE.md` §0 approval. A fifth, same-shape item from Stage 87A's
own hardening pass: `L-120`'s recommended promotion (same file, §P) —
also `status: retained`, awaiting the same `CLAUDE.md` §0 approval.
Sequence from here: **87 (Documentation Schema and Knowledge-Compiled
Documentation) — Stage 87A `done`; Stage 87B `done` (2026-11-07),
including its own post-closeout hardening (twice, 2026-11-09) against
four found-and-fixed publication-integrity defects total; Stage 87C
`done` (2026-11-10), implemented and independently audited **PASS**
(`planning/retros/_audit-phase-87-stage-87c.md`), then a separately
authorised corrective-closeout pass against that already-`done` stage
found and fixed five further real issues (a seeded doc annotation; a
`CL-ADPT-005` canonical-mutation governance violation, fixed by
restoring the original record and superseding it with `CL-ADPT-012`; a
wrong `CONTRIBUTING.md` coverage claim; a comparator limitations
assessment; a learnings-triage re-confirmation), independently audited
**PASS** on re-audit after one FAIL (missing changelog entry) —
**this does not reopen or change Stage 87C's own `done` status or its
original PASS audit's verdict**
(`planning/retros/_audit-phase-87-stage-87c-corrective-closeout.md`) —
`planning/phase-87-documentation-schema-knowledge-compiled-documentation.md`
(plan's own §T). **Phase 87 overall remains `not done`.** A new Stage
87D plan (documentation consistency, deterministic reference
generation, and Phase 87 closeout — plan's own §U) was then drafted and
independently reviewed **READY WITH NON-BLOCKING OBSERVATIONS** (§V's
first review round, four textual corrections applied, none
architectural). A fresh governing task then found five real
implementation-readiness gaps in that first draft (2026-11-11,
commits `6e05aee`/`7d226d8`): a default-value checker that could only
catch a wrong documented default, never an omitted one (fixed with an
explicit four-point policy; five real undocumented defaults confirmed
by an exhaustive `ast` scan); an independently-reproduced
installed-wheel execution-boundary crash in `docs compile`, confined to
one command, concluded maintainer-only and requiring disclosure, not a
packaging fix (new §U.2a); a proposed new validator that would have
duplicated two checks `check_user_docs.py` already has, redesigned to
extend that file instead; `L-129`'s `undo` first-run gap now requiring
explicit disclosure in the plan rather than a fix; and §U.3
(cross-document consistency) now explicitly deferred beyond Stage 87D,
not a voluntary lead choice. A new §U.8 names Stage 87D's exactly two
mandatory deliverables. A second independent planning review,
re-deriving everything from scratch, returned **READY WITH
NON-BLOCKING OBSERVATIONS** again (two further minor precision
corrections, neither architectural). Against the original Phase 87
requirements, only one item is genuinely outstanding — a
deterministic/drift-checked `docs/reference/cli.md`/`configuration.md`
generator (§U.2, now §U.8 Deliverable 1); a semantic cross-document
consistency checker (§U.3) is scoped as a voluntary, separately
gateable addition, not a closeout requirement. **Stage 87D is planned
and reviewed only (twice, now across both review rounds) —
implementation is explicitly not authorised by either pass and has not
begun.** This is a recommendation, not a pre-decision: **the next
concrete step is for the lead/user to decide whether to authorise
Stage 87D implementation** (all of it, §U.8's Deliverable 1 only, or
Deliverable 1 plus the voluntary §U.3) — no session, agent, or
reconciliation pass may self-authorise it; only once that authorisation
is given and implementation completes does Phase 87's own closeout get
reassessed.
A smaller, nearer-term item that does *not* need that authorisation:
Stage 87C's own five candidate learnings (`L-125`-`L-129`,
`planning/learnings/inbox.md`) are all independently triaged
`promote`, but each `status` stays `candidate` until its own drafted
destination artifact actually lands (e.g. `L-125`'s
`docs/architecture/documentation-compilation-pipeline.md` step 6
addition) — landing those is ordinary documentation/knowledge
maintenance, not a new phase decision. A smaller,
independent outstanding item from the
hardening pass: `EV-CTXT-021` (`planning/knowledge/codecompass-domain/`) is a
verified, uncited fact about `sync_vendor`'s clone-failure fallback
that `CL-CTXT-005` does not yet mention — a future
`context-researcher`/reconciliation pass over `codecompass-domain/`
should amend `CL-CTXT-005` to include it (adding `EV-CTXT-021` to its
`supporting_evidence`) or explicitly decline with a documented reason.
Found during Stage 87B's hardening pass, `L-123`; this is a hand-off
for the ordinary knowledge-reconciliation workflow, not something this
reconciliation itself may decide. → 88 (Agent Integration and MCP, split from
the old merged phase) → 89 (Incremental Knowledge and Documentation
Reconciliation, split from the old merged phase, independent of MCP) →
90 (Comparative Development Trials, methodology strengthened) → 91
(External Validation and Adoption) → 92 (v2.0 Hardening and Release).
None of 88-92 is phase-planned yet; each gets its own `CLAUDE.md` §1
plan file when it is actually next.

Other open items requiring a human/lead decision, none currently claimed
by a drafted plan or phase number:

- Whether to fund any Post-v2 Cross-Project Semantic Overlay stage
  (`planning/post-v2-cross-project-overlay-backlog.md`) — explicitly not
  authorised by any amendment to date; Stage 1 cannot begin before Phase
  82 is `done` — it now is, but no further authorisation has been given.
  Unaffected by either the realignment or its corrective amendment
  (`decisions/0084` §5, `decisions/0085` §8).
- Priority A's own narrowly-scoped follow-up trial, sketched (not
  started) in `planning/phase-78-amendment-followup-plan.md` — now
  superseded in strategic priority by Phase 83/85's own, sharper
  change-assurance/self-curation framing (`decisions/0078`,
  `decisions/0084`), but not deleted; still available if a human
  decision prefers it first.
- The "Strict mechanical isolation for documentation-reconstruction
  stages" backlog item — `resolved` (Phase 81B Amendment 4), no further
  action pending. Phase 87's documentation compiler reuses this same
  isolation mechanism rather than reopening it.
- `L-101` (promoted, `planning/learnings/promoted.md`): an oracle
  execution mechanism must pin the interpreter and `PYTHONPATH` of the
  exact tree it executes, or a sibling checkout's own editable package
  install silently shadows a scratch mutation — already landed in
  `oracle.py`, recorded for any future execution-provider work (Phase
  83).
- `L-102` (promoted, `planning/learnings/promoted.md`): classify a
  subprocess oracle's outcome from its own structured report (e.g.
  pytest's `--junit-xml`), never from a bare exit code alone — already
  landed in `oracle.py::_classify_pytest_junit`, recorded for any future
  second execution provider (Phase 83).
- `L-103` (retained, `planning/learnings/inbox.md`): validate a value's
  type before checking its membership against a closed `set` — no
  current second instance to fix, but worth re-checking the next time a
  new closed-enum/status check is added against raw/YAML-parsed input
  (Phase 83's own future execution-provider work, or Phase 84's new
  knowledge-API query parsing, are the most likely triggers).
