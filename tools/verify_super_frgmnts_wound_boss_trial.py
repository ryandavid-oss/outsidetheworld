#!/usr/bin/env python3
"""Verify the isolated Seam Hunter boss-trial wiring."""

from pathlib import Path
import wave

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "super_frgmnts.html"
BACKGROUND_SLICES = {
    (
        ROOT
        / "Images"
        / "Game"
        / "Super-Frgmnts"
        / "foundry-wound-boss-room-background-runtime-v3-left.png"
    ): (1290, 1882),
    (
        ROOT
        / "Images"
        / "Game"
        / "Super-Frgmnts"
        / "foundry-wound-boss-room-background-runtime-v3-right.png"
    ): (1290, 1882),
}
LASER_SHEET = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "enemy-tall-gaunt-alien-laser-eyes-sheet-v1.png"
)
EXPECTED_LASER_SHEET_SIZE = (960, 840)
LASER_IMPACT_SHEET = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "wound-laser-ground-impact-sheet-v1.png"
)
EXPECTED_LASER_IMPACT_SHEET_SIZE = (384, 288)
DEATH_SHEET = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "enemy-seam-hunter-death-sheet-v1.png"
)
EXPECTED_DEATH_SHEET_SIZE = (1400, 1115)
GANTRY_WATCH_SHEET = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "enemy-seam-hunter-upward-watch-sheet-v2.png"
)
EXPECTED_GANTRY_WATCH_SHEET_SIZE = (2020, 1832)
GANTRY_TURN_SHEET = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "enemy-seam-hunter-upward-turn-sheet-v1.png"
)
EXPECTED_GANTRY_TURN_SHEET_SIZE = (2045, 1832)
ANNOUNCEMENT_TITLE = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "seam-hunter-encounter-title-runtime-v1.png"
)
EXPECTED_ANNOUNCEMENT_TITLE_SIZE = (1400, 320)
WOUND_VESPERITE = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "wound-touched-vesperite-runtime-v1.png"
)
EXPECTED_WOUND_VESPERITE_SIZE = (128, 144)
WOUND_VESPERITE_CONTRACT = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Boss-Room"
    / "Wound-Vesperite"
    / "WOUND-TOUCHED-VESPERITE-v1.md"
)
ANNOUNCEMENT_AUDIO = {
    (
        ROOT
        / "Audio"
        / "super-frgmnts-wound-ignition-v1.wav"
    ): 0.6,
    (
        ROOT
        / "Audio"
        / "super-frgmnts-title-arrival-v1.wav"
    ): 0.88,
    (
        ROOT
        / "Audio"
        / "super-frgmnts-energy-sweep-v1.wav"
    ): 0.8,
    (
        ROOT
        / "Audio"
        / "super-frgmnts-resonance-tail-v1.wav"
    ): 2.4,
}
BOSS_MUSIC = (
    ROOT
    / "Audio"
    / "super-frgmnts-seam-hunter-boss-v1.m4a"
)
BOSS_MUSIC_SOURCE = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Boss-Room"
    / "Music"
    / "Raw"
    / "subterranean-apex-source-v1.wav"
)
BOSS_MUSIC_DURATION = 120.0
ANNOUNCEMENT_CONTRACT = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Boss-Room"
    / "Announcement"
    / "WOUND-BOSS-ANNOUNCEMENT-v1.md"
)
LIFT_ASSETS = {
    (
        ROOT
        / "Images"
        / "Game"
        / "Super-Frgmnts"
        / "wound-construction-lift-tower-runtime-v1.png"
    ): (320, 592),
    (
        ROOT
        / "Images"
        / "Game"
        / "Super-Frgmnts"
        / "wound-construction-lift-platform-runtime-v1.png"
    ): (320, 72),
    (
        ROOT
        / "Images"
        / "Game"
        / "Super-Frgmnts"
        / "wound-construction-lift-cable-tile-v1.png"
    ): (8, 64),
    (
        ROOT
        / "Images"
        / "Game"
        / "Super-Frgmnts"
        / "wound-construction-gantry-runway-runtime-v2.png"
    ): (1420, 64),
    (
        ROOT
        / "Images"
        / "Game"
        / "Super-Frgmnts"
        / "wound-construction-gantry-car-runtime-v1.png"
    ): (300, 152),
}

