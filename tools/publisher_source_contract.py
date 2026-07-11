#!/usr/bin/env python3
"""Source-safe parsing and serialization helpers for OTW published essays."""

from __future__ import annotations

import copy
import difflib
import hashlib
import html
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import narrative_sync

PUBLISHER_METADATA_PATTERN = re.compile(r'<!--\s*otw-publisher\s*([\s\S]*?)\s*-->', re.I)
IMAGE_BLOCK_PATTERN = re.compile(r'^!\[([^\]]*)\]\((\S+?)(?:\s+"((?:\\"|[^"])*)")?\)\s*$', re.S)
HR_PATTERN = re.compile(r'^\s*(?:-{3,}|\*{3,}|_{3,})\s*$')
HEADING_PATTERN = re.compile(r'^(#{2,3})\s+(.+?)\s*$')
ORDERED_LIST_PATTERN = re.compile(r'^\d+[.)]\s+')
UNORDERED_LIST_PATTERN = re.compile(r'^[-*+]\s+')
DATE_LINE_PATTERN = re.compile(r'^(?:(Date:)\s*|(###)\s*)(.*?)\s*$', re.I)
TITLE_LINE_PATTERN = re.compile(r'^#\s+(.+?)\s*$')
FENCE_PATTERN = re.compile(r'^\s*(```|~~~)')
TABLE_SEPARATOR_PATTERN = re.compile(r'^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$')
FOOTNOTE_PATTERN = re.compile(r'(^|\n)\s*\[\^.+?\]:|\[\^.+?\]')
HTML_BLOCK_PATTERN = re.compile(r'^\s*<([a-zA-Z][\w:-]*)\b[\s\S]*?>')


EDITABLE_TYPES = {
    "paragraph",
    "heading",
    "quote",
    "list",
    "image",
    "divider",
}


@dataclass
class SourceBlock:
    id: str
    type: str
    markdown: str
    editable: bool
    protected_reason: str = ""
    attrs: dict[str, Any] = field(default_factory=dict)
    metadata_block: dict[str, Any] | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "markdown": self.markdown,
            "editable": self.editable,
            "protectedReason": self.protected_reason,
            "attrs": self.attrs,
            "metadataBlock": self.metadata_block,
        }


@dataclass
class SourceDocument:
    path: Path
    source: str
    title: str
    date: str
    metadata: dict[str, Any]
    metadata_raw: str
    subhead: str
    blocks: list[SourceBlock]
    date_prefix: str = "Date:"
    body_prefix: str = ""
    source_hash: str = ""
    malformed_metadata: bool = False

    @property
    def stem(self) -> str:
        return self.path.stem

    @property
    def slug(self) -> str:
        return narrative_sync.essay_slug_from_stem(self.stem)

    @property
    def archive_path(self) -> str:
        return f"{narrative_sync.share_output_folder}/{self.stem}.html"

    @property
    def og_path(self) -> str:
        return f"{narrative_sync.og_output_folder}/{self.stem}.png"

    def to_json(self, include_source: bool = False) -> dict[str, Any]:
        data = {
            "title": self.title,
            "date": self.date,
            "slug": self.slug,
            "stem": self.stem,
            "sourcePath": str(self.path.relative_to(ROOT)),
            "archivePath": self.archive_path,
            "ogPath": self.og_path,
            "sourceHash": self.source_hash,
            "subhead": self.subhead,
            "hasPublisherMetadata": bool(self.metadata),
            "malformedMetadata": self.malformed_metadata,
            "blocks": [block.to_json() for block in self.blocks],
        }
        if include_source:
            data["source"] = self.source
        return data


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_newlines(value: str) -> str:
    return str(value or "").replace("\r\n", "\n").replace("\r", "\n")


def normalize_plain_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


def markdown_unescape(value: str) -> str:
    return (value or "").replace('\\"', '"').replace("\\[", "[").replace("\\]", "]").replace("\\\\", "\\")


def escape_markdown_text(value: str) -> str:
    return str(value or "").replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def block_plain_text(markdown: str) -> str:
    return normalize_plain_text(narrative_sync.strip_markdown(markdown or ""))


