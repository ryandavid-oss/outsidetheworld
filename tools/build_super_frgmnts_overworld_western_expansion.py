#!/usr/bin/env python3
"""Build and review the Western Signal Flats Overworld expansion plate."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OVERWORLD = ROOT / "Design/Super-Frgmnts/Overworld"
PRODUCTION = OVERWORLD / "Production"
RAW = PRODUCTION / "Raw/western-signal-flats-raw-v1.png"
LANDING = PRODUCTION / "Plates/overworld-landing-flats-v1.png"
OUTPOST = PRODUCTION / "Plates/overworld-dras-outpost-v1.png"
THRESHOLD = PRODUCTION / "Plates/overworld-coreworks-threshold-v1.png"
OUTPUT = PRODUCTION / "Plates/overworld-western-signal-flats-v1.png"
RUNTIME = (
    ROOT
    / "Images/Game/Super-Frgmnts/overworld-western-signal-flats-v1.png"
)
REVIEWS = OVERWORLD / "Western-Signal-Flats/Reviews"
CONTACT = REVIEWS / "overworld-four-plate-contact-v1.png"
SEAM = REVIEWS / "western-to-landing-seam-audit-v1.png"

PLATE_SIZE = (1672, 941)
GROUND_Y = 744
FONT_PATH = "/System/Library/Fonts/SFNSMono.ttf"


def seam_delta(left: Image.Image, right: Image.Image, width: int = 1) -> float:
    left_edge = left.crop((left.width - width, 0, left.width, left.height))
    right_edge = right.crop((0, 0, width, right.height))
    means = ImageStat.Stat(ImageChops.difference(left_edge, right_edge)).mean
    return sum(means) / 3


def seam_structure_delta(
    left: Image.Image,
    right: Image.Image,
    width: int = 96,
) -> float:
    """Compare enough mirrored edge context to catch landscape discontinuities."""
    left_edge = left.crop(
        (left.width - width, 0, left.width, left.height)
    ).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    right_edge = right.crop((0, 0, width, right.height))
    means = ImageStat.Stat(
        ImageChops.difference(left_edge, right_edge)
    ).mean
    return sum(means) / 3


def validate_plate(image: Image.Image, name: str) -> Image.Image:
    assert image.size == PLATE_SIZE, (
        f"{name}: expected {PLATE_SIZE}, received {image.size}"
    )
    assert image.mode in {"RGB", "RGBA"}, f"{name}: unsupported {image.mode}"
    return image.convert("RGB")


def build_contact(plates: list[Image.Image]) -> Image.Image:
    labels = (
        "WESTERN SIGNAL FLATS",
        "LANDING FLATS",
        "DRAS OUTPOST",
        "COREWORKS THRESHOLD",
    )
    scale = 0.235
    preview_size = (
        round(PLATE_SIZE[0] * scale),
        round(PLATE_SIZE[1] * scale),
    )
    margin = 24
    label_height = 38
    width = preview_size[0] * 2 + margin * 3
    height = (preview_size[1] + label_height) * 2 + margin * 3
    sheet = Image.new("RGB", (width, height), (5, 8, 23))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(FONT_PATH, 17)

    for index, (plate, label) in enumerate(zip(plates, labels)):
        column = index % 2
        row = index // 2
        x = margin + column * (preview_size[0] + margin)
        y = margin + row * (preview_size[1] + label_height + margin)
        draw.text((x, y), label, fill=(247, 240, 234), font=font)
        y += label_height
        preview = plate.resize(preview_size, Image.Resampling.NEAREST)
        sheet.paste(preview, (x, y))
        draw.rectangle(
            (x, y, x + preview_size[0], y + preview_size[1]),
            outline=(88, 245, 223) if index == 0 else (241, 184, 91),
            width=2,
        )
    return sheet


def build_seam_review(left: Image.Image, right: Image.Image) -> Image.Image:
    crop_width = 420
    review = Image.new("RGB", (crop_width * 2, PLATE_SIZE[1]))
    review.paste(
        left.crop((left.width - crop_width, 0, left.width, left.height)),
        (0, 0),
    )
    review.paste(right.crop((0, 0, crop_width, right.height)), (crop_width, 0))
    return review


def main() -> None:
    west = validate_plate(Image.open(RAW), RAW.name)
    landing = validate_plate(Image.open(LANDING), LANDING.name)
    outpost = validate_plate(Image.open(OUTPOST), OUTPOST.name)
    threshold = validate_plate(Image.open(THRESHOLD), THRESHOLD.name)

    boundary_delta = seam_delta(west, landing)
    structure_delta = seam_structure_delta(west, landing)
    assert boundary_delta <= 0.1, (
        "Western-to-Landing boundary color delta is too high: "
        f"{boundary_delta:.2f}"
    )
    assert structure_delta <= 5, (
        "Western-to-Landing landscape continuity delta is too high: "
        f"{structure_delta:.2f}"
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    REVIEWS.mkdir(parents=True, exist_ok=True)
    west.save(OUTPUT, optimize=True)
    west.save(RUNTIME, optimize=True)
    build_contact([west, landing, outpost, threshold]).save(
        CONTACT, optimize=True
    )
    build_seam_review(west, landing).save(SEAM, optimize=True)

    assert Image.open(OUTPUT).size == PLATE_SIZE
    assert Image.open(RUNTIME).size == PLATE_SIZE
    assert GROUND_Y == 744

    print("SUPER FRGMNTS Western Signal Flats: BUILT")
    print(f"- runtime plate: {RUNTIME.relative_to(ROOT)}")
    print(f"- right-edge seam RGB delta: {boundary_delta:.2f}")
    print(f"- 96px landscape continuity delta: {structure_delta:.2f}")
    print("- four 1672 x 941 plates // world width 6688 // ground y 744")


if __name__ == "__main__":
    main()
