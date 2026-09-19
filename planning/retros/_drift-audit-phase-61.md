# Docs drift audit — Phase 61

Independent, read-only, per-phase drift audit (`docs-reconstructor`),
2026-09-19. **Verdict: no drift found.**

## Scope

Phase 61's only `src/` change: `HaskellAdapter.repository_url()` now
sets `RepositoryLocation.subdirectory` for a monorepo member.

## Findings

1. **`docs/config-schema.md` / `repository_url()` / monorepo claims** —
   no doc in `docs/`, `README.md`, or `ai-docs/` describes
   `repository_url()`/`RepositoryLocation`/the Haskell adapter's
   monorepo `subdirectory` behaviour at all. `docs/config-schema.md`'s
   own "pinned source snapshot at `vendor/<name>/src/`" claim was true
   before and after this fix and never claimed that snapshot is scoped
   to a monorepo subpackage — not made stale.
2. **`architecture/overview.md`'s Haskell adapter section** (monorepo
   root resolution via `_resolve_package_dir()`) describes a distinct
   code path (local filesystem resolution) from `repository_url()`'s new
   `subdirectory` field (upstream-git-clone resolution) — remains
   accurate, unchanged.
3. **The two new "Known footguns" bullets independently re-verified**
   against real code (`source_resolution.py::resolve_and_clone`,
   `sync.py::sync_vendor`) and a real artifact
   (`ledgerkit-scratch-61/vendor/{hledger,hledger-lib}/src/`,
   byte-identical unscoped top-level listings; `FILETREE.md` correctly
   scoped) — both bullets confirmed accurate.
4. **`docs/external-adapters.md`** — no claim contradicted by this
   phase's findings.
5. **`context-quality-evaluation.md`'s new ground rule** — a
   methodology addition, not a current-truth system claim; doesn't
   contradict `architecture/`/`docs/`.

## Not in scope

`decisions/0057`/`0058` (append-only ADRs); the external
`codecompass-adaptor-haskell`/`codecompass-adaptor-protocol` repositories.
