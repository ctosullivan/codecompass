---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger-lib/Hledger/Reports/MultiBalanceReport.hs
lines: [205, 215]
content_hash: sha256:dbce4ac0f38901656610193a7b5234d58b3c48aa0c20948238be1b0796eef08d
extracted_at: 2026-09-17T17:33:57.615509+00:00
---

# multibalancereport-hs-a

An excerpt of Hledger/Reports/MultiBalanceReport.hs.

Excerpt from `hledger-lib/Hledger/Reports/MultiBalanceReport.hs:205-215`
at `hledger` commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

```
    fullreportq = dbg3 "getPostings fullreportq" $ And [datelessq, fullreportspanq]
    datelessq   = dbg3 "getPostings datelessq" $ filterQuery (not . queryIsDateOrDate2) depthlessq

    -- The user's query with no depth limit, and expanded to the report span
    -- if there is one (otherwise any date queries are left as-is, which
    -- handles the hledger-ui+future txns case above).
    depthlessq = dbg3 "getPostings depthlessq" $ filterQuery (not . queryIsDepth) query

    fullreportspan  = if requiresHistorical ropts then DateSpan Nothing (Exact <$> spanEnd reportspan) else reportspan
    fullreportspanq = (if date2_ ropts then Date2 else Date) $ case fullreportspan of
        DateSpan Nothing Nothing -> emptydatespan
```
