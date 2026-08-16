(function () {
  "use strict";

  const lessonUrl = "https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-old-testament-2026/33?lang=eng";
  const categories = [
    {
      title: "Job’s Story", shortTitle: "Job’s Story", clues: [
        { value: 100, clue: "Before any trials began, Job was described with four character traits. Name any two.", answer: "He was perfect (or blameless), upright, feared God, and turned away from evil.", reference: "Job 1:1", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/1?id=p1&lang=eng#p1" },
        { value: 200, clue: "After losing his possessions and children, Job fell to the ground. What surprising thing did he do next?", answer: "He worshipped God.", reference: "Job 1:20", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/1?id=p20&lang=eng#p20", insight: "Sorrow and faith can exist at the same time." },
        { value: 300, clue: "Finish Job’s words: “The Lord gave, and the Lord hath taken away; ______.”", answer: "“Blessed be the name of the Lord.”", reference: "Job 1:21", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/1?id=p21&lang=eng#p21" },
        { value: 400, clue: "What painful physical condition struck Job after his other losses?", answer: "He was covered with sore boils from the sole of his foot to the crown of his head.", reference: "Job 2:7", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/2?id=p7&lang=eng#p7" },
        { value: 500, clue: "For how long did Job’s friends sit silently with him when they saw his grief?", answer: "Seven days and seven nights.", reference: "Job 2:13", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/2?id=p13&lang=eng#p13", insight: "Being present can be a powerful first step in comforting someone." }
      ]
    },
    {
      title: "Faith Under Fire", shortTitle: "Faith Under Fire", clues: [
        { value: 100, clue: "According to Satan’s accusation, why was Job faithful to God?", answer: "Satan claimed Job was faithful only because God had protected and blessed him.", reference: "Job 1:9–11", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/1?id=p9-p11&lang=eng#p9" },
        { value: 200, clue: "Complete Job’s declaration of trust: “Though he slay me, ______.”", answer: "“Yet will I trust in him.”", reference: "Job 13:15", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/13?id=p15&lang=eng#p15" },
        { value: 300, clue: "When Job’s wife told him to curse God, what question did Job ask in response?", answer: "“Shall we receive good at the hand of God, and shall we not receive evil?”", reference: "Job 2:9–10", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/2?id=p9-p10&lang=eng#p9", insight: "Job did not pretend his suffering was easy; he chose to keep trusting." },
        { value: 400, clue: "This week’s lesson teaches that unanswered questions can coexist with what?", answer: "Faith.", reference: "Come, Follow Me introduction", scriptureUrl: lessonUrl, media: { title: "Seeing God’s Family through the Overview Lens", speaker: "Sister Tamara W. Runia", youtubeId: "lgcOJSiAISY", start: 454, end: 545, duration: "1-minute 31-second excerpt" } },
        { value: 500, clue: "What did Job refuse to surrender, even when his faith and motives were questioned?", answer: "His integrity.", reference: "Job 2:3, 9; 27:5", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/27?id=p5&lang=eng#p5" }
      ]
    },
    {
      title: "My Redeemer Lives", shortTitle: "My Redeemer", clues: [
        { value: 100, clue: "Who declared, “I know that my redeemer liveth”?", answer: "Job.", reference: "Job 19:25", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/19?id=p25&lang=eng#p25" },
        { value: 200, clue: "Who is the Redeemer Job testified of?", answer: "Jesus Christ.", reference: "Job 19:25–27", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/19?id=p25-p27&lang=eng#p25" },
        { value: 300, clue: "According to Job’s testimony, what would he one day see “in [his] flesh”?", answer: "He would see God.", reference: "Job 19:26–27", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/19?id=p26-p27&lang=eng#p26", insight: "Job’s words point to resurrection and a living Redeemer." },
        { value: 400, clue: "Job asked, “If a man die, shall he live again?” Because of Jesus Christ, what is the answer?", answer: "Yes. Because Jesus Christ was resurrected, we will all live again.", reference: "Job 14:14; Alma 11:42–44", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/14?id=p14&lang=eng#p14" },
        { value: 500, clue: "What hymn suggested in this week’s lesson echoes Job’s testimony?", answer: "“I Know That My Redeemer Lives” (Hymns, no. 136).", reference: "Job 19:25; Hymns, no. 136", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/19?id=p25&lang=eng#p25" }
      ]
    },
    {
      title: "Through the Trial", shortTitle: "Through the Trial", clues: [
        { value: 100, clue: "What question was at the heart of the debate between Job and his friends?", answer: "Why do righteous people sometimes suffer?", reference: "Job 21–24", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/21?id=p1&lang=eng#p1" },
        { value: 200, clue: "Finish Job’s hopeful comparison: “When he hath tried me, I shall come forth as ______.”", answer: "Gold.", reference: "Job 23:10", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/23?id=p10&lang=eng#p10" },
        { value: 300, clue: "Second Nephi teaches that what is necessary “in all things” for God’s plan?", answer: "Opposition.", reference: "2 Nephi 2:11–13", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/bofm/2-ne/2?id=p11-p13&lang=eng#p11" },
        { value: 400, clue: "In Ether 12:27, what can Christ make strong when we humble ourselves and have faith in Him?", answer: "Our weak things.", reference: "Ether 12:27", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/bofm/ether/12?id=p27&lang=eng#p27" },
        { value: 500, clue: "Job’s friends accused him when he was suffering. According to Job, what should good friends do instead?", answer: "Uplift and strengthen with their words.", reference: "Job 16:1–5", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/16?id=p1-p5&lang=eng#p1", insight: "A Christlike friend comforts instead of guessing why someone is suffering." }
      ]
    },
    {
      title: "God’s Greater View", shortTitle: "God’s View", clues: [
        { value: 100, clue: "When God answered Job, did He give a detailed explanation for every trial?", answer: "No. He taught Job to see His wisdom, power, and greater perspective.", reference: "Job 38–40", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/38?id=p1&lang=eng#p1", media: { title: "Yet Will I Trust Him", speaker: "Elder Dale G. Renlund", sourceUrl: "https://assets.churchofjesuschrist.org/q50klju3vmizhx2a089b4d32etakc1714346xtb7-720p-en.mp4", posterUrl: "https://www.churchofjesuschrist.org/imgs/960a93tcf3t8eciguovi13aoywgcv9umb83vwxes/full/!1280,/0/default", captionsUrl: "media/cfm816/yet-will-i-trust-him-en.vtt", start: 127, end: 280, duration: "2-minute 33-second excerpt" } },
        { value: 200, clue: "What did the Lord ask Job: “Where wast thou when I laid” what?", answer: "“The foundations of the earth.”", reference: "Job 38:4", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/38?id=p4&lang=eng#p4" },
        { value: 300, clue: "The Lord pointed to animals, weather, stars, and the earth to teach Job. What do these examples all have in common?", answer: "They are God’s creations and show His wisdom and power.", reference: "Job 38–39", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/38?id=p1&lang=eng#p1" },
        { value: 400, clue: "After hearing the Lord, Job said, “I know that thou canst do” what?", answer: "“Every thing.”", reference: "Job 42:2", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/42?id=p2&lang=eng#p2" },
        { value: 500, clue: "Complete the central lesson heading: “God’s perspective is ______.”", answer: "“Greater than mine.”", reference: "Come, Follow Me; Job 38–40; 42", scriptureUrl: "https://www.churchofjesuschrist.org/study/scriptures/ot/job/42?id=p1-p6&lang=eng#p1", insight: "We may not see the whole picture, but we can trust the One who does.", media: { title: "Think Celestial!", speaker: "President Russell M. Nelson", youtubeId: "ZghD9LplPug", start: 470, end: 520, duration: "50-second excerpt" } }
      ]
    }
  ];

  const lightningQuestions = [
    { question: "What best summarizes Job’s response to suffering?", choices: ["He never felt sad", "He kept his integrity and faith", "He received every answer immediately", "He stopped asking questions"], correct: 1, reference: "Job 1:20–22; 2:9–10" },
    { question: "What truth did Job proclaim in one of his hardest moments?", choices: ["Trials are always punishment", "Good people never suffer", "My Redeemer lives", "Friends always understand"], correct: 2, reference: "Job 19:25–27" },
    { question: "How did the Lord broaden Job’s perspective?", choices: ["By discussing His creations", "By blaming Job’s friends", "By removing every memory", "By saying questions are wrong"], correct: 0, reference: "Job 38–40" },
    { question: "What should a Christlike friend do when someone is suffering?", choices: ["Assume they sinned", "Avoid them", "Uplift and encourage", "Demand an explanation"], correct: 2, reference: "Job 16:1–5" },
    { question: "Which idea belongs at the heart of this week’s lesson?", choices: ["Faith removes every question", "Questions can coexist with faith", "Trials prove God is absent", "We should understand everything now"], correct: 1, reference: "Come, Follow Me introduction" }
  ];

  const storageKey = "trials-and-trust-game-v1";
  const state = {
    mode: "board",
    teams: [{ name: "Team Olive", score: 0 }, { name: "Team Gold", score: 0 }],
    activeTeam: 0,
    used: new Set(),
    selected: null,
    showMedia: false,
    showAnswer: false,
    resetArmed: false,
    quizIndex: 0,
    quizScore: 0,
    quizChoice: null
  };

  const dom = {
    game: document.getElementById("game"),
    boardTab: document.getElementById("board-tab"),
    quizTab: document.getElementById("quiz-tab"),
    boardView: document.getElementById("board-view"),
    quizView: document.getElementById("quiz-view"),
    boardProgress: document.getElementById("board-progress"),
    scoreRow: document.getElementById("score-row"),
    gameBoard: document.getElementById("game-board"),
    boardFinish: document.getElementById("board-finish"),
    resetControl: document.getElementById("reset-control"),
    modalRoot: document.getElementById("modal-root")
  };

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (character) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#039;" }[character];
    });
  }

  function loadState() {
    try {
      const stored = JSON.parse(localStorage.getItem(storageKey));
      if (Array.isArray(stored?.teams) && stored.teams.length === 2) {
        state.teams = state.teams.map(function (team, index) {
          const score = Number(stored.teams[index]?.score);
          return { name: team.name, score: Number.isFinite(score) ? score : 0 };
        });
      }
      if (Array.isArray(stored?.used)) {
        state.used = new Set(stored.used.filter(function (id) { return /^\d-[0-4]$/.test(id); }));
      }
      if (stored?.activeTeam === 0 || stored?.activeTeam === 1) state.activeTeam = stored.activeTeam;
    } catch (_) {
      // The game still works when browser storage is unavailable or invalid.
    }
  }

  function saveState() {
    try {
      localStorage.setItem(storageKey, JSON.stringify({ teams: state.teams, used: Array.from(state.used), activeTeam: state.activeTeam }));
    } catch (_) {
      // A live game can continue without persistence.
    }
  }

  function formatTimestamp(totalSeconds) {
    return Math.floor(totalSeconds / 60) + ":" + String(totalSeconds % 60).padStart(2, "0");
  }

  function setMode(mode, shouldScroll) {
    state.mode = mode;
    const boardActive = mode === "board";
    dom.boardTab.classList.toggle("active", boardActive);
    dom.quizTab.classList.toggle("active", !boardActive);
    dom.boardTab.setAttribute("aria-selected", String(boardActive));
    dom.quizTab.setAttribute("aria-selected", String(!boardActive));
    dom.boardView.hidden = !boardActive;
    dom.quizView.hidden = boardActive;
    if (boardActive) renderBoard(); else renderQuiz();
    if (shouldScroll) requestAnimationFrame(function () { dom.game.scrollIntoView({ behavior: "smooth", block: "start" }); });
  }

  function renderBoard() {
    const completed = state.used.size;
    dom.boardProgress.setAttribute("aria-label", completed + " of 25 clues complete");
    dom.boardProgress.querySelector("span").textContent = completed + "/25 complete";
    dom.boardProgress.querySelector("i").style.width = (completed * 4) + "%";

    dom.scoreRow.innerHTML = state.teams.map(function (team, index) {
      const active = state.activeTeam === index;
      return '<button type="button" class="team-card team-' + index + (active ? ' is-active' : '') + '" data-team="' + index + '" aria-pressed="' + active + '">' +
        '<span class="team-label"><i></i> ' + escapeHtml(team.name) + '</span><b>' + team.score.toLocaleString() + '</b>' +
        '<small>' + (active ? "Choosing now" : "Tap to choose") + '</small></button>';
    }).join("") + '<div class="score-tools" aria-label="Manual score controls"><span>Score fix</span><div>' +
      '<button type="button" data-score="-100" aria-label="Subtract 100 from ' + escapeHtml(state.teams[state.activeTeam].name) + '">−100</button>' +
      '<button type="button" data-score="100" aria-label="Add 100 to ' + escapeHtml(state.teams[state.activeTeam].name) + '">+100</button></div></div>';

    dom.gameBoard.innerHTML = categories.map(function (category, categoryIndex) {
      return '<div class="category-column"><div class="category-title"><span class="desktop-title">' + escapeHtml(category.title) + '</span>' +
        '<span class="mobile-title">' + escapeHtml(category.shortTitle) + '</span></div>' + category.clues.map(function (clue, clueIndex) {
          const id = categoryIndex + "-" + clueIndex;
          const used = state.used.has(id);
          return '<button type="button" class="clue-tile' + (used ? ' used' : '') + '" data-category="' + categoryIndex + '" data-clue="' + clueIndex + '"' +
            (used ? ' disabled' : '') + ' aria-label="' + escapeHtml(category.title + " for " + clue.value + " points" + (used ? ", completed" : "")) + '">' +
            (used ? '<span aria-hidden="true">✓</span>' : clue.value) + '</button>';
        }).join("") + '</div>';
    }).join("");

    if (completed === 25) {
      const result = state.teams[0].score === state.teams[1].score ? "It’s a tie—finish with the reflection question below." :
        (state.teams[0].score > state.teams[1].score ? state.teams[0].name : state.teams[1].name) + " wins this round!";
      dom.boardFinish.innerHTML = '<span aria-hidden="true">✦</span><div><strong>Every clue is complete!</strong><p>' + escapeHtml(result) + '</p></div><button type="button" id="finish-quiz">Play lightning quiz</button>';
      dom.boardFinish.hidden = false;
    } else {
      dom.boardFinish.hidden = true;
      dom.boardFinish.innerHTML = "";
    }

    dom.resetControl.innerHTML = state.resetArmed ?
      '<div class="reset-confirm"><span>Start over?</span><button type="button" id="confirm-reset">Yes, reset</button><button type="button" id="cancel-reset">Cancel</button></div>' :
      '<button type="button" class="reset-link" id="arm-reset">Reset game</button>';
  }

  function openClue(categoryIndex, clueIndex) {
    const id = categoryIndex + "-" + clueIndex;
    if (state.used.has(id)) return;
    state.selected = [categoryIndex, clueIndex];
    state.showMedia = Boolean(categories[categoryIndex].clues[clueIndex].media);
    state.showAnswer = false;
    renderModal();
  }

  function closeClue() {
    state.selected = null;
    state.showMedia = false;
    state.showAnswer = false;
    document.body.classList.remove("modal-open");
    dom.modalRoot.innerHTML = "";
  }

  function gradeClue(correct) {
    if (!state.selected) return;
    const categoryIndex = state.selected[0];
    const clueIndex = state.selected[1];
    const clue = categories[categoryIndex].clues[clueIndex];
    if (correct) state.teams[state.activeTeam].score += clue.value;
    state.used.add(categoryIndex + "-" + clueIndex);
    state.activeTeam = state.activeTeam === 0 ? 1 : 0;
    saveState();
    closeClue();
    renderBoard();
  }

  function resetGame() {
    state.teams = [{ name: "Team Olive", score: 0 }, { name: "Team Gold", score: 0 }];
    state.activeTeam = 0;
    state.used = new Set();
    state.selected = null;
    state.showMedia = false;
    state.showAnswer = false;
    state.resetArmed = false;
    state.quizIndex = 0;
    state.quizScore = 0;
    state.quizChoice = null;
    try { localStorage.removeItem(storageKey); } catch (_) {}
    closeClue();
    if (state.mode === "board") renderBoard(); else renderQuiz();
  }

  function renderModal() {
    if (!state.selected) return;
    const categoryIndex = state.selected[0];
    const clueIndex = state.selected[1];
    const category = categories[categoryIndex];
    const clue = category.clues[clueIndex];
    const media = clue.media;
    let content = "";

    if (state.showMedia && media) {
      let player = "";
      if (media.youtubeId) {
        const source = "https://www.youtube-nocookie.com/embed/" + encodeURIComponent(media.youtubeId) + "?start=" + media.start + "&end=" + media.end + "&rel=0&playsinline=1";
        player = '<iframe src="' + source + '" title="' + escapeHtml(media.title + " excerpt by " + media.speaker) + '" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>';
      } else if (media.sourceUrl) {
        player = '<video id="timed-video" controls playsinline preload="metadata" poster="' + escapeHtml(media.posterUrl || "") + '" aria-label="' + escapeHtml(media.title + " excerpt by " + media.speaker) + '">' +
          '<source src="' + escapeHtml(media.sourceUrl) + '" type="video/mp4"><track kind="captions" src="' + escapeHtml(media.captionsUrl) + '" srclang="en" label="English" default></video>';
      }
      content = '<div class="media-stage"><div class="media-heading"><div><span class="media-kicker">WATCH FIRST • ' + escapeHtml(media.duration) + '</span>' +
        '<h2>' + escapeHtml(media.title) + '</h2><p>' + escapeHtml(media.speaker) + '</p></div><span class="media-time" aria-label="Excerpt from ' +
        formatTimestamp(media.start) + ' to ' + formatTimestamp(media.end) + '">' + formatTimestamp(media.start) + '–' + formatTimestamp(media.end) + '</span></div>' +
        '<div class="video-frame">' + player + '</div><div class="media-footer"><p><span aria-hidden="true">▶</span> Press play, then continue when the excerpt finishes.</p>' +
        '<button type="button" class="continue-clue-button" id="continue-clue">Continue to clue <span>→</span></button></div></div>';
    } else {
      const qrSource = "media/cfm816/qr/clue-" + (categoryIndex + 1) + "-" + (clueIndex + 1) + ".png";
      const clueBody = !state.showAnswer ?
        '<div class="clue-search-reference" aria-label="Find the answer in ' + escapeHtml(clue.reference) + '"><span>FIND IT IN</span><strong>' + escapeHtml(clue.reference) + '</strong></div>' +
        '<p class="clue-question">' + escapeHtml(clue.clue) + '</p><div class="think-strip"><span aria-hidden="true">⌛</span><p><strong>Think together.</strong> Scan, read, and discuss your answer.</p></div>' +
        '<button type="button" class="reveal-button" id="reveal-answer">Reveal answer <span>→</span></button>' :
        '<p class="answer-label">ANSWER</p><p class="clue-answer">' + escapeHtml(clue.answer) + '</p><p class="scripture-reference"><span>READ:</span> ' + escapeHtml(clue.reference) + '</p>' +
        (clue.insight ? '<p class="clue-insight"><span aria-hidden="true">✦</span>' + escapeHtml(clue.insight) + '</p>' : '') +
        '<div class="grade-actions"><button type="button" class="not-quite" id="grade-no">Not quite</button><button type="button" class="got-it" id="grade-yes">Correct <span>+' + clue.value + '</span></button></div>' +
        '<small class="turn-note">After scoring, it will be ' + escapeHtml(state.teams[state.activeTeam === 0 ? 1 : 0].name) + '’s turn.</small>';
      content = '<div class="clue-presentation-layout"><a class="qr-panel" href="' + escapeHtml(clue.scriptureUrl) + '" target="_blank" rel="noreferrer" aria-label="Open ' + escapeHtml(clue.reference) + ' on this device">' +
        '<span>SCAN WITH YOUR PHONE</span><img src="' + qrSource + '" alt="QR code for ' + escapeHtml(clue.reference) + '" width="900" height="900"><strong>Open the passage</strong>' +
        '<small>churchofjesuschrist.org <i aria-hidden="true">↗</i></small></a><div class="clue-content"><span class="clue-value">' + clue.value + '</span>' + clueBody + '</div></div>';
    }

    dom.modalRoot.innerHTML = '<div class="modal-backdrop" id="modal-backdrop" role="presentation"><div class="clue-dialog" id="clue-dialog" role="dialog" aria-modal="true" aria-labelledby="clue-category" tabindex="-1">' +
      '<div class="dialog-top"><div><p id="clue-category">' + escapeHtml(category.title) + '</p><span>' + escapeHtml(state.teams[state.activeTeam].name) + ' • ' + clue.value + ' points</span></div>' +
      '<button type="button" class="close-button" id="close-clue" aria-label="Close clue">×</button></div><div class="dialog-body' + (state.showMedia ? ' media-dialog-body' : '') + '">' + content + '</div></div></div>';
    document.body.classList.add("modal-open");

    const timedVideo = document.getElementById("timed-video");
    if (timedVideo && media) {
      timedVideo.addEventListener("loadedmetadata", function () { timedVideo.currentTime = media.start; }, { once: true });
      timedVideo.addEventListener("play", function () { if (timedVideo.currentTime >= media.end - 0.25) timedVideo.currentTime = media.start; });
      timedVideo.addEventListener("timeupdate", function () { if (timedVideo.currentTime >= media.end) timedVideo.pause(); });
    }
    requestAnimationFrame(function () { document.getElementById("clue-dialog")?.focus(); });
  }

  function renderQuiz() {
    const complete = state.quizIndex >= lightningQuestions.length;
    if (complete) {
      const title = state.quizScore === 5 ? "Golden finish!" : state.quizScore >= 3 ? "Well done!" : "Keep searching.";
      const message = state.quizScore === 5 ? "You know Job’s story and its message of trust." : "The scriptures are always ready for another look.";
      dom.quizView.innerHTML = '<div class="quiz-results"><span class="results-spark" aria-hidden="true">✦</span><p class="section-kicker">ROUND COMPLETE</p><h2>' + title + '</h2>' +
        '<p class="results-score">' + state.quizScore + '<span>/5</span></p><p>' + message + '</p><button type="button" class="start-button" id="restart-quiz">Play again <span>↻</span></button></div>';
      return;
    }

    const question = lightningQuestions[state.quizIndex];
    const answered = state.quizChoice !== null;
    const choices = question.choices.map(function (choice, index) {
      const correct = question.correct === index;
      const selected = state.quizChoice === index;
      const className = !answered ? "" : correct ? "is-correct" : selected ? "is-wrong" : "is-muted";
      return '<button type="button" data-quiz-choice="' + index + '" class="' + className + '"' + (answered ? ' disabled' : '') + '><span>' + String.fromCharCode(65 + index) + '</span>' + escapeHtml(choice) + '</button>';
    }).join("");
    const feedback = answered ? '<div class="quiz-feedback ' + (state.quizChoice === question.correct ? 'correct' : 'wrong') + '" role="status"><div><strong>' +
      (state.quizChoice === question.correct ? "That’s right!" : "Good try—take another look.") + '</strong><p>' + escapeHtml(question.reference) + '</p></div><button type="button" id="next-question">' +
      (state.quizIndex === lightningQuestions.length - 1 ? "See results" : "Next question") + ' <span>→</span></button></div>' : '';
    const progress = ((state.quizIndex + (answered ? 1 : 0)) / lightningQuestions.length) * 100;
    dom.quizView.innerHTML = '<div class="quiz-header"><div><p class="section-kicker">LIGHTNING ROUND</p><h2>Question ' + (state.quizIndex + 1) + ' of ' + lightningQuestions.length + '</h2></div>' +
      '<div class="quiz-score"><span>Score</span><b>' + state.quizScore + '/' + lightningQuestions.length + '</b></div></div><div class="quiz-progress"><i style="width:' + progress + '%"></i></div>' +
      '<div class="quiz-card"><p class="quiz-question">' + escapeHtml(question.question) + '</p><div class="answer-grid">' + choices + '</div>' + feedback + '</div>';
  }

  dom.boardTab.addEventListener("click", function () { setMode("board", false); });
  dom.quizTab.addEventListener("click", function () { setMode("quiz", false); });
  document.getElementById("start-game").addEventListener("click", function () { setMode("board", true); });
  document.getElementById("header-quiz").addEventListener("click", function () { setMode("quiz", true); });

  dom.scoreRow.addEventListener("click", function (event) {
    const teamButton = event.target.closest("[data-team]");
    if (teamButton) {
      state.activeTeam = Number(teamButton.dataset.team);
      saveState();
      renderBoard();
      return;
    }
    const scoreButton = event.target.closest("[data-score]");
    if (scoreButton) {
      state.teams[state.activeTeam].score += Number(scoreButton.dataset.score);
      saveState();
      renderBoard();
    }
  });

  dom.gameBoard.addEventListener("click", function (event) {
    const button = event.target.closest("[data-category][data-clue]");
    if (button) openClue(Number(button.dataset.category), Number(button.dataset.clue));
  });

  dom.resetControl.addEventListener("click", function (event) {
    if (event.target.closest("#arm-reset")) { state.resetArmed = true; renderBoard(); }
    if (event.target.closest("#cancel-reset")) { state.resetArmed = false; renderBoard(); }
    if (event.target.closest("#confirm-reset")) resetGame();
  });

  dom.boardFinish.addEventListener("click", function (event) { if (event.target.closest("#finish-quiz")) setMode("quiz", false); });

  dom.quizView.addEventListener("click", function (event) {
    const choice = event.target.closest("[data-quiz-choice]");
    if (choice && state.quizChoice === null) {
      state.quizChoice = Number(choice.dataset.quizChoice);
      if (state.quizChoice === lightningQuestions[state.quizIndex].correct) state.quizScore += 1;
      renderQuiz();
      return;
    }
    if (event.target.closest("#next-question")) { state.quizIndex += 1; state.quizChoice = null; renderQuiz(); }
    if (event.target.closest("#restart-quiz")) { state.quizIndex = 0; state.quizScore = 0; state.quizChoice = null; renderQuiz(); }
  });

  dom.modalRoot.addEventListener("mousedown", function (event) { if (event.target.id === "modal-backdrop") closeClue(); });
  dom.modalRoot.addEventListener("click", function (event) {
    if (event.target.closest("#close-clue")) closeClue();
    if (event.target.closest("#continue-clue")) { state.showMedia = false; renderModal(); }
    if (event.target.closest("#reveal-answer")) { state.showAnswer = true; renderModal(); }
    if (event.target.closest("#grade-no")) gradeClue(false);
    if (event.target.closest("#grade-yes")) gradeClue(true);
  });
  document.addEventListener("keydown", function (event) { if (event.key === "Escape" && state.selected) closeClue(); });

  loadState();
  setMode("board", false);
})();
