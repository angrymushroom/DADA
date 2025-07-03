-- sql/dimensions/create_dim_asset_dm.sql
-- Description: Creates the dim_asset_dm dimension table.
-- This table stores information about different assets (tokens).

CREATE TABLE IF NOT EXISTS dim_asset_dm (
    asset_id SERIAL PRIMARY KEY,
    asset_symbol VARCHAR(255) NOT NULL UNIQUE, -- e.g., ADA, MIN, IUSD
    asset_name VARCHAR(255), -- e.g., Cardano, Minswap, Indigo Protocol iUSD
    asset_policy_id VARCHAR(255), -- For native tokens on Cardano
    asset_fingerprint VARCHAR(255) -- For native tokens on Cardano
);
