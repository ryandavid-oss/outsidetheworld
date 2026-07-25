#!/usr/bin/env python3
"""Build Revision 3D Dras Outpost blocking and flow approval sheets.

Design-only. No live game files are modified.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OVERWORLD = ROOT / "Design/Super-Frgmnts/Overworld"
OUTPOST_DIR = OVERWORLD / "Phase-3/Outpost"
REVIEW_DIR = OUTPOST_DIR / "Reviews"
PLATE = OVERWORLD / "Production/Plates/overworld-dras-outpost-v1.png"
DRAS = OVERWORLD / "Phase-3/Dras/Assets/dras-runtime-candidate-v1.png"
ARYN = ROOT / "Images/Builder/signal-ranger-idle-focused-v2.png"
FIELD_DESKTOP = (
    OVERWORLD
    / "Phase-3/Dialogue/Reviews/dialogue-field-relay-desktop-v1.png"
)
FIELD_MOBILE = (
    OVERWORLD
    / "Phase-3/Dialogue/Reviews/dialogue-field-relay-mobile-v1.png"
)

FONT_PATH = "/System/Library/Fonts/SFNSMono.ttf"
FONT_BOLD_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
GROUND_Y = 744
DRAS_X = 280

COLORS = {
    "void": (5, 6, 12, 255),
    "panel": (5, 9, 24, 245),
    "ink": (238, 238, 238, 255),
    "soft": (160, 190, 245, 255),
    "blue": (99, 149, 238, 255),
    "teal": (145, 175, 179, 255),
    "cyan": (83, 240, 225, 255),
    "gold": (217, 192, 140, 255),
    "pink": (255, 105, 180, 255),
    "green": (75, 227, 110, 255),
    "amethyst": (155, 89, 182, 255),
}

ZONES = {
    "arrival_runway": (0, 560, 152, 744),
    "first_contact": (152, 560, 496, 744),
    "camp_placeholder": (428, 596, 772, 744),
    "credit_terminal": (1232, 586, 1468, 744),
    "east_release": (1468, 560, 1672, 744),
    "walk_lane": (0, 670, 1672, 744),
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


def actor_shadow() -> Image.Image:
    shadow = Image.new("RGBA", (72, 12), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.ellipse((0, 2, 71, 11), fill=(2, 2, 12, 70))
    return shadow.filter(ImageFilter.GaussianBlur(0.6))


def place_actor(scene: Image.Image, actor: Image.Image, x: int) -> None:
    shadow = actor_shadow()
    scene.alpha_composite(
        shadow,
        (x + actor.width // 2 - shadow.width // 2, GROUND_Y - 7),
    )
    scene.alpha_composite(actor, (x, GROUND_Y - actor.height))


def scene_with_actors(aryn_x: int) -> Image.Image:
    scene = Image.open(PLATE).convert("RGBA")
    place_actor(scene, Image.open(ARYN).convert("RGBA"), aryn_x)
    place_actor(scene, Image.open(DRAS).convert("RGBA"), DRAS_X)
    return scene


def zone_overlay(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    name: str,
    color: tuple[int, int, int, int],
    *,
    fill_alpha: int = 24,
) -> None:
    left, top, right, bottom = box
    draw.rounded_rectangle(
        box,
        radius=7,
        fill=(*color[:3], fill_alpha),
        outline=color,
        width=2,
    )
    label(draw, (left + 12, top + 10), name, size=14, fill=color, bold=True)


def build_map() -> Path:
    output = REVIEW_DIR / "outpost-blocking-map-v1.png"
    scene = scene_with_actors(54)
    overlay = Image.new("RGBA", scene.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, 1672, 110), fill=COLORS["panel"])
    label(draw, (24, 18), "DRAS OUTPOST // BLOCKING MAP", size=29, bold=True)
    label(
        draw,
        (26, 62),
        "Story rhythm: arrive → notice → settle → listen → release east",
        size=16,
        fill=COLORS["soft"],
    )

    zone_overlay(draw, ZONES["arrival_runway"], "ARRIVAL RUNWAY", COLORS["blue"])
    zone_overlay(
        draw,
        ZONES["first_contact"],
        "FIRST-CONTACT TRIGGER",
        COLORS["pink"],
    )
    zone_overlay(
        draw,
        ZONES["camp_placeholder"],
        "CAMP PLACEHOLDER",
        COLORS["gold"],
    )
    zone_overlay(
        draw,
        ZONES["credit_terminal"],
        "TERMINAL PLACEHOLDER",
        COLORS["teal"],
    )
    zone_overlay(
        draw,
        ZONES["east_release"],
        "EAST RELEASE",
        COLORS["green"],
    )
    left, top, right, bottom = ZONES["walk_lane"]
    draw.rectangle(
        (left, top, right, bottom),
        fill=(83, 240, 225, 16),
        outline=COLORS["cyan"],
        width=2,
    )
    label(draw, (810, 708), "CONTINUOUS WALKING LANE", size=14, fill=COLORS["cyan"], bold=True)

    # First portrait-mobile camera hold: Dras lands in the right third.
    draw.rectangle((0, 128, 540, 744), outline=COLORS["amethyst"], width=3)
    label(draw, (18, 140), "MOBILE CAMERA HOLD // 540 WORLD PX", size=14, fill=COLORS["amethyst"], bold=True)

    # Exact anchor and pacing measures.
    draw.line((0, 520, DRAS_X, 520), fill=COLORS["gold"], width=2)
    draw.line((0, 512, 0, 528), fill=COLORS["gold"], width=2)
    draw.line((DRAS_X, 512, DRAS_X, 528), fill=COLORS["gold"], width=2)
    label(draw, (74, 488), "280 PX TO DRAS", size=14, fill=COLORS["gold"], bold=True)
    draw.line((152, 544, 496, 544), fill=COLORS["pink"], width=2)
    label(draw, (226, 514), "344 PX TRIGGER", size=13, fill=COLORS["pink"])

    map_image = Image.alpha_composite(scene, overlay)
    map_image.convert("RGB").save(output)
    return output


def framed_strip(
    canvas: Image.Image,
    image: Image.Image,
    *,
    box: tuple[int, int, int, int],
    heading: str,
    note: str,
    accent: tuple[int, int, int, int],
) -> None:
    draw = ImageDraw.Draw(canvas)
    left, top, right, bottom = box
    draw.rounded_rectangle(
        box,
        radius=10,
        fill=COLORS["panel"],
        outline=accent,
        width=2,
    )
    label(draw, (left + 18, top + 14), heading, size=20, fill=accent, bold=True)
    label(draw, (left + 246, top + 17), note, size=14, fill=COLORS["soft"])
    target = (right - left - 36, bottom - top - 62)
    fitted = image.copy()
    fitted.thumbnail(target, Image.Resampling.LANCZOS)
    canvas.alpha_composite(
        fitted,
        (
            left + 18 + (target[0] - fitted.width) // 2,
            top + 48 + (target[1] - fitted.height) // 2,
        ),
    )


def build_desktop_sequence() -> Path:
    output = REVIEW_DIR / "outpost-desktop-sequence-v1.png"
    canvas = Image.new("RGBA", (1780, 1540), COLORS["void"])
    draw = ImageDraw.Draw(canvas)
    label(draw, (46, 28), "DRAS OUTPOST // DESKTOP STORY SEQUENCE", size=32, bold=True)
    label(
        draw,
        (48, 74),
        "No final camp or terminal art is introduced in this pass.",
        size=17,
        fill=COLORS["pink"],
    )

    # Storyboard strips favor actor staging over the full atmospheric plate. The
    # full-height world remains visible in the blocking map and mobile study.
    approach = scene_with_actors(54).crop((0, 382, 1672, 822))
    conversation = Image.open(FIELD_DESKTOP).convert("RGBA").crop(
        (0, 490, 1672, 921)
    )
    release = scene_with_actors(868).crop((0, 382, 1672, 822))

    framed_strip(
        canvas,
        approach,
        box=(46, 118, 1734, 548),
        heading="01 // APPROACH",
        note="First visit: automatic, gentle trigger after Aryn enters the zone.",
        accent=COLORS["blue"],
    )
    framed_strip(
        canvas,
        conversation,
        box=(46, 574, 1734, 1082),
        heading="02 // SETTLE & LISTEN",
        note="Camera lifts both actors; simulation and gameplay input pause.",
        accent=COLORS["gold"],
    )
    framed_strip(
        canvas,
        release,
        box=(46, 1108, 1734, 1490),
        heading="03 // RELEASE EAST",
        note="Camera returns smoothly; camp and terminal become the next discoveries.",
        accent=COLORS["green"],
    )
    canvas.convert("RGB").save(output)
    return output


def phone_frame(
    canvas: Image.Image,
    scene: Image.Image,
    x: int,
    *,
    heading: str,
    accent: tuple[int, int, int, int],
    note: str,
) -> None:
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (x, 126, x + 430, 1058),
        radius=38,
        fill=(3, 4, 12, 255),
        outline=accent,
        width=4,
    )
    canvas.alpha_composite(scene, (x, 126))
    label(draw, (x + 18, 1078), heading, size=19, fill=accent, bold=True)
    draw.multiline_text(
        (x + 18, 1114),
        note,
        font=font(13),
        fill=COLORS["soft"],
        spacing=5,
    )


def mobile_world_crop(camera_x: int, aryn_x: int) -> Image.Image:
    scene = scene_with_actors(aryn_x)
    crop = scene.crop((camera_x, 0, camera_x + 540, 941))
    phone = Image.new("RGBA", (430, 932), COLORS["void"])
    world = crop.resize((430, 749), Image.Resampling.LANCZOS)
    phone.alpha_composite(world, (0, 92))
    draw = ImageDraw.Draw(phone)
    draw.rectangle((0, 0, 430, 92), fill=COLORS["panel"])
    label(draw, (18, 28), "SUPER FRGMNTS // OUTPOST", size=15, bold=True)
    draw.line((18, 68, 412, 68), fill=COLORS["pink"], width=1)
    draw.rectangle((0, 841, 430, 932), fill=COLORS["panel"])
    label(draw, (18, 862), "CONTROLS ACTIVE", size=12, fill=COLORS["teal"], bold=True)
    label(draw, (18, 894), "Camera follows Aryn horizontally.", size=12, fill=COLORS["soft"])
    return phone


def build_mobile_sequence() -> Path:
    output = REVIEW_DIR / "outpost-mobile-sequence-v1.png"
    canvas = Image.new("RGBA", (1510, 1230), COLORS["void"])
    draw = ImageDraw.Draw(canvas)
    label(draw, (46, 28), "PORTRAIT MOBILE // OUTPOST FLOW", size=32, bold=True)
    label(
        draw,
        (48, 74),
        "The conversation removes the thumb problem entirely: controls hide while paused.",
        size=17,
        fill=COLORS["soft"],
    )

    approach = mobile_world_crop(0, 54)
    conversation = Image.open(FIELD_MOBILE).convert("RGBA")
    release = mobile_world_crop(320, 668)
    phone_frame(
        canvas,
        approach,
        46,
        heading="01 // APPROACH",
        accent=COLORS["blue"],
        note="Dras enters the right third.\nControls remain active.",
    )
    phone_frame(
        canvas,
        conversation,
        540,
        heading="02 // CONVERSATION",
        accent=COLORS["gold"],
        note="Actors remain visible.\nControls are fully suppressed.",
    )
    phone_frame(
        canvas,
        release,
        1034,
        heading="03 // RELEASE",
        accent=COLORS["green"],
        note="Camera resumes tracking.\nTerminal becomes the next landmark.",
    )
    canvas.convert("RGB").save(output)
    return output


def build_contact_sheet(map_path: Path, desktop_path: Path, mobile_path: Path) -> Path:
    output = REVIEW_DIR / "outpost-blocking-contact-sheet-v1.png"
    canvas = Image.new("RGBA", (1800, 1570), COLORS["void"])
    draw = ImageDraw.Draw(canvas)
    label(draw, (46, 28), "REVISION 3D // DRAS OUTPOST APPROVAL PACKET", size=34, bold=True)
    label(
        draw,
        (48, 76),
        "World blocking first. Final camp art, terminal behavior, and canon copy remain separate decisions.",
        size=17,
        fill=COLORS["soft"],
    )
    map_image = Image.open(map_path).convert("RGBA").resize(
        (1708, 961), Image.Resampling.LANCZOS
    )
    canvas.alpha_composite(map_image, (46, 120))
    desktop = Image.open(desktop_path).convert("RGBA")
    desktop.thumbnail((820, 420), Image.Resampling.LANCZOS)
    canvas.alpha_composite(desktop, (46, 1120))
    mobile = Image.open(mobile_path).convert("RGBA")
    mobile.thumbnail((820, 420), Image.Resampling.LANCZOS)
    canvas.alpha_composite(mobile, (930, 1120))
    label(draw, (46, 1090), "DESKTOP STORY BEATS", size=17, fill=COLORS["gold"], bold=True)
    label(draw, (930, 1090), "MOBILE CAMERA & INPUT", size=17, fill=COLORS["teal"], bold=True)
    canvas.convert("RGB").save(output)
    return output


def write_contract() -> Path:
    output = OUTPOST_DIR / "OUTPOST-BLOCKING-CONTRACT.md"
    output.write_text(
        """# Dras Outpost blocking contract

