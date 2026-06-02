import requests
import config

contact_id = 'K1F0eWeO1DUiLARx2swX'
url = f'https://services.leadconnectorhq.com/contacts/{contact_id}'
headers = {'Authorization': f'Bearer {config.GHL_TOKEN}'}

resp = requests.get(url, headers=headers)
contact = resp.json()['contact']

print('TODOS LOS CUSTOM FIELDS:')
print('=' * 80)
if 'customFields' in contact:
    for field in contact['customFields']:
        field_id = field['id']
        field_value = field['value']
        print(f"ID: {field_id:30s} | VALUE: {field_value}")
