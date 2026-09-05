"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const all = selector => [...document.querySelectorAll(selector)];
  const order = ["start", "worship", "discuss", "learning", "home-study", "finish"];
  const scenes = all(".scene"), videos = all("video"), dialogs = all("dialog");
  const notes = {
    start: ["Welcome · 1 minute", "Give everyone a few quiet seconds to think about their week. One student may share if they want to. Use the choices only to help begin a conversation, then invite an opening prayer. Start the class timer when class begins."],
    worship: ["First video · 12:23 with stops", "Play the complete video. At the first stop, leave 30 quiet seconds to write an idea about Christ in section 1. At the second, consider a choice for section 2. You choose when to continue."],
    discuss: ["Discuss sacrament meeting · 75 seconds", "Let the class choose one situation. Ask how remembering Jesus Christ in sacrament meeting could help. Take one or two responses, then ask what makes that difficult. Listen before offering your own answer."],
    learning: ["Second video · 5:07 with stop", "Play the complete video. At the partner stop, students can share a question or just where they would begin looking for an answer. Keep pairs seated and give both people a turn within 45 seconds."],
    "home-study": ["Discuss learning at home · 75 seconds", "Ask what students would choose to study and how they could begin. Invite one or two ideas. Ask how someone else could help them think it through. An unanswered question can be a worthwhile starting point."],
    finish: ["Choose a step and close · 1 minute", "Invite each student to choose something small enough to do this week and write when they will do it. The cards stay with students. Close with prayer and help everyone move to the next class on time."],
    psalm: ["Psalms extra · 60–90 seconds", "Use only if time remains. Read Psalm 119:105, then choose one phrase to explore. Ask what the image of a lamp suggests. A personal application can stay private; do not promise that every answer will come on a particular schedule."]
  };
  // Suggested stops in the gaps between sentences in the English captions.
  const cues = {
    forgiveness: { video: "y-worship-video", at: 188, label: "Video 1 · 3:08 · Quiet reflection", seconds: 30, title: "What did you hear about Christ’s willingness to forgive?", instruction: "Write an idea you want to remember in section 1. This is yours to keep.", note: "Have cards on chairs, or pass them out now. Give the full 30 seconds for thought. If time allows, ask why someone might find forgiveness hard to believe. Do not ask for personal mistakes." },
    worship: { video: "y-worship-video", at: 440.5, label: "Video 1 · 7:21 · A choice you can make", seconds: 30, title: "What would help you participate when you don’t feel like it?", instruction: "Think of one choice you could make during sacrament meeting. Write it in section 2.", note: "Allow honest answers about distraction or uncertainty. Ask how one small choice could help someone remember Christ. Keep this pause brief; the discussion after the video gives more room to talk." },
    partner: { video: "y-learning-video", at: 153.2, label: "Video 2 · 2:33 · Talk with a partner", seconds: 45, title: "What’s a question about Jesus Christ or His gospel you’d like to explore?", instruction: "Share the question—or just where you’d start looking—with someone beside you. Give both people a turn. Use section 3 for a note.", note: "Keep nearby pairs seated. Listen without rushing to supply an answer. A student can write privately instead. If a question needs more time, identify a reliable Church source to explore after class." }
  };
  let current = "start", returnTo = "start", activeCue = null, shortClock = null;
  let classRemaining = 25 * 60 * 1000, classDeadline = 0, toastTimeout;
  const videoState = new Map(videos.map(video => [video.id, { seen: new Set(), last: 0, localURL: null }]));
  const formatTime = milliseconds => {
    const seconds = Math.max(0, Math.ceil(milliseconds / 1000));
    return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
  };
  function announce(message) { $("y-announcement").textContent = message; }
  function toast(message) {
    $("y-toast").textContent = message;
    $("y-toast").hidden = false;
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => { $("y-toast").hidden = true; }, 6500);
  }
  function pauseVideos() { videos.forEach(video => video.pause()); }
  function focusVisible(element) {
    if (!element || element.closest("[hidden]") || (element.closest("dialog") && !element.closest("dialog").open)) element = $("y-stage");
    element.focus({ preventScroll: true });
  }
  function openDialog(dialog, focusTarget, opener = document.activeElement) {
    pauseVideos();
    dialog.returnFocus = opener;
    if (!dialog.open) dialog.showModal();
    (focusTarget || dialog).focus({ preventScroll: true });
  }
  dialogs.forEach(dialog => {
    dialog.addEventListener("close", () => {
      if (dialog.id === "y-cue") { activeCue = null; clearShortClock(); }
      focusVisible(dialog.returnFocus);
    });
    dialog.addEventListener("click", event => {
      if (event.target !== dialog) return;
      const bounds = dialog.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
    });
  });
  function loadOnline(video) {
    const source = video.querySelector("source");
    if (!source.getAttribute("src")) { source.src = source.dataset.src; video.load(); }
  }
  function show(id) {
    if (![...order, "psalm"].includes(id)) return;
    if (id === "psalm" && order.includes(current)) returnTo = current;
    const moveFocus = Boolean(document.activeElement?.closest(".scene"));
    pauseVideos();
    dialogs.forEach(dialog => { if (dialog.open) dialog.close(); });
    clearShortClock();
    all(".video-tools details").forEach(details => { details.open = false; });
    current = id;
    scenes.forEach(scene => { scene.hidden = scene.id !== id; });
    $("y-section").value = id;
    const index = order.indexOf(id);
    $("y-previous").disabled = index === 0;
    $("y-next").disabled = index === order.length - 1;
    $("y-next").textContent = id === "psalm" ? "Return to lesson →" : id === "start" ? "Let’s watch →" : ["worship", "learning"].includes(id) ? "Let’s talk →" : id === "finish" ? "Finished" : "Next →";
    $("y-step-count").textContent = index < 0 ? "Extra" : `${index + 1} / 6`;
    $("y-progress").style.width = `${((index < 0 ? order.indexOf(returnTo) : index) + 1) / order.length * 100}%`;
    $("y-psalm-open").textContent = id === "psalm" ? "Back to lesson" : "Psalms extra";
    $("teacher-section").textContent = notes[id][0];
    $("teacher-note").textContent = notes[id][1];
    const video = $(id).querySelector("video");
    if (video && !videoState.get(video.id).localURL) loadOnline(video);
    history.replaceState(null, "", `#${id}`);
    announce(notes[id][0]);
    window.scrollTo({ top: 0, behavior: "instant" });
    if (moveFocus) focusVisible($("y-stage"));
  }
  function advance(direction) {
    if (current === "psalm") return show(returnTo);
    show(order[Math.max(0, Math.min(order.length - 1, order.indexOf(current) + direction))]);
  }
  $("y-next").addEventListener("click", () => advance(1));
  $("y-previous").addEventListener("click", () => advance(-1));
  $("y-section").addEventListener("change", event => show(event.target.value));
  $("y-psalm-open").addEventListener("click", () => show(current === "psalm" ? returnTo : "psalm"));
  window.addEventListener("hashchange", () => show(location.hash.slice(1)));

  function choose(selector, attribute, responseID, prompts) {
    all(selector).forEach(button => button.addEventListener("click", () => {
      all(selector).forEach(other => other.setAttribute("aria-pressed", String(other === button)));
      $(responseID).textContent = prompts[button.dataset[attribute]];
    }));
  }
  choose("[data-warmup]", "warmup", "warmup-response", {
    space: "What helps you slow down enough to notice what God may be teaching you?",
    restart: "What does the sacrament mean after a week you wish had gone differently?",
    belonging: "What helps a person feel wanted at church?"
  });
  choose("[data-action]", "action", "action-response", {
    distracted: "You’re at church, but your mind is on school, work, or your phone. What could help you turn your attention to Christ?",
    hardweek: "You’ve had a week you wish you could redo. How might remembering Christ during the sacrament affect what you do next?",
    belonging: "A friend says, “I don’t feel like I fit in at church.” What would you want to understand before offering advice?"
  });
  $("home-ideas").addEventListener("click", () => {
    const expanded = $("home-ideas").getAttribute("aria-expanded") !== "true";
    $("home-ideas").setAttribute("aria-expanded", String(expanded));
    $("home-examples").hidden = !expanded;
    $("home-ideas").textContent = expanded ? "Hide ideas" : "Ways to get started";
  });
  const reflectionPrompts = {
    word: "Where could you turn to hear God’s word as you think about this decision?",
    lamp: "What might a lamp help you see? What might still be out of sight?",
    path: "What is one step you could take without knowing how everything will turn out?"
  };
  choose("[data-reflection]", "reflection", "psalm-feedback", reflectionPrompts);
  function resetReflection() {
    all("[data-reflection]").forEach(button => button.setAttribute("aria-pressed", "false"));
    $("psalm-feedback").textContent = "Choose a phrase to talk about.";
  }
  $("psalm-reset").addEventListener("click", resetReflection);
  all("[data-scripture]").forEach(link => link.addEventListener("click", event => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button > 0) return;
    event.preventDefault();
    openDialog($("y-scripture"), $("y-scripture-title"), link);
  }));
  $("y-scripture-close").addEventListener("click", () => $("y-scripture").close());
  $("y-teacher-open").addEventListener("click", () => openDialog($("y-teacher"), $("teacher-close")));
  $("teacher-close").addEventListener("click", () => $("y-teacher").close());

  function renderClassClock() {
    $("y-class-time").textContent = formatTime(classRemaining);
    $("y-class-symbol").textContent = classDeadline ? "Ⅱ" : "▶";
    $("y-class-timer").setAttribute("aria-label", `${classDeadline ? "Pause" : classRemaining ? "Start" : "Restart"} class timer, ${formatTime(classRemaining)} remaining`);
    $("y-class-timer").classList.toggle("running", Boolean(classDeadline));
    $("y-class-timer").classList.toggle("ending", classRemaining <= 120000);
  }
  function updateClassClock() {
    if (!classDeadline) return;
    classRemaining = Math.max(0, classDeadline - Date.now());
    if (!classRemaining) { classDeadline = 0; toast("Time to close with prayer."); }
    renderClassClock();
  }
  $("y-class-timer").addEventListener("click", () => {
    const wasRunning = Boolean(classDeadline);
    updateClassClock();
    if (wasRunning) classDeadline = 0;
    else { if (!classRemaining) classRemaining = 25 * 60 * 1000; classDeadline = Date.now() + classRemaining; }
    renderClassClock();
  });
  $("y-reset-timer").addEventListener("click", () => {
    classRemaining = 25 * 60 * 1000; classDeadline = 0;
    renderClassClock(); toast("Class timer reset to 25:00.");
  });
  function clearShortClock() {
    shortClock = null;
    $("discuss-countdown").textContent = "1:15";
    all("[data-short-timer]").forEach(button => { button.textContent = "Start 75 seconds"; });
  }
  function renderShortClock() {
    if (!shortClock) return;
    shortClock.output.textContent = formatTime(shortClock.remaining);
    shortClock.button.textContent = shortClock.deadline ? "Pause timer" : shortClock.remaining === 0 ? "Start again" : shortClock.remaining === shortClock.total ? `Start ${shortClock.total / 1000} seconds` : "Resume timer";
  }
  function updateShortClock() {
    if (!shortClock?.deadline) return;
    shortClock.remaining = Math.max(0, shortClock.deadline - Date.now());
    if (!shortClock.remaining) { shortClock.deadline = 0; announce("Time’s up. Finish your thought."); }
    renderShortClock();
  }
  function toggleShortClock(button, output, seconds) {
    if (!shortClock || shortClock.button !== button) shortClock = { button, output, total: seconds * 1000, remaining: seconds * 1000, deadline: 0 };
    const wasRunning = Boolean(shortClock.deadline);
    updateShortClock();
    if (wasRunning) shortClock.deadline = 0;
    else { if (!shortClock.remaining) shortClock.remaining = shortClock.total; shortClock.deadline = Date.now() + shortClock.remaining; }
    renderShortClock();
  }
  all("[data-short-timer]").forEach(button => button.addEventListener("click", () => toggleShortClock(button, $("discuss-countdown"), Number(button.dataset.shortTimer))));
  $("cue-timer").addEventListener("click", () => {
    if (activeCue) toggleShortClock($("cue-timer"), $("cue-time"), cues[activeCue.key].seconds);
  });
  setInterval(() => { updateClassClock(); updateShortClock(); }, 250);

  async function openCue(key, preview = false) {
    const cue = cues[key], video = $(cue.video), sceneAtPause = current;
    pauseVideos();
    // Native video fullscreen cannot contain an HTML dialog; page fullscreen can.
    if (document.fullscreenElement === video) {
      try { await document.exitFullscreen(); } catch { toast("Exit video fullscreen to see the pause prompt."); }
    }
    if (video.webkitDisplayingFullscreen && video.webkitExitFullscreen) video.webkitExitFullscreen();
    if (!preview && current !== sceneAtPause) return;
    clearShortClock();
    activeCue = { key, preview };
    $("cue-label").textContent = `${preview ? "Preview · " : ""}${cue.label}`;
    $("cue-title").textContent = cue.title;
    $("cue-instruction").textContent = cue.instruction;
    $("cue-note").textContent = cue.note;
    $("cue-time").textContent = formatTime(cue.seconds * 1000);
    $("cue-timer").textContent = `Start ${cue.seconds} seconds`;
    $("cue-continue").textContent = preview ? "Close preview" : "Continue video →";
    $("y-cue").querySelector("details").open = false;
    openDialog($("y-cue"), $("cue-title"), preview ? $("y-teacher-open") : video);
  }
  $("cue-close").addEventListener("click", () => $("y-cue").close());
  $("cue-continue").addEventListener("click", () => {
    const cueToResume = activeCue;
    $("y-cue").close();
    if (cueToResume && !cueToResume.preview) $(cues[cueToResume.key].video).play().catch(() => toast("Press Play on the video to continue."));
  });
  all("[data-preview-cue]").forEach(button => button.addEventListener("click", () => {
    $("y-teacher").close();
    openCue(button.dataset.previewCue, true);
  }));
  function markPastCues(video) {
    const state = videoState.get(video.id);
    Object.entries(cues).forEach(([key, cue]) => { if (cue.video === video.id && cue.at <= video.currentTime) state.seen.add(key); });
    state.last = video.currentTime;
  }
  videos.forEach(video => {
    const state = videoState.get(video.id);
    video.addEventListener("seeked", () => markPastCues(video));
    video.addEventListener("timeupdate", () => {
      const previous = state.last;
      state.last = video.currentTime;
      if (video.seeking || video.paused || video.closest(".scene").hidden) return;
      const passed = Object.entries(cues).filter(([key, cue]) => cue.video === video.id && !state.seen.has(key) && previous < cue.at && video.currentTime >= cue.at);
      passed.forEach(([key]) => state.seen.add(key));
      if (passed.length && $("guided-pauses").checked && !dialogs.some(dialog => dialog.open)) openCue(passed[0][0]);
    });
    video.addEventListener("ended", () => { markPastCues(video); announce("Video finished. Choose Let’s talk to continue."); });
    const error = $(video.id.replace("-video", "-error"));
    video.addEventListener("error", () => { error.hidden = false; });
    video.querySelector("source").addEventListener("error", () => { error.hidden = false; });
    video.addEventListener("loadeddata", () => { error.hidden = true; });
  });
  all("[data-local-video]").forEach(input => input.addEventListener("change", () => {
    const file = input.files?.[0];
    if (!file) return;
    if (file.type && !file.type.startsWith("video/")) { toast("Choose a video file."); input.value = ""; return; }
    const video = $(input.dataset.localVideo), state = videoState.get(video.id);
    video.pause();
    if (state.localURL) URL.revokeObjectURL(state.localURL);
    state.localURL = URL.createObjectURL(file);
    state.seen.clear(); state.last = 0;
    video.src = state.localURL; video.load();
    $(video.id.replace("-video", "-file")).textContent = `Using ${file.name}. This file stays on your device.`;
    all("[data-online-video]").find(button => button.dataset.onlineVideo === video.id).hidden = false;
  }));
  all("[data-online-video]").forEach(button => button.addEventListener("click", () => {
    const video = $(button.dataset.onlineVideo), state = videoState.get(video.id);
    video.pause(); video.removeAttribute("src");
    if (state.localURL) URL.revokeObjectURL(state.localURL);
    state.localURL = null; state.seen.clear(); state.last = 0;
    video.querySelector("source").src = video.querySelector("source").dataset.src;
    video.load();
    $(video.id.replace("-video", "-file")).textContent = "Using the online video.";
    all("[data-local-video]").find(input => input.dataset.localVideo === video.id).value = "";
    button.hidden = true;
  }));

  async function toggleFullscreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await $("y-app").requestFullscreen();
    } catch { toast("Fullscreen is unavailable here. Use your browser’s presentation or zoom controls."); }
  }
  $("y-fullscreen").addEventListener("click", toggleFullscreen);
  document.addEventListener("fullscreenchange", () => {
    const active = document.fullscreenElement === $("y-app");
    $("y-fullscreen").setAttribute("aria-pressed", String(active));
    $("y-fullscreen").textContent = active ? "Exit fullscreen" : "Fullscreen";
  });
  document.addEventListener("keydown", event => {
    if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey || dialogs.some(dialog => dialog.open) || event.target.closest("input,select,textarea,video,summary,[contenteditable]")) return;
    if (["ArrowRight", "PageDown", "ArrowLeft", "PageUp", "Home", "End", "f", "F"].includes(event.key)) event.preventDefault();
    if (["ArrowRight", "PageDown"].includes(event.key)) advance(1);
    if (["ArrowLeft", "PageUp"].includes(event.key)) advance(-1);
    if (event.key === "Home") show("start");
    if (event.key === "End") show("finish");
    if (["f", "F"].includes(event.key)) toggleFullscreen();
  });
  window.addEventListener("pagehide", pauseVideos);
  resetReflection();
  renderClassClock();
  show([...order, "psalm"].includes(location.hash.slice(1)) ? location.hash.slice(1) : "start");
})();
