---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger-lib/Hledger/Reports/PostingsReport.hs
lines: [66, 75]
content_hash: sha256:05954972f3f46b4aeb200ac9295a5b293bbf107b873a1c09d109c5250465675b
extracted_at: 2026-09-17T17:33:57.615509+00:00
---

# postingsreport-hs-a

An excerpt of Hledger/Reports/PostingsReport.hs.

Excerpt from `hledger-lib/Hledger/Reports/PostingsReport.hs:66-75`
at `hledger` commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

```

-- | Select postings from the journal and add running balance and other
-- information to make a postings report. Used by eg hledger's register command.
postingsReport :: ReportSpec -> Journal -> PostingsReport
postingsReport rspec@ReportSpec{_rsReportOpts=ropts@ReportOpts{..}} j = items
    where
      (reportspan, colspans) = reportSpanBothDates j rspec
      whichdate   = whichDate ropts
      depthSpec   = queryDepth $ _rsQuery rspec
      multiperiod = interval_ /= NoInterval
```
