# SUPER FRGMNTS Performance Report

**Audit date:** 2026-07-29

**Branch:** `audit/overnight-full-review`

**Renderer:** Canvas 2D, 1,672 × 941 logical widescreen surface

## Test environment

- Local static serving from `/Users/rylee/Projects/outsidetheworld`.
- Connected in-app Chromium browser.
- Reported browser viewport: 1,280 × 720, device-pixel ratio 2.
- Requested 1,440 × 900 and 390 × 844 viewport changes were accepted by the
  browser capability but did not change `innerWidth`, `innerHeight`,
  orientation, or pointer characteristics.
- Python 3.14.3 for repository verification and asset inspection.
- Bundled Node 24.14.0 for inline JavaScript syntax checking.
- Measurements are local-loopback observations, not Internet or production-CDN
  measurements.
- A fresh port supplied a separate browser cache origin for each cold-load
  request inventory.

## Method

Scenarios reviewed:

- Canonical title at cold and warm load.
- Title-to-Arrival launch.
- Direct Overworld, Foundry, Wound, and RD-42 readiness.
- All eight Foundry room spawns.
- Foundry pause/resume and 20 restarts.
- Wound idle moving construction.
- Sustained Wound combat and 50 rapid rifle hits.
- Twenty death→Retry cycles.
- Ten Wound completion→surface-return transitions.
- Multi-minute scene and transition play.

The connected browser did not expose a native performance trace, JS heap
snapshot, GC event stream, or decoded-image memory. Frame observations use
changing rounded world telemetry (`woundLeftLiftY`, `woundRightLiftY`, and
`woundBridgeX`) as a lower-bound requestAnimationFrame cadence proxy. One
combined value is sampled repeatedly; it can reveal stalls but is not an
authoritative FPS counter.

## Before-and-after summary

| Metric | Baseline | Final | Change |
| --- | ---: | ---: | ---: |
| Canonical desktop local request bytes, excluding font/favicon | 10,700,803 | 8,139,951 | -2,560,852 (-23.93%) |
| Parser-visible inactive title assets on desktop | 2 | 0 | -2 requests |
| HTML raw bytes | 1,006,053 | 1,010,636 | +4,583 |
| HTML gzip-9 bytes | 144,901 | 145,495 | +594 |
| Python verification contracts | 42 | 43 | +1 |
| Wound proxy changes / observation | 222 / 3,002 ms | 352 / 3,000 ms | Not directly causal; final sample isolated |
| Wound proxy median interval | 14 ms | 10 ms | No regression observed |
| Wound proxy p95 interval | 20 ms | 12 ms | No regression observed |
| Wound proxy maximum interval | 29 ms | 17 ms | No regression observed |
| Canvas elements after repeated cycles | 1 | 1 | Stable |
| Persistent music elements after repeated cycles | 2 | 2 | Stable |

The code fix was justified by request bytes, not timing. The cold observation
window was 1,397 ms at baseline and 1,514 ms final, with both including an
artificial 1.2-second settle and browser-control overhead. That noise does not
demonstrate a time-to-ready improvement. A later warm cached navigation
completed in 62 ms with the title action ready; earlier warm observations were
189–218 ms under a more heavily loaded browser session. These are useful local
sanity checks, not controlled benchmark results.

## Loading observations

### Baseline canonical desktop entry

The fresh-origin server observed:

- `super_frgmnts.html`
- desktop title painting
- portrait title painting
- Wound boss announcement title
- jump control icon
- fire control icon
- Veyra atmospheric approach painting
- title audio

Total before fonts and favicon: 10,700,803 bytes.

The 2,486,472-byte portrait painting and 78,963-byte boss announcement were
unusable on the desktop title route. They were the only removed requests.

### Final canonical desktop entry

The fresh-origin server observed:

- `super_frgmnts.html`
- desktop title painting
- jump control icon
- fire control icon
- Veyra atmospheric approach painting
- title audio

Total before fonts and favicon: 8,139,951 bytes.

The title image completed at its authored 1,672 × 941 dimensions. The boss
element had no `src`. A separate Wound route loaded the correct 1,400 × 320
boss title, confirming that route selection deferred rather than removed it.

### Largest canonical-entry transfers

| Resource | Encoded bytes |
| --- | ---: |
| Title audio | 2,881,035 |
| Desktop title painting | 2,446,925 |
| Veyra atmospheric approach | 1,800,249 |
| Final HTML | 1,010,636 |
| Fire control icon | 721 |
| Jump control icon | 385 |

The remaining cold bytes are content-bearing and were not altered because the
audit prohibited asset compression/replacement and required preserving audio
and art quality.

## Bundle and code observations

- Final `super_frgmnts.html`: 25,336 lines and 1,010,636 raw bytes.
- Baseline inline JavaScript: approximately 902,830 bytes.
- Gzip reduces the complete final HTML to 145,495 bytes, so transfer size is
  not proportional to raw source size.
- The monolith still incurs one large parse/compile unit and makes runtime
  behavior difficult to test independently.
- There is no generated development versus production bundle to compare.
- No source map, development logger, debug frame logging, or duplicate
  animation loop was observed.

## Asset observations

### Inventory

- 119 unique image/audio references.
- 119 exact-case local paths present.
- Total referenced encoded content: 70,881,596 bytes.
- Referenced images alone would occupy approximately 202,681,174 bytes as
  decoded RGBA if all were resident simultaneously.
