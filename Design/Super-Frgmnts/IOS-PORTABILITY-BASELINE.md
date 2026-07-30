# SUPER FRGMNTS // Native Apple Platform Baseline 2

**Status:** Active
**Established:** 2026-07-29
**Supersedes:** Platform Baseline 1, established 2026-07-26
**Product direction:** Native iOS, iPadOS, and macOS

## Decision

All new SUPER FRGMNTS production development targets a native Apple-platform
package. The supported product family is:

1. iPhone on iOS;
2. iPad on iPadOS; and
3. Apple silicon and Intel Macs on macOS, subject to the deployment targets
   selected when the Xcode project is established.

The existing `super_frgmnts.html` game is frozen as an executable design,
content, timing, and parity reference. It is not the foundation of the native
shipping runtime. Do not add web gameplay, browser-renderer improvements, PWA
packaging, WebGL migration, or a Capacitor/WKWebView shell.

Do not delete or broadly refactor the frozen web implementation until the
corresponding native systems and content have passed parity review. It contains
approved behavior and authored values that must be extracted deliberately.

## Why Baseline 1 was superseded

Baseline 1 assumed the shared browser runtime would provide sufficient
production performance on Apple devices. Production-scale review challenged
that assumption before public release. Packaging the same HTML, Canvas, CSS,
and JavaScript inside WKWebView would preserve the renderer whose performance
is in question rather than replace it.

The project is unreleased and its episodic scope will grow. The least risky
time to change the production architecture is therefore now, before additional
episodes, enemies, fragments, effects, and native integrations multiply the
migration cost.

The architectural parts of Baseline 1 remain valuable: explicit game rules,
versioned content, action-based input, bounded asset ownership, serializable
saves, and platform-service boundaries. Only the web-first runtime and release
assumptions are retired.

## Native implementation baseline

The first implementation path is Swift and SpriteKit in one source-controlled
Xcode project, with shared game modules used by the iOS, iPadOS, and macOS
application surfaces.

- SpriteKit owns scene presentation, sprites, cameras, effects, and rendering.
- Swift game-domain types own simulation, collision policy, enemies, weapons,
  rewards, episode state, and win/loss rules.
- SwiftUI, UIKit, or AppKit may host menus and platform presentation where
  appropriate; gameplay rules must not live in those views.
- Apple frameworks provide lifecycle, controller, audio, persistence, haptic,
  accessibility, commerce, and Game Center integration behind narrow
  interfaces.
- Raw Metal is not the starting point. Introduce a lower-level native renderer
  only if measured SpriteKit limitations remain after a representative
  production-load implementation and profiling pass.
- A third-party engine requires a new written decision. It must not be adopted
  merely to preserve a web export.

The production-load vertical slice is the commitment gate for this baseline.
It validates SpriteKit before the full episode is ported; it is not permission
to resume browser development while validation is underway.

## Architectural boundaries

Native work converges toward four boundaries:

1. **Game domain** — deterministic simulation, collision policy, enemies,
   weapons, rewards, camera intent, episode state, and win/loss rules.
2. **Content** — versioned data for rooms, dialogue, assets, enemy populations,
   pickups, animation timing, and tuning values.
3. **Platform services** — input, lifecycle, audio focus, persistence, haptics,
   achievements, controllers, sharing, and commerce.
4. **Presentation** — SpriteKit scenes and effects plus native menus, dialogue,
   HUD, and accessibility surfaces.

The game domain must not require knowledge of `SKScene`, SwiftUI, UIKit,
AppKit, a particular controller, or a particular screen size. Presentation
reads domain state and emits actions. Platform services satisfy Swift
protocols owned by the game, not the other way around.

Do not port the monolithic JavaScript runtime line by line. Extract approved
rules and authored values into native systems and versioned content, then
verify their behavior against the frozen game.

## Input contract

Gameplay consumes actions rather than device events:

- `moveLeft`
- `moveRight`
- `drop`
- `jump`
- `fire`
- `switchWeapon`
- `interact`
- `pause`
- `restart`

