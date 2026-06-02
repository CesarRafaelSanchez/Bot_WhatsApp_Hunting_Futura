import requests
import base64
import config

def get_chat_id_for_sending(session_id: str, contact_id: str):
    """Resuelve un chatId válido para enviar mensajes, convirtiendo @lid si es necesario."""
    if "@lid" not in contact_id:
        return contact_id

    url = f"{config.OPENWA_BASE_URL}/sessions/{session_id}/contacts/{contact_id}"
    headers = {
        "X-API-Key": config.OPENWA_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code in [200, 201]:
            res_data = response.json()
            raw_id = res_data.get("id", "")
            if isinstance(raw_id, str) and "@" in raw_id:
                return raw_id
    except Exception as e:
        print(f"⚠️ Error al resolver chatId de envío: {e}")

    return contact_id


def split_text_into_chunks(text: str, max_chars: int = 4000):
    """Divide un texto largo en partes seguras para enviar por OpenWA."""
    lines = text.split("\n")
    chunks = []
    current = []
    current_len = 0

    for line in lines:
        line_with_break = line + "\n"
        if current_len + len(line_with_break) > max_chars and current:
            chunks.append("".join(current).rstrip())
            current = [line_with_break]
            current_len = len(line_with_break)
        else:
            current.append(line_with_break)
            current_len += len(line_with_break)

    if current:
        chunks.append("".join(current).rstrip())

    return chunks


def send_whatsapp_message(session_id: str, chat_id: str, text: str):
    """Envía un mensaje de texto a través de la API de OpenWA."""
    chat_id = get_chat_id_for_sending(session_id, chat_id)
    url = f"{config.OPENWA_BASE_URL}/sessions/{session_id}/messages/send-text"
    headers = {
        "X-API-Key": config.OPENWA_API_KEY,
        "Content-Type": "application/json"
    }

    chunks = split_text_into_chunks(text)
    responses = []

    for idx, chunk in enumerate(chunks, start=1):
        chunk_to_send = chunk
        if len(chunks) > 1:
            chunk_to_send = f"{chunk}\n\n({idx}/{len(chunks)})"

        payload = {"chatId": chat_id, "text": chunk_to_send}
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code in [200, 201]:
                responses.append(response.json())
                continue
            print(f"⚠️ OpenWA devolvió código de error: {response.status_code}")
            print(f"⚠️ Request URL: {url}")
            print(f"⚠️ Request payload: {payload}")
            print(f"⚠️ Response body: {response.text}")
            return None
        except Exception as e:
            print(f"⚠️ Error crítico en OpenWA Client: {e}")
            return None

    return responses


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


def send_whatsapp_image(session_id: str, chat_id: str, image_bytes: bytes, caption: str = ""):
    """Convierte los bytes en imagen y los envía a WhatsApp (WAHA)."""
    chat_id = get_chat_id_for_sending(session_id, chat_id)
    url = f"{config.OPENWA_BASE_URL}/sessions/{session_id}/messages/send-image"
    
    headers = {
        "X-API-Key": config.OPENWA_API_KEY,
        "Content-Type": "application/json"
    }

    b64_data = base64.b64encode(image_bytes).decode('utf-8')
    data_uri = f"data:image/jpeg;base64,{b64_data}"

    payload = {
        "chatId": chat_id,
        "file": data_uri,
        "caption": caption
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        print("📤 [OpenWA IMG] Status:", response.status_code)
        print("📤 [OpenWA IMG] Response:", response.text[:500])

        if response.status_code not in [200, 201]:
            return None

        return response.json() if response.text else True

    except Exception as e:
        print(f"⚠️ Error enviando imagen por OpenWA: {e}")
        return None