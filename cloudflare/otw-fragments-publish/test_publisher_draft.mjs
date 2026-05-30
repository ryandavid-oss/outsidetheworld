import assert from "node:assert/strict";
import worker from "./src/index.js";

class MockR2Object {
  constructor(value) {
    this.value = value;
  }

  async json() {
    return JSON.parse(this.value);
  }
}

class MockR2Bucket {
  constructor() {
    this.objects = new Map();
    this.options = new Map();
  }

  async put(key, value, options = {}) {
    this.objects.set(key, String(value));
    this.options.set(key, options);
  }

  async get(key) {
    if (!this.objects.has(key)) {
      return null;
    }
    return new MockR2Object(this.objects.get(key));
  }
}

const draftObjectKey = "publisher_drafts/current.json.enc";
const publishKey = "test-publisher-key";
const draftEncryptionKey = "test-publisher-draft-encryption-key";

function env(bucket = new MockR2Bucket()) {
  return {
    PUBLISH_KEY: publishKey,
    PUBLISHER_DRAFT_KEY: draftEncryptionKey,
    IOTD_BUCKET: bucket,
    GITHUB_OWNER: "owner",
    GITHUB_REPO: "repo",
    GITHUB_BRANCH: "main"
  };
}

async function json(request, testEnv) {
  const response = await worker.fetch(request, testEnv);
  return {
    status: response.status,
    body: await response.json()
  };
}

function request(path, options = {}) {
  return new Request(`https://worker.test${path}`, options);
}

const article = {
  schema: "otw.publisher.article",
  version: 3,
  createdAt: "2026-05-29T12:00:00.000Z",
  updatedAt: "2026-05-29T13:00:00.000Z",
  title: "Server Draft Test",
  subhead: "A quiet saved draft",
  metadata: {
    docName: "Server Draft Test",
    publishDate: "2026-05-29",
    slug: "server-draft-test"
  },
  body: {
    blocks: [
      {
        id: "paragraph_1",
        type: "paragraph",
        html: "Paragraph before image.",
        text: "Paragraph before image."
      },
      {
        id: "image_1",
        type: "image",
        source: {
          kind: "url",
          url: "https://pub.example.test/narrative/image.jpg",
          objectKey: "narrative/image.jpg"
        },
        alt: "Image alt text",
        caption: "Image caption",
        displaySize: "small",
        alignment: "right",
        wrapMode: "wrap-left",
        status: "uploaded",
        upload: {
          status: "uploaded",
          uploadedUrl: "https://pub.example.test/narrative/image.jpg",
          objectKey: "narrative/image.jpg"
        }
      },
      {
        id: "image_local",
        type: "image",
        source: {
          kind: "local-data-url",
          mime: "image/png",
          dataUrl: "data:image/png;base64,abc123"
        },
        alt: "Local alt text",
        caption: "Local caption",
        displaySize: "medium",
        alignment: "center",
        wrapMode: "none",
        status: "needs-key",
        upload: {
          status: "needs-key",
          uploadedUrl: "",
          objectKey: ""
        }
      },
      {
        id: "paragraph_2",
        type: "paragraph",
        html: "Paragraph after image.",
        text: "Paragraph after image."
      }
    ]
  }
};

const publishPayload = {
  schema: "otw.publisher.publishPayload",
  version: 1,
  body: {
    format: "markdown",
    markdown: "Paragraph before image.\n\n![Image alt text](https://pub.example.test/narrative/image.jpg \"Image caption\")\n\nParagraph after image.",
    blocks: []
  },
  images: [],
  validation: {
    readiness: "Ready to publish"
  }
};

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function draftRequestBody(overrides = {}) {
  return {
    draftId: "server-draft-test",
    clientUpdatedAt: article.updatedAt,
    readiness: "Ready to publish",
    article: clone(article),
    publishPayload: clone(publishPayload),
    ...overrides
  };
}

function authorizedHeaders(key = publishKey) {
  return {
    "content-type": "application/json",
    "x-publish-key": key
  };
}

{
  const testEnv = env();
  const result = await json(request("/publisher-draft"), testEnv);
  assert.equal(result.status, 401);
  assert.equal(result.body.ok, false);
  assert.equal(result.body.error, "Unauthorized");
  assert.equal("draft" in result.body, false);
}

{
  const testEnv = env();
  const result = await json(request("/publisher-draft", {
    headers: { "x-publish-key": "wrong" }
  }), testEnv);
  assert.equal(result.status, 401);
  assert.equal(result.body.ok, false);
  assert.equal(result.body.error, "Unauthorized");
  assert.equal("draft" in result.body, false);
}

{
  const bucket = new MockR2Bucket();
  const testEnv = env(bucket);
  bucket.objects.set(draftObjectKey, JSON.stringify({ draft: "exists" }));

  for (const options of [
    { method: "GET" },
    { method: "GET", headers: { "x-publish-key": "wrong" } },
    { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(draftRequestBody()) },
    { method: "POST", headers: authorizedHeaders("wrong"), body: JSON.stringify(draftRequestBody()) }
  ]) {
    const result = await json(request("/publisher-draft", options), testEnv);
    assert.equal(result.status, 401);
    assert.deepEqual(result.body, { ok: false, error: "Unauthorized" });
  }
}

