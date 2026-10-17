(() => {
  'use strict';
  const byId = id => document.getElementById(id);
  const promises = {
    news: {
      title: 'Who hears good news?',
      body: 'Isaiah speaks to people who are poor, oppressed, and displaced. As you consider spiritual applications, keep those circumstances in view.',
      claim: 'Jesus names the poor among the recipients of His ministry. Consider what that announcement would mean to someone living in poverty.',
      question: 'What would good news sound like to someone living with poverty or exclusion?',
      source: 'https://www.workingpreacher.org/commentaries/revised-common-lectionary/third-sunday-of-advent-2/commentary-on-isaiah-611-4-8-11-6',
      label: 'Explore the context with Anathea Portier-Young ↗'
    },
    healing: {
      title: 'Binding up a wound',
      body: 'The image is of someone tending an injury. Isaiah goes on to describe ruined towns being rebuilt. The chapter reaches from personal grief to the life of a whole community.',
      claim: 'Jesus identifies Himself with the messenger sent to heal the brokenhearted. He describes caring for people who are hurting as part of His mission.',
      question: 'What do these promised actions help you understand about Jesus?',
      source: 'https://www.churchofjesuschrist.org/study/scriptures/ot/isa/61?lang=eng',
      label: 'Read Isaiah 61:1–4 ↗'
    },
    release: {
      title: 'A year of release',
      body: 'The language of release and a year of favor evokes Jubilee in Leviticus 25: land returns and Israelites serving because of poverty can return to their families. This is a connection in the imagery, rather than proof of a particular calendar year.',
      claim: 'Jesus announces release for captives. Consider the different kinds of freedom people needed then, and still need now.',
      question: 'What does the promise of release add to your understanding of His mission?',
      source: 'https://www.churchofjesuschrist.org/study/scriptures/ot/lev/25?lang=eng',
      label: 'Read Leviticus 25:8–13, 39–41 ↗'
    },
    comfort: {
      title: 'The mourner’s headdress',
      body: 'Ashes on the head expressed mourning. Isaiah’s promised beautiful headdress evokes celebration and restored dignity. Consider what this image helps a mourner hope for, while allowing grief its own time.',
      claim: 'Jesus reads from a chapter that promises comfort to people who mourn. Grief is one of the needs this passage names.',
      question: 'What does comfort look like while a person is still grieving?',
      source: 'https://www.churchofjesuschrist.org/study/manual/old-testament-seminary-student-study-guide-obs/the-book-of-isaiah/isaiah-61-the-mission-of-the-lord-and-his-servants?id=html&lang=eng',
      label: 'Read the background to Isaiah’s image ↗'
    }
  };
  for (const button of document.querySelectorAll('[data-promise]')) {
    button.addEventListener('click', () => {
      const item = promises[button.dataset.promise];
      if (!item) return;
      for (const peer of document.querySelectorAll('[data-promise]')) peer.setAttribute('aria-pressed', String(peer === button));
      byId('annotation-title').textContent = item.title;
      byId('annotation-body').textContent = item.body;
      byId('claim-connection').textContent = item.claim;
      byId('promise-question').textContent = item.question;
      byId('annotation-source').href = item.source;
      byId('annotation-source').textContent = item.label;
    });
  }
  const scenes = {
    reads: {reference:'Luke 4:16–21',heading:'Jesus says the passage is fulfilled.',body:'Jesus reads from Isaiah and declares the scripture fulfilled in His listeners’ hearing. By identifying Himself with the Spirit-anointed messenger, He claims the mission of bringing God’s promised restoration.',verses:'p16-p21',start:'p16',record:'the reading and declaration of fulfillment.',interpretation:'a messianic claim expressed through Isaiah’s description of the mission.'},
    marvel: {reference:'Luke 4:22–24',heading:'A question from His neighbors.',body:'Luke records amazement and a question about Jesus being Joseph’s son. Jesus anticipates a demand that He perform locally the works heard about elsewhere. He then invokes the rejection prophets experience in their own country.',verses:'p22-p24',start:'p22',record:'amazement, the family connection, and Jesus’ anticipated demand for miracles.',interpretation:'the hometown connection may carry an expectation of proof or special consideration.'},
    outsiders: {reference:'Luke 4:25–27',heading:'A widow and a Syrian commander.',body:'Jesus recalls Elijah’s ministry to a widow in Sidonian territory and Elisha’s healing of Naaman the Syrian. He draws both examples from Israel’s own scriptures, bringing help given beyond Israel into the exchange.',verses:'p25-p27',start:'p25',record:'Jesus singles out the foreign widow and Naaman.',interpretation:'the examples challenge the assumption that local or insider status controls access to God’s help.'},
    anger: {reference:'Luke 4:28–30',heading:'The crowd drives Him out.',body:'Luke places the congregation’s fury after these examples. They drive Jesus out and attempt to throw Him from a cliff. He passes through them and continues on His way. Luke does not narrate a formal blasphemy trial in this scene.',verses:'p28-p30',start:'p28',record:'anger and attempted violence following the two examples.',interpretation:'His claim, prophetic rebuke, and challenge to hometown expectations together illuminate the conflict; individual motives remain partly inferred.'}
  };
  for (const button of document.querySelectorAll('[data-scene]')) {
    button.addEventListener('click', () => {
      const item = scenes[button.dataset.scene];
      if (!item) return;
      for (const peer of document.querySelectorAll('[data-scene]')) peer.setAttribute('aria-pressed', String(peer === button));
      byId('scene-reference').textContent = item.reference;
      byId('scene-heading').textContent = item.heading;
      byId('scene-body').textContent = item.body;
      byId('scene-source').href = `https://www.churchofjesuschrist.org/study/scriptures/nt/luke/4?lang=eng&id=${item.verses}#${item.start}`;
      const evidence = byId('scene-evidence');
      evidence.replaceChildren();
      for (const [index, label, value] of [[0,'Luke records: ',item.record],[1,'Reading the exchange: ',item.interpretation]]) {
        if (index) evidence.append(document.createElement('br'));
        const strong = document.createElement('strong'); strong.textContent = label;
        evidence.append(strong, document.createTextNode(value));
      }
    });
  }
  const noteKey = 'otw-isaiah61-concept-reflection-v1';
  const field = byId('reflection-note'), status = byId('note-status');
  try { const saved = localStorage.getItem(noteKey); if (saved !== null) {field.value = saved;status.textContent = 'Loaded your note from this browser.';} } catch {status.textContent = 'Browser storage is unavailable. You can still write here and copy your note.';}
  field.addEventListener('input',()=>{status.textContent = 'Unsaved changes. Use Save to keep this note in this browser.';});
  byId('save-note').addEventListener('click',()=>{try {localStorage.setItem(noteKey,field.value);status.textContent = 'Saved only in this browser.';} catch {status.textContent = 'Could not save in this browser. Copy your note before leaving.';}});
  byId('clear-note').addEventListener('click',()=>{try {localStorage.removeItem(noteKey);} catch {}field.value = '';status.textContent = 'Note cleared.';field.focus();});
})();
