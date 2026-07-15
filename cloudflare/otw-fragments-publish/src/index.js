const FRAGMENTS_PATH = "fragments_data.js";
const FRAGMENTS_USER_REGISTRY_PATH = "fragments_users.json";
const CHANGELOG_PATH = "changelog.json";
const IMAGE_MANIFEST_PATH = "image_manifest.json";
const WORDPERSON_MANIFEST_PATH = "wordperson_manifest.json";
const DRIFT_POETRY_PATH = "new_poetry_data.js";
const FRGMNTS_WAITLIST_PATH = "frgmnts_waitlist.json";
const PROFESSIONAL_INQUIRIES_PATH = "professional_inquiries.json";
const FRGMNTS_SUPPORT_REQUESTS_PATH = "frgmnts_support_requests.json";
const FRGMNTS_SEAT_CHECKINS_PATH = "frgmnts_seat_checkins.json";
const CURRENT_NARRATIVE_DIR = "current_narrative";
const PUBLISHER_DRAFT_OBJECT_KEY = "publisher_drafts/current.json.enc";
const PUBLISHER_DRAFT_SCHEMA = "otw.publisher.serverDraft";
const PUBLISHER_DRAFT_MAX_BYTES = 1024 * 1024;
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

function bytesToBase64(bytes) {
  let binary = "";
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary);
}

function base64ToBytes(value) {
  const binary = atob(String(value || ""));
  return Uint8Array.from(binary, (char) => char.charCodeAt(0));
}

async function draftCryptoKey(secret) {
  const keyMaterial = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(String(secret || ""))
  );
  return crypto.subtle.importKey("raw", keyMaterial, "AES-GCM", false, ["encrypt", "decrypt"]);
}

function getPublisherDraftEncryptionSecret(env) {
  const secret = String(env.PUBLISHER_DRAFT_KEY || env.PUBLISHER_DRAFT_ENCRYPTION_KEY || "").trim();
  if (!secret) {
    throw new Error("Publisher draft encryption key is not configured");
  }
  return secret;
}

async function encryptPublisherDraft(secret, draft) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const key = await draftCryptoKey(secret);
  const plaintext = new TextEncoder().encode(JSON.stringify(draft));
  const ciphertext = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, plaintext);
  return {
    schema: "otw.publisher.encryptedDraft",
    version: 1,
    algorithm: "AES-GCM",
    iv: bytesToBase64(iv),
    ciphertext: bytesToBase64(new Uint8Array(ciphertext))
  };
}

async function decryptPublisherDraft(secret, envelope) {
  if (!envelope || envelope.schema !== "otw.publisher.encryptedDraft" || envelope.algorithm !== "AES-GCM") {
    throw new Error("Stored publisher draft is not readable");
  }
  const key = await draftCryptoKey(secret);
  const iv = base64ToBytes(envelope.iv);
  const ciphertext = base64ToBytes(envelope.ciphertext);
  const plaintext = await crypto.subtle.decrypt({ name: "AES-GCM", iv }, key, ciphertext);
  return JSON.parse(new TextDecoder("utf-8").decode(plaintext));
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

  if (entry.image) {
    normalized.image = String(entry.image).trim();
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

function normalizeWaitlistEmail(raw) {
  const email = String(raw || "").trim().toLowerCase();
  if (!email) {
    throw new Error("Email is required");
  }

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new Error("A valid email address is required");
  }

  if (email.length > 320) {
    throw new Error("Email is too long");
  }

  return email;
}

function normalizeWaitlistEntry(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Waitlist payload must be an object");
  }

  const email = normalizeWaitlistEmail(entry.email);
  const trap = String(entry.website || "").trim();
  if (trap) {
    throw new Error("Spam check failed");
  }

  const source = String(entry.source || "frgmnts_launch_page").trim().slice(0, 80) || "frgmnts_launch_page";
  const note = String(entry.note || "").trim().slice(0, 200);

  return {
    email,
    source,
    note,
    timestamp: new Date().toISOString()
  };
}

function normalizeStoredWaitlistEntry(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Stored waitlist entry must be an object");
  }

  const email = normalizeWaitlistEmail(entry.email);
  const source = String(entry.source || "frgmnts_launch_page").trim().slice(0, 80) || "frgmnts_launch_page";
  const note = String(entry.note || "").trim().slice(0, 200);
  const timestamp = normalizeTimestamp(entry.timestamp);

  return {
    email,
    source,
    note,
    timestamp
  };
}

function normalizeProfessionalInquiryField(raw, label, maxLength) {
  const value = String(raw || "").trim();
  if (!value) {
    throw new Error(`${label} is required`);
  }
  if (value.length > maxLength) {
    throw new Error(`${label} is too long`);
  }
  return value;
}

function normalizeProfessionalInquiryType(raw) {
  const value = String(raw || "").trim();
  const normalized = value.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
  const allowed = new Set(["web_systems", "ios_product_work", "design", "collaboration", "other"]);
  if (!allowed.has(normalized)) {
    throw new Error("Inquiry type is invalid");
  }
  return normalized;
}

function normalizeProfessionalInquiryEntry(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Professional inquiry payload must be an object");
  }

  const trap = String(entry.website || "").trim();
  if (trap) {
    throw new Error("Spam check failed");
  }

  return {
    name: normalizeProfessionalInquiryField(entry.name, "Name", 120),
    contact: normalizeProfessionalInquiryField(entry.contact, "Contact information", 200),
    inquiry_type: normalizeProfessionalInquiryType(entry.inquiry_type),
    comment: normalizeProfessionalInquiryField(entry.comment, "Comment", 4000),
    source: String(entry.source || "professional_archive_contact_form").trim().slice(0, 80) || "professional_archive_contact_form",
    timestamp: new Date().toISOString()
  };
}

