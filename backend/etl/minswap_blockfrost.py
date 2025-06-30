from blockfrost import BlockFrostApi, ApiError, ApiUrls
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

api = BlockFrostApi(
    project_id=os.getenv("BLOCKFROST_API_KEY"),
    base_url=ApiUrls.mainnet.value
)

POOL_ADDRESS = "addr1qy2jt0qpqz2z2z9zx5w4xemekkce7yderz53kjue53lpqv90lkfa9sgrfjuz6uvt4uqtrqhl2kj0a9lnr9ndzutx32gqleeckv"

def fetch_pool_balance():
    utxos = api.address_utxos(POOL_ADDRESS)
    total_lovelace = 0
    asset_balances = {}

    for utxo in utxos:
        for amount in utxo.amount:
            if amount.unit == 'lovelace':
                total_lovelace += int(amount.quantity)
            else:
                unit = amount.unit
                qty = int(amount.quantity)
                if unit not in asset_balances:
                    asset_balances[unit] = 0
                asset_balances[unit] += qty

    # For now, just return ADA
    ada = total_lovelace / 1_000_000
    return ada, asset_balances

def insert_tvl(ada_amount):
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tvl_snapshots (protocol_name, tvl, snapshot_time)
        VALUES (%s, %s, %s)
    """, (
        'minswap',
        ada_amount,
        datetime.utcnow()
    ))
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    ada, tokens = fetch_pool_balance()
    print(f"Total ADA in pool: {ada}")
    print(f"Other tokens: {tokens}")
    insert_tvl(ada)
