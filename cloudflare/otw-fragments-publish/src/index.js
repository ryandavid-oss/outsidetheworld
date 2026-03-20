const FRAGMENTS_PATH = "fragments_data.js";
const CHANGELOG_PATH = "changelog.json";
const IMAGE_MANIFEST_PATH = "image_manifest.json";
const CURRENT_NARRATIVE_DIR = "current_narrative";
const FRAGMENTS_PATTERN = /window\.otw_fragments\s*=\s*(\[[\s\S]*?\])\s*;/m;

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

function isAuthorized(request, env) {
  const key = request.headers.get("x-publish-key");
  return Boolean(key && env.PUBLISH_KEY && key === env.PUBLISH_KEY);
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

  if (entry.author) {
    normalized.author = String(entry.author).trim();
  }

  return normalized;
}

function dedupeFragments(entries) {
  const seen = new Set();
  const out = [];

  for (const entry of entries) {
    const normalized = normalizeFragmentEntry(entry);
    const key = [
      normalized.timestamp,
      String(normalized.author || "").trim(),
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

function replaceFragmentsArray(raw, entries) {
  const replacement = `window.otw_fragments = ${JSON.stringify(entries, null, 2)};`;
  return raw.replace(FRAGMENTS_PATTERN, replacement);
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

function sortFragments(entries) {
  return entries.slice().sort((a, b) => String(b.timestamp || "").localeCompare(String(a.timestamp || "")));
}

function sortChangelog(entries) {
  return entries.slice().sort((a, b) => String(b.date || "").localeCompare(String(a.date || "")));
}

function sortIotd(entries) {
  return entries.slice().sort((a, b) => String(b.date || "").localeCompare(String(a.date || "")));
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
          publish_bot_fragment: "POST /publish-bot-fragment",
          publish_changelog_entry: "POST /publish-changelog-entry",
          publish_ghost_draft: "POST /publish-ghost-draft",
          publish_iotd_entry: "POST /publish-iotd-entry"
        }
      });
    }

    if (request.method === "POST" && url.pathname === "/publish-fragment") {
      if (!isAuthorized(request, env)) {
        return jsonResponse({ ok: false, error: "Unauthorized" }, 401);
      }

      try {
        const body = await request.json();
        const entry = normalizeFragmentEntry(body);
        const file = await loadFragmentsFile(env);
        const merged = sortFragments(dedupeFragments([entry, ...file.fragments]));
        const updatedRaw = replaceFragmentsArray(file.raw, merged);
        const result = await saveRepoFile(env, FRAGMENTS_PATH, updatedRaw, file.sha, "Publish fragment");

        return jsonResponse({
          ok: true,
          published: entry,
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
        const file = await loadFragmentsFile(env);
        const existingBotTexts = new Set(
          file.fragments
            .filter((entry) => entry.author === "OTW_BOT" || entry.author === "OTW_Bot" || entry.tag === "OTW_BOT")
            .map((entry) => String(entry.text || "").trim())
        );

        const available = BOT_POOL.filter((text) => !existingBotTexts.has(text));
        const pool = available.length ? available : BOT_POOL;
        const text = pool[Math.floor(Math.random() * pool.length)];

        const entry = normalizeFragmentEntry({
          timestamp: new Date().toISOString(),
          text,
          tag: "OTW_BOT",
          author: "OTW_Bot"
        });

        const merged = sortFragments(dedupeFragments([entry, ...file.fragments]));
        const updatedRaw = replaceFragmentsArray(file.raw, merged);
        const result = await saveRepoFile(env, FRAGMENTS_PATH, updatedRaw, file.sha, "Publish OTW_Bot fragment");

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

    return jsonResponse({ ok: false, error: "Not found" }, 404);
  }
};
