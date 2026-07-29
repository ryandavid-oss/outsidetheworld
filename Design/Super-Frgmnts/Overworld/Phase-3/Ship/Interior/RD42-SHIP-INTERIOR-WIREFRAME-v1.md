# SUPER FRGMNTS // RD-42 Interior Wireframe v1

**Status:** Integrated greybox target

**Established:** 2026-07-28

**Logical plate:** 1,672 × 941

**Playable shell:** x = 220–1,452
**Main deck:** y = 744

This wireframe defines the first collision, camera, interaction, and art
reservations for the RD-42 interior. It is intentionally more precise than the
visual direction and less permanent than final collision data. Greybox review
may adjust a coordinate when movement or mobile framing proves a better value.

The single plate is the ship's inhabited spine, not an exhaustive cutaway of
the complete pressure hull. The composition deliberately spends its readable
width on cockpit, hatch, personal/pack space, and the story-critical cargo
rack; inaccessible systems remain implied behind panels and below the deck.

The behavioral authority is
[`RD42-SHIP-INTERIOR-CONTRACT-v1.md`](RD42-SHIP-INTERIOR-CONTRACT-v1.md).

Visual review:
[`RD42-SHIP-INTERIOR-WIREFRAME-v1.svg`](RD42-SHIP-INTERIOR-WIREFRAME-v1.svg).

## Whole-room diagram

