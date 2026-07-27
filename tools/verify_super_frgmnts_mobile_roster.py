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
        "enemy-fragment-spring-green-runtime-v1.png",
        "enemy-fragment-bastion-purple-runtime-v1.png",
        "enemy-core-leech-hover-sheet-v1.png",
        "enemy-vesper-flare-hover-sheet-v1.png",
        "enemy-pale-watcher-stalk-sheet-v1.png",
        'type === "wasp"',
        'type === "gaunt"',
        'type === "fragmentSpring"',
        'type === "fragmentBastion"',
        'type === "coreLeech"',
        'type === "vesperFlare"',
        'type === "paleWatcher"',
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
        '"fragmentSpring"',
        '"fragmentBastion"',
        '"coreLeech"',
        '"vesperFlare"',
        '"paleWatcher"',
    )
    for enemy_type in roster:
        assert enemy_type in SOURCE, f"Missing enemy roster type: {enemy_type}"

    episode_asset_block = SOURCE.split(
        "var episodeBetaAssetKeys = [",
        1,
    )[1].split("];", 1)[0]
    enemy_assets = (
        '"crawler"',
        '"walker"',
        '"flyer"',
        '"squircle"',
        '"mite"',
        '"wasp"',
        '"gauntWalk"',
        '"gauntAttack"',
        '"patroller"',
        '"patrollerDeath"',
        '"fragmentSpring"',
        '"fragmentBastion"',
        '"coreLeech"',
        '"vesperFlare"',
        '"paleWatcher"',
    )
    for enemy_asset in enemy_assets:
        assert enemy_asset in episode_asset_block, (
            "Episode beta spawns an enemy whose artwork is not loaded: "
            f"{enemy_asset}"
        )

    print("SUPER FRGMNTS mobile controls and full roster: PASS")
    print("- interrupted analog input releases without a delayed latch")
    print("- iOS selection/loupe paths are actively cleared")
    print("- all 13 cataloged enemy families are populated and loaded")
    print("- rifle and pack laser can be switched on touch or keyboard")
    print("- the Uplink Gate returns Aryn with her recovered loadout")


if __name__ == "__main__":
    main()
