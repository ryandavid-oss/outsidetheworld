PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS waitlist_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL COLLATE NOCASE UNIQUE,
  source TEXT NOT NULL,
  note TEXT NOT NULL DEFAULT '',
  consent_version TEXT NOT NULL,
  submitted_at TEXT NOT NULL,
  retention_until TEXT,
  deleted_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_waitlist_retention
  ON waitlist_entries (retention_until)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS professional_inquiries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  contact TEXT NOT NULL,
  inquiry_type TEXT NOT NULL,
  comment TEXT NOT NULL,
  source TEXT NOT NULL,
  consent_version TEXT NOT NULL,
  submitted_at TEXT NOT NULL,
  retention_until TEXT NOT NULL,
  deleted_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_professional_retention
  ON professional_inquiries (retention_until)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS support_requests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL DEFAULT '',
  email TEXT NOT NULL COLLATE NOCASE,
  handle TEXT NOT NULL DEFAULT '',
  topic TEXT NOT NULL,
  message TEXT NOT NULL,
  urgent INTEGER NOT NULL DEFAULT 0 CHECK (urgent IN (0, 1)),
  source TEXT NOT NULL,
  consent_version TEXT NOT NULL,
  submitted_at TEXT NOT NULL,
  retention_until TEXT NOT NULL,
  deleted_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_support_retention
  ON support_requests (retention_until)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS seat_checkins (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL DEFAULT '',
  email TEXT NOT NULL COLLATE NOCASE,
  did_try TEXT NOT NULL,
  stopped_at TEXT NOT NULL,
  signals_json TEXT NOT NULL,
  message TEXT NOT NULL DEFAULT '',
  wants_reply INTEGER NOT NULL DEFAULT 0 CHECK (wants_reply IN (0, 1)),
  source TEXT NOT NULL,
  consent_version TEXT NOT NULL,
  submitted_at TEXT NOT NULL,
  retention_until TEXT NOT NULL,
  deleted_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_seat_checkin_retention
  ON seat_checkins (retention_until)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS privacy_request_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  request_type TEXT NOT NULL,
  subject_reference TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'received',
  requested_at TEXT NOT NULL,
  completed_at TEXT,
  notes TEXT NOT NULL DEFAULT ''
);
