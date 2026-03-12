# Changelog Helper

Use this helper to append a changelog entry without hand-editing `changelog.json`.

## Usage

```bash
python3 tools/add_changelog_entry.py \
  --date 2026-03-11 \
  --type Tweak \
  --text "Updated homepage layout and promoted the new index."
```

The helper will:

1. Add the new entry
2. De-duplicate exact duplicates
3. Sort newest date first
4. Write back to `changelog.json`
