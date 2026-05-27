import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

OPENWA_BASE_URL = "http://100.112.88.76:2785/api"
#para Mathias seria reemplazar lo anterior por este:
#OPENWA_BASE_URL = "http://100.112.88.76:2785/api"
OPENWA_API_KEY = "owa_k1_948401275d0cfdf81ce18fd0b3faa1d4a08a5d52d7005834a6eea03a03d0bd84"
# Base de datos expandida con Roles
USERS_DB = {
    "51932068040": {"name": "Rafael Sanchez TI", "ghl_id": "PaTMhzFbNbsRTvE3os5o", "role": "TI"},
    "206893205217341": {"name": "Rafael Sanchez TI", "ghl_id": "PaTMhzFbNbsRTvE3os5o", "role": "TI"},
    # Tu LID de prueba
    "51957770680": {"name": "Humberto Benavides", "ghl_id": "qOREYbNFDXYgi4ePmLT6", "role": "CEO"},
    "51934841065": {"name": "Mathias Villena TI", "ghl_id": "51PrMSG3YMKkq0XlKdrY", "role": "TI"}
}

# Oportunidades distribuidas para la simulación
MOCK_GHL_OPPORTUNITIES = [
    {
        "id": "S1oCOFz2USAEo5upP1V3",
        "name": "EDIFICIO CANAVAL 2",
        "assignedTo": "PaTMhzFbNbsRTvE3os5o",
        "status": "open",
        "contact": {"name": "Administración: EDIFICIO CANAVAL 2"}
    },
    {
        "id": "X9zABC123fghI789jKlm",
        "name": "TORRE JAVIER PRADO",
        "assignedTo": "PaTMhzFbNbsRTvE3os5o",
        "status": "open",
        "contact": {"name": "Gerencia: Torre JP"}
    },
    {
        "id": "M01",
        "name": "HUNTING VERTICAL INDUSTRIAL",
        "assignedTo": "51PrMSG3YMKkq0XlKdrY",
        "status": "open",
        "contact": {"name": "Planta Vulcan"}
    },
    {
        "id": "C01",
        "name": "ALIANZA ESTRATÉGICA CORPORATIVA",
        "assignedTo": "qOREYbNFDXYgi4ePmLT6",
        "status": "open",
        "contact": {"name": "Grupo Romero"}
    }
]


def send_whatsapp_message(session_id, chat_id, text):
    url = f"{OPENWA_BASE_URL}/sessions/{session_id}/messages/send-text"
    headers = {"X-API-Key": OPENWA_API_KEY, "Content-Type": "application/json"}
    payload = {"chatId": chat_id, "text": text}
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        print(f"⚠️ Error OpenWA: {e}")
        return None


@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.json
    if not payload or payload.get("event") != "message.received":
        return jsonify({"status": "ignored"}), 200

    session_id = payload.get("sessionId")
    message_data = payload.get("data", {})
    from_jid = message_data.get("from")
    user_input = message_data.get("body", "").strip()

    if not from_jid:
        return jsonify({"status": "no_sender"}), 200

    phone_clean = from_jid.split("@")[0].replace("+", "")
    user = USERS_DB.get(phone_clean)

    if not user:
        reply_text = "⚠️ *Acceso Restringido:* Su número no está autorizado en la red de Hunting de Grupo Futura."
        send_whatsapp_message(session_id, from_jid, reply_text)
        return jsonify({"status": "unauthorized"}), 200

    # LÓGICA DE MENÚ INTERACTIVO
    if user_input == "1":
        # Opción 1: Mis Oportunidades
        my_leads = [op for op in MOCK_GHL_OPPORTUNITIES if op["assignedTo"] == user["ghl_id"]]
        if my_leads:
            reply_text = f"📋 *Oportunidades Asignadas a Vd.*\n\n"
            for idx, lead in enumerate(my_leads, 1):
                reply_text += f"*{idx}. {lead['name']}*\n"
                reply_text += f"   • Cuenta: {lead['contact']['name']}\n"
                reply_text += f"   • Estado: {lead['status'].upper()}\n\n"
        else:
            reply_text = "En este momento no cuenta con oportunidades asignadas en GHL."

        reply_text += "¿Desea algo más? Responda con el número de opción."

    elif user_input == "2":
        # Opción 2: Resumen Ejecutivo (Ideal para el CEO)
        total_leads = len(MOCK_GHL_OPPORTUNITIES)
        reply_text = (
            f"📊 *Resumen Ejecutivo del Pipeline - GHL*\n\n"
            f"• *Total Oportunidades Activas:* {total_leads}\n"
            f"• *Asignadas a Rafael:* 2\n"
            f"• *Asignadas a Mathias:* 1\n"
            f"• *Asignadas a Presidencia:* 1\n\n"
            f"💡 _Datos en tiempo real extraídos del CRM._"
        )

    else:
        # Menú Principal (Si escribe cualquier otra cosa o saludo)
        reply_text = (
            f"Hola *{user['name']}* 👋\n"
            f"Bienvenido al Asistente de Automatización de Hunting.\n\n"
            f"Por favor, seleccione una opción enviando solo el número:\n\n"
            f"*[ 1 ]* Ver mis oportunidades asignadas\n"
            f"*[ 2 ]* Ver resumen ejecutivo del Pipeline (Global)\n"
        )

    send_whatsapp_message(session_id, from_jid, reply_text)
    return jsonify({"status": "processed"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)