{
  const testEnv = env();
  testEnv.PUBLISH_KEY = "";
  const save = await json(request("/publisher-draft", {
    method: "POST",
    headers: authorizedHeaders("anything"),
    body: JSON.stringify(draftRequestBody())
  }), testEnv);
  assert.equal(save.status, 401);
  assert.deepEqual(save.body, { ok: false, error: "Unauthorized" });

  const load = await json(request("/publisher-draft", {
    headers: { "x-publish-key": "anything" }
  }), testEnv);
  assert.equal(load.status, 401);
  assert.deepEqual(load.body, { ok: false, error: "Unauthorized" });
}

{
  const testEnv = env();
  delete testEnv.PUBLISHER_DRAFT_KEY;

  const save = await json(request("/publisher-draft", {
    method: "POST",
    headers: authorizedHeaders(),
    body: JSON.stringify(draftRequestBody())
  }), testEnv);
  assert.equal(save.status, 400);
  assert.equal(save.body.ok, false);
  assert.match(save.body.error, /encryption key is not configured/i);

  const load = await json(request("/publisher-draft", {
    headers: {
      "x-publish-key": publishKey
    }
  }), testEnv);
  assert.equal(load.status, 400);
  assert.equal(load.body.ok, false);
  assert.match(load.body.error, /encryption key is not configured/i);
}

{
  const bucket = new MockR2Bucket();
  const testEnv = env(bucket);
  const result = await json(request("/publisher-draft", {
    method: "POST",
    headers: authorizedHeaders(),
    body: JSON.stringify({
      ...draftRequestBody(),
      publisherAccessKey: publishKey
    })
  }), testEnv);

  assert.equal(result.status, 200);
  assert.equal(result.body.ok, true);
  assert.equal(result.body.draft.article.title, "Server Draft Test");
  assert.equal(result.body.draft.article.body.blocks[1].displaySize, "small");
  assert.equal(result.body.draft.article.body.blocks[1].alignment, "right");
  assert.equal(result.body.draft.article.body.blocks[1].wrapMode, "wrap-left");
  assert.equal(result.body.draft.article.body.blocks[1].upload.uploadedUrl, "https://pub.example.test/narrative/image.jpg");
  assert.equal(result.body.draft.article.body.blocks[2].source.kind, "local-placeholder");
  assert.equal("dataUrl" in result.body.draft.article.body.blocks[2].source, false);
  assert.equal("publisherAccessKey" in result.body.draft, false);

  const stored = bucket.objects.get(draftObjectKey);
  assert.ok(stored);
  const envelope = JSON.parse(stored);
  assert.equal(envelope.schema, "otw.publisher.encryptedDraft");
  assert.equal(envelope.version, 1);
  assert.equal(envelope.algorithm, "AES-GCM");
  assert.ok(envelope.iv);
  assert.ok(envelope.ciphertext);
  assert.equal(stored.includes("Server Draft Test"), false);
  assert.equal(stored.includes(publishKey), false);
  assert.equal(stored.includes(draftEncryptionKey), false);
  assert.equal(bucket.options.get(draftObjectKey).customMetadata.draftId, undefined);
  assert.equal(bucket.options.get(draftObjectKey).customMetadata.schema, "otw.publisher.serverDraft");

  const loaded = await json(request("/publisher-draft", {
    headers: {
      "x-publish-key": publishKey
    }
  }), testEnv);
  assert.equal(loaded.status, 200);
  assert.equal(loaded.body.ok, true);
  assert.equal(loaded.body.draft.article.body.blocks[0].text, "Paragraph before image.");
  assert.equal(loaded.body.draft.article.body.blocks[1].caption, "Image caption");
  assert.equal(loaded.body.draft.article.body.blocks[1].alt, "Image alt text");
  assert.equal(loaded.body.draft.article.body.blocks[1].source.objectKey, "narrative/image.jpg");
  assert.equal(loaded.body.draft.article.body.blocks[1].displaySize, "small");
  assert.equal(loaded.body.draft.article.body.blocks[1].alignment, "right");
  assert.equal(loaded.body.draft.article.body.blocks[1].wrapMode, "wrap-left");
}

{
  const bucket = new MockR2Bucket();
  const testEnv = env(bucket);
  const first = await json(request("/publisher-draft", {
    method: "POST",
    headers: authorizedHeaders(),
    body: JSON.stringify(draftRequestBody())
  }), testEnv);
  assert.equal(first.status, 200);
  const firstStored = JSON.parse(bucket.objects.get(draftObjectKey));

  const second = await json(request("/publisher-draft", {
    method: "POST",
    headers: authorizedHeaders(),
    body: JSON.stringify(draftRequestBody())
  }), testEnv);
  assert.equal(second.status, 200);
  const secondStored = JSON.parse(bucket.objects.get(draftObjectKey));
  assert.notEqual(firstStored.iv, secondStored.iv);
  assert.notEqual(firstStored.ciphertext, secondStored.ciphertext);
}