Status: Revision 3D review candidate. Design-only; not integrated.

## First visit

- Aryn enters from the west with controls active.
- Dras becomes readable in the right third before dialogue begins.
- Crossing the first-contact zone initiates one automatic conversation after a
  short camera settle; it never triggers during a jump or fall.
- The simulation, timer, ambient threats, and actor input pause.
- The conversation camera lifts both actors into the upper safe band.
- Touch controls disappear. Desktop controls are ignored except dialogue input.
- Closing dialogue eases back to gameplay and releases the camera east.

## Return visits

- No automatic interruption.
- A compact `TALK` prompt appears inside the proximity zone.
- Dras remains non-damaging and non-solid so he never seals the only route.
- The prompt and speaker name are text; neither relies on color alone.

## Spatial contract

- Dras anchor: plate-two local X 280, feet at Y 744.
- Arrival runway: X 0–152.
- First-contact zone: X 152–496.
- Camp placeholder: X 428–772.
- Abandoned credit-terminal placeholder: X 1232–1468.
- Continuous walk lane: Y 670–744 across the entire plate.
- Portrait mobile first-contact camera: 540 world pixels wide, held at local X 0.

## Boundaries

- Camp props are placeholders in this pass.
- Terminal behavior, currency economy, final lore copy, voice, and facial
  animation are out of scope.
