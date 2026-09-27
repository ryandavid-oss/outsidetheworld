// Run against the local server, or set OTW_TEST_URL to the published lesson.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const base = process.env.OTW_TEST_URL || 'http://127.0.0.1:8927/cfm927-otw.html';

(async () => {
  const browser = await chromium.launch({channel:'chrome',headless:true});
  try {
    const page = await browser.newPage({viewport:{width:1280,height:720},reducedMotion:'reduce'});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.clock.install();
    await page.goto(base+'#discuss/opening');
    await page.locator('#think-toggle').click();
    await page.waitForFunction(() => document.querySelector('#reflection-dialog').classList.contains('is-visible'));
    assert.equal(await page.locator('.reflection-passage').count(),3);
    const original = await page.locator('#reflection-stage').textContent();
    assert.equal(await page.locator('#arrival-music').getAttribute('src'),null,'reading does not start music');
    assert.equal(await page.locator('#think-toggle').getAttribute('aria-expanded'),'true');
    await page.clock.fastForward(5000);
    await page.locator('#reflection-hold').click();
    const held = await page.locator('#reflection-time').textContent();
    await page.clock.fastForward(12000);
    assert.equal(await page.locator('#reflection-time').textContent(),held,'Hold pauses the reading timer');
    assert.equal(await page.locator('#reflection-hold').textContent(),'Resume');
    await page.locator('#reflection-hold').click();
    await page.clock.fastForward(26000);
    assert.equal(await page.locator('#reflection-time').textContent(),'Take your time');
    assert.equal(await page.locator('#reflection-dialog').evaluate(d=>d.open),true,'timer completion leaves reading open');
    assert.equal(await page.locator('#reflection-stage').textContent(),original,'all passages remain unchanged');
    assert.equal(await page.locator('#timer-display').textContent(),'25:00','reading timer is independent');
    await page.setViewportSize({width:320,height:640});
    assert.equal(await page.locator('#reflection-dialog').evaluate(d=>d.scrollWidth<=d.clientWidth),true,'completed timer controls fit a narrow phone');
    await page.setViewportSize({width:1280,height:720});
    await page.locator('#reflection-hold').click();
    assert.equal(await page.locator('#reflection-time').textContent(),'0:30');
    await page.locator('#reflection-heading').focus();
    for (const key of ['ArrowRight','ArrowLeft','Home','End','f']) await page.keyboard.press(key);
    assert.equal(new URL(page.url()).hash,'#discuss/opening','background lesson shortcuts are suspended');
    assert.equal(await page.evaluate(()=>!!document.fullscreenElement),false);
    await page.locator('#reflection-return').focus();
    await page.keyboard.press('Tab');
    assert.equal(await page.evaluate(()=>document.querySelector('#reflection-dialog').contains(document.activeElement)),true,'tab focus stays inside dialog');
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#reflection-dialog').evaluate(d=>d.open),false);
    assert.equal(await page.locator('#think-toggle').evaluate(e=>e===document.activeElement),true,'closing restores focus');
    assert.equal(await page.locator('#think-toggle').getAttribute('aria-expanded'),'false');

    await page.locator('#timer-toggle').click();
    await page.locator('#think-toggle').click();
    await page.clock.fastForward(5000);
    assert.equal(await page.locator('#timer-display').textContent(),'24:55','class timer continues during reading');
    await page.evaluate(()=>{location.hash='guide';});
    await page.locator('#guide-title').waitFor();
    assert.equal(await page.locator('#reflection-dialog').evaluate(d=>d.open),false,'route changes dismiss reading');
    assert.equal(await page.locator('body').evaluate(e=>e.classList.contains('reflection-open')),false,'route changes unlock scrolling');
    await page.goto(base+'#discuss/opening');
    await page.locator('#timer-reset').click();
    await page.locator('#think-toggle').click();
    await page.route('**/icecastRelay/**',route=>route.abort());
    await page.locator('#reflection-music-toggle').click();
    await page.locator('#reflection-music-status').waitFor({state:'visible'});
    assert.match(await page.locator('#reflection-music-status').textContent(),/couldn’t connect/,'connection errors are visible inside the dialog');
    assert.equal(await page.locator('#reflection-music-toggle').textContent(),'Play music');
    await page.locator('#reflection-return').click();

    // Check real fonts, transitions, image loading and layout at projector/tablet/phone sizes.
    const visual = await browser.newPage();
    visual.on('pageerror',error=>errors.push(error.message));
    await visual.goto(base+'#discuss/opening');
    for (const size of [{width:1920,height:1080},{width:1440,height:900},{width:1280,height:720},{width:1024,height:768},{width:820,height:1180},{width:390,height:844},{width:320,height:640}]) {
      await visual.setViewportSize(size);
      await visual.locator('#think-toggle').click();
      await visual.evaluate(()=>document.fonts.ready);
      await visual.waitForFunction(()=>[...document.querySelectorAll('.reflection-passage')].every(e=>getComputedStyle(e).opacity==='1'));
      await visual.locator('.reflection-art img').evaluate(image=>image.decode());
      const dimensions = await visual.evaluate(()=>{
        const dialog=document.querySelector('#reflection-dialog'),footer=document.querySelector('.reflection-controls').getBoundingClientRect();
        return {clientWidth:dialog.clientWidth,scrollWidth:dialog.scrollWidth,footerTop:footer.top,dialogTop:dialog.getBoundingClientRect().top,passages:[...document.querySelectorAll('.reflection-passage')].map(e=>{const r=e.getBoundingClientRect();return{top:r.top,bottom:r.bottom,left:r.left,right:r.right};})};
      });
      assert.ok(dimensions.scrollWidth<=dimensions.clientWidth,`no horizontal overflow at ${size.width}`);
      if(size.width>700) assert.ok(dimensions.passages.every(p=>p.top>=dimensions.dialogTop&&p.bottom<=dimensions.footerTop),`all three passages fit above controls at ${size.width}x${size.height}: ${JSON.stringify(dimensions)}`);
      if(size.width===1280||size.width===390) await visual.screenshot({path:`/tmp/cfm927-reflection-${size.width}.png`});
      if(size.width<=700) {
        await visual.locator('.reflection-comfort').scrollIntoViewIfNeeded();
        assert.equal(await visual.locator('#reflection-return').isVisible(),true,'mobile return remains available while reading');
      }
      await visual.locator('#reflection-return').click();
      await visual.waitForFunction(()=>!document.querySelector('#reflection-dialog').open);
      assert.equal(await visual.locator('#think-toggle').evaluate(e=>e===document.activeElement),true);
    }
    assert.deepEqual(errors,[]);
    console.log('PASS: three simultaneous passages, projector and mobile layouts, image and fades, manual timer/return, independent class time, focus and keyboard guards, route cleanup, and visible music failure/retry.');
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
