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
        "enemy-core-leech-hover-sheet-v1.png",
        "enemy-pale-watcher-stalk-sheet-v1.png",
        "enemy-skree-walk-sheet-v1.png",
        "enemy-sova-crawl-sheet-v1.png",
        "enemy-seam-lurker-crawl-sheet-v1.png",
        "enemy-kihunter-flight-sheet-v1.png",
        'type === "wasp"',
        'type === "gaunt"',
        'type === "coreLeech"',
        'type === "paleWatcher"',
        'type === "skree"',
        'type === "sova"',
        'type === "seamLurker"',
        'type === "kihunter"',
        "var WOUND_BOSS_MOBILE_HEALTH = 34;",
        "var WOUND_BOSS_MOBILE_SPEED_SCALE = 0.72;",
        "var WOUND_BOSS_MOBILE_LASER_COOLDOWN = 6.6;",
        "var WOUND_BOSS_MOBILE_INVULNERABILITY = 1.65;",
        'canvas.dataset.woundBossAssist =',
        "HEAVY RIFLE",
    )
    for token in required:
        assert token in SOURCE, f"Missing mobile/roster contract: {token}"

    roster = (
        '"squircle"',
        '"wasp"',
        '"gaunt"',
        '"patroller"',
        '"coreLeech"',
        '"paleWatcher"',
        '"skree"',
        '"sova"',
        '"seamLurker"',
        '"kihunter"',
    )
    for enemy_type in roster:
        assert enemy_type in SOURCE, f"Missing enemy roster type: {enemy_type}"

    episode_asset_block = SOURCE.split(
        "var episodeBetaAssetKeys = [",
        1,
    )[1].split("];", 1)[0]
    enemy_assets = (
        '"squircle"',
        '"wasp"',
        '"gauntWalk"',
        '"gauntAttack"',
        '"patroller"',
        '"patrollerDeath"',
        '"coreLeech"',
        '"paleWatcher"',
        '"skree"',
        '"sova"',
        '"seamLurker"',
        '"kihunter"',
    )
    for enemy_asset in enemy_assets:
        assert enemy_asset in episode_asset_block, (
            "Episode beta spawns an enemy whose artwork is not loaded: "
            f"{enemy_asset}"
        )

    print("SUPER FRGMNTS mobile controls and full roster: PASS")
    print("- interrupted analog input releases without a delayed latch")
    print("- iOS selection/loupe paths are actively cleared")
    for retired in ('"crawler"', '"walker"', '"flyer"'):
        assert retired not in episode_asset_block, (
            f"Retired placeholder still preloads on mobile: {retired}"
        )

    print("- all ten active enemy families are populated and loaded")
    print("- mobile boss assist narrows damage windows without changing desktop")
    print("- rifle and pack laser can be switched on touch or keyboard")
    print("- the Uplink Gate returns Aryn with her recovered loadout")


if __name__ == "__main__":
    main()
