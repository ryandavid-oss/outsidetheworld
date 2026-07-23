ALTER TABLE shirt_orders
  ADD COLUMN artwork_access_token_hash TEXT;

ALTER TABLE shirt_orders
  ADD COLUMN artwork_access_expires_at TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS idx_shirt_orders_artwork_access_token
  ON shirt_orders (artwork_access_token_hash)
  WHERE artwork_access_token_hash IS NOT NULL;
