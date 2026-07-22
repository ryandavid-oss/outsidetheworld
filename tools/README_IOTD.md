# Image of the Day Helper

The online `otw_app.html#iotd` publisher is the primary publishing path. It uses
Arizona's calendar date, uploads each image to a content-fingerprinted URL, and
asks for confirmation before adding another image to an occupied date.

Use this helper when adding a repo-local Image of the Day entry without the
online publisher.

## Usage

```bash
python3 tools/add_iotd_entry.py \
  --date 2026-03-11 \
  --title "DESERT_SIGNAL" \
  --caption "Short caption here." \
  --image Images/IOTD/2026-03-11.jpg
```

Captions accept light Markdown: paragraphs and line breaks, bold, italics,
links, lists, and blockquotes.

The helper will:

1. Add and sort the new entry in `image_manifest.json`
2. Validate the manifest
3. Allow multiple images on one date while rejecting duplicate IDs or images
4. Fail if the image file is missing
5. Rebuild the permanent image record, sitemap, and compact homepage payload

Responsive derivatives are generated separately so the published original
remains available for opening and downloading:

```bash
python3 tools/build_responsive_media.py --upload
```

That command updates `responsive_media.json`, refreshes
`frontpage_payload.json`, and uploads immutable WebP/JPEG sizes used by the
homepage and Image of the Day archive. Run it after adding or changing public
homepage media.

To repair one or two newly published images without regenerating the entire
media inventory, pass their exact public URLs:

```bash
python3 tools/build_responsive_media.py --upload \
  --source "https://otw-media.ryandavid.workers.dev/o/iotd/example.jpg"
```

## Recommended flow

1. Place the image file in `Images/IOTD/`
2. Run `add_iotd_entry.py`
3. Run `build_responsive_media.py --upload`
4. Review `git diff`
5. Commit

## Manifest identity

New online entries include `id` and `publishedAt`. The calendar `date` is for
display and grouping; it is not an image filename or a unique key. Older
entries without those fields remain supported.
