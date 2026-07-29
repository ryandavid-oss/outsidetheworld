#!/usr/bin/env python3
"""Build curated Ludo impact and death runtime assets for Aryn."""

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

LIGHT_SOURCE = RAW_ROOT / "aryn-ludo-impact-light-sheet-v1.png"
LIGHT_METADATA = RAW_ROOT / "aryn-ludo-impact-light-sheet-v1.json"
HEAVY_SOURCE = RAW_ROOT / "aryn-ludo-impact-heavy-sheet-v1.png"
HEAVY_METADATA = RAW_ROOT / "aryn-ludo-impact-heavy-sheet-v1.json"
DEATH_SOURCE = RAW_ROOT / "aryn-ludo-death-sheet-v1.png"
DEATH_METADATA = RAW_ROOT / "aryn-ludo-death-sheet-v1.json"

LIGHT_RUNTIME = RUNTIME_ROOT / "aryn-impact-light-ludo-runtime-v1.png"
HEAVY_RUNTIME = RUNTIME_ROOT / "aryn-impact-heavy-ludo-runtime-v1.png"
DEATH_RUNTIME = RUNTIME_ROOT / "aryn-death-ludo-runtime-v1.png"
LIGHT_REVIEW = REVIEW_ROOT / "aryn-ludo-impact-light-preview-v1.gif"
HEAVY_REVIEW = REVIEW_ROOT / "aryn-ludo-impact-heavy-preview-v1.gif"
DEATH_REVIEW = REVIEW_ROOT / "aryn-ludo-death-preview-v1.gif"
CONTACT_SHEET = REVIEW_ROOT / "aryn-ludo-combat-contact-v1.png"
MANIFEST_OUTPUT = LUDO_ROOT / "aryn-ludo-combat-runtime-v1.json"

FRAME_SIZE = 112
BASELINE_Y = 105
SOURCE_SCALE = 0.165
REVIEW_BACKGROUND = (3, 6, 18, 255)

# The lighter reaction keeps Aryn controlled and upright. It is used for the
# first and third non-lethal contacts so repeated hits do not look identical.
LIGHT_COMPONENTS = (
    (0, "ready"),
    (2, "contact"),
    (4, "recoil"),
    (7, "recoil hold"),
    (10, "recover"),
    (14, "reset"),
)

# The heavier reaction has a deeper torso and leg response. It is alternated
# with the lighter sequence for later non-lethal contacts.
HEAVY_COMPONENTS = (
    (0, "ready"),
    (3, "contact"),
    (5, "deep recoil"),
    (7, "recoil hold"),
    (9, "recover low"),
    (12, "recover"),
    (15, "reset"),
)

# The generated death sequence includes a long standing lead-in and several
# near-duplicate prone frames. These selections preserve the readable arc:
# stagger, knee, brace, fall, impact, and final stillness.
DEATH_COMPONENTS = (
    (0, "ready"),
    (7, "stagger"),
    (12, "fold"),
    (18, "knee"),
    (20, "kneel"),
    (24, "collapse"),
    (26, "brace"),
    (27, "fall"),
    (28, "impact"),
    (29, "prone"),
    (30, "settle"),
    (31, "still"),
)


