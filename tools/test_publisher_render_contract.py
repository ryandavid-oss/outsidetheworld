#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import json
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def load_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


narrative_sync = load_module(ROOT / "narrative_sync.py")
atom_feed = load_module(ROOT / "tools" / "generate_atom_feed.py")

IMAGE_ONE = "https://pub-fd35040d2a3b40af985b8aa67b98eaa8.r2.dev/narrative/fixture-one.png"
IMAGE_TWO = "https://pub-fd35040d2a3b40af985b8aa67b98eaa8.r2.dev/narrative/fixture-two.png"
PUBLISHER_KEY_SENTINEL = "publisher-key-should-not-render"


def publisher_comment(metadata):
    return "<!-- otw-publisher\n" + json.dumps(metadata, separators=(",", ":")) + "\n-->"


def assert_no_public_leaks(value):
    lowered = str(value).lower()
    assert "otw-publisher" not in lowered
    assert "javascript:" not in lowered
    assert "data:image" not in lowered
    assert "blob:" not in lowered
    assert "onerror=" not in lowered
    assert "onclick=" not in lowered
    assert "<script" not in lowered
    assert PUBLISHER_KEY_SENTINEL not in value
    for control in ["Retry", "Remove", "Uploaded", "Move image", "Replace image"]:
        assert control not in value


def extract_share_entry_body(value):
    match = re.search(
        r'<div class="entry-body"[^>]*>\s*([\s\S]*?)\s*</div>\s*(?:<footer class="entry-signoff"[\s\S]*?</footer>\s*)?(?:<nav class="reader-nav"[\s\S]*?</nav>\s*)?<div class="archive-actions">',
        value,
    )
    assert match
    return match.group(1)


def extract_meta(html_value):
    meta = {}
    for name in [
        "description",
        "twitter:card",
        "twitter:title",
        "twitter:description",
        "twitter:image",
    ]:
        match = re.search(rf'<meta\s+name="{re.escape(name)}"\s+content="([^"]*)"', html_value)
        if match:
            meta[name] = match.group(1)
    for prop in [
        "og:site_name",
        "og:type",
        "og:locale",
        "og:title",
        "og:description",
        "og:url",
        "og:image",
        "og:image:secure_url",
        "og:image:type",
        "og:image:width",
        "og:image:height",
        "og:image:alt",
    ]:
        match = re.search(rf'<meta\s+property="{re.escape(prop)}"\s+content="([^"]*)"', html_value)
        if match:
            meta[prop] = match.group(1)
    canonical = re.search(r'<link\s+rel="canonical"\s+href="([^"]*)"', html_value)
    if canonical:
        meta["canonical"] = canonical.group(1)
    return meta


def fixture_metadata():
    return {
        "schema": "otw.publisher.post",
        "version": 1,
        "source": "publisher.html",
        "subhead": "A field note from the new desk",
        "publisherKey": PUBLISHER_KEY_SENTINEL,
        "unknownFutureField": {"should": "be ignored"},
        "images": [
            {
                "id": "image_one",
                "url": IMAGE_ONE,
                "objectKey": "narrative/fixture-one.png",
                "alt": "Small right wrapped image",
                "caption": "A small image that lets the words move around it.",
                "displaySize": "small",
                "alignment": "right",
                "wrapMode": "wrap-left",
            },
            {
                "id": "image_two",
                "url": IMAGE_TWO,
                "objectKey": "narrative/fixture-two.png",
                "alt": "Large centered image",
                "caption": "A large centered image after the divider.",
                "displaySize": "large",
                "alignment": "center",
                "wrapMode": "none",
            },
        ],
        "blocks": [
            {"id": "p1", "type": "paragraph"},
            {
                "id": "image_one",
                "type": "image",
                "imageRef": "image_one",
                "url": IMAGE_ONE,
                "objectKey": "narrative/fixture-one.png",
                "displaySize": "small",
                "alignment": "right",
                "wrapMode": "wrap-left",
            },
            {"id": "p2", "type": "paragraph"},
            {"id": "divider", "type": "divider"},
            {
                "id": "image_two",
                "type": "image",
                "imageRef": "image_two",
                "url": IMAGE_TWO,
                "objectKey": "narrative/fixture-two.png",
                "displaySize": "large",
                "alignment": "center",
                "wrapMode": "none",
            },
            {"id": "p3", "type": "paragraph"},
        ],
    }


def fixture_markdown():
    metadata = fixture_metadata()
    return f"""# Publisher Fixture
Date: May 29, 2026

{publisher_comment(metadata)}

_A field note from the new desk_

First paragraph with **bold detail** and a [normal link](https://outsidetheworld.com/personal.html).

![Small right wrapped image]({IMAGE_ONE} "A small image that lets the words move around it.")

Second paragraph after the wrapped image. It should remain readable and keep clean order.

---

![Large centered image]({IMAGE_TWO} "A large centered image after the divider.")

Final paragraph after the large image.
"""


def run_temp_sync(temp):
    input_dir = temp / "current_narrative"
    input_dir.mkdir()
    shutil.copy(
        ROOT / "current_narrative" / "2026-03-16-just-a-midnights-summary.md",
        input_dir / "2026-03-16-just-a-midnights-summary.md",
    )
    (input_dir / "2026-05-29-publisher-fixture.md").write_text(fixture_markdown(), encoding="utf-8")

    old_input = narrative_sync.input_folder
    old_output = narrative_sync.output_file
    old_share = narrative_sync.share_output_folder
    old_og = narrative_sync.og_output_folder
    try:
        narrative_sync.input_folder = str(input_dir)
        narrative_sync.output_file = str(temp / "narrative_data.js")
        narrative_sync.share_output_folder = str(temp / "archive")
        narrative_sync.og_output_folder = str(temp / "og")
        narrative_sync.sync_production()
    finally:
        narrative_sync.input_folder = old_input
        narrative_sync.output_file = old_output
        narrative_sync.share_output_folder = old_share
        narrative_sync.og_output_folder = old_og


