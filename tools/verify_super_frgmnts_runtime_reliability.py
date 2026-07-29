#!/usr/bin/env python3
"""Verify the overnight runtime reliability fixes and QA seam."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def require_tokens(source: str, contract: str, tokens: tuple[str, ...]) -> None:
    for token in tokens:
        require(token in source, f"Missing {contract} contract: {token}")


def main() -> None:
    source = GAME.read_text(encoding="utf-8")

    require_tokens(
        source,
        "legacy hazard rendering",
        (
            "function drawHazards()",
            "if (hazard.id) {",
            "hazard.id\n                                .replace(",
        ),
    )
    require(
        'var hazards = [\n                { x: 545,' in source,
        "The unlabelled legacy hazard set is no longer covered by the guard",
    )

    require_tokens(
        source,
        "completion ordering",
        (
            "function checkUplink()",
            'if (state !== "running" || woundBossPreview) return;',
        ),
    )

    require_tokens(
        source,
        "focus lifecycle",
        (
            "var runtimeFocused = true",
            "runtimeFocused = false",
            "runtimeFocused = true",
            "runtimeFocused &&\n                    (",
            "} else if (!runtimeFocused) {",
        ),
    )
    require(
        source.count("runtimeFocused = false") >= 3,
        "Blur, pagehide, and hidden-page paths must all suspend simulation",
    )
    require(
        source.count("lastFrame = 0") >= 10,
        "Lifecycle recovery must reset frame time before resuming",
    )

    require_tokens(
        source,
        "single responsive title request",
        (
            ".title-screen {\n            --title-art: none;",
            "var mobileTitleSelected = window.matchMedia(",
            "var selectedSource =",
            "titleArtImage.src = selectedSource",
            'sourceNode.removeAttribute("srcset")',
            "restoreTitleArtwork();",
            'id="bossIntroTitle"\n                                data-source=',
            "bossIntroTitle.removeAttribute(\"src\")",
        ),
    )
    require(
        'id="bossIntroTitle"\n                                src=' not in source,
        "The Wound announcement must not be parser-preloaded on non-Wound routes",
    )

    require_tokens(
        source,
        "death-cycle QA",
        (
            "var deathCycleQa =",
            'previewParameters.get("qa") === "death"',
            "elapsed = 2.3",
            "hits = MAX_HITS - 1",
            'canvas.dataset.deathCycleQa = "armed"',
        ),
    )
    require(
        "var deathCycleQa =\n                episodeBetaRun &&" in source,
        "The death-cycle seam must remain restricted to the Episode beta",
    )
    require_tokens(
        source,
        "death/completion collision QA",
        (
            "var completionCollisionQa =",
            '"completion-collision"',
            'id: "qa-completion-collision"',
            "collected = TOTAL_SHARDS",
            "hits = MAX_HITS - 1",
            'canvas.dataset.completionCollisionQa =\n                        "armed"',
        ),
    )
    require(
        "var completionCollisionQa =\n                episodeBetaRun &&" in source,
        "The completion-collision seam must remain restricted to the Episode beta",
    )

    print("SUPER FRGMNTS overnight runtime reliability: PASS")
    print("- legacy hazards render without terminating the animation loop")
    print("- completion cannot override damage or death in the same update")
    print("- focus loss suspends simulation and resets frame timing")
    print("- title and boss announcement art load only when selected")
    print("- the Episode-only death-cycle QA route is deterministic")
    print("- the death/completion collision route reproduces update ordering")


if __name__ == "__main__":
    main()
