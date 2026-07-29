# SUPER FRGMNTS Overnight Audit Progress

**Audit date:** 2026-07-29

**Working branch:** `audit/overnight-full-review`

**Starting commit:** `eb0cf56b` (`Ship Super Frgmnts Beta 2 stabilization`)

## Phase 0 — Safety and repository preparation

**Status:** Complete

- Read the canonical `Design/Super-Frgmnts/SUPER-FRGMNTS-HANDOFF.md` first.
- Read the repository and SUPER FRGMNTS README files, active platform baseline,
  release manifest, production-run contract, unified Level 1 plan, and current
  Shard Foundry level-design contract.
- Confirmed that the canonical runtime is the static, single-file
  `super_frgmnts.html`; there is no game-specific package manifest, lockfile,
  bundler, typechecker, linter, or JavaScript test-runner configuration.
- Confirmed that validation is provided by 42
  `tools/verify_super_frgmnts_*.py` contract scripts plus inline-JavaScript
  syntax checking and browser review.
- Starting repository state was clean on `main`, exactly tracking
  `origin/main`.
- Created the isolated local branch `audit/overnight-full-review`.
- No pre-existing user work was present or modified.
- No deployment, publication, remote write, asset rewrite, or production
  change has been performed.

## Phase 1 — Architecture and runtime map

**Status:** Complete

Initial confirmed map:

- Entry point and runtime: `super_frgmnts.html` (982 KiB, 25,225 lines).
- Rendering: one 1,672 × 941 logical HTML Canvas 2D surface with nearest-neighbor
  pixel-art presentation and responsive CSS sizing.
- Runtime organization: one strict-mode inline JavaScript IIFE; scenes are
  configured in-page from query parameters without navigation or page reload.
- Primary scenes: title, arrival bridge, four-plate Overworld, RD-42 interior,
  eight-plate Shard Foundry, Foundry-to-Wound bridge, The Wound boss room, and
  post-Wound surface return.
- Simulation/render driver: a single `requestAnimationFrame` loop through
  `frame(now)`, `update(delta)`, and `draw()`.
- Input: shared action state driven by keyboard and pointer/touch controls;
  controller Start is implemented for the boss-announcement skip only.
- Audio: two persistent HTML audio music channels for crossfades, one lazily
  created Web Audio context for synthesized tones, and per-effect reusable
  HTML audio channel pools.
- Assets: scene-keyed image definitions with critical-load failure UI,
  prefetching, room-local Foundry lower-plate retention, and explicit inactive
  scene release.
- Persistence confirmed so far: local storage for sound preference and session
  storage for Episode 01 credits. No general continue-game/save slot has been
  found.
- Collision and physics: elapsed-time integration with a 33 ms delta cap,
  horizontal acceleration/friction, gravity, coyote time, jump buffering,
  one-way platform top-crossing tests, explicit drop-through exclusion, and
  room-bounded Deepworks floors.
- Damage lifecycle: five-hit health, 1.15-second desktop invulnerability,
  authored airborne/grounded death resolution, and scene-specific retry reset.
- Scene lifecycle: `configureEpisodeScene()` rebuilds world geometry and
  population in place; image groups are requested/released by scene, while
  all global event listeners and the animation loop are installed once.
- Save/continue behavior: no save-slot or Continue Game UI exists. The only
  persisted gameplay value is Episode 01 credits in session storage, plus the
  sound preference in local storage. Continue-game valid/invalid-save cases
  are therefore not implemented features in this beta.

## Phase 2 — Baseline

**Status:** Complete

Environment and commands:

- `python3 --version` → Python 3.14.3.
- `node --version` could not run from the normal shell because `node` is not on
  `PATH`. The bundled Node 24.14.0 runtime was used for syntax validation.
- `for test in tools/verify_super_frgmnts_*.py; do python3 "$test" || exit 1;
  done` → all 42 contracts passed in 3.12 seconds.
- Inline JavaScript piped to bundled `node --check` → passed.
- `git diff --check` → passed.
- There is no dependency install, development/production bundler, separate
  production build, typecheck, lint, unit-test runner, integration-test
  runner, or browser-test runner for this static game.

Baseline artifact/load facts:

- `super_frgmnts.html`: 1,006,053 bytes raw; 144,901 bytes at gzip level 9.
- Inline JavaScript: 902,830 bytes.
- 119 unique image/audio references; all 119 exist with exact case.
- All referenced images/audio: 70,881,596 encoded bytes.
- All referenced images if simultaneously resident: approximately 202,681,174
  decoded bytes, though scene release prevents that normal state.
- Expected portability exceptions only: the two documented 2,816 × 184
  Vesperite strips are the sole referenced images above 2,048 pixels.
- Direct scene image groups: Foundry 14,258,494 encoded bytes / approximately
  52.3 MB decoded; Overworld 13,653,303 / 49.0 MB; Wound 12,394,078 / 67.7 MB;
  isolated interior 16,065,728 / 59.1 MB.

Cold public-entry observation on a new local origin:

- HTML `load` plus a 1.2-second observation window completed in 1,397 ms.
- The server observed requests for the HTML, both desktop and portrait title
  paintings, boss-announcement title, two control icons, arrival painting,
  and title audio: 10,700,803 local bytes before fonts/favicon.
- The 2,486,472-byte portrait title and 78,963-byte boss title were requested
  on a 1,280 × 720 desktop viewport even though neither was usable there.
- The canonical entry produced two uncaught `drawHazards()` exceptions because
  legacy pre-title hazard records have no `id`. The first exception terminated
  the only animation loop. Starting Episode 01 then configured and drew the
  Overworld once, but telemetry remained unchanged afterward, confirming a
  public-entry hard lock.
