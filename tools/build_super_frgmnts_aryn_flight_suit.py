#!/usr/bin/env python3
"""Normalize Aryn's supplied flight-suit run and jump sheets for RD-42."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = (
    PROJECT_ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Overworld"
    / "Phase-3"
    / "Aryn"
    / "Flight-Suit"
)
RAW_ROOT = ASSET_ROOT / "Raw"
REVIEW_ROOT = ASSET_ROOT / "Reviews"
RUNTIME_ROOT = PROJECT_ROOT / "Images" / "Game" / "Super-Frgmnts"

FRAME_SIZE = 112
GRID_COLUMNS = 6
GRID_ROWS = 6
FRAME_COUNT = GRID_COLUMNS * GRID_ROWS
BASELINE_Y = 104
BACKGROUND = (3, 6, 18, 255)


@dataclass(frozen=True)
class Sequence:
    name: str
    source_stem: str
    source_frame_size: tuple[int, int]
    frame_duration_ms: int
    normalized_size: tuple[int, int]
    normalized_offset: tuple[int, int]
    phase_map: dict[str, list[int]]

    @property
    def source(self) -> Path:
        return RAW_ROOT / f"{self.source_stem}.png"

    @property
    def metadata(self) -> Path:
        return RAW_ROOT / f"{self.source_stem}.json"

    @property
    def runtime(self) -> Path:
        return (
            RUNTIME_ROOT
            / f"aryn-flight-suit-{self.name}-runtime-v1.png"
        )

    @property
    def review(self) -> Path:
        return (
            REVIEW_ROOT
            / f"aryn-flight-suit-{self.name}-preview-v1.gif"
        )

    @property
    def contact(self) -> Path:
        return (
            REVIEW_ROOT
            / f"aryn-flight-suit-{self.name}-contact-v1.png"
        )


SEQUENCES = (
    Sequence(
        name="run",
        source_stem="aryn-flight-suit-run-source-v1",
        source_frame_size=(316, 626),
        frame_duration_ms=78,
        normalized_size=(51, 100),
        normalized_offset=(30, 5),
        phase_map={
            "neutral_lead_in": [0, 6],
            "run_cycle": [7, 32],
            "neutral_resolve": [33, 35],
        },
    ),
    Sequence(
        name="jump",
        source_stem="aryn-flight-suit-jump-source-v1",
        source_frame_size=(284, 596),
        frame_duration_ms=71,
        normalized_size=(54, 113),
        normalized_offset=(29, 1),
        phase_map={
            "anticipation": [0, 10],
            "takeoff_and_airborne": [11, 17],
            "descent_and_landing": [18, 29],
            "neutral_resolve": [30, 35],
        },
    ),
)

MANIFEST = ASSET_ROOT / "aryn-flight-suit-movement-v1.json"


def load_frames(sequence: Sequence) -> list[Image.Image]:
    sheet = Image.open(sequence.source).convert("RGBA")
    metadata = json.loads(
        sequence.metadata.read_text(encoding="utf-8")
    )
    entries = [
        metadata["frames"][key]
        for key in sorted(metadata["frames"])
    ]
    if len(entries) != FRAME_COUNT:
        raise ValueError(
            f"Expected {FRAME_COUNT} {sequence.name} frames; "
            f"found {len(entries)}"
        )
    durations = {entry["duration"] for entry in entries}
    if durations != {sequence.frame_duration_ms}:
        raise ValueError(
            f"Expected uniform {sequence.frame_duration_ms} ms "
            f"{sequence.name} frames; found {sorted(durations)}"
        )

    expected_sheet_size = (
        GRID_COLUMNS * sequence.source_frame_size[0],
        GRID_ROWS * sequence.source_frame_size[1],
    )
    if sheet.size != expected_sheet_size:
        raise ValueError(
            f"{sequence.name} sheet is {sheet.size}; "
            f"expected {expected_sheet_size}"
        )

    frames: list[Image.Image] = []
    for index, entry in enumerate(entries):
        rect = entry["frame"]
        if (
            rect["w"],
            rect["h"],
        ) != sequence.source_frame_size:
            raise ValueError(
                f"{sequence.name} frame {index} is "
                f"{rect['w']}x{rect['h']}; expected "
                f"{sequence.source_frame_size[0]}x"
                f"{sequence.source_frame_size[1]}"
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


def normalize(
    sequence: Sequence,
    source: Image.Image,
) -> Image.Image:
    reduced = source.resize(
        sequence.normalized_size,
        Image.Resampling.LANCZOS,
    )
    runtime = Image.new(
        "RGBA",
        (FRAME_SIZE, FRAME_SIZE),
        (0, 0, 0, 0),
    )
    runtime.alpha_composite(
        reduced,
        sequence.normalized_offset,
    )
    return runtime


def build_atlas(
    sequence: Sequence,
    frames: list[Image.Image],
) -> None:
    atlas = Image.new(
        "RGBA",
        (
            GRID_COLUMNS * FRAME_SIZE,
            GRID_ROWS * FRAME_SIZE,
        ),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(frames):
        atlas.alpha_composite(
            frame,
            (
                (index % GRID_COLUMNS) * FRAME_SIZE,
                (index // GRID_COLUMNS) * FRAME_SIZE,
            ),
        )
    atlas.save(sequence.runtime, optimize=True)


def gif_durations(
    frame_count: int,
    source_duration_ms: int,
) -> list[int]:
    """Distribute GIF centiseconds while preserving total cadence."""
    target_total = round(
        frame_count * source_duration_ms / 10
    ) * 10
    short_count = (
        frame_count * 80 - target_total
    ) // 10
    long_count = frame_count - short_count
    durations: list[int] = []
    accumulator = 0
    for _ in range(frame_count):
        accumulator += long_count
        if accumulator >= frame_count:
            durations.append(80)
            accumulator -= frame_count
        else:
            durations.append(70)
    if sum(durations) != target_total:
        raise ValueError(
            f"Could not represent {target_total} ms GIF cadence"
        )
    return durations


def build_review(
    sequence: Sequence,
    frames: list[Image.Image],
) -> None:
    reviews: list[Image.Image] = []
    for frame in frames:
        review = Image.new(
            "RGBA",
            (FRAME_SIZE, FRAME_SIZE),
            BACKGROUND,
        )
        review.alpha_composite(frame)
        reviews.append(
            review.resize(
                (FRAME_SIZE * 4, FRAME_SIZE * 4),
                Image.Resampling.NEAREST,
            ).convert("RGB")
        )
    reviews[0].save(
        sequence.review,
        save_all=True,
        append_images=reviews[1:],
        duration=gif_durations(
            len(reviews),
            sequence.frame_duration_ms,
        ),
        loop=0,
        disposal=2,
        optimize=False,
    )


def build_contact(
    sequence: Sequence,
    frames: list[Image.Image],
) -> None:
    panel = 128
    contact = Image.new(
        "RGBA",
        (GRID_COLUMNS * panel, GRID_ROWS * 144),
        BACKGROUND,
    )
    draw = ImageDraw.Draw(contact)
    for index, frame in enumerate(frames):
        column = index % GRID_COLUMNS
        row = index // GRID_COLUMNS
        x = column * panel
        y = row * 144
        contact.alpha_composite(frame, (x + 8, y + 4))
        draw.text(
            (x + 8, y + 120),
            (
                f"{index:02d} // "
                f"{index * sequence.frame_duration_ms:04d} ms"
            ),
            fill=(88, 245, 223, 255),
        )
    contact.resize(
        (contact.width * 2, contact.height * 2),
        Image.Resampling.NEAREST,
    ).save(sequence.contact, optimize=True)


def relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def build_manifest() -> None:
    sequences: dict[str, object] = {}
    for sequence in SEQUENCES:
        sequences[sequence.name] = {
            "source": {
                "image": relative(sequence.source),
                "metadata": relative(sequence.metadata),
                "frame_size": list(
                    sequence.source_frame_size
                ),
                "grid": [GRID_COLUMNS, GRID_ROWS],
                "frame_count": FRAME_COUNT,
                "frame_duration_ms":
                    sequence.frame_duration_ms,
                "total_duration_ms":
                    FRAME_COUNT * sequence.frame_duration_ms,
            },
            "runtime": {
                "image": relative(sequence.runtime),
                "frame_size": [FRAME_SIZE, FRAME_SIZE],
                "atlas_size": [
                    GRID_COLUMNS * FRAME_SIZE,
                    GRID_ROWS * FRAME_SIZE,
                ],
                "grid": [GRID_COLUMNS, GRID_ROWS],
                "normalized_source_size": list(
                    sequence.normalized_size
                ),
                "normalized_offset": list(
                    sequence.normalized_offset
                ),
                "baseline_y": BASELINE_Y,
            },
            "phase_map": sequence.phase_map,
            "reviews": {
                "animation": relative(sequence.review),
                "contact_sheet": relative(sequence.contact),
            },
        }

    manifest = {
        "asset": "Aryn Sol-Mavi flight-suit movement",
        "status":
            "normalized and integrated for persistent RD-42 movement",
        "sequences": sequences,
        "runtime_behavior": {
            "scope": "RD-42 interior only",
            "idle_source":
                "armor-change frame 35 resolved flight-suit hold",
            "run_source":
                "flight-suit run frames 7-32 loop",
            "jump_source":
                "flight-suit jump phases mapped to physics",
            "rearm":
                "return to the flight/suit alcove and press Down",
        },
        "design_boundaries": [
            "Flight-suit locomotion persists while Aryn explores the RD-42 main deck.",
            "The supplied run lead-in and resolve frames are retained for provenance but the runtime loop uses frames 7-32.",
            "The authored jump poses are mapped to takeoff, airborne velocity, descent, and landing rather than forced into a 2.556 second canned jump.",
            "Aryn must restore field armor before using the dorsal hatch or securing the service kit.",
            "Unarmored damage, weapon, hatch traversal, and keel-deck animation remain outside this asset set.",
            "Reverse armor-change playback remains provisional until an authored re-arm sequence exists.",
        ],
        "review_route":
            "super_frgmnts.html?preview=ship-interior&autostart=1",
    }
    MANIFEST.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    for sequence in SEQUENCES:
        frames = [
            normalize(sequence, frame)
            for frame in load_frames(sequence)
        ]
        build_atlas(sequence, frames)
        build_review(sequence, frames)
        build_contact(sequence, frames)
        for output in (
            sequence.runtime,
            sequence.review,
            sequence.contact,
        ):
            print(f"Wrote {relative(output)}")
    build_manifest()
    print(f"Wrote {relative(MANIFEST)}")


if __name__ == "__main__":
    main()
