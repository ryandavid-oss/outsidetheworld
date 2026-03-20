# Future Features

Working notes for upcoming refinements, experiments, and quality-of-life improvements across Outside The World.

This file is intentionally practical. It is not a polished roadmap. It is a running ledger so good ideas do not get lost.

## Current priorities

### Fragments

- Keep refining the mobile publisher experience.
- Consider a coordinated rename of the private app shell later:
  - `fragments_publisher.html` -> `otw_app.html`
  - only do this when the manifest, service worker, and installed-app cache behavior feel stable enough to avoid needless churn
- Consider a stronger publish payoff animation or toast if the current success feedback still feels too subtle.
- Revisit edit/delete later if the pain of typo correction keeps recurring.
  - Likely requires stable fragment IDs plus Worker support for update/delete actions.
- Keep the public feed simple and calm.
- Continue improving cache behavior where needed.
- Keep expanding the fake `Sponsored Signals` rail on `fragments.html`.
  - Add more dry, Douglas Adams-style nonsense ads over time.
  - Especially preserve and build on the tone of entries like `Signal Socks`.

### OTW_Bot

- Build a much larger quip library.
- Decide whether quips should be:
  - manually added
  - scheduled automatically
  - triggered by a helper tool
- Long-term goal:
  - OTW_Bot should post permanent entries into `fragments_data.js`
  - avoid temporary render-time injection
- Add repeat protection so the bot does not reuse lines too quickly.

### Ghost Writer

- Keep the new centered-text and divider tools lightweight and reliable.
- Consider a second centered-text style later:
  - quieter / reflective
  - larger pull-quote / emphasis
- Keep authoring controls expressive without turning the tool into a full CMS.

### Personal Feed

- Keep the live-post stat strip on the newest post only.
- Watch spacing and readability as newer essays get longer and more structured.
- Revisit whether additional live metadata is ever needed beyond:
  - words
  - chars
  - read time

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

- Better commit/publish visibility from the mobile tools.
- A small internal changelog for infrastructure changes.
- More reusable writing components:
  - pull quotes
  - callout notes
  - centered whispers / signal lines

## Rule of thumb

If an idea makes publishing calmer, clearer, or more sustainable, it is probably worth keeping on the list.

If an idea starts turning the site into a noisy platform instead of a deliberate personal system, pause and reassess.
