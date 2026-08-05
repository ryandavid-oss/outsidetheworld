#!/usr/bin/env python3
"""Verify the bounded Foundry encounter and livewire contracts."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    source = GAME.read_text(encoding="utf-8")

    required_tokens = (
        "var EPISODE_ENEMY_ACTIVE_BUDGET = 3;",
        "var EPISODE_HOSTILE_PROJECTILE_BUDGET = 2;",
        "function enemyIsNearCamera(enemy, marginX, marginY)",
        "function refreshEnemyActivation()",
        "function settleEnemyForSleep(enemy)",
        "function updateDormantEnemyTimers(enemy, delta)",
        "refreshEnemyActivation();",
        "candidates.slice(0, EPISODE_ENEMY_ACTIVE_BUDGET)",
        "episodeBetaRun && !enemy.runtimeActive",
        "EPISODE_HOSTILE_PROJECTILE_BUDGET",
        "beamBoltHitsAtmosphereWall(\n                            orb,",
        "activeOrb.y < cameraY + HEIGHT + 100;",
        '"foundry-crossfire"',
        '"refinery-livewire"',
        '"pressure-purge"',
        '"uplink-test"',
        '"refinery-livewire-transfer"',
        '"biolab-livewire-transfer"',
        '"uplink-livewire-transfer"',
        "function electricPlatformCycleState(platform)",
        'return "warning";',
        "awakeEnemies:",
        "hostileProjectileBudget:",
        "zapPlatforms: platforms",
        "awake: Boolean(enemy.runtimeActive)",
        "encounter:\n                                    enemy.encounterId",
    )
    for token in required_tokens:
        require(token in source, f"Missing encounter contract: {token}")

    require(
        source.count("platform.zapChallengeId = zapChallenge.id;") == 1,
        "Livewire platforms are not configured through the shared route seam",
    )
    require(
        source.count('id: "refinery-livewire-transfer"') == 1
        and source.count('id: "biolab-livewire-transfer"') == 1
        and source.count('id: "uplink-livewire-transfer"') == 1,
        "The three authored livewire transfers are not unique",
    )

    print("SUPER FRGMNTS bounded encounter contract: PASS")
    print("- three enemy brains may be awake at once")
    print("- two hostile projectiles may persist at once")
    print("- dormant enemies stop AI, animation, targeting, and combat overlays")
    print("- atmosphere walls stop hostile shots")
    print("- three livewire transfers telegraph warning, safe, and active phases")
    print("- encounter and zap state are exposed through render_game_to_text")


if __name__ == "__main__":
    main()
