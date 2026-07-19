import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "image_manifest.json"
VALIDATOR_PATH = ROOT / "tools" / "validate_iotd_manifest.py"
DISCOVERY_BUILDER_PATH = ROOT / "tools" / "build_discovery.py"
FRONTPAGE_BUILDER_PATH = ROOT / "tools" / "build_frontpage_payload.py"


def load_manifest() -> list:
    if not MANIFEST_PATH.exists():
        return []

    try:
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: image_manifest.json is not valid JSON: {exc}") from exc

    if not isinstance(data, list):
        raise SystemExit("ERROR: image_manifest.json must contain an array")

    return data


def normalize_image_path(raw_path: str) -> str:
    raw = raw_path.strip()
    path = Path(raw)

    if path.is_absolute():
        try:
            rel = path.relative_to(ROOT)
            return rel.as_posix()
        except ValueError as exc:
            raise SystemExit("ERROR: absolute image path must be inside this repo") from exc

    return raw.lstrip("./")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Append a new Image of the Day entry to image_manifest.json"
    )
    parser.add_argument("--date", required=True, help="Date in YYYY-MM-DD format")
    parser.add_argument("--title", required=True, help="Display title")
    parser.add_argument("--caption", required=True, help="Caption text")
    parser.add_argument(
        "--image",
        required=True,
        help="Image path, e.g. Images/IOTD/2026-03-11.jpg",
    )
    args = parser.parse_args()

    date = args.date.strip()
    title = args.title.strip()
    caption = args.caption.strip()
    image = normalize_image_path(args.image)

    if len(date) != 10 or date[4] != "-" or date[7] != "-":
        raise SystemExit("ERROR: --date must be in YYYY-MM-DD format")

    if not title:
        raise SystemExit("ERROR: --title is required")

    if not caption:
        raise SystemExit("ERROR: --caption is required")

    if not image.startswith("Images/IOTD/"):
        raise SystemExit("ERROR: --image must point to Images/IOTD/")

    image_path = ROOT / image
    if not image_path.exists():
        raise SystemExit(f"ERROR: image file does not exist: {image}")

    manifest = load_manifest()

    if any(str(item.get("date", "")).strip() == date for item in manifest):
        raise SystemExit(f"ERROR: an entry already exists for {date}")

    if any(str(item.get("image", "")).strip() == image for item in manifest):
        raise SystemExit(f"ERROR: an entry already exists for image {image}")

    manifest.append(
        {
            "date": date,
            "title": title,
            "caption": caption,
            "image": image,
        }
    )

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=4) + "\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH)],
        cwd=ROOT,
        check=False,
    )

    if result.returncode != 0:
        return result.returncode

    discovery_result = subprocess.run(
        [sys.executable, str(DISCOVERY_BUILDER_PATH)],
        cwd=ROOT,
        check=False,
    )
    if discovery_result.returncode != 0:
        return discovery_result.returncode

    frontpage_result = subprocess.run(
        [sys.executable, str(FRONTPAGE_BUILDER_PATH)],
        cwd=ROOT,
        check=False,
    )
    if frontpage_result.returncode != 0:
        return frontpage_result.returncode

    print(f"OK: added IOTD entry and permanent record for {date}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
