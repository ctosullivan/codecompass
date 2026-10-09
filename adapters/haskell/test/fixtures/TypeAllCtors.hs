-- Synthetic fixture (this repository's own) for the `Type(..)` shape
-- confirmed real in hledger-lib/Hledger/Query.hs's own `Query(..)` /
-- `OrdPlus(..)` / `QueryOpt(..)` entries (CL-HSAPI-001, EV-HSAPI-008).
module TypeAllCtors (
  Query(..)
 ,runQuery
)
where

data Query = MatchAll | MatchNone

-- | Run a query against nothing in particular.
runQuery :: Query -> Bool
runQuery _ = True
