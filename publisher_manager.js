(() => {
  const managerBtn = document.getElementById('publishedEssaysBtn');
  const manager = document.getElementById('publishedManager');
  const status = document.getElementById('pmStatus');
  const list = document.getElementById('pmEssayList');
  const workspace = document.getElementById('pmWorkspace');
  const search = document.getElementById('pmSearch');
  const filter = document.getElementById('pmFilter');
  const refreshBtn = document.getElementById('pmRefreshBtn');
  const composeBtn = document.getElementById('pmComposeBtn');
  const tokenMeta = document.querySelector('meta[name="otw-publisher-token"]');
  const token = tokenMeta ? tokenMeta.content : '';

  if (!managerBtn || !manager) return;

  const state = {
    essays: [],
    detail: null,
    selectedSlug: ''
  };

  function setStatus(message) {
    if (status) {
      status.textContent = message || 'Published essay launcher';
    }
  }

  function escapeHtml(value) {
    return String(value || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  async function api(path, options = {}) {
    if (!token) {
      throw new Error('Start tools/publisher_server.py to manage published essays.');
    }
    const response = await fetch(path, {
      ...options,
      headers: {
        'content-type': 'application/json; charset=utf-8',
        'x-publisher-token': token,
        ...(options.headers || {})
      }
    });
    const payload = await response.json().catch(() => null);
    if (!response.ok || !payload || payload.ok === false) {
      throw new Error(payload?.error || `Request failed (${response.status})`);
    }
    return payload;
  }

  function readingStatus(essay) {
    return essay.readingAidStatus?.status || 'none';
  }

  function chip(value, level = '') {
    const cls = level ? `pm-chip ${level}` : 'pm-chip';
    return `<span class="${cls}">${escapeHtml(value)}</span>`;
  }

  function filteredEssays() {
    const query = search.value.trim().toLowerCase();
    const mode = filter.value;
    return state.essays.filter((essay, index) => {
      const haystack = `${essay.title} ${essay.slug} ${essay.date} ${essay.archivePath}`.toLowerCase();
      if (query && !haystack.includes(query)) return false;
      if (mode === 'latest' && !query) return index < 8;
      if (mode === 'unpublished-revision') return essay.revisionStatus?.status === 'draft revision';
      if (mode === 'stale-aids') return readingStatus(essay) === 'stale' || readingStatus(essay) === 'validation error';
      if (mode === 'long') return Number(essay.wordCount || 0) >= 1800;
      return true;
    });
  }

  function renderEssayList() {
    const essays = filteredEssays();
    list.innerHTML = essays.map((essay) => {
      const aidStatus = readingStatus(essay);
      const aidLevel = aidStatus === 'validation error' ? 'is-danger' : (aidStatus === 'stale' ? 'is-warning' : '');
      const revision = essay.revisionStatus?.status || 'clean';
      return `
        <button class="pm-essay ${essay.slug === state.selectedSlug ? 'is-selected' : ''}" type="button" data-slug="${escapeHtml(essay.slug)}">
          <span class="pm-essay-title">${escapeHtml(essay.title)}</span>
          <span class="pm-essay-meta">${escapeHtml(essay.date)} - ${escapeHtml(essay.slug)}</span>
          <span class="pm-chip-row">
            ${chip(revision, revision === 'draft revision' ? 'is-warning' : '')}
            ${chip(`aids: ${aidStatus}`, aidLevel)}
            ${chip(`${essay.wordCount || 0} words`)}
          </span>
        </button>
      `;
    }).join('') || '<div class="pm-empty">No essays match</div>';
  }

  function renderWorkspace() {
    const detail = state.detail;
    if (!detail) {
      workspace.innerHTML = `
        <div class="pm-empty">
          Select an essay to reopen it in the composer.
        </div>
      `;
      return;
    }

    const essay = detail.essay;
    const revision = essay.revisionStatus?.status || 'clean';
    const aidStatus = detail.sidecarStatus?.status || readingStatus(essay);
    const aidWarning = aidStatus === 'approved'
      ? 'Approved reading aids are present. Local republish will verify anchors before writing production output.'
      : aidStatus === 'stale' || aidStatus === 'validation error'
        ? 'Reading aids need attention. V1 does not edit older essay aids; local republish will not silently approve broken anchors.'
        : 'No old-essay reading-aid workflow is required for revision mode.';

    workspace.innerHTML = `
      <div class="pm-workspace-head">
        <div class="pm-row">
          <h2 class="pm-workspace-title">${escapeHtml(essay.title)}</h2>
          ${chip(`date: ${essay.date}`)}
          ${chip(`slug: ${essay.slug}`)}
          ${chip(revision, revision === 'draft revision' ? 'is-warning' : '')}
        </div>
        <div class="pm-chip-row">
          ${chip(essay.archivePath)}
          ${chip(essay.ogPath)}
          ${chip(`reading aids: ${aidStatus}`, aidStatus === 'stale' || aidStatus === 'validation error' ? 'is-warning' : '')}
        </div>
      </div>
      <div class="pm-form">
        <p class="pm-copy">
          Open this essay in the normal composer, make revisions there, then use the revision bar above the editor to save a draft, preview, republish locally, or restore a backup.
        </p>
        <p class="pm-copy">${escapeHtml(aidWarning)}</p>
        <div class="pm-actions">
          <button class="pm-action is-primary" type="button" data-pm-action="open-composer">Open in Composer</button>
          <button class="pm-action" type="button" data-pm-action="view-archive">Open Current Archive</button>
        </div>
      </div>
    `;
  }

  async function loadEssays() {
    setStatus('Loading library');
    const payload = await api('/api/published-essays');
    state.essays = payload.essays || [];
    renderEssayList();
    setStatus(`${state.essays.length} published essays`);
    if (!state.detail && state.essays.length) {
      await loadEssay(state.essays[0].slug);
    }
  }

  async function loadEssay(slug) {
    state.selectedSlug = slug;
    setStatus('Loading essay');
    const payload = await api(`/api/published-essays/${encodeURIComponent(slug)}`);
    state.detail = payload;
    renderEssayList();
    renderWorkspace();
    setStatus('Essay selected');
  }

  function openSelectedInComposer() {
    if (!state.detail) return;
    const opener = window.otwPublisher?.openPublishedRevisionInComposer;
    if (!opener) {
      setStatus('Composer bridge unavailable');
      return;
    }
    const opened = opener(state.detail);
    if (opened) {
      manager.hidden = true;
      setStatus('Opened in composer');
    }
  }

  managerBtn.addEventListener('click', async () => {
    manager.hidden = !manager.hidden;
    if (manager.hidden) return;
    try {
      await loadEssays();
    } catch (error) {
      setStatus(error.message);
    }
  });

  composeBtn.addEventListener('click', () => {
    manager.hidden = true;
    window.otwPublisher?.exitPublishedRevisionMode?.();
    window.otwPublisher?.clearLocalDraft?.();
  });

  refreshBtn.addEventListener('click', () => {
    loadEssays().catch((error) => setStatus(error.message));
  });

  search.addEventListener('input', renderEssayList);
  filter.addEventListener('change', renderEssayList);

  list.addEventListener('click', (event) => {
    const button = event.target.closest('[data-slug]');
    if (!button) return;
    loadEssay(button.dataset.slug).catch((error) => setStatus(error.message));
  });

  workspace.addEventListener('click', (event) => {
    const action = event.target.closest('[data-pm-action]')?.dataset.pmAction;
    if (!action) return;
    if (action === 'open-composer') {
      openSelectedInComposer();
    } else if (action === 'view-archive' && state.detail?.essay?.archivePath) {
      window.open(state.detail.essay.archivePath, '_blank', 'noopener');
    }
  });

  window.addEventListener('otw-published-revision-updated', (event) => {
    if (event.detail?.essay?.slug === state.selectedSlug) {
      state.detail = event.detail;
      renderWorkspace();
    }
    loadEssays().catch(() => {});
  });

  setStatus('Published essay launcher');
})();
