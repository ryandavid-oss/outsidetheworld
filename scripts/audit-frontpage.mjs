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

function imageCandidates(post, fallbackImage = '') {
  return [firstPublisherImage(post), firstMarkdownImage(post?.body), post?.og_image, fallbackImage]
    .map((value) => String(value || '').trim())
    .filter((value, index, values) => value && values.indexOf(value) === index);
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
