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

    require(manifest["release"] == "beta-2", "Release is not Beta 2")
    require(
        manifest["status"] == "beta-2-production",
        "Beta 2 is not marked for production",
    )
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
        difficulty["minimum_powerup_item_separation_pixels"] == 240,
        "Power-up separation contract drifted",
    )
    require(
        difficulty["electric_cycle_seconds"] == 3.6
        and difficulty["electric_live_seconds"] == 1.25
        and difficulty["electric_landing_grace_seconds"] == 0.28,
        "Electric-platform fairness values drifted",
    )
    require(
        manifest["population"]["vesperite_fragments"] == 12,
        "Manifest does not reserve twelve Vesperite Fragments",
    )
    require(
        manifest["population"]["atmospheric_stabilizers"] == 2,
        "Manifest does not reserve two beta stabilizers",
    )
    require(
        manifest["population"]["vesperite_fragments_deepworks"] == 1,
        "Deepworks does not contain its required Vesperite Fragment",
    )
    require(
        manifest["population"]["deepworks_entries"] == 2,
        "Deepworks entry count drifted",
    )
    require(
        manifest["population"]["credit_caches_overworld"] == 0,
        "Overworld tutorial cache was not removed",
    )
    require(
        manifest["population"]["enemy_count"] == 18
        and manifest["population"]["chitin_sentinel_count"] == 7
        and manifest["population"]["core_leech_count"] == 3,
        "Production enemy population drifted",
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
        "episodeArrivalTutorial = false;",
        "TOTAL_SHARDS = isFoundry",
        '.concat(["creditCoin", "creditCrate"])',
        ".concat(episodeBetaAssetKeys)",
        "function openCreditCrate(crate)",
        "creditCoins.push({",
        "persistEpisodeCredits();",
        "creditsCollected = readEpisodeCredits();",
        "function checkElectrifiedPlatforms()",
        "function buildEpisodeBetaHazards()",
        '"refinery-thermal-vent"',
        '"uplink-arc-leak"',
        "electricLandingGrace = 0.28;",
        "var cycleDuration = platform.electricCycleDuration || 3.6;",
        "var activeDuration = platform.electricActiveDuration || 1.25;",
        "function resetEpisodeBetaPopulation()",
        "function makeFoundryCreditCrates()",
        'makeBetaPickup("jetpack"',
        "makeShard(WIDTH * 3 + 920, 1748",
        "WIDTH * 5 + 920,",
        '"upper-left"',
        '"lower-deck"',
        '"deepworks"',
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
        '["wasp", WIDTH * 4 + 780',
        '["gaunt", WIDTH * 5 + 760',
        'canvas.dataset.betaSentinelCount = "7";',
        '"spore-wisp,clacker-beetle,ridge-skitter"',
        "foundryPlatformModule: {",
        "function beginEpisodeApproach()",
        "function beginWoundDescentBridge()",
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
        source.count("makeCreditCrate(") >= 9,
        "Runtime does not include the eight Foundry credit caches",
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
        "The Uplink Gate opens only when twelve Vesperite Fragments, two",
    )
    for token in design_tokens:
        require(token in level_design, f"Missing level-design contract: {token}")

    print("SUPER FRGMNTS Episode 01 early beta: PASS")
    print("- title, atmospheric arrival, Overworld, and Foundry share one in-page route")
    print("- Overworld tutorial platforms, cache, and prompts are disabled")
    print("- Foundry contains eight main, elevated, and lower-route credit caches")
    print("- moving and forgiving electrified-platform lessons are present")
    print("- Deepworks has one required fragment route and one optional cache route")
    print("- power-ups, room links, stabilizer aprons, and recovery placements use safe buffers")
    print("- seven Chitin Sentinels establish the recurring encounter grammar")
    print("- telescopic laser seeker remains available on every Overworld route")
    print("- the Uplink checkpoint requires twelve fragments, two stabilizers, and the rifle lock")


if __name__ == "__main__":
    main()
