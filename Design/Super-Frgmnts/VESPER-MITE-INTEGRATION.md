# Vesper Mite // ground-traveler integration

Working name: **Vesper Mite**.

The supplied Ludo atlas contains 36 untrimmed RGBA frames arranged in six
columns and six rows. Every frame is 530 × 650 pixels with a 64 ms duration.
No animation tags are supplied. Frames 0–17 read as one coherent lift and
settle cycle; frames 18–35 substantially repeat that motion.

The completed Episode 01 integration:

- retain all 36 frames in the nearest-neighbor 636 × 780
  `enemy-vesper-mite-ground-gait-sheet-v2.png` runtime atlas;
- use frames 0–17 as a provisional 1.152-second scuttling gait;
- bind the creature to a Foundry deck or catwalk rather than flyer physics;
- add occasional randomized reversals inside a bounded patrol;
- allow contact damage and telescopic laser seeker damage; descending contact
  still hurts Aryn and never becomes a stomp attack;
- retain the isolated specimen through `?preview=foundry-expansion&mite=1`;
- populate one specimen in the Episode 01 beta roster.

The wing-like silhouette is part of the creature's shell and gait. It does not
grant hovering behavior.
