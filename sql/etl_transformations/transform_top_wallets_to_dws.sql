-- sql/etl_transformations/transform_top_wallets_to_dws.sql
-- Description: Inserts top wallets data into the dws_top_wallets_dm fact table.
-- Dependencies: dim_protocol_dm, dim_asset_dm, dim_time_dm
-- Output: dws_top_wallets_dm

INSERT INTO dws_top_wallets_dm (protocol_id, asset_id, time_id, wallet_address, balance_usd, data_source)
SELECT
    %s, -- protocol_id
    %s, -- asset_id
    %s, -- time_id
    wallet_address,
    balance_usd,
    data_source
FROM (
    -- Dummy data for top wallets
    SELECT 'dummy_wallet_1_Indigo' as wallet_address, 100000.0 as balance_usd, 'Dummy Data' as data_source
    UNION ALL SELECT 'dummy_wallet_2_Indigo', 50000.0, 'Dummy Data'
    UNION ALL SELECT 'dummy_wallet_3_Indigo', 33333.33, 'Dummy Data'
    UNION ALL SELECT 'dummy_wallet_4_Indigo', 25000.0, 'Dummy Data'
    UNION ALL SELECT 'dummy_wallet_5_Indigo', 20000.0, 'Dummy Data'
    UNION ALL SELECT 'dummy_wallet_6_Indigo', 16666.67, 'Dummy Data'
    UNION ALL SELECT 'dummy_wallet_7_Indigo', 14285.71, 'Dummy Data'
    UNION ALL SELECT 'dummy_wallet_8_Indigo', 12500.0, 'Dummy Data'
    UNION ALL SELECT 'dummy_wallet_9_Indigo', 11111.11, 'Dummy Data'
    UNION ALL SELECT 'dummy_wallet_10_Indigo', 10000.0, 'Dummy Data'
) AS dummy_data
ON CONFLICT (protocol_id, asset_id, time_id, wallet_address) DO NOTHING;
