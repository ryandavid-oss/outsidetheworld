#!/usr/bin/env python3
"""Build the design-only Revision 3A.1 ship collision and gangway review."""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SHIP_DIR = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Overworld"
    / "Phase-3"
    / "Ship"
)
OUTPUT_DIR = SHIP_DIR / "Collision"
LANDING_PLATE = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Overworld"
    / "Production"
    / "Plates"
    / "overworld-landing-flats-v1.png"
)
SHIP_ASSET = SHIP_DIR / "Assets" / "aryn-ship-transparent-v1.png"
HOVER_FIELD = SHIP_DIR / "Assets" / "aryn-ship-hover-field-v1.png"
ARYN_SPRITE = ROOT / "Images" / "Builder" / "signal-ranger-idle-focused-v2.png"
SHIP_MANIFEST = SHIP_DIR / "ship-revision-3a-manifest.json"

DEPLOYED_CONCEPT = OUTPUT_DIR / "ship-gangway-deployed-concept-v1.png"
COLLISION_GUIDE = OUTPUT_DIR / "ship-collision-revision-3a1-guide-v1.png"
ROUTE_DETAIL = OUTPUT_DIR / "ship-collision-route-detail-v1.png"
CONTACT_SHEET = OUTPUT_DIR / "ship-collision-revision-3a1-contact-sheet-v1.png"
MANIFEST = OUTPUT_DIR / "ship-collision-revision-3a1-manifest.json"

WORLD_WIDTH = 1672
WORLD_HEIGHT = 941
GROUND_Y = 744
PLAYER_COLLISION_HEIGHT = 100
PLAYER_COLLISION_WIDTH = 44
JUMP_VELOCITY = -790
GRAVITY = 2050
JUMP_APEX_RISE = JUMP_VELOCITY * JUMP_VELOCITY / (2 * GRAVITY)

FONT_PATH = "/System/Library/Fonts/SFNSMono.ttf"
FONT_BOLD_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

COLORS = {
    "ink": (246, 241, 245, 255),
    "muted": (181, 192, 218, 255),
    "cyan": (83, 240, 225, 255),
    "cyan_fill": (26, 135, 132, 92),
    "magenta": (239, 89, 174, 255),
    "gold": (247, 194, 96, 255),
    "gold_fill": (121, 77, 32, 210),
    "blue": (127, 170, 255, 255),
    "blue_fill": (68, 99, 177, 56),
    "panel": (4, 8, 25, 255),
    "panel_soft": (8, 14, 36, 244),
    "shell": (8, 11, 27, 255),
}

TRIGGER_ZONE = {
    "x": 1040,
    "y": 596,
    "width": 120,
    "height": 148,
    "player_center_right": 1160,
}
PROPOSED_ARYN_PLACEMENT = {
    "x": 1120,
    "y": 632,
    "width": 112,
    "height": 112,
    "center_x": 1176,
    "previous_x": 1000,
}

SURFACES = [
    {
        "id": "gangway_lower",
        "label": "LOWER TREAD",
        "x": 918,
        "y": 704,
        "width": 72,
        "height": 10,
        "kind": "deployed-gangway",
    },
    {
        "id": "gangway_middle",
        "label": "MIDDLE TREAD",
        "x": 888,
        "y": 668,
        "width": 80,
        "height": 10,
        "kind": "deployed-gangway",
    },
    {
        "id": "gangway_upper",
        "label": "UPPER TREAD",
        "x": 856,
        "y": 632,
        "width": 88,
        "height": 10,
        "kind": "deployed-gangway",
    },
    {
        "id": "ship_boarding_deck",
        "label": "BOARDING DECK",
        "x": 814,
        "y": 600,
        "width": 128,
        "height": 12,
        "kind": "deployed-gangway",
    },
    {
        "id": "ship_dorsal_step",
        "label": "DORSAL STEP",
        "x": 716,
        "y": 520,
        "width": 112,
        "height": 10,
        "kind": "hull-traction-pad",
    },
    {
        "id": "ship_cockpit_perch",
        "label": "COCKPIT PERCH",
        "x": 528,
        "y": 448,
        "width": 176,
        "height": 10,
        "kind": "hull-traction-pad",
    },
]


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD_PATH if bold else FONT_PATH, size)


