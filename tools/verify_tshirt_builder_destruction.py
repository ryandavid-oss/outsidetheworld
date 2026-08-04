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
    ('id="pageDestructionFacade"', "destructible page façade"),
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
    ("motion.feetY = groundY()", "combat ground reset"),
    ("motion.combatJumpRequested", "authored combat jump queue"),
    ("cueJump: function", "encounter jump choreography API"),
    ("function activeRunSpeed()", "faster combat pursuit"),
    ("page-shard-fly", "page fragment flight animation"),
]:
    require(html, fragment, label)

if "aryn-drop-ludo-runtime" in html:
    raise AssertionError("Front-facing drop animation must not be used by the T-shirt runner")

for fragment, label in [
    ("var shotTimes = [1.6, 3.0, 4.4, 5.8, 7.2, 8.6, 10.0, 11.4, 12.8, 14.2, 15.6, 17.0, 18.4, 21.2]", "fourteen-shot encounter cadence"),
    ("var killShotIndex = 13", "fourteenth-shot kill"),
    ("fireShot(encounter.nextShot === killShotIndex", "single final direct hit"),
    ('setStatus("Shot 14 // Direct hit", "Seam Hunter // Eliminated")', "explicit kill confirmation"),
    ("encounter.canonicalElapsed >= 26", "sub-30-second ceiling"),
    ("Beam.createVolley", "beam creation"),
    ("Beam.updateProjectile", "beam guidance"),
    ("Beam.drawProjectile", "beam drawing"),
    ("enemy-tall-gaunt-alien-walk-sheet-v1.png", "Seam Hunter walk sheet"),
    ("enemy-seam-hunter-death-sheet-v1.png", "Seam Hunter death sheet"),
    ("function captureFacade()", "live-DOM façade capture"),
    ("cloneWithCanvasPixels", "shirt preview canvas cloning"),
    ("function shatterFragment", "independent shard construction"),
    ("var shardClips", "twelve-piece fracture map"),
    ("obliterateRemainingFacade", "complete façade destruction"),
    ('window.scrollTo({\n            top: 0', "scroll-to-top prologue"),
    ('facade.replaceChildren()', "reversible façade cleanup"),
    ('"page-destruction-facade-ready"', "real builder restoration"),
    ("var enemyRoute = [", "authored Seam Hunter route"),
    ("var runnerJumpTimes = [4.05, 8.05, 12.35, 16.35]", "authored pursuit jumps"),
    ("return chasePoint()", "Aryn chase-line targeting"),
    ('kind: "debris"', "small impact debris"),
    ('kind: "dust"', "impact dust"),
    ('kind: "smoke"', "impact smoke"),
    ('kind: "fire"', "impact fire"),
    ('kind: "ring"', "lethal blast ring"),
    ("drawImpactFlash", "lethal impact flash"),
    ("window.OTWPageDestruction", "QA control surface"),
]:
    require(encounter, fragment, label)

if "html2canvas" in encounter.lower() or "data-page-damage" in encounter:
    raise AssertionError("Encounter must use the reversible DOM façade, not screenshots or live-DOM damage")

print("T-shirt builder page-destruction encounter: PASS")
