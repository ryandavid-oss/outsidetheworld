# OTW media delivery

This Worker serves the `otw-iotd` R2 bucket through cacheable production
routes.

- `/o/<object-key>` serves the preserved original with browser and edge cache
  lifetimes.
- `/v/<fingerprint>/<width>` negotiates WebP/JPEG responsive derivatives and
  serves them with a one-year immutable lifetime.
- `tools/build_responsive_media.py --upload` creates the derivative objects
  and `responsive_media.json` lookup used by the public site.

The current origin is `https://otw-media.ryandavid.workers.dev`. A future
`media.outsidetheworld.com` custom domain can point at the same Worker without
changing the R2 object layout.