{
  const bucket = new MockR2Bucket();
  const testEnv = env(bucket);
  const blobArticle = clone(article);
  blobArticle.body.blocks.push({
    id: "image_blob",
    type: "image",
    source: {
      kind: "url",
      url: "blob:https://publisher.test/local-preview",
      objectKey: ""
    },
    alt: "Blob alt",
    caption: "Blob caption",
    displaySize: "medium",
    alignment: "center",
    wrapMode: "none",
    status: "local",
    upload: {
      status: "local",
      uploadedUrl: "blob:https://publisher.test/uploaded-preview",
      objectKey: ""
    }
  });
  const blobPayload = clone(publishPayload);
  blobPayload.body.markdown += "\n\n![Blob alt](blob:https://publisher.test/local-preview \"Blob caption\")";

  const result = await json(request("/publisher-draft", {
    method: "POST",
    headers: authorizedHeaders(),
    body: JSON.stringify(draftRequestBody({
      article: blobArticle,
      publishPayload: blobPayload
    }))
  }), testEnv);
  assert.equal(result.status, 200);

  const returned = JSON.stringify(result.body.draft);
  const stored = bucket.objects.get(draftObjectKey);
  assert.equal(returned.includes("blob:"), false);
  assert.equal(stored.includes("blob:"), false);
  const imageBlock = result.body.draft.article.body.blocks.find((block) => block.id === "image_blob");
  assert.equal(imageBlock.source.kind, "local-placeholder");
  assert.equal("url" in imageBlock.source, false);
}

{
  const bucket = new MockR2Bucket();
  const testEnv = env(bucket);
  const result = await json(request("/publisher-draft", {
    method: "POST",
    headers: authorizedHeaders(),
    body: JSON.stringify(draftRequestBody({
      article: {
        ...clone(article),
        title: `Leaked ${publishKey}`
      }
    }))
  }), testEnv);
  assert.equal(result.status, 400);
  assert.equal(result.body.ok, false);
  assert.equal(bucket.objects.has(draftObjectKey), false);
}

{
  const bucket = new MockR2Bucket();
  const testEnv = env(bucket);
  const saved = await json(request("/publisher-draft", {
    method: "POST",
    headers: authorizedHeaders(),
    body: JSON.stringify(draftRequestBody())
  }), testEnv);
  assert.equal(saved.status, 200);
  const rotatedPublishKeyEnv = { ...testEnv, PUBLISH_KEY: "rotated-publish-key" };
  const loadAfterPublishKeyRotation = await json(request("/publisher-draft", {
    headers: {
      "x-publish-key": "rotated-publish-key"
    }
  }), rotatedPublishKeyEnv);
  assert.equal(loadAfterPublishKeyRotation.status, 200);
  assert.equal(loadAfterPublishKeyRotation.body.ok, true);
  assert.equal(loadAfterPublishKeyRotation.body.draft.article.title, "Server Draft Test");
}

{
  const bucket = new MockR2Bucket();
  const testEnv = env(bucket);
  const saved = await json(request("/publisher-draft", {
    method: "POST",
    headers: authorizedHeaders(),
    body: JSON.stringify(draftRequestBody())
  }), testEnv);
  assert.equal(saved.status, 200);
  const stored = bucket.objects.get(draftObjectKey);
  const wrongDraftKeyEnv = { ...testEnv, PUBLISHER_DRAFT_KEY: "different-draft-encryption-key" };
  const load = await json(request("/publisher-draft", {
    headers: {
      "x-publish-key": publishKey
    }
  }), wrongDraftKeyEnv);
  assert.equal(load.status, 400);
  assert.equal(load.body.ok, false);
  assert.equal(bucket.objects.get(draftObjectKey), stored);
}

{
  const bucket = new MockR2Bucket();
  const testEnv = env(bucket);
  bucket.objects.set(draftObjectKey, JSON.stringify({
    schema: "otw.publisher.encryptedDraft",
    version: 1,
    algorithm: "AES-GCM",
    iv: "not-valid",
    ciphertext: "not-valid"
  }));
  const load = await json(request("/publisher-draft", {
    headers: {
      "x-publish-key": publishKey
    }
  }), testEnv);
  assert.equal(load.status, 400);
  assert.equal(load.body.ok, false);
}

{
  const testEnv = env();
  const result = await json(request("/publisher-draft", {
    method: "POST",
    headers: authorizedHeaders(),
    body: JSON.stringify({
      article: {
        ...article,
        schema: "unexpected"
      }
    })
  }), testEnv);
  assert.equal(result.status, 400);
  assert.equal(result.body.ok, false);
}

{
  const testEnv = env();
  const result = await json(request("/publisher-draft", {
    method: "POST",
    headers: authorizedHeaders(),
    body: JSON.stringify(null)
  }), testEnv);
  assert.equal(result.status, 400);
  assert.equal(result.body.ok, false);
}

console.log("publisher draft route tests passed");