def build_base_composite() -> Image.Image:
    """Rebuild the approved ship scene with the proposed safer spawn spacing."""
    ship_manifest = json.loads(SHIP_MANIFEST.read_text(encoding="utf-8"))
    placement = ship_manifest["placement"]
    plate = Image.open(LANDING_PLATE).convert("RGBA")
    ship = Image.open(SHIP_ASSET).convert("RGBA").resize(
        (
            placement["ship"]["width"],
            placement["ship"]["height"],
        ),
        Image.Resampling.LANCZOS,
    )
    hover_field = Image.open(HOVER_FIELD).convert("RGBA")
    aryn = Image.open(ARYN_SPRITE).convert("RGBA")
    plate.alpha_composite(
        hover_field,
        (
            placement["shadow"]["x"],
            placement["shadow"]["y"],
        ),
    )
    plate.alpha_composite(
        ship,
        (
            placement["ship"]["x"],
            placement["ship"]["y"],
        ),
    )
    plate.alpha_composite(
        aryn,
        (
            PROPOSED_ARYN_PLACEMENT["x"],
            PROPOSED_ARYN_PLACEMENT["y"],
        ),
    )
    return plate


def draw_tread(
    draw: ImageDraw.ImageDraw,
    surface: dict,
    *,
    opacity: int = 255,
) -> None:
    x = surface["x"]
    y = surface["y"]
    width = surface["width"]
    height = surface["height"]
    shell = (*COLORS["shell"][:3], opacity)
    gold_fill = (*COLORS["gold_fill"][:3], min(opacity, COLORS["gold_fill"][3]))
    cyan = (*COLORS["cyan"][:3], opacity)
    draw.rounded_rectangle(
        (x, y, x + width, y + height),
        radius=3,
        fill=shell,
        outline=(*COLORS["gold"][:3], opacity),
        width=2,
    )
    draw.rectangle(
        (x + 5, y + 3, x + width - 5, y + height - 2),
        fill=gold_fill,
    )
    draw.line((x + 6, y, x + width - 6, y), fill=cyan, width=2)


