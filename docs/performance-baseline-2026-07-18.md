# Outside the World performance baseline

Measured July 18, 2026 (America/Phoenix). This document records the site before performance remediation. No production code was changed while collecting it.

## Executive finding

The homepage's cache is not entirely broken. An immediate return visit served its nine observed R2 images from the browser's disk cache and transferred only 595 bytes from OTW-owned resources. The actual problem is the combination of:

1. very large original images on cold or delayed visits;
2. no explicit cache lifetime on the R2 images;
3. a ten-minute lifetime on every sampled `outsidetheworld.com` asset;
4. five homepage data requests that explicitly revalidate on every visit; and
5. lazy-loaded images placed close enough to the viewport that the browser begins loading them before the reader reaches them.

This makes fast repeat visits possible but not dependable. A cold desktop homepage visit transferred a median 30.54 MB. A cold mobile visit transferred a median 13.48 MB.

## Method

- Lighthouse 13.0.1, three sequential cold-cache runs for `index.html` on simulated mobile and desktop profiles.
- One mobile screening run for six representative first-click destinations.
- A clean Chrome profile controlled through the Chrome DevTools Protocol for cold and immediate-repeat cache comparison.
- Live browser inspection before scrolling and after a complete homepage scroll.
- HTTP header inspection of 84 unique OTW-owned assets observed across the tested pages.
- Lighthouse figures are lab measurements, not field Core Web Vitals. Three-run medians are used for the homepage because individual tests vary.

## Homepage baseline

| Metric | Mobile median | Desktop median | Desired budget |
|---|---:|---:|---:|
| Lighthouse performance | 76 | 75 | At least 90 |
| First Contentful Paint | 0.94 s | 0.25 s | At most 1.8 s |
| Largest Contentful Paint | 7.22 s | 8.80 s | At most 2.5 s |
| Speed Index | 0.98 s | 0.38 s | At most 3.4 s |
| Total Blocking Time | 68 ms | 0 ms | At most 200 ms |
| Cumulative Layout Shift | 0.022 | 0.006 | At most 0.1 |
| Transfer size | 13.48 MB | 30.54 MB | Under 1 MB before scrolling |
| Requests | 32 | 40 | Informational; bytes and priority matter more |

Mobile LCP runs were 33.45 s, 7.22 s, and 7.05 s. The 33-second outlier demonstrates the instability the reader has noticed. Lighthouse identified the secondary Midweek Weather image, not the current hero, as the mobile LCP candidate because it enters the initial mobile viewport and is marked lazy. Desktop consistently identified the current hero as the LCP candidate.

Lighthouse estimated that the median mobile run could save 12.73 MB through improved image delivery and 13.02 MB through effective cache lifetimes. Desktop estimates were 27.34 MB and 27.99 MB respectively.

## Homepage media behavior

- The current hero, `The Intake`, is a 2,650,465-byte JPEG.
- Its source is approximately 3,023 pixels square, while the tested mobile presentation was about 378 by 213 pixels and the desktop presentation about 836 by 523 pixels.
- On the live desktop load, 29 image elements existed. Only three were visibly in the initial viewport, but 13 had already completed loading.
- Completed images extended to approximately 1,896 pixels down a 720-pixel-high viewport, or more than two and a half screens ahead.
- After a complete scroll, all 29 image elements had loaded and 27 unique image assets were observed.
- The current homepage's complete observed image set is approximately 9.9 MB in the ordinary browser session. Lighthouse loaded additional large Image of the Day assets on the wider desktop profile, producing the larger 30.54 MB median transfer.

The problem is not the height of the hero. It is that the browser receives the original photographic file rather than a derivative made for the actual display size.

## Cache baseline

Eighty-four unique OTW-owned resources were inspected across the homepage and representative destinations.

| Host | Assets sampled | Observed policy |
|---|---:|---|
| `outsidetheworld.com` | 47 | `Cache-Control: max-age=600` |
| `*.r2.dev` | 37 | No `Cache-Control` header |

Cloudflare documents `r2.dev` as a non-production endpoint that does not support Cloudflare caching. Production media should be attached to a custom domain.

### Immediate repeat test

| Measurement | Cold visit | Immediate return |
|---|---:|---:|
| OTW-owned requests observed | 25 | 24 |
| Encoded transfer | 12,416,491 bytes | 595 bytes |
| Disk-cache hits | 0 | 19 |
| R2 requests | 9 | 9 |
| R2 disk-cache hits | 0 | 9 |
| Homepage data requests | 5 | 5 |
| Homepage data disk-cache hits | 0 | 0 |

