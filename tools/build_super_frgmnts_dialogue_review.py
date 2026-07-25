#!/usr/bin/env python3
"""Build Revision 3C dialogue-system approval images and contracts.

This is a design-only builder. It does not modify the live game.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OVERWORLD = ROOT / "Design/Super-Frgmnts/Overworld"
DIALOGUE_DIR = OVERWORLD / "Phase-3/Dialogue"
REVIEW_DIR = DIALOGUE_DIR / "Reviews"
DRAS_MASTER = (
    OVERWORLD / "Phase-3/Dras/Assets/dras-transparent-master-v1.png"
)
DRAS_RUNTIME = (
    OVERWORLD / "Phase-3/Dras/Assets/dras-runtime-candidate-v1.png"
)
ARYN_SPRITE = ROOT / "Images/Builder/signal-ranger-idle-focused-v2.png"
OUTPOST_PLATE = (
    OVERWORLD / "Production/Plates/overworld-dras-outpost-v1.png"
)

FONT_PATH = "/System/Library/Fonts/SFNSMono.ttf"
FONT_BOLD_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
GROUND_Y = 744
DRAS_X = 280

COLORS = {
    "void": (5, 6, 12, 255),
    "panel": (7, 12, 28, 246),
    "panel_deep": (3, 6, 18, 250),
    "panel_warm": (23, 17, 29, 248),
    "ink": (238, 238, 238, 255),
    "soft": (160, 190, 245, 255),
    "brand_blue": (99, 149, 238, 255),
    "light_blue": (160, 190, 245, 255),
    "teal": (145, 175, 179, 255),
    "navy": (27, 54, 93, 255),
    "logo_teal": (61, 82, 85, 255),
    "gold": (217, 192, 140, 255),
    "amethyst": (155, 89, 182, 255),
    "rose": (224, 191, 184, 255),
    "pink": (255, 105, 180, 255),
    "green": (75, 227, 110, 255),
}

WORKING_CARDS = (
    {
        "speaker": "DRAS EHDRE",
        "text": (
            "Aryn Sol-Mavi. I wondered whether anyone beyond this dust "
            "still remembered us."
        ),
    },
    {
        "speaker": "DRAS EHDRE",
        "text": (
            "The Coreworks drew Vesperite for half the system. Then the "
            "infestation came up through the shafts."
        ),
    },
    {
        "speaker": "DRAS EHDRE",
        "text": (
            "Shipments stopped. Credits stopped. The air failed. Everyone "
            "who could leave, did."
        ),
    },
    {
        "speaker": "DRAS EHDRE",
        "text": (
            "We thought the infestation was the disaster. I am no longer "
            "certain. Something below the drills is awake."
        ),
    },
    {
        "speaker": "DRAS EHDRE",
        "text": (
            "Clear the infestation. Restore the atmosphere. Recover the "
            "stranded credits—and workers may come home."
        ),
    },
    {
        "speaker": "DRAS EHDRE",
        "text": (
            "The Foundry gate is ahead. Once you cross it, the planet "
            "starts counting on you."
        ),
    },
)


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD_PATH if bold else FONT_PATH, size)


def label(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    *,
    size: int,
    fill: tuple[int, int, int, int] = COLORS["ink"],
    bold: bool = False,
) -> None:
    draw.text(xy, text, font=font(size, bold=bold), fill=fill)


def wrap_text(text: str, characters: int) -> str:
    return "\n".join(
        textwrap.wrap(
            text,
            width=characters,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )


def build_scene() -> Image.Image:
    scene = Image.open(OUTPOST_PLATE).convert("RGBA")
    dras = Image.open(DRAS_RUNTIME).convert("RGBA")
    aryn = Image.open(ARYN_SPRITE).convert("RGBA")
    place_actor(scene, aryn, 74)
    place_actor(scene, dras, DRAS_X)
    return scene


def place_actor(scene: Image.Image, actor: Image.Image, x: int) -> None:
    shadow = Image.new("RGBA", (72, 12), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.ellipse((0, 2, 71, 11), fill=(2, 2, 12, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(0.6))
    scene.alpha_composite(
        shadow,
        (x + actor.width // 2 - 36, GROUND_Y - 7),
    )
    scene.alpha_composite(actor, (x, GROUND_Y - actor.height))


def portrait_asset(size: tuple[int, int]) -> Image.Image:
    master = Image.open(DRAS_MASTER).convert("RGBA")
    # Face, scarf, staff lamp, and cyan badge—all identity-bearing cues.
    crop = master.crop(
        (
            round(master.width * 0.12),
            0,
            round(master.width * 0.95),
            round(master.height * 0.47),
        )
    )
    crop.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    canvas.alpha_composite(
        crop,
        ((size[0] - crop.width) // 2, size[1] - crop.height),
    )
    return canvas


def dim_scene(scene: Image.Image, alpha: int = 32) -> Image.Image:
    output = scene.copy()
    veil = Image.new("RGBA", output.size, (2, 3, 12, alpha))
    return Image.alpha_composite(output, veil)


def settle_dialogue_camera(scene: Image.Image, shift_y: int) -> Image.Image:
    """Lift actors into the dialogue-safe band without changing world geometry."""
    output = Image.new("RGBA", scene.size, COLORS["void"])
    output.alpha_composite(scene, (0, shift_y))
    return output


def draw_corner_brackets(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    color: tuple[int, int, int, int],
    length: int = 28,
    width: int = 3,
) -> None:
    left, top, right, bottom = box
    segments = (
        (left, top + length, left, top, left + length, top),
        (right - length, top, right, top, right, top + length),
        (left, bottom - length, left, bottom, left + length, bottom),
        (right - length, bottom, right, bottom, right, bottom - length),
    )
    for x1, y1, x2, y2, x3, y3 in segments:
        draw.line((x1, y1, x2, y2, x3, y3), fill=color, width=width)


def draw_field_relay(
    scene: Image.Image,
    *,
    mobile: bool = False,
) -> Image.Image:
    if not mobile:
        output = dim_scene(scene, 24)
        overlay = Image.new("RGBA", output.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        panel = (64, 626, 1608, 896)
        draw.rounded_rectangle(
            panel,
            radius=14,
            fill=COLORS["panel"],
            outline=COLORS["teal"],
            width=3,
        )
        draw_corner_brackets(draw, panel, COLORS["pink"], 24, 3)
        draw.rectangle((88, 648, 270, 866), fill=(4, 8, 22, 255))
        draw.rounded_rectangle(
            (98, 658, 260, 820),
            radius=6,
            fill=(16, 20, 34, 255),
            outline=COLORS["gold"],
            width=2,
        )
        overlay.alpha_composite(portrait_asset((150, 150)), (104, 666))
        label(draw, (106, 830), "FIELD RELAY 07", size=14, fill=COLORS["soft"])

        label(
            draw,
            (302, 650),
            "COREWORKS FIELD RELAY // LOCAL CHANNEL",
            size=14,
            fill=COLORS["teal"],
        )
        label(
            draw,
            (302, 682),
            "DRAS EHDRE",
            size=24,
            fill=COLORS["gold"],
            bold=True,
        )
        draw.line((302, 718, 1490, 718), fill=COLORS["logo_teal"], width=2)
        body = wrap_text(WORKING_CARDS[0]["text"], 72)
        draw.multiline_text(
            (302, 744),
            body,
            font=font(22),
            fill=COLORS["ink"],
            spacing=10,
        )
        label(draw, (302, 850), "01 / 06", size=14, fill=COLORS["soft"])
        label(draw, (1188, 850), "ESC  SKIP", size=13, fill=COLORS["soft"])
        draw.rounded_rectangle(
            (1322, 824, 1568, 872),
            radius=5,
            fill=(99, 149, 238, 30),
            outline=COLORS["light_blue"],
            width=2,
        )
        label(
            draw,
            (1361, 837),
            "CONTINUE  ›",
            size=17,
            fill=COLORS["ink"],
            bold=True,
        )
        draw.rectangle((88, 872, 880, 878), fill=COLORS["navy"])
        draw.rectangle((88, 872, 220, 878), fill=COLORS["pink"])
        output = Image.alpha_composite(output, overlay)
        return output

    # Portrait mobile: panel occupies the lower third after touch controls hide.
    output = dim_scene(scene, 26)
    overlay = Image.new("RGBA", output.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    panel = (14, 566, output.width - 14, output.height - 18)
    draw.rounded_rectangle(
        panel,
        radius=18,
        fill=COLORS["panel"],
        outline=COLORS["teal"],
        width=3,
    )
    draw_corner_brackets(draw, panel, COLORS["pink"], 18, 2)
    draw.rounded_rectangle(
        (32, 574, 120, 662),
        radius=5,
        fill=(15, 19, 33, 255),
        outline=COLORS["gold"],
        width=2,
    )
    overlay.alpha_composite(portrait_asset((82, 82)), (35, 578))
    label(draw, (136, 578), "DRAS EHDRE", size=18, fill=COLORS["gold"], bold=True)
    label(draw, (136, 606), "FIELD RELAY 07", size=11, fill=COLORS["teal"])
    body = wrap_text(WORKING_CARDS[0]["text"], 35)
    draw.multiline_text(
        (32, 686),
        body,
        font=font(16),
        fill=COLORS["ink"],
        spacing=9,
    )
    label(draw, (32, 816), "01 / 06", size=12, fill=COLORS["soft"])
    draw.rounded_rectangle(
        (236, 802, 394, 858),
        radius=7,
        fill=(99, 149, 238, 34),
        outline=COLORS["light_blue"],
        width=2,
    )
    label(draw, (258, 820), "CONTINUE ›", size=14, bold=True)
    draw.rectangle((32, 874, 398, 879), fill=COLORS["navy"])
    draw.rectangle((32, 874, 93, 879), fill=COLORS["pink"])
    return Image.alpha_composite(output, overlay)


def draw_coreworks_archive(
    scene: Image.Image,
    *,
    mobile: bool = False,
) -> Image.Image:
    if not mobile:
        output = dim_scene(scene, 38)
        overlay = Image.new("RGBA", output.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        panel = (0, 650, 1672, 921)
        draw.rectangle(panel, fill=COLORS["panel_warm"])
        draw.rectangle((0, 650, 1672, 658), fill=COLORS["amethyst"])
        draw.rectangle((0, 658, 1672, 664), fill=COLORS["gold"])
        draw.rectangle((36, 682, 286, 724), fill=COLORS["navy"])
        label(
            draw,
            (52, 692),
            "ARCHIVE // WITNESS",
            size=15,
            fill=COLORS["light_blue"],
            bold=True,
        )
        label(draw, (324, 680), "DRAS EHDRE", size=23, fill=COLORS["rose"], bold=True)
        label(
            draw,
            (324, 716),
            "COREWORKS OUTPOST • RECORDED LOCALLY",
            size=13,
            fill=COLORS["soft"],
        )
        draw.line((324, 748, 1608, 748), fill=COLORS["plum"] if "plum" in COLORS else COLORS["amethyst"], width=2)
        body = wrap_text(WORKING_CARDS[0]["text"], 84)
        draw.multiline_text(
            (324, 776),
            body,
            font=font(22),
            fill=COLORS["ink"],
            spacing=9,
        )
        label(draw, (44, 866), "LOG 01 / 06", size=14, fill=COLORS["soft"])
        label(draw, (1138, 866), "ENTER  ADVANCE", size=14, fill=COLORS["gold"])
        label(draw, (1422, 866), "ESC  EXIT", size=14, fill=COLORS["soft"])
        for x in range(42, 278, 16):
            height = 7 + (x // 16) % 3 * 5
            draw.rectangle((x, 756, x + 8, 756 + height), fill=COLORS["amethyst"])
        return Image.alpha_composite(output, overlay)

    output = dim_scene(scene, 40)
    overlay = Image.new("RGBA", output.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    panel = (0, 578, output.width, output.height)
    draw.rectangle(panel, fill=COLORS["panel_warm"])
    draw.rectangle((0, 578, output.width, 586), fill=COLORS["amethyst"])
    draw.rectangle((0, 586, output.width, 591), fill=COLORS["gold"])
    draw.rectangle((18, 610, 204, 646), fill=COLORS["navy"])
    label(draw, (30, 619), "ARCHIVE // WITNESS", size=12, fill=COLORS["light_blue"], bold=True)
    label(draw, (18, 670), "DRAS EHDRE", size=19, fill=COLORS["rose"], bold=True)
    label(draw, (18, 702), "COREWORKS OUTPOST", size=11, fill=COLORS["soft"])
    draw.line((18, 730, output.width - 18, 730), fill=COLORS["amethyst"], width=2)
    body = wrap_text(WORKING_CARDS[0]["text"], 36)
    draw.multiline_text(
        (18, 750),
        body,
        font=font(15),
        fill=COLORS["ink"],
        spacing=8,
    )
    label(draw, (18, 876), "LOG 01 / 06", size=11, fill=COLORS["soft"])
    label(draw, (269, 876), "TAP TO ADVANCE", size=11, fill=COLORS["gold"])
    return Image.alpha_composite(output, overlay)


def desktop_direction(
    direction: str,
) -> Path:
    scene = settle_dialogue_camera(build_scene(), -132)
    if direction == "field-relay":
        output = draw_field_relay(scene)
        path = REVIEW_DIR / "dialogue-field-relay-desktop-v1.png"
    else:
        output = draw_coreworks_archive(scene)
        path = REVIEW_DIR / "dialogue-coreworks-archive-desktop-v1.png"
    output.convert("RGB").save(path)
    return path


def mobile_scene() -> Image.Image:
    full = settle_dialogue_camera(build_scene(), -150)
    crop = full.crop((0, 0, 540, 941))
    return crop.resize((430, 749), Image.Resampling.LANCZOS)


def mobile_direction(direction: str) -> Path:
    phone_scene = Image.new("RGBA", (430, 932), COLORS["void"])
    world = mobile_scene()
    phone_scene.alpha_composite(world, (0, 92))
    draw = ImageDraw.Draw(phone_scene)
    draw.rectangle((0, 0, 430, 92), fill=COLORS["panel_deep"])
    label(draw, (18, 28), "SUPER FRGMNTS // PAUSED", size=15, bold=True)
    draw.line((18, 68, 412, 68), fill=COLORS["pink"], width=1)

    if direction == "field-relay":
        output = draw_field_relay(phone_scene, mobile=True)
        path = REVIEW_DIR / "dialogue-field-relay-mobile-v1.png"
    else:
        output = draw_coreworks_archive(phone_scene, mobile=True)
        path = REVIEW_DIR / "dialogue-coreworks-archive-mobile-v1.png"
    output.convert("RGB").save(path)
    return path


def build_comparison(paths: dict[str, Path]) -> Path:
    output = REVIEW_DIR / "dialogue-directions-comparison-v1.png"
    canvas = Image.new("RGBA", (1900, 1460), COLORS["void"])
    draw = ImageDraw.Draw(canvas)
    label(draw, (48, 28), "REVISION 3C // DIALOGUE VISUAL SYSTEM", size=34, bold=True)
    label(
        draw,
        (50, 76),
        "Two production-minded directions • same scene • same working copy",
        size=18,
        fill=COLORS["soft"],
    )

    directions = (
        (
            "FIELD RELAY",
            "Recommended",
            paths["field_desktop"],
            paths["field_mobile"],
            COLORS["teal"],
            (
                "Human, intimate, and palette-rich.",
                "Portrait gives Dras immediate emotional presence.",
                "Best fit for first contact and later character scenes.",
            ),
        ),
        (
            "COREWORKS ARCHIVE",
            "Alternate",
            paths["archive_desktop"],
            paths["archive_mobile"],
            COLORS["amethyst"],
            (
                "Institutional, austere, and lore-forward.",
                "Excellent for terminals, recordings, and system alerts.",
                "Less warmth for Dras's first appearance.",
            ),
        ),
    )
    for index, (name, status, desktop_path, mobile_path, accent, notes) in enumerate(directions):
        left = 48 + index * 926
        top = 126
        draw.rounded_rectangle(
            (left, top, left + 878, 1402),
            radius=14,
            fill=COLORS["panel_deep"],
            outline=accent,
            width=3,
        )
        label(draw, (left + 24, top + 22), name, size=25, fill=accent, bold=True)
        label(
            draw,
            (left + 24, top + 62),
            status.upper(),
            size=14,
            fill=COLORS["gold"] if index == 0 else COLORS["soft"],
            bold=True,
        )
        desktop = Image.open(desktop_path).convert("RGBA").resize(
            (830, 467), Image.Resampling.LANCZOS
        )
        canvas.alpha_composite(desktop, (left + 24, top + 104))
        mobile = Image.open(mobile_path).convert("RGBA").resize(
            (230, 498), Image.Resampling.LANCZOS
        )
        canvas.alpha_composite(mobile, (left + 24, top + 596))

        label(draw, (left + 290, top + 622), "WHY IT WORKS", size=18, fill=accent, bold=True)
        for note_index, note in enumerate(notes):
            wrapped = wrap_text(note, 38)
            draw.multiline_text(
                (left + 290, top + 668 + note_index * 88),
                f"• {wrapped}",
                font=font(15),
                fill=COLORS["ink"],
                spacing=5,
            )

        label(
            draw,
            (left + 290, top + 956),
            "SHARED CONTRACT",
            size=17,
            fill=COLORS["light_blue"],
            bold=True,
        )
        shared = (
            "Gameplay paused; controls hidden",
            "Continue is a real 44px+ target",
            "Full text exposed to assistive tech",
            "Reduced motion reveals text instantly",
        )
        for item_index, item in enumerate(shared):
            label(
                draw,
                (left + 290, top + 992 + item_index * 34),
                f"• {item}",
                size=13,
                fill=COLORS["soft"],
            )
    canvas.convert("RGB").save(output)
    return output


def write_working_copy() -> Path:
    output = DIALOGUE_DIR / "WORKING-COPY.md"
    lines = [
        "# Dras Ehdre first-contact dialogue",
        "",
        "> Status: working copy for Revision 3C visual and pacing review. "
        "Nothing here is permanent canon.",
        "",
    ]
    for index, card in enumerate(WORKING_CARDS, start=1):
        lines.extend(
            [
                f"## Card {index} of {len(WORKING_CARDS)}",
                "",
                f"**{card['speaker']}**",
                "",
                card["text"],
                "",
            ]
        )
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def write_contract() -> Path:
    output = DIALOGUE_DIR / "DIALOGUE-CONTRACT.md"
    output.write_text(
        """# SUPER FRGMNTS dialogue contract

