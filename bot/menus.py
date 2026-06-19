from services import ghl_client

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


def obtener_menu_principal(nombre: str, role: str) -> str:
    """Genera un menú completamente único y aislado según el Rol."""
    role_upper = role.upper()
    if role_upper == "CEO":
        return (
            f"Hola *{nombre}* 👋 (CEO)\n"
            f"Bienvenido al Asistente de Alta Gerencia de Grupo Futura.\n\n"
            f"Por favor, seleccione una opción ejecutiva:\n\n"
            f"*[ 2 ]* Ver reporte estratégico del Pipeline"
        )
    elif role_upper == "HUNTER":
        return (
            f"Hola *{nombre}* 👋\n"
            f"Bienvenido al Panel operativo de Hunters.\n\n"
            f"Por favor, seleccione una opción:\n\n"
            f"*[ 1 ]* Ver mis oportunidades asignadas en GHL\n"
            f"*[ 2 ]* Buscar proyecto por nombre\n"
            f"*[ 3 ]* Filtrar oportunidades por estado\n"
            f"*[ 4 ]* Consultar disponibilidad de edificio\n"
            f"*[ 5 ]* Registrar visita de campo"
        )
    elif role_upper == "BACKOFFICE":
        return (
            f"Hola *{nombre}* 👋 ({role})\n"
            f"Bienvenido al panel de control global.\n\n"
            f"Por favor, seleccione una opción:\n\n"
            f"*[ 1 ]* Ver mis oportunidades asignadas\n"
            f"*[ 2 ]* Ver resumen estratégico del Pipeline"
        )
    else:  # ROL TI
        return (
            f"Hola *{nombre}* 👋 (Administrador TI)\n"
            f"Ecosistema de Automatización de Hunting.\n\n"
            f"Por favor, seleccione una opción:\n\n"
            f"*[ 1 ]* Ver mis oportunidades asignadas\n"
            f"*[ 2 ]* Ver resumen estratégico del Pipeline\n"
            f"*[ 3 ]* Panel de Administración de Usuarios ⚙️\n"
            f"*[ 4 ]* Histórico de Proyectos ⏳\n"
            f"*[ 5 ]* Entorno de Simulación 🎭"
        )


def obtener_menu_admin() -> str:
    """Submenú exclusivo para gestión de altas, bajas y cambios de rol."""
    return (
        "⚙️ *Panel de Control de Usuarios (Solo TI)*\n\n"
        "Seleccione la acción que desea ejecutar:\n\n"
        "*[ 31 ]* Registrar nuevo usuario (Alta)\n"
        "*[ 32 ]* Dar de baja a un usuario (Baja)\n"
        "*[ 33 ]* Modificar Rol de un usuario\n\n"
        "*[ 0 ]* Volver al Menú Principal"
    )


def obtener_menu_historico() -> str:
    """Submenú secundario para segmentar el tipo de histórico (UX Campo/Oficina)."""
    return (
        "⏳ *Histórico de Proyectos (Límite: Últimos 20)*\n\n"
        "Seleccione cómo desea consultar su información:\n\n"
        "*[ 41 ]* Ver proyectos por Estado (Ganados / Perdidos)\n"
        "*[ 42 ]* Ver histórico General (Cronológico)\n"
        "*[ 43 ]* Buscar un proyecto por su Nombre 🔍\n\n"
        "*[ 0 ]* Volver al Menú Principal"
    )


def obtener_menu_filtro_estados() -> str:
    """Submenú para elegir entre proyectos ganados o perdidos."""
    return (
        "🎭 *Filtrar Histórico por Estado*\n\n"
        "*[ 411 ]* Ver Habilitaciones Completas (Ganados)\n"
        "*[ 412 ]* Ver Hunting Perdidos / No Recuperables\n\n"
        "*[ 4 ]* Volver al Menú de Historial"
    )


