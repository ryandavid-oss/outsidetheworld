const ORIGINAL_BROWSER_CACHE = "public, max-age=86400, stale-while-revalidate=604800";
const ORIGINAL_EDGE_CACHE = "public, max-age=604800, stale-while-revalidate=2592000";
const VARIANT_CACHE = "public, max-age=31536000, immutable";

function jsonResponse(payload, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "access-control-allow-origin": "*",
      "x-content-type-options": "nosniff"
    }
  });
}

function safeObjectKey(pathname) {
  let decoded;
  try {
    decoded = decodeURIComponent(pathname);
  } catch {
    return "";
  }
  const key = decoded.replace(/^\/+/, "");
  if (!key || key.includes("\0") || key.split("/").some((part) => !part || part === "." || part === "..")) {
    return "";
  }
  return key;
}

function accepts(request, mime) {
  return String(request.headers.get("accept") || "").toLowerCase().includes(mime);
}

function variantFormats(request) {
  const formats = [];
  if (accepts(request, "image/avif")) formats.push("avif");
  if (accepts(request, "image/webp")) formats.push("webp");
  formats.push("jpg");
  return [...new Set(formats)];
}

function variantRequest(pathname, request) {
  const match = pathname.match(/^\/v\/([a-f0-9]{12,64})\/(\d{2,4})\/?$/i);
  if (!match) return null;
  const width = Number(match[2]);
  if (!Number.isInteger(width) || width < 64 || width > 2400) return null;
  return {
    fingerprint: match[1].toLowerCase(),
    width,
    formats: variantFormats(request)
  };
}

function responseHeaders(object, cacheControl, { varyAccept = false } = {}) {
  const headers = new Headers();
  object.writeHttpMetadata?.(headers);
  if (object.httpMetadata?.contentType && !headers.has("content-type")) {
    headers.set("content-type", object.httpMetadata.contentType);
  }
  if (object.etag) headers.set("etag", object.etag);
  if (Number.isFinite(object.size)) headers.set("content-length", String(object.size));
  headers.set("cache-control", cacheControl);
  headers.set("cloudflare-cdn-cache-control", cacheControl === VARIANT_CACHE ? VARIANT_CACHE : ORIGINAL_EDGE_CACHE);
  headers.set("access-control-allow-origin", "*");
  headers.set("cross-origin-resource-policy", "cross-origin");
  headers.set("x-content-type-options", "nosniff");
  if (varyAccept) headers.set("vary", "Accept");
  return headers;
}

function isNotModified(request, object) {
  const requestEtag = String(request.headers.get("if-none-match") || "");
  return Boolean(object.etag && requestEtag.split(",").map((value) => value.trim()).includes(object.etag));
}

async function findVariant(bucket, variant, method) {
  for (const format of variant.formats) {
    const key = `_variants/${variant.fingerprint}/${variant.width}.${format}`;
    const object = method === "HEAD" ? await bucket.head(key) : await bucket.get(key);
    if (object) return { object, key, format };
  }
  return null;
}

function variantCacheRequest(request, variant, format) {
  const url = new URL(request.url);
  url.search = "";
  url.searchParams.set("format", format);
  return new Request(url.toString(), { method: "GET" });
}

async function serveVariant(request, env, ctx, cache) {
  const url = new URL(request.url);
  const variant = variantRequest(url.pathname, request);
  if (!variant) return jsonResponse({ ok: false, error: "Invalid media variant" }, 400);

  if (request.method === "GET" && cache) {
    for (const format of variant.formats) {
      const cached = await cache.match(variantCacheRequest(request, variant, format));
      if (cached) return cached;
    }
  }

  const result = await findVariant(env.MEDIA_BUCKET, variant, request.method);
  if (!result) return jsonResponse({ ok: false, error: "Media variant not found" }, 404);

  const headers = responseHeaders(result.object, VARIANT_CACHE, { varyAccept: true });
  if (isNotModified(request, result.object)) return new Response(null, { status: 304, headers });

  const response = new Response(request.method === "HEAD" ? null : result.object.body, { headers });
  if (request.method === "GET" && cache) {
    const cacheKey = variantCacheRequest(request, variant, result.format);
    ctx?.waitUntil?.(cache.put(cacheKey, response.clone()));
  }
  return response;
}

async function serveOriginal(request, env, ctx, cache) {
  const url = new URL(request.url);
  const key = safeObjectKey(url.pathname.replace(/^\/o\//, ""));
  if (!key) return jsonResponse({ ok: false, error: "Invalid media key" }, 400);

  const cacheKey = new Request(url.toString(), { method: "GET" });
  if (request.method === "GET" && cache) {
    const cached = await cache.match(cacheKey);
    if (cached) return cached;
  }

  const object = request.method === "HEAD"
    ? await env.MEDIA_BUCKET.head(key)
    : await env.MEDIA_BUCKET.get(key);
  if (!object) return jsonResponse({ ok: false, error: "Media object not found" }, 404);

  const headers = responseHeaders(object, ORIGINAL_BROWSER_CACHE);
  if (isNotModified(request, object)) return new Response(null, { status: 304, headers });

  const response = new Response(request.method === "HEAD" ? null : object.body, { headers });
  if (request.method === "GET" && cache) {
    ctx?.waitUntil?.(cache.put(cacheKey, response.clone()));
  }
  return response;
}

export async function handleRequest(request, env, ctx = {}, cache = globalThis.caches?.default) {
  if (!env.MEDIA_BUCKET) return jsonResponse({ ok: false, error: "Media bucket is not configured" }, 503);

  const url = new URL(request.url);
  if (request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "access-control-allow-origin": "*",
        "access-control-allow-methods": "GET, HEAD, OPTIONS",
        "access-control-allow-headers": "If-None-Match",
        "access-control-max-age": "86400"
      }
    });
  }
  if (request.method !== "GET" && request.method !== "HEAD") {
    return jsonResponse({ ok: false, error: "Method not allowed" }, 405);
  }
  if (url.pathname === "/" || url.pathname === "/health") {
    return jsonResponse({ ok: true, service: "otw-media", routes: ["/o/<object-key>", "/v/<fingerprint>/<width>"] });
  }
  if (url.pathname.startsWith("/v/")) return serveVariant(request, env, ctx, cache);
  if (url.pathname.startsWith("/o/")) return serveOriginal(request, env, ctx, cache);
  return jsonResponse({ ok: false, error: "Not found" }, 404);
}

export default {
  fetch(request, env, ctx) {
    return handleRequest(request, env, ctx);
  }
};
