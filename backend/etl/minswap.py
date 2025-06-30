import requests
from backend.db import get_db_connection

def get_minswap_tvl():
    address = "addr1qy2jt0qpqz2z2z9zx5w4xemekkce7yderz53kjue53lpqv90lkfa9sgrfjuz6uvt4uqtrqhl2kj0a9lnr9ndzutx32gqleeckv"
    url = "https://api.koios.rest/api/v1/address_info"
    res = requests.post(url, json={"_addresses": [address]})
    data = res.json()
    utxos = data[0].get('utxo_set', [])
    total = sum(int(x['value']) for x in utxos if x['value'])
    return total

def get_minswap_total_tvl(addresses):
    url = "https://api.koios.rest/api/v1/address_info"
    resp = requests.post(url, json={"_addresses": addresses})
    data = resp.json()
    total = 0
    for addr in data:
        utxos = addr.get("utxo_set", [])
        total += sum(int(u["value"]) for u in utxos)
    return total

def store_minswap_tvl():
    tvl = get_minswap_tvl()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tvl_snapshots (protocol_name, tvl)
        VALUES (%s, %s)
    """, ("Minswap", tvl))
    print('inserted Minswap %s' %tvl)
    conn.commit()
    cursor.close()
    conn.close()

#store_minswap_tvl()