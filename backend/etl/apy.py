from blockfrost import BlockFrostApi, ApiError, ApiUrls
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, UTC

load_dotenv()

api = BlockFrostApi(
    project_id=os.getenv("BLOCKFROST_API_KEY"),
    base_url=ApiUrls.mainnet.value,
)

# Policy ID for qADA (Liqwid's qToken for ADA)
QADA_ASSET_POLICY_ID = "a04ce7a52545e5e33c2867e148898d9e667a69602285f6a1298f9d68"

def get_liqwid_lending_pool_addresses(policy_id):
    """Gets all addresses holding a specific Liqwid qToken, which are the lending pools."""
    all_pool_addresses = set()
    try:
        assets = api.assets_policy(policy_id)
        for asset in assets:
            holders = api.asset_addresses(asset.asset)
            for holder in holders:
                all_pool_addresses.add(holder.address)
    except ApiError as e:
        print(f"Error fetching assets for policy {policy_id}: {e}")
    return list(all_pool_addresses)

def fetch_and_insert_liqwid_apy():
    """Calculates and inserts dummy APY for Liqwid lending pools."""
    lending_pool_addresses = get_liqwid_lending_pool_addresses(QADA_ASSET_POLICY_ID)
    if not lending_pool_addresses:
        print("No Liqwid lending pool addresses found for APY calculation. Exiting.")
        return

    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    cursor = conn.cursor()

    for address in lending_pool_addresses:
        try:
            # Simplified APY calculation: Assume a fixed supply and borrow rate
            # In a real scenario, you'd fetch actual supply/borrow amounts and interest rate models
            supply_apy = 0.035 # 3.5% dummy supply APY
            borrow_apy = 0.08 # 8% dummy borrow APY

            # Insert Supply APY
            cursor.execute("""
                INSERT INTO apy_snapshots (protocol_name, protocol_segment, address, pool_name, apy, snapshot_time, data_source, chain)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (protocol_name, protocol_segment, address, snapshot_time) DO NOTHING;
            """, (
                'Liqwid',
                'Lending Pool - Supply',
                address,
                'qADA',
                supply_apy,
                datetime.now(UTC),
                'Estimated',
                'Cardano'
            ))

            # Insert Borrow APY
            cursor.execute("""
                INSERT INTO apy_snapshots (protocol_name, protocol_segment, address, pool_name, apy, snapshot_time, data_source, chain)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (protocol_name, protocol_segment, address, snapshot_time) DO NOTHING;
            """, (
                'Liqwid',
                'Lending Pool - Borrow',
                address,
                'qADA',
                borrow_apy,
                datetime.now(UTC),
                'Estimated',
                'Cardano'
            ))

        except ApiError as e:
            print(f"Error fetching data for address {address} for APY: {e}")

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    fetch_and_insert_liqwid_apy()
    print("Successfully fetched and inserted Liqwid APY data.")