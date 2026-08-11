# 0018. `promote` is the sole reactive depth-escalation and cost-disclosure point

## Status

Accepted

## Context

With `decisions/0017` making bootstrap free and universal, and with
`depth = FULL` carrying real cost (an AI call — see `decisions/0019` for
what that call actually does), the project needs a single, explicit,
deliberate point where a user or agent opts into that cost for one
specific dependency. Today, escalating a vendor to `FULL` means
hand-editing `vendor.toml`'s `depth` field directly and re-running
`sync` — there is no command that names the action, discloses cost
before spending it, or bundles the full set of things "getting more from
this dependency" actually requires: source resolution, grounded
generation, Skill export, Cursor `.mdc` export, and refreshing the root
routing table so the change is visible immediately. `architecture/
overview.md`'s "Retrofitting to existing projects" section already
states the reactive-promotion principle ("promotion to `FULL` happen[s]
selectively and reactively later") but no command implements it as a
first-class action today.

Separately, `planning/ROADMAP.md` currently plans Phase 9 ("Agent Skills
export + Cursor `.mdc` export," `decisions/0013`) and Phase 10 (`init`
bulk-discovery refinement) as their own later phases. `decisions/0017`
already subsumes Phase 10's scope. This decision subsumes Phase 9's
*trigger point*: Skill/`.mdc` generation moves from "a separate phase
run at some point across every `FULL` vendor" to "part of what `promote`
does for the one vendor being promoted, at the moment it's promoted."

## Decision

1. New `depcompass promote <vendor>` command. Before doing anything
   AI-assisted, it prints a cost disclosure (model, estimated call
   count/cost) and requires confirmation (or a `--yes` flag for
   scripted/non-interactive use).
2. On confirmation, `promote`: (a) sets that vendor's `depth = FULL` in
   `vendor.toml`; (b) resolves the vendor's real source location per
   `decisions/0021`; (c) generates `FULL`-depth grounded content per
   `decisions/0019`; (d) generates that vendor's per-vendor Skill
   (`decisions/0013`) and Cursor `.mdc` export; (e) re-runs `index` so
   the root `CLAUDE.md` routing table reflects the change immediately.
3. `promote` is idempotent on an already-`FULL` vendor: re-running it
   regenerates that vendor's `FULL` content (same disclosure, same
   confirmation) rather than erroring — an explicit, on-demand refresh
   path distinct from `check --fix`, which regenerates because of
   detected staleness rather than a deliberate request.
4. `promote` is the only command in the system that costs money or
   requires confirmation. `sync` never escalates depth on its own; it
   only regenerates content for vendors already at their configured
   depth.
5. This supersedes the scope of `planning/ROADMAP.md`'s Phase 9 (Skills
   + `.mdc` export moves into `promote`) and Phase 10 (subsumed by
   `decisions/0017`). See `planning/ROADMAP.md` for the resulting
   renumbering and `planning/phase-7-bootstrap-and-promote.md` for the
   implementation.

## Alternatives considered

- **Keep depth escalation as a `vendor.toml` hand-edit + `sync`, with no
  dedicated command.** Rejected — this is the status quo friction this
  decision exists to fix: no cost disclosure, no bundling of the
  follow-on steps, easy to forget one of them (e.g. `.mdc` export left
  stale after a manual `depth` edit).
- **Let `sync` itself detect a `depth` change in `vendor.toml` and
  perform the escalation implicitly.** Rejected — reintroduces the
  "hidden cost, no disclosure" problem `promote` exists to prevent; a
  user hand-editing `depth` and then running an apparently-routine
  `sync` could trigger real spend with no confirmation step.
- **Batch promotion** (a `--all` or multi-vendor form). Deferred, not
  rejected — out of scope for the initial command. The reactive-
  promotion principle is specifically about single-vendor, on-demand
  escalation; a careless batch form could undermine "asks nothing until
  something is actually needed." Revisit only if real usage shows a
  recurring need.

## Consequences

- `vendor.toml`'s schema gains no new required fields from this decision
  alone — `promote` is purely an orchestration command over existing
  config mutation and generation primitives; `context_path`'s fate is
  decided separately in `decisions/0019`.
- `sync_vendor`'s contract stays unchanged: "regenerate content at
  whatever depth `vendor.toml` already says." It must not itself perform
  depth escalation or the Skill/`.mdc`/index steps `promote` owns.
- `planning/phase-7-bootstrap-and-promote.md` inherits `decisions/0013`'s
  unfinished requirements (trigger-description tuning, `references/`
  bundling, a trigger-accuracy evaluation step) since Skill generation's
  actual implementation now happens here rather than in a dedicated
  later phase.
- `check --fix` (`decisions/0005`, Phase 6) is unaffected — it continues
  to call `sync_vendor` directly for vendors already at `FULL`; it does
  not go through `promote`, since staleness-driven regeneration isn't a
  depth escalation and doesn't need its own fresh cost-disclosure/
  confirmation gate (the original `promote` call already disclosed and
  confirmed that vendor's ongoing regeneration cost).
