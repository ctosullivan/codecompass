-- Synthetic fixture (this repository's own, not copied from hledger) for
-- REQ-HSAPI-005: a module with no export list at all -- every top-level
-- name is exported, but this version does not enumerate them.
module NoExportList where

answer :: Int
answer = 42
