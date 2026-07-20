#!/usr/bin/env python3
"""Regression checks for Image of the Day identity, dating, and rendering."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"ERROR: {message}")


def main() -> int:
    manifest = json.loads((ROOT / "image_manifest.json").read_text(encoding="utf-8"))
    responsive = json.loads((ROOT / "responsive_media.json").read_text(encoding="utf-8"))["sources"]

    ids = [str(item.get("id") or "") for item in manifest if item.get("id")]
    images = [str(item.get("image") or "") for item in manifest]
    require(len(ids) == len(set(ids)), "IOTD ids must be unique")
    require(len(images) == len(set(images)), "IOTD image URLs must be unique")

    repaired = {
        "CUTE_LITTLE_CAR": ("2026-07-18", "dc899bac89e3"),
        "BLESSED_RAIN": ("2026-07-19", "7a810ca618f3"),
        "THE_FIRE_DRAGON": ("2026-07-20", "1f92010c12c6"),
    }
    by_title = {str(item.get("title") or ""): item for item in manifest}
    for title, (date, fingerprint) in repaired.items():
        item = by_title.get(title)
        require(bool(item), f"missing repaired record {title}")
        require(item["date"] == date, f"{title} must be dated {date}")
        require(str(item.get("id") or "").endswith(fingerprint), f"{title} id lost its fingerprint")
        require(str(item["image"]).endswith(f"{fingerprint}.jpg"), f"{title} image is not immutable")
        require(item["image"] in responsive, f"{title} has no responsive media record")

    fire_caption = str(by_title["THE_FIRE_DRAGON"].get("caption") or "").replace("\r\n", "\n")
    require("\n\n" in fire_caption, "IOTD paragraph breaks were flattened in the manifest")

    publisher = (ROOT / "otw_app.html").read_text(encoding="utf-8")
    require("America/Phoenix" in publisher, "publisher date is not pinned to Arizona")
    require("IOTD_DATE_OCCUPIED" in publisher, "publisher lacks same-date confirmation")
    require("data-iotd-format" in publisher, "publisher lacks caption formatting controls")

    for filename in ("image_of_the_day.html", "IOTD_Main.html"):
        source = (ROOT / filename).read_text(encoding="utf-8")
        require("renderOtwMarkdown" in source, f"{filename} does not render Markdown captions")
        require("seenEntries" in source and "seenDates" not in source, f"{filename} still discards same-date images")

    print("OK: IOTD dates, immutable identity, responsive media, and rich captions are intact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
