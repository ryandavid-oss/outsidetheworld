# OTW Publisher Metadata

Publisher posts remain Markdown-first. The published `.md` file contains readable fallback Markdown plus an optional `otw-publisher` HTML comment with structured metadata for the OTW rendering pipeline.

```md
<!-- otw-publisher
{
  "schema": "otw.publisher.post",
  "version": 2,
  "formatting": {
    "mode": "otw-enhanced-markdown",
    "version": 1,
    "fallback": "markdown"
  }
}
-->
```

## Compatibility

- Version 1 metadata is still accepted for existing posts.
- Version 2 adds rich editorial formatting metadata.
- Non-OTW Markdown renderers ignore the comment and render the fallback Markdown body.
- OTW renderers sanitize the metadata before applying it.

## Images

Image presentation remains metadata-driven:

- `displaySize`: `x-small`, `small`, `medium`, `large`, `original`
- `alignment`: `left`, `center`, `right`
- `wrapMode`: `none`, `wrap-left`, `wrap-right`

The Markdown image syntax remains:

```md
![Alt text](image-url "Visible caption")
```

## Rich Text

Version 2 body blocks can include sanitized inline HTML:

- `blocks[].html`
- `blocks[].items[].html` for list items

This preserves publisher-only visual formatting such as:

- Text color
- Highlight color
- Underline
- Bold and italic
- Links
- Inline code
- Line breaks
- Block line spacing through `lineSpacing`

Allowed `lineSpacing` values are `1.0`, `1.15`, `1.5`, and `2.0`.

Allowed inline CSS properties are:

- `color`
- `background-color`
- `font-weight`
- `font-style`
- `text-decoration`
- `text-decoration-line`

Unsafe CSS values such as `url(...)`, `expression(...)`, `javascript:`, `data:`, and `blob:` are removed. Unsupported properties are dropped.

## Design Rule

Markdown is the durable fallback. The metadata comment is the OTW enhancement layer. A plain Markdown reader may not reproduce every visual choice, but the OTW custom pipeline can restore the intended editorial styling while preserving a readable source document.
