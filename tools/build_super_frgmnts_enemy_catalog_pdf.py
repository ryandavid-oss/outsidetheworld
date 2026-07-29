#!/usr/bin/env python3
"""Build the render-verified SUPER FRGMNTS enemy measurement catalog."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/pdf/super-frgmnts-enemy-catalog.pdf"
PAGE_WIDTH, PAGE_HEIGHT = landscape(letter)

NAVY = HexColor("#050814")
PANEL = HexColor("#0d1426")
PANEL_ALT = HexColor("#111b31")
LINE = HexColor("#31415f")
CYAN = HexColor("#58f5df")
PINK = HexColor("#ff69b4")
GOLD = HexColor("#ffd36c")
CREAM = HexColor("#f5ecd8")
MUTED = HexColor("#9aabc7")
WHITE = HexColor("#ffffff")


@dataclass(frozen=True)
class Enemy:
    runtime_type: str
    name: str
    role: str
    hp: int
    footprint: str
    render_size: str
    frame_atlas: tuple[str, ...]
    asset: str
    frame_width: int
    frame_height: int


ENEMIES = (
    Enemy(
        "crawler",
        "Ridge Skitter",
        "Fast ground crawler",
        1,
        "94 x 66",
        "94 x 66",
        ("64 x 64 frame", "64 x 64 static asset"),
        "Images/Game/enemy-crawler-ridge-skitter.png",
        64,
        64,
    ),
    Enemy(
        "walker",
        "Clacker Beetle",
        "Ground patrol",
        1,
        "82 x 82",
        "82 x 82",
        ("64 x 64 frame", "64 x 64 static asset"),
        "Images/Game/enemy-walker-clacker-beetle.png",
        64,
        64,
    ),
    Enemy(
        "flyer",
        "Spore Wisp",
        "Legacy airborne hazard",
        1,
        "88 x 88",
        "88 x 88",
        ("64 x 64 frame", "64 x 64 static asset"),
        "Images/Game/enemy-flyer-spore-wisp.png",
        64,
        64,
    ),
    Enemy(
        "squircle",
        "Squircle Minion",
        "Surface-crawling platform enemy",
        1,
        "58 x 46",
        "96 x 80",
        ("96 x 80 frame", "864 x 320 atlas - 36 frames"),
        "Images/Game/enemy-squircle-minion-standard-blue-sheet.png",
        96,
        80,
    ),
    Enemy(
        "mite",
        "Vesper Mite",
        "Ground-traveling scuttler; does not fly",
        1,
        "86 x 76",
        "100 x 122",
        ("106 x 130 frame", "636 x 780 atlas - 36 frames"),
        "Images/Game/Super-Frgmnts/enemy-vesper-mite-ground-gait-sheet-v2.png",
        106,
        130,
    ),
    Enemy(
        "wasp",
        "Ember Wasp",
        "Fast flying insect",
        1,
        "96 x 74",
        "112 x 86",
        ("112 x 86 frame", "672 x 516 atlas - 36 frames"),
        "Images/Game/Super-Frgmnts/enemy-flying-wasp-flight-sheet-v1.png",
        112,
        86,
    ),
    Enemy(
        "gaunt",
        "Seam Hunter",
        "Tall melee stalker",
        4,
        "88 x 128",
        "144 x 144 walk",
        (
            "Walk: 128 x 128 / 768 x 768 - 36",
            "Attack: 160 x 128 / 800 x 640 - 25",
        ),
        "Images/Game/Super-Frgmnts/enemy-tall-gaunt-alien-walk-sheet-v1.png",
        128,
        128,
    ),
    Enemy(
        "patroller",
        "Chitin Sentinel",
        "Armored ground patrol",
        5,
        "82 x 98",
        "136 x 126",
        (
            "114 x 106 frame",
            "684 x 636 patrol/death - 36 each",
        ),
        "Images/Game/Super-Frgmnts/enemy-chitin-sentinel-patrol-sheet-v1.png",
        114,
        106,
    ),
    Enemy(
        "fragmentSpring",
        "Spring Fragment",
        "Small fast airborne Fragment",
        1,
        "60 x 44",
        "68 x 48",
        ("80 x 57 frame", "400 x 285 atlas - 25 frames"),
        "Images/Game/Super-Frgmnts/enemy-fragment-spring-green-runtime-v1.png",
        80,
        57,
    ),
    Enemy(
        "fragmentBastion",
        "Bastion Fragment",
        "Heavy Fragment with spike-armor cycle",
        2,
        "66 x 58",
        "72 x 63",
        ("80 x 70 frame", "480 x 420 atlas - 36 frames"),
        "Images/Game/Super-Frgmnts/enemy-fragment-bastion-purple-runtime-v1.png",
        80,
        70,
    ),
    Enemy(
        "coreLeech",
        "Core Leech",
        "Hovering parasite",
        2,
        "78 x 96",
        "122 x 122",
        ("112 x 112 frame", "672 x 672 atlas - 36 frames"),
        "Images/Game/Super-Frgmnts/enemy-core-leech-hover-sheet-v1.png",
        112,
        112,
    ),
    Enemy(
        "vesperFlare",
        "Vesper Flare",
        "Fast thermal flyer",
        2,
        "82 x 86",
        "116 x 116",
        ("112 x 112 frame", "672 x 672 atlas - 36 frames"),
        "Images/Game/Super-Frgmnts/enemy-vesper-flare-hover-sheet-v1.png",
        112,
        112,
    ),
    Enemy(
        "paleWatcher",
        "Pale Watcher",
        "Uplink ground guard",
        3,
        "66 x 110",
        "120 x 120",
        ("112 x 112 frame", "672 x 672 atlas - 36 frames"),
        "Images/Game/Super-Frgmnts/enemy-pale-watcher-stalk-sheet-v1.png",
        112,
        112,
    ),
)


def wrap_text(text: str, font: str, size: float, width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if stringWidth(candidate, font, size) <= width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(
    pdf: canvas.Canvas,
    lines: list[str] | tuple[str, ...],
    x: float,
    top_y: float,
    font: str,
    size: float,
    color,
    leading: float,
    max_lines: int | None = None,
) -> None:
    pdf.setFont(font, size)
    pdf.setFillColor(color)
    visible = lines if max_lines is None else lines[:max_lines]
    for index, line in enumerate(visible):
        pdf.drawString(x, top_y - index * leading, line)


def first_frame_reader(enemy: Enemy) -> ImageReader:
    image = Image.open(ROOT / enemy.asset).convert("RGBA")
    frame = image.crop((0, 0, enemy.frame_width, enemy.frame_height))
    bounds = frame.getbbox()
    if bounds:
        frame = frame.crop(bounds)
    buffer = BytesIO()
    frame.save(buffer, format="PNG")
    buffer.seek(0)
    return ImageReader(buffer)


def aryn_reader() -> ImageReader:
    image = Image.open(
        ROOT / "Images/Game/Super-Frgmnts/aryn-command-rest-runtime-v1.png"
    ).convert("RGBA")
    bounds = image.getbbox()
    if bounds:
        image = image.crop(bounds)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return ImageReader(buffer)


def draw_pixel_border(
    pdf: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    color=LINE,
    line_width: float = 1,
) -> None:
    pdf.setStrokeColor(color)
    pdf.setLineWidth(line_width)
    pdf.rect(x, y, width, height, stroke=1, fill=0)
    corner = 6
    pdf.setFillColor(color)
    pdf.rect(x, y + height - corner, corner, corner, stroke=0, fill=1)
    pdf.rect(x + width - corner, y, corner, corner, stroke=0, fill=1)


def draw_header(pdf: canvas.Canvas, section: str, page_number: int) -> None:
    pdf.setFillColor(NAVY)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    pdf.setFillColor(CYAN)
    pdf.rect(0, PAGE_HEIGHT - 6, PAGE_WIDTH, 6, stroke=0, fill=1)
    pdf.setFont("Courier-Bold", 9)
    pdf.setFillColor(MUTED)
    pdf.drawString(32, PAGE_HEIGHT - 28, "SUPER FRGMNTS // SEASON ONE: VEYRA")
    pdf.setFillColor(GOLD)
    pdf.drawRightString(PAGE_WIDTH - 32, PAGE_HEIGHT - 28, section)
    pdf.setStrokeColor(LINE)
    pdf.line(32, PAGE_HEIGHT - 38, PAGE_WIDTH - 32, PAGE_HEIGHT - 38)
    pdf.setFillColor(MUTED)
    pdf.setFont("Courier", 8)
    pdf.drawString(32, 18, "Current Episode 01 beta runtime // measurements in pixels")
    pdf.drawRightString(PAGE_WIDTH - 32, 18, f"PAGE {page_number}")


def draw_aryn_reference(pdf: canvas.Canvas) -> None:
    x, y, width, height = 38, 242, 348, 220
    pdf.setFillColor(PANEL)
    pdf.rect(x, y, width, height, stroke=0, fill=1)
    draw_pixel_border(pdf, x, y, width, height, CYAN, 1.2)
    pdf.setFillColor(CYAN)
    pdf.setFont("Courier-Bold", 10)
    pdf.drawString(x + 18, y + height - 24, "SCALE REFERENCE // NOT AN ENEMY")
    pdf.setFillColor(CREAM)
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(x + 18, y + height - 54, "Aryn Sol-Mavi")

    image_box_x = x + 18
    image_box_y = y + 44
    image_box_size = 112
    pdf.setFillColor(PANEL_ALT)
    pdf.rect(
        image_box_x,
        image_box_y,
        image_box_size,
        image_box_size,
        stroke=0,
        fill=1,
    )
    draw_pixel_border(
        pdf,
        image_box_x,
        image_box_y,
        image_box_size,
        image_box_size,
        LINE,
    )
    pdf.drawImage(
        aryn_reader(),
        image_box_x + 6,
        image_box_y + 6,
        width=image_box_size - 12,
        height=image_box_size - 12,
        preserveAspectRatio=True,
        anchor="c",
        mask="auto",
    )

    metric_x = x + 150
    metric_y = y + 139
    metrics = (
        ("Sprite frame", "112 x 112"),
        ("Runtime render", "112 x 112"),
        ("Combat body", "48 x 82"),
        ("Platform foot width", "44"),
        ("Run atlas", "896 x 112 / 8 frames"),
    )
    for label, value in metrics:
        pdf.setFont("Courier-Bold", 8)
        pdf.setFillColor(MUTED)
        pdf.drawString(metric_x, metric_y, label.upper())
        pdf.setFont("Helvetica-Bold", 11)
        pdf.setFillColor(CREAM)
        pdf.drawString(metric_x, metric_y - 14, value)
        metric_y -= 29


def draw_cover(pdf: canvas.Canvas) -> None:
    draw_header(pdf, "ENEMY CATALOG", 1)
    pdf.setFont("Helvetica-Bold", 31)
    pdf.setFillColor(WHITE)
    pdf.drawString(38, PAGE_HEIGHT - 92, "Enemy Sprite & Vitality Catalog")
    pdf.setFont("Courier-Bold", 11)
    pdf.setFillColor(PINK)
    pdf.drawString(40, PAGE_HEIGHT - 116, "13 RUNTIME FAMILIES // CURRENT EARLY-BETA VALUES")
    pdf.setFont("Helvetica", 10)
    pdf.setFillColor(MUTED)
    intro = (
        "A production reference for enemy names, hit points, gameplay "
        "footprints, rendered sprite sizes, and shipping frame/atlas dimensions."
    )
    draw_lines(
        pdf,
        wrap_text(intro, "Helvetica", 10, 700),
        40,
        PAGE_HEIGHT - 140,
        "Helvetica",
        10,
        MUTED,
        14,
    )

    draw_aryn_reference(pdf)

    roster_x, roster_y, roster_w, roster_h = 406, 242, 348, 220
    pdf.setFillColor(PANEL)
    pdf.rect(roster_x, roster_y, roster_w, roster_h, stroke=0, fill=1)
    draw_pixel_border(pdf, roster_x, roster_y, roster_w, roster_h, PINK, 1.2)
    pdf.setFont("Courier-Bold", 10)
    pdf.setFillColor(PINK)
    pdf.drawString(roster_x + 18, roster_y + roster_h - 24, "EPISODE 01 ROSTER")
    for index, enemy in enumerate(ENEMIES):
        column = 0 if index < 7 else 1
        row = index if index < 7 else index - 7
        entry_x = roster_x + 18 + column * 168
        entry_y = roster_y + roster_h - 52 - row * 24
        pdf.setFont("Courier-Bold", 8)
        pdf.setFillColor(GOLD)
        pdf.drawString(entry_x, entry_y, f"{index + 1:02d}")
        pdf.setFillColor(CREAM)
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(entry_x + 22, entry_y, enemy.name)
        pdf.setFillColor(MUTED)
        pdf.setFont("Courier", 7)
        pdf.drawRightString(entry_x + 157, entry_y, f"{enemy.hp} HP")

    key_x, key_y, key_w, key_h = 38, 70, 716, 160
    pdf.setFillColor(PANEL_ALT)
    pdf.rect(key_x, key_y, key_w, key_h, stroke=0, fill=1)
    draw_pixel_border(pdf, key_x, key_y, key_w, key_h, LINE)
    pdf.setFont("Courier-Bold", 10)
    pdf.setFillColor(GOLD)
    pdf.drawString(key_x + 18, key_y + key_h - 24, "HOW TO READ THE MEASUREMENTS")
    notes = (
        (
            "Gameplay footprint",
            "The enemy.width x enemy.height values used by the current runtime for positioning and contact checks.",
        ),
        (
            "Runtime render",
            "The width x height actually drawn to the game canvas. Transparent frame padding may make visible art smaller.",
        ),
        (
            "Frame / atlas",
            "The shipping frame cell followed by the complete asset dimensions and frame count.",
        ),
        (
            "Hit points",
            "Current enemy health values. Weapon ammo, damage, boss durability, and final combat balance remain open.",
        ),
    )
    for index, (label, copy) in enumerate(notes):
        column = index % 2
        row = index // 2
        note_x = key_x + 18 + column * 350
        note_y = key_y + key_h - 52 - row * 53
        pdf.setFont("Helvetica-Bold", 9)
        pdf.setFillColor(CYAN if column == 0 else PINK)
        pdf.drawString(note_x, note_y, label)
        lines = wrap_text(copy, "Helvetica", 8, 320)
        draw_lines(pdf, lines, note_x, note_y - 13, "Helvetica", 8, MUTED, 10, 3)


def draw_table_header(pdf: canvas.Canvas, y: float) -> None:
    columns = (
        (32, 58, "SPRITE"),
        (90, 120, "NAME / TYPE"),
        (210, 32, "HP"),
        (242, 74, "FOOTPRINT"),
        (316, 82, "RENDER"),
        (398, 166, "FRAME / ATLAS"),
        (564, 196, "ROLE"),
    )
    pdf.setFillColor(PANEL_ALT)
    pdf.rect(32, y - 24, 728, 24, stroke=0, fill=1)
    for x, _, label in columns:
        pdf.setFillColor(GOLD)
        pdf.setFont("Courier-Bold", 7.5)
        pdf.drawString(x + 7, y - 16, label)
    pdf.setStrokeColor(LINE)
    pdf.line(32, y - 24, 760, y - 24)


def draw_enemy_row(pdf: canvas.Canvas, enemy: Enemy, index: int, y: float) -> None:
    row_height = 62
    pdf.setFillColor(PANEL if index % 2 == 0 else NAVY)
    pdf.rect(32, y - row_height, 728, row_height, stroke=0, fill=1)
    pdf.setStrokeColor(LINE)
    pdf.line(32, y - row_height, 760, y - row_height)

    thumb_x, thumb_y, thumb_size = 38, y - 55, 48
    pdf.setFillColor(PANEL_ALT)
    pdf.rect(thumb_x, thumb_y, thumb_size, thumb_size, stroke=0, fill=1)
    pdf.drawImage(
        first_frame_reader(enemy),
        thumb_x + 3,
        thumb_y + 3,
        width=thumb_size - 6,
        height=thumb_size - 6,
        preserveAspectRatio=True,
        anchor="c",
        mask="auto",
    )

    pdf.setFont("Helvetica-Bold", 9.5)
    pdf.setFillColor(CREAM)
    pdf.drawString(97, y - 20, enemy.name)
    pdf.setFont("Courier", 7)
    pdf.setFillColor(MUTED)
    pdf.drawString(97, y - 35, enemy.runtime_type)

    pdf.setFont("Helvetica-Bold", 15)
    pdf.setFillColor(PINK if enemy.hp > 1 else CYAN)
    pdf.drawCentredString(226, y - 30, str(enemy.hp))

    for x, value in ((249, enemy.footprint), (323, enemy.render_size)):
        pdf.setFont("Courier-Bold", 8)
        pdf.setFillColor(CREAM)
        lines = value.split(" ")
        if len(value) <= 13:
            pdf.drawString(x, y - 28, value)
        else:
            draw_lines(
                pdf,
                wrap_text(value, "Courier-Bold", 8, 68),
                x,
                y - 20,
                "Courier-Bold",
                8,
                CREAM,
                11,
                3,
            )

    draw_lines(
        pdf,
        enemy.frame_atlas,
        405,
        y - 19,
        "Courier",
        6.8,
        CREAM,
        11,
        3,
    )
    role_lines = wrap_text(enemy.role, "Helvetica", 8.2, 182)
    draw_lines(
        pdf,
        role_lines,
        571,
        y - 19,
        "Helvetica",
        8.2,
        MUTED,
        11,
        3,
    )


def draw_catalog_page(
    pdf: canvas.Canvas,
    enemies: tuple[Enemy, ...],
    page_number: int,
    range_label: str,
) -> None:
    draw_header(pdf, range_label, page_number)
    pdf.setFont("Helvetica-Bold", 22)
    pdf.setFillColor(WHITE)
    pdf.drawString(32, PAGE_HEIGHT - 72, "Runtime Enemy Specifications")
    pdf.setFont("Courier", 8)
    pdf.setFillColor(MUTED)
    pdf.drawRightString(
        PAGE_WIDTH - 32,
        PAGE_HEIGHT - 70,
        "FOOTPRINT / RENDER / FRAME / ATLAS",
    )
    table_y = PAGE_HEIGHT - 92
    draw_table_header(pdf, table_y)
    row_y = table_y - 24
    for index, enemy in enumerate(enemies):
        draw_enemy_row(pdf, enemy, index, row_y - index * 62)


def build_pdf() -> Path:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT), pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    pdf.setTitle("SUPER FRGMNTS Enemy Sprite and Vitality Catalog")
    pdf.setSubject(
        "Episode 01 enemy names, hit points, and runtime sprite measurements"
    )
    pdf.setAuthor("Outside the World")

    draw_cover(pdf)
    pdf.showPage()
    draw_catalog_page(pdf, ENEMIES[:7], 2, "ROSTER 01-07")
    pdf.showPage()
    draw_catalog_page(pdf, ENEMIES[7:], 3, "ROSTER 08-13")
    pdf.save()
    return OUTPUT


if __name__ == "__main__":
    output = build_pdf()
    print(output)
