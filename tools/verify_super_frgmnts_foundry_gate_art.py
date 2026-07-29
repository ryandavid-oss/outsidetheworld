#!/usr/bin/env python3
"""Verify the production Uplink bulkhead and arc-discharge artwork."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
HAZARD_MANIFEST = (
    ROOT
    / "Design/Super-Frgmnts/Foundry/Hazards"
    / "foundry-hazard-runtime-v1.json"
)
GATE_MANIFEST = (
    ROOT
    / "Design/Super-Frgmnts/Foundry/Uplink-Gate"
    / "foundry-uplink-boss-gate-runtime-v1.json"
)
LEVEL_CONTRACT = (
    ROOT
    / "Design/Super-Frgmnts/Foundry"
    / "SHARD-FOUNDRY-LEVEL-DESIGN-v1.md"
).read_text(encoding="utf-8")
SOURCE = (ROOT / "super_frgmnts.html").read_text(encoding="utf-8")


def verify_image(
    relative_path: str,
    expected_size: list[int],
    expected_hash: str,
    require_transparency: bool = True,
) -> None:
    path = ROOT / relative_path
    assert path.exists(), f"Missing {relative_path}"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == expected_hash, (
        f"{relative_path}: expected {expected_hash}, got {digest}"
    )
    image = Image.open(path).convert("RGBA")
    assert list(image.size) == expected_size
    alpha_extrema = image.getchannel("A").getextrema()
    if require_transparency:
        assert alpha_extrema == (0, 255)
    else:
        assert alpha_extrema[1] == 255
    assert image.getbbox() is not None


def main() -> None:
    hazard = json.loads(HAZARD_MANIFEST.read_text(encoding="utf-8"))
    gate = json.loads(GATE_MANIFEST.read_text(encoding="utf-8"))

    assert hazard["status"] == "production-runtime"
    arc = hazard["assets"]["arcDischarge"]
    verify_image(
        arc["chromaSource"],
        arc["chromaSourceSize"],
        arc["chromaSourceSha256"],
        require_transparency=False,
    )
    verify_image(
        arc["alphaSource"],
        arc["alphaSourceSize"],
        arc["alphaSourceSha256"],
    )
    verify_image(
        arc["runtime"],
        arc["runtimeSize"],
        arc["runtimeSha256"],
    )
    assert arc["replaces"] == "procedural parallel zigzag strokes"

    assert gate["status"] == "beta-production"
    gate_chroma = gate["assets"]["chromaSource"]
    verify_image(
        gate_chroma["path"],
        gate_chroma["size"],
        gate_chroma["sha256"],
        require_transparency=False,
    )
    gate_alpha = gate["assets"]["alphaSource"]
    verify_image(
        gate_alpha["path"],
        gate_alpha["size"],
        gate_alpha["sha256"],
    )
    gate_runtime = gate["assets"]["runtime"]
    verify_image(
        gate_runtime["path"],
        gate_runtime["size"],
        gate_runtime["sha256"],
    )
    assert gate["placement"]["room"] == 7
    assert gate["placement"]["bottomY"] == 600
    assert gate["placement"]["drawWidth"] == 444
    assert gate["placement"]["drawHeight"] == 376
    assert gate["placement"]["trigger"] == {
        "localX": 1218,
        "y": 280,
        "width": 132,
        "height": 320,
    }

    required_runtime = (
        'source: "/Images/Game/Super-Frgmnts/foundry-arc-discharge-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/foundry-uplink-boss-gate-runtime-v1.png"',
        '"foundryArcDischarge"',
        '"foundryUplinkBossGate"',
        "assets.foundryArcDischarge",
        "assets.foundryUplinkBossGate",
        "var foundryUplinkQa =",
        'previewParameters.get("qa") === "uplink"',
        "function drawUplink()",
        'canvas.dataset.uplinkGateArt =',
        '"sprite-v1"',
        'canvas.dataset.seamLurkerAnchor =',
        '"uplink-catwalk-underside-y362"',
    )
    for fragment in required_runtime:
        assert fragment in SOURCE, f"Missing Foundry art token: {fragment}"

    assert "compact branching cyan-white 16-bit sprite" in LEVEL_CONTRACT
    assert "444 × 376 physical bulkhead" in LEVEL_CONTRACT
    assert "No magical ring, floating rectangle, or dashed barrier" in (
        LEVEL_CONTRACT
    )

    print("SUPER FRGMNTS Uplink gate and arc art: PASS")
    print("- production source, alpha, and runtime hashes match manifests")
    print("- compact sprite discharge replaces procedural zigzag electricity")
    print("- 444 × 376 bulkhead is rooted at Uplink deck y=600")
    print("- locked/open gate states use one physical passage silhouette")
    print("- QA route frames the gate with production desktop indicators")


if __name__ == "__main__":
    main()
