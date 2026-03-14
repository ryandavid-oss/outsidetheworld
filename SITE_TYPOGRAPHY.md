# Site Typography

This is the working typography reference for Outside The World.

## Primary Brand Fonts

### Inter

- Role: primary OTW sans
- Best for: body copy, UI text, navigation, forms, interface text
- Tone: clean, modern, readable, understated

Preferred weights:

- Light `300`
- Regular `400`
- Bold `700`
- Black `900`

Fallback stack:

```css
Inter, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif
```

### Fira Code

- Role: OTW system / signal mono
- Best for: captions, labels, timestamps, metadata, chips, buttons, status text
- Tone: technical, atmospheric, machine-log, signal-console

Preferred weights:

- Light `300`
- Regular `400`
- Medium `500`
- Bold `700`

Fallback stack:

```css
"Fira Code", "SFMono-Regular", Menlo, Monaco, Consolas, "Liberation Mono", monospace
```

### IBM Plex Serif

- Role: editorial / literary serif
- Best for: major headlines, poetic statements, editorial titles, reading surfaces
- Tone: thoughtful, warm, serious, authored

Preferred weights:

- Regular `400`
- Medium `500`
- Semibold `600`
- Bold `700`

Fallback stack:

```css
"IBM Plex Serif", Georgia, "Times New Roman", serif
```

### IBM Plex Sans

- Role: refined flagship sans
- Best for: premium body/UI on flagship pages
- Tone: modern, designed, calm, precise

Preferred weights:

- Regular `400`
- Medium `500`
- Semibold `600`
- Bold `700`

Fallback stack:

```css
"IBM Plex Sans", system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif
```

### IBM Plex Mono

- Role: refined flagship mono
- Best for: labels, counters, metadata, chips on newer flagship pages
- Tone: system-like, editorial, precise

Preferred weights:

- Regular `400`
- Medium `500`
- Semibold `600`

Fallback stack:

```css
"IBM Plex Mono", "SFMono-Regular", Menlo, Monaco, Consolas, "Liberation Mono", monospace
```

## Recommended Usage

### Standard OTW System

- Headlines: `IBM Plex Serif`
- Body copy: `Inter`
- Captions / labels / metadata / buttons: `Fira Code`

### Flagship / Premium OTW System

- Headlines: `IBM Plex Serif`
- Body copy: `IBM Plex Sans`
- Captions / labels / metadata: `IBM Plex Mono`

## Current Usage by Purpose

### Headlines

Primary:

- `IBM Plex Serif`

Seen on:

- [index.html](/Users/rylee_1/Projects/outsidetheworld/index.html)
- [personal.html](/Users/rylee_1/Projects/outsidetheworld/personal.html)
- [poetry.html](/Users/rylee_1/Projects/outsidetheworld/poetry.html)
- [change_log.html](/Users/rylee_1/Projects/outsidetheworld/change_log.html)
- [ghost-writer.html](/Users/rylee_1/Projects/outsidetheworld/ghost-writer.html)

### Body Copy

Primary:

- `Inter`

Seen on:

- [theme.css](/Users/rylee_1/Projects/outsidetheworld/theme.css)
- [personal.html](/Users/rylee_1/Projects/outsidetheworld/personal.html)
- [professional.html](/Users/rylee_1/Projects/outsidetheworld/professional.html)
- [findthesignal.html](/Users/rylee_1/Projects/outsidetheworld/findthesignal.html)
- [image_of_the_day.html](/Users/rylee_1/Projects/outsidetheworld/image_of_the_day.html)

Flagship exception:

- `IBM Plex Sans`

Seen on:

- [index.html](/Users/rylee_1/Projects/outsidetheworld/index.html)
- [gee_res.html](/Users/rylee_1/Projects/outsidetheworld/gee_res.html)

### Captions / Labels / Metadata

Primary:

- `Fira Code`

Used for:

- timestamps
- labels
- metadata chips
- archive/system text
- utility buttons

Flagship exception:

- `IBM Plex Mono`

Used on:

- [index.html](/Users/rylee_1/Projects/outsidetheworld/index.html)
- [gee_res.html](/Users/rylee_1/Projects/outsidetheworld/gee_res.html)

## Legacy / Limited Use

### Merriweather

- Role: older reading serif
- Current status: limited legacy presence
- Remaining known use: [wayback.html](/Users/rylee_1/Projects/outsidetheworld/wayback.html)

Recommendation:

- Prefer `IBM Plex Serif` for new work unless a page intentionally preserves older archive typography.

## Brand Summary

- `IBM Plex Serif` carries the OTW voice.
- `Inter` carries readability.
- `Fira Code` carries the signal/system identity.
- `IBM Plex Sans` and `IBM Plex Mono` are the polished flagship variants.

## Avoid

- Mixing too many font families on a single page.
- Using mono for long-form body copy.
- Using serif for dense utility UI.
- Switching between `Fira Code` and `IBM Plex Mono` on the same page without a clear hierarchy reason.
