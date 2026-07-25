#!/usr/bin/env python3
"""Build the Phase 2B Coreworks overworld production landscape."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_DIR = (
    ROOT / "Design" / "Super-Frgmnts" / "Overworld" / "Production"
)
MANIFEST_PATH = PRODUCTION_DIR / "production-manifest.json"

FONT_PATH = "/System/Library/Fonts/SFNSMono.ttf"
FONT_BOLD_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

COLORS = {
    "background": (5, 8, 23),
    "ink": (247, 240, 234),
    "cyan": (75, 243, 226),
    "amber": (241, 184, 91),
    "orange": (240, 117, 69),
    "muted": (189, 198, 220),
}


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD_PATH if bold else FONT_PATH, size)


def load_manifest() -> dict:
    with MANIFEST_PATH.open(encoding="utf-8") as source:
        return json.load(source)


def validate_manifest(manifest: dict) -> None:
    target = manifest["target_plate"]
    world = manifest["world"]
    plates = manifest["plates"]

    assert target == {"width": 1672, "height": 941, "ground_y": 744}
    assert world["width"] == target["width"] * world["plate_count"]
    assert world["height"] == target["height"]
    assert world["seams_x"] == [target["width"], target["width"] * 2]
    assert world["plate_count"] == len(plates) == 3

    for plate in plates:
        assert plate["target_ground_y"] == target["ground_y"]
        assert (
            plate["target_ground_y"] - plate["source_ground_y"]
            == plate["vertical_shift"]
        )
        assert (PRODUCTION_DIR / plate["raw"]).is_file(), plate["raw"]


def fit_width(image: Image.Image, width: int) -> Image.Image:
    if image.width == width:
        return image
    if image.width > width:
        return image.crop((0, 0, width, image.height))

    missing = width - image.width
    edge = image.crop((image.width - 1, 0, image.width, image.height))
    extension = Image.new("RGB", (missing, image.height))
    for x in range(missing):
        extension.paste(edge, (x, 0))
    output = Image.new("RGB", (width, image.height))
    output.paste(image, (0, 0))
    output.paste(extension, (image.width, 0))
    return output


def fit_height(image: Image.Image, height: int) -> Image.Image:
    if image.height == height:
        return image
    if image.height > height:
        return image.crop((0, 0, image.width, height))

    missing = height - image.height
    edge = image.crop((0, image.height - 1, image.width, image.height))
    extension = Image.new("RGB", (image.width, missing))
    for y in range(missing):
        extension.paste(edge, (0, y))
    output = Image.new("RGB", (image.width, height))
    output.paste(image, (0, 0))
    output.paste(extension, (0, image.height))
    return output


def align_ground(
    image: Image.Image,
    *,
    source_ground_y: int,
    target_ground_y: int,
    target_size: tuple[int, int],
) -> Image.Image:
    width, height = target_size
    image = fit_height(fit_width(image.convert("RGB"), width), height)
    shift_up = source_ground_y - target_ground_y
    if shift_up < 0:
        raise ValueError("Production builder only supports upward ground alignment")
    if shift_up == 0:
        return image

    output = Image.new("RGB", target_size, image.getpixel((0, image.height - 1)))
    output.paste(image, (0, -shift_up))

    # Mirror the hidden bottom tail. This avoids a flat repeated scanline while
    # keeping the extension below the playable floor visually quiet.
    source_tail = image.crop(
        (0, image.height - shift_up, image.width, image.height)
    )
    source_tail = ImageOps.flip(source_tail)
    output.paste(source_tail, (0, height - shift_up))
    return output


def average_strip(
    image: Image.Image,
    box: tuple[int, int, int, int],
) -> tuple[int, int, int]:
    pixels = list(image.crop(box).get_flattened_data())
    count = max(1, len(pixels))
    return tuple(sum(pixel[channel] for pixel in pixels) // count for channel in range(3))


def clamp_channel(value: float) -> int:
    return max(0, min(255, round(value)))


def harmonize_pair(
    left: Image.Image,
    right: Image.Image,
    *,
    band_width: int,
    sample_width: int = 8,
    correction_limit: int = 24,
) -> tuple[Image.Image, Image.Image, float, float]:
    if left.size != right.size:
        raise ValueError("Seam pair plates must share dimensions")

    width, height = left.size
    left = left.copy()
    right = right.copy()
    before_total = 0.0
    after_total = 0.0

    left_pixels = left.load()
    right_pixels = right.load()

    for y in range(height):
        left_average = average_strip(
            left, (width - sample_width, y, width, y + 1)
        )
        right_average = average_strip(
            right, (0, y, sample_width, y + 1)
        )
        midpoint = tuple(
            (left_average[channel] + right_average[channel]) / 2
            for channel in range(3)
        )

        left_delta = tuple(
            max(
                -correction_limit,
                min(correction_limit, midpoint[channel] - left_average[channel]),
            )
            for channel in range(3)
        )
        right_delta = tuple(
            max(
                -correction_limit,
                min(correction_limit, midpoint[channel] - right_average[channel]),
            )
            for channel in range(3)
        )

        before_total += sum(
            abs(left_average[channel] - right_average[channel])
            for channel in range(3)
        ) / 3

        for offset in range(band_width):
            left_weight = (offset + 1) / band_width
            right_weight = (band_width - offset) / band_width
            left_x = width - band_width + offset
            right_x = offset

            left_pixel = left_pixels[left_x, y]
            right_pixel = right_pixels[right_x, y]
            left_pixels[left_x, y] = tuple(
                clamp_channel(
                    left_pixel[channel] + left_delta[channel] * left_weight
                )
                for channel in range(3)
            )
            right_pixels[right_x, y] = tuple(
                clamp_channel(
                    right_pixel[channel] + right_delta[channel] * right_weight
                )
                for channel in range(3)
            )

        corrected_left = average_strip(
            left, (width - sample_width, y, width, y + 1)
        )
        corrected_right = average_strip(
            right, (0, y, sample_width, y + 1)
        )
        after_total += sum(
            abs(corrected_left[channel] - corrected_right[channel])
            for channel in range(3)
        ) / 3

    return (
        left,
        right,
        before_total / height,
        after_total / height,
    )


def assemble_master(plates: list[Image.Image]) -> Image.Image:
    width = sum(plate.width for plate in plates)
    height = plates[0].height
    master = Image.new("RGB", (width, height))
    x = 0
    for plate in plates:
        if plate.height != height:
            raise ValueError("All production plates must share height")
        master.paste(plate, (x, 0))
        x += plate.width
    return master


def build_contact_sheet(plates: list[Image.Image], manifest: dict) -> Image.Image:
    scale = 0.31
    margin = 32
    label_height = 50
    preview_width = round(plates[0].width * scale)
    preview_height = round(plates[0].height * scale)
    width = preview_width * len(plates) + margin * (len(plates) + 1)
    height = preview_height + margin * 2 + label_height
    sheet = Image.new("RGB", (width, height), COLORS["background"])
    draw = ImageDraw.Draw(sheet)
    outlines = (COLORS["cyan"], COLORS["amber"], COLORS["orange"])

    for index, (plate, metadata) in enumerate(zip(plates, manifest["plates"])):
        x = margin + index * (preview_width + margin)
        y = margin + label_height
        preview = plate.resize(
            (preview_width, preview_height), Image.Resampling.NEAREST
        )
        sheet.paste(preview, (x, y))
        draw.rectangle(
            (x, y, x + preview_width, y + preview_height),
            outline=outlines[index],
            width=3,
        )
        draw.text(
            (x, margin),
            f"PLATE {index + 1} // {metadata['name'].upper()}",
            font=font(22, bold=True),
            fill=COLORS["ink"],
        )
    return sheet


def build_seam_audit(master: Image.Image, manifest: dict) -> Image.Image:
    crop_width = 900
    label_height = 60
    seams = manifest["world"]["seams_x"]
    output = Image.new(
        "RGB",
        (crop_width, master.height * len(seams) + label_height * len(seams)),
        COLORS["background"],
    )
    draw = ImageDraw.Draw(output)

    y = 0
    labels = (
        "SEAM 1 // LANDING FLATS → DRAS OUTPOST",
        "SEAM 2 // DRAS OUTPOST → COREWORKS THRESHOLD",
    )
    for seam, label in zip(seams, labels):
        crop = master.crop(
            (
                seam - crop_width // 2,
                0,
                seam + crop_width // 2,
                master.height,
            )
        )
        output.paste(crop, (0, y))
        draw.line(
            (crop_width // 2, y, crop_width // 2, y + master.height),
            fill=COLORS["cyan"],
            width=2,
        )
        y += master.height
        draw.rectangle(
            (0, y, crop_width, y + label_height), fill=COLORS["background"]
        )
        draw.text(
            (20, y + 16),
            label,
            font=font(21, bold=True),
            fill=COLORS["ink"],
        )
        y += label_height
    return output


def main() -> None:
    manifest = load_manifest()
    validate_manifest(manifest)
    target = manifest["target_plate"]
    target_size = (target["width"], target["height"])

    plates = []
    for metadata in manifest["plates"]:
        raw = Image.open(PRODUCTION_DIR / metadata["raw"])
        plate = align_ground(
            raw,
            source_ground_y=metadata["source_ground_y"],
            target_ground_y=metadata["target_ground_y"],
            target_size=target_size,
        )
        plates.append(plate)

    seam_metrics = []
    for index in range(len(plates) - 1):
        left, right, before, after = harmonize_pair(
            plates[index],
            plates[index + 1],
            band_width=manifest["seam_harmonization_width"],
        )
        plates[index] = left
        plates[index + 1] = right
        seam_metrics.append((before, after))

    for plate, metadata in zip(plates, manifest["plates"]):
        output_path = PRODUCTION_DIR / metadata["output"]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plate.save(output_path, optimize=True)

    outputs = manifest["outputs"]
    master = assemble_master(plates)
    master_path = PRODUCTION_DIR / outputs["master"]
    master.save(master_path, optimize=True)

    contact_sheet = build_contact_sheet(plates, manifest)
    contact_sheet.save(PRODUCTION_DIR / outputs["contact_sheet"], optimize=True)

    seam_audit = build_seam_audit(master, manifest)
    seam_audit.save(PRODUCTION_DIR / outputs["seam_audit"], optimize=True)

    assert master.size == (
        manifest["world"]["width"],
        manifest["world"]["height"],
    )
    for plate in plates:
        assert plate.size == target_size

    print(f"Built {master_path.relative_to(ROOT)}")
    for index, (before, after) in enumerate(seam_metrics, start=1):
        print(
            f"Seam {index} mean boundary RGB delta: "
            f"{before:.2f} → {after:.2f}"
        )
    print(
        "Validated three 1672×941 plates, 5016×941 master, "
        "y=744 ground alignment, and both seams."
    )


if __name__ == "__main__":
    main()
