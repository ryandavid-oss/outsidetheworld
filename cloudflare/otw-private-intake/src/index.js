const MAX_JSON_BYTES = 32 * 1024;
const CONSENT_VERSION = "2026-07-23";

const ROUTES = Object.freeze({
  "/subscribe-frgmnts-waitlist": "waitlist",
  "/submit-professional-inquiry": "professional",
  "/submit-frgmnts-support-request": "support",
  "/submit-frgmnts-seat-checkin": "seat"
});

function configuredOrigins(env) {
  return new Set(
    String(env.ALLOWED_ORIGINS || "")
      .split(",")
      .map((origin) => origin.trim())
      .filter(Boolean)
  );
}

function requestOrigin(request) {
  return String(request.headers.get("origin") || "").trim();
}

function isAllowedOrigin(request, env) {
  const origin = requestOrigin(request);
  return Boolean(origin && configuredOrigins(env).has(origin));
}

function corsHeaders(request, env) {
  const headers = {
    "access-control-allow-methods": "POST,OPTIONS",
    "access-control-allow-headers": "content-type",
    "access-control-max-age": "86400",
    "cache-control": "no-store",
    "content-type": "application/json; charset=utf-8",
    "referrer-policy": "no-referrer",
    "vary": "Origin",
    "x-content-type-options": "nosniff"
  };

  if (isAllowedOrigin(request, env)) {
    headers["access-control-allow-origin"] = requestOrigin(request);
  }

  return headers;
}

function jsonResponse(request, env, data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: corsHeaders(request, env)
  });
}

function addYears(timestamp, years) {
  const value = new Date(timestamp);
  value.setUTCFullYear(value.getUTCFullYear() + years);
  return value.toISOString();
}

function addMonths(timestamp, months) {
  const value = new Date(timestamp);
  value.setUTCMonth(value.getUTCMonth() + months);
  return value.toISOString();
}

function normalizeEmail(raw, maxLength = 254) {
  const email = String(raw || "").trim().toLowerCase();
  if (!email) {
    throw new Error("Email is required");
  }
  if (email.length > maxLength || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new Error("A valid email address is required");
  }
  return email;
}

function normalizeRequiredText(raw, label, maxLength) {
  const value = String(raw || "").trim();
  if (!value) {
    throw new Error(`${label} is required`);
  }
  if (value.length > maxLength) {
    throw new Error(`${label} is too long`);
  }
  return value;
}

function normalizeOptionalText(raw, label, maxLength, collapseWhitespace = true) {
  let value = String(raw || "").trim();
  if (collapseWhitespace) {
    value = value.replace(/\s+/g, " ");
  }
  if (value.length > maxLength) {
    throw new Error(`${label} is too long`);
  }
  return value;
}

function rejectHoneypot(entry) {
  if (String(entry?.website || "").trim()) {
    throw new Error("Spam check failed");
  }
}

function normalizeSource(raw, fallback) {
  return String(raw || fallback).trim().slice(0, 80) || fallback;
}

function normalizeWaitlistEntry(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Waitlist payload must be an object");
  }
  rejectHoneypot(entry);
  const submittedAt = new Date().toISOString();
  return {
    email: normalizeEmail(entry.email, 320),
    source: normalizeSource(entry.source, "frgmnts_launch_page"),
    note: normalizeOptionalText(entry.note, "Note", 200),
    submittedAt,
    retentionUntil: addYears(submittedAt, 2)
  };
}

function normalizeProfessionalInquiryType(raw) {
  const value = String(raw || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
  const allowed = new Set(["web_systems", "ios_product_work", "design", "collaboration", "other"]);
  if (!allowed.has(value)) {
    throw new Error("Inquiry type is invalid");
  }
  return value;
}

function normalizeProfessionalInquiry(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Professional inquiry payload must be an object");
  }
  rejectHoneypot(entry);
  const submittedAt = new Date().toISOString();
  return {
    name: normalizeRequiredText(entry.name, "Name", 120),
    contact: normalizeRequiredText(entry.contact, "Contact information", 200),
    inquiryType: normalizeProfessionalInquiryType(entry.inquiry_type),
    comment: normalizeRequiredText(entry.comment, "Comment", 4000),
    source: normalizeSource(entry.source, "professional_archive_contact_form"),
    submittedAt,
    retentionUntil: addYears(submittedAt, 2)
  };
}

