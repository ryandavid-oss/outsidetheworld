#!/usr/bin/env python3
"""Build approval studies for the SUPER FRGMNTS Breathing Chamber."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Images" / "Game" / "super-frgmnts-foundry-expanded-prototype-v1.png"
FAN_HOUSING = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "foundry-ventilation-fan-housing-v1.png"
)
FAN_ROTOR = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "foundry-ventilation-fan-rotor-v1.png"
)
STABILIZER_DORMANT = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "atmospheric-stabilizer-dormant-v1.png"
)
STABILIZER_ACTIVE = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "atmospheric-stabilizer-active-v1.png"
)
OUTPUT = ROOT / "Design" / "Super-Frgmnts" / "Breathing-Chamber"

WIDTH = 1672
HEIGHT = 1882
FAN_CENTER = (627, 594)
FAN_SCALE = 0.26

INK = "#f4f0eb"
NAVY = "#03050d"
PANEL = "#091124"
GRID = "#223457"
CYAN = "#58f5df"
BLUE = "#77a3ff"
ROSE = "#ff69b4"
GOLD = "#ffd36c"
VIOLET = "#b47cff"
MUTED = "#a7b4cf"

FONT_MONO = Path("/System/Library/Fonts/SFNSMono.ttf")
FONT_DISPLAY = Path("/System/Library/Fonts/Avenir Next Condensed.ttc")


def font(size: int, display: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_DISPLAY if display else FONT_MONO
    return ImageFont.truetype(str(path), size=size)


def alpha_fill(image: Image.Image, color: str, alpha: int) -> None:
    overlay = Image.new("RGBA", image.size, color)
    overlay.putalpha(alpha)
    image.alpha_composite(overlay)


def label(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    *,
    color: str = INK,
    fill: str = PANEL,
    size: int = 22,
    anchor: str = "la",
    padding: int = 10,
) -> None:
    face = font(size)
    box = draw.textbbox(xy, text, font=face, anchor=anchor, stroke_width=0)
    draw.rounded_rectangle(
        (
            box[0] - padding,
            box[1] - padding // 2,
            box[2] + padding,
            box[3] + padding // 2,
        ),
        radius=5,
        fill=fill,
        outline=color,
        width=2,
    )
    draw.text(xy, text, font=face, fill=color, anchor=anchor)


def arrow(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[int, int]],
    color: str,
    *,
    width: int = 10,
    head: int = 24,
) -> None:
    draw.line(points, fill=color, width=width, joint="curve")
    x1, y1 = points[-2]
    x2, y2 = points[-1]
    angle = math.atan2(y2 - y1, x2 - x1)
    left = (
        x2 - head * math.cos(angle - math.pi / 6),
        y2 - head * math.sin(angle - math.pi / 6),
    )
    right = (
        x2 - head * math.cos(angle + math.pi / 6),
        y2 - head * math.sin(angle + math.pi / 6),
    )
    draw.polygon([(x2, y2), left, right], fill=color)


def fan_layer(active: bool, angle: float, opacity: float = 1.0) -> Image.Image:
    housing = Image.open(FAN_HOUSING).convert("RGBA")
    rotor = Image.open(FAN_ROTOR).convert("RGBA")
    rotor = rotor.rotate(
        angle,
        resample=Image.Resampling.NEAREST,
        center=FAN_CENTER,
        expand=False,
    )
    combined = Image.alpha_composite(housing, rotor)

    if active:
        alpha = combined.getchannel("A")
        glow_alpha = alpha.filter(ImageFilter.GaussianBlur(28))
        glow = Image.new("RGBA", combined.size, CYAN)
        glow.putalpha(glow_alpha.point(lambda value: int(value * 0.18)))
        combined = Image.alpha_composite(glow, combined)

    target = (
        round(combined.width * FAN_SCALE),
        round(combined.height * FAN_SCALE),
    )
    combined = combined.resize(target, Image.Resampling.NEAREST)
    if opacity < 1:
        combined.putalpha(combined.getchannel("A").point(lambda a: int(a * opacity)))
    return combined


def place_fan(
    room: Image.Image,
    center: tuple[int, int],
    *,
    active: bool,
    angle: float,
    opacity: float = 1.0,
) -> None:
    fan = fan_layer(active, angle, opacity)
    source_center = (
        round(FAN_CENTER[0] * FAN_SCALE),
        round(FAN_CENTER[1] * FAN_SCALE),
    )
    x = center[0] - source_center[0]
    y = center[1] - source_center[1]
    room.alpha_composite(fan, (x, y))


def base_room(*, active: bool) -> Image.Image:
    room = ImageOps.mirror(Image.open(SOURCE).convert("RGBA"))
    place_fan(room, (541, 218), active=active, angle=12, opacity=1 if active else 0.58)
    place_fan(room, (1186, 218), active=active, angle=39, opacity=1 if active else 0.58)
    stabilizer_path = STABILIZER_ACTIVE if active else STABILIZER_DORMANT
    stabilizer = Image.open(stabilizer_path).convert("RGBA")
    stabilizer = stabilizer.resize((420, 735), Image.Resampling.LANCZOS)
    room.alpha_composite(stabilizer, (1210, 869))
    return room


def draw_platforms(draw: ImageDraw.ImageDraw) -> None:
    painted = [
        (907, 891, 1522, 915),
        (226, 891, 816, 915),
        (1026, 600, 1672, 624),
        (0, 600, 696, 624),
        (1059, 338, 1652, 362),
        (798, 338, 925, 362),
        (24, 338, 668, 362),
    ]
    descent = [
        (1152, 1370, 1362, 1394),
        (846, 1122, 1022, 1140),
        (506, 997, 682, 1025),
        (322, 760, 492, 778),
        (662, 635, 832, 659),
        (1012, 480, 1182, 498),
        (0, 210, 280, 238),
    ]
    for rect in painted:
        draw.rectangle(rect, outline=BLUE, width=5)
    for rect in descent:
        draw.rectangle(rect, fill="#173b43", outline=CYAN, width=5)


def traversal_study() -> Image.Image:
    room = base_room(active=True)
    alpha_fill(room, NAVY, 86)
    draw = ImageDraw.Draw(room, "RGBA")

    for x in range(0, WIDTH + 1, 104):
        draw.line((x, 0, x, HEIGHT), fill=GRID + "55", width=1)
    for y in range(0, HEIGHT + 1, 104):
        draw.line((0, y, WIDTH, y), fill=GRID + "55", width=1)

    draw_platforms(draw)

    # Primary set-piece elements.
    draw.line((930, 735, 930, 1510), fill=GOLD, width=7)
    draw.line((1130, 735, 1130, 1510), fill=GOLD, width=7)
    for rail_y in range(790, 1480, 70):
        draw.line((930, rail_y, 1130, rail_y), fill=GOLD + "77", width=3)
    draw.rounded_rectangle(
        (900, 720, 1160, 765),
        radius=8,
        fill="#2f291cdd",
        outline=GOLD,
        width=7,
    )
    draw.rounded_rectangle(
        (900, 1470, 1160, 1515),
        radius=8,
        outline=GOLD + "77",
        width=4,
    )

    draw.rounded_rectangle(
        (1210, 869, 1630, 1604),
        radius=22,
        outline=ROSE,
        width=8,
    )
    # The old deck-level room transition becomes a permanent service bulkhead.
    # Refinery access is deliberately moved to the restored upper exit.
    draw.rectangle((1645, 1418, 1671, 1604), fill="#100915dd", outline=ROSE, width=5)
    for field_y in range(1435, 1590, 26):
        draw.line((1649, field_y, 1667, field_y + 14), fill=ROSE, width=3)
    draw.rectangle((1588, 288, 1671, 620), outline=CYAN, width=8)
    draw.line((1588, 338, 1671, 338), fill=CYAN, width=12)

    descent_points = [
        (138, 226),
        (330, 355),
        (1088, 490),
        (744, 647),
        (408, 770),
        (592, 1010),
        (930, 1135),
        (1257, 1390),
        (1410, 1545),
    ]
    arrow(draw, descent_points, ROSE, width=11, head=30)

    ascent_points = [
        (1410, 1545),
        (1030, 1480),
        (1030, 750),
        (1120, 615),
        (1095, 490),
        (1300, 350),
        (1638, 338),
    ]
    arrow(draw, ascent_points, CYAN, width=12, head=32)

    # Camera bands and room-scale annotations.
    for y, text in (
        (338, "UPPER CROSS TIER"),
        (600, "MID GANTRY"),
        (997, "LOWER SHAFT"),
        (1604, "MAIN CONCRETE DECK"),
        (1816, "DEEPWORKS FLOOR"),
    ):
        draw.line((0, y, WIDTH, y), fill=VIOLET + "aa", width=2)
        label(draw, (18, y - 15), f"Y {y} // {text}", color=VIOLET, size=18)

    draw.rounded_rectangle(
        (18, 18, 1240, 112),
        radius=8,
        fill=NAVY + "e8",
        outline=CYAN,
        width=3,
    )
    draw.text(
        (40, 34),
        "SUPER FRGMNTS // THE BREATHING CHAMBER",
        font=font(34, display=True),
        fill=INK,
    )
    draw.text(
        (42, 78),
        "THE ROOM IS A ONE-WAY FALL THAT BECOMES AN ASCENT WHEN IT BREATHES",
        font=font(18),
        fill=CYAN,
    )

    label(draw, (46, 178), "ENTRY // DORMANT", color=BLUE, size=18)
    label(draw, (1508, 270), "RESTORED EXIT", color=CYAN, size=18, anchor="ra")
    label(draw, (1395, 840), "ATMOSPHERIC STABILIZER", color=ROSE, size=18, anchor="ma")
    label(draw, (890, 700), "FULL-HEIGHT FREIGHT LIFT", color=GOLD, size=18, anchor="ra")
    label(draw, (890, 1535), "LIFT BOARDS HERE", color=GOLD, size=18, anchor="ra")
    label(
        draw,
        (1630, 1390),
        "DECK ROUTE SEALED",
        color=ROSE,
        size=16,
        anchor="ra",
    )

    legend_y = 1720
    draw.rounded_rectangle(
        (24, legend_y, 1648, 1795),
        radius=8,
        fill=NAVY + "e8",
        outline=MUTED,
        width=2,
    )
    legend = (
        (ROSE, "DORMANT DESCENT"),
        (CYAN, "RESTORED ASCENT"),
        (GOLD, "POWERED LIFT"),
        (BLUE, "PAINTED CATWALK"),
    )
    cursor = 55
    for color, text in legend:
        draw.line((cursor, legend_y + 38, cursor + 46, legend_y + 38), fill=color, width=8)
        draw.text(
            (cursor + 62, legend_y + 38),
            text,
            font=font(17),
            fill=INK,
            anchor="lm",
        )
        cursor += 385

    draw.line((0, 1816, WIDTH, 1816), fill=GOLD, width=4)
    return room.convert("RGB")


def scaled_room_state(active: bool, panel_size: tuple[int, int]) -> Image.Image:
    room = base_room(active=active)
    draw = ImageDraw.Draw(room, "RGBA")

    if active:
        # Clean-air direction and powered lift.
        for center_x in (541, 1186):
            for radius, alpha in ((210, 28), (145, 36), (90, 48)):
                draw.ellipse(
                    (
                        center_x - radius,
                        218 - radius,
                        center_x + radius,
                        218 + radius,
                    ),
                    outline=CYAN + f"{alpha:02x}",
                    width=14,
                )
        draw.line((930, 735, 930, 1510), fill=GOLD, width=9)
        draw.line((1130, 735, 1130, 1510), fill=GOLD, width=9)
        for rail_y in range(790, 1480, 70):
            draw.line((930, rail_y, 1130, rail_y), fill=GOLD + "66", width=4)
        draw.rounded_rectangle(
            (900, 720, 1160, 765),
            radius=8,
            fill="#2f291cdd",
            outline=GOLD,
            width=9,
        )
        draw.rounded_rectangle(
            (900, 1470, 1160, 1515),
            radius=8,
            outline=GOLD + "77",
            width=5,
        )
        arrow(
            draw,
            [(1410, 1540), (1030, 1480), (1030, 750), (1120, 610), (1640, 338)],
            CYAN,
            width=15,
            head=38,
        )
        cyan_wash = Image.new("RGBA", room.size, CYAN)
        cyan_wash.putalpha(18)
        room = Image.alpha_composite(room, cyan_wash)
    else:
        # Toxic settling haze and one-way descent.
        haze = Image.new("RGBA", room.size, (0, 0, 0, 0))
        hd = ImageDraw.Draw(haze)
        for band in range(10):
            y = 420 + band * 125
            hd.rectangle((0, y, WIDTH, y + 190), fill=(120, 32, 112, 12 + band * 2))
        haze = haze.filter(ImageFilter.GaussianBlur(32))
        room = Image.alpha_composite(room, haze)
        alpha_fill(room, NAVY, 78)
        arrow(
            ImageDraw.Draw(room, "RGBA"),
            [(140, 226), (330, 355), (1080, 490), (740, 650), (410, 770), (930, 1135), (1410, 1540)],
            ROSE,
            width=15,
            head=38,
        )

    room.thumbnail(panel_size, Image.Resampling.LANCZOS)
    return room


def state_study() -> Image.Image:
    canvas = Image.new("RGB", (1820, 1120), NAVY)
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (70, 48),
        "THE BREATHING CHAMBER // STATE STUDY",
        font=font(42, display=True),
        fill=INK,
    )
    draw.text(
        (72, 102),
        "ONE VOLUME // TWO EMOTIONAL AND MECHANICAL READINGS",
        font=font(19),
        fill=CYAN,
    )

    dormant = scaled_room_state(False, (790, 890))
    restored = scaled_room_state(True, (790, 890))
    left = (70, 164)
    right = (960, 164)
    canvas.paste(dormant.convert("RGB"), left)
    canvas.paste(restored.convert("RGB"), right)

    draw.rectangle((*left, left[0] + dormant.width, left[1] + dormant.height), outline=ROSE, width=5)
    draw.rectangle((*right, right[0] + restored.width, right[1] + restored.height), outline=CYAN, width=5)
    label(draw, (left[0] + 18, left[1] + 22), "DORMANT // COMMIT TO THE FALL", color=ROSE, size=19)
    label(draw, (right[0] + 18, right[1] + 22), "RESTORED // EARN THE ASCENT", color=CYAN, size=19)

    footer_y = 1070
    draw.text(
        (70, footer_y),
        "DROP → STABILIZE → WATCH THE ROOM BREATHE → RIDE → CLIMB → EXIT ABOVE",
        font=font(21),
        fill=GOLD,
        anchor="lm",
    )
    return canvas


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    traversal_path = OUTPUT / "breathing-chamber-traversal-approval-v1.png"
    state_path = OUTPUT / "breathing-chamber-state-study-v1.png"
    traversal_study().save(traversal_path, optimize=True)
    state_study().save(state_path, optimize=True)
    print(traversal_path)
    print(state_path)


if __name__ == "__main__":
    main()
