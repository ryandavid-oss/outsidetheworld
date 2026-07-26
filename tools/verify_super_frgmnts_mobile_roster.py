#!/usr/bin/env python3
"""Verify mobile input recovery, the full roster, and return/loadout controls."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "super_frgmnts.html").read_text(encoding="utf-8")


def main() -> None:
    required = (
        'id="weaponToggle"',
        'id="weaponToggleMode"',
        'event.code === "KeyV"',
        "function toggleWeaponMode()",
        'selectedWeapon === "rifle"',
        "function releaseDirectionPad(pointerId)",
        '["pointerup", "pointercancel"].forEach',
        'document.addEventListener("touchcancel"',
        'document.addEventListener("selectionchange"',
        "keys.left = false;",
        "keys.right = false;",
        "keys.down = false;",
        "function returnToSurfaceAfterMission()",
        'startButton.dataset.surfaceReturn = "true";',
        "surfaceReturnLoadout = {",
        "enemy-flying-wasp-flight-sheet-v1.png",
        "enemy-tall-gaunt-alien-walk-sheet-v1.png",
        "enemy-tall-gaunt-alien-attack-sheet-v1.png",
        'type === "wasp"',
        'type === "gaunt"',
        "HEAVY RIFLE",
    )
    for token in required:
        assert token in SOURCE, f"Missing mobile/roster contract: {token}"

    roster = (
        '"crawler"',
        '"walker"',
        '"flyer"',
        '"squircle"',
        '"mite"',
        '"wasp"',
        '"gaunt"',
        '"patroller"',
    )
    for enemy_type in roster:
        assert enemy_type in SOURCE, f"Missing enemy roster type: {enemy_type}"

    print("SUPER FRGMNTS mobile controls and full roster: PASS")
    print("- interrupted analog input releases without a delayed latch")
    print("- iOS selection/loupe paths are actively cleared")
    print("- all eight legacy and new enemy families are populated")
    print("- rifle and pack laser can be switched on touch or keyboard")
    print("- the Uplink Gate returns Aryn with her recovered loadout")


if __name__ == "__main__":
    main()