Status: Revision 3C review candidate. Design-only; not integrated.

## Recommended visual direction

Use **Field Relay** for live character conversations. It makes Dras human before
he becomes a lore delivery system, gives the palette room to breathe, and
preserves the scene behind the panel. Reserve **Coreworks Archive** for abandoned
terminals, recovered logs, system warnings, and non-human transmissions.

## Interaction

- Opening dialogue pauses the simulation, timer, hostile motion, and actor input.
- Touch controls disappear while the dialogue is active.
- Keyboard: Enter or Space completes/advances; Escape opens a skip confirmation.
- Touch: first tap completes a visual text reveal; the next tap advances.
- Continue is always visible and at least 44 by 44 CSS pixels.
- Skip is available but visually secondary. Closing restores focus to gameplay.

## Text volume

- One thought per card.
- Prefer 38–44 visible characters per desktop line and 28–35 on mobile.
- Prefer 2–3 short visual lines; never exceed 5 mobile lines.
- Avoid orphaned one-word lines and text over scenic faces.

## Accessibility

- Use a labelled `role="dialog"` container while gameplay is paused.
- Put the full card text in the accessibility tree when the card opens; never
  announce typewriter characters one by one.
- Move focus to Continue and keep keyboard focus inside the dialogue.
- Speaker identity must be text, not portrait or color alone.
- Reduced motion reveals the complete card immediately and disables portrait,
  border, waveform, and indicator animation.
