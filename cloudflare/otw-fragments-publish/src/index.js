const FRAGMENTS_PATH = "fragments_data.js";
const FRAGMENTS_USER_REGISTRY_PATH = "fragments_users.json";
const CHANGELOG_PATH = "changelog.json";
const IMAGE_MANIFEST_PATH = "image_manifest.json";
const WORDPERSON_MANIFEST_PATH = "wordperson_manifest.json";
const DRIFT_POETRY_PATH = "new_poetry_data.js";
const CURRENT_NARRATIVE_DIR = "current_narrative";
const FRAGMENTS_PATTERN = /window\.otw_fragments\s*=\s*(\[[\s\S]*?\])\s*;/m;
const DRIFT_POETRY_PATTERN = /const livingVerse\s*=\s*(\[[\s\S]*?\])\s*;/m;

const BOT_POOL = [
  "OTW_Bot has detected elevated emotional weather in this sector. Recommend hydration and one less tab open.",
  "Signal integrity remains acceptable. Human operator appears melodramatic but functional.",
  "Reminder: not every passing thought is a crisis. Some of them are just undercaffeinated.",
  "Your archive is not messy. It is merely experiencing historical abundance.",
  "OTW_Bot would like to congratulate you on surviving another completely unnecessary worry spiral.",
  "Please note that three good paragraphs are sometimes superior to one tortured masterpiece.",
  "There is no shame in posting a fragment instead of an essay. Efficiency is a virtue.",
  "Current recommendation: close the tab, keep the insight.",
  "Minor alert: your perfectionism has mistaken itself for taste again.",
  "OTW_Bot supports your right to leave some thoughts at one paragraph and walk away.",
  "Try not to build a cathedral every time all you need is a porch light.",
  "A passing thought has requested asylum. Fragment status granted.",
  "A fragment is simply a blog post that declined to put on formalwear.",
  "Not all signals are urgent. Some just want witness.",
  "OTW_Bot suggests you trust the reader more and explain yourself less.",
  "The signal was never lost. It was merely avoiding committee review.",
  "OTW_Bot believes in the power of one clean sentence and then leaving people alone.",
  "A reminder from the machinery: being memorable is not the same as being loud.",
  "The shortest route to coherence is often simply saying the thing plainly.",
  "You are allowed to keep the post small and the feeling true."
];

function corsHeaders() {
  return {
    "access-control-allow-origin": "*",
    "access-control-allow-methods": "GET,POST,OPTIONS",
    "access-control-allow-headers": "content-type,x-publish-key"
  };
}

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      ...corsHeaders()
    }
  });
}

function getPublishHeader(request) {
  return String(request.headers.get("x-publish-key") || "").trim();
}

function matchesSecret(key, secret) {
  return Boolean(key && secret && key === secret);
}

function isAuthorized(request, env) {
  const key = getPublishHeader(request);
  return matchesSecret(key, env.PUBLISH_KEY);
}

function isWordpersonAuthorized(request, env) {
  const key = getPublishHeader(request);
  return matchesSecret(key, env.WORDPERSON_PUBLISH_KEY);
}

function isFamilyFeedAuthorized(request, env) {
  const key = getPublishHeader(request);
  return matchesSecret(key, env.PUBLISH_KEY) || matchesSecret(key, env.WORDPERSON_PUBLISH_KEY);
}

function decodeBase64Utf8(content) {
  const binary = atob(content.replace(/\n/g, ""));
  const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
  return new TextDecoder("utf-8").decode(bytes);
}

function encodeBase64Utf8(content) {
  const bytes = new TextEncoder().encode(content);
  let binary = "";
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary);
}

function normalizeTag(raw) {
  const tag = String(raw || "FRAGMENT").trim().toUpperCase();
  return tag.replace(/[^A-Z0-9]+/g, "_").replace(/^_+|_+$/g, "") || "FRAGMENT";
}

function normalizeTimestamp(raw) {
  if (!raw) {
    return new Date().toISOString();
  }
  const value = new Date(raw);
  if (Number.isNaN(value.getTime())) {
    throw new Error("Invalid timestamp");
  }
  return value.toISOString();
}

function normalizeFragmentEntry(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Fragment payload must be an object");
  }

  const text = String(entry.text || "").trim();
  if (!text) {
    throw new Error("Fragment text is required");
  }

  const normalized = {
    timestamp: normalizeTimestamp(entry.timestamp),
    text,
    tag: normalizeTag(entry.tag)
  };

  if (entry.author_id) {
    normalized.author_id = String(entry.author_id).trim();
  }

  if (entry.author) {
    normalized.author = String(entry.author).trim();
  }

  if (entry.author_handle) {
    normalized.author_handle = String(entry.author_handle).trim();
  }

  return normalized;
}

