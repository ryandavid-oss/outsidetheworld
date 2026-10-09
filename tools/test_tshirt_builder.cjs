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
    await context.addInitScript(() => {
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
        this.canvas.drawings.push({ text: value, point: args });
        return text.call(this, value, ...args);
      };
    });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const ready = () => page.waitForFunction(() => document.querySelector('#renderState').textContent === 'Ready to play');
    const side = async value => { await page.locator(`[data-side="${value}"]`).first().click(); await ready(); };
    const size = async value => {
      await page.locator('#artSizeInput').evaluate((input, value) => {
        input.value = value; input.dispatchEvent(new Event('input', { bubbles: true }));
      }, String(value));
      await ready();
    };
    const drawing = () => page.locator('#preview').evaluate(canvas => canvas.drawings);
    const frontText = 'Hi_fr gmnts\nRyan & friends';
    const backText = 'Made for friends\nArizona, 2026.';

    await page.goto(base); await ready();
    assert.equal(await page.locator('#artSizeInput').inputValue(), '100');
    await size(75);
    assert.equal((await drawing()).find(entry => entry.image?.startsWith('blob:')).box[2], 210);
    await page.locator('#customTextInput').fill(frontText); await ready();
    assert.equal((await drawing()).filter(entry => entry.text).map(entry => entry.text).join(''), frontText.replaceAll('\n', ''));
    await side('back'); await size(125);
    assert.equal((await drawing()).find(entry => entry.image?.startsWith('blob:')).box[2], 1000);
    await page.locator('#customTextInput').fill(backText); await ready();
    await side('front');
    assert.equal(await page.locator('#artSizeInput').inputValue(), '75');
    assert.equal(await page.locator('#customTextInput').inputValue(), frontText);
    if (shots) await page.screenshot({ path: `${shots}/desktop-front.png`, fullPage: true });
    await page.locator('#keepButton').click();
    const shared = page.url();
    const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('otw-frgmnts-shirt-build-v1')));
    assert.equal(saved.frontArtSize, 75); assert.equal(saved.backArtSize, 125);
    assert.equal(saved.frontSlogan, frontText); assert.equal(saved.slogan, backText);
    await page.goto(base); await page.reload(); await ready();
    assert.equal(await page.locator('#customTextInput').inputValue(), frontText, 'device restore');
    await page.evaluate(() => localStorage.clear());
    await page.goto(shared); await page.reload(); await ready();
    assert.equal(await page.locator('#customTextInput').inputValue(), frontText, 'shared link restore');
    await side('back');
    assert.equal(await page.locator('#customTextInput').inputValue(), backText);
    assert.equal(await page.locator('#artSizeInput').inputValue(), '125');

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
    assert.ok(spec.includes('Total shirts: 3') && spec.includes('BLACK - M x 2') && spec.includes('WHITE - L x 1'));
    assert.ok(spec.split('\n').length < 50, 'printer instructions stay concise');
    for (const color of ['black', 'white']) for (const textSide of ['front', 'back']) {
      const [, png] = [...files].find(([name]) => name.includes(`/colorways/${color}/artwork/${textSide}-text-`));
      assert.equal(png.readUInt32BE(0), 0x89504e47);
      assert.equal(png[25], 6, 'text production artwork has an alpha channel');
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
    await page.locator('#orderCloseButton').click();

    await page.goto(base + '#body=long&color=white&front=frgmnts&back=brandmark&words=THE_ANALOG_DAWN');
    await page.reload(); await ready();
    assert.equal(await page.locator('#artSizeInput').inputValue(), '100', 'legacy links use original size');
    await side('back');
    assert.equal(await page.locator('#customTextInput').inputValue(), 'THE ANALOG DAWN');
    await size(150); await ready();
    const logo = (await drawing()).find(entry => entry.image?.startsWith('blob:'));
    assert.ok(logo.box[1] >= 200, 'large graphics stay below the collar');
    await page.locator('#customTextInput').fill('X'.repeat(80)); await ready();
    assert.equal((await drawing()).filter(entry => entry.text).length, 80, 'long custom text is rendered, not dropped');
    await page.locator('#phraseGrid [data-words-off]').click(); await ready();
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
    console.log('T-shirt sizing, text, persistence, print ZIP, order payload, and mobile layout: PASS');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
