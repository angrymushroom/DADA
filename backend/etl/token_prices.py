from blockfrost import BlockFrostApi, ApiError, ApiUrls
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, UTC

load_dotenv()

api = BlockFrostApi(
    project_id=os.getenv("BLOCKFROST_API_KEY"),
    base_url=ApiUrls.mainnet.value
)

# Define common tokens and their policy_id + asset_name_hex
# For ADA, asset is 'lovelace'
COMMON_TOKENS = {
    "ADA": "lovelace",
    "MIN": "29d222ce763455e3d7a09a665ce554f00ac89d2e99a1a83d267170c64d494e4d494e", # Minswap Token
    "iUSD": "f66d78b4a3cb3d37afa0ec36461e51ecbde00f26c8f0a68f94b6988069555344", # Indigo iUSD
    "LQ": "da8c30857834c6ae7203935b89278c532b3995245295456f993e1d244c51", # Liqwid LQ Token
}

def fetch_and_insert_token_prices():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    cursor = conn.cursor()

    for symbol, asset_id in COMMON_TOKENS.items():
        try:
            if asset_id == "lovelace":
                # For ADA, we'll use a dummy price for now. Real price would come from an oracle.
                price_usd = 0.35 # Dummy price for ADA
                token_address = ""
            else:
                # For other tokens, fetch asset info to get policy_id and asset_name
                asset_info = api.asset(asset_id)
                token_address = asset_info.policy_id + asset_info.asset_name
                # Dummy price for other tokens. Real price would come from an oracle.
                price_usd = 1.0 # Dummy price for other tokens

            cursor.execute("""
                INSERT INTO token_prices (token_symbol, token_address, price_usd, snapshot_time, data_source, chain)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (token_symbol, token_address, snapshot_time) DO NOTHING;
            """, (
                symbol,
                token_address,
                price_usd,
                datetime.now(UTC),
                'Blockfrost/Manual',
                'Cardano'
            ))
        except ApiError as e:
            print(f"Error fetching data for token {symbol} ({asset_id}): {e}")

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    fetch_and_insert_token_prices()
    print("Successfully fetched and inserted token prices.")