def slug_for_path(path: Path) -> str:
    return narrative_sync.essay_slug_from_stem(path.stem)


def display_date_to_file_date(display_date: str) -> str:
    parsed = narrative_sync.parse_display_date(display_date)
    return parsed.strftime("%Y-%m-%d") if parsed else ""


def split_markdown_blocks(markdown: str) -> list[str]:
    text = normalize_newlines(markdown).strip()
    if not text:
        return []
    return re.split(r"\n\s*\n", text)


def parse_publisher_metadata(body: str) -> tuple[dict[str, Any], str, str, bool]:
    match = PUBLISHER_METADATA_PATTERN.search(body or "")
    if not match:
        return {}, "", body, False

    raw_comment = match.group(0)
    malformed = False
    metadata: dict[str, Any] = {}
    try:
        candidate = json.loads(match.group(1).strip())
        metadata = narrative_sync.sanitize_publisher_metadata(candidate)
        if not metadata:
            malformed = True
    except Exception:
        malformed = True
    cleaned = (body[: match.start()] + body[match.end() :]).strip()
    return metadata, raw_comment, cleaned, malformed


def extract_leading_subhead(body: str, metadata: dict[str, Any]) -> tuple[str, str]:
    expected = narrative_sync.publisher_subhead({"publisher": metadata}) if metadata else ""
    blocks = split_markdown_blocks(body)
    if not blocks:
        return "", body.strip()

    first = blocks[0].strip()
    if re.fullmatch(r"_(.+)_", first, flags=re.S) or re.fullmatch(r"\*(.+)\*", first, flags=re.S):
        subhead = first[1:-1].strip()
        remaining = "\n\n".join(blocks[1:]).strip()
        return subhead, remaining

    if expected and normalize_plain_text(block_plain_text(first)) == normalize_plain_text(expected):
        remaining = "\n\n".join(blocks[1:]).strip()
        return expected, remaining

    return expected, body.strip()


