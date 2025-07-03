-- sql/dws/create_dws_token_prices_dm.sql
-- Description: Creates the dws_token_prices_dm fact table.
-- This table stores detailed token price snapshots.

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
