-- sql/dws/create_dws_apy_snapshots_dm.sql
-- Description: Creates the dws_apy_snapshots_dm fact table.
-- This table stores detailed APY snapshots.

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
