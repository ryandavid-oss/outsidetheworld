"use strict";
(() => {
  // KJV verse text checked against the linked Church scripture pages, September 5, 2026.
  // Chapter headings and study notes are excluded; passages are included locally for immediate reading.
  const scriptureChapters = {
  "ot/ps/103": {
    "title": "Psalm 103",
    "verses": {
      "1": "Bless the Lord, O my soul: and all that is within me, bless his holy name.",
      "2": "Bless the Lord, O my soul, and forget not all his benefits:",
      "3": "Who forgiveth all thine iniquities; who healeth all thy diseases;",
      "4": "Who redeemeth thy life from destruction; who crowneth thee with lovingkindness and tender mercies;",
      "5": "Who satisfieth thy mouth with good things; so that thy youth is renewed like the eagle’s.",
      "8": "The Lord is merciful and gracious, slow to anger, and plenteous in mercy.",
      "9": "He will not always chide: neither will he keep his anger for ever.",
      "10": "He hath not dealt with us after our sins; nor rewarded us according to our iniquities.",
      "11": "For as the heaven is high above the earth, so great is his mercy toward them that fear him.",
      "12": "As far as the east is from the west, so far hath he removed our transgressions from us.",
      "13": "Like as a father pitieth his children, so the Lord pitieth them that fear him.",
      "14": "For he knoweth our frame; he remembereth that we are dust."
    }
  },
  "ot/ps/119": {
    "title": "Psalm 119",
    "verses": {
      "105": "Thy word is a lamp unto my feet, and a light unto my path."
    }
  },
  "ot/ps/118": {
    "title": "Psalm 118",
    "verses": {
      "22": "The stone which the builders refused is become the head stone of the corner.",
      "25": "Save now, I beseech thee, O Lord: O Lord, I beseech thee, send now prosperity.",
      "26": "Blessed be he that cometh in the name of the Lord: we have blessed you out of the house of the Lord."
    }
  },
  "ot/ps/110": {
    "title": "Psalm 110",
    "verses": {
      "4": "The Lord hath sworn, and will not repent, Thou art a priest for ever after the order of Melchizedek."
    }
  },
  "nt/matt/21": {
    "title": "Matthew 21",
    "verses": {
      "9": "And the multitudes that went before, and that followed, cried, saying, Hosanna to the Son of David: Blessed is he that cometh in the name of the Lord; Hosanna in the highest.",
      "42": "Jesus saith unto them, Did ye never read in the scriptures, The stone which the builders rejected, the same is become the head of the corner: this is the Lord’s doing, and it is marvellous in our eyes?"
    }
  },
  "nt/heb/5": {
    "title": "Hebrews 5",
    "verses": {
      "4": "And no man taketh this honour unto himself, but he that is called of God, as was Aaron.",
      "5": "So also Christ glorified not himself to be made an high priest; but he that said unto him, Thou art my Son, to day have I begotten thee.",
      "6": "As he saith also in another place, Thou art a priest for ever after the order of Melchisedec.",
      "7": "Who in the days of his flesh, when he had offered up prayers and supplications with strong crying and tears unto him that was able to save him from death, and was heard in that he feared;",
      "8": "Though he were a Son, yet learned he obedience by the things which he suffered;",
      "9": "And being made perfect, he became the author of eternal salvation unto all them that obey him;",
      "10": "Called of God an high priest after the order of Melchisedec."
    }
  }
};

  function scriptureFor(href) {
    let url;
    try { url = new URL(href); } catch (_) { return null; }
    if (url.origin !== "https://www.churchofjesuschrist.org") return null;
    const chapterId = url.pathname.replace("/study/scriptures/", "");
    if (!Object.hasOwn(scriptureChapters, chapterId)) return null;
    const chapter = scriptureChapters[chapterId];
    const range = /^p(\d+)(?:-p(\d+))?$/.exec(url.searchParams.get("id") || url.hash.slice(1));
    if (!chapter || !range) return null;
    const first = Number(range[1]);
    const last = Number(range[2] || range[1]);
    if (first > last || last - first > 30) return null;
    const verses = [];
    for (let number = first; number <= last; number += 1) {
      if (!Object.hasOwn(chapter.verses, number)) return null;
      verses.push({ number, text: chapter.verses[number] });
    }
    return { title: chapter.title + ":" + first + (last === first ? "" : "–" + last), verses };
  }

  function renderScripture(content, passage) {
    content.replaceChildren();
    passage.verses.forEach(verse => {
      const paragraph = document.createElement("p");
      const number = document.createElement("span");
      number.className = "scripture-verse-number";
      number.textContent = String(verse.number);
      number.setAttribute("aria-label", "Verse " + verse.number);
      const text = document.createElement("span");
      text.textContent = verse.text;
      paragraph.append(number, text);
      content.append(paragraph);
    });
    content.scrollTop = 0;
  }
  function init({ announce, notify, returnToLesson }) {
  const $ = id => document.getElementById(id);
  const all = selector => [...document.querySelectorAll(selector)];
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
    $("activity-reference").textContent = scenario.reference;
    $("activity-reference").href = scenario.url;
    $("activity-verse").textContent = scenario.verse;
    $("activity-verse").hidden = true;
    $("activity-invitation").hidden = false;
    $("reveal-scripture").textContent = "Show one verse";
    $("reveal-scripture").setAttribute("aria-expanded", "false");
  }
  document.querySelectorAll("[data-scenario]").forEach((button) => button.addEventListener("click", () => chooseScenario(button.dataset.scenario)));
  $("reveal-scripture").addEventListener("click", () => {
    const revealed = $("activity-verse").hidden;
    $("activity-verse").hidden = !revealed;
    $("activity-invitation").hidden = revealed;
    $("reveal-scripture").textContent = revealed ? "Hide verse" : "Show one verse";
    $("reveal-scripture").setAttribute("aria-expanded", String(revealed));
    if (revealed) announce(scenarios[selectedScenario].verseNumber + ". " + scenarios[selectedScenario].verse);
  });

  // Spoken responses stay in memory in this page, with no storage or network requests.
  const praiseWords = [];
  function paintPraise() {
    const wall = $("praise-wall");
    // Keep the first response prominent; allow more room for longer phrases and a fuller wall.
    const wordWeight = praiseWords.reduce((total, word) => total + Math.max(6, Array.from(word).length) / 6, 0);
    wall.style.setProperty("--praise-scale", (26 / Math.sqrt(Math.max(1, wordWeight))).toFixed(3));
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
        announce("Removed “" + word + "”.");
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
    if (praiseWords.length >= 12) { notify("12 words added. Remove one to add another."); return; }
    if (praiseWords.some((existing) => existing.toLocaleLowerCase() === word.toLocaleLowerCase())) { notify("That word is already on the wall."); return; }
    praiseWords.push(word);
    paintPraise();
    $("praise-word").value = "";
    $("praise-word").focus();
    announce("Added “" + word + "” to our praise.");
  });
  $("praise-reset").addEventListener("click", () => {
    praiseWords.length = 0;
    paintPraise();
    $("praise-word").value = "";
    $("praise-word").focus();
    announce("Words cleared.");
  });

  const lampPhrases = ["Thy word", "is a lamp unto my feet,", "and a light unto my path."];
  const lampQuestions = ["What word stands out to you?", "Which scripture has helped you recently?", "When has a scripture helped you make a decision?", "What will you do this week to follow Jesus Christ?"];
  let lampStep = 0;
  function paintLamp() {
    lampPhrases.forEach((_, index) => { $("lamp-phrase-" + (index + 1)).hidden = index >= lampStep; });
    document.querySelectorAll("[data-lamp-step]").forEach((step) => step.classList.toggle("is-lit", Number(step.dataset.lampStep) <= lampStep));
    $("lamp-placeholder").hidden = lampStep > 0;
    $("lamp-question").textContent = lampQuestions[lampStep];
    $("lamp-count").textContent = lampStep + " of 3 phrases";
    $("lamp-reveal").disabled = lampStep === 3;
    $("lamp-reveal").textContent = lampStep === 3 ? "Full verse shown" : lampStep === 0 ? "Show first phrase" : "Show next phrase";
    $("lamp-reset").disabled = lampStep === 0;
  }
  $("lamp-reveal").addEventListener("click", () => {
    if (lampStep >= 3) return;
    lampStep += 1;
    paintLamp();
    announce(lampPhrases[lampStep - 1]);
    if (lampStep === 3) $("lamp-reset").focus();
  });
  $("lamp-reset").addEventListener("click", () => { lampStep = 0; paintLamp(); $("lamp-reveal").focus(); });

  const connections = [
    { reference: "Psalm 118:22", url: "ot/ps/118?lang=eng&id=p22#p22", verse: "“The stone which the builders refused is become the head stone of the corner.”", answer: "Matthew 21:42", answerUrl: "nt/matt/21?lang=eng&id=p42#p42", explanation: "Jesus quotes this psalm as He teaches about the rejected stone. What does it mean to build your life on Him?" },
    { reference: "Psalm 118:25–26", url: "ot/ps/118?lang=eng&id=p25-p26#p25", verse: "“Blessed be he that cometh in the name of the Lord.” (verse 26)", answer: "Matthew 21:9", answerUrl: "nt/matt/21?lang=eng&id=p9#p9", explanation: "The crowd uses these words as Jesus enters Jerusalem. How can we show our love for Him?" },
    { reference: "Psalm 110:4", url: "ot/ps/110?lang=eng&id=p4#p4", verse: "“Thou art a priest for ever after the order of Melchizedek.”", answer: "Hebrews 5:4–10", answerUrl: "nt/heb/5?lang=eng&id=p4-p10#p4", explanation: "Hebrews identifies Jesus Christ as the high priest described in this psalm. What do these verses teach about His obedience and power to save?" },
  ];
  const connectionChoices = Array.from(document.querySelectorAll("[data-connection]"));
  let connectionIndex = 0;
  let connectionRevealed = false;
  function paintConnection() {
    const item = connections[connectionIndex];
    connectionRevealed = false;
    $("connection-count").textContent = "Passage " + (connectionIndex + 1) + " of 3";
    $("connection-reference").textContent = "Read " + item.reference;
    $("connection-reference").href = "https://www.churchofjesuschrist.org/study/scriptures/" + item.url;
    $("connection-verse").textContent = item.verse;
    $("connection-answer-reference").textContent = "Read " + item.answer;
    $("connection-answer-reference").href = "https://www.churchofjesuschrist.org/study/scriptures/" + item.answerUrl;
    $("connection-explanation").textContent = item.explanation;
    $("connection-answer").hidden = true;
    $("connection-feedback").textContent = "";
    $("connection-reveal").hidden = false;
    $("connection-next").hidden = true;
    $("connection-next").textContent = connectionIndex === connections.length - 1 ? "Return to lesson →" : "Next passage →";
    connectionChoices.forEach((button) => { button.disabled = false; button.setAttribute("aria-pressed", "false"); button.classList.toggle("is-match", false); });
  }
  function revealConnection() {
    connectionRevealed = true;
    $("connection-answer").hidden = false;
    $("connection-feedback").textContent = "";
    $("connection-reveal").hidden = true;
    $("connection-next").hidden = false;
    connectionChoices.forEach((button, index) => { button.disabled = true; button.classList.toggle("is-match", index === connectionIndex); button.setAttribute("aria-pressed", String(index === connectionIndex)); });
    announce(connections[connectionIndex].answer + ". " + connections[connectionIndex].explanation);
    $("connection-next").focus({ preventScroll: true });
  }
  connectionChoices.forEach((button, index) => button.addEventListener("click", () => {
    if (connectionRevealed) return;
    connectionChoices.forEach((choice) => choice.setAttribute("aria-pressed", String(choice === button)));
    if (index === connectionIndex) revealConnection();
    else $("connection-feedback").textContent = "Try another answer, or select Show answer.";
  }));
  $("connection-reveal").addEventListener("click", revealConnection);
  $("connection-next").addEventListener("click", () => {
    if (!connectionRevealed) return;
    if (connectionIndex === connections.length - 1) { returnToLesson(); return; }
    connectionIndex += 1;
    paintConnection();
    $("connection-reference").focus({ preventScroll: true });
    announce("Read " + connections[connectionIndex].reference + ". " + connections[connectionIndex].verse);
  });
  $("connection-reset").addEventListener("click", () => { connectionIndex = 0; paintConnection(); $("connection-reference").focus({ preventScroll: true }); });

  let wordIndex = 0;
  const verseWords = ["word", "lamp", "path"];
  function resetVerse() {
    wordIndex = 0;
    verseWords.forEach((_, index) => {
      $(`blank-${index}`).textContent = "_____";
      $(`blank-${index}`).classList.remove("filled");
      $(`blank-${index}`).classList.toggle("current", index === 0);
    });
    all("[data-word]").forEach(button => { button.disabled = false; });
    document.querySelector("[data-puzzle-feedback]").textContent = "Which word goes first?";
  }
  all("[data-word]").forEach(button => button.addEventListener("click", () => {
    if (wordIndex >= verseWords.length) return;
    if (button.dataset.word !== verseWords[wordIndex]) {
      document.querySelector("[data-puzzle-feedback]").textContent = "Not quite. Take another look at the verse.";
      return;
    }
    $(`blank-${wordIndex}`).textContent = verseWords[wordIndex];
    $(`blank-${wordIndex}`).classList.remove("current");
    $(`blank-${wordIndex}`).classList.add("filled");
    button.disabled = true;
    wordIndex++;
    if (wordIndex < verseWords.length) $(`blank-${wordIndex}`).classList.add("current");
    document.querySelector("[data-puzzle-feedback]").textContent = wordIndex < verseWords.length ? "That’s it. What comes next?" : "Let’s read the whole verse together.";
  }));
  document.querySelector("[data-puzzle-reset]").addEventListener("click", resetVerse);
  const reflectionPrompts = {
    word: "Where could you turn to hear God’s word as you think about this decision?",
    lamp: "What might a lamp help you see? What might still be out of sight?",
    path: "What is one step you could take without knowing how everything will turn out?"
  };
  all("[data-reflection]").forEach(button => button.addEventListener("click", () => {
    all("[data-reflection]").forEach(other => other.setAttribute("aria-pressed", String(other === button)));
    document.querySelector("[data-reflection-feedback]").textContent = reflectionPrompts[button.dataset.reflection];
  }));
  function resetReflection() {
    all("[data-reflection]").forEach(button => button.setAttribute("aria-pressed", "false"));
    document.querySelector("[data-reflection-feedback]").textContent = "Choose a phrase to talk about.";
  }
  document.querySelector("[data-reflection-reset]").addEventListener("click", resetReflection);
  const menu = $("moments-menu");
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && menu.open) {
      menu.open = false;
      menu.querySelector("summary").focus();
    }
  });
  chooseScenario("weary");
  paintPraise();
  paintLamp();
  paintConnection();
  resetVerse();
  resetReflection();
  }
  window.CFMExtras = { init, scriptureFor, renderScripture };
})();
