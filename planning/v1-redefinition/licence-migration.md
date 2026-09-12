# Licence migration plan — MIT → GPL-3.0-or-later (required output 3)

Gate **G11/G12** (`realignment-2026-09.md` §7). Implemented at Phase 43d,
**only after explicit approval** — this document is the plan, not the
change.

## 1. Why

`hledger` (the compatibility reference for Ledgerkit, and increasingly a
project CodeCompass itself indexes/relates evidence about) is
**GPL-3.0-or-later**, confirmed at the SPDX-field level in its own
`package.yaml` files (`realignment-2026-09.md` §1.2). Aligning
CodeCompass's own licence with the same family removes the need for an
artificial clean-room boundary when a CodeCompass development agent
inspects `hledger` source, documentation, or tests to understand
behaviour it is helping relate for Ledgerkit's benefit — the same
source-assisted development model Ledgerkit itself is adopting for its
own hledger-compatibility work.

This is **not** because CodeCompass bundles or redistributes hledger
code — it doesn't and won't (§4). It is because a permissively-licensed
tool built partly by inspecting a copyleft project's source, without
matching licence terms itself, invites exactly the kind of "did we
launder GPL logic through an MIT wrapper" question this plan exists to
pre-empt. GPL-3.0-or-later on CodeCompass's own code removes that
question at the source.

## 2. Current state (inspected, not assumed)

| Item | Current value | Source |
|---|---|---|
| `LICENSE` | MIT, copyright "Cormac O' Sullivan", 2026 | `LICENSE` (repo root) |
| `pyproject.toml` | `license = { text = "MIT" }`; classifier `License :: OSI Approved :: MIT License` | `pyproject.toml` |
| `README.md` | `## License` → "MIT — see `LICENSE`." | `README.md` |
| `CONTRIBUTING.md` | No licence mentions | grep, confirmed empty |
| Copyright ownership | **Single author** — `git log --format='%an <%ae>'` returns exactly one identity across all 129 commits | `git log`, this session |
| Third-party contributions requiring consent | **None** — no other committer exists | as above |
| Bundled/vendored third-party source | **None committed** — `vendor/` (per-dependency cloned upstream source) is fully `.gitignore`d, never tracked (`decisions/0004`/`0010`) | `.gitignore`, `git ls-files \| grep '^vendor/'` (empty) |
| Runtime dependencies' own licences | `typer`, `rich`, `anthropic`, `pipdeptree` — all MIT | `pip show <pkg>`, this session |
| Generated templates embedding a licence string | **None found** — `skill.py`/`commands.py`/`claude_md.py`'s generated output (Skills, `.mdc`, `/discovery`, routing table) contains no licence text to update | grep across `src/codecompass/{skill,commands,claude_md}.py`'s literal templates, this session |
| Git tags / PyPI releases | **None** — nothing published under any licence | `git tag -l` (empty), `decisions/0047`/`0048` |

**Conclusion: this is a legally simple relicensing.** One copyright
holder, no third-party code to review or negotiate, no published
release history to reconcile (there is none — MIT never applied to any
public artifact). The only genuine work is doing it as a deliberate,
documented, reviewable change rather than a silent file swap.

## 3. Mechanical changes (Phase 43d, held behind gate G12)

| File / location | Change |
|---|---|
| `LICENSE` | Replace MIT text with the canonical GPL-3.0-or-later `COPYING` text (the FSF's own instructions: use the license text verbatim, unmodified; add the standard "how to apply" notice block with CodeCompass's name, a copyright line, and the "or (at your option) any later version" clause — this is what makes it "-or-later", not a separate declaration). Retain a copyright line for the existing MIT-era history (the licence *going forward* changes; historical commits remain describable as MIT-licensed at the time they were made — §5). |
| `pyproject.toml` | `license = { text = "GPL-3.0-or-later" }`; classifier `License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)` (the exact Trove classifier string PyPI recognises) |
| `README.md` | `## License` section: "GPL-3.0-or-later — see [`LICENSE`](LICENSE). (Previously MIT; see `decisions/0053` for the relicensing rationale.)" |
| `CONTRIBUTING.md` | Add a short note: contributions are made under the project's current licence (GPL-3.0-or-later going forward); no separate CLA exists or is planned (single-maintainer project) |
| `ai-docs/README.md` | Check for any licence-adjacent capability/boundary claim (none currently expected, but re-verified at Phase 43d, not assumed here) |
| `decisions/0053` | New ADR — see §6 |

**Explicitly not changed:** no git tag or release is rewritten (none
exist); no historical commit is re-labelled; the change lands as one
normal phase commit, dated, in `CHANGELOG.md`'s `[Unreleased]` section
like any other phase (promoted to a dated section only at Phase 70/G9,
same as everything else — G2-b is unaffected by this change).

