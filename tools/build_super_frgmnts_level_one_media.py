#!/usr/bin/env python3
"""Build the authentic Super Frgmnts media package for the Level One essay.

The compositions use only shipped game art, creator screenshots, and frames
captured from the live browser build. The primary article format is animated
WebP; compact GIFs, mobile WebPs, and poster frames are exported alongside it.
"""

from __future__ import annotations

import argparse
import math
import textwrap
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
GAME_ART = ROOT / "Images" / "Game" / "Super-Frgmnts"
OUTPUT = ROOT / "media" / "narrative" / "2026-08-03-level-one"
MOBILE_OUTPUT = OUTPUT / "mobile"
GIF_OUTPUT = OUTPUT / "gifs"
POSTER_OUTPUT = OUTPUT / "posters"

DESKTOP_SIZE = (960, 540)
MOBILE_SIZE = (640, 360)
GIF_SIZE = (560, 315)
SHEET_SIZE = (1400, 900)

CAPTURE_CROP = (124, 65, 1156, 648)
ARRIVAL_CROP = (180, 132, 1100, 586)

FONT_REGULAR = Path("/System/Library/Fonts/SFNSMono.ttf")
FONT_BOLD = Path("/System/Library/Fonts/SFNSMono.ttf")

COLORS = {
    "ink": (3, 6, 18),
    "panel": (7, 12, 29),
    "paper": (246, 244, 239),
    "muted": (154, 181, 200),
    "cyan": (88, 245, 223),
    "blue": (107, 154, 255),
    "pink": (255, 105, 180),
    "amber": (255, 195, 94),
    "red": (255, 82, 104),
    "green": (75, 227, 110),
}


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size)


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    image = image.convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize(
        (math.ceil(image.width * scale), math.ceil(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = max(0, (resized.width - size[0]) // 2)
    top = max(0, (resized.height - size[1]) // 2)
    return resized.crop((left, top, left + size[0], top + size[1]))


def crop_capture(path: Path, crop: tuple[int, int, int, int]) -> Image.Image:
    return cover(Image.open(path).convert("RGB").crop(crop), DESKTOP_SIZE)


def wrap_for_width(
    draw: ImageDraw.ImageDraw,
    value: str,
    text_font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    words = value.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if not current or draw.textlength(candidate, font=text_font) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_tracking_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    text_font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    tracking: int = 2,
) -> None:
    x, y = xy
    for character in value:
        draw.text((x, y), character, font=text_font, fill=fill)
        x += int(draw.textlength(character, font=text_font)) + tracking


def resize_frames(
    frames: Sequence[Image.Image], size: tuple[int, int]
) -> list[Image.Image]:
    return [frame.resize(size, Image.Resampling.LANCZOS) for frame in frames]


def save_animation(
    stem: str,
    frames: Sequence[Image.Image],
    *,
    duration_ms: int,
    poster_index: int | None = None,
) -> None:
    if not frames:
        raise ValueError(f"{stem}: no frames supplied")
    desktop = [frame.convert("RGB") for frame in frames]
    poster_position = poster_index if poster_index is not None else len(desktop) // 2
    poster = desktop[max(0, min(len(desktop) - 1, poster_position))]
    poster.save(POSTER_OUTPUT / f"{stem}.jpg", quality=88, optimize=True)

    desktop[0].save(
        OUTPUT / f"{stem}.webp",
        save_all=True,
        append_images=desktop[1:],
        duration=duration_ms,
        loop=0,
        quality=70,
        method=6,
        minimize_size=True,
    )

    mobile = resize_frames(desktop, MOBILE_SIZE)
    mobile[0].save(
        MOBILE_OUTPUT / f"{stem}.webp",
        save_all=True,
        append_images=mobile[1:],
        duration=duration_ms,
        loop=0,
        quality=66,
        method=6,
        minimize_size=True,
    )

    gif_source = resize_frames(desktop[::2] or desktop, GIF_SIZE)
    gif_frames = [
        frame.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        for frame in gif_source
    ]
    gif_frames[0].save(
        GIF_OUTPUT / f"{stem}.gif",
        save_all=True,
        append_images=gif_frames[1:],
        duration=duration_ms * 2,
        loop=0,
        optimize=True,
        disposal=2,
    )


def sheet_frames(name: str, frame_width: int = 112) -> list[Image.Image]:
    sheet = Image.open(GAME_ART / name).convert("RGBA")
    return [
        sheet.crop((x, 0, x + frame_width, sheet.height))
        for x in range(0, sheet.width, frame_width)
    ]


def build_aryn_sheet() -> None:
    canvas = Image.new("RGB", SHEET_SIZE, COLORS["ink"])
    draw = ImageDraw.Draw(canvas)

    for x in range(0, SHEET_SIZE[0], 28):
        draw.line((x, 0, x, SHEET_SIZE[1]), fill=(10, 18, 39), width=1)
    for y in range(0, SHEET_SIZE[1], 28):
        draw.line((0, y, SHEET_SIZE[0], y), fill=(10, 18, 39), width=1)

    draw.rectangle((0, 0, SHEET_SIZE[0], 112), fill=(4, 9, 24))
    draw.rectangle((0, 108, SHEET_SIZE[0], 112), fill=COLORS["pink"])
    draw_tracking_text(
        draw,
        (54, 24),
        "ARYN SOL-MAVI // RUNTIME MOTION STUDY",
        font(26, bold=True),
        COLORS["paper"],
        tracking=2,
    )
    draw.text(
        (56, 66),
        "THE FINISHED 112 × 112 WORLD-SPACE ANIMATION CELLS",
        font=font(17),
        fill=COLORS["muted"],
    )

    rows = [
        (
            "RUN",
            "8 CELLS // 12 FPS",
            sheet_frames("aryn-run-ludo-runtime-v2.png"),
            COLORS["cyan"],
        ),
        (
            "JUMP",
            "7 CELLS // VARIABLE HEIGHT",
            sheet_frames("aryn-jump-ludo-runtime-v1.png"),
            COLORS["blue"],
        ),
        (
            "PACK FIRE",
            "6 OF 12 CELLS // ANTENNA ORIGIN",
            sheet_frames("aryn-rifle-fire-ludo-runtime-v1.png")[::2],
            COLORS["amber"],
        ),
        (
            "COLLAPSE",
            "6 OF 12 CELLS // EXTRACTION",
            sheet_frames("aryn-death-ludo-runtime-v1.png")[::2],
            COLORS["pink"],
        ),
    ]

    row_y = [145, 330, 515, 700]
    cell_size = 120
    cell_gap = 8
    sprite_scale = 1.0
    for (label, note, frames, accent), y in zip(rows, row_y):
        draw.rectangle((38, y, 314, y + 148), fill=(6, 13, 31), outline=accent, width=2)
        draw.text((60, y + 29), label, font=font(24, bold=True), fill=accent)
        note_lines = textwrap.wrap(note, width=23)
        for line_index, line in enumerate(note_lines):
            draw.text(
                (60, y + 72 + line_index * 21),
                line,
                font=font(14),
                fill=COLORS["muted"],
            )

        for frame_index, sprite in enumerate(frames):
            x = 340 + frame_index * (cell_size + cell_gap)
            draw.rectangle(
                (x, y, x + cell_size, y + cell_size),
                fill=(8, 16, 36),
                outline=(31, 52, 84),
                width=1,
            )
            scaled_size = round(112 * sprite_scale)
            enlarged = sprite.resize((scaled_size, scaled_size), Image.Resampling.NEAREST)
            canvas.paste(
                enlarged,
                (x + (cell_size - scaled_size) // 2, y + (cell_size - scaled_size) // 2),
                enlarged,
            )
            draw.text(
                (x + 7, y + cell_size + 5),
                f"{frame_index + 1:02d}",
                font=font(12),
                fill=COLORS["muted"],
            )

    rest = Image.open(GAME_ART / "aryn-command-rest-runtime-v1.png").convert("RGBA")
    rest = rest.resize((138, 138), Image.Resampling.NEAREST)
    canvas.paste(rest, (1236, 8), rest)
    draw.text((1114, 78), "COMMAND REST", font=font(13), fill=COLORS["cyan"])

    canvas.save(
        OUTPUT / "super-frgmnts-aryn-runtime-motion-study-v1.png",
        optimize=True,
    )
    canvas.resize((1000, 643), Image.Resampling.LANCZOS).save(
        MOBILE_OUTPUT / "super-frgmnts-aryn-runtime-motion-study-v1.png",
        optimize=True,
    )


def tinted_membrane(color: tuple[int, int, int], size: tuple[int, int]) -> Image.Image:
    source = Image.open(
        GAME_ART / "foundry-atmosphere-lock-membrane-runtime-v1.png"
    ).convert("RGBA")
    source = source.resize(size, Image.Resampling.NEAREST)
    alpha = source.getchannel("A")
    luminance = ImageOps.grayscale(source)
    tinted = ImageOps.colorize(luminance, black=(12, 8, 22), white=color).convert("RGBA")
    tinted.putalpha(alpha)
    return tinted


def draw_door_pair(
    base: Image.Image,
    *,
    center_x: int,
    top_y: int,
    color: tuple[int, int, int],
    pulse: float,
) -> None:
    face_size = (136, 350)
    membrane = tinted_membrane(color, face_size)
    housing = Image.open(
        GAME_ART / "foundry-atmosphere-lock-housing-runtime-v1.png"
    ).convert("RGBA").resize(face_size, Image.Resampling.NEAREST)
    for mirrored, x in ((False, center_x - face_size[0]), (True, center_x)):
        membrane_face = ImageOps.mirror(membrane) if mirrored else membrane
        housing_face = ImageOps.mirror(housing) if mirrored else housing
        glow_alpha = membrane_face.getchannel("A").filter(
            ImageFilter.GaussianBlur(radius=18 + pulse * 4)
        )
        glow = Image.new("RGBA", face_size, color + (0,))
        glow.putalpha(glow_alpha.point(lambda value: int(value * (0.36 + pulse * 0.08))))
        base.alpha_composite(glow, (x, top_y))
        base.alpha_composite(membrane_face, (x, top_y))
        base.alpha_composite(housing_face, (x, top_y))


def build_bubble_door_loop(source_screenshot: Path) -> None:
    background = cover(Image.open(source_screenshot).convert("RGB"), DESKTOP_SIZE).convert("RGBA")
    veil = Image.new("RGBA", DESKTOP_SIZE, (2, 5, 15, 44))
    background.alpha_composite(veil)

    positions = [72, 178, 119, 211]
    colors = [COLORS["red"], COLORS["pink"], COLORS["red"], COLORS["green"]]
    labels = ["REVISION A", "REVISION B", "REVISION C", "FINALLY ANCHORED"]
    keyframes: list[Image.Image] = []
    for state_index, (position, color, label) in enumerate(zip(positions, colors, labels)):
        frame = background.copy()
        draw_door_pair(
            frame,
            center_x=570,
            top_y=position,
            color=color,
            pulse=0.35 + state_index * 0.16,
        )
        draw = ImageDraw.Draw(frame)
        draw.rounded_rectangle((34, 28, 596, 118), radius=8, fill=(4, 8, 23, 226), outline=color, width=2)
        draw_tracking_text(
            draw,
            (56, 43),
            "THE BUBBLE DOOR MOVED AGAIN",
            font(21, bold=True),
            COLORS["paper"],
            tracking=1,
        )
        draw.text((57, 81), label, font=font(16), fill=color)
        draw.text(
            (815, 495),
            f"LOCK Y // {position:03d}",
            font=font(14),
            fill=COLORS["muted"],
        )
        keyframes.append(frame.convert("RGB"))

    frames: list[Image.Image] = []
    for index, current in enumerate(keyframes):
        next_frame = keyframes[(index + 1) % len(keyframes)]
        frames.extend([current] * 7)
        frames.extend(Image.blend(current, next_frame, step / 5) for step in range(1, 5))
    save_animation(
        "super-frgmnts-bubble-door-regression-v1",
        frames,
        duration_ms=125,
        poster_index=len(frames) - 8,
    )


def build_arrival_loop(capture_dir: Path) -> None:
    sources = sorted(capture_dir.glob("frame-*.png"))
    if len(sources) < 85:
        raise RuntimeError(
            f"RD-42 capture requires at least 85 frames; found {len(sources)} in {capture_dir}"
        )
    frames = [crop_capture(path, ARRIVAL_CROP) for path in sources[8:85:2]]
    last = frames[-1]
    first = frames[0]
    black = Image.new("RGB", DESKTOP_SIZE, COLORS["ink"])
    frames.extend(Image.blend(last, black, step / 5) for step in range(1, 6))
    frames.extend(Image.blend(black, first, step / 5) for step in range(1, 6))
    save_animation(
        "super-frgmnts-rd42-descent-v1",
        frames,
        duration_ms=180,
        poster_index=25,
    )


def dialogue_keyframe(
    *,
    speaker: str,
    role: str,
    text: str,
    portrait_name: str,
    accent: tuple[int, int, int],
) -> Image.Image:
    background = cover(
        Image.open(GAME_ART / "overworld-dras-outpost-v1.png"),
        DESKTOP_SIZE,
    ).convert("RGBA")
    darkness = Image.new("RGBA", DESKTOP_SIZE, (2, 4, 14, 116))
    background.alpha_composite(darkness)
    draw = ImageDraw.Draw(background)

    draw.rounded_rectangle(
        (30, 316, 930, 516),
        radius=10,
        fill=(4, 8, 22, 238),
        outline=accent,
        width=2,
    )
    draw.rectangle((30, 316, 38, 516), fill=accent)

    portrait = Image.open(GAME_ART / portrait_name).convert("RGBA")
    portrait = cover(portrait, (230, 230)).convert("RGBA")
    mask = Image.new("L", portrait.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((0, 0, 229, 229), radius=12, fill=255)
    portrait.putalpha(mask)
    background.alpha_composite(portrait, (54, 284))
    draw.rounded_rectangle((52, 282, 286, 516), radius=13, outline=accent, width=3)

    draw_tracking_text(
        draw,
        (320, 342),
        speaker,
        font(22, bold=True),
        accent,
        tracking=1,
    )
    draw.text((320, 375), role, font=font(14), fill=COLORS["muted"])

    text_font = font(25)
    lines = wrap_for_width(draw, text, text_font, 566)
    for line_index, line in enumerate(lines[:4]):
        draw.text(
            (320, 414 + line_index * 31),
            line,
            font=text_font,
            fill=COLORS["paper"],
        )

    draw.text(
        (38, 26),
        "VEYRA SURFACE // FIELD TRANSCRIPT",
        font=font(15),
        fill=COLORS["muted"],
    )
    return background.convert("RGB")


def build_dialogue_loop() -> None:
    dras = dialogue_keyframe(
        speaker="DRAS EHDRE",
        role="COREWORKS FOREMAN",
        text="There are entire crates of Galactic Credits below. Whatever you recover is yours.",
        portrait_name="dras-dialogue-portrait-runtime-v2.png",
        accent=COLORS["cyan"],
    )
    aryn = dialogue_keyframe(
        speaker="ARYN SOL-MAVI",
        role="SIGNAL RANGER",
        text="I won’t say no to honest money. Or a cold Diet Coke, if your emergency stores are feeling generous.",
        portrait_name="aryn-dialogue-portrait-runtime-v3.png",
        accent=COLORS["pink"],
    )
    black = Image.new("RGB", DESKTOP_SIZE, COLORS["ink"])
    frames: list[Image.Image] = [dras] * 18
    frames.extend(Image.blend(dras, black, step / 5) for step in range(1, 5))
    frames.extend(Image.blend(black, aryn, step / 5) for step in range(1, 5))
    frames.extend([aryn] * 23)
    frames.extend(Image.blend(aryn, black, step / 5) for step in range(1, 5))
    frames.extend(Image.blend(black, dras, step / 5) for step in range(1, 5))
    save_animation(
        "super-frgmnts-aryn-dras-dialogue-v1",
        frames,
        duration_ms=120,
        poster_index=30,
    )


def build_action_loop(capture_dir: Path) -> None:
    sources = sorted(capture_dir.glob("frame-*.png"))
    if len(sources) < 40:
        raise RuntimeError(
            f"Foundry action capture requires at least 40 frames; found {len(sources)} in {capture_dir}"
        )
    frames = [crop_capture(path, CAPTURE_CROP) for path in sources[:42:2]]
    save_animation(
        "super-frgmnts-foundry-action-v1",
        frames,
        duration_ms=180,
        poster_index=10,
    )


def build_landing_invitation() -> None:
    background = cover(
        Image.open(GAME_ART / "overworld-landing-flats-v1.png"),
        DESKTOP_SIZE,
    ).convert("RGBA")
    ship_source = Image.open(GAME_ART / "aryn-ship-v2.png").convert("RGBA")
    hover_source = Image.open(GAME_ART / "aryn-ship-hover-field-v1.png").convert("RGBA")
    aryn_source = Image.open(GAME_ART / "aryn-command-rest-runtime-v1.png").convert("RGBA")

    ship_width = 590
    ship_height = round(ship_width * ship_source.height / ship_source.width)
    ship = ship_source.resize((ship_width, ship_height), Image.Resampling.LANCZOS)
    hover = hover_source.resize((520, 29), Image.Resampling.LANCZOS)
    aryn = aryn_source.resize((82, 82), Image.Resampling.NEAREST)

    frames: list[Image.Image] = []
    frame_count = 32
    for index in range(frame_count):
        phase = index / frame_count * math.pi * 2
        frame = background.copy()
        bob = round(math.sin(phase) * 3)
        ship_x = (DESKTOP_SIZE[0] - ship_width) // 2
        ship_y = 248 + bob

        glow = hover.copy()
        glow.putalpha(int(132 + 52 * (0.5 + 0.5 * math.sin(phase * 2))))
        frame.alpha_composite(glow, ((DESKTOP_SIZE[0] - glow.width) // 2, ship_y + ship_height - 8))
        frame.alpha_composite(ship, (ship_x, ship_y))
        frame.alpha_composite(aryn, ((DESKTOP_SIZE[0] - aryn.width) // 2, ship_y - 33))

        veil = Image.new("RGBA", DESKTOP_SIZE, (2, 5, 15, 0))
        veil_draw = ImageDraw.Draw(veil)
        veil_draw.rectangle((0, 434, 960, 540), fill=(2, 5, 15, 190))
        frame.alpha_composite(veil)
        draw = ImageDraw.Draw(frame)
        draw_tracking_text(
            draw,
            (64, 455),
            "SUPER FRGMNTS // ARRIVAL ON VEYRA",
            font(17, bold=True),
            COLORS["muted"],
            tracking=1,
        )
        draw.text((64, 486), "PLAY LEVEL ONE  →", font=font(29, bold=True), fill=COLORS["paper"])
        draw.rectangle((64, 525, 410, 529), fill=COLORS["pink"])
        frames.append(frame.convert("RGB"))

    save_animation(
        "super-frgmnts-landing-invitation-v1",
        frames,
        duration_ms=125,
        poster_index=8,
    )


def write_manifest() -> None:
    manifest = """# Level One essay media

All visuals in this directory are composed from the released Super Frgmnts
game art or captured from the running browser build.

| Primary file | Essay placement | Suggested caption |
| --- | --- | --- |
| `super-frgmnts-aryn-runtime-motion-study-v1.png` | After “Spoiler: It went so, so poorly.” | One character. Dozens of cells. None of them knew about the others. |
| `super-frgmnts-bubble-door-regression-v1.webp` | After the paragraph about destabilizing connected systems | The bubble door moved again. It would not be the last time. |
| `super-frgmnts-rd42-descent-v1.webp` | After remembering the browser version on the commute | Returning to the version that worked. |
| `super-frgmnts-aryn-dras-dialogue-v1.webp` | After the world developed a personality | The writing stopped being filler and became the game. |
| `super-frgmnts-foundry-action-v1.webp` | After “It kind of kicks ass.” | Reader, it kind of kicks ass. |
| `super-frgmnts-landing-invitation-v1.webp` | After the closing paragraph | A small, playable piece of Veyra. |

Primary animated assets are 960×540 WebPs. `mobile/` contains 640×360
variants, `gifs/` contains compact 560×315 fallbacks, and `posters/` contains
static JPEG poster frames.
"""
    (OUTPUT / "README.md").write_text(manifest, encoding="utf-8")


def ensure_output_directories() -> None:
    for directory in (OUTPUT, MOBILE_OUTPUT, GIF_OUTPUT, POSTER_OUTPUT):
        directory.mkdir(parents=True, exist_ok=True)


def resolve_bubble_screenshot(requested: Path) -> Path:
    if requested.exists():
        return requested
    candidates = sorted(
        requested.parent.glob("Screenshot 2026-08-03 at 11.51.38*.png")
    )
    if not candidates:
        raise FileNotFoundError(
            f"Could not find the bubble-door source screenshot near {requested}"
        )
    return candidates[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--arrival-capture",
        type=Path,
        default=Path("/tmp/super-frgmnts-arrival-capture"),
    )
    parser.add_argument(
        "--action-capture",
        type=Path,
        default=Path("/tmp/super-frgmnts-action-capture"),
    )
    parser.add_argument(
        "--bubble-screenshot",
        type=Path,
        default=Path("/Users/rylee/Downloads/Screenshot 2026-08-03 at 11.51.38 AM.png"),
    )
    args = parser.parse_args()

    ensure_output_directories()
    build_aryn_sheet()
    build_bubble_door_loop(resolve_bubble_screenshot(args.bubble_screenshot))
    build_arrival_loop(args.arrival_capture)
    build_dialogue_loop()
    build_action_loop(args.action_capture)
    build_landing_invitation()
    write_manifest()

    for path in sorted(OUTPUT.rglob("*")):
        if path.is_file():
            print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
