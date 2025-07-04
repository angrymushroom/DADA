-- sql/etl_transformations/transform_risk_metrics_to_dws.sql
-- Description: Inserts risk metrics data into the dws_risk_metrics_dm fact table.
-- Dependencies: dim_protocol_dm, dim_time_dm, dws_tvl_snapshots_dm, dws_top_wallets_dm
-- Output: dws_risk_metrics_dm

INSERT INTO dws_risk_metrics_dm (protocol_id, time_id, metric_name, metric_value, data_source)
SELECT
    %s, -- protocol_id
    %s, -- time_id
    'tvl_volatility',
    COALESCE(stddev(dws_tvl.tvl_usd), 0.0),
    'Internal Calculation'
FROM
    dws_tvl_snapshots_dm dws_tvl
WHERE
    dws_tvl.protocol_id = %s AND dws_tvl.time_id IN (
        SELECT time_id FROM dim_time_dm WHERE date > (SELECT date FROM dim_time_dm WHERE time_id = %s) - INTERVAL '7 days'
    )
GROUP BY
    %s, %s -- protocol_id, time_id
ON CONFLICT (protocol_id, time_id, metric_name) DO UPDATE SET
    metric_value = EXCLUDED.metric_value,
    data_source = EXCLUDED.data_source;

INSERT INTO dws_risk_metrics_dm (protocol_id, time_id, metric_name, metric_value, data_source)
SELECT
    protocol_id,
    time_id,
    'whale_concentration_pct',
    COALESCE(
        (SUM(CASE WHEN rn <= 10 THEN balance_usd ELSE 0 END) / NULLIF(SUM(balance_usd), 0)) * 100,
        0.0
    ),
    'Internal Calculation'
FROM (
    SELECT
        protocol_id,
        time_id,
        balance_usd,
        ROW_NUMBER() OVER (PARTITION BY protocol_id ORDER BY balance_usd DESC) as rn
    FROM
        dws_top_wallets_dm
    WHERE
        protocol_id = %s AND time_id = %s
) AS ranked_wallets
GROUP BY
    protocol_id, time_id
ON CONFLICT (protocol_id, time_id, metric_name) DO UPDATE SET
    metric_value = EXCLUDED.metric_value,
    data_source = EXCLUDED.data_source;
