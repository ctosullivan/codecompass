-- | Minimal, mechanical reads of a Haskell package's own manifest
-- files (@package.yaml@, and the hpack-generated @<name>.cabal@) --
-- never a general YAML\/Cabal parser, matching this adapter's own
-- "small, mechanical, no full parser" scope (mirrors, on the Haskell
-- side, why CodeCompass's own Python side uses real @PyYAML@ for its
-- own, differently-scoped needs -- decisions\/0057).
module Adapter.Manifest
  ( readPackageVersion
  , resolveExposedModules
  , moduleNameToPath
  ) where

import Control.Monad (forM)
import Data.Char (isSpace)
import Data.List (dropWhileEnd, isPrefixOf, isSuffixOf, stripPrefix)
import qualified Data.Set as Set
import System.Directory (doesDirectoryExist, doesFileExist, listDirectory)
import System.FilePath (takeExtension, (</>))

trim :: String -> String
trim = dropWhileEnd isSpace . dropWhile isSpace

-- | @package.yaml@'s own top-level @version:@ scalar. A trivial,
-- single-field read -- not a YAML parser -- since this is the one
-- field the adapter needs that CodeCompass's own Python-side
-- 'HaskellAdapter' does not already resolve and pass down (it is
-- needed here only to label the dependency tree's own root node).
readPackageVersion :: FilePath -> IO (Maybe String)
readPackageVersion projectRoot = do
  let manifest = projectRoot </> "package.yaml"
  exists <- doesFileExist manifest
  if not exists
    then return Nothing
    else do
      contents <- readFile manifest
      return (firstFieldValue "version" contents)

firstFieldValue :: String -> String -> Maybe String
firstFieldValue field contents =
  case filter (isPrefixOf (field ++ ":") . trim) (lines contents) of
    (line : _) ->
      let afterColon = drop 1 (dropWhile (/= ':') (trim line))
       in Just (trim afterColon)
    [] -> Nothing

-- | The package's own exposed-module set (REQ-HSAPI-004): a module not
-- in this set contributes no symbols, regardless of its own export
-- list. Prefers the hpack-generated @<name>.cabal@'s own already-
-- computed @exposed-modules:@ list (the most reliable real source,
-- since hpack has already resolved its own default rules) and falls
-- back to the hpack default itself (every @.hs@ file under
-- @source-dirs@, minus @other-modules@) when no @.cabal@ file is
-- present yet.
resolveExposedModules :: FilePath -> String -> IO (Set.Set String)
resolveExposedModules projectRoot packageName = do
  let cabalPath = projectRoot </> (packageName ++ ".cabal")
  cabalExists <- doesFileExist cabalPath
  if cabalExists
    then do
      contents <- readFile cabalPath
      return (Set.fromList (exposedModulesFromCabal contents))
    else hpackDefaultExposedModules projectRoot

-- | Parses a generated @.cabal@ file's @library@ stanza's
-- @exposed-modules:@ list: one dotted module name per line, indented
-- more deeply than the @exposed-modules:@ line itself, terminated by a
-- line indented no more deeply (a blank line, or the next field).
exposedModulesFromCabal :: String -> [String]
exposedModulesFromCabal contents =
  case dropWhile (not . isExposedModulesLine) (lines contents) of
    [] -> []
    (keyLine : rest) ->
      let keyIndent = indentOf keyLine
       in [ trim l
          | l <- takeWhile (\l -> not (null (trim l)) && indentOf l > keyIndent) rest
          , not (null (trim l))
          ]
  where
    isExposedModulesLine l = trim l == "exposed-modules:" || "exposed-modules:" `isPrefixOf` trim l
    indentOf l = length (takeWhile isSpace l)

-- | hpack's own default when @package.yaml@ states no explicit
-- @exposed-modules:@: every @.hs@ file under the library's
-- @source-dirs@ (default @src@, but @source-dirs: .@ is common for
-- small packages -- read directly from @package.yaml@, not assumed),
-- minus @other-modules@, minus files that are never real exposed
-- modules regardless (@Setup.hs@, build-generated @Paths_*@\/
-- @PackageInfo_*@ modules, and anything under a hidden or
-- @.stack-work@ directory).
hpackDefaultExposedModules :: FilePath -> IO (Set.Set String)
hpackDefaultExposedModules projectRoot = do
  manifestExists <- doesFileExist (projectRoot </> "package.yaml")
  sourceDirs <-
    if manifestExists
      then do
        contents <- readFile (projectRoot </> "package.yaml")
        return (sourceDirsFromPackageYaml contents)
      else return ["."]
  otherModules <-
    if manifestExists
      then otherModulesFromPackageYaml <$> readFile (projectRoot </> "package.yaml")
      else return []
  files <- concat <$> mapM (findHaskellFiles projectRoot) sourceDirs
  let names = [f | Just f <- map (pathToModuleName) files]
  return (Set.fromList names Set.\\ Set.fromList otherModules)

-- | A real @source-dirs:@ value can be a single scalar (@source-dirs:
-- .@) or a YAML list (@source-dirs:\n- src@) -- both real, observed
-- shapes; defaults to @["src"]@ (hpack's own default) if the key is
-- absent entirely.
sourceDirsFromPackageYaml :: String -> [String]
sourceDirsFromPackageYaml contents =
  case firstFieldValue "source-dirs" contents of
    Just scalar | not (null scalar) -> [scalar]
    _ ->
      case dropWhile (not . isKeyLine) (lines contents) of
        [] -> ["src"]
        (keyLine : rest) ->
          let keyIndent = indentOf keyLine
              items = takeWhile (\l -> not (null (trim l)) && indentOf l >= keyIndent) rest
           in case [drop 1 (trim l) | l <- items, "-" `isPrefixOf` trim l] of
                [] -> ["src"]
                xs -> map trim xs
  where
    isKeyLine l = trim l == "source-dirs:"
    indentOf l = length (takeWhile isSpace l)

otherModulesFromPackageYaml :: String -> [String]
otherModulesFromPackageYaml contents =
  case dropWhile (not . isKeyLine) (lines contents) of
    [] -> []
    (keyLine : rest) ->
      let keyIndent = length (takeWhile isSpace keyLine)
          items =
            takeWhile (\l -> not (null (trim l)) && length (takeWhile isSpace l) >= keyIndent) rest
       in [drop 1 (trim l) | l <- items, "-" `isPrefixOf` trim l]
  where
    isKeyLine l = trim l == "other-modules:"

findHaskellFiles :: FilePath -> FilePath -> IO [FilePath]
findHaskellFiles projectRoot relDir = do
  let dir = projectRoot </> relDir
  exists <- doesDirectoryExist dir
  if not exists
    then return []
    else do
      entries <- listDirectory dir
      let visible = filter (\e -> not ("." `isPrefixOf` e) && e /= "dist-newstyle") entries
      results <- forM visible $ \entry -> do
        let full = dir </> entry
        isDir <- doesDirectoryExist full
        if isDir
          then findHaskellFiles projectRoot (relDir </> entry)
          else
            return
              [ relDir </> entry
              | takeExtension entry == ".hs"
              , entry /= "Setup.hs"
              , not ("Paths_" `isPrefixOf` entry)
              , not ("PackageInfo_" `isPrefixOf` entry)
              ]
      return (concat results)

-- | @src/Foo/Bar.hs@ (relative to a source-dir) -> @Foo.Bar@. The
-- inverse of 'moduleNameToPath'.
pathToModuleName :: FilePath -> Maybe String
pathToModuleName path =
  let noExt = if ".hs" `isSuffixOf` path then take (length path - 3) path else path
      normalized = map (\c -> if c == '/' then '.' else c) noExt
      cleaned = case stripPrefix "." normalized of
        Just rest -> rest
        Nothing -> normalized
   in if null cleaned then Nothing else Just cleaned

-- | @Foo.Bar@ -> candidate relative paths (tried against every real
-- @source-dirs@ entry by the caller): @Foo\/Bar.hs@.
moduleNameToPath :: String -> FilePath
moduleNameToPath name = map (\c -> if c == '.' then '/' else c) name ++ ".hs"
