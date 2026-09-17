---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger/hledger.1
lines: [7054, 7098]
content_hash: sha256:9135b2cd44f0f5505a84da7275b445ee0552c6de1aa7a405418f4d370bd8b1d8
extracted_at: 2026-09-17T17:33:57.615509+00:00
---

# depth-manual-section

The manual's '.SH Depth' section, in full.

Excerpt from `hledger/hledger.1:7054-7098`
at `hledger` commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

```
.SH Depth
With the \f[CR]\-\-depth NUM\f[R] option (short form, usually preferred:
\f[CR]\-NUM\f[R]), reports will show accounts only to the specified
depth, hiding deeper subaccounts.
Use this when you want a summary with less detail.
This flag has the same effect as a \f[CR]depth:\f[R] query argument.
So all of these are equivalent: \f[CR]depth:2\f[R],
\f[CR]\-\-depth=2\f[R], \f[CR]\-2\f[R].
.PP
You can also provide custom depths for specific accounts, by providing a
\f[CR]REGEX=NUM\f[R] argument instead of just \f[CR]NUM\f[R] \f[I](since
1.41)\f[R].
For example, \f[CR]\-\-depth assets=2\f[R] (or
\f[CR]depth:assets=2\f[R]) will collapse accounts matching the regular
expression \(dqassets\(dq to depth 2.
So \f[CR]assets:bank:savings\f[R] would be collapsed to
\f[CR]assets:bank\f[R], but \f[CR]liabilities:bank:credit card\f[R]
would not be affected.
.PP
If REGEX contains spaces or other special characters, enclose it in
quotes in the usual way.
Eg: \f[CR]\-\-depth \(aqcredit card=2\(aq\f[R]
.SS Combining depth options
If a command line contains multiple general depth options, the last one
wins.
(Useful for overriding a depth specified by scripts.)
.PP
Or a command may contain a combination of general and custom depth
options.
In this case, the most specifically (deepest) matching option wins.
Some examples:
.IP \(bu 2
\f[CR]\-\-depth assets=3 \-\-depth expenses=2 \-\-depth 1\f[R] would
collapse accounts containing \(dqassets\(dq to depth 3, accounts
containing \(dqexpenses\(dq to depth 2, and all other accounts to depth
1.
.IP \(bu 2
\f[CR]\-\-depth assets=1 \-\-depth savings=2\f[R] would collapse
\f[CR]assets:bank:savings\f[R] to depth 2 (not depth 1; because
\(dqsavings\(dq matches a deeper part of the account name than
\(dqassets\(dq).
.PP
Note currently, to override a custom depth option
\f[CR]\-\-depth REGEX=NUM\f[R] with a later option, the later option
must use the same REGEX.
```
