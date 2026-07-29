# SUPER FRGMNTS // Working Handoff

**Status:** Active development checkpoint

**Updated:** 2026-07-28

**Checkpoint:** The `main` commit containing this file

This is the short-form operating context for future SUPER FRGMNTS work. Use it
with the linked manifests and contracts instead of reconstructing the project
from old tasks, worktrees, or historical branches.

## Canonical source and release path

- Repository: `/Users/rylee/Projects/outsidetheworld`
- Branch: `main`
- Runtime: [`super_frgmnts.html`](../../super_frgmnts.html)
- Design index: [`Design/Super-Frgmnts/README.md`](README.md)
- Production URL:
  `https://outsidetheworld.com/super_frgmnts.html`
- Hosting: GitHub Pages publishes from `main`.
- Rollback tag: `super-frgmnts-pre-blaster-2026-07-23`
  (commit `6b759e8e`)

Only `main` is a source of truth. The Claude worktree
`.claude/worktrees/relaxed-benz` and the old
`codex/tshirt-builder-frgmnts` branch are historical and must not be used for
development or deployment.

A local commit is not a production deployment. Push `main` only after explicit
deployment approval, then verify GitHub Pages and the production URL.

## Product canon

- Game: **SUPER FRGMNTS**
- Season One setting: **Veyra**
- Episode 01: **Arrival on Veyra**
- First subterranean level: **The Shard Foundry**
- Hero: **Aryn Sol-Mavi**, an Interworld Fleet Signal Ranger acting without
  Fleet authorization
- Surface contact: **Dras Ehdre**
- Dras's camp dog: **Jane**
- Aryn's optional surface companion: **Trillian** (separate from Jane)
- Strategic material: **Vesperite**
- Currency: **Galactic Credits**
- Collectibles: **Signal Shards**
- Level exit: **Uplink Gate**
- Coreworks zones: **Foundry**, **Refinery**, **Biolab**, **Deepworks**, and
  **Uplink**

Season One belongs to Veyra: discovery, extermination, economic recovery, and
the Fleet cover-up. The game is designed as an episodic release rather than a
story that must resolve in Episode 01.

## Platform baseline

The production game remains web-first and iOS-ready. Follow
[`IOS-PORTABILITY-BASELINE.md`](IOS-PORTABILITY-BASELINE.md) for input,
lifecycle, asset, save-state, and future PWA/Capacitor decisions.

Important constraints:

- accepted mobile support floor: 360 CSS pixels;
- keyboard, touch, and future controllers must map to shared game actions;
- focus loss must release controls, pause gameplay, and pause audio;
- no intentional frame-rate cap;
- runtime atlases should remain at or below 2,048 pixels per axis unless an
  exception is documented;
- episode-critical installed play must not depend on a network request.

## Current playable flow

1. Title screen and intentional user-gesture audio unlock.
2. Aryn arrives on Veyra standing on her hovering RD-42.
3. The player may travel west into the optional Western Signal Flats to unlock
   Signal Sweep, recover Trillian, fit her field harness, and breach a sealed
   salvage cache. The hawk guides unfinished western assignments.
4. The player traverses the ship, reaches Dras's camp, and completes the
   canonical opening dialogue.
5. A safe calibration lane teaches movement, firing, a shootable credit cache,
   coin recovery, moving platforms, and an electrified platform.
6. Aryn stands on the physical Coreworks surface transport. Its one-shot
   energy vortex locks controls, fades Aryn, and hands off to the Foundry.
7. The Shard Foundry provides eight horizontal plates, three traversal layers,
   two relays, twelve Signal Shards, two curated Deepworks entries, power-ups,
   a non-bypassable three-hit Vesperite lock, fourteen spaced enemies, three
   authored hazard beats, an eight-minute clock, and the Uplink Gate.
8. The completed Uplink Gate freezes and preserves the Foundry run, then opens
   The Wound at a safe portal-bay boss checkpoint.
9. Seam Hunter's death reveals Wound-touched Vesperite. Deliberate Down-input
   recovery completes the beta, fades the stage to black, and automatically
   returns Aryn beside the Coreworks transport with the specimen and loadout
   preserved.

