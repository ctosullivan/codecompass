# Context-quality evaluation — Stage 89C Task B, `ReportSpec.with_combined_section` (blind controlled comparison, two drafts)

## Verdict / rating summary (read first)

| | Draft 1 | Draft 2 |
|---|---|---|
| **Verdict** | PASS WITH GAPS | PASS WITH GAPS |
| **Context advantage** | LOW | LOW |
| **Would this have misled the implementing engineer?** | no | no |

Both packets were accurate and non-misleading on the one claim (`CL-BFS-004`)
they carried. Neither packet's incremental contribution clears the bar for
MODERATE, for reasons explained in full below — chiefly a **confound in the
comparison design itself** (the task specification each engineer received
apparently stated the correct design answer directly), not a defect unique to
either packet.

## Setup

- **Reference project:** Ledgerkit (local; pristine pre-task baseline
  inspected at `/tmp/claude-1000/.../scratchpad/stage89c-exec/ledgerkit-seed`).
- **Pinned commit:** `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9` (confirmed by
  `git log`/`git rev-parse` in the seed checkout and in both verification
  checkouts; also independently confirmed by both drafts' own reports via
  `git log --oneline -5`).
- **CodeCompass revision:** not separately stated in the materials supplied;
  the packets' own `contract_revision`/`knowledge_revision` fields are the
  only CodeCompass-side versioning present (see Grounding below).
- **Task:** Add `ReportSpec.with_combined_section(name, *sections, label=None) -> ReportSection`,
  a static method that unions multiple `ReportSection`s' `accounts` (and
  `exclude`) patterns into one new section, without mutating inputs. The
  central open design question, deliberately left to the engineer: does
  `with_combined_section` need its own de-duplication/aggregation logic, or
  does `balance_from_spec`'s existing OR-union posting-match logic already
  prevent double-counting when two sections' patterns overlap?
- **Context CodeCompass supplied:** reproduced in full below (both packets
  verbatim except where noted).

## Ground truth, established directly against `ledgerkit-seed`

Read `ledgerkit/reports.py::balance_from_spec` and `ledgerkit/models.py`
(`ReportSection`/`ReportSpec`) directly. The decisive code (reports.py,
confirmed at line 663 in the seed checkout):

```python
# Section account patterns: OR logic — posting must match at least one.
if not any(_matches_pattern(pat, posting.account) for pat in section.accounts):
    continue
# Section exclude patterns: posting must not match any.
if any(_matches_pattern(pat, posting.account) for pat in section.exclude):
    continue
...
pairs.append((account, posting.amount.quantity))
```

For a given posting, inclusion is gated by a single boolean `any(...)` test
per section, not a per-pattern loop that could append more than once. This
means: **a posting matching more than one pattern in `section.accounts` is
still only ever appended to `pairs` once.** Therefore `with_combined_section`
needs **no extra dedup/aggregation logic of its own** — unioning the account
patterns (and excludes) from the input sections into one tuple and handing
that to the unmodified `balance_from_spec` is correct by construction. I
confirmed this arithmetically against the real `tests/fixtures/filtered.journal`
fixture (`expenses:food:groceries` = £150.00, `expenses:food:coffee` = £9.00,
`expenses:housing:rent` = £1,200.00): a section combining a `"groceries"`
pattern and a broader `"food"` pattern (which also matches `groceries`) sums
to £159.00, not £309.00 — matching the pinned acceptance suite's own
assertion. This is the correct answer to the task's central question.

## Independent re-derivation of the packet diff

I diffed `draft-1-packet.json` and `draft-2-packet.json` myself (byte-level,
via `json.load` + field comparison), not by trusting either report. Result:

