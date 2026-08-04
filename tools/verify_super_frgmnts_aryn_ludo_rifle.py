#!/usr/bin/env python3
"""Verify the retired Ludo heavy rifle remains archival-review only."""

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
RUN_MANIFEST = LUDO_ROOT / "aryn-ludo-rifle-run-runtime-v1.json"
DRAW_RUNTIME = (
    ROOT / "Images/Game/Super-Frgmnts/aryn-rifle-draw-ludo-runtime-v1.png"
)
FIRE_RUNTIME = (
    ROOT / "Images/Game/Super-Frgmnts/aryn-rifle-fire-ludo-runtime-v1.png"
)
RUN_READY_RUNTIME = (
    ROOT
    / "Images/Game/Super-Frgmnts/aryn-rifle-run-ready-ludo-runtime-v1.png"
)
RUN_FIRE_RUNTIME = (
    ROOT
    / "Images/Game/Super-Frgmnts/aryn-rifle-run-fire-ludo-runtime-v1.png"
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
    run_manifest = json.loads(RUN_MANIFEST.read_text())
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
    verify_strip(
        RUN_READY_RUNTIME,
        run_manifest["ready_run"]["frame_count"],
        contract["baseline_y"],
    )
    verify_strip(
        RUN_FIRE_RUNTIME,
        run_manifest["moving_fire"]["frame_count"],
        contract["baseline_y"],
    )

    require(
        manifest["design_contract"]["production_default"]
        == "backpack telescopic laser seeker",
        "The rifle replaced the production-default telescopic laser seeker",
    )
    require(
        manifest["design_contract"]["episode_beta_pickup"] is True,
        "The rifle is not marked as an Episode beta pickup",
    )
    require(
        manifest["design_contract"]["combat_balance"].endswith(
            "remain undecided"
        ),
        "The rifle manifest prematurely fixes combat balance",
    )

    archival_runtime_contracts = (
        'previewParameters.get("weapon") === "rifle";',
        "/Images/Game/Super-Frgmnts/aryn-rifle-draw-ludo-runtime-v1.png",
        "/Images/Game/Super-Frgmnts/aryn-rifle-fire-ludo-runtime-v1.png",
        "/Images/Game/Super-Frgmnts/aryn-rifle-run-ready-ludo-runtime-v1.png",
        "/Images/Game/Super-Frgmnts/aryn-rifle-run-fire-ludo-runtime-v1.png",
        '"rifleDrawLudo",',
        '"rifleFireLudo",',
        '"rifleRunReadyLudo",',
        '"rifleRunFireLudo",',
        "function heavyRifleActive()",
        "return riflePreview;",
        "// Production progression is PACK-only.",
    )
    for runtime_contract in archival_runtime_contracts:
        require(
            runtime_contract in source,
            f"Missing archival rifle review contract: {runtime_contract}",
        )

    require(
        "aryn-ludo-rifle-shoot-reference-v1.png" not in source,
        "The raw rifle shooting master is loaded by the game",
    )
    require(
        "aryn-ludo-rifle-draw-reference-v1.png" not in source,
        "The raw rifle draw master is loaded by the game",
    )
    require(
        run_manifest["design_contract"]["ground_running_does_not_stow_rifle"]
        is True,
        "The authored running-rifle contract still stows during ground movement",
    )
    require(
        run_manifest["design_contract"]["airborne_movement_preserves_rifle"]
        is True,
        "The running-rifle contract does not preserve the rifle in the air",
    )
    require(
        run_manifest["design_contract"][
            "airborne_fire_uses_authored_full_body_motion"
        ]
        is True,
        "The running-rifle contract does not support airborne fire",
    )
    require('id="weaponToggle"' not in source, "Production still exposes weapon swapping")
    require('id="weaponToggleMode"' not in source, "Production still labels a weapon swap")
    require(
        'makeBetaPickup("rifle"' not in source,
        "Production still spawns the retired heavy-rifle pickup",
    )
    require(
        'return event.code === "KeyX";' in source,
        "Keyboard firing is not mapped to X",
    )
    require(
        "ControlLeft" not in source and "ControlRight" not in source,
        "The conflicting macOS Control firing shortcut is still active",
    )
    require(
        contract["standing_foresection_shift"] == 14,
        "Standing rifle foresection is not normalized to the running rifle",
    )

    print("SUPER FRGMNTS archival Ludo heavy-rifle contract: PASS")
    print("- authored standing and moving strips remain intact for preservation")
    print("- the rifle is reachable only through its explicit archival review route")
    print("- production exposes neither a rifle pickup nor weapon-swap control")
    print("- keyboard fire uses X, avoiding the macOS Control-arrow shortcut")
    print("- the modular PACK is the only production combat chassis")


if __name__ == "__main__":
    main()
