#!/usr/bin/env python3
"""Build the Phase 1 Coreworks overworld composition guides."""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "Design" / "Super-Frgmnts" / "Overworld"
MANIFEST_PATH = OUTPUT_DIR / "overworld-layout.json"
GUIDE_PATH = OUTPUT_DIR / "overworld-composition-guide.png"
CONTACT_SHEET_PATH = OUTPUT_DIR / "overworld-plates-contact-sheet.png"

FONT_PATH = "/System/Library/Fonts/SFNSMono.ttf"
FONT_BOLD_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

COLORS = {
    "ink": (247, 240, 234, 255),
    "muted": (189, 198, 220, 255),
    "cyan": (75, 243, 226, 255),
    "cyan_dim": (42, 159, 199, 255),
    "magenta": (232, 78, 173, 255),
    "amber": (241, 184, 91, 255),
    "orange": (240, 117, 69, 255),
    "blue": (119, 163, 255, 255),
    "panel": (5, 8, 23, 226),
    "grid": (125, 154, 210, 42),
    "collision": (75, 243, 226, 34),
    "interaction": (232, 78, 173, 24),
}


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD_PATH if bold else FONT_PATH, size)


def load_manifest() -> dict:
    with MANIFEST_PATH.open(encoding="utf-8") as source:
        return json.load(source)


def validate(manifest: dict) -> None:
    coordinates = manifest["coordinate_system"]
    world_width = coordinates["world_width"]
    world_height = coordinates["world_height"]
    plate_width = coordinates["plate_width"]
    plate_height = coordinates["plate_height"]
    seams = coordinates["plate_seams_x"]

    assert world_width == plate_width * 3
    assert world_height == plate_height
    assert seams == [plate_width, plate_width * 2]
    assert len(manifest["plates"]) == 3
    assert [plate["x"] for plate in manifest["plates"]] == [
        0,
        plate_width,
        plate_width * 2,
    ]

    floor = next(item for item in manifest["collision"] if item["id"] == "desert_floor")
    assert floor["y"] == coordinates["ground_y"]
    assert floor["x"] >= 0
    assert floor["x"] + floor["width"] <= world_width

    for collection_name in ("anchors", "interaction_zones"):
        for item in manifest[collection_name]:
            assert 0 <= item["x"] < world_width, item["id"]
            assert 0 <= item["y"] < world_height, item["id"]
            assert item["x"] + item["width"] <= world_width, item["id"]
            assert item["y"] + item["height"] <= world_height, item["id"]

    for anchor in manifest["anchors"]:
        if anchor["z_layer"] not in {"far-mountains", "midground-ruins"}:
            assert not any(
                anchor["x"] < seam < anchor["x"] + anchor["width"]
                for seam in seams
            ), f"{anchor['id']} straddles a plate seam"


def vertical_gradient(
    size: tuple[int, int],
    stops: list[tuple[float, tuple[int, int, int]]],
) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size)
    pixels = image.load()
    for y in range(height):
        position = y / max(1, height - 1)
        for index in range(len(stops) - 1):
            start_position, start_color = stops[index]
            end_position, end_color = stops[index + 1]
            if start_position <= position <= end_position:
                span = max(0.0001, end_position - start_position)
                amount = (position - start_position) / span
                color = tuple(
                    round(start_color[channel] * (1 - amount) + end_color[channel] * amount)
                    for channel in range(3)
                )
                break
        else:
            color = stops[-1][1]
        for x in range(width):
            pixels[x, y] = (*color, 255)
    return image


def text_box(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    *,
    fill: tuple[int, int, int, int] = COLORS["ink"],
    outline: tuple[int, int, int, int] = COLORS["blue"],
    background: tuple[int, int, int, int] = COLORS["panel"],
    size: int = 16,
    bold: bool = False,
    padding: int = 7,
) -> tuple[int, int, int, int]:
    label_font = font(size, bold=bold)
    left, top, right, bottom = draw.textbbox(xy, text, font=label_font)
    box = (
        left - padding,
        top - padding,
        right + padding,
        bottom + padding,
    )
    draw.rounded_rectangle(box, radius=3, fill=background, outline=outline, width=2)
    draw.text(xy, text, font=label_font, fill=fill)
    return box


