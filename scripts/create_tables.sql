-- 1. TVL snapshots
CREATE TABLE IF NOT EXISTS tvl_snapshots (
    id SERIAL PRIMARY KEY,
    protocol_name TEXT NOT NULL,
    tvl NUMERIC,
    snapshot_time TIMESTAMP DEFAULT now()
);

-- 2. APY snapshots
CREATE TABLE IF NOT EXISTS apy_snapshots (
    id SERIAL PRIMARY KEY,
    protocol_name TEXT NOT NULL,
    pool_name TEXT,
    apy NUMERIC,
    snapshot_time TIMESTAMP DEFAULT now()
);

-- 3. Token prices
CREATE TABLE IF NOT EXISTS token_prices (
    id SERIAL PRIMARY KEY,
    token_symbol TEXT NOT NULL,
    price_usd NUMERIC,
    snapshot_time TIMESTAMP DEFAULT now()
);

-- 4. Top wallet holdings
CREATE TABLE IF NOT EXISTS top_wallets (
    id SERIAL PRIMARY KEY,
    protocol_name TEXT NOT NULL,
    wallet_address TEXT NOT NULL,
    balance NUMERIC,
    snapshot_time TIMESTAMP DEFAULT now()
);

-- 5. Risk metrics (generic)
CREATE TABLE IF NOT EXISTS risk_metrics (
    id SERIAL PRIMARY KEY,
    protocol_name TEXT NOT NULL,
    metric_name TEXT,
    metric_value NUMERIC,
    collected_at TIMESTAMP DEFAULT now()
);
