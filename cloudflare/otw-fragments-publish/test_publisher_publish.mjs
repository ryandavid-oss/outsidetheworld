import assert from "node:assert/strict";
import worker from "./src/index.js";

const publishKey = "test-publisher-key";
const baseImageUrl = "https://pub.example.test/narrative/publisher-test.jpg";

function env() {
  return {
    PUBLISH_KEY: publishKey,
    GITHUB_OWNER: "owner",
    GITHUB_REPO: "repo",
    GITHUB_BRANCH: "main",
    GITHUB_TOKEN: "test-token"
  };
}

function request(path, options = {}) {
  return new Request(`https://worker.test${path}`, options);
}

function authorizedHeaders(key = publishKey) {
  return {
    "content-type": "application/json",
    "x-publish-key": key
  };
}

async function json(response) {
  return {
    status: response.status,
    body: await response.json()
  };
}

function decodeBase64Utf8(content) {
  return new TextDecoder().decode(
    Uint8Array.from(atob(content.replace(/\n/g, "")), (char) => char.charCodeAt(0))
  );
}

function encodeBase64Utf8(content) {
  const bytes = new TextEncoder().encode(content);
  let binary = "";
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary);
}

function publisherMetadata(imageUrl = baseImageUrl) {
  return {
    schema: "otw.publisher.post",
    version: 2,
    formatting: {
      mode: "otw-enhanced-markdown",
      version: 1,
      fallback: "markdown"
    },
    generatedAt: "2026-05-29T20:00:00.000Z",
    images: [
      {
        url: imageUrl,
        alt: "Publisher image alt",
        caption: "Publisher image caption",
        objectKey: "narrative/publisher-test.jpg",
        displaySize: "small",
        alignment: "right",
        wrapMode: "wrap-left"
      }
    ],
    blocks: [
      {
        type: "paragraph",
        html: 'Paragraph before the image with a <span style="color: #6395EE; text-decoration: underline">normal link</span>.',
        text: "Paragraph before the image with a normal link."
      },
      { type: "divider" },
      { type: "image", imageIndex: 0 },
      { type: "paragraph" }
    ]
  };
}

function publisherMarkdown(overrides = {}) {
  const title = overrides.title ?? "Publisher Contract Test";
  const date = overrides.date ?? "May 29, 2026";
  const imageUrl = overrides.imageUrl ?? baseImageUrl;
  const metadata = overrides.metadata ?? publisherMetadata(imageUrl);
  const body = overrides.body ?? [
    "<!-- otw-publisher",
    JSON.stringify(metadata),
    "-->",
    "",
    "_A quiet subhead for the new publisher._",
    "",
    "Paragraph before the image with a [normal link](https://outsidetheworld.com/).",
    "",
    "---",
    "",
    `![Publisher image alt](${imageUrl} "Publisher image caption")`,
    "",
    "Paragraph after the image with **bold text**."
  ].join("\n");

  return `# ${title}\nDate: ${date}\n\n${body}\n`;
}

function publishBody(overrides = {}) {
  return {
    title: overrides.title ?? "Publisher Contract Test",
    date: overrides.date ?? "2026-05-29",
    slug: overrides.slug ?? "publisher-contract-test",
    markdown: overrides.markdown ?? publisherMarkdown(overrides),
    source: overrides.source ?? "publisher.html"
  };
}

async function postPublish(testEnv, body, key = publishKey) {
  return json(await worker.fetch(request("/publish-ghost-draft", {
    method: "POST",
    headers: key === null ? { "content-type": "application/json" } : authorizedHeaders(key),
    body: JSON.stringify(body)
  }), testEnv));
}

async function postDrift(testEnv, body, key = publishKey) {
  return json(await worker.fetch(request("/publish-drift-poem", {
    method: "POST",
    headers: key === null ? { "content-type": "application/json" } : authorizedHeaders(key),
    body: JSON.stringify(body)
  }), testEnv));
}

async function withMockGitHub(handler, testFn) {
  const originalFetch = globalThis.fetch;
  const calls = [];
  globalThis.fetch = async (url, options = {}) => {
    const href = String(url);
    if (href.startsWith("https://api.github.com/")) {
      calls.push({ url: href, options });
      return handler(href, options, calls);
    }
    return originalFetch(url, options);
  };

  try {
    await testFn(calls);
  } finally {
    globalThis.fetch = originalFetch;
  }
}

