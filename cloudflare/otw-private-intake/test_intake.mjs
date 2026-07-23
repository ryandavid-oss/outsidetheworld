import assert from "node:assert/strict";
import worker, {
  normalizeProfessionalInquiry,
  normalizeSeatCheckin,
  normalizeShirtOrder,
  normalizeSupportRequest,
  normalizeWaitlistEntry,
  purgeExpiredRecords,
  sendShirtOrderNotification
} from "./src/index.js";

assert.equal(normalizeWaitlistEntry({
  email: " Person@Example.com "
}).email, "person@example.com");

assert.equal(normalizeProfessionalInquiry({
  name: "A Person",
  contact: "person@example.com",
  inquiry_type: "Design",
  comment: "A concise inquiry."
}).inquiryType, "design");

const supportEntry = normalizeSupportRequest({
  email: "person@example.com",
  topic: "bug_report",
  message: "A useful bug report."
});
const expectedSupportRetention = new Date(supportEntry.submittedAt);
expectedSupportRetention.setUTCMonth(expectedSupportRetention.getUTCMonth() + 12);
assert.equal(supportEntry.retentionUntil, expectedSupportRetention.toISOString());

assert.deepEqual(normalizeSeatCheckin({
  email: "person@example.com",
  did_try: "a_little",
  stopped_at: "profile_setup",
  signals: ["trust_and_privacy"]
}).signals, ["trust_and_privacy"]);

const orderEntry = normalizeShirtOrder({
  name: "A Buyer",
  email: "buyer@example.com",
  venmo_handle: "@buyer-name",
  size: "xl",
  shipping_address: "123 Example Way\nPhoenix, AZ 85001",
  shipping_state: "az",
  price_acknowledged: true,
  order_terms_acknowledged: true,
  shirt_price_cents: 2900,
  shipping_cents: 0,
  total_cents: 2900,
  build_code: "OTW-1A2B",
  body_style: "short",
  color: "black",
  front_art: "frgmnts",
  back_art: "full"
});
assert.equal(orderEntry.venmoHandle, "buyer-name");
assert.equal(orderEntry.size, "XL");
assert.equal(orderEntry.shippingState, "AZ");
assert.equal(orderEntry.shirtPriceCents, 2900);
assert.equal(orderEntry.shippingCents, 0);
assert.equal(orderEntry.totalCents, 2900);

const shippedOrderEntry = normalizeShirtOrder({
  name: "Another Buyer",
  email: "buyer2@example.com",
  venmo_handle: "@buyer-two",
  size: "M",
  shipping_address: "456 Example Way\nLos Angeles, CA 90001",
  shipping_state: "CA",
  price_acknowledged: true,
  order_terms_acknowledged: true,
  shirt_price_cents: 2900,
  shipping_cents: 500,
  total_cents: 3400,
  build_code: "OTW-2B3C",
  body_style: "long",
  color: "navy",
  front_art: "brandmark",
  back_art: "frgmnts"
});
assert.equal(shippedOrderEntry.shippingCents, 500);
assert.equal(shippedOrderEntry.totalCents, 3400);
assert.throws(() => normalizeShirtOrder({
  name: "Price Tamper",
  email: "tamper@example.com",
  venmo_handle: "@tamper",
  size: "M",
  shipping_address: "456 Example Way\nLos Angeles, CA 90001",
  shipping_state: "CA",
  price_acknowledged: true,
  order_terms_acknowledged: true,
  shirt_price_cents: 2900,
  shipping_cents: 0,
  total_cents: 2900,
  build_code: "OTW-2B3C",
  body_style: "long",
  color: "navy",
  front_art: "brandmark",
  back_art: "frgmnts"
}), /displayed total/);

const notificationSubmissions = [];
const notificationResult = await sendShirtOrderNotification(
  { ORDER_NOTIFICATION_ENDPOINT: "https://formspree.io/f/testform" },
  shippedOrderEntry,
  new Blob([new Uint8Array(2048)], { type: "image/jpeg" }),
  "image/jpeg",
  "OTW-TEST1234",
  "https://otw-private-intake.ryandavid.workers.dev/shirt-order-artwork/" + "a".repeat(64),
  async (url, init) => {
    notificationSubmissions.push({ url, init });
    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { "content-type": "application/json" }
    });
  }
);
assert.equal(notificationResult.status, "sent");
assert.equal(notificationResult.attachmentDelivered, true);
assert.equal(notificationSubmissions.length, 1);
assert.equal(notificationSubmissions[0].url, "https://formspree.io/f/testform");
assert.equal(notificationSubmissions[0].init.body.get("order_id"), "OTW-TEST1234");
assert.equal(notificationSubmissions[0].init.body.get("order_total"), "$34.00 USD");
assert.match(
  notificationSubmissions[0].init.body.get("finished_design_download"),
  /shirt-order-artwork/
);
assert.equal(notificationSubmissions[0].init.body.get("finished_design").type, "image/jpeg");

