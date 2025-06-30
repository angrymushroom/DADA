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

POOL_ADDRESS = "addr1xyaat796qyq08x2jgunpn2lamdfdjsd9x3acsc67sa98kdacxk92m5cvvr46z6rq3t27sa2e96dhewx8qzp8eh58lx3slsxqwp"

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
        'indigo',
        ada_amount,
        datetime.utcnow()
    ))
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    ada = fetch_pool_balance()
    print(f"Indigo ADA TVL: {ada}")
    insert_tvl(ada)