- No live game file, deployment, or production collision is changed.
""",
        encoding="utf-8",
    )
    return output


def write_manifest(paths: dict[str, Path]) -> Path:
    output = OUTPOST_DIR / "outpost-revision-3d-manifest.json"
    manifest = {
        "revision": "3D",
        "status": "review-candidate-unapproved",
        "anchors_local_plate_2": {
            "dras": {"x": DRAS_X, "feet_y": GROUND_Y},
            "zones": {key: list(value) for key, value in ZONES.items()},
        },
        "first_visit": {
            "trigger": "automatic after grounded camera settle",
            "simulation": "paused",
            "controls": "suppressed",
            "dialogue_direction": "field-relay",
        },
        "return_visit": {
            "trigger": "manual TALK prompt",
            "npc_collision": "non-solid",
        },
        "reviews": {key: str(value) for key, value in paths.items()},
        "scope": {
            "live_game_modified": False,
            "integrated": False,
            "committed": False,
            "camp_art_final": False,
            "terminal_behavior_final": False,
        },
    }
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return output


def main() -> None:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    paths = {
        "map": build_map(),
        "desktop_sequence": build_desktop_sequence(),
        "mobile_sequence": build_mobile_sequence(),
    }
    paths["contact_sheet"] = build_contact_sheet(
        paths["map"],
        paths["desktop_sequence"],
        paths["mobile_sequence"],
    )
    outputs = [*paths.values(), write_contract(), write_manifest(paths)]
    for output in outputs:
        print(output)


if __name__ == "__main__":
    main()
