# Image of the Day Helper

Use this helper to add a new Image of the Day entry without hand-editing `image_manifest.json`.

## Usage

```bash
python3 tools/add_iotd_entry.py \
  --date 2026-03-11 \
  --title "DESERT_SIGNAL" \
  --caption "Short caption here." \
  --image Images/IOTD/2026-03-11.jpg
```

The helper will:

1. Append the new entry to `image_manifest.json`
2. Validate the manifest
3. Fail if the date or image already exists
4. Fail if the image file is missing
5. Rebuild the permanent image record and sitemap

## Recommended flow

1. Place the image file in `Images/IOTD/`
2. Run `add_iotd_entry.py`
3. Review `git diff`
4. Commit
