# Governing prompt (verbatim) — Phase 78 corrective amendment of the exit decision

Saved verbatim per this project's own convention. Direct user request,
2026-10-02, following Phase 78's own terminal commit `3b751c8`.

---

You are the CodeCompass orchestrator. Assume no knowledge of prior
conversations. Work from current main at or after Phase 78 terminal
commit 3b751c8, including the Phase 78 plan, trial reports, research
traces, completion audits, CG-001, ADR 0069, ROADMAP and CONTEXT.

Perform a corrective amendment of Phase 78's exit decision only.
Preserve the completed trial and its evidence; do not rerun or rewrite
it merely to obtain a preferred result. Do not implement CodeCompass or
Ledgerkit product code.

A post-completion review found that Phase 78 was executed without
incorporating the final planning correction. Its CG-001: not-recurred
rule still relies on treatment tracing the relationship at a cost "no
worse than baseline." This is logically insufficient: both arms could
incur the same material manual-reconstruction cost precisely because
CodeCompass lacks the relationship capability.

Correct the evaluation as follows:

1. Separate the two questions completely:
    - CG-001 outcome: Did the treatment agent incur material, avoidable
      manual effort because current CodeCompass could not supply the
      required first-party relationship?
    - Context advantage: How did treatment perform relative to
      baseline? Baseline parity may determine LOW/MODERATE/HIGH
      advantage, but must not determine whether CG-001 recurred.
2. Commission a fresh independent re-evaluation of the existing Phase 78
   evidence. Judge absolute materiality from the treatment trace: files
   and ranges read, searches performed, failed queries, reconstruction
   steps, uncertainty resolved and which work a plausible relationship
   capability could actually have avoided. Do not request private
   reasoning.
3. Reassess applicability carefully. Distinguish: existing source
   relationships that a current graph could have exposed; and proposed
   future relationships — new parser producer, Journal storage and CLI
   consumer — that do not yet exist and therefore could not be
   discovered by source-relationship indexing. Decide whether the trial
   adequately tested CG-001, tested it only partially, or was
   inconclusive for the capability hypothesis.
4. Apply this corrected decision tree:
    - The task did not adequately exercise discoverable existing
      relationships → inconclusive/task-not-applicable; Priority A
      cannot close from this trial.
    - It exercised them, but their discovery was not materially costly
      despite the missing capability → not-recurred.
    - It exercised them and their absence caused material, avoidable
      manual reconstruction → recurred. Keep this classification
      separate from the independently retained LOW/MODERATE/HIGH
      context-advantage rating.
5. Reconcile the inconsistent CG-001 evidence rules. The Phase 78 plan
   says a genuinely separate producer/consumer occurrence can satisfy
   the recurrence bar, while the closeout triage says a different
   concrete edge cannot change CG-001 from candidate. Establish one
   symmetric rule that applies to both positive and negative evidence.
   Do not allow differently shaped evidence to close the broader
   hypothesis while declaring it incapable of supporting recurrence.
6. Correct the strategic language. The accumulated LOW/MODERATE/LOW/LOW
   results may justify stopping or pausing further investment, but do
   not by themselves prove that task-context completeness has been
   achieved. If closure remains justified, frame it accurately as
   further Priority A capability investment not currently justified by
   demonstrated marginal benefit, with explicit reopening triggers.
7. Follow the repository's append-only decision rules: do not silently
   rewrite accepted ADR 0069; supersede or qualify it with a new
   numbered ADR if its conclusion changes; append a corrective Phase 78
   review record; reconcile CG-001, the Phase 78 plan/retro/audit
   record, ROADMAP, CONTEXT, CHANGELOG and reference-project
   registration without altering historical trial evidence.
8. Possible outcomes:
    - Not-recurred confirmed under the corrected rule: retain strategic
      closure with corrected rationale.
    - Recurred: reopen the Priority A exit decision and plan only the
      smallest evidence-supported relationship capability plus its
      validation; do not implement it yet.
    - Inconclusive/partially applicable: reopen the exit decision and
      plan one narrowly scoped follow-up using a genuine existing
      cross-module change whose relevant source relationships already
      exist. Do not repeat the full Phase 78 trial or invent an
      artificial benchmark.

Run the normal documentation, knowledge-base and consistency checks,
then commission an independent audit of the corrective decision. Stop
after committing the corrected documentary/planning state. Report the
commit SHA, the independently determined classification, whether ADR
0069 remains operative or is superseded, and any narrowly scoped
follow-up requiring review.
