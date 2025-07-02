from blockfrost import BlockFrostApi, ApiError, ApiUrls
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, UTC

load_dotenv()

api = BlockFrostApi(
    project_id=os.getenv("BLOCKFROST_API_KEY"),
    base_url=ApiUrls.mainnet.value
)

# Define assets for which to fetch top holders
# For ADA, asset is 'lovelace'
ASSETS_TO_TRACK = {
    "iUSD": "f66d78b4a3cb3d37afa0ec36461e51ecbde00f26c8f0a68f94b6988069555344", # Indigo iUSD
}

def fetch_and_insert_top_wallets():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    cursor = conn.cursor()

    for token_symbol, asset_id in ASSETS_TO_TRACK.items():
        try:
            # Blockfrost's asset_addresses endpoint returns addresses holding a specific asset
            # We can limit the count to get top holders (though Blockfrost doesn't sort by quantity)
            # For a true "top" list, we might need to fetch more and sort locally or use a different API
            asset_holders = api.asset_addresses(asset=asset_id, count=10) # Fetch top 10 holders

            for holder in asset_holders:
                wallet_address = holder.address
                balance = int(holder.quantity)
                
                # Convert lovelace to ADA for display
                if asset_id == 'lovelace':
                    balance = balance / 1_000_000

                cursor.execute("""
                    INSERT INTO top_wallets (protocol_name, protocol_segment, wallet_address, balance, snapshot_time, data_source, chain)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (protocol_name, protocol_segment, wallet_address, snapshot_time) DO NOTHING;
                """, (
                    token_symbol, # Using token_symbol as protocol_name for simplicity here
                    'Wallet',
                    wallet_address,
                    balance,
                    datetime.now(UTC),
                    'Blockfrost',
                    'Cardano'
                ))
        except ApiError as e:
            print(f"Error fetching top wallets for {token_symbol} ({asset_id}): {e}")

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    fetch_and_insert_top_wallets()
    print("Successfully fetched and inserted top wallet data.")
