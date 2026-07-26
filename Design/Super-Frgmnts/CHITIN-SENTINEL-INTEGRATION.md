# Chitin Sentinel // provisional enemy integration

Working name: **Chitin Sentinel**.

The supplied Ludo patrol atlas contains 36 untrimmed RGBA frames in a six by
six grid. Each source frame is 570 × 526 pixels with a 54 ms duration, making
one 1.944-second patrol cycle.

The supplied death atlas also contains 36 untrimmed RGBA frames in a six by
six grid. Each source frame is 544 × 482 pixels with a 61 ms duration, making
one 2.196-second collapse from guard stance to a prone body.

For the isolated integration:

- retain all 36 frames from both sources in two nearest-neighbor 684 × 636
  runtime atlases;
- patrol slowly and deliberately on one broad upper Foundry catwalk;
- require exactly five tier-one pack-blaster hits;
- flash the armor and report the remaining integrity after each hit;
- do not allow stomps to bypass the armored encounter;
- make the death animation non-interruptible and award 1,250 points only
  after the fifth hit;
- expose one specimen through
  `?preview=foundry-expansion&patroller=1&autostart=1`.

This is a scale, motion, and durability trial. It does not populate the
Episode 01 run until the enemy name, size, patrol speed, five-hit rhythm, and
death timing are approved.
