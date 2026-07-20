import assert from "node:assert/strict";
import { handleRequest } from "./src/index.js";

class MockObject {
  constructor(key, body, type = "image/jpeg") {
    this.key = key;
    this.body = new Blob([body]).stream();
    this.size = Buffer.byteLength(body);
    this.etag = `\"${key}-etag\"`;
    this.httpMetadata = { contentType: type };
  }

  writeHttpMetadata(headers) {
    headers.set("content-type", this.httpMetadata.contentType);
  }
}

class MockBucket {
  constructor(entries = {}) {
    this.entries = new Map(Object.entries(entries));
    this.requested = [];
  }

  async get(key) {
    this.requested.push(key);
    const entry = this.entries.get(key);
    return entry ? new MockObject(key, entry.body, entry.type) : null;
  }

  async head(key) {
    const object = await this.get(key);
    if (object) object.body = null;
    return object;
  }
}

const noCache = null;

{
  const bucket = new MockBucket({ "2026-07-17.jpg": { body: "original" } });
  const response = await handleRequest(
    new Request("https://media.example/o/2026-07-17.jpg"),
    { MEDIA_BUCKET: bucket },
    {},
    noCache
  );
  assert.equal(response.status, 200);
  assert.equal(await response.text(), "original");
  assert.equal(response.headers.get("cache-control"), "public, max-age=86400, stale-while-revalidate=604800");
  assert.equal(response.headers.get("access-control-allow-origin"), "*");
}

{
  const key = "iotd/2026-07-20-the-fire-dragon-1f92010c12c6.jpg";
  const bucket = new MockBucket({ [key]: { body: "immutable-original" } });
  const response = await handleRequest(
    new Request(`https://media.example/o/${key}`),
    { MEDIA_BUCKET: bucket },
    {},
    noCache
  );
  assert.equal(response.status, 200);
  assert.equal(await response.text(), "immutable-original");
  assert.equal(response.headers.get("cache-control"), "public, max-age=31536000, immutable");
  assert.equal(response.headers.get("cloudflare-cdn-cache-control"), "public, max-age=31536000, immutable");
}

{
  const fingerprint = "abcdef1234567890";
  const bucket = new MockBucket({
    [`_variants/${fingerprint}/640.webp`]: { body: "webp", type: "image/webp" },
    [`_variants/${fingerprint}/640.jpg`]: { body: "jpeg", type: "image/jpeg" }
  });
  const response = await handleRequest(
    new Request(`https://media.example/v/${fingerprint}/640`, { headers: { accept: "image/avif,image/webp,*/*" } }),
    { MEDIA_BUCKET: bucket },
    {},
    noCache
  );
  assert.equal(response.status, 200);
  assert.equal(await response.text(), "webp");
  assert.deepEqual(bucket.requested, [
    `_variants/${fingerprint}/640.avif`,
    `_variants/${fingerprint}/640.webp`
  ]);
  assert.equal(response.headers.get("cache-control"), "public, max-age=31536000, immutable");
  assert.equal(response.headers.get("vary"), "Accept");
}

{
  const bucket = new MockBucket();
  const response = await handleRequest(
    new Request("https://media.example/o/../secret"),
    { MEDIA_BUCKET: bucket },
    {},
    noCache
  );
  assert.equal(response.status, 404);
}

console.log("otw-media worker tests passed");
