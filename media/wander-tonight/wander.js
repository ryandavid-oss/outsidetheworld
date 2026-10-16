(() => {
  'use strict';
  const key = 'otw-wander-2026-10-16';
  const cards = [...document.querySelectorAll('[data-card]')];
  const names = new Map(cards.map(card => [card.dataset.card, card.querySelector('h2').textContent]));
  const status = document.getElementById('favorite-status');
  const note = document.getElementById('selection-note');
  const title = document.getElementById('our-plan-title');
  const copy = document.getElementById('plan-copy');
  const eyebrow = document.getElementById('plan-eyebrow');
  const links = document.getElementById('saved-plan-links');
  const savedLink = document.getElementById('saved-card-link');
  const saveExplanation = document.getElementById('save-explanation');
  let favorite = null;
  let canSave = true;
  try {
    const stored = localStorage.getItem(key);
    if (names.has(stored)) favorite = stored;
  } catch (_) { canSave = false; }

  function render(announce = false) {
    cards.forEach(card => {
      const selected = card.dataset.card === favorite;
      card.classList.toggle('is-favorite', selected);
      card.querySelectorAll('[data-favorite]').forEach(button => {
        button.hidden = false;
        button.setAttribute('aria-pressed', String(selected));
        button.setAttribute('aria-label', `${selected ? 'Clear choice of' : 'Choose'} ${names.get(card.dataset.card)}`);
        const label = button.querySelector('span');
        if (label) label.textContent = selected ? 'Current pick' : 'Pick this one';
      });
    });
    const name = names.get(favorite);
    if (name) {
      note.textContent = `Current pick: ${name}. You can change it anytime.`;
      eyebrow.textContent = 'Current pick';
      title.textContent = name;
      copy.textContent = 'Saved as your favorite. Details and directions are in the card above.';
      savedLink.href = `#${favorite}`;
      savedLink.textContent = 'See this option ↑';
      links.hidden = false;
      saveExplanation.hidden = false;
      saveExplanation.textContent = canSave ? 'Saved in this browser. Nothing is sent.' : 'Chosen for this visit. This browser isn’t allowing saved favorites.';
      if (announce) status.textContent = `${name} is selected. ${canSave ? 'Saved in this browser.' : 'Chosen for this visit only.'}`;
    } else {
      note.textContent = canSave ? 'Tap a heart to save a favorite. You can change it later.' : 'Tap a heart to choose for this visit. This browser isn’t allowing saved favorites.';
      eyebrow.textContent = 'Your pick';
      title.textContent = 'Anything look good?';
      copy.textContent = 'Tap a heart on any neighborhood to save it here.';
      links.hidden = true;
      saveExplanation.hidden = true;
      if (announce) status.textContent = 'Favorite cleared. Choose any of the five options.';
    }
  }
  function choose(id) {
    favorite = favorite === id ? null : id;
    try {
      if (favorite) localStorage.setItem(key, favorite);
      else localStorage.removeItem(key);
      canSave = true;
    } catch (_) { canSave = false; }
    render(true);
  }
  document.querySelectorAll('[data-favorite]').forEach(button => {
    button.addEventListener('click', () => choose(button.dataset.favorite));
  });
  document.getElementById('clear-favorite').addEventListener('click', () => {
    // Return focus to a visible control before the clear button is hidden.
    const previous = favorite;
    if (previous) document.querySelector(`#${previous} .heart-button`).focus({ preventScroll: true });
    choose(null);
    document.getElementById(previous || 'possibilities').scrollIntoView({ block: 'start' });
  });
  window.addEventListener('storage', event => {
    if (event.key !== key && event.key !== null) return;
    favorite = names.has(event.newValue) ? event.newValue : null;
    render();
  });
  render();

  // Native scrolling remains usable without JavaScript or a pointer.
  cards.forEach(card => {
    const rail = card.querySelector('.photo-rail');
    const arrows = card.querySelector('.gallery-arrows');
    const prev = arrows.querySelector('[data-direction="-1"]');
    const next = arrows.querySelector('[data-direction="1"]');
    arrows.hidden = false;
    let frame;
    const update = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        prev.disabled = rail.scrollLeft < 4;
        next.disabled = rail.scrollLeft + rail.clientWidth >= rail.scrollWidth - 4;
      });
    };
    arrows.querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
      const width = rail.querySelector('.photo').getBoundingClientRect().width;
      const gap = parseFloat(getComputedStyle(rail).columnGap) || 10;
      rail.scrollBy({ left: (width + gap) * Number(button.dataset.direction), behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
    }));
    rail.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update, { passive: true });
    update();
  });

  // Keep date-specific language honest if this invitation is opened later.
  function updateDate() {
    const parts = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Phoenix', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', hourCycle: 'h23' }).formatToParts(new Date());
    const values = Object.fromEntries(parts.map(part => [part.type, part.value]));
    const day = `${values.year}-${values.month}-${values.day}`;
    const target = '2026-10-16';
    const notice = document.getElementById('date-notice');
    const event = document.getElementById('event-kicker');
    if (day === target) {
      notice.hidden = true;
      event.textContent = Number(values.hour) >= 22 ? 'Earlier tonight · Oct 16 · confirmed' : 'Tonight only · Oct 16 · confirmed';
    } else {
      notice.hidden = false;
      notice.textContent = 'These options were checked for Friday, October 16, 2026. Event details belong to that date; check current hours for another day.';
      event.textContent = 'For Oct 16, 2026 · confirmed listing';
    }
  }
  updateDate();
  window.addEventListener('pageshow', updateDate);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) updateDate(); });
})();
