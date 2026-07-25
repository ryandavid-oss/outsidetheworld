#!/usr/bin/env python3
"""Build the consolidated Revision 3 morning approval sheet."""

from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PHASE = ROOT / "Design/Super-Frgmnts/Overworld/Phase-3"
OUTPUT_DIR = PHASE / "Morning-Review"
OUTPUT = OUTPUT_DIR / "revision-3-morning-approval-sheet-v1.png"

DRAS_SCALE = PHASE / "Dras/Reviews/dras-scale-study-v1.png"
DIALOGUE = PHASE / "Dialogue/Reviews/dialogue-directions-comparison-v1.png"
OUTPOST_MOBILE = PHASE / "Outpost/Reviews/outpost-mobile-sequence-v1.png"

FONT_PATH = "/System/Library/Fonts/SFNSMono.ttf"
FONT_BOLD_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

COLORS = {
    "void": (5, 6, 12, 255),
    "panel": (7, 12, 28, 255),
    "ink": (238, 238, 238, 255),
    "soft": (160, 190, 245, 255),
    "blue": (99, 149, 238, 255),
    "teal": (145, 175, 179, 255),
    "gold": (217, 192, 140, 255),
    "pink": (255, 105, 180, 255),
    "green": (75, 227, 110, 255),
    "amethyst": (155, 89, 182, 255),
}


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD_PATH if bold else FONT_PATH, size)


def label(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    *,
    size: int,
    fill: tuple[int, int, int, int] = COLORS["ink"],
    bold: bool = False,
) -> None:
    draw.text(xy, text, font=font(size, bold=bold), fill=fill)


def fit_inside(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    return image


def framed_art(
    canvas: Image.Image,
    path: Path,
    box: tuple[int, int, int, int],
    *,
    heading: str,
    status: str,
    accent: tuple[int, int, int, int],
) -> None:
    draw = ImageDraw.Draw(canvas)
    left, top, right, bottom = box
    draw.rounded_rectangle(
        box,
        radius=14,
        fill=COLORS["panel"],
        outline=accent,
        width=3,
    )
    label(draw, (left + 20, top + 16), heading, size=23, fill=accent, bold=True)
    label(draw, (left + 20, top + 52), status, size=13, fill=COLORS["soft"])
    target = (right - left - 40, bottom - top - 98)
    art = fit_inside(path, target)
    canvas.alpha_composite(
        art,
        (
            left + 20 + (target[0] - art.width) // 2,
            top + 82 + (target[1] - art.height) // 2,
        ),
    )


def wrapped_lines(text: str, width: int) -> list[str]:
    return textwrap.wrap(
        text,
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    )


def decision_card(
    draw: ImageDraw.ImageDraw,
    top: int,
    number: str,
    heading: str,
    body: str,
    accent: tuple[int, int, int, int],
) -> int:
    left, right = 932, 1754
    lines = wrapped_lines(body, 62)
    height = 112 + len(lines) * 26
    draw.rounded_rectangle(
        (left, top, right, top + height),
        radius=10,
        fill=COLORS["panel"],
        outline=accent,
        width=2,
    )
    draw.rounded_rectangle(
        (left + 18, top + 18, left + 78, top + 68),
        radius=5,
        fill=accent,
    )
    label(
        draw,
        (left + 33, top + 29),
        number,
        size=17,
        fill=COLORS["void"],
        bold=True,
    )
    label(draw, (left + 96, top + 20), heading, size=20, fill=accent, bold=True)
    for index, line in enumerate(lines):
        label(
            draw,
            (left + 96, top + 58 + index * 26),
            line,
            size=14,
            fill=COLORS["ink"],
        )
    return top + height + 18


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGBA", (1800, 1980), COLORS["void"])
    draw = ImageDraw.Draw(canvas)
    label(draw, (46, 28), "SUPER FRGMNTS // REVISION 3 MORNING REVIEW", size=35, bold=True)
    label(
        draw,
        (48, 78),
        "Quality pass: identity, scale, dialogue, camera, input, and Outpost story rhythm",
        size=17,
        fill=COLORS["soft"],
    )
    draw.rounded_rectangle(
        (1392, 26, 1754, 84),
        radius=6,
        fill=(255, 105, 180, 30),
        outline=COLORS["pink"],
        width=2,
    )
    label(
        draw,
        (1430, 44),
        "LOCAL • UNCOMMITTED",
        size=16,
        fill=COLORS["void"],
        bold=True,
    )

    framed_art(
        canvas,
        DRAS_SCALE,
        (46, 122, 890, 700),
        heading="3B // DRAS EHDRE",
        status="Recommendation: 104px visible silhouette",
        accent=COLORS["gold"],
    )
    framed_art(
        canvas,
        DIALOGUE,
        (914, 122, 1754, 700),
        heading="3C // DIALOGUE LANGUAGE",
        status="Field Relay for people • Archive for machines",
        accent=COLORS["teal"],
    )
    framed_art(
        canvas,
        OUTPOST_MOBILE,
        (46, 728, 890, 1888),
        heading="3D // OUTPOST FLOW",
        status="Approach → conversation → release, including portrait mobile",
        accent=COLORS["blue"],
    )

    label(draw, (932, 736), "MORNING DECISIONS", size=25, bold=True)
    label(
        draw,
        (934, 774),
        "Recommended defaults are explicit; nothing below is canon yet.",
        size=14,
        fill=COLORS["soft"],
    )
    top = 816
    top = decision_card(
        draw,
        top,
        "01",
        "DRAS MASTER & SCALE",
        "Approve the extracted identity and 104px human-scale runtime candidate.",
        COLORS["gold"],
    )
    top = decision_card(
        draw,
        top,
        "02",
        "FIELD RELAY",
        "Approve Field Relay for living character conversations and first contact.",
        COLORS["teal"],
    )
    top = decision_card(
        draw,
        top,
        "03",
        "COREWORKS ARCHIVE",
        "Approve the alternate visual grammar for terminals, logs, and system alerts.",
        COLORS["amethyst"],
    )
    top = decision_card(
        draw,
        top,
        "04",
        "FIRST-CONTACT FLOW",
        "Approve automatic first meeting, manual return visits, and non-solid Dras.",
        COLORS["blue"],
    )
    top = decision_card(
        draw,
        top,
        "05",
        "MOBILE CONVERSATION",
        "Approve paused gameplay, hidden controls, and the actor-safe camera settle.",
        COLORS["green"],
    )
    top = decision_card(
        draw,
        top,
        "06",
        "WORKING COPY",
        "Review the six sample cards separately; they remain editable and non-canon.",
        COLORS["pink"],
    )

    draw.line((46, 1924, 1754, 1924), fill=COLORS["teal"], width=2)
    label(
        draw,
        (48, 1942),
        "Live game untouched • no deployment • no commit • final camp and terminal art deferred",
        size=15,
        fill=COLORS["soft"],
    )
    canvas.convert("RGB").save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
