from database import users_model, state_model
from bot import menus
from services import openwa_client
import sys


def procesar_flujo_bot(session_id: str, phone_clean: str, user_input: str, message_data: dict) -> str:
    print(f"📞 [BOT] Recibió mensaje de {phone_clean}: {user_input}", flush=True)

    # 1. Buscar usuario en DB
    user = users_model.get_user_by_identifier(phone_clean)

    # 2. AUTO-INDEXACIÓN AUTOMÁTICA
    if not user:
        print(f"🔍 [LID Desconocido] Solicitando traducción de ID '{phone_clean}' a OpenWA...")
        real_phone = openwa_client.get_contact_phone(session_id, phone_clean)

        if real_phone:
            real_phone_clean = str(real_phone).split("@")[0].replace("+", "").strip()
            user_by_phone = users_model.get_user_by_phone_only(real_phone_clean)

            if user_by_phone:
                users_model.update_user_whatsapp_id(real_phone_clean, phone_clean)
                print(f"⚡ [AUTO-INDEX] Éxito: Enlazado WhatsApp ID '{phone_clean}' al celular '{real_phone_clean}'")
                user = user_by_phone

    if not user:
        return "⚠️ *Acceso Restringido:* Su número no está autorizado en la red de Hunting."

    role = user["role"].upper()

    # =========================================================
    # INTERCEPTOR GLOBAL DE SALUDOS (RESETEO DE ESTADO)
    # =========================================================
    if user_input.strip().lower() in ["hola", "menu", "menú", "inicio", "salir", "volver"]:
        state_model.clear_user_state(phone_clean)
        return menus.obtener_menu_principal(user["name"], role)

    state, state_data = state_model.get_user_state(phone_clean)

    # =========================================================
    # MOTOR DE ESTADOS INTERACTIVOS (INTERCEPTOR DE FORMULARIOS)
    # =========================================================
    if state:
        if state == "HUNTER_VIEWING_OPPORTUNITIES" and role == "HUNTER":
            from services import ghl_client
            opportunities = ghl_client.get_opportunities_by_user(user["ghl_id"])

            if user_input.strip() == "0":
                state_model.clear_user_state(phone_clean)
                return menus.obtener_menu_principal(user["name"], role)

            if user_input.strip().isdigit():
                opp_index = int(user_input.strip()) - 1
                if 0 <= opp_index < len(opportunities):
                    state_model.clear_user_state(phone_clean)
                    selected_opp = opportunities[opp_index]
                    # 🚀 ENRIQUECER SOLO LA OPORTUNIDAD SELECCIONADA
                    print(f"➡️ [ROUTER] Usuario seleccionó oportunidad: {selected_opp.get('name')}", flush=True)
                    enriched_opp = ghl_client.enrich_opportunity(selected_opp)

                    # 📸 DESCARGAR Y ENVIAR LAS FOTOS POR WHATSAPP SI EXISTEN
                    target_jid = f"{user['phone']}@c.us" if user.get("phone") else f"{phone_clean}@c.us"

                    if enriched_opp.get("foto_edificio"):
                        print(f"➡️ [ROUTER] Descargando y enviando foto del edificio: {enriched_opp['foto_edificio']}", flush=True)
                        img_bytes = ghl_client.download_image_bytes(enriched_opp["foto_edificio"])
                        if img_bytes:
                            openwa_client.send_whatsapp_image(session_id, target_jid, img_bytes, "📸 Foto del Edificio")

                    if enriched_opp.get("foto_montantes"):
                        print(f"➡️ [ROUTER] Descargando y enviando foto de montantes: {enriched_opp['foto_montantes']}", flush=True)
                        img_bytes = ghl_client.download_image_bytes(enriched_opp["foto_montantes"])
                        if img_bytes:
                            openwa_client.send_whatsapp_image(session_id, target_jid, img_bytes, "📸 Foto de Montantes")

                    return menus.mostrar_detalles_oportunidad(enriched_opp)
                return menus.mostrar_oportunidades_resumidas(opportunities) + "\n\n⚠️ Número inválido. Seleccione un número de la lista o *0* para volver."

            if opportunities:
                return menus.mostrar_oportunidades_resumidas(opportunities) + "\n\n⚠️ Por favor, seleccione un número de la lista o *0* para volver al Menú Principal."
            state_model.clear_user_state(phone_clean)
            return "📋 No se encontraron oportunidades asignadas.\n\n*0* Volver al Menú Principal"

        elif state == "BUSCAR_PROYECTO" and role in ["HUNTER", "TI", "BACKOFFICE", "CEO"]:
            from services import ghl_client
            opps = ghl_client.get_opportunities_advanced(user["ghl_id"], search_query=user_input.strip())
            state_model.clear_user_state(phone_clean)
            return menus.formatear_lista_historico(opps) + "\n\n*0* Volver al Menú Principal"

        elif state == "PROJECTS_BY_STATE_SELECTION" and role in ["HUNTER", "TI", "BACKOFFICE", "CEO"]:
            from services import ghl_client
            if user_input.strip() == "1":
                opps = ghl_client.get_opportunities_advanced(user["ghl_id"], stage_id="dc5a218f-50a8-4bb6-9351-82b2f10d9886")
                state_model.clear_user_state(phone_clean)
                return menus.formatear_lista_historico(opps) + "\n\n*0* Volver al Menú Principal"
            if user_input.strip() == "2":
                opps = ghl_client.get_opportunities_advanced(user["ghl_id"], stage_id="b9549f80-9858-4e84-8afc-aacdcd4db23f")
                state_model.clear_user_state(phone_clean)
                return menus.formatear_lista_historico(opps) + "\n\n*0* Volver al Menú Principal"
            return menus.obtener_menu_estado()

        elif role == "TI":
            if state == "TI_ALTA_TELEFONO":
                state_data["new_phone"] = user_input.strip()
                state_model.set_user_state(phone_clean, "TI_ALTA_NOMBRE", state_data)
                return "👤 *Paso 2:* Ingrese el NOMBRE COMPLETO del nuevo usuario:"

            elif state == "TI_ALTA_NOMBRE":
                state_data["new_name"] = user_input.strip()
                state_model.set_user_state(phone_clean, "TI_ALTA_GHL_ID", state_data)
                return "🆔 *Paso 3:* Ingrese el ID de usuario de GoHighLevel (GHL ID):"

            elif state == "TI_ALTA_GHL_ID":
                state_data["new_ghl_id"] = user_input.strip()
                state_model.set_user_state(phone_clean, "TI_ALTA_ROL", state_data)
                return "🎭 *Paso 4:* Ingrese el ROL (*HUNTER*, *CEO*, *BACKOFFICE*, *TI*):"

            elif state == "TI_ALTA_ROL":
                nuevo_rol = user_input.upper().strip()
                if nuevo_rol not in ["HUNTER", "CEO", "BACKOFFICE", "TI"]:
                    return "⚠️ Rol inválido. Ingrese uno correcto: *HUNTER*, *CEO*, *BACKOFFICE*, *TI*"

                exito = users_model.create_user(state_data["new_phone"], None, state_data["new_name"],
                                                state_data["new_ghl_id"], nuevo_rol)
                state_model.clear_user_state(phone_clean)
                if exito:
                    return f"✅ *Usuario creado con éxito.*\n\n• Teléfono: {state_data['new_phone']}\n• Nombre: {state_data['new_name']}\n• Rol: {nuevo_rol}\n\nSe auto-indexará al enviar su primer mensaje."
                return "❌ Error: Ese número de teléfono ya está registrado."

            elif state == "TI_BAJA_TELEFONO":
                exito = users_model.update_user_status(user_input.strip(), "inactive")
                state_model.clear_user_state(phone_clean)
                if exito:
                    return f"🗑️ Usuario '{user_input}' dado de BAJA de manera exitosa."
                return "❌ No se encontró ningún usuario activo con ese celular o ID."

            elif state == "TI_MOD_TELEFONO":
                state_data["mod_phone"] = user_input.strip()
                state_model.set_user_state(phone_clean, "TI_MOD_ROL", state_data)
                return "🎭 *Paso 2:* Ingrese el NUEVO ROL (*HUNTER*, *CEO*, *BACKOFFICE*, *TI*):"

            elif state == "TI_MOD_ROL":
                nuevo_rol = user_input.upper().strip()
                if nuevo_rol not in ["HUNTER", "CEO", "BACKOFFICE", "TI"]:
                    return "⚠️ Rol inválido. Ingrese: *HUNTER*, *CEO*, *BACKOFFICE*, *TI*"

                users_model.update_user_role(state_data["mod_phone"], nuevo_rol)
                state_model.clear_user_state(phone_clean)
                return f"✅ Rol de '{state_data['mod_phone']}' actualizado correctamente a *{nuevo_rol}*."

    # =========================================================
    # ENRUTAMIENTO DE ENTRADAS ESTÁNDAR (MENÚS RESIDENCIALES)
    # =========================================================
    if user_input == "1" and role == "HUNTER":
        from services import ghl_client
        opps = ghl_client.get_opportunities_by_user(user["ghl_id"])
        state_model.set_user_state(phone_clean, "HUNTER_VIEWING_OPPORTUNITIES", {})
        return menus.mostrar_oportunidades_resumidas(opps)

    elif user_input == "1" and role == "TI":
        return menus.procesar_opcion_asignadas(user["ghl_id"])

    elif user_input == "1" and role == "BACKOFFICE":
        return menus.procesar_opcion_asignadas(user["ghl_id"])

    elif user_input == "1" and role == "CEO":
        return menus.procesar_opcion_asignadas(user["ghl_id"])

    elif user_input == "2" and role == "HUNTER":
        state_model.set_user_state(phone_clean, "BUSCAR_PROYECTO", {})
        return "🔍 *Buscador de Proyectos:*\n\nPor favor, escriba el nombre del edificio o proyecto que desea buscar:"

    elif user_input == "3" and role == "HUNTER":
        state_model.set_user_state(phone_clean, "PROJECTS_BY_STATE_SELECTION", {})
        return menus.obtener_menu_estado()

    elif user_input == "2" and role in ["CEO", "BACKOFFICE", "TI"]:
        return menus.procesar_opcion_ceo()

    elif user_input == "3" and role == "TI":
        return menus.obtener_menu_admin()

    elif user_input == "31" and role == "TI":
        state_model.set_user_state(phone_clean, "TI_ALTA_TELEFONO")
        return "📱 *Paso 1:* Ingrese el número de CELULAR del nuevo usuario (ej: 51987654321):"

    elif user_input == "32" and role == "TI":
        state_model.set_user_state(phone_clean, "TI_BAJA_TELEFONO")
        return "🗑️ Ingrese el celular o WhatsApp ID del usuario que dará de BAJA:"

    elif user_input == "33" and role == "TI":
        state_model.set_user_state(phone_clean, "TI_MOD_TELEFONO")
        return "✏️ Ingrese el celular o WhatsApp ID del usuario a modificar:"

    elif user_input == "4" and role in ["HUNTER", "TI"]:
        return menus.obtener_menu_historico()

    elif user_input == "41" and role in ["HUNTER", "TI"]:
        return menus.obtener_menu_filtro_estados()

    elif user_input == "411" and role in ["HUNTER", "TI"]:
        from services import ghl_client
        opps = ghl_client.get_opportunities_advanced(user["ghl_id"], stage_id="dc5a218f-50a8-4bb6-9351-82b2f10d9886")
        return menus.formatear_lista_historico(opps)

    elif user_input == "412" and role in ["HUNTER", "TI"]:
        from services import ghl_client
        opps = ghl_client.get_opportunities_advanced(user["ghl_id"], stage_id="b9549f80-9858-4e84-8afc-aacdcd4db23f")
        return menus.formatear_lista_historico(opps)

    elif user_input == "42" and role in ["HUNTER", "TI"]:
        from services import ghl_client
        opps = ghl_client.get_opportunities_advanced(user["ghl_id"])
        return menus.formatear_lista_historico(opps)

    elif user_input == "43" and role in ["HUNTER", "TI"]:
        state_model.set_user_state(phone_clean, "HUNTER_BUSCAR_NOMBRE")
        return "🔍 *Buscador de Proyectos:*\n\nPor favor, escriba el nombre del edificio o proyecto que desea buscar:"

    elif user_input == "0":
        state_model.clear_user_state(phone_clean)
        return menus.obtener_menu_principal(user["name"], role)

    else:
        state_model.clear_user_state(phone_clean)
        return menus.obtener_menu_principal(user["name"], role)