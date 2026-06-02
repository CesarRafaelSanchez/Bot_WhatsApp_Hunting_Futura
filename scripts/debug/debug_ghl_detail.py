import requests
import json
import config

base = 'https://services.leadconnectorhq.com'
search_url = f'{base}/opportunities/search'
params = {'location_id': config.LOCATION_ID, 'pipeline_id': config.PIPELINE_ID, 'limit': 1}
headers = {'Authorization': f'Bearer {config.GHL_TOKEN}', 'Version': '2021-04-15', 'Content-Type': 'application/json'}
resp = requests.get(search_url, headers=headers, params=params)
js = resp.json()
opp = js['opportunities'][0]
print('search opp id', opp.get('id'))
print('search opp keys', list(opp.keys()))

detail_url = f"{base}/opportunities/{opp.get('id')}"
resp2 = requests.get(detail_url, headers=headers)
print('detail status', resp2.status_code)
try:
    detail = resp2.json()
except Exception as e:
    print('detail json error', e)
    print(resp2.text)
    raise
print('detail keys', list(detail.keys()))
print('detail sample', json.dumps({k: detail.get(k) for k in ['id','name','pipelineStageId','customFields','contact','contactId','formFields']}, indent=2, ensure_ascii=False))
print('detail contact keys', list(detail.get('contact', {}).keys()))
print('detail contact', json.dumps(detail.get('contact', {}), indent=2, ensure_ascii=False))
print('detail customFields', json.dumps(detail.get('customFields', []), indent=2, ensure_ascii=False))
print('detail formFields', json.dumps(detail.get('formFields', []), indent=2, ensure_ascii=False))