def test_existing_markdown_without_metadata_degrades_cleanly():
    markdown = (
        "Paragraph with **bold** and [safe link](https://outsidetheworld.com/).\n\n"
        "---\n\n"
        '![Plain alt](https://outsidetheworld.com/Images/Equal.svg "Plain caption")'
    )
    without_metadata = narrative_sync.markdown_to_html(markdown)
    with_empty_metadata = narrative_sync.markdown_to_html(markdown, {})

    assert without_metadata == with_empty_metadata
    assert '<strong>bold</strong>' in without_metadata
    assert '<a href="https://outsidetheworld.com/">safe link</a>' in without_metadata
    assert '<hr>' in without_metadata
    assert '<figure class="otw-figure">' in without_metadata
    assert "otw-figure--small" not in without_metadata
    assert "Plain caption" in without_metadata


def test_local_image_paths_normalize_to_root_relative_paths():
    markdown = (
        '![Local markdown image](Images/Blog/local-preview.png "Local caption")\n\n'
        '<figure><img src="Images/Blog/legacy-figure.jpg" alt="Legacy figure"></figure>'
    )
    html = narrative_sync.markdown_to_html(markdown)

    assert 'src="/Images/Blog/local-preview.png"' in html
    assert 'src="/Images/Blog/legacy-figure.jpg"' in html
    assert 'src="Images/' not in html


def test_metadata_parser_edge_cases_fail_closed():
    missing_metadata = "Just body text."
    metadata, cleaned = narrative_sync.extract_publisher_metadata(missing_metadata)
    assert metadata == {}
    assert cleaned == missing_metadata

    cases = [
        ('<!-- otw-publisher\n{"schema":\n-->\nText.', "malformed"),
        (publisher_comment({"schema": "wrong.schema", "version": 1}) + "\nText.", "wrong schema"),
        (publisher_comment({"schema": "otw.publisher.post", "version": 3, "images": [], "blocks": []}) + "\nText.", "wrong version"),
    ]

    for body, _label in cases:
        metadata, cleaned = narrative_sync.extract_publisher_metadata(body)
        assert metadata == {}
        assert cleaned == "Text."

    metadata, cleaned = narrative_sync.extract_publisher_metadata(
        publisher_comment({**fixture_metadata(), "unknown": "<script>ignored</script>"}) + "\nText."
    )
    assert metadata["schema"] == "otw.publisher.post"
    assert metadata["version"] == 1
    assert "unknown" not in metadata
    assert PUBLISHER_KEY_SENTINEL not in str(metadata)
    assert cleaned == "Text."


def test_metadata_cardinality_edge_cases_do_not_break_rendering():
    fewer_metadata = {
        "schema": "otw.publisher.post",
        "version": 1,
        "images": [
            {
                "id": "image_one",
                "url": IMAGE_ONE,
                "alt": "First metadata alt",
                "caption": "First metadata caption",
                "displaySize": "small",
                "alignment": "right",
                "wrapMode": "wrap-left",
            }
        ],
        "blocks": [
            {"id": "image_one", "type": "image", "imageRef": "image_one", "url": IMAGE_ONE, "displaySize": "small", "alignment": "right", "wrapMode": "wrap-left"}
        ],
    }
    markdown = f'![First]({IMAGE_ONE} "First")\n\n![Second]({IMAGE_TWO} "Second")'
    html = narrative_sync.markdown_to_html(markdown, fewer_metadata)

    assert "First metadata caption" in html
    assert "Second" in html
    assert html.count("<figure") == 2
    assert html.count("otw-figure--small") == 1
    assert "otw-figure--wrap-left" in html

    more_metadata = {
        **fewer_metadata,
        "images": [
            *fewer_metadata["images"],
            {"id": "extra", "url": "https://outsidetheworld.com/extra.png", "caption": "Extra should not render", "displaySize": "large"},
        ],
        "blocks": [
            *fewer_metadata["blocks"],
            {"id": "extra", "type": "image", "imageRef": "extra", "url": "https://outsidetheworld.com/extra.png", "displaySize": "large"},
        ],
    }
    html = narrative_sync.markdown_to_html(f'![First]({IMAGE_ONE} "First")', more_metadata)
    assert "Extra should not render" not in html
    assert "extra.png" not in html


def test_all_image_presentation_options_render_and_css_agrees():
    sizes = ["x-small", "small", "medium", "large", "original"]
    alignments = ["left", "center", "right"]
    wraps = ["none", "wrap-left", "wrap-right"]
    css = (ROOT / "theme.css").read_text(encoding="utf-8")

    assert "sizes: x-small, small, medium, large, original" in css
    assert "alignments: left, center, right" in css
    assert "wraps: none, wrap-left, wrap-right" in css
    assert "max-width: 100%" in css
    assert "width: min(100%, var(--otw-figure-max-width, 720px))" in css
    assert "width: min(100%, var(--otw-figure-wrap-width, 340px))" in css
    assert "height: auto" in css
    assert "float: none" in css
    assert "--otw-figure-max-width: var(--otw-figure-natural-width, 100%)" in css
    assert "max-width: none" in css
    assert "text-align: center" in css
    assert "font-family: 'Inter', ui-sans-serif, system-ui" in css
    assert "font-size: clamp(0.98rem, 1.2vw, 1.08rem)" in css
    assert "object-fit: cover" not in css[css.index(".otw-figure"):css.index("/* 6. NAVIGATION")]

    for size in sizes:
        for alignment in alignments:
            for wrap in wraps:
                metadata = {
                    "schema": "otw.publisher.post",
                    "version": 1,
                    "images": [{"id": "image", "url": IMAGE_ONE, "alt": "Alt", "caption": "Caption", "width": 1400, "height": 800, "displaySize": size, "alignment": alignment, "wrapMode": wrap}],
                    "blocks": [{"id": "image", "type": "image", "imageRef": "image", "url": IMAGE_ONE, "displaySize": size, "alignment": alignment, "wrapMode": wrap}],
                }
                html = narrative_sync.markdown_to_html(f'![Alt]({IMAGE_ONE} "Caption")', metadata)
                assert f"otw-figure--{size}" in html
                assert f"otw-figure--align-{alignment}" in html
                assert f"otw-figure--{wrap}" in html
                assert 'alt="Alt"' in html
                assert 'style="--otw-figure-natural-width: 1400px;"' in html
                assert "<figcaption><em>Caption</em></figcaption>" in html


