---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger-lib/Hledger/Query.hs
lines: [482, 487]
content_hash: sha256:4b904471982a7b5d98f47775cb7abc4511244c6533c3ddac57b95bfde38ccd62
extracted_at: 2026-09-16T00:15:19.080425+00:00
---

# tag-query-parser

parseTag — splits tag:NAMEREGEX[=VALREGEX] on the first '=', compiles NAMEREGEX and (if present) VALREGEX as case-insensitive regexes.

Excerpt from `hledger-lib/Hledger/Query.hs:482-487`
at `hledger` commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

```
parseTag :: T.Text -> Either RegexError Query
parseTag s = do
    tag <- toRegexCI $ if T.null v then s else n
    body <- if T.null v then pure Nothing else Just <$> toRegexCI (T.tail v)
    return $ Tag tag body
  where (n,v) = T.break (=='=') s
```