let fallbackAttempts = 0;
const fallbackNotification = await sendShirtOrderNotification(
  { ORDER_NOTIFICATION_ENDPOINT: "https://formspree.io/f/testform" },
  orderEntry,
  new Blob([new Uint8Array(2048)], { type: "image/jpeg" }),
  "image/jpeg",
  "OTW-TEST5678",
  "https://otw-private-intake.ryandavid.workers.dev/shirt-order-artwork/" + "b".repeat(64),
  async (_url, init) => {
    fallbackAttempts += 1;
    if (fallbackAttempts === 1) {
      assert.equal(init.body.get("finished_design").type, "image/jpeg");
      return new Response(JSON.stringify({
        error: "File Uploads Not Permitted",
        errors: [{ message: "File Uploads Not Permitted" }]
      }), {
        status: 422,
        headers: { "content-type": "application/json" }
      });
    }
    assert.equal(init.body.get("finished_design"), null);
    assert.match(init.body.get("finished_design_status"), /private download link/);
    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { "content-type": "application/json" }
    });
  }
);
assert.equal(fallbackAttempts, 2);
assert.equal(fallbackNotification.status, "sent");
assert.equal(fallbackNotification.attachmentDelivered, false);

class FakeStatement {
  constructor(database, sql) {
    this.database = database;
    this.sql = sql;
    this.values = [];
  }

  bind(...values) {
    this.values = values;
    return this;
  }

  async run() {
    this.database.writes.push({ sql: this.sql, values: this.values });
    return { meta: { changes: 1 } };
  }

  async all() {
    return { results: this.database.expiredOrderRows };
  }
}

class FakeDatabase {
  constructor() {
    this.writes = [];
    this.expiredOrderRows = [];
  }

  prepare(sql) {
    return new FakeStatement(this, sql);
  }
}

class FakeBucket {
  constructor() {
    this.puts = [];
    this.deletes = [];
  }

  async put(key, value, options) {
    this.puts.push({ key, value, options });
  }

  async delete(key) {
    this.deletes.push(key);
  }
}

const database = new FakeDatabase();
const bucket = new FakeBucket();
const env = {
  ALLOWED_ORIGINS: "https://outsidetheworld.com",
  INTAKE_DB: database,
  ORDER_ARTIFACTS: bucket
};

const forbidden = await worker.fetch(new Request(
  "https://intake.example/subscribe-frgmnts-waitlist",
  {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "origin": "https://example.com"
    },
    body: JSON.stringify({ email: "person@example.com" })
  }
), env);
assert.equal(forbidden.status, 403);

const accepted = await worker.fetch(new Request(
  "https://intake.example/subscribe-frgmnts-waitlist",
  {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "origin": "https://outsidetheworld.com"
    },
    body: JSON.stringify({ email: "person@example.com" })
  }
), env);
assert.equal(accepted.status, 200);
assert.equal(database.writes.length, 1);
assert.equal((await accepted.json()).ok, true);
assert.equal(accepted.headers.get("access-control-allow-origin"), "https://outsidetheworld.com");

const orderForm = new FormData();
orderForm.append("order", JSON.stringify({
  name: "A Buyer",
  email: "buyer@example.com",
  venmo_handle: "@buyer-name",
  size: "XL",
  shipping_address: "123 Example Way\nPhoenix, AZ 85001",
  shipping_state: "AZ",
  price_acknowledged: true,
  order_terms_acknowledged: true,
  shirt_price_cents: 2900,
  shipping_cents: 0,
  total_cents: 2900,
  build_code: "OTW-1A2B",
  body_style: "short",
  color: "black",
  front_art: "frgmnts",
  back_art: "full",
  slogan: "THE ANALOG DAWN"
}));
orderForm.append(
  "artwork",
  new Blob([new Uint8Array(2048)], { type: "image/jpeg" }),
  "shirt.jpg"
);
const acceptedOrder = await worker.fetch(new Request(
  "https://intake.example/submit-shirt-order",
  {
    method: "POST",
    headers: {
      "origin": "https://outsidetheworld.com"
    },
    body: orderForm
  }
), env);
const acceptedOrderBody = await acceptedOrder.json();
assert.equal(acceptedOrder.status, 200);
assert.equal(acceptedOrderBody.ok, true);
assert.match(acceptedOrderBody.order_id, /^OTW-[A-F0-9]{8}$/);
assert.equal(acceptedOrderBody.shipping_cents, 0);
assert.equal(acceptedOrderBody.total_cents, 2900);
assert.equal(database.writes.length, 2);
assert.equal(bucket.puts.length, 1);
assert.equal(bucket.puts[0].options.httpMetadata.contentType, "image/jpeg");

await purgeExpiredRecords(env, "2026-07-23T12:00:00.000Z");
assert.equal(database.writes.length, 7);
assert.equal(
  database.writes.slice(2).every(({ sql, values }) =>
    sql.includes("DELETE FROM") &&
    sql.includes("retention_until <= ?") &&
    values[0] === "2026-07-23T12:00:00.000Z"
  ),
  true
);

console.log("private intake worker tests passed");