def test_published_image_haze_uses_the_frgmnts_palette():
    reader_css = (ROOT / "archive_reader.css").read_text(encoding="utf-8")
    theme_css = (ROOT / "theme.css").read_text(encoding="utf-8")
    residue_html = (ROOT / "residue_archive.html").read_text(encoding="utf-8")

    for source in (reader_css, theme_css, residue_html):
        assert "rgba(255, 105, 180" in source
        assert "rgba(155, 89, 182" in source

    assert "box-shadow: var(--reader-image-shadow)" in reader_css
    assert "box-shadow: var(--otw-published-image-shadow)" in theme_css
    assert "box-shadow: var(--archive-image-shadow)" in residue_html


def test_publisher_rich_formatting_metadata_restores_visual_styles():
    base_metadata = {
        "schema": "otw.publisher.post",
        "formatting": {
            "mode": "otw-enhanced-markdown",
            "version": 1,
            "fallback": "markdown",
        },
        "subhead": "A field note from the new desk",
        "images": [],
        "blocks": [
            {
                "id": "p1",
                "type": "paragraph",
                "html": 'First <span style="color: #6395EE; background-color: #A0BEF5; text-decoration: underline; position: fixed">styled</span> paragraph.',
                "text": "First styled paragraph.",
                "lineSpacing": "1.5",
            },
            {
                "id": "h1",
                "type": "heading",
                "level": 2,
                "html": 'Publisher <u>heading</u>',
                "text": "Publisher heading",
                "lineSpacing": "1.15",
            },
            {
                "id": "quote",
                "type": "quote",
                "html": '<span style="font-style: italic">Quoted field note</span>',
                "text": "Quoted field note",
                "lineSpacing": "2.0",
            },
            {
                "id": "list",
                "type": "list",
                "items": [
                    {"id": "li1", "html": 'One <span style="font-weight: 700">strong</span>', "text": "One strong"},
                    {"id": "li2", "html": '<span style="background-color: #91AFB3">Two</span>', "text": "Two"},
                ],
                "lineSpacing": "1.0",
            },
        ],
    }
    markdown = """_A field note from the new desk_

First styled paragraph.

## Publisher heading

> Quoted field note

- One strong
- Two
"""
    for version in [1, 2]:
        metadata = {**base_metadata, "version": version}
        sanitized = narrative_sync.sanitize_publisher_metadata(metadata)
        html = narrative_sync.markdown_to_html(markdown, sanitized)

        assert sanitized["version"] == version
        if version == 2:
            assert sanitized["formatting"]["mode"] == "otw-enhanced-markdown"
        assert '<p><em>A field note from the new desk</em></p>' in html
        assert '<p style="line-height: 1.5;">First <span style="color: #6395EE; background-color: #A0BEF5; text-decoration: underline">styled</span> paragraph.</p>' in html
        assert '<h2 style="line-height: 1.15;">Publisher <u>heading</u></h2>' in html
        assert '<blockquote style="line-height: 2;"><span style="font-style: italic">Quoted field note</span></blockquote>' in html
        assert '<ul style="line-height: 1;"><li>One <span style="font-weight: 700">strong</span></li><li><span style="background-color: #91AFB3">Two</span></li></ul>' in html
        assert "position: fixed" not in html
        assert_no_public_leaks(html)


def test_sanitization_security_for_markdown_and_metadata():
    malicious_metadata = {
        "schema": "otw.publisher.post",
        "version": 1,
        "publisherKey": PUBLISHER_KEY_SENTINEL,
        "images": [
            {
                "id": "image",
                "url": IMAGE_ONE,
                "alt": '<script>alert("alt")</script>',
                "caption": '<script>alert("caption")</script>',
                "displaySize": "small",
                "alignment": "right",
                "wrapMode": "wrap-left",
            },
            {"id": "bad_js", "url": "javascript:alert(1)", "caption": "Bad"},
            {"id": "bad_data", "url": "data:image/png;base64,abc", "caption": "Bad"},
            {"id": "bad_blob", "url": "blob:https://example.test/local", "caption": "Bad"},
        ],
        "blocks": [
            {"id": "image", "type": "image", "imageRef": "image", "url": IMAGE_ONE, "displaySize": "small", "alignment": "right", "wrapMode": "wrap-left"},
            {"id": "bad_js", "type": "image", "url": "javascript:alert(1)"},
            {"id": "bad_data", "type": "image", "url": "data:image/png;base64,abc"},
            {"id": "bad_blob", "type": "image", "url": "blob:https://example.test/local"},
            {"id": "bad_protocol_relative", "type": "image", "url": "//example.test/local.png"},
            {"id": "bad_traversal", "type": "image", "url": "../Images/secret.png"},
        ],
    }
    body = (
        f'![Safe]({IMAGE_ONE} "Safe")\n\n'
        "[bad link](javascript:alert(1))\n\n"
        '![bad js](javascript:alert(1) "Bad")\n\n'
        '![bad data](data:image/png;base64,abc "Bad")\n\n'
        '![bad blob](blob:https://example.test/local "Bad")\n\n'
        '![bad protocol](//example.test/local.png "Bad")\n\n'
        '![bad traversal](../Images/secret.png "Bad")\n\n'
        '<figure><img src="" alt="Empty"></figure>\n\n'
        '<figure><img src="../Images/secret.png" alt="Traversal"></figure>'
    )
    html = narrative_sync.markdown_to_html(body, malicious_metadata)

    assert "&lt;script&gt;" in html
    assert "&lt;script&gt;alert(\"caption\")&lt;/script&gt;" in html
    assert '<script>alert("alt")</script>' not in html
    assert '<script>alert("caption")</script>' not in html
    assert 'src=""' not in html
    assert 'src="//' not in html
    assert "../Images/secret.png" not in html
    assert_no_public_leaks(html)

    metadata, cleaned = narrative_sync.extract_publisher_metadata(
        '<!-- otw-publisher\n{"schema":"otw.publisher.post","version":1,"subhead":"\\u003cscript\\u003ealert(1)\\u003c/script\\u003e","images":[],"blocks":[]}\n-->\nText.'
    )
    assert metadata["subhead"] == "<script>alert(1)</script>"
    assert cleaned == "Text."
    assert PUBLISHER_KEY_SENTINEL not in str(metadata)
    assert "javascript:" not in str(metadata)
    assert "data:image" not in str(metadata)
    assert "blob:" not in str(metadata)


