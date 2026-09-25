(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const official = 'https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-old-testament-2026/39?lang=eng';
  const scripture = (chapter, verses) => `https://www.churchofjesuschrist.org/study/scriptures/ot/isa/${chapter}?lang=eng&id=${verses}#${verses.split(/[,-]/)[0]}`;
  const paths = {
    hope: {
      name: 'Hope for a fearful heart', short: 'Hope · Isaiah 35', reference: 'Isaiah 35:3–6', url: scripture(35, 'p3-p6'),
      context: 'Isaiah describes restoration: the desert blossoms, people are healed, and the redeemed return to Zion. In the middle of these promises, he calls on people to strengthen one another. Their reason for courage is that God will come and save them.',
      verses: [
        [3, 'Strengthen ye the weak hands, and confirm the feeble knees.'],
        [4, 'Say to them that are of a fearful heart, Be strong, fear not: behold, your God will come with vengeance, even God with a recompence; he will come and save you.'],
        [5, 'Then the eyes of the blind shall be opened, and the ears of the deaf shall be unstopped.'],
        [6, 'Then shall the lame man leap as an hart, and the tongue of the dumb sing: for in the wilderness shall waters break out, and streams in the desert.']
      ],
      groups: [[0, 1], [2, 3]],
      question: 'What do you notice about the reason Isaiah gives people to have courage?',
      alternate: 'Which words help you understand what the Savior is like?',
      application: 'How could these verses shape the way we respond to someone who feels afraid or worn down?',
      applicationHint: 'What could we say? What could we do?',
      note: 'Let people notice the reason for courage in verse 4. If someone shares something painful, acknowledge it. Leave room for hope while a difficulty is still unresolved.'
    },
    refuge: {
      name: 'Refuge in the storm', short: 'Refuge · Isaiah 25', reference: 'Isaiah 25:4, 8–9', url: scripture(25, 'p4,p8-p9'),
      context: 'Isaiah praises the Lord for being a refuge to people in distress. He looks forward to the Lord overcoming death and wiping away tears. The people rejoice in the salvation they have waited for.',
      verses: [
        [4, 'For thou hast been a strength to the poor, a strength to the needy in his distress, a refuge from the storm, a shadow from the heat, when the blast of the terrible ones is as a storm against the wall.'],
        [8, 'He will swallow up death in victory; and the Lord God will wipe away tears from off all faces; and the rebuke of his people shall he take away from off all the earth: for the Lord hath spoken it.'],
        [9, 'And it shall be said in that day, Lo, this is our God; we have waited for him, and he will save us: this is the Lord; we have waited for him, we will be glad and rejoice in his salvation.']
      ],
      groups: [[0], [1, 2]],
      question: 'What might the Savior’s refuge look like while a difficult situation is still unresolved?',
      alternate: 'What do the promises in verses 8–9 help you understand about the Savior?',
      application: 'How could we help someone feel the Savior’s care during a difficult week?',
      applicationHint: 'Think of one small, specific act of care.',
      note: 'Distinguish comfort we can receive now from promises whose fulfillment is still ahead. People can discuss the passage without sharing a personal loss.'
    },
    mercy: {
      name: 'Mercy as we return', short: 'Mercy · Isaiah 30', reference: 'Isaiah 30:15, 18–21', url: scripture(30, 'p15,p18-p21'),
      context: 'Isaiah warns a people who have resisted the Lord’s counsel and sought security in Egypt. Even here, the Lord invites them to return. Isaiah speaks of His mercy, His response to their cries, and His guidance through adversity.',
      verses: [
        [15, 'For thus saith the Lord God, the Holy One of Israel; In returning and rest shall ye be saved; in quietness and in confidence shall be your strength: and ye would not.'],
        [18, 'And therefore will the Lord wait, that he may be gracious unto you, and therefore will he be exalted, that he may have mercy upon you: for the Lord is a God of judgment: blessed are all they that wait for him.'],
        [19, 'For the people shall dwell in Zion at Jerusalem: thou shalt weep no more: he will be very gracious unto thee at the voice of thy cry; when he shall hear it, he will answer thee.'],
        [20, 'And though the Lord give you the bread of adversity, and the water of affliction, yet shall not thy teachers be removed into a corner any more, but thine eyes shall see thy teachers:'],
        [21, 'And thine ears shall hear a word behind thee, saying, This is the way, walk ye in it, when ye turn to the right hand, and when ye turn to the left.']
      ],
      groups: [[0, 1], [2, 3], [4]],
      question: 'What do these verses help you understand about the Lord’s willingness to receive someone who returns to Him?',
      alternate: 'What do you notice about His mercy and guidance in these verses?',
      application: 'What could one small step toward the Savior look like this week?',
      applicationHint: 'You can consider this quietly or share a thought.',
      note: 'Keep the invitation open and gentle. A person can think about returning to the Lord without describing private struggles to the class.'
    }
  };
  const escape = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const verseHTML = verses => `<div class="verse-list">${verses.map(([number, text]) => `<p class="verse"><span class="verse-number">${number}</span>${escape(text)}</p>`).join('')}</div>`;
  const sourceHTML = path => `<a class="source-link" href="${escape(path.url)}" target="_blank" rel="noopener noreferrer">${path.reference} · King James Version · Read on the Church website ↗</a>`;
  const stepsFor = () => ['opening', ...paths[selectedPath].groups.map((_,index) => `read-${index+1}`), 'reflect', 'apply', 'closing'];
  const timerKey = 'otw-cfm927-class-timer';
  const duration = 25 * 60 * 1000;
  let selectedPath = 'hope', currentStep = 'opening', presenting = false;
  let timer = { remaining: duration, deadline: null };
  let pauseDeadline = null;
  let toastTimeout;
  try {
    const saved = JSON.parse(sessionStorage.getItem(timerKey));
    if (saved && Number.isFinite(saved.remaining) && saved.remaining >= 0 && saved.remaining <= duration && (saved.deadline === null || Number.isFinite(saved.deadline))) timer = saved;
    const path = sessionStorage.getItem('otw-cfm927-path');
    if (Object.hasOwn(paths, path)) selectedPath = path;
  } catch { /* The page also works when storage is unavailable. */ }
  function saveTimer() { try { sessionStorage.setItem(timerKey, JSON.stringify(timer)); } catch {} }
  function remaining() { return timer.deadline === null ? timer.remaining : Math.max(0, timer.deadline - Date.now()); }
  function timeString(ms) { const seconds = Math.max(0, Math.ceil(ms / 1000)); return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`; }
  function notify(message) {
    $('status').textContent = message; $('status').hidden = false;
    clearTimeout(toastTimeout); toastTimeout = setTimeout(() => { $('status').hidden = true; }, 4000);
  }
  function updateClock() {
    const value = remaining();
    if (timer.deadline !== null && value === 0) { timer = { remaining: 0, deadline: null }; saveTimer(); $('announcement').textContent = 'The 25-minute class time is complete. Time to close.'; }
    if ($('timer-toggle')) {
      $('timer-display').textContent = timeString(value);
      $('timer-label').textContent = value === 0 ? 'Time to close' : timer.deadline !== null ? 'Pause timer' : value === duration ? 'Start class' : 'Resume timer';
      $('timer-toggle').classList.toggle('expired', value === 0);
      $('timer-toggle').setAttribute('aria-label', value === 0 ? 'Class timer complete' : `${timer.deadline !== null ? 'Pause' : 'Start'} class timer, ${timeString(value)} remaining`);
      $('timer-toggle').setAttribute('aria-pressed', String(timer.deadline !== null));
      $('timer-toggle').disabled = value === 0;
    }
    if (pauseDeadline !== null) {
      const left = Math.max(0, pauseDeadline - Date.now());
      if ($('pause-clock')) $('pause-clock').textContent = left ? timeString(left) : 'Continue when you’re ready.';
      if (left === 0) { pauseDeadline = null; if ($('think-toggle')) { $('think-toggle').textContent = 'Another 30 seconds'; $('think-toggle').setAttribute('aria-pressed', 'false'); } }
    }
  }
  function openDiscussion(step = 'opening') {
    location.hash = ['opening', 'closing'].includes(step) ? `discuss/${step}` : `discuss/${selectedPath}/${step}`;
  }
  function focusTitle(id) { const element = $(id); if (element) element.focus({preventScroll:true}); window.scrollTo({top:0,behavior:'instant'}); }
  function renderStudy() {
    $('study/hope').innerHTML = Object.entries(paths).map(([id, path], index) => `<details class="passage" id="passage-${id}" ${id === 'hope' ? 'open' : ''}>
      <summary><span class="passage-number">0${index + 1}</span><span class="passage-name">${path.name}<small>${path.reference}</small></span><span class="expand-mark" aria-hidden="true">+</span></summary>
      <div class="passage-body"><div>${verseHTML(path.verses)}${sourceHTML(path)}</div><div class="reflection"><h3>Consider</h3><p>${path.question}</p><details class="plain-language"><summary>In plain language</summary><p>${path.context}</p></details></div></div>
    </details>`).join('');
  }
  function renderPresentation() {
    const path = paths[selectedPath], steps = stepsFor(), index = steps.indexOf(currentStep);
    let content;
    if (currentStep === 'opening') content = `<p class="eyebrow">As we gather · September 27</p><h2 id="slide-title" tabindex="-1">What did you learn this week about <em>the Savior?</em></h2><p class="slide-hint">A verse. An experience. A question you’re still thinking about.</p><div class="reflection-pause"><button class="button secondary" id="think-toggle" type="button" aria-pressed="false">Take 30 seconds to think</button><span class="pause-clock" id="pause-clock" role="status"></span></div>`;
    else if (currentStep.startsWith('read-')) {
      const group = path.groups[Number(currentStep.slice(5))-1];
      content = `<p class="eyebrow">Read together · ${path.name}</p><h2 id="slide-title" tabindex="-1">${path.reference}</h2>${verseHTML(group.map(i => path.verses[i]))}${sourceHTML(path)}`;
    } else if (currentStep === 'reflect') content = `<p class="eyebrow">What do you notice? · ${path.reference}</p><h2 id="slide-title" tabindex="-1">${path.question}</h2><details class="alternate"><summary>Another question</summary><p>${path.alternate}</p></details>`;
    else if (currentStep === 'apply') content = `<p class="eyebrow">Living what we learn</p><h2 id="slide-title" tabindex="-1">${path.application}</h2><p class="slide-hint">${path.applicationHint}</p>`;
    else content = `<p class="eyebrow">Into the week</p><h2 id="slide-title" tabindex="-1">What is one phrase about the Savior you want to <em>carry with you?</em></h2><p class="slide-hint">Return to it in your study and prayers this week.</p>`;
    $('discuss/opening').innerHTML = `<div class="presentation-top"><label class="path-control" for="path-select"><span>Our passage</span><select id="path-select" aria-label="Choose discussion passage">${Object.entries(paths).map(([id,p]) => `<option value="${id}" ${id === selectedPath ? 'selected' : ''}>${p.short}</option>`).join('')}</select></label><div class="presentation-tools"><a href="#guide">Leader guide</a><button class="quiet-button" id="fullscreen" type="button">${document.fullscreenElement ? 'Exit fullscreen' : 'Fullscreen'}</button></div></div>
      <div class="slide ${currentStep.startsWith('read-') ? 'reading-slide' : ''}">${content}</div>
      <nav class="presentation-controls" aria-label="Discussion controls"><div class="timer-controls"><button class="timer" id="timer-toggle" type="button"><span id="timer-display">25:00</span><span class="timer-label" id="timer-label">Start class</span></button><button class="quiet-button timer-reset" id="timer-reset" type="button" aria-label="Reset class timer to 25 minutes">↺</button></div><div class="navigation"><button class="button secondary" id="previous" type="button" ${index === 0 ? 'disabled' : ''}>← <span>Back</span></button><span class="slide-count" aria-label="Slide ${index+1} of ${steps.length}">${index+1} / ${steps.length}</span><button class="button" id="next" type="button">${index === steps.length-1 ? 'Back to start' : 'Next'} <span aria-hidden="true">→</span></button></div></nav><div class="progress" aria-hidden="true"><span style="width:${((index+1)/steps.length)*100}%"></span></div>`;
    $('path-select').addEventListener('change', event => {
      selectedPath = event.target.value;
      pauseDeadline = null;
      if (!stepsFor().includes(currentStep)) currentStep = 'read-1';
      try { sessionStorage.setItem('otw-cfm927-path', selectedPath); } catch {}
      if (['opening', 'closing'].includes(currentStep)) { renderPresentation(); $('path-select').focus(); } else openDiscussion(currentStep);
    });
    $('previous').addEventListener('click', () => openDiscussion(steps[Math.max(0,index-1)]));
    $('next').addEventListener('click', () => openDiscussion(steps[(index+1)%steps.length]));
    $('timer-toggle').addEventListener('click', () => { const left = remaining(); if (!left) return; timer = timer.deadline !== null ? {remaining:left,deadline:null} : {remaining:left,deadline:Date.now()+left}; saveTimer(); updateClock(); });
    $('timer-reset').addEventListener('click', () => { timer = {remaining:duration,deadline:null}; saveTimer(); updateClock(); notify('Class timer reset to 25:00.'); });
    $('fullscreen').addEventListener('click', async () => {
      try { if (document.fullscreenElement) await document.exitFullscreen(); else if (document.documentElement.requestFullscreen) await document.documentElement.requestFullscreen(); else notify('Fullscreen is unavailable in this browser. The discussion still works here.'); } catch { notify('Fullscreen is unavailable. You can continue in this window.'); }
    });
    if ($('think-toggle')) $('think-toggle').addEventListener('click', () => {
      if (pauseDeadline !== null) { pauseDeadline = null; $('pause-clock').textContent = ''; $('think-toggle').textContent = 'Take 30 seconds to think'; $('think-toggle').setAttribute('aria-pressed','false'); }
      else { pauseDeadline = Date.now()+30000; $('think-toggle').textContent = 'Stop reflection timer'; $('think-toggle').setAttribute('aria-pressed','true'); updateClock(); }
    });
    updateClock();
  }
  function renderGuide() {
    $('guide').innerHTML = `<p class="eyebrow">For the person leading · September 27, 2026</p><h1 id="guide-title" tabindex="-1">A little structure.<br>Room to listen.</h1><p class="guide-intro">One opening question, one passage to explore, and one invitation to take home. Stay with a meaningful conversation; the other passages are there if you need them.</p>
      <div class="guide-actions"><a class="button" href="#discuss/opening">Open discussion →</a><a class="button secondary" href="#">Return to study</a><button class="button secondary" id="print-guide" type="button">Print guide</button></div>
      <h2>Begin here</h2><blockquote>What did you learn this week about the Savior?</blockquote><p>“Take a moment to look back through your scriptures or notes. A phrase, an experience, or a question you’re still thinking about would be welcome.”</p>
      <h2>Your 25 minutes</h2><ol class="rundown">
      <li><time>0–2</time><div><strong>Welcome and opening prayer</strong><p>Put up the opening question. Give people a moment to settle.</p></div></li>
      <li><time>2–7</time><div><strong>Listen to what people brought</strong><p>Allow quiet thinking time, then invite responses. Try: “What helped you see that?” or “Could we read that verse together?”</p></div></li>
      <li><time>7–17</time><div><strong>Explore one passage</strong><p>Begin with Isaiah 35:3–6 if the conversation needs a starting point. Read slowly and ask what people notice about the Savior. Follow a useful contribution.</p></div></li>
      <li><time>17–22</time><div><strong>Connect it with daily life</strong><p>“How could these verses shape the way we respond to someone who feels afraid or worn down?” Invite a specific, practical thought.</p></div></li>
      <li><time>22–25</time><div><strong>Carry one phrase home</strong><p>Invite everyone to choose a phrase. Share a brief testimony connected to the discussion, encourage continued home study, and close with prayer.</p></div></li></ol>
      <h2>A few words when you need them</h2><ul class="guide-tips"><li><strong>If it’s quiet:</strong> “Which word or phrase caught your attention?” Give people a little time to look.</li><li><strong>After a meaningful comment:</strong> “What does that help the rest of us notice?” Let another person respond.</li><li><strong>If the conversation wanders:</strong> “Let’s bring that back to the passage. What does it help us understand about the Savior?”</li><li><strong>If you don’t know:</strong> “I’d like to study that more before giving you an answer.”</li><li><strong>To make room for others:</strong> “Thank you. Let’s hear from someone who hasn’t had a chance yet.”</li></ul>
      <h2>Follow the conversation</h2><p>The passage menu in discussion mode lets you change direction. Choose one; you do not need to cover all three.</p><div class="guide-options">${Object.entries(paths).map(([id,path]) => `<a class="text-link" href="#discuss/${id}/read-1">${path.short} →</a>`).join('')}</div>
      ${Object.values(paths).map(path => `<details class="plain-language"><summary>${path.name} · Leader note</summary><p>${path.note}</p></details>`).join('')}
      <div class="guide-note"><p><strong>On the screen:</strong> use the discussion view. This guide is a separate view you can keep open on your phone. It is a public page, with no sign-in.</p><p><strong>Time:</strong> select “Start class” when class begins. The timer continues as you move between slides and survives a refresh in the same tab. Pause or reset it yourself. The 30-second reflection timer also waits for you to continue.</p><p><strong>Navigation:</strong> use the buttons or ← / →. Home returns to the opening; End goes to the closing invitation. F toggles fullscreen. Nothing advances automatically.</p></div>
      <h2>Keep the official study close</h2><p><a href="${official}" target="_blank" rel="noopener noreferrer">September 21–27: “A Marvellous Work and a Wonder” ↗</a></p><p><a href="https://www.churchofjesuschrist.org/feature/sunday-meeting-schedule?lang=eng" target="_blank" rel="noopener noreferrer">Guidance for a 25-minute Sunday School class ↗</a></p>`;
    $('print-guide').addEventListener('click', () => window.print());
  }
  function updateAvailability() {
    const sunday = Date.now() >= Date.parse('2026-09-27T00:00:00-07:00');
    $('lead-link').hidden = !sunday || presenting || location.hash === '#guide';
    $('guide-link').hidden = !sunday;
  }
  function route(initial = false) {
    const parts = location.hash.slice(1).split('/');
    presenting = parts[0] === 'discuss';
    const guide = parts[0] === 'guide';
    pauseDeadline = null;
    $('study-view').hidden = presenting || guide;
    $('discuss/opening').hidden = !presenting;
    $('guide').hidden = !guide;
    $('site-footer').hidden = presenting;
    $('study-link').hidden = !presenting && !guide;
    document.body.classList.toggle('is-presenting', presenting);
    updateAvailability();
    if (presenting) {
      if (Object.hasOwn(paths,parts[1])) { selectedPath = parts[1]; currentStep = stepsFor().includes(parts[2]) ? parts[2] : 'read-1'; }
      else currentStep = stepsFor().includes(parts[1]) ? parts[1] : 'opening';
      renderPresentation(); focusTitle('slide-title');
      $('announcement').textContent = `Discussion ${stepsFor().indexOf(currentStep)+1} of ${stepsFor().length}: ${currentStep.startsWith('read-') ? paths[selectedPath].reference : $('slide-title').textContent}`;
    } else if (guide) { renderGuide(); focusTitle('guide-title'); }
    else if (parts[0] === 'study' && Object.hasOwn(paths,parts[1])) {
      const passage = $('passage-'+parts[1]); passage.open = true;
      requestAnimationFrame(() => { passage.scrollIntoView({block:'start'}); passage.querySelector('summary').focus({preventScroll:true}); });
    } else if (!initial) focusTitle('main');
  }
  window.addEventListener('hashchange', () => route());
  window.addEventListener('pageshow', () => { updateAvailability(); updateClock(); });
  document.addEventListener('visibilitychange', () => { updateAvailability(); updateClock(); });
  document.addEventListener('fullscreenchange', () => { if ($('fullscreen')) $('fullscreen').textContent = document.fullscreenElement ? 'Exit fullscreen' : 'Fullscreen'; });
  document.addEventListener('keydown', event => {
    if (!presenting || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || event.target.closest('input,textarea,select,button,a,summary,[contenteditable="true"]')) return;
    const steps = stepsFor(), index = steps.indexOf(currentStep);
    if (event.key === 'ArrowRight' && index < steps.length-1) { event.preventDefault(); openDiscussion(steps[index+1]); }
    if (event.key === 'ArrowLeft' && index > 0) { event.preventDefault(); openDiscussion(steps[index-1]); }
    if (event.key === 'Home') { event.preventDefault(); openDiscussion('opening'); }
    if (event.key === 'End') { event.preventDefault(); openDiscussion('closing'); }
    if (event.key.toLowerCase() === 'f') { event.preventDefault(); $('fullscreen').click(); }
  });
  renderStudy(); route(true);
  setInterval(updateClock, 250);
  setInterval(updateAvailability, 30000);
})();
