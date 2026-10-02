# Governing prompt (verbatim) — strict isolation backlog item

Saved verbatim per this project's own convention (each amendment/
follow-on governing prompt is preserved as-is under `planning/`). This
is a planning-only task: record one actionable backlog item, do not
implement the isolation system now.

---

Add strict isolation for documentation reconstruction to CodeCompass's
roadmap/backlog as a future capability.

Repository: https://github.com/ctosullivan/codecompass
Related template: https://github.com/ctosullivan/codecompass-template —
retain MIT licensing and lightweight adoption.

Assume no knowledge of this conversation. Read repository instructions,
current roadmap/backlog, and Phase 79/80 isolation records. Save this
prompt verbatim under planning/.

The existing process uses curated exports and transcript checks. These
provide best-effort separation; they do not mechanically prevent access
to excluded material. Strict isolation therefore remains UNMET.

Record one actionable item in the existing planning structure, linking
any existing isolation work rather than creating duplicate entries.
Preserve current priorities and Phase 78. This task records future
work; do not implement the isolation system now or make it a new gate
for current documentation work.

The item should cover:

1. Stage-specific enforced boundaries
    * Implementation reconstruction receives runnable primary
      implementation evidence, tests, fixtures and required
      dependencies. It cannot access conceptual knowledge, legacy
      documentation or prior reconstruction narratives.
    * Fresh documentation drafting receives the approved knowledge
      snapshot, implementation reconstruction and comparison findings.
      It cannot access legacy narrative documentation.
    * Legacy reconciliation receives both only after the fresh draft
      has been committed.
2. A genuinely isolated execution mechanism
    Evaluate containers, separate workers or another suitable
    mechanism. Require fresh agent context without inherited
    conversation history, allowlisted inputs, and enforcement against
    access through parent directories, Git history, symlinks, mounts,
    retrieval tools or network routes. A separate directory or
    instruction alone does not qualify.
3. Runnable, reproducible inputs
    Record input manifests, revisions and hashes. Include transitive
    implementation dependencies and fixtures so isolation does not
    prevent verification of the selected workflows. Distinguish
    intended exclusions from missing inputs.
4. Meaningful acceptance checks
    Demonstrate that permitted inputs and selected executable
    workflows work. Attempt access to forbidden files, repository
    history and relevant escape routes; access must be denied
    mechanically. Verify draft-before-reconciliation ordering and
    retain evidence of the achieved boundary.
5. Honest failure handling
    If enforcement cannot be established, report strict isolation as
    UNMET with the reason. Any best-effort fallback must be explicitly
    labelled. Report isolation, workflow completion, documentation
    accuracy and coding-context usefulness separately.

Specify the problem, proposed scope, dependencies, acceptance criteria
and suggested priority. Keep template adoption optional and concise;
defer template changes until a working approach exists.

Update the relevant roadmap/backlog links and planning changelog, commit
the planning changes, and report the item's location and commit
reference.