def test_trusted_legacy_figure_blocks_are_preserved_but_sanitized():
    markdown = (
        '<figure class="otw-figure" onclick="alert(1)">'
        f'<img src="{IMAGE_ONE}" alt="Legacy" onerror="alert(1)">'
        '<figcaption onclick="alert(1)">Legacy caption</figcaption>'
        "</figure>\n\n"
        '<figure><img src="javascript:alert(1)" onerror="alert(1)"><figcaption>Unsafe URL</figcaption></figure>'
    )
    html = narrative_sync.markdown_to_html(markdown)

    assert '<figure class="otw-figure">' in html
    assert "Legacy caption" in html
    assert "Unsafe URL" in html
    assert_no_public_leaks(html)


def test_reused_image_url_can_keep_distinct_presentation_by_order_after_sanitization():
    url = "https://pub-fd35040d2a3b40af985b8aa67b98eaa8.r2.dev/narrative/reused.png"
    raw_metadata = {
        "schema": "otw.publisher.post",
        "version": 1,
        "images": [
            {"id": "image_a", "url": url, "alt": "First", "caption": "First caption", "displaySize": "small", "alignment": "left", "wrapMode": "none"},
            {"id": "image_b", "url": url, "alt": "Second", "caption": "Second caption", "displaySize": "large", "alignment": "right", "wrapMode": "wrap-left"},
        ],
        "blocks": [
            {"id": "image_a", "type": "image", "imageRef": "image_a", "url": url, "displaySize": "small", "alignment": "left", "wrapMode": "none"},
            {"id": "image_b", "type": "image", "imageRef": "image_b", "url": url, "displaySize": "large", "alignment": "right", "wrapMode": "wrap-left"},
        ],
    }
    metadata = narrative_sync.sanitize_publisher_metadata(raw_metadata)
    markdown = f'![First]({url} "First caption")\n\n![Second]({url} "Second caption")'
    html = narrative_sync.markdown_to_html(markdown, metadata)
    first = html.index("First caption")
    second = html.index("Second caption")

    assert len(metadata["images"]) == 2
    assert "otw-figure--small" in html[:second]
    assert "otw-figure--large" in html[first:]
    assert "otw-figure--align-left" in html[:second]
    assert "otw-figure--align-right" in html[first:]
    assert first < second


def test_atom_feed_strips_publisher_metadata_and_stays_valid_xml():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        narrative_data = temp / "narrative_data.js"
        fragments_data = temp / "fragments_data.js"
        output = temp / "atom.xml"
        narrative_data.write_text(
            'const current_narrative = [{'
            '"title":"Publisher Atom Test",'
            '"date":"May 29, 2026",'
            '"share_path":"archive/test.html",'
            '"body":"<!-- otw-publisher {\\\\\\"schema\\\\\\":\\\\\\"otw.publisher.post\\\\\\"} --> Visible summary text."'
            '}];',
            encoding="utf-8",
        )
        fragments_data.write_text("window.otw_fragments = [];", encoding="utf-8")

        old_narrative = atom_feed.NARRATIVE_DATA
        old_fragments = atom_feed.FRAGMENTS_DATA
        old_output = atom_feed.OUTPUT
        try:
            atom_feed.NARRATIVE_DATA = narrative_data
            atom_feed.FRAGMENTS_DATA = fragments_data
            atom_feed.OUTPUT = output
            atom_feed.main()
        finally:
            atom_feed.NARRATIVE_DATA = old_narrative
            atom_feed.FRAGMENTS_DATA = old_fragments
            atom_feed.OUTPUT = old_output

        root = ET.fromstring(output.read_text(encoding="utf-8"))
        text = "".join(root.itertext())
        assert root.tag.endswith("feed")
        assert "Visible summary text" in text
        assert "otw-publisher" not in text
        assert PUBLISHER_KEY_SENTINEL not in text


def test_realistic_publisher_fixture_end_to_end():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        run_temp_sync(temp)

        narrative_json = (temp / "narrative_data.js").read_text(encoding="utf-8")
        share_html = (temp / "archive" / "2026-05-29-publisher-fixture.html").read_text(encoding="utf-8")
        assert '"publisher"' in narrative_json
        assert '"body": "_A field note from the new desk_' in narrative_json
        assert '"displaySize": "small"' in narrative_json
        assert '"alignment": "right"' in narrative_json
        assert '"wrapMode": "wrap-left"' in narrative_json
        assert_no_public_leaks(narrative_json)

        for expected in [
            '<p class="entry-deck">A field note from the new desk</p>',
            'class="entry-feature entry-feature--natural entry-feature--focal-center"',
            'fetchpriority="high"',
            "otw-figure--large",
            "otw-figure--align-center",
            "otw-figure--none",
            "A small image that lets the words move around it.",
            "A large centered image after the divider.",
            '<a href="https://outsidetheworld.com/personal.html">normal link</a>',
            "<hr>",
        ]:
            assert expected in share_html
        assert "otw-publisher" not in share_html
        assert PUBLISHER_KEY_SENTINEL not in share_html
        assert_no_public_leaks(extract_share_entry_body(share_html))
        assert share_html.count(IMAGE_ONE) >= 4
        assert extract_share_entry_body(share_html).count(IMAGE_ONE) == 0

        fragments_data = temp / "fragments_data.js"
        fragments_data.write_text("window.otw_fragments = [];", encoding="utf-8")
        atom_output = temp / "atom.xml"
        old_narrative = atom_feed.NARRATIVE_DATA
        old_fragments = atom_feed.FRAGMENTS_DATA
        old_output = atom_feed.OUTPUT
        try:
            atom_feed.NARRATIVE_DATA = temp / "narrative_data.js"
            atom_feed.FRAGMENTS_DATA = fragments_data
            atom_feed.OUTPUT = atom_output
            atom_feed.main()
        finally:
            atom_feed.NARRATIVE_DATA = old_narrative
            atom_feed.FRAGMENTS_DATA = old_fragments
            atom_feed.OUTPUT = old_output

        atom_text = atom_output.read_text(encoding="utf-8")
        ET.fromstring(atom_text)
        assert "Publisher Fixture" in atom_text
        assert_no_public_leaks(atom_text)


