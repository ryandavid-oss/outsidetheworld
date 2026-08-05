#!/usr/bin/env python3
"""Static release contract for Episode 01 Hard Mode and recovery drops."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "super_frgmnts.html"


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    contracts = {
        "title difficulty selector": 'id="titleDifficultyButton"',
        "session-persistent difficulty": '"super-frgmnts-difficulty-v1"',
        "three-times hostile integrity":
            "var HARD_MODE_ENEMY_HEALTH_MULTIPLIER = 3;",
        "Seam Hunter bonus integrity":
            "var HARD_MODE_WOUND_BOSS_BONUS_HEALTH = 200;",
        "Seam Hunter amplified damage":
            "var HARD_MODE_WOUND_BOSS_DAMAGE = 2;",
        "one-time roster scaling":
            "function applyEnemyDifficultyToRoster(roster)",
        "random recovery drops":
            "var ENEMY_HEALTH_DROP_CHANCE = 0.3;",
        "rare recovery cores":
            "var ENEMY_HEALTH_CORE_CHANCE = 0.12;",
        "drop-count performance budget":
            "var ENEMY_HEALTH_DROP_BUDGET = mobilePerformanceMode",
        "automatic drop attraction":
            "function updateEnemyHealthPickups(delta)",
        "full-Energy absorption":
            '"ENERGY FULL // ABSORBED"',
        "difficulty text-render parity":
            "seamHunterBonusHealth: hardMode",
        "drop text-render parity":
            "enemyHealthDrops: {",
        "controller difficulty shortcut":
            "if (packPressed) {\n                        toggleHardMode();",
        "opening Diet Coke seam":
            "Or a cold Diet Coke, if your emergency stores are feeling generous.",
    }

    for label, token in contracts.items():
        assert token in source, f"missing Hard Mode contract: {label}"

    print("SUPER FRGMNTS Episode 01 Hard Mode: PASS")
    for label in contracts:
        print(f"- {label}")


if __name__ == "__main__":
    main()
