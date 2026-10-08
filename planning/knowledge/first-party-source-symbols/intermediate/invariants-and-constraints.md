# first-party-source-symbols — invariants and constraints

<!-- codecompass-knowledge: CL-FPSS-002 semantic-sha256:84b9a0ef0af5c96661d6947c574e0680223aa75805224bb6c25da49f4aea6b13 projection-sha256:83b684a8bd854f9eaaa6a1ca100ddb6306bb56d9fc2907ebfbd1a40e38f3010f -->
### CL-FPSS-002

The five-value exposure classification (public/restricted/internal/ conventional_private/unknown) is applied per-language as a strict, disjoint subset of the vocabulary, never the full five values by any one language's real extractor: Python produces only public (no leading underscore) or conventional_private (leading underscore) -- e.g. `def public_fn(): ...` -> public, `def _private_fn(): ...` -> conventional_private. Rust produces public (bare `pub`), restricted (any `pub(crate)`/`pub(super)`/`pub(in path)`/`pub(self)` form), or internal (no modifier) -- e.g. `pub fn foo() {}` -> public, `pub(crate) fn bar() {}` -> restricted, `fn internal_fn() {}` -> internal. JavaScript/TypeScript produce only public (leading `export` present) or internal (absent) -- e.g. `export function add(...) {}` -> public, `function internalHelper() {}` -> internal. `unknown` is never produced by any of the three real extractors this module ships; it exists only as a schema-level/vocabulary allowance for a hypothetical future, less-certain extractor. `conventional_private` is deliberately distinct from `internal`: the former names a naming *convention* a caller can freely ignore, the latter names a language-enforced non-visibility default -- Python's leading-underscore convention is never classified as `internal`.

Supporting evidence: ["EV-FPSS-003", "EV-FPSS-004", "EV-FPSS-005", "EV-FPSS-020"]
Status: status=supported, evidence_support_state=supported
Provenance: OBSERVED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-FPSS-004 semantic-sha256:46b9e3c6e5afe4445cd4bc859f2f2af19e6e718c6ce565da266e0b29c652a610 projection-sha256:33bc9be09de29b4eaae8b598c16120ee719f29938d153a1e4808a398c41afb3d -->
### CL-FPSS-004

The occurrence-based symbol identity rule -- UNIQUE(source_file_id, name, kind, line) at the schema level, line: int (never None) in SourceSymbol -- exists to solve a real, reproducible problem: ordinary function overloading (a real, common language feature in both Python via @typing.overload and TypeScript via repeated signature declarations) produces multiple declarations that legitimately share one (source_file_id, name, kind) triple but occupy distinct lines. A name-only (or name+kind-only) identity key would make the second such declaration collide with the first as a uniqueness violation the moment any real project containing an overload was synced. The problem this solves is not merely a name clash in the abstract -- it is specifically that overloads are multiple *individually real* declarations, not duplicate facts about one logical symbol, so an identity scheme that could only keep one of them (whether by rejecting the insert or by silently merging/overwriting) would discard real, legitimate information a caller inspecting a specific line deserves an accurate answer about.

Supporting evidence: ["EV-FPSS-010", "EV-FPSS-011", "EV-FPSS-012", "EV-FPSS-017"]
Status: status=supported, evidence_support_state=supported
Provenance: OBSERVED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-FPSS-005 semantic-sha256:9ede5989bba2837c01ee3283c297a02160029323868f110cc5093ba55eb82200 projection-sha256:884d1c34a9f3b3557c118e3669999efac38d8cd185e8ca2d2d4d505893325782 -->
### CL-FPSS-005

meta.source_index_version is documented (by decisions/0065 and the phase-77 plan) as a project-level marker whose *absence* (not a NULL value -- its total absence as a key) is meant to mean "first-party source has never been indexed under Phase-77-aware code," distinct from a per-file symbol_index_status value, and is meant to be written unconditionally by rebuild_deterministic on every Phase-77-aware rebuild (even one finding zero first-party files) so that a genuine "not yet indexed" project state is never confused with a genuine "indexed, but this symbol doesn't exist" negative result. This statement originally described documented design *intent* only, as both source documents themselves frame it (the ADR's own "Decision" section, the plan's own "new, this amendment" section) -- the producing dispatch's own export contained no code implementing either the write path (rebuild_deterministic) or the read/gate path (cli.py). A subsequent adversarial review with full repository access confirmed both directly: sync.py:417-438 unconditionally passes source_index_version="1" into rebuild_deterministic, graph.py:1071-1076 writes it whenever non-None, and cli.py:1094/1157 gate on the key's absence before reading source_files/source_symbols -- matching the documented intent exactly, including the "written even with zero first-party files" detail.

