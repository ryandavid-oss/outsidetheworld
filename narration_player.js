(function () {
    const STORAGE_PREFIX = 'otw_narration_position:';
    const PLAYBACK_SPEEDS = [1, 1.25, 1.5, 0.75];

    const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

    const formatTime = (value) => {
        const seconds = Math.max(0, Math.floor(Number(value) || 0));
        return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
    };

    const readPosition = (key) => {
        try {
            const stored = window.localStorage && window.localStorage.getItem(key);
            const value = stored ? JSON.parse(stored) : null;
            return value && typeof value === 'object' ? value : null;
        } catch {
            return null;
        }
    };

    const writePosition = (key, value) => {
        try {
            if (window.localStorage) {
                window.localStorage.setItem(key, JSON.stringify(value));
            }
        } catch {
            // Listening still works when storage is unavailable.
        }
    };

    const clearPosition = (key) => {
        try {
            if (window.localStorage) {
                window.localStorage.removeItem(key);
            }
        } catch {
            // Nothing else is required when storage is unavailable.
        }
    };

    const initNarrationPlayer = (player) => {
        const audio = player.querySelector('[data-narration-audio]');
        const surface = player.querySelector('.narration-player__surface');
        const playButton = player.querySelector('[data-narration-play]');
        const scrubber = player.querySelector('[data-narration-scrubber]');
        const currentLabel = player.querySelector('[data-narration-current]');
        const totalLabel = player.querySelector('[data-narration-total]');
        const durationLabel = player.querySelector('[data-narration-duration-label]');
        const statusLabel = player.querySelector('[data-narration-status]');
        const promptLabel = player.querySelector('[data-narration-prompt]');
        const waveformClip = player.querySelector('[data-narration-waveform-clip]');
        const speedButton = player.querySelector('[data-narration-speed]');
        const followButton = player.querySelector('[data-narration-follow]');
        const dismissButton = player.querySelector('[data-narration-dock-dismiss]');
        const chapterButtons = Array.from(player.querySelectorAll('[data-narration-chapter]'));
        const entryBody = document.getElementById('entry-body');

        if (!audio || !surface || !playButton || !scrubber) {
            return;
        }

        const initialStatus = statusLabel ? statusLabel.textContent : 'Audio narration';
        const initialPrompt = promptLabel ? promptLabel.textContent : 'Press play and stay awhile.';
        const durationFallback = Math.max(0, Number(player.getAttribute('data-narration-duration')) || 0);
        const narrationId = player.getAttribute('data-narration-id') || window.location.pathname;
        const storageKey = `${STORAGE_PREFIX}${narrationId}`;
        const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        let hasStarted = false;
        let followAlong = false;
        let dockSuppressed = false;
        let activeChapterIndex = -1;
        let lastStoredSecond = -1;
        let dockFrame = 0;
        let savedPositionApplied = false;

        const chapters = chapterButtons.map((button) => ({
            button,
            startSeconds: Math.max(0, Number(button.getAttribute('data-narration-chapter')) || 0),
            target: button.getAttribute('data-narration-target') || '',
            elements: [],
        }));

        if (entryBody && chapters.some((chapter) => chapter.target)) {
            const bodyChildren = Array.from(entryBody.children);
            chapters.forEach((chapter, index) => {
                if (!chapter.target) {
                    return;
                }
                const target = document.getElementById(chapter.target);
                const startIndex = bodyChildren.indexOf(target);
                if (startIndex < 0) {
                    return;
                }
                const nextTarget = chapters.slice(index + 1).find((item) => item.target);
                const nextElement = nextTarget ? document.getElementById(nextTarget.target) : null;
                const endIndex = nextElement ? bodyChildren.indexOf(nextElement) : bodyChildren.length;
                chapter.elements = bodyChildren.slice(startIndex, endIndex > startIndex ? endIndex : bodyChildren.length);
                target.setAttribute('data-narration-section-start', '');
            });
        }

        const effectiveDuration = () => (
            Number.isFinite(audio.duration) && audio.duration > 0 ? audio.duration : durationFallback
        );

        const setStatus = (value) => {
            if (statusLabel) {
                statusLabel.textContent = value;
            }
        };

        const setPrompt = (value) => {
            if (promptLabel) {
                promptLabel.textContent = value;
            }
        };

        const updatePlayerHeight = () => {
            if (!player.classList.contains('is-docked')) {
                player.style.minHeight = `${Math.ceil(surface.offsetHeight)}px`;
            }
        };

        const expandPlayer = () => {
            if (!player.classList.contains('is-expanded')) {
                player.classList.add('is-expanded');
                window.requestAnimationFrame(updatePlayerHeight);
            }
        };

        const scrollToChapter = (chapter) => {
            if (!followAlong || !chapter || !chapter.target) {
                return;
            }
            const target = document.getElementById(chapter.target);
            if (!target) {
                return;
            }
            const bounds = target.getBoundingClientRect();
            if (bounds.top >= 88 && bounds.top <= window.innerHeight * 0.72) {
                return;
            }
            target.scrollIntoView({
                behavior: reducedMotion.matches ? 'auto' : 'smooth',
                block: 'center',
            });
        };

        const applyFollowAlong = () => {
            if (!entryBody) {
                return;
            }
            entryBody.classList.toggle('is-narration-following', followAlong);
            chapters.forEach((chapter, index) => {
                chapter.elements.forEach((element) => {
                    element.classList.toggle('is-narration-current', followAlong && index === activeChapterIndex);
                });
            });
        };

        const syncChapter = (shouldScroll = false) => {
            if (!chapters.length) {
                return;
            }
            const currentTime = Number(audio.currentTime) || 0;
            let nextIndex = 0;
            chapters.forEach((chapter, index) => {
                if (currentTime >= chapter.startSeconds) {
                    nextIndex = index;
                }
            });
            const didChange = nextIndex !== activeChapterIndex;
            activeChapterIndex = nextIndex;
            chapters.forEach((chapter, index) => {
                chapter.button.setAttribute('aria-current', index === activeChapterIndex ? 'true' : 'false');
            });
            applyFollowAlong();
            if (shouldScroll && didChange) {
                scrollToChapter(chapters[activeChapterIndex]);
            }
        };

        const updateProgress = (shouldScroll = false) => {
            const duration = effectiveDuration();
            const current = clamp(Number(audio.currentTime) || 0, 0, duration || Number.MAX_SAFE_INTEGER);
            const ratio = duration > 0 ? clamp(current / duration, 0, 1) : 0;
            scrubber.max = String(duration || 1);
            scrubber.value = String(current);
            if (currentLabel) {
                currentLabel.textContent = formatTime(current);
            }
            if (totalLabel) {
                totalLabel.textContent = formatTime(duration);
            }
            if (durationLabel) {
                durationLabel.textContent = formatTime(duration);
            }
            if (waveformClip) {
                waveformClip.setAttribute('width', String(640 * ratio));
            }
            syncChapter(shouldScroll);
        };

        const saveCurrentPosition = (force = false) => {
            const current = Number(audio.currentTime) || 0;
            const duration = effectiveDuration();
            const wholeSecond = Math.floor(current);
            if (!force && Math.abs(wholeSecond - lastStoredSecond) < 5) {
                return;
            }
            lastStoredSecond = wholeSecond;
            if (current < 2 || (duration && current >= duration - 4)) {
                clearPosition(storageKey);
                return;
            }
            writePosition(storageKey, {
                time: current,
                rate: audio.playbackRate,
                updatedAt: Date.now(),
            });
        };

        const setDocked = (isDocked) => {
            player.classList.toggle('is-docked', isDocked);
            document.body.classList.toggle('has-narration-dock', isDocked);
        };

        const updateDock = () => {
            dockFrame = 0;
            if (!hasStarted) {
                setDocked(false);
                return;
            }
            const bounds = player.getBoundingClientRect();
            if (bounds.bottom > 20) {
                dockSuppressed = false;
            }
            setDocked(bounds.bottom < 0 && !dockSuppressed);
        };

        const scheduleDockUpdate = () => {
            if (!dockFrame) {
                dockFrame = window.requestAnimationFrame(updateDock);
            }
        };

        const setPlayingState = (isPlaying) => {
            player.classList.toggle('is-playing', isPlaying);
            playButton.setAttribute('aria-label', `${isPlaying ? 'Pause' : hasStarted ? 'Resume' : 'Play'} ${document.getElementById(player.getAttribute('aria-labelledby'))?.textContent || 'audio narration'}`);
            if (isPlaying) {
                setStatus('Still out there with you');
                setPrompt(followAlong ? 'The essay will move with the narration.' : 'Follow the words, or simply listen.');
            } else if (audio.ended) {
                setStatus('Finished');
                setPrompt('Still out there with you.');
            } else if (hasStarted) {
                setStatus('Paused');
                setPrompt('Your place is saved on this device.');
            } else {
                setStatus(initialStatus);
                setPrompt(initialPrompt);
            }
        };

        const startPlayback = async () => {
            hasStarted = true;
            dockSuppressed = false;
            expandPlayer();
            player.classList.remove('has-audio-error');
            try {
                await audio.play();
            } catch {
                setPlayingState(false);
                setStatus('Audio unavailable');
                setPrompt('The recording could not begin. You can keep reading here.');
            }
            scheduleDockUpdate();
        };

        const restoreSavedPosition = () => {
            if (savedPositionApplied) {
                updateProgress();
                return;
            }
            const saved = readPosition(storageKey);
            const duration = effectiveDuration();
            if (!saved) {
                savedPositionApplied = true;
                updateProgress();
                return;
            }
            const time = Number(saved.time) || 0;
            const rate = Number(saved.rate) || 1;
            if (time >= 2 && (!duration || time < duration - 4)) {
                try {
                    audio.currentTime = time;
                    audio.playbackRate = PLAYBACK_SPEEDS.includes(rate) ? rate : 1;
                    setStatus(`Resume at ${formatTime(time)}`);
                    setPrompt('Your place from last time is ready.');
                    savedPositionApplied = true;
                } catch {
                    updateProgress();
                    return;
                }
            } else {
                savedPositionApplied = true;
            }
            updateProgress();
        };

        player.classList.add('is-enhanced');
        audio.controls = false;
        updatePlayerHeight();
        restoreSavedPosition();

        playButton.addEventListener('click', () => {
            if (audio.paused || audio.ended) {
                if (audio.ended) {
                    audio.currentTime = 0;
                }
                startPlayback();
            } else {
                audio.pause();
            }
        });

        player.querySelectorAll('[data-narration-skip]').forEach((button) => {
            button.addEventListener('click', () => {
                const duration = effectiveDuration();
                const delta = Number(button.getAttribute('data-narration-skip')) || 0;
                audio.currentTime = clamp((Number(audio.currentTime) || 0) + delta, 0, duration || Number.MAX_SAFE_INTEGER);
                updateProgress();
            });
        });

        scrubber.addEventListener('input', () => {
            const duration = effectiveDuration();
            audio.currentTime = clamp(Number(scrubber.value) || 0, 0, duration || Number.MAX_SAFE_INTEGER);
            hasStarted = true;
            expandPlayer();
            updateProgress();
        });

        chapterButtons.forEach((button, index) => {
            button.addEventListener('click', () => {
                const chapter = chapters[index];
                audio.currentTime = chapter.startSeconds;
                hasStarted = true;
                expandPlayer();
                syncChapter(false);
                scrollToChapter(chapter);
                startPlayback();
            });
        });

        if (followButton) {
            followButton.addEventListener('click', () => {
                followAlong = !followAlong;
                followButton.setAttribute('aria-pressed', followAlong ? 'true' : 'false');
                followButton.textContent = followAlong ? 'Following' : 'Follow along';
                applyFollowAlong();
                if (followAlong && activeChapterIndex >= 0) {
                    scrollToChapter(chapters[activeChapterIndex]);
                    if (!audio.paused) {
                        setPrompt('The essay will move with the narration.');
                    }
                } else if (!audio.paused) {
                    setPrompt('Follow the words, or simply listen.');
                }
            });
        }

        if (speedButton) {
            speedButton.addEventListener('click', () => {
                const currentIndex = PLAYBACK_SPEEDS.indexOf(audio.playbackRate);
                audio.playbackRate = PLAYBACK_SPEEDS[(currentIndex + 1 + PLAYBACK_SPEEDS.length) % PLAYBACK_SPEEDS.length];
            });
        }

        if (dismissButton) {
            dismissButton.addEventListener('click', () => {
                audio.pause();
                dockSuppressed = true;
                setDocked(false);
            });
        }

        audio.addEventListener('play', () => setPlayingState(true));
        audio.addEventListener('pause', () => {
            saveCurrentPosition(true);
            setPlayingState(false);
        });
        audio.addEventListener('timeupdate', () => {
            updateProgress(true);
            saveCurrentPosition();
        });
        audio.addEventListener('loadedmetadata', restoreSavedPosition);
        audio.addEventListener('durationchange', updateProgress);
        audio.addEventListener('ratechange', () => {
            if (speedButton) {
                const value = Number(audio.playbackRate).toFixed(2).replace(/\.00$/, '').replace(/0$/, '');
                speedButton.textContent = `${value}×`;
            }
        });
        audio.addEventListener('ended', () => {
            clearPosition(storageKey);
            setPlayingState(false);
            updateProgress();
        });
        audio.addEventListener('error', () => {
            player.classList.add('has-audio-error');
            setPlayingState(false);
            setStatus('Audio unavailable');
            setPrompt('The recording could not be loaded. You can keep reading here.');
        });

        window.addEventListener('scroll', scheduleDockUpdate, { passive: true });
        window.addEventListener('resize', () => {
            updatePlayerHeight();
            scheduleDockUpdate();
        });
        window.addEventListener('pagehide', () => saveCurrentPosition(true));

        if ('mediaSession' in navigator) {
            const title = document.getElementById(player.getAttribute('aria-labelledby'))?.textContent || document.title;
            try {
                navigator.mediaSession.metadata = new MediaMetadata({
                    title,
                    artist: 'Outside The World',
                    album: 'Outside The World essay narration',
                });
                navigator.mediaSession.setActionHandler('play', startPlayback);
                navigator.mediaSession.setActionHandler('pause', () => audio.pause());
                navigator.mediaSession.setActionHandler('seekbackward', (details) => {
                    audio.currentTime = Math.max(0, audio.currentTime - (details.seekOffset || 15));
                });
                navigator.mediaSession.setActionHandler('seekforward', (details) => {
                    audio.currentTime = Math.min(effectiveDuration() || Number.MAX_SAFE_INTEGER, audio.currentTime + (details.seekOffset || 15));
                });
                navigator.mediaSession.setActionHandler('seekto', (details) => {
                    if (Number.isFinite(details.seekTime)) {
                        audio.currentTime = clamp(details.seekTime, 0, effectiveDuration() || Number.MAX_SAFE_INTEGER);
                    }
                });
            } catch {
                // The custom player remains fully usable when Media Session is partial.
            }
        }
    };

    const init = () => {
        document.querySelectorAll('[data-narration-player]').forEach(initNarrationPlayer);
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
}());
