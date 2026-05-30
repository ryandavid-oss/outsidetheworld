import html
import json
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

# --- CONFIG ---
input_folder = 'current_narrative'
output_file = 'narrative_data.js'
share_output_folder = 'archive'
og_output_folder = 'Images/og/archive'
site_url = 'https://outsidetheworld.com'

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
    if not url or re.match(r'^(javascript:|data:|blob:)', url, re.I):
        return ''
    if re.match(r'^(https?:|/)', url, re.I):
        return url
    return ''

def normalize_choice(value, allowed, fallback):
    value = str(value or '').strip().lower()
    return value if value in allowed else fallback

def normalize_image_presentation(value):
    value = value or {}
    return {
        'displaySize': normalize_choice(value.get('displaySize'), ['small', 'medium', 'large', 'original'], 'medium'),
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
    image_html = f'<img src="{safe_src}" alt="{safe_alt}"{title_attr}>'
    if as_block and caption:
        safe_caption = html.escape(caption, quote=False)
        classes = figure_classes(metadata) if metadata else 'otw-figure'
        return f'<figure class="{classes}"><img src="{safe_src}" alt="{safe_alt}"><figcaption><em>{safe_caption}</em></figcaption></figure>'
    if as_block and metadata:
        classes = figure_classes(metadata)
        return f'<figure class="{classes}"><img src="{safe_src}" alt="{safe_alt}"></figure>'
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
    blocks = re.split(r'\n\s*\n', (markdown or '').strip())
    html_blocks = []

    for block in blocks:
        raw = block.strip()
        if not raw:
            continue
        if raw == '---':
            html_blocks.append('<hr>')
            continue
        if raw.startswith('<div class="otw-center">') and raw.endswith('</div>'):
            html_blocks.append(sanitize_trusted_html_block(raw))
            continue
        if is_trusted_figure_block(raw):
            html_blocks.append(sanitize_trusted_html_block(raw))
            continue

        image_match = IMAGE_MARKDOWN_PATTERN.fullmatch(raw)
        if image_match:
            html_blocks.append(render_markdown_image(image_match, as_block=True, image_metadata=image_metadata, image_queue=image_queue))
            continue

        lines = raw.splitlines()
        if all(re.match(r'^\s*[-*]\s+', line) for line in lines):
            items = ''.join(f'<li>{inline_markdown(re.sub(r"^\s*[-*]\s+", "", line), image_metadata, image_queue)}</li>' for line in lines)
            html_blocks.append(f'<ul>{items}</ul>')
            continue
        if all(re.match(r'^\s*\d+\.\s+', line) for line in lines):
            items = ''.join(f'<li>{inline_markdown(re.sub(r"^\s*\d+\.\s+", "", line), image_metadata, image_queue)}</li>' for line in lines)
            html_blocks.append(f'<ol>{items}</ol>')
            continue
        if raw.startswith('### '):
            html_blocks.append(f'<h3>{inline_markdown(raw[4:].strip(), image_metadata, image_queue)}</h3>')
            continue
        if raw.startswith('## '):
            html_blocks.append(f'<h2>{inline_markdown(raw[3:].strip(), image_metadata, image_queue)}</h2>')
            continue

        emphasis_match = re.match(r'^\s*(?:_([^_\n]+)_|\*([^*\n]+)\*)\s*$', raw)
        if emphasis_match:
            emphasized = emphasis_match.group(1) or emphasis_match.group(2) or ''
            html_blocks.append(f'<p><em>{inline_markdown(emphasized, image_metadata, image_queue)}</em></p>')
        else:
            html_blocks.append(f'<p>{inline_markdown(raw, image_metadata, image_queue).replace(chr(10), "<br>")}</p>')

    return '\n'.join(html_blocks)

def sanitize_publisher_metadata(metadata):
    if not isinstance(metadata, dict) or metadata.get('schema') != 'otw.publisher.post' or metadata.get('version') != 1:
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
        elif block_type == 'list':
            sanitized['ordered'] = bool(block.get('ordered'))
            sanitized['checklist'] = bool(block.get('checklist'))
        blocks.append(sanitized)

    cleaned = {
        'schema': 'otw.publisher.post',
        'version': 1,
        'source': 'publisher.html',
        'subhead': str(metadata.get('subhead') or ''),
        'blocks': blocks,
        'images': images,
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

def render_share_page(post):
    stem = post_stem(post['file'])
    post_id = build_post_id(post)
    share_path = f"{share_output_folder}/{stem}.html"
    share_url = f"{site_url}/{share_path}"
    archive_url = f"{site_url}/residue_archive.html?post={quote(post_id)}"
    og_image = f"{site_url}/{og_output_folder}/{stem}.png"
    description = excerpt(post['body'])
    published = parse_display_date(post['date'])
    published_meta = f'<meta property="article:published_time" content="{published.date().isoformat()}" />' if published else ''
    body_html = markdown_to_html(post['body'], post.get('publisher'))

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <title>{smartypants_safe(post['title'])} | Outside The World</title>
    <link rel="canonical" href="{share_url}" />
    <link href="../favicon.svg" rel="icon" type="image/svg+xml" />
    <link href="../theme.css" rel="stylesheet" />
    <meta name="description" content="{smartypants_safe(description)}" />
    <meta name="theme-color" content="#0a0a0a" />
    <meta property="og:site_name" content="Outside The World" />
    <meta property="og:type" content="article" />
    <meta property="og:locale" content="en_US" />
    <meta property="og:title" content="{smartypants_safe(post['title'])}" />
    <meta property="og:description" content="{smartypants_safe(description)}" />
    <meta property="og:url" content="{share_url}" />
    <meta property="og:image" content="{og_image}" />
    <meta property="og:image:secure_url" content="{og_image}" />
    <meta property="og:image:type" content="image/png" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:image:alt" content="{smartypants_safe(post['title'])} — Outside The World archive card" />
    {published_meta}
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{smartypants_safe(post['title'])}" />
    <meta name="twitter:description" content="{smartypants_safe(description)}" />
    <meta name="twitter:image" content="{og_image}" />
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;900&family=Fira+Code:wght@300;500;700&family=Merriweather:ital,wght@0,300;0,700;1,300&display=swap');

        html, body {{
            max-width: 100%;
            overflow-x: hidden;
        }}

        body {{
            margin: 0;
            min-height: 100vh;
            background: radial-gradient(circle at top left, rgba(155, 89, 182, 0.1) 0%, var(--bg-dark) 100%);
            color: #e0e6ed;
            font-family: 'Inter', sans-serif;
        }}

        .share-shell {{
            width: min(100%, 960px);
            margin: 0 auto;
            padding: clamp(20px, 6vw, 72px);
        }}

        .share-card {{
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
            padding: clamp(24px, 7vw, 80px);
            background: rgba(0, 0, 0, 0.78);
            border: 1px solid rgba(145, 175, 179, 0.12);
            box-shadow: 0 40px 100px rgba(0, 0, 0, 0.8);
        }}

        .entry-title {{
            margin: 0 0 14px;
            color: #fff;
            font-size: clamp(2rem, 12vw, 2.8rem);
            font-weight: 900;
            line-height: 1.08;
            overflow-wrap: anywhere;
        }}

        .entry-toolbar {{
            display: flex;
            gap: 14px;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            margin-bottom: clamp(34px, 6vw, 56px);
            min-width: 0;
        }}

        .entry-meta,
        .share-btn,
        .share-status,
        .archive-link,
        .archive-legal {{
            font-family: 'Fira Code', monospace;
            font-size: 0.62rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            overflow-wrap: anywhere;
        }}

        .entry-meta {{
            color: var(--brand-teal);
        }}

        .share-controls {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
            max-width: 100%;
        }}

        .share-btn,
        .archive-link {{
            min-height: 44px;
            border: 1px solid rgba(145, 175, 179, 0.18);
            background: rgba(145, 175, 179, 0.04);
            color: var(--brand-teal);
            padding: 10px 14px;
            text-decoration: none;
            cursor: pointer;
        }}

        .share-status {{
            color: rgba(224, 230, 237, 0.65);
        }}

        .entry-body {{
            color: #d1d1d1;
            font-family: 'Merriweather', serif;
            font-size: clamp(1rem, 3.8vw, 1.1rem);
            font-weight: 300;
            line-height: 1.85;
            overflow-wrap: break-word;
        }}

        .entry-body p {{
            margin: 0 0 1.5rem;
        }}

        .entry-body strong {{
            color: #fff;
            font-family: 'Inter', sans-serif;
            font-weight: 900;
        }}

        .entry-body a {{
            color: var(--brand-teal);
            text-decoration: none;
            border-bottom: 1px dashed rgba(145, 175, 179, 0.4);
        }}

        .entry-body img {{
            display: block;
            max-width: min(100%, 720px);
            height: auto;
            margin: 40px auto;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
        }}

        .entry-body figure,
        .entry-body .otw-figure {{
            margin: 40px auto;
            max-width: min(100%, var(--otw-figure-max-width, 720px));
        }}

        .entry-body figure img,
        .entry-body .otw-figure img {{
            margin: 0 auto;
        }}

        .entry-body figure figcaption,
        .entry-body .otw-figure figcaption {{
            margin-top: 12px;
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.5;
            text-align: center;
        }}

        .entry-body .otw-figure--small {{ --otw-figure-max-width: 320px; }}
        .entry-body .otw-figure--medium {{ --otw-figure-max-width: 520px; }}
        .entry-body .otw-figure--large {{ --otw-figure-max-width: 760px; }}
        .entry-body .otw-figure--original {{ --otw-figure-max-width: 100%; }}

        .entry-body .otw-figure--small,
        .entry-body .otw-figure--medium,
        .entry-body .otw-figure--large {{
            width: min(100%, var(--otw-figure-max-width, 720px));
        }}

        .entry-body .otw-figure--small img,
        .entry-body .otw-figure--medium img,
        .entry-body .otw-figure--large img {{
            width: 100%;
        }}

        .entry-body .otw-figure--align-left {{
            margin-left: 0;
            margin-right: auto;
        }}

        .entry-body .otw-figure--align-center {{
            margin-left: auto;
            margin-right: auto;
        }}

        .entry-body .otw-figure--align-right {{
            margin-left: auto;
            margin-right: 0;
        }}

        .entry-body .otw-figure--wrap-left,
        .entry-body .otw-figure--wrap-right {{
            clear: none;
            width: min(45%, var(--otw-figure-max-width, 520px));
            max-width: min(45%, var(--otw-figure-max-width, 520px));
            margin-top: 0.35rem;
            margin-bottom: 1rem;
        }}

        .entry-body .otw-figure--wrap-left {{
            float: left;
            margin-left: 0;
            margin-right: 1.5rem;
        }}

        .entry-body .otw-figure--wrap-right {{
            float: right;
            margin-left: 1.5rem;
            margin-right: 0;
        }}

        .entry-body hr {{
            border: 0;
            border-top: 1px solid rgba(145, 175, 179, 0.16);
            margin: 2.5rem 0;
        }}

        .archive-actions {{
            display: flex;
            justify-content: space-between;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 42px;
            padding-top: 18px;
            border-top: 1px solid rgba(145, 175, 179, 0.12);
        }}

        .archive-legal {{
            width: min(100%, 800px);
            margin: 0 auto;
            padding: 24px 12px 0;
            color: rgba(224, 224, 224, 0.5);
            line-height: 1.9;
            text-align: center;
        }}

        .archive-legal a {{
            color: inherit;
            text-decoration: none;
        }}

        .archive-legal-brand {{
            margin-top: 6px;
        }}

        @media (max-width: 899px) {{
            .entry-body .otw-figure--wrap-left,
            .entry-body .otw-figure--wrap-right {{
                float: none;
                clear: both;
                width: min(100%, var(--otw-figure-max-width, 520px));
                max-width: min(100%, var(--otw-figure-max-width, 520px));
                margin: 40px auto;
            }}

            .share-card {{
                border: none;
                background: rgba(0, 0, 0, 0.85);
            }}

            .share-controls,
            .share-btn,
            .share-status,
            .archive-link {{
                width: 100%;
            }}

            .share-btn,
            .archive-link {{
                text-align: center;
            }}
        }}
    </style>
</head>
<body>
    <main class="share-shell">
        <article class="share-card">
            <h1 class="entry-title">{smartypants_safe(post['title'])}</h1>
            <div class="entry-toolbar">
                <div class="entry-meta">TEMPORAL_MARK: {smartypants_safe(post['date'].upper())}</div>
                <div class="share-controls">
                    <button type="button" class="share-btn" onclick="copyShareLink()">COPY / SHARE LINK</button>
                    <span class="share-status" id="share-status">STATIC_ARCHIVE_SIGNAL</span>
                </div>
            </div>
            <div class="entry-body">
{body_html}
            </div>
            <div class="archive-actions">
                <a class="archive-link" href="{archive_url}">OPEN ARCHIVE MATRIX</a>
                <a class="archive-link" href="../personal.html">RETURN TO OTW</a>
            </div>
        </article>
        <div class="archive-legal">
            <a href="../privacy.html">Privacy</a>
            <span aria-hidden="true">&nbsp;|&nbsp;</span>
            <a href="../terms.html">Terms</a>
            <span aria-hidden="true">&nbsp;|&nbsp;</span>
            <a href="../trademarks.html">Trademarks</a>
            <span aria-hidden="true">&nbsp;|&nbsp;</span>
            <a href="../support.html">Support</a>
            <div class="archive-legal-brand">© 2026 Outside the World is New, LLC. Outside The World is a claimed brand identifier.</div>
        </div>
    </main>
    <script>
        async function copyShareLink() {{
            const statusEl = document.getElementById('share-status');
            const url = window.location.href.split('#')[0];
            try {{
                if (navigator.share) {{
                    await navigator.share({{ title: document.title, text: 'Outside The World archive signal', url }});
                    statusEl.textContent = 'LINK_SHARED';
                    return;
                }}
                await navigator.clipboard.writeText(url);
                statusEl.textContent = 'LINK_COPIED';
            }} catch {{
                statusEl.textContent = 'COPY_FAILED';
            }}
        }}
    </script>
</body>
</html>
'''

def write_share_pages(posts):
    Path(share_output_folder).mkdir(parents=True, exist_ok=True)
    Path(og_output_folder).mkdir(parents=True, exist_ok=True)

    for post in posts:
        stem = post_stem(post['file'])
        post['post_id'] = build_post_id(post)
        post['share_path'] = f"{share_output_folder}/{stem}.html"
        post['og_image'] = f"{og_output_folder}/{stem}.png"

        share_file = Path(post['share_path'])
        share_file.write_text(render_share_page(post), encoding='utf-8')
        generate_og_image(post, Path(post['og_image']))

def sync_production():
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
    write_share_pages(posts)

    with open(output_file, 'w', encoding='utf-8') as out:
        out.write(f"const current_narrative = {json.dumps(posts, indent=4)};")
    
    print(f"SUCCESS: {len(posts)} entries synced with preserved spacing and static share pages.")

if __name__ == "__main__":
    sync_production()
