#!/usr/bin/env python3
"""Validate OTW permanent records, canonical URLs, sitemap, and local links."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://outsidetheworld.com"
GENERATED_DIRS = ("wayback", "poems", "iotd", "fragments")
FACEBOOK_CDN_PATTERN = re.compile(r"https?://[^\s\"'<>]*fbcdn\.net\b", re.I)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.canonical = ""
        self.robots = ""
        self.references: list[tuple[str, str]] = []
        self.h1_count = 0
        self.title_count = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if tag == "link" and values.get("rel", "").lower() == "canonical":
            self.canonical = values.get("href", "")
        if tag == "meta" and values.get("name", "").lower() == "robots":
            self.robots = values.get("content", "")
        if tag == "h1":
            self.h1_count += 1
        if tag == "title":
            self._in_title = True
        for attr in ("href", "src"):
            if values.get(attr):
                self.references.append((attr, values[attr]))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self._in_title:
            self.title_count += 1
            self._in_title = False


def public_path_from_url(url: str) -> Path | None:
    parsed = urlsplit(url)
    if parsed.scheme and parsed.netloc and parsed.netloc != "outsidetheworld.com":
        return None
    path = unquote(parsed.path)
    if path in {"", "/"}:
        return ROOT / "index.html"
    candidate = ROOT / path.lstrip("/")
    if candidate.is_dir():
        candidate /= "index.html"
    return candidate


def page_files() -> list[Path]:
    pages = [ROOT / "threads.html", ROOT / "ryandavid-burningham.html"]
    for directory in GENERATED_DIRS:
        pages.extend(sorted((ROOT / directory).glob("*.html")))
    return pages


def main() -> int:
    errors: list[str] = []

    media_audit_paths = [
        ROOT / "wayback.html",
        ROOT / "wayback_purified.js",
        ROOT / "sitemap.xml",
        *sorted((ROOT / "blogger_posts").glob("*.md")),
        *sorted((ROOT / "wayback").glob("*.html")),
    ]
    for path in media_audit_paths:
        if not path.exists():
            continue
        if FACEBOOK_CDN_PATTERN.search(path.read_text(encoding="utf-8")):
            errors.append(f"retired Facebook CDN dependency: {path.relative_to(ROOT)}")

    sitemap_path = ROOT / "sitemap.xml"
    try:
        sitemap_root = ET.parse(sitemap_path).getroot()
    except (ET.ParseError, OSError) as exc:
        print(f"ERROR: sitemap.xml is invalid: {exc}")
        return 1

    sitemap_urls = [node.text or "" for node in sitemap_root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    sitemap_set = set(sitemap_urls)
    if len(sitemap_urls) != len(sitemap_set):
        errors.append("sitemap.xml contains duplicate canonical URLs")

    for url in sitemap_urls:
        local_path = public_path_from_url(url)
        if local_path is not None and not local_path.exists():
            errors.append(f"sitemap URL has no local file: {url}")

    pages = page_files()
    for path in pages:
        if not path.exists():
            errors.append(f"expected discovery page is missing: {path.relative_to(ROOT)}")
            continue
        source = path.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(source)
        relative = path.relative_to(ROOT)

        if not parser.canonical:
            errors.append(f"missing canonical: {relative}")
        elif parser.canonical not in sitemap_set:
            errors.append(f"canonical absent from sitemap: {relative} -> {parser.canonical}")
        if "noindex" in parser.robots.lower():
            errors.append(f"generated page is noindex: {relative}")
        if parser.title_count != 1:
            errors.append(f"expected one title element: {relative}")
        if parser.h1_count != 1:
            errors.append(f"expected one h1: {relative}")

        collection = relative.parts[0] if relative.parts else ""
        if collection in GENERATED_DIRS and 'class="dig-path"' not in source:
            errors.append(f"missing cross-archive dig path: {relative}")
        if collection == "wayback":
            if re.search(r"&lt;img\b", source, flags=re.I):
                errors.append(f"escaped legacy image markup is visible: {relative}")
            content_match = re.search(
                r'<div class="record-content record-content--wayback">([\s\S]*?)</div>\s*</article>',
                source,
                flags=re.I,
            )
            content = content_match.group(1) if content_match else ""
            if re.search(r"<(?:script|style|iframe|object|embed|link|meta)\b", content, flags=re.I):
                errors.append(f"unsafe legacy element in record content: {relative}")
            if re.search(r"\son[a-z]+\s*=|javascript:", content, flags=re.I):
                errors.append(f"unsafe legacy attribute in record content: {relative}")
        elif collection == "poems" and 'class="poem-text"' not in source:
            errors.append(f"poem is not using stanza-preserving markup: {relative}")
        elif collection == "iotd" and "entry-image--photograph" not in source:
            errors.append(f"image record is missing photograph markup: {relative}")
        elif collection == "fragments" and "fragment-text" not in source:
            errors.append(f"fragment record is missing compact text markup: {relative}")

        json_scripts = re.findall(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>',
            source,
            flags=re.I,
        )
        if not json_scripts:
            errors.append(f"missing JSON-LD: {relative}")
        for payload in json_scripts:
            try:
                json.loads(payload)
            except json.JSONDecodeError as exc:
                errors.append(f"invalid JSON-LD in {relative}: {exc}")

        page_url = parser.canonical or f"{SITE_URL}/{relative.as_posix()}"
        for attr, reference in parser.references:
            parsed = urlsplit(reference)
            if parsed.scheme in {"mailto", "tel", "data", "blob", "javascript"}:
                continue
            if parsed.scheme in {"http", "https"} and parsed.netloc != "outsidetheworld.com":
                continue
            target_url = urljoin(page_url, reference)
            target = public_path_from_url(target_url)
            if target is not None and not target.exists():
                errors.append(f"broken local {attr} in {relative}: {reference}")

    if errors:
        for error in errors[:100]:
            print(f"ERROR: {error}")
        if len(errors) > 100:
            print(f"ERROR: {len(errors) - 100} additional validation errors omitted")
        return 1

    print(f"DISCOVERY_VALID: {len(pages)} permanent pages and {len(sitemap_urls)} sitemap URLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