The five data files returned tiny validation responses rather than their bodies, but they still required network trips because the homepage requests them with `cache: 'no-cache'`. The R2 images happened to be stored heuristically by Chrome, but the server promises no lifetime and the development endpoint provides no CDN cache.

## Bootstrap and data cost

- `index.html`: 194,739 bytes raw, with substantial inline CSS and JavaScript that cannot be cached independently.
- `narrative_data.js`: 678,372 bytes raw and roughly 156 KB transferred compressed. It contains full article bodies even though the homepage only needs card metadata.
- Homepage bootstrap files use `cache: 'no-cache'` for `frontpage_manifest.json`, `narrative_data.js`, `image_manifest.json`, `new_poetry_data.js`, and `fragments_data.js`.
- No service worker currently controls homepage requests. The existing OTW app service worker is scoped to the separate application shell.

## First-click screening

| Destination | Score | FCP | LCP | CLS | Transfer | Primary finding |
|---|---:|---:|---:|---:|---:|---|
| Image of the Day | 66 | 3.37 s | 110.13 s | 0 | 106.37 MB | All 42 gallery originals can enter the lazy-load range; one GIF is 8.22 MB and several photographs exceed 4-6 MB. The manifest is fetched with `cache: 'no-store'`. |
| Fragments | 56 | 2.62 s | 4.32 s | 0.700 | 3.37 MB | Severe layout shift plus oversized link-preview and media images. |
| Current essay | 70 | 4.13 s | 5.07 s | 0 | 1.18 MB | The feature image is modest, but a 748 KB lazy previous-article thumbnail is delivered to a roughly 197 by 148 slot. |
| Professional | 99 | 1.64 s | 1.64 s | 0.049 | 272 KB | Healthy control page; it demonstrates that the hosting stack itself is capable of good performance. |
| The Drift | n/a | 3.02 s | No LCP recorded | 0.127 | 305 KB | Lightweight, but Lighthouse could not identify an LCP candidate; CLS narrowly misses the target. |
| Wayback | n/a | 3.31 s | No LCP recorded | 0.050 | 671 KB | `wayback_purified.js` transfers about 251 KB compressed and contains the archive corpus. Lighthouse could not identify an LCP candidate. |

The Image of the Day result is the largest immediate ancillary risk. Its Lighthouse image-delivery audit estimated 105.91 MB of avoidable image transfer.

## Ranked remediation sequence

### P0: production media delivery

1. Attach the R2 bucket to a custom hostname such as `media.outsidetheworld.com`.
2. Give immutable, uniquely named media a one-year browser lifetime with `immutable`.
3. Generate AVIF, WebP, and JPEG derivatives at a small, explicit set of widths.
4. Emit `srcset` and `sizes` from the content pipeline.
5. Generate art-directed hero derivatives without reducing the hero's visual height.

### P0: stop gallery over-fetching

1. Give Image of the Day a bounded initial batch or pagination strategy.
2. Replace `cache: 'no-store'` on its manifest.
3. Keep full originals available only when the reader opens an image.
4. Prevent the browser's lazy-load distance from placing the whole compact grid inside its preload window.

### P1: slim the homepage bootstrap

1. Generate a small frontpage payload containing only the selected cards and their presentation metadata.
2. Do not ship full essay bodies to `index.html`.
3. Remove forced revalidation from immutable or versioned data resources.
4. move large inline CSS and JavaScript into versioned, independently cacheable files where appropriate.
5. Defer Last.fm and other nonessential network work until idle or until their modules approach the viewport.

### P1: repair layout and thumbnails

1. Stabilize Fragments card dimensions before its API responses render.
2. Add responsive derivatives to fragment media and link previews.
3. Give article navigation thumbnails a small thumbnail source instead of the editorial original.

### P2: regression protection

1. Reject or warn on homepage images above an agreed byte and dimension budget.
2. Run Lighthouse budgets against the homepage, Image of the Day, a current article, and Fragments.
3. Assert response cache policies during deployment.
4. Record real-user LCP, INP, and CLS after the delivery changes ship.

## Acceptance budgets

- Mobile LCP at or below 2.5 seconds at the 75th percentile.
- INP at or below 200 ms and CLS at or below 0.1.
- Homepage hero derivative at or below 350 KB.
- Cold homepage transfer under 1 MB before scrolling.
- Immediate-repeat OTW-owned transfer under 100 KB.
- No immutable image, CSS, or JavaScript validation request on an ordinary return visit.
- No image delivered at materially more than the physical pixels required for its slot and device pixel ratio.
- Image of the Day does not download the complete archive before reader interaction.

Machine-readable summary: `docs/performance-baseline-2026-07-18.json`.