def metadata_blocks(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    blocks = metadata.get("blocks") if isinstance(metadata, dict) else []
    return [block for block in blocks if isinstance(block, dict)] if isinstance(blocks, list) else []


def markdown_block_render_type(markdown: str) -> str:
    block = markdown.strip()
    if IMAGE_BLOCK_PATTERN.match(block):
        return "image"
    if HR_PATTERN.match(block):
        return "divider"
    if HEADING_PATTERN.match(block):
        return "heading"
    if block.startswith(">"):
        return "quote"
    lines = block.splitlines()
    if lines and all(UNORDERED_LIST_PATTERN.match(line) or ORDERED_LIST_PATTERN.match(line) for line in lines):
        return "list"
    return "paragraph"


def matching_metadata_block(markdown: str, blocks: list[dict[str, Any]], cursor: int) -> tuple[dict[str, Any] | None, int]:
    render_type = markdown_block_render_type(markdown)
    while cursor < len(blocks):
        candidate = blocks[cursor]
        cursor += 1
        candidate_type = candidate.get("type")
        if candidate_type == render_type:
            return candidate, cursor
        if candidate_type == "paragraph" and render_type == "paragraph":
            return candidate, cursor
    return None, cursor


def classify_list(block: str) -> tuple[bool, str, dict[str, Any]]:
    lines = block.splitlines()
    if not lines:
        return False, "empty list", {}
    ordered = bool(ORDERED_LIST_PATTERN.match(lines[0]))
    unordered = bool(UNORDERED_LIST_PATTERN.match(lines[0]))
    if not (ordered or unordered):
        return False, "not a simple list", {}
    matcher = ORDERED_LIST_PATTERN if ordered else UNORDERED_LIST_PATTERN
    if any(line.startswith((" ", "\t")) for line in lines):
        return False, "nested or indented lists are protected", {}
    if any(not matcher.match(line) for line in lines):
        return False, "mixed or multiline lists are protected", {}
    return True, "", {"ordered": ordered, "items": [matcher.sub("", line).strip() for line in lines]}


def classify_block(block: str, index: int, metadata_block: dict[str, Any] | None = None) -> SourceBlock:
    raw = block.strip()
    block_id = str((metadata_block or {}).get("id") or f"block-{index:03d}")
    if not raw:
        return SourceBlock(block_id, "raw", block, False, "empty block", metadata_block=metadata_block)

    if FENCE_PATTERN.match(raw):
        return SourceBlock(block_id, "raw", block, False, "fenced code blocks are protected", metadata_block=metadata_block)
    if TABLE_SEPARATOR_PATTERN.search(raw):
        return SourceBlock(block_id, "raw", block, False, "tables are protected", metadata_block=metadata_block)
    if FOOTNOTE_PATTERN.search(raw):
        return SourceBlock(block_id, "raw", block, False, "footnotes are protected", metadata_block=metadata_block)

    image_match = IMAGE_BLOCK_PATTERN.match(raw)
    if image_match:
        return SourceBlock(
            block_id,
            "image",
            raw,
            True,
            attrs={
                "alt": markdown_unescape(image_match.group(1) or ""),
                "url": image_match.group(2) or "",
                "caption": markdown_unescape(image_match.group(3) or ""),
            },
            metadata_block=metadata_block,
        )

    if HR_PATTERN.match(raw):
        return SourceBlock(block_id, "divider", raw, True, metadata_block=metadata_block)

    heading_match = HEADING_PATTERN.match(raw)
    if heading_match:
        return SourceBlock(
            block_id,
            "heading",
            raw,
            True,
            attrs={"level": len(heading_match.group(1)), "text": heading_match.group(2).strip()},
            metadata_block=metadata_block,
        )

    if raw.startswith(">"):
        lines = raw.splitlines()
        if all(line.startswith(">") and not line.startswith(">>") for line in lines):
            return SourceBlock(
                block_id,
                "quote",
                raw,
                True,
                attrs={"text": "\n".join(line[1:].strip() for line in lines)},
                metadata_block=metadata_block,
            )
        return SourceBlock(block_id, "raw", raw, False, "nested blockquotes are protected", metadata_block=metadata_block)

    simple_list, reason, attrs = classify_list(raw)
    if simple_list:
        return SourceBlock(block_id, "list", raw, True, attrs=attrs, metadata_block=metadata_block)
    if reason != "not a simple list":
        return SourceBlock(block_id, "raw", raw, False, reason, metadata_block=metadata_block)

    html_match = HTML_BLOCK_PATTERN.match(raw)
    if html_match:
        tag = html_match.group(1).lower()
        if tag in {"p", "span", "strong", "em", "b", "i", "a", "code", "br"}:
            return SourceBlock(block_id, "paragraph", raw, True, metadata_block=metadata_block)
        return SourceBlock(block_id, "raw", raw, False, f"HTML <{tag}> blocks are protected", metadata_block=metadata_block)

    return SourceBlock(block_id, "paragraph", raw, True, metadata_block=metadata_block)


def parse_source(path: Path) -> SourceDocument:
    source = normalize_newlines(path.read_text(encoding="utf-8"))
    source_hash = sha256_text(source)
    lines = source.splitlines()
    if len(lines) < 2:
        raise ValueError(f"{path} is missing title/date lines")
    title_match = TITLE_LINE_PATTERN.match(lines[0] or "")
    date_match = DATE_LINE_PATTERN.match(lines[1] or "")
    if not title_match or not date_match:
        raise ValueError(f"{path} must start with '# title' and 'Date:'")

    raw_body = "\n".join(lines[2:]).strip()
    metadata, metadata_raw, body_without_metadata, malformed_metadata = parse_publisher_metadata(raw_body)
    subhead, body = extract_leading_subhead(body_without_metadata, metadata)
    markdown_blocks = split_markdown_blocks(body)
    pub_blocks = metadata_blocks(metadata)
    cursor = 0
    blocks: list[SourceBlock] = []
    for index, markdown_block in enumerate(markdown_blocks, start=1):
        metadata_block, cursor = matching_metadata_block(markdown_block, pub_blocks, cursor)
        blocks.append(classify_block(markdown_block, index, metadata_block))

    return SourceDocument(
        path=path,
        source=source,
        title=title_match.group(1).strip(),
        date=date_match.group(3).strip(),
        metadata=metadata,
        metadata_raw=metadata_raw,
        subhead=subhead,
        blocks=blocks,
        date_prefix="###" if date_match.group(2) else "Date:",
        source_hash=source_hash,
        malformed_metadata=malformed_metadata,
    )


def publisher_metadata_comment(metadata: dict[str, Any]) -> str:
    if not metadata:
        return ""
    safe = copy.deepcopy(metadata)
    json_text = (
        json.dumps(safe, ensure_ascii=False, indent=2)
        .replace("--", "\\u002d\\u002d")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )
    return f"<!-- otw-publisher\n{json_text}\n-->"


def inline_markdown_to_plain_html(markdown: str) -> str:
    value = html.escape(str(markdown or ""), quote=False)
    value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", value)
    value = re.sub(r"`(.+?)`", r"<code>\1</code>", value)
    value = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|/[^)\s]+|#[^)\s]+|mailto:[^)\s]+)\)", r'<a href="\2">\1</a>', value)
    return value


