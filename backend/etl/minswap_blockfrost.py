
from blockfrost import BlockFrostApi, ApiError, ApiUrls
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, UTC, timedelta
from charli3_dendrite.backend import set_backend
from charli3_dendrite.backend.blockfrost import BlockFrostBackend
from charli3_dendrite.dexs.amm.minswap import MinswapCPPState, MinswapV2CPPState

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

def get_all_minswap_pools():
    """Gets all Minswap pool addresses by querying LP token policies."""
    all_pool_addresses = set()
    
    # Configure the backend for charli3-dendrite
    set_backend(BlockFrostBackend(project_id=os.getenv("BLOCKFROST_API_KEY")))

    # Get LP policy IDs from MinswapCPPState (V1 pools)
    for policy_id in MinswapCPPState.lp_policy():
        try:
            assets = api.assets_policy(policy_id)
            for asset in assets:
                # Get addresses holding this LP token
                holders = api.asset_addresses(asset.asset)
                for holder in holders:
                    all_pool_addresses.add(holder.address)
        except ApiError as e:
            print(f"Error fetching assets for policy {policy_id}: {e}")

    # Get LP policy IDs from MinswapV2CPPState (V2 pools)
    for policy_id in MinswapV2CPPState.lp_policy():
        try:
            assets = api.assets_policy(policy_id)
            for asset in assets:
                # Get addresses holding this LP token
                holders = api.asset_addresses(asset.asset)
                for holder in holders:
                    all_pool_addresses.add(holder.address)
        except ApiError as e:
            print(f"Error fetching assets for policy {policy_id}: {e}")

    return list(all_pool_addresses)

def fetch_and_insert_all_pools_tvl():
    """Fetches TVL for all Minswap pools and inserts it into the database.
    
    This function also applies data retention based on DATA_RETENTION_DAYS.
    """
    pool_addresses = get_all_minswap_pools()
    if not pool_addresses:
        print("No Minswap pool addresses found. Exiting.")
        return

    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    cursor = conn.cursor()

    for address in pool_addresses:
        try:
            utxos = api.address_utxos(address)
            for utxo in utxos:
                for amount in utxo.amount:
                    asset = amount.unit
                    tvl = int(amount.quantity)
                    if asset == 'lovelace':
                        tvl = tvl / 1_000_000 # Convert lovelace to ADA

                    cursor.execute("""
                        INSERT INTO tvl_snapshots (protocol_name, protocol_segment, address, asset, tvl, snapshot_time, data_source, chain)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (protocol_name, protocol_segment, address, snapshot_time) DO NOTHING;
                    """, (
                        'Minswap',
                        'DEX',
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
    delete_old_data("Minswap", DATA_RETENTION_DAYS)

if __name__ == "__main__":
    # For production, schedule this script to run periodically (e.g., hourly, daily)
    # using a tool like cron or a Python-based scheduler.
    # The frequency of execution determines the granularity of your collected data.
    fetch_and_insert_all_pools_tvl()
    print("Successfully fetched and inserted Minswap TVL data.")

