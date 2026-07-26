#!/usr/bin/env python3
"""Build curated Ludo jump and platform-drop runtime assets for Aryn."""

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

JUMP_SOURCE = RAW_ROOT / "aryn-ludo-jump-sheet-v1.png"
JUMP_METADATA = RAW_ROOT / "aryn-ludo-jump-sheet-v1.json"
DROP_SOURCE = RAW_ROOT / "aryn-ludo-platform-drop-sheet-v1.png"
DROP_METADATA = RAW_ROOT / "aryn-ludo-platform-drop-sheet-v1.json"
RUN_SOURCE = RAW_ROOT / "aryn-ludo-run-sheet-v3.png"
RUN_METADATA = RAW_ROOT / "aryn-ludo-run-sheet-v3.json"

RUNTIME_ROOT = PROJECT_ROOT / "Images" / "Game" / "Super-Frgmnts"
JUMP_RUNTIME = RUNTIME_ROOT / "aryn-jump-ludo-runtime-v1.png"
DROP_RUNTIME = RUNTIME_ROOT / "aryn-drop-ludo-runtime-v1.png"
JUMP_REVIEW = REVIEW_ROOT / "aryn-ludo-jump-runtime-preview-v1.gif"
DROP_REVIEW = REVIEW_ROOT / "aryn-ludo-drop-runtime-preview-v1.gif"
CONTACT_SHEET = REVIEW_ROOT / "aryn-ludo-jump-drop-contact-v1.png"
MANIFEST_OUTPUT = LUDO_ROOT / "aryn-ludo-jump-drop-runtime-v1.json"

FRAME_SIZE = 112
BASELINE_Y = 105
SOURCE_SCALE = 0.165
REVIEW_BACKGROUND = (3, 6, 18, 255)

# The jump generator supplies strong anticipation and recovery poses but no
# convincing airborne silhouette. A clean flight-phase pose from the approved
# run generation completes the jump without reviving the old chest-rifle art.
JUMP_COMPONENTS = (
    ("jump", 11, "launch crouch"),
    ("jump", 13, "launch extension"),
    ("jump", 14, "toe-off"),
    ("run", 14, "airborne hold"),
    ("jump", 26, "landing impact"),
    ("jump", 30, "landing recovery"),
    ("jump", 32, "landing settle"),
)

# The front-facing generation is reserved for the intentional down-through
# action. The arms widen during the fall, then begin returning before the game
# hands visual control back to the normal side-facing airborne pose.
DROP_COMPONENTS = (
    ("drop", 14, "drop commit"),
    ("drop", 16, "arms opening"),
    ("drop", 19, "controlled fall"),
    ("drop", 25, "fall release"),
)


def load_frames(
    sheet_path: Path,
    metadata_path: Path,
    expected_size: tuple[int, int],
) -> list[Image.Image]:
    sheet = Image.open(sheet_path).convert("RGBA")
    metadata = json.loads(metadata_path.read_text())
    frame_entries = [metadata["frames"][key] for key in sorted(metadata["frames"])]

    if len(frame_entries) != 36:
        raise ValueError(
            f"{sheet_path.name}: expected 36 frames, found {len(frame_entries)}"
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


def build_contact_sheet(
    jump_frames: list[Image.Image],
    drop_frames: list[Image.Image],
) -> None:
    width = FRAME_SIZE * max(len(jump_frames), len(drop_frames))
    contact = Image.new("RGBA", (width, 280), REVIEW_BACKGROUND)
    draw = ImageDraw.Draw(contact)
    draw.text((8, 6), "REGULAR JUMP // SIDE PROFILE", fill=(235, 240, 255, 255))
    for index, frame in enumerate(jump_frames):
        contact.alpha_composite(frame, (index * FRAME_SIZE, 22))
        draw.text(
            (index * FRAME_SIZE + 5, 133),
            str(index),
            fill=(132, 255, 235, 255),
        )

    draw.text((8, 151), "PLATFORM DROP // FRONT VIEW", fill=(235, 240, 255, 255))
    for index, frame in enumerate(drop_frames):
        contact.alpha_composite(frame, (index * FRAME_SIZE, 168))
        draw.text(
            (index * FRAME_SIZE + 5, 262),
            str(index),
            fill=(255, 211, 108, 255),
        )
    contact.resize((width * 2, 560), Image.Resampling.NEAREST).save(
        CONTACT_SHEET,
        optimize=True,
    )


def component_manifest(
    components: tuple[tuple[str, int, str], ...],
) -> list[dict[str, object]]:
    return [
        {"source": source, "frame": frame, "role": role}
        for source, frame, role in components
    ]


def main() -> None:
    jump_source_frames = load_frames(
        JUMP_SOURCE,
        JUMP_METADATA,
        (386, 640),
    )
    drop_source_frames = load_frames(
        DROP_SOURCE,
        DROP_METADATA,
        (372, 640),
    )
    run_source_frames = load_frames(
        RUN_SOURCE,
        RUN_METADATA,
        (418, 556),
    )
    source_sets = {
        "jump": jump_source_frames,
        "drop": drop_source_frames,
        "run": run_source_frames,
    }

    jump_frames = [
        baseline_frame(source_sets[source][index])
        for source, index, _ in JUMP_COMPONENTS
    ]
    drop_frames = [
        baseline_frame(source_sets[source][index])
        for source, index, _ in DROP_COMPONENTS
    ]

    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    build_strip(jump_frames).save(JUMP_RUNTIME, optimize=True)
    build_strip(drop_frames).save(DROP_RUNTIME, optimize=True)

    # The airborne hold is repeated in review only. Runtime physics controls how
    # long frame 3 remains visible.
    jump_review_frames = (
        jump_frames[:4]
        + [jump_frames[3], jump_frames[3]]
        + jump_frames[4:]
    )
    build_review_gif(
        jump_review_frames,
        JUMP_REVIEW,
        [55, 55, 55, 90, 90, 90, 55, 55, 80],
    )
    build_review_gif(
        drop_frames,
        DROP_REVIEW,
        [70, 70, 70, 90],
    )
    build_contact_sheet(jump_frames, drop_frames)

    manifest = {
        "asset": "Aryn Sol-Mavi curated Ludo jump and platform drop",
        "status": "local preview candidate",
        "preview_query": "aryn=ludo",
        "runtime_contract": {
            "frame_size": [FRAME_SIZE, FRAME_SIZE],
            "baseline_y": BASELINE_Y,
            "source_scale": SOURCE_SCALE,
            "jump_frame_count": len(jump_frames),
            "drop_frame_count": len(drop_frames),
        },
        "jump": {
            "runtime": str(JUMP_RUNTIME.relative_to(PROJECT_ROOT)),
            "components": component_manifest(JUMP_COMPONENTS),
            "launch_frames": [0, 1, 2],
            "airborne_frame": 3,
            "landing_frames": [4, 5, 6],
        },
        "drop": {
            "runtime": str(DROP_RUNTIME.relative_to(PROJECT_ROOT)),
            "components": component_manifest(DROP_COMPONENTS),
            "frames": [0, 1, 2, 3],
        },
        "notes": [
            "All component frames are baseline-normalized before runtime export.",
            "Game physics owns vertical movement; source-sheet translation is discarded.",
            "The existing production jump remains the default animation.",
        ],
    }
    MANIFEST_OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n")

    for output in (
        JUMP_RUNTIME,
        DROP_RUNTIME,
        JUMP_REVIEW,
        DROP_REVIEW,
        CONTACT_SHEET,
        MANIFEST_OUTPUT,
    ):
        print(f"Wrote {output.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
