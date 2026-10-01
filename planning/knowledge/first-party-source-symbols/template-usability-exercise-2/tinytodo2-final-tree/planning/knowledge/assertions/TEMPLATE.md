# Assertion: <a stable, short id — e.g. `topic-001`>

One record per material thing you've established about your project's
subject matter — a definition, a rule, an invariant, a relationship
between two concepts, how something transforms state, or a boundary
("X is never Y"). Keep the id stable once assigned; if the statement
itself later changes, write a **new** assertion and mark this one as
superseded below — never edit a past assertion's own statement in place.

## Statement

The claim itself, stated precisely and in one place. If it's long enough
to need examples to be understood, that's fine — put the precise
one-sentence version here and the examples in their own section below.

## Kind

One of: `definition` / `relationship` / `rule` / `invariant` /
`state_transformation` / `boundary`. Pick the one that best describes
*what kind of statement this is*, not how important it is.

## Basis

One of:
- `directly_stated` — a source document says this outright.
- `inferred` — you derived it from evidence, but no single source states
  it in these words.
- `proposed_policy` — this is a decision your project made, not a fact
  about the world (a domain rule and a product policy are different
  kinds of claim — don't blur them).
- `observed_behaviour` — you watched the real system do this.

## Evidence

Where this comes from, precisely enough that someone else could check it:
a file and line range, a specific test, a specific command you ran and
its output, a specific external document and section. A citation that
doesn't resolve to something real is a defect in this record, not an
acceptable placeholder.

## Justification

One or two sentences connecting the evidence to the statement. Why does
what you found actually support what you're claiming?

## Examples

Concrete cases that illustrate this assertion.

## Counterexamples

Cases that test or bound it. An empty list here means "I looked and
found none" — not "I didn't check."

## Depends on

Other assertion ids this one relies on, if any (list form: `[topic-002,
topic-005]`). Used later to figure out what needs re-checking when one
of those changes.

## Open questions

Anything genuinely unresolved — distinct from a counterexample (which
tests the claim) and from a gap (no evidence yet). This is "I looked, and
a real question remains."

## Evidence-support state

One of: `supported` / `partially_supported` / `unsupported` /
`conflicting`. A qualitative read of how completely your evidence backs
this — never a number, never a percentage, never "pretty confident."

## Status

One of: `proposed` (not yet evidenced either way) / `supported` /
`contradicted` / `verified` (specifically confirmed against real
behaviour, a higher bar than "supported" — see the note below) /
`superseded`.

**A note on `verified`**: don't set this just because a later
implementation-comparison happened to agree with this assertion in
general. Reserve it for a real, separate, deliberate check of *this
specific* assertion against primary evidence — and be especially
careful with a `rule`/`invariant`/`proposed_policy`: the current
implementation matching what you said doesn't prove the rule itself is
the right one, only that the code currently does what you described.

## Supersedes

The id of the assertion this one replaces, if any — otherwise leave
blank. A withdrawn assertion (evidence now contradicts it, nothing
replaces it) doesn't need an invented replacement — just move its own
`status` to `contradicted` and leave this blank.