def composer_block_from_source_block(block: SourceBlock) -> dict[str, Any]:
    metadata = block.metadata_block if isinstance(block.metadata_block, dict) else {}
    block_id = block.id or str(metadata.get("id") or "")
    text = block_plain_text(block.markdown)
    html_value = metadata.get("html") if isinstance(metadata.get("html"), str) else inline_markdown_to_plain_html(block.markdown)

    if not block.editable:
        return {
            "id": block_id or f"raw_{sha256_text(block.markdown)[:8]}",
            "type": "raw",
            "originalType": block.type or "raw",
            "raw": block.markdown,
            "markdown": block.markdown,
            "sourceMarkdown": block.markdown,
            "text": block.protected_reason or "Protected raw block",
            "protectedReason": block.protected_reason or "Protected raw block",
        }

    if block.type == "paragraph":
        return {
            "id": block_id,
            "type": "paragraph",
            "html": html_value,
            "sourceHtml": html_value,
            "sourceMarkdown": block.markdown,
            "text": text,
        }

    if block.type == "heading":
        level = int(block.attrs.get("level") or metadata.get("level") or 2)
        heading_text = block.attrs.get("text") or HEADING_PATTERN.sub(r"\2", block.markdown.strip())
        return {
            "id": block_id,
            "type": "heading",
            "level": level if 2 <= level <= 6 else 2,
            "html": metadata.get("html") if isinstance(metadata.get("html"), str) else inline_markdown_to_plain_html(str(heading_text)),
            "sourceHtml": metadata.get("html") if isinstance(metadata.get("html"), str) else inline_markdown_to_plain_html(str(heading_text)),
            "sourceMarkdown": block.markdown,
            "text": block_plain_text(str(heading_text)),
        }

    if block.type == "quote":
        quote_text = block.attrs.get("text") or "\n".join(line[1:].strip() for line in block.markdown.strip().splitlines())
        return {
            "id": block_id,
            "type": "quote",
            "html": metadata.get("html") if isinstance(metadata.get("html"), str) else inline_markdown_to_plain_html(str(quote_text)),
            "sourceHtml": metadata.get("html") if isinstance(metadata.get("html"), str) else inline_markdown_to_plain_html(str(quote_text)),
            "sourceMarkdown": block.markdown,
            "text": block_plain_text(str(quote_text)),
        }

    if block.type == "list":
        simple, _, attrs = classify_list(block.markdown.strip())
        items = []
        if simple:
            for index, item in enumerate(attrs.get("items", []), start=1):
                existing = {}
                existing_items = metadata.get("items") if isinstance(metadata.get("items"), list) else []
                if index - 1 < len(existing_items) and isinstance(existing_items[index - 1], dict):
                    existing = existing_items[index - 1]
                items.append({
                    "id": str(existing.get("id") or f"{block_id}-item-{index}"),
                    "html": existing.get("html") if isinstance(existing.get("html"), str) else inline_markdown_to_plain_html(str(item)),
                    "text": block_plain_text(str(item)),
                })
        return {
            "id": block_id,
            "type": "list",
            "ordered": bool(attrs.get("ordered")) if simple else bool(metadata.get("ordered")),
            "items": items,
            "sourceMarkdown": block.markdown,
        }

    if block.type == "image":
        url = str(metadata.get("url") or block.attrs.get("url") or "")
        alt = str(metadata.get("alt") or block.attrs.get("alt") or "")
        caption = str(metadata.get("caption") or block.attrs.get("caption") or "")
        display_size = str(metadata.get("displaySize") or "medium")
        alignment = str(metadata.get("alignment") or "center")
        wrap_mode = str(metadata.get("wrapMode") or "none")
        return {
            "id": block_id,
            "type": "image",
            "source": {
                "kind": "url",
                "url": url,
                "objectKey": str(metadata.get("objectKey") or ""),
            },
            "alt": alt,
            "caption": caption,
            "credit": str(metadata.get("credit") or ""),
            "width": int(metadata.get("width") or 0),
            "height": int(metadata.get("height") or 0),
            "featureLayout": str(metadata.get("featureLayout") or "natural"),
            "featureFocal": str(metadata.get("featureFocal") or "center"),
            "displaySize": display_size,
            "alignment": alignment,
            "wrapMode": wrap_mode,
            "status": "uploaded",
            "upload": {
                "status": "uploaded",
                "uploadedUrl": url,
                "objectKey": str(metadata.get("objectKey") or ""),
                "error": "",
            },
            "sourceMarkdown": block.markdown,
        }

    if block.type == "divider":
        return {
            "id": block_id,
            "type": "divider",
            "sourceMarkdown": block.markdown,
        }

    return {
        "id": block_id or f"raw_{sha256_text(block.markdown)[:8]}",
        "type": "raw",
        "originalType": block.type or "raw",
        "raw": block.markdown,
        "markdown": block.markdown,
        "sourceMarkdown": block.markdown,
        "text": "Protected raw block",
        "protectedReason": "Unsupported block type",
    }


