import requests

liqwid_lp_address = "addr1zxhew7fmsup08qvhdnkg8ccra88pw7q5trrncja3dlszhq6pr0ayfupfkpyjs0lxpyulnd9wq4ct2zmaz0rg0e8zpjyq7wxle2"
url = "https://api.koios.rest/api/v1/address_info"
res = requests.post(url, json={"_addresses": [liqwid_lp_address]})
data = res.json()
print('range is %s' % len(data))
utxos = data[0].get('utxo_set', [])
total = sum(int(x['value']) for x in utxos if x['value'])
print(total)