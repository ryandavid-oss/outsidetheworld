#!/usr/bin/env python3
"""Build The Wound v3 wide boss-room plate, slices, and scale reviews."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Boss-Room"
)
MASTER_SOURCE = (
    PACKAGE
    / "Raw"
    / "wound-boss-room-background-master-v3-source.png"
)
MASTER = (
    PACKAGE
    / "Raw"
    / "wound-boss-room-background-master-v3.png"
)
RUNTIME_LEFT = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "foundry-wound-boss-room-background-runtime-v3-left.png"
)
RUNTIME_RIGHT = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "foundry-wound-boss-room-background-runtime-v3-right.png"
)
TITLE_RUNTIME = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "foundry-wound-boss-room-title-runtime-v3.png"
)
REVIEWS = PACKAGE / "Reviews"
SCALE_REVIEW = REVIEWS / "wound-boss-room-scale-review-v3.png"
SWEEP_REVIEW = REVIEWS / "wound-boss-room-sweep-review-v3.png"

ARYN = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "aryn-command-rest-runtime-v1.png"
)
SEAM_WALK = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "enemy-tall-gaunt-alien-walk-sheet-v1.png"
)
SEAM_ATTACK = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "enemy-tall-gaunt-alien-attack-sheet-v1.png"
)

PLATE_SIZE = (2580, 1882)
RUNTIME_SLICE_SIZE = (1290, 1882)
TITLE_RUNTIME_SIZE = (1290, 941)
DECK_Y = 1360
SOURCE_DECK_Y = 697
ARYN_SIZE = (112, 112)
SEAM_WALK_SIZE = (448, 448)
SEAM_ATTACK_SIZE = (560, 448)


def paste_grounded(
    canvas: Image.Image,
    sprite: Image.Image,
    center_x: int,
    floor_y: int,
) -> None:
    alpha_bounds = sprite.getbbox()
    bottom_padding = (
        sprite.height - alpha_bounds[3]
        if alpha_bounds
        else 0
    )
    canvas.alpha_composite(
        sprite,
        (
            center_x - sprite.width // 2,
            floor_y - sprite.height + bottom_padding,
        ),
    )


def main() -> None:
    REVIEWS.mkdir(parents=True, exist_ok=True)
    RUNTIME_LEFT.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(MASTER_SOURCE) as source:
        source = source.convert("RGB")
        if source.height <= SOURCE_DECK_Y:
            raise ValueError(
                "Generated source does not contain the approved deck split"
            )
        upper = source.crop(
            (0, 0, source.width, SOURCE_DECK_Y)
        ).resize(
            (PLATE_SIZE[0], DECK_Y),
            Image.Resampling.NEAREST,
        )
        underdeck = source.crop(
            (
                0,
                SOURCE_DECK_Y,
                source.width,
                source.height,
            )
        ).resize(
            (PLATE_SIZE[0], PLATE_SIZE[1] - DECK_Y),
            Image.Resampling.NEAREST,
        )
    background = Image.new("RGB", PLATE_SIZE)
    background.paste(upper, (0, 0))
    background.paste(underdeck, (0, DECK_Y))
    background.save(MASTER, optimize=True)
    background.crop((0, 0, 1290, 1882)).save(
        RUNTIME_LEFT,
        optimize=True,
    )
    background.crop((1290, 0, 2580, 1882)).save(
        RUNTIME_RIGHT,
        optimize=True,
    )
    background.resize(
        TITLE_RUNTIME_SIZE,
        Image.Resampling.NEAREST,
    ).save(
        TITLE_RUNTIME,
        optimize=True,
    )

    with Image.open(ARYN) as source:
        aryn = source.convert("RGBA")
    if aryn.size != ARYN_SIZE:
        raise ValueError(
            f"Expected Aryn size {ARYN_SIZE}, received {aryn.size}"
        )

    with Image.open(SEAM_WALK) as source:
        walk = (
            source.convert("RGBA")
            .crop((0, 0, 128, 128))
            .transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            .resize(SEAM_WALK_SIZE, Image.Resampling.NEAREST)
        )

    with Image.open(SEAM_ATTACK) as source:
        attack_frame = 17
        source_x = attack_frame % 5 * 160
        source_y = attack_frame // 5 * 128
        sweep = (
            source.convert("RGBA")
            .crop((source_x, source_y, source_x + 160, source_y + 128))
            .transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            .resize(SEAM_ATTACK_SIZE, Image.Resampling.NEAREST)
        )

    scale_review = background.convert("RGBA")
    paste_grounded(scale_review, aryn, 140, DECK_Y)
    paste_grounded(scale_review, walk, 1280, DECK_Y)
    scale_review.convert("RGB").save(SCALE_REVIEW, optimize=True)

    sweep_review = background.convert("RGBA")
    paste_grounded(sweep_review, aryn, 140, DECK_Y)
    paste_grounded(sweep_review, sweep, 1280, DECK_Y)
    sweep_review.convert("RGB").save(SWEEP_REVIEW, optimize=True)

    print(
        f"{MASTER.relative_to(ROOT)} "
        f"{PLATE_SIZE[0]}x{PLATE_SIZE[1]}"
    )
    print(
        f"{RUNTIME_LEFT.relative_to(ROOT)} "
        f"{RUNTIME_SLICE_SIZE[0]}x{RUNTIME_SLICE_SIZE[1]}"
    )
    print(
        f"{RUNTIME_RIGHT.relative_to(ROOT)} "
        f"{RUNTIME_SLICE_SIZE[0]}x{RUNTIME_SLICE_SIZE[1]}"
    )
    print(
        f"{TITLE_RUNTIME.relative_to(ROOT)} "
        f"{TITLE_RUNTIME_SIZE[0]}x{TITLE_RUNTIME_SIZE[1]}"
    )
    print(f"{SCALE_REVIEW.relative_to(ROOT)}")
    print(f"{SWEEP_REVIEW.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
