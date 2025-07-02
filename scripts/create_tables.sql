-- Drop tables if they exist to ensure a clean slate for schema updates
DROP TABLE IF EXISTS tvl_snapshots CASCADE;
DROP TABLE IF EXISTS apy_snapshots CASCADE;
DROP TABLE IF EXISTS token_prices CASCADE;
DROP TABLE IF EXISTS top_wallets CASCADE;
DROP TABLE IF EXISTS risk_metrics CASCADE;

-- 1. TVL snapshots
CREATE TABLE tvl_snapshots (
    id SERIAL PRIMARY KEY,
    protocol_name VARCHAR(100) NOT NULL,
    protocol_segment VARCHAR(100),
    address VARCHAR(255) NOT NULL,
    asset VARCHAR(255),
    tvl NUMERIC(30,4) NOT NULL,
    snapshot_time TIMESTAMP NOT NULL,
    data_source VARCHAR(100),
    chain VARCHAR(50),
    UNIQUE (protocol_name, protocol_segment, address, snapshot_time)
);
CREATE INDEX idx_tvl_snapshots_protocol_time ON tvl_snapshots(protocol_name, snapshot_time);

-- 2. APY snapshots
CREATE TABLE IF NOT EXISTS apy_snapshots (
    id SERIAL PRIMARY KEY,
    protocol_name VARCHAR(100) NOT NULL,
    protocol_segment VARCHAR(100),
    address VARCHAR(255),
    pool_name VARCHAR(100),
    apy NUMERIC(10,4),
    snapshot_time TIMESTAMP NOT NULL DEFAULT now(),
    data_source VARCHAR(100),
    chain VARCHAR(50),
    UNIQUE (protocol_name, protocol_segment, address, snapshot_time)
);
CREATE INDEX idx_apy_snapshots_protocol_time ON apy_snapshots(protocol_name, snapshot_time);

-- 3. Token prices
CREATE TABLE IF NOT EXISTS token_prices (
    id SERIAL PRIMARY KEY,
    token_symbol VARCHAR(50) NOT NULL,
    token_address VARCHAR(255),
    price_usd NUMERIC(20,8),
    snapshot_time TIMESTAMP NOT NULL DEFAULT now(),
    data_source VARCHAR(100),
    chain VARCHAR(50),
    UNIQUE (token_symbol, token_address, snapshot_time)
);
CREATE INDEX idx_token_prices_time ON token_prices(snapshot_time);

-- 4. Top wallet holdings
CREATE TABLE IF NOT EXISTS top_wallets (
    id SERIAL PRIMARY KEY,
    protocol_name VARCHAR(100) NOT NULL,
    protocol_segment VARCHAR(100),
    wallet_address VARCHAR(255) NOT NULL,
    balance NUMERIC(30,8),
    snapshot_time TIMESTAMP NOT NULL DEFAULT now(),
    data_source VARCHAR(100),
    chain VARCHAR(50),
    UNIQUE (protocol_name, protocol_segment, wallet_address, snapshot_time)
);
CREATE INDEX idx_top_wallets_protocol_time ON top_wallets(protocol_name, snapshot_time);

-- 5. Risk metrics (generic)
CREATE TABLE IF NOT EXISTS risk_metrics (
    id SERIAL PRIMARY KEY,
    protocol_name VARCHAR(100) NOT NULL,
    protocol_segment VARCHAR(100),
    metric_name VARCHAR(100),
    metric_value NUMERIC(30,10),
    collected_at TIMESTAMP NOT NULL DEFAULT now(),
    data_source VARCHAR(100),
    chain VARCHAR(50),
    UNIQUE (protocol_name, protocol_segment, metric_name, collected_at)
);
CREATE INDEX idx_risk_metrics_protocol_time ON risk_metrics(protocol_name, collected_at);