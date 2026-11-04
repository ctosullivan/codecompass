# Documentation-compilation pipeline (Phase 87)

Current state: **Stage 87A only, hardened** — one bounded documentation
section at a time, demonstrated end-to-end against the real
repository, then hardened against three integration defects a
follow-up review found in the publication path itself (binding
publication to persisted, hash-verified review evidence rather than a
manually typed verdict string; confining the write target to an
approved documentation path; sourcing the clean-room broker's prompt
from the evidence packet's own verified on-disk bytes). Stage 87B
(schema-governed `README.md`/`docs/getting-started.md`, a narrow
execution harness for tested examples, real multi-section manual
maintenance) and Stage 87C (the complete minimum publication suite,
deterministic CLI-reference generation, the matched-baseline quality
comparison) are planned but not implemented — see
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
| `src/codecompass/doc_compiler.py` | Deterministic resolution/hydration/gap-detection/citation-scope-checking, plus `publish_section`/`maintain_document`. See `docs/architecture/components.md`'s own entry for this module. |
| `scripts/compile_doc_section.py` | The clean-room section-compilation adapter — see "Clean-room composition" below. |
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
   Writes/replaces exactly one `codecompass-grounded-by region:<id>`
   region. Machine-readable grounding is unconditional — it is
   unaffected by the schema's own reader-visible `citation_display`
   setting. The citation-tagged draft and both review records are then
   preserved permanently under `planning/retros/
   phase-87-published-evidence/` for later audits.
9. **Maintain** (`maintain_document`) — branches on the real five
   `GroundedRegionFinding` states (`new`/`noop`/`doc_candidate`/
   `claims_changed`/`concurrent_conflict`) using the three
   already-implemented resolution functions
   `knowledge_intermediate.py` provides for exactly this problem — no
   new diffing model. A human edit with no knowledge change
   (`doc_candidate`) is never auto-regenerated; both changing at once
   (`concurrent_conflict`) is reported for the lead's own resolution,
   never auto-merged.

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
