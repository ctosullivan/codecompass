{-# LANGUAGE OverloadedStrings #-}

import Adapter.Deps (buildTreeFromOutputs)
import Adapter.Scanner
  ( ScanDiagnostic (..)
  , SymbolEntry (..)
  , scanModule
  )
import Data.Aeson (Value (..))
import qualified Data.Aeson.KeyMap as KM
import Data.List (find, sort)
import Test.Hspec

fixture :: FilePath -> FilePath
fixture name = "test/fixtures/" ++ name

byName :: String -> [SymbolEntry] -> Maybe SymbolEntry
byName n = find ((== n) . symName)

main :: IO ()
main = hspec $ do
  describe "Adapter.Scanner (REQ-HSAPI-001, real hledger-lib excerpt)" $ do
    it "produces exactly the exported-name set, excluding the commented-out entry" $ do
      (symbols, diagnostics) <- scanModule "Hledger.Data.AccountName" (fixture "AccountName.hs")
      diagnostics `shouldBe` []
      sort (map symName symbols)
        `shouldBe` sort
          [ "accountLeafName"
          , "accountNameComponents"
          , "accountNameFromComponents"
          , "accountSummarisedName"
          , "isAccountNamePrefixOf"
          , "isSubAccountNameOf"
          , "tests_AccountName"
          ]
      symName <$> byName "isAccountRegex" symbols `shouldBe` Nothing

    it "labels every baseline entry 'export', never 'reexport'/'undetermined'" $ do
      (symbols, _) <- scanModule "Hledger.Data.AccountName" (fixture "AccountName.hs")
      all ((== "export") . symKind) symbols `shouldBe` True

  describe "Adapter.Scanner (REQ-HSAPI-006, purpose-pairing by body location)" $ do
    it "gives a name with a real preceding '-- | ...' comment its own real purpose" $ do
      (symbols, _) <- scanModule "Hledger.Data.AccountName" (fixture "AccountName.hs")
      symPurpose <$> byName "accountSummarisedName" symbols
        `shouldBe` Just (Just "Truncate all account name components but the last to two characters.")

    it "gives a name with no preceding comment purpose:null, not a scan failure" $ do
      (symbols, _) <- scanModule "Hledger.Data.AccountName" (fixture "AccountName.hs")
      symPurpose <$> byName "accountLeafName" symbols `shouldBe` Just Nothing
      symPurpose <$> byName "accountNameComponents" symbols `shouldBe` Just Nothing

  describe "Adapter.Scanner (REQ-HSAPI-001, Type(..) expansion)" $ do
    it "records the bare type name for a Type(..) entry" $ do
      (symbols, _) <- scanModule "TypeAllCtors" (fixture "TypeAllCtors.hs")
      sort (map symName symbols) `shouldBe` sort ["Query", "runQuery"]
      symPurpose <$> byName "runQuery" symbols
        `shouldBe` Just (Just "Run a query against nothing in particular.")

  describe "Adapter.Scanner (REQ-HSAPI-002, module <Name> re-export, real hledger-lib excerpt)" $ do
    it "records a self re-export and flags a CPP-gated entry as undetermined" $ do
      (symbols, _) <- scanModule "Hledger.Data.Types" (fixture "Types.hs")
      case byName "Hledger.Data.Types" symbols of
        Just entry -> do
          symKind entry `shouldBe` "reexport"
          symNote entry `shouldBe` Just "self re-export (this module's own export surface)"
        Nothing -> expectationFailure "expected a self re-export entry"
      case byName "Year" symbols of
        Just entry -> symKind entry `shouldBe` "undetermined"
        Nothing -> expectationFailure "expected the CPP-gated 'Year' entry to still be recorded"

    it "resolves a file-local 'import ... as X' alias to the real modules it covers" $ do
      (symbols, _) <- scanModule "Hledger" (fixture "Hledger.hs")
      case byName "X" symbols of
        Just entry -> do
          symKind entry `shouldBe` "reexport"
          symNote entry
            `shouldBe` Just
              "alias for Hledger.Utils, Hledger.Query, Hledger.Reports, Hledger.Read, Hledger.Data"
        Nothing -> expectationFailure "expected a resolved 'X' re-export entry"

  describe "Adapter.Scanner (REQ-HSAPI-005, no export list)" $ do
    it "detects the no-export-list case and reports zero symbols plus a diagnostic" $ do
      (symbols, diagnostics) <- scanModule "NoExportList" (fixture "NoExportList.hs")
      symbols `shouldBe` []
      map diagSeverity diagnostics `shouldBe` ["warning"]

  describe "Adapter.Deps (real stack dot / stack ls dependencies output)" $ do
    it "builds a DepNode tree with a cycle guard, from recorded real-shaped text" $ do
      -- Not a live `stack` invocation (no toolchain assumed in every CI
      -- environment) -- exercises the same parsing functions directly
      -- against text shaped exactly like real `stack dot --external`/
      -- `stack ls dependencies --external` output (recorded live against
      -- the real hledger-lib package during Phase 60's own development).
      let dot =
            unlines
              [ "strict digraph deps {"
              , "\"hledger-lib\" [style=dashed];"
              , "\"hledger-lib\" -> \"aeson\";"
              , "\"aeson\" -> \"base\";"
              , "}"
              ]
          ls = unlines ["aeson 2.2.5.1", "base 4.19.0.0", "hledger-lib 1.52.4"]
          tree = buildTreeFromOutputs dot ls "hledger-lib"
      lookupField "name" tree `shouldBe` Just (String "hledger-lib")
      lookupField "version" tree `shouldBe` Just (String "1.52.4")

    it "attaches a child's own version and guards against infinite recursion on a cycle" $ do
      -- NOT deduplicated, mirroring the Cargo adapter's own precedent
      -- (architecture/overview.md: "diamond dependencies appear in
      -- full, repeated, exactly as the underlying tool reports them"):
      -- a -> b -> a appears once at each real depth: b's own children
      -- still list "a" (a real edge), but that nested "a" node's own
      -- children stop (an empty array), preventing infinite recursion
      -- rather than pretending the repeated edge doesn't exist.
      let dot = unlines ["\"a\" -> \"b\";", "\"b\" -> \"a\";"]
          ls = unlines ["a 1.0", "b 2.0"]
          tree = buildTreeFromOutputs dot ls "a"
      case lookupField "children" tree of
        Just (Array cs) -> case toListOf cs of
          (childB : _) -> do
            lookupField "name" childB `shouldBe` Just (String "b")
            lookupField "version" childB `shouldBe` Just (String "2.0")
            case lookupField "children" childB of
              Just (Array grandchildren) -> case toListOf grandchildren of
                (nestedA : _) -> do
                  lookupField "name" nestedA `shouldBe` Just (String "a")
                  lookupField "children" nestedA `shouldBe` Just (Array mempty)
                [] -> expectationFailure "expected the repeated 'a' edge to still appear once"
              _ -> expectationFailure "expected a children array"
          [] -> expectationFailure "expected at least one child"
        _ -> expectationFailure "expected a children array"
  where
    lookupField k (Object o) = KM.lookup k o
    lookupField _ _ = Nothing
    toListOf = foldr (:) []
