# Outside the World performance remediation: Phase 3

Measured July 18, 2026 (America/Phoenix) after production deployment. Cold-route
results are three Lighthouse 13.0.3 mobile runs against the live site, matching
the baseline version and settings. The reported headline is the median.

## First-click route result

| Route | Baseline score | Phase 3 score | Baseline LCP | Phase 3 LCP | Baseline transfer | Phase 3 transfer |
|---|---:|---:|---:|---:|---:|---:|
| Current Writing | 67 | 100 | 6.05 s | 1.00 s | 720,590 B | 267,286 B |
| Fragments | 56 | 97 | 4.20 s | 2.56 s | 3,369,607 B | 499,039 B |
| Poetry | 78 | 99 | 4.30 s | 0.98 s | 305,303 B | 138,613 B |
| Professional | 79 | 100 | 4.16 s | 0.94 s | 271,773 B | 105,047 B |
| Current essay | 71 | 98 | 4.93 s | 2.29 s | 1,181,788 B | 148,953 B |

Current Writing's median LCP improved 83%, Poetry 77%, Professional 77%, the
current essay 54%, and Fragments 39%. Transfer fell 63%, 55%, 61%, 87%, and 85%
respectively.

The homepage and Image of the Day were control routes in this phase. Their cold
baseline medians remained 2.19-second and 2.42-second LCP respectively. No Phase
3 code change was made to either route.

Fragments is the sole modified median slightly above a strict 2.5-second LCP
target, by 64 milliseconds. Its remaining LCP is the first live feed text, which
cannot render until the external frgmnts API responds. The page's own layout and
media work are no longer the bottleneck.

## Layout stability

Fragments fell from 0.6999 CLS to 0. Poetry, Professional, Current Writing, and
the current essay all remained at or below 0.0124 median CLS. The implementation
reserves or hides only the not-yet-populated downstream region; it does not hide
the usable page once data is ready.

## Warm-return proof

A fresh persistent Chrome profile was used with storage reset disabled. These
are paired Lighthouse 13.0.3 runs, not inferred cache-header behavior.

| Route | First visit / click | Warm return | Transfer reduction |
|---|---:|---:|---:|
| Homepage LCP | 2.23 s | 0.79 s | 65% faster |
| Homepage transfer | 315,502 B | 1,525 B | 99.5% smaller |
| Current Writing LCP | 0.86 s | 0.04 s | 95% faster |
| Current Writing transfer | 261,214 B | 830 B | 99.7% smaller |

The homepage image/cache concern is therefore resolved in the measured return
path: repeat navigation does not redownload the image set.

## What changed

- Current Writing now loads an 8.1 KB compressed, body-free
  `narrative_index.json`. The full 662 KB archive source is fetched only if the
  compact contract fails, and the forced fallback was verified in-browser.
- Fragments uses an explicit 300-pixel viewport gate for avatars, link previews,
  and photography. Native lazy loading had still downloaded multi-megabyte media
  because ten cards landed inside Chrome's generous near-viewport boundary.
- Fragments and Poetry reserve or conceal their downstream mobile region until
  the live list has its final geometry, eliminating the large rail/stage shift.
- Parser-discovered analytics and blocking font imports were removed from the
  affected first-click routes. Professional fonts now enter after first paint,
  which eliminated a production-only font recalculation race.
- Adjacent essay thumbnails use `data-reader-src` and an explicit 240-pixel
  reader viewport gate. The current essay no longer downloads a 749 KB older
  essay image at page entry. `narrative_sync.py` now emits this behavior for all
  present and future current essays.
- Seven compressed route budgets and structural loading contracts now run in
  both whole-site integrity and narrative publishing. They reject heavy compact
  payloads, parser-loaded full archives, early analytics, blocking archive/poetry
  font imports, and eagerly sourced adjacent media.

## Variance retained intentionally

The after-run set includes a 4.18-second Current Writing LCP outlier even though
the other two runs were 1.00 and 0.93 seconds. It also includes first runs that
transferred delayed fonts or analytics after rendering. These runs remain in the
machine-readable record. Medians describe the normal result; they do not make
network variance cease to exist.

## Integrity

- Compact homepage payload test: passed at 9,260 compressed bytes.
- Compact narrative index test: passed at 8,146 compressed bytes.
- First-click route budgets: all seven passed.
- Publisher render contract: 29 tests passed.
- Publisher source contract: passed.
- Browser checks: compact and legacy Current Writing, Fragments media viewer,
  Poetry rendering, Professional content, and deferred essay navigation passed.
- GitHub Pages deployment: passed at `a850253`.
- OTW Whole-Site Integrity: passed at `a850253`.

