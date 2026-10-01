# Usability exercise: adopting codecompass-template into tinytodo

Date: 2026-10-01. Template: `codecompass-template` (local clone).
Target project: `invented-project/tinytodo` (one prior commit `df80660`,
clean working tree, two passing tests).

## Step-by-step log

### 1. Read the template's own README.md first

Clear, well-organized, honest about scope ("What this template
deliberately does not include" is a genuinely useful section — most
templates don't say what they're *not*). ~5 minutes to read fully
including the "What's here" and "reusable workflow shape" sections.

### 2. Step 1 of "Adopting this template" — copy contents into tinytodo

This is where the first real blocker showed up. The instruction says:

> Use this repository as a template for your own new project (or copy
> its contents into an existing one).

tinytodo already has its own `README.md` (project-specific: what
tinytodo is, its CLI usage). The template also ships a `README.md` — but
that one describes the *template itself* ("A minimal, MIT-licensed
starting point for a project that wants to adopt CodeCompass..."). A
literal "copy its contents into an existing one" would silently replace
tinytodo's own project README with a description of the template
instead of the project. Same problem, lower stakes, with `LICENSE`: the
template ships an MIT `LICENSE`, and a literal copy would silently assign
a license to a project that hadn't chosen one.

Neither case is addressed anywhere in the README's adoption steps. I had
to stop and make a judgment call rather than proceed confidently:
**kept tinytodo's own `README.md` as-is, and did not copy `LICENSE`.**
I'm confident this is the right call for any real adopter, so I **fixed
it in the template** (see "Fixes made" below) rather than just working
around it quietly.

Everything else copied cleanly with no further collisions: `CLAUDE.md`,
`.gitignore`, `vendor.toml`, `docs/`, `decisions/`, `planning/` (with all
its subdirectories, including the heavier-workflow template
directories, which really were present and non-empty — `assertions/`,
`snapshots/`, `coding-context-selection/`, `documentation-verification/`,
`implementation-comparison/`, `legacy-reconciliation/`, `propagation/`,
each with a real `TEMPLATE.md`, none a stub). Total time for the actual
copy: a couple of minutes once the README/LICENSE question was resolved.

### 3. Steps 2-4 — install CodeCompass, `codecompass sync`, `codecompass query ...`

Skipped, as expected and instructed. This is **not a usability defect**:
the README is explicit that step 2 is a separate `pip install
codecompass-context` (or ecosystem equivalent), clearly distinguished
from "adapt this template to your project." `vendor.toml` is documented
as starting empty and staying empty until CodeCompass is actually run —
exactly what happened. I left `vendor.toml` untouched and noted the skip
in `planning/CONTEXT.md` and `planning/ROADMAP.md` so it doesn't read as
an oversight to the next person who looks at this project.

### 4. Step 5 — adapt CLAUDE.md, docs/architecture.md, planning/ to the project

Since tinytodo is a small *existing* project rather than a blank one,
I filled in `docs/architecture.md` for real (what tinytodo is, its one
module's actual pieces, its zero third-party dependencies, a pointer to
the decision record below) instead of leaving the skeleton headings in
place. This was the template's explicit intent ("Replace this whole
file's content as your project takes real shape") and took about 10
minutes, entirely because there was real source to describe, not because
the template was unclear.

I also updated `planning/ROADMAP.md` and `planning/CONTEXT.md` to
reflect that adoption had happened, and wrote a retro at
`planning/retros/2026-10-01-adopt-codecompass-template.md`, all per the
template's own `CLAUDE.md` §§2, 4, 5 — this wasn't asked for explicitly
by the exercise prompt, but skipping it would have meant adopting the
template's rules on paper while not actually living under them, which
felt like it would undersell the exercise.

### 5. The heavier-weight workflow: `_next_id`'s id-reuse design

**Assertion** (`planning/knowledge/assertions/task-ids-001.md`, using
`assertions/TEMPLATE.md`'s exact shape): straightforward to fill in
*except* that the "Evidence" section's demand for precise, checkable
citations pushed me to actually verify the claim rather than transcribe
the docstring. I ran the project's two existing tests by hand (pytest
isn't installed in this sandbox — `pip install pytest` was blocked by
the environment's externally-managed-Python guard, so I executed the
test bodies directly with plain Python instead, which is a sandbox
limitation, not a template issue) and they passed. More importantly, I
tried the specific edge case the docstring calls out — delete *every*
task, then add a new one — and confirmed by hand that the id really does
reset to `1`. That's real, not assumed, and it also surfaced a genuine
gap: **neither existing test covers this case**, so I logged it as a
candidate in a new `planning/knowledge/learnings.md` (the template
doesn't ship a default file for lightweight learnings entries, just the
`README.md` describing the lifecycle — "one running file or
one-file-per-candidate, whichever suits," so creating `learnings.md`
was a reasonable, template-sanctioned choice, not a guess against the
grain of the instructions).

**Snapshot** (`planning/knowledge/snapshots/task-ids@v1.toml`, using
`snapshots/TEMPLATE.md`'s TOML sidecar shape): this is where the second
real blocker showed up, and it's a blocker inherent to the exercise's
own constraints rather than a template defect. The snapshot format's
"historical integrity" check (`snapshots/TEMPLATE.md`, "Two checks, not
one") is explicitly defined as re-fetching the exact historical
revision via `git show <rev>:<path>` and re-hashing it. The assertion
record I'd just written is brand new and **uncommitted** (the exercise
instructions say not to commit anything in either repo), so there is no
commit to freeze it against — "freeze this uncommitted file's history"
is a contradiction in terms, not a gap in the template's instructions.
I handled this by doing a genuine partial freeze: the two *source*
evidence files the assertion cites (`src/tinytodo.py`,
`tests/test_tinytodo.py`) really were already committed, unmodified,
at `df80660` — confirmed with `git status` showing no modifications to
either — so those two entries in the snapshot carry real, re-checkable
`repository_revision` + `content_hash` pairs. The assertion's own entry
is explicitly marked `repository_revision = "UNCOMMITTED"` with a header
comment explaining why, rather than a fabricated commit hash. I consider
this the honest result of the exercise, not a failure: the workflow is
fully usable, and what's labeled incomplete is labeled incomplete for a
real, stated reason, which is exactly the posture
`docs/mechanical-isolation.md` itself argues for ("report the tier you
actually achieved... don't let a single overall 'done' verdict quietly
launder a known, disclosed limitation").

**Conceptual documentation** (`docs/task-ids.md`, using
`docs/conceptual-documentation-guide.md`'s guidance): the guide's
concrete advice was genuinely usable while writing, not just descriptive
— "pick an architecture from the material, not a template" meant not
forcing this into the `docs/architecture.md` skeleton's headings (it's
mostly one invariant plus its one caveat, so it got its own short page
with "the guarantee" / "the limit" / "why built this way" / "what's
actually been checked"); "cite the snapshot, not the live knowledge
base" meant the page explicitly cites
`task-ids@v1.toml#task-ids-001`, with a note that the snapshot itself is
only partially frozen (so a reader isn't misled about what "cited" means
here); "every claim traces to something citable" meant the open
regression-test gap got stated as a limitation in the doc itself rather
than smoothed over. Linked from `docs/architecture.md` and
`decisions/0001-task-ids-are-never-reused.md` (the latter written first,
since CLAUDE.md §3 of the adopted project calls for a decision record on
exactly this kind of non-obvious tradeoff, and the assertion/snapshot/doc
all point back to it).

## Blockers hit, in order

1. **README.md / LICENSE collision on adoption into an existing project**
   (real template defect — fixed, see below).
2. **pytest not installed, and not installable without
   `--break-system-packages`** — environment limitation, not a template
   issue; worked around by running the test bodies directly with plain
   Python.
3. **Snapshot freezing requires a commit that the exercise's own rules
   forbid making** — not a template defect (a snapshot is inherently a
   freeze of committed history; the template's own docs are explicit
   about what "historical integrity" means and I simply couldn't satisfy
   it for one file in this run). Handled by partial, honestly-labeled
   freezing rather than fabricating a revision.
4. CodeCompass CLI steps unavailable — expected and clearly flagged by
   the template's own text; not a blocker in the usability-defect sense.

## Fix made in the template

`codecompass-template/README.md`, "Adopting this template" step 1: added
an explicit callout that copying the template into an *existing* project
should not blindly overwrite that project's own `README.md` (the
template's own README describes the template, not the adopting project)
or add the template's `LICENSE` (a real per-project choice, not something
to inherit silently). This is the only change made to the template;
nothing else looked like a genuine defect on inspection — I also spot-
checked every markdown cross-reference in the template (`grep` for
`*.md` links/backtick-paths across the whole repo) and every target
exists and is non-empty, including the five heavier-workflow
`TEMPLATE.md` files beyond the two the exercise asked me to use
(`coding-context-selection`, `documentation-verification`,
`implementation-comparison`, `legacy-reconciliation`, `propagation`).

## What changed, concretely

**`codecompass-template/`** (uncommitted): `README.md` modified (the fix
above). Nothing else touched.

**`invented-project/tinytodo/`** (uncommitted, new/untracked):
- `CLAUDE.md`, `.gitignore`, `vendor.toml` — copied from template
  verbatim.
- `docs/architecture.md`, `docs/conceptual-documentation-guide.md`,
  `docs/mechanical-isolation.md` — copied from template;
  `architecture.md` then filled in for real (not left as the skeleton).
- `docs/task-ids.md` — new conceptual documentation, written from the
  snapshot below.
- `decisions/README.md`, `decisions/TEMPLATE.md` — copied from template.
- `decisions/0001-task-ids-are-never-reused.md` — new decision record.
- `planning/ROADMAP.md`, `planning/CONTEXT.md` — copied from template,
  then updated to reflect the adoption and the knowledge-workflow work.
- `planning/retros/TEMPLATE.md` — copied from template.
- `planning/retros/2026-10-01-adopt-codecompass-template.md` — new retro.
- `planning/context-gaps/README.md`, `planning/knowledge/README.md`,
  and all seven `planning/knowledge/*/TEMPLATE.md` files — copied from
  template verbatim (not otherwise modified).
- `planning/knowledge/learnings.md` — new, one candidate entry (the
  untested delete-everything-resets-id-to-1 caveat).
- `planning/knowledge/assertions/task-ids-001.md` — new assertion.
- `planning/knowledge/snapshots/task-ids@v1.toml` — new, partially-frozen
  snapshot (assertion entry marked `UNCOMMITTED`; two evidence entries
  genuinely frozen against commit `df80660`).

`tinytodo`'s own `README.md`, `LICENSE` (absent), `src/tinytodo.py`, and
`tests/test_tinytodo.py` were **not** touched. `src/__pycache__/`,
created incidentally while manually running the tests, was deleted
afterward so it wouldn't linger as an untracked artifact unrelated to the
exercise.

Nothing was committed in either repository, as instructed; both working
trees were left exactly as described above.

## Was this more honest than just checking that links resolve?

Yes, materially. A links-resolve check would have passed this template
with full marks and surfaced none of the above. It would have missed:
the README.md/LICENSE collision entirely (every individual link in the
README resolves fine; the problem is in what a literal reading of step 1
does to a *second* file that already exists on the target side, which
no link-checker would ever model); the fact that the Evidence section's
rigor actually changes behavior (it is what pushed a real manual check of
the delete-everything case, which then found a real untested gap in
tinytodo's own suite); and the genuine, inherent tension between "freeze
into a snapshot" and "don't commit anything," which only shows up when
you actually try to produce a snapshot with a real `repository_revision`
field rather than confirm the TOML schema is well-formed. All three of
these came from actually walking through the adoption and the workflow
end to end with a real (if small) piece of subject matter, not from
checking that every markdown path mentioned in the repo exists.
