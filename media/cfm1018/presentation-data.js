(() => {
  'use strict';
  const jesus = '/media/cfm1018/nazareth.webp';
  const scripture = (book, chapter, range, start) => `https://www.churchofjesuschrist.org/study/scriptures/${book}/${chapter}?lang=eng&id=${range}#${start}`;
  const slides = [
    {
      id: 'opening', group: 'begin', label: 'Opening', type: 'opening',
      eyebrow: 'Isaiah 61 · Luke 4', title: 'What Jesus\ncame to do.',
      subtitle: 'Sunday, October 18', image: jesus,
      alt: 'A painting based on Jesus’ declaration in the Nazareth scene from The Chosen.'
    },
    {
      id: 'mission', group: 'mission', label: 'Read Isaiah 61', type: 'scripture',
      eyebrow: 'Read together · Isaiah 61:1–3', title: 'What has He come to do?',
      lines: ['“bind up the brokenhearted”', '“proclaim liberty to the captives”', '“comfort all that mourn”', '“beauty for ashes”'],
      reference: 'Isaiah 61:1–3 · selected phrases · KJV',
      source: scripture('ot/isa', '61', 'p1-p3', 'p1')
    },
    {
      id: 'fulfilled', group: 'mission', label: 'Jesus’ declaration', type: 'declaration',
      eyebrow: 'Luke 4:21',
      quote: 'This day is this scripture fulfilled in your ears.',
      reference: 'Luke 4:21 · KJV',
      source: scripture('nt/luke', '4', 'p21', 'p21'),
      image: jesus, alt: 'Jesus faces the congregation with the scroll in His hands.'
    },
    {
      id: 'question-mission', group: 'mission', label: 'Discuss His mission', type: 'question',
      eyebrow: 'Isaiah 61:1–3 · Luke 4:16–21',
      questions: ['What do these promised actions help you understand about Jesus?', 'What would good news sound like to one of the people named in this passage?'],
      source: scripture('ot/isa', '61', 'p1-p3', 'p1')
    },
    {
      id: 'nazareth', group: 'mercy', label: 'The response in Nazareth', type: 'context',
      eyebrow: 'Read together · Luke 4:22–27', title: 'They know Him.\nWhat will He do here?',
      quote: 'Is not this Joseph’s son?',
      body: 'Jesus anticipates a demand for miracles in His hometown. He replies with two stories from their scriptures.',
      reference: 'Luke 4:22 · KJV; summary of verses 23–27',
      source: scripture('nt/luke', '4', 'p22-p27', 'p22')
    },
    {
      id: 'widow', group: 'mercy', label: 'Elijah and the widow', type: 'story',
      eyebrow: 'Jesus’ first example · Luke 4:25–26', title: 'A widow in Sidon.',
      body: 'God sends Elijah beyond Israel to a widow at Zarephath.',
      reference: '1 Kings 17:8–16',
      source: scripture('ot/1-kgs', '17', 'p8-p16', 'p8'),
      image: '/media/cfm1018/elijah-and-widow.webp',
      alt: 'The widow offers Elijah a small flatbread while her son watches from the doorway.'
    },
    {
      id: 'naaman', group: 'mercy', label: 'Naaman’s healing', type: 'story',
      eyebrow: 'Jesus’ second example · Luke 4:27', title: 'A commander\nfrom Syria.',
      body: 'Naaman receives healing through Israel’s prophet. He belongs to a nation with a history of conflict with Israel.',
      reference: '2 Kings 5:1–14',
      source: scripture('ot/2-kgs', '5', 'p1-p14', 'p1'),
      image: '/media/cfm1018/naaman.webp',
      alt: 'Naaman looks at his healed hands in the Jordan while two attendants watch from the bank.'
    },
    {
      id: 'anger', group: 'mercy', label: 'Why the anger?', type: 'context',
      eyebrow: 'Read together · Luke 4:28–30', title: 'The congregation\nturns against Him.',
      quote: 'filled with wrath',
      body: 'Luke places their fury after the widow and Naaman examples. The crowd drives Jesus out and tries to kill Him.',
      reference: 'Luke 4:28 · excerpt · KJV; summary of verses 29–30',
      source: scripture('nt/luke', '4', 'p28-p30', 'p28')
    },
    {
      id: 'question-mercy', group: 'mercy', label: 'Discuss their expectations', type: 'question',
      eyebrow: 'Luke 4:22–30',
      questions: ['What expectations does Jesus challenge in this exchange?', 'Where might we recognize those expectations in ourselves?'],
      source: scripture('nt/luke', '4', 'p22-p30', 'p22')
    },
    {
      id: 'closing', group: 'close', label: 'Closing', type: 'closing',
      eyebrow: 'As you return to these verses this week',
      title: 'Which part of His mission would you like to understand more deeply?',
      image: jesus, alt: 'Jesus holding the scroll in Nazareth.',
      reference: 'Isaiah 61 · Luke 4'
    }
  ];
  const groups = [
    {id:'begin', title:'Begin'},
    {id:'mission', title:'Jesus’ mission'},
    {id:'mercy', title:'The response in Nazareth'},
    {id:'close', title:'Close'}
  ];
  const ids = new Set(slides.map(slide => slide.id));
  function resolveId(value) {
    let candidate = '';
    try {candidate = decodeURIComponent(String(value || '').replace(/^#/, ''));} catch {}
    return ids.has(candidate) ? candidate : 'opening';
  }
  function nextId(current, direction) {
    const index = slides.findIndex(slide => slide.id === resolveId(current));
    return slides[Math.max(0, Math.min(slides.length - 1, index + Math.sign(direction)))].id;
  }
  function commandForKey(key, shiftKey = false) {
    if (['ArrowRight','ArrowDown','PageDown'].includes(key)) return 'next';
    if (['ArrowLeft','ArrowUp','PageUp'].includes(key)) return 'previous';
    if (key === ' ' || key === 'Spacebar') return shiftKey ? 'previous' : 'next';
    if (key === 'Home') return 'opening';
    if (key === 'End') return 'closing';
    return {f:'fullscreen',h:'controls',m:'menu',i:'picture',Escape:'escape'}[key.length === 1 ? key.toLowerCase() : key] || null;
  }
  globalThis.LessonDeck = Object.freeze({slides, groups, resolveId, nextId, commandForKey});
})();
