# backend/etl/indigo.py

import requests
from backend.db import get_db_connection

def get_indigo_tvl():
    # Replace with the actual Indigo script address
    pool_address = "addr1xyaat796qyq08x2jgunpn2lamdfdjsd9x3acsc67sa98kdacxk92m5cvvr46z6rq3t27sa2e96dhewx8qzp8eh58lx3slsxqwp"
    url = "https://api.koios.rest/api/v1/address_info"
    resp = requests.post(url, json={"_addresses": [pool_address]})
    data = resp.json()
    utxos = data[0].get("utxo_set", [])
    total = sum(int(utxo["value"]) for utxo in utxos if utxo.get("value"))
    return total

def store_indigo_tvl():
    tvl = get_indigo_tvl()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tvl_snapshots (protocol_name, tvl)
        VALUES (%s, %s)
    """, ("indigo", tvl))
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    store_indigo_tvl()
    print("✅ Indigo TVL stored:", get_indigo_tvl())