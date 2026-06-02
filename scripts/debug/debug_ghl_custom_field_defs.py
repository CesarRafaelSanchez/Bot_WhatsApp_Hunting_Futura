import requests
import config

base = 'https://services.leadconnectorhq.com'
urls = [
    '/fields',
    '/custom-fields',
    '/customFields',
    '/custom-fields?type=contact',
    '/custom-fields?type=opportunity',
    '/contacts/custom-fields',
    '/contacts/customFields',
    '/opportunities/custom-fields',
    '/opportunities/customFields',
    '/settings/custom-fields',
    '/settings/customFields',
    '/contacts/fields',
    '/opportunities/fields',
    '/field-definitions',
    '/fields/contact',
    '/fields/opportunity',
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
