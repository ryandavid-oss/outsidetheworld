# Outside the World performance remediation: Phase 2

Measured July 18, 2026 (America/Phoenix) after production deployment. Results
are three cold mobile Lighthouse 13.0.3 runs against the live homepage. The
reported headline is the median; the individual runs remain below so variance
is visible.

## Result

| Homepage mobile | Phase 1 | Phase 2 median | Change |
|---|---:|---:|---:|
| Performance score | 95 | 97 | +2 points |
| Largest Contentful Paint | 2.86 s | 2.42 s | 15% faster |
| Cold transfer | 0.48 MB | 0.32 MB | 34% smaller |
| Requests | 22 | 17 | 5 fewer |
| Total Blocking Time | 60 ms | 45 ms | 25% lower |
| Cumulative Layout Shift | 0.0221 | 0 | eliminated |

The Phase 2 acceptance target was a dependable median mobile LCP of 2.5 seconds
or better. Production reached 2.42 seconds.

## Individual production runs

| Run | Score | FCP | LCP | Speed Index | TBT | CLS | Transfer | Requests |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 93 | 0.99 s | 2.98 s | 3.67 s | 16.5 ms | 0 | 481,782 B | 18 |
| 2 | 99 | 0.94 s | 2.18 s | 0.94 s | 45 ms | 0 | 315,173 B | 16 |
| 3 | 97 | 1.01 s | 2.42 s | 2.35 s | 123 ms | 0 | 315,384 B | 17 |

The first run is retained intentionally. It shows that network and rendering
variance still exists even though the median clears the target.

## What changed

- Added a deterministic `frontpage_payload.json` generated from the full essay,
  IOTD, poetry, fragment, front-page, and responsive-media sources.
- Reduced the normal homepage bootstrap from six source requests to one compact
  request. The payload contains only the source prefixes needed to reproduce the
  current slots: 12 essays, 8 images, 7 poems, and 1 founder fragment.
- Removed full essay bodies and unused publisher metadata from the homepage
  path. The payload is 58,113 bytes raw and approximately 9.3 KB compressed.
- Embedded only the 19 responsive-image lookups used by those cards.
- Preserved the complete pre-Phase-2 loader as an automatic fallback when the
  compact payload is missing, malformed, or has no renderable core records.
- Added a selection-equivalence and freshness test. The generated payload must
  reproduce the same homepage picks as all full source files and remain below a
  20 KB compressed budget.
- Wired regeneration into narrative publishing, discovery builds, IOTD entry
  creation, fragment/poetry changes, front-page manifest changes, and responsive
  media rebuilds.
- Suppressed the static pre-hydration grid so an obsolete hard-coded headline
  cannot flash before the current payload renders. A delayed two-second test
  held the grid at opacity 0, then revealed `The Intake` only after hydration.

## Runtime verification

All three production Lighthouse runs requested `frontpage_payload.json` at
roughly 9.7 KB transferred. None requested `narrative_data.js`,
`frontpage_manifest.json`, `image_manifest.json`, `new_poetry_data.js`,
`fragments_data.js`, or `responsive_media.json`.

The forced-failure browser test returned HTTP 404 for the compact payload and
confirmed that the legacy loader produced identical visible slot data and the
same 20 section entries. The live homepage subsequently reported compact mode,
`The Intake` as its lead, four populated editorial sections, 20 section entries,
and zero failed front-page images.

## Integrity

- Compact payload contract and freshness test: passed.
- Publisher server and private archive smoke tests: passed.
- Discovery validation: 814 permanent pages and 857 sitemap URLs.
- Complete local surface audit: 910 documents, 0 errors, 0 warnings.
- Production whole-site integrity workflow: passed at `47cebc2`.
- GitHub Pages deployment: passed at `47cebc2`.