- High-contrast mode strengthens the panel fill and uses a 3px light border.
- Meaning never depends on amber, pink, cyan, or animated light alone.

## Presentation

- Field Relay uses `palette.html`: Brand Teal for structure, Brand Gold for the
  speaker, Brand Light Blue for actions, Brand Pink for progress, and Void Dark
  for the panel.
- The scene dims only enough to establish focus; actors remain visible.
- Dras's portrait is optional after first contact, but the nameplate is permanent.
- Dialogue animation and audio pause whenever the page loses visibility.
""",
        encoding="utf-8",
    )
    return output


def write_manifest(paths: dict[str, Path], comparison: Path) -> Path:
    output = DIALOGUE_DIR / "dialogue-revision-3c-manifest.json"
    manifest = {
        "revision": "3C",
        "status": "review-candidate-unapproved",
        "recommendation": {
            "character_dialogue": "field-relay",
            "terminal_and_system_dialogue": "coreworks-archive",
            "reason": (
                "Field Relay gives first contact warmth and presence; Coreworks "
                "Archive remains a useful secondary grammar for machines."
            ),
        },
        "working_copy_cards": len(WORKING_CARDS),
        "reviews": {key: str(value) for key, value in paths.items()},
        "comparison": str(comparison),
        "scope": {
            "live_game_modified": False,
            "integrated": False,
            "committed": False,
            "copy_is_canon": False,
        },
    }
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return output


def main() -> None:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    paths = {
        "field_desktop": desktop_direction("field-relay"),
        "field_mobile": mobile_direction("field-relay"),
        "archive_desktop": desktop_direction("archive"),
        "archive_mobile": mobile_direction("archive"),
    }
    comparison = build_comparison(paths)
    outputs = [
        *paths.values(),
        comparison,
        write_working_copy(),
        write_contract(),
        write_manifest(paths, comparison),
    ]
    for output in outputs:
        print(output)


if __name__ == "__main__":
    main()
