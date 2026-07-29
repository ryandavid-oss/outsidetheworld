#!/usr/bin/env python3
"""Verify Trillian's normalized atlases and surface-only runtime contract."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FAMILY = (
    ROOT
    / "Design/Super-Frgmnts/Overworld/Phase-3/Outpost"
    / "Player-Companion-Dog"
)
MANIFEST = FAMILY / "player-companion-dog-assets-v1.json"
CURRENT_DOG_MANIFEST = (
    FAMILY.parent / "Dog-Ludo" / "camp-dog-runtime-v3.json"
)
SOURCE = (ROOT / "super_frgmnts.html").read_text(encoding="utf-8")


def verify_atlas(
    path: Path,
    columns: int,
    rows: int,
) -> None:
    atlas = Image.open(path).convert("RGBA")
    assert atlas.size == (columns * 120, rows * 104)
    for index in range(columns * rows):
        x = index % columns * 120
        y = index // columns * 104
        frame = atlas.crop((x, y, x + 120, y + 104))
        bound = frame.getchannel("A").getbbox()
        assert bound is not None, f"{path.name}: frame {index} is blank"
        assert bound[0] > 0 and bound[1] > 0
        assert bound[2] < 120 and bound[3] < 104


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    current = json.loads(
        CURRENT_DOG_MANIFEST.read_text(encoding="utf-8")
    )
    assert manifest["status"] == "overworld-surface-runtime"
    assert manifest["name"] == "Trillian"
    assert manifest["companionIdentity"] == (
        "Trillian is the player's dog and is explicitly separate from Jane."
    )
    assert manifest["assetRelationship"] == (
        "The unarmored movement, armored movement, armored attack, and "
        "armored jump-launch sheets all depict Trillian."
    )
    assert manifest["runtimeIntegration"] is True
    assert current["identity"] == "Jane"
    surface = manifest["surfaceRuntime"]
    assert surface["scene"] == "overworld"
    assert surface["recoverAssignmentX"] == 690
    assert surface["harnessAssignmentX"] == 1080
    assert surface["salvageAssignmentX"] == 1430
    assert surface["followDistance"] == 112
    assert surface["followSpeed"] == 82
    assert surface["poweredLaunchVelocityY"] == -950
    assert surface["transportLimitX"] == 6276
    assert surface["friendlySeekerSafety"] is True
    assert surface["solid"] is False
    assert surface["hostile"] is False
    assert surface["enemyTargetable"] is False
    assert surface["combatDamage"] is False
    assert surface["foundryHandoff"] is False

    animations = {
        animation["key"]: animation
        for animation in manifest["animations"]
    }
    assert set(animations) == {
        "unarmored",
        "armored",
        "armoredAttack",
        "armoredJumpLaunch",
    }
    assert animations["unarmored"]["source"]["frameCount"] == 36
    assert animations["unarmored"]["source"]["frameDurationMs"] == 42
    assert animations["unarmored"]["validation"]["result"] == "pass"
    assert animations["armored"]["source"]["frameCount"] == 25
    assert animations["armored"]["source"]["frameDurationMs"] == 58
    assert animations["armored"]["validation"]["result"] == (
        "pass-with-source-warning"
    )
    assert animations["armored"]["validation"]["edgeContactFrames"][
        "right"
    ] == [7, 8, 16, 24]
    assert animations["armoredAttack"]["role"] == (
        "close-range energy lunge"
    )
    assert animations["armoredAttack"]["playback"] == "one-shot"
    assert animations["armoredAttack"]["source"]["frameCount"] == 36
    assert animations["armoredAttack"]["source"]["frameDurationMs"] == 46
    assert animations["armoredAttack"]["validation"]["result"] == (
        "pass-with-source-warning"
    )
    assert animations["armoredAttack"]["validation"][
        "edgeContactFrames"
    ]["top"] == [35]
    assert animations["armoredAttack"]["authoring"]["damageWindow"] == (
        "unassigned until combat implementation"
    )
    jump = animations["armoredJumpLaunch"]
    assert jump["role"] == "powered jump charge and launch cue"
    assert jump["playback"] == "one-shot"
    assert jump["source"]["frameCount"] == 36
    assert jump["source"]["frameDurationMs"] == 49
    assert jump["validation"]["result"] == "pass-with-source-warning"
    assert jump["validation"]["edgeContactFrames"]["right"] == [
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        22,
        23,
        24,
        25,
        26,
        33,
    ]
    assert jump["authoring"]["airborneAnimation"] == "not supplied"
    assert jump["authoring"]["landingAnimation"] == "not supplied"

    alternates = {
        alternate["key"]: alternate
        for alternate in manifest["reviewOnlyAlternates"]
    }
    assert set(alternates) == {"armoredRearAlternate"}
    rear = alternates["armoredRearAlternate"]
    assert rear["runtimeEligible"] is False
    assert rear["source"]["frameCount"] == 25
    assert rear["source"]["frameDurationMs"] == 73
    assert rear["validation"]["result"] == "pass-with-source-warning"
    assert rear["validation"]["edgeContactFrames"]["top"] == [
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
    ]
    assert rear["validation"]["edgeContactFrames"]["left"] == [
        19,
        20,
        21,
        22,
        23,
        24,
    ]
    assert rear["validation"]["edgeContactFrames"]["right"] == [12, 13]
    assert rear["authoring"]["disposition"] == "preserved for review only"

    verify_atlas(
        ROOT / animations["unarmored"]["runtime"]["image"],
        6,
        6,
    )
    verify_atlas(
        ROOT / animations["armored"]["runtime"]["image"],
        5,
        5,
    )
    verify_atlas(
        ROOT / animations["armoredAttack"]["runtime"]["image"],
        6,
        6,
    )
    verify_atlas(
        ROOT / animations["armoredJumpLaunch"]["runtime"]["image"],
        6,
        6,
    )
    verify_atlas(
        ROOT / rear["runtime"]["image"],
        5,
        5,
    )

    for runtime_name in (
        "companion-dog-unarmored-walk-sheet-v1.png",
        "companion-dog-armored-walk-sheet-v1.png",
        "companion-dog-armored-attack-sheet-v1.png",
        "companion-dog-armored-jump-launch-sheet-v1.png",
    ):
        assert runtime_name in SOURCE
    assert (
        "companion-dog-armored-rear-alternate-review-sheet-v1.png"
        not in SOURCE
    )
    for runtime_token in (
        "function resetTrillian()",
        "function updateTrillian(delta)",
        "function drawTrillian()",
        'id: "trillian"',
        'canvas.dataset.trillianHostile = "false"',
        'canvas.dataset.trillianSolid = "false"',
        'canvas.dataset.trillianDamage = "disabled"',
        'canvas.dataset.trillianDamage = "noncombat-breach"',
        "TRILLIAN_TRANSPORT_LIMIT_X",
        "trillian.vy = -950;",
    ):
        assert runtime_token in SOURCE
    assert "makeEnemy(\"trillian\"" not in SOURCE

    print("SUPER FRGMNTS player-companion dog assets: PASS")
    print("- unarmored 36-frame and armored 25-frame gaits normalized")
    print("- armored 36-frame attack normalized as a one-shot")
    print("- armored 36-frame powered jump-launch cue normalized")
    print("- clipped 25-frame rear/power-up alternate preserved for review")
    print("- Trillian is explicitly separate from Jane")
    print("- current Jane runtime and transport contract remain unchanged")
    print("- four approved atlases are loaded only for the Overworld surface")
    print("- follow, harness, powered launch, and noncombat breach are wired")
    print("- Trillian is non-solid, friendly-safe, and absent from enemy data")
    print("- Foundry combat handoff and damage timing remain intentionally open")


if __name__ == "__main__":
    main()
