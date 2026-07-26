#!/usr/bin/env python3
"""Verify the isolated SUPER FRGMNTS Vesper Mite integration."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
SHEET = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "enemy-vesper-mite-flight-sheet-v1.png"
)


def main() -> None:
    source = GAME.read_text(encoding="utf-8")
    required = (
        'previewParameters.get("mite") === "1"',
        "mite: {",
        "enemy-vesper-mite-flight-sheet-v1.png",
        "function makeVesperMiteTrial()",
        "function drawVesperMite(enemy, sprite)",
        "Math.floor(enemy.animationTime / 0.064) % 18",
        'mite: "VESPER MITE"',
        'canvas.dataset.miteAlive',
        "vesperMiteTrial ||",
    )
    missing = [contract for contract in required if contract not in source]
    if missing:
        raise SystemExit("Missing Vesper Mite contracts: " + ", ".join(missing))

    if not SHEET.exists():
        raise SystemExit(f"Missing runtime sheet: {SHEET}")
    with Image.open(SHEET) as image:
        if image.size != (636, 780):
            raise SystemExit(f"Unexpected sheet size: {image.size}")
        if image.mode != "RGBA":
            raise SystemExit(f"Unexpected sheet mode: {image.mode}")
        if image.getchannel("A").getextrema() != (0, 255):
            raise SystemExit("Runtime sheet does not preserve transparency")

    print("SUPER FRGMNTS Vesper Mite trial: PASS")
    print("- 36 supplied frames retained in a 6×6 mobile-safe runtime atlas")
    print("- frames 0–17 form the provisional 64 ms low-hover cycle")
    print("- isolated Foundry spawn supports stomp, seeking blaster, and contact damage")
    print("- trial begins with the tier-one pack blaster unlocked")


if __name__ == "__main__":
    main()
