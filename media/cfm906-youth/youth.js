"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const all = selector => [...document.querySelectorAll(selector)];
  const order = ["start", "worship", "discuss", "learning", "home-study", "finish"];
  const optional = ["psalm", "psalms", "praise", "lamp", "connections", "reflection"];
  const scenes = all(".scene"), videos = all("video"), dialogs = all("dialog");
  const notes = {
    start: ["Welcome · 1 minute", "Let students hold up a number or simply think. Take one short response, then invite an opening prayer. Start the class timer when class begins."],
    worship: ["First video · 12:23 with stops", "Play the complete video. The first stop is for box 1 on the handout; the second is for box 2. Keep each to about 30 seconds. You choose when to continue."],
    discuss: ["Discuss sacrament meeting · 1 minute", "Ask how sacrament meeting can help us come closer to Jesus. Use the choices if students need a starting point. Take two or three brief answers."],
    learning: ["Second video · 5:07 with stop", "Play the complete video. At the partner stop, keep everyone seated: 22 students make 11 pairs. Each person shares one idea. Allow 45 seconds for both people together."],
    "home-study": ["Discuss learning at home · 1 minute", "Ask what students could learn about Jesus at home and bring back to class. Take two short ideas. Use Need an idea? if the class needs help getting started."],
    finish: ["Write a plan and close · 1 minute", "Give students a quiet moment to finish the last line. They do not need to share it. Close with prayer and help everyone move to the next class on time."],
    psalm: ["Finish the verse · 1 minute", "Read the verse, then fill in the blanks. Ask for one example of how a scripture has helped someone."],
    psalms: ["Psalms moment · 1 minute", "Choose a situation. Read the passage and ask which words could help."],
    praise: ["Praise wall · 30–60 seconds", "Type a few words from the class. Click a word to remove it."],
    lamp: ["One phrase at a time · 1 minute", "Reveal the verse slowly. Choose one question to discuss."],
    connections: ["Find Christ · 1–2 minutes", "Match a psalm to the New Testament. One passage is enough if time is short."],
    reflection: ["A lamp for our feet · 1 minute", "Read the verse. Choose a phrase and take one or two thoughts."]
  };
  // Checkpoints fall in gaps between sentences in the supplied English captions.
  const cues = {
    forgiveness: { video: "y-worship-video", at: 188, label: "Video 1 · 3:08 · Write or draw", seconds: 30, title: "What did they say about Jesus forgiving us?", instruction: "Jot down a few words or draw something in box 1.", note: "If cards are not already on chairs, ask two helpers to pass them out here. Ask one or two students what they noticed. No one needs to share a personal story." },
    worship: { video: "y-worship-video", at: 440.5, label: "Video 1 · 7:21 · Choose one", seconds: 30, title: "What could help you think about Jesus during sacrament meeting?", instruction: "You could sing, pray, listen, or help someone feel welcome. Pick one for box 2.", note: "Invite a quick show of hands or two brief answers. Ask how that choice could help them remember Jesus. Keep this stop to about 30 seconds." },
    partner: { video: "y-learning-video", at: 153.2, label: "Video 2 · 2:33 · Talk with a partner", seconds: 45, title: "What’s one way you could learn about Jesus at home?", instruction: "Turn to the person next to you. Share an idea, then let them have a turn. Jot one down in box 3.", note: "Keep students seated in 11 nearby pairs. Give both people a turn within 45 seconds. If attendance is odd, use one group of three. A student may write instead of speaking." }
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
    if (![...order, ...optional].includes(id)) return;
    if (optional.includes(id) && order.includes(current)) returnTo = current;
    const moveFocus = Boolean(document.activeElement?.closest(".scene")) || $("moments-menu").contains(document.activeElement);
    pauseVideos();
    dialogs.forEach(dialog => { if (dialog.open) dialog.close(); });
    clearShortClock();
    $("moments-menu").open = false;
    all(".video-tools details").forEach(details => { details.open = false; });
    current = id;
    scenes.forEach(scene => { scene.hidden = scene.id !== id; });
    $("y-section").value = id;
    const index = order.indexOf(id);
    $("y-previous").disabled = index === 0;
    $("y-next").disabled = false;
    $("y-next").textContent = optional.includes(id) ? "Return to lesson →" : id === "start" ? "Let’s watch →" : ["worship", "learning"].includes(id) ? "Let’s talk →" : id === "finish" ? "Back to start" : "Next →";
    $("y-step-count").textContent = index < 0 ? "Extra" : `${index + 1} / 6`;
    $("y-progress").style.width = `${((index < 0 ? order.indexOf(returnTo) : index) + 1) / order.length * 100}%`;
    $("teacher-section").textContent = notes[id][0];
    $("teacher-note").textContent = notes[id][1];
    const video = $(id).querySelector("video");
    if (video && !videoState.get(video.id).localURL) loadOnline(video);
    try { history.replaceState(null, "", `#${id}`); } catch { /* Keep navigation usable when history is unavailable. */ }
    announce(notes[id][0]);
    window.scrollTo({ top: 0, behavior: "instant" });
    if (moveFocus) focusVisible($("y-stage"));
  }
  function backToStart() {
    const heading = $("start-title");
    // Dialog close events run later; send their focus back to the opening screen too.
    dialogs.forEach(dialog => { dialog.returnFocus = heading; });
    activeCue = null;
    returnTo = "start";
    show("start");
    $("y-app").scrollTo?.({ top: 0, left: 0, behavior: "instant" });
    heading.focus({ preventScroll: true });
  }
  all("[data-lesson-start]").forEach(button => button.addEventListener("click", backToStart));
  function advance(direction) {
    if (current === "finish" && direction > 0) return backToStart();
    if (optional.includes(current)) return show(returnTo);
    show(order[Math.max(0, Math.min(order.length - 1, order.indexOf(current) + direction))]);
  }
  $("y-next").addEventListener("click", () => advance(1));
  $("y-previous").addEventListener("click", () => advance(-1));
  $("y-section").addEventListener("change", event => show(event.target.value));
  all("[data-moment]").forEach(button => button.addEventListener("click", () => show(button.dataset.moment)));
  document.addEventListener("click", event => {
    if (!$("moments-menu").contains(event.target)) $("moments-menu").open = false;
  });
  window.addEventListener("hashchange", () => show(location.hash.slice(1)));

  function choose(selector, attribute, responseID, prompts) {
    all(selector).forEach(button => button.addEventListener("click", () => {
      all(selector).forEach(other => other.setAttribute("aria-pressed", String(other === button)));
      $(responseID).textContent = prompts[button.dataset[attribute]];
    }));
  }
  choose("[data-warmup]", "warmup", "warmup-response", { song: "Which song did you think of?", scripture: "What stood out to you in that scripture?", kindness: "What did that person do?" });
  choose("[data-action]", "action", "action-response", { prepare: "What could help you get ready for the sacrament?", listen: "What could help you listen when it’s hard to pay attention?", welcome: "What could you say to someone who’s sitting alone?" });
  $("home-ideas").addEventListener("click", () => {
    const expanded = $("home-ideas").getAttribute("aria-expanded") !== "true";
    $("home-ideas").setAttribute("aria-expanded", String(expanded));
    $("home-examples").hidden = !expanded;
    $("home-ideas").textContent = expanded ? "Hide ideas" : "Need an idea?";
  });
  window.CFMExtras.init({ announce, notify: toast, returnToLesson: () => show(returnTo) });
  all("[data-scripture]").forEach(link => link.addEventListener("click", event => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button > 0) return;
    const passage = window.CFMExtras.scriptureFor(link.href);
    if (!passage) return;
    event.preventDefault();
    $("y-scripture-title").textContent = passage.title;
    $("y-scripture-source").href = link.href;
    window.CFMExtras.renderScripture($("y-scripture-body"), passage);
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
    $("discuss-countdown").textContent = "1:00";
    all("[data-short-timer]").forEach(button => { button.textContent = "Start 60 seconds"; });
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
    if (event.key === "Home") backToStart();
    if (event.key === "End") show("finish");
    if (["f", "F"].includes(event.key)) toggleFullscreen();
  });
  window.addEventListener("pagehide", pauseVideos);
  renderClassClock();
  show([...order, ...optional].includes(location.hash.slice(1)) ? location.hash.slice(1) : "start");
})();