def composer_article_for_document(document: SourceDocument, source: str | None = None) -> dict[str, Any]:
    doc = document if source is None else document_from_source_text(document.path, source)
    file_date = display_date_to_file_date(doc.date)
    feature_image_ref = str((doc.metadata or {}).get("featureImageRef") or "")
    composer_blocks = [composer_block_from_source_block(block) for block in doc.blocks]
    for block in composer_blocks:
        if block.get("type") == "image" and block.get("id") == feature_image_ref:
            block["isFeature"] = True
    return {
        "schema": "otw.publisher.article",
        "version": 3,
        "createdAt": "",
        "updatedAt": "",
        "title": doc.title,
        "subhead": doc.subhead,
        "metadata": {
            "docName": doc.title,
            "articleDate": file_date,
            "publishDate": file_date,
            "slug": doc.slug,
            "surface": "Outside The World Article",
            "publishedRevision": True,
            "sourcePath": str(doc.path.relative_to(ROOT)),
            "archivePath": doc.archive_path,
            "ogPath": doc.og_path,
        },
        "body": {
            "blocks": composer_blocks,
        },
    }


def update_metadata_for_blocks(metadata: dict[str, Any], blocks: list[SourceBlock], subhead: str) -> dict[str, Any]:
    if not metadata:
        return {}
    updated = copy.deepcopy(metadata)
    updated["subhead"] = subhead or ""
    next_blocks = []
    images = []
    for block in blocks:
        existing = copy.deepcopy(block.metadata_block or {})
        if not block.editable:
            next_blocks.append(existing or {"id": block.id, "type": "raw"})
            continue
        if block.type == "paragraph":
            existing.update({
                "id": block.id,
                "type": "paragraph",
                "html": inline_markdown_to_plain_html(block.markdown.strip()),
                "text": block_plain_text(block.markdown),
            })
        elif block.type == "heading":
            level = int(block.attrs.get("level") or 2)
            text = HEADING_PATTERN.sub(r"\2", block.markdown.strip())
            existing.update({
                "id": block.id,
                "type": "heading",
                "level": level if level in {2, 3} else 2,
                "html": inline_markdown_to_plain_html(text),
                "text": block_plain_text(text),
            })
        elif block.type == "quote":
            text = "\n".join(line[1:].strip() for line in block.markdown.strip().splitlines())
            existing.update({
                "id": block.id,
                "type": "quote",
                "html": inline_markdown_to_plain_html(text),
                "text": block_plain_text(text),
            })
        elif block.type == "list":
            simple, _, attrs = classify_list(block.markdown.strip())
            items = attrs.get("items", []) if simple else []
            existing.update({
                "id": block.id,
                "type": "list",
                "ordered": bool(attrs.get("ordered")),
                "items": [
                    {
                        "id": f"{block.id}-item-{index + 1}",
                        "html": inline_markdown_to_plain_html(item),
                        "text": block_plain_text(item),
                    }
                    for index, item in enumerate(items)
                ],
            })
        elif block.type == "image":
            match = IMAGE_BLOCK_PATTERN.match(block.markdown.strip())
            alt = markdown_unescape(match.group(1) if match else block.attrs.get("alt", ""))
            url = match.group(2) if match else block.attrs.get("url", "")
            caption = markdown_unescape(match.group(3) if match and match.group(3) else block.attrs.get("caption", ""))
            existing.update({
                "id": block.id,
                "type": "image",
                "imageRef": existing.get("imageRef") or block.id,
                "url": url,
                "alt": alt,
                "caption": caption,
                "credit": str(existing.get("credit") or ""),
                "width": int(existing.get("width") or 0),
                "height": int(existing.get("height") or 0),
                "featureLayout": str(existing.get("featureLayout") or "natural"),
                "featureFocal": str(existing.get("featureFocal") or "center"),
            })
            image_meta = {
                "id": existing.get("imageRef") or block.id,
                "url": url,
                "alt": alt,
                "caption": caption,
                "credit": str(existing.get("credit") or ""),
                "width": int(existing.get("width") or 0),
                "height": int(existing.get("height") or 0),
                "featureLayout": str(existing.get("featureLayout") or "natural"),
                "featureFocal": str(existing.get("featureFocal") or "center"),
                "displaySize": existing.get("displaySize", "medium"),
                "alignment": existing.get("alignment", "center"),
                "wrapMode": existing.get("wrapMode", "none"),
            }
            if existing.get("objectKey"):
                image_meta["objectKey"] = existing.get("objectKey")
            images.append(image_meta)
        elif block.type == "divider":
            existing.update({"id": block.id, "type": "divider"})
        next_blocks.append(existing)
    updated["blocks"] = [block for block in next_blocks if block]
    if images:
        existing_images = {
            str((item or {}).get("id")): item
            for item in updated.get("images", [])
            if isinstance(item, dict) and item.get("id")
        }
        merged = []
        for image in images:
            previous = existing_images.get(str(image.get("id"))) or {}
            merged.append({**previous, **image})
        updated["images"] = merged
    return narrative_sync.sanitize_publisher_metadata(updated)


