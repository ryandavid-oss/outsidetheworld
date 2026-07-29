# SUPER FRGMNTS // RD-42 Ship Interior Contract v1

**Status:** Isolated production-art interior integrated

**Established:** 2026-07-28

**Owning scene:** RD-42 interior

**Runtime impact:** Live normal-route interior with isolated review routes

This contract turns Aryn's climbable RD-42 into a small reusable interior
scene. The first required visit occurs during the Return to Dras interlude,
when Aryn recovers a compatible service kit for the failed Coreworks
transport.

Use this contract with:

- [`../../../../Post-Foundry/RETURN-TO-DRAS-INTERLUDE-v1.md`](../../../../Post-Foundry/RETURN-TO-DRAS-INTERLUDE-v1.md);
- [`../Collision/README.md`](../Collision/README.md);
- [`../Collision/ship-collision-revision-3a1-manifest.json`](../Collision/ship-collision-revision-3a1-manifest.json);
- [`../../../../IOS-PORTABILITY-BASELINE.md`](../../../../IOS-PORTABILITY-BASELINE.md); and
- [`RD42-SHIP-INTERIOR-WIREFRAME-v1.md`](RD42-SHIP-INTERIOR-WIREFRAME-v1.md).

## Experience target

Boarding the RD-42 should feel like entering a real place inside the hull Aryn
has already climbed.

The player:

1. jumps to the top-middle roof perch;
2. stands directly over the dorsal hatch;
3. sees `▼ ENTER RD-42`;
4. presses the shared Down/interact action;
5. watches Aryn lower herself feet-first through the hull;
6. continues the same descent from the interior ceiling hatch;
7. lands in the central airlock; and
8. regains control inside a compact, safe ship.

The scene is a sanctuary and character space, not a corridor inserted solely
to hold a quest object. Its first version remains deliberately small enough to
belong inside the approved exterior silhouette.

One plate is sufficient because it represents the RD-42's **inhabited spine**:
the cockpit, dorsal access, berth and pack workspace, and immediately useful
cargo. Closed pressure panels, the shallow under-deck volume, and the aft
engineering wall imply inaccessible flight systems without pretending the
player has seen every cubic foot of the ship.

## Exterior authority

The current runtime draws the ship at:

- world x = `OVERWORLD_ORIGIN_X + 176`;
- world y = `417 + shipHoverOffset`;
- draw width = 792;
- draw height = 311; and
- horizontal center = `OVERWORLD_ORIGIN_X + 572`.

The approved live roof perch is:

- local x = 500–644;
- world x = `OVERWORLD_ORIGIN_X + 500` through
  `OVERWORLD_ORIGIN_X + 644`;
- base y = 448;
- width = 144; and
- motion group = the existing 1.6-second RD-42 hover.

Aryn's normal Arrival spawn center already aligns with the ship center at local
x = 572. No new exterior climb, gangway, or ground-level door is required.

## Dorsal hatch activation

### Spatial trigger

The provisional hatch interaction occupies the inner portion of the center
roof perch:

- local center x = 572;
- local interaction x = 520–624;
- interaction width = 104;
- world interaction x =
  `OVERWORLD_ORIGIN_X + 520` through `OVERWORLD_ORIGIN_X + 624`;
- standing y = `448 + shipHoverOffset`; and
- valid center tolerance = ±52 pixels.

The interaction is valid only when:

- Aryn is alive and in normal surface gameplay;
- both feet are supported by the center ship surface;
- her center lies inside the hatch interaction range;
- no dialogue, pause, modal, damage, or scene transition is active; and
- the interior's critical assets are ready or can show a recoverable loading
  state.

Prompt:

`▼ ENTER RD-42`

### Opening-route prompt behavior

Aryn begins Arrival on Veyra standing directly over this location. To avoid
placing an immediate backwards-facing prompt over the episode's first frame:

- `shipHatchArmed` begins false on the initial arrival spawn;
- it becomes true after Aryn deliberately leaves the hatch range once; and
- it remains true for the rest of the surface scene.

All post-Wound surface-return states begin with `shipHatchArmed = true`.

This makes the interior voluntarily revisitable during the opening without
redirecting the initial control handoff.

### Down-action priority

When the hatch prompt is valid, ship entry takes priority over:

- Signal Sweep;
- optional surface assignments;
- any future ship-surface drop-through behavior; and
- generic world interactions outside the hatch range.

The interaction consumes one press. A held Down action cannot retrigger the
transition on arrival inside the ship.

Keyboard, touch-stick downward input, controller interaction, and future
native controls map to the same `interact` game action.

## Exterior descent

The exterior half of boarding is an authored state, not ordinary falling
physics.

| Phase | Provisional duration | Behavior |
| --- | ---: | --- |
| Align | 0.18 s maximum | Ease Aryn's center to the live ship center. |
| Prime | 0.10 s | The hatch seam and two cyan status marks illuminate. |
| Open | 0.22 s | The dorsal panels retract beneath Aryn. |
| Lower | 0.52 s | Aryn crouches and descends feet-first through the opening. |
| Occlude | 0.13 s | The foreground hatch rim hides her remaining silhouette. |
| Scene handoff | 0.10 s | Transfer to the already-open interior ceiling hatch. |

Total exterior target: approximately **1.25 seconds**.

During the sequence:

- movement, jumping, firing, weapon switching, pause toggling, and repeated
  interaction are suppressed;
- the rifle is stowed before the hatch opens;
- Aryn and every hatch layer inherit the exact live ship hover offset;
- camera tracking eases to the ship center;
- the ship continues hovering;
- the desert and ambient actors continue their non-hostile motion;
- no black full-screen cut occurs before Aryn is visibly inside the hull; and
- a foreground hatch rim draws after Aryn to provide physical occlusion.

The preferred final animation shows Aryn crouching, bracing one hand near the
hatch, and lowering herself feet-first. The greybox may prove the motion with
the existing idle silhouette, vertical translation, and the foreground mask
before a dedicated sprite strip is authored.

## Interior arrival

The interior scene begins with the ceiling hatch already open and Aryn's lower
body already visible beneath it.

| Phase | Provisional duration | Behavior |
| --- | ---: | --- |
| Continue descent | 0.50 s | Aryn travels down the short recessed access rails. |
| Release | 0.12 s | She releases the rails for a restrained final drop. |
| Land | 0.15 s | Aryn settles onto the airlock deck without a damage pose. |
| Close | 0.20 s | The ceiling panels close and their cyan seam returns to idle. |

Total interior arrival target: approximately **0.97 seconds**.

The complete exterior-to-control target is therefore approximately
**2.2 seconds**.

Control returns only after Aryn is grounded, the hatch is closed, held input
has been released, and the interior camera is stable.

Required accessibility announcement:

> RD-42 interior. Aryn entered through the dorsal hatch.

## Interior scene shape

The scene uses one standard **1,672 × 941** logical plate for compatibility
with the existing renderer and camera.

The actual ship shell occupies only the central portion:

- shell left bound = x 220;
- shell right bound = x 1,452;
- playable width = 1,232;
- outer dorsal housing reaches approximately y 226–272;
- normal occupied ceiling = y 438;
- overhead systems bay = approximately y 320–438;
- main deck = y 744; and
- dorsal hatch center = x 684.

The interior is a gameplay-readable stage representation of the exterior, not
an attempt to pretend the RD-42 contains kilometers of corridors. Sloping hull
ribs, tapered ends, and visible engine-pod intrusions keep the room tied to the
ship's manta-like silhouette.

The 306-pixel occupied volume between y 438 and y 744 is approximately 3.4
times the live sprite's 89-pixel visible height. The dorsal hatch chimney is
the one deliberate tall exception. Aryn remains at her established runtime
scale; the room and its furniture carry the scale correction.

Detailed coordinates and prop reservations live in
[`RD42-SHIP-INTERIOR-WIREFRAME-v1.md`](RD42-SHIP-INTERIOR-WIREFRAME-v1.md).

## Integrated review routes

The greybox is intentionally isolated from the current Episode 01 route:

- exterior hatch and continuous descent:
  `?preview=overworld&scene=ship-entry&autostart=1`;
- neutral interior exploration:
  `?preview=ship-interior&autostart=1`;
- service-kit objective:
  `?preview=ship-interior&objective=service-kit&autostart=1`; and
- post-Wound response with Trillian present:
  `?preview=ship-interior&state=post-wound&trillian=1&autostart=1`.