Touch, keyboard, mouse where appropriate, and Game Controller input translate
into the same actions. A mechanic must not be available through only one
supported input source.

Every held action requires immediate release paths for:

- touch or button cancellation;
- controller disconnect;
- application resignation or suspension;
- scene transition;
- pause, dialogue, and modal presentation; and
- control-layout or orientation change.

Touch controls must respect safe areas, remain usable with thumbs, and never
use the joystick's visual position as the source of truth for movement state.
The macOS package must support keyboard play; controller support is shared
across the product family.

## Rendering and timing contract

- Keep a stable logical world and scale it deliberately for each display.
- Run gameplay from elapsed time with a bounded fixed-step simulation.
- The shipping performance floor is a stable 60 Hz presentation at the
  production-load acceptance target.
- A 120 Hz ProMotion mode is desirable only when the device can sustain it
  without unstable pacing, unacceptable thermal load, or gameplay changes.
- Pixel-art assets use deliberate nearest-neighbor sampling.
- Batch compatible sprites through texture atlases and avoid unnecessary draw
  calls, effects, and node traversal.
- Cull or deactivate rooms, actors, particles, and effects that cannot affect
  the current simulation or camera.
- Gameplay correctness must not depend on viewport, refresh rate, device
  orientation, or display scale.
- Reduced-motion behavior must preserve all gameplay information.

Performance review records frame-time percentiles rather than relying on a
single average FPS value. It also records draw count, node count, memory,
launch time, scene-transition time, suspension/resume behavior, and sustained
thermal performance on physical devices.

## Production-load acceptance target

The initial native target preserves the already-approved scale forecast:

- fifty-four enemies, representing three times the Beta 2 roster;
- twenty-four Vesperite Fragments, representing twice the Beta 2 count;
- the eight-room Shard Foundry scene ownership and traversal model;
- representative projectiles, particles, glow, HUD, audio, and camera work as
  soon as their production quantities are defined; and
- no test-only simplification that removes the expensive presentation features
  the shipping scene requires.

The frozen browser benchmark at
`?episode=01&stage=foundry&room=4&autostart=1&load-profile=production-scale&frame-profile=benchmark`
is the reference workload and telemetry precedent. Native measurements replace
browser measurements for all promotion decisions.

The first physical-device matrix is:

- iPad Pro M4 with ProMotion enabled and Low Power Mode disabled;
- iPhone 17 Pro;
- MacBook Pro with M2 Pro; and
- Mac mini M4.

Record the exact device identifier, OS build, Xcode version, build
configuration, resolution, refresh-rate mode, and power state with every
accepted result.

## Asset and memory contract

- Bundle episode-critical assets locally; installed play must not require a
  network connection.
- Load assets by scene or nearby room rather than as one global payload.
- Inactive scene textures and audio must be releasable.
- Every asset family requires a manifest, runtime dimensions, frame timing,
  color and sampling expectations, and a named owning scene.
- Runtime texture atlases should remain at or below 2,048 pixels on either
  axis. Larger atlases require a measured and documented exception.
- Source masters may be larger, but only normalized runtime derivatives ship.
- Background plates remain independently loadable.
- Audio uses one lifecycle-aware director and bounded effect-channel pools.
- A feature review records its incremental package size and decoded-memory
  effect when it introduces a substantial asset group.

The two existing 2,816 × 184 Vesperite boulder strips must be split into
native atlases no wider than 2,048 pixels before their native scene is promoted.
Preserve frame order through versioned content data.

Scene loading must fail visibly and recoverably. A missing optional asset may
degrade gracefully; a missing critical asset must produce an in-game recovery
path rather than a blank or stuck scene.

## Audio and lifecycle contract

- One audio director owns music, ambience, and bounded effect playback.
- Mute and volume state survive scene and application transitions.
- Backgrounding, focus loss, calls, audio-route changes, and application
  suspension stop gameplay and sampled effects safely.
- Resume restores at most one music stream and never duplicates a loop.
- Pause freezes mission time, simulation, animation state, and controls
  together.
