import assert from "node:assert/strict";
import worker, {
  normalizeProfessionalInquiry,
  normalizeSeatCheckin,
  normalizeSupportRequest,
  normalizeWaitlistEntry,
  purgeExpiredRecords
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
}

class FakeDatabase {
  constructor() {
    this.writes = [];
  }

  prepare(sql) {
    return new FakeStatement(this, sql);
  }
}

const database = new FakeDatabase();
const env = {
  ALLOWED_ORIGINS: "https://outsidetheworld.com",
  INTAKE_DB: database
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

await purgeExpiredRecords(env, "2026-07-23T12:00:00.000Z");
assert.equal(database.writes.length, 5);
assert.equal(
  database.writes.slice(1).every(({ sql, values }) =>
    sql.includes("DELETE FROM") &&
    sql.includes("retention_until <= ?") &&
    values[0] === "2026-07-23T12:00:00.000Z"
  ),
  true
);

console.log("private intake worker tests passed");
