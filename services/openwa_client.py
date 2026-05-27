import requests
import config

def send_whatsapp_message(session_id: str, chat_id: str, text: str):
    """Envía un mensaje de texto a través de la API de OpenWA."""
    url = f"{config.OPENWA_BASE_URL}/sessions/{session_id}/messages/send-text"
    headers = {
        "X-API-Key": config.OPENWA_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"chatId": chat_id, "text": text}
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return response.json()
        print(f"⚠️ OpenWA devolvió código de error: {response.status_code}")
        return None
    except Exception as e:
        print(f"⚠️ Error crítico en OpenWA Client: {e}")
        return None


def get_contact_phone(session_id: str, contact_id: str):
    """Consulta a la API de OpenWA y extrae el celular real desde el campo 'id'."""
    full_id = contact_id if "@" in contact_id else f"{contact_id}@lid"
    url = f"{config.OPENWA_BASE_URL}/sessions/{session_id}/contacts/{full_id}"

    headers = {
        "X-API-Key": config.OPENWA_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code in [200, 201]:
            res_data = response.json()

            # Extraemos directamente del campo 'id' y limpiamos el sufijo @c.us
            raw_id = res_data.get("id", "")
            if isinstance(raw_id, str) and "@" in raw_id:
                return raw_id.split("@")[0]

        return None
    except Exception as e:
        print(f"⚠️ Error al consultar contacto en OpenWA: {e}")
        return None