from flask import Flask, request, jsonify
from bot import router
from services import openwa_client
from database import users_model

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.json

    # Validar que el webhook contenga el evento correcto
    if not payload or payload.get("event") != "message.received":
        return jsonify({"status": "ignored"}), 200

    session_id = payload.get("sessionId")
    message_data = payload.get("data", {})
    from_jid = message_data.get("from")
    user_input = message_data.get("body", "").strip()

    if not from_jid:
        return jsonify({"status": "no_sender"}), 200

    # Limpieza del formato del número (remueve @c.us o prefijos del JID de WhatsApp)
    phone_clean = from_jid.split("@")[0].replace("+", "")

    print(f"📞 [DEBUG] Teléfono limpio recibido de WhatsApp: '{phone_clean}'")

    # Interceptar tráfico enviando la data completa para auto-indexado seguro
    reply_text = router.procesar_flujo_bot(session_id, phone_clean, user_input, message_data)

    # UX SOLUCIÓN ERROR 400: Si el origen es @lid, forzamos el envío al número real @c.us autorizado en DB
    target_jid = from_jid
    if "@lid" in from_jid:
        user = users_model.get_user_by_identifier(phone_clean)
        if user and user.get("phone"):
            target_jid = f"{user['phone']}@c.us"

    # Enviar el mensaje formateado de vuelta a OpenWA de forma segura
    openwa_client.send_whatsapp_message(session_id, target_jid, reply_text)
    print(message_data)

    return jsonify({"status": "processed"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)