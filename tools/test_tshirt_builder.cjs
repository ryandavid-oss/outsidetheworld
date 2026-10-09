// Run against a local static server with Playwright and installed Chrome.
// OTW_TEST_URL and OTW_SCREENSHOTS optionally select the page and screenshot folder.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const base = process.env.OTW_TEST_URL || 'http://127.0.0.1:8936/tshirt_builder.html';
const shots = process.env.OTW_SCREENSHOTS;
if (shots) fs.mkdirSync(shots, { recursive: true });

function unzipStored(bytes) {
  const files = new Map();
  let offset = 0;
  while (bytes.readUInt32LE(offset) === 0x04034b50) {
    assert.equal(bytes.readUInt16LE(offset + 8), 0);
    const size = bytes.readUInt32LE(offset + 18);
    const nameLength = bytes.readUInt16LE(offset + 26);
    const extraLength = bytes.readUInt16LE(offset + 28);
    const start = offset + 30 + nameLength + extraLength;
    files.set(bytes.subarray(offset + 30, offset + 30 + nameLength).toString(), bytes.subarray(start, start + size));
    offset = start + size;
  }
  return files;
}

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, reducedMotion: 'reduce' });
    const recordCanvas = () => {
      // Record actual canvas drawing, including the buffer copied into the visible preview.
      const proto = CanvasRenderingContext2D.prototype;
      const clear = proto.clearRect, draw = proto.drawImage, text = proto.fillText;
      proto.clearRect = function (...args) { this.canvas.drawings = []; return clear.apply(this, args); };
      proto.drawImage = function (image, ...args) {
        this.canvas.drawings ||= [];
        if (image instanceof HTMLCanvasElement) this.canvas.drawings.push(...(image.drawings || []));
        else this.canvas.drawings.push({ image: image.src, box: args });
        return draw.call(this, image, ...args);
      };
      proto.fillText = function (value, ...args) {
        this.canvas.drawings ||= [];
        const metric = this.measureText(value);
        this.canvas.drawings.push({ text: value, point: args, font: this.font,
          ink: { left: args[0] - metric.actualBoundingBoxLeft, right: args[0] + metric.actualBoundingBoxRight,
            top: args[1] - metric.actualBoundingBoxAscent, bottom: args[1] + metric.actualBoundingBoxDescent } });
        return text.call(this, value, ...args);
      };
    };
    await context.addInitScript(recordCanvas);
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const ready = () => page.waitForFunction(() => document.querySelector('#renderState').textContent === 'Ready');
    const side = async value => { await page.locator(`[data-side="${value}"]`).first().click(); await ready(); };
    const size = async value => {
      await page.locator('#artSizeInput').evaluate((input, value) => {
        input.value = value; input.dispatchEvent(new Event('input', { bubbles: true }));
      }, String(value));
      await ready();
    };
    const drawing = () => page.locator('#preview').evaluate(canvas => canvas.drawings);
    const range = async (selector, value) => {
      await page.locator(selector).evaluate((input, value) => {
        input.value = value; input.dispatchEvent(new Event('input', { bubbles: true }));
      }, String(value));
      await ready();
    };
    const textCenter = entries => {
      const lines = new Map();
      for (const entry of entries.filter(entry => entry.text?.trim())) {
        const bounds = lines.get(entry.point[1]) || { left: Infinity, right: -Infinity };
        bounds.left = Math.min(bounds.left, entry.ink.left); bounds.right = Math.max(bounds.right, entry.ink.right);
        lines.set(entry.point[1], bounds);
      }
      return [...lines.values()].map(bounds => (bounds.left + bounds.right) / 2);
    };
    const frontText = 'Hi_fr gmnts\nRyan & friends';
    const backText = 'Made for friends\nArizona, 2026.';

    await page.goto(base); await ready();
    assert.equal(await page.locator('[data-side]').count(), 2, 'one side selector edits artwork and text');
    assert.equal(await page.locator('.pixel-runner, .mode7-world, #destroyPageButton, #surpriseButton, [data-lock]').count(), 0, 'arcade controls and scenery are retired');
    assert.equal(await page.locator('#quickColors [data-color]:visible').count(), 4);
    assert.equal(await page.locator('#colorPicker').evaluate(picker => picker.open), false);
    await page.locator('#colorPicker summary').click();
    assert.equal(await page.locator('#colorGrid [data-color]:visible').count(), 51, 'the complete short-sleeve collection remains available');
    await page.locator('#colorSearch').fill('eucalyptus');
    assert.equal(await page.locator('#colorGrid [data-color]:visible').count(), 1);
    await page.locator('#colorGrid [data-color="eucalyptus-blue"]').click(); await ready();
    assert.equal(await page.locator('#selectedColor').textContent(), 'Eucalyptus Blue');
    assert.equal(await page.locator('#colorPicker').evaluate(picker => picker.open), false);
    await page.locator('#quickColors [data-color="black"]').click(); await ready();
    await page.locator('#colorSearch').evaluate(input => { input.value = ''; input.dispatchEvent(new Event('input', { bubbles: true })); });
    assert.equal(await page.locator('#artSizeInput').inputValue(), '100');
    await size(75);
    assert.equal((await drawing()).find(entry => entry.image?.startsWith('blob:')).box[2], 210);
    await page.locator('#customTextInput').fill(frontText); await ready();
    assert.equal((await drawing()).filter(entry => entry.text).map(entry => entry.text).join(''), frontText.replaceAll('\n', ''));
    assert.equal(await page.locator('#textFontInput option').count(), 8);
    for (const [id, family] of Object.entries({ 'fira-code': 'Fira Code', inter: 'Inter', 'ibm-plex-sans': 'IBM Plex Sans', 'ibm-plex-mono': 'IBM Plex Mono', saira: 'Saira', fraunces: 'Fraunces', merriweather: 'Merriweather', 'ibm-plex-serif': 'IBM Plex Serif' })) {
      await page.locator('#textFontInput').selectOption(id); await ready();
      assert.ok((await drawing()).filter(entry => entry.text).every(entry => entry.font.includes(family)), family + ' is used for the artwork');
      assert.ok(await page.evaluate(family => [...document.fonts].some(face => face.family.replaceAll('"', '') === family && face.status === 'loaded'), family), family + ' loads the real font');
    }
    await page.locator('#textFontInput').selectOption('fraunces'); await ready();
    await page.locator('#textLayoutPicker summary').click();
    await page.locator('#centerTextButton').click(); await ready();
    assert.ok(textCenter(await drawing()).every(center => Math.abs(center - 1000) < .01), 'each line centers by its visible glyphs');
    const initialTextY = (await drawing()).find(entry => entry.text).point[1];
    await range('#textYInput', 10);
    assert.equal((await drawing()).find(entry => entry.text).point[1], initialTextY + 200, 'height moves the text down independently');
    await range('#textXInput', -5);
    assert.ok(textCenter(await drawing()).every(center => Math.abs(center - 900) < .01), 'horizontal position moves every line together');
    await page.locator('#centerTextButton').click(); await ready();
    await range('#textSizeInput', 125);
    assert.ok((await drawing()).find(entry => entry.text).font.includes('55px'), 'text size is independent of graphic size');
    await side('back'); await size(125);
    assert.equal((await drawing()).find(entry => entry.image?.startsWith('blob:')).box[2], 1000);
    await page.locator('#customTextInput').fill(backText); await ready();
    await page.locator('#textFontInput').selectOption('saira'); await ready();
    await range('#textSizeInput', 115); await range('#textXInput', -5); await range('#textYInput', -10);
    await side('front');
    assert.equal(await page.locator('#artSizeInput').inputValue(), '75');
    assert.equal(await page.locator('#customTextInput').inputValue(), frontText);
    assert.equal(await page.locator('#textFontInput').inputValue(), 'fraunces');
    assert.equal(await page.locator('#textSizeInput').inputValue(), '125');
    assert.equal(await page.locator('#textXInput').inputValue(), '0');
    assert.equal(await page.locator('#textYInput').inputValue(), '10');
    if (shots) await page.screenshot({ path: `${shots}/desktop-front.png`, fullPage: true });
    await page.locator('#keepButton').click();
    const shared = page.url();
    const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('otw-frgmnts-shirt-build-v1')));
    assert.equal(saved.frontArtSize, 75); assert.equal(saved.backArtSize, 125);
    assert.equal(saved.frontSlogan, frontText); assert.equal(saved.slogan, backText);
    assert.deepEqual(saved.frontTextStyle, { font: 'fraunces', size: 125, x: 0, y: 10 });
    assert.deepEqual(saved.backTextStyle, { font: 'saira', size: 115, x: -5, y: -10 });
    await page.goto(base); await page.reload(); await ready();
    assert.equal(await page.locator('#customTextInput').inputValue(), frontText, 'device restore');
    assert.equal(await page.locator('#textFontInput').inputValue(), 'fraunces', 'saved typeface restores');
    await page.evaluate(() => localStorage.clear());
    await page.goto(shared); await page.reload(); await ready();
    assert.equal(await page.locator('#customTextInput').inputValue(), frontText, 'shared link restore');
    assert.equal(await page.locator('#textSizeInput').inputValue(), '125', 'shared text size restores');
    assert.equal(await page.locator('#textYInput').inputValue(), '10', 'shared text position restores');
    await side('back');
    assert.equal(await page.locator('#customTextInput').inputValue(), backText);
    assert.equal(await page.locator('#artSizeInput').inputValue(), '125');
    assert.equal(await page.locator('#textFontInput').inputValue(), 'saira');
    assert.equal(await page.locator('#textXInput').inputValue(), '-5');
    assert.equal(await page.locator('#textYInput').inputValue(), '-10');

    await page.locator('#exportButton').click();
    assert.equal(await page.locator('#exportDesignFrontText').textContent(), frontText);
    await page.locator('.export-size-input').nth(2).fill('2');
    await page.locator('#exportAddColorwayButton').click();
    await page.locator('.export-color-select').nth(1).selectOption('white');
    await page.locator('.export-colorway').nth(1).locator('.export-size-input').nth(3).fill('1');
    const downloadEvent = page.waitForEvent('download', { timeout: 60000 });
    await page.locator('#exportSubmitButton').click();
    const download = await downloadEvent;
    const files = unzipStored(fs.readFileSync(await download.path()));
    const spec = [...files].find(([name]) => name.endsWith('/print-spec.txt'))[1].toString();
    assert.ok(spec.includes(frontText)); assert.ok(spec.includes(backText));
    assert.ok(spec.includes('Typeface: Fraunces; size: 125%') && spec.includes('Typeface: Saira; size: 115%'), 'printer notes identify both text treatments');
    assert.ok(spec.includes('Total shirts: 3') && spec.includes('BLACK - M x 2') && spec.includes('WHITE - L x 1'));
    assert.ok(spec.split('\n').length < 50, 'printer instructions stay concise');
    for (const color of ['black', 'white']) for (const textSide of ['front', 'back']) {
      const [, png] = [...files].find(([name]) => name.includes(`/colorways/${color}/artwork/${textSide}-text-`));
      assert.equal(png.readUInt32BE(0), 0x89504e47);
      assert.equal(png[25], 6, 'text production artwork has an alpha channel');
      const bounds = await page.evaluate(async base64 => {
        const image = new Image(); image.src = 'data:image/png;base64,' + base64; await image.decode();
        const canvas = document.createElement('canvas'); canvas.width = image.width; canvas.height = image.height;
        const ctx = canvas.getContext('2d'); ctx.drawImage(image, 0, 0);
        const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
        let left = canvas.width, right = 0, top = canvas.height, bottom = 0;
        for (let y = 0; y < canvas.height; y++) for (let x = 0; x < canvas.width; x++) if (pixels[(y * canvas.width + x) * 4 + 3]) {
          left = Math.min(left, x); right = Math.max(right, x); top = Math.min(top, y); bottom = Math.max(bottom, y);
        }
        return { left, right, top, bottom, width: canvas.width, height: canvas.height };
      }, png.toString('base64'));
      assert.ok(bounds.left >= 100 && bounds.top >= 100 && bounds.right < bounds.width - 100 && bounds.bottom < bounds.height - 100, 'exported glyphs have transparent padding on every edge');
    }

    // Intercept the private endpoint: this verifies the order payload without submitting an order.
    let submitted;
    await page.route('**/submit-shirt-order', async route => {
      submitted = route.request().postDataBuffer().toString();
      await route.fulfill({ json: { ok: true, order_id: 'TEST', total_cents: 2900 } });
    });
    await page.locator('#buyButton').click();
    await page.locator('#orderPreview').waitFor({ state: 'visible' });
    for (const [name, value] of Object.entries({ name: 'Test Order', email: 'test@example.com', venmo_handle: 'test-user', shipping_address: '1 Test Street', note: 'Test note' })) {
      await page.locator(`#orderForm [name="${name}"]`).fill(value);
    }
    await page.locator('#orderForm [name="size"]').selectOption('M');
    await page.locator('#orderShippingState').selectOption('AZ');
    await page.locator('#orderForm [name="price_acknowledged"]').check();
    await page.locator('#orderForm [name="order_terms_acknowledged"]').check();
    await page.locator('#orderSubmitButton').click();
    await page.waitForFunction(() => document.querySelector('#orderStatus').textContent.includes('Order TEST received'));
    assert.ok(submitted.includes('Front graphic: OTW Brandmark at 75%'));
    assert.ok(submitted.includes('Back graphic: OTW Main Logo at 125%'));
    assert.ok(submitted.includes(JSON.stringify(frontText).slice(1, -1)));
    assert.ok(submitted.includes('Test note'));
    assert.ok(submitted.includes('Typeface: Fraunces; size: 125%') && submitted.includes('Typeface: Saira; size: 115%'), 'the existing order note preserves typeface and placement');
    await page.locator('#orderCloseButton').click();

    await page.goto(base + '#body=long&color=white&front=frgmnts&back=brandmark&words=THE_ANALOG_DAWN');
    await page.reload(); await ready();
    assert.equal(await page.locator('#artSizeInput').inputValue(), '100', 'legacy links use original size');
    assert.equal(await page.locator('#textFontInput').inputValue(), 'fira-code', 'legacy links retain the original typeface');
    assert.equal(await page.locator('#textSizeInput').inputValue(), '100');
    await side('back');
    assert.equal(await page.locator('#customTextInput').inputValue(), 'THE ANALOG DAWN');
    await size(150); await ready();
    const logo = (await drawing()).find(entry => entry.image?.startsWith('blob:'));
    assert.ok(logo.box[1] >= 200, 'large graphics stay below the collar');
    await page.locator('#customTextInput').fill('X'.repeat(80)); await ready();
    assert.equal((await drawing()).filter(entry => entry.text).length, 80, 'long custom text is rendered, not dropped');
    await range('#textSizeInput', 160); await range('#textXInput', 25); await range('#textYInput', 40);
    assert.ok((await drawing()).filter(entry => entry.text?.trim()).every(entry => entry.ink.left >= 500 - .01 && entry.ink.right <= 1500 + .01 && entry.ink.top >= 260 - .01 && entry.ink.bottom <= 1550 + .01), 'large text stays inside the print area');
    await page.locator('#textLayoutPicker summary').click();
    await page.locator('#resetTextPositionButton').click(); await ready();
    assert.equal(await page.locator('#textXInput').inputValue(), '0');
    assert.equal(await page.locator('#textYInput').inputValue(), '0');
    await page.locator('#phrasePicker summary').click();
    await page.locator('#phraseGrid [data-words-off]').click(); await ready();
    assert.equal(await page.locator('#phrasePicker').evaluate(picker => picker.open), false);
    assert.equal((await drawing()).filter(entry => entry.text).length, 0);
    await page.locator('[data-art="none"]').click();
    assert.equal(await page.locator('#artSizeInput').isDisabled(), true);
    await page.locator('#resetButton').click(); await ready();
    assert.equal(await page.locator('#artSizeInput').inputValue(), '100');
    assert.equal(await page.locator('#customTextInput').inputValue(), '');
    await side('back');
    assert.equal(await page.locator('#customTextInput').inputValue(), 'THE ANALOG DAWN');

    await page.setViewportSize({ width: 390, height: 844 });
    await page.locator('#customTextInput').fill(backText); await ready();
    if (shots) {
      await page.locator('#words-heading').scrollIntoViewIfNeeded();
      await page.screenshot({ path: `${shots}/mobile-text.png` });
      await page.locator('#shirtStage').scrollIntoViewIfNeeded();
      await page.screenshot({ path: `${shots}/mobile-preview.png` });
    }
    assert.ok(await page.evaluate(() => document.querySelector('main').getBoundingClientRect().right <= innerWidth), 'mobile controls fit viewport');
    assert.ok(await page.locator('#customTextInput').evaluate(input => input.getBoundingClientRect().right <= innerWidth), 'mobile text field fits viewport');
    assert.deepEqual(errors, []);
    const raceContext = await browser.newContext({ viewport: { width: 1440, height: 1100 } });
    await raceContext.addInitScript(recordCanvas);
    const racePage = await raceContext.newPage();
    await racePage.goto(base);
    await racePage.waitForFunction(() => document.querySelector('#renderState').textContent === 'Ready');
    await racePage.locator('#customTextInput').fill('Font race');
    await racePage.waitForFunction(() => document.querySelector('#renderState').textContent === 'Ready');
    let releaseFont, noticeFont;
    const requestedFont = new Promise(resolve => { noticeFont = resolve; });
    await racePage.route('**/fraunces-latin.woff2', async route => {
      await new Promise(resolve => { releaseFont = resolve; noticeFont(); });
      await route.continue();
    });
    await racePage.locator('#textFontInput').selectOption('fraunces');
    await requestedFont;
    await racePage.locator('[data-side="back"]').click();
    releaseFont();
    await racePage.waitForFunction(() => document.querySelector('#renderState').textContent === 'Ready');
    assert.equal(await racePage.locator('#textFontInput').inputValue(), 'fira-code');
    const raceDrawings = await racePage.locator('#preview').evaluate(canvas => canvas.drawings);
    assert.ok(raceDrawings.filter(entry => entry.text).every(entry => entry.font.includes('Fira Code')), 'a slow front font cannot overwrite the later back preview');
    assert.ok(raceDrawings.some(entry => entry.image?.includes('-back.jpg')));
    await raceContext.close();
    console.log('Eight typefaces, independent text sizing and position, visible centering, persistence, print ZIP, order payload, and mobile layout: PASS');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