function normalizeFrgmntsSupportTopic(value) {
  const normalized = String(value || "").trim().toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
  const allowed = new Set(["account_access", "seat_code_or_invite", "safety_issue", "bug_report", "other"]);
  if (!allowed.has(normalized)) {
    throw new Error("Support topic is invalid");
  }
  return normalized;
}

function normalizeFrgmntsSupportEmail(raw) {
  const email = String(raw || "").trim().toLowerCase();
  if (!email) {
    throw new Error("Email is required");
  }
  if (email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new Error("A valid email address is required");
  }
  return email;
}

function normalizeOptionalSupportText(raw, fieldName, maxLength) {
  const value = String(raw || "").trim().replace(/\s+/g, " ");
  if (!value) {
    return "";
  }
  if (value.length > maxLength) {
    throw new Error(`${fieldName} is too long`);
  }
  return value;
}

function normalizeOptionalFrgmntsHandle(raw) {
  const value = String(raw || "").trim().toLowerCase().replace(/^@+/, "");
  if (!value) {
    return "";
  }
  if (!/^[a-z0-9._]{3,24}$/.test(value)) {
    throw new Error("Handle must be 3-24 characters using lowercase letters, numbers, dots, or underscores");
  }
  return value;
}

function normalizeFrgmntsSupportMessage(raw) {
  const value = String(raw || "").trim().replace(/\r\n/g, "\n");
  if (value.length < 8 || value.length > 4000) {
    throw new Error("Message must be between 8 and 4000 characters");
  }
  return value;
}

function normalizeSeatCheckinStatus(raw) {
  const value = String(raw || "").trim();
  const allowed = new Set(["not_yet", "a_little", "yes_but_stopped"]);
  if (!allowed.has(value)) {
    throw new Error("Please choose how far you got");
  }
  return value;
}

function normalizeSeatCheckinStopPoint(raw) {
  const value = String(raw || "").trim();
  const allowed = new Set(["didnt_start", "testflight", "code_prompt", "seat_code", "profile_setup", "still_deciding", "other"]);
  if (!allowed.has(value)) {
    throw new Error("Please choose where things stalled");
  }
  return value;
}

function normalizeSeatCheckinSignal(raw) {
  const value = String(raw || "").trim();
  const allowed = new Set([
    "too_many_apps",
    "trust_and_privacy",
    "install_confusing",
    "not_enough_time",
    "not_sure_its_for_me",
    "not_sure_who_is_there",
    "already_too_much_social",
    "other"
  ]);
  if (!allowed.has(value)) {
    throw new Error("One of the selected signals is invalid");
  }
  return value;
}

function normalizeSeatCheckinSignals(raw) {
  if (!Array.isArray(raw)) {
    throw new Error("Please choose at least one signal");
  }

  const unique = [];
  const seen = new Set();
  for (const item of raw) {
    const normalized = normalizeSeatCheckinSignal(item);
    if (seen.has(normalized)) continue;
    seen.add(normalized);
    unique.push(normalized);
  }

  if (!unique.length) {
    throw new Error("Please choose at least one signal");
  }

  if (unique.length > 6) {
    throw new Error("Please keep the selected signals to six or fewer");
  }

  return unique;
}

function normalizeOptionalSeatCheckinMessage(raw) {
  const value = String(raw || "").trim().replace(/\r\n/g, "\n");
  if (!value) {
    return "";
  }
  if (value.length > 3000) {
    throw new Error("Response note must be 3000 characters or fewer");
  }
  return value;
}

function normalizeFrgmntsSeatCheckinEntry(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Seat check-in payload must be an object");
  }

  const trap = String(entry.website || "").trim();
  if (trap) {
    throw new Error("Spam check failed");
  }

  return {
    name: normalizeOptionalSupportText(entry.name, "Name", 120),
    email: normalizeFrgmntsSupportEmail(entry.email),
    did_try: normalizeSeatCheckinStatus(entry.did_try),
    stopped_at: normalizeSeatCheckinStopPoint(entry.stopped_at),
    signals: normalizeSeatCheckinSignals(entry.signals),
    message: normalizeOptionalSeatCheckinMessage(entry.message),
    wants_reply: entry.wants_reply === true,
    source: String(entry.source || "frgmnts_seat_checkin_page").trim().slice(0, 80) || "frgmnts_seat_checkin_page",
    timestamp: new Date().toISOString()
  };
}

function normalizeStoredFrgmntsSeatCheckinEntry(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Stored seat check-in entry must be an object");
  }

  return {
    name: normalizeOptionalSupportText(entry.name, "Stored seat check-in name", 120),
    email: normalizeFrgmntsSupportEmail(entry.email),
    did_try: normalizeSeatCheckinStatus(entry.did_try),
    stopped_at: normalizeSeatCheckinStopPoint(entry.stopped_at),
    signals: normalizeSeatCheckinSignals(entry.signals),
    message: normalizeOptionalSeatCheckinMessage(entry.message),
    wants_reply: entry.wants_reply === true,
    source: String(entry.source || "frgmnts_seat_checkin_page").trim().slice(0, 80) || "frgmnts_seat_checkin_page",
    timestamp: normalizeTimestamp(entry.timestamp)
  };
}

function normalizeFrgmntsSupportRequestEntry(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Support request payload must be an object");
  }

  const trap = String(entry.website || "").trim();
  if (trap) {
    throw new Error("Spam check failed");
  }

  return {
    name: normalizeOptionalSupportText(entry.name, "Name", 120),
    email: normalizeFrgmntsSupportEmail(entry.email),
    handle: normalizeOptionalFrgmntsHandle(entry.handle),
    topic: normalizeFrgmntsSupportTopic(entry.topic),
    message: normalizeFrgmntsSupportMessage(entry.message),
    urgent: entry.urgent === true,
    source: String(entry.source || "frgmnts_faq_modal").trim().slice(0, 80) || "frgmnts_faq_modal",
    timestamp: new Date().toISOString()
  };
}