def blocks_from_payload(payload_blocks: list[dict[str, Any]]) -> list[SourceBlock]:
    blocks = []
    for index, block in enumerate(payload_blocks or [], start=1):
        block_type = str(block.get("type") or "raw")
        markdown = normalize_newlines(str(block.get("markdown") or "")).strip()
        editable = bool(block.get("editable")) and block_type in EDITABLE_TYPES
        parsed = classify_block(markdown, index, block.get("metadataBlock") if isinstance(block.get("metadataBlock"), dict) else None)
        if parsed.type != block_type and block_type != "raw":
            editable = False
        parsed.id = str(block.get("id") or parsed.id)
        parsed.editable = editable
        parsed.protected_reason = "" if editable else str(block.get("protectedReason") or parsed.protected_reason or "protected raw block")
        parsed.metadata_block = block.get("metadataBlock") if isinstance(block.get("metadataBlock"), dict) else parsed.metadata_block
        blocks.append(parsed)
    return blocks


def serialize_with_preserved_tail(document: SourceDocument, title: str, date: str, subhead: str, blocks: list[SourceBlock]) -> str | None:
    if subhead != document.subhead or len(blocks) != len(document.blocks):
        return None

    original_parts = document.source.split("\n", 2)
    if len(original_parts) < 3:
        return None

    tail = original_parts[2]
    cursor = 0
    pieces: list[str] = []
    for original, updated in zip(document.blocks, blocks):
        needle = original.markdown.strip()
        if not needle:
            return None
        index = tail.find(needle, cursor)
        if index < 0:
            return None
        pieces.append(tail[cursor:index])
        pieces.append(updated.markdown.strip())
        cursor = index + len(needle)
    pieces.append(tail[cursor:])

    date_line = f"### {date}" if document.date_prefix == "###" else f"Date: {date}"
    return f"# {title}\n{date_line}\n{''.join(pieces)}".rstrip() + "\n"


