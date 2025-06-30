import requests
from backend.db import get_db_connection

def fetch_prices():
    r = requests.get("https://api-mainnet-prod.minswap.org/pools")
    pools = r.json()
    # Map token -> price
    prices = {}
    for p in pools:
        symbol = p['assetA']['symbol']
        price = float(p['price'])
        prices[symbol] = price
    return prices

def main():
    conn = get_db_connection()
    cur = conn.cursor()
    prices = fetch_prices()
    for symbol, price in prices.items():
        cur.execute(
            "INSERT INTO token_prices (token_symbol, price_usd) VALUES (%s, %s)",
            (symbol, price)
        )
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
