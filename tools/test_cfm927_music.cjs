// Deterministic browser checks; the live Church stream is checked separately.
// Uses the same Playwright + installed Chrome setup as test_cfm927.cjs.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const base = process.env.OTW_TEST_URL || 'http://127.0.0.1:8927/cfm927-otw.html';

// A quiet, generated PCM tone provides real media events without a network dependency.
const sampleRate = 8000, samples = sampleRate * 30;
const wav = Buffer.alloc(44 + samples * 2);
wav.write('RIFF', 0); wav.writeUInt32LE(wav.length - 8, 4); wav.write('WAVEfmt ', 8);
wav.writeUInt32LE(16, 16); wav.writeUInt16LE(1, 20); wav.writeUInt16LE(1, 22);
wav.writeUInt32LE(sampleRate, 24); wav.writeUInt32LE(sampleRate * 2, 28);
wav.writeUInt16LE(2, 32); wav.writeUInt16LE(16, 34); wav.write('data', 36);
wav.writeUInt32LE(samples * 2, 40);
for (let i = 0; i < samples; i++) wav.writeInt16LE(Math.round(500 * Math.sin(i * 2 * Math.PI * 220 / sampleRate)), 44 + i * 2);

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    let requests = 0, fail = false, held;
    await page.route('**/icecastRelay/**', async route => {
      requests++;
      if (held) { held(route); return; }
      if (fail) return route.abort();
      await route.fulfill({ contentType: 'audio/wav', body: wav });
    });
    const stopped = () => page.waitForFunction(() => {
      const audio = document.querySelector('#arrival-music');
      return audio.paused && !audio.hasAttribute('src');
    });
    const play = async () => {
      await page.locator('#music-toggle').click();
      await page.waitForFunction(() => document.querySelector('#arrival-music').currentTime > 0.1);
      assert.equal(await page.locator('#music-toggle').textContent(), 'Stop music');
    };

    await page.goto(base + '#discuss/opening');
    assert.equal(requests, 0, 'opening the lesson does not load or autoplay music');
    await play();
    await page.locator('#path-select').selectOption('refuge');
    assert.equal(await page.locator('#music-toggle').textContent(), 'Stop music', 'rerender preserves playback controls');
    await page.locator('#timer-toggle').click();
    await page.waitForFunction(() => {
      const audio = document.querySelector('#arrival-music');
      return !audio.paused && audio.volume > 0 && audio.volume < 0.3;
    });
    await stopped();
    assert.equal(await page.locator('#timer-toggle').getAttribute('aria-pressed'), 'true');
    assert.equal(await page.locator('#music-toggle').textContent(), 'Play music');

    await page.locator('#timer-toggle').click();
    await page.locator('#timer-reset').click();
    assert.equal(requests, 1, 'timer pause and reset never restart music');
    await play();
    await page.locator('#slide-title').focus();
    await page.keyboard.press('ArrowRight');
    await page.waitForURL('**#discuss/refuge/read-1');
    await stopped();
    await page.locator('#previous').click();
    await page.locator('#music-toggle').waitFor();
    assert.equal(requests, 2, 'returning to the opening does not restart music');

    await play();
    await page.locator('#think-toggle').click();
    await page.waitForFunction(() => {
      const audio = document.querySelector('#arrival-music');
      return !audio.paused && Math.abs(audio.volume - 0.14) < 0.001;
    });
    assert.equal(requests, 3, 'reflection continues existing music without reconnecting');
    await page.keyboard.press('Escape');
    await stopped();
    await page.waitForFunction(() => !document.querySelector('#reflection-dialog').open);
    await play();
    await page.evaluate(async data => {
      const other = document.createElement('video');
      other.id = 'lesson-video'; other.src = data; document.body.append(other);
      await other.play();
    }, 'data:audio/wav;base64,' + wav.toString('base64'));
    await stopped();
    assert.equal(await page.locator('#lesson-video').evaluate(video => !video.paused && !video.muted && video.volume === 1), true, 'lesson media remains audible');
    await page.locator('#lesson-video').evaluate(video => video.remove());

    await play();
    await page.getByRole('link', { name: 'Leader guide', exact: true }).click();
    await stopped();
    await page.getByRole('link', { name: 'Open discussion' }).click();
    await page.locator('#music-toggle').waitFor();
    await play();
    await page.locator('#music-toggle').click();
    await stopped();

    fail = true;
    await page.locator('#music-toggle').click();
    await page.waitForFunction(() => document.querySelector('#status').textContent.includes('couldn’t connect'));
    await stopped();
    assert.equal(await page.locator('#music-toggle').textContent(), 'Play music', 'failed stream can be retried');
    fail = false;
    await play();
    await page.locator('#music-toggle').click();
    await stopped();

    await page.locator('#think-toggle').click();
    assert.equal(await page.locator('#arrival-music').getAttribute('src'), null, 'reading opens silently after music has stopped');
    await page.keyboard.press('Escape');
    await page.waitForFunction(() => !document.querySelector('#reflection-dialog').open);

    // The automatic return fades and releases existing audio, without restarting it.
    await play();
    await page.clock.install();
    await page.locator('#think-toggle').click();
    await page.clock.fastForward(60000);
    await page.clock.fastForward(1300);
    await stopped();
    assert.equal(await page.locator('#reflection-dialog').evaluate(d => d.open), false);
    assert.equal(await page.locator('#music-toggle').textContent(), 'Play music');
    await page.clock.resume();

    let pendingRoute;
    held = route => { pendingRoute = route; };
    await page.locator('#music-toggle').click();
    await page.waitForFunction(() => document.querySelector('#music-toggle').textContent === 'Connecting…');
    await page.locator('#timer-toggle').click();
    await stopped();
    if (pendingRoute) await pendingRoute.fulfill({ contentType: 'audio/wav', body: wav }).catch(() => {});
    assert.equal(await page.locator('#music-toggle').textContent(), 'Play music', 'starting class cancels a pending connection');
    assert.deepEqual(errors, []);
    console.log('PASS: explicit play, fade and release, navigation, reflection, independent lesson media, manual stop, failure/retry, pending-play cancellation, and no automatic restart.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
