# backend/etl/liqwid.py
import requests
from backend.db import get_db_connection

def get_liqwid_tvl():
    # Known LQ–ADA pool address from GeckoTerminal
    pool_address = "addr1zxhew7fmsup08qvhdnkg8ccra88pw7q5trrncja3dlszhq6pr0ayfupfkpyjs0lxpyulnd9wq4ct2zmaz0rg0e8zpjyq7wxle2"  # replace with exact pool script address
    url = "https://api.koios.rest/api/v1/address_info"
    resp = requests.post(url, json={"_addresses": [pool_address]})
    data = resp.json()
    utxos = data[0].get("utxo_set", [])
    total = sum(int(utxo["value"]) for utxo in utxos if utxo.get("value"))
    return total

def store_liqwid_tvl():
    tvl = get_liqwid_tvl()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tvl_snapshots (protocol_name, tvl)
        VALUES (%s, %s)
    """, ("liqwid", tvl))
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    store_liqwid_tvl()
    print("✅ Liqwid TVL stored:", get_liqwid_tvl())

