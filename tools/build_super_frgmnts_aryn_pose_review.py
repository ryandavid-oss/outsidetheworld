#!/usr/bin/env python3
"""Prepare and review stronger rested-pose candidates for Aryn Sol-Mavi.

The AI-assisted pose renders are external to this deterministic builder. This
script creates their identity board, post-processes approved chroma sources, and
builds actual-size review images. It never modifies the live game.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PHASE = ROOT / "Design/Super-Frgmnts/Overworld/Phase-3"
ARYN_DIR = PHASE / "Aryn"
RAW_DIR = ARYN_DIR / "Raw"
ASSET_DIR = ARYN_DIR / "Assets"
REVIEW_DIR = ARYN_DIR / "Reviews"

CURRENT_IDLE = ROOT / "Images/Builder/signal-ranger-idle-focused-v2.png"
RUN_SHEET = ROOT / "Images/Builder/aryn-run-10pose-balanced-gait-sheet.png"
JUMP = ROOT / "Images/Builder/signal-ranger-jump-takeoff.png"
OUTPOST = (
    ROOT
    / "Design/Super-Frgmnts/Overworld/Production/Plates"
    / "overworld-dras-outpost-v1.png"
)
DRAS = PHASE / "Dras/Assets/dras-runtime-candidate-v1.png"

REFERENCE_BOARD = RAW_DIR / "aryn-identity-motion-reference-v1.png"
COMMAND_UNCROPPED = (
    ASSET_DIR / "aryn-command-rest-transparent-uncropped-v1.png"
)
FIELD_UNCROPPED = (
    ASSET_DIR / "aryn-field-rest-transparent-uncropped-v1.png"
)
COMMAND_MASTER = ASSET_DIR / "aryn-command-rest-master-v1.png"
FIELD_MASTER = ASSET_DIR / "aryn-field-rest-master-v1.png"
COMMAND_RUNTIME = ASSET_DIR / "aryn-command-rest-runtime-candidate-v1.png"
FIELD_RUNTIME = ASSET_DIR / "aryn-field-rest-runtime-candidate-v1.png"
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


def visible_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    alpha = image.convert("RGBA").getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        raise RuntimeError("Sprite contains no visible pixels.")
    return bbox


def crop_run_frame(index: int) -> Image.Image:
    sheet = Image.open(RUN_SHEET).convert("RGBA")
    frame_width = sheet.width // 10
    return sheet.crop(
        (
            index * frame_width,
            0,
            (index + 1) * frame_width,
            sheet.height,
        )
    )


def prepare_reference() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGBA", (1340, 720), COLORS["void"])
    draw = ImageDraw.Draw(canvas)
    label(draw, (38, 26), "ARYN SOL-MAVI // IDENTITY & MOTION AUTHORITY", size=31, bold=True)
    label(
        draw,
        (40, 72),
        "Preserve armor, helmet, backpack, antenna, palette, proportions, and right-facing profile.",
        size=16,
        fill=COLORS["soft"],
    )

    references = (
        (
            "CURRENT IDLE",
            Image.open(CURRENT_IDLE).convert("RGBA"),
            "Identity authority; posture is the defect.",
            COLORS["pink"],
        ),
        (
            "RUN FRAME",
            crop_run_frame(6),
            "Confident head carriage and armor articulation.",
            COLORS["blue"],
        ),
        (
            "TAKEOFF",
            Image.open(JUMP).convert("RGBA"),
            "Torso, gauntlets, boots, and backpack reference.",
            COLORS["teal"],
        ),
    )
    for index, (heading, sprite, note, accent) in enumerate(references):
        left = 38 + index * 432
        top = 118
        draw.rounded_rectangle(
            (left, top, left + 396, 674),
            radius=10,
            fill=COLORS["panel"],
            outline=accent,
            width=2,
        )
        label(draw, (left + 20, top + 18), heading, size=20, fill=accent, bold=True)
        enlarged = sprite.resize((448, 448), Image.Resampling.NEAREST)
        canvas.alpha_composite(enlarged, (left - 26, top + 66))
        label(draw, (left + 18, top + 500), note, size=13, fill=COLORS["soft"])
    canvas.convert("RGB").save(REFERENCE_BOARD)
    return REFERENCE_BOARD


def trim_master(source_path: Path, output_path: Path) -> Image.Image:
    source = Image.open(source_path).convert("RGBA")
    red, green, blue, alpha = source.split()
    alpha = alpha.point(lambda value: 0 if value < 8 else value)
    cleaned = Image.merge("RGBA", (red, green, blue, alpha))
    bbox = alpha.getbbox()
    if bbox is None:
        raise RuntimeError(f"No visible candidate pixels: {source_path}")
    margin = 10
    left = max(0, bbox[0] - margin)
    top = max(0, bbox[1] - margin)
    right = min(cleaned.width, bbox[2] + margin)
    bottom = min(cleaned.height, bbox[3] + margin)
    master = cleaned.crop((left, top, right, bottom))
    master.save(output_path)
    return master


def runtime_from_master(
    master: Image.Image,
    output_path: Path,
    *,
    target_height: int,
    baseline: int,
) -> Image.Image:
    scale = target_height / master.height
    width = round(master.width * scale)
    sprite = master.resize((width, target_height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (112, 112), (0, 0, 0, 0))
    x = (112 - width) // 2
    y = baseline - target_height
    canvas.alpha_composite(sprite, (x, y))
    canvas.save(output_path)
    return canvas


def panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    accent: tuple[int, int, int, int],
) -> None:
    draw.rounded_rectangle(
        box,
        radius=10,
        fill=COLORS["panel"],
        outline=accent,
        width=2,
    )


def build_pose_comparison(
    current: Image.Image,
    command: Image.Image,
    field: Image.Image,
    current_bbox: tuple[int, int, int, int],
) -> Path:
    output = REVIEW_DIR / "aryn-rested-pose-comparison-v1.png"
    canvas = Image.new("RGBA", (1720, 1040), COLORS["void"])
    draw = ImageDraw.Draw(canvas)
    label(draw, (42, 28), "ARYN SOL-MAVI // RESTED-POSE AUTHORITY STUDY", size=32, bold=True)
    label(
        draw,
        (44, 74),
        "All three use the same 112×112 runtime canvas and the current feet baseline.",
        size=16,
        fill=COLORS["soft"],
    )
    cards = (
        (
            "CURRENT // COLLAPSED",
            current,
            "Shoulders and helmet fall forward.\nReads depleted, apologetic, or injured.",
            COLORS["pink"],
        ),
        (
            "COMMAND REST",
            command,
            "Broad base, lifted chest, quiet authority.\nStrongest silhouette at a complete stop.",
            COLORS["gold"],
        ),
        (
            "FIELD REST",
            field,
            "Narrower base, active hands, ready to move.\nBest bridge back into traversal.",
            COLORS["teal"],
        ),
    )
    for index, (heading, sprite, note, accent) in enumerate(cards):
        left = 42 + index * 558
        top = 120
        panel(draw, (left, top, left + 520, 942), accent=accent)
        label(draw, (left + 22, top + 20), heading, size=21, fill=accent, bold=True)

        grid_left, grid_top = left + 52, top + 86
        draw.rectangle(
            (grid_left, grid_top, grid_left + 416, grid_top + 416),
            fill=(4, 7, 20, 255),
            outline=COLORS["blue"],
            width=1,
        )
        for value in range(0, 417, 56):
            draw.line(
                (grid_left + value, grid_top, grid_left + value, grid_top + 416),
                fill=(99, 149, 238, 28),
                width=1,
            )
            draw.line(
                (grid_left, grid_top + value, grid_left + 416, grid_top + value),
                fill=(99, 149, 238, 28),
                width=1,
            )
        enlarged = sprite.resize((416, 416), Image.Resampling.NEAREST)
        canvas.alpha_composite(enlarged, (grid_left, grid_top))
        baseline_y = grid_top + round(current_bbox[3] / 112 * 416)
        draw.line(
            (grid_left, baseline_y, grid_left + 416, baseline_y),
            fill=COLORS["green"],
            width=2,
        )

        draw.multiline_text(
            (left + 24, top + 546),
            note,
            font=font(15),
            fill=COLORS["ink"],
            spacing=8,
        )
        checklist = (
            ("HEAD LEVEL", index > 0),
            ("SHOULDERS OPEN", index > 0),
            ("HIPS UNDER TORSO", index > 0),
            ("FEET DELIBERATE", index > 0),
        )
        for row, (text, passes) in enumerate(checklist):
            y = top + 644 + row * 38
            color = COLORS["green"] if passes else COLORS["pink"]
            label(draw, (left + 24, y), "●", size=15, fill=color)
            label(draw, (left + 52, y), text, size=14, fill=COLORS["soft"])

        if heading == "COMMAND REST":
            draw.rounded_rectangle(
                (left + 24, top + 776, left + 300, top + 816),
                radius=5,
                fill=COLORS["gold"],
            )
            label(
                draw,
                (left + 46, top + 786),
                "POWER RECOMMENDATION",
                size=14,
                fill=COLORS["void"],
                bold=True,
            )
    label(
        draw,
        (44, 982),
        "Recommendation: Command Rest as the true idle; Field Rest can remain a useful pre-run or alert stance.",
        size=17,
        fill=COLORS["gold"],
    )
    canvas.convert("RGB").save(output)
    return output


def place_actor(scene: Image.Image, actor: Image.Image, x: int, ground_y: int = 744) -> None:
    scene.alpha_composite(actor, (x, ground_y - actor.height))


def build_world_test(
    current: Image.Image,
    command: Image.Image,
    field: Image.Image,
) -> Path:
    output = REVIEW_DIR / "aryn-rested-pose-world-test-v1.png"
    canvas = Image.new("RGBA", (1760, 1080), COLORS["void"])
    draw = ImageDraw.Draw(canvas)
    label(draw, (42, 28), "ACTUAL WORLD TEST // DRAS OUTPOST", size=32, bold=True)
    label(
        draw,
        (44, 74),
        "No enlarged concept art: each actor is rendered at the intended world scale.",
        size=16,
        fill=COLORS["soft"],
    )
    plate = Image.open(OUTPOST).convert("RGBA")
    dras = Image.open(DRAS).convert("RGBA")
    states = (
        ("CURRENT IDLE", current, COLORS["pink"]),
        ("COMMAND REST", command, COLORS["gold"]),
        ("FIELD REST", field, COLORS["teal"]),
    )
    for index, (heading, sprite, accent) in enumerate(states):
        left = 42 + index * 572
        panel(draw, (left, 122, left + 536, 990), accent=accent)
        label(draw, (left + 20, 142), heading, size=20, fill=accent, bold=True)
        scene = plate.copy()
        place_actor(scene, sprite, 74)
        place_actor(scene, dras, 280)
        crop = scene.crop((0, 236, 620, 820)).resize(
            (496, 467),
            Image.Resampling.LANCZOS,
        )
        canvas.alpha_composite(crop, (left + 20, 188))
        draw.rectangle(
            (left + 132, 684, left + 404, 956),
            fill=(4, 7, 20, 255),
            outline=COLORS["blue"],
            width=1,
        )
        detail = sprite.resize((272, 272), Image.Resampling.NEAREST)
        canvas.alpha_composite(detail, (left + 132, 684))
        label(
            draw,
            (left + 20, 956),
            "Aryn 112×112 • Dras 96×112",
            size=13,
            fill=COLORS["soft"],
        )
    canvas.convert("RGB").save(output)
    return output


def build_transition_contract(
    command: Image.Image,
    field: Image.Image,
) -> Path:
    output = REVIEW_DIR / "aryn-idle-transition-contract-v1.png"
    canvas = Image.new("RGBA", (1680, 820), COLORS["void"])
    draw = ImageDraw.Draw(canvas)
    label(draw, (42, 28), "RUN → REST // TRANSITION CONTRACT", size=32, bold=True)
    label(
        draw,
        (44, 74),
        "The stronger pose needs a short settle; snapping directly from a run frame would look mechanical.",
        size=16,
        fill=COLORS["soft"],
    )

    frames = (
        ("RUN CONTACT", crop_run_frame(9), COLORS["blue"]),
        ("SETTLE A", field, COLORS["teal"]),
        ("SETTLE B", command, COLORS["gold"]),
        ("COMMAND REST", command, COLORS["green"]),
    )
    for index, (heading, sprite, accent) in enumerate(frames):
        left = 42 + index * 404
        panel(draw, (left, 126, left + 368, 540), accent=accent)
        label(draw, (left + 18, 144), heading, size=17, fill=accent, bold=True)
        enlarged = sprite.resize((336, 336), Image.Resampling.NEAREST)
        canvas.alpha_composite(enlarged, (left + 16, 186))
        if index < len(frames) - 1:
            label(draw, (left + 374, 322), "›", size=28, fill=COLORS["soft"], bold=True)

    contracts = (
        ("DURATION", "180–240ms after horizontal speed reaches zero"),
        ("FEET", "Preserve the planted contact foot; no visible slide"),
        ("TORSO", "Shoulders rise before the helmet settles"),
        ("LOOP", "Command Rest breathes ±1px; no held seam"),
        ("REDUCED MOTION", "Use Command Rest immediately with no settle frames"),
    )
    for index, (heading, body) in enumerate(contracts):
        left = 42 + (index % 3) * 536
        top = 582 + (index // 3) * 92
        label(draw, (left, top), heading, size=15, fill=COLORS["gold"], bold=True)
        label(draw, (left, top + 28), body, size=13, fill=COLORS["soft"])
    canvas.convert("RGB").save(output)
    return output


def write_manifest(
    current_bbox: tuple[int, int, int, int],
    outputs: list[Path],
) -> Path:
    output = ARYN_DIR / "aryn-revision-3e-manifest.json"
    manifest = {
        "revision": "3E",
        "status": "approved-local-prototype",
        "identity_authority": str(CURRENT_IDLE),
        "posture_references": [
            "/Users/rylee/Downloads/Untitled.jpg",
            (
                "/var/folders/fw/ry1pp5b94xb50wnxsgcfds240000gp/T/"
                "codex-clipboard-35b5924e-7df5-4b75-85ab-96c6dd160a88.png"
            ),
        ],
        "runtime": {
            "canvas": [112, 112],
            "visible_height": current_bbox[3] - current_bbox[1],
            "baseline_y_in_canvas": current_bbox[3],
            "recommendation": "command-rest",
            "alternate": "field-rest",
            "state_rule": {
                "field_rest": "movement, landing, recent fire, or nearby threat",
                "command_rest": "canonical idle after 1.8 calm seconds and exposition",
            },
        },
        "transition": {
            "duration_ms": [180, 240],
            "frames": "art pass pending; local prototype switches by state",
            "reduced_motion": "immediate command-rest",
        },
        "outputs": [str(path) for path in outputs],
        "scope": {
            "live_game_modified": True,
            "integrated": "local-only",
            "deployed": False,
            "committed": False,
        },
    }
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return output


def build_reviews() -> list[Path]:
    for directory in (ASSET_DIR, REVIEW_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    current = Image.open(CURRENT_IDLE).convert("RGBA")
    current_bbox = visible_bbox(current)
    target_height = current_bbox[3] - current_bbox[1]
    command_master = trim_master(COMMAND_UNCROPPED, COMMAND_MASTER)
    field_master = trim_master(FIELD_UNCROPPED, FIELD_MASTER)
    command = runtime_from_master(
        command_master,
        COMMAND_RUNTIME,
        target_height=target_height,
        baseline=current_bbox[3],
    )
    field = runtime_from_master(
        field_master,
        FIELD_RUNTIME,
        target_height=target_height,
        baseline=current_bbox[3],
    )
    outputs = [
        COMMAND_MASTER,
        FIELD_MASTER,
        COMMAND_RUNTIME,
        FIELD_RUNTIME,
        build_pose_comparison(current, command, field, current_bbox),
        build_world_test(current, command, field),
        build_transition_contract(command, field),
    ]
    outputs.append(write_manifest(current_bbox, outputs))
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-reference", action="store_true")
    parser.add_argument("--build-reviews", action="store_true")
    args = parser.parse_args()
    if not args.prepare_reference and not args.build_reviews:
        parser.error("Choose an explicit build action.")
    if args.prepare_reference:
        print(prepare_reference())
    if args.build_reviews:
        for output in build_reviews():
            print(output)


if __name__ == "__main__":
    main()
