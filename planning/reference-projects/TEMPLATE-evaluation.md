<!-- Copy to `<name>/<NN>-<task-slug>.md` for each evaluated task. Structure
     is verbatim from context-quality-evaluation.md §2 — fill in every
     section, do not skip one. See that spec for the ground rules (§1),
     criteria definitions (§3), verdict definitions (§4), and
     context-advantage definitions (§5). -->

# Context-quality evaluation — <task slug>

## Setup

- **Reference project:** <url>
- **Pinned commit:** <sha>
- **CodeCompass revision:** <sha / version>
- **Task:** <one paragraph — the genuine development task, drawn from the
  project's own roadmap/backlog/bugs, never invented for this evaluation>
- **Context CodeCompass supplied:** <verbatim or attached — graph query
  results, generated Skill content, "what matters for this task" output>

## Criteria assessment

<One short paragraph + a rating (strong / adequate / weak / n/a) per
criterion.>

| Criterion | Rating | Notes |
|---|---|---|
| Accuracy | | Were CodeCompass's claims correct against the actual target source/docs? |
| Relevance | | Was the supplied context actually connected to *this task*, or generic? |
| Completeness | | Did it contain the *important* context needed (not everything)? |
| Freshness | | Did it reflect the actual pinned revision and dependency versions in play? |
| Grounding / provenance | | Could each material claim be traced to a specific source/evidence location? |
| Noise | | Was irrelevant information kept reasonably low? |
| Safety / trustworthiness | | Did CodeCompass present anything incorrect/misleading as authoritative? |

## Verdict: PASS | PASS WITH GAPS | FAIL

<One paragraph justifying it, per the verdict definitions (§4). Remember:
incorrect/misleading content outranks incomplete content.>

## Context advantage: LOW | MODERATE | HIGH

Could a competent fresh Claude session have obtained equivalent context
trivially through ordinary repository inspection (a few greps, reading an
obvious file, one `--help`)? <yes / partly / no> + one paragraph.

## Material gaps / failures

- <bullet — each also filed as a candidate learning with an ID>

## Would this have misled the implementing agent? yes | no | partially

<The single most important line — expand if yes/partially.>