def formatear_lista_historico(opportunities) -> str:
    """Helper genérico para dibujar la ficha completa en WhatsApp."""
    if not opportunities:
        return "📋 *Estatus de Oportunidades:*\n\nNo se encontraron registros que coincidan con los criterios."

    reply = f"📋 *Registros Encontrados ({len(opportunities)})*\n"
    reply += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n"

    for idx, opp in enumerate(opportunities, 1):
        stage_id = opp.get("stage")
        stage_name = STAGE_NAMES.get(stage_id, "Etapa Desconocida")
        reply += f"*{idx}. {opp['name']}*\n"
        reply += f"🚩 *Etapa:* {stage_name}\n"
        reply += f"🏢 *Inmobiliaria:* {opp['inmobiliaria']}\n"
        reply += f"📍 *Dirección:* {opp['direccion']}\n"
        reply += f"📌 *Coordenadas:* {opp.get('coordenadas', 'No especificada')}\n"
        reply += f"• *Supervisor:* {opp.get('supervisor') or 'Sin asignar'}\n"
        reply += f"• *Ejecutivo:* {opp.get('ejecutivo') or 'Sin asignar'}\n"
        if opp.get('foto'):
            reply += f"📸 *Foto del Edificio:* Adjunta en el chat.\n"
        else:
            reply += f"📸 Aún no se llena la ficha de datos\n"
        reply += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
    return reply


def mostrar_oportunidades_resumidas(opportunities) -> str:
    if not opportunities:
        return "📋 *Oportunidades Asignadas:*\n\nNo se encontraron registros asignados a su usuario.\n\n*0* Volver al Menú Principal"

    reply = f"📋 *Oportunidades Asignadas ({len(opportunities)})*\n"
    reply += "Seleccione el número de la oportunidad:\n"
    reply += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n"

    for idx, opp in enumerate(opportunities, 1):
        reply += f"*{idx}. {opp['name']}*\n"
    reply += "\n*0* Volver al Menú Principal"
    return reply


def mostrar_oportunidades_asignadas(opportunities) -> str:
    if not opportunities:
        return "📋 *Oportunidades Asignadas:*\n\nNo se encontraron registros asignados a su usuario.\n\n*0* Volver al Menú Principal"

    reply = f"📋 *Oportunidades Asignadas ({len(opportunities)})*\n"
    reply += "Estas son todas las oportunidades asignadas a su usuario.\n"
    reply += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n"

    for idx, opp in enumerate(opportunities, 1):
        reply += f"*{idx}. {opp['name']}*\n"
    reply += "\n*0* Volver al Menú Principal"
    return reply


def mostrar_detalles_oportunidad(opp: dict) -> str:
    """Muestra los detalles completos de una oportunidad seleccionada."""
    stage_id = opp.get("stage")
    stage_name = STAGE_NAMES.get(stage_id, "Etapa Desconocida")
    
    reply = f"📌 *{opp['name']}*\n\n"
    reply += f"🚩 *Etapa:* {stage_name}\n"
    reply += f"🏢 *Inmobiliaria:* {opp['inmobiliaria']}\n"
    reply += f"📍 *Dirección:* {opp['direccion']}\n"
    reply += f"📌 *Coordenadas:* {opp.get('coordenadas', 'No especificada')}\n"
    reply += f"• *Supervisor:* {opp.get('supervisor') or 'Sin asignar'}\n"
    reply += f"• *Ejecutivo:* {opp.get('ejecutivo') or 'Sin asignar'}\n"
    
    hay_foto = False
    if opp.get('foto_edificio'):
        reply += f"📸 *Foto del Edificio:* Adjunta arriba ☝️\n"
        hay_foto = True
    if opp.get('foto_montantes'):
        reply += f"📸 *Foto de Montantes:* Adjunta arriba ☝️\n"
        hay_foto = True
        
    if not hay_foto:
        reply += f"📸 Aún no se llena la ficha de datos (Sin fotos)\n"
    
    reply += "\n*0* Volver al Menú Principal"
    return reply


def obtener_menu_estado() -> str:
    return (
        "🎭 *Filtrar Proyectos por Estado*\n\n"
        "Seleccione una opción:\n"
        "*[ 1 ]* Ganados\n"
        "*[ 2 ]* Perdidos\n"
        "*[ 0 ]* Volver al Menú Principal"
    )


def procesar_opcion_hunter(ghl_id: str) -> str:
    """Mapea directamente a la lista resumida de oportunidades asignadas para Hunters (Opción 1)."""
    opportunities = ghl_client.get_opportunities_by_user(ghl_id)
    return mostrar_oportunidades_resumidas(opportunities)


