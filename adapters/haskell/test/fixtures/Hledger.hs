-- Real excerpt (trimmed) from hledger-lib's own Hledger.hs,
-- GPL-3.0-or-later, (c) Simon Michael and contributors:
-- https://github.com/simonmichael/hledger
-- Used here, under the same license, as a real-world test fixture for
-- REQ-HSAPI-002's aliased `module <Name>` case: `X` aliases five real
-- imports via `as X`, file-locally resolvable without a cross-file read.
module Hledger (
  module X
 ,tests_Hledger
)
where

import           Hledger.Data    as X
import           Hledger.Read    as X
import           Hledger.Reports as X
import           Hledger.Query   as X
import           Hledger.Utils   as X

tests_Hledger :: [Bool]
tests_Hledger = []
