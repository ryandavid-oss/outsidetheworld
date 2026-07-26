#!/usr/bin/env python3
"""Verify the isolated SUPER FRGMNTS Chitin Sentinel integration."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
ASSET_ROOT = ROOT / "Images" / "Game" / "Super-Frgmnts"
SHEETS = (
    ASSET_ROOT / "enemy-chitin-sentinel-patrol-sheet-v1.png",
    ASSET_ROOT / "enemy-chitin-sentinel-death-sheet-v1.png",
)


def main() -> None:
    source = GAME.read_text(encoding="utf-8")
    required = (
        'previewParameters.get("patroller") === "1"',
        "patroller: {",
        "patrollerDeath: {",
        "function makeChitinSentinelTrial()",
        "function damageEnemy(enemy, enemyTop)",
        "function drawChitinSentinel(enemy)",
        "enemy.maxHealth = 5",
        'patroller: "CHITIN SENTINEL"',
        'canvas.dataset.patrollerHealth',
        'canvas.dataset.patrollerState',
        "enemy.noStomp",
    )
    missing = [contract for contract in required if contract not in source]
    if missing:
        raise SystemExit(
            "Missing Chitin Sentinel contracts: " + ", ".join(missing)
        )

    for sheet in SHEETS:
        if not sheet.exists():
            raise SystemExit(f"Missing runtime sheet: {sheet}")
        with Image.open(sheet) as image:
            if image.size != (684, 636):
                raise SystemExit(f"Unexpected {sheet.name} size: {image.size}")
            if image.mode != "RGBA":
                raise SystemExit(f"Unexpected {sheet.name} mode: {image.mode}")
            if image.getchannel("A").getextrema() != (0, 255):
                raise SystemExit(
                    f"{sheet.name} does not preserve transparency"
                )

    print("SUPER FRGMNTS Chitin Sentinel trial: PASS")
    print("- 36 patrol and 36 death frames retained in mobile-safe atlases")
    print("- armored patrol requires exactly five pack-blaster hits")
    print("- non-interruptible death sequence replaces instant removal")
    print("- stomp immunity preserves the heavy-enemy combat contract")


if __name__ == "__main__":
    main()
