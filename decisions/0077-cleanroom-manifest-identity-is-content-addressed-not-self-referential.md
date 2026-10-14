# 0077. The clean-room manifest's identity is a content-addressed
digest, never a self-referential commit field

## Status

Accepted (2026-10-14, direct user instruction — Phase 81B Amendment 5,
corrective). Implemented in `scripts/prepare_cleanroom_branch.py`;
existing `cleanroom/redoc-*`/`cleanroom/result-*` branches are left
exactly as committed under the superseded convention (see
"Consequences" below), not rewritten.

## Context

The original clean-room manifest (`CLEANROOM-MANIFEST.yaml`) tried to
record `handoff_commit`: the SHA of the Git commit that would contain
the manifest itself, once committed to its own `cleanroom/redoc-*`
branch. This is circular by construction — a commit's own tree hash
depends on every file inside it, including the manifest, so the manifest
cannot name its own eventual commit SHA without changing that SHA.

The real workaround in use: build the tree, commit it with
`handoff_commit: null`, read back the resulting SHA, hand-edit the
manifest to record it, and commit *again* purely to persist that edit.
Inspecting a real branch (`cleanroom/redoc-b939d23`) confirmed the
practical consequence: its manifest's `handoff_commit` names
`5c96278...`, one commit behind the branch's real tip `8325272...` — the
manifest's own self-description is permanently one commit stale relative
to wherever the tree actually, finally lives.

Separately, the manifest's own payload integrity was validated only
partially: `intermediary_projection_hashes` covered the rendered
knowledge projection, but no hash existed anywhere for the actual
source/test/config payload, and the one validation step that did exist
(`intermediary_projection_hashes` matching) re-read the *parent
repository* (`ROOT / planning/knowledge/...`), not the staged tree
itself — so a staged/exported clean-room tree could never be validated
on its own, independent of the repository that produced it.

## Decision

**The manifest's identity is now a non-circular, content-addressed
claim, computable entirely before any commit exists:**

- `manifest_schema_version` (currently `2`).
- `documented_revision` — the exact source commit, unchanged in meaning
  from before, now actually enforced (see the companion exact-revision-
  export fix in the same amendment).
- `payload_file_hashes` — a `{relpath: sha256}` mapping covering every
  writer-visible payload file (allow-listed source/test/config content
  plus the two generated root instruction files), excluding only the
  manifest file itself.
- `payload_tree_sha256` — a single canonical SHA-256 digest computed
  over `payload_file_hashes`' own sorted `"hash  path"` lines. The
  manifest file is the sole, explicit, deliberate exception to this
  digest's own input set: a file cannot bind its own identity without
  changing it, so it is excluded rather than approximated.

**The `handoff_commit` field is retired, not renamed.** The actual
branch/commit that holds a given payload is recorded externally — this
plan file's own log and this project's retro — where naming a commit
after the fact isn't circular, because the file doing the naming isn't
itself part of what's being named.

**`cmd_validate` becomes fully self-contained.** It checks a staged tree
purely against its own manifest: every `payload_file_hashes` entry
present with a matching fresh hash (catches changed/removed/renamed
content), no unlisted file present (catches an addition), and the
manifest's own `payload_tree_sha256` internally consistent with its own
`payload_file_hashes` (catches manifest tampering) — no step reads
anything outside the staged tree. The old `intermediary_projection_hashes`
freshness check against the live parent repository is kept as a
build-time-only informational marker (is the knowledge layer stale
relative to this handoff), explicitly dropped from `validate`'s own
scope.

## Alternatives considered

- **Keep `handoff_commit`, just document it as "the previous commit,
  not this one."** Rejected — a field whose name says one thing and
  whose value means something else by convention is exactly the kind of
  misleading self-reference this decision exists to remove, not
  preserve under a caveat.
- **Rename to `payload_commit` and keep the two-commit workflow.**
  Considered (named explicitly as an option in the governing prompt).
  Rejected because the underlying circularity — and the two-commit
  dance it requires — doesn't go away merely by renaming the field; the
  content-addressed digest is computable in one pass, before any commit,
  and is strictly more useful (it binds content, not just a pointer to
  wherever that content currently lives).
- **Rewrite existing `cleanroom/redoc-*` branches to the new schema.**
  Rejected per the governing prompt's own explicit instruction and this
  project's general practice: historical artifacts are not rewritten to
  look different after the fact. The old convention is documented as
  superseded for *future* exports only.

## Consequences

- Every `prepare_cleanroom_branch.py build` invocation from this point
  forward produces a manifest schema v2 tree; `cmd_validate` only
  understands this schema (an old-schema manifest with no
  `payload_file_hashes` fails closed with an explicit message, rather
  than silently reporting a false pass).
- A clean-room branch's own checkout can now be validated in complete
  isolation — copied anywhere, with no access to `ctosullivan/
  codecompass` at all — which is a precondition this plan's own
  "reusing this for another project" guidance already assumed but this
  implementation did not, until now, actually satisfy.
- Existing branches built under the old schema (`handoff_commit`,
  `intermediary_projection_hashes`-only validation) remain exactly as
  committed; they are not retroactively re-validated against the new
  scheme and their own historical `PASS` results stand as whatever they
  verified at the time, against the rules that existed then.
