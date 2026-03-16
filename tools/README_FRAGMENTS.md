# Fragments Workflow

The `Fragments` app is a mobile-friendly drafting and staging tool.

The public feed still reads from:

- `fragments_data.js`

That file remains the single source of truth for what appears on the site.

## Phone to Site Flow

1. Open `fragments_publisher.html` on your phone.
2. Write a fragment and tap `Stage Fragment`.
3. Tap `Download Outbox` to export a JSON file.
4. On your Mac, import that JSON into `fragments_data.js`.
5. Commit and push.

## Import Command

From the repo root:

```bash
python3 tools/import_fragments_outbox.py ~/Downloads/fragments-outbox-2026-03-15.json
```

What it does:

- reads the exported JSON outbox
- normalizes tags to OTW-style uppercase labels
- rejects malformed entries
- deduplicates exact matches
- prepends the new fragments into `fragments_data.js`
- keeps newest entries first

## Dry Run

To validate the file before writing:

```bash
python3 tools/import_fragments_outbox.py ~/Downloads/fragments-outbox-2026-03-15.json --dry-run
```

## After Import

Publish normally:

```bash
git add fragments_data.js
git commit -m "Add fragments"
git push
```