def test_canonical_archive_page_emits_full_preview_metadata():
    share_html = narrative_sync.render_share_page({
        "title": "Publisher Fixture",
        "date": "May 29, 2026",
        "file": "2026-05-29-publisher-fixture.md",
        "body": "A field note from the new desk with enough detail for a preview.",
    })
    meta = extract_meta(share_html)

    assert meta["canonical"] == "https://outsidetheworld.com/archive/2026-05-29-publisher-fixture.html"
    assert meta["og:url"] == "https://outsidetheworld.com/archive/2026-05-29-publisher-fixture.html"
    assert meta["og:title"] == "Publisher Fixture"
    assert meta["og:site_name"] == "Outside The World"
    assert meta["og:type"] == "article"
    assert meta["og:image"] == "https://outsidetheworld.com/Images/og/archive/2026-05-29-publisher-fixture.png"
    assert meta["og:image:secure_url"] == meta["og:image"]
    assert meta["og:image:width"] == "1200"
    assert meta["og:image:height"] == "630"
    assert meta["twitter:card"] == "summary_large_image"
    assert meta["twitter:title"] == "Publisher Fixture"
    assert meta["twitter:image"] == meta["og:image"]
    assert "A field note from the new desk" in meta["og:description"]
    assert "residue_archive.html?post=" not in share_html


def test_canonical_archive_page_prefers_first_article_image_when_present():
    share_html = narrative_sync.render_share_page({
        "title": "Publisher Fixture",
        "date": "May 29, 2026",
        "file": "2026-05-29-publisher-fixture.md",
        "body": f"Introductory paragraph.\n\n![Markdown alt text]({IMAGE_TWO} \"Markdown caption\")",
        "publisher": fixture_metadata(),
    })
    meta = extract_meta(share_html)

    assert meta["canonical"] == "https://outsidetheworld.com/archive/2026-05-29-publisher-fixture.html"
    assert meta["og:url"] == "https://outsidetheworld.com/archive/2026-05-29-publisher-fixture.html"
    assert meta["og:image"] == IMAGE_ONE
    assert meta["og:image:secure_url"] == IMAGE_ONE
    assert meta["twitter:image"] == IMAGE_ONE
    assert meta["og:image:type"] == "image/png"
    assert "og:image:width" not in meta
    assert "og:image:height" not in meta
    assert meta["og:image:alt"] == "Small right wrapped image"


def test_explicit_feature_image_drives_opening_and_is_not_duplicated_in_body():
    metadata = fixture_metadata()
    metadata["version"] = 2
    metadata["featureImageRef"] = "image_two"
    for image in metadata["images"]:
        if image["id"] == "image_two":
            image.update({
                "width": 1600,
                "height": 900,
                "credit": "OTW Studio",
                "featureLayout": "cinematic",
                "featureFocal": "top",
            })
    metadata = narrative_sync.sanitize_publisher_metadata(metadata)
    assert metadata["featureImageRef"] == "image_two"
    share_html = narrative_sync.render_share_page({
        "title": "Feature Selection Fixture",
        "date": "May 29, 2026",
        "file": "2026-05-29-feature-selection-fixture.md",
        "body": f'![First]({IMAGE_ONE})\n\nBody copy.\n\n![Second]({IMAGE_TWO} "Chosen feature")',
        "publisher": metadata,
    })
    body = extract_share_entry_body(share_html)

    assert f'<img src="{IMAGE_TWO}"' in share_html
    assert 'class="entry-feature entry-feature--cinematic entry-feature--focal-top"' in share_html
    assert 'fetchpriority="high"' in share_html
    assert 'style="--feature-aspect: 1600 / 900;"' in share_html
    assert 'width="1600" height="900"' in share_html
    assert 'class="entry-feature-credit">OTW Studio</span>' in share_html
    assert body.count(IMAGE_TWO) == 0
    assert body.count(IMAGE_ONE) == 1
    assert narrative_sync.first_article_image({"title": "Feature", "publisher": metadata})["url"] == IMAGE_TWO


def test_article_shell_has_home_identity_schema_and_consistent_section_levels():
    share_html = narrative_sync.render_share_page({
        "title": "Branded Reader Fixture",
        "date": "July 11, 2026",
        "file": "2026-07-11-branded-reader-fixture.md",
        "body": "## I. First\n\nOpening copy.\n\n### II. Second\n\nClosing copy.",
    })

    assert 'href="/" aria-label="Outside The World home"' in share_html
    assert 'src="/Images/Equal.svg"' in share_html
    assert 'src="/Images/Equal_dark.svg"' in share_html
    assert 'By <strong><a href="/ryandavid-burningham.html" rel="author">RyanDavid Burningham</a></strong>' in share_html
    assert '<script type="application/ld+json">' in share_html
    assert '"@type": "Article"' in share_html
    assert '"name": "RyanDavid Burningham"' in share_html
    assert '<span class="entry-section-index">II.</span> <span class="entry-section-title">Second</span>' in share_html
    assert '<h3>II. Second</h3>' not in share_html


def test_article_shell_adapts_to_length_media_and_opening_structure():
    long_body = "## I. Opening\n\n" + " ".join(["substantial"] * 2800)
    long_html = narrative_sync.render_share_page({
        "title": "Long Reader Fixture",
        "date": "July 11, 2026",
        "file": "2026-07-11-long-reader-fixture.md",
        "body": long_body,
    })
    short_html = narrative_sync.render_share_page({
        "title": "Short Reader Fixture",
        "date": "July 11, 2026",
        "file": "2026-07-11-short-reader-fixture.md",
        "body": "A concise field note with a complete thought.",
    })

    assert 'reader-card--long reader-card--text-led' in long_html
    assert 'data-reader-dock' in long_html
    assert 'article-length-long article-media-text-led' in long_html
    assert 'reader-card--short reader-card--text-led' in short_html
    assert 'data-reader-dock' not in short_html


def test_opening_dropcap_wraps_first_visible_letter_inside_markup():
    body = "**This opening begins in bold and continues with enough words to receive the intentional opening treatment. " + " ".join(["reader"] * 45) + "**"
    share_html = narrative_sync.render_share_page({
        "title": "Dropcap Fixture",
        "date": "July 11, 2026",
        "file": "2026-07-11-dropcap-fixture.md",
        "body": body,
    })
    entry_body = extract_share_entry_body(share_html)

    assert 'entry-body__opening entry-body__dropcap' in entry_body
    assert '<strong><span class="entry-dropcap">T</span>his' in entry_body


