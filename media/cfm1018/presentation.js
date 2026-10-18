(() => {
  'use strict';
  const deck = globalThis.LessonDeck;
  if (!deck) return;
  const byId = id => document.getElementById(id);
  const stage = byId('slide-stage');
  const controls = byId('presentation-controls');
  const menu = byId('slide-menu');
  const help = byId('presentation-help');
  const status = byId('presentation-status');
  const questionIndex = new Map();
  let currentId = deck.resolveId(location.hash);
  let pictureOnly = false;
  let controlsHidden = false;
  let dialogFocusTarget = stage;
  const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const currentSlide = () => deck.slides.find(slide => slide.id === currentId);
  const sourceHTML = slide => slide.reference ? `<p class="slide-source">${slide.source ? `<a href="${escape(slide.source)}" target="_blank" rel="noopener">${escape(slide.reference)} ↗</a>` : escape(slide.reference)}</p>` : '';
  const imageHTML = slide => `<figure class="slide-art"><img src="${escape(slide.image)}" width="1536" height="1024" alt="${escape(slide.alt)}" decoding="async" fetchpriority="high"></figure>`;
  function render() {
    const slide = currentSlide();
    const eyebrow = `<p class="eyebrow">${escape(slide.eyebrow)}</p>`;
    const title = slide.title ? `<h1 id="slide-title">${escape(slide.title)}</h1>` : '';
    let body = '';
    if (slide.type === 'opening') {
      body = `<header class="tv-lesson-heading" aria-label="Official Come, Follow Me lesson"><p class="tv-lesson-title">October 12–18: “The Redeemer Shall Come to Zion”</p><p class="tv-lesson-range">Isaiah 58–66</p></header><div class="slide-copy">${eyebrow}${title}<p class="slide-subtitle">${escape(slide.subtitle)}</p></div>${imageHTML(slide)}`;
    } else if (slide.type === 'scripture') {
      body = `${eyebrow}${title}<blockquote class="scripture-lines">${slide.lines.map(line => `<p>${escape(line)}</p>`).join('')}</blockquote>${sourceHTML(slide)}`;
    } else if (slide.type === 'declaration') {
      body = `<div class="slide-copy">${eyebrow}<h1 class="sr-only" id="slide-title">Jesus’ declaration</h1><blockquote class="declaration-quote">“${escape(slide.quote)}”</blockquote>${sourceHTML(slide)}</div>${imageHTML(slide)}`;
    } else if (slide.type === 'question') {
      const index = questionIndex.get(slide.id) || 0;
      body = `${eyebrow}<h1 id="slide-title">${escape(slide.questions[index])}</h1><div class="question-actions"><button type="button" data-another-question>${index === 0 ? 'A follow-up question' : 'Return to the first question'}</button><a href="${escape(slide.source)}" target="_blank" rel="noopener">Read the passage ↗</a></div>`;
    } else if (slide.type === 'context') {
      body = `${eyebrow}${title}<blockquote class="context-quote">“${escape(slide.quote)}”</blockquote><p class="context-body">${escape(slide.body)}</p>${sourceHTML(slide)}`;
    } else if (slide.type === 'story') {
      body = `<div class="slide-copy">${eyebrow}${title}<p class="story-summary">${escape(slide.body)}</p>${sourceHTML(slide)}</div>${imageHTML(slide)}`;
    } else if (slide.type === 'closing') {
      body = `<div class="slide-copy">${eyebrow}${title}<p class="slide-subtitle">${escape(slide.reference)}</p></div>${imageHTML(slide)}`;
    }
    stage.innerHTML = `<section class="slide slide-${escape(slide.type)}" aria-labelledby="slide-title">${body}</section>`;
    document.body.classList.toggle('picture-only', pictureOnly && Boolean(slide.image));
    byId('previous-slide').disabled = currentId === deck.slides[0].id;
    byId('next-slide').disabled = currentId === deck.slides[deck.slides.length - 1].id;
    byId('image-only').hidden = !slide.image;
    byId('image-only').setAttribute('aria-pressed', String(pictureOnly && Boolean(slide.image)));
    byId('image-only').textContent = pictureOnly ? 'Show words' : 'Picture only';
    byId('current-section').textContent = deck.groups.find(group => group.id === slide.group).title;
    for (const button of document.querySelectorAll('[data-slide-id]')) {
      if (button.dataset.slideId === currentId) button.setAttribute('aria-current', 'true');
      else button.removeAttribute('aria-current');
    }
    status.textContent = slide.label;
    document.title = `${slide.label} · What Jesus came to do`;
  }
  function goTo(value, push = true) {
    currentId = deck.resolveId(value);
    pictureOnly = false;
    dialogFocusTarget = stage;
    if (menu.open) menu.close();
    if (help.open) help.close();
    if (push) {
      try {history.pushState(null, '', `#${currentId}`);} catch {location.hash = currentId;}
    }
    render();
    stage.focus({preventScroll:true});
    window.scrollTo(0, 0);
  }
  function move(direction) {
    const target = deck.nextId(currentId, direction);
    if (target !== currentId) goTo(target);
  }
  function togglePicture() {
    if (!currentSlide().image) return;
    pictureOnly = !pictureOnly;
    render();
    stage.focus({preventScroll:true});
    status.textContent = pictureOnly ? 'Picture only. Press I to restore the words.' : currentSlide().label;
  }
  function toggleControls() {
    controlsHidden = !controlsHidden;
    controls.hidden = controlsHidden;
    byId('show-controls').hidden = !controlsHidden;
    document.body.classList.toggle('controls-hidden', controlsHidden);
    if (controlsHidden) stage.focus({preventScroll:true});
    else byId('hide-controls').focus();
    status.textContent = controlsHidden ? 'Controls hidden. Press H to show them.' : 'Controls shown.';
  }
  async function toggleFullscreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else if (typeof document.documentElement.requestFullscreen === 'function') await document.documentElement.requestFullscreen();
      else throw new Error('Fullscreen unavailable');
    } catch {
      showNotice('Fullscreen is unavailable here. You can still use the presentation in this window.');
    }
  }
  function showNotice(message) {
    let notice = byId('presentation-notice');
    if (!notice) {notice = document.createElement('p');notice.id = 'presentation-notice';notice.className = 'presentation-notice';notice.setAttribute('role','status');document.body.append(notice);}
    notice.textContent = message;
    status.textContent = message;
    notice.hidden = false;
    notice.addEventListener('click', () => {notice.hidden = true;}, {once:true});
  }
  function openMenu() {
    dialogFocusTarget = controlsHidden ? stage : byId('open-menu');
    menu.showModal();
    menu.querySelector('[aria-current="true"]')?.focus();
  }
  function returnFocus() {
    if (!menu.open && !help.open) dialogFocusTarget.focus({preventScroll:true});
  }
  byId('menu-groups').innerHTML = deck.groups.map(group => `<section class="menu-group"><h3>${escape(group.title)}</h3>${deck.slides.filter(slide => slide.group === group.id).map(slide => `<button type="button" data-slide-id="${escape(slide.id)}">${escape(slide.label)}</button>`).join('')}</section>`).join('');
  byId('previous-slide').addEventListener('click', () => move(-1));
  byId('next-slide').addEventListener('click', () => move(1));
  byId('open-menu').addEventListener('click', openMenu);
  byId('image-only').addEventListener('click', togglePicture);
  byId('fullscreen').addEventListener('click', toggleFullscreen);
  byId('hide-controls').addEventListener('click', toggleControls);
  byId('show-controls').addEventListener('click', toggleControls);
  byId('open-help').addEventListener('click', () => {menu.close();help.showModal();});
  menu.addEventListener('close', returnFocus);
  help.addEventListener('close', returnFocus);
  for (const button of document.querySelectorAll('[data-close-dialog]')) {
    button.addEventListener('click', () => button.closest('dialog').close());
  }
  menu.addEventListener('click', event => {
    const button = event.target.closest('[data-slide-id]');
    if (button) goTo(button.dataset.slideId);
  });
  stage.addEventListener('click', event => {
    if (!event.target.closest('[data-another-question]')) return;
    const slide = currentSlide();
    questionIndex.set(slide.id, ((questionIndex.get(slide.id) || 0) + 1) % slide.questions.length);
    render();stage.focus({preventScroll:true});
  });
  document.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.repeat || menu.open || help.open) return;
    if (event.target.closest('input,textarea,select,[contenteditable="true"]')) return;
    if ([' ','Spacebar'].includes(event.key) && event.target.closest('button,a')) return;
    const command = deck.commandForKey(event.key, event.shiftKey);
    if (!command) return;
    if (command === 'escape' && !pictureOnly) return;
    event.preventDefault();
    if (command === 'next') move(1);
    else if (command === 'previous') move(-1);
    else if (command === 'opening' || command === 'closing') goTo(command);
    else if (command === 'fullscreen') toggleFullscreen();
    else if (command === 'controls') toggleControls();
    else if (command === 'menu') openMenu();
    else if (command === 'picture') togglePicture();
    else if (command === 'escape' && pictureOnly) togglePicture();
  });
  window.addEventListener('hashchange', () => goTo(location.hash, false));
  document.addEventListener('fullscreenchange', () => {
    byId('fullscreen').textContent = document.fullscreenElement ? 'Exit fullscreen' : 'Fullscreen';
    byId('fullscreen').setAttribute('aria-pressed', String(Boolean(document.fullscreenElement)));
  });
  try {history.replaceState(null, '', `#${currentId}`);} catch {}
  render();
  for (const source of new Set(deck.slides.map(slide => slide.image).filter(Boolean))) {
    const picture = new Image();
    picture.src = source;
  }
})();