REQUIRED_SNIPPETS = {
    "preview route": (
        'previewParameters.get("preview") === "wound-boss"'
    ),
    "isolated arena": "function buildWoundBossPlatforms()",
    "wide arena width": (
        "var WOUND_BOSS_WORLD_WIDTH = 2580;"
    ),
    "left background slice": (
        "foundry-wound-boss-room-background-runtime-v3-left.png"
    ),
    "right background slice": (
        "foundry-wound-boss-room-background-runtime-v3-right.png"
    ),
    "clear combat runway": (
        "var WOUND_COMBAT_LANE_WIDTH = 1420;"
    ),
    "left lift boundary": (
        "var WOUND_LIFT_LEFT_X = 250;"
    ),
    "right lift boundary": (
        "WOUND_COMBAT_LANE_X + WOUND_COMBAT_LANE_WIDTH"
    ),
    "200 hit points": "var WOUND_BOSS_HEALTH = 200;",
    "walk render size": (
        "var WOUND_BOSS_WALK_RENDER_SIZE = 448;"
    ),
    "attack render width": (
        "var WOUND_BOSS_ATTACK_RENDER_WIDTH = 560;"
    ),
    "visible sweep start": (
        "var WOUND_BOSS_SWEEP_FIRST_FRAME = 14;"
    ),
    "visible sweep finish": (
        "var WOUND_BOSS_SWEEP_LAST_FRAME = 19;"
    ),
    "boss factory": "function makeWoundBoss()",
    "strategic platform route": "woundBossRoute: true",
    "integrated construction art": (
        "wound-construction-lift-tower-runtime-v1.png"
    ),
    "integrated gantry art": (
        "wound-construction-gantry-car-runtime-v1.png"
    ),
    "wide gantry runway art": (
        "wound-construction-gantry-runway-runtime-v2.png"
    ),
    "platform surface anchor": (
        "var WOUND_LIFT_PLATFORM_SURFACE_Y = 12;"
    ),
    "fifteen percent faster lifts": (
        "var WOUND_LIFT_SPEED = 0.5 * 1.15;"
    ),
    "entrance lift encounter gate": (
        "woundEncounterGateLift: true"
    ),
    "entrance lift parked at top": (
        '"parked-top"'
    ),
    "entrance lift combat release": (
        '"combat-cycle"'
    ),
    "gantry surface anchor": (
        "var WOUND_GANTRY_CAR_SURFACE_Y = 86;"
    ),
    "preview-only boss marker": "boss.woundBoss = true;",
    "four damage phases": "function woundBossDamagePhase(enemy)",
    "threshold phase synchronization": (
        "function syncWoundBossDamagePhase("
    ),
    "pink damage tinge": '"pink-tinge"',
    "blinking pink damage state": '"pink-blink"',
    "critical redline state": '"redline-blink"',
    "phase-scaled pursuit": "function woundBossEffectiveSpeedScale(enemy)",
    "phase-scaled recovery": "function woundBossRecoveryScale(enemy)",
    "phase-scaled laser cadence": (
        "function woundBossLaserCooldownForPhase(enemy)"
    ),
    "one-time opening laser lock": (
        "var WOUND_BOSS_OPENING_LASER_LOCK = 0.5;"
    ),
    "mobile opening laser lock": (
        "var WOUND_BOSS_MOBILE_OPENING_LASER_LOCK = 0.65;"
    ),
    "opening laser armed": "boss.openingLaserPending = true;",
    "opening target lock behavior": '"opening-lock"',
    "opening laser telemetry": (
        'canvas.dataset.woundBossOpeningLaser ='
    ),
    "phase-scaled high-ground response": (
        "function woundBossConfusionDurationForPhase(enemy)"
    ),
    "grounded sprite compensation": (
        "WOUND_BOSS_WALK_BOTTOM_PADS"
    ),
    "rifle granted": "heavyRifleOwned = true;",
    "PACK selected": 'selectedWeapon = "pack";',
    "boss-lane rifle travel": (
        "var WOUND_BOSS_RIFLE_BOLT_LIFE = 1.8;"
    ),
    "boss-lane world culling": (
        "woundBossPreview &&\n                        activeBolt.direct"
    ),
    "boss rifle-ready hold": (
        "function woundBossRifleHoldActive()"
    ),
    "faster trial rifle fire": (
        "var WOUND_BOSS_RIFLE_FIRE_DURATION = 0.3;"
    ),
    "faster trial rifle cooldown": (
        "var WOUND_BOSS_RIFLE_COOLDOWN = 0.3;"
    ),
    "compressed rifle animation": (
        "function activeRifleFireDuration()"
    ),
    "broad boss body contact": (
        "function getWoundBossBodyHurtbox("
    ),
    "whole-body damage": (
        'woundBossHitType = "body";'
    ),
    "always vulnerable": (
        'canvas.dataset.woundBossVulnerable =\n                        "true";'
    ),
    "aggressive near pursuit": (
        "var WOUND_BOSS_STALK_SPEED = 88;"
    ),
    "aggressive mid pursuit": (
        "var WOUND_BOSS_MID_SPEED = 132;"
    ),
    "aggressive far pursuit": (
        "var WOUND_BOSS_SURGE_SPEED = 196;"
    ),
    "readable turn duration": (
        "var WOUND_BOSS_TURN_DURATION = 0.54;"
    ),
    "turn-behind confirmation": (
        "var WOUND_BOSS_TURN_CONFIRM_TIME = 0.1;"
    ),
    "turn braking": (
        "var WOUND_BOSS_TURN_BRAKE_TIME = 0.16;"
    ),
    "single turn flip": (
        "enemy.turnFlipped = true;"
    ),
    "post-turn commitment": (
        "var WOUND_BOSS_POST_TURN_COMMIT = 0.38;"
    ),
    "accelerated pursuit": (
        "function approachWoundBossVelocity("
    ),
    "lift-only confusion threshold": (
        "var WOUND_BOSS_CONFUSION_ELEVATION = 190;"
    ),
    "high-ground confusion grace": (
        "var WOUND_BOSS_CONFUSION_GRACE = 0.25;"
    ),
    "bounded confusion duration": (
        "var WOUND_BOSS_CONFUSION_DURATION = 1.6;"
    ),
    "confusion behavior": (
        "function beginWoundBossConfused("
    ),
    "lost perception telemetry": (
        'canvas.dataset.woundBossPerception =\n                    "lost";'
    ),
    "search behavior": (
        'enemy.behavior === "search"'
    ),
    "direction-aware left search edge": (
        "enemy.searchDirection < 0"
    ),
    "direction-aware right search edge": (
        "enemy.searchDirection > 0"
    ),
    "curated gantry-watch asset": (
        "enemy-seam-hunter-upward-watch-sheet-v2.png"
    ),
    "authored gantry-watch frame count": (
        "var WOUND_BOSS_WATCH_FRAME_COUNT = 16;"
    ),
    "upward-watch entry state": (
        'enemy.behavior === "gantry-watch-enter"'
    ),
    "held upward-watch state": (
        'enemy.behavior === "gantry-watch"'
    ),
    "authored upward turnaround asset": (
        "enemy-seam-hunter-upward-turn-sheet-v1.png"
    ),
    "authored upward turnaround state": (
        'enemy.behavior === "gantry-watch-turn"'
    ),
    "curated upward turnaround frame count": (
        "var WOUND_BOSS_WATCH_TURN_FRAME_COUNT = 19;"
    ),
    "confirmed tracking begins authored turn": (
        "beginWoundBossGantryWatchTurn(\n"
        "                                    enemy,\n"
        "                                    watchFacing"
    ),
    "shaft-sentry retreat": (
        'enemy.behavior === "shaft-retreat"'
    ),
    "shaft-sentry guard": (
        'enemy.behavior === "shaft-guard"'
    ),
    "high-gantry pose trigger": (
        "playerOnWoundGantry"
    ),
    "gantry watch has an independent latch": (
        "enemy.gantryWatchArmed"
    ),
    "gantry watch survives prior lift confusion": (
        "boss.confusionUsed = woundBossSentryQa;"
    ),
    "gantry watch tracking deadzone": (
        "var WOUND_BOSS_WATCH_TRACK_DEADZONE = 110;"
    ),
    "gantry watch tracking confirmation": (
        "var WOUND_BOSS_WATCH_TRACK_CONFIRM = 0.2;"
    ),
    "gantry watch exit grace": (
        "var WOUND_BOSS_WATCH_EXIT_GRACE = 0.28;"
    ),
    "gantry watch turn cadence": (
        "var WOUND_BOSS_WATCH_TURN_FRAME_DURATION = 0.045;"
    ),
    "main-deck turn confirmation": (
        "var WOUND_BOSS_TURN_CONFIRM_TIME = 0.1;"
    ),
    "main-deck turn duration": (
        "var WOUND_BOSS_TURN_DURATION = 0.54;"
    ),
    "post-turn commitment": (
        "var WOUND_BOSS_POST_TURN_COMMIT = 0.38;"
    ),
    "heavy-rifle projectile treatment": (
        "function drawHeavyRifleBolt(bolt)"
    ),
    "heavy-rifle white-hot core": (
        'ctx.fillStyle = "#fff7d2";'
    ),
    "laser asset": (
        "enemy-tall-gaunt-alien-laser-eyes-sheet-v1.png"
    ),
    "aggressive laser cadence": (
        "var WOUND_BOSS_LASER_COOLDOWN = 4.4;"
    ),
    "laser visible damage start": (
        "var WOUND_BOSS_LASER_FIRST_ACTIVE_FRAME = 15;"
    ),
    "laser visible damage finish": (
        "var WOUND_BOSS_LASER_LAST_ACTIVE_FRAME = 30;"
    ),
    "laser behavior": (
        "function beginWoundBossLaser("
    ),
    "laser beam renderer": (
        "function drawWoundBossLaserBeam("
    ),
    "locked downward laser aim": (
        "function lockWoundBossLaserAim("
    ),
    "bounded downward angle": (
        "var WOUND_BOSS_LASER_MIN_ANGLE = 0.2;"
    ),
    "diagonal laser collision": (
        "function woundBossLaserIntersectsPlayer("
    ),
    "charge path telegraph": (
        "ctx.setLineDash([12, 10]);"
    ),
    "horizontal-beam-free active pose": (
        "var spriteFrameIndex ="
    ),
    "source-sampled laser extension": (
        "WOUND_BOSS_LASER_FRAME_WIDTH - 1"
    ),
    "laser ground-impact asset": (
        "wound-laser-ground-impact-sheet-v1.png"
    ),
    "laser ground-impact renderer": (
        "function drawWoundBossLaserImpact("
    ),
    "impact begins on active laser": (
        "enemy.laserImpactTime = 0;"
    ),
    "impact is cosmetic telemetry": (
        'canvas.dataset.woundBossLaserImpact = "active";'
    ),
    "boss death asset": (
        "enemy-seam-hunter-death-sheet-v1.png"
    ),
    "25-frame death sequence": (
        "var WOUND_BOSS_DEATH_FRAME_COUNT = 25;"
    ),
    "authored death timing": (
        "var WOUND_BOSS_DEATH_FRAME_DURATION = 0.107;"
    ),
    "death sequence start": (
        "function beginWoundBossDeath("
    ),
    "delayed victory finalization": (
        "function finalizeWoundBossDeath("
    ),
    "ground impact cue": (
        "WOUND_BOSS_DEATH_IMPACT_FRAME"
    ),
    "persistent corpse telemetry": (
        'canvas.dataset.woundBossCorpse = "true";'
    ),
    "persistent final corpse frame": (
        "? WOUND_BOSS_DEATH_FRAME_COUNT - 1"
    ),
    "unique Wound Vesperite asset": (
        "wound-touched-vesperite-runtime-v1.png"
    ),
    "dynamic remains position": (
        "woundVesperiteX = Math.max("
    ),
    "post-death reward reveal": (
        "function revealWoundVesperiteReward()"
    ),
    "deliberate reward interaction": (
        "function activateWoundVesperiteReward()"
    ),
    "shared down interaction route": (
        "if (activateWoundVesperiteReward())"
    ),
    "per-frame death deck contact": (
        "var WOUND_BOSS_DEATH_BOTTOM_PADS = ["
    ),
    "post-death hold": (
        "var WOUND_BOSS_AFTERMATH_HOLD_DURATION = 1.4;"
    ),
    "post-death darken": (
        "var WOUND_BOSS_AFTERMATH_DARKEN_DURATION = 1.05;"
    ),
    "post-death fade": (
        "var WOUND_BOSS_AFTERMATH_FADE_DURATION = 0.9;"
    ),
    "post-death aftermath update": (
        "function updateWoundBossAftermath(delta)"
    ),
    "near-black corpse treatment": (
        "corpseDarkenProgress * 0.94"
    ),
    "reward renderer": (
        "function drawWoundVesperiteReward()"
    ),
    "silhouette-following reward bloom": (
        '"blur(13px) brightness(1.35) saturate(1.45)"'
    ),
    "reward deck reflection": (
        "var deckGlow ="
    ),
    "future pack material storage": (
        '"wound-touched-vesperite";'
    ),
    "post-victory mission timer hold": (
        "woundBossAftermathActive ||\n                            woundVesperiteRewardReady"
    ),
    "reward-only QA route": (
        'previewParameters.get("qa") === "reward"'
    ),
    "mobile reward interaction label": (
        "Drag down to recover exposed material after the encounter."
    ),
    "gained Wound access": (
        '"THE WOUND // ACCESS GAINED"'
    ),
    "specimen recovery heading": (
        '"SPECIMEN RECOVERED"'
    ),
    "Dras study objective": (
        "Return this to Dras for further study."
    ),
    "laser damage": (
        'takeHit("SEAM LASER")'
    ),
    "boss-aware camera framing": (
        "woundBossPreview && framedWoundBoss"
    ),
    "gantry dual framing": (
        '"gantry-dual-frame"'
    ),
    "aftermath corpse framing": (
        '"aftermath-corpse"'
    ),
    "aftermath reward dual framing": (
        '"aftermath-dual-frame"'
    ),
    "shaft-sentry QA spawn": (
        'previewParameters.get("qa") === "sentry"'
    ),
    "pursuit behavior": '"pursuit"',
    "confused state": '"confused"',
    "turn behavior": '"turn"',
    "reset behavior": '"reset"',
    "boss victory": "function winWoundBossTrial()",
    "body-contact exemption": (
        "Body contact is safe in this trial."
    ),
    "encounter title asset": (
        "seam-hunter-encounter-title-runtime-v1.png"
    ),
    "encounter announcement overlay": (
        'class="boss-intro"'
    ),
    "encounter threshold trigger": (
        "player.x + 56 >= WOUND_BOSS_ENGAGE_X"
    ),
    "encounter announcement state": (
        'state = "boss-intro";'
    ),
    "encounter announcement start": (
        "function beginWoundBossIntro()"
    ),
    "encounter announcement update": (
        "function updateWoundBossIntro(delta)"
    ),
    "encounter announcement completion": (
        "function completeWoundBossIntro(skipped)"
    ),
    "full announcement every retry": (
        'woundBossIntroState = "pending";'
    ),
    "visible skip control": (
        'id="bossIntroSkip"'
    ),
    "enter-only keyboard skip": (
        'event.code === "NumpadEnter"'
    ),
    "controller confirm or pause skip": (
        "if (confirmPressed || pausePressed) {"
    ),
    "edge-triggered controller guard": (
        "function gamepadButtonJustPressed(buttons, index)"
    ),
    "mobile safe-area skip": (
        "env(safe-area-inset-right)"
    ),
    "locked player control": (
        'state === "boss-intro"'
    ),
    "continuous platform clock": (
        "platformMotionElapsed += delta;"
    ),
    "paused mission timer telemetry": (
        "canvas.dataset.woundBossIntroTimerStart"
    ),
    "announcement timer end telemetry": (
        "canvas.dataset.woundBossIntroTimerEnd"
    ),
    "wound ignition cue": (
        "super-frgmnts-wound-ignition-v1.wav"
    ),
    "title arrival cue": (
        "super-frgmnts-title-arrival-v1.wav"
    ),
    "energy sweep cue": (
        "super-frgmnts-energy-sweep-v1.wav"
    ),
    "resonance tail cue": (
        "super-frgmnts-resonance-tail-v1.wav"
    ),
    "dedicated boss score": (
        "super-frgmnts-seam-hunter-boss-v1.m4a"
    ),
    "boss music scene": (
        'wound: backgroundMusic.dataset.woundTrack'
    ),
    "boss music handoff": (
        'setAudioScene("wound", false);'
    ),
    "boss music preload": (
        'backgroundMusicSecondary.dataset.scene = "wound";'
    ),
    "boss reveal concealment": (
        'canvas.dataset.woundBossReveal = "concealed";'
    ),
    "boss reveal visibility": (
        'canvas.dataset.woundBossReveal = "visible";'
    ),
    "boss reveal fade": (
        "var woundBossRevealAlpha = 1;"
    ),
    "post-title boss reveal start": (
        "var WOUND_BOSS_REVEAL_START = 5.05;"
    ),
    "post-title boss reveal duration": (
        "var WOUND_BOSS_REVEAL_DURATION = 1.2;"
    ),
    "separate announcement phase telemetry": (
        "canvas.dataset.woundBossIntroPhase"
    ),
    "boss score volume": (
        "wound: 0.38"
    ),
    "boss reveal easing telemetry": (
        "canvas.dataset.woundBossRevealAlpha"
    ),
    "health bar delayed until gameplay": (
        'woundBossIntroState === "playing"'
    ),
    "anonymous pre-intro mission readout": (
        '"HOSTILE SIGNAL // UNRESOLVED"'
    ),
    "pending boss render guard": (
        'woundBossIntroState === "pending"'
    ),
    "reduced-motion presentation": (
        "@media (prefers-reduced-motion: reduce)"
    ),
}