function normalizeFragmentsUser(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Fragments user registry entry must be an object");
  }

  const id = String(entry.id || "").trim();
  const name = String(entry.name || "").trim();
  const handle = String(entry.handle || "").trim();
  const avatar = String(entry.avatar || "").trim();
  const publishKeySecretName = entry.publishKeySecretName == null
    ? null
    : String(entry.publishKeySecretName).trim();

  if (!id) {
    throw new Error("Fragments user registry entry is missing id");
  }

  if (!name) {
    throw new Error(`Fragments user ${id} is missing name`);
  }

  if (!handle) {
    throw new Error(`Fragments user ${id} is missing handle`);
  }

  return {
    id,
    name,
    handle: handle.startsWith("@") ? handle : `@${handle}`,
    avatar,
    publishKeySecretName,
    verified: entry.verified === true
  };
}

function publicFragmentsUser(user) {
  return {
    id: user.id,
    name: user.name,
    handle: user.handle,
    avatar: user.avatar,
    verified: user.verified === true
  };
}

function dedupeFragments(entries) {
  const seen = new Set();
  const out = [];

  for (const entry of entries) {
    const normalized = normalizeFragmentEntry(entry);
    const key = [
      normalized.timestamp,
      String(normalized.author || "").trim(),
      String(normalized.author_handle || "").trim(),
      normalized.tag,
      normalized.text
    ].join("||");

    if (seen.has(key)) continue;
    seen.add(key);
    out.push(normalized);
  }

  return out;
}

function normalizeChangelogEntry(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Changelog payload must be an object");
  }

  const date = String(entry.date || "").trim();
  const type = String(entry.type || "Other").trim() || "Other";
  const text = String(entry.text || "").trim();

  if (date.length !== 10 || date[4] !== "-" || date[7] !== "-") {
    throw new Error("Changelog date must be in YYYY-MM-DD format");
  }

  if (!text) {
    throw new Error("Changelog text is required");
  }

  return { date, type, text };
}

function normalizeNarrativeDate(raw) {
  const date = String(raw || "").trim();
  if (date.length !== 10 || date[4] !== "-" || date[7] !== "-") {
    throw new Error("Narrative date must be in YYYY-MM-DD format");
  }
  return date;
}

function stripMarkdownForTitle(value) {
  return String(value || "")
    .replace(/<[^>]+>/g, " ")
    .replace(/[#>*_`-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function slugify(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function deriveNarrativeTitle(body) {
  const lines = String(body || "")
    .split(/\r?\n/)
    .map((line) => stripMarkdownForTitle(line))
    .filter(Boolean);

  return lines[0] || "Untitled draft";
}

function normalizeNarrativeEntry(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Narrative payload must be an object");
  }

  const body = String(entry.body || "").trim();
  if (!body) {
    throw new Error("Narrative body is required");
  }

  const date = normalizeNarrativeDate(entry.date);
  const rawTitle = String(entry.title || "").trim();
  const title = rawTitle || deriveNarrativeTitle(body);

  if (!title) {
    throw new Error("Narrative title could not be derived");
  }

  return { title, date, body };
}

function normalizeDriftDate(raw) {
  const date = String(raw || "").trim();
  if (date.length !== 10 || date[4] !== "-" || date[7] !== "-") {
    throw new Error("Drift date must be in YYYY-MM-DD format");
  }
  return date;
}

function formatDriftDate(raw) {
  const date = normalizeDriftDate(raw);
  const value = new Date(`${date}T12:00:00`);
  if (Number.isNaN(value.getTime())) {
    throw new Error("Drift date could not be formatted");
  }
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric"
  }).format(value);
}

function deriveDriftTitle(body) {
  const firstLine = String(body || "")
    .split(/\r?\n/)
    .map((line) => stripMarkdownForTitle(line))
    .find(Boolean);

  if (!firstLine) {
    return "Untitled drift";
  }

  return firstLine.length > 72
    ? `${firstLine.slice(0, 69).trimEnd()}...`
    : firstLine;
}

function inferDriftTheme(entry) {
  const text = `${entry?.title || ""} ${entry?.body || ""}`.toLowerCase();
  const themeRules = [
    { theme: "Longing", words: ["long", "wish", "promise", "yearn", "waiting", "remember", "memory"] },
    { theme: "Night", words: ["night", "moon", "stars", "winter", "dark", "evening"] },
    { theme: "Nature", words: ["wind", "mountain", "desert", "sky", "rain", "cloud", "horizon"] },
    { theme: "Becoming", words: ["grow", "become", "change", "path", "begin", "future"] },
    { theme: "Devotion", words: ["believe", "faith", "promise", "grace", "soul", "heart"] },
    { theme: "Solitude", words: ["alone", "solitary", "quiet", "silence", "friend", "invisible"] }
  ];

  let bestTheme = "Drift";
  let bestScore = 0;

  themeRules.forEach(({ theme, words }) => {
    const score = words.reduce((total, word) => total + (text.includes(word) ? 1 : 0), 0);
    if (score > bestScore) {
      bestTheme = theme;
      bestScore = score;
    }
  });

  return bestTheme;
}

function hashString(value) {
  let hash = 0;
  for (const char of String(value || "")) {
    hash = ((hash << 5) - hash) + char.charCodeAt(0);
    hash |= 0;
  }
  return Math.abs(hash);
}

