// Run a local HTTP server at OTW_TEST_URL (default http://127.0.0.1:8765),
// then: node --test tools/test_public_frgmnts.cjs (requires Playwright).
const { test, before, after } = require('node:test');
const assert = require('node:assert/strict');
const { chromium } = require('playwright');
const base = process.env.OTW_TEST_URL || 'http://127.0.0.1:8765';
let browser;
before(async () => { browser = await chromium.launch({ headless: true }); });
after(async () => { await browser?.close(); });
const post = (overrides = {}) => ({ id: 'public-post', text: 'Original public words',
  timestamp: '2026-09-17T12:00:00.000Z', published_at: '2026-09-17T12:00:00.000Z',
  author: { display_name: 'RyanDavid', handle: 'outsidetheworld' }, tag: 'FRAGMENT',
  revision: 1, edited_at: null, ...overrides });
async function fixture(path, initial = [post()]) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  let items = initial, status = 200;
  const errors = [], requested = [];
  await context.addInitScript(() => {
    for (const version of [1, 2]) localStorage.setItem(`otwFounderFragmentsCacheV${version}`,
      JSON.stringify({ version, savedAt: Date.now(), items: [{ id: 'stale', text: 'STALE BROWSER WORDS', timestamp: '2030-01-01' }] }));
  });
  await context.route('**/*', async route => {
    const url = route.request().url(); requested.push(url);
    if (url.includes('api.frgmnts.app/v1/public/fragments/')) {
      return route.fulfill({ status, contentType: 'application/json', body: JSON.stringify({ items }) });
    }
    if (url.startsWith(base)) return route.continue();
    return route.abort();
  });
  const page = await context.newPage();
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(`${base}/${path}`, { waitUntil: 'networkidle' });
  return { page, context, errors, requested, set: (next, code = 200) => { items = next; status = code; } };
}
async function refreshHome(page) { await page.evaluate(() => refreshLatestFragmentFromPublicFeed()); }
async function refreshFeed(page) {
  await page.getByRole('button', { name: /refresh/i }).click();
  await page.waitForFunction(() => !document.getElementById('refreshFeedBtn').disabled);
}

test('feed replaces same-ID text and marks Edited without changing publication time', async () => {
  const f = await fixture('fragments.html');
  try {
    const originalDate = await f.page.locator('.fragment-time').innerText();
    assert.equal(await f.page.locator('.fragment-edited').count(), 0);
    f.set([post({ text: 'Corrected public words', revision: 2, edited_at: '2026-09-18T15:00:00Z' })]);
    await refreshFeed(f.page);
    assert.equal(await f.page.locator('.fragment-body').innerText(), 'Corrected public words');
    assert.ok((await f.page.locator('.fragment-time').innerText()).startsWith(originalDate));
    assert.equal(await f.page.locator('.fragment-edited').innerText(), 'Edited');
    assert.equal(await f.page.locator('.fragment-edited a, a[href*="history"]').count(), 0);
    assert.deepEqual(f.errors, []);
    await f.page.screenshot({ path: '/tmp/otw-edited-feed-mobile.png', fullPage: true });
  } finally { await f.context.close(); }
});

test('feed outage clears cards, load-more data and an open media viewer', async () => {
  const f = await fixture('fragments.html', Array.from({ length: 11 }, (_, i) => post({ id: `p${i}`, media: [{ url: `${base}/Images/Profile.jpg`, type: 'PHOTO' }] })));
  try {
    assert.equal(await f.page.locator('.fragment-card').count(), 10);
    await f.page.locator('[data-media-open]').first().click();
    assert.equal(await f.page.locator('#mediaViewer').evaluate(e => e.open), true);
    await f.page.locator('#mediaViewerClose').click();
    f.set([], 503); await refreshFeed(f.page);
    assert.equal(await f.page.locator('.fragment-card').count(), 0);
    assert.equal(await f.page.locator('#feedControls').isVisible(), false);
    assert.match(await f.page.locator('#fragmentsFeed').innerText(), /temporarily unavailable/);
    await f.page.locator('#loadMoreBtn').dispatchEvent('click');
    assert.equal(await f.page.locator('.fragment-card').count(), 0);
    assert.equal(await f.page.locator('#mediaViewer').evaluate(e => e.open), false);
    assert.deepEqual(f.errors, []);
  } finally { await f.context.close(); }
});

test('empty canonical feed is valid and never invokes static or browser fallback', async () => {
  const f = await fixture('fragments.html?source=local', []);
  try {
    assert.match(await f.page.locator('#fragmentsFeed').innerText(), /No public frgmnts yet/);
    assert.equal(f.requested.some(url => url.includes('fragments_data.js')), false);
    assert.equal(await f.page.evaluate(() => localStorage.getItem('otwFounderFragmentsCacheV2')), null);
  } finally { await f.context.close(); }
});

test('feed renders edited user text as text, not executable markup', async () => {
  const f = await fixture('fragments.html', [post({ text: '<img src=x onerror="window.exploited=true">', revision: 2, edited_at: '2026-09-18' })]);
  try {
    assert.match(await f.page.locator('.fragment-body').innerText(), /<img/);
    assert.equal(await f.page.evaluate(() => Boolean(window.exploited)), false);
    assert.equal(await f.page.locator('.fragment-body img').count(), 0);
  } finally { await f.context.close(); }
});