- Three items are **byte-for-byte identical** in both packets: the claim
  `CL-BFS-004` (the `any()`-based "counts exactly once" fact, cited at
  `reports.py` line 663), the requirement `REQ-BFS-002` (an "accepted
  obligation" framing of the same fact as a MUST), and the evidence
  `EV-BFS-001` (a description of what `balance_from_spec` does overall).
- Draft 2's packet contains **one additional item absent from Draft 1's**:
  `EV-BALANCEFROMS-004`, a `scoped_verification`-authority evidence record
  asserting "a real, independently executed oracle run of the
  newly-coverable check 'overlapping-account-patterns-no-double-count'
  passes," with its own `run_id`, `tested_subject_digest`, and
  `test_input_digest`.
- Consistent with that addition, `CL-BFS-004`'s own `consistency.reasons`
  string differs between the two packets: "3 required scope(s) have no
  passing evidence at all" (Draft 1) vs. "2 required scope(s) have no
  passing evidence at all" (Draft 2) — i.e. the extra evidence item reduces
  the claim's own unmet-scope count by one, correctly and consistently.

**Is the differing content itself well-grounded?** Yes, on inspection.
`EV-BALANCEFROMS-004`'s `tested_subject_digest`
(`7a2c2d039f3991aae6b6fa2f7df09e22ae7d4e530c93cdf45c55cb152fef6c78`) matches
neither draft's own eventual implementation digest (I compared it against
both drafts' own later `oracle-result.json` `tested_subject_digest` values,
which are two different hashes, neither equal to this one) — so this is
independent, pre-existing evidence from a separate reference run, not
information leaked backward from either engineer's own future code. The
check it reports on (`combined-section-no-double-count`) is exactly the
scope both drafts' own later, independently-executed verifier oracle runs
also confirmed (see below) — I reran both drafts' pinned acceptance suite
myself and got the same `PASS` result. So Draft 2's one extra item is both
accurate and non-contaminating.

## Freshness / provenance check (shared by both packets)

Both packets cite `source_revision: "ledgerkit@7224bb5c113cd3aad7e86e994365703cd0070154"`
for `CL-BFS-004` and `EV-BFS-001` — **not** the actual pinned commit
(`a7740fd...`). I checked this directly: `7224bb5c` is a real, older commit
in the seed repo's history (`git cat-file -t` confirms it's a commit; `git log --oneline --all` finds it as "clean-room assertion research... phase-3"). Critically, `git diff 7224bb5c a7740fd -- ledgerkit/reports.py`
produces **no output** — the file is byte-identical between the two
revisions, and `git blame` traces the cited lines to an even earlier commit
(`acc93a39`, 2026-05-02), well before either revision. So the claim is
still accurate at the actual pinned commit despite citing an older
`source_revision` — this looks like content-addressed "last confirmed true
at" provenance rather than "HEAD at packet-generation time," and in this
instance it does not produce a stale or wrong claim. It is, however, a
non-obvious provenance subtlety that could mislead a reader who takes
`source_revision` to mean "the pinned commit" at face value; flagged as a
gap, not an error.

## A shared, independently confirmable packet defect: silent per-item truncation

