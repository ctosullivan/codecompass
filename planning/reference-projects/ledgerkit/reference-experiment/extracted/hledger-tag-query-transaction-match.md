---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger-lib/Hledger/Query.hs
lines: [949, 972]
content_hash: sha256:63823a7b56a7379a26608f7320987b2bc05db135aa9e0dfbc2888997f357f992
extracted_at: 2026-09-16T00:15:19.080425+00:00
---

# tag-query-transaction-match

matchesTransaction in full — its Tag case (line 968-972) mirrors matchesPosting's payee/note special-case, else patternsMatchTags against transactionAllTags.

Excerpt from `hledger-lib/Hledger/Query.hs:949-972`
at `hledger` commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

```
matchesTransaction :: Query -> Transaction -> Bool
matchesTransaction (Not q) t = not $ q `matchesTransaction` t
matchesTransaction (Any) _ = True
matchesTransaction (None) _ = False
matchesTransaction (Or qs) t = any (`matchesTransaction` t) qs
matchesTransaction (And qs) t = all (`matchesTransaction` t) qs
matchesTransaction (AnyPosting  qs) t = any (\p -> all (`matchesPosting` p) qs) $ tpostings t
matchesTransaction (AllPostings qs) t = all1 (\p -> all (`matchesPosting` p) qs) $ tpostings t
matchesTransaction (Code r) t = regexMatchText r $ tcode t
matchesTransaction (Desc r) t = regexMatchText r $ tdescription t
matchesTransaction q@(Acct _) t = any (q `matchesPosting`) $ tpostings t
matchesTransaction (Date spn) t = spanContainsDate spn $ tdate t
matchesTransaction (Date2 spn) t = spanContainsDate spn $ transactionDate2 t
matchesTransaction (StatusQ s) t = tstatus t == s
matchesTransaction (Real v) t = v == hasRealPostings t
matchesTransaction q@(Amt _ _) t = any (q `matchesPosting`) $ tpostings t
matchesTransaction q@(Depth _) t = any (q `matchesPosting`) $ tpostings t
matchesTransaction q@(DepthAcct _ _) t = any (q `matchesPosting`) $ tpostings t
matchesTransaction q@(Sym _) t = any (q `matchesPosting`) $ tpostings t
matchesTransaction (Tag n v) t = case (reString n, v) of
  ("payee", Just v') -> regexMatchText v' $ transactionPayee t
  ("note", Just v') -> regexMatchText v' $ transactionNote t
  (_, v') -> patternsMatchTags n v' $ transactionAllTags t
matchesTransaction (Type _) _ = False
```