def load_frames(
    sheet_path: Path,
    metadata_path: Path,
    expected_count: int,
    expected_size: tuple[int, int],
) -> list[Image.Image]:
    sheet = Image.open(sheet_path).convert("RGBA")
    metadata = json.loads(metadata_path.read_text())
    frame_entries = [metadata["frames"][key] for key in sorted(metadata["frames"])]

    if len(frame_entries) != expected_count:
        raise ValueError(
            f"{sheet_path.name}: expected {expected_count} frames, "
            f"found {len(frame_entries)}"
        )

    frames: list[Image.Image] = []
    for index, entry in enumerate(frame_entries):
        rect = entry["frame"]
        frame_size = (rect["w"], rect["h"])
        if frame_size != expected_size:
            raise ValueError(
                f"{sheet_path.name} frame {index}: {frame_size}; "
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


def baseline_frame(source: Image.Image) -> Image.Image:
    reduced = source.resize(
        (
            round(source.width * SOURCE_SCALE),
            round(source.height * SOURCE_SCALE),
        ),
        Image.Resampling.LANCZOS,
    )
    bounds = reduced.getbbox()
    if not bounds:
        raise ValueError("Source frame has no visible pixels")
    trimmed = reduced.crop(bounds)
    if trimmed.width > FRAME_SIZE or trimmed.height > BASELINE_Y:
        raise ValueError(
            f"Normalized frame is too large: {trimmed.size}; "
            f"runtime is {FRAME_SIZE}x{FRAME_SIZE}"
        )

    runtime = Image.new("RGBA", (FRAME_SIZE, FRAME_SIZE), (0, 0, 0, 0))
    runtime.alpha_composite(
        trimmed,
        (
            round((FRAME_SIZE - trimmed.width) / 2),
            BASELINE_Y - trimmed.height,
        ),
    )
    return runtime


def select_frames(
    source_frames: list[Image.Image],
    components: tuple[tuple[int, str], ...],
) -> list[Image.Image]:
    return [baseline_frame(source_frames[index]) for index, _ in components]


def build_strip(frames: list[Image.Image]) -> Image.Image:
    strip = Image.new(
        "RGBA",
        (FRAME_SIZE * len(frames), FRAME_SIZE),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(frames):
        strip.alpha_composite(frame, (index * FRAME_SIZE, 0))
    return strip


def build_review_gif(
    frames: list[Image.Image],
    path: Path,
    durations: list[int],
) -> None:
    review_frames: list[Image.Image] = []
    for frame in frames:
        review = Image.new(
            "RGBA",
            (FRAME_SIZE, FRAME_SIZE),
            REVIEW_BACKGROUND,
        )
        review.alpha_composite(frame)
        review_frames.append(review.convert("RGB"))

    review_frames[0].save(
        path,
        save_all=True,
        append_images=review_frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=False,
    )


def build_contact_row(
    contact: Image.Image,
    draw: ImageDraw.ImageDraw,
    title: str,
    frames: list[Image.Image],
    roles: tuple[tuple[int, str], ...],
    y: int,
) -> None:
    draw.text((8, y), title, fill=(235, 240, 255, 255))
    for index, frame in enumerate(frames):
        x = index * FRAME_SIZE
        contact.alpha_composite(frame, (x, y + 18))
        draw.text((x + 5, y + 119), str(index), fill=(132, 255, 235, 255))
        draw.text(
            (x + 20, y + 119),
            roles[index][1][:12],
            fill=(255, 211, 108, 255),
        )


def build_contact_sheet(
    light_frames: list[Image.Image],
    heavy_frames: list[Image.Image],
    death_frames: list[Image.Image],
) -> None:
    width = FRAME_SIZE * len(death_frames)
    contact = Image.new("RGBA", (width, 430), REVIEW_BACKGROUND)
    draw = ImageDraw.Draw(contact)
    build_contact_row(
        contact,
        draw,
        "LIGHT IMPACT // CONTROLLED RECOIL",
        light_frames,
        LIGHT_COMPONENTS,
        6,
    )
    build_contact_row(
        contact,
        draw,
        "HEAVY IMPACT // DEEP RECOIL",
        heavy_frames,
        HEAVY_COMPONENTS,
        145,
    )
    build_contact_row(
        contact,
        draw,
        "HEALTH DEPLETED // COLLAPSE",
        death_frames,
        DEATH_COMPONENTS,
        284,
    )
    contact.resize((width * 2, 860), Image.Resampling.NEAREST).save(
        CONTACT_SHEET,
        optimize=True,
    )


def component_manifest(
    components: tuple[tuple[int, str], ...],
) -> list[dict[str, object]]:
    return [
        {"frame": frame, "role": role}
        for frame, role in components
    ]


def main() -> None:
    light_source_frames = load_frames(
        LIGHT_SOURCE,
        LIGHT_METADATA,
        16,
        (500, 554),
    )
    heavy_source_frames = load_frames(
        HEAVY_SOURCE,
        HEAVY_METADATA,
        16,
        (362, 558),
    )
    death_source_frames = load_frames(
        DEATH_SOURCE,
        DEATH_METADATA,
        36,
        (574, 606),
    )

    light_frames = select_frames(light_source_frames, LIGHT_COMPONENTS)
    heavy_frames = select_frames(heavy_source_frames, HEAVY_COMPONENTS)
    death_frames = select_frames(death_source_frames, DEATH_COMPONENTS)

    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    build_strip(light_frames).save(LIGHT_RUNTIME, optimize=True)
    build_strip(heavy_frames).save(HEAVY_RUNTIME, optimize=True)
    build_strip(death_frames).save(DEATH_RUNTIME, optimize=True)

    build_review_gif(
        light_frames,
        LIGHT_REVIEW,
        [50, 50, 55, 55, 55, 80],
    )
    build_review_gif(
        heavy_frames,
        HEAVY_REVIEW,
        [45, 45, 45, 50, 50, 55, 85],
    )
    build_review_gif(
        death_frames + [death_frames[-1]] * 4,
        DEATH_REVIEW,
        [65] * len(death_frames) + [70, 70, 70, 140],
    )
    build_contact_sheet(light_frames, heavy_frames, death_frames)

    manifest = {
        "asset": "Aryn Sol-Mavi curated Ludo combat reactions",
        "status": "local preview candidate",
        "preview_query": "aryn=ludo",
        "runtime_contract": {
            "frame_size": [FRAME_SIZE, FRAME_SIZE],
            "baseline_y": BASELINE_Y,
            "source_scale": SOURCE_SCALE,
            "light_impact_frame_count": len(light_frames),
            "heavy_impact_frame_count": len(heavy_frames),
            "death_frame_count": len(death_frames),
        },
        "light_impact": {
            "runtime": str(LIGHT_RUNTIME.relative_to(PROJECT_ROOT)),
            "components": component_manifest(LIGHT_COMPONENTS),
        },
        "heavy_impact": {
            "runtime": str(HEAVY_RUNTIME.relative_to(PROJECT_ROOT)),
            "components": component_manifest(HEAVY_COMPONENTS),
        },
        "death": {
            "runtime": str(DEATH_RUNTIME.relative_to(PROJECT_ROOT)),
            "components": component_manifest(DEATH_COMPONENTS),
            "final_frame_hold": True,
        },
        "source_decisions": {
            "rifle_shoot_reference": (
                "source master only; curated into an isolated rifle preview"
            ),
            "rifle_draw_reference": (
                "source master only; curated into an isolated rifle preview"
            ),
            "reason": (
                "The backpack telescopic laser seeker remains the production "
                "default. The conventional rifle is evaluated separately as "
                "a special weapon for route clearing, bosses, and heavy combat."
            ),
        },
        "notes": [
            "All runtime frames are baseline-normalized to prevent source drift.",
            "Light and heavy impacts alternate across non-lethal contacts.",
            "The death sequence is reserved for health depletion.",
            "Telescopic laser seeker firing remains compatible with running and jumping.",
            "Production animation remains unchanged unless aryn=ludo is present.",
        ],
    }
    MANIFEST_OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n")

    for output in (
        LIGHT_RUNTIME,
        HEAVY_RUNTIME,
        DEATH_RUNTIME,
        LIGHT_REVIEW,
        HEAVY_REVIEW,
        DEATH_REVIEW,
        CONTACT_SHEET,
        MANIFEST_OUTPUT,
    ):
        print(f"Wrote {output.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
