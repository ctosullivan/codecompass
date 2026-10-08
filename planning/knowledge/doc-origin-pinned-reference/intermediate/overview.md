# doc-origin-pinned-reference — overview

<!-- codecompass-knowledge: CL-DOCORIGIN-001 semantic-sha256:554afa8a2ea80bf9538a5d5c6d1e1f0e34b5931a03696a2ffb73730e9484a2e3 projection-sha256:8dc1a0c9b1cc63cf6667eefed805b3cd4abd89d84555dbdb514636957a0d8bd5 -->
### CL-DOCORIGIN-001

The smallest correct schema-level fix for CG-005 is one new closed doc_artifacts.origin CHECK-enum value, added through the existing generic _migrate_doc_artifacts_constraints mechanism (one more _SCHEMA_VERSION bump, following the exact Phase 17/21/27 precedent), with no change required to any other origin consumer in src/codecompass/ — every other write site is an unconditional per-caller constant unaffected by adding a new option elsewhere, every origin-reading branch (build_doc_relations_edges' skill preference, cli.py's third_party filter/display/undo filter) is scoped to Skill-kind rows or an explicit unrelated value list, and both kind='spec_doc' coverage-gap queries filter on kind only. The open part of the fix is not the schema change itself but *how* scan_spec_docs decides when to assign the new value (see CL-DOCORIGIN-002).

Supporting evidence: [EV-DOCORIGIN-001, EV-DOCORIGIN-003, EV-DOCORIGIN-004, EV-DOCORIGIN-005]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-DOCORIGIN-002 semantic-sha256:b3a18bc639471d4c859a269d6c7ddbccc9045988b0fe34cbba5ba5db558ac297 projection-sha256:536318036aa2a66f1ae5812678df06de45d4f0565bc8099204c09e710548b4bf -->
### CL-DOCORIGIN-002

A real, mechanically-checkable, content-level signal for "this spec_doc-glob-matched file is externally-pinned, tool-ingested reference material" already exists in the one implemented ingestion pipeline today (a uniform YAML frontmatter block carrying reference/source_url/resolved_commit/content_hash/etc.), but scan_spec_docs reads none of it — it only ever reads a file's first H1 or filename stem, treating any frontmatter present as unmatched prose. No path-based or configuration-based signal is available at scan_spec_docs's call site today: the directory this material lands in when synced (dev-docs/hledger-reference/) is an ordinary, arbitrarily-named subdirectory reached only via the pre-existing generic dev-docs/**/*.md glob, indistinguishable in shape from any project's own hand-authored dev-docs content, and there is no vendor.toml or other config entry marking it as external. Any fix that wants scan_spec_docs itself to assign the new origin value automatically would need to add frontmatter parsing (a real, new capability this module does not have today) — it cannot be done by refining the existing glob/title logic alone.

Supporting evidence: [EV-DOCORIGIN-002, EV-DOCORIGIN-006, EV-DOCORIGIN-007]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-DOCORIGIN-003 semantic-sha256:f7576656cea5af3894bfdcb1f541046eba070ccabb5fd3ca65c9a762ab42d915 projection-sha256:49b095aa41caa07d9ee9edb8102a0da565aefc4446d4a276e9c4bbe5132ae87c -->
### CL-DOCORIGIN-003

CG-005's own rejection of reusing 'vendor_upstream' for this material (on grounds that it is designed for a vendor's own embedded upstream docs and this material has no tracked vendors row) is not merely a correct semantic argument but understates the actual failure mode: reusing 'vendor_upstream' with a vendor_name that has no corresponding vendor.toml entry would raise an uncaught KeyError inside _insert_doc_artifacts at sync time (a hard crash), and omitting vendor_name entirely while still using origin='vendor_upstream' would silently violate that value's only real-world invariant observed in this codebase (every current vendor_upstream row has a non-null, resolvable vendor_name) without CodeCompass itself ever checking or enforcing that invariant at the schema level.

