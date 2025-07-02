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

# Temporary hardcoded Liqwid pool addresses for testing
LIQWID_POOL_ADDRESSES = [
    "addr1zxhew7fmsup08qvhdnkg8ccra88pw7q5trrncja3dlszhq6pr0ayfupfkpyjs0lxpyulnd9wq4ct2zmaz0rg0e8zpjyq7wxle2", # Existing address
    "addr1z8p79rpkcdz8x9d6tft0x0dx5mwuzac2sa4gm8cvkw5hcn8dxhcxap54sz6a9x970gzmgkvnchja2wc4pkpq5kn9xfeslms4pf", # Example: Liqwid ADA pool (might need to verify this is a real Liqwid pool)
    "addr1w8snz7c4974vzdpxu65ruphl3zjdvtxw8strf2c2tmqnxzgusf9xw" # Example: Liqwid USDC pool (might need to verify this is a real Liqwid pool)
]

def fetch_and_insert_liqwid_tvl():
    """Fetches TVL for hardcoded Liqwid pools and inserts it into the database."""
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    cursor = conn.cursor()

    for address in LIQWID_POOL_ADDRESSES:
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
                        'Liqwid',
                        'Lending Pool',
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
    fetch_and_insert_liqwid_tvl()
    print("Successfully fetched and inserted Liqwid TVL data.")
