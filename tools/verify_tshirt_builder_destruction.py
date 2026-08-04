#!/usr/bin/env python3
"""Verify the reversible Aryn versus Seam Hunter page encounter."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "tshirt_builder.html"
ENCOUNTER = ROOT / "tshirt_builder_destruction.js"


def require(source: str, fragment: str, label: str) -> None:
    if fragment not in source:
        raise AssertionError(f"Missing {label}: {fragment}")


def image_size(relative_path: str, expected: tuple[int, int]) -> None:
    path = ROOT / relative_path
    if not path.is_file():
        raise AssertionError(f"Missing runtime asset: {relative_path}")
    with Image.open(path) as image:
        if image.size != expected:
            raise AssertionError(
                f"Unexpected size for {relative_path}: {image.size}, expected {expected}"
            )


html = HTML.read_text(encoding="utf-8")
encounter = ENCOUNTER.read_text(encoding="utf-8")

for path, expected in {
    "Images/Game/Super-Frgmnts/aryn-run-ludo-runtime-v2.png": (896, 112),
    "Images/Game/Super-Frgmnts/aryn-jump-ludo-runtime-v1.png": (784, 112),
    "Images/Game/Super-Frgmnts/aryn-command-rest-runtime-v1.png": (112, 112),
    "Images/Game/Super-Frgmnts/enemy-tall-gaunt-alien-walk-sheet-v1.png": (768, 768),
    "Images/Game/Super-Frgmnts/enemy-seam-hunter-death-sheet-v1.png": (1400, 1115),
}.items():
    image_size(path, expected)

for fragment, label in [
    ('id="destroyPageButton"', "encounter trigger"),
    ("Destroy this page", "trigger label"),
    ('id="pageDestructionCanvas"', "encounter canvas"),
    ('id="restoreTimelineButton"', "restore control"),
    ("aryn-run-ludo-runtime-v2.png", "new run animation"),
    ("aryn-jump-ludo-runtime-v1.png", "new jump animation"),
    ("aryn-command-rest-runtime-v1.png", "new rest pose"),
    ("signal-ranger-climb-2frame-sheet.png", "retained climb fallback"),
    ('src="/beam_system.js', "canonical beam renderer"),
    ('src="/tshirt_builder_destruction.js', "encounter runtime"),
    ("window.arynPageRunner", "runner encounter controller"),
    ("motion.jumpPhaseUntil = performance.now() + 150", "three-frame launch timing"),
    ("motion.landUntil = now + 180", "three-frame landing timing"),
]:
    require(html, fragment, label)

if "aryn-drop-ludo-runtime" in html:
    raise AssertionError("Front-facing drop animation must not be used by the T-shirt runner")

for fragment, label in [
    ("var shotTimes = [3.0, 5.2, 7.4, 9.6, 11.8, 14.0, 16.2, 18.4, 20.6]", "nine-shot encounter cadence"),
    ("var hitShotIndexes = new Set([6, 7, 8])", "three-hit finish"),
    ("encounter.canonicalElapsed >= 26", "sub-30-second ceiling"),
    ("Beam.createVolley", "beam creation"),
    ("Beam.updateProjectile", "beam guidance"),
    ("Beam.drawProjectile", "beam drawing"),
    ("enemy-tall-gaunt-alien-walk-sheet-v1.png", "Seam Hunter walk sheet"),
    ("enemy-seam-hunter-death-sheet-v1.png", "Seam Hunter death sheet"),
    ("data-page-damage", "reversible damage markers"),
    ("clearDamage", "damage restoration"),
    ("window.OTWPageDestruction", "QA control surface"),
]:
    require(encounter, fragment, label)

print("T-shirt builder page-destruction encounter: PASS")
