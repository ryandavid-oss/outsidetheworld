# SUPER FRGMNTS Playtest Matrix

**Audit date:** 2026-07-29

**Primary browser size:** 1,280 × 720 at DPR 2

**Legend:** Pass, Fail, Partial, Blocked, N/A

The full campaign was exercised as adjacent real-UI scene checkpoints. The
Wound-to-chapter ending was played continuously. Every Foundry plate was
loaded and inspected, but all collectibles were not manually retraversed in
one uninterrupted eight-plate run.

| Feature or scenario | Exact test performed | Expected behavior | Actual behavior | Status | Issue reference | Fix reference | Retest result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Canonical title initial render | Opened `/super_frgmnts.html` on a fresh local origin and waited through critical art load | Load Game overlay and animated title remain live | Baseline threw twice in `drawHazards()` and ended the only frame loop | Pass after fix | P0-01 | Guard telemetry export when `hazard.id` is absent | Title loaded with selected desktop art and no throw-driven freeze |
| Load Game audio handshake | Clicked Load Game from the canonical title | Unlock audio once and expose Begin Episode | Signal overlay closed; title action focused; no duplicate audio elements | Pass | — | — | Same result after fix |
| Begin Episode | Clicked Begin Episode and allowed the atmospheric bridge to complete | Start the Episode 01 Arrival scene | Baseline drew once then froze; final worker telemetry changed across two 650 ms samples | Pass after fix | P0-01 | Legacy-hazard render guard | Arrival simulation advances |
| Rapid title confirmation | Activated the only title action and observed disabled/launching state during the bridge | One transition, no duplicate scene start | One bridge and one Arrival scene; no duplicated canvas/audio | Pass | — | Existing button/state guards | Pass |
| Title options | Inspected all title actions and keyboard/pointer semantics | Every implemented option is reachable | Beta 2 exposes Load Game and Begin Episode only; both worked | Pass | — | — | Pass |
| Continue valid save | Inspected UI, storage use, and route logic | Applicable only if Continue exists | No save-slot or Continue feature exists in this beta | N/A | — | — | N/A |
| Continue without/with malformed save | Inspected UI, storage parsing, and storage keys | Invalid saves must not crash if feature exists | Only sound preference and Episode credit count persist; no Continue parser exists | N/A | — | — | N/A |
| Arrival bridge skip/natural completion | Began Episode, observed bridge, and allowed it to auto-complete after a skip-button timing attempt | Exactly one Arrival handoff | One Arrival scene loaded; no repeated handoff | Pass | — | — | Pass |
| Arrival dialogue: Keep Listening | Direct dialogue review route; clicked Skip, then Keep Listening | Confirmation closes and dialogue resumes | Dialogue returned to the current card and remained interactive | Pass | — | — | Pass |
| Arrival dialogue: Skip Scene | Reopened Skip confirmation and clicked Skip Scene | Finish dialogue and restore gameplay safely | Gameplay resumed with transport charging state and no overlay | Pass | — | — | Pass |
| Coreworks transport | Direct transport route; waited for activation and clicked Enter Foundry | One vortex sequence followed by Foundry | Canonical Foundry URL and running scene loaded | Pass | — | — | Pass |
| Coreworks Start Over | From transport-ready message clicked Start Over | Reset and replay activation | Activation restarted cleanly and reached ready state again | Pass | — | — | Pass |
| Foundry room 0 | Loaded `qa=room&room=0`, clicked Load Game, inspected spawn/telemetry | Grounded Foundry plate, valid population | Grounded x138; Foundry zone; 16 enemies, 2 hazards, 1 route lock | Pass | — | — | Pass |
| Foundry room 1 | Loaded `qa=room&room=1` | Grounded Foundry plate, valid population | Grounded x2350; Foundry zone; counts stable | Pass | — | — | Pass |
| Foundry room 2 | Loaded `qa=room&room=2` | Grounded Refinery plate, valid population | Grounded x4102; Refinery zone; counts stable | Pass | — | — | Pass |
| Foundry room 3 | Loaded `qa=room&room=3` | Grounded Refinery plate, valid population | Grounded x5774; Refinery zone; counts stable | Pass | — | — | Pass |
| Foundry room 4 | Loaded `qa=room&room=4` | Grounded Biolab plate, valid population | Grounded x7446; Biolab zone; counts stable | Pass | — | — | Pass |
| Foundry room 5 | Loaded `qa=room&room=5` | Grounded Biolab plate, valid population | Grounded x9118; Biolab zone; counts stable | Pass | — | — | Pass |
| Foundry room 6 | Loaded `qa=room&room=6` | Grounded Uplink plate, valid population | Grounded x10790; Uplink zone; counts stable | Pass | — | — | Pass |
| Foundry room 7 | Loaded `qa=room&room=7` | Grounded Uplink plate, valid population | Grounded x12462; Uplink zone; counts stable | Pass | — | — | Pass |
| Complete manual eight-plate traversal | Inspected every plate entry and route contract; did not manually recollect every objective in one run | All required routes reachable | Room spawns and contract geometry pass; uninterrupted collectible run not completed | Partial | Measurement limitation | — | Static traversal contract and all plate spawns pass |
| Deepworks routes | Reviewed collision/reachability contracts and Deepworks-enabled room data | Required and optional lower routes are reachable with jet assist | Geometry contract passes; full manual lower-route traversal not completed | Partial | Measurement limitation | — | Existing reachability verifier passes |
| Moving platforms | Observed Wound lifts/gantry for multiple minutes and sampled rounded positions | Continuous bounded movement without frozen state | Baseline 222 changes/3.002 s; isolated final 352/3.000 s | Pass | — | — | No stall over 17 ms in final proxy |
| Pause/resume | In running Foundry clicked Pause, waited 1.3 s, clicked Resume | Timer and simulation freeze, then continue | Timer stayed at 01:30 and resumed decrementing | Pass | — | Existing pause state | Pass |
| Pause while moving | Paused during an active Foundry scene with enemies/platforms running | Controls release and world stops | Timer/world state held; controls were reset | Pass | — | Existing control release | Pass |
| Pause on exact damage/completion frame | Reviewed state guards; exact-frame pointer injection was not available | No competing pause/damage/completion state | Death/completion collision is covered separately; exact pause collision not injected | Partial | Measurement limitation | P2-01 state guard helps ordering | Outstanding automated case |
| Foundry restart repetition | Clicked Restart 20 times; sampled cycles 1/5/10/15/20 | Clean reset without growth or stale state | Timer 08:00, 16 enemies, 2 hazards, 1 canvas, 2 audio elements every sample | Pass | — | — | Pass |
| Damage and death | Episode-only `qa=death`; one-hit player spawned in an active thermal hazard | Authored death then Retry | Five empty hearts and `Death becomes you` after each run | Pass | — | Deterministic QA seam | Pass |
| Death→respawn repetition | Initial death plus 19 Retry actions | Twenty clean deaths and resets | All 20 completed; DOM/audio counts stayed stable | Pass | — | Deterministic QA seam | Pass |
| Fire during lost state | Clicked Fire after cycle 20 while loss message was visible | No projectile/state escape | Loss message remained visible and state did not restart | Pass | — | Existing `state` guard | Pass |
| Fatal damage plus completion | Loaded `qa=completion-collision`: 12 shards, 2 relays, cleared lock, one-hit player in active gate hazard | Death wins; no next-scene transition | Remained on Foundry URL with active hazard and death screen | Pass | P2-01 | `checkUplink()` running-state guard | Pass |
| Foundry completion repetition | Used deterministic Wound reward checkpoint to exercise the completion handoff ten times | One surface return per recovery | Ten full recoveries reached canonical surface-return URL | Pass | — | — | Pass |
| Wound safe bay/threshold | Direct Episode Wound; clicked Load Game and moved right with the real touch pad | Safe start, then one boss announcement | Safe bay held; threshold triggered exactly one announcement | Pass | — | — | Pass |
| Boss intro controls | Observed full announcement; reviewed Enter/Start/Skip paths | Timer/combatants lock while platforms move; explicit skip available | Construction moved; combat and timer held; Skip control present | Pass | — | — | Pass |
| Sustained heavy-rifle fire | Fired 50 shots at approximately 315–320 ms intervals | Bounded cadence, valid damage, no runaway state | Boss health moved 50→0; every intended shot hit; no DOM/audio growth | Pass | — | — | Pass |
| Boss death/aftermath | Waited through authored collapse, corpse hold, dissolve, and reward reveal | Passage/reward unlock only after death sequence | Correct 25-frame collapse and delayed material reveal | Pass | — | — | Pass |
| Reward recovery | Moved into range and dragged touch pad down | Store Wound-touched Vesperite and lock transition | Stored flag became true; black surface transition started | Pass | — | — | Pass |
| Ten surface-return transitions | Repeated reward route, real Down gesture, and waited through each URL handoff | Ten independent Overworld return states | Cycles 1–10 each ended at `stage=overworld&return=1`; final DOM 1 canvas/2 audio | Pass | — | — | Pass |
| Post-Wound transport lock | Inspected returned surface after recovery | Transport remains sealed | Status reported transport offline/sealed and did not reactivate | Pass | — | — | Pass |
| Dras return report | Moved left to Dras and advanced all R01–R31 cards | Complete report, then cliffhanger | All 31 cards advanced to Close chapter | Pass | — | — | Pass |
| Chapter One close | Clicked Close chapter, then Return to Veyra/Skip transition | Stable chapter-complete state | Cliffhanger completed with Primary Biolab hook | Pass | — | — | Pass |
| RD-42 flight-suit change | Direct interior; moved to suit cradle and pressed Down | Authored suit transition and flight-suit state | Flight suit became active after approximately 2.95 s | Pass | — | — | Pass |
| RD-42 flight-suit jump | Clicked Jump after suit change | Higher suit jump and clean landing | y744→599 and returned grounded at y744 | Pass | — | — | Pass |
| RD-42 armor-gated hatch | Approached hatch in flight suit and pressed Down | Hatch refuses non-field armor | `FIELD ARMOR REQUIRED. HATCH LOCKED`; remained inside | Pass | — | — | Pass |
| RD-42 re-arm and exit | Returned to cradle, re-armed, recovered service kit, used hatch | Restore armor, keep kit, emerge outside | Command Rest/seeker restored; kit carried; exterior scene loaded | Pass | — | — | Pass |
| Pack-bench wrong interaction | Pressed Down at nearby pack bench before kit | Non-objective station must not grant kit | Unknown Material remained locked; objective unchanged | Pass | — | — | Pass |
| Touch controls | Used real direction-pad drag for movement, threshold entry, interaction, and ten reward recoveries | No stuck control; correct left/right/down actions | Movement and Down interactions were reliable | Pass | — | Existing centralized release | Pass |
| Keyboard controls | Title keyboard semantics and source contracts inspected; full held-key traversal was not available through this browser control surface | Arrow/A/D, Space, X, V, R behave as documented | Contracts and UI semantics pass; extended physical keyboard play not completed | Partial | Measurement limitation | — | Needs automated key-hold case |
| Opposing held movement | Could not inject simultaneous held left/right through the connected control surface | Deterministic neutral or documented priority | Shared state/direction code inspected only | Blocked | Tool limitation | — | Add browser keydown test |
| Focus loss while moving | Reviewed baseline handlers and frame gate; browser-created tabs did not transfer native focus | Controls/audio release and simulation freezes | Baseline code would continue visible unfocused simulation; fixed code gates focus | Partial | P2-02 | `runtimeFocused` lifecycle gate | Static verifier passes; native OS retest outstanding |
| Hidden/background tab | Reviewed visibility handler and delta reset; parked completed tabs on `about:blank` | No updates or huge resume delta | Hidden path resets controls/audio/frame time; no large-jump defect found | Partial | Tool limitation | Existing plus P2-02 lifecycle code | Needs native visibility timing trace |
| Resize/orientation | Requested desktop and 390×844 portrait capabilities; inspected resize contracts | Canvas coordinates remain valid and nearest-neighbor | Browser remained 1280×720 despite accepted request | Blocked | Tool limitation | — | Static responsive verifier passes |
| Reload during transition | Reloaded canonical scene URLs and repeated transitions; did not hit the exact blackout frame | Reloadable URL yields coherent scene | Canonical scene URLs reloaded correctly | Partial | Tool timing limitation | Existing history routing | Exact blackout reload outstanding |
| Audio gesture policy | Loaded fresh pages before and after clicking Load Game | No audio before gesture; one reusable audio system afterward | Explicit signal gate remained; 2 music elements across cycles | Pass | — | Existing audio director | Pass |
| Mute persistence | Started with stored Sound: Off preference and launched scenes | Preference remains consistent; gameplay unaffected | Sound Off persisted and scenes continued without stacking | Pass | — | Existing local storage | Pass |
| Gamepad | Inspected code and canonical documentation; no hardware available | Only boss Start skip is claimed | Mapping exists; full controller support is future scope | Partial | Hardware limitation | — | Hardware retest needed |
| Asset path/case | Extracted all unique image/audio paths and exact-case checked filesystem | Every referenced asset resolves outside case-insensitive macOS assumptions | 119/119 present with exact case | Pass | — | — | Pass |
| Critical asset failure | Inspected timeout/retry contract; did not intentionally corrupt an asset | In-page Retry Load instead of silent failure | Source contract passes; destructive/missing-asset scenario not induced | Partial | Test limitation | Existing retry UI | Add request-failure browser test |
| Title route request selection | Fresh port server log at desktop title | Request only selected desktop art; no boss art | Portrait and boss requests absent; boss `src` null | Pass | P2-03 | Runtime responsive/scene source assignment | Pass |
| Wound boss-title request | Direct Wound route after loading fix | Wound title still loads at authored size | 1,400×320 image loaded | Pass | P2-03 | Wound-only source assignment | Pass |
| Return to title | Inspected available production UI and history behavior | Only test where supported | No in-game Return to Title button is currently exposed; popstate title configuration exists | N/A | — | — | N/A |

## Uncovered cases to automate next

- A contiguous title→Arrival→Overworld→all Foundry objectives→Wound→surface
  run with no direct scene checkpoint.
- Native desktop blur/focus and actual hidden/visible transitions while holding
  movement.
- True 390 × 844 portrait play, rotation during gameplay, and mobile Safari
  safe-area behavior.
- Simultaneous opposing keyboard inputs and keys held across a scene change.
- Pause on the same frame as damage and pause on the same frame as completion.
- Reload during the black transition and during the boss announcement.
- Deepworks required and optional routes under real movement.
- Missing image/audio request injection and Retry Load behavior.
- Gamepad Start on physical hardware.