function buildDriftThumbprint(entry) {
  const theme = inferDriftTheme(entry);
  const palettes = {
    Drift: [
      "linear-gradient(135deg, #1f3558 0%, #0f1728 46%, #47285f 100%)",
      "linear-gradient(135deg, #192c4b 0%, #1b2438 48%, #39506f 100%)"
    ],
    Longing: [
      "linear-gradient(135deg, #5c3659 0%, #182848 52%, #c06c84 100%)",
      "linear-gradient(135deg, #4a2947 0%, #1f3558 54%, #b4769f 100%)"
    ],
    Night: [
      "linear-gradient(135deg, #0f2027 0%, #203a43 48%, #2c5364 100%)",
      "linear-gradient(135deg, #182848 0%, #1f3558 45%, #4b6cb7 100%)"
    ],
    Nature: [
      "linear-gradient(135deg, #1f4037 0%, #213b3a 46%, #6ca485 100%)",
      "linear-gradient(135deg, #29443a 0%, #355c7d 50%, #6c8b6f 100%)"
    ],
    Becoming: [
      "linear-gradient(135deg, #355c7d 0%, #6c5b7b 52%, #8aa7d9 100%)",
      "linear-gradient(135deg, #2d4a69 0%, #5f4f86 52%, #88a4db 100%)"
    ],
    Devotion: [
      "linear-gradient(135deg, #3d2a55 0%, #5e3f76 52%, #d9c08c 100%)",
      "linear-gradient(135deg, #4f2853 0%, #5a4580 56%, #c9a86a 100%)"
    ],
    Solitude: [
      "linear-gradient(135deg, #22313f 0%, #3a4c63 52%, #7f8fa6 100%)",
      "linear-gradient(135deg, #233142 0%, #37445c 50%, #6f82a1 100%)"
    ]
  };

  const palette = palettes[theme] || palettes.Drift;
  const index = hashString(`${entry.title} ${entry.body}`) % palette.length;
  return palette[index];
}

function normalizeDriftPoemEntry(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Drift payload must be an object");
  }

  const body = String(entry.body || "").trim();
  if (!body) {
    throw new Error("Drift body is required");
  }

  const date = normalizeDriftDate(entry.date);
  const title = String(entry.title || "").trim() || deriveDriftTitle(body);
  const source = String(entry.source || "drift_publisher").trim() || "drift_publisher";
  const era = String(entry.era || "CURRENT_SIGNAL").trim().toUpperCase() || "CURRENT_SIGNAL";
  const thumbprint = String(entry.thumbprint || "").trim() || buildDriftThumbprint({ title, body });

  return {
    title,
    date: formatDriftDate(date),
    era,
    source,
    thumbprint,
    body
  };
}

function normalizeIotdDate(raw) {
  const date = String(raw || "").trim();
  if (date.length !== 10 || date[4] !== "-" || date[7] !== "-") {
    throw new Error("IOTD date must be in YYYY-MM-DD format");
  }
  return date;
}

function sanitizeIotdTitle(raw) {
  return String(raw || "UNTITLED_SIGNAL")
    .trim()
    .replace(/\s+/g, "_")
    .toUpperCase() || "UNTITLED_SIGNAL";
}

function detectImageExtension(file) {
  const fromName = String(file?.name || "").trim().toLowerCase();
  if (fromName.includes(".")) {
    const ext = fromName.split(".").pop();
    if (ext) return ext;
  }

  const mime = String(file?.type || "").toLowerCase();
  if (mime === "image/jpeg") return "jpg";
  if (mime === "image/png") return "png";
  if (mime === "image/gif") return "gif";
  if (mime === "image/webp") return "webp";

  return "jpg";
}

function buildIotdObjectKey(date, extension) {
  return `${date}.${extension}`;
}

function buildIotdImageUrl(env, objectKey) {
  const base = String(env.IOTD_PUBLIC_BASE_URL || "").replace(/\/+$/g, "");
  if (!base) {
    throw new Error("IOTD public base URL is not configured");
  }
  return `${base}/${objectKey}`;
}

function normalizeNarrativeImageAlt(raw) {
  return String(raw || "").trim() || "Narrative image";
}

function normalizeNarrativeImageCaption(raw) {
  return String(raw || "").trim();
}

function getNarrativePublicBaseUrl(env) {
  const base = String(env.NARRATIVE_PUBLIC_BASE_URL || env.IOTD_PUBLIC_BASE_URL || "").replace(/\/+$/g, "");
  if (!base) {
    throw new Error("Narrative public base URL is not configured");
  }
  return base;
}

function buildNarrativeImageUrl(env, objectKey) {
  return `${getNarrativePublicBaseUrl(env)}/${objectKey}`;
}

function buildNarrativeImageObjectKey(date, title, extension) {
  const titleSlug = slugify(title) || "untitled-draft";
  const stamp = Date.now().toString(36);
  return `narrative/${date}-${titleSlug}-${stamp}.${extension}`;
}

