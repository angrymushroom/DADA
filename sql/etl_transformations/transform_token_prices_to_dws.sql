INSERT INTO dws_token_prices_dm (asset_id, time_id, price_usd, data_source)
SELECT
    da.asset_id,
    dt.time_id,
    oc.price_usd,
    'CoinGecko'
FROM
    ods_coingecko_prices_hm oc
JOIN
    dim_time_dm dt ON oc.timestamp::date = dt.date
JOIN
    dim_asset_dm da ON oc.coingecko_id = da.asset_name -- Assuming coingecko_id maps to asset_name for now
ON CONFLICT (asset_id, time_id) DO UPDATE SET
    price_usd = EXCLUDED.price_usd,
    data_source = EXCLUDED.data_source;