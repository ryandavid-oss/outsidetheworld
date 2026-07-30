#!/usr/bin/env python3
"""Verify the opt-in SUPER FRGMNTS production-scale benchmark contract."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    source = GAME.read_text(encoding="utf-8")

    required_tokens = (
        'previewParameters.get("load-profile") || "default"',
        'requestedLoadProfile === "production-scale"',
        'requestedFrameProfile === "benchmark"',
        "var PRODUCTION_SCALE_ENEMY_MULTIPLIER = 3;",
        "var PRODUCTION_SCALE_SHARD_MULTIPLIER = 2;",
        "var FRAME_BENCHMARK_WARMUP_MS = 2000;",
        "var FRAME_BENCHMARK_SAMPLE_MS = 10000;",
        "function productionScaleLoadActive()",
        "function applyProductionScaleLoad()",
        '"production-scale-v1"',
        '"distributed-eight-room"',
        '"suppressed-for-repeatability"',
        "function resetFrameBenchmark()",
        "function updateFrameBenchmark(",
        "function completeFrameBenchmark(now)",
        "function frameBenchmarkPercentile(values, percentile)",
        '"frame-time-v1"',
        "canvas.dataset.benchmarkResult",
        '"Main-thread timing excludes asynchronous GPU completion."',
        "updateDuration + drawDuration",
    )
    for token in required_tokens:
        require(
            token in source,
            f"Missing performance benchmark contract: {token}",
        )

    require(
        source.index("applyProductionScaleLoad();")
        < source.index("canvas.dataset.enemyRoster = enemies"),
        "The production-scale population must be applied before roster telemetry",
    )
    require(
        source.index("resetFrameBenchmark();")
        < source.index("jumpBuffer = 0;", source.index("function resetGame")),
        "The frame benchmark must reset with the gameplay run",
    )
    require(
        "if (productionScaleLoadActive()) return;"
        in source[source.index("function takeHit(") :],
        "The repeatable load profile must suppress player damage",
    )

    print("SUPER FRGMNTS performance benchmark: PASS")
    print("- production load is explicitly query-gated")
    print("- the current Foundry roster scales to 3x enemies and 2x fragments")
    print("- benchmark sampling includes warmup and frame-time percentiles")
    print("- normal gameplay remains on the default load and frame profiles")


if __name__ == "__main__":
    main()
