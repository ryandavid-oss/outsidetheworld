# Aryn Sol-Mavi // Armor-Change Animation v1

**Status:** Integrated with persistent RD-42 flight-suit movement

**Established:** 2026-07-28

The supplied 36-frame sequence changes Aryn from field armor into her orange
flight suit. Every source frame lasts 76 ms, for a complete authored duration
of 2.736 seconds.

## Assets

- Raw source:
  [`Raw/aryn-armor-change-source-v1.png`](Raw/aryn-armor-change-source-v1.png)
- Raw metadata:
  [`Raw/aryn-armor-change-source-v1.json`](Raw/aryn-armor-change-source-v1.json)
- Runtime candidate:
  [`../../../../../../Images/Game/Super-Frgmnts/aryn-armor-change-runtime-v1.png`](../../../../../../Images/Game/Super-Frgmnts/aryn-armor-change-runtime-v1.png)
- Animated review:
  [`Reviews/aryn-armor-change-preview-v1.gif`](Reviews/aryn-armor-change-preview-v1.gif)
- Contact sheet:
  [`Reviews/aryn-armor-change-contact-v1.png`](Reviews/aryn-armor-change-contact-v1.png)
- Manifest:
  [`aryn-armor-change-v1.json`](aryn-armor-change-v1.json)

Regenerate the normalized derivatives with:

```sh
python3 tools/build_super_frgmnts_aryn_armor_change.py
```

## Runtime behavior

The isolated RD-42 preview supports a stationary interaction:

1. Aryn aligns with the RD-42 flight/suit cradle.
2. Normal movement and combat presentation lock.
3. The 36-frame sequence replaces the standard field sprite.
4. Control returns with Aryn persistently wearing the flight suit.
5. The companion
   [`../Flight-Suit/README.md`](../Flight-Suit/README.md) movement set supplies
   her run, jump, fall, landing, and standing presentation around the main
   deck.
6. Returning to the alcove and pressing Down reverses the sequence and
   restores her field armor.

Every runtime frame is now normalized to a 90-pixel visible-height target
around baseline y 104 while preserving the source-frame center. This removes
the height jump between the 88-pixel armored source pose and the former
95-pixel resolved flight-suit pose. Inside the RD-42, the shared 112-pixel
physics cell renders at 168 pixels, producing an approximately 135-pixel
visible Aryn in both costumes.

This sheet remains authoritative only for the stationary costume change. The
separate supplied flight-suit movement set now closes the main-deck locomotion
gap. Neither set includes unarmored hatch descent, damage, weapon, pack, or
keel-service-deck poses, so the dorsal hatch and service-kit pickup require
field armor. The reverse re-arm remains provisional until its own authored
sequence exists.

## Art-direction value

The resolved flight-suit frames are also an identity reference for the next
RD-42 interior pass: pale cyan energy, cobalt-blue apparel, warm orange, and
small pink accents should lead the occupied cabin. The Foundry remains a
pixel-language reference only, not the ship's palette or material identity.
