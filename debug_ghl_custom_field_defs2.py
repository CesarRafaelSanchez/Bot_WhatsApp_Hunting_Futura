import requests
import config

base = 'https://api.leadconnectorhq.com'
urls = [
    '/custom-fields',
    '/contacts/custom-fields',
    '/contacts/customFields',
    '/contacts/fields',
    '/opportunities/custom-fields',
    '/opportunities/fields',
    '/settings/custom-fields',
    '/settings/customFields',
    '/field-definitions',
    '/fields/contact',
    '/fields/opportunity',
    '/forms',
    '/form',
    '/forms/definitions',
]
headers = {
    'Authorization': f'Bearer {config.GHL_TOKEN}',
    'Version': '2021-04-15',
    'Content-Type': 'application/json',
}
for path in urls:
    url = base + path
    try:
        resp = requests.get(url, headers=headers)
        print(path, resp.status_code)
        text = resp.text
        if len(text) > 1000:
            text = text[:1000] + '...'
        print(text)
    except Exception as e:
        print(path, 'ERROR', e)
    print('---')
