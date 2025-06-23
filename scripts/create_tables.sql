CREATE TABLE IF NOT EXISTS tvl_snapshots (
  id SERIAL PRIMARY KEY,
  protocol_name TEXT,
  tvl BIGINT,
  snapshot_time TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS top_wallets (
  id SERIAL PRIMARY KEY,
  protocol_name TEXT,
  wallet_address TEXT,
  balance BIGINT,
  snapshot_time TIMESTAMP DEFAULT now()
);
