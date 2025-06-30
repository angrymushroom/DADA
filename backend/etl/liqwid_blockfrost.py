from blockfrost import BlockFrostApi, ApiError, ApiUrls
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

api = BlockFrostApi(
    project_id=os.getenv("BLOCKFROST_API_KEY"),
    base_url=ApiUrls.mainnet.value,
)

POOL_ADDRESS = "addr1zxhew7fmsup08qvhdnkg8ccra88pw7q5trrncja3dlszhq6pr0ayfupfkpyjs0lxpyulnd9wq4ct2zmaz0rg0e8zpjyq7wxle2"

def fetch_pool_balance():
    utxos = api.address_utxos(POOL_ADDRESS)
    total_lovelace = 0
    for utxo in utxos:
        for amount in utxo.amount:
            if amount.unit == 'lovelace':
                total_lovelace += int(amount.quantity)
    ada = total_lovelace / 1_000_000
    return ada

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
        'liqwid',
        ada_amount,
        datetime.utcnow()
    ))
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    ada = fetch_pool_balance()
    print(f"Liqwid ADA TVL: {ada}")
    insert_tvl(ada)
