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

    window.copyShareLink = async function copyShareLink() {
        const url = window.location.href.split('#')[0];
        try {
            if (navigator.share) {
                await navigator.share({ title: document.title, text: 'Outside The World archive signal', url });
                setShareStatus('LINK_SHARED');
                return;
            }

            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(url);
                setShareStatus('LINK_COPIED');
                return;
            }

            setShareStatus('COPY_UNAVAILABLE');
        } catch {
            setShareStatus('COPY_FAILED');
        }
    };

    const initShare = () => {
        const shareButton = document.querySelector('[data-share-button]');
        if (shareButton) {
            shareButton.addEventListener('click', window.copyShareLink);
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initReaderMode();
            initShare();
        });
    } else {
        initReaderMode();
        initShare();
    }
}());
