#!/usr/bin/env python3
"""Verify Aryn's opt-in Ludo heavy-rifle preview contract."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
LUDO_ROOT = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Overworld"
    / "Phase-3"
    / "Aryn"
    / "Ludo"
)
MANIFEST = LUDO_ROOT / "aryn-ludo-rifle-runtime-v1.json"
DRAW_RUNTIME = (
    ROOT / "Images/Game/Super-Frgmnts/aryn-rifle-draw-ludo-runtime-v1.png"
)
FIRE_RUNTIME = (
    ROOT / "Images/Game/Super-Frgmnts/aryn-rifle-fire-ludo-runtime-v1.png"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify_strip(path: Path, frame_count: int, baseline: int) -> None:
    require(path.is_file(), f"Missing runtime asset: {path.name}")
    image = Image.open(path).convert("RGBA")
    require(
        image.size == (112 * frame_count, 112),
        f"{path.name} is {image.size}; expected {(112 * frame_count, 112)}",
    )

    for index in range(frame_count):
        frame = image.crop((index * 112, 0, (index + 1) * 112, 112))
        bounds = frame.getbbox()
        require(bounds is not None, f"{path.name} frame {index} is empty")
        require(
            bounds[3] == baseline,
            f"{path.name} frame {index} ends at {bounds[3]}; expected {baseline}",
        )
        require(
            bounds[0] >= 0 and bounds[2] <= 112,
            f"{path.name} frame {index} exceeds its fixed runtime cell",
        )


def main() -> None:
    source = GAME.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text())
    contract = manifest["runtime_contract"]

    verify_strip(
        DRAW_RUNTIME,
        contract["draw_frame_count"],
        contract["baseline_y"],
    )
    verify_strip(
        FIRE_RUNTIME,
        contract["fire_frame_count"],
        contract["baseline_y"],
    )

    require(
        manifest["design_contract"]["production_default"]
        == "pack-mounted seeking blaster",
        "The rifle replaced the production-default pack blaster",
    )
    require(
        manifest["design_contract"]["episode_beta_pickup"] is True,
        "The rifle is not marked as an Episode beta pickup",
    )

    runtime_contracts = (
        'previewParameters.get("weapon") === "rifle";',
        "/Images/Game/Super-Frgmnts/aryn-rifle-draw-ludo-runtime-v1.png",
        "/Images/Game/Super-Frgmnts/aryn-rifle-fire-ludo-runtime-v1.png",
        '"rifleDrawLudo",',
        '"rifleFireLudo",',
        "var rifleReady = false;",
        "var riflePendingFire = false;",
        "function stowRifle()",
        "function beginRifleDraw()",
        "rifleDrawTime = 0;",
        "function heavyRifleActive()",
        "rifleFireTime = rifleActive ? RIFLE_FIRE_DURATION : 0;",
        'visual.pose = "rifleDrawLudo";',
        'visual.pose = "rifleFireLudo";',
        '? "rifle-ready"',
        ': "rifle-stowed"',
        "direct: rifleActive,",
        "player.vx = 0;",
        'canvas.dataset.arynWeapon = heavyRifleActive()',
        "riflePreview ||",
    )
    for runtime_contract in runtime_contracts:
        require(
            runtime_contract in source,
            f"Missing rifle preview contract: {runtime_contract}",
        )

    require(
        "aryn-ludo-rifle-shoot-reference-v1.png" not in source,
        "The raw rifle shooting master is loaded by the game",
    )
    require(
        "aryn-ludo-rifle-draw-reference-v1.png" not in source,
        "The raw rifle draw master is loaded by the game",
    )

    print("SUPER FRGMNTS Aryn Ludo heavy-rifle contract: PASS")
    print("- fixed-canvas draw and firing animation alignment")
    print("- rifle remains an optional Episode beta special weapon")
    print("- first fire draws; movement stows; next fire redraws")
    print("- firing is a fast direct amber route-clearing round")
    print("- pack blaster remains the production default")


if __name__ == "__main__":
    main()
