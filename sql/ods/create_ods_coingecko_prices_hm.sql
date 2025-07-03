-- sql/ods/create_ods_coingecko_prices_hm.sql
-- Description: Creates the ods_coingecko_prices_hm table.
-- This table serves as a landing zone for raw price data fetched from CoinGecko.

CREATE TABLE IF NOT EXISTS ods_coingecko_prices_hm (
    id SERIAL PRIMARY KEY,
    coingecko_id VARCHAR(255) NOT NULL,
    price_usd NUMERIC(20, 8) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL
);
