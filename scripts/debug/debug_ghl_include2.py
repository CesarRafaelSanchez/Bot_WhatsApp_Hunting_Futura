import requests
import config

base = 'https://services.leadconnectorhq.com'
search_url = f'{base}/opportunities/search'
headers = {'Authorization': f'Bearer {config.GHL_TOKEN}', 'Version': '2021-04-15', 'Content-Type': 'application/json'}

candidates = [
    ('include', 'contact'),
    ('include', 'customFields'),
    ('include', 'formFields'),
    ('include', 'contact,customFields'),
    ('include', 'contact,formFields'),
    ('include[]', 'contact'),
    ('include[]', 'customFields'),
    ('include[]', 'formFields'),
    ('include[]', 'contact'),
    ('include[]', 'customFields'),
    ('include[]', 'contact,customFields'),
    ('include[]', 'contact,formFields'),
]
for key, value in candidates:
    params = {'location_id': config.LOCATION_ID, 'pipeline_id': config.PIPELINE_ID, 'limit': 1, key: value}
    resp = requests.get(search_url, headers=headers, params=params)
    print(key, value, resp.status_code)
    text = resp.text
    if len(text) > 200:
        text = text[:200] + '...'
    print(text)
    print('---')
