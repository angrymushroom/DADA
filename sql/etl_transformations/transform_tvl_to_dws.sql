-- sql/etl_transformations/transform_tvl_to_dws.sql
-- Description: Inserts TVL data into the dws_tvl_snapshots_dm fact table.
-- Dependencies: dim_protocol_dm, dim_time_dm
-- Output: dws_tvl_snapshots_dm

INSERT INTO dws_tvl_snapshots_dm (protocol_id, time_id, address, tvl_usd, data_source)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (protocol_id, time_id, address) DO NOTHING;
