import json
import requests
import config

url = 'https://services.leadconnectorhq.com/opportunities/search'
params = {
    'location_id': config.LOCATION_ID,
    'pipeline_id': config.PIPELINE_ID,
    'limit': 1,
}
headers = {
    'Authorization': f'Bearer {config.GHL_TOKEN}',
    'Version': '2021-04-15',
    'Content-Type': 'application/json',
}

resp = requests.get(url, headers=headers, params=params)
print('status', resp.status_code)
js = resp.json()
opp = js['opportunities'][0]
print('opp keys:', list(opp.keys()))
print('contact keys:', list(opp.get('contact', {}).keys()))
print('contact:', json.dumps(opp.get('contact', {}), indent=2, ensure_ascii=False))
print('customFields:', json.dumps(opp.get('customFields', []), indent=2, ensure_ascii=False))
print('contact customFields:', json.dumps(opp.get('contact', {}).get('customFields', []), indent=2, ensure_ascii=False))
print('formFields:', json.dumps(opp.get('formFields', []), indent=2, ensure_ascii=False))
print('custom_field_items:', [ (f.get('key'), f.get('id'), f.get('value')) for f in opp.get('customFields', []) ])