## 4. Source-assisted development policy — provenance and attribution

This is the policy this plan exists to enable (required output 10, as it
applies to CodeCompass's *own* development and to what CodeCompass hands
Ledgerkit via the adoption blueprint). Four distinct activities, each
with its own attribution requirement:

| Activity | What it means | Attribution requirement |
|---|---|---|
| **Source inspection** | Reading `hledger` source to understand behaviour, terminology, or edge cases before relating evidence about it in CodeCompass's own context graph or Ledgerkit's compatibility work | None beyond the normal `vendor_doc`-style provenance CodeCompass already records for any upstream source it reads (commit/revision it was read at) |
| **Algorithm/architecture understanding** | Learning *why* hledger's model works a certain way (e.g. its query-semantics evaluation order) to inform an independent design decision | Cite the source location informally in an ADR or design doc if it materially shaped the decision (already this project's habit — see how `decisions/*` cite `planning/*` and vice versa) |
| **Adapted implementation** | Writing new code whose *structure* is influenced by having read the reference implementation, but whose actual text is independently written | Record the influence in a code comment or ADR ("modelled on hledger's X, independently implemented") — this is the normal, expected outcome of source-assisted development and carries no special licence obligation beyond CodeCompass's own (GPL-3.0-or-later) licence covering the resulting code |
| **Directly translated material** | Code, text, or test fixtures copied or mechanically translated from hledger with only syntactic adaptation | **Must** carry an explicit provenance comment naming the exact upstream file/commit/licence, and the receiving project's licence must be GPL-compatible (which GPL-3.0-or-later is, by construction) — this is the one category that actually depends on the relicensing having happened first |

**CodeCompass itself is not expected to perform "directly translated
material"** — it discovers, selects, connects, grounds, retrieves, and
explains (README.md §1.9); it does not reimplement hledger behaviour.
This table exists because (a) the relicensing is *justified* by wanting
to remove friction from *Ledgerkit's* use of this model, and CodeCompass
should document the policy it is enabling even though it isn't the
primary user of the "directly translated" category, and (b) the
`adoption-blueprint.md` hands this same table to Ledgerkit, where all
four categories are genuinely in play.

**Executable verification stays independent of source inspection
regardless of licence** (this task's own instruction, restated): reading
hledger's source explains *intent*; running the `hledger` executable and
comparing output is what actually verifies external compatibility. A
licence alignment changes what agents may *read*, not what counts as
*proof*.

## 5. Historical / release-history integrity

- No git tag exists (`git tag -l` empty) and nothing has been published
  to PyPI. **There is no published release history to preserve or
  falsify.** The "do not rewrite historical release tags" constraint
  this task warns about does not bind here, for the same reason it
  didn't bind the original v1 redefinition (`README.md` §2.4).
- Individual **commits** made before the relicensing commit remain, as a
  historical fact, made under MIT (git history is not rewritten; the
  licence file at any given historical commit correctly shows MIT at
  that point in time). The relicensing takes effect from the commit that
  changes `LICENSE`/`pyproject.toml` forward. This is the standard,
  legally unremarkable way an unpublished, single-author project
  changes its licence.

## 6. ADR

Proposed draft in `proposed-governance-changes.md` §C
(`decisions/0053`, not yet written to `decisions/`) — argues the
specific reason (source-assisted, hledger-facing development posture),
the alternatives considered (stay MIT + maintain a clean-room boundary;
dual-license), and the consequence that CodeCompass's own code becomes
GPL-3.0-or-later going forward with no bundled-code entanglement.

## 7. Human approval requirement

**Gate G12 — ✅ approved 2026-09-12** ("Proceed as recommended").
`realignment-2026-09.md` §7. This was a licence change — even though the
legal analysis here is simple (§2's conclusion), the downstream effect on
anyone using CodeCompass (permissive → copyleft) is exactly the kind of
decision this project's own governance reserves for explicit human
approval, same posture as `CLAUDE.md` §0 gives `CLAUDE.md` itself. §3's
mechanical changes are now implemented (Phase 43d); `decisions/0053` is
`Accepted`.

## 8. Verification (once approved and implemented)

- `pyproject.toml` parses; `pip install -e .` still succeeds (SPDX
  licence-field syntax is valid).
- `python scripts/check_user_docs.py --strict` clean (no check currently
  asserts a specific licence string, so none should newly fail; if one
  should be added — e.g. "LICENSE and pyproject.toml licence fields
  agree" — that's a small Phase 43d addition, not a blocker to write
  this plan).
- `git log` shows the change as one normal, dated commit.
- `CHANGELOG.md` `[Unreleased]` gains an entry (same discipline as every
  other phase).
