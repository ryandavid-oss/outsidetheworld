#!/usr/bin/env python3
"""Build deterministic source and review assets for Dras Ehdre.

The AI-assisted background extraction is intentionally outside this script.
Everything before and after that step is reproducible with Pillow. This is a
design-review builder only; it never touches the live game.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(
    "/Users/rylee/Downloads/ChatGPT Image Jul 24, 2026 at 11_21_08 PM.png"
)
DRAS_DIR = ROOT / "Design/Super-Frgmnts/Overworld/Phase-3/Dras"
RAW_DIR = DRAS_DIR / "Raw"
ASSET_DIR = DRAS_DIR / "Assets"
REVIEW_DIR = DRAS_DIR / "Reviews"
UNCROPPED = ASSET_DIR / "dras-transparent-uncropped-v1.png"
MASTER = ASSET_DIR / "dras-transparent-master-v1.png"
RUNTIME = ASSET_DIR / "dras-runtime-candidate-v1.png"
OUTPOST_PLATE = (
    ROOT
    / "Design/Super-Frgmnts/Overworld/Production/Plates"
    / "overworld-dras-outpost-v1.png"
)
ARYN_SPRITE = ROOT / "Images/Builder/signal-ranger-idle-focused-v2.png"

FONT_PATH = "/System/Library/Fonts/SFNSMono.ttf"
FONT_BOLD_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
PLATE_SIZE = (1672, 941)
GROUND_Y = 744
DRAS_LOCAL_X = 280
DRAS_RUNTIME_BOX = (96, 112)
DRAS_VISIBLE_HEIGHT = 104

COLORS = {
    "panel": (4, 8, 25, 255),
    "panel_soft": (9, 15, 36, 255),
    "ink": (238, 238, 238, 255),
    "muted": (160, 190, 245, 255),
    "cyan": (145, 175, 179, 255),
    "cyan_bright": (83, 240, 225, 255),
    "blue": (99, 149, 238, 255),
    "light_blue": (160, 190, 245, 255),
    "gold": (217, 192, 140, 255),
    "pink": (255, 105, 180, 255),
    "plum": (103, 81, 104, 255),
}

# Pose two is the most complete, balanced instance in the repeated concept strip.
# Padding is retained so the extraction model can distinguish the complete silhouette.
IDENTITY_CROP = (288, 148, 568, 888)


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD_PATH if bold else FONT_PATH, size)


def prepare_identity_crop() -> Path:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Dras source concept not found: {SOURCE}")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    output = RAW_DIR / "dras-identity-crop-v1.png"
    with Image.open(SOURCE) as source:
        source.convert("RGB").crop(IDENTITY_CROP).save(output)
    return output


def trim_transparent_master() -> Image.Image:
    if not UNCROPPED.exists():
        raise FileNotFoundError(
            "Run the chroma extraction step before building Dras reviews: "
            f"{UNCROPPED}"
        )

    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    source = Image.open(UNCROPPED).convert("RGBA")
    red, green, blue, alpha = source.split()
    # Remove only nearly invisible extraction debris. Keep the hair, coat fringe,
    # staff silhouette, and original antialiasing intact.
    alpha = alpha.point(lambda value: 0 if value < 8 else value)
    cleaned = Image.merge("RGBA", (red, green, blue, alpha))
    bbox = alpha.getbbox()
    if bbox is None:
        raise RuntimeError("Dras extraction has no visible pixels.")

    margin = 12
    left = max(0, bbox[0] - margin)
    top = max(0, bbox[1] - margin)
    right = min(cleaned.width, bbox[2] + margin)
    bottom = min(cleaned.height, bbox[3] + margin)
    master = cleaned.crop((left, top, right, bottom))
    master.save(MASTER)
    return master


def fit_actor(
    master: Image.Image,
    *,
    canvas_size: tuple[int, int],
    visible_height: int,
) -> Image.Image:
    scale = visible_height / master.height
    width = max(1, round(master.width * scale))
    actor = master.resize((width, visible_height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    x = (canvas_size[0] - width) // 2
    y = canvas_size[1] - visible_height
    canvas.alpha_composite(actor, (x, y))
    return canvas


def build_runtime(master: Image.Image) -> Image.Image:
    runtime = fit_actor(
        master,
        canvas_size=DRAS_RUNTIME_BOX,
        visible_height=DRAS_VISIBLE_HEIGHT,
    )
    runtime.save(RUNTIME)
    return runtime


def actor_shadow(width: int = 72, height: int = 12) -> Image.Image:
    shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.ellipse((0, 2, width - 1, height - 1), fill=(2, 2, 12, 70))
    draw.ellipse((12, 4, width - 13, height - 2), fill=(2, 2, 9, 82))
    return shadow.filter(ImageFilter.GaussianBlur(0.6))


def place_actor(
    scene: Image.Image,
    actor: Image.Image,
    x: int,
    *,
    ground_y: int = GROUND_Y,
    add_shadow: bool = True,
) -> None:
    if add_shadow:
        shadow = actor_shadow()
        scene.alpha_composite(
            shadow,
            (x + actor.width // 2 - shadow.width // 2, ground_y - 7),
        )
    scene.alpha_composite(actor, (x, ground_y - actor.height))


def draw_panel(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    *,
    title: str | None = None,
    accent: tuple[int, int, int, int] = COLORS["cyan_bright"],
) -> ImageDraw.ImageDraw:
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        box,
        radius=12,
        fill=COLORS["panel_soft"],
        outline=accent,
        width=2,
    )
    if title:
        draw.text(
            (box[0] + 20, box[1] + 16),
            title,
            font=font(22, bold=True),
            fill=COLORS["ink"],
        )
    return draw


def label(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    *,
    fill: tuple[int, int, int, int] = COLORS["ink"],
    size: int = 18,
    bold: bool = False,
) -> None:
    draw.text(xy, text, font=font(size, bold=bold), fill=fill)


def build_scale_study(master: Image.Image) -> Path:
    output = REVIEW_DIR / "dras-scale-study-v1.png"
    canvas = Image.new("RGBA", (1680, 1040), COLORS["panel"])
    draw = ImageDraw.Draw(canvas)
    label(
        draw,
        (44, 30),
        "SUPER FRGMNTS // DRAS EHDRE SCALE STUDY",
        size=34,
        bold=True,
    )
    label(
        draw,
        (46, 79),
        "Actual Outpost art • Aryn sprite at production size • three Dras candidates",
        fill=COLORS["muted"],
        size=18,
    )

    plate = Image.open(OUTPOST_PLATE).convert("RGBA")
    aryn = Image.open(ARYN_SPRITE).convert("RGBA")
    candidates = (
        (96, "QUIET / 96 PX", "Reads slightly frail"),
        (104, "CANONICAL / 104 PX", "Recommended: human scale + coat mass"),
        (112, "HEROIC / 112 PX", "Too dominant for the first meeting"),
    )
    card_width = 510
    for index, (height, heading, note) in enumerate(candidates):
        left = 44 + index * 544
        top = 124
        box = (left, top, left + card_width, 934)
        accent = COLORS["gold"] if height == 104 else COLORS["blue"]
        draw_panel(canvas, box, accent=accent)

        crop = plate.crop((0, 246, 660, 821)).resize(
            (466, 406), Image.Resampling.LANCZOS
        )
        scene = crop.convert("RGBA")
        scale = 406 / 575
        scaled_ground = round((GROUND_Y - 246) * scale)

        aryn_scaled = aryn.resize(
            (round(112 * scale), round(112 * scale)),
            Image.Resampling.LANCZOS,
        )
        actor = fit_actor(
            master,
            canvas_size=(96, 120),
            visible_height=height,
        )
        actor = actor.resize(
            (round(actor.width * scale), round(actor.height * scale)),
            Image.Resampling.LANCZOS,
        )
        place_actor(
            scene,
            aryn_scaled,
            88,
            ground_y=scaled_ground,
        )
        place_actor(
            scene,
            actor,
            250,
            ground_y=scaled_ground,
        )
        canvas.alpha_composite(scene, (left + 22, top + 72))

        label(draw, (left + 24, top + 500), heading, size=21, bold=True)
        label(
            draw,
            (left + 24, top + 536),
            note,
            fill=accent,
            size=16,
        )
        label(
            draw,
            (left + 24, top + 582),
            "Aryn: 112×112 draw canvas",
            fill=COLORS["muted"],
            size=15,
        )
        label(
            draw,
            (left + 24, top + 612),
            f"Dras: {height}px visible silhouette",
            fill=COLORS["muted"],
            size=15,
        )

        # Pixel ruler makes the choice reviewable rather than impressionistic.
        ruler_x = left + 414
        ruler_top = top + 532
        ruler_height = round(height * 1.4)
        draw.line(
            (ruler_x, ruler_top, ruler_x, ruler_top + ruler_height),
            fill=accent,
            width=3,
        )
        for tick in range(0, height + 1, 16):
            y = ruler_top + round(tick * 1.4)
            draw.line((ruler_x - 8, y, ruler_x + 8, y), fill=accent, width=2)

        if height == 104:
            draw.rounded_rectangle(
                (left + 24, top + 694, left + 245, top + 746),
                radius=6,
                fill=(217, 192, 140, 36),
                outline=COLORS["gold"],
                width=2,
            )
            label(
                draw,
                (left + 42, top + 708),
                "RECOMMENDED",
                fill=COLORS["panel"],
                size=17,
                bold=True,
            )

    label(
        draw,
        (46, 980),
        "Decision principle: Dras should feel weathered and substantial—not boss-sized.",
        fill=COLORS["light_blue"],
        size=18,
    )
    canvas.convert("RGB").save(output)
    return output


def build_outpost_placement(runtime: Image.Image) -> tuple[Path, Path]:
    composite_path = REVIEW_DIR / "dras-outpost-placement-v1.png"
    guide_path = REVIEW_DIR / "dras-outpost-placement-guide-v1.png"
    plate = Image.open(OUTPOST_PLATE).convert("RGBA")
    composite = plate.copy()
    place_actor(composite, runtime, DRAS_LOCAL_X)
    composite.convert("RGB").save(composite_path)

    guide = composite.copy()
    overlay = Image.new("RGBA", PLATE_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, 1672, 104), fill=(4, 8, 25, 224))
    label(
        draw,
        (24, 18),
        "DRAS OUTPOST // APPROACH & DISCOVERY ANCHOR",
        size=28,
        bold=True,
    )
    label(
        draw,
        (26, 61),
        "Aryn arrives from the west. Keep 208px of clean walking space before dialogue.",
        fill=COLORS["muted"],
        size=16,
    )
    draw.rounded_rectangle(
        (152, 544, 496, 744),
        radius=8,
        fill=(255, 105, 180, 23),
        outline=COLORS["pink"],
        width=3,
    )
    label(draw, (164, 558), "PROXIMITY DIALOGUE", fill=COLORS["pink"], size=15)
    draw.line((DRAS_LOCAL_X + 48, 626, DRAS_LOCAL_X + 48, 744), fill=COLORS["gold"], width=2)
    draw.ellipse(
        (DRAS_LOCAL_X + 42, 738, DRAS_LOCAL_X + 54, 750),
        fill=COLORS["gold"],
    )
    label(draw, (350, 650), "DRAS EHDRE", fill=COLORS["gold"], size=17, bold=True)
    draw.line((342, 672, DRAS_LOCAL_X + 60, 674), fill=COLORS["gold"], width=2)

    draw.rounded_rectangle(
        (428, 596, 772, 744),
        radius=8,
        fill=(99, 149, 238, 20),
        outline=COLORS["blue"],
        width=2,
    )
    label(draw, (444, 610), "CAMP PLACEHOLDER ZONE", fill=COLORS["light_blue"], size=15)
    draw.rounded_rectangle(
        (1232, 586, 1468, 744),
        radius=8,
        fill=(145, 175, 179, 20),
        outline=COLORS["cyan"],
        width=2,
    )
    label(draw, (1248, 600), "CREDIT TERMINAL", fill=COLORS["cyan"], size=15)

    guide = Image.alpha_composite(guide, overlay)
    guide.convert("RGB").save(guide_path)
    return composite_path, guide_path


def build_mobile_study(runtime: Image.Image) -> Path:
    output = REVIEW_DIR / "dras-mobile-discovery-study-v1.png"
    canvas = Image.new("RGBA", (1280, 1040), COLORS["panel"])
    draw = ImageDraw.Draw(canvas)
    label(draw, (48, 30), "PORTRAIT MOBILE // DRAS DISCOVERY", size=32, bold=True)
    label(
        draw,
        (50, 76),
        "540-world-pixel camera window • controls hidden during dialogue • safe-area aware",
        fill=COLORS["muted"],
        size=17,
    )

    plate = Image.open(OUTPOST_PLATE).convert("RGBA")
    scene = plate.copy()
    place_actor(scene, runtime, DRAS_LOCAL_X)
    aryn = Image.open(ARYN_SPRITE).convert("RGBA")
    place_actor(scene, aryn, 74)

    crop = scene.crop((0, 0, 540, 941))
    phone_w, phone_h = 430, 840
    scaled = crop.resize((430, 749), Image.Resampling.LANCZOS)

    for index, (x, title, note) in enumerate(
        (
            (
                92,
                "APPROACH",
                "Dras enters the right third before the prompt.",
            ),
            (
                758,
                "CONVERSATION",
                "Camera settles; actors remain visible above the panel.",
            ),
        )
    ):
        box = (x - 24, 126, x + phone_w + 24, 1004)
        draw.rounded_rectangle(
            box,
            radius=44,
            fill=(8, 10, 20, 255),
            outline=COLORS["plum"] if index else COLORS["blue"],
            width=4,
        )
        draw.rounded_rectangle(
            (x, 150, x + phone_w, 990),
            radius=28,
            fill=(2, 3, 10, 255),
        )
        canvas.alpha_composite(scaled, (x, 194))
        draw.rectangle((x, 150, x + phone_w, 194), fill=(4, 8, 25, 244))
        label(draw, (x + 18, 163), title, size=17, bold=True)
        draw.rectangle(
            (x, 857, x + phone_w, 943),
            fill=(4, 8, 25, 220),
        )
        label(
            draw,
            (x + 18, 872),
            note,
            fill=COLORS["ink"],
            size=13,
        )
        label(
            draw,
            (x + 18, 904),
            "Gameplay controls are suppressed here.",
            fill=COLORS["muted"],
            size=12,
        )
        # Top/bottom safe-area guides.
        draw.line((x + 16, 178, x + phone_w - 16, 178), fill=COLORS["pink"], width=1)
        draw.line((x + 16, 964, x + phone_w - 16, 964), fill=COLORS["pink"], width=1)

    canvas.convert("RGB").save(output)
    return output


def build_motion_contract(runtime: Image.Image) -> Path:
    output = REVIEW_DIR / "dras-idle-talk-motion-contract-v1.png"
    canvas = Image.new("RGBA", (1680, 900), COLORS["panel"])
    draw = ImageDraw.Draw(canvas)
    label(
        draw,
        (44, 28),
        "DRAS EHDRE // RESTRAINED IDLE & TALK MOTION CONTRACT",
        size=32,
        bold=True,
    )
    label(
        draw,
        (46, 72),
        "Planning frames only. Identity art remains unchanged until animation approval.",
        fill=COLORS["pink"],
        size=17,
    )

    ground = 430
    frames = (
        (0, 0.78, "REST"),
        (-1, 0.92, "INHALE"),
        (-1, 1.0, "LIGHT"),
        (0, 0.88, "SETTLE"),
        (1, 0.74, "WEIGHT"),
        (0, 0.78, "LOOP"),
    )
    scale = 2.45
    actor = runtime.resize(
        (round(runtime.width * scale), round(runtime.height * scale)),
        Image.Resampling.NEAREST,
    )
    for index, (offset, light, name) in enumerate(frames):
        left = 46 + index * 270
        box = (left, 124, left + 244, 520)
        draw.rounded_rectangle(
            box,
            radius=10,
            fill=COLORS["panel_soft"],
            outline=COLORS["blue"] if index not in (2, 5) else COLORS["gold"],
            width=2,
        )
        draw.line((left + 20, ground, left + 224, ground), fill=COLORS["plum"], width=2)
        x = left + (244 - actor.width) // 2
        y = ground - actor.height + round(offset * scale)
        canvas.alpha_composite(actor, (x, y))
        pulse_alpha = round(58 * light)
        draw.ellipse(
            (x + 70, y + 64, x + 91, y + 85),
            outline=(246, 194, 96, pulse_alpha),
            width=2,
        )
        label(draw, (left + 18, 468), f"{index + 1:02d} // {name}", size=15, bold=True)

    sections = (
        (
            46,
            "IDLE // 1600 MS",
            (
                "• Continuous six-pose rhythm; no held seam.",
                "• Body settles by only ±1 px at runtime.",
                "• Staff remains planted: age, weight, dignity.",
                "• Devices breathe below 12% luminance.",
            ),
            COLORS["cyan_bright"],
        ),
        (
            576,
            "TALK // EVENT-DRIVEN",
            (
                "• No constant mouth flap at this scale.",
                "• One restrained beard/shoulder accent per phrase.",
                "• Staff light answers key lore beats only.",
                "• Long pauses preserve Dras's patience and gravity.",
            ),
            COLORS["gold"],
        ),
        (
            1106,
            "ACCESSIBILITY",
            (
                "• Reduced motion uses the REST frame only.",
                "• Dialogue meaning never depends on light pulses.",
                "• Text remains complete in the accessibility tree.",
                "• Animation pauses with the page and game.",
            ),
            COLORS["pink"],
        ),
    )
    for left, heading, lines, accent in sections:
        draw.rounded_rectangle(
            (left, 566, left + 492, 842),
            radius=10,
            fill=COLORS["panel_soft"],
            outline=accent,
            width=2,
        )
        label(draw, (left + 20, 588), heading, fill=accent, size=19, bold=True)
        for line_index, line in enumerate(lines):
            label(
                draw,
                (left + 20, 636 + line_index * 43),
                line,
                fill=COLORS["ink"],
                size=15,
            )
    canvas.convert("RGB").save(output)
    return output


def build_identity_detail(master: Image.Image) -> Path:
    output = REVIEW_DIR / "dras-identity-fidelity-detail-v1.png"
    canvas = Image.new("RGBA", (1380, 900), COLORS["panel"])
    draw = ImageDraw.Draw(canvas)
    label(draw, (42, 30), "DRAS EHDRE // IDENTITY FIDELITY GATE", size=32, bold=True)
    label(
        draw,
        (44, 76),
        "Source crop → transparent master → actual runtime reduction",
        fill=COLORS["muted"],
        size=17,
    )

    source = Image.open(RAW_DIR / "dras-identity-crop-v1.png").convert("RGBA")
    source = source.resize((280, 740), Image.Resampling.LANCZOS)
    canvas.alpha_composite(source, (54, 128))

    checker = Image.new("RGBA", (420, 740), (18, 21, 32, 255))
    check_draw = ImageDraw.Draw(checker)
    for y in range(0, 740, 32):
        for x in range(0, 420, 32):
            if (x // 32 + y // 32) % 2:
                check_draw.rectangle((x, y, x + 31, y + 31), fill=(31, 35, 49, 255))
    large = master.copy()
    large.thumbnail((390, 700), Image.Resampling.LANCZOS)
    checker.alpha_composite(
        large,
        ((checker.width - large.width) // 2, checker.height - large.height - 18),
    )
    canvas.alpha_composite(checker, (430, 128))

    runtime = Image.open(RUNTIME).convert("RGBA").resize(
        (384, 448), Image.Resampling.NEAREST
    )
    canvas.alpha_composite(runtime, (938, 216))
    label(draw, (54, 844), "IDENTITY AUTHORITY", fill=COLORS["gold"], size=17, bold=True)
    label(draw, (430, 844), "CLEAN MASTER", fill=COLORS["cyan_bright"], size=17, bold=True)
    label(draw, (938, 684), "4× RUNTIME PIXELS", fill=COLORS["light_blue"], size=17, bold=True)
    label(
        draw,
        (938, 724),
        "96×112 canvas\n104px visible silhouette",
        fill=COLORS["muted"],
        size=15,
    )
    canvas.convert("RGB").save(output)
    return output


def write_manifest(master: Image.Image, runtime: Image.Image) -> Path:
    output = DRAS_DIR / "dras-revision-3b-manifest.json"
    aryn = Image.open(ARYN_SPRITE).convert("RGBA")
    manifest = {
        "revision": "3B",
        "status": "review-candidate-unapproved",
        "character": {
            "name": "Dras Ehdre",
            "identity_authority": str(RAW_DIR / "dras-identity-crop-v1.png"),
            "transparent_master": str(MASTER),
            "master_size": list(master.size),
        },
        "runtime_candidate": {
            "asset": str(RUNTIME),
            "canvas": list(runtime.size),
            "visible_height": DRAS_VISIBLE_HEIGHT,
            "world_anchor_local_plate_2": {
                "x": DRAS_LOCAL_X,
                "ground_y": GROUND_Y,
            },
            "aryn_draw_canvas": list(aryn.size),
            "recommendation": (
                "Use 104px visible height inside a 96x112 transparent canvas. "
                "This keeps Dras human-scaled while preserving the coat's mass."
            ),
        },
        "motion_contract": {
            "status": "planning-only",
            "idle_duration_ms": 1600,
            "vertical_travel_px": 1,
            "loop": "continuous; no held end frame",
            "staff": "planted",
            "reduced_motion": "static REST frame",
        },
        "scope": {
            "live_game_modified": False,
            "integrated": False,
            "committed": False,
        },
    }
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return output


def build_reviews() -> list[Path]:
    for path in (ASSET_DIR, REVIEW_DIR):
        path.mkdir(parents=True, exist_ok=True)
    master = trim_transparent_master()
    runtime = build_runtime(master)
    outputs = [
        MASTER,
        RUNTIME,
        build_scale_study(master),
        *build_outpost_placement(runtime),
        build_mobile_study(runtime),
        build_motion_contract(runtime),
        build_identity_detail(master),
        write_manifest(master, runtime),
    ]
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prepare-identity",
        action="store_true",
        help="Crop the selected Dras identity pose from the source strip.",
    )
    parser.add_argument(
        "--build-reviews",
        action="store_true",
        help="Build the transparent master, runtime candidate, and review sheets.",
    )
    args = parser.parse_args()

    if not args.prepare_identity and not args.build_reviews:
        parser.error("Choose an explicit build action.")

    if args.prepare_identity:
        print(prepare_identity_crop())
    if args.build_reviews:
        for output in build_reviews():
            print(output)


if __name__ == "__main__":
    main()