The detailed level contract is
[`UNIFIED-LEVEL-ONE-PLAN.md`](UNIFIED-LEVEL-ONE-PLAN.md). The current population
manifest is
[`Foundry/episode-01-early-beta-v1.json`](Foundry/episode-01-early-beta-v1.json).
The active easy-to-medium placement and playtest contract is
[`Foundry/SHARD-FOUNDRY-LEVEL-DESIGN-v1.md`](Foundry/SHARD-FOUNDRY-LEVEL-DESIGN-v1.md).
The assembled beta route and state-carry contract is
[`EPISODE-01-BETA-PRODUCTION-RUN-v1.md`](EPISODE-01-BETA-PRODUCTION-RUN-v1.md).

## Approved next design direction

The automatic post-Wound surface return is now part of the current playable
flow. The continuation after materialization remains outside it. Its RD-42
boarding and one-plate interior are implemented as isolated review greyboxes:

1. Aryn returns to the surface carrying Wound-touched Vesperite.
2. Dras scans the specimen without taking it and directs Aryn toward the
   Primary Biolab beneath the processing floors already crossed.
3. The specimen participates in a deterministic Coreworks transport overload.
4. Aryn returns to the RD-42 for one phase coupler and two shielded field
   braids.
5. She enters through the top-middle dorsal hatch by pressing Down and
   physically descends into a compact, reusable ship interior.
6. Aryn and Dras repair the transport together before she descends toward the
   Primary Biolab.

The story and staging contract is
[`Post-Foundry/RETURN-TO-DRAS-INTERLUDE-v1.md`](Post-Foundry/RETURN-TO-DRAS-INTERLUDE-v1.md).
The ship behavior and precise greybox layout are
[`Overworld/Phase-3/Ship/Interior/RD42-SHIP-INTERIOR-CONTRACT-v1.md`](Overworld/Phase-3/Ship/Interior/RD42-SHIP-INTERIOR-CONTRACT-v1.md)
and
[`Overworld/Phase-3/Ship/Interior/RD42-SHIP-INTERIOR-WIREFRAME-v1.md`](Overworld/Phase-3/Ship/Interior/RD42-SHIP-INTERIOR-WIREFRAME-v1.md).

## Routes and review URLs

Serve the repository locally:

```sh
python3 -m http.server 8765 --directory /Users/rylee/Projects/outsidetheworld
```

Then use:

- Full entry:
  `http://127.0.0.1:8765/super_frgmnts.html`
- Episode 01 overworld:
  `http://127.0.0.1:8765/super_frgmnts.html?episode=01&stage=overworld&autostart=1`
- Foundry:
  `http://127.0.0.1:8765/super_frgmnts.html?episode=01&stage=foundry&autostart=1`
- Production Wound checkpoint:
  `http://127.0.0.1:8765/super_frgmnts.html?episode=01&stage=wound&autostart=1`
- Production recovery/return QA:
  `http://127.0.0.1:8765/super_frgmnts.html?episode=01&stage=wound&autostart=1&qa=reward`
- Reloadable surface return:
  `http://127.0.0.1:8765/super_frgmnts.html?episode=01&stage=overworld&autostart=1&return=1`
- Overworld review:
  `http://127.0.0.1:8765/super_frgmnts.html?preview=overworld`
- Western assignment review:
  `http://127.0.0.1:8765/super_frgmnts.html?episode=01&stage=overworld&scene=western&assignment=survey&autostart=1`
  (`assignment` accepts `survey`, `trillian`, `harness`, `jump`, `salvage`,
  or `droid`; prerequisite states are prepared without changing the production
  route)
- Transport review:
  `http://127.0.0.1:8765/super_frgmnts.html?preview=overworld&scene=transport&autostart=1`
- Expanded Foundry review:
  `http://127.0.0.1:8765/super_frgmnts.html?preview=foundry-expansion&autostart=1`
- Heavy-rifle review:
  `http://127.0.0.1:8765/super_frgmnts.html?preview=foundry-expansion&weapon=rifle&autostart=1`
- The Wound boss trial:
  `http://127.0.0.1:8765/super_frgmnts.html?preview=wound-boss&autostart=1`
- The Wound post-battle reward review:
  `http://127.0.0.1:8765/super_frgmnts.html?preview=wound-boss&autostart=1&qa=reward`
- RD-42 exterior hatch and continuous descent:
  `http://127.0.0.1:8765/super_frgmnts.html?preview=overworld&scene=ship-entry&autostart=1`
- RD-42 neutral interior:
  `http://127.0.0.1:8765/super_frgmnts.html?preview=ship-interior&autostart=1`
