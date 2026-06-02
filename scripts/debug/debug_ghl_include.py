import requests
import json
import config

base = 'https://services.leadconnectorhq.com'
search_url = f'{base}/opportunities/search'
headers = {'Authorization': f'Bearer {config.GHL_TOKEN}', 'Version': '2021-04-15', 'Content-Type': 'application/json'}

for include in [None, 'customFields', 'formFields', 'contact.customFields', 'customFields,formFields', 'include=contact.customFields', 'include=customFields,formFields,contact']:
    params = {'location_id': config.LOCATION_ID, 'pipeline_id': config.PIPELINE_ID, 'limit': 1}
    if include:
        params['include'] = include
    resp = requests.get(search_url, headers=headers, params=params)
    print('include=', include, 'status', resp.status_code)
    js = resp.json()
    opp = js['opportunities'][0]
    print('opp keys', list(opp.keys()))
    print('customFields len', len(opp.get('customFields', [])))
    print('contact keys', list(opp.get('contact', {}).keys()))
    print('contact customFields len', len(opp.get('contact', {}).get('customFields', [])))
    print('formFields len', len(opp.get('formFields', [])))
    print('---')
