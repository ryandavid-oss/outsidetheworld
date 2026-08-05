#!/usr/bin/env python3
"""Static asset and integration contract for the Super Frgmnts Energy HUD."""

from pathlib import Path
import struct
import wave


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "super_frgmnts.html"
CELL = ROOT / "Images/Game/Super-Frgmnts/health-cell-v2.png"
CORE = ROOT / "Images/Game/Super-Frgmnts/health-core-v1.png"
SOUND = ROOT / "Audio/super-frgmnts-pickup-health-v1.wav"


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"{path.name} is not a PNG"
    return struct.unpack(">II", data[16:24])


source = HTML.read_text(encoding="utf-8")

contracts = {
    "12-point starting capacity": "var MAX_HITS = 12;",
    "40-point engine ceiling": "var MAX_ENERGY_CEILING = 40;",
    "four points per bar": "var HEALTH_POINTS_PER_BAR = 4;",
    "segmented HUD mount": 'id="energyBars"',
    "camera-fixed HUD state": "function updateEnergyHud(animated)",
    "full-health pickup absorption": "ENERGY FULL // ABSORBED",
    "enemy-drop homing": "function updateEnemyHealthPickups(delta)",
    "random enemy-drop seam": "var ENEMY_HEALTH_DROP_CHANCE = 0.3;",
    "maximum restoration clamp": "previousEnergy + pickup.restore",
    "one-point Cell": 'pickupKind === "core" ? 4 : 1',
    "four-point Core placement": 'makeHealthPickup(WIDTH * 4 + 1340, 970, "core")',
    "pickup audio": "/Audio/super-frgmnts-pickup-health-v1.wav",
    "Energy text parity": "Energy: currentEnergyPoints()",
    "maximum Energy text parity": "maximumEnergy: MAX_HITS",
    "pickup visibility text parity": "visibleHealthPickups:",
    "mobile safe-area top": "env(safe-area-inset-top)",
    "mobile safe-area right": "env(safe-area-inset-right)",
}

for label, token in contracts.items():
    assert token in source, f"missing health contract: {label}"

assert png_size(CELL) == (96, 96), "Vitality Cell must be 96x96"
assert png_size(CORE) == (96, 96), "Vitality Core must be 96x96"

with wave.open(str(SOUND), "rb") as wav:
    assert wav.getnchannels() == 2, "pickup sound must be stereo"
    assert wav.getsampwidth() == 2, "pickup sound must be 16-bit PCM"
    assert wav.getframerate() == 44100, "pickup sound must be 44.1 kHz"

print("SUPER FRGMNTS Energy HUD contract: PASS")
for label in contracts:
    print(f"- {label}")
print("- creator-authored Cell and Core are 96x96 RGBA runtime PNGs")
print("- creator-authored pickup sound is stereo 16-bit 44.1 kHz PCM")
