#!/usr/bin/env python3
"""Build normalized preview candidates for Foundry pickups and economy assets."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PICKUP_ROOT = (
    PROJECT_ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Power-Ups"
)
RAW_ROOT = PICKUP_ROOT / "Raw"
REVIEW_ROOT = PICKUP_ROOT / "Reviews"
RUNTIME_ROOT = PROJECT_ROOT / "Images" / "Game" / "Super-Frgmnts"
MANIFEST_OUTPUT = PICKUP_ROOT / "foundry-pickup-runtime-v1.json"
CONTACT_SHEET = REVIEW_ROOT / "foundry-pickup-contact-v1.png"

ASSETS = {
    "galactic_credit_coin": {
        "source": RAW_ROOT / "galactic-credit-coin-source-v1.png",
        "runtime": RUNTIME_ROOT / "foundry-credit-coin-runtime-v1.png",
        "canvas": (48, 48),
        "visible": (44, 30),
        "role": "currency released by credit crates",
        "status": "art ready; economy value deliberately unassigned",
    },
    "jetpack_pickup": {
        "source": RAW_ROOT / "jetpack-pickup-source-v1.png",
        "runtime": RUNTIME_ROOT / "foundry-jetpack-pickup-runtime-v1.png",
        "canvas": (72, 80),
        "visible": (62, 72),
        "role": "pack-assisted traversal unlock",
        "status": "art ready; duration and fuel model deliberately unassigned",
    },
    "galactic_credit_crate": {
        "source": RAW_ROOT / "galactic-credit-crate-source-v1.png",
        "runtime": RUNTIME_ROOT / "foundry-credit-crate-runtime-v1.png",
        "canvas": (112, 80),
        "visible": (104, 68),
        "role": "shootable container that releases Galactic Credits",
        "status": "art ready; opening and coin-burst animation pending",
    },
    "vesperite": {
        "source": RAW_ROOT / "vesperite-source-v1.png",
        "runtime": RUNTIME_ROOT / "foundry-vesperite-runtime-v1.png",
        "canvas": (72, 72),
        "visible": (64, 58),
        "role": "Veyran energy material and mission-economy object",
        "status": "art ready; collectible role deliberately unassigned",
    },
    "heavy_rifle_pickup": {
        "source": RAW_ROOT / "heavy-rifle-pickup-source-v1.png",
        "runtime": RUNTIME_ROOT / "foundry-heavy-rifle-pickup-runtime-v1.png",
        "canvas": (136, 64),
        "visible": (128, 48),
        "role": "temporary route-clearing, boss-killing, and heavy-combat weapon unlock",
        "status": "art ready; placement and persistence deliberately unassigned",
    },
}


def normalize(
    source_path: Path,
    canvas_size: tuple[int, int],
    visible_size: tuple[int, int],
) -> Image.Image:
    source = Image.open(source_path).convert("RGBA")
    bounds = source.getbbox()
    if bounds is None:
        raise ValueError(f"{source_path.name} contains no visible pixels")
    cropped = source.crop(bounds)
    target_width, target_height = visible_size
    scale = min(
        target_width / cropped.width,
        target_height / cropped.height,
    )
    reduced = cropped.resize(
        (
            max(1, round(cropped.width * scale)),
            max(1, round(cropped.height * scale)),
        ),
        Image.Resampling.LANCZOS,
    )
    runtime = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    runtime.alpha_composite(
        reduced,
        (
            round((canvas_size[0] - reduced.width) / 2),
            canvas_size[1] - reduced.height - 4,
        ),
    )
    return runtime


def build_contact_sheet(runtime_images: dict[str, Image.Image]) -> None:
    panel_width = 184
    width = panel_width * len(runtime_images)
    height = 164
    background = (3, 6, 18, 255)
    contact = Image.new("RGBA", (width, height), background)
    draw = ImageDraw.Draw(contact)

    for index, (key, image) in enumerate(runtime_images.items()):
        left = index * panel_width
        draw.rectangle(
            (left + 4, 4, left + panel_width - 5, height - 5),
            outline=(65, 101, 136, 255),
            width=2,
        )
        preview_scale = min(
            (panel_width - 20) / image.width,
            112 / image.height,
        )
        preview = image.resize(
            (
                round(image.width * preview_scale),
                round(image.height * preview_scale),
            ),
            Image.Resampling.NEAREST,
        )
        contact.alpha_composite(
            preview,
            (
                left + round((panel_width - preview.width) / 2),
                12,
            ),
        )
        draw.text(
            (left + 10, 132),
            key.replace("_", " ").upper(),
            fill=(235, 240, 255, 255),
        )

    contact.save(CONTACT_SHEET, optimize=True)


def main() -> None:
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)

    runtime_images: dict[str, Image.Image] = {}
    manifest_assets: dict[str, dict[str, object]] = {}
    for key, contract in ASSETS.items():
        runtime = normalize(
            contract["source"],
            contract["canvas"],
            contract["visible"],
        )
        runtime.save(contract["runtime"], optimize=True)
        runtime_images[key] = runtime
        manifest_assets[key] = {
            "source": str(contract["source"].relative_to(PROJECT_ROOT)),
            "runtime": str(contract["runtime"].relative_to(PROJECT_ROOT)),
            "runtime_size": list(runtime.size),
            "role": contract["role"],
            "status": contract["status"],
        }

    build_contact_sheet(runtime_images)
    manifest = {
        "package": "SUPER FRGMNTS Foundry pickups and economy candidates",
        "status": "normalized art only; gameplay integration pending",
        "assets": manifest_assets,
        "design_boundaries": [
            "Galactic Credits and Signal Shards remain separate systems.",
            "Vesperite is not assigned a collectible value by this build.",
            "Power-up duration, persistence, and purchase prices remain open.",
            "No runtime game code loads these candidates yet.",
        ],
    }
    MANIFEST_OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n")

    for contract in ASSETS.values():
        print(f"Wrote {contract['runtime'].relative_to(PROJECT_ROOT)}")
    print(f"Wrote {CONTACT_SHEET.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {MANIFEST_OUTPUT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
