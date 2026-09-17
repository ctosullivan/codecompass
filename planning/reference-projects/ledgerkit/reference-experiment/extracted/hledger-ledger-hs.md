---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger-lib/Hledger/Data/Ledger.hs
lines: [54, 67]
content_hash: sha256:61b83bf2f8407bd32dcc8c184b9dafc83cc72f5533a22b042a1f00af529aaf1f
extracted_at: 2026-09-17T17:33:57.615509+00:00
---

# ledger-hs

An excerpt of Hledger/Data/Ledger.hs.

Excerpt from `hledger-lib/Hledger/Data/Ledger.hs:54-67`
at `hledger` commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

```
-- | Filter a journal's transactions with the given query, then build
-- a "Ledger", containing the journal plus the tree of all its
-- accounts with their subaccount-inclusive and subaccount-exclusive
-- balances. If the query includes a depth limit, the ledger's journal
-- will be depth limited, but the ledger's account tree will not.
ledgerFromJournal :: Query -> Journal -> Ledger
ledgerFromJournal q j = nullledger{ljournal=j'', laccounts=as}
  where
    (q',depthq)  = (filterQuery (not . queryIsDepth) q, filterQuery queryIsDepth q)
    j'  = filterJournalAmounts (filterQuery queryIsSym q) $ -- remove amount parts which the query's sym: terms would exclude
          filterJournalPostings q' j
    -- Ledger does not use date-separated balances, so dates are left empty
    as  = accountsFromPostings (const $ Just nulldate) $ journalPostings j'
    j'' = filterJournalPostings depthq j'
```
