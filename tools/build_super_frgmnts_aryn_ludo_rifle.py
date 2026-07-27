#!/usr/bin/env python3
"""Build preview-only Ludo rifle animations for Aryn Sol-Mavi."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LUDO_ROOT = (
    PROJECT_ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Overworld"
    / "Phase-3"
    / "Aryn"
    / "Ludo"
)
RAW_ROOT = LUDO_ROOT / "Raw"
REVIEW_ROOT = LUDO_ROOT / "Reviews"
RUNTIME_ROOT = PROJECT_ROOT / "Images" / "Game" / "Super-Frgmnts"

DRAW_SOURCE = RAW_ROOT / "aryn-ludo-rifle-draw-reference-v1.png"
DRAW_METADATA = RAW_ROOT / "aryn-ludo-rifle-draw-reference-v1.json"
FIRE_SOURCE = RAW_ROOT / "aryn-ludo-rifle-shoot-reference-v1.png"
FIRE_METADATA = RAW_ROOT / "aryn-ludo-rifle-shoot-reference-v1.json"

DRAW_RUNTIME = RUNTIME_ROOT / "aryn-rifle-draw-ludo-runtime-v1.png"
FIRE_RUNTIME = RUNTIME_ROOT / "aryn-rifle-fire-ludo-runtime-v1.png"
DRAW_REVIEW = REVIEW_ROOT / "aryn-ludo-rifle-draw-preview-v1.gif"
FIRE_REVIEW = REVIEW_ROOT / "aryn-ludo-rifle-fire-preview-v1.gif"
CONTACT_SHEET = REVIEW_ROOT / "aryn-ludo-rifle-contact-v1.png"
MANIFEST_OUTPUT = LUDO_ROOT / "aryn-ludo-rifle-runtime-v1.json"

FRAME_SIZE = 112
BASELINE_Y = 105
SOURCE_SCALE = 0.165
RIFLE_FORESECTION_X = 82
RIFLE_FORESECTION_SHIFT = 14
REVIEW_BACKGROUND = (3, 6, 18, 255)

# The generated draw contains a long idle lead and a firing tail. These frames
# preserve the readable reach, clear, shoulder, and aim beats without replaying
# the later muzzle animation.
DRAW_COMPONENTS = (
    (0, "stowed"),
    (3, "reach"),
    (6, "grip"),
    (9, "clear"),
    (11, "lift"),
    (13, "shoulder"),
    (16, "cross body"),
    (18, "low ready"),
    (20, "raise"),
    (22, "aim"),
)

# The firing source is deliberately condensed to a fast, forceful pulse. The
# selected frames retain ignition, the largest flash silhouettes, recoil, beam
# tail, and a clean aimed recovery.
FIRE_COMPONENTS = (
    (0, "aim"),
    (2, "ignition"),
    (4, "flash"),
    (7, "flash hold"),
    (10, "recoil"),
    (14, "recoil hold"),
    (18, "pulse"),
    (22, "pulse tail"),
    (26, "beam"),
    (30, "beam tail"),
    (34, "recover"),
    (35, "aim"),
)


def load_frames(
    sheet_path: Path,
    metadata_path: Path,
    expected_size: tuple[int, int],
) -> list[Image.Image]:
    sheet = Image.open(sheet_path).convert("RGBA")
    metadata = json.loads(metadata_path.read_text())
    entries = [metadata["frames"][key] for key in sorted(metadata["frames"])]
    if len(entries) != 36:
        raise ValueError(f"{sheet_path.name}: expected 36 frames")

    frames: list[Image.Image] = []
    for index, entry in enumerate(entries):
        rect = entry["frame"]
        size = (rect["w"], rect["h"])
        if size != expected_size:
            raise ValueError(
                f"{sheet_path.name} frame {index}: {size}; "
                f"expected {expected_size}"
            )
        frames.append(
            sheet.crop(
                (
                    rect["x"],
                    rect["y"],
                    rect["x"] + rect["w"],
                    rect["y"] + rect["h"],
                )
            )
        )
    return frames


def normalize_fixed_canvas(source: Image.Image) -> Image.Image:
    """Scale the whole Ludo cell so Aryn's body never drifts with the rifle."""
    reduced = source.resize(
        (
            round(source.width * SOURCE_SCALE),
            round(source.height * SOURCE_SCALE),
        ),
        Image.Resampling.LANCZOS,
    )
    if reduced.width > FRAME_SIZE or reduced.height > BASELINE_Y:
        raise ValueError(f"Normalized frame is too large: {reduced.size}")

    runtime = Image.new("RGBA", (FRAME_SIZE, FRAME_SIZE), (0, 0, 0, 0))
    runtime.alpha_composite(
        reduced,
        (
            round((FRAME_SIZE - reduced.width) / 2),
            BASELINE_Y - reduced.height,
        ),
    )
    return runtime


