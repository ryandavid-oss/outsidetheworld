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

  function normalizeImagePresentation(value = {}) {
    return {
      displaySize: normalizeChoice(value.displaySize, ["small", "medium", "large", "original"], "medium"),
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
      const token = `@@OTW_RENDER_${snippets.length}@@`;
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
    if (!images.byUrl.size) return template.innerHTML;

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
      if (caption) {
        let figcaption = figure.querySelector("figcaption");
        if (!figcaption) {
          figcaption = document.createElement("figcaption");
          figure.appendChild(figcaption);
        }
        let emphasis = figcaption.querySelector("em");
        if (!emphasis) {
          emphasis = document.createElement("em");
          figcaption.textContent = "";
          figcaption.appendChild(emphasis);
        }
        emphasis.textContent = caption;
      }
    });

    return template.innerHTML;
  }

  function renderFallbackMarkdown(markdown) {
    return String(markdown || "")
      .split(/\n{2,}/)
      .map((chunk) => {
        const raw = chunk.trim();
        const imageMatch = raw.match(imageMarkdownBlockPattern);
        if (imageMatch && imageMatch[0] === raw) {
          return renderFallbackImage(imageMatch, true);
        }
        if (raw === "---") return "<hr>";
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
