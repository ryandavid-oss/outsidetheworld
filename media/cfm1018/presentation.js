(() => {
  'use strict';
  const deck = globalThis.LessonDeck;
  const readings = globalThis.LessonReadings;
  if (!deck) return;
  const byId = id => document.getElementById(id);
  const stage = byId('slide-stage');
  const controls = byId('presentation-controls');
  const menu = byId('slide-menu');
  const help = byId('presentation-help');
  const reader = byId('scripture-reader');
  const status = byId('presentation-status');
  const questionIndex = new Map();
  const readingPositions = new Map();
  const readingScales = [0.88, 1, 1.18];
  const readingWordLimits = [96, 78, 58];
  let readingKey = null, readingPages = [], readingPage = 0, readingSize = 1;
  let currentId = deck.resolveId(location.hash);
  let pictureOnly = false;
  let controlsHidden = false;
  let wordplayRevealed = false;
  let dialogFocusTarget = stage;
  const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const currentSlide = () => deck.slides.find(slide => slide.id === currentId);
  const readingLink = (slide, label) => {
    const passage = readings?.forSource(slide.source);
    return `<a href="${escape(slide.source)}" target="_blank" rel="noopener"${passage ? ` data-reading="${escape(passage.key)}" aria-haspopup="dialog" aria-controls="scripture-reader"` : ''}>${escape(label)}${passage ? '' : ' ↗'}</a>`;
  };
  const sourceHTML = slide => slide.reference ? `<p class="slide-source">${slide.source ? readingLink(slide, slide.reference) : escape(slide.reference)}</p>` : '';
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
    } else if (slide.type === 'wordplay') {
      body = `<header class="wordplay-heading">${eyebrow}${title}</header>
        <div class="wordplay-pair${wordplayRevealed ? ' is-revealed' : ''}">
          <figure class="word-card word-ashes"><figcaption><p class="word-english">Ashes</p><p class="hebrew word-hebrew" lang="he" dir="rtl"><span class="letter-aleph">אֵ</span><span class="letter-pe">פֶ</span><span>ר</span></p><p class="word-pronunciation">’ēper <span>· eh-fer</span></p><p class="word-meaning">Ashes on the head.<br>A sign of mourning.</p></figcaption><div class="word-portrait"><img src="${escape(slide.artwork)}" width="1536" height="1024" alt="An imagined mourner with ashes scattered on his uncovered head."></div></figure>
          ${wordplayRevealed ? `<figure class="word-card word-beauty"><figcaption><p class="word-english">Beauty</p><p class="hebrew word-hebrew" lang="he" dir="rtl"><span class="letter-pe">פְּ</span><span class="letter-aleph">אֵ</span><span>ר</span></p><p class="word-pronunciation">pə’ēr <span>· peh-air</span></p><p class="word-meaning">A festive headdress.<br>A sign of honor and joy.</p></figcaption><div class="word-portrait"><img src="${escape(slide.artwork)}" width="1536" height="1024" alt="The same imagined man wearing a cream linen festive head covering, his head gently raised."></div></figure>` : `<div class="word-promise"><p>What does God give<br>in its place?</p><button type="button" data-reveal-wordplay>Reveal the promise <span aria-hidden="true">→</span></button></div>`}
        </div>
        <div class="wordplay-reflection" aria-live="polite">${wordplayRevealed ? `<p class="wordplay-explanation">The same three Hebrew letters.<br><strong>The first two exchange places.</strong></p><p class="wordplay-question">${escape(slide.question)}</p>` : `<p class="wordplay-invitation">“To give unto them beauty for ashes.”</p>`}</div>
        <div class="wordplay-actions">${readingLink(slide, 'Read Isaiah 61:3')}${wordplayRevealed ? '<button type="button" data-open-reflection>Linger here: the planting of the Lord <span aria-hidden="true">↗</span></button><button type="button" class="wordplay-replay" data-reset-wordplay>Show ashes again</button>' : ''}</div>`;
    } else if (slide.type === 'reflection') {
      body = `<div class="slide-copy">${eyebrow}${title}<p class="reflection-question">${escape(slide.body)}</p>${sourceHTML(slide)}<button type="button" class="reflection-return" data-return-wordplay>Back to beauty for ashes <span aria-hidden="true">↩</span></button></div>${imageHTML(slide)}`;
    } else if (slide.type === 'declaration') {
      body = `<div class="slide-copy">${eyebrow}<h1 class="sr-only" id="slide-title">Jesus’ declaration</h1><blockquote class="declaration-quote">“${escape(slide.quote)}”</blockquote>${sourceHTML(slide)}</div>${imageHTML(slide)}`;
    } else if (slide.type === 'question') {
      const index = questionIndex.get(slide.id) || 0;
      body = `${eyebrow}<h1 id="slide-title">${escape(slide.questions[index])}</h1><div class="question-actions"><button type="button" data-another-question>${index === 0 ? 'A follow-up question' : 'Return to the first question'}</button>${readingLink(slide, 'Read the passage')}</div>`;
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
    byId('next-slide').innerHTML = `${slide.type === 'wordplay' && !wordplayRevealed ? 'Reveal' : 'Next'} <span aria-hidden="true">→</span>`;
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
    if (currentId === 'planted') wordplayRevealed = true;
    pictureOnly = false;
    dialogFocusTarget = stage;
    if (menu.open) menu.close();
    if (help.open) help.close();
    if (reader.open) reader.close();
    if (push) {
      try {history.pushState(null, '', `#${currentId}`);} catch {location.hash = currentId;}
    }
    render();
    stage.focus({preventScroll:true});
    window.scrollTo(0, 0);
  }
  function move(direction) {
    if (currentSlide().type === 'wordplay' && ((direction > 0 && !wordplayRevealed) || (direction < 0 && wordplayRevealed))) {
      revealWordplay(direction > 0);return;
    }
    const target = deck.nextId(currentId, direction);
    if (target !== currentId) goTo(target);
  }
  function revealWordplay(revealed) {
    wordplayRevealed = revealed;render();stage.focus({preventScroll:true});
    status.textContent = revealed ? 'Beauty for ashes. The same three Hebrew letters; the first two exchange places.' : 'Ashes. A sign of mourning. Reveal the promise when you are ready.';
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
  function currentReading() {
    return readings?.passages.find(passage => passage.key === readingKey);
  }
  function prepareReading(verseNumber) {
    readingPages = readings.paginate(currentReading().verses, readingWordLimits[readingSize]);
    const remembered = verseNumber ?? readingPositions.get(readingKey);
    readingPage = Math.max(0, readingPages.findIndex(page => page.some(verse => verse.number === remembered)));
  }
  function renderReading() {
    const passage = currentReading(), verses = readingPages[readingPage];
    const first = verses[0].number, last = verses[verses.length - 1].number;
    const locationLabel = first === last ? `Verse ${first}` : `Verses ${first}–${last}`;
    byId('reader-title').textContent = passage.title;
    byId('reader-passage').value = passage.key;
    byId('reader-text').innerHTML = verses.map(verse => `<p class="reader-verse"><span class="reader-number" aria-label="Verse ${verse.number}">${verse.number}</span><span class="reader-verse-text">${escape(verse.text)}</span></p>`).join('');
    byId('reader-location').textContent = locationLabel;
    byId('reader-page-count').textContent = `${readingPage + 1} of ${readingPages.length}`;
    byId('reader-source').href = passage.source;
    byId('reader-source').setAttribute('aria-label', `Open ${passage.title} on the Church website`);
    byId('reader-previous').disabled = readingPage === 0;
    byId('reader-next').disabled = readingPage === readingPages.length - 1;
    byId('reader-smaller').disabled = readingSize === 0;
    byId('reader-larger').disabled = readingSize === readingScales.length - 1;
    reader.style.setProperty('--reader-scale', readingScales[readingSize]);
    byId('reader-body').scrollTop = 0;
    readingPositions.set(readingKey, first);
    byId('reader-status').textContent = `${passage.title}. ${locationLabel}. Page ${readingPage + 1} of ${readingPages.length}.`;
  }
  function openReading(key, trigger) {
    if (!readings?.passages.some(passage => passage.key === key)) return false;
    if (trigger) dialogFocusTarget = trigger;
    readingKey = key;
    prepareReading();renderReading();
    if (!reader.open) reader.showModal();
    document.body.classList.add('scripture-open');
    byId('reader-body').focus({preventScroll:true});
    return true;
  }
  function moveReading(direction) {
    const next = Math.max(0, Math.min(readingPages.length - 1, readingPage + direction));
    if (next !== readingPage) {readingPage = next;renderReading();}
  }
  function resizeReading(direction) {
    const next = Math.max(0, Math.min(readingScales.length - 1, readingSize + direction));
    if (next === readingSize) return;
    const verse = readingPages[readingPage][0].number;
    readingSize = next;prepareReading(verse);renderReading();
  }
  function returnFocus() {
    if (!menu.open && !help.open && !reader.open) (dialogFocusTarget.isConnected ? dialogFocusTarget : stage).focus({preventScroll:true});
  }
  byId('reader-passage').innerHTML = (readings?.passages || []).map(passage => `<option value="${escape(passage.key)}">${escape(passage.title)}</option>`).join('');
  byId('reader-passage').addEventListener('change', event => openReading(event.target.value));
  byId('reader-previous').addEventListener('click', () => moveReading(-1));
  byId('reader-next').addEventListener('click', () => moveReading(1));
  byId('reader-smaller').addEventListener('click', () => resizeReading(-1));
  byId('reader-larger').addEventListener('click', () => resizeReading(1));
  reader.addEventListener('close', () => {document.body.classList.remove('scripture-open');returnFocus();});
  reader.addEventListener('click', event => {if (event.target === reader) reader.close();});
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
    if (event.target.closest('[data-reveal-wordplay]')) {revealWordplay(true);return;}
    if (event.target.closest('[data-reset-wordplay]')) {revealWordplay(false);return;}
    if (event.target.closest('[data-open-reflection]')) {goTo('planted');return;}
    if (event.target.closest('[data-return-wordplay]')) {goTo('beauty-for-ashes');return;}
    const link = event.target.closest('[data-reading]');
    if (link && !event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey && openReading(link.dataset.reading, link)) {event.preventDefault();return;}
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
    if (reader.open) {
      if (command === 'next' || command === 'previous') {event.preventDefault();moveReading(command === 'next' ? 1 : -1);}
      else if (command === 'opening' || command === 'closing') {event.preventDefault();readingPage = command === 'opening' ? 0 : readingPages.length - 1;renderReading();}
      else if (command === 'fullscreen') {event.preventDefault();toggleFullscreen();}
      return;
    }
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
  for (const source of new Set(deck.slides.flatMap(slide => [slide.image, slide.artwork]).filter(Boolean))) {
    const picture = new Image();
    picture.src = source;
  }
})();
