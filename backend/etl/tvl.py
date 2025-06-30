import requests
from backend.db import get_db_connection

def fetch_minswap_tvl():
    r = requests.get("https://api-mainnet-prod.minswap.org/pools")
    pools = r.json()
    total_tvl = sum(float(p['tvl']['usd']) for p in pools)
    return total_tvl

def main():
    tvl = fetch_minswap_tvl()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tvl_snapshots (protocol_name, tvl) VALUES (%s, %s)",
        ("minswap", tvl)
    )
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
