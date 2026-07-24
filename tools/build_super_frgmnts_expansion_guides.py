#!/usr/bin/env python3
"""Build deterministic vertical-outpaint and collision-guide PNGs for Super Frgmnts."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "Design" / "Super-Frgmnts" / "Expansion-Guides"

PLATE_WIDTH = 1672
PLATE_HEIGHT = 941
COMPOSITE_HEIGHT = PLATE_HEIGHT * 2
BLEND_HEIGHT = 180
BLEND_END = PLATE_HEIGHT + BLEND_HEIGHT

GAME_WIDTH = 1600
GAME_HEIGHT = 900
SOURCE_X_SCALE = PLATE_WIDTH / GAME_WIDTH
SOURCE_Y_SCALE = PLATE_HEIGHT / GAME_HEIGHT

DECK_Y = PLATE_HEIGHT + round(663 * SOURCE_Y_SCALE)
DEEPWORKS_Y = PLATE_HEIGHT + round(875 * SOURCE_Y_SCALE)
DROP_LEFT = round(300 * SOURCE_X_SCALE)
DROP_RIGHT = round(1082 * SOURCE_X_SCALE)

FONT_PATH = "/System/Library/Fonts/SFNSMono.ttf"
FONT_BOLD_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

COLORS = {
    "void": (5, 7, 19),
    "panel": (7, 10, 23, 224),
    "ink": (247, 240, 234, 255),
    "muted": (186, 198, 215, 255),
    "cyan": (88, 245, 223, 255),
    "blue": (119, 163, 255, 255),
    "gold": (255, 211, 108, 255),
    "pink": (255, 105, 180, 255),
    "amethyst": (155, 89, 182, 255),
    "rose": (224, 191, 184, 255),
    "red": (255, 72, 96, 255),
}

PLATES = {
    "foundry": {
        "title": "FOUNDRY",
        "source": ROOT / "Images" / "Builder" / "signal-foundry-bg.png",
        "current": [
            (318, 567, 204, "current"),
            (632, 443, 188, "current"),
            (954, 566, 218, "current"),
            (1239, 447, 186, "current"),
        ],
        "proposed": [
            (240, 1300, 280, "standard"),
            (565, 1160, 250, "standard"),
            (865, 1020, 270, "standard"),
            (1115, 880, 270, "standard"),
            (0, 740, 270, "edge"),
            (735, 740, 260, "standard"),
            (1402, 740, 270, "edge"),
            (1160, 600, 260, "standard"),
            (880, 460, 255, "standard"),
            (590, 320, 270, "standard"),
            (300, 180, 280, "standard"),
            (1240, 260, 245, "boost"),
        ],
        "moving": [
            (480, 870, 270, 80),
        ],
    },
    "refinery": {
        "title": "REFINERY",
        "source": ROOT / "Images" / "Game" / "signal-foundry-refinery.png",
        "current": [
            (278, 554, 205, "current"),
            (612, 432, 185, "current"),
            (954, 548, 218, "moving-current"),
            (1282, 422, 180, "current"),
        ],
        "proposed": [
            (1190, 1300, 295, "standard"),
            (880, 1160, 255, "standard"),
            (575, 1020, 265, "standard"),
            (270, 880, 270, "standard"),
            (0, 740, 285, "edge"),
            (690, 740, 275, "standard"),
            (1387, 740, 285, "edge"),
            (1030, 600, 285, "standard"),
            (730, 460, 260, "standard"),
            (405, 320, 255, "standard"),
            (90, 180, 270, "standard"),
            (1280, 280, 250, "boost"),
        ],
        "moving": [
            (520, 1080, 300, 90),
            (1000, 820, 310, 95),
        ],
    },
    "biolab": {
        "title": "BIOLAB",
        "source": ROOT / "Images" / "Game" / "signal-foundry-biolab.png",
        "current": [
            (198, 542, 214, "current"),
            (514, 414, 188, "current"),
            (854, 532, 218, "moving-current"),
            (1172, 402, 188, "current"),
            (1452, 540, 170, "current"),
        ],
        "proposed": [
            (165, 1300, 280, "standard"),
            (1170, 1300, 280, "standard"),
            (455, 1160, 260, "standard"),
            (925, 1160, 260, "standard"),
            (165, 1020, 270, "standard"),
            (1230, 1020, 270, "standard"),
            (460, 880, 270, "standard"),
            (940, 880, 270, "standard"),
            (0, 740, 275, "edge"),
            (700, 740, 275, "standard"),
            (1397, 740, 275, "edge"),
            (155, 600, 290, "standard"),
            (1225, 600, 290, "standard"),
            (450, 460, 270, "standard"),
            (950, 460, 270, "standard"),
            (710, 320, 260, "standard"),
            (235, 180, 285, "boost"),
            (1150, 180, 285, "boost"),
        ],
        "moving": [
            (720, 1020, 230, 105),
        ],
    },
    "uplink": {
        "title": "UPLINK",
        "source": ROOT / "Images" / "Game" / "signal-foundry-uplink.png",
        "current": [
            (204, 550, 205, "current"),
            (532, 426, 188, "current"),
            (862, 548, 218, "moving-current"),
            (1184, 416, 188, "current"),
            (1438, 532, 148, "current"),
        ],
        "proposed": [
            (500, 1300, 265, "standard"),
            (1030, 1300, 260, "standard"),
            (750, 1160, 270, "standard"),
            (1015, 1020, 270, "standard"),
            (710, 880, 275, "standard"),
            (0, 740, 280, "edge"),
            (410, 740, 270, "standard"),
            (990, 740, 270, "standard"),
            (1392, 740, 280, "edge"),
            (700, 600, 275, "standard"),
            (960, 460, 275, "standard"),
            (700, 320, 275, "standard"),
            (685, 180, 310, "standard"),
            (1260, 240, 245, "boost"),
        ],
        "moving": [
            (410, 980, 285, 90),
        ],
    },
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD_PATH if bold else FONT_PATH
    return ImageFont.truetype(path, size)


def text_box(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    *,
    fill: tuple[int, int, int, int] = COLORS["ink"],
    background: tuple[int, int, int, int] = COLORS["panel"],
    outline: tuple[int, int, int, int] = COLORS["blue"],
    size: int = 22,
    bold: bool = False,
    padding: int = 10,
) -> None:
    label_font = font(size, bold)
    bounds = draw.textbbox(xy, text, font=label_font)
    rect = (
        bounds[0] - padding,
        bounds[1] - padding,
        bounds[2] + padding,
        bounds[3] + padding,
    )
    draw.rounded_rectangle(rect, radius=4, fill=background, outline=outline, width=2)
    draw.text(xy, text, font=label_font, fill=fill)


def dashed_line(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    *,
    fill: tuple[int, int, int, int],
    width: int = 3,
    dash: int = 16,
    gap: int = 10,
) -> None:
    x1, y1 = start
    x2, y2 = end
    if y1 == y2:
        cursor = x1
        while cursor < x2:
            draw.line((cursor, y1, min(cursor + dash, x2), y2), fill=fill, width=width)
            cursor += dash + gap
    elif x1 == x2:
        cursor = y1
        while cursor < y2:
            draw.line((x1, cursor, x2, min(cursor + dash, y2)), fill=fill, width=width)
            cursor += dash + gap
    else:
        raise ValueError("Only horizontal or vertical dashed lines are supported")


def game_platform_to_source(platform: tuple[int, int, int, str]) -> tuple[int, int, int, str]:
    x, y, width, kind = platform
    return (
        round(x * SOURCE_X_SCALE),
        PLATE_HEIGHT + round(y * SOURCE_Y_SCALE),
        round(width * SOURCE_X_SCALE),
        kind,
    )


def draw_grid(draw: ImageDraw.ImageDraw) -> None:
    for x in range(0, PLATE_WIDTH + 1, 32):
        alpha = 40 if x % 128 else 100
        draw.line((x, 0, x, COMPOSITE_HEIGHT), fill=(119, 163, 255, alpha), width=1)
    for y in range(0, COMPOSITE_HEIGHT + 1, 32):
        alpha = 40 if y % 128 else 100
        draw.line((0, y, PLATE_WIDTH, y), fill=(119, 163, 255, alpha), width=1)


def draw_platform(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    kind: str,
) -> None:
    palette = {
        "current": COLORS["cyan"],
        "moving-current": COLORS["gold"],
        "standard": COLORS["cyan"],
        "edge": COLORS["blue"],
        "boost": COLORS["pink"],
    }
    color = palette[kind]
    fill = (*color[:3], 72)
    height = 24
    draw.rectangle((x, y, x + width, y + height), fill=fill, outline=color, width=2)
    draw.line((x, y, x + width, y), fill=color, width=6)
    if kind == "boost":
        for marker_x in range(x + 16, x + width - 8, 28):
            draw.polygon(
                (
                    (marker_x, y + 17),
                    (marker_x + 7, y + 7),
                    (marker_x + 14, y + 17),
                ),
                fill=color,
            )


def build_expansion_canvas(source: Image.Image) -> Image.Image:
    canvas = Image.new("RGBA", (PLATE_WIDTH, COMPOSITE_HEIGHT), (0, 0, 0, 0))
    canvas.paste(source.convert("RGBA"), (0, PLATE_HEIGHT))
    return canvas


def build_outpaint_mask() -> Image.Image:
    mask = Image.new("L", (PLATE_WIDTH, COMPOSITE_HEIGHT), 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle((0, 0, PLATE_WIDTH, BLEND_END - 1), fill=255)
    return mask


def build_collision_guide(key: str, config: dict, source: Image.Image) -> Image.Image:
    guide = Image.new("RGBA", (PLATE_WIDTH, COMPOSITE_HEIGHT), (*COLORS["void"], 255))

    dimmed_source = ImageEnhance.Brightness(source.convert("RGB")).enhance(0.48).convert("RGBA")
    guide.paste(dimmed_source, (0, PLATE_HEIGHT))

    overlay = Image.new("RGBA", guide.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    draw.rectangle((0, 0, PLATE_WIDTH, PLATE_HEIGHT - 1), fill=(27, 54, 93, 128))
    draw.rectangle(
        (0, PLATE_HEIGHT, PLATE_WIDTH, BLEND_END - 1),
        fill=(255, 211, 108, 64),
        outline=COLORS["gold"],
        width=3,
    )
    draw.rectangle(
        (0, BLEND_END, PLATE_WIDTH - 1, COMPOSITE_HEIGHT - 1),
        outline=(88, 245, 223, 148),
        width=3,
    )
    draw_grid(draw)

    major_bands = [
        (1020, "LOWER GANTRY BAND"),
        (600, "MID GANTRY BAND"),
        (260, "UPPER GANTRY BAND"),
    ]
    for y, label in major_bands:
        dashed_line(draw, (0, y), (PLATE_WIDTH, y), fill=COLORS["amethyst"], width=3)
        text_box(
            draw,
            (22, y - 38),
            f"Y {y} // {label}",
            fill=COLORS["rose"],
            outline=COLORS["amethyst"],
            size=16,
            padding=7,
        )

    draw.rectangle(
        (DROP_LEFT, DECK_Y, DROP_RIGHT, DEEPWORKS_Y),
        fill=(88, 245, 223, 34),
        outline=COLORS["cyan"],
        width=3,
    )
    dashed_line(draw, (0, DECK_Y), (PLATE_WIDTH, DECK_Y), fill=COLORS["gold"], width=4)
    dashed_line(draw, (0, DEEPWORKS_Y), (PLATE_WIDTH, DEEPWORKS_Y), fill=COLORS["blue"], width=4)

    for platform in config["current"]:
        draw_platform(draw, *game_platform_to_source(platform))
    for platform in config["proposed"]:
        draw_platform(draw, *platform)

    for x, y, width, travel in config["moving"]:
        draw.rectangle(
            (x, y - travel, x + width, y + travel + 24),
            fill=(255, 211, 108, 20),
            outline=COLORS["gold"],
            width=2,
        )
        dashed_line(draw, (x + width // 2, y - travel), (x + width // 2, y + travel), fill=COLORS["gold"])
        draw_platform(draw, x, y, width, "moving-current")

    text_box(
        draw,
        (24, 28),
        f"SUPER FRGMNTS // {config['title']} EXPANSION GUIDE",
        outline=COLORS["cyan"],
        size=25,
        bold=True,
        padding=12,
    )
    text_box(
        draw,
        (24, 86),
        "TRANSPARENT/GENERATE AREA // NEW UPPER PLATE",
        fill=COLORS["blue"],
        outline=COLORS["blue"],
        size=16,
        padding=8,
    )
    text_box(
        draw,
        (PLATE_WIDTH - 460, PLATE_HEIGHT + 24),
        "180 PX BLEND / INPAINT ZONE",
        fill=COLORS["gold"],
        outline=COLORS["gold"],
        size=16,
        padding=8,
    )
    text_box(
        draw,
        (PLATE_WIDTH - 375, BLEND_END + 26),
        "LOCK ORIGINAL PIXELS",
        fill=COLORS["cyan"],
        outline=COLORS["cyan"],
        size=16,
        padding=8,
    )
    text_box(
        draw,
        (24, DECK_Y - 56),
        f"MAIN CONCRETE DECK // Y {DECK_Y}",
        fill=COLORS["gold"],
        outline=COLORS["gold"],
        size=16,
        padding=8,
    )
    text_box(
        draw,
        (DROP_LEFT + 24, DEEPWORKS_Y - 58),
        f"DEEPWORKS DROP CORRIDOR // X {DROP_LEFT}-{DROP_RIGHT}",
        fill=COLORS["cyan"],
        outline=COLORS["cyan"],
        size=15,
        padding=7,
    )

    legend_y = 108
    legend_x = PLATE_WIDTH - 410
    draw.rounded_rectangle(
        (legend_x, legend_y, PLATE_WIDTH - 20, legend_y + 192),
        radius=6,
        fill=COLORS["panel"],
        outline=COLORS["rose"],
        width=2,
    )
    draw.text((legend_x + 18, legend_y + 14), "COLLISION LEGEND", font=font(18, True), fill=COLORS["ink"])
    legend_items = [
        ("CURRENT PLATFORM", COLORS["cyan"]),
        ("PROPOSED / STANDARD", COLORS["cyan"]),
        ("SHARED EDGE LINK", COLORS["blue"]),
        ("BOOST-ONLY OPTIONAL", COLORS["pink"]),
        ("MOVING PLATFORM PATH", COLORS["gold"]),
    ]
    for index, (label, color) in enumerate(legend_items):
        item_y = legend_y + 48 + index * 27
        draw.line((legend_x + 18, item_y + 7, legend_x + 72, item_y + 7), fill=color, width=6)
        draw.text((legend_x + 84, item_y - 4), label, font=font(14), fill=COLORS["muted"])

    guide = Image.alpha_composite(guide, overlay)
    return guide.convert("RGB")


def build_contact_sheet(guides: list[tuple[str, Image.Image]]) -> Image.Image:
    thumb_width = 418
    thumb_height = round(COMPOSITE_HEIGHT * thumb_width / PLATE_WIDTH)
    gutter = 24
    label_height = 44
    sheet_width = gutter * 3 + thumb_width * 2
    sheet_height = gutter * 3 + (thumb_height + label_height) * 2
    sheet = Image.new("RGB", (sheet_width, sheet_height), COLORS["void"])
    draw = ImageDraw.Draw(sheet)

    for index, (name, guide) in enumerate(guides):
        column = index % 2
        row = index // 2
        x = gutter + column * (thumb_width + gutter)
        y = gutter + row * (thumb_height + label_height + gutter)
        thumb = guide.resize((thumb_width, thumb_height), Image.Resampling.NEAREST)
        sheet.paste(thumb, (x, y))
        draw.text((x, y + thumb_height + 10), name.upper(), font=font(18, True), fill=COLORS["ink"])

    return sheet


def validate_expansion_canvas(canvas: Image.Image, source: Image.Image) -> None:
    if canvas.size != (PLATE_WIDTH, COMPOSITE_HEIGHT):
        raise ValueError(f"Unexpected expansion canvas dimensions: {canvas.size}")
    upper_alpha = canvas.getchannel("A").crop((0, 0, PLATE_WIDTH, PLATE_HEIGHT))
    if upper_alpha.getbbox() is not None:
        raise ValueError("Upper outpaint region must be completely transparent")
    lower = canvas.crop((0, PLATE_HEIGHT, PLATE_WIDTH, COMPOSITE_HEIGHT))
    if lower.tobytes() != source.convert("RGBA").tobytes():
        raise ValueError("Source plate pixels changed in the protected lower half")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rendered_guides: list[tuple[str, Image.Image]] = []

    for key, config in PLATES.items():
        source = Image.open(config["source"])
        if source.size != (PLATE_WIDTH, PLATE_HEIGHT):
            raise ValueError(f"{config['source']} has unexpected dimensions {source.size}")

        canvas = build_expansion_canvas(source)
        validate_expansion_canvas(canvas, source)
        canvas.save(OUTPUT_DIR / f"{key}-vertical-expansion-canvas.png", optimize=True)

        mask = build_outpaint_mask()
        mask.save(OUTPUT_DIR / f"{key}-outpaint-mask-white-edit.png", optimize=True)

        guide = build_collision_guide(key, config, source)
        guide.save(OUTPUT_DIR / f"{key}-collision-guide.png", optimize=True)
        rendered_guides.append((key, guide))

    contact_sheet = build_contact_sheet(rendered_guides)
    contact_sheet.save(OUTPUT_DIR / "super-frgmnts-expansion-guides-contact-sheet.png", optimize=True)

    print(f"Generated {len(PLATES) * 3 + 1} PNG files in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
