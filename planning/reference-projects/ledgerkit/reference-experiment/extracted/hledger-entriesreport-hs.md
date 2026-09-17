---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger-lib/Hledger/Reports/EntriesReport.hs
lines: [1, 42]
content_hash: sha256:f3af5efa4671a88aac9deedf9e2fd512efcf47f89cc02584d991fcf3450ef288
extracted_at: 2026-09-17T17:33:57.615509+00:00
---

# entriesreport-hs

Hledger/Reports/EntriesReport.hs, in full.

Excerpt from `hledger-lib/Hledger/Reports/EntriesReport.hs:1-42`
at `hledger` commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

```
{-# LANGUAGE FlexibleInstances   #-}
{-# LANGUAGE OverloadedStrings   #-}
{-# LANGUAGE ScopedTypeVariables #-}
{-|

Journal entries report, used by the print command.

-}

module Hledger.Reports.EntriesReport (
  EntriesReport,
  EntriesReportItem,
  entriesReport,
  -- * Tests
  tests_EntriesReport
)
where

import Data.List (sortBy)
import Data.Ord (comparing)
import Data.Time (fromGregorian)

import Hledger.Data
import Hledger.Query (Query(..), filterQuery, queryIsDepth)
import Hledger.Reports.ReportOptions
import Hledger.Utils


-- | A journal entries report is a list of whole transactions as
-- originally entered in the journal (mostly). This is used by eg
-- hledger's print command and hledger-web's journal entries view.
type EntriesReport = [EntriesReportItem]
type EntriesReportItem = Transaction

-- | Select transactions for an entries report.
entriesReport :: ReportSpec -> Journal -> EntriesReport
entriesReport rspec@ReportSpec{_rsReportOpts=ropts} =
      sortBy (comparing $ transactionDateFn ropts)
    . map  (if invert_ ropts then transactionNegate else id)
    . jtxns
    . journalApplyValuationFromOpts (setDefaultConversionOp NoConversionOp rspec)
    . filterJournalTransactions (filterQuery (not.queryIsDepth) $ _rsQuery rspec)
```
