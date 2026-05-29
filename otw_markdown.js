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

  function renderFallbackImage(match, asBlock = false) {
    const alt = markdownUnescape(match[1] || "");
    const src = match[2] || "";
    const caption = markdownUnescape(match[3] || "").trim();
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
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_match, label, url) => stash(`<a href="${escapeHtml(url)}">${escapeHtml(label)}</a>`))
      .replace(/\*\*([^*]+)\*\*/g, (_match, text) => stash(`<strong>${escapeHtml(text)}</strong>`))
      .replace(/`([^`]+)`/g, (_match, text) => stash(`<code>${escapeHtml(text)}</code>`));

    rendered = escapeHtml(rendered);
    snippets.forEach(({ token, html }) => {
      rendered = rendered.replace(token, html);
    });
    return rendered;
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

  global.renderOtwMarkdown = renderOtwMarkdown;
  global.enhanceOtwMarkdownImages = enhanceOtwMarkdownImages;
}(window));
