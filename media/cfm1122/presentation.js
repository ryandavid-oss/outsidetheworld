(() => {
  'use strict';

  const get = (id) => document.getElementById(id);
  const stage = get('stage');
  const slides = [...stage.querySelectorAll('.slide')];
  const previous = get('previous');
  const next = get('next');
  const screens = get('screens');
  const screensButton = get('screens-button');
  const controls = get('controls');
  const fullscreen = get('fullscreen');
  const showControls = get('show-controls');
  const hideControls = get('hide-controls');
  const clip = get('clip');
  const playClip = get('play-clip');
  const clipTemplate = get('clip-template');
  const currentFromHash = () => Math.max(0, slides.findIndex((slide) => '#' + slide.id === location.hash));
  let current = -1;

  const screenButtons = slides.map((slide, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = slide.dataset.label;
    button.addEventListener('click', () => {
      screens.close();
      goTo(index);
      slide.querySelector('h1, h2').focus({ preventScroll: true });
    });
    return button;
  });
  get('screen-list').append(...screenButtons);

  function goTo(index, updateHash = true) {
    const target = Math.max(0, Math.min(slides.length - 1, index));
    if (target === current) return;

    if (slides[current]?.id === 'podcast') {
      clip.querySelector('iframe')?.remove();
      playClip.hidden = false;
    }
    current = target;
    slides.forEach((slide, i) => {
      slide.hidden = i !== current;
      screenButtons[i].setAttribute('aria-current', i === current ? 'step' : 'false');
    });
    const slide = slides[current];
    stage.scrollTop = 0;
    previous.disabled = current === 0;
    next.disabled = current === slides.length - 1;
    get('progress').textContent = `${current + 1} / ${slides.length} · ${slide.dataset.label}`;
    if (updateHash) history.replaceState(null, '', '#' + slide.id);
  }

  function openScreens() {
    screens.showModal();
    screenButtons[current].focus();
  }

  function toggleControls() {
    controls.hidden = !controls.hidden;
    showControls.hidden = !controls.hidden;
    (controls.hidden ? showControls : hideControls).focus();
  }

  async function toggleFullscreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
      get('notice').textContent = '';
    } catch {
      get('notice').textContent = 'Fullscreen is unavailable here. You can still advance the screens in this window.';
    }
  }

  playClip.addEventListener('click', () => {
    clip.append(clipTemplate.content.cloneNode(true));
    playClip.hidden = true;
    clip.querySelector('iframe').focus();
  });
  screensButton.addEventListener('click', openScreens);
  previous.addEventListener('click', () => goTo(current - 1));
  next.addEventListener('click', () => goTo(current + 1));
  fullscreen.addEventListener('click', toggleFullscreen);
  document.addEventListener('fullscreenchange', () => {
    fullscreen.textContent = document.fullscreenElement ? 'Exit fullscreen' : 'Fullscreen';
  });
  hideControls.addEventListener('click', toggleControls);
  showControls.addEventListener('click', toggleControls);

  const shortcuts = {
    ArrowRight: () => goTo(current + 1),
    PageDown: () => goTo(current + 1),
    ArrowLeft: () => goTo(current - 1),
    PageUp: () => goTo(current - 1),
    Home: () => goTo(0),
    End: () => goTo(slides.length - 1),
    f: toggleFullscreen,
    h: toggleControls,
    m: openScreens
  };

  document.addEventListener('keydown', (event) => {
    if (screens.open || event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.target.closest('input, textarea, select, [contenteditable]')) return;
    const command = shortcuts[event.key] || shortcuts[event.key.toLowerCase()];
    if (!command) return;
    event.preventDefault();
    command();
  });
  window.addEventListener('hashchange', () => goTo(currentFromHash(), false));
  goTo(currentFromHash(), false);
})();
