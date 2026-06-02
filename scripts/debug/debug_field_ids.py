import requests
import config
import json

headers = {
    'Authorization': f'Bearer {config.GHL_TOKEN}',
    'Version': '2021-04-15',
    'Content-Type': 'application/json'
}

print("Obteniendo la lista maestra de Custom Fields de la cuenta...")
url = f"https://services.leadconnectorhq.com/locations/{config.LOCATION_ID}/customFields"

response = requests.get(url, headers=headers)
if response.status_code == 200:
    custom_fields = response.json().get("customFields", [])
    print("\n🔍 BUSCANDO CAMPOS RELACIONADOS A FOTOS/EDIFICIOS:")
    print("=" * 80)
    for field in custom_fields:
        name = field.get("name", "").lower()
        if "foto" in name or "edificio" in name or "imagen" in name or "file" in name or "archivo" in name or "subir" in name:
            print(f"🔥 ENCONTRADO -> ID: {field.get('id'):25} | NOMBRE: {field.get('name')}")
else:
    print(f"⚠️ Error al obtener campos: {response.status_code}")
    print(response.text)
