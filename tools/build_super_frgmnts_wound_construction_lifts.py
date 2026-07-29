#!/usr/bin/env python3
"""Build the exact modular construction-lift kit for The Wound."""

from pathlib import Path
import random

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Boss-Room"
    / "Construction-Lifts"
)
RAW = PACKAGE / "Raw"
REVIEWS = PACKAGE / "Reviews"
RUNTIME = ROOT / "Images" / "Game" / "Super-Frgmnts"

PLATFORM_SOURCE = (
    RAW / "wound-construction-platform-clean-source-v1.png"
)
ROOM_BACKGROUND = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Boss-Room"
    / "Raw"
    / "wound-boss-room-background-master-v3.png"
)

TOWER_PATH = RUNTIME / "wound-construction-lift-tower-runtime-v1.png"
PLATFORM_PATH = (
    RUNTIME / "wound-construction-lift-platform-runtime-v1.png"
)
CABLE_PATH = RUNTIME / "wound-construction-lift-cable-tile-v1.png"
RUNWAY_PATH = (
    RUNTIME / "wound-construction-gantry-runway-runtime-v2.png"
)
GANTRY_CAR_PATH = (
    RUNTIME / "wound-construction-gantry-car-runtime-v1.png"
)
KIT_REVIEW_PATH = (
    REVIEWS / "wound-construction-lift-kit-review-v2.png"
)
ROOM_REVIEW_PATH = (
    REVIEWS / "wound-construction-lifts-room-review-v2.png"
)

TOWER_SIZE = (320, 592)
PLATFORM_SIZE = (320, 72)
CABLE_SIZE = (8, 64)
RUNWAY_SIZE = (1420, 64)
GANTRY_CAR_SIZE = (300, 152)
PLATFORM_SURFACE_Y = 12
GANTRY_SURFACE_Y = 86

PALETTE = {
    "outline": "#050811",
    "deep": "#070b14",
    "shell": "#111827",
    "body": "#202a3b",
    "panel": "#303b50",
    "rim": "#59657a",
    "edge": "#7b8494",
    "highlight": "#b5bdc9",
    "amber": "#ffd36c",
    "amber_dark": "#8a713c",
    "rust": "#70412d",
}


def rect(
    draw: ImageDraw.ImageDraw,
    bounds: tuple[int, int, int, int],
    fill: str,
    outline: str | None = None,
    width: int = 1,
) -> None:
    draw.rectangle(bounds, fill=fill, outline=outline, width=width)


def pixel_line(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[int, int]],
    fill: str,
    width: int,
) -> None:
    draw.line(points, fill=fill, width=width)


