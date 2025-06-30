import requests

minswap_lp_address = "addr1xyaat796qyq08x2jgunpn2lamdfdjsd9x3acsc67sa98kdacxk92m5cvvr46z6rq3t27sa2e96dhewx8qzp8eh58lx3slsxqwp"
url = "https://api.koios.rest/api/v1/address_info"
res = requests.post(url, json={"_addresses": [minswap_lp_address]})
data = res.json()
print('range is %s' % len(data))
utxos = data[0].get('utxo_set', [])
total = sum(int(x['value']) for x in utxos if x['value'])
print(total)