Supporting evidence: ["EV-FPSS-014", "EV-FPSS-018"]
Status: status=supported, evidence_support_state=supported
Provenance: OBSERVED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-FPSS-006 semantic-sha256:82145aa4c47d0ce5af9087d9b738b02e3afd99e22c0ce40e73701b5a6b9406d2 projection-sha256:b46c96b9d7549049e36b9228af0260bbe33b9b9ed7a905c89052230a1a95817f -->
### CL-FPSS-006

_migrate_source_files_columns implements a nullable-everywhere migration contract, not a "NOT NULL once populated" contract: it adds each of source_files's four new Phase-77 columns (language, content_hash, symbol_index_status, symbol_index_diagnostic) via a separate `ALTER TABLE ... ADD COLUMN` statement, each with no NOT NULL constraint and no DEFAULT clause, gated by a PRAGMA table_info introspection check so only genuinely-missing columns are added (an idempotent, rerun-safe design). It never drops or recreates source_files, specifically because source_files.id is referenced by uses_edges.source_file_id ON DELETE CASCADE, and a drop/recreate would cascade-delete every uses_edges row -- this same column set is also declared identically (all four nullable, no NOT NULL) in the CREATE TABLE source_files statement used for a brand-new database, so a fresh and a migrated database are meant to end up with identical column definitions. The additional claim that this equivalence is "verified directly (test_graph.py)" is the ADR's own self-report; the original dispatch's export did not include tests/test_graph.py, so that specific test's existence and outcome could not be independently confirmed at that time. A subsequent adversarial review with full repository access located tests/test_graph.py::test_fresh_and_upgraded_source_files_schema_are_identical, read it, and ran it plus its sibling migration-safety test against the real, unmodified code -- both PASS. The ADR's self-citation is accurate, not merely asserted.

Supporting evidence: ["EV-FPSS-015", "EV-FPSS-019"]
Status: status=verified, evidence_support_state=supported
Provenance: OBSERVED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-FPSS-007 semantic-sha256:f42da56a0ecc1447c046ea24c8fafa6397d43760815cd399de42ec749d31a7a1 projection-sha256:4887e3a877b1d0f1f1e3682a5653f285d4955f9f6927e3faaa94c5897435e900 -->
### CL-FPSS-007

The indexed_partial techniques' "honest, coarse" fidelity limitation that decisions/0065/planning/phase-77 describe only in general prose ("a multi-line signature, an unusual formatting style, or (rarely) a false match inside a string/comment can defeat them") is real and trivially reproducible with ordinary Rust/TypeScript constructs, but its concrete shape is narrower and more specific than a first reading of that prose suggests. Specifically: (a) a parameter list spanning multiple physical lines does NOT, by itself, defeat either extractor, because both regexes only need to match the keyword+name text on the line where a declaration's own name first appears; (b) a single-line "//" comment or a single-line string literal containing declaration-like text does NOT produce a false match, because both item regexes anchor with `^` against each line's own stripped leading content; but (c) a multi-line Rust raw-string literal whose own interior line matches the anchored pattern DOES produce a genuine false-positive source_symbols row, and (d) a plain "/* ... */" block comment in JS/TS (as opposed to a "/**" JSDoc comment, which is specially recognized) is not treated as a comment at all, so a commented-out declaration inside one DOES produce a genuine false-positive row. Both real false positives are silent: status stays indexed_partial, diagnostic stays None, with nothing in the returned SourceFileExtraction distinguishing them from genuine declarations.

Supporting evidence: ["EV-FPSS-008", "EV-FPSS-009", "EV-FPSS-021", "EV-FPSS-022"]
Status: status=verified, evidence_support_state=supported
Provenance: OBSERVED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-FPSS-008 semantic-sha256:5099b8635d182acb1b6b89a775cee29938e2dea4d31f1de66a7645d5bd66947e projection-sha256:6334b5ee2fbb2c63099985bd8c65118021bd017281ccd9176819870dd7c3b2a3 -->
### CL-FPSS-008

Two further extraction-scope/fidelity limitations exist beyond CL-FPSS-007's indexed_partial false-positive boundary, neither mentioned by decisions/0065 or the phase-77 plan, both structural properties of the extractors rather than untested edge cases: (a) Python extraction is top-level-only -- _extract_python_source_symbols walks only ast.iter_child_nodes(tree), the module's own direct children, with no recursive descent into a ClassDef's or FunctionDef's own body, so a method defined inside a class or a function nested inside another function is never visited and never emitted as its own SourceSymbol row; (b) a JS/TS const binding's kind is recorded literally as "const", never "function", regardless of what it's bound to -- _JS_FAMILY_ITEM_RE's third capture group is one of the literal keywords (function/class/interface/const/type/enum), and _extract_js_family_source_symbols assigns kind=kind directly from that match with no inspection of the right-hand side of an "=", so `export const foo = () => {}` is schema-indistinguishable from `export const PI = 3.14`.

Supporting evidence: ["EV-FPSS-023"]
Status: status=supported, evidence_support_state=supported
Provenance: OBSERVED
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