- RD-42 service-kit objective:
  `http://127.0.0.1:8765/super_frgmnts.html?preview=ship-interior&objective=service-kit&autostart=1`
- RD-42 post-Wound/Trillian state:
  `http://127.0.0.1:8765/super_frgmnts.html?preview=ship-interior&state=post-wound&trillian=1&autostart=1`

The historical `scene=portal` transport review URL remains an alias, but new
work should use `scene=transport`.

## Controls

- Left/Right arrows or A/D: move
- Down: interact, board or exit the RD-42, enter Deepworks, or drop through a
  one-way platform
- Space: jump
- X: fire the backpack's telescopic laser seeker
- V: switch between the telescopic laser seeker and recovered heavy-rifle tool
- R: restart
- Touch: analog direction pad plus FIRE, JUMP, and weapon switch controls

Up does not jump. The JUMP action is the only jump input.

## The Wound boss encounter

Seam Hunter is the first-level boss inside **The Wound**. The production route
now enters the same implementation used by the isolated trial, carrying the
Foundry loadout and forcing the recovered heavy rifle ready. The direct route
and isolated trial grant the rifle for review. Seam Hunter retains 50
provisional playtest hit points. His full authored body is vulnerable from
either direction, with no frontal ricochet or special face/rear requirement.
His readable sweep remains damaging only during visible frames, and his
laser-eye attack runs once every five seconds.

The approved v3 room is **2,580 × 1,882 px** with a deck at **y = 1,360**.
Its horizontal structure is:

- portal arrival bay: x = 0–250;
- left construction lift: x = 250–570;
- clear combat runway: x = 570–1,990;
- right construction lift: x = 1,990–2,310;
- Wound threshold: x = 2,310–2,580.

The room retains exactly three continuously moving construction platforms:
one vertical lift on each side and one horizontal gantry above. The wide
background ships as two 1,290 × 1,882 runtime slices to preserve the 2,048 px
texture ceiling. The portal bay is safe until Aryn enters the combat runway or
initiates combat with a shot. Desktop camera framing tracks the midpoint
between Aryn and the living boss. Boss-trial rifle bolts persist for 1.8
seconds and use room-bound culling so they can cross the 1,420 px runway; this
does not settle the rifle's final global range, damage, or ammunition. See
[`Foundry/Boss-Room/WOUND-BOSS-ROOM-BACKGROUND-v3.md`](Foundry/Boss-Room/WOUND-BOSS-ROOM-BACKGROUND-v3.md)
and
[`Foundry/Boss-Room/Construction-Lifts/WOUND-CONSTRUCTION-LIFT-KIT-v2.md`](Foundry/Boss-Room/Construction-Lifts/WOUND-CONSTRUCTION-LIFT-KIT-v2.md).

The isolated trial now carries a provisional pursuit-and-elevator rhythm.
Seam Hunter aggressively tracks Aryn across the main deck, closing far gaps
at 160 px/s, transitioning through 108 px/s, and slowing to 72 px/s near
attack range. His velocity ramps instead of snapping. Aryn must remain behind
him for 0.16 seconds before he starts a 0.7-second turn; he brakes, flips once,
then commits forward for 0.55 seconds before reconsidering. His body remains
solid.
Reaching 190 px above the deck for 0.25 seconds breaks his tracking and causes
1.6 seconds of visible confusion; if Aryn remains upstairs, he searches
slowly without reading her live position or attacking. Descending restores
pursuit and rearms the elevator escape. The trial rifle cycles every 0.30
seconds rather than 0.46 seconds. Blind-search edge turns are
direction-sensitive, preventing rapid facing oscillation at either lift.
Laser charge captures one deck target, telegraphs a locked downward
11.5–35.5° path, and fires a single thick diagonal beam with matching damage;
it does not track after commitment or operate while Seam Hunter is confused.
The first active beam frame triggers a 12-frame cosmetic red-plasma deck
impact with no additional hitbox.