- Normal runtime residency is lower because inactive scene assets are released
  and Foundry lower plates stream by nearby room.

### Scene-group estimates

| Scene group | Unique images | Encoded bytes | Approx. decoded RGBA |
| --- | ---: | ---: | ---: |
| Foundry | 51 | 14,258,494 | 52.3 MB |
| Overworld | 34 | 13,653,303 | 49.0 MB |
| Wound | 34 | 12,394,078 | 67.7 MB |
| Isolated RD-42/interior route | 38 | 16,065,728 | 59.1 MB |

The Wound is the largest decoded scene group even though it is not the largest
encoded group. The upward-turn/watch boss sheets are approximately 15 MB each
decoded; the Foundry expanded background is approximately 9.4 MB; the two
Wound background slices are approximately 7.3 MB each.

The only referenced images with an axis above 2,048 pixels are the two
documented 2,816 × 184 Vesperite impact/collapse strips. No unexpected
portability exception was found.

## Frame-time observations

### Baseline Wound moving-world proxy

- Duration: 3,002 ms.
- Observable changes: 222 (approximately 74 changes/second).
- Mean interval: 13.50 ms.
- Median: 14 ms.
- p95: 20 ms.
- Maximum: 29 ms.

### Final isolated Wound proxy

Before the final sample, 17 completed test tabs were navigated to `about:blank`
so their game loops could not compete for the browser process.

- Duration: 3,000 ms.
- Observable changes: 352 (approximately 117 changes/second).
- Mean interval: 8.50 ms.
- Median: 10 ms.
- p95: 12 ms.
- Maximum: 17 ms.

This is consistent with a high-refresh requestAnimationFrame loop without an
observable stall in the final sample. It must not be read as a certified
117 FPS result: rounded moving-world telemetry and browser-control sampling are
proxies, and the baseline/final browser load differed. The reliability and
loading fixes do not change animation timing, physics constants, or scene
drawing complexity.

### Paused and hidden work

- Foundry timer stayed at 01:30 for a 1.3-second paused observation.
- Paused state draws only when `renderRequested` is set.
- Hidden pages reset `lastFrame` and do not update.
- The audit adds the missing focus gate so visible-but-unfocused windows also
  skip simulation.
- No duplicate `requestAnimationFrame` registration was found.

## Memory and lifecycle observations

### Stable proxies

- Twenty Foundry restarts: one canvas and two persistent music elements at
  samples 1, 5, 10, 15, and 20.
- Twenty death→Retry cycles: one canvas and two music elements at the same
  sample points.
- Ten complete Wound→surface transitions: final state retained one canvas and
  two music elements.
- Enemy and hazard counts returned to 16 and 2 on Foundry restarts.
- Scene changes rebuild arrays rather than appending a second population.
- Global input, lifecycle, and button listeners are installed once.
- One Web Audio context is created lazily. Effect channel pools have fixed
  configured sizes.
- Music crossfades reuse two channels; scene changes do not append audio tags.

### What could not be measured

- Browser JS heap at session start/end.
- Detached DOM nodes.
- Decoded-image residency and release timing.
- Audio node and decoded audio buffer memory.
- GC frequency and pause duration.
- Main-thread long tasks and style/layout slices.

The stable proxies rule out obvious DOM/audio duplication, but they do not
prove the absence of a smaller object or decoded-resource leak.

## Hot-path code review

The main candidates for a trace-guided follow-up are:

- `particles`, `popups`, bolts, and other collections rebuilt with `filter()`
  each update.
- New trail and effect objects during repeated firing.
- Repeated `find()`, `some()`, and `filter()` passes over enemies and platforms.
- Selected repeated DOM queries in update/HUD paths.
- Wound camera/platform filtering and telemetry writes on each draw.

No measurable frame instability or retained-count growth justified changing
these overnight. Pooling or caching without a trace could introduce stale
state, alter effect density, or complicate cleanup.

## Audio observations

- Audio remains behind the explicit Load Game gesture.
- Two music channels support bounded crossfades.
- Repeated restarts did not add audio elements or stack visible music state.
- The title, Overworld, Foundry, Wound, and RD-42 route to distinct tracks.
- Pause and sound preference behaved consistently in play.
- Missing-audio failure was not induced.
- Native clipping/loudness measurement was unavailable; 50 rapid boss rifle
  shots produced no runaway UI or channel growth.

## Remaining bottlenecks

1. Content-heavy cold entry: 8.14 MB local uncompressed request bytes remain,
   dominated by title audio and two authored paintings.
2. Wound decoded memory: approximately 67.7 MB before browser/Canvas overhead.
3. Single-file parse/compile and global runtime state.
4. Per-frame transient allocation candidates without native profiling.
5. Optional Google Fonts stylesheet request for an otherwise local game.

## Recommended measurement follow-up

- Add a checked-in browser benchmark with PerformanceObserver long-task data,
  `requestAnimationFrame` deltas, request inventories, and deterministic scene
  routes.
- Capture Chrome/Android and Safari/WKWebView heap and decoded-image residency
  before/after 20 restarts and 10 scene transitions.
- Establish budgets per target: cold bytes, title-interactive time, scene-ready
  time, p95 frame time, worst frame, peak decoded memory, and retained heap.
- Re-run the Wound and Foundry busiest scenes at 60 Hz and 120 Hz on real
  hardware.
- Decide separately whether title audio packaging or font self-hosting is
  artistically and operationally acceptable; neither should be changed only
  for a synthetic score.
