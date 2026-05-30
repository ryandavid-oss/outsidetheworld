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
    match = re.search(r'<div class="entry-body">\s*([\s\S]*?)\s*</div>\s*<div class="archive-actions">', value)
    assert match
    return match.group(1)


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


def test_metadata_parser_edge_cases_fail_closed():
    missing_metadata = "Just body text."
    metadata, cleaned = narrative_sync.extract_publisher_metadata(missing_metadata)
    assert metadata == {}
    assert cleaned == missing_metadata

    cases = [
        ('<!-- otw-publisher\n{"schema":\n-->\nText.', "malformed"),
        (publisher_comment({"schema": "wrong.schema", "version": 1}) + "\nText.", "wrong schema"),
        (publisher_comment({"schema": "otw.publisher.post", "version": 2, "images": [], "blocks": []}) + "\nText.", "wrong version"),
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
    sizes = ["small", "medium", "large", "original"]
    alignments = ["left", "center", "right"]
    wraps = ["none", "wrap-left", "wrap-right"]
    css = (ROOT / "theme.css").read_text(encoding="utf-8")

    assert "sizes: small, medium, large, original" in css
    assert "alignments: left, center, right" in css
    assert "wraps: none, wrap-left, wrap-right" in css
    assert "max-width: 100%" in css
    assert "height: auto" in css
    assert "float: none" in css
    assert "object-fit: cover" not in css[css.index(".otw-figure"):css.index("/* 6. NAVIGATION")]

    for size in sizes:
        for alignment in alignments:
            for wrap in wraps:
                metadata = {
                    "schema": "otw.publisher.post",
                    "version": 1,
                    "images": [{"id": "image", "url": IMAGE_ONE, "alt": "Alt", "caption": "Caption", "displaySize": size, "alignment": alignment, "wrapMode": wrap}],
                    "blocks": [{"id": "image", "type": "image", "imageRef": "image", "url": IMAGE_ONE, "displaySize": size, "alignment": alignment, "wrapMode": wrap}],
                }
                html = narrative_sync.markdown_to_html(f'![Alt]({IMAGE_ONE} "Caption")', metadata)
                assert f"otw-figure--{size}" in html
                assert f"otw-figure--align-{alignment}" in html
                assert f"otw-figure--{wrap}" in html
                assert 'alt="Alt"' in html
                assert "<figcaption><em>Caption</em></figcaption>" in html


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
        ],
    }
    body = (
        f'![Safe]({IMAGE_ONE} "Safe")\n\n'
        "[bad link](javascript:alert(1))\n\n"
        '![bad js](javascript:alert(1) "Bad")\n\n'
        '![bad data](data:image/png;base64,abc "Bad")\n\n'
        '![bad blob](blob:https://example.test/local "Bad")'
    )
    html = narrative_sync.markdown_to_html(body, malicious_metadata)

    assert "&lt;script&gt;" in html
    assert "&lt;script&gt;alert(\"caption\")&lt;/script&gt;" in html
    assert '<script>alert("alt")</script>' not in html
    assert '<script>alert("caption")</script>' not in html
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
            "<em>A field note from the new desk</em>",
            "otw-figure--small",
            "otw-figure--align-right",
            "otw-figure--wrap-left",
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


def test_public_pages_use_shared_post_renderer():
    personal = (ROOT / "personal.html").read_text(encoding="utf-8")
    view_post = (ROOT / "view_post.html").read_text(encoding="utf-8")
    residue = (ROOT / "residue_archive.html").read_text(encoding="utf-8")
    post = (ROOT / "post.html").read_text(encoding="utf-8")

    assert "renderOtwPost(post)" in personal
    assert "window.renderOtwPost ? window.renderOtwPost(post)" in view_post
    assert "window.renderOtwPost" in residue
    assert "renderOtwMarkdown" in post


def test_public_css_contract_exists_everywhere():
    for path in [
        ROOT / "theme.css",
        ROOT / "personal.html",
        ROOT / "view_post.html",
        ROOT / "residue_archive.html",
        ROOT / "narrative_sync.py",
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


def run():
    tests = [
        test_existing_markdown_without_metadata_degrades_cleanly,
        test_metadata_parser_edge_cases_fail_closed,
        test_metadata_cardinality_edge_cases_do_not_break_rendering,
        test_all_image_presentation_options_render_and_css_agrees,
        test_sanitization_security_for_markdown_and_metadata,
        test_trusted_legacy_figure_blocks_are_preserved_but_sanitized,
        test_reused_image_url_can_keep_distinct_presentation_by_order_after_sanitization,
        test_atom_feed_strips_publisher_metadata_and_stays_valid_xml,
        test_realistic_publisher_fixture_end_to_end,
        test_public_pages_use_shared_post_renderer,
        test_public_css_contract_exists_everywhere,
    ]
    for test in tests:
        test()
    print(f"publisher render contract tests passed: {len(tests)}")


if __name__ == "__main__":
    run()
