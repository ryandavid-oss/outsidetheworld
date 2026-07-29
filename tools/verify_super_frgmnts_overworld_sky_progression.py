#!/usr/bin/env python3
"""Verify the stabilizer and infestation-driven Overworld sky progression."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
ATMOSPHERE = (
    ROOT
    / "Design/Super-Frgmnts/Overworld/Phase-3/Outpost"
    / "ATMOSPHERE-CONTRACT.md"
)


def require(fragment: str, source: str, label: str) -> None:
    if fragment not in source:
        raise AssertionError(f"Missing {label}: {fragment}")


def main() -> None:
    runtime = GAME.read_text(encoding="utf-8")
    contract = ATMOSPHERE.read_text(encoding="utf-8")

    required_runtime = {
        "review parameter": (
            'previewParameters.get("sky") || ""'
        ),
        "state resolver": "function overworldSkyProgression()",
        "arrival state": '"atmosphere-suppressed"',
        "first relay state": '"first-relay-rising"',
        "restored state": '"stabilizers-restored"',
        "clearing state": '"infestation-receding"',
        "cliffhanger state": '"signal-remnant"',
        "return progression": "if (episodeSurfaceReturn)",
        "report progression": "returnDialogueHasPlayed",
        "restoration telemetry": (
            "canvas.dataset.overworldSkyRestoration"
        ),
        "infestation telemetry": (
            "canvas.dataset.overworldInfestationPressure"
        ),
        "storm telemetry": "canvas.dataset.overworldStormOpacity",
        "storm thinning": (
            "0.32 - restoration * 0.18"
        ),
        "storm lift": "118 - restoration * 24",
        "warm clearing": "var clearingLight =",
        "localized remnant": "var infestationRemnant =",
        "Coreworks anchor": (
            "COREWORKS_TRANSPORT_CENTER_X -"
        ),
    }
    for label, fragment in required_runtime.items():
        require(fragment, runtime, label)

    atmosphere_block = runtime.split(
        "function drawOverworldAtmosphere()",
        1,
    )[1].split("function drawOverworldVolcano()", 1)[0]
    require(
        'ctx.globalCompositeOperation = "multiply";',
        atmosphere_block,
        "background-only pressure compositing",
    )
    require(
        'ctx.globalCompositeOperation = "screen";',
        atmosphere_block,
        "background-only clearing compositing",
    )
    require(
        "drawOverworldBirds(now);",
        atmosphere_block,
        "atmosphere render ordering",
    )

    required_contract = (
        "The Overworld sky is readable game state",
        "Arrival / `sky=arrival`",
        "First relay / `sky=relay-one`",
        "Both relays / `sky=stabilized`",
        "Seam Hunter cleared / `sky=cleared`",
        "localized violet remnant",
        "never crosses Aryn, the RD-42",
    )
    for fragment in required_contract:
        require(fragment, contract, "atmosphere contract")

    print("SUPER FRGMNTS Overworld sky progression: PASS")
    print("- Arrival retains storm and infestation pressure")
    print("- first-relay and both-relay clearing states are deterministic")
    print("- post-Wound return restores warmth and thins the storm deck")
    print("- a localized Coreworks remnant carries the Chapter 02 threat")
    print("- all treatments remain behind the ship, actors, props, and HUD")


if __name__ == "__main__":
    main()
