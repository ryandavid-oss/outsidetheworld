import argparse
import hashlib
import html
import json
import os
import re
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

# --- CONFIG ---
input_folder = 'current_narrative'
output_file = 'narrative_data.js'
share_output_folder = 'archive'
og_output_folder = 'Images/og/archive'
reading_aids_folder = 'reading_aids'
site_url = 'https://outsidetheworld.com'
READING_AIDS_PREVIEW_ENV = 'OTW_READING_AIDS_PREVIEW'

MONTHS = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12,
}

def slugify(value):
    return re.sub(r'[^a-z0-9]+', '-', str(value or '').lower().replace('&', ' and ')).strip('-')

def build_post_id(post):
    return f"{post.get('date') or 'undated'}--{slugify(post.get('title') or 'untitled')}"

def post_stem(filename):
    return Path(filename).stem

def canonical_share_path(post):
    stem = post_stem(post.get('file') or '')
    return f"{share_output_folder}/{stem}.html" if stem else ''

def canonical_share_url(post):
    share_path = post.get('share_path') or canonical_share_path(post)
    return f"{site_url}/{share_path}" if share_path else site_url

def parse_display_date(value):
    try:
        return datetime.strptime(value, '%B %d, %Y')
    except ValueError:
        return None

def strip_markdown(value):
    text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', value or '')
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[*_`>#-]+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def excerpt(value, limit=180):
    text = strip_markdown(value)
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(' ', 1)[0].rstrip('.,;:') + '...'

def smartypants_safe(value):
    return html.escape(value or '', quote=True)

IMAGE_MARKDOWN_PATTERN = re.compile(r'!\[([^\]]*)\]\((\S+?)(?:\s+"((?:\\"|[^"])*)")?\)')
HTML_IMAGE_PATTERN = re.compile(r'<img\b([^>]*)>', re.I)
HTML_ATTR_PATTERN = re.compile(r'([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*(["\'])(.*?)\2', re.S)
PUBLISHER_METADATA_PATTERN = re.compile(r'<!--\s*otw-publisher\s*([\s\S]*?)\s*-->', re.I)

def markdown_unescape(value):
    return (value or '').replace('\\"', '"').replace('\\[', '[').replace('\\]', ']').replace('\\\\', '\\')

def safe_link_url(value):
    url = str(value or '').strip()
    if re.match(r'^(https?:|mailto:|#|/)', url, re.I):
        return url
    return ''

def safe_image_url(value):
    url = str(value or '').strip()
    if not url:
        return ''

    lower = url.lower()
    if lower.startswith(('javascript:', 'data:', 'blob:', '//')):
        return ''
    if re.match(r'^https?://', url, re.I):
        return url
    if re.match(r'^[a-z][a-z0-9+.-]*:', url, re.I):
        return ''

    path_part = unquote(re.split(r'[?#]', url, maxsplit=1)[0])
    if any(part in ('.', '..') for part in path_part.split('/')):
        return ''

    if url.startswith('/'):
        return url
    if re.search(r'[\s<>]', url):
        return ''
    return f"/{url}"

def normalize_choice(value, allowed, fallback):
    value = str(value or '').strip().lower()
    return value if value in allowed else fallback

def normalize_image_presentation(value):
    value = value or {}
    return {
        'displaySize': normalize_choice(value.get('displaySize'), ['x-small', 'small', 'medium', 'large', 'original'], 'medium'),
        'alignment': normalize_choice(value.get('alignment'), ['left', 'center', 'right'], 'center'),
        'wrapMode': normalize_choice(value.get('wrapMode'), ['none', 'wrap-left', 'wrap-right'], 'none'),
    }

def normalize_publisher_images(metadata):
    images = metadata.get('images') if isinstance(metadata, dict) else []
    blocks = metadata.get('blocks') if isinstance(metadata, dict) else []
    by_url = {}
    by_id = {}

    if not isinstance(images, list):
        images = []
    if not isinstance(blocks, list):
        blocks = []

    for image in images:
        if not isinstance(image, dict):
            continue
        media = image.get('media') if isinstance(image.get('media'), dict) else {}
        url = safe_image_url(image.get('url') or media.get('url') or media.get('publishUrl'))
        if not url:
            continue
        normalized = {
            'id': str(image.get('id') or image.get('imageRef') or ''),
            'url': url,
            'objectKey': str(image.get('objectKey') or media.get('objectKey') or ''),
            'alt': str(image.get('alt') or ''),
            'caption': str(image.get('caption') or ''),
            **normalize_image_presentation(image),
        }
        by_url[url] = normalized
        if normalized['id']:
            by_id[normalized['id']] = normalized

    for block in blocks:
        if not isinstance(block, dict) or block.get('type') != 'image':
            continue
        media = block.get('media') if isinstance(block.get('media'), dict) else {}
        url = safe_image_url(block.get('url') or media.get('url') or media.get('publishUrl'))
        image = by_id.get(str(block.get('imageRef') or block.get('id') or '')) or by_url.get(url)
        if not image and not url:
            continue
        normalized = {
            **(image or {}),
            'id': str(block.get('imageRef') or block.get('id') or (image or {}).get('id') or ''),
            'url': url or image['url'],
            'objectKey': str(block.get('objectKey') or (image or {}).get('objectKey') or ''),
            'alt': str(block.get('alt') or (image or {}).get('alt') or ''),
            'caption': str(block.get('caption') or (image or {}).get('caption') or ''),
            **normalize_image_presentation({**(image or {}), **block}),
        }
        by_url[normalized['url']] = normalized
        if normalized['id']:
            by_id[normalized['id']] = normalized

    return by_url

def normalize_publisher_image_sequence(metadata):
    images = metadata.get('images') if isinstance(metadata, dict) else []
    blocks = metadata.get('blocks') if isinstance(metadata, dict) else []
    by_url = {}
    by_id = {}
    ordered = []

    if not isinstance(blocks, list):
        blocks = []
    if not isinstance(images, list):
        images = []

    for image in images:
        if not isinstance(image, dict):
            continue
        media = image.get('media') if isinstance(image.get('media'), dict) else {}
        url = safe_image_url(image.get('url') or media.get('url') or media.get('publishUrl'))
        if not url:
            continue
        normalized = {
            'id': str(image.get('id') or image.get('imageRef') or ''),
            'url': url,
            'objectKey': str(image.get('objectKey') or media.get('objectKey') or ''),
            'alt': str(image.get('alt') or ''),
            'caption': str(image.get('caption') or ''),
            **normalize_image_presentation(image),
        }
        by_url[url] = normalized
        if normalized['id']:
            by_id[normalized['id']] = normalized

    for block in blocks:
        if not isinstance(block, dict) or block.get('type') != 'image':
            continue
        url = safe_image_url(block.get('url'))
        image = by_id.get(str(block.get('imageRef') or block.get('id') or '')) or by_url.get(url)
        if not image and not url:
            continue
        ordered.append({
            **(image or {}),
            'id': str(block.get('imageRef') or block.get('id') or (image or {}).get('id') or ''),
            'url': url or image['url'],
            'objectKey': str(block.get('objectKey') or (image or {}).get('objectKey') or ''),
            'alt': str(block.get('alt') or (image or {}).get('alt') or ''),
            'caption': str(block.get('caption') or (image or {}).get('caption') or ''),
            **normalize_image_presentation({**(image or {}), **block}),
        })

    return ordered or list(by_url.values())

def sanitize_publisher_image_list(metadata):
    raw_images = metadata.get('images') if isinstance(metadata.get('images'), list) else []
    sanitized_images = []

    for image in raw_images:
        if not isinstance(image, dict):
            continue
        media = image.get('media') if isinstance(image.get('media'), dict) else {}
        url = safe_image_url(image.get('url') or media.get('url') or media.get('publishUrl'))
        if not url:
            continue
        normalized = {
            'id': str(image.get('id') or image.get('imageRef') or '')[:120],
            'url': url,
            'objectKey': str(image.get('objectKey') or media.get('objectKey') or '')[:300],
            'alt': str(image.get('alt') or ''),
            'caption': str(image.get('caption') or ''),
            **normalize_image_presentation(image),
        }
        sanitized_images.append(normalized)

    return sanitized_images

def figure_classes(presentation):
    normalized = normalize_image_presentation(presentation or {})
    return ' '.join([
        'otw-figure',
        f"otw-figure--{normalized['displaySize']}",
        f"otw-figure--align-{normalized['alignment']}",
        f"otw-figure--{normalized['wrapMode']}",
    ])

def render_markdown_image(match, as_block=False, image_metadata=None, image_queue=None):
    alt = markdown_unescape(html.unescape(match.group(1) or ''))
    src = safe_image_url(html.unescape(match.group(2) or ''))
    if not src:
        return ''
    caption = markdown_unescape(html.unescape(match.group(3) or '')).strip()
    if not src:
        return ''
    safe_src = html.escape(src, quote=True)
    metadata = None
    queued = image_queue.get(src) if image_queue else None
    if queued:
        metadata = queued.pop(0)
    elif image_metadata:
        metadata = image_metadata.get(src)
    if metadata:
        alt = metadata.get('alt') or alt
        caption = metadata.get('caption') or caption
    safe_alt = html.escape(alt, quote=True)
    title_attr = f' title="{html.escape(caption, quote=True)}"' if caption else ''
    image_attrs = f'src="{safe_src}" alt="{safe_alt}" loading="lazy" decoding="async"'
    image_html = f'<img {image_attrs}{title_attr}>'
    if as_block and caption:
        safe_caption = html.escape(caption, quote=False)
        classes = figure_classes(metadata) if metadata else 'otw-figure'
        return f'<figure class="{classes}"><img {image_attrs}><figcaption><em>{safe_caption}</em></figcaption></figure>'
    if as_block and metadata:
        classes = figure_classes(metadata)
        return f'<figure class="{classes}"><img {image_attrs}></figure>'
    return image_html

def is_trusted_figure_block(value):
    raw = (value or '').strip()
    lowered = raw.lower()
    return lowered.startswith('<figure') and lowered.endswith('</figure>') and '<script' not in lowered

def sanitize_trusted_html_block(value):
    sanitized = re.sub(r'<\s*(script|iframe|object|embed)\b[\s\S]*?<\s*/\s*\1\s*>', '', value or '', flags=re.I)
    sanitized = re.sub(r'\s+on[a-z0-9_-]+\s*=\s*"[^"]*"', '', sanitized, flags=re.I)
    sanitized = re.sub(r"\s+on[a-z0-9_-]+\s*=\s*'[^']*'", '', sanitized, flags=re.I)
    sanitized = re.sub(r'\s+on[a-z0-9_-]+\s*=\s*[^\s>]+', '', sanitized, flags=re.I)

    def clean_url_attr(match):
        attr = match.group(1)
        quote_char = match.group(2)
        url = match.group(3)
        safe_url = safe_image_url(url) if attr.lower() == 'src' else safe_link_url(url)
        return f' {attr}={quote_char}{html.escape(safe_url, quote=True)}{quote_char}' if safe_url else ''

    sanitized = re.sub(r'\s+(src|href)\s*=\s*(["\'])(.*?)\2', clean_url_attr, sanitized, flags=re.I)
    return sanitized

PUBLISHER_METADATA_VERSIONS = {1, 2}
PUBLISHER_INLINE_TAGS = {'a', 'b', 'br', 'code', 'em', 'font', 'i', 'span', 'strong', 'u'}
PUBLISHER_INLINE_STYLES = {
    'background-color',
    'color',
    'font-style',
    'font-weight',
    'text-decoration',
    'text-decoration-line',
}
PUBLISHER_LINE_SPACING = {
    '1.0': '1',
    '1.15': '1.15',
    '1.5': '1.5',
    '2.0': '2',
}

def safe_visual_style_value(value):
    value = str(value or '').strip()
    if not value:
        return ''
    if re.search(r'(url\s*\(|expression\s*\(|javascript:|data:|blob:)', value, re.I):
        return ''
    return value

def sanitize_publisher_style(value):
    declarations = []
    for declaration in str(value or '').split(';'):
        if ':' not in declaration:
            continue
        prop, raw_value = declaration.split(':', 1)
        prop = prop.strip().lower()
        style_value = safe_visual_style_value(raw_value)
        if prop in PUBLISHER_INLINE_STYLES and style_value:
            declarations.append(f'{prop}: {style_value}')
    return '; '.join(declarations)

class PublisherInlineSanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag not in PUBLISHER_INLINE_TAGS:
            return
        if tag == 'br':
            self.parts.append('<br>')
            return

        attrs_dict = {name.lower(): value for name, value in attrs}
        clean_tag = 'span' if tag == 'font' else tag
        clean_attrs = []
        if tag == 'a':
            href = safe_link_url(attrs_dict.get('href'))
            if href:
                clean_attrs.append(f'href="{html.escape(href, quote=True)}"')
        style_parts = []
        if tag == 'font' and attrs_dict.get('color'):
            color = safe_visual_style_value(attrs_dict.get('color'))
            if color:
                style_parts.append(f'color: {color}')
        style = sanitize_publisher_style(attrs_dict.get('style'))
        if style:
            style_parts.append(style)
        if style_parts:
            clean_attrs.append(f'style="{html.escape("; ".join(style_parts), quote=True)}"')
        attr_text = f' {" ".join(clean_attrs)}' if clean_attrs else ''
        self.parts.append(f'<{clean_tag}{attr_text}>')

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag not in PUBLISHER_INLINE_TAGS or tag == 'br':
            return
        clean_tag = 'span' if tag == 'font' else tag
        self.parts.append(f'</{clean_tag}>')

    def handle_data(self, data):
        self.parts.append(html.escape(data or '', quote=False))

    def get_html(self):
        return ''.join(self.parts).strip()

def sanitize_publisher_inline_html(value):
    parser = PublisherInlineSanitizer()
    try:
        parser.feed(str(value or ''))
        parser.close()
    except Exception:
        return html.escape(str(value or ''), quote=False)
    return parser.get_html()

def normalize_publisher_line_spacing(value):
    value = str(value or '').strip()
    return value if value in PUBLISHER_LINE_SPACING else ''

def publisher_line_spacing_attr(block):
    line_spacing = normalize_publisher_line_spacing((block or {}).get('lineSpacing'))
    if not line_spacing:
        return ''
    return f' style="line-height: {PUBLISHER_LINE_SPACING[line_spacing]};"'

def plain_text_from_html(value):
    text = re.sub(r'<[^>]+>', '', value or '')
    return re.sub(r'\s+', ' ', html.unescape(text)).strip()

def publisher_block_matches_render_type(block, render_type):
    block_type = block.get('type') if isinstance(block, dict) else ''
    if block_type == 'image':
        return render_type == 'image'
    if block_type == 'divider':
        return render_type == 'divider'
    return block_type == render_type

def render_publisher_enhanced_block(render_type, rendered_html, block):
    if not isinstance(block, dict):
        return rendered_html
    block_type = block.get('type')
    if block_type in {'paragraph', 'heading', 'quote'}:
        content = sanitize_publisher_inline_html(block.get('html'))
        if not content:
            content = sanitize_publisher_inline_html(block.get('text'))
        if not content:
            return rendered_html
        style_attr = publisher_line_spacing_attr(block)
        if block_type == 'heading':
            try:
                level = int(block.get('level') or 2)
            except (TypeError, ValueError):
                level = 2
            level = min(6, max(1, level))
            return f'<h{level}{style_attr}>{content}</h{level}>'
        if block_type == 'quote':
            return f'<blockquote{style_attr}>{content}</blockquote>'
        return f'<p{style_attr}>{content}</p>'

    if block_type == 'list':
        items = block.get('items') if isinstance(block.get('items'), list) else []
        if not items:
            return rendered_html
        tag = 'ol' if block.get('ordered') else 'ul'
        class_attr = ' class="otw-list--checklist"' if block.get('checklist') else ''
        style_attr = publisher_line_spacing_attr(block)
        item_html = ''.join(
            f'<li>{sanitize_publisher_inline_html(item.get("html") or item.get("text") or "")}</li>'
            for item in items
            if isinstance(item, dict)
        )
        return f'<{tag}{class_attr}{style_attr}>{item_html}</{tag}>' if item_html else rendered_html

    return rendered_html

def inline_markdown(value, image_metadata=None, image_queue=None):
    value = html.escape(value or '', quote=False)
    value = IMAGE_MARKDOWN_PATTERN.sub(lambda m: render_markdown_image(m, image_metadata=image_metadata, image_queue=image_queue), value)
    value = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        lambda m: f'<a href="{html.escape(safe_link_url(m.group(2)), quote=True)}">{m.group(1)}</a>' if safe_link_url(m.group(2)) else m.group(1),
        value
    )
    value = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', value)
    value = re.sub(r'`([^`]+)`', r'<code>\1</code>', value)
    return value

def markdown_to_html(markdown, publisher_metadata=None):
    image_metadata = normalize_publisher_images(publisher_metadata or {})
    image_queue = {}
    for image in normalize_publisher_image_sequence(publisher_metadata or {}):
        image_queue.setdefault(image.get('url'), []).append(image)
    publisher_blocks = publisher_metadata.get('blocks') if isinstance(publisher_metadata, dict) and isinstance(publisher_metadata.get('blocks'), list) else []
    publisher_block_index = 0
    publisher_subhead = publisher_metadata.get('subhead') if isinstance(publisher_metadata, dict) else ''
    blocks = re.split(r'\n\s*\n', (markdown or '').strip())
    html_blocks = []

    def next_publisher_block(render_type):
        nonlocal publisher_block_index
        while publisher_block_index < len(publisher_blocks):
            block = publisher_blocks[publisher_block_index]
            publisher_block_index += 1
            if publisher_block_matches_render_type(block, render_type):
                return block
        return None

    def append_rendered_block(rendered_html, render_type):
        if render_type == 'paragraph' and publisher_subhead:
            if plain_text_from_html(rendered_html) == re.sub(r'\s+', ' ', str(publisher_subhead)).strip():
                html_blocks.append(rendered_html)
                return
        metadata_block = next_publisher_block(render_type)
        html_blocks.append(render_publisher_enhanced_block(render_type, rendered_html, metadata_block))

    for block in blocks:
        raw = block.strip()
        if not raw:
            continue
        if raw == '---':
            append_rendered_block('<hr>', 'divider')
            continue
        if raw.startswith('<div class="otw-center">') and raw.endswith('</div>'):
            html_blocks.append(sanitize_trusted_html_block(raw))
            continue
        if is_trusted_figure_block(raw):
            append_rendered_block(sanitize_trusted_html_block(raw), 'image')
            continue

        image_match = IMAGE_MARKDOWN_PATTERN.fullmatch(raw)
        if image_match:
            append_rendered_block(render_markdown_image(image_match, as_block=True, image_metadata=image_metadata, image_queue=image_queue), 'image')
            continue

        lines = raw.splitlines()
        if all(re.match(r'^\s*>\s?', line) for line in lines):
            quote = '\n'.join(re.sub(r'^\s*>\s?', '', line) for line in lines)
            rendered = f'<blockquote>{inline_markdown(quote, image_metadata, image_queue).replace(chr(10), "<br>")}</blockquote>'
            append_rendered_block(rendered, 'quote')
            continue
        if all(re.match(r'^\s*[-*]\s+', line) for line in lines):
            item_values = [
                inline_markdown(re.sub(r'^\s*[-*]\s+(?:\[[ xX]\]\s+)?', '', line), image_metadata, image_queue)
                for line in lines
            ]
            items = ''.join(f'<li>{item}</li>' for item in item_values)
            append_rendered_block(f'<ul>{items}</ul>', 'list')
            continue
        if all(re.match(r'^\s*\d+\.\s+', line) for line in lines):
            item_values = [
                inline_markdown(re.sub(r'^\s*\d+\.\s+', '', line), image_metadata, image_queue)
                for line in lines
            ]
            items = ''.join(f'<li>{item}</li>' for item in item_values)
            append_rendered_block(f'<ol>{items}</ol>', 'list')
            continue
        heading_match = re.match(r'^(#{2,6})\s+(.+)$', raw)
        if heading_match:
            level = len(heading_match.group(1))
            rendered = f'<h{level}>{inline_markdown(heading_match.group(2).strip(), image_metadata, image_queue)}</h{level}>'
            append_rendered_block(rendered, 'heading')
            continue

        emphasis_match = re.match(r'^\s*(?:_([^_\n]+)_|\*([^*\n]+)\*)\s*$', raw)
        if emphasis_match:
            emphasized = emphasis_match.group(1) or emphasis_match.group(2) or ''
            append_rendered_block(f'<p><em>{inline_markdown(emphasized, image_metadata, image_queue)}</em></p>', 'paragraph')
        else:
            append_rendered_block(f'<p>{inline_markdown(raw, image_metadata, image_queue).replace(chr(10), "<br>")}</p>', 'paragraph')

    return '\n'.join(html_blocks)

def sanitize_publisher_metadata(metadata):
    if not isinstance(metadata, dict) or metadata.get('schema') != 'otw.publisher.post':
        return {}
    try:
        version = int(metadata.get('version') or 0)
    except (TypeError, ValueError):
        return {}
    if version not in PUBLISHER_METADATA_VERSIONS:
        return {}

    images = sanitize_publisher_image_list(metadata)
    blocks = []
    raw_blocks = metadata.get('blocks') if isinstance(metadata.get('blocks'), list) else []

    for block in raw_blocks:
        if not isinstance(block, dict):
            continue
        block_type = normalize_choice(
            block.get('type'),
            ['paragraph', 'heading', 'quote', 'divider', 'list', 'image', 'raw'],
            ''
        )
        if not block_type:
            continue

        sanitized = {
            'id': str(block.get('id') or '')[:120],
            'type': block_type,
        }
        if block_type == 'image':
            url = safe_image_url(block.get('url'))
            image_ref = str(block.get('imageRef') or block.get('id') or '')[:120]
            if image_ref:
                sanitized['imageRef'] = image_ref
            if url:
                sanitized['url'] = url
            object_key = str(block.get('objectKey') or '')[:300]
            if object_key:
                sanitized['objectKey'] = object_key
            sanitized.update(normalize_image_presentation(block))
        elif block_type == 'heading':
            try:
                level = int(block.get('level') or 2)
            except (TypeError, ValueError):
                level = 2
            sanitized['level'] = min(6, max(1, level))
            html_value = sanitize_publisher_inline_html(block.get('html'))
            text_value = str(block.get('text') or '')
            line_spacing = normalize_publisher_line_spacing(block.get('lineSpacing'))
            if html_value:
                sanitized['html'] = html_value
            if text_value:
                sanitized['text'] = text_value
            if line_spacing:
                sanitized['lineSpacing'] = line_spacing
        elif block_type in {'paragraph', 'quote'}:
            html_value = sanitize_publisher_inline_html(block.get('html'))
            text_value = str(block.get('text') or '')
            line_spacing = normalize_publisher_line_spacing(block.get('lineSpacing'))
            if html_value:
                sanitized['html'] = html_value
            if text_value:
                sanitized['text'] = text_value
            if line_spacing:
                sanitized['lineSpacing'] = line_spacing
        elif block_type == 'list':
            sanitized['ordered'] = bool(block.get('ordered'))
            sanitized['checklist'] = bool(block.get('checklist'))
            line_spacing = normalize_publisher_line_spacing(block.get('lineSpacing'))
            if line_spacing:
                sanitized['lineSpacing'] = line_spacing
            raw_items = block.get('items') if isinstance(block.get('items'), list) else []
            items = []
            for item in raw_items:
                if not isinstance(item, dict):
                    continue
                item_html = sanitize_publisher_inline_html(item.get('html'))
                item_text = str(item.get('text') or '')
                item_metadata = {'id': str(item.get('id') or '')[:120]}
                if item_html:
                    item_metadata['html'] = item_html
                if item_text:
                    item_metadata['text'] = item_text
                if item_metadata.get('html') or item_metadata.get('text'):
                    items.append(item_metadata)
            if items:
                sanitized['items'] = items
        blocks.append(sanitized)

    cleaned = {
        'schema': 'otw.publisher.post',
        'version': version,
        'source': 'publisher.html',
        'subhead': str(metadata.get('subhead') or ''),
        'blocks': blocks,
        'images': images,
    }
    if version >= 2:
        cleaned['formatting'] = {
            'mode': 'otw-enhanced-markdown',
            'version': 1,
            'fallback': 'markdown',
        }
    return cleaned

def extract_publisher_metadata(body):
    match = PUBLISHER_METADATA_PATTERN.search(body or '')
    if not match:
        return {}, body
    try:
        metadata = json.loads(match.group(1))
        metadata = sanitize_publisher_metadata(metadata)
    except json.JSONDecodeError:
        metadata = {}
    cleaned = PUBLISHER_METADATA_PATTERN.sub('', body or '', count=1).strip()
    return metadata, cleaned

def absolute_url(path):
    if not path:
        return ''
    if re.match(r'^https?://', path):
        return path
    return f"{site_url}/{path.lstrip('/')}"

def html_attrs(value):
    return {
        match.group(1).lower(): html.unescape(match.group(3) or '')
        for match in HTML_ATTR_PATTERN.finditer(value or '')
    }

def image_mime_type(url):
    path = re.sub(r'[?#].*$', '', str(url or '')).lower()
    if path.endswith(('.jpg', '.jpeg')):
        return 'image/jpeg'
    if path.endswith('.png'):
        return 'image/png'
    if path.endswith('.webp'):
        return 'image/webp'
    if path.endswith('.gif'):
        return 'image/gif'
    return ''

def first_article_image(post):
    metadata = post.get('publisher') if isinstance(post.get('publisher'), dict) else {}

    for image in normalize_publisher_image_sequence(metadata):
        url = safe_image_url(image.get('url'))
        if not url:
            continue
        return {
            'url': absolute_url(url),
            'alt': image.get('alt') or image.get('caption') or f"{post.get('title') or 'Outside The World'} article image",
            'type': image_mime_type(url),
            'width': '',
            'height': '',
        }

    body = post.get('body') or ''
    body_images = [
        (match.start(), 'markdown', match)
        for match in IMAGE_MARKDOWN_PATTERN.finditer(body)
    ] + [
        (match.start(), 'html', match)
        for match in HTML_IMAGE_PATTERN.finditer(body)
    ]

    for _, image_type, match in sorted(body_images, key=lambda item: item[0]):
        if image_type == 'markdown':
            url = safe_image_url(html.unescape(match.group(2) or ''))
            if not url:
                continue
            alt = markdown_unescape(html.unescape(match.group(1) or '')).strip()
            caption = markdown_unescape(html.unescape(match.group(3) or '')).strip()
            image_alt = alt or caption
        else:
            attrs = html_attrs(match.group(1))
            url = safe_image_url(attrs.get('src'))
            if not url:
                continue
            image_alt = str(attrs.get('alt') or attrs.get('title') or '').strip()

        return {
            'url': absolute_url(url),
            'alt': image_alt or f"{post.get('title') or 'Outside The World'} article image",
            'type': image_mime_type(url),
            'width': '',
            'height': '',
        }

    return None

def archive_card_image(post, stem):
    return {
        'url': f"{site_url}/{og_output_folder}/{stem}.png",
        'alt': f"{post.get('title') or 'Outside The World'} — Outside The World archive card",
        'type': 'image/png',
        'width': '1200',
        'height': '630',
    }

def preview_image_meta_tags(preview_image):
    tags = [
        f'<meta property="og:image" content="{smartypants_safe(preview_image["url"])}" />',
        f'<meta property="og:image:secure_url" content="{smartypants_safe(preview_image["url"])}" />',
    ]
    if preview_image.get('type'):
        tags.append(f'<meta property="og:image:type" content="{smartypants_safe(preview_image["type"])}" />')
    if preview_image.get('width'):
        tags.append(f'<meta property="og:image:width" content="{smartypants_safe(preview_image["width"])}" />')
    if preview_image.get('height'):
        tags.append(f'<meta property="og:image:height" content="{smartypants_safe(preview_image["height"])}" />')
    tags.append(f'<meta property="og:image:alt" content="{smartypants_safe(preview_image["alt"])}" />')
    return '\n    '.join(tags)

def normalize_plain_text(value):
    return re.sub(r'\s+', ' ', html.unescape(value or '')).strip()

def publisher_subhead(post):
    metadata = post.get('publisher') if isinstance(post.get('publisher'), dict) else {}
    return normalize_plain_text(str(metadata.get('subhead') or ''))

def markdown_without_leading_deck(markdown, deck):
    if not deck:
        return markdown or ''
    blocks = re.split(r'\n\s*\n', (markdown or '').strip())
    if blocks and normalize_plain_text(strip_markdown(blocks[0])) == normalize_plain_text(deck):
        return '\n\n'.join(blocks[1:]).strip()
    return markdown or ''

def reader_description(post, deck):
    if deck:
        return deck
    return excerpt(markdown_without_leading_deck(post.get('body') or '', deck))

def article_plain_text(post, deck):
    body = markdown_without_leading_deck(post.get('body') or '', deck)
    return strip_markdown(body)

def article_word_count(post, deck):
    text = article_plain_text(post, deck)
    return len(re.findall(r"[A-Za-z0-9]+(?:[’'][A-Za-z0-9]+)?", text))

def article_read_minutes(word_count):
    return max(1, (word_count + 224) // 225)

def essay_slug_from_stem(stem):
    return re.sub(r'^\d{4}-\d{2}-\d{2}-', '', stem or '')

def essay_slug_from_post(post):
    return essay_slug_from_stem(post_stem(post.get('file') or ''))

def reading_aid_path_for_slug(slug):
    return Path(reading_aids_folder) / f"{slug}.json"

def reading_aid_path_for_post(post):
    return reading_aid_path_for_slug(essay_slug_from_post(post))

def essay_source_path(post):
    filename = post.get('file') or ''
    return Path(input_folder) / filename if filename else None

def essay_hash_for_post(post):
    path = essay_source_path(post)
    if not path or not path.exists():
        return ''
    return hashlib.sha256(path.read_bytes()).hexdigest()

def should_assign_paragraph_id(paragraph_html):
    if re.search(r'<\s*(img|figure|pre|script|iframe|object|embed)\b', paragraph_html or '', flags=re.I):
        return False
    paragraph_text = normalize_plain_text(plain_text_from_html(paragraph_html))
    return bool(paragraph_text)

def assign_reader_paragraph_ids(body_html):
    paragraph_index = 0

    def replace_paragraph(match):
        nonlocal paragraph_index
        opening_tag = match.group(2)
        paragraph_html = match.group(3)
        if not should_assign_paragraph_id(paragraph_html):
            return match.group(0)

        paragraph_index += 1
        paragraph_id = f"p-{paragraph_index:03d}"
        if re.search(r'\bid\s*=', opening_tag, flags=re.I):
            opening_tag = re.sub(
                r'\bid\s*=\s*(["\'])(.*?)\1',
                f'id="{paragraph_id}"',
                opening_tag,
                count=1,
                flags=re.I,
            )
        else:
            opening_tag = opening_tag[:-1] + f' id="{paragraph_id}">'
        return ''.join([match.group(1), opening_tag, paragraph_html, match.group(4)])

    return re.sub(r'(\s*)(<p\b[^>]*>)([\s\S]*?)(</p>)', replace_paragraph, body_html or '', flags=re.I)

def extract_reader_paragraphs(body_html):
    paragraphs = []
    for match in re.finditer(r'<p\b([^>]*)>([\s\S]*?)</p>', body_html or '', flags=re.I):
        attrs = html_attrs(match.group(1))
        paragraph_id = attrs.get('id')
        if not paragraph_id:
            continue
        text = normalize_plain_text(plain_text_from_html(match.group(2)))
        if text:
            paragraphs.append({
                'id': paragraph_id,
                'text': text,
                'word_count': len(re.findall(r"[A-Za-z0-9]+(?:[’'][A-Za-z0-9]+)?", text)),
            })
    return paragraphs

def render_reader_body_html(post, deck=None):
    resolved_deck = publisher_subhead(post) if deck is None else deck
    body_html = enhance_reader_body_html(markdown_to_html(post.get('body') or '', post.get('publisher')), resolved_deck)
    return assign_reader_paragraph_ids(body_html)

def reading_aids_preview_enabled():
    return str(os.environ.get(READING_AIDS_PREVIEW_ENV) or '').strip().lower() in {'1', 'true', 'yes', 'on'}

def validate_text_field(value, label, max_length, errors):
    text = str(value or '').strip()
    if not text:
        errors.append(f"{label} is empty.")
    if len(text) > max_length:
        errors.append(f"{label} is too long ({len(text)} characters, max {max_length}).")

def validate_locked_flag(item, label, errors):
    if 'locked' in item and not isinstance(item.get('locked'), bool):
        errors.append(f"{label}.locked must be true or false.")

def validate_allowed_keys(item, allowed, label, errors):
    extra = sorted(set(item.keys()) - set(allowed))
    if extra:
        errors.append(f"{label} has unsupported fields: {', '.join(extra)}.")

def validate_reading_aids(aids, slug, paragraph_ids, essay_hash=''):
    errors = []
    warnings = []
    if not isinstance(aids, dict):
        return ["Reading aid sidecar must be a JSON object."], warnings

    validate_allowed_keys(
        aids,
        {'slug', 'essayHash', 'reviewStatus', 'generatedAt', 'approvedAt', 'model', 'signalBrief', 'readerMap', 'checkpoints', 'plainSignals'},
        'sidecar',
        errors,
    )

    if aids.get('slug') != slug:
        errors.append(f"slug mismatch: expected {slug}, found {aids.get('slug')!r}.")
    if aids.get('reviewStatus') not in {'draft', 'approved'}:
        errors.append("reviewStatus must be draft or approved.")
    if not aids.get('essayHash'):
        errors.append("essayHash is required.")
    elif essay_hash and aids.get('essayHash') != essay_hash:
        warnings.append("essayHash is stale for the current essay source.")

    signal_brief = aids.get('signalBrief')
    if signal_brief is not None:
        if not isinstance(signal_brief, dict):
            errors.append("signalBrief must be an object.")
        else:
            validate_allowed_keys(signal_brief, {'text', 'locked'}, 'signalBrief', errors)
            validate_text_field(signal_brief.get('text'), 'signalBrief.text', 1400, errors)
            validate_locked_flag(signal_brief, 'signalBrief', errors)

    reader_map = aids.get('readerMap') or []
    if not isinstance(reader_map, list):
        errors.append("readerMap must be a list.")
    else:
        for index, item in enumerate(reader_map):
            label = f"readerMap[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} must be an object.")
                continue
            validate_allowed_keys(item, {'label', 'title', 'summary', 'locked'}, label, errors)
            validate_text_field(item.get('label'), f"{label}.label", 40, errors)
            validate_text_field(item.get('title'), f"{label}.title", 180, errors)
            validate_text_field(item.get('summary'), f"{label}.summary", 600, errors)
            validate_locked_flag(item, label, errors)

    checkpoint_ids = set()
    checkpoints = aids.get('checkpoints') or []
    if not isinstance(checkpoints, list):
        errors.append("checkpoints must be a list.")
    else:
        for index, item in enumerate(checkpoints):
            label = f"checkpoints[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} must be an object.")
                continue
            validate_allowed_keys(item, {'afterParagraphId', 'label', 'text', 'locked'}, label, errors)
            paragraph_id = item.get('afterParagraphId')
            if not paragraph_id:
                errors.append(f"{label}.afterParagraphId is required.")
            elif paragraph_id not in paragraph_ids:
                errors.append(f"{label}.afterParagraphId references missing paragraph {paragraph_id}.")
            elif paragraph_id in checkpoint_ids:
                errors.append(f"{label}.afterParagraphId duplicates {paragraph_id}.")
            checkpoint_ids.add(paragraph_id)
            validate_text_field(item.get('label'), f"{label}.label", 80, errors)
            validate_text_field(item.get('text'), f"{label}.text", 800, errors)
            validate_locked_flag(item, label, errors)

    plain_signal_ids = set()
    plain_signals = aids.get('plainSignals') or []
    if not isinstance(plain_signals, list):
        errors.append("plainSignals must be a list.")
    else:
        for index, item in enumerate(plain_signals):
            label = f"plainSignals[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} must be an object.")
                continue
            validate_allowed_keys(item, {'paragraphId', 'label', 'text', 'locked'}, label, errors)
            paragraph_id = item.get('paragraphId')
            if not paragraph_id:
                errors.append(f"{label}.paragraphId is required.")
            elif paragraph_id not in paragraph_ids:
                errors.append(f"{label}.paragraphId references missing paragraph {paragraph_id}.")
            elif paragraph_id in plain_signal_ids:
                errors.append(f"{label}.paragraphId duplicates {paragraph_id}.")
            plain_signal_ids.add(paragraph_id)
            validate_text_field(item.get('label'), f"{label}.label", 80, errors)
            validate_text_field(item.get('text'), f"{label}.text", 800, errors)
            validate_locked_flag(item, label, errors)

    return errors, warnings

def load_reading_aids_for_post(post, paragraph_ids, include_drafts=False):
    path = reading_aid_path_for_post(post)
    if not path.exists():
        return None

    slug = essay_slug_from_post(post)
    try:
        aids = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        print(f"WARNING: Skipping reading aids for {slug}: invalid JSON ({exc}).")
        return None

    essay_hash = essay_hash_for_post(post)
    errors, warnings = validate_reading_aids(aids, slug, paragraph_ids, essay_hash)
    for warning in warnings:
        print(f"WARNING: {slug}: {warning}")
    if errors:
        print(f"WARNING: Skipping reading aids for {slug}: {'; '.join(errors)}")
        return None

    if aids.get('reviewStatus') != 'approved' and not include_drafts:
        return None
    if aids.get('essayHash') != essay_hash and not include_drafts:
        print(f"WARNING: Skipping stale approved reading aids for {slug}.")
        return None
    return aids

def render_reading_aids_intro(aids):
    if not aids:
        return ''

    pieces = ['<section class="reading-aids" id="reading-aids-panel" aria-label="Reading aids">']
    if aids.get('reviewStatus') == 'draft':
        pieces.append('<p class="reading-aids__draft">Draft reading aids visible in local preview.</p>')
    pieces.append(
        '<p class="reading-aids__disclosure">'
        'Reading tools are AI-assisted. They are provided to help readers navigate the essay. '
        'They may not perfectly reflect the author&rsquo;s intent, beliefs, or emphasis. '
        'The essay itself remains the source text.'
        '</p>'
    )

    controls = []
    panels = []
    signal_brief = aids.get('signalBrief') if isinstance(aids.get('signalBrief'), dict) else None
    if signal_brief and signal_brief.get('text'):
        controls.append(
            '''<button type="button" class="reading-aid-tool reading-aid-tool--summary" aria-expanded="false" aria-controls="reading-aid-summary" data-reader-aid-toggle>
                    <span class="reading-aid-tool__icon" aria-hidden="true">I</span>
                    <span>Article Summary</span>
                </button>'''
        )
        panels.append(
            f'''<div class="reading-aid-panel reading-aid-panel--summary" id="reading-aid-summary" hidden>
                    <p>{html.escape(str(signal_brief.get('text') or ''), quote=False)}</p>
                </div>'''
        )

    reader_map = aids.get('readerMap') if isinstance(aids.get('readerMap'), list) else []
    if reader_map:
        map_items = []
        for item in reader_map:
            if not isinstance(item, dict):
                continue
            item_label = html.escape(str(item.get('label') or ''), quote=False)
            item_title = html.escape(str(item.get('title') or ''), quote=False)
            item_summary = html.escape(str(item.get('summary') or ''), quote=False)
            map_items.append(
                f'''<li>
                        <div class="reading-aid-map__header">
                            <span class="reading-aid-map__label">{item_label}</span>
                            <strong>{item_title}</strong>
                        </div>
                        <p>{item_summary}</p>
                    </li>'''
            )
        if map_items:
            controls.append(
                '''<button type="button" class="reading-aid-tool reading-aid-tool--map" aria-expanded="false" aria-controls="reading-aid-map" data-reader-aid-toggle>
                        <span class="reading-aid-tool__icon" aria-hidden="true">II</span>
                        <span>Reader Map</span>
                    </button>'''
            )
            panels.append(
                f'''<div class="reading-aid-panel reading-aid-panel--map" id="reading-aid-map" hidden>
                        <ol class="reading-aid-map">{''.join(map_items)}</ol>
                    </div>'''
            )

    if controls:
        pieces.append(f'''<div class="reading-aid-tools" role="group" aria-label="Reader tools">{''.join(controls)}</div>''')
    if panels:
        pieces.append(f'''<div class="reading-aid-panels">{''.join(panels)}</div>''')

    pieces.append('</section>')
    return '\n'.join(pieces)

def render_clarify_note(paragraph_id, item):
    control_id = f"clarify-{paragraph_id}"
    return f'''<div class="clarify-note" data-clarify-note>
                <button type="button" class="clarify-note__toggle" aria-expanded="false" aria-controls="{control_id}" data-clarify-toggle>Clarify</button>
                <div class="clarify-note__panel" id="{control_id}" hidden>
                    <p>{html.escape(str(item.get('text') or ''), quote=False)}</p>
                </div>
            </div>'''

def render_checkpoint(item):
    return f'''<details class="reading-checkpoint">
                <summary>Where We Are</summary>
                <div class="reading-checkpoint__panel">
                    <p>{html.escape(str(item.get('text') or ''), quote=False)}</p>
                </div>
            </details>'''

def inject_reading_aid_body_notes(body_html, aids):
    if not aids:
        return body_html

    plain_signals = {
        item.get('paragraphId'): item
        for item in aids.get('plainSignals') or []
        if isinstance(item, dict) and item.get('paragraphId')
    }
    checkpoints = {
        item.get('afterParagraphId'): item
        for item in aids.get('checkpoints') or []
        if isinstance(item, dict) and item.get('afterParagraphId')
    }

    def replace_paragraph(match):
        attrs = html_attrs(match.group(1))
        paragraph_id = attrs.get('id')
        paragraph_block = match.group(0)
        if not paragraph_id:
            return paragraph_block
        if paragraph_id in plain_signals:
            paragraph_block = (
                f'<div class="reading-aid-anchor" id="aid-anchor-{paragraph_id}">'
                f'{paragraph_block}'
                f'{render_clarify_note(paragraph_id, plain_signals[paragraph_id])}'
                '</div>'
            )
        if paragraph_id in checkpoints:
            paragraph_block += '\n' + render_checkpoint(checkpoints[paragraph_id])
        return paragraph_block

    return re.sub(r'<p\b([^>]*)>[\s\S]*?</p>', replace_paragraph, body_html or '', flags=re.I)

def add_classes_to_tag(opening_tag, classes):
    class_text = ' '.join(classes)
    class_match = re.search(r'\bclass\s*=\s*(["\'])(.*?)\1', opening_tag, flags=re.I)
    if class_match:
        existing_classes = class_match.group(2).strip()
        merged_classes = f"{existing_classes} {class_text}".strip()
        return opening_tag[:class_match.start(2)] + merged_classes + opening_tag[class_match.end(2):]
    return opening_tag[:-1] + f' class="{class_text}">'

def remove_leading_duplicate_deck_html(body_html, deck):
    if not deck:
        return body_html
    first_block = re.match(r'\s*<p\b[^>]*>[\s\S]*?</p>\s*', body_html or '', flags=re.I)
    if not first_block:
        return body_html
    if normalize_plain_text(plain_text_from_html(first_block.group(0))) == normalize_plain_text(deck):
        return (body_html or '')[first_block.end():].lstrip()
    return body_html

def enhance_reader_body_html(body_html, deck):
    body_html = remove_leading_duplicate_deck_html(body_html, deck)
    first_paragraph = None
    for paragraph in re.finditer(r'(\s*)(<p\b[^>]*>)([\s\S]*?)(</p>)', body_html or '', flags=re.I):
        paragraph_html = paragraph.group(3)
        if re.search(r'<\s*(img|figure|pre|code)\b', paragraph_html, flags=re.I):
            continue
        paragraph_text = normalize_plain_text(plain_text_from_html(paragraph_html))
        if len(paragraph_text) >= 80:
            first_paragraph = paragraph
            break

    if not first_paragraph:
        return body_html

    paragraph_html = first_paragraph.group(3)
    if re.search(r'<\s*(img|figure|pre|code)\b', paragraph_html, flags=re.I):
        return body_html

    paragraph_text = normalize_plain_text(plain_text_from_html(paragraph_html))
    classes = ['entry-body__opening']
    if len(paragraph_text) >= 180 and len(paragraph_text.split()) >= 32:
        classes.append('entry-body__dropcap')

    opening_tag = add_classes_to_tag(first_paragraph.group(2), classes)
    enhanced = ''.join([
        first_paragraph.group(1),
        opening_tag,
        first_paragraph.group(3),
        first_paragraph.group(4),
    ])
    return ''.join([
        (body_html or '')[:first_paragraph.start()],
        enhanced,
        (body_html or '')[first_paragraph.end():],
    ])

def archive_relative_href(post):
    return f"{post_stem(post.get('file') or '')}.html"

def render_reader_nav(newer_post=None, older_post=None):
    items = []
    if newer_post:
        items.append(
            f'''<a class="reader-nav-card reader-nav-card--newer" href="{archive_relative_href(newer_post)}">
                    <span class="reader-nav-label">Newer Essay</span>
                    <span class="reader-nav-title">{smartypants_safe(newer_post.get('title'))}</span>
                </a>'''
        )
    if older_post:
        items.append(
            f'''<a class="reader-nav-card reader-nav-card--older" href="{archive_relative_href(older_post)}">
                    <span class="reader-nav-label">Older Essay</span>
                    <span class="reader-nav-title">{smartypants_safe(older_post.get('title'))}</span>
                </a>'''
        )
    if not items:
        return ''
    return f'''<nav class="reader-nav" aria-label="Adjacent essays">
                {''.join(items)}
            </nav>'''

def find_font(candidates):
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return None

def wrap_draw_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    line = ''
    for word in words:
        candidate = f"{line} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def generate_og_image(post, og_path):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print('WARNING: Pillow is not installed. Skipping generated OG cards.')
        return False

    og_path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1200, 630
    img = Image.new('RGB', (width, height), '#070707')
    draw = ImageDraw.Draw(img)

    # Atmospheric void with restrained OTW color fields.
    for y in range(height):
        shade = int(7 + (y / height) * 8)
        draw.line([(0, y), (width, y)], fill=(shade, shade, shade + 2))
    for radius, alpha in [(620, 42), (430, 28), (280, 24)]:
        box = (740 - radius, 100 - radius, 740 + radius, 100 + radius)
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay)
        odraw.ellipse(box, fill=(155, 89, 182, alpha))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)

    title_font_path = find_font([
        '/System/Library/Fonts/SFNS.ttf',
        '/System/Library/Fonts/HelveticaNeue.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    ])
    mono_font_path = find_font([
        '/System/Library/Fonts/SFNSMono.ttf',
        '/System/Library/Fonts/Menlo.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
    ])
    title_font = ImageFont.truetype(title_font_path, 92) if title_font_path else ImageFont.load_default()
    meta_font = ImageFont.truetype(mono_font_path, 24) if mono_font_path else ImageFont.load_default()
    small_font = ImageFont.truetype(mono_font_path, 20) if mono_font_path else ImageFont.load_default()

    draw.rectangle((76, 72, width - 76, height - 72), outline=(32, 48, 50), width=2)
    draw.text((104, 102), 'OUTSIDE THE WORLD', fill=(99, 149, 238), font=meta_font)
    draw.text((104, 146), f"TEMPORAL_MARK: {post['date'].upper()}", fill=(145, 175, 179), font=small_font)

    y = 250
    for line in wrap_draw_text(draw, post['title'], title_font, 940)[:3]:
        draw.text(
            (104, y),
            line,
            fill=(245, 247, 250),
            font=title_font,
            stroke_width=2,
            stroke_fill=(245, 247, 250),
        )
        y += 98

    draw.text((104, height - 122), 'SHAREABLE_ARCHIVE_SIGNAL', fill=(145, 175, 179), font=small_font)
    draw.text((width - 352, height - 122), 'outsidetheworld.com', fill=(224, 191, 184), font=small_font)
    img.save(og_path, 'PNG', optimize=True)
    return True

def render_share_page(post, newer_post=None, older_post=None, include_draft_reading_aids=False):
    stem = post_stem(post['file'])
    share_path = f"{share_output_folder}/{stem}.html"
    share_url = canonical_share_url({**post, 'share_path': share_path})
    archive_url = "../residue_archive.html"
    preview_image = first_article_image(post) or archive_card_image(post, stem)
    og_image = preview_image['url']
    og_image_tags = preview_image_meta_tags(preview_image)
    deck = publisher_subhead(post)
    deck_html = f'\n                <p class="entry-deck">{smartypants_safe(deck)}</p>' if deck else ''
    description = reader_description(post, deck)
    published = parse_display_date(post['date'])
    published_meta = f'<meta property="article:published_time" content="{published.date().isoformat()}" />' if published else ''
    word_count = article_word_count(post, deck)
    read_minutes = article_read_minutes(word_count)
    body_html = render_reader_body_html(post, deck)
    paragraph_ids = {paragraph['id'] for paragraph in extract_reader_paragraphs(body_html)}
    reading_aids = load_reading_aids_for_post(post, paragraph_ids, include_draft_reading_aids)
    reading_aids_intro = render_reading_aids_intro(reading_aids)
    reading_aids_block = f'\n            {reading_aids_intro}' if reading_aids_intro else ''
    reading_tools_toggle = (
        '<button type="button" class="share-btn reading-tools-toggle" '
        'aria-pressed="false" aria-controls="reading-aids-panel" '
        'data-reading-tools-toggle>Show Reading Tools</button>'
    ) if reading_aids else ''
    reading_tools_control = (
        f'''
                        <span class="reading-tools-control">
                            {reading_tools_toggle}
                        </span>'''
    ) if reading_tools_toggle else ''
    body_reading_tools_attr = ' data-reading-tools="off"' if reading_aids else ''
    body_html = inject_reading_aid_body_notes(body_html, reading_aids)
    reader_nav = render_reader_nav(newer_post, older_post)

    return f'''<!DOCTYPE html>
<html lang="en" data-reader-mode="dark">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <title>{smartypants_safe(post['title'])} | Outside The World</title>
    <link rel="canonical" href="{share_url}" />
    <link href="../favicon.svg" rel="icon" type="image/svg+xml" />
    <link href="../theme.css" rel="stylesheet" />
    <script>
        (function() {{
            try {{
                var storedMode = window.localStorage && window.localStorage.getItem('otw_archive_reader_mode');
                if (storedMode === 'dark' || storedMode === 'light') {{
                    document.documentElement.setAttribute('data-reader-mode', storedMode);
                }}
            }} catch (error) {{}}
        }}());
    </script>
    <link href="../archive_reader.css" rel="stylesheet" />
    <meta name="description" content="{smartypants_safe(description)}" />
    <meta name="theme-color" content="#060809" />
    <meta property="og:site_name" content="Outside The World" />
    <meta property="og:type" content="article" />
    <meta property="og:locale" content="en_US" />
    <meta property="og:title" content="{smartypants_safe(post['title'])}" />
    <meta property="og:description" content="{smartypants_safe(description)}" />
    <meta property="og:url" content="{share_url}" />
    {og_image_tags}
    {published_meta}
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{smartypants_safe(post['title'])}" />
    <meta name="twitter:description" content="{smartypants_safe(description)}" />
    <meta name="twitter:image" content="{smartypants_safe(og_image)}" />
    <script src="../archive_reader.js?v=20260609-share-fallback" defer></script>
</head>
<body class="archive-reader-page"{body_reading_tools_attr}>
    <main class="archive-reader">
        <article class="reader-card" aria-labelledby="entry-title">
            <div class="reader-chrome">
                <div class="reader-mode-toggle" role="group" aria-label="Reader mode">
                    <button class="reader-mode-button" type="button" data-reader-mode-option="dark" aria-pressed="true">Dark</button>
                    <button class="reader-mode-button" type="button" data-reader-mode-option="light" aria-pressed="false">Light</button>
                </div>
            </div>
            <header class="entry-header">
                <p class="entry-label">Narrative Archive</p>
                <h1 class="entry-title" id="entry-title">{smartypants_safe(post['title'])}</h1>{deck_html}
                <div class="entry-meta-strip" aria-label="Essay details">
                    <span class="entry-meta-item"><strong>Filed</strong> {smartypants_safe(post['date'])}</span>
                    <span class="entry-meta-item"><strong>Words</strong> {word_count:,}</span>
                    <span class="entry-meta-item"><strong>Read</strong> {read_minutes} min</span>
                    <span class="entry-meta-actions">{reading_tools_control}
                        <span class="share-controls">
                            <button type="button" class="share-btn" data-share-button>COPY / SHARE LINK</button>
                            <span class="share-status" id="share-status" aria-live="polite"></span>
                        </span>
                    </span>
                </div>
            </header>{reading_aids_block}
            <div class="entry-body">
{body_html}
            </div>
            {reader_nav}
            <div class="archive-actions">
                <a class="archive-link" href="{archive_url}">OPEN ARCHIVE MATRIX</a>
                <a class="archive-link" href="../personal.html">RETURN TO OTW</a>
            </div>
        </article>
        <footer class="archive-legal">
            <a href="../privacy.html">Privacy</a>
            <span aria-hidden="true">&nbsp;|&nbsp;</span>
            <a href="../terms.html">Terms</a>
            <span aria-hidden="true">&nbsp;|&nbsp;</span>
            <a href="../trademarks.html">Trademarks</a>
            <span aria-hidden="true">&nbsp;|&nbsp;</span>
            <a href="../support.html">Support</a>
            <div class="archive-legal-brand">© 2026 Outside the World is New, LLC. Outside The World is a claimed brand identifier.</div>
        </footer>
    </main>
</body>
</html>
'''

def write_share_pages(posts, include_draft_reading_aids=False):
    Path(share_output_folder).mkdir(parents=True, exist_ok=True)
    Path(og_output_folder).mkdir(parents=True, exist_ok=True)

    for index, post in enumerate(posts):
        stem = post_stem(post['file'])
        post['post_id'] = build_post_id(post)
        post['share_path'] = canonical_share_path(post)
        post['og_image'] = f"{og_output_folder}/{stem}.png"

        share_file = Path(post['share_path'])
        newer_post = posts[index - 1] if index > 0 else None
        older_post = posts[index + 1] if index < len(posts) - 1 else None
        share_file.write_text(
            render_share_page(post, newer_post, older_post, include_draft_reading_aids),
            encoding='utf-8',
        )
        og_path = Path(post['og_image'])
        if not og_path.exists() or os.environ.get('OTW_REGENERATE_OG') == '1':
            generate_og_image(post, og_path)

def load_posts():
    posts = []
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)

    files = [f for f in os.listdir(input_folder) if f.endswith('.md')]
    print(f"UPLINK_SYNC: Processing {len(files)} entries...")

    for filename in files:
        file_path = os.path.join(input_folder, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if len(lines) < 2:
                continue

            # 1. Target the top two lines specifically
            # Line 0 is the Title, Line 1 is the Date
            title = lines[0].replace('#', '').strip()
            date_str = lines[1].replace('Date:', '').replace('###', '').strip()

            # 2. Preserve EVERYTHING from line 2 (the 3rd line) onward
            # This keeps your spacing, your poems, and your formatting intact
            raw_body_content = "".join(lines[2:]).strip()
            publisher_metadata, body_content = extract_publisher_metadata(raw_body_content)

            post = {
                "title": title,
                "date": date_str,
                "body": body_content,
                "file": filename
            }
            if publisher_metadata:
                post["publisher"] = publisher_metadata
            posts.append(post)
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Sort: Newest filename (YYYY-MM-DD) first
    posts.sort(key=lambda x: x['file'], reverse=True)
    return posts

def sync_production(include_draft_reading_aids=False):
    posts = load_posts()
    write_share_pages(posts, include_draft_reading_aids)

    with open(output_file, 'w', encoding='utf-8') as out:
        out.write(f"const current_narrative = {json.dumps(posts, indent=4)};")
    
    print(f"SUCCESS: {len(posts)} entries synced with preserved spacing and static share pages.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate current narrative data and static archive essay pages.")
    parser.add_argument(
        "--reading-aids-preview",
        action="store_true",
        help="Include draft reading aid sidecars for explicit local preview only.",
    )
    args = parser.parse_args()
    sync_production(include_draft_reading_aids=args.reading_aids_preview or reading_aids_preview_enabled())
