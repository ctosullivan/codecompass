{-# LANGUAGE OverloadedStrings #-}

-- | JSON-Lines wire protocol handling: reads one request object per
-- line from stdin, dispatches @initialize@/@analyze_project@/
-- @shutdown@, writes one response object per line to stdout. Speaks
-- exactly the protocol codecompass-adaptor-protocol defines
-- (@SCHEMA.md@, @schemas\/*.json@) -- see decisions\/0057 and
-- decisions\/0058 in the codecompass repository. Zero CodeCompass-
-- specific or Haskell-analysis-specific knowledge lives here; that is
-- supplied by the caller via 'AnalyzeProject'.
module Adapter.Protocol
  ( runServer
  , AnalyzeProject
  , AnalysisError (..)
  , adapterName
  , adapterVersion
  , protocolVersion
  , ecosystemName
  ) where

import Control.Monad (unless)
import Data.Aeson (Value (..), (.=))
import qualified Data.Aeson as A
import qualified Data.Aeson.KeyMap as KM
import qualified Data.ByteString.Char8 as BS
import qualified Data.ByteString.Lazy.Char8 as BL
import qualified Data.Text as T
import System.IO

-- | The wire-level protocol version this adapter speaks. Distinct from
-- 'adapterVersion' (this repository's own semver release) --
-- decisions\/0058's own "what protocol_version is not" note.
protocolVersion :: Int
protocolVersion = 1

adapterName :: T.Text
adapterName = "codecompass-adaptor-haskell"

adapterVersion :: T.Text
adapterVersion = "0.1.0"

ecosystemName :: T.Text
ecosystemName = "haskell"

-- | A protocol-level error: one of the closed
-- @not_found@\/@parse_error@\/@unsupported_capability@\/@internal_error@
-- codes plus a human-readable message.
data AnalysisError = AnalysisError
  { errorCode :: T.Text
  , errorMessage :: T.Text
  }

-- | The caller-supplied analysis function: given the already-resolved
-- project root and target package name, produce either an error or the
-- neutral @result@ object for @analyze_project@.
type AnalyzeProject = FilePath -> String -> IO (Either AnalysisError Value)

-- | Read JSON-Lines requests from stdin until EOF, dispatch each one,
-- write JSON-Lines responses to stdout. Runs until stdin closes (the
-- host's own @shutdown@-then-close-stdin sequence, decisions\/0057).
runServer :: AnalyzeProject -> IO ()
runServer analyze = do
  hSetBuffering stdout LineBuffering
  hSetBinaryMode stdin False
  hSetEncoding stdin utf8
  hSetEncoding stdout utf8
  loop
  where
    loop = do
      eof <- isEOF
      unless eof $ do
        line <- BS.getLine
        handleLine analyze (BL.fromStrict line)
        loop

handleLine :: AnalyzeProject -> BL.ByteString -> IO ()
handleLine analyze raw = case A.decode raw of
  Just (Object obj) -> dispatch analyze obj
  _ -> return () -- malformed line, no id to reply to: drop silently

dispatch :: AnalyzeProject -> A.Object -> IO ()
dispatch analyze obj = case KM.lookup "id" obj of
  Nothing -> return () -- no id at all: nothing to correlate a reply to
  Just idVal -> case methodOf obj of
    Just "initialize" -> respondResult idVal initializeResult
    Just "analyze_project" -> handleAnalyzeProject analyze idVal (paramsOf obj)
    Just "shutdown" -> respondResult idVal (Object KM.empty)
    Just other ->
      respondError idVal "unsupported_capability" ("unknown method: " <> other)
    Nothing -> respondError idVal "internal_error" "missing or invalid 'method'"

methodOf :: A.Object -> Maybe T.Text
methodOf obj = case KM.lookup "method" obj of
  Just (String s) -> Just s
  _ -> Nothing

paramsOf :: A.Object -> A.Object
paramsOf obj = case KM.lookup "params" obj of
  Just (Object p) -> p
  _ -> KM.empty

handleAnalyzeProject :: AnalyzeProject -> Value -> A.Object -> IO ()
handleAnalyzeProject analyze idVal params =
  case (KM.lookup "project_root" params, KM.lookup "package_name" params) of
    (Just (String root), Just (String pkgName)) -> do
      outcome <- analyze (T.unpack root) (T.unpack pkgName)
      case outcome of
        Right result -> respondResult idVal result
        Left (AnalysisError code msg) -> respondError idVal code msg
    _ ->
      respondError
        idVal
        "parse_error"
        "analyze_project requires string 'project_root' and 'package_name' params"

initializeResult :: Value
initializeResult =
  A.object
    [ "protocol_version" .= protocolVersion
    , "adapter_name" .= adapterName
    , "adapter_version" .= adapterVersion
    , "ecosystem" .= ecosystemName
    , "capabilities" .= (["dependencies", "symbols", "observations", "diagnostics"] :: [T.Text])
    ]

respondResult :: Value -> Value -> IO ()
respondResult idVal result =
  BL.putStrLn (A.encode (A.object ["id" .= idVal, "result" .= result]))

respondError :: Value -> T.Text -> T.Text -> IO ()
respondError idVal code msg =
  BL.putStrLn
    (A.encode (A.object ["id" .= idVal, "error" .= A.object ["code" .= code, "message" .= msg]]))
