---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger-lib/Hledger/Query.hs
lines: [902, 925]
content_hash: sha256:0a339ee6343f3e805329d8964998dff42755a88340901cd885e6538ecadaed3f
extracted_at: 2026-09-16T00:15:19.080425+00:00
---

# tag-query-posting-match

matchesPosting in full — its Tag case (line 921-924) special-cases 'payee'/'note' as synthetic tag names before falling back to patternsMatchTags against postingAllTags (inherited tags).

Excerpt from `hledger-lib/Hledger/Query.hs:902-925`
at `hledger` commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

```
matchesPosting :: Query -> Posting -> Bool
matchesPosting (Not q) p = not $ q `matchesPosting` p
matchesPosting (Any) _ = True
matchesPosting (None) _ = False
matchesPosting (Or qs) p = any (`matchesPosting` p) qs
matchesPosting (And qs) p = all (`matchesPosting` p) qs
matchesPosting (AnyPosting  qs) p = all (`matchesPosting` p) qs
matchesPosting (AllPostings qs) p = all1 (`matchesPosting` p) qs
matchesPosting (Code r) p = maybe False (regexMatchText r . tcode) $ ptransaction p
matchesPosting (Desc r) p = maybe False (regexMatchText r . tdescription) $ ptransaction p
matchesPosting (Acct r) p = matches p || maybe False matches (poriginal p) where matches = regexMatchText r . paccount
matchesPosting (Date spn) p = spn `spanContainsDate` postingDate p
matchesPosting (Date2 spn) p = spn `spanContainsDate` postingDate2 p
matchesPosting (StatusQ s) p = postingStatus p == s
matchesPosting (Real v) p = v == isReal p
matchesPosting q@(Depth _) Posting{paccount=a} = q `matchesAccount` a
matchesPosting q@(DepthAcct _ _) Posting{paccount=a} = q `matchesAccount` a
matchesPosting q@(Amt _ _) Posting{pamount=as} = q `matchesMixedAmount` as
matchesPosting (Sym r) Posting{pamount=as} = any (matchesCommodity (Sym r) . acommodity) $ amountsRaw as
matchesPosting (Tag n v) p = case (reString n, v) of
  ("payee", Just v') -> maybe False (regexMatchText v' . transactionPayee) $ ptransaction p
  ("note", Just v') -> maybe False (regexMatchText v' . transactionNote) $ ptransaction p
  (_, mv) -> patternsMatchTags n mv $ postingAllTags p
matchesPosting (Type _) _ = False
```
