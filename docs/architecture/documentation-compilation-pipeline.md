# Documentation-compilation pipeline (Phase 87)

Current state: **Stages 87A and 87B, both hardened and independently
demonstrated end-to-end against the real repository.** Stage 87A
established the compile/review/publish lifecycle for one
schema-governed document (`README.md`), then was hardened against
three integration defects a follow-up review found in the publication
path itself (binding publication to persisted, hash-verified review
evidence rather than a manually typed verdict string; confining the
write target to an approved documentation path; sourcing the
clean-room broker's prompt from the evidence packet's own verified
on-disk bytes). Stage 87B extended this to a second schema-governed
document (`docs/getting-started.md`), project-wide `docs maintain`
discovery across every schema in the project, a cross-document
grounded-region-ID uniqueness check, a narrow sandboxed execution
harness that can actually run a small, explicitly allow-listed set of
tested documentation examples (`scripts/execute_doc_example.py` —
never a general command runner), and a publication-time concurrency
guard that revalidates live region state and a cooperating-writer file
lock immediately before every write, so a human edit or a concurrent
publish is never silently overwritten. Stage 87C (the complete minimum
publication suite, deterministic CLI-reference generation, the
matched-baseline quality comparison) remains planned but not
implemented, and not authorised by this stage — see
`planning/phase-87-documentation-schema-knowledge-compiled-documentation.md`
for the full design and three-stage boundary. This page describes what
exists today, not the full eventual design.

## Why this exists

Professional project documentation becomes an explicit, repeatable
*output* of the canonical knowledge system, via a user-defined,
versioned schema, rather than a one-off clean-room exercise repeated by
hand each time a doc goes stale. **No second source of project truth**:
the compiler reads Phase 84's `knowledge_api` only — it never caches,
duplicates, or independently asserts a canonical fact.

## Components

