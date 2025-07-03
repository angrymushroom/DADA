import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, UTC, timedelta
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.db import get_db_connection

load_dotenv()

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

def get_or_create_asset_id(cursor, asset_symbol, asset_name, asset_policy_id=None, asset_fingerprint=None):
    """Gets or creates an asset_id from dim_asset_dm for a given asset."""
    cursor.execute("SELECT asset_id FROM dim_asset_dm WHERE asset_symbol = %s", (asset_symbol,))
    asset_id = cursor.fetchone()
    if asset_id:
        return asset_id[0]
    else:
        cursor.execute("""
            INSERT INTO dim_asset_dm (asset_symbol, asset_name, asset_policy_id, asset_fingerprint)
            VALUES (%s, %s, %s, %s) RETURNING asset_id;
        """, (asset_symbol, asset_name, asset_policy_id, asset_fingerprint))
        return cursor.fetchone()[0]

def fetch_and_insert_liqwid_apy():
    """Calculates and inserts dummy APY for Liqwid lending pools into the new star schema.

    This function also applies data retention based on DATA_RETENTION_DAYS.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    current_timestamp = datetime.now(UTC)
    time_id = get_or_create_time_id(cursor, current_timestamp)
    protocol_id = get_or_create_protocol_id(cursor, 'Liqwid', 'Lending Pool', 'Cardano')
    asset_id = get_or_create_asset_id(cursor, 'ADA', 'Cardano', 'lovelace', '') # Assuming qADA is tied to ADA

    # Simplified APY calculation: Assume a fixed supply and borrow rate
    supply_apy = 0.035 # 3.5% dummy supply APY
    borrow_apy = 0.08 # 8% dummy borrow APY

    # Insert Supply APY
    cursor.execute("""
        INSERT INTO dws_apy_snapshots_dm (protocol_id, asset_id, time_id, pool_name, apy_value, data_source)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (protocol_id, asset_id, time_id, pool_name) DO NOTHING;
    """, (
        protocol_id,
        asset_id,
        time_id,
        'qADA - Supply',
        supply_apy,
        'Estimated'
    ))

    # Insert Borrow APY
    cursor.execute("""
        INSERT INTO dws_apy_snapshots_dm (protocol_id, asset_id, time_id, pool_name, apy_value, data_source)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (protocol_id, asset_id, time_id, pool_name) DO NOTHING;
    """, (
        protocol_id,
        asset_id,
        time_id,
        'qADA - Borrow',
        borrow_apy,
        'Estimated'
    ))

    conn.commit()
    cursor.close()
    conn.close()

    # Apply data retention after new data is inserted
    delete_old_data("dws_apy_snapshots_dm", "Liqwid", DATA_RETENTION_DAYS)

if __name__ == "__main__":
    fetch_and_insert_liqwid_apy()
    print("Successfully fetched and inserted Liqwid APY data.")

if __name__ == "__main__":
    # For production, schedule this script to run periodically (e.g., hourly, daily)
    # using a tool like cron or a Python-based scheduler.
    # The frequency of execution determines the granularity of your collected data.
    fetch_and_insert_liqwid_apy()
    print("Successfully fetched and inserted Liqwid APY data.")
