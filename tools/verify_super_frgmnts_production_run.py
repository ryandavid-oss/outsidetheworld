#!/usr/bin/env python3
"""Verify the assembled Episode 01 beta-production route."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
CONTRACT = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "EPISODE-01-BETA-PRODUCTION-RUN-v1.md"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def function_body(source: str, name: str, next_name: str) -> str:
    match = re.search(
        rf"function {re.escape(name)}\([^)]*\) \{{(.*?)"
        rf"\n            \}}\n\n"
        rf"            function {re.escape(next_name)}",
        source,
        flags=re.DOTALL,
    )
    require(match is not None, f"Could not inspect {name}")
    return match.group(1)


def main() -> None:
    source = GAME.read_text(encoding="utf-8")
    contract = CONTRACT.read_text(encoding="utf-8")

    required_runtime_tokens = (
        'episodeStage === "wound"',
        'var isWound = scene === "wound";',
        'if (scene === "wound") {',
        "return sceneKeys.concat(woundBossAssetKeys);",
        "woundBossPreview = isWound;",
        "WORLD_WIDTH = isWound",
        "? WOUND_BOSS_WORLD_WIDTH",
        "? buildWoundBossPlatforms()",
        'setAudioScene(isWound ? "wound" : scene);',
        "function beginEpisodeApproach()",
        "function beginWoundDescentBridge()",
        'routeStage === "wound"',
        ".stage-shell.is-episode-blackout::after",
        'woundBossPreview &&\n                previewParameters.get("qa") === "reward"',
        'canvas.dataset.episodeScene = scene;',
        '"surface-return-complete"',
        "function surfaceTransportIsSealed()",
        '"sealed-after-return"',
    )
    for token in required_runtime_tokens:
        require(
            token in source,
            f"Missing production route contract: {token}",
        )

    checkpoint = function_body(
        source,
        "captureEpisodeWoundSnapshot",
        "beginEpisodeWoundTransition",
    )
    for field in (
        "score: score",
        "hits: hits",
        "timeLeft: timeLeft",
        "collected: collected",
        "creditsCollected: creditsCollected",
        "vesperiteCollected: vesperiteCollected",
        "jetpackOwned: jetpackOwned",
        "heavyRifleOwned: heavyRifleOwned",
        "selectedWeapon: selectedWeapon",
        "blasterTier: blasterTier",
    ):
        require(field in checkpoint, f"Wound checkpoint omits {field}")
    require(
        "if (annihilationComplete)" in checkpoint
        and "score += 1500;" in checkpoint,
        "Foundry annihilation bonus is not awarded at the Uplink checkpoint",
    )

    wound_transition = function_body(
        source,
        "beginEpisodeWoundTransition",
        "beginEpisodeSurfaceReturn",
    )
    for token in (
        "state = \"transition\";",
        "releaseAllControls();",
        "episodeWoundSnapshot = captureEpisodeWoundSnapshot();",
        'canvas.dataset.episodeTransition =\n                    "foundry-to-wound";',
        "beginWoundDescentBridge();",
    ):
        require(token in wound_transition, f"Unsafe Wound transition: {token}")

    wound_bridge = function_body(
        source,
        "beginWoundDescentBridge",
        "episodeSceneAssetKeys",
    )
    for token in (
        'showEpisodeBridge("wound", "wound");',
        '"Uplink Gate // Checkpoint secured"',
        '"Coreworks // Sublevel transit"',
        '"Unknown chamber // Pressure seal"',
        "completeEpisodeBridge",
    ):
        require(
            token in wound_bridge,
            f"Incomplete Foundry-to-Wound bridge: {token}",
        )

    uplink = function_body(source, "checkUplink", "winGame")
    require(
        "if (episodeBetaRun)" in uplink
        and "beginEpisodeWoundTransition();" in uplink,
        "The production Uplink Gate still ends before The Wound",
    )
    require(
        "if (surfaceTransportIsSealed())" in uplink
        and '"RETURN ROUTE SEALED"' in uplink
        and "return;" in uplink,
        "Surface-return transport can reactivate after specimen recovery",
    )

    boss_completion = function_body(
        source,
        "winWoundBossTrial",
        "takeHit",
    )
    require(
        "if (episodeOneRun)" in boss_completion
        and "beginEpisodeSurfaceReturn();" in boss_completion,
        "Production boss recovery does not enter the surface return",
    )
    require(
        'canvas.dataset.woundVesperiteReward =\n'
        '                        "recovered"' in boss_completion,
        "Production completion does not mark the specimen recovered",
    )

    surface_transition = function_body(
        source,
        "beginEpisodeSurfaceReturn",
        "returnToSurfaceAfterMission",
    )
    for token in (
        'packUpgradeMaterial: "wound-touched-vesperite"',
        'stageShell.classList.add("is-episode-blackout");',
        "returningToSurface: true",
        "fadeFromBlack: true",
        '"overworld"',
    ):
        require(
            token in surface_transition,
            f"Unsafe surface-return transition: {token}",
        )

    reset_match = re.search(
        r"function resetGame\(autostart\) \{(.*?)\n            \}\n\n"
        r"            function makeShard",
        source,
        flags=re.DOTALL,
    )
    require(reset_match is not None, "Could not inspect resetGame")
    reset_body = reset_match.group(1)
    require(
        "if (woundBossPreview && episodeWoundSnapshot)" in reset_body,
        "Boss retry does not restore the Uplink checkpoint",
    )
    require(
        'state === "lost"' in reset_body
        and "hits = regenerateWoundRetry" in reset_body
        and "? 0" in reset_body
        and ": episodeWoundSnapshot.hits" in reset_body,
        "Boss retry does not regenerate Aryn's health",
    )
    require(
        re.search(
            r"surfaceReturnLoadout\s*\.packUpgradeMaterial",
            reset_body,
        )
        and "woundVesperiteRecovered" in reset_body,
        "Surface return does not restore Wound-touched Vesperite",
    )

    required_contract_tokens = (
        "## Player-facing sequence",
        "## Checkpoint contract",
        "### Uplink Gate → The Wound",
        "### Wound recovery → surface",
        "The whole stage reaches opaque black before scene replacement.",
        "Boss retry begins in the safe bay with five hearts",
        "Desktop and 390 × 844 portrait framing",
        "The Coreworks transport remains physically present but sealed",
    )
    for token in required_contract_tokens:
        require(token in contract, f"Production contract omits: {token}")

    require(
        "window.location.href" not in source,
        "The production run still contains a full-page scene reload",
    )

    print("SUPER FRGMNTS Episode 01 beta production run: PASS")
    print("- Arrival, Overworld, Foundry, Wound, recovery, and surface share one runtime")
    print("- the Uplink Gate preserves Foundry progress for the boss checkpoint")
    print("- boss retries regenerate health while restoring score, time, and equipment")
    print("- Wound-touched Vesperite recovery is the completion condition")
    print("- a locked black transition returns Aryn to the Veyra surface")
    print("- the returned player cannot re-enter the Foundry transport")


if __name__ == "__main__":
    main()
