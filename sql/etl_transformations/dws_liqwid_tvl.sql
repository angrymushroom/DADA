-- sql/etl_transformations/transform_liqwid_tvl_to_dws.sql
-- Description: Transforms Liqwid TVL data into the dws_tvl_snapshots_dm fact table.
-- Dependencies: dim_protocol_dm, dim_asset_dm, dim_time_dm
-- Output: dws_tvl_snapshots_dm

INSERT INTO dws_tvl_snapshots_dm (protocol_id, asset_id, time_id, address, tvl_usd, data_source)
SELECT
    dp.protocol_id,
    da.asset_id,
    dt.time_id,
    'dummy_liqwid_pool_address', -- Dummy address for now
    500000.0, -- Dummy TVL value
    'Dummy Data'
FROM
    dim_protocol_dm dp
JOIN
    dim_asset_dm da ON da.asset_symbol = 'ADA'
JOIN
    dim_time_dm dt ON dt.date = CURRENT_DATE
WHERE
    dp.protocol_name = 'Liqwid'
ON CONFLICT (protocol_id, time_id, address) DO NOTHING;