FORBIDDEN_SNIPPETS = {
    "front armor ricochet": "FRONT ARMOR // RICOCHET",
    "obsolete reward cradle renderer": (
        "function drawWoundVesperiteCradle("
    ),
    "obsolete reward cradle announcement": (
        "EXTRACTION CRADLE ONLINE"
    ),
    "obsolete bait commitment": "beginWoundBossBaitCommit",
    "obsolete pass-through window": "var woundCrossingOpen =",
    "obsolete horizontal beam height": (
        "function getWoundBossLaserBeamY("
    ),
}


def main() -> int:
    failures: list[str] = []

    if not HTML.exists():
        failures.append("missing super_frgmnts.html")
        html = ""
    else:
        html = HTML.read_text(encoding="utf-8")

    for path, expected_size in BACKGROUND_SLICES.items():
        if not path.exists():
            failures.append(
                f"missing Wound boss-room slice: {path.name}"
            )
            continue
        with Image.open(path) as image:
            if image.size != expected_size:
                failures.append(
                    f"{path.name} size is "
                    f"{image.size}, expected "
                    f"{expected_size}"
                )

    if not LASER_SHEET.exists():
        failures.append("missing Seam Hunter laser-eye runtime sheet")
    else:
        with Image.open(LASER_SHEET) as image:
            if image.size != EXPECTED_LASER_SHEET_SIZE:
                failures.append(
                    "laser-eye runtime sheet size is "
                    f"{image.size}, expected "
                    f"{EXPECTED_LASER_SHEET_SIZE}"
                )

    if not LASER_IMPACT_SHEET.exists():
        failures.append("missing laser ground-impact runtime sheet")
    else:
        with Image.open(LASER_IMPACT_SHEET) as image:
            if image.size != EXPECTED_LASER_IMPACT_SHEET_SIZE:
                failures.append(
                    "laser ground-impact sheet size is "
                    f"{image.size}, expected "
                    f"{EXPECTED_LASER_IMPACT_SHEET_SIZE}"
                )

    if not DEATH_SHEET.exists():
        failures.append("missing Seam Hunter death runtime sheet")
    else:
        with Image.open(DEATH_SHEET) as image:
            if image.size != EXPECTED_DEATH_SHEET_SIZE:
                failures.append(
                    "Seam Hunter death sheet size is "
                    f"{image.size}, expected "
                    f"{EXPECTED_DEATH_SHEET_SIZE}"
                )
            if max(image.size) > 2048:
                failures.append(
                    "Seam Hunter death sheet exceeds "
                    "the 2,048 px texture ceiling"
                )

    if not GANTRY_WATCH_SHEET.exists():
        failures.append("missing Seam Hunter gantry-watch sheet")
    else:
        with Image.open(GANTRY_WATCH_SHEET) as image:
            if image.size != EXPECTED_GANTRY_WATCH_SHEET_SIZE:
                failures.append(
                    "gantry-watch sheet size is "
                    f"{image.size}, expected "
                    f"{EXPECTED_GANTRY_WATCH_SHEET_SIZE}"
                )
            if max(image.size) > 2048:
                failures.append(
                    "gantry-watch sheet exceeds "
                    "the 2,048 px texture ceiling"
                )

    if not GANTRY_TURN_SHEET.exists():
        failures.append("missing Seam Hunter gantry-turn sheet")
    else:
        with Image.open(GANTRY_TURN_SHEET) as image:
            if image.size != EXPECTED_GANTRY_TURN_SHEET_SIZE:
                failures.append(
                    "gantry-turn sheet size is "
                    f"{image.size}, expected "
                    f"{EXPECTED_GANTRY_TURN_SHEET_SIZE}"
                )
            if max(image.size) > 2048:
                failures.append(
                    "gantry-turn sheet exceeds "
                    "the 2,048 px texture ceiling"
                )

    if not ANNOUNCEMENT_TITLE.exists():
        failures.append("missing Seam Hunter announcement title")
    else:
        with Image.open(ANNOUNCEMENT_TITLE) as image:
            if image.size != EXPECTED_ANNOUNCEMENT_TITLE_SIZE:
                failures.append(
                    "announcement title size is "
                    f"{image.size}, expected "
                    f"{EXPECTED_ANNOUNCEMENT_TITLE_SIZE}"
                )
            if image.mode != "RGBA":
                failures.append(
                    "announcement title mode is "
                    f"{image.mode}, expected RGBA"
                )

    if not ANNOUNCEMENT_CONTRACT.exists():
        failures.append("missing Wound boss announcement contract")

    if not WOUND_VESPERITE.exists():
        failures.append("missing Wound-touched Vesperite runtime asset")
    else:
        with Image.open(WOUND_VESPERITE) as image:
            if image.size != EXPECTED_WOUND_VESPERITE_SIZE:
                failures.append(
                    "Wound-touched Vesperite size is "
                    f"{image.size}, expected "
                    f"{EXPECTED_WOUND_VESPERITE_SIZE}"
                )
            if image.mode != "RGBA":
                failures.append(
                    "Wound-touched Vesperite mode is "
                    f"{image.mode}, expected RGBA"
                )
            elif image.getchannel("A").getextrema()[0] != 0:
                failures.append(
                    "Wound-touched Vesperite has no transparent pixels"
                )

    if not WOUND_VESPERITE_CONTRACT.exists():
        failures.append("missing Wound-touched Vesperite contract")

    for path, expected_duration in ANNOUNCEMENT_AUDIO.items():
        if not path.exists():
            failures.append(
                f"missing announcement audio: {path.name}"
            )
            continue
        with wave.open(str(path), "rb") as audio:
            if audio.getframerate() != 48_000:
                failures.append(
                    f"{path.name} rate is "
                    f"{audio.getframerate()}, expected 48000"
                )
            if audio.getnchannels() != 2:
                failures.append(
                    f"{path.name} has "
                    f"{audio.getnchannels()} channels, expected 2"
                )
            if audio.getsampwidth() != 2:
                failures.append(
                    f"{path.name} sample width is "
                    f"{audio.getsampwidth()}, expected 2"
                )
            duration = audio.getnframes() / audio.getframerate()
            if abs(duration - expected_duration) > 0.025:
                failures.append(
                    f"{path.name} duration is "
                    f"{duration:.3f}, expected "
                    f"{expected_duration:.3f}"
                )

    if not BOSS_MUSIC.exists():
        failures.append("missing dedicated Seam Hunter boss score")
    elif not 2_500_000 <= BOSS_MUSIC.stat().st_size <= 3_500_000:
        failures.append(
            "boss score runtime size is "
            f"{BOSS_MUSIC.stat().st_size} bytes, expected "
            "a 2.5–3.5 MB AAC asset"
        )

    if not BOSS_MUSIC_SOURCE.exists():
        failures.append("missing preserved Seam Hunter boss-score master")
    else:
        with wave.open(str(BOSS_MUSIC_SOURCE), "rb") as audio:
            if audio.getframerate() != 48_000:
                failures.append(
                    "boss score rate is "
                    f"{audio.getframerate()}, expected 48000"
                )
            if audio.getnchannels() != 2:
                failures.append(
                    "boss score has "
                    f"{audio.getnchannels()} channels, expected 2"
                )
            if audio.getsampwidth() != 2:
                failures.append(
                    "boss score sample width is "
                    f"{audio.getsampwidth()}, expected 2"
                )
            duration = audio.getnframes() / audio.getframerate()
            if abs(duration - BOSS_MUSIC_DURATION) > 0.025:
                failures.append(
                    "boss score duration is "
                    f"{duration:.3f}, expected "
                    f"{BOSS_MUSIC_DURATION:.3f}"
                )

    for path, expected_size in LIFT_ASSETS.items():
        if not path.exists():
            failures.append(
                f"missing construction-lift asset: {path.name}"
            )
            continue
        with Image.open(path) as image:
            if image.size != expected_size:
                failures.append(
                    f"{path.name} size is {image.size}, "
                    f"expected {expected_size}"
                )

    for label, snippet in REQUIRED_SNIPPETS.items():
        if snippet not in html:
            failures.append(f"missing {label}: {snippet}")

    for label, snippet in FORBIDDEN_SNIPPETS.items():
        if snippet in html:
            failures.append(f"obsolete {label} remains: {snippet}")

    platform_count = html.count("woundBossRoute: true")
    if platform_count != 3:
        failures.append(
            "expected exactly 3 Wound construction platforms, "
            f"found {platform_count}"
        )

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("PASS: The Wound boss trial is wired")
    print("- isolated ?preview=wound-boss route")
    print("- Aryn enters with the modular PACK chassis")
    print("- Seam Hunter starts at 200 HP (136 with mobile assist)")
    print("- each quarter-health threshold changes color and aggression")
    print("- 448 px walk and 560 × 448 px sweep renders")
    print("- 2,580 px room with a 1,420 px clear combat runway")
    print("- split background textures stay within the 2,048 px ceiling")
    print("- three-platform construction rig and grounded art baseline")
    print("- exact modular construction-lift artwork and surface anchors")
    print("- the full boss body accepts modular PACK damage")
    print("- 15% faster construction lifts with a top-parked entrance gate")
    print("- laser cadence accelerates from 4.4 to 2.73 seconds")
    print("- one-time opening laser reaches its active frame after 1.25 seconds")
    print("- laser damage is limited to visible frames 15–30")
    print("- four-stage speed, recovery, range, and pursuit escalation")
    print("- confirmed, braked turns with short post-turn commitment")
    print("- lift-height perception break, bounded confusion, and blind search")
    print("- stable direction-aware search reversals at both lift boundaries")
    print("- curated non-damaging upward watch on the horizontal gantry")
    print("- delayed, deadzone-protected tracking while Aryn remains above")
    print("- authored in-place turnaround for confirmed gantry tracking")
    print("- lift confusion cannot consume the later gantry watch")
    print("- shaft retreat, guard, and downward-laser sentry loop")
    print("- lower dual framing while Aryn rides the high gantry")
    print("- locked downward laser telegraph, render, and diagonal hit test")
    print("- 12-frame cosmetic laser ground-impact animation")
    print("- 25-frame death collapse with delayed victory")
    print("- grounded final corpse pose and open-passage telemetry")
    print("- held corpse, near-black fade, and complete disappearance")
    print("- corpse-centered aftermath and responsive reward dual framing")
    print("- unique Wound-touched Vesperite at Seam Hunter's resting place")
    print("- post-victory remains reveal and explicit recovery")
    print("- shared keyboard/mobile Down interaction with proximity prompt")
    print("- stored future pack-upgrade material with no immediate ability")
    print("- frozen post-battle timer until the specimen is secured")
    print("- 6.35-second threshold-triggered boss announcement")
    print("- empty room, title-only darkness, then isolated boss reveal")
    print("- supplied transparent title and four authored audio cues")
    print("- concealed pre-announcement boss and health-bar reveal")
    print("- dedicated 120-second Seam Hunter combat score")
    print("- louder boss music handoff on reveal and explicit skip")
    print("- explicit Enter, Start, and mobile-safe Skip controls")
    print("- combatants lock while the entrance lift stays parked through the announcement")
    print("- mission clock held exactly for the full announcement")
    print("- shared production/preview sweep damage and victory flow")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
