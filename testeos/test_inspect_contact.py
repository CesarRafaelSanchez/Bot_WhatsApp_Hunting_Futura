import requests, json, config

url = f'https://services.leadconnectorhq.com/contacts/K1F0eWeO1DUiLARx2swX'
headers = {
    'Authorization': f'Bearer {config.GHL_TOKEN}',
    'Version': '2021-04-15'
}
resp = requests.get(url, headers=headers)
data = resp.json()

# Buscar campos personalizados
if 'contact' in data and 'customFields' in data['contact']:
    print('CUSTOM FIELDS:')
    print('=' * 80)
    for field in data['contact']['customFields']:
        print(f"ID: {field['id']:30s} | VALUE: {field['value']}")
else:
    print('customFields not found. Available keys:')
    if 'contact' in data:
        print(list(data['contact'].keys()))
