# Cloning, building, and updating the Haskell adapter submodules

CodeCompass's Haskell adapter (Phase 60) is not shipped as part of this
repository. It's a separate, independent project
(`codecompass-adaptor-haskell`), checked out locally as a git submodule
alongside its protocol contract (`codecompass-adaptor-protocol`, also a
submodule). See [`architecture/overview.md`](../../architecture/overview.md)'s
"External adapters" section for why this exists and how the protocol
works; [`decisions/0057`](../../decisions/0057-external-process-adapter-protocol.md)
and
[`decisions/0058`](../../decisions/0058-adapter-protocol-and-haskell-adapter-as-separate-repositories.md)
for the full rationale. For the wire protocol itself, see
[`../protocol-adapter/wire-protocol.md`](../protocol-adapter/wire-protocol.md).

**Naming note**: the two real repositories are named
`codecompass-adaptor-protocol` and `codecompass-adaptor-haskell`
("adaptor" spelling — the account owner's own choice when creating
them). Earlier planning documents and ADRs (`decisions/0057`,
`decisions/0058`) were drafted before those repositories existed and use
"adapter" spelling throughout their prose — a spelling difference only,
not a naming error or a second, different pair of repositories.

## Cloning

A fresh clone needs `--recurse-submodules`:

```
git clone --recurse-submodules git@github.com:ctosullivan/codecompass.git
```

**If you already have an existing clone that predates this**, a plain
`git clone`/`git pull` leaves `protocol/codecompass-adaptor-protocol/`
and `adapters/haskell/` as **empty directories** — this is the single
most likely point of confusion for a contributor who hasn't seen a
submodule-based repository before. Fix it with:

```
git submodule update --init --recursive
```

## Building the adapter locally

Requires a working `stack` installation (the same toolchain that builds
`hledger` itself).

```
cd adapters/haskell
stack build
```

`HaskellAdapter` (`src/codecompass/adapters/haskell.py`) locates the
built executable itself via `stack path --local-install-root`, run
inside `adapters/haskell/` — there's no separate install step or PATH
configuration needed beyond `stack build` having succeeded once.

## Updating a submodule to a new release

Submodules are **not** edited from the parent repository. To move
`codecompass`'s own pin forward to a new protocol or adapter release:

```
cd protocol/codecompass-adaptor-protocol
git fetch --tags
git checkout <new-tag>
cd ../..
git add protocol/codecompass-adaptor-protocol
git commit -m "chore: bump codecompass-adaptor-protocol to <new-tag>"
```

The same pattern applies to `adapters/haskell/`. This commit records
only the new pinned commit SHA (a "gitlink") in `codecompass`'s own
history — never the submodule's own file content.

## Commit independence (a hard rule, not just a description)

- A change to the protocol's own schemas/docs/examples is a commit in
  `codecompass-adaptor-protocol`'s own history.
- A change to the adapter's own Haskell code is a commit in
  `codecompass-adaptor-haskell`'s own history.
- A change to CodeCompass core — including a submodule gitlink bump — is
  a commit in `codecompass`'s own history.

No single commit ever spans tracked content in more than one of these
three repositories.
