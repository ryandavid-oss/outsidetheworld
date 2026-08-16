(function () {
  "use strict";

  const churchBase = "https://www.churchofjesuschrist.org/study/scriptures/";
  const lessonUrl = "https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-old-testament-2026/33?lang=eng";

  function scripture(reference, url, verses, note) {
    return { reference: reference, url: url, verses: verses, note: note || "" };
  }

  const passages = {
    job1_1: scripture("Job 1:1", churchBase + "ot/job/1?id=p1&lang=eng#p1", [
      ["1", "There was a man in the land of Uz, whose name was Job; and that man was perfect and upright, and one that feared God, and eschewed evil."]
    ]),
    job1_9_11: scripture("Job 1:9–11", churchBase + "ot/job/1?id=p9-p11&lang=eng#p9", [
      ["9", "Then Satan answered the Lord, and said, Doth Job fear God for nought?"],
      ["10", "Hast not thou made an hedge about him, and about his house, and about all that he hath on every side? thou hast blessed the work of his hands, and his substance is increased in the land."],
      ["11", "But put forth thine hand now, and touch all that he hath, and he will curse thee to thy face."]
    ]),
    job1_20: scripture("Job 1:20", churchBase + "ot/job/1?id=p20&lang=eng#p20", [
      ["20", "Then Job arose, and rent his mantle, and shaved his head, and fell down upon the ground, and worshipped,"]
    ]),
    job1_21: scripture("Job 1:21", churchBase + "ot/job/1?id=p21&lang=eng#p21", [
      ["21", "And said, Naked came I out of my mother’s womb, and naked shall I return thither: the Lord gave, and the Lord hath taken away; blessed be the name of the Lord."]
    ]),
    job2_3: scripture("Job 2:3", churchBase + "ot/job/2?id=p3&lang=eng#p3", [
      ["3", "And the Lord said unto Satan, Hast thou considered my servant Job, that there is none like him in the earth, a perfect and an upright man, one that feareth God, and escheweth evil? and still he holdeth fast his integrity, although thou movedst me against him, to destroy him without cause."]
    ]),
    job2_7: scripture("Job 2:7", churchBase + "ot/job/2?id=p7&lang=eng#p7", [
      ["7", "So went Satan forth from the presence of the Lord, and smote Job with sore boils from the sole of his foot unto his crown."]
    ]),
    job2_9_10: scripture("Job 2:9–10", churchBase + "ot/job/2?id=p9-p10&lang=eng#p9", [
      ["9", "Then said his wife unto him, Dost thou still retain thine integrity? curse God, and die."],
      ["10", "But he said unto her, Thou speakest as one of the foolish women speaketh. What? shall we receive good at the hand of God, and shall we not receive evil? In all this did not Job sin with his lips."]
    ]),
    job2_13: scripture("Job 2:13", churchBase + "ot/job/2?id=p13&lang=eng#p13", [
      ["13", "So they sat down with him upon the ground seven days and seven nights, and none spake a word unto him: for they saw that his grief was very great."]
    ]),
    job13_15: scripture("Job 13:15", churchBase + "ot/job/13?id=p15&lang=eng#p15", [
      ["15", "Though he slay me, yet will I trust in him: but I will maintain mine own ways before him."]
    ]),
    job14_14: scripture("Job 14:14", churchBase + "ot/job/14?id=p14&lang=eng#p14", [
      ["14", "If a man die, shall he live again? all the days of my appointed time will I wait, till my change come."]
    ]),
    job16_1_5: scripture("Job 16:1–5", churchBase + "ot/job/16?id=p1-p5&lang=eng#p1", [
      ["1", "Then Job answered and said,"],
      ["2", "I have heard many such things: miserable comforters are ye all."],
      ["3", "Shall vain words have an end? or what emboldeneth thee that thou answerest?"],
      ["4", "I also could speak as ye do: if your soul were in my soul’s stead, I could heap up words against you, and shake mine head at you."],
      ["5", "But I would strengthen you with my mouth, and the moving of my lips should assuage your grief."]
    ]),
    job19_25: scripture("Job 19:25", churchBase + "ot/job/19?id=p25&lang=eng#p25", [
      ["25", "For I know that my redeemer liveth, and that he shall stand at the latter day upon the earth:"]
    ]),
    job19_25_27: scripture("Job 19:25–27", churchBase + "ot/job/19?id=p25-p27&lang=eng#p25", [
      ["25", "For I know that my redeemer liveth, and that he shall stand at the latter day upon the earth:"],
      ["26", "And though after my skin worms destroy this body, yet in my flesh shall I see God:"],
      ["27", "Whom I shall see for myself, and mine eyes shall behold, and not another; though my reins be consumed within me."]
    ]),
    job19_26_27: scripture("Job 19:26–27", churchBase + "ot/job/19?id=p26-p27&lang=eng#p26", [
      ["26", "And though after my skin worms destroy this body, yet in my flesh shall I see God:"],
      ["27", "Whom I shall see for myself, and mine eyes shall behold, and not another; though my reins be consumed within me."]
    ]),
    job21_7_9: scripture("Job 21:7–9", churchBase + "ot/job/21?id=p7-p9&lang=eng#p7", [
      ["7", "Wherefore do the wicked live, become old, yea, are mighty in power?"],
      ["8", "Their seed is established in their sight with them, and their offspring before their eyes."],
      ["9", "Their houses are safe from fear, neither is the rod of God upon them."]
    ], "A complete example from the broader debate in Job 21–24."),
    job23_10: scripture("Job 23:10", churchBase + "ot/job/23?id=p10&lang=eng#p10", [
      ["10", "But he knoweth the way that I take: when he hath tried me, I shall come forth as gold."]
    ]),
    job27_5: scripture("Job 27:5", churchBase + "ot/job/27?id=p5&lang=eng#p5", [
      ["5", "God forbid that I should justify you: till I die I will not remove mine integrity from me."]
    ]),
    job38_1_7: scripture("Job 38:1–7", churchBase + "ot/job/38?id=p1-p7&lang=eng#p1", [
      ["1", "Then the Lord answered Job out of the whirlwind, and said,"],
      ["2", "Who is this that darkeneth counsel by words without knowledge?"],
      ["3", "Gird up now thy loins like a man; for I will demand of thee, and answer thou me."],
      ["4", "Where wast thou when I laid the foundations of the earth? declare, if thou hast understanding."],
      ["5", "Who hath laid the measures thereof, if thou knowest? or who hath stretched the line upon it?"],
      ["6", "Whereupon are the foundations thereof fastened? or who laid the corner stone thereof;"],
      ["7", "When the morning stars sang together, and all the sons of God shouted for joy?"]
    ], "A complete lesson-relevant passage from the Lord’s longer response in Job 38–40."),
    job38_4: scripture("Job 38:4", churchBase + "ot/job/38?id=p4&lang=eng#p4", [
      ["4", "Where wast thou when I laid the foundations of the earth? declare, if thou hast understanding."]
    ]),
    job38_31_35: scripture("Job 38:31–35", churchBase + "ot/job/38?id=p31-p35&lang=eng#p31", [
      ["31", "Canst thou bind the sweet influences of Pleiades, or loose the bands of Orion?"],
      ["32", "Canst thou bring forth Mazzaroth in his season? or canst thou guide Arcturus with his sons?"],
      ["33", "Knowest thou the ordinances of heaven? canst thou set the dominion thereof in the earth?"],
      ["34", "Canst thou lift up thy voice to the clouds, that abundance of waters may cover thee?"],
      ["35", "Canst thou send lightnings, that they may go, and say unto thee, Here we are?"]
    ]),
    job39_1_2: scripture("Job 39:1–2", churchBase + "ot/job/39?id=p1-p2&lang=eng#p1", [
      ["1", "Knowest thou the time when the wild goats of the rock bring forth? or canst thou mark when the hinds do calve?"],
      ["2", "Canst thou number the months that they fulfil? or knowest thou the time when they bring forth?"]
    ]),
    job42_2: scripture("Job 42:2", churchBase + "ot/job/42?id=p2&lang=eng#p2", [
      ["2", "I know that thou canst do every thing, and that no thought can be withholden from thee."]
    ]),
    job42_1_6: scripture("Job 42:1–6", churchBase + "ot/job/42?id=p1-p6&lang=eng#p1", [
      ["1", "Then Job answered the Lord, and said,"],
      ["2", "I know that thou canst do every thing, and that no thought can be withholden from thee."],
      ["3", "Who is he that hideth counsel without knowledge? therefore have I uttered that I understood not; things too wonderful for me, which I knew not."],
      ["4", "Hear, I beseech thee, and I will speak: I will demand of thee, and declare thou unto me."],
      ["5", "I have heard of thee by the hearing of the ear: but now mine eye seeth thee."],
      ["6", "Wherefore I abhor myself, and repent in dust and ashes."]
    ]),
    nephi2_11_13: scripture("2 Nephi 2:11–13", churchBase + "bofm/2-ne/2?id=p11-p13&lang=eng#p11", [
      ["11", "For it must needs be, that there is an opposition in all things. If not so, my firstborn in the wilderness, righteousness could not be brought to pass, neither wickedness, neither holiness nor misery, neither good nor bad. Wherefore, all things must needs be a compound in one; wherefore, if it should be one body it must needs remain as dead, having no life neither death, nor corruption nor incorruption, happiness nor misery, neither sense nor insensibility."],
      ["12", "Wherefore, it must needs have been created for a thing of naught; wherefore there would have been no purpose in the end of its creation. Wherefore, this thing must needs destroy the wisdom of God and his eternal purposes, and also the power, and the mercy, and the justice of God."],
      ["13", "And if ye shall say there is no law, ye shall also say there is no sin. If ye shall say there is no sin, ye shall also say there is no righteousness. And if there be no righteousness there be no happiness. And if there be no righteousness nor happiness there be no punishment nor misery. And if these things are not there is no God. And if there is no God we are not, neither the earth; for there could have been no creation of things, neither to act nor to be acted upon; wherefore, all things must have vanished away."]
    ]),
    alma11_42_44: scripture("Alma 11:42–44", churchBase + "bofm/alma/11?id=p42-p44&lang=eng#p42", [
      ["42", "Now, there is a death which is called a temporal death; and the death of Christ shall loose the bands of this temporal death, that all shall be raised from this temporal death."],
      ["43", "The spirit and the body shall be reunited again in its perfect form; both limb and joint shall be restored to its proper frame, even as we now are at this time; and we shall be brought to stand before God, knowing even as we know now, and have a bright recollection of all our guilt."],
      ["44", "Now, this restoration shall come to all, both old and young, both bond and free, both male and female, both the wicked and the righteous; and even there shall not so much as a hair of their heads be lost; but every thing shall be restored to its perfect frame, as it is now, or in the body, and shall be brought and be arraigned before the bar of Christ the Son, and God the Father, and the Holy Spirit, which is one Eternal God, to be judged according to their works, whether they be good or whether they be evil."]
    ]),
    ether12_27: scripture("Ether 12:27", churchBase + "bofm/ether/12?id=p27&lang=eng#p27", [
      ["27", "And if men come unto me I will show unto them their weakness. I give unto men weakness that they may be humble; and my grace is sufficient for all men that humble themselves before me; for if they humble themselves before me, and have faith in me, then will I make weak things become strong unto them."]
    ])
  };

  const categories = [
    {
      title: "Job’s Story",
      clues: [
        { value: 100, question: "Before any trials began, Job was described with four character traits. Name any two.", answer: "He was perfect (or blameless), upright, feared God, and turned away from evil.", passages: [passages.job1_1] },
        { value: 200, question: "After losing his possessions and children, Job fell to the ground. What surprising thing did he do next?", answer: "He worshipped God.", insight: "Sorrow and faith can exist at the same time.", passages: [passages.job1_20] },
        { value: 300, question: "Finish Job’s words: “The Lord gave, and the Lord hath taken away; ______.”", answer: "“Blessed be the name of the Lord.”", passages: [passages.job1_21] },
        { value: 400, question: "What painful physical condition struck Job after his other losses?", answer: "He was covered with sore boils from the sole of his foot to the crown of his head.", passages: [passages.job2_7] },
        { value: 500, question: "For how long did Job’s friends sit silently with him when they saw his grief?", answer: "Seven days and seven nights.", insight: "Being present can be a powerful first step in comforting someone.", passages: [passages.job2_13] }
      ]
    },
    {
      title: "Faith Under Fire",
      clues: [
        { value: 100, question: "According to Satan’s accusation, why was Job faithful to God?", answer: "Satan claimed Job was faithful only because God had protected and blessed him.", passages: [passages.job1_9_11] },
        { value: 200, question: "Complete Job’s declaration of trust: “Though he slay me, ______.”", answer: "“Yet will I trust in him.”", passages: [passages.job13_15] },
        { value: 300, question: "When Job’s wife told him to curse God, what question did Job ask in response?", answer: "“Shall we receive good at the hand of God, and shall we not receive evil?”", insight: "Job did not pretend his suffering was easy; he chose to keep trusting.", passages: [passages.job2_9_10] },
        { value: 400, question: "This week’s lesson teaches that unanswered questions can coexist with what?", answer: "Faith.", insight: "The lesson connects this principle to Job’s continuing declaration of trust.", passages: [passages.job13_15], lessonUrl: lessonUrl },
        { value: 500, question: "What did Job refuse to surrender, even when his faith and motives were questioned?", answer: "His integrity.", passages: [passages.job2_3, passages.job2_9_10, passages.job27_5] }
      ]
    },
    {
      title: "My Redeemer Lives",
      clues: [
        { value: 100, question: "Who declared, “I know that my redeemer liveth”?", answer: "Job.", passages: [passages.job19_25] },
        { value: 200, question: "Who is the Redeemer Job testified of?", answer: "Jesus Christ.", passages: [passages.job19_25_27] },
        { value: 300, question: "According to Job’s testimony, what would he one day see “in [his] flesh”?", answer: "He would see God.", insight: "Job’s words point to resurrection and a living Redeemer.", passages: [passages.job19_26_27] },
        { value: 400, question: "Job asked, “If a man die, shall he live again?” Because of Jesus Christ, what is the answer?", answer: "Yes. Because Jesus Christ was resurrected, we will all live again.", passages: [passages.job14_14, passages.alma11_42_44] },
        { value: 500, question: "What hymn suggested in this week’s lesson echoes Job’s testimony?", answer: "“I Know That My Redeemer Lives” (Hymns, no. 136).", passages: [passages.job19_25] }
      ]
    },
    {
      title: "Through the Trial",
      clues: [
        { value: 100, question: "What question was at the heart of the debate between Job and his friends?", answer: "Why do righteous people sometimes suffer?", passages: [passages.job21_7_9], lessonUrl: lessonUrl },
        { value: 200, question: "Finish Job’s hopeful comparison: “When he hath tried me, I shall come forth as ______.”", answer: "Gold.", passages: [passages.job23_10] },
        { value: 300, question: "Second Nephi teaches that what is necessary “in all things” for God’s plan?", answer: "Opposition.", passages: [passages.nephi2_11_13] },
        { value: 400, question: "In Ether 12:27, what can Christ make strong when we humble ourselves and have faith in Him?", answer: "Our weak things.", passages: [passages.ether12_27] },
        { value: 500, question: "Job’s friends accused him when he was suffering. According to Job, what should good friends do instead?", answer: "Uplift and strengthen with their words.", insight: "A Christlike friend comforts instead of guessing why someone is suffering.", passages: [passages.job16_1_5] }
      ]
    },
    {
      title: "God’s Greater View",
      clues: [
        { value: 100, question: "When God answered Job, did He give a detailed explanation for every trial?", answer: "No. He taught Job to see His wisdom, power, and greater perspective.", passages: [passages.job38_1_7], lessonUrl: lessonUrl },
        { value: 200, question: "What did the Lord ask Job: “Where wast thou when I laid” what?", answer: "“The foundations of the earth.”", passages: [passages.job38_4] },
        { value: 300, question: "The Lord pointed to animals, weather, stars, and the earth to teach Job. What do these examples all have in common?", answer: "They are God’s creations and show His wisdom and power.", passages: [passages.job38_31_35, passages.job39_1_2] },
        { value: 400, question: "After hearing the Lord, Job said, “I know that thou canst do” what?", answer: "“Every thing.”", passages: [passages.job42_2] },
        { value: 500, question: "Complete the central lesson heading: “God’s perspective is ______.”", answer: "“Greater than mine.”", insight: "We may not see the whole picture, but we can trust the One who does.", passages: [passages.job42_1_6], lessonUrl: lessonUrl }
      ]
    }
  ];

  const flatClues = [];
  categories.forEach(function (category, categoryIndex) {
    category.clues.forEach(function (clue, clueIndex) {
      flatClues.push({ category: category.title, categoryIndex: categoryIndex, clueIndex: clueIndex, clue: clue });
    });
  });

  const storageKey = "cfm816-teacher-viewed-v1";
  const viewed = new Set();
  const dom = {
    grid: document.getElementById("teacher-grid"),
    progress: document.getElementById("teacher-progress"),
    modalRoot: document.getElementById("teacher-modal-root"),
    theme: document.getElementById("teacher-theme"),
    clearViewed: document.getElementById("clear-viewed")
  };
  let selectedIndex = null;
  let previousFocus = null;
  let clearArmed = false;
  let clearTimer = null;

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (character) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#039;" }[character];
    });
  }

  function loadViewed() {
    try {
      const stored = JSON.parse(localStorage.getItem(storageKey));
      if (Array.isArray(stored)) stored.filter(function (id) { return /^\d-[0-4]$/.test(id); }).forEach(function (id) { viewed.add(id); });
    } catch (_) {}
  }

  function saveViewed() {
    try { localStorage.setItem(storageKey, JSON.stringify(Array.from(viewed))); } catch (_) {}
  }

  function clueId(categoryIndex, clueIndex) {
    return categoryIndex + "-" + clueIndex;
  }

  function renderGrid() {
    dom.grid.innerHTML = categories.map(function (category, categoryIndex) {
      const buttons = category.clues.map(function (clue, clueIndex) {
        const id = clueId(categoryIndex, clueIndex);
        const flatIndex = categoryIndex * 5 + clueIndex;
        return '<button class="teacher-clue' + (viewed.has(id) ? ' viewed' : '') + '" type="button" data-flat-index="' + flatIndex + '" aria-label="' +
          escapeHtml(category.title + " for " + clue.value + " points") + '">' + clue.value + '</button>';
      }).join("");
      return '<section class="teacher-category"><h3>' + escapeHtml(category.title) + '</h3>' + buttons + '</section>';
    }).join("");
    const complete = viewed.size;
    dom.progress.innerHTML = '<span>' + complete + '/25 viewed</span><div><i style="width:' + ((complete / 25) * 100) + '%"></i></div>';
    dom.progress.setAttribute("aria-label", complete + " of 25 clues viewed");
  }

  function renderPassage(passage) {
    const verses = passage.verses.map(function (verse) {
      return '<p><span class="verse-number">' + escapeHtml(verse[0]) + '</span>' + escapeHtml(verse[1]) + '</p>';
    }).join("");
    const note = passage.note ? '<p class="passage-note">' + escapeHtml(passage.note) + '</p>' : '';
    return '<section class="teacher-passage"><h3><a href="' + escapeHtml(passage.url) + '" target="_blank" rel="noreferrer">' +
      escapeHtml(passage.reference) + ' <span aria-hidden="true">↗</span></a></h3>' + verses + note + '</section>';
  }

  function renderModal() {
    if (selectedIndex === null) {
      dom.modalRoot.innerHTML = "";
      document.body.classList.remove("teacher-modal-open");
      return;
    }
    const item = flatClues[selectedIndex];
    const clue = item.clue;
    const passagesHtml = clue.passages.map(renderPassage).join("");
    const insight = clue.insight ? '<p class="teacher-insight"><strong>Teaching thought:</strong> ' + escapeHtml(clue.insight) + '</p>' : '';
    const lessonLink = clue.lessonUrl ? '<span>Passage selected from the cited lesson section • <a href="' + escapeHtml(clue.lessonUrl) + '" target="_blank" rel="noreferrer">open lesson</a></span>' : '<span>Tap a reference to open it in Gospel Library</span>';
    dom.modalRoot.innerHTML = '<div class="teacher-backdrop" id="teacher-backdrop"><article class="teacher-dialog" role="dialog" aria-modal="true" aria-labelledby="teacher-dialog-title">' +
      '<header class="teacher-dialog-top"><div class="teacher-dialog-meta"><span>' + clue.value + ' POINTS</span><strong>' + escapeHtml(item.category) + '</strong></div>' +
      '<button class="teacher-close" id="teacher-close" type="button" aria-label="Close answer key">×</button></header>' +
      '<div class="teacher-detail"><section class="teacher-question-card"><span class="teacher-label">QUESTION</span><h2 id="teacher-dialog-title">' + escapeHtml(clue.question) + '</h2></section>' +
      '<div class="teacher-detail-grid"><section class="teacher-scripture-card"><div class="teacher-scripture-head"><span class="teacher-label">SCRIPTURE TEXT</span>' + lessonLink + '</div>' + passagesHtml + '</section>' +
      '<aside class="teacher-answer-card"><span class="teacher-label">ANSWER</span><p>' + escapeHtml(clue.answer) + '</p>' + insight + '</aside></div></div>' +
      '<nav class="teacher-dialog-nav" aria-label="Clue navigation"><button type="button" data-teacher-nav="previous"' + (selectedIndex === 0 ? ' disabled' : '') + '>← Previous</button>' +
      '<button class="back-board" type="button" data-teacher-nav="close">Back to board</button><button type="button" data-teacher-nav="next"' + (selectedIndex === flatClues.length - 1 ? ' disabled' : '') + '>Next →</button></nav>' +
      '</article></div>';
    document.body.classList.add("teacher-modal-open");
  }

  function selectClue(index, keepPreviousFocus) {
    if (!Number.isInteger(index) || index < 0 || index >= flatClues.length) return;
    if (!keepPreviousFocus) previousFocus = document.activeElement;
    selectedIndex = index;
    const item = flatClues[index];
    viewed.add(clueId(item.categoryIndex, item.clueIndex));
    saveViewed();
    renderGrid();
    renderModal();
    history.replaceState(null, "", "#teacher-clue-" + (item.categoryIndex + 1) + "-" + (item.clueIndex + 1));
    requestAnimationFrame(function () { document.getElementById("teacher-close")?.focus(); });
  }

  function closeModal() {
    selectedIndex = null;
    renderModal();
    history.replaceState(null, "", location.pathname + location.search);
    if (previousFocus && typeof previousFocus.focus === "function") previousFocus.focus();
    previousFocus = null;
  }

  function applyTheme(theme, persist) {
    const dark = theme === "dark";
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    dom.theme.setAttribute("aria-pressed", String(dark));
    dom.theme.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
    dom.theme.querySelector(".theme-label").textContent = dark ? "Light mode" : "Dark mode";
    const themeColor = document.querySelector('meta[name="theme-color"]');
    if (themeColor) themeColor.content = dark ? "#0a0a0a" : "#e9eff4";
    if (persist) {
      try { localStorage.setItem("cfm816-otw-theme", dark ? "dark" : "light"); } catch (_) {}
    }
  }

  function openFromHash() {
    const match = location.hash.match(/^#teacher-clue-([1-5])-([1-5])$/);
    if (!match) return;
    selectClue((Number(match[1]) - 1) * 5 + (Number(match[2]) - 1), false);
  }

  dom.grid.addEventListener("click", function (event) {
    const button = event.target.closest("[data-flat-index]");
    if (button) selectClue(Number(button.dataset.flatIndex), false);
  });

  dom.modalRoot.addEventListener("click", function (event) {
    if (event.target.id === "teacher-backdrop" || event.target.closest("#teacher-close") || event.target.closest('[data-teacher-nav="close"]')) {
      closeModal();
      return;
    }
    const navigation = event.target.closest("[data-teacher-nav]");
    if (!navigation || selectedIndex === null) return;
    if (navigation.dataset.teacherNav === "previous") selectClue(selectedIndex - 1, true);
    if (navigation.dataset.teacherNav === "next") selectClue(selectedIndex + 1, true);
  });

  dom.theme.addEventListener("click", function () {
    applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark", true);
  });

  dom.clearViewed.addEventListener("click", function () {
    if (!clearArmed) {
      clearArmed = true;
      dom.clearViewed.textContent = "Tap again to clear";
      clearTimer = window.setTimeout(function () {
        clearArmed = false;
        dom.clearViewed.textContent = "Clear viewed clues";
      }, 3000);
      return;
    }
    window.clearTimeout(clearTimer);
    clearArmed = false;
    viewed.clear();
    saveViewed();
    renderGrid();
    dom.clearViewed.textContent = "Clear viewed clues";
  });

  document.addEventListener("keydown", function (event) {
    if (selectedIndex === null) return;
    if (event.key === "Escape") closeModal();
    if (event.key === "ArrowLeft" && selectedIndex > 0) selectClue(selectedIndex - 1, true);
    if (event.key === "ArrowRight" && selectedIndex < flatClues.length - 1) selectClue(selectedIndex + 1, true);
    if (event.key === "Tab") {
      const focusable = Array.from(dom.modalRoot.querySelectorAll('a[href], button:not([disabled])'));
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
  });

  loadViewed();
  renderGrid();
  applyTheme(document.documentElement.dataset.theme === "dark" ? "dark" : "light", false);
  openFromHash();
})();
