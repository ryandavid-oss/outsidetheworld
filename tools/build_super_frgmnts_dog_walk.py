#!/usr/bin/env python3
"""Build the readable two-phase Veyra camp-dog gait for the overworld."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUTPOST = ROOT / "Design/Super-Frgmnts/Overworld/Phase-3/Outpost"
ASSETS = OUTPOST / "Assets"
PUBLIC_ASSETS = ROOT / "Images/Game/Super-Frgmnts"

FRAME_SPECS = (
    (
        ASSETS / "veyra-camp-dog-walk-contact-master-v2.png",
        ASSETS / "veyra-camp-dog-walk-contact-runtime-v2.png",
    ),
    (
        ASSETS / "veyra-camp-dog-walk-pass-master-v2.png",
        ASSETS / "veyra-camp-dog-walk-pass-runtime-v2.png",
    ),
)
SHEET = ASSETS / "veyra-camp-dog-walk-sheet-v2.png"
PUBLIC_SHEET = PUBLIC_ASSETS / "veyra-camp-dog-walk-sheet-v2.png"

RUNTIME_SIZE = (96, 64)
SUBJECT_LIMIT = (80, 56)
SUBJECT_BOTTOM = 60


def build_runtime(master_path: Path) -> Image.Image:
    source = Image.open(master_path).convert("RGBA")
    alpha_box = source.getchannel("A").getbbox()
    if alpha_box is None:
        raise ValueError(f"No visible dog pixels in {master_path}")

    dog = source.crop(alpha_box)
    scale = min(
        SUBJECT_LIMIT[0] / dog.width,
        SUBJECT_LIMIT[1] / dog.height,
    )
    target = (
        max(1, round(dog.width * scale)),
        max(1, round(dog.height * scale)),
    )
    dog = dog.resize(target, Image.Resampling.LANCZOS)

    runtime = Image.new("RGBA", RUNTIME_SIZE, (0, 0, 0, 0))
    runtime.alpha_composite(
        dog,
        (
            (RUNTIME_SIZE[0] - dog.width) // 2,
            SUBJECT_BOTTOM - dog.height,
        ),
    )
    return runtime


def main() -> None:
    frames = []
    for master_path, runtime_path in FRAME_SPECS:
        runtime = build_runtime(master_path)
        runtime.save(runtime_path, optimize=True)
        frames.append(runtime)

    sheet = Image.new(
        "RGBA",
        (RUNTIME_SIZE[0] * len(frames), RUNTIME_SIZE[1]),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(frames):
        sheet.alpha_composite(frame, (index * RUNTIME_SIZE[0], 0))
    sheet.save(SHEET, optimize=True)
    PUBLIC_ASSETS.mkdir(parents=True, exist_ok=True)
    sheet.save(PUBLIC_SHEET, optimize=True)

    print(
        f"Wrote {len(frames)} walk frames, {SHEET.relative_to(ROOT)}, "
        f"and {PUBLIC_SHEET.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