def serialize_document(document: SourceDocument, patch: dict[str, Any] | None = None) -> str:
    if not patch:
        return document.source

    title = str(patch.get("title", document.title)).strip() or document.title
    date = str(patch.get("date", document.date)).strip() or document.date
    subhead = str(patch.get("subhead", document.subhead)).strip()
    blocks = blocks_from_payload(patch.get("blocks", [])) if "blocks" in patch else document.blocks
    if "blocks" in patch:
        preserved = serialize_with_preserved_tail(document, title, date, subhead, blocks)
        if preserved is not None:
            return preserved
    metadata = update_metadata_for_blocks(document.metadata, blocks, subhead) if document.metadata else {}

    date_line = f"### {date}" if document.date_prefix == "###" else f"Date: {date}"
    pieces = [f"# {title}", date_line, ""]
    if metadata:
        pieces.append(publisher_metadata_comment(metadata))
        pieces.append("")
    if subhead:
        pieces.append(f"_{escape_markdown_text(subhead)}_")
        pieces.append("")
    pieces.append("\n\n".join(block.markdown.strip() for block in blocks).strip())
    return "\n".join(pieces).rstrip() + "\n"


def document_from_source_text(path: Path, source: str) -> SourceDocument:
    temp_path = path
    source = normalize_newlines(source)
    lines = source.splitlines()
    if len(lines) < 2:
        raise ValueError("Draft source must include title and date lines")
    title_match = TITLE_LINE_PATTERN.match(lines[0] or "")
    date_match = DATE_LINE_PATTERN.match(lines[1] or "")
    if not title_match or not date_match:
        raise ValueError("Draft source must start with '# title' and 'Date:'")
    raw_body = "\n".join(lines[2:]).strip()
    metadata, metadata_raw, body_without_metadata, malformed_metadata = parse_publisher_metadata(raw_body)
    subhead, body = extract_leading_subhead(body_without_metadata, metadata)
    pub_blocks = metadata_blocks(metadata)
    cursor = 0
    blocks = []
    for index, markdown_block in enumerate(split_markdown_blocks(body), start=1):
        metadata_block, cursor = matching_metadata_block(markdown_block, pub_blocks, cursor)
        blocks.append(classify_block(markdown_block, index, metadata_block))
    return SourceDocument(
        path=temp_path,
        source=source,
        title=title_match.group(1).strip(),
        date=date_match.group(3).strip(),
        metadata=metadata,
        metadata_raw=metadata_raw,
        subhead=subhead,
        blocks=blocks,
        date_prefix="###" if date_match.group(2) else "Date:",
        source_hash=sha256_text(source),
        malformed_metadata=malformed_metadata,
    )


def post_from_source_document(document: SourceDocument, source: str | None = None) -> dict[str, Any]:
    doc = document if source is None else document_from_source_text(document.path, source)
    post = {
        "title": doc.title,
        "date": doc.date,
        "body": "\n\n".join(block.markdown.strip() for block in doc.blocks).strip(),
        "file": doc.path.name,
    }
    if doc.metadata:
        post["publisher"] = doc.metadata
    return post


def paragraphs_for_source(document: SourceDocument, source: str | None = None) -> list[dict[str, Any]]:
    post = post_from_source_document(document, source)
    deck = narrative_sync.publisher_subhead(post)
    body_html = narrative_sync.render_reader_body_html(post, deck)
    paragraphs = narrative_sync.extract_reader_paragraphs(body_html)
    return add_paragraph_fingerprints(paragraphs)


def paragraph_fingerprint(text: str) -> str:
    return sha256_text(normalize_plain_text(text).lower())[:16]


