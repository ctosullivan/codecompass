-- Real excerpt (trimmed) from hledger-lib's own
-- Hledger/Data/Types.hs, GPL-3.0-or-later, (c) Simon Michael and
-- contributors: https://github.com/simonmichael/hledger
-- Used here, under the same license, as a real-world test fixture for
-- REQ-HSAPI-002 (self re-export) and REQ-HSAPI-003 (a CPP conditional
-- gating an export-list entry).
{-# LANGUAGE CPP #-}

module Hledger.Data.Types (
  module Hledger.Data.Types,
#if MIN_VERSION_time(1,11,0)
  Year
#endif
)
where

data Amount = Amount
