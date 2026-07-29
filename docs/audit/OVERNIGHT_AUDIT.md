# SUPER FRGMNTS Overnight Audit

**Audit date:** 2026-07-29

**Branch:** `audit/overnight-full-review`

**Starting commit:** `eb0cf56b`

**Canonical reference:** `Design/Super-Frgmnts/SUPER-FRGMNTS-HANDOFF.md`

## Executive summary

The game is in substantially better condition than its public entry point
initially suggested. Direct review routes, scene data, art integration, combat,
the Wound conclusion, and the RD-42 interior were stable in extended play.
However, the canonical title URL had a P0 defect: its first render threw while
converting an optional hazard ID into a telemetry key. That exception ended
the only animation loop, so beginning Episode 01 produced a visually populated
but permanently frozen Overworld. The defect was reproduced, fixed with a
two-line guard, covered by a repository verifier, and retested through the
title-to-Arrival path.

Three P2 issues were also addressed. Completion can no longer override death
when both happen in one update; window focus loss now suspends simulation as
the lifecycle design requires; and the desktop title no longer downloads the
portrait title plus a Wound-only boss title. The latter removes 2,560,852
bytes, or 23.93%, from the observed local desktop cold-entry request set.

No P1 issue was found. Five P3 concerns remain deliberately deferred: the lack
of automated behavioral browser tests, the 25,336-line single-file runtime,
hot-loop allocations and DOM lookups without demonstrated frame instability,
one inaccurate pause-screen phrase, and the optional external font
dependency. There was no redesign, asset mutation, dependency change,
deployment, publication, or remote write.

## Finding count

| Severity | Found | Fixed | Deferred |
| --- | ---: | ---: | ---: |
| P0 | 1 | 1 | 0 |
| P1 | 0 | 0 | 0 |
| P2 | 3 | 3 | 0 |
| P3 | 5 | 0 | 5 |

## Repository and architecture overview

### Repository shape and entry point

- The canonical production game is the static `super_frgmnts.html`.
- There is no package manifest, lockfile, framework runtime, bundler,
  typechecker, linter, JavaScript unit runner, or browser test runner for this
  game.
- The final HTML is 1,010,636 raw bytes, 145,495 bytes at gzip level 9, and
  contains one strict-mode inline JavaScript IIFE.
- The file is served directly for local review. Query parameters select
  isolated scenes and QA states.

### Scene and progression model

- The title, atmospheric arrival bridge, four-plate Overworld, RD-42 interior,
  eight-plate Shard Foundry, Wound bridge, Wound boss encounter, and surface
  return all share one runtime.
- `configureEpisodeScene()` rebuilds geometry, population, mission state, and
  scene asset bindings in place. History state keeps scene URLs reloadable.
- The Foundry-to-Wound handoff stores a runtime checkpoint snapshot. Wound
  retries restore Foundry score, health, time, and equipment. Wound-touched
  Vesperite is the completion condition for returning to the surface.
- There is no save-slot or Continue Game feature in Beta 2. Session storage
  persists Episode credits; local storage persists the sound preference.

### Update, render, and state

- One `requestAnimationFrame` loop calls `update(delta)` and `draw()`.
- Delta is elapsed-time based and capped at 33 ms to avoid a huge resume step.
- Simulation states include ready, running, paused, dying, lost, transporting,
  ship transitions, suit/kit transitions, boss intro, and dialogue.
- Scene transitions reset frame timing and release controls.
- The final lifecycle gate requires both page visibility and window focus.

### Player, collision, combat, and hazards

- Horizontal movement uses acceleration and friction. Gravity, coyote time,
  jump buffering, one-way top-crossing, explicit drop-through exclusion, and
  moving-platform support are elapsed-time based.
- Damage uses five health points and desktop invulnerability of 1.15 seconds.
  Ludo mode resolves an authored death pose before presenting Retry.
- The intrinsic telescopic seeker and optional heavy rifle share bounded bolt
  arrays. Expired particles, popups, orbs, bolts, and defeated actors are
  filtered out.
- Foundry hazards use authored thermal and arc machinery. Legacy title/default
  hazards have no telemetry ID, which is valid after the P0 guard.
- Uplink completion requires twelve shards, both relays, and the route
  obstruction cleared.

### Input and audio

- Keyboard and pointer/touch controls feed a shared action state. Full
  controller support is not claimed; gamepad Start only skips the boss
  announcement.
- Input listeners and the animation loop are registered once, not per scene.
- Two persistent HTML audio elements provide music crossfades. One lazy Web
  Audio context provides synthesized tones. Sound effects use bounded,
  reusable HTML audio channel pools.
- Audio is unlocked by the explicit Load Game gesture. Pause, mute, focus
  loss, and visibility changes stop or pause the applicable channels.

### Assets and rendering

