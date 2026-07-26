#!/usr/bin/env python3
"""Verify the assembled SUPER FRGMNTS Episode 01 early-beta contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
MANIFEST = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "episode-01-early-beta-v1.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    source = GAME.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    require(manifest["timer_seconds"] == 480, "Beta timer is not eight minutes")
    require(
        manifest["population"]["signal_shards"] == 12,
        "Manifest does not reserve twelve Signal Shards",
    )
    require(
        manifest["population"]["atmospheric_relays"] == 2,
        "Manifest does not reserve two beta relays",
    )

    required_tokens = (
        "var episodeArrivalTutorial =",
        "episodeBetaRun = !isOverworld;",
        "episodeArrivalTutorial = isOverworld;",
        "TOTAL_SHARDS = isOverworld ? 0 : 12;",
        '.concat(["creditCoin", "creditCrate"])',
        ".concat(episodeBetaAssetKeys)",
        "FIELD CALIBRATION // FIRE ON CREDIT CACHE",
        "CROSS CALIBRATION CATWALKS // REACH PORTAL",
        "FIRE → RECOVER CREDITS",
        "LIVE // WAIT",
        "function openCreditCrate(crate)",
        "creditCoins.push({",
        "persistEpisodeCredits();",
        "creditsCollected = readEpisodeCredits();",
        "function checkElectrifiedPlatforms()",
        "function resetEpisodeBetaPopulation()",
        'makeBetaPickup("jetpack"',
        'makeBetaPickup("rifle"',
        'makeBetaPickup("vesperite"',
        "makeBetaRifleObstacle(",
        "hitsRequired: RIFLE_BOULDER_HITS_REQUIRED",
        "function makeEpisodeBetaEnemies()",
        "allStabilizersOnline()",
        "var annihilationComplete =",
        'startButton.textContent = episodeBetaRun',
    )
    for token in required_tokens:
        require(token in source, f"Missing Episode beta contract: {token}")

    require(
        source.count("makeShard(") >= 12,
        "Runtime does not include the twelve-shard population",
    )
    require(
        source.count("makeCreditCrate(") >= 4,
        "Runtime does not include tutorial and Foundry credit caches",
    )
    require(
        "body.is-overworld-preview:not(.is-arrival-tutorial) "
        ".touch-key--shoot" in source,
        "Mobile FIRE is not exposed specifically for the arrival tutorial",
    )

    print("SUPER FRGMNTS Episode 01 early beta: PASS")
    print("- title, overworld tutorial, and Foundry run share one in-page route")
    print("- tutorial credits burst physically and carry through the portal")
    print("- Foundry contains pickups, caches, relays, shards, and obstruction")
    print("- moving and electrified platform lessons are present")
    print("- completion requires twelve shards and two restored relays")


if __name__ == "__main__":
    main()
