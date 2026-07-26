# Vesper Mite // provisional enemy integration

Working name: **Vesper Mite**.

The supplied Ludo atlas contains 36 untrimmed RGBA frames arranged in six
columns and six rows. Every frame is 530 × 650 pixels with a 64 ms duration.
No animation tags are supplied. Frames 0–17 read as one coherent lift and
settle cycle; frames 18–35 substantially repeat that motion.

For the first integration:

- retain all 36 frames in a nearest-neighbor 636 × 780 runtime atlas;
- use frames 0–17 as a provisional 1.152-second low-hover loop;
- keep the creature non-projectile and close to a Foundry catwalk;
- add occasional randomized reversals inside a bounded patrol;
- allow contact damage, a descending stomp, and the seeking pack blaster;
- expose only one specimen through `?preview=foundry-expansion&mite=1`.

This is an isolated behavior and scale trial. It does not populate the Episode
01 run until its name, size, movement, and encounter role are approved.
