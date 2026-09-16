---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger-lib/Hledger/Data/Dates.hs
lines: [429, 429]
content_hash: sha256:435044333c6c422f07924e85ec7d8edb878d16f5b15bd10a19ff2be1ae4e0b19
extracted_at: 2026-09-16T00:15:19.080425+00:00
---

# date-query-span-single

Single-date span construction — cited by LK-COMPAT-QUERY-DATE-001.yaml's evidence.ref.

Excerpt from `hledger-lib/Hledger/Data/Dates.hs:429-429`
at `hledger` commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

```
          span' (SmartCompleteDate day)       = (Exact day, Exact $ nextday day)
```