function normalizeStoredFrgmntsSupportRequestEntry(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Stored support request entry must be an object");
  }

  return {
    name: normalizeOptionalSupportText(entry.name, "Stored support request name", 120),
    email: normalizeFrgmntsSupportEmail(entry.email),
    handle: normalizeOptionalFrgmntsHandle(entry.handle),
    topic: normalizeFrgmntsSupportTopic(entry.topic),
    message: normalizeFrgmntsSupportMessage(entry.message),
    urgent: entry.urgent === true,
    source: String(entry.source || "frgmnts_faq_modal").trim().slice(0, 80) || "frgmnts_faq_modal",
    timestamp: normalizeTimestamp(entry.timestamp)
  };
}

function normalizeStoredProfessionalInquiryEntry(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Stored professional inquiry entry must be an object");
  }

  return {
    name: normalizeProfessionalInquiryField(entry.name, "Stored inquiry name", 120),
    contact: normalizeProfessionalInquiryField(entry.contact, "Stored inquiry contact", 200),
    inquiry_type: normalizeProfessionalInquiryType(entry.inquiry_type),
    comment: normalizeProfessionalInquiryField(entry.comment, "Stored inquiry comment", 4000),
    source: String(entry.source || "professional_archive_contact_form").trim().slice(0, 80) || "professional_archive_contact_form",
    timestamp: normalizeTimestamp(entry.timestamp)
  };
}

function formatNarrativeDisplayDate(date) {
  return new Intl.DateTimeFormat("en-US", {
    timeZone: "UTC",
    year: "numeric",
    month: "long",
    day: "numeric"
  }).format(date);
}

function normalizeNarrativeDate(raw) {
  const date = String(raw || "").trim();
  if (!date) {
    throw new Error("Narrative date is required");
  }

  if (/^\d{4}-\d{2}-\d{2}$/.test(date)) {
    const value = new Date(`${date}T12:00:00Z`);
    if (Number.isNaN(value.getTime())) {
      throw new Error("Narrative date could not be parsed");
    }
    return {
      display: formatNarrativeDisplayDate(value),
      fileDate: date
    };
  }

  const value = new Date(`${date} 12:00:00 UTC`);
  if (Number.isNaN(value.getTime())) {
    throw new Error("Narrative date must be in 'March 27, 2026' format");
  }

  return {
    display: formatNarrativeDisplayDate(value),
    fileDate: value.toISOString().slice(0, 10)
  };
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

function normalizeNarrativeSlug(value) {
  return slugify(value).slice(0, 96);
}

function narrativeMarkdownDocumentFromEntry(entry) {
  if (!entry || typeof entry !== "object") {
    return "";
  }
  if (typeof entry.markdown === "string") {
    return entry.markdown;
  }
  if (typeof entry.fullMarkdown === "string") {
    return entry.fullMarkdown;
  }
  if (entry.content && typeof entry.content.markdown === "string") {
    return entry.content.markdown;
  }
  return "";
}

function parseNarrativeMarkdownDocument(markdown) {
  const normalized = String(markdown || "").replace(/\r\n/g, "\n").trim();
  if (!normalized) {
    return null;
  }
  const lines = normalized.split("\n");
  const titleMatch = String(lines[0] || "").match(/^#\s+(.+?)\s*$/);
  const dateMatch = String(lines[1] || "").match(/^Date:\s*(.+?)\s*$/i);
  if (!titleMatch || !dateMatch) {
    throw new Error("Narrative markdown document must start with title and date lines");
  }
  return {
    title: stripMarkdownForTitle(titleMatch[1]),
    date: dateMatch[1].trim(),
    body: lines.slice(2).join("\n").trim()
  };
}

function assertPublishSafeNarrativeMarkdown(markdown, publishKey = "") {
  const value = String(markdown || "");
  if (publishKey && value.includes(publishKey)) {
    throw new Error("Narrative markdown must not contain the publisher key");
  }
  if (/data:image\/[a-z0-9.+-]+(?:;[a-z0-9=:+/.-]+)*,/i.test(value)) {
    throw new Error("Narrative markdown must not contain inline image data");
  }
  if (/\bblob:/i.test(value) || /\botw-local-image:/i.test(value)) {
    throw new Error("Narrative markdown must not contain local image references");
  }
  if (/\bjavascript:/i.test(value)) {
    throw new Error("Narrative markdown must not contain unsafe URLs");
  }
  if (/<\s*(script|iframe|object|embed)\b/i.test(value)) {
    throw new Error("Narrative markdown must not contain unsafe HTML");
  }
  if (/\son[a-z0-9_-]+\s*=/i.test(value)) {
    throw new Error("Narrative markdown must not contain event handler attributes");
  }
}

function assertPublisherMetadataComment(markdown) {
  const match = String(markdown || "").match(/<!--\s*otw-publisher\s*([\s\S]*?)-->/i);
  if (!match) {
    throw new Error("Publisher markdown must include publisher metadata");
  }

  let metadata;
  try {
    metadata = JSON.parse(match[1].trim());
  } catch {
    throw new Error("Publisher metadata must be valid JSON");
  }

  if (!metadata || metadata.schema !== "otw.publisher.post" || ![1, 2].includes(Number(metadata.version || 0))) {
    throw new Error("Publisher metadata schema is invalid");
  }
}

function deriveNarrativeTitle(body) {
  const lines = String(body || "")
    .split(/\r?\n/)
    .map((line) => stripMarkdownForTitle(line))
    .filter(Boolean);

  return lines[0] || "Untitled draft";
}

function normalizeNarrativeEntry(entry, options = {}) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Narrative payload must be an object");
  }

  const markdownDocument = narrativeMarkdownDocumentFromEntry(entry);
  const parsedMarkdown = markdownDocument ? parseNarrativeMarkdownDocument(markdownDocument) : null;
  const rawBody = parsedMarkdown ? parsedMarkdown.body : entry.body;
  const body = String(rawBody || "").trim();
  if (!body) {
    throw new Error("Narrative body is required");
  }

  assertPublishSafeNarrativeMarkdown(body, options.publishKey);
  if (String(entry.source || "").trim() === "publisher.html") {
    assertPublisherMetadataComment(body);
  }

  const date = normalizeNarrativeDate(entry.date || parsedMarkdown?.date);
  const rawTitle = String(entry.title || "").trim();
  const title = rawTitle || parsedMarkdown?.title || deriveNarrativeTitle(body);
  const slug = normalizeNarrativeSlug(entry.slug);

  if (!title) {
    throw new Error("Narrative title could not be derived");
  }
  if (options.publishKey && `${title}\n${date.display}`.includes(options.publishKey)) {
    throw new Error("Narrative markdown must not contain the publisher key");
  }

  return { title, date: date.display, fileDate: date.fileDate, slug, body };
}

