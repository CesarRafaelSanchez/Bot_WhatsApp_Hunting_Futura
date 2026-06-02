import requests
import json
import config

base = 'https://services.leadconnectorhq.com'
search_url = f'{base}/opportunities/search'
headers = {'Authorization': f'Bearer {config.GHL_TOKEN}', 'Version': '2021-04-15', 'Content-Type': 'application/json'}
params = {'location_id': config.LOCATION_ID, 'pipeline_id': config.PIPELINE_ID, 'limit': 1}
resp = requests.get(search_url, headers=headers, params=params)
js = resp.json()
opp = js['opportunities'][0]
contact_id = opp.get('contactId') or opp.get('contact', {}).get('id')
print('contact_id', contact_id)
contact_url = f'{base}/contacts/{contact_id}'
resp2 = requests.get(contact_url, headers=headers, params={'location_id': config.LOCATION_ID})
print('contact status', resp2.status_code)
print(resp2.text)
