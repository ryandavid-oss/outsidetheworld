#!/usr/bin/env python3
"""Verify The Wound v3 wide boss-room background package."""

from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Boss-Room"
)
MASTER = (
    PACKAGE
    / "Raw"
    / "wound-boss-room-background-master-v3.png"
)
SOURCE = (
    PACKAGE
    / "Raw"
    / "wound-boss-room-background-master-v3-source.png"
)
RUNTIME_SLICES = (
    (
        ROOT
        / "Images"
        / "Game"
        / "Super-Frgmnts"
        / "foundry-wound-boss-room-background-runtime-v3-left.png"
    ),
    (
        ROOT
        / "Images"
        / "Game"
        / "Super-Frgmnts"
        / "foundry-wound-boss-room-background-runtime-v3-right.png"
    ),
)
TITLE_RUNTIME = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "foundry-wound-boss-room-title-runtime-v3.png"
)
REVIEWS = (
    PACKAGE / "Reviews" / "wound-boss-room-scale-review-v3.png",
    PACKAGE / "Reviews" / "wound-boss-room-sweep-review-v3.png",
)
CONTRACT = PACKAGE / "WOUND-BOSS-ROOM-BACKGROUND-v3.md"
BUILD_SCRIPT = ROOT / "tools" / "build_super_frgmnts_wound_boss_room.py"
EXPECTED_SIZE = (2580, 1882)
EXPECTED_SLICE_SIZE = (1290, 1882)


def main() -> int:
    failures: list[str] = []

    for path in (
        SOURCE,
        MASTER,
        CONTRACT,
        BUILD_SCRIPT,
        TITLE_RUNTIME,
        *RUNTIME_SLICES,
        *REVIEWS,
    ):
        if not path.exists():
            failures.append(f"missing {path.relative_to(ROOT)}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    with Image.open(MASTER) as source:
        master = source.convert("RGB")
        if source.size != EXPECTED_SIZE:
            failures.append(f"master size is {source.size}")
        if source.mode != "RGB":
            failures.append(f"master mode is {source.mode}, expected RGB")

    runtime = Image.new("RGB", EXPECTED_SIZE)
    for index, runtime_path in enumerate(RUNTIME_SLICES):
        with Image.open(runtime_path) as source:
            runtime_slice = source.convert("RGB")
            if source.size != EXPECTED_SLICE_SIZE:
                failures.append(
                    f"{runtime_path.name} size is {source.size}"
                )
            if source.mode != "RGB":
                failures.append(
                    f"{runtime_path.name} mode is {source.mode}, "
                    "expected RGB"
                )
            runtime.paste(
                runtime_slice,
                (index * EXPECTED_SLICE_SIZE[0], 0),
            )

    if ImageChops.difference(master, runtime).getbbox() is not None:
        failures.append("stitched runtime slices differ from the master")

    with Image.open(TITLE_RUNTIME) as title:
        if title.size != (1290, 941):
            failures.append(
                f"title runtime size is {title.size}"
            )
        if title.mode != "RGB":
            failures.append(
                f"title runtime mode is {title.mode}, expected RGB"
            )

    for review_path in REVIEWS:
        with Image.open(review_path) as review:
            if review.size != EXPECTED_SIZE:
                failures.append(
                    f"{review_path.name} size is {review.size}"
                )

    if max(EXPECTED_SLICE_SIZE) > 2048:
        failures.append("a runtime slice exceeds the 2,048-pixel axis limit")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("PASS: The Wound v3 wide boss-room package is valid")
    print("- stitched runtime slices are pixel-identical to the RGB master")
    print("- master and reviews are 2,580 × 1,882 pixels")
    print("- both runtime slices stay within the 2,048-pixel axis limit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
