CREATE TABLE IF NOT EXISTS shirt_orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT 'received'
    CHECK (status IN ('received', 'contacted', 'paid', 'fulfilled', 'cancelled')),
  name TEXT NOT NULL,
  email TEXT NOT NULL COLLATE NOCASE,
  venmo_handle TEXT NOT NULL COLLATE NOCASE,
  size TEXT NOT NULL CHECK (size IN ('S', 'M', 'L', 'XL', '2XL')),
  shipping_address TEXT NOT NULL,
  shipping_state TEXT NOT NULL,
  note TEXT NOT NULL DEFAULT '',
  shirt_price_cents INTEGER NOT NULL CHECK (shirt_price_cents = 2900),
  shipping_cents INTEGER NOT NULL CHECK (shipping_cents IN (0, 500)),
  total_cents INTEGER NOT NULL CHECK (total_cents = shirt_price_cents + shipping_cents),
  currency TEXT NOT NULL DEFAULT 'USD' CHECK (currency = 'USD'),
  price_acknowledged INTEGER NOT NULL DEFAULT 1 CHECK (price_acknowledged = 1),
  order_terms_acknowledged INTEGER NOT NULL DEFAULT 1 CHECK (order_terms_acknowledged = 1),
  build_code TEXT NOT NULL,
  body_style TEXT NOT NULL,
  color TEXT NOT NULL,
  front_art TEXT NOT NULL,
  back_art TEXT NOT NULL,
  slogan TEXT NOT NULL DEFAULT '',
  artwork_key TEXT NOT NULL UNIQUE,
  artwork_content_type TEXT NOT NULL,
  artwork_bytes INTEGER NOT NULL,
  artwork_sha256 TEXT NOT NULL,
  notification_status TEXT NOT NULL DEFAULT 'pending'
    CHECK (notification_status IN ('pending', 'sent', 'failed')),
  notification_attachment INTEGER NOT NULL DEFAULT 0
    CHECK (notification_attachment IN (0, 1)),
  notification_attempts INTEGER NOT NULL DEFAULT 0,
  notification_error TEXT NOT NULL DEFAULT '',
  notification_last_attempt_at TEXT,
  notification_sent_at TEXT,
  source TEXT NOT NULL,
  consent_version TEXT NOT NULL,
  submitted_at TEXT NOT NULL,
  retention_until TEXT NOT NULL,
  fulfilled_at TEXT,
  deleted_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_shirt_orders_status
  ON shirt_orders (status, submitted_at);

CREATE INDEX IF NOT EXISTS idx_shirt_orders_email
  ON shirt_orders (email, submitted_at);

CREATE INDEX IF NOT EXISTS idx_shirt_orders_retention
  ON shirt_orders (retention_until)
  WHERE deleted_at IS NULL;
