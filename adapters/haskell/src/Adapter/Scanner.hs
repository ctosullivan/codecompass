-- | Mechanical, no-AI, no-full-parser Haskell export-list scanner --
-- this adapter's own analogue of CodeCompass's Rust adapter own
-- @extract_rust_symbols@ (@src\/codecompass\/symbols.py@), for a
-- visibility model governed by a module header's own export list
-- rather than a per-declaration keyword. Implements
-- REQ-HSAPI-001 through REQ-HSAPI-006
-- (@planning\/knowledge\/haskell-api-surface-extraction\/@ in the
-- codecompass repository), approved by @DEC-HSAPI-001@.
module Adapter.Scanner
  ( SymbolEntry (..)
  , ScanDiagnostic (..)
  , scanModule
  ) where

import Data.Char (isAlphaNum, isSpace)
import Data.List (findIndex, isPrefixOf, stripPrefix)
import qualified Data.Map.Strict as Map
import Data.Map.Strict (Map)

data SymbolEntry = SymbolEntry
  { symName :: String
  , symPurpose :: Maybe String
  , symModule :: String
  , symKind :: String -- "export" | "reexport" | "undetermined" (decisions/0059)
  , symNote :: Maybe String
  }
  deriving (Show, Eq)

data ScanDiagnostic = ScanDiagnostic
  { diagSeverity :: String
  , diagMessage :: String
  }
  deriving (Show, Eq)

trim :: String -> String
trim = f . f where f = reverse . dropWhile isSpace

-- | Scans one already-located @.hs@ file for the module named
-- 'moduleName''s own exported symbols. REQ-HSAPI-004 (the
-- package-level exposed-modules filter) is applied by the caller
-- *before* this function is ever called -- this function only ever
-- sees modules already known to be in the package's own exposed set.
scanModule :: String -> FilePath -> IO ([SymbolEntry], [ScanDiagnostic])
scanModule moduleName filePath = do
  raw <- readFile filePath
  let noBlock = stripBlockComments raw
      cleanedLines = map stripLineComment (lines noBlock)
      bodyLines = lines noBlock -- comments (incl. "-- | ...") preserved for pass 2
  case break (\l -> "module" `isPrefixOf` trim l) cleanedLines of
    (_, []) ->
      return
        ( []
        , [ScanDiagnostic "warning" (moduleName ++ ": no 'module' header line found; skipped")]
        )
    (_, modLine : restLines) ->
      let afterName = dropModuleNameAndKeyword modLine
          tagged = tagLines (afterName : restLines)
       in case scanForOpenParenOrWhere tagged of
            NoExportList ->
              return
                ( []
                , [ ScanDiagnostic
                      "warning"
                      ( moduleName
                          ++ ": no export list (every top-level name is exported); "
                          ++ "not enumerated in this version (REQ-HSAPI-005)"
                      )
                  ]
                )
            ExportListEntries rawEntries -> do
              let aliasMap = buildAliasMap (lines raw)
                  entries = map (classifyEntry moduleName aliasMap) rawEntries
                  symbols = map (attachPurpose bodyLines moduleName) entries
              return (symbols, [])

-- --- Comment stripping ----------------------------------------------

-- | Removes every @{- ... -}@ span (non-nested -- sufficient in
-- practice for real code; the same simplification the research's own
-- verified-sufficient prototype used, CL-HSAPI-001).
stripBlockComments :: String -> String
stripBlockComments [] = []
stripBlockComments ('{' : '-' : rest) = stripBlockComments (dropBlock rest)
  where
    dropBlock ('-' : '}' : xs) = xs
    dropBlock (_ : xs) = dropBlock xs
    dropBlock [] = []
stripBlockComments (c : rest) = c : stripBlockComments rest

