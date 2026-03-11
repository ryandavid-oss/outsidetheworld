# Outside the World

This repository contains the live `outsidetheworld` site, historical artifacts, imported media archives, and small automation scripts used to refresh page data.

## Top-level layout

- `*.html`: Public page entry points. Keep these paths stable unless you are intentionally changing a public URL.
- `Images/`, `media/`: Public-facing assets used by the live pages.
- `OTW Archive/`, `Archive_Construction_Debris/`, `Stories/`, `blogger_posts/`, `Repaired/`: Historical imports and archive material.
- `tools/`: Utility scripts for media cleanup and data generation.
- `.github/workflows/`: GitHub Actions that refresh site data after content changes.

## Pinned root data files

These files are intentionally kept at the repository root because live HTML pages reference them directly:

- `changelog.json`
- `favorites_manifest.json`
- `hipsta_manifest.json`
- `image_manifest.json`
- `insta_manifest.json`
- `shirt_scripting.json`
- `poetry_data.js`
- `narrative_data.js`
- `wayback_purified.js`

Before moving any of those files, update every consuming page and verify the site paths still resolve correctly.

## Current cleanup rule

For structure changes, prefer:

1. Leave public HTML entry points in place.
2. Leave pinned root data files in place.
3. Reorganize only tooling, docs, and clearly internal files first.
