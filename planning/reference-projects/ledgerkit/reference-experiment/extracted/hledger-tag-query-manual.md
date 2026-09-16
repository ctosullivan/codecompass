---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger/hledger.1
lines: [7372, 7394]
content_hash: sha256:4672d39a7d93eda90cb466b21d89ce1aba3bf8c79511976f6d59937fd9b0e64b
extracted_at: 2026-09-16T00:15:19.080425+00:00
---

# tag-query-manual

The '### tag: query' section — syntax, infix-matching rule, and the three inheritance rules (accounts from parents, postings from account+transaction, transactions from postings).

Excerpt from `hledger/hledger.1:7372-7394`
at `hledger` commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

```
.SS tag: query
\f[B]\f[CB]tag:NAMEREGEX[=VALREGEX]\f[B]\f[R]
.PD 0
.P
.PD
Match by tag name, and optionally also by tag value.
Note:
.IP \(bu 2
Both regular expressions do infix matching.
If you need a complete match, use \f[CR]\(ha\f[R] and \f[CR]$\f[R].
.PD 0
.P
.PD
Eg: \f[CR]tag:\(aq\(hafullname$\(aq\f[R],
\f[CR]tag:\(aq\(hafullname$=\(hafullvalue$\f[R]
.IP \(bu 2
To match values, ignoring names, do \f[CR]tag:.=VALREGEX\f[R]
.IP \(bu 2
Accounts also inherit the tags of their parent accounts.
.IP \(bu 2
Postings also inherit the tags of their account and their transaction .
.IP \(bu 2
Transactions also acquire the tags of their postings.
```
