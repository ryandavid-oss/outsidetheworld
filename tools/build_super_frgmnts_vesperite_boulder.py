#!/usr/bin/env python3
"""Build the preview-only Vesperite boulder destruction sequence."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BOULDER_ROOT = (
    PROJECT_ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Vesperite-Boulder"
)
RAW_ROOT = BOULDER_ROOT / "Raw"
REVIEW_ROOT = BOULDER_ROOT / "Reviews"
RUNTIME_ROOT = PROJECT_ROOT / "Images" / "Game" / "Super-Frgmnts"

IMPACT_SOURCE = RAW_ROOT / "vesperite-boulder-impact-source-v1.png"
IMPACT_METADATA = RAW_ROOT / "vesperite-boulder-impact-source-v1.json"
COLLAPSE_SOURCE = RAW_ROOT / "vesperite-boulder-destruction-source-v1.png"
COLLAPSE_METADATA = RAW_ROOT / "vesperite-boulder-destruction-source-v1.json"
RUBBLE_SOURCE = RAW_ROOT / "vesperite-boulder-rubble-source-v1.png"

INTACT_RUNTIME = RUNTIME_ROOT / "vesperite-boulder-intact-runtime-v1.png"
IMPACT_RUNTIME = RUNTIME_ROOT / "vesperite-boulder-impact-runtime-v1.png"
COLLAPSE_RUNTIME = RUNTIME_ROOT / "vesperite-boulder-collapse-runtime-v1.png"
RUBBLE_RUNTIME = RUNTIME_ROOT / "vesperite-boulder-rubble-runtime-v1.png"
REVIEW_GIF = REVIEW_ROOT / "vesperite-boulder-destruction-preview-v1.gif"
MANIFEST_OUTPUT = BOULDER_ROOT / "vesperite-boulder-runtime-v1.json"

FRAME_WIDTH = 176
FRAME_HEIGHT = 184
BOULDER_WIDTH = 166
BOULDER_HEIGHT = 176
BASELINE_Y = 180
FRAME_COUNT = 16
IMPACT_FRAME_MS = 55
COLLAPSE_FRAME_MS = 70
HITS_REQUIRED = 3


def load_frames(
    sheet_path: Path,
    metadata_path: Path,
) -> list[Image.Image]:
    sheet = Image.open(sheet_path).convert("RGBA")
    metadata = json.loads(metadata_path.read_text())
    entries = [metadata["frames"][key] for key in sorted(metadata["frames"])]
    if len(entries) != FRAME_COUNT:
        raise ValueError(
            f"{sheet_path.name}: expected {FRAME_COUNT} frames; "
            f"received {len(entries)}"
        )

    frames: list[Image.Image] = []
    for entry in entries:
        rect = entry["frame"]
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


def normalize_boulder(source: Image.Image) -> Image.Image:
    """Keep every generated boulder frame on one collision-stable canvas."""
    reduced = source.resize(
        (BOULDER_WIDTH, BOULDER_HEIGHT),
        Image.Resampling.LANCZOS,
    )
    runtime = Image.new(
        "RGBA",
        (FRAME_WIDTH, FRAME_HEIGHT),
        (0, 0, 0, 0),
    )
    runtime.alpha_composite(
        reduced,
        (
            (FRAME_WIDTH - BOULDER_WIDTH) // 2,
            BASELINE_Y - BOULDER_HEIGHT,
        ),
    )
    return runtime


def normalize_rubble(source: Image.Image) -> Image.Image:
    bounds = source.getbbox()
    if bounds is None:
        raise ValueError("Rubble source is empty")
    cropped = source.crop(bounds)
    rubble_width = 164
    rubble_height = round(cropped.height * rubble_width / cropped.width)
    reduced = cropped.resize(
        (rubble_width, rubble_height),
        Image.Resampling.LANCZOS,
    )
    runtime = Image.new(
        "RGBA",
        (FRAME_WIDTH, FRAME_HEIGHT),
        (0, 0, 0, 0),
    )
    runtime.alpha_composite(
        reduced,
        (
            (FRAME_WIDTH - rubble_width) // 2,
            BASELINE_Y - rubble_height,
        ),
    )
    return runtime


def build_strip(frames: list[Image.Image]) -> Image.Image:
    strip = Image.new(
        "RGBA",
        (FRAME_WIDTH * len(frames), FRAME_HEIGHT),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(frames):
        strip.alpha_composite(frame, (index * FRAME_WIDTH, 0))
    return strip


def build_review(
    impact_frames: list[Image.Image],
    collapse_frames: list[Image.Image],
    rubble: Image.Image,
) -> None:
    background = (3, 6, 18, 255)
    ordered_frames = impact_frames + collapse_frames + [rubble] * 5
    durations = (
        [IMPACT_FRAME_MS] * len(impact_frames)
        + [COLLAPSE_FRAME_MS] * len(collapse_frames)
        + [180, 180, 180, 180, 420]
    )
    reviews: list[Image.Image] = []
    for frame in ordered_frames:
        review = Image.new(
            "RGBA",
            (FRAME_WIDTH, FRAME_HEIGHT),
            background,
        )
        review.alpha_composite(frame)
        reviews.append(
            review.resize(
                (FRAME_WIDTH * 3, FRAME_HEIGHT * 3),
                Image.Resampling.NEAREST,
            ).convert("RGB")
        )
    reviews[0].save(
        REVIEW_GIF,
        save_all=True,
        append_images=reviews[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=False,
    )


def main() -> None:
    impact_frames = [
        normalize_boulder(frame)
        for frame in load_frames(IMPACT_SOURCE, IMPACT_METADATA)
    ]
    collapse_frames = [
        normalize_boulder(frame)
        for frame in load_frames(COLLAPSE_SOURCE, COLLAPSE_METADATA)
    ]
    rubble = normalize_rubble(Image.open(RUBBLE_SOURCE).convert("RGBA"))

    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    collapse_frames[0].save(INTACT_RUNTIME, optimize=True)
    build_strip(impact_frames).save(IMPACT_RUNTIME, optimize=True)
    build_strip(collapse_frames).save(COLLAPSE_RUNTIME, optimize=True)
    rubble.save(RUBBLE_RUNTIME, optimize=True)
    build_review(impact_frames, collapse_frames, rubble)

    manifest = {
        "asset": "Vesperite route-obstruction boulder",
        "status": "local heavy-rifle preview candidate",
        "preview_query": "aryn=ludo&weapon=rifle",
        "runtime_contract": {
            "frame_size": [FRAME_WIDTH, FRAME_HEIGHT],
            "baseline_y": BASELINE_Y,
            "collision_size": [BOULDER_WIDTH, BOULDER_HEIGHT],
            "impact_frame_count": len(impact_frames),
            "impact_frame_ms": IMPACT_FRAME_MS,
            "collapse_frame_count": len(collapse_frames),
            "collapse_frame_ms": COLLAPSE_FRAME_MS,
        },
        "states": {
            "intact": str(INTACT_RUNTIME.relative_to(PROJECT_ROOT)),
            "impact": str(IMPACT_RUNTIME.relative_to(PROJECT_ROOT)),
            "collapse": str(COLLAPSE_RUNTIME.relative_to(PROJECT_ROOT)),
            "rubble": str(RUBBLE_RUNTIME.relative_to(PROJECT_ROOT)),
        },
        "gameplay_contract": {
            "collision": "solid while intact, impacted, or collapsing",
            "damage_source": "heavy rifle direct round",
            "hits_required": HITS_REQUIRED,
            "traversal": "taller than Aryn's unassisted jump apex",
            "remnant": "persistent rubble with no collision",
            "pack_blaster": "does not clear the obstruction",
            "preview_only": True,
        },
        "notes": [
            "Each of the first two hits plays the impact sequence and leaves the boulder solid.",
            "The third impact flows into collapse without restoring player control through the rock.",
            "The solid top prevents platform drops from embedding Aryn inside the obstruction.",
            "The final rubble remains as environmental continuity after collision is removed.",
        ],
    }
    MANIFEST_OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n")

    for output in (
        INTACT_RUNTIME,
        IMPACT_RUNTIME,
        COLLAPSE_RUNTIME,
        RUBBLE_RUNTIME,
        REVIEW_GIF,
        MANIFEST_OUTPUT,
    ):
        print(f"Wrote {output.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