I checked the raw JSON. Every `summary` field in both packets is
hard-truncated at **exactly 280 characters**, with no ellipsis marker, and
three of the four items (`CL-BFS-004`, `REQ-BFS-002`, `EV-BFS-001`, in both
packets) are cut off mid-word ("...it matc", "...journal fi", "...with
balance"). Yet the packet's own `bounds` object reports
`"truncated": false`. This is a verifiable internal inconsistency: the
packet's self-reported completeness metadata does not account for
per-item field truncation. It did not mislead either engineer in this case
(both went to the real source rather than relying on the summary text
alone), but it is a trustworthiness/grounding defect that generalizes
badly — a `bounds.truncated` check cannot be relied upon to detect this
class of silent truncation. This applies identically to both drafts (not a
differentiator between them).

## Criteria assessment

| Criterion | Draft 1 | Draft 2 | Notes |
|---|---|---|---|
| Accuracy | adequate | adequate | Both packets' claims are correct against the real source (confirmed independently). |
| Relevance | strong | strong | Narrowly scoped to the exact design question at issue. |
| Completeness | weak | adequate | Draft 1: 3 items, all `"unconfirmed"`, zero empirical confirmation attached. Draft 2: same 3 items plus one genuine, correctly-scoped passing-oracle-run record that closes one of the three unconfirmed scopes. |
| Freshness | adequate | adequate | `source_revision` cites an older commit than the actual pin; content at both revisions is identical (verified), so not actually stale, but the citation itself is not the pinned SHA. |
| Grounding / provenance | adequate | strong | Draft 2's extra evidence item carries independently reproducible provenance (digests/run id) of a kind the other three items lack entirely. Shared truncation defect (above) dents both. |
| Noise | strong | strong | Compact; no irrelevant content in either packet. |
| Safety / trustworthiness | adequate | adequate | No overclaiming — both packets honestly flag every item `"unconfirmed"`. The `bounds.truncated: false` vs. actual mid-word truncation is a real (shared) defect. |

## Did either engineer add unnecessary/incorrect dedup logic?

No. I read both `draft-N-code/ledgerkit/models.py` directly.

- **Draft 1**: unions `accounts`/`exclude` via an explicit `seen_accounts`/
  `seen_exclude` set-and-list pattern (preserves first-seen order, drops
  exact-duplicate pattern strings only). No amount-level aggregation or
  posting-matching logic is added. Its own docstring states explicitly:
  "...so unioning patterns from several sections into one `accounts` tuple
  needs no extra deduplication here."
- **Draft 2**: unions via `tuple(dict.fromkeys(...))` (functionally
  identical — order-preserving de-duplication of pattern strings only). Its
  own docstring: "merging two sections' patterns into one `accounts` tuple
  cannot cause a posting to be counted twice... because `balance_from_spec`
  already includes a posting once its account matches *any* of
  `section.accounts`."

Both implementations are **functionally equivalent and correct** — neither
added spurious amount-aggregation/dedup logic; both correctly delegate
counting semantics to the existing, unmodified `balance_from_spec`. I
independently ran the pinned 11-method acceptance suite
(`tests/test_combined_section_acceptance.py`) against both drafts' own
verification checkouts (`ledgerkit-verify-control`/`ledgerkit-verify-treatment`,
still present on disk with working `.venv`s) myself: **11/11 pass for both**,
and I also ran each draft's full regression suite myself (957 passed for
one checkout, 958 for the other — the one-test difference is explained by
one draft's own test file adding one extra test method beyond the other's,
not a behavioural difference). Neither implementation regressed anything
else in the 950+-test suite.

## Did each engineer actually use their packet's own Evidence, or re-derive independently?

Both. Read both `draft-N-report.md` directly.

- **Draft 1's report** cites its packet's items by their real IDs
  (`CL-BFS-004`, `REQ-BFS-002`, `EV-BFS-001`) and explicitly states: "I used
  the packet as a **pointer to what to verify**, not as a substitute for
  verification — its own `consistency` block flags every item as
  `'unconfirmed'`... I did not treat any of its claims as settled." It then
  independently re-read `balance_from_spec`, traced the control flow by
  hand, and wrote its own fresh executable test before concluding.
- **Draft 2's report** cites `CL-BFS-004` *and* `EV-BALANCEFROMS-004` (the
  one item unique to its own packet) and similarly states the packet's
  status was "unconfirmed by its own consistency metadata — it's presented
  as a claim to verify, not a given," then independently verified the same
  fact against the real source and wrote its own fresh test plus an ad hoc
  verification script before concluding.

Both reports accurately reflect their own packet's actual contents (no
report invents an item its own packet didn't contain, and no report omits
an item its packet did contain) — a good-faith, correctly-cited use of
Evidence by both, in both cases subordinated to independent verification
rather than trusted blindly.

## Equal-raw-access check (`L-027`)

Both engineers' own reports describe directly reading `ledgerkit/reports.py`
themselves — Draft 1: "`ledgerkit/reports.py` lines 590–696... to verify the
context packet's claim... at the real current line number"; Draft 2:
"`ledgerkit/reports.py`, `balance_from_spec` (lines ~600-693, full docstring
+ body). Read closely to confirm the exact matching mechanics... This is the
load-bearing fact for the whole task." Both had **full, unscoped access to
the one decisive file**, both actually read it, and both independently
confirmed the packet's central claim by hand before writing any code. Per
`context-quality-evaluation.md` §1's `L-027` rule, this means almost all of
the credit for the correct design decision belongs to **agent diligence
reading the one obviously-relevant file the task itself names**, not to the
packet. The packet functioned, at best, as a one-sentence pointer to a fact
a diligent agent would find anyway in a ~100-line function it was always
going to have to read to implement the method correctly.

## A confound worth naming explicitly

