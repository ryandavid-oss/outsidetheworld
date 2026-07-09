import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const root = path.resolve(new URL('..', import.meta.url).pathname);
const failures = [];
const warnings = [];

function fail(message) {
  failures.push(message);
}

function warn(message) {
  warnings.push(message);
}

function readText(relativePath) {
  const absolutePath = path.join(root, relativePath);
  if (!fs.existsSync(absolutePath)) {
    fail(`Missing required source: ${relativePath}`);
    return '';
  }
  return fs.readFileSync(absolutePath, 'utf8');
}

function loadScriptArray(relativePath, expression) {
  const source = readText(relativePath);
  if (!source) return [];
  const context = { window: {} };
  try {
    return vm.runInNewContext(`${source}; ${expression};`, context, {
      filename: relativePath,
      timeout: 1000
    });
  } catch (error) {
    fail(`Could not evaluate ${relativePath}: ${error.message}`);
    return [];
  }
}

function parseDate(value) {
  const date = new Date(value || '');
  return Number.isNaN(date.valueOf()) ? 0 : date.valueOf();
}

function slugify(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function archivePath(post) {
  if (post?.share_path) return post.share_path;
  const stem = String(post?.file || '').split('/').pop().replace(/\.md$/i, '');
  if (stem) return `archive/${stem}.html`;
  const date = new Date(post?.date || '');
  if (!Number.isNaN(date.valueOf())) {
    return `archive/${date.toISOString().slice(0, 10)}-${slugify(post?.title || 'untitled')}.html`;
  }
  return '';
}

function firstMarkdownImage(value) {
  return String(value || '').match(/!\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)/)?.[1] || '';
}

function firstPublisherImage(post) {
  const publisher = post?.publisher && typeof post.publisher === 'object' ? post.publisher : null;
  const image = publisher?.images?.find((candidate) => candidate?.url)?.url;
  if (image) return image;
  const block = publisher?.blocks?.find((candidate) => candidate?.type === 'image' && candidate?.url)?.url;
  return block || '';
}

function isRemoteUrl(value) {
  return /^https?:\/\//i.test(String(value || ''));
}

function localExists(relativePath) {
  return Boolean(relativePath) && fs.existsSync(path.join(root, relativePath));
}

function extractTagContent(html, selectorPattern) {
  const match = html.match(selectorPattern);
  return match ? match[1].trim() : '';
}

function countMatches(value, pattern) {
  return (String(value || '').match(pattern) || []).length;
}

function imageCandidates(post, fallbackImage = '') {
  return [firstPublisherImage(post), firstMarkdownImage(post?.body), post?.og_image, fallbackImage]
    .map((value) => String(value || '').trim())
    .filter((value, index, values) => value && values.indexOf(value) === index);
}

const indexHtml = readText('index.html');
const robotsTxt = readText('robots.txt');
const sitemapXml = readText('sitemap.xml');