def test_opening_dropcap_stays_on_short_first_paragraph():
    share_html = narrative_sync.render_share_page({
        "title": "Short Opening Fixture",
        "date": "July 14, 2026",
        "file": "2026-07-14-short-opening-fixture.md",
        "body": (
            "**Did you know that I love taking mushrooms?**\n\n"
            "Settle that into your brainpan a little bit before I proceed.\n\n"
            "Ready?\n\n"
            "Without wading into far too much detail, this deliberately longer paragraph should not receive "
            "an opening drop cap merely because the paragraphs before it are short. " + "reader " * 35
        ),
    })
    entry_body = extract_share_entry_body(share_html)
    reader_css = (ROOT / "archive_reader.css").read_text(encoding="utf-8")

    assert '<p class="entry-body__opening entry-body__dropcap" id="p-001"><strong><span class="entry-dropcap">D</span>id' in entry_body
    assert '<p id="p-004"><span class="entry-dropcap">W</span>' not in entry_body
    assert ".entry-body__opening {\n    display: flow-root;" in reader_css


def test_opening_dropcap_skips_legacy_tag_metadata():
    share_html = narrative_sync.render_share_page({
        "title": "Tagged Opening Fixture",
        "date": "July 14, 2026",
        "file": "2026-07-14-tagged-opening-fixture.md",
        "body": "Tags: Apple News, Tech News\n\n**Once upon a time, the real essay began here.**",
    })
    entry_body = extract_share_entry_body(share_html)

    assert '<p id="p-001">Tags: Apple News, Tech News</p>' in entry_body
    assert '<p class="entry-body__opening entry-body__dropcap" id="p-002"><strong><span class="entry-dropcap">O</span>nce' in entry_body


def test_canonical_archive_page_uses_markdown_image_when_no_publisher_image_exists():
    share_html = narrative_sync.render_share_page({
        "title": "Markdown Image Fixture",
        "date": "May 30, 2026",
        "file": "2026-05-30-markdown-image-fixture.md",
        "body": f"Introductory paragraph.\n\n![Markdown alt text]({IMAGE_TWO} \"Markdown caption\")",
    })
    meta = extract_meta(share_html)

    assert meta["og:image"] == IMAGE_TWO
    assert meta["og:image:secure_url"] == IMAGE_TWO
    assert meta["twitter:image"] == IMAGE_TWO
    assert meta["og:image:type"] == "image/png"
    assert "og:image:width" not in meta
    assert "og:image:height" not in meta
    assert meta["og:image:alt"] == "Markdown alt text"


def test_canonical_archive_page_uses_normalized_local_article_image_for_preview():
    share_html = narrative_sync.render_share_page({
        "title": "Local Image Fixture",
        "date": "May 31, 2026",
        "file": "2026-05-31-local-image-fixture.md",
        "body": 'Introductory paragraph.\n\n![Local image](Images/Blog/local-preview.png "Local caption")',
    })
    meta = extract_meta(share_html)

    assert 'src="/Images/Blog/local-preview.png"' in share_html
    assert meta["og:image"] == "https://outsidetheworld.com/Images/Blog/local-preview.png"
    assert meta["og:image:secure_url"] == meta["og:image"]
    assert meta["twitter:image"] == meta["og:image"]
    assert meta["og:image:type"] == "image/png"
    assert "og:image:width" not in meta
    assert "og:image:height" not in meta
    assert meta["og:image:alt"] == "Local image"


def test_canonical_archive_page_uses_normalized_local_html_image_for_preview():
    share_html = narrative_sync.render_share_page({
        "title": "Local HTML Image Fixture",
        "date": "June 1, 2026",
        "file": "2026-06-01-local-html-image-fixture.md",
        "body": (
            "Introductory paragraph.\n\n"
            '<figure><img src="Images/Blog/local-html-preview.jpeg" alt="Local HTML image"></figure>'
        ),
    })
    meta = extract_meta(share_html)

    assert 'src="/Images/Blog/local-html-preview.jpeg"' in share_html
    assert meta["og:image"] == "https://outsidetheworld.com/Images/Blog/local-html-preview.jpeg"
    assert meta["og:image:secure_url"] == meta["og:image"]
    assert meta["twitter:image"] == meta["og:image"]
    assert meta["og:image:type"] == "image/jpeg"
    assert "og:image:width" not in meta
    assert "og:image:height" not in meta
    assert meta["og:image:alt"] == "Local HTML image"


def test_archive_reader_assigns_body_paragraph_ids_only():
    share_html = narrative_sync.render_share_page({
        "title": "Paragraph Id Fixture",
        "date": "June 2, 2026",
        "file": "2026-06-02-paragraph-id-fixture.md",
        "body": (
            "First substantial body paragraph with enough shape to receive the opening reader treatment.\n\n"
            "## A Heading That Should Not Become A Paragraph\n\n"
            "Second body paragraph that can receive a stable generated paragraph id."
        ),
    })
    body = extract_share_entry_body(share_html)

    assert 'id="p-001"' in body
    assert 'id="p-002"' in body
    assert "<h2 id=" not in body


