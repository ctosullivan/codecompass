---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger-lib/Hledger/Query.hs
lines: [868, 878]
content_hash: sha256:8c1f13a296dd71b34dd4068813a356978dc47ff0f46bcfc089a94e1386fb8456
extracted_at: 2026-09-17T17:33:57.615509+00:00
---

# query-hs-matchesaccount

matchesAccount, Hledger/Query.hs, in full.

Excerpt from `hledger-lib/Hledger/Query.hs:868-878`
at `hledger` commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

```
matchesAccount :: Query -> AccountName -> Bool
matchesAccount (None) _ = False
matchesAccount (Not m) a = not $ matchesAccount m a
matchesAccount (Or ms) a = any (`matchesAccount` a) ms
matchesAccount (And ms) a = all (`matchesAccount` a) ms
matchesAccount (AnyPosting  qs) a = all (`matchesAccount` a) qs
matchesAccount (AllPostings qs) a = all1 (`matchesAccount` a) qs
matchesAccount (Acct r) a = regexMatchText r a
matchesAccount (Depth d) a = accountNameLevel a <= d
matchesAccount (DepthAcct r d) a = accountNameLevel a <= d || not (regexMatchText r a)
matchesAccount (Tag _ _) _ = False
```
