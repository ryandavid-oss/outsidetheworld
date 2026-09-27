// Run against the local server, or set OTW_TEST_URL to the published lesson.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const base = process.env.OTW_TEST_URL || 'http://127.0.0.1:8927/cfm927-otw.html';
(async () => {
  const browser = await chromium.launch({channel:'chrome',headless:true});
  try {
    const page = await browser.newPage({viewport:{width:1280,height:720},reducedMotion:'reduce'});
    const errors = [];
    page.on('pageerror',e=>errors.push(e.message));
    await page.clock.install();
    await page.goto(base+'#discuss/opening');
    const open = async () => {
      await page.locator('#think-toggle').click();
      await page.clock.runFor(20);
    };
    const current = () => page.locator('.reflection-passage.is-current').allTextContents();
    await open();
    assert.match(await page.locator('#think-toggle').textContent(),/60 seconds/);
    assert.equal(await page.locator('#reflection-dialog button,#reflection-dialog a,#reflection-dialog input,#reflection-dialog header,#reflection-dialog footer').count(),0,'reading has no visible controls, headings or links');
    assert.equal(await page.locator('.reflection-passage.is-current').count(),3);
    assert.equal(await page.locator('#arrival-music').getAttribute('src'),null,'reading never starts music');
    assert.match((await current())[0],/fear not/);
    await page.clock.fastForward(23000);
    assert.match((await current())[0],/fear not/,'initial passages have time to be read');
    await page.clock.fastForward(2200);
    assert.match((await current())[0],/perfect peace/);
    assert.match((await current())[1],/refuge from the storm/,'other passages remain during first change');
    await page.clock.fastForward(7000);
    assert.match((await current())[1],/in quietness/);
    assert.match((await current())[2],/wipe away tears/);
    await page.clock.fastForward(7000);
    assert.match((await current())[2],/walk ye in it/);
    await page.clock.fastForward(19000);
    assert.equal(await page.locator('#reflection-dialog').evaluate(d=>d.open),true,'reading remains for nearly a full minute');
    await page.clock.fastForward(3000);
    assert.equal(await page.locator('#reflection-dialog').evaluate(d=>d.open),false,'reading returns automatically after 60 seconds');
    assert.equal(new URL(page.url()).hash,'#discuss/opening');
    assert.equal(await page.locator('#timer-display').textContent(),'25:00','class timer stays independent');
    assert.equal(await page.locator('#think-toggle').evaluate(e=>e===document.activeElement),true);
    assert.equal(await page.locator('#think-toggle').getAttribute('aria-expanded'),'false');

    await open();
    assert.match((await current())[0],/fear not/,'reopening starts the sequence again');
    for (const key of ['ArrowRight','ArrowLeft','Home','End','f','Tab','Shift+Tab']) await page.keyboard.press(key);
    assert.equal(new URL(page.url()).hash,'#discuss/opening','background lesson shortcuts are suspended');
    assert.equal(await page.evaluate(()=>!!document.fullscreenElement),false);
    assert.equal(await page.locator('#reflection-dialog').evaluate(d=>d===document.activeElement),true,'focus stays inside reading');
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#reflection-dialog').evaluate(d=>d.open),false,'Escape returns early');
    await open();
    await page.locator('.reflection-emphasis').first().click();
    assert.equal(await page.locator('#reflection-dialog').evaluate(d=>d.open),false,'a tap returns early');
    await page.locator('#timer-toggle').click();
    await open();
    await page.clock.fastForward(5000);
    assert.equal(await page.locator('#timer-display').textContent(),'24:55','running class timer continues');
    await page.evaluate(()=>{location.hash='guide';});
    await page.locator('#guide-title').waitFor();
    assert.equal(await page.locator('#reflection-dialog').evaluate(d=>d.open),false);
    assert.equal(await page.locator('body').evaluate(e=>e.classList.contains('reflection-open')),false,'navigation unlocks background scrolling');
    await page.clock.fastForward(60000);
    assert.equal(new URL(page.url()).hash,'#guide','cancelled reading cannot navigate later');
    assert.match(await page.locator('#guide').textContent(),/Isaiah 26:3/,'sources remain available in the guide');

    // Each arrangement fits common projector, tablet and phone viewports without scrolling.
    await page.goto(base+'#discuss/opening');
    for (const size of [{width:1920,height:1080},{width:1440,height:900},{width:1280,height:720},{width:1024,height:768},{width:820,height:1180},{width:390,height:844},{width:320,height:640}]) {
      await page.setViewportSize(size);
      await open();
      await page.evaluate(()=>document.fonts.ready);
      await page.locator('.reflection-art img').evaluate(i=>i.decode());
      for (const phase of ['first','second']) {
        if (phase==='second') await page.clock.fastForward(41000);
        const d = await page.evaluate(()=>{
          const dialog=document.querySelector('#reflection-dialog');
          return {width:dialog.scrollWidth,height:dialog.scrollHeight,quotes:[...document.querySelectorAll('.reflection-passage.is-current')].map(e=>e.getBoundingClientRect().toJSON())};
        });
        assert.ok(d.width<=size.width && d.height<=size.height,`no overflow ${size.width}x${size.height}, ${phase}: ${JSON.stringify(d)}`);
        assert.ok(d.quotes.every(q=>q.top>=0&&q.left>=0&&q.right<=size.width+1&&q.bottom<=size.height+1),`all passages fit ${size.width}x${size.height}, ${phase}`);
      }
      await page.keyboard.press('Escape');
    }
    // Backgrounding does not leave a stalled reading or a future surprise navigation.
    await open();
    await page.evaluate(()=>Object.defineProperty(document,'hidden',{configurable:true,value:true}));
    await page.clock.fastForward(61000);
    assert.equal(await page.locator('#reflection-dialog').evaluate(d=>d.open),false);
    assert.deepEqual(errors,[]);
    console.log('PASS: 60-second automatic return, staggered scripture changes, no visible UI, fitting projector/mobile layouts, focus and keyboard guards, early exits, independent class timer and navigation cleanup.');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
