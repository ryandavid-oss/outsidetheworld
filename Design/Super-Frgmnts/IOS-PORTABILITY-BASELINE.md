# SUPER FRGMNTS // Platform Baseline 1

**Status:** Active
**Established:** 2026-07-26
**Product direction:** Web-first, iOS-ready

## Purpose

SUPER FRGMNTS remains a first-class web game. Its canonical production runtime
is `super_frgmnts.html` on `main`, published through GitHub Pages.

The long-term platform target is to reuse that runtime in:

1. the public web edition;
2. an installable, offline-capable PWA;
3. a Capacitor/WKWebView iOS application; and
4. selective native integrations where they materially improve the game.

A full SpriteKit or other native-engine rewrite is not the baseline plan.
Artwork, episode data, movement, combat, camera, enemy behavior, dialogue, and
level logic should remain shared across platforms.

This document is a direction for future work, not a claim that the current
single-file runtime is already fully separated. Do not stop useful game work
for a broad speculative refactor. When a feature touches one of the seams
below, improve that seam as part of the feature.

## Product principles

- The web edition must never become a lesser demo of the iOS edition.
- A future iOS package should bundle episode-critical assets locally and remain
  playable without a network connection after installation.
- Platform differences belong in small adapters, not duplicated game rules.
- Native features are enhancements. The game must remain complete without
  Game Center, iCloud, haptics, controller support, or push notifications.
- App Store presentation must feel like a complete game, not a remote webpage
  placed inside an application shell.

## Architectural boundaries

Future work should converge toward four boundaries:

1. **Game core** — simulation, collision, enemies, weapons, rewards, camera,
   episode state, and win/loss rules.
2. **Content** — versioned manifests for rooms, dialogue, assets, enemy
   populations, pickups, and tuning values.
3. **Platform services** — input, lifecycle, audio focus, persistence, haptics,
   achievements, controllers, sharing, and commerce.
4. **Presentation** — Canvas rendering, DOM overlays, menus, dialogue, and
   accessibility announcements.

The game core must not require knowledge of Safari, WKWebView, Capacitor, Swift,
keyboard key codes, or a particular touch-control layout.

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

Keyboard, touch, controller, and future native input translate into these same
actions. A new mechanic must not be available only through one input source.

Every held action requires immediate release paths for:

- `pointerup`;
- `pointercancel`;
- `touchcancel`;
- lost pointer capture;
- window blur;
- page or application suspension;
- pause, dialogue, and modal transitions; and
- control-layout replacement or orientation change.

The playable surface must suppress selection, callouts, dragging, accidental
zoom, and browser gestures without disabling normal behavior elsewhere on the
site. Visual joystick position must never be the source of truth for movement
state.

The accepted mobile support floor remains 360 CSS pixels wide. Touch targets
must remain usable with thumbs, safe-area insets, and browser or native chrome.

## Rendering and timing contract

- Keep a stable logical world and scale it for the display.
- Simulation and animation use elapsed time, not an assumed frame count.
- Target smooth 60 Hz presentation without an intentional FPS cap.
- Cap expensive device-pixel-ratio work when additional resolution does not
  materially improve the pixel-art presentation.
- Pixel-art assets use deliberate nearest-neighbor scaling.
- Gameplay correctness must not depend on a specific viewport, refresh rate,
  or device orientation.
- Reduced-motion behavior must preserve all gameplay information.

## Asset and memory contract

- Assets load by scene or nearby room, not as one global game payload.
- Inactive scene images and audio must be releasable.
- New asset families require a manifest, runtime dimensions, frame timing, and
  a named owning scene.
- Runtime animation atlases should remain at or below 2,048 pixels on either
  axis. Larger atlases must be split or carry a documented exception.
- Source masters may be larger, but only normalized runtime derivatives ship.
- Background plates should remain independently streamable.
- Audio uses one lifecycle-aware director and bounded effect-channel pools.
- A feature review records its incremental transfer size and decoded-memory
  effect when it introduces a substantial asset group.

