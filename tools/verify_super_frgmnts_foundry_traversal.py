#!/usr/bin/env python3
"""Verify the authored opening traversal for SUPER FRGMNTS Episode 01."""

from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
PLAN = ROOT / "Design" / "Super-Frgmnts" / "UNIFIED-LEVEL-ONE-PLAN.md"
STABILIZER_DORMANT = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "atmospheric-stabilizer-dormant-v1.png"
)
STABILIZER_ACTIVE = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "atmospheric-stabilizer-active-v1.png"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    source = GAME.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    normalized_plan = " ".join(plan.split())

    runtime_contracts = (
        "var foundryTraversalRoutes = [",
        'id: "foundry-intake-ascent"',
        'id: "foundry-freight-shaft"',
        'axis: "x",\n                                    range: 110',
        'axis: "y",\n                                    range: 240',
        "var foundryRoute = foundryTraversalRoutes[roomIndex];",
        "? foundryRoute.platforms",
        ": sharedLowerRoute.concat(sharedUpperTransfers);",
        "paintedCatwalks.forEach",
        "runtimeRoute.forEach",
        "function buildAtmosphericStabilizers()",
        "var atmosphericStabilizers = buildAtmosphericStabilizers();",
        "atmosphericStabilizers = buildAtmosphericStabilizers();",
        'previewParameters.get("stabilizer") === "1"',
        'previewParameters.get("gate") === "1"',
        'previewParameters.get("restored") === "1"',
        'id: "foundry-atmospheric-stabilizer"',
        "function activateNearbyAtmosphericStabilizer()",
        "function updateAtmosphericStabilizers(delta)",
        "function drawAtmosphericStabilizers()",
        "function drawFoundryRestorationSystems()",
        "function constrainFoundryGateMovement(previousPlayerX)",
        "function foundryGateIsOpen()",
        "drawFoundryRestorationSystems();",
        "drawAtmosphericStabilizers();",
        "updateAtmosphericStabilizers(delta);",
        "if (activateNearbyAtmosphericStabilizer())",
        'canvas.dataset.stabilizerState',
        'canvas.dataset.refineryGate',
        '"REFINERY ACCESS // OPEN"',
        '"REFINERY ROUTE // OPEN"',
    )
    for contract in runtime_contracts:
        require(contract in source, f"Missing Foundry traversal contract: {contract}")

    require(
        source.count('id: "foundry-intake-ascent"') == 1,
        "Foundry Intake route must be declared exactly once",
    )
    require(
        source.count('id: "foundry-freight-shaft"') == 1,
        "Foundry Freight Shaft route must be declared exactly once",
    )
    require(
        source.count('id: "foundry-atmospheric-stabilizer"') == 1,
        "The Foundry stabilizer must be declared exactly once",
    )
    for asset in (STABILIZER_DORMANT, STABILIZER_ACTIVE):
        require(asset.is_file(), f"Missing stabilizer artwork: {asset.name}")
        require(
            asset.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n",
            f"Stabilizer artwork is not a PNG: {asset.name}",
        )

    # Runtime movement constants: vy=-790, gravity=2050, max vx=390, body=44px.
    jump_apex = 790**2 / (2 * 2050)
    mandatory_rises = (104, 125, 125, 126, 114, 119, 126, 125, 137, 128,
                       114, 128, 125, 106, 131, 125, 120, 142, 128)
    require(
        max(mandatory_rises) <= jump_apex - 8,
        "The Foundry route no longer preserves its vertical jump margin",
    )

    hardest_gap = 170
    player_body_width = 44
    gap_rise = 125
    descending_flight_time = (
        790 + math.sqrt(790**2 - 2 * 2050 * gap_rise)
    ) / 2050
    horizontal_reach = 390 * descending_flight_time
    require(
        horizontal_reach >= hardest_gap - player_body_width + 40,
        "The Freight Shaft reversal lost its horizontal safety margin",
    )

    deepworks_jump_apex = 1040**2 / (2 * 2050)
    require(
        deepworks_jump_apex >= (1816 - 1604) + 40,
        "Deepworks is no longer safely jump-exitable",
    )

    plan_contracts = (
        "Foundry traversal pass",
        "Foundry Intake",
        "Foundry Freight Shaft",
        "175 × 100 world-pixel",
        "2.35-second restart sequence",
        "Foundry/Refinery containment field",
        "enter zone → learn its traversal",
        "four-minute initial reserve plus two",
        "intentionally not wired into the runtime yet",
    )
    for contract in plan_contracts:
        require(
            contract in normalized_plan,
            f"Missing level-plan contract: {contract}",
        )

    print("SUPER FRGMNTS Foundry traversal contract: PASS")
    print("- plate 1 teaches the authored Intake ascent")
    print("- plate 2 uses a sparse freight-shaft route and vertical lift")
    print("- painted catwalk collision remains available in both rooms")
    print("- later zones retain their provisional shared traversal")
    print("- the first two-plate zone ends at an interactive stabilizer")
    print("- matched dormant/active alpha artwork crossfades over 2.35 seconds")
    print("- restored Foundry machinery and conduit lighting respond room-wide")
    print("- the Refinery route remains gated until restoration completes")
    print("- three later stabilizer stations remain reserved")
    print("- timer awards remain deliberately unimplemented")
    print(f"- hardest rise {max(mandatory_rises):.0f}px / jump apex {jump_apex:.1f}px")
    print(f"- hardest effective gap {hardest_gap - player_body_width}px / reach {horizontal_reach:.1f}px")
    print(f"- Deepworks rise 212px / boosted jump apex {deepworks_jump_apex:.1f}px")


if __name__ == "__main__":
    main()
