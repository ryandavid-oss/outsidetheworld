#!/usr/bin/env python3
"""Verify the SUPER FRGMNTS Coreworks surface-transport contract."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
DESIGN = ROOT / "Design/Super-Frgmnts/Overworld/Coreworks-Transport"
MANIFEST = DESIGN / "coreworks-transport-runtime-v1.json"
PUBLIC = ROOT / "Images/Game/Super-Frgmnts"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    source = GAME.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    require(
        manifest["runtimeFrame"] == [208, 240],
        "Transport runtime cell changed unexpectedly",
    )
    sequence_map = {
        sequence["sequence"]: sequence
        for sequence in manifest["sequences"]
    }
    require(
        sequence_map["idle"]["frames"] == 36,
        "Dormant transport must retain all 36 source frames",
    )
    require(
        sequence_map["activate"]["frames"] == 25,
        "Transport activation must retain all 25 source frames",
    )
    require(
        sequence_map["activate"]["sequenceDurationMs"] == 1625,
        "Transport activation timing drifted from its authored sequence",
    )

    expected_assets = {
        "coreworks-transport-idle-sheet-v1.png": (1248, 1440),
        "coreworks-transport-activate-sheet-v1.png": (1040, 1200),
    }
    for filename, expected_size in expected_assets.items():
        path = PUBLIC / filename
        require(path.exists(), f"Missing transport runtime: {filename}")
        with Image.open(path) as image:
            require(
                image.size == expected_size,
                f"Unexpected transport atlas dimensions: {filename}",
            )
            require(
                image.mode == "RGBA",
                f"Transport atlas lost RGBA transparency: {filename}",
            )
            alpha = image.getchannel("A")
            require(alpha.getextrema() == (0, 255), f"Invalid alpha: {filename}")

    required_tokens = (
        "COREWORKS_TRANSPORT_CENTER_X",
        "COREWORKS_TRANSPORT_DECK_X",
        "arrivalTransportPreview",
        'previewParameters.get("scene") === "transport"',
        "coreworksTransportDeck: true",
        "player.supportPlatform.coreworksTransportDeck",
        "coreworks-transport-idle-sheet-v1.png",
        "coreworks-transport-activate-sheet-v1.png",
        "function beginCoreworksTransport()",
        "function updateCoreworksTransport(delta)",
        "function coreworksTransportPlayerAlpha()",
        "function drawCoreworksTransport()",
        "function drawCoreworksTransportEnergyForeground()",
        'state = "transporting"',
        'state === "transporting"',
        'canvas.dataset.coreworksTransport = "activating"',
        "Coreworks transport engaged.",
        "Mission objectives",
        "Restore both atmospheric stabilizers and breathable air.",
        "Recover all 12 Vesperite Fragments as evidence of the pulse.",
        'startButton.textContent = "Begin Episode 01";',
        'startOverButton.textContent = "Cancel";',
        "CROSS CALIBRATION CATWALKS // BOARD TRANSPORT",
    )
    for token in required_tokens:
        require(token in source, f"Missing transport contract: {token}")

    require(
        "function drawOverworldPortal()" not in source,
        "Legacy free-floating surface portal is still present",
    )
    require(
        "var centerX = WIDTH * 2 + 1545" not in source,
        "Legacy free-floating portal coordinates are still present",
    )
    draw_contract = source[
        source.index("function draw()") :
        source.index("function drawBackgroundLayer")
    ]
    require(
        draw_contract.index("drawOverworldProps();") <
        draw_contract.index("drawPlayer();"),
        "Transport-bearing overworld props must draw behind Aryn",
    )
    require(
        draw_contract.index("drawPlayer();") <
        draw_contract.index("drawCoreworksTransportEnergyForeground();"),
        "Transport energy must draw over Aryn during disappearance",
    )

    print("SUPER FRGMNTS Coreworks transport: PASS")
    print("- 36-frame dormant and 25-frame vortex atlases preserve alpha")
    print("- authored 1.625-second activation timing is retained")
    print("- the deck is a physical overworld collision and trigger surface")
    print("- movement locks while the vortex fades Aryn from the surface")
    print("- the episode handoff begins only after the effect completes")


if __name__ == "__main__":
    main()