function normalizeDriftDate(raw) {
  const date = String(raw || "").trim();
  if (date.length !== 10 || date[4] !== "-" || date[7] !== "-") {
    throw new Error("Drift date must be in YYYY-MM-DD format");
  }
  return date;
}

function normalizeHomepageFocal(raw) {
  const focal = String(raw || "").trim().toLowerCase();
  const allowed = new Set([
    "top-left", "top", "top-right",
    "left", "center", "right",
    "bottom-left", "bottom", "bottom-right"
  ]);
  return allowed.has(focal) ? focal : "center";
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
  const image = String(entry.image || entry.imageUrl || "").trim();
  const homepageFocal = normalizeHomepageFocal(entry.homepageFocal);

  const normalized = {
    title,
    date: formatDriftDate(date),
    era,
    source,
    thumbprint,
    body
  };
  if (image) {
    normalized.image = image;
  }
  if (entry.homepageFocal != null && String(entry.homepageFocal).trim()) {
    normalized.homepageFocal = homepageFocal;
  }
  return normalized;
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
    if (ext === "jpeg") return "jpg";
    if (["jpg", "png", "gif", "webp"].includes(ext)) return ext;
  }

  const mime = String(file?.type || "").toLowerCase();
  if (mime === "image/jpeg") return "jpg";
  if (mime === "image/png") return "png";
  if (mime === "image/gif") return "gif";
  if (mime === "image/webp") return "webp";

  return "jpg";
}

function buildFragmentImageObjectKey(userId, timestamp, extension) {
  const safeUserId = String(userId || "family").trim().replace(/[^a-z0-9_-]+/gi, "_").toLowerCase() || "family";
  const safeStamp = String(timestamp || new Date().toISOString()).replace(/[^0-9a-z]+/gi, "-").replace(/^-+|-+$/g, "").toLowerCase();
  return `fragments/${safeUserId}/${safeStamp}.${extension}`;
}

