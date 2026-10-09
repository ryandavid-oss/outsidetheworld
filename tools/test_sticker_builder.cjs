// Run against a local static server with Playwright and installed Chrome.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const base = process.env.OTW_TEST_URL || 'http://127.0.0.1:8936/sticker_builder.html';
const shots = process.env.OTW_SCREENSHOTS;
if (shots) fs.mkdirSync(shots, { recursive: true });

function zipFiles(bytes) {
  const files = new Map();
  for (let offset = 0; bytes.readUInt32LE(offset) === 0x04034b50;) {
    assert.equal(bytes.readUInt16LE(offset + 8), 0);
    const size = bytes.readUInt32LE(offset + 18), nameLength = bytes.readUInt16LE(offset + 26);
    const start = offset + 30 + nameLength + bytes.readUInt16LE(offset + 28);
    files.set(bytes.subarray(offset + 30, offset + 30 + nameLength).toString(), bytes.subarray(start, start + size));
    offset = start + size;
  }
  return files;
}

function pngInfo(bytes) {
  assert.equal(bytes.readUInt32BE(0), 0x89504e47);
  const density = [];
  for (let offset = 8; offset < bytes.length;) {
    const size = bytes.readUInt32BE(offset), type = bytes.subarray(offset + 4, offset + 8).toString();
    if (type === 'pHYs') density.push({ x: bytes.readUInt32BE(offset + 8), y: bytes.readUInt32BE(offset + 12), unit: bytes[offset + 16] });
    offset += 12 + size;
  }
  return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20), colorType: bytes[25], density };
}

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const ready = () => page.waitForFunction(() => document.querySelector('#renderState').textContent === 'Ready');
    const download = async selector => {
      const event = page.waitForEvent('download');
      await page.locator(selector).click();
      const result = await event;
      return fs.readFileSync(await result.path());
    };
    const range = async (selector, value) => {
      await page.locator(selector).evaluate((input, value) => {
        input.value = value; input.dispatchEvent(new Event('input', { bubbles: true }));
      }, String(value));
      await ready();
    };
    await page.goto(base); await ready();
    assert.equal(await page.locator('[data-artwork]').count(), 5);
    assert.equal(await page.locator('#stickerHeight').isVisible(), false, 'circles need only a diameter field');
    assert.equal(await page.locator('#artworkScale').isVisible(), false, 'the largest artwork fit stays the default');
    await page.locator('.scale-picker summary').focus();
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('#artworkScale').isVisible(), true, 'manual sizing remains available from the keyboard');
    await range('#artworkScale', 75);
    assert.equal(await page.locator('#scaleValue').textContent(), '75%');
    await page.locator('.scale-picker summary').click();
    assert.equal(await page.locator('#svgUpload').isVisible(), false, 'custom uploads stay tucked away until needed');
    const catalog = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/products/stickers.json')));
    for (const entry of catalog) {
      await page.locator(`[data-artwork="${entry.id}"]`).click(); await ready();
      assert.equal(await page.locator('#designReadout').textContent(), entry.label);
      const shape = entry.id.includes('wordmark') ? 'rounded' : 'circle';
      assert.equal(await page.locator(`[data-shape="${shape}"]`).getAttribute('aria-pressed'), 'true', 'each artwork starts in its intended shape');
      assert.equal(await page.locator('#stickerHeight').isVisible(), shape !== 'circle', 'height appears for rectangular stickers');
      assert.equal(await page.locator('#artworkScale').inputValue(), '100', 'artwork starts at the largest fit');
      assert.equal(await page.locator('[data-color="white"]').getAttribute('aria-pressed'), 'true');
      const svg = (await download('#exportSvg')).toString();
      const original = fs.readFileSync(path.join(__dirname, '..', entry.path), 'utf8');
      assert.equal((svg.match(/<path\b/g) || []).length, (original.match(/<path\b/g) || []).length, 'all vector paths survive export');
      if (shape === 'circle') {
        const coverage = await page.evaluate(async data => {
          const image = new Image(); image.src = 'data:image/png;base64,' + data; await image.decode();
          const canvas = document.createElement('canvas'); canvas.width = image.width; canvas.height = image.height;
          const ctx = canvas.getContext('2d'); ctx.drawImage(image, 0, 0);
          const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
          let radius = 0, left = canvas.width, right = 0;
          for (let y = 0; y < canvas.height; y++) for (let x = 0; x < canvas.width; x++) {
            const index = (y * canvas.width + x) * 4;
            if (pixels[index + 3] < 250 || Math.min(pixels[index], pixels[index + 1], pixels[index + 2]) > 245) continue;
            radius = Math.max(radius, Math.hypot(x + .5 - canvas.width / 2, y + .5 - canvas.height / 2));
            left = Math.min(left, x); right = Math.max(right, x);
          }
          return { border: canvas.width / 2 - radius, width: right - left, size: canvas.width,
            previewOutside: document.querySelector('#stickerPreview').getContext('2d').getImageData(600, 1090, 1, 1).data[3] };
        }, (await download('#exportPng')).toString('base64'));
        assert.ok(coverage.border >= 35 && coverage.border <= 39, 'the visible artwork fills the circle while retaining the selected white border');
        if (entry.id.startsWith('otw-')) assert.ok(coverage.width / coverage.size > .9, 'round OTW artwork fills over 90% of the sticker diameter');
        assert.equal(coverage.previewOutside, 0, 'the preview has no shadow outside the sticker');
      }
      if (shots) await page.locator('.preview-stage').screenshot({ path: `${shots}/${entry.id}.png` });
    }
    await page.locator('#stickerWidth').fill('5'); await ready();
    assert.ok(Number(await page.locator('#stickerHeight').inputValue()) > 1.35, 'wordmark height follows its width to keep the artwork large');
    await range('#borderSpacing', .3);
    assert.ok(Number(await page.locator('#stickerHeight').inputValue()) > 1.65, 'wordmark height accommodates the selected border');
    await page.locator('#stickerWidth').fill('3'); await range('#borderSpacing', .12);
    await page.locator('[data-artwork="frgmnts-brandmark-light"]').click(); await ready();
    await page.locator('[data-shape="rectangle"]').click(); await ready();
    await page.locator('#stickerWidth').fill('2.5');
    await page.locator('#stickerHeight').fill('1.25');
    await page.locator('#stickerQuantity').fill('250'); await ready();
    await range('#artworkScale', 100); await range('#borderSpacing', 0.15);
    const files = zipFiles(await download('#exportPackage'));
    assert.equal(files.size, 4);
    const file = suffix => [...files].find(([name]) => name.endsWith(suffix))[1];
    const svg = file('/artwork.svg').toString();
    assert.ok(svg.includes('width="2.5in"') && svg.includes('height="1.25in"') && svg.includes('viewBox="0 0 750 375"'));
    assert.deepEqual(pngInfo(file('/artwork.png')), { width: 750, height: 375, colorType: 6, density: [{ x: 11811, y: 11811, unit: 1 }] });
    assert.equal(file('/original.svg').toString(), fs.readFileSync(path.join(__dirname, '../Images/Stickers/frgmnts-brandmark-light.svg'), 'utf8'));
    const notes = file('/print-notes.txt').toString();
    assert.ok(notes.includes('Quantity: 250') && notes.includes('Size: 2.5 x 1.25 inches') && notes.includes('Shape: Rectangle'));
    assert.ok(notes.split('\n').length <= 12, 'printer notes remain short');

    await page.locator('[data-shape="circle"]').click(); await ready();
    assert.equal(await page.locator('#stickerHeight').isDisabled(), true);
    const circlePng = await download('#exportPng');
    assert.equal(pngInfo(circlePng).height, 750);
    const pixels = await page.evaluate(async data => {
      const image = new Image(); image.src = 'data:image/png;base64,' + data; await image.decode();
      const canvas = document.createElement('canvas'); canvas.width = image.width; canvas.height = image.height;
      const ctx = canvas.getContext('2d'); ctx.drawImage(image, 0, 0);
      return { corner: ctx.getImageData(0, 0, 1, 1).data[3], center: ctx.getImageData(image.width / 2, image.height / 2, 1, 1).data[3] };
    }, circlePng.toString('base64'));
    assert.deepEqual(pixels, { corner: 0, center: 255 });
    await page.locator('[data-color="ink"]').click(); await ready();
    assert.ok((await download('#exportSvg')).toString().includes('fill="#1a1c20"'));
    await page.locator('[data-shape="rounded"]').click(); await ready();
    assert.ok(/rx="[1-9][\d.]*"/.test((await download('#exportSvg')).toString()));
    if (shots) await page.screenshot({ path: `${shots}/desktop.png`, fullPage: true });

    await page.locator('#stickerWidth').fill('');
    assert.equal(await page.locator('#exportPackage').isDisabled(), true, 'empty dimensions cannot export stale sizing');
    await page.locator('#stickerWidth').fill('9');
    assert.equal(await page.locator('#exportSvg').isDisabled(), true, 'oversized dimensions cannot export');
    await page.locator('#stickerWidth').fill('3');
    await page.locator('#stickerQuantity').fill('1.5');
    assert.equal(await page.locator('#exportPng').isDisabled(), true, 'fractional quantities cannot export');
    await page.locator('#stickerQuantity').fill('100'); await ready();
    assert.equal(await page.locator('#exportPackage').isDisabled(), false);

    // Uploaded vectors stay local and are checked before they can replace the current artwork.
    await page.locator('.upload-picker summary').click();
    assert.equal(await page.locator('#svgUpload').isVisible(), true);
    await page.locator('#svgUpload').setInputFiles({ name: 'unsafe.svg', mimeType: 'image/svg+xml', buffer: Buffer.from('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><script>window.stickerInjected=true</script></svg>') });
    await page.waitForFunction(() => document.querySelector('#systemMessage').dataset.level === 'error');
    assert.equal(await page.evaluate(() => window.stickerInjected), undefined);
    assert.equal(await page.locator('#designReadout').textContent(), 'frgmnts mark');
    const custom = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50"><defs><linearGradient id="color"><stop stop-color="#6395ee"/><stop offset="1" stop-color="#91afb3"/></linearGradient></defs><rect width="100" height="50" fill="url(#color)"/></svg>';
    await page.locator('#svgUpload').setInputFiles({ name: 'my-design.svg', mimeType: 'image/svg+xml', buffer: Buffer.from(custom) });
    await page.waitForFunction(() => document.querySelector('#designReadout').textContent === 'my-design'); await ready();
    const customExport = (await download('#exportSvg')).toString();
    assert.ok(customExport.includes('id="design-color"') && customExport.includes('fill="url(#design-color)"'), 'local gradient references remain valid');

    // A slower first selection must not overwrite a later selection.
    await page.reload(); await ready();
    let release, pending;
    await page.route('**/otw-brandmark-dark.svg', async route => {
      if (route.request().resourceType() !== 'fetch') return route.continue();
      pending = new Promise(resolve => { release = resolve; });
      await pending; await route.continue();
    });
    await page.locator('[data-artwork="otw-brandmark-dark"]').click();
    while (!release) await new Promise(resolve => setTimeout(resolve, 20));
    await page.locator('[data-artwork="otw-brandmark-light"]').click(); await ready();
    release();
    await page.waitForResponse(response => response.url().endsWith('otw-brandmark-dark.svg') && response.request().resourceType() === 'fetch');
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    assert.equal(await page.locator('#designReadout').textContent(), 'OTW mark · light');

    await page.setViewportSize({ width: 390, height: 844 });
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'mobile fits viewport');
    if (shots) await page.screenshot({ path: `${shots}/mobile.png`, fullPage: true });
    await page.getByRole('link', { name: 'T-shirts', exact: true }).click();
    assert.ok(page.url().includes('tshirt_builder.html'));
    await page.getByRole('link', { name: 'Stickers', exact: true }).click(); await ready();
    assert.deepEqual(errors, []);
    console.log('Five sticker SVGs, default shapes, largest artwork fit, even white borders, shadow-free preview, 300 DPI exports, print ZIP, uploads, stale loads, and mobile layout: PASS');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
