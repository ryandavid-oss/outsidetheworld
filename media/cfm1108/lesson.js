(() => {
  'use strict';
  const slides = [...document.querySelectorAll('.slide')];
  const menu = document.getElementById('menu'), scenarioDialog = document.getElementById('scenario-dialog'), readingDialog = document.getElementById('reading-dialog');
  const menuButton = document.getElementById('menu-button');
  const prev = document.getElementById('prev'), next = document.getElementById('next');
  const progress = document.getElementById('progress'), controls = document.querySelector('.controls'), show = document.getElementById('show');
  const cards = {
    distance: ['01 · Feeling distant', 'Someone feels distant from God and isn’t sure how to begin again.'],
    hurt: ['02 · Feeling pushed away', 'Someone has been hurt or pushed away in a place where they hoped to belong.'],
    burden: ['03 · Carrying a burden', 'Someone is carrying a private burden that others don’t understand.']
  };
  let current = 0, returnFocus = null;
  const indexForHash = () => Math.max(0, slides.findIndex(s => s.id === decodeURIComponent(location.hash.slice(1))));
  function go(index, update = true) {
    current = Math.max(0, Math.min(slides.length - 1, index));
    slides.forEach((slide, i) => slide.hidden = i !== current);
    prev.disabled = current === 0; next.disabled = current === slides.length - 1;
    progress.textContent = `${String(current + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')} · ${slides[current].dataset.label}`;
    document.querySelectorAll('#menu-list button').forEach((button, i) => button.setAttribute('aria-current', i === current ? 'true' : 'false'));
    if (update) history.replaceState(null, '', `#${slides[current].id}`);
  }
  const menuList = document.getElementById('menu-list');
  slides.forEach((slide, i) => {
    const button = document.createElement('button'); button.type = 'button'; button.textContent = slide.dataset.label;
    button.addEventListener('click', () => { menu.close(); go(i); }); menuList.append(button);
  });
  function openDialog(dialog, button) { returnFocus = button; dialog.showModal(); }
  menuButton.addEventListener('click', () => { menuButton.setAttribute('aria-expanded', 'true'); openDialog(menu, menuButton); });
  menu.addEventListener('close', () => menuButton.setAttribute('aria-expanded', 'false'));
  document.querySelectorAll('[data-close]').forEach(button => button.addEventListener('click', () => button.closest('dialog').close()));
  scenarioDialog.addEventListener('close', () => { if (returnFocus) returnFocus.focus(); });
  document.querySelectorAll('[data-card]').forEach(button => button.addEventListener('click', () => {
    const [title, description] = cards[button.dataset.card];
    document.getElementById('scenario-number').textContent = title;
    document.getElementById('scenario-title').textContent = title.slice(5);
    document.getElementById('scenario-text').textContent = description;
    openDialog(scenarioDialog, button);
  }));
  let reading = null, readingPage = 0;
  const readingPrev = document.getElementById('reading-prev'), readingNext = document.getElementById('reading-next');
  function updateReading() {
    const [number, verse] = reading.pages[readingPage];
    const text = document.getElementById('reading-text');
    text.replaceChildren(); const span = document.createElement('span'); const sup = document.createElement('sup');
    sup.textContent = number; span.append(sup, document.createTextNode(verse)); text.append(span);
    document.getElementById('reading-page').textContent = `Page ${readingPage + 1} of ${reading.pages.length}`;
    readingPrev.disabled = readingPage === 0; readingNext.disabled = readingPage === reading.pages.length - 1;
  }
  document.querySelectorAll('[data-reading]').forEach(button => button.addEventListener('click', () => {
    reading = window.lessonReadings[button.dataset.reading]; readingPage = 0;
    document.getElementById('reading-title').textContent = reading.title;
    document.getElementById('reading-source').href = reading.source;
    updateReading(); openDialog(readingDialog, button);
  }));
  readingPrev.addEventListener('click', () => {if (readingPage > 0) {readingPage--; updateReading();}});
  readingNext.addEventListener('click', () => {if (readingPage < reading.pages.length - 1) {readingPage++; updateReading();}});
  readingDialog.addEventListener('close', () => {if (returnFocus) returnFocus.focus();});
  prev.addEventListener('click', () => go(current - 1)); next.addEventListener('click', () => go(current + 1));
  function toggleControls() { const hidden = !controls.hidden; controls.hidden = hidden; show.hidden = !hidden; }
  document.getElementById('hide').addEventListener('click', toggleControls); show.addEventListener('click', toggleControls);
  async function fullscreen() { try { if (document.fullscreenElement) await document.exitFullscreen(); else await document.documentElement.requestFullscreen(); } catch {} }
  document.getElementById('fullscreen').addEventListener('click', fullscreen);
  document.addEventListener('keydown', e => {
    if (readingDialog.open) {
      if (['ArrowRight','PageDown'].includes(e.key)) {e.preventDefault();readingNext.click();}
      else if (['ArrowLeft','PageUp'].includes(e.key)) {e.preventDefault();readingPrev.click();}
      return;
    }
    if (e.target.matches('input, textarea, select') || menu.open || scenarioDialog.open) return;
    if (['ArrowRight', 'ArrowDown', 'PageDown'].includes(e.key) || (e.key === ' ' && !e.shiftKey && e.target.tagName !== 'BUTTON')) {e.preventDefault();go(current + 1);}
    else if (['ArrowLeft', 'ArrowUp', 'PageUp'].includes(e.key) || (e.key === ' ' && e.shiftKey && e.target.tagName !== 'BUTTON')) {e.preventDefault();go(current - 1);}
    else if (e.key === 'Home') go(0); else if (e.key === 'End') go(slides.length - 1);
    else if (e.key.toLowerCase() === 'f') fullscreen(); else if (e.key.toLowerCase() === 'h') toggleControls();
    else if (e.key.toLowerCase() === 'm') {menuButton.setAttribute('aria-expanded', 'true');openDialog(menu, menuButton);}
  });
  addEventListener('hashchange', () => go(indexForHash(), false)); go(indexForHash(), false);
})();
