import requests

url = "https://bot.novacoresac.com/crm-notificaciones"
payload = {
    "opportunity_name": "NEO LLOQUE",
    "pipleline_stage": "En Habilitación Técnica",
    "user": {
        "firstName": "Jean Pierre Sihue Silva",
        "lastName": "Hunter",
        "email": "j.sihue@futurapro.pe",
        "phone": "+51918371086"
    }
}

print("Enviando webhook de prueba GHL...")
response = requests.post(url, json=payload)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
