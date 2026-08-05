#!/usr/bin/env python3
"""Build a compact review sheet for Aryn's three-panel Prism cutscene."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PANEL_DIR = ROOT / "Design" / "Super-Frgmnts" / "Aryn" / "Prism-Cutscene"
OUTPUT = PANEL_DIR / "aryn-prism-comic-sequence-review-v1.png"
PANELS = [
    ("01 // REACH", "aryn-prism-comic-panel-01-reach-v1.png"),
    ("02 // INSTALL", "aryn-prism-comic-panel-02-install-v1.png"),
    ("03 // ACTIVATE", "aryn-prism-comic-panel-03-activate-v1.png"),
]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype("/System/Library/Fonts/SFNSMono.ttf", size=size)


def main() -> None:
    width = 1280
    margin = 52
    title_height = 142
    label_height = 42
    panel_width = width - margin * 2
    panel_height = round(panel_width * 941 / 1672)
    gap = 42
    height = title_height + len(PANELS) * (label_height + panel_height + gap) + margin

    sheet = Image.new("RGB", (width, height), "#070b16")
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, 38), "PRISM INSTALL // COMIC SEQUENCE V1", font=font(38), fill="#f4f7ff")
    draw.text(
        (margin, 94),
        "Review assets only — native panel size 1672 × 941",
        font=font(18),
        fill="#8fa8c6",
    )

    y = title_height
    for label, filename in PANELS:
        draw.text((margin, y), label, font=font(24), fill="#58f5df")
        y += label_height
        panel = Image.open(PANEL_DIR / filename).convert("RGB")
        panel = panel.resize((panel_width, panel_height), Image.Resampling.LANCZOS)
        sheet.paste(panel, (margin, y))
        draw.rectangle(
            (margin, y, margin + panel_width - 1, y + panel_height - 1),
            outline="#405f7e",
            width=2,
        )
        y += panel_height + gap

    sheet.save(OUTPUT, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
