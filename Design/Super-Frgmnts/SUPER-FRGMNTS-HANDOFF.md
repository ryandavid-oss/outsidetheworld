# SUPER FRGMNTS // Working Handoff

**Status:** Active development checkpoint

**Updated:** 2026-07-27

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
3. The player traverses the ship, reaches Dras's camp, and completes the
   canonical opening dialogue.
4. A safe calibration lane teaches movement, firing, a shootable credit cache,
   coin recovery, moving platforms, and an electrified platform.
5. Aryn stands on the physical Coreworks surface transport. Its one-shot
   energy vortex locks controls, fades Aryn, and hands off to the Foundry.
6. The Shard Foundry provides eight horizontal plates, three traversal layers,
   two relays, twelve Signal Shards, power-ups, destructible Vesperite,
   enemies, an eight-minute clock, and the Uplink Gate.

The detailed level contract is
[`UNIFIED-LEVEL-ONE-PLAN.md`](UNIFIED-LEVEL-ONE-PLAN.md). The current population
manifest is
[`Foundry/episode-01-early-beta-v1.json`](Foundry/episode-01-early-beta-v1.json).

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
- Overworld review:
  `http://127.0.0.1:8765/super_frgmnts.html?preview=overworld`
- Transport review:
  `http://127.0.0.1:8765/super_frgmnts.html?preview=overworld&scene=transport&autostart=1`
- Expanded Foundry review:
  `http://127.0.0.1:8765/super_frgmnts.html?preview=foundry-expansion&autostart=1`
- Heavy-rifle review:
  `http://127.0.0.1:8765/super_frgmnts.html?preview=foundry-expansion&weapon=rifle&autostart=1`

The historical `scene=portal` transport review URL remains an alias, but new
work should use `scene=transport`.

## Controls

- Left/Right arrows or A/D: move
- Down: interact, enter Deepworks, or drop through a one-way platform
- Space: jump
- X: fire
- V: switch between the pack emitter and recovered heavy rifle
- R: restart
- Touch: analog direction pad plus FIRE, JUMP, and weapon switch controls

Up does not jump. The JUMP action is the only jump input.

## Current equipment and world systems

- Pack emitter supports seeking fire, heat, and overheat behavior.
- Heavy rifle is a recoverable alternate weapon with draw, ready, stationary
  firing, running firing, airborne firing, and holster timeout states.
- The heavy rifle destroys mandatory Vesperite obstructions in three hits.
- The jet-assist pickup improves vertical traversal.
- Credit caches burst physical coins; credits persist across the
  overworld-to-Foundry handoff.
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

Raw masters and runtime manifests live under
`Design/Super-Frgmnts/Foundry/Enemies/`. Normalized shipping atlases live under
`Images/Game/Super-Frgmnts/`.

## Current checkpoint package

The commit containing this handoff adds or finalizes:

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

- final enemy density, damage, pickup economy, and difficulty balance;
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
