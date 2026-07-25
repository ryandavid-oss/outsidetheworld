#!/usr/bin/env python3
"""Build the Revision 3A ship asset and approval reviews.

This script is intentionally design-only. It does not modify the live game.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OVERWORLD = ROOT / "Design" / "Super-Frgmnts" / "Overworld"
SHIP_DIR = OVERWORLD / "Phase-3" / "Ship"
ASSET_DIR = SHIP_DIR / "Assets"
REVIEW_DIR = SHIP_DIR / "Reviews"

SOURCE_SHIP = ASSET_DIR / "aryn-ship-transparent-uncropped-v1.png"
PRODUCTION_SHIP = ASSET_DIR / "aryn-ship-transparent-v1.png"
SHADOW_ASSET = ASSET_DIR / "aryn-ship-hover-field-v1.png"
LANDING_PLATE = (
    OVERWORLD / "Production" / "Plates" / "overworld-landing-flats-v1.png"
)
ARYN_SPRITE = ROOT / "Images" / "Builder" / "signal-ranger-idle-focused-v2.png"

COMPOSITE = REVIEW_DIR / "landing-flats-ship-composite-v1.png"
GUIDE = REVIEW_DIR / "landing-flats-ship-placement-guide-v1.png"
DETAIL = REVIEW_DIR / "landing-flats-ship-scale-detail-v1.png"
PORTRAIT = REVIEW_DIR / "landing-flats-ship-portrait-crop-v1.png"
CONTACT_SHEET = REVIEW_DIR / "ship-revision-3a-contact-sheet-v1.png"
HOVER_PREVIEW = REVIEW_DIR / "landing-flats-ship-hover-preview-v2.gif"
HOVER_KEYFRAMES = REVIEW_DIR / "landing-flats-ship-hover-keyframes-v2.png"
MANIFEST = SHIP_DIR / "ship-revision-3a-manifest.json"

WORLD_WIDTH = 1672
WORLD_HEIGHT = 941
GROUND_Y = 744

SHIP_PLACEMENT = {
    "x": 176,
    "y": 417,
    "width": 792,
    "height": 311,
    "bottom_y": 728,
    "hover_gap": 16,
}
SHADOW_PLACEMENT = {
    "x": 194,
    "y": 702,
    "width": 756,
    "height": 42,
    "bottom_y": 744,
}
ARYN_PLACEMENT = {
    "x": 1000,
    "y": 632,
    "width": 112,
    "height": 112,
    "feet_y": 744,
}
PORTRAIT_WORLD_CROP = {
    "x": 620,
    "y": 0,
    "width": 560,
    "height": 941,
}
HOVER_OFFSETS = (
    0.0,
    -0.9,
    -1.9,
    -2.7,
    -3.2,
    -2.7,
    -1.9,
    -0.9,
    0.0,
    0.9,
    1.9,
    2.7,
    3.2,
    2.7,
    1.9,
    0.9,
)
HOVER_FRAME_DURATION_MS = 100

FONT_PATH = "/System/Library/Fonts/SFNSMono.ttf"
FONT_BOLD_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

COLORS = {
    "ink": (244, 241, 247, 255),
    "muted": (173, 185, 216, 255),
    "cyan": (83, 240, 225, 255),
    "magenta": (239, 89, 174, 255),
    "amber": (246, 194, 96, 255),
    "blue": (127, 170, 255, 255),
    "panel": (4, 8, 25, 255),
    "panel_soft": (8, 14, 36, 255),
    "plum": (59, 29, 67, 255),
}


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD_PATH if bold else FONT_PATH, size)


def ensure_directories() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)


def clean_and_crop_ship() -> Image.Image:
    """Remove weak matte debris, then crop with a consistent transparent margin."""
    source = Image.open(SOURCE_SHIP).convert("RGBA")
    red, green, blue, alpha = source.split()

    # The chroma extraction left two low-opacity caps above the upper pods.
    # They are all below alpha 64. Stronger antialiasing and hull pixels remain
    # untouched, preserving the image-generation result rather than redrawing it.
    cleaned_alpha = alpha.point(lambda value: 0 if value < 64 else value)
    cleaned = Image.merge("RGBA", (red, green, blue, cleaned_alpha))
    bbox = cleaned_alpha.getbbox()
    if bbox is None:
        raise RuntimeError("The ship asset has no visible pixels after matte cleanup.")

    production = cleaned.crop(bbox)
    production.save(PRODUCTION_SHIP)
    return production


def build_shadow() -> Image.Image:
    """Create a restrained, pixel-stepped hover shadow as a separate overlay."""
    width = SHADOW_PLACEMENT["width"]
    height = SHADOW_PLACEMENT["height"]
    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)

    # Nested hard-edged ellipses read as a soft shadow after display scaling
    # without introducing a blurry photographic effect into the pixel scene.
    draw.ellipse((0, 4, width - 1, height - 1), fill=(9, 5, 19, 28))
    draw.ellipse((42, 7, width - 43, height - 1), fill=(7, 4, 16, 40))
    draw.ellipse((116, 11, width - 117, height - 2), fill=(5, 3, 14, 52))
    draw.ellipse((220, 15, width - 221, height - 3), fill=(2, 2, 10, 64))

    # A low-opacity cyan center turns the separation into a deliberate hover
    # field. The stronger breathing-light animation remains reserved for Phase 4.
    glow = Image.new("RGBA", shadow.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse(
        (180, 15, width - 181, height - 4),
        fill=(35, 222, 214, 14),
    )
    glow_draw.ellipse(
        (278, 19, width - 279, height - 6),
        fill=(89, 250, 235, 18),
    )
    shadow = Image.alpha_composite(shadow, glow)

    # Sparse deterministic edge pixels break the perfectly smooth ellipse.
    pixels = shadow.load()
    for x in range(8, width - 8, 8):
        y = 2 + ((x // 8) % 3)
        if (x // 8) % 2 == 0:
            pixels[x, y] = (20, 9, 29, 18)
    shadow.save(SHADOW_ASSET)
    return shadow


def resize_ship(ship: Image.Image) -> Image.Image:
    return ship.resize(
        (SHIP_PLACEMENT["width"], SHIP_PLACEMENT["height"]),
        Image.Resampling.LANCZOS,
    )


def build_composite(ship: Image.Image, shadow: Image.Image) -> Image.Image:
    plate = Image.open(LANDING_PLATE).convert("RGBA")
    if plate.size != (WORLD_WIDTH, WORLD_HEIGHT):
        raise ValueError(f"Unexpected Landing Flats size: {plate.size}")

    composite = plate.copy()
    composite.alpha_composite(
        shadow,
        (SHADOW_PLACEMENT["x"], SHADOW_PLACEMENT["y"]),
    )
    composite.alpha_composite(
        resize_ship(ship),
        (SHIP_PLACEMENT["x"], SHIP_PLACEMENT["y"]),
    )
    aryn = Image.open(ARYN_SPRITE).convert("RGBA")
    composite.alpha_composite(aryn, (ARYN_PLACEMENT["x"], ARYN_PLACEMENT["y"]))
    composite.save(COMPOSITE)
    return composite


def adjusted_shadow(shadow: Image.Image, offset_y: float) -> tuple[Image.Image, int]:
    """Pulse the fixed ground shadow inversely to the ship's hover height."""
    scale_x = 1.0 - offset_y * 0.008
    width = round(shadow.width * scale_x)
    resized = shadow.resize((width, shadow.height), Image.Resampling.LANCZOS)
    alpha_scale = 1.0 + offset_y * 0.05
    red, green, blue, alpha = resized.split()
    alpha = alpha.point(lambda value: min(255, round(value * alpha_scale)))
    resized = Image.merge("RGBA", (red, green, blue, alpha))
    center_x = SHADOW_PLACEMENT["x"] + SHADOW_PLACEMENT["width"] // 2
    return resized, center_x - width // 2


