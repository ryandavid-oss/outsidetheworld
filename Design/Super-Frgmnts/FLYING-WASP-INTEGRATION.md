# Flying Wasp // provisional enemy integration

**Flying Wasp** is a temporary production identifier, not a locked species
name.

The supplied Ludo atlas contains 36 untrimmed RGBA frames arranged in six
columns and six rows. Each source frame is 560 × 432 pixels with a 46 ms
duration. The complete sequence reads as one coherent 1.656-second airborne
loop, so the runtime candidate retains all 36 frames.

The runtime atlas is 672 × 516 pixels, with 112 × 86 pixel frames and
nearest-neighbor reduction. This keeps the creature’s amber wing motion,
charcoal body, green eyes, and transparent silhouette intact while reducing
the source atlas from 6.1 MB to a mobile-safe runtime asset.

For review:

- keep it out of Episode 01 population and balance;
- treat it as an airborne silhouette and motion test only;
- do not infer health, attacks, drops, or encounter placement yet;
- use the runtime atlas in an isolated trial before naming or tuning it.

The original image and Ludo manifest are preserved under
`Foundry/Enemies/Flying-Wasp/Raw`. A looping review GIF is in that enemy’s
`Reviews` directory.
