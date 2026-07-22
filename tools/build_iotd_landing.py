#!/usr/bin/env python3
"""Pre-render the current IOTD stage while preserving the dynamic archive."""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PAGE_PATH = ROOT / "image_of_the_day.html"
MANIFEST_PATH = ROOT / "image_manifest.json"
RESPONSIVE_PATH = ROOT / "responsive_media.json"


def attr(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def record_stem(item: dict[str, Any]) -> str:
    if item.get("id"):
        return str(item["id"])
    title = str(item.get("title") or "image").lower().replace("&", " and ")
    slug = re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", title))
    return f"{item['date']}-{slug}"


def record_url(item: dict[str, Any]) -> str:
    return f"iotd/{record_stem(item)}.html"


def image_plan(source: str, responsive: dict[str, Any]) -> dict[str, Any]:
    media = responsive.get(source) if isinstance(responsive, dict) else None
    variants = media.get("variants") if isinstance(media, dict) else []
    variants = variants if isinstance(variants, list) else []
    return {
        "src": variants[min(len(variants) - 1, 2)]["url"] if variants else source,
        "srcset": ", ".join(
            f"{variant['url']} {variant['width']}w"
            for variant in variants
            if variant.get("url") and variant.get("width")
        ),
        "original": str(media.get("original") or source) if isinstance(media, dict) else source,
        "width": int(media.get("width") or 0) if isinstance(media, dict) else 0,
        "height": int(media.get("height") or 0) if isinstance(media, dict) else 0,
    }


def orientation(width: int, height: int) -> str:
    if not width or not height:
        return "portrait"
    ratio = width / height
    if ratio > 1.14:
        return "landscape"
    if ratio < 0.88:
        return "portrait"
    return "square"


def previous_label(current: dict[str, Any], previous: dict[str, Any]) -> str:
    from datetime import date

    current_date = date.fromisoformat(str(current["date"]))
    previous_date = date.fromisoformat(str(previous["date"]))
    return "YESTERDAY" if (current_date - previous_date).days == 1 else "PREVIOUS_SIGNAL"


def render_caption(markdown: str) -> str:
    # Imported lazily so this small builder keeps the site's existing Markdown contract.
    from narrative_sync import markdown_to_html

    return markdown_to_html(markdown or "")


def render_signal_title(value: str) -> str:
    # Preserve the underscore treatment while preferring meaningful wrap points.
    return html.escape(value or "DAILY_SIGNAL").replace("_", "_<wbr>")


def replace_marker(source: str, name: str, content: str) -> str:
    pattern = re.compile(
        rf"(?P<indent>^[ \t]*)<!-- {re.escape(name)}_START -->.*?^[ \t]*<!-- {re.escape(name)}_END -->",
        flags=re.DOTALL | re.MULTILINE,
    )
    match = pattern.search(source)
    if not match:
        raise SystemExit(f"ERROR: {name} markers are missing from {PAGE_PATH.name}")
    indent = match.group("indent")
    replacement = (
        f"{indent}<!-- {name}_START -->\n"
        f"{content.rstrip()}\n"
        f"{indent}<!-- {name}_END -->"
    )
    return source[: match.start()] + replacement + source[match.end() :]


def render_stage(items: list[dict[str, Any]], responsive: dict[str, Any]) -> tuple[str, str, str]:
    current = items[0]
    previous = items[1] if len(items) > 1 else None
    plan = image_plan(str(current["image"]), responsive)
    sizes = "(max-width: 768px) 100vw, (max-width: 1320px) 66vw, 960px"
    size_attrs = ""
    if plan["width"] and plan["height"]:
        size_attrs += f' width="{plan["width"]}" height="{plan["height"]}"'
    if plan["srcset"]:
        size_attrs += f' srcset="{attr(plan["srcset"])}" sizes="{attr(sizes)}"'

    previous_markup = (
        f'<a id="heroPrevious" class="hero-btn" href="{attr(record_url(previous))}">'
        f'{previous_label(current, previous)}</a>'
        if previous
        else '<a id="heroPrevious" class="hero-btn" href="#" hidden>PREVIOUS_SIGNAL</a>'
    )
    caption = render_caption(str(current.get("caption") or ""))
    image_alt = f"{current.get('title') or 'Image of the day'} // Image of the day"
    atmosphere = f'--hero-atmosphere: url("{str(plan["src"]).replace(chr(34), "")}")'

    stage = f'''        <div class="hero-card is-{orientation(plan["width"], plan["height"])}" id="heroCard" style="{attr(atmosphere)}">
            <header class="hero-heading">
                <h2 id="heroTitle" class="hero-title">{render_signal_title(str(current.get("title") or "DAILY_SIGNAL"))}</h2>
            </header>
            <div class="hero-visual">
                <div class="hero-atmosphere" id="heroAtmosphere" aria-hidden="true" style="{attr(atmosphere)}"></div>
                <img id="heroImg" class="hero-img" src="{attr(plan["src"])}"{size_attrs} alt="{attr(image_alt)}" loading="eager" decoding="async" fetchpriority="high" />
            </div>
            <div class="hero-meta">
                <div class="hero-description">
                    <div id="heroDate" class="hero-date">{attr(str(current["date"]).replace("-", "_"))}</div>
                    <div id="heroCaption" class="hero-caption">{caption}</div>
                </div>

                <div class="hero-actions">
                    <a id="heroRecord" class="hero-btn hero-btn--primary" href="{attr(record_url(current))}">VIEW_RECORD</a>
                    <a id="heroOpen" class="hero-btn" href="{attr(plan["original"])}" target="_blank" rel="noopener">OPEN_ORIGINAL</a>
                    <a id="heroDownload" class="hero-btn" href="{attr(plan["original"])}" download>DOWNLOAD</a>
                </div>

                <div class="hero-paths" aria-label="Image discovery">
                    {previous_markup}
                    <button id="heroRandom" class="hero-btn" type="button">RANDOM_SIGNAL</button>
                </div>
            </div>
        </div>'''

    preload = f'    <link rel="preload" as="image" href="{attr(plan["src"])}" fetchpriority="high"'
    if plan["srcset"]:
        preload += f' imagesrcset="{attr(plan["srcset"])}" imagesizes="{attr(sizes)}"'
    preload += " />"
    social = f'''    <meta property="og:image" content="{attr(plan["original"])}" />
    <meta property="og:image:alt" content="{attr(image_alt)}" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="Image of the Day | Outside The World" />
    <meta name="twitter:description" content="Daily signal capture from Outside The World in Queen Creek, Arizona." />
    <meta name="twitter:image" content="{attr(plan["original"])}" />'''
    return stage, preload, social


def main() -> int:
    items = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(items, list) or not items:
        raise SystemExit("ERROR: image_manifest.json must contain at least one record")
    items = sorted(
        items,
        key=lambda item: (str(item.get("publishedAt") or item.get("date") or ""), str(item.get("id") or item.get("image") or "")),
        reverse=True,
    )
    responsive_payload = json.loads(RESPONSIVE_PATH.read_text(encoding="utf-8"))
    responsive = responsive_payload.get("sources") if isinstance(responsive_payload, dict) else {}
    stage, preload, social = render_stage(items, responsive or {})

    source = PAGE_PATH.read_text(encoding="utf-8")
    source = replace_marker(source, "IOTD_SOCIAL", social)
    source = replace_marker(source, "IOTD_PRELOAD", preload)
    source = replace_marker(source, "IOTD_CURRENT", stage)
    PAGE_PATH.write_text(source, encoding="utf-8")
    print(f"Wrote {PAGE_PATH.name} with {items[0]['date']} pre-rendered above the fold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
