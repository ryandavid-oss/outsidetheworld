#!/usr/bin/env python3
"""Build permanent discovery pages and the public sitemap for OTW.

The interactive archive interfaces remain the primary human experience. This
builder gives every public record a stable, static HTML document that crawlers,
feed readers, link unfurlers, and people without JavaScript can understand.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from narrative_sync import markdown_to_html  # noqa: E402


SITE_URL = "https://outsidetheworld.com"
AUTHOR_NAME = "RyanDavid Burningham"
AUTHOR_URL = f"{SITE_URL}/ryandavid-burningham.html"
DEFAULT_SOCIAL_IMAGE = f"{SITE_URL}/Images/og/otw-feed-1200x630.jpg"
TODAY = datetime.now().date().isoformat()
PRIVATE_SOURCE_HASHES = {
    "e83d7bbca16ee63b2efbb00e906e5395a144c1131a649f84ae39c38d04ccbfe5",
}
PRIVATE_DISCOVERY_TOMBSTONES = (
    "wayback/2009-08-10-private-record.html",
)

ROOT_PAGES = [
    ("index.html", 1.0),
    ("ryandavid-burningham.html", 0.95),
    ("threads.html", 0.90),
    ("residue_archive.html", 0.88),
    ("professional.html", 0.86),
    ("fragments.html", 0.82),
    ("image_of_the_day.html", 0.82),
    ("wayback.html", 0.80),
    ("poetry.html", 0.80),
    ("drift_poetry.html", 0.80),
    ("change_log.html", 0.62),
    ("resume.html", 0.62),
    ("museum.html", 0.60),
    ("flotsam.html", 0.58),
    ("favorites.html", 0.54),
    ("mac30.html", 0.52),
    ("emmy.html", 0.50),
]

LEGACY_IMAGE_TAG = re.compile(r"<img\b[^>]*>", re.I)
LEGACY_ATTRIBUTE = re.compile(
    r"([^\s=/>]+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))",
    re.I,
)


@dataclass
class DiscoveryRecord:
    path: str
    title: str
    description: str
    kind: str
    date_display: str = ""
    date_iso: str = ""
    body: str = ""
    image: str = ""
    label: str = ""
    author: str = AUTHOR_NAME
    source_path: str = ""

    @property
    def url(self) -> str:
        return f"{SITE_URL}/{quote(self.path, safe='/')}"


def read_balanced_json_array(text: str, start: int) -> str:
    depth = 0
    in_string = False
    escaping = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaping:
                escaping = False
            elif char == "\\":
                escaping = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise ValueError("JSON array was not closed")


def load_js_array(path: Path, assignment_pattern: str) -> list[dict]:
    source = path.read_text(encoding="utf-8")
    match = re.search(assignment_pattern, source)
    if not match:
        raise ValueError(f"Could not locate the public data array in {path.name}")
    start = source.find("[", match.end())
    return json.loads(read_balanced_json_array(source, start))


def slugify(value: str, fallback: str = "signal") -> str:
    slug = re.sub(
        r"^-+|-+$",
        "",
        re.sub(r"[^a-z0-9]+", "-", str(value or "").lower().replace("&", " and ")),
    )
    return slug or fallback


def clean_text(value: str) -> str:
    text = html.unescape(str(value or ""))
    text = re.sub(r"<!--\s*otw-publisher\s*[\s\S]*?-->", " ", text, flags=re.I)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[*_`>#]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def clean_source_lines(value: str) -> str:
    return "\n".join(line.rstrip() for line in str(value or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")).strip()


def excerpt(value: str, limit: int = 190) -> str:
    text = clean_text(value)
    if len(text) <= limit:
        return text
    shortened = text[:limit].rsplit(" ", 1)[0].rstrip(".,;:")
    return f"{shortened}…"


def without_repeated_title(value: str, title: str) -> str:
    lines = str(value or "").splitlines()
    if lines and clean_text(lines[0]).casefold() == clean_text(title).casefold():
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines.pop(0)
    return "\n".join(lines).strip()


def parse_display_date(value: str) -> str:
    raw = str(value or "").strip()
    for pattern in ("%B %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, pattern).date().isoformat()
        except ValueError:
            pass
    return ""


def asset_url(value: str, *, absolute: bool = False) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    if re.match(r"^https?://", raw, re.I):
        return raw
    path = "/" + raw.lstrip("/")
    return f"{SITE_URL}{path}" if absolute else path


def legacy_image_attributes(tag: str) -> dict[str, str]:
    attributes: dict[str, str] = {}
    for match in LEGACY_ATTRIBUTE.finditer(tag):
        value = next((group for group in match.groups()[1:] if group is not None), "")
        attributes[match.group(1).lower()] = html.unescape(value).strip()
    return attributes


def canonical_local_asset_path(value: str) -> str:
    parts = list(Path(value).parts)
    if parts and parts[0].casefold() == "images":
        parts[0] = "Images"
    return Path(*parts).as_posix() if parts else ""


def normalize_legacy_image_source(value: str, *, page_relative: bool = False) -> str:
    raw = html.unescape(str(value or "")).strip().replace("\\", "/")
    if not raw or re.match(r"^(?:javascript|data|blob):", raw, re.I):
        return ""
    if raw.startswith("//"):
        return f"https:{raw}"
    if re.match(r"^https?://", raw, re.I):
        secure = re.sub(r"^http://", "https://", raw, count=1, flags=re.I)
        parsed = urlsplit(secure)
        if parsed.netloc.lower() in {"outsidetheworld.com", "www.outsidetheworld.com"}:
            raw_path = parsed.path.lstrip("/")
            local_path = next(
                (
                    canonical_local_asset_path(candidate)
                    for candidate in (raw_path, unquote(raw_path))
                    if candidate and (ROOT / canonical_local_asset_path(candidate)).is_file()
                ),
                "",
            )
            if local_path:
                encoded = quote(local_path, safe="/+@,;=-_.()")
                return f"../{encoded}" if page_relative else encoded
            return ""
        return secure

    raw_path = unquote(raw.split("?", 1)[0].split("#", 1)[0])
    encoded_path = raw.split("?", 1)[0].split("#", 1)[0]
    if ".." in Path(encoded_path).parts or ".." in Path(raw_path).parts:
        return ""
    candidates = (
        encoded_path.removeprefix("./").lstrip("/"),
        raw_path.removeprefix("./").lstrip("/"),
    )
    local_path = next(
        (
            canonical_local_asset_path(candidate)
            for candidate in candidates
            if candidate and (ROOT / canonical_local_asset_path(candidate)).is_file()
        ),
        "",
    )
    if not local_path:
        return ""
    encoded = quote(local_path, safe="/+@,;=-_.()")
    return f"../{encoded}" if page_relative else encoded


def legacy_wayback_images(value: str) -> list[str]:
    decoded = html.unescape(str(value or ""))
    sources: list[str] = []
    for tag in LEGACY_IMAGE_TAG.findall(decoded):
        source = normalize_legacy_image_source(legacy_image_attributes(tag).get("src", ""))
        if source and source not in sources:
            sources.append(source)
    return sources


def render_legacy_wayback_body(value: str, title: str) -> str:
    decoded = html.unescape(str(value or ""))
    figures: dict[str, str] = {}
    missing_count = 0
    missing_token = "OTWLEGACYMISSINGTOKEN"

    def replace_image(match: re.Match[str]) -> str:
        nonlocal missing_count
        attributes = legacy_image_attributes(match.group(0))
        source = normalize_legacy_image_source(attributes.get("src", ""), page_relative=True)
        if not source:
            missing_count += 1
            return f"\n\n{missing_token}\n\n" if missing_count == 1 else ""
        token = f"OTWLEGACYIMAGE{len(figures):04d}TOKEN"
        alt = clean_text(attributes.get("alt", "")) or f"Recovered image from {title}"
        dimensions = ""
        for name in ("width", "height"):
            candidate = attributes.get(name, "")
            if candidate.isdigit() and 0 < int(candidate) <= 10000:
                dimensions += f' {name}="{candidate}"'
        figures[token] = (
            '<figure class="entry-image entry-image--wayback">'
            f'<img src="{html.escape(source, quote=True)}" alt="{html.escape(alt, quote=True)}"'
            f'{dimensions} loading="lazy" decoding="async" />'
            "</figure>"
        )
        return f"\n\n{token}\n\n"

    prepared = LEGACY_IMAGE_TAG.sub(replace_image, decoded)
    if missing_count:
        noun = "image file" if missing_count == 1 else "image files"
        pronoun = "Its" if missing_count == 1 else "Their"
        figures[missing_token] = (
            '<figure class="entry-image entry-image--missing">'
            f"<figcaption>{missing_count} {noun} did not survive this recovery. {pronoun} absence has been indexed.</figcaption>"
            "</figure>"
        )
    rendered = markdown_to_html(prepared)
    for token, figure in figures.items():
        rendered = rendered.replace(f"<p>{token}</p>", figure).replace(token, figure)
    return rendered


def json_script(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def founder_identity(name: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]+", "", str(name or "").lower())
    return normalized in {"", "ryandavid", "theryandavid", "ryandavidburningham", "rylee", "ryleeburningham"}


def fragment_author(item: dict) -> str:
    author = item.get("author")
    if isinstance(author, dict):
        author = author.get("name") or author.get("display_name")
    return str(author or item.get("author_name") or "RyanDavid").strip()


def fragment_id(item: dict) -> str:
    stamp = re.sub(r"[^0-9]", "", str(item.get("timestamp") or "undated"))
    words = clean_text(item.get("text") or "").split()[:8]
    return f"{stamp}--{slugify(' '.join(words), 'fragment')}"


def load_records() -> dict[str, list[DiscoveryRecord]]:
    wayback_data = load_js_array(ROOT / "wayback_purified.js", r"const\s+wayback_raw_dump\s*=")
    poem_data = load_js_array(ROOT / "poetry_data.js", r"const\s+archive\s*=")
    drift_data = load_js_array(ROOT / "new_poetry_data.js", r"const\s+livingVerse\s*=")
    fragment_data = load_js_array(ROOT / "fragments_data.js", r"window\.otw_fragments\s*=")
    image_data = json.loads((ROOT / "image_manifest.json").read_text(encoding="utf-8"))

    wayback: list[DiscoveryRecord] = []
    used_paths: set[str] = set()
    for index, item in enumerate(wayback_data):
        source_name = str(item.get("file") or "")
        source_hash = hashlib.sha256(source_name.encode("utf-8")).hexdigest()
        if source_hash in PRIVATE_SOURCE_HASHES:
            continue
        stem = Path(str(item.get("file") or f"wayback-{index + 1}")).stem
        base = slugify(stem, f"wayback-{index + 1}")[:150]
        path = f"wayback/{base}.html"
        if path in used_paths:
            path = f"wayback/{base}-{index + 1}.html"
        used_paths.add(path)
        title = str(item.get("title") or "Untitled recovered entry").strip()
        body = without_repeated_title(str(item.get("body") or ""), title)
        legacy_images = legacy_wayback_images(body)
        preferred_image = next(
            (source for source in legacy_images if not re.match(r"^https?://", source, re.I)),
            legacy_images[0] if legacy_images else "",
        )
        wayback.append(
            DiscoveryRecord(
                path=path,
                title=title,
                description=excerpt(body) or f"A recovered Outside The World entry titled {title}.",
                kind="wayback",
                date_display=str(item.get("date") or item.get("year") or "Recovered date unknown"),
                date_iso=parse_display_date(item.get("date") or ""),
                body=body,
                image=preferred_image,
                label="Recovered weblog entry",
                source_path=stem,
            )
        )

    poems: list[DiscoveryRecord] = []
    for collection, label in ((drift_data, "The Drift"), (poem_data, "Verse Archive")):
        for index, item in enumerate(collection):
            poem_id = slugify(item.get("id") or f"poem-{index + 1}")
            title = str(item.get("title") or "Untitled poem").strip()
            title_slug = slugify(title)[:90]
            path_stem = poem_id if poem_id.endswith(title_slug) else f"{poem_id}-{title_slug}"
            path = f"poems/{path_stem}.html"
            body = clean_source_lines(item.get("body") or "")
            poems.append(
                DiscoveryRecord(
                    path=path,
                    title=title,
                    description=excerpt(body) or f"An original poem by {AUTHOR_NAME}.",
                    kind="poem",
                    date_display=str(item.get("date") or "Recovered poem"),
                    date_iso=parse_display_date(item.get("date") or ""),
                    body=body,
                    image=str(item.get("image") or ""),
                    label=label,
                    source_path=str(item.get("id") or ""),
                )
            )

    images: list[DiscoveryRecord] = []
    for item in image_data:
        title = str(item.get("title") or "Image of the Day").strip()
        date_display = str(item.get("date") or "").strip()
        caption = re.sub(r"\s+", " ", str(item.get("caption") or "")).strip()
        images.append(
            DiscoveryRecord(
                path=f"iotd/{slugify(date_display, 'undated')}-{slugify(title)[:90]}.html",
                title=title,
                description=caption or f"An Image of the Day photograph from Outside The World, published {date_display}.",
                kind="image",
                date_display=date_display,
                date_iso=parse_display_date(date_display),
                body=caption,
                image=str(item.get("image") or ""),
                label="Image of the Day",
                source_path=date_display,
            )
        )

    fragments: list[DiscoveryRecord] = []
    for item in fragment_data:
        if not founder_identity(fragment_author(item)):
            continue
        body = clean_source_lines(item.get("text") or "")
        title = excerpt(body, 72) or "Untitled fragment"
        author = fragment_author(item)
        timestamp = str(item.get("timestamp") or "")
        date_iso = timestamp[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", timestamp) else ""
        fragments.append(
            DiscoveryRecord(
                path=f"fragments/{fragment_id(item)}.html",
                title=title,
                description=excerpt(body) or "A public fragment from Outside The World.",
                kind="fragment",
                date_display=date_iso or "Public fragment",
                date_iso=date_iso,
                body=body,
                image=str(item.get("image") or ""),
                label=str(item.get("tag") or "Fragment").replace("_", " ").title(),
                author=AUTHOR_NAME if founder_identity(author) else author,
                source_path=fragment_id(item),
            )
        )

    return {"wayback": wayback, "poem": poems, "image": images, "fragment": fragments}


def navigation_for(records: list[DiscoveryRecord], index: int) -> tuple[DiscoveryRecord | None, DiscoveryRecord | None]:
    newer = records[index - 1] if index > 0 else None
    older = records[index + 1] if index + 1 < len(records) else None
    return newer, older


def render_record(
    record: DiscoveryRecord,
    newer: DiscoveryRecord | None,
    older: DiscoveryRecord | None,
    dig_target: DiscoveryRecord | None,
) -> str:
    collection = {
        "wayback": ("The Wayback", "../wayback.html"),
        "poem": (record.label, "../drift_poetry.html" if record.label == "The Drift" else "../poetry.html"),
        "image": ("Image of the Day", "../image_of_the_day.html"),
        "fragment": ("Fragments", "../fragments.html"),
    }[record.kind]
    social_image = asset_url(record.image, absolute=True) or DEFAULT_SOCIAL_IMAGE
    local_image = asset_url(record.image)
    author_url = AUTHOR_URL if founder_identity(record.author) else f"{SITE_URL}/fragments.html"
    author_href = "../ryandavid-burningham.html" if founder_identity(record.author) else "../fragments.html"

    if record.kind == "poem":
        image_html = ""
        if local_image:
            image_html = (
                '<figure class="entry-image entry-image--poem">'
                f'<img src="{html.escape(local_image, quote=True)}" alt="Artwork accompanying {html.escape(record.title, quote=True)}" />'
                "</figure>"
            )
        content = f'{image_html}<div class="poem-text">{html.escape(record.body)}</div>'
        schema_type = "CreativeWork"
        schema_extra = {"genre": "Poetry"}
    elif record.kind == "image":
        content = (
            '<figure class="entry-image entry-image--photograph">'
            f'<a href="{html.escape(local_image, quote=True)}">'
            f'<img src="{html.escape(local_image, quote=True)}" alt="{html.escape(record.title, quote=True)}" />'
            "</a>"
            + (f'<figcaption>{html.escape(record.body)}</figcaption>' if record.body else "")
            + "</figure>"
        )
        schema_type = "ImageObject"
        schema_extra = {"contentUrl": social_image, "caption": record.body}
    elif record.kind == "fragment":
        content = f'<blockquote class="fragment-text">{html.escape(record.body)}</blockquote>'
        if local_image:
            content += (
                '<figure class="entry-image entry-image--fragment">'
                f'<img src="{html.escape(local_image, quote=True)}" alt="Image attached to this fragment" />'
                "</figure>"
            )
        schema_type = "SocialMediaPosting"
        schema_extra = {"articleBody": record.body}
    else:
        content = f'<div class="prose">{render_legacy_wayback_body(record.body, record.title)}</div>'
        schema_type = "BlogPosting"
        schema_extra = {"articleBody": clean_text(record.body)}

    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "@id": f"{record.url}#record",
        "url": record.url,
        "name": record.title,
        "headline": record.title,
        "description": record.description,
        "isPartOf": {"@id": f"{SITE_URL}/#website"},
        "author": {"@type": "Person", "name": record.author, "url": author_url},
        "mainEntityOfPage": record.url,
        **schema_extra,
    }
    if record.date_iso:
        schema["datePublished"] = record.date_iso
    if social_image != DEFAULT_SOCIAL_IMAGE:
        schema["image"] = social_image

    def nav_card(item: DiscoveryRecord | None, direction: str) -> str:
        if not item:
            return '<span class="entry-nav__empty" aria-hidden="true"></span>'
        return (
            f'<a class="entry-nav__card entry-nav__card--{direction}" href="../{html.escape(item.path, quote=True)}">'
            f'<span>{"Newer" if direction == "newer" else "Older"}</span>'
            f'<strong>{html.escape(item.title)}</strong>'
            "</a>"
        )

    date_meta = ""
    if record.date_display:
        datetime_attr = f' datetime="{record.date_iso}"' if record.date_iso else ""
        date_meta = f'<time{datetime_attr}>{html.escape(record.date_display)}</time><span aria-hidden="true">/</span>'

    dig_html = ""
    if dig_target:
        dig_html = (
            f'<a class="dig-path" href="../{html.escape(dig_target.path, quote=True)}">'
            '<span>Dig somewhere else</span>'
            f'<strong>{html.escape(dig_target.title)}</strong>'
            f'<em>{html.escape(dig_target.label)}</em>'
            "</a>"
        )

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <meta name="color-scheme" content="dark" />
  <meta name="theme-color" content="#09090b" />
  <meta name="robots" content="index,follow,max-image-preview:large" />
  <title>{html.escape(record.title)} | Outside The World</title>
  <meta name="description" content="{html.escape(record.description, quote=True)}" />
  <link rel="canonical" href="{record.url}" />
  <link rel="icon" type="image/svg+xml" href="../favicon.svg" />
  <link rel="stylesheet" href="../archive_entry.css" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="Outside The World" />
  <meta property="og:title" content="{html.escape(record.title, quote=True)}" />
  <meta property="og:description" content="{html.escape(record.description, quote=True)}" />
  <meta property="og:url" content="{record.url}" />
  <meta property="og:image" content="{html.escape(social_image, quote=True)}" />
  <meta property="og:image:alt" content="{html.escape(record.title, quote=True)}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{html.escape(record.title, quote=True)}" />
  <meta name="twitter:description" content="{html.escape(record.description, quote=True)}" />
  <meta name="twitter:image" content="{html.escape(social_image, quote=True)}" />
  <script type="application/ld+json">{json_script(schema)}</script>
</head>
<body class="record-page record-page--{record.kind}">
  <a class="skip-link" href="#record">Skip to the record</a>
  <header class="record-masthead">
    <a class="record-brand" href="../index.html" aria-label="Outside The World home">
      <img src="../Images/Equal.svg" alt="Outside The World" />
    </a>
    <nav aria-label="Record navigation">
      <a href="../threads.html">Threads</a>
      <a href="{collection[1]}">{html.escape(collection[0])}</a>
    </nav>
  </header>
  <main id="record" class="record-shell">
    <article class="record">
      <header class="record-header">
        <p class="record-kicker"><span aria-hidden="true"></span>{html.escape(record.label)}</p>
        <h1>{html.escape(record.title)}</h1>
        <div class="record-meta">
          {date_meta}<a href="{author_href}">{html.escape(record.author)}</a>
        </div>
      </header>
      <div class="record-content record-content--{record.kind}">
        {content}
      </div>
    </article>
    <nav class="entry-nav" aria-label="Adjacent records">
      {nav_card(newer, "newer")}
      {nav_card(older, "older")}
    </nav>
    {dig_html}
  </main>
  <footer class="record-footer">
    <p>Filed where it can be found again.</p>
    <p><a href="../index.html">Outside The World</a> / <a href="../threads.html">Threads</a> / <a href="../atom.xml">Atom</a></p>
  </footer>
</body>
</html>
'''


def write_records(groups: dict[str, list[DiscoveryRecord]]) -> None:
    all_records = sorted(
        (record for records in groups.values() for record in records),
        key=lambda record: record.path,
    )
    tombstones = [
        DiscoveryRecord(path=path, title="", description="", kind="wayback", source_path="__private_tombstone__")
        for path in PRIVATE_DISCOVERY_TOMBSTONES
    ]

    def select_dig_target(record: DiscoveryRecord) -> DiscoveryRecord | None:
        candidates = sorted(
            (candidate for candidate in (*all_records, *tombstones) if candidate.kind != record.kind),
            key=lambda candidate: candidate.path,
        )
        if not candidates:
            return None
        digest = hashlib.sha256(record.path.encode("utf-8")).digest()
        selected = candidates[int.from_bytes(digest[:8], "big") % len(candidates)]
        if selected.source_path != "__private_tombstone__":
            return selected
        public_candidates = [candidate for candidate in candidates if candidate.source_path != "__private_tombstone__"]
        return public_candidates[int.from_bytes(digest[8:16], "big") % len(public_candidates)] if public_candidates else None

    for kind, records in groups.items():
        output_name = {
            "poem": "poems",
            "image": "iotd",
            "fragment": "fragments",
            "wayback": "wayback",
        }[kind]
        output_dir = ROOT / output_name
        output_dir.mkdir(parents=True, exist_ok=True)
        expected = {Path(record.path).name for record in records}
        for stale in output_dir.glob("*.html"):
            if stale.name not in expected:
                stale.unlink()
        for index, record in enumerate(records):
            newer, older = navigation_for(records, index)
            (ROOT / record.path).write_text(
                render_record(record, newer, older, select_dig_target(record)),
                encoding="utf-8",
            )


def resolve_record(groups: dict[str, list[DiscoveryRecord]], kind: str, title: str) -> DiscoveryRecord | None:
    wanted = title.casefold()
    return next((record for record in groups[kind] if record.title.casefold() == wanted), None)


def thread_link(record: DiscoveryRecord | None, fallback_url: str, title: str, copy: str) -> str:
    href = f"{quote(record.path, safe='/')}" if record else fallback_url
    display_title = record.title if record else title
    return (
        f'<a class="thread-link" href="{html.escape(href, quote=True)}">'
        f'<strong>{html.escape(display_title)}</strong><span>{html.escape(copy)}</span></a>'
    )


def write_threads(groups: dict[str, list[DiscoveryRecord]]) -> None:
    sections = [
        (
            "Arizona and the desert",
            "Weather, streets, heat, mountains, monsoon light, and the state that keeps getting into the work.",
            [
                thread_link(resolve_record(groups, "poem", "Sonoran Vitality"), "poetry.html", "Verse Archive", "Summer rain with a desert address."),
                thread_link(resolve_record(groups, "wayback", "The state needs a bath"), "wayback.html", "The Wayback", "Phoenix air awaiting a monsoon-sized correction."),
                thread_link(resolve_record(groups, "wayback", "In Tucson"), "wayback.html", "In Tucson", "Older geography, recovered intact enough."),
            ],
        ),
        (
            "Technology and the machines around us",
            "Apple, web systems, old hardware, newer dependencies, and the occasional device with too much emotional leverage.",
            [
                '<a class="thread-link" href="archive/2026-03-06-the-macbook-neo-makes-an-awful-lot-of-sense.html"><strong>The MacBook Neo makes an awful lot of sense</strong><span>A machine considered on its own strange terms.</span></a>',
                '<a class="thread-link" href="archive/2026-03-27-50-best-apple-products.html"><strong>50 Best Apple Products</strong><span>A list with history, preference, and the usual unnecessary confidence.</span></a>',
                '<a class="thread-link" href="archive/2026-02-25-a-brand-new-otw--baby.html"><strong>A Brand New OTW, baby</strong><span>The site notices itself changing again.</span></a>',
            ],
        ),
        (
            "Faith, doubt, and Latter-day Saint thought",
            "Not a doctrinal department. A recurring argument with belief, authority, mercy, anger, and belonging.",
            [
                '<a class="thread-link" href="archive/2026-06-05-the-crucible-of-continuous-revelation.html"><strong>The Crucible of Continuous Revelation</strong><span>Faith asked to sit inside unresolved tension.</span></a>',
                '<a class="thread-link" href="archive/2026-07-02-religion-fills-me-with-anger-god-does-not.html"><strong>Religion fills me with anger. God does not.</strong><span>The distinction is doing considerable work.</span></a>',
                '<a class="thread-link" href="archive/2026-06-01-different-mercies-of-the-same-light.html"><strong>Different Mercies of the Same Light</strong><span>Another angle on belief and the people carrying it.</span></a>',
            ],
        ),
        (
            "Poetry, including the embarrassing stuff",
            "The current Drift and the recovered verse archive. Some lines survived because no one stopped them.",
            [
                '<a class="thread-link" href="drift_poetry.html"><strong>The Drift</strong><span>Newer poems still moving.</span></a>',
                '<a class="thread-link" href="poetry.html"><strong>Verse Archive</strong><span>Recovered poems and earlier weather.</span></a>',
                thread_link(resolve_record(groups, "poem", "Outside The World"), "poetry.html", "Outside The World", "The phrase beneath the entire site."),
            ],
        ),
        (
            "Photography and daily interruption",
            "Pictures that mattered enough to keep, including the ones that briefly took over the front page.",
            [
                '<a class="thread-link" href="image_of_the_day.html"><strong>Image of the Day</strong><span>The living image run.</span></a>',
                *[
                    thread_link(record, "image_of_the_day.html", "Image of the Day", record.description)
                    for record in groups["image"][:3]
                ],
            ],
        ),
    ]
    section_html = "".join(
        f'''<section class="thread-section">
  <div class="thread-intro"><p>{index:02d}</p><h2>{html.escape(title)}</h2><span>{html.escape(copy)}</span></div>
  <div class="thread-links">{"".join(links)}</div>
</section>'''
        for index, (title, copy, links) in enumerate(sections, 1)
    )
    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Threads Through the Archive | Outside The World",
        "url": f"{SITE_URL}/threads.html",
        "description": "Recurring paths through Outside The World: Arizona, technology, faith, Latter-day Saint thought, poetry, and photography.",
        "author": {"@id": f"{AUTHOR_URL}#person"},
        "isPartOf": {"@id": f"{SITE_URL}/#website"},
    }
    (ROOT / "threads.html").write_text(
        f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <meta name="theme-color" content="#09090b" />
  <meta name="color-scheme" content="dark" />
  <meta name="robots" content="index,follow,max-image-preview:large" />
  <title>Threads Through the Archive | Outside The World</title>
  <meta name="description" content="Recurring paths through Outside The World: Arizona, technology, faith, Latter-day Saint thought, poetry, and photography." />
  <link rel="canonical" href="{SITE_URL}/threads.html" />
  <link rel="icon" type="image/svg+xml" href="favicon.svg" />
  <link rel="stylesheet" href="archive_entry.css" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Outside The World" />
  <meta property="og:title" content="Threads Through the Archive" />
  <meta property="og:description" content="Recurring paths through twenty-six years of writing, poetry, photography, technology, faith, and place." />
  <meta property="og:url" content="{SITE_URL}/threads.html" />
  <meta property="og:image" content="{DEFAULT_SOCIAL_IMAGE}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Threads Through the Archive" />
  <meta name="twitter:description" content="Recurring paths through twenty-six years of Outside The World." />
  <meta name="twitter:image" content="{DEFAULT_SOCIAL_IMAGE}" />
  <script type="application/ld+json">{json_script(schema)}</script>
</head>
<body class="threads-page">
  <header class="record-masthead">
    <a class="record-brand" href="index.html" aria-label="Outside The World home"><img src="Images/Equal.svg" alt="Outside The World" /></a>
    <nav aria-label="Threads navigation"><a href="residue_archive.html">Current archive</a><a href="wayback.html">Wayback</a></nav>
  </header>
  <main class="threads-shell">
    <header class="threads-hero">
      <p class="record-kicker"><span aria-hidden="true"></span>Recurring evidence</p>
      <h1>Threads through<br />the mess.</h1>
      <p>These are not departments. They are paths the archive kept making whether anyone organized them or not.</p>
    </header>
    <div class="threads-list">{section_html}</div>
  </main>
  <footer class="record-footer"><p>No taxonomy was harmed. It was merely asked to loosen up.</p><p><a href="index.html">Outside The World</a> / <a href="ryandavid-burningham.html">Who made this mess?</a></p></footer>
</body>
</html>
''',
        encoding="utf-8",
    )


def html_metadata(path: Path) -> tuple[str, str, bool]:
    source = path.read_text(encoding="utf-8", errors="ignore")
    noindex = bool(re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex', source, re.I))
    canonical = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', source, re.I)
    image = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', source, re.I)
    return (canonical.group(1) if canonical else "", image.group(1) if image else "", noindex)


def root_lastmod(path: Path) -> str:
    if path.name == "index.html" or path.name in {"threads.html", "ryandavid-burningham.html"}:
        return TODAY
    match = re.match(r"(\d{4}-\d{2}-\d{2})", path.name)
    return match.group(1) if match else ""


def write_sitemap(groups: dict[str, list[DiscoveryRecord]]) -> None:
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    ET.register_namespace("image", "http://www.google.com/schemas/sitemap-image/1.1")
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    image_ns = "{http://www.google.com/schemas/sitemap-image/1.1}"
    root = ET.Element(f"{ns}urlset")
    seen: set[str] = set()

    def add(url: str, lastmod: str = "", image_url: str = "", image_title: str = "") -> None:
        if not url or url in seen:
            return
        seen.add(url)
        node = ET.SubElement(root, f"{ns}url")
        ET.SubElement(node, f"{ns}loc").text = url
        if lastmod:
            ET.SubElement(node, f"{ns}lastmod").text = lastmod
        if image_url and image_url != DEFAULT_SOCIAL_IMAGE:
            image_node = ET.SubElement(node, f"{image_ns}image")
            ET.SubElement(image_node, f"{image_ns}loc").text = image_url
            if image_title:
                ET.SubElement(image_node, f"{image_ns}title").text = image_title

    for relative, _priority in ROOT_PAGES:
        path = ROOT / relative
        if not path.exists():
            continue
        canonical, social_image, noindex = html_metadata(path)
        if noindex:
            continue
        add(canonical or (SITE_URL + "/" if relative == "index.html" else f"{SITE_URL}/{relative}"), root_lastmod(path), social_image)

    for archive_path in sorted((ROOT / "archive").glob("*.html"), reverse=True):
        canonical, social_image, noindex = html_metadata(archive_path)
        if noindex or not canonical:
            continue
        add(canonical, root_lastmod(archive_path), social_image, archive_path.stem)

    for records in groups.values():
        for record in records:
            add(record.url, record.date_iso, asset_url(record.image, absolute=True), record.title)

    ET.indent(root, space="  ")
    xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    (ROOT / "sitemap.xml").write_bytes(xml)
    print(f"DISCOVERY_SITEMAP: {len(seen)} canonical URLs written")


def main() -> None:
    groups = load_records()
    write_records(groups)
    write_threads(groups)
    write_sitemap(groups)
    counts = ", ".join(f"{kind}={len(records)}" for kind, records in groups.items())
    print(f"DISCOVERY_BUILD: {counts}")


if __name__ == "__main__":
    main()