def procesar_opcion_asignadas(ghl_id: str) -> str:
    """Muestra oportunidades asignadas sin los controles específicos de Hunter."""
    opportunities = ghl_client.get_opportunities_by_user(ghl_id)
    return mostrar_oportunidades_asignadas(opportunities)


def procesar_opcion_ceo() -> str:
    """Consolida las etapas para el reporte del CEO."""
    opportunities = ghl_client.get_pipeline_summary()
    if not opportunities:
        return "No se encontraron oportunidades en el Pipeline de Hunting."

    fase_prospeccion = 0
    fase_win = 0
    fase_tecnica = 0
    fase_completado = 0
    fase_perdido = 0
    otras_etapas = 0

    STAGES_PROSPECCION = ["4d5d6906-d70f-466a-9b9b-0acf0a203138", "d8481911-0c96-4a53-a246-3f43170a6d24"]
    STAGE_WIN = "fdc27149-b398-4ed7-9271-946c66dc9f0f"
    STAGES_TECNICA = ["46400c15-10a3-4c96-a5b0-76f0cf65b753", "5214c97a-30b6-44b4-8f6f-dd1798622a8b"]
    STAGE_COMPLETADO = "dc5a218f-50a8-4bb6-9351-82b2f10d9886"
    STAGE_PERDIDO = "b9549f80-9858-4e84-8afc-aacdcd4db23f"

    for opp in opportunities:
        stage_id = opp.get("pipelineStageId")
        if stage_id in STAGES_PROSPECCION:
            fase_prospeccion += 1
        elif stage_id == STAGE_WIN:
            fase_win += 1
        elif stage_id in STAGES_TECNICA:
            fase_tecnica += 1
        elif stage_id == STAGE_COMPLETADO:
            fase_completado += 1
        elif stage_id == STAGE_PERDIDO:
            fase_perdido += 1
        else:
            otras_etapas += 1

    reply = f"📊 *Resumen Ejecutivo: Hunting & Habilitación* 🚀\n\n"
    reply += f"• *Total Proyectos en Pipeline:* {len(opportunities)}\n\n"
    reply += f"🎯 *Fase 1 (Prospección Inicial):* {fase_prospeccion}\n"
    reply += f"⏳ *Fase 2 (Esperando Respuesta WIN):* {fase_win} ⚠️\n"
    reply += f"🏗️ *Fase 3 (En Habilitación Técnica):* {fase_tecnica}\n"
    reply += f"✅ *Fase 4 (Habilitación Completa):* {fase_completado}\n"
    reply += f"❌ *Fase 5 (Hunting Perdidos):* {fase_perdido}\n"

    if otras_etapas > 0:
        reply += f"📁 *Otras etapas en proceso:* {otras_etapas}\n"

    reply += f"\n💡 _Datos reales extraídos en vivo desde GoHighLevel._"
    return reply


def obtener_submenu_visitas() -> str:
    """Submenú secundario para registro de visitas de campo."""
    return (
        "🚶‍♂️ *Registro de Visitas de Campo*\n\n"
        "Por favor, seleccione una opción:\n\n"
        "*[ 51 ]* Registrar visita a un NUEVO edificio (Prospecto / Hunting)\n"
        "*[ 52 ]* Registrar visita a un EDIFICIO TRABAJANDO / ASIGNADO\n\n"
        "*[ 0 ]* Volver al Menú Principal"
    )


def mostrar_coincidencias_busqueda(opportunities, search_query: str) -> str:
    """Muestra los resultados de coincidencia encontrados para la visita de campo."""
    if not opportunities:
        return ""

    reply = f"📋 *Coincidencias Encontradas ({len(opportunities)})*\n"
    reply += "Seleccione el número del edificio:\n"
    reply += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n"

    for idx, opp in enumerate(opportunities, 1):
        reply += f"*{idx}. {opp['name']}*\n"
        
    reply += f"\nSi su edificio no aparece en la lista, responda con la palabra *NUEVO* para registrar la visita usando el nombre buscado (*{search_query.upper()}*).\n\n"
    reply += "*0* Volver al Menú Principal"
    return reply