```text
WORLD x=0                                                                  x=1672
┌──────────────────────────────────────────────────────────────────────────────┐
│                            NONPLAYABLE VOID                                  │
│                                                                              │
│      /======================= RD-42 PRESSURE SHELL =====================\     │
│     /                                                                        \    y≈272
│    /       COCKPIT             AIRLOCK            HAB / PACK       CARGO      \   │
│   /                                                                            \  │
│  |    canopy       nav       ╔══ DORSAL HATCH ══╗      bunk      parts rack    | │
│  |   ┌──────┐   ┌──────┐     ║       ↓          ║    ┌────┐     ┌────────┐     | │
│  |   │      │   │      │     ║   entry rails    ║    │    │     │ KIT ●  │     | │
│  |   └──────┘   └──────┘     ╚══════════════════╝    └────┘     └────────┘     | │
│  |       flight cradle              ARYN ↓        Trillian   pack     engineering| │
│  |          ◇                         X=684         berth     bench        wall    | │
│  |                                                                            | │
│  |____________________________ MAIN DECK y=744 _______________________________| │
│        x=220   300    548              820             1130            1452      │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

The diagram communicates relationships, not sprite scale. Coordinate tables
below are authoritative for the greybox.

## Coordinate bands

| Band | X range | Width | Function |
| --- | ---: | ---: | --- |
| Left exterior void | 0–220 | 220 | Nonplayable negative space |
| Cockpit | 220–548 | 328 | Optional flight and local-index interaction |
| Airlock | 548–820 | 272 | Required entry and exit clear zone |
| Habitation / pack | 820–1,130 | 310 | Optional character and future-upgrade space |
| Cargo / engineering | 1,130–1,452 | 322 | Required service-kit objective |
| Right exterior void | 1,452–1,672 | 220 | Nonplayable negative space |

Vertical bands:

| Band | Y range | Function |
| --- | ---: | --- |
| Upper void | 0–236 | Exterior darkness and camera breathing room |
| Tapered shell ceiling | 236–320 | Sloped ribs and dorsal-hatch housing |
| Habitable volume | 320–744 | Player, props, canopy, and machinery |
| Main deck / underfloor | 744–840 | Solid deck and shallow service volume |
| Lower void | 840–941 | Dark hull depth; nonplayable |

## Collision target

### Main collision

| ID | Type | X | Y | Width | Height | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `rd42_main_deck` | solid | 244 | 744 | 1,184 | 96 | Continuous mandatory route |
| `rd42_left_bound` | invisible wall | 220 | 236 | 24 | 604 | Follows the cockpit hull end |
| `rd42_right_bound` | invisible wall | 1,428 | 236 | 24 | 604 | Follows the engineering hull end |
| `rd42_ceiling_bound` | invisible ceiling | 244 | 236 | 1,184 | 20 | Disabled only during authored hatch transition |

The mandatory route is flat. Painted ribs, floor plates, and low thresholds
must not imply collidable steps that the greybox does not contain.

### Reserved future collision

The floor panel at x = 962–1,086 is a sealed visual reservation only.

- It is not interactive in v1.
- It has no opening collider.
- It does not imply a reachable lower deck.
- It may later become a service trench under its own approved contract.

## Zone boundaries

Open bulkhead frames reserve the room divisions:

| Frame | Center X | Clear opening | Foreground use |
| --- | ---: | ---: | --- |
| Cockpit / airlock | 548 | x = 508–588 | Angled rib; never blocks Aryn |
| Airlock / habitation | 820 | x = 780–860 | Strongest interior silhouette |
| Habitation / cargo | 1,130 | x = 1,090–1,170 | Engineering pressure frame |

Each opening remains at least 80 world pixels wide at Aryn's shoulder height
and at least 136 pixels wide near the deck. Foreground ribs may overlap the
sprite visually but never hide an active prompt.

## Dorsal hatch

| Property | Value |
| --- | ---: |
| Interior center X | 684 |
| Opening X | 624–744 |
| Opening width | 120 |
| Closed ceiling Y | 272 |
| Open visual depth | y = 252–326 |
| Entry landing center | x = 684 |
| Entry clear floor | x = 596–772 |
| Exit interaction zone | x = 624–744, y = 596–744 |
| Prompt anchor | x = 684, y = 574 |

The entry clear zone contains no furniture, companion, terminal, or ambient
prop. Aryn must always have at least 88 pixels of clear space on either side
when control returns.

The access rails lower from x = 650 and x = 718. They are animation guides,
not climbable collision during normal play.

## Interaction anchors

| ID | Label | Center X | Base Y | Radius | Availability |
| --- | --- | ---: | ---: | ---: | --- |
| `rd42_exit` | `▼ EXIT RD-42` | 684 | 744 | 78 | Whenever no mandatory pickup animation is active |
| `rd42_flight_console` | `▼ ACCESS LOCAL INDEX` | 386 | 744 | 86 | Optional; partial match requires specimen |
| `rd42_pack_bench` | `▼ INSPECT PACK BENCH` | 1,026 | 744 | 82 | Optional |
| `rd42_service_kit` | `▼ RECOVER TRANSIT SERVICE KIT` | 1,274 | 744 | 92 | Only during the service-kit objective |
| `rd42_berth` | `▼ CHECK TRILLIAN` | 894 | 744 | 72 | Optional and only if Trillian is present |

Prompt resolution uses the closest valid anchor and the priority documented in
the interior contract.

## Prop reservations

### Cockpit

| Prop | Bounds | Layer | Notes |
| --- | --- | --- | --- |
| Forward canopy | x 252–390, y 356–548 | rear | View or sensor glass consistent with exterior scale |
| Flight cradle | x 404–486, y 558–744 | mid | Non-solid silhouette; Aryn does not sit in v1 |
| Navigation table | x 318–408, y 612–710 | interactive rear | Owns local-index prompt |
| Central-link indicator | x 466–526, y 432–500 | rear emissive | Reads disconnected; no live Fleet contact |

### Airlock

| Prop | Bounds | Layer | Notes |
| --- | --- | --- | --- |
| Dorsal hatch | x 624–744, y 252–326 | rear/foreground | Split render for descent occlusion |
| Left access rail | x 644–660, y 292–596 | animated | Retracts after landing |
| Right access rail | x 708–724, y 292–596 | animated | Retracts after landing |
| Weapon hardpoint | x 756–808, y 448–690 | rear | Visual only; no loadout changes |
| Entry floor marks | x 612–756, y 720–744 | floor emissive | Cyan alignment marks |

### Habitation and pack

| Prop | Bounds | Layer | Notes |
| --- | --- | --- | --- |
| Trillian berth | x 840–936, y 642–744 | mid | Conditional empty/occupied state |
| Fold-down bunk | x 850–994, y 438–596 | rear | Mounted above berth without blocking actor |
| Ration heater | x 948–1,004, y 576–686 | rear | Small warm-light accent |
| Pack bench | x 994–1,084, y 532–710 | interactive rear | Specimen-reactive; no upgrade in v1 |
| Personal shelf | x 864–970, y 374–430 | rear | Sparse Aryn details |
| Sealed floor panel | x 962–1,086, y 732–760 | floor | Future service-trench reservation |

### Cargo and engineering

| Prop | Bounds | Layer | Notes |
| --- | --- | --- | --- |
| Shallow cargo rack | x 1,166–1,332, y 418–704 | rear | Holds keyed service case |
| Service case | x 1,238–1,310, y 608–672 | interactive | Separate sprite; absent after recovery |
| Engineering wall | x 1,334–1,416, y 344–710 | rear/emissive | Shows compatible transit hardware |
| Spare braid coil | x 1,180–1,232, y 520–578 | rear | Noninteractive supporting detail |
| Pressure status column | x 1,390–1,424, y 446–650 | rear emissive | Stable cyan in v1 |

## Player positions

The greybox treats Aryn as the current 112 × 112 draw silhouette with the
existing narrower collision body.

| State | Center X | Feet Y | Facing |
| --- | ---: | ---: | --- |
| Interior descent start | 684 | 360 | right |
| Rail release | 684 | 650 | right |
| Entry control return | 684 | 744 | right |
| Exit alignment | 684 | 744 | last safe facing |
| Service-kit pickup | 1,274 | 744 | right |
| Cockpit interaction | 386 | 744 | left |

The descent start is an authored pose and ignores normal ceiling collision.
Normal player physics begins only at the grounded control-return state.

## Exterior-to-interior coordinate mapping

Exterior:

- ship local center = x 572;
- world center = `OVERWORLD_ORIGIN_X + 572`;
- roof feet y = `448 + shipHoverOffset`; and
- activation width = 104.

Interior:

- hatch center = x 684;
- initial authored feet y = 360;
- deck feet y = 744; and
- exit interaction width = 120.

The differing scene coordinates are intentional. Continuity comes from the
matching centered hatch, Aryn's uninterrupted downward motion, the cyan seam,
and the same panel design—not from pretending the two Canvas scenes share a
single world origin.

## Desktop camera

| Property | Value |
| --- | ---: |
| Logical viewport | 1,672 × 941 |
| Camera X | 0 |
| Camera Y | 0 |
| Entry focus X | 684 |
| Look-ahead | 0 |
| Vertical pan | none |

The full shell remains visible. The 220-pixel void margins prevent the
interior from reading as wider than the exterior while retaining the standard
plate.

## Portrait-mobile camera

The exact world width varies with the existing responsive camera, but review
uses a target visible width of approximately 540 world pixels.

| Mode | Target center X | Required visible content |
| --- | ---: | --- |
| Entry | 684 | Hatch, Aryn, both airlock thresholds |
| Cockpit interaction | 386 | Aryn, console, canopy edge |
| Pack interaction | 1,026 | Aryn, pack bench, nearest airlock frame |
| Service-kit interaction | 1,274 | Aryn, service case, engineering wall |
| Exit | 684 | Aryn, rails, ceiling hatch |

Camera clamp:

- minimum interior camera center ≈ 490;
- maximum interior camera center ≈ 1,182;
- no exterior void beyond the shell wall should fill more than one third of a
  portrait frame; and
- prompt and Aryn remain simultaneously visible.

The ceiling hatch stays inside the upper mobile safe band throughout entry and
exit. Touch controls remain below the deck presentation and clear of device
safe-area insets.

## Art silhouette guide

The pressure shell should taper from the center toward both ends:

```text
ceiling y

