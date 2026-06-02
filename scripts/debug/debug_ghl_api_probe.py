import requests
import config

bases = [
    'https://api.leadconnectorhq.com',
    'https://api.leadconnectorhq.com/v1',
    'https://services.leadconnectorhq.com/v1'
]
paths = [
    '/contacts',
    '/contacts/K1F0eWeO1DUiLARx2swX',
    '/contacts/K1F0eWeO1DUiLARx2swX/custom_fields',
    '/contacts/K1F0eWeO1DUiLARx2swX/customFields',
    '/contacts/K1F0eWeO1DUiLARx2swX/fields',
    '/contacts/K1F0eWeO1DUiLARx2swX/field-definitions',
    '/settings/customFields',
    '/settings/contacts/custom-fields',
    '/settings/contacts/customFields',
    '/settings/contact/custom-fields',
]
headers = {
    'Authorization': f'Bearer {config.GHL_TOKEN}',
    'Version': '2021-04-15',
    'Content-Type': 'application/json'
}

for base in bases:
    print('BASE', base)
    for path in paths:
        url = base + path
        try:
            resp = requests.get(url, headers=headers)
            print(url, resp.status_code, resp.text[:250].replace('\n', ' '))
        except Exception as e:
            print(url, 'ERROR', e)
    print('---')
