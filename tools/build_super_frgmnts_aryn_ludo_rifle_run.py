#!/usr/bin/env python3
"""Build Aryn's authored heavy-rifle running and firing runtime atlases."""

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

SOURCE_SHEET = RAW_ROOT / "aryn-ludo-rifle-run-fire-sheet-v1.png"
SOURCE_METADATA = RAW_ROOT / "aryn-ludo-rifle-run-fire-sheet-v1.json"
READY_RUNTIME = RUNTIME_ROOT / "aryn-rifle-run-ready-ludo-runtime-v1.png"
FIRE_RUNTIME = RUNTIME_ROOT / "aryn-rifle-run-fire-ludo-runtime-v1.png"
READY_REVIEW = REVIEW_ROOT / "aryn-ludo-rifle-run-ready-preview-v1.gif"
FIRE_REVIEW = REVIEW_ROOT / "aryn-ludo-rifle-run-fire-preview-v1.gif"
CONTACT_SHEET = REVIEW_ROOT / "aryn-ludo-rifle-run-contact-v1.png"
MANIFEST_OUTPUT = LUDO_ROOT / "aryn-ludo-rifle-run-runtime-v1.json"

SOURCE_FRAME_SIZE = (592, 552)
RUNTIME_FRAME_SIZE = 112
RUNTIME_RESIZE = (98, 91)
RUNTIME_X_OFFSET = 7
RUNTIME_BASELINE_Y = 105
FRAME_DURATION_MS = 58
REVIEW_BACKGROUND = (3, 6, 18, 255)

# Frames 15-23 are a complete gait; frame 24 returns very closely to frame 15.
# Removing only the generated muzzle material produces a stable rifle-ready run.
READY_SOURCE_FRAMES = tuple(range(15, 24))

# Frames 10-17 contain a clean lead-in, one authored muzzle pulse, recoil, and
# recovery. At the supplied 58 ms cadence they fit one heavy-rifle shot.
FIRE_SOURCE_FRAMES = tuple(range(10, 18))