test('homepage updates same-ID edits and replaces withdrawn newest with an older remaining post', async () => {
  const f = await fixture('index.html');
  try {
    assert.equal(await f.page.locator('#latestFragmentText').innerText(), 'Original public words');
    f.set([post({ text: 'Corrected public words', revision: 2, edited_at: '2026-09-18T15:00:00Z' })]);
    await refreshHome(f.page);
    assert.equal(await f.page.locator('#latestFragmentText').innerText(), 'Corrected public words');
    assert.match(await f.page.locator('#latestFragmentDate').innerText(), /Edited/i);
    assert.equal(await f.page.locator('#latestFragmentDate').getAttribute('datetime'), post().timestamp);
    await f.page.locator('#latestFragment').screenshot({ path: '/tmp/otw-edited-home-mobile.png' });
    f.set([post({ id: 'older', text: 'Older remaining words', timestamp: '2026-09-15T12:00:00Z' })]);
    await refreshHome(f.page);
    assert.equal(await f.page.locator('#latestFragmentText').innerText(), 'Older remaining words');
    assert.doesNotMatch(await f.page.locator('#latestFragmentDate').innerText(), /Edited/i);
    assert.deepEqual(f.errors, []);
  } finally { await f.context.close(); }
});

test('homepage clears removed or unavailable posts and never restores archived text', async () => {
  const f = await fixture('index.html');
  try {
    f.set([]); await refreshHome(f.page);
    assert.equal(await f.page.locator('#latestFragment').isVisible(), false);
    assert.equal(await f.page.locator('#latestFragmentText').textContent(), '');
    f.set([post()]); await refreshHome(f.page);
    f.set([], 503); await refreshHome(f.page);
    assert.equal(await f.page.locator('#latestFragment').isVisible(), false);
    assert.equal(await f.page.locator('#latestFragmentText').textContent(), '');
    assert.equal(f.requested.some(url => url.includes('fragments_data.js')), false);
    assert.equal(await f.page.evaluate(() => localStorage.getItem('otwFounderFragmentsCacheV1')), null);
    assert.deepEqual(f.errors, []);
  } finally { await f.context.close(); }
});

test('homepage accepts newest photo-only post', async () => {
  const f = await fixture('index.html', [post({ text: '', media: [{ url: `${base}/Images/Profile.jpg`, type: 'PHOTO' }] })]);
  try {
    assert.equal(await f.page.locator('#latestFragment').isVisible(), true);
    assert.equal(await f.page.locator('#latestFragmentText').isVisible(), false);
    assert.equal(await f.page.locator('#latestFragmentMedia').isVisible(), true);
    assert.deepEqual(f.errors, []);
  } finally { await f.context.close(); }
});

test('homepage search uses canonical text and clears its snapshot across page restoration', async () => {
  const f = await fixture('index.html', [post({ text: 'Zebramoon corrected caption' })]);
  try {
    const entries = await f.page.evaluate(() => buildSearchIndex());
    assert.equal(entries.filter(e => e.kind === 'frgmnt').length, 1);
    assert.ok(entries.some(e => e.snippet === 'Zebramoon corrected caption'));
    f.set([post({ text: 'Replacement current caption', revision: 2, edited_at: '2026-09-18' })]);
    await f.page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pagehide')));
    assert.equal(await f.page.locator('#latestFragmentText').textContent(), '');
    const refreshed = await f.page.evaluate(() => buildSearchIndex());
    assert.equal(refreshed.some(e => e.snippet.includes('Zebramoon')), false);
    assert.ok(refreshed.some(e => e.snippet === 'Replacement current caption'));
    assert.deepEqual(f.errors, []);
  } finally { await f.context.close(); }
});

test('homepage rejects an older in-flight response after a newer refresh', async () => {
  const f = await fixture('index.html');
  try {
    await f.page.evaluate(async () => {
      const realFetch = window.fetch;
      let release;
      window.fetch = () => new Promise(resolve => { release = resolve; });
      const stale = refreshLatestFragmentFromPublicFeed();
      window.fetch = realFetch;
      await refreshLatestFragmentFromPublicFeed();
      release(new Response(JSON.stringify({ items: [{ id: 'stale', text: 'STALE ASYNC WORDS', timestamp: '2030-01-01' }] })));
      await stale;
    });
    assert.equal(await f.page.locator('#latestFragmentText').innerText(), 'Original public words');
  } finally { await f.context.close(); }
});

test('feed ignores a delayed response after leaving the page', async () => {
  const f = await fixture('fragments.html');
  try {
    await f.page.evaluate(() => {
      const realFetch = window.fetch;
      window.fetch = (url, options) => String(url).includes('api.frgmnts.app')
        ? new Promise(resolve => { window.releaseFeed = resolve; }) : realFetch(url, options);
      document.getElementById('refreshFeedBtn').click();
      window.dispatchEvent(new PageTransitionEvent('pagehide'));
      window.releaseFeed(new Response(JSON.stringify({ items: [{ id: 'stale', text: 'STALE ASYNC WORDS' }] })));
    });
    await f.page.waitForTimeout(50);
    assert.equal(await f.page.locator('.fragment-card').count(), 0);
    assert.equal(await f.page.locator('#feedControls').isVisible(), false);
    assert.deepEqual(f.errors, []);
  } finally { await f.context.close(); }
});
