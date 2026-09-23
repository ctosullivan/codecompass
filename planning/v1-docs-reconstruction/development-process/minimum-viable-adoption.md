---
status: PROPOSAL (Phase 64, Cluster C — durable reframing of an existing source table)
---

# Minimum viable adoption

A smaller project — one person, no agent roster, no formal
decision-record process, no roadmap/status-tracking machinery — can
still run Scope → Plan → Domain → Design → Implement without adopting
any of CodeCompass's own governance structure around it. The five
stages are the portable part (see
[`process.md`](process.md)'s "Portability" section); everything a larger
project adds on top of them is optional scaffolding, not a
precondition. *(source:
[`development-methodology.md`](../../v1-redefinition/development-methodology.md)'s
own "Minimum viable adoption" section, reproduced here near-verbatim —
this table already was the lightweight-equivalent artifact the source
document names as needing to reach outside its own internal planning
tree)*

| Stage | A fuller expression of this stage (e.g. CodeCompass's own — see [`codecompass-instantiation.md`](codecompass-instantiation.md)) | Minimum viable equivalent |
|---|---|---|
| **Scope** | A phase's own opening problem statement, reviewed against a roadmap | One paragraph, anywhere durable (an issue, a commit message, the top of a plan file) — the goal, and what's explicitly out |
| **Plan** | A dedicated per-unit-of-work plan file | One short file (or the top of a design note) naming what will change and how it'll be checked |
| **Domain** | A dedicated research role producing structured records, reviewed by an independent skeptic role | A short "what I found, and how I know" note — even a few bullet points citing a real file, line, or command output — plus a second look by anyone else available (a colleague, or the same person coming back to it later with fresh eyes) who is deliberately asked to poke holes in it, not just skim it |
| **Design** | A dedicated documentation role producing a reviewed design document | A short written proposal (a paragraph is enough for a small change) that says what the Domain stage found, what will be built, and what's still unknown — read by the person who actually owns the decision before code is written |
| **Implement** | A curation role assembling a compacted implementation packet, then a formal revalidation step | Whoever writes the code reads the Domain note and the Design proposal first (not just the Plan), and after shipping, updates the Domain note with anything new that was learned — the "reconcile new evidence back" step, done by hand |

## What must not be dropped, even at this minimum

- **The order**: domain understanding before design; design before code.
- **The written form**: even one paragraph — not "it's in my head."
- **The independent second look**, before a genuine ambiguity gets
  decided.

## What may be dropped

- Dedicated roles for each stage.
- Structured record schemas — plain prose is fine.
- A formal review-gate lifecycle with named states.
- Any project-specific concept or tooling.

A team of one can still distinguish "I read this in the docs" from "I
tested this myself" from "we decided to do X anyway" — that distinction,
not the tooling built around it, is what this process actually protects.
*(source: "Minimum viable adoption," closing paragraph — quoted near
verbatim, since it is already written for exactly this kind of reader)*
