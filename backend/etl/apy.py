import requests
from backend.db import get_db_connection

def fetch_minswap_apys():
    r = requests.get("https://api-mainnet-prod.minswap.org/pools")
    pools = r.json()
    return [(p['assetA']['symbol'], p['apy']) for p in pools]

def main():
    conn = get_db_connection()
    cur = conn.cursor()
    for pool_name, apy in fetch_minswap_apys():
        cur.execute(
            "INSERT INTO apy_snapshots (protocol_name, pool_name, apy) VALUES (%s, %s, %s)",
            ("minswap", pool_name, apy)
        )
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
