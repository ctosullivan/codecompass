{-# LANGUAGE OverloadedStrings #-}

-- | Dependency-tree construction via real @stack@ subprocess calls.
-- @stack ls dependencies@ has no JSON output mode (confirmed live,
-- codecompass's own decisions\/0057); @stack dot --external@'s real
-- GraphViz DOT output is the tree-structure source instead, combined
-- with @stack ls dependencies@'s flat name->version map to label each
-- node. Both commands take an explicit @TARGET@ (the package name) --
-- without it, a package inside a multi-package Stack project (a
-- monorepo like @hledger@) reports the *whole project's* dependency
-- graph, not the one target package's own closure (confirmed live
-- against the real @hledger@\/@hledger-lib@ checkout).
module Adapter.Deps
  ( DepsResult (..)
  , buildDependencyTree
  , buildTreeFromOutputs
  ) where

import Control.Exception (SomeException, try)
import Data.Aeson (Value, object, (.=))
import qualified Data.Map.Strict as Map
import Data.Map.Strict (Map)
import Data.Maybe (fromMaybe)
import System.Exit (ExitCode (..))
import System.Process (CreateProcess (cwd), proc, readCreateProcessWithExitCode)

data DepsResult = DepsResult
  { depsTree :: Value
  , depsRawDot :: String
  , depsRawLsDependencies :: String
  }

-- | Runs @stack dot --external <package>@ and
-- @stack ls dependencies --external <package>@ inside 'projectRoot',
-- and builds the neutral wire @DepNode@-shaped tree rooted at
-- 'packageName'. @dev_only@ is always @False@ -- neither command
-- exposes a per-edge dev/build-only distinction the way @cargo
-- metadata@ does; a real, disclosed limitation (mirrors the existing
-- Python-side npm\/Cargo adapters' own honestly-disclosed gaps), not an
-- oversight.
buildDependencyTree :: FilePath -> String -> IO (Either String DepsResult)
buildDependencyTree projectRoot packageName = do
  dotOutcome <- runStack projectRoot ["dot", "--external", packageName]
  case dotOutcome of
    Left err -> return (Left err)
    Right dotOutput -> do
      lsOutcome <- runStack projectRoot ["ls", "dependencies", "--external", packageName]
      case lsOutcome of
        Left err -> return (Left err)
        Right lsOutput ->
          return
            (Right (DepsResult (buildTreeFromOutputs dotOutput lsOutput packageName) dotOutput lsOutput))

-- | Pure core, exposed separately so tests can exercise it directly
-- against recorded real-shaped text (`decisions/0014`'s
-- fixture-based-primary-strategy posture, applied on the Haskell side)
-- without needing a live `stack` subprocess.
buildTreeFromOutputs :: String -> String -> String -> Value
buildTreeFromOutputs dotOutput lsOutput packageName =
  buildNode (parseDotEdges dotOutput) (parseLsDependencies lsOutput) [] packageName

runStack :: FilePath -> [String] -> IO (Either String String)
runStack projectRoot args = do
  outcome <-
    try (readCreateProcessWithExitCode (proc "stack" args) {cwd = Just projectRoot} "") ::
      IO (Either SomeException (ExitCode, String, String))
  return $ case outcome of
    Left e -> Left ("failed to run 'stack " ++ unwords args ++ "': " ++ show e)
    Right (ExitSuccess, out, _) -> Right out
    Right (ExitFailure code, _, err) ->
      Left ("'stack " ++ unwords args ++ "' failed (exit " ++ show code ++ "): " ++ err)

-- | Parses @"A" -> "B";@ edge lines from real @stack dot@ output into a
-- @name -> [child names]@ adjacency map. Every other line (dashed
-- project-package declarations, box/rank styling groups) is ignored.
parseDotEdges :: String -> Map String [String]
parseDotEdges = foldr addEdge Map.empty . lines
  where
    addEdge line acc = case parseEdgeLine line of
      Just (from, to) -> Map.insertWith (++) from [to] acc
      Nothing -> acc

parseEdgeLine :: String -> Maybe (String, String)
parseEdgeLine line = do
  rest0 <- stripQuote line
  (from, rest1) <- breakOnQuote rest0
  rest2 <- stripArrow rest1
  rest3 <- stripQuote rest2
  (to, _) <- breakOnQuote rest3
  return (from, to)
  where
    stripQuote s = case dropWhile (== ' ') s of
      ('"' : xs) -> Just xs
      _ -> Nothing
    breakOnQuote s = case break (== '"') s of
      (name, '"' : rest) -> Just (name, rest)
      _ -> Nothing
    stripArrow s = case dropWhile (== ' ') s of
      ('-' : '>' : xs) -> Just xs
      _ -> Nothing

-- | Parses @stack ls dependencies@'s flat, plain-text @NAME VERSION@
-- lines (confirmed live: no JSON mode exists for this command).
parseLsDependencies :: String -> Map String String
parseLsDependencies output =
  Map.fromList
    [ (name, unwords rest)
    | line <- lines output
    , (name : rest) <- [words line]
    , not (null rest)
    ]

buildNode :: Map String [String] -> Map String String -> [String] -> String -> Value
buildNode adjacency versions visited name =
  object
    [ "name" .= name
    , "version" .= fromMaybe "unknown" (Map.lookup name versions)
    , "dev_only" .= False
    , "children" .= children
    ]
  where
    children
      | name `elem` visited = [] -- cycle guard, mirrors the Cargo adapter's own precedent
      | otherwise =
          [ buildNode adjacency versions (name : visited) child
          | child <- fromMaybe [] (Map.lookup name adjacency)
          ]
