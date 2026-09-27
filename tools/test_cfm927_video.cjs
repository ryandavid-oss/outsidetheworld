// Run with the same Playwright + installed Chrome setup as test_cfm927.cjs.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const base = process.env.OTW_TEST_URL || 'http://127.0.0.1:8927/cfm927-otw.html';
(async () => {
  const browser = await chromium.launch({channel:'chrome',headless:true});
  try {
    const page = await browser.newPage({viewport:{width:1280,height:720}});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    let requests = 0;
    page.on('request', request => { if (request.url().includes('amy-wright-excerpt.mp4')) requests++; });
    await page.goto(base + '#discuss/watch');
    await page.evaluate(() => document.fonts.ready);
    assert.equal(requests, 0, 'video is not fetched until requested');
    const video = page.locator('#lesson-video');
    assert.equal(await video.evaluate(v => v.paused), true, 'no autoplay');
    await video.focus();
    await page.keyboard.press('ArrowRight');
    assert.equal(new URL(page.url()).hash, '#discuss/watch', 'video controls do not advance the lesson');
    await video.evaluate(v => v.play());
    await page.waitForFunction(() => document.querySelector('#lesson-video').currentTime > 0.5);
    const info = await video.evaluate(v => ({duration:v.duration,width:v.videoWidth,height:v.videoHeight,cues:[...v.textTracks[0].cues].map(c=>({start:c.startTime,end:c.endTime,text:c.text}))}));
    assert.ok(Math.abs(info.duration - 75.2) < 0.05, 'physical clip contains only the requested excerpt');
    assert.deepEqual([info.width,info.height],[1280,720]);
    assert.equal(info.cues.length,14);
    assert.match(info.cues[0].text,/Waiting upon the Lord/);
    assert.match(info.cues.at(-1).text,/emphasis should always be on Jesus/);
    assert.ok(info.cues.every(c=>c.start>=0&&c.end<=info.duration));
    await video.evaluate(v=>{v.pause();v.currentTime=1;window.excerpt=v;});
    await page.screenshot({path:'/tmp/cfm927-video-projector.png'});
    const dimensions = await page.evaluate(()=>({w:document.documentElement.scrollWidth,h:document.documentElement.scrollHeight}));
    assert.ok(dimensions.w<=1280&&dimensions.h<=722,'video fits a 720p projector');

    await video.evaluate(v=>v.play());
    await page.getByRole('link',{name:'Leader guide',exact:true}).click();
    await page.locator('#guide-title').waitFor();
    assert.equal(await page.evaluate(()=>window.excerpt.paused),true,'opening the guide pauses hidden video');
    await page.getByRole('link',{name:'Open the excerpt'}).click();
    await page.locator('#lesson-video').waitFor();
    assert.equal(await video.evaluate(v=>v.paused),true,'returning requires manual play');
    await video.evaluate(v=>v.play());
    await page.waitForFunction(()=>document.querySelector('#lesson-video').readyState>=3);
    // Play through the actual clip; the simple local server does not support range seeks.
    await video.evaluate(v=>{v.playbackRate=16;});
    await page.waitForFunction(()=>document.querySelector('#lesson-video').ended);
    assert.equal(new URL(page.url()).hash,'#discuss/watch','completion does not advance the lesson');
    assert.equal(await video.evaluate(v=>v.paused),true);
    await video.evaluate(v=>{v.currentTime=0;v.playbackRate=1;return v.play();});
    await video.evaluate(v=>{window.excerpt=v;});
    await page.locator('#next').click();
    await page.waitForURL('**#discuss/hope/reflect');
    await page.locator('.alternate').waitFor();
    assert.equal(await page.evaluate(()=>window.excerpt.paused),true,'next stops video');
    assert.deepEqual(errors,[]);
    console.log('PASS: 75.2-second 720p clip, retimed captions, lazy loading, projector fit, manual playback, keyboard guards, pause on navigation, and no auto advance.');
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