Supporting evidence: [EV-DOCORIGIN-003]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-DOCORIGIN-004 semantic-sha256:b98cb12449a0e4ce5337edb859c434216671107d9aca0414efe58fecaf49f5e4 projection-sha256:08aefca5c3af154ca3b40f1c007f21458986c16fe4b23407b46e6b2093ee4ed1 -->
### CL-DOCORIGIN-004

CG-005's own example name for the new value ("e.g. pinned_reference") is not contradicted by any evidence gathered in this research, but the broader idea that the name must also anticipate a non-Git, URL-sourced-only pinned reference (i.e. something not commit-pinned) is not supported by anything currently implemented: the only real ingestion pipeline that exists is entirely Git-commit-pinned (every frontmatter field observed is Git-shaped: resolved_commit, fetch_method: local_clone, requested_ref as a Git tag), and the pipeline's own references.toml `source` field, while typed as an unvalidated free string, has zero working code path for any value other than "git" — no "url" fetch method is implemented anywhere. Whether the new origin value's name/semantics should be scoped narrowly to "Git-commit-pinned" or written more generally to anticipate a future non-Git source is a naming/scope judgment call this research does not resolve.

Supporting evidence: [EV-DOCORIGIN-009]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: DEC-DOCORIGIN-001 semantic-sha256:60b9e919a3afc7425e774c387c493949da9b70dd3408d12414a4e2e7d39d3fc4 projection-sha256:a6e78fe98ecceecbca6c82fc5a759ca845c03e342a926e6f2b4184221f964665 -->
### DEC-DOCORIGIN-001

1) Name the new doc_artifacts.origin value `pinned_reference`, scoped semantically to "externally-sourced reference material, revision-pinned and materialized into the project tree by a tool" -- not narrowed to "git-pinned" in the name itself, since the fetch *mechanism* (git vs. a future url source) is a separate concern from the provenance *class* the origin column records, and no schema change would be needed later if a non-git source is ever implemented. 2) Implement automatic detection: teach scan_spec_docs to recognise a YAML frontmatter block containing both `resolved_commit` and `source_url` keys (the two fields present in every real ingested file and structurally absent from ordinary hand-authored dev-docs prose) and assign origin='pinned_reference' instead of 'project' when found -- a small, mechanical, no-AI structural check, not a config-driven manual override. 3) Do not extend this to vendor_doc-kind rows in this phase -- vendor_upstream stays exactly as it is; whether a vendor_doc that happens to be externally-pinned should ever share pinned_reference is left an explicit non-goal (unrelated to CG-005's own real-world instance, which is spec_doc-kind only). 4) No explicit backfill/migration step is needed for already-synced databases: doc_artifacts is dropped and fully repopulated on every whole-project sync (CL-DOCORIGIN-001's own traced precedent), so the new classification applies automatically the next time affected files are synced.

Status: status=approved
Provenance: DECLARED
<!-- /codecompass-knowledge -->


## Candidate additions

Add new domain knowledge, edge cases, invariants, or open questions below, strictly between the two marker comments. Content outside this region — including this paragraph — is never read as knowledge; it is just narrative framing CodeCompass leaves untouched.

Plain prose becomes an unclassified Claim (a factual hypothesis, not yet evidence-backed) — this is the default and the common case. Merely mentioning a Decision id anywhere in your prose does NOT make your addition a Requirement, and merely using the word "should" or "must" does NOT make it declared intent — both need the explicit structured forms below.

To propose a REQUIREMENT, start the block with a line reading exactly "Type: Requirement", followed by:
  Decision: <id of an existing, already-approved Decision>
  Statement: <the requirement itself, one line>
  Example: <a Given/When/Then acceptance example>
CodeCompass never invents a Decision on your behalf — a missing or not-yet-approved Decision id, or an Example that doesn't structurally read as Given/When/Then, falls back to an ordinary Claim using your Statement text, never a fabricated placeholder example.

To declare project INTENT (a proposed policy, not yet a fact about the system), start the block with a line reading exactly "Type: Intent", followed by the intended behaviour as plain prose on the lines after it.

Anything else — plain prose with no Type: header — stays an unclassified Claim until a reviewer looks at it.

<!-- codecompass-candidates:start --><!-- codecompass-candidates:end -->
