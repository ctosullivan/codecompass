-- Real excerpt (trimmed) from hledger-lib's own
-- Hledger/Data/AccountName.hs, GPL-3.0-or-later, (c) Simon Michael and
-- contributors: https://github.com/simonmichael/hledger
-- Used here, under the same license, as a real-world test fixture for
-- REQ-HSAPI-001 (baseline export-list scan) and REQ-HSAPI-006
-- (purpose-pairing by body location, not export-list order).
{-# LANGUAGE NoMonomorphismRestriction #-}
{-# LANGUAGE OverloadedStrings #-}
{-|

'AccountName's are strings like @assets:cash:petty@, with multiple
components separated by ':'.  From a set of these we derive the account
hierarchy.

-}

module Hledger.Data.AccountName (
   accountLeafName
  ,accountNameComponents
  ,accountNameFromComponents
  ,accountSummarisedName
  ,isAccountNamePrefixOf
--  ,isAccountRegex
  ,isSubAccountNameOf
  ,tests_AccountName
)
where

import Data.Text (Text)
import qualified Data.Text as T

-- accountNameComponents :: AccountName -> [String]
-- accountNameComponents = splitAtElement acctsepchar

accountNameComponents :: Text -> [Text]
accountNameComponents = T.splitOn ":"

accountNameFromComponents :: [Text] -> Text
accountNameFromComponents = T.intercalate ":"

accountLeafName :: Text -> Text
accountLeafName = last . accountNameComponents

-- | Truncate all account name components but the last to two characters.
accountSummarisedName :: Text -> Text
accountSummarisedName a = a

isAccountNamePrefixOf :: Text -> Text -> Bool
isAccountNamePrefixOf p a = p == a

isSubAccountNameOf :: Text -> Text -> Bool
isSubAccountNameOf s p = s == p

tests_AccountName :: [Bool]
tests_AccountName = []