def test_reading_aids_render_only_when_approved_or_previewed():
    with tempfile.TemporaryDirectory() as temp_name:
        temp = Path(temp_name)
        input_dir = temp / "current_narrative"
        reading_dir = temp / "reading_aids"
        input_dir.mkdir()
        reading_dir.mkdir()
        filename = "2026-06-03-aid-fixture.md"
        source = (
            "# Aid Fixture\n"
            "Date: June 3, 2026\n\n"
            "First substantial paragraph that gives the reader a place to begin and enough language for a checkpoint.\n\n"
            "Second substantial paragraph that is dense enough to carry a clarify note without attaching the note to page chrome.\n"
        )
        (input_dir / filename).write_text(source, encoding="utf-8")
        post = {
            "title": "Aid Fixture",
            "date": "June 3, 2026",
            "file": filename,
            "body": "\n".join(source.splitlines()[2:]).strip(),
        }

        old_input = narrative_sync.input_folder
        old_reading = narrative_sync.reading_aids_folder
        try:
            narrative_sync.input_folder = str(input_dir)
            narrative_sync.reading_aids_folder = str(reading_dir)
            sidecar = {
                "slug": "aid-fixture",
                "essayHash": narrative_sync.essay_hash_for_post(post),
                "reviewStatus": "draft",
                "generatedAt": "2026-06-03T00:00:00Z",
                "model": "test-model",
                "signalBrief": {"text": "A quiet orientation for local preview.", "locked": False},
                "readerMap": [
                    {"label": "01", "title": "Opening", "summary": "The essay begins by locating the reader.", "locked": False}
                ],
                "checkpoints": [
                    {"afterParagraphId": "p-001", "label": "Where We Are", "text": "The first movement has established the ground.", "locked": False}
                ],
                "plainSignals": [
                    {"paragraphId": "p-002", "label": "Plain Signal", "text": "In plain terms, this passage names the pressure point.", "locked": False}
                ],
            }
            (reading_dir / "aid-fixture.json").write_text(json.dumps(sidecar), encoding="utf-8")

            public_html = narrative_sync.render_share_page(post)
            preview_html = narrative_sync.render_share_page(post, include_draft_reading_aids=True)
            assert "Article Summary" not in public_html
            assert "Article Summary" in preview_html
            assert 'data-reading-tools="off"' in preview_html
            assert 'data-reading-tools-toggle>Show Reading Tools</button>' in preview_html
            assert "Signal Brief" not in preview_html
            assert "Plain Signal" not in preview_html
            assert 'aria-controls="reading-aid-summary"' in preview_html
            assert 'id="reading-aid-summary" hidden' in preview_html
            assert "Clarify" in preview_html
            assert "Where We Are" in preview_html

            sidecar["reviewStatus"] = "approved"
            (reading_dir / "aid-fixture.json").write_text(json.dumps(sidecar), encoding="utf-8")
            approved_html = narrative_sync.render_share_page(post)
            assert "Article Summary" in approved_html
            assert 'data-reading-tools-toggle>Show Reading Tools</button>' in approved_html
            assert "Signal Brief" not in approved_html
            assert "Plain Signal" not in approved_html
        finally:
            narrative_sync.input_folder = old_input
            narrative_sync.reading_aids_folder = old_reading


def test_residue_archive_legacy_urls_resolve_to_canonical_archive_paths():
    residue = (ROOT / "residue_archive.html").read_text(encoding="utf-8")

    assert "function redirectLegacyPostUrlIfNeeded()" in residue
    assert "window.location.replace(canonicalUrl.toString())" in residue
    assert "const postId = params.get('post')" in residue
    assert "return new URL(buildCanonicalArchivePath(post), window.location.origin).toString();" in residue
    assert "url.searchParams.set('post'" not in residue
    assert "residue_archive.html?post=" not in residue


def test_residue_archive_hydrates_complete_canonical_entries_without_relative_path_drift():
    residue = (ROOT / "residue_archive.html").read_text(encoding="utf-8")

    assert '<base href="/">' in residue
    assert "function normalizeCanonicalArchivePath" in residue
    assert "async function hydrateCanonicalEntry" in residue
    assert "new DOMParser()" in residue
    assert "canonicalDocument.querySelector('.entry-body')" in residue
    assert "canonicalDocument.querySelector('.entry-feature')" in residue
    assert "fetch(readerPath" in residue
    assert "Open Standalone Reader" in residue
    assert "const previewBody =" not in residue
    assert "event.state && event.state.postId" in residue


def test_reader_byline_link_uses_reader_palette_instead_of_browser_blue():
    reader_css = (ROOT / "archive_reader.css").read_text(encoding="utf-8")

    assert ".entry-byline a" in reader_css
    assert "color: inherit" in reader_css


def test_residue_directory_keeps_controls_fixed_and_gives_the_post_list_one_scroll_owner():
    residue = (ROOT / "residue_archive.html").read_text(encoding="utf-8")

    assert "flex: 1 1 0" in residue
    assert "min-height: 0" in residue
    assert "overscroll-behavior-y: contain" in residue
    assert "scrollbar-gutter: stable" in residue
    assert "list.scrollTop = 0" in residue
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in residue
    assert "@media (min-width: 900px) and (max-height: 760px)" in residue


def test_share_copy_search_and_feed_paths_do_not_emit_legacy_residue_urls():
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    residue = (ROOT / "residue_archive.html").read_text(encoding="utf-8")
    archive_pages = "".join(path.read_text(encoding="utf-8") for path in (ROOT / "archive").glob("*.html"))

    assert "residue_archive.html?post=" not in index
    assert "residue_archive.html?post=" not in residue
    assert "residue_archive.html?post=" not in archive_pages
    assert "archive/Images/" not in archive_pages
    assert 'src="Images/' not in archive_pages
    assert re.search(r'<img\b[^>]*\bsrc="(?!https?://|/)', archive_pages) is None
    assert "buildCanonicalArchivePath(post)" in index
    assert "buildCanonicalArchivePath(post)" in residue

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        narrative_data = temp / "narrative_data.js"
        fragments_data = temp / "fragments_data.js"
        output = temp / "atom.xml"
        narrative_data.write_text(
            'const current_narrative = [{'
            '"title":"Missing Share Path",'
            '"date":"May 30, 2026",'
            '"file":"2026-05-30-missing-share-path.md",'
            '"body":"Visible summary text."'
            '}];',
            encoding="utf-8",
        )
        fragments_data.write_text("window.otw_fragments = [];", encoding="utf-8")

        old_narrative = atom_feed.NARRATIVE_DATA
        old_fragments = atom_feed.FRAGMENTS_DATA
        old_output = atom_feed.OUTPUT
        try:
            atom_feed.NARRATIVE_DATA = narrative_data
            atom_feed.FRAGMENTS_DATA = fragments_data
            atom_feed.OUTPUT = output
            atom_feed.main()
        finally:
            atom_feed.NARRATIVE_DATA = old_narrative
            atom_feed.FRAGMENTS_DATA = old_fragments
            atom_feed.OUTPUT = old_output

        atom_text = output.read_text(encoding="utf-8")
        assert "https://outsidetheworld.com/archive/2026-05-30-missing-share-path.html" in atom_text
        assert "residue_archive.html?post=" not in atom_text


