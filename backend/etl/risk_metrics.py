from datetime import datetime, UTC, timedelta

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.db import get_db_connection

# Configure data retention (in days) via environment variable
# Set to 0 or comment out to disable retention
DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", 0))

def delete_old_data(protocol_name, retention_days):
    """Deletes data older than retention_days for a given protocol."""
    if retention_days <= 0:
        print(f"Data retention is disabled for {protocol_name}.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    cutoff_date = datetime.now(UTC) - timedelta(days=retention_days)
    print(f"Deleting {protocol_name} risk metrics data older than {cutoff_date}...")
    cursor.execute("""
        DELETE FROM risk_metrics
        WHERE protocol_name = %s AND collected_at < %s;
    """, (protocol_name, cutoff_date))
    deleted_rows = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Deleted {deleted_rows} old rows for {protocol_name}.")


def compute_risk_metrics(protocol_name, protocol_segment):
    conn = get_db_connection()
    cur = conn.cursor()

    # TVL volatility
    cur.execute("""
        SELECT stddev(tvl) FROM tvl_snapshots
        WHERE protocol_name = %s AND snapshot_time > now() - interval '7 days'
    """, (protocol_name,))
    tvl_vol = cur.fetchone()[0]

    # Whale concentration (based on available top_wallets data)
    cur.execute("""
        SELECT sum(balance) FROM (
            SELECT balance FROM top_wallets
            WHERE protocol_name = %s
            ORDER BY balance DESC
            LIMIT 10
        ) t
    """, (protocol_name,))
    top_balance = cur.fetchone()[0] or 0

    cur.execute("""
        SELECT sum(balance) FROM top_wallets
        WHERE protocol_name = %s
    """, (protocol_name,))
    total_balance = cur.fetchone()[0] or 1

    whale_pct = (top_balance / total_balance) * 100 if total_balance > 0 else 0

    cur.close()
    conn.close()
    return tvl_vol, whale_pct

def fetch_and_insert_risk_metrics():
    protocols = {
        "Minswap": "DEX",
        "Indigo": "CDP",
        "Liqwid": "Lending Pool"
    }

    conn = get_db_connection()
    cur = conn.cursor()

    for protocol_name, protocol_segment in protocols.items():
        tvl_vol, whale_pct = compute_risk_metrics(protocol_name, protocol_segment)

        # Insert TVL Volatility
        cur.execute(
            """
            INSERT INTO risk_metrics (protocol_name, protocol_segment, metric_name, metric_value, collected_at, data_source, chain)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (protocol_name, protocol_segment, metric_name, collected_at) DO NOTHING;
            """,
            (
                protocol_name,
                protocol_segment,
                "tvl_volatility",
                tvl_vol,
                datetime.now(UTC),
                "Internal Calculation",
                "Cardano"
            )
        )

        # Insert Whale Concentration
        cur.execute(
            """
            INSERT INTO risk_metrics (protocol_name, protocol_segment, metric_name, metric_value, collected_at, data_source, chain)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (protocol_name, protocol_segment, metric_name, collected_at) DO NOTHING;
            """,
            (
                protocol_name,
                protocol_segment,
                "whale_concentration_pct",
                whale_pct,
                datetime.now(UTC),
                "Internal Calculation",
                "Cardano"
            )
        )
    conn.commit()
    cur.close()
    conn.close()

    # Apply data retention after new data is inserted
    delete_old_data("Risk Metrics", DATA_RETENTION_DAYS)

if __name__ == "__main__":
    # For production, schedule this script to run periodically (e.g., hourly, daily)
    # using a tool like cron or a Python-based scheduler.
    # The frequency of execution determines the granularity of your collected data.
    fetch_and_insert_risk_metrics()
    print("Successfully fetched and inserted risk metrics.")
