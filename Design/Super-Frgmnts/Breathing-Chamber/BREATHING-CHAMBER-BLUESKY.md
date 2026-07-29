# SUPER FRGMNTS // The Breathing Chamber

## Signature sentence

**The room is a one-way fall that becomes an ascent when it breathes.**

The Breathing Chamber is the second Foundry plate and the first major
environmental set piece of Episode 01. Aryn enters near its ceiling, descends
through a dead industrial lung, restores the atmospheric stabilizer at the
bottom, and uses the machinery she awakened to climb back through a transformed
room.

This is not another platform route. It is the first time the player should feel
that Aryn has changed Veyra.

## What the room must accomplish

- Deliver the height and spatial memory of a classic tall exploration room.
- Teach that dropping is easy, while returning requires understanding the
  environment.
- Make atmospheric restoration visible across an entire plate.
- Give the two wall fans, conduits, lamps, freight machinery, haze, and
  stabilizer a shared purpose.
- Reuse the same volume in two mechanically different directions.
- End the Foundry with a meaningful upward escape into the Refinery.
- Remain readable and forgiving on a 360–390 px portrait phone.

## Blue-sky directions considered

### A // Vertical Lungs

Restoration creates wind columns that lift Aryn directly through the room.

Strengths:

- immediate and spectacular;
- ties restoration directly to movement;
- visually easy to understand.

Risks:

- wall-mounted fans do not naturally imply vertical thrust;
- air steering may become imprecise on mobile;
- a long automatic lift can reduce player agency.

### B // Pressure Organ

The fans pulse in alternating rhythms, moving shutters and temporary bridges.

Strengths:

- strong industrial personality;
- room feels like a musical machine;
- supports later mastery and optional routes.

Risks:

- timing complexity arrives too early in Episode 01;
- visual rhythm can become frustrating rather than wondrous;
- moving geometry would compete with the camera and touch controls.

### C // The One-Way Fall / Powered Ascent

Aryn descends through dormant machinery. Restoration starts the wall fans,
clears the haze, illuminates the conduits, and awakens a full-height freight
lift that carries her back toward the upper exit.

Strengths:

- clean cause and effect;
- preserves manual platforming;
- lets the player see the room twice in different emotional states;
- exploits the existing drop-through mechanic;
- uses a freight lift already present in the room’s vocabulary;
- creates a memorable return journey without requiring new combat systems.

This is the selected direction.

## Emotional arc

### 1 // Promise

Aryn enters on the upper-left cross tier. Across the chamber, the Refinery exit
is visible but unreachable. The player can see:

- two enormous dormant wall fans;
- a dead freight-lift rail disappearing into the depths;
- cyan conduits with no current;
- the silhouette of the stabilizer far below;
- a faint magenta contamination layer descending through the shaft.

The room silently asks: **How will I ever get back up?**

### 2 // Surrender

The route downward is intentionally easier than the route upward. Down presses
let Aryn commit to the descent through one-way catwalks. Platforms grow sparser,
the ceiling recedes, and the camera begins to reveal the stabilizer.

This descent should feel deliberate rather than accidental.

### 3 // Contact

At the main deck, the stabilizer occupies the far-right machinery bay. The
containment threshold beyond it is locked. The freight lift is parked nearby,
dark and inert.

The player has reached a genuine dead end.

The existing deck-level Foundry/Refinery transition is retired in this room.
That boundary becomes a sealed service bulkhead, not an alternate exit. Even
after restoration, walking right from the stabilizer cannot bypass the return
ascent. The actual Refinery transition lives at the upper-right cross tier.

### 4 // Breath

Restoration is a room-scale performance:

1. Aryn engages the interface.
2. Amber service lights answer near the stabilizer.
3. A power pulse travels upward through the deck conduit.
4. The first fan coughs and begins turning.
5. The second fan joins at a slightly different phase.
6. Magenta haze is pulled toward the vents.
7. The freight-lift rail illuminates from bottom to top.
8. The lift rises for the first time.
9. The upper containment threshold unlocks.

The room should not become clean or cheerful. It becomes functional.

### 5 // Ascent

The freight lift now cycles from the main deck to the lower edge of the
mid-gantry. Aryn rides it upward but retains control. She may:

- remain aboard for the intended route;
- jump to optional intermediate decks;
- drop back down without creating a softlock;
- use the moving platform as a second chance after a missed jump.

The last three jumps return her to the right-hand upper catwalk. From there she
crosses the restored threshold into the Refinery.

### 6 // Memory

At the room boundary, the camera briefly allows the player to see the two fans,
the active lift, and the stabilized chamber behind Aryn. The point is not a
victory banner. The room itself is the proof of success.

## Traversal topology

### Dormant descent

1. Upper-left room link at approximately `y = 210`.
2. Drop to the left upper catwalk at `y = 338`.
3. Reverse toward the `y = 480` service perch.
4. Descend through the `y = 635` and `y = 760` bands.
5. Continue through the `y = 997`, `y = 1122`, and freight-rail bands.
6. Reach the main concrete deck at `y = 1604`.
7. Approach the stabilizer at the far right.

The descent route must remain possible without using the freight lift.

### Restored ascent

1. Board the freight lift beside the stabilizer.
2. Ride from approximately `y = 1500` to `y = 735`.
3. Jump to the right mid catwalk at `y = 600`.
4. Jump to the service perch at `y = 480`.
5. Reach the right upper catwalk at `y = 338`.
6. Cross the upper containment threshold into the Refinery.

Every mandatory rise after leaving the lift remains within the existing
142-pixel maximum authored jump.

### Verified ascent envelope