function buildFragmentImageUrl(env, objectKey) {
  const base = String(env.IOTD_PUBLIC_BASE_URL || "").replace(/\/+$/g, "");
  if (!base) {
    throw new Error("Fragment image base URL is not configured");
  }
  return `${base}/${objectKey}`;
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

function buildDriftImageObjectKey(date, title, extension) {
  const titleSlug = slugify(title) || "untitled-drift";
  const stamp = Date.now().toString(36);
  return `poetry/${date}-${titleSlug}-${stamp}.${extension}`;
}

function buildDriftImageUrl(env, objectKey) {
  const base = String(env.IOTD_PUBLIC_BASE_URL || "").replace(/\/+$/g, "");
  if (!base) {
    throw new Error("Drift image base URL is not configured");
  }
  return `${base}/${objectKey}`;
}

function normalizeNarrativeImageAlt(raw) {
  return String(raw || "").trim() || "Narrative image";
}

function normalizeNarrativeImageCaption(raw) {
  return String(raw || "").trim();
}

function validateNarrativeImageFile(file) {
  const maxBytes = 25 * 1024 * 1024;
  if ((file.size || 0) > maxBytes) {
    throw new Error("Narrative image must be smaller than 25 MB");
  }

  const type = String(file.type || "").toLowerCase();
  const supportedTypes = new Set(["image/jpeg", "image/png", "image/webp", "image/gif"]);
  if (type && !supportedTypes.has(type)) {
    throw new Error("Narrative image must be JPEG, PNG, WebP, or GIF");
  }
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

function escapeMarkdownImageAlt(value) {
  return String(value || "")
    .replace(/[\r\n]+/g, " ")
    .replace(/\\/g, "\\\\")
    .replace(/\[/g, "\\[")
    .replace(/\]/g, "\\]")
    .trim();
}

function escapeMarkdownImageTitle(value) {
  return String(value || "")
    .replace(/[\r\n]+/g, " ")
    .replace(/\\/g, "\\\\")
    .replace(/"/g, '\\"')
    .trim();
}

function buildNarrativeImageSnippets({ url, alt, caption }) {
  const safeUrl = escapeHtmlAttr(url);
  const safeAlt = escapeHtmlAttr(alt);
  const safeCaption = escapeHtmlAttr(caption);
  const markdownAlt = escapeMarkdownImageAlt(alt);
  const markdownCaption = escapeMarkdownImageTitle(caption);
  const markdown = markdownCaption
    ? `![${markdownAlt}](${url} "${markdownCaption}")`
    : `![${markdownAlt}](${url})`;
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
  const homepageFocal = normalizeHomepageFocal(entry.homepageFocal);

  if (!image) {
    throw new Error("IOTD image URL is required");
  }

  const normalized = { date, title, caption, image };
  if (entry.homepageFocal != null && String(entry.homepageFocal).trim()) {
    normalized.homepageFocal = homepageFocal;
  }
  return normalized;
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

async function loadOptionalRepoFile(env, path) {
  const response = await githubRequest(
    env,
    `/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/${path}?ref=${env.GITHUB_BRANCH}`
  );

  if (response.status === 404) {
    return null;
  }

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

async function buildRegisteredFragmentEntryFromRequest(request, env, user) {
  const contentType = String(request.headers.get("content-type") || "").toLowerCase();

  if (contentType.includes("multipart/form-data")) {
    if (!env.IOTD_BUCKET) {
      throw new Error("Image bucket binding is not configured");
    }

    const formData = await request.formData();
    const file = formData.get("image");
    const payload = {
      timestamp: formData.get("timestamp"),
      text: formData.get("text"),
      tag: formData.get("tag")
    };

    const entry = buildRegisteredFragmentEntry(payload, user);

    if (file instanceof File && file.size > 0) {
      const extension = detectImageExtension(file);
      const objectKey = buildFragmentImageObjectKey(user.id, entry.timestamp, extension);
      await env.IOTD_BUCKET.put(objectKey, await file.arrayBuffer(), {
        httpMetadata: {
          contentType: file.type || "application/octet-stream"
        }
      });
      entry.image = buildFragmentImageUrl(env, objectKey);
    }

    return entry;
  }

  const body = await request.json();
  return buildRegisteredFragmentEntry(body, user);
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

async function loadFrgmntsWaitlistFile(env) {
  const file = await loadOptionalRepoFile(env, FRGMNTS_WAITLIST_PATH);
  if (!file) {
    return { sha: null, entries: [] };
  }

  let entries;
  try {
    entries = JSON.parse(file.raw);
  } catch (error) {
    throw new Error(`Could not parse ${FRGMNTS_WAITLIST_PATH}: ${error.message}`);
  }

  if (!Array.isArray(entries)) {
    throw new Error(`${FRGMNTS_WAITLIST_PATH} is not an array`);
  }

  return { ...file, entries: entries.map(normalizeStoredWaitlistEntry) };
}

async function loadProfessionalInquiriesFile(env) {
  const file = await loadOptionalRepoFile(env, PROFESSIONAL_INQUIRIES_PATH);
  if (!file) {
    return { sha: null, entries: [] };
  }

  let entries;
  try {
    entries = JSON.parse(file.raw);
  } catch (error) {
    throw new Error(`Could not parse ${PROFESSIONAL_INQUIRIES_PATH}: ${error.message}`);
  }

  if (!Array.isArray(entries)) {
    throw new Error(`${PROFESSIONAL_INQUIRIES_PATH} is not an array`);
  }

  return { ...file, entries: entries.map(normalizeStoredProfessionalInquiryEntry) };
}

async function loadFrgmntsSupportRequestsFile(env) {
  const file = await loadOptionalRepoFile(env, FRGMNTS_SUPPORT_REQUESTS_PATH);
  if (!file) {
    return { sha: null, entries: [] };
  }

  let entries;
  try {
    entries = JSON.parse(file.raw);
  } catch (error) {
    throw new Error(`Could not parse ${FRGMNTS_SUPPORT_REQUESTS_PATH}: ${error.message}`);
  }

  if (!Array.isArray(entries)) {
    throw new Error(`${FRGMNTS_SUPPORT_REQUESTS_PATH} is not an array`);
  }

  return { ...file, entries: entries.map(normalizeStoredFrgmntsSupportRequestEntry) };
}

async function loadFrgmntsSeatCheckinsFile(env) {
  const file = await loadOptionalRepoFile(env, FRGMNTS_SEAT_CHECKINS_PATH);
  if (!file) {
    return { sha: null, entries: [] };
  }

  let entries;
  try {
    entries = JSON.parse(file.raw);
  } catch (error) {
    throw new Error(`Could not parse ${FRGMNTS_SEAT_CHECKINS_PATH}: ${error.message}`);
  }

  if (!Array.isArray(entries)) {
    throw new Error(`${FRGMNTS_SEAT_CHECKINS_PATH} is not an array`);
  }

  return { ...file, entries: entries.map(normalizeStoredFrgmntsSeatCheckinEntry) };
}

function sortFragments(entries) {
  return entries.slice().sort((a, b) => String(b.timestamp || "").localeCompare(String(a.timestamp || "")));
}

function sortChangelog(entries) {
  return entries.slice().sort((a, b) => String(b.date || "").localeCompare(String(a.date || "")));
}

function dedupeWaitlist(entries) {
  const seen = new Set();
  const out = [];

  for (const entry of entries) {
    const normalized = normalizeStoredWaitlistEntry(entry);
    if (seen.has(normalized.email)) continue;
    seen.add(normalized.email);
    out.push(normalized);
  }

  return out;
}

function sortWaitlist(entries) {
  return entries.slice().sort((a, b) => String(b.timestamp || "").localeCompare(String(a.timestamp || "")));
}

function dedupeProfessionalInquiries(entries) {
  const seen = new Set();
  const out = [];

  for (const entry of entries) {
    const normalized = normalizeStoredProfessionalInquiryEntry(entry);
    const key = [
      normalized.name.toLowerCase(),
      normalized.contact.toLowerCase(),
      normalized.inquiry_type,
      normalized.comment.toLowerCase()
    ].join("||");
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(normalized);
  }

  return out;
}

function sortProfessionalInquiries(entries) {
  return entries.slice().sort((a, b) => String(b.timestamp || "").localeCompare(String(a.timestamp || "")));
}

function sortFrgmntsSupportRequests(entries) {
  return entries.slice().sort((a, b) => String(b.timestamp || "").localeCompare(String(a.timestamp || "")));
}

function sortFrgmntsSeatCheckins(entries) {
  return entries.slice().sort((a, b) => String(b.timestamp || "").localeCompare(String(a.timestamp || "")));
}

async function saveWaitlistEntryWithRetry(env, entry, maxAttempts = 3) {
  let lastError = null;

  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      const file = await loadFrgmntsWaitlistFile(env);
      const existing = file.entries.some((item) => normalizeWaitlistEmail(item.email) === entry.email);
      if (existing) {
        return { duplicate: true, entry, count: file.entries.length };
      }

      const merged = sortWaitlist(dedupeWaitlist([entry, ...file.entries]));
      const updatedRaw = `${JSON.stringify(merged, null, 2)}\n`;
      const result = await saveRepoFile(
        env,
        FRGMNTS_WAITLIST_PATH,
        updatedRaw,
        file.sha,
        "Add frgmnts waitlist entry"
      );
      return { duplicate: false, entry, result, count: merged.length };
    } catch (error) {
      lastError = error;
      if (!isGithubConflictError(error) || attempt === maxAttempts) {
        throw error;
      }
    }
  }

  throw lastError || new Error("Waitlist save retry failed");
}

async function saveProfessionalInquiryWithRetry(env, entry, maxAttempts = 3) {
  let lastError = null;

  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      const file = await loadProfessionalInquiriesFile(env);
      const merged = sortProfessionalInquiries(dedupeProfessionalInquiries([entry, ...file.entries]));
      const updatedRaw = `${JSON.stringify(merged, null, 2)}\n`;
      const result = await saveRepoFile(
        env,
        PROFESSIONAL_INQUIRIES_PATH,
        updatedRaw,
        file.sha,
        "Add professional inquiry"
      );
      return { entry, result, count: merged.length };
    } catch (error) {
      lastError = error;
      if (!isGithubConflictError(error) || attempt === maxAttempts) {
        throw error;
      }
    }
  }

  throw lastError || new Error("Professional inquiry save retry failed");
}

async function saveFrgmntsSupportRequestWithRetry(env, entry, maxAttempts = 3) {
  let lastError = null;

  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      const file = await loadFrgmntsSupportRequestsFile(env);
      const merged = sortFrgmntsSupportRequests([entry, ...file.entries]);
      const updatedRaw = `${JSON.stringify(merged, null, 2)}\n`;
      const result = await saveRepoFile(
        env,
        FRGMNTS_SUPPORT_REQUESTS_PATH,
        updatedRaw,
        file.sha,
        "Add frgmnts support request"
      );
      return { entry, result, count: merged.length };
    } catch (error) {
      lastError = error;
      if (!isGithubConflictError(error) || attempt === maxAttempts) {
        throw error;
      }
    }
  }

  throw lastError || new Error("frgmnts support request save retry failed");
}