- Direct Foundry, Overworld, Wound, and RD-42 routes did not reproduce that
  exception.

## Phase 3 — Gameplay and reliability playtest

**Status:** Complete

Completed so far:

- Public title load, explicit audio handshake, and Begin Episode action.
- All eight Foundry plate QA entry points across Foundry, Refinery, Biolab, and
  Uplink: correct grounded spawn, 16-enemy population, two authored hazards,
  one required route lock, and no console warnings/errors.
- Foundry pause/resume: timer stayed at 01:30 for 1.3 seconds while paused and
  resumed decrementing afterward.
- Twenty Foundry restart cycles: every sampled reset restored 08:00, 16
  enemies, two hazards, one canvas, and two music elements with no console
  errors.
- Twenty deterministic death→Retry cycles: every sampled cycle ended on the
  loss screen with one canvas and two music elements. Firing while lost did
  not escape the loss state.
- Ten full Wound specimen-recovery→surface-return transitions: all ten reached
  the canonical returned-Overworld URL with stored material.
- Simultaneous fatal damage plus a fully satisfied Uplink objective:
  deterministic QA route remained in Foundry death state and did not begin the
  Wound transition.
- Wound safe bay, threshold approach through real touch input, complete
  announcement/combat flow, 50 direct rifle hits, boss death, corpse
  aftermath, delayed specimen reveal, proximity recovery, black surface
  return, sealed transport, all 31 Dras report cards, Chapter One cliffhanger,
  and stable completed state.
- Arrival dialogue skip confirmation: both Keep Listening and Skip Scene
  branches behaved correctly.
- Coreworks transport: activation, Start Over, and Enter Foundry branches
  behaved correctly.
- RD-42: production art, suit change, flight-suit jump, armor-gated hatch,
  reverse re-arm, service-kit recovery, and exterior re-emergence all passed
  without console errors.
- The connected browser could not supply a true portrait viewport or native
  window focus/background transfer. Those cases are explicitly partial in the
  playtest matrix.

## Phase 4 — Performance audit

**Status:** Complete

- Wound idle construction telemetry changed 222 times over 3,002 ms
  (approximately 74 observable updates/second; median 14 ms, p95 20 ms,
  maximum 29 ms). This is a lower-bound rendering-cadence proxy because the
  available browser API does not expose a native performance trace or heap
  profiler.
- No duplicate canvas or audio elements appeared across 20 resets.
- Reliable JS heap measurement is unavailable in the connected browser; scene
  group decoded-size estimates, retained DOM nodes, collection sizes, and
  repeated-cycle telemetry are being used as memory proxies.
- Final isolated Wound telemetry changed 352 times over 3,000 ms (median
  10 ms, p95 12 ms, maximum 17 ms). Seventeen completed test tabs were parked
  before this sample, so it demonstrates no final regression but is not a
  controlled optimization comparison.
- Final fresh-origin desktop entry requested 8,142,642 local bytes before
  fonts/favicon, down 2,558,161 bytes or 23.91%. The portrait title and Wound
  boss title no longer load on the desktop title route.
- Final HTML is 1,013,327 raw bytes and 145,907 bytes at gzip level 9.

## Phase 5 — Fixes and regression coverage

**Status:** Complete

- P0 fixed: optional hazard telemetry IDs no longer terminate the renderer and
  only animation loop.
- P2 fixed: Uplink completion now requires the current state to remain
  `running`, preventing a fatal-hit/completion race.
- P2 fixed: focus is now an explicit simulation lifecycle gate with frame-time
  reset on every interruption/resume path.
- P2 fixed: responsive title art is selected at runtime and the Wound
  announcement title is assigned only on Wound routes.
- Added `tools/verify_super_frgmnts_runtime_reliability.py`.
- Added Episode-only `qa=death` and `qa=completion-collision` seams for
  deterministic browser regression.
- Created commit `bd6669d7` (`audit: harden runtime reliability`).

## Phase 6 — Final verification and reports

**Status:** Complete

- All 43 `tools/verify_super_frgmnts_*.py` contracts passed in 3.43 seconds
  after the regenerative retry follow-up.
- Inline JavaScript passed bundled Node 24.14.0 syntax checking.
- `git diff --check` passed.
- Browser retest passed the canonical title→Arrival route, death cycles,
  fatal-damage/completion ordering, title request selection, Wound art
  selection, and surface-return repetition.
- Completed:
  - `docs/audit/OVERNIGHT_AUDIT.md`
  - `docs/audit/PERFORMANCE_REPORT.md`
  - `docs/audit/PLAYTEST_MATRIX.md`
- No deployment, publication, push, production service change, asset rewrite,
  or external communication occurred.

## Approved follow-up — Regenerative Wound retry

**Status:** Implemented

- Product decision: a failed Wound attempt is a regenerative checkpoint, not
  a player-condition save state.
- Retry returns Aryn to the safe bay with five hearts.
- Score, mission time, Signal Shards, Galactic Credits, optional Vesperite,
  jet assist, heavy rifle, and seeker tier still restore from the Uplink
  checkpoint.
- Boss state, projectiles, heat, invulnerability, and temporary combat state
  continue to reset through the existing encounter reset.
- Added deterministic `qa=retry` browser coverage with a damaged checkpoint
  and forced fatal hit.
- Browser result: Retry restored five hearts, the 06:00 checkpoint clock,
  score 2400, the rifle, and a 50-health Seam Hunter while retaining the
  checkpoint's one-hit marker as evidence that health regenerated rather than
  restoring the snapshot.
