#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from datetime import datetime, time
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
NARRATIVE_DATA = ROOT / "narrative_data.js"
FRAGMENTS_DATA = ROOT / "fragments_data.js"
OUTPUT = ROOT / "atom.xml"

SITE_URL = "https://outsidetheworld.com"
FEED_URL = f"{SITE_URL}/atom.xml"
SITE_TITLE = "Outside The World"
SITE_SUBTITLE = "Blog posts and fragments from Outside The World."
PHOENIX = ZoneInfo("America/Phoenix")
ATOM_NS = "http://www.w3.org/2005/Atom"
PUBLISHER_METADATA_RE = re.compile(r"<!--\s*otw-publisher\s*[\s\S]*?\s*-->", re.I)


def extract_json_array(path: Path, pattern: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(pattern, text, re.S)
    if not match:
        raise ValueError(f"Could not find JSON array in {path.name}")
    return json.loads(match.group(1))


def slugify(value: str) -> str:
    return re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", str(value or "").lower().replace("&", " and ")))


def build_archive_post_id(post: dict) -> str:
    return f"{post.get('date', 'undated')}--{slugify(post.get('title', 'untitled'))}"


def build_fragment_id(fragment: dict) -> str:
    stamp = re.sub(r"[^0-9]", "", str(fragment.get("timestamp", "undated")))
    body_stub = slugify(" ".join(str(fragment.get("text", "")).split()[:8])) or "fragment"
    return f"{stamp}--{body_stub}"


def clean_text(value: str) -> str:
    text = html.unescape(str(value or ""))
    text = PUBLISHER_METADATA_RE.sub(" ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"!\[[^\]]*\]\(([^)]+)\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    text = re.sub(r"[*_`>#-]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def build_excerpt(value: str, max_length: int = 220) -> str:
    clean = clean_text(value)
    if len(clean) <= max_length:
        return clean
    return f"{clean[:max_length].rstrip()}..."


def build_fragment_title(fragment: dict) -> str:
    clean = clean_text(fragment.get("text", ""))
    if not clean:
        return "Untitled fragment"
    words = clean.split()
    title = " ".join(words[:7])
    return f"{title}..." if len(words) > 7 else title


def format_updated(dt: datetime) -> str:
    return dt.astimezone().replace(microsecond=0).isoformat()


def parse_narrative_date(raw: str) -> datetime:
    parsed = datetime.strptime(raw, "%B %d, %Y")
    return datetime.combine(parsed.date(), time(hour=12), PHOENIX)


def parse_fragment_date(raw: str) -> datetime:
    if raw.endswith("Z"):
        raw = raw.replace("Z", "+00:00")
    return datetime.fromisoformat(raw)


def add_text(parent: ET.Element, tag: str, value: str, **attrib: str) -> ET.Element:
    child = ET.SubElement(parent, f"{{{ATOM_NS}}}{tag}", attrib)
    child.text = value
    return child


def build_entries() -> list[dict]:
    narratives = extract_json_array(NARRATIVE_DATA, r"const\s+current_narrative\s*=\s*(\[[\s\S]*?\])\s*;")
    fragments = extract_json_array(FRAGMENTS_DATA, r"window\.otw_fragments\s*=\s*(\[[\s\S]*?\])\s*;")

    entries: list[dict] = []

    for post in narratives:
        updated = parse_narrative_date(post["date"])
        post_id = build_archive_post_id(post)
        url = f"{SITE_URL}/{post['share_path']}" if post.get("share_path") else f"{SITE_URL}/residue_archive.html?post={quote(post_id)}"
        summary = build_excerpt(post.get("body", ""))
        entries.append(
            {
                "kind": "blog",
                "title": post.get("title") or "Untitled entry",
                "url": url,
                "id": url,
                "updated": updated,
                "summary": summary,
            }
        )

    for fragment in fragments:
        updated = parse_fragment_date(fragment["timestamp"])
        fragment_id = build_fragment_id(fragment)
        url = f"{SITE_URL}/fragments.html?entry={quote(fragment_id)}"
        tag = str(fragment.get("tag", "Fragment")).replace("_", " ").title()
        author = fragment.get("author")
        title = build_fragment_title(fragment)
        if author == "OTW_Bot":
            full_title = f"OTW_Bot: {title}"
        else:
            full_title = f"{tag}: {title}"
        entries.append(
            {
                "kind": "fragment",
                "title": full_title,
                "url": url,
                "id": url,
                "updated": updated,
                "summary": build_excerpt(fragment.get("text", ""), 180),
            }
        )

    entries.sort(key=lambda entry: entry["updated"], reverse=True)
    return entries[:50]


def write_feed(entries: list[dict]) -> None:
    ET.register_namespace("", ATOM_NS)
    feed = ET.Element(f"{{{ATOM_NS}}}feed")
    add_text(feed, "title", SITE_TITLE)
    add_text(feed, "subtitle", SITE_SUBTITLE)
    add_text(feed, "id", FEED_URL)
    add_text(feed, "updated", format_updated(entries[0]["updated"] if entries else datetime.now(PHOENIX)))
    ET.SubElement(feed, f"{{{ATOM_NS}}}link", {"href": SITE_URL})
    ET.SubElement(feed, f"{{{ATOM_NS}}}link", {"href": FEED_URL, "rel": "self", "type": "application/atom+xml"})
    author = ET.SubElement(feed, f"{{{ATOM_NS}}}author")
    add_text(author, "name", "RyanDavid")
    add_text(author, "uri", SITE_URL)

    for item in entries:
        entry = ET.SubElement(feed, f"{{{ATOM_NS}}}entry")
        add_text(entry, "title", item["title"])
        ET.SubElement(entry, f"{{{ATOM_NS}}}link", {"href": item["url"]})
        add_text(entry, "id", item["id"])
        add_text(entry, "updated", format_updated(item["updated"]))
        add_text(entry, "summary", item["summary"], type="text")

    ET.indent(feed, space="  ")
    xml_bytes = ET.tostring(feed, encoding="utf-8", xml_declaration=True)
    OUTPUT.write_bytes(xml_bytes)


def main() -> None:
    entries = build_entries()
    write_feed(entries)
    print(f"Wrote {OUTPUT} with {len(entries)} entries.")


if __name__ == "__main__":
    main()