- Rendering is Canvas 2D at a 1,672 × 941 logical widescreen resolution.
- Pixel presentation uses nearest-neighbor rendering and CSS scaling. Portrait
  mode uses a narrower logical view while retaining the 941-pixel height.
- Assets are declared by key. Critical assets have an in-page failure and
  retry flow. Inactive scene groups are released, and lower Foundry plates are
  retained only near the active room.
- All 119 referenced image/audio paths exist with exact case.

### Existing verification

- Baseline verification consisted of 42 Python contract scripts.
- This audit adds a 43rd contract,
  `tools/verify_super_frgmnts_runtime_reliability.py`.
- The new verifier covers the legacy-hazard guard, completion ordering, focus
  lifecycle, route-specific title loading, and the two Episode-only QA seams.
- Browser behavior was exercised manually through the connected browser;
  there is still no checked-in automated browser runner.

## Baseline

### Repository safety

- `main` was clean and exactly tracking `origin/main`.
- No pre-existing user changes existed.
- Work moved to `audit/overnight-full-review` before edits.
- No user files were reset, stashed, discarded, overwritten, or amended.

### Applicable checks

- Python: 3.14.3.
- Normal shell `node` was unavailable on `PATH`; bundled Node 24.14.0 was used.
- All 42 baseline Python contracts passed in 3.12 seconds.
- Inline JavaScript syntax checking passed after extracting the complete IIFE.
- `git diff --check` passed.
- No install, build, production-build, typecheck, lint, unit, integration, or
  browser-runner command exists for this static artifact.

### Baseline runtime evidence

- Canonical title URL: two uncaught `TypeError` exceptions from
  `hazard.id.replace(...)` in `drawHazards()`.
- The first throw occurred before the frame scheduled its successor.
- After Load Game and Begin Episode, the Overworld drew once, but worker and
  ambient telemetry did not change over the next observation window.
- Direct Overworld, Foundry, Wound, and RD-42 URLs did not contain the legacy
  hazard data and therefore did not reproduce this crash.
- The desktop cold entry requested 10,700,803 local bytes before font and
  favicon traffic, including an unused 2,486,472-byte portrait title and
  78,963-byte Wound announcement.

## Findings

### P0

#### P0-01 — Canonical entry terminates the only animation loop

**Evidence:** The default URL threw `TypeError: Cannot read properties of
undefined (reading 'replace')` twice from `drawHazards()`. Legacy hazards are
valid collision records without `id`; the renderer treated `id` as mandatory
only when exporting optional telemetry. Worker telemetry remained unchanged
after the episode started.

**Root cause:** A later telemetry addition called `hazard.id.replace(...)`
unconditionally. The frame scheduled the next `requestAnimationFrame` only
after `draw()`, so the exception permanently terminated the loop.

**Fix:** Telemetry export now runs only when `hazard.id` exists. Rendering,
collision, art, timing, and hazard values are unchanged.

**Regression coverage:** The new verifier retains an unlabelled legacy hazard
fixture and requires the guard. Browser retest loaded the canonical title,
began Episode 01, completed the arrival bridge, and observed changing
Overworld worker telemetry across two 650 ms samples.

**Status:** Fixed.

### P1

No P1 finding.

### P2

#### P2-01 — Death and Uplink completion could both fire in one update

**Evidence:** The update order processes electrified platforms, hazards,
enemies, energy orbs, and bolts before `checkUplink()`. Damage can change
`state` from `running` to `dying`, but the old `checkUplink()` had no state
guard. A player taking a fatal hit while overlapping a satisfied Uplink could
therefore begin the Wound transition after death.

**Root cause:** Completion assumed its caller was still in `running` state
even though earlier functions in the same update can change that state.

**Fix:** `checkUplink()` now returns unless `state === "running"`.

**Regression coverage:** The Episode-only
`qa=completion-collision` seam starts a one-hit player inside an active hazard
and fully satisfied Uplink. Browser retest produced `Death becomes you`, five
empty hearts, an active QA hazard, and remained on the Foundry URL with no
Wound transition.

**Status:** Fixed.

#### P2-02 — Visible window blur did not suspend simulation

**Evidence:** Baseline blur handling released controls and paused audio, but
the frame gate considered only `document.visibilityState`. A browser window
can be visible but unfocused, so enemies, hazards, and the timer could continue
after focus loss despite the canonical lifecycle requirement.

**Root cause:** Focus and visibility were treated as the same lifecycle signal.

**Fix:** A `runtimeFocused` flag now gates simulation and boss gamepad polling.
Blur, pagehide, and hidden-page paths clear the flag and reset `lastFrame`;
focus, pageshow, and visible-page paths restore it and request a fresh render.