The shaft boundary now uses the approved hybrid sentry response. Seam Hunter
plants instead of walking fruitlessly into an elevator opening, withdraws
210 px into the combat lane, and guards the shaft. If Aryn stays outside the
lane, he uses the normal five-second, downward-only laser cadence from that
guard position; re-entering the lane restores pursuit. When Aryn is above him
on the horizontal gantry, a dedicated 16-frame, 1.216-second rise leads into
a held upward stare. The motion is fully authored in the sprite and requires
no programmatic body tilt. He plants without attacking and tracks Aryn left
or right using a 110 px deadzone and 0.42-second facing confirmation,
preventing rapid flips as the gantry crosses his center. Descending restores
pursuit. A confirmed tracking change now plays a curated 19-frame,
1.406-second in-place turnaround through a frontal silhouette rather than
flipping the held pose instantly. The same authored sequence mirrors for the
opposite direction and remains non-damaging. See
[`Foundry/Boss-Room/Shaft-Sentry/SEAM-HUNTER-SHAFT-SENTRY-v1.md`](Foundry/Boss-Room/Shaft-Sentry/SEAM-HUNTER-SHAFT-SENTRY-v1.md).
Lift confusion and the horizontal-gantry watch use separate latches: becoming
hidden on a vertical lift no longer consumes the watch when Aryn transfers to
the upper gantry. Descending to the main deck rearms both reactions.

While Aryn is supported by the horizontal gantry, the vertical camera lowers
into a dual-character composition: Aryn remains in the upper quarter while
Seam Hunter and the main deck stay visible below. Normal deck framing is
unchanged, and portrait framing uses a separate safe upper anchor. The
developer-only `qa=sentry` variant starts Aryn on the moving gantry for this
pose and camera review.

These are playtest values, not final combat balance or a global rifle
decision.

The heavy-rifle projectile now uses a longer gold discharge with a white-hot
core, broken cyan/gold wake pixels, and localized muzzle and impact sparks.
The treatment is cosmetic: cadence, damage, collision point, speed, and
boss-trial lifetime are unchanged.

Seam Hunter now has a dedicated 25-frame death sequence lasting 2.675 seconds.
The lethal hit cancels pursuit, melee, laser, collision, and further damage
without stopping Aryn or the construction platforms. A cosmetic deck impact
lands on frame 13. Wound access waits for the final frame, while encounter
completion waits for the later material recovery. Measured per-frame bottom
padding keeps the collapsed body physically on the deck instead of hovering.
See
[`Foundry/Boss-Room/Seam-Hunter-Death/SEAM-HUNTER-DEATH-v1.md`](Foundry/Boss-Room/Seam-Hunter-Death/SEAM-HUNTER-DEATH-v1.md).

The final death frame opens a short playable epilogue instead of ending the
encounter immediately. The corpse holds for 1.4 seconds, darkens into a
near-black silhouette over 1.05 seconds, and disappears over a 0.9-second
fade. A unique violet-and-electric-blue Vesperite specimen is revealed at the
boss's captured resting place during that fade; the separate construction
cradle has been removed. The mission timer freezes throughout the aftermath
and approach, while all three construction platforms continue moving. Within
the transition, the camera centers the corpse; afterward, it frames Aryn and
the specimen together whenever both can fit, including portrait/mobile play.
Within 118 px on the main deck, the shared Down/interact action and the touch
stick's downward gesture show and activate `▼ RECOVER`. The specimen then
contracts toward Aryn's backpack and is stored as future pack-upgrade
material. The isolated route shows its completion card. The production route
instead applies the final score bonuses, fades fully to black, and returns
Aryn to the surface with the specimen serialized as pack material. It does
not immediately change the pack, weapons, jump, stats, or abilities. The
current descriptive runtime label is **Wound-touched Vesperite**; it may be
renamed later. See
[`Foundry/Boss-Room/Wound-Vesperite/WOUND-TOUCHED-VESPERITE-v1.md`](Foundry/Boss-Room/Wound-Vesperite/WOUND-TOUCHED-VESPERITE-v1.md).

Crossing x = 670 now begins a 6.35-second, fully skippable **MAIN ENCOUNTER //
SEAM HUNTER** announcement on every attempt. Aryn and Seam Hunter lock while
the lifts, upper gantry, and environmental motion continue; the mission clock
does not advance. Enter, numpad Enter, controller Start/Options, or the visible
safe-area-aware touch Skip control dismisses it. Held movement never skips the
announcement. The supplied transparent title and four 48 kHz stereo cues are
integrated without changing combat balance. See
[`Foundry/Boss-Room/Announcement/WOUND-BOSS-ANNOUNCEMENT-v1.md`](Foundry/Boss-Room/Announcement/WOUND-BOSS-ANNOUNCEMENT-v1.md).