-- | Truncates a line at its own @--@ line-comment marker, UNLESS the
-- line is a CPP directive (starts with @#@) -- those are preserved
-- verbatim so 'tagLines' can still recognise them.
stripLineComment :: String -> String
stripLineComment line
  | "#" `isPrefixOf` trim line = line
  | otherwise = go line
  where
    go [] = []
    go ('-' : '-' : _) = []
    go (c : cs) = c : go cs

-- --- CPP-aware character tagging --------------------------------------

-- | Flattens lines into a @(Char, insideCppGate)@ stream: a CPP
-- @#if@\/@#ifdef@\/@#ifndef@ line increments a depth counter, @#endif@
-- decrements it, and every character of every *other* line is tagged
-- with whether that counter was above zero at the time -- so an
-- export-list entry whose text was read while inside an
-- @#if@\/@#endif@ span can be identified later (REQ-HSAPI-003), without
-- a CPP directive line's own text (which can itself contain parens,
-- e.g. @#if MIN_VERSION_time(1,11,0)@) ever being scanned as Haskell
-- syntax.
tagLines :: [String] -> [(Char, Bool)]
tagLines = go (0 :: Int)
  where
    go _ [] = []
    go depth (l : ls)
      | isCppIf l = go (depth + 1) ls
      | isCppEndif l = go (max 0 (depth - 1)) ls
      | isCppOther l = go depth ls
      | otherwise = [(c, depth > 0) | c <- l ++ "\n"] ++ go depth ls
    isCppIf l = any (`isPrefixOf` trim l) ["#if", "#ifdef", "#ifndef"]
    isCppEndif l = "#endif" `isPrefixOf` trim l
    isCppOther l = case trim l of
      ('#' : _) -> True
      _ -> False

-- --- Module header / export-list span ---------------------------------

dropModuleNameAndKeyword :: String -> String
dropModuleNameAndKeyword l =
  let afterKeyword = trim (drop (length ("module" :: String)) (trim l))
      isNameChar c = isAlphaNum c || c `elem` ("._'" :: String)
      nameChars = takeWhile isNameChar afterKeyword
   in drop (length nameChars) afterKeyword

data RawEntry = RawEntry String Bool

data ScanOutcome = NoExportList | ExportListEntries [RawEntry]

scanForOpenParenOrWhere :: [(Char, Bool)] -> ScanOutcome
scanForOpenParenOrWhere = go
  where
    go cs =
      let cs1 = dropWhile (isSpace . fst) cs
       in case cs1 of
            (('(', _) : rest) -> ExportListEntries (splitEntries (collectSpan rest))
            [] -> NoExportList
            (_ : rest)
              | map fst (take 5 cs1) == "where" -> NoExportList
              | otherwise -> go rest

-- | Consumes characters (already past the opening paren, which starts
-- depth at 1) until the matching close paren, tracking nested depth so
-- e.g. @Type(..)@'s own inner parens don't end the span early.
collectSpan :: [(Char, Bool)] -> [(Char, Bool)]
collectSpan = go (1 :: Int)
  where
    go _ [] = []
    go depth ((c, cpp) : rest)
      | c == ')' = if depth == 1 then [] else (c, cpp) : go (depth - 1) rest
      | c == '(' = (c, cpp) : go (depth + 1) rest
      | otherwise = (c, cpp) : go depth rest

-- | Splits the span's content on top-level commas (depth 0 relative to
-- the span's own nested parens) into raw entries, recording whether
-- any character contributing to an entry was read while inside a CPP
-- gate.
splitEntries :: [(Char, Bool)] -> [RawEntry]
splitEntries = go (0 :: Int) [] False
  where
    flush buf sawCpp acc =
      let txt = trim (reverse buf)
       in if null txt then acc else RawEntry txt sawCpp : acc
    go _ buf sawCpp [] = reverse (flush buf sawCpp [])
    go depth buf sawCpp ((c, cpp) : rest)
      | c == ',' && depth == 0 = reverse (flush buf sawCpp []) ++ go 0 [] False rest
      | c == '(' = go (depth + 1) (c : buf) (sawCpp || cpp) rest
      | c == ')' = go (depth - 1) (c : buf) (sawCpp || cpp) rest
      | otherwise = go depth (c : buf) (sawCpp || cpp) rest

-- --- Classification (REQ-HSAPI-001/002/003) ----------------------------

classifyEntry :: String -> Map String [String] -> RawEntry -> SymbolEntry
classifyEntry currentModule aliasMap (RawEntry txt sawCpp)
  | sawCpp =
      SymbolEntry
        (headIdentifier txt)
        Nothing
        currentModule
        "undetermined"
        (Just "gated by a CPP conditional the adapter cannot evaluate (REQ-HSAPI-003)")
  | Just afterModuleWord <- stripModuleWord txt =
      let name = trim afterModuleWord
       in SymbolEntry name Nothing currentModule "reexport" (reexportNote currentModule aliasMap name)
  | otherwise = SymbolEntry (headIdentifier txt) Nothing currentModule "export" Nothing

headIdentifier :: String -> String
headIdentifier txt = trim (takeWhile (/= '(') txt)

stripModuleWord :: String -> Maybe String
stripModuleWord txt = case stripPrefix "module" (trim txt) of
  Just rest@(c : _) | isSpace c -> Just rest
  _ -> Nothing

reexportNote :: String -> Map String [String] -> String -> Maybe String
reexportNote currentModule aliasMap name
  | name == currentModule = Just "self re-export (this module's own export surface)"
  | Just mods <- Map.lookup name aliasMap = Just ("alias for " ++ joinComma mods)
  | otherwise = Nothing
  where
    joinComma [] = ""
    joinComma [x] = x
    joinComma (x : xs) = x ++ ", " ++ joinComma xs

-- | @import [qualified] Real.Module as Alias@ lines -> @Alias -> [Real.Module]@
-- (an alias can cover several real modules, e.g. hledger-lib's own
-- @Hledger.hs@ reusing @as X@ across five separate import lines).
buildAliasMap :: [String] -> Map String [String]
buildAliasMap ls =
  Map.fromListWith (++) [(alias, [m]) | l <- ls, Just (m, alias) <- [parseImportAs l]]

parseImportAs :: String -> Maybe (String, String)
parseImportAs line = case words (trim line) of
  ("import" : "qualified" : m : "as" : a : _) -> Just (m, a)
  ("import" : m : "as" : a : _) -> Just (m, a)
  _ -> Nothing

-- --- Purpose pairing (REQ-HSAPI-006) ------------------------------------

attachPurpose :: [String] -> String -> SymbolEntry -> SymbolEntry
attachPurpose bodyLines _ entry
  | symKind entry /= "export" = entry
  | otherwise = case findIndex (isDefinitionLine (symName entry)) bodyLines of
      Nothing -> entry
      Just i -> entry {symPurpose = purposeAbove bodyLines i}

isDefinitionLine :: String -> String -> Bool
isDefinitionLine name line = case words (trim line) of
  (n : "::" : _) -> n == name
  (kw : n : _) | kw `elem` (["data", "newtype", "type", "class"] :: [String]) -> n == name
  (n : _) -> takeWhile (\c -> c `notElem` ("([{" :: String)) n == name
  [] -> False

purposeAbove :: [String] -> Int -> Maybe String
purposeAbove ls i
  | i <= 0 = Nothing
  | otherwise =
      let prev = trim (ls !! (i - 1))
       in case stripPrefix "-- |" prev of
            Just rest -> nonEmpty (trim rest)
            Nothing -> case stripPrefix "--|" prev of
              Just rest -> nonEmpty (trim rest)
              Nothing -> Nothing
  where
    nonEmpty t = if null t then Nothing else Just t