**Regression coverage:** The repository verifier requires the gate and all
interruption paths. The connected browser could create background tabs but
could not actively transfer native window focus, so a real OS-level blur/resume
timing test remains outstanding.

**Status:** Fixed with static and code-path coverage; native focus transfer is
listed as a remaining test risk.

#### P2-03 — Desktop cold entry eagerly downloads route-inactive title art

**Evidence:** A fresh 1,280 × 720 local origin requested the desktop title,
portrait title, and Wound boss announcement. The latter two totaled 2,565,435
bytes and were not usable on that route.

**Root cause:** Responsive title sources and the boss announcement had parser-
visible URLs before scene selection. The title was also duplicated as a static
CSS URL.

**Fix:** Static CSS and markup now begin without fetchable art URLs. Runtime
selection assigns exactly one desktop or portrait title source and reuses it
for the blurred backing layer. The boss title receives a source only in a Wound
scene. Art files, dimensions, filters, timing, and presentation are unchanged.

**Regression coverage:** The new verifier requires data-only initial markup
and runtime selection. A fresh post-fix server log requested only the desktop
title; the boss element had no `src`. A direct Wound retest loaded the correct
1,400 × 320 announcement.

**Status:** Fixed.

### P3

#### P3-01 — Contract tests do not execute browser behavior

All 42 baseline contracts passed while the public game was universally frozen.
They are valuable source and asset contracts, but they cannot detect an
exception in the first animation frame. A repository-owned browser smoke test
should assert that the canonical entry reaches Arrival and that a world
telemetry value advances over time.

**Status:** Deferred. The audit adds the smallest static verifier and manual
browser regression, not a new test framework.

#### P3-02 — The runtime is a 25,336-line mutable single file

The 903 KiB-class inline runtime combines scene configuration, actors, physics,
audio, assets, UI, and QA seams. It has extensive shared mutable state and
several scene-configuration branches that must be kept synchronized.
Compression keeps network transfer modest, but maintainability and behavioral
test isolation are poor.

**Status:** Deferred. A broad rewrite would exceed the demonstrated risk and
could disturb game feel.

#### P3-03 — Hot paths allocate and query more than necessary

Per-frame paths create bolt trail objects, rebuild filtered particle and popup
arrays, scan enemy and platform collections, and perform some repeated DOM
queries. The sustained cadence sample and repeated cycles did not demonstrate
a gameplay-visible stall or retained growth, so optimization without a real
trace would be speculative.

**Status:** Deferred pending a native performance trace and heap profile.

#### P3-04 — Foundry pause copy uses a survey-era phrase

The pause text chooses the generic expansion-preview wording before its
Episode-specific branch and can describe the production Foundry run as a
“unified world survey.” This is inaccurate but does not affect state,
progression, or accessibility.

**Status:** Deferred to avoid unrelated cosmetic churn.

#### P3-05 — Title styling has an optional external font dependency

The page requests Google Fonts CSS. Local font fallbacks preserve function if
the request fails, and no game-critical asset depends on it, but the request
adds an avoidable external cold-load dependency and complicates offline/native
packaging.

**Status:** Deferred because font packaging or replacement is an asset and
design decision.

## Gameplay and reliability result

- All eight Foundry plate entry points loaded with the expected zone, grounded
  spawn, 16 enemies, two hazards, and one route lock.
- Pause held the Foundry timer constant for 1.3 seconds and resume continued it.
- Twenty Foundry restart cycles preserved one canvas, two music elements, and
  stable population counts.
- Twenty deterministic death→Retry cycles ended correctly with the same one
  canvas and two music elements. Firing while lost did not escape the loss
  state.
- The Wound was played from safe bay through threshold, announcement, 50-hit
  rifle combat, boss death, corpse dissolve, specimen recovery, surface
  return, all 31 Dras report cards, and Chapter One completion.
- Ten full specimen-recovery→surface-return transitions ended on the canonical
  Overworld return URL with stored material, one canvas, and two music elements.
- RD-42 suit change, flight-suit jump, armor-gated hatch, re-arm, service-kit
  recovery, and exit all passed.
- Arrival dialogue Keep Listening and Skip Scene branches passed.
- Coreworks transport activation, Start Over, and Enter Foundry branches passed.
- No duplicate animation-loop registration, listener installation, canvas, or
  music element was observed.

The campaign was exercised as adjacent scene checkpoints, not as one
uninterrupted manual traversal of every collectible across all eight Foundry
plates. The matrix records that limitation.

## Performance result

The detailed evidence is in `docs/audit/PERFORMANCE_REPORT.md`.

- Desktop cold-entry local bytes: 10,700,803 → 8,139,951
  (`-2,560,852`, `-23.93%`).
- HTML: 1,006,053 → 1,010,636 raw bytes; gzip 144,901 → 145,495.
  The reliability code adds 594 compressed bytes.