| Component | Role |
|---|---|
| `*.schema.yaml` | A versioned, user-authored schema (one per governed document) naming each section's required knowledge, audience, tone, depth, and evidence bar. Minimal by design — a project maintainer edits it directly. |
| `scripts/check_doc_schema.py` | Validates a schema: required fields, a known `schema_version`, every `required_knowledge` entry resolved to a real record (a `discover:<query>` entry resolved to exactly one match, never a guessed first result), section ids restricted to `[a-z0-9-]+` (the real grounded-region parser silently truncates at a `.`). |
| `src/codecompass/doc_compiler.py` | Deterministic resolution/hydration/gap-detection/citation-scope-checking, plus `publish_section`/`maintain_document`/`compute_schema_slug`/`decide_publish_safety` (Stage 87B's publication-safety decision logic — see step 8 below). See `docs/architecture/components.md`'s own entry for this module. |
| `scripts/compile_doc_section.py` | The clean-room section-compilation adapter — see "Clean-room composition" below. |
| `scripts/execute_doc_example.py` | Stage 87B's execution harness — runs a small, explicitly allow-listed set of real documentation examples inside a real `unshare`/`pivot_root` namespace sandbox, with offline-mirrored git/pip caches so no live network is reachable from inside the sandbox. Never a general command runner: a command not in its own hand-maintained allow-list is rejected before the sandbox is even entered. |
| `codecompass docs schema-init\|compile\|record-review\|publish\|maintain` | The CLI surface. See `docs/reference/cli.md`. |

## Pipeline (per section)

1. **Resolve** `required_knowledge` to concrete record ids
   (`doc_compiler.resolve_section_ids`) — a `discover:` query was
   already resolved once, at schema-validation time, never guessed at
   compile time.
2. **Check currency** (`check_record_currency`) — reuses
   `knowledge_api.get()`'s own `ConsistencyEnvelope` directly; no
   independent currency computation.
3. **Find gaps** (`find_section_gaps`) — a record below the section's
   own `min_claim_status`, or stale/unconfirmed evidence, blocks that
   section's generation entirely; never filled with plausible filler.
4. **Hydrate** (`resolve_section_packet`) — full record content via
   `knowledge_api.get()`'s `details["fields"]`, never
   `search()`/`get_context_packet()`'s own 280-character `summary`.
   Budgeted against the real serialized content; a required record
   exceeding the budget is a blocking error, never a silent truncation.
5. **Compose** (`compile_doc_section.compose_section`) — see below.
6. **Validate citations** (`validate_section_citations`) — the
   deterministic *scope* half of claim verification: every
   `{{cite:RECORD-ID}}` tag must name a record inside *this section's
   own* resolved packet, not merely a record that exists somewhere in
   the project. The AI-assisted *depth* half (does the cited record's
   content actually support the sentence's specific wording) and the
   *completeness* question (any factual claim with no tag at all) are
   answered by a separate, independently-dispatched review — never the
   generating model grading itself, and never performed inside this
   module (`CLAUDE.md` §8).
7. **Editorial review** — a second, independent dispatch, structurally
   separate from claim verification: usefulness, clarity, audience fit.
   A section can pass claim verification and fail this, or vice versa.
   **Record each review** (`docs record-review --kind semantic|
   editorial`) — persists the verdict, findings, and evidence
   references, bound by hash to this exact draft/evidence/schema
   identity. A manually typed verdict string is no longer accepted at
   publish time (hardening pass; see below).
8. **Publish** (`publish_section`, via `docs publish`) — only once both
   persisted review records exist, are well-formed, verdict-passing,
   and still match the section's *current* draft/evidence/schema hash
   (a recompile or a knowledge change since review invalidates a stale
   record). The write target is resolved and confined by
   `resolve_publication_target` (`README.md`, or a `docs/**/*.md` file,
   confirmed to stay inside the project root even through a symlink).
   **Stage 87B publication-time concurrency guard**: the whole command
   runs inside a cooperating-writer file lock (`_doc_publish_lock`,
   `cli.py`), and checks both the live region's grounded-region state
   (`doc_compiler.decide_publish_safety`) and the cited knowledge/
   schema-section's own freshness **twice** — once before the lock is
   acquired, and again, inside the lock, immediately before the write
   itself, since both the first check and the write are plain,
   synchronous Python with a real (if small) gap between them that a
   concurrent, non-cooperating editor's own disk write or a knowledge
   change can land in. The region-state check refuses the write
   outright if the live region shows a real human edit
   (`doc_candidate`) or a live-and-knowledge both changed
   (`concurrent_conflict`) — a `claims_changed`/`noop` region, or a
   brand-new region whose live content hash already matches the new
   body (an idempotent republish), may proceed. The persisted baseline
   advances only *after* the write itself succeeds — never on
   detection, a failed validation, or a rejected publish. This
   protects cooperating `docs publish`/`docs maintain` invocations
   against each other; a human editing the file directly is never
   locked out by the file lock, but the write-boundary revalidation
   still catches that case and refuses the write regardless. The
   residual window between that final, write-boundary check and the
   write itself is narrower, not zero — closing it completely would
   need a full transactional write, deliberately not built here;
   disclosed in `_doc_publish_lock`'s own docstring rather than
   assumed away. Writes/replaces exactly one
   `codecompass-grounded-by region:<id>` region. Machine-readable
   grounding is unconditional — it is unaffected by the schema's own
   reader-visible `citation_display` setting. The citation-tagged
   draft and both review records are then preserved permanently under
   `planning/retros/phase-87-published-evidence/` for later audits.
9. **Maintain** (`maintain_document`, via `docs maintain`) — branches
   on the real five `GroundedRegionFinding` states (`new`/`noop`/
   `doc_candidate`/`claims_changed`/`concurrent_conflict`) using the
   three already-implemented resolution functions
   `knowledge_intermediate.py` provides for exactly this problem — no
   new diffing model. A human edit with no knowledge change
   (`doc_candidate`) is never auto-regenerated; both changing at once
   (`concurrent_conflict`) is reported for the lead's own resolution,
   never auto-merged. **Stage 87B**: called with no schema-path
   arguments, it discovers every `**/*.schema.yaml` under the project
   root itself and reconciles every document any of them governs in
   one call, across as many schema-governed documents as exist (no
   longer limited to one document per invocation); explicit arguments
   still scope it to just those schemas. Writing a fresh
   `doc_region_edit` reconciliation item
   (`write_doc_candidates_to_manifests`) is idempotent against an
   already-pending, unresolved item for the same region at the same
   content hash, so repeated `maintain` runs against an unresolved
   `doc_candidate` never pile up duplicate manifests. A schema-
   validation-time check (`scripts/check_doc_schema.py`,
   `doc-schema-duplicate-region-id`) additionally rejects a composed
   region id (`<schema-slug>-<section-id>`) that collides across two
   different schema files, or within one — this is checked before
   `maintain` or `compile` ever runs against the colliding schemas.

## Clean-room composition — a corrected, narrower isolation posture

`scripts/compile_doc_section.py` does **not** reuse
`prepare_cleanroom_branch.py`'s export mechanism: that script exports
files from a pinned *git revision* (`git cat-file -p
<revision>:<path>`), never from working-tree disk, so it has no path
to a freshly generated, uncommitted evidence packet. Instead:

- The hydrated packet and a manifest (schema section, pinned source
  revision, content `sha256`) are written to a fresh
  `tempfile.mkdtemp()` staging directory — never git-tracked, never
  committed.
- The packet's content hash is re-verified against its own manifest
  immediately before use — a mismatch (altered between writing and
  use) is rejected, fail-closed.
- **The broker's system prompt is built from the packet read back from
  those same verified on-disk bytes, not from the in-memory object
  still held by the caller** (hardening pass correction): verifying a
  file's hash proves nothing about what the broker actually receives
  unless the receiving step is sourced from that same verified file,
  not from a second, independently-held copy that could silently
  diverge from it.
- The staging directory is always removed before `compose_section`
  returns, on both the success and every failure path — never left
  behind for a caller to clean up, and never committed either way.
- `verify_cleanroom_isolation.py`'s real sandbox preflight still runs
  as a subprocess before every compile run and fails closed on a
  non-zero exit.
- `cleanroom_broker.run_inference` is invoked **directly**, not from
  inside a new namespace sandbox — its own existing sanitised-env,
  neutral-cwd, no-tool subprocess call is the real isolation boundary
  for this bounded, self-contained prompt. No new sandbox is
  constructed because this adapter's evidence is never a broad,
  git-tracked export with a classification gate to protect against in
  the first place; no new broker is created either. See
  `docs/development/clean-room-redocumentation.md`'s own note on this
  second, narrower caller.
- The returned text is never trusted at face value: an embedded
  file-path marker (an attempt to declare a different output than the
  one requested) is rejected outright.

## Real demonstration

One section (`README.md`'s "Understanding Digests," grounded in
`CL-CTXT-005`) was compiled and published end to end against the real
repository — no mocking, no synthetic fixture. Two of three real
iterations were correctly rejected by independent review before the
third passed; see
`planning/retros/phase-87-stage-87a-knowledge-compilation.md` for the
full account. This section's own pending-review record
(`planning/retros/phase-87-pending-review/readme-md/
vendor-digest-concept.json`) predates the hardening pass below and was
never retroactively rewritten into the new, hash-bound format — it
remains as the real demonstration's own historical evidence, not a
record a future `docs publish` call will ever read again (the section
is already published).

## Hardening pass (post-demonstration)

A follow-up review found three integration defects in the publication
path itself, none of which affected the real demonstration's own
generated content:

1. **Publication was bound to manually typed verdict strings, not to
   any actual review record.** `docs publish` accepted
   `--semantic-verdict supported --editorial-verdict pass` as plain
   CLI arguments — proving only that someone typed those words, not
   that an independent review had run, or that its findings related to
   the exact draft being published. Corrected: `docs record-review`
   now persists each review (verdict, findings, evidence references,
   self-reported reviewer identity) bound by a `draft_sha256`/
   `evidence_sha256`/`schema_section_sha256` identity triple to the
   pending draft; `docs publish` validates both persisted records
   against the section's *current* identity rather than accepting a
   label at face value, and preserves the tagged draft plus both
   records permanently for audit.
2. **The write target was never confined.** `docs_publish` resolved
   `project_root / schema["document"]` with no validation at all — an
   absolute path, a `..` traversal, or a symlinked intermediate
   directory in `document` would have been followed as given.
   Corrected: `doc_compiler.resolve_publication_target` restricts every
   compiler-owned write to `README.md` or a `docs/**/*.md` file,
   resolves symlinks before comparing against the project root (never
   a string-prefix check), and is enforced at both schema-validation
   time (`check_doc_schema.py`) and publish time.
3. **The broker's input wasn't provably the verified bytes.** See
   "Clean-room composition" above — `compose_section` now builds its
   prompt from the packet read back from its own verified on-disk
   file, and always removes its staging directory, success or failure.

All three were reproduced by a failing regression test before the fix
and confirmed passing after; see `tests/test_cli.py` (publish/
record-review hardening tests) and `tests/test_compile_doc_section.py`
(verified-bytes and staging-cleanup tests).
