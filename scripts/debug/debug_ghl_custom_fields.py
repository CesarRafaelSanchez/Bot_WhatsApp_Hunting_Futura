import requests
import config

url = 'https://services.leadconnectorhq.com/opportunities/search'
params = {
    'location_id': config.LOCATION_ID,
    'pipeline_id': config.PIPELINE_ID,
    'limit': 5,
}
headers = {
    'Authorization': f'Bearer {config.GHL_TOKEN}',
    'Version': '2021-04-15',
    'Content-Type': 'application/json',
}

resp = requests.get(url, headers=headers, params=params)
print('status', resp.status_code)
try:
    js = resp.json()
except Exception as e:
    print('json error', e)
    print(resp.text)
    raise
print('count', len(js.get('opportunities', [])))
for i, opp in enumerate(js.get('opportunities', []), 1):
    print('OPP', i, opp.get('name'))
    print(' stage', opp.get('pipelineStageId'))
    cf = opp.get('contact', {}).get('customFields', []) + opp.get('customFields', [])
    for field in cf:
        print('  key', field.get('key'), 'id', field.get('id'), 'value', field.get('value'))
    print('-----')
