# Conformance test vectors

This directory contains message fixtures, not an executable test
harness — the protocol repository ships schemas and documentation only,
in no particular programming language, so it never bundles a
language-specific validator.

- [`manifest.json`](manifest.json) lists every vector, which schema it
  must be checked against, and whether a correct implementation should
  find it `"valid"` or `"invalid"`.
- [`valid/`](valid/) holds messages that must pass validation against
  their listed schema.
- [`invalid/`](invalid/) holds messages that must be **rejected** by
  their listed schema — each one deliberately breaks exactly one rule
  (a missing required field, a value outside a closed enum, a response
  carrying both `result` and `error`, a message using the wrong
  `method`, an error code outside the closed set).

## How to use this from your own implementation

Load `manifest.json`, and for each entry, run your language's own JSON
Schema validator (draft 2020-12) with `schemas/<schema>` against
`conformance/<vector>`, and confirm the validator's verdict matches
`expect`. For example, in Python:

```python
import json
from pathlib import Path
from jsonschema import Draft202012Validator

root = Path(__file__).parent
manifest = json.loads((root / "manifest.json").read_text())
for entry in manifest["vectors"]:
    schema = json.loads((root / entry["schema"]).read_text())
    instance = json.loads((root / entry["vector"]).read_text())
    errors = list(Draft202012Validator(schema).iter_errors(instance))
    is_valid = not errors
    assert is_valid == (entry["expect"] == "valid"), entry
```

Any language with an off-the-shelf JSON Schema validator can run the
equivalent loop. This is what `codecompass-adaptor-haskell`'s own CI
does (using a small script, not a shipped part of the adapter itself),
and what CodeCompass's own test suite does from the Python side.
