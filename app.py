from flask import Flask, request, jsonify
from bot import router
from services import openwa_client
from database import users_model

app = Flask(__name__)

# Caché en memoria para deduplicar webhooks repetidos por timeouts (WAHA/OpenWA retries)
PROCESSED_MESSAGE_IDS = set()
PROCESSED_MESSAGE_IDS_LIST = []
MAX_CACHE_SIZE = 200

# Diccionario de Etapas de GHL para Notificaciones
STAGE_NAMES = {
    "4d5d6906-d70f-466a-9b9b-0acf0a203138": "Edificio Prospectado",
    "d8481911-0c96-4a53-a246-3f43170a6d24": "Prospecto Aceptado",
    "164e9a2c-2ab8-4bd1-91b9-c2c3aa2dd85d": "Pendiente Envió de Formulario de Asignación",
    "9a80e73d-3400-4a97-95f8-69daf0022903": "Formulario de Asignación/Reasignación Completado",
    "76f257d1-73b2-46a5-86f6-0b83fc59b716": "Validación Back Office",
    "24d7f973-ff62-4e0a-8b38-2585b53cc3b1": "Solicitud de Asignación/Reasignacion Enviada a WIN",
    "fdc27149-b398-4ed7-9271-946c66dc9f0f": "Esperando Respuesta WIN",
    "63afa897-dcb3-4d08-9a7a-c82f1e87c49f": "Asignación Aprobada",
    "a6a2dcde-adf1-4c1a-b1f7-e4ea84c24515": "Asignación Rechazada",
    "cdee1a56-b9e5-46e1-9cd4-442cae7b853e": "Pendiente Reasignación",
    "07edaecc-8564-4618-a2be-bb9d7c81444c": "Pendiente Envío de Formulario Ficha de Datos",
    "9ed38e74-7708-45cb-9211-89b28224edb7": "Formulario de Ficha de Datos Completado",
    "72fa8462-287b-4410-a8ae-2f91ede38445": "Validación Back Office 2",
    "085ad64f-769b-42f7-986d-6eef802f0634": "Ficha de Datos Enviada a WIN",
    "f251b78c-b57f-4cbd-aa61-3653b54c7677": "Pendiente Inicio de Habilitación (construccion)",
    "46400c15-10a3-4c96-a5b0-76f0cf65b753": "En Habilitación Técnica",
    "5214c97a-30b6-44b4-8f6f-dd1798622a8b": "Standby por Accesos",
    "dc5a218f-50a8-4bb6-9351-82b2f10d9886": "Habilitación Completa",
    "b9549f80-9858-4e84-8afc-aacdcd4db23f": "Hunting Perdido/ No Recuperable"
}

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

    # Deduplicación por ID único de mensaje de WhatsApp
    message_id = message_data.get("id")
    if message_id:
        if message_id in PROCESSED_MESSAGE_IDS:
            print(f"👻 [DEDUPLICADOR] Mensaje duplicado detectado y omitido: {message_id}", flush=True)
            return jsonify({"status": "ignored_duplicate"}), 200

        # Guardar en caché
        PROCESSED_MESSAGE_IDS.add(message_id)
        PROCESSED_MESSAGE_IDS_LIST.append(message_id)
        if len(PROCESSED_MESSAGE_IDS_LIST) > MAX_CACHE_SIZE:
            oldest = PROCESSED_MESSAGE_IDS_LIST.pop(0)
            PROCESSED_MESSAGE_IDS.discard(oldest)


    if not from_jid:
        return jsonify({"status": "no_sender"}), 200

    # Limpieza del formato del número (remueve @c.us o prefijos del JID de WhatsApp)
    phone_clean = from_jid.split("@")[0].replace("+", "")

    print(f"📞 [DEBUG] Teléfono limpio recibido de WhatsApp: '{phone_clean}'")

    # Interceptar tráfico enviando la data completa para auto-indexado seguro
    reply_text = router.procesar_flujo_bot(session_id, phone_clean, user_input, message_data)

    # Mantener el target_jid idéntico al origen (from_jid) para responder por el mismo canal activo
    target_jid = from_jid

    # Enviar el mensaje formateado de vuelta a OpenWA de forma segura
    openwa_client.send_whatsapp_message(session_id, target_jid, reply_text)
    print(message_data)

    return jsonify({"status": "processed"}), 200


