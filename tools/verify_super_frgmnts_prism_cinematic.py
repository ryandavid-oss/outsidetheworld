#!/usr/bin/env python3
"""Verify the first-run Foundry Prism cinematic and its approved panels."""

from __future__ import annotations

import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
ASSET_ROOT = ROOT / "Images" / "Game" / "Super-Frgmnts"
PANELS = (
    "aryn-prism-comic-panel-01-diet-coke-discover-v1.png",
    "aryn-prism-comic-panel-02-diet-coke-drink-v1.png",
    "aryn-prism-comic-panel-03-diet-coke-activate-v3.png",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as image:
        signature = image.read(24)
    require(signature[:8] == b"\x89PNG\r\n\x1a\n", f"{path} is not a PNG")
    return struct.unpack(">II", signature[16:24])


def main() -> None:
    source = GAME.read_text(encoding="utf-8")

    for panel in PANELS:
        path = ASSET_ROOT / panel
        require(path.exists(), f"Missing approved Prism panel: {panel}")
        require(
            png_size(path) == (1672, 941),
            f"Unexpected approved Prism panel size: {panel}",
        )
        require(
            f'/Images/Game/Super-Frgmnts/{panel}' in source,
            f"Approved Prism panel is not wired into the runtime: {panel}",
        )

    required_runtime_tokens = (
        'makeBetaPickup("prism", 1338, 1450)',
        'enemy.encounterId === "intake-sweep"',
        "intakeDefenders.every(function (enemy)",
        "return !enemy.alive;",
        "!episodeProgress.prismInstalled",
        'state = "prism-install";',
        "episodeProgress.prismInstalled = true;",
        'setEpisodePhase("prism-acquired");',
        'syncEpisodeBeamProgression("prismSplinter");',
        'canvas.dataset.prismInstallPanel = "reach";',
        "PRISM_INSTALL_PANEL_NAMES",
    )
    for token in required_runtime_tokens:
        require(token in source, f"Missing Prism cinematic contract: {token}")

    old_runtime_panels = (
        "aryn-prism-comic-panel-01-reach-v1.png",
        "aryn-prism-comic-panel-02-install-v1.png",
        "aryn-prism-comic-panel-03-activate-v1.png",
    )
    for panel in old_runtime_panels:
        require(
            f'/Images/Game/Super-Frgmnts/{panel}' not in source,
            f"Obsolete Prism panel is still wired into the runtime: {panel}",
        )

    print("SUPER FRGMNTS first-run Prism cinematic: PASS")
    print("- all three approved Diet Coke panels are wired at 1672 x 941")
    print("- the pickup remains beyond the first underground intake fight")
    print("- the cinematic freezes gameplay and commits Prism progression once")
    print("- later visits cannot replay the acquisition sequence")


if __name__ == "__main__":
    main()
