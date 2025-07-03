-- sql/dws/create_dws_tvl_snapshots_dm.sql
-- Description: Creates the dws_tvl_snapshots_dm fact table.
-- This table stores detailed Total Value Locked (TVL) snapshots.

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