def normalize_platform(
    source: Image.Image,
    target_size: tuple[int, int],
) -> Image.Image:
    """Remove repeated center bays without stretching the source art."""
    alpha_bounds = source.getbbox()
    if not alpha_bounds:
        raise ValueError("Platform source has no visible pixels")

    subject = source.crop(alpha_bounds)
    target_width, target_height = target_size
    desired_ratio = target_width / target_height
    composite_width = round(subject.height * desired_ratio)
    center_width = min(
        round(subject.width * 0.15),
        composite_width // 3,
    )
    side_width = (composite_width - center_width) // 2
    composite_width = side_width * 2 + center_width
    if composite_width >= subject.width:
        raise ValueError("Platform source is not wide enough to recompose")

    center_x = subject.width // 2
    center_left = center_x - center_width // 2
    pieces = [
        subject.crop((0, 0, side_width, subject.height)),
        subject.crop(
            (
                center_left,
                0,
                center_left + center_width,
                subject.height,
            )
        ),
        subject.crop(
            (
                subject.width - side_width,
                0,
                subject.width,
                subject.height,
            )
        ),
    ]
    recomposed = Image.new(
        "RGBA",
        (composite_width, subject.height),
        (0, 0, 0, 0),
    )
    cursor = 0
    for piece in pieces:
        recomposed.alpha_composite(piece, (cursor, 0))
        cursor += piece.width

    # A half-resolution color pass gives the generator artwork the same
    # deliberate pixel density as the room without blurring it at runtime.
    half_size = (
        max(1, target_width // 2),
        max(1, target_height // 2),
    )
    reduced = recomposed.resize(
        half_size,
        Image.Resampling.LANCZOS,
    )
    alpha = reduced.getchannel("A")
    colored = (
        reduced.convert("RGB")
        .quantize(colors=48, dither=Image.Dither.NONE)
        .convert("RGBA")
    )
    colored.putalpha(alpha)
    return colored.resize(target_size, Image.Resampling.NEAREST)


def add_steel_texture(
    image: Image.Image,
    seed: int,
    regions: list[tuple[int, int, int, int]],
    count: int,
) -> None:
    draw = ImageDraw.Draw(image)
    rng = random.Random(seed)
    for _ in range(count):
        region = rng.choice(regions)
        x = rng.randint(region[0], max(region[0], region[2] - 3))
        y = rng.randint(region[1], max(region[1], region[3] - 2))
        length = rng.randint(2, 7)
        color = (
            PALETTE["rust"]
            if rng.random() < 0.3
            else PALETTE["edge"]
        )
        draw.line(
            [(x, y), (min(region[2], x + length), y)],
            fill=color,
            width=1,
        )


def build_tower() -> Image.Image:
    tower = Image.new("RGBA", TOWER_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(tower)

    # Top machinery bridge and motor.
    rect(draw, (36, 46, 284, 74), PALETTE["outline"])
    rect(draw, (42, 42, 278, 68), PALETTE["body"])
    rect(draw, (48, 46, 272, 54), PALETTE["rim"])
    rect(draw, (94, 8, 226, 51), PALETTE["outline"])
    rect(draw, (100, 12, 220, 47), PALETTE["panel"])
    rect(draw, (112, 17, 208, 43), PALETTE["shell"])
    rect(draw, (126, 14, 194, 46), PALETTE["body"])
    for x in (118, 134, 186, 202):
        rect(draw, (x, 12, x + 6, 48), PALETTE["rim"])
    rect(draw, (143, 18, 177, 42), PALETTE["deep"])
    rect(draw, (150, 18, 170, 42), PALETTE["panel"])
    rect(draw, (153, 20, 157, 40), PALETTE["edge"])

    # Amber maintenance beacon.
    rect(draw, (252, 13, 278, 43), PALETTE["outline"])
    rect(draw, (256, 17, 274, 39), PALETTE["amber_dark"])
    rect(draw, (259, 20, 271, 35), PALETTE["amber"])
    rect(draw, (261, 21, 264, 33), "#fff2b0")

    # Load-bearing guide columns. Their centers align to x=30 and x=290.
    for left in (16, 276):
        rect(draw, (left, 60, left + 28, 566), PALETTE["outline"])
        rect(draw, (left + 4, 62, left + 24, 562), PALETTE["body"])
        rect(draw, (left + 7, 64, left + 11, 560), PALETTE["rim"])
        rect(draw, (left + 16, 64, left + 20, 560), PALETTE["deep"])
        rect(draw, (left + 21, 66, left + 23, 558), PALETTE["edge"])

    # Inner tower frame and repeatable structural bays.
    for left in (48, 260):
        rect(draw, (left, 66, left + 12, 552), PALETTE["outline"])
        rect(draw, (left + 3, 68, left + 9, 550), PALETTE["panel"])
        rect(draw, (left + 5, 70, left + 7, 548), PALETTE["rim"])

    bay_top = 78
    bay_height = 88
    while bay_top < 518:
        bay_bottom = min(548, bay_top + bay_height)
        pixel_line(
            draw,
            [(58, bay_top + 6), (262, bay_bottom - 6)],
            PALETTE["outline"],
            14,
        )
        pixel_line(
            draw,
            [(262, bay_top + 6), (58, bay_bottom - 6)],
            PALETTE["outline"],
            14,
        )
        pixel_line(
            draw,
            [(58, bay_top + 6), (262, bay_bottom - 6)],
            PALETTE["body"],
            8,
        )
        pixel_line(
            draw,
            [(262, bay_top + 6), (58, bay_bottom - 6)],
            PALETTE["body"],
            8,
        )
        rect(
            draw,
            (48, bay_bottom - 5, 272, bay_bottom + 5),
            PALETTE["outline"],
        )
        rect(
            draw,
            (54, bay_bottom - 2, 266, bay_bottom + 2),
            PALETTE["rim"],
        )
        bay_top += bay_height

    # Brake teeth and limit switches establish a mechanical travel path.
    for y in range(92, 528, 44):
        for x in (22, 286):
            rect(draw, (x, y, x + 16, y + 10), PALETTE["deep"])
            rect(draw, (x + 3, y + 2, x + 13, y + 6), PALETTE["edge"])
            rect(draw, (x + 6, y + 3, x + 9, y + 6), PALETTE["amber_dark"])

    # Junction box and conduit.
    rect(draw, (226, 326, 256, 366), PALETTE["outline"])
    rect(draw, (230, 330, 252, 362), PALETTE["panel"])
    rect(draw, (236, 336, 246, 343), PALETTE["amber_dark"])
    pixel_line(
        draw,
        [(252, 347), (267, 347), (267, 210)],
        PALETTE["outline"],
        5,
    )
    pixel_line(
        draw,
        [(253, 347), (265, 347), (265, 210)],
        PALETTE["rim"],
        2,
    )

    # Bottom shock absorbers and feet.
    rect(draw, (4, 552, 54, 584), PALETTE["outline"])
    rect(draw, (266, 552, 316, 584), PALETTE["outline"])
    for center_x in (30, 290):
        rect(
            draw,
            (center_x - 9, 536, center_x + 9, 575),
            PALETTE["deep"],
        )
        for y in range(540, 568, 6):
            pixel_line(
                draw,
                [(center_x - 8, y), (center_x + 8, y + 5)],
                PALETTE["edge"],
                3,
            )
        rect(
            draw,
            (center_x - 14, 571, center_x + 14, 588),
            PALETTE["panel"],
            PALETTE["outline"],
            3,
        )
    rect(draw, (0, 584, 320, 591), PALETTE["outline"])
    rect(draw, (8, 580, 312, 586), PALETTE["body"])
    rect(draw, (14, 581, 306, 583), PALETTE["rim"])

    add_steel_texture(
        tower,
        seed=1701,
        regions=[
            (16, 70, 44, 540),
            (276, 70, 304, 540),
            (62, 80, 258, 540),
        ],
        count=62,
    )
    return tower


def build_cable() -> Image.Image:
    cable = Image.new("RGBA", CABLE_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(cable)
    rect(draw, (1, 0, 6, 63), PALETTE["outline"])
    rect(draw, (2, 0, 5, 63), "#2b303a")
    rect(draw, (3, 0, 3, 63), PALETTE["edge"])
    for y in range(-4, 68, 8):
        pixel_line(draw, [(1, y), (6, y + 5)], "#10141d", 2)
        pixel_line(draw, [(2, y + 1), (5, y + 4)], "#8a713c", 1)
    return cable


def build_runway() -> Image.Image:
    runway = Image.new("RGBA", RUNWAY_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(runway)
    width, height = RUNWAY_SIZE
    rect(draw, (0, 8, width - 1, 58), PALETTE["outline"])
    rect(draw, (8, 12, width - 9, 54), PALETTE["body"])
    rect(draw, (8, 12, width - 9, 20), PALETTE["rim"])
    rect(draw, (8, 23, width - 9, 29), PALETTE["panel"])
    rect(draw, (8, 51, width - 9, 58), PALETTE["deep"])
    rect(draw, (12, 55, width - 13, 62), PALETTE["edge"])
    rect(draw, (18, 57, width - 19, 61), PALETTE["outline"])

    for x in range(24, width - 90, 96):
        pixel_line(
            draw,
            [(x, 48), (x + 46, 28), (x + 92, 48)],
            PALETTE["outline"],
            10,
        )
        pixel_line(
            draw,
            [(x, 48), (x + 46, 28), (x + 92, 48)],
            PALETTE["panel"],
            5,
        )
        rect(draw, (x + 43, 24, x + 49, 52), PALETTE["rim"])

    for x in range(54, width - 40, 118):
        rect(draw, (x, 35, x + 18, 41), PALETTE["amber_dark"])
        rect(draw, (x + 3, 36, x + 15, 39), PALETTE["amber"])

    for x in (0, width - 28):
        rect(draw, (x, 2, x + 27, 63), PALETTE["outline"])
        rect(draw, (x + 5, 8, x + 22, 56), PALETTE["panel"])
        for y in (15, 44):
            draw.ellipse(
                (x + 9, y, x + 17, y + 8),
                fill=PALETTE["edge"],
                outline=PALETTE["deep"],
            )

    add_steel_texture(
        runway,
        seed=1714,
        regions=[(20, 12, width - 20, 54)],
        count=74,
    )
    return runway


def build_gantry_car(platform_source: Image.Image) -> Image.Image:
    car = Image.new("RGBA", GANTRY_CAR_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(car)

    # Trolley wheels and load carriage.
    for center_x in (112, 188):
        draw.ellipse(
            (center_x - 18, 0, center_x + 18, 34),
            fill=PALETTE["outline"],
        )
        draw.ellipse(
            (center_x - 12, 5, center_x + 12, 29),
            fill=PALETTE["rim"],
        )
        draw.ellipse(
            (center_x - 6, 11, center_x + 6, 23),
            fill=PALETTE["deep"],
        )
    rect(draw, (94, 20, 206, 49), PALETTE["outline"])
    rect(draw, (100, 23, 200, 45), PALETTE["panel"])
    rect(draw, (137, 20, 163, 49), PALETTE["body"])
    rect(draw, (144, 24, 156, 45), PALETTE["edge"])
    rect(draw, (120, 36, 180, 54), PALETTE["outline"])
    rect(draw, (126, 39, 174, 51), PALETTE["body"])

    # Rigid suspension rods land on the approved x=54 and x=246 anchors.
    for anchor_x in (54, 246):
        rect(draw, (anchor_x - 5, 40, anchor_x + 5, 88), PALETTE["outline"])
        rect(draw, (anchor_x - 2, 42, anchor_x + 2, 86), PALETTE["edge"])
        rect(draw, (anchor_x - 10, 78, anchor_x + 10, 92), PALETTE["panel"])
        rect(draw, (anchor_x - 6, 81, anchor_x + 6, 88), PALETTE["amber_dark"])

    deck = normalize_platform(platform_source, (300, 72))
    car.alpha_composite(deck, (0, GANTRY_SURFACE_Y - PLATFORM_SURFACE_Y))
    return car


def tile_cable(
    canvas: Image.Image,
    tile: Image.Image,
    center_x: int,
    start_y: int,
    end_y: int,
) -> None:
    if end_y <= start_y:
        return
    y = start_y
    while y < end_y:
        remaining = end_y - y
        height = min(tile.height, remaining)
        segment = tile.crop((0, 0, tile.width, height))
        canvas.alpha_composite(
            segment,
            (center_x - tile.width // 2, y),
        )
        y += height


def build_kit_review(
    tower: Image.Image,
    platform: Image.Image,
    cable: Image.Image,
    runway: Image.Image,
    gantry_car: Image.Image,
) -> Image.Image:
    review = Image.new("RGBA", (1600, 760), "#050713")
    review.alpha_composite(tower, (55, 78))
    review.alpha_composite(platform, (415, 104))
    review.alpha_composite(runway, (100, 270))
    review.alpha_composite(gantry_car, (690, 362))
    tile_cable(review, cable, 575, 390, 650)
    return review


def build_room_review(
    tower: Image.Image,
    platform: Image.Image,
    cable: Image.Image,
    runway: Image.Image,
    gantry_car: Image.Image,
) -> Image.Image:
    with Image.open(ROOM_BACKGROUND) as source:
        review = source.convert("RGBA")

    tower_y = 768
    for x in (250, 1990):
        review.alpha_composite(tower, (x, tower_y))
        tile_cable(review, cable, x + 160, tower_y + 46, 1090)
        review.alpha_composite(
            platform,
            (x, 1090 - PLATFORM_SURFACE_Y),
        )

    review.alpha_composite(runway, (570, 690))
    review.alpha_composite(
        gantry_car,
        (1140, 780 - GANTRY_SURFACE_Y),
    )
    return review


def main() -> None:
    if not PLATFORM_SOURCE.exists():
        raise FileNotFoundError(PLATFORM_SOURCE)
    if not ROOM_BACKGROUND.exists():
        raise FileNotFoundError(ROOM_BACKGROUND)

    RUNTIME.mkdir(parents=True, exist_ok=True)
    REVIEWS.mkdir(parents=True, exist_ok=True)

    with Image.open(PLATFORM_SOURCE) as source:
        platform_source = source.convert("RGBA")

    tower = build_tower()
    platform = normalize_platform(platform_source, PLATFORM_SIZE)
    cable = build_cable()
    runway = build_runway()
    gantry_car = build_gantry_car(platform_source)

    outputs = [
        (TOWER_PATH, tower),
        (PLATFORM_PATH, platform),
        (CABLE_PATH, cable),
        (RUNWAY_PATH, runway),
        (GANTRY_CAR_PATH, gantry_car),
        (
            KIT_REVIEW_PATH,
            build_kit_review(
                tower,
                platform,
                cable,
                runway,
                gantry_car,
            ),
        ),
        (
            ROOM_REVIEW_PATH,
            build_room_review(
                tower,
                platform,
                cable,
                runway,
                gantry_car,
            ),
        ),
    ]
    for path, image in outputs:
        image.save(path, optimize=True)
        print(
            f"{path.relative_to(ROOT)} "
            f"{image.width}x{image.height}"
        )


if __name__ == "__main__":
    main()