function escapeHtmlAttr(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function buildNarrativeImageSnippets({ url, alt, caption }) {
  const safeUrl = escapeHtmlAttr(url);
  const safeAlt = escapeHtmlAttr(alt);
  const safeCaption = escapeHtmlAttr(caption);
  const markdown = `![${alt}](${url})`;
  const figure = caption
    ? `<figure>\n  <img src="${safeUrl}" alt="${safeAlt}">\n  <figcaption><em>${safeCaption}</em></figcaption>\n</figure>`
    : `<figure>\n  <img src="${safeUrl}" alt="${safeAlt}">\n</figure>`;

  return { markdown, figure };
}

function normalizeIotdCaption(raw) {
  return String(raw || "").trim();
}

function normalizeIotdTitleForFilename(title) {
  return sanitizeIotdTitle(title);
}

function normalizeIotdEntry(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("IOTD payload must be an object");
  }

  const date = normalizeIotdDate(entry.date);
  const title = normalizeIotdTitleForFilename(entry.title);
  const caption = normalizeIotdCaption(entry.caption);
  const image = String(entry.image || "").trim();

  if (!image) {
    throw new Error("IOTD image URL is required");
  }

  return { date, title, caption, image };
}

function normalizeWordpersonDate(raw) {
  const value = String(raw || "").trim();
  if (!value) {
    return new Date().toISOString().slice(0, 10);
  }
  if (value.length !== 10 || value[4] !== "-" || value[7] !== "-") {
    throw new Error("word.person date must be in YYYY-MM-DD format");
  }
  return value;
}

function normalizeWordpersonBody(raw) {
  const body = String(raw || "").trim();
  if (!body) {
    throw new Error("word.person body is required");
  }
  return body;
}

function deriveWordpersonTitle(body) {
  const cleaned = stripMarkdownForTitle(body);
  if (!cleaned) {
    return "Untitled reflection";
  }

  const firstSentence = cleaned.split(/(?<=[.!?])\s+/)[0]?.trim() || cleaned;
  return firstSentence.length > 72 ? `${firstSentence.slice(0, 69).trimEnd()}...` : firstSentence;
}

function normalizeWordpersonTitle(raw, body) {
  const title = String(raw || "").trim();
  return title || deriveWordpersonTitle(body);
}

function deriveWordpersonExcerpt(body) {
  const firstParagraph = String(body || "")
    .split(/\n\s*\n/)
    .map((part) => stripMarkdownForTitle(part))
    .find(Boolean);

  const source = firstParagraph || stripMarkdownForTitle(body);
  if (!source) {
    return "";
  }

  return source.length > 190 ? `${source.slice(0, 187).trimEnd()}...` : source;
}

function normalizeWordpersonAlt(raw, title) {
  const alt = String(raw || "").trim();
  return alt || title;
}

function buildWordpersonImageUrl(env, objectKey) {
  const base = String(env.IOTD_PUBLIC_BASE_URL || "").replace(/\/+$/g, "");
  if (!base) {
    throw new Error("Public image base URL is not configured");
  }
  return `${base}/${objectKey}`;
}

function normalizeWordpersonEntry(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("word.person payload must be an object");
  }

  const date = normalizeWordpersonDate(entry.date);
  const body = normalizeWordpersonBody(entry.body);
  const title = normalizeWordpersonTitle(entry.title, body);
  const excerpt = String(entry.excerpt || "").trim() || deriveWordpersonExcerpt(body);
  const image = String(entry.image || "").trim();
  const alt = normalizeWordpersonAlt(entry.alt, title);
  const id = String(entry.id || "").trim();

  if (!image) {
    throw new Error("word.person image URL is required");
  }

  if (!id) {
    throw new Error("word.person id is required");
  }

  return { id, date, title, image, alt, excerpt, body };
}

function dedupeWordperson(entries) {
  const seen = new Set();
  const out = [];

  for (const entry of entries) {
    const normalized = normalizeWordpersonEntry(entry);
    if (seen.has(normalized.id)) continue;
    seen.add(normalized.id);
    out.push(normalized);
  }

  return out;
}

function dedupeIotd(entries) {
  const seen = new Set();
  const out = [];

  for (const entry of entries) {
    const normalized = normalizeIotdEntry(entry);
    const key = normalized.date;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(normalized);
  }

  return out;
}

function dedupeChangelog(entries) {
  const seen = new Set();
  const out = [];

  for (const entry of entries) {
    const normalized = normalizeChangelogEntry(entry);
    const key = [
      normalized.date,
      normalized.type.trim().toLowerCase(),
      normalized.text.trim().toLowerCase()
    ].join("||");

    if (seen.has(key)) continue;
    seen.add(key);
    out.push(normalized);
  }

  return out;
}

async function githubRequest(env, path, options = {}) {
  const response = await fetch(`https://api.github.com${path}`, {
    ...options,
    headers: {
      authorization: `Bearer ${env.GITHUB_TOKEN}`,
      accept: "application/vnd.github+json",
      "user-agent": "otw-fragments-publish-worker",
      ...(options.headers || {})
    }
  });
  return response;
}

