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

def markdown_unescape(value):
    return (value or '').replace('\\"', '"').replace('\\[', '[').replace('\\]', ']').replace('\\\\', '\\')

def render_markdown_image(match, as_block=False):
    alt = markdown_unescape(html.unescape(match.group(1) or ''))
    src = html.unescape(match.group(2) or '')
    caption = markdown_unescape(html.unescape(match.group(3) or '')).strip()
    safe_src = html.escape(src, quote=True)
    safe_alt = html.escape(alt, quote=True)
    title_attr = f' title="{html.escape(caption, quote=True)}"' if caption else ''
    image_html = f'<img src="{safe_src}" alt="{safe_alt}"{title_attr}>'
    if as_block and caption:
        safe_caption = html.escape(caption, quote=False)
        return f'<figure class="otw-figure"><img src="{safe_src}" alt="{safe_alt}"><figcaption><em>{safe_caption}</em></figcaption></figure>'
    return image_html

def is_trusted_figure_block(value):
    raw = (value or '').strip()
    lowered = raw.lower()
    return lowered.startswith('<figure') and lowered.endswith('</figure>') and '<script' not in lowered

def inline_markdown(value):
    value = html.escape(value or '', quote=False)
    value = IMAGE_MARKDOWN_PATTERN.sub(lambda m: render_markdown_image(m), value)
    value = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>', value)
    value = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', value)
    value = re.sub(r'`([^`]+)`', r'<code>\1</code>', value)
    return value

def markdown_to_html(markdown):
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
            html_blocks.append(raw)
            continue
        if is_trusted_figure_block(raw):
            html_blocks.append(raw)
            continue

        image_match = IMAGE_MARKDOWN_PATTERN.fullmatch(raw)
        if image_match:
            html_blocks.append(render_markdown_image(image_match, as_block=True))
            continue

        lines = raw.splitlines()
        if all(re.match(r'^\s*[-*]\s+', line) for line in lines):
            items = ''.join(f'<li>{inline_markdown(re.sub(r"^\s*[-*]\s+", "", line))}</li>' for line in lines)
            html_blocks.append(f'<ul>{items}</ul>')
            continue
        if all(re.match(r'^\s*\d+\.\s+', line) for line in lines):
            items = ''.join(f'<li>{inline_markdown(re.sub(r"^\s*\d+\.\s+", "", line))}</li>' for line in lines)
            html_blocks.append(f'<ol>{items}</ol>')
            continue
        if raw.startswith('### '):
            html_blocks.append(f'<h3>{inline_markdown(raw[4:].strip())}</h3>')
            continue
        if raw.startswith('## '):
            html_blocks.append(f'<h2>{inline_markdown(raw[3:].strip())}</h2>')
            continue

        html_blocks.append(f'<p>{inline_markdown(raw).replace(chr(10), "<br>")}</p>')

    return '\n'.join(html_blocks)

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
    body_html = markdown_to_html(post['body'])

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
            max-width: min(100%, 720px);
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
            body_content = "".join(lines[2:]).strip()

            posts.append({
                "title": title,
                "date": date_str,
                "body": body_content,
                "file": filename
            })
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
