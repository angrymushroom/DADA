import requests

minswap_lp_address = "addr1qy2jt0qpqz2z2z9zx5w4xemekkce7yderz53kjue53lpqv90lkfa9sgrfjuz6uvt4uqtrqhl2kj0a9lnr9ndzutx32gqleeckv"
url = "https://api.koios.rest/api/v1/address_info"
res = requests.post(url, json={"_addresses": [minswap_lp_address]})
data = res.json()
print('range is %s' % len(data))
utxos = data[0].get('utxo_set', [])
total = sum(int(x['value']) for x in utxos if x['value'])
print(total)