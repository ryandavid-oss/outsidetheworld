(() => {
  'use strict';
  const DISCUSSION_OPENS_AT = Date.parse('2026-09-13T00:00:00-07:00'); // Midnight in Arizona.
  const OFFICIAL = 'https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-old-testament-2026/37?lang=eng';
  const GONG = 'https://www.churchofjesuschrist.org/study/general-conference/2021/10/51gong?lang=eng';
  const scriptureURL = (book, chapter, verses) => `https://www.churchofjesuschrist.org/study/scriptures/ot/${book}/${chapter}?lang=eng&id=${verses}#${verses.split('-')[0]}`;
  const readingSummaries = [
    {
      book: 'Proverbs', code: 'prov', chapters: [1, 2, 3, 4], title: 'Learning to live wisely',
      text: 'These chapters sound like a parent teaching a child how to live. Listen, keep learning, and refuse invitations to hurt others. Seek wisdom as carefully as you would search for something valuable. Trust God with your decisions, welcome correction, and treat people honestly and generously. Pay attention to what you let into your heart and where your choices are taking you. Wisdom grows as you put it into practice.'
    },
    {
      book: 'Proverbs', code: 'prov', chapters: [15, 16], title: 'Words, anger, and humility',
      text: 'The way we speak can calm a conflict or make it worse. Wise people listen to correction, think before answering, and learn to govern their anger. Pride can lead us into trouble, even when we feel certain we are right. Bring your plans to God and be willing to have them directed. Honesty, humility, and self-control are worth more than wealth or power.'
    },
    {
      book: 'Proverbs', code: 'prov', chapters: [22], title: 'Character in everyday life',
      text: 'A good reputation matters more than riches. Rich and poor alike belong to God. Teach children, share with people in need, and never use someone’s poverty to take advantage of them. Notice how angry companions can shape your own behavior. Be careful about debts and commitments, respect what belongs to others, and take your work seriously.'
    },
    {
      book: 'Proverbs', code: 'prov', chapters: [31], title: 'Strength that blesses others',
      text: 'A mother counsels a king to use good judgment and speak up for people who cannot defend themselves. The chapter then praises a capable woman who works, plans, provides, helps the poor, and speaks with wisdom and kindness. Her family and community benefit from her strength. Her reverence for God and the good she does deserve lasting praise.'
    },
    {
      book: 'Ecclesiastes', code: 'eccl', chapters: [1, 2, 3], title: 'When life refuses to add up',
      text: 'The writer looks at life’s repeating patterns and asks what all our effort amounts to. He tries pleasure, wealth, achievement, and learning, but none lets him escape loss or death. Wisdom is valuable, yet it can bring painful awareness. Life includes seasons of grief and joy, holding on and letting go. We cannot see everything God is doing. We can still do good and enjoy food, work, and ordinary life as His gifts.'
    },
    {
      book: 'Ecclesiastes', code: 'eccl', chapters: [11, 12], title: 'Live faithfully with the time you have',
      text: 'Keep planting and working even when you cannot predict the outcome. Waiting for perfect conditions can keep you from doing anything at all. Enjoy the life you have, and remember that your choices matter to God. Turn to your Creator while you are young, before the difficulties of aging come. The book closes by calling us to revere God and keep His commandments, knowing that He will judge our actions.'
    }
  ];
  const passages = {
    wisdom: { title: 'Proverbs 2:2, 6', url: scriptureURL('prov', 2, 'p2-p6'), verses: [
      ['2', 'So that thou incline thine ear unto wisdom, and apply thine heart to understanding;'],
      ['6', 'For the Lord giveth wisdom: out of his mouth cometh knowledge and understanding.']
    ] },
    anger: { title: 'Proverbs 15:1, 18', url: scriptureURL('prov', 15, 'p1-p18'), verses: [
      ['1', 'A soft answer turneth away wrath: but grievous words stir up anger.'],
      ['18', 'A wrathful man stirreth up strife: but he that is slow to anger appeaseth strife.']
    ] },
    trust: { title: 'Proverbs 3:5–6', url: scriptureURL('prov', 3, 'p5-p6'), verses: [
      ['5', 'Trust in the Lord with all thine heart; and lean not unto thine own understanding.'],
      ['6', 'In all thy ways acknowledge him, and he shall direct thy paths.']
    ] },
    grief: { title: 'Ecclesiastes 1:17–18', url: scriptureURL('eccl', 1, 'p17-p18'), verses: [
      ['17', 'And I gave my heart to know wisdom, and to know madness and folly: I perceived that this also is vexation of spirit.'],
      ['18', 'For in much wisdom is much grief: and he that increaseth knowledge increaseth sorrow.']
    ] },
    humility: { title: 'Proverbs 15:31–33', url: scriptureURL('prov', 15, 'p31-p33'), verses: [
      ['31', 'The ear that heareth the reproof of life abideth among the wise.'],
      ['32', 'He that refuseth instruction despiseth his own soul: but he that heareth reproof getteth understanding.'],
      ['33', 'The fear of the Lord is the instruction of wisdom; and before honour is humility.']
    ] },
    discern: { title: 'Proverbs 3:7', url: scriptureURL('prov', 3, 'p7'), verses: [
      ['7', 'Be not wise in thine own eyes: fear the Lord, and depart from evil.']
    ] }
  };
  const scenarios = [
    {
      id: 'weary', title: 'When you don’t want to hear it', short: 'Worn out', subtitle: 'You know the words. Today they’re hard to hear.',
      situation: 'It’s been a long week. Someone offers a familiar piece of spiritual advice. You believe the words, but today they feel like one more thing you’re failing to do. You stop listening.',
      notice: 'What might this person need before they can hear the advice?', cues: ['A little understanding', 'Room to breathe', 'Help with the load'],
      passage: 'wisdom', reading: 'What do these verses ask of us? Where does wisdom come from?',
      questions: ['How do you turn to God on a day when you have very little to give?', 'How would you offer counsel to someone who is worn out?', 'What helps you hear the Savior when everything feels like another demand?'],
      christ: 'How would Jesus Christ receive this person? What could we learn from Him?',
      invitation: 'What would help you turn toward God this week?',
      carry: 'A phrase I could return to when I feel worn out is…',
      teacher: 'Let people describe what exhaustion can feel like. Ask what they notice in the passage before offering an explanation. Receiving care can be part of a thoughtful next step.'
    },
    {
      id: 'anger', title: 'When anger feels good', short: 'Anger', subtitle: 'The reply is written. Do you send it?',
      situation: 'A message lands badly. You type the reply you’ve been holding back for months. It is sharp, accurate, and satisfying. Your thumb hovers over Send.',
      notice: 'What makes sending that reply so appealing?', cues: ['Finally being heard', 'Defending someone', 'Having the last word'],
      passage: 'anger', reading: 'What difference do our words make in these verses?',
      questions: ['What could a soft answer sound like when the problem still needs to be addressed?', 'How can you recognize the moment anger starts choosing your words for you?', 'What would you want to be true of this relationship after the conversation?'],
      christ: 'The official lesson invites us to consider the Savior’s responses in Mark 12:13–17 and John 8:1–11. What do you notice about His words and His purpose?',
      extra: { title: 'See the Savior’s example: John 8:1–11', url: 'https://www.churchofjesuschrist.org/study/scriptures/nt/john/8?lang=eng&id=p1-p11#p1' },
      invitation: 'Before one difficult reply this week, pause and pray. Try writing a response that is both truthful and gentle.',
      carry: 'A sentence I could use before the conversation gets heated is…',
      teacher: 'Invite the group to compose an actual first sentence. Let several versions stand. A gentle response can still name a problem and set a boundary.'
    },
    {
      id: 'trust', title: 'When trusting felt like it failed', short: 'Disappointment', subtitle: 'You tried to do right. Things still went wrong.',
      situation: 'You prayed, sought counsel, and took the step you believed was right. Things still went badly. Now someone says, “Just trust,” and you wonder what that is supposed to mean.',
      notice: 'What would you want someone to understand before offering reassurance?', cues: ['The loss is real', 'The effort was sincere', 'There are still questions'],
      passage: 'trust', companion: 'grief', reading: 'Read Proverbs, then Ecclesiastes. How do these passages speak to someone who feels let down?',
      questions: ['What might trusting God look like while disappointment is still unresolved?', 'What does this passage actually promise, and what outcome might we have assumed it promised?', 'How can we stay close to someone whose questions are still open?'],
      christ: 'What would you want to say to Jesus Christ about the disappointment?',
      invitation: 'Take a question to God in prayer. Read the passage again or spend time with “Trust Again.” What do you feel prompted to do?',
      carry: 'A question I want to keep studying is…',
      teacher: 'Acknowledge the loss before discussing what could be learned. Do not ask the room to explain why a particular person suffered. Someone can participate without sharing their own experience.'
    },
    {
      id: 'stumble', title: 'When the wise person stumbles', short: 'Discernment', subtitle: 'What can you still trust?',
      situation: 'Someone whose counsel helped you makes a choice that harms others. You feel let down. You begin wondering which parts of what they taught you can still be trusted.',
      notice: 'What would you need to consider before deciding what to trust?', cues: ['The counsel itself', 'The harm and accountability', 'Their response to correction'],
      passage: 'humility', companion: 'discern', reading: 'What do these verses connect with wisdom? How would we recognize those qualities in someone?',
      questions: ['How can we remain teachable while becoming more discerning about whom we trust?', 'What does a person’s response to correction help us understand?', 'How could we examine the counsel honestly while taking the harm seriously?'],
      christ: 'How can faith in Jesus Christ help us respond when someone we respect lets us down?',
      invitation: 'Take one piece of counsel back to the scriptures and to prayer. What holds up? What needs more thought or help?',
      carry: 'A quality I want to look for, and practice myself, is…',
      teacher: 'Keep the situation hypothetical; do not invite naming people or recounting someone else’s wrongdoing. Allow accountability to matter. Restoring trust in a person calls for discernment.'
    }
  ];
  const byId = Object.fromEntries(scenarios.map(s => [s.id, s]));
  const steps = ['Notice', 'Read', 'Reflect', 'Live'];
  const $ = id => document.getElementById(id);
  const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const external = (url, text, cls = '') => `<a class="${cls}" href="${escape(url)}" target="_blank" rel="noopener noreferrer">${text} <span aria-hidden="true">↗</span></a>`;
  let mode = 'home', currentScenario = scenarios[0], studyStep = 0, selected = ['anger', 'trust'], minutes = 25, slide = 'opening', questionIndex = 0;
  let clockHandle = null, clockEnd = 0, clockRemaining = 0, readerReturn = null, guideReturn = null;
  function passageHTML(id, compact = false) {
    const p = passages[id];
    return `<div class="passage${compact ? ' compact' : ''}"><div class="passage-top"><span class="eyebrow">READ THE SCRIPTURES</span>${external(p.url, p.title, 'passage-reference')}</div><blockquote>${p.verses.map(([n, text]) => `<p><sup>${n}</sup>${escape(text)}</p>`).join('')}</blockquote><p class="verse-credit">King James Version · Selected verses · ${external(p.url, 'Read in context')}</p></div>`;
  }
  function makeHash() {
    if (mode === 'study') return `#study/${currentScenario.id}/${studyStep}`;
    if (mode === 'discuss') return `#discuss/${slide}?paths=${selected.join(',')}&minutes=${minutes}`;
    return '#welcome';
  }
  function setHash(replace = false) { try { history[replace ? 'replaceState' : 'pushState'](null, '', makeHash()); } catch { /* Navigation works without history. */ } }
  function focusHeading(id) { window.scrollTo({top: 0, behavior: 'instant'}); $(id)?.focus({preventScroll: true}); }
  function updateDiscussionButton() { $('mode-toggle').hidden = mode !== 'discuss' && Date.now() < DISCUSSION_OPENS_AT; }
  function scheduleDiscussionButton() {
    updateDiscussionButton();
    const remaining = DISCUSSION_OPENS_AT - Date.now();
    if (remaining > 0) setTimeout(scheduleDiscussionButton, Math.min(remaining, 2147483647));
  }
  function visibility() {
    $('welcome').hidden = mode !== 'home'; $('study').hidden = mode !== 'study'; $('presentation').hidden = mode !== 'discuss'; $('resources').hidden = mode !== 'home';
    document.body.classList.toggle('discuss-mode', mode === 'discuss');
    $('mode-toggle').innerHTML = mode === 'discuss' ? 'Return to personal study' : 'Lead the discussion <span aria-hidden="true">↗</span>';
    updateDiscussionButton();
  }
  function stopClock() { if (clockHandle !== null) clearInterval(clockHandle); clockHandle = null; clockEnd = 0; clockRemaining = 0; }
  function closeDialogs() { for (const id of ['leader-guide', 'scripture-reader']) if ($(id).open) $(id).close(); }
  function home(push = true) { stopClock(); closeDialogs(); mode = 'home'; visibility(); if (push) setHash(); focusHeading('welcome-title'); }
  function openStudy(id, step = 0, push = true) {
    stopClock(); closeDialogs(); mode = 'study'; currentScenario = Object.hasOwn(byId, id) ? byId[id] : scenarios[0];
    studyStep = Number.isInteger(step) && step >= 0 && step <= 3 ? step : 0;
    questionIndex = 0; visibility(); renderStudy(); if (push) setHash(); focusHeading('study-title');
  }
  function renderStudy() {
    const s = currentScenario;
    let content = '';
    if (studyStep === 0) content = `<p class="eyebrow">PICTURE THIS</p><p class="situation">${escape(s.situation)}</p><div class="reflection-prompt"><span class="eyebrow">PAUSE HERE</span><h3>${escape(s.notice)}</h3><details><summary>A few places to begin</summary><ul class="starting-points">${s.cues.map(c => `<li>${escape(c)}</li>`).join('')}</ul></details></div>`;
    if (studyStep === 1) content = `<p class="reading-invitation">${escape(s.reading)}</p>${passageHTML(s.passage)}${s.companion ? `<details class="companion"><summary>Read alongside ${passages[s.companion].title}</summary>${passageHTML(s.companion)}</details>` : ''}<div class="christ-connection"><span class="eyebrow">CONSIDER THE SAVIOR</span><p>${escape(s.christ)}</p>${s.extra ? external(s.extra.url, s.extra.title) : ''}</div>${['trust','stumble'].includes(s.id) ? `<details class="companion"><summary>Continue with “Trust Again”</summary><p class="quiet">Elder Gerrit W. Gong · Linked in this week’s lesson</p>${external(GONG, 'Read the full talk')}</details>` : ''}`;
    if (studyStep === 2) content = `<p class="eyebrow">THINK IT THROUGH</p><h3 class="main-question" id="study-question">${escape(s.questions[0])}</h3><p class="question-counter" id="study-question-count">Question 1 of ${s.questions.length}</p><button type="button" class="text-button" data-action="another-study">Try another question ↻</button><div class="reflection-prompt"><h3>Which words in the passage shape your answer?</h3><p>Think it over, talk with someone, or write in your journal.</p><button class="button secondary" type="button" data-read="${s.passage}">Return to the passage</button></div>`;
    if (studyStep === 3) content = `<p class="eyebrow">THIS WEEK</p><h3 class="main-question">What will you carry into the week?</h3><p class="invitation">${escape(s.invitation)}</p><div class="carry-card"><p class="eyebrow">FINISH THE THOUGHT</p><p>${escape(s.carry)}</p></div><p>This is the kind of stuff we can discuss on Sunday</p><div class="study-end-links">${external(OFFICIAL, 'Continue the official study', 'text-button')}<button type="button" class="text-button" data-action="home">Explore another moment →</button></div>`;
    $('study').innerHTML = `<div class="study-top"><button type="button" class="text-button" data-action="home">← All four moments</button><button type="button" class="text-button" data-action="share">Share this path ↗</button></div><div class="study-layout"><aside class="study-heading"><p class="eyebrow">${String(scenarios.indexOf(s) + 1).padStart(2,'0')} / FOUR FAMILIAR MOMENTS</p><h2 id="study-title" tabindex="-1">${escape(s.title)}</h2><nav class="step-nav" aria-label="Study steps">${steps.map((label, i) => `<button type="button" data-step="${i}"${i === studyStep ? ' aria-current="step"' : ''}><span>${i + 1}</span>${label}</button>`).join('')}</nav></aside><div class="study-content">${content}<nav class="study-navigation" aria-label="Continue studying"><button type="button" class="button secondary" data-action="study-back">${studyStep === 0 ? 'All moments' : '← ' + steps[studyStep - 1]}</button><span class="quiet">${studyStep + 1} of 4</span><button type="button" class="button" data-action="study-next">${studyStep === 3 ? 'All moments' : steps[studyStep + 1] + ' →'}</button></nav><p class="local-status" id="share-status" role="status"></p></div></div>`;
  }
  function slideOrder() { return ['opening', ...selected.flatMap(id => [`${id}-notice`, `${id}-read`, `${id}-reflect`]), 'closing']; }
  function startDiscussion(target = 'opening', push = true) {
    stopClock(); closeDialogs(); mode = 'discuss'; questionIndex = 0;
    slide = slideOrder().includes(target) ? target : 'opening'; visibility(); renderDiscussion(); if (push) setHash(); focusHeading('slide-title');
  }
  function renderDiscussion() {
    const order = slideOrder(), index = order.indexOf(slide), [id, phase] = slide.split('-'), s = byId[id];
    let body = '';
    if (slide === 'opening') body = `<div class="discussion-opening"><div><p class="eyebrow">AS WE GATHER · PROVERBS &amp; ECCLESIASTES</p><h2 class="opening-title" id="slide-title" tabindex="-1">Wisdom for<br>the <em>hard days.</em></h2><p class="opening-class-question">What did you learn this week about the Savior?</p><p class="slide-gentle">You’re welcome to share, or just listen.</p><details class="opening-context"><summary>From this week’s Come, Follow Me</summary><blockquote>Life is always better—if not always perfect—when we trust and follow the Lord Jesus Christ.</blockquote>${external(OFFICIAL, 'Open the official lesson')}</details></div><img class="discussion-art" src="media/cfm913/savior-with-children.jpg" srcset="media/cfm913/savior-with-children-800.jpg 800w, media/cfm913/savior-with-children.jpg 1600w" sizes="(max-width: 900px) calc(100vw - 48px), 45vw" width="1600" height="900" alt="Painting of Jesus Christ sitting with children, reaching toward a child with a bowed head."></div>`;
    else if (slide === 'closing') body = `<p class="eyebrow">CARRY IT INTO THE WEEK</p><h2 class="opening-title closing-question" id="slide-title" tabindex="-1">What will you do this week to follow <em>Jesus Christ</em>?</h2>${external(OFFICIAL, 'Continue the official Come, Follow Me study', 'class-source')}`;
    else if (phase === 'notice') body = `<p class="eyebrow">${escape(s.title)} · NOTICE</p><h2 class="scenario-situation" id="slide-title" tabindex="-1">${escape(s.situation)}</h2><p class="discussion-question">${escape(s.notice)}</p><details class="opening-context"><summary>A few places to begin</summary><p>${s.cues.map(escape).join(' · ')}</p></details>`;
    else if (phase === 'read') body = `<p class="eyebrow">${escape(s.title)} · READ TOGETHER</p><h2 class="reading-title" id="slide-title" tabindex="-1">${passages[s.passage].title}</h2>${passageHTML(s.passage, true)}<p class="reading-class-question">Which word or phrase stands out to you?</p>${s.companion ? `<button type="button" class="class-source" data-read="${s.companion}">Read alongside ${passages[s.companion].title} ↗</button>` : ''}`;
    else body = `<p class="eyebrow">${escape(s.title)} · REFLECT TOGETHER</p><h2 class="discussion-big-question" id="slide-title" tabindex="-1">${escape(s.questions[questionIndex])}</h2><div class="class-question-actions"><button type="button" class="button discussion-action" data-action="another-class">Another question ↻</button><button type="button" class="class-source" data-read="${s.passage}">Return to the passage ↗</button><button type="button" class="button discussion-action" data-action="christ">Consider the Savior ↗</button></div>`;
    $('presentation').innerHTML = `<div class="class-toolbar"><button type="button" class="class-source" data-action="guide">Shape the discussion</button><span class="class-plan">${selected.length} ${selected.length === 1 ? 'moment' : 'moments'} · ${minutes}-minute suggested plan</span><button type="button" class="class-source" data-action="fullscreen" id="fullscreen-button"${!document.documentElement.requestFullscreen ? ' hidden' : ''}>${document.fullscreenElement ? 'Exit fullscreen' : 'Fullscreen'}</button></div><div class="class-stage" id="class-stage">${body}</div><nav class="class-navigation" aria-label="Discussion navigation"><button type="button" class="button secondary" data-action="class-back"${index === 0 ? ' disabled' : ''}>← Back</button><div class="class-middle"><label class="sr-only" for="slide-jump">Jump to a discussion moment</label><select id="slide-jump">${order.map((item,i) => `<option value="${item}"${item === slide ? ' selected' : ''}>${i + 1}. ${slideLabel(item)}</option>`).join('')}</select><div class="quiet-clock"><button type="button" class="class-source" data-action="pause" id="pause-button">Quiet moment · 30 seconds</button><span id="quiet-clock-display" aria-live="off"></span><button type="button" class="class-source" data-action="reset-clock" id="reset-clock" hidden>Reset</button></div></div><button type="button" class="button" data-action="class-next">${index === order.length - 1 ? 'Back to opening' : 'Continue →'}</button></nav>`;
  }
  function slideLabel(item) {
    if (item === 'opening') return 'Gather'; if (item === 'closing') return 'A next step';
    const [id, phase] = item.split('-'); return `${byId[id].short} · ${phase === 'notice' ? 'Situation' : phase === 'read' ? 'Scripture' : 'Discussion'}`;
  }
  function moveSlide(direction) {
    const order = slideOrder(), index = order.indexOf(slide);
    startDiscussion(order[direction > 0 && index === order.length - 1 ? 0 : Math.max(0, index + direction)]);
  }
  function showReader(title, content) {
    readerReturn = document.activeElement;
    $('scripture-reader').innerHTML = `<div class="dialog-top"><h2 id="reader-title">${escape(title)}</h2><button type="button" class="button secondary small" data-close="scripture-reader">Close</button></div>${content}`;
    $('scripture-reader').showModal();
  }
  function showReadingSummary() {
    const sections = readingSummaries.map(s => {
      const range = s.chapters.length === 1 ? String(s.chapters[0]) : `${s.chapters[0]}–${s.chapters.at(-1)}`;
      const chapterLinks = s.chapters.map(chapter => external(`https://www.churchofjesuschrist.org/study/scriptures/ot/${s.code}/${chapter}?lang=eng`, `${s.book} ${chapter}`)).join('');
      return `<section class="chapter-summary"><p class="eyebrow">${s.book} ${range}</p><h3>${s.title}</h3><p>${s.text}</p><div class="chapter-links" aria-label="Read the scripture text">${chapterLinks}</div></section>`;
    }).join('');
    showReader('The readings in plain language', `<p class="summary-intro">Summaries of this week’s readings. Each section links to the scripture text.</p><div class="chapter-summaries">${sections}</div><div class="summary-source">${external(OFFICIAL, 'This week’s Come, Follow Me lesson')}<button type="button" class="button secondary small" data-close="scripture-reader">Back to the lesson</button></div>`);
    $('scripture-reader').scrollTop = 0;
  }
  function planText(count, length) {
    if (!count) return 'Choose at least one moment to build a plan.';
    const gather = length === 15 ? 2 : 3, close = 3, available = length - gather - close, each = Math.floor(available / count), spare = available % count;
    return `${gather} min to gather · about ${each}${spare ? '–' + (each + 1) : ''} min per moment · ${close} min for a next step.`;
  }
  function showGuide() {
    guideReturn = document.activeElement; const s = byId[slide.split('-')[0]];
    $('leader-guide').innerHTML = `<div class="dialog-top"><div><p class="eyebrow">FOR THE DISCUSSION LEADER</p><h2 id="guide-title">Plan the discussion</h2></div><button type="button" class="button secondary small" data-close="leader-guide">Close</button></div><p>Choose the scenarios and the time you have.</p><form id="guide-form"><fieldset><legend>Moments to include</legend><p class="quiet">Start with one or two.</p>${scenarios.map(s => `<label class="scenario-check"><input type="checkbox" name="paths" value="${s.id}"${selected.includes(s.id) ? ' checked' : ''}><span>${escape(s.title)}</span></label>`).join('')}</fieldset><label class="duration-label" for="plan-minutes">Time available<select id="plan-minutes" name="minutes">${[15,25,40].map(m => `<option value="${m}"${m === minutes ? ' selected' : ''}>${m} minutes</option>`).join('')}</select></label><p class="plan-rundown" id="plan-rundown">${planText(selected.length, minutes)}</p><p id="guide-error" role="alert"></p><button class="button" type="submit">Use this plan</button></form><div class="leader-notes"><h3>${s ? 'For this moment' : 'Getting started'}</h3><p>${escape(s ? s.teacher : 'Invite a verse or thought from home study. Give everyone a few quiet seconds before taking responses. People may speak about the hypothetical situation without sharing their own story.')}</p><details><summary>If the room goes quiet</summary><ol><li>Wait long enough for a thought to form.</li><li>Ask: “Which word in the passage caught your attention?”</li><li>Offer a short conversation with a neighbor.</li><li>Ask for one observation.</li></ol></details><details><summary>Keep it connected to Come, Follow Me</summary><p>Return to the scriptures and this week’s official study as the discussion develops.</p>${external('https://www.churchofjesuschrist.org/study/manual/teaching-in-the-saviors-way-2022/07-part-2/11-invite-diligent-learning?lang=eng', 'Teaching in the Savior’s Way: Invite Diligent Learning')}</details><p class="quiet">Arrow keys move between screens. Home returns to the opening. Notes are visible to the room when opened.</p></div>`;
    $('leader-guide').showModal();
  }
  function paintClock() {
    if (!$('quiet-clock-display')) return;
    const remaining = clockEnd ? Math.max(0, Math.ceil((clockEnd - Date.now()) / 1000)) : clockRemaining;
    $('quiet-clock-display').textContent = remaining ? `0:${String(remaining).padStart(2, '0')}` : 'Take the time you need.';
    if (clockEnd && !remaining) { stopClock(); $('pause-button').textContent = 'Another quiet moment'; $('announcement').textContent = 'Thirty seconds have passed. Continue when the group is ready.'; }
  }
  function toggleClock() {
    if (clockHandle !== null) {
      clockRemaining = Math.max(0, Math.ceil((clockEnd - Date.now()) / 1000)); clearInterval(clockHandle); clockHandle = null; clockEnd = 0;
      $('pause-button').textContent = 'Resume quiet moment'; paintClock(); return;
    }
    clockEnd = Date.now() + (clockRemaining || 30) * 1000; clockRemaining = 0;
    $('pause-button').textContent = 'Pause quiet moment'; $('reset-clock').hidden = false; clockHandle = setInterval(paintClock, 250); paintClock();
  }
  async function sharePath() {
    const url = new URL(location.href); url.hash = `study/${currentScenario.id}/0`; const status = $('share-status');
    try {
      if (navigator.share) await navigator.share({title: currentScenario.title, text: 'Wisdom for the Hard Days · A Come, Follow Me companion', url: url.href});
      else if (navigator.clipboard?.writeText) { await navigator.clipboard.writeText(url.href); status.textContent = 'Link copied. Share it whenever you’re ready.'; }
      else status.textContent = `Copy this link: ${url.href}`;
    } catch (error) { if (error.name !== 'AbortError') status.textContent = `Copy this link: ${url.href}`; }
  }
  function readRoute(initialLoad = false) {
    const [path, query = ''] = location.hash.slice(1).split('?'), parts = path.split('/');
    if (parts[0] === 'study' && Object.hasOwn(byId, parts[1])) { openStudy(parts[1], Number(parts[2]), false); return; }
    if (parts[0] === 'discuss') {
      const params = new URLSearchParams(query), ids = [...new Set((params.get('paths') || selected.join(',')).split(','))].filter(id => Object.hasOwn(byId, id));
      selected = ids.length ? ids : ['anger', 'trust']; const requestedMinutes = Number(params.get('minutes'));
      if ([15,25,40].includes(requestedMinutes)) minutes = requestedMinutes;
      startDiscussion(parts[1], false); return;
    }
    if (initialLoad === true) { mode = 'home'; visibility(); }
    else home(false);
  }
  $('scenario-list').innerHTML = scenarios.map((s, i) => `<button type="button" class="scenario-card" data-scenario="${s.id}"><span class="scenario-number">0${i + 1}</span><span><strong>${escape(s.title)}</strong><small>${escape(s.subtitle)}</small></span><span class="scenario-arrow" aria-hidden="true">↗</span></button>`).join('');
  $('mode-toggle').addEventListener('click', () => mode === 'discuss' ? home() : startDiscussion());
  document.addEventListener('click', event => {
    const button = event.target.closest('button'); if (!button || button.disabled) return;
    if (button.dataset.scenario) return openStudy(button.dataset.scenario);
    if (button.dataset.step !== undefined) return openStudy(currentScenario.id, Number(button.dataset.step));
    if (button.dataset.read && Object.hasOwn(passages, button.dataset.read)) return showReader(passages[button.dataset.read].title, passageHTML(button.dataset.read));
    if (button.dataset.close) return $(button.dataset.close)?.close();
    switch (button.dataset.action) {
      case 'reading-summary': return showReadingSummary();
      case 'home': return home();
      case 'study-back': return studyStep === 0 ? home() : openStudy(currentScenario.id, studyStep - 1);
      case 'study-next': return studyStep === 3 ? home() : openStudy(currentScenario.id, studyStep + 1);
      case 'another-study': questionIndex = (questionIndex + 1) % currentScenario.questions.length; $('study-question').textContent = currentScenario.questions[questionIndex]; $('study-question-count').textContent = `Question ${questionIndex + 1} of ${currentScenario.questions.length}`; $('announcement').textContent = currentScenario.questions[questionIndex]; return;
      case 'class-back': return moveSlide(-1);
      case 'class-next': return moveSlide(1);
      case 'another-class': { const s = byId[slide.split('-')[0]]; questionIndex = (questionIndex + 1) % s.questions.length; $('slide-title').textContent = s.questions[questionIndex]; $('announcement').textContent = s.questions[questionIndex]; return; }
      case 'christ': { const s = byId[slide.split('-')[0]]; return showReader('Look toward Jesus Christ', `<p class="christ-dialog-question">${escape(s.christ)}</p>${s.extra ? external(s.extra.url, s.extra.title) : ''}`); }
      case 'guide': return showGuide();
      case 'pause': return toggleClock();
      case 'reset-clock': stopClock(); $('quiet-clock-display').textContent = ''; $('pause-button').textContent = 'Quiet moment · 30 seconds'; $('reset-clock').hidden = true; return;
      case 'share': return void sharePath();
      case 'fullscreen': { const action = document.fullscreenElement ? document.exitFullscreen?.() : document.documentElement.requestFullscreen?.(); if (action?.catch) action.catch(() => { $('announcement').textContent = 'Fullscreen is unavailable here. The discussion view remains ready to use.'; }); return; }
    }
  });
  document.addEventListener('change', event => {
    if (event.target.id === 'slide-jump') startDiscussion(event.target.value);
    if (event.target.closest('#guide-form')) { const count = $('guide-form').querySelectorAll('input[name="paths"]:checked').length; $('plan-rundown').textContent = planText(count, Number($('plan-minutes').value)); }
  });
  document.addEventListener('submit', event => {
    if (event.target.id !== 'guide-form') return; event.preventDefault();
    const values = [...event.target.querySelectorAll('input[name="paths"]:checked')].map(input => input.value).filter(id => Object.hasOwn(byId, id));
    if (!values.length) { $('guide-error').textContent = 'Choose at least one moment.'; return; }
    selected = values; const requested = Number($('plan-minutes').value); minutes = [15,25,40].includes(requested) ? requested : 25;
    startDiscussion(slideOrder().includes(slide) ? slide : 'opening');
  });
  document.addEventListener('keydown', event => {
    if (mode !== 'discuss' || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || document.querySelector('dialog[open]') || event.target.closest('input, textarea, select, button, a, summary, [contenteditable="true"]')) return;
    if (['ArrowRight','PageDown','ArrowLeft','PageUp','Home','End'].includes(event.key)) {
      event.preventDefault(); if (event.key === 'Home') startDiscussion(); else if (event.key === 'End') startDiscussion('closing'); else moveSlide(['ArrowRight','PageDown'].includes(event.key) ? 1 : -1);
    }
  });
  document.addEventListener('fullscreenchange', () => { const button = $('fullscreen-button'); if (button) button.textContent = document.fullscreenElement ? 'Exit fullscreen' : 'Fullscreen'; });
  $('scripture-reader').addEventListener('close', () => { if (readerReturn?.isConnected) readerReturn.focus({preventScroll:true}); });
  $('leader-guide').addEventListener('close', () => { if (guideReturn?.isConnected) guideReturn.focus({preventScroll:true}); });
  window.addEventListener('pageshow', updateDiscussionButton); document.addEventListener('visibilitychange', updateDiscussionButton);
  window.addEventListener('popstate', readRoute); window.addEventListener('hashchange', readRoute); readRoute(true); scheduleDiscussionButton();
})();