The direct interior routes can exit to the live ship exterior and re-enter
through the same hatch. They do not connect the post-Wound interlude to the
production chapter yet.

## Interior music

The RD-42 uses the dedicated two-minute `Spaceship Interior Loop`, not the
Overworld or Foundry score.

- The lossless stereo 48 kHz source is preserved at
  [`Audio/Spaceship_Interior_Loop_2026-07-29T063049.wav`](Audio/Spaceship_Interior_Loop_2026-07-29T063049.wav).
- The web runtime uses
  `Audio/super-frgmnts-rd42-interior-loop-v1.m4a` at a nominal 192 kbps.
- Runtime playback loops at `0.27`, slightly below the exterior Overworld mix.
- Approaching the exterior hatch preloads the interior channel.
- The authored descent crossfades to the interior score over 480 ms when the
  interior world becomes active.
- Exiting through the dorsal hatch crossfades back to the Overworld score over
  the same interval.
- Pause, mute, focus loss, mobile backgrounding, and gesture recovery use the
  shared episode audio lifecycle.

The source/runtime hashes and encoding contract live in
[`Audio/rd42-interior-music-v1.json`](Audio/rd42-interior-music-v1.json).

## Required zones

### Cockpit // optional

The cockpit occupies the left end of the shell.

It contains:

- Aryn's combined flight/suit cradle;
- a shallow forward canopy or sensor window;
- a navigation table;
- the deliberately disconnected Central Command link;
- local ship status; and
- one optional Coreworks Archive interaction.

The cockpit is visible from the entry but never blocks the service-kit route.

After Aryn carries Wound-touched Vesperite, the offline local spectral index
may report:

```text
LOCAL SPECTRAL INDEX // PARTIAL MATCH
SOURCE // RESTRICTED
CENTRAL AUTHORIZATION REQUIRED
```

This is a hint, not proof. It does not identify the specimen, unlock a file,
contact the Fleet, or explain the cover-up.

### Flight/suit alcove // isolated review interaction

The human-scale flight cradle at the cockpit edge doubles as Aryn's armor
change station. A shallow wall dock and retractable privacy/decontamination
screen define an alcove without enlarging the ship or blocking the cockpit
route.

The supplied 36-frame sequence is authoritative for **armored to flight
suit**:

- 36 frames at 76 ms each;
- complete authored duration = 2.736 seconds;
- Aryn remains stationary at the cradle;
- the ordinary player sprite is hidden while the sequence plays; and
- the final flight-suit pose supplies her main-deck standing state.

The change asset is normalized and documented under
[`../../Aryn/Armor-Change/README.md`](../../Aryn/Armor-Change/README.md).
Supplied run and jump sheets documented under
[`../../Aryn/Flight-Suit/README.md`](../../Aryn/Flight-Suit/README.md) now
support persistent flight-suit locomotion on the main deck. Control returns
after the forward sequence. Aryn can walk, run, jump, fall, and land in the
flight suit, then return to the alcove and press Down to re-arm.

The dorsal hatch and service-kit pack rail require field armor because the
current unarmored set does not include hatch traversal, pack attachment,
damage, or weapon poses. Reverse playback is still provisional; it is not a
claim that an authored re-arm sequence exists.

### Airlock // required entry and exit

The airlock occupies the center-left section and contains:

- the ceiling hatch;
- the entry landing clear zone;
- two recessed access rails;
- an equipment-seal indicator;
- a compact suit and weapon hardpoint; and
- the return interaction beneath the hatch.

Exit prompt:

`▼ EXIT RD-42`

The player uses Down because it is the shared interaction action even though
Aryn travels upward.

### Habitation and pack bench // optional

The central-right section communicates who Aryn is when she is not fighting.

It contains:

- a fold-down bunk;
- a ration heater;
- a small personal shelf;
- one restrained unsanctioned-flight detail;
- a conditional Trillian berth;
- Aryn's pack service bench; and
- a sealed keel-deck hatch reserved for future expansion.

The room should feel disciplined and used, not sterile and not cluttered into
comic relief.

When Wound-touched Vesperite is present, the pack bench may repeat its pulse
and display:

`UNKNOWN MATERIAL // INSTALLATION LOCKED`

The bench cannot consume the specimen or modify the pack during this
interlude.

### Keel service deck // reserved future area

