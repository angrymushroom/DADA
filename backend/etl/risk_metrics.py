from backend.db import get_db_connection

def compute_risk_metrics(protocol):
    conn = get_db_connection()
    cur = conn.cursor()
    # TVL volatility
    cur.execute("""
        SELECT stddev(tvl) FROM tvl_snapshots
        WHERE protocol_name = %s AND snapshot_time > now() - interval '7 days'
    """, (protocol,))
    tvl_vol = cur.fetchone()[0]

    # Whale concentration
    cur.execute("""
        SELECT sum(balance) FROM (
            SELECT balance FROM top_wallets
            WHERE protocol_name = %s
            ORDER BY balance DESC
            LIMIT 10
        ) t
    """, (protocol,))
    top_balance = cur.fetchone()[0] or 0

    cur.execute("""
        SELECT sum(balance) FROM top_wallets
        WHERE protocol_name = %s
    """, (protocol,))
    total_balance = cur.fetchone()[0] or 1

    whale_pct = (top_balance / total_balance) * 100

    cur.close()
    conn.close()
    return tvl_vol, whale_pct

def main():
    protocol = "minswap"
    tvl_vol, whale_pct = compute_risk_metrics(protocol)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO risk_metrics (protocol_name, metric_name, metric_value) VALUES (%s, %s, %s)",
        (protocol, "tvl_volatility", tvl_vol)
    )
    cur.execute(
        "INSERT INTO risk_metrics (protocol_name, metric_name, metric_value) VALUES (%s, %s, %s)",
        (protocol, "whale_concentration_pct", whale_pct)
    )
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
