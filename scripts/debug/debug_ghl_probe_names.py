import requests
import config

base = 'https://services.leadconnectorhq.com'
paths = [
    '/contacts/{id}',
    '/contacts/{id}/customFields',
    '/contacts/{id}/custom-fields',
    '/contacts/{id}/fields',
    '/contacts/{id}/field-definitions',
    '/contacts/{id}/custom_field_definitions',
    '/opportunities/{id}',
    '/opportunities/{id}/customFields',
    '/opportunities/{id}/custom-fields',
    '/opportunities/{id}/fields',
    '/opportunities/{id}/formFields',
    '/opportunities/{id}/relations',
    '/contacts/custom-fields',
    '/contacts/fields',
    '/opportunities/custom-fields',
    '/opportunities/fields',
    '/settings/custom-fields',
    '/settings/contacts/custom-fields',
    '/settings/opportunities/custom-fields',
]
headers = {'Authorization': f'Bearer {config.GHL_TOKEN}', 'Version': '2021-04-15', 'Content-Type': 'application/json'}

# get sample ids
resp = requests.get(base + '/opportunities/search', headers=headers, params={'location_id': config.LOCATION_ID, 'pipeline_id': config.PIPELINE_ID, 'limit': 1})
opp = resp.json()['opportunities'][0]
contact_id = opp['contactId']
opp_id = opp['id']
print('contact_id', contact_id)
print('opp_id', opp_id)
for path in paths:
    url = base + path.format(id=contact_id if 'contact' in path else opp_id)
    try:
        r = requests.get(url, headers=headers)
        print(path, r.status_code, r.text[:500])
    except Exception as e:
        print(path, 'ERROR', e)
    print('---')