async function loadRepoFile(env, path) {
  const response = await githubRequest(
    env,
    `/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/${path}?ref=${env.GITHUB_BRANCH}`
  );

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Could not load ${path}: ${response.status} ${text}`);
  }

  const payload = await response.json();
  const raw = decodeBase64Utf8(payload.content);
  return { sha: payload.sha, raw };
}

async function saveRepoFile(env, path, content, sha, message) {
  const encoded = encodeBase64Utf8(content);
  const response = await githubRequest(
    env,
    `/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/${path}`,
    {
      method: "PUT",
      headers: {
        "content-type": "application/json; charset=utf-8"
      },
      body: JSON.stringify({
        message,
        content: encoded,
        ...(sha ? { sha } : {}),
        branch: env.GITHUB_BRANCH
      })
    }
  );

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Could not save ${path}: ${response.status} ${text}`);
  }

  return response.json();
}

async function loadFragmentsFile(env) {
  const file = await loadRepoFile(env, FRAGMENTS_PATH);
  const match = file.raw.match(FRAGMENTS_PATTERN);
  if (!match) {
    throw new Error("Could not locate window.otw_fragments in fragments_data.js");
  }

  let fragments;
  try {
    fragments = JSON.parse(match[1]);
  } catch (error) {
    throw new Error(`Could not parse fragments array: ${error.message}`);
  }

  if (!Array.isArray(fragments)) {
    throw new Error("window.otw_fragments is not an array");
  }

  return { ...file, fragments };
}

async function loadFragmentsUserRegistry(env) {
  const file = await loadRepoFile(env, FRAGMENTS_USER_REGISTRY_PATH);
  let entries;

  try {
    entries = JSON.parse(file.raw);
  } catch (error) {
    throw new Error(`Could not parse ${FRAGMENTS_USER_REGISTRY_PATH}: ${error.message}`);
  }

  if (!Array.isArray(entries)) {
    throw new Error(`${FRAGMENTS_USER_REGISTRY_PATH} is not an array`);
  }

  return entries.map(normalizeFragmentsUser);
}

function resolveRegisteredFragmentsUser(key, env, users) {
  const publishKey = String(key || "").trim();
  if (!publishKey) {
    return null;
  }

  for (const user of users) {
    if (!user.publishKeySecretName) {
      continue;
    }

    const expectedSecret = String(env[user.publishKeySecretName] || "").trim();
    if (matchesSecret(publishKey, expectedSecret)) {
      return user;
    }
  }

  return null;
}

function getFragmentsUserById(users, id) {
  return users.find((user) => user.id === id) || null;
}

async function getAuthorizedFragmentsUser(request, env) {
  const users = await loadFragmentsUserRegistry(env);
  const user = resolveRegisteredFragmentsUser(getPublishHeader(request), env, users);
  return { users, user };
}

function buildRegisteredFragmentEntry(payload, user) {
  const normalized = normalizeFragmentEntry(payload);
  return {
    ...normalized,
    author_id: user.id,
    author: user.name,
    author_handle: user.handle
  };
}

function replaceFragmentsArray(raw, entries) {
  const replacement = `window.otw_fragments = ${JSON.stringify(entries, null, 2)};`;
  return raw.replace(FRAGMENTS_PATTERN, replacement);
}

function isGithubConflictError(error) {
  const message = String(error?.message || "");
  return message.includes("Could not save") && message.includes("409");
}

async function saveFragmentEntryWithRetry(env, entry, message, maxAttempts = 3) {
  let lastError = null;

  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      const file = await loadFragmentsFile(env);
      const merged = sortFragments(dedupeFragments([entry, ...file.fragments]));
      const updatedRaw = replaceFragmentsArray(file.raw, merged);
      const result = await saveRepoFile(env, FRAGMENTS_PATH, updatedRaw, file.sha, message);
      return { result, merged };
    } catch (error) {
      lastError = error;
      if (!isGithubConflictError(error) || attempt === maxAttempts) {
        throw error;
      }
    }
  }

  throw lastError || new Error("Fragment publish retry failed");
}

async function loadChangelogFile(env) {
  const file = await loadRepoFile(env, CHANGELOG_PATH);
  let entries;
  try {
    entries = JSON.parse(file.raw);
  } catch (error) {
    throw new Error(`Could not parse changelog.json: ${error.message}`);
  }

  if (!Array.isArray(entries)) {
    throw new Error("changelog.json is not an array");
  }

  return { ...file, entries };
}

async function loadImageManifestFile(env) {
  const file = await loadRepoFile(env, IMAGE_MANIFEST_PATH);
  let entries;
  try {
    entries = JSON.parse(file.raw);
  } catch (error) {
    throw new Error(`Could not parse image_manifest.json: ${error.message}`);
  }

  if (!Array.isArray(entries)) {
    throw new Error("image_manifest.json is not an array");
  }

  return { ...file, entries };
}

async function loadWordpersonManifestFile(env) {
  const file = await loadRepoFile(env, WORDPERSON_MANIFEST_PATH);
  let entries;
  try {
    entries = JSON.parse(file.raw);
  } catch (error) {
    throw new Error(`Could not parse wordperson_manifest.json: ${error.message}`);
  }

  if (!Array.isArray(entries)) {
    throw new Error("wordperson_manifest.json is not an array");
  }

  return { ...file, entries };
}

