# Fragments Workflow

The legacy `Fragments` publisher is retired. `fragments_publisher.html` now redirects to `otw_app.html`, and active narrative authoring lives in `publisher.html`.

The public feed still reads from:

- `fragments_data.js`

That file remains the single source of truth for what appears on the site.

## Legacy Phone to Site Flow

1. Open the archived Fragments workflow if you intentionally restore it.
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

## OTW_Bot Helper

To add a real persistent `OTW_Bot` post into the feed:

```bash
python3 tools/add_otw_bot_fragment.py
```

That uses the built-in quip pool and writes a normal archived entry into `fragments_data.js`.

To supply your own bot line:

```bash
python3 tools/add_otw_bot_fragment.py --text "The machine has opinions about this particular mood."
```

To preview without writing:

```bash
python3 tools/add_otw_bot_fragment.py --dry-run
```
