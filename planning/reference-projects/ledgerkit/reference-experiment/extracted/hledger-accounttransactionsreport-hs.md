---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger-lib/Hledger/Reports/AccountTransactionsReport.hs
lines: [99, 108]
content_hash: sha256:46bfbd3376a3c2387625ad7d566ffdf8d250b5bcf25e3197f2cb564971eb3182
extracted_at: 2026-09-17T17:33:57.615509+00:00
---

# accounttransactionsreport-hs

An excerpt of Hledger/Reports/AccountTransactionsReport.hs.

Excerpt from `hledger-lib/Hledger/Reports/AccountTransactionsReport.hs:99-108`
at `hledger` commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

```
accountTransactionsReport rspec@ReportSpec{_rsReportOpts=ropts} j thisacctq = items
  where
    -- A depth limit should not affect the account transactions report; it should show all transactions in/below this account.
    -- Queries on currency or amount are also ignored at this stage; they are handled earlier, before valuation.
    reportq = simplifyQuery $ And [aregisterq, periodq]
      where
        aregisterq = filterQuery (not . queryIsCurOrAmt) . filterQuery (not . queryIsDepth) $ _rsQuery rspec
        periodq = Date . periodAsDateSpan $ period_ ropts
    amtq = filterQuery queryIsCurOrAmt $ _rsQuery rspec
    queryIsCurOrAmt q = queryIsSym q || queryIsAmt q
```
