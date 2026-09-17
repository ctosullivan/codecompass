---
reference: hledger
source_url: https://github.com/simonmichael/hledger
requested_ref: 1.52.4
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
fetch_method: local_clone
path: hledger/Hledger/Cli/Commands/Accounts.hs
lines: [60, 112]
content_hash: sha256:86f18220833e0ac7e33b2211d61d64089eeb21a4b70c2987561c2e471ff301fd
extracted_at: 2026-09-17T17:33:57.615509+00:00
---

# accounts-hs

An excerpt of Hledger/Cli/Commands/Accounts.hs.

Excerpt from `hledger/Hledger/Cli/Commands/Accounts.hs:60-112`
at `hledger` commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

```
  let tree     = tree_ ropts
      directives = boolopt "directives" rawopts
      locations = boolopt "locations" rawopts
      types = boolopt "types" rawopts
      -- Modified queries. These may not work with boolean queries (#2371).
      -- a depth limit will clip and exclude account names later, but we don't want to exclude accounts at this stage
      nodepthq = dbg4 "nodepthq" $ filterQuery (not . queryIsDepth) query
      -- just the acct: part of the query will be reapplied later, after clipping
      acctq = dbg4 "acctq" $ filterQuery queryIsAcct query
      dep = dbg4 "depth" $ queryDepth $ filterQuery queryIsDepth query
      -- when finding accounts used by postings, we remove tags that were declared on the posting,
      -- so that a tag: query will match account tags and not posting tags.
      matchedused = dbg5 "matchedused" $ nub $ map paccount $ journalPostings $
        filterJournalPostings nodepthq $ journalPostingsKeepAccountTagsOnly j
      matcheddeclared = dbg5 "matcheddeclared" $
        nub $
        filter (matchesAccountExtra (journalAccountType j) (journalInheritedAccountTags j) nodepthq) $
        map fst $ jdeclaredaccounts j
      matchedundeclared = dbg5 "matchedundeclared" $ nub $ matchedused \\ matcheddeclared
      matchedunused = dbg5 "matchedunused" $ nub $ matcheddeclared \\ matchedused
      found = dbg5 "matchedacct" $ findMatchedByArgument rawopts "account" $ journalAccountNamesDeclaredOrImplied j
      matchedall = matcheddeclared ++ matchedused
      accts = dbg5 "accts to show" $
        case declarablesSelectorFromOpts opts of
          Nothing         -> matchedall
          Just Used       -> matchedused
          Just Declared   -> matcheddeclared
          Just Undeclared -> matchedundeclared
          Just Unused     -> matchedunused
          Just Find       -> [found]

  -- 2. sort them by declaration order (then undeclared accounts alphabetically)
  -- within each group of siblings
      sortedaccts = sortAccountNamesByDeclaration j tree accts

  -- 2a. in tree mode, add parent accounts for tree structure context
      acctswithparents =
        if tree
        then dbg4 "acctswithparents" $
             sortAccountNamesByDeclaration j tree $  -- re-sort after adding parents
             expandAccountNames sortedaccts          -- add all parent accounts
        else sortedaccts

  -- 3. if there's a depth limit, depth-clip and remove any no longer useful items
      clippedaccts =
        dbg4 "clippedaccts" $
        (if tree then id else filter (matchesAccount acctq)) $  -- in tree mode, keep parent accounts even if they don't match
        nub $                            -- clipping can leave duplicates (adjacent, hopefully)
        filter (not . T.null) $          -- depth:0 can leave nulls
        map (clipAccountName dep) $      -- clip at depth if specified
        acctswithparents                 -- use expanded list instead of sortedaccts

  -- 4. print what remains as a list or tree, maybe applying --drop in the former case.
```
