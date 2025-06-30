import requests
from backend.db import get_db_connection

def fetch_top_holders(policy_id):
    r = requests.post("https://api.koios.rest/api/v1/asset_addresses", json={"_asset_policy": policy_id})
    addresses = r.json()
    # Sort by quantity
    top = sorted(addresses, key=lambda x: int(x['quantity']), reverse=True)[:10]
    return top

def main():
    protocol = "minswap"
    policy_id = "addr1qy2jt0qpqz2z2z9zx5w4xemekkce7yderz53kjue53lpqv90lkfa9sgrfjuz6uvt4uqtrqhl2kj0a9lnr9ndzutx32gqleeckv"  # Fill in
    conn = get_db_connection()
    cur = conn.cursor()
    for holder in fetch_top_holders(policy_id):
        cur.execute(
            "INSERT INTO top_wallets (protocol_name, wallet_address, balance) VALUES (%s, %s, %s)",
            (protocol, holder['address'], holder['quantity'])
        )
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
