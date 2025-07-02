
from blockfrost import BlockFrostApi, ApiError, ApiUrls
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, UTC
from charli3_dendrite.backend import set_backend
from charli3_dendrite.backend.blockfrost import BlockFrostBackend
from charli3_dendrite.dexs.amm.minswap import MinswapCPPState, MinswapV2CPPState

load_dotenv()

api = BlockFrostApi(
    project_id=os.getenv("BLOCKFROST_API_KEY"),
    base_url=ApiUrls.mainnet.value
)

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
    """Fetches TVL for all Minswap pools and inserts it into the database."""
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

if __name__ == "__main__":
    fetch_and_insert_all_pools_tvl()
    print("Successfully fetched and inserted Minswap TVL data.")

