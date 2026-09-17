---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger-lib/Hledger/Reports/PostingsReport.hs
lines: [166, 176]
content_hash: sha256:268ad3fc1dd020849d9026b7878a327996b8e403e1b2474937a178f95c802946
extracted_at: 2026-09-17T17:33:57.615509+00:00
---

# postingsreport-hs-b

An excerpt of Hledger/Reports/PostingsReport.hs.

Excerpt from `hledger-lib/Hledger/Reports/PostingsReport.hs:166-176`
at `hledger` commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

```
      -- want to keep prices around, so we can toggle between cost and no cost quickly. We can use
      -- the show_costs_ flag to be efficient when we can, and detailed when we have to.
      . (if show_costs_ ropts then id else journalMapPostingAmounts mixedAmountStripCosts)
      $ journalValueAndFilterPostings rspec{_rsQuery=beforeandduringq} j

    -- filter postings by the query, with no start date or depth limit
    beforeandduringq = dbg4 "beforeandduringq" $ And [depthless $ dateless q, beforeendq]
      where
        depthless  = filterQuery (not . queryIsDepth)
        dateless   = filterQuery (not . queryIsDateOrDate2)
        beforeendq = dateqtype $ DateSpan Nothing (Exact <$> spanEnd reportspan)
```
