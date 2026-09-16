---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger-lib/Hledger/Query.hs
lines: [1008, 1024]
content_hash: sha256:0ede176e2e7172ffdb2a557e1890ffdb248cf3c13c0beea77295c96c2a70126b
extracted_at: 2026-09-16T00:15:19.080425+00:00
---

# tag-query-pattern-match

patternsMatchTags/matchesTag — the actual regex-against-(name,value)-pairs matching logic every Tag case above delegates to.

Excerpt from `hledger-lib/Hledger/Query.hs:1008-1024`
at `hledger` commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

```
patternsMatchTags :: Regexp -> Maybe Regexp -> [Tag] -> Bool
patternsMatchTags namepat valuepat = any (matches namepat valuepat)
  where
    matches npat vpat (n,v) = regexMatchText npat n && maybe (const True) regexMatchText vpat v

-- | Does the query match the name and optionally the value of this tag ?
-- Non-tag: query terms are ignored (this might disrupt some boolean queries).
matchesTag :: Query -> Tag -> Bool
matchesTag (Not q)          t = not $ q `matchesTag` t
matchesTag (Any)            _ = True
matchesTag (None)           _ = False
matchesTag (Or qs)          t = any (`matchesTag` t) $ filter queryIsTag qs
matchesTag (And qs)         t = all (`matchesTag` t) $ filter queryIsTag qs
matchesTag (AnyPosting qs)  t = all (`matchesTag` t) $ filter queryIsTag qs
matchesTag (AllPostings qs) t = all1 (`matchesTag` t) $ filter queryIsTag qs
matchesTag (Tag npat mvpat) t = patternsMatchTags npat mvpat [t]
matchesTag _                _ = False
```
