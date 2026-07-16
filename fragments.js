(() => {
  'use strict';

  const PAGE_SIZE = 10;
  const PUBLIC_FEED_URL = 'https://api.frgmnts.app/v1/public/fragments/outsidetheworld?limit=200';
  const REQUEST_TIMEOUT_MS = 6000;
  const CACHE_KEY = 'otwFounderFragmentsCacheV2';
  const CACHE_MAX_AGE_MS = 24 * 60 * 60 * 1000;
  const FORCE_LOCAL = new URLSearchParams(window.location.search).get('source') === 'local';

  let allFragments = [];
  let userRegistry = [];
  let visibleCount = PAGE_SIZE;
  let feedSource = 'loading';
  let loadActive = false;

  function isRecord(value) {
    return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
  }

  function firstString(...values) {
    for (const value of values) {
      if (typeof value === 'string' && value.trim()) return value.trim();
    }
    return '';
  }

  function escapeHtml(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function safeWebUrl(value) {
    const raw = typeof value === 'string' ? value.trim() : '';
    if (!raw) return '';
    try {
      const url = new URL(raw);
      return url.protocol === 'http:' || url.protocol === 'https:' ? url.href : '';
    } catch (error) {
      return '';
    }
  }

  function slugify(value) {
    return String(value ?? '')
      .toLowerCase()
      .replace(/&/g, ' and ')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
  }

  const SIGNAL_STYLES = {
    POSITIVITY: {
      label: 'Positivity',
      icon: '<circle cx="12" cy="12" r="3.4" fill="currentColor"></circle><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M18.7 5.3l-2.1 2.1M7.4 16.6l-2.1 2.1"></path>'
    },
    CHECK_IN: {
      label: 'Check-In',
      icon: '<rect x="3.5" y="3.5" width="17" height="17" rx="4.25" fill="currentColor" stroke="none"></rect><path class="signal-cutout" d="M12 16.4 7.7 12.3a2.55 2.55 0 0 1 3.6-3.6l.7.7.7-.7a2.55 2.55 0 0 1 3.6 3.6Z" stroke="none"></path>'
    },
    REGRET: {
      label: 'Regret',
      icon: '<circle cx="12" cy="12" r="9" fill="currentColor" stroke="none"></circle><path class="signal-cutout signal-stroke" d="M8.1 9.2h5.2a3.7 3.7 0 1 1 0 7.4h-1.1M8.1 9.2l2.4-2.3M8.1 9.2l2.4 2.3"></path>'
    },
    SPIRITUAL: {
      label: 'Spiritual',
      icon: '<path d="m9.1 3.2.8 2.4 2.4.8-2.4.8-.8 2.4-.8-2.4-2.4-.8 2.4-.8Zm6.3 7.1 1.2 3.5 3.5 1.2-3.5 1.2-1.2 3.5-1.2-3.5-3.5-1.2 3.5-1.2 1.2-3.5ZM5.2 13.1l.6 1.8 1.8.6-1.8.6-.6 1.8-.6-1.8-1.8-.6 1.8-.6.6-1.8Z" fill="currentColor" stroke="none"></path>'
    },
    RESIDUE: {
      label: 'Residue',
      icon: '<path d="M3 8.2h10.1c2.7 0 2.7-4 0-4-1.1 0-1.8.6-2.1 1.3M3 12h15.3c3.1 0 3.1-4.7 0-4.7-1.2 0-2.1.7-2.4 1.6M3 15.8h9.5c2.7 0 2.7 4 0 4-1.1 0-1.8-.6-2.1-1.3"></path>'
    },
    COMPLAINT: {
      label: 'Complaint',
      icon: '<path d="M5 3.5h14a2.5 2.5 0 0 1 2.5 2.5v9a2.5 2.5 0 0 1-2.5 2.5h-7l-4.5 3v-3H5A2.5 2.5 0 0 1 2.5 15V6A2.5 2.5 0 0 1 5 3.5Z" fill="currentColor" stroke="none"></path><path class="signal-cutout signal-stroke" d="M12 7v4.5M12 14.5h.01"></path>'
    },
    OTW_BOT: {
      label: 'OTW Bot',
      icon: '<path d="M5 3.5h14a2.5 2.5 0 0 1 2.5 2.5v9a2.5 2.5 0 0 1-2.5 2.5h-7l-4.5 3v-3H5A2.5 2.5 0 0 1 2.5 15V6A2.5 2.5 0 0 1 5 3.5Z" fill="currentColor" stroke="none"></path><path class="signal-cutout signal-stroke signal-dots" d="M8 10.7h.01M12 10.7h.01M16 10.7h.01"></path>'
    },
    FRAGMENT: {
      label: 'Fragment',
      icon: '<path d="M13.5 5H5.7A2.2 2.2 0 0 0 3.5 7.2v11.1a2.2 2.2 0 0 0 2.2 2.2h11.1a2.2 2.2 0 0 0 2.2-2.2v-7.8M16.8 3.2a2.1 2.1 0 0 1 3 3L11 15l-4 1 1-4 8.8-8.8Z"></path>'
    }
  };

  function signalPresentation(value) {
    const key = String(value ?? '')
      .trim()
      .toUpperCase()
      .replace(/[\s-]+/g, '_');
    return SIGNAL_STYLES[key] || SIGNAL_STYLES.FRAGMENT;
  }

  function signalIcon(style) {
    return `<svg class="signal-symbol" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${style.icon}</svg>`;
  }

  function embeddedAuthor(fragment) {
    if (isRecord(fragment.author)) return fragment.author;
    if (isRecord(fragment.user)) return fragment.user;
    if (isRecord(fragment.profile)) return fragment.profile;
    return {};
  }

  function fragmentText(fragment) {
    return firstString(fragment.text, fragment.body, fragment.content, fragment.message);
  }

  function fragmentTimestamp(fragment) {
    return firstString(
      fragment.timestamp,
      fragment.created_at,
      fragment.createdAt,
      fragment.published_at,
      fragment.publishedAt
    );
  }

  function extractItems(payload) {
    if (Array.isArray(payload)) return payload;
    if (!isRecord(payload)) return null;
    if (Array.isArray(payload.items)) return payload.items;
    if (Array.isArray(payload.fragments)) return payload.fragments;
    if (Array.isArray(payload.data)) return payload.data;
    if (isRecord(payload.data) && Array.isArray(payload.data.items)) return payload.data.items;
    return null;
  }

  function saveCache(items) {
    if (!Array.isArray(items) || !items.length) return;
    try {
      window.localStorage.setItem(CACHE_KEY, JSON.stringify({
        version: 2,
        savedAt: Date.now(),
        items
      }));
    } catch (error) {
      console.warn('Could not preserve the founder feed in this browser.', error);
    }
  }

  function loadCache() {
    try {
      const raw = window.localStorage.getItem(CACHE_KEY);
      if (!raw) return null;
      const cached = JSON.parse(raw);
      const fresh = Number(cached.savedAt) > 0 && Date.now() - Number(cached.savedAt) <= CACHE_MAX_AGE_MS;
      if (cached.version !== 2 || !fresh || !Array.isArray(cached.items) || !cached.items.length) {
        window.localStorage.removeItem(CACHE_KEY);
        return null;
      }
      return cached.items;
    } catch (error) {
      try {
        window.localStorage.removeItem(CACHE_KEY);
      } catch (storageError) {
        // Storage can be unavailable in privacy-restricted browsing modes.
      }
      return null;
    }
  }

  async function fetchLiveItems(forceReload = false) {
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    try {
      const response = await fetch(PUBLIC_FEED_URL, {
        cache: forceReload ? 'reload' : 'default',
        credentials: 'omit',
        headers: { Accept: 'application/json' },
        signal: controller.signal
      });
      if (!response.ok) throw new Error(`Live founder feed returned ${response.status}`);
      const items = extractItems(await response.json());
      if (!Array.isArray(items) || !items.length) throw new Error('Live founder feed was empty');
      saveCache(items);
      return items;
    } finally {
      window.clearTimeout(timeoutId);
    }
  }

  function isFounderFragment(fragment) {
    const author = embeddedAuthor(fragment);
    const authorID = firstString(fragment.author_id, fragment.authorId, author.id).toLowerCase();
    const handle = firstString(
      fragment.author_handle,
      fragment.authorHandle,
      author.handle,
      author.username
    ).toLowerCase().replace(/^@+/, '');
    const name = firstString(
      typeof fragment.author === 'string' ? fragment.author : '',
      fragment.author_name,
      fragment.authorName,
      author.name,
      author.display_name,
      author.displayName
    ).toLowerCase();

    if (!authorID && !handle && !name) return true;
    return authorID === 'ryan' ||
      authorID === 'outsidetheworld' ||
      handle === 'outsidetheworld' ||
      name === 'the_ryandavid' ||
      name === 'ryandavid' ||
      name === 'ryan david';
  }

  async function loadLocalItems() {
    const response = await fetch(`fragments_data.js?ts=${Date.now()}`, { cache: 'no-store' });
    if (!response.ok) throw new Error(`Founder archive returned ${response.status}`);
    const scriptText = await response.text();
    const evaluate = new Function(
      'window',
      `${scriptText}; return Array.isArray(window.otw_fragments) ? window.otw_fragments : [];`
    );
    return evaluate({}).filter(isFounderFragment);
  }

  async function loadItems(forceReload = false) {
    if (!FORCE_LOCAL) {
      try {
        return { items: await fetchLiveItems(forceReload), source: 'live' };
      } catch (error) {
        console.warn('Live founder feed unavailable.', error);
      }
    }

    const cached = !forceReload ? loadCache() : null;
    if (cached) return { items: cached, source: 'cache' };
    return { items: await loadLocalItems(), source: 'local' };
  }

  async function loadUserRegistry() {
    const response = await fetch(`fragments_users.json?ts=${Date.now()}`, { cache: 'no-store' });
    if (!response.ok) return [];
    const payload = await response.json();
    return Array.isArray(payload) ? payload : [];
  }

  function renderBody(text) {
    const source = String(text ?? '');
    const urlPattern = /https?:\/\/[^\s<>"']+/gi;
    let cursor = 0;
    let html = '';

    for (const match of source.matchAll(urlPattern)) {
      const raw = match[0];
      const clean = raw.replace(/[),.!?;:]+$/g, '');
      const trailing = raw.slice(clean.length);
      const href = safeWebUrl(clean);
      html += escapeHtml(source.slice(cursor, match.index));
      html += href
        ? `<a href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">${escapeHtml(clean)}</a>${escapeHtml(trailing)}`
        : escapeHtml(raw);
      cursor = match.index + raw.length;
    }

    return html + escapeHtml(source.slice(cursor));
  }

  function normalizeMedia(value) {
    const source = typeof value === 'string' ? { url: value } : value;
    if (!isRecord(source)) return null;
    const type = firstString(
      source.type,
      source.kind,
      source.media_type,
      source.mediaType,
      source.mime_type,
      source.mimeType,
      source.content_type,
      source.contentType
    ).toLowerCase();
    if (type.includes('video') || type.includes('gif')) return null;
    const url = safeWebUrl(firstString(
      source.url,
      source.src,
      source.image,
      source.image_url,
      source.imageUrl,
      source.public_url,
      source.publicUrl,
      source.cdn_url,
      source.cdnUrl
    ));
    if (!url || /\.(?:gif|m4v|mov|mp4|webm)(?:$|\?)/i.test(url)) return null;
    return {
      url,
      alt: firstString(source.alt, source.alt_text, source.altText),
      caption: firstString(source.caption, source.description)
    };
  }

  function fragmentMedia(fragment) {
    const values = [
      fragment.image,
      fragment.image_url,
      fragment.imageUrl,
      fragment.media_url,
      fragment.mediaUrl,
      fragment.media,
      fragment.attachment,
      fragment.attachments,
      fragment.images,
      fragment.media_items,
      fragment.mediaItems
    ];
    const candidates = [];
    values.forEach((value) => {
      if (Array.isArray(value)) candidates.push(...value);
      else if (isRecord(value) && Array.isArray(value.items)) candidates.push(...value.items);
      else if (value) candidates.push(value);
    });
    const seen = new Set();
    return candidates.map(normalizeMedia).filter((asset) => {
      if (!asset || seen.has(asset.url)) return false;
      seen.add(asset.url);
      return true;
    });
  }

  function fragmentLinkPreview(fragment) {
    const candidates = [
      fragment.link_preview,
      fragment.linkPreview,
      fragment.shared_link,
      fragment.sharedLink,
      fragment.url_preview,
      fragment.urlPreview,
      fragment.link
    ];
    const candidate = candidates.find((value) => typeof value === 'string' || isRecord(value));
    const source = typeof candidate === 'string' ? { url: candidate } : (candidate || {});
    const url = safeWebUrl(firstString(
      source.url,
      source.href,
      source.external_url,
      source.externalUrl,
      fragment.link_url,
      fragment.linkUrl
    ));
    if (!url) return null;
    const parsed = new URL(url);
    const host = firstString(source.domain, parsed.hostname.replace(/^www\./, ''));
    return {
      url,
      host,
      title: firstString(source.title, source.headline, source.name, host),
      image: safeWebUrl(firstString(
        source.image_url,
        source.imageUrl,
        source.image,
        source.thumbnail_url,
        source.thumbnailUrl
      ))
    };
  }

  function buildLinkCard(fragment) {
    const preview = fragmentLinkPreview(fragment);
    if (!preview) return '';
    const layoutClass = preview.image ? '' : ' is-text-only';
    const image = preview.image
      ? `<span class="fragment-link-image"><img src="${escapeHtml(preview.image)}" alt="" loading="lazy" decoding="async" /></span>`
      : '';
    return `
      <a class="fragment-link-card${layoutClass}" href="${escapeHtml(preview.url)}" target="_blank" rel="noopener noreferrer">
        ${image}
        <span class="fragment-link-copy">
          <span class="fragment-link-title">${escapeHtml(preview.title)}</span>
          <span class="fragment-link-host">${escapeHtml(preview.host)}</span>
        </span>
      </a>
    `;
  }

  function fragmentID(fragment) {
    const stamp = String(fragmentTimestamp(fragment) || 'undated').replace(/[^0-9]/g, '');
    const bodyStub = slugify(fragmentText(fragment).split(/\s+/).slice(0, 8).join(' ')) || 'fragment';
    return `${stamp}--${bodyStub}`;
  }

  function initials(value) {
    const parts = String(value ?? '').trim().split(/\s+/).filter(Boolean).slice(0, 2);
    return parts.length ? parts.map((part) => part.charAt(0).toUpperCase()).join('') : 'OT';
  }

  function initialsAvatar(name) {
    return `<div class="fragment-avatar initials-avatar" aria-hidden="true">${escapeHtml(initials(name))}</div>`;
  }

  function authorProfile(fragment) {
    const author = embeddedAuthor(fragment);
    const authorID = firstString(fragment.author_id, fragment.authorId, author.id);
    const registryUser = authorID
      ? userRegistry.find((entry) => String(entry.id ?? '').trim() === authorID)
      : null;

    const name = firstString(
      registryUser?.name,
      typeof fragment.author === 'string' ? fragment.author : '',
      fragment.author_name,
      fragment.authorName,
      author.name,
      author.display_name,
      author.displayName,
      'RyanDavid'
    );
    const rawHandle = firstString(
      registryUser?.handle,
      fragment.author_handle,
      fragment.authorHandle,
      author.handle,
      author.username,
      '@outsidetheworld'
    );
    const handle = rawHandle.startsWith('@') ? rawHandle : `@${rawHandle}`;
    const normalizedHandle = handle.toLowerCase().replace(/^@+/, '');
    const normalizedName = name.toLowerCase().replace(/[^a-z0-9]+/g, '');
    const role = firstString(
      registryUser?.role,
      fragment.author_role,
      fragment.authorRole,
      author.role
    ).toLowerCase();
    const isBot = authorID === 'otw_bot' || normalizedHandle === 'otw_bot';
    const hasIdentity = Boolean(authorID || rawHandle || name);
    const isFounder = !isBot && (role === 'founder' ||
      !hasIdentity ||
      authorID === 'ryan' ||
      authorID === 'outsidetheworld' ||
      normalizedHandle === 'outsidetheworld' ||
      normalizedName === 'theryandavid' ||
      normalizedName === 'ryandavid'
    );
    const avatar = firstString(
      registryUser?.avatar,
      fragment.author_avatar,
      fragment.authorAvatar,
      author.avatar,
      author.avatar_url,
      author.avatarUrl,
      isFounder ? 'Images/Profile.jpg' : ''
    );
    const verified = registryUser?.verified === true ||
      fragment.author_verified === true ||
      fragment.authorVerified === true ||
      author.verified === true ||
      author.is_verified === true ||
      isFounder;

    return {
      name,
      handle,
      verified,
      isFounder,
      isBot,
      avatarHtml: avatar
        ? `<img class="fragment-avatar" src="${escapeHtml(avatar)}" alt="${escapeHtml(name)}" />`
        : initialsAvatar(name)
    };
  }

  function formatTimestamp(timestamp) {
    const value = new Date(timestamp);
    if (Number.isNaN(value.getTime())) return escapeHtml(timestamp);
    const options = { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' };
    if (value.getFullYear() !== new Date().getFullYear()) options.year = 'numeric';
    return new Intl.DateTimeFormat('en-US', options).format(value);
  }

  function verifiedBadge(verified, isFounder) {
    if (!verified) return '';
    const color = isFounder ? '#D9C08C' : '#9B59B6';
    const label = isFounder ? 'Founder' : 'Verified';
    return `
      <svg class="verified-badge" viewBox="0 0 24 24" aria-label="${label}">
        <path fill="${color}" d="M12 1.8l2.76 1.58 3.16-.23 1.58 2.76 2.76 1.58-.23 3.16L23 12l-1.97 2.55.23 3.16-2.76 1.58-1.58 2.76-3.16-.23L12 22.2l-2.76-1.58-3.16.23-1.58-2.76-2.76-1.58.23-3.16L1 12l1.97-2.55-.23-3.16 2.76-1.58 1.58-2.76 3.16.23L12 1.8z"></path>
        <path fill="#F5F7FB" d="M10.55 15.62l-2.6-2.6 1.2-1.2 1.4 1.4 4.26-4.26 1.2 1.2z"></path>
      </svg>
    `;
  }

  function buildCard(fragment) {
    const tag = firstString(fragment.tag, fragment.fragment_tag, fragment.category, 'FRAGMENT');
    const signalStyle = signalPresentation(tag);
    const signal = slugify(signalStyle.label) || 'fragment';
    const timestamp = formatTimestamp(fragmentTimestamp(fragment));
    const author = authorProfile(fragment);
    const id = fragmentID(fragment);
    const bodyText = fragmentText(fragment);
    const body = bodyText ? `<p class="fragment-body">${renderBody(bodyText)}</p>` : '';
    const linkCard = buildLinkCard(fragment);
    const media = fragmentMedia(fragment)[0] || null;
    const mediaMarkup = media
      ? `
        <div class="fragment-media">
          <button class="fragment-media-button" type="button" data-media-open="${id}" data-media-caption="${escapeHtml(media.caption)}" aria-label="Open image">
            <img src="${escapeHtml(media.url)}" alt="${escapeHtml(media.alt)}" loading="lazy" decoding="async" />
          </button>
        </div>
      `
      : '';
    const photoOnly = media && !bodyText && !linkCard ? ' is-photo-only' : '';
    const contentClass = media ? ' has-media' : '';

    return `
      <article class="fragment-card${author.isBot ? ' is-bot' : ''}${photoOnly}" id="fragment-${id}" data-fragment-id="${id}" data-signal="${escapeHtml(signal)}">
        <div class="fragment-head">
          <div class="fragment-identity">
            ${author.avatarHtml}
            <div class="fragment-id">
              <div class="fragment-title-top">
                <div class="fragment-name">${escapeHtml(author.name)}</div>
                ${verifiedBadge(author.verified, author.isFounder)}
              </div>
              <div class="fragment-handle">${escapeHtml(author.handle)}</div>
            </div>
          </div>
          <div class="fragment-time">${timestamp}</div>
        </div>
        <div class="fragment-content${contentClass}">
          ${mediaMarkup}
          ${body}
          ${linkCard}
        </div>
        <div class="fragment-foot">
          <div class="fragment-signal">
            <span class="signal-glyph" aria-hidden="true">${signalIcon(signalStyle)}</span>
            <span>${escapeHtml(signalStyle.label)}</span>
          </div>
          <div class="fragment-foot-meta">Public frgmnt</div>
        </div>
      </article>
    `;
  }

  function renderLoading(container) {
    container.innerHTML = `
      <section class="empty-card feed-loading" aria-label="Loading founder frgmnts">
        <span class="feed-loading-signal" aria-hidden="true"></span>
        <span>Tuning the signal</span>
      </section>
    `;
  }

  function renderEmpty(container, error = '') {
    const title = error ? 'Feed temporarily unavailable.' : 'No public frgmnts yet.';
    const copy = error || 'The narrow little ledge is quiet for the moment.';
    container.innerHTML = `
      <section class="empty-card">
        <h2 class="empty-title">${escapeHtml(title)}</h2>
        <p class="empty-copy">${escapeHtml(copy)}</p>
      </section>
    `;
  }

  function feedStatus() {
    if (feedSource === 'cache') {
      return '<p class="feed-status">Live feed is taking a moment. Showing the most recent saved copy.</p>';
    }
    if (feedSource === 'local') {
      return '<p class="feed-status">Live feed is taking a moment. Showing the founder archive.</p>';
    }
    return '';
  }

  function updateLoadMore() {
    const controls = document.getElementById('feedControls');
    const button = document.getElementById('loadMoreBtn');
    const remaining = Math.max(0, allFragments.length - visibleCount);
    controls.hidden = remaining <= 0;
    if (remaining > 0) button.textContent = `Load ${Math.min(PAGE_SIZE, remaining)} More`;
  }

  function openMedia(button) {
    const image = button.querySelector('img');
    const viewer = document.getElementById('mediaViewer');
    const viewerImage = document.getElementById('mediaViewerImage');
    const viewerCaption = document.getElementById('mediaViewerCaption');
    if (!image?.src || !viewer || !viewerImage || !viewerCaption) return;
    viewerImage.src = image.src;
    viewerImage.alt = image.alt;
    viewerCaption.textContent = button.dataset.mediaCaption || '';
    viewerCaption.hidden = !viewerCaption.textContent;
    viewer.showModal();
  }

  function bindMediaButtons() {
    document.querySelectorAll('[data-media-open]').forEach((button) => {
      if (button.dataset.mediaReady === 'true') return;
      button.dataset.mediaReady = 'true';
      button.addEventListener('click', () => openMedia(button));
    });
  }

  function renderVisible(requestedID = null) {
    const container = document.getElementById('fragmentsFeed');
    const items = allFragments.slice(0, visibleCount);
    container.innerHTML = items.map(buildCard).join('') + feedStatus();
    bindMediaButtons();
    updateLoadMore();

    if (requestedID && typeof CSS !== 'undefined' && CSS.escape) {
      const requested = document.querySelector(`[data-fragment-id="${CSS.escape(requestedID)}"]`);
      requested?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  async function renderFragments({ forceReload = false } = {}) {
    if (loadActive) return;
    const container = document.getElementById('fragmentsFeed');
    const refreshButton = document.getElementById('refreshFeedBtn');
    loadActive = true;
    container.setAttribute('aria-busy', 'true');
    refreshButton.disabled = true;
    if (!allFragments.length) renderLoading(container);

    try {
      const [loaded, users] = await Promise.all([
        loadItems(forceReload),
        loadUserRegistry().catch(() => [])
      ]);
      feedSource = loaded.source;
      userRegistry = users;
      allFragments = loaded.items.filter((fragment) => {
        return fragment && (fragmentText(fragment) || fragmentMedia(fragment).length || fragmentLinkPreview(fragment));
      });
    } catch (error) {
      renderEmpty(container, error.message || 'Could not load frgmnts right now.');
      return;
    } finally {
      loadActive = false;
      container.setAttribute('aria-busy', 'false');
      refreshButton.disabled = false;
    }

    if (!allFragments.length) {
      renderEmpty(container);
      updateLoadMore();
      return;
    }

    const requestedID = new URLSearchParams(window.location.search).get('entry');
    visibleCount = PAGE_SIZE;
    if (requestedID) {
      const requestedIndex = allFragments.findIndex((fragment) => fragmentID(fragment) === requestedID);
      if (requestedIndex >= 0) visibleCount = Math.max(PAGE_SIZE, requestedIndex + 1);
    }
    renderVisible(requestedID);
  }

  document.getElementById('refreshFeedBtn').addEventListener('click', () => {
    void renderFragments({ forceReload: true });
  });
  document.getElementById('loadMoreBtn').addEventListener('click', () => {
    visibleCount += PAGE_SIZE;
    renderVisible();
  });
  document.getElementById('mediaViewerClose').addEventListener('click', () => {
    document.getElementById('mediaViewer').close();
  });
  document.getElementById('mediaViewer').addEventListener('click', (event) => {
    if (event.target === event.currentTarget) event.currentTarget.close();
  });
  document.getElementById('mediaViewer').addEventListener('close', () => {
    document.getElementById('mediaViewerImage').removeAttribute('src');
  });

  void renderFragments();
})();
