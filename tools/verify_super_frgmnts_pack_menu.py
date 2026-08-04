#!/usr/bin/env python3
"""Static integration contract for the Super Frgmnts PACK configuration menu."""

from hashlib import sha256
from pathlib import Path
import wave


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "super_frgmnts.html"
SWITCH_SOUND = ROOT / "Audio/super-frgmnts-ui-switch-v1.wav"
CLICK_SOUND = ROOT / "Audio/super-frgmnts-menu-ui-click-v1.wav"


source = HTML.read_text(encoding="utf-8")

contracts = {
    "dedicated pause dialog": 'id="pausePackLayer"',
    "pause Resume action": 'id="pauseResumeButton"',
    "pause PACK action": 'id="pausePackButton"',
    "pause restart action": 'id="pauseRestartButton"',
    "PACK back action": 'id="packBackButton"',
    "PACK resume action": 'id="packResumeButton"',
    "Focus module control": 'data-pack-module="focusPulse"',
    "Rime module control": 'data-pack-module="rimeLock"',
    "Ghost module control": 'data-pack-module="ghostVector"',
    "Prism module control": 'data-pack-module="prismSplinter"',
    "Solar module control": 'data-pack-module="solarNeedle"',
    "base backpack label": '"BACKPACK BASE"',
    "canonical module mutation": "beamLoadout.enabled.add(moduleName)",
    "canonical module removal": "beamLoadout.enabled.delete(moduleName)",
    "module persistence": "PACK_MODULES_STORAGE_KEY",
    "Focus charge reset": "beamChargeTime = 0;",
    "pending fire reset": "shootBuffer = 0;",
    "pause simulation freeze": 'if (state === "paused") return;',
    "keyboard PACK shortcut": 'event.code === "KeyE"',
    "controller PACK shortcut": "var packPressed = gamepadButtonJustPressed(buttons, 3);",
    "touch-accessible module buttons": 'class="pack-module-card" type="button"',
    "menu screen text parity": "menuScreen:",
    "menu focus text parity": "menuFocus: focusedMenuControl",
    "discovered module text parity": "discoveredModules: discoveredBeamModules",
    "enabled module text parity": "enabledModules: enabledBeamModules",
    "switch sound wiring": "/Audio/super-frgmnts-ui-switch-v1.wav",
    "menu click sound wiring": "/Audio/super-frgmnts-menu-ui-click-v1.wav",
    "mobile safe-area top": "env(safe-area-inset-top)",
    "mobile safe-area right": "env(safe-area-inset-right)",
}

for label, token in contracts.items():
    assert token in source, f"missing PACK menu contract: {label}"

module_controls = source.count('data-pack-module="')
assert module_controls == 5, f"expected exactly five PACK module buttons, found {module_controls}"

expected_hashes = {
    SWITCH_SOUND: "3c9b49f7e41acf4301117a9c043295f2efd116dcb372cf40a3485ee248aa7f42",
    CLICK_SOUND: "30df80e9f2603067bae49f9326b767f9898397414b972d6f0e89ed0b1fe51382",
}

for sound, expected_hash in expected_hashes.items():
    assert sound.exists(), f"missing transferred sound: {sound.name}"
    assert sha256(sound.read_bytes()).hexdigest() == expected_hash, f"hash mismatch: {sound.name}"
    with wave.open(str(sound), "rb") as wav:
        assert wav.getnchannels() == 2, f"{sound.name} must be stereo"
        assert wav.getsampwidth() == 2, f"{sound.name} must be 16-bit PCM"
        assert wav.getframerate() == 44100, f"{sound.name} must be 44.1 kHz"

print("SUPER FRGMNTS PACK configuration contract: PASS")
for label in contracts:
    print(f"- {label}")
print("- exactly five independent module toggles")
print("- creator-authored UI sounds match the transfer package")
