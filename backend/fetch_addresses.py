import requests
import yaml

def fetch_minswap_addresses():
    url = "https://api-mainnet-prod.minswap.org/pools"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    addresses = [p["poolAddress"] for p in data["data"]]
    return addresses

def save_to_yaml(addresses, filename="config/protocol_addresses.yaml"):
    cfg = {
        "protocols": {
            "minswap": addresses,
            "indigo": [],
            "liqwid": []
        }
    }
    with open(filename, "w") as f:
        yaml.dump(cfg, f)
    print(f"✅ Saved {len(addresses)} Minswap addresses to {filename}")

def main():
    print("🔄 Fetching Minswap pool addresses...")
    addresses = fetch_minswap_addresses()
    for addr in addresses:
        print("-", addr)
    save_to_yaml(addresses)

if __name__ == "__main__":
    main()
