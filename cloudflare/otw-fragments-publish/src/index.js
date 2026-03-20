const FRAGMENTS_PATH = "fragments_data.js";
const CHANGELOG_PATH = "changelog.json";
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
        sha,
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

function sortFragments(entries) {
  return entries.slice().sort((a, b) => String(b.timestamp || "").localeCompare(String(a.timestamp || "")));
}

function sortChangelog(entries) {
  return entries.slice().sort((a, b) => String(b.date || "").localeCompare(String(a.date || "")));
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
          publish_changelog_entry: "POST /publish-changelog-entry"
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

    return jsonResponse({ ok: false, error: "Not found" }, 404);
  }
};
