(function (global) {
  const hasDocument = Boolean(global.document);
  const imageMarkdownPattern = /!\[([^\]]*)\]\((\S+?)(?:\s+"((?:\\"|[^"])*)")?\)/g;
  const imageMarkdownBlockPattern = /!\[([^\]]*)\]\((\S+?)(?:\s+"((?:\\"|[^"])*)")?\)/;

  function escapeHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function markdownUnescape(value) {
    return String(value || "")
      .replace(/\\"/g, '"')
      .replace(/\\\[/g, "[")
      .replace(/\\\]/g, "]")
      .replace(/\\\\/g, "\\");
  }

  function safeLinkUrl(value) {
    const url = String(value || "").trim();
    if (/^(https?:|mailto:|#|\/)/i.test(url)) return url;
    return "";
  }

  function safeImageUrl(value) {
    const url = String(value || "").trim();
    if (!url || /^(javascript:|data:|blob:)/i.test(url)) return "";
    if (/^(https?:|\/)/i.test(url)) return url;
    return "";
  }

  function normalizeChoice(value, allowed, fallback) {
    const normalized = String(value || "").trim().toLowerCase();
    return allowed.includes(normalized) ? normalized : fallback;
  }

  function normalizeTextAlign(value) {
    const normalized = String(value || "").trim().toLowerCase();
    if (normalized === "center" || normalized.includes("center")) return "center";
    if (normalized === "right" || normalized === "end" || normalized.includes("right")) return "right";
    return "";
  }

  function normalizeImagePresentation(value = {}) {
    return {
      displaySize: normalizeChoice(value.displaySize, ["x-small", "small", "medium", "large", "original"], "medium"),
      alignment: normalizeChoice(value.alignment, ["left", "center", "right"], "center"),
      wrapMode: normalizeChoice(value.wrapMode, ["none", "wrap-left", "wrap-right"], "none")
    };
  }

  function normalizePublisherImages(metadata = {}) {
    const images = Array.isArray(metadata.images) ? metadata.images : [];
    const blocks = Array.isArray(metadata.blocks) ? metadata.blocks : [];
    const byUrl = new Map();
    const byId = new Map();
    const ordered = [];

    images.forEach((image) => {
      const url = safeImageUrl(image && (image.url || image.media?.url || image.media?.publishUrl));
      if (!url) return;
      const normalized = {
        id: String(image.id || image.imageRef || ""),
        url,
        objectKey: String(image.objectKey || image.media?.objectKey || ""),
        alt: String(image.alt || ""),
        caption: String(image.caption || ""),
        credit: String(image.credit || ""),
        width: Math.max(0, Number(image.width || image.media?.width) || 0),
        height: Math.max(0, Number(image.height || image.media?.height) || 0),
        ...normalizeImagePresentation(image)
      };
      byUrl.set(url, normalized);
      if (normalized.id) byId.set(normalized.id, normalized);
    });

    blocks.forEach((block) => {
      if (!block || block.type !== "image") return;
      const url = safeImageUrl(block.url || block.media?.url || block.media?.publishUrl);
      const image = byId.get(String(block.imageRef || block.id || "")) || (url ? byUrl.get(url) : null);
      if (!image && !url) return;
      const normalized = {
        ...(image || {}),
        id: String(block.imageRef || block.id || image?.id || ""),
        url: url || image.url,
        objectKey: String(block.objectKey || image?.objectKey || ""),
        alt: String(block.alt || image?.alt || ""),
        caption: String(block.caption || image?.caption || ""),
        credit: String(block.credit || image?.credit || ""),
        width: Math.max(0, Number(block.width || image?.width) || 0),
        height: Math.max(0, Number(block.height || image?.height) || 0),
        ...normalizeImagePresentation({ ...image, ...block })
      };
      byUrl.set(normalized.url, normalized);
      if (normalized.id) byId.set(normalized.id, normalized);
      ordered.push(normalized);
    });

    return {
      byUrl,
      ordered: ordered.length ? ordered : Array.from(byUrl.values())
    };
  }

  function sanitizeRenderedHtml(root) {
    root.querySelectorAll("script, iframe, object, embed").forEach((node) => node.remove());
    root.querySelectorAll("*").forEach((node) => {
      Array.from(node.attributes).forEach((attr) => {
        const name = attr.name.toLowerCase();
        const value = attr.value || "";
        if (name.startsWith("on")) {
          node.removeAttribute(attr.name);
          return;
        }
        if ((name === "href" || name === "src") && /^(javascript:|data:|blob:)/i.test(value.trim())) {
          node.removeAttribute(attr.name);
        }
      });
    });
  }

  const richInlineTags = new Set(["A", "B", "BR", "CODE", "EM", "FONT", "I", "SPAN", "STRONG", "U"]);
  const richInlineStyleProperties = new Set([
    "background-color",
    "font-style",
    "font-weight",
    "text-decoration",
    "text-decoration-line"
  ]);
  const richLineSpacing = {
    "1.0": "1",
    "1.15": "1.15",
    "1.5": "1.5",
    "2.0": "2"
  };

  function safeStyleValue(value) {
    const normalized = String(value || "").trim();
    if (!normalized || /(url\s*\(|expression\s*\(|javascript:|data:|blob:)/i.test(normalized)) return "";
    return normalized;
  }

  function sanitizeInlineStyle(value) {
    const probe = document.createElement("span");
    probe.setAttribute("style", String(value || ""));
    const clean = document.createElement("span");
    Array.from(probe.style).forEach((property) => {
      const normalized = property.toLowerCase();
      if (!richInlineStyleProperties.has(normalized)) return;
      const styleValue = safeStyleValue(probe.style.getPropertyValue(property));
      if (styleValue) {
        clean.style.setProperty(normalized, styleValue);
      }
    });
    return clean.getAttribute("style") || "";
  }

  function sanitizeEnhancedInlineHtml(value) {
    const source = document.createElement("template");
    source.innerHTML = String(value || "");

    function cleanNode(node) {
      if (node.nodeType === Node.TEXT_NODE) {
        return document.createTextNode(node.textContent || "");
      }
      if (node.nodeType !== Node.ELEMENT_NODE) {
        return document.createDocumentFragment();
      }

      const tag = node.tagName.toUpperCase();
      const fragmentChildren = () => {
        const fragment = document.createDocumentFragment();
        node.childNodes.forEach((child) => fragment.append(cleanNode(child)));
        return fragment;
      };
      if (!richInlineTags.has(tag)) {
        return fragmentChildren();
      }
      if (tag === "BR") {
        return document.createElement("br");
      }

      const clean = document.createElement(tag === "FONT" ? "span" : tag.toLowerCase());
      if (tag === "A") {
        const href = safeLinkUrl(node.getAttribute("href") || "");
        if (href) {
          clean.setAttribute("href", href);
        }
      }
      if (node.getAttribute("style")) {
        const style = sanitizeInlineStyle(node.getAttribute("style"));
        if (style) {
          clean.setAttribute("style", style);
        }
      }
      node.childNodes.forEach((child) => clean.append(cleanNode(child)));
      return clean;
    }

    const clean = document.createElement("template");
    source.content.childNodes.forEach((node) => clean.content.append(cleanNode(node)));
    return clean.innerHTML.trim();
  }

  function normalizedText(value) {
    return String(value || "").replace(/\s+/g, " ").trim();
  }

  function isPublisherSubheadElement(element, metadata) {
    return Boolean(
      metadata
      && metadata.subhead
      && element
      && element.tagName === "P"
      && normalizedText(element.textContent) === normalizedText(metadata.subhead)
    );
  }

  function publisherBlockMatchesElement(block, element) {
    if (!block || !element) return false;
    const tag = element.tagName;
    if (block.type === "paragraph") return tag === "P";
    if (block.type === "heading") return /^H[1-6]$/.test(tag);
    if (block.type === "quote") return tag === "BLOCKQUOTE";
    if (block.type === "list") return tag === "UL" || tag === "OL";
    if (block.type === "divider") return tag === "HR";
    if (block.type === "image") return tag === "FIGURE" || tag === "IMG" || Boolean(element.querySelector("img"));
    return false;
  }

  function applyPublisherLineSpacing(element, value) {
    const lineHeight = richLineSpacing[String(value || "").trim()];
    if (element && lineHeight) {
      element.style.lineHeight = lineHeight;
    }
  }

  function applyPublisherTextAlign(element, value) {
    const alignment = normalizeTextAlign(value);
    if (element && alignment) {
      element.style.textAlign = alignment;
    }
  }

  function applyPublisherTextBlock(element, block) {
    if (!element || !block) return;
    const htmlValue = typeof block.html === "string" ? block.html : "";
    if (htmlValue.trim()) {
      element.innerHTML = sanitizeEnhancedInlineHtml(htmlValue);
    }
    applyPublisherLineSpacing(element, block.lineSpacing);
    applyPublisherTextAlign(element, block.textAlign);
  }

  function applyPublisherListBlock(element, block) {
    if (!element || !block) return;
    const items = Array.from(element.children).filter((child) => child.tagName === "LI");
    const metadataItems = Array.isArray(block.items) ? block.items : [];
    items.forEach((item, index) => {
      const metadataItem = metadataItems[index];
      const htmlValue = typeof metadataItem?.html === "string" ? metadataItem.html : "";
      if (htmlValue.trim()) {
        item.innerHTML = sanitizeEnhancedInlineHtml(htmlValue);
      }
    });
    applyPublisherLineSpacing(element, block.lineSpacing);
    applyPublisherTextAlign(element, block.textAlign);
  }

  function applyPublisherRichBlocks(root, metadata = {}) {
    const blocks = Array.isArray(metadata.blocks) ? metadata.blocks : [];
    if (!blocks.length) return;

    const elements = Array.from(root.children).filter((element) => {
      return /^(P|H[1-6]|BLOCKQUOTE|UL|OL|HR|FIGURE|IMG)$/.test(element.tagName)
        || Boolean(element.querySelector && element.querySelector("img"));
    });
    let cursor = 0;

    blocks.forEach((block) => {
      if (!block || !block.type) return;
      while (cursor < elements.length && isPublisherSubheadElement(elements[cursor], metadata)) {
        cursor += 1;
      }
      while (cursor < elements.length && !publisherBlockMatchesElement(block, elements[cursor])) {
        cursor += 1;
      }
      if (cursor >= elements.length) return;

      const element = elements[cursor];
      cursor += 1;
      if (block.type === "paragraph" || block.type === "heading" || block.type === "quote") {
        applyPublisherTextBlock(element, block);
      } else if (block.type === "list") {
        applyPublisherListBlock(element, block);
      }
    });
  }

  function renderFallbackImage(match, asBlock = false) {
    const alt = markdownUnescape(match[1] || "");
    const src = safeImageUrl(match[2] || "");
    const caption = markdownUnescape(match[3] || "").trim();
    if (!src) return "";
    const title = caption && !asBlock ? ` title="${escapeHtml(caption)}"` : "";
    const image = `<img src="${escapeHtml(src)}" alt="${escapeHtml(alt)}"${title}>`;
    if (asBlock && caption) {
      return `<figure class="otw-figure">${image}<figcaption><em>${escapeHtml(caption)}</em></figcaption></figure>`;
    }
    return image;
  }

  function renderFallbackInline(value) {
    const snippets = [];
    const stash = (html) => {
      const token = `OTWRENDERPLACEHOLDER${snippets.length}END`;
      snippets.push({ token, html });
      return token;
    };

    let rendered = String(value || "")
      .replace(imageMarkdownPattern, (...args) => stash(renderFallbackImage(args)))
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_match, label, url) => {
        const safeUrl = safeLinkUrl(url);
        return stash(safeUrl ? `<a href="${escapeHtml(safeUrl)}">${escapeHtml(label)}</a>` : escapeHtml(label));
      })
      .replace(/\*\*([^*]+)\*\*/g, (_match, text) => stash(`<strong>${escapeHtml(text)}</strong>`))
      .replace(/__([^_]+)__/g, (_match, text) => stash(`<strong>${escapeHtml(text)}</strong>`))
      .replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, (_match, prefix, text) => `${prefix}${stash(`<em>${escapeHtml(text)}</em>`)}`)
      .replace(/(^|[^_])_([^_\n]+)_(?!_)/g, (_match, prefix, text) => `${prefix}${stash(`<em>${escapeHtml(text)}</em>`)}`)
      .replace(/`([^`]+)`/g, (_match, text) => stash(`<code>${escapeHtml(text)}</code>`));

    rendered = escapeHtml(rendered);
    snippets.forEach(({ token, html }) => {
      rendered = rendered.replace(token, html);
    });
    return rendered;
  }

  function applyFigurePresentation(figure, presentation) {
    if (!figure || !presentation) return;
    const normalized = normalizeImagePresentation(presentation);
    figure.classList.add(
      "otw-figure",
      `otw-figure--${normalized.displaySize}`,
      `otw-figure--align-${normalized.alignment}`,
      `otw-figure--${normalized.wrapMode}`
    );
    figure.dataset.displaySize = normalized.displaySize;
    figure.dataset.alignment = normalized.alignment;
    figure.dataset.wrapMode = normalized.wrapMode;
    if (Number(presentation.width) > 0) {
      figure.style.setProperty("--otw-figure-natural-width", `${Math.round(Number(presentation.width))}px`);
    }
  }

  function ensureFigureForImage(image) {
    const existing = image.closest("figure");
    if (existing) return existing;

    const figure = document.createElement("figure");
    figure.className = "otw-figure";
    const parent = image.parentElement;
    const standaloneParagraph = parent
      && parent.tagName === "P"
      && Array.from(parent.childNodes).every((node) => {
        if (node === image) return true;
        return node.nodeType === Node.TEXT_NODE && !node.textContent.trim();
      });

    image.replaceWith(figure);
    figure.appendChild(image);
    if (standaloneParagraph) {
      parent.replaceWith(figure);
    }
    return figure;
  }

  function applyOtwPublisherMetadata(html, metadata = {}) {
    if (!hasDocument || !html) return html || "";
    const images = normalizePublisherImages(metadata);
    const template = document.createElement("template");
    template.innerHTML = html;
    sanitizeRenderedHtml(template.content);

    const orderedByUrl = new Map();
    images.ordered.forEach((image) => {
      if (!image || !image.url) return;
      const existing = orderedByUrl.get(image.url) || [];
      existing.push(image);
      orderedByUrl.set(image.url, existing);
    });

    template.content.querySelectorAll("img").forEach((image) => {
      const src = safeImageUrl(image.getAttribute("src") || "");
      const orderedMatches = orderedByUrl.get(src);
      const presentation = orderedMatches && orderedMatches.length
        ? orderedMatches.shift()
        : images.byUrl.get(src);
      if (!presentation) return;

      const figure = ensureFigureForImage(image);
      applyFigurePresentation(figure, presentation);

      if (presentation.alt) {
        image.setAttribute("alt", presentation.alt);
      }

      const caption = presentation.caption.trim();
      const credit = presentation.credit.trim();
      if (caption || credit) {
        let figcaption = figure.querySelector("figcaption");
        if (!figcaption) {
          figcaption = document.createElement("figcaption");
          figure.appendChild(figcaption);
        }
        figcaption.textContent = "";
        if (caption) {
          const emphasis = document.createElement("em");
          emphasis.textContent = caption;
          figcaption.appendChild(emphasis);
        }
        if (credit) {
          const creditElement = document.createElement("span");
          creditElement.className = "otw-figure-credit";
          creditElement.textContent = credit;
          figcaption.appendChild(creditElement);
        }
      }
    });

    applyPublisherRichBlocks(template.content, metadata);
    return template.innerHTML;
  }

  function renderFallbackMarkdown(markdown) {
    return String(markdown || "")
      .replace(/\r\n?/g, "\n")
      .split(/\n{2,}/)
      .map((chunk) => {
        const raw = chunk.trim();
        if (!raw) return "";
        const imageMatch = raw.match(imageMarkdownBlockPattern);
        if (imageMatch && imageMatch[0] === raw) {
          return renderFallbackImage(imageMatch, true);
        }
        if (raw === "---") return "<hr>";
        const lines = raw.split("\n");
        if (lines.every((line) => /^\s*>\s?/.test(line))) {
          const quote = lines.map((line) => line.replace(/^\s*>\s?/, "")).join("\n");
          return `<blockquote>${renderFallbackInline(quote).replace(/\n/g, "<br>")}</blockquote>`;
        }
        if (lines.every((line) => /^\s*[-+*]\s+/.test(line))) {
          return `<ul>${lines.map((line) => `<li>${renderFallbackInline(line.replace(/^\s*[-+*]\s+/, ""))}</li>`).join("")}</ul>`;
        }
        if (lines.every((line) => /^\s*\d+[.)]\s+/.test(line))) {
          return `<ol>${lines.map((line) => `<li>${renderFallbackInline(line.replace(/^\s*\d+[.)]\s+/, ""))}</li>`).join("")}</ol>`;
        }
        const heading = raw.match(/^(#{1,3})\s+(.+)$/s);
        if (heading && !heading[2].includes("\n")) {
          const level = heading[1].length;
          return `<h${level}>${renderFallbackInline(heading[2])}</h${level}>`;
        }
        return `<p>${renderFallbackInline(raw).replace(/\n/g, "<br>")}</p>`;
      })
      .join("");
  }

  function enhanceOtwMarkdownImages(html) {
    if (!hasDocument || !html || (!html.includes("<img") && !html.includes("<figure"))) {
      return html || "";
    }

    const template = document.createElement("template");
    template.innerHTML = html;

    template.content.querySelectorAll("figure").forEach((figure) => {
      figure.classList.add("otw-figure");
    });
    sanitizeRenderedHtml(template.content);

    template.content.querySelectorAll("img[title]").forEach((image) => {
      const caption = (image.getAttribute("title") || "").trim();
      if (!caption || image.closest("figure")) return;

      const figure = document.createElement("figure");
      figure.className = "otw-figure";

      const imageClone = image.cloneNode(true);
      imageClone.removeAttribute("title");

      const figcaption = document.createElement("figcaption");
      const emphasis = document.createElement("em");
      emphasis.textContent = caption;
      figcaption.appendChild(emphasis);
      figure.appendChild(imageClone);
      figure.appendChild(figcaption);

      const parent = image.parentElement;
      const isStandaloneParagraph = parent
        && parent.tagName === "P"
        && Array.from(parent.childNodes).every((node) => {
          if (node === image) return true;
          return node.nodeType === Node.TEXT_NODE && !node.textContent.trim();
        });

      if (isStandaloneParagraph) {
        parent.replaceWith(figure);
      }
    });

    return template.innerHTML;
  }

  function renderOtwMarkdown(markdown, markedOptions = {}) {
    const parser = global.marked && typeof global.marked.parse === "function"
      ? global.marked.parse.bind(global.marked)
      : null;
    const html = parser
      ? parser(String(markdown || ""), markedOptions)
      : renderFallbackMarkdown(markdown);
    return enhanceOtwMarkdownImages(html);
  }

  function renderOtwPost(post, markedOptions = {}) {
    const html = renderOtwMarkdown(post && post.body ? post.body : "", markedOptions);
    return applyOtwPublisherMetadata(html, post && post.publisher ? post.publisher : {});
  }

  global.renderOtwMarkdown = renderOtwMarkdown;
  global.renderOtwPost = renderOtwPost;
  global.applyOtwPublisherMetadata = applyOtwPublisherMetadata;
  global.enhanceOtwMarkdownImages = enhanceOtwMarkdownImages;
}(window));
