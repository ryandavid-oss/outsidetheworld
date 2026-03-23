# Future Publishing Plan

Goal: keep the site static and Git-backed, but restore the ability to publish from iPhone, iPad, or Mac without being tied to the desktop workflow.

## Current state

- Public site stays on GitHub Pages for now.
- Authoring happens through `ghost-writer.html`.
- New posts are stored as markdown in `current_narrative/`.
- `narrative_sync.py` converts those markdown files into `narrative_data.js`.
- GitHub automation handles the sync/publish side after content lands in the repo.

## Future direction

Build a private publishing page backed by a small serverless endpoint.

Intent:
- Keep Git as source of truth.
- Keep the static-site architecture.
- Replace the Mac-only content entry step with a secure web-based publishing surface.

## Target workflow

1. Open a private publish page from phone, tablet, or desktop.
2. Authenticate.
3. Write title/body and optionally attach images.
4. Submit to a secure backend endpoint.
5. Backend creates a markdown file in `current_narrative/`.
6. Existing repo automation updates `narrative_data.js`.
7. Site redeploys normally.

## Phase plan

### Phase 1

Text-only publishing.

- Reuse the ideas behind `ghost-writer.html`.
- Add a mobile-friendly private publish UI.
- Send title/body/date to a secure endpoint.
- Endpoint writes a markdown file into `current_narrative/`.

### Phase 2

Image publishing.

- Add image upload support.
- Store images outside the repo if practical.
- Inject stable image links into the markdown body or post metadata.

### Phase 3

Hardening.

- Strong auth.
- Duplicate-submission protection.
- Draft recovery/autosave.
- Publish logs/status.

## Constraints

- Do not break the current GitHub Pages site.
- Do not replace the current markdown-based narrative model.
- Prefer low-cost infrastructure.
- Optimize for low-friction mobile publishing.

## Options to revisit later

- Cloudflare Pages + Functions + R2
- Netlify Functions
- Vercel Functions
- Other serverless endpoint tied back to GitHub

## Low-priority nice to have

- Revisit static asset caching/expires behavior if the site moves beyond plain GitHub Pages hosting.
- Goal: allow longer-lived cache headers for truly static assets without risking stale HTML, manifests, or frequently updated data files.
- This is a performance/publishing polish item, not an urgent problem.

## Short version

This is not a CMS migration plan.

It is a plan to preserve the current site architecture while replacing the input method with a secure, mobile-friendly publisher.
