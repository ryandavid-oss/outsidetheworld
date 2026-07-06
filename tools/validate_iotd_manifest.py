import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "image_manifest.json"
IOTD_PUBLIC_BASE_URL = "https://pub-fd35040d2a3b40af985b8aa67b98eaa8.r2.dev/"


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

    seen_dates = set()
    seen_images = set()

    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            return fail(f"Entry {index} is not an object")

        date = str(item.get("date", "")).strip()
        title = str(item.get("title", "")).strip()
        caption = str(item.get("caption", "")).strip()
        image = str(item.get("image", "")).strip()

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
        if date in seen_dates:
            return fail(f"Duplicate date detected: {date}")
        if image in seen_images:
            return fail(f"Duplicate image detected: {image}")

        if image.startswith("Images/IOTD/"):
            image_path = ROOT / image
            if not image_path.exists():
                return fail(f"Image file does not exist for entry {index}: {image}")

            filename_date = image_path.stem
        else:
            filename_date = Path(image).stem

        if filename_date != date:
            print(
                f"WARNING: entry {index} date {date} does not match filename {Path(image).name}"
            )

        seen_dates.add(date)
        seen_images.add(image)

    print(f"OK: validated {len(items)} image manifest entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
