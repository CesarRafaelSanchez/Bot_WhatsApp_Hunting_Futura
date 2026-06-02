import requests
import json
import config

headers = {
    'Authorization': f'Bearer {config.GHL_TOKEN}',
    'Version': '2021-04-15',
    'Content-Type': 'application/json'
}

contact_id = 'K1F0eWeO1DUiLARx2swX'
url = f'https://services.leadconnectorhq.com/contacts/{contact_id}'
resp = requests.get(url, headers=headers)
print('status', resp.status_code)
try:
    data = resp.json()
except Exception as e:
    print('json error', e)
    print(resp.text)
    raise
print('top keys', list(data.keys()))
contact = data.get('contact', {})
print('contact keys', list(contact.keys()))
print('contact sample', json.dumps({k: contact.get(k) for k in ['id','name','customFields','email','phone','tags']}, indent=2, ensure_ascii=False))
print('customFields', json.dumps(contact.get('customFields', []), indent=2, ensure_ascii=False))
