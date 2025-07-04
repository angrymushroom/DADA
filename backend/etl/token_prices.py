import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, UTC, timedelta
from pycoingecko import CoinGeckoAPI
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

# Define common tokens and their CoinGecko API IDs
COMMON_TOKENS = {
    "ADA": "cardano",
    "MIN": "minswap",
    "INDY": "indigo-dao-governance-token",
    "LQ": "liqwid-finance",
    "IUSD": "iusd",
}

# Map CoinGecko IDs to their respective policy_id + asset_name_hex for token_address
# This is a simplified mapping and might need more robust handling for complex cases
TOKEN_ADDRESS_MAP = {
    "minswap": {"policy_id": "29d222ce763455e3d7a09a665ce554f00ac89d2e99a1a83d267170c6", "asset_name": "4d494e"},
    "liqwid-finance": {"policy_id": "da8c30857834c6ae7203935b89278c532b3995245295456f993e1d24", "asset_name": "4c51"},
    "iusd": {"policy_id": "f66d78b4a3cb3d37afa0ec36461e51ecbde00f26c8f0a68f94b69880", "asset_name": "69555344"},
}

def fetch_and_insert_token_prices():
    conn = get_db_connection()
    cursor = conn.cursor()
    cg = CoinGeckoAPI()

    current_timestamp = datetime.now(UTC)
    time_id = get_or_create_time_id(cursor, current_timestamp)

    try:
        coingecko_ids = list(COMMON_TOKENS.values())
        prices = cg.get_price(ids=coingecko_ids, vs_currencies='usd')

        for token_symbol, coingecko_id in COMMON_TOKENS.items():
            if coingecko_id in prices:
                price_usd = prices[coingecko_id]['usd']
                
                # Insert into ODS table
                cursor.execute("""
                    INSERT INTO ods_coingecko_prices_hm (coingecko_id, price_usd, timestamp)
                    VALUES (%s, %s, %s);
                """, (
                    coingecko_id,
                    price_usd,
                    current_timestamp
                ))

        conn.commit()

        # Execute SQL transformation to DWS
        with open('sql/etl_transformations/transform_token_prices_to_dws.sql', 'r') as f:
            sql_transform = f.read()
        cursor.execute(sql_transform)

    except Exception as e:
        print(f"Error fetching prices from CoinGecko or transforming data: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    # Apply data retention after new data is inserted
    # Note: For dim tables, retention is usually not applied or handled differently.
    # For ods_coingecko_prices_hm, you might want a separate retention policy (e.g., truncate daily/weekly).
    # For dws_token_prices_dm, we apply retention based on time_id.
    delete_old_data("dws_token_prices_dm", "Token Prices", DATA_RETENTION_DAYS)

if __name__ == "__main__":
    fetch_and_insert_token_prices()
    print("Successfully fetched and inserted token prices.")