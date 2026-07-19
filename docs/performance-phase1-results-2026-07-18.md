# Outside the World performance remediation: Phase 1

Measured July 18, 2026 (America/Phoenix) after production deployment. The
homepage mobile figures are three-run Lighthouse medians. The final desktop
and Image of the Day figures are production confirmation runs after the last
priority and layout-stability patches.

## Result

| Surface | Measurement | Before | After | Change |
|---|---|---:|---:|---:|
| Homepage mobile | Performance score | 76 | 95 | +19 points |
| Homepage mobile | LCP | 7.22 s | 2.86 s | 60% faster |
| Homepage mobile | Cold transfer | 13.48 MB | 0.48 MB | 96% smaller |
| Homepage desktop | Performance score | 75 | 98 | +23 points |
| Homepage desktop | LCP | 8.80 s | 1.19 s | 87% faster |
| Homepage desktop | Cold transfer | 30.54 MB | 1.14 MB | 96% smaller |
| Image of the Day mobile | Performance score | 66 | 94 | +28 points |
| Image of the Day mobile | LCP | 110.13 s | 2.47 s | 98% faster |
| Image of the Day mobile | Cold transfer | 106.37 MB | 0.41 MB | 99.6% smaller |
| Image of the Day mobile | CLS | 0 | 0 | stable |

The homepage’s current `The Intake` hero fell from a 2,650,465-byte original to
approximately 38 KB on the tested mobile viewport and 125 KB on desktop. The
full original remains available when a reader opens the image.

## What changed

- Added a cache-aware media delivery Worker in front of the R2 bucket.
- Generated 750 immutable WebP/JPEG representations for 89 source images at up
  to five widths. The one animated GIF deliberately remains animated and uses
  its original source.
- Added `srcset` and `sizes` selection to the homepage and Image of the Day.
- Replaced production `r2.dev` references with the cached media origin.
- Prevented homepage and gallery images from receiving a URL until they
  approach the viewport. The gallery confirmation loaded 10 responsive images,
  not all 43 originals.
- Restored normal browser caching for homepage data and the IOTD manifest.
- Delayed analytics until interaction or after the first screen settles.
- Removed the render-blocking Google Fonts stylesheet from IOTD while retaining
  the same fonts.
- Added upload-time image reduction for new IOTD and Drift images.

## Cache contract

- Responsive variants: `public, max-age=31536000, immutable` in the browser and
  at the edge.
- Originals: one day in the browser, one week at the edge, with stale reuse.
- Homepage data: ordinary browser caching rather than forced revalidation.

All 750 responsive representations were checked at the media endpoint in both
WebP and JPEG negotiation paths. The complete local site audit finished with
zero errors and zero warnings; the production integrity workflow also passed.

## Honest remaining bottleneck

Homepage mobile LCP is now stable enough to expose the next architectural cost:
the homepage downloads the full `narrative_data.js` corpus before it can select
the first essay card. The correct Phase 2 move is a compact, generated homepage
payload containing only the cards the homepage actually renders. That is the
remaining path from the current 2.86-second median toward a dependable 2.5
seconds or better.