Seam Hunter, his name, and his health bar remain concealed through the empty
approach and the complete announcement, preventing wide desktop framing from
spoiling his reveal. Once the words and darkness clear, the approved
120-second **Subterranean Apex** score begins at increased volume and Seam
Hunter materializes over 1.2 seconds. Gameplay and the health bar wait until
he is fully visible. Skipping starts the same score immediately; victory,
loss, and retry return to the Foundry score. See
[`Foundry/Boss-Room/Music/WOUND-BOSS-MUSIC-v1.md`](Foundry/Boss-Room/Music/WOUND-BOSS-MUSIC-v1.md).

## Current equipment and world systems

- Aryn's backpack is her persistent power-up chassis. Its telescopic laser
  seeker is her only always-carried self-defense weapon and is available on
  every route, including the Overworld.
- The seeker attracts shots toward hostile targets and repels their course
  away from nearby friendlies such as Dras, Jane, and the Outpost worker
  droid; friendly safety wins when those behaviors conflict.
- Aryn has no stomp or contact-damage attack. Touching a hostile damages her;
  living enemies are defeated with the seeker or a recovered heavy rifle.
- Aryn's unassisted jump has one consistent launch height. Higher traversal
  requires the backpack's jet-assist module.
- The heavy rifle is a recoverable special weapon for Vesperite route
  clearing, boss killing, and heavy combat. It supports draw, ready,
  stationary firing, running firing, airborne firing, and holster timeout
  states.
- The heavy rifle destroys mandatory Vesperite obstructions in three hits.
- Rifle ammo, seeker overheat, seeker range and projectile lifetime, backpack
  range-versus-damage scaling, boss hit counts, and any additional weapon
  mechanic remain open decisions. Existing runtime values are provisional
  playtest behavior, not settled canon.
- The jet-assist pickup improves vertical traversal.
- Credit caches burst physical coins; credits persist across the
  overworld-to-Foundry handoff.
- Jane is a non-solid terrain-aware Overworld actor who wanders, sniffs,
  watches, approaches, and returns home without entering the transport deck.
- **Trillian**, the player's dog, has separate unarmored and armored movement
  states plus an armored energy-lunge attack and powered-jump launch cue.
  Trillian is not Jane. Her optional Overworld surface loop is live: she waits
  in Western Signal Flats, follows after recovery, switches gait when the
  field harness is fitted, uses the authored charge/launch cue with a
  physics-driven vertical arc, and performs the energy lunge only against a
  sealed salvage cache. The lunge has no combat damage, Trillian never enters
  enemy targeting, and she stops before the Coreworks transport. Foundry
  handoff, combat targeting, hurt, incapacitated, recovery, and damage balance
  remain unimplemented. The clipped 25-frame rear/power-up alternate remains
  review-only and is not used as an airborne or landing continuation.
- The non-solid, non-hostile Outpost worker droid drifts above the ground near
  the abandoned credit terminal, periodically descends into a secondary
  maintenance animation, and offers an optional post-contact service task.
- One non-hostile, non-solid, non-targetable hawk makes occasional passes
  through the Overworld sky, alternating direction after every pass. Its
  25-frame source atlas is preserved, while runtime uses a curated 16-frame
  cadence that removes near-duplicate wings-up holds at the loop boundary. It
  circles above the next unfinished western assignment while that target is on
  screen. It never enters enemy or seeker-targeting data.
- The Overworld is now four 1,672 × 941 plates (6,688 pixels wide). Western
  Signal Flats is prepended at x=0; the original Landing Flats, Dras Outpost,
  and Coreworks Threshold retain their sequence with a +1,672-pixel runtime
  origin offset. All five new assignments are optional and untimed, and none
  gates the Foundry.
- Signal Sweep uses the shared Down/interact action away from closer
  interactions, emits a non-damaging radial pulse, and points to the nearest
  unfinished optional surface assignment.
- Atmospheric stabilizers restore room machinery and gate progression.
- Pause, mute, focus-loss audio, control cancellation, touch-callout
  suppression, and mobile camera compensation are active.

## Episode 01 enemy catalog

The beta roster contains these 13 cataloged families:

| Runtime type | Working name | Role |
| --- | --- | --- |
| `crawler` | Ridge Skitter | Fast ground crawler |
| `walker` | Clacker Beetle | Ground patrol |
| `flyer` | Spore Wisp | Legacy airborne hazard |
| `squircle` | Squircle Minion | Surface-crawling platform enemy |
| `mite` | Vesper Mite | Ground-traveling scuttler; it does not fly |
| `wasp` | Ember Wasp | Fast flying insect |
| `gaunt` | Seam Hunter | Four-hit tall stalker |
| `patroller` | Chitin Sentinel | Five-hit armored patrol |
| `fragmentSpring` | Spring Fragment | Small fast airborne Fragment |
| `fragmentBastion` | Bastion Fragment | Two-hit heavy Fragment |
| `coreLeech` | Core Leech | Two-hit hovering parasite |
| `vesperFlare` | Vesper Flare | Two-hit fast thermal flyer |
| `paleWatcher` | Pale Watcher | Three-hit Uplink ground guard |

Additional intake assets are not part of the 13-family beta population:

| Runtime type | Working name | Status |
| --- | --- | --- |
| — | Geemer | Source-only ground-and-platform walker |
| `skree` | Skree | Runtime-ready ground patrol; not spawned |
| `sova` | Sova | Runtime-ready ground crawler; not spawned |
| `gloamRoller` | Gloam Roller | Runtime-ready crawl-to-roll ground patrol; not spawned |
| `seamLurker` | Seam Lurker | Runtime-ready ceiling patrol; drop attack absent; not spawned |
| `kihunter` | Kihunter | Runtime-ready flying patrol; not spawned |

Raw masters and runtime manifests live under
`Design/Super-Frgmnts/Foundry/Enemies/`. Normalized shipping atlases live under
`Images/Game/Super-Frgmnts/`.

## Current checkpoint package

The commit containing this handoff adds or finalizes:

- the complete Arrival → Overworld → Foundry → Wound → Vesperite recovery →
  surface beta-production route;
- the state-preserving Uplink boss checkpoint and automatic black surface
  return;
- the physical Coreworks surface transport, including 36-frame idle and
  25-frame activation atlases;
- the Core Leech, Vesper Flare, and Pale Watcher runtime families;
- production population and preloading for the complete 13-family catalog;
- ground-patrol physics and naming for the Vesper Mite;
- build scripts, manifests, review GIFs, and feature verifiers for the new
  assets;
- updated arrival, beta, roster, and Vesper Mite contracts.

The transport sources and reviews are in
`Design/Super-Frgmnts/Overworld/Coreworks-Transport/`. Regenerate derivatives
with `tools/build_super_frgmnts_coreworks_transport.py`; do not hand-edit the
runtime atlases.

The three new enemy derivatives are generated by
`tools/build_super_frgmnts_catalog_enemies.py`.

## Verification levels

During focused development, run the verifier for the system being changed and
review the relevant desktop and 390 × 844 portrait route.

The assembled production run is checked with:

```sh
python3 tools/verify_super_frgmnts_production_run.py
```

The isolated ship-interior contract is checked with:

```sh
python3 tools/verify_super_frgmnts_rd42_interior.py
```

Before a commit intended for deployment, run every SUPER FRGMNTS contract:

```sh
for test in tools/verify_super_frgmnts_*.py; do
  python3 "$test" || exit 1
done
git diff --check
```

Also check the single inline JavaScript block with `node --check`, then perform
one desktop and one portrait-mobile browser run with no console errors or
missing critical artwork. A production deployment additionally requires a
direct check of the live GitHub Pages URL.

## Deliberately deferred

- final combat damage and credit economy; the first-level placement candidate
  remains subject to its documented desktop and portrait playtest gate;
- timer awards from atmospheric relays; the active beta still starts at eight
  minutes;
- the between-level Galactic Credit store and start-of-next-level purchases;
- email gating and the proposed one-time $5 web purchase;
- PWA packaging, TestFlight, and the Capacitor iOS shell;
- full separation of the monolithic HTML runtime into game-core, content,
  platform-service, and presentation modules;
- replacement art for the provisional Refinery, Biolab, and Uplink upper
  plates;
- split versions of the two documented 2,816-pixel Vesperite animation strips.

Do not implement these merely because they are listed. Treat each as its own
approved, bounded task.

## Working discipline

- Keep one gameplay system or asset family per task whenever practical.
- Batch new asset intake before integration.
- Preserve raw masters under `Design/`; ship only normalized derivatives from
  `Images/` and `Audio/`.
- Update this handoff whenever canon, routes, controls, architecture, or the
  production checkpoint materially changes.
- Never deploy from a worktree or historical branch.
