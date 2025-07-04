-- scripts/create_tables.sql
-- Description: This script creates all necessary tables for the DADA project.
-- It drops existing tables to ensure a clean slate for schema migration.

-- Drop existing tables (order matters due to foreign key constraints)
DROP TABLE IF EXISTS dws_tvl_snapshots_dm CASCADE;
DROP TABLE IF EXISTS dws_token_prices_dm CASCADE;
DROP TABLE IF EXISTS dws_apy_snapshots_dm CASCADE;
DROP TABLE IF EXISTS dws_top_wallets_dm CASCADE;
DROP TABLE IF EXISTS dws_risk_metrics_dm CASCADE;
DROP TABLE IF EXISTS ods_coingecko_prices_hm CASCADE;

DROP TABLE IF EXISTS apy_snapshots CASCADE;
DROP TABLE IF EXISTS risk_metrics CASCADE;
DROP TABLE IF EXISTS token_prices CASCADE;
DROP TABLE IF EXISTS top_wallets CASCADE;
DROP TABLE IF EXISTS tvl_snapshots CASCADE;

DROP TABLE IF EXISTS dim_protocol_dm CASCADE;
DROP TABLE IF EXISTS dim_asset_dm CASCADE;
DROP TABLE IF EXISTS dim_time_dm CASCADE;

-- Create Dimension Tables
CREATE TABLE IF NOT EXISTS dim_time_dm (
    time_id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    year SMALLINT NOT NULL,
    month SMALLINT NOT NULL,
    day SMALLINT NOT NULL,
    day_of_week SMALLINT NOT NULL,
    day_name VARCHAR(9) NOT NULL,
    month_name VARCHAR(9) NOT NULL,
    quarter SMALLINT NOT NULL,
    week_of_year SMALLINT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_protocol_dm (
    protocol_id SERIAL PRIMARY KEY,
    protocol_name VARCHAR(255) NOT NULL UNIQUE,
    protocol_segment VARCHAR(255), -- e.g., 'DEX', 'Lending Pool', 'CDP'
    chain VARCHAR(255) -- e.g., 'Cardano'
);

CREATE TABLE IF NOT EXISTS dim_asset_dm (
    asset_id SERIAL PRIMARY KEY,
    asset_symbol VARCHAR(255) NOT NULL UNIQUE, -- e.g., ADA, MIN, IUSD
    asset_name VARCHAR(255), -- e.g., Cardano, Minswap, Indigo Protocol iUSD
    asset_policy_id VARCHAR(255), -- For native tokens on Cardano
    asset_fingerprint VARCHAR(255) -- For native tokens on Cardano
);

-- Create ODS Tables
CREATE TABLE IF NOT EXISTS ods_coingecko_prices_hm (
    id SERIAL PRIMARY KEY,
    coingecko_id VARCHAR(255) NOT NULL,
    price_usd NUMERIC(20, 8) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL
);

-- Create DWS Fact Tables
CREATE TABLE IF NOT EXISTS dws_tvl_snapshots_dm (
    tvl_snapshot_id SERIAL PRIMARY KEY,
    protocol_id INT NOT NULL, -- FK to dim_protocol_dm
    asset_id INT, -- FK to dim_asset_dm (optional, as some TVL might be overall protocol TVL)
    time_id INT NOT NULL, -- FK to dim_time_dm
    address VARCHAR(255), -- The pool/CDP address
    tvl_usd NUMERIC(38, 8) NOT NULL,
    data_source VARCHAR(255),
    
    CONSTRAINT fk_protocol
        FOREIGN KEY(protocol_id)
        REFERENCES dim_protocol_dm(protocol_id),
    CONSTRAINT fk_asset
        FOREIGN KEY(asset_id)
        REFERENCES dim_asset_dm(asset_id),
    CONSTRAINT fk_time
        FOREIGN KEY(time_id)
        REFERENCES dim_time_dm(time_id),
    UNIQUE (protocol_id, time_id, address)
);

CREATE TABLE IF NOT EXISTS dws_token_prices_dm (
    token_price_id SERIAL PRIMARY KEY,
    asset_id INT NOT NULL, -- FK to dim_asset_dm
    time_id INT NOT NULL, -- FK to dim_time_dm
    price_usd NUMERIC(20, 8) NOT NULL,
    data_source VARCHAR(255),
    
    CONSTRAINT fk_asset
        FOREIGN KEY(asset_id)
        REFERENCES dim_asset_dm(asset_id),
    CONSTRAINT fk_time
        FOREIGN KEY(time_id)
        REFERENCES dim_time_dm(time_id),
    UNIQUE (asset_id, time_id)
);

CREATE TABLE IF NOT EXISTS dws_apy_snapshots_dm (
    apy_snapshot_id SERIAL PRIMARY KEY,
    protocol_id INT NOT NULL, -- FK to dim_protocol_dm
    asset_id INT, -- FK to dim_asset_dm (if APY is asset-specific)
    time_id INT NOT NULL, -- FK to dim_time_dm
    pool_name VARCHAR(255), -- e.g., qADA
    apy_value NUMERIC(10, 8) NOT NULL,
    data_source VARCHAR(255),
    
    CONSTRAINT fk_protocol
        FOREIGN KEY(protocol_id)
        REFERENCES dim_protocol_dm(protocol_id),
    CONSTRAINT fk_asset
        FOREIGN KEY(asset_id)
        REFERENCES dim_asset_dm(asset_id),
    CONSTRAINT fk_time
        FOREIGN KEY(time_id)
        REFERENCES dim_time_dm(time_id),
    UNIQUE (protocol_id, asset_id, time_id, pool_name)
);

CREATE TABLE IF NOT EXISTS dws_top_wallets_dm (
    top_wallet_id SERIAL PRIMARY KEY,
    protocol_id INT NOT NULL, -- FK to dim_protocol_dm
    asset_id INT NOT NULL, -- FK to dim_asset_dm
    time_id INT NOT NULL, -- FK to dim_time_dm
    wallet_address VARCHAR(255) NOT NULL,
    balance_usd NUMERIC(20, 8) NOT NULL,
    data_source VARCHAR(255),
    
    CONSTRAINT fk_protocol
        FOREIGN KEY(protocol_id)
        REFERENCES dim_protocol_dm(protocol_id),
    CONSTRAINT fk_asset
        FOREIGN KEY(asset_id)
        REFERENCES dim_asset_dm(asset_id),
    CONSTRAINT fk_time
        FOREIGN KEY(time_id)
        REFERENCES dim_time_dm(time_id),
    UNIQUE (protocol_id, asset_id, time_id, wallet_address)
);

CREATE TABLE IF NOT EXISTS dws_risk_metrics_dm (
    risk_metric_id SERIAL PRIMARY KEY,
    protocol_id INT NOT NULL, -- FK to dim_protocol_dm
    time_id INT NOT NULL, -- FK to dim_time_dm
    metric_name VARCHAR(255) NOT NULL,
    metric_value NUMERIC(20, 8) NOT NULL,
    data_source VARCHAR(255),
    
    CONSTRAINT fk_protocol
        FOREIGN KEY(protocol_id)
        REFERENCES dim_protocol_dm(protocol_id),
    CONSTRAINT fk_time
        FOREIGN KEY(time_id)
        REFERENCES dim_time_dm(time_id),
    UNIQUE (protocol_id, time_id, metric_name)
);