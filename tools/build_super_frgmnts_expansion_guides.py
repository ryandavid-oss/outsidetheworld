#!/usr/bin/env python3
"""Build revision-3 vertical expansion guides for SUPER FRGMNTS.

The live game is the coordinate authority. This script reads its world,
movement, and Deepworks constants before deriving composite coordinates.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont


ROOT = Path(__file__).resolve().parents[1]
GAME_FILE = ROOT / "super_frgmnts.html"
OUTPUT_DIR = ROOT / "Design" / "Super-Frgmnts" / "Expansion-Guides"

PLATE_WIDTH = 1672
PLATE_HEIGHT = 941
COMPOSITE_HEIGHT = PLATE_HEIGHT * 2
BLEND_HEIGHT = 180
BLEND_END = PLATE_HEIGHT + BLEND_HEIGHT
PROTECT_TOP = BLEND_END

GRID = 16
NORMAL_RISE = 128
BOOST_RISE = 192
PLATFORM_HEIGHT = 24
MIN_PLATFORM_WIDTH = 144
MAX_HORIZONTAL_GAP = 160
PLAYER_COLLISION_HEIGHT = 100
PLAYER_DRAW_HEIGHT = 112
JUMP_SAFETY_MARGIN = 8

FONT_PATH = "/System/Library/Fonts/SFNSMono.ttf"
FONT_BOLD_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

COLORS = {
    "void": (5, 7, 19),
    "panel": (7, 10, 23, 238),
    "ink": (247, 240, 234, 255),
    "muted": (186, 198, 215, 255),
    "current": (232, 238, 245, 255),
    "proposed": (88, 245, 223, 255),
    "anchor": (119, 163, 255, 255),
    "moving": (255, 211, 108, 255),
    "boost": (255, 105, 180, 255),
    "annotation": (185, 140, 255, 255),
    "route_left": (120, 255, 200, 255),
    "route_right": (150, 190, 255, 255),
    "rose": (224, 191, 184, 255),
    "red": (255, 92, 112, 255),
}


ROOMS = {
    "foundry": {
        "title": "FOUNDRY",
        "source": ROOT / "Images" / "Builder" / "signal-foundry-bg.png",
        "lanes": {
            "LA": (0, 288),
            "LB": (368, 688),
            "M": (752, 920),
            "RB": (992, 1312),
            "RA": (1392, 1672),
            "BOOST": (704, 976),
        },
        "current": [
            (318, 567, 204, "current"),
            (632, 443, 188, "current"),
            (954, 566, 218, "current"),
            (1239, 447, 186, "current"),
        ],
        "moving": [(704, 900, 272, 56)],
    },
    "refinery": {
        "title": "REFINERY",
        "source": ROOT / "Images" / "Game" / "signal-foundry-refinery.png",
        "lanes": {
            "LA": (0, 304),
            "LB": (352, 672),
            "M": (752, 920),
            "RB": (1008, 1328),
            "RA": (1376, 1672),
            "BOOST": (704, 976),
        },
        "current": [
            (278, 554, 205, "current"),
            (612, 432, 185, "current"),
            (954, 548, 218, "moving"),
            (1282, 422, 180, "current"),
        ],
        "moving": [(688, 772, 288, 64), (704, 1028, 272, 48)],
    },
    "biolab": {
        "title": "BIOLAB",
        "source": ROOT / "Images" / "Game" / "signal-foundry-biolab.png",
        "lanes": {
            "LA": (0, 320),
            "LB": (384, 720),
            "M": (752, 912),
            "RB": (960, 1296),
            "RA": (1360, 1672),
            "BOOST": (704, 976),
        },
        "current": [
            (198, 542, 214, "current"),
            (514, 414, 188, "current"),
            (854, 532, 218, "moving"),
            (1172, 402, 188, "current"),
            (1452, 540, 170, "current"),
        ],
        "moving": [(704, 900, 272, 56)],
    },
    "uplink": {
        "title": "UPLINK",
        "source": ROOT / "Images" / "Game" / "signal-foundry-uplink.png",
        "lanes": {
            "LA": (0, 272),
            "LB": (336, 672),
            "M": (752, 920),
            "RB": (1008, 1344),
            "RA": (1408, 1672),
            "BOOST": (704, 976),
        },
        "current": [
            (204, 550, 205, "current"),
            (532, 426, 188, "current"),
            (862, 548, 218, "moving"),
            (1184, 416, 188, "current"),
            (1438, 532, 148, "current"),
        ],
        "moving": [(704, 772, 272, 64)],
    },
}


def extract_number(source: str, pattern: str, label: str) -> float:
    match = re.search(pattern, source, flags=re.MULTILINE | re.DOTALL)
    if not match:
        raise ValueError(f"Could not read {label} from {GAME_FILE}")
    return float(match.group(1))


def read_game_contract() -> dict[str, float | int]:
    source = GAME_FILE.read_text(encoding="utf-8")
    return {
        "width": int(extract_number(source, r"var WIDTH = (\d+);", "WIDTH")),
        "height": int(extract_number(source, r"var HEIGHT = (\d+);", "HEIGHT")),
        "ground_y": int(extract_number(source, r"var GROUND_Y = (\d+);", "GROUND_Y")),
        "deepworks_y": int(
            extract_number(
                source,
                r"var deepworksRooms = .*?y: (\d+),",
                "Deepworks y",
            )
        ),
        "jump_velocity": extract_number(
            source,
            r"player\.vy = inDeepworks \? -\d+ : -(\d+);",
            "normal jump velocity",
        ),
        "gravity": extract_number(
            source,
            r"player\.vy \+= (\d+) \* delta;",
            "gravity",
        ),
        "delta_cap": extract_number(
            source,
            r"Math\.min\((0\.\d+), \(now - lastFrame\)",
            "frame delta cap",
        ),
    }


GAME = read_game_contract()
if (GAME["width"], GAME["height"]) != (PLATE_WIDTH, PLATE_HEIGHT):
    raise ValueError(
        "Expansion plates must match the live game canvas exactly; "
        f"game is {GAME['width']}×{GAME['height']}, plates are "
        f"{PLATE_WIDTH}×{PLATE_HEIGHT}"
    )

DECK_Y = PLATE_HEIGHT + int(GAME["ground_y"])
DEEPWORKS_Y = PLATE_HEIGHT + int(GAME["deepworks_y"])
DEEPWORKS_LEFT = 258
DEEPWORKS_RIGHT = 1124
DROP_ENTRY_LEFT = 300
DROP_ENTRY_RIGHT = 1082
GRID_PHASE_Y = DECK_Y % GRID
ROUTE_BANDS = [DECK_Y - NORMAL_RISE * index for index in range(1, 13)]
TRANSITION_Y = DECK_Y - NORMAL_RISE * 8
BOOST_LAUNCH_Y = DECK_Y - BOOST_RISE
BOOST_PERCH_Y = TRANSITION_Y - BOOST_RISE


def simulated_jump_rise(velocity: float, gravity: float, delta: float) -> float:
    y = 0.0
    minimum_y = 0.0
    vertical_velocity = -velocity
    while vertical_velocity < 0:
        vertical_velocity += gravity * delta
        y += vertical_velocity * delta
        minimum_y = min(minimum_y, y)
    return -minimum_y


WORST_FRAME_JUMP_RISE = simulated_jump_rise(
    float(GAME["jump_velocity"]),
    float(GAME["gravity"]),
    float(GAME["delta_cap"]),
)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD_PATH if bold else FONT_PATH, size)


def text_box(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    *,
    fill: tuple[int, int, int, int] = COLORS["ink"],
    background: tuple[int, int, int, int] = COLORS["panel"],
    outline: tuple[int, int, int, int] = COLORS["anchor"],
    size: int = 18,
    bold: bool = False,
    padding: int = 7,
) -> tuple[int, int, int, int]:
    label_font = font(size, bold)
    bounds = draw.textbbox(xy, text, font=label_font)
    rect = (
        bounds[0] - padding,
        bounds[1] - padding,
        bounds[2] + padding,
        bounds[3] + padding,
    )
    draw.rounded_rectangle(rect, radius=3, fill=background, outline=outline, width=2)
    draw.text(xy, text, font=label_font, fill=fill)
    return rect


def dashed_line(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    *,
    fill: tuple[int, int, int, int],
    width: int = 2,
    dash: int = 14,
    gap: int = 10,
) -> None:
    x1, y1 = start
    x2, y2 = end
    if y1 == y2:
        cursor = x1
        while cursor < x2:
            draw.line((cursor, y1, min(cursor + dash, x2), y2), fill=fill, width=width)
            cursor += dash + gap
        return
    if x1 == x2:
        cursor = y1
        while cursor < y2:
            draw.line((x1, cursor, x2, min(cursor + dash, y2)), fill=fill, width=width)
            cursor += dash + gap
        return
    raise ValueError("Only horizontal or vertical dashed lines are supported")


def horizontal_gap(first: tuple[int, int], second: tuple[int, int]) -> int:
    first_left, first_right = first
    second_left, second_right = second
    if min(first_right, second_right) >= max(first_left, second_left):
        return 0
    return max(first_left, second_left) - min(first_right, second_right)


def planned_platforms(config: dict) -> list[dict]:
    lanes = config["lanes"]
    planned: list[dict] = []
    for route, lane_pair in (("left", ("LA", "LB")), ("right", ("RA", "RB"))):
        for index, y in enumerate(ROUTE_BANDS):
            lane = lane_pair[index % 2]
            x0, x1 = lanes[lane]
            planned.append(
                {
                    "x0": x0,
                    "x1": x1,
                    "y": y,
                    "kind": "proposed" if y < PROTECT_TOP else "annotation",
                    "role": f"{route}-route",
                    "lane": lane,
                    "bake_into_art": y < PROTECT_TOP,
                }
            )

    for lane in ("LA", "RA"):
        x0, x1 = lanes[lane]
        planned.append(
            {
                "x0": x0,
                "x1": x1,
                "y": TRANSITION_Y,
                "kind": "anchor",
                "role": "room-transition",
                "lane": lane,
                "bake_into_art": True,
            }
        )

    for y in (ROUTE_BANDS[3], TRANSITION_Y, ROUTE_BANDS[-1]):
        x0, x1 = lanes["M"]
        planned.append(
            {
                "x0": x0,
                "x1": x1,
                "y": y,
                "kind": "proposed",
                "role": "cross-link",
                "lane": "M",
                "bake_into_art": y < PROTECT_TOP,
            }
        )

    boost_x0, boost_x1 = lanes["BOOST"]
    for y, role in (
        (BOOST_LAUNCH_Y, "boost-launch"),
        (BOOST_PERCH_Y, "boost-perch"),
    ):
        planned.append(
            {
                "x0": boost_x0,
                "x1": boost_x1,
                "y": y,
                "kind": "boost" if y < PROTECT_TOP else "boost-annotation",
                "role": role,
                "lane": "BOOST",
                "bake_into_art": y < PROTECT_TOP,
            }
        )
    return sorted(planned, key=lambda platform: (platform["y"], platform["x0"], platform["kind"]))


def current_platforms(config: dict) -> list[dict]:
    return [
        {
            "x0": x,
            "x1": x + width,
            "y": PLATE_HEIGHT + y,
            "kind": kind,
            "role": "current-runtime",
            "lane": "CURRENT",
            "bake_into_art": False,
        }
        for x, y, width, kind in config["current"]
    ]


def validate_geometry(key: str, config: dict) -> None:
    lanes = config["lanes"]
    errors: list[str] = []

    if DECK_Y != PLATE_HEIGHT + int(GAME["ground_y"]):
        errors.append("deck does not map directly from the live game")
    if DEEPWORKS_Y != PLATE_HEIGHT + int(GAME["deepworks_y"]):
        errors.append("Deepworks does not map directly from the live game")
    if NORMAL_RISE + JUMP_SAFETY_MARGIN > WORST_FRAME_JUMP_RISE:
        errors.append(
            f"normal rise {NORMAL_RISE} leaves less than {JUMP_SAFETY_MARGIN}px "
            f"below the simulated {WORST_FRAME_JUMP_RISE:.2f}px jump"
        )

    for lane_name, (x0, x1) in lanes.items():
        if x0 % GRID:
            errors.append(f"{lane_name} x0={x0} is not on the {GRID}px grid")
        if x1 - x0 < MIN_PLATFORM_WIDTH:
            errors.append(f"{lane_name} width {x1 - x0} is under {MIN_PLATFORM_WIDTH}px")

    for route, lane_pair in (("left", ("LA", "LB")), ("right", ("RA", "RB"))):
        previous = (0, PLATE_WIDTH)
        previous_y = DECK_Y
        for index, y in enumerate(ROUTE_BANDS):
            lane = lane_pair[index % 2]
            current = lanes[lane]
            rise = previous_y - y
            gap = horizontal_gap(previous, current)
            if rise != NORMAL_RISE:
                errors.append(f"{route} route rise {previous_y}->{y} is {rise}px")
            if gap > MAX_HORIZONTAL_GAP:
                errors.append(f"{route} route gap to {lane}@{y} is {gap}px")
            previous = current
            previous_y = y

    for lane in ("LA", "RA"):
        x0, x1 = lanes[lane]
        if lane == "LA" and x0 != 0:
            errors.append("left transition anchor does not touch x=0")
        if lane == "RA" and x1 != PLATE_WIDTH:
            errors.append(f"right transition anchor does not touch x={PLATE_WIDTH}")
        route_lane = lanes["LB" if lane == "LA" else "RB"]
        if horizontal_gap((x0, x1), route_lane) > MAX_HORIZONTAL_GAP:
            errors.append(f"{lane} transition anchor is disconnected")

    for platform in planned_platforms(config):
        if platform["y"] >= PROTECT_TOP and platform["bake_into_art"]:
            errors.append(f"{platform['role']} at y={platform['y']} alters protected art")
        if platform["y"] < PROTECT_TOP and not platform["bake_into_art"]:
            errors.append(f"{platform['role']} at y={platform['y']} is missing from art")

    if errors:
        raise ValueError(f"{key} geometry failed:\n- " + "\n- ".join(errors))


def build_expansion_canvas(source: Image.Image) -> Image.Image:
    canvas = Image.new("RGBA", (PLATE_WIDTH, COMPOSITE_HEIGHT), (0, 0, 0, 0))
    canvas.paste(source.convert("RGBA"), (0, PLATE_HEIGHT))
    return canvas


def build_outpaint_mask() -> Image.Image:
    mask = Image.new("L", (PLATE_WIDTH, COMPOSITE_HEIGHT), 0)
    ImageDraw.Draw(mask).rectangle((0, 0, PLATE_WIDTH, PROTECT_TOP - 1), fill=255)
    return mask


def draw_grid(draw: ImageDraw.ImageDraw) -> None:
    for x in range(0, PLATE_WIDTH + 1, GRID):
        alpha = 30 if x % 128 else 78
        draw.line((x, 0, x, COMPOSITE_HEIGHT), fill=(119, 163, 255, alpha), width=1)
    for y in range(GRID_PHASE_Y, COMPOSITE_HEIGHT + 1, GRID):
        alpha = 30 if (y - GRID_PHASE_Y) % 128 else 78
        draw.line((0, y, PLATE_WIDTH, y), fill=(119, 163, 255, alpha), width=1)


def draw_platform(draw: ImageDraw.ImageDraw, platform: dict) -> None:
    x0, x1, y = platform["x0"], platform["x1"], platform["y"]
    kind = platform["kind"]
    color_key = "annotation" if kind in ("annotation", "boost-annotation") else kind
    color = COLORS[color_key]

    if kind in ("annotation", "boost-annotation"):
        outline = COLORS["boost"] if kind == "boost-annotation" else color
        draw.rectangle((x0, y, x1 - 1, y + PLATFORM_HEIGHT), outline=outline, width=2)
        for marker_x in range(x0 + 4, x1 - 8, GRID):
            draw.line(
                (marker_x, y + 2, marker_x + 8, y + PLATFORM_HEIGHT - 2),
                fill=(*outline[:3], 120),
                width=1,
            )
        draw.line((x0, y, x1 - 1, y), fill=outline, width=4)
        return

    draw.rectangle(
        (x0, y, x1 - 1, y + PLATFORM_HEIGHT),
        fill=(*color[:3], 60),
        outline=color,
        width=2,
    )
    draw.line((x0, y, x1 - 1, y), fill=color, width=5)


def platform_center(platform: dict) -> tuple[int, int]:
    return ((platform["x0"] + platform["x1"]) // 2, platform["y"])


def draw_routes(draw: ImageDraw.ImageDraw, config: dict, planned: list[dict]) -> None:
    by_key = {(platform["role"], platform["y"]): platform for platform in planned}
    for route, color in (("left-route", COLORS["route_left"]), ("right-route", COLORS["route_right"])):
        previous = {
            "x0": 0,
            "x1": PLATE_WIDTH,
            "y": DECK_Y,
        }
        for y in ROUTE_BANDS:
            current = by_key[(route, y)]
            first = platform_center(previous)
            second = platform_center(current)
            draw.line((first, second), fill=(*color[:3], 178), width=3)
            previous = current


def build_collision_guide(key: str, config: dict, source: Image.Image) -> Image.Image:
    guide = Image.new("RGBA", (PLATE_WIDTH, COMPOSITE_HEIGHT), (*COLORS["void"], 255))
    dimmed_source = ImageEnhance.Brightness(source.convert("RGB")).enhance(0.46).convert("RGBA")
    guide.paste(dimmed_source, (0, PLATE_HEIGHT))

    overlay = Image.new("RGBA", guide.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, PLATE_WIDTH, PLATE_HEIGHT - 1), fill=(27, 54, 93, 112))
    draw.rectangle(
        (0, PLATE_HEIGHT, PLATE_WIDTH - 1, PROTECT_TOP - 1),
        fill=(255, 211, 108, 52),
        outline=COLORS["moving"],
        width=3,
    )
    dashed_line(
        draw,
        (0, PROTECT_TOP),
        (PLATE_WIDTH, PROTECT_TOP),
        fill=COLORS["red"],
        width=3,
        dash=20,
        gap=12,
    )
    draw_grid(draw)

    planned = planned_platforms(config)
    draw_routes(draw, config, planned)

    for y in ROUTE_BANDS:
        dashed_line(
            draw,
            (0, y),
            (PLATE_WIDTH, y),
            fill=(119, 163, 255, 112),
            width=1,
            dash=10,
            gap=18,
        )

    for platform in current_platforms(config):
        draw_platform(draw, platform)
    for platform in planned:
        draw_platform(draw, platform)

    for x, y, width, travel in config["moving"]:
        color = COLORS["moving"]
        draw.rectangle(
            (x, y - travel, x + width, y + travel + PLATFORM_HEIGHT),
            fill=(*color[:3], 18),
            outline=(*color[:3], 190),
            width=2,
        )
        dashed_line(
            draw,
            (x + width // 2, y - travel),
            (x + width // 2, y + travel),
            fill=color,
        )

    dashed_line(draw, (0, DECK_Y), (PLATE_WIDTH, DECK_Y), fill=COLORS["current"], width=5)
    dashed_line(draw, (0, DEEPWORKS_Y), (PLATE_WIDTH, DEEPWORKS_Y), fill=COLORS["moving"], width=3)
    draw.rectangle(
        (DEEPWORKS_LEFT, DECK_Y, DEEPWORKS_RIGHT, DEEPWORKS_Y),
        fill=(88, 245, 223, 26),
        outline=(*COLORS["proposed"][:3], 160),
        width=2,
    )

    text_box(
        draw,
        (24, 24),
        f"SUPER FRGMNTS // {config['title']} // EXPANSION GUIDE REV 3",
        outline=COLORS["proposed"],
        size=23,
        bold=True,
        padding=10,
    )
    text_box(
        draw,
        (24, 78),
        (
            f"LIVE GAME: {GAME['width']}x{GAME['height']} // "
            f"NORMAL RISE {NORMAL_RISE} // GRID {GRID} PHASE {GRID_PHASE_Y}"
        ),
        fill=COLORS["anchor"],
        outline=COLORS["anchor"],
        size=14,
        padding=6,
    )
    text_box(
        draw,
        (24, TRANSITION_Y - 34),
        f"ROOM TRANSITION // Y {TRANSITION_Y}",
        fill=COLORS["anchor"],
        outline=COLORS["anchor"],
        size=14,
        padding=6,
    )
    text_box(
        draw,
        (24, PLATE_HEIGHT + 18),
        f"BLEND / INPAINT // Y {PLATE_HEIGHT}-{PROTECT_TOP - 1}",
        fill=COLORS["moving"],
        outline=COLORS["moving"],
        size=14,
        padding=6,
    )
    text_box(
        draw,
        (24, PROTECT_TOP + 18),
        f"PROTECTED ORIGINAL // Y {PROTECT_TOP}+",
        fill=COLORS["red"],
        outline=COLORS["red"],
        size=14,
        padding=6,
    )
    text_box(
        draw,
        (24, DECK_Y - 48),
        f"CONCRETE DECK // Y {DECK_Y}",
        fill=COLORS["current"],
        outline=COLORS["current"],
        size=14,
        padding=6,
    )
    text_box(
        draw,
        (DEEPWORKS_LEFT + 18, DEEPWORKS_Y - 42),
        (
            f"DEEPWORKS // Y {DEEPWORKS_Y} // "
            f"PLAYABLE X {DEEPWORKS_LEFT}-{DEEPWORKS_RIGHT}"
        ),
        fill=COLORS["moving"],
        outline=COLORS["moving"],
        size=13,
        padding=5,
    )

    legend_x0, legend_y0, legend_x1, legend_y1 = 696, 646, 976, 818
    draw.rounded_rectangle(
        (legend_x0, legend_y0, legend_x1, legend_y1),
        radius=5,
        fill=COLORS["panel"],
        outline=COLORS["rose"],
        width=2,
    )
    draw.text(
        (legend_x0 + 14, legend_y0 + 10),
        "COLLISION LEGEND",
        font=font(15, True),
        fill=COLORS["ink"],
    )
    legend_items = [
        ("current", "CURRENT RUNTIME"),
        ("proposed", "GENERATE STRUCTURE"),
        ("anchor", "ROOM LINK"),
        ("boost", "BOOST OPTIONAL"),
        ("annotation", "COLLISION ONLY"),
        ("moving", "MOVING PATH"),
    ]
    for index, (color_key, label) in enumerate(legend_items):
        item_y = legend_y0 + 40 + index * 21
        draw.line(
            (legend_x0 + 14, item_y + 6, legend_x0 + 50, item_y + 6),
            fill=COLORS[color_key],
            width=5,
        )
        draw.text(
            (legend_x0 + 60, item_y - 2),
            label,
            font=font(12),
            fill=COLORS["muted"],
        )

    return Image.alpha_composite(guide, overlay).convert("RGB")


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
        draw.text(
            (x, y + thumb_height + 10),
            name.upper(),
            font=font(18, True),
            fill=COLORS["ink"],
        )
    return sheet


def validate_expansion_canvas(canvas: Image.Image, source: Image.Image) -> None:
    if canvas.size != (PLATE_WIDTH, COMPOSITE_HEIGHT):
        raise ValueError(f"Unexpected expansion canvas dimensions: {canvas.size}")
    upper_alpha = canvas.getchannel("A").crop((0, 0, PLATE_WIDTH, PLATE_HEIGHT))
    if upper_alpha.getbbox() is not None:
        raise ValueError("Upper outpaint region must be completely transparent")
    lower = canvas.crop((0, PLATE_HEIGHT, PLATE_WIDTH, COMPOSITE_HEIGHT))
    if lower.tobytes() != source.convert("RGBA").tobytes():
        raise ValueError("Source plate pixels changed in the lower half")


def manifest_for_room(config: dict) -> dict:
    return {
        "source": str(config["source"].relative_to(ROOT)),
        "lanes": {key: list(value) for key, value in config["lanes"].items()},
        "planned_platforms": planned_platforms(config),
        "current_runtime_platforms": current_platforms(config),
        "moving_platform_concepts": [
            {
                "x0": x,
                "x1": x + width,
                "center_y": y,
                "travel": travel,
            }
            for x, y, width, travel in config["moving"]
        ],
    }


def build_manifest() -> dict:
    return {
        "revision": 3,
        "coordinate_authority": "super_frgmnts.html",
        "canvas": [PLATE_WIDTH, COMPOSITE_HEIGHT],
        "source_plate": [PLATE_WIDTH, PLATE_HEIGHT],
        "new_upper_plate": [0, PLATE_HEIGHT - 1],
        "blend_zone": [PLATE_HEIGHT, PROTECT_TOP - 1],
        "protected_from": PROTECT_TOP,
        "live_game": GAME,
        "composite_anchors": {
            "concrete_deck_y": DECK_Y,
            "deepworks_floor_y": DEEPWORKS_Y,
            "deepworks_playable_x": [DEEPWORKS_LEFT, DEEPWORKS_RIGHT],
            "drop_entry_x": [DROP_ENTRY_LEFT, DROP_ENTRY_RIGHT],
            "room_transition_y": TRANSITION_Y,
        },
        "movement_contract": {
            "normal_rise": NORMAL_RISE,
            "boost_rise": BOOST_RISE,
            "normal_jump_rise_at_delta_cap": round(WORST_FRAME_JUMP_RISE, 3),
            "jump_safety_margin": JUMP_SAFETY_MARGIN,
            "max_horizontal_gap": MAX_HORIZONTAL_GAP,
            "player_collision_height": PLAYER_COLLISION_HEIGHT,
            "player_draw_height": PLAYER_DRAW_HEIGHT,
            "grid": GRID,
            "grid_phase_y": GRID_PHASE_Y,
        },
        "rooms": {key: manifest_for_room(config) for key, config in ROOMS.items()},
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rendered_guides: list[tuple[str, Image.Image]] = []

    for key, config in ROOMS.items():
        validate_geometry(key, config)
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

    build_contact_sheet(rendered_guides).save(
        OUTPUT_DIR / "super-frgmnts-expansion-guides-contact-sheet.png",
        optimize=True,
    )
    (OUTPUT_DIR / "collision-manifest.json").write_text(
        json.dumps(build_manifest(), indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"PASS: generated revision-3 guides in {OUTPUT_DIR}")
    print(f"  live game canvas       {GAME['width']}×{GAME['height']}")
    print(f"  deck / Deepworks       y={DECK_Y} / y={DEEPWORKS_Y}")
    print(
        f"  jump at {float(GAME['delta_cap']) * 1000:.0f}ms cap  "
        f"{WORST_FRAME_JUMP_RISE:.2f}px; route rise {NORMAL_RISE}px"
    )
    print(f"  room transition        y={TRANSITION_Y}")


if __name__ == "__main__":
    main()
