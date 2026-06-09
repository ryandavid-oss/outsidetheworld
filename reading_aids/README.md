# Archive Reading Aids

Reading aids are reviewed, static sidecar files for archive essays. They are not embedded in essay markdown, and production archive pages only render sidecars with `"reviewStatus": "approved"`.

Required environment:

```bash
export OPENAI_API_KEY=...
```

Optional model override:

```bash
export OTW_READING_AID_MODEL=gpt-5.4-mini
```

Generate or update the latest essay and preview draft aids locally:

```bash
python tools/generate_reading_aids.py --latest --preview
```

Generate by title slug:

```bash
python tools/generate_reading_aids.py --slug different-mercies-of-the-same-light --preview
```

Approve after review:

```bash
python tools/generate_reading_aids.py --slug different-mercies-of-the-same-light --approve
```

Locked edits:

- Set `"locked": true` on `signalBrief` or an individual `readerMap`, `checkpoints`, or `plainSignals` item to preserve that author edit during regeneration.
- Locked paragraph notes are preserved by `paragraphId` or `afterParagraphId`; locked reader-map items are preserved by label.
- If a locked note points to a paragraph that no longer exists, validation warns clearly and the sidecar will not publish until fixed.

Preview and publishing behavior:

- `--preview` regenerates archive pages with draft aids visible by passing the explicit local preview flag to `narrative_sync.py`.
- Running `python narrative_sync.py` without preview only includes approved, current, valid reading aids.
- No browser-side AI calls are added. The only AI request is the local generator call to the configured OpenAI API.
