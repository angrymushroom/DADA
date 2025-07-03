-- sql/dws/create_dws_top_wallets_dm.sql
-- Description: Creates the dws_top_wallets_dm fact table.
-- This table stores detailed top wallet snapshots.

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
