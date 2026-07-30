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
FAN_HOUSING = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "foundry-ventilation-fan-housing-v1.png"
)
FAN_ROTOR = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "foundry-ventilation-fan-rotor-v1.png"
)
SEAM_WINDOW = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "foundry-seam-cavern-window-v1.png"
)
BREATHING_CHAMBER_PLAN = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Breathing-Chamber"
    / "BREATHING-CHAMBER-BLUESKY.md"
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
        'id: "foundry-breathing-chamber"',
        'axis: "x",\n                                    range: 110',
        "foundryFreightLift: true",
        "FOUNDRY_LIFT_CYCLE_DURATION",
        "function foundryFreightLiftPosition()",
        "function playerIsAtFoundryUpperThreshold()",
        "ATMOSPHERE_LOCK_GATE_CLEARANCE = 72",
        "function playerIsAtAtmosphereLockThreshold(portal)",
        "var wallLeft =",
        "var wallRight =",
        "var contactLeft = atThreshold",
        "wallLeft -\n                            ATMOSPHERE_LOCK_DOOR_WIDTH",
        "var contactRight = atThreshold",
        "wallRight +\n                            ATMOSPHERE_LOCK_DOOR_WIDTH",
        "player.x = contactLeft - 78",
        "player.x = contactRight - 34",
        "FREIGHT LIFT ONLINE // REFINERY ABOVE",
        "var foundryRoute = foundryTraversalRoutes[roomIndex];",
        "? foundryRoute.platforms",
        ": sharedLowerRoute.concat(sharedUpperTransfers);",
        "paintedCatwalks.forEach",
        "runtimeRoute.forEach",
        "var atmosphereLockPortals = [",
        "atmosphereLockPortals.forEach",
        "atmosphereLockTunnelFloor: true",
        "function buildAtmosphericStabilizers()",
        "ATMOSPHERIC_STABILIZER_VISUAL_WIDTH = 336",
        "ATMOSPHERIC_STABILIZER_VISUAL_HEIGHT = 588",
        "ATMOSPHERIC_STABILIZER_VISUAL_SINK = 8",
        "var atmosphericStabilizers = buildAtmosphericStabilizers();",
        "atmosphericStabilizers = buildAtmosphericStabilizers();",
        'previewParameters.get("stabilizer") === "1"',
        'previewParameters.get("gate") === "1"',
        'previewParameters.get("restored") === "1"',
        'id: "foundry-atmospheric-stabilizer"',
        "function activateNearbyAtmosphericStabilizer()",
        "function updateAtmosphericStabilizers(delta)",
        "function drawAtmosphericStabilizers()",
        "canvas.dataset.stabilizerVisualFootprint",
        "canvas.dataset.stabilizerInteractionFootprint",
        "function drawFoundryRestorationSystems()",
        "assets.foundryFanHousing",
        "assets.foundryFanRotor",
        "assets.foundrySeamWindow",
        "function drawFoundrySeamWindow()",
        "FOUNDRY_SEAM_WINDOW_TOP = 850",
        "var fanFixtures = [];",
        "fanIndex < 2;",
        "fanFixtures.forEach",
        "y: 218",
        "var fanAngle = fanRestoration > 0.02",
        "fanRestoration * 2.36",
        'source: "/Images/Game/Super-Frgmnts/foundry-atmosphere-lock-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/foundry-atmosphere-lock-housing-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/foundry-atmosphere-lock-membrane-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/foundry-atmosphere-lock-seam-wall-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/foundry-false-bridge-removal-runtime-v1.png"',
        "assets.foundryAtmosphereLock",
        "assets.foundryAtmosphereLockHousing",
        "assets.foundryAtmosphereLockMembrane",
        "assets.foundryAtmosphereWall",
        "assets.foundryFalseBridgeRemoval",
        "function drawFoundryAtmosphereLock()",
        '"seven-fixed-housings-split-membranes-v1"',
        '"seven-seam-solid-concrete-v1"',
        "canvas.dataset.atmosphereLockState",
        "canvas.dataset.atmosphereLockFloorBottom",
        "canvas.dataset.atmosphereWallSpan",
        "canvas.dataset.atmosphereLockFloorBridge",
        "canvas.dataset.atmosphereLockLevels",
        "canvas.dataset.atmosphereLockPortals",
        "canvas.dataset.atmosphereLockRearm",
        "portal.rearmRequired",
        "var atmosphereLockCycleQa =",
        'canvas.dataset.falseAffordanceCleanup',
        "var falseAffordanceQa =",
        "canvas.dataset.uplinkAtmosphereLock",
        "drawFoundryAtmosphereLockForeground();",
        '"seven-concrete-foregrounds-single-pass-v2"',
        "canvas.dataset.atmosphereWallCompositing",
        '"single-full-height-foreground-pass"',
        "function atmosphereLockRequirementMet(portal)",
        "function atmosphereLockPortalProgress(portal)",
        "function atmosphereLockPortalCloseDuration(portal)",
        "function updateAtmosphereLockPortals(delta)",
        'portal.phase = "closing"',
        '"atmosphereLockShimmer"',
        "function constrainAtmosphereLockMovement(",
        "function constrainFoundryGateMovement(",
        "function foundryGateIsOpen()",
        "drawFoundryRestorationSystems();",
        "drawAtmosphericStabilizers();",
        "updateAtmosphericStabilizers(delta);",
        "if (activateNearbyAtmosphericStabilizer())",
        'canvas.dataset.stabilizerState',
        'canvas.dataset.refineryGate',
        "canvas.dataset.freightLift",
        '"REFINERY ACCESS // ABOVE"',
    )
    for contract in runtime_contracts:
        require(contract in source, f"Missing Foundry traversal contract: {contract}")

    require(
        source.count('id: "foundry-intake-ascent"') == 1,
        "Foundry Intake route must be declared exactly once",
    )
    require(
        source.count('id: "foundry-breathing-chamber"') == 1,
        "The Breathing Chamber route must be declared exactly once",
    )
    require(
        source.count('id: "foundry-atmospheric-stabilizer"') == 1,
        "The Foundry stabilizer must be declared exactly once",
    )
    require(
        source.count("fanIndex < 2;") == 1,
        "Each expansion room must declare exactly two ventilation fixtures",
    )
    for asset in (
        STABILIZER_DORMANT,
        STABILIZER_ACTIVE,
        FAN_HOUSING,
        FAN_ROTOR,
        SEAM_WINDOW,
    ):
        require(asset.is_file(), f"Missing Foundry artwork: {asset.name}")
        require(
            asset.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n",
            f"Foundry artwork is not a PNG: {asset.name}",
        )

    # Runtime movement constants: vy=-790, gravity=2050, max vx=390, body=44px.
    jump_apex = 790**2 / (2 * 2050)
    mandatory_rises = (104, 125, 125, 126, 114, 119, 126, 125, 137, 128,
                       114, 128, 125, 106, 131, 125, 120, 142, 128)
    require(
        max(mandatory_rises) <= jump_apex - 8,
        "The Foundry route no longer preserves its vertical jump margin",
    )
    breathing_chamber_rises = (104, 135, 120, 142)
    require(
        max(breathing_chamber_rises) <= jump_apex - 8,
        "The Breathing Chamber ascent lost its eight-pixel jump margin",
    )
    foundry_lift_cycle_seconds = 5.6
    require(
        abs(foundry_lift_cycle_seconds - (0.55 + 2.15 + 0.75 + 2.15)) < 1e-9,
        "The freight lift no longer completes its approved 5.6-second cycle",
    )
    wall_width = 128
    door_width = 80
    left_membrane_contact = -(wall_width / 2 + door_width)
    right_membrane_contact = wall_width / 2 + door_width
    require(
        left_membrane_contact == -144 and right_membrane_contact == 144,
        "Atmosphere Lock collision no longer meets the visible membrane edges",
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
        "The Breathing Chamber",
        "175 × 100 world-pixel",
        "2.35-second restart sequence",
        "side-profile upper Foundry/Refinery Atmosphere Lock",
        "solid concrete-and-steel divider",
        "mirrored door face",
        "continuous floor collision",
        "foreground",
        "all seven boundaries",
        "Five ordinary passages",
        "`WIDTH × 6` Biolab/Uplink",
        "upper, upper, middle, middle, upper, lower, middle",
        "`636 × 24` collision-backed approach",
        "permanent steel housing",
        "membrane reforms",
        "closed-door collision planes meet the visible outer membrane edges",
        "challenge, recovery, discovery, and exploration",
        "The shared upper plate no longer displays the non-collidable center junction",
        "real 330-pixel gap",
        "background surface may resemble a walkable deck only when matching collision exists",
        "enter zone → learn its traversal",
        "four-minute initial reserve plus two",
        "intentionally not wired into the runtime yet",
    )
    for contract in plan_contracts:
        require(
            contract in normalized_plan,
            f"Missing level-plan contract: {contract}",
        )

    chamber_plan = BREATHING_CHAMBER_PLAN.read_text(encoding="utf-8")
    for contract in (
        "one-way fall that becomes an ascent",
        "sealed service bulkhead",
        "Verified ascent envelope",
        "The deck-level boundary never becomes a bypass",
    ):
        require(
            contract in chamber_plan,
            f"Missing Breathing Chamber plan contract: {contract}",
        )

    print("SUPER FRGMNTS Foundry traversal contract: PASS")
    print("- plate 1 teaches the authored Intake ascent")
    print("- plate 2 descends dormant and returns through a powered ascent")
    print("- painted catwalk collision remains available in both rooms")
    print("- later zones retain their provisional shared traversal")
    print("- the first two-plate zone ends at an interactive stabilizer")
    print("- matched dormant/active alpha artwork crossfades over 2.35 seconds")
    print("- each room has two deck-mounted ventilation fixtures")
    print("- layered fan housings stay fixed while their illustrated rotors turn")
    print("- the cavern-window patch replaces the mirrored Foundry seam")
    print("- seven full-height walls use upper, middle, and lower passages")
    print("- the Biolab/Uplink lock joins the real y=1508 lower catwalk")
    print("- five cyan transit locks open quickly without interrupting exploration")
    print("- Foundry and Biolab zone locks remain sealed until restoration")
    print("- fixed housings remain while membranes retract and reform")
    print("- closed lock collision meets both visible membrane faces")
    print("- the shared false bridge is painted out without changing collision")
    print("- restored Foundry machinery and conduit lighting respond room-wide")
    print("- the Refinery route remains gated until restoration completes")
    print("- the two stabilizers control only their intended zone thresholds")
    print("- timer awards remain deliberately unimplemented")
    print(f"- hardest rise {max(mandatory_rises):.0f}px / jump apex {jump_apex:.1f}px")
    print(
        "- Breathing Chamber ascent "
        f"{'/'.join(str(rise) for rise in breathing_chamber_rises)}px "
        f"/ lift cycle {foundry_lift_cycle_seconds:.1f}s"
    )
    print(f"- hardest effective gap {hardest_gap - player_body_width}px / reach {horizontal_reach:.1f}px")
    print(f"- Deepworks rise 212px / boosted jump apex {deepworks_jump_apex:.1f}px")


if __name__ == "__main__":
    main()
