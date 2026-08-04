#!/usr/bin/env python3
"""Deterministic movement and Foley contract for Super Frgmnts."""

from pathlib import Path
import math
import wave


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "super_frgmnts.html"
SOURCE = HTML.read_text(encoding="utf-8")

FIXED_STEP = 1 / 120
GRAVITY = 2250.0
JUMP_VELOCITY = 1050.0
RELEASE_VELOCITY = 400.0
RUN_SPEED = 420.0
PLAYER_HEIGHT = 112.0


def simulate_jump(release_after: float | None = None) -> tuple[float, float]:
    y = 0.0
    velocity = -JUMP_VELOCITY
    elapsed = 0.0
    minimum_y = y
    landed = False
    while elapsed < 2.0 and not landed:
        if (
            release_after is not None
            and elapsed >= release_after
            and velocity < -RELEASE_VELOCITY
        ):
            velocity = -RELEASE_VELOCITY
        next_velocity = min(1050.0, velocity + GRAVITY * FIXED_STEP)
        y += (velocity + next_velocity) * 0.5 * FIXED_STEP
        velocity = next_velocity
        elapsed += FIXED_STEP
        minimum_y = min(minimum_y, y)
        landed = elapsed > FIXED_STEP and y >= 0 and velocity > 0
    return -minimum_y, elapsed


held_apex, held_flight = simulate_jump()
short_apex, _ = simulate_jump(0.08)

assert math.isclose(held_apex, 245.0, abs_tol=0.15), held_apex
assert math.isclose(held_apex / PLAYER_HEIGHT, 2.1875, abs_tol=0.005)
assert short_apex < held_apex * 0.55, (short_apex, held_apex)
assert math.isclose(held_flight, 0.9333333333, abs_tol=FIXED_STEP * 1.1)
assert math.isclose(RUN_SPEED * held_flight, 392.0, abs_tol=4.0)

contracts = {
    "120 Hz fixed step": "var MOVEMENT_FIXED_STEP = 1 / 120;",
    "twelve-substep cap": "var MOVEMENT_MAX_SUBSTEPS = 12;",
    "native gravity": "var MOVEMENT_GRAVITY = 2250;",
    "native run speed": "var MOVEMENT_RUN_SPEED = 420;",
    "native launch velocity": "var MOVEMENT_JUMP_VELOCITY = 1050;",
    "released-jump clamp": "var MOVEMENT_JUMP_RELEASE_VELOCITY = 400;",
    "jump buffer": "var MOVEMENT_JUMP_BUFFER = 0.14;",
    "coyote time": "var MOVEMENT_COYOTE_TIME = 0.105;",
    "accepted jump cue": 'beginAcceptedMovementJump("jump")',
    "accepted jet-assist cue": 'beginAcceptedMovementJump("jet-assist")',
    "landing transition cue": 'recordMovementAudio(\n                                "landing"',
    "actual-travel footstep gate": "horizontalTravel > 0.1",
    "run-frame one trigger": "runFrame === 1",
    "run-frame five trigger": "runFrame === 5",
    "grounded text parity": "grounded: player.onGround",
    "vertical velocity text parity": "verticalVelocity: Number(player.vy.toFixed(2))",
    "jump-state text parity": "jumpState: currentMovementJumpState()",
    "QA apex text parity": "qaApex: Number(qaApex.toFixed(2))",
}

for label, token in contracts.items():
    assert token in SOURCE, f"missing movement contract: {label}"

runtime_audio = {
    "jump": ("super-frgmnts-aryn-jump-v2.wav", 0.3221768707),
    "landing": ("super-frgmnts-aryn-land-v2.wav", 0.1073922902),
    "footstep": ("super-frgmnts-aryn-footstep-v1.wav", 0.0580498866),
}

for cue, (filename, expected_duration) in runtime_audio.items():
    path = ROOT / "Audio" / filename
    with wave.open(str(path), "rb") as wav:
        assert wav.getnchannels() == 2, f"{cue} must be stereo"
        assert wav.getsampwidth() == 2, f"{cue} must be 16-bit PCM"
        assert wav.getframerate() == 44100, f"{cue} must be 44.1 kHz"
        duration = wav.getnframes() / wav.getframerate()
        assert math.isclose(duration, expected_duration, abs_tol=1 / 44100)

print("SUPER FRGMNTS movement and Foley contract: PASS")
print(f"- held apex {held_apex:.2f}px / {held_apex / PLAYER_HEIGHT:.4f} Aryn heights")
print(f"- short-hop apex {short_apex:.2f}px")
print(f"- held same-height envelope {RUN_SPEED * held_flight:.1f}px")
print("- coyote, buffer, release clamp, and no-raw-input audio seams are present")
print("- footsteps require grounded visible running with actual horizontal travel")
print("- jump, landing, and footstep runtime WAV contracts match")