def add_paragraph_fingerprints(paragraphs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for index, paragraph in enumerate(paragraphs):
        text = normalize_plain_text(paragraph.get("text") or "")
        previous_text = normalize_plain_text(paragraphs[index - 1].get("text") or "") if index > 0 else ""
        next_text = normalize_plain_text(paragraphs[index + 1].get("text") or "") if index + 1 < len(paragraphs) else ""
        item = dict(paragraph)
        item["fingerprint"] = paragraph_fingerprint(text)
        item["contextFingerprint"] = sha256_text(
            "|".join([paragraph_fingerprint(previous_text), paragraph_fingerprint(text), paragraph_fingerprint(next_text)])
        )[:16]
        item["index"] = index
        out.append(item)
    return out


def aid_anchor_ids(sidecar: dict[str, Any] | None) -> list[tuple[str, str, int]]:
    anchors: list[tuple[str, str, int]] = []
    if not isinstance(sidecar, dict):
        return anchors
    for index, item in enumerate(sidecar.get("plainSignals") or []):
        if isinstance(item, dict) and item.get("paragraphId"):
            anchors.append(("plainSignals", str(item.get("paragraphId")), index))
    for index, item in enumerate(sidecar.get("checkpoints") or []):
        if isinstance(item, dict) and item.get("afterParagraphId"):
            anchors.append(("checkpoints", str(item.get("afterParagraphId")), index))
    return anchors


def analyze_anchor_stability(
    baseline_paragraphs: list[dict[str, Any]],
    draft_paragraphs: list[dict[str, Any]],
    sidecar: dict[str, Any] | None,
) -> dict[str, Any]:
    baseline_by_id = {item["id"]: item for item in baseline_paragraphs}
    draft_by_id = {item["id"]: item for item in draft_paragraphs}
    draft_by_fingerprint: dict[str, list[dict[str, Any]]] = {}
    for item in draft_paragraphs:
        draft_by_fingerprint.setdefault(item["fingerprint"], []).append(item)

    results = []
    blocking = []
    for list_name, anchor_id, index in aid_anchor_ids(sidecar):
        baseline = baseline_by_id.get(anchor_id)
        current = draft_by_id.get(anchor_id)
        if current and baseline and current.get("fingerprint") == baseline.get("fingerprint"):
            status = "unchanged"
            suggestion = None
        elif baseline:
            matches = draft_by_fingerprint.get(baseline.get("fingerprint"), [])
            if len(matches) == 1:
                status = "moved"
                suggestion = matches[0]
            else:
                best = None
                best_score = 0.0
                for candidate in draft_paragraphs:
                    score = difflib.SequenceMatcher(
                        None,
                        normalize_plain_text(baseline.get("text") or "").lower(),
                        normalize_plain_text(candidate.get("text") or "").lower(),
                    ).ratio()
                    if score > best_score:
                        best = candidate
                        best_score = score
                if best and best_score >= 0.72:
                    status = "changed"
                    suggestion = {**best, "confidence": round(best_score, 3)}
                else:
                    status = "missing"
                    suggestion = None
                    blocking.append(f"{list_name}[{index}] references missing paragraph {anchor_id}.")
        elif current:
            status = "unknown-baseline"
            suggestion = None
        else:
            status = "missing"
            suggestion = None
            blocking.append(f"{list_name}[{index}] references missing paragraph {anchor_id}.")
        results.append({
            "list": list_name,
            "index": index,
            "anchorId": anchor_id,
            "status": status,
            "suggestion": suggestion,
        })
    return {
        "anchors": results,
        "blocking": blocking,
        "hasBlockingIssues": bool(blocking),
    }


def diff_sources(before: str, after: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile="published",
            tofile="draft",
            lineterm="",
        )
    )


def semantic_same(before: str, after: str) -> bool:
    def normalize(value: str) -> str:
        value = normalize_newlines(value)
        value = re.sub(r"[ \t]+\n", "\n", value)
        value = re.sub(r"\n{3,}", "\n\n", value)
        return value.strip()

    return normalize(before) == normalize(after)


def current_narrative_paths() -> list[Path]:
    folder = ROOT / narrative_sync.input_folder
    return sorted(folder.glob("*.md"), reverse=True)


def library_documents() -> list[SourceDocument]:
    return [parse_source(path) for path in current_narrative_paths()]


def iso_stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