async function saveFrgmntsSeatCheckinWithRetry(env, entry, maxAttempts = 3) {
  let lastError = null;

  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      const file = await loadFrgmntsSeatCheckinsFile(env);
      const merged = sortFrgmntsSeatCheckins([entry, ...file.entries]);
      const updatedRaw = `${JSON.stringify(merged, null, 2)}\n`;
      const result = await saveRepoFile(
        env,
        FRGMNTS_SEAT_CHECKINS_PATH,
        updatedRaw,
        file.sha,
        "Add frgmnts seat check-in"
      );
      return { entry, result, count: merged.length };
    } catch (error) {
      lastError = error;
      if (!isGithubConflictError(error) || attempt === maxAttempts) {
        throw error;
      }
    }
  }

  throw lastError || new Error("frgmnts seat check-in save retry failed");
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

async function findAvailableNarrativePath(env, date, title, slugOverride = "") {
  const baseSlug = normalizeNarrativeSlug(slugOverride) || slugify(title) || "untitled-draft";

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

function isPlainObject(value) {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function sanitizePublisherDraftValue(value, publishKey, depth = 0) {
  if (depth > 24) {
    throw new Error("Draft payload is too deeply nested");
  }

  if (Array.isArray(value)) {
    if (value.length > 1000) {
      throw new Error("Draft payload contains too many array items");
    }
    return value.map((item) => sanitizePublisherDraftValue(item, publishKey, depth + 1));
  }

  if (isPlainObject(value)) {
    const output = {};
    Object.entries(value).forEach(([key, child]) => {
      const normalizedKey = key.toLowerCase().replace(/[^a-z0-9]/g, "");
      if (
        normalizedKey === "publishkey" ||
        normalizedKey === "publisherkey" ||
        normalizedKey === "publisheraccesskey" ||
        normalizedKey === "accesskey"
      ) {
        return;
      }
      if (key === "dataUrl") {
        output.dataUrlLength = String(child || "").length;
        return;
      }
      output[key] = sanitizePublisherDraftValue(child, publishKey, depth + 1);
    });
    return output;
  }

  if (typeof value === "string") {
    if (publishKey && value.includes(publishKey)) {
      throw new Error("Draft payload must not contain the publisher key");
    }
    return value
      .replace(/data:image\/[a-z0-9.+-]+(?:;[a-z0-9=:+/.-]+)*,[^\s)"']+/gi, "")
      .replace(/blob:[^\s)"']+/gi, "");
  }

  if (typeof value === "number" || typeof value === "boolean" || value == null || typeof value === "string") {
    return value;
  }

  return null;
}

function normalizePublisherDraftImageBlock(block) {
  const normalized = { ...block };
  const source = isPlainObject(normalized.source) ? { ...normalized.source } : {};
  if (source.kind === "local-data-url" || source.dataUrl) {
    source.kind = "local-placeholder";
    source.dataUrlLength = Number(source.dataUrlLength || String(source.dataUrl || "").length || 0);
    delete source.dataUrl;
  }
  if (source.url && String(source.url).startsWith("blob:")) {
    source.kind = "local-placeholder";
    source.urlLength = String(source.url).length;
    delete source.url;
  }
  if (source.kind === "url" && !source.url) {
    source.kind = "local-placeholder";
    delete source.url;
  }
  normalized.source = source;
  return normalized;
}

function normalizePublisherDraftArticle(article) {
  if (!isPlainObject(article) || article.schema !== "otw.publisher.article") {
    throw new Error("Publisher draft article is invalid");
  }

  const body = isPlainObject(article.body) ? article.body : {};
  const blocks = Array.isArray(body.blocks) ? body.blocks : [];
  const normalizedBlocks = blocks.map((block) => {
    if (!isPlainObject(block)) {
      throw new Error("Publisher draft contains an invalid block");
    }
    return block.type === "image" ? normalizePublisherDraftImageBlock(block) : block;
  });

  return {
    ...article,
    title: String(article.title || ""),
    subhead: String(article.subhead || ""),
    createdAt: normalizeTimestamp(article.createdAt || new Date().toISOString()),
    updatedAt: normalizeTimestamp(article.updatedAt || new Date().toISOString()),
    body: {
      ...body,
      blocks: normalizedBlocks
    }
  };
}

function normalizePublisherDraftPayload(payload, publishKey) {
  if (!isPlainObject(payload)) {
    throw new Error("Publisher draft payload must be an object");
  }

  const sanitized = sanitizePublisherDraftValue(payload, publishKey);
  const article = normalizePublisherDraftArticle(sanitized.article);
  const draftId = normalizeNarrativeSlug(sanitized.draftId || sanitized.id || article.metadata?.slug || article.title) || "current";
  const savedAt = new Date().toISOString();
  const clientUpdatedAt = normalizeTimestamp(sanitized.clientUpdatedAt || article.updatedAt || savedAt);
  const readiness = String(sanitized.readiness || sanitized.publishPayload?.validation?.readiness || "").trim().slice(0, 120);
  const publishPayload = isPlainObject(sanitized.publishPayload)
    ? sanitized.publishPayload
    : null;

  const draft = {
    schema: PUBLISHER_DRAFT_SCHEMA,
    version: 1,
    draftId,
    savedAt,
    clientUpdatedAt,
    article,
    readiness,
    publishPayload
  };

  const encoded = new TextEncoder().encode(JSON.stringify(draft));
  if (encoded.byteLength > PUBLISHER_DRAFT_MAX_BYTES) {
    throw new Error("Publisher draft is too large to save");
  }

  return draft;
}

function publicPublisherDraft(draft) {
  if (!draft) {
    return null;
  }
  return {
    schema: draft.schema,
    version: draft.version,
    draftId: draft.draftId,
    savedAt: draft.savedAt,
    clientUpdatedAt: draft.clientUpdatedAt,
    article: draft.article,
    readiness: draft.readiness || "",
    publishPayload: draft.publishPayload || null
  };
}

async function loadPublisherDraft(env) {
  if (!env.IOTD_BUCKET) {
    throw new Error("Draft bucket binding is not configured");
  }
  const encryptionSecret = getPublisherDraftEncryptionSecret(env);
  const object = await env.IOTD_BUCKET.get(PUBLISHER_DRAFT_OBJECT_KEY);
  if (!object) {
    return null;
  }
  const envelope = await object.json();
  return decryptPublisherDraft(encryptionSecret, envelope);
}

async function savePublisherDraft(env, draft) {
  if (!env.IOTD_BUCKET) {
    throw new Error("Draft bucket binding is not configured");
  }
  const envelope = await encryptPublisherDraft(getPublisherDraftEncryptionSecret(env), draft);
  await env.IOTD_BUCKET.put(PUBLISHER_DRAFT_OBJECT_KEY, JSON.stringify(envelope), {
    httpMetadata: {
      contentType: "application/json; charset=utf-8"
    },
    customMetadata: {
      schema: PUBLISHER_DRAFT_SCHEMA,
      savedAt: draft.savedAt
    }
  });
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
          publisher_draft: "GET,POST /publisher-draft",
          subscribe_frgmnts_waitlist: "POST /subscribe-frgmnts-waitlist",
          submit_frgmnts_support_request: "POST /submit-frgmnts-support-request",
          submit_frgmnts_seat_checkin: "POST /submit-frgmnts-seat-checkin",
          submit_professional_inquiry: "POST /submit-professional-inquiry",
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

        const entry = await buildRegisteredFragmentEntryFromRequest(request, env, user);
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
        const entry = normalizeNarrativeEntry(body, { publishKey: getPublishHeader(request) });
        const path = await findAvailableNarrativePath(env, entry.fileDate, entry.title, entry.slug);
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

    if (request.method === "GET" && url.pathname === "/publisher-draft") {
      if (!isAuthorized(request, env)) {
        return jsonResponse({ ok: false, error: "Unauthorized" }, 401);
      }

      try {
        const draft = await loadPublisherDraft(env);
        return jsonResponse({
          ok: true,
          draft: publicPublisherDraft(draft)
        });
      } catch (error) {
        return jsonResponse({ ok: false, error: error.message || "Could not load publisher draft" }, 400);
      }
    }

    if (request.method === "POST" && url.pathname === "/publisher-draft") {
      if (!isAuthorized(request, env)) {
        return jsonResponse({ ok: false, error: "Unauthorized" }, 401);
      }

      try {
        const body = await request.json();
        const draft = normalizePublisherDraftPayload(body, getPublishHeader(request));
        await savePublisherDraft(env, draft);

        return jsonResponse({
          ok: true,
          draft: publicPublisherDraft(draft)
        });
      } catch (error) {
        return jsonResponse({ ok: false, error: error.message || "Could not save publisher draft" }, 400);
      }
    }

    if (request.method === "POST" && url.pathname === "/subscribe-frgmnts-waitlist") {
      try {
        const body = await request.json();
        const entry = normalizeWaitlistEntry(body);
        const result = await saveWaitlistEntryWithRetry(env, entry);

        return jsonResponse({
          ok: true,
          duplicate: result.duplicate === true,
          subscribed: entry.email,
          message: result.duplicate
            ? "This email is already on the frgmnts waitlist."
            : "You are on the frgmnts waitlist.",
          commit: result.result?.commit?.sha || null
        });
      } catch (error) {
        return jsonResponse({ ok: false, error: error.message || "Unknown waitlist subscribe error" }, 400);
      }
    }

    if (request.method === "POST" && url.pathname === "/submit-frgmnts-support-request") {
      try {
        const body = await request.json();
        const entry = normalizeFrgmntsSupportRequestEntry(body);
        const result = await saveFrgmntsSupportRequestWithRetry(env, entry);

        return jsonResponse({
          ok: true,
          message: entry.urgent
            ? "Your urgent safety request has been received."
            : "Your support request has been received.",
          count: result.count,
          commit: result.result?.commit?.sha || null
        });
      } catch (error) {
        return jsonResponse({ ok: false, error: error.message || "Unknown frgmnts support request error" }, 400);
      }
    }

    if (request.method === "POST" && url.pathname === "/submit-frgmnts-seat-checkin") {
      try {
        const body = await request.json();
        const entry = normalizeFrgmntsSeatCheckinEntry(body);
        const result = await saveFrgmntsSeatCheckinWithRetry(env, entry);

        return jsonResponse({
          ok: true,
          message: entry.wants_reply
            ? "Thanks. Your note came through, and we can follow up."
            : "Thanks. Your note came through.",
          count: result.count,
          commit: result.result?.commit?.sha || null
        });
      } catch (error) {
        return jsonResponse({ ok: false, error: error.message || "Unknown frgmnts seat check-in error" }, 400);
      }
    }

    if (request.method === "POST" && url.pathname === "/submit-professional-inquiry") {
      try {
        const body = await request.json();
        const entry = normalizeProfessionalInquiryEntry(body);
        const result = await saveProfessionalInquiryWithRetry(env, entry);

        return jsonResponse({
          ok: true,
          submitted: {
            name: entry.name,
            inquiry_type: entry.inquiry_type,
            timestamp: entry.timestamp
          },
          message: "Your inquiry has been received.",
          commit: result.result?.commit?.sha || null
        });
      } catch (error) {
        return jsonResponse({ ok: false, error: error.message || "Unknown professional inquiry error" }, 400);
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
        validateNarrativeImageFile(file);

        const date = normalizeNarrativeDate(formData.get("date"));
        const title = String(formData.get("title") || "").trim() || "Untitled draft";
        const alt = normalizeNarrativeImageAlt(formData.get("alt"));
        const caption = normalizeNarrativeImageCaption(formData.get("caption"));
        const extension = detectImageExtension(file);
        const objectKey = buildNarrativeImageObjectKey(date.fileDate, title, extension);
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
        const homepageFocal = normalizeHomepageFocal(formData.get("homepageFocal"));
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
          image: imageUrl,
          homepageFocal
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
        const contentType = String(request.headers.get("content-type") || "").toLowerCase();
        let body;
        let imageFile = null;

        if (contentType.includes("multipart/form-data")) {
          if (!env.IOTD_BUCKET) {
            throw new Error("Drift image bucket binding is not configured");
          }
          const formData = await request.formData();
          imageFile = formData.get("image");
          if (!(imageFile instanceof File) || imageFile.size <= 0) {
            throw new Error("Drift homepage image file is required");
          }
          body = {
            date: formData.get("date"),
            title: formData.get("title"),
            body: formData.get("body"),
            homepageFocal: formData.get("homepageFocal")
          };
        } else {
          body = await request.json();
        }

        const publishDate = normalizeDriftDate(body.date);
        const normalized = normalizeDriftPoemEntry(body);

        let objectKey = null;
        if (imageFile) {
          validateNarrativeImageFile(imageFile);
          const extension = detectImageExtension(imageFile);
          objectKey = buildDriftImageObjectKey(publishDate, normalized.title, extension);
          await env.IOTD_BUCKET.put(objectKey, await imageFile.arrayBuffer(), {
            httpMetadata: {
              contentType: imageFile.type || "application/octet-stream"
            }
          });
          normalized.image = buildDriftImageUrl(env, objectKey);
        }

        const file = await loadDriftPoetryFile(env);
        const entry = {
          id: buildUniqueDriftId(file.entries, publishDate, normalized.title),
          ...normalized
        };
        const merged = sortDriftPoetry(dedupeDriftPoetry([entry, ...file.entries]));
        const updatedRaw = replaceDriftPoetryArray(file.raw, merged);
        const result = await saveRepoFile(env, DRIFT_POETRY_PATH, updatedRaw, file.sha, "Publish Drift poem");

        return jsonResponse({
          ok: true,
          published: entry,
          object_key: objectKey,
          commit: result.commit?.sha || null
        });
      } catch (error) {
        return jsonResponse({ ok: false, error: error.message || "Unknown Drift publish error" }, 400);
      }
    }

    return jsonResponse({ ok: false, error: "Not found" }, 404);
  }
};
