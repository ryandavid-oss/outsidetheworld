(function () {
    const STORAGE_KEY = 'otw_archive_reader_mode';
    const VALID_MODES = new Set(['dark', 'light']);

    const readStoredMode = () => {
        try {
            const storedMode = window.localStorage && window.localStorage.getItem(STORAGE_KEY);
            return VALID_MODES.has(storedMode) ? storedMode : null;
        } catch {
            return null;
        }
    };

    const writeStoredMode = (mode) => {
        try {
            if (window.localStorage) {
                window.localStorage.setItem(STORAGE_KEY, mode);
            }
        } catch {
            // Reader mode still works for the current page if storage is unavailable.
        }
    };

    const updateThemeColor = (mode) => {
        const themeMeta = document.querySelector('meta[name="theme-color"]');
        if (themeMeta) {
            themeMeta.setAttribute('content', mode === 'light' ? '#f4f1ea' : '#060809');
        }
    };

    const applyMode = (mode, shouldPersist) => {
        const safeMode = VALID_MODES.has(mode) ? mode : 'dark';
        document.documentElement.setAttribute('data-reader-mode', safeMode);
        updateThemeColor(safeMode);

        document.querySelectorAll('[data-reader-mode-option]').forEach((button) => {
            const isActive = button.getAttribute('data-reader-mode-option') === safeMode;
            button.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });

        if (shouldPersist) {
            writeStoredMode(safeMode);
        }
    };

    const initReaderMode = () => {
        applyMode(readStoredMode() || document.documentElement.getAttribute('data-reader-mode') || 'dark', false);

        document.querySelectorAll('[data-reader-mode-option]').forEach((button) => {
            button.addEventListener('click', () => {
                applyMode(button.getAttribute('data-reader-mode-option'), true);
            });
        });
    };

    const setShareStatus = (message) => {
        const statusEl = document.getElementById('share-status');
        if (statusEl) {
            statusEl.textContent = message;
        }
    };

    const legacyCopyText = (text) => {
        const input = document.createElement('textarea');
        input.value = text;
        input.setAttribute('readonly', '');
        input.style.position = 'fixed';
        input.style.left = '-9999px';
        input.style.top = '0';
        document.body.appendChild(input);
        input.focus({ preventScroll: true });
        input.select();
        input.setSelectionRange(0, input.value.length);
        try {
            return document.execCommand('copy');
        } catch {
            return false;
        } finally {
            input.remove();
        }
    };

    const copyText = async (text) => {
        try {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(text);
                return true;
            }
        } catch {
            // Fall through to the legacy copy path.
        }
        return legacyCopyText(text);
    };

    window.copyShareLink = async function copyShareLink() {
        const url = window.location.href.split('#')[0];
        if (await copyText(url)) {
            setShareStatus('LINK_COPIED');
            return;
        }

        try {
            if (navigator.share) {
                await navigator.share({ title: document.title, text: 'Outside The World archive signal', url });
                setShareStatus('LINK_SHARED');
                return;
            }
        } catch {
            // Fall through to a single failure state.
        }

        setShareStatus('COPY_UNAVAILABLE');
    };

    const initShare = () => {
        const shareButton = document.querySelector('[data-share-button]');
        if (shareButton) {
            shareButton.addEventListener('click', window.copyShareLink);
        }
    };

    const clarifyMedia = window.matchMedia('(min-width: 1180px)');

    const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

    const restoreFloatingPanel = (panel) => {
        if (!panel || !panel.classList.contains('clarify-note__panel--floating')) {
            return;
        }
        const homeId = panel.getAttribute('data-clarify-home');
        const home = homeId ? document.getElementById(homeId) : null;
        panel.classList.remove('clarify-note__panel--floating');
        panel.style.left = '';
        panel.style.top = '';
        if (home && !home.contains(panel)) {
            home.appendChild(panel);
        }
    };

    const setDisclosureState = (button, panel, isExpanded) => {
        button.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
        if (!isExpanded) {
            panel.hidden = true;
            restoreFloatingPanel(panel);
            return;
        }
        panel.hidden = !isExpanded;
    };

    const closeDisclosureGroup = (selector, exceptButton) => {
        document.querySelectorAll(selector).forEach((button) => {
            const panelId = button.getAttribute('aria-controls');
            const panel = panelId ? document.getElementById(panelId) : null;
            if (!panel || button === exceptButton) {
                return;
            }
            setDisclosureState(button, panel, false);
        });
    };

    const initReaderAidTools = () => {
        document.querySelectorAll('[data-reader-aid-toggle]').forEach((button) => {
            const panelId = button.getAttribute('aria-controls');
            const panel = panelId ? document.getElementById(panelId) : null;
            if (!panel) {
                return;
            }

            button.addEventListener('click', () => {
                const isExpanded = button.getAttribute('aria-expanded') === 'true';
                closeDisclosureGroup('[data-reader-aid-toggle]', button);
                setDisclosureState(button, panel, !isExpanded);
            });
        });
    };

    const prepareClarifyHome = (button, panel) => {
        const note = button.closest('[data-clarify-note]');
        if (!note) {
            return;
        }
        if (!note.id) {
            note.id = `${panel.id}-home`;
        }
        panel.setAttribute('data-clarify-home', note.id);
    };

    const positionClarifyPanel = (button, panel) => {
        panel.style.left = '-9999px';
        panel.style.top = '-9999px';
        panel.hidden = false;
        const buttonRect = button.getBoundingClientRect();
        const panelWidth = panel.offsetWidth;
        const panelHeight = panel.offsetHeight;
        const margin = 16;
        let left = buttonRect.right + 10;
        if (left + panelWidth > window.innerWidth - margin) {
            left = buttonRect.left - panelWidth - 10;
        }
        left = clamp(left, margin, Math.max(margin, window.innerWidth - panelWidth - margin));
        const top = clamp(buttonRect.top - 4, margin, Math.max(margin, window.innerHeight - panelHeight - margin));
        panel.style.left = `${left}px`;
        panel.style.top = `${top}px`;
    };

    const openClarifyPanel = (button, panel) => {
        closeDisclosureGroup('[data-clarify-toggle]', button);
        button.setAttribute('aria-expanded', 'true');
        if (clarifyMedia.matches) {
            prepareClarifyHome(button, panel);
            panel.classList.add('clarify-note__panel--floating');
            document.body.appendChild(panel);
            positionClarifyPanel(button, panel);
            return;
        }
        restoreFloatingPanel(panel);
        panel.hidden = false;
    };

    const repositionOpenClarifyPanel = () => {
        const button = document.querySelector('[data-clarify-toggle][aria-expanded="true"]');
        if (!button || !clarifyMedia.matches) {
            return;
        }
        const panelId = button.getAttribute('aria-controls');
        const panel = panelId ? document.getElementById(panelId) : null;
        if (panel && panel.classList.contains('clarify-note__panel--floating')) {
            positionClarifyPanel(button, panel);
        }
    };

    const closeOpenClarifyOnScroll = () => {
        if (!document.querySelector('[data-clarify-toggle][aria-expanded="true"]')) {
            return;
        }
        closeDisclosureGroup('[data-clarify-toggle]');
    };

    const initClarifyNotes = () => {
        document.querySelectorAll('[data-clarify-toggle]').forEach((button) => {
            const panelId = button.getAttribute('aria-controls');
            const panel = panelId ? document.getElementById(panelId) : null;
            if (!panel) {
                return;
            }

            button.addEventListener('click', () => {
                const isExpanded = button.getAttribute('aria-expanded') === 'true';
                if (isExpanded) {
                    setDisclosureState(button, panel, false);
                    return;
                }
                openClarifyPanel(button, panel);
            });
        });

        document.addEventListener('click', (event) => {
            if (
                event.target.closest('[data-clarify-note]') ||
                event.target.closest('.clarify-note__panel--floating')
            ) {
                return;
            }
            closeDisclosureGroup('[data-clarify-toggle]');
        });

        window.addEventListener('resize', repositionOpenClarifyPanel);
        window.addEventListener('scroll', closeOpenClarifyOnScroll, { passive: true });
        if (clarifyMedia.addEventListener) {
            clarifyMedia.addEventListener('change', () => closeDisclosureGroup('[data-clarify-toggle]'));
        }
    };

    const closeCheckpoints = () => {
        document.querySelectorAll('.reading-checkpoint[open]').forEach((checkpoint) => {
            checkpoint.open = false;
        });
    };

    const setReadingToolsState = (button, enabled) => {
        document.body.setAttribute('data-reading-tools', enabled ? 'on' : 'off');
        button.setAttribute('aria-pressed', enabled ? 'true' : 'false');
        button.textContent = enabled ? 'Hide Reading Tools' : 'Show Reading Tools';
        if (!enabled) {
            closeDisclosureGroup('[data-reader-aid-toggle]');
            closeDisclosureGroup('[data-clarify-toggle]');
            closeCheckpoints();
        }
    };

    const initReadingToolsMaster = () => {
        const button = document.querySelector('[data-reading-tools-toggle]');
        if (!button) {
            return;
        }
        setReadingToolsState(button, document.body.getAttribute('data-reading-tools') === 'on');
        button.addEventListener('click', () => {
            const isEnabled = document.body.getAttribute('data-reading-tools') === 'on';
            setReadingToolsState(button, !isEnabled);
        });
    };

    const initReadingAids = () => {
        initReadingToolsMaster();
        initReaderAidTools();
        initClarifyNotes();

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                closeDisclosureGroup('[data-reader-aid-toggle]');
                closeDisclosureGroup('[data-clarify-toggle]');
            }
        });
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initReaderMode();
            initShare();
            initReadingAids();
        });
    } else {
        initReaderMode();
        initShare();
        initReadingAids();
    }
}());