const homepageTitle = extractTagContent(indexHtml, /<title>([\s\S]*?)<\/title>/i);
const homepageDescription = extractTagContent(indexHtml, /<meta\s+name=["']description["']\s+content=["']([^"']+)["']/i);
const homepageCanonical = extractTagContent(indexHtml, /<link\s+rel=["']canonical["']\s+href=["']([^"']+)["']/i);
const homepageRobots = extractTagContent(indexHtml, /<meta\s+name=["']robots["']\s+content=["']([^"']+)["']/i);
const homepageOgImage = extractTagContent(indexHtml, /<meta\s+property=["']og:image["']\s+content=["']([^"']+)["']/i);
const homepageTwitterImage = extractTagContent(indexHtml, /<meta\s+name=["']twitter:image["']\s+content=["']([^"']+)["']/i);
const socialPreviewPath = 'Images/og/otw-feed-1200x630.jpg';

if (homepageTitle !== 'Outside The World &mdash; Writing, Images, Fragments, and Work') {
  fail(`Homepage title is not the approved SEO title: ${homepageTitle || 'missing'}`);
}
if (homepageDescription !== 'Essays, poems, images, fragments, and professional work by Rylee Burningham.') {
  fail(`Homepage meta description is missing or unexpected: ${homepageDescription || 'missing'}`);
}
if (homepageCanonical !== 'https://outsidetheworld.com/') {
  fail(`Homepage canonical is missing or unexpected: ${homepageCanonical || 'missing'}`);
}
if (/noindex/i.test(homepageRobots)) {
  fail('Homepage robots meta contains noindex.');
}
if (!homepageOgImage.endsWith(`/${socialPreviewPath}`) || !localExists(socialPreviewPath)) {
  fail(`Homepage og:image should use the stable local preview: ${homepageOgImage || 'missing'}`);
}
if (!homepageTwitterImage.endsWith(`/${socialPreviewPath}`)) {
  fail(`Homepage twitter:image should use the stable local preview: ${homepageTwitterImage || 'missing'}`);
}
if (countMatches(indexHtml, /<h1\b/gi) !== 1) {
  fail('Homepage should contain exactly one h1 in initial HTML.');
}
if (!indexHtml.includes('<main class="front-page"')) fail('Homepage is missing a main landmark.');
if (!indexHtml.includes('href="personal.html"')) fail('Homepage is missing a crawlable Personal link.');
if (!indexHtml.includes('href="image_of_the_day.html"')) fail('Homepage is missing a crawlable Image of the Day link.');
if (!indexHtml.includes('href="drift_poetry.html"')) fail('Homepage is missing a crawlable Drift link.');
if (!indexHtml.includes('href="fragments.html"')) fail('Homepage is missing a crawlable frgmnts link.');
if (!indexHtml.includes('href="professional.html"')) fail('Homepage is missing a crawlable professional link.');
if (!robotsTxt.includes('Sitemap: https://outsidetheworld.com/sitemap.xml')) {
  fail('robots.txt does not reference the canonical sitemap.');
}
if (!sitemapXml.includes('<loc>https://outsidetheworld.com/</loc>')) {
  fail('sitemap.xml is missing the homepage URL.');
}

const frontpageManifest = (() => {
  const source = readText('frontpage_manifest.json');
  if (!source) return {};
  try {
    return JSON.parse(source);
  } catch (error) {
    fail(`frontpage_manifest.json is not valid JSON: ${error.message}`);
    return {};
  }
})();

const imageManifest = (() => {
  const source = readText('image_manifest.json');
  if (!source) return [];
  try {
    const parsed = JSON.parse(source);
    if (!Array.isArray(parsed)) {
      fail('image_manifest.json must be an array.');
      return [];
    }
    return parsed;
  } catch (error) {
    fail(`image_manifest.json is not valid JSON: ${error.message}`);
    return [];
  }
})();

const narratives = loadScriptArray('narrative_data.js', 'current_narrative');
const livingVerse = loadScriptArray('new_poetry_data.js', 'livingVerse');
const poetryArchive = loadScriptArray('poetry_data.js', 'archive');
const fragments = loadScriptArray('fragments_data.js', 'window.otw_fragments');

[
  ['frontpage_manifest.json', frontpageManifest],
  ['narrative_data.js', narratives],
  ['image_manifest.json', imageManifest],
  ['new_poetry_data.js', livingVerse],
  ['poetry_data.js', poetryArchive],
  ['fragments_data.js', fragments]
].forEach(([name, value]) => {
  if (Array.isArray(value) && !value.length) warn(`${name} is empty.`);
});

if (!frontpageManifest.lead?.type) fail('frontpage_manifest.json is missing a lead recipe.');

const sortedNarratives = [...(Array.isArray(narratives) ? narratives : [])]
  .filter((post) => post?.title && archivePath(post))
  .sort((a, b) => parseDate(b.date) - parseDate(a.date) || String(b.title).localeCompare(String(a.title)));

const latestEssay = sortedNarratives[0];
if (!latestEssay) {
  fail('No latest essay could be resolved from narrative_data.js.');
} else {
  const url = archivePath(latestEssay);
  if (!localExists(url)) fail(`Latest essay archive page is missing: ${url}`);
  if (!indexHtml.includes(`href="${url}"`)) {
    fail(`Homepage initial HTML does not link to the latest essay: ${url}`);
  }
  if (!indexHtml.includes(latestEssay.title)) {
    fail(`Homepage initial HTML does not include the latest essay title: ${latestEssay.title}`);
  }
  if (!sitemapXml.includes(`<loc>https://outsidetheworld.com/${url}</loc>`)) {
    fail(`sitemap.xml is missing the latest essay URL: ${url}`);
  }
  if (!parseDate(latestEssay.date)) fail(`Latest essay has an unparseable date: ${latestEssay.title}`);

  const newestImage = [...imageManifest]
    .filter((entry) => entry?.date && entry?.image)
    .sort((a, b) => parseDate(b.date) - parseDate(a.date))[0]?.image || '';
  const candidates = imageCandidates(latestEssay, newestImage);
  if (!candidates.length) {
    fail(`Latest essay has no homepage image candidates: ${latestEssay.title}`);
  }
  if (!candidates.some((candidate) => isRemoteUrl(candidate) || localExists(candidate))) {
    fail(`Latest essay image candidates do not resolve locally or remotely: ${latestEssay.title}`);
  }
  if (latestEssay.og_image && !localExists(latestEssay.og_image)) {
    fail(`Latest essay local OG fallback is missing: ${latestEssay.og_image}`);
  }
}

const jsonLdBlocks = [...indexHtml.matchAll(/<script\s+type=["']application\/ld\+json["']>([\s\S]*?)<\/script>/gi)]
  .map((match) => match[1].trim());
if (!jsonLdBlocks.length) {
  fail('Homepage is missing JSON-LD structured data.');
}
jsonLdBlocks.forEach((block, index) => {
  try {
    const parsed = JSON.parse(block);
    const graph = Array.isArray(parsed['@graph']) ? parsed['@graph'] : [parsed];
    if (!graph.some((node) => node['@type'] === 'WebSite')) fail(`JSON-LD block ${index + 1} is missing WebSite data.`);
    if (!graph.some((node) => node['@type'] === 'WebPage')) fail(`JSON-LD block ${index + 1} is missing WebPage data.`);
    if (!graph.some((node) => node['@type'] === 'ItemList')) fail(`JSON-LD block ${index + 1} is missing ItemList data.`);
  } catch (error) {
    fail(`Homepage JSON-LD block ${index + 1} is not valid JSON: ${error.message}`);
  }
});

imageManifest.forEach((entry, index) => {
  if (!entry?.date) fail(`image_manifest.json entry ${index} is missing date.`);
  if (!parseDate(entry?.date)) fail(`image_manifest.json entry ${index} has an unparseable date: ${entry?.date}`);
  if (!entry?.image) fail(`image_manifest.json entry ${index} is missing image.`);
});

const duplicateSlots = new Set();
[frontpageManifest.lead, ...(frontpageManifest.modules || []), ...(frontpageManifest.rail || [])]
  .filter(Boolean)
  .forEach((rule) => {
    if (!rule.slot) fail('A frontpage recipe is missing slot.');
    if (duplicateSlots.has(rule.slot)) fail(`Duplicate homepage slot: ${rule.slot}`);
    duplicateSlots.add(rule.slot);
  });

if (warnings.length) {
  console.warn(`Warnings (${warnings.length}):`);
  warnings.forEach((message) => console.warn(`- ${message}`));
}

if (failures.length) {
  console.error(`Failures (${failures.length}):`);
  failures.forEach((message) => console.error(`- ${message}`));
  process.exit(1);
}

console.log('Frontpage audit OK');
console.log(`Latest essay: ${latestEssay?.title || 'n/a'}`);
console.log(`Narratives: ${sortedNarratives.length}`);
console.log(`IOTD entries: ${imageManifest.length}`);
console.log(`Living poems: ${Array.isArray(livingVerse) ? livingVerse.length : 0}`);
console.log(`Recovered poems: ${Array.isArray(poetryArchive) ? poetryArchive.length : 0}`);
console.log(`frgmnts: ${Array.isArray(fragments) ? fragments.length : 0}`);