def draw_cloud(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    alpha: int,
) -> None:
    color = (209, 187, 213, alpha)
    points = []
    for step in range(13):
        px = x + round(width * step / 12)
        py = y + round(math.sin(step * 0.85) * 8)
        points.append((px, py))
    draw.line(points, fill=color, width=5)
    draw.line([(px, py + 10) for px, py in points], fill=(186, 142, 183, alpha // 2), width=2)


def draw_background(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    rng = random.Random(73)

    for _ in range(115):
        x = rng.randrange(width)
        y = rng.randrange(80, 410)
        radius = rng.choice((1, 1, 1, 2))
        alpha = rng.randrange(35, 105)
        draw.ellipse((x, y, x + radius, y + radius), fill=(225, 220, 232, alpha))

    draw_cloud(draw, 180, 210, 670, 52)
    draw_cloud(draw, 1010, 292, 560, 38)
    draw_cloud(draw, 1780, 190, 710, 44)
    draw_cloud(draw, 2600, 268, 520, 56)
    draw_cloud(draw, 3400, 188, 760, 42)
    draw_cloud(draw, 4260, 282, 570, 58)

    far_mountains = [
        (0, 604),
        (160, 512),
        (320, 556),
        (520, 430),
        (720, 530),
        (920, 446),
        (1110, 562),
        (1320, 452),
        (1510, 558),
        (1700, 472),
        (1910, 542),
        (2110, 438),
        (2290, 552),
        (2440, 462),
        (2590, 548),
        (2780, 426),
        (2980, 540),
        (3160, 458),
        (3344, 536),
        (3540, 448),
        (3720, 558),
        (3900, 430),
        (4100, 556),
        (4280, 440),
        (4470, 548),
        (4660, 454),
        (4850, 550),
        (width, 480),
        (width, 744),
        (0, 744),
    ]
    draw.polygon(far_mountains, fill=(28, 25, 58, 255))

    volcano = [
        (3680, 660),
        (3940, 360),
        (4200, 222),
        (4280, 260),
        (4360, 372),
        (4650, 660),
    ]
    draw.polygon(volcano, fill=(35, 24, 48, 255))
    draw.line([(4170, 258), (4200, 222), (4236, 251)], fill=(240, 117, 69, 220), width=8)
    draw.line([(4192, 249), (4220, 235)], fill=(98, 224, 210, 180), width=3)
    draw.ellipse((4140, 78, 4310, 236), fill=(101, 70, 102, 34))
    draw.ellipse((4170, 46, 4360, 202), fill=(88, 67, 101, 25))

    near_mountains = [
        (0, 684),
        (190, 596),
        (400, 650),
        (620, 548),
        (870, 672),
        (1110, 576),
        (1370, 670),
        (1600, 570),
        (1840, 676),
        (2070, 586),
        (2290, 680),
        (2530, 584),
        (2780, 680),
        (3040, 566),
        (3344, 664),
        (3550, 574),
        (3770, 680),
        (4010, 582),
        (4250, 676),
        (4490, 566),
        (4740, 674),
        (width, 584),
        (width, 744),
        (0, 744),
    ]
    draw.polygon(near_mountains, fill=(43, 28, 58, 255))

    for x in (560, 2420, 2780, 3500):
        draw.line((x, 486, x - 8, 700), fill=(74, 53, 79, 255), width=11)
        draw.line((x, 486, x + 28, 508), fill=(74, 53, 79, 255), width=7)

    # Collapsed viaduct and broken cables on the settlement plate.
    draw.line((2460, 504, 4200, 470), fill=(66, 55, 76, 255), width=14)
    draw.line((2460, 504, 3370, 528), fill=(102, 65, 83, 255), width=4)
    for x in range(2500, 4180, 132):
        draw.line((x, 486, x - 28, 690), fill=(61, 48, 70, 255), width=8)
    draw.arc((3050, 470, 3510, 650), 190, 350, fill=(87, 60, 82, 255), width=4)
    draw.arc((3320, 450, 3860, 650), 190, 350, fill=(79, 54, 76, 255), width=3)


def draw_ground(draw: ImageDraw.ImageDraw, manifest: dict) -> None:
    ground_y = manifest["coordinate_system"]["ground_y"]
    width = manifest["coordinate_system"]["world_width"]
    draw.rectangle((0, ground_y, width, 941), fill=(43, 25, 42, 255))
    draw.polygon(
        [
            (0, ground_y),
            (250, ground_y - 18),
            (520, ground_y + 4),
            (850, ground_y - 12),
            (1130, ground_y + 2),
            (1460, ground_y - 8),
            (1770, ground_y + 5),
            (2070, ground_y - 10),
            (2360, ground_y + 4),
            (2700, ground_y - 8),
            (3000, ground_y + 3),
            (3344, ground_y - 12),
            (3650, ground_y + 3),
            (3980, ground_y - 10),
            (4320, ground_y + 4),
            (4680, ground_y - 8),
            (width, ground_y + 2),
            (width, ground_y + 42),
            (0, ground_y + 42),
        ],
        fill=(115, 62, 64, 255),
    )
    draw.line((64, ground_y, width - 64, ground_y), fill=COLORS["cyan"], width=3)
    draw.line((64, ground_y + 7, width - 64, ground_y + 7), fill=(232, 78, 173, 110), width=2)

    # Buried freight-road fragments.
    for x in range(2560, 4560, 132):
        draw.rounded_rectangle(
            (x, ground_y - 7, x + 102, ground_y + 10),
            radius=2,
            fill=(75, 61, 76, 255),
            outline=(129, 91, 100, 255),
            width=2,
        )

    tutorial_rock = next(
        item for item in manifest["collision"] if item["id"] == "tutorial_rock"
    )
    rock_x = tutorial_rock["x"]
    rock_y = tutorial_rock["y"]
    rock_right = rock_x + tutorial_rock["width"]
    draw.polygon(
        [
            (rock_x, ground_y),
            (rock_x + 18, rock_y + 16),
            (rock_x + 54, rock_y),
            (rock_right - 24, rock_y + 8),
            (rock_right, ground_y),
        ],
        fill=(93, 55, 65, 255),
        outline=(196, 122, 86, 255),
    )


def anchor_by_id(manifest: dict, anchor_id: str) -> dict:
    return next(anchor for anchor in manifest["anchors"] if anchor["id"] == anchor_id)


def draw_ship(draw: ImageDraw.ImageDraw, anchor: dict) -> None:
    x, y, w, h = (anchor[key] for key in ("x", "y", "width", "height"))
    center = x + w // 2
    body = [
        (x, y + round(h * 0.72)),
        (x + round(w * 0.22), y + round(h * 0.30)),
        (center - round(w * 0.12), y + round(h * 0.18)),
        (center, y + round(h * 0.36)),
        (center + round(w * 0.12), y + round(h * 0.18)),
        (x + round(w * 0.78), y + round(h * 0.30)),
        (x + w, y + round(h * 0.72)),
        (x + round(w * 0.72), y + round(h * 0.88)),
        (center, y + h),
        (x + round(w * 0.28), y + round(h * 0.88)),
    ]
    draw.polygon(body, fill=(38, 45, 111, 255), outline=(119, 163, 255, 255))
    draw.polygon(
        [
            (center - round(w * 0.13), y + round(h * 0.42)),
            (center, y + round(h * 0.29)),
            (center + round(w * 0.13), y + round(h * 0.42)),
            (center, y + round(h * 0.77)),
        ],
        fill=(75, 243, 226, 210),
    )
    for lamp_x in (x + round(w * 0.21), x + round(w * 0.79)):
        draw.ellipse(
            (lamp_x - 9, y + round(h * 0.54) - 9, lamp_x + 9, y + round(h * 0.54) + 9),
            fill=COLORS["magenta"],
        )


def draw_dras(draw: ImageDraw.ImageDraw, anchor: dict) -> None:
    x, y, w, h = (anchor[key] for key in ("x", "y", "width", "height"))
    draw.line((x + 12, y + 4, x + 12, y + h), fill=(241, 184, 91, 255), width=5)
    draw.ellipse((x + 30, y, x + 68, y + 38), fill=(207, 184, 165, 255), outline=COLORS["ink"])
    draw.polygon(
        [
            (x + 24, y + 34),
            (x + 76, y + 34),
            (x + 88, y + h),
            (x + 16, y + h),
        ],
        fill=(126, 78, 54, 255),
        outline=(241, 184, 91, 255),
    )
    draw.line((x + 30, y + 52, x + 74, y + 52), fill=(137, 56, 64, 255), width=8)
    draw.ellipse((x + 46, y + 57, x + 56, y + 67), fill=COLORS["cyan"])


def draw_camp(draw: ImageDraw.ImageDraw, anchor: dict) -> None:
    x, y, w, h = (anchor[key] for key in ("x", "y", "width", "height"))
    draw.line((x + 18, y + 12, x + 18, y + h), fill=(135, 106, 83, 255), width=5)
    draw.line((x + w - 36, y + 18, x + w - 36, y + h), fill=(135, 106, 83, 255), width=5)
    draw.polygon(
        [(x, y + 22), (x + w - 10, y), (x + w, y + 38), (x + 16, y + 52)],
        fill=(124, 68, 68, 255),
        outline=COLORS["amber"],
    )
    draw.rectangle((x + 60, y + 76, x + 162, y + 130), fill=(49, 48, 62, 255), outline=COLORS["cyan_dim"])
    draw.ellipse((x + 204, y + 88, x + 254, y + 128), fill=(55, 49, 59, 255), outline=COLORS["amber"])
    draw.line((x + w - 74, y + 42, x + w - 52, y + 98), fill=COLORS["muted"], width=2)
    for offset in (0, 13, 26):
        draw.ellipse((x + w - 70 + offset, y + 84, x + w - 64 + offset, y + 90), fill=COLORS["cyan"])


def draw_terminal(draw: ImageDraw.ImageDraw, anchor: dict) -> None:
    x, y, w, h = (anchor[key] for key in ("x", "y", "width", "height"))
    draw.rounded_rectangle((x, y, x + w, y + h), radius=12, fill=(43, 46, 62, 255), outline=COLORS["amber"], width=4)
    draw.rectangle((x + 25, y + 24, x + w - 25, y + 78), fill=(20, 31, 54, 255), outline=COLORS["magenta"], width=3)
    draw.line((x + 52, y + 92, x + 52, y + h), fill=COLORS["muted"], width=4)
    draw.line((x + w - 52, y + 92, x + w - 52, y + h), fill=COLORS["muted"], width=4)


def draw_tower(draw: ImageDraw.ImageDraw, anchor: dict) -> None:
    x, y, w, h = (anchor[key] for key in ("x", "y", "width", "height"))
    draw.polygon(
        [(x + 46, y + h), (x + 82, y + 26), (x + 146, y), (x + 178, y + h)],
        fill=(45, 48, 62, 255),
        outline=(129, 104, 119, 255),
    )
    for y_offset in range(64, h - 30, 72):
        draw.line((x + 65, y + y_offset, x + 165, y + y_offset - 18), fill=COLORS["cyan_dim"], width=4)
    draw.line((x + 82, y + 26, x + 28, y - 42), fill=(107, 80, 95, 255), width=6)
    draw.line((x + 146, y, x + 210, y - 62), fill=(107, 80, 95, 255), width=6)


def draw_portal(draw: ImageDraw.ImageDraw, anchor: dict) -> None:
    x, y, w, h = (anchor[key] for key in ("x", "y", "width", "height"))
    draw.ellipse((x, y, x + w, y + h), fill=(20, 22, 47, 255), outline=COLORS["cyan"], width=11)
    draw.ellipse((x + 38, y + 36, x + w - 38, y + h - 28), outline=COLORS["magenta"], width=7)
    draw.ellipse((x + 72, y + 72, x + w - 72, y + h - 62), fill=(43, 225, 201, 74), outline=(98, 224, 210, 255), width=4)
    for angle in range(0, 360, 45):
        radians = math.radians(angle)
        cx = x + w / 2 + math.cos(radians) * (w * 0.43)
        cy = y + h / 2 + math.sin(radians) * (h * 0.43)
        draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=COLORS["amber"])


def draw_annotations(image: Image.Image, manifest: dict) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    coordinates = manifest["coordinate_system"]
    width = coordinates["world_width"]
    height = coordinates["world_height"]
    seams = coordinates["plate_seams_x"]
    ground_y = coordinates["ground_y"]

    for x in range(0, width + 1, 128):
        draw.line((x, 0, x, height), fill=COLORS["grid"], width=1)
    for y in range(0, height + 1, 128):
        draw.line((0, y, width, y), fill=COLORS["grid"], width=1)

    for seam in seams:
        draw.line((seam, 0, seam, height), fill=COLORS["blue"], width=5)
    draw.line((0, ground_y, width, ground_y), fill=COLORS["cyan"], width=4)

    for collision in manifest["collision"]:
        if collision["id"] in {"left_world_bound", "right_world_bound"}:
            continue
        x = collision["x"]
        y = collision["y"]
        right = x + collision["width"]
        bottom = y + collision["height"]
        draw.rectangle((x, y, right, bottom), outline=COLORS["cyan"], width=3)

    for zone in manifest["interaction_zones"]:
        x = zone["x"]
        y = zone["y"]
        right = x + zone["width"]
        bottom = y + zone["height"]
        draw.rectangle((x, y, right, bottom), outline=COLORS["magenta"], width=3)

    draw.rectangle((0, 0, width, 98), fill=(5, 8, 23, 226))
    text_box(
        draw,
        (24, 20),
        "SUPER FRGMNTS // COREWORKS OVERWORLD // PHASE 1 COMPOSITION",
        outline=COLORS["cyan"],
        size=24,
        bold=True,
    )
    text_box(
        draw,
        (24, 65),
        "5016 × 941 // THREE 1672 PX PLATES // GROUND Y 744 // UNTIL PORTAL: NO TIMER",
        outline=COLORS["blue"],
        fill=COLORS["muted"],
        size=15,
    )

    for seam in seams:
        text_box(
            draw,
            (seam - 120, 112),
            f"PLATE SEAM // X {seam}",
            outline=COLORS["blue"],
            size=15,
        )
    plate_colors = (COLORS["cyan"], COLORS["amber"], COLORS["orange"])
    for index, plate in enumerate(manifest["plates"]):
        text_box(
            draw,
            (plate["x"] + 26, 112),
            f"PLATE {index + 1} // {plate['name'].upper()}",
            outline=plate_colors[index],
            size=18,
            bold=True,
        )

    labels = {
        "aryn_ship": (170, 350),
        "aryn_spawn": (946, 566),
        "dras_ehdre": (1840, 510),
        "dras_camp": (2060, 548),
        "credit_terminal": (2870, 520),
        "atmosphere_tower": (3650, 288),
        "coreworks_portal": (4538, 362),
        "vesper_volcano": (3970, 134),
    }
    for anchor in manifest["anchors"]:
        label_position = labels[anchor["id"]]
        label_color = COLORS["orange"] if anchor["id"] == "vesper_volcano" else COLORS["cyan"]
        text_box(
            draw,
            label_position,
            f"{anchor['label'].upper()} // X {anchor['x']}",
            outline=label_color,
            fill=COLORS["ink"],
            size=14,
        )

    text_box(
        draw,
        (1350, ground_y - 44),
        "SAFE JUMP LESSON",
        outline=COLORS["amber"],
        size=13,
    )
    text_box(
        draw,
        (1824, ground_y - 202),
        "DRAS DIALOGUE ZONE",
        outline=COLORS["magenta"],
        size=13,
    )
    text_box(
        draw,
        (4590, ground_y - 238),
        "PORTAL STARTS 08:00",
        outline=COLORS["magenta"],
        size=13,
    )


def build_guide(manifest: dict) -> Image.Image:
    coordinates = manifest["coordinate_system"]
    width = coordinates["world_width"]
    height = coordinates["world_height"]
    image = vertical_gradient(
        (width, height),
        [
            (0.0, (7, 11, 34)),
            (0.48, (23, 26, 59)),
            (0.72, (107, 56, 91)),
            (1.0, (182, 106, 90)),
        ],
    )
    draw = ImageDraw.Draw(image, "RGBA")
    draw_background(draw, width, height)
    draw_ground(draw, manifest)
    draw_ship(draw, anchor_by_id(manifest, "aryn_ship"))
    draw_dras(draw, anchor_by_id(manifest, "dras_ehdre"))
    draw_camp(draw, anchor_by_id(manifest, "dras_camp"))
    draw_terminal(draw, anchor_by_id(manifest, "credit_terminal"))
    draw_tower(draw, anchor_by_id(manifest, "atmosphere_tower"))
    draw_portal(draw, anchor_by_id(manifest, "coreworks_portal"))

    spawn = anchor_by_id(manifest, "aryn_spawn")
    draw.rectangle(
        (
            spawn["x"],
            spawn["y"],
            spawn["x"] + spawn["width"],
            spawn["y"] + spawn["height"],
        ),
        fill=(119, 163, 255, 90),
        outline=COLORS["blue"],
        width=3,
    )
    draw_annotations(image, manifest)
    return image


def build_contact_sheet(guide: Image.Image, manifest: dict) -> Image.Image:
    coordinates = manifest["coordinate_system"]
    plate_width = coordinates["plate_width"]
    plate_height = coordinates["plate_height"]
    scale = 0.31
    preview_width = round(plate_width * scale)
    preview_height = round(plate_height * scale)
    margin = 32
    label_height = 52
    plate_count = len(manifest["plates"])
    sheet = Image.new(
        "RGBA",
        (
            preview_width * plate_count + margin * (plate_count + 1),
            preview_height + margin * 2 + label_height,
        ),
        (5, 8, 23, 255),
    )
    sheet_draw = ImageDraw.Draw(sheet, "RGBA")

    for index, plate in enumerate(manifest["plates"]):
        crop = guide.crop((plate["x"], 0, plate["x"] + plate_width, plate_height))
        crop = crop.resize((preview_width, preview_height), Image.Resampling.LANCZOS)
        left = margin + index * (preview_width + margin)
        top = margin + label_height
        sheet.alpha_composite(crop, (left, top))
        sheet_draw.rectangle(
            (left, top, left + preview_width, top + preview_height),
            outline=COLORS["cyan"] if index == 0 else COLORS["amber"],
            width=3,
        )
        sheet_draw.text(
            (left, margin),
            f"PLATE {index + 1} // {plate['name'].upper()}",
            font=font(22, bold=True),
            fill=COLORS["ink"],
        )

    return sheet


def main() -> None:
    manifest = load_manifest()
    validate(manifest)
    guide = build_guide(manifest)
    guide.save(GUIDE_PATH, optimize=True)
    contact_sheet = build_contact_sheet(guide, manifest)
    contact_sheet.save(CONTACT_SHEET_PATH, optimize=True)
    print(f"Built {GUIDE_PATH.relative_to(ROOT)}")
    print(f"Built {CONTACT_SHEET_PATH.relative_to(ROOT)}")
    print("Validated 5016×941 world, three plates, seams, ground, anchors, and zones.")


if __name__ == "__main__":
    main()
