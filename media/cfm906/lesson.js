"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const sequence = ["welcome", "worship", "renewal", "learning", "together", "take-home"];
  const optionalMoments = ["psalms", "praise", "lamp", "connections"];
  const labels = { welcome: "Welcome", worship: "Watch: our worship", renewal: "Discuss: renewal", learning: "Watch: our learning", together: "Discuss: learning", "take-home": "Take it home", psalms: "A moment in the Psalms", praise: "Gather our praise", lamp: "A light for the next step", connections: "Find Christ in the Psalms" };
  const slides = Array.from(document.querySelectorAll(".slide"));
  const videos = Array.from(document.querySelectorAll("video"));
  const guide = $("lesson-guide");
  let current = "welcome";
  let returnFromMoment = "welcome";
  let noticeTimeout;
  const localVideos = new Map();
  let wakeLock = null;

  function notify(message) {
    clearTimeout(noticeTimeout);
    $("status-message").textContent = message;
    $("status-message").hidden = false;
    noticeTimeout = setTimeout(() => { $("status-message").hidden = true; }, 6000);
  }

  function activateVideo(video) {
    if (!video || video.dataset.initialized) return;
    const source = video.querySelector("source");
    source.src = source.dataset.src;
    video.dataset.initialized = "true";
    video.load();
  }

  function show(id, updateHash = true) {
    if (!Object.hasOwn(labels, id)) return;
    const isOptional = optionalMoments.includes(id);
    if (isOptional && sequence.includes(current)) returnFromMoment = current;
    const focusWasInSlide = $("stage").contains(document.activeElement) || $("moments-menu").contains(document.activeElement);
    videos.forEach((video) => { if (video.closest(".slide").id !== id) video.pause(); });
    current = id;
    slides.forEach((slide) => { slide.hidden = slide.id !== current; });
    document.querySelectorAll(".video-options").forEach((details) => { details.open = false; });
    $("moments-menu").open = false;
    $("moment-select").value = id;
    $("psalms-toggle").setAttribute("aria-pressed", String(id === "psalms"));
    const index = sequence.indexOf(id);
    $("previous").disabled = index === 0;
    $("next").disabled = index === sequence.length - 1;
    $("next").textContent = isOptional ? "Return to lesson →" : id === "welcome" ? "Begin →" : (id === "worship" || id === "learning") ? "Discuss →" : id === "take-home" ? "Complete" : "Next →";
    $("lesson-progress").style.width = (isOptional ? (sequence.indexOf(returnFromMoment) + 1) : index + 1) / sequence.length * 100 + "%";
    $("slide-announcement").textContent = (index >= 0 ? `${index + 1} of ${sequence.length}. ` : "Optional. ") + labels[id];
    activateVideo($(id).querySelector("video"));
    if (updateHash) {
      try { history.replaceState(null, "", "#" + id); } catch (_) { /* The lesson still works when history is unavailable. */ }
    }
    if (focusWasInSlide) $("stage").focus({ preventScroll: true });
    window.scrollTo({ top: 0, behavior: "instant" });
  }

  function advance(direction) {
    if (optionalMoments.includes(current)) { show(returnFromMoment); return; }
    const index = Math.max(0, Math.min(sequence.length - 1, sequence.indexOf(current) + direction));
    if (sequence[index] !== current) show(sequence[index]);
  }

  $("previous").addEventListener("click", () => advance(-1));
  $("next").addEventListener("click", () => advance(1));
  $("moment-select").addEventListener("change", (event) => show(event.target.value));
  $("psalms-toggle").addEventListener("click", () => show(current === "psalms" ? returnFromMoment : "psalms"));
  document.querySelectorAll("[data-moment]").forEach((button) => button.addEventListener("click", () => show(button.dataset.moment)));
  document.addEventListener("click", (event) => { if (!$("moments-menu").contains(event.target)) $("moments-menu").open = false; });
  window.addEventListener("hashchange", () => {
    const id = location.hash.slice(1);
    if (Object.hasOwn(labels, id)) show(id, false);
  });

  $("guide-toggle").addEventListener("click", () => {
    videos.forEach((video) => video.pause());
    $("moments-menu").open = false;
    guide.showModal();
  });
  $("guide-close").addEventListener("click", () => guide.close());
  guide.addEventListener("click", (event) => {
    if (event.target !== guide) return;
    const rect = guide.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) guide.close();
  });

  document.querySelectorAll("[data-reveal]").forEach((button) => {
    button.addEventListener("click", () => {
      const content = $(button.dataset.reveal);
      content.hidden = !content.hidden;
      button.setAttribute("aria-expanded", String(!content.hidden));
      button.innerHTML = content.hidden ? 'Go a little deeper <span aria-hidden="true">+</span>' : 'Hide follow-up <span aria-hidden="true">−</span>';
    });
  });

  const scenarios = {
    weary: { reference: "Psalm 103:13–14", url: "https://www.churchofjesuschrist.org/study/scriptures/ot/ps/103?lang=eng&id=p13-p14#p13", verse: "“For he knoweth our frame; he remembereth that we are dust.”", verseNumber: "Psalm 103:14" },
    forgiveness: { reference: "Psalm 103:8–12", url: "https://www.churchofjesuschrist.org/study/scriptures/ot/ps/103?lang=eng&id=p8-p12#p8", verse: "“As far as the east is from the west, so far hath he removed our transgressions from us.”", verseNumber: "Psalm 103:12" },
    direction: { reference: "Psalm 119:105", url: "https://www.churchofjesuschrist.org/study/scriptures/ot/ps/119?lang=eng&id=p105#p105", verse: "“Thy word is a lamp unto my feet, and a light unto my path.”", verseNumber: "Psalm 119:105" },
  };
  let selectedScenario = "weary";
  function chooseScenario(id) {
    if (!Object.hasOwn(scenarios, id)) return;
    selectedScenario = id;
    const scenario = scenarios[id];
    document.querySelectorAll("[data-scenario]").forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.scenario === id)));
    $("activity-reference").textContent = scenario.reference + " ↗";
    $("activity-reference").href = scenario.url;
    $("activity-verse").textContent = scenario.verse;
    $("activity-verse").hidden = true;
    $("activity-invitation").hidden = false;
    $("reveal-scripture").textContent = "Reveal a verse";
    $("reveal-scripture").setAttribute("aria-expanded", "false");
  }
  document.querySelectorAll("[data-scenario]").forEach((button) => button.addEventListener("click", () => chooseScenario(button.dataset.scenario)));
  $("reveal-scripture").addEventListener("click", () => {
    const revealed = $("activity-verse").hidden;
    $("activity-verse").hidden = !revealed;
    $("activity-invitation").hidden = revealed;
    $("reveal-scripture").textContent = revealed ? "Hide verse" : "Reveal a verse";
    $("reveal-scripture").setAttribute("aria-expanded", String(revealed));
    if (revealed) $("slide-announcement").textContent = scenarios[selectedScenario].verseNumber + ". " + scenarios[selectedScenario].verse;
  });

  // Spoken responses stay in memory in this page, with no storage or network requests.
  const praiseWords = [];
  function paintPraise() {
    const wall = $("praise-wall");
    wall.replaceChildren();
    praiseWords.forEach((word, index) => {
      const item = document.createElement("div");
      item.setAttribute("role", "listitem");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "praise-word";
      button.textContent = word;
      button.setAttribute("aria-label", "Remove “" + word + "” from our praise wall");
      button.addEventListener("click", () => {
        praiseWords.splice(index, 1);
        paintPraise();
        $("praise-word").focus();
        $("slide-announcement").textContent = "Removed “" + word + "”.";
      });
      item.append(button);
      wall.append(item);
    });
    $("praise-empty").hidden = praiseWords.length > 0;
    $("praise-reset").disabled = praiseWords.length === 0;
    $("praise-add").disabled = praiseWords.length >= 12;
  }
  $("praise-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const word = Array.from($("praise-word").value.trim().replace(/\s+/g, " ")).slice(0, 32).join("");
    if (!word) { $("praise-word").focus(); return; }
    if (praiseWords.length >= 12) { notify("Our wall is full. Remove a word to make room for another."); return; }
    if (praiseWords.some((existing) => existing.toLocaleLowerCase() === word.toLocaleLowerCase())) { notify("That word is already part of our praise."); return; }
    praiseWords.push(word);
    paintPraise();
    $("praise-word").value = "";
    $("praise-word").focus();
    $("slide-announcement").textContent = "Added “" + word + "” to our praise.";
  });
  $("praise-reset").addEventListener("click", () => {
    praiseWords.length = 0;
    paintPraise();
    $("praise-word").value = "";
    $("praise-word").focus();
    $("slide-announcement").textContent = "The praise wall is clear.";
  });

  const lampPhrases = ["Thy word", "is a lamp unto my feet,", "and a light unto my path."];
  const lampQuestions = ["What word stands out to you?", "Where have you heard the Lord’s word this week?", "What is one next step His word can help you take?", "How can that next step bring you closer to Jesus Christ?"];
  let lampStep = 0;
  function paintLamp() {
    lampPhrases.forEach((_, index) => { $("lamp-phrase-" + (index + 1)).hidden = index >= lampStep; });
    document.querySelectorAll("[data-lamp-step]").forEach((step) => step.classList.toggle("is-lit", Number(step.dataset.lampStep) <= lampStep));
    $("lamp-placeholder").hidden = lampStep > 0;
    $("lamp-question").textContent = lampQuestions[lampStep];
    $("lamp-count").textContent = lampStep + " of 3 phrases";
    $("lamp-reveal").disabled = lampStep === 3;
    $("lamp-reveal").textContent = lampStep === 3 ? "Verse revealed" : lampStep === 0 ? "Reveal first phrase" : "Reveal next phrase";
    $("lamp-reset").disabled = lampStep === 0;
  }
  $("lamp-reveal").addEventListener("click", () => {
    if (lampStep >= 3) return;
    lampStep += 1;
    paintLamp();
    $("slide-announcement").textContent = lampPhrases[lampStep - 1];
    if (lampStep === 3) $("lamp-reset").focus();
  });
  $("lamp-reset").addEventListener("click", () => { lampStep = 0; paintLamp(); $("lamp-reveal").focus(); });

  const connections = [
    { reference: "Psalm 118:22", url: "ot/ps/118?lang=eng&id=p22#p22", verse: "“The stone which the builders refused is become the head stone of the corner.”", answer: "Matthew 21:42", answerUrl: "nt/matt/21?lang=eng&id=p42#p42", explanation: "Jesus quotes this psalm as He teaches about the rejected stone. What does it mean to build your life on Him?" },
    { reference: "Psalm 118:25–26", url: "ot/ps/118?lang=eng&id=p25-p26#p25", verse: "“Blessed be he that cometh in the name of the Lord.” (verse 26)", answer: "Matthew 21:9", answerUrl: "nt/matt/21?lang=eng&id=p9#p9", explanation: "The crowd uses these words as Jesus enters Jerusalem. How can our worship welcome Him into our lives?" },
    { reference: "Psalm 110:4", url: "ot/ps/110?lang=eng&id=p4#p4", verse: "“Thou art a priest for ever after the order of Melchizedek.”", answer: "Hebrews 5:4–10", answerUrl: "nt/heb/5?lang=eng&id=p4-p10#p4", explanation: "Hebrews applies this psalm to Christ’s calling as a high priest. What do these verses help you understand about His saving work?" },
  ];
  const connectionChoices = Array.from(document.querySelectorAll("[data-connection]"));
  let connectionIndex = 0;
  let connectionRevealed = false;
  function paintConnection() {
    const item = connections[connectionIndex];
    connectionRevealed = false;
    $("connection-count").textContent = "Connection " + (connectionIndex + 1) + " of 3";
    $("connection-reference").textContent = "Read " + item.reference + " ↗";
    $("connection-reference").href = "https://www.churchofjesuschrist.org/study/scriptures/" + item.url;
    $("connection-verse").textContent = item.verse;
    $("connection-answer-reference").textContent = "Read " + item.answer + " ↗";
    $("connection-answer-reference").href = "https://www.churchofjesuschrist.org/study/scriptures/" + item.answerUrl;
    $("connection-explanation").textContent = item.explanation;
    $("connection-answer").hidden = true;
    $("connection-feedback").textContent = "";
    $("connection-reveal").hidden = false;
    $("connection-next").hidden = true;
    $("connection-next").textContent = connectionIndex === connections.length - 1 ? "Return to lesson →" : "Next connection →";
    connectionChoices.forEach((button) => { button.disabled = false; button.setAttribute("aria-pressed", "false"); button.classList.toggle("is-match", false); });
  }
  function revealConnection() {
    connectionRevealed = true;
    $("connection-answer").hidden = false;
    $("connection-feedback").textContent = "Here is the connection from this week’s lesson.";
    $("connection-reveal").hidden = true;
    $("connection-next").hidden = false;
    connectionChoices.forEach((button, index) => { button.disabled = true; button.classList.toggle("is-match", index === connectionIndex); button.setAttribute("aria-pressed", String(index === connectionIndex)); });
    $("slide-announcement").textContent = connections[connectionIndex].answer + ". " + connections[connectionIndex].explanation;
    $("connection-next").focus({ preventScroll: true });
  }
  connectionChoices.forEach((button, index) => button.addEventListener("click", () => {
    if (connectionRevealed) return;
    connectionChoices.forEach((choice) => choice.setAttribute("aria-pressed", String(choice === button)));
    if (index === connectionIndex) revealConnection();
    else $("connection-feedback").textContent = "Look again at the passage, or reveal the connection together.";
  }));
  $("connection-reveal").addEventListener("click", revealConnection);
  $("connection-next").addEventListener("click", () => {
    if (!connectionRevealed) return;
    if (connectionIndex === connections.length - 1) { show(returnFromMoment); return; }
    connectionIndex += 1;
    paintConnection();
    $("connection-reference").focus({ preventScroll: true });
    $("slide-announcement").textContent = "Read " + connections[connectionIndex].reference + ". " + connections[connectionIndex].verse;
  });
  $("connection-reset").addEventListener("click", () => { connectionIndex = 0; paintConnection(); $("connection-reference").focus({ preventScroll: true }); });

  const totalMilliseconds = 25 * 60 * 1000;
  let remainingMilliseconds = totalMilliseconds;
  let deadline = null;
  let timerInterval = null;
  let timeUpAnnounced = false;

  function paintTimer() {
    if (deadline !== null) remainingMilliseconds = Math.max(0, deadline - Date.now());
    const seconds = Math.ceil(remainingMilliseconds / 1000);
    $("timer-display").textContent = `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
    $("timer-toggle").classList.toggle("is-ending", seconds <= 120);
    if (seconds === 0 && deadline !== null) {
      deadline = null;
      clearInterval(timerInterval);
      timerInterval = null;
      if (!timeUpAnnounced) { notify("Time to close with prayer and move to the next class."); timeUpAnnounced = true; }
    }
    const running = deadline !== null;
    $("timer-toggle").classList.toggle("is-running", running);
    $("timer-symbol").textContent = running ? "Ⅱ" : "▶";
    $("timer-toggle").setAttribute("aria-label", running ? "Pause class timer" : seconds === 0 ? "Start a new 25-minute class timer" : seconds === 1500 ? "Start 25-minute class timer" : "Resume class timer");
  }
  $("timer-toggle").addEventListener("click", () => {
    if (deadline !== null) {
      remainingMilliseconds = Math.max(0, deadline - Date.now());
      deadline = null;
      clearInterval(timerInterval);
      timerInterval = null;
    } else {
      if (remainingMilliseconds <= 0) remainingMilliseconds = totalMilliseconds;
      deadline = Date.now() + remainingMilliseconds;
      timeUpAnnounced = false;
      timerInterval = setInterval(paintTimer, 250);
    }
    paintTimer();
  });
  $("timer-reset").addEventListener("click", () => {
    clearInterval(timerInterval);
    timerInterval = null;
    deadline = null;
    remainingMilliseconds = totalMilliseconds;
    timeUpAnnounced = false;
    paintTimer();
    notify("Timer reset to 25:00. Press play when class begins.");
  });

  async function requestWakeLock() {
    if (!("wakeLock" in navigator) || document.visibilityState !== "visible" || !document.fullscreenElement || wakeLock) return;
    try { wakeLock = await navigator.wakeLock.request("screen"); wakeLock.addEventListener("release", () => { wakeLock = null; }); } catch (_) { /* Fullscreen remains usable if screen wake lock is unavailable. */ }
  }
  async function toggleFullscreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else if (document.documentElement.requestFullscreen) await document.documentElement.requestFullscreen();
      else notify("Use your browser’s fullscreen command to fill the display.");
    } catch (_) { notify("Use your browser’s fullscreen command to fill the display."); }
  }
  $("fullscreen-toggle").addEventListener("click", toggleFullscreen);
  document.addEventListener("fullscreenchange", () => {
    const full = Boolean(document.fullscreenElement);
    $("fullscreen-toggle").setAttribute("aria-pressed", String(full));
    $("fullscreen-toggle").setAttribute("aria-label", full ? "Exit fullscreen" : "Enter fullscreen");
    $("fullscreen-toggle").querySelector("span").textContent = full ? "Exit fullscreen" : "Fullscreen";
    if (full) requestWakeLock();
    else if (wakeLock) wakeLock.release().catch(() => {});
  });
  document.addEventListener("visibilitychange", () => { paintTimer(); requestWakeLock(); });
  window.addEventListener("keydown", (event) => {
    if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || guide.open) return;
    if (event.key === "Escape" && $("moments-menu").open) { $("moments-menu").open = false; $("moments-menu").querySelector("summary").focus(); return; }
    if (event.target instanceof Element && event.target.closest("input, select, textarea, video, summary, [contenteditable]")) return;
    if (event.key === "ArrowRight" || event.key === "PageDown") { event.preventDefault(); advance(1); }
    else if (event.key === "ArrowLeft" || event.key === "PageUp") { event.preventDefault(); advance(-1); }
    else if (event.key === "Home") { event.preventDefault(); show("welcome"); }
    else if (event.key === "End") { event.preventDefault(); show("take-home"); }
    else if (event.key.toLowerCase() === "f") { event.preventDefault(); toggleFullscreen(); }
  });

  function errorFor(video) { return $(video.id === "sabbath-video" ? "sabbath-error" : "school-error"); }
  function fileStatusFor(video) { return $(video.id === "sabbath-video" ? "sabbath-file-status" : "school-file-status"); }
  videos.forEach((video) => {
    video.addEventListener("error", () => { errorFor(video).hidden = false; });
    video.querySelector("source").addEventListener("error", () => { errorFor(video).hidden = false; });
    video.addEventListener("loadeddata", () => { errorFor(video).hidden = true; });
    video.addEventListener("play", () => { videos.forEach((other) => { if (other !== video) other.pause(); }); });
    video.addEventListener("ended", () => { $("slide-announcement").textContent = "Video complete. Continue to discussion when ready."; });
  });
  document.querySelectorAll("[data-for-video]").forEach((input) => {
    input.addEventListener("change", () => {
      const file = input.files?.[0];
      if (!file) return;
      if (file.type && !file.type.startsWith("video/")) { notify("Choose a video file saved on your device."); input.value = ""; return; }
      const video = $(input.dataset.forVideo);
      video.pause();
      if (localVideos.has(video.id)) URL.revokeObjectURL(localVideos.get(video.id));
      const url = URL.createObjectURL(file);
      localVideos.set(video.id, url);
      video.src = url;
      video.dataset.initialized = "true";
      errorFor(video).hidden = true;
      video.load();
      fileStatusFor(video).textContent = "Using “" + file.name + "” from this device.";
      document.querySelector(`[data-restore-video="${video.id}"]`).hidden = false;
    });
  });
  document.querySelectorAll("[data-restore-video]").forEach((button) => {
    button.addEventListener("click", () => {
      const video = $(button.dataset.restoreVideo);
      video.pause();
      video.removeAttribute("src");
      if (localVideos.has(video.id)) { URL.revokeObjectURL(localVideos.get(video.id)); localVideos.delete(video.id); }
      video.querySelector("source").src = video.querySelector("source").dataset.src;
      errorFor(video).hidden = true;
      video.load();
      fileStatusFor(video).textContent = "Using the Church’s online video.";
      document.querySelector(`[data-for-video="${video.id}"]`).value = "";
      button.hidden = true;
    });
  });
  window.addEventListener("pagehide", () => { videos.forEach((video) => video.pause()); });
  chooseScenario("weary");
  paintPraise();
  paintLamp();
  paintConnection();
  paintTimer();
  const initialId = location.hash.slice(1);
  show(Object.hasOwn(labels, initialId) ? initialId : "welcome", false);
})();