- Baseline Wound moving-world proxy: 222 changes / 3,002 ms, median 14 ms,
  p95 20 ms, max 29 ms.
- Final isolated proxy: 352 changes / 3,000 ms, median 10 ms, p95 12 ms,
  max 17 ms. This is an observable dataset cadence, not a native FPS trace,
  and the final sample was taken after parking 17 completed test tabs.
- No browser JS heap API or native performance trace was available. DOM counts,
  scene decoded-size estimates, and repeated cycles were used as memory proxies.

## Files changed

- `super_frgmnts.html`
- `tools/verify_super_frgmnts_runtime_reliability.py`
- `docs/audit/OVERNIGHT_PROGRESS.md`
- `docs/audit/OVERNIGHT_AUDIT.md`
- `docs/audit/PERFORMANCE_REPORT.md`
- `docs/audit/PLAYTEST_MATRIX.md`

No image, audio, font, manifest, lockfile, generated artifact, or dependency
file changed.

## Tests added

- `tools/verify_super_frgmnts_runtime_reliability.py`
- `?episode=01&stage=foundry&autostart=1&qa=death`
  deterministic death-cycle seam.
- `?episode=01&stage=foundry&autostart=1&qa=completion-collision`
  deterministic fatal-damage/completion ordering seam.

Both QA seams require the Episode beta and have no effect on normal routes.

## Final verification

### Commands that ran

```sh
/usr/bin/time -p sh -c 'for test in tools/verify_super_frgmnts_*.py; do python3 "$test" || exit 1; done'
```

Result: all 43 contracts passed in 3.20 seconds.

```sh
sed -n '/^    <script>$/,/^    <\/script>$/p' super_frgmnts.html |
  sed '1d;$d' |
  /Users/rylee/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --check
```

Result: passed.

```sh
git diff --check
```

Result: passed.

```sh
python3 -m http.server 8768 --bind 127.0.0.1
```

Result: canonical title, default title→Arrival, Wound art selection, death
cycles, collision ordering, and transition browser checks launched locally.

There is no project build, typecheck, lint, unit runner, integration runner, or
automated browser runner to execute.

### Checks still failing

No applicable repository check fails. The blocked/partial browser conditions
below are measurement gaps, not failing commands.

## Areas not fully tested

- A true 390 × 844 portrait viewport could not be established. The connected
  browser accepted viewport requests but continued to report 1,280 × 720,
  DPR 2. Portrait behavior has source-contract coverage, and touch controls
  were exercised at desktop size.
- Native window blur/background/foreground transfer was not exposed by the
  connected browser. The lifecycle code and verifier cover it, but an OS-level
  timing test is still required.
- JS heap snapshots, decoded-image residency, garbage-collection events, long
  tasks, and a native frame trace were unavailable.
- No gamepad hardware was available. Only the claimed boss Start mapping was
  inspected; full controller support is explicitly future scope.
- Deepworks geometry and reachability have contract coverage, but the complete
  required and optional routes were not manually traversed in this session.
- Reload during the exact black-transition interval, opposing held keyboard
  inputs, pause on the exact fatal-damage frame, and pause on the exact
  completion frame were not reliably injectable through the browser surface.
- Continue Game and malformed-save behavior are not applicable because Beta 2
  has no save-slot/Continue feature.

## Remaining risks

- The P0 escaped 42 passing source contracts. Until a real browser smoke test
  runs in CI, another first-frame exception can regress unnoticed.
- Scene group decoded-size estimates reach about 67.7 MB for the Wound before
  browser overhead. Mobile Safari/WKWebView memory needs device measurement.
- The monolithic global state makes scene-ordering fixes harder to reason about.
- The optional Google Fonts request remains an external/offline dependency.
- The focus fix should receive native desktop and mobile lifecycle validation.

## Recommended next three engineering tasks

1. Add a minimal automated browser smoke suite that loads the canonical URL,
   clicks Load Game and Begin Episode, verifies changing world telemetry, and
   runs the two QA ordering routes at desktop and portrait-mobile sizes.
2. Add performance and memory budgets on real target hardware: cold request
   bytes, scene decoded memory, p95 frame time, restart-cycle heap growth, and
   audio context/channel counts, especially in iOS WKWebView.
3. Extract testable runtime modules behind a generated single-file shipping
   artifact, beginning with lifecycle/state transitions and asset selection.
   Require pixel, timing, audio, and collision parity before each extraction.

## Commits created

- `bd6669d7` — `audit: harden runtime reliability`
- `audit: document overnight review` — documentation commit containing this
  report and the other morning deliverables

## Safety confirmation

The starting worktree was clean, so there was no pre-existing user work to
merge around. All work is isolated on `audit/overnight-full-review`. No remote
branch was pushed, no pull request was opened, no deployment occurred, and no
production or external service was modified.