def repulsor_dust(frame_index: int) -> Image.Image:
    """Build a sparse, seamlessly looping dust-and-energy particle layer."""
    layer = Image.new("RGBA", (WORLD_WIDTH, WORLD_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    origins = (350, 794)
    frame_phase = frame_index / len(HOVER_OFFSETS)
    palette = (
        (221, 153, 100),
        (188, 119, 83),
        (89, 224, 213),
    )

    for index in range(12):
        age = (frame_phase + index / 12) % 1.0
        fade = math.sin(math.pi * age)
        if fade < 0.08:
            continue
        origin = origins[index % 2]
        direction = -1 if (index // 2) % 2 == 0 else 1
        travel = 12 + (index % 4) * 7
        x = round(origin + direction * travel * age)
        y = round(740 - 5 * math.sin(math.pi * age) - (index % 3))
        width = 2 + index % 4
        height = 1 + (index // 3) % 2
        color = palette[index % len(palette)]
        max_alpha = 42 if index % 3 == 2 else 66
        alpha = round(max_alpha * fade)
        draw.rectangle(
            (x - width // 2, y - height, x + width // 2, y),
            fill=(*color, alpha),
        )
    return layer


def subpixel_ship_layer(
    supersampled_ship: Image.Image,
    offset_y: float,
) -> tuple[Image.Image, tuple[int, int]]:
    """Render the hover offset at quarter-pixel precision without held frames."""
    scale = 4
    padding = 5
    layer = Image.new(
        "RGBA",
        (
            SHIP_PLACEMENT["width"] * scale,
            (SHIP_PLACEMENT["height"] + padding * 2) * scale,
        ),
        (0, 0, 0, 0),
    )
    layer.alpha_composite(
        supersampled_ship,
        (0, padding * scale + round(offset_y * scale)),
    )
    layer = layer.resize(
        (
            SHIP_PLACEMENT["width"],
            SHIP_PLACEMENT["height"] + padding * 2,
        ),
        Image.Resampling.LANCZOS,
    )
    return layer, (
        SHIP_PLACEMENT["x"],
        SHIP_PLACEMENT["y"] - padding,
    )


def build_hover_frame(
    plate: Image.Image,
    supersampled_ship: Image.Image,
    shadow: Image.Image,
    aryn: Image.Image,
    frame_index: int,
) -> Image.Image:
    offset_y = HOVER_OFFSETS[frame_index]
    frame = plate.copy()
    pulsed_shadow, shadow_x = adjusted_shadow(shadow, offset_y)
    frame.alpha_composite(
        pulsed_shadow,
        (shadow_x, SHADOW_PLACEMENT["y"]),
    )
    frame = Image.alpha_composite(frame, repulsor_dust(frame_index))
    ship_layer, ship_xy = subpixel_ship_layer(supersampled_ship, offset_y)
    frame.alpha_composite(ship_layer, ship_xy)
    frame.alpha_composite(aryn, (ARYN_PLACEMENT["x"], ARYN_PLACEMENT["y"]))
    return frame


def build_hover_preview(ship: Image.Image, shadow: Image.Image) -> None:
    plate = Image.open(LANDING_PLATE).convert("RGBA")
    aryn = Image.open(ARYN_SPRITE).convert("RGBA")
    supersampled_ship = ship.resize(
        (
            SHIP_PLACEMENT["width"] * 4,
            SHIP_PLACEMENT["height"] * 4,
        ),
        Image.Resampling.LANCZOS,
    )
    frames = [
        build_hover_frame(plate, supersampled_ship, shadow, aryn, index)
        for index in range(len(HOVER_OFFSETS))
    ]

    preview_frames = [
        frame.convert("RGB").resize((960, 540), Image.Resampling.LANCZOS)
        for frame in frames
    ]
    preview_frames[0].save(
        HOVER_PREVIEW,
        save_all=True,
        append_images=preview_frames[1:],
        duration=HOVER_FRAME_DURATION_MS,
        loop=0,
        disposal=2,
        optimize=True,
    )

    selected = (4, 0, 12)
    keyframes = Image.new("RGBA", (1472, 418), COLORS["panel"])
    key_draw = ImageDraw.Draw(keyframes)
    labels = ("HIGH // −3.2 PX", "MID // 0 PX", "LOW // +3.2 PX")
    for slot, (frame_index, label) in enumerate(zip(selected, labels)):
        image = frames[frame_index].resize((480, 270), Image.Resampling.LANCZOS)
        x = 8 + slot * 488
        keyframes.alpha_composite(image, (x, 64))
        key_draw.text(
            (x + 12, 20),
            label,
            font=font(18, bold=True),
            fill=COLORS["cyan"],
        )
    key_draw.text(
        (20, 360),
        "1.6 S LOOP // ±3.2 PX CONTINUOUS BOB // NO HELD FRAMES // OUTWARD REPULSOR DUST",
        font=font(17),
        fill=COLORS["muted"],
    )
    keyframes.save(HOVER_KEYFRAMES)


def text_label(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    *,
    fill: tuple[int, int, int, int],
    size: int = 18,
) -> None:
    x, y = xy
    label_font = font(size)
    bounds = draw.textbbox((x, y), value, font=label_font)
    draw.rounded_rectangle(
        (bounds[0] - 7, bounds[1] - 4, bounds[2] + 7, bounds[3] + 5),
        radius=4,
        fill=(3, 7, 20, 224),
        outline=fill,
        width=2,
    )
    draw.text((x, y), value, font=label_font, fill=fill)


def build_placement_guide(composite: Image.Image) -> Image.Image:
    guide = composite.copy()
    overlay = Image.new("RGBA", guide.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    draw.line((0, GROUND_Y, WORLD_WIDTH, GROUND_Y), fill=COLORS["amber"], width=3)
    draw.rectangle(
        (
            SHIP_PLACEMENT["x"],
            SHIP_PLACEMENT["y"],
            SHIP_PLACEMENT["x"] + SHIP_PLACEMENT["width"],
            SHIP_PLACEMENT["y"] + SHIP_PLACEMENT["height"],
        ),
        outline=COLORS["cyan"],
        width=3,
    )
    draw.rectangle(
        (
            ARYN_PLACEMENT["x"],
            ARYN_PLACEMENT["y"],
            ARYN_PLACEMENT["x"] + ARYN_PLACEMENT["width"],
            ARYN_PLACEMENT["y"] + ARYN_PLACEMENT["height"],
        ),
        outline=COLORS["magenta"],
        width=3,
    )
    text_label(
        draw,
        (SHIP_PLACEMENT["x"] + 8, SHIP_PLACEMENT["y"] - 31),
        "SHIP 792 × 331",
        fill=COLORS["cyan"],
    )
    text_label(
        draw,
        (ARYN_PLACEMENT["x"] + 8, ARYN_PLACEMENT["y"] - 31),
        "ARYN 112 × 112 DRAW BOX",
        fill=COLORS["magenta"],
    )
    text_label(
        draw,
        (18, GROUND_Y - 34),
        "GROUND Y 744",
        fill=COLORS["amber"],
    )
    guide = Image.alpha_composite(guide, overlay)
    guide.save(GUIDE)
    return guide


def build_detail(composite: Image.Image) -> Image.Image:
    # Native-pixel crop preserves the scale relationship for close inspection.
    crop_box = (112, 336, 1176, 800)
    detail = composite.crop(crop_box)
    draw = ImageDraw.Draw(detail)
    draw.line(
        (0, GROUND_Y - crop_box[1], detail.width, GROUND_Y - crop_box[1]),
        fill=COLORS["amber"],
        width=2,
    )
    detail.save(DETAIL)
    return detail


def build_portrait(composite: Image.Image) -> Image.Image:
    crop = PORTRAIT_WORLD_CROP
    portrait = composite.crop(
        (
            crop["x"],
            crop["y"],
            crop["x"] + crop["width"],
            crop["y"] + crop["height"],
        )
    )
    target_width = 390
    target_height = round(portrait.height * target_width / portrait.width)
    portrait = portrait.resize(
        (target_width, target_height),
        Image.Resampling.LANCZOS,
    )
    portrait.save(PORTRAIT)
    return portrait


def panel(
    canvas: Image.Image,
    xy: tuple[int, int],
    size: tuple[int, int],
    title: str,
) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    x, y = xy
    width, height = size
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (x, y, x + width, y + height),
        radius=12,
        fill=COLORS["panel_soft"],
        outline=(53, 72, 119, 255),
        width=2,
    )
    draw.text(
        (x + 20, y + 16),
        title,
        font=font(22, bold=True),
        fill=COLORS["ink"],
    )
    inner = Image.new("RGBA", (width - 40, height - 64), (0, 0, 0, 0))
    return inner, draw


def fit(image: Image.Image, bounds: tuple[int, int]) -> Image.Image:
    width, height = bounds
    scale = min(width / image.width, height / image.height)
    return image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )


def build_contact_sheet(
    composite: Image.Image,
    guide: Image.Image,
    detail: Image.Image,
    portrait: Image.Image,
) -> Image.Image:
    sheet = Image.new("RGBA", (1900, 1900), COLORS["panel"])
    draw = ImageDraw.Draw(sheet)

    draw.text(
        (80, 42),
        "SUPER FRGMNTS // OVERWORLD REVISION 3A",
        font=font(36, bold=True),
        fill=COLORS["ink"],
    )
    draw.text(
        (82, 90),
        "SHIP LANDING COMPOSITION // APPROVAL IMAGE",
        font=font(22),
        fill=COLORS["cyan"],
    )
    draw.text(
        (82, 124),
        "Design-only review. No live-game integration.",
        font=font(18),
        fill=COLORS["muted"],
    )

    # Full composition
    draw.rounded_rectangle(
        (80, 170, 1820, 1195),
        radius=14,
        fill=COLORS["panel_soft"],
        outline=(53, 72, 119, 255),
        width=2,
    )
    draw.text(
        (108, 192),
        "01 // FULL LANDING FLATS COMPOSITION",
        font=font(22, bold=True),
        fill=COLORS["ink"],
    )
    full = fit(composite, (1672, 941))
    sheet.alpha_composite(full, (114, 240))

    # Scale-detail panel
    draw.rounded_rectangle(
        (80, 1230, 1285, 1818),
        radius=14,
        fill=COLORS["panel_soft"],
        outline=(53, 72, 119, 255),
        width=2,
    )
    draw.text(
        (108, 1252),
        "02 // NATIVE SCALE RELATIONSHIP",
        font=font(22, bold=True),
        fill=COLORS["ink"],
    )
    detail_fit = fit(detail, (1148, 500))
    detail_x = 108 + (1148 - detail_fit.width) // 2
    sheet.alpha_composite(detail_fit, (detail_x, 1304))
    draw.text(
        (108, 1772),
        "Aryn remains at her current 112 × 112 gameplay draw box.",
        font=font(17),
        fill=COLORS["muted"],
    )

    # Portrait crop panel
    draw.rounded_rectangle(
        (1315, 1230, 1820, 1818),
        radius=14,
        fill=COLORS["panel_soft"],
        outline=(53, 72, 119, 255),
        width=2,
    )
    draw.text(
        (1343, 1252),
        "03 // PORTRAIT CROP",
        font=font(22, bold=True),
        fill=COLORS["ink"],
    )
    portrait_fit = fit(portrait, (390, 505))
    portrait_x = 1372 + (390 - portrait_fit.width) // 2
    sheet.alpha_composite(portrait_fit, (portrait_x, 1304))
    draw.text(
        (1343, 1772),
        "Candidate world window x 620–1180",
        font=font(15),
        fill=COLORS["muted"],
    )

    sheet.save(CONTACT_SHEET)
    return sheet


def write_manifest(production_ship: Image.Image) -> None:
    data = {
        "revision": "3A",
        "status": "approved",
        "approval": {
            "approved_on": "2026-07-25",
            "approved_revision": "hover-preview-v2",
        },
        "scope": "Ship scale, placement, grounding, and portrait framing only",
        "live_game_modified": False,
        "coordinate_system": {
            "plate_width": WORLD_WIDTH,
            "plate_height": WORLD_HEIGHT,
            "ground_y": GROUND_Y,
        },
        "assets": {
            "ship": str(PRODUCTION_SHIP.relative_to(ROOT)),
            "ship_dimensions": {
                "width": production_ship.width,
                "height": production_ship.height,
            },
            "shadow": str(SHADOW_ASSET.relative_to(ROOT)),
            "aryn_reference": str(ARYN_SPRITE.relative_to(ROOT)),
        },
        "matte_cleanup": {
            "rule": "Alpha values below 64 set to zero; stronger pixels unchanged",
            "reason": "Remove two faint low-opacity caps above the upper pods",
        },
        "placement": {
            "ship": SHIP_PLACEMENT,
            "shadow": SHADOW_PLACEMENT,
            "aryn": ARYN_PLACEMENT,
        },
        "portrait_crop_candidate": PORTRAIT_WORLD_CROP,
        "hover_motion_proof": {
            "preview": str(HOVER_PREVIEW.relative_to(ROOT)),
            "keyframes": str(HOVER_KEYFRAMES.relative_to(ROOT)),
            "cycle_ms": len(HOVER_OFFSETS) * HOVER_FRAME_DURATION_MS,
            "frame_duration_ms": HOVER_FRAME_DURATION_MS,
            "ship_offset_y_px": list(HOVER_OFFSETS),
            "curve": "Continuous eased loop with quarter-pixel rendering and no duplicated hold frames",
            "runtime_interpolation": "Evaluate the curve every render frame rather than stepping through preview samples",
            "shadow_behavior": "Fixed to ground; subtly widens and fades as the ship rises",
            "repulsor_dust": {
                "style": "Sparse sand pixels with restrained cyan energy flecks",
                "direction": "Outward from the two lower repulsors",
                "runtime_note": "Implement as a separate particle layer; never bake into the landscape plate",
            },
        },
        "approval_questions": [
            "Does the ship feel large enough to be Aryn's vessel without crowding the plate?",
            "Is the gap between the ship and Aryn comfortable?",
            "Does the 16-pixel hover gap read as deliberate sci-fi lift?",
            "Does the restrained cyan ground field support the hover without becoming an effect spectacle?",
            "Is the partial ship reveal in the portrait crop narratively acceptable?",
        ],
    }
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def validate(ship: Image.Image, composite: Image.Image, portrait: Image.Image) -> None:
    assert ship.mode == "RGBA"
    assert ship.getchannel("A").getbbox() is not None
    assert composite.size == (WORLD_WIDTH, WORLD_HEIGHT)
    assert SHIP_PLACEMENT["y"] + SHIP_PLACEMENT["height"] == 728
    assert GROUND_Y - SHIP_PLACEMENT["bottom_y"] == SHIP_PLACEMENT["hover_gap"]
    assert SHADOW_PLACEMENT["y"] + SHADOW_PLACEMENT["height"] == GROUND_Y
    assert ARYN_PLACEMENT["y"] + ARYN_PLACEMENT["height"] == GROUND_Y
    assert portrait.width == 390
    assert min(HOVER_OFFSETS) == -3.2 and max(HOVER_OFFSETS) == 3.2
    assert all(
        HOVER_OFFSETS[index] != HOVER_OFFSETS[(index + 1) % len(HOVER_OFFSETS)]
        for index in range(len(HOVER_OFFSETS))
    )
    assert PRODUCTION_SHIP.exists()
    assert SHADOW_ASSET.exists()
    assert all(
        path.exists()
        for path in (
            COMPOSITE,
            GUIDE,
            DETAIL,
            PORTRAIT,
            CONTACT_SHEET,
            HOVER_PREVIEW,
            HOVER_KEYFRAMES,
            MANIFEST,
        )
    )


def main() -> None:
    ensure_directories()
    ship = clean_and_crop_ship()
    shadow = build_shadow()
    composite = build_composite(ship, shadow)
    guide = build_placement_guide(composite)
    detail = build_detail(composite)
    portrait = build_portrait(composite)
    build_contact_sheet(composite, guide, detail, portrait)
    build_hover_preview(ship, shadow)
    write_manifest(ship)
    validate(ship, composite, portrait)
    print(f"Production ship: {PRODUCTION_SHIP} ({ship.width}x{ship.height})")
    print(f"Composite: {COMPOSITE}")
    print(f"Contact sheet: {CONTACT_SHEET}")
    print(f"Hover preview: {HOVER_PREVIEW}")
    print(f"Manifest: {MANIFEST}")


if __name__ == "__main__":
    main()
