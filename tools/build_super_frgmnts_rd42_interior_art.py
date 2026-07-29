#!/usr/bin/env python3
"""Validate and package the approved RD-42 production interior plate."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INTERIOR_ROOT = (
    PROJECT_ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Overworld"
    / "Phase-3"
    / "Ship"
    / "Interior"
)
MASTER = (
    INTERIOR_ROOT
    / "Assets"
    / "rd42-interior-rear-plate-production-v1.png"
)
RUNTIME = (
    PROJECT_ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "rd42-interior-rear-plate-runtime-v1.png"
)
SCALE_REVIEW = (
    INTERIOR_ROOT
    / "Reviews"
    / "rd42-interior-rear-plate-scale-check-production-v1.png"
)
MANIFEST = (
    INTERIOR_ROOT
    / "rd42-interior-rear-plate-production-v1.json"
)

WIDTH = 1672
HEIGHT = 941
OCCUPIED_CEILING_Y = 438
GAMEPLAY_DECK_Y = 744
DORSAL_HATCH_CENTER_X = 684
PLAYER_CELL = 112
PLAYER_SPRITE = (
    PROJECT_ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "aryn-field-rest-runtime-v1.png"
)
PLAYER_REVIEW_CENTERS = (386, 684, 1274)

OTW_PALETTE = {
    "brand_blue": "#6395EE",
    "brand_light_blue": "#A0BEF5",
    "brand_teal": "#91AFB3",
    "logo_navy": "#1B365D",
    "logo_teal": "#3D5255",
    "logo_ink": "#1A1C20",
    "void_dark": "#0A0A0A",
    "text_main": "#EEEEEE",
}


def load_font(size: int) -> ImageFont.ImageFont:
    for candidate in (
        Path("/System/Library/Fonts/Menlo.ttc"),
        Path("/System/Library/Fonts/SFNSMono.ttf"),
        Path("/Library/Fonts/Arial Unicode.ttf"),
    ):
        if candidate.exists():
            return ImageFont.truetype(
                str(candidate),
                size=size,
            )
    return ImageFont.load_default()


def validate_master() -> Image.Image:
    master = Image.open(MASTER).convert("RGB")
    if master.size != (WIDTH, HEIGHT):
        raise ValueError(
            f"RD-42 production master is {master.size}; "
            f"expected {(WIDTH, HEIGHT)}"
        )
    return master


def write_runtime(master: Image.Image) -> None:
    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    master.save(RUNTIME, optimize=True)


def write_scale_review(master: Image.Image) -> None:
    review = master.convert("RGBA")
    overlay = Image.new(
        "RGBA",
        review.size,
        (0, 0, 0, 0),
    )
    draw = ImageDraw.Draw(overlay)
    font = load_font(16)
    title_font = load_font(22)

    draw.rectangle(
        (20, 18, 612, 96),
        fill=(10, 10, 10, 218),
        outline=(160, 190, 245, 255),
        width=2,
    )
    draw.text(
        (40, 32),
        "RD-42 PRODUCTION ART // RUNTIME ARYN",
        font=title_font,
        fill=(238, 238, 238, 255),
    )
    draw.text(
        (40, 65),
        "112 px cell  •  occupied volume 306 px  •  OTW light palette",
        font=font,
        fill=(160, 190, 245, 255),
    )

    for y, label, color in (
        (
            OCCUPIED_CEILING_Y,
            "OCCUPIED CEILING // y438",
            (145, 175, 179, 255),
        ),
        (
            GAMEPLAY_DECK_Y,
            "GAMEPLAY DECK // y744",
            (238, 238, 238, 255),
        ),
    ):
        draw.line(
            (20, y, WIDTH - 20, y),
            fill=color,
            width=2,
        )
        draw.text(
            (28, y - 24),
            label,
            font=font,
            fill=color,
        )

    player = Image.open(PLAYER_SPRITE).convert("RGBA")
    for center_x in PLAYER_REVIEW_CENTERS:
        player_x = center_x - PLAYER_CELL // 2
        player_y = GAMEPLAY_DECK_Y - 100
        overlay.alpha_composite(player, (player_x, player_y))
        draw.rectangle(
            (
                player_x,
                GAMEPLAY_DECK_Y - 100,
                player_x + PLAYER_CELL,
                GAMEPLAY_DECK_Y + 12,
            ),
            outline=(99, 149, 238, 255),
            width=2,
        )

    review = Image.alpha_composite(review, overlay)
    SCALE_REVIEW.parent.mkdir(parents=True, exist_ok=True)
    review.convert("RGB").save(SCALE_REVIEW, optimize=True)


def write_manifest() -> None:
    manifest = {
        "id": "rd42-interior-rear-plate-production-v1",
        "status": "approved-runtime-art",
        "established": "2026-07-28",
        "runtime_integrated": True,
        "generation": {
            "method": "OpenAI built-in image generation",
            "mode": "style-transfer and geometry-preserving production pass",
            "edit_target":
                "Design/Super-Frgmnts/Overworld/Phase-3/Ship/Interior/Assets/rd42-interior-rear-plate-pixel-candidate-v2.png",
            "geometry_reference":
                "Design/Super-Frgmnts/Overworld/Phase-3/Ship/Interior/Reviews/rd42-interior-wireframe-compressed-v2.png",
            "palette_reference":
                "Core OTW palette supplied 2026-07-28",
            "logo_references": [
                "Images/Builder/OTW_Brandmark.svg",
                "Images/Builder/OTW_Brandmark_dark.svg",
            ],
            "prompt_summary":
                "Preserve the 1672x941 compact side-on geometry while replacing the Foundry-dark material language with the lighter OTW blue/teal palette, adding the flight/suit alcove, sealed keel hatch, and a faithful in-world pixel OTW mark.",
        },
        "asset": {
            "master": str(MASTER.relative_to(PROJECT_ROOT)),
            "runtime": str(RUNTIME.relative_to(PROJECT_ROOT)),
            "width": WIDTH,
            "height": HEIGHT,
            "format": "PNG",
            "layer": "rear-only",
            "style": "16-bit SNES-era pixel art",
        },
        "geometry": {
            "normal_occupied_ceiling_y":
                OCCUPIED_CEILING_Y,
            "gameplay_deck_y": GAMEPLAY_DECK_Y,
            "occupied_volume_height":
                GAMEPLAY_DECK_Y - OCCUPIED_CEILING_Y,
            "dorsal_hatch_center_x":
                DORSAL_HATCH_CENTER_X,
            "player_reference_box": [
                PLAYER_CELL,
                PLAYER_CELL,
            ],
            "flight_suit_alcove_x": [438, 562],
            "sealed_keel_hatch_x": [962, 1086],
        },
        "palette": {
            "authoritative": OTW_PALETTE,
            "usage": {
                "dominant_occupied_cabin": [
                    "#A0BEF5",
                    "#91AFB3",
                    "#EEEEEE",
                ],
                "structure_and_depth": [
                    "#6395EE",
                    "#1B365D",
                    "#3D5255",
                ],
                "sparse_only": [
                    "#1A1C20",
                    "#0A0A0A",
                ],
            },
        },
        "brandmark": {
            "treatment":
                "faithful three-band OTW symbol translated into an in-world 16-bit cockpit bulkhead mosaic",
            "placement":
                "cockpit-side bulkhead beside the flight/suit alcove",
            "text": False,
            "ui_watermark": False,
        },
        "separate_runtime_layers": [
            "dorsal hatch doors",
            "service-kit case",
            "Trillian occupied marker",
            "specimen response glows",
            "Aryn",
            "particles",
            "interaction prompts",
        ],
        "review": {
            "scale_check": str(
                SCALE_REVIEW.relative_to(PROJECT_ROOT)
            ),
            "supersedes":
                "rd42-interior-rear-plate-pixel-candidate-v2",
            "scale_approved": True,
            "runtime_art_approved": True,
        },
    }
    MANIFEST.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    master = validate_master()
    write_runtime(master)
    write_scale_review(master)
    write_manifest()
    for output in (RUNTIME, SCALE_REVIEW, MANIFEST):
        print(f"Wrote {output.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
