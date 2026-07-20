import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "image_manifest.json"
IOTD_PUBLIC_BASE_URL = "https://otw-media.ryandavid.workers.dev/o/"


def fail(message: str) -> int:
    print(f"ERROR: {message}")
    return 1


def main() -> int:
    if not MANIFEST_PATH.exists():
        return fail("image_manifest.json is missing")

    try:
        items = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return fail(f"image_manifest.json is not valid JSON: {exc}")

    if not isinstance(items, list) or not items:
        return fail("image_manifest.json must be a non-empty array")

    date_counts: Counter[str] = Counter()
    seen_ids = set()
    seen_images = set()

    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            return fail(f"Entry {index} is not an object")

        date = str(item.get("date", "")).strip()
        title = str(item.get("title", "")).strip()
        caption = str(item.get("caption", "")).strip()
        image = str(item.get("image", "")).strip()
        entry_id = str(item.get("id", "")).strip()
        published_at = str(item.get("publishedAt", "")).strip()

        if not date or len(date) != 10:
            return fail(f"Entry {index} has an invalid date: {date!r}")
        if not title:
            return fail(f"Entry {index} is missing a title")
        if not image:
            return fail(f"Entry {index} is missing an image path")
        if not (
            image.startswith("Images/IOTD/")
            or image.startswith(IOTD_PUBLIC_BASE_URL)
        ):
            return fail(
                f"Entry {index} image must live under Images/IOTD/ or the IOTD R2 public URL: {image}"
            )
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return fail(f"Entry {index} has an invalid calendar date: {date!r}")
        if entry_id and entry_id in seen_ids:
            return fail(f"Duplicate id detected: {entry_id}")
        if image in seen_images:
            return fail(f"Duplicate image detected: {image}")
        if published_at:
            try:
                datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            except ValueError:
                return fail(f"Entry {index} has an invalid publishedAt value: {published_at!r}")

        if image.startswith("Images/IOTD/"):
            image_path = ROOT / image
            if not image_path.exists():
                return fail(f"Image file does not exist for entry {index}: {image}")

            filename_date = image_path.stem
        else:
            filename_date = Path(image).stem

        if entry_id and filename_date != entry_id:
            return fail(f"Entry {index} id {entry_id!r} does not match image filename {Path(image).name!r}")
        if not filename_date.startswith(date):
            print(
                f"WARNING: entry {index} date {date} does not match filename {Path(image).name}"
            )

        date_counts[date] += 1
        if entry_id:
            seen_ids.add(entry_id)
        seen_images.add(image)

    shared_dates = [date for date, count in date_counts.items() if count > 1]
    if shared_dates:
        print(f"INFO: multiple images are recorded for {', '.join(sorted(shared_dates))}")
    print(f"OK: validated {len(items)} image manifest entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
