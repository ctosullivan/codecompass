{-# LANGUAGE OverloadedStrings #-}

-- | Entry point: wires the generic protocol loop ("Adapter.Protocol")
-- to this ecosystem's own real analysis logic (dependency tree via
-- @stack@, API surface via the export-list scanner). Never imported by
-- CodeCompass -- runs only as an independent subprocess.
module Main (main) where

import Adapter.Deps (DepsResult (..), buildDependencyTree)
import Adapter.Manifest (moduleNameToPath, readPackageVersion, resolveExposedModules)
import Adapter.Protocol (AnalysisError (..), runServer)
import Adapter.Scanner (ScanDiagnostic (..), SymbolEntry (..), scanModule)
import Control.Monad (filterM)
import Data.Aeson (Value, object, (.=))
import qualified Data.Set as Set
import qualified Data.Text as T
import System.Directory (doesDirectoryExist, doesFileExist)
import System.FilePath ((</>))

main :: IO ()
main = runServer analyzeProject

analyzeProject :: FilePath -> String -> IO (Either AnalysisError Value)
analyzeProject projectRoot packageName = do
  rootExists <- doesDirectoryExist projectRoot
  if not rootExists
    then
      return
        (Left (AnalysisError "not_found" ("project_root does not exist: " <> T.pack projectRoot)))
    else do
      depsOutcome <- buildDependencyTree projectRoot packageName
      case depsOutcome of
        Left err -> return (Left (AnalysisError "internal_error" (T.pack err)))
        Right deps -> do
          (symbols, scanDiagnostics) <- scanExposedModules projectRoot packageName
          let observations =
                [ observation
                    "executable"
                    ("ran 'stack dot --external " ++ packageName ++ "'")
                    "stack"
                    (depsRawDot deps)
                , observation
                    "executable"
                    ("ran 'stack ls dependencies --external " ++ packageName ++ "'")
                    "stack"
                    (depsRawLsDependencies deps)
                ]
          return $
            Right $
              object
                [ "dependencies" .= depsTree deps
                , "symbols" .= map symbolToJSON symbols
                , "observations" .= observations
                , "diagnostics" .= map diagnosticToJSON scanDiagnostics
                ]

observation :: String -> String -> String -> String -> Value
observation method whatWasDone tool rawResult =
  object
    [ "method" .= method
    , "what_was_done" .= whatWasDone
    , "location" .= (Nothing :: Maybe String)
    , "raw_result" .= rawResult
    , "tool" .= tool
    , "tool_version" .= (Nothing :: Maybe String)
    ]

symbolToJSON :: SymbolEntry -> Value
symbolToJSON s =
  object
    [ "name" .= symName s
    , "purpose" .= symPurpose s
    , "module" .= symModule s
    , "kind" .= symKind s
    , "note" .= symNote s
    ]

diagnosticToJSON :: ScanDiagnostic -> Value
diagnosticToJSON d = object ["severity" .= diagSeverity d, "message" .= diagMessage d]

-- | REQ-HSAPI-004: resolve the package's own exposed-module set first,
-- then scan only those files -- a module outside this set contributes
-- no symbols regardless of its own export list.
scanExposedModules :: FilePath -> String -> IO ([SymbolEntry], [ScanDiagnostic])
scanExposedModules projectRoot packageName = do
  exposed <- resolveExposedModules projectRoot packageName
  _ <- readPackageVersion projectRoot -- kept for parity with a real manifest read; version itself comes from `stack ls dependencies` (Adapter.Deps)
  results <- mapM (scanOneModule projectRoot) (Set.toList exposed)
  let (symbolLists, diagLists) = unzip results
  return (concat symbolLists, concat diagLists)

scanOneModule :: FilePath -> String -> IO ([SymbolEntry], [ScanDiagnostic])
scanOneModule projectRoot moduleName = do
  let candidates = [projectRoot </> moduleNameToPath moduleName]
  existing <- filterM doesFileExist candidates
  case existing of
    (path : _) -> scanModule moduleName path
    [] ->
      return
        ( []
        , [ScanDiagnostic "warning" (moduleName ++ ": exposed module's source file not found")]
        )