async function loadDriftPoetryFile(env) {
  const file = await loadRepoFile(env, DRIFT_POETRY_PATH);
  const match = file.raw.match(DRIFT_POETRY_PATTERN);
  if (!match) {
    throw new Error("Could not locate livingVerse in new_poetry_data.js");
  }

  let entries;
  try {
    entries = JSON.parse(match[1]);
  } catch (error) {
    throw new Error(`Could not parse livingVerse array: ${error.message}`);
  }

  if (!Array.isArray(entries)) {
    throw new Error("livingVerse is not an array");
  }

  return { ...file, entries };
}

function sortFragments(entries) {
  return entries.slice().sort((a, b) => String(b.timestamp || "").localeCompare(String(a.timestamp || "")));
}

function sortChangelog(entries) {
  return entries.slice().sort((a, b) => String(b.date || "").localeCompare(String(a.date || "")));
}

function sortIotd(entries) {
  return entries.slice().sort((a, b) => String(b.date || "").localeCompare(String(a.date || "")));
}

function sortWordperson(entries) {
  return entries.slice().sort((a, b) => String(b.date || "").localeCompare(String(a.date || "")));
}

function sortDriftPoetry(entries) {
  return entries.slice().sort((a, b) => {
    const aTime = new Date(String(a.date || "")).getTime() || 0;
    const bTime = new Date(String(b.date || "")).getTime() || 0;
    if (bTime !== aTime) {
      return bTime - aTime;
    }
    return String(a.title || "").localeCompare(String(b.title || ""));
  });
}

function buildUniqueDriftId(existingEntries, date, title) {
  const titleSlug = slugify(title);
  for (let attempt = 0; attempt < 50; attempt += 1) {
    const suffix = attempt === 0 ? "" : `-${attempt + 1}`;
    const id = titleSlug
      ? `living-poem-${date}-${titleSlug}${suffix}`
      : `living-poem-${date}${suffix}`;
    if (!existingEntries.some((entry) => String(entry.id || "") === id)) {
      return id;
    }
  }

  throw new Error("Could not find an available Drift poem id");
}

function dedupeDriftPoetry(entries) {
  const seen = new Set();
  const out = [];

  for (const entry of entries) {
    const id = String(entry?.id || "").trim();
    if (!id || seen.has(id)) continue;
    seen.add(id);
    out.push(entry);
  }

  return out;
}

function replaceDriftPoetryArray(raw, entries) {
  const replacement = `const livingVerse = ${JSON.stringify(entries, null, 4)};`;
  return raw.replace(DRIFT_POETRY_PATTERN, replacement);
}

function buildUniqueWordpersonIdentity(existingEntries, date, title, extension) {
  const titleSlug = slugify(title) || "reflection";
  for (let attempt = 0; attempt < 50; attempt += 1) {
    const suffix = attempt === 0 ? "" : `-${attempt + 1}`;
    const id = `${date}-${titleSlug}${suffix}`;
    const objectKey = `wordperson/${id}.${extension}`;
    const exists = existingEntries.some((entry) => {
      const imagePath = String(entry.image || "");
      return entry.id === id || imagePath.endsWith(`/${objectKey}`) || imagePath.endsWith(objectKey);
    });
    if (!exists) {
      return { id, objectKey };
    }
  }

  throw new Error("Could not find an available word.person post identity");
}

