#!/usr/bin/env python3
"""Build the compact, deterministic data payload used by the OTW homepage.

The full source files remain authoritative. This builder mirrors the homepage's
normalization contract while omitting article bodies and other data that cards
never render. The browser retains a legacy-source fallback for safe deployment.
"""

from __future__ import annotations

import hashlib
import html
import json
import math
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote, urlparse


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "frontpage_payload.json"
ARTICLE_FALLBACK = "Images/editorial-fallback-v1.webp"
VALID_FOCALS = {
    "top-left",
    "top",
    "top-right",
    "left",
    "center",
    "right",
    "bottom-left",
    "bottom",
    "bottom-right",
}
MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def parse_js_array(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"=\s*(\[.*\])\s*;\s*$", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Could not find the data array in {path.name}")
    value = json.loads(match.group(1))
    if not isinstance(value, list):
        raise ValueError(f"Expected an array in {path.name}")
    return value


def strip_html(value: Any) -> str:
    parser = _TextExtractor()
    try:
        parser.feed(html.unescape(str(value or "")))
        parser.close()
    except Exception:
        return html.unescape(str(value or ""))
    return "".join(parser.parts)


def clean_text(value: Any) -> str:
    text = strip_html(value)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_`>#-]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return text.strip()


def clean_fragment_text(value: Any) -> str:
    text = strip_html(str(value or "").replace("\r\n", "\n").replace("\r", "\n"))
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^\s{0,3}(?:[-+*>#]+|\d+\.)\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_`]+", "", text)
    text = re.sub(r"[^\S\n]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" +([,.;:!?])", r"\1", text)
    return text.strip()


def build_excerpt(value: Any, max_length: int) -> str:
    text = clean_text(value)
    if len(text) <= max_length:
        return text
    candidate = text[: max_length + 1]
    minimum = max_length * 35 // 100
    sentence_ends = [
        match.end()
        for match in re.finditer(r"[.!?](?:[\"')\]]*)?(?=\s|$)", candidate)
        if match.end() >= minimum
    ]
    if sentence_ends:
        return candidate[: sentence_ends[-1]].strip()
    boundary = candidate.rfind(" ")
    excerpt = candidate[: boundary if boundary > 0 else max_length].rstrip()
    return f"{excerpt}..."


def unique_strings(values: Iterable[Any]) -> list[str]:
    output: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in output:
            output.append(text)
    return output


def normalize_focal(value: Any) -> str:
    focal = str(value or "").lower()
    return focal if focal in VALID_FOCALS else "center"


def slugify(value: Any) -> str:
    text = str(value or "").lower().replace("&", " and ")
    return re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", text))


def archive_path(post: dict[str, Any]) -> str:
    if post.get("share_path"):
        return str(post["share_path"])
    file_name = Path(str(post.get("file") or "")).name
    stem = re.sub(r"\.md$", "", file_name, flags=re.IGNORECASE)
    if stem:
        return f"archive/{quote(stem, safe='')}.html"
    return "residue_archive.html"


def markdown_image(value: Any) -> str:
    match = re.search(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", str(value or ""))
    return match.group(1) if match else ""


def essay_image(post: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    publisher = post.get("publisher") if isinstance(post.get("publisher"), dict) else {}
    images = publisher.get("images") if isinstance(publisher.get("images"), list) else []
    image = next((item for item in images if isinstance(item, dict) and item.get("url")), None)
    if image:
        return str(image.get("url") or ""), image
    blocks = publisher.get("blocks") if isinstance(publisher.get("blocks"), list) else []
    block = next(
        (
            item
            for item in blocks
            if isinstance(item, dict) and item.get("type") == "image" and item.get("url")
        ),
        None,
    )
    if block:
        return str(block.get("url") or ""), block
    return markdown_image(post.get("body")), {}


def normalize_essay(post: dict[str, Any]) -> dict[str, Any]:
    publisher = post.get("publisher") if isinstance(post.get("publisher"), dict) else {}
    date = str(post.get("date") or "")
    title = re.sub(r"\s+", " ", strip_html(post.get("title"))).strip() or "Untitled essay"
    description = clean_text(publisher.get("subhead")) or build_excerpt(post.get("body"), 240)
    url = archive_path(post)
    source_image, image_meta = essay_image(post)
    candidates = unique_strings((source_image, ARTICLE_FALLBACK))
    uses_fallback = not source_image
    meta_alt = clean_text(image_meta.get("alt"))
    meta_caption = clean_text(image_meta.get("caption"))
    if uses_fallback:
        image_alt = ""
    elif meta_alt and not re.match(r"^narrative image$", meta_alt, flags=re.IGNORECASE):
        image_alt = meta_alt
    else:
        image_alt = meta_caption or f"Image for {title}"
    return {
        "key": f"essay:{url}",
        "type": "essay",
        "label": "Essay",
        "title": title,
        "date": date,
        "description": description,
        "image": candidates[0] if candidates else "",
        "imageCandidates": candidates,
        "imageAlt": image_alt,
        "homepageFocal": normalize_focal(image_meta.get("homepageFocal")),
        "usesEditorialFallback": uses_fallback,
        "url": url,
        "sourceName": "narrative_data.js",
    }


def display_date(value: Any) -> str:
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", str(value or ""))
    if not match:
        return ""
    return f"{MONTHS[int(match.group(2)) - 1]} {int(match.group(3))}, {match.group(1)}"


def normalize_iotd(entry: dict[str, Any]) -> dict[str, Any]:
    date = str(entry.get("date") or "")
    image = str(entry.get("image") or "")
    title = re.sub(r"\s+", " ", strip_html(entry.get("title"))).strip() or "Image of the Day"
    caption = clean_text(entry.get("caption")) or "From the Image of the Day run."
    return {
        "key": f"iotd:{date}:{image}",
        "type": "iotd",
        "label": "Image",
        "date": date,
        "title": title,
        "caption": caption,
        "description": caption,
        "image": image,
        "imageCandidates": unique_strings((image,)),
        "imageAlt": title,
        "homepageFocal": normalize_focal(entry.get("homepageFocal")),
        "homepageFit": "contain" if str(entry.get("homepageFit") or "").lower() == "contain" else "cover",
        "displayDate": display_date(date),
        "url": "image_of_the_day.html",
        "sourceName": "image_manifest.json",
    }


def normalize_drift(poem: dict[str, Any]) -> dict[str, Any]:
    date = str(poem.get("date") or "")
    title = re.sub(r"\s+", " ", strip_html(poem.get("title"))).strip() or "Untitled poem"
    body = str(poem.get("body") or "").strip()
    stanzas = [
        [line.strip() for line in stanza.splitlines() if line.strip()]
        for stanza in re.split(r"\n\s*\n", body)
        if stanza.strip()
    ]
    lines = [line for stanza in stanzas for line in stanza]
    longest = max((len(line) for line in lines), default=1)
    shape = [
        [{"width": max(18, min(100, math.floor((len(line) / longest) * 88 + 0.5) + 12))} for line in stanza]
        for stanza in stanzas
    ]
    poem_id = str(poem.get("id") or "")
    image = str(poem.get("image") or "")
    return {
        "key": f"drift:{poem_id or title}",
        "type": "drift",
        "label": "Poem",
        "title": title,
        "date": date,
        "description": build_excerpt(body, 135),
        "poemBody": body,
        "image": image,
        "imageCandidates": unique_strings((image,)),
        "imageAlt": f"{title} artwork",
        "homepageFocal": normalize_focal(poem.get("homepageFocal")),
        "thumbprint": str(poem.get("thumbprint") or ""),
        "stanzaCount": len(stanzas),
        "lineCount": len(lines),
        "poemShape": shape,
        "url": f"drift_poetry.html?poem={quote(poem_id, safe='')}",
        "sourceName": str(poem.get("source") or "new_poetry_data.js"),
    }


def first_text(*values: Any) -> str:
    return next((value.strip() for value in values if isinstance(value, str) and value.strip()), "")


def founder_fragment(fragment: dict[str, Any]) -> bool:
    author = fragment.get("author") if isinstance(fragment.get("author"), dict) else {}
    name_value = fragment.get("author") if isinstance(fragment.get("author"), str) else ""
    author_id = first_text(fragment.get("author_id"), fragment.get("authorId"), author.get("id"))
    name = first_text(
        name_value,
        fragment.get("author_name"),
        fragment.get("authorName"),
        author.get("name"),
        author.get("display_name"),
        author.get("displayName"),
        "The_RyanDavid",
    )
    handle = first_text(
        fragment.get("author_handle"),
        fragment.get("authorHandle"),
        fragment.get("handle"),
        author.get("handle"),
        author.get("username"),
        "@outsidetheworld",
    ).lstrip("@").lower()
    explicit = bool(
        first_text(
            fragment.get("author_id"),
            fragment.get("authorId"),
            fragment.get("author_handle"),
            fragment.get("authorHandle"),
            fragment.get("handle"),
            name_value,
        )
        or author
    )
    return not explicit or author_id.lower() in {"ryan", "outsidetheworld"} or handle == "outsidetheworld" or name.lower() in {"the_ryandavid", "ryan david"}


def fragment_text(fragment: dict[str, Any]) -> str:
    return first_text(fragment.get("text"), fragment.get("body"), fragment.get("content"), fragment.get("message"))


def fragment_timestamp(fragment: dict[str, Any]) -> str:
    return first_text(
        fragment.get("timestamp"),
        fragment.get("created_at"),
        fragment.get("createdAt"),
        fragment.get("published_at"),
        fragment.get("publishedAt"),
    )


def safe_http_url(value: Any) -> str:
    raw = str(value or "").strip()
    parsed = urlparse(raw)
    return raw if parsed.scheme in {"http", "https"} and parsed.netloc else ""


def fragment_image(fragment: dict[str, Any]) -> str:
    values = [
        fragment.get("image"),
        fragment.get("image_url"),
        fragment.get("imageUrl"),
        fragment.get("media_url"),
        fragment.get("mediaUrl"),
        fragment.get("media"),
        fragment.get("attachment"),
        fragment.get("attachments"),
        fragment.get("images"),
    ]
    candidates: list[Any] = []
    for value in values:
        if isinstance(value, list):
            candidates.extend(value)
        elif isinstance(value, dict) and isinstance(value.get("items"), list):
            candidates.extend(value["items"])
        elif value:
            candidates.append(value)
    for candidate in candidates:
        source = {"url": candidate} if isinstance(candidate, str) else candidate
        if not isinstance(source, dict):
            continue
        media_type = first_text(
            source.get("type"), source.get("kind"), source.get("media_type"), source.get("mediaType"), source.get("mime_type"), source.get("mimeType")
        ).lower()
        if "video" in media_type:
            continue
        url = safe_http_url(
            first_text(
                source.get("url"),
                source.get("src"),
                source.get("image"),
                source.get("image_url"),
                source.get("imageUrl"),
                source.get("public_url"),
                source.get("publicUrl"),
                source.get("cdn_url"),
                source.get("cdnUrl"),
            )
        )
        if url and not re.search(r"\.(?:m4v|mov|mp4|webm)(?:$|\?)", url, flags=re.IGNORECASE):
            return url
    return ""


def fragment_link_preview(fragment: dict[str, Any]) -> dict[str, str] | None:
    candidates = [
        fragment.get("link_preview"),
        fragment.get("linkPreview"),
        fragment.get("shared_link"),
        fragment.get("sharedLink"),
        fragment.get("url_preview"),
        fragment.get("urlPreview"),
        fragment.get("link"),
    ]
    candidate = next((value for value in candidates if isinstance(value, (str, dict))), None)
    source = {"url": candidate} if isinstance(candidate, str) else (candidate or {})
    url = safe_http_url(
        first_text(
            source.get("url"),
            source.get("href"),
            source.get("external_url"),
            source.get("externalUrl"),
            fragment.get("link_url"),
            fragment.get("linkUrl"),
            fragment.get("shared_url"),
            fragment.get("sharedUrl"),
        )
    )
    if not url:
        return None
    hostname = urlparse(url).hostname or ""
    host = first_text(source.get("site_name"), source.get("siteName"), source.get("publisher"), re.sub(r"^www\.", "", hostname))
    return {
        "url": url,
        "host": host,
        "title": first_text(source.get("title"), source.get("headline"), source.get("name"), fragment.get("link_title"), fragment.get("linkTitle"), host),
        "description": first_text(source.get("description"), source.get("summary"), source.get("excerpt"), fragment.get("link_description"), fragment.get("linkDescription")),
    }


def fragment_id(fragment: dict[str, Any]) -> str:
    stamp = re.sub(r"[^0-9]", "", fragment_timestamp(fragment) or "undated")
    stub = slugify(" ".join(fragment_text(fragment).split()[:8])) or "fragment"
    return f"{stamp}--{stub}"


def fragment_display_date(value: str) -> str:
    try:
        stamp = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(stamp)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return f"{MONTHS[parsed.month - 1]} {parsed.day}, {parsed.year}"
    except (TypeError, ValueError):
        return ""


def normalize_fragment(fragment: dict[str, Any]) -> dict[str, Any]:
    raw = fragment_text(fragment)
    text = clean_fragment_text(raw)
    embedded = fragment.get("author") if isinstance(fragment.get("author"), dict) else {}
    author_value = fragment.get("author") if isinstance(fragment.get("author"), str) else ""
    author = clean_text(first_text(author_value, fragment.get("author_name"), fragment.get("authorName"), embedded.get("name"), embedded.get("display_name"), embedded.get("displayName"), "The_RyanDavid")) or "The_RyanDavid"
    raw_handle = first_text(fragment.get("author_handle"), fragment.get("authorHandle"), fragment.get("handle"), embedded.get("handle"), embedded.get("username"), "@outsidetheworld")
    handle = raw_handle if raw_handle.startswith("@") else f"@{raw_handle}"
    timestamp = fragment_timestamp(fragment)
    image = fragment_image(fragment)
    link_preview = fragment_link_preview(fragment)
    item_id = fragment_id(fragment)
    words = clean_text(raw).split()
    title = " ".join(words[:7]) if words else "Untitled frgmnt"
    if len(words) > 7:
        title += "..."
    return {
        "key": f"fragment:{item_id}",
        "type": "fragment",
        "label": "frgmnt",
        "text": text,
        "title": title,
        "description": text,
        "author": author,
        "handle": handle,
        "tag": clean_text(fragment.get("tag")) or "frgmnt",
        "date": fragment_display_date(timestamp),
        "timestamp": timestamp,
        "image": image,
        "imageCandidates": unique_strings((image,)),
        "imageAlt": f"Image shared by {author}" if image else "",
        "linkPreview": link_preview,
        "url": f"fragments.html?entry={quote(item_id, safe='')}",
        "sourceName": "fragments_data.js",
    }


def sort_stamp(item: dict[str, Any]) -> tuple[float, str]:
    value = str(item.get("timestamp") or item.get("date") or "")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        stamp = parsed.timestamp()
    except ValueError:
        try:
            stamp = datetime.strptime(value, "%B %d, %Y").replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            stamp = 0
    return stamp, value


def compact_responsive_media(items: Iterable[dict[str, Any]]) -> dict[str, Any]:
    payload = json.loads((ROOT / "responsive_media.json").read_text(encoding="utf-8"))
    available = payload.get("sources") if isinstance(payload.get("sources"), dict) else {}
    candidates = {
        candidate
        for item in items
        for candidate in item.get("imageCandidates", [])
        if isinstance(candidate, str) and candidate
    }
    return {candidate: available[candidate] for candidate in sorted(candidates) if candidate in available}


def content_key(item: dict[str, Any] | None) -> str:
    if not item:
        return ""
    return str(item.get("key") or item.get("url") or f"{item.get('type', 'item')}:{item.get('title') or item.get('text') or ''}")


def source_for_type(content_type: str, sources: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    if content_type == "essay":
        return sources["essays"]
    if content_type == "iotd":
        return sources["images"]
    if content_type == "drift":
        return sources["drift"]
    if content_type == "fragment":
        return sources["fragments"]
    if content_type == "editorial":
        editorial = sources["essays"] + [item for item in sources["drift"] if item.get("imageCandidates")]
        return sorted(editorial, key=sort_stamp, reverse=True)
    return []


def pick_unique(
    rule: dict[str, Any],
    sources: dict[str, list[dict[str, Any]]],
    used: set[str],
) -> dict[str, Any] | None:
    items = source_for_type(str(rule.get("type") or ""), sources)
    preferred: dict[str, Any] | None = None
    if rule.get("mode") == "featured" and rule.get("url"):
        preferred = next((item for item in items if item.get("url") == rule.get("url")), None)
    elif items:
        offset = int(rule.get("offset") or 0) if rule.get("mode") == "offset" else 0
        preferred = items[max(0, offset)] if max(0, offset) < len(items) else items[0]
    if preferred and content_key(preferred) not in used:
        used.add(content_key(preferred))
        return preferred
    fallback = next((item for item in items if content_key(item) not in used), None)
    if fallback:
        used.add(content_key(fallback))
    return fallback


def pick_unused(
    rule: dict[str, Any],
    sources: dict[str, list[dict[str, Any]]],
    used: set[str],
) -> list[dict[str, Any]]:
    count = max(0, int(rule.get("count") or 0))
    picked: list[dict[str, Any]] = []
    for item in source_for_type(str(rule.get("type") or ""), sources):
        key = content_key(item)
        if not key or key in used:
            continue
        picked.append(item)
        used.add(key)
        if len(picked) >= count:
            break
    return picked


def selected_frontpage_items(
    manifest: dict[str, Any], sources: dict[str, list[dict[str, Any]]]
) -> list[dict[str, Any]]:
    """Mirror renderFrontPage's deterministic picks without rendering any DOM."""
    used: set[str] = set()
    selected: list[dict[str, Any]] = []
    lead = pick_unique(manifest.get("lead") or {}, sources, used)
    if lead:
        selected.append(lead)

    rules = list(manifest.get("modules") or []) + list(manifest.get("rail") or [])
    for rule in rules:
        if not isinstance(rule, dict) or not rule.get("slot") or rule.get("type") == "fragment":
            continue
        adjusted = dict(rule)
        if lead and lead.get("type") != "essay" and rule.get("slot") == "moduleEssay":
            adjusted.update({"mode": "latest", "offset": 0})
        item = pick_unique(adjusted, sources, used)
        if item:
            selected.append(item)

    fragment_rule = next(
        (rule for rule in manifest.get("rail") or [] if isinstance(rule, dict) and rule.get("type") == "fragment"),
        {"type": "fragment", "count": 1},
    )
    selected.extend(pick_unused(fragment_rule, sources, used))
    for rule in manifest.get("sections") or []:
        if isinstance(rule, dict) and rule.get("slot"):
            selected.extend(pick_unused(rule, sources, used))
    return selected


def trim_sources_to_selection(
    sources: dict[str, list[dict[str, Any]]], selected: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    """Keep the smallest source prefixes that can reproduce every selected slot."""
    selected_keys = {content_key(item) for item in selected}
    trimmed: dict[str, list[dict[str, Any]]] = {}
    for name, items in sources.items():
        selected_indexes = [index for index, item in enumerate(items) if content_key(item) in selected_keys]
        trimmed[name] = items[: max(selected_indexes) + 1] if selected_indexes else []
    return trimmed


def build_payload() -> dict[str, Any]:
    manifest = json.loads((ROOT / "frontpage_manifest.json").read_text(encoding="utf-8"))
    narratives = parse_js_array(ROOT / "narrative_data.js")
    image_manifest = json.loads((ROOT / "image_manifest.json").read_text(encoding="utf-8"))
    poems = parse_js_array(ROOT / "new_poetry_data.js")
    fragments = parse_js_array(ROOT / "fragments_data.js")

    essays = [normalize_essay(item) for item in narratives]
    images = [normalize_iotd(item) for item in image_manifest if item.get("date") and item.get("image")]
    drift = [normalize_drift(item) for item in poems]
    founder_fragments = [
        normalize_fragment(item)
        for item in fragments
        if founder_fragment(item)
        and (clean_text(fragment_text(item)) or fragment_link_preview(item))
        and str(item.get("author") or "") != "OTW_Bot"
        and str(item.get("author_id") or "") != "otw_bot"
        and not re.search(r"worker test fragment", clean_text(fragment_text(item)), flags=re.IGNORECASE)
    ]
    for collection in (essays, images, drift, founder_fragments):
        collection.sort(key=sort_stamp, reverse=True)

    complete_sources = {
        "essays": essays,
        "images": images,
        "drift": drift,
        "fragments": founder_fragments,
    }
    selected = selected_frontpage_items(manifest, complete_sources)
    sources = trim_sources_to_selection(complete_sources, selected)
    all_items = [item for collection in sources.values() for item in collection]
    core = {
        "manifest": manifest,
        "sources": sources,
        "responsiveMedia": compact_responsive_media(all_items),
    }
    digest = hashlib.sha256(
        json.dumps(core, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "schema": "otw.frontpage.payload",
        "version": 1,
        "contentHash": digest,
        **core,
    }


def write_payload() -> dict[str, Any]:
    payload = build_payload()
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    counts = {name: len(items) for name, items in payload["sources"].items()}
    print(
        f"Wrote {OUTPUT_PATH.relative_to(ROOT)} "
        f"({OUTPUT_PATH.stat().st_size:,} bytes; {counts}; "
        f"{len(payload['responsiveMedia'])} responsive lookups)."
    )
    return payload


def main() -> int:
    write_payload()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