The sealed hatch beneath the pack bench establishes that the RD-42 continues
below the occupied main deck. It is not a second room squeezed into the
current rear plate. When eventually approved and unlocked, the hatch should
transition through a short ladder or service lift into a separate lower-deck
scene.

Working uses for that future deck are:

- direct access to repair manifolds, shield-braid conduits, and the phase
  coupler bus;
- a compact emergency shelter or concealment compartment;
- a later lockdown sequence in which Aryn can hide from an enemy boarding
  party; and
- a constrained invasion route where damaged systems and enemy presence
  change the room without turning the upper cabin into a combat arena.

For the current chapter, the hatch is sealed, noninteractive, and free of
collision changes. It may show a keyed seam and depth cues, but it does not
open, accept a prompt, imply a secret collectible, or block the pack bench.

The bounded future concept is recorded in
[`RD42-KEEL-SERVICE-DECK-SEED-v1.md`](RD42-KEEL-SERVICE-DECK-SEED-v1.md).

### Cargo and engineering // required objective

The right end contains:

- shallow cargo racks;
- an exposed engineering wall;
- visible compatible transit hardware;
- the keyed Core Transit Service Kit; and
- enough clear floor for the recovery animation and prompt.

The service case contains:

- one phase coupler;
- two shielded field braids; and
- small keyed connectors packed with them.

Quest prompt:

`▼ RECOVER TRANSIT SERVICE KIT`

Before the transport fails, the service case remains visible but has no
recovery prompt. The player cannot take, sell, destroy, or duplicate it early.

## Service-kit recovery

Recovery is a single deterministic interaction:

1. Aryn opens the cargo rack.
2. The keyed case slides forward.
3. Its three occupied slots become readable for a short hold.
4. The case closes.
5. It attaches to the lower magnetic rail of Aryn's backpack or resolves to an
   equivalent clearly communicated carried state.
6. The objective updates to return to Dras.

Provisional duration: **0.85 seconds**.

The carried kit:

- does not alter movement, jump, damage, firing cadence, or weapon selection;
- remains visible if the final character silhouette can support it cleanly;
- otherwise uses a persistent HUD/objective indicator;
- survives exit to the Overworld and focus loss;
- cannot be dropped; and
- disappears only when deliberately delivered to Dras.

## Trillian berth

Trillian remains distinct from Jane.

If Trillian has been recovered:

- her berth contains her blanket, fitted harness hook, and water bowl;
- she may be present in a calm non-solid rest state while Aryn is aboard;
- she cannot block the hatch, cockpit, bench, or service kit; and
- no interior combat behavior is introduced.

If Trillian has not been recovered:

- the same nook remains readable but empty;
- the harness hook is unused; and
- no dialogue implies that Aryn has already found her.

The berth is an optional continuity reward and never gates the service kit.

## Interior input and combat

- Left and Right move Aryn across the deck.
- Space/JUMP retains its normal action, though no jump is required to reach
  any mandatory interaction.
- Down/interact activates the nearest valid interior prompt.
- Fire and weapon switch are disabled while inside the safe ship.
- Aryn's current weapon ownership and selection remain stored.
- Pause, mute, focus loss, and accessibility settings behave normally.
- Signal Sweep is unavailable inside the ship; the room is too small to
  justify a competing pulse.
- No enemy, damage volume, timer, environmental hazard, or death state is
  present.

Only one prompt may be visible at a time. Interior prompt priority is:

1. service kit when required;
2. ceiling-hatch exit;
3. pack bench;
4. cockpit console; and
5. optional habitation detail.

## Exit sequence

When Aryn activates `▼ EXIT RD-42` beneath the ceiling hatch:

1. she aligns to x 684;
2. the ceiling panels open;
3. recessed access rails lower;
4. she rises into the hatch using a short authored climb or lift-assisted
   motion;
5. the scene hands off while her upper body is already beyond the interior
   ceiling;
6. the exterior resumes with Aryn emerging through the roof;
7. the exterior foreground rim reveals her from the shoulders upward;
8. she steps onto the center roof perch;
9. the hatch closes; and
10. control returns after all held input is released.

The exit places Aryn at:

- center x = `OVERWORLD_ORIGIN_X + 572`;
- feet y = `448 + shipHoverOffset`;
- support = the live center ship surface; and
- facing = her last safe interior facing, unless framing requires a stable
  default.

