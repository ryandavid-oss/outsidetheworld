# Future Features

Working notes for upcoming refinements, experiments, and quality-of-life improvements across Outside The World.

This file is intentionally practical. It is not a polished roadmap. It is a running ledger so good ideas do not get lost.

## Current priorities

### OTW App

- Keep `otw_app.html` focused on active maintenance tools:
  - `publisher.html`
  - Image of the Day
  - The Drift
  - Palette
  - archived inbox viewers
- Keep old `fragments_publisher.html` installs/bookmarks redirecting cleanly.
- Continue improving install/cache behavior where needed.
- Treat the retired Fragments, Changelog, Ghost Writer, OTW_Bot, and analytics lanes as historical unless they are intentionally rebuilt.

### Personal Feed

- Keep the live-post stat strip on the newest post only.
- Watch spacing and readability as newer essays get longer and more structured.
- Revisit whether additional live metadata is ever needed beyond:
  - words
  - chars
  - read time

### Search

- Keep the public search focused on live/public content.
- Consider a second `Deep Archive Search` later for internal use:
  - Instagram archive
  - construction debris
  - older markdown and repo-only materials
  - keep this separate from the public-facing search so the main experience stays clean

## Medium-term ideas

### Multi-user fragments concept

This is interesting, but should not be rushed.

- Family interest in `Fragments` suggests real product potential.
- Current system is still single-publisher and not ready for multiple people.
- If explored later, likely needs:
  - separate identities
  - per-user auth
  - moderation / delete controls
  - a distinct feed model from the personal stream

Possible future concept names:

- `signal_circle`
- `inside_the_world`
- `house_fragments`

### Narrative publishing

- Reuse the Worker-based publish architecture that now powers `Fragments`.
- Longer-term goal:
  - private mobile publisher for full narrative posts
  - markdown written directly into `current_narrative/`
- See also:
  - `FUTURE_PUBLISHING_PLAN.md`

## Ongoing cleanup targets

### Wayback / archive polish

- Fix visible punctuation oddities only when clearly broken.
- Avoid broad spacing cleanups that may erase the voice of older posts.
- If future archive regeneration happens, be mindful of:
  - image path casing
  - malformed apostrophe entities
  - encoding consistency

### Content formatting

- Continue watching for punctuation corruption from mobile publishing.
- Keep Unicode / UTF-8 handling stable through:
  - publisher app
  - import helpers
  - Cloudflare Worker

## Nice-to-have later

- Better commit/publish visibility from the active mobile tools.
- More reusable writing components:
  - pull quotes
  - callout notes
  - centered whispers / signal lines

## Rule of thumb

If an idea makes publishing calmer, clearer, or more sustainable, it is probably worth keeping on the list.

If an idea starts turning the site into a noisy platform instead of a deliberate personal system, pause and reassess.