function normalizeSupportTopic(raw) {
  const value = String(raw || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
  const allowed = new Set(["account_access", "seat_code_or_invite", "safety_issue", "bug_report", "other"]);
  if (!allowed.has(value)) {
    throw new Error("Support topic is invalid");
  }
  return value;
}

function normalizeHandle(raw) {
  const value = String(raw || "").trim().toLowerCase().replace(/^@+/, "");
  if (!value) {
    return "";
  }
  if (!/^[a-z0-9._]{3,24}$/.test(value)) {
    throw new Error("Handle must be 3-24 characters using lowercase letters, numbers, dots, or underscores");
  }
  return value;
}

function normalizeSupportRequest(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Support request payload must be an object");
  }
  rejectHoneypot(entry);
  const submittedAt = new Date().toISOString();
  const message = normalizeRequiredText(entry.message, "Message", 4000);
  if (message.length < 8) {
    throw new Error("Message must be between 8 and 4000 characters");
  }
  return {
    name: normalizeOptionalText(entry.name, "Name", 120),
    email: normalizeEmail(entry.email),
    handle: normalizeHandle(entry.handle),
    topic: normalizeSupportTopic(entry.topic),
    message,
    urgent: entry.urgent === true,
    source: normalizeSource(entry.source, "frgmnts_faq_modal"),
    submittedAt,
    retentionUntil: addMonths(submittedAt, 12)
  };
}

function normalizeSeatStatus(raw) {
  const value = String(raw || "").trim();
  const allowed = new Set(["not_yet", "a_little", "yes_but_stopped"]);
  if (!allowed.has(value)) {
    throw new Error("Please choose how far you got");
  }
  return value;
}

function normalizeStopPoint(raw) {
  const value = String(raw || "").trim();
  const allowed = new Set([
    "didnt_start",
    "testflight",
    "code_prompt",
    "seat_code",
    "profile_setup",
    "still_deciding",
    "other"
  ]);
  if (!allowed.has(value)) {
    throw new Error("Please choose where things stalled");
  }
  return value;
}

function normalizeSeatSignals(raw) {
  if (!Array.isArray(raw)) {
    throw new Error("Please choose at least one signal");
  }
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
  const signals = [...new Set(raw.map((value) => String(value || "").trim()))];
  if (!signals.length || signals.length > 6 || signals.some((value) => !allowed.has(value))) {
    throw new Error("One or more selected signals are invalid");
  }
  return signals;
}

function normalizeSeatCheckin(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Seat check-in payload must be an object");
  }
  rejectHoneypot(entry);
  const submittedAt = new Date().toISOString();
  return {
    name: normalizeOptionalText(entry.name, "Name", 120),
    email: normalizeEmail(entry.email),
    didTry: normalizeSeatStatus(entry.did_try),
    stoppedAt: normalizeStopPoint(entry.stopped_at),
    signals: normalizeSeatSignals(entry.signals),
    message: normalizeOptionalText(entry.message, "Response note", 3000, false),
    wantsReply: entry.wants_reply === true,
    source: normalizeSource(entry.source, "frgmnts_seat_checkin_page"),
    submittedAt,
    retentionUntil: addMonths(submittedAt, 12)
  };
}

async function readJsonRequest(request) {
  const contentType = String(request.headers.get("content-type") || "").toLowerCase();
  if (!contentType.includes("application/json")) {
    throw new Error("Content-Type must be application/json");
  }
  const contentLength = Number(request.headers.get("content-length") || "0");
  if (Number.isFinite(contentLength) && contentLength > MAX_JSON_BYTES) {
    throw new Error("Request is too large");
  }
  const text = await request.text();
  if (new TextEncoder().encode(text).byteLength > MAX_JSON_BYTES) {
    throw new Error("Request is too large");
  }
  return JSON.parse(text);
}

async function saveWaitlist(env, entry) {
  const result = await env.INTAKE_DB.prepare(`
    INSERT INTO waitlist_entries (
      email, source, note, consent_version, submitted_at, retention_until
    ) VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(email) DO NOTHING
  `).bind(
    entry.email,
    entry.source,
    entry.note,
    CONSENT_VERSION,
    entry.submittedAt,
    entry.retentionUntil
  ).run();
  return { duplicate: Number(result.meta?.changes || 0) === 0 };
}

