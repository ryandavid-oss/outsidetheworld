"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const sequence = ["welcome", "worship", "renewal", "learning", "together", "take-home"];
  const optionalMoments = ["psalms", "praise", "lamp", "connections", "puzzle", "reflection"];
  const labels = { welcome: "Welcome", worship: "Sacrament meeting", renewal: "Discuss worship", learning: "Sunday School", together: "Discuss learning", "take-home": "At home", psalms: "Psalms moment", praise: "Praise wall", lamp: "Psalm 119:105", connections: "Find Christ in the Psalms", puzzle: "Finish the verse", reflection: "A lamp for our feet" };
  const slides = Array.from(document.querySelectorAll(".slide"));
  const videos = Array.from(document.querySelectorAll("video"));
  const guide = $("lesson-guide");
  const scriptureReader = $("scripture-reader");
  const cueDialog = $("lesson-cue");
  let scriptureOpener = null;
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

  // Stops fall between sentences in the supplied English captions.
  const cues = {
    forgiveness: { video: "sabbath-video", at: 188, label: "Video 1 · 3:08 · A moment to think", seconds: 30, title: "What did you hear about the Savior’s willingness to forgive?", instruction: "Take a quiet moment to think.", note: "Allow 30 seconds. Invite one brief thought if someone wants to share." },
    worship: { video: "sabbath-video", at: 440.5, label: "Video 1 · 7:21 · Looking ahead", seconds: 30, title: "What could help you worship more fully next Sunday?", instruction: "Think of one change you could make.", note: "Take one or two brief responses." },
    partner: { video: "school-video", at: 153.2, label: "Video 2 · 2:33 · Talk with someone nearby", seconds: 45, title: "What could you study at home and bring to class?", instruction: "Share one idea with someone nearby.", note: "Give each person a turn. Keep the whole conversation to 45 seconds." }
  };
  const pauseState = new Map(videos.map(video => [video.id, { seen: new Set(), last: 0 }]));
  let activeCue = null, cueRequest = 0, cueInterval = null, cueDeadline = null, cueRemaining = 0;
  const formatCueTime = milliseconds => {
    const seconds = Math.max(0, Math.ceil(milliseconds / 1000));
    return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
  };
  function stopCueClock() {
    clearInterval(cueInterval);
    cueInterval = null;
    cueDeadline = null;
  }
  function closeCue() {
    cueRequest += 1; // Also cancel a prompt waiting for native fullscreen to exit.
    stopCueClock();
    activeCue = null;
    if (cueDialog.open) cueDialog.close();
  }
  function paintCueClock() {
    if (!activeCue) return;
    if (cueDeadline !== null) {
      cueRemaining = Math.max(0, cueDeadline - Date.now());
      if (!cueRemaining) {
        stopCueClock();
        $("slide-announcement").textContent = "Finish your thought when you’re ready.";
      }
    }
    $("cue-time").textContent = formatCueTime(cueRemaining);
    const total = cues[activeCue.key].seconds * 1000;
    $("cue-timer").textContent = cueDeadline !== null ? "Pause timer" : !cueRemaining ? "Start again" : cueRemaining === total ? `Start ${total / 1000} seconds` : "Resume timer";
  }
  $("cue-timer").addEventListener("click", () => {
    if (!activeCue) return;
    const wasRunning = cueDeadline !== null;
    paintCueClock();
    if (wasRunning) stopCueClock();
    else {
      if (!cueRemaining) cueRemaining = cues[activeCue.key].seconds * 1000;
      cueDeadline = Date.now() + cueRemaining;
      cueInterval = setInterval(paintCueClock, 250);
    }
    paintCueClock();
  });
  async function openCue(key, preview = false) {
    const cue = cues[key], video = $(cue.video), section = current;
    const request = ++cueRequest;
    videos.forEach(item => item.pause());
    // Native video fullscreen cannot contain the prompt; page fullscreen can.
    if (document.fullscreenElement === video) {
      try { await document.exitFullscreen(); } catch (_) { notify("Exit video fullscreen to see the prompt."); }
    }
    if (video.webkitDisplayingFullscreen && video.webkitExitFullscreen) video.webkitExitFullscreen();
    if (request !== cueRequest || current !== section || guide.open || scriptureReader.open || cueDialog.open) return;
    stopCueClock();
    video.pause();
    activeCue = { key, preview };
    cueRemaining = cue.seconds * 1000;
    $("cue-label").textContent = `${preview ? "Preview · " : ""}${cue.label}`;
    $("cue-title").textContent = cue.title;
    $("cue-instruction").textContent = cue.instruction;
    $("cue-note").textContent = cue.note;
    $("cue-continue").textContent = preview ? "Close preview" : "Continue video →";
    cueDialog.querySelector("details").open = false;
    cueDialog.returnFocus = preview ? $("guide-toggle") : video;
    paintCueClock();
    if (!cueDialog.open) cueDialog.showModal();
    $("cue-title").focus({ preventScroll: true });
  }
  $("cue-close").addEventListener("click", closeCue);
  $("cue-continue").addEventListener("click", () => {
    const resume = activeCue;
    closeCue();
    if (resume && !resume.preview) {
      const video = $(cues[resume.key].video);
      if (!video.closest(".slide").hidden) video.play().catch(() => notify("Press Play on the video to continue."));
    }
  });
  cueDialog.addEventListener("cancel", event => { event.preventDefault(); closeCue(); });
  cueDialog.addEventListener("click", event => {
    if (event.target !== cueDialog) return;
    const bounds = cueDialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) closeCue();
  });
  cueDialog.addEventListener("close", () => {
    if (cueDialog.open) return;
    closeCue();
    const opener = cueDialog.returnFocus;
    if (opener && !opener.closest(".slide")?.hidden) opener.focus({ preventScroll: true });
    else $("stage").focus({ preventScroll: true });
  });
  document.querySelectorAll("[data-preview-cue]").forEach(button => button.addEventListener("click", () => {
    guide.close();
    openCue(button.dataset.previewCue, true);
  }));
  function resetVideoCues(video) {
    const state = pauseState.get(video.id);
    state.seen.clear();
    state.last = 0;
    closeCue();
  }
  function markPastCues(video) {
    const state = pauseState.get(video.id);
    Object.entries(cues).forEach(([key, cue]) => {
      if (cue.video === video.id && cue.at <= video.currentTime) state.seen.add(key);
    });
    state.last = video.currentTime;
  }
  videos.forEach(video => {
    const state = pauseState.get(video.id);
    video.addEventListener("seeked", () => markPastCues(video));
    video.addEventListener("timeupdate", () => {
      const previous = state.last;
      state.last = video.currentTime;
      if (video.seeking || video.paused || video.closest(".slide").hidden) return;
      const passed = Object.entries(cues).filter(([key, cue]) => cue.video === video.id && !state.seen.has(key) && previous < cue.at && video.currentTime >= cue.at);
      passed.forEach(([key]) => state.seen.add(key));
      if (passed.length && $("guided-pauses").checked && !guide.open && !scriptureReader.open && !cueDialog.open) openCue(passed[0][0]);
    });
    video.addEventListener("ended", () => markPastCues(video));
  });

  function activateVideo(video) {
    if (!video || video.dataset.initialized) return;
    const source = video.querySelector("source");
    source.src = source.dataset.src;
    video.dataset.initialized = "true";
    video.load();
  }

  function show(id, updateHash = true) {
    if (!Object.hasOwn(labels, id)) return;
    closeCue();
    if (scriptureReader.open) scriptureReader.close();
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
    $("next").disabled = false;
    $("next").textContent = isOptional ? "Return to lesson →" : id === "welcome" ? "Begin →" : (id === "worship" || id === "learning") ? "Discuss →" : id === "take-home" ? "Back to start" : "Next →";
    $("lesson-progress").style.width = (isOptional ? (sequence.indexOf(returnFromMoment) + 1) : index + 1) / sequence.length * 100 + "%";
    $("slide-announcement").textContent = (index >= 0 ? `${index + 1} of ${sequence.length}. ` : "Optional. ") + labels[id];
    activateVideo($(id).querySelector("video"));
    if (updateHash) {
      try { history.replaceState(null, "", "#" + id); } catch (_) { /* The lesson still works when history is unavailable. */ }
    }
    if (focusWasInSlide) $("stage").focus({ preventScroll: true });
    window.scrollTo({ top: 0, behavior: "instant" });
  }

  function backToStart() {
    const heading = $("welcome-title");
    scriptureOpener = heading;
    cueDialog.returnFocus = heading;
    videos.forEach((video) => video.pause());
    if (guide.open) guide.close();
    returnFromMoment = "welcome";
    show("welcome");
    $("presentation").scrollTo?.({ top: 0, left: 0, behavior: "instant" });
    heading.focus({ preventScroll: true });
  }
  document.querySelectorAll("[data-lesson-start]").forEach((button) => button.addEventListener("click", backToStart));
  function advance(direction) {
    if (current === "take-home" && direction > 0) { backToStart(); return; }
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
    closeCue();
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

  const { scriptureFor, renderScripture } = window.CFMExtras;

  document.querySelectorAll("[data-scripture]").forEach((link) => {
    link.addEventListener("click", (event) => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || (event.button !== undefined && event.button !== 0)) return;
      const passage = scriptureFor(link.href);
      if (!passage) return; // Keep the original Church link usable if a passage is not included.
      event.preventDefault();
      closeCue();
      scriptureOpener = link;
      videos.forEach((video) => video.pause());
      $("scripture-reader-title").textContent = passage.title;
      $("scripture-reader-source").href = link.href;
      const content = $("scripture-reader-body");
      renderScripture(content, passage);
      scriptureReader.showModal();
      document.body.classList.toggle("scripture-reading", true);
      content.scrollTop = 0;
      $("scripture-reader-title").focus({ preventScroll: true });
    });
  });
  $("scripture-reader-close").addEventListener("click", () => scriptureReader.close());
  scriptureReader.addEventListener("cancel", (event) => { event.preventDefault(); scriptureReader.close(); });
  scriptureReader.addEventListener("click", (event) => {
    if (event.target !== scriptureReader) return;
    const rect = scriptureReader.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) scriptureReader.close();
  });
  scriptureReader.addEventListener("close", () => {
    document.body.classList.toggle("scripture-reading", false);
    if (scriptureOpener && document.contains(scriptureOpener) && !scriptureOpener.closest(".slide")?.hidden) scriptureOpener.focus({ preventScroll: true });
  });

  document.querySelectorAll("[data-reveal]").forEach((button) => {
    button.addEventListener("click", () => {
      const content = $(button.dataset.reveal);
      content.hidden = !content.hidden;
      button.setAttribute("aria-expanded", String(!content.hidden));
      button.innerHTML = content.hidden ? 'Another question <span aria-hidden="true">+</span>' : 'Hide question <span aria-hidden="true">−</span>';
    });
  });

  window.CFMExtras.init({
    announce: message => { $("slide-announcement").textContent = message; },
    notify,
    returnToLesson: () => show(returnFromMoment)
  });

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
    if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || guide.open || scriptureReader.open || cueDialog.open) return;
    if (event.key === "Escape" && $("moments-menu").open) { $("moments-menu").open = false; $("moments-menu").querySelector("summary").focus(); return; }
    if (event.target instanceof Element && event.target.closest("input, select, textarea, video, summary, [contenteditable]")) return;
    if (event.key === "ArrowRight" || event.key === "PageDown") { event.preventDefault(); advance(1); }
    else if (event.key === "ArrowLeft" || event.key === "PageUp") { event.preventDefault(); advance(-1); }
    else if (event.key === "Home") { event.preventDefault(); backToStart(); }
    else if (event.key === "End") { event.preventDefault(); show("take-home"); }
    else if (event.key.toLowerCase() === "f") { event.preventDefault(); toggleFullscreen(); }
  });

  function errorFor(video) { return $(video.id === "sabbath-video" ? "sabbath-error" : "school-error"); }
  function fileStatusFor(video) { return $(video.id === "sabbath-video" ? "sabbath-file-status" : "school-file-status"); }
  videos.forEach((video) => {
    video.addEventListener("error", () => { errorFor(video).hidden = false; });
    video.querySelector("source").addEventListener("error", () => { errorFor(video).hidden = false; });
    video.addEventListener("loadeddata", () => { errorFor(video).hidden = true; });
    video.addEventListener("play", () => { if (guide.open || scriptureReader.open || cueDialog.open) video.pause(); videos.forEach((other) => { if (other !== video) other.pause(); }); });
    video.addEventListener("ended", () => { $("slide-announcement").textContent = "Video finished. Select Discuss to continue."; });
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
      resetVideoCues(video);
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
      resetVideoCues(video);
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
  window.addEventListener("pagehide", () => { closeCue(); videos.forEach((video) => video.pause()); });
  paintTimer();
  const initialId = location.hash.slice(1);
  show(Object.hasOwn(labels, initialId) ? initialId : "welcome", false);
})();