async function findAvailableNarrativePath(env, date, title) {
  const baseSlug = slugify(title) || "untitled-draft";

  for (let attempt = 0; attempt < 50; attempt += 1) {
    const suffix = attempt === 0 ? "" : `-${attempt + 1}`;
    const path = `${CURRENT_NARRATIVE_DIR}/${date}-${baseSlug}${suffix}.md`;
    const response = await githubRequest(
      env,
      `/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/${path}?ref=${env.GITHUB_BRANCH}`
    );

    if (response.status === 404) {
      return path;
    }

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Could not verify narrative path ${path}: ${response.status} ${text}`);
    }
  }

  throw new Error("Could not find an available narrative filename");
}

function buildNarrativeMarkdown(entry) {
  return `# ${entry.title}\nDate: ${entry.date}\n\n${entry.body.trim()}\n`;
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/") {
      return jsonResponse({
        ok: true,
        service: "otw-fragments-publish",
        routes: {
          publish_fragment: "POST /publish-fragment",
          fragments_user_profile: "GET /fragments-user-profile",
          publish_bot_fragment: "POST /publish-bot-fragment",
          publish_changelog_entry: "POST /publish-changelog-entry",
          publish_ghost_draft: "POST /publish-ghost-draft",
          upload_ghost_image: "POST /upload-ghost-image",
          publish_iotd_entry: "POST /publish-iotd-entry",
          publish_wordperson_entry: "POST /publish-wordperson-entry",
          publish_drift_poem: "POST /publish-drift-poem"
        }
      });
    }

    if (request.method === "GET" && url.pathname === "/fragments-user-profile") {
      try {
        const { user } = await getAuthorizedFragmentsUser(request, env);
        if (!user) {
          return jsonResponse({ ok: false, error: "Unauthorized" }, 401);
        }

        return jsonResponse({
          ok: true,
          user: publicFragmentsUser(user)
        });
      } catch (error) {
        return jsonResponse({ ok: false, error: error.message || "Could not load fragments user profile" }, 400);
      }
    }

    if (request.method === "POST" && url.pathname === "/publish-fragment") {
      try {
        const { user } = await getAuthorizedFragmentsUser(request, env);
        if (!user) {
          return jsonResponse({ ok: false, error: "Unauthorized" }, 401);
        }

        const body = await request.json();
        const entry = buildRegisteredFragmentEntry(body, user);
        const { result } = await saveFragmentEntryWithRetry(env, entry, "Publish fragment");

        return jsonResponse({
          ok: true,
          published: entry,
          user: publicFragmentsUser(user),
          commit: result.commit?.sha || null
        });
      } catch (error) {
        return jsonResponse({ ok: false, error: error.message || "Unknown publish error" }, 400);
      }
    }

    if (request.method === "POST" && url.pathname === "/publish-bot-fragment") {
      if (!isAuthorized(request, env)) {
        return jsonResponse({ ok: false, error: "Unauthorized" }, 401);
      }

      try {
        const users = await loadFragmentsUserRegistry(env);
        const botUser = getFragmentsUserById(users, "otw_bot");
        const file = await loadFragmentsFile(env);
        const existingBotTexts = new Set(
          file.fragments
            .filter((entry) => entry.author === "OTW_BOT" || entry.author === "OTW_Bot" || entry.tag === "OTW_BOT")
            .map((entry) => String(entry.text || "").trim())
        );

        const available = BOT_POOL.filter((text) => !existingBotTexts.has(text));
        const pool = available.length ? available : BOT_POOL;
        const text = pool[Math.floor(Math.random() * pool.length)];

        const entry = buildRegisteredFragmentEntry({
          timestamp: new Date().toISOString(),
          text,
          tag: "OTW_BOT"
        }, botUser || {
          id: "otw_bot",
          name: "OTW_Bot",
          handle: "@otw_bot"
        });

        const { result } = await saveFragmentEntryWithRetry(env, entry, "Publish OTW_Bot fragment");

        return jsonResponse({
          ok: true,
          commit: result.commit?.sha || null
        });
      } catch (error) {
        return jsonResponse({ ok: false, error: error.message || "Unknown bot publish error" }, 400);
      }
    }

    if (request.method === "POST" && url.pathname === "/publish-changelog-entry") {
      if (!isAuthorized(request, env)) {
        return jsonResponse({ ok: false, error: "Unauthorized" }, 401);
      }

      try {
        const body = await request.json();
        const entry = normalizeChangelogEntry(body);
        const file = await loadChangelogFile(env);
        const merged = sortChangelog(dedupeChangelog([entry, ...file.entries]));
        const updatedRaw = `${JSON.stringify(merged, null, 2)}\n`;
        const result = await saveRepoFile(env, CHANGELOG_PATH, updatedRaw, file.sha, "Publish changelog entry");

        return jsonResponse({
          ok: true,
          published: entry,
          commit: result.commit?.sha || null
        });
      } catch (error) {
        return jsonResponse({ ok: false, error: error.message || "Unknown changelog publish error" }, 400);
      }
    }

    if (request.method === "POST" && url.pathname === "/publish-ghost-draft") {
      if (!isAuthorized(request, env)) {
        return jsonResponse({ ok: false, error: "Unauthorized" }, 401);
      }

      try {
        const body = await request.json();
        const entry = normalizeNarrativeEntry(body);
        const path = await findAvailableNarrativePath(env, entry.date, entry.title);
        const markdown = buildNarrativeMarkdown(entry);
        const result = await saveRepoFile(env, path, markdown, null, "Publish ghost draft");

        return jsonResponse({
          ok: true,
          published: entry,
          file: path,
          commit: result.commit?.sha || null
        });
      } catch (error) {
        return jsonResponse({ ok: false, error: error.message || "Unknown ghost publish error" }, 400);
      }
    }

    if (request.method === "POST" && url.pathname === "/upload-ghost-image") {
      if (!isAuthorized(request, env)) {
        return jsonResponse({ ok: false, error: "Unauthorized" }, 401);
      }

      try {
        if (!env.IOTD_BUCKET) {
          throw new Error("Image bucket binding is not configured");
        }

        const formData = await request.formData();
        const file = formData.get("image");
        if (!(file instanceof File)) {
          throw new Error("Narrative image file is required");
        }

        const date = normalizeNarrativeDate(formData.get("date"));
        const title = String(formData.get("title") || "").trim() || "Untitled draft";
        const alt = normalizeNarrativeImageAlt(formData.get("alt"));
        const caption = normalizeNarrativeImageCaption(formData.get("caption"));
        const extension = detectImageExtension(file);
        const objectKey = buildNarrativeImageObjectKey(date, title, extension);
        const imageUrl = buildNarrativeImageUrl(env, objectKey);

        await env.IOTD_BUCKET.put(objectKey, await file.arrayBuffer(), {
          httpMetadata: {
            contentType: file.type || "application/octet-stream"
          }
        });

        return jsonResponse({
          ok: true,
          uploaded: {
            object_key: objectKey,
            url: imageUrl,
            alt,
            caption,
            ...buildNarrativeImageSnippets({
              url: imageUrl,
              alt,
              caption
            })
          }
        });
      } catch (error) {
        return jsonResponse({ ok: false, error: error.message || "Unknown ghost image upload error" }, 400);
      }
    }

    if (request.method === "POST" && url.pathname === "/publish-iotd-entry") {
      if (!isAuthorized(request, env)) {
        return jsonResponse({ ok: false, error: "Unauthorized" }, 401);
      }

      try {
        if (!env.IOTD_BUCKET) {
          throw new Error("IOTD bucket binding is not configured");
        }

        const formData = await request.formData();
        const file = formData.get("image");
        if (!(file instanceof File)) {
          throw new Error("IOTD image file is required");
        }

        const date = normalizeIotdDate(formData.get("date"));
        const title = normalizeIotdTitleForFilename(formData.get("title"));
        const caption = normalizeIotdCaption(formData.get("caption"));
        const extension = detectImageExtension(file);
        const objectKey = buildIotdObjectKey(date, extension);
        const imageUrl = buildIotdImageUrl(env, objectKey);

        await env.IOTD_BUCKET.put(objectKey, await file.arrayBuffer(), {
          httpMetadata: {
            contentType: file.type || "application/octet-stream"
          }
        });

        const entry = normalizeIotdEntry({
          date,
          title,
          caption,
          image: imageUrl
        });

        const fileData = await loadImageManifestFile(env);
        const merged = sortIotd(dedupeIotd([entry, ...fileData.entries]));
        const updatedRaw = `${JSON.stringify(merged, null, 2)}\n`;
        const result = await saveRepoFile(env, IMAGE_MANIFEST_PATH, updatedRaw, fileData.sha, "Publish IOTD entry");

        return jsonResponse({
          ok: true,
          published: entry,
          object_key: objectKey,
          commit: result.commit?.sha || null
        });
      } catch (error) {
        return jsonResponse({ ok: false, error: error.message || "Unknown IOTD publish error" }, 400);
      }
    }

    if (request.method === "POST" && url.pathname === "/publish-wordperson-entry") {
      if (!(isAuthorized(request, env) || isWordpersonAuthorized(request, env))) {
        return jsonResponse({ ok: false, error: "Unauthorized" }, 401);
      }

      try {
        if (!env.IOTD_BUCKET) {
          throw new Error("Image bucket binding is not configured");
        }

        const formData = await request.formData();
        const file = formData.get("image");
        if (!(file instanceof File)) {
          throw new Error("word.person image file is required");
        }

        const date = normalizeWordpersonDate(formData.get("date"));
        const body = normalizeWordpersonBody(formData.get("body"));
        const title = normalizeWordpersonTitle(formData.get("title"), body);
        const alt = normalizeWordpersonAlt(formData.get("alt"), title);
        const extension = detectImageExtension(file);

        const manifestFile = await loadWordpersonManifestFile(env);
        const identity = buildUniqueWordpersonIdentity(manifestFile.entries, date, title, extension);
        const imageUrl = buildWordpersonImageUrl(env, identity.objectKey);

        await env.IOTD_BUCKET.put(identity.objectKey, await file.arrayBuffer(), {
          httpMetadata: {
            contentType: file.type || "application/octet-stream"
          }
        });

        const entry = normalizeWordpersonEntry({
          id: identity.id,
          date,
          title,
          image: imageUrl,
          alt,
          excerpt: formData.get("excerpt"),
          body
        });

        const merged = sortWordperson(dedupeWordperson([entry, ...manifestFile.entries]));
        const updatedRaw = `${JSON.stringify(merged, null, 2)}\n`;
        const result = await saveRepoFile(
          env,
          WORDPERSON_MANIFEST_PATH,
          updatedRaw,
          manifestFile.sha,
          "Publish word.person entry"
        );

        return jsonResponse({
          ok: true,
          published: entry,
          object_key: identity.objectKey,
          commit: result.commit?.sha || null
        });
      } catch (error) {
        return jsonResponse({ ok: false, error: error.message || "Unknown word.person publish error" }, 400);
      }
    }

    if (request.method === "POST" && url.pathname === "/publish-drift-poem") {
      if (!isAuthorized(request, env)) {
        return jsonResponse({ ok: false, error: "Unauthorized" }, 401);
      }

      try {
        const body = await request.json();
        const normalized = normalizeDriftPoemEntry(body);
        const file = await loadDriftPoetryFile(env);
        const entry = {
          id: buildUniqueDriftId(file.entries, normalizeDriftDate(body.date), normalized.title),
          ...normalized
        };
        const merged = sortDriftPoetry(dedupeDriftPoetry([entry, ...file.entries]));
        const updatedRaw = replaceDriftPoetryArray(file.raw, merged);
        const result = await saveRepoFile(env, DRIFT_POETRY_PATH, updatedRaw, file.sha, "Publish Drift poem");

        return jsonResponse({
          ok: true,
          published: entry,
          commit: result.commit?.sha || null
        });
      } catch (error) {
        return jsonResponse({ ok: false, error: error.message || "Unknown Drift publish error" }, 400);
      }
    }

    return jsonResponse({ ok: false, error: "Not found" }, 404);
  }
};
