---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger-lib/Hledger/Data/Dates.hs
lines: [1132, 1148]
content_hash: sha256:3edd1888479398b2a7a822febd4ae7327440b5c3325bdba7f4174fc57d5f98c9
extracted_at: 2026-09-16T00:15:19.080425+00:00
---

# date-query-span-double

doubledatespanp, exclusive end date — cited by LK-COMPAT-QUERY-DATE-001.yaml's evidence.ref.

Excerpt from `hledger-lib/Hledger/Data/Dates.hs:1132-1148`
at `hledger` commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

```
-- >>> parsewith (doubledatespanp (fromGregorian 2018 01 01) <* eof) "20180101-201804"
-- Right DateSpan 2018Q1
-- >>> parsewith (doubledatespanp (fromGregorian 2018 01 01) <* eof) "2017..2018"
-- Right DateSpan 2017
-- >>> parsewith (doubledatespanp (fromGregorian 2018 01 01) <* eof) "2017-2018"
-- Right DateSpan 2017
-- >>> parsewith (doubledatespanp (fromGregorian 2018 01 01) <* eof) "2017-01-2018"
-- Right DateSpan 2017
-- >>> parsewith (doubledatespanp (fromGregorian 2018 01 01) <* eof) "2017-01-01-2018"
-- Right DateSpan 2017
doubledatespanp :: Day -> TextParser m DateSpan
doubledatespanp rdate = liftA2 fromToSpan
    (optional ((string' "from" <|> string' "since") *> skipNonNewlineSpaces) *> smartdateorquarterstartp rdate)
    (skipNonNewlineSpaces *> choice [string' "to", string "..", string "-"]
    *> skipNonNewlineSpaces *> smartdateorquarterstartp rdate)
  where
    fromToSpan = DateSpan `on` (Just . fixSmartDate rdate)
```