Scene loading must fail visibly and recoverably. A missing optional asset may
degrade gracefully; a missing critical asset must produce an in-game retry
path rather than a blank screen.

### Current reviewed atlas exceptions

The shipping web beta currently contains two narrow 2,816 × 184 Vesperite
boulder strips:

- `vesperite-boulder-impact-runtime-v1.png`
- `vesperite-boulder-collapse-runtime-v1.png`

They are accepted for the web beta because they are shallow, scene-scoped, and
do not create an oversized decoded surface. Before TestFlight promotion, split
each strip into two atlases no wider than 2,048 pixels and preserve its frame
order through the runtime manifest.

## Audio and lifecycle contract

- One intentional user gesture unlocks game audio.
- Music transitions are owned by the audio director, not individual scenes.
- Mute state survives scene changes.
- Backgrounding, focus loss, phone calls, audio-route changes, and application
  suspension stop gameplay and sampled effects safely.
- Resume restores at most one music stream and never duplicates a loop.
- Pause freezes the mission clock, simulation, animation, and controls
  together.
- Application restoration must not leave movement, firing, or the analog stick
  latched.

## Persistence contract

Persistent game data must use a versioned, serializable save model. Web storage
is an implementation detail behind a save adapter, not the canonical state
model.

The save model should be capable of representing:

- episode and checkpoint progress;
- Galactic Credits and purchases;
- unlocked equipment and selected weapon;
- settings and accessibility preferences;
- achievements and completion bonuses; and
- schema version and migration history.

The web adapter may initially use local storage or IndexedDB. A future iOS
adapter may add local native storage and optional iCloud synchronization
without changing game rules.

## Native integration boundary

The first iOS build should use the shared web runtime inside Capacitor/WKWebView
with bundled local assets. Swift or native plugins should be introduced only
for bounded capabilities such as:

- haptics;
- Game Center achievements and leaderboards;
- iCloud save synchronization;
- external-controller support;
- native audio interruption reporting;
- StoreKit purchases, if ever approved for the game economy; and
- native sharing, review, and support surfaces.

JavaScript must treat these capabilities as optional and feature-detect them.

## Feature acceptance gate

A new gameplay or presentation feature is portable when:

- desktop keyboard play still works;
- 360–390 px portrait touch play still works;
- every held input survives cancellation and focus loss;
- pause, mute, background, and resume behavior remain coherent;
- the feature does not require a network request during normal installed play;
- assets are assigned to a scene and released when inactive;
- state is serializable rather than trapped only in DOM elements;
- no browser-specific API is called directly from game rules;
- accessibility announcements remain meaningful;
- JavaScript syntax and the relevant SUPER FRGMNTS contracts pass; and
- at least one desktop and one portrait-mobile browser review show no console
  errors or blank critical artwork.

An iOS/TestFlight promotion adds:

- current-device and lower-memory-device profiling;
- safe-area and orientation review on physical hardware;
- interruption tests for calls, Control Center, headphones, and app switching;
- offline launch and restoration tests;
- controller and haptic fallback tests when those features exist; and
- App Store completeness, privacy, and metadata review.

## Migration sequence

No migration work is required merely because this baseline exists. When the
game is ready:

1. finish the production web episode and stabilize its save model;
2. add the PWA manifest, offline cache, icons, and install presentation;
3. create a thin Capacitor iOS shell that bundles the same production files;
4. profile memory, rendering, audio, and lifecycle behavior in TestFlight;
5. add only the native integrations justified by testing; and
6. keep the web, PWA, and iOS editions on the same content and game-core
   version.

## Decision rule

When two implementations are equally good for the current web game, prefer the
one that:

1. keeps game rules independent of the browser;
2. makes assets and state explicit;
3. has a complete interruption and restoration path; and
4. can be exercised by both touch and non-touch input.

Portability must support the atmosphere, fidelity, and joy of SUPER FRGMNTS.
It is not permission to flatten the game into the lowest common denominator.