def shorten_rifle_foresection(frame: Image.Image) -> Image.Image:
    """Match the standing rifle silhouette to the authored running rifle."""
    shortened = frame.copy()
    foresection = frame.crop(
        (RIFLE_FORESECTION_X, 0, FRAME_SIZE, FRAME_SIZE)
    )
    shortened.paste(
        (0, 0, 0, 0),
        (RIFLE_FORESECTION_X, 0, FRAME_SIZE, FRAME_SIZE),
    )
    shortened.alpha_composite(
        foresection,
        (RIFLE_FORESECTION_X - RIFLE_FORESECTION_SHIFT, 0),
    )
    return shortened


def select_frames(
    source_frames: list[Image.Image],
    components: tuple[tuple[int, str], ...],
) -> list[Image.Image]:
    return [
        normalize_fixed_canvas(source_frames[index])
        for index, _ in components
    ]


def build_strip(frames: list[Image.Image]) -> Image.Image:
    strip = Image.new(
        "RGBA",
        (FRAME_SIZE * len(frames), FRAME_SIZE),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(frames):
        strip.alpha_composite(frame, (index * FRAME_SIZE, 0))
    return strip


def build_review(
    frames: list[Image.Image],
    output: Path,
    durations: list[int],
) -> None:
    reviews: list[Image.Image] = []
    for frame in frames:
        review = Image.new("RGBA", (FRAME_SIZE, FRAME_SIZE), REVIEW_BACKGROUND)
        review.alpha_composite(frame)
        reviews.append(
            review.resize((FRAME_SIZE * 3, FRAME_SIZE * 3), Image.Resampling.NEAREST)
            .convert("RGB")
        )
    reviews[0].save(
        output,
        save_all=True,
        append_images=reviews[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=False,
    )


def build_contact_sheet(
    draw_frames: list[Image.Image],
    fire_frames: list[Image.Image],
) -> None:
    width = FRAME_SIZE * max(len(draw_frames), len(fire_frames))
    contact = Image.new("RGBA", (width, 286), REVIEW_BACKGROUND)
    draw = ImageDraw.Draw(contact)
    rows = (
        ("SPECIAL WEAPON // DRAW AND BRACE", draw_frames, DRAW_COMPONENTS, 6),
        ("SPECIAL WEAPON // RIFLE DISCHARGE", fire_frames, FIRE_COMPONENTS, 145),
    )
    for title, frames, components, y in rows:
        draw.text((8, y), title, fill=(235, 240, 255, 255))
        for frame_index, frame in enumerate(frames):
            x = frame_index * FRAME_SIZE
            contact.alpha_composite(frame, (x, y + 18))
            draw.text((x + 4, y + 119), str(frame_index), fill=(88, 245, 223, 255))
            draw.text(
                (x + 18, y + 119),
                components[frame_index][1][:12],
                fill=(255, 211, 108, 255),
            )
    contact.resize((width * 2, 572), Image.Resampling.NEAREST).save(
        CONTACT_SHEET,
        optimize=True,
    )


def manifest_components(
    components: tuple[tuple[int, str], ...],
) -> list[dict[str, object]]:
    return [
        {"source_frame": source_frame, "role": role}
        for source_frame, role in components
    ]


def main() -> None:
    draw_source_frames = load_frames(DRAW_SOURCE, DRAW_METADATA, (640, 566))
    fire_source_frames = load_frames(FIRE_SOURCE, FIRE_METADATA, (640, 556))
    draw_frames = select_frames(draw_source_frames, DRAW_COMPONENTS)
    fire_frames = select_frames(fire_source_frames, FIRE_COMPONENTS)
    # Only the final horizontal draw pose needs the shortened silhouette. The
    # preceding angled frames remain untouched so the authored draw reads
    # naturally. All standing-fire frames share the corrected muzzle plane.
    draw_frames[-1] = shorten_rifle_foresection(draw_frames[-1])
    fire_frames = [
        shorten_rifle_foresection(frame)
        for frame in fire_frames
    ]

    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    build_strip(draw_frames).save(DRAW_RUNTIME, optimize=True)
    build_strip(fire_frames).save(FIRE_RUNTIME, optimize=True)
    build_review(
        draw_frames + [draw_frames[-1]] * 2,
        DRAW_REVIEW,
        [70] * len(draw_frames) + [100, 220],
    )
    build_review(
        fire_frames + [fire_frames[-1]] * 2,
        FIRE_REVIEW,
        [38] * len(fire_frames) + [80, 180],
    )
    build_contact_sheet(draw_frames, fire_frames)

    manifest = {
        "asset": "Aryn Sol-Mavi Ludo rifle special weapon",
        "status": "Episode 01 early-beta pickup",
        "preview_query": "aryn=ludo&weapon=rifle",
        "runtime_contract": {
            "frame_size": [FRAME_SIZE, FRAME_SIZE],
            "baseline_y": BASELINE_Y,
            "source_scale": SOURCE_SCALE,
            "body_alignment": "fixed source canvas; never center on rifle bounds",
            "standing_foresection_shift": RIFLE_FORESECTION_SHIFT,
            "draw_frame_count": len(draw_frames),
            "fire_frame_count": len(fire_frames),
        },
        "draw": {
            "runtime": str(DRAW_RUNTIME.relative_to(PROJECT_ROOT)),
            "components": manifest_components(DRAW_COMPONENTS),
        },
        "fire": {
            "runtime": str(FIRE_RUNTIME.relative_to(PROJECT_ROOT)),
            "components": manifest_components(FIRE_COMPONENTS),
        },
        "design_contract": {
            "production_default": "pack-mounted seeking blaster",
            "rifle_role": "optional route-clearing heavy special weapon",
            "mobility_tradeoff": (
                "The first grounded draw is braced; the ready rifle supports "
                "ground and airborne movement"
            ),
            "projectile": "fast, direct, amber heavy round",
            "destruction_target": "Vesperite route obstructions",
            "preview_only": False,
            "episode_beta_pickup": True,
        },
        "notes": [
            "The rifle begins stowed.",
            "The first firing input draws, braces, and then discharges.",
            "Aryn holds the rifle ready after firing while running or airborne.",
            "Jumping, dropping, and falling preserve the rifle and allow aerial fire.",
            "The rifle automatically stows after 2.25 grounded seconds without firing.",
            "The idle holster countdown pauses in the air and resumes on landing.",
            "Three direct heavy rounds clear each Vesperite obstruction and leave non-colliding rubble.",
            "The existing backpack remains visible and remains Aryn's upgrade hub.",
            "The isolated weapon=rifle route remains available for review.",
            "The Episode 01 beta activates the same behavior after Aryn collects the heavy-rifle pickup.",
        ],
    }
    MANIFEST_OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n")

    for output in (
        DRAW_RUNTIME,
        FIRE_RUNTIME,
        DRAW_REVIEW,
        FIRE_REVIEW,
        CONTACT_SHEET,
        MANIFEST_OUTPUT,
    ):
        print(f"Wrote {output.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