The player cannot fall through the ship during the handoff.

## Re-entry states

The room can present four states without changing its geometry:

| State | Service kit | Specimen response | Cockpit index |
| --- | --- | --- | --- |
| Arrival exploration | In rack, unavailable | None | Central link disconnected |
| Post-Wound, before failure | In rack, unavailable | Pack bench pulse | Partial match available |
| Service-kit objective | Recoverable | Pack bench pulse | Partial match available |
| After kit recovery | Empty keyed rack | Pack bench pulse | Partial match remains |

Future upgrade, mission-select, store, save, or flight-console functions require
their own approved contracts.

## Camera

### Desktop

- Show the complete 1,672 × 941 plate.
- Keep the whole compact shell visible.
- Do not zoom the room into an implausibly large corridor.
- The arrival camera starts centered on the airlock.
- Optional cockpit and cargo interactions may use restrained horizontal
  emphasis without cutting off the opposite room entirely.

### Portrait mobile

- Support the accepted 360 CSS-pixel floor.
- Start with the hatch, landing zone, and nearest doorway readable.
- Track Aryn horizontally across the shell.
- Clamp the camera to the interior bounds rather than revealing empty world
  beyond the hull.
- Keep prompts, pause, and touch controls clear of safe-area insets.
- Never crop both Aryn and the active interaction out of the same frame.

### Reduced motion

Reduced motion replaces the long physical transfer with:

1. a clear hatch-open pose;
2. a short cyan fade;
3. the interior hatch-open pose;
4. Aryn grounded beneath it; and
5. the hatch closing.

The player still understands that Aryn descended through the top of the ship.

## Visual direction

The production interior derives from Aryn's artwork, the approved exterior,
and the supplied Core OTW palette. The Foundry remains a reference for pixel
density, hard clusters, and gameplay readability only; its dark industrial
palette and pipe-heavy material identity do not carry into the ship.

- `#A0BEF5` light blue, `#91AFB3` teal, and `#EEEEEE` off-white dominate the
  occupied cabin;
- `#6395EE` brand blue supports interactive and identity details;
- `#1B365D` navy and `#3D5255` dark teal define ribs and controlled depth;
- `#1A1C20` ink and `#0A0A0A` void black appear sparingly in seams, the canopy,
  hatch depth, and inaccessible recesses;
- broader quiet panel shapes and less uniform micro-detail than the Foundry;
- faceted ribs and angled bulkheads;
- engine-pod intrusions rather than rectangular hallway walls;
- a dark overhead systems bay that contrasts with the lighter cabin;
- a faithful three-band OTW symbol translated into a small cockpit-bulkhead
  pixel mosaic rather than applied as a UI watermark; and
- crisp pixel-art silhouettes at gameplay scale.

Avoid:

- a bright white generic starship corridor;
- a cavernous hangar;
- multiple unexplained decks;
- perfectly clean showroom surfaces;
- a window larger than the exterior canopy could support;
- baked characters or quest items in the background;
- text that must be read from environmental pixels; and
- visual scale that implies the interior is several times larger than the
  exterior.

## Render order

1. void outside the pressure shell;
2. rear hull and canopy view;
3. rear wall, lighting, and machinery;
4. background furniture and noninteractive cargo;
5. interactive props;
6. rear hatch layers and access rails;
7. Aryn and conditional Trillian;
8. foreground bulkhead ribs;
9. foreground hatch rim and occlusion mask;
10. close emission, particles, and prompts; and
11. HUD and accessibility presentation.

## Asset plan

Every final asset remains scene-scoped and locally installed.

| Asset | Candidate runtime form | Limit |
| --- | --- | --- |
| Interior background | 1,672 × 941 production-v1 plate | Integrated |
| Foreground shell/ribs | 1,672 × 941 alpha plate | One texture below 2,048 px per axis |
| Exterior dorsal hatch | Small gridded animation atlas | Below 2,048 px per axis |
| Interior ceiling hatch | Small gridded animation atlas | Below 2,048 px per axis |
| Aryn descend/emerge | Dedicated gridded sprite atlas | Below 2,048 px per axis |
| Service kit | Small alpha sprite or short atlas | Below 2,048 px per axis |
| Specimen-reactive light | Separate alpha overlay | Scene-scoped |
| Conditional Trillian rest | Reuse or new bounded rest strip | Scene-scoped |
| Aryn armor change | 672 × 672 grid; 36 frames at 112 × 112 | Integrated with flight-suit movement |
| Flight/suit alcove screen | Small alpha animation or foreground layer | Scene-scoped |
| Sealed keel-deck hatch | Rear/floor plate detail | Noninteractive in current chapter |