def draw_gangway_art(image: Image.Image) -> Image.Image:
    """Draw a structural placeholder for the deployable gangway and traction pads."""
    result = image.copy()
    overlay = Image.new("RGBA", result.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Telescoping struts connect the treads without pretending to be final art.
    gangway = SURFACES[:4]
    for upper, lower in zip(gangway, gangway[1:]):
        upper_center = (
            upper["x"] + upper["width"] // 2,
            upper["y"] + upper["height"],
        )
        lower_center = (
            lower["x"] + lower["width"] // 2,
            lower["y"],
        )
        draw.line(
            (upper_center, lower_center),
            fill=(83, 240, 225, 180),
            width=5,
        )
        draw.line(
            (
                upper_center[0] + 8,
                upper_center[1],
                lower_center[0] + 8,
                lower_center[1],
            ),
            fill=(247, 194, 96, 150),
            width=3,
        )

    # The hinge sits under the outer-right wing and shares the ship's bob.
    draw.ellipse((805, 582, 835, 612), fill=COLORS["shell"], outline=COLORS["cyan"], width=3)
    draw.ellipse((814, 591, 826, 603), fill=COLORS["gold"])

    for surface in SURFACES:
        draw_tread(draw, surface)

    result = Image.alpha_composite(result, overlay)
    return result


def label_box(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    color: tuple[int, int, int, int],
    *,
    size: int = 16,
) -> None:
    x, y = xy
    label_font = font(size)
    bounds = draw.textbbox((x, y), text, font=label_font)
    draw.rounded_rectangle(
        (bounds[0] - 6, bounds[1] - 4, bounds[2] + 6, bounds[3] + 5),
        radius=3,
        fill=(3, 7, 20, 224),
        outline=color,
        width=2,
    )
    draw.text((x, y), text, font=label_font, fill=color)


def draw_arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple[int, int, int, int],
    *,
    width: int = 3,
) -> None:
    draw.line((*start, *end), fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    length = 12
    for delta in (-0.55, 0.55):
        draw.line(
            (
                end[0],
                end[1],
                end[0] - math.cos(angle + delta) * length,
                end[1] - math.sin(angle + delta) * length,
            ),
            fill=color,
            width=width,
        )


def build_collision_guide(deployed: Image.Image) -> Image.Image:
    guide = deployed.copy()
    overlay = Image.new("RGBA", guide.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    zone = TRIGGER_ZONE
    draw.rectangle(
        (
            zone["x"],
            zone["y"],
            zone["x"] + zone["width"],
            zone["y"] + zone["height"],
        ),
        fill=COLORS["blue_fill"],
        outline=COLORS["blue"],
        width=3,
    )
    label_box(
        draw,
        (zone["x"] - 24, zone["y"] - 34),
        "MOVE LEFT 16 PX → DEPLOY",
        COLORS["blue"],
    )

    for index, surface in enumerate(SURFACES):
        x = surface["x"]
        y = surface["y"]
        width = surface["width"]
        draw.rectangle(
            (x, y - 3, x + width, y + 3),
            fill=COLORS["cyan_fill"],
            outline=COLORS["cyan"],
            width=2,
        )
        label_x = x - 10 if index < 4 else x
        label_y = y + 17 if index % 2 == 0 else y - 31
        label_box(draw, (label_x, label_y), surface["label"], COLORS["cyan"], size=13)

    route_centers = [
        (1056, GROUND_Y),
        *[
            (surface["x"] + surface["width"] // 2, surface["y"])
            for surface in SURFACES
        ],
    ]
    for start, end in zip(route_centers, route_centers[1:]):
        draw_arrow(draw, start, end, COLORS["magenta"], width=3)

    # Physics-accurate expert shortcut from Aryn's start to the boarding deck.
    start_x = 1056
    start_y = GROUND_Y
    velocity_x = -372
    velocity_y = JUMP_VELOCITY
    points: list[tuple[int, int]] = []
    for step in range(25):
        time = step * 0.02
        x = start_x + velocity_x * time
        y = start_y + velocity_y * time + 0.5 * GRAVITY * time * time
        points.append((round(x), round(y)))
    draw.line(points, fill=COLORS["gold"], width=3)
    label_box(
        draw,
        (1000, 546),
        "EXPERT SHORTCUT // 144 PX RISE",
        COLORS["gold"],
        size=14,
    )

    label_box(
        draw,
        (26, 24),
        "REVISION 3A.1 // DEPLOYABLE SHIP TUTORIAL",
        COLORS["ink"],
        size=23,
    )
    label_box(
        draw,
        (26, 65),
        "CYAN = ONE-WAY SURFACE  //  MAGENTA = FORGIVING ROUTE  //  GOLD = SKILL JUMP",
        COLORS["muted"],
        size=14,
    )

    guide = Image.alpha_composite(guide, overlay)
    guide.save(COLLISION_GUIDE)
    return guide


def build_route_detail(guide: Image.Image) -> Image.Image:
    detail = guide.crop((480, 380, 1320, 800))
    detail = detail.resize((1344, 672), Image.Resampling.LANCZOS)
    detail.save(ROUTE_DETAIL)
    return detail


def fit(image: Image.Image, bounds: tuple[int, int]) -> Image.Image:
    width, height = bounds
    scale = min(width / image.width, height / image.height)
    return image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )


def build_contact_sheet(
    deployed: Image.Image,
    guide: Image.Image,
    detail: Image.Image,
) -> Image.Image:
    sheet = Image.new("RGBA", (1900, 1800), COLORS["panel"])
    draw = ImageDraw.Draw(sheet)

    draw.text(
        (72, 42),
        "SUPER FRGMNTS // REVISION 3A.1",
        font=font(36, bold=True),
        fill=COLORS["ink"],
    )
    draw.text(
        (74, 92),
        "SHIP COLLISION + PROXIMITY GANGWAY // APPROVAL IMAGE",
        font=font(21),
        fill=COLORS["cyan"],
    )
    draw.text(
        (74, 126),
        "Design-only geometry. The gangway art shown here is a structural placeholder.",
        font=font(17),
        fill=COLORS["muted"],
    )

    panels = [
        (
            (72, 170, 1828, 1110),
            "01 // DEPLOYED IN THE LANDING FLATS",
            deployed,
            (1672, 840),
        ),
        (
            (72, 1140, 1230, 1730),
            "02 // COLLISION + ROUTE LOGIC",
            detail,
            (1102, 480),
        ),
    ]
    for bounds, title, image, image_bounds in panels:
        left, top, right, bottom = bounds
        draw.rounded_rectangle(
            bounds,
            radius=14,
            fill=COLORS["panel_soft"],
            outline=(53, 72, 119, 255),
            width=2,
        )
        draw.text(
            (left + 24, top + 20),
            title,
            font=font(21, bold=True),
            fill=COLORS["ink"],
        )
        fitted = fit(image, image_bounds)
        x = left + (right - left - fitted.width) // 2
        y = top + 66
        sheet.alpha_composite(fitted, (x, y))

    draw.rounded_rectangle(
        (1260, 1140, 1828, 1730),
        radius=14,
        fill=COLORS["panel_soft"],
        outline=(53, 72, 119, 255),
        width=2,
    )
    draw.text(
        (1286, 1162),
        "03 // WHAT IT TEACHES",
        font=font(21, bold=True),
        fill=COLORS["ink"],
    )
    notes = [
        ("APPROACH", "The ship responds when Aryn turns back toward it."),
        ("JUMP", "Three forgiving treads establish vertical movement."),
        ("MASTERY", "A near-limit jump can skip directly to the deck."),
        ("DROP", "Down passes through every ship surface consistently."),
        ("MOTION", "Ship, ramp, colliders, and supported Aryn bob together."),
        ("SAFETY", "The gangway remains deployed once opened."),
    ]
    y = 1222
    for heading, body in notes:
        draw.text(
            (1288, y),
            heading,
            font=font(17, bold=True),
            fill=COLORS["gold"],
        )
        draw.multiline_text(
            (1288, y + 28),
            body,
            font=font(15),
            fill=COLORS["muted"],
            spacing=5,
        )
        y += 80

    sheet.save(CONTACT_SHEET)
    return sheet


def write_manifest() -> None:
    ship_manifest = json.loads(SHIP_MANIFEST.read_text(encoding="utf-8"))
    ship_motion = ship_manifest["hover_motion_proof"]
    steps = []
    previous_y = GROUND_Y
    for surface in SURFACES:
        rise = previous_y - surface["y"]
        steps.append(
            {
                **surface,
                "type": "one-way-moving-platform",
                "rise_from_previous": rise,
                "normal_route": True,
                "drop_through": True,
                "motion_group": "aryn_ship_hover",
            }
        )
        previous_y = surface["y"]

    data = {
        "revision": "3A.1",
        "status": "approved",
        "approval": {
            "approved_on": "2026-07-25",
            "approved_revision": "ship-collision-revision-3a1",
        },
        "scope": "Ship collision surfaces and proximity-deployed boarding gangway",
        "live_game_modified": False,
        "design_intent": (
            "Make the first major environment prop conquerable so the player "
            "learns that illustrated machinery can be traversed."
        ),
        "physics_reference": {
            "jump_velocity": JUMP_VELOCITY,
            "gravity": GRAVITY,
            "theoretical_jump_apex_rise": round(JUMP_APEX_RISE, 2),
            "player_collision_width": PLAYER_COLLISION_WIDTH,
            "player_collision_height": PLAYER_COLLISION_HEIGHT,
            "normal_route_max_rise": max(step["rise_from_previous"] for step in steps),
            "expert_shortcut": {
                "from": "desert_floor",
                "to": "ship_boarding_deck",
                "rise": GROUND_Y
                - next(
                    surface["y"]
                    for surface in SURFACES
                    if surface["id"] == "ship_boarding_deck"
                ),
                "apex_margin": round(
                    JUMP_APEX_RISE
                    - (
                        GROUND_Y
                        - next(
                            surface["y"]
                            for surface in SURFACES
                            if surface["id"] == "ship_boarding_deck"
                        )
                    ),
                    2,
                ),
                "requires_running_jump": True,
            },
        },
        "trigger": {
            **TRIGGER_ZONE,
            "condition": (
                "Deploy once Aryn's collision center moves left of x=1160 "
                "while grounded; her proposed spawn center is x=1176."
            ),
            "deploy_duration_ms": 450,
            "colliders_activate_at_progress": 0.9,
            "persists_for_scene": True,
            "retract_while_occupied": False,
        },
        "spawn_adjustment": {
            "from": {
                "x": PROPOSED_ARYN_PLACEMENT["previous_x"],
                "y": PROPOSED_ARYN_PLACEMENT["y"],
            },
            "to": {
                "x": PROPOSED_ARYN_PLACEMENT["x"],
                "y": PROPOSED_ARYN_PLACEMENT["y"],
            },
            "delta_x": (
                PROPOSED_ARYN_PLACEMENT["x"]
                - PROPOSED_ARYN_PLACEMENT["previous_x"]
            ),
            "reason": (
                "Create readable approach space and guarantee the gangway can "
                "finish deploying before Aryn reaches its lower tread."
            ),
        },
        "surfaces": steps,
        "motion_contract": {
            "group": "aryn_ship_hover",
            "ship_offset_curve": ship_motion["ship_offset_y_px"],
            "cycle_ms": ship_motion["cycle_ms"],
            "rule": (
                "Every gangway and hull surface receives the exact ship deltaY. "
                "Aryn inherits that delta while supported."
            ),
        },
        "render_contract": {
            "order": [
                "landscape",
                "hover field and dust",
                "ship",
                "deployed gangway",
                "Aryn",
            ],
            "gangway_art_status": "structural-placeholder",
            "final_art_direction": (
                "Telescoping violet-alloy treads with cyan traction rims, "
                "magenta hinge lights, and dark mechanical struts."
            ),
        },
        "input_contract": {
            "jump": "Space or JUMP button",
            "drop": "Down while supported uses the existing one-way drop behavior",
            "new_input_required": False,
        },
        "approval_questions": [
            "Should approaching the ship automatically deploy the gangway?",
            "Is moving the overworld spawn 120 pixels right an acceptable trade for readable deployment space?",
            "Is the three-tread novice route appropriately welcoming?",
            "Should the near-limit direct jump remain as an unannounced skill shortcut?",
            "Is the cockpit perch high enough to feel rewarding without implying a larger ship interior?",
        ],
    }
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def validate() -> None:
    assert LANDING_PLATE.exists()
    assert SHIP_ASSET.exists()
    assert HOVER_FIELD.exists()
    assert ARYN_SPRITE.exists()
    assert Image.open(LANDING_PLATE).size == (WORLD_WIDTH, WORLD_HEIGHT)
    assert round(JUMP_APEX_RISE, 2) == 152.22
    rises = []
    previous_y = GROUND_Y
    for surface in SURFACES:
        rise = previous_y - surface["y"]
        rises.append(rise)
        assert rise <= 128, (surface["id"], rise)
        assert surface["width"] >= PLAYER_COLLISION_WIDTH + 20
        previous_y = surface["y"]
    assert max(rises) == 80
    boarding_deck = next(
        surface for surface in SURFACES if surface["id"] == "ship_boarding_deck"
    )
    assert GROUND_Y - boarding_deck["y"] == 144
    assert JUMP_APEX_RISE - 144 > 8
    assert PROPOSED_ARYN_PLACEMENT["center_x"] - TRIGGER_ZONE["player_center_right"] == 16
    assert PROPOSED_ARYN_PLACEMENT["x"] - PROPOSED_ARYN_PLACEMENT["previous_x"] == 120
    assert all(
        path.exists()
        for path in (
            DEPLOYED_CONCEPT,
            COLLISION_GUIDE,
            ROUTE_DETAIL,
            CONTACT_SHEET,
            MANIFEST,
        )
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    source = build_base_composite()
    deployed = draw_gangway_art(source)
    deployed.save(DEPLOYED_CONCEPT)
    guide = build_collision_guide(deployed)
    detail = build_route_detail(guide)
    build_contact_sheet(deployed, guide, detail)
    write_manifest()
    validate()
    print(f"Deployed concept: {DEPLOYED_CONCEPT}")
    print(f"Collision guide: {COLLISION_GUIDE}")
    print(f"Contact sheet: {CONTACT_SHEET}")
    print(f"Manifest: {MANIFEST}")


if __name__ == "__main__":
    main()