Both reports quote language from their own received **task specification**
(not the context packet) that already states the correct design answer.
Draft 1 quotes: *"This constructor itself performs no aggregation and calls
no posting-matching logic — it only merges the two declarative pattern
tuples."* Draft 2: *"the task description explicitly flagged it as 'the
most important sentence in this task specification.'"* If the task prompt
each engineer received already stated the correct answer outright
(independent of, and prior to, whatever either context packet said), then
this comparison cannot cleanly attribute either engineer's correct design
decision to their packet at all — the task framing itself pre-answered the
central question for both arms symmetrically. I note this as a disclosed
observation per the dispatch instructions (not something I used to infer or
act on the draft↔arm allocation) rather than as a finding about either
packet's own quality, but it materially weakens how much credit either
packet can honestly claim for the correct outcome, and should be considered
before this comparison is used to argue CodeCompass materially helped on
this task.

## Disclosed observation: accidental de-blinding in raw materials

While reading `draft-N-verify/oracle-raw/*.txt` to independently confirm the
primary-scope oracle result (a step required by this evaluation's own
methodology), I incidentally observed that the raw subprocess transcripts
embed an unredacted absolute path containing the literal real checkout
names (`ledgerkit-verify-control` for Draft 1's raw output,
`ledgerkit-verify-treatment` for Draft 2's). The materials' own
`redaction-log.md` explicitly redacted this same path from
`oracle-result.json`'s `raw_output_ref` field but did not redact the
identical path as it appears a second time, verbatim, inside the raw
`.txt` transcript files themselves — an incomplete redaction sweep. I am
disclosing this because it might reveal the control/treatment allocation;
per this dispatch's own instructions I did **not** act on it, guess from it,
or let it change any rating above — every verdict, advantage rating, and
criterion score in this report was reached from the two packets' and two
implementations' own content on their own technical merits, independent of
which named arm either draft happens to correspond to.

## Material gaps / failures

- **G1 (shared, both drafts).** `bounds.truncated: false` does not account
  for the packet's own per-item 280-character field truncation — three of
  four items in both packets are cut off mid-word. A consumer that checks
  `bounds.truncated` to decide whether it's safe to rely on `summary` text
  verbatim will be wrong. Candidate learning: packet-bounds truncation
  detection should check per-field, not only aggregate item/char counts.
- **G2 (shared, both drafts).** `source_revision` on `CL-BFS-004`/`EV-BFS-001`
  cites a commit (`7224bb5c...`) distinct from the actual pinned commit
  (`a7740fd...`) used for the task, with no explanation of the "last
  confirmed at" semantics that make this non-stale. Harmless here (content
  is identical at both revisions, verified), but the metadata alone doesn't
  let a consumer know that without doing the same git archaeology I did.
- **G3 (Draft 1 only, relative completeness).** Draft 1's packet carries
  zero empirical/oracle confirmation for any of its three items (all
  "unconfirmed," 3 unmet scopes) — the one real content difference
  identified in the diff above is Draft 2's additional, accurate,
  non-contaminating confirming evidence item that Draft 1 lacks.
- **G4 (design confound, both drafts, non-packet).** The task specification
  itself appears to state the correct design answer directly, independent
  of either context packet — see "A confound worth naming explicitly"
  above. This limits how much of either engineer's correct conclusion can
  honestly be attributed to CodeCompass's context rather than to the task
  prompt's own framing.

## Would this have misled the implementing agent? no (both drafts)

Neither packet contained an incorrect or misleading claim. Both correctly
and accurately described `balance_from_spec`'s real `any()`-based,
count-once-per-section matching behavior, grounded at the correct file and
(functionally, if not literally-pinned) line/revision. Both engineers used
their packet appropriately — as a pointer to verify, not an authority to
trust blindly — and both reached the same correct, independently-verified
conclusion (no extra dedup/aggregation logic needed in
`with_combined_section`), confirmed by my own independent re-run of the
pinned 11-method acceptance suite against both implementations (11/11 pass,
both) and the full regression suite (957/958 pass, no regressions). The
context-advantage is rated LOW for both, honestly: a fresh, diligent Claude
session given this same task — which itself names `balance_from_spec` as
"the one real call site" and (per both reports) already states the design
answer in its own prose — would very plausibly have reached the identical
correct conclusion from a single read of a ~100-line function, with or
without either context packet.
