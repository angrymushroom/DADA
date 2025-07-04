-- sql/etl_transformations/transform_apy_to_dws.sql
-- Description: Transforms APY data into the dws_apy_snapshots_dm fact table.
-- Dependencies: dim_protocol_dm, dim_asset_dm, dim_time_dm
-- Output: dws_apy_snapshots_dm

INSERT INTO dws_apy_snapshots_dm (protocol_id, asset_id, time_id, pool_name, apy_value, data_source)
SELECT
    dp.protocol_id,
    da.asset_id,
    dt.time_id,
    'qADA - Supply', -- Hardcoded for now, will be dynamic later
    0.035, -- Dummy APY value
    'Estimated'
FROM
    dim_protocol_dm dp
JOIN
    dim_asset_dm da ON da.asset_symbol = 'ADA'
JOIN
    dim_time_dm dt ON dt.date = CURRENT_DATE
WHERE
    dp.protocol_name = 'Liqwid'
ON CONFLICT (protocol_id, asset_id, time_id, pool_name) DO UPDATE SET
    apy_value = EXCLUDED.apy_value,
    data_source = EXCLUDED.data_source;

INSERT INTO dws_apy_snapshots_dm (protocol_id, asset_id, time_id, pool_name, apy_value, data_source)
SELECT
    dp.protocol_id,
    da.asset_id,
    dt.time_id,
    'qADA - Borrow', -- Hardcoded for now, will be dynamic later
    0.08, -- Dummy APY value
    'Estimated'
FROM
    dim_protocol_dm dp
JOIN
    dim_asset_dm da ON da.asset_symbol = 'ADA'
JOIN
    dim_time_dm dt ON dt.date = CURRENT_DATE
WHERE
    dp.protocol_name = 'Liqwid'
ON CONFLICT (protocol_id, asset_id, time_id, pool_name) DO UPDATE SET
    apy_value = EXCLUDED.apy_value,
    data_source = EXCLUDED.data_source;