236                         _________
                           /         \
272          _____________/  HATCH    \________________
300         /                                             \
340        /                                               \
           |                                               |
           |                                               |
744        |_____________________ DECK ____________________|
840          \___________________________________________/

             220        548      684      820     1130   1452   x
```

The cockpit end may taper more sharply than the cargo end, but both sides must
retain a clear 112-pixel-high player lane.

## Lighting map

| Zone | Base light | Accent | Specimen response |
| --- | --- | --- | --- |
| Cockpit | dark indigo | cyan instruments | local-index magenta warning |
| Airlock | graphite | cyan hatch seam | one restrained violet echo |
| Habitation | muted violet | warm low amber | pack bench violet-blue pulse |
| Cargo | graphite | cyan rack keys | service case cyan locator |
| Engineering | deep blue-black | cyan conduits | no independent response |

Lighting never communicates availability alone. Every interactive state also
uses a prompt, silhouette change, text, or sound.

## Audio reservations

The greybox may use provisional existing cues. Final audio direction reserves:

- low pressure-shell ambience;
- restrained engine/repulsor hum;
- two-part dorsal hatch open and close;
- soft access-rail movement;
- grounded boot landing;
- service-case release and magnetic pack latch;
- pack-bench harmonic response; and
- local-index access denial.

No alarm loop plays during normal occupancy.

## Greybox debug overlay

The isolated review should optionally draw:

- shell bounds;
- deck and wall collision;
- zone divisions;
- hatch activation and exit zones;
- interaction radii;
- player center and feet;
- portrait camera limits;
- current prompt priority; and
- service-kit and specimen state.

Suggested query:

```text
super_frgmnts.html?preview=ship-interior&debug=layout&autostart=1
```

## Coordinate-change rule

Greybox review may alter a listed coordinate only when the change improves:

- Aryn clearance;
- prompt separation;
- exterior/interior transition readability;
- desktop composition;
- 360–390 px portrait framing; or
- the credible relationship between interior and exterior scale.

Any accepted adjustment must update this wireframe and the eventual runtime
manifest together. Final art should not silently redefine collision or
interaction anchors.
