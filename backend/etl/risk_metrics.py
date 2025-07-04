import os
import sys
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, UTC, timedelta

load_dotenv()

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.db import get_db_connection

# Configure data retention (in days) via environment variable
# Set to 0 or comment out to disable retention
DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", 0))

def delete_old_data(table_name, protocol_name, retention_days):
    """Deletes data older than retention_days for a given protocol from a specified table."""
    if retention_days <= 0:
        print(f"Data retention is disabled for {protocol_name} in {table_name}.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    cutoff_date = datetime.now(UTC) - timedelta(days=retention_days)
    print(f"Deleting {protocol_name} data from {table_name} older than {cutoff_date}...")
    cursor.execute(f"""
        DELETE FROM {table_name}
        WHERE protocol_id IN (
            SELECT protocol_id FROM dim_protocol_dm WHERE protocol_name = %s
        ) AND time_id IN (
            SELECT time_id FROM dim_time_dm WHERE date < %s
        );
    """, (protocol_name, cutoff_date.date()))
    deleted_rows = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Deleted {deleted_rows} old rows for {protocol_name} in {table_name}.")

def get_or_create_time_id(cursor, timestamp):
    """Gets or creates a time_id from dim_time_dm for a given timestamp."""
    date_only = timestamp.date()
    cursor.execute("SELECT time_id FROM dim_time_dm WHERE date = %s", (date_only,))
    time_id = cursor.fetchone()
    if time_id:
        return time_id[0]
    else:
        # Populate dim_time_dm for the date if it doesn't exist
        cursor.execute("SELECT populate_dim_time_dm(%s, %s)", (date_only, date_only))
        cursor.execute("SELECT time_id FROM dim_time_dm WHERE date = %s", (date_only,))
        return cursor.fetchone()[0]

def get_or_create_protocol_id(cursor, protocol_name, protocol_segment, chain):
    """Gets or creates a protocol_id from dim_protocol_dm for a given protocol."""
    cursor.execute("SELECT protocol_id FROM dim_protocol_dm WHERE protocol_name = %s", (protocol_name,))
    protocol_id = cursor.fetchone()
    if protocol_id:
        return protocol_id[0]
    else:
        cursor.execute("""
            INSERT INTO dim_protocol_dm (protocol_name, protocol_segment, chain)
            VALUES (%s, %s, %s) RETURNING protocol_id;
        """, (protocol_name, protocol_segment, chain))
        return cursor.fetchone()[0]


def compute_risk_metrics(protocol_id, protocol_name):
    conn = get_db_connection()
    cur = conn.cursor()

    # TVL volatility
    cur.execute("""
        SELECT stddev(tvl_usd) FROM dws_tvl_snapshots_dm
        WHERE protocol_id = %s AND time_id IN (
            SELECT time_id FROM dim_time_dm WHERE date > now() - interval '7 days'
        )
    """, (protocol_id,))
    tvl_vol = cur.fetchone()[0] or 0.0

    # Whale concentration (based on available dws_top_wallets_dm data)
    top_balance = 0
    total_balance = 0
    whale_pct = 0

    cur.execute("""
        SELECT count(*) FROM dws_top_wallets_dm
        WHERE protocol_id = %s
    """, (protocol_id,))
    if cur.fetchone()[0] > 0: # Only proceed if there's data for the protocol
        cur.execute("""
            SELECT sum(balance_usd) FROM (
                SELECT balance_usd FROM dws_top_wallets_dm
                WHERE protocol_id = %s
                ORDER BY balance_usd DESC
                LIMIT 10
            ) t
        """, (protocol_id,))
        top_balance = cur.fetchone()[0] or 0

        cur.execute("""
            SELECT sum(balance_usd) FROM dws_top_wallets_dm
            WHERE protocol_id = %s
        """, (protocol_id,))
        total_balance = cur.fetchone()[0] or 1

        whale_pct = (top_balance / total_balance) * 100 if total_balance > 0 else 0

    cur.close()
    conn.close()
    return tvl_vol, whale_pct

def fetch_and_insert_risk_metrics():
    protocols = {
        "Minswap": {"segment": "DEX", "chain": "Cardano"},
        "Indigo": {"segment": "CDP", "chain": "Cardano"},
        "Liqwid": {"segment": "Lending Pool", "chain": "Cardano"}
    }

    conn = get_db_connection()
    cur = conn.cursor()

    current_timestamp = datetime.now(UTC)
    time_id = get_or_create_time_id(cur, current_timestamp)

    for protocol_name, details in protocols.items():
        protocol_id = get_or_create_protocol_id(cur, protocol_name, details["segment"], details["chain"])
        
        # Execute SQL transformation to DWS
        with open('sql/etl_transformations/transform_risk_metrics_to_dws.sql', 'r') as f:
            sql_transform = f.read()
        cur.execute(sql_transform, (
            protocol_id, time_id, protocol_id, time_id, protocol_id, time_id, # For TVL volatility
            protocol_id, time_id # For Whale Concentration
        ))

    conn.commit()
    cur.close()
    conn.close()

    # Apply data retention after new data is inserted
    delete_old_data("dws_risk_metrics_dm", "Risk Metrics", DATA_RETENTION_DAYS)

if __name__ == "__main__":
    # For production, schedule this script to run periodically (e.g., hourly, daily)
    # using a tool like cron or a Python-based scheduler.
    # The frequency of execution determines the granularity of your collected data.
    fetch_and_insert_risk_metrics()
    print("Successfully fetched and inserted risk metrics.")

if __name__ == "__main__":
    # For production, schedule this script to run periodically (e.g., hourly, daily)
    # using a tool like cron or a Python-based scheduler.
    # The frequency of execution determines the granularity of your collected data.
    fetch_and_insert_risk_metrics()
    print("Successfully fetched and inserted risk metrics.")
