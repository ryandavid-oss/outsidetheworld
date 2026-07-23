const MAX_JSON_BYTES = 32 * 1024;
const MAX_ORDER_BYTES = 10 * 1024 * 1024;
const SHIRT_PRICE_CENTS = 2900;
const NON_ARIZONA_SHIPPING_CENTS = 500;
const CONSENT_VERSION = "2026-07-23";
const US_STATE_CODES = new Set([
  "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
  "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
  "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
  "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
  "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
  "DC"
]);

const ROUTES = Object.freeze({
  "/subscribe-frgmnts-waitlist": "waitlist",
  "/submit-professional-inquiry": "professional",
  "/submit-frgmnts-support-request": "support",
  "/submit-frgmnts-seat-checkin": "seat",
  "/submit-shirt-order": "shirt_order"
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

function normalizeVenmoHandle(raw) {
  const value = String(raw || "").trim().toLowerCase().replace(/^@+/, "");
  if (!value) {
    throw new Error("Venmo username is required");
  }
  if (!/^[a-z0-9._-]{3,64}$/.test(value)) {
    throw new Error("Venmo username must use only letters, numbers, dots, underscores, or hyphens");
  }
  return value;
}

function normalizeOrderSize(raw) {
  const value = String(raw || "").trim().toUpperCase();
  const allowed = new Set(["S", "M", "L", "XL", "2XL"]);
  if (!allowed.has(value)) {
    throw new Error("Please choose a valid shirt size");
  }
  return value;
}

function normalizeShippingState(raw) {
  const value = String(raw || "").trim().toUpperCase();
  if (!US_STATE_CODES.has(value)) {
    throw new Error("Please choose a valid U.S. shipping state");
  }
  return value;
}

function normalizeOrderSlug(raw, label, allowed) {
  const value = String(raw || "").trim().toLowerCase();
  if (!/^[a-z0-9-]{1,64}$/.test(value) || (allowed && !allowed.has(value))) {
    throw new Error(`${label} is invalid`);
  }
  return value;
}

function normalizeShirtOrder(entry) {
  if (!entry || typeof entry !== "object") {
    throw new Error("Shirt order payload must be an object");
  }
  rejectHoneypot(entry);
  const shippingState = normalizeShippingState(entry.shipping_state);
  const shippingCents = shippingState === "AZ" ? 0 : NON_ARIZONA_SHIPPING_CENTS;
  const totalCents = SHIRT_PRICE_CENTS + shippingCents;
  if (
    entry.price_acknowledged !== true ||
    entry.order_terms_acknowledged !== true ||
    Number(entry.shirt_price_cents) !== SHIRT_PRICE_CENTS ||
    Number(entry.shipping_cents) !== shippingCents ||
    Number(entry.total_cents) !== totalCents
  ) {
    throw new Error("Please confirm the displayed total and custom-order terms");
  }

  const buildCode = String(entry.build_code || "").trim().toUpperCase();
  if (!/^OTW-[A-F0-9]{4}$/.test(buildCode)) {
    throw new Error("Build code is invalid");
  }

  const submittedAt = new Date().toISOString();
  const artOptions = new Set(["none", "brandmark", "full", "frgmnts"]);
  return {
    name: normalizeRequiredText(entry.name, "Name", 120),
    email: normalizeEmail(entry.email),
    venmoHandle: normalizeVenmoHandle(entry.venmo_handle),
    size: normalizeOrderSize(entry.size),
    shippingAddress: normalizeRequiredText(entry.shipping_address, "Shipping address", 500),
    shippingState,
    note: normalizeOptionalText(entry.note, "Order note", 1000, false),
    shirtPriceCents: SHIRT_PRICE_CENTS,
    shippingCents,
    totalCents,
    buildCode,
    bodyStyle: normalizeOrderSlug(
      entry.body_style,
      "Shirt style",
      new Set(["short", "long"])
    ),
    color: normalizeOrderSlug(entry.color, "Shirt color"),
    frontArt: normalizeOrderSlug(entry.front_art, "Front artwork", artOptions),
    backArt: normalizeOrderSlug(entry.back_art, "Back artwork", artOptions),
    slogan: normalizeOptionalText(entry.slogan, "Shirt phrase", 80),
    source: normalizeSource(entry.source, "tshirt_builder"),
    submittedAt,
    retentionUntil: addMonths(submittedAt, 24)
  };
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

async function readShirtOrderRequest(request) {
  const contentType = String(request.headers.get("content-type") || "").toLowerCase();
  if (!contentType.includes("multipart/form-data")) {
    throw new Error("Shirt orders must use multipart form data");
  }

  const contentLength = Number(request.headers.get("content-length") || "0");
  if (Number.isFinite(contentLength) && contentLength > MAX_ORDER_BYTES) {
    throw new Error("Order submission is too large");
  }

  const form = await request.formData();
  const rawOrder = form.get("order");
  const artwork = form.get("artwork");
  if (typeof rawOrder !== "string" || new TextEncoder().encode(rawOrder).byteLength > MAX_JSON_BYTES) {
    throw new Error("Order details are missing or too large");
  }
  if (
    !artwork ||
    typeof artwork === "string" ||
    typeof artwork.arrayBuffer !== "function" ||
    typeof artwork.size !== "number"
  ) {
    throw new Error("Finished shirt artwork is required");
  }

  const artworkType = String(artwork.type || "").toLowerCase();
  if (!new Set(["image/jpeg", "image/png"]).has(artworkType)) {
    throw new Error("Finished artwork must be a JPEG or PNG image");
  }
  if (artwork.size < 1024 || artwork.size > MAX_ORDER_BYTES) {
    throw new Error("Finished artwork must be between 1 KB and 10 MB");
  }

  return {
    entry: normalizeShirtOrder(JSON.parse(rawOrder)),
    artwork,
    artworkType
  };
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

function hexDigest(buffer) {
  return Array.from(new Uint8Array(buffer))
    .map((value) => value.toString(16).padStart(2, "0"))
    .join("");
}

function orderMoney(cents) {
  return `$${(Number(cents) / 100).toFixed(2)} USD`;
}

function formspreeErrorCodes(payload) {
  return Array.isArray(payload?.errors)
    ? payload.errors.map((error) => String(error?.code || "").trim()).filter(Boolean)
    : [];
}

function formspreeDeniedFileUpload(payload) {
  if (formspreeErrorCodes(payload).includes("NO_FILE_UPLOADS")) {
    return true;
  }
  const errorText = [
    payload?.error,
    ...(Array.isArray(payload?.errors)
      ? payload.errors.map((error) => error?.message)
      : [])
  ].map((value) => String(value || "").toLowerCase()).join(" ");
  return errorText.includes("file upload") && (
    errorText.includes("not permitted") ||
    errorText.includes("not supported") ||
    errorText.includes("unavailable")
  );
}

async function sendShirtOrderNotification(
  env,
  entry,
  artwork,
  artworkType,
  orderId,
  artworkDownloadUrl,
  fetchImpl = fetch
) {
  const endpointText = String(env.ORDER_NOTIFICATION_ENDPOINT || "").trim();
  if (!endpointText) {
    return { status: "not_configured", attachmentDelivered: false };
  }

  const endpoint = new URL(endpointText);
  if (
    endpoint.protocol !== "https:" ||
    endpoint.hostname !== "formspree.io" ||
    !/^\/f\/[a-z0-9]+$/i.test(endpoint.pathname)
  ) {
    throw new Error("Order notification endpoint is invalid");
  }

  const form = new FormData();
  form.set("_subject", `NEW OTW SHIRT ORDER // ${orderId}`);
  form.set("order_id", orderId);
  form.set("name", entry.name);
  form.set("_replyto", entry.email);
  form.set("email", entry.email);
  form.set("venmo_username", `@${entry.venmoHandle}`);
  form.set("shirt_size", entry.size);
  form.set("shipping_address", entry.shippingAddress);
  form.set("shipping_state", entry.shippingState);
  form.set("shirt_price", orderMoney(entry.shirtPriceCents));
  form.set("shipping", entry.shippingCents ? orderMoney(entry.shippingCents) : "FREE");
  form.set("order_total", orderMoney(entry.totalCents));
  form.set("build_code", entry.buildCode);
  form.set("shirt_style", entry.bodyStyle);
  form.set("shirt_color", entry.color);
  form.set("front_art", entry.frontArt);
  form.set("back_art", entry.backArt);
  form.set("slogan", entry.slogan || "NONE");
  form.set("customer_note", entry.note || "NONE");
  form.set("payment_status", "NOT COLLECTED // SEND A VENMO GOODS-AND-SERVICES REQUEST");
  form.set("custom_order_terms", "ACKNOWLEDGED");
  form.set("finished_design_download", artworkDownloadUrl);
  form.set("download_link_expires", "30 days after order submission");
  form.set(
    "finished_design",
    artwork,
    `otw-frgmnts-${entry.buildCode.toLowerCase()}.${artworkType === "image/png" ? "png" : "jpg"}`
  );

  async function submitNotification() {
    const response = await fetchImpl(endpoint.href, {
      method: "POST",
      headers: { accept: "application/json" },
      body: form
    });
    const payload = await response.json().catch(() => ({}));
    return { response, payload };
  }

  let { response, payload } = await submitNotification();
  let attachmentDelivered = true;
  if (!response.ok && formspreeDeniedFileUpload(payload)) {
    form.delete("finished_design");
    form.set(
      "finished_design_status",
      `Use the private download link above. Direct attachment delivery is unavailable on this Formspree plan.`
    );
    attachmentDelivered = false;
    ({ response, payload } = await submitNotification());
  }

  if (!response.ok) {
    const code = formspreeErrorCodes(payload)[0] || `HTTP_${response.status}`;
    throw new Error(`Order notification failed (${code})`);
  }

  return { status: "sent", attachmentDelivered };
}

async function recordShirtOrderNotification(env, orderId, status, attachmentDelivered, error = "") {
  await env.INTAKE_DB.prepare(`
    UPDATE shirt_orders
    SET notification_status = ?,
        notification_attachment = ?,
        notification_attempts = notification_attempts + 1,
        notification_error = ?,
        notification_last_attempt_at = ?,
        notification_sent_at = CASE WHEN ? = 'sent' THEN ? ELSE notification_sent_at END
    WHERE order_id = ?
  `).bind(
    status,
    attachmentDelivered ? 1 : 0,
    String(error || "").slice(0, 240),
    new Date().toISOString(),
    status,
    status === "sent" ? new Date().toISOString() : null,
    orderId
  ).run();
}

async function saveShirtOrder(env, entry, artwork, artworkType) {
  if (!env.ORDER_ARTIFACTS || typeof env.ORDER_ARTIFACTS.put !== "function") {
    throw new Error("Private order artwork storage is not configured");
  }

  const uuid = crypto.randomUUID();
  const orderId = `OTW-${uuid.slice(0, 8).toUpperCase()}`;
  const submittedDate = new Date(entry.submittedAt);
  const extension = artworkType === "image/png" ? "png" : "jpg";
  const artworkKey = [
    "shirt-orders",
    submittedDate.getUTCFullYear(),
    String(submittedDate.getUTCMonth() + 1).padStart(2, "0"),
    `${uuid}.${extension}`
  ].join("/");
  const artworkBytes = await artwork.arrayBuffer();
  const artworkSha256 = hexDigest(await crypto.subtle.digest("SHA-256", artworkBytes));
  const accessToken = hexDigest(crypto.getRandomValues(new Uint8Array(32)));
  const accessTokenHash = hexDigest(
    await crypto.subtle.digest("SHA-256", new TextEncoder().encode(accessToken))
  );
  const accessTokenExpiresAt = addMonths(entry.submittedAt, 1);

  await env.ORDER_ARTIFACTS.put(artworkKey, artworkBytes, {
    httpMetadata: {
      contentType: artworkType,
      cacheControl: "private, no-store"
    },
    customMetadata: {
      orderId,
      buildCode: entry.buildCode
    }
  });

  try {
    await env.INTAKE_DB.prepare(`
      INSERT INTO shirt_orders (
        order_id, status, name, email, venmo_handle, size, shipping_address, shipping_state, note,
        shirt_price_cents, shipping_cents, total_cents, currency,
        price_acknowledged, order_terms_acknowledged,
        build_code, body_style, color, front_art, back_art, slogan,
        artwork_key, artwork_content_type, artwork_bytes, artwork_sha256,
        artwork_access_token_hash, artwork_access_expires_at,
        source, consent_version, submitted_at, retention_until
      ) VALUES (
        ?, 'received', ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, 'USD',
        1, 1,
        ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?,
        ?, ?,
        ?, ?, ?, ?
      )
    `).bind(
      orderId,
      entry.name,
      entry.email,
      entry.venmoHandle,
      entry.size,
      entry.shippingAddress,
      entry.shippingState,
      entry.note,
      entry.shirtPriceCents,
      entry.shippingCents,
      entry.totalCents,
      entry.buildCode,
      entry.bodyStyle,
      entry.color,
      entry.frontArt,
      entry.backArt,
      entry.slogan,
      artworkKey,
      artworkType,
      artwork.size,
      artworkSha256,
      accessTokenHash,
      accessTokenExpiresAt,
      entry.source,
      CONSENT_VERSION,
      entry.submittedAt,
      entry.retentionUntil
    ).run();
  } catch (error) {
    await env.ORDER_ARTIFACTS.delete(artworkKey);
    throw error;
  }

  return { orderId, artworkKey, artworkAccessToken: accessToken };
}

async function notifyShirtOrder(env, entry, artwork, artworkType, orderId, artworkAccessToken) {
  if (!String(env.ORDER_NOTIFICATION_ENDPOINT || "").trim()) {
    return { status: "not_configured", attachmentDelivered: false };
  }

  try {
    const artworkDownloadUrl = new URL(
      `/shirt-order-artwork/${artworkAccessToken}`,
      "https://otw-private-intake.ryandavid.workers.dev"
    ).href;
    const result = await sendShirtOrderNotification(
      env,
      entry,
      artwork,
      artworkType,
      orderId,
      artworkDownloadUrl
    );
    await recordShirtOrderNotification(
      env,
      orderId,
      result.status,
      result.attachmentDelivered
    );
    return result;
  } catch (error) {
    await recordShirtOrderNotification(env, orderId, "failed", false, error.message);
    console.error(`Shirt order notification failed for ${orderId}`);
    return { status: "failed", attachmentDelivered: false };
  }
}

async function serveShirtOrderArtwork(request, env, token) {
  if (!/^[a-f0-9]{64}$/.test(token)) {
    return new Response("Not found", { status: 404 });
  }
  const tokenHash = hexDigest(
    await crypto.subtle.digest("SHA-256", new TextEncoder().encode(token))
  );
  const result = await env.INTAKE_DB.prepare(`
    SELECT order_id, artwork_key, artwork_content_type
    FROM shirt_orders
    WHERE artwork_access_token_hash = ?
      AND artwork_access_expires_at > ?
      AND deleted_at IS NULL
    LIMIT 1
  `).bind(tokenHash, new Date().toISOString()).all();
  const row = result.results?.[0];
  if (!row) {
    return new Response("Not found", { status: 404 });
  }

  const artwork = await env.ORDER_ARTIFACTS.get(row.artwork_key);
  if (!artwork) {
    return new Response("Not found", { status: 404 });
  }
  const extension = row.artwork_content_type === "image/png" ? "png" : "jpg";
  return new Response(artwork.body, {
    status: 200,
    headers: {
      "cache-control": "private, no-store",
      "content-disposition": `attachment; filename="otw-frgmnts-${String(row.order_id).toLowerCase()}.${extension}"`,
      "content-type": row.artwork_content_type,
      "referrer-policy": "no-referrer",
      "x-content-type-options": "nosniff"
    }
  });
}

async function purgeExpiredOrderArtifacts(env, timestamp) {
  if (!env.ORDER_ARTIFACTS || typeof env.ORDER_ARTIFACTS.delete !== "function") {
    return;
  }

  const result = await env.INTAKE_DB.prepare(`
    SELECT artwork_key
    FROM shirt_orders
    WHERE retention_until IS NOT NULL
      AND retention_until <= ?
      AND deleted_at IS NULL
  `).bind(timestamp).all();
  const keys = (result.results || [])
    .map((row) => String(row.artwork_key || "").trim())
    .filter(Boolean);
  await Promise.all(keys.map((key) => env.ORDER_ARTIFACTS.delete(key)));
}

async function purgeExpiredRecords(env, timestamp = new Date().toISOString()) {
  await purgeExpiredOrderArtifacts(env, timestamp);
  const tables = [
    "waitlist_entries",
    "professional_inquiries",
    "support_requests",
    "seat_checkins",
    "shirt_orders"
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
  if (route === "shirt_order") {
    const { entry, artwork, artworkType } = await readShirtOrderRequest(request);
    const result = await saveShirtOrder(env, entry, artwork, artworkType);
    const notification = await notifyShirtOrder(
      env,
      entry,
      artwork,
      artworkType,
      result.orderId,
      result.artworkAccessToken
    );
    return {
      order_id: result.orderId,
      shirt_price_cents: entry.shirtPriceCents,
      shipping_cents: entry.shippingCents,
      total_cents: entry.totalCents,
      notification_status: notification.status,
      notification_attachment: notification.attachmentDelivered,
      message: "Your order request and finished artwork have been received."
    };
  }

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
  normalizeShirtOrder,
  normalizeSupportRequest,
  normalizeWaitlistEntry,
  purgeExpiredRecords,
  sendShirtOrderNotification
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

    if (request.method === "GET" && url.pathname.startsWith("/shirt-order-artwork/")) {
      return serveShirtOrderArtwork(
        request,
        env,
        url.pathname.slice("/shirt-order-artwork/".length)
      );
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