def test_public_pages_use_appropriate_post_payloads():
    view_post = (ROOT / "view_post.html").read_text(encoding="utf-8")
    residue = (ROOT / "residue_archive.html").read_text(encoding="utf-8")
    post = (ROOT / "post.html").read_text(encoding="utf-8")

    assert "window.renderOtwPost ? window.renderOtwPost(post)" in view_post
    assert "narrative_index.json" in residue
    assert '<script src="narrative_data.js"' not in residue
    assert "buildCanonicalArchivePath(post)" in residue
    assert "renderOtwMarkdown" in post


def test_public_css_contract_exists_everywhere():
    for path in [
        ROOT / "theme.css",
        ROOT / "view_post.html",
        ROOT / "residue_archive.html",
    ]:
        text = path.read_text(encoding="utf-8")
        for token in [
            "otw-figure--small",
            "otw-figure--medium",
            "otw-figure--large",
            "otw-figure--original",
            "otw-figure--align-left",
            "otw-figure--align-center",
            "otw-figure--align-right",
            "otw-figure--wrap-left",
            "otw-figure--wrap-right",
            "float: none",
        ]:
            assert token in text


def test_publisher_preview_modes_keep_quick_preview_browser_only():
    publisher = (ROOT / "publisher.html").read_text(encoding="utf-8")
    preview = (ROOT / "publisher_preview.html").read_text(encoding="utf-8")

    assert "async function renderDraftWithProductionRenderer" in publisher
    assert "function openDraftPreview" in publisher
    assert "publisher_preview.html?draft=" in publisher
    assert publisher.count("return renderDraftWithProductionRenderer({") == 1
    assert publisher.count("localPublisherApi('/api/draft-preview'") == 1
    assert "Preview saved Markdown in this tab" in publisher
    assert "window.location.assign(previewUrl);" in publisher
    assert publisher.count("const previewWindow = reservePreviewWindow();") == 2
    assert 'id="publisherServerNotice"' in publisher
    assert "function syncPublisherServerAvailability()" in publisher
    assert "function reservePreviewWindow()" in publisher
    assert "function navigateReservedPreviewWindow(previewWindow, previewUrl)" in publisher
    assert "Preview tab blocked. Allow pop-ups for this local publisher and try again." in publisher
    assert "window.open(previewShellUrl(" not in publisher
    assert "Quick Preview opens in this tab." in publisher
    assert preview.count("data-publisher-return") == 4
    assert "publisher.html?resume=${Date.now()}" in preview


def test_publisher_just_write_mode_preserves_the_composer_contract():
    publisher = (ROOT / "publisher.html").read_text(encoding="utf-8")

    for token in [
        'id="justWriteBtn"',
        'id="justWriteExitBtn"',
        'aria-pressed="false">Just Write</button>',
        'aria-label="Exit Just Write"',
        "function enterJustWrite()",
        "function exitJustWrite({ exitFullscreen = true } = {})",
        "requestFullscreen",
        "webkitRequestFullscreen",
        "fullscreenchange",
        "webkitfullscreenchange",
        "justWriteBtn.addEventListener('click', enterJustWrite)",
        "justWriteExitBtn.addEventListener('click', exitJustWrite)",
        "document.documentElement.classList.add('is-just-writing')",
        "document.body.classList.add('is-just-writing')",
        "body.is-just-writing .editor",
        "body.is-just-writing .article-title-stack",
        "saveDraft();",
        "rememberSelection();",
        "restoreSelection();",
        "function wrapRootInlineRunAtRange(range)",
        "wrapRootInlineRunAtRange(range);",
        "editor.replaceChildren(initialParagraph);",
    ]:
        assert token in publisher

    assert publisher.count('id="editor"') == 1
    assert "contenteditable=\"true\"" in publisher
    assert "isJustWriting()" in publisher


def run():
    tests = [
        test_existing_markdown_without_metadata_degrades_cleanly,
        test_local_image_paths_normalize_to_root_relative_paths,
        test_metadata_parser_edge_cases_fail_closed,
        test_metadata_cardinality_edge_cases_do_not_break_rendering,
        test_all_image_presentation_options_render_and_css_agrees,
        test_published_image_haze_uses_the_frgmnts_palette,
        test_sanitization_security_for_markdown_and_metadata,
        test_trusted_legacy_figure_blocks_are_preserved_but_sanitized,
        test_reused_image_url_can_keep_distinct_presentation_by_order_after_sanitization,
        test_atom_feed_strips_publisher_metadata_and_stays_valid_xml,
        test_realistic_publisher_fixture_end_to_end,
        test_canonical_archive_page_emits_full_preview_metadata,
        test_canonical_archive_page_prefers_first_article_image_when_present,
        test_explicit_feature_image_drives_opening_and_is_not_duplicated_in_body,
        test_article_shell_has_home_identity_schema_and_consistent_section_levels,
        test_article_shell_adapts_to_length_media_and_opening_structure,
        test_opening_dropcap_wraps_first_visible_letter_inside_markup,
        test_opening_dropcap_stays_on_short_first_paragraph,
        test_opening_dropcap_skips_legacy_tag_metadata,
        test_canonical_archive_page_uses_markdown_image_when_no_publisher_image_exists,
        test_canonical_archive_page_uses_normalized_local_article_image_for_preview,
        test_canonical_archive_page_uses_normalized_local_html_image_for_preview,
        test_archive_reader_assigns_body_paragraph_ids_only,
        test_reading_aids_render_only_when_approved_or_previewed,
        test_residue_archive_legacy_urls_resolve_to_canonical_archive_paths,
        test_residue_archive_hydrates_complete_canonical_entries_without_relative_path_drift,
        test_reader_byline_link_uses_reader_palette_instead_of_browser_blue,
        test_residue_directory_keeps_controls_fixed_and_gives_the_post_list_one_scroll_owner,
        test_share_copy_search_and_feed_paths_do_not_emit_legacy_residue_urls,
        test_public_pages_use_appropriate_post_payloads,
        test_public_css_contract_exists_everywhere,
        test_publisher_preview_modes_keep_quick_preview_browser_only,
        test_publisher_just_write_mode_preserves_the_composer_contract,
    ]
    for test in tests:
        test()
    print(f"publisher render contract tests passed: {len(tests)}")


if __name__ == "__main__":
    run()