The exterior ship master remains the identity authority. The dorsal hatch is a
separate hover-linked layer unless a later approved art pass explicitly
updates the normalized ship derivative.

## Scene state and telemetry

The runtime exposes reviewable values:

- `data-scene="rd42-interior"`;
- `data-ship-hatch="closed|prompt|aligning|opening|descending|transition|closing"`;
- `data-ship-hatch-armed="true|false"`;
- `data-ship-interior-state="arrival|post-wound|kit-required|kit-recovered"`;
- `data-ship-service-kit="rack|available|recovering|carried|delivered"`;
- `data-ship-specimen-response="inactive|pulsing"`;
- `data-ship-cockpit-match="locked|partial-match"`;
- `data-ship-trillian-berth="empty|occupied"`;
- `data-ship-suit-alcove="idle|aligning|changing|flight-suit|rearming"`;
- `data-ship-keel-hatch="sealed"`;
- `data-ship-art="production-v1|fallback-greybox"`;
- `data-ship-camera-mode="entry|follow|interaction|exit"`;
- `data-ship-transition-progress`;
- `data-player-supported-by="ship-center-roof|ship-interior-deck"`; and
- `data-pack-upgrade-material`.

The state model must be serializable and must never depend solely on DOM or
Canvas presentation state.

## Lifecycle and recovery

- Focus loss pauses the transition rather than completing it invisibly.
- If the application is suspended mid-transition, restoration resolves to the
  last safe endpoint: exterior roof before entry or interior deck after entry.
- Held movement, Down, fire, and jump actions release before control returns.
- Missing critical interior art shows a retry surface while Aryn remains safe
  on the exterior roof.
- A failed optional cockpit or Trillian asset may degrade without blocking the
  required service-kit path.
- A failed armor-change review asset leaves the cradle inert and Aryn armored.
- A failed flight-suit movement asset also leaves the cradle inert and Aryn
  armored; the runtime never substitutes armored locomotion after a visible
  costume change.
- Audio transition owns at most one ambient loop.
- The ship interior must work offline with installed episode assets.

## Greybox review routes

Recommended isolated routes:

```text
super_frgmnts.html?preview=overworld&scene=ship-entry&autostart=1
super_frgmnts.html?preview=ship-interior&autostart=1
super_frgmnts.html?preview=ship-interior&objective=service-kit&autostart=1
super_frgmnts.html?preview=ship-interior&state=post-wound&trillian=1&autostart=1
```

These are isolated runtime review routes, not claims that the sequence has
joined the production episode path.

## Production-art acceptance

The production plate retains the accepted greybox behavior:

- Aryn can enter only from the live center roof perch;
- Down chooses ship entry instead of Signal Sweep in the hatch range;
- the opening prompt remains suppressed until Aryn deliberately leaves and
  returns;
- Aryn visibly descends through the exterior and interior hatches;
- exterior and hatch layers share the exact hover delta;
- exit restores Aryn to the correct moving support without a fall;
- the required path needs no jump, jet assist, weapon, or companion;
- the service kit cannot be recovered early or twice;
- pre- and post-Wound room states restore correctly;
- desktop and 390 × 844 portrait-mobile framing pass;
- reduced motion preserves the direction and meaning of travel;
- focus loss cannot strand Aryn between scenes;
- no interior input remains latched after transition; and
- critical-asset failure has a visible recovery path.

## Explicitly outside this contract

- a flyable ship;
- moving the exterior ship to another Overworld plate;
- fast travel;
- a permanent save station;
- a store or Galactic Credit spending screen;
- a finished pack-upgrade economy;
- weapon modification;
- shipboard combat;
- unarmored damage, weapon, pack, and hatch-traversal presentation;
- an authored re-arm animation;
- opening or entering the keel service deck;
- enemy invasion of the RD-42;
- Fleet communication;
- voice acting;
- final audio composition; and
- production deployment.