def load_source_frames() -> list[Image.Image]:
    sheet = Image.open(SOURCE_SHEET).convert("RGBA")
    metadata = json.loads(SOURCE_METADATA.read_text())
    entries = [metadata["frames"][key] for key in sorted(metadata["frames"])]
    if len(entries) != 25:
        raise ValueError(f"Expected 25 source frames, found {len(entries)}")

    frames: list[Image.Image] = []
    for index, entry in enumerate(entries):
        rect = entry["frame"]
        size = (rect["w"], rect["h"])
        if size != SOURCE_FRAME_SIZE:
            raise ValueError(
                f"Frame {index} is {size}; expected {SOURCE_FRAME_SIZE}"
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
    reduced = source.resize(RUNTIME_RESIZE, Image.Resampling.LANCZOS)
    bounds = reduced.getbbox()
    if bounds is None:
        raise ValueError("Cannot normalize an empty rifle-running frame")
    offset_y = RUNTIME_BASELINE_Y - bounds[3]
    runtime = Image.new(
        "RGBA",
        (RUNTIME_FRAME_SIZE, RUNTIME_FRAME_SIZE),
        (0, 0, 0, 0),
    )
    runtime.alpha_composite(reduced, (RUNTIME_X_OFFSET, offset_y))
    return runtime


def without_muzzle(source: Image.Image) -> Image.Image:
    """Remove generated flash/smoke while preserving the rifle barrel."""
    clean = source.copy()
    pixels = clean.load()
    for y in range(source.height):
        for x in range(395, source.width):
            red, green, blue, alpha = pixels[x, y]
            if alpha == 0:
                continue
            warm_flash = red > 115 and green > 45 and red > blue * 1.24
            pale_core = red > 185 and green > 155 and blue > 105
            if warm_flash or pale_core:
                pixels[x, y] = (0, 0, 0, 0)
    # The generator also leaves a pale smoke tongue on one recovery frame.
    # The authored barrel ends at this shared plane, so this stabilizes its
    # silhouette while removing all remaining particles.
    clean.paste((0, 0, 0, 0), (430, 0, source.width, source.height))
    return clean


def select_runtime_frames(
    source_frames: list[Image.Image],
    indices: tuple[int, ...],
    remove_muzzle: bool,
) -> list[Image.Image]:
    return [
        normalize_fixed_canvas(
            without_muzzle(source_frames[index])
            if remove_muzzle
            else source_frames[index]
        )
        for index in indices
    ]


def build_strip(frames: list[Image.Image]) -> Image.Image:
    strip = Image.new(
        "RGBA",
        (RUNTIME_FRAME_SIZE * len(frames), RUNTIME_FRAME_SIZE),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(frames):
        strip.alpha_composite(frame, (index * RUNTIME_FRAME_SIZE, 0))
    return strip


def build_review(frames: list[Image.Image], output: Path, hold_ms: int) -> None:
    reviews: list[Image.Image] = []
    for frame in frames:
        review = Image.new(
            "RGBA",
            (RUNTIME_FRAME_SIZE, RUNTIME_FRAME_SIZE),
            REVIEW_BACKGROUND,
        )
        review.alpha_composite(frame)
        reviews.append(
            review.resize((336, 336), Image.Resampling.NEAREST).convert("RGB")
        )
    reviews[0].save(
        output,
        save_all=True,
        append_images=reviews[1:] + [reviews[-1]],
        duration=[FRAME_DURATION_MS] * len(reviews) + [hold_ms],
        loop=0,
        disposal=2,
        optimize=False,
    )


def build_contact_sheet(
    ready_frames: list[Image.Image],
    fire_frames: list[Image.Image],
) -> None:
    columns = max(len(ready_frames), len(fire_frames))
    contact = Image.new(
        "RGBA",
        (columns * RUNTIME_FRAME_SIZE, 286),
        REVIEW_BACKGROUND,
    )
    draw = ImageDraw.Draw(contact)
    rows = (
        ("RIFLE READY RUN // CLEAN GAIT", ready_frames, READY_SOURCE_FRAMES, 6),
        ("MOVING HEAVY SHOT // AUTHORED PULSE", fire_frames, FIRE_SOURCE_FRAMES, 145),
    )
    for title, frames, source_indices, y in rows:
        draw.text((8, y), title, fill=(235, 240, 255, 255))
        for frame_index, frame in enumerate(frames):
            x = frame_index * RUNTIME_FRAME_SIZE
            contact.alpha_composite(frame, (x, y + 18))
            draw.text(
                (x + 4, y + 119),
                f"{frame_index} / src {source_indices[frame_index]}",
                fill=(88, 245, 223, 255),
            )
    contact.resize(
        (contact.width * 2, contact.height * 2),
        Image.Resampling.NEAREST,
    ).save(CONTACT_SHEET, optimize=True)


def write_manifest() -> None:
    manifest = {
        "asset": "Aryn Sol-Mavi authored heavy-rifle running set",
        "status": "active Episode runtime",
        "source_sheet": str(SOURCE_SHEET.relative_to(PROJECT_ROOT)),
        "source_metadata": str(SOURCE_METADATA.relative_to(PROJECT_ROOT)),
        "runtime_contract": {
            "frame_size": [RUNTIME_FRAME_SIZE, RUNTIME_FRAME_SIZE],
            "source_frame_size": list(SOURCE_FRAME_SIZE),
            "source_resize": list(RUNTIME_RESIZE),
            "horizontal_offset": RUNTIME_X_OFFSET,
            "baseline_y": RUNTIME_BASELINE_Y,
            "frame_duration_ms": FRAME_DURATION_MS,
        },
        "ready_run": {
            "source_frames": list(READY_SOURCE_FRAMES),
            "frame_count": len(READY_SOURCE_FRAMES),
            "runtime": str(READY_RUNTIME.relative_to(PROJECT_ROOT)),
            "muzzle_treatment": (
                "flash colors removed beyond source x=395; particles clipped "
                "at the shared barrel plane x=430"
            ),
        },
        "moving_fire": {
            "source_frames": list(FIRE_SOURCE_FRAMES),
            "frame_count": len(FIRE_SOURCE_FRAMES),
            "runtime": str(FIRE_RUNTIME.relative_to(PROJECT_ROOT)),
            "duration_ms": len(FIRE_SOURCE_FRAMES) * FRAME_DURATION_MS,
        },
        "design_contract": {
            "first_shot_still_draws": True,
            "ground_running_does_not_stow_rifle": True,
            "airborne_movement_preserves_rifle": True,
            "airborne_fire_uses_authored_full_body_motion": True,
            "moving_fire_uses_authored_full_body_motion": True,
            "pack_blaster_remains_default": True,
        },
        "notes": [
            "The authored full-body motion replaces the split-body prototype.",
            "The rifle-ready gait and firing pulse share the supplied body registration.",
            "Stationary draw, ready, and firing animations remain available.",
            "Aryn keeps the rifle through jumps, drops, and falls and can fire airborne.",
        ],
    }
    MANIFEST_OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n")


def main() -> None:
    source_frames = load_source_frames()
    ready_frames = select_runtime_frames(
        source_frames,
        READY_SOURCE_FRAMES,
        remove_muzzle=True,
    )
    fire_frames = select_runtime_frames(
        source_frames,
        FIRE_SOURCE_FRAMES,
        remove_muzzle=False,
    )

    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    build_strip(ready_frames).save(READY_RUNTIME, optimize=True)
    build_strip(fire_frames).save(FIRE_RUNTIME, optimize=True)
    build_review(ready_frames, READY_REVIEW, hold_ms=58)
    build_review(fire_frames, FIRE_REVIEW, hold_ms=180)
    build_contact_sheet(ready_frames, fire_frames)
    write_manifest()

    for output in (
        READY_RUNTIME,
        FIRE_RUNTIME,
        READY_REVIEW,
        FIRE_REVIEW,
        CONTACT_SHEET,
        MANIFEST_OUTPUT,
    ):
        print(f"Wrote {output.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
