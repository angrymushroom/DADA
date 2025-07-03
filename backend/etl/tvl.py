import requests
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, UTC, timedelta
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.db import get_db_connection
from pycoingecko import CoinGeckoAPI

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

def fetch_minswap_tvl():
    r = requests.get("https://api.llama.fi/tvl/minswap")
    r.raise_for_status() # Raise an exception for HTTP errors
    total_tvl = r.json()
    return total_tvl



def fetch_and_insert_all_tvl():
    conn = get_db_connection()
    cursor = conn.cursor()

    current_timestamp = datetime.now(UTC)
    time_id = get_or_create_time_id(cursor, current_timestamp)

    protocols = {
        "Minswap": {"llama_id": "minswap", "segment": "DEX", "chain": "Cardano"},
        "Indigo": {"llama_id": "", "segment": "CDP", "chain": "Cardano"}, # Placeholder for now
        "Liqwid": {"llama_id": "", "segment": "Lending Pool", "chain": "Cardano"} # Placeholder for now
    }

    for protocol_name, details in protocols.items():
        protocol_id = get_or_create_protocol_id(cursor, protocol_name, details["segment"], details["chain"])
        
        try:
            if details["llama_id"]:
                r = requests.get(f"https://api.llama.fi/tvl/{details['llama_id']}")
                r.raise_for_status()
                total_tvl = r.json()
                data_source = 'DefiLlama'
            else:
                total_tvl = 0.0 # Placeholder TVL
                data_source = 'Manual'

            cursor.execute("""
                INSERT INTO dws_tvl_snapshots_dm (protocol_id, time_id, address, tvl_usd, data_source)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (protocol_id, time_id, address) DO NOTHING;
            """, (
                protocol_id,
                time_id,
                'Overall',
                total_tvl,
                data_source
            ))
            delete_old_data("dws_tvl_snapshots_dm", protocol_name, DATA_RETENTION_DAYS)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching TVL for {protocol_name} from DefiLlama: {e}")

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    fetch_and_insert_all_tvl()
    print("Successfully fetched and inserted all TVL data.")
