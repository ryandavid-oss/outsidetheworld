#!/usr/bin/env python3
"""Build the SUPER FRGMNTS Arrival on Veyra player's field manual."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/pdf/super-frgmnts-arrival-on-veyra-player-guide.pdf"
PAGE_WIDTH = 8.5 * inch
PAGE_HEIGHT = 5.5 * inch
BOX_ART_CANDIDATES = (
    Path("/Users/rylee/.codex/attachments/37359f9a-bd29-4878-abfd-b229ee733041/codex-clipboard-e3337003-f69b-411d-a152-5a4065f36aec.png"),
    Path("/Users/rylee/Downloads/Box_Art.png"),
)

VOID = HexColor("#050713")
NAVY = HexColor("#0a1020")
PANEL = HexColor("#101a30")
PANEL_ALT = HexColor("#17243d")
CYAN = HexColor("#58f5df")
PINK = HexColor("#ff69b4")
GREEN = HexColor("#6bff38")
GOLD = HexColor("#ffd36c")
ORANGE = HexColor("#ff6b35")
CREAM = HexColor("#f7f0ea")
MUTED = HexColor("#9fb1cc")
LINE = HexColor("#334563")
RED = HexColor("#ff5268")
WHITE = HexColor("#ffffff")


def root_path(relative: str) -> Path:
    return ROOT / relative


def wrap_text(text: str, font: str, size: float, width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if not current or stringWidth(candidate, font, size) <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(
    pdf: canvas.Canvas,
    text: str,
    x: float,
    top_y: float,
    width: float,
    font: str = "Helvetica",
    size: float = 9,
    color=CREAM,
    leading: float | None = None,
    max_lines: int | None = None,
) -> float:
    line_height = leading or size * 1.35
    lines = wrap_text(text, font, size, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    pdf.setFont(font, size)
    pdf.setFillColor(color)
    for index, line in enumerate(lines):
        pdf.drawString(x, top_y - index * line_height, line)
    return top_y - len(lines) * line_height


def image_reader(
    relative: str,
    crop: tuple[int, int, int, int] | None = None,
    trim_alpha: bool = False,
) -> tuple[ImageReader, int, int]:
    image = Image.open(root_path(relative)).convert("RGBA")
    if crop is not None:
        image = image.crop(crop)
    if trim_alpha:
        bounds = image.getbbox()
        if bounds:
            image = image.crop(bounds)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return ImageReader(buffer), image.width, image.height


def external_image_reader(path: Path) -> tuple[ImageReader, int, int]:
    image = Image.open(path).convert("RGB")
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=92)
    buffer.seek(0)
    return ImageReader(buffer), image.width, image.height


def draw_external_contain(
    pdf: canvas.Canvas,
    path: Path,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    reader, image_width, image_height = external_image_reader(path)
    scale = min(width / image_width, height / image_height)
    draw_width = image_width * scale
    draw_height = image_height * scale
    pdf.drawImage(
        reader,
        x + (width - draw_width) / 2,
        y + (height - draw_height) / 2,
        draw_width,
        draw_height,
    )


def crop_reader_to_aspect(
    relative: str,
    target_aspect: float,
) -> tuple[ImageReader, int, int]:
    image = Image.open(root_path(relative)).convert("RGB")
    source_aspect = image.width / image.height
    if source_aspect > target_aspect:
        crop_width = round(image.height * target_aspect)
        left = (image.width - crop_width) // 2
        image = image.crop((left, 0, left + crop_width, image.height))
    elif source_aspect < target_aspect:
        crop_height = round(image.width / target_aspect)
        top = (image.height - crop_height) // 2
        image = image.crop((0, top, image.width, top + crop_height))
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=92)
    buffer.seek(0)
    return ImageReader(buffer), image.width, image.height


def draw_image_cover(
    pdf: canvas.Canvas,
    relative: str,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    reader, _, _ = crop_reader_to_aspect(relative, width / height)
    pdf.drawImage(reader, x, y, width, height, mask="auto")


def draw_image_contain(
    pdf: canvas.Canvas,
    relative: str,
    x: float,
    y: float,
    width: float,
    height: float,
    crop: tuple[int, int, int, int] | None = None,
    trim_alpha: bool = False,
) -> None:
    reader, image_width, image_height = image_reader(
        relative, crop=crop, trim_alpha=trim_alpha
    )
    scale = min(width / image_width, height / image_height)
    draw_width = image_width * scale
    draw_height = image_height * scale
    pdf.drawImage(
        reader,
        x + (width - draw_width) / 2,
        y + (height - draw_height) / 2,
        draw_width,
        draw_height,
        mask="auto",
    )


def fill_alpha(pdf: canvas.Canvas, color, alpha: float) -> None:
    pdf.saveState()
    pdf.setFillColor(color)
    pdf.setFillAlpha(alpha)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    pdf.restoreState()


def pixel_border(
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
    notch = 5
    pdf.setFillColor(color)
    pdf.rect(x, y + height - notch, notch, notch, stroke=0, fill=1)
    pdf.rect(x + width - notch, y, notch, notch, stroke=0, fill=1)


def panel(
    pdf: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    fill=PANEL,
    border=LINE,
) -> None:
    pdf.setFillColor(fill)
    pdf.rect(x, y, width, height, stroke=0, fill=1)
    pixel_border(pdf, x, y, width, height, border, 1)


def section_header(
    pdf: canvas.Canvas,
    section: str,
    title: str,
    page_number: int,
) -> None:
    pdf.setFillColor(VOID)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    pdf.setFillColor(CYAN)
    pdf.rect(0, PAGE_HEIGHT - 6, PAGE_WIDTH, 6, stroke=0, fill=1)
    pdf.setFont("Courier-Bold", 7.5)
    pdf.setFillColor(MUTED)
    pdf.drawString(28, PAGE_HEIGHT - 24, "SUPER FRGMNTS // FIELD MANUAL 01")
    pdf.setFillColor(GOLD)
    pdf.drawRightString(PAGE_WIDTH - 28, PAGE_HEIGHT - 24, section.upper())
    pdf.setStrokeColor(LINE)
    pdf.line(28, PAGE_HEIGHT - 31, PAGE_WIDTH - 28, PAGE_HEIGHT - 31)
    pdf.setFillColor(CREAM)
    pdf.setFont("Helvetica-Bold", 23)
    pdf.drawString(28, PAGE_HEIGHT - 60, title)
    pdf.setFont("Courier", 7)
    pdf.setFillColor(MUTED)
    pdf.drawString(28, 13, "ARRIVAL ON VEYRA // PS4 CONTROLLER + TOUCH")
    pdf.drawRightString(PAGE_WIDTH - 28, 13, f"{page_number:02d}")


def bullet(
    pdf: canvas.Canvas,
    label: str,
    body: str,
    x: float,
    top_y: float,
    width: float,
    color=CYAN,
) -> float:
    pdf.setFillColor(color)
    pdf.rect(x, top_y - 5, 5, 5, stroke=0, fill=1)
    pdf.setFont("Courier-Bold", 8)
    pdf.drawString(x + 10, top_y, label.upper())
    return draw_wrapped(
        pdf,
        body,
        x + 10,
        top_y - 13,
        width - 10,
        size=8,
        color=MUTED,
        leading=10.3,
    ) - 6


def control_row(
    pdf: canvas.Canvas,
    button: str,
    action: str,
    detail: str,
    x: float,
    top_y: float,
    width: float,
    accent=CYAN,
) -> None:
    panel(pdf, x, top_y - 43, width, 39, fill=PANEL_ALT, border=LINE)
    pdf.setFillColor(accent)
    pdf.roundRect(x + 8, top_y - 34, 74, 22, 4, stroke=0, fill=1)
    pdf.setFont("Courier-Bold", 7.6)
    pdf.setFillColor(VOID)
    pdf.drawCentredString(x + 45, top_y - 26, button)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.setFillColor(CREAM)
    pdf.drawString(x + 90, top_y - 20, action)
    draw_wrapped(
        pdf,
        detail,
        x + 90,
        top_y - 32,
        width - 99,
        size=6.8,
        color=MUTED,
        leading=8,
        max_lines=1,
    )


def draw_cover(pdf: canvas.Canvas) -> None:
    pdf.setFillColor(HexColor("#000000"))
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    box_art = next((path for path in BOX_ART_CANDIDATES if path.exists()), None)
    if box_art is None:
        raise FileNotFoundError("SUPER FRGMNTS box art was not found")
    draw_external_contain(pdf, box_art, 40, 0, PAGE_WIDTH - 80, PAGE_HEIGHT)
    pdf.setFillColor(CYAN)
    pdf.rect(0, 0, 25, PAGE_HEIGHT, stroke=0, fill=1)
    pdf.setFillColor(PINK)
    pdf.rect(PAGE_WIDTH - 25, 0, 25, PAGE_HEIGHT, stroke=0, fill=1)
    pdf.saveState()
    pdf.translate(15, PAGE_HEIGHT / 2)
    pdf.rotate(90)
    pdf.setFillColor(VOID)
    pdf.setFont("Courier-Bold", 8)
    pdf.drawCentredString(0, -2, "PLAYER'S FIELD MANUAL // ARRIVAL ON VEYRA")
    pdf.restoreState()
    pdf.saveState()
    pdf.translate(PAGE_WIDTH - 15, PAGE_HEIGHT / 2)
    pdf.rotate(-90)
    pdf.setFillColor(VOID)
    pdf.setFont("Courier-Bold", 8)
    pdf.drawCentredString(0, -2, "PS4 CONTROLLER + TOUCH // FIELD MANUAL 01")
    pdf.restoreState()
    pdf.showPage()


def draw_welcome(pdf: canvas.Canvas) -> None:
    section_header(pdf, "Briefing", "Welcome to Veyra", 2)
    panel(pdf, 28, 42, 283, 272, fill=PANEL, border=CYAN)
    pdf.setFont("Courier-Bold", 8)
    pdf.setFillColor(PINK)
    pdf.drawString(44, 294, "DISTRESS SIGNAL // VERIFIED")
    y = draw_wrapped(
        pdf,
        "The Veyra Coreworks are poisoned, the atmospheric stabilizers are offline, and something is moving through the Vesperite seams.",
        44,
        274,
        248,
        font="Helvetica-Bold",
        size=10,
        color=CREAM,
        leading=13,
    ) - 10
    for number, objective in enumerate(
        (
            "Locate Dras Ehdre on the surface.",
            "Prepare Aryn's PACK aboard the RD-42.",
            "Restore both atmospheric stabilizers.",
            "Recover all 12 Vesperite Fragments.",
            "Trace the pulse to its source.",
        ),
        start=1,
    ):
        pdf.setFillColor(GOLD)
        pdf.setFont("Courier-Bold", 8)
        pdf.drawString(44, y, f"0{number}")
        y = draw_wrapped(
            pdf,
            objective,
            68,
            y,
            220,
            size=8.4,
            color=MUTED,
            leading=10,
        ) - 5
    draw_image_cover(
        pdf,
        "media/narrative/2026-08-03-level-one/posters/super-frgmnts-rd42-descent-v1.jpg",
        327,
        106,
        257,
        208,
    )
    pixel_border(pdf, 327, 106, 257, 208, GOLD, 1.4)
    panel(pdf, 327, 42, 257, 52, fill=PANEL_ALT, border=LINE)
    pdf.setFont("Courier-Bold", 8)
    pdf.setFillColor(CYAN)
    pdf.drawString(341, 77, "QUICK START")
    draw_wrapped(
        pdf,
        "Connect the controller, press Cross to load if asked, choose a mode, and press Cross to start.",
        341,
        62,
        228,
        size=7.5,
        color=MUTED,
        leading=9,
    )
    pdf.showPage()


def draw_personnel(pdf: canvas.Canvas) -> None:
    section_header(pdf, "Personnel", "Who Answered the Signal", 3)
    cards = (
        (
            28,
            "ARYN SOL-MAVI",
            "SIGNAL RANGER",
            "Images/Game/Super-Frgmnts/aryn-dialogue-portrait-runtime-v3.png",
            "Independent, capable, and on Veyra without Fleet authorization. Her PACK begins with a guided base beam and grows through field-built modules.",
            CYAN,
        ),
        (
            320,
            "DRAS EHDRE",
            "COREWORKS FOREMAN",
            "Images/Game/Super-Frgmnts/dras-dialogue-portrait-runtime-v2.png",
            "The last foreman watching the abandoned Coreworks. Return to Dras after major discoveries; he keeps the portal working and the bad news organized.",
            GOLD,
        ),
    )
    for x, name, role, asset, description, accent in cards:
        panel(pdf, x, 68, 264, 246, fill=PANEL, border=accent)
        draw_image_contain(pdf, asset, x + 8, 150, 112, 154)
        pdf.setFont("Helvetica-Bold", 15)
        pdf.setFillColor(CREAM)
        pdf.drawString(x + 126, 285, name)
        pdf.setFont("Courier-Bold", 7)
        pdf.setFillColor(accent)
        pdf.drawString(x + 126, 267, role)
        draw_wrapped(
            pdf,
            description,
            x + 126,
            247,
            122,
            size=7.6,
            color=MUTED,
            leading=9.3,
        )
        pdf.setStrokeColor(LINE)
        pdf.line(x + 14, 137, x + 250, 137)
        if name.startswith("ARYN"):
            note = "COMMAND: Talk with Down. Use the RD-42 as Aryn's workshop."
        else:
            note = "FIELD NOTE: If Dras looks worried, the next assignment is probably underground."
        draw_wrapped(
            pdf,
            note,
            x + 16,
            119,
            232,
            font="Courier-Bold",
            size=7,
            color=CREAM,
            leading=9,
        )
    pdf.showPage()


def draw_controller(pdf: canvas.Canvas) -> None:
    section_header(pdf, "Controls", "DualShock 4 Layout", 4)
    pdf.setFont("Courier", 7.2)
    pdf.setFillColor(MUTED)
    pdf.drawString(29, 320, "The browser recognizes the PS4 controller automatically after input.")
    left_x, right_x = 28, 312
    width = 272
    rows_left = (
        ("L-STICK / D-PAD", "MOVE", "Walk, run, and select menu items.", CYAN),
        ("DOWN", "INTERACT / DROP", "Talk, enter, recover, activate, or descend.", GOLD),
        ("CROSS", "JUMP / CONFIRM", "Hold for height; press again after Jet Assist.", CYAN),
        ("SQUARE / R1 / R2", "FIRE", "Tap or hold according to the active PACK.", PINK),
    )
    rows_right = (
        ("TRIANGLE", "PACK", "Open configuration; change mode on title.", GREEN),
        ("OPTIONS", "PAUSE / RESUME", "Freeze the action or resume immediately.", GOLD),
        ("CIRCLE", "BACK", "Back out of menus; opens dialogue skip menu.", RED),
        ("CROSS", "TOGGLE", "Enable or disable the highlighted PACK module.", CYAN),
    )
    for index, row in enumerate(rows_left):
        control_row(pdf, *row[:3], left_x, 302 - index * 56, width, accent=row[3])
    for index, row in enumerate(rows_right):
        control_row(pdf, *row[:3], right_x, 302 - index * 56, width, accent=row[3])
    panel(pdf, 28, 42, 556, 32, fill=PANEL_ALT, border=PINK)
    pdf.setFont("Courier-Bold", 7.6)
    pdf.setFillColor(PINK)
    pdf.drawString(41, 61, "MENU LEGEND")
    pdf.setFont("Courier", 7)
    pdf.setFillColor(CREAM)
    pdf.drawString(126, 61, "D-PAD SELECTS // CROSS CONFIRMS // CIRCLE BACKS OUT // OPTIONS RESUMES")
    pdf.showPage()


def draw_touch(pdf: canvas.Canvas) -> None:
    section_header(pdf, "Controls", "Touch Play", 5)
    screen_x, screen_y, screen_w, screen_h = 28, 111, 556, 203
    draw_image_cover(
        pdf,
        "media/narrative/2026-08-03-level-one/posters/super-frgmnts-foundry-action-v1.jpg",
        screen_x,
        screen_y,
        screen_w,
        screen_h,
    )
    pixel_border(pdf, screen_x, screen_y, screen_w, screen_h, CYAN, 1.4)
    pdf.saveState()
    pdf.setFillColor(VOID)
    pdf.setFillAlpha(0.28)
    pdf.circle(screen_x + 69, screen_y + 52, 36, stroke=0, fill=1)
    pdf.setStrokeColor(CYAN)
    pdf.setStrokeAlpha(0.8)
    pdf.setLineWidth(2)
    pdf.circle(screen_x + 69, screen_y + 52, 36, stroke=1, fill=0)
    pdf.setFillColor(CYAN)
    pdf.setFillAlpha(0.72)
    pdf.circle(screen_x + 69, screen_y + 52, 14, stroke=0, fill=1)
    pdf.setFillColor(PINK)
    pdf.setFillAlpha(0.78)
    pdf.roundRect(screen_x + screen_w - 81, screen_y + 25, 58, 38, 6, stroke=0, fill=1)
    pdf.setFillColor(GOLD)
    pdf.roundRect(screen_x + screen_w - 142, screen_y + 68, 58, 38, 6, stroke=0, fill=1)
    pdf.restoreState()
    pdf.setFont("Courier-Bold", 8)
    pdf.setFillColor(VOID)
    pdf.drawCentredString(screen_x + screen_w - 52, screen_y + 40, "FIRE")
    pdf.drawCentredString(screen_x + screen_w - 113, screen_y + 83, "JUMP")
    panel(pdf, 28, 42, 556, 57, fill=PANEL, border=LINE)
    tips = (
        ("MOVE", "Drag the left disc left or right."),
        ("DOWN", "Pull down to interact or drop."),
        ("ACTION", "Tap Jump or Fire; hold Fire when charging."),
        ("PACK", "Tap Pause, then PACK Configuration."),
    )
    column_width = 133
    for index, (label, body) in enumerate(tips):
        x = 39 + index * column_width
        pdf.setFont("Courier-Bold", 7.3)
        pdf.setFillColor((CYAN, GOLD, PINK, GREEN)[index])
        pdf.drawString(x, 82, label)
        draw_wrapped(pdf, body, x, 68, 118, size=6.8, color=MUTED, leading=8)
    pdf.setFont("Courier-Bold", 7)
    pdf.setFillColor(GOLD)
    pdf.drawRightString(PAGE_WIDTH - 29, 320, "BEST IN LANDSCAPE")
    pdf.showPage()


def draw_basics(pdf: canvas.Canvas) -> None:
    section_header(pdf, "Training", "Coreworks Basics", 6)
    cards = (
        (
            28,
            188,
            "01 // JUMP",
            "Hold Cross for a full jump. Release early for a short hop. Jet Assist adds one midair boost before landing.",
            "Images/Game/Super-Frgmnts/aryn-jump-ludo-runtime-v1.png",
            (0, 0, 112, 112),
            CYAN,
        ),
        (
            312,
            188,
            "02 // DOWN",
            "Use Down for prompts, hatches, people, machinery, objective recovery, and drop-through catwalks.",
            "Images/Game/Super-Frgmnts/aryn-drop-ludo-runtime-v1.png",
            (0, 0, 112, 112),
            GOLD,
        ),
        (
            28,
            42,
            "03 // FIRE",
            "Shoot hostile creatures and credit crates. The base beam guides itself; modules trade guidance for new effects.",
            "Images/Game/Super-Frgmnts/aryn-command-rest-runtime-v1.png",
            None,
            PINK,
        ),
        (
            312,
            42,
            "04 // COLLECT",
            "Most loose items collect on contact. Credits and health dropped by enemies fly directly to Aryn.",
            "Images/Game/Super-Frgmnts/foundry-credit-crate-runtime-v1.png",
            None,
            GREEN,
        ),
    )
    for x, y, label, body, asset, crop, accent in cards:
        panel(pdf, x, y, 272, 126, fill=PANEL, border=accent)
        draw_image_contain(
            pdf,
            asset,
            x + 10,
            y + 16,
            78,
            92,
            crop=crop,
            trim_alpha=True,
        )
        pdf.setFont("Courier-Bold", 8)
        pdf.setFillColor(accent)
        pdf.drawString(x + 100, y + 96, label)
        draw_wrapped(
            pdf,
            body,
            x + 100,
            y + 77,
            154,
            size=7.4,
            color=MUTED,
            leading=9,
        )
    pdf.showPage()


def draw_route(pdf: canvas.Canvas) -> None:
    section_header(pdf, "Objectives", "Mission Route", 7)
    routes = (
        ("01", "ARRIVAL", "Find Dras. Install Ghost Vector aboard the RD-42.", CYAN),
        ("02", "FOUNDRY", "Restore 2 stabilizers. Recover 12 fragments. Find Prism and Jet Assist.", GOLD),
        ("03", "THE WOUND", "Follow the pulse. First contact is about survival, not victory.", PINK),
        ("04", "MATERIALS VAULT", "Fight upward through 3 levels and recover the Heliocline catalyst.", GREEN),
        ("05", "REMATCH", "Install Solar Needle, return to Dras, and re-enter the Wound.", ORANGE),
    )
    y = 303
    for index, (number, name, body, accent) in enumerate(routes):
        if index < len(routes) - 1:
            pdf.setStrokeColor(LINE)
            pdf.setLineWidth(2)
            pdf.line(54, y - 17, 54, y - 55)
        pdf.setFillColor(accent)
        pdf.circle(54, y, 16, stroke=0, fill=1)
        pdf.setFont("Courier-Bold", 8)
        pdf.setFillColor(VOID)
        pdf.drawCentredString(54, y - 3, number)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.setFillColor(CREAM)
        pdf.drawString(82, y + 5, name)
        draw_wrapped(pdf, body, 82, y - 10, 286, size=7.3, color=MUTED, leading=8.8)
        y -= 57
    panel(pdf, 397, 42, 187, 272, fill=PANEL, border=PINK)
    draw_image_contain(
        pdf,
        "Images/Game/Super-Frgmnts/aryn-ship-v2.png",
        408,
        226,
        165,
        72,
        trim_alpha=True,
    )
    pdf.setFont("Courier-Bold", 8)
    pdf.setFillColor(CYAN)
    pdf.drawString(412, 210, "UPLINK REQUIREMENTS")
    y = 188
    for line in (
        "Both stabilizers online",
        "12 / 12 fragments",
        "Prism Splinter installed",
    ):
        pdf.setFillColor(GREEN)
        pdf.rect(412, y - 4, 5, 5, stroke=0, fill=1)
        draw_wrapped(pdf, line, 425, y, 144, size=7.2, color=CREAM, leading=9)
        y -= 26
    pdf.setStrokeColor(LINE)
    pdf.line(412, 105, 569, 105)
    draw_wrapped(
        pdf,
        "When the first Seam Hunter feels impossible, the story has noticed.",
        412,
        88,
        157,
        font="Courier-Bold",
        size=7.2,
        color=GOLD,
        leading=9,
    )
    pdf.showPage()


def pack_card(
    pdf: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    code: str,
    name: str,
    body: str,
    accent,
) -> None:
    panel(pdf, x, y, width, height, fill=PANEL, border=accent)
    pdf.setFillColor(accent)
    pdf.rect(x + 10, y + height - 34, 44, 22, stroke=0, fill=1)
    pdf.setFont("Courier-Bold", 8)
    pdf.setFillColor(VOID)
    pdf.drawCentredString(x + 32, y + height - 27, code)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.setFillColor(CREAM)
    pdf.drawString(x + 64, y + height - 26, name)
    draw_wrapped(
        pdf,
        body,
        x + 12,
        y + height - 50,
        width - 24,
        size=7.1,
        color=MUTED,
        leading=8.8,
    )


def draw_pack(pdf: canvas.Canvas) -> None:
    section_header(pdf, "Systems", "PACK Configuration", 8)
    pdf.setFont("Courier", 7.2)
    pdf.setFillColor(MUTED)
    pdf.drawString(29, 320, "One modular backpack beam. Toggle discovered modules independently with Triangle.")
    pack_card(pdf, 28, 189, 272, 114, "BASE", "Backpack Base", "Fast guided shot. Turn every module off to restore maximum seeker guidance.", CYAN)
    pack_card(pdf, 312, 189, 272, 114, "GHO", "Ghost Vector", "Passes through terrain and closed geometry. Phase speed removes guidance.", PINK)
    pack_card(pdf, 28, 63, 272, 114, "PRI", "Prism Splinter", "Divides into three widening lanes. Wide coverage; each lane flies straight.", GREEN)
    pack_card(pdf, 312, 63, 272, 114, "SOL", "Solar Needle", "High direct damage and hostile penetration. Guidance is substantially reduced.", ORANGE)
    panel(pdf, 28, 34, 556, 20, fill=PANEL_ALT, border=GOLD)
    pdf.setFont("Courier-Bold", 6.8)
    pdf.setFillColor(GOLD)
    pdf.drawCentredString(PAGE_WIDTH / 2, 41, "RECOMMENDED REMATCH // PRISM + SOLAR     SAFEST TERRAIN SHOT // GHOST ONLY")
    pdf.showPage()


def pickup_card(
    pdf: canvas.Canvas,
    x: float,
    y: float,
    name: str,
    note: str,
    asset: str,
    accent,
) -> None:
    panel(pdf, x, y, 176, 105, fill=PANEL, border=accent)
    draw_image_contain(pdf, asset, x + 7, y + 22, 58, 72, trim_alpha=True)
    pdf.setFont("Courier-Bold", 7.1)
    pdf.setFillColor(accent)
    pdf.drawString(x + 70, y + 78, name)
    draw_wrapped(pdf, note, x + 70, y + 62, 94, size=6.5, color=MUTED, leading=7.8)


def draw_pickups(pdf: canvas.Canvas) -> None:
    section_header(pdf, "Inventory", "Energy and Pickups", 9)
    pickups = (
        (28, 188, "HEALTH CELL", "+1 Energy. Absorbed on contact, even when Aryn is full.", "Images/Game/Super-Frgmnts/health-cell-v2.png", CYAN),
        (218, 188, "HEALTH CORE", "+4 Energy. Absorbed on contact; recovery clamps at maximum.", "Images/Game/Super-Frgmnts/health-core-v1.png", PINK),
        (408, 188, "JET ASSIST", "One extra midair boost. Refreshes after landing.", "Images/Game/Super-Frgmnts/foundry-jetpack-pickup-runtime-v1.png", GOLD),
        (28, 69, "DIET COKE", "The recognizable route to Prism Splinter. Collect on contact.", "Images/Game/Super-Frgmnts/prism-diet-coke-pickup-runtime-v1.png", GREEN),
        (218, 69, "CREDIT CRATE", "Shoot it open. Released credits collect automatically.", "Images/Game/Super-Frgmnts/foundry-credit-crate-runtime-v1.png", GOLD),
        (408, 69, "VESPERITE*", "Recover all 12. *Artist's conception; field scale may vary.", "Images/Game/Super-Frgmnts/foundry-vesperite-runtime-v1.png", PINK),
    )
    for item in pickups:
        pickup_card(pdf, *item)
    pdf.setFont("Courier-Bold", 7)
    pdf.setFillColor(CREAM)
    pdf.drawString(29, 317, "ENERGY // 12 / 12 = THREE BARS OF FOUR POINTS")
    pdf.setFillColor(MUTED)
    pdf.drawRightString(PAGE_WIDTH - 29, 317, "LOW ENERGY: TEAL > AMBER > MAGENTA-RED")
    pdf.showPage()


def draw_difficulty(pdf: canvas.Canvas) -> None:
    draw_image_cover(
        pdf,
        "Images/Game/Super-Frgmnts/foundry-wound-boss-room-title-runtime-v3.png",
        0,
        0,
        PAGE_WIDTH,
        PAGE_HEIGHT,
    )
    fill_alpha(pdf, VOID, 0.72)
    pdf.setFillColor(PINK)
    pdf.rect(0, PAGE_HEIGHT - 6, PAGE_WIDTH, 6, stroke=0, fill=1)
    pdf.setFont("Courier-Bold", 8)
    pdf.setFillColor(GOLD)
    pdf.drawString(30, PAGE_HEIGHT - 28, "FIELD NOTES // DIFFICULTY")
    pdf.setFont("Helvetica-Bold", 24)
    pdf.setFillColor(CREAM)
    pdf.drawString(30, PAGE_HEIGHT - 60, "Choose Your Trouble")
    panel(pdf, 30, 189, 260, 117, fill=Color(0.04, 0.07, 0.13, 0.95), border=CYAN)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.setFillColor(CYAN)
    pdf.drawString(46, 280, "NORMAL MODE")
    draw_wrapped(pdf, "Standard hostile integrity and Seam Hunter damage.", 46, 257, 226, size=8.2, color=MUTED, leading=10)
    pdf.setFont("Courier-Bold", 7)
    pdf.setFillColor(CREAM)
    pdf.drawString(46, 215, "GOOD FOR THE FIRST TRANSMISSION")
    panel(pdf, 322, 189, 260, 117, fill=Color(0.04, 0.07, 0.13, 0.95), border=RED)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.setFillColor(RED)
    pdf.drawString(338, 280, "HARD MODE")
    draw_wrapped(pdf, "Ordinary enemies: 3x integrity. Seam Hunter: +200 integrity and increased damage.", 338, 257, 226, size=8.2, color=MUTED, leading=10)
    pdf.setFont("Courier-Bold", 7)
    pdf.setFillColor(CREAM)
    pdf.drawString(338, 215, "TRIANGLE CHANGES MODE ON TITLE")
    panel(pdf, 30, 52, 552, 118, fill=Color(0.04, 0.07, 0.13, 0.95), border=PINK)
    pdf.setFont("Courier-Bold", 8)
    pdf.setFillColor(PINK)
    pdf.drawString(46, 146, "ARYN'S FIELD NOTES")
    notes = (
        "Green bubble doors are ready. Red ones still have an unmet objective.",
        "If a route looks unreachable, search for Jet Assist or a drop-through deck.",
        "If the beam behaves strangely, open PACK and check which modules are lit.",
        "If one particular bubble door moved again, it is now local architecture.",
    )
    y = 126
    for note in notes:
        pdf.setFillColor(CYAN)
        pdf.rect(47, y - 4, 4, 4, stroke=0, fill=1)
        draw_wrapped(pdf, note, 59, y, 505, size=7.3, color=CREAM, leading=8.8, max_lines=1)
        y -= 20
    pdf.setFont("Courier-Bold", 8)
    pdf.setFillColor(CREAM)
    pdf.drawCentredString(PAGE_WIDTH / 2, 28, "PLAY // OUTSIDETHEWORLD.COM/SUPER_FRGMNTS.HTML")
    pdf.showPage()


def draw_back_cover(pdf: canvas.Canvas) -> None:
    pdf.setFillColor(VOID)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    draw_image_contain(
        pdf,
        "Images/Game/Super-Frgmnts/planet-veyra-title-v1.png",
        63,
        250,
        PAGE_WIDTH - 126,
        70,
        trim_alpha=True,
    )
    draw_image_contain(
        pdf,
        "Images/Game/Super-Frgmnts/aryn-ship-v2.png",
        135,
        133,
        PAGE_WIDTH - 270,
        105,
        trim_alpha=True,
    )
    pdf.setFont("Helvetica-Bold", 22)
    pdf.setFillColor(CREAM)
    pdf.drawCentredString(PAGE_WIDTH / 2, 102, "TRANSMISSION ENDS HERE.")
    pdf.setFont("Courier", 8)
    pdf.setFillColor(MUTED)
    pdf.drawCentredString(PAGE_WIDTH / 2, 76, "A SMALL, PLAYABLE PIECE OF VEYRA")
    pdf.setFont("Courier-Bold", 8)
    pdf.setFillColor(CYAN)
    pdf.drawCentredString(PAGE_WIDTH / 2, 47, "HTTPS://OUTSIDETHEWORLD.COM/SUPER_FRGMNTS.HTML")
    pdf.setFillColor(PINK)
    pdf.rect(0, 0, PAGE_WIDTH, 7, stroke=0, fill=1)
    pdf.showPage()


def build() -> Path:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT), pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    pdf.setTitle("SUPER FRGMNTS - Arrival on Veyra Player's Field Manual")
    pdf.setAuthor("Super Intention / Outside The World")
    pdf.setSubject("PS4 controller and touch player guide for SUPER FRGMNTS")
    draw_cover(pdf)
    draw_welcome(pdf)
    draw_personnel(pdf)
    draw_controller(pdf)
    draw_touch(pdf)
    draw_basics(pdf)
    draw_route(pdf)
    draw_pack(pdf)
    draw_pickups(pdf)
    draw_difficulty(pdf)
    draw_back_cover(pdf)
    pdf.save()
    return OUTPUT


if __name__ == "__main__":
    print(build())