- Restoration must not leave movement, firing, or analog input latched.
- iOS and iPadOS behavior must respect the active audio session; macOS behavior
  must remain coherent across focus and device changes.

## Persistence contract

Persistent state uses a versioned, `Codable` save model. UserDefaults, files,
Keychain, iCloud, and Game Center are storage or service implementations, not
the canonical game state.

The save model must represent:

- episode and checkpoint progress;
- Galactic Credits and purchases;
- unlocked equipment and selected weapon;
- settings and accessibility preferences;
- achievements and completion bonuses; and
- schema version and migration history.

Every schema version requires deterministic decoding, migration tests, and a
recoverable response to corrupt or unsupported data. Optional iCloud
synchronization must not make offline local play unavailable.

## Native integration boundary

Native capabilities remain behind bounded services:

- Game Controller;
- haptics;
- Game Center achievements and leaderboards;
- local and optional iCloud save synchronization;
- audio interruption and route handling;
- StoreKit purchases, if the economy later authorizes them;
- native sharing, review, and support surfaces; and
- platform accessibility APIs.

The game remains complete when an optional service such as Game Center,
iCloud, haptics, or commerce is unavailable.

## First native milestone

Create a production-representative Foundry slice centered on Room 4:

1. establish the Xcode project, shared modules, targets, signing-neutral build
   settings, and automated tests;
2. render the approved room art, camera, Aryn, HUD, and representative effects;
3. implement movement, jump, drop, fire, collision, pause, and one
   representative enemy behavior through native action and domain boundaries;
4. instantiate the fifty-four-enemy and twenty-four-fragment workload with the
   same scene-ownership intent as the browser benchmark;
5. implement touch, keyboard, and controller mappings plus safe lifecycle
   release behavior;
6. run the physical-device matrix and capture frame, memory, thermal, launch,
   interruption, and restoration results; and
7. compare motion, timing, collision, framing, art, and atmosphere with the
   frozen reference.

The milestone passes when the representative build sustains the 60 Hz floor
on the primary iPad and iPhone targets, behaves correctly on macOS, survives
lifecycle tests, and reveals no architectural blocker to the projected
episode scale.

If SpriteKit misses the gate, profile and document the limiting subsystem
before changing engines. The next option must still produce native Apple
packages; returning to a browser runtime is not a fallback.

## Migration sequence

1. Preserve the current browser build and its production-scale benchmark.
2. Inventory and classify authored content, rules, assets, audio, and
   presentation behavior before extraction.
3. Complete and accept the first native milestone.
4. Establish native content schemas and port the shared episode shell.
5. Port systems in bounded vertical slices with behavioral parity tests.
6. Port and optimize each scene with explicit asset ownership.
7. Add native services only after the core offline game is stable.
8. Exercise iOS and iPadOS builds through TestFlight and validate the macOS
   package independently.
9. Promote the native package only after the complete Episode 01 route passes
   performance, lifecycle, save, input, accessibility, and content review.

## Out of scope

The following work is not part of the active product:

- new web gameplay or content;
- Canvas renderer optimization;
- WebGL renderer development;
- PWA packaging or offline-web work;
- Capacitor or WKWebView application packaging;
- browser compatibility, responsive-layout, or Gamepad API work; and
- maintaining feature parity with the frozen browser implementation after its
  role as a migration reference is complete.

Any exception requires an explicit product-direction change. Preservation work
must be narrowly scoped and must not become continued web development.

## Decision rule

When choosing between native implementations, prefer the one that:

1. sustains the production workload on the physical-device matrix;
2. keeps game rules independent of rendering and platform UI;
3. makes content, assets, and state explicit and testable;
4. has complete interruption and restoration paths;
5. supports touch, keyboard, and controller input without duplicated rules;
6. preserves the atmosphere, fidelity, and joy of SUPER FRGMNTS; and
7. reduces the cost of adding later episodes rather than optimizing only the
   current room.

Native architecture is not permission to flatten the game into the lowest
common denominator. The platform change exists to give the full game room to
grow.