function githubPublishMock(existingPaths = new Set()) {
  return async (url, options) => {
    const method = String(options.method || "GET").toUpperCase();
    const path = decodeURIComponent(url.split("/contents/")[1]?.split("?")[0] || "");

    if (method === "GET") {
      if (existingPaths.has(path)) {
        return new Response(JSON.stringify({ sha: "existing-sha" }), {
          status: 200,
          headers: { "content-type": "application/json" }
        });
      }
      return new Response(JSON.stringify({ message: "Not Found" }), {
        status: 404,
        headers: { "content-type": "application/json" }
      });
    }

    if (method === "PUT") {
      return new Response(JSON.stringify({
        commit: { sha: "published-commit-sha" },
        path
      }), {
        status: 200,
        headers: { "content-type": "application/json" }
      });
    }

    return new Response(JSON.stringify({ error: "Unexpected GitHub request" }), {
      status: 500,
      headers: { "content-type": "application/json" }
    });
  };
}

function githubDriftMock(existingRaw = "const livingVerse = [];\n") {
  return async (url, options) => {
    const method = String(options.method || "GET").toUpperCase();
    const path = decodeURIComponent(url.split("/contents/")[1]?.split("?")[0] || "");

    if (path !== "new_poetry_data.js") {
      return new Response(JSON.stringify({ message: "Not Found" }), {
        status: 404,
        headers: { "content-type": "application/json" }
      });
    }

    if (method === "GET") {
      return new Response(JSON.stringify({
        sha: "existing-poetry-sha",
        content: encodeBase64Utf8(existingRaw)
      }), {
        status: 200,
        headers: { "content-type": "application/json" }
      });
    }

    if (method === "PUT") {
      return new Response(JSON.stringify({
        commit: { sha: "published-drift-sha" },
        path
      }), {
        status: 200,
        headers: { "content-type": "application/json" }
      });
    }

    return new Response(JSON.stringify({ error: "Unexpected GitHub request" }), {
      status: 500,
      headers: { "content-type": "application/json" }
    });
  };
}

function putCalls(calls) {
  return calls.filter((call) => String(call.options.method || "GET").toUpperCase() === "PUT");
}

{
  await withMockGitHub(githubPublishMock(), async (calls) => {
    const result = await postPublish(env(), publishBody(), null);
    assert.equal(result.status, 401);
    assert.deepEqual(result.body, { ok: false, error: "Unauthorized" });
    assert.equal(calls.length, 0);
  });
}

{
  await withMockGitHub(githubPublishMock(), async (calls) => {
    const result = await postPublish(env(), publishBody(), "wrong-key");
    assert.equal(result.status, 401);
    assert.deepEqual(result.body, { ok: false, error: "Unauthorized" });
    assert.equal(calls.length, 0);
  });
}

{
  await withMockGitHub(githubPublishMock(), async (calls) => {
    const result = await postPublish(env(), {
      ...publishBody(),
      markdown: "Date: May 29, 2026\n\nBody without a markdown title."
    });
    assert.equal(result.status, 400);
    assert.equal(result.body.ok, false);
    assert.match(result.body.error, /must start with title and date/i);
    assert.equal(calls.length, 0);
  });
}

{
  await withMockGitHub(githubPublishMock(), async (calls) => {
    const result = await postPublish(env(), {
      ...publishBody(),
      markdown: "# Empty Body\nDate: May 29, 2026\n\n"
    });
    assert.equal(result.status, 400);
    assert.equal(result.body.ok, false);
    assert.match(result.body.error, /body is required/i);
    assert.equal(calls.length, 0);
  });
}

for (const markdown of [
  publisherMarkdown({ body: "Publisher body without metadata." }),
  publisherMarkdown({ body: "<!-- otw-publisher\nnot json\n-->\n\nPublisher body." }),
  publisherMarkdown({
    metadata: {
      schema: "wrong.schema",
      version: 1
    }
  }),
  publisherMarkdown({
    metadata: {
      schema: "otw.publisher.post",
      version: 3
    }
  })
]) {
  await withMockGitHub(githubPublishMock(), async (calls) => {
    const result = await postPublish(env(), {
      ...publishBody(),
      markdown
    });
    assert.equal(result.status, 400);
    assert.equal(result.body.ok, false);
    assert.equal(calls.length, 0);
  });
}

