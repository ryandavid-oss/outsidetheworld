#!/usr/bin/env python3
"""Verify Aryn Sol-Mavi's persistent backpack and defense contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = (ROOT / "super_frgmnts.html").read_text(encoding="utf-8")
PACK_CONTRACT = (
    ROOT
    / "Design/Super-Frgmnts/Overworld/Phase-3/Aryn/Pack"
    / "PACK-CHASSIS-CONTRACT-v1.md"
).read_text(encoding="utf-8")
HANDOFF = (
    ROOT / "Design/Super-Frgmnts/SUPER-FRGMNTS-HANDOFF.md"
).read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    normalized_pack_contract = " ".join(PACK_CONTRACT.split())
    normalized_handoff = " ".join(HANDOFF.split())
    runtime_contracts = (
        "var blasterTier = 1;",
        'canvas.dataset.arynSeeker = "always-equipped";',
        "function getFriendlySafetyZones()",
        'id: "dras",',
        'id: "jane",',
        "function steerBoltAwayFromFriendlies(bolt, stats, delta)",
        "steerBoltAwayFromFriendlies(bolt, stats, delta);",
        "bolt.friendlyAvoidance = safetyZone.id;",
        "canvas.dataset.lastSeekerAvoidance = safetyZone.id;",
        "player.vy = -790;",
        "jetpackOwned &&",
        "jetpackBoostAvailable",
        "function damageEnemy(\n                enemy,\n                enemyTop,\n                bolt,\n                woundHitZone",
        '"telescopic-laser-seeker"',
    )
    for token in runtime_contracts:
        require(token in GAME, f"Missing Aryn character contract: {token}")

    require(
        GAME.count("blasterTier = 1;") == 2,
        "Aryn's reset loadout does not guarantee the tier-one seeker",
    )
    require(
        "body.is-overworld-preview:not(.is-arrival-tutorial) .touch-key--shoot"
        not in GAME,
        "The fire control is still hidden in an Overworld route",
    )
    require(
        "inDeepworks ? -1040 : -790" not in GAME,
        "Deepworks still grants an unexplained unassisted jump boost",
    )
    require(
        'text: "JET ASSIST REQUIRED"' in GAME
        and "if (!jetpackOwned)" in GAME,
        "Deepworks can strand Aryn before jet assist is online",
    )
    require(
        "RIFLE_ENEMY_DAMAGE" not in GAME
        and "RIFLE_BOSS_DAMAGE" not in GAME
        and "enemy.boss" not in GAME,
        "Undecided rifle or boss balance was encoded in the runtime",
    )
    require(
        "var canStomp" not in GAME and "var stomped" not in GAME,
        "Aryn still has a stomp attack outside the seeker defense contract",
    )

    documentation_contracts = (
        "persistent equipment and power-up chassis",
        "telescopic laser seeker",
        "only always-carried self-defense weapon",
        "always equipped",
        "Friendly avoidance wins",
        "one consistent unassisted jump",
        "clearing Vesperite route obstructions, killing bosses, and handling heavy combat",
        "ammo model, damage, boss effectiveness, and interaction with armor remain undecided",
        "whether the telescopic laser seeker overheats",
        "no stomp or contact-damage attack",
    )
    for phrase in documentation_contracts:
        require(
            phrase in normalized_pack_contract,
            f"Missing pack documentation contract: {phrase}",
        )

    require(
        "only always-carried self-defense weapon and is available"
        in normalized_handoff,
        "The handoff does not preserve the always-available seeker rule",
    )
    require(
        "Higher traversal requires the backpack's jet-assist module."
        in normalized_handoff,
        "The handoff does not preserve the jet-assisted height rule",
    )

    print("SUPER FRGMNTS Aryn character refinement: PASS")
    print("- backpack is the persistent power-up chassis")
    print("- telescopic laser seeker is always equipped, including Overworld")
    print("- seeker bends toward enemies and away from Dras and Jane")
    print("- heavy rifle roles are set while combat balance remains open")
    print("- higher jumps require the backpack jet-assist module")


if __name__ == "__main__":
    main()
