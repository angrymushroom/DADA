
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, UTC, timedelta
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.db import get_db_connection
from blockfrost import BlockFrostApi, ApiError, ApiUrls
from pycoingecko import CoinGeckoAPI

load_dotenv()

api = BlockFrostApi(
    project_id=os.getenv("BLOCKFROST_API_KEY"),
    base_url=ApiUrls.mainnet.value
)

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

# The asset ID for iUSD (policy_id + asset_name_hex)
IUSD_ASSET = "f66d78b4a3cb3d37afa0ec36461e51ecbde00f26c8f0a68f94b6988069555344"

def get_indigo_cdp_addresses(asset_id):
    """Gets all addresses holding a specific Indigo iAsset, which are the CDPs, with pagination."""
    all_pool_addresses = set()
    page = 1
    while True:
        try:
            asset_holders = api.asset_addresses(asset=asset_id, count=100, page=page)
            if not asset_holders:
                break
            for holder in asset_holders:
                all_pool_addresses.add(holder.address)
            page += 1
        except ApiError as e:
            print(f"Error fetching asset holders for {asset_id} (page {page}): {e}")
            break
    return list(all_pool_addresses)

def fetch_and_insert_indigo_tvl():
    """Fetches TVL for all Indigo CDPs and inserts it into the dws_tvl_snapshots_dm table.

    This function also applies data retention based on DATA_RETENTION_DAYS.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cg = CoinGeckoAPI()

    current_timestamp = datetime.now(UTC)
    time_id = get_or_create_time_id(cursor, current_timestamp)
    protocol_id = get_or_create_protocol_id(cursor, 'Indigo', 'CDP', 'Cardano')
    iusd_asset_id_dim = get_or_create_asset_id(cursor, 'IUSD', 'Indigo Protocol iUSD', IUSD_ASSET, '')

    try:
        ada_price_usd = cg.get_price(ids='cardano', vs_currencies='usd')['cardano']['usd']
    except Exception as e:
        print(f"Error fetching ADA price from CoinGecko: {e}")
        ada_price_usd = 0.0 # Fallback to 0 if price cannot be fetched

    cdp_addresses = get_indigo_cdp_addresses(IUSD_ASSET)
    if not cdp_addresses:
        print("No CDP addresses found. Exiting.")
        return

    for address in cdp_addresses:
        try:
            utxos = api.address_utxos(address)
            for utxo in utxos:
                for amount in utxo.amount:
                    # We are interested in the collateral (ADA, etc.), not the iUSD itself
                    if amount.unit == IUSD_ASSET:
                        continue

                    asset_symbol = amount.unit
                    tvl = int(amount.quantity)
                    
                    # Determine asset_id for the collateral asset
                    if asset_symbol == 'lovelace':
                        collateral_asset_id = get_or_create_asset_id(cursor, 'ADA', 'Cardano', 'lovelace', '')
                        tvl_ada = tvl / 1_000_000  # Convert lovelace to ADA
                        tvl_usd = tvl_ada * ada_price_usd # Convert ADA to USD
                    else:
                        # For other assets, we would need their price in USD. For now, we'll use a dummy value or skip.
                        # This part needs further development to fetch prices for other assets.
                        collateral_asset_id = get_or_create_asset_id(cursor, asset_symbol, asset_symbol, asset_symbol, '') # Placeholder
                        tvl_usd = tvl # Placeholder, assuming 1:1 for non-ADA assets for now

                    cursor.execute("""
                        INSERT INTO dws_tvl_snapshots_dm (protocol_id, asset_id, time_id, address, tvl_usd, data_source)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (protocol_id, asset_id, time_id, address) DO NOTHING;
                    """, (
                        protocol_id,
                        collateral_asset_id,
                        time_id,
                        address,
                        tvl_usd,
                        'Blockfrost/CoinGecko'
                    ))
        except ApiError as e:
            print(f"Error fetching data for address {address}: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    # Apply data retention after new data is inserted
    delete_old_data("dws_tvl_snapshots_dm", "Indigo", DATA_RETENTION_DAYS)

if __name__ == "__main__":
    # For production, schedule this script to run periodically (e.g., hourly, daily)
    # using a tool like cron or a Python-based scheduler.
    # The frequency of execution determines the granularity of your collected data.
    fetch_and_insert_indigo_tvl()
    print("Successfully fetched and inserted Indigo TVL data.")

if __name__ == "__main__":
    # For production, schedule this script to run periodically (e.g., hourly, daily)
    # using a tool like cron or a Python-based scheduler.
    # The frequency of execution determines the granularity of your collected data.
    fetch_and_insert_indigo_tvl()
    print("Successfully fetched and inserted Indigo TVL data.")