for (const markdown of [
  publisherMarkdown({ imageUrl: "data:image/png;base64,abc123" }),
  publisherMarkdown({ imageUrl: "blob:https://publisher.test/local-preview" }),
  publisherMarkdown({ imageUrl: "otw-local-image:image_123" }),
  publisherMarkdown({ imageUrl: "javascript:alert(1)" }),
  publisherMarkdown({ body: "<script>alert(1)</script>" }),
  publisherMarkdown({ body: "<img src=\"https://pub.example.test/a.jpg\" onerror=\"alert(1)\">" })
]) {
  await withMockGitHub(githubPublishMock(), async (calls) => {
    const result = await postPublish(env(), {
      ...publishBody(),
      markdown
    });
    assert.equal(result.status, 400);
    assert.equal(result.body.ok, false);
    assert.equal(calls.length, 0);
  });
}

{
  await withMockGitHub(githubPublishMock(), async (calls) => {
    const result = await postPublish(env(), {
      ...publishBody(),
      title: `Leaked ${publishKey}`
    });
    assert.equal(result.status, 400);
    assert.equal(result.body.ok, false);
    assert.match(result.body.error, /publisher key/i);
    assert.equal(calls.length, 0);
  });
}

{
  await withMockGitHub(githubPublishMock(), async (calls) => {
    const result = await postPublish(env(), {
      title: "Legacy Markdown Publish",
      date: "2026-05-29",
      slug: "legacy-markdown-publish",
      body: "Legacy body without publisher metadata."
    });
    assert.equal(result.status, 200);
    assert.equal(result.body.ok, true);
    assert.equal(result.body.file, "current_narrative/2026-05-29-legacy-markdown-publish.md");
    const writes = putCalls(calls);
    assert.equal(writes.length, 1);
    const requestBody = JSON.parse(writes[0].options.body);
    const savedMarkdown = decodeBase64Utf8(requestBody.content);
    assert.ok(savedMarkdown.includes("Legacy body without publisher metadata."));
    assert.equal(savedMarkdown.includes("otw-publisher"), false);
  });
}

{
  await withMockGitHub(githubPublishMock(), async (calls) => {
    const result = await postPublish(env(), publishBody());
    assert.equal(result.status, 200);
    assert.equal(result.body.ok, true);
    assert.equal(result.body.file, "current_narrative/2026-05-29-publisher-contract-test.md");
    assert.equal(result.body.commit, "published-commit-sha");

    const writes = putCalls(calls);
    assert.equal(writes.length, 1);
    const requestBody = JSON.parse(writes[0].options.body);
    const savedMarkdown = decodeBase64Utf8(requestBody.content);
    assert.equal(requestBody.branch, "main");
    assert.equal("sha" in requestBody, false);
    assert.ok(savedMarkdown.startsWith("# Publisher Contract Test\nDate: May 29, 2026\n\n"));
    assert.ok(savedMarkdown.includes("<!-- otw-publisher"));
    assert.ok(savedMarkdown.includes("\"displaySize\":\"small\""));
    assert.ok(savedMarkdown.includes("\"alignment\":\"right\""));
    assert.ok(savedMarkdown.includes("\"wrapMode\":\"wrap-left\""));
    assert.ok(savedMarkdown.includes(`![Publisher image alt](${baseImageUrl} "Publisher image caption")`));
    assert.equal(savedMarkdown.includes("data:image"), false);
    assert.equal(savedMarkdown.includes("blob:"), false);
    assert.equal(savedMarkdown.includes(publishKey), false);
    assert.equal(/(Retry|Replace|Remove|Move image|Uploaded)/.test(savedMarkdown), false);
  });
}

{
  const existingPath = "current_narrative/2026-05-29-publisher-contract-test.md";
  await withMockGitHub(githubPublishMock(new Set([existingPath])), async (calls) => {
    const result = await postPublish(env(), publishBody());
    assert.equal(result.status, 200);
    assert.equal(result.body.ok, true);
    assert.equal(result.body.file, "current_narrative/2026-05-29-publisher-contract-test-2.md");
    assert.equal(putCalls(calls).length, 1);
  });
}

{
  await withMockGitHub(githubDriftMock(), async (calls) => {
    const image = "Images/poetry/permission-to-fall.jpg";
    const result = await postDrift(env(), {
      title: "Permission to Fall",
      date: "2026-06-24",
      body: "Line one\nLine two",
      image
    });
    assert.equal(result.status, 200);
    assert.equal(result.body.ok, true);

    const writes = putCalls(calls);
    assert.equal(writes.length, 1);
    const requestBody = JSON.parse(writes[0].options.body);
    const savedPoetry = decodeBase64Utf8(requestBody.content);
    assert.ok(savedPoetry.includes('"title": "Permission to Fall"'));
    assert.ok(savedPoetry.includes(`"image": "${image}"`));
  });
}

console.log("publisher publish route tests passed");