async function saveProfessionalInquiry(env, entry) {
  await env.INTAKE_DB.prepare(`
    INSERT INTO professional_inquiries (
      name, contact, inquiry_type, comment, source, consent_version, submitted_at, retention_until
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    entry.name,
    entry.contact,
    entry.inquiryType,
    entry.comment,
    entry.source,
    CONSENT_VERSION,
    entry.submittedAt,
    entry.retentionUntil
  ).run();
}

async function saveSupportRequest(env, entry) {
  await env.INTAKE_DB.prepare(`
    INSERT INTO support_requests (
      name, email, handle, topic, message, urgent, source, consent_version, submitted_at, retention_until
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    entry.name,
    entry.email,
    entry.handle,
    entry.topic,
    entry.message,
    entry.urgent ? 1 : 0,
    entry.source,
    CONSENT_VERSION,
    entry.submittedAt,
    entry.retentionUntil
  ).run();
}

async function saveSeatCheckin(env, entry) {
  await env.INTAKE_DB.prepare(`
    INSERT INTO seat_checkins (
      name, email, did_try, stopped_at, signals_json, message, wants_reply,
      source, consent_version, submitted_at, retention_until
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    entry.name,
    entry.email,
    entry.didTry,
    entry.stoppedAt,
    JSON.stringify(entry.signals),
    entry.message,
    entry.wantsReply ? 1 : 0,
    entry.source,
    CONSENT_VERSION,
    entry.submittedAt,
    entry.retentionUntil
  ).run();
}

async function purgeExpiredRecords(env, timestamp = new Date().toISOString()) {
  const tables = [
    "waitlist_entries",
    "professional_inquiries",
    "support_requests",
    "seat_checkins"
  ];

  for (const table of tables) {
    await env.INTAKE_DB.prepare(`
      DELETE FROM ${table}
      WHERE retention_until IS NOT NULL
        AND retention_until <= ?
    `).bind(timestamp).run();
  }
}

async function handlePost(request, env, route) {
  const body = await readJsonRequest(request);
  if (route === "waitlist") {
    const result = await saveWaitlist(env, normalizeWaitlistEntry(body));
    return {
      duplicate: result.duplicate,
      message: result.duplicate
        ? "This email is already on the frgmnts waitlist."
        : "You are on the frgmnts waitlist."
    };
  }
  if (route === "professional") {
    await saveProfessionalInquiry(env, normalizeProfessionalInquiry(body));
    return { message: "Your inquiry has been received." };
  }
  if (route === "support") {
    const entry = normalizeSupportRequest(body);
    await saveSupportRequest(env, entry);
    return {
      message: entry.urgent
        ? "Your urgent safety request has been received."
        : "Your support request has been received."
    };
  }
  if (route === "seat") {
    const entry = normalizeSeatCheckin(body);
    await saveSeatCheckin(env, entry);
    return {
      message: entry.wantsReply
        ? "Thanks. Your note came through, and we can follow up."
        : "Thanks. Your note came through."
    };
  }
  throw new Error("Unsupported intake route");
}

export {
  normalizeProfessionalInquiry,
  normalizeSeatCheckin,
  normalizeSupportRequest,
  normalizeWaitlistEntry,
  purgeExpiredRecords
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const route = ROUTES[url.pathname];

    if (request.method === "GET" && url.pathname === "/") {
      return jsonResponse(request, env, {
        ok: true,
        service: "otw-private-intake",
        status: "ready"
      });
    }

    if (!route) {
      return jsonResponse(request, env, { ok: false, error: "Not found" }, 404);
    }

    if (!isAllowedOrigin(request, env)) {
      return jsonResponse(request, env, { ok: false, error: "Origin is not allowed" }, 403);
    }

    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: corsHeaders(request, env)
      });
    }

    if (request.method !== "POST") {
      return jsonResponse(request, env, { ok: false, error: "Method not allowed" }, 405);
    }

    try {
      const result = await handlePost(request, env, route);
      return jsonResponse(request, env, { ok: true, ...result });
    } catch (error) {
      return jsonResponse(request, env, {
        ok: false,
        error: error instanceof SyntaxError
          ? "Request body must be valid JSON"
          : error.message || "Submission could not be processed"
      }, 400);
    }
  },

  async scheduled(_event, env, context) {
    context.waitUntil(purgeExpiredRecords(env));
  }
};