@app.route("/crm-notificaciones", methods=["POST"])
def webhook_crm_notificaciones():
    payload = request.json
    
    if not payload:
        return jsonify({"status": "error", "message": "No payload provided"}), 400

    print("📢 [WEBHOOK CRM] Payload Recibido:")
    print(payload, flush=True)

    # Extraemos los campos importantes del payload de GHL
    assigned_to = payload.get("assignedTo")
    pipeline_stage_id = payload.get("pipelineStageId")
    
    # Buscar al Gestor/Hunter en la DB
    gestor = None
    if assigned_to:
        gestor = users_model.get_user_by_ghl_id(assigned_to)
        
    # Fallback 1: Buscar por dict 'user' que envía el trigger de GHL
    if not gestor and "user" in payload:
        user_phone = payload["user"].get("phone")
        if user_phone:
            phone_clean = user_phone.replace("+", "").strip()
            gestor = users_model.get_user_by_identifier(phone_clean)

    if not gestor:
        print("⚠️ [WEBHOOK CRM] No se pudo resolver al Gestor del payload.")
        return jsonify({"status": "ignored", "reason": "gestor_not_found"}), 200

    # Obtener nombre legible de la etapa
    stage_name = None
    if pipeline_stage_id:
        stage_name = STAGE_NAMES.get(pipeline_stage_id)
        
    # Fallback 2: Obtener de 'pipleline_stage'
    if not stage_name:
        stage_name = payload.get("pipleline_stage") or payload.get("pipeline_stage") or "Etapa Desconocida"

    # Obtener nombre del contacto/proyecto
    contacto_name = payload.get("name") or payload.get("opportunity_name") or payload.get("first_name", "Proyecto/Contacto")

    # Preparar el mensaje amigable
    mensaje_notificacion = (
        f"🔔 *Actualización de Proyecto*\n\n"
        f"El proyecto/contacto *{contacto_name}* acaba de pasar a la etapa:\n"
        f"📌 *{stage_name}*\n\n"
        f"_(Notificación automática desde GHL)_"
    )

    # Determinar el ID de WhatsApp del Gestor para enviarle el mensaje
    whatsapp_id = gestor.get("whatsapp_id")
    phone = gestor.get("phone")
    chat_id = whatsapp_id if (whatsapp_id and whatsapp_id.lower() != "none") else f"{phone}@c.us"

    # Verificar si hay un TI simulando a este gestor
    ti_simulators = users_model.get_ti_users_simulating(phone)

    if ti_simulators:
        for ti in ti_simulators:
            ti_wa_id = ti.get("whatsapp_id")
            ti_phone = ti.get("phone")
            ti_chat_id = ti_wa_id if (ti_wa_id and ti_wa_id.lower() != "none") else f"{ti_phone}@c.us"
            print(f"🚀 [WEBHOOK CRM] Redirigiendo notificación a TI {ti_phone} (Simulando a {phone})")
            
            # Decoramos el mensaje para que el TI sepa que es interceptado
            msg_ti = f"🎭 *[MODO SIMULACIÓN: {gestor.get('name')}]*\n" + mensaje_notificacion
            openwa_client.send_whatsapp_message("hunting-bot", ti_chat_id, msg_ti)
            
        return jsonify({"status": "success", "message": "Notification redirected to simulators"}), 200

    print(f"🚀 [WEBHOOK CRM] Notificando al Gestor {gestor.get('name')} al chat {chat_id} sobre la etapa {stage_name}")

    # Enviar mensaje por WhatsApp
    # Asumimos que podemos usar la sesión 'hunting-bot' (que sabemos que está activa) 
    # O podríamos iterar, pero dado que el servidor corre el bot para esta sesión:
    openwa_client.send_whatsapp_message("hunting-bot", chat_id, mensaje_notificacion)

    return jsonify({"status": "success", "message": "Notification sent to Gestor"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)