| Transfer | Rise | Apex margin | Horizontal overlap |
| --- | ---: | ---: | ---: |
| Main deck to parked lift | 104 px | 48.2 px | direct boarding |
| Lift top to right mid catwalk | 135 px | 17.2 px | 134 px |
| Mid catwalk to service perch | 120 px | 32.2 px | 156 px |
| Service perch to upper catwalk | 142 px | 10.2 px | 123 px |

The current normal jump apex is approximately 152.2 world pixels. No mandatory
transfer requires edge-perfect horizontal placement, and the final 142-pixel
rise retains more than the eight-pixel safety floor used by the Foundry
traversal verifier.

## Freight-lift behavior

- Dormant position: parked near the main deck with no motion.
- Activation cue: rail lights fill from bottom to top before the lift moves.
- Restored travel: approximately 765 world pixels.
- Cycle duration: 5.6 seconds round trip, eased gently at both endpoints.
- Boarding pause: 0.55 seconds at the bottom.
- Upper pause: 0.75 seconds to allow a calm exit.
- Horizontal width: 210–240 world pixels.
- Aryn inherits platform motion without sliding.
- Falling from the lift is recoverable; the room never locks behind her.
- Reduced-motion preferences shorten camera pursuit and glow trails but do not
  change platform timing.

## Environmental state language

| System | Dormant | Restored |
| --- | --- | --- |
| Wall fans | still, dim cyan residue | rotating rapidly with restrained cyan bloom |
| Freight rail | nearly black | amber-to-cyan upward pulse |
| Freight lift | parked | full-height cycle |
| Service lamps | isolated magenta emergency lamps | alternating cyan and warm amber |
| Haze | heavy, slowly descending | pulled laterally toward both fans |
| Vegetation | still | small directional sway near active vents |
| Audio | distant metal strain and toxic hiss | deep rotor bed, relay chatter, cleaner high air |
| Threshold | magenta containment field | field retracts at the upper exit |

The palette should remain 70% dark structure. Restoration adds directional
light; it does not flood the room with neon.

## Activation timeline

| Time | Beat |
| ---: | --- |
| 0.00 s | Down input accepted; stabilizer interface responds |
| 0.30 s | nearby amber relays illuminate; authored generator start begins |
| 0.70 s | conduit pulse leaves the stabilizer |
| 1.15 s | first fan stutters once |
| 1.50 s | first fan reaches operating speed |
| 1.80 s | second fan begins at an offset phase |
| 2.15 s | haze bends visibly toward the upper vents |
| 2.35 s | existing stabilizer restart completes |
| 2.60 s | freight rail fills upward |
| 3.10 s | lift releases from its bottom lock |
| 3.60 s | upper threshold begins retracting |
| 4.20 s | player control and objective fully settle |

Suggested accessibility announcement:

> Foundry atmosphere restored. Freight lift online. Refinery access available
> above.

## Camera direction

### Descent

- Down input temporarily biases the camera 12% below Aryn.
- The camera changes vertical bands only after Aryn commits to a lower surface.
- Long empty space above her should remain visible; it reinforces scale.

### Stabilizer reveal

- The camera eases toward the machine before Aryn reaches interaction range.
- The reveal should never remove control for more than 0.8 seconds.

### Activation

- Follow the first conduit pulse upward for no more than 1.1 seconds.
- Catch one fan beginning to turn.
- Return to Aryn before the lift releases.

### Ascent

- Hold Aryn between 42% and 58% of visible height.
- Add a modest upward look-ahead while the lift rises.
- On portrait mobile, keep Aryn and the lift above the thumb-control band.

## Sound direction

The room needs a layered machine performance rather than one generic power-up
sound:

- stabilizer relay clack;
- authored two-second generator wake layer
  (`/Audio/super-frgmnts-generator-startup-v1.wav`) at 0.30 seconds;
- low capacitor charge beneath the authored wake layer;
- fan cough with a loose bearing;
- second fan entering at a slightly different pitch;
- freight brake releasing;
- metal cable tension;
- containment field collapsing;
- room tone changing from hiss-heavy to rotor-heavy.

The Foundry music should continue. Restoration adds stems and machinery; it does
not restart the track. The generator wake plays once per restart, follows the
global sound toggle, and stops on pause or focus loss.

## Mobile and accessibility guardrails

- The intended lift exit must be possible with one thumb held right and one
  jump press.
- No mandatory jump should begin beneath the mobile FIRE or JUMP buttons.
- The activation camera returns before control is required.
- Fan glow cannot obscure platform edges.
- Haze displacement must not be the only indication that restoration worked.
- The lift rail, objective copy, sound, and accessibility announcement all
  communicate the state change.
- The room remains completable with reduced motion and sound disabled.

## What remains deliberately absent

- enemies;
- shards;
- hearts;
- coin boxes;
- coins;
- power-ups;
- timer awards;
- lethal fan blades;
- wind steering.

The first prototype proves the room’s fall, breath, and ascent. Population comes
later.

## Prototype acceptance criteria

- The dormant route reliably carries Aryn from the upper entrance to the
  stabilizer.
- The player cannot reach the Refinery exit before restoration.
- The deck-level boundary never becomes a bypass around the powered ascent.
- The activation sequence is readable without explanatory copy.
- Both fans visibly and audibly respond.
- The freight lift provides the only mandatory return route.
- Every post-lift jump retains at least an 8-pixel vertical safety margin.
- Falling from the ascent never creates a softlock.
- The complete loop is readable at 360 px portrait width.
- The room feels materially different on the second traversal.

## Recommended build order

1. Author the dormant one-way descent.
2. Park and collision-test the freight lift.
3. Move the Refinery transition to the upper exit.
4. Wire lift and threshold state to the existing stabilizer.
5. Add activation camera choreography.
6. Add haze displacement, rail light, and fan staggering.
7. Add the layered sound performance.
8. Test the complete loop before adding any population systems.
