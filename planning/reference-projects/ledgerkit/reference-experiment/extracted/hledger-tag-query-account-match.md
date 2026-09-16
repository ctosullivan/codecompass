---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger-lib/Hledger/Query.hs
lines: [889, 897]
content_hash: sha256:186a01def0a83afb6fb9330875dc82818d028bbf075459d7003b224388c57d89
extracted_at: 2026-09-16T00:15:19.080425+00:00
---

# tag-query-account-match

matchesAccountExtra's Tag case — matches an account's own inherited tag set (atags), the concrete mechanism behind the manual's 'accounts inherit the tags of their parent accounts' claim.

Excerpt from `hledger-lib/Hledger/Query.hs:889-897`
at `hledger` commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

```
matchesAccountExtra :: (AccountName -> Maybe AccountType) -> (AccountName -> [Tag]) -> Query -> AccountName -> Bool
matchesAccountExtra atypes atags (Not q  ) a = not $ matchesAccountExtra atypes atags q a
matchesAccountExtra atypes atags (Or  qs ) a = any (\q -> matchesAccountExtra atypes atags q a) qs
matchesAccountExtra atypes atags (And qs ) a = all (\q -> matchesAccountExtra atypes atags q a) qs
matchesAccountExtra atypes atags (AnyPosting  qs ) a = all (\q -> matchesAccountExtra atypes atags q a) qs
matchesAccountExtra atypes atags (AllPostings qs ) a = all1 (\q -> matchesAccountExtra atypes atags q a) qs
matchesAccountExtra atypes _     (Type ts) a = maybe False (\t -> any (t `isAccountSubtypeOf`) ts) $ atypes a
matchesAccountExtra _      atags (Tag npat vpat) a = patternsMatchTags npat vpat $ atags a
matchesAccountExtra _      _     q         a = matchesAccount q a
```
