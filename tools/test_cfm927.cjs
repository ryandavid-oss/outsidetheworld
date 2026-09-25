// Run against a local static server. Requires Playwright and installed Chrome.
// OTW_TEST_URL may point to a deployed copy; OTW_SCREENSHOTS enables screenshots.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const base = process.env.OTW_TEST_URL || 'http://127.0.0.1:8927/cfm927-otw.html';
const shots = process.env.OTW_SCREENSHOTS;
if (shots) fs.mkdirSync(shots, {recursive:true});

(async () => {
  const browser = await chromium.launch({channel:'chrome', headless:true});
  try {
    const context = await browser.newContext({viewport:{width:1440,height:1000}});
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('response', response => { if (response.status() >= 400) errors.push(`${response.status()} ${response.url()}`); });
    await page.clock.install({time:new Date('2026-09-25T12:00:00-07:00')});
    await page.goto(base);
    await page.evaluate(() => document.fonts.ready);
    assert.equal(await page.locator('h1').textContent(), '“He will come and save you.”');
    assert.equal(await page.locator('#lead-link').isVisible(), false, 'Sunday control is hidden before Sunday');
    assert.equal(await page.locator('.passage').count(), 3);
    await page.getByRole('link', {name:'Begin with Isaiah 35'}).click();
    assert.equal(await page.locator('#passage-hope').getAttribute('open'), '');
    await page.waitForFunction(() => document.activeElement.tagName === 'SUMMARY');
    await page.goto(base);
    if (shots) await page.screenshot({path:`${shots}/desktop.png`,fullPage:true});
    await page.goto(base+'#discuss/opening');
    assert.equal(await page.locator('#slide-title').textContent(), 'What did you learn this week about the Savior?');
    assert.equal(await page.locator('#timer-display').textContent(), '25:00');
    await page.locator('#fullscreen').click();
    await page.waitForFunction(() => !!document.fullscreenElement);
    await page.locator('#fullscreen').click();
    await page.waitForFunction(() => !document.fullscreenElement);
    await page.locator('#timer-toggle').click();
    await page.clock.fastForward(10000);
    assert.equal(await page.locator('#timer-display').textContent(), '24:50');
    await page.locator('#next').click();
    await page.waitForURL('**#discuss/hope/read-1');
    await page.locator('.reading-slide').waitFor();
    assert.match(await page.locator('.slide').textContent(), /he will come and save you/);
    await page.reload();
    assert.equal(await page.locator('#timer-display').textContent(), '24:50', 'running timer survives reload');
    await page.clock.fastForward(5000);
    assert.equal(await page.locator('#timer-display').textContent(), '24:45');
    await page.locator('#timer-toggle').click();
    await page.clock.fastForward(5000);
    assert.equal(await page.locator('#timer-display').textContent(), '24:45', 'pause holds remaining time');
    await page.locator('#timer-reset').click();
    await page.goto(base+'#discuss/opening');
    await page.locator('#think-toggle').click();
    await page.clock.fastForward(31000);
    assert.equal(new URL(page.url()).hash, '#discuss/opening', 'reflection timer never advances');
    assert.match(await page.locator('#pause-clock').textContent(), /Continue when/);
    assert.equal(await page.locator('#timer-display').textContent(), '25:00', 'reflection timer is independent');
    await page.locator('#timer-toggle').click();
    await page.clock.fastForward(1500000);
    assert.equal(await page.locator('#timer-display').textContent(), '0:00');
    assert.equal(new URL(page.url()).hash, '#discuss/opening', 'class timer never advances');
    assert.equal(await page.locator('#timer-toggle').isDisabled(), true);
    await page.locator('#timer-reset').click();
    await page.locator('#slide-title').focus();
    await page.keyboard.press('ArrowRight');
    await page.waitForURL('**#discuss/hope/read-1');
    await page.locator('.reading-slide').waitFor();
    await page.locator('#path-select').selectOption('mercy');
    await page.waitForURL('**#discuss/mercy/read-1');
    await page.waitForFunction(() => document.querySelector('#slide-title').textContent === 'Isaiah 30:15, 18–21');
    await page.locator('#path-select').focus();
    await page.keyboard.press('Home');
    assert.equal(new URL(page.url()).hash, '#discuss/mercy/read-1', 'navigation ignores form controls');
    await page.locator('#slide-title').focus();
    await page.keyboard.press('End');
    await page.waitForURL('**#discuss/closing');
    await page.waitForFunction(() => document.querySelector('#next').textContent.includes('Back to start'));
    await page.locator('#next').click();
    await page.waitForURL('**#discuss/opening');
    await page.locator('#think-toggle').waitFor();
    await page.goto(base+'#guide');
    assert.equal(await page.locator('.rundown li').count(), 5);
    assert.equal(await page.locator('.presentation-view').isVisible(), false);
    await page.goto(base);
    await page.clock.setSystemTime(new Date('2026-09-26T23:59:59-07:00'));
    await page.evaluate(() => window.dispatchEvent(new Event('pageshow')));
    assert.equal(await page.locator('#lead-link').isVisible(), false);
    await page.clock.setSystemTime(new Date('2026-09-27T00:00:00-07:00'));
    await page.evaluate(() => window.dispatchEvent(new Event('pageshow')));
    assert.equal(await page.locator('#lead-link').isVisible(), true, 'Sunday control opens at Arizona midnight');

    // Every discussion path fits both common projector sizes, and narrow phones do not overflow.
    for (const viewport of [{width:1440,height:900},{width:1280,height:720},{width:390,height:844},{width:320,height:640}]) {
      await page.setViewportSize(viewport);
      const routes = ['', '#guide', ...['hope','refuge','mercy'].flatMap(path => ['read-1','read-2',...(path === 'mercy' ? ['read-3'] : []),'reflect','apply'].map(step=>`#discuss/${path}/${step}`)), '#discuss/opening', '#discuss/closing'];
      for (const route of routes) {
        await page.goto(base+route);
        await page.evaluate(() => document.fonts.ready);
        const dimensions = await page.evaluate(() => ({width:document.documentElement.scrollWidth, height:document.documentElement.scrollHeight, innerHeight, innerWidth}));
        assert.ok(dimensions.width <= viewport.width, `horizontal overflow ${viewport.width} ${route}`);
        if (viewport.width >= 1280 && route.startsWith('#discuss')) assert.ok(dimensions.height <= viewport.height+2, `projector vertical overflow ${viewport.width}x${viewport.height} ${route}: ${dimensions.height}`);
      }
      if (shots && viewport.width === 390) { await page.goto(base); await page.screenshot({path:`${shots}/phone.png`,fullPage:true}); }
      if (shots && viewport.width === 1440) {
        await page.goto(base+'#discuss/opening'); await page.screenshot({path:`${shots}/discussion.png`});
        await page.goto(base+'#discuss/hope/read-1'); await page.screenshot({path:`${shots}/scripture.png`});
      }
    }
    const blocked = await browser.newContext();
    await blocked.addInitScript(() => Object.defineProperty(window,'sessionStorage',{get(){throw new Error('Storage blocked');}}));
    const fallback = await blocked.newPage();
    await fallback.goto(base+'#discuss/opening');
    await fallback.locator('#timer-toggle').click();
    await fallback.locator('#next').click();
    await fallback.waitForURL('**#discuss/hope/read-1');
    await fallback.locator('.reading-slide').waitFor();
    assert.match(await fallback.locator('.slide').textContent(), /Strengthen ye the weak hands/);
    await blocked.close();
    assert.deepEqual(errors, []);
    console.log('PASS: study, all three paths, responsive layouts, projector fit, keyboard guards, leader guide, Sunday availability, independent manual timers, reload persistence, and blocked storage.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
