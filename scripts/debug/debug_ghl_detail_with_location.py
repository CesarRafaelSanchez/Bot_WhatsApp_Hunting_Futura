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
print('search opp id', opp.get('id'))
print('search opp keys', list(opp.keys()))

detail_url = f"{base}/opportunities/{opp.get('id')}"
params2 = {'location_id': config.LOCATION_ID}
resp2 = requests.get(detail_url, headers=headers, params=params2)
print('detail status', resp2.status_code)
try:
    detail = resp2.json()
except Exception as e:
    print('detail json error', e)
    print(resp2.text)
    raise
print('detail keys', list(detail.keys()))
print('detail sample', json.dumps({k: detail.get(k) for k in ['id','name','pipelineStageId','customFields','contact','contactId','formFields']}, indent=2, ensure_ascii=False))
print('detail raw', json.dumps(detail, indent=2, ensure_ascii=False))
