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

Responsive derivatives are generated separately so the published original
remains available for opening and downloading:

```bash
python3 tools/build_responsive_media.py --upload
```

That command updates `responsive_media.json` and uploads immutable WebP/JPEG
sizes used by the homepage and Image of the Day archive. Run it after adding or
changing public homepage media.

## Recommended flow

1. Place the image file in `Images/IOTD/`
2. Run `add_iotd_entry.py`
3. Run `build_responsive_media.py --upload`
4. Review `git diff`
5. Commit
