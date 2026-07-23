#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const [inputPath, outputPath] = process.argv.slice(2);

if (!inputPath || !outputPath) {
  throw new Error("Usage: build_private_intake_seed.mjs <waitlist.json> <output.sql>");
}

const entries = JSON.parse(fs.readFileSync(inputPath, "utf8"));
if (!Array.isArray(entries)) {
  throw new Error("Waitlist input must be an array");
}

function sqlString(value) {
  return `'${String(value ?? "").replaceAll("'", "''")}'`;
}

function normalizeEmail(value) {
  const email = String(value || "").trim().toLowerCase();
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new Error("Waitlist input contains an invalid email address");
  }
  return email;
}

function normalizeTimestamp(value) {
  const timestamp = new Date(value);
  if (Number.isNaN(timestamp.getTime())) {
    throw new Error("Waitlist input contains an invalid timestamp");
  }
  return timestamp.toISOString();
}

function addYears(timestamp, years) {
  const value = new Date(timestamp);
  value.setUTCFullYear(value.getUTCFullYear() + years);
  return value.toISOString();
}

const statements = entries.map((entry) => {
  const email = normalizeEmail(entry?.email);
  const source = String(entry?.source || "frgmnts_launch_page").trim().slice(0, 80);
  const note = String(entry?.note || "").trim().slice(0, 200);
  const submittedAt = normalizeTimestamp(entry?.timestamp);
  const retentionUntil = addYears(submittedAt, 2);

  return [
    "INSERT INTO waitlist_entries",
    "  (email, source, note, consent_version, submitted_at, retention_until)",
    `VALUES (${sqlString(email)}, ${sqlString(source)}, ${sqlString(note)}, ` +
      `${sqlString("2026-03-30")}, ${sqlString(submittedAt)}, ${sqlString(retentionUntil)})`,
    "ON CONFLICT(email) DO NOTHING;"
  ].join("\n");
});

const output = [
  "PRAGMA foreign_keys = ON;",
  ...statements,
  ""
].join("\n");

fs.mkdirSync(path.dirname(outputPath), { recursive: true, mode: 0o700 });
fs.writeFileSync(outputPath, output, { encoding: "utf8", mode: 0o600 });
console.log(`Prepared ${entries.length} waitlist records for private migration.`);
