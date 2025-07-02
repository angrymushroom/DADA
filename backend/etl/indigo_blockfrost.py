
from blockfrost import BlockFrostApi, ApiError, ApiUrls
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, UTC, timedelta

load_dotenv()

api = BlockFrostApi(
    project_id=os.getenv("BLOCKFROST_API_KEY"),
    base_url=ApiUrls.mainnet.value
)

# Configure data retention (in days) via environment variable
# Set to 0 or comment out to disable retention
DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", 0))

def delete_old_data(protocol_name, retention_days):
    """Deletes data older than retention_days for a given protocol."""
    if retention_days <= 0:
        print(f"Data retention is disabled for {protocol_name}.")
        return

    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    cursor = conn.cursor()
    cutoff_date = datetime.now(UTC) - timedelta(days=retention_days)
    print(f"Deleting {protocol_name} TVL data older than {cutoff_date}...")
    cursor.execute("""
        DELETE FROM tvl_snapshots
        WHERE protocol_name = %s AND snapshot_time < %s;
    """, (protocol_name, cutoff_date))
    deleted_rows = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Deleted {deleted_rows} old rows for {protocol_name}.")

# The asset ID for iUSD (policy_id + asset_name_hex)
IUSD_ASSET = "f66d78b4a3cb3d37afa0ec36461e51ecbde00f26c8f0a68f94b6988069555344"

def get_indigo_cdp_addresses(asset_id):
    """Gets all addresses holding a specific Indigo iAsset, which are the CDPs."""
    try:
        asset_holders = api.asset_addresses(asset=asset_id, count=100) # Get up to 1000 holders
        return [holder.address for holder in asset_holders]
    except ApiError as e:
        print(f"Error fetching asset holders for {asset_id}: {e}")
        return []

def fetch_and_insert_indigo_tvl():
    """Fetches TVL for all Indigo CDPs and inserts it into the database.

    This function also applies data retention based on DATA_RETENTION_DAYS.
    """
    cdp_addresses = get_indigo_cdp_addresses(IUSD_ASSET)
    if not cdp_addresses:
        print("No CDP addresses found. Exiting.")
        return

    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    cursor = conn.cursor()

    for address in cdp_addresses:
        try:
            utxos = api.address_utxos(address)
            for utxo in utxos:
                for amount in utxo.amount:
                    # We are interested in the collateral (ADA, etc.), not the iUSD itself
                    if amount.unit == IUSD_ASSET:
                        continue

                    asset = amount.unit
                    tvl = int(amount.quantity)
                    if asset == 'lovelace':
                        tvl = tvl / 1_000_000  # Convert lovelace to ADA

                    cursor.execute("""
                        INSERT INTO tvl_snapshots (protocol_name, protocol_segment, address, asset, tvl, snapshot_time, data_source, chain)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (protocol_name, protocol_segment, address, snapshot_time) DO NOTHING;
                    """, (
                        'Indigo',
                        'CDP',
                        address,
                        asset,
                        tvl,
                        datetime.now(UTC),
                        'Blockfrost',
                        'Cardano'
                    ))
        except ApiError as e:
            print(f"Error fetching data for address {address}: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    # Apply data retention after new data is inserted
    delete_old_data("Indigo", DATA_RETENTION_DAYS)

if __name__ == "__main__":
    # For production, schedule this script to run periodically (e.g., hourly, daily)
    # using a tool like cron or a Python-based scheduler.
    # The frequency of execution determines the granularity of your collected data.
    fetch_and_insert_indigo_tvl()
    print("Successfully fetched and inserted Indigo TVL data.")

