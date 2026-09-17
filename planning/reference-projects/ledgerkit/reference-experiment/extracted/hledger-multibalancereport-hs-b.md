---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger-lib/Hledger/Reports/MultiBalanceReport.hs
lines: [220, 238]
content_hash: sha256:efeb8719668b954db1205b1423b13e2719e1bf8c7c93dbeec1f182ffc6da4389
extracted_at: 2026-09-17T17:33:57.615509+00:00
---

# multibalancereport-hs-b

An excerpt of Hledger/Reports/MultiBalanceReport.hs.

Excerpt from `hledger-lib/Hledger/Reports/MultiBalanceReport.hs:220-238`
at `hledger` commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

```
generateMultiBalanceAccount :: ReportSpec -> Journal -> PriceOracle -> Maybe DayPartition -> [Posting] -> Account BalanceData
generateMultiBalanceAccount rspec@ReportSpec{_rsReportOpts=ropts} j priceoracle colspans =
    -- Set account declaration info (for sorting purposes)
    mapAccounts (accountSetDeclarationInfo j)
    -- Add declared accounts if called with --declared and --empty
    . (if (declared_ ropts && empty_ ropts) then addDeclaredAccounts rspec j else id)
    -- Negate amounts if applicable
    . (if invert_ ropts then fmap (mapBalanceData maNegate) else id)
    -- Mark which accounts are boring and which are interesting
    . markAccountBoring rspec
    -- Process changes into normal, cumulative, or historical amounts, plus value them
    . calculateReportAccount rspec j priceoracle colspans
    -- Clip account names
    . map clipPosting
  where
    -- Clip postings to the requested depth according to the query
    clipPosting p = p{paccount = clipOrEllipsifyAccountName depthSpec $ paccount p}
    depthSpec = dbg3 "generateMultiBalanceAccount depthSpec"
              . queryDepth . filterQuery queryIsDepth $ _rsQuery rspec
```
