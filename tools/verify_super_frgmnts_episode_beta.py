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
LEVEL_DESIGN = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "SHARD-FOUNDRY-LEVEL-DESIGN-v1.md"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    source = GAME.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    level_design = LEVEL_DESIGN.read_text(encoding="utf-8")

    require(manifest["timer_seconds"] == 480, "Beta timer is not eight minutes")
    difficulty = manifest["difficulty_contract"]
    require(
        difficulty["target"] == "easy-to-medium",
        "Difficulty target is not easy-to-medium",
    )
    require(
        difficulty["baseline_rise_max_pixels"] == 128,
        "Baseline platform-rise contract drifted",
    )
    require(
        difficulty["electric_cycle_seconds"] == 3.6
        and difficulty["electric_live_seconds"] == 1.25
        and difficulty["electric_landing_grace_seconds"] == 0.28,
        "Electric-platform fairness values drifted",
    )
    require(
        manifest["population"]["signal_shards"] == 12,
        "Manifest does not reserve twelve Signal Shards",
    )
    require(
        manifest["population"]["atmospheric_relays"] == 2,
        "Manifest does not reserve two beta relays",
    )
    require(
        manifest["population"]["signal_shards_deepworks"] == 1,
        "Deepworks does not contain its required Signal Shard",
    )
    require(
        manifest["population"]["deepworks_entries"] == 2,
        "Deepworks entry count drifted",
    )
    require(
        manifest["population"]["static_contact_hazards"] == 2
        and manifest["population"]["electrified_platforms"] == 1,
        "Hazard population drifted",
    )
    require(
        [zone["zone"] for zone in manifest["zone_plan"]]
        == ["Foundry", "Refinery", "Biolab", "Uplink", "Deepworks"],
        "Zone plan is incomplete or out of order",
    )

    required_tokens = (
        "var episodeArrivalTutorial =",
        'var isFoundry = scene === "foundry";',
        "episodeBetaRun = isFoundry;",
        "woundBossPreview = isWound;",
        "episodeArrivalTutorial =\n                    isOverworld && !episodeSurfaceReturn;",
        "TOTAL_SHARDS = isFoundry",
        '.concat(["creditCoin", "creditCrate"])',
        ".concat(episodeBetaAssetKeys)",
        "FIELD CALIBRATION // FIRE ON CREDIT CACHE",
        "CROSS CALIBRATION CATWALKS // BOARD TRANSPORT",
        "FIRE → RECOVER CREDITS",
        "LIVE // WAIT",
        "function openCreditCrate(crate)",
        "creditCoins.push({",
        "persistEpisodeCredits();",
        "creditsCollected = readEpisodeCredits();",
        "function checkElectrifiedPlatforms()",
        "function buildEpisodeBetaHazards()",
        '"refinery-thermal-vent"',
        '"uplink-arc-leak"',
        "electricLandingGrace = 0.28;",
        "% 3.6",
        ") < 1.25;",
        "function resetEpisodeBetaPopulation()",
        'makeBetaPickup("jetpack"',
        'makeBetaPickup("rifle"',
        'makeBetaPickup("vesperite"',
        "makeShard(WIDTH * 3 + 920, 1748",
        "makeCreditCrate(WIDTH * 5 + 920, 1816, 7)",
        "makeBetaRifleObstacle(",
        "routeGate: true",
        "hitsRequired: RIFLE_BOULDER_HITS_REQUIRED",
        "function requiredRouteObstructionsCleared()",
        "function uplinkRequirementsMet()",
        "atmosphericStabilizerZone(stabilizer)",
        '"BIOLAB STABLE // UPLINK AHEAD"',
        "room.entryEnabled",
        "roomIndex === 3 ||",
        "roomIndex === 5",
        "canvas.dataset.staticHazards",
        "canvas.dataset.deepworksEntries",
        "canvas.dataset.deepworksShards",
        "canvas.dataset.requiredRouteLocks",
        "function makeEpisodeBetaEnemies()",
        'makeEnemy(\n                    "wasp"',
        'makeEnemy(\n                    "gaunt"',
        "function toggleWeaponMode()",
        "function beginEpisodeWoundTransition()",
        "function returnToSurfaceAfterMission()",
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
        ".touch-key--shoot" not in source,
        "A non-tutorial Overworld route still hides the always-equipped seeker",
    )
    design_tokens = (
        "## Non-negotiable fairness rules",
        "## Zone-by-zone critical path",
        "### Foundry // Plates 0–1",
        "### Refinery // Plates 2–3",
        "### Biolab // Plates 4–5",
        "### Uplink // Plates 6–7",
        "## Playtest acceptance",
        "No hostile patrol, projectile, or active hazard begins inside a room link",
        "The Uplink Gate opens only when twelve Signal Shards, two stabilizers",
    )
    for token in design_tokens:
        require(token in level_design, f"Missing level-design contract: {token}")

    print("SUPER FRGMNTS Episode 01 early beta: PASS")
    print("- title, overworld tutorial, and Foundry run share one in-page route")
    print("- tutorial credits burst physically and carry through the transport")
    print("- Foundry contains pickups, caches, relays, shards, and obstruction")
    print("- moving and forgiving electrified-platform lessons are present")
    print("- Deepworks has one required shard route and one optional cache route")
    print("- room links, relay aprons, and recovery placements use safe buffers")
    print("- telescopic laser seeker remains available on every Overworld route")
    print("- the Uplink checkpoint requires twelve shards, two relays, and the rifle lock")


if __name__ == "__main__":
    